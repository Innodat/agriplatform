"""Focused guards for synthetic projection evidence; no database operations."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))
import qualify_current_account_actor as projection
import qualify_identity_baseline as qualification


def digest(data):
    return hashlib.sha256(data).hexdigest()


@pytest.mark.parametrize('corruption', ['reference.json', 'actor-reference.json', 'versions/0002_actor_registry.py'])
def test_projection_reference_retains_original_evidence(tmp_path, monkeypatch, corruption):
    baseline = qualification.baseline
    owner = qualification.OWNER
    for name in ['source-pins.json', 'reference.json', 'actor-reference.json',
                 'versions/0002_actor_registry.py', 'versions/0003_current_account_actor.py']:
        path = tmp_path/name
        path.parent.mkdir(exist_ok=True)
        shutil.copyfile(owner/name, path)
    reference = {'source_pins': json.loads((tmp_path/'source-pins.json').read_bytes()),
                 'migration_sha256': digest((tmp_path/'versions/0003_current_account_actor.py').read_bytes()),
                 'projection': {}}
    content = json.dumps(reference).encode()
    (tmp_path/'projection-reference.json').write_bytes(content)
    monkeypatch.setattr(baseline, 'HERE', tmp_path)
    monkeypatch.setattr(baseline, 'PROJECTION_REFERENCE_SHA256', digest(content))
    assert baseline.trusted_projection_reference() == {}
    (tmp_path/corruption).write_bytes(b'corrupted immutable evidence')
    with pytest.raises(baseline.BaselineError, match='identity_reference_unavailable'):
        baseline.trusted_projection_reference()


def test_projection_snapshot_includes_effective_auth_table_and_column_privileges(monkeypatch):
    baseline = qualification.baseline
    monkeypatch.setattr(baseline, 'catalog_snapshot', lambda connection: {})
    class Result:
        def __init__(self, rows): self.rows = rows
        def __iter__(self): return iter(self.rows)
    class Connection:
        def __init__(self, public, extra_denied=False):
            self.public = public
            self.extra_denied = extra_denied
        def execute(self, sql):
            query = str(sql)
            if "n.nspname='auth'" in query and 'has_table_privilege' in query:
                return Result([['identity_account_projection_owner', 'users', 'SELECT', self.public]] +
                              ([['identity_account_projection_owner', 'unrelated_vendor_table', 'SELECT', False]] if self.extra_denied else []))
            if "n.nspname='auth'" in query and 'has_column_privilege' in query:
                return Result([['identity_account_projection_owner', 'users', 'id', 'SELECT', self.public]] +
                              ([['identity_account_projection_owner', 'users', 'new_vendor_column', 'SELECT', False],
                                ['identity_account_projection_owner', 'unrelated_vendor_table', 'id', 'SELECT', False]] if self.extra_denied else []))
            return Result([])
    denied = baseline.projection_catalog_snapshot(Connection(False))
    assert denied['projection_auth_effective_tables'] == []
    assert denied['projection_auth_effective_columns'] == []
    before = baseline.projection_catalog_fingerprints(denied)
    assert baseline.projection_catalog_fingerprints(baseline.projection_catalog_snapshot(Connection(False, extra_denied=True))) == before
    after = baseline.projection_catalog_fingerprints(baseline.projection_catalog_snapshot(Connection(True)))
    assert baseline.projection_catalog_fingerprints(baseline.projection_catalog_snapshot(Connection(True, extra_denied=True))) == after
    assert {key for key in before if before[key] != after[key]} == {
        'projection_auth_effective_tables', 'projection_auth_effective_columns'}


def prior_fixture(tmp_path):
    owner = tmp_path/'previous-owner'
    pins = {}
    for name in projection.PREVIOUS_FILES:
        data = subprocess.run(['git', 'show', projection.PREVIOUS_COMMIT+':services/access/identity-migrations/'+name],
                              cwd=projection.ROOT, capture_output=True, check=True).stdout
        path = owner/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        pins[name] = digest(data)
    manifest = {'commit': projection.PREVIOUS_COMMIT, 'sha256': pins}
    (tmp_path/'previous-source.json').write_text(json.dumps(manifest))
    command = [str(projection.PREVIOUS_PYTHON), '-I', '-B', '-c', projection.PREVIOUS_LAUNCHER,
               str(owner), str(projection.ROOT)]
    records = []
    for case in ['previous', 'failure', 'unknown']:
        log = b'retained synthetic launcher log'
        (tmp_path/('previous-'+case+'.log')).write_bytes(log)
        records.append({'case': case, 'command': command[:], 'exit_code': 0,
                        'commit': projection.PREVIOUS_COMMIT, 'head': 'identity_0002', 'log_sha256': digest(log)})
    (tmp_path/'previous-execution.json').write_text(json.dumps(records))
    runner = projection.ProjectionQualification(tmp_path, {})
    runner.sql = lambda *args: [('identity_0002',)]
    runner.passed = lambda *args, **kwargs: None
    return runner, manifest, records


@pytest.mark.parametrize('corruption', [None, 'missing_manifest', 'extra_manifest', 'missing_file', 'extra_file',
                                     'tampered_file', 'self_consistent_tamper', 'launcher', 'interpreter',
                                     'missing_receipt', 'duplicate_receipt', 'log', 'missing_log'])
def test_prior_evidence_requires_exact_committed_files_launcher_and_logs(tmp_path, corruption):
    runner, manifest, records = prior_fixture(tmp_path)
    if corruption == 'missing_manifest': manifest['sha256'].pop('env.py')
    if corruption == 'extra_manifest': manifest['sha256']['extra.py'] = digest(b'extra')
    if corruption == 'missing_file': (tmp_path/'previous-owner/env.py').unlink()
    if corruption == 'extra_file': (tmp_path/'previous-owner/extra.py').write_text('extra')
    if corruption in ('tampered_file', 'self_consistent_tamper'):
        (tmp_path/'previous-owner/env.py').write_bytes(b'changed')
        if corruption == 'self_consistent_tamper': manifest['sha256']['env.py'] = digest(b'changed')
    if corruption == 'launcher': records[0]['command'][4] = 'pass'
    if corruption == 'interpreter': records[0]['command'][0] = '/usr/bin/python3'
    if corruption == 'missing_receipt': records.pop()
    if corruption == 'duplicate_receipt': records.append(records[0])
    if corruption == 'log': (tmp_path/'previous-previous.log').write_bytes(b'tampered log')
    if corruption == 'missing_log': (tmp_path/'previous-previous.log').unlink()
    (tmp_path/'previous-source.json').write_text(json.dumps(manifest))
    (tmp_path/'previous-execution.json').write_text(json.dumps(records))
    if corruption:
        with pytest.raises((AssertionError, FileNotFoundError)): runner.prior_evidence()
    else:
        runner.prior_evidence()


def recorder_fixture(tmp_path, monkeypatch, mutation=None):
    (tmp_path/'versions').mkdir()
    for name, body in [('0001_baseline.py', 'LEGACY_INTEGRATION_SQL = "captured baseline"'),
                       ('0002_actor_registry.py', 'ACTOR_SCHEMA_SQL = "captured actor"'),
                       ('0003_current_account_actor.py', 'PROJECTION_SCHEMA_SQL = "captured projection"')]:
        (tmp_path/'versions'/name).write_text(body+'\n')
    (tmp_path/'identity_baseline.py').write_text('PROJECTION_REFERENCE_SHA256 = None\n')
    (tmp_path/'source-pins.json').write_text('{}')
    monkeypatch.setattr(qualification, 'OWNER', tmp_path)
    baseline = qualification.baseline
    monkeypatch.setattr(baseline, 'preflight', lambda *args: 'clean')
    monkeypatch.setattr(baseline, 'verify_projection_role', lambda *args, **kwargs: None)
    monkeypatch.setattr(baseline, 'source_sql', lambda: [])
    monkeypatch.setattr(baseline, 'verify_catalog', lambda *args: None)
    monkeypatch.setattr(baseline, 'projection_catalog_snapshot', lambda *args: {})
    statements = []
    class Transaction:
        def rollback(self): pass
    class Connection:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def begin(self): return Transaction()
        def exec_driver_sql(self, sql): statements.append(str(sql))
        def execute(self, sql): statements.append(str(sql))
    class Engine:
        def connect(self): return Connection()
        def dispose(self):
            if mutation: (tmp_path/mutation).write_bytes(b'concurrent changed source')
    monkeypatch.setattr(qualification, 'engine', lambda url: Engine())
    runner = qualification.Qualification(tmp_path, {'owner_urls': {'projection_reference': 'synthetic'}})
    return runner, statements


@pytest.mark.parametrize('mutation', ['identity_baseline.py', 'source-pins.json', 'versions/0001_baseline.py',
                                      'versions/0002_actor_registry.py', 'versions/0003_current_account_actor.py'])
def test_projection_recorder_refuses_changed_captured_sources(tmp_path, monkeypatch, mutation):
    runner, statements = recorder_fixture(tmp_path, monkeypatch, mutation)
    with pytest.raises(AssertionError, match='projection_reference_source_changed'):
        runner.record_projection_reference()
    assert statements == ['captured baseline', 'captured actor', 'captured projection']
    assert not (tmp_path/'projection-reference.json').exists()
    assert not (tmp_path/'.projection-reference-recording').exists()


def test_projection_recorder_preserves_helper_and_foreign_temporary(tmp_path, monkeypatch):
    runner, _ = recorder_fixture(tmp_path, monkeypatch)
    helper = (tmp_path/'identity_baseline.py').read_bytes()
    temporary = tmp_path/'.projection-reference-recording'
    temporary.write_bytes(b'foreign retained evidence')
    with pytest.raises(FileExistsError): runner.record_projection_reference()
    assert temporary.read_bytes() == b'foreign retained evidence'
    assert (tmp_path/'identity_baseline.py').read_bytes() == helper
    assert not (tmp_path/'projection-reference.json').exists()


def test_projection_recorder_binds_executed_bytes_without_editing_helper(tmp_path, monkeypatch):
    runner, _ = recorder_fixture(tmp_path, monkeypatch)
    helper = (tmp_path/'identity_baseline.py').read_bytes()
    executed_ddl = (tmp_path/'versions/0003_current_account_actor.py').read_bytes()
    runner.record_projection_reference()
    assert (tmp_path/'identity_baseline.py').read_bytes() == helper
    reference = json.loads((tmp_path/'projection-reference.json').read_text())
    assert reference['migration_sha256'] == digest(executed_ddl)
    assert runner.records[-1]['helper_sha256'] == digest(helper)
    assert runner.records[-1]['pin_update_required'] is True


def test_projection_rollback_snapshot_uses_reader_categories(tmp_path, monkeypatch):
    sentinel = {'projection_auth_effective_columns': [['denied']]}
    monkeypatch.setattr(projection.baseline, 'projection_catalog_snapshot', lambda connection: sentinel)
    class Connection:
        def __enter__(self): return self
        def __exit__(self, *args): pass
    class Engine:
        def connect(self): return Connection()
        def dispose(self): pass
    monkeypatch.setattr(projection, 'engine', lambda url: Engine())
    runner = projection.ProjectionQualification(tmp_path, {'owner_urls': {'failure': 'synthetic'}})
    assert runner.snapshot('failure') is sentinel
