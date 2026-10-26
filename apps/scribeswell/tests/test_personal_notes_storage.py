"""Actual restricted-login PostgreSQL proof; requires an explicitly disposable fixture."""
import asyncio
import json
import os
from pathlib import Path
import sys
import time
from uuid import uuid4
import pytest
import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from personal_notes_storage import PersonalNotesStorage
from personal_notes_contract import parse_command
from personal_notes_access import NotesError

APP=Path(__file__).resolve().parents[1]
A='10000000-0000-4000-8000-000000000001'; B='10000000-0000-4000-8000-000000000002'
ACTOR='20000000-0000-4000-8000-000000000001'
IDENTITY={'account_id':A,'actor_id':ACTOR}

def command(kind,**fields):return parse_command(kind,json.dumps({'operation_id':str(uuid4()),**fields},ensure_ascii=False).encode())
def value(text='בְּרֵאשִׁית'):
    return {'document':{'version':1,'blocks':[{'type':'paragraph','direction':'rtl','content':[{'type':'text','text':text,'marks':[]}]}]},'connections':[],'highlights':[]}
def run(coro):return asyncio.run(coro)
def close_study(storage,study):
    current=run(storage.read(IDENTITY,study,None,deadline()))
    return run(storage.execute(IDENTITY,'study.delete',command('study.delete',expected_revision=current['revision']),study,None,deadline()))
def deadline():return time.monotonic()+5

@pytest.fixture(scope='module')
def native():
    raw=os.environ.get('SCRIBESWELL_NOTES_TEST_ADMIN_URL')
    if not raw:pytest.skip('Explicit isolated PostgreSQL17+ fixture required')
    url=make_url(raw)
    assert url.host=='127.0.0.1' and url.database=='postgres'
    database='scribeswell_notes_'+uuid4().hex
    roles=['scribeswell_studies_migrator','scribeswell_studies_runtime','scribeswell_studies_operator']
    public_roles=['anon','authenticated','service_role','scribeswell_runtime']
    with psycopg.connect(raw,autocommit=True) as admin:
        assert int(admin.execute('SHOW server_version_num').fetchone()[0])>=170000
        assert not admin.execute('SELECT rolname FROM pg_roles WHERE rolname=ANY(%s)',(roles+public_roles,)).fetchall(),'Fresh cluster required'
        for role in public_roles:admin.execute(sql.SQL("CREATE ROLE {} LOGIN PASSWORD 'synthetic-only'").format(sql.Identifier(role)))
        admin.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(database)))
    admin_url=url.set(database=database).render_as_string(hide_password=False)
    with psycopg.connect(admin_url,autocommit=True) as admin:
        admin.execute(sql.SQL('REVOKE TEMPORARY ON DATABASE {} FROM PUBLIC').format(sql.Identifier(database)))
        admin.execute((APP/'tools/sql/prepare_personal_notes_roles.sql').read_text())
        # Authoritative previous public schema with actual pre-existing corpus rows.
        admin.execute((APP/'supabase/migrations/20260614000000_scribeswell_create_schema.sql').read_text())
        admin.execute("INSERT INTO scribeswell.book VALUES(1,'Gen','Genesis','בראשית','old','torah',1);INSERT INTO scribeswell.chapter(id,book_id,chapter_num) VALUES(1,1,1);INSERT INTO scribeswell.verse(id,chapter_id,verse_num,book_id,chapter_num) VALUES(1,1,1,1,1);INSERT INTO scribeswell.word(id,verse_id,position,surface_he) VALUES(1,1,1,'בְּרֵאשִׁית')")
        admin.execute('GRANT USAGE ON SCHEMA scribeswell TO scribeswell_runtime;GRANT SELECT ON ALL TABLES IN SCHEMA scribeswell TO scribeswell_runtime')
        for table in ('book','chapter','verse','word','morpheme'):
            admin.execute(sql.SQL('CREATE POLICY previous_runtime_read ON scribeswell.{} FOR SELECT TO scribeswell_runtime USING(true)').format(sql.Identifier(table)))
        admin.execute("ALTER ROLE scribeswell_studies_migrator PASSWORD 'synthetic-only'")
        admin.execute("ALTER ROLE scribeswell_studies_runtime PASSWORD 'synthetic-only'")
        admin.execute('CREATE SCHEMA foreign_owner; CREATE TABLE foreign_owner.sentinel(id integer); INSERT INTO foreign_owner.sentinel VALUES(1)')
    migrator=url.set(database=database,username=roles[0],password='synthetic-only').render_as_string(hide_password=False)
    runtime=url.set(database=database,username=roles[1],password='synthetic-only').render_as_string(hide_password=False)
    from alembic.config import Config
    from alembic import command as alembic
    previous=os.environ.get('SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL')
    os.environ['SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL']=migrator
    from database import Database
    from services import bible_service
    public_url=url.set(database=database,username='scribeswell_runtime',password='synthetic-only').render_as_string(hide_password=False)
    previous_consumer=Database(public_url,'scribeswell_runtime');previous_consumer.open()
    def previous_read():
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(bible_service,'get_database',lambda:previous_consumer)
            return bible_service.get_books().model_dump(mode='json')
    public_before=previous_read();assert public_before['data'][0]['osis_id']=='Gen'
    try:
        # Preserve the old controlled entry's head-only rule; qualify its frozen history.
        import tempfile,shutil
        with tempfile.TemporaryDirectory(prefix='scribeswell-previous-history-') as directory:
            target=Path(directory)
            shutil.copytree(APP/'studies-migrations',target/'history')
            shutil.copytree(APP/'studies-database-tools',target/'studies-database-tools')
            (target/'history/versions/0002_study_rename.py').unlink()
            (target/'history/versions/0003_collected_passages.py').unlink()
            (target/'history/versions/0004_note_deletion.py').unlink()
            (target/'history/versions/0005_study_deletion.py').unlink()
            (target/'history/versions/0006_own_highlights.py').unlink()
            old_config=Config();old_config.set_main_option('script_location',str(target/'history'))
            alembic.upgrade(old_config,'head')
        import importlib.util
        previous_spec=importlib.util.spec_from_file_location('previous_notes_sql_consumer',APP/'tests/fixtures/personal_notes_storage_previous.py')
        previous_module=importlib.util.module_from_spec(previous_spec);previous_spec.loader.exec_module(previous_module)
        old_storage=previous_module.PersonalNotesStorage(runtime)
        old_study=create(old_storage,'Previous consumer title')['study_id']
        old_note=run(old_storage.execute(IDENTITY,'note.create',command('note.create',value=value('previous consumer')),old_study,None,deadline()))
        old_before=run(old_storage.read(IDENTITY,old_study,old_note['note_id'],deadline()))
        # Fail after the actual 0002 ALTERs, then prove transactional rollback and forward retry.
        with tempfile.TemporaryDirectory(prefix='scribeswell-rename-failure-') as directory:
            target=Path(directory)
            shutil.copytree(APP/'studies-migrations',target/'history')
            shutil.copytree(APP/'studies-database-tools',target/'studies-database-tools')
            migration=target/'history/versions/0002_study_rename.py'
            migration.write_text(migration.read_text().replace('\ndef downgrade():', "\n    raise RuntimeError('synthetic failure after rename ALTERs')\n\ndef downgrade():"))
            failed_config=Config();failed_config.set_main_option('script_location',str(target/'history'))
            with pytest.raises(Exception,match='scribeswell_studies_migration_failed'):alembic.upgrade(failed_config,'head')
            with psycopg.connect(admin_url) as admin:
                assert admin.execute('SELECT version_num FROM scribeswell_studies.alembic_version').fetchone()[0]=='scribeswell_studies_0001'
                checks=admin.execute("SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='scribeswell_studies.receipts'::regclass AND contype='c'").fetchall()
                assert all('study.rename' not in definition for (definition,) in checks)
            assert run(old_storage.read(IDENTITY,old_study,old_note['note_id'],deadline()))==old_before
        # Freeze the immediate previous0002 consumer before testing additive0003 failure.
        with tempfile.TemporaryDirectory(prefix='scribeswell-previous-rename-history-') as directory:
            target=Path(directory);shutil.copytree(APP/'studies-migrations',target/'history');shutil.copytree(APP/'studies-database-tools',target/'studies-database-tools')
            (target/'history/versions/0003_collected_passages.py').unlink()
            (target/'history/versions/0004_note_deletion.py').unlink()
            (target/'history/versions/0005_study_deletion.py').unlink()
            (target/'history/versions/0006_own_highlights.py').unlink()
            cfg=Config();cfg.set_main_option('script_location',str(target/'history'));alembic.upgrade(cfg,'head')
        with tempfile.TemporaryDirectory(prefix='scribeswell-passages-failure-') as directory:
            target=Path(directory);shutil.copytree(APP/'studies-migrations',target/'history');shutil.copytree(APP/'studies-database-tools',target/'studies-database-tools')
            migration=target/'history/versions/0003_collected_passages.py'
            migration.write_text(migration.read_text().replace('\ndef downgrade():', "\n    raise RuntimeError('synthetic failure after collection DDL')\n\ndef downgrade():"))
            cfg=Config();cfg.set_main_option('script_location',str(target/'history'))
            with pytest.raises(Exception,match='scribeswell_studies_migration_failed'):alembic.upgrade(cfg,'head')
            with psycopg.connect(admin_url) as admin:
                assert admin.execute('SELECT version_num FROM scribeswell_studies.alembic_version').fetchone()[0]=='scribeswell_studies_0002'
                assert admin.execute("SELECT to_regclass('scribeswell_studies.passage_lists'),to_regclass('scribeswell_studies.passage_entries')").fetchone()==(None,None)
            assert run(old_storage.read(IDENTITY,old_study,old_note['note_id'],deadline()))==old_before
        # Real previous checkpoint/schema, invalid legacy tombstone and transactional0004 refusal.
        with tempfile.TemporaryDirectory(prefix='scribeswell-previous-deletion-history-') as directory:
            target=Path(directory);shutil.copytree(APP/'studies-migrations',target/'history');shutil.copytree(APP/'studies-database-tools',target/'studies-database-tools')
            (target/'history/versions/0004_note_deletion.py').unlink()
            (target/'history/versions/0005_study_deletion.py').unlink()
            (target/'history/versions/0006_own_highlights.py').unlink()
            cfg=Config();cfg.set_main_option('script_location',str(target/'history'));alembic.upgrade(cfg,'head')
        sys.path.insert(0,str(APP/'tests/fixtures'))
        from note_deletion_baseline_loader import load
        baseline_contract,baseline_storage=load();checkpoint=baseline_storage.PersonalNotesStorage(runtime)
        legacy=run(checkpoint.execute(IDENTITY,'note.create',baseline_contract.parse_command('note.create',json.dumps({'operation_id':str(uuid4()),'value':value('legacy inactive payload')}).encode()),old_study,None,deadline()))
        with psycopg.connect(admin_url) as admin:admin.execute('UPDATE scribeswell_studies.notes SET active=false WHERE id=%s',(legacy['note_id'],))
        with pytest.raises(Exception,match='scribeswell_studies_migration_failed'):alembic.upgrade(Config(str(APP/'studies-alembic.ini')),'head')
        with psycopg.connect(admin_url) as admin:
            assert admin.execute('SELECT version_num FROM scribeswell_studies.alembic_version').fetchone()[0]=='scribeswell_studies_0003'
            assert admin.execute('SELECT value FROM scribeswell_studies.notes WHERE id=%s',(legacy['note_id'],)).fetchone()[0]==value('legacy inactive payload')
            assert not admin.execute("SELECT 1 FROM pg_constraint WHERE conname='notes_closed_value_empty'").fetchone()
            # Explicit fixture-only forward repair; migration itself never adopts/erases data.
            admin.execute('UPDATE scribeswell_studies.notes SET value=%s WHERE id=%s',(psycopg.types.json.Jsonb({'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}),legacy['note_id']))
        # Stop at0004 to construct the concrete preexisting closed-parent failure.
        with tempfile.TemporaryDirectory(prefix='scribeswell-previous-study-deletion-') as directory:
            target=Path(directory);shutil.copytree(APP/'studies-migrations',target/'history');shutil.copytree(APP/'studies-database-tools',target/'studies-database-tools')
            (target/'history/versions/0005_study_deletion.py').unlink()
            (target/'history/versions/0006_own_highlights.py').unlink()
            cfg=Config();cfg.set_main_option('script_location',str(target/'history'));alembic.upgrade(cfg,'head')
        sys.path.insert(0,str(APP/'tests/fixtures'))
        from study_deletion_baseline_loader import load as study_baseline
        previous_contract,previous_storage=study_baseline();previous_study=previous_storage.PersonalNotesStorage(runtime)
        invalid_parent=run(previous_study.execute(IDENTITY,'study.create',previous_contract.parse_command('study.create',json.dumps({'operation_id':str(uuid4()),'title':'Deleted study'}).encode()),None,None,deadline()))['study_id']
        invalid_child=run(previous_study.execute(IDENTITY,'note.create',previous_contract.parse_command('note.create',json.dumps({'operation_id':str(uuid4()),'value':value('preexisting violation must survive')}).encode()),invalid_parent,None,deadline()))['note_id']
        with psycopg.connect(admin_url) as admin:admin.execute('UPDATE scribeswell_studies.studies SET active=false WHERE id=%s',(invalid_parent,))
        with psycopg.connect(migrator) as owner:
            assert not owner.execute('SELECT rolbypassrls FROM pg_roles WHERE rolname=current_user').fetchone()[0]
            assert owner.execute('SELECT count(*) FROM scribeswell_studies.notes').fetchone()[0]==0
        with pytest.raises(Exception,match='scribeswell_studies_migration_failed'):alembic.upgrade(Config(str(APP/'studies-alembic.ini')),'head')
        with psycopg.connect(admin_url) as admin:
            assert admin.execute('SELECT version_num FROM scribeswell_studies.alembic_version').fetchone()[0]=='scribeswell_studies_0004'
            assert admin.execute('SELECT value FROM scribeswell_studies.notes WHERE id=%s',(invalid_child,)).fetchone()[0]==value('preexisting violation must survive')
            assert all(row[0] for row in admin.execute("SELECT relforcerowsecurity FROM pg_class WHERE oid=ANY(ARRAY['scribeswell_studies.studies'::regclass,'scribeswell_studies.notes'::regclass,'scribeswell_studies.passage_lists'::regclass,'scribeswell_studies.passage_entries'::regclass])").fetchall())
            assert not admin.execute("SELECT 1 FROM pg_trigger WHERE tgname='active_study_insert'").fetchone()
            # Explicit fixture-only controlled forward repair, never migration adoption.
            admin.execute('UPDATE scribeswell_studies.notes SET active=false,value=%s WHERE id=%s',(psycopg.types.json.Jsonb({'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}),invalid_child))
        alembic.upgrade(Config(str(APP/'studies-alembic.ini')),'head')
        assert run(checkpoint.read(IDENTITY,old_study,old_note['note_id'],deadline()))['value']==old_before['value']
        run(checkpoint.execute(IDENTITY,'note.replace',baseline_contract.parse_command('note.replace',json.dumps({'operation_id':str(uuid4()),'expected_revision':'1','value':old_before['value']}).encode()),old_study,old_note['note_id'],deadline()))
        assert run(old_storage.read(IDENTITY,old_study,old_note['note_id'],deadline()))==old_before
        assert run(old_storage.lookup(IDENTITY,old_note['operation_id'],'note.create',deadline()))['outcome']==old_note
        run(old_storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision='1',value=value('previous consumer still writes')),old_study,old_note['note_id'],deadline()))
        alembic.upgrade(Config(str(APP/'studies-alembic.ini')),'head')
        assert previous_read()==public_before
        yield PersonalNotesStorage(runtime),admin_url,runtime,migrator
    finally:
        assert previous_read()==public_before
        previous_consumer.close()
        if previous is None:os.environ.pop('SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL',None)
        else:os.environ['SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL']=previous
        # Teardown only this randomly allocated database/roles in the explicit fresh fixture.
        with psycopg.connect(raw,autocommit=True) as admin:
            admin.execute(sql.SQL('DROP DATABASE {} WITH (FORCE)').format(sql.Identifier(database)))
            for role in roles+public_roles:admin.execute(sql.SQL('DROP ROLE {}').format(sql.Identifier(role)))

def create(storage,title=None):return run(storage.execute(IDENTITY,'study.create',command('study.create',title=title),None,None,deadline()))
def test_native_create_write_reopen_noop_replay_and_isolation(native):
    storage,_,_,_=native
    study=create(storage)['study_id']; payload=command('note.create',value=value())
    ack=run(storage.execute(IDENTITY,'note.create',payload,study,None,deadline()))
    assert run(storage.execute(IDENTITY,'note.create',payload,study,None,deadline()))==ack
    current=run(storage.read(IDENTITY,study,ack['note_id'],deadline()))
    assert current['value']==value()
    noop=run(storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision='1',value=value()),study,ack['note_id'],deadline()))
    assert noop['revision']=='1'
    assert run(storage.read(IDENTITY,study,ack['note_id'],deadline()))==current
    replacement=command('note.replace',expected_revision='1',value=value('שָׁלוֹם'))
    updated=run(storage.execute(IDENTITY,'note.replace',replacement,study,ack['note_id'],deadline()))
    assert updated['revision']=='2'
    assert run(storage.lookup(IDENTITY,replacement.operation_id,'note.replace',deadline()))=={'status':'committed','outcome':updated}
    with pytest.raises(NotesError,match='note_revision_conflict'):
        run(storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision='1',value=value()),study,ack['note_id'],deadline()))
    changed=replacement.model_copy(update={'value':command('note.create',value=value('different')).value})
    with pytest.raises(NotesError,match='operation_payload_mismatch'):run(storage.execute(IDENTITY,'note.replace',changed,study,ack['note_id'],deadline()))
    other={'account_id':B,'actor_id':ACTOR}
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.read(other,study,ack['note_id'],deadline()))
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute(other,'note.create',command('note.create',value=value('forbidden')),study,None,deadline()))
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute(other,'note.replace',command('note.replace',expected_revision='2',value=value('forbidden')),study,ack['note_id'],deadline()))
    assert run(storage.list(other,None,20,None,deadline()))['items']==[]
    assert run(storage.lookup(other,replacement.operation_id,'note.replace',deadline()))=={'status':'unresolved'}

def test_concurrent_default_titles_and_same_operation(native):
    storage,*_=native
    async def races():
        results=await asyncio.gather(*(storage.execute(IDENTITY,'study.create',command('study.create',title=None),None,None,deadline()) for _ in range(6)))
        assert len({r['study_id'] for r in results})==6
        payload=command('study.create',title=None)
        same=await asyncio.gather(*(storage.execute(IDENTITY,'study.create',payload,None,None,deadline()) for _ in range(5)))
        assert all(r==same[0] for r in same)
        listed=await storage.list(IDENTITY,None,50,None,deadline())
        titles=[s['title'] for s in listed['items']]
        assert len(titles)==len(set(titles))
    run(races())

def test_native_restricted_roles_constraints_and_closed_resource(native):
    storage,admin_url,runtime,_=native
    study=create(storage,'Closed test')['study_id']; payload=command('note.create',value=value())
    ack=run(storage.execute(IDENTITY,'note.create',payload,study,None,deadline()))
    with psycopg.connect(runtime) as c:
        assert c.execute('SELECT count(*) FROM scribeswell_studies.studies').fetchone()[0]==0
    for role in ('anon','authenticated','service_role','scribeswell_runtime'):
        public_url=make_url(runtime).set(username=role,password='synthetic-only').render_as_string(hide_password=False)
        with psycopg.connect(public_url) as c:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):c.execute('SELECT * FROM scribeswell_studies.studies')
    for statement in ('CREATE TEMP TABLE forbidden_temp(id int)','CREATE TABLE scribeswell_studies.forbidden(id int)','SELECT * FROM scribeswell_studies.alembic_version','SELECT * FROM foreign_owner.sentinel',
                      'UPDATE scribeswell_studies.receipts SET fingerprint=fingerprint','DELETE FROM scribeswell_studies.notes','SET ROLE scribeswell_studies_migrator'):
        with psycopg.connect(runtime) as c:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):c.execute(statement)
    with psycopg.connect(runtime) as c:
        c.execute("SELECT set_config('app.account_id',%s,true)",(A,))
        with pytest.raises(psycopg.errors.InsufficientPrivilege):c.execute('UPDATE scribeswell_studies.notes SET created_by=%s WHERE id=%s',(ACTOR,ack['note_id']))
    close_study(storage,study)
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute(IDENTITY,'note.create',payload,study,None,deadline()))
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.lookup(IDENTITY,payload.operation_id,'note.create',deadline()))

def test_native_revision_race_and_deadline(native):
    storage,_,runtime,_=native
    study=create(storage)['study_id']; ack=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value()),study,None,deadline()))
    async def race():
        results=await asyncio.gather(*(storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision='1',value=value(str(i))),study,ack['note_id'],deadline()) for i in range(2)),return_exceptions=True)
        assert sum(isinstance(r,NotesError) and r.code=='note_revision_conflict' for r in results)==1
        assert sum(isinstance(r,dict) and r.get('revision')=='2' for r in results)==1
    run(race())
    with psycopg.connect(runtime) as lock:
        lock.execute("SELECT set_config('app.account_id',%s,true)",(A,))
        lock.execute('SELECT id FROM scribeswell_studies.studies WHERE id=%s FOR UPDATE',(study,))
        started=time.monotonic()
        with pytest.raises(NotesError,match='request_deadline_exceeded'):
            run(storage.execute(IDENTITY,'note.create',command('note.create',value=value()),study,None,time.monotonic()+.15))
        assert time.monotonic()-started<1

def test_cursor_owner_parent_and_pagination(native):
    storage,*_=native
    first=run(storage.list(IDENTITY,None,1,None,deadline()))
    assert first['next_cursor']
    second=run(storage.list(IDENTITY,None,1,first['next_cursor'],deadline()))
    assert first['items'][0]['id']!=second['items'][0]['id']
    with pytest.raises(NotesError,match='input_invalid'):run(storage.list({'account_id':B,'actor_id':ACTOR},None,1,first['next_cursor'],deadline()))

def test_native_migration_failure_rollback_retry_and_owner_force_rls(native):
    storage,admin_url,runtime,migrator=native
    from alembic import command as alembic
    from alembic.config import Config
    study=create(storage,'Before migration failure')['study_id']
    saved=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value('acknowledged before failure')),study,None,deadline()))
    before=run(storage.read(IDENTITY,study,saved['note_id'],deadline()))
    # A copied history is owned by this fixture; ordinary Alembic resolves its ledger.
    import tempfile,shutil
    with tempfile.TemporaryDirectory(prefix='scribeswell-notes-migration-') as directory:
        target=Path(directory);shutil.copytree(APP/'studies-migrations',target/'history')
        shutil.copytree(APP/'studies-database-tools',target/'studies-database-tools')
        env=(target/'history/env.py').read_text().replace("parents[1]/'studies-database-tools'","parents[1]/'studies-database-tools'")
        (target/'history/env.py').write_text(env)
        failure=target/'history/versions/0006_failure.py'
        failure.write_text("from alembic import op\nrevision='fixture_0006'\ndown_revision='scribeswell_studies_0005'\ndef upgrade():\n op.execute('CREATE TABLE scribeswell_studies.failure_probe(id int)')\n raise RuntimeError('synthetic failure')\n")
        cfg=Config();cfg.set_main_option('script_location',str(target/'history'))
        with pytest.raises(Exception,match='scribeswell_studies_migration_failed'):alembic.upgrade(cfg,'head')
        with psycopg.connect(admin_url) as admin:
            assert admin.execute("SELECT to_regclass('scribeswell_studies.failure_probe')").fetchone()[0] is None
            assert admin.execute('SELECT version_num FROM scribeswell_studies.alembic_version').fetchone()[0]=='scribeswell_studies_0005'
        failure.write_text(failure.read_text().replace(" raise RuntimeError('synthetic failure')",''))
        alembic.upgrade(cfg,'head');alembic.upgrade(cfg,'head')
        assert run(storage.read(IDENTITY,study,saved['note_id'],deadline()))==before
    with psycopg.connect(migrator) as owner:
        assert owner.execute('SELECT count(*) FROM scribeswell_studies.notes').fetchone()[0]==0
    with psycopg.connect(runtime) as c:
        c.execute("SELECT set_config('app.account_id',%s,true)",(A,))
        with pytest.raises(psycopg.errors.InsufficientPrivilege):c.execute('INSERT INTO scribeswell_studies.studies(id,account_id,title,created_by,updated_by) VALUES(%s,%s,%s,%s,%s)',(str(uuid4()),B,'forbidden',ACTOR,ACTOR))

def test_native_receipt_survives_lost_response_and_scope_constraints(native):
    storage,admin_url,runtime,_=native
    payload=command('study.create',title='Lost response')
    # Commit to PostgreSQL, deliberately discard the original response, recover by lookup/replay.
    run(storage.execute(IDENTITY,'study.create',payload,None,None,deadline()))
    recovered=run(storage.lookup(IDENTITY,payload.operation_id,'study.create',deadline()))
    assert recovered['status']=='committed'
    assert run(storage.execute(IDENTITY,'study.create',payload,None,None,deadline()))==recovered['outcome']
    with psycopg.connect(runtime) as c:
        c.execute("SELECT set_config('app.account_id',%s,true)",(A,))
        with pytest.raises(psycopg.errors.CheckViolation):c.execute('INSERT INTO scribeswell_studies.notes(id,account_id,study_id,value,created_by,updated_by) VALUES(%s,%s,%s,%s,%s,%s)',(str(uuid4()),A,str(uuid4()),psycopg.types.json.Jsonb(value()),ACTOR,ACTOR))
    study=recovered['outcome']['study_id'];ack=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value()),study,None,deadline()))
    with psycopg.connect(admin_url) as c:c.execute('UPDATE scribeswell_studies.notes SET revision=9223372036854775807 WHERE id=%s',(ack['note_id'],))
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision='9223372036854775807',value=value('overflow')),study,ack['note_id'],deadline()))

def test_native_browser_create_write_reopen(native):
    if os.environ.get('SCRIBESWELL_NOTES_BROWSER_QUALIFY')!='true':pytest.skip('Explicit browser qualification opt-in required')
    import socket,threading,subprocess
    import uvicorn
    from fastapi import FastAPI,Request
    from personal_notes_router import build_router
    from personal_notes_access import StudiesAccess
    from fastapi.responses import JSONResponse
    from datetime import datetime,timezone
    owner=FastAPI()
    @owner.post('/v2/check')
    async def check(request:Request):
        assert request.headers['x-service-key']=='synthetic-server-only'
        assert await request.json()=={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}}
        return {'account_id':A,'actor_id':ACTOR,'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'},'decision_id':str(uuid4()),'checked_at':datetime.now(timezone.utc).isoformat()}
    @owner.post('/v2/enrollments/scribeswell-studies')
    async def enroll(request:Request):
        payload=await request.json()
        return {'operation_id':payload['operation_id'],'status':'committed','result':{'disposition':'created','account_id':A,'actor_id':ACTOR,'permission':'scribeswell.studies.use'}}
    servers=[]
    def start(app):
        sock=socket.socket();sock.bind(('127.0.0.1',0));sock.listen(128)
        server=uvicorn.Server(uvicorn.Config(app,log_level='critical',access_log=False));thread=threading.Thread(target=server.run,kwargs={'sockets':[sock]},daemon=True);thread.start();servers.append((server,thread,sock));end=time.monotonic()+5
        while not server.started:
            if time.monotonic()>end:raise RuntimeError('Fixture startup deadline')
            time.sleep(.01)
        return f'http://127.0.0.1:{sock.getsockname()[1]}'
    try:
        access_url=start(owner);api_app=FastAPI();api_app.include_router(build_router(StudiesAccess(access_url,'synthetic-server-only'),native[0]));api_url=start(api_app)
        # Earlier storage scenarios belong to this same fixture; browser needs an unused default name.
        # Release default names only; preserve earlier overflow rows and lifecycle evidence.
        with psycopg.connect(native[1]) as c:c.execute("UPDATE scribeswell_studies.studies SET title='Fixture '||id::text WHERE active AND title LIKE 'Untitled study%'")
        env={**os.environ,'SCRIBESWELL_NOTES_NATIVE_API':api_url}
        result=subprocess.run(['npm','run','test:browser','--workspace=apps/scribeswell/web','--','personal-notes.spec.cjs','--project=desktop','--grep','native PostgreSQL'],env=env,cwd=APP.parents[1],timeout=90,capture_output=True,text=True)
        assert result.returncode==0,result.stdout+result.stderr
    finally:
        for server,thread,sock in reversed(servers):server.should_exit=True;thread.join(timeout=5);sock.close()


def test_native_unknown_commit_outcome_resolves_same_receipt(native,monkeypatch):
    storage,*_=native
    payload=command('study.create',title='Uncertain commit response')
    original=psycopg.AsyncConnection.commit
    async def lost_commit(connection):
        await original(connection)
        raise psycopg.OperationalError('synthetic commit response loss')
    with monkeypatch.context() as patch:
        patch.setattr(psycopg.AsyncConnection,'commit',lost_commit)
        with pytest.raises(NotesError,match='operation_unresolved'):
            run(storage.execute(IDENTITY,'study.create',payload,None,None,deadline()))
    outcome=run(storage.lookup(IDENTITY,payload.operation_id,'study.create',deadline()))
    assert outcome['status']=='committed'
    assert run(storage.execute(IDENTITY,'study.create',payload,None,None,deadline()))==outcome['outcome']



def test_native_rename_noop_replay_conflict_attribution_and_independent_note(native):
    storage,admin_url,_,_=native
    study=create(storage,'Original')['study_id']
    saved=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value()),study,None,deadline()))
    note_before=run(storage.read(IDENTITY,study,saved['note_id'],deadline()))
    before=run(storage.read(IDENTITY,study,None,deadline()))
    noop=command('study.rename',expected_revision='1',title='Original')
    assert run(storage.execute(IDENTITY,'study.rename',noop,study,None,deadline()))['revision']=='1'
    assert run(storage.read(IDENTITY,study,None,deadline()))==before
    rename=command('study.rename',expected_revision='1',title='  English שָׁלוֹם  ')
    ack=run(storage.execute(IDENTITY,'study.rename',rename,study,None,deadline()))
    assert ack['revision']=='2' and ack['note_id'] is None
    after=run(storage.read(IDENTITY,study,None,deadline()))
    assert after['title']==rename.title and after['updated_by_actor_id']==ACTOR
    assert after['created_at']==before['created_at'] and after['created_by_actor_id']==before['created_by_actor_id']
    assert after['updated_at']>before['updated_at']
    assert run(storage.read(IDENTITY,study,saved['note_id'],deadline()))==note_before
    assert run(storage.lookup(IDENTITY,rename.operation_id,'study.rename',deadline()))=={'status':'committed','outcome':ack}
    later=command('study.rename',expected_revision='2',title='Later title')
    run(storage.execute(IDENTITY,'study.rename',later,study,None,deadline()))
    assert run(storage.execute(IDENTITY,'study.rename',rename,study,None,deadline()))==ack
    assert run(storage.read(IDENTITY,study,None,deadline()))['title']=='Later title'
    with pytest.raises(NotesError,match='operation_payload_mismatch'):
        run(storage.execute(IDENTITY,'study.rename',rename.model_copy(update={'title':'forged'}),study,None,deadline()))
    with pytest.raises(NotesError,match='operation_payload_mismatch'):
        run(storage.execute(IDENTITY,'study.rename',rename,str(uuid4()),None,deadline()))
    with pytest.raises(NotesError,match='study_revision_conflict'):
        run(storage.execute(IDENTITY,'study.rename',command('study.rename',expected_revision='1',title='stale'),study,None,deadline()))
    with pytest.raises(NotesError,match='resource_unavailable'):
        run(storage.execute({'account_id':B,'actor_id':ACTOR},'study.rename',rename,study,None,deadline()))
    with psycopg.connect(admin_url) as c:
        assert c.execute("SELECT count(*) FROM scribeswell_studies.receipts WHERE command='study.rename' AND operation_id=%s",(rename.operation_id,)).fetchone()[0]==1
    close_study(storage,study)
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute(IDENTITY,'study.rename',rename,study,None,deadline()))
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.lookup(IDENTITY,rename.operation_id,'study.rename',deadline()))


def test_native_rename_and_note_races_preserve_both_and_metadata_cas(native):
    storage,*_=native
    study=create(storage,'Race')['study_id']
    note=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value()),study,None,deadline()))
    async def race():
        results=await asyncio.gather(storage.execute(IDENTITY,'study.rename',command('study.rename',expected_revision='1',title='Renamed race'),study,None,deadline()),storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision='1',value=value('Independent note')),study,note['note_id'],deadline()))
        assert [r['revision'] for r in results]==['2','2']
        results=await asyncio.gather(*(storage.execute(IDENTITY,'study.rename',command('study.rename',expected_revision='2',title=str(i)),study,None,deadline()) for i in range(2)),return_exceptions=True)
        assert sum(isinstance(r,NotesError) and r.code=='study_revision_conflict' for r in results)==1
        assert sum(isinstance(r,dict) and r.get('revision')=='3' for r in results)==1
        duplicate=command('study.rename',expected_revision='3',title='One rename effect')
        repeated=await asyncio.gather(*(storage.execute(IDENTITY,'study.rename',duplicate,study,None,deadline()) for _ in range(5)))
        assert all(result==repeated[0] for result in repeated) and repeated[0]['revision']=='4'
    run(race())
    assert run(storage.read(IDENTITY,study,note['note_id'],deadline()))['value']==value('Independent note')


def test_native_rename_lost_commit_and_overflow(native,monkeypatch):
    storage,admin_url,*_=native
    study=create(storage,'Lost rename')['study_id']
    payload=command('study.rename',expected_revision='1',title='Recovered rename')
    original=psycopg.AsyncConnection.commit
    async def lost(connection):
        await original(connection)
        raise psycopg.OperationalError('synthetic lost commit reply')
    with monkeypatch.context() as patch:
        patch.setattr(psycopg.AsyncConnection,'commit',lost)
        with pytest.raises(NotesError,match='operation_unresolved'):run(storage.execute(IDENTITY,'study.rename',payload,study,None,deadline()))
    ack=run(storage.lookup(IDENTITY,payload.operation_id,'study.rename',deadline()))['outcome']
    assert ack['revision']=='2' and run(storage.execute(IDENTITY,'study.rename',payload,study,None,deadline()))==ack
    with psycopg.connect(admin_url) as c:c.execute('UPDATE scribeswell_studies.studies SET revision=9223372036854775807 WHERE id=%s',(study,))
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute(IDENTITY,'study.rename',command('study.rename',expected_revision='9223372036854775807',title='overflow'),study,None,deadline()))


def test_unknown_alembic_history_refuses_without_reversing_acknowledged_data(native):
    storage,admin_url,_,_=native
    from alembic import command as alembic
    from alembic.config import Config
    study=create(storage,'Retained before unknown history')['study_id']
    # A deliberately corrupt disposable ledger is never interpreted/repaired by app code.
    with psycopg.connect(admin_url) as c:c.execute("UPDATE scribeswell_studies.alembic_version SET version_num='unknown_fixture_revision'")
    with pytest.raises(Exception,match='scribeswell_studies_migration_failed'):
        alembic.upgrade(Config(str(APP/'studies-alembic.ini')),'head')
    assert run(storage.read(IDENTITY,study,None,deadline()))['title']=='Retained before unknown history'
    with psycopg.connect(admin_url) as c:assert c.execute('SELECT version_num FROM scribeswell_studies.alembic_version').fetchone()[0]=='unknown_fixture_revision'

# Prepared for the deferred final native integration phase; collection-only proof below.
def passage_items(*texts):
    from passage_references import parse_reference
    return [{'id':str(uuid4()),'reference':parse_reference(text)} for text in texts]

def replace_passages(storage,study,items,revision='1',payload=None,identity=IDENTITY):
    return run(storage.execute(identity,'study.passages.replace',payload or command('study.passages.replace',expected_revision=revision,items=items),study,None,deadline()))

def test_native_collected_passages_noop_replay_independent_attribution_and_identity(native):
    storage,admin_url,_,_=native
    study=create(storage,'Collection title')['study_id']
    note=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value('must survive collection')),study,None,deadline()))
    before_study=run(storage.read(IDENTITY,study,None,deadline()));before_note=run(storage.read(IDENTITY,study,note['note_id'],deadline()))
    assert run(storage.passages(IDENTITY,study,deadline()))=={'study_id':study,'revision':'1','items':[]}
    empty=replace_passages(storage,study,[]);assert empty['revision']=='1'
    with psycopg.connect(admin_url) as c:assert c.execute('SELECT count(*) FROM scribeswell_studies.passage_lists WHERE study_id=%s',(study,)).fetchone()[0]==0
    items=passage_items('Gen1','Ps110:1','Ps110:1–3','Gen1:31–2:3','Matt26:63–64')
    payload=command('study.passages.replace',expected_revision='1',items=items)
    ack=replace_passages(storage,study,items,payload=payload);assert ack['revision']=='2'
    assert run(storage.passages(IDENTITY,study,deadline()))=={'study_id':study,'revision':'2','items':items}
    with psycopg.connect(admin_url) as c:
        header=c.execute('SELECT * FROM scribeswell_studies.passage_lists WHERE study_id=%s',(study,)).fetchone()
        rows=c.execute('SELECT * FROM scribeswell_studies.passage_entries WHERE study_id=%s ORDER BY position',(study,)).fetchall()
    assert replace_passages(storage,study,items,revision='2')['revision']=='2'
    with psycopg.connect(admin_url) as c:
        assert c.execute('SELECT * FROM scribeswell_studies.passage_lists WHERE study_id=%s',(study,)).fetchone()==header
        assert c.execute('SELECT * FROM scribeswell_studies.passage_entries WHERE study_id=%s ORDER BY position',(study,)).fetchall()==rows
    assert replace_passages(storage,study,items,payload=payload)==ack
    assert run(storage.lookup(IDENTITY,payload.operation_id,'study.passages.replace',deadline()))=={'status':'committed','outcome':ack}
    with pytest.raises(NotesError,match='passage_revision_conflict'):replace_passages(storage,study,items[1:])
    altered=payload.model_copy(update={'expected_revision':'2'})
    with pytest.raises(NotesError,match='operation_payload_mismatch'):replace_passages(storage,study,items,payload=altered)
    forged=[{**items[0],'reference':items[1]['reference']}]
    with pytest.raises(NotesError,match='input_invalid'):replace_passages(storage,study,forged,revision='2')
    rebound=[{**items[0],'id':str(uuid4())},*items[1:]]
    with pytest.raises(NotesError,match='input_invalid'):replace_passages(storage,study,rebound,revision='2')
    removed=replace_passages(storage,study,items[1:],revision='2');assert removed['revision']=='3'
    assert replace_passages(storage,study,items,payload=payload)==ack
    assert run(storage.passages(IDENTITY,study,deadline()))['items']==items[1:] # replay cannot resurrect
    assert run(storage.read(IDENTITY,study,None,deadline()))==before_study
    assert run(storage.read(IDENTITY,study,note['note_id'],deadline()))==before_note
    other={'account_id':B,'actor_id':ACTOR}
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.passages(other,study,deadline()))
    with pytest.raises(NotesError,match='resource_unavailable'):replace_passages(storage,study,[],identity=other)
    assert run(storage.lookup(other,payload.operation_id,'study.passages.replace',deadline()))=={'status':'unresolved'}
    close_study(storage,study)
    with pytest.raises(NotesError,match='resource_unavailable'):replace_passages(storage,study,items,payload=payload)
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.lookup(IDENTITY,payload.operation_id,'study.passages.replace',deadline()))

def test_native_collected_passages_concurrency_permissions_and_overflow(native):
    storage,admin_url,runtime,_=native;study=create(storage,'Collection race')['study_id']
    payload=command('study.passages.replace',expected_revision='1',items=passage_items('Gen1'))
    async def same():
        outcomes=await asyncio.gather(*(storage.execute(IDENTITY,'study.passages.replace',payload,study,None,deadline()) for _ in range(3)))
        assert all(ack==outcomes[0] for ack in outcomes)
        race=await asyncio.gather(*(storage.execute(IDENTITY,'study.passages.replace',command('study.passages.replace',expected_revision='2',items=passage_items(text)),study,None,deadline()) for text in ('Ps110','Gen2')),return_exceptions=True)
        assert sum(isinstance(result,NotesError) and result.code=='passage_revision_conflict' for result in race)==1
        assert sum(isinstance(result,dict) and result['revision']=='3' for result in race)==1
    run(same())
    with psycopg.connect(runtime) as c:
        assert c.execute('SELECT count(*) FROM scribeswell_studies.passage_lists').fetchone()[0]==0
        assert c.execute('SELECT count(*) FROM scribeswell_studies.passage_entries').fetchone()[0]==0
    for statement in ('UPDATE scribeswell_studies.passage_entries SET book_id=book_id','UPDATE scribeswell_studies.passage_lists SET created_by=created_by'):
        with psycopg.connect(runtime) as c:
            c.execute("SELECT set_config('app.account_id',%s,true)",(A,))
            with pytest.raises(psycopg.errors.InsufficientPrivilege):c.execute(statement)
    for role in ('anon','authenticated','service_role','scribeswell_runtime'):
        url=make_url(runtime).set(username=role,password='synthetic-only').render_as_string(hide_password=False)
        for table in ('passage_lists','passage_entries'):
            with psycopg.connect(url) as c:
                with pytest.raises(psycopg.errors.InsufficientPrivilege):c.execute('SELECT * FROM scribeswell_studies.'+table)
    with psycopg.connect(runtime) as c:
        c.execute("SELECT set_config('app.account_id',%s,true)",(B,))
        assert c.execute('DELETE FROM scribeswell_studies.passage_entries WHERE study_id=%s RETURNING id',(study,)).fetchall()==[]
        assert c.execute('DELETE FROM scribeswell_studies.passage_lists WHERE study_id=%s RETURNING study_id',(study,)).fetchall()==[]
    with psycopg.connect(admin_url) as c:c.execute('UPDATE scribeswell_studies.passage_lists SET revision=9223372036854775807 WHERE study_id=%s',(study,))
    with pytest.raises(NotesError,match='resource_unavailable'):replace_passages(storage,study,[],revision='9223372036854775807')
    assert run(storage.passages(IDENTITY,study,deadline()))['revision']=='9223372036854775807'

def test_native_collected_passages_structural_constraints(native):
    storage,_,runtime,_=native;study=create(storage,'Collection constraint')['study_id']
    replace_passages(storage,study,passage_items('Gen1'))
    sql_insert='INSERT INTO scribeswell_studies.passage_entries(account_id,study_id,id,position,catalogue_id,catalogue_version,versification_id,book_id,kind,start_chapter,start_verse,end_chapter,end_verse,created_by) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    from passage_references import CATALOGUE_VERSION
    base=[A,study,str(uuid4()),2,'scribeswell.references.v1',CATALOGUE_VERSION,'oshb-hebrew-json-c2d8e9e5','Gen','verse_range',1,1,1,2,ACTOR]
    for changes in ({3:0},{9:0},{10:0},{12:0},{11:None},{9:2,11:1},{8:'chapter'},{0:B}):
        values=base[:]
        for key,val in changes.items():values[key]=val
        with psycopg.connect(runtime) as c:
            c.execute("SELECT set_config('app.account_id',%s,true)",(A,))
            with pytest.raises((psycopg.errors.CheckViolation,psycopg.errors.InsufficientPrivilege)):c.execute(sql_insert,values)
    # Same canonical chapter under another ID is rejected by the database, not just the DTO.
    duplicate=base[:];duplicate[8:13]=['chapter',1,None,None,None]
    with psycopg.connect(runtime) as c:
        c.execute("SELECT set_config('app.account_id',%s,true)",(A,))
        with pytest.raises(psycopg.errors.UniqueViolation):c.execute(sql_insert,duplicate)

def test_native_maximum_collection_replace_reorder_with_competing_note_and_title_deadlines(native):
    """Prepared only: measure actual200-row writes before considering optimization."""
    storage,*_=native
    from passage_references import parse_reference,BOOKS
    study=create(storage,'Maximum collection deadline')['study_id']
    note=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value('before maximum list')),study,None,deadline()))
    references=[parse_reference(f'Gen 1:1–{chapter}:{verse}') for chapter,count in enumerate(BOOKS['Gen']['chapter_verse_counts'],1) for verse in range(1,count+1)][:200]
    items=[{'id':str(uuid4()),'reference':reference} for reference in references]
    async def stage(expected_revision,ordered,label,title_revision,note_revision):
        async def bounded(kind,payload,note_id=None):
            started=time.monotonic();end=started+5
            outcome=await storage.execute(IDENTITY,kind,payload,study,note_id,end)
            assert time.monotonic()<end,'Native maximum collection/competing operation exceeded real5s deadline'
            return outcome
        results=await asyncio.gather(
            bounded('study.passages.replace',command('study.passages.replace',expected_revision=expected_revision,items=ordered)),
            bounded('study.rename',command('study.rename',expected_revision=title_revision,title=label)),
            bounded('note.replace',command('note.replace',expected_revision=note_revision,value=value(label)),note['note_id']))
        current=await storage.passages(IDENTITY,study,deadline())
        assert current['items']==ordered and current['revision']==str(int(expected_revision)+1)
        assert (await storage.read(IDENTITY,study,None,deadline()))['title']==label
        assert (await storage.read(IDENTITY,study,note['note_id'],deadline()))['value']==value(label)
        return results
    first=run(stage('1',items,'Maximum collection installed','1','1'))
    assert first[0]['revision']=='2'
    reordered=run(stage('2',list(reversed(items)),'Maximum collection reordered','2','2'))
    assert reordered[0]['revision']=='3'

def test_native_note_format2_fence_original_v1_receipt_and_actual_baseline(native):
    """Prepared only until final integration; actual restricted-login/SQL proof."""
    from passage_references import parse_reference
    sys.path.insert(0,str(Path(__file__).with_name('fixtures')))
    from note_links_baseline_loader import load
    baseline,previous=load()
    storage,admin_url,runtime,*_=native
    old=previous.PersonalNotesStorage(runtime)
    study=create(storage,'Format compatibility')['study_id']
    original=baseline.parse_command('note.create',json.dumps({'operation_id':str(uuid4()),'value':value('ordinary baseline')}).encode())
    ack=run(old.execute(IDENTITY,'note.create',original,study,None,deadline()));note=ack['note_id']
    ordinary=run(old.read(IDENTITY,study,note,deadline()))
    assert ordinary==run(storage.read(IDENTITY,study,note,deadline()))
    # An actual baseline writer commits its own no-op replacement at revision1.
    original_replace=baseline.parse_command('note.replace',json.dumps({'operation_id':str(uuid4()),'expected_revision':'1','value':ordinary['value']}).encode())
    replacement_ack=run(old.execute(IDENTITY,'note.replace',original_replace,study,note,deadline()))
    assert replacement_ack['revision']=='1' and run(old.read(IDENTITY,study,note,deadline()))==ordinary
    v=value('explanation ');v['document']['version']=2
    v['document']['blocks'][0]['content'].append({'type':'passage_link','reference':parse_reference('Gen 1:31–2:3'),'label':'Genesis 1:31–2:3'})
    updated=run(storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision='1',value=v),study,note,deadline()))
    rich=run(storage.read(IDENTITY,study,note,deadline()))
    noop=run(storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision=rich['revision'],value=v),study,note,deadline()))
    assert noop['revision']==rich['revision'] and run(storage.read(IDENTITY,study,note,deadline()))==rich
    with pytest.raises(NotesError,match='studies_storage_unavailable'):run(old.read(IDENTITY,study,note,deadline()))
    # Both actual old/current receipt paths acknowledge the original v1 replacement
    # at revision1, despite current richer revision2, without replacing that row.
    with psycopg.connect(admin_url) as connection:
        rich_row=connection.execute('SELECT * FROM scribeswell_studies.notes WHERE id=%s',(note,)).fetchone()
        rich_receipts=connection.execute('SELECT count(*) FROM scribeswell_studies.receipts').fetchone()[0]
    assert run(storage.execute(IDENTITY,'note.replace',parse_command('note.replace',original_replace.model_dump_json().encode()),study,note,deadline()))==replacement_ack
    assert run(old.execute(IDENTITY,'note.replace',original_replace,study,note,deadline()))==replacement_ack
    assert run(storage.read(IDENTITY,study,note,deadline()))==rich
    with psycopg.connect(admin_url) as connection:
        assert connection.execute('SELECT * FROM scribeswell_studies.notes WHERE id=%s',(note,)).fetchone()==rich_row
        assert connection.execute('SELECT count(*) FROM scribeswell_studies.receipts').fetchone()[0]==rich_receipts
    downgrade=command('note.replace',expected_revision=updated['revision'],value=value('legacy overwrite'))
    with psycopg.connect(admin_url) as connection:
        before=connection.execute('SELECT * FROM scribeswell_studies.notes WHERE id=%s',(note,)).fetchone()
        receipt_count=connection.execute('SELECT count(*) FROM scribeswell_studies.receipts').fetchone()[0]
    with pytest.raises(NotesError,match='note_format_unsupported'):run(storage.execute(IDENTITY,'note.replace',downgrade,study,note,deadline()))
    with psycopg.connect(admin_url) as connection:
        assert connection.execute('SELECT * FROM scribeswell_studies.notes WHERE id=%s',(note,)).fetchone()==before
        assert connection.execute('SELECT count(*) FROM scribeswell_studies.receipts').fetchone()[0]==receipt_count
    assert run(storage.read(IDENTITY,study,note,deadline()))==rich

    without_link=value('kept format2');without_link['document']['version']=2
    removed=run(storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision=rich['revision'],value=without_link),study,note,deadline()))
    assert run(storage.read(IDENTITY,study,note,deadline()))['value']==without_link
    with pytest.raises(NotesError,match='note_format_unsupported'):
        run(storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision=removed['revision'],value=value()),study,note,deadline()))

def test_native_library_search_filtered_matching_pagination_isolation_and_zero_mutation(native):
    """PREPARED ONLY: actual restricted PostgreSQL17 matching, not a mocked SQL claim."""
    from psycopg.types.json import Jsonb
    from passage_references import parse_reference
    storage,admin_url,*_=native
    marker='Library native only '+uuid4().hex
    target=create(storage,marker+' café 100%_\\')['study_id']
    content=value();content['document']['version']=2
    content['document']['blocks']=[{'type':'paragraph','direction':'auto','content':[
        {'type':'text','text':marker+' for','marks':['bold']},
        {'type':'external_link','url':'https://url-target-only.invalid/hidden-needle','content':[{'type':'text','text':'matted','marks':[]}]},
        {'type':'text','text':' שָׁלוֹם','marks':[]},
        {'type':'passage_link','reference':parse_reference('Gen 1:31–2:3'),'label':'Stored custom label'}]},
        {'type':'list','style':'bullet','items':[[{'type':'paragraph','direction':'rtl','content':[{'type':'text','text':'List paragraph','marks':[]}]}]]}]
    for _ in range(2):run(storage.execute(IDENTITY,'note.create',command('note.create',value=content),target,None,deadline()))
    run(storage.execute(IDENTITY,'study.passages.replace',command('study.passages.replace',expected_revision='1',items=[{'id':str(uuid4()),'reference':parse_reference('Matt 26:63–64')},{'id':str(uuid4()),'reference':parse_reference('Gen 2')}]),target,None,deadline()))
    # More than the old default page hides target from an unfiltered first-page scan.
    for i in range(22):create(storage,marker+' filler '+str(i))
    assert target not in [s['id'] for s in run(storage.list(IDENTITY,None,20,None,deadline()))['items']]
    other={'account_id':B,'actor_id':ACTOR}
    foreign=run(storage.execute(other,'study.create',command('study.create',title=marker+' foreign'),None,None,deadline()))['study_id']
    run(storage.execute(other,'note.create',command('note.create',value=content),foreign,None,deadline()))
    closed=create(storage,marker+' closed')['study_id']
    inactive=create(storage,'Inactive note parent')['study_id']
    inactive_note=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value(marker+' inactive-note-only')),inactive,None,deadline()))['note_id']
    equal_ids=[str(uuid4()) for _ in range(3)]
    malformed=create(storage,'Malformed JSON parent')['study_id']
    with psycopg.connect(admin_url) as c:
        c.execute("UPDATE scribeswell_studies.studies SET active=false,title='Deleted study' WHERE id=%s",(closed,))
        c.execute('UPDATE scribeswell_studies.notes SET active=false,value=%s WHERE id=%s',(psycopg.types.json.Jsonb({'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}),inactive_note))
        for identifier in equal_ids:
            c.execute("INSERT INTO scribeswell_studies.studies(account_id,id,title,created_at,updated_at,created_by,updated_by) VALUES(%s,%s,%s,'2026-10-25T00:00:00Z','2026-10-25T00:00:00Z',%s,%s)",(A,identifier,marker+' equal',ACTOR,ACTOR))
        # Stored unknown array/object/numeric shapes must never cause a cast/traversal failure.
        for blocks in ({'arbitrary':marker},[{'type':'paragraph','direction':'auto','content':{'text':marker}}],[{'type':'paragraph','direction':'auto','content':[{'type':'passage_link','label':'malformed label','reference':{'target':{'kind':'chapter','chapter':{}}}}]}]):
            malformed_value={'document':{'version':2,'blocks':blocks},'connections':[],'highlights':[]}
            c.execute('INSERT INTO scribeswell_studies.notes(account_id,study_id,id,value,created_by,updated_by) VALUES(%s,%s,%s,%s,%s,%s)',(A,malformed,str(uuid4()),Jsonb(malformed_value),ACTOR,ACTOR))
    def search(text,limit=20,cursor=None,identity=IDENTITY):
        payload=parse_command('studies.search',json.dumps({'query':text,'limit':limit,'cursor':cursor},ensure_ascii=False).encode())
        return run(storage.search(identity,payload,deadline()))
    def snapshot():
        with psycopg.connect(admin_url) as c:
            return {table:c.execute(sql.SQL('SELECT t.* FROM scribeswell_studies.{} t ORDER BY to_jsonb(t)::text').format(sql.Identifier(table))).fetchall() for table in ('studies','notes','receipts','passage_lists','passage_entries')}
    before=snapshot()
    for query in ('CAFÉ 100%_\\',marker+' formatted','Stored custom label','List paragraph','שָׁלוֹם','Gen 1:31','Genesis 2','בראשית ב:ב','Matthew','Matt 26:64','Gen 1:30–2:1','Gen 2:25'):
        ids=[s['id'] for s in search(query)['items']]
        assert target in ids and foreign not in ids and closed not in ids and malformed not in ids
        assert ids.count(target)==1
    for query in ('hidden-needle',marker+' inactive-note-only','Gen 999','Gen 3:1'):
        assert target not in [s['id'] for s in search(query)['items']]
    assert [s['id'] for s in search('cafe\u0301 100%_\\')['items']]==[target]
    found=[];cursor=None
    while True:
        page=search(marker,1,cursor);found.extend(s['id'] for s in page['items']);cursor=page['next_cursor']
        if cursor is None:break
    assert len(found)==len(set(found)) and target in found and foreign not in found and closed not in found
    assert [identifier for identifier in found if identifier in equal_ids]==sorted(equal_ids,reverse=True)
    # Literal labels are recognized fields; search does not certify/repair a corrupt aggregate.
    assert [s['id'] for s in search('malformed label')['items']]==[malformed]
    assert search(marker+' inactive-note-only')['items']==[]
    assert snapshot()==before,'Search mutated saved content/attribution/revisions/receipts'
    # Previous GET and its original cursor still work after search.
    old=run(storage.list(IDENTITY,None,1,None,deadline()));assert old['next_cursor']
    assert run(storage.list(IDENTITY,None,1,old['next_cursor'],deadline()))['items'][0]['id']!=old['items'][0]['id']
    assert target not in [s['id'] for s in search(marker,identity=other)['items']]

    # New reads reflect acknowledged saved replacements; no search index/backfill exists.
    note_page=run(storage.list(IDENTITY,target,50,None,deadline()))
    for note in note_page['items']:
        run(storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision=note['revision'],value={'document':{'version':2,'blocks':[]},'connections':[],'highlights':[]}),target,note['id'],deadline()))
    assert target not in [s['id'] for s in search(marker+' formatted')['items']]
    assert target in [s['id'] for s in search('Matthew')['items']]

def test_native_library_search_numeric_reference_guards_identity_and_format1(native):
    """Prepared only: otherwise-valid corrupt references exercise real numeric guards."""
    from copy import deepcopy
    from psycopg.types.json import Jsonb
    from passage_references import parse_reference
    storage,admin_url,*_=native
    marker='Unique ordinary saved body '+uuid4().hex
    ordinary=create(storage,'Ordinary note parent')['study_id']
    run(storage.execute(IDENTITY,'note.create',command('note.create',value=value(marker)),ordinary,None,deadline()))
    canonical=parse_reference('Gen 1:1–2:3');cases=[]
    malformed_numbers=[('object',{}),('array',[]),('boolean',True),('decimal',1.5),('oversized',10**100)]
    for label,number in malformed_numbers:
        reference=deepcopy(canonical);reference['target']={'kind':'chapter','chapter':number}
        cases.append(('chapter-'+label,reference,2))
        for endpoint in ('start','end'):
            for coordinate in ('chapter','verse'):
                reference=deepcopy(canonical);reference['target'][endpoint][coordinate]=number
                cases.append((endpoint+'-'+coordinate+'-'+label,reference,2))
    for start,end in (({'chapter':2,'verse':3},{'chapter':1,'verse':1}),({'chapter':2,'verse':3},{'chapter':2,'verse':2})):
        reference=deepcopy(canonical);reference['target'].update(start=start,end=end)
        cases.append(('reversed-range',reference,2))
    for field,wrong in (('catalogue_id','unsupported.catalogue'),('catalogue_version','0'*64),('versification_id','crosswire-kjv-3765')):
        reference=deepcopy(canonical);reference[field]=wrong;cases.append(('wrong-'+field,reference,2))
    cases.append(('unsupported-document',deepcopy(canonical),3))
    invalid_studies=[]
    with psycopg.connect(admin_url) as connection:
        for label,reference,version in cases:
            study=create(storage,'Guard case '+label)['study_id'];invalid_studies.append(study)
            stored={'document':{'version':version,'blocks':[{'type':'paragraph','direction':'auto','content':[{'type':'passage_link','reference':reference,'label':'Visible guard label'}]}]},'connections':[],'highlights':[]}
            connection.execute('INSERT INTO scribeswell_studies.notes(account_id,study_id,id,value,created_by,updated_by) VALUES(%s,%s,%s,%s,%s,%s)',(A,study,str(uuid4()),Jsonb(stored),ACTOR,ACTOR))
        # Normalized collection rows also reject mismatched version/versification at search.
        for field,wrong in (('catalogue_version','0'*64),('versification_id','crosswire-kjv-3765')):
            study=create(storage,'Collection identity guard')['study_id'];invalid_studies.append(study)
            reference=deepcopy(canonical);reference[field]=wrong
            connection.execute('INSERT INTO scribeswell_studies.passage_lists(account_id,study_id,revision,created_by,updated_by) VALUES(%s,%s,2,%s,%s)',(A,study,ACTOR,ACTOR))
            connection.execute("INSERT INTO scribeswell_studies.passage_entries(account_id,study_id,id,position,catalogue_id,catalogue_version,versification_id,book_id,kind,start_chapter,start_verse,end_chapter,end_verse,created_by) VALUES(%s,%s,%s,1,%s,%s,%s,'Gen','verse_range',1,1,2,3,%s)",(A,study,str(uuid4()),reference['catalogue_id'],reference['catalogue_version'],reference['versification_id'],ACTOR))
    def all_ids(query):
        found=[];cursor=None
        while True:
            payload=parse_command('studies.search',json.dumps({'query':query,'limit':50,'cursor':cursor}).encode())
            page=run(storage.search(IDENTITY,payload,deadline()));found.extend(item['id'] for item in page['items']);cursor=page['next_cursor']
            if cursor is None:return found
    assert all_ids(marker)==[ordinary],'Active format1 unique note-body text was not found'
    for query in ('Gen','Genesis 1','Gen 2:1','Gen 1:1–2:3'):
        found=all_ids(query)
        for (label,_,_),study in zip(cases,invalid_studies):
            assert study not in found,(label,query)
        assert all(study not in found for study in invalid_studies[len(cases):]),'Mismatched normalized collection identity matched'
    unsupported=invalid_studies[len(cases)-1]
    assert unsupported not in all_ids('Visible guard label'),'Unsupported document version contributed visible text'

def test_native_note_deletion_erasure_receipt_recovery_constraints_and_previous_consumer(native):
    storage,admin_url,runtime,_=native
    study=create(storage,'Delete target')['study_id'];initial=command('note.create',value=value('erase private body'))
    created=run(storage.execute(IDENTITY,'note.create',initial,study,None,deadline()));note=created['note_id']
    other=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value('keep other body')),study,None,deadline()))
    before=run(storage.read(IDENTITY,study,other['note_id'],deadline()))
    payload=command('note.delete',expected_revision='1');ack=run(storage.execute(IDENTITY,'note.delete',payload,study,note,deadline()))
    assert ack['revision']=='2' and ack['note_id']==note
    assert run(storage.execute(IDENTITY,'note.delete',payload,study,note,deadline()))==ack
    assert run(storage.lookup(IDENTITY,payload.operation_id,'note.delete',deadline()))['outcome']==ack
    assert run(storage.read(IDENTITY,study,other['note_id'],deadline()))==before
    with psycopg.connect(admin_url) as c:
        row=c.execute('SELECT active,value,revision,updated_by,updated_at>=created_at FROM scribeswell_studies.notes WHERE id=%s',(note,)).fetchone()
        assert row[:3]==(False,{'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]},2) and str(row[3])==ACTOR and row[4]
    with psycopg.connect(runtime) as c:
        c.execute("SELECT set_config('app.account_id',%s,true)",(A,))
        for statement,args in [('UPDATE scribeswell_studies.notes SET value=%s WHERE id=%s',(psycopg.types.json.Jsonb(value('refill forbidden')),note)),('UPDATE scribeswell_studies.notes SET active=true WHERE id=%s',(note,))]:
            with pytest.raises(psycopg.errors.CheckViolation),c.transaction():c.execute(statement,args)
    for kind,payload2 in [('note.create',initial),('note.delete',command('note.delete',expected_revision='2')),('note.replace',command('note.replace',expected_revision='2',value=value()))]:
        with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute(IDENTITY,kind,payload2,study,None if kind=='note.create' else note,deadline()))
    with pytest.raises(NotesError,match='operation_payload_mismatch'):run(storage.execute(IDENTITY,'note.delete',parse_command('note.delete',json.dumps({'operation_id':payload.operation_id,'expected_revision':'2'}).encode()),study,note,deadline()))
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute({'account_id':B,'actor_id':ACTOR},'note.delete',command('note.delete',expected_revision='2'),study,note,deadline()))
    sys.path.insert(0,str(APP/'tests/fixtures'));from note_deletion_baseline_loader import load
    _,previous=load();old=previous.PersonalNotesStorage(runtime)
    assert run(old.list(IDENTITY,study,50,None,deadline()))['items']==[before]
    with pytest.raises(NotesError,match='resource_unavailable'):run(old.read(IDENTITY,study,note,deadline()))
    close_study(storage,study)
    assert run(storage.lookup(IDENTITY,payload.operation_id,'note.delete',deadline()))['outcome']==ack
    assert run(storage.execute(IDENTITY,'note.delete',payload,study,note,deadline()))==ack
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.lookup(IDENTITY,initial.operation_id,'note.create',deadline()))

def test_native_note_deletion_race_rollback_overflow_and_lost_commit(native,monkeypatch):
    storage,admin_url,_,_=native;study=create(storage,'Deletion atomicity')['study_id']
    created=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value('retain on rollback')),study,None,deadline()));note=created['note_id']
    before=run(storage.read(IDENTITY,study,note,deadline()))
    original=psycopg.AsyncCursor.execute
    async def fail_receipt(self,query,params=None,**kwargs):
        if str(query).startswith('INSERT INTO scribeswell_studies.receipts'):raise psycopg.errors.CheckViolation('fixture receipt failure')
        return await original(self,query,params,**kwargs)
    deletion=command('note.delete',expected_revision='1')
    with monkeypatch.context() as patch:
        patch.setattr(psycopg.AsyncCursor,'execute',fail_receipt)
        with pytest.raises(NotesError):run(storage.execute(IDENTITY,'note.delete',deletion,study,note,deadline()))
    assert run(storage.read(IDENTITY,study,note,deadline()))==before
    assert run(storage.lookup(IDENTITY,deletion.operation_id,'note.delete',deadline()))=={'status':'unresolved'}
    saving=command('note.replace',expected_revision='1',value=value('concurrent save'))
    async def race():
        return await asyncio.gather(storage.execute(IDENTITY,'note.delete',deletion,study,note,deadline()),storage.execute(IDENTITY,'note.replace',saving,study,note,deadline()),return_exceptions=True)
    results=run(race());assert sum(isinstance(item,dict) for item in results)==1
    assert sum(isinstance(item,NotesError) and item.code in ('resource_unavailable','note_revision_conflict') for item in results)==1
    delete_won=isinstance(results[0],dict);winner=results[0] if delete_won else results[1]
    with psycopg.connect(admin_url) as c:
        assert c.execute('SELECT active,value,revision FROM scribeswell_studies.notes WHERE id=%s',(note,)).fetchone()==(not delete_won,{'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]} if delete_won else value('concurrent save'),2)
        receipts=c.execute('SELECT operation_id,command,outcome FROM scribeswell_studies.receipts WHERE account_id=%s AND operation_id IN(%s,%s)',(A,deletion.operation_id,saving.operation_id)).fetchall()
        assert len(receipts)==1 and str(receipts[0][0])==winner['operation_id']
        assert receipts[0][1]==('note.delete' if delete_won else 'note.replace') and receipts[0][2]==winner
    overflow=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value('overflow must retain')),study,None,deadline()))['note_id']
    with psycopg.connect(admin_url) as c:c.execute('UPDATE scribeswell_studies.notes SET revision=9223372036854775807 WHERE id=%s',(overflow,))
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute(IDENTITY,'note.delete',command('note.delete',expected_revision='9223372036854775807'),study,overflow,deadline()))
    assert run(storage.read(IDENTITY,study,overflow,deadline()))['value']==value('overflow must retain')
    lost=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value('lost delete reply')),study,None,deadline()))['note_id']
    payload=command('note.delete',expected_revision='1');commit=psycopg.AsyncConnection.commit
    async def lose_commit(self):await commit(self);raise psycopg.OperationalError('fixture lost reply')
    with monkeypatch.context() as patch:
        patch.setattr(psycopg.AsyncConnection,'commit',lose_commit)
        with pytest.raises(NotesError,match='operation_unresolved'):run(storage.execute(IDENTITY,'note.delete',payload,study,lost,deadline()))
    outcome=run(storage.lookup(IDENTITY,payload.operation_id,'note.delete',deadline()))
    assert outcome['status']=='committed' and outcome['outcome']['revision']=='2'
    assert run(storage.execute(IDENTITY,'note.delete',payload,study,lost,deadline()))==outcome['outcome']

def test_native_byte_frozen_old_save_races_new_deletion_without_resurrection_or_failed_receipts(native):
    """Prepared only: the actual previous checkpoint writer competes under real locks."""
    storage,admin_url,runtime,_=native
    sys.path.insert(0,str(APP/'tests/fixtures'));from note_deletion_baseline_loader import load
    old_contract,previous=load();old=previous.PersonalNotesStorage(runtime)
    study=create(storage,'Previous writer deletion race')['study_id']
    note=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value('before old writer race')),study,None,deadline()))['note_id']
    deletion=command('note.delete',expected_revision='1')
    saving=old_contract.parse_command('note.replace',json.dumps({'operation_id':str(uuid4()),'expected_revision':'1','value':value('actual old writer won')}).encode())
    async def race():
        return await asyncio.gather(storage.execute(IDENTITY,'note.delete',deletion,study,note,deadline()),old.execute(IDENTITY,'note.replace',saving,study,note,deadline()),return_exceptions=True)
    results=run(race());delete_won=isinstance(results[0],dict);winner=results[0] if delete_won else results[1]
    assert isinstance(winner,dict) and winner['revision']=='2'
    loser=results[1] if delete_won else results[0]
    assert isinstance(loser,NotesError) and loser.code in ('resource_unavailable','note_revision_conflict')
    empty={'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}
    with psycopg.connect(admin_url) as c:
        assert c.execute('SELECT active,value,revision FROM scribeswell_studies.notes WHERE id=%s',(note,)).fetchone()==(not delete_won,empty if delete_won else value('actual old writer won'),2)
        receipts=c.execute('SELECT operation_id,command,outcome FROM scribeswell_studies.receipts WHERE account_id=%s AND operation_id IN(%s,%s)',(A,deletion.operation_id,saving.operation_id)).fetchall()
        assert len(receipts)==1 and str(receipts[0][0])==winner['operation_id']
        assert receipts[0][1]==('note.delete' if delete_won else 'note.replace') and receipts[0][2]==winner
    if not delete_won:
        # Either race order ends with a closed row; an old writer can never refill it.
        run(storage.execute(IDENTITY,'note.delete',command('note.delete',expected_revision='2'),study,note,deadline()))
    late=old_contract.parse_command('note.replace',json.dumps({'operation_id':str(uuid4()),'expected_revision':'2','value':value('late old writer must not restore')}).encode())
    with pytest.raises(NotesError,match='resource_unavailable'):run(old.execute(IDENTITY,'note.replace',late,study,note,deadline()))
    with psycopg.connect(admin_url) as c:
        assert c.execute('SELECT active,value,revision FROM scribeswell_studies.notes WHERE id=%s',(note,)).fetchone()==(False,empty,2 if delete_won else 3)
        assert c.execute('SELECT count(*) FROM scribeswell_studies.receipts WHERE account_id=%s AND operation_id=%s',(A,late.operation_id)).fetchone()[0]==0
        failed=saving.operation_id if delete_won else deletion.operation_id
        assert c.execute('SELECT count(*) FROM scribeswell_studies.receipts WHERE account_id=%s AND operation_id=%s',(A,failed)).fetchone()[0]==0


def test_native_study_deletion_atomic_erasure_original_receipts_and_previous_f6_consumer(native):
    storage,admin_url,runtime,_=native
    study=create(storage,'Private study title to erase')['study_id']
    independent=create(storage,'Independent copy')['study_id']
    original=command('note.create',value=value('Private body to erase'))
    note=run(storage.execute(IDENTITY,'note.create',original,study,None,deadline()))
    old_deleted=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value('Already erased')),study,None,deadline()))
    child_delete=command('note.delete',expected_revision='1')
    child_ack=run(storage.execute(IDENTITY,'note.delete',child_delete,study,old_deleted['note_id'],deadline()))
    retained=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value('Independent copy body')),independent,None,deadline()))
    copy_before=run(storage.read(IDENTITY,independent,retained['note_id'],deadline()))
    replace_passages(storage,study,passage_items('Gen1'))
    with psycopg.connect(admin_url) as c:
        old_tombstone=c.execute('SELECT * FROM scribeswell_studies.notes WHERE id=%s',(old_deleted['note_id'],)).fetchone()
    payload=command('study.delete',expected_revision='1');ack=run(storage.execute(IDENTITY,'study.delete',payload,study,None,deadline()))
    assert ack['note_id'] is None and ack['revision']=='2'
    with psycopg.connect(runtime,row_factory=psycopg.rows.dict_row) as c:
        c.execute("SELECT set_config('app.account_id',%s,true)",(A,))
        parent=c.execute('SELECT * FROM scribeswell_studies.studies WHERE id=%s',(study,)).fetchone()
        erased=c.execute('SELECT * FROM scribeswell_studies.notes WHERE id=%s',(note['note_id'],)).fetchone()
        assert parent['title']=='Deleted study' and not parent['active'] and parent['revision']==2 and parent['updated_by']==ACTOR
        assert not erased['active'] and erased['revision']==2 and erased['updated_by']==ACTOR
        assert erased['value']=={'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}
        for table in ('passage_lists','passage_entries'):assert c.execute(f'SELECT count(*) FROM scribeswell_studies.{table} WHERE study_id=%s',(study,)).fetchone()['count']==0
        receipt=c.execute("SELECT outcome FROM scribeswell_studies.receipts WHERE command='study.delete' AND operation_id=%s",(payload.operation_id,)).fetchone()['outcome']
        assert receipt==ack and set(receipt)=={'operation_id','command','study_id','note_id','revision'}
    with psycopg.connect(admin_url) as c:assert c.execute('SELECT * FROM scribeswell_studies.notes WHERE id=%s',(old_deleted['note_id'],)).fetchone()==old_tombstone
    assert run(storage.read(IDENTITY,independent,retained['note_id'],deadline()))==copy_before
    assert run(storage.execute(IDENTITY,'study.delete',payload,study,None,deadline()))==ack
    assert run(storage.lookup(IDENTITY,payload.operation_id,'study.delete',deadline()))['outcome']==ack
    assert run(storage.execute(IDENTITY,'note.delete',child_delete,study,old_deleted['note_id'],deadline()))==child_ack
    assert run(storage.lookup(IDENTITY,child_delete.operation_id,'note.delete',deadline()))['outcome']==child_ack
    with pytest.raises(NotesError,match='operation_payload_mismatch'):run(storage.execute(IDENTITY,'study.delete',payload.model_copy(update={'expected_revision':'2'}),study,None,deadline()))
    for kind,args in [('study.delete',command('study.delete',expected_revision='2')),('note.create',original)]:
        with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute(IDENTITY,kind,args,study,None,deadline()))
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.lookup(IDENTITY,original.operation_id,'note.create',deadline()))
    sys.path.insert(0,str(APP/'tests/fixtures'));from study_deletion_baseline_loader import load
    contract,previous=load();old=previous.PersonalNotesStorage(runtime)
    assert all(row['id']!=study for row in run(old.list(IDENTITY,None,50,None,deadline()))['items'])
    with pytest.raises(NotesError,match='resource_unavailable'):run(old.read(IDENTITY,study,None,deadline()))
    for kind,fields,note_id in [('note.create',{'value':value('old writer cannot refill')},None),('note.replace',{'expected_revision':'2','value':value('old writer cannot refill')},note['note_id'])]:
        old_command=contract.parse_command(kind,json.dumps({'operation_id':str(uuid4()),**fields}).encode())
        with pytest.raises(NotesError,match='resource_unavailable'):run(old.execute(IDENTITY,kind,old_command,study,note_id,deadline()))
    # Actual previous f6 consumer still writes its unaffected owned resource.
    old_payload=contract.parse_command('note.replace',json.dumps({'operation_id':str(uuid4()),'expected_revision':copy_before['revision'],'value':copy_before['value']}).encode())
    run(old.execute(IDENTITY,'note.replace',old_payload,independent,retained['note_id'],deadline()))


def test_native_study_deletion_overflow_rollback_alternate_writes_and_race(native,monkeypatch):
    storage,admin_url,runtime,_=native
    study=create(storage,'Overflow must preserve title')['study_id']
    note=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value('Overflow protected')),study,None,deadline()))
    payload=command('study.delete',expected_revision='1')
    with psycopg.connect(admin_url) as c:c.execute('UPDATE scribeswell_studies.notes SET revision=9223372036854775807 WHERE id=%s',(note['note_id'],))
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute(IDENTITY,'study.delete',payload,study,None,deadline()))
    assert run(storage.read(IDENTITY,study,None,deadline()))['title']=='Overflow must preserve title'
    with psycopg.connect(admin_url) as c:
        assert not c.execute('SELECT 1 FROM scribeswell_studies.receipts WHERE operation_id=%s',(payload.operation_id,)).fetchone()
        c.execute('UPDATE scribeswell_studies.notes SET revision=1 WHERE id=%s',(note['note_id'],))
    # Fail exactly at receipt insertion: transaction must undo every cleanup write.
    original=psycopg.AsyncCursor.execute
    async def fail_receipt(cursor,query,params=None,*args,**kwargs):
        if str(query).startswith('INSERT INTO scribeswell_studies.receipts'):raise RuntimeError('fixture receipt failure')
        return await original(cursor,query,params,*args,**kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(psycopg.AsyncCursor,'execute',fail_receipt)
        with pytest.raises(NotesError,match='studies_storage_unavailable'):run(storage.execute(IDENTITY,'study.delete',payload,study,None,deadline()))
    assert run(storage.read(IDENTITY,study,note['note_id'],deadline()))['value']==value('Overflow protected')
    # This test's alternate-write scope is closed by an acknowledged command.
    deletion=run(storage.execute(IDENTITY,'study.delete',payload,study,None,deadline()))
    assert run(storage.lookup(IDENTITY,payload.operation_id,'study.delete',deadline()))['outcome']==deletion
    with psycopg.connect(runtime) as c:
        c.execute("SELECT set_config('app.account_id',%s,true)",(A,))
        for statement,args in [
          ('INSERT INTO scribeswell_studies.notes(id,account_id,study_id,value,created_by,updated_by) VALUES(%s,%s,%s,%s,%s,%s)',(str(uuid4()),A,study,psycopg.types.json.Jsonb(value()),ACTOR,ACTOR)),
          ('INSERT INTO scribeswell_studies.passage_lists(account_id,study_id,revision,created_by,updated_by) VALUES(%s,%s,2,%s,%s)',(A,study,ACTOR,ACTOR)),
          ("INSERT INTO scribeswell_studies.passage_entries(account_id,study_id,id,position,catalogue_id,catalogue_version,versification_id,book_id,kind,start_chapter,created_by) VALUES(%s,%s,%s,1,'scribeswell.references.v1',%s,'oshb-hebrew-json-c2d8e9e5','Gen','chapter',1,%s)",(A,study,str(uuid4()),'0'*64,ACTOR)),
          ("UPDATE scribeswell_studies.studies SET title='Refill' WHERE id=%s",(study,)),
          ('UPDATE scribeswell_studies.studies SET active=true WHERE id=%s',(study,))]:
            with pytest.raises(psycopg.errors.CheckViolation),c.transaction():c.execute(statement,args)
    # Closing a still-populated active parent through the restricted alternate path refuses.
    other=create(storage,'Guarded active parent')['study_id']
    run(storage.execute(IDENTITY,'note.create',command('note.create',value=value()),other,None,deadline()))
    with psycopg.connect(runtime) as c:
        c.execute("SELECT set_config('app.account_id',%s,true)",(A,))
        with pytest.raises(psycopg.errors.CheckViolation),c.transaction():c.execute("UPDATE scribeswell_studies.studies SET active=false,title='Deleted study' WHERE id=%s",(other,))


async def ordered_parent_commands(first_storage,first_args,second_storage,second_args):
    """Hold the first actual parent lock until the competing writer has entered."""
    acquired=asyncio.Event();release=asyncio.Event();contending=asyncio.Event()
    class First(type(first_storage)):
        async def _parent(self,*args,**kwargs):
            row=await super()._parent(*args,**kwargs)
            if kwargs.get('lock'):acquired.set();await asyncio.wait_for(release.wait(),1)
            return row
    class Second(type(second_storage)):
        async def _parent(self,*args,**kwargs):
            if kwargs.get('lock'):contending.set()
            return await super()._parent(*args,**kwargs)
    first=asyncio.create_task(First(first_storage.url).execute(*first_args,deadline()))
    await asyncio.wait_for(acquired.wait(),1)
    second=asyncio.create_task(Second(second_storage.url).execute(*second_args,deadline()))
    await asyncio.wait_for(contending.wait(),1)
    release.set()
    return await asyncio.gather(first,second,return_exceptions=True)


@pytest.mark.parametrize('writer',['current','previous-f6'])
@pytest.mark.parametrize('first',['writer','delete'])
def test_native_study_deletion_deterministic_parent_lock_orders(native,writer,first):
    storage,admin_url,runtime,_=native
    study=create(storage,'Deterministic parent race')['study_id']
    if writer=='current':
        note=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value('Before race')),study,None,deadline()))['note_id']
        producer=storage;kind='note.replace';payload=command(kind,expected_revision='1',value=value('Winning current writer'))
    else:
        sys.path.insert(0,str(APP/'tests/fixtures'));from study_deletion_baseline_loader import load
        contract,previous=load();producer=previous.PersonalNotesStorage(runtime);kind='note.create';note=None
        payload=contract.parse_command(kind,json.dumps({'operation_id':str(uuid4()),'value':value('Winning previous writer')}).encode())
    delete=command('study.delete',expected_revision='1')
    writer_args=(IDENTITY,kind,payload,study,note);delete_args=(IDENTITY,'study.delete',delete,study,None)
    if first=='writer':written,erased=run(ordered_parent_commands(producer,writer_args,storage,delete_args))
    else:erased,written=run(ordered_parent_commands(storage,delete_args,producer,writer_args))
    assert isinstance(erased,dict) and erased['command']=='study.delete'
    if first=='writer':assert isinstance(written,dict) and written['command']==kind
    else:assert isinstance(written,NotesError) and written.code=='resource_unavailable'
    with psycopg.connect(admin_url) as c:
        assert c.execute('SELECT active,title,revision FROM scribeswell_studies.studies WHERE id=%s',(study,)).fetchone()==(False,'Deleted study',2)
        rows=c.execute('SELECT active,revision,value FROM scribeswell_studies.notes WHERE study_id=%s',(study,)).fetchall()
        assert len(rows)==(1 if writer=='current' or first=='writer' else 0)
        for active,revision,body in rows:
            assert not active and revision==(3 if writer=='current' and first=='writer' else 2)
            assert body=={'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}
        assert c.execute('SELECT count(*) FROM scribeswell_studies.receipts WHERE operation_id=%s',(delete.operation_id,)).fetchone()[0]==1
        assert c.execute('SELECT count(*) FROM scribeswell_studies.receipts WHERE operation_id=%s',(payload.operation_id,)).fetchone()[0]==(1 if first=='writer' else 0)
    assert run(storage.lookup(IDENTITY,delete.operation_id,'study.delete',deadline()))['outcome']==erased


def test_native_study_deletion_parent_overflow(native):
    storage,admin_url,*_=native
    overflowing=create(storage,'Parent overflow stays active')['study_id']
    with psycopg.connect(admin_url) as c:c.execute('UPDATE scribeswell_studies.studies SET revision=9223372036854775807 WHERE id=%s',(overflowing,))
    overflow=command('study.delete',expected_revision='9223372036854775807')
    with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute(IDENTITY,'study.delete',overflow,overflowing,None,deadline()))
    with psycopg.connect(admin_url) as c:
        assert c.execute('SELECT active,title FROM scribeswell_studies.studies WHERE id=%s',(overflowing,)).fetchone()==(True,'Parent overflow stays active')
        assert not c.execute('SELECT 1 FROM scribeswell_studies.receipts WHERE operation_id=%s',(overflow.operation_id,)).fetchone()


@pytest.mark.parametrize('closed',[False,True])
def test_native_study_deletion_foreign_current_access_cannot_delete_replay_or_lookup(native,closed):
    storage,admin_url,*_=native
    study=create(storage,'Owner private title')['study_id']
    run(storage.execute(IDENTITY,'note.create',command('note.create',value=value('Owner private body')),study,None,deadline()))
    replace_passages(storage,study,passage_items('Gen1'))
    deletion=command('study.delete',expected_revision='1')
    if closed:run(storage.execute(IDENTITY,'study.delete',deletion,study,None,deadline()))
    def snapshot():
        with psycopg.connect(admin_url,row_factory=psycopg.rows.dict_row) as c:
            return {table:c.execute(f'SELECT * FROM scribeswell_studies.{table} WHERE '+('id=%s' if table=='studies' else 'study_id=%s')+' ORDER BY '+('position' if table=='passage_entries' else 'operation_id' if table=='receipts' else 'id' if table in ('studies','notes') else 'study_id'),(study,)).fetchall() for table in ('studies','notes','passage_lists','passage_entries','receipts')}
    before=snapshot();foreign={'account_id':B,'actor_id':ACTOR}
    # This identity is already admitted at the owner boundary; local ownership
    # must independently refuse new commands and the owner's original operation.
    for original in (command('study.delete',expected_revision='1'),deletion):
        with pytest.raises(NotesError,match='resource_unavailable'):run(storage.execute(foreign,'study.delete',original,study,None,deadline()))
        assert snapshot()==before
    assert run(storage.lookup(foreign,deletion.operation_id,'study.delete',deadline()))=={'status':'unresolved'}
    assert snapshot()==before
