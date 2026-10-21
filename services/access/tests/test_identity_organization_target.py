"""Focused contract checks for private account-free organization verification."""
from pathlib import Path
import importlib.util
import subprocess
import sys
import pytest

HERE=Path(__file__).resolve().parent


def migration():
    path=HERE.parent/'identity-migrations/versions/0019_organization_target.py'
    spec=importlib.util.spec_from_file_location('organization_target_migration',path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


def test_exact_migration_boundary_and_transactional_execution(monkeypatch):
    value=migration();seen=[]
    assert (value.revision,value.down_revision)==('identity_0019','identity_0018')
    class Connection:
        def exec_driver_sql(self,sql,execution_options):seen.append((sql,execution_options))
    monkeypatch.setattr(value.op,'get_bind',lambda:Connection())
    value.upgrade()
    assert seen==[(value.ORGANIZATION_TARGET_SQL,{'no_parameters':True})]
    with pytest.raises(RuntimeError,match='Destructive rollback'):value.downgrade()


def test_account_free_projection_does_not_expand_tables_roles_or_policies():
    sql=migration().ORGANIZATION_TARGET_SQL
    assert 'RETURNS TABLE (org_id uuid)' in sql
    assert 'STABLE SECURITY DEFINER SET search_path = pg_catalog, pg_temp' in sql
    assert 'FROM identity.org AS organization' in sql
    for forbidden in ('identity.users','identity.org_member','identity.actor','CREATE ROLE','CREATE POLICY','GRANT SELECT','ALTER DEFAULT PRIVILEGES'):
        assert forbidden not in sql
    assert 'TO access_command_owner;' in sql
    assert 'OWNER TO identity_target_projection_owner;' in sql
    assert 'aclexplode(routine.proacl)' in sql
    assert "IS DISTINCT FROM 'setup'" in sql
    assert "nullif(current_setting('app.account_id', true), '') IS NOT NULL" in sql
    assert sql.index('IS NOT TRUE') < sql.index('selected_org::uuid')


@pytest.mark.parametrize('file,args',[
    ('qualify_identity_organization_target.py',['--all']),
    ('qualify_identity_organization_target.py',['--verify-retained']),
    ('qualify_identity_baseline.py',['--record-organization-target-reference']),
])
def test_optimized_qualification_refuses_before_fixture_io(file,args):
    result=subprocess.run([sys.executable,'-O','-I','-B',str(HERE/file),*args],env={'PATH':'/usr/bin:/bin'},capture_output=True,text=True)
    assert result.returncode!=0 and 'optimized_python_prohibited' in result.stderr
    assert 'IDENTITY_QUALIFICATION_DIR' not in result.stderr


def test_unexpected_qualification_failure_never_renders_diagnostics():
    code=f"""import sys
sys.path.insert(0,{str(HERE)!r})
import qualify_identity_organization_target as q
def fail():raise RuntimeError('synthetic-sensitive-sql-and-credential')
q.main=fail
q.run()
"""
    result=subprocess.run([sys.executable,'-I','-B','-c',code],env={'PATH':'/usr/bin:/bin'},capture_output=True,text=True)
    assert result.returncode==1
    assert result.stdout==''
    assert result.stderr=='organization_target_qualification_failed:RuntimeError\n'


def test_head19_dispatch_requires_current_head_and_retains18(monkeypatch):
    import qualify_identity_baseline as q
    b=q.baseline;seen=[]
    monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
    monkeypatch.setattr(b,'verify_catalog',lambda c,k:seen.append(k))
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.ACCOUNT_ACTOR_ENSURE_REVISION)
    b.verify_owned_postcondition(object())
    assert seen==['account_actor_ensure']
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):
        b.verify_owned_postcondition(object(),require_head=True)
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.ORGANIZATION_TARGET_REVISION)
    b.verify_owned_postcondition(object(),require_head=True)
    assert seen[-1]=='organization_target'


@pytest.mark.parametrize('defect',[None,'migration','missing_reference','modified_reference','source_pins'])
def test_organization_reference_retains18_trust_and_refuses_drift(tmp_path,monkeypatch,defect):
    import json
    from hashlib import sha256
    import qualify_identity_baseline as q
    b=q.baseline;calls=[]
    monkeypatch.setattr(b,'trusted_account_actor_ensure_reference',lambda:calls.append('head18'))
    monkeypatch.setattr(b,'HERE',tmp_path)
    (tmp_path/'versions').mkdir()
    source=tmp_path/'versions/0019_organization_target.py';source.write_bytes(b'captured migration')
    (tmp_path/'source-pins.json').write_text('{}')
    content=json.dumps({'source_pins':{},'migration_sha256':sha256(source.read_bytes()).hexdigest(),'organization_target':{}}).encode()
    path=tmp_path/'organization-target-reference.json';path.write_bytes(content)
    monkeypatch.setattr(b,'ORGANIZATION_TARGET_REFERENCE_SHA256',sha256(content).hexdigest())
    if defect=='migration':source.write_bytes(b'drift')
    elif defect=='missing_reference':path.unlink()
    elif defect=='modified_reference':path.write_bytes(content+b' ')
    elif defect=='source_pins':(tmp_path/'source-pins.json').write_text('{"changed":"pin"}')
    if defect:
        with pytest.raises(b.BaselineError,match='identity_reference_unavailable'):b.trusted_organization_target_reference()
    else:assert b.trusted_organization_target_reference()=={}
    assert calls==['head18']


def test_source_custody_binds_fixture_validators_and_private_bootstrap_inputs(tmp_path,monkeypatch):
    import json
    import qualify_identity_organization_target as q
    proof=tmp_path/'proof';proof.mkdir()
    prior=tmp_path/'account-ensure-j9ial0p1';prior.mkdir()
    (prior/'run.json').write_text(json.dumps({'target':'platform/deployment/environments/kdg-local.json','run_id':'synthetic-run'}))
    monkeypatch.setattr(q,'ROOT',Path('/'))
    monkeypatch.setattr(q,'OWNER',tmp_path/'identity-owner')
    monkeypatch.setattr(q,'previous_sources',lambda p:(tmp_path,{}))
    seen=[]
    monkeypatch.setattr(q,'digest',lambda p:seen.append(p) or 'synthetic-digest')
    q.source_snapshot(proof)
    assert {proof/'bootstrap.py',proof/'bootstrap_run.py',proof/'auth-helper-definitions.json',prior/'credentials.json',prior/'run.json',tmp_path/'org-storage-reviewed-20261021/credentials.json',Path('/platform/deployment/dev.py'),Path('/platform/deployment/native_cli.py'),Path('/platform/deployment/schema/development-target-v1.json'),Path('/platform/deployment/.local/kdg/synthetic-run/supabase/config.toml')} <= set(seen)


def test_retained_inspection_refuses_changed_external_consumer_state(tmp_path,monkeypatch):
    import json
    import qualify_identity_organization_target as q
    runner=object.__new__(q.Qualification);runner.proof=tmp_path
    (tmp_path/'organization-target-source.json').write_text('{}')
    retained={case:{} for case in q.CASES};retained['external_previous']='known-rows-and-fks'
    (tmp_path/'organization-target-retained.json').write_text(json.dumps(retained))
    monkeypatch.setattr(q,'source_snapshot',lambda proof:{})
    monkeypatch.setattr(runner,'check',lambda case:None)
    monkeypatch.setattr(runner,'data_state',lambda case:{})
    monkeypatch.setattr(runner,'external_state',lambda case:'changed-rows-or-fks')
    with pytest.raises(AssertionError,match='retained_external_rows_or_fks_changed'):runner.verify_retained()


@pytest.mark.parametrize('statement,routine',[
    ('ALTER FUNCTION identity.organization_target(uuid) VOLATILE',True),
    ('ALTER FUNCTION identity.organization_target(uuid) STABLE',True),
    ('GRANT EXECUTE ON FUNCTION identity.organization_target(uuid) TO access_runtime',True),
    ('ALTER TABLE identity.org DISABLE ROW LEVEL SECURITY',False),
])
def test_synthetic_drift_uses_actual_owner_then_restores_migrator(statement,routine):
    import qualify_identity_organization_target as q
    runner=object.__new__(q.Qualification)
    seen=[]
    class Result:
        def __init__(self,value):self.value=value
        def one(self):return self.value
        def scalar_one(self):return self.value
    class Connection:
        role='identity_migrator'
        def exec_driver_sql(self,sql):
            if sql=='SELECT session_user,current_user':return Result(('identity_migrator',self.role))
            if sql=='SELECT current_user':return Result(self.role)
            if sql=='SET LOCAL ROLE identity_target_projection_owner':self.role='identity_target_projection_owner'
            elif sql=='RESET ROLE':self.role='identity_migrator'
            else:seen.append((sql,self.role))
    c=Connection()
    runner.drift_mutation(c,statement)
    assert seen==[(statement,'identity_target_projection_owner' if routine else 'identity_migrator')]
    assert c.role=='identity_migrator'
