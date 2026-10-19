"""Connection continuity and fail-closed framing, using private Unix sockets only."""
from contextlib import contextmanager, redirect_stdout
import json
import io
from pathlib import Path
import socket
import socketserver
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import test_docker_gate
import dev


def response(body=None, status=200, headers=b'', protocol=b'HTTP/1.1'):
    raw = json.dumps(body if body is not None else {}).encode()
    return protocol + b' ' + str(status).encode() + b' Result\r\nContent-Length: ' + str(len(raw)).encode() + b'\r\n' + headers + b'\r\n' + raw


class Peer:
    def __init__(self, replies):
        self.replies = replies
        self.connections = 0
        self.requests = []
        self.closed = threading.Event()
        self.hook = None

    @contextmanager
    def serve(self):
        peer = self
        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                peer.connections += 1
                self.request.settimeout(1)
                try:
                    while True:
                        data = b''
                        while b'\r\n\r\n' not in data:
                            chunk = self.request.recv(4096)
                            if not chunk:
                                return
                            data += chunk
                        header, body = data.split(b'\r\n\r\n', 1)
                        fields = dict(line.lower().split(b':', 1) for line in header.split(b'\r\n')[1:])
                        length = int(fields.get(b'content-length', b'0'))
                        while len(body) < length:
                            chunk = self.request.recv(4096)
                            if not chunk:
                                return
                            body += chunk
                        peer.requests.append(header.split(b'\r\n')[0])
                        if peer.hook:
                            if peer.hook(self.request, len(peer.requests)):
                                continue
                        reply = peer.replies[len(peer.requests) - 1]
                        if reply is None:
                            return
                        self.request.sendall(reply)
                except OSError:
                    pass
                finally:
                    peer.closed.set()
        with tempfile.TemporaryDirectory(prefix='env-session-') as temp:
            self.path = str(Path(temp) / 'daemon.sock')
            with socketserver.UnixStreamServer(self.path, Handler) as server:
                worker = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': .01}, daemon=True)
                worker.start()
                try:
                    yield self.path
                finally:
                    server.shutdown()
                    worker.join(2)


class DockerSessionTests(unittest.TestCase):
    def test_owner_entry_observation_propagates_clock_and_deadline_cancellation(self):
        for source in ['clock', 'deadline']:
            for cancellation in [KeyboardInterrupt('SECRET'), SystemExit(91), GeneratorExit()]:
                body = []
                def deadline():
                    if source == 'deadline':
                        raise cancellation
                    return 5
                with self.subTest(source=source, cancellation=type(cancellation).__name__), \
                        patch.object(dev.time, 'monotonic', side_effect=cancellation if source == 'clock' else None,
                                     return_value=1):
                    with self.assertRaises(type(cancellation)) as caught:
                        with dev._owner_observation('fresh', 'custody', deadline):
                            body.append(True)
                    self.assertIs(caught.exception, cancellation)
                    self.assertEqual(body, [])

    def test_owner_exit_observation_cancellation_preserves_original_error(self):
        for cancellation in [KeyboardInterrupt('SECRET'), SystemExit(91), GeneratorExit()]:
            original = dev.Refusal('docker', 'docker_timeout')
            with self.subTest(cancellation=type(cancellation).__name__), \
                    patch.object(dev.time, 'monotonic', side_effect=[1, cancellation]):
                with self.assertRaises(dev.Refusal) as caught:
                    with dev._owner_observation('fresh', 'custody', lambda: 5):
                        raise original
            self.assertIs(caught.exception, original)
            self.assertNotIn('owner_failure', dev.refusal_result(original))

    def test_owner_deadline_observation_failure_preserves_success_and_original_error(self):
        for value in [RuntimeError('SECRET'), ValueError('SECRET'), None, 'SECRET', True,
                      [], {}, float('nan'), float('inf'), float('-inf')]:
            for fail_body in [False, True]:
                original, body = dev.Refusal('docker', 'docker_timeout'), []
                def deadline():
                    if isinstance(value, Exception):
                        raise value
                    return value
                def execute():
                    with dev._owner_observation('fresh', 'custody', deadline):
                        body.append(True)
                        if fail_body:
                            raise original
                with self.subTest(value=type(value).__name__, fail_body=fail_body), \
                        patch.object(dev.time, 'monotonic', return_value=1):
                    if fail_body:
                        with self.assertRaises(dev.Refusal) as caught:
                            execute()
                        self.assertIs(caught.exception, original)
                    else:
                        execute()
                self.assertEqual(body, [True])
                self.assertNotIn('owner_failure', dev.refusal_result(original))

    def test_owner_observation_preserves_outcomes_and_bounds_elapsed(self):
        for scope, check in [('acquisition', 'custody'), ('fresh', 'custody'), ('guard', 'budget')]:
            for entry, end, expected_check, elapsed in [(1, 2, check, 1000),
                    (5, 6, 'already_expired', 1000), (1, -1, check, 0),
                    (1, 1e20, check, dev.DOCKER_ELAPSED_MAX)]:
                original = dev.Refusal('docker', 'docker_timeout')
                with self.subTest(scope=scope, entry=entry, end=end), \
                        patch.object(dev.time, 'monotonic', side_effect=[entry, end]):
                    with self.assertRaises(dev.Refusal) as caught:
                        with dev._owner_observation(scope, check, lambda: 5):
                            raise original
                self.assertIs(caught.exception, original)
                self.assertEqual(dev.refusal_result(original)['owner_failure'], {
                    'schema_version': 1, 'scope': scope, 'check': expected_check, 'elapsed_ms': elapsed})
        for original in [dev.Refusal('custody', 'changed'), KeyboardInterrupt('SECRET'),
                         TimeoutError('SECRET'), dev.Refusal('other', 'docker_timeout')]:
            with self.subTest(error=type(original)), patch.object(dev.time, 'monotonic', return_value=10):
                with self.assertRaises(type(original)) as caught:
                    with dev._owner_observation('fresh', 'custody', lambda: 5):
                        raise original
                self.assertIs(caught.exception, original)
                self.assertNotIn('owner_failure', vars(original))
        with patch.object(dev.time, 'monotonic', return_value=10):
            with dev._owner_observation('fresh', 'custody', lambda: 5):
                pass  # Observation never introduces a refusal on success.

    def test_owner_observation_optional_clock_attributes_and_request_metadata(self):
        class Hostile(dev.Refusal):
            def __getattribute__(self, name):
                if name in ('owner_failure', 'docker_failure', '__dict__'):
                    raise AssertionError('SECRET attribute')
                return super().__getattribute__(name)
            def __str__(self):
                raise AssertionError('must never stringify')
        for clocks in [[RuntimeError('SECRET')], [float('nan')], [float('inf')],
                       [1, RuntimeError('SECRET')], [1, float('nan')], [1, float('inf')]]:
            original = Hostile('docker', 'docker_timeout')
            with self.subTest(clocks=clocks), patch.object(dev.time, 'monotonic', side_effect=clocks):
                with self.assertRaises(Hostile) as caught:
                    with dev._owner_observation('fresh', 'custody', lambda: 5):
                        raise original
            self.assertIs(caught.exception, original)
            self.assertNotIn('owner_failure', dev.refusal_result(original))
        original = Hostile('docker', 'docker_timeout')
        original.docker_failure = {'schema_version': 1, 'operation': 'image_inspect',
                                   'phase': 'receive', 'elapsed_ms': 4}
        with patch.object(dev.time, 'monotonic', return_value=1), self.assertRaises(Hostile):
            with dev._owner_observation('guard', 'budget', lambda: 5):
                raise original
        self.assertNotIn('owner_failure', dev.refusal_result(original))
        self.assertEqual(dev.refusal_result(original)['docker_failure'],
                         BaseException.__dict__['__dict__'].__get__(original)['docker_failure'])

    def test_owner_formatter_closed_types_original_chain_and_truncation(self):
        valid = {'schema_version': 1, 'scope': 'fresh', 'check': 'custody', 'elapsed_ms': 0}
        malformed = [None, [], dict(valid, secret='SECRET'), dict(valid, schema_version=True),
                     dict(valid, elapsed_ms=True), dict(valid, elapsed_ms=-1),
                     dict(valid, elapsed_ms=2147483648), dict(valid, elapsed_ms=1.0),
                     dict(valid, scope='SECRET'), dict(valid, check='budget'),
                     dict(valid, scope='guard'), {k: v for k, v in valid.items() if k != 'scope'}]
        class Hostile(dict):
            def __iter__(self):
                raise AssertionError('must not inspect untrusted containers')
        class HostileKey(str):
            def __hash__(self):
                return super().__hash__()
            def __eq__(self, other):
                raise AssertionError('must not compare untrusted keys')
        malformed += [Hostile(valid), {HostileKey('scope'): 'fresh', 'schema_version': 1,
                                      'check': 'custody', 'elapsed_ms': 0}]
        outer = dev.Refusal('execution', 'execution_cleanup_unresolved')
        for value in malformed:
            outer.owner_failure = value
            self.assertNotIn('owner_failure', dev.refusal_result(outer))
        original = dev.Refusal('docker', 'docker_timeout')
        original.owner_failure = valid
        outer.owner_failure = dict(valid, scope='acquisition')
        outer.__cause__ = RuntimeError('SECRET cleanup')
        outer.__cause__.__context__ = original
        original.__context__ = outer
        result = dev.refusal_result(outer)
        self.assertEqual(result['owner_failure'], valid)
        self.assertEqual((result['stage'], result['code']), ('execution', 'execution_cleanup_unresolved'))
        cursor = outer
        for _ in range(40):
            cursor.__cause__ = RuntimeError('SECRET')
            cursor = cursor.__cause__
        self.assertNotIn('owner_failure', dev.refusal_result(outer))


    def test_close_failure_acceptance_keeps_qualifier_transport_refusal(self):
        import qualify_startup
        transport = test_docker_gate.ScriptedSocket(response())
        session = dev.DockerSession(deadline=5)
        output = io.StringIO()
        def qualify(*args):
            with session:
                session.exchange('GET', '/version')
        with patch.object(dev.time, 'monotonic', return_value=1), \
                patch.object(dev.socket, 'socket', return_value=transport) as factory, \
                patch.object(transport, 'connect', side_effect=TimeoutError('SECRET original')), \
                patch.object(transport, 'close', side_effect=OSError('SECRET close')) as close, \
                patch.object(qualify_startup.startup, 'qualify', side_effect=qualify), redirect_stdout(output):
            code = qualify_startup.main(['--target', 'SECRET target', '--run-id', 'SECRET run',
                                          '--control', 'pinned-cli-postgres'])
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(output.getvalue()), {'ok': False, 'runtime_ready': False,
                'stage': 'docker', 'code': 'docker_timeout', 'docker_failure': {
                    'schema_version': 1, 'operation': 'daemon_version', 'phase': 'connect', 'elapsed_ms': 0}})
            self.assertTrue(session.closed)
            self.assertIsNone(session.stream)
            close.assert_called_once()
            for reuse in [session.__enter__, lambda: session.exchange('GET', '/version')]:
                with self.assertRaises(dev.Refusal) as caught:
                    reuse()
                self.assertEqual(caught.exception.code, 'docker_session_closed')
            factory.assert_called_once()
        self.assertNotIn('SECRET', output.getvalue())

    def test_close_failure_preserves_active_exchange_error_and_cancellation(self):
        errors = [TimeoutError('SECRET timeout'), OSError('SECRET transport'),
                  dev.Refusal('docker', 'docker_response_invalid'),
                  KeyboardInterrupt('SECRET interrupt'), SystemExit(91)]
        for original in errors:
            transport = test_docker_gate.ScriptedSocket(response())
            session = dev.DockerSession(deadline=5)
            with self.subTest(error=type(original).__name__), \
                    patch.object(dev.time, 'monotonic', return_value=1), \
                    patch.object(dev.socket, 'socket', return_value=transport) as factory, \
                    patch.object(transport, 'connect', side_effect=original), \
                    patch.object(transport, 'close', side_effect=OSError('SECRET close')) as close:
                expected = dev.Refusal if isinstance(original, OSError) else type(original)
                with self.assertRaises(expected) as caught:
                    with session:
                        session.exchange('GET', '/version')
                if isinstance(original, OSError):
                    self.assertEqual(caught.exception.code,
                                     'docker_timeout' if isinstance(original, TimeoutError) else 'docker_unavailable')
                    self.assertIs(caught.exception.__cause__, original)
                else:
                    self.assertIs(caught.exception, original)
                self.assertEqual(caught.exception.docker_failure,
                                 {'schema_version': 1, 'operation': 'daemon_version', 'phase': 'connect', 'elapsed_ms': 0})
                self.assertTrue(session.closed)
                self.assertIsNone(session.stream)
                session.close()
                close.assert_called_once()
                factory.assert_called_once()

    def test_context_close_failure_preserves_active_body_error_only(self):
        for original in [RuntimeError('SECRET body'), KeyboardInterrupt('SECRET interrupt')]:
            transport = test_docker_gate.ScriptedSocket(response())
            session = dev.DockerSession()
            session.stream = transport
            with self.subTest(error=type(original).__name__), \
                    patch.object(transport, 'close', side_effect=OSError('SECRET close')) as close:
                with self.assertRaises(type(original)) as caught:
                    with session:
                        raise original
                self.assertIs(caught.exception, original)
                self.assertTrue(session.closed)
                self.assertIsNone(session.stream)
                self.assertIsNone(session.docker_failure)
                session.close()
                close.assert_called_once()

    def test_standalone_or_normal_exit_close_error_is_reported_once(self):
        for normal_exit in [False, True]:
            transport = test_docker_gate.ScriptedSocket(response())
            session = dev.DockerSession()
            session.stream = transport
            failure = OSError('SECRET close')
            with self.subTest(normal_exit=normal_exit), patch.object(transport, 'close', side_effect=failure) as close:
                with self.assertRaises(OSError) as caught:
                    if normal_exit:
                        with session:
                            pass
                    else:
                        session.close()
                self.assertIs(caught.exception, failure)
                self.assertTrue(session.closed)
                self.assertIsNone(session.stream)
                self.assertIsNone(session.docker_failure)
                session.close()
                session.__exit__(None, None, None)
                close.assert_called_once()

    def test_non_os_close_failure_propagates_and_does_not_repeat(self):
        cases = [(mode, failure) for mode in ['exchange', 'explicit', 'body']
                 for failure in [RuntimeError('SECRET close'), KeyboardInterrupt('SECRET close')]]
        for mode, failure in cases:
            transport = test_docker_gate.ScriptedSocket(response())
            session = dev.DockerSession(deadline=5)
            if mode != 'exchange':
                session.stream = transport
            with self.subTest(mode=mode, error=type(failure).__name__), \
                    patch.object(dev.time, 'monotonic', return_value=1), \
                    patch.object(dev.socket, 'socket', return_value=transport), \
                    patch.object(transport, 'connect', side_effect=TimeoutError('SECRET transport')), \
                    patch.object(transport, 'close', side_effect=failure) as close:
                with self.assertRaises(type(failure)) as caught:
                    if mode == 'explicit':
                        session.close()
                    else:
                        with session:
                            if mode == 'body':
                                raise ValueError('SECRET body')
                            session.exchange('GET', '/version')
                self.assertIs(caught.exception, failure)
                self.assertTrue(session.closed)
                self.assertIsNone(session.stream)
                session.close()
                close.assert_called_once()

    def test_close_failure_after_mutating_transmission_keeps_phase_and_no_replay(self):
        for phase in ['send', 'receive', 'idle_after', 'budget_after']:
            transport = test_docker_gate.ScriptedSocket(response())
            session = dev.DockerSession(deadline=5)
            current = [1]
            def send(raw):
                transport.request = raw[:16] if phase == 'send' else raw
                if phase == 'send':
                    raise TimeoutError('SECRET partial write')
            def receive(size):
                raise TimeoutError('SECRET lost response')
            def idle():
                if phase == 'idle_after':
                    dev.refuse('docker', 'docker_response_invalid')
                if phase == 'budget_after':
                    current[0] = 6
            with self.subTest(phase=phase), \
                    patch.object(dev.time, 'monotonic', side_effect=lambda: current[0]), \
                    patch.object(dev.socket, 'socket', return_value=transport) as factory, \
                    patch.object(transport, 'sendall', side_effect=send) as sent, \
                    patch.object(transport, 'recv', side_effect=receive if phase == 'receive' else transport.recv), \
                    patch.object(session, 'idle', side_effect=idle), \
                    patch.object(transport, 'close', side_effect=OSError('SECRET close')) as close:
                with self.assertRaises(dev.Refusal) as caught:
                    with session:
                        session.exchange('POST', '/v1.48/volumes/create', {})
                record = dev.refusal_result(caught.exception)
                self.assertEqual(record['code'], 'docker_response_invalid' if phase == 'idle_after' else 'docker_timeout')
                self.assertEqual(record['docker_failure'], {'schema_version': 1, 'operation': 'volume_create',
                    'phase': phase, 'elapsed_ms': 5000 if phase == 'budget_after' else 0})
                self.assertTrue(transport.request.startswith(b'POST '))
                for reuse in [session.__enter__, lambda: session.exchange('GET', '/version')]:
                    with self.assertRaises(dev.Refusal):
                        reuse()
                sent.assert_called_once()
                factory.assert_called_once()
                close.assert_called_once()
                self.assertNotIn('SECRET', json.dumps(record))

    def test_successful_exchange_then_close_failure_never_emits_qualifier_success(self):
        import qualify_startup
        transport = test_docker_gate.ScriptedSocket(response())
        session = dev.DockerSession(deadline=5)
        output = io.StringIO()
        exchanged = []
        def qualify(*args):
            with session:
                exchanged.append(session.exchange('GET', '/version'))
                return {'ok': True, 'runtime_ready': True}
        with patch.object(dev.time, 'monotonic', return_value=1), \
                patch.object(dev.socket, 'socket', return_value=transport), \
                patch.object(session, 'idle'), \
                patch.object(transport, 'close', side_effect=OSError('SECRET close')) as close, \
                patch.object(qualify_startup.startup, 'qualify', side_effect=qualify), redirect_stdout(output):
            code = qualify_startup.main(['--target', 'SECRET target', '--run-id', 'SECRET run',
                                          '--control', 'pinned-cli-postgres'])
        self.assertEqual(exchanged, [(200, {})])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue()), {'ok': False, 'runtime_ready': False,
                         'stage': 'startup', 'code': 'startup_proof_refused'})
        self.assertIsNone(session.stream)
        self.assertTrue(session.closed)
        self.assertIsNone(session.docker_failure)
        close.assert_called_once()
        self.assertNotIn('SECRET', output.getvalue())

    def test_failure_diagnostics_acceptance_connect_and_qualifier_json(self):
        import qualify_startup
        with patch.object(dev.socket, 'socket', side_effect=TimeoutError('SECRET socket/path?token')), \
                patch.object(dev.time, 'monotonic', return_value=1):
            with self.assertRaises(dev.Refusal) as caught:
                dev.docker_exchange('GET', '/version')
        expected = {'schema_version': 1, 'operation': 'daemon_version',
                    'phase': 'connect', 'elapsed_ms': 0}
        self.assertEqual(caught.exception.docker_failure, expected)
        output = io.StringIO()
        with patch.object(qualify_startup.startup, 'qualify', side_effect=caught.exception), redirect_stdout(output):
            status = qualify_startup.main(['--target', 'SECRET target', '--run-id', 'SECRET id',
                                          '--control', 'pinned-cli-postgres'])
        self.assertEqual(status, 2)
        self.assertEqual(json.loads(output.getvalue()), {'ok': False, 'runtime_ready': False,
                         'stage': 'docker', 'code': 'docker_timeout', 'docker_failure': expected})
        self.assertNotIn('SECRET', output.getvalue())

    def test_failure_phases_elapsed_and_permanent_closure(self):
        for operation, phase in [('connect', 'connect'), ('sendall', 'send'), ('recv', 'receive')]:
            transport = test_docker_gate.ScriptedSocket(response())
            current = [10.0]
            def timeout(*args):
                current[0] += .125
                raise TimeoutError('SECRET environment password SQL signed-url')
            with self.subTest(phase=phase), patch.object(dev.time, 'monotonic', side_effect=lambda: current[0]), \
                    patch.object(dev.socket, 'socket', return_value=transport) as factory, \
                    patch.object(transport, operation, side_effect=timeout), patch.object(transport, 'close') as close:
                session = dev.DockerSession()
                with self.assertRaises(dev.Refusal) as caught:
                    session.exchange('POST', '/v1.48/volumes/create', {'SECRET': 'payload'})
                expected = {'schema_version': 1, 'operation': 'volume_create', 'phase': phase, 'elapsed_ms': 125}
                self.assertEqual(dev.refusal_result(caught.exception)['docker_failure'], expected)
                self.assertTrue(session.closed)
                close.assert_called_once()
                for reuse in [lambda: session.exchange('GET', '/version'), session.__enter__]:
                    with self.assertRaises(dev.Refusal) as reused:
                        reuse()
                    self.assertEqual(reused.exception.code, 'docker_session_closed')
                    self.assertEqual(dev.refusal_result(reused.exception)['docker_failure'], expected)
                factory.assert_called_once()
                self.assertNotIn('SECRET', json.dumps(dev.refusal_result(caught.exception)))

    def test_framing_idle_and_processing_budget_phases(self):
        for expected_phase in ['receive', 'idle_before', 'idle_after', 'budget_after']:
            current = [0.0]
            transport = test_docker_gate.ScriptedSocket(b'SECRET framing' if expected_phase == 'receive' else response())
            def idle(session):
                if expected_phase in ['idle_before', 'idle_after']:
                    dev.refuse('docker', 'docker_response_invalid')
                current[0] = 2
            with self.subTest(phase=expected_phase), patch.object(dev.socket, 'socket', return_value=transport), \
                    patch.object(dev.time, 'monotonic', side_effect=lambda: current[0]), \
                    patch.object(dev.DockerSession, 'idle', idle):
                session = dev.DockerSession(deadline=1)
                if expected_phase == 'idle_before':
                    session.stream = transport
                with self.assertRaises(dev.Refusal) as caught:
                    session.exchange('GET', '/version')
                diagnostic = dev.refusal_result(caught.exception)['docker_failure']
                self.assertEqual(diagnostic['phase'], expected_phase)
                self.assertEqual(diagnostic['operation'], 'daemon_version')

    def test_invalid_sensitive_request_never_acquires_socket(self):
        for method, path, body in [('GET', '/SECRET?token=SECRET', None),
                                   ('POST', '/v1.48/volumes/create', {'key': 'SECRET' * 4000})]:
            with self.subTest(method=method), patch.object(dev.socket, 'socket') as factory:
                with dev.DockerSession() as session, self.assertRaises(dev.Refusal) as caught:
                    session.exchange(method, path, body)
                result = dev.refusal_result(caught.exception)
                self.assertEqual(result['docker_failure']['operation'], 'unvalidated')
                self.assertEqual(result['docker_failure']['phase'], 'validate')
                self.assertNotIn('SECRET', json.dumps(result))
                factory.assert_not_called()

    def test_elapsed_observation_is_nonnegative_and_capped(self):
        for end, expected in [(-1, 0), (10**20, 2147483647)]:
            current = [0]
            def timeout(*args):
                current[0] = end
                raise TimeoutError()
            with self.subTest(end=end), patch.object(dev.time, 'monotonic', side_effect=lambda: current[0]), \
                    patch.object(dev.socket, 'socket', side_effect=timeout):
                with self.assertRaises(dev.Refusal) as caught:
                    dev.docker_exchange('GET', '/version')
                self.assertEqual(caught.exception.docker_failure['elapsed_ms'], expected)

    def test_formatter_exact_validation_chain_cycles_and_ordinary_shape(self):
        valid = {'schema_version': 1, 'operation': 'container_archive', 'phase': 'receive', 'elapsed_ms': 0}
        outer = dev.Refusal('execution', 'execution_cleanup_unresolved')
        ordinary = {'ok': False, 'runtime_ready': False, 'stage': outer.stage, 'code': outer.code}
        self.assertEqual(dev.refusal_result(outer), ordinary)
        malformed = [None, [], dict(valid, secret='SECRET'), dict(valid, schema_version=True),
                     dict(valid, elapsed_ms=True), dict(valid, elapsed_ms=-1), dict(valid, elapsed_ms=2147483648),
                     dict(valid, elapsed_ms=1.0), dict(valid, operation='SECRET /route'),
                     dict(valid, phase='SECRET'), {k: v for k, v in valid.items() if k != 'phase'}]
        class Hostile(dict):
            def __iter__(self):
                raise AssertionError('must not inspect untrusted containers')
        malformed.append(Hostile(valid))
        class HostileKey(str):
            def __hash__(self):
                return super().__hash__()
            def __eq__(self, other):
                raise AssertionError('must not compare untrusted keys')
        malformed.append({HostileKey('schema_version'): 1, 'operation': 'daemon_version',
                          'phase': 'receive', 'elapsed_ms': 0})
        for value in malformed:
            outer.docker_failure = value
            self.assertEqual(dev.refusal_result(outer), ordinary)
        original = dev.Refusal('docker', 'docker_timeout')
        original.docker_failure = valid
        middle = RuntimeError('SECRET exception text')
        middle.__context__ = original
        outer.__cause__ = middle
        outer.docker_failure = dict(valid, operation='volume_remove')
        original.__context__ = outer
        self.assertEqual(dev.refusal_result(outer), dict(ordinary, docker_failure=valid))
        # Oversized chains terminate without serializing any exception text.
        top = dev.Refusal('startup', 'bounded')
        top.docker_failure = valid
        cursor = top
        for _ in range(100):
            cursor.__context__ = RuntimeError('SECRET')
            cursor = cursor.__context__
        self.assertNotIn('docker_failure', dev.refusal_result(top))

    def test_initial_observation_clock_failure_closes_existing_connection(self):
        transport = test_docker_gate.ScriptedSocket(response())
        session = dev.DockerSession(deadline=5)
        session.stream = transport
        original = RuntimeError('SECRET initial observation failure')
        with patch.object(dev.time, 'monotonic', side_effect=[original, 1]), \
                patch.object(dev.socket, 'socket') as factory, \
                patch.object(transport, 'sendall') as send, patch.object(transport, 'close') as close:
            with self.assertRaises(RuntimeError) as caught:
                session.exchange('GET', '/version')
            self.assertIs(caught.exception, original)
            self.assertTrue(session.closed)
            self.assertIsNone(session.stream)
            self.assertIsNone(session.docker_failure)
            self.assertNotIn('docker_failure', vars(original))
            close.assert_called_once()
            send.assert_not_called()
            factory.assert_not_called()
        with patch.object(dev.time, 'monotonic', return_value=1), patch.object(dev.socket, 'socket') as factory:
            with self.assertRaises(dev.Refusal) as reused:
                session.exchange('GET', '/version')
            self.assertEqual(reused.exception.code, 'docker_session_closed')
            self.assertNotIn('docker_failure', dev.refusal_result(reused.exception))
            factory.assert_not_called()

    def test_observation_clock_failure_preserves_refusal_and_closes(self):
        transport = test_docker_gate.ScriptedSocket(response())
        current = [False]
        def clock():
            if current[0]:
                raise RuntimeError('SECRET observation failure')
            return 0
        def timeout(*args):
            current[0] = True
            raise TimeoutError('SECRET original failure')
        with patch.object(dev.time, 'monotonic', side_effect=clock), \
                patch.object(dev.socket, 'socket', return_value=transport), \
                patch.object(transport, 'connect', side_effect=timeout), patch.object(transport, 'close') as close:
            session = dev.DockerSession()
            with self.assertRaises(dev.Refusal) as caught:
                session.exchange('GET', '/version')
            self.assertEqual(caught.exception.code, 'docker_timeout')
            self.assertTrue(session.closed)
            close.assert_called_once()
            self.assertNotIn('docker_failure', dev.refusal_result(caught.exception))

    def test_closed_operation_vocabulary_covers_existing_route_families(self):
        resource = 'a' * 64
        routes = [('GET', '/version', 'daemon_version'),
                  ('GET', '/v1.48/images/sha256:' + resource + '/json', 'image_inspect'),
                  ('GET', self.use_path(), 'volume_use')]
        for plural, kind in [('networks', 'network'), ('volumes', 'volume'), ('containers', 'container')]:
            routes.extend([('GET', '/v1.48/' + plural + '/' + resource + ('/json' if kind == 'container' else ''), kind + '_inspect'),
                           ('POST', '/v1.48/' + plural + '/create', kind + '_create'),
                           ('DELETE', '/v1.48/' + plural + '/' + resource, kind + '_remove')])
        for action in ['archive', 'start', 'stop', 'exec']:
            routes.append(('PUT' if action == 'archive' else 'POST', '/v1.48/containers/' + resource + '/' + action,
                           'exec_create' if action == 'exec' else 'container_' + action))
        routes.extend([('POST', '/v1.48/exec/' + resource + '/start', 'exec_start'),
                       ('GET', '/v1.48/exec/' + resource + '/json', 'exec_inspect')])
        for method, path, expected in routes:
            self.assertEqual(dev._docker_operation(method, path), expected)
            self.assertIn(expected, dev.DOCKER_OPERATIONS)

    def use_path(self):
        return ('/v1.48/containers/json?all=true&filters=%7B%22volume%22%3A%5B%22'
                'supabase_db_agriplatform-kdg-AAAAAAAAAAAAAAAAAAAAAA%22%5D%7D')

    def test_only_canonical_use_route_admits_array_response(self):
        for path in ['/version', '/v1.48/volumes/owned', '/v1.48/networks/owned',
                     '/v1.48/images/sha256:' + 'a' * 64 + '/json', self.use_path()]:
            transport = test_docker_gate.ScriptedSocket(response([]))
            with self.subTest(path=path), patch.object(dev.socket, 'socket', return_value=transport):
                if path == self.use_path():
                    self.assertEqual(dev.docker_exchange('GET', path), (200, []))
                else:
                    with self.assertRaises(dev.Refusal) as caught:
                        dev.docker_exchange('GET', path)
                    self.assertEqual(caught.exception.code, 'docker_response_invalid')

    def test_use_route_rejects_object_null_scalar_and_bad_framing(self):
        replies = [response({}), response('sensitive-container-marker'),
                   response(1), response(True),
                   b'HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\nnull',
                   b'HTTP/1.1 200 OK\r\nContent-Length: 1\r\n\r\n[',
                   b'HTTP/1.1 200 OK\r\nContent-Length: 999999\r\n\r\n',
                   response([]) + b'extra']
        for wire in replies:
            with self.subTest(wire=wire[:60]):
                transport = test_docker_gate.ScriptedSocket(wire)
                with patch.object(dev.socket, 'socket', return_value=transport), self.assertRaises(dev.Refusal) as caught:
                    dev.docker_exchange('GET', self.use_path())
                self.assertEqual(caught.exception.code, 'docker_response_invalid')

    def test_changed_use_query_refuses_before_socket_access(self):
        path = self.use_path()
        variants = [path.replace('all=true&', ''), path.replace('all=true', 'all=false'),
                    path + '&limit=1', path + '&all=true', path.replace('volume', 'name'),
                    path.replace('%22%5D%7D', '%22,%22foreign%22%5D%7D'),
                    path.replace('supabase_db_', 'foreign_'),
                    path.replace('AAAAAAAAAAAAAAAAAAAAAA', 'bad%22%5D%7D'),
                    '/v1.48/containers/json', '/v1.48/containers/json?all=true',
                    path.replace('%7B', '%7b')]
        for variant in variants:
            with self.subTest(path=variant), patch.object(dev.socket, 'socket') as connect:
                with dev.DockerSession() as session, self.assertRaises(dev.Refusal) as caught:
                    session.exchange('GET', variant)
                self.assertEqual(caught.exception.code, 'docker_request_invalid')
                connect.assert_not_called()
        for method, body in [('POST', None), ('GET', {}), ('DELETE', None)]:
            with patch.object(dev.socket, 'socket') as connect:
                with dev.DockerSession() as session, self.assertRaises(dev.Refusal) as caught:
                    session.exchange(method, path, body)
                self.assertEqual(caught.exception.code, 'docker_request_invalid')
                connect.assert_not_called()

    def test_partial_request_body_eof_releases_peer_promptly(self):
        peer = Peer([])
        with peer.serve() as endpoint:
            with socket.socket(socket.AF_UNIX) as client:
                client.connect(endpoint)
                client.sendall(b'POST /v1.48/volumes/create HTTP/1.1\r\nContent-Length: 9\r\n\r\n{}')
                client.shutdown(socket.SHUT_WR)
                self.assertTrue(peer.closed.wait(.5))
        self.assertEqual(peer.requests, [])

    def test_high_descriptor_supports_idle_observation(self):
        import fcntl
        left, right = socket.socketpair()
        self.addCleanup(left.close)
        self.addCleanup(right.close)
        high = socket.socket(fileno=fcntl.fcntl(left.fileno(), fcntl.F_DUPFD_CLOEXEC, 2048))
        self.addCleanup(high.close)
        session = dev.DockerSession()
        session.stream = high
        session.idle()
        right.sendall(b'extra')
        with self.assertRaises(dev.Refusal) as caught:
            session.idle()
        self.assertEqual(caught.exception.code, 'docker_response_invalid')

    def test_decode_processing_cannot_exceed_total_deadline(self):
        current = [0.0]
        transport = test_docker_gate.ScriptedSocket(response())
        def decode(raw):
            current[0] = 2.0
            return {}
        with patch.object(dev.socket, 'socket', return_value=transport), \
                patch.object(dev.time, 'monotonic', side_effect=lambda: current[0]), \
                patch.object(dev, 'decode', side_effect=decode):
            with self.assertRaises(dev.Refusal) as caught:
                dev.docker_exchange('GET', '/version', deadline=1)
        self.assertEqual(caught.exception.code, 'docker_timeout')

    def test_final_idle_processing_cannot_exceed_total_deadline(self):
        current = [0.0]
        transport = test_docker_gate.ScriptedSocket(response())
        def idle(session):
            current[0] = 2.0
        with patch.object(dev.socket, 'socket', return_value=transport), \
                patch.object(dev.time, 'monotonic', side_effect=lambda: current[0]), \
                patch.object(dev.DockerSession, 'idle', idle):
            with dev.DockerSession(deadline=1) as session, self.assertRaises(dev.Refusal) as caught:
                session.exchange('GET', '/version')
        self.assertEqual(caught.exception.code, 'docker_timeout')

    def test_final_observable_trailing_bytes_and_eof_refuse(self):
        for ending in ['bytes', 'eof']:
            peer = Peer([response()])
            ready = threading.Event()
            def finish(stream, count):
                stream.sendall(response())
                if ending == 'bytes':
                    stream.sendall(b'extra')
                else:
                    stream.shutdown(socket.SHUT_WR)
                ready.set()
                return True
            peer.hook = finish
            original_idle = dev.DockerSession.idle
            def synchronized_idle(session):
                self.assertTrue(ready.wait(1))
                return original_idle(session)
            with peer.serve() as endpoint, patch.object(dev.DockerSession, 'idle', synchronized_idle):
                with dev.DockerSession(_socket_path=endpoint) as session, self.assertRaises(dev.Refusal) as caught:
                    session.exchange('GET', '/version')
                self.assertEqual(caught.exception.code, 'docker_response_invalid')
            self.assertEqual(peer.connections, 1)
            self.assertEqual(len(peer.requests), 1)

    def test_sequential_requests_share_one_connection_and_release_descriptor(self):
        peer = Peer([test_docker_gate.version_response('28.0.0'), response()])
        with peer.serve() as endpoint:
            with dev.DockerSession(_socket_path=endpoint) as session:
                self.assertEqual(dev.docker_prerequisite(_session=session), '28.0.0')
                descriptor = session.stream
                self.assertEqual(session.exchange('GET', '/v1.48/volumes/owned'), (200, {}))
            self.assertEqual(descriptor.fileno(), -1)
            self.assertTrue(peer.closed.wait(1))
            with self.assertRaises(dev.Refusal):
                session.exchange('GET', '/version')
        self.assertEqual(peer.connections, 1)
        self.assertEqual(len(peer.requests), 2)

    def test_bad_second_response_poisoning_cannot_send_or_reconnect(self):
        samples = [b'bad\r\n\r\n',
                   b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\nContent-Length: 2\r\n\r\n{}',
                   b'HTTP/1.1 200 OK\r\nContent-Length: 999999\r\n\r\n',
                   response() + b'extra', response(headers=b'Connection: keep-alive, CLOSE\r\n'),
                   response(protocol=b'HTTP/1.0'), response(headers=b'Transfer-Encoding: chunked\r\n'),
                   response(headers=b'Content-Encoding: gzip\r\n'), response([]),
                   response(headers=b'X: bad\x00value\r\n')]
        for wire in samples:
            with self.subTest(wire=wire[:70]):
                peer = Peer([response(), wire])
                with peer.serve() as endpoint, dev.DockerSession(_socket_path=endpoint) as session:
                    session.exchange('GET', '/version')
                    descriptor = session.stream
                    with self.assertRaises(dev.Refusal) as caught:
                        session.exchange('GET', '/v1.48/volumes/owned')
                    self.assertEqual(caught.exception.code, 'docker_response_invalid')
                    self.assertEqual(descriptor.fileno(), -1)
                    with self.assertRaises(dev.Refusal):
                        session.exchange('GET', '/version')
                self.assertEqual(peer.connections, 1)
                self.assertEqual(len(peer.requests), 2)

    def test_truncated_second_response_refuses_on_eof(self):
        peer = Peer([response(), None])
        def truncate(stream, count):
            if count == 2:
                stream.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 9\r\n\r\n{}')
        peer.hook = truncate
        with peer.serve() as endpoint, dev.DockerSession(_socket_path=endpoint) as session:
            session.exchange('GET', '/version')
            with self.assertRaises(dev.Refusal) as caught:
                session.exchange('GET', '/v1.48/volumes/owned')
        self.assertEqual(caught.exception.code, 'docker_response_invalid')
        self.assertEqual(peer.connections, 1)
        self.assertEqual(len(peer.requests), 2)

    def test_slow_trickle_cannot_reset_total_deadline(self):
        peer = Peer([response()])
        def trickle(stream, count):
            for byte in response():
                stream.sendall(bytes([byte]))
                time.sleep(.02)
            return True
        peer.hook = trickle
        started = time.monotonic()
        with peer.serve() as endpoint, dev.DockerSession(_socket_path=endpoint, deadline=started + .1) as session:
            with self.assertRaises(dev.Refusal) as caught:
                session.exchange('GET', '/version')
        self.assertEqual(caught.exception.code, 'docker_timeout')
        self.assertLess(time.monotonic() - started, .5)
        self.assertEqual(peer.connections, 1)

    def test_disconnect_before_or_after_mutation_never_replays(self):
        for at in [1, 2, 3]:
            peer = Peer([response(), response(status=201), response()])
            peer.replies[at - 1] = None
            with peer.serve() as endpoint, dev.DockerSession(_socket_path=endpoint) as session:
                with self.assertRaises(dev.Refusal):
                    session.exchange('GET', '/version')
                    session.exchange('POST', '/v1.48/volumes/create', {})
                    session.exchange('GET', '/v1.48/volumes/owned')
                with self.assertRaises(dev.Refusal):
                    session.exchange('POST', '/v1.48/volumes/create', {})
            self.assertEqual(peer.connections, 1)
            self.assertEqual(sum(request.startswith(b'POST') for request in peer.requests), int(at > 1))

    def test_socket_path_replacement_cannot_receive_subsequent_requests(self):
        peer = Peer([response(), response()])
        with peer.serve() as endpoint, socket.socket(socket.AF_UNIX) as replacement:
            with dev.DockerSession(_socket_path=endpoint) as session:
                session.exchange('GET', '/version')
                Path(endpoint).unlink()
                replacement.bind(endpoint)
                replacement.listen()
                replacement.settimeout(.03)
                session.exchange('GET', '/v1.48/volumes/owned')
                with self.assertRaises(TimeoutError):
                    replacement.accept()
        self.assertEqual(peer.connections, 1)
        self.assertEqual(len(peer.requests), 2)

    def test_total_deadline_spans_individually_fast_requests(self):
        peer = Peer([response()] * 4)
        peer.hook = lambda stream, count: time.sleep(.06)
        with peer.serve() as endpoint, dev.DockerSession(_socket_path=endpoint, deadline=time.monotonic() + .1) as session:
            session.exchange('GET', '/version')
            with self.assertRaises(dev.Refusal) as result:
                session.exchange('GET', '/v1.48/volumes/owned')
        self.assertEqual(result.exception.code, 'docker_timeout')
        self.assertEqual(peer.connections, 1)

    def test_callback_exception_and_invalid_route_close_without_additional_send(self):
        peer = Peer([response()])
        with peer.serve() as endpoint:
            with self.assertRaises(RuntimeError):
                with dev.DockerSession(_socket_path=endpoint) as session:
                    session.exchange('GET', '/version')
                    descriptor = session.stream
                    raise RuntimeError('callback')
            self.assertEqual(descriptor.fileno(), -1)
        self.assertEqual(peer.connections, 1)
        with patch.object(dev.socket, 'socket') as connect:
            with dev.DockerSession() as session, self.assertRaises(dev.Refusal):
                session.exchange('DELETE', '/containers/foreign')
            connect.assert_not_called()

    def test_late_unsolicited_bytes_are_refused_before_next_request(self):
        peer = Peer([response()])
        sent = threading.Event()
        def trailing(stream, count):
            stream.sendall(response())
            time.sleep(.03)
            stream.sendall(b'unsolicited')
            sent.set()
            return True
        peer.hook = trailing
        with peer.serve() as endpoint, dev.DockerSession(_socket_path=endpoint) as session:
            session.exchange('GET', '/version')
            self.assertTrue(sent.wait(1))
            with self.assertRaises(dev.Refusal):
                session.exchange('GET', '/v1.48/volumes/owned')
        self.assertEqual(len(peer.requests), 1)


if __name__ == '__main__':
    unittest.main()
