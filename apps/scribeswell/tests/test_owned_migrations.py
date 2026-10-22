"""Adoption is a verified operation, never blind stamping."""
from pathlib import Path
import importlib.util

APP = Path(__file__).resolve().parents[1]

def test_owned_baseline_has_independent_pinned_reference():
    assert (APP / 'migrations/reference.json').is_file()
    spec = importlib.util.spec_from_file_location('scribeswell_baseline', APP / 'migrations/baseline.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.verify_pins()

import json
import os
import subprocess
import sys
from urllib.parse import urlsplit,quote,unquote
import pytest
sys.path.insert(0,str(APP / 'migrations'))
from generate_reference import prepared_fixture
from baseline import REVISION

def migration_url(url):
    parsed=urlsplit(url)
    return parsed._replace(netloc='scribeswell_migrator:'+quote(unquote(parsed.password or ''),safe='')+'@'+parsed.hostname+':'+str(parsed.port)).geturl()

@pytest.fixture(scope='module')
def migration_database():
    if not os.environ.get('SCRIBESWELL_TEST_DATABASE_URL'):
        pytest.skip('Set SCRIBESWELL_TEST_DATABASE_URL to a disposable local cluster')
    with prepared_fixture() as value:
        yield value

@pytest.fixture
def prepared(migration_database):
    admin,url=migration_database
    admin.prepare_threshold=None
    admin.execute('DROP TABLE IF EXISTS scribeswell.alembic_version')
    yield admin,url

def invoke(url,command='upgrade',revision='head',extra_env=None):
    env={k:v for k,v in os.environ.items() if not k.startswith('PG')}
    env['SCRIBESWELL_MIGRATION_DATABASE_URL']=migration_url(url)
    env.update(extra_env or {})
    return subprocess.run([sys.executable,'-m','alembic','-c',str(APP/'alembic.ini'),command,revision],env=env,capture_output=True,text=True,timeout=20)

def business_state(admin):
    return {table:admin.execute('SELECT * FROM scribeswell.'+table+' ORDER BY id').fetchall() for table in ['book','chapter','verse','word','morpheme']} | {s:admin.execute('SELECT last_value,is_called FROM scribeswell.'+s+'_id_seq').fetchone() for s in ['chapter','verse','word','morpheme']}

def test_upgrade_and_replay_preserve_rows_sequences_and_access(prepared):
    admin,url=prepared
    admin.execute("INSERT INTO scribeswell.book VALUES (1,'Gen','Genesis','א','old','torah',1) ON CONFLICT DO NOTHING")
    admin.execute('INSERT INTO scribeswell.chapter VALUES (101,1,1) ON CONFLICT DO NOTHING')
    before=business_state(admin)
    first=invoke(url)
    assert first.returncode==0,first.stderr
    assert business_state(admin)==before
    assert admin.execute('SELECT * FROM scribeswell.alembic_version').fetchall()==[(REVISION,)]
    assert invoke(url).returncode==0
    assert business_state(admin)==before
    assert not admin.execute("SELECT 1 FROM pg_class c,LATERAL aclexplode(c.relacl) a WHERE c.oid='scribeswell.alembic_version'::regclass AND a.grantee<>c.relowner").fetchall()
    for role in ['scribeswell_runtime','scribeswell_import','service_role']:
        with admin.transaction():
            admin.execute('SET LOCAL ROLE '+role)
            assert admin.execute('SELECT count(*) FROM scribeswell.'+('book' if role=='scribeswell_import' else 'book_read')).fetchone()[0]==1

@pytest.mark.parametrize('change,restore',[
    ('ALTER TABLE scribeswell.book ALTER COLUMN name_en DROP NOT NULL','ALTER TABLE scribeswell.book ALTER COLUMN name_en SET NOT NULL'),
    ('ALTER TABLE scribeswell.book DISABLE ROW LEVEL SECURITY','ALTER TABLE scribeswell.book ENABLE ROW LEVEL SECURITY'),
    ('CREATE TABLE scribeswell.extra(id int)','DROP TABLE scribeswell.extra'),
    ('GRANT UPDATE ON scribeswell.book TO anon','REVOKE UPDATE ON scribeswell.book FROM anon'),
    ('GRANT UPDATE(name_en) ON scribeswell.book TO anon','REVOKE UPDATE(name_en) ON scribeswell.book FROM anon'),
    ('ALTER VIEW scribeswell.book_read OWNER TO postgres','ALTER VIEW scribeswell.book_read OWNER TO scribeswell_migrator'),
    ('ALTER ROLE scribeswell_migrator CREATEDB','ALTER ROLE scribeswell_migrator NOCREATEDB'),
    ('GRANT scribeswell_import TO scribeswell_migrator','REVOKE scribeswell_import FROM scribeswell_migrator'),
    ('ALTER DEFAULT PRIVILEGES IN SCHEMA scribeswell GRANT INSERT ON TABLES TO anon','ALTER DEFAULT PRIVILEGES IN SCHEMA scribeswell REVOKE INSERT ON TABLES FROM anon'),
    ('ALTER POLICY direct_read ON scribeswell.book USING (false)','ALTER POLICY direct_read ON scribeswell.book USING (true)'),
    ('CREATE COLLATION scribeswell.extra FROM pg_catalog."C"','DROP COLLATION scribeswell.extra'),
    ('CREATE FUNCTION scribeswell.extra() RETURNS int LANGUAGE sql AS $$SELECT 1$$','DROP FUNCTION scribeswell.extra()'),
])
def test_rejects_drift_before_ledger(prepared,change,restore):
    admin,url=prepared
    before=business_state(admin)
    admin.execute(change)
    try:
        result=invoke(url)
        assert result.returncode!=0
        assert admin.execute("SELECT to_regclass('scribeswell.alembic_version')").fetchone()==(None,)
        assert business_state(admin)==before
    finally:
        admin.execute(restore)

@pytest.mark.parametrize('definition',[
    'CREATE TABLE scribeswell.alembic_version(version_num varchar(32) PRIMARY KEY)',
    "CREATE TABLE scribeswell.alembic_version(version_num varchar(32) PRIMARY KEY); INSERT INTO scribeswell.alembic_version VALUES ('unknown')",
    "CREATE TABLE scribeswell.alembic_version(version_num varchar(32)); INSERT INTO scribeswell.alembic_version VALUES ('scribeswell_0001'),('scribeswell_0001')",
    "CREATE TABLE scribeswell.alembic_version(version_num text); INSERT INTO scribeswell.alembic_version VALUES ('scribeswell_0001')",
])
def test_rejects_existing_unqualified_ledger(prepared,definition):
    admin,url=prepared
    admin.execute(definition)
    before=admin.execute('SELECT * FROM scribeswell.alembic_version').fetchall()
    assert invoke(url).returncode!=0
    assert admin.execute('SELECT * FROM scribeswell.alembic_version').fetchall()==before

@pytest.mark.parametrize('command,revision',[('stamp','head'),('downgrade','base')])
def test_rejects_unsupported_commands(prepared,command,revision):
    admin,url=prepared
    assert invoke(url,command,revision).returncode!=0
    assert admin.execute("SELECT to_regclass('scribeswell.alembic_version')").fetchone()==(None,)

def test_lock_timeout_then_retry(prepared):
    admin,url=prepared
    with admin.transaction():
        admin.execute("SELECT pg_advisory_xact_lock(hashtext('scribeswell-owned-migrations'))")
        result=invoke(url)
        assert result.returncode!=0
        assert admin.execute("SELECT to_regclass('scribeswell.alembic_version')").fetchone()==(None,)
    assert invoke(url).returncode==0

def test_ambient_pg_does_not_redirect(prepared):
    admin,url=prepared
    assert invoke(url,extra_env={'PGHOST':'invalid.example','PGOPTIONS':'-c role=postgres','PGSERVICE':'untrusted'}).returncode==0

def test_concurrent_upgrades_serialize(prepared):
    from concurrent.futures import ThreadPoolExecutor
    admin,url=prepared
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes=list(pool.map(lambda _:invoke(url),range(2)))
    assert [result.returncode for result in outcomes]==[0,0]
    assert admin.execute('SELECT * FROM scribeswell.alembic_version').fetchall()==[(REVISION,)]

@pytest.mark.parametrize('change,restore',[
    ('ALTER SCHEMA scribeswell RENAME TO absent','ALTER SCHEMA absent RENAME TO scribeswell'),
    ('ALTER TABLE scribeswell.word RENAME TO absent','ALTER TABLE scribeswell.absent RENAME TO word'),
    ('CREATE SCHEMA unrelated AUTHORIZATION scribeswell_migrator','DROP SCHEMA unrelated'),
    ('CREATE SCHEMA unrelated; CREATE TABLE unrelated.secret(id int); GRANT SELECT ON unrelated.secret TO scribeswell_migrator','DROP SCHEMA unrelated CASCADE'),
    ('CREATE SCHEMA unrelated; CREATE TABLE unrelated.secret(id int); GRANT SELECT(id) ON unrelated.secret TO scribeswell_migrator','DROP SCHEMA unrelated CASCADE'),
    ('CREATE SCHEMA unrelated; GRANT CREATE ON SCHEMA unrelated TO PUBLIC','DROP SCHEMA unrelated'),
    ('CREATE SCHEMA unrelated; CREATE TABLE unrelated.secret(id int); GRANT USAGE ON SCHEMA unrelated TO PUBLIC; GRANT SELECT ON unrelated.secret TO PUBLIC','DROP SCHEMA unrelated CASCADE'),
    ('ALTER ROLE scribeswell_import SUPERUSER','ALTER ROLE scribeswell_import NOSUPERUSER'),
])
def test_missing_partial_or_extra_authority(prepared,change,restore):
    admin,url=prepared
    admin.execute(change)
    try:
        assert invoke(url).returncode!=0
        assert admin.execute("SELECT to_regclass('scribeswell.alembic_version')").fetchone()==(None,)
    finally:admin.execute(restore)

@pytest.mark.parametrize('change',[
    'CREATE INDEX extra_ledger ON scribeswell.alembic_version(version_num)',
    "ALTER TABLE scribeswell.alembic_version ALTER COLUMN version_num SET DEFAULT 'scribeswell_0001'",
    'REVOKE SELECT ON scribeswell.alembic_version FROM scribeswell_migrator',
    'GRANT SELECT ON scribeswell.alembic_version TO scribeswell_runtime',
    'ALTER TABLE scribeswell.alembic_version OWNER TO postgres',
    "DELETE FROM scribeswell.alembic_version",
    "UPDATE scribeswell.alembic_version SET version_num='unknown'",
])
def test_replay_rejects_ledger_drift(prepared,change):
    admin,url=prepared
    assert invoke(url).returncode==0
    admin.execute(change)
    assert invoke(url).returncode!=0

@pytest.mark.parametrize('command',['stamp','downgrade','ensure_version'])
def test_programmatic_unsupported_routes(prepared,command,monkeypatch):
    from alembic import command as commands
    from alembic.config import Config
    admin,url=prepared
    monkeypatch.setenv('SCRIBESWELL_MIGRATION_DATABASE_URL',migration_url(url))
    args=() if command=='ensure_version' else ('head' if command=='stamp' else 'base',)
    with pytest.raises(RuntimeError,match='scribeswell_upgrade_only'):
        getattr(commands,command)(Config(str(APP/'alembic.ini')),*args)
    assert admin.execute("SELECT to_regclass('scribeswell.alembic_version')").fetchone()==(None,)

def load_adapter():
    spec=importlib.util.spec_from_file_location('scribeswell_migration_adapter',APP/'deployment/migrate.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

VALID_ENV={'SUPABASE_URL':'https://demo.supabase.co','SCRIBESWELL_MIGRATION_DATABASE_URL':'postgresql://scribeswell_migrator:secret@db.demo.supabase.co/postgres?sslmode=require'}

def test_adapter_safe_evidence_and_stripped_environment(tmp_path):
    adapter=load_adapter();calls=[]
    class Process:
        returncode=0
        def __init__(self,args,**kwargs):calls.append((args,kwargs))
        def communicate(self,request,**kwargs):
            assert json.loads(request)['url']==VALID_ENV['SCRIBESWELL_MIGRATION_DATABASE_URL']
            return json.dumps({'before':None,'after':REVISION}),None
        def poll(self):return 0
    target=tmp_path/'evidence.json'
    result=adapter.main(target,environ=VALID_ENV|{'PGHOST':'hostile','PGOPTIONS':'-c role=postgres'},run=Process)
    assert result['complete'] and result['owners']['scribeswell']['status']=='succeeded'
    assert not any(k.startswith('PG') or k=='SCRIBESWELL_MIGRATION_DATABASE_URL' for k in calls[0][1]['env'])
    assert 'secret' not in target.read_text()
    previous=target.read_bytes()
    with pytest.raises(SystemExit):adapter.main(target,environ=VALID_ENV,run=lambda *a,**k:pytest.fail('must not launch'))
    assert target.read_bytes()==previous

@pytest.mark.parametrize('environment',[
    {}, VALID_ENV|{'SUPABASE_URL':'https://other.supabase.co'},
    VALID_ENV|{'SCRIBESWELL_MIGRATION_DATABASE_URL':'postgresql://postgres:secret@db.demo.supabase.co/postgres?sslmode=require'},
    VALID_ENV|{'SCRIBESWELL_MIGRATION_DATABASE_URL':VALID_ENV['SCRIBESWELL_MIGRATION_DATABASE_URL']+'&options=-crole=postgres'},
])
def test_adapter_rejects_bad_configuration_before_worker(tmp_path,environment):
    target=tmp_path/'evidence.json'
    with pytest.raises(SystemExit):load_adapter().main(target,environ=environment,run=lambda *a,**k:pytest.fail('must not launch'))
    report=json.loads(target.read_text())
    assert not report['complete'] and report['owners']['scribeswell']['status']=='failed'
    assert 'secret' not in target.read_text()

def test_adapter_timeout_kills_reaps_and_marks_unknown(tmp_path):
    events=[]
    class Process:
        def __init__(self,*args,**kwargs):self.returncode=None
        def communicate(self,*args,**kwargs):
            events.append('communicate')
            if self.returncode is None:raise subprocess.TimeoutExpired('worker',.01)
            return '',None
        def kill(self):events.append('kill');self.returncode=-9
        def poll(self):return self.returncode
    target=tmp_path/'evidence.json'
    with pytest.raises(SystemExit):load_adapter().main(target,environ=VALID_ENV,run=Process,timeout=.01)
    report=json.loads(target.read_text())
    assert report['complete'] is False and report['owners']['scribeswell']['status']=='unknown'
    assert events==['communicate','kill','communicate']

def test_offline_upgrade_rejected_before_mutation(prepared,monkeypatch):
    from alembic import command
    from alembic.config import Config
    admin,url=prepared
    monkeypatch.setenv('SCRIBESWELL_MIGRATION_DATABASE_URL',migration_url(url))
    with pytest.raises(RuntimeError,match='scribeswell_offline_prohibited'):
        command.upgrade(Config(str(APP/'alembic.ini')),'head',sql=True)
    assert admin.execute("SELECT to_regclass('scribeswell.alembic_version')").fetchone()==(None,)

def test_real_supervised_worker_records_committed_before_after(prepared,tmp_path,monkeypatch):
    admin,url=prepared
    adapter=load_adapter()
    # Production binding is covered above; local fixture gets no production bypass.
    monkeypatch.setattr(adapter,'validate_url',lambda env:migration_url(url))
    target=tmp_path/'actual.json'
    result=adapter.main(target,environ={})
    assert result['complete']
    assert result['owners']['scribeswell']=={'status':'succeeded','before':None,'after':REVISION}
    assert admin.execute('SELECT * FROM scribeswell.alembic_version').fetchall()==[(REVISION,)]

@pytest.mark.parametrize('output',['not-json','[]','{}','{"before":null,"after":"unknown"}','{"before":[],"after":"scribeswell_0001"}'])
def test_adapter_malformed_results_fail_safely(tmp_path,output):
    class Process:
        returncode=0
        def __init__(self,*args,**kwargs):pass
        def communicate(self,*args,**kwargs):return output,None
        def poll(self):return 0
    target=tmp_path/'evidence.json'
    with pytest.raises(SystemExit):load_adapter().main(target,environ=VALID_ENV,run=Process)
    report=json.loads(target.read_text())
    assert not report['complete'] and report['owners']['scribeswell']['status']=='failed'

def test_actual_database_connection_failure_safe_evidence(tmp_path,monkeypatch):
    adapter=load_adapter()
    monkeypatch.setattr(adapter,'validate_url',lambda env:'postgresql://scribeswell_migrator:secret@127.0.0.1:1/postgres')
    target=tmp_path/'failure.json'
    with pytest.raises(SystemExit):adapter.main(target,environ={})
    report=json.loads(target.read_text())
    assert not report['complete'] and report['owners']['scribeswell']['outcome_requires_reconciliation']
    assert 'secret' not in target.read_text() and 'postgresql' not in target.read_text()

@pytest.mark.parametrize('change,restore',[
    ('ALTER TABLE scribeswell.chapter DISABLE TRIGGER ALL','ALTER TABLE scribeswell.chapter ENABLE TRIGGER ALL'),
    ('CREATE SCHEMA unrelated; CREATE TABLE unrelated.secret(id int); GRANT USAGE ON SCHEMA unrelated TO PUBLIC; GRANT SELECT(id) ON unrelated.secret TO PUBLIC','DROP SCHEMA unrelated CASCADE'),
    ('CREATE SCHEMA unrelated; GRANT USAGE ON SCHEMA unrelated TO PUBLIC; CREATE FUNCTION unrelated.privileged() RETURNS int LANGUAGE sql SECURITY DEFINER AS $$SELECT 1$$','DROP SCHEMA unrelated CASCADE'),
    ('CREATE SCHEMA unrelated; ALTER DEFAULT PRIVILEGES IN SCHEMA unrelated GRANT SELECT ON TABLES TO scribeswell_migrator','ALTER DEFAULT PRIVILEGES IN SCHEMA unrelated REVOKE SELECT ON TABLES FROM scribeswell_migrator; DROP SCHEMA unrelated'),
])
def test_reviewed_authority_and_trigger_gaps_reject_before_ledger(prepared,change,restore):
    admin,url=prepared
    before=business_state(admin)
    admin.execute(change)
    try:
        assert invoke(url).returncode!=0
        assert admin.execute("SELECT to_regclass('scribeswell.alembic_version')").fetchone()==(None,)
        assert business_state(admin)==before
    finally:admin.execute(restore)
    assert invoke(url).returncode==0


def test_public_database_create_rejected(prepared):
    from psycopg import sql
    admin,url=prepared
    name=admin.info.dbname
    assert not admin.execute("SELECT has_database_privilege('scribeswell_migrator',current_database(),'CREATE')").fetchone()[0]
    admin.execute(sql.SQL('GRANT CREATE ON DATABASE {} TO PUBLIC').format(sql.Identifier(name)))
    try:
        assert invoke(url).returncode!=0
        assert admin.execute("SELECT to_regclass('scribeswell.alembic_version')").fetchone()==(None,)
    finally:
        admin.execute(sql.SQL('REVOKE CREATE ON DATABASE {} FROM PUBLIC').format(sql.Identifier(name)))
    assert not admin.execute("SELECT has_database_privilege('scribeswell_migrator',current_database(),'CREATE')").fetchone()[0]
    assert invoke(url).returncode==0


@pytest.mark.parametrize('revision',['base',REVISION])
def test_nonhead_upgrade_rejected_cli_and_programmatic(prepared,monkeypatch,revision):
    from alembic import command
    from alembic.config import Config
    admin,url=prepared
    assert invoke(url).returncode==0
    before=business_state(admin)
    assert invoke(url,revision=revision).returncode!=0
    monkeypatch.setenv('SCRIBESWELL_MIGRATION_DATABASE_URL',migration_url(url))
    with pytest.raises(RuntimeError,match='scribeswell_upgrade_head_only'):
        command.upgrade(Config(str(APP/'alembic.ini')),revision)
    assert admin.execute('SELECT * FROM scribeswell.alembic_version').fetchall()==[(REVISION,)]
    assert business_state(admin)==before


def test_postvalidation_failure_rolls_back_created_ledger(prepared,monkeypatch):
    import baseline
    from alembic import command
    from alembic.config import Config
    admin,url=prepared
    before=business_state(admin)
    original=baseline.preflight
    observed=[]
    def injected(connection):
        if observed:
            assert connection.exec_driver_sql('SELECT version_num FROM scribeswell.alembic_version').scalar()==REVISION
            observed.append('ledger_exists_inside_transaction')
            raise baseline.BaselineError('injected_postvalidation_failure')
        state=original(connection)
        observed.append('preflight_passed')
        return state
    monkeypatch.setattr(baseline,'preflight',injected)
    monkeypatch.setenv('SCRIBESWELL_MIGRATION_DATABASE_URL',migration_url(url))
    with pytest.raises(RuntimeError,match='injected_postvalidation_failure'):
        command.upgrade(Config(str(APP/'alembic.ini')),'head')
    assert observed==['preflight_passed','ledger_exists_inside_transaction']
    # admin is a separate connection from the actual migrator transaction.
    assert admin.execute("SELECT to_regclass('scribeswell.alembic_version')").fetchone()==(None,)
    assert business_state(admin)==before


@pytest.mark.parametrize('before',[None,REVISION])
def test_failed_worker_preserves_valid_known_before(tmp_path,before):
    class Process:
        returncode=1
        def __init__(self,*args,**kwargs):pass
        def communicate(self,*args,**kwargs):
            return json.dumps({'code':'scribeswell_migration_failed','before':before}),None
        def poll(self):return 1
    target=tmp_path/'failed.json'
    with pytest.raises(SystemExit):load_adapter().main(target,environ=VALID_ENV,run=Process)
    entry=json.loads(target.read_text())['owners']['scribeswell']
    assert entry['before']==before
    assert 'after' not in entry
    assert entry['status']=='failed' and entry['outcome_requires_reconciliation']


def test_worker_emits_known_before_after_upgrade_failure(monkeypatch,capsys):
    import io
    from alembic import command
    def fail(config,revision):
        config.attributes['scribeswell_before']=REVISION
        raise RuntimeError('sensitive-error-must-not-cross-ipc')
    monkeypatch.setattr(command,'upgrade',fail)
    monkeypatch.setattr(sys,'stdin',io.StringIO(json.dumps({'url':'postgresql://scribeswell_migrator:secret@127.0.0.1:1/postgres'})))
    with pytest.raises(SystemExit):load_adapter().worker()
    assert json.loads(capsys.readouterr().out)=={'code':'scribeswell_migration_failed','before':REVISION}


@pytest.mark.parametrize('response',[
    {'code':'scribeswell_migration_failed','before':'secret'},
    {'code':'scribeswell_migration_failed','before':[]},
    {'code':'scribeswell_migration_failed','before':REVISION,'after':REVISION},
    {'code':'untrusted','before':REVISION},
])
def test_failed_worker_rejects_unvalidated_observations(tmp_path,response):
    class Process:
        returncode=1
        def __init__(self,*args,**kwargs):pass
        def communicate(self,*args,**kwargs):return json.dumps(response),None
        def poll(self):return 1
    target=tmp_path/'failed.json'
    with pytest.raises(SystemExit):load_adapter().main(target,environ=VALID_ENV,run=Process)
    entry=json.loads(target.read_text())['owners']['scribeswell']
    assert 'before' not in entry and 'after' not in entry
    assert entry['status']=='failed' and entry['outcome_requires_reconciliation']
    assert 'secret' not in target.read_text()


def test_actual_worker_timeout_reaps_and_releases_transaction(prepared,tmp_path,monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    import time
    import psycopg
    admin,url=prepared
    before=business_state(admin)
    adapter=load_adapter()
    monkeypatch.setattr(adapter,'validate_url',lambda env:migration_url(url))
    target=tmp_path/'timeout.json'
    with psycopg.connect(url,autocommit=True) as observer:
        with admin.transaction():
            admin.execute("SELECT pg_advisory_xact_lock(hashtext('scribeswell-owned-migrations'))")
            with ThreadPoolExecutor(max_workers=1) as executor:
                attempt=executor.submit(adapter.main,target,environ={},timeout=2.5)
                deadline=time.monotonic()+2
                waiting=[]
                while time.monotonic()<deadline:
                    waiting=observer.execute("SELECT pid FROM pg_stat_activity WHERE datname=current_database() AND usename='scribeswell_migrator' AND wait_event='advisory'").fetchall()
                    if waiting:break
                    time.sleep(.02)
                assert waiting,'real migrator must be observed waiting on the held owner lock'
                with pytest.raises(SystemExit):attempt.result(timeout=8)
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                remaining=observer.execute('SELECT pid FROM pg_stat_activity WHERE pid=ANY(%s)',([row[0] for row in waiting],)).fetchall()
                if not remaining:break
                time.sleep(.02)
            assert not remaining,'killed worker backend must disappear while the owner lock remains held'
            assert observer.execute("SELECT to_regclass('scribeswell.alembic_version')").fetchone()==(None,)
    report=json.loads(target.read_text())
    assert report['complete'] is False
    assert report['owners']['scribeswell']=={'status':'unknown','outcome_requires_reconciliation':True}
    assert business_state(admin)==before
    assert 'fixture' not in target.read_text() and 'postgresql' not in target.read_text()
