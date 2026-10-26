"""App component acceptance. No database/native collection or owner calls."""
import asyncio, hashlib, json, sys, time
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from personal_notes_contract import parse_command,ContractInputError
from fastapi import FastAPI
from fastapi.testclient import TestClient
from personal_notes_router import build_router
from passage_references import parse_reference
ID='11111111-1111-4111-8111-111111111111'
DETAILS={'operation_id':ID,'expected_revision':'1','title':'Study שלום','introduction':'First\nשני','source_url':'https://example.invalid/source'}

def test_details_replace_accepts_complete_value_and_nullable_clear():
 assert parse_command('study.details.replace',json.dumps(DETAILS).encode()).introduction=='First\nשני'
 assert parse_command('study.details.replace',json.dumps({**DETAILS,'introduction':None,'source_url':None}).encode()).source_url is None

@pytest.mark.parametrize('field,value',[('introduction','x'*10001),('introduction','bad\x00text'),('source_url','javascript:alert(1)'),('source_url','https://u:p@example.invalid'),('source_url','https://example.invalid/'+'א'*1024)])
def test_details_invalid_candidates_refuse_without_echo(field,value):
 with pytest.raises(ContractInputError):parse_command('study.details.replace',json.dumps({**DETAILS,field:value}).encode())

def test_details_and_context_routes_are_current_authorized_and_private():
 events=[]
 class Access:
  async def check(self,*args):events.append('access');return {'account_id':ID,'actor_id':ID}
 class Store:
  async def execute(self,identity,command,payload,study,note,deadline):events.append(command);return {'operation_id':ID,'command':command,'study_id':ID,'note_id':None,'revision':'2'}
  async def context_notes(self,identity,payload,deadline):events.append('context');assert payload.reference.book_id=='Gen';return {'items':[],'next_cursor':None}
 app=FastAPI();app.include_router(build_router(Access(),Store()));client=TestClient(app)
 for method,path,body in [('put','/api/studies/'+ID,DETAILS),('post','/api/studies/context-notes',{'reference':parse_reference('Gen 1:1')})]:
  result=getattr(client,method)(path,headers={'Authorization':'Bearer current'},json=body)
  assert result.status_code==200 and result.headers['cache-control']=='private, no-store'
  assert getattr(client,method)(path,json=body).status_code==401
 assert events==['access','study.details.replace','access','context']

from contextlib import asynccontextmanager
from datetime import datetime,timezone
from personal_notes_storage import PersonalNotesStorage
from personal_notes_access import NotesError
class Cursor:
 def __init__(self):self.calls=[];self.receipt=None;self.rows=[]
 async def execute(self,sql,args=()):self.calls.append((sql,args));self.last=sql
 async def fetchone(self):return self.receipt if 'receipts' in self.last else None
 async def fetchall(self):return self.rows
class Store(PersonalNotesStorage):
 def __init__(self):super().__init__('unused');self.cursor=Cursor();self.parent={'title':'Old','introduction':'Previous','source_url':'https://example.invalid','revision':1};self.locks=[]
 @asynccontextmanager
 async def transaction(self,*args,**kwargs):yield self.cursor
 async def _parent(self,*args,lock=False):self.locks.append(lock);return self.parent
 async def _live_outcome(self,*args):self.locks.append('live')
def run(store,command,body,study=ID):
 return asyncio.run(store.execute({'account_id':ID,'actor_id':ID},command,parse_command(command,json.dumps(body).encode()),study,None,time.monotonic()+5))

def test_details_replace_locks_revision_attribution_and_noop():
 store=Store();result=run(store,'study.details.replace',DETAILS)
 assert result['revision']=='2' and store.locks==[True]
 sql,args=next((sql,args) for sql,args in store.cursor.calls if sql.startswith('UPDATE'))
 assert args[:3]==(DETAILS['title'],DETAILS['introduction'],DETAILS['source_url']) and 'updated_by' in sql and 'clock_timestamp()' in sql
 assert store.cursor.calls[-1][0].startswith('INSERT INTO scribeswell_studies.receipts')
 store=Store();store.parent.update({key:DETAILS[key] for key in ('title','introduction','source_url')})
 assert run(store,'study.details.replace',DETAILS)['revision']=='1'
 assert not any(sql.startswith('UPDATE') for sql,_ in store.cursor.calls)
 store=Store();store.parent['revision']=2
 with pytest.raises(NotesError,match='study_revision_conflict'):run(store,'study.details.replace',DETAILS)
 assert not any(sql.startswith(('INSERT','UPDATE')) for sql,_ in store.cursor.calls)

def test_old_create_receipt_replay_preserves_absent_additive_fingerprint_and_title_null():
 store=Store();body={'operation_id':ID,'title':None}
 canonical={'command':'study.create','version':1,'study_id':None,'note_id':None,'payload':body}
 outcome={'operation_id':ID,'command':'study.create','study_id':ID,'note_id':None,'revision':'1'}
 store.cursor.receipt={'fingerprint':hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),'outcome':outcome}
 assert run(store,'study.create',body,None)==outcome and store.locks==['live']
 with pytest.raises(NotesError,match='operation_payload_mismatch'):run(store,'study.create',{**body,'introduction':None},None)

def test_details_create_and_copy_retain_metadata_and_include_bytes():
 store=Store();run(store,'study.create',{'operation_id':ID,'title':'New','introduction':'Intro','source_url':None},None)
 sql,args=next((sql,args) for sql,args in store.cursor.calls if sql.startswith('INSERT INTO scribeswell_studies.studies'))
 assert 'introduction,source_url' in sql and args[3:5]==('Intro',None)
 from test_own_copies import Storage,run as copy_run
 store=Storage();store.parent.update(introduction='Copied\nIntro',source_url='https://example.invalid')
 copy_run(store,'study.copy',{'expected_revision':'1'})
 sql,args=next((sql,args) for sql,args in store.cursor.calls if sql.startswith('INSERT INTO scribeswell_studies.studies'))
 assert args[3:5]==('Copied\nIntro','https://example.invalid')
 from own_copies import check_bounds
 with pytest.raises(NotesError,match='copy_limit_exceeded'):check_bounds('Title',[],[],'א'*1100000,None)

def test_context_query_cursor_account_reference_and_sql_filters():
 from personal_notes_context import context_query,context_sql
 from personal_notes_search import encode_cursor,decode_cursor
 ref=parse_reference('Gen1:1');query=context_query(ref);stamp='2026-10-26T10:00:00.000000Z'
 cursor=encode_cursor(ID,query,stamp,ID)
 assert decode_cursor(cursor,ID,query)==[stamp,ID]
 for account,q in [('22222222-2222-4222-8222-222222222222',query),(ID,context_query(parse_reference('Gen1:2')))]:
  with pytest.raises(NotesError):decode_cursor(cursor,account,q)
 sql,args=context_sql(ID,ref,[stamp,ID],20)
 assert "n.visibility='study'" in sql and 'n.active AND s.active' in sql and 'n.account_id=q.account' in sql
 assert 'EXISTS(SELECT 1' in sql and 'ORDER BY n.created_at DESC,n.id DESC LIMIT' in sql and args[-1]==21
 assert "jsonb_typeof" in sql and 'connections' in sql and 'segments' in sql and "passage_link" in sql

def test_context_saved_preview_is_bounded_unique_and_study_attributed():
 from personal_notes_context import context_item
 ref=parse_reference('Gen1:1')
 value={'document':{'version':2,'blocks':[{'type':'paragraph','direction':'auto','content':[{'type':'text','text':'א'*200,'marks':[]},{'type':'passage_link','label':'Gen1:1','reference':ref}]}]},'connections':[],'highlights':[]}
 result=context_item({'value':value,'study_id':ID,'study_title':'Title','account_id':ID,'id':ID,'revision':1})
 assert len(result['preview'])==120 and result['references']==[ref] and result['study_title']=='Title'

@pytest.mark.parametrize('change',[{'limit':0},{'limit':51},{'limit':True},{'reference':None},{'owner_account_id':ID},{'cursor':'not valid'}])
def test_context_endpoint_accepts_one_closed_canonical_reference_and_bounded_page(change):
 with pytest.raises(ContractInputError):parse_command('notes.context',json.dumps({'reference':parse_reference('Gen1:1'),**change}).encode())

def test_details_complete_replacement_requires_explicit_clear_fields_and_scalar_limit():
 for missing in ('introduction','source_url'):
  body={k:v for k,v in DETAILS.items() if k!=missing}
  with pytest.raises(ContractInputError):parse_command('study.details.replace',json.dumps(body).encode())
 assert parse_command('study.details.replace',json.dumps({**DETAILS,'introduction':'𐐀'*10000},ensure_ascii=False).encode()).introduction=='𐐀'*10000


def test_context_unsupported_matching_neighbor_cannot_poison_page_or_hide_later_match():
 from datetime import timedelta
 from copy import deepcopy
 ref=parse_reference('Gen1:1');v={'document':{'version':2,'blocks':[{'type':'paragraph','direction':'auto','content':[{'type':'passage_link','reference':ref,'label':'Gen1:1'}]}]},'connections':[],'highlights':[]}
 now=datetime.now(timezone.utc);base={'study_id':ID,'study_title':'Study','account_id':ID,'revision':1,'created_at':now,'value':v}
 bad={**base,'id':'22222222-2222-4222-8222-222222222222','value':deepcopy(v)};bad['value']['document']['blocks'].append({'type':'unsupported_sibling','content':'private'})
 good={**base,'id':'33333333-3333-4333-8333-333333333333','created_at':now-timedelta(seconds=1)}
 class Pages(Cursor):
  def __init__(self):super().__init__();self.pages=[[bad,good],[good]]
  async def fetchall(self):return self.pages.pop(0)
 store=Store();store.cursor=Pages()
 def page(cursor=None):return asyncio.run(store.context_notes({'account_id':ID,'actor_id':ID},parse_command('notes.context',json.dumps({'reference':ref,'limit':1,'cursor':cursor}).encode()),time.monotonic()+5))
 first=page();assert first['items']==[] and first['next_cursor'] is not None
 second=page(first['next_cursor']);assert [item['note_id'] for item in second['items']]==[good['id']] and second['next_cursor'] is None
 assert len(store.cursor.calls)==2 and all(args[-1]==2 for _,args in store.cursor.calls)
