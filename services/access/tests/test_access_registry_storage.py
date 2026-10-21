"""Focused registry history/guard checks; native qualifier proves SQL behavior."""
from pathlib import Path
import importlib.util
import sys
import pytest

OWNER=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(OWNER/'migrations'))


def test_registry_revision_is_a_known_exact_history():
    from access_baseline import validate_revision
    assert validate_revision(['access_0003'])=='access_0003'


def test_storage_migration_is_additive_and_refuses_downgrade():
    path=OWNER/'migrations/versions/0003_registry_storage.py'
    assert path.is_file(), 'registry migration missing'
    spec=importlib.util.spec_from_file_location('registry_storage_revision',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert module.revision=='access_0003' and module.down_revision=='access_0002'
    with pytest.raises(RuntimeError,match='Destructive rollback'):module.downgrade()


def test_optimized_qualifier_refuses_before_any_fixture_access():
    import subprocess
    code=f"""
import sys
sys.path.insert(0,{str(OWNER/'tests')!r})
import qualify_access_registry_storage as q
q.fixture=lambda:(_ for _ in ()).throw(RuntimeError('fixture_reached'))
sys.argv=['qualifier','--all']
try:q.main()
except RuntimeError as error:
    if str(error)!='access_qualification_optimized_python_prohibited':raise
else:raise RuntimeError('optimized_execution_accepted')
"""
    result=subprocess.run([sys.executable,'-I','-B','-O','-c',code],capture_output=True,text=True,timeout=60)
    assert result.returncode==0,result.stderr


@pytest.mark.parametrize('name',('applications','permissions','entry_permissions'))
@pytest.mark.parametrize('drift',('unlogged','inherited','owner','rls'))
def test_registry_table_shape_refuses_before_columns(monkeypatch,name,drift):
    import access_baseline as baseline
    def query(connection,sql):
        if 'FROM pg_class WHERE oid=' in sql:
            return [('wrong_owner' if drift=='owner' else 'access_migrator','r',drift=='rls',False,None,False,'d','u' if drift=='unlogged' else 'p')]
        if 'FROM pg_inherits' in sql:return [(1,)]
        pytest.fail('unsafe table reached column inspection')
    monkeypatch.setattr(baseline,'rows',query)
    with pytest.raises(baseline.BaselineError,match='access_catalog_mismatch'):baseline.verify_registry(object(),name)


def test_non_utf8_refuses_before_source_catalog_or_effects(monkeypatch):
    import access_baseline as baseline
    calls=[]
    def rows(connection,sql):
        calls.append(sql)
        assert sql=='SHOW server_encoding'
        return [('SQL_ASCII',)]
    monkeypatch.setattr(baseline,'rows',rows)
    with pytest.raises(baseline.BaselineError,match='access_utf8_encoding_required'):baseline.preflight(object())
    assert calls==['SHOW server_encoding']


@pytest.mark.parametrize('saved',({}, {'clean':{}}, {'clean':{},'previous':{},'extra':{}}))
def test_retained_inventory_must_match_fixture(saved):
    import qualify_access_registry_storage as q
    private={'databases':{'native':'','red':'','clean':'','previous':''}}
    with pytest.raises(AssertionError,match='retained_case_inventory_mismatch'):q.require_retained_inventory(saved,private)
    q.require_retained_inventory({'clean':{},'previous':{}},private)


@pytest.mark.parametrize('mutation',('addition','removal'))
def test_completion_recomputes_source_inventory(monkeypatch,tmp_path,mutation):
    import qualify_access_registry_storage as q
    monkeypatch.setattr(q,'ROOT',tmp_path)
    original=tmp_path/'existing.py';original.write_text('original')
    monkeypatch.setattr(q,'source_paths',lambda proof:list(tmp_path.glob('*.py')))
    captured=q.source_snapshot(tmp_path)
    if mutation=='addition':(tmp_path/'added.py').write_text('new source')
    else:original.unlink()
    with pytest.raises(AssertionError,match='qualification_source_changed'):q.verify_source_completion(tmp_path,captured)


def test_snapshot_establishes_bounded_read_only_repeatable_read_before_observation(monkeypatch,tmp_path):
    import qualify_access_registry_storage as q
    from types import SimpleNamespace
    events=[]
    class Connection:
        dialect=SimpleNamespace(server_version_info=(17,))
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def exec_driver_sql(self,sql):
            events.append(sql)
            return []
        def execute(self,*args):return SimpleNamespace(scalar_one=lambda:None)
    class Database:
        def begin(self):return Connection()
        def dispose(self):pass
    qualifier=q.Qualification(tmp_path,{})
    monkeypatch.setattr(qualifier,'db',lambda *args:Database())
    assert qualifier.snapshot('synthetic')
    assert events[0]=='SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'
    assert 'statement_timeout' in events[1] and 'lock_timeout' in events[1] and 'idle_in_transaction_session_timeout' in events[1]
    assert "SET LOCAL transaction_timeout='30s'"==events[2]
    assert 't.tgenabled,t.tgisinternal' in next(sql for sql in events if 'FROM pg_trigger' in sql)


@pytest.mark.parametrize('name',('applications','permissions','entry_permissions'))
def test_registry_disabled_internal_fk_trigger_is_rejected(monkeypatch,name):
    import access_baseline as baseline
    original=baseline.require_equal
    inspected=[]
    def query(connection,sql):
        inspected.append(sql)
        if 'WHERE t.tgrelid=' in sql and 't.tgisinternal' in sql:return [('entry_permissions_app_id_permission_fkey','D')]
        return []
    def compare(actual,expected,*args):
        if actual and actual[0][-1]=='D':original(actual,expected,*args)
    monkeypatch.setattr(baseline,'rows',query)
    monkeypatch.setattr(baseline,'acl',lambda *args,**kwargs:[])
    monkeypatch.setattr(baseline,'require_equal',compare)
    class Connection:
        dialect=type('Dialect',(),{'server_version_info':(17,)})()
    with pytest.raises(baseline.BaselineError,match='access_catalog_mismatch'):baseline.verify_registry(Connection(),name)
    assert any('t.tgisinternal' in sql for sql in inspected)
