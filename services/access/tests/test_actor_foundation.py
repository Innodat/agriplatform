"""Focused provenance/launcher checks; real structural and contention tests are synthetic owner qualification."""
from pathlib import Path
import importlib.util
import subprocess
import sys
from types import SimpleNamespace
import pytest

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))
spec = importlib.util.spec_from_file_location('actor_qualification', TESTS/'qualify_actor_foundation.py')
qualification = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qualification)


@pytest.mark.parametrize('alteration', [None, 'source', 'extra'])
def test_previous_sources_are_anchored_to_actual_commit(tmp_path, alteration):
    owner = tmp_path/'previous-owner'
    for name in qualification.PREVIOUS_FILES:
        target = owner/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(subprocess.run(
            ['git', 'show', qualification.PREVIOUS_COMMIT+':services/access/identity-migrations/'+name],
            cwd=qualification.ROOT, capture_output=True, check=True).stdout)
    # A self-supplied manifest cannot authorize different owner bytes.
    (tmp_path/'previous-source.json').write_text('{"commit":"self-approved","sha256":{}}')
    if alteration == 'source':
        (owner/'env.py').write_text('raise RuntimeError("untrusted")')
    elif alteration == 'extra':
        (owner/'versions/0002_untrusted.py').write_text('pass')
    runner = qualification.ActorQualification(tmp_path, {})
    if alteration:
        with pytest.raises(AssertionError):
            runner.previous_sources()
    else:
        assert set(runner.previous_sources()) == set(qualification.PREVIOUS_FILES)


def test_previous_release_launcher_is_committed_and_keeps_credentials_in_environment(tmp_path, monkeypatch):
    url = 'postgresql://identity_migrator:private-fixture@127.0.0.1:5432/synthetic'
    runner = qualification.ActorQualification(tmp_path, {'owner_urls': {'previous': url}})
    monkeypatch.setattr(runner, 'previous_sources', lambda: {'env.py': 'trusted'})
    monkeypatch.setattr(runner, 'record', lambda *args, **kwargs: None)
    calls = []
    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        return SimpleNamespace(returncode=0, stdout=b'', stderr=b'')
    monkeypatch.setattr(qualification.subprocess, 'run', run)
    runner.previous_upgrade('previous')
    argv, options = calls[0]
    assert argv[1:5] == ['-I', '-B', '-c', qualification.PREVIOUS_LAUNCHER]
    assert all('private-fixture' not in arg for arg in argv)
    assert options['env']['IDENTITY_MIGRATION_DATABASE_URL'] == url.replace('postgresql://', 'postgresql+psycopg://', 1)
    assert options['timeout'] == 90
    assert not (tmp_path/'previous-upgrade.py').exists()
