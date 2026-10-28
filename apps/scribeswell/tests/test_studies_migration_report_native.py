"""Actual private report/commit proof; parent supplies a uniquely owned PG17 cluster."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from uuid import uuid4

import psycopg
from psycopg import sql
import pytest
from sqlalchemy.engine import make_url

from test_personal_notes_storage import APP, A, B, IDENTITY, command, deadline, run, value
sys.path.insert(0,str(APP/'deployment'))
from studies_release_contract import TARGET, valid_result


@pytest.fixture
def report_database():
    raw=os.environ.get('SCRIBESWELL_NOTES_TEST_ADMIN_URL')
    if not raw:pytest.skip('Explicit fresh local PostgreSQL17 fixture required')
    url=make_url(raw)
    assert url.host=='127.0.0.1' and url.database=='postgres' and url.port not in (55481,55482)
    database='scribeswell_report_'+uuid4().hex
    private=['scribeswell_studies_migrator','scribeswell_studies_runtime','scribeswell_studies_operator']
    public=['anon','authenticated','service_role','scribeswell_runtime']
    created=[]
    database_created=False
    with psycopg.connect(raw,autocommit=True) as admin:
        assert int(admin.execute('SHOW server_version_num').fetchone()[0])>=170000
        assert not admin.execute('SELECT rolname FROM pg_roles WHERE rolname=ANY(%s)',(private+public,)).fetchall(),'Fresh cluster required'
    try:
        with psycopg.connect(raw,autocommit=True) as admin:
            for role in public:
                admin.execute(sql.SQL("CREATE ROLE {} LOGIN PASSWORD 'synthetic-only'").format(sql.Identifier(role)))
                created.append(role)
            admin.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(database)))
            database_created=True
        admin_url=url.set(database=database).render_as_string(hide_password=False)
        with psycopg.connect(admin_url,autocommit=True) as admin:
            admin.execute(sql.SQL('REVOKE TEMPORARY ON DATABASE {} FROM PUBLIC').format(sql.Identifier(database)))
            admin.execute((APP/'tools/sql/prepare_personal_notes_roles.sql').read_text())
            created.extend(private)
            for role in private[:2]:
                admin.execute(sql.SQL("ALTER ROLE {} PASSWORD 'synthetic-only'").format(sql.Identifier(role)))
            admin.execute((APP/'supabase/migrations/20260614000000_scribeswell_create_schema.sql').read_text())
            admin.execute("INSERT INTO scribeswell.book VALUES(1,'Gen','Genesis','בראשית','old','torah',1)")
            admin.execute('GRANT USAGE ON SCHEMA scribeswell TO scribeswell_runtime; GRANT SELECT ON ALL TABLES IN SCHEMA scribeswell TO scribeswell_runtime')
            admin.execute('CREATE POLICY previous_runtime_read ON scribeswell.book FOR SELECT TO scribeswell_runtime USING(true)')
            admin.execute('CREATE SCHEMA foreign_owner; CREATE TABLE foreign_owner.sentinel(id integer); INSERT INTO foreign_owner.sentinel VALUES(1)')
        def login(role):return url.set(database=database,username=role,password='synthetic-only').render_as_string(hide_password=False)
        yield admin_url,login(private[0]),login(private[1]),login('scribeswell_runtime')
    finally:
        # Exact resources from this invocation only. Never discover/drop other fixtures.
        with psycopg.connect(raw,autocommit=True) as admin:
            if database_created:admin.execute(sql.SQL('DROP DATABASE {} WITH (FORCE)').format(sql.Identifier(database)))
            for role in reversed(created):admin.execute(sql.SQL('DROP ROLE {}').format(sql.Identifier(role)))


def invoke(migrator,app=APP):
    environ={key:val for key,val in os.environ.items() if not key.startswith('PG') and key!='SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL'}
    return subprocess.run([sys.executable,str(app/'deployment/studies_migrate.py')],
        input=json.dumps({'url':migrator}),capture_output=True,text=True,env=environ,timeout=30)


def success(result,before):
    assert result.returncode==0,'private worker failed (raw diagnostics suppressed)'
    observed=json.loads(result.stdout)
    assert valid_result(observed) and observed['before']==before and observed['after']==TARGET
    return observed


def failed(result):
    assert result.returncode!=0
    assert json.loads(result.stdout)=={'complete':False,'code':'scribeswell_studies_migration_failed'}
    assert 'postgresql' not in result.stdout and result.stderr==''


def ledger(admin_url):
    with psycopg.connect(admin_url) as admin:
        return admin.execute('SELECT version_num FROM scribeswell_studies.alembic_version').fetchall()


def public_read(url):
    # Genuine existing public API consumer remains open across private upgrade/repeat.
    from database import Database
    from services import bible_service
    database=Database(url,'scribeswell_runtime');database.open()
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(bible_service,'get_database',lambda:database)
        try:return bible_service.get_books().model_dump(mode='json')
        finally:database.close()


def history_copy(target):
    shutil.copytree(APP/'studies-migrations',target/'studies-migrations')
    shutil.copytree(APP/'studies-database-tools',target/'studies-database-tools')
    shutil.copy2(APP/'studies-alembic.ini',target/'studies-alembic.ini')
    (target/'deployment').mkdir()
    for source in ('studies_migrate.py','studies_release_contract.py'):
        shutil.copy2(APP/'deployment'/source,target/'deployment'/source)
    return target


def previous_one(migrator,tmp_path,monkeypatch):
    from alembic import command as alembic
    from alembic.config import Config
    target=history_copy(tmp_path/'previous')
    for source in (target/'studies-migrations/versions').glob('*.py'):
        if not source.name.startswith('0001_'):source.unlink()
    monkeypatch.setenv('SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL',migrator)
    config=Config(str(target/'studies-alembic.ini'))
    alembic.upgrade(config,'head')
    # Ordinary head-only Alembic still supports genuinely frozen historical packages.
    assert config.attributes['scribeswell_studies_before'] is None
    assert config.attributes['scribeswell_studies_after']=='scribeswell_studies_0001'


def old_consumer(runtime):
    spec=importlib.util.spec_from_file_location('report_previous_consumer',APP/'tests/fixtures/personal_notes_storage_previous.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.PersonalNotesStorage(runtime)


def seed_previous(storage):
    study=run(storage.execute(IDENTITY,'study.create',command('study.create',title='Preserved private study'),None,None,deadline()))['study_id']
    note=run(storage.execute(IDENTITY,'note.create',command('note.create',value=value('Preserved private note')),study,None,deadline()))
    before=run(storage.read(IDENTITY,study,note['note_id'],deadline()))
    return study,note,before


def test_fresh_worker_reports_committed_head_and_repeat_preserves_public(report_database):
    admin,migrator,_,public=report_database
    previous=public_read(public)
    success(invoke(migrator),None)
    assert ledger(admin)==[(TARGET,)]
    success(invoke(migrator),TARGET)
    assert ledger(admin)==[(TARGET,)] and public_read(public)==previous


def test_head_saved_rows_revisions_and_receipts_survive_private_disable_and_restore(report_database,monkeypatch):
    """A route/config transition never reverses schema or overwrites saved data."""
    from datetime import datetime,timezone
    from fastapi.testclient import TestClient
    import httpx
    from pydantic import SecretStr
    import config
    import personal_notes_access
    from personal_notes_storage import PersonalNotesStorage
    from database import Database
    from services import bible_service
    admin,migrator,runtime,public=report_database
    success(invoke(migrator),None)
    storage=PersonalNotesStorage(runtime)
    study,note,_=seed_previous(storage)
    update=command('note.replace',expected_revision='1',value=value('Saved current-head observation'))
    acknowledged=run(storage.execute(IDENTITY,'note.replace',update,study,note['note_id'],deadline()))
    before=run(storage.read(IDENTITY,study,note['note_id'],deadline()))
    assert before['revision']=='2'
    public_database=Database(public,'scribeswell_runtime');public_database.open()
    monkeypatch.setattr(bible_service,'get_database',lambda:public_database)
    calls=[]
    def check(request):
        calls.append(request.url.path)
        return httpx.Response(200,json={'account_id':A,'actor_id':IDENTITY['actor_id'],'decision_id':str(uuid4()),
            'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'},'checked_at':datetime.now(timezone.utc).isoformat()})
    original=personal_notes_access.StudiesAccess
    monkeypatch.setattr(personal_notes_access,'StudiesAccess',lambda url,key,**kwargs:original(url,key,httpx.MockTransport(check),**kwargs))
    monkeypatch.setattr(config.settings,'scribeswell_studies_database_url',SecretStr(runtime))
    monkeypatch.setattr(config.settings,'scribeswell_studies_access_url','http://access:8000')
    monkeypatch.setattr(config.settings,'scribeswell_studies_service_key',SecretStr('synthetic-server-only'))
    monkeypatch.setattr(config.settings,'scribeswell_studies_account_id',A)
    def mounted(enabled):
        monkeypatch.setattr(config.settings,'scribeswell_studies_enabled',enabled)
        spec=importlib.util.spec_from_file_location('bounded_native_'+uuid4().hex,APP/'backend/main.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return TestClient(module.app)
    headers={'Authorization':'Bearer current'};path=f'/api/studies/{study}/notes/{note["note_id"]}'
    try:
        enabled=mounted(True)
        assert enabled.get(path,headers=headers).json()==before
        public_before=enabled.get('/api/bible/books').json()
        disabled=mounted(False)
        assert disabled.get(path,headers=headers).status_code==404
        assert disabled.get('/api/bible/books').json()==public_before
        assert ledger(admin)==[(TARGET,)]
        restored=mounted(True)
        assert restored.get(path,headers=headers).json()==before
        receipt=restored.get('/api/operations/'+update.operation_id+'?command=note.replace',headers=headers)
        assert receipt.status_code==200 and receipt.json()=={'status':'committed','outcome':acknowledged}
        assert restored.get('/api/bible/books').json()==public_before
        assert calls==['/v2/check']*3
        success(invoke(migrator),TARGET)
        assert run(storage.read(IDENTITY,study,note['note_id'],deadline()))==before
    finally:public_database.close()


def test_previous_populated_worker_and_repeat_preserve_previous_consumers_and_denials(report_database,tmp_path,monkeypatch):
    admin,migrator,runtime,public=report_database
    previous_one(migrator,tmp_path,monkeypatch)
    storage=old_consumer(runtime);study,note,before=seed_previous(storage)
    public_before=public_read(public)
    success(invoke(migrator),'scribeswell_studies_0001')
    assert ledger(admin)==[(TARGET,)]
    assert run(storage.read(IDENTITY,study,note['note_id'],deadline()))==before
    assert run(storage.lookup(IDENTITY,note['operation_id'],'note.create',deadline()))['outcome']==note
    success(invoke(migrator),TARGET)
    assert run(storage.read(IDENTITY,study,note['note_id'],deadline()))==before
    assert public_read(public)==public_before
    # Prior running private consumer still writes, and the same restricted login
    # retains real owner/ledger/DDL/cross-account denial after the release helper.
    run(storage.execute(IDENTITY,'note.replace',command('note.replace',expected_revision='1',value=value('Previous consumer still writes')),study,note['note_id'],deadline()))
    for statement in ('SELECT * FROM scribeswell_studies.alembic_version','CREATE TABLE scribeswell_studies.forbidden(id int)','SELECT * FROM foreign_owner.sentinel'):
        with psycopg.connect(runtime) as connection:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):connection.execute(statement)
    with psycopg.connect(runtime) as connection:
        connection.execute("SELECT set_config('app.account_id',%s,true)",(B,))
        assert connection.execute('SELECT count(*) FROM scribeswell_studies.notes').fetchone()==(0,)


@pytest.mark.parametrize('failure',['migration','commit'])
def test_failed_migration_or_commit_has_no_success_observations_and_forward_retry(report_database,tmp_path,monkeypatch,failure):
    from alembic import command as alembic
    from alembic.config import Config
    admin,migrator,runtime,public=report_database
    previous_one(migrator,tmp_path,monkeypatch)
    storage=old_consumer(runtime);study,note,before=seed_previous(storage)
    public_before=public_read(public)
    app=history_copy(tmp_path/'failing')
    migration=app/'studies-migrations/versions/0009_note_metadata_predicates.py'
    original=migration.read_text()
    if failure=='migration':
        migration.write_text(original.replace('\ndef downgrade():',"\n raise RuntimeError('synthetic failure after actual DDL')\n\ndef downgrade():"))
    else:
        # Deferred PostgreSQL trigger fires at COMMIT, after after-head observation.
        with psycopg.connect(admin) as connection:
            connection.execute("CREATE FUNCTION scribeswell_studies.fixture_commit_failure() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.version_num='scribeswell_studies_0009' THEN RAISE EXCEPTION 'synthetic deferred failure'; END IF; RETURN NEW; END $$")
            connection.execute('CREATE CONSTRAINT TRIGGER fixture_commit_failure AFTER INSERT OR UPDATE ON scribeswell_studies.alembic_version DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION scribeswell_studies.fixture_commit_failure()')
    config=Config(str(app/'studies-alembic.ini'))
    config.attributes.update(scribeswell_studies_expected_head=TARGET,scribeswell_studies_before='stale',scribeswell_studies_after='stale')
    with pytest.raises(Exception,match='scribeswell_studies_migration_failed'):
        alembic.upgrade(config,'head')
    assert 'scribeswell_studies_before' not in config.attributes and 'scribeswell_studies_after' not in config.attributes
    failed(invoke(migrator,app))
    assert ledger(admin)==[('scribeswell_studies_0001',)]
    with psycopg.connect(admin) as connection:
        assert connection.execute("SELECT to_regclass('scribeswell_studies.note_revision_metadata')").fetchone()==(None,)
    assert run(storage.read(IDENTITY,study,note['note_id'],deadline()))==before
    assert public_read(public)==public_before
    if failure=='commit':
        with psycopg.connect(admin) as connection:
            connection.execute('DROP TRIGGER fixture_commit_failure ON scribeswell_studies.alembic_version')
            connection.execute('DROP FUNCTION scribeswell_studies.fixture_commit_failure()')
    else:migration.write_text(original)
    success(invoke(migrator,app),'scribeswell_studies_0001')
    success(invoke(migrator,app),TARGET)
    assert run(storage.read(IDENTITY,study,note['note_id'],deadline()))==before


@pytest.mark.parametrize('versions',[['unknown'],['scribeswell_studies_0001','scribeswell_studies_0002']])
def test_unknown_or_multiple_current_heads_refuse_without_changes(report_database,tmp_path,monkeypatch,versions):
    admin,migrator,runtime,_=report_database
    previous_one(migrator,tmp_path,monkeypatch)
    storage=old_consumer(runtime);study,note,before=seed_previous(storage)
    with psycopg.connect(admin) as connection:
        connection.execute('DELETE FROM scribeswell_studies.alembic_version')
        for version in versions:connection.execute('INSERT INTO scribeswell_studies.alembic_version(version_num) VALUES(%s)',(version,))
    failed(invoke(migrator))
    assert sorted(ledger(admin))==sorted((version,) for version in versions)
    assert run(storage.read(IDENTITY,study,note['note_id'],deadline()))==before
