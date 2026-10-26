"""PREPARED ONLY: never collected or run during own-copy implementation.

Requires an explicitly disposable final-phase fixture; synthetic aggregate seeds
exercise private SQL, never claim actual corpus/owner admission proof.
"""
import asyncio,json,os
from urllib.parse import urlsplit
from uuid import uuid4
import psycopg
from psycopg.types.json import Jsonb
import pytest
from test_personal_notes_storage import native,create,command,run,deadline,IDENTITY,A,B,ACTOR,value
from personal_notes_access import NotesError

@pytest.fixture
def copies_native(request):
 if os.environ.get('SCRIBESWELL_OWN_COPIES_NATIVE')!='1':pytest.skip('explicit final-phase native qualification only')
 assert urlsplit(os.environ.get('SCRIBESWELL_NOTES_TEST_ADMIN_URL','')).port not in (55481,55482)
 return request.getfixturevalue('native')

def seed(fixture):
 storage,*_=fixture;study=create(storage,'Exact copied title')['study_id']
 note=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value('Private complete writing')),study,None,deadline()))
 return storage,study,note

def duplicate(storage,study,note,attempt=None):
 return run(storage.execute(IDENTITY,'note.duplicate',attempt or command('note.duplicate',expected_revision=note['revision']),study,note['note_id'],deadline()))

def test_native_same_operation_concurrency_has_one_independent_effect(copies_native):
 storage,study,note=seed(copies_native);attempt=command('note.duplicate',expected_revision='1')
 async def race():return await asyncio.gather(*(storage.execute(IDENTITY,'note.duplicate',attempt,study,note['note_id'],deadline()) for _ in range(2)))
 a,b=run(race());assert a==b and a['note_id']!=note['note_id']
 assert len(run(storage.list(IDENTITY,study,50,None,deadline()))['items'])==2

def test_native_copy_receipt_survives_source_deletion_and_copy_is_independent(copies_native):
 storage,study,note=seed(copies_native);attempt=command('note.duplicate',expected_revision='1');copy=duplicate(storage,study,note,attempt)
 run(storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision='1',value=value('Changed copy')),study,copy['note_id'],deadline()))
 assert run(storage.read(IDENTITY,study,note['note_id'],deadline()))['value']==value('Private complete writing')
 run(storage.execute(IDENTITY,'note.delete',command('note.delete',expected_revision='1'),study,note['note_id'],deadline()))
 assert duplicate(storage,study,note,attempt)==copy
 assert run(storage.lookup(IDENTITY,attempt.operation_id,'note.duplicate',deadline()))['outcome']==copy
 assert run(storage.read(IDENTITY,study,copy['note_id'],deadline()))['copy_credit']['label']=='Original unavailable'

def test_native_copy_of_copy_retains_bounded_original_credit_and_owner_privacy(copies_native):
 storage,study,note=seed(copies_native);first=duplicate(storage,study,note);second=duplicate(storage,study,first)
 credit=run(storage.read(IDENTITY,study,second['note_id'],deadline()))['copy_credit']
 assert credit['source_note_id']==first['note_id'] and credit['origin_note_id']==note['note_id']
 with psycopg.connect(copies_native[2]) as db:
  db.execute("SELECT set_config('app.account_id',%s,true)",(B,));assert db.execute('SELECT count(*) FROM scribeswell_studies.note_copy_provenance').fetchone()==(0,)
 for sql in ['UPDATE scribeswell_studies.note_copy_provenance SET relation=relation','DELETE FROM scribeswell_studies.note_copy_provenance','TRUNCATE scribeswell_studies.note_copy_provenance']:
  with psycopg.connect(copies_native[2]) as db:
   db.execute("SELECT set_config('app.account_id',%s,true)",(A,))
   with pytest.raises(psycopg.Error):db.execute(sql)


def test_native_whole_copy_includes_more_than_a_page_ordered_passages_and_outlives_source(copies_native):
 from passage_references import parse_reference
 storage,study,note=seed(copies_native)
 for i in range(51):run(storage.execute(IDENTITY,'note.create',command('note.create',value=value(str(i))),study,None,deadline()))
 items=[{'id':str(uuid4()),'reference':parse_reference('Gen1:'+str(n))} for n in (3,1,2)]
 run(storage.execute(IDENTITY,'study.passages.replace',command('study.passages.replace',expected_revision='1',items=items),study,None,deadline()))
 attempt=command('study.copy',expected_revision='1');copy=run(storage.execute(IDENTITY,'study.copy',attempt,study,None,deadline()))
 with psycopg.connect(copies_native[2]) as db:
  db.execute("SELECT set_config('app.account_id',%s,true)",(A,));assert db.execute('SELECT count(*) FROM scribeswell_studies.notes WHERE study_id=%s AND active',(copy['study_id'],)).fetchone()==(52,)
 passages=run(storage.passages(IDENTITY,copy['study_id'],deadline()))['items'];assert [p['reference'] for p in passages]==[p['reference'] for p in items]
 assert not set(p['id'] for p in passages)&set(p['id'] for p in items)
 run(storage.execute(IDENTITY,'study.delete',command('study.delete',expected_revision='1'),study,None,deadline()))
 assert run(storage.execute(IDENTITY,'study.copy',attempt,study,None,deadline()))==copy
 assert run(storage.read(IDENTITY,copy['study_id'],None,deadline()))['title']=='Exact copied title'

def test_native_over_limit_copy_has_no_destination_receipt_or_provenance(copies_native):
 storage,study,note=seed(copies_native)
 for i in range(128):run(storage.execute(IDENTITY,'note.create',command('note.create',value=value(str(i))),study,None,deadline()))
 attempt=command('study.copy',expected_revision='1')
 with pytest.raises(NotesError,match='copy_limit_exceeded'):run(storage.execute(IDENTITY,'study.copy',attempt,study,None,deadline()))
 assert run(storage.lookup(IDENTITY,attempt.operation_id,'study.copy',deadline()))=={'status':'unresolved'}
 with psycopg.connect(copies_native[2]) as db:
  db.execute("SELECT set_config('app.account_id',%s,true)",(A,));assert db.execute('SELECT count(*) FROM scribeswell_studies.study_copy_provenance WHERE source_study_id=%s',(study,)).fetchone()==(0,)


def test_native_provenance_failure_rolls_back_complete_copy_and_exact_retry(copies_native):
 storage,study,note=seed(copies_native);attempt=command('note.duplicate',expected_revision='1')
 with psycopg.connect(copies_native[1]) as db:
  db.execute("CREATE FUNCTION scribeswell_studies.synthetic_copy_fail() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic' USING ERRCODE='23514'; END $$")
  db.execute('CREATE TRIGGER synthetic_copy_fail BEFORE INSERT ON scribeswell_studies.note_copy_provenance FOR EACH ROW EXECUTE FUNCTION scribeswell_studies.synthetic_copy_fail()')
 try:
  with pytest.raises(NotesError):duplicate(storage,study,note,attempt)
  assert len(run(storage.list(IDENTITY,study,50,None,deadline()))['items'])==1
  assert run(storage.lookup(IDENTITY,attempt.operation_id,'note.duplicate',deadline()))=={'status':'unresolved'}
 finally:
  with psycopg.connect(copies_native[1]) as db:
   db.execute('DROP TRIGGER synthetic_copy_fail ON scribeswell_studies.note_copy_provenance');db.execute('DROP FUNCTION scribeswell_studies.synthetic_copy_fail()')
 assert duplicate(storage,study,note,attempt)['note_id']!=note['note_id']


def test_native_historical_base_survives_later_revision_but_never_revives_deleted_source(copies_native):
 storage,study,note=seed(copies_native);branch=value('Older local branch')
 run(storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision='1',value=value('Current server branch')),study,note['note_id'],deadline()))
 fork=run(storage.execute(IDENTITY,'note.conflict_copy',command('note.conflict_copy',base_revision='1',value=branch),study,note['note_id'],deadline()))
 assert run(storage.read(IDENTITY,study,fork['note_id'],deadline()))['value']==branch
 assert run(storage.read(IDENTITY,study,note['note_id'],deadline()))['value']==value('Current server branch')
 run(storage.execute(IDENTITY,'note.delete',command('note.delete',expected_revision='2'),study,note['note_id'],deadline()))
 with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute(IDENTITY,'note.conflict_copy',command('note.conflict_copy',base_revision='1',value=branch),study,note['note_id'],deadline()))


def test_native_copy_save_delete_race_never_has_partial_destination(copies_native):
 storage,study,note=seed(copies_native)
 async def race():
  return await asyncio.gather(storage.execute(IDENTITY,'study.copy',command('study.copy',expected_revision='1'),study,None,deadline()),storage.execute(IDENTITY,'study.delete',command('study.delete',expected_revision='1'),study,None,deadline()),return_exceptions=True)
 copied,closed=run(race());assert isinstance(closed,dict)
 if isinstance(copied,NotesError):assert copied.code=='resource_unavailable'
 else:
  assert len(run(storage.list(IDENTITY,copied['study_id'],50,None,deadline()))['items'])==1
  assert run(storage.read(IDENTITY,copied['study_id'],None,deadline()))['copy_credit']['label']=='Original unavailable'


def test_native_original_payload_mismatch_rejected_without_another_effect(copies_native):
 storage,study,note=seed(copies_native);attempt=command('note.duplicate',expected_revision='1');duplicate(storage,study,note,attempt)
 from personal_notes_contract import parse_command
 mismatch=parse_command('note.duplicate',json.dumps({'operation_id':attempt.operation_id,'expected_revision':'2'}).encode())
 with pytest.raises(NotesError,match='operation_payload_mismatch'):duplicate(storage,study,note,mismatch)
 assert len(run(storage.list(IDENTITY,study,50,None,deadline()))['items'])==2


def test_native_synthetic_historical_anchor_base_is_exact_and_deleted_source_stays_closed(copies_native,monkeypatch):
 from test_own_highlights import value as rich_value
 from own_highlights import metadata
 import own_highlights
 storage,study,note=seed(copies_native);branch=rich_value()
 # Restricted fixture seed establishes correspondence only; this deliberately
 # does not claim actual published-corpus observation/admission authority.
 with psycopg.connect(copies_native[2]) as db:
  db.execute("SELECT set_config('app.account_id',%s,true)",(A,))
  db.execute('UPDATE scribeswell_studies.notes SET value=%s,revision=2 WHERE id=%s',(Jsonb(branch),note['note_id']))
  db.execute('INSERT INTO scribeswell_studies.note_revision_metadata(account_id,study_id,note_id,revision,metadata,created_by) VALUES(%s,%s,%s,2,%s,%s)',(A,study,note['note_id'],Jsonb(metadata(branch)),ACTOR))
 monkeypatch.setattr(own_highlights,'observe',lambda *_:pytest.fail('historical exact anchor must not observe source'))
 current={**branch,'document':value('Current server writing')['document']}
 run(storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision='2',value=current),study,note['note_id'],deadline()))
 branch['highlights'][0]['colour']='#123456'
 fork=run(storage.execute(IDENTITY,'note.conflict_copy',command('note.conflict_copy',base_revision='2',value=branch),study,note['note_id'],deadline()))
 copied=run(storage.read(IDENTITY,study,fork['note_id'],deadline()))['value']
 assert copied['highlights'][0]['id']!=branch['highlights'][0]['id'] and copied['highlights'][0]['anchor']==branch['highlights'][0]['anchor'] and copied['highlights'][0]['colour']=='#123456'
 with pytest.raises(NotesError,match='note_base_unavailable'):run(storage.execute(IDENTITY,'note.conflict_copy',command('note.conflict_copy',base_revision='99',value=branch),study,note['note_id'],deadline()))
 run(storage.execute(IDENTITY,'note.delete',command('note.delete',expected_revision='3'),study,note['note_id'],deadline()))
 with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute(IDENTITY,'note.conflict_copy',command('note.conflict_copy',base_revision='2',value=branch),study,note['note_id'],deadline()))


def test_native_copy_cross_account_source_and_provenance_destination_scope_fail_closed(copies_native):
 storage,study,note=seed(copies_native);other={'account_id':B,'actor_id':ACTOR}
 with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute(other,'note.duplicate',command('note.duplicate',expected_revision='1'),study,note['note_id'],deadline()))
 with psycopg.connect(copies_native[2]) as db:
  db.execute("SELECT set_config('app.account_id',%s,true)",(B,))
  with pytest.raises(psycopg.Error):db.execute("INSERT INTO scribeswell_studies.note_copy_provenance(account_id,study_id,note_id,source_account_id,source_study_id,source_note_id,origin_account_id,origin_study_id,origin_note_id,relation,created_by) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,'note.duplicate',%s)",(B,study,note['note_id'],A,study,note['note_id'],A,study,note['note_id'],ACTOR))


@pytest.mark.parametrize('table,note_scope',[('study_copy_provenance',False),('note_copy_provenance',True)])
@pytest.mark.parametrize('foreign_field',['source_account_id','origin_account_id'])
def test_native_own_copy_provenance_refuses_cross_account_credit(copies_native,table,note_scope,foreign_field):
 storage,study,note=seed(copies_native)
 fields={'account_id':A,'study_id':study,'source_account_id':A,'source_study_id':study,'origin_account_id':A,'origin_study_id':study,'relation':'note.duplicate' if note_scope else 'study.copy','created_by':ACTOR}
 if note_scope:fields.update(note_id=note['note_id'],source_note_id=note['note_id'],origin_note_id=note['note_id'])
 fields[foreign_field]=B
 with psycopg.connect(copies_native[2]) as db:
  db.execute("SELECT set_config('app.account_id',%s,true)",(A,))
  with pytest.raises(psycopg.errors.CheckViolation):db.execute('INSERT INTO scribeswell_studies.'+table+'('+','.join(fields)+') VALUES('+','.join(['%s']*len(fields))+')',tuple(fields.values()))


@pytest.mark.parametrize('change',['note.create','note.replace','study.passages.replace'])
def test_native_copy_waits_for_source_child_parent_lock_and_copies_coherent_result(copies_native,change):
 from personal_notes_storage import PersonalNotesStorage
 from passage_references import parse_reference
 storage,study,note=seed(copies_native)
 async def scenario():
  held=asyncio.Event();release=asyncio.Event()
  class SourceStorage(PersonalNotesStorage):
   async def _parent(self,*args,lock=False):
    row=await super()._parent(*args,lock=lock)
    if lock:held.set();await release.wait()
    return row
  source=SourceStorage(copies_native[2])
  fields={'value':value('Concurrent writing')} if change=='note.create' else {'expected_revision':'1','value':value('Concurrent writing')} if change=='note.replace' else {'expected_revision':'1','items':[{'id':str(uuid4()),'reference':parse_reference('Gen1:2')},{'id':str(uuid4()),'reference':parse_reference('Gen1:1')}]}
  changed=asyncio.create_task(source.execute(IDENTITY,change,command(change,**fields),study,note['note_id'] if change=='note.replace' else None,deadline()))
  async with asyncio.timeout(2):await held.wait()
  copied=asyncio.create_task(storage.execute(IDENTITY,'study.copy',command('study.copy',expected_revision='1'),study,None,deadline()))
  # Both real writers coordinate through the existing source parent lock.
  release.set();return await changed,await copied
 changed,copied=run(scenario())
 source_notes=run(storage.list(IDENTITY,study,50,None,deadline()))['items'];destination_notes=run(storage.list(IDENTITY,copied['study_id'],50,None,deadline()))['items']
 assert sorted(json.dumps(row['value'],sort_keys=True) for row in destination_notes)==sorted(json.dumps(row['value'],sort_keys=True) for row in source_notes)
 assert len(destination_notes)==(2 if change=='note.create' else 1)
 source_passages=run(storage.passages(IDENTITY,study,deadline()))['items'];destination_passages=run(storage.passages(IDENTITY,copied['study_id'],deadline()))['items']
 assert [p['reference'] for p in destination_passages]==[p['reference'] for p in source_passages]
