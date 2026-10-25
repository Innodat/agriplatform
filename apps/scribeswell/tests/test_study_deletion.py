"""Confirmed whole-study deletion; native database qualification remains deferred."""
import asyncio
from contextlib import asynccontextmanager
import json
import time
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from test_personal_notes_api import Access, ACCOUNT, OP
from personal_notes_router import build_router
from personal_notes_contract import parse_command, OperationAck, ContractInputError, MAX_REVISION
from personal_notes_storage import PersonalNotesStorage
from personal_notes_access import NotesError


def test_delete_route_current_authority_and_closed_payload():
 class Storage:
  async def execute(self,identity,command,payload,study,note,deadline):
   assert identity['account_id']==ACCOUNT and command=='study.delete' and study==OP and note is None
   return dict(operation_id=OP,command=command,study_id=study,note_id=None,revision='2')
 app=FastAPI();app.include_router(build_router(Access(),Storage()))
 result=TestClient(app).request('DELETE',f'/api/studies/{OP}',headers={'Authorization':'Bearer current'},json={'operation_id':OP,'expected_revision':'1'})
 assert result.status_code==200 and result.json()['command']=='study.delete'
 assert result.headers['cache-control']=='private, no-store'


def test_study_delete_dto_and_correlated_ack():
 payload=parse_command('study.delete',json.dumps({'operation_id':OP,'expected_revision':'1'}).encode())
 assert payload.expected_revision=='1'
 ack=OperationAck(operation_id=OP,command='study.delete',study_id=OP,note_id=None,revision='2')
 assert ack.note_id is None
 with pytest.raises(ValueError):OperationAck(operation_id=OP,command='study.delete',study_id=OP,note_id=OP,revision='2')

@pytest.mark.parametrize('payload',[{}, {'operation_id':OP,'expected_revision':1},{'operation_id':OP,'expected_revision':'1','title':'private'}])
def test_study_delete_rejects_invalid_payload(payload):
 with pytest.raises(ContractInputError):parse_command('study.delete',json.dumps(payload).encode())


def test_study_delete_locked_cleanup_overflow_and_tombstone_recovery():
 class Cursor:
  def __init__(self):self.calls=[];self.row=None;self.overflow=False
  async def execute(self,sql,args=()):self.calls.append((sql,args))
  async def fetchone(self):return ({'id':OP} if self.overflow else None) if 'revision>=' in self.calls[-1][0] else None if 'fingerprint,outcome' in self.calls[-1][0] else self.row
 cursor=Cursor()
 class Storage(PersonalNotesStorage):
  @asynccontextmanager
  async def transaction(self,*args,**kwargs):yield cursor
  async def _parent(self,*args,**kwargs):assert kwargs.get('lock');return {'revision':3}
 storage=Storage('unused');identity={'account_id':ACCOUNT,'actor_id':ACCOUNT}
 payload=parse_command('study.delete',json.dumps({'operation_id':OP,'expected_revision':'3'}).encode())
 async def run():
  ack=await storage.execute(identity,'study.delete',payload,OP,None,time.monotonic()+5)
  assert ack['revision']=='4' and ack['note_id'] is None
  writes=[(sql,args) for sql,args in cursor.calls if sql.startswith(('UPDATE','DELETE','INSERT'))]
  assert ['notes','passage_entries','passage_lists','studies','receipts']==[sql.split('.')[1].split()[0].split('(')[0] for sql,_ in writes]
  assert writes[0][1][0].obj=={'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}
  assert 'AND active' in writes[0][0] and 'Deleted study' in writes[3][0]
  assert set(writes[-1][1][4].obj)=={'operation_id','command','study_id','note_id','revision'}
  cursor.calls=[];cursor.overflow=True
  with pytest.raises(NotesError,match='resource_unavailable'):await storage.execute(identity,'study.delete',payload,OP,None,time.monotonic()+5)
  assert not any(sql.startswith(('UPDATE','DELETE','INSERT')) for sql,_ in cursor.calls)
  cursor.calls=[];cursor.overflow=False;cursor.row={'id':OP}
  await storage._live_outcome(cursor,ACCOUNT,ack)
  assert 'NOT active' in cursor.calls[-1][0] and cursor.calls[-1][1]==(ACCOUNT,OP)
  cursor.row=None
  with pytest.raises(NotesError,match='resource_unavailable'):await storage._live_outcome(cursor,ACCOUNT,ack)
 asyncio.run(run())

@pytest.mark.parametrize('suffix',['?extra=private','?command=study.delete','?command=study.delete&command=study.delete'])
def test_study_delete_query_allowlist(suffix):
 app=FastAPI();app.include_router(build_router(Access(),object()))
 response=TestClient(app).request('DELETE',f'/api/studies/{OP}'+suffix,headers={'Authorization':'Bearer current'},json={'operation_id':OP,'expected_revision':'1'})
 assert response.status_code==400 and response.headers['cache-control']=='private, no-store'
 assert 'private' not in response.text

@pytest.mark.parametrize('command',['delete','lookup'])
@pytest.mark.parametrize('denial',['missing','authentication_required','studies_access_denied'])
def test_study_deletion_current_authority_precedes_storage(command,denial):
 calls=[]
 class CurrentAccess:
  async def check(self,*args):calls.append('access');raise NotesError(denial)
 class Storage:
  async def execute(self,*args):calls.append('storage');raise AssertionError
  async def lookup(self,*args):calls.append('storage');raise AssertionError
 app=FastAPI();app.include_router(build_router(CurrentAccess(),Storage()));client=TestClient(app)
 headers={} if denial=='missing' else {'Authorization':'Bearer current'}
 response=client.request('DELETE',f'/api/studies/{OP}',headers=headers,json={'operation_id':OP,'expected_revision':'1'}) if command=='delete' else client.get(f'/api/operations/{OP}?command=study.delete',headers=headers)
 assert response.status_code==(403 if denial=='studies_access_denied' else 401)
 assert response.headers['cache-control']=='private, no-store' and calls==([] if denial=='missing' else ['access'])


def test_study_delete_original_replay_payload_mismatch_and_metadata_conflict():
 import hashlib
 class Cursor:
  receipt=None
  calls=[]
  async def execute(self,sql,args=()):self.calls.append((sql,args))
  async def fetchone(self):return self.receipt if 'receipts' in self.calls[-1][0] else {'id':OP}
 cursor=Cursor()
 class Storage(PersonalNotesStorage):
  @asynccontextmanager
  async def transaction(self,*args,**kwargs):yield cursor
  async def _parent(self,*args,**kwargs):return {'revision':2}
 storage=Storage('unused');identity={'account_id':ACCOUNT,'actor_id':ACCOUNT}
 payload=parse_command('study.delete',json.dumps({'operation_id':OP,'expected_revision':'1'}).encode())
 outcome=dict(operation_id=OP,command='study.delete',study_id=OP,note_id=None,revision='2')
 fingerprint=hashlib.sha256(json.dumps(dict(command='study.delete',version=1,study_id=OP,note_id=None,payload=payload.model_dump(mode='json')),sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
 async def run():
  with pytest.raises(NotesError,match='study_revision_conflict'):await storage.execute(identity,'study.delete',payload,OP,None,time.monotonic()+5)
  assert not any(sql.startswith(('UPDATE','DELETE','INSERT')) for sql,_ in cursor.calls)
  cursor.receipt={'fingerprint':fingerprint,'outcome':outcome};cursor.calls=[]
  assert await storage.execute(identity,'study.delete',payload,OP,None,time.monotonic()+5)==outcome
  assert not any(sql.startswith(('UPDATE','DELETE','INSERT')) for sql,_ in cursor.calls)
  cursor.receipt['fingerprint']='changed'
  with pytest.raises(NotesError,match='operation_payload_mismatch'):await storage.execute(identity,'study.delete',payload,OP,None,time.monotonic()+5)
 asyncio.run(run())


def test_study_deletion_previous_f6_checkpoint_is_byte_frozen():
 import sys
 from pathlib import Path
 sys.path.insert(0,str(Path(__file__).parent/'fixtures'))
 from study_deletion_baseline_loader import load
 contract,storage=load()
 with pytest.raises(contract.ContractInputError):contract.parse_command('study.delete',json.dumps({'operation_id':OP,'expected_revision':'1'}).encode())
 assert storage.NoteView is contract.NoteView
