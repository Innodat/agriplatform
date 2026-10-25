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
        alembic.upgrade(Config(str(APP/'studies-alembic.ini')),'head')
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
    with psycopg.connect(admin_url) as c:
        c.execute('UPDATE scribeswell_studies.studies SET active=false WHERE id=%s',(study,))
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
        failure=target/'history/versions/0004_failure.py'
        failure.write_text("from alembic import op\nrevision='fixture_0004'\ndown_revision='scribeswell_studies_0003'\ndef upgrade():\n op.execute('CREATE TABLE scribeswell_studies.failure_probe(id int)')\n raise RuntimeError('synthetic failure')\n")
        cfg=Config();cfg.set_main_option('script_location',str(target/'history'))
        with pytest.raises(Exception,match='scribeswell_studies_migration_failed'):alembic.upgrade(cfg,'head')
        with psycopg.connect(admin_url) as admin:
            assert admin.execute("SELECT to_regclass('scribeswell_studies.failure_probe')").fetchone()[0] is None
            assert admin.execute('SELECT version_num FROM scribeswell_studies.alembic_version').fetchone()[0]=='scribeswell_studies_0003'
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
        with pytest.raises(psycopg.errors.ForeignKeyViolation):c.execute('INSERT INTO scribeswell_studies.notes(id,account_id,study_id,value,created_by,updated_by) VALUES(%s,%s,%s,%s,%s,%s)',(str(uuid4()),A,str(uuid4()),psycopg.types.json.Jsonb(value()),ACTOR,ACTOR))
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
        with psycopg.connect(native[1]) as c:c.execute('UPDATE scribeswell_studies.studies SET active=false WHERE active')
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
        c.execute('UPDATE scribeswell_studies.studies SET active=false WHERE id=%s',(study,))
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
    with psycopg.connect(admin_url) as c:c.execute('UPDATE scribeswell_studies.studies SET active=false WHERE id=%s',(study,))
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
    for statement in ('DELETE FROM scribeswell_studies.passage_lists','UPDATE scribeswell_studies.passage_entries SET book_id=book_id','UPDATE scribeswell_studies.passage_lists SET created_by=created_by'):
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
