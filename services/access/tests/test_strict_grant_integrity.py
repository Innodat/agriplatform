"""Strict organization grant storage has no legacy permission exemption."""
import importlib.util
from pathlib import Path
import sys
from unittest.mock import patch
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'migrations'))
import access_baseline as baseline


def test_exact_twelve_retains_all_historical_versions():
    assert baseline.HEAD=='access_0015'
    for i in range(1,13):assert baseline.validate_revision([f'access_{i:04}'])==f'access_{i:04}'
    for value in ([],['access_9999'],['access_0011','access_0012']):
        with pytest.raises(baseline.BaselineError):baseline.validate_revision(value)


def test_strict_migration_is_direct_validated_ddl_without_adoption():
    spec=importlib.util.spec_from_file_location('_strict_grants',ROOT/'migrations/versions/0012_strict_grant_integrity.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert (module.revision,module.down_revision)==('access_0012','access_0011')
    with patch.object(module.op,'execute') as execute:module.upgrade()
    sql='\n'.join(call.args[0] for call in execute.call_args_list)
    for fragment in ('DROP CONSTRAINT grants_registry_permission_scope_fkey','DROP CONSTRAINT grants_nonlegacy_active_fields','DROP COLUMN registry_permission','grants_permission_scope_fkey','FOREIGN KEY (permission, scope_kind)','REFERENCES access.permissions(permission, scope_kind) ON DELETE RESTRICT','grants_active_fields','revoked_at IS NOT NULL','membership_id IS NOT NULL','created_actor_id IS NOT NULL','updated_actor_id IS NOT NULL','updated_at IS NOT NULL'):
        assert fragment in sql
    for forbidden in ('pts.poetry','INSERT INTO','UPDATE access.','DELETE FROM','NOT VALID','GRANT ','identity.','CREATE FUNCTION','TRIGGER'):
        assert forbidden not in sql
    with pytest.raises(RuntimeError,match='Destructive rollback'):module.downgrade()


@pytest.mark.parametrize('strict,bridge,expected',[(False,True,'access_0011'),(True,False,'access_0012')])
def test_identity_selects_schema_resolved_direct_fk_before_full_verification(monkeypatch,strict,bridge,expected):
    spec=importlib.util.spec_from_file_location('_strict_identity',ROOT/'identity-migrations/identity_baseline.py')
    identity=importlib.util.module_from_spec(spec);spec.loader.exec_module(identity)
    calls=[];selected=[]
    class Result:
        def __init__(self,sql):self.sql=sql
        def all(self):return [('access_command_owner','access_migrator',False,'false','true')]
        def scalar_one(self):
            if ('enroll_studies_account' in self.sql or 'check_organization_permission' in self.sql or 'revoke_organization_grant' in self.sql or 'assign_organization_grant' in self.sql):return False
            if 'grants_permission_scope_fkey' in self.sql:return strict
            if 'pg_attribute' in self.sql:return bridge if 'registry_permission' in self.sql else True
            return True
    class Connection:
        def execute(self,sql):calls.append(str(sql));return Result(str(sql))
    monkeypatch.setattr(baseline,'verify_operator_roles',lambda c:None)
    monkeypatch.setattr(baseline,'verify_catalog',lambda c,r:selected.append(r))
    monkeypatch.setattr(baseline,'require_equal',lambda *args:None)
    monkeypatch.setattr(baseline,'rows',lambda *args:[])
    monkeypatch.setattr(baseline,'acl',lambda *args:[])
    assert identity.verified_access_command_extension(Connection())==(True,True)
    assert selected==[expected]
    query=next(sql for sql in calls if 'grants_permission_scope_fkey' in sql)
    for fragment in ("n.nspname='access'","c.relname='grants'","p.relname='permissions'","k.contype='f'"):
        assert fragment in query
    assert all('FROM access.' not in sql and 'FROM identity.' not in sql and '::regclass' not in sql for sql in calls)

def qualifier():
    sys.path.insert(0,str(ROOT/'tests'))
    import qualify_strict_grant_integrity
    return qualify_strict_grant_integrity


def test_qualification_refuses_optimized_python_before_opening_fixture(tmp_path):
    import subprocess
    result=subprocess.run([sys.executable,'-I','-B','-O',str(ROOT/'tests/qualify_strict_grant_integrity.py'),'--all'],capture_output=True,env={'PATH':'/usr/bin:/bin','ACCESS_QUALIFICATION_DIR':str(tmp_path/'missing')},timeout=10)
    assert result.returncode!=0 and b'access_qualification_optimized_python_prohibited' in result.stderr
    assert not (tmp_path/'missing').exists()


def test_qualification_log_custody_ignores_root_outputs_and_refuses_changed_owned_log(tmp_path):
    q=qualifier()
    generated=tmp_path/'clean-head-123.log';generated.write_bytes(b'fixed owner result')
    (tmp_path/'root-stdout.log').write_bytes(b'independent inspection')
    logs=q.qualification_logs(tmp_path)
    assert set(logs)=={generated.name}
    q.verify_qualification_logs(tmp_path,logs)
    (tmp_path/'root-stdout.log').write_bytes(b'new independent inspection')
    q.verify_qualification_logs(tmp_path,logs)
    generated.write_bytes(b'changed')
    with pytest.raises(AssertionError,match='qualification_log_custody_mismatch'):q.verify_qualification_logs(tmp_path,logs)


def test_bridge_custody_includes_consumed_helpers_driver_auth_and_runtime(tmp_path,monkeypatch):
    q=qualifier();proof=q.ROOT/'platform/deployment/.local/identity-baseline/_unit_strict_custody'
    # Exercise path inventory without reading or creating secret files.
    seen=[]
    monkeypatch.setattr(Path,'read_bytes',lambda path:seen.append(path) or b'fixed')
    monkeypatch.setattr(Path,'read_text',lambda path: '{"run_id":"11111111-1111-4111-8111-111111111111"}')
    monkeypatch.setattr(q.base,'source_paths',lambda p:[q.ACCESS/'access_operator.py'])
    q.source_snapshot(proof)
    assert proof/'runtime-credential.json' in seen and proof/'root_qualification_driver.py' in seen
    assert proof/'auth-helper-definitions.json' in seen
    assert q.ACCESS/'tests/qualify_application_register.py' in seen
    assert q.ACCESS/'tests/qualify_organization_application_storage.py' in seen


def test_privileged_snapshot_reuses_storage_mro_and_read_only_observation(monkeypatch,tmp_path):
    q=qualifier();calls=[]
    monkeypatch.setattr(q.base.Qualification,'snapshot',lambda self,case:dict(base_snapshot=True,catalog_triggers=[]))
    class Result:
        def scalar_one(self):return None
        def __iter__(self):return iter(())
    class Connection:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def exec_driver_sql(self,sql):calls.append(sql);return Result()
        def execute(self,*args):return Result()
    class Engine:
        def begin(self):return Connection()
        def dispose(self):pass
    instance=q.Qualification(tmp_path,{})
    monkeypatch.setattr(instance,'admin',lambda case:Engine())
    assert instance.snapshot('clean')['base_snapshot'] is True
    assert calls[0]=='SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'


def test_mutated_retained_state_refuses_before_any_database_inspection(tmp_path,monkeypatch):
    import json
    from hashlib import sha256
    q=qualifier()
    for name in ('credentials.json','run.json','bootstrap-fixed.log','clean-head-123.log'):(tmp_path/name).write_bytes(b'fixed')
    retained=tmp_path/'retained-state.json';retained.write_bytes(b'original')
    digest=sha256(retained.read_bytes()).hexdigest()
    retained.write_bytes(b'edited')
    (tmp_path/'bootstrap-source-custody.json').write_text(json.dumps(dict(status='passed',before={},after={},generated_inputs={name:sha256((tmp_path/name).read_bytes()).hexdigest() for name in ('credentials.json','run.json')},logs={'bootstrap-fixed.log':sha256(b'fixed').hexdigest()})))
    (tmp_path/'results.json').write_text(json.dumps(dict(status='passed',source={},logs=q.qualification_logs(tmp_path),retained_state_sha256=digest)))
    monkeypatch.setenv('ACCESS_QUALIFICATION_DIR',str(tmp_path))
    monkeypatch.setattr(sys,'argv',['qualifier','--verify-retained'])
    monkeypatch.setattr(q,'load_fixture',lambda proof:({},{}))
    monkeypatch.setattr(q,'source_snapshot',lambda proof:{})
    class NoDatabase:
        def __init__(self,*args):pytest.fail('database qualification initialized before custody validation')
    monkeypatch.setattr(q,'Qualification',NoDatabase)
    with pytest.raises(AssertionError,match='retained_state_custody_mismatch'):q.main()


@pytest.mark.parametrize('case,code,state',[('failure','access_migration_busy',None),('locks','access_migration_failed_requires_reconciliation','55P03')])
def test_lock_probe_requires_exact_sanitized_reason(tmp_path,monkeypatch,case,code,state):
    import json
    from types import SimpleNamespace
    q=qualifier();instance=q.Qualification(tmp_path,dict(access_owner_urls={case:'not opened'}))
    child=SimpleNamespace(returncode=1,stderr=b'',stdout=json.dumps(dict(code=code,sqlstate=state,error_class='MigrationFailure')).encode())
    monkeypatch.setattr(q.subprocess,'run',lambda *args,**kwargs:child)
    instance.migration_refusal(case)
    assert json.loads((tmp_path/(case+'-migration-refusal.json')).read_text())['sqlstate']==state
    child.stdout=json.dumps(dict(code='access_migration_failed_requires_reconciliation',sqlstate='42501',error_class='MigrationFailure')).encode()
    with pytest.raises(AssertionError,match='migration_lock_reason_mismatch'):instance.migration_refusal(case)


def test_snapshot_ignores_only_internal_ri_name_rebuilds():
    q=qualifier()
    def trigger(name='RI_ConstraintTrigger_a_123',enabled='O',internal=True,event='DELETE',function='RI_FKey_restrict_del'):
        return ['permissions',name,enabled,internal,'CREATE CONSTRAINT TRIGGER "'+name+'" AFTER '+event+' ON access.permissions FROM access.grants NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE FUNCTION "'+function+'"()']
    original=trigger()
    rebuilt=trigger('RI_ConstraintTrigger_a_999')
    user=trigger('custom_fk_guard',internal=False)
    expected=q.canonical_trigger_rows([original,user])
    assert expected==q.canonical_trigger_rows([user,rebuilt])
    assert len(q.canonical_trigger_rows([original,rebuilt]))==2
    assert original[1]=='RI_ConstraintTrigger_a_123'  # No input snapshot mutation.
    for changed in (trigger(enabled='D'),trigger(event='UPDATE'),trigger(function='RI_FKey_noaction_upd'),trigger('RI_ConstraintTrigger_c_123'),trigger(internal=False)):
        assert expected!=q.canonical_trigger_rows([changed,user])
    changed_definition=trigger();changed_definition[4]=changed_definition[4].replace('NOT DEFERRABLE','DEFERRABLE')
    assert expected!=q.canonical_trigger_rows([changed_definition,user])
    assert expected!=q.canonical_trigger_rows([original,trigger('renamed_user_guard',internal=False)])
    # Even an RI-shaped user trigger name remains exact.
    assert q.canonical_trigger_rows([trigger(internal=False)])!=q.canonical_trigger_rows([trigger('RI_ConstraintTrigger_a_999',internal=False)])
