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
        alembic.upgrade(Config(str(APP/'studies-alembic.ini')),'head')
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
        failure=target/'history/versions/0002_failure.py'
        failure.write_text("from alembic import op\nrevision='fixture_0002'\ndown_revision='scribeswell_studies_0001'\ndef upgrade():\n op.execute('CREATE TABLE scribeswell_studies.failure_probe(id int)')\n raise RuntimeError('synthetic failure')\n")
        cfg=Config();cfg.set_main_option('script_location',str(target/'history'))
        with pytest.raises(Exception,match='scribeswell_studies_migration_failed'):alembic.upgrade(cfg,'head')
        with psycopg.connect(admin_url) as admin:
            assert admin.execute("SELECT to_regclass('scribeswell_studies.failure_probe')").fetchone()[0] is None
            assert admin.execute('SELECT version_num FROM scribeswell_studies.alembic_version').fetchone()[0]=='scribeswell_studies_0001'
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
