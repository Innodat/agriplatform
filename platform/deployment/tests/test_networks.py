"""Run-network acceptance against actual private Unix sockets; no Docker writes."""
from contextlib import redirect_stdout
import copy
import fcntl
import io
import json
import os
from pathlib import Path
import socket
import sys
import threading
import time
import unittest
import uuid
from unittest.mock import Mock, patch

import test_dev
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dev
import networks
import startup
import qualify_networks as proof


class NetworkAcceptance(unittest.TestCase):
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
        for control, count in [('positive', 7), ('existing', 5), ('conflict', 7)]:
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
        self.patch_root = patch.object(dev, 'ROOT', self.root)
        self.patch_root.start()
        self.addCleanup(self.patch_root.stop)

    def acquire(self, endpoint):
        return networks.acquire(self.input, self.run_id, _socket_path=endpoint)

    def refused(self, endpoint, code):
        with self.assertRaises(dev.Refusal) as result:
            self.acquire(endpoint)
        self.assertEqual(result.exception.code, code)

    def test_prepared_absent_creates_exact_bridge_and_hands_id_to_startup(self):
        self.prepare()
        before = (self.run / 'inventory.json').read_bytes()
        daemon = proof.SyntheticDaemon(self.target, self.run_id)
        work = self.root / 'work'
        work.mkdir(mode=0o700)
        startup.initialize_workdir(work, self.target, self.run_id)
        with daemon.serve() as endpoint:
            argv, env = networks.invocation(self.input, self.run_id, '/synthetic/supabase', work,
                                            _socket_path=endpoint)
        self.assertEqual(argv[-2:], ['--network-id', daemon.network_id])
        self.assertEqual(env['DOCKER_HOST'], 'unix:///var/run/docker.sock')
        daemon.validate_events()
        self.assertNotIn('ConfigFrom', daemon.events[2][2])
        self.assertEqual(daemon.events[2], ('POST', networks.PREFIX + 'create', proof.expected_request(self.target, self.run_id)))
        self.assertEqual(daemon.events[-1][:2], ('GET', networks.PREFIX + daemon.network_id))
        self.assertEqual((self.run / 'inventory.json').read_bytes(), before)
        self.assertEqual(set(os.listdir(self.run)), {'inventory.json', 'supabase'})

    def test_existing_reuses_without_post_and_descriptor_is_closed(self):
        self.prepare()
        daemon = proof.SyntheticDaemon(self.target, self.run_id, 'existing')
        with daemon.serve() as endpoint:
            result = self.acquire(endpoint)
        self.assertEqual(result['Id'], daemon.network_id)
        self.assertEqual(set(result), set(startup.fixture_network(self.target, self.run_id)))
        daemon.validate_events()

    def test_conflict_verifies_winning_network(self):
        self.prepare()
        daemon = proof.SyntheticDaemon(self.target, self.run_id, 'conflict')
        with daemon.serve() as endpoint:
            self.assertEqual(self.acquire(endpoint)['Id'], daemon.network_id)
        daemon.validate_events()

    def test_foreign_unsafe_and_attached_networks_refuse_without_post(self):
        self.prepare()
        for control in ['foreign', 'unsafe-options', 'ipv6', 'attached']:
            with self.subTest(control=control):
                daemon = proof.SyntheticDaemon(self.target, self.run_id, control)
                with daemon.serve() as endpoint:
                    self.refused(endpoint, 'network_not_run_owned')
                daemon.validate_events()

    def test_lost_create_response_never_retries_and_next_invocation_inspects_first(self):
        self.prepare()
        daemon = proof.SyntheticDaemon(self.target, self.run_id, 'lost-response')
        with daemon.serve() as endpoint:
            self.refused(endpoint, 'docker_response_invalid')
            self.assertEqual(len(daemon.events), 3)
            daemon.control = 'existing'
            self.assertEqual(self.acquire(endpoint)['Id'], daemon.network_id)
        self.assertEqual(sum(method == 'POST' for method, _, _ in daemon.events), 1)
        self.assertEqual(daemon.events[4][:2], ('GET', networks.PREFIX + daemon.name))

    def test_replacement_is_rejected(self):
        self.prepare()
        daemon = proof.SyntheticDaemon(self.target, self.run_id, 'replacement')
        with daemon.serve() as endpoint:
            self.refused(endpoint, 'network_replaced')
        daemon.validate_events()

    def test_old_docker_contacts_only_version(self):
        self.prepare()
        daemon = proof.SyntheticDaemon(self.target, self.run_id, 'old-daemon')
        with daemon.serve() as endpoint:
            self.refused(endpoint, 'docker_28_required')
        daemon.validate_events()

    def test_missing_preparation_and_changed_sources_never_contact_daemon(self):
        self.input.write_text(json.dumps(self.target))
        with patch.object(dev, 'ROOT', self.root), patch.object(dev.socket, 'socket') as connect:
            self.refused('/nonexistent/private.sock', 'prepared_run_required')
        connect.assert_not_called()
        self.prepare()
        source = self.root / 'platform/deployment/networks.py'
        source.write_bytes(source.read_bytes() + b'\n')
        with patch.object(dev.socket, 'socket') as connect:
            self.refused('/nonexistent/private.sock', 'prepared_input_changed')
        connect.assert_not_called()

    def test_malformed_oversized_slow_and_error_responses_refuse_safely(self):
        self.prepare()
        for control in ['malformed', 'oversized', 'slow', 'daemon-error']:
            with self.subTest(control=control):
                daemon = proof.SyntheticDaemon(self.target, self.run_id, control)
                with daemon.serve() as endpoint:
                    self.refused(endpoint, proof.EXPECTED[control])
                daemon.validate_events()

    def test_all_actual_safety_fields_are_required_with_exact_types(self):
        self.prepare()
        expected = proof.SyntheticDaemon(self.target, self.run_id, 'existing').network
        mutations = [('Driver', 'overlay'), ('Scope', 'swarm'), ('Internal', True),
                     ('Attachable', True), ('Ingress', True), ('ConfigOnly', True),
                     ('EnableIPv4', False), ('EnableIPv6', 0), ('ConfigFrom', {'Network': 'foreign'}),
                     ('Containers', []), ('Labels', {}), ('Options', {startup.BINDING: '127.0.0.1', 'extra': 'value'}),
                     ('Id', 'a' * 12), ('Id', 'A' * 64), ('Id', 'sha256:' + 'a' * 64), ('Id', True)]
        for key in dict(proof.expected_request(self.target, self.run_id), ConfigFrom={'Network': ''}):
            candidate = copy.deepcopy(expected)
            del candidate[key]
            with self.subTest(missing=key), self.assertRaises(dev.Refusal):
                networks.descriptor(candidate, self.target, self.run_id)
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                daemon = proof.SyntheticDaemon(self.target, self.run_id, 'existing')
                daemon.network[key] = value
                with daemon.serve() as endpoint, self.assertRaises(dev.Refusal):
                    self.acquire(endpoint)
                self.assertFalse(any(event[0] == 'POST' for event in daemon.events))

    def test_preparation_and_source_changes_during_daemon_exchange_refuse(self):
        self.prepare()
        for kind in ['source', 'target', 'inventory', 'run_replacement']:
            with self.subTest(kind=kind):
                source = self.root / 'platform/deployment/networks.py'
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

    def test_public_qualifier_success_and_negative_safe_codes(self):
        self.prepare()
        for control in ['positive', 'existing', 'conflict', *proof.EXPECTED]:
            with self.subTest(control=control):
                output = io.StringIO()
                run_id = str(uuid.uuid4()) if control == 'missing-preparation' else self.run_id
                with redirect_stdout(output):
                    result = proof.main(['--target', str(self.input), '--run-id', run_id, '--control', control])
                record = json.loads(output.getvalue())
                self.assertFalse(record['runtime_ready'])
                self.assertNotIn('sensitive-marker', output.getvalue())
                self.assertEqual(result, 2 if control in proof.EXPECTED else 0, record)
                self.assertEqual(record['code'], proof.EXPECTED.get(control, 'network_synthetic_qualified'))
                if control not in proof.EXPECTED:
                    self.assertEqual(record['created'], control == 'positive')

    def test_one_operation_deadline_spans_version_and_network_requests(self):
        self.prepare()
        daemon = proof.SyntheticDaemon(self.target, self.run_id, 'existing')
        daemon.hook = lambda method, path: time.sleep(.09)
        with daemon.serve() as endpoint, patch.object(networks, 'SECONDS', .15):
            self.refused(endpoint, 'docker_timeout')
        self.assertEqual(len(daemon.events), 2)
        self.assertFalse(any(method == 'POST' for method, _, _ in daemon.events))

    def test_create_response_and_conflict_winner_are_verified_without_retry(self):
        self.prepare()
        for scenario, code in [('short-id', 'network_id_invalid'), ('warning', 'network_create_uncertain'),
                               ('created-id-mismatch', 'network_replaced'), ('foreign-winner', 'network_not_run_owned'),
                               ('missing-winner', 'network_create_conflict')]:
            with self.subTest(scenario=scenario):
                daemon = proof.SyntheticDaemon(self.target, self.run_id)
                original = daemon.dispatch
                def altered(method, path, body):
                    status, response = original(method, path, body)
                    if method == 'POST':
                        if scenario == 'short-id':
                            response['Id'] = 'a' * 12
                        elif scenario == 'warning':
                            response['Warning'] = 'sensitive-marker'
                        elif scenario == 'created-id-mismatch':
                            daemon.network['Id'] = 'b' * 64
                        elif scenario == 'foreign-winner':
                            daemon.network['Labels'] = {}
                            status = 409
                        elif scenario == 'missing-winner':
                            daemon.present = False
                            status = 409
                    return status, response
                daemon.dispatch = altered
                with daemon.serve() as endpoint:
                    self.refused(endpoint, code)
                self.assertEqual(sum(method == 'POST' for method, _, _ in daemon.events), 1)

    def test_public_subprocess_accepts_repo_relative_target_and_ignores_ambient_daemon(self):
        self.prepare()
        import shutil
        import subprocess
        for module in ['images.py', 'toolchain.py']:
            shutil.copyfile(test_dev.ROOT / 'platform/deployment' / module,
                            self.root / 'platform/deployment' / module)
        result = subprocess.run([sys.executable, 'platform/deployment/tests/qualify_networks.py',
                                 '--target', 'target.json', '--run-id', self.run_id],
                                cwd=self.root, capture_output=True, text=True, timeout=10,
                                env={**os.environ, 'DOCKER_HOST': 'tcp://sensitive-marker:2375',
                                     'DOCKER_CONTEXT': 'production'})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        record = json.loads(result.stdout)
        self.assertEqual(record['code'], 'network_synthetic_qualified')
        self.assertFalse(record['runtime_ready'])
        self.assertEqual(result.stderr, '')
        self.assertNotIn('sensitive-marker', result.stdout)

    def test_wrong_production_flag_is_caught_by_independent_daemon_expectation(self):
        self.prepare()
        daemon = proof.SyntheticDaemon(self.target, self.run_id)
        original = networks.create_input
        def wrong_flag(target, run_id):
            return dict(original(target, run_id), EnableIPv4=False)
        with daemon.serve() as endpoint, patch.object(networks, 'create_input', side_effect=wrong_flag):
            self.refused(endpoint, 'network_create_failed')
        self.assertEqual(daemon.errors, ['create_input_mismatch'])
        self.assertFalse(daemon.present)

    def test_event_validation_rejects_missing_duplicate_and_reordered_success_observations(self):
        self.prepare()
        for control in ['positive', 'existing', 'conflict']:
            daemon = proof.SyntheticDaemon(self.target, self.run_id, control)
            with daemon.serve() as endpoint:
                self.acquire(endpoint)
            daemon.validate_events()
            original = list(daemon.events)
            mutations = []
            for index in range(len(original)):
                mutations.append(original[:index] + original[index + 1:])
                mutations.append(original[:index] + [original[index]] + original[index:])
            for index in range(len(original) - 1):
                if original[index] != original[index + 1]:
                    reordered = list(original)
                    reordered[index], reordered[index + 1] = reordered[index + 1], reordered[index]
                    mutations.append(reordered)
            for index, events in enumerate(mutations):
                with self.subTest(control=control, mutation=index):
                    daemon.events = events
                    with self.assertRaises(dev.Refusal) as result:
                        daemon.validate_events()
                    self.assertEqual(result.exception.code, 'synthetic_event_mismatch')

    def test_name_replacement_is_rejected_while_original_id_still_resolves(self):
        self.prepare()
        daemon = proof.SyntheticDaemon(self.target, self.run_id, 'existing')
        original = daemon.dispatch
        name_reads = []
        id_reads = []
        def replace_name(method, path, body):
            status, response = original(method, path, body)
            if path == networks.PREFIX + daemon.name:
                name_reads.append(path)
                if len(name_reads) > 1:
                    response['Id'] = 'b' * 64
            elif path == networks.PREFIX + daemon.network_id:
                id_reads.append(response['Id'])
            return status, response
        daemon.dispatch = replace_name
        handoff = Mock()
        with daemon.serve() as endpoint, self.assertRaises(dev.Refusal) as result:
            networks.acquire(self.input, self.run_id, _socket_path=endpoint, _handoff=handoff)
        self.assertEqual(result.exception.code, 'network_replaced')
        self.assertEqual(id_reads, [daemon.network_id])
        self.assertEqual(len(name_reads), 2)
        handoff.assert_not_called()

    def test_mid_operation_lock_state_changes_refuse_before_create_or_handoff(self):
        self.prepare()
        lock = self.run.parent / ('.network-' + self.run_id + '.lock')
        for kind in ['nonempty', 'mode', 'hardlink']:
            for when in ['before-create', 'before-handoff']:
                with self.subTest(kind=kind, when=when):
                    daemon = proof.SyntheticDaemon(self.target, self.run_id,
                                                  'positive' if when == 'before-create' else 'existing')
                    def mutate(method, path):
                        final_id = path == networks.PREFIX + daemon.network_id and daemon.inspect_count == 3
                        if ((when == 'before-create' and path == networks.PREFIX + daemon.name)
                                or (when == 'before-handoff' and final_id)):
                            if kind == 'nonempty':
                                lock.write_text('sensitive-marker')
                            elif kind == 'mode':
                                lock.chmod(0o644)
                            else:
                                os.link(lock, self.root / 'lock-alias')
                    daemon.hook = mutate
                    handoff = Mock()
                    with daemon.serve() as endpoint, self.assertRaises(dev.Refusal) as result:
                        networks.acquire(self.input, self.run_id, _socket_path=endpoint, _handoff=handoff)
                    self.assertEqual(result.exception.code, 'network_lock_changed')
                    self.assertFalse(any(method == 'POST' for method, _, _ in daemon.events))
                    handoff.assert_not_called()
                    (self.root / 'lock-alias').unlink(missing_ok=True)
                    lock.write_text('')
                    lock.chmod(0o600)

    def test_wrong_negative_code_reports_qualification_mismatch(self):
        self.prepare()
        for control in ['foreign', 'missing-preparation']:
            output = io.StringIO()
            with patch.object(networks, 'invocation', side_effect=dev.Refusal('network', 'wrong_code')):
                with redirect_stdout(output):
                    result = proof.main(['--target', str(self.input), '--run-id', self.run_id, '--control', control])
            self.assertEqual(result, 2)
            self.assertEqual(json.loads(output.getvalue())['code'], 'synthetic_outcome_mismatch')

    def test_malformed_and_noncanonical_run_ids_refuse_before_input_or_daemon_access(self):
        for run_id in ['not-a-uuid', '', self.run_id.upper(), self.run_id.replace('-', '')]:
            with self.subTest(run_id=run_id), patch.object(dev, 'read') as read, patch.object(dev.socket, 'socket') as connect:
                with self.assertRaises(dev.Refusal) as result:
                    networks.acquire('/nonexistent/target.json', run_id)
                self.assertEqual(result.exception.code, 'invalid_run_id')
                output = io.StringIO()
                with redirect_stdout(output):
                    status = proof.main(['--target', '/nonexistent/target.json', '--run-id', run_id])
                self.assertEqual(status, 2)
                self.assertEqual(json.loads(output.getvalue())['code'], 'invalid_run_id')
                read.assert_not_called()
                connect.assert_not_called()

    def test_no_public_endpoint_override(self):
        output = io.StringIO()
        with redirect_stdout(output):
            result = proof.main(['--target', str(self.input), '--run-id', self.run_id, '--socket', '/private.sock'])
        self.assertEqual(result, 2)
        self.assertEqual(json.loads(output.getvalue())['code'], 'invalid_arguments')


class BoundedTransport(unittest.TestCase):
    def test_arbitrary_routes_methods_and_requests_are_rejected_before_connect(self):
        for method, path, body in [('DELETE', networks.PREFIX + 'a' * 64, None),
                                   ('GET', '/containers/json', None), ('GET', '/networks/x', None),
                                   ('GET', '/version', {}), ('GET', networks.PREFIX + 'a' * 64, {}),
                                   ('POST', networks.PREFIX + 'create', {'x': 'x' * 20000})]:
            with self.subTest(path=path), patch.object(dev.socket, 'socket', side_effect=OSError) as connect, self.assertRaises(dev.Refusal):
                dev.docker_exchange(method, path, body)
            connect.assert_not_called()

    def test_post_timeout_does_not_retry(self):
        import test_docker_gate
        transport = test_docker_gate.ScriptedSocket(b'')
        with patch.object(transport, 'sendall', side_effect=TimeoutError('sensitive-marker')), patch.object(dev.socket, 'socket', return_value=transport) as connect:
            with self.assertRaises(dev.Refusal) as result:
                dev.docker_exchange('POST', networks.PREFIX + 'create', {})
            self.assertEqual(result.exception.code, 'docker_timeout')
            connect.assert_called_once()


if __name__ == '__main__':
    unittest.main()
