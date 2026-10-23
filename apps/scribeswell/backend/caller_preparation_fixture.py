"""Bounded Linux synthetic IPC only; no preparation, custody or durability claim.

Fixed trusted children create no descendants. Version1 does pure codec work;
version2 captures only explicit synthetic local files. Parent inputs are supplied
bytes and an optional trusted root fd, never blocking storage/owner reads.
Synchronous spawn/OS scheduling are charged on return, not hard-preemptible.
"""
import base64
import fcntl
from dataclasses import dataclass, fields
from functools import wraps
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import time

from apps.scribeswell.backend.caller_preparation_evidence import (
    WorkerResult, encode_worker_result, parse_attempt, parse_target_descriptor,
    parse_worker_result,
)

_WORK_SECONDS = 58.0
_TOTAL_SECONDS = 60.0
_CLEANUP_SECONDS = 2.0
_MAX_REQUEST = 65536
_MAX_RESPONSE = 4096
_ROOT = str(Path(__file__).resolve().parents[3])


class PreparationFixtureError(ValueError):
    code = 'scribeswell_preparation_fixture_invalid'

    def __init__(self):
        super().__init__(self.code)


def _safe(function):
    @wraps(function)
    def call(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (ValueError, TypeError, AttributeError, OverflowError, RecursionError):
            pass
        try:
            raise PreparationFixtureError() from None
        except PreparationFixtureError as error:
            error.__context__ = None
            raise
    return call


@dataclass(frozen=True, slots=True, repr=False)
class FixtureObservation:
    status: str
    code: str
    termination: str
    reply: WorkerResult | None


def _require(condition):
    if not condition:
        raise ValueError()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def _fixture(request_raw, target, records):
    parsed = parse_attempt(records, request_raw=request_raw, target=target)
    _require(target.kind == 'local_disposable' and parsed[0].payload.admission_class == 'synthetic_fixture')
    _require(parsed[-1].kind == 'finished')
    return parsed[-1]


@_safe
def _encode_envelope(request_raw, target, records):
    _fixture(request_raw, target, records)
    value = dict(schema_version=1, request_b64=base64.b64encode(request_raw).decode('ascii'),
                 target={field.name: object.__getattribute__(target, field.name) for field in fields(target)},
                 records_b64=[base64.b64encode(raw).decode('ascii') for raw in records])
    # Every value is already bounded exact primitive data from validated inputs.
    # Do not accumulate serialized transport beyond its cap.
    result = bytearray()
    encoder = json.JSONEncoder(sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    for piece in encoder.iterencode(value):
        encoded = piece.encode('ascii')
        _require(len(result)+len(encoded) <= _MAX_REQUEST)
        result.extend(encoded)
    return bytes(result)


def _pairs(items):
    value = {}
    for key, item in items:
        _require(key not in value)
        value[key] = item
    return value


def _reject_number(raw):
    raise ValueError()


def _base64(value, limit):
    _require(type(value) is str and len(value) <= ((limit+2)//3)*4)
    raw = base64.b64decode(value, validate=True)
    _require(len(raw) <= limit and base64.b64encode(raw).decode('ascii') == value)
    return raw


@_safe
def _decode_envelope(raw):
    _require(type(raw) is bytes and len(raw) <= _MAX_REQUEST)
    text = raw.decode('utf-8', errors='strict')
    _require(not text.startswith('\ufeff'))
    value = json.loads(text, object_pairs_hook=_pairs, parse_float=_reject_number, parse_constant=_reject_number)
    pending = [(value, 1)]
    while pending:
        item, depth = pending.pop()
        if type(item) in (dict, list):
            _require(depth <= 4)
            pending.extend((child, depth+1) for child in (item.values() if type(item) is dict else item))
    _require(type(value) is dict and value.keys() == {'schema_version', 'request_b64', 'target', 'records_b64'})
    _require(type(value['schema_version']) is int and value['schema_version'] == 1)
    raw_request = _base64(value['request_b64'], 8192)
    target = parse_target_descriptor(_canonical(value['target']))
    _require(type(value['records_b64']) is list and 1 <= len(value['records_b64']) <= 4)
    records = tuple(_base64(encoded, 32768) for encoded in value['records_b64'])
    _fixture(raw_request, target, records)
    return raw_request, target, records


@_safe
def _read_request(stream):
    raw = bytearray()
    while True:
        chunk = stream.read(_MAX_REQUEST+1-len(raw))
        _require(type(chunk) is bytes)
        if not chunk:
            break
        _require(len(raw)+len(chunk) <= _MAX_REQUEST)
        raw.extend(chunk)
    return bytes(raw)


def _worker_main():
    """Fixed pure declaration worker. Never import storage or database code."""
    try:
        request, target, records = _decode_envelope(_read_request(sys.stdin.buffer))
        end = _fixture(request, target, records)
        reply = WorkerResult(1, end.run_id, end.request_sha256, end.target_sha256, end.sequence,
                             hashlib.sha256(records[-1]).hexdigest(), end.payload.outcome, end.payload.code)
        sys.stdout.buffer.write(encode_worker_result(reply))
        sys.stdout.buffer.flush()
        return 0
    except (PreparationFixtureError, OSError, ValueError):
        return 2


def _worker_command():
    bootstrap = ('import sys; sys.path.insert(0,sys.argv[1]); '
                 'from apps.scribeswell.backend.caller_preparation_fixture import _worker_main; '
                 'raise SystemExit(_worker_main())')
    return [sys.executable, '-I', '-S', '-c', bootstrap, _ROOT]


class _Deadline(Exception):
    pass


class _ChildFailed(Exception):
    pass


def _check(work_deadline):
    if time.monotonic() >= work_deadline:
        raise _Deadline()


def _exchange(process, payload, work_deadline):
    response, offset = bytearray(), 0
    with selectors.DefaultSelector() as selector:
        for pipe in (process.stdin, process.stdout):
            os.set_blocking(pipe.fileno(), False)
        selector.register(process.stdin, selectors.EVENT_WRITE)
        selector.register(process.stdout, selectors.EVENT_READ)
        while selector.get_map() or process.poll() is None:
            _check(work_deadline)
            remaining = work_deadline-time.monotonic()
            if remaining <= 0:
                raise _Deadline()
            for key, _ in selector.select(min(remaining, 0.025)):
                _check(work_deadline)
                try:
                    if key.fileobj is process.stdin:
                        count = os.write(key.fd, payload[offset:offset+4096])
                        _require(type(count) is int and 0 < count <= min(4096, len(payload)-offset))
                        offset += count
                        if offset == len(payload):
                            selector.unregister(process.stdin)
                            process.stdin.close()
                    else:
                        chunk = os.read(key.fd, _MAX_RESPONSE+1-len(response))
                        if not chunk:
                            selector.unregister(process.stdout)
                            process.stdout.close()
                        else:
                            _require(len(response)+len(chunk) <= _MAX_RESPONSE)
                            response.extend(chunk)
                except BlockingIOError:
                    continue
        _check(work_deadline)
        if process.returncode != 0:
            raise _ChildFailed()
    return bytes(response)


def _finish(process, total_deadline):
    """No final drain or retry; never extend an exhausted cleanup budget."""
    if process is None:
        return 'not_started', False
    close_failed = False
    for pipe in (process.stdin, process.stdout):
        try:
            if pipe is not None:
                pipe.close()
        except OSError:
            close_failed = True
    try:
        if process.poll() is not None:
            return 'child_exited', close_failed
    except OSError:
        pass
    forced = False
    try:
        process.kill()
        forced = True
    except OSError:
        pass
    remaining = min(_CLEANUP_SECONDS, total_deadline-time.monotonic())
    if remaining <= 0:
        return 'termination_unverified', close_failed
    try:
        returncode = process.wait(timeout=remaining)
        # kill() may return normally after a natural exit in its internal poll
        # race. Only an observed SIGKILL exit supports a forced-stop claim.
        termination = 'forced_termination_reaped' if forced and returncode == -signal.SIGKILL else 'child_exited'
        return termination, close_failed
    except (subprocess.TimeoutExpired, OSError):
        return 'termination_unverified', close_failed


def _observe(payload, *, request_raw, target, records, started, root_fd=None):
    """One lifecycle for the two fixed trusted workers; no caller callback API."""
    work_deadline, total_deadline = started+_WORK_SECONDS, started+_TOTAL_SECONDS
    process, reply, code = None, None, 'fixture_transport_invalid'
    try:
        _check(work_deadline)
        try:
            command = _worker_command() if root_fd is None else _capture_command(root_fd)
            resources = {} if root_fd is None else {'pass_fds': (root_fd,)}
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.DEVNULL, env={}, close_fds=True, bufsize=0, cwd=_ROOT,
                                       **resources)
        except OSError:
            code = 'fixture_spawn_failed'
        if process is not None:
            _check(work_deadline)
            response = _exchange(process, payload, work_deadline)
            try:
                reply = parse_worker_result(response, request_raw=request_raw, target=target, records=records)
            except ValueError:
                code = 'fixture_reply_invalid'
            _check(work_deadline)
    except _Deadline:
        reply, code = None, 'fixture_deadline_exceeded'
    except _ChildFailed:
        reply, code = None, 'fixture_child_failed'
    except (OSError, ValueError):
        reply, code = None, 'fixture_transport_invalid'
    finally:
        termination, close_failed = _finish(process, total_deadline)
    # Charge cleanup/scheduling overrun before accepting the final observation.
    if time.monotonic() >= total_deadline:
        reply, code = None, 'fixture_deadline_exceeded'
    if termination == 'termination_unverified' or close_failed:
        reply, code = None, 'fixture_cleanup_unverified'
    if reply is not None:
        return FixtureObservation('fixture_reply_validated', 'fixture_reply_validated', termination, reply)
    return FixtureObservation('unknown', code, termination, None)


@_safe
def supervise_fixture(*, request_raw: bytes, target, records: tuple[bytes, ...]) -> FixtureObservation:
    """Validate declarations only; retains version1 behavior and no store import."""
    started = time.monotonic()
    payload = _encode_envelope(request_raw, target, records)
    return _observe(payload, request_raw=request_raw, target=target, records=records, started=started)


@_safe
def _encode_capture(request_raw, target, records):
    value = json.loads(_encode_envelope(request_raw, target, records))
    value.update(schema_version=2, operation='fixture.capture')
    raw = _canonical(value)
    _require(len(raw) <= _MAX_REQUEST)
    return raw


@_safe
def _decode_capture(raw):
    _require(type(raw) is bytes and len(raw) <= _MAX_REQUEST)
    text = raw.decode('utf-8', errors='strict')
    _require(not text.startswith('\ufeff'))
    value = json.loads(text, object_pairs_hook=_pairs, parse_float=_reject_number, parse_constant=_reject_number)
    _require(type(value) is dict and value.keys() == {'schema_version','operation','request_b64','target','records_b64'})
    _require(type(value['schema_version']) is int and value['schema_version'] == 2
             and value['operation'] == 'fixture.capture')
    del value['operation']
    value['schema_version'] = 1
    return _decode_envelope(_canonical(value))


def _capture_command(root_fd):
    bootstrap = ('import sys; sys.path.insert(0,sys.argv[1]); '
                 'from apps.scribeswell.backend.caller_preparation_fixture import _capture_main; '
                 'raise SystemExit(_capture_main(int(sys.argv[2])))')
    return [sys.executable, '-I', '-S', '-c', bootstrap, _ROOT, str(root_fd)]


def _capture_main(root_fd):
    """Only this fixed worker imports storage; every filesystem wait is supervised."""
    from apps.scribeswell.backend.caller_preparation_storage import create_fixture_attempt, read_fixture_prefix
    try:
        request, target, records = _decode_capture(_read_request(sys.stdin.buffer))
        end = _fixture(request, target, records)
        with create_fixture_attempt(root_fd, request_raw=request, target=target) as writer:
            for raw in records:
                acknowledged = writer.append(raw)
        _require(read_fixture_prefix(root_fd, request_raw=request, target=target) == records)
        _require(acknowledged.sequence == end.sequence
                 and acknowledged.record_sha256 == hashlib.sha256(records[-1]).hexdigest())
        reply = WorkerResult(1, end.run_id, end.request_sha256, end.target_sha256, acknowledged.sequence,
                             acknowledged.record_sha256, end.payload.outcome, end.payload.code)
        sys.stdout.buffer.write(encode_worker_result(reply))
        sys.stdout.buffer.flush()
        return 0
    except (PreparationFixtureError, OSError, ValueError):
        return 2


@_safe
def capture_fixture(root_fd: int, *, request_raw: bytes, target, records: tuple[bytes, ...]) -> FixtureObservation:
    """Acknowledge supervised synthetic local capture only; never preparation SQL."""
    started = time.monotonic()
    payload = _encode_capture(request_raw, target, records)
    _require(type(root_fd) is int and root_fd >= 0)
    try:
        pinned = fcntl.fcntl(root_fd, fcntl.F_DUPFD_CLOEXEC, 3)
    except OSError:
        _require(False)
    close_failed = False
    try:
        result = _observe(payload, request_raw=request_raw, target=target, records=records,
                          started=started, root_fd=pinned)
    finally:
        try:
            os.close(pinned)
        except OSError:
            close_failed = True
    if close_failed:
        return FixtureObservation('unknown', 'fixture_cleanup_unverified', result.termination, None)
    if time.monotonic() >= started+_TOTAL_SECONDS:
        return FixtureObservation('unknown', 'fixture_deadline_exceeded', result.termination, None)
    if result.status == 'fixture_reply_validated':
        return FixtureObservation('fixture_records_acknowledged', 'fixture_records_acknowledged', result.termination, result.reply)
    return result
