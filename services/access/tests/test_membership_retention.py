"""Retained membership history structural contract."""
from pathlib import Path
import importlib.util
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_identity_baseline as qualification


def revision_module():
    path=qualification.OWNER/'versions/0012_membership_retention.py'
    spec=importlib.util.spec_from_file_location('membership_retention_revision',path)
    revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
    return revision


def test_retention_migration_preserves_guard_and_limits_constraint_replacement():
    revision=revision_module();sql=revision.MEMBERSHIP_RETENTION_SQL
    assert revision.revision=='identity_0012' and revision.down_revision=='identity_0011'
    prior=(qualification.OWNER/'versions/0011_membership_binding.py').read_text()
    body=prior.split('BEGIN\n',1)[1].split('$revision_guard$;',1)[0]
    assert body in sql
    assert sql.index('identity_membership_history_retained')<sql.index('identity_membership_binding_immutable')
    assert "TG_OP IN ('DELETE', 'TRUNCATE')" in sql
    assert "CONSTRAINT = 'org_member_history_retained'" in sql
    for name in ['org_member_org_id_fkey','org_member_user_id_fkey','member_role_member_id_fkey']:
        assert name in sql
    assert sql.count('ON DELETE RESTRICT')==3
    assert 'BEFORE INSERT OR UPDATE OR DELETE ON identity.org_member' in sql
    assert 'BEFORE TRUNCATE ON identity.org_member' in sql and 'FOR EACH STATEMENT' in sql
    assert not any(word in sql for word in ['GRANT ','REVOKE ','SECURITY DEFINER','auth.users'])
    with pytest.raises(RuntimeError,match='Destructive'):revision.downgrade()


def test_retention_is_head_with_prior_history_available(monkeypatch):
    b=qualification.baseline
    assert b.MEMBERSHIP_RETENTION_REVISION=='identity_0012'
    monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.MEMBERSHIP_RETENTION_REVISION)
    seen=[];monkeypatch.setattr(b,'verify_catalog',lambda c,k:seen.append(k))
    b.verify_owned_postcondition(object(),require_head=True)
    assert seen==['membership_retention']
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.MEMBERSHIP_BINDING_REVISION)
    b.verify_owned_postcondition(object())
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):b.verify_owned_postcondition(object(),require_head=True)


@pytest.mark.parametrize('mutation',[None,'identity_baseline.py','source-pins.json','reference.json','actor-reference.json',
    'projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json',
    'target-reference.json','profile-reference.json','legacy-role-reference.json','token-hook-reference.json','membership-binding-reference.json',
    'versions/0001_baseline.py','versions/0002_actor_registry.py','versions/0003_current_account_actor.py',
    'versions/0004_current_account_organization.py','versions/0005_operator_authority.py','versions/0006_actor_command.py',
    'versions/0007_organization_targets.py','versions/0008_profile_fields.py','versions/0009_legacy_roles.py',
    'versions/0010_token_hook.py','versions/0011_membership_binding.py','versions/0012_membership_retention.py'])
def test_retention_recorder_custody_publication_and_every_prior_catalog(tmp_path,monkeypatch,mutation):
    from test_actor_command_qualification import recorder
    from test_projection_qualification import digest
    import stat
    runner,statements=recorder(tmp_path,monkeypatch,mutation)
    (tmp_path/'identity_baseline.py').write_text('MEMBERSHIP_RETENTION_REFERENCE_SHA256 = None\n')
    for name in ['command-reference.json','target-reference.json','profile-reference.json','legacy-role-reference.json','token-hook-reference.json','membership-binding-reference.json']:(tmp_path/name).write_text('{}')
    for number,name,symbol in [(7,'organization_targets','TARGET_SCHEMA_SQL'),(8,'profile_fields','PROFILE_FIELDS_SQL'),(9,'legacy_roles','LEGACY_ROLES_SQL'),(10,'token_hook','TOKEN_HOOK_SQL'),(11,'membership_binding','MEMBERSHIP_BINDING_SQL'),(12,'membership_retention','MEMBERSHIP_RETENTION_SQL')]:
        (tmp_path/f'versions/{number:04d}_{name}.py').write_text(f'{symbol} = "captured {name}"\n')
    runner.private={'owner_urls':{'membership_retention_reference':'synthetic'}}
    b=qualification.baseline
    monkeypatch.setattr(b,'trusted_membership_binding_reference',lambda:{})
    monkeypatch.setattr(b,'verify_target_roles',lambda *a,**k:None)
    monkeypatch.setattr(b,'verify_profile_privileges',lambda *a,**k:None)
    monkeypatch.setattr(b,'target_catalog_snapshot',lambda *a:{})
    monkeypatch.setattr(b,'IMPORTED_SOURCE_SHA256',digest((tmp_path/'identity_baseline.py').read_bytes()))
    helper=(tmp_path/'identity_baseline.py').read_bytes();catalogs=[]
    monkeypatch.setattr(b,'verify_catalog',lambda c,kind:catalogs.append(kind))
    deadline="SET LOCAL statement_timeout='60s'; SET LOCAL lock_timeout='5s'"
    preflights=[]
    def preflight(*args):
        assert statements[-1]==deadline
        preflights.append(len(statements));return 'clean'
    monkeypatch.setattr(b,'preflight',preflight)
    if mutation:
        with pytest.raises(AssertionError,match='membership_retention_reference_source_changed'):runner.record_membership_retention_reference()
        assert not (tmp_path/'membership-retention-reference.json').exists()
    else:
        runner.record_membership_retention_reference()
        assert (tmp_path/'identity_baseline.py').read_bytes()==helper
        assert runner.records[-1]['pin_update_required'] is True
        assert stat.S_IMODE((tmp_path/'membership-retention-reference.json').stat().st_mode)==0o600
        with pytest.raises(AssertionError,match='already_exists'):runner.record_membership_retention_reference()
    assert len(preflights)==2
    assert catalogs==['owned','actor','projection','organization','authority','command','target','profile','legacy_roles','token_hook','membership_binding']
    assert statements==[deadline,'captured baseline','captured actor','captured projection','captured organization','captured authority','captured command',
        'captured organization_targets','captured profile_fields','captured legacy_roles','captured token_hook','captured membership_binding','captured membership_retention',deadline]


def test_reference_retains_prior_trust_and_own_source(tmp_path,monkeypatch):
    import json
    from test_projection_qualification import digest
    b=qualification.baseline;calls=[]
    monkeypatch.setattr(b,'trusted_membership_binding_reference',lambda:calls.append('binding'))
    monkeypatch.setattr(b,'HERE',tmp_path)
    (tmp_path/'versions').mkdir();(tmp_path/'versions/0012_membership_retention.py').write_bytes(b'source')
    (tmp_path/'source-pins.json').write_text('{}')
    content=json.dumps({'source_pins':{},'migration_sha256':digest(b'source'),'membership_retention':{}}).encode()
    (tmp_path/'membership-retention-reference.json').write_bytes(content)
    monkeypatch.setattr(b,'MEMBERSHIP_RETENTION_REFERENCE_SHA256',digest(content))
    assert b.trusted_membership_retention_reference()=={} and calls==['binding']
    (tmp_path/'versions/0012_membership_retention.py').write_bytes(b'drift')
    with pytest.raises(b.BaselineError,match='identity_reference_unavailable'):b.trusted_membership_retention_reference()


@pytest.mark.parametrize('module,args',[('qualify_identity_baseline',['--record-membership-retention-reference']),('qualify_membership_retention',[])])
def test_optimized_execution_refused_before_fixture(module,args):
    import subprocess
    source="""import importlib,sys
sys.path.insert(0,sys.argv[1])
module=importlib.import_module(sys.argv[2])
module.fixture=lambda: (_ for _ in ()).throw(RuntimeError('fixture_reached'))
sys.argv=[module.__file__]+sys.argv[3:]
try:module.main()
except RuntimeError as error:
    if str(error) not in {'membership_retention_reference_optimized_python_prohibited','membership_retention_qualification_optimized_python_prohibited'}:raise RuntimeError('wrong_guard')
else:raise RuntimeError('missing_guard')
"""
    result=subprocess.run([sys.executable,'-I','-B','-O','-c',source,str(Path(__file__).resolve().parent),module,*args],capture_output=True,text=True,timeout=10)
    assert result.returncode==0 and result.stdout==result.stderr==''


@pytest.mark.parametrize('defect',['wrong_definition','unvalidated','deferrable','deferred','valid'])
def test_exact_canonical11_fk_precondition(defect):
    import qualify_membership_retention as retention
    rows=[[table,name,definition,True,False,False] for (table,name),definition in retention.FK_DEFINITIONS.items()]
    if defect=='wrong_definition':rows[0][2]=rows[0][2].replace('CASCADE','NO ACTION')
    elif defect=='unvalidated':rows[0][3]=False
    elif defect=='deferrable':rows[0][4]=True
    elif defect=='deferred':rows[0][5]=True
    if defect=='valid':retention.MembershipRetentionQualification.verify_constraints(rows)
    else:
        with pytest.raises(AssertionError,match='prior_fk_definition_mismatch'):retention.MembershipRetentionQualification.verify_constraints(rows)


def test_prior_execution_manifest_is_exact25_baseline11_files():
    import qualify_membership_retention as retention
    assert len(retention.PREVIOUS_FILES)==25
    assert {'versions/0011_membership_binding.py','membership-binding-reference.json'}<=retention.PREVIOUS_FILES
    assert 'versions/0012_membership_retention.py' not in retention.PREVIOUS_FILES
    assert retention.PREVIOUS_COMMIT=='e124da80b9c0a3bbd3951d4ec1f248009502ac7d'


@pytest.mark.parametrize('phase',['first_fk','late_trigger'])
@pytest.mark.parametrize('failure',['create_after_commit','body'])
def test_partial_fk_failure_fixture_restores_exact_objects(tmp_path,failure,phase):
    import qualify_membership_retention as retention
    import json,stat
    runner=retention.MembershipRetentionQualification(tmp_path,{})
    state={'created':False};commands=[]
    def sql(case,statement,values=None):
        commands.append(statement)
        if statement.startswith('SELECT '):return [('event_trigger','synthetic_membership_retention_failure')] if state['created'] else []
        if statement.startswith('CREATE FUNCTION'):
            paths=list(tmp_path.glob('membership-retention-event-restoration-required-*.json'))
            assert len(paths)==1 and json.loads(paths[0].read_text())['before']==[]
            if phase=='first_fk':assert "confdeltype='r'" in statement and "WHEN TAG IN ('ALTER TABLE')" in statement
            else:assert "tgname='org_member_history_truncate_guard'" in statement and "WHEN TAG IN ('CREATE TRIGGER')" in statement
            state['created']=True
            if failure=='create_after_commit':raise RuntimeError('synthetic_create_after_commit')
        if statement.startswith('DROP EVENT TRIGGER'):state['created']=False
        return []
    runner.admin_sql=sql
    with pytest.raises(RuntimeError,match='synthetic_'):
        with runner.failure_fixture('failure',phase):raise RuntimeError('synthetic_body')
    assert state['created'] is False
    paths=list(tmp_path.glob('membership-retention-event-restored-*.json'))
    assert len(paths)==1 and stat.S_IMODE(paths[0].stat().st_mode)==0o600


@pytest.mark.parametrize('signame',['SIGINT','SIGTERM'])
@pytest.mark.parametrize('cleanup_fails',[False,True])
def test_failure_fixture_signal_and_failed_cleanup_keep_witness(tmp_path,monkeypatch,signame,cleanup_fails):
    import qualify_membership_retention as retention
    signal=retention.signal
    originals={signal.SIGINT:object(),signal.SIGTERM:object()};handlers=dict(originals)
    monkeypatch.setattr(signal,'getsignal',lambda sig:handlers[sig])
    monkeypatch.setattr(signal,'signal',lambda sig,handler:handlers.__setitem__(sig,handler))
    runner=retention.MembershipRetentionQualification(tmp_path,{})
    state={'created':False}
    def sql(case,statement,values=None):
        if statement.startswith('SELECT '):return [('event_trigger','synthetic_membership_retention_failure')] if state['created'] else []
        if statement.startswith('CREATE FUNCTION'):state['created']=True
        if statement.startswith('DROP EVENT TRIGGER'):
            if cleanup_fails:raise RuntimeError('synthetic_cleanup_failed')
            state['created']=False
        return []
    runner.admin_sql=sql
    expected='synthetic_cleanup_failed' if cleanup_fails else 'profile_fixture_interrupted'
    with pytest.raises(RuntimeError,match=expected):
        with runner.failure_fixture('failure'):handlers[getattr(signal,signame)](getattr(signal,signame),None)
    assert handlers==originals
    assert len(list(tmp_path.glob('membership-retention-event-restoration-required-*.json')))==1
    assert len(list(tmp_path.glob('membership-retention-event-restored-*.json')))==(0 if cleanup_fails else 1)
    assert state['created'] is cleanup_fails


def test_failure_fixture_refuses_preexisting_object_without_mutation(tmp_path):
    import qualify_membership_retention as retention
    runner=retention.MembershipRetentionQualification(tmp_path,{})
    commands=[]
    def sql(case,statement,values=None):commands.append(statement);return [('event_trigger','synthetic_membership_retention_failure')]
    runner.admin_sql=sql
    with pytest.raises(AssertionError,match='already_exists'):
        with runner.failure_fixture('failure'):raise AssertionError('body_reached')
    assert len(commands)==1 and commands[0].startswith('SELECT ')
    assert not list(tmp_path.glob('membership-retention-event-*.json'))


@pytest.mark.parametrize('characterize',[False,True])
def test_auth_role_truncate_uses_existing_privilege_and_restores_admin_state(tmp_path,characterize):
    import qualify_membership_retention as retention
    from types import SimpleNamespace
    runner=retention.MembershipRetentionQualification(tmp_path,{})
    commands=[]
    class Result:
        def __init__(self,value):self.value=value
        def scalar_one(self):return self.value
        def __iter__(self):return iter(self.value)
    class Transaction:
        def __init__(self,c):self.c=c;self.role=c.role;self.empty=c.empty
        def rollback(self):self.c.role=self.role;self.c.empty=self.empty
    class Connection:
        role='supabase_admin';empty=False
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def begin(self):return Transaction(self)
        def begin_nested(self):return Transaction(self)
        def execute(self,statement,values=None):
            statement=str(statement);commands.append(statement)
            if statement.startswith('SET LOCAL ROLE'):self.role='supabase_auth_admin'
            if statement=='SELECT current_user':return Result(self.role)
            if 'has_table_privilege' in statement:return Result('identity.users' not in statement)
            if statement.startswith('TRUNCATE '):
                assert self.role=='supabase_auth_admin'
                if statement=='TRUNCATE identity.users CASCADE':
                    error=RuntimeError('synthetic_permission');error.orig=SimpleNamespace(sqlstate='42501');raise error
                if characterize:self.empty=True
                else:
                    error=RuntimeError('synthetic_retention')
                    error.orig=SimpleNamespace(sqlstate='23514',diag=SimpleNamespace(message_primary='identity_membership_history_retained',constraint_name='org_member_history_retained'))
                    raise error
            if statement.startswith('SELECT to_jsonb'):return Result([] if self.empty else [({'id':1},)])
            return Result(None)
    c=Connection()
    class Admin:
        def connect(self):return c
        def dispose(self):commands.append('dispose')
    runner.admin=lambda case:Admin()
    def state(connection):
        assert connection.role=='supabase_admin'
        return {name:[] if connection.empty else [{'id':1}] for name in ['org_member','member_role','audit_log']}
    runner.state=state;runner.sequence_state=lambda c:{'synthetic_sequence':(7,True)};runner.passed=lambda *a,**k:None
    observed=runner.auth_truncation('clean',{'member':'1','role':'1'},characterize=characterize)
    assert len(observed)==(1 if characterize else 0)
    assert c.role=='supabase_admin' and not c.empty
    assert commands[0]=="SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"
    assert commands[-1]=='dispose'
    assert sum(command.startswith('TRUNCATE ') for command in commands)==(2 if characterize else 13)
    assert not any(command.startswith(('GRANT ','REVOKE ')) for command in commands)



def retention_fixture(tmp_path):
    import qualify_membership_retention as retention
    import uuid,json
    row={key:str(uuid.uuid4()) for key in ['account','other','spare','org','other_org','spare_org']}
    row.update({key:str(number) for number,key in enumerate(['member','other_member','other_org_member','role','deleted_role'],1)})
    (tmp_path/'member-retention-fixtures.json').write_text(json.dumps({'characterization':row,'clean':row}))
    runner=retention.MembershipRetentionQualification(tmp_path,{group:{case:'' for case in retention.REQUIRED_CASES}
        for group in ['owner_urls','runtime_urls','databases']})
    return runner,row


@pytest.mark.parametrize('defect',['duplicate','numeric_duplicate','missing','malformed','valid'])
def test_role_fixture_ids_are_distinct_positive_decimal_before_db(tmp_path,defect):
    import json
    runner,row=retention_fixture(tmp_path)
    if defect=='duplicate':row['deleted_role']=row['role']
    elif defect=='numeric_duplicate':row['deleted_role']='0'+row['role']
    elif defect=='missing':row.pop('deleted_role')
    elif defect=='malformed':row['deleted_role']='not-an-id'
    (tmp_path/'member-retention-fixtures.json').write_text(json.dumps({'characterization':row,'clean':row}))
    runner.sql=lambda *a:(_ for _ in ()).throw(RuntimeError('database_reached'))
    if defect=='valid':runner.validate_targets()
    else:
        with pytest.raises(AssertionError):runner.validate_targets()


@pytest.mark.parametrize('defect',['missing','wrong_member','wrong_live_role','wrong_deleted_role','live_deleted','deleted_live','valid'])
def test_fixture_actual_roles_are_exact_live_admin_and_deleted_employee(tmp_path,defect):
    runner,v=retention_fixture(tmp_path);runner.validate_targets()
    rows=[(v['role'],v['member'],'admin',True),(v['deleted_role'],v['member'],'employee',False)]
    if defect=='missing':rows.pop()
    elif defect=='wrong_member':rows[0]=(v['role'],v['other_member'],'admin',True)
    elif defect=='wrong_live_role':rows[0]=(v['role'],v['member'],'employee',True)
    elif defect=='wrong_deleted_role':rows[1]=(v['deleted_role'],v['member'],'admin',False)
    elif defect=='live_deleted':rows[0]=(v['role'],v['member'],'admin',False)
    elif defect=='deleted_live':rows[1]=(v['deleted_role'],v['member'],'employee',True)
    calls=[]
    def sql(case,statement,values):
        calls.append(statement)
        assert values==v
        if 'FROM identity.org_member' in statement:
            return [(v['member'],v['account'],v['org']),(v['other_member'],v['other'],v['org']),(v['other_org_member'],v['account'],v['other_org'])]
        assert 'FROM identity.member_role WHERE id IN' in statement
        return rows
    runner.sql=sql
    if defect=='valid':runner.fixture_rows('clean')
    else:
        with pytest.raises(AssertionError,match='fixture_role_rows_mismatch'):runner.fixture_rows('clean')
    assert len(calls)==2


@pytest.mark.parametrize('command_failure',[False,True])
def test_conflicting_lock_is_released_before_recovery_even_on_failure(tmp_path,monkeypatch,command_failure):
    import qualify_membership_retention as retention
    commands=[]
    class Result:
        def scalar_one(self):return 'identity_0011'
    class Transaction:
        def rollback(self):commands.append('rollback')
    class Connection:
        def __enter__(self):return self
        def __exit__(self,*a):pass
        def begin(self):return Transaction()
        def execute(self,statement):commands.append(str(statement));return Result()
    class Database:
        def connect(self):return Connection()
        def dispose(self):commands.append('dispose')
    runner=retention.MembershipRetentionQualification(tmp_path,{'owner_urls':{'failure':'synthetic'}})
    monkeypatch.setattr(retention,'engine',lambda url:Database())
    times=iter([10,15]);monkeypatch.setattr(retention.time,'monotonic',lambda:next(times))
    runner.data_state=lambda case:{'data':'unchanged'}
    runner.snapshot=lambda case:{'catalog':'unchanged'}
    runner.sql=lambda *args:[('identity_0011',)]
    def command(label,case,expected):
        assert commands[-1]=='LOCK TABLE identity.org_member IN ACCESS SHARE MODE'
        assert expected=='identity_migration_failed_requires_reconciliation'
        if command_failure:raise RuntimeError('synthetic_command_failure')
    runner.command=command;passed=[];runner.passed=lambda *a,**k:passed.append(k)
    if command_failure:
        with pytest.raises(RuntimeError,match='synthetic_command_failure'):runner.conflicting_reader_lock()
        assert passed==[]
    else:
        runner.conflicting_reader_lock();assert passed[0]['elapsed_seconds']==5
    assert commands[-2:]==['rollback','dispose']


@pytest.mark.parametrize('failure',['refused','unexpected'])
def test_fk_drift_preflight_is_same_connection_and_rollback_restores(tmp_path,monkeypatch,failure):
    import qualify_membership_retention as retention
    c=None;commands=[]
    class Result:
        def scalar_one(self):return 'identity_0011'
    class Transaction:
        def rollback(self):c.changed=False;commands.append('rollback')
    class Connection:
        changed=False
        def __enter__(self):return self
        def __exit__(self,*a):pass
        def begin(self):return Transaction()
        def execute(self,statement):
            statement=str(statement);commands.append(statement)
            if statement.startswith('ALTER TABLE'):self.changed=True
            return Result()
    c=Connection()
    class Database:
        def connect(self):return c
        def dispose(self):commands.append('dispose')
    runner=retention.MembershipRetentionQualification(tmp_path,{'owner_urls':{'unknown':'synthetic'}})
    monkeypatch.setattr(retention,'engine',lambda url:Database())
    snapshot=lambda:{'constraints':['changed' if c.changed else 'old'],'functions':[]}
    monkeypatch.setattr(retention.baseline,'target_catalog_snapshot',lambda connection:snapshot())
    def preflight(connection,mode):
        assert connection is c and mode=='clean' and c.changed
        if failure=='unexpected':raise RuntimeError('synthetic_preflight_failure')
        raise retention.baseline.BaselineError('identity_catalog_mismatch:constraints')
    monkeypatch.setattr(retention.baseline,'preflight',preflight)
    runner.data_state=lambda case:{'data':'unchanged'};runner.snapshot=lambda case:snapshot()
    runner.state=lambda connection:{'data':'unchanged'};runner.passed=lambda *a,**k:None
    if failure=='unexpected':
        with pytest.raises(RuntimeError,match='synthetic_preflight_failure'):runner.fk_drift_refusal()
    else:runner.fk_drift_refusal()
    assert not c.changed and commands[-2:]==['rollback','dispose']


@pytest.mark.parametrize('sequence_changed',[False,True])
def test_restart_identity_is_admin_only_and_checks_sequence_preservation(tmp_path,sequence_changed):
    import qualify_membership_retention as retention
    commands=[];state={'sequence':7}
    class Result:
        def scalar_one(self):return 'supabase_admin'
    class Transaction:
        def rollback(self):commands.append('rollback')
    class Connection:
        def __enter__(self):return self
        def __exit__(self,*a):pass
        def begin(self):return Transaction()
        def execute(self,statement):commands.append(str(statement));return Result()
    class Admin:
        def connect(self):return Connection()
        def dispose(self):commands.append('dispose')
    runner=retention.MembershipRetentionQualification(tmp_path,{})
    runner.admin=lambda case:Admin();runner.state=lambda c:{'all_rows':'unchanged'}
    runner.sequence_state=lambda c:{'sequence':(state['sequence'],True)}
    def reject(c,statement,v):
        commands.append(statement)
        assert 'RESTART IDENTITY CASCADE' in statement and v=={}
        if sequence_changed:state['sequence']=1
    runner.retention_reject=reject;runner.passed=lambda *a,**k:None
    if sequence_changed:
        with pytest.raises(AssertionError):runner.admin_restart_truncation('clean')
    else:runner.admin_restart_truncation('clean')
    assert commands[-2:]==['rollback','dispose']
    assert not any(command.startswith(('SET LOCAL ROLE','GRANT ','REVOKE ')) for command in commands)
    assert sum(command.startswith('TRUNCATE ') for command in commands)==(1 if sequence_changed else 2)
