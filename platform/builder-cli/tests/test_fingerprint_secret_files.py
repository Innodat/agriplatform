"""Retained synthetic filesystem proof, requiring actual mapped UID/GID 10001."""
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback

import pytest

BUILDER = Path(__file__).resolve().parents[1]
SOURCE = BUILDER / 'examples/owned-service'
PROCESS = Path(__file__).with_name('secret_files_process.py')


def safe_check(condition, code):
    if not condition:
        pytest.fail(code, pytrace=False)


def child(command):
    result = None
    failure = None
    try:
        result = subprocess.run(command, capture_output=True, timeout=10)
    except subprocess.TimeoutExpired:
        failure = 'secret_fixture_process_timeout'
    except OSError:
        failure = 'secret_fixture_process_start_failed'
    if failure:
        pytest.fail(failure, pytrace=False)
    return result


def load(source=SOURCE):
    # Copied sibling imports execute through the same owner module search path.
    sys.modules.pop('command_fingerprint', None)
    sys.path.insert(0, str(source))
    try:
        spec = importlib.util.spec_from_file_location('fingerprint_secret_files', source / 'fingerprint_secret_files.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


@pytest.fixture
def helper():
    return load()


@pytest.fixture
def run():
    assert os.geteuid() == os.getegid() == 10001, 'run in the explicit UID/GID10001 namespace'
    root = os.environ.get('SECRET_TEST_RUN_ROOT')
    assert root and Path(root).is_absolute(), 'explicit SECRET_TEST_RUN_ROOT required'
    approved = BUILDER.parent / 'deployment/.local/write-secret-files-20261022'
    assert Path(root).resolve().is_relative_to(approved.resolve()), 'synthetic proof root must be ignored ENV run'
    Path(root).mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix='case-', dir=root))
    (directory / 'namespace.json').write_text(json.dumps({
        'uid': os.getuid(), 'euid': os.geteuid(), 'gid': os.getgid(), 'egid': os.getegid(),
        'uid_map': Path('/proc/self/uid_map').read_text(),
        'gid_map': Path('/proc/self/gid_map').read_text()}))
    return directory


@pytest.fixture
def store(run):
    directory = run / 'secrets/fingerprints'
    directory.mkdir(parents=True, mode=0o700)
    directory.chmod(0o700)
    return directory


def write_key(store, filename_id='old', **changes):
    doc = {'schema_version': 1, 'owner_id': 'kdg_capture', 'environment_id': 'synthetic-ci',
           'key_id': filename_id, 'key_b64': base64.b64encode(os.urandom(32)).decode('ascii')}
    doc.update(changes)
    path = store / (filename_id + '.json')
    path.write_text(json.dumps(doc))
    path.chmod(0o400)
    return path


def config(helper, store, active='old'):
    return helper.SecretFileConfig(active, str(store), 'synthetic-ci', 'kdg_capture')


def refuse(helper, operation):
    with pytest.raises(helper.FingerprintError, match='^operation_verification_unavailable$') as error:
        operation()
    assert error.value.__context__ is None
    assert error.value.__cause__ is None
    assert str(error.value) == 'operation_verification_unavailable'
    return error.value


def test_protected_active_material_executes_existing_helper(helper, store):
    path = write_key(store)
    before = path.read_bytes(), path.stat()
    material = helper.load_active(config(helper, store))
    assert repr(material) == '<FingerprintSecret redacted>'
    assert repr(config(helper, store)) == '<SecretFileConfig redacted>'
    fingerprint = sys.modules['command_fingerprint']
    stored = fingerprint.create_fingerprint({'answer': True}, key_id=material.key_id, key=material.key)
    safe_check(fingerprint.verify_fingerprint({'answer': True}, stored, keys={material.key_id: material.key}),
               'secret_fixture_fingerprint_verification_failed')
    safe_check((path.read_bytes(), path.stat()) == before, 'secret_fixture_original_changed')
    assert path.stat().st_uid == path.stat().st_gid == store.stat().st_uid == store.stat().st_gid == 10001


@pytest.mark.parametrize('field,value', [('active_key_id','../old'), ('active_key_id','é'),
    ('active_key_id','a'*65), ('active_key_id',''), ('owner_id','other'),
    ('environment_id',''), ('environment_id','a'*129), ('environment_id','bad\n'),
    ('secret_dir','relative'), ('secret_dir','/a/../b'), ('secret_dir','/a//b'),
    ('secret_dir','/a/'), ('secret_dir','/a\0'), ('secret_dir','/a\n'),
    ('secret_dir','/a\ud800')])
def test_configuration_is_explicit_closed_and_bounded(helper, store, field, value):
    args = dict(active_key_id='old', secret_dir=str(store), environment_id='synthetic-ci', owner_id='kdg_capture')
    args[field] = value
    refuse(helper, lambda: helper.SecretFileConfig(**args))


@pytest.mark.parametrize('changes', [{'schema_version':True}, {'schema_version':2},
    {'owner_id':'other'}, {'environment_id':'SYNTHETIC-CI'}, {'key_id':'new'},
    {'key_b64':'bad'}, {'key_b64':base64.b64encode(b'x'*31).decode()},
    {'key_b64':base64.b64encode(b'x'*33).decode()}, {'key_b64':None},
    {'key_b64':base64.b64encode(b'x'*32).decode()+'\n'}, {'unknown':'canary'}])
def test_schema_namespace_and_material_refuse_without_repair(helper, store, changes):
    path = write_key(store, **changes)
    before = path.read_bytes(), path.stat()
    refuse(helper, lambda: helper.load_active(config(helper, store)))
    safe_check((path.read_bytes(), path.stat()) == before, 'secret_fixture_original_changed')


@pytest.mark.parametrize('raw', [b'', b'\xff', b'{"key_b64":"sensitive-canary",}',
    b'[]', b'null', b'{"schema_version":1,"schema_version":1}', b'{'*2000,
    b' '*4097])
def test_invalid_document_is_bounded_and_exception_chain_has_no_content(helper, store, raw):
    path = store / 'old.json'
    path.write_bytes(raw)
    path.chmod(0o400)
    error = refuse(helper, lambda: helper.load_active(config(helper, store)))
    rendered = ''.join(traceback.format_exception(error))
    safe_check('sensitive-canary' not in rendered, 'secret_fixture_exception_content_leaked')
    safe_check('JSONDecodeError' not in rendered, 'secret_fixture_json_exception_leaked')
    safe_check('UnicodeDecodeError' not in rendered, 'secret_fixture_unicode_exception_leaked')


def test_noncanonical_base64_padding_bits_are_rejected(helper, store):
    path = write_key(store)
    doc = json.loads(path.read_text())
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    encoded = doc['key_b64']
    doc['key_b64'] = encoded[:-2] + alphabet[alphabet.index(encoded[-2]) + 1] + '='
    safe_check(base64.b64decode(doc['key_b64']) == base64.b64decode(encoded),
               'secret_fixture_base64_equivalence_failed')
    path.chmod(0o600)
    path.write_text(json.dumps(doc))
    path.chmod(0o400)
    refuse(helper, lambda: helper.load_active(config(helper, store)))


@pytest.mark.parametrize('kind', ['symlink', 'fifo', 'directory', 'device'])
def test_nonregular_files_never_block_or_follow(helper, store, monkeypatch, kind):
    path = store / 'old.json'
    if kind == 'symlink':
        target = write_key(store, 'target')
        path.symlink_to(target)
    elif kind == 'fifo':
        os.mkfifo(path, 0o400)
    elif kind == 'directory':
        path.mkdir(mode=0o400)
    else:
        original = helper.os.open
        def open_device(name, flags, **kwargs):
            if name == 'old.json':
                return original('/dev/null', flags)
            return original(name, flags, **kwargs)
        monkeypatch.setattr(helper.os, 'open', open_device)
    refuse(helper, lambda: helper.load_active(config(helper, store)))


@pytest.mark.parametrize('target,mode', [('directory',0o750), ('directory',0o1700),
    ('file',0o600), ('file',0o440), ('file',0o1400)])
def test_exact_modes_are_required(helper, store, target, mode):
    path = write_key(store)
    (store if target == 'directory' else path).chmod(mode)
    refuse(helper, lambda: helper.load_active(config(helper, store)))
    assert ((store if target == 'directory' else path).stat().st_mode & 0o7777) == mode


def test_symlink_directory_components_are_rejected(helper, store, run):
    write_key(store)
    link = run / 'alias'
    link.symlink_to(store.parent, target_is_directory=True)
    refuse(helper, lambda: helper.load_active(config(helper, link / 'fingerprints')))
    leaf = run / 'leaf'
    leaf.symlink_to(store, target_is_directory=True)
    refuse(helper, lambda: helper.load_active(config(helper, leaf)))


@pytest.mark.parametrize('kind', ['uid', 'gid', 'directory_owner', 'file_owner'])
def test_wrong_identity_and_actual_unmapped_owner(helper, store, monkeypatch, kind):
    write_key(store)
    if kind in ('uid', 'gid'):
        monkeypatch.setattr(helper.os, 'geteuid' if kind == 'uid' else 'getegid', lambda: 10002)
        refuse(helper, lambda: helper.load_active(config(helper, store)))
    elif kind == 'directory_owner':
        # Actual host-root ownership appears unmapped in this namespace.
        assert Path('/etc').stat().st_uid != 10001
        refuse(helper, lambda: helper.load_active(config(helper, Path('/etc'))))
    else:
        # Redirect only the filename open to a real foreign-owned descriptor;
        # fstat and permission/ownership validation execute without substitution.
        assert Path('/etc/passwd').stat().st_uid != 10001
        original = helper.os.open
        def open_file(path, flags, **kwargs):
            if path == 'old.json':
                return original('/etc/passwd', flags)
            return original(path, flags, **kwargs)
        monkeypatch.setattr(helper.os, 'open', open_file)
        refuse(helper, lambda: helper.load_active(config(helper, store)))


def process(source, store, receipt, action, active='old'):
    result = child([sys.executable, '-I', '-B', str(PROCESS), str(source), str(store),
                    str(receipt), action, active])
    safe_check(result.stdout in (b'', b'secret_fixture:ok\n'), 'secret_fixture_unexpected_stdout')
    safe_check(result.stderr in (b'', b'secret_fixture:refused\n'), 'secret_fixture_unexpected_stderr')
    return result.returncode


def test_separate_process_restart_rotation_old_active_configuration_overlap_and_missing_key(helper, store, run):
    old = write_key(store)
    receipt = run / 'retained-outcome.json'
    assert process(SOURCE, store, receipt, 'create') == 0
    original = receipt.read_bytes()
    assert process(SOURCE, store, receipt, 'verify') == 0
    write_key(store, 'new')
    assert process(SOURCE, store, receipt, 'verify', 'new') == 0
    assert process(SOURCE, store, receipt, 'verify', 'old') == 0
    newer = run / 'new-outcome.json'
    assert process(SOURCE, store, newer, 'create', 'new') == 0
    safe_check(json.loads(newer.read_text())['key_id'] == 'new', 'secret_fixture_active_selection_wrong')
    assert process(SOURCE, store, newer, 'verify', 'old') == 0
    retained = old.read_bytes()
    old.rename(store / 'retained-old.private')
    assert process(SOURCE, store, receipt, 'verify', 'new') == 1
    assert process(SOURCE, store, run / 'absent.json', 'create') == 1
    safe_check(receipt.read_bytes() == original, 'secret_fixture_outcome_changed')
    # Wrong bytes never become a match and do not mutate retained outcomes.
    write_key(store)
    assert process(SOURCE, store, receipt, 'verify', 'new') == 1
    safe_check(receipt.read_bytes() == original, 'secret_fixture_outcome_changed')
    old.chmod(0o600)
    old.write_bytes(retained)
    old.chmod(0o400)
    assert process(SOURCE, store, receipt, 'verify', 'new') == 0


def test_missing_invalid_ids_and_no_directory_scan(helper, store, monkeypatch):
    write_key(store)
    # Invalid unrelated files are never scanned or read.
    (store / 'unrelated.json').write_text('sensitive-canary')
    monkeypatch.setattr(os, 'listdir', lambda *args: pytest.fail('directory scan forbidden'))
    assert helper.load_active(config(helper, store))
    for key_id in ['../old', '', 'é', 'a'*65, 'missing']:
        refuse(helper, lambda: helper.load_verification(config(helper, store), key_id))


def test_real_installer_copies_siblings_and_preserves_edits_and_provenance(helper, store, run):
    node = os.environ.get('FINGERPRINT_TEST_NODE')
    assert node and Path(node).is_file(), 'explicit prepared Node required'
    source = run / 'candidate'
    source.mkdir()
    for name in ['command_fingerprint.py', 'fingerprint_secret_files.py']:
        (source / name).write_bytes((SOURCE / name).read_bytes())
    output = run / 'owner'
    script = run / 'install.mjs'
    script.write_text('''import {installScaffold,checkScaffold} from INSTALLER;
const [repositoryRoot,output]=process.argv.slice(2);
try {
installScaffold(output,{'base.txt':{classification:'generated',content:'base'}},
 {generator:'builder-v1',template:'application-v1-candidate',recipe:'a'.repeat(64),source:'b'.repeat(64)},
 undefined,{repositoryRoot,declarations:[{source:'candidate',destination:'api/custom'}]});
checkScaffold(output);
} catch { console.error('secret_fixture:refused'); process.exit(1); }
'''.replace('INSTALLER', json.dumps((BUILDER / 'src/scaffold-install.ts').as_uri())))
    def install():
        result = child([node, str(script), str(run), str(output)])
        safe_check(result.returncode == 0, 'secret_fixture_installer_refused')
    install()
    copied = output / 'api/custom'
    provenance = (output / '.generated-files.json').read_bytes()
    manifest = json.loads(provenance)
    for name in ['command_fingerprint.py', 'fingerprint_secret_files.py']:
        safe_check((copied / name).read_bytes() == (source / name).read_bytes(), 'secret_fixture_copied_bytes_changed')
        safe_check(manifest['extensions']['imports'][0]['files'][name] == hashlib.sha256((source / name).read_bytes()).hexdigest(), 'secret_fixture_provenance_hash_changed')
    write_key(store)
    receipt = run / 'copied-outcome.json'
    assert process(copied, store, receipt, 'create') == 0
    assert process(copied, store, receipt, 'verify') == 0
    edited = copied / 'fingerprint_secret_files.py'
    edited.write_bytes(edited.read_bytes() + b'\n# Owner-maintained extension\nOWNER_EXTENSION = True\n')
    owner_bytes = edited.read_bytes()
    (copied / 'owner.txt').write_text('owner addition')
    for item in source.iterdir():
        item.unlink()
    source.rmdir()
    install()
    safe_check(edited.read_bytes() == owner_bytes, 'secret_fixture_owner_bytes_changed')
    assert (copied / 'owner.txt').read_text() == 'owner addition'
    safe_check((output / '.generated-files.json').read_bytes() == provenance, 'secret_fixture_provenance_changed')
    assert load(copied).OWNER_EXTENSION
    assert process(copied, store, receipt, 'verify') == 0


def test_descriptor_read_detects_replacement_and_keeps_read_budget(helper, store, monkeypatch):
    path = write_key(store)
    original = helper.os.read
    total = 0
    def read_and_replace(fd, size):
        nonlocal total
        assert 0 < size <= 4097
        value = original(fd, min(size, 17))
        total += len(value)
        if total == 17:
            path.rename(store / 'original-retained.private')
            write_key(store)
        return value
    monkeypatch.setattr(helper.os, 'read', read_and_replace)
    refuse(helper, lambda: helper.load_active(config(helper, store)))
    assert total <= 4097
    assert (store / 'original-retained.private').is_file()


@pytest.mark.parametrize('target,field', [('directory', 'uid'), ('directory', 'gid'),
                                        ('file', 'uid'), ('file', 'gid')])
def test_isolated_wrong_owner_metadata_refuses(helper, store, monkeypatch, target, field):
    path = write_key(store)
    inode = (store if target == 'directory' else path).stat().st_ino
    original = helper.os.fstat
    def wrong_owner(fd):
        info = original(fd)
        if info.st_ino != inode:
            return info
        # All other fields, including kind and the exact approved mode, stay real.
        fields = list(info)
        fields[4 if field == 'uid' else 5] = 10002
        return os.stat_result(fields)
    monkeypatch.setattr(helper.os, 'fstat', wrong_owner)
    refuse(helper, lambda: helper.load_active(config(helper, store)))


@pytest.mark.parametrize('active_state', ['missing', 'malformed'])
def test_recorded_key_verifies_independently_of_unavailable_active(helper, store, run, active_state):
    old = write_key(store)
    receipt = run / 'retained-outcome.json'
    safe_check(process(SOURCE, store, receipt, 'create') == 0, 'secret_fixture_create_failed')
    original = receipt.read_bytes(), old.read_bytes(), old.stat()
    if active_state == 'malformed':
        active = store / 'new.json'
        active.write_bytes(b'{malformed-active')
        active.chmod(0o400)
    selected = config(helper, store, 'new')
    refuse(helper, lambda: helper.load_active(selected))
    safe_check(process(SOURCE, store, receipt, 'verify', 'new') == 0,
               'secret_fixture_recorded_verification_failed')
    safe_check((receipt.read_bytes(), old.read_bytes(), old.stat()) == original,
               'secret_fixture_original_changed')
    safe_check(not (store / 'new.json').exists() if active_state == 'missing'
               else (store / 'new.json').read_bytes() == b'{malformed-active',
               'secret_fixture_active_mutated')


@pytest.mark.parametrize('mutation', ['rewrite', 'truncate'])
def test_chunked_read_rejects_in_place_mutation(helper, store, monkeypatch, mutation):
    path = write_key(store)
    original_bytes = path.read_bytes()
    retained = store / 'original-retained.private'
    retained.write_bytes(original_bytes)
    retained.chmod(0o400)
    original_encoded = json.loads(original_bytes)['key_b64'].encode('ascii')
    decoded = base64.b64decode(original_encoded)
    replacement_key = bytes([decoded[0] ^ 1]) + decoded[1:]
    replacement_encoded = base64.b64encode(replacement_key)
    key_offset = original_bytes.index(original_encoded)
    safe_check(key_offset >= 17 and len(replacement_encoded) == len(original_encoded),
               'secret_fixture_mutation_layout_invalid')
    inode = path.stat().st_ino
    original_read = helper.os.read
    changed = False
    def mutate(fd, size):
        nonlocal changed
        value = original_read(fd, min(size, 17))
        if not changed:
            changed = True
            path.chmod(0o600)
            with path.open('r+b') as writer:
                if mutation == 'rewrite':
                    # Change only still-unread canonical key material. The
                    # namespace/schema and the already-read prefix stay valid.
                    writer.seek(key_offset)
                    writer.write(replacement_encoded)
                else:
                    writer.truncate(20)
            path.chmod(0o400)
        return value
    monkeypatch.setattr(helper.os, 'read', mutate)
    refuse(helper, lambda: helper.load_active(config(helper, store)))
    safe_check(path.stat().st_ino == inode, 'secret_fixture_inode_replaced')
    safe_check(retained.read_bytes() == original_bytes, 'secret_fixture_retained_original_changed')

    if mutation == 'rewrite':
        monkeypatch.setattr(helper.os, 'read', original_read)
        rewritten = path.read_bytes()
        safe_check(len(rewritten) == len(original_bytes) and rewritten[:17] == original_bytes[:17],
                   'secret_fixture_rewrite_shape_changed')
        material = helper.load_active(config(helper, store))
        safe_check(material.key == replacement_key, 'secret_fixture_rewritten_key_invalid')


def test_exact_document_boundary_succeeds(helper, store):
    path = write_key(store)
    content = path.read_bytes()
    path.chmod(0o600)
    path.write_bytes(content + b' ' * (4096 - len(content)))
    path.chmod(0o400)
    safe_check(path.stat().st_size == 4096, 'secret_fixture_boundary_size_wrong')
    safe_check(helper.load_active(config(helper, store)).key_id == 'old',
               'secret_fixture_boundary_load_failed')


def test_read_time_growth_is_bounded(helper, store, monkeypatch):
    path = write_key(store)
    original_bytes = path.read_bytes()
    retained = store / 'original-retained.private'
    retained.write_bytes(original_bytes)
    retained.chmod(0o400)
    original_read = helper.os.read
    total = 0
    grown = False
    def grow(fd, size):
        nonlocal total, grown
        # This hook first executes after the real initial fstat accepted the file.
        if not grown:
            grown = True
            path.chmod(0o600)
            with path.open('ab') as writer:
                writer.write(b' ' * 5000)
            path.chmod(0o400)
        value = original_read(fd, min(size, 17))
        total += len(value)
        return value
    monkeypatch.setattr(helper.os, 'read', grow)
    refuse(helper, lambda: helper.load_active(config(helper, store)))
    safe_check(total == 4097, 'secret_fixture_read_budget_not_enforced')
    safe_check(path.stat().st_size > 4096, 'secret_fixture_growth_not_exercised')
    safe_check(retained.read_bytes() == original_bytes, 'secret_fixture_retained_original_changed')


def test_deliberate_pytest_failures_exclude_child_output_and_material_canaries(run):
    # Actually failing nested pytest cases exercise pytest's rendered report, not
    # just exception strings. pytrace=False keeps arguments/locals out of reports.
    nested = run / 'test_safe_failures.py'
    nested.write_text('''import runpy
import subprocess
import pytest
ns = runpy.run_path(SOURCE)
secret = bytes([83,69,67,82,69,84,95,67,65,78,65,82,89])
digest = bytes([68,73,71,69,83,84,95,67,65,78,65,82,89])
@pytest.mark.parametrize('case', ['secret_equality','digest_equality','stdout','stderr','timeout','start'])
def test_deliberate(case, monkeypatch):
    if case.endswith('equality'):
        left = secret if case == 'secret_equality' else digest
        ns['safe_check'](left == b'different', 'secret_fixture_equality_failed')
    def invoke(*args, **kwargs):
        if case == 'timeout':
            raise subprocess.TimeoutExpired(secret, 10, output=secret, stderr=digest)
        if case == 'start':
            raise OSError(secret)
        return subprocess.CompletedProcess([], 1, secret if case == 'stdout' else b'',
                                           digest if case == 'stderr' else b'')
    monkeypatch.setattr(ns['subprocess'], 'run', invoke)
    ns['process']('public-source','public-dir','public-receipt','verify')
'''.replace('SOURCE', repr(str(Path(__file__).resolve()))))
    result = child([sys.executable, '-I', '-B', '-m', 'pytest', str(nested),
                    '-q', '-p', 'no:cacheprovider'])
    safe_check(result.returncode == 1, 'secret_fixture_canary_probe_not_failed')
    rendered = result.stdout + result.stderr
    safe_check(b'6 failed' in rendered, 'secret_fixture_canary_cases_incomplete')
    for canary in [b'SECRET_CANARY', b'DIGEST_CANARY']:
        safe_check(canary not in rendered, 'secret_fixture_canary_leaked')
    (run / 'safe-failure-rendering.log').write_bytes(rendered)
