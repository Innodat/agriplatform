"""Application-only publication containment; no native fixtures or credentials."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
import corpus_operator as operator
from test_corpus_publication_input import command, encode, source_bytes

OPERATION = '44444444-4444-4444-8444-444444444444'
TARGET = operator.OperatorTarget('local_disposable',
    'postgresql://scribeswell_corpus_operator:fixture@127.0.0.1:1/disposable', 'disposable')


def test_explicit_original_publication_lookup_with_missing_outcome(monkeypatch):
    source = source_bytes()
    seal = encode(command('seal', source))
    calls = []
    def exchange(request, deadline):
        import json
        calls.append(json.loads(request))
        return b'{"receipt":null}'
    monkeypatch.setattr(operator, '_exchange', exchange)
    assert operator.lookup_publication(TARGET, seal, source, operation_id=OPERATION) is None
    assert calls[0]['operation_id'] == OPERATION
    assert calls[0]['version'] == 'publication-v1'

import base64
from dataclasses import asdict
import io
import json
import time
import pytest
from corpus_publish import PublishError, _activation
from corpus_publication_input import parse_command


def inputs():
    source = source_bytes()
    return encode(command('seal', source)), source


def request():
    raw, source = inputs()
    return dict(version='publication-v1', target=asdict(TARGET), lookup=True,
                raw=base64.b64encode(raw).decode(), source=base64.b64encode(source).decode(),
                operation_id=OPERATION)


def receipt():
    raw, _ = inputs()
    activation = _activation(parse_command(raw), OPERATION)
    return dict(version=1, operation_id=OPERATION, command='publication.activate',
                source_revision=activation['source_revision'], source_id='tanakh',
                attempt_id=activation['seal']['payload']['expected_attempt_id'],
                generation=activation['seal']['payload']['expected_generation'],
                executor_actor_id='22222222-2222-4222-8222-222222222222', status='published')


def worker(monkeypatch, payload):
    class Stream:
        def __init__(self, data=b''): self.buffer = io.BytesIO(data)
    stdout = Stream()
    monkeypatch.setattr(operator.sys, 'stdin', Stream(payload))
    monkeypatch.setattr(operator.sys, 'stdout', stdout)
    operator._worker_main()
    return json.loads(stdout.buffer.getvalue())


@pytest.mark.parametrize('field,value', [('operation_id', 'bad'), ('source_revision', OPERATION),
    ('attempt_id', OPERATION), ('generation', '999'), ('status', 'complete'),
    ('version', True), ('source_id', 'other'), ('executor_actor_id', 'bad')])
def test_receipt_must_match_original_activation(field, value, monkeypatch):
    value_receipt = receipt()
    value_receipt[field] = value
    monkeypatch.setattr(operator, '_exchange', lambda *args: json.dumps({'receipt':value_receipt}).encode())
    with pytest.raises(PublishError, match='unknown_outcome') as error:
        operator.publish_closed_attempt(TARGET, *inputs(), operation_id=OPERATION)
    assert error.value.__context__ is None


def test_original_receipt_and_explicit_denial(monkeypatch):
    expected = receipt()
    monkeypatch.setattr(operator, '_exchange', lambda *args: json.dumps({'receipt':expected}).encode())
    result = operator.publish_closed_attempt(TARGET, *inputs(), operation_id=OPERATION)
    assert asdict(result) == expected
    monkeypatch.setattr(operator, '_exchange', lambda *args: b'{"error":"access_denied"}')
    with pytest.raises(PublishError, match='access_denied'):
        operator.lookup_publication(TARGET, *inputs(), operation_id=OPERATION)


@pytest.mark.parametrize('change', ['extra', 'lookup', 'source', 'operation', 'nonseal', 'missing'])
def test_child_validates_before_connection(change, monkeypatch):
    value = request()
    if change == 'extra': value['proof'] = {}
    elif change == 'lookup': value['lookup'] = 1
    elif change == 'source': value['source'] = base64.b64encode(b'invalid').decode()
    elif change == 'operation': value['operation_id'] = 'bad'
    elif change == 'nonseal': value['raw'] = base64.b64encode(encode(command('begin', source_bytes()))).decode()
    else: del value['source']
    monkeypatch.setattr(operator.psycopg, 'connect', lambda *a, **k: pytest.fail('connected'))
    assert 'receipt' not in worker(monkeypatch, json.dumps(value).encode())


@pytest.mark.parametrize("lookup_only", [True, False])
def test_worker_qualifies_and_uses_restricted_connection(monkeypatch, lookup_only):
    import corpus_publish
    calls = []
    class Connection:
        def __enter__(self): return self
        def __exit__(self, *args): pass
    def connect(url, **kwargs):
        calls.append(kwargs)
        return Connection()
    def lookup(connection, raw, source, *, operation_id):
        assert (raw, source) == inputs() and operation_id == OPERATION
        return None
    monkeypatch.setattr(operator.psycopg, 'connect', connect)
    monkeypatch.setattr(corpus_publish, 'lookup_publication' if lookup_only else 'publish_closed_attempt', lookup)
    value = request()
    value['lookup'] = lookup_only
    assert worker(monkeypatch, json.dumps(value).encode()) == {'receipt':None}
    assert calls == [dict(autocommit=True, connect_timeout=5, sslcertmode='disable',
        gssencmode='disable', require_auth='password,md5,scram-sha-256', passfile='/dev/null')]


@pytest.mark.parametrize('response', [b'bad', b'{}', b'{"receipt":null}',
    b'{"error":"secret"}', b'{"receipt":null,"receipt":null}'])
def test_malformed_publish_response_is_unknown(response, monkeypatch):
    monkeypatch.setattr(operator, '_exchange', lambda *a: response)
    with pytest.raises(PublishError, match='unknown_outcome'):
        operator.publish_closed_attempt(TARGET, *inputs(), operation_id=OPERATION)


@pytest.mark.parametrize('mode', ['overflow', 'late', 'qualification', 'environment'])
def test_actual_child_containment(mode, monkeypatch):
    monkeypatch.setattr(operator, '_OPERATION_SECONDS', 1.0)
    monkeypatch.setattr(operator, '_REAP_SECONDS', .2)
    actual = operator._worker_command()
    if mode == 'overflow':
        code = "import sys;sys.stdin.buffer.read();sys.stdout.write('x'*100000)"
    elif mode == 'late':
        code = "import sys,time;sys.stdin.buffer.read();sys.stdout.write('{\"receipt\":null}');sys.stdout.flush();time.sleep(30)"
    elif mode == 'environment':
        monkeypatch.setenv('PGPASSWORD', 'hostile-secret')
        code = "import sys,os;sys.stdin.buffer.read();assert set(os.environ)<={'LANG','LC_CTYPE'};sys.stdout.write('{\"receipt\":null}')"
    else:
        code = actual[-1].replace('from corpus_operator import _worker_main;',
            'import corpus_publish,time;corpus_publish._prepare=lambda *a:time.sleep(30);from corpus_operator import _worker_main;')
    monkeypatch.setattr(operator, '_worker_command', lambda: [sys.executable, '-I', '-c', code])
    launched = []
    popen = operator.subprocess.Popen
    def launch(*a, **k):
        child = popen(*a, **k)
        launched.append(child)
        assert not any('fixture' in part for part in a[0])
        return child
    monkeypatch.setattr(operator.subprocess, 'Popen', launch)
    start = time.monotonic()
    if mode == 'environment':
        assert operator.lookup_publication(TARGET, *inputs(), operation_id=OPERATION) is None
    else:
        with pytest.raises(PublishError, match='unknown_outcome'):
            operator.lookup_publication(TARGET, *inputs(), operation_id=OPERATION)
    assert time.monotonic() - start < 2
    assert len(launched) == 1 and launched[0].poll() is not None


def test_actual_private_protocol_source_failure_precedes_connect():
    raw, _ = inputs()
    with pytest.raises(PublishError, match='input_invalid'):
        operator.publish_closed_attempt(TARGET, raw, b'invalid', operation_id=OPERATION)


def test_invalid_admission_does_not_spawn(monkeypatch):
    monkeypatch.setattr(operator.subprocess, 'Popen', lambda *a, **k: pytest.fail('spawn'))
    for target, operation, raw in [(None, OPERATION, inputs()[0]), (TARGET, 'bad', inputs()[0]),
        (TARGET, OPERATION, b'bad')]:
        with pytest.raises(PublishError, match='input_invalid') as error:
            operator.lookup_publication(target, raw, inputs()[1], operation_id=operation)
        assert error.value.__context__ is None


@pytest.mark.parametrize('code', ['corpus_mismatch', 'deadline_exceeded'])
@pytest.mark.parametrize('boundary', ['worker', 'parent'])
def test_known_publication_failures_preserved(code, boundary, monkeypatch):
    if boundary == 'parent':
        monkeypatch.setattr(operator, '_exchange', lambda *a: json.dumps({'error':code}).encode())
        with pytest.raises(PublishError) as error:
            operator.publish_closed_attempt(TARGET, *inputs(), operation_id=OPERATION)
        assert error.value.code == 'corpus_publish.' + code
    else:
        import corpus_publish
        class Connection:
            def __enter__(self): return self
            def __exit__(self, *args): pass
        monkeypatch.setattr(operator.psycopg, 'connect', lambda *a, **k: Connection())
        def fail(*args, **kwargs): raise PublishError(code)
        monkeypatch.setattr(corpus_publish, 'lookup_publication', fail)
        assert worker(monkeypatch, json.dumps(request()).encode()) == {'error':code}


@pytest.mark.parametrize('lookup_only', [False, True])
def test_successful_original_receipt_through_actual_child(monkeypatch, lookup_only):
    child = operator._worker_command()
    # Fixed test-only stub runs in the isolated child. Actual source qualification,
    # dispatch, serialization, pipe exchange and parent receipt checks stay intact.
    injection = '''
import corpus_operator, corpus_publish
class SyntheticConnection:
    def __enter__(self): return self
    def __exit__(self, *args): pass
corpus_operator.psycopg.connect = lambda *args, **kwargs: SyntheticConnection()
def synthetic_publication(connection, raw, source, *, operation_id):
    assert operation_id == '44444444-4444-4444-8444-444444444444'
    assert corpus_publish._prepare(raw, source, operation_id).command == 'corpus.seal'
    return corpus_publish.PublicationReceipt(**RECEIPT)
corpus_publish.publish_closed_attempt = synthetic_publication
corpus_publish.lookup_publication = synthetic_publication
'''.replace('RECEIPT', repr(receipt()))
    child[-1] = child[-1].replace('from corpus_operator import _worker_main;',
        '\n' + injection + '\nfrom corpus_operator import _worker_main;')
    monkeypatch.setattr(operator, '_worker_command', lambda: child)
    invoke = operator.lookup_publication if lookup_only else operator.publish_closed_attempt
    assert asdict(invoke(TARGET, *inputs(), operation_id=OPERATION)) == receipt()


@pytest.mark.parametrize('invalid', ['source_type', 'source_size', 'command_size', 'nonseal'])
@pytest.mark.parametrize('lookup_only', [False, True])
def test_additional_admission_failures_never_spawn(invalid, lookup_only, monkeypatch):
    raw, source = inputs()
    if invalid == 'source_type': source = bytearray(source)
    elif invalid == 'source_size': source = b'x' * (operator.MAX_SOURCE_BYTES + 1)
    elif invalid == 'command_size': raw = b'x' * (operator.MAX_COMMAND_BYTES + 1)
    else: raw = encode(command('begin', source))
    monkeypatch.setattr(operator.subprocess, 'Popen', lambda *a, **k: pytest.fail('spawn'))
    invoke = operator.lookup_publication if lookup_only else operator.publish_closed_attempt
    with pytest.raises(PublishError) as error:
        invoke(TARGET, raw, source, operation_id=OPERATION)
    assert error.value.code == 'corpus_publish.input_invalid'
    assert error.value.__context__ is None


def test_valid_json_checksum_mismatch_never_connects(monkeypatch):
    value = request()
    # Same valid complete JSON/inventory, different original bytes/checksum.
    changed_source = source_bytes() + b' '
    assert json.loads(changed_source) == json.loads(source_bytes())
    value['source'] = base64.b64encode(changed_source).decode()
    monkeypatch.setattr(operator.psycopg, 'connect', lambda *a, **k: pytest.fail('connected'))
    assert worker(monkeypatch, json.dumps(value).encode()) == {'error':'input_invalid'}
