"""Focused pre-effect route guards; native qualification proves database behavior."""
from pathlib import Path
import runpy
import sys
from types import SimpleNamespace
import pytest

OWNER=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(OWNER/'migrations'))


def test_only_exact_known_history_is_accepted():
    from access_baseline import validate_revision,BaselineError
    for rows in ([],['unknown'],['access_0001','access_0002']):
        with pytest.raises(BaselineError,match='access_unknown_history'):validate_revision(rows)
    assert validate_revision(['access_0001'])=='access_0001'
    assert validate_revision(['access_0002'])=='access_0002'


@pytest.mark.parametrize('offline,command',[(True,'upgrade'),(False,'stamp'),(False,'downgrade')])
def test_non_upgrade_routes_refuse_before_connecting(monkeypatch,offline,command):
    import sqlalchemy
    from alembic import context
    from access_baseline import BaselineError
    monkeypatch.setattr(context,'is_offline_mode',lambda:offline)
    function=lambda:None;function.__name__=command
    monkeypatch.setattr(context,'config',SimpleNamespace(cmd_opts=SimpleNamespace(cmd=(function,))),raising=False)
    def connect(*args,**kwargs):pytest.fail('prohibited route connected')
    monkeypatch.setattr(sqlalchemy,'create_engine',connect)
    with pytest.raises(BaselineError,match='access_offline_migrations_prohibited' if offline else 'access_use_verified_upgrade_route'):
        runpy.run_path(str(OWNER/'migrations/env.py'))


def test_programmatic_stamp_refuses_before_preflight_or_ddl(monkeypatch):
    import sqlalchemy
    import access_baseline
    from alembic import context
    events=[]
    class Connection:
        dialect=SimpleNamespace(server_version_info=(17,))
        def __enter__(self):return self
        def __exit__(self,*args):events.append('rollback' if args[0] else 'commit')
        def exec_driver_sql(self,sql):events.append('bounds')
    class Engine:
        def begin(self):return Connection()
        def dispose(self):events.append('disposed')
    def stamp(*args):pass
    monkeypatch.setenv('ACCESS_MIGRATION_DATABASE_URL','synthetic-config')
    monkeypatch.setattr(sqlalchemy,'create_engine',lambda *args,**kwargs:Engine())
    monkeypatch.setattr(context,'config',SimpleNamespace(cmd_opts=None),raising=False)
    monkeypatch.setattr(context,'is_offline_mode',lambda:False)
    monkeypatch.setattr(context,'configure',lambda **kwargs:None)
    monkeypatch.setattr(context,'get_context',lambda:SimpleNamespace(opts={'fn':stamp}))
    monkeypatch.setattr(access_baseline,'preflight',lambda c:pytest.fail('prohibited route preflight'))
    monkeypatch.setattr(context,'run_migrations',lambda:pytest.fail('prohibited route DDL'))
    with pytest.raises(access_baseline.BaselineError,match='access_use_verified_upgrade_route'):
        runpy.run_path(str(OWNER/'migrations/env.py'))
    assert events[-2:]==['rollback','disposed']


def test_configuration_and_connection_errors_are_sanitized(monkeypatch):
    import sqlalchemy
    from alembic import context
    from access_baseline import BaselineError
    def upgrade(*args):pass
    monkeypatch.setenv('ACCESS_MIGRATION_DATABASE_URL','private-secret-configuration')
    monkeypatch.setattr(context,'config',SimpleNamespace(cmd_opts=SimpleNamespace(cmd=(upgrade,))),raising=False)
    monkeypatch.setattr(context,'is_offline_mode',lambda:False)
    def connect(*args,**kwargs):raise ValueError('private-secret-configuration and sensitive SQL value')
    monkeypatch.setattr(sqlalchemy,'create_engine',connect)
    with pytest.raises(BaselineError) as error:runpy.run_path(str(OWNER/'migrations/env.py'))
    assert str(error.value)=='access_migration_failed_requires_reconciliation'
    assert error.value.__suppress_context__ is True


def test_access_owner_fixture_urls_are_validated_separately_before_network():
    from qualify_access_membership_binding import validate_access_urls
    import copy
    run={'run_id':'99b7231c-0a5b-4bdb-98e8-3329564c526a'};target={'ports':{'database':55482,'supabase_api':55481}}
    private=dict(admin_url='postgresql://postgres:synthetic@127.0.0.1:55482/postgres',api_url='http://127.0.0.1:55481')
    for group,user in [('databases','postgres'),('owner_urls','identity_migrator'),('runtime_urls','access_runtime'),('access_owner_urls','access_migrator')]:private[group]={'native':f'postgresql://{user}:synthetic@127.0.0.1:55482/postgres'}
    validate_access_urls(private,run,target)
    for changed in ('foreign.invalid','127.0.0.1:55555','identity_migrator:synthetic@127.0.0.1'):
        invalid=copy.deepcopy(private)
        invalid['access_owner_urls']['native']='postgresql://'+(changed if '@' in changed else 'access_migrator:synthetic@'+changed)+'/postgres'
        with pytest.raises(AssertionError):validate_access_urls(invalid,run,target)


def role_guard_connection(monkeypatch, *, flags=None, incoming=None, administrator_flags=None, definer=False):
    import access_baseline as baseline
    original=baseline.rows
    safe_flags=[(role,True,False,False,False,False,False) for role in ('access_migrator','access_runtime')]
    def query(connection,sql):
        if "FROM pg_roles WHERE rolname='access_capability_reader'" in sql:return []
        if sql=='SELECT session_user,current_user':return [('access_migrator','access_migrator')]
        if 'SELECT rolname,rolcanlogin' in sql and "'access_runtime'" in sql:return safe_flags if flags is None else flags
        if 'SELECT rolname,rolcanlogin' in sql and "'supabase_admin'" in sql:return administrator_flags
        if 'pg_auth_members WHERE roleid' in sql and 'access_check_reader' in sql:return []
        if 'pg_auth_members WHERE member' in sql:return []
        if 'FROM pg_auth_members m WHERE roleid' in sql:return [] if incoming is None else incoming
        if 'p.prosecdef' in sql:return [(1,)] if definer else []
        pytest.fail('guard failed to refuse before downstream catalog work')
    monkeypatch.setattr(baseline,'rows',query)
    class Connection:
        def execute(self,sql):return SimpleNamespace(scalar_one=lambda:False)
    return baseline,Connection()


@pytest.mark.parametrize('role',('access_migrator','access_runtime'))
@pytest.mark.parametrize('attribute',range(2,7))
def test_either_access_role_elevated_attribute_refuses_before_catalog(monkeypatch,role,attribute):
    flags=[list((name,True,False,False,False,False,False)) for name in ('access_migrator','access_runtime')]
    flags[0 if role=='access_migrator' else 1][attribute]=True
    baseline,connection=role_guard_connection(monkeypatch,flags=[tuple(r) for r in flags])
    with pytest.raises(baseline.BaselineError,match='access_migration_role_excess_authority'):
        baseline.verify_prerequisites(connection)


@pytest.mark.parametrize('incoming',[
    [('untrusted','untrusted',False,False,True)],
    [('postgres','postgres',False,False,True)],
    [('postgres','supabase_admin',True,False,False),('postgres','postgres',False,True,True)],
    [('postgres','supabase_admin',True,False,False),('postgres','postgres',True,False,True)],
    [('postgres','ordinary',True,False,False),('postgres','postgres',False,False,True)],
])
def test_unknown_incoming_owner_membership_refuses_without_role_changes(monkeypatch,incoming):
    baseline,connection=role_guard_connection(monkeypatch,incoming=incoming)
    with pytest.raises(baseline.BaselineError,match='access_migration_role_excess_authority'):
        baseline.verify_prerequisites(connection)


def test_bootstrap_names_require_the_actual_administrator_profiles(monkeypatch):
    baseline,connection=role_guard_connection(monkeypatch,
        incoming=[('postgres','supabase_admin',True,False,False),('postgres','postgres',False,False,True)],
        administrator_flags=[('postgres',True,False,False,False,False,False,True),('supabase_admin',True,False,False,False,False,False,True)])
    with pytest.raises(baseline.BaselineError,match='access_migration_role_excess_authority'):
        baseline.verify_prerequisites(connection)


def test_identity_definer_execution_refuses_before_local_catalog(monkeypatch):
    baseline,connection=role_guard_connection(monkeypatch,definer=True)
    with pytest.raises(baseline.BaselineError,match='access_migration_role_excess_authority'):
        baseline.verify_prerequisites(connection)


@pytest.mark.parametrize('table',('grants','alembic_version'))
@pytest.mark.parametrize('drift',('unlogged','temporary','parent','child'))
def test_nonpermanent_or_inherited_table_refuses_before_column_work(monkeypatch,table,drift):
    import access_baseline as baseline
    ledger=table=='alembic_version'
    def query(connection,sql):
        if "FROM pg_roles WHERE rolname='access_capability_reader'" in sql:return []
        if 'FROM pg_class WHERE oid=' in sql:
            return [('access_migrator','r',not ledger,not ledger,None,False,'d',{'unlogged':'u','temporary':'t'}.get(drift,'p'))]
        if 'FROM pg_inherits' in sql:return [(1,)]
        pytest.fail('unsafe table reached column work')
    monkeypatch.setattr(baseline,'rows',query)
    with pytest.raises(baseline.BaselineError,match='access_unknown_history' if ledger else 'access_catalog_mismatch'):
        baseline.verify_table(object(),table,'access_0001')


def test_qualifier_requires_the_intended_database_refusal():
    from qualify_access_membership_binding import require_database_error
    from sqlalchemy.exc import DBAPIError
    class Original(Exception):
        def __init__(self,state,constraint=None):
            self.sqlstate=state;self.diag=SimpleNamespace(constraint_name=constraint)
    def operation(state,constraint=None):
        def fail():raise DBAPIError('synthetic',None,Original(state,constraint))
        return fail
    require_database_error(operation('42501'),'42501')
    require_database_error(operation('23514','grants_membership_id_positive'),'23514','grants_membership_id_positive')
    require_database_error(operation('22003'),'22003')
    for call in [(operation('22P02'),'42501',None),(operation('23514','different'),'23514','grants_membership_id_positive')]:
        with pytest.raises(AssertionError):require_database_error(*call)


def test_clean_qualifier_refuses_preupgraded_case(monkeypatch,tmp_path):
    import qualify_access_membership_binding as qualifier
    class Connection:
        def __enter__(self):return self
        def __exit__(self,*args):pass
    class Database:
        def begin(self):return Connection()
        def dispose(self):pass
    q=qualifier.Qualification(tmp_path,{})
    monkeypatch.setattr(q,'db',lambda case:Database())
    monkeypatch.setattr(qualifier.baseline,'preflight',lambda connection:'access_0002')
    monkeypatch.setattr(q,'command',lambda *args,**kwargs:pytest.fail('preupgraded clean case migrated'))
    with pytest.raises(AssertionError,match='exactly empty'):q.clean_previous()


def test_bootstrap_witness_must_cover_unchanged_executed_sources(monkeypatch,tmp_path):
    import json
    import qualify_access_membership_binding as qualifier
    from hashlib import sha256
    monkeypatch.setattr(qualifier,'ROOT',tmp_path)
    source=tmp_path/'bootstrap.py';source.write_text('synthetic source')
    monkeypatch.setattr(qualifier,'source_paths',lambda proof:[source])
    captured={'bootstrap.py':sha256(source.read_bytes()).hexdigest()}
    logs={}
    for name in ('bootstrap.log','bootstrap_identity18.log'):
        (tmp_path/name).write_text('PASS');logs[name]=sha256(b'PASS').hexdigest()
    witness=dict(status='passed',before=captured,after=captured,steps=['bootstrap.py','bootstrap_identity18.py'],logs=logs)
    path=tmp_path/'bootstrap-source-custody.json';path.write_text(json.dumps(witness))
    qualifier.verify_preparation(tmp_path)
    source.write_text('changed source')
    with pytest.raises(AssertionError,match='bootstrap execution custody'):qualifier.verify_preparation(tmp_path)
    source.write_text('synthetic source');witness['status']='started';path.write_text(json.dumps(witness))
    with pytest.raises(AssertionError,match='bootstrap execution custody'):qualifier.verify_preparation(tmp_path)


def test_optimized_python_refuses_before_fixture_in_isolated_subprocess():
    import subprocess
    code=f"""
import sys
sys.path.insert(0,{str(OWNER/'tests')!r})
import qualify_access_membership_binding as qualifier

def fail_fixture():
    raise RuntimeError('fixture_must_not_be_reached')

qualifier.fixture=fail_fixture
sys.argv=['qualifier','--all']
try:
    qualifier.main()
except RuntimeError as error:
    if str(error) != 'access_qualification_optimized_python_prohibited':
        raise
else:
    raise RuntimeError('optimized_python_was_not_refused')
"""
    result=subprocess.run([sys.executable,'-I','-B','-O','-c',code],capture_output=True,text=True,timeout=60)
    assert result.returncode==0,result.stderr
