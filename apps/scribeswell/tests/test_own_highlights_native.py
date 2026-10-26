"""PREPARED ONLY. Native private aggregation tests; never collected/executed here.

Actual public proof uses the separate reader-evidence native suite. These tests
use connections-only aggregates so no source observation double certifies proof.
"""
import asyncio
import json
import os
from uuid import uuid4
from urllib.parse import urlsplit
import psycopg
from psycopg.types.json import Jsonb
import pytest
from test_personal_notes_storage import native,create,command,run,deadline,IDENTITY,A,B,ACTOR
from personal_notes_access import NotesError
from passage_references import parse_reference

@pytest.fixture
def own_native(request):
 if os.environ.get('SCRIBESWELL_OWN_HIGHLIGHTS_NATIVE')!='1':pytest.skip('explicit final-phase native qualification only')
 assert urlsplit(os.environ.get('SCRIBESWELL_NOTES_TEST_ADMIN_URL','')).port not in (55481,55482)
 return request.getfixturevalue('native')

def aggregate():return {'format_version':3,'document':{'version':1,'blocks':[]},'connections':[{'id':str(uuid4()),'reference':parse_reference('Gen1:1')}],'highlights':[]}
def created(fixture):
 storage,*_=fixture;study=create(storage)['study_id'];ack=run(storage.execute(IDENTITY,'note.create',command('note.create',value=aggregate()),study,None,deadline()));return storage,study,ack

def test_native_metadata_atomic_immutable_owner_scoped_without_body(own_native):
 storage,study,ack=created(own_native);_,admin,runtime,_=own_native
 with psycopg.connect(runtime) as db:
  db.execute("SELECT set_config('app.account_id',%s,true)",(A,));row=db.execute('SELECT metadata FROM scribeswell_studies.note_revision_metadata WHERE note_id=%s',(ack['note_id'],)).fetchone()[0]
  assert set(row)=={'connections','highlights','references'} and 'document' not in json.dumps(row)
  assert row['references']==[parse_reference('Gen1:1')]
  db.execute("SELECT set_config('app.account_id',%s,true)",(B,));assert db.execute('SELECT count(*) FROM scribeswell_studies.note_revision_metadata').fetchone()==(0,)
 for statement in ['UPDATE scribeswell_studies.note_revision_metadata SET metadata=metadata','DELETE FROM scribeswell_studies.note_revision_metadata','TRUNCATE scribeswell_studies.note_revision_metadata','ALTER TABLE scribeswell_studies.note_revision_metadata ADD forbidden integer']:
  with psycopg.connect(runtime) as db:
   db.execute("SELECT set_config('app.account_id',%s,true)",(A,))
   with pytest.raises(psycopg.Error):db.execute(statement)
 # Owner bypass does not permit history mutation either.
 with psycopg.connect(admin) as db:
  with pytest.raises(psycopg.errors.CheckViolation):db.execute('UPDATE scribeswell_studies.note_revision_metadata SET metadata=metadata')

def test_native_old_writer_cannot_erase_format3_or_forge_base_metadata(own_native):
 storage,study,ack=created(own_native);_,_,runtime,_=own_native
 empty={'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}
 with psycopg.connect(runtime) as db:
  db.execute("SELECT set_config('app.account_id',%s,true)",(A,))
  with pytest.raises(psycopg.errors.CheckViolation):db.execute('UPDATE scribeswell_studies.notes SET value=%s WHERE id=%s',(Jsonb(empty),ack['note_id']))
 with psycopg.connect(runtime) as db:
  db.execute("SELECT set_config('app.account_id',%s,true)",(A,))
  with pytest.raises(psycopg.errors.CheckViolation):db.execute('INSERT INTO scribeswell_studies.note_revision_metadata(account_id,study_id,note_id,revision,metadata,created_by) VALUES(%s,%s,%s,2,%s,%s)',(A,study,ack['note_id'],Jsonb({'connections':[],'highlights':[],'references':[]}),ACTOR))
 assert run(storage.read(IDENTITY,study,ack['note_id'],deadline()))['revision']=='1'

def test_native_competing_aggregate_updates_keep_one_revision_and_all_metadata(own_native):
 storage,study,ack=created(own_native)
 async def race():
  return await asyncio.gather(*(storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision='1',value=aggregate()),study,ack['note_id'],deadline()) for _ in range(2)),return_exceptions=True)
 results=run(race());assert sum(isinstance(r,dict) for r in results)==1
 assert any(isinstance(r,NotesError) and r.code=='note_revision_conflict' for r in results)
 with psycopg.connect(own_native[2]) as db:
  db.execute("SELECT set_config('app.account_id',%s,true)",(A,));assert db.execute('SELECT revision FROM scribeswell_studies.note_revision_metadata WHERE note_id=%s ORDER BY revision',(ack['note_id'],)).fetchall()==[(1,),(2,)]

def test_native_metadata_failure_rolls_back_note_and_receipt(own_native):
 storage,study,ack=created(own_native);_,admin,_,_=own_native
 with psycopg.connect(admin) as db:
  db.execute("CREATE FUNCTION scribeswell_studies.synthetic_metadata_fail() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic' USING ERRCODE='23514'; END $$")
  db.execute('CREATE TRIGGER synthetic_metadata_fail BEFORE INSERT ON scribeswell_studies.note_revision_metadata FOR EACH ROW EXECUTE FUNCTION scribeswell_studies.synthetic_metadata_fail()')
 attempt=command('note.replace',expected_revision='1',value=aggregate())
 try:
  with pytest.raises(NotesError):run(storage.execute(IDENTITY,'note.replace',attempt,study,ack['note_id'],deadline()))
  assert run(storage.read(IDENTITY,study,ack['note_id'],deadline()))['revision']=='1'
  assert run(storage.lookup(IDENTITY,attempt.operation_id,'note.replace',deadline()))=={'status':'unresolved'}
 finally:
  with psycopg.connect(admin) as db:db.execute('DROP TRIGGER synthetic_metadata_fail ON scribeswell_studies.note_revision_metadata');db.execute('DROP FUNCTION scribeswell_studies.synthetic_metadata_fail()')
 assert run(storage.execute(IDENTITY,'note.replace',attempt,study,ack['note_id'],deadline()))['revision']=='2'

def test_native_search_derives_connections_once_without_collection(own_native):
 from personal_notes_contract import parse_command
 storage,study,ack=created(own_native)
 query=parse_command('studies.search',json.dumps({'query':'Gen1:1'}).encode())
 result=run(storage.search(IDENTITY,query,deadline()))
 assert [s['id'] for s in result['items']].count(study)==1
 assert run(storage.passages(IDENTITY,study,deadline()))['items']==[]
