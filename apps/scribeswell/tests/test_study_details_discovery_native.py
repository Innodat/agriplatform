"""PREPARED ONLY: uncollected/unexecuted until explicitly authorized final phase.

Disposable PostgreSQL fixture only. Synthetic corpus anchors test SQL, not live owners.
"""
import hashlib,json,os
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4
import psycopg
from psycopg.types.json import Jsonb
import pytest
from test_personal_notes_storage import native,create,command,run,deadline,IDENTITY,A,B,ACTOR,value,close_study
from personal_notes_access import NotesError
from passage_references import parse_reference

@pytest.fixture
def details_native(request):
 if os.environ.get('SCRIBESWELL_STUDY_DETAILS_NATIVE')!='1':pytest.skip('explicit final-phase qualification only')
 assert urlsplit(os.environ.get('SCRIBESWELL_NOTES_TEST_ADMIN_URL','')).port not in (55481,55482)
 return request.getfixturevalue('native')

def details(storage,study,revision='1',introduction='Intro\nמבוא',source_url='https://example.invalid/source'):
 return run(storage.execute(IDENTITY,'study.details.replace',command('study.details.replace',expected_revision=revision,title='Detailed study',introduction=introduction,source_url=source_url),study,None,deadline()))

def context(storage,reference='Gen1:1',cursor=None,limit=20,identity=IDENTITY):
 from personal_notes_contract import parse_command
 return run(storage.context_notes(identity,parse_command('notes.context',json.dumps({'reference':parse_reference(reference),'cursor':cursor,'limit':limit}).encode()),deadline()))

def linked(storage,study,reference='Gen1:1',text='Own explanation'):
 v=value(text);v['document']['version']=2;v['document']['blocks'][0]['content'].append({'type':'passage_link','label':reference,'reference':parse_reference(reference)})
 return run(storage.execute(IDENTITY,'note.create',command('note.create',value=v),study,None,deadline()))

def test_native_additive_metadata_old_create_receipt_and_old_title_writer_preserve_details(details_native):
 storage,admin_url,*_=details_native;study=create(storage,'Initial')['study_id'];details(storage,study)
 # The pre-adoption receipt canonical payload has no new keys and must replay.
 from personal_notes_contract import parse_command
 op=str(uuid4());payload={'operation_id':op,'title':None}
 canonical={'command':'study.create','version':1,'study_id':None,'note_id':None,'payload':payload}
 outcome={'operation_id':op,'command':'study.create','study_id':study,'note_id':None,'revision':'1'}
 fingerprint=hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
 with psycopg.connect(admin_url) as db:db.execute('INSERT INTO scribeswell_studies.receipts(account_id,command,command_version,operation_id,fingerprint,outcome,study_id,created_by) VALUES(%s,%s,1,%s,%s,%s,%s,%s)',(A,'study.create',op,fingerprint,Jsonb(outcome),study,ACTOR))
 assert run(storage.execute(IDENTITY,'study.create',parse_command('study.create',json.dumps(payload).encode()),None,None,deadline()))==outcome
 run(storage.execute(IDENTITY,'study.rename',command('study.rename',expected_revision='2',title='Old title writer'),study,None,deadline()))
 saved=run(storage.read(IDENTITY,study,None,deadline()));assert saved['introduction']=='Intro\nמבוא' and saved['source_url']=='https://example.invalid/source' and saved['revision']=='3'
 with psycopg.connect(admin_url) as db:
  assert db.execute("SELECT data_type,is_nullable FROM information_schema.columns WHERE table_schema='scribeswell_studies' AND table_name='studies' AND column_name='introduction'").fetchone()==('text','YES')
  assert db.execute('SELECT version_num FROM scribeswell_studies.alembic_version').fetchone()[0]=='scribeswell_studies_0008'


def test_native_metadata_revision_noop_null_clear_constraints_and_receipt_atomicity(details_native):
 storage,admin_url,runtime,*_=details_native;study=create(storage,'Initial')['study_id'];ack=details(storage,study)
 assert details(storage,study,'2')['revision']=='2'
 with pytest.raises(NotesError,match='study_revision_conflict'):details(storage,study,'1')
 details(storage,study,'2',None,None)
 saved=run(storage.read(IDENTITY,study,None,deadline()));assert saved.get('introduction') is None and saved.get('source_url') is None
 with psycopg.connect(runtime) as db:
  db.execute("SELECT set_config('app.account_id',%s,true)",(A,))
  with pytest.raises(psycopg.errors.CheckViolation):db.execute('UPDATE scribeswell_studies.studies SET introduction=%s WHERE id=%s',('x'*10001,study))
 with psycopg.connect(runtime) as db:
  db.execute("SELECT set_config('app.account_id',%s,true)",(B,));assert db.execute('SELECT id FROM scribeswell_studies.studies WHERE id=%s',(study,)).fetchall()==[]


def test_native_previous_running_title_only_delete_still_erases_additive_details(details_native):
 storage,admin_url,runtime,*_=details_native;study=create(storage,'Initial')['study_id'];details(storage,study)
 # Exact previous writer SQL remains supported; the new BEFORE-close trigger
 # clears additive content without teaching the previous release new columns.
 with psycopg.connect(runtime) as db:
  db.execute("SELECT set_config('app.account_id',%s,true)",(A,))
  db.execute("UPDATE scribeswell_studies.studies SET title='Deleted study',active=false,revision=revision+1,updated_by=%s,updated_at=clock_timestamp() WHERE account_id=%s AND id=%s",(ACTOR,A,study))
 with psycopg.connect(admin_url) as db:
  assert db.execute('SELECT active,introduction,source_url FROM scribeswell_studies.studies WHERE id=%s',(study,)).fetchone()==(False,None,None)


def test_native_context_filters_parent_note_visibility_before_limit_and_each_note_once(details_native):
 storage,admin_url,*_=details_native;study=create(storage,'Visible')['study_id'];wanted=linked(storage,study)
 # Newer nonmatching notes must not consume matching page slots.
 for _ in range(22):linked(storage,study,'Gen2:1')
 gone=linked(storage,study);run(storage.execute(IDENTITY,'note.delete',command('note.delete',expected_revision='1'),study,gone['note_id'],deadline()))
 dead=create(storage,'Closed parent')['study_id'];linked(storage,dead);close_study(storage,dead)
 assert [n['note_id'] for n in context(storage,limit=1)['items']]==[wanted['note_id']]
 other=run(storage.execute({'account_id':B,'actor_id':ACTOR},'study.create',command('study.create',title='Other owner'),None,None,deadline()))['study_id']
 v=value('Other secret');v['document']['version']=2;v['document']['blocks'][0]['content'].append({'type':'passage_link','reference':parse_reference('Gen1:1'),'label':'Gen1:1'})
 run(storage.execute({'account_id':B,'actor_id':ACTOR},'note.create',command('note.create',value=v),other,None,deadline()))
 assert all(n['owner_account_id']==A for n in context(storage)['items'])
 # Future unsupported visibility/kinds are inserted only by disposable fixture admin.
 with psycopg.connect(admin_url) as db:
  db.execute('ALTER TABLE scribeswell_studies.notes DROP CONSTRAINT notes_visibility_check')
  db.execute('INSERT INTO scribeswell_studies.notes(id,account_id,study_id,visibility,value,created_by,updated_by) VALUES(%s,%s,%s,%s,%s,%s,%s)',(str(uuid4()),A,study,'private_response',Jsonb(v),ACTOR,ACTOR))
 assert [n['note_id'] for n in context(storage,limit=1)['items']]==[wanted['note_id']]


def test_native_context_keyset_cursor_bound_to_reference_account_and_saved_preview(details_native):
 storage,*_=details_native;study=create(storage,'Paging')['study_id'];ids={linked(storage,study)['note_id'] for _ in range(3)}
 first=context(storage,limit=2);second=context(storage,cursor=first['next_cursor'],limit=2)
 assert len(first['items'])==2 and len(second['items'])==1 and {n['note_id'] for n in first['items']+second['items']}==ids
 assert all(n['study_title']=='Paging' and len(n['preview'])<=120 for n in first['items'])
 for kwargs in ({'reference':'Gen1:2'},{'identity':{'account_id':B,'actor_id':ACTOR}}):
  with pytest.raises(NotesError,match='scribeswell_personal_notes_input_invalid'):context(storage,cursor=first['next_cursor'],**kwargs)


def test_native_context_connections_document_links_and_highlight_overlap_deduplicate(details_native):
 storage,*_=details_native;study=create(storage,'References')['study_id']
 from test_own_highlights import value as highlighted
 v=highlighted();ref=v['highlights'][0]['anchor']['segments'][0]['reference'];v['connections']=[{'id':str(uuid4()),'reference':ref}]
 # Synthetic trusted fixture seed avoids pretending a live source observation.
 with psycopg.connect(details_native[1]) as db:
  identifier=str(uuid4());db.execute('INSERT INTO scribeswell_studies.notes(id,account_id,study_id,value,created_by,updated_by) VALUES(%s,%s,%s,%s,%s,%s)',(identifier,A,study,Jsonb(v),ACTOR,ACTOR))
 result=context(storage);assert sum(n['note_id']==identifier for n in result['items'])==1
 linked(storage,study,'Gen1:31–2:2');assert len(context(storage,'Gen2:1')['items'])==1


def test_native_whole_copy_preserves_details_and_atomic_byte_preflight(details_native):
 storage,admin_url,*_=details_native;study=create(storage,'Initial')['study_id'];details(storage,study);linked(storage,study)
 copied=run(storage.execute(IDENTITY,'study.copy',command('study.copy',expected_revision='2'),study,None,deadline()))['study_id']
 saved=run(storage.read(IDENTITY,copied,None,deadline()));assert saved['introduction']=='Intro\nמבוא' and saved['source_url']=='https://example.invalid/source'
 # Byte preflight uses a fixture admin oversized value with otherwise bounded note count.
 with psycopg.connect(admin_url) as db:
  db.execute('UPDATE scribeswell_studies.notes SET value=%s WHERE account_id=%s AND study_id=%s',(Jsonb(value('א'*1100000)),A,study))
  before=db.execute('SELECT count(*) FROM scribeswell_studies.studies WHERE account_id=%s',(A,)).fetchone()[0]
 with pytest.raises(NotesError,match='copy_limit_exceeded'):run(storage.execute(IDENTITY,'study.copy',command('study.copy',expected_revision='2'),study,None,deadline()))
 with psycopg.connect(admin_url) as db:assert db.execute('SELECT count(*) FROM scribeswell_studies.studies WHERE account_id=%s',(A,)).fetchone()[0]==before


@pytest.mark.parametrize('sibling',[{'type':'unsupported_sibling','content':'private'}, {'type':'paragraph','direction':'auto','content':7}])
def test_native_context_unsupported_neighbor_has_bounded_cursor_to_valid_later_match(details_native,sibling):
 from copy import deepcopy
 storage,admin_url,*_=details_native;reference='Gen3:1' if sibling['type']=='unsupported_sibling' else 'Gen4:1';study=create(storage,'Malformed neighbor')['study_id'];wanted=linked(storage,study,reference)
 original=run(storage.read(IDENTITY,study,wanted['note_id'],deadline()))['value'];bad=deepcopy(original);bad['document']['blocks'].append(sibling)
 with psycopg.connect(admin_url) as db:
  db.execute('INSERT INTO scribeswell_studies.notes(id,account_id,study_id,value,created_by,updated_by) VALUES(%s,%s,%s,%s,%s,%s)',(str(uuid4()),A,study,Jsonb(bad),ACTOR,ACTOR))
 first=context(storage,reference,limit=1);assert first['items']==[] and first['next_cursor']
 second=context(storage,reference,cursor=first['next_cursor'],limit=1)
 assert second['items'][0]['note_id']==wanted['note_id']


def test_native_details_replace_races_title_only_rename_under_one_metadata_revision(details_native):
 import asyncio
 storage,*_=details_native;study=create(storage,'Initial')['study_id']
 async def race():return await asyncio.gather(
  storage.execute(IDENTITY,'study.details.replace',command('study.details.replace',expected_revision='1',title='Details winner',introduction='Exact intro',source_url='https://example.invalid/details'),study,None,deadline()),
  storage.execute(IDENTITY,'study.rename',command('study.rename',expected_revision='1',title='Rename winner'),study,None,deadline()),return_exceptions=True)
 results=run(race());assert sum(isinstance(r,dict) for r in results)==1
 assert next(r for r in results if isinstance(r,NotesError)).code=='study_revision_conflict'
 saved=run(storage.read(IDENTITY,study,None,deadline()));assert saved['revision']=='2'
 assert (saved['title'],saved.get('introduction'),saved.get('source_url')) in [('Details winner','Exact intro','https://example.invalid/details'),('Rename winner',None,None)]


def test_native_details_replace_races_delete_without_resurrection_or_retained_metadata(details_native):
 import asyncio
 storage,admin_url,*_=details_native;study=create(storage,'Initial')['study_id']
 async def race():return await asyncio.gather(
  storage.execute(IDENTITY,'study.details.replace',command('study.details.replace',expected_revision='1',title='Updated',introduction='Private intro',source_url='https://example.invalid/details'),study,None,deadline()),
  storage.execute(IDENTITY,'study.delete',command('study.delete',expected_revision='1'),study,None,deadline()),return_exceptions=True)
 results=run(race());assert sum(isinstance(r,dict) for r in results)==1
 assert next(r for r in results if isinstance(r,NotesError)).code in ('study_revision_conflict','resource_unavailable')
 if isinstance(results[0],dict):run(storage.execute(IDENTITY,'study.delete',command('study.delete',expected_revision='2'),study,None,deadline()))
 with psycopg.connect(admin_url) as db:assert db.execute('SELECT active,introduction,source_url FROM scribeswell_studies.studies WHERE id=%s',(study,)).fetchone()==(False,None,None)
 with pytest.raises(NotesError,match='resource_unavailable'):details(storage,study,'2')


def test_native_details_replace_races_whole_study_copy_with_one_coherent_metadata_snapshot(details_native):
 import asyncio
 storage,*_=details_native;study=create(storage,'Initial')['study_id'];details(storage,study)
 async def race():return await asyncio.gather(
  storage.execute(IDENTITY,'study.details.replace',command('study.details.replace',expected_revision='2',title='New title',introduction='New intro',source_url='https://example.invalid/new'),study,None,deadline()),
  storage.execute(IDENTITY,'study.copy',command('study.copy',expected_revision='2'),study,None,deadline()),return_exceptions=True)
 replaced,copied=run(race());assert isinstance(replaced,dict)
 if isinstance(copied,NotesError):assert copied.code=='study_revision_conflict'
 else:
  saved=run(storage.read(IDENTITY,copied['study_id'],None,deadline()))
  assert (saved['title'],saved['introduction'],saved['source_url'])==('Detailed study','Intro\nמבוא','https://example.invalid/source')
 current=run(storage.read(IDENTITY,study,None,deadline()));assert (current['title'],current['introduction'],current['source_url'])==('New title','New intro','https://example.invalid/new')
