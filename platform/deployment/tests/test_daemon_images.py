"""Owner-to-private-daemon contracts and safe refusal controls."""
from concurrent.futures import ThreadPoolExecutor
import copy
import json
import io
import os
from pathlib import Path
import shutil
import threading
import time
import unittest
import uuid
from contextlib import nullcontext, redirect_stdout, redirect_stderr
from types import SimpleNamespace
from unittest.mock import patch

import test_images
import dev
import daemon_images
import startup
import qualify_daemon_images as proof


class DaemonImages(unittest.TestCase):
    def setUp(self):
        self.owner = test_images.PersistenceGuards(methodName='runTest')
        self.owner.setUp()
        self.addCleanup(self.owner.doCleanups)
        for name in startup.PROOF_SOURCES:
            path = self.owner.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(test_images.ROOT / name, path)
        self.owner.qualify()
        self.expected = proof.expected_images(self.owner.args.run_id)

    def acquire(self, endpoint):
        return daemon_images.acquire(self.owner.args.target, self.owner.args.run_id, _socket_path=endpoint)

    def expected_events(self):
        return ([('GET', '/version', None)]
                + [('GET', '/v1.48/images/' + child + '/json', None) for child in self.expected]
                + [('GET', '/v1.48/images/' + value['Id'] + '/json', None) for value in self.expected.values()])

    def public(self, control='positive'):
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            status = proof.main(['--target', self.owner.args.target, '--run-id', self.owner.args.run_id,
                                 '--control', control])
        self.assertEqual(errors.getvalue(), '')
        self.assertNotIn('sensitive-marker', output.getvalue())
        return status, json.loads(output.getvalue())

    def test_late_child_and_config_rejections_have_exact_event_prefix(self):
        for request in [4, 5, 7, 8, 9]:
            for control, code in [('missing', 'image_missing'), ('wrong-id', 'image_identity_mismatch')]:
                with self.subTest(request=request, control=control):
                    daemon = proof.SyntheticDaemon(self.expected)
                    def fail_late(method, route):
                        if len(daemon.events) == request:
                            daemon.control = control
                    daemon.hook = fail_late
                    with daemon.serve() as endpoint, self.assertRaises(dev.Refusal) as caught:
                        self.acquire(endpoint)
                    self.assertEqual(caught.exception.code, code)
                    self.assertEqual(daemon.events, self.expected_events()[:request])

    def test_same_bytes_cannot_hide_evidence_replacement_or_restored_writes(self):
        for path in [self.owner.run / 'postgres-linux-amd64.json', self.owner.tool_receipt]:
            for mutation in ['replace', 'restore']:
                with self.subTest(path=path.name, mutation=mutation):
                    raw, before = path.read_bytes(), path.stat()
                    daemon = proof.SyntheticDaemon(self.expected)
                    def mutate(method, route):
                        if len(daemon.events) != 5:
                            return
                        if mutation == 'replace':
                            replacement = path.with_name('replacement-test')
                            replacement.write_bytes(raw)
                            replacement.chmod(0o600)
                            replacement.replace(path)
                            self.assertNotEqual(path.stat().st_ino, before.st_ino)
                        else:
                            path.write_bytes(b'changed')
                            path.write_bytes(raw)
                            # Force distinct mtime even on coarse filesystems.
                            os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns + 1000000000))
                        self.assertEqual(path.read_bytes(), raw)
                    daemon.hook = mutate
                    with daemon.serve() as endpoint, self.assertRaises(dev.Refusal) as caught:
                        self.acquire(endpoint)
                    self.assertEqual(caught.exception.code, 'image_evidence_changed')
                    self.assertEqual(daemon.events, self.expected_events()[:5])

    def test_public_missing_receipts_refuse_safely_before_daemon_traffic(self):
        for path, stage, code in [(self.owner.run / 'receipt.json', 'startup', 'existing_images_required'),
                                  (self.owner.tool_receipt, 'startup', 'existing_images_required')]:
            raw = path.read_bytes()
            try:
                path.unlink()
                with patch.object(proof, 'SyntheticDaemon') as daemon, patch.object(dev, 'docker_exchange') as exchange:
                    status, result = self.public()
                self.assertEqual(status, 2)
                self.assertEqual(result, {'ok': False, 'runtime_ready': False, 'stage': stage, 'code': code})
                daemon.assert_not_called()
                exchange.assert_not_called()
            finally:
                path.write_bytes(raw)
                path.chmod(0o600)

    def test_public_sensitive_error_projection(self):
        for control, stage, code in [('malformed', 'docker', 'docker_response_invalid'),
                                     ('daemon-error', 'daemon_images', 'image_inspection_failed'),
                                     ('wrong-id', 'daemon_images', 'image_identity_mismatch')]:
            with self.subTest(control=control):
                status, result = self.public(control)
                self.assertEqual(status, 2)
                self.assertEqual(result, {'ok': False, 'runtime_ready': False, 'stage': stage, 'code': code})

    def test_deadline_expires_at_late_config_inspections(self):
        self.assertEqual(daemon_images.SECONDS, 5)
        for request in [7, 9]:
            daemon = proof.SyntheticDaemon(self.expected)
            def delay(method, route):
                if len(daemon.events) == request:
                    daemon.stop.wait(1.2)
            daemon.hook = delay
            with daemon.serve() as endpoint, patch.object(daemon_images, 'SECONDS', 1):
                with self.assertRaises(dev.Refusal) as caught:
                    self.acquire(endpoint)
            self.assertEqual(caught.exception.code, 'docker_timeout')
            self.assertEqual(daemon.events, self.expected_events()[:request])

    def test_deadline_includes_final_evidence_check(self):
        daemon = proof.SyntheticDaemon(self.expected)
        offset = 0
        snapshot = daemon_images.file_snapshot
        def delayed_snapshot(paths):
            nonlocal offset
            result = snapshot(paths)
            if len(daemon.events) == 9:
                offset = 6
            return result
        clock = SimpleNamespace(monotonic=lambda: time.monotonic() + offset)
        with daemon.serve() as endpoint, patch.object(daemon_images, 'time', clock), \
                patch.object(daemon_images, 'file_snapshot', side_effect=delayed_snapshot):
            with self.assertRaises(dev.Refusal) as caught:
                self.acquire(endpoint)
        self.assertEqual(caught.exception.code, 'image_deadline')
        self.assertEqual(daemon.events, self.expected_events())

    def test_exact_fresh_observations_ignore_tags_and_discard_sensitive_metadata(self):
        for control in ['positive', 'index-only']:
            daemon = proof.SyntheticDaemon(self.expected, control)
            with daemon.serve() as endpoint:
                self.assertEqual(self.acquire(endpoint), self.expected)
                daemon.validate_events()
                daemon.events.clear()
                self.assertEqual(self.acquire(endpoint), self.expected)
            daemon.validate_events()
            self.assertNotIn('sensitive-marker', json.dumps(self.expected))

    def test_complete_negative_matrix(self):
        for control, code in proof.EXPECTED.items():
            with self.subTest(control=control):
                daemon = proof.SyntheticDaemon(self.expected, control)
                with daemon.serve() as endpoint, patch.object(daemon_images, 'SECONDS', .2):
                    with self.assertRaises(dev.Refusal) as caught:
                        self.acquire(endpoint)
                self.assertEqual(caught.exception.code, code)
                daemon.validate_events()

    def test_missing_and_stale_evidence_refuse_before_daemon(self):
        for path in [self.owner.run / 'receipt.json', self.owner.tool_receipt,
                     self.owner.root / 'platform/deployment/daemon_images.py']:
            original = path.read_bytes()
            try:
                path.write_bytes(b'{}')
                with patch.object(dev, 'docker_exchange') as exchange:
                    with self.assertRaises((dev.Refusal, KeyError, OSError)):
                        self.acquire('/not-used')
                exchange.assert_not_called()
            finally:
                path.write_bytes(original)

    def test_changed_evidence_and_lock_during_observation_refuse(self):
        for kind in ['source', 'manifest', 'receipt', 'tool', 'preparation', 'lock']:
            with self.subTest(kind=kind):
                paths = {'source': self.owner.root / 'platform/deployment/daemon_images.py',
                         'manifest': self.owner.run / 'postgres-linux-amd64.json',
                         'receipt': self.owner.run / 'receipt.json', 'tool': self.owner.tool_receipt,
                         'preparation': self.owner.root / 'platform/deployment/.local/kdg' / self.owner.args.run_id / 'supabase/config.toml',
                         'lock': self.owner.root / 'platform/deployment/.local/kdg' / ('.network-' + self.owner.args.run_id + '.lock')}
                path = paths[kind]
                raw = path.read_bytes() if path.exists() else b''
                daemon = proof.SyntheticDaemon(self.expected)
                def mutate(method, route):
                    if len(daemon.events) == 2:
                        path.write_bytes(b'changed')
                daemon.hook = mutate
                try:
                    with daemon.serve() as endpoint, self.assertRaises((dev.Refusal, OSError)):
                        self.acquire(endpoint)
                finally:
                    path.write_bytes(raw)

    def test_same_run_lock_bounds_concurrent_checks(self):
        entered, release = threading.Event(), threading.Event()
        daemon = proof.SyntheticDaemon(self.expected)
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
                self.assertEqual(len(daemon.events), 1)
            finally:
                release.set()
            self.assertEqual(first.result(), self.expected)

    def test_distinct_run_has_independent_lock_and_observations(self):
        run_id = str(uuid.uuid4())
        args = SimpleNamespace(target=self.owner.args.target, run_id=run_id)
        with patch.object(dev, 'free_ports', return_value=nullcontext()):
            dev.prepare(self.owner.target, self.owner.raw, run_id, self.owner.target_path, dev.source_evidence())
        tools = self.owner.tools.parent / run_id
        shutil.copytree(self.owner.tools, tools)
        with patch.object(startup.images, 'existing_tools', return_value=(tools / 'payload',
                          dev.digest((tools / 'receipt.json').read_bytes()))):
            startup.images.qualify(args)
            daemon = proof.SyntheticDaemon(proof.expected_images(run_id))
            first_run = self.owner.root / 'platform/deployment/.local/kdg' / self.owner.args.run_id
            with daemon_images.networks.run_lock(first_run, time.monotonic() + 5), daemon.serve() as endpoint:
                observed = daemon_images.acquire(args.target, run_id, _socket_path=endpoint)
            self.assertEqual(observed, self.expected)
            daemon.validate_events()

    def test_one_total_deadline_includes_version_and_all_inspections(self):
        daemon = proof.SyntheticDaemon(self.expected)
        daemon.hook = lambda *args: time.sleep(.06)
        with daemon.serve() as endpoint, patch.object(daemon_images, 'SECONDS', .15):
            with self.assertRaises(dev.Refusal) as caught:
                self.acquire(endpoint)
        self.assertEqual(caught.exception.code, 'docker_timeout')
        self.assertLess(len(daemon.events), 9)

    def test_foreign_and_mutating_routes_refuse_before_connect(self):
        base = '/v1.48/images/'
        for path in ['public.ecr.aws/supabase/postgres:latest/json',
                     'public.ecr.aws/foreign/postgres@sha256:' + 'a' * 64 + '/json',
                     'sha256:' + 'a' * 64 + '/json?platform=linux', '../json', 'json', 'create']:
            with patch.object(dev.socket, 'socket') as connect, self.assertRaises(dev.Refusal):
                dev.docker_exchange('GET', base + path)
            connect.assert_not_called()
        with patch.object(dev.socket, 'socket') as connect, self.assertRaises(dev.Refusal):
            dev.docker_exchange('POST', base + 'create', {})
        connect.assert_not_called()

    def test_omitted_and_foreign_startup_descriptors_refuse_before_events(self):
        from test_startup_adapter import BoundaryControls
        plan = startup.existing_images(self.owner.args)[1]
        for observations in [None, {}, {'foreign': next(iter(self.expected.values()))},
                             dict(self.expected, **{'foreign': {}})]:
            with self.assertRaises(dev.Refusal):
                startup.validate_image_observations(observations, plan)
            fixture = BoundaryControls(methodName='runTest')
            fixture.setUp()
            fixture.fixture['image_observations'] = observations
            for command in [fixture.args, ['image', 'inspect', fixture.fixture['postgres_image']]]:
                events = []
                with self.assertRaises(dev.Refusal):
                    startup.fixture_command('docker', command, fixture.fixture, events)
                self.assertEqual(events, [])

    def test_event_oracle_rejects_missing_reordered_or_duplicate_requests(self):
        daemon = proof.SyntheticDaemon(self.expected)
        with daemon.serve() as endpoint:
            self.acquire(endpoint)
        events = daemon.events.copy()
        for changed in [events[:-1], events + events[-1:], [events[1], events[0], *events[2:]]]:
            daemon.events = changed
            with self.assertRaises(dev.Refusal):
                daemon.validate_events()
