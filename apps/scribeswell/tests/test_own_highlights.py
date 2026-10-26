"""Synthetic aggregate contract acceptance; no database/owner calls."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from personal_notes_contract import parse_command
from passage_references import make_reference

ID='11111111-1111-4111-8111-111111111111'
def value():
 return {'format_version':3,'document':{'version':1,'blocks':[]},'connections':[], 'highlights':[{'id':ID,'colour':'#FFCC00','anchor':{'version':1,'source_id':'source-v1','source_revision':ID,'catalogue_version':make_reference('Gen',{'kind':'verse_range','start':{'chapter':1,'verse':1},'end':{'chapter':1,'verse':1}})['catalogue_version'],'versification_id':'oshb-hebrew-json-c2d8e9e5','tokenization_version':'tokens-v1','segments':[{'reference':make_reference('Gen',{'kind':'verse_range','start':{'chapter':1,'verse':1},'end':{'chapter':1,'verse':1}}),'start_position':1,'end_position':1,'observed_word_ids':['9007199254740993'],'verse_token_digest':'a'*64}]}}]}
def test_current_note_aggregate_preserves_exact_decimal_ids_and_writing():
 result=parse_command('note.create',json.dumps({'operation_id':ID,'value':value()}).encode())
 assert result.value.model_dump(mode='json')==value()

import copy
import pytest
from personal_notes_contract import ContractInputError
from own_highlights import validate,metadata
from personal_notes_access import NotesError

def command(v):return parse_command('note.create',json.dumps({'operation_id':ID,'value':v}).encode())
@pytest.mark.parametrize('mutate',[
 lambda v:v.update(format_version=True),lambda v:v.update(format_version=3.0),
 lambda v:v['highlights'][0]['anchor'].update(version=True),
 lambda v:v['highlights'][0].update(colour='#ffcc00'),
 lambda v:v['highlights'][0]['anchor'].update(source_id='x'*65),
 lambda v:v['highlights'][0]['anchor']['segments'][0].update(observed_word_ids=[9007199254740993]),
 lambda v:v['highlights'][0]['anchor']['segments'][0].update(observed_word_ids=['092']),
 lambda v:v['highlights'][0]['anchor']['segments'][0].update(end_position=2),
 lambda v:v['highlights'].append(copy.deepcopy(v['highlights'][0])),
 lambda v:v['highlights'][0]['anchor']['segments'][0]['reference'].update(book_id='Matt'),
])
def test_invalid_aggregate_rejects_whole_value(mutate):
 v=value();mutate(v)
 with pytest.raises(ContractInputError):command(v)

def proof(v):
 a=v['highlights'][0]['anchor'];s=a['segments'][0];p=s['reference']['target']['start']
 return {('Gen',1,1):{'version':1,'status':'ready',**{k:a[k] for k in ('source_id','source_revision','catalogue_version','versification_id','tokenization_version')},'book':'Gen',**p,'verse_token_digest':s['verse_token_digest'],'observed_word_ids':list(s['observed_word_ids']),'token_count':1}}

def test_new_anchor_requires_current_actual_ids_while_retained_anchor_needs_no_proof():
 v=value();validate(v,{},proof(v))
 validate(v,metadata(v),{})
 recoloured=copy.deepcopy(v);recoloured['highlights'][0]['colour']='#123456';validate(recoloured,metadata(v),{})
 with pytest.raises(NotesError,match='highlight_proof_unavailable'):validate(v,{}, {})
 for field,new in [('observed_word_ids',['2']),('source_revision','22222222-2222-4222-8222-222222222222'),('verse_token_digest','b'*64)]:
  wrong=proof(v);wrong[('Gen',1,1)][field]=new
  with pytest.raises(NotesError,match='highlight_proof_invalid'):validate(v,{},wrong)
 changed=copy.deepcopy(v);changed['highlights'][0]['anchor']['segments'][0]['observed_word_ids']=['2']
 with pytest.raises(NotesError,match='highlight_proof_unavailable'):validate(changed,metadata(v),{})

def test_metadata_keeps_all_references_and_anchor_identity_without_writing_or_colour():
 v=value();ref=v['highlights'][0]['anchor']['segments'][0]['reference'];v['document']={'version':2,'blocks':[{'type':'paragraph','direction':'auto','content':[{'type':'passage_link','label':'A reference','reference':ref},{'type':'text','text':'private writing','marks':[]}]}]}
 result=metadata(v)
 assert result['references']==[ref]
 assert 'private writing' not in json.dumps(result) and '#FFCC00' not in json.dumps(result)

def test_continuous_cross_verse_anchor_requires_full_interior_end_proof():
 v=value();a=v['highlights'][0]['anchor'];s=copy.deepcopy(a['segments'][0]);s['reference']=make_reference('Gen',{'kind':'verse_range','start':{'chapter':1,'verse':2},'end':{'chapter':1,'verse':2}});s['observed_word_ids']=['2'];a['segments'].append(s)
 command(v)
 e=proof(v);e[('Gen',1,1)]['token_count']=2;e[('Gen',1,1)]['observed_word_ids'].append('3');e[('Gen',1,2)]={**e[('Gen',1,1)],'verse':2,'token_count':1,'observed_word_ids':['2']}
 with pytest.raises(NotesError,match='highlight_proof_invalid'):validate(v,{},e)
 s['reference']=make_reference('Gen',{'kind':'verse_range','start':{'chapter':1,'verse':3},'end':{'chapter':1,'verse':3}})
 with pytest.raises(ContractInputError):command(v)

def test_reader_proof_uses_actual_complete_words_and_preserves_public_text(monkeypatch):
 from contextlib import contextmanager
 from services import bible_service
 from corpus_evidence import verse_token_digest
 from reader_evidence import observed
 ref=value()['highlights'][0]['anchor']['segments'][0]['reference']
 pub={**proof(value())[('Gen',1,1)],'observed_word_ids':['9007199254740993']}
 words=[{'id':9007199254740993,'verse_id':1,'position':1,'surface_he':'אָב','display_he':'אָב','lemma_strong':None,'morph_code':None}]
 pub['verse_token_digest']=verse_token_digest(pub['source_id'],pub['catalogue_version'],pub['versification_id'],pub['tokenization_version'],'Gen',1,1,[[1,'אָב']])
 class DB:
  entered=False
  @contextmanager
  def reader_snapshot(self):
   assert not self.entered;self.entered=True
   try:yield
   finally:self.entered=False
  def one(self,*args,**kwargs):assert self.entered;return {'id':1}
  def read(self,table,**kwargs):
   assert self.entered
   return [{'id':1,'verse_num':1,'book_id':1,'chapter_num':1}] if table=='verse_read' else words
  def reader_publications(self,*args):assert self.entered;return {1:pub}
 db=DB();monkeypatch.setattr(bible_service,'get_database',lambda:db)
 result=bible_service.get_verses('Gen',1).model_dump(mode='json');e=result['data'][0]['anchor_evidence']
 assert e['status']=='ready' and e['reference']==ref and e['observed_word_ids']==['9007199254740993']
 pub['verse_token_digest']='f'*64
 result=bible_service.get_verses('Gen',1).model_dump(mode='json')
 assert result['data'][0]['words'][0]['surface_he']=='אָב' and result['data'][0]['anchor_evidence']=={'version':1,'status':'unavailable'}


def test_snapshot_and_optional_failure_savepoint_restore_pool_context():
 from contextlib import contextmanager
 from contextvars import ContextVar
 from database import Database
 import psycopg
 calls=[]
 class Result:
  def fetchone(self):return {'evidence':None}
 class Connection:
  @contextmanager
  def transaction(self):
   calls.append('begin')
   try:yield
   except Exception:calls.append('rollback');raise
   else:calls.append('commit')
  def execute(self,sql,args=()):
   calls.append(sql)
   if 'scribeswell.reader_verse_evidence' in sql:raise psycopg.errors.UndefinedFunction('synthetic')
   return Result()
 db=Database.__new__(Database);db._connection=ContextVar('test',default=None);connection=Connection()
 class Pool:
  @contextmanager
  def connection(self):yield connection
 db.pool=Pool()
 with db.reader_snapshot():
  assert db._connection.get() is connection
  assert db.reader_publication('Gen',1,1) is None
  calls.append('public text still readable')
 assert db._connection.get() is None
 assert calls[0:2]==['begin','SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY']
 assert calls.index('rollback')<calls.index('public text still readable')<calls.index('commit')


def test_reader_profile_is_explicit_and_previous_profiles_remain_pinned():
 sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations'))
 from release_profile import selection,valid_result,evidence
 expected=selection({'profile':'reader-evidence-v1','custody':None})
 assert valid_result({'before':'scribeswell_0004','after':'scribeswell_0005','validation':evidence(expected)},expected)
 assert valid_result({'before':'scribeswell_0005','after':'scribeswell_0005','validation':evidence(expected)},expected)
 assert not valid_result({'before':'scribeswell_0003','after':'scribeswell_0005','validation':evidence(expected)},expected)
 previous=selection({'profile':'publication-v1','custody':None})
 assert not valid_result({'before':'scribeswell_0004','after':'scribeswell_0005','validation':evidence(previous)},previous)

def test_storage_admission_precedes_private_locks_and_is_atomic(monkeypatch):
 import asyncio,time,hashlib
 from contextlib import asynccontextmanager
 from datetime import datetime,timezone
 import own_highlights
 from personal_notes_storage import PersonalNotesStorage
 now=datetime.now(timezone.utc);events=[];calls=[]
 row={'id':ID,'study_id':ID,'account_id':ID,'visibility':'study','revision':1,'value':{'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]},'created_at':now,'updated_at':now,'created_by':ID,'updated_by':ID}
 class Cursor:
  receipt=None
  async def execute(self,sql,args=()):calls.append((sql,args))
  async def fetchone(self):return self.receipt
 cursor=Cursor()
 class Storage(PersonalNotesStorage):
  @asynccontextmanager
  async def transaction(self,*args,write=False,**kwargs):events.append('write' if write else 'read');yield cursor
  async def _parent(self,*args,lock=False):events.append('parent-lock' if lock else 'parent-read');return {}
  async def _note(self,*args,lock=False):events.append('note-lock' if lock else 'note-read');return row
 storage=Storage('unused');identity={'account_id':ID,'actor_id':ID}
 def observe(v,deadline):events.append('proof');assert 'write' not in events;return proof(value())
 monkeypatch.setattr(own_highlights,'observe',observe)
 payload=parse_command('note.replace',json.dumps({'operation_id':ID,'expected_revision':'1','value':value()}).encode())
 async def execute():return await storage.execute(identity,'note.replace',payload,ID,ID,time.monotonic()+5)
 ack=asyncio.run(execute())
 assert ack['revision']=='2' and events.index('proof')<events.index('parent-lock')<events.index('note-lock')
 assert any('INSERT INTO scribeswell_studies.note_revision_metadata' in sql for sql,_ in calls)
 assert calls[-1][0].startswith('INSERT INTO scribeswell_studies.receipts')
 # Changed identity fails under locks before any aggregate/metadata/receipt mutation.
 calls.clear();events.clear();monkeypatch.setattr(own_highlights,'observe',lambda *_:{})
 with pytest.raises(NotesError,match='highlight_proof_unavailable'):asyncio.run(execute())
 assert not any(sql.startswith(('UPDATE','INSERT')) for sql,_ in calls)
 # Exact current anchors and recolouring do not call an unavailable corpus.
 row['value']=value();calls.clear();events.clear()
 monkeypatch.setattr(own_highlights,'observe',lambda *_:pytest.fail('unchanged anchor must not observe source'))
 asyncio.run(execute())
 # Format3 is retained even after every mark is removed.
 row['value']={**value(),'highlights':[]};events.clear();calls.clear()
 legacy=parse_command('note.replace',json.dumps({'operation_id':ID,'expected_revision':'1','value':{'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}}).encode())
 with pytest.raises(NotesError,match='note_format_unsupported'):asyncio.run(storage.execute(identity,'note.replace',legacy,ID,ID,time.monotonic()+5))
 assert not any(sql.startswith(('UPDATE','INSERT')) for sql,_ in calls)
 # Known committed replay reconciles before observing source, even when unavailable.
 body=payload.model_dump(mode='json');fingerprint=hashlib.sha256(json.dumps({'command':'note.replace','version':1,'study_id':ID,'note_id':ID,'payload':body},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
 cursor.receipt={'fingerprint':fingerprint,'outcome':ack};events.clear();calls.clear()
 result=asyncio.run(execute());assert result==ack and 'write' not in events

def test_long_chapter_fetches_publication_once_with_full_ordered_inventory(monkeypatch):
 from contextlib import contextmanager
 from services import bible_service
 from corpus_evidence import verse_token_digest
 from passage_references import make_reference
 calls=[];reference=make_reference('Ps',{'kind':'chapter','chapter':119})
 class DB:
  entered=False
  @contextmanager
  def reader_snapshot(self):self.entered=True;yield;self.entered=False
  def one(self,*args,**kwargs):assert self.entered;return {'id':27}
  def read(self,table,**kwargs):
   assert self.entered;calls.append(table)
   if table=='verse_read':return [{'id':v,'verse_num':v,'book_id':27,'chapter_num':119} for v in range(1,177)]
   return [{'id':v,'verse_id':v,'position':1,'surface_he':'אָב','display_he':'אָב','lemma_strong':None,'morph_code':None} for v in range(1,177)]
  def reader_publications(self,book,chapter,numbers):
   assert self.entered and book=='Ps' and chapter==119 and numbers==list(range(1,177));calls.append('proof-batch')
   return {v:{'version':1,'status':'ready','source_id':'source-v1','source_revision':ID,'catalogue_version':reference['catalogue_version'],'versification_id':reference['versification_id'],'tokenization_version':'tokens-v1','book':'Ps','chapter':119,'verse':v,'observed_word_ids':[str(v)],'verse_token_digest':verse_token_digest('source-v1',reference['catalogue_version'],reference['versification_id'],'tokens-v1','Ps',119,v,[[1,'אָב']])} for v in numbers}
 monkeypatch.setattr(bible_service,'get_database',DB)
 result=bible_service.get_verses('Ps',119).model_dump(mode='json')
 assert len(result['data'])==176 and all(v['anchor_evidence']['status']=='ready' for v in result['data'])
 assert calls==['verse_read','word_read','proof-batch']

@pytest.mark.parametrize('code,status_code',[('highlight_proof_invalid',409),('highlight_proof_unavailable',503)])
def test_highlight_admission_errors_use_safe_typed_private_http_contract(code,status_code):
 from fastapi import FastAPI
 from fastapi.testclient import TestClient
 from personal_notes_router import build_router
 class Access:
  async def check(self,*args):return {'account_id':ID,'actor_id':ID}
 class Storage:
  async def execute(self,*args):raise NotesError(code)
 app=FastAPI();app.include_router(build_router(Access(),Storage()))
 response=TestClient(app).post(f'/api/studies/{ID}/notes',headers={'Authorization':'Bearer current'},json={'operation_id':ID,'value':value()})
 assert response.status_code==status_code and response.json()=={'error':'Request could not be completed','code':code,'details':None}
 assert response.headers['cache-control']=='private, no-store'

@pytest.mark.parametrize('field',['id','colour','source_id','source_revision','catalogue_version','versification_id','tokenization_version','verse_token_digest','observed_word_ids'])
def test_anchor_lexical_fields_reject_trailing_newline(field):
 v=value();h=v['highlights'][0];a=h['anchor'];segment=a['segments'][0]
 if field in ('id','colour'):h[field]+='\n'
 elif field=='observed_word_ids':segment[field][0]+='\n'
 elif field=='verse_token_digest':segment[field]+='\n'
 else:a[field]+='\n'
 with pytest.raises(ContractInputError):command(v)
