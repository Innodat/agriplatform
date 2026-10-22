"""Private check-reader bridge contracts; native cases live in the qualifier."""
from pathlib import Path
import importlib.util
import json
from hashlib import sha256
import subprocess
import sys
import pytest

HERE = Path(__file__).resolve().parent


def migration():
    import qualify_identity_baseline  # installs the existing owner import seam
    spec = importlib.util.spec_from_file_location('check_reader_bridge_migration', HERE.parent/'identity-migrations/versions/0020_check_reader_bridge.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bridge_uses_existing_owner_set_edge_and_checks_before_grants(monkeypatch):
    module = migration(); calls = []
    class Connection:
        def exec_driver_sql(self, sql, **kwargs): calls.append(sql)
    monkeypatch.setattr(module.op, 'get_bind', lambda: Connection())
    monkeypatch.setattr(module, 'verify_catalog', lambda c, kind: calls.append(('catalog', kind)))
    monkeypatch.setattr(module, 'verify_check_reader_role', lambda c, staged=False, legacy=False: calls.append(('verify', staged, legacy)))
    module.upgrade()
    assert (module.revision, module.down_revision) == ('identity_0020', 'identity_0019')
    assert calls[0:2] == [('catalog', 'organization_target'), ('verify', True, True)]
    assert 'SET LOCAL ROLE identity_operator_authority_owner' in module.SENSITIVE_EXECUTE_SQL
    assert 'REVOKE EXECUTE ON FUNCTION %s FROM PUBLIC' in module.SENSITIVE_EXECUTE_SQL
    assert calls[-6:] == [('verify', True, False), 'GRANT USAGE ON SCHEMA identity TO access_check_reader',
        'SET LOCAL ROLE identity_account_projection_owner',
        'GRANT EXECUTE ON FUNCTION identity.current_account_organization() TO access_check_reader',
        'RESET ROLE', ('verify', False, False)]
    with pytest.raises(RuntimeError, match='Destructive rollback'): module.downgrade()


def test_preparation_is_true_admin_empty_role_only():
    sql = (HERE.parent/'tools/prepare_access_check_reader.sql').read_text()
    assert 'SELECT rolsuper FROM pg_roles WHERE rolname=current_user' in sql
    assert 'CREATE ROLE access_check_reader NOLOGIN NOINHERIT NOSUPERUSER' in sql
    assert 'NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS' in sql
    assert 'GRANT ' not in sql and 'ALTER ROLE' not in sql


def test_head20_dispatch_retains_exact19(monkeypatch):
    import qualify_identity_baseline as q
    b = q.baseline; seen = []
    monkeypatch.setattr(b, 'verify_legacy_history', lambda c: None)
    monkeypatch.setattr(b, 'verify_catalog', lambda c, k: seen.append(k))
    monkeypatch.setattr(b, 'verify_owned_history', lambda c: b.ORGANIZATION_TARGET_REVISION)
    b.verify_owned_postcondition(object())
    assert seen == ['organization_target']
    with pytest.raises(b.BaselineError, match='identity_unknown_history'):
        b.verify_owned_postcondition(object(), require_head=True)
    monkeypatch.setattr(b, 'verify_owned_history', lambda c: b.CHECK_READER_BRIDGE_REVISION)
    b.verify_owned_postcondition(object(), require_head=True)
    assert seen[-1] == 'check_reader_bridge'


@pytest.mark.parametrize('defect', [None, 'migration', 'missing_reference', 'modified_reference', 'source_pins'])
def test_reference_chains_immutable19_and_refuses_drift(tmp_path, monkeypatch, defect):
    import qualify_identity_baseline as q
    b = q.baseline; calls = []
    monkeypatch.setattr(b, 'trusted_organization_target_reference', lambda: calls.append('head19'))
    monkeypatch.setattr(b, 'HERE', tmp_path)
    (tmp_path/'versions').mkdir()
    source = tmp_path/'versions/0020_check_reader_bridge.py'; source.write_bytes(b'captured migration')
    (tmp_path/'source-pins.json').write_text('{}')
    content = json.dumps(dict(source_pins={}, migration_sha256=sha256(source.read_bytes()).hexdigest(), check_reader_bridge={})).encode()
    path = tmp_path/'check-reader-bridge-reference.json'; path.write_bytes(content)
    monkeypatch.setattr(b, 'CHECK_READER_BRIDGE_REFERENCE_SHA256', sha256(content).hexdigest())
    if defect == 'migration': source.write_bytes(b'drift')
    elif defect == 'missing_reference': path.unlink()
    elif defect == 'modified_reference': path.write_bytes(content+b' ')
    elif defect == 'source_pins': (tmp_path/'source-pins.json').write_text('{"changed":"pin"}')
    if defect:
        with pytest.raises(b.BaselineError, match='identity_reference_unavailable'): b.trusted_check_reader_bridge_reference()
    else: assert b.trusted_check_reader_bridge_reference() == {}
    assert calls == ['head19']


@pytest.mark.parametrize('file,args', [('qualify_check_reader_bridge.py', ['--all']),
    ('qualify_check_reader_bridge.py', ['--verify-retained'])])
def test_optimized_qualification_refuses_before_fixture_io(file, args):
    result = subprocess.run([sys.executable, '-O', '-I', '-B', str(HERE/file), *args], env={'PATH':'/usr/bin:/bin'}, capture_output=True, text=True)
    assert result.returncode != 0 and 'optimized_python_prohibited' in result.stderr
    assert 'IDENTITY_QUALIFICATION_DIR' not in result.stderr


def test_unexpected_qualification_failure_is_safe():
    code = f"import sys\nsys.path.insert(0,{str(HERE)!r})\nimport qualify_check_reader_bridge as q\ndef fail():raise RuntimeError('synthetic-sensitive-sql-and-credential')\nq.main=fail\nq.run()\n"
    result = subprocess.run([sys.executable, '-I', '-B', '-c', code], env={'PATH':'/usr/bin:/bin'}, capture_output=True, text=True)
    assert result.returncode == 1 and result.stdout == ''
    assert result.stderr == 'check_reader_bridge_qualification_failed:RuntimeError\n'


@pytest.mark.parametrize('key', [
    ('public','get_user_roles',''),
    ('identity','authorize','requested_permission identity.app_permission'),
    ('identity','create_user','email text'),
    ('identity','custom_access_token_hook','event jsonb'),
    ('identity','membership_join_org_allowed','p_org uuid'),
    ('identity','membership_join_profile_allowed','p_account uuid'),
])
@pytest.mark.parametrize('defect', [None, 'acl', 'owner', 'body'])
def test_foreign_recognition_accepts_exact_narrowed_acl_without_drift(monkeypatch, key, defect):
    import qualify_application_register as q
    from types import SimpleNamespace
    b = q.baseline
    owner, hashes, _ = b._FOREIGN_FUNCTIONS[key]
    row = [*key, owner, sorted(hashes)[0], b._FOREIGN_20_ACLS[key]]
    if defect == 'acl': row[-1] += ',unexpected'
    if defect == 'owner': row[-3] = 'unexpected_owner'
    if defect == 'body': row[-2] = '0' * 64
    def query(connection, sql):
        if 'FROM pg_proc p JOIN' in sql: return [row]
        if 'FROM pg_namespace WHERE' in sql: return [('public', True, False)]
        if 'LEFT JOIN pg_depend' in sql or "c.relkind='S'" in sql: return []
        pytest.fail('unrecognized foreign privilege query')
    monkeypatch.setattr(b, 'rows', query)
    connection = SimpleNamespace(dialect=SimpleNamespace(server_version_info=(17,)))
    if defect:
        with pytest.raises(b.BaselineError, match='access_operator_roles_invalid'):
            b.verify_operator_foreign_privileges(connection, 'access_command_owner')
    else: b.verify_operator_foreign_privileges(connection, 'access_command_owner')


def test_retained_log_custody_refuses_modified_and_missing_log(tmp_path, monkeypatch):
    import qualify_application_register as base
    original_cases = base.CASES
    import qualify_check_reader_bridge as q
    base.CASES = original_cases
    path = tmp_path/'check-reader-controlled19-to20.log'
    path.write_text('safe synthetic witness\n')
    expected = q.qualification_logs(tmp_path)
    q.verify_qualification_logs(tmp_path, expected)
    path.write_text('changed')
    with pytest.raises(AssertionError, match='qualification_log_custody_mismatch'):
        q.verify_qualification_logs(tmp_path, expected)
    path.unlink()
    with pytest.raises(AssertionError, match='qualification_log_custody_mismatch'):
        q.verify_qualification_logs(tmp_path, expected)


@pytest.mark.parametrize('failure', ['observer', 'runner', 'mutation-check'])
def test_refusal_restores_fixture_when_probe_fails_and_keeps_safe_witness(tmp_path, monkeypatch, failure):
    import qualify_application_register as base
    original_cases = base.CASES
    import qualify_check_reader_bridge as q
    base.CASES = original_cases
    runner = object.__new__(q.Qualification)
    runner.proof = tmp_path
    state = {'mutated': False, 'executed': False}
    calls = []
    def admin_sql(sql):
        calls.append(sql)
        state['mutated'] = sql == 'fixture-change'
    def raw_catalog():
        if state['mutated'] and failure == 'observer':
            raise RuntimeError('synthetic observer failure')
        return {'mutated': state['mutated']}
    def identity(*args, **kwargs):
        state['executed'] = True
        if failure == 'runner': raise RuntimeError('synthetic runner failure')
    def snapshot(case):
        return {'mutated': state['mutated'], 'unexpected': state['executed'] and state['mutated']}
    monkeypatch.setattr(runner, 'admin_sql', admin_sql)
    monkeypatch.setattr(runner, 'raw_catalog', raw_catalog)
    monkeypatch.setattr(runner, 'identity', identity)
    monkeypatch.setattr(runner, 'snapshot', snapshot)
    monkeypatch.setattr(runner, 'catalog', lambda: pytest.fail('validated observer used for drift'))
    with pytest.raises((RuntimeError, AssertionError)):
        runner.refusal('synthetic-probe', 'fixture-change', 'fixture-restore')
    assert calls == ['fixture-change', 'fixture-restore']
    assert state['mutated'] is False
    witness = json.loads((tmp_path/'check-reader-synthetic-probe-refusal.json').read_text())
    assert witness['restored'] is True and witness['stage'] == 'synthetic-probe'
    assert set(witness) == {'stage', 'status', 'restored'}


@pytest.mark.parametrize('flag_index', range(1, 8), ids=[
    'superuser', 'inherit', 'createrole', 'createdb', 'login', 'replication', 'bypassrls'])
@pytest.mark.parametrize('staged', [True, False])
def test_reader_verifier_denies_each_unsafe_role_flag(flag_index, staged):
    import qualify_identity_baseline as q
    b = q.baseline
    row = [b.CHECK_READER] + [False] * 7
    row[flag_index] = True
    class Connection:
        def execute(self, sql):
            assert str(sql) == b.CHECK_READER_ROLE_QUERIES['check_reader_role']
            return [row]
    with pytest.raises(b.BaselineError, match='^identity_check_reader_role_unsafe$'):
        b.verify_check_reader_role(Connection(), staged=staged)


def test_reader_policy_role_dependency_refuses_without_changing_historical_query():
    import qualify_identity_baseline as q
    b = q.baseline
    assert "s.deptype IN ('a','o')" in b.PROJECTION_ROLE_QUERIES['projection_dependencies']
    assert "s.deptype IN ('a','o','r')" in b.CHECK_READER_ROLE_QUERIES['check_reader_dependencies']
    class Result(list):
        def all(self): return self
    class Connection:
        def execute(self, sql):
            if str(sql) == b.CHECK_READER_ROLE_QUERIES['check_reader_role']:
                return [(b.CHECK_READER,) + (False,) * 7]
            if str(sql) == b.CHECK_READER_ROLE_QUERIES['check_reader_memberships']:
                return Result()
            assert str(sql) == b.CHECK_READER_ROLE_QUERIES['check_reader_dependencies']
            return Result([('synthetic_database', 'pg_policy', 'r', 'policy synthetic_foreign_policy')])
    with pytest.raises(b.BaselineError, match='^identity_check_reader_role_not_empty$'):
        b.verify_check_reader_role(Connection(), staged=True, legacy=True)


@pytest.mark.parametrize('label', ['unsafe-login', 'blocked-advisory', 'blocked-ledger-lock'])
@pytest.mark.parametrize('defect', [None, 'unrelated-error', 'earlier-expected-error', 'later-unrelated-error', 'slow-lock'])
def test_negative_migration_requires_exact_final_error_and_bounded_lock(tmp_path, monkeypatch, label, defect):
    import qualify_application_register as base
    original_cases = base.CASES
    import qualify_check_reader_bridge as q
    base.CASES = original_cases
    from types import SimpleNamespace
    runner = object.__new__(q.Qualification)
    runner.proof = tmp_path
    runner.private = {'owner_urls': {'bridge': 'postgresql://synthetic.invalid/synthetic'}}
    code = q.REFUSAL_CODES[label]
    error = 'identity_baseline.BaselineError: ' + code + '\n'
    if defect == 'unrelated-error': error = 'RuntimeError: unrelated failure\n'
    if defect == 'earlier-expected-error': error += 'identity_baseline.BaselineError: identity_reference_unavailable\n'
    if defect == 'later-unrelated-error': error += 'RuntimeError: unrelated final failure\n'
    lock_probe = label.startswith('blocked-')
    elapsed = q.LOCK_PROBE_ELAPSED_BOUND + 1 if defect == 'slow-lock' else 1
    clock = iter([0, elapsed])
    monkeypatch.setattr(q.time, 'monotonic', lambda: next(clock))
    def run(*args, **kwargs):
        assert kwargs['timeout'] == (q.LOCK_PROBE_TIMEOUT if lock_probe else 90)
        return SimpleNamespace(returncode=1, stdout=b'', stderr=error.encode())
    monkeypatch.setattr(q.subprocess, 'run', run)
    if defect in ('unrelated-error', 'earlier-expected-error', 'later-unrelated-error'):
        with pytest.raises(AssertionError, match='identity_refusal_code_mismatch'):
            runner.identity(label, success=False)
    elif defect == 'slow-lock' and lock_probe:
        with pytest.raises(AssertionError, match='identity_lock_probe_exceeded_bound'):
            runner.identity(label, success=False)
    else: runner.identity(label, success=False)


@pytest.mark.parametrize('legacy',[True,False])
@pytest.mark.parametrize('defect',[None,'admin','inherit','no_set','wrong_member','extra_edge','dependency','schema','effective_right'])
def test_staged_bridge_allows_only_known_global_set_edge_with_empty_local_rights(monkeypatch,legacy,defect):
    import qualify_identity_baseline as q
    b=q.baseline
    edge=[b.CHECK_READER,'access_migrator',False,'false','true']
    if defect=='admin':edge[2]=True
    if defect=='inherit':edge[3]='true'
    if defect=='no_set':edge[4]='false'
    if defect=='wrong_member':edge[1]='access_runtime'
    members=[tuple(edge)]
    if defect=='extra_edge':members.append((b.CHECK_READER,'identity_migrator',False,'false','true'))
    checked=[]
    class Result(list):
        def all(self):return self
        def scalar_one(self):return bool(self[0])
    class Connection:
        def execute(self,sql,parameters=None):
            sql=str(sql)
            checked.append(sql)
            if sql==b.CHECK_READER_ROLE_QUERIES['check_reader_role']:
                return Result([(b.CHECK_READER,)+(False,)*7])
            if sql==b.CHECK_READER_ROLE_QUERIES['check_reader_memberships']:return Result(members)
            if sql==b.CHECK_READER_ROLE_QUERIES['check_reader_dependencies']:
                return Result([('fixture','pg_namespace','a','schema identity')] if defect=='dependency' else [])
            if 'SELECT nspname,p FROM pg_namespace' in sql:
                return Result([('public','USAGE')]+([('identity','USAGE')] if defect=='schema' else []))
            if 'has_database_privilege' in sql:return Result([False])
            if 'SELECT EXISTS (' in sql:
                assert parameters=={'role':b.CHECK_READER,'staged':True,'legacy':legacy}
                return Result([defect=='effective_right'])
            pytest.fail('unexpected staged query')
    # Staged execution must not request already-installed per-database bridge rights.
    monkeypatch.setattr(b,'verified_access_reader_extension',lambda *_:pytest.fail('installed extension invoked during staging'))
    if defect:
        with pytest.raises(b.BaselineError):b.verify_check_reader_role(Connection(),staged=True,legacy=legacy)
    else:
        b.verify_check_reader_role(Connection(),staged=True,legacy=legacy)
        assert any('SELECT EXISTS (' in sql for sql in checked)
        assert any('check_reader' not in sql and 'has_database_privilege' in sql for sql in checked)
