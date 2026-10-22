"""App-local supervised corpus calls; no discovery, provisioning or public runner.

The private child protocol is deliberately independent of argv and ambient settings.
"""
import base64
from dataclasses import asdict, dataclass
import importlib.util
import json
import logging
import os
from pathlib import Path
import re
import selectors
import subprocess
import sys
import time
from urllib.parse import parse_qs, unquote, urlsplit

import psycopg
from corpus_evidence import MAX_SOURCE_BYTES, EvidenceError
from corpus_publication import (CommandReceipt, PublicationError, _receipt,
                                execute_command as _execute, lookup_outcome as _lookup)
from corpus_publication_input import MAX_COMMAND_BYTES, parse_command, prepare_command
from database import validate_url

_OPERATION_SECONDS = 60
_REAP_SECONDS = 2
_MAX_RESPONSE = 4096
_MAX_REQUEST = (MAX_SOURCE_BYTES + MAX_COMMAND_BYTES) * 4 // 3 + 65536
_ROLE = 'scribeswell_corpus_operator'
_LOG = logging.getLogger(__name__)
_SAFE_FAILURES = {'access_denied', 'input_invalid', 'conflict', 'unavailable', 'unknown_outcome'}
_SOURCE_FAILURES = {'checksum_invalid', 'checksum_mismatch', 'duplicate_json_key',
    'identity_invalid', 'json_invalid', 'position_invalid', 'source_inventory_invalid',
    'source_structure_invalid', 'source_too_large', 'source_word_invalid',
    'surface_too_large', 'text_invalid', 'tokens_invalid', 'unicode_invalid'}
_BACKEND = Path(__file__).resolve().parent
_CONTRACT = _BACKEND.parents[2] / 'platform' / 'deployment' / 'target_contract.py'


@dataclass(frozen=True, slots=True, repr=False)
class OperatorTarget:
    """Explicit target custody; local_disposable is a declaration, not proof."""
    kind: str
    database_url: str
    binding: str


def _target(target):
    failed = False
    try:
        if type(target) is not OperatorTarget or not all(
                type(value) is str and 0 < len(value) <= 8192
                and all(32 < ord(char) < 127 for char in value)
                for value in (target.kind, target.database_url, target.binding)):
            raise ValueError
        value = target.database_url
        if re.search(r'%(?![0-9A-Fa-f]{2})', value):
            raise ValueError
        url = urlsplit(value)
        port = url.port  # Reject invalid port syntax, including before spawning.
        if port is not None and not 1 <= port <= 65535:
            raise ValueError
        query = parse_qs(url.query, keep_blank_values=True, strict_parsing=True)
        if set(query) - {'sslmode', 'connect_timeout'} or any(len(v) != 1 for v in query.values()):
            raise ValueError
        if 'connect_timeout' in query and (not re.fullmatch(r'[1-9]|10', query['connect_timeout'][0])):
            raise ValueError
        if 'sslmode' in query and query['sslmode'][0] not in ('disable', 'require', 'verify-full'):
            raise ValueError
        validate_url(value, _ROLE)
        if target.kind == 'local_disposable':
            if (url.hostname not in ('127.0.0.1', '::1') or unquote(url.username or '') != _ROLE
                    or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,62}', target.binding)
                    or unquote(url.path) != '/' + target.binding):
                raise ValueError
        elif target.kind == 'supabase':
            # libpq interprets commas (including percent-encoded commas) as
            # multiple hosts. The shared contract binds the suffix/role; add
            # a single DNS-host syntax check before passing any URL to libpq.
            if not re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}',
                                url.hostname or ''):
                raise ValueError
            project = urlsplit(target.binding)
            if (project.scheme != 'https' or project.netloc != project.hostname
                    or project.path not in ('', '/') or project.query or project.fragment):
                raise ValueError
            spec = importlib.util.spec_from_file_location('_corpus_target_contract', _CONTRACT)
            contract = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(contract)
            contract.database_url(value, target.binding, _ROLE)
        else:
            raise ValueError
    except Exception:
        failed = True
    if failed:
        raise PublicationError('input_invalid')
    return 'postgresql:' + value.split(':', 1)[1]


def _decode(payload):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError
            result[key] = value
        return result
    return json.loads(payload, object_pairs_hook=unique)


def _worker_command():
    # -I excludes Python environment, user site and the current directory. The
    # sole app import root is fixed from this file, never caller/environment input.
    code = ('import sys; sys.path.insert(0, ' + repr(str(_BACKEND)) + '); '
            'from corpus_operator import _worker_main; raise SystemExit(_worker_main())')
    return [sys.executable, '-I', '-c', code]


def _exchange(request, deadline):
    """Multiplex bounded pipe chunks; never accumulate arbitrary child output."""
    process = None
    response = bytearray()
    work_deadline = deadline - _REAP_SECONDS
    try:
        if time.monotonic() >= work_deadline:
            raise TimeoutError
        process = subprocess.Popen(_worker_command(), stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                   env={'LANG': 'C.UTF-8'}, close_fds=True)
        with selectors.DefaultSelector() as selector:
            for pipe in (process.stdin, process.stdout):
                os.set_blocking(pipe.fileno(), False)
            selector.register(process.stdin, selectors.EVENT_WRITE)
            selector.register(process.stdout, selectors.EVENT_READ)
            offset = 0
            while selector.get_map() or process.poll() is None:
                remaining = work_deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError
                for key, _ in selector.select(min(remaining, .05)):
                    if key.fileobj is process.stdin:
                        count = os.write(key.fd, memoryview(request)[offset:offset + 65536])
                        offset += count
                        if offset == len(request):
                            selector.unregister(process.stdin)
                            process.stdin.close()
                    else:
                        chunk = os.read(key.fd, min(65536, _MAX_RESPONSE + 1 - len(response)))
                        if not chunk:
                            selector.unregister(process.stdout)
                            process.stdout.close()
                        else:
                            response.extend(chunk)
                            if len(response) > _MAX_RESPONSE:
                                raise ValueError
            if process.returncode != 0 or time.monotonic() >= work_deadline:
                raise ValueError
        return bytes(response)
    finally:
        if process is not None:
            if process.poll() is None:
                forced = False
                try:
                    process.kill()
                    forced = True
                except ProcessLookupError:
                    pass
                # Bound direct-child reaping; never drain pipes during cleanup.
                try:
                    process.wait(timeout=max(.001, min(_REAP_SECONDS, deadline - time.monotonic())))
                except subprocess.TimeoutExpired:
                    _LOG.warning('{"service":"scribeswell","action":"corpus_operator_cleanup",'
                                 '"code":"termination_unverified"}')
                else:
                    if forced:
                        _LOG.warning('{"service":"scribeswell","action":"corpus_operator_cleanup",'
                                     '"code":"forced_termination_reaped"}')
            for pipe in (process.stdin, process.stdout):
                if pipe is not None:
                    pipe.close()


def _invoke(target, raw, source_raw, *, lookup):
    deadline = time.monotonic() + _OPERATION_SECONDS
    _target(target)
    command = parse_command(raw)
    if not lookup and (type(source_raw) is not bytes or len(source_raw) > MAX_SOURCE_BYTES):
        raise EvidenceError('source_too_large')
    request = json.dumps({'version': 1, 'target': asdict(target), 'lookup': lookup,
                          'raw': base64.b64encode(raw).decode('ascii'),
                          'source': None if lookup else base64.b64encode(source_raw).decode('ascii')},
                         separators=(',', ':')).encode('ascii')
    failure = None
    result = None
    try:
        response = _exchange(request, deadline)
        value = _decode(response)
        if type(value) is not dict or len(value) != 1:
            raise ValueError
        if set(value) == {'error'}:
            if type(value['error']) is not str or value['error'] not in _SAFE_FAILURES:
                raise ValueError
            failure = value['error']
        elif set(value) == {'source_error'}:
            if type(value['source_error']) is not str or value['source_error'] not in _SOURCE_FAILURES:
                raise ValueError
            failure = 'source_evidence.' + value['source_error']
        elif set(value) == {'receipt'}:
            if value['receipt'] is None and lookup:
                result = None
            else:
                result = _receipt(value['receipt'], command)
        else:
            raise ValueError
        if time.monotonic() >= deadline - _REAP_SECONDS:
            raise ValueError
    except Exception:
        failure = 'unknown_outcome'
    if failure:
        if failure.startswith('source_evidence.'):
            raise EvidenceError(failure.removeprefix('source_evidence.'))
        raise PublicationError(failure)
    return result


def execute_command(target: OperatorTarget, raw: bytes, source_raw: bytes) -> CommandReceipt:
    """Supervise source qualification before connect, then return committed receipt.

    On unknown_outcome preserve these exact inputs and explicitly lookup; never
    retry with a new operation. No caller-selectable timeout is provided.
    """
    return _invoke(target, raw, source_raw, lookup=False)


def lookup_outcome(target: OperatorTarget, raw: bytes) -> CommandReceipt | None:
    """Lookup original input under current authority; None remains unresolved."""
    return _invoke(target, raw, None, lookup=True)


def _worker_main():
    """Private bounded stdin protocol; no argv input, discovery or stderr output."""
    response = {'error': 'unknown_outcome'}
    try:
        payload = sys.stdin.buffer.read(_MAX_REQUEST + 1)
        if len(payload) > _MAX_REQUEST:
            raise ValueError
        request = _decode(payload)
        if (type(request) is not dict or set(request) != {'version', 'target', 'lookup', 'raw', 'source'}
                or type(request['version']) is not int or request['version'] != 1
                or type(request['lookup']) is not bool or type(request['target']) is not dict
                or set(request['target']) != {'kind', 'database_url', 'binding'}):
            raise ValueError
        target = OperatorTarget(**request['target'])
        url = _target(target)
        raw = base64.b64decode(request['raw'], validate=True)
        if len(raw) > MAX_COMMAND_BYTES:
            raise ValueError
        if request['lookup']:
            if request['source'] is not None:
                raise ValueError
            parse_command(raw)
            source = None
        else:
            source = base64.b64decode(request['source'], validate=True)
            if len(source) > MAX_SOURCE_BYTES:
                raise ValueError
            prepare_command(raw, source)
        # Credentials are explicit URL password only: libpq defaults otherwise
        # include client certificates, GSS caches and a per-user password file.
        with psycopg.connect(url, autocommit=True, connect_timeout=5,
                             sslcertmode='disable', gssencmode='disable',
                             require_auth='password,md5,scram-sha-256',
                             passfile='/dev/null') as connection:
            receipt = _lookup(connection, raw) if request['lookup'] else _execute(connection, raw, source)
        response = {'receipt': None if receipt is None else asdict(receipt)}
    except EvidenceError as error:
        code = error.code.removeprefix('source_evidence.')
        if code in _SOURCE_FAILURES:
            response = {'source_error': code}
    except PublicationError as error:
        code = error.code.removeprefix('corpus_publication.')
        if code in _SAFE_FAILURES:
            response = {'error': code}
    except Exception:
        pass
    sys.stdout.buffer.write(json.dumps(response, separators=(',', ':')).encode('ascii'))
    sys.stdout.buffer.flush()
    return 0
