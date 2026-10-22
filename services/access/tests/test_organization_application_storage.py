"""Access8 storage contract and exact prior-version compatibility."""
import importlib.util
from pathlib import Path
import sys
from unittest.mock import patch
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'migrations'))
import access_baseline as baseline
import access_registration_baseline as registration


def migration():
    spec=importlib.util.spec_from_file_location('_organization_storage',ROOT/'migrations/versions/0008_organization_application_storage.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_eight_is_additive_and_prior_seven_remain_known():
    assert baseline.validate_revision(['access_0008'])=='access_0008'
    for i in range(1,9):assert baseline.validate_revision([f'access_000{i}'])==f'access_000{i}'
    for values in ([],['access_0014'],['access_0007','access_0008']):
        with pytest.raises(baseline.BaselineError):baseline.validate_revision(values)
    assert registration._sql('access_0008')==registration._sql('access_0007')


def test_storage_migration_is_private_structural_only():
    module=migration();assert module.revision=='access_0008' and module.down_revision=='access_0007'
    with patch.object(module.op,'execute') as execute:module.upgrade()
    sql=execute.call_args.args[0]
    assert 'CREATE TABLE access.organization_applications' in sql
    for item in ('PRIMARY KEY (org_id, app_id)','ON DELETE RESTRICT','ENABLE ROW LEVEL SECURITY','FORCE ROW LEVEL SECURITY','TO access_migrator','current_setting(\'app.org_id\', true)','FOR EACH STATEMENT EXECUTE FUNCTION access.registry_storage_immutable()'):
        assert item in sql
    for forbidden in ('INSERT INTO','GRANT ','CREATE FUNCTION','identity.','access_command_owner','access_operator','access_runtime'):
        assert forbidden not in sql
    with pytest.raises(RuntimeError,match='Destructive rollback'):module.downgrade()


def test_identity_selects_eight_using_only_metadata(monkeypatch):
    spec=importlib.util.spec_from_file_location('_storage_identity_baseline',ROOT/'identity-migrations/identity_baseline.py')
    identity=importlib.util.module_from_spec(spec);spec.loader.exec_module(identity)
    calls=[];selected=[]
    class Result:
        def __init__(self,sql):self.sql=sql
        def all(self):return [('access_command_owner','access_migrator',False,'false','true')]
        def scalar_one(self):return 'assign_organization_grant' not in self.sql and 'configure_organization_application' not in self.sql and 'pg_attribute' not in self.sql and 'grants_permission_scope_fkey' not in self.sql
    class Connection:
        def execute(self,sql):calls.append(str(sql));return Result(str(sql))
    monkeypatch.setattr(baseline,'verify_operator_roles',lambda c:None)
    monkeypatch.setattr(baseline,'verify_catalog',lambda c,r:selected.append(r))
    monkeypatch.setattr(baseline,'require_equal',lambda *args:None)
    monkeypatch.setattr(baseline,'rows',lambda *args:[])
    monkeypatch.setattr(baseline,'acl',lambda *args:[])
    assert identity.verified_access_command_extension(Connection())==(True,True)
    assert selected==['access_0008']
    assert any('pg_class' in sql and 'organization_applications' in sql for sql in calls)
    assert all('FROM access.' not in sql and 'FROM identity.' not in sql for sql in calls)


def test_optimized_qualification_refuses_before_fixture_access(tmp_path):
    import os,subprocess
    fixture=tmp_path/'missing'
    result=subprocess.run([sys.executable,'-I','-B','-O',str(ROOT/'tests/qualify_organization_application_storage.py'),'--all'],capture_output=True,env={'PATH':'/usr/bin:/bin','ACCESS_QUALIFICATION_DIR':str(fixture)},timeout=10)
    assert result.returncode!=0 and b'access_qualification_optimized_python_prohibited' in result.stderr
    assert not fixture.exists()


def test_storage_catalog_needs_no_access_schema_usage(monkeypatch):
    import re
    from types import SimpleNamespace
    queries=[]
    class Connection:
        dialect=SimpleNamespace(server_version_info=(17,))
        def execute(self,sql):
            sql=str(sql);queries.append(sql)
            # Model the independently observed restricted Identity catalog boundary:
            # OID discovery is permitted, schema-qualified regclass input is not.
            if re.search(r"'access\.[^']+'::regclass",sql):
                raise PermissionError('schema_usage_required')
            return SimpleNamespace(all=lambda:[])
    monkeypatch.setattr(baseline,'require_equal',lambda *args:None)
    baseline.verify_organization_applications(Connection())
    assert queries and all('FROM access.' not in sql for sql in queries)
    assert any("n.nspname='access' AND c.relname='organization_applications'" in sql for sql in queries)
    internal=next(sql for sql in queries if 't.tgconstrrelid' in sql)
    assert "t.tgrelid=(SELECT c.oid" in internal and "k.conrelid=(SELECT c.oid" in internal


def run_unprepared_qualification(path):
    import json,subprocess
    result=subprocess.run([sys.executable,'-I','-B',str(ROOT/'tests/qualify_organization_application_storage.py'),'--all'],capture_output=True,env={'PATH':'/usr/bin:/bin','ACCESS_QUALIFICATION_DIR':str(path)},timeout=10)
    assert result.returncode==1 and result.stderr==b''
    assert json.loads(result.stdout)=={'ok':False,'code':'access_qualification_failed_requires_inspection'}
    return result


def test_failure_diagnostics_preserve_prior_invocation_bytes(tmp_path):
    import json
    run_unprepared_qualification(tmp_path)
    initial=list(tmp_path.glob('failure-frames-*.json'));assert len(initial)==1
    original=initial[0].read_bytes()
    run_unprepared_qualification(tmp_path)
    records=list(tmp_path.glob('failure-frames-*.json'));assert len(records)==2
    assert initial[0].read_bytes()==original
    for path in records:
        data=json.loads(path.read_bytes())
        assert set(data)=={'type','frames'}
        assert all(set(frame)=={'file','line','function'} for frame in data['frames'])
        assert path.stat().st_mode & 0o777==0o600


@pytest.mark.parametrize('storage',('missing','file'))
def test_failure_without_available_fixture_storage_is_safe(tmp_path,storage):
    path=tmp_path/storage
    if storage=='file':path.write_bytes(b'preserve')
    run_unprepared_qualification(path)
    if storage=='file':assert path.read_bytes()==b'preserve'
    else:assert not path.exists()
