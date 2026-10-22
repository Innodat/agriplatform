"""Staged Access10 grant storage; no grant execution or effective authority."""
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
    spec=importlib.util.spec_from_file_location('_grant_storage',ROOT/'migrations/versions/0010_grant_lifecycle_storage.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_exact_ten_retains_all_prior_versions_and_command_bytes():
    assert baseline.HEAD=='access_0015'
    for i in range(1,11):assert baseline.validate_revision([f'access_{i:04}'])==f'access_{i:04}'
    for values in ([],['access_0016'],['access_0009','access_0010']):
        with pytest.raises(baseline.BaselineError):baseline.validate_revision(values)
    assert registration._sql('access_0010')==registration._sql('access_0009')


def test_storage_is_additive_ddl_with_nullable_external_provenance():
    module=migration();assert (module.revision,module.down_revision)==('access_0010','access_0009')
    with patch.object(module.op,'execute') as execute:module.upgrade()
    sql=execute.call_args.args[0]
    for fragment in ('ALTER TABLE access.grants','scope_kind text NOT NULL DEFAULT',"CHECK (scope_kind = 'organization')",'revision bigint NOT NULL DEFAULT 1','CHECK (revision > 0)','revoked_at timestamptz','created_actor_id uuid','updated_actor_id uuid','updated_at timestamptz'):
        assert fragment in sql
    for column in ('created_actor_id','updated_actor_id'):assert f'grants_{column}_non_nil' in sql
    for column in ('revoked_at','updated_at'):assert f'CHECK (isfinite({column}))' in sql
    for forbidden in ('INSERT ','UPDATE ','GRANT ','REFERENCES','CREATE FUNCTION','TRIGGER','identity.','membership_id','created_by','created_at'):
        assert forbidden not in sql
    with pytest.raises(RuntimeError,match='Destructive rollback'):module.downgrade()


@pytest.mark.parametrize('staged,expected',[(False,'access_0009'),(True,'access_0010')])
def test_identity_selects_exact_bundle_from_schema_resolved_column_metadata(monkeypatch,staged,expected):
    spec=importlib.util.spec_from_file_location('_grant_storage_identity',ROOT/'identity-migrations/identity_baseline.py')
    identity=importlib.util.module_from_spec(spec);spec.loader.exec_module(identity)
    calls=[];selected=[]
    class Result:
        def __init__(self,sql):self.sql=sql
        def all(self):return [('access_command_owner','access_migrator',False,'false','true')]
        def scalar_one(self):return False if ('check_organization_permission' in self.sql or 'revoke_organization_grant' in self.sql or 'assign_organization_grant' in self.sql) or 'grants_permission_scope_fkey' in self.sql else (False if 'registry_permission' in self.sql else staged) if 'pg_attribute' in self.sql else True
    class Connection:
        def execute(self,sql):calls.append(str(sql));return Result(str(sql))
    monkeypatch.setattr(baseline,'verify_operator_roles',lambda c:None)
    monkeypatch.setattr(baseline,'verify_catalog',lambda c,r:selected.append(r))
    monkeypatch.setattr(baseline,'require_equal',lambda *args:None)
    monkeypatch.setattr(baseline,'rows',lambda *args:[])
    monkeypatch.setattr(baseline,'acl',lambda *args:[])
    assert identity.verified_access_command_extension(Connection())==(True,True)
    assert selected==[expected]
    query=next(sql for sql in calls if 'pg_attribute' in sql)
    assert "n.nspname='access'" in query and "c.relname='grants'" in query and "a.attname='revision'" in query
    assert all('FROM access.' not in sql and 'FROM identity.' not in sql and '::regclass' not in sql for sql in calls)


def test_qualification_refuses_optimized_python_before_fixture_access(tmp_path):
    import subprocess
    fixture=tmp_path/'missing'
    result=subprocess.run([sys.executable,'-I','-B','-O',str(ROOT/'tests/qualify_grant_lifecycle_storage.py'),'--all'],capture_output=True,env={'PATH':'/usr/bin:/bin','ACCESS_QUALIFICATION_DIR':str(fixture)},timeout=10)
    assert result.returncode!=0 and b'access_qualification_optimized_python_prohibited' in result.stderr
    assert not fixture.exists()


def test_qualification_failure_keeps_unique_safe_diagnostics(tmp_path):
    import json,subprocess
    before=None
    for count in (1,2):
        result=subprocess.run([sys.executable,'-I','-B',str(ROOT/'tests/qualify_grant_lifecycle_storage.py'),'--all'],capture_output=True,env={'PATH':'/usr/bin:/bin','ACCESS_QUALIFICATION_DIR':str(tmp_path)},timeout=10)
        assert result.returncode==1 and result.stderr==b''
        assert json.loads(result.stdout)==dict(ok=False,code='access_qualification_failed_requires_inspection')
        paths=list(tmp_path.glob('failure-frames-*.json'));assert len(paths)==count
        if before:assert before[0].read_bytes()==before[1]
        before=(paths[0],paths[0].read_bytes())
        for path in paths:
            record=json.loads(path.read_text());assert set(record)=={'type','frames'}
            assert all(set(frame)=={'file','line','function'} for frame in record['frames'])
            assert path.stat().st_mode&0o777==0o600


def qualifier():
    sys.path.insert(0,str(ROOT/'tests'))
    import qualify_grant_lifecycle_storage
    return qualify_grant_lifecycle_storage


def test_previous_package_refuses_file_tamper_and_coordinated_manifest_tamper(tmp_path,monkeypatch):
    import json
    from hashlib import sha256
    q=qualifier()
    assert q.PREVIOUS_INVENTORY_SHA256=='b276f6292c88e901d5850ba56bd9f93205560848f9840981e719eff03845f787'
    root=tmp_path/'previous-root';root.mkdir()
    source=root/'adapter.py';source.write_bytes(b'original reviewed bytes')
    sources={'adapter.py':sha256(source.read_bytes()).hexdigest()}
    manifest=dict(baseline_commit='7a565562c7b5086f2f7b432358f0048c45a47efc',sources=sources)
    path=tmp_path/'previous-source.json';path.write_text(json.dumps(manifest))
    # A tiny synthetic inventory stands in for the independently reviewed79 files.
    digest=sha256(json.dumps(sources,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    monkeypatch.setattr(q,'PREVIOUS_INVENTORY_SHA256',digest)
    assert q.previous_inventory(tmp_path)==manifest
    source.write_bytes(b'tampered source')
    with pytest.raises(AssertionError,match='previous_source_mismatch'):q.previous_inventory(tmp_path)
    manifest['sources']['adapter.py']=sha256(source.read_bytes()).hexdigest()
    path.write_text(json.dumps(manifest))
    with pytest.raises(AssertionError,match='previous_inventory_mismatch'):q.previous_inventory(tmp_path)


@pytest.mark.parametrize('change',('alter','delete'))
def test_retained_log_tamper_refuses_before_database_inspection(tmp_path,monkeypatch,change):
    import json
    q=qualifier()
    generated=tmp_path/'configure-head-123.log';generated.write_bytes(b'approved generated log')
    (tmp_path/'root-stdout.log').write_bytes(b'root-owned independent inspection')
    logs=q.qualification_logs(tmp_path)
    assert set(logs)=={generated.name}
    q.verify_qualification_logs(tmp_path,logs)
    (tmp_path/'root-stdout.log').write_bytes(b'root can append inspections')
    q.verify_qualification_logs(tmp_path,logs)
    if change=='alter':generated.write_bytes(b'changed log')
    else:generated.unlink()
    (tmp_path/'results.json').write_text(json.dumps(dict(status='passed',source={},logs=logs)))
    (tmp_path/'bootstrap-source-custody.json').write_text(json.dumps(dict(status='passed',before={},after={},logs={})))
    monkeypatch.setenv('ACCESS_QUALIFICATION_DIR',str(tmp_path))
    monkeypatch.setattr(sys,'argv',['qualifier','--verify-retained'])
    monkeypatch.setattr(q,'load_fixture',lambda proof:({},{}))
    monkeypatch.setattr(q,'source_snapshot',lambda proof:{})
    class NoDatabase:
        def __init__(self,*args):pass
        def snapshot(self,*args):pytest.fail('database inspected before log validation')
        def retained(self):pytest.fail('retained inspection ran before log validation')
    monkeypatch.setattr(q,'Qualification',NoDatabase)
    with pytest.raises(AssertionError,match='qualification_log_custody_mismatch'):q.main()


def test_previous_child_failure_discards_sql_tracebacks_and_unapproved_output(tmp_path,monkeypatch):
    from types import SimpleNamespace
    import json
    q=qualifier();instance=q.Qualification(tmp_path,dict(access_operator_urls={'upgrade':'not opened'}))
    private=b'password=secret SELECT sensitive_sql driver traceback'
    child=SimpleNamespace(returncode=1,stdout=private,stderr=private)
    monkeypatch.setattr(q.subprocess,'run',lambda *args,**kwargs:child)
    with pytest.raises(AssertionError,match='actual_previous9_adapter_failed'):instance.previous9('upgrade',[],'failure')
    saved=(tmp_path/'previous9-failure.log').read_bytes()
    assert private not in saved and json.loads(saved)==dict(error_class='ChildFailure',sqlstate=None,returncode=1)
    child.stdout=json.dumps(dict(ok=False,error_class='OperationalError',sqlstate='42501')).encode()
    with pytest.raises(AssertionError):instance.previous9('upgrade',[],'safe-failure')
    assert json.loads((tmp_path/'previous9-safe-failure.log').read_text())==dict(error_class='OperationalError',sqlstate='42501',returncode=1)


def test_previous_child_success_persists_only_validated_compact_receipts(tmp_path,monkeypatch):
    from types import SimpleNamespace
    import json
    q=qualifier();value=q.base.document()
    receipt=dict(operation_id=value['operation_id'],result=dict(command='application.register',target={'app_id':'synthetic_app'},disposition='created',revision='1',event_id='11111111-1111-4111-8111-111111111111'),command_version=1,result_version=1,committed_at='2001-01-01 00:00:00+00:00',status='committed')
    child=SimpleNamespace(returncode=0,stdout=json.dumps(dict(ok=True,receipts=[receipt])).encode(),stderr=b'')
    monkeypatch.setattr(q.subprocess,'run',lambda *args,**kwargs:child)
    instance=q.Qualification(tmp_path,dict(access_operator_urls={'upgrade':'not opened'}))
    assert instance.previous9('upgrade',[value],'success')==[receipt]
    assert json.loads((tmp_path/'previous9-success.log').read_text())==[receipt]
    receipt['unexpected']='driver payload'
    child.stdout=json.dumps(dict(ok=True,receipts=[receipt])).encode()
    with pytest.raises(AssertionError):instance.previous9('upgrade',[value],'unapproved')
    assert b'driver payload' not in (tmp_path/'previous9-unapproved.log').read_bytes()


def test_retained_refuses_exact_known_nine_before_claiming_ten(tmp_path,monkeypatch):
    q=qualifier()
    class Result:
        def all(self):return [('access_0009',)]
    class Connection:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def exec_driver_sql(self,sql):return Result()
    class Engine:
        def begin(self):return Connection()
        def dispose(self):pass
    instance=q.Qualification(tmp_path,{})
    monkeypatch.setattr(instance,'db',lambda case:Engine())
    # The shared postcondition deliberately permits this known older catalog.
    monkeypatch.setattr(q.baseline,'preflight',lambda c:None)
    monkeypatch.setattr(q.baseline,'verify_postcondition',lambda c:None)
    with pytest.raises(AssertionError,match='retained_head_not_ten'):instance.retained()
    assert instance.results==[]
