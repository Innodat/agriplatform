"""Synthetic offline proof of the copyable candidate; no owner runtime imports."""
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
import hashlib
import hmac
import importlib.util
from importlib.metadata import version
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import traceback

import pytest

BUILDER = Path(__file__).resolve().parents[1]
SOURCE = BUILDER / 'examples/owned-service/command_fingerprint.py'
KEY = bytes(range(32))
OTHER_KEY = bytes(range(32, 64))


def load(path, name='fingerprint_candidate'):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def helper():
    return load(SOURCE)


@pytest.fixture
def command():
    # The consumer has already normalized typed IDs, revisions and dates.
    return {'command_type': 'capture.edit', 'command_version': 1,
            'org_id': '00000000-0000-4000-8000-000000000001',
            'executor_account_id': '00000000-0000-4000-8000-000000000002',
            'payload': {'capture_id': '00000000-0000-4000-8000-000000000003',
                        'expected_revision': '9223372036854775807',
                        'observation_date': '2026-10-22',
                        'answers': [False, ' unchanged é ', 3]}}


def test_independent_jcs_and_hmac_vectors(helper):
    assert version('rfc8785') == '0.1.4'
    vectors = [
        # RFC8785 section 3.2.2 numbers plus section 3.2.2.2 escaping.
        # https://www.rfc-editor.org/rfc/rfc8785.html#section-3.2.2
        ({'numbers': [333333333.33333329, 1E30, 4.50, 2e-3, 1e-27]},
         b'{"numbers":[333333333.3333333,1e+30,4.5,0.002,1e-27]}'),
        ({'string': '\x0f\b\t\n\f\r"\\/'},
         br'{"string":"\u000f\b\t\n\f\r\"\\/"}'),
        ({'z': 1, 'a': [True, 2]}, b'{"a":[true,2],"z":1}'),
        ({'small': 0.000001, 'n': 1e30, 'negative_zero': -0.0},
         b'{"n":1e+30,"negative_zero":0,"small":0.000001}'),
        ({'\ue000': 2, '\U0001f600': 1}, '{"\U0001f600":1,"\ue000":2}'.encode()),
        ({'n': [2**53 - 1, -(2**53 - 1)], 's': 'é e\u0301'},
         '{"n":[9007199254740991,-9007199254740991],"s":"é e\u0301"}'.encode()),
    ]
    for document, canonical in vectors:
        stored = helper.create_fingerprint(document, key_id='old_key-1', key=KEY)
        assert stored.digest == hmac.digest(KEY, canonical, 'sha256')
        assert len(stored.digest) == 32
        assert (stored.version, stored.algorithm, stored.key_id) == (1, 'hmac-sha256', 'old_key-1')
        assert helper.verify_fingerprint(document, stored, keys={'old_key-1': KEY})
    assert helper.create_fingerprint({'s': 'é'}, key_id='a', key=KEY).digest != helper.create_fingerprint({'s': 'e\u0301'}, key_id='a', key=KEY).digest


def test_reordered_command_and_every_changed_meaning(helper, command, monkeypatch):
    stored = helper.create_fingerprint(command, key_id='old', key=KEY)
    original = deepcopy(command)
    calls = []
    real_compare = hmac.compare_digest
    monkeypatch.setattr(hmac, 'compare_digest', lambda a, b: (calls.append((len(a), len(b))), real_compare(a, b))[1])
    reordered = dict(reversed(list(command.items())))
    reordered['payload'] = dict(reversed(list(command['payload'].items())))
    assert helper.verify_fingerprint(reordered, stored, keys={'old': KEY})
    for field, value in [
        ('command_type', 'capture.create'), ('command_version', 2),
        ('org_id', '00000000-0000-4000-8000-000000000004'),
        ('executor_account_id', '00000000-0000-4000-8000-000000000005'),
    ]:
        changed = deepcopy(command)
        changed[field] = value
        assert not helper.verify_fingerprint(changed, stored, keys={'old': KEY})
    for replacement in [[3, ' unchanged é ', False], [False, 'changed', 3]]:
        changed = deepcopy(command)
        changed['payload']['answers'] = replacement
        assert not helper.verify_fingerprint(changed, stored, keys={'old': KEY})
    assert calls == [(32, 32)] * 7
    assert command == original
    with pytest.raises(FrozenInstanceError):
        stored.key_id = 'new'
    assert repr(stored) == '<CommandFingerprint redacted>'
    assert str(stored) == repr(stored)
    assert not hasattr(stored, 'key')


def test_rotation_reconstructed_process_and_wrong_retained_key(helper, command):
    old = helper.create_fingerprint(command, key_id='old', key=KEY)
    new = helper.create_fingerprint(command, key_id='new', key=OTHER_KEY)
    restarted = load(SOURCE, 'fingerprint_restarted')
    retained = restarted.CommandFingerprint(version=old.version, algorithm=old.algorithm,
                                             key_id=old.key_id, digest=old.digest)
    assert restarted.verify_fingerprint(command, retained, keys={'old': KEY, 'new': OTHER_KEY})
    assert helper.verify_fingerprint(command, new, keys={'old': KEY, 'new': OTHER_KEY})
    assert not helper.verify_fingerprint(command, old, keys={'old': OTHER_KEY, 'new': OTHER_KEY})
    assert (old.version, old.algorithm, old.key_id, old.digest) == (1, 'hmac-sha256', 'old', retained.digest)


@pytest.mark.parametrize('changes', [
    {'version': 2}, {'version': True}, {'version': '1'}, {'algorithm': 'sha256'},
    {'algorithm': None}, {'key_id': ''}, {'key_id': 'x'*65}, {'key_id': 'é'},
    {'key_id': 'old\n'}, {'key_id': '../old'}, {'digest': b'x'*31},
    {'digest': bytearray(32)}, {'digest': b'x'*33}, {'digest': 'sensitive-digest'},
])
def test_malformed_stored_metadata_refuses_without_mutation(helper, command, changes):
    stored = replace(helper.create_fingerprint(command, key_id='old', key=KEY), **changes)
    before = (stored.version, stored.algorithm, stored.key_id, stored.digest)
    with pytest.raises(helper.FingerprintError, match='^operation_verification_unavailable$'):
        helper.verify_fingerprint(command, stored, keys={'old': KEY})
    assert before == (stored.version, stored.algorithm, stored.key_id, stored.digest)


@pytest.mark.parametrize('keys', [{}, {'new': OTHER_KEY}, {'old': b'secret'}, {'old': bytearray(32)}, None])
def test_missing_or_bad_recorded_key_never_falls_back(helper, command, keys):
    stored = helper.create_fingerprint(command, key_id='old', key=KEY)
    with pytest.raises(helper.FingerprintError, match='^operation_verification_unavailable$'):
        helper.verify_fingerprint(command, stored, keys=keys)
    with pytest.raises(helper.FingerprintError, match='^operation_verification_unavailable$'):
        helper.verify_fingerprint(command, {'digest': 'sensitive'}, keys={'old': KEY})


@pytest.mark.parametrize('value', [b'sensitive', bytearray(1), (1, 2), {1}, object(),
    '\0sensitive', '\ud800sensitive', '\udfff', float('nan'), float('inf'),
    -float('inf'), 2**53, -(2**53), {1: 'sensitive'}, {'bad\0': 1}, {'\ud800': 1}])
def test_invalid_json_is_bounded_and_redacted(helper, value):
    with pytest.raises(helper.FingerprintError, match='^invalid_fingerprint_input$') as error:
        helper.create_fingerprint({'payload': value}, key_id='old', key=KEY)
    assert repr(error.value) == "FingerprintError('invalid_fingerprint_input')"
    stored = helper.create_fingerprint({}, key_id='old', key=KEY)
    with pytest.raises(helper.FingerprintError, match='^invalid_fingerprint_input$'):
        helper.verify_fingerprint({'payload': value}, stored, keys={'old': KEY})



@pytest.mark.parametrize('document', [None, [], 'text', 1, 1.5, True])
def test_non_object_roots_are_rejected(helper, document):
    with pytest.raises(helper.FingerprintError, match='^invalid_fingerprint_input$'):
        helper.create_fingerprint(document, key_id='old', key=KEY)


def test_custom_containers_and_numeric_subclasses_are_rejected(helper):
    class CustomDict(dict):
        pass
    class CustomList(list):
        pass
    class CustomInt(int):
        pass
    class CustomFloat(float):
        pass
    for document in [CustomDict(), {'payload': CustomDict()},
                     {'payload': CustomList()}, {'payload': CustomInt(1)},
                     {'payload': CustomFloat(1.5)}]:
        with pytest.raises(helper.FingerprintError, match='^invalid_fingerprint_input$'):
            helper.create_fingerprint(document, key_id='old', key=KEY)


def test_canonicalizer_exception_traceback_is_sanitized(helper, monkeypatch):
    canary = 'sensitive-canonicalizer-canary'
    stored = helper.create_fingerprint({}, key_id='old', key=KEY)
    def fail(document):
        raise helper.rfc8785.CanonicalizationError(canary)
    monkeypatch.setattr(helper.rfc8785, 'dumps', fail)
    for operation in [lambda: helper.create_fingerprint({}, key_id='old', key=KEY),
                      lambda: helper.verify_fingerprint({}, stored, keys={'old': KEY})]:
        with pytest.raises(helper.FingerprintError, match='^invalid_fingerprint_input$') as error:
            operation()
        rendered = ''.join(traceback.format_exception(error.value))
        assert canary not in rendered
        assert 'CanonicalizationError' not in rendered
        assert error.value.__suppress_context__


def test_cyclic_and_excessively_deep_inputs_fail_safely(helper):
    cyclic = []
    cyclic.append(cyclic)
    deep = []
    for _ in range(2000):
        deep = [deep]
    for value in [cyclic, deep]:
        with pytest.raises(helper.FingerprintError, match='^invalid_fingerprint_input$'):
            helper.create_fingerprint({'payload': value}, key_id='old', key=KEY)
    # Repeated references without a cycle are ordinary JSON values.
    shared = [1]
    assert helper.create_fingerprint({'payload': [shared, shared]}, key_id='old', key=KEY)


@pytest.mark.parametrize('key_id,key', [('', KEY), ('x'*65, KEY), ('bad\n', KEY),
    ('é', KEY), ('../bad', KEY), ('old', b''), ('old', b'x'*31),
    ('old', b'x'*33), ('old', bytearray(32)), ('old', 'sensitive')])
def test_bad_creation_material_has_safe_unavailable_error(helper, key_id, key):
    with pytest.raises(helper.FingerprintError, match='^operation_verification_unavailable$'):
        helper.create_fingerprint({}, key_id=key_id, key=key)



def run_installer(command):
    try:
        result = subprocess.run(command, capture_output=True, timeout=10)
    except subprocess.TimeoutExpired:
        pytest.fail('fingerprint_fixture_process_timeout: limit_seconds=10', pytrace=False)
    except OSError as error:
        pytest.fail(f'fingerprint_fixture_process_start_failed: errno={error.errno}', pytrace=False)
    if result.returncode:
        # Child emits only an allowlisted stage/code; never dump arbitrary output.
        context = result.stderr[-256:].decode('ascii', errors='replace')
        marker = re.search(r'^fingerprint_fixture_(import|scaffold):([a-z_]{1,64})$',
                           context, re.MULTILINE)
        stage, code = marker.groups() if marker else ('process', 'exit_failed')
        pytest.fail(f'fingerprint_fixture_{stage}:{code}; exit={result.returncode}; '
                    f'stdout_bytes={len(result.stdout)}; stderr_bytes={len(result.stderr)}',
                    pytrace=False)


@pytest.mark.parametrize('outcome,expected', [
    (subprocess.TimeoutExpired('synthetic', 10, stderr=b'sensitive-canary'), 'process_timeout'),
    (OSError(2, 'sensitive-canary'), 'process_start_failed: errno=2'),
    (subprocess.CompletedProcess([], 1, b'sensitive-canary', b'fingerprint_fixture_import:module_load_failed\n'), 'import:module_load_failed'),
    (subprocess.CompletedProcess([], 1, b'', b'fingerprint_fixture_scaffold:scaffold_conflict\n'), 'scaffold:scaffold_conflict'),
    (subprocess.CompletedProcess([], -9, b'sensitive-canary'*1000, b'sensitive-canary'*1000), 'process:exit_failed'),
])
def test_installer_failures_are_bounded_and_classified(monkeypatch, outcome, expected):
    def run(command, **kwargs):
        assert kwargs == {'capture_output': True, 'timeout': 10}
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome
    monkeypatch.setattr(subprocess, 'run', run)
    with pytest.raises(pytest.fail.Exception) as error:
        run_installer(['synthetic-node'])
    assert expected in str(error.value)
    assert 'sensitive-canary' not in str(error.value)
    assert len(str(error.value)) < 200


def test_existing_installer_copies_executes_and_preserves_owner_bytes(tmp_path):
    node = os.environ.get('FINGERPRINT_TEST_NODE')
    assert node and Path(node).is_file(), 'FINGERPRINT_TEST_NODE must name the explicit prepared Node binary'
    source = tmp_path / 'candidate'
    source.mkdir()
    initial = SOURCE.read_bytes()
    (source / SOURCE.name).write_bytes(initial)
    output = tmp_path / 'owner'
    script = tmp_path / 'install.mjs'
    script.write_text('''let installer;
try { installer = await import(INSTALLER); }
catch { console.error('fingerprint_fixture_import:module_load_failed'); process.exit(1); }
const [repositoryRoot,output]=process.argv.slice(2);
try {
installer.installScaffold(output,{'base.txt':{classification:'generated',content:'base'}},
 {generator:'builder-v1',template:'application-v1-candidate',recipe:'a'.repeat(64),source:'b'.repeat(64)},
 undefined,{repositoryRoot,declarations:[{source:'candidate',destination:'api/custom'}]});
installer.checkScaffold(output);
} catch (error) {
 const code = /^scaffold_[a-z_]{1,48}$/.test(error?.message) ? error.message : 'scaffold_failed';
 console.error('fingerprint_fixture_scaffold:' + code); process.exit(1);
}
'''.replace('INSTALLER', json.dumps((BUILDER / 'src/scaffold-install.ts').as_uri())))
    def install():
        run_installer([node, str(script), str(tmp_path), str(output)])
    install()
    copied = output / 'api/custom' / SOURCE.name
    assert copied.read_bytes() == initial
    installed = load(copied, 'installed_candidate')
    stored = installed.create_fingerprint({'payload': [False, 'é']}, key_id='old', key=KEY)
    assert installed.verify_fingerprint({'payload': [False, 'é']}, stored, keys={'old': KEY})
    assert not installed.verify_fingerprint({'payload': ['é', False]}, stored, keys={'old': KEY})
    assert stored.digest == hmac.digest(KEY, '{"payload":[false,"é"]}'.encode(), 'sha256')
    rotated = installed.create_fingerprint({'payload': [False, 'é']}, key_id='new', key=OTHER_KEY)
    assert installed.verify_fingerprint({'payload': [False, 'é']}, stored, keys={'old': KEY, 'new': OTHER_KEY})
    assert installed.verify_fingerprint({'payload': [False, 'é']}, rotated, keys={'old': KEY, 'new': OTHER_KEY})
    with pytest.raises(installed.FingerprintError, match='^operation_verification_unavailable$'):
        installed.verify_fingerprint({'payload': [False, 'é']}, stored, keys={'new': OTHER_KEY})
    provenance = (output / '.generated-files.json').read_bytes()
    manifest = json.loads(provenance)
    assert manifest['extensions']['imports'][0]['files'][SOURCE.name] == hashlib.sha256(initial).hexdigest()
    owner = initial + b'\n# Owner-maintained extension\nOWNER_EXTENSION = True\n'
    copied.write_bytes(owner)
    (output / 'api/custom/owner.txt').write_text('owner addition')
    (source / SOURCE.name).unlink()
    source.rmdir()
    install()
    assert copied.read_bytes() == owner
    assert (output / '.generated-files.json').read_bytes() == provenance
    assert (output / 'api/custom/owner.txt').read_text() == 'owner addition'
    edited = load(copied, 'owner_edited_candidate')
    reconstructed = edited.CommandFingerprint(version=stored.version, algorithm=stored.algorithm,
                                               key_id=stored.key_id, digest=stored.digest)
    assert edited.OWNER_EXTENSION
    assert edited.verify_fingerprint({'payload': [False, 'é']}, reconstructed, keys={'old': KEY})
