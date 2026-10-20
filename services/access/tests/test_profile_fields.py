"""Column-hardening custody; live role/RLS behavior is separately qualified."""
from pathlib import Path
import importlib.util
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_identity_baseline as qualification


def test_profile_head_and_prior_target_supported(monkeypatch):
    b=qualification.baseline
    assert b.PROFILE_REVISION=='identity_0008'
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.PROFILE_REVISION)
    monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
    seen=[];monkeypatch.setattr(b,'verify_catalog',lambda c,k:seen.append(k))
    b.verify_owned_postcondition(object(),require_head=True)
    assert seen==['profile']
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.TARGET_REVISION)
    b.verify_owned_postcondition(object())
    assert seen==['profile','target']
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):
        b.verify_owned_postcondition(object(),require_head=True)


def test_profile_revision_changes_only_authenticated_column_writes():
    spec=importlib.util.spec_from_file_location('profile_revision',qualification.OWNER/'versions/0008_profile_fields.py')
    revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
    assert revision.revision=='identity_0008' and revision.down_revision=='identity_0007'
    sql=revision.PROFILE_FIELDS_SQL
    assert 'REVOKE INSERT, UPDATE ON identity.users FROM authenticated' in sql
    assert 'REVOKE INSERT (%s), UPDATE (%s)' in sql
    assert 'GRANT INSERT (id, username) ON identity.users TO authenticated' in sql
    assert 'GRANT UPDATE (username, deleted_at) ON identity.users TO authenticated' in sql
    assert not any(word in sql for word in ('CREATE POLICY','ALTER TABLE','CREATE FUNCTION','GRANT SELECT','service_role','auth.users'))
    with pytest.raises(RuntimeError,match='Destructive'):revision.downgrade()


@pytest.mark.parametrize('defect',['table','protected','missing'])
def test_effective_profile_acl_refuses_public_inherited_and_missing_privileges(defect):
    b=qualification.baseline
    class Result:
        def scalar_one(self):return defect=='table'
        def all(self):
            rows=[(column,permission,column in allowed) for permission,allowed in [('INSERT',{'id','username'}),('UPDATE',{'username','deleted_at'})] for column in ['id','username','deleted_at','is_platform_admin']]
            if defect=='protected':rows[-1]=('is_platform_admin','UPDATE',True)
            if defect=='missing':rows[0]=('id','INSERT',False)
            return rows
    class Connection:
        def execute(self,*args,**kwargs):return Result()
    with pytest.raises(b.BaselineError,match='identity_profile_column_privileges_mismatch'):
        b.verify_profile_privileges(Connection())


def test_profile_recorder_cli_rejects_optimized_before_fixture():
    import subprocess,os
    environment=dict(os.environ);environment.pop('IDENTITY_QUALIFICATION_DIR',None)
    result=subprocess.run([sys.executable,'-I','-B','-O',qualification.__file__,'--record-profile-reference'],env=environment,capture_output=True,text=True,timeout=10)
    assert result.returncode==1 and result.stdout==''
    assert result.stderr=='identity_qualification_failed:RuntimeError\n'


@pytest.mark.parametrize('mutation',[None,'identity_baseline.py','source-pins.json','reference.json','actor-reference.json',
    'projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json','target-reference.json',
    'versions/0001_baseline.py','versions/0002_actor_registry.py','versions/0003_current_account_actor.py',
    'versions/0004_current_account_organization.py','versions/0005_operator_authority.py','versions/0006_actor_command.py',
    'versions/0007_organization_targets.py','versions/0008_profile_fields.py'])
def test_profile_recorder_binds_all_sources_and_exclusive_publication_without_pinning(tmp_path,monkeypatch,mutation):
    from test_actor_command_qualification import recorder
    from test_projection_qualification import digest
    import stat
    runner,statements=recorder(tmp_path,monkeypatch,mutation)
    (tmp_path/'identity_baseline.py').write_text('PROFILE_REFERENCE_SHA256 = None\n')
    (tmp_path/'command-reference.json').write_text('{}')
    (tmp_path/'target-reference.json').write_text('{}')
    (tmp_path/'versions/0007_organization_targets.py').write_text('TARGET_SCHEMA_SQL = "captured target"\n')
    (tmp_path/'versions/0008_profile_fields.py').write_text('PROFILE_FIELDS_SQL = "captured profile"\n')
    runner.private={'owner_urls':{'profile_reference':'synthetic'}}
    b=qualification.baseline
    monkeypatch.setattr(b,'trusted_target_reference',lambda:{})
    monkeypatch.setattr(b,'verify_target_roles',lambda *a,**k:None)
    monkeypatch.setattr(b,'verify_profile_privileges',lambda *a,**k:None)
    monkeypatch.setattr(b,'target_catalog_snapshot',lambda *a:{})
    monkeypatch.setattr(b,'IMPORTED_SOURCE_SHA256',digest((tmp_path/'identity_baseline.py').read_bytes()))
    helper=(tmp_path/'identity_baseline.py').read_bytes()
    if mutation:
        with pytest.raises(AssertionError,match='profile_reference_source_changed'):runner.record_profile_reference()
        assert not (tmp_path/'profile-reference.json').exists()
    else:
        runner.record_profile_reference()
        assert (tmp_path/'identity_baseline.py').read_bytes()==helper
        assert runner.records[-1]['pin_update_required'] is True
        assert stat.S_IMODE((tmp_path/'profile-reference.json').stat().st_mode)==0o600
        with pytest.raises(AssertionError,match='profile_reference_already_exists'):runner.record_profile_reference()
    assert statements==['captured baseline','captured actor','captured projection','captured organization','captured authority','captured command','captured target','captured profile']


def test_profile_reference_rechecks_historical_chain_and_own_source(tmp_path,monkeypatch):
    import json
    from test_projection_qualification import digest
    b=qualification.baseline;calls=[]
    monkeypatch.setattr(b,'trusted_target_reference',lambda:calls.append('target'))
    monkeypatch.setattr(b,'HERE',tmp_path)
    (tmp_path/'versions').mkdir();(tmp_path/'versions/0008_profile_fields.py').write_bytes(b'source')
    (tmp_path/'source-pins.json').write_text('{}')
    reference={'source_pins':{},'migration_sha256':digest(b'source'),'profile':{}}
    content=json.dumps(reference).encode();(tmp_path/'profile-reference.json').write_bytes(content)
    monkeypatch.setattr(b,'PROFILE_REFERENCE_SHA256',digest(content))
    assert b.trusted_profile_reference()=={} and calls==['target']
    (tmp_path/'versions/0008_profile_fields.py').write_bytes(b'drift')
    with pytest.raises(b.BaselineError,match='identity_reference_unavailable'):b.trusted_profile_reference()


def test_profile_optimized_qualifier_refuses_before_fixture():
    import subprocess
    source="""import sys
sys.path.insert(0,sys.argv[1])
import qualify_profile_fields as profile
profile.fixture=lambda: (_ for _ in ()).throw(RuntimeError('fixture_reached'))
try:profile.main()
except RuntimeError as error:
    if str(error)!='profile_qualification_optimized_python_prohibited':raise RuntimeError('wrong_guard')
else:raise RuntimeError('missing_guard')
"""
    result=subprocess.run([sys.executable,'-I','-B','-O','-c',source,str(Path(__file__).resolve().parent)],capture_output=True,text=True,timeout=10)
    assert result.returncode==0 and result.stdout==result.stderr==''


@pytest.mark.parametrize('failure',['after_grant_commit','body'])
def test_temporary_set_only_edges_restore_exactly_on_exception(tmp_path,monkeypatch,failure):
    import qualify_profile_fields as profile
    from contextlib import contextmanager
    import stat
    state={'granted':False}
    class Result:
        def __iter__(self):
            return iter([(role,'access_runtime','supabase_admin',False,'false','true') for role in ['authenticated','service_role']] if state['granted'] else [])
    class Admin:
        @contextmanager
        def begin(self):
            state.pop('pending',None);yield self
            if 'pending' in state:
                state['granted']=state['pending']
                if state['pending'] and failure=='after_grant_commit':raise RuntimeError('synthetic_after_commit')
        def execute(self,statement):
            statement=str(statement)
            if statement.startswith('GRANT '):state['pending']=True
            if statement.startswith('REVOKE '):state['pending']=False
            return Result()
        def dispose(self):pass
    runner=profile.ProfileQualification(tmp_path,{})
    runner.admin=lambda case:Admin()
    with pytest.raises(RuntimeError,match='synthetic_'):
        with runner.fixture_execution('clean'):raise RuntimeError('synthetic_body')
    assert state['granted'] is False
    required=list(tmp_path.glob('profile-role-restoration-required-*.json'))
    restored=list(tmp_path.glob('profile-role-restored-*.json'))
    assert len(required)==len(restored)==1
    assert all(stat.S_IMODE(path.stat().st_mode)==0o600 for path in required+restored)


def test_denial_proof_refuses_duplicate_key_as_substitute_for_column_or_rls_denial(tmp_path):
    import qualify_profile_fields as profile
    class Savepoint:
        rolled_back=False
        def rollback(self):self.rolled_back=True
    class Error(Exception):
        class orig:sqlstate='23505'
    class Connection:
        savepoint=Savepoint()
        def begin_nested(self):return self.savepoint
        def execute(self,*args):raise Error()
    connection=Connection()
    with pytest.raises(AssertionError):
        profile.ProfileQualification(tmp_path,{}).denied(connection,'synthetic',{})
    assert connection.savepoint.rolled_back


def test_effective_profile_acl_accepts_only_exact_supported_columns():
    b=qualification.baseline
    class Result:
        def scalar_one(self):return False
        def all(self):return [(column,permission,column in allowed) for permission,allowed in [('INSERT',{'id','username'}),('UPDATE',{'username','deleted_at'})]
            for column in ['id','username','deleted_at','actor_key','is_system','is_platform_admin','created_by','created_at','updated_by','updated_at']]
    class Connection:
        def execute(self,*args,**kwargs):return Result()
    b.verify_profile_privileges(Connection())


def test_independent_profile_reference_changes_only_acl_catalog_categories():
    b=qualification.baseline
    prior=b.trusted_target_reference();current=b.trusted_profile_reference()
    assert prior.keys()==current.keys()
    assert {category for category in prior if prior[category]!=current[category]}=={
        'relations','columns','effective_tables','effective_columns'}


@pytest.mark.parametrize('grant',[
    'GRANT UPDATE (is_system) ON identity.users TO PUBLIC',
    'GRANT INSERT ON identity.users TO authenticated'])
@pytest.mark.parametrize('failure',['grant_after_commit','snapshot'])
def test_acl_fixture_restores_before_snapshot_or_grant_exception(tmp_path,grant,failure):
    import qualify_profile_fields as profile
    import json,stat
    runner=profile.ProfileQualification(tmp_path,{})
    before=[('id','authenticated=a/identity_migrator'),('table','original')]
    state={'granted':False};commands=[]
    revoke='REVOKE INSERT ON identity.users FROM authenticated' if 'INSERT' in grant else 'REVOKE UPDATE (is_system) ON identity.users FROM PUBLIC'
    restore='GRANT INSERT (id, username) ON identity.users TO authenticated' if 'INSERT' in grant else None
    def sql(case,statement,values=None):
        commands.append(statement)
        if statement==profile.PROFILE_ACL_SQL:return [('table','changed')] if state['granted'] else before
        if statement==grant:
            # Recovery metadata must already be durable before the first write.
            witnesses=list(tmp_path.glob('profile-acl-restoration-required-*.json'))
            assert len(witnesses)==1 and json.loads(witnesses[0].read_text())['before']==[list(r) for r in before]
            state['granted']=True
            if failure=='grant_after_commit':raise RuntimeError('synthetic_grant_after_commit')
        if statement==revoke:state['granted']=False
        return []
    runner.sql=sql
    with pytest.raises(RuntimeError,match='synthetic_'):
        with runner.acl_fixture('unsafe',grant,revoke,restore):
            raise RuntimeError('synthetic_snapshot')
    assert state['granted'] is False and revoke in commands
    if restore:assert restore in commands
    witnesses=list(tmp_path.glob('profile-acl-restored-*.json'))
    assert len(witnesses)==1 and stat.S_IMODE(witnesses[0].stat().st_mode)==0o600


@pytest.mark.parametrize('failure',['create_after_commit','snapshot'])
def test_event_fixture_preserves_receipts_and_restores_on_exception(tmp_path,failure):
    import qualify_profile_fields as profile
    import json
    runner=profile.ProfileQualification(tmp_path,{})
    state={'created':False};commands=[]
    def sql(case,statement,values=None):
        commands.append(statement)
        if statement.startswith('SELECT '):return [('event_trigger','synthetic_profile_failure')] if state['created'] else []
        if statement.startswith('CREATE FUNCTION'):
            witnesses=list(tmp_path.glob('profile-event-restoration-required-*.json'))
            assert len(witnesses)==1 and json.loads(witnesses[0].read_text())['before']==[]
            state['created']=True
            if failure=='create_after_commit':raise RuntimeError('synthetic_create_after_commit')
        if statement.startswith('DROP EVENT TRIGGER'):state['created']=False
        return []
    runner.admin_sql=sql
    with pytest.raises(RuntimeError,match='synthetic_'):
        with runner.failure_fixture('failure'):raise RuntimeError('synthetic_snapshot')
    assert state['created'] is False
    assert len(list(tmp_path.glob('profile-event-restored-*.json')))==1


def test_event_fixture_refuses_existing_objects_without_mutating(tmp_path):
    import qualify_profile_fields as profile
    runner=profile.ProfileQualification(tmp_path,{})
    commands=[]
    def sql(case,statement,values=None):commands.append(statement);return [('event_trigger','synthetic_profile_failure')]
    runner.admin_sql=sql
    with pytest.raises(AssertionError,match='already_exists'):
        with runner.failure_fixture('failure'):raise RuntimeError('body_reached')
    assert len(commands)==1 and commands[0].startswith('SELECT ')
    assert not list(tmp_path.glob('profile-event-*.json'))


@pytest.mark.parametrize('statement',['GRANT INSERT ON identity.users TO authenticated',
    'REVOKE UPDATE (is_system) ON identity.users FROM PUBLIC',
    'CREATE EVENT TRIGGER synthetic_profile_failure', 'DROP EVENT TRIGGER synthetic_profile_failure'])
def test_fixture_sql_always_applies_deadlines_and_disposes(tmp_path,statement):
    import qualify_profile_fields as profile
    from contextlib import contextmanager
    events=[]
    class Result:returns_rows=False
    class Database:
        @contextmanager
        def begin(self):yield self
        def execute(self,query,values=None):events.append(str(query));return Result()
        def dispose(self):events.append('dispose')
    profile.ProfileQualification(tmp_path,{})._bounded_sql(Database(),statement)
    assert events==["SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'",statement,'dispose']
