"""Prepared volume acquisition acceptance; private synthetic daemon only."""
import copy
import json
import os
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import test_dev
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dev
import startup
import volumes
import qualify_volumes as proof


class VolumeAcceptance(unittest.TestCase):
    setUp = test_dev.PreparationAcceptance.setUp
    invoke = test_dev.PreparationAcceptance.invoke

    def test_acquisition_retains_original_peer_when_socket_path_is_replaced(self):
        import socket
        self.prepare()
        daemon = proof.SyntheticDaemon(self.target, self.run_id)
        with daemon.serve() as endpoint, socket.socket(socket.AF_UNIX) as replacement:
            def replace(method, path):
                if path == '/version':
                    Path(endpoint).unlink()
                    replacement.bind(endpoint)
                    replacement.listen()
            daemon.hook = replace
            self.acquire(endpoint)
            replacement.settimeout(.03)
            with self.assertRaises(TimeoutError):
                replacement.accept()
        daemon.validate_events()
        self.assertEqual(daemon.connections, 1)

    def test_disconnect_at_every_exchange_never_reconnects_or_replays(self):
        self.prepare()
        for control, count in [('positive', 4), ('existing', 3)]:
            for when in ['disconnect_at', 'truncated_at', 'disconnect_after']:
                for request in range(1, count + 1):
                    with self.subTest(control=control, when=when, request=request):
                        daemon = proof.SyntheticDaemon(self.target, self.run_id, control)
                        setattr(daemon, when, request)
                        original_idle = dev.DockerSession.idle
                        def synchronized_idle(session):
                            if when == 'disconnect_after' and len(daemon.events) == request:
                                self.assertTrue(daemon.disconnected.wait(1))
                            return original_idle(session)
                        with daemon.serve() as endpoint, patch.object(dev.DockerSession, 'idle', synchronized_idle):
                            with self.assertRaises(dev.Refusal):
                                self.acquire(endpoint)
                        self.assertEqual(daemon.connections, 1)
                        self.assertEqual(len(daemon.events), request)
                        self.assertLessEqual(sum(event[0] == 'POST' for event in daemon.events), 1)

    def prepare(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout)
        patcher = patch.object(dev, 'ROOT', self.root)
        patcher.start()
        self.addCleanup(patcher.stop)

    def acquire(self, endpoint, **kwargs):
        return volumes.acquire(self.input, self.run_id, _socket_path=endpoint, **kwargs)

    def test_absent_acquires_exact_volume_and_hands_complete_descriptor_to_startup(self):
        self.prepare()
        inventory = (self.run / 'inventory.json').read_bytes()
        daemon = proof.SyntheticDaemon(self.target, self.run_id)
        with daemon.serve() as endpoint:
            result = self.acquire(endpoint)
        daemon.validate_events()
        self.assertTrue(result['post_attempted'])
        self.assertFalse(result['runtime_ready'])
        self.assertNotIn('Mountpoint', result['volume'])
        self.assertEqual(result['volume']['Name'], 'supabase_db_' + dev.project_identity(self.target, self.run_id))
        fixture = {'network': startup.fixture_network(self.target, self.run_id),
                   'project': dev.project_identity(self.target, self.run_id),
                   'target_id': self.target['target_id'], 'run_id': self.run_id,
                   'volume': result['volume']}
        code, output, _ = startup.fixture_command('docker', ['volume', 'inspect', result['volume']['Name']], fixture, [])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output), [result['volume']])
        self.assertEqual((self.run / 'inventory.json').read_bytes(), inventory)

    def test_all_private_controls(self):
        self.prepare()
        for control in proof.CONTROLS:
            if control == 'missing-preparation':
                continue
            with self.subTest(control=control):
                daemon = proof.SyntheticDaemon(self.target, self.run_id, control)
                with daemon.serve() as endpoint:
                    if control in proof.EXPECTED:
                        with self.assertRaises(dev.Refusal) as caught:
                            self.acquire(endpoint)
                        self.assertEqual(caught.exception.code, proof.EXPECTED[control])
                    else:
                        result = self.acquire(endpoint)
                        self.assertEqual(result['post_attempted'], control != 'existing')
                daemon.validate_events()

    def test_descriptor_requires_exact_safety_fields_and_types(self):
        self.prepare()
        expected = proof.SyntheticDaemon(self.target, self.run_id, 'existing').volume
        for key in ['Name', 'Driver', 'Scope', 'Labels', 'Options']:
            candidate = copy.deepcopy(expected)
            del candidate[key]
            with self.subTest(missing=key), self.assertRaises(dev.Refusal):
                startup.volume_descriptor(candidate, self.target, self.run_id)
        for key, value in [('Name', 'other'), ('Driver', 'nfs'), ('Scope', 'global'),
                           ('Labels', {}), ('Options', []), ('Options', {'device': '/private'}),
                           ('ClusterVolume', {}), ('ClusterVolume', None),
                           ('CreatedAt', None), ('CreatedAt', 'x' * 129)]:
            candidate = dict(expected, **{key: value})
            with self.subTest(key=key, value=value), self.assertRaises(dev.Refusal):
                startup.volume_descriptor(candidate, self.target, self.run_id)
        for options in [None, {}]:
            self.assertEqual(startup.volume_descriptor(dict(expected, Options=options), self.target, self.run_id)['Options'], options)

    def refused(self, endpoint, code):
        with self.assertRaises(dev.Refusal) as caught:
            self.acquire(endpoint)
        self.assertEqual(caught.exception.code, code)

    def test_missing_preparation_no_daemon_access(self):
        self.input.write_text(json.dumps(self.target))
        with patch.object(dev, 'ROOT', self.root), patch.object(dev.socket, 'socket') as connect:
            with self.assertRaises(dev.Refusal) as caught:
                self.acquire('/nonexistent')
        self.assertEqual(caught.exception.code, 'prepared_run_required')
        connect.assert_not_called()

    def test_preparation_and_source_changes_during_daemon_exchange_refuse(self):
        self.prepare()
        for kind in ['source', 'target', 'inventory', 'run_replacement']:
            with self.subTest(kind=kind):
                source = self.root / 'platform/deployment/volumes.py'
                original_source, original_target = source.read_bytes(), self.input.read_bytes()
                inventory = self.run / 'inventory.json'
                original_inventory = inventory.read_bytes()
                daemon = proof.SyntheticDaemon(self.target, self.run_id, 'existing')
                def mutate(method, path):
                    if path != '/version':
                        return
                    if kind == 'source':
                        source.write_bytes(original_source + b'\n')
                    elif kind == 'target':
                        self.input.write_bytes(original_target + b'\n')
                    elif kind == 'inventory':
                        inventory.write_bytes(b'{}')
                    else:
                        self.run.rename(self.run.with_suffix('.old'))
                        import shutil
                        shutil.copytree(self.run.with_suffix('.old'), self.run)
                daemon.hook = mutate
                with daemon.serve() as endpoint, self.assertRaises(dev.Refusal):
                    self.acquire(endpoint)
                self.assertEqual(len(daemon.events), 1)
                source.write_bytes(original_source)
                self.input.write_bytes(original_target)
                inventory.write_bytes(original_inventory)

    def test_concurrent_same_run_is_bounded_and_no_second_daemon_access(self):
        self.prepare()
        entered, release = threading.Event(), threading.Event()
        daemon = proof.SyntheticDaemon(self.target, self.run_id, 'existing')
        def hold(method, path):
            if path == '/version':
                entered.set()
                release.wait(2)
        daemon.hook = hold
        results = []
        with daemon.serve() as endpoint:
            worker = threading.Thread(target=lambda: results.append(self.acquire(endpoint)))
            worker.start()
            self.assertTrue(entered.wait(1))
            before = time.monotonic()
            self.refused(endpoint, 'network_busy')
            self.assertLess(time.monotonic() - before, 1)
            self.assertEqual(len(daemon.events), 1)
            release.set()
            worker.join(timeout=2)
        self.assertEqual(len(results), 1)

    def test_symlink_unprotected_and_replaced_lock_refuse(self):
        self.prepare()
        lock = self.run.parent / ('.network-' + self.run_id + '.lock')
        outsider = self.root / 'outside'
        outsider.write_text('sensitive-marker')
        lock.symlink_to(outsider)
        with patch.object(dev.socket, 'socket') as connect, self.assertRaises(OSError):
            self.acquire('/nonexistent/private.sock')
        connect.assert_not_called()
        lock.unlink()
        lock.write_text('')
        lock.chmod(0o644)
        with patch.object(dev.socket, 'socket') as connect:
            self.refused('/nonexistent/private.sock', 'network_lock_unsafe')
        connect.assert_not_called()
        lock.chmod(0o600)
        daemon = proof.SyntheticDaemon(self.target, self.run_id, 'existing')
        def replace(method, path):
            if path == '/version':
                lock.unlink()
                lock.write_text('')
                lock.chmod(0o600)
        daemon.hook = replace
        with daemon.serve() as endpoint:
            self.refused(endpoint, 'network_lock_changed')
        self.assertEqual(len(daemon.events), 1)
        self.assertEqual(outsider.read_text(), 'sensitive-marker')

    def test_one_operation_deadline_spans_version_and_network_requests(self):
        self.prepare()
        daemon = proof.SyntheticDaemon(self.target, self.run_id, 'existing')
        daemon.hook = lambda method, path: time.sleep(.09)
        with daemon.serve() as endpoint, patch.object(volumes, 'SECONDS', .15):
            self.refused(endpoint, 'docker_timeout')
        self.assertEqual(len(daemon.events), 2)
        self.assertFalse(any(method == 'POST' for method, _, _ in daemon.events))

    def test_lost_response_later_attempt_inspects_without_post(self):
        self.prepare()
        daemon = proof.SyntheticDaemon(self.target, self.run_id, 'lost-response')
        with daemon.serve() as endpoint:
            self.refused(endpoint, 'docker_response_invalid')
            daemon.control = 'existing'
            result = self.acquire(endpoint)
        self.assertFalse(result['post_attempted'])
        self.assertEqual(sum(event[0] == 'POST' for event in daemon.events), 1)
        self.assertEqual(daemon.events[4], ('GET', proof.API_PREFIX + daemon.name, None))

    def test_changed_evidence_before_post_and_handoff_refuses(self):
        self.prepare()
        source = self.root / 'platform/deployment/volumes.py'
        original = source.read_bytes()
        for control, index in [('positive', 2), ('existing', 3)]:
            daemon = proof.SyntheticDaemon(self.target, self.run_id, control)
            def change(method, path):
                if len(daemon.events) == index:
                    source.write_bytes(original + b'\n')
            daemon.hook = change
            handoff = []
            with daemon.serve() as endpoint, self.assertRaises(dev.Refusal):
                self.acquire(endpoint, _handoff=lambda *args: handoff.append(args))
            self.assertEqual(handoff, [])
            self.assertFalse(any(event[0] == 'POST' for event in daemon.events))
            source.write_bytes(original)

    def test_startup_refuses_incomplete_or_mismatched_volume(self):
        target = self.target
        fixture = {'project': dev.project_identity(target, self.run_id),
                   'target_id': target['target_id'], 'run_id': self.run_id,
                   'network': startup.fixture_network(target, self.run_id)}
        name = 'supabase_db_' + fixture['project']
        for volume in [None, {'Name': name}, dict(startup.fixture_volume(target, self.run_id), Name='foreign')]:
            with self.subTest(volume=volume), self.assertRaises(dev.Refusal):
                startup.fixture_command('docker', ['volume', 'inspect', name], dict(fixture, volume=volume), [])

    def test_network_lock_blocks_volume_adapter_before_daemon_contact(self):
        self.prepare()
        entered, release = threading.Event(), threading.Event()
        def hold():
            with volumes.networks.run_lock(self.run, time.monotonic() + 3):
                entered.set()
                release.wait(2)
        worker = threading.Thread(target=hold)
        worker.start()
        self.assertTrue(entered.wait(1))
        try:
            with patch.object(dev.socket, 'socket') as connect:
                self.refused('/nonexistent', 'network_busy')
            connect.assert_not_called()
        finally:
            release.set()
            worker.join(2)

    def test_changed_target_inventory_and_lock_at_mutation_and_handoff(self):
        self.prepare()
        inventory = self.run / 'inventory.json'
        lock = self.run.parent / ('.network-' + self.run_id + '.lock')
        for kind in ['target', 'inventory', 'lock']:
            for control, index in [('positive', 2), ('existing', 3)]:
                with self.subTest(kind=kind, control=control):
                    original_target, original_inventory = self.input.read_bytes(), inventory.read_bytes()
                    daemon = proof.SyntheticDaemon(self.target, self.run_id, control)
                    def mutate(method, path):
                        if len(daemon.events) != index:
                            return
                        if kind == 'target':
                            self.input.write_bytes(original_target + b'\n')
                        elif kind == 'inventory':
                            inventory.write_bytes(b'{}')
                        else:
                            lock.unlink()
                            lock.write_bytes(b'')
                            lock.chmod(0o600)
                    daemon.hook = mutate
                    handoff = []
                    with daemon.serve() as endpoint, self.assertRaises(dev.Refusal):
                        self.acquire(endpoint, _handoff=lambda *args: handoff.append(args))
                    self.assertEqual(handoff, [])
                    self.assertFalse(any(event[0] == 'POST' for event in daemon.events))
                    self.input.write_bytes(original_target)
                    inventory.write_bytes(original_inventory)

    def test_changed_source_inside_handoff_refuses_result(self):
        self.prepare()
        source = self.root / 'platform/deployment/volumes.py'
        daemon = proof.SyntheticDaemon(self.target, self.run_id, 'existing')
        def handoff(target, result):
            source.write_bytes(source.read_bytes() + b'\n')
            return result
        with daemon.serve() as endpoint, self.assertRaises(dev.Refusal) as caught:
            self.acquire(endpoint, _handoff=handoff)
        self.assertEqual(caught.exception.code, 'source_changed')

    def test_create_response_and_reinspection_must_match(self):
        self.prepare()
        for kind, code in [('wrong-response', 'volume_not_run_owned'),
                           ('wrong-reinspection', 'volume_changed'),
                           ('missing-reinspection', 'volume_changed'),
                           ('error-status', 'volume_create_failed')]:
            daemon = proof.SyntheticDaemon(self.target, self.run_id)
            original = daemon.dispatch
            def altered(method, path, body):
                status, response = original(method, path, body)
                if method == 'POST':
                    if kind == 'wrong-response':
                        response['Labels'] = {}
                    elif kind == 'wrong-reinspection':
                        daemon.volume['CreatedAt'] = 'later'
                    elif kind == 'missing-reinspection':
                        daemon.present = False
                    else:
                        status = 500
                return status, response
            daemon.dispatch = altered
            with self.subTest(kind=kind), daemon.serve() as endpoint:
                self.refused(endpoint, code)
            self.assertEqual(sum(event[0] == 'POST' for event in daemon.events), 1)

    def test_public_endpoint_override_is_rejected(self):
        import io
        from contextlib import redirect_stdout
        output = io.StringIO()
        with redirect_stdout(output):
            status = proof.main(['--target', str(self.input), '--run-id', self.run_id,
                                 '--socket', '/private'])
        self.assertEqual(status, 2)
        self.assertEqual(json.loads(output.getvalue())['code'], 'invalid_arguments')

    def test_public_output_excludes_uncontrolled_timestamp(self):
        import io
        from contextlib import redirect_stdout
        self.prepare()
        daemon = proof.SyntheticDaemon(self.target, self.run_id)
        daemon.volume['CreatedAt'] = 'sensitive-marker'
        output = io.StringIO()
        with patch.object(proof, 'SyntheticDaemon', return_value=daemon), redirect_stdout(output):
            status = proof.main(['--target', str(self.input), '--run-id', self.run_id])
        self.assertEqual(status, 0, output.getvalue())
        self.assertNotIn('sensitive-marker', output.getvalue())
        self.assertNotIn('CreatedAt', json.loads(output.getvalue())['volume'])

    def test_racing_owned_preserves_existing_winner_observation(self):
        self.prepare()
        daemon = proof.SyntheticDaemon(self.target, self.run_id, 'racing-owned')
        before = daemon.volume['CreatedAt']
        with daemon.serve() as endpoint:
            result = self.acquire(endpoint)
        daemon.validate_events()
        self.assertNotEqual(result['volume']['CreatedAt'], before)
        self.assertEqual(result['volume']['CreatedAt'], '2026-10-14T00:00:00Z')
        self.assertTrue(result['post_attempted'])

    def test_two_runs_acquire_independently_and_reject_cross_run_descriptor(self):
        import uuid
        self.prepare()
        first = self.run_id
        second = str(uuid.uuid4())
        self.run_id = second
        self.assertEqual(self.invoke().returncode, 0)
        self.run_id = first
        daemon1 = proof.SyntheticDaemon(self.target, first)
        daemon2 = proof.SyntheticDaemon(self.target, second)
        entered, release = threading.Event(), threading.Event()
        results, errors = [], []
        def hold(method, path):
            if path == '/version':
                entered.set()
                release.wait(3)
        daemon1.hook = hold
        def acquire_first(endpoint):
            try:
                results.append(self.acquire(endpoint))
            except BaseException as error:
                errors.append(error)
        with daemon1.serve() as endpoint1, daemon2.serve() as endpoint2:
            worker = threading.Thread(target=acquire_first, args=(endpoint1,))
            worker.start()
            try:
                self.assertTrue(entered.wait(1))
                other = volumes.acquire(self.input, second, _socket_path=endpoint2)
            finally:
                release.set()
                worker.join(3)
        self.assertEqual(errors, [])
        self.assertEqual(len(results), 1)
        self.assertNotEqual(results[0]['volume']['Name'], other['volume']['Name'])
        for result, own, foreign in [(results[0], first, second), (other, second, first)]:
            self.assertEqual(result['volume']['Labels']['io.agriplatform.env.run'], own)
            self.assertTrue((self.run.parent / ('.network-' + own + '.lock')).exists())
            with self.assertRaises(dev.Refusal):
                startup.volume_descriptor(result['volume'], self.target, foreign)
        daemon1.validate_events()
        daemon2.validate_events()
