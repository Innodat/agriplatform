"""Joint acquisition contracts against independent private Unix fixture oracles."""
import unittest

import test_daemon_images
import qualify_resources as proof
import resources


class Resources(unittest.TestCase):
    def setUp(self):
        self.owner = test_daemon_images.DaemonImages(methodName='runTest')
        self.owner.setUp()
        self.addCleanup(self.owner.doCleanups)

    def acquire(self, endpoint, **kwargs):
        return resources.acquire(self.owner.owner.args.target, self.owner.owner.args.run_id,
                                 _socket_path=endpoint, **kwargs)

    def daemon(self, control='positive', **kwargs):
        return proof.SyntheticDaemon(self.owner.owner.target, self.owner.owner.args.run_id,
                                     self.owner.expected, control, **kwargs)

    def test_combined_exact_order_single_connection_and_constructor(self):
        for control in ['positive', 'existing']:
            daemon = self.daemon(control)
            called = []
            def construct(target, result):
                called.append(result)
                self.assertEqual(result['images'], self.owner.expected)
                self.assertEqual(result['network']['Id'], daemon.network.network_id)
                self.assertEqual(result['volume']['Name'], daemon.volume.name)
                self.assertIs(result['runtime_ready'], False)
                return result
            with daemon.serve() as endpoint:
                result = self.acquire(endpoint, _handoff=construct)
            self.assertEqual(daemon.connections, 1)
            self.assertEqual(called, [result])
            daemon.validate_events()

    def test_negative_matrix_refuses_without_handoff_or_later_requests(self):
        import dev
        from unittest.mock import patch
        for control, code in proof.EXPECTED.items():
            with self.subTest(control=control):
                daemon, called = self.daemon(control), []
                with daemon.serve() as endpoint, patch.object(resources, 'SECONDS', .2 if control == 'slow' else 5):
                    with self.assertRaises(dev.Refusal) as caught:
                        self.acquire(endpoint, _handoff=lambda *args: called.append(args))
                self.assertEqual(caught.exception.code, code)
                self.assertEqual(called, [])
                daemon.validate_events(success=False)
                if control == 'use-late':
                    self.assertEqual(len(daemon.events), len(daemon.expected))
                else:
                    self.assertLess(len(daemon.events), len(daemon.expected))

    def test_late_volume_reference_refuses_before_constructor(self):
        import dev
        daemon, called = self.daemon(), []
        original = daemon.dispatch
        observations = []
        def dispatch(method, path, body):
            if path.startswith('/v1.48/containers/json?'):
                daemon.events.append((method, path, body))
                observations.append(path)
                return 200, [] if len(observations) == 1 else [{'Id': 'sensitive-container-marker'}]
            return original(method, path, body)
        daemon.dispatch = dispatch
        with daemon.serve() as endpoint:
            with self.assertRaises(dev.Refusal) as caught:
                self.acquire(endpoint, _handoff=lambda *args: called.append(args))
        self.assertEqual(caught.exception.code, 'volume_in_use')
        self.assertEqual(len(observations), 2)
        self.assertEqual(called, [])
        self.assertEqual(daemon.connections, 1)

    def test_final_use_query_invalid_outcomes_refuse_without_constructor(self):
        import dev
        cases = [('object', 200, {}, 'docker_response_invalid'),
                 ('null', 200, None, 'docker_response_invalid'),
                 ('scalar', 200, 'sensitive-container-marker', 'docker_response_invalid'),
                 ('created-status', 201, [], 'volume_use_failed'),
                 ('missing-status', 404, {}, 'volume_use_failed'),
                 ('error-status', 500, {'message': 'sensitive-container-marker'}, 'volume_use_failed'),
                 ('oversized', 200, [], 'docker_response_invalid')]
        for defect, status, response, code in cases:
            with self.subTest(defect=defect):
                daemon, called = self.daemon(), []
                original = daemon.dispatch
                def dispatch(method, path, body):
                    result = original(method, path, body)
                    if path == proof.volume_proof.expected_use_path(daemon.volume.name) and daemon.use_count == 2:
                        if defect == 'oversized':
                            daemon.control = 'use-oversized'
                        return status, response
                    return result
                daemon.dispatch = dispatch
                with daemon.serve() as endpoint, self.assertRaises(dev.Refusal) as caught:
                    self.acquire(endpoint, _handoff=lambda *args: called.append(args))
                self.assertEqual((caught.exception.stage, caught.exception.code),
                                 ('docker' if code.startswith('docker_') else 'volume', code))
                self.assertEqual(called, [])
                self.assertEqual(daemon.use_count, 2)
                daemon.control = 'positive'
                daemon.validate_events()

    def test_missing_owner_evidence_refuses_before_connection(self):
        import dev
        from unittest.mock import patch
        for path in [self.owner.owner.run / 'receipt.json', self.owner.owner.tool_receipt]:
            original = path.read_bytes()
            try:
                path.unlink()
                with patch.object(dev.socket, 'socket') as connect, self.assertRaises(dev.Refusal) as caught:
                    self.acquire('/unused')
                self.assertEqual((caught.exception.stage, caught.exception.code),
                                 ('startup', 'existing_images_required'))
                connect.assert_not_called()
            finally:
                path.write_bytes(original)
                path.chmod(0o600)

    def test_changed_evidence_before_each_post_and_handoff_prevents_progress(self):
        import dev
        paths = [self.owner.owner.target_path, self.owner.owner.tool_receipt,
                 self.owner.owner.run / 'receipt.json',
                 self.owner.owner.root / 'platform/deployment/resources.py',
                 self.owner.owner.root / 'platform/deployment/.local/kdg' / self.owner.owner.args.run_id / 'inventory.json',
                 self.owner.owner.root / 'platform/deployment/.local/kdg' / ('.network-' + self.owner.owner.args.run_id + '.lock')]
        for boundary in ['network', 'volume', 'handoff']:
            for path in paths:
                with self.subTest(boundary=boundary, path=path.name):
                    daemon, called = self.daemon(), []
                    original = path.read_bytes() if path.exists() else b''
                    if boundary == 'handoff':
                        at = len(daemon.expected)
                    else:
                        post = '/v1.48/' + ('networks' if boundary == 'network' else 'volumes') + '/create'
                        at = next(i for i, event in enumerate(daemon.expected, 1) if event[1] == post) - 1
                    def mutate(method, route):
                        if len(daemon.events) == at:
                            path.write_bytes(b'changed')
                    daemon.hook = mutate
                    try:
                        with daemon.serve() as endpoint, self.assertRaises((dev.Refusal, OSError, ValueError)):
                            self.acquire(endpoint, _handoff=lambda *args: called.append(args))
                        self.assertEqual(called, [])
                        self.assertEqual(daemon.events, daemon.expected[:at])
                    finally:
                        path.write_bytes(original)

    def test_late_resource_replacement_refuses_before_constructor(self):
        import dev
        for resource in ['network', 'volume', 'child', 'config']:
            daemon, called = self.daemon(), []
            final_start = len(daemon.expected) - 13
            if resource == 'network':
                at = len(daemon.expected) - 3
            elif resource == 'volume':
                at = len(daemon.expected) - 1
            else:
                at = final_start + (1 if resource == 'child' else 5)
            def replace(method, route):
                if len(daemon.events) != at:
                    return
                if resource == 'network':
                    daemon.network.network['Id'] = 'f' * 64
                elif resource == 'volume':
                    daemon.volume.volume['CreatedAt'] = '2026-10-16T00:00:00Z'
                else:
                    daemon.image_control = 'wrong-id'
            daemon.hook = replace
            with daemon.serve() as endpoint, self.assertRaises(dev.Refusal):
                self.acquire(endpoint, _handoff=lambda *args: called.append(args))
            self.assertEqual(called, [])
            self.assertEqual(daemon.events, daemon.expected[:at])

    def test_transport_failure_at_every_exchange_never_reconnects_or_replays(self):
        import dev
        for kind in ['disconnect_at', 'truncated_at', 'disconnect_after']:
            for request in range(1, len(self.daemon().expected) + 1):
                with self.subTest(kind=kind, request=request):
                    daemon, called = self.daemon(), []
                    setattr(daemon, kind, request)
                    original_idle = dev.DockerSession.idle
                    def synchronized_idle(session):
                        if kind == 'disconnect_after' and len(daemon.events) == request:
                            self.assertTrue(daemon.disconnected.wait(1))
                        return original_idle(session)
                    from unittest.mock import patch
                    with daemon.serve() as endpoint, patch.object(dev.DockerSession, 'idle', synchronized_idle):
                        with self.assertRaises(dev.Refusal):
                            self.acquire(endpoint, _handoff=lambda *args: called.append(args))
                    self.assertEqual(called, [])
                    self.assertEqual(daemon.connections, 1)
                    self.assertEqual(daemon.events, daemon.expected[:request])

    def test_single_total_deadline_does_not_reset_at_adapter_boundaries(self):
        import dev
        import time
        from unittest.mock import patch
        daemon, called = self.daemon(), []
        daemon.hook = lambda *args: time.sleep(.03)
        with daemon.serve() as endpoint, patch.object(resources, 'SECONDS', .4):
            with self.assertRaises(dev.Refusal) as caught:
                self.acquire(endpoint, _handoff=lambda *args: called.append(args))
        self.assertEqual(caught.exception.code, 'docker_timeout')
        self.assertEqual(called, [])
        self.assertEqual(daemon.connections, 1)
        self.assertLess(len(daemon.events), len(daemon.expected))

    def test_callback_exception_and_final_evidence_change_release_lock_and_connection(self):
        import dev
        import networks
        import time
        from unittest.mock import patch
        for kind in ['exception', 'evidence', 'deadline', 'post-owner']:
            daemon = self.daemon()
            path = self.owner.owner.tool_receipt
            raw = path.read_bytes()
            sessions = []
            real_session = dev.DockerSession
            offset = [0]
            def session_factory(**kwargs):
                session = real_session(**kwargs)
                sessions.append(session)
                return session
            def construct(target, result):
                if kind == 'exception':
                    raise RuntimeError('constructor failed')
                if kind == 'evidence':
                    path.write_bytes(b'changed')
                if kind == 'deadline':
                    offset[0] = 6
                if kind == 'post-owner':
                    self.assertFalse(sessions[0].closed)
                return result
            try:
                with daemon.serve() as endpoint, patch.object(dev, 'DockerSession', side_effect=session_factory), \
                        patch.object(resources, 'time', __import__('types').SimpleNamespace(monotonic=lambda: time.monotonic() + offset[0])):
                    if kind == 'post-owner':
                        import startup
                        owner_probe = startup.existing_images
                        calls = []
                        def probe(args):
                            calls.append(None)
                            if len(calls) == 2:
                                self.assertTrue(sessions[0].closed)
                                dev.refuse('daemon_images', 'image_evidence_changed')
                            return owner_probe(args)
                        with patch.object(startup, 'existing_images', side_effect=probe), self.assertRaises(dev.Refusal):
                            self.acquire(endpoint, _handoff=construct)
                    else:
                        with self.assertRaises((RuntimeError, dev.Refusal)):
                            self.acquire(endpoint, _handoff=construct)
                self.assertTrue(sessions[0].closed)
                run_path = self.owner.owner.root / 'platform/deployment/.local/kdg' / self.owner.owner.args.run_id
                with networks.run_lock(run_path, time.monotonic() + 1):
                    pass
            finally:
                path.write_bytes(raw)

    def test_socket_path_replacement_retains_original_peer(self):
        import socket
        from pathlib import Path
        daemon = self.daemon()
        with daemon.serve() as endpoint, socket.socket(socket.AF_UNIX) as replacement:
            def replace(method, route):
                if route == '/version':
                    Path(endpoint).unlink()
                    replacement.bind(endpoint)
                    replacement.listen()
            daemon.hook = replace
            self.acquire(endpoint)
            replacement.settimeout(.03)
            with self.assertRaises(TimeoutError):
                replacement.accept()
        daemon.validate_events()

    def test_same_run_concurrent_acquisition_refuses_before_second_connection(self):
        import dev
        import threading
        from concurrent.futures import ThreadPoolExecutor
        entered, release = threading.Event(), threading.Event()
        daemon = self.daemon()
        def pause(method, route):
            if route == '/version':
                entered.set()
                release.wait(2)
        daemon.hook = pause
        with daemon.serve() as endpoint, ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(self.acquire, endpoint)
            self.assertTrue(entered.wait(2))
            try:
                with self.assertRaises(dev.Refusal) as caught:
                    self.acquire(endpoint)
                self.assertEqual(caught.exception.code, 'network_busy')
                self.assertEqual(daemon.connections, 1)
            finally:
                release.set()
            first.result()
        daemon.validate_events()

    def test_observable_eof_at_final_evidence_boundaries_refuses(self):
        from contextlib import contextmanager
        import select
        import socket
        from unittest.mock import patch
        import daemon_images
        import dev
        for boundary in ['before-constructor', 'after-constructor']:
            with self.subTest(boundary=boundary):
                daemon, sessions, called, injected = self.daemon(), [], [], []
                session_type = dev.DockerSession
                owner_evidence = daemon_images.qualified_evidence
                def make_session(**kwargs):
                    session = session_type(**kwargs)
                    sessions.append(session)
                    return session
                @contextmanager
                def guarded(*args):
                    with owner_evidence(*args) as (target, plan, current):
                        def evidence():
                            current()
                            at_boundary = bool(called) == (boundary == 'after-constructor')
                            if (sessions and not sessions[0].closed and not injected
                                    and len(daemon.events) == len(daemon.expected) and at_boundary):
                                # Deterministic observable EOF at this evidence boundary.
                                sessions[0].stream.shutdown(socket.SHUT_RD)
                                poller = select.poll()
                                poller.register(sessions[0].stream, select.POLLIN)
                                self.assertTrue(poller.poll(0))
                                injected.append(True)
                        yield target, plan, evidence
                with daemon.serve() as endpoint, patch.object(dev, 'DockerSession', side_effect=make_session), \
                        patch.object(daemon_images, 'qualified_evidence', side_effect=guarded):
                    with self.assertRaises(dev.Refusal) as caught:
                        self.acquire(endpoint, _handoff=lambda target, result: called.append(True) or result)
                self.assertEqual((caught.exception.stage, caught.exception.code), ('docker', 'docker_response_invalid'))
                self.assertEqual(injected, [True])
                self.assertEqual(called, [] if boundary == 'before-constructor' else [True])
                self.assertTrue(sessions[0].closed)
                daemon.validate_events()

    def test_public_main_status_json_parser_and_constructor_wiring(self):
        from contextlib import redirect_stdout, redirect_stderr
        import io
        import json
        from unittest.mock import patch
        import startup
        args = ['--target', self.owner.owner.args.target, '--run-id', self.owner.owner.args.run_id]
        for control in proof.CONTROLS:
            with self.subTest(control=control):
                output, errors = io.StringIO(), io.StringIO()
                with redirect_stdout(output), redirect_stderr(errors), patch.object(resources, 'SECONDS', .2 if control == 'slow' else 5), \
                        patch.object(startup, 'invocation', wraps=startup.invocation) as constructor:
                    status = proof.main(args + ['--control', control])
                result = json.loads(output.getvalue())
                self.assertEqual(errors.getvalue(), '')
                self.assertNotIn('sensitive-marker', output.getvalue())
                self.assertIs(result['runtime_ready'], False)
                if control in ['positive', 'existing']:
                    self.assertEqual(status, 0)
                    self.assertTrue(result['ok'])
                    self.assertEqual((result['stage'], result['code']), ('resources', 'resources_synthetic_qualified'))
                    self.assertEqual(len(result['api_events']), 32 if control == 'positive' else 29)
                    constructor.assert_called_once()
                    self.assertEqual(constructor.call_args.args[0], '/synthetic/not-executed/supabase')
                else:
                    self.assertEqual(status, 2)
                    code = proof.EXPECTED[control]
                    stage = ('docker' if code.startswith('docker_') else
                             'daemon_images' if control.startswith('image-') else
                             'network' if control.startswith('network-') else 'volume')
                    self.assertEqual(result, {'ok': False, 'runtime_ready': False, 'stage': stage, 'code': code})
                    constructor.assert_not_called()
        for invalid in [[], args + ['--control', 'conflict'], args + ['--socket', '/tmp/foreign'],
                        ['--target', self.owner.owner.args.target], args + ['--contr', 'positive']]:
            output, errors = io.StringIO(), io.StringIO()
            with redirect_stdout(output), redirect_stderr(errors), patch.object(proof, 'SyntheticDaemon') as daemon:
                status = proof.main(invalid)
            self.assertEqual(status, 2)
            self.assertEqual(json.loads(output.getvalue()), {'ok': False, 'runtime_ready': False,
                                                           'stage': 'arguments', 'code': 'invalid_arguments'})
            self.assertEqual(errors.getvalue(), '')
            daemon.assert_not_called()

    def test_same_run_after_lost_create_response_inspects_and_reuses_without_duplicate_post(self):
        import dev
        for control in ['lost-network-response', 'lost-volume-response']:
            with self.subTest(control=control):
                daemon = self.daemon(control)
                with daemon.serve() as endpoint:
                    with self.assertRaises(dev.Refusal) as caught:
                        self.acquire(endpoint)
                    self.assertEqual(caught.exception.code, 'docker_response_invalid')
                    daemon.validate_events(success=False)
                    self.assertTrue(daemon.network.present)
                    if control == 'lost-volume-response':
                        self.assertTrue(daemon.volume.present)
                    first_events = daemon.events.copy()
                    daemon.events.clear()
                    daemon.connections = 0
                    daemon.disconnect_at = None
                    daemon.control = daemon.image_control = 'positive'
                    daemon.expected = daemon.expected_events()
                    result = self.acquire(endpoint)
                daemon.validate_events()
                self.assertEqual(result['network']['Id'], daemon.network.network_id)
                self.assertEqual(result['volume']['Name'], daemon.volume.name)
                all_events = first_events + daemon.events
                for resource in ['networks', 'volumes']:
                    self.assertEqual(sum(event[:2] == ('POST', '/v1.48/' + resource + '/create') for event in all_events), 1)
                self.assertFalse(any(event[:2] == ('POST', '/v1.48/networks/create') for event in daemon.events))
                if control == 'lost-volume-response':
                    self.assertFalse(any(event[0] == 'POST' for event in daemon.events))

    def test_private_network_conflict_recovers_owned_winner_and_finishes_joint_checks(self):
        daemon, called = self.daemon(_network_conflict=True), []
        with daemon.serve() as endpoint:
            result = self.acquire(endpoint, _handoff=lambda target, value: called.append(value) or value)
        daemon.validate_events()
        self.assertEqual(daemon.events[10][0:2], ('POST', '/v1.48/networks/create'))
        self.assertEqual(daemon.events[11], ('GET', '/v1.48/networks/' + daemon.network.name, None))
        self.assertEqual(called, [result])
        self.assertEqual(result['images'], self.owner.expected)
        self.assertEqual(result['volume']['Name'], daemon.volume.name)

    def test_same_byte_evidence_replacement_or_restored_write_blocks_each_boundary(self):
        import dev
        import os
        for boundary in ['network', 'volume', 'handoff']:
            for path in [self.owner.owner.run / 'postgres-linux-amd64.json', self.owner.owner.tool_receipt]:
                for mutation in ['replace', 'restore']:
                    with self.subTest(boundary=boundary, path=path.name, mutation=mutation):
                        daemon, called = self.daemon(), []
                        raw, before = path.read_bytes(), path.stat()
                        if boundary == 'handoff':
                            at = len(daemon.expected)
                        else:
                            route = '/v1.48/' + ('networks' if boundary == 'network' else 'volumes') + '/create'
                            at = next(i for i, event in enumerate(daemon.expected, 1) if event[1] == route) - 1
                        def mutate(method, route):
                            if len(daemon.events) != at:
                                return
                            if mutation == 'replace':
                                replacement = path.with_name('replacement-proof')
                                replacement.write_bytes(raw)
                                replacement.chmod(0o600)
                                replacement.replace(path)
                                self.assertNotEqual(path.stat().st_ino, before.st_ino)
                            else:
                                path.write_bytes(b'changed')
                                path.write_bytes(raw)
                                os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
                            self.assertEqual(path.read_bytes(), raw)
                        daemon.hook = mutate
                        with daemon.serve() as endpoint, self.assertRaises(dev.Refusal) as caught:
                            self.acquire(endpoint, _handoff=lambda *args: called.append(args))
                        self.assertEqual((caught.exception.stage, caught.exception.code), ('daemon_images', 'image_evidence_changed'))
                        self.assertEqual(daemon.events, daemon.expected[:at])
                        self.assertEqual(called, [])

    def test_final_network_and_volume_checks_reject_foreign_unsafe_missing_and_error(self):
        import dev
        for resource, checks in [('network', [28, 29, 30]), ('volume', [31])]:
            for at in checks:
                for defect in ['foreign', 'unsafe', 'missing', 'error']:
                    with self.subTest(resource=resource, request=at, defect=defect):
                        daemon, called = self.daemon(), []
                        owner = daemon.network if resource == 'network' else daemon.volume
                        def mutate(method, route):
                            if len(daemon.events) != at:
                                return
                            actual = owner.network if resource == 'network' else owner.volume
                            if defect == 'foreign':
                                actual['Labels']['io.agriplatform.env.owner'] = 'foreign'
                            elif defect == 'unsafe':
                                actual['Options'] = ({'com.docker.network.bridge.host_binding_ipv4': '0.0.0.0'}
                                                     if resource == 'network' else {'device': '/private'})
                            elif defect == 'missing':
                                owner.present = False
                            else:
                                owner.control = 'daemon-error'
                        daemon.hook = mutate
                        with daemon.serve() as endpoint, self.assertRaises(dev.Refusal) as caught:
                            self.acquire(endpoint, _handoff=lambda *args: called.append(args))
                        suffix = ('not_run_owned' if defect in ['foreign', 'unsafe'] else
                                  'replaced' if resource == 'network' and defect == 'missing' else
                                  'changed' if defect == 'missing' else 'inspection_failed')
                        self.assertEqual((caught.exception.stage, caught.exception.code), (resource, resource + '_' + suffix))
                        self.assertEqual(daemon.events, daemon.expected[:at])
                        self.assertEqual(daemon.connections, 1)
                        self.assertEqual(called, [])
