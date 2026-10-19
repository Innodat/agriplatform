"""Joint acquisition contracts against independent private Unix fixture oracles."""
import unittest

import test_daemon_images
import qualify_resources as proof
import resources


class Resources(unittest.TestCase):
    def test_acquisition_already_expired_keeps_evidence_before_timeout_and_closes(self):
        from contextlib import contextmanager
        import daemon_images
        import dev
        from unittest.mock import patch
        now, events, sessions, handoffs, closes = [1], [], [], [], []
        qualified, real_session = daemon_images.qualified_evidence, dev.DockerSession
        @contextmanager
        def owner(*args):
            with qualified(*args) as (target, plan, evidence):
                def current():
                    events.append('evidence')
                    evidence()
                    events.append('evidence_checked')
                yield target, plan, current
        def session_factory(**kwargs):
            session = real_session(**kwargs)
            sessions.append(session)
            self.assertEqual(session.deadline, 6)
            now[0] = 7
            close = session.close
            def close_once():
                closes.append(True)
                close()
            session.close = close_once
            return session
        with patch.object(daemon_images, 'qualified_evidence', side_effect=owner), \
                patch.object(dev, 'DockerSession', side_effect=session_factory), \
                patch.object(real_session, 'exchange') as exchange, \
                patch.object(dev.time, 'monotonic', side_effect=lambda: now[0]):
            with self.assertRaises(dev.Refusal) as caught:
                self.acquire('/synthetic/not-connected', _handoff=lambda *args: handoffs.append(True))
        self.assertEqual(events, ['evidence', 'evidence_checked'])
        self.assertEqual(dev.refusal_result(caught.exception), {
            'ok': False, 'stage': 'docker', 'code': 'docker_timeout', 'runtime_ready': False,
            'owner_failure': {'schema_version': 1, 'scope': 'acquisition',
                              'check': 'already_expired', 'elapsed_ms': 0}})
        exchange.assert_not_called()
        self.assertEqual(handoffs, [])
        self.assertEqual(closes, [True])
        self.assertTrue(sessions[0].closed)
        self.assertIsNone(sessions[0].stream)

    def test_owner_context_cleanup_refusal_retains_observed_timeout_and_closes_once(self):
        from contextlib import contextmanager
        import time
        import daemon_images
        import dev
        from unittest.mock import patch
        daemon = self.daemon()
        now, events, sessions, originals, handoffs = [time.monotonic()], [], [], [], []
        qualified, real_session = daemon_images.qualified_evidence, dev.DockerSession
        wrapper = dev.Refusal('owner', 'owner_cleanup_changed')
        @contextmanager
        def owner(*args):
            with qualified(*args) as (target, plan, evidence):
                def current():
                    evidence()
                    events.append('evidence')
                    if daemon.events:
                        now[0] += 6
                try:
                    yield target, plan, current
                except dev.Refusal as original:
                    originals.append(original)
                    events.append('owner_exit')
                    raise wrapper
        def session_factory(**kwargs):
            session = real_session(**kwargs)
            sessions.append(session)
            close = session.close
            def close_once():
                events.append('connection_close')
                close()
            session.close = close_once
            return session
        with daemon.serve() as endpoint, \
                patch.object(daemon_images, 'qualified_evidence', side_effect=owner), \
                patch.object(dev, 'DockerSession', side_effect=session_factory), \
                patch.object(dev.time, 'monotonic', side_effect=lambda: now[0]):
            with self.assertRaises(dev.Refusal) as caught:
                self.acquire(endpoint, _handoff=lambda *args: handoffs.append(True))
        self.assertIs(caught.exception, wrapper)
        self.assertEqual(len(originals), 1)
        self.assertIs(wrapper.__context__, originals[0])
        self.assertEqual((originals[0].stage, originals[0].code), ('docker', 'docker_timeout'))
        self.assertEqual(dev.refusal_result(wrapper), {'ok': False, 'runtime_ready': False,
            'stage': 'owner', 'code': 'owner_cleanup_changed', 'owner_failure': {
                'schema_version': 1, 'scope': 'acquisition', 'check': 'custody', 'elapsed_ms': 6000}})
        self.assertEqual(events, ['evidence', 'evidence', 'connection_close', 'owner_exit'])
        self.assertEqual(handoffs, [])
        self.assertTrue(sessions[0].closed)
        self.assertIsNone(sessions[0].stream)
        self.assertEqual(daemon.connections, 1)
        self.assertEqual(daemon.events, daemon.expected[:1])
        self.assertFalse(daemon.errors or daemon.network.errors or daemon.volume.errors)

    def test_guard_outer_boundary_preserves_order_and_nested_observation(self):
        import dev
        from types import SimpleNamespace
        from unittest.mock import patch
        for scenario in ['expiry', 'already-expired', 'nested', 'custody', 'idle', 'cancel', 'success']:
            events, now = [], [6 if scenario == 'already-expired' else 1]
            original = dev.Refusal('docker', 'docker_timeout')
            def current():
                events.append('current')
                if scenario == 'nested':
                    original.owner_failure = {'schema_version': 1, 'scope': 'fresh',
                                              'check': 'custody', 'elapsed_ms': 7}
                    raise original
                if scenario == 'custody':
                    raise dev.Refusal('custody', 'changed')
                if scenario == 'cancel':
                    raise KeyboardInterrupt()
                if scenario == 'expiry':
                    now[0] = 6
            def idle():
                events.append('idle')
                if scenario == 'idle':
                    raise dev.Refusal('docker', 'docker_response_invalid')
            def budget():
                events.append('budget')
                if now[0] >= 5:
                    raise original
            session = SimpleNamespace(deadline=5, idle=idle, budget=budget)
            guard = resources.FreshGuard(None, None, session, current, 5, None, None, None, None)
            with self.subTest(scenario=scenario), patch.object(dev.time, 'monotonic', side_effect=lambda: now[0]):
                if scenario == 'success':
                    guard.check()
                else:
                    with self.assertRaises(KeyboardInterrupt if scenario == 'cancel' else dev.Refusal) as caught:
                        guard.check()
            expected = ['current'] if scenario in ['nested', 'custody', 'cancel'] else (
                ['current', 'idle'] if scenario == 'idle' else ['current', 'idle', 'budget'])
            self.assertEqual(events, expected)
            self.assertEqual(guard.ownership_lost, scenario == 'custody')
            if scenario in ['expiry', 'already-expired', 'nested']:
                self.assertIs(caught.exception, original)
                self.assertEqual(dev.refusal_result(original)['owner_failure'],
                    {'schema_version': 1, 'scope': 'fresh' if scenario == 'nested' else 'guard',
                     'check': {'expiry': 'budget', 'already-expired': 'already_expired',
                               'nested': 'custody'}[scenario],
                     'elapsed_ms': {'expiry': 5000, 'already-expired': 0, 'nested': 7}[scenario]})
            elif scenario != 'success':
                self.assertNotIn('owner_failure', vars(caught.exception))

    def test_fresh_custody_timeout_and_already_expired_keep_executable_order(self):
        from contextlib import contextmanager
        from pathlib import Path
        from types import SimpleNamespace
        import tempfile
        import startup
        import daemon_images
        import dev
        from unittest.mock import patch
        for scenario in ['expiry', 'already-expired', 'custody', 'cancel',
                         'executable-expiry', 'executable-refusal', 'executable-cancel']:
            now, events, sessions = [1], [], []
            executable_error = (KeyboardInterrupt('SECRET') if scenario == 'executable-cancel'
                                else dev.Refusal('custody', 'executable_changed'))
            @contextmanager
            def owner(*args):
                def evidence():
                    events.append('evidence')
                    if scenario == 'expiry':
                        now[0] = 7
                    if scenario == 'custody':
                        raise dev.Refusal('custody', 'changed')
                    if scenario == 'cancel':
                        raise KeyboardInterrupt()
                yield self.owner.owner.target, None, evidence
            def executable():
                events.append('executable')
                if events.count('executable') == 2:
                    if scenario.startswith('executable-'):
                        now[0] = 7
                    if scenario in ['executable-refusal', 'executable-cancel']:
                        raise executable_error
            real_session = dev.DockerSession
            def session_factory(**kwargs):
                session = real_session(**kwargs)
                sessions.append(session)
                if scenario == 'already-expired':
                    now[0] = 7
                return session
            with tempfile.TemporaryDirectory() as temporary:
                work = Path(temporary)
                startup.initialize_workdir(work, self.owner.owner.target, self.owner.owner.args.run_id)
                with self.subTest(scenario=scenario), \
                        patch.object(daemon_images, 'qualified_evidence', side_effect=owner), \
                        patch.object(dev, 'DockerSession', side_effect=session_factory), \
                        patch.object(dev.time, 'monotonic', side_effect=lambda: now[0]):
                    with self.assertRaises(KeyboardInterrupt if scenario in ['cancel', 'executable-cancel']
                                           else dev.Refusal) as caught:
                        with resources.fresh_session(self.owner.owner.args.target, self.owner.owner.args.run_id,
                                '/synthetic/not-executed', work,
                                _executable_custody=SimpleNamespace(check=executable)):
                            self.fail('no handoff after failure')
            self.assertEqual(events, ['executable', 'evidence'] + (
                ['executable'] if scenario not in ['custody', 'cancel'] else []))
            self.assertTrue(sessions[0].closed)
            self.assertIsNone(sessions[0].stream)
            record = vars(caught.exception)
            if scenario in ['expiry', 'already-expired', 'executable-expiry']:
                self.assertEqual(dev.refusal_result(caught.exception)['owner_failure'], {
                    'schema_version': 1, 'scope': 'fresh',
                    'check': 'already_expired' if scenario == 'already-expired' else 'custody',
                    'elapsed_ms': 0 if scenario == 'already-expired' else 6000})
            else:
                self.assertNotIn('owner_failure', record)
                if scenario in ['executable-refusal', 'executable-cancel']:
                    self.assertIs(caught.exception, executable_error)

    def test_owner_timeout_public_qualifier_keeps_custody_boundary_without_request_metadata(self):
        from contextlib import contextmanager, redirect_stdout
        import io
        import json
        import time
        from unittest.mock import patch
        import daemon_images
        import dev
        import qualify_startup
        daemon, called, checks = self.daemon(), [], []
        qualified = daemon_images.qualified_evidence
        now = [time.monotonic()]
        @contextmanager
        def evidence_owner(*args):
            with qualified(*args) as (target, plan, evidence):
                def current():
                    evidence()
                    checks.append(True)
                    # The first request completed; custody consumes the budget.
                    if daemon.events:
                        now[0] += 6
                yield target, plan, current
        output = io.StringIO()
        with daemon.serve() as endpoint:
            def qualify(*args):
                return self.acquire(endpoint, _handoff=lambda *args: called.append(True))
            with patch.object(daemon_images, 'qualified_evidence', side_effect=evidence_owner), \
                    patch.object(time, 'monotonic', side_effect=lambda: now[0]), \
                    patch.object(qualify_startup.startup, 'qualify', side_effect=qualify), redirect_stdout(output):
                status = qualify_startup.main(['--target', self.owner.owner.args.target,
                    '--run-id', self.owner.owner.args.run_id, '--control', 'pinned-cli-postgres'])
        self.assertEqual(status, 2)
        self.assertEqual(json.loads(output.getvalue()), {'ok': False, 'runtime_ready': False,
            'stage': 'docker', 'code': 'docker_timeout', 'owner_failure': {
                'schema_version': 1, 'scope': 'acquisition', 'check': 'custody', 'elapsed_ms': 6000}})
        self.assertEqual(checks, [True, True])
        self.assertEqual(called, [])
        self.assertEqual(daemon.connections, 1)
        self.assertEqual(daemon.events, daemon.expected[:1])

    def assert_stopped(self, pids):
        from pathlib import Path
        import time
        self.assertTrue(pids)
        for pid in pids:
            deadline = time.monotonic() + .5
            while True:
                try:
                    text = Path('/proc/' + str(pid) + '/status').read_text()
                except FileNotFoundError:
                    break
                state = next(line.split()[1] for line in text.splitlines() if line.startswith('State:'))
                if state in ['Z', 'X']:
                    break
                self.assertLess(time.monotonic(), deadline, 'spawned process remains running')
                time.sleep(.01)

    def source_with_descendant(self, source, *, exit_parent=False):
        witness = "extra = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
        witness += "(work/'tmp/processes.json').write_text(json.dumps([os.getpid(), extra.pid]))\n"
        if exit_parent:
            witness += 'sys.exit(1)\n'
        return source.replace("f = json.loads((work/'fixture.json').read_text())", witness + "f = json.loads((work/'fixture.json').read_text())")

    def test_integrated_listener_custody_before_post_and_descendant_cleanup(self):
        import dev
        import startup
        import json
        import socket
        from unittest.mock import patch
        from test_startup_lifecycle import Lifecycle
        for defect in ['removed', 'replaced', 'chmod']:
            daemon = proof.GuardedDaemon(self.owner.owner.target, self.owner.owner.args.run_id, self.owner.expected)
            runner, pids, replacements, recorded = startup.guarded_fixture_command, [], [], []
            def observe(*args):
                def mutate(*_):
                    if len(daemon.events) == 41:
                        path = args[1] / 'docker/owner.sock'
                        if defect == 'chmod':
                            path.chmod(0o644)
                        else:
                            path.unlink()
                            if defect == 'replaced':
                                replacement = socket.socket(socket.AF_UNIX)
                                replacement.bind(str(path))
                                path.chmod(0o600)
                                replacements.append(replacement)
                daemon.hook = mutate
                try:
                    return runner(*args)
                finally:
                    pids.extend(json.loads((args[1] / 'tmp/processes.json').read_text()))
                    recorded.extend(startup.decode_fixture(args[1] / 'events.json'))
            try:
                with self.subTest(defect=defect), patch.object(startup, 'guarded_fixture_command', side_effect=observe):
                    with self.assertRaises(dev.Refusal) as caught:
                        self.integrated_probe(daemon, source=self.source_with_descendant(Lifecycle().process_source()))
                self.assertEqual(caught.exception.code, 'invalid_owner_handoff')
                self.assertEqual(daemon.events, daemon.expected[:41])
                self.assertFalse(any(event['kind'] == 'fresh_volume_create_acknowledged' for event in recorded))
                self.assert_stopped(pids)
            finally:
                for replacement in replacements:
                    replacement.close()

    def test_guarded_runner_output_bounds_and_terminal_descendant_cleanup(self):
        import dev
        import startup
        import json
        import os
        import stat
        import time
        from unittest.mock import patch
        from test_startup_lifecycle import Lifecycle
        for scenario in ['stdout', 'stderr', 'combined', 'malformed', 'inherited-pipe']:
            daemon = proof.GuardedDaemon(self.owner.owner.target, self.owner.owner.args.run_id, self.owner.expected)
            source = self.source_with_descendant(Lifecycle().process_source(), exit_parent=scenario == 'inherited-pipe')
            if scenario in ['stdout', 'stderr', 'combined']:
                writes = ([(1, 600000), (2, 600000)] if scenario == 'combined' else
                          [(1 if scenario == 'stdout' else 2, 2 * 1024 * 1024)])
                output = 'for fd, remaining in ' + repr(writes) + ':\n'
                output += "    while remaining:\n        remaining -= os.write(fd, b'x' * min(65536, remaining))\n"
                source = source.replace("f = json.loads((work/'fixture.json').read_text())", output + "f = json.loads((work/'fixture.json').read_text())")
            runner, consumed, pids = startup.guarded_fixture_command, [], []
            read = os.read
            def bounded_read(fd, size):
                raw = read(fd, size)
                if stat.S_ISFIFO(os.fstat(fd).st_mode):
                    consumed.append(len(raw))
                return raw
            def observe(*args):
                try:
                    with patch.object(startup.os, 'read', side_effect=bounded_read):
                        return runner(*args)
                finally:
                    pids.extend(json.loads((args[1] / 'tmp/processes.json').read_text()))
            install = startup.install_fixture
            def inject(work, *args, **kwargs):
                install(work, *args, **kwargs)
                if scenario != 'malformed':
                    return
                path = work / 'bin/docker'
                code = '''original_handoff = startup.owner_handoff
def handoff(fixture, phase, args, environment):
    if phase == 'probe': return original_handoff(fixture, phase, args, environment)
    import socket
    with socket.socket(socket.AF_UNIX) as peer:
        peer.connect(str(Path(fixture['workdir']) / 'docker/owner.sock'))
        peer.sendall(b'{')
        peer.shutdown(socket.SHUT_WR)
        peer.recv(8)
    startup.fail('invalid_owner_handoff')
startup.owner_handoff = handoff
'''
                path.write_text(path.read_text().replace('args, env = sys.argv[1:], dict(os.environ)', code + 'args, env = sys.argv[1:], dict(os.environ)'))
            started = time.monotonic()
            with self.subTest(scenario=scenario), patch.object(startup, 'guarded_fixture_command', side_effect=observe), \
                    patch.object(startup, 'install_fixture', side_effect=inject), \
                    patch.object(resources, 'SECONDS', 2 if scenario == 'inherited-pipe' else 5):
                with self.assertRaises(dev.Refusal) as caught:
                    self.integrated_probe(daemon, source=source)
            self.assertEqual(caught.exception.code, 'invalid_owner_handoff' if scenario == 'malformed' else
                             'docker_timeout' if scenario == 'inherited-pipe' else 'command_output_too_large')
            self.assertEqual(daemon.events, daemon.expected[:29 if scenario == 'malformed' else 28])
            self.assertEqual(len(pids), 2)
            self.assert_stopped(pids)
            if scenario in ['stdout', 'stderr', 'combined']:
                self.assertEqual(sum(consumed), 1024 * 1024 + 1)
            self.assertLess(time.monotonic() - started, 4 if scenario == 'inherited-pipe' else 5)

    def test_integrated_handoff_rejects_real_grandchild_and_wrong_parsed_uid(self):
        import dev
        import startup
        import struct
        from unittest.mock import patch
        install, unpack = startup.install_fixture, struct.unpack
        for defect in ['grandchild', 'uid']:
            daemon = proof.GuardedDaemon(self.owner.owner.target, self.owner.owner.args.run_id, self.owner.expected)
            pids = []
            def inject(work, *args, **kwargs):
                install(work, *args, **kwargs)
                if defect != 'grandchild':
                    return
                path = work / 'bin/docker'
                code = '''original_handoff = startup.owner_handoff
def handoff(fixture, phase, args, environment):
    if phase == 'probe': return original_handoff(fixture, phase, args, environment)
    import socket, json
    ready_read, ready_write = os.pipe()
    child = os.fork()
    if child == 0:
        try:
            os.close(ready_write)
            os.read(ready_read, 1)
            os.close(ready_read)
            with socket.socket(socket.AF_UNIX) as peer:
                peer.connect(str(Path(fixture['workdir']) / 'docker/owner.sock'))
                peer.sendall(json.dumps({'token': environment['ENV_PRIVATE_OWNER_TOKEN'], 'phase': phase, 'args': args}).encode())
                peer.shutdown(socket.SHUT_WR)
                peer.recv(8)
        finally: os._exit(0)
    os.close(ready_read)
    (Path(fixture['workdir']) / 'tmp/grandchild.pid').write_text(str(child))
    os.write(ready_write, b'1')
    os.close(ready_write)
    os.waitpid(child, 0)
    startup.fail('invalid_owner_handoff')
startup.owner_handoff = handoff
'''
                path.write_text(path.read_text().replace('args, env = sys.argv[1:], dict(os.environ)', code + 'args, env = sys.argv[1:], dict(os.environ)'))
            runner, credentials = startup.guarded_fixture_command, []
            def observe(*args):
                try:
                    return runner(*args)
                finally:
                    witness = args[1] / 'tmp/grandchild.pid'
                    if witness.exists():
                        pids.append(int(witness.read_text()))
            def parsed(format, raw):
                result = unpack(format, raw)
                if format == '3i' and len(raw) == 12:
                    credentials.append(result)
                    if defect == 'uid' and len(credentials) == 2:
                        return result[0], result[1] + 1, result[2]
                return result
            with self.subTest(defect=defect), patch.object(startup, 'install_fixture', side_effect=inject), \
                    patch.object(startup, 'guarded_fixture_command', side_effect=observe), patch.object(startup.struct, 'unpack', side_effect=parsed):
                with self.assertRaises(dev.Refusal) as caught:
                    self.integrated_probe(daemon)
            self.assertEqual(caught.exception.code, 'invalid_owner_handoff')
            self.assertEqual(daemon.events, daemon.expected[:29])
            self.assertEqual(len(credentials), 2)
            if defect == 'grandchild':
                self.assert_stopped(pids)

    def test_integrated_pre_ack_joint_and_post_mutation_custody_refuse(self):
        import dev
        import startup
        from unittest.mock import patch
        cases = [('image', 45), ('config-image', 49), ('network', 53), ('volume', 56), ('use', 57)]
        cases += [(field, 42) for field in ['source', 'receipt', 'lock', 'config']]
        for field, at in cases:
            daemon = proof.GuardedDaemon(self.owner.owner.target, self.owner.owner.args.run_id, self.owner.expected)
            paths = {'source': self.owner.owner.root / 'platform/deployment/resources.py',
                     'receipt': self.owner.owner.tool_receipt,
                     'lock': self.owner.owner.root / 'platform/deployment/.local/kdg' /
                             ('.network-' + self.owner.owner.args.run_id + '.lock')}
            path = paths.get(field)
            saved = path.read_bytes() if path is not None and path.exists() else b''
            runner, recorded = startup.guarded_fixture_command, []
            def observe(*args):
                def mutate(*_):
                    if len(daemon.events) != at:
                        return
                    if field in ['image', 'config-image']:
                        daemon.image_control = 'wrong-id'
                    elif field == 'network':
                        daemon.network.network['Id'] = 'f' * 64
                    elif field == 'volume':
                        daemon.volume.volume['CreatedAt'] = 'changed'
                    elif field == 'use':
                        daemon.volume.control = 'use-stopped'
                    else:
                        (args[1] / 'supabase/config.toml' if field == 'config' else path).write_bytes(b'changed')
                daemon.hook = mutate
                try:
                    return runner(*args)
                finally:
                    recorded.extend(startup.decode_fixture(args[1] / 'events.json'))
            try:
                with self.subTest(field=field, request=at), patch.object(startup, 'guarded_fixture_command', side_effect=observe):
                    with self.assertRaises(dev.Refusal):
                        self.integrated_probe(daemon)
                self.assertEqual(daemon.events, daemon.expected[:at])
                self.assertEqual(daemon.connections, 1)
                self.assertEqual(sum(method == 'POST' and '/volumes/' in route for method, route, _ in daemon.events), 1)
                self.assertFalse(any(event['kind'] in ['fresh_volume_create_acknowledged', 'postgres_create',
                    'secret_transfer', 'postgres_start_refused'] for event in recorded))
            finally:
                if path is not None:
                    path.write_bytes(saved)

    def test_integrated_executable_mutation_before_launch_and_post_refuses(self):
        import dev
        import startup
        from pathlib import Path
        from unittest.mock import patch
        install = startup.install_fixture
        for boundary in ['launch', 'post']:
            for mutation in ['replace', 'in-place']:
                daemon = proof.GuardedDaemon(self.owner.owner.target, self.owner.owner.args.run_id, self.owner.expected)
                def bind(work, target, run_id, network, executable, *args, **kwargs):
                    install(work, target, run_id, network, executable, *args, **kwargs)
                    path = Path(executable)
                    raw = path.read_bytes()
                    def change():
                        if mutation == 'replace':
                            replacement = path.with_name('changed-cli')
                            replacement.write_bytes(raw)
                            replacement.chmod(0o700)
                            replacement.replace(path)
                        else:
                            path.write_bytes(raw)
                    if boundary == 'launch':
                        change()
                    else:
                        def hook(*_):
                            if len(daemon.events) == 41:
                                change()
                        daemon.hook = hook
                with self.subTest(boundary=boundary, mutation=mutation), patch.object(startup, 'install_fixture', side_effect=bind):
                    with self.assertRaises(dev.Refusal) as caught:
                        self.integrated_probe(daemon)
                    self.assertEqual(caught.exception.code, 'tool_payload_changed')
                    self.assertEqual(daemon.events, daemon.expected[:28 if boundary == 'launch' else 41])
                    self.assertFalse(any(method == 'POST' and '/volumes/' in path for method, path, _ in daemon.events))

    def integrated_probe(self, daemon, *, source=None):
        from pathlib import Path
        import tempfile
        import sys
        import startup
        from test_startup_lifecycle import Lifecycle
        with tempfile.TemporaryDirectory() as directory, daemon.serve() as endpoint:
            executable = Path(directory) / 'supabase'
            executable.write_text('#!' + sys.executable + '\n' + (source or Lifecycle().process_source()))
            executable.chmod(0o700)
            return startup.synthetic_probe(
                executable, self.owner.owner.target, self.owner.owner.args.run_id,
                control='fresh-lifecycle-positive', selection_plan=startup.existing_images(self.owner.owner.args)[1],
                image_observations=self.owner.expected,
                _guarded_target=(self.owner.owner.args.target, endpoint))

    def test_integrated_owner_negative_matrix_never_replays_or_returns_proof(self):
        import dev
        import startup
        from unittest.mock import patch
        command = startup.guarded_fixture_command
        for scenario, (code, count) in proof.GUARDED_FAILURES.items():
            daemon = proof.GuardedDaemon(self.owner.owner.target, self.owner.owner.args.run_id, self.owner.expected, scenario)
            recorded = []
            def observe(*args):
                try:
                    return command(*args)
                finally:
                    recorded.extend(startup.decode_fixture(args[1] / 'events.json'))
            with self.subTest(scenario=scenario), patch.object(startup, 'guarded_fixture_command', side_effect=observe):
                with self.assertRaises(dev.Refusal) as caught:
                    self.integrated_probe(daemon)
            self.assertEqual(caught.exception.code, code)
            daemon.validate_events(success=False)
            self.assertEqual(len(daemon.events), count)
            self.assertLessEqual(sum(method == 'POST' and '/volumes/' in path for method, path, _ in daemon.events), 1)
            if count <= 44:
                self.assertFalse(any(event['kind'] in ['fresh_volume_create_acknowledged', 'postgres_create',
                                                      'secret_transfer', 'postgres_start_refused'] for event in recorded))
            self.assertNotIn('sensitive', str(caught.exception))

    def test_integrated_handoff_custody_and_total_deadline_refuse_with_cleanup(self):
        import dev
        import startup
        import time
        from unittest.mock import patch
        for defect in ['source', 'receipt', 'lock', 'deadline', 'post-owner']:
            daemon = proof.GuardedDaemon(self.owner.owner.target, self.owner.owner.args.run_id, self.owner.expected)
            path = {'source': self.owner.owner.root / 'platform/deployment/resources.py',
                    'receipt': self.owner.owner.tool_receipt,
                    'lock': self.owner.owner.root / 'platform/deployment/.local/kdg' /
                            ('.network-' + self.owner.owner.args.run_id + '.lock')}.get(defect)
            raw = path.read_bytes() if path is not None and path.exists() else b''
            def mutate(*args):
                # The truthful CLI missing probe passed. Fail during the next
                # joint observation before the owner can send its volume POST.
                if len(daemon.events) == 30:
                    if path is not None:
                        path.write_bytes(b'changed')
                    if defect == 'deadline':
                        time.sleep(.4)
            daemon.hook = mutate
            owner = startup.existing_images
            calls = []
            def owner_check(*args):
                calls.append(True)
                if defect == 'post-owner' and len(calls) == 3:
                    dev.refuse('daemon_images', 'image_evidence_changed')
                return owner(*args)
            try:
                with self.subTest(defect=defect), patch.object(startup, 'existing_images', side_effect=owner_check), \
                        patch.object(resources, 'SECONDS', .8 if defect == 'deadline' else 5):
                    with self.assertRaises(dev.Refusal):
                        self.integrated_probe(daemon)
                self.assertEqual(daemon.connections, 1)
                if defect != 'post-owner':
                    self.assertFalse(any(method == 'POST' and '/volumes/' in route for method, route, _ in daemon.events))
            finally:
                if path is not None:
                    path.write_bytes(raw)

    def test_integrated_private_handoff_adversaries_and_drip_deadline(self):
        import dev
        import startup
        import time
        from pathlib import Path
        from unittest.mock import patch
        install = startup.install_fixture
        for defect in ['forged', 'malformed', 'duplicate', 'repeated', 'wrong-args', 'drip', 'empty', 'oversized', 'no-eof']:
            daemon = proof.GuardedDaemon(self.owner.owner.target, self.owner.owner.args.run_id, self.owner.expected)
            descendant = []
            runner = startup.guarded_fixture_command
            def observe(*args):
                try:
                    return runner(*args)
                finally:
                    witness = args[1] / 'tmp/request.pid'
                    if witness.exists():
                        descendant.append(int(witness.read_text()))
            def inject(work, *args, **kwargs):
                install(work, *args, **kwargs)
                wrapper = work / 'bin/docker'
                injected = '''original_handoff = startup.owner_handoff
def handoff(fixture, phase, args, environment):
    if phase == 'probe': return original_handoff(fixture, phase, args, environment)
    import socket, json, time
    token = environment['ENV_PRIVATE_OWNER_TOKEN']
    message = {'token': token, 'phase': phase, 'args': args}
    defect = __DEFECT__
    if defect == 'forged': message['token'] = '0' * 32
    if defect == 'repeated': message['phase'] = 'probe'
    if defect == 'wrong-args': message['args'] = args + ['extra']
    raw = json.dumps(message).encode()
    if defect == 'malformed': raw = b'{'
    if defect == 'duplicate': raw = raw[:-1] + b',"phase":"create"}'
    if defect == 'empty': raw = b''
    if defect == 'oversized': raw = b'x' * 2049
    with socket.socket(socket.AF_UNIX) as peer:
        peer.connect(str(Path(fixture['workdir']) / 'docker/owner.sock'))
        (Path(fixture['workdir']) / 'tmp/request.pid').write_text(str(os.getpid()))
        if defect == 'drip':
            peer.sendall(raw[:1])
            time.sleep(10)
        peer.sendall(raw)
        if defect == 'no-eof': time.sleep(10)
        peer.shutdown(socket.SHUT_WR)
        peer.recv(8)
    startup.fail('invalid_owner_handoff')
startup.owner_handoff = handoff
'''.replace('__DEFECT__', repr(defect))
                wrapper.write_text(wrapper.read_text().replace('args, env = sys.argv[1:], dict(os.environ)',
                                   injected + 'args, env = sys.argv[1:], dict(os.environ)'))
            started = time.monotonic()
            with self.subTest(defect=defect), patch.object(startup, 'install_fixture', side_effect=inject), \
                    patch.object(startup, 'guarded_fixture_command', side_effect=observe), \
                    patch.object(resources, 'SECONDS', 2 if defect in ['drip', 'no-eof'] else 5):
                with self.assertRaises(dev.Refusal) as caught:
                    self.integrated_probe(daemon)
            self.assertEqual(caught.exception.code, 'docker_timeout' if defect in ['drip', 'no-eof'] else 'invalid_owner_handoff')
            self.assertEqual(daemon.events, daemon.expected[:29])
            self.assertEqual(daemon.connections, 1)
            self.assertLess(time.monotonic() - started, 4 if defect in ['drip', 'no-eof'] else 5)
            self.assertEqual(len(descendant), 1)
            self.assert_stopped(descendant)

    def test_guarded_public_qualifier_wiring_and_safe_output(self):
        from contextlib import redirect_stdout, redirect_stderr
        import io
        import json
        from pathlib import Path
        import tempfile
        import sys
        from unittest.mock import patch
        import qualify_startup
        import startup
        from test_startup_lifecycle import Lifecycle
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / 'supabase'
            executable.write_text('#!' + sys.executable + '\n' + Lifecycle().process_source())
            executable.chmod(0o700)
            def selected_cli(args):
                return startup.synthetic_probe(executable, self.owner.owner.target, args.run_id,
                    control=args._profile_control, selection_plan=startup.existing_images(args)[1],
                    image_observations=args._image_observations, _guarded_target=args._guarded_target)
            for control in ['guarded-fresh', 'guarded-bad-ack', 'guarded-late-use']:
                output, errors = io.StringIO(), io.StringIO()
                with self.subTest(control=control), patch.object(startup, 'qualify', side_effect=selected_cli), \
                        redirect_stdout(output), redirect_stderr(errors):
                    status = qualify_startup.main(['--target', self.owner.owner.args.target,
                        '--run-id', self.owner.owner.args.run_id, '--control', control])
                result = json.loads(output.getvalue())
                self.assertEqual(errors.getvalue(), '')
                self.assertIs(result['runtime_ready'], False)
                self.assertEqual(status, 0 if control == 'guarded-fresh' else 2)
                for private in ['sensitive', 'ENV_PRIVATE_OWNER', 'Mountpoint', 'CreatedAt']:
                    self.assertNotIn(private, output.getvalue())
                if status == 0:
                    self.assertEqual(len(result['api_events']), 70)
                    self.assertTrue(result['guarded_volume_owner_proven'])
                else:
                    self.assertEqual(set(result), {'ok', 'runtime_ready', 'stage', 'code'})
                    self.assertEqual(result['code'], 'volume_create_failed' if control == 'guarded-bad-ack' else 'volume_in_use')

    def test_integrated_private_work_configuration_change_prevents_owner_ack(self):
        import dev
        import startup
        from unittest.mock import patch
        from test_startup_lifecycle import Lifecycle
        for phase in ['inspect', 'create', 'pre-post']:
            daemon = proof.GuardedDaemon(self.owner.owner.target, self.owner.owner.args.run_id, self.owner.expected)
            source = Lifecycle().process_source().replace(
                'for command in commands:\n    subprocess.run',
                "for command in commands:\n    if command[:2] == ['volume', " + repr(phase) + "]:\n"
                "        (work/'supabase/config.toml').write_text('untrusted')\n    subprocess.run")
            command = startup.guarded_fixture_command
            def observe(*args):
                if phase == 'pre-post':
                    def mutate(*_):
                        if len(daemon.events) == 41:
                            (args[1] / 'supabase/config.toml').write_text('untrusted')
                    daemon.hook = mutate
                return command(*args)
            with self.subTest(phase=phase), patch('startup.guarded_fixture_command', side_effect=observe):
                with self.assertRaises(dev.Refusal) as caught:
                    self.integrated_probe(daemon, source=source)
                self.assertEqual(caught.exception.code, 'configuration_changed')
                self.assertFalse(any(method == 'POST' and '/volumes/' in path for method, path, _ in daemon.events))


    def test_integrated_fresh_cli_creates_through_retained_volume_owner(self):
        from pathlib import Path
        import tempfile
        import sys
        import startup
        from test_startup_lifecycle import Lifecycle
        daemon = proof.GuardedDaemon(self.owner.owner.target, self.owner.owner.args.run_id, self.owner.expected)
        with tempfile.TemporaryDirectory() as directory, daemon.serve() as endpoint:
            executable = Path(directory) / 'supabase'
            executable.write_text('#!' + sys.executable + '\n' + Lifecycle().process_source())
            executable.chmod(0o700)
            result = startup.synthetic_probe(
                executable, self.owner.owner.target, self.owner.owner.args.run_id,
                control='fresh-lifecycle-positive', selection_plan=startup.existing_images(self.owner.owner.args)[1],
                image_observations=self.owner.expected,
                _guarded_target=(self.owner.owner.args.target, endpoint))
        posts = [event for event in daemon.events if event[0] == 'POST' and '/volumes/' in event[1]]
        self.assertEqual(posts, [('POST', '/v1.48/volumes/create', proof.volume_proof.expected_request(
            self.owner.owner.target, self.owner.owner.args.run_id))])
        self.assertTrue(result['guarded_volume_owner_proven'])
        self.assertTrue(result['first_start_refused'])
        self.assertIs(result['runtime_ready'], False)
        self.assertEqual(daemon.connections, 1)
        daemon.validate_events()
        self.assertEqual(result['observed_volume'], {key: daemon.volume.volume[key] for key in
                         ['Name', 'Driver', 'Scope', 'Labels', 'Options']})

    def test_fresh_public_qualifier_rejects_changed_constructor_inputs(self):
        import copy
        import hashlib
        from contextlib import redirect_stdout
        import io
        import json
        import startup
        from unittest.mock import patch
        original = resources.invocation
        for field in ['target', 'run', 'network']:
            def changed_invocation(*args, **kwargs):
                constructor = startup.invocation
                def changed(*inputs):
                    inputs = list(copy.deepcopy(inputs))
                    if field == 'target':
                        inputs[2]['target_id'] = 'foreign'
                    elif field == 'run':
                        inputs[3] = '00000000-0000-0000-0000-000000000000'
                    else:
                        inputs[4]['Labels'] = {}
                    return constructor(*inputs)
                with patch.object(startup, 'invocation', side_effect=changed):
                    return original(*args, **kwargs)
            output = io.StringIO()
            # A plausible argv is not evidence that the constructor received the
            # admitted inputs. This stub deliberately accepts all input variants.
            plausible = (['--network-id', hashlib.sha256(self.owner.owner.args.run_id.encode()).hexdigest()],
                         {'DOCKER_HOST': 'unix:///var/run/docker.sock'})
            with self.subTest(field=field), patch.object(startup, 'invocation', return_value=plausible), \
                    patch.object(resources, 'invocation', side_effect=changed_invocation), redirect_stdout(output):
                status = proof.main(['--target', self.owner.owner.args.target, '--run-id', self.owner.owner.args.run_id, '--control', 'fresh'])
            self.assertEqual(status, 2)
            self.assertEqual(json.loads(output.getvalue())['code'], 'synthetic_outcome_mismatch')

    def test_fresh_image_daemon_and_network_negatives_have_exact_terminal_events(self):
        import dev
        import startup
        from unittest.mock import patch
        cases = [('image-missing', 'image_missing', 2), ('image-foreign', 'image_identity_mismatch', 2),
                 ('old-daemon', 'docker_28_required', 1), ('malformed', 'docker_response_invalid', 2),
                 ('slow', 'docker_timeout', 2), ('network-foreign', 'network_not_run_owned', 11),
                 ('network-replaced', 'network_replaced', 12), ('network-error', 'network_inspection_failed', 11),
                 ('lost-network-response', 'docker_response_invalid', 12)]
        for defect, code, count in cases:
            with self.subTest(defect=defect):
                daemon = self.daemon('fresh')
                if defect.startswith('image-'):
                    daemon.image_control = 'missing' if defect == 'image-missing' else 'wrong-id'
                elif defect in ['old-daemon', 'malformed', 'slow']:
                    daemon.image_control = defect
                    if defect != 'old-daemon':
                        daemon.control = defect
                elif defect == 'lost-network-response':
                    daemon.disconnect_at = count
                else:
                    daemon.network = proof.network_proof.SyntheticDaemon(
                        self.owner.owner.target, self.owner.owner.args.run_id,
                        {'network-foreign': 'foreign', 'network-replaced': 'replacement', 'network-error': 'daemon-error'}[defect])
                    daemon.expected = daemon.expected_events()
                with daemon.serve() as endpoint, patch.object(startup, 'invocation') as construct, \
                        patch.object(resources, 'SECONDS', .2 if defect == 'slow' else 5):
                    with self.assertRaises(dev.Refusal) as caught:
                        self.fresh_invocation(endpoint)
                    construct.assert_not_called()
                self.assertEqual(caught.exception.code, code)
                self.assertEqual(daemon.events, daemon.expected[:count])
                self.assertEqual(daemon.connections, 1)
                self.assertFalse(daemon.errors or daemon.network.errors or daemon.volume.errors)

    def test_fresh_existing_bridge_and_conflict_winner_preserve_exact_constructor_inputs(self):
        import startup
        from unittest.mock import patch
        for mode in ['existing', 'conflict']:
            daemon = self.daemon('fresh', _network_conflict=mode == 'conflict')
            if mode == 'existing':
                daemon.network.present = True
                daemon.expected = daemon.expected_events()
            with daemon.serve() as endpoint, patch.object(startup, 'invocation', wraps=startup.invocation) as construct:
                self.fresh_invocation(endpoint)
                construct.assert_called_once()
                _, _, target, run_id, network = construct.call_args.args
                self.assertEqual(target, self.owner.owner.target)
                self.assertEqual(run_id, self.owner.owner.args.run_id)
                expected = proof.network_proof.expected_request(target, run_id)
                self.assertEqual(network, {key: expected[key] for key in ['Name', 'Driver', 'Scope', 'Internal', 'Options', 'Labels']} |
                                 {'Id': daemon.network.network_id, 'Containers': {}})
            daemon.validate_events()
            self.assertEqual(sum(method == 'POST' for method, _, _ in daemon.events), mode == 'conflict')
            self.assertFalse(daemon.volume.present)

    def test_fresh_late_image_and_each_final_bridge_replacement_refuse_before_constructor(self):
        import dev
        import startup
        from unittest.mock import patch
        for resource in ['child', 'config', 'bridge-id-first', 'bridge-name', 'bridge-id-last']:
            daemon = self.daemon('fresh')
            if resource in ['child', 'config']:
                at = len(daemon.expected) - (11 if resource == 'child' else 7)
            else:
                at = len(daemon.expected) - {'bridge-id-first': 3, 'bridge-name': 2, 'bridge-id-last': 1}[resource]
            def replace(*args):
                if len(daemon.events) == at:
                    if resource in ['child', 'config']:
                        daemon.image_control = 'wrong-id'
                    else:
                        daemon.network.network['Id'] = 'f' * 64
            daemon.hook = replace
            with self.subTest(resource=resource), daemon.serve() as endpoint, patch.object(startup, 'invocation') as construct:
                with self.assertRaises(dev.Refusal) as caught:
                    self.fresh_invocation(endpoint)
                construct.assert_not_called()
            self.assertEqual(caught.exception.code, 'image_identity_mismatch' if resource in ['child', 'config'] else 'network_replaced')
            self.assertEqual(daemon.events, daemon.expected[:at])
            self.assertEqual(daemon.connections, 1)

    def test_fresh_invalid_workdir_refuses_before_daemon_mutation(self):
        from pathlib import Path
        import tempfile
        from unittest.mock import patch
        import dev
        import startup
        for defect in ['missing', 'contaminated', 'configuration']:
            daemon = self.daemon('fresh')
            with tempfile.TemporaryDirectory() as directory, daemon.serve() as endpoint:
                work = Path(directory)
                if defect != 'missing':
                    startup.initialize_workdir(work, self.owner.owner.target, self.owner.owner.args.run_id)
                    path = work / '.env' if defect == 'contaminated' else work / 'supabase/config.toml'
                    path.write_text('untrusted')
                with self.assertRaises(dev.Refusal):
                    resources.invocation(self.owner.owner.args.target, self.owner.owner.args.run_id,
                                         '/synthetic/supabase', work, _socket_path=endpoint)
            self.assertFalse(any(method == 'POST' for method, _, _ in daemon.events))
            self.assertFalse(daemon.network.present)

    def test_fresh_invocation_leaves_volume_absent(self):
        from pathlib import Path
        import tempfile
        import startup
        daemon = self.daemon('fresh')
        with tempfile.TemporaryDirectory() as directory, daemon.serve() as endpoint:
            work = Path(directory)
            startup.initialize_workdir(work, self.owner.owner.target, self.owner.owner.args.run_id)
            resources.invocation(self.owner.owner.args.target, self.owner.owner.args.run_id,
                                 '/synthetic/supabase', work, _socket_path=endpoint)
        self.assertFalse(daemon.volume.present)
        self.assertFalse(any(method == 'POST' and '/volumes/' in path for method, path, _ in daemon.events))
        daemon.validate_events()

    def fresh_invocation(self, endpoint):
        from pathlib import Path
        import tempfile
        import startup
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            startup.initialize_workdir(work, self.owner.owner.target, self.owner.owner.args.run_id)
            return resources.invocation(self.owner.owner.args.target, self.owner.owner.args.run_id,
                                        '/synthetic/supabase', work, _socket_path=endpoint)

    def test_fresh_existing_ambiguous_and_late_refuse(self):
        import dev
        from unittest.mock import patch
        import startup
        for control in proof.FRESH_CONTROLS[1:]:
            daemon = self.daemon(control)
            with daemon.serve() as endpoint, patch.object(startup, 'invocation') as construct:
                with self.assertRaises(dev.Refusal) as caught:
                    self.fresh_invocation(endpoint)
                construct.assert_not_called()
            self.assertEqual(caught.exception.code, proof.EXPECTED[control])
            daemon.validate_events(success=False)
            self.assertFalse(any(method == 'POST' and '/volumes/' in path for method, path, _ in daemon.events))
            if control != 'fresh-late':
                self.assertFalse(any(method == 'POST' for method, _, _ in daemon.events))
            else:
                self.assertTrue(daemon.network.present)

    def test_fresh_transport_loss_at_every_exchange_refuses_without_reconnect(self):
        import dev
        from unittest.mock import patch
        import startup
        for kind in ['disconnect_at', 'truncated_at', 'disconnect_after']:
            for request in range(1, len(self.daemon('fresh').expected) + 1):
                daemon = self.daemon('fresh')
                setattr(daemon, kind, request)
                original_idle = dev.DockerSession.idle
                def idle(session):
                    if kind == 'disconnect_after' and len(daemon.events) == request:
                        self.assertTrue(daemon.disconnected.wait(1))
                    return original_idle(session)
                with daemon.serve() as endpoint, patch.object(startup, 'invocation') as construct, patch.object(dev.DockerSession, 'idle', idle):
                    with self.assertRaises(dev.Refusal):
                        self.fresh_invocation(endpoint)
                    construct.assert_not_called()
                self.assertEqual(daemon.connections, 1)
                self.assertEqual(daemon.events, daemon.expected[:request])

    def test_fresh_custody_changes_before_network_mutation_and_constructor_refuse(self):
        import dev
        from unittest.mock import patch
        import startup
        paths = [self.owner.owner.target_path, self.owner.owner.tool_receipt,
                 self.owner.owner.run / 'receipt.json',
                 self.owner.owner.root / 'platform/deployment/resources.py',
                 self.owner.owner.root / 'platform/deployment/.local/kdg' / self.owner.owner.args.run_id / 'inventory.json',
                 self.owner.owner.root / 'platform/deployment/.local/kdg' / ('.network-' + self.owner.owner.args.run_id + '.lock')]
        for boundary in ['network', 'constructor']:
            for path in paths:
                daemon = self.daemon('fresh')
                raw = path.read_bytes() if path.exists() else b''
                at = (next(i for i, event in enumerate(daemon.expected, 1) if event[0] == 'POST') - 1
                      if boundary == 'network' else len(daemon.expected))
                def mutate(*args):
                    if len(daemon.events) == at:
                        path.write_bytes(b'changed')
                daemon.hook = mutate
                try:
                    with daemon.serve() as endpoint, patch.object(startup, 'invocation') as construct:
                        with self.assertRaises((dev.Refusal, OSError, ValueError)):
                            self.fresh_invocation(endpoint)
                        construct.assert_not_called()
                    self.assertEqual(daemon.events, daemon.expected[:at])
                finally:
                    path.write_bytes(raw)

    def test_fresh_total_budget_and_constructor_postchecks_refuse(self):
        import dev
        import startup
        import time
        from unittest.mock import patch
        for defect in ['slow', 'constructor-custody', 'constructor-budget', 'post-owner']:
            daemon = self.daemon('fresh')
            if defect == 'slow':
                daemon.hook = lambda *args: time.sleep(.03)
            path = self.owner.owner.tool_receipt
            raw = path.read_bytes()
            original = startup.invocation
            def construct(*args):
                result = original(*args)
                if defect == 'constructor-custody':
                    path.write_bytes(b'changed')
                if defect == 'constructor-budget':
                    time.sleep(.3)
                return result
            probes = []
            owner = startup.existing_images
            def probe(*args):
                probes.append(True)
                if defect == 'post-owner' and len(probes) == 2:
                    dev.refuse('daemon_images', 'image_evidence_changed')
                return owner(*args)
            try:
                with daemon.serve() as endpoint, patch.object(resources, 'SECONDS', .2 if defect in ['slow', 'constructor-budget'] else 5), \
                        patch.object(startup, 'invocation', side_effect=construct), patch.object(startup, 'existing_images', side_effect=probe):
                    with self.assertRaises(dev.Refusal):
                        self.fresh_invocation(endpoint)
                self.assertEqual(daemon.connections, 1)
            finally:
                path.write_bytes(raw)

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
            if control in proof.FRESH_CONTROLS:
                continue  # Invocation admission has its own exact negative matrix above.
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
                if control in ['positive', 'existing', 'fresh']:
                    self.assertEqual(status, 0)
                    self.assertTrue(result['ok'])
                    self.assertEqual((result['stage'], result['code']), ('resources', 'resources_synthetic_qualified'))
                    self.assertEqual(len(result['api_events']), {'positive': 32, 'existing': 29, 'fresh': 28}[control])
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

class ExecutionSupervisor(unittest.TestCase):
    """Private socket/process integration; root runs these cases serially."""
    setUp = Resources.setUp
    assert_stopped = Resources.assert_stopped
    source_with_descendant = Resources.source_with_descendant

    def run_execution_case(self, scenario, *, runner=None):
        import json
        import sys
        import tempfile
        import time
        from pathlib import Path
        from unittest.mock import patch
        import dev
        import startup
        from test_startup_lifecycle import Lifecycle
        from test_pinned_execution import OwnerDaemon, PersistenceDaemon, AuthJobDaemon, AuthCatalogDaemon
        from contextlib import nullcontext
        import socketserver
        import threading
        import copy

        # Existing independent in-memory descriptors back a real private Docker
        # protocol peer; the production DockerSession owns all framing/closure.
        initialized = scenario.startswith('initialized-')
        poststart = scenario.startswith('auth-')
        api_privileges = scenario.startswith('auth-api-')
        backend = scenario.startswith('auth-backend-') or api_privileges
        catalog = scenario.startswith('auth-catalog-') or backend
        migration = scenario.startswith('auth-migration-') or catalog
        persistence = scenario.startswith('persistence-') or initialized
        engine = AuthCatalogDaemon() if catalog else (AuthJobDaemon() if migration else (PersistenceDaemon() if persistence else OwnerDaemon()))
        if migration:
            # Discard direct-owner setup; the actual private process must replay it.
            engine.row = None
            engine.events.clear()
            # The fresh real owner supplies the only execution deadline below.
            engine.deadline = float('inf')
        # Bind templates to this retained-owner harness's prepared UUID, which
        # differs from the direct-owner fixture's independent default UUID.
        target, run_id = self.owner.owner.target, self.owner.owner.args.run_id
        engine.fixture['run_id'] = run_id
        if migration:
            engine.fixture['project'] = dev.project_identity(target, run_id)
        network = {**proof.network_proof.expected_request(target, run_id),
                   'Id': engine.network['Id'], 'Containers': {}, 'ConfigFrom': {'Network': ''}}
        volume_request = proof.volume_proof.expected_request(target, run_id)
        volume = {key: volume_request[key] for key in ['Name', 'Driver', 'Labels']}
        volume.update(Scope='local', Options=None)
        engine.network = engine.volume = None
        connections, errors, injected, reached, created = [], [], [], [], []
        fault_at, group_signals = [], []
        real_monotonic = time.monotonic
        clock_shift = [0]
        if migration and scenario == 'auth-migration-nonzero':
            def job_failure(method, path, body):
                if method == 'GET' and engine.job_row and engine.job_row['State']['Status'] == 'exited':
                    engine.job_row['State']['ExitCode'] = 1
            engine.job_fault = job_failure

        def dispatch(method, path, body):
            if path == '/version':
                engine.events.append((method, path, body))
                return 200, {'Os': 'linux', 'Version': '28.0.0'}
            if method == 'POST' and path == '/v1.48/networks/create':
                engine.events.append((method, path, body))
                engine.network = copy.deepcopy(network)
                return 201, {'Id': network['Id'], 'Warning': ''}
            if method == 'POST' and path == '/v1.48/volumes/create':
                engine.events.append((method, path, body))
                engine.volume = copy.deepcopy(volume)
                return 201, copy.deepcopy(volume)
            if api_privileges and path.endswith('/exec'):
                query = body['Cmd'][-1]
                mode = ('apply' if 'api default privileges delta failed' in query else
                        'verify' if 'api default privileges verification failed' in query else None)
                engine.catalog_valid = scenario != 'auth-api-' + str(mode) + '-nonzero'
            result = engine.exchange(method, path, body)
            if api_privileges and engine.catalog_modes and engine.catalog_modes[-1] in ('apply', 'verify'):
                mode = engine.catalog_modes[-1]
                if path.startswith('/v1.48/exec/') and path.endswith('/json') and engine.exec_started:
                    if scenario == 'auth-api-verify-identity' and mode == 'verify':
                        result[1]['ContainerID'] = 'f'*64
                    if scenario == 'auth-api-verify-custody' and mode == 'verify':
                        engine.row['State']['Health']['Status'] = 'unhealthy'
                if path.startswith('/v1.48/exec/') and path.endswith('/start'):
                    if scenario == 'auth-api-apply-deadline' and mode == 'apply':
                        clock_shift[0] = 121
            if migration and path.endswith('/start') and 'c'*64 in path and scenario == 'auth-migration-response-deadline':
                fault_at.append((len(engine.events), guards[0].deadline))
                clock_shift[0] = 121
            if method == 'POST' and '/containers/create?' in path:
                created.append(result[1]['Id'])
            if '/archive?' in path and scenario.startswith('copy-') or path.endswith('/start') and not scenario.startswith('copy-'):
                reached.append((method, path))
            if scenario == 'post-start-health' and path.endswith('/start'):
                engine.row['State']['Health']['Status'] = 'invalid'
            if scenario in ('persistence-sql-failure', 'initialized-sql-failure') and '/containers/create?' in path and engine.creates == 2:
                engine.marker = None
            return result

        class Handler(socketserver.BaseRequestHandler):
            def handle(peer):
                connections.append(True)
                # The initialized CLI launches its independent wrapper sequence
                # between owner requests. Let the retained owner's 120s execution
                # deadline bound that idle interval, rather than injecting a
                # separate five-second daemon EOF into envelope-refusal controls.
                peer.request.settimeout(120 if initialized or poststart else 5)
                try:
                    while True:
                        data = b''
                        while b'\r\n\r\n' not in data:
                            piece = peer.request.recv(4096)
                            if not piece:
                                return
                            data += piece
                            if len(data) > 16384:
                                raise ValueError()
                        header, body = data.split(b'\r\n\r\n', 1)
                        lines = header.split(b'\r\n')
                        method, path, protocol = lines[0].decode().split(' ')
                        fields = dict(line.lower().split(b':', 1) for line in lines[1:])
                        size = int(fields.get(b'content-length', b'0'))
                        if size > 16384 or protocol != 'HTTP/1.1':
                            raise ValueError()
                        while len(body) < size:
                            piece = peer.request.recv(4096)
                            if not piece:
                                raise ValueError()
                            body += piece
                        if len(body) != size:
                            raise ValueError()
                        payload = body if b'application/x-tar' in fields.get(b'content-type', b'') else dev.decode(body) if body else None
                        status, result = dispatch(method, path, payload)
                        target = ('/archive?' in path if scenario.startswith('copy-') else
                                  path.endswith('/start') if scenario.startswith('start-') else False)
                        if initialized and engine.creates == 2:
                            target = ('/archive?' in path if scenario.startswith('initialized-copy-') else
                                      path.endswith('/start') if scenario.startswith('initialized-start-') else
                                      '/containers/create?' in path if scenario.startswith('initialized-create-') else False)
                        if (api_privileges and scenario == 'auth-api-apply-lost'
                                and path.startswith('/v1.48/exec/') and path.endswith('/start')
                                and engine.catalog_modes[-1] == 'apply'):
                            target = True
                        if target:
                            injected.append((method, path))
                            if scenario.endswith('-malformed'):
                                peer.request.sendall(b'HTTP/1.1 200 Result\r\nContent-Length: 1\r\n\r\nx')
                            return
                        raw = b'' if result is None and status in (200, 204) else json.dumps(result).encode()
                        peer.request.sendall((f'HTTP/1.1 {status} Result\r\nContent-Length: {len(raw)}\r\n\r\n').encode()+raw)
                except (OSError, ValueError, dev.Refusal):
                    errors.append('private_peer_failure')

        selected_runner = runner or startup.guarded_fixture_command
        cleanup = resources.FreshGuard.cleanup_execution
        create_container = resources.FreshGuard.container_create
        initialize = startup.initialize_workdir
        install = startup.install_fixture
        killpg = startup.os.killpg
        def signal_group(pid, selected_signal):
            group_signals.append(pid)
            return killpg(pid, selected_signal)
        def initialize_secondary(work, *args):
            if scenario == 'initialized-fixture-failure' and guards:
                startup.fail('fixture_init_failed')
            return initialize(work, *args)
        def install_secondary(work, *args, **kwargs):
            install(work, *args, **kwargs)
            if poststart and scenario in ('auth-health-envelope', 'auth-job-envelope', 'auth-health-ack', 'auth-health-lost', 'auth-job-lost'):
                path = work / 'bin/docker'
                phase = 'auth_job' if scenario.startswith('auth-job-') else 'poststart_health'
                code = ("original_handoff = startup.owner_handoff\n"
                        "def handoff(fixture, phase, args, environment, **kwargs):\n"
                        "    if phase == " + repr(phase) + ": args = args + ['extra']\n"
                        "    return original_handoff(fixture, phase, args, environment, **kwargs)\n"
                        "startup.owner_handoff = handoff\n")
                if scenario in ('auth-health-ack', 'auth-health-lost'):
                    code = ("original_handoff = startup.owner_handoff\n"
                            "class AckPeer:\n"
                            "    def __init__(self, peer): self.peer = peer\n"
                            "    def __enter__(self): self.peer.__enter__(); return self\n"
                            "    def __exit__(self, *args): return self.peer.__exit__(*args)\n"
                            "    def __getattr__(self, name): return getattr(self.peer, name)\n"
                            "    def recv(self, size):\n"
                            "        data = self.peer.recv(size)\n"
                            "        return " + ("b''" if scenario.endswith('lost') else "b'bad' if data else data") + "\n"
                            "def handoff(fixture, phase, args, environment, **kwargs):\n"
                            "    if phase != 'poststart_health': return original_handoff(fixture, phase, args, environment, **kwargs)\n"
                            "    socket_type = startup.socket.socket\n"
                            "    startup.socket.socket = lambda *args, **kwargs: AckPeer(socket_type(*args, **kwargs))\n"
                            "    try: return original_handoff(fixture, phase, args, environment, **kwargs)\n"
                            "    finally: startup.socket.socket = socket_type\n"
                            "startup.owner_handoff = handoff\n")
                if scenario == 'auth-job-lost':
                    code = ("original_handoff = startup.owner_handoff\n"
                            "def handoff(fixture, phase, args, environment, **kwargs):\n"
                            "    if phase == 'auth_job':\n"
                            "        with startup.socket.socket(startup.socket.AF_UNIX) as peer:\n"
                            "            peer.connect(str(Path(fixture['workdir'])/'docker/owner.sock'))\n"
                            "            peer.shutdown(startup.socket.SHUT_WR)\n"
                            "            peer.recv(1)\n"
                            "        startup.fail('invalid_owner_handoff')\n"
                            "    return original_handoff(fixture, phase, args, environment, **kwargs)\n"
                            "startup.owner_handoff = handoff\n")
                path.write_text(path.read_text().replace('args, env = sys.argv[1:], dict(os.environ)', code + 'args, env = sys.argv[1:], dict(os.environ)'))
            if scenario not in ('initialized-probe-envelope', 'initialized-ensure-envelope', 'initialized-probe-ack', 'initialized-ensure-ack') or not guards:
                return
            path = work / 'bin/docker'
            selected_phase = 'initialized_probe' if scenario.startswith('initialized-probe-') else 'initialized_ensure'
            code = ("original_handoff = startup.owner_handoff\n"
                    "def handoff(fixture, phase, args, environment, **kwargs):\n"
                    "    if phase == " + repr(selected_phase) + ": args = args + ['extra']\n"
                    "    return original_handoff(fixture, phase, args, environment, **kwargs)\n"
                    "startup.owner_handoff = handoff\n")
            if scenario.endswith('-ack'):
                code = ("original_handoff = startup.owner_handoff\n"
                        "class AckPeer:\n"
                        "    def __init__(self, peer): self.peer = peer\n"
                        "    def __enter__(self): self.peer.__enter__(); return self\n"
                        "    def __exit__(self, *args): return self.peer.__exit__(*args)\n"
                        "    def __getattr__(self, name): return getattr(self.peer, name)\n"
                        "    def recv(self, size):\n"
                        "        data = self.peer.recv(size)\n"
                        "        return b'bad\\n' if data == b'OK\\n' else data\n"
                        "def handoff(fixture, phase, args, environment, **kwargs):\n"
                        "    if phase != " + repr(selected_phase) + ": return original_handoff(fixture, phase, args, environment, **kwargs)\n"
                        "    socket_type = startup.socket.socket\n"
                        "    startup.socket.socket = lambda *args, **kwargs: AckPeer(socket_type(*args, **kwargs))\n"
                        "    try: return original_handoff(fixture, phase, args, environment, **kwargs)\n"
                        "    finally: startup.socket.socket = socket_type\n"
                        "startup.owner_handoff = handoff\n")
            path.write_text(path.read_text().replace('args, env = sys.argv[1:], dict(os.environ)', code + 'args, env = sys.argv[1:], dict(os.environ)'))
        def create_with_fault(guard, *args, **kwargs):
            result = create_container(guard, *args, **kwargs)
            if poststart:
                execution_deadlines.append(guard.deadline)
            if kwargs.get('_replacement') and scenario in ('initialized-wrapper-mutation', 'initialized-listener-mutation',
                                                          'initialized-deadline', 'initialized-interrupt'):
                fault_at.append((len(engine.events), guard.deadline))
                if scenario == 'initialized-wrapper-mutation':
                    path = guard._second_fixture[0] / 'bin/docker'
                    path.write_text(path.read_text() + '\n# changed after create\n')
                elif scenario == 'initialized-listener-mutation':
                    (guard._second_fixture[0] / 'docker/owner.sock').chmod(0o644)
                elif scenario == 'initialized-deadline':
                    clock_shift[0] = 121
                else:
                    raise KeyboardInterrupt()
            return result
        calls, guards, pids, fixture_workdirs = [], [], [], []
        execute_job = resources.FreshGuard.execute_auth_job
        job_owned = resources.FreshGuard.auth_job_owned
        job_entry_deadlines = []
        catalog_entry_deadlines = []
        catalog_sql = resources.FreshGuard.auth_catalog_sql
        backend_sql = getattr(resources.FreshGuard, 'cli_db_backend_sql', None)
        backend_phases, backend_deadlines = [], []
        api_deadlines = []
        api_sql = getattr(resources.FreshGuard, 'api_default_privileges_sql', None)
        def api_after_auth_and_cli_exit(guard):
            self.assert_stopped(json.loads((fixture_workdirs[-1] / 'tmp/processes.json').read_text()))
            self.assertEqual(len(group_signals), 1)
            self.assertEqual(backend_phases, ['present', 'departed'])
            self.assertTrue(guard.auth_cli_terminated)
            self.assertTrue(guard.auth_catalog_precondition_verified and guard.auth_catalog_verified)
            self.assertTrue(guard.auth_job_exit_verified and guard.auth_job_disposed)
            self.assertEqual(engine.catalog_modes, ['post', 'post', 'pre', 'post'])
            api_deadlines.append(guard.deadline)
            try:
                return api_sql(guard)
            finally:
                before = len(engine.events)
                with self.assertRaises(dev.Refusal) as replay:
                    api_sql(guard)
                self.assertEqual(replay.exception.code, 'invalid_owner_handoff')
                self.assertEqual(len(engine.events), before)

        def backend_at_cli_boundary(guard, mode, process=None):
            current_pids = json.loads((fixture_workdirs[-1] / 'tmp/processes.json').read_text())
            if mode == 'present':
                self.assertIsNone(process.poll())
                self.assertFalse(guard.auth_cli_terminated)
                self.assertEqual(group_signals, [])
                for pid in current_pids:
                    state = Path('/proc/' + str(pid) + '/stat').read_text().split(') ', 1)[1].split()[0]
                    self.assertNotEqual(state, 'Z', 'CLI must be live before backend observation')
            else:
                self.assert_stopped(current_pids)
                self.assertEqual(len(group_signals), 1)
                self.assertTrue(guard.auth_cli_terminated)
            backend_phases.append(mode)
            backend_deadlines.append(guard.deadline)
            if scenario == 'auth-backend-wrapper-alarm' and mode == 'present':
                # Exceed the unchanged helper alarm while its verified CLI
                # parent is blocked. Timeout must stop that parent, not return
                # control to an unchecked CLI continuation.
                time.sleep(6)
            engine.catalog_valid = scenario != 'auth-backend-' + mode + '-failure'
            return backend_sql(guard, mode, process)
        def catalog_after_cli_exit(guard, mode):
            current_pids = json.loads((fixture_workdirs[-1] / 'tmp/processes.json').read_text())
            self.assert_stopped(current_pids)
            self.assertEqual(len(group_signals), 1)
            self.assertTrue(guard.auth_cli_terminated)
            catalog_entry_deadlines.append(guard.deadline)
            engine.catalog_valid = scenario != 'auth-catalog-' + mode + '-failure'
            if mode == 'post' and scenario in ('auth-catalog-request-admitted', 'auth-catalog-request-wrong-refusal'):
                serializer = dev._docker_request
                def injected_serializer(method, path, body, persistent):
                    if startup.lifecycle.valid_api_default_privileges_exec(body):
                        if scenario == 'auth-catalog-request-admitted':
                            return b'constructed only, never transmitted'
                        dev.refuse('docker', 'docker_timeout')
                    return serializer(method, path, body, persistent)
                with patch.object(dev, '_docker_request', side_effect=injected_serializer):
                    return catalog_sql(guard, mode)
            return catalog_sql(guard, mode)
        def execute_after_cli_exit(guard):
            current_pids = json.loads((fixture_workdirs[-1] / 'tmp/processes.json').read_text())
            self.assert_stopped(current_pids)
            self.assertEqual(len(group_signals), 1)
            self.assertTrue(guard.auth_cli_terminated)
            job_entry_deadlines.append(guard.deadline)
            return execute_job(guard)
        def inspect_job_with_fault(guard):
            if scenario == 'auth-migration-deadline' and guard.auth_job_start_attempted and not fault_at:
                fault_at.append((len(engine.events), guard.deadline))
                clock_shift[0] = 121
            if scenario == 'auth-migration-interrupt' and guard.auth_job_start_attempted and not fault_at:
                fault_at.append((len(engine.events), guard.deadline))
                raise KeyboardInterrupt()
            return job_owned(guard)
        execution_deadlines, health_observations, health_deadlines = [], [], []
        health = resources.FreshGuard.poststart_health
        def health_with_fault(guard):
            if scenario == 'auth-polling':
                engine.row['State']['Health']['Status'] = ['starting', 'unhealthy', 'starting', 'healthy'][len(health_observations)]
            before = guard.deadline
            state = health(guard)
            health_observations.append(state['Health']['Status'])
            health_deadlines.append((before, guard.deadline))
            if poststart and not migration and not fault_at:
                fault_at.append((len(engine.events), guard.deadline))
                if scenario == 'auth-instance':
                    engine.row['State']['StartedAt'] = '2026-10-17T12:00:00.000000002Z'
                elif scenario == 'auth-custody':
                    changed = guard._fixture[0] / 'bin/docker'
                    changed.write_text(changed.read_text() + '\n# changed custody\n')
                elif scenario == 'auth-deadline':
                    clock_shift[0] = 121
                elif scenario == 'auth-interrupt':
                    raise KeyboardInterrupt()
            return state
        def record_cleanup(guard, *args, **kwargs):
            entry = {'at': time.monotonic(), 'closed': guard.session.closed, 'execution_deadline': guard.deadline}
            calls.append(entry)
            try:
                return cleanup(guard, *args, **kwargs)
            finally:
                entry.update(deadline=guard.deadline, duration=time.monotonic()-entry['at'])
        def observe(*args):
            guards.append(args[-1])
            fixture_workdirs.append(args[1])
            try:
                return selected_runner(*args)
            finally:
                pids.extend(json.loads((args[1] / 'tmp/processes.json').read_text()))
                self.assertFalse((args[1] / 'forbidden_after_start').exists())

        with tempfile.TemporaryDirectory(prefix='env-execution-process-') as directory:
            root = Path(directory)
            path = str(root / 'daemon.sock')
            executable = root / 'supabase'
            process_source = self.source_with_descendant(Lifecycle().process_source())
            if poststart:
                continuation = """if result.returncode: sys.exit(result.returncode)
result = subprocess.run(['docker', 'container', 'inspect', 'supabase_db_'+p, '--format', '{{json .State}}'], capture_output=True, text=True)
if result.returncode: sys.exit(result.returncode)
assert json.loads(result.stdout)['Health']['Status'] == 'healthy'
from test_pinned_execution import PoststartAuthBoundary
job_args, job_env = PoststartAuthBoundary().job(f)
os.environ.update(job_env)
auth = next(tag for tag in f['images'] if '/gotrue:' in tag)
result = subprocess.run(['docker', 'image', 'inspect', auth], capture_output=True)
if result.returncode: sys.exit(result.returncode)
result = subprocess.run(['docker', *job_args])
"""
                if scenario == 'auth-polling':
                    single_poll = """result = subprocess.run(['docker', 'container', 'inspect', 'supabase_db_'+p, '--format', '{{json .State}}'], capture_output=True, text=True)
if result.returncode: sys.exit(result.returncode)
assert json.loads(result.stdout)['Health']['Status'] == 'healthy'
"""
                    repeated_polls = """for attempt in range(4):
    result = subprocess.run(['docker', 'container', 'inspect', 'supabase_db_'+p, '--format', '{{json .State}}'], capture_output=True, text=True)
    if result.returncode: sys.exit(result.returncode)
    status = json.loads(result.stdout)['Health']['Status']
    if status == 'healthy': break
    assert status in ('starting', 'unhealthy')
else: sys.exit(125)
"""
                    self.assertIn(single_poll, continuation)
                    continuation = continuation.replace(single_poll, repeated_polls)
                process_source = process_source.replace("(work/'forbidden_after_start').write_text", continuation + "(work/'forbidden_after_start').write_text")
            if scenario in ('initialized-probe-ack', 'initialized-ensure-ack', 'auth-health-ack', 'auth-health-lost'):
                # Keep the descendant alive in the CLI group, but let the owner's
                # pipe EOF expose this ACK refusal immediately after the CLI exits.
                # Inherited-pipe retention has a separate dedicated control.
                process_source = process_source.replace(
                    "extra = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])",
                    "extra = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)")
            executable.write_text('#!'+sys.executable+'\n'+process_source)
            executable.chmod(0o700)
            with socketserver.UnixStreamServer(path, Handler) as server:
                thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': .01}, daemon=True)
                thread.start()
                try:
                    with patch.object(startup, 'guarded_fixture_command', side_effect=observe), \
                            patch.object(resources.FreshGuard, 'cleanup_execution', new=record_cleanup), \
                            patch.object(resources.FreshGuard, 'container_create', new=create_with_fault), \
                            patch.object(resources.FreshGuard, 'poststart_health', new=health_with_fault), \
                            patch.object(resources.FreshGuard, 'execute_auth_job', new=execute_after_cli_exit), \
                            patch.object(resources.FreshGuard, 'auth_catalog_sql', new=catalog_after_cli_exit), \
                            patch.object(resources.FreshGuard, 'api_default_privileges_sql', new=api_after_auth_and_cli_exit, create=True), \
                            patch.object(resources.FreshGuard, 'cli_db_backend_sql', new=backend_at_cli_boundary, create=True), \
                            patch.object(resources.FreshGuard, 'auth_job_owned', new=inspect_job_with_fault), \
                            patch.object(startup, 'initialize_workdir', side_effect=initialize_secondary), \
                            patch.object(startup, 'install_fixture', side_effect=install_secondary), \
                            patch.object(startup.os, 'killpg', side_effect=signal_group), \
                            patch.object(time, 'monotonic', side_effect=lambda: real_monotonic() + clock_shift[0]), \
                            patch.object(dev, 'free_ports'):
                        result = None
                        with (nullcontext() if scenario in ('persistence-positive', 'initialized-positive', 'auth-positive', 'auth-polling', 'auth-migration-positive', 'auth-catalog-positive', 'auth-backend-positive', 'auth-api-positive') else self.assertRaises(KeyboardInterrupt if scenario in ('initialized-interrupt', 'auth-interrupt', 'auth-migration-interrupt') else dev.Refusal)) as caught:
                            result = startup.synthetic_probe(executable, self.owner.owner.target, self.owner.owner.args.run_id,
                                    control='fresh-pinned-cli-postgres-api-default-privileges' if api_privileges else 'fresh-pinned-cli-postgres-cli-db-backend' if backend else ('fresh-pinned-cli-postgres-auth-catalog' if catalog else ('fresh-pinned-cli-postgres-auth-migration' if migration else ('fresh-pinned-cli-postgres-auth-boundary' if poststart else ('fresh-pinned-cli-postgres-initialized' if initialized else ('fresh-pinned-cli-postgres-persistence' if persistence else 'fresh-pinned-cli-postgres'))))),
                                    selection_plan=startup.existing_images(self.owner.owner.args)[1],
                                    image_observations=self.owner.expected,
                                    _guarded_target=(self.owner.owner.args.target, path))
                finally:
                    server.shutdown()
                    thread.join(timeout=1)

        if result is not None and not api_privileges:
            self.assertNotIn('api_default_privileges_verified', result)
        if api_privileges:
            guard = guards[0]
            positive = scenario == 'auth-api-positive'
            self.assert_stopped(pids)
            self.assertEqual((len(pids), len(group_signals), len(connections), len(calls)), (2, 1, 1, 1))
            self.assertEqual(backend_phases, ['present', 'departed'])
            self.assertEqual(backend_deadlines, execution_deadlines * 2)
            self.assertEqual(catalog_entry_deadlines, execution_deadlines * 2)
            self.assertEqual(api_deadlines, execution_deadlines)
            self.assertEqual(created, ['a'*64, 'c'*64])
            self.assertTrue(guard.api_default_privileges_attempted)
            self.assertEqual(guard.api_default_privileges_verified, positive)
            expected_modes = ['post', 'post', 'pre', 'post', 'apply']
            if positive or scenario.startswith('auth-api-verify-'):
                expected_modes.append('verify')
            self.assertEqual(engine.catalog_modes, expected_modes)
            events = engine.events
            exec_creates = [i for i, (method, path, _) in enumerate(events) if method == 'POST' and path.endswith('/exec')]
            self.assertEqual(len(exec_creates), len(expected_modes))
            self.assertEqual(sum(startup.lifecycle.API_DEFAULT_PRIVILEGES_SQL in body['Cmd'][-1]
                                 for method, path, body in events if method == 'POST' and path.endswith('/exec')), 1)
            job_delete = next(i for i, (method, path, _) in enumerate(events) if method == 'DELETE' and 'c'*64 in path)
            self.assertLess(job_delete, exec_creates[3])
            self.assertIsNone(engine.job_row)
            if scenario in ('auth-api-apply-lost', 'auth-api-apply-deadline'):
                self.assertTrue(guard.session.closed)
                self.assertFalse(guard.cleaned)
                self.assertIsNotNone(engine.row)
                self.assertEqual(caught.exception.code, 'execution_cleanup_unresolved')
                self.assertFalse(any(method == 'DELETE' and 'a'*64 in path for method, path, _ in events))
            else:
                self.assertTrue(guard.cleaned)
                self.assertIsNone(engine.row)
                pg_disposal = next(i for i, (method, path, _) in enumerate(events)
                                   if 'a'*64 in path and (method == 'DELETE' or (method == 'POST' and '/stop?' in path)))
                self.assertLess(exec_creates[-1], pg_disposal)
                if not positive:
                    expected_code = ('execution_invalid_exec' if scenario.endswith('-identity') else
                                     'execution_invalid_health' if scenario.endswith('-custody') else 'execution_sql_failed')
                    self.assertEqual(caught.exception.code, expected_code)
            if positive:
                self.assertEqual(result['stage'], 'pinned_cli_postgres_api_default_privileges')
                self.assertTrue(result['api_default_privileges_verified'])
                for key in ['cli_db_backend_present_verified', 'cli_db_backend_departure_verified',
                            'auth_catalog_precondition_verified', 'auth_catalog_verified',
                            'api_default_privileges_request_refused', 'cli_terminated_before_dispatch',
                            'auth_job_exit_verified', 'auth_job_disposal_verified', 'pg_shutdown_verified', 'cleanup_verified']:
                    self.assertTrue(result[key])
                self.assertFalse(result['fresh_setup_completed'] or result['runtime_ready'])
            else:
                self.assertIsNone(result)
            return
        if backend:
            guard = guards[0]
            if scenario == 'auth-backend-wrapper-alarm':
                self.assert_stopped(pids)
                self.assertEqual(backend_phases, ['present'])
                self.assertEqual(caught.exception.code, 'invalid_owner_handoff')
                self.assertEqual((len(pids), len(group_signals), len(connections), len(calls)), (2, 1, 1, 1))
                self.assertEqual(created, ['a'*64])
                self.assertFalse(guard.cli_db_backend_present_verified or guard.cli_db_backend_departure_verified)
                self.assertFalse(guard.auth_job_dispatched or guard.ownership_lost)
                self.assertTrue(guard.cleaned)
                self.assertEqual(job_entry_deadlines, [])
                self.assertEqual(catalog_entry_deadlines, [])
                self.assertIsNone(engine.row)
                return
            positive = scenario == 'auth-backend-positive'
            present_failed = scenario == 'auth-backend-present-failure'
            self.assert_stopped(pids)
            self.assertEqual((len(pids), len(group_signals), len(connections), len(calls)), (2, 1, 1, 1))
            self.assertEqual(backend_phases, ['present'] if present_failed else ['present', 'departed'])
            self.assertEqual(backend_deadlines, execution_deadlines * len(backend_phases))
            self.assertEqual(created, ['a'*64, 'c'*64] if positive else ['a'*64])
            self.assertEqual(job_entry_deadlines, execution_deadlines if positive else [])
            self.assertEqual(catalog_entry_deadlines, execution_deadlines * 2 if positive else [])
            self.assertTrue(guard.cleaned)
            self.assertIsNone(engine.row)
            self.assertIsNone(engine.job_row)
            self.assertEqual(guard.cli_db_backend_present_verified, not present_failed)
            self.assertEqual(guard.cli_db_backend_departure_verified, positive)
            self.assertEqual(guard.auth_catalog_verified, positive)
            events = engine.events
            exec_creates = [i for i, (method, path, _) in enumerate(events) if method == 'POST' and path.endswith('/exec')]
            self.assertFalse(any('alter default privileges' in str(body) for _, _, body in events))
            self.assertEqual(len(exec_creates), 4 if positive else len(backend_phases))
            pg_disposal = next(i for i, (method, path, _) in enumerate(events) if 'a'*64 in path and (method == 'DELETE' or (method == 'POST' and '/stop?' in path)))
            self.assertLess(exec_creates[-1], pg_disposal)
            if positive:
                job_create = next(i for i, (method, path, _) in enumerate(events) if method == 'POST' and 'name=supabase_auth_migrate_' in path)
                job_delete = next(i for i, (method, path, _) in enumerate(events) if method == 'DELETE' and 'c'*64 in path)
                self.assertLess(exec_creates[2], job_create)
                self.assertLess(job_delete, exec_creates[3])
                for key in ['cli_db_backend_present_verified', 'cli_db_backend_departure_verified', 'auth_catalog_precondition_verified', 'auth_catalog_verified', 'api_default_privileges_request_refused', 'auth_job_exit_verified', 'auth_job_disposal_verified', 'cli_terminated_before_dispatch', 'pg_shutdown_verified', 'cleanup_verified']:
                    self.assertTrue(result[key])
                self.assertFalse(result['fresh_setup_completed'] or result['runtime_ready'])
                self.assertNotIn('api_default_privileges_verified', result)
            else:
                self.assertEqual(caught.exception.code, 'execution_sql_failed')
            return
        if catalog:
            guard = guards[0]
            self.assert_stopped(pids)
            self.assertEqual((len(pids), len(group_signals), len(connections), len(calls)), (2, 1, 1, 1))
            pre_failed = scenario == 'auth-catalog-pre-failure'
            self.assertEqual(created, ['a'*64] if pre_failed else ['a'*64, 'c'*64])
            self.assertEqual(engine.catalog_modes, ['pre'] if pre_failed else ['pre', 'post'])
            self.assertEqual(catalog_entry_deadlines, execution_deadlines * (1 if pre_failed else 2))
            self.assertEqual(job_entry_deadlines, [] if pre_failed else execution_deadlines)
            self.assertTrue(guard.cleaned)
            self.assertIsNone(engine.row)
            self.assertIsNone(engine.job_row)
            self.assertEqual(guard.auth_catalog_precondition_verified, not pre_failed)
            self.assertEqual(guard.auth_catalog_verified, scenario == 'auth-catalog-positive')
            events = engine.events
            exec_creates = [i for i, (method, path, _) in enumerate(events) if method == 'POST' and path.endswith('/exec')]
            self.assertFalse(any('alter default privileges' in str(body) for _, _, body in events))
            self.assertEqual(len(exec_creates), 1 if pre_failed else 2)
            pg_disposal = next(i for i, (method, path, _) in enumerate(events) if 'a'*64 in path and (method == 'DELETE' or (method == 'POST' and '/stop?' in path)))
            self.assertLess(exec_creates[-1], pg_disposal)
            if not pre_failed:
                job_create = next(i for i, (method, path, _) in enumerate(events) if method == 'POST' and 'name=supabase_auth_migrate_' in path)
                job_delete = next(i for i, (method, path, _) in enumerate(events) if method == 'DELETE' and 'c'*64 in path)
                self.assertLess(exec_creates[0], job_create)
                self.assertLess(job_delete, exec_creates[1])
            if scenario == 'auth-catalog-positive':
                for key in ['auth_catalog_precondition_verified', 'auth_catalog_verified', 'api_default_privileges_request_refused', 'auth_job_exit_verified', 'auth_job_disposal_verified', 'cli_terminated_before_dispatch', 'pg_shutdown_verified', 'cleanup_verified']:
                    self.assertTrue(result[key])
                self.assertFalse(result['fresh_setup_completed'] or result['runtime_ready'])
            else:
                expected_code = {'auth-catalog-request-admitted': 'invalid_owner_handoff',
                                 'auth-catalog-request-wrong-refusal': 'docker_timeout'}.get(scenario, 'execution_sql_failed')
                self.assertEqual(caught.exception.code, expected_code)
                self.assertIsNone(result)
                self.assertFalse(guard.api_default_privileges_request_refused)
            return
        if migration:
            guard = guards[0]
            self.assert_stopped(pids)
            self.assertEqual(len(pids), 2)
            self.assertEqual(len(group_signals), 1)
            self.assertEqual(created, ['a'*64, 'c'*64])
            self.assertEqual(len(connections), 1)
            self.assertEqual(len(calls), 1)
            self.assertEqual(job_entry_deadlines, execution_deadlines)
            if scenario == 'auth-migration-response-deadline':
                # Expiry during the start exchange closes the retained transport:
                # cleanup cannot reconnect or infer the uncertain job outcome.
                self.assertTrue(guard.session.closed)
                self.assertFalse(guard.cleaned)
                self.assertIsNotNone(engine.row)
                self.assertIsNotNone(engine.job_row)
                self.assertFalse(guard.auth_job_exit_verified)
                self.assertFalse(any(method == 'DELETE' for method, _, _ in engine.events))
                self.assertEqual(caught.exception.code, 'execution_cleanup_unresolved')
                self.assertEqual(calls[0]['execution_deadline'], execution_deadlines[0])
                return
            self.assertTrue(guard.cleaned)
            self.assertIsNone(engine.row)
            self.assertIsNone(engine.job_row)
            writes = [(method, path) for method, path, _ in engine.events if method != 'GET']
            job_deletes = [i for i, (method, path) in enumerate(writes) if method == 'DELETE' and 'c'*64 in path]
            pg_disposal = [i for i, (method, path) in enumerate(writes) if method in ('DELETE', 'POST') and 'a'*64 in path and ('force=' in path or '/stop?' in path)]
            self.assertEqual(len(job_deletes), 1)
            self.assertLess(job_deletes[0], min(pg_disposal))
            self.assertEqual(sum(method == 'POST' and path.endswith('/start') for method, path in writes), 2)
            if scenario == 'auth-migration-positive':
                self.assertNotIn('api_default_privileges_request_refused', result)
                for key in ['auth_job_dispatched', 'auth_job_exit_verified', 'auth_job_disposal_verified',
                            'cli_terminated_before_dispatch', 'pg_shutdown_verified', 'cleanup_verified']:
                    self.assertTrue(result[key])
                for key in ['auth_job_refused', 'fresh_setup_completed', 'runtime_ready']:
                    self.assertFalse(result[key])
            else:
                self.assertFalse(guard.auth_job_exit_verified)
                self.assertEqual(calls[0]['execution_deadline'], execution_deadlines[0])
                if scenario == 'auth-migration-nonzero': self.assertEqual(caught.exception.code, 'execution_auth_job_failed')
                if scenario == 'auth-migration-deadline': self.assertEqual(caught.exception.code, 'docker_timeout')
            return
        if poststart:
            guard = guards[0]
            self.assert_stopped(pids)
            self.assertEqual(len(pids), 2)
            self.assertEqual(len(group_signals), 1, 'signal the proven CLI group once')
            self.assertEqual(created, ['a'*64])
            self.assertEqual(len(connections), 1)
            self.assertEqual(len(calls), 1)
            self.assertTrue(guard.cleanup_attempted)
            self.assertEqual(sum('/containers/create?' in p for _, p, _ in engine.events), 1)
            self.assertEqual(sum(p.endswith('/start') for _, p, _ in engine.events), 1)
            if scenario in ('auth-positive', 'auth-polling'):
                self.assertNotIn('api_default_privileges_request_refused', result)
                self.assertTrue(result['auth_job_profile_validated'])
                self.assertTrue(result['auth_job_refused'])
                self.assertFalse(result['auth_job_dispatched'])
                self.assertFalse(result['runtime_ready'])
                self.assertTrue(guard.cleaned)
                self.assertIsNone(engine.row)
                if scenario == 'auth-polling':
                    self.assertEqual(health_observations, ['starting', 'unhealthy', 'starting', 'healthy'])
                    self.assertEqual(len(execution_deadlines), 1)
                    self.assertEqual(health_deadlines, [(execution_deadlines[0], execution_deadlines[0])] * 4)
            elif scenario == 'auth-custody':
                self.assertTrue(guard.ownership_lost)
                self.assertFalse(guard.cleaned)
                self.assertIsNotNone(engine.row)
            else:
                self.assertFalse(guard.auth_job_refused)
                self.assertTrue(guard.cleaned)
                self.assertIsNone(engine.row)
                if scenario == 'auth-deadline':
                    self.assertEqual(caught.exception.code, 'docker_timeout')
                    self.assertEqual(calls[0]['execution_deadline'], fault_at[0][1],
                                     'post-start observations cannot reset the execution deadline')
            return
        if initialized:
            self.assertEqual(len(group_signals), len(set(group_signals)), 'never signal a reaped numeric group twice')
            self.assert_stopped(pids)
        if scenario in ('initialized-fixture-failure', 'initialized-probe-envelope', 'initialized-ensure-envelope', 'initialized-probe-ack', 'initialized-ensure-ack'):
            self.assertEqual(created, ['a'*64])
            self.assertEqual(len(calls), 0)
            self.assertEqual(errors, [], 'private daemon must remain available for final owned checks')
            self.assertIsNone(engine.row)
            self.assertIsNotNone(engine.volume)
            self.assertFalse(guards[0].persistence_verified)
            self.assertEqual(len(pids), 2 if scenario == 'initialized-fixture-failure' else 4)
            self.assertEqual(len(group_signals), 1 if scenario == 'initialized-fixture-failure' else 2)
            self.assertEqual(caught.exception.code, 'fixture_init_failed' if scenario == 'initialized-fixture-failure' else
                             'execution_cleanup_unresolved' if scenario.endswith('-ack') else 'invalid_owner_handoff')
            if scenario.endswith('-ack'):
                self.assertEqual(guards[0].phase, 11 if scenario == 'initialized-probe-ack' else 9)
            return
        if scenario in ('initialized-wrapper-mutation', 'initialized-listener-mutation', 'initialized-deadline', 'initialized-interrupt'):
            guard = guards[0]
            self.assertEqual(created, ['a'*64, 'c'*64])
            self.assertEqual(len(pids), 4)
            self.assertEqual(len(group_signals), 2)
            self.assertEqual(len(calls), 1)
            self.assertFalse(guard.persistence_verified)
            self.assertEqual(engine.executed_sql_modes, ['write', 'schemas'])
            if scenario.endswith('mutation'):
                self.assertTrue(guard.ownership_lost)
                self.assertEqual(len(engine.events), fault_at[0][0])
                self.assertIsNotNone(engine.row)
                self.assertIsNotNone(engine.volume)
            else:
                if scenario == 'initialized-deadline':
                    self.assertEqual(caught.exception.code, 'docker_timeout')
                self.assertTrue(guard.cleaned)
                self.assertIsNone(engine.row)
                self.assertIsNone(engine.volume)
                self.assertEqual(calls[0]['execution_deadline'], fault_at[0][1])
                self.assertEqual(calls[0]['deadline'], guard.deadline)
                self.assertAlmostEqual(calls[0]['deadline'] - calls[0]['at'], 10, delta=.1)
            return
        if scenario in ('initialized-create-lost', 'initialized-create-malformed'):
            guard = guards[0]
            self.assertEqual(caught.exception.code, 'docker_response_invalid')
            self.assertEqual(created, ['a'*64, 'c'*64])
            self.assertEqual(len(injected), 1)
            self.assertEqual(len(calls), 0)
            self.assertTrue(guard.session.closed)
            self.assertEqual(guard.phase, -1)
            self.assertIsNone(guard.container_id)
            self.assertFalse(guard.persistence_verified)
            self.assertFalse(guard.cleaned)
            self.assertEqual(engine.row['Id'], 'c'*64)
            self.assertIsNotNone(engine.volume)
            self.assertIsNotNone(engine.network)
            self.assertEqual(engine.executed_sql_modes, ['write', 'schemas'])
            mutations = [(m, p) for m, p, _ in engine.events if m != 'GET']
            self.assertIn('/containers/create?', mutations[-1][1])
            self.assertEqual(sum('/containers/create?' in p for _, p in mutations), 2)
            deletes = [p for m, p in mutations if m == 'DELETE']
            self.assertEqual(deletes, ['/v1.48/containers/' + 'a'*64 + '?force=false'])
            self.assertEqual(len(pids), 4)
            self.assertEqual(len(group_signals), 2)
            return
        if persistence:
            self.assertEqual(created, ['a'*64, 'c'*64])
            self.assertEqual(len(guards), 2 if initialized else 1)
            if initialized:
                self.assertIs(guards[0], guards[1])
                self.assertEqual(len(fixture_workdirs), 2)
                self.assertNotEqual(fixture_workdirs[0], fixture_workdirs[1])
                self.assertEqual(guards[0]._fixture[0], fixture_workdirs[0])
                self.assertEqual(guards[0]._second_fixture[0], fixture_workdirs[1])
            self.assertEqual(len(calls), 1)
            self.assertEqual(len(connections), 1)
            self.assertEqual(errors, [])
            self.assertEqual(len(pids), 4 if initialized else 2)
            self.assert_stopped(pids)
            if scenario.startswith(('initialized-copy-', 'initialized-start-')):
                self.assertEqual(caught.exception.code, 'execution_cleanup_unresolved')
                self.assertEqual(len(injected), 1)
                self.assertTrue(calls[0]['closed'])
                self.assertFalse(guards[0].cleaned)
                self.assertFalse(guards[0].persistence_verified)
                self.assertIsNotNone(engine.row)
                self.assertIsNotNone(engine.volume)
                self.assertIsNotNone(engine.network)
                self.assertEqual(engine.executed_sql_modes, ['write', 'schemas'])
                deletes = [p for m, p, _ in engine.events if m == 'DELETE' and '/containers/' in p]
                self.assertEqual(deletes, ['/v1.48/containers/' + 'a'*64 + '?force=false'])
                return
            self.assertTrue(guards[0].cleaned)
            self.assertIsNone(engine.row)
            self.assertIsNone(engine.volume)
            self.assertIsNone(engine.network)
            self.assertEqual(sum('/archive?' in p for _, p, _ in engine.events), 2)
            if scenario in ('persistence-positive', 'initialized-positive'):
                self.assertTrue(result['persisted_run_marker_verified'])
                self.assertTrue(result['owner_recreation_verified'])
                if initialized:
                    self.assertEqual(result['cli_start_count'], 2)
                    self.assertEqual(result['cli_start_boundaries'], ['fresh', 'initialized'])
                    self.assertTrue(result['initialized_cli_recreation_verified'])
                    self.assertNotIn('cli_first_start_only', result)
                else:
                    self.assertEqual(result['owner_start_count'], 2)
                    self.assertTrue(result['cli_first_start_only'])
                self.assertNotIn('first_start_only', result)
                self.assertFalse(result['runtime_ready'])
                self.assertEqual(engine.sql_modes, ['write', 'schemas', 'verify', 'schemas'])
            else:
                self.assertEqual(caught.exception.code, 'execution_sql_failed')
                self.assertEqual(engine.executed_sql_modes, ['write', 'schemas', 'verify'])
                self.assertEqual(engine.sql_modes, ['write', 'schemas', 'verify'])
                self.assertFalse(guards[0].persistence_verified)
            return

        diagnostic = {'scenario': scenario, 'code': caught.exception.code,
                      'phase': guards[0].phase if guards else None,
                      'events': [(m, p) for m, p, _ in engine.events]}
        self.assertEqual(created, ['a'*64], diagnostic)
        self.assertEqual(len(reached), 1, diagnostic)
        self.assertEqual(caught.exception.code,
                         'execution_invalid_health' if scenario == 'post-start-health' else 'execution_cleanup_unresolved',
                         diagnostic)
        self.assertEqual(len(guards), 1, diagnostic)
        self.assertEqual(len(calls), 1, 'automatic owner cleanup was not invoked exactly once; '+str(diagnostic))
        guard = guards[0]
        self.assertTrue(guard.cleanup_attempted)
        self.assertAlmostEqual(calls[0]['deadline'] - calls[0]['at'], 10, delta=.1)
        self.assertLess(calls[0]['duration'], 10.1)
        self.assertEqual(len(connections), 1)
        self.assertEqual(errors, [])
        self.assertEqual(len(pids), 2)
        self.assert_stopped(pids)
        self.assertEqual(sum('/archive?' in p for _, p, _ in engine.events), 1)
        self.assertEqual(sum(p.endswith('/start') for _, p, _ in engine.events), 0 if scenario.startswith('copy-') else 1)
        deletes = [(m, p) for m, p, _ in engine.events if m == 'DELETE']
        if scenario == 'post-start-health':
            self.assertEqual(caught.exception.code, 'execution_invalid_health')
            self.assertTrue(guard.cleaned)
            self.assertFalse(calls[0]['closed'])
            self.assertEqual(len(deletes), 3)
            self.assertTrue(deletes[0][1].endswith('?force=true'))
            self.assertIsNone(engine.row)
            self.assertIsNone(engine.volume)
            self.assertIsNone(engine.network)
        else:
            self.assertEqual(caught.exception.code, 'execution_cleanup_unresolved')
            self.assertEqual(len(injected), 1)
            # Existing finally cleanup remains authoritative; retain the original
            # exchange observation through its implicit exception context.
            import dev
            record = dev.refusal_result(caught.exception)
            self.assertEqual((record['stage'], record['code']),
                             (caught.exception.stage, 'execution_cleanup_unresolved'))
            observation = record['docker_failure']
            self.assertEqual(observation['operation'], 'container_archive' if scenario.startswith('copy-') else 'container_start')
            self.assertEqual(observation['phase'], 'receive')
            self.assertEqual(set(observation), {'schema_version', 'operation', 'phase', 'elapsed_ms'})
            self.assertTrue(calls[0]['closed'])
            self.assertFalse(guard.cleaned)
            self.assertEqual(deletes, [])
            self.assertIsNotNone(engine.row)
            self.assertIsNotNone(engine.volume)
            self.assertIsNotNone(engine.network)

    def test_initialized_second_custody_mutation_latches_before_any_further_mutation(self):
        for scenario in ['initialized-wrapper-mutation', 'initialized-listener-mutation']:
            with self.subTest(scenario=scenario):
                self.run_execution_case(scenario)

    def test_initialized_nested_deadline_and_interrupt_terminate_both_groups(self):
        for scenario in ['initialized-deadline', 'initialized-interrupt']:
            with self.subTest(scenario=scenario):
                self.run_execution_case(scenario)

    def test_initialized_private_probe_ensure_envelopes_refuse(self):
        for scenario in ['initialized-probe-envelope', 'initialized-ensure-envelope', 'initialized-probe-ack', 'initialized-ensure-ack']:
            with self.subTest(scenario=scenario):
                self.run_execution_case(scenario)

    def test_initialized_unknown_second_create_is_never_adopted(self):
        for scenario in ['initialized-create-lost', 'initialized-create-malformed']:
            with self.subTest(scenario=scenario):
                self.run_execution_case(scenario)

    def test_initialized_failure_before_secondary_launch_preserves_volume(self):
        self.run_execution_case('initialized-fixture-failure')

    def test_initialized_secondary_supervisor_uncertain_copy_start_preserves_without_replay(self):
        for scenario in ['initialized-copy-lost', 'initialized-copy-malformed',
                         'initialized-start-lost', 'initialized-start-malformed']:
            with self.subTest(scenario=scenario):
                self.run_execution_case(scenario)

    def test_initialized_cli_recreation_keeps_both_groups_and_private_custodies(self):
        self.run_execution_case('initialized-positive')

    def test_initialized_cli_lost_marker_never_claims_persistence(self):
        self.run_execution_case('initialized-sql-failure')

    def test_persistence_recreation_keeps_one_peer_and_terminates_cli_descendants(self):
        self.run_execution_case('persistence-positive')

    def test_persistence_lost_marker_fails_without_repair_and_cleans_once(self):
        self.run_execution_case('persistence-sql-failure')

    def test_execution_post_start_failure_automatically_cleans_once_and_terminates_descendants(self):
        self.run_execution_case('post-start-health')

    def test_execution_uncertain_archive_start_preserves_closed_peer_without_replay(self):
        for scenario in ['copy-lost', 'copy-malformed', 'start-lost', 'start-malformed']:
            with self.subTest(scenario=scenario):
                self.run_execution_case(scenario)

    def test_execution_missing_supervisor_finally_cleanup_is_detected(self):
        import inspect
        import startup
        source = inspect.getsource(startup.guarded_fixture_command)
        self.assertEqual(source.count('                guard.cleanup_execution()'), 1)
        namespace = {}
        exec(compile(source.replace('                guard.cleanup_execution()', '                pass'),
                     '<supervisor-cleanup-removal-mutation>', 'exec'), startup.__dict__, namespace)
        with self.assertRaisesRegex(AssertionError, 'automatic owner cleanup was not invoked exactly once'):
            self.run_execution_case('post-start-health', runner=namespace['guarded_fixture_command'])

    def test_auth_poststart_real_private_handoff_and_refused_job_dispose(self):
        self.run_execution_case('auth-positive')

    def test_auth_poststart_repeated_not_ready_polls_preserve_execution_deadline(self):
        self.run_execution_case('auth-polling')

    def test_auth_poststart_malformed_or_lost_health_and_job_exchanges_refuse(self):
        for scenario in ['auth-health-envelope', 'auth-health-ack', 'auth-health-lost', 'auth-job-envelope', 'auth-job-lost']:
            with self.subTest(scenario=scenario):
                self.run_execution_case(scenario)

    def test_auth_poststart_instance_custody_deadline_and_interrupt_preserve_limits(self):
        for scenario in ['auth-instance', 'auth-custody', 'auth-deadline', 'auth-interrupt']:
            with self.subTest(scenario=scenario):
                self.run_execution_case(scenario)


    def test_auth_migration_cli_terminated_before_dispatch_and_owned_disposal(self):
        self.run_execution_case('auth-migration-positive')

    def test_auth_migration_failures_keep_deadline_and_clean_job_before_pg(self):
        for scenario in ['auth-migration-nonzero', 'auth-migration-deadline', 'auth-migration-response-deadline', 'auth-migration-interrupt']:
            with self.subTest(scenario=scenario):
                self.run_execution_case(scenario)

    def test_auth_migration_process_oracle_detects_skipped_cli_termination(self):
        import inspect
        import startup
        source = inspect.getsource(startup.guarded_fixture_command)
        original = "                                    os.killpg(process.pid, signal.SIGKILL)\n                                    process.wait(timeout=min(2, guard.remaining()))\n                                    group_terminated = True\n"
        self.assertIn(original, source)
        namespace = {}
        exec(compile(source.replace(original, ''), '<auth-job-skipped-cli-termination>', 'exec'), startup.__dict__, namespace)
        with self.assertRaisesRegex(AssertionError, 'spawned process remains running'):
            self.run_execution_case('auth-migration-positive', runner=namespace['guarded_fixture_command'])


    def test_auth_catalog_process_order_and_same_pg_disposal(self):
        self.run_execution_case('auth-catalog-positive')

    def test_auth_catalog_process_predicate_failures_do_not_qualify(self):
        for scenario in ['auth-catalog-pre-failure', 'auth-catalog-post-failure']:
            with self.subTest(scenario=scenario):
                self.run_execution_case(scenario)

    def test_default_privileges_request_process_failures_cannot_return_success(self):
        for scenario in ('auth-catalog-request-admitted', 'auth-catalog-request-wrong-refusal'):
            with self.subTest(scenario=scenario):
                self.run_execution_case(scenario)

    def test_auth_catalog_process_oracle_detects_skipped_cli_termination(self):
        import inspect
        import startup
        namespace = {}
        source = inspect.getsource(startup.guarded_fixture_command)
        original = "                                    os.killpg(process.pid, signal.SIGKILL)\n                                    process.wait(timeout=min(2, guard.remaining()))\n                                    group_terminated = True\n"
        self.assertIn(original, source)
        exec(compile(source.replace(original, ''), '<catalog-skipped-cli-termination>', 'exec'), startup.__dict__, namespace)
        with self.assertRaisesRegex(AssertionError, 'spawned process remains running'):
            self.run_execution_case('auth-catalog-positive', runner=namespace['guarded_fixture_command'])


    def test_cli_db_backend_process_order_and_same_pg_disposal(self):
        self.run_execution_case('auth-backend-positive')

    def test_cli_db_backend_wrapper_alarm_stops_cli_without_continuation(self):
        self.run_execution_case('auth-backend-wrapper-alarm')

    def test_cli_db_backend_process_predicate_failures_block_job(self):
        for scenario in ['auth-backend-present-failure', 'auth-backend-departed-failure']:
            with self.subTest(scenario=scenario):
                self.run_execution_case(scenario)

    def test_cli_db_backend_process_oracle_detects_skipped_cli_termination(self):
        import inspect
        import startup
        namespace = {}
        source = inspect.getsource(startup.guarded_fixture_command)
        original = "                                    os.killpg(process.pid, signal.SIGKILL)\n                                    process.wait(timeout=min(2, guard.remaining()))\n                                    group_terminated = True\n"
        self.assertIn(original, source)
        exec(compile(source.replace(original, ''), '<backend-skipped-cli-termination>', 'exec'), startup.__dict__, namespace)
        with self.assertRaisesRegex(AssertionError, 'spawned process remains running'):
            self.run_execution_case('auth-backend-positive', runner=namespace['guarded_fixture_command'])

    def test_api_default_privileges_process_order_and_verified_cleanup(self):
        self.run_execution_case('auth-api-positive')

    def test_api_default_privileges_process_nonzero_and_identity_failures_never_qualify(self):
        for scenario in ('auth-api-apply-nonzero', 'auth-api-verify-nonzero', 'auth-api-verify-identity'):
            with self.subTest(scenario=scenario):
                self.run_execution_case(scenario)

    def test_api_default_privileges_process_lost_response_deadline_and_custody_block_success(self):
        for scenario in ('auth-api-apply-lost', 'auth-api-apply-deadline', 'auth-api-verify-custody'):
            with self.subTest(scenario=scenario):
                self.run_execution_case(scenario)
