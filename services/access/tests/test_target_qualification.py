"""Selected-organization target head custody and restricted role preparation."""
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_identity_baseline as qualification


def test_target_head_is_required_and_prior_command_remains_supported(monkeypatch):
    b=qualification.baseline
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.TARGET_REVISION)
    monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
    seen=[]
    monkeypatch.setattr(b,'verify_catalog',lambda c,k:seen.append(k))
    b.verify_owned_postcondition(object())
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):
        b.verify_owned_postcondition(object(),require_head=True)
    assert seen==['target']
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.COMMAND_REVISION)
    b.verify_owned_postcondition(object())
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):
        b.verify_owned_postcondition(object(),require_head=True)


@pytest.mark.parametrize('mutation',[None,'identity_baseline.py','source-pins.json','reference.json','actor-reference.json','projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json','versions/0001_baseline.py','versions/0002_actor_registry.py','versions/0003_current_account_actor.py','versions/0004_current_account_organization.py','versions/0005_operator_authority.py','versions/0006_actor_command.py','versions/0007_organization_targets.py'])
def test_target_recorder_binds_full_source_chain_without_pinning(tmp_path,monkeypatch,mutation):
    from test_actor_command_qualification import recorder
    from test_projection_qualification import digest
    import stat
    runner,statements=recorder(tmp_path,monkeypatch,mutation)
    (tmp_path/'identity_baseline.py').write_text('TARGET_REFERENCE_SHA256 = None\n')
    (tmp_path/'command-reference.json').write_text('{}')
    (tmp_path/'versions/0007_organization_targets.py').write_text('TARGET_SCHEMA_SQL = "captured target"\n')
    runner.private={'owner_urls':{'target_reference':'synthetic'}}
    b=qualification.baseline
    monkeypatch.setattr(b,'trusted_command_reference',lambda:{})
    monkeypatch.setattr(b,'verify_target_roles',lambda *a,**k:None)
    monkeypatch.setattr(b,'target_catalog_snapshot',lambda *a:{})
    monkeypatch.setattr(b,'IMPORTED_SOURCE_SHA256',digest((tmp_path/'identity_baseline.py').read_bytes()))
    helper=(tmp_path/'identity_baseline.py').read_bytes()
    if mutation:
        with pytest.raises(AssertionError,match='target_reference_source_changed'):runner.record_target_reference()
        assert not (tmp_path/'target-reference.json').exists()
    else:
        runner.record_target_reference()
        assert (tmp_path/'identity_baseline.py').read_bytes()==helper
        assert runner.records[-1]['pin_update_required'] is True
        assert stat.S_IMODE((tmp_path/'target-reference.json').stat().st_mode)==0o600
        with pytest.raises(AssertionError,match='target_reference_already_exists'):runner.record_target_reference()
    assert statements==['captured baseline','captured actor','captured projection','captured organization','captured authority','captured command','captured target']


@pytest.mark.parametrize('role',qualification.baseline.TARGET_ROLES)
@pytest.mark.parametrize('defect',['missing','unsafe','membership','dependencies','effective'])
def test_target_roles_refuse_unsafe_preparation(role,defect):
    b=qualification.baseline
    class Result:
        def __init__(self,rows=(),scalar=False):self.rows=rows;self.scalar=scalar
        def all(self):return self.rows
        def scalar_one(self):return self.scalar
    class Connection:
        def execute(self,sql,params=None):
            sql=str(sql)
            for candidate,queries in b.TARGET_ROLE_QUERIES.items():
                bad=candidate==role
                if sql==queries['target_role']:
                    return Result([] if bad and defect=='missing' else [(candidate,False,False,False,False,bad and defect=='unsafe',False,False)])
                if sql==queries['target_memberships']:
                    expected=[(b.TARGET_OWNER,'identity_migrator',False,'false','true')] if candidate==b.TARGET_OWNER else []
                    return Result([('unexpected',)] if bad and defect=='membership' else expected)
                if sql==queries['target_dependencies']:
                    return Result([('unexpected',)] if bad and defect=='dependencies' else [])
            assert 'has_database_privilege' in sql and 'has_any_column_privilege' in sql
            return Result(scalar=params['role']==role and defect=='effective')
    with pytest.raises(b.BaselineError,match='identity_target_role_'):b.verify_target_roles(Connection(),staged=True)


def test_target_reference_rechecks_previous_chain_and_own_source(tmp_path,monkeypatch):
    import json
    from test_projection_qualification import digest
    b=qualification.baseline
    calls=[]
    monkeypatch.setattr(b,'trusted_command_reference',lambda:calls.append('command'))
    monkeypatch.setattr(b,'HERE',tmp_path)
    (tmp_path/'versions').mkdir()
    (tmp_path/'versions/0007_organization_targets.py').write_bytes(b'source')
    (tmp_path/'source-pins.json').write_text('{}')
    reference={'source_pins':{},'migration_sha256':digest(b'source'),'target':{}}
    content=json.dumps(reference).encode();(tmp_path/'target-reference.json').write_bytes(content)
    monkeypatch.setattr(b,'TARGET_REFERENCE_SHA256',digest(content))
    assert b.trusted_target_reference()=={} and calls==['command']
    (tmp_path/'versions/0007_organization_targets.py').write_bytes(b'drift')
    with pytest.raises(b.BaselineError,match='identity_reference_unavailable'):b.trusted_target_reference()


def test_role_preparation_refuses_non_superuser_before_creating_roles():
    # PostgreSQL16+ CREATEROLE implicitly grants creator membership; preparation
    # therefore requires true superuser, not merely the ability to CREATE ROLE.
    source=(qualification.OWNER.parent/'tools/prepare_identity_target_roles.sql').read_text()
    guard=source.index("MESSAGE='identity_target_preparation_admin_required'")
    assert source.index('SELECT rolsuper FROM pg_roles WHERE rolname=current_user') < guard
    assert guard < source.index('CREATE ROLE')


@pytest.mark.parametrize('entry,code',[
    ('targets.main()', 'target_qualification_optimized_python_prohibited'),
    ('qualification.Qualification.record_target_reference(object())', 'target_reference_optimized_python_prohibited')])
def test_optimized_python_refuses_before_fixture_connection_or_publication(entry,code):
    import subprocess
    source="""
import sys
sys.path.insert(0,sys.argv[1])
import qualify_identity_baseline as qualification
import qualify_organization_targets as targets
def forbidden(*args,**kwargs):
    raise RuntimeError('fixture_or_connection_reached')
targets.fixture=forbidden
qualification.engine=forbidden
try:
    exec(sys.argv[2])
except RuntimeError as error:
    if str(error)!=sys.argv[3]:
        raise SystemExit(2)
else:
    raise SystemExit(3)
print('optimized_refusal_before_effects')
"""
    result=subprocess.run([sys.executable,'-I','-B','-O','-c',source,str(Path(__file__).resolve().parent),entry,code],capture_output=True,text=True,timeout=10)
    assert result.returncode==0 and result.stdout=='optimized_refusal_before_effects\n' and result.stderr==''


def test_actual_recorder_cli_rejects_optimized_python_before_fixture():
    import subprocess
    import os
    environment=dict(os.environ)
    environment.pop('IDENTITY_QUALIFICATION_DIR',None)
    result=subprocess.run([sys.executable,'-I','-B','-O',str(Path(qualification.__file__)), '--record-target-reference'],env=environment,capture_output=True,text=True,timeout=10)
    assert result.returncode==1
    assert result.stderr=='identity_qualification_failed:RuntimeError\n'
    assert result.stdout==''


@pytest.mark.parametrize('failure',['after_committed_grant','body'])
def test_fixture_grant_exception_restores_exact_acl_and_private_witnesses(tmp_path,monkeypatch,failure):
    import qualify_organization_targets as targets
    from contextlib import contextmanager
    import signal
    import stat
    state={'granted':False}
    before=[('candidate','owner,reader'),('point','owner,reader,setup,command')]
    class Connection:
        def execute(self,statement):
            statement=str(statement)
            if statement.startswith('GRANT EXECUTE'):state['pending']=True
            if statement.startswith('REVOKE EXECUTE'):state['pending']=False
    class Database:
        @contextmanager
        def begin(self):
            state.pop('pending',None)
            yield Connection()
            if 'pending' in state:
                state['granted']=state['pending']
                if state['pending'] and failure=='after_committed_grant':
                    raise RuntimeError('synthetic_after_commit')
        def dispose(self):pass
    runner=targets.TargetQualification(tmp_path,{'owner_urls':{'clean':'unused'}})
    def sql(case,statement,values=None):
        if statement==targets.ACL_SQL:
            return [('candidate','temporary'),('point','temporary')] if state['granted'] else before
        return [(False,False)]
    runner.sql=sql
    monkeypatch.setattr(targets,'engine',lambda url:Database())
    handlers={sig:signal.getsignal(sig) for sig in [signal.SIGINT,signal.SIGTERM]}
    with pytest.raises(RuntimeError,match='synthetic_'):
        with runner.fixture_execution('clean'):
            raise RuntimeError('synthetic_body')
    assert state['granted'] is False
    assert runner.sql('clean',targets.ACL_SQL)==before
    assert all(signal.getsignal(sig)==handler for sig,handler in handlers.items())
    required=list(tmp_path.glob('target-acl-restoration-required-*.json'))
    restored=list(tmp_path.glob('target-acl-restored-*.json'))
    assert len(required)==len(restored)==1
    assert all(stat.S_IMODE(path.stat().st_mode)==0o600 for path in required+restored)


def test_recipient_membership_fixture_restores_when_refusal_check_fails(tmp_path,monkeypatch):
    import qualify_organization_targets as targets
    from contextlib import contextmanager
    statements=[]
    class Admin:
        @contextmanager
        def begin(self):yield self
        def execute(self,statement):statements.append(str(statement))
        def dispose(self):pass
    runner=targets.TargetQualification(tmp_path,{})
    runner.admin=lambda case:Admin()
    runner.data_state=lambda case:{}
    def command(label,case,**kwargs):
        if label=='target-recipient-member':raise RuntimeError('synthetic_refusal_check_failure')
    runner.command=command
    with pytest.raises(RuntimeError,match='synthetic_refusal_check_failure'):runner.recipient_unsafe()
    assert statements==['GRANT access_target_reader TO access_runtime','REVOKE access_target_reader FROM access_runtime']
