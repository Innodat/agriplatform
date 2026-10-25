"""Own-note deletion component contract; native execution is separately gated."""
import json
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from test_personal_notes_api import Access, ACCOUNT, OP
from personal_notes_router import build_router
from personal_notes_contract import parse_command, ContractInputError

NOTE='40000000-0000-4000-8000-000000000001'

def test_delete_route_uses_closed_payload_current_authority_and_no_store():
 class Storage:
  async def execute(self,identity,command,payload,study,note,deadline):
   assert identity['account_id']==ACCOUNT and command=='note.delete' and study==OP and note==NOTE
   return dict(operation_id=OP,command=command,study_id=study,note_id=note,revision='2')
 app=FastAPI();app.include_router(build_router(Access(),Storage()));client=TestClient(app)
 response=client.request('DELETE',f'/api/studies/{OP}/notes/{NOTE}',headers={'Authorization':'Bearer current'},json={'operation_id':OP,'expected_revision':'1'})
 assert response.status_code==200 and response.json()['command']=='note.delete'
 assert response.headers['cache-control']=='private, no-store'

@pytest.mark.parametrize('raw',[b'{}',json.dumps({'operation_id':OP,'expected_revision':1}).encode(),json.dumps({'operation_id':OP,'expected_revision':'1','value':{}}).encode(),b'{"operation_id":"'+OP.encode()+b'","expected_revision":"1","expected_revision":"2"}'])
def test_delete_rejects_invalid_payload(raw):
 with pytest.raises(ContractInputError):parse_command('note.delete',raw)

def test_locked_erasure_and_original_delete_recovery():
 import asyncio, time, hashlib
 from contextlib import asynccontextmanager
 from datetime import datetime,timezone
 from personal_notes_storage import PersonalNotesStorage
 from personal_notes_access import NotesError
 from personal_notes_contract import MAX_REVISION
 empty={'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}
 now=datetime.now(timezone.utc)
 row=dict(id=NOTE,study_id=OP,account_id=ACCOUNT,visibility='study',revision=3,value={**empty,'document':{'version':2,'blocks':[]}},created_at=now,updated_at=now,created_by=ACCOUNT,updated_by=ACCOUNT)
 class Cursor:
  receipt=None
  def __init__(self):self.calls=[]
  async def execute(self,sql,args=()):self.calls.append((sql,args))
  async def fetchone(self):return self.receipt
 cursor=Cursor();locks=[]
 class Storage(PersonalNotesStorage):
  @asynccontextmanager
  async def transaction(self,*args,**kwargs):yield cursor
  async def _parent(self,*args,**kwargs):assert kwargs.get('lock');locks.append('parent');return {}
  async def _note(self,*args,**kwargs):assert kwargs.get('lock');locks.append('note');return row
 storage=Storage('unused');identity={'account_id':ACCOUNT,'actor_id':ACCOUNT}
 payload=parse_command('note.delete',json.dumps(dict(operation_id=OP,expected_revision='3')).encode())
 async def run():
  ack=await storage.execute(identity,'note.delete',payload,OP,NOTE,time.monotonic()+5)
  assert locks==['parent','note'] and ack['revision']=='4'
  writes=[(sql,args) for sql,args in cursor.calls if sql.startswith(('UPDATE','INSERT'))]
  assert len(writes)==2
  assert writes[0][1][0].obj==empty and writes[0][1][1] is False
  assert 'revision=revision+1' in writes[0][0] and 'updated_by' in writes[0][0]
  assert set(writes[1][1][4].obj)=={'operation_id','command','study_id','note_id','revision'}
  cursor.calls=[];row['revision']=int(MAX_REVISION)
  overflow=parse_command('note.delete',json.dumps(dict(operation_id=OP,expected_revision=MAX_REVISION)).encode())
  with pytest.raises(NotesError,match='resource_unavailable'):await storage.execute(identity,'note.delete',overflow,OP,NOTE,time.monotonic()+5)
  assert not any(sql.startswith(('UPDATE','INSERT')) for sql,_ in cursor.calls)
  row['revision']=4;cursor.calls=[]
  with pytest.raises(NotesError,match='note_revision_conflict'):await storage.execute(identity,'note.delete',payload,OP,NOTE,time.monotonic()+5)
  assert not any(sql.startswith(('UPDATE','INSERT')) for sql,_ in cursor.calls)
  # The dedicated recovery boundary never needs an active parent and refuses absent scope.
  cursor.receipt={'id':NOTE};cursor.calls=[]
  await PersonalNotesStorage._live_outcome(storage,cursor,ACCOUNT,ack)
  assert len(cursor.calls)==1 and 'NOT active' in cursor.calls[0][0] and cursor.calls[0][1]==(ACCOUNT,OP,NOTE)
  cursor.receipt=None
  with pytest.raises(NotesError,match='resource_unavailable'):await PersonalNotesStorage._live_outcome(storage,cursor,ACCOUNT,ack)
 asyncio.run(run())

@pytest.mark.parametrize('suffix',['?unexpected=private','?command=note.delete'])
def test_delete_rejects_query_parameters(suffix):
 app=FastAPI();app.include_router(build_router(Access(),object()))
 result=TestClient(app).request('DELETE',f'/api/studies/{OP}/notes/{NOTE}'+suffix,headers={'Authorization':'Bearer current'},json={'operation_id':OP,'expected_revision':'1'})
 assert result.status_code==400 and result.headers['cache-control']=='private, no-store'
 assert 'private' not in result.text

def test_real_previous_checkpoint_is_frozen_and_refuses_delete():
 import sys
 from pathlib import Path
 sys.path.insert(0,str(Path(__file__).parent/'fixtures'))
 from note_deletion_baseline_loader import load
 contract,storage=load()
 with pytest.raises(contract.ContractInputError):contract.parse_command('note.delete',json.dumps({'operation_id':OP,'expected_revision':'1'}).encode())
 assert storage.NoteView is contract.NoteView

@pytest.mark.parametrize('command',['delete','lookup'])
@pytest.mark.parametrize('denial',['missing','authentication_required','studies_access_denied'])
def test_delete_and_original_lookup_refuse_auth_before_storage(command,denial):
 from personal_notes_access import NotesError
 calls=[]
 class CurrentAccess:
  async def check(self,*args):
   calls.append('access')
   raise NotesError(denial)
 class UntouchedStorage:
  async def execute(self,*args):calls.append('storage');raise AssertionError('Unauthorized deletion reached storage')
  async def lookup(self,*args):calls.append('storage');raise AssertionError('Unauthorized deletion lookup reached storage')
 app=FastAPI();app.include_router(build_router(CurrentAccess(),UntouchedStorage()));client=TestClient(app)
 headers={} if denial=='missing' else {'Authorization':'Bearer current'}
 response=client.request('DELETE',f'/api/studies/{OP}/notes/{NOTE}',headers=headers,json={'operation_id':OP,'expected_revision':'1'}) if command=='delete' else client.get(f'/api/operations/{OP}?command=note.delete',headers=headers)
 code='authentication_required' if denial=='missing' else denial
 assert response.status_code==(403 if code=='studies_access_denied' else 401)
 assert response.json()=={'error':'Request could not be completed','code':code,'details':None}
 assert response.headers['cache-control']=='private, no-store'
 assert calls==([] if denial=='missing' else ['access'])
