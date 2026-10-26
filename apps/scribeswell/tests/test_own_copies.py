"""Own-copy component acceptance: synthetic stores, never native SQL."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from personal_notes_contract import parse_command
ID='11111111-1111-4111-8111-111111111111'
EMPTY={'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}

def test_copy_commands_accept_exact_source_revision_and_local_base():
 for command,payload in [('note.duplicate',{'expected_revision':'1'}),('study.copy',{'expected_revision':'1'}),('note.conflict_copy',{'base_revision':'1','value':EMPTY})]:
  raw={'operation_id':ID,**payload}
  assert parse_command(command,json.dumps(raw).encode()).model_dump(mode='json')==raw

import asyncio,copy,time
from contextlib import asynccontextmanager
from datetime import datetime,timezone
import pytest
from personal_notes_access import NotesError
from personal_notes_storage import PersonalNotesStorage
from test_own_highlights import value as rich_value,proof
from own_copies import independent_value,check_bounds

def test_copy_is_independent_and_preserves_exact_anchors_colours_and_connections():
 source=rich_value();source['connections']=[{'id':ID,'reference':source['highlights'][0]['anchor']['segments'][0]['reference']}]
 copied=independent_value(source)
 assert copied['highlights'][0]['id']!=ID and copied['connections'][0]['id']!=ID
 assert copied['highlights'][0]['anchor']==source['highlights'][0]['anchor']
 assert copied['highlights'][0]['colour']==source['highlights'][0]['colour']
 copied['highlights'][0]['colour']='#000000';assert source['highlights'][0]['colour']=='#FFCC00'

@pytest.mark.parametrize('notes,passages',[(129,0),(0,201)])
def test_whole_copy_refuses_excess_counts(notes,passages):
 with pytest.raises(NotesError,match='copy_limit_exceeded'):
  check_bounds('Study',[{'visibility':'study','value':EMPTY}]*notes,[{'reference':{}}]*passages)

def test_whole_copy_byte_bound_is_canonical_and_atomic_preflight():
 check_bounds('S',[{'visibility':'study','value':EMPTY}]*128,[{'reference':{}}]*200)
 with pytest.raises(NotesError,match='copy_limit_exceeded'):
  check_bounds('S',[{'visibility':'study','value':{'body':'א'*1100000}}],[])

class Cursor:
 def __init__(self):self.calls=[];self.metadata=None;self.receipt=None;self.notes=[]
 async def execute(self,sql,args=()):self.calls.append((sql,args));self.last=sql
 async def fetchone(self):
  if 'receipts' in self.last:return self.receipt
  if 'SELECT metadata' in self.last:return {'metadata':self.metadata} if self.metadata is not None else None
  return None
 async def fetchall(self):return self.notes
class Storage(PersonalNotesStorage):
 def __init__(self):
  super().__init__('unused');self.cursor=Cursor();self.events=[]
  now=datetime.now(timezone.utc)
  self.source={'id':ID,'study_id':ID,'account_id':ID,'visibility':'study','revision':2,'value':rich_value(),'created_at':now,'updated_at':now,'created_by':ID,'updated_by':ID}
  self.parent={'id':ID,'title':'Exact title','revision':1}
 @asynccontextmanager
 async def transaction(self,*args,write=False,**kwargs):self.events.append('write' if write else 'read');yield self.cursor
 async def _parent(self,*args,lock=False):self.events.append('parent-lock' if lock else 'parent');return self.parent
 async def _note(self,*args,lock=False):self.events.append('note-lock' if lock else 'note');return self.source
 async def _passages(self,*args):return {'revision':'1','items':[]},[]
 async def _live_outcome(self,*args):self.events.append('destination')

def run(storage,command,extra):
 payload=parse_command(command,json.dumps({'operation_id':ID,**extra}).encode())
 return asyncio.run(storage.execute({'account_id':ID,'actor_id':ID},command,payload,ID,None if command=='study.copy' else ID,time.monotonic()+5))

def test_duplicate_uses_trusted_source_without_observation_and_receipt_is_last(monkeypatch):
 import own_highlights
 monkeypatch.setattr(own_highlights,'observe',lambda *_:pytest.fail('trusted source does not require corpus'))
 store=Storage();ack=run(store,'note.duplicate',{'expected_revision':'2'})
 assert ack['note_id']!=ID and ack['study_id']==ID
 assert store.events.index('parent-lock')<store.events.index('note-lock')
 calls=store.cursor.calls
 assert calls[-1][0].startswith('INSERT INTO scribeswell_studies.receipts')
 assert any('INSERT INTO scribeswell_studies.note_revision_metadata' in sql for sql,_ in calls)
 assert any('INSERT INTO scribeswell_studies.note_copy_provenance' in sql for sql,_ in calls)

def test_duplicate_conflict_has_no_write():
 store=Storage()
 with pytest.raises(NotesError,match='note_revision_conflict'):run(store,'note.duplicate',{'expected_revision':'1'})
 assert not any(sql.startswith('INSERT') for sql,_ in store.cursor.calls)

def test_conflict_uses_original_immutable_base_and_observes_only_new_anchors(monkeypatch):
 from own_highlights import metadata
 import own_highlights
 store=Storage();branch=rich_value();store.cursor.metadata=metadata(branch)
 monkeypatch.setattr(own_highlights,'observe',lambda *_:pytest.fail('unchanged historical anchor'))
 ack=run(store,'note.conflict_copy',{'base_revision':'1','value':branch})
 assert ack['note_id']!=ID
 assert any('note_revision_metadata WHERE' in sql and args[-1]==1 for sql,args in store.cursor.calls)
 branch['highlights'][0]['anchor']['segments'][0]['observed_word_ids']=['2']
 def observe(value,deadline):assert 'write' not in store.events;return proof(branch)
 store.events=[];monkeypatch.setattr(own_highlights,'observe',observe)
 run(store,'note.conflict_copy',{'base_revision':'1','value':branch})

def test_missing_rich_base_retains_branch_and_legacy_needs_no_history():
 store=Storage();branch=rich_value();original=copy.deepcopy(branch)
 with pytest.raises(NotesError,match='note_base_unavailable'):run(store,'note.conflict_copy',{'base_revision':'1','value':branch})
 assert branch==original and 'write' not in store.events
 run(store,'note.conflict_copy',{'base_revision':'1','value':EMPTY})

@pytest.mark.parametrize('command,extra',[('note.duplicate',{'expected_revision':'2'}),('note.conflict_copy',{'base_revision':'1','value':EMPTY}),('study.copy',{'expected_revision':'1'})])
def test_replay_uses_destination_before_source_even_after_source_loss(command,extra):
 import hashlib
 store=Storage();payload={'operation_id':ID,**extra};note=None if command=='study.copy' else ID
 outcome={'operation_id':ID,'command':command,'study_id':ID,'note_id':None if command=='study.copy' else ID,'revision':'1'}
 fingerprint=hashlib.sha256(json.dumps({'command':command,'version':1,'study_id':ID,'note_id':note,'payload':payload},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
 store.cursor.receipt={'fingerprint':fingerprint,'outcome':outcome}
 assert run(store,command,extra)==outcome and store.events==['read','destination']

@pytest.mark.parametrize('command,extra,path',[('note.duplicate',{'expected_revision':'2'},'notes/'+ID+'/duplicate'),('note.conflict_copy',{'base_revision':'1','value':EMPTY},'notes/'+ID+'/conflict-copy'),('study.copy',{'expected_revision':'1'},'copy')])
def test_copy_routes_and_lookup_are_current_authorized_no_store(command,extra,path):
 from fastapi import FastAPI
 from fastapi.testclient import TestClient
 from personal_notes_router import build_router
 events=[]
 class Access:
  async def check(self,*args):events.append('access');return {'account_id':ID,'actor_id':ID}
 class Store:
  async def execute(self,identity,kind,payload,*args):events.append(kind);raise NotesError('copy_limit_exceeded')
  async def lookup(self,identity,op,kind,*args):events.append(kind);return {'status':'unresolved'}
 app=FastAPI();app.include_router(build_router(Access(),Store()));client=TestClient(app)
 response=client.post('/api/studies/'+ID+'/'+path,headers={'Authorization':'Bearer current'},json={'operation_id':ID,**extra})
 assert response.status_code==409 and response.json()['code']=='copy_limit_exceeded' and events==['access',command]
 assert response.headers['cache-control']=='private, no-store'
 assert client.get('/api/operations/'+ID+'?command='+command,headers={'Authorization':'Bearer current'}).status_code==200

def test_whole_study_copies_complete_snapshot_beyond_one_page_with_metadata_and_credit():
 store=Storage();store.cursor.notes=[{**store.source,'id':str(__import__('uuid').uuid4()),'value':EMPTY} for _ in range(52)]
 ack=run(store,'study.copy',{'expected_revision':'1'})
 assert ack['study_id']!=ID and ack['note_id'] is None
 calls=store.cursor.calls
 assert sum('INSERT INTO scribeswell_studies.notes(' in sql for sql,_ in calls)==52
 assert sum('INSERT INTO scribeswell_studies.note_revision_metadata' in sql for sql,_ in calls)==52
 assert sum('INSERT INTO scribeswell_studies.note_copy_provenance' in sql for sql,_ in calls)==52
 assert 'LIMIT 129' in next(sql for sql,_ in calls if 'ORDER BY id' in sql)
 assert calls[-1][0].startswith('INSERT INTO scribeswell_studies.receipts')

@pytest.mark.parametrize('kind',['limit','unsupported','revision'])
def test_study_copy_preflights_whole_aggregate_before_any_insert(kind):
 store=Storage();store.cursor.notes=[store.source]*129 if kind=='limit' else [{**store.source,'visibility':'private_response'}] if kind=='unsupported' else []
 with pytest.raises(NotesError,match={'limit':'copy_limit_exceeded','unsupported':'note_format_unsupported','revision':'study_revision_conflict'}[kind]):
  run(store,'study.copy',{'expected_revision':'2' if kind=='revision' else '1'})
 assert not any(sql.startswith('INSERT') for sql,_ in store.cursor.calls)

def test_copy_source_kind_and_unknown_aggregate_fail_closed():
 store=Storage();store.source['visibility']='private_response'
 with pytest.raises(NotesError,match='note_format_unsupported'):run(store,'note.duplicate',{'expected_revision':'2'})
 with pytest.raises(NotesError,match='note_format_unsupported'):independent_value({**EMPTY,'unknown':'sensitive'})
 assert not any(sql.startswith('INSERT') for sql,_ in store.cursor.calls)

@pytest.mark.parametrize('command,extra',[('note.duplicate',{'expected_revision':'2'}),('note.conflict_copy',{'base_revision':'1','value':EMPTY}),('study.copy',{'expected_revision':'1'})])
def test_active_parent_is_rechecked_and_deleted_source_never_resurrects(command,extra):
 store=Storage()
 async def gone(*args,**kwargs):raise NotesError('resource_unavailable')
 store._parent=gone
 with pytest.raises(NotesError,match='resource_unavailable'):run(store,command,extra)
 assert not any(sql.startswith('INSERT') for sql,_ in store.cursor.calls)

def test_conflict_new_anchor_observation_failure_never_mutates_or_receipts(monkeypatch):
 import own_highlights
 store=Storage();store.cursor.metadata={'connections':[],'highlights':[],'references':[]}
 monkeypatch.setattr(own_highlights,'observe',lambda *_:{})
 with pytest.raises(NotesError,match='highlight_proof_unavailable'):run(store,'note.conflict_copy',{'base_revision':'1','value':rich_value()})
 assert 'write' not in store.events


def test_provenance_copy_of_copy_preserves_original_without_chain_or_content():
 from own_copies import provenance
 class C(Cursor):
  async def fetchone(self):return {'origin_account_id':ID,'origin_study_id':'22222222-2222-4222-8222-222222222222','origin_note_id':'33333333-3333-4333-8333-333333333333'}
 cursor=C();asyncio.run(provenance(cursor,ID,ID,ID,ID,ID,'note.duplicate',ID))
 sql,args=cursor.calls[-1]
 assert 'source_note_id,origin_note_id' in sql and args[-1]=='33333333-3333-4333-8333-333333333333' and args[5]=='22222222-2222-4222-8222-222222222222'
 assert not any(word in sql for word in ('title','body','email','chain'))


def test_credit_resolves_only_current_owned_source_and_never_caches_inaccessible_labels():
 from own_copies import credit
 class C(Cursor):
  async def fetchone(self):
   if 'provenance' in self.last:return {'relation':'note.duplicate','source_account_id':ID,'source_study_id':ID,'source_note_id':ID,'origin_account_id':'22222222-2222-4222-8222-222222222222','origin_study_id':ID,'origin_note_id':ID,'created_at':datetime.now(timezone.utc),'created_by':ID}
   pytest.fail('must not read inaccessible original')
 cursor=C();result=asyncio.run(credit(cursor,ID,ID,ID))
 assert result['label']=='Original unavailable' and len(cursor.calls)==1
