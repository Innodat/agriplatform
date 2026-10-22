"""Supervised invocation: real restricted caller plus hostile transport cases."""
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit, unquote

import pytest

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP / 'backend'))
import corpus_operator as supervised
from corpus_publication import PublicationError
from test_corpus_publication import (controller_database, enabled, body, counts,
                                     OPERATOR, ACTOR)
from test_corpus_publication_input import source_bytes, encode
from test_postgres_acceptance import role_url


def target_for(url):
    return supervised.OperatorTarget('local_disposable', role_url(url, OPERATOR),
                                     unquote(urlsplit(url).path[1:]))


def test_supervised_transitions_and_original_lookup(enabled):
    admin, url = enabled
    target = target_for(url)
    raw_source = source_bytes()
    def corpus_snapshot():
        return tuple(admin.execute('SELECT to_jsonb(t) FROM scribeswell.' + table + ' t ORDER BY id').fetchall()
                     for table in ('book', 'chapter', 'verse', 'word', 'morpheme'))
    before = corpus_snapshot()
    first = body()
    began = supervised.execute_command(target, encode(first), raw_source)
    recovery = body('recover', began)
    recovered = supervised.execute_command(target, encode(recovery), raw_source)
    seal = body('seal', recovered)
    sealed = supervised.execute_command(target, encode(seal), raw_source)
    assert began.executor_actor_id == recovered.executor_actor_id == sealed.executor_actor_id == ACTOR
    assert recovered.generation == '2' and sealed.state == 'closed'
    for value, receipt in ((first, began), (recovery, recovered), (seal, sealed)):
        assert supervised.lookup_outcome(target, encode(value)) == receipt
    assert supervised.lookup_outcome(target, encode(body())) is None
    assert counts(admin) == (1, 2, 3, 0)
    assert raw_source == source_bytes()
    assert corpus_snapshot() == before


def test_committed_response_lost_then_explicit_reconciliation(enabled, monkeypatch):
    admin, url = enabled
    target = target_for(url)
    value = body()
    original = supervised._worker_command
    command = original()
    # Execute the real adapter and COMMIT but deliberately discard its stdout.
    command[-1] = command[-1].replace('from corpus_operator import _worker_main;',
        "import os; sys.stdout = open(os.devnull, 'w'); from corpus_operator import _worker_main;")
    monkeypatch.setattr(supervised, '_worker_command', lambda: command)
    with pytest.raises(PublicationError, match='unknown_outcome'):
        supervised.execute_command(target, encode(value), source_bytes())
    assert counts(admin) == (1, 1, 1, 0)
    monkeypatch.setattr(supervised, '_worker_command', original)
    receipt = supervised.lookup_outcome(target, encode(value))
    assert receipt is not None and receipt.operation_id == value['operation_id']
    assert counts(admin) == (1, 1, 1, 0)


def test_lookup_rechecks_revocation(enabled):
    admin, url = enabled
    target = target_for(url)
    value = body()
    supervised.execute_command(target, encode(value), source_bytes())
    admin.execute('UPDATE scribeswell.corpus_operator_authority SET enabled=false,revision=revision+1')
    with pytest.raises(PublicationError, match='access_denied') as error:
        supervised.lookup_outcome(target, encode(value))
    assert error.value.__context__ is None


LOCAL = supervised.OperatorTarget('local_disposable',
    'postgresql://scribeswell_corpus_operator:fixture@127.0.0.1:5432/disposable', 'disposable')


@pytest.mark.parametrize('target', [
    supervised.OperatorTarget('other', LOCAL.database_url, LOCAL.binding),
    supervised.OperatorTarget('local_disposable', LOCAL.database_url, 'other'),
    supervised.OperatorTarget('local_disposable', LOCAL.database_url.replace('127.0.0.1', 'localhost'), LOCAL.binding),
    supervised.OperatorTarget('local_disposable', LOCAL.database_url.replace('127.0.0.1', 'db.example.org'), LOCAL.binding),
    supervised.OperatorTarget('local_disposable', LOCAL.database_url.replace(OPERATOR, 'postgres'), LOCAL.binding),
    supervised.OperatorTarget('local_disposable', LOCAL.database_url + '?options=-crole=postgres', LOCAL.binding),
    supervised.OperatorTarget('local_disposable', LOCAL.database_url + '?connect_timeout=0', LOCAL.binding),
    supervised.OperatorTarget('local_disposable', LOCAL.database_url + '?connect_timeout=11', LOCAL.binding),
    supervised.OperatorTarget('local_disposable', LOCAL.database_url + '?sslmode=disable&sslmode=require', LOCAL.binding),
    supervised.OperatorTarget('local_disposable', LOCAL.database_url.replace(':5432/', ':broken/'), LOCAL.binding),
    supervised.OperatorTarget('local_disposable', LOCAL.database_url.replace(':fixture@', ':%xx@'), LOCAL.binding),
    supervised.OperatorTarget('supabase', 'postgresql://scribeswell_corpus_operator:fixture@db.abc.supabase.co/postgres?sslmode=require', 'https://other.supabase.co'),
    supervised.OperatorTarget('supabase', 'postgresql://scribeswell_corpus_operator:fixture@db.abc.supabase.co/postgres?sslmode=require', 'https://abc.supabase.co?x=y'),
    None,
])
def test_invalid_target_never_spawns(target, monkeypatch):
    monkeypatch.setattr(supervised.subprocess, 'Popen', lambda *a, **k: pytest.fail('spawned'))
    with pytest.raises(PublicationError, match='input_invalid') as error:
        supervised.execute_command(target, encode(body()), source_bytes())
    assert error.value.__context__ is None
    assert 'fixture' not in str(error.value)


@pytest.mark.parametrize('target', [
    LOCAL,
    supervised.OperatorTarget('local_disposable', LOCAL.database_url.replace('127.0.0.1', '[::1]'), LOCAL.binding),
    supervised.OperatorTarget('supabase', 'postgresql://scribeswell_corpus_operator:fixture@db.abc.supabase.co/postgres?sslmode=require', 'https://abc.supabase.co'),
    supervised.OperatorTarget('supabase', 'postgresql://scribeswell_corpus_operator.abc:fixture@aws-0-eu.pooler.supabase.com/postgres?sslmode=verify-full&connect_timeout=3', 'https://abc.supabase.co'),
])
def test_explicit_target_shapes_and_suppressed_frozen_repr(target):
    from dataclasses import FrozenInstanceError
    assert supervised._target(target).startswith('postgresql://')
    assert 'fixture' not in repr(target) and 'postgresql' not in repr(target)
    with pytest.raises(FrozenInstanceError):
        target.binding = 'other'


@pytest.mark.parametrize('raw,source', [(b'invalid', b'invalid'), (encode(body()), b'x' * (supervised.MAX_SOURCE_BYTES + 1))])
def test_invalid_input_never_spawns(raw, source, monkeypatch):
    monkeypatch.setattr(supervised.subprocess, 'Popen', lambda *a, **k: pytest.fail('spawned'))
    with pytest.raises(ValueError):
        supervised.execute_command(LOCAL, raw, source)


def child(code):
    return [sys.executable, '-I', '-c', code]


@pytest.mark.parametrize('code', [
    "import sys; sys.stdin.buffer.read(); sys.stdout.write('not json')",
    "import sys; sys.stdin.buffer.read(); sys.stdout.write('x' * 1000000)",
    "import sys; sys.stdin.buffer.read(); sys.stdout.write('{}')",
    "import sys; sys.stdin.buffer.read(); sys.stdout.write('{\"receipt\":null}'); sys.exit(1)",
    "import sys; sys.stdin.buffer.read(); sys.stdout.write('{\"receipt\":null}')",
    "import sys; sys.stdin.buffer.read(); sys.stdout.write('{\"receipt\":null,\"receipt\":null}')",
    "import sys; sys.stdin.buffer.read(); sys.stdout.write('{\"error\":\"raw secret fixture\"}')",
    "import sys; sys.stdin.buffer.read(); sys.stdout.write('{\"error\":\"access_denied\",\"extra\":1}')",
])
def test_bad_child_response_never_success(code, monkeypatch):
    monkeypatch.setattr(supervised, '_worker_command', lambda: child(code))
    with pytest.raises(PublicationError, match='unknown_outcome') as error:
        supervised.execute_command(LOCAL, encode(body()), source_bytes())
    assert error.value.__context__ is None and 'fixture' not in str(error.value)


@pytest.mark.parametrize('field,value', [('operation_id','33333333-3333-4333-8333-333333333333'),
    ('command','corpus.seal'), ('source_id','other'), ('generation','2'),
    ('executor_actor_id','invalid'), ('attempt_id','invalid'), ('version',True), ('state','closed')])
def test_forged_receipt_validated_against_original(field, value, monkeypatch):
    raw = body()
    receipt = dict(version=1,operation_id=raw['operation_id'],command='corpus.begin',
        source_id='tanakh',executor_actor_id=ACTOR,attempt_id='33333333-3333-4333-8333-333333333333',
        generation='1',state='updating')
    receipt[field] = value
    monkeypatch.setattr(supervised, '_exchange', lambda *a: json.dumps({'receipt':receipt}).encode())
    with pytest.raises(PublicationError, match='unknown_outcome'):
        supervised.execute_command(LOCAL, encode(raw), source_bytes())


@pytest.mark.parametrize('mode', ['read', 'write', 'closed_stdout'])
def test_stalled_child_bounded_killed_and_reaped(mode, monkeypatch):
    monkeypatch.setattr(supervised, '_OPERATION_SECONDS', .4)
    monkeypatch.setattr(supervised, '_REAP_SECONDS', .1)
    code = "import time; time.sleep(30)"
    if mode == 'read':
        code = "import sys,time; sys.stdin.buffer.read(); time.sleep(30)"
    elif mode == 'closed_stdout':
        code = "import os,time; os.close(1); time.sleep(30)"
    monkeypatch.setattr(supervised, '_worker_command', lambda: child(code))
    launched = []
    original = supervised.subprocess.Popen
    def launch(*args, **kwargs):
        process = original(*args, **kwargs)
        launched.append(process)
        return process
    monkeypatch.setattr(supervised.subprocess, 'Popen', launch)
    start = time.monotonic()
    with pytest.raises(PublicationError, match='unknown_outcome'):
        supervised.lookup_outcome(LOCAL, encode(body()))
    assert time.monotonic() - start < 1.5
    assert len(launched) == 1 and launched[0].poll() is not None
    if mode == 'write':
        # Also exercise a blocked stdin larger than the operating-system pipe.
        with pytest.raises(TimeoutError):
            supervised._exchange(b'x' * 1000000, time.monotonic() + .4)
        assert launched[-1].poll() is not None


def test_ambient_credentials_scrubbed_and_stdin_only(monkeypatch):
    for key in ('PGHOST', 'PGSERVICE', 'PGPASSWORD', 'PGOPTIONS', 'PYTHONPATH',
                'PYTHONSTARTUP', 'SCRIBESWELL_DATABASE_URL', 'SCRIBESWELL_AUDIT_DATABASE_URL',
                'SCRIBESWELL_MIGRATION_DATABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY'):
        monkeypatch.setenv(key, 'hostile-secret')
    code = """import json,os,sys
request=json.loads(sys.stdin.buffer.read())
assert set(os.environ) <= {'LANG','LC_CTYPE'}
assert request['target']['database_url'].find(':fixture@') > 0
assert not any('fixture' in arg or 'hostile-secret' in arg for arg in sys.argv)
sys.stdout.write('{"receipt":null}')
"""
    monkeypatch.setattr(supervised, '_worker_command', lambda: child(code))
    assert supervised.lookup_outcome(LOCAL, encode(body())) is None


def test_child_revalidates_target_and_source_before_connect(monkeypatch):
    import base64
    import io
    from dataclasses import asdict
    raw = encode(body())
    def connect(*a, **k):
        pytest.fail('invalid child request connected')
    monkeypatch.setattr(supervised.psycopg, 'connect', connect)
    for target, source in ((asdict(LOCAL), b'invalid'),
        (dict(asdict(LOCAL), binding='other'), source_bytes())):
        request = dict(version=1,target=target,lookup=False,
            raw=base64.b64encode(raw).decode(),source=base64.b64encode(source).decode())
        class Stream:
            def __init__(self, value=b''):
                self.buffer = io.BytesIO(value)
        stdin, stdout = Stream(json.dumps(request).encode()), Stream()
        monkeypatch.setattr(supervised.sys, 'stdin', stdin)
        monkeypatch.setattr(supervised.sys, 'stdout', stdout)
        assert supervised._worker_main() == 0
        assert 'receipt' not in json.loads(stdout.buffer.getvalue())


def test_full_source_qualification_is_inside_deadline(monkeypatch):
    monkeypatch.setattr(supervised, '_OPERATION_SECONDS', .5)
    monkeypatch.setattr(supervised, '_REAP_SECONDS', .1)
    command = supervised._worker_command()
    command[-1] = command[-1].replace('from corpus_operator import _worker_main;',
        "import corpus_operator,time; corpus_operator.prepare_command=lambda *a: time.sleep(30); from corpus_operator import _worker_main;")
    monkeypatch.setattr(supervised, '_worker_command', lambda: command)
    start = time.monotonic()
    with pytest.raises(PublicationError, match='unknown_outcome'):
        supervised.execute_command(LOCAL, encode(body()), source_bytes())
    assert time.monotonic() - start < 1.5


def test_source_failure_is_safe_and_target_never_connected(monkeypatch):
    from corpus_evidence import EvidenceError
    # This explicit target has no server: the source error must precede any connect.
    with pytest.raises(EvidenceError, match='checksum_mismatch') as error:
        supervised.execute_command(LOCAL, encode(body()), b'invalid')
    assert error.value.__context__ is None


def test_fixed_budget_and_no_public_override():
    import inspect
    assert supervised._OPERATION_SECONDS == 60 and supervised._REAP_SECONDS == 2
    assert tuple(inspect.signature(supervised.execute_command).parameters) == ('target', 'raw', 'source_raw')
    assert tuple(inspect.signature(supervised.lookup_outcome).parameters) == ('target', 'raw')


@pytest.mark.parametrize('host', [
    'evil.example,aws-0-eu.pooler.supabase.com',
    'evil.example%2caws-0-eu.pooler.supabase.com',
    'evil.example%2Caws-0-eu.pooler.supabase.com',
    'evil.example%2faws-0-eu.pooler.supabase.com',
    'evil.example%40aws-0-eu.pooler.supabase.com',
    'evil.example\\aws-0-eu.pooler.supabase.com',
    'evil..aws-0-eu.pooler.supabase.com',
])
def test_invalid_pooler_single_host_binding_never_spawns(host, monkeypatch):
    target = supervised.OperatorTarget('supabase',
        'postgresql://scribeswell_corpus_operator.abc:fixture@' + host + '/postgres?sslmode=require',
        'https://abc.supabase.co')
    monkeypatch.setattr(supervised.subprocess, 'Popen', lambda *a, **k: pytest.fail('spawned invalid multi-host target'))
    with pytest.raises(PublicationError, match='input_invalid'):
        supervised.lookup_outcome(target, encode(body()))


@pytest.mark.parametrize('scheme', ['postgresql', 'POSTGRESQL', 'postgresql+psycopg', 'POSTGRESQL+PSYCOPG'])
@pytest.mark.parametrize('kind', ['local_disposable', 'supabase'])
def test_validated_scheme_is_usable_libpq_conninfo(scheme, kind):
    from psycopg.conninfo import conninfo_to_dict
    if kind == 'local_disposable':
        target = supervised.OperatorTarget(kind, LOCAL.database_url.replace('postgresql', scheme, 1), LOCAL.binding)
        host, database, sslmode = '127.0.0.1', 'disposable', None
    else:
        target = supervised.OperatorTarget(kind,
            scheme + '://scribeswell_corpus_operator:fixture@db.abc.supabase.co/postgres?sslmode=require',
            'https://abc.supabase.co')
        host, database, sslmode = 'db.abc.supabase.co', 'postgres', 'require'
    parsed = conninfo_to_dict(supervised._target(target))
    assert parsed['host'] == host and parsed['dbname'] == database
    assert parsed['user'] == OPERATOR and parsed['password'] == 'fixture'
    assert parsed.get('sslmode') == sslmode


def worker_request(*, lookup=True):
    import base64
    from dataclasses import asdict
    return dict(version=1, target=asdict(LOCAL), lookup=lookup,
                raw=base64.b64encode(encode(body())).decode('ascii'),
                source=None if lookup else base64.b64encode(source_bytes()).decode('ascii'))


def run_private_worker(monkeypatch, payload):
    import io
    class Stream:
        def __init__(self, value=b''):
            self.buffer = io.BytesIO(value)
    stdin, stdout = Stream(payload), Stream()
    monkeypatch.setattr(supervised.sys, 'stdin', stdin)
    monkeypatch.setattr(supervised.sys, 'stdout', stdout)
    assert supervised._worker_main() == 0
    return json.loads(stdout.buffer.getvalue())


def test_worker_connect_disables_ambient_authentication_sources(monkeypatch):
    calls = []
    def connect(url, **kwargs):
        calls.append((url, kwargs))
        raise RuntimeError('private-driver-secret')
    monkeypatch.setattr(supervised.psycopg, 'connect', connect)
    result = run_private_worker(monkeypatch, json.dumps(worker_request()).encode())
    assert result == {'error': 'unknown_outcome'}
    assert len(calls) == 1
    url, kwargs = calls[0]
    from psycopg.conninfo import conninfo_to_dict
    parameters = conninfo_to_dict(url, **{key:value for key,value in kwargs.items() if key != 'autocommit'})
    assert parameters['password'] == 'fixture'
    assert kwargs == dict(autocommit=True, connect_timeout=5, sslcertmode='disable',
                          gssencmode='disable', require_auth='password,md5,scram-sha-256',
                          passfile='/dev/null')


def test_unverified_reap_warns_safely_with_bounded_cleanup(monkeypatch, caplog):
    import subprocess
    class Pipe:
        closed = False
        def fileno(self):
            raise OSError('private-pipe-secret')
        def close(self):
            self.closed = True
    class Process:
        stdin, stdout = Pipe(), Pipe()
        killed = False
        waits = []
        def poll(self):
            return None
        def kill(self):
            self.killed = True
        def wait(self, *, timeout):
            self.waits.append(timeout)
            raise subprocess.TimeoutExpired('private-command-secret', timeout)
    process = Process()
    monkeypatch.setattr(supervised.subprocess, 'Popen', lambda *a, **k: process)
    monkeypatch.setattr(supervised, '_REAP_SECONDS', .1)
    with caplog.at_level('WARNING'):
        with pytest.raises(PublicationError) as error:
            supervised.lookup_outcome(LOCAL, encode(body()))
    assert error.value.code == 'corpus_publication.unknown_outcome'
    assert error.value.__context__ is None
    assert process.killed and len(process.waits) == 1 and 0 < process.waits[0] <= .1
    assert process.stdin.closed and process.stdout.closed
    assert [json.loads(record.getMessage()) for record in caplog.records] == [
        dict(service='scribeswell', action='corpus_operator_cleanup', code='termination_unverified')]
    assert all(record.exc_info is None for record in caplog.records)


def test_exhausted_admission_budget_never_spawns(monkeypatch):
    clock = [0.0]
    target_validation = supervised._target
    def admission(target):
        result = target_validation(target)
        clock[0] = 58.0
        return result
    monkeypatch.setattr(supervised.time, 'monotonic', lambda: clock[0])
    monkeypatch.setattr(supervised, '_target', admission)
    monkeypatch.setattr(supervised.subprocess, 'Popen', lambda *a, **k: pytest.fail('exhausted admission spawned'))
    with pytest.raises(PublicationError) as error:
        supervised.lookup_outcome(LOCAL, encode(body()))
    assert error.value.code == 'corpus_publication.unknown_outcome'
    assert error.value.__context__ is None


@pytest.mark.parametrize('invalid', ['oversized', 'duplicate', 'version_bool', 'version_string',
    'version_float', 'lookup_int', 'lookup_string', 'lookup_null', 'raw_base64',
    'source_base64', 'source_on_lookup'])
def test_private_protocol_rejects_invalid_requests_before_connect(invalid, monkeypatch):
    request = worker_request()
    if invalid == 'oversized':
        monkeypatch.setattr(supervised, '_MAX_REQUEST', 256)
        payload = b'x' * 257
    elif invalid == 'duplicate':
        payload = json.dumps(request).encode().replace(b'"version": 1', b'"version": 1, "version": 1')
    else:
        if invalid.startswith('version_'):
            request['version'] = {'version_bool':True, 'version_string':'1', 'version_float':1.0}[invalid]
        elif invalid.startswith('lookup_'):
            request['lookup'] = {'lookup_int':0, 'lookup_string':'false', 'lookup_null':None}[invalid]
        elif invalid == 'raw_base64':
            request['raw'] = '***'
        elif invalid == 'source_base64':
            request['lookup'], request['source'] = False, '***'
        elif invalid == 'source_on_lookup':
            request['source'] = 'eA=='
        payload = json.dumps(request).encode()
    monkeypatch.setattr(supervised.psycopg, 'connect', lambda *a, **k: pytest.fail('invalid protocol connected'))
    assert run_private_worker(monkeypatch, payload) == {'error':'unknown_outcome'}


@pytest.mark.parametrize('failure', ['conflict', 'unavailable'])
def test_supervised_safe_controller_failures_preserve_protected_state(enabled, failure):
    admin, url = enabled
    target = target_for(url)
    if failure == 'conflict':
        supervised.execute_command(target, encode(body()), source_bytes())
    else:
        admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
    def snapshot():
        return tuple(admin.execute('SELECT to_jsonb(t) FROM scribeswell.' + table +
                                   ' t ORDER BY to_jsonb(t)::text').fetchall()
            for table in ('corpus_fence_control','corpus_epoch','corpus_attempt',
                          'corpus_command_outcome','corpus_operator_principal',
                          'corpus_operator_authority','corpus_write_binding'))
    before = snapshot()
    with pytest.raises(PublicationError) as error:
        supervised.execute_command(target, encode(body()), source_bytes())
    assert error.value.code == 'corpus_publication.' + failure
    assert error.value.__context__ is None
    assert snapshot() == before


@pytest.mark.parametrize('site', ['connect', 'commit'])
def test_blocked_actual_worker_connection_or_transaction_commit(enabled, site, tmp_path, monkeypatch, caplog):
    admin, url = enabled
    marker = tmp_path / ('entered-' + site)
    command = supervised._worker_command()
    if site == 'connect':
        injection = '''import corpus_operator, time
from pathlib import Path
def blocked_connect(*args, **kwargs):
    Path(MARKER).write_text('connect')
    time.sleep(30)
corpus_operator.psycopg.connect = blocked_connect
'''
    else:
        # The real adapter reaches this generator only on successful transaction
        # exit, immediately before it sends its COMMIT. Never synthesize a receipt.
        injection = '''import psycopg, time
from pathlib import Path
original_commit = psycopg.Transaction._commit_gen
def blocked_commit(self):
    Path(MARKER).write_text('commit')
    time.sleep(30)
    yield from original_commit(self)
psycopg.Transaction._commit_gen = blocked_commit
'''
    injection = injection.replace('MARKER', repr(str(marker)))
    command[-1] = command[-1].replace('from corpus_operator import _worker_main;',
                                     '\n' + injection + '\nfrom corpus_operator import _worker_main;')
    monkeypatch.setattr(supervised, '_worker_command', lambda: command)
    monkeypatch.setattr(supervised, '_OPERATION_SECONDS', 2)
    monkeypatch.setattr(supervised, '_REAP_SECONDS', .25)
    launched = []
    popen = supervised.subprocess.Popen
    def launch(*args, **kwargs):
        process = popen(*args, **kwargs)
        launched.append(process)
        return process
    monkeypatch.setattr(supervised.subprocess, 'Popen', launch)
    value = body()
    before = counts(admin)
    start = time.monotonic()
    with caplog.at_level('WARNING'):
        with pytest.raises(PublicationError) as error:
            supervised.execute_command(target_for(url), encode(value), source_bytes())
    assert error.value.code == 'corpus_publication.unknown_outcome'
    assert error.value.__context__ is None
    assert time.monotonic() - start < 3
    assert marker.read_text() == site
    assert len(launched) == 1 and launched[0].poll() is not None
    assert [json.loads(record.getMessage()) for record in caplog.records] == [
        dict(service='scribeswell', action='corpus_operator_cleanup', code='forced_termination_reaped')]
    assert counts(admin) == before
