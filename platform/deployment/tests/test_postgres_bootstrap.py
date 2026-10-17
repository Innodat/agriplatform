"""Acceptance for isolated selected-image SQL/key qualification; no socket access."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import startup_lifecycle as lifecycle


class BehavioralAcceptance(unittest.TestCase):
    def test_missing_image_is_refused_before_any_container_mutation(self):
        calls = []
        def command(argv, **kwargs):
            calls.append(argv)
            return b"[]"
        with self.assertRaises(dev.Refusal):
            lifecycle.run_bootstrap("public.ecr.aws/supabase/postgres@sha256:" + "a" * 64,
                                    "sha256:" + "b" * 64, "d998c960-c37e-4ef6-807a-9fc6fe6a4f3b", command)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][:2], ["image", "inspect"])

import dev


class BootstrapAcceptance(unittest.TestCase):
    def test_real_bootstrap_is_an_explicit_control_and_never_runtime_ready(self):
        import qualify_startup
        self.assertIn('postgres-bootstrap', qualify_startup.BOOTSTRAP_CONTROLS)
        self.assertEqual(lifecycle.bootstrap_success(), {
            'ok': True, 'stage': 'postgres_bootstrap', 'code': 'qualified',
            'initialized': True, 'runtime_ready': False, 'cleanup_verified': True,
            'shutdown_verified': True, 'forced_shutdown': False,
            'role_passwords_verified': True, 'jwt_settings_verified': True,
            'migration_markers_verified': True, 'internal_schemas_verified': True,
            'root_key_verified': True})
        self.assertNotIn(lifecycle.ROOT_KEY.decode(), json.dumps(lifecycle.bootstrap_success()))


IMAGE = 'public.ecr.aws/supabase/postgres@sha256:' + 'a' * 64
CONFIG = 'sha256:' + 'b' * 64
RUN = 'd998c960-c37e-4ef6-807a-9fc6fe6a4f3b'
ID = 'c' * 64


class DockerDouble:
    def __init__(self, fault=None):
        self.calls = []
        self.fault = fault
        self.created = False
        self.removed = False
        self.started = False
        self.stopped = False

    def __call__(self, argv, **kwargs):
        import hashlib
        self.calls.append(argv)
        assert kwargs['timeout'] <= 10 and kwargs['limit'] == 65536
        if argv[:2] == ['image', 'inspect']:
            return json.dumps([dict(Id=CONFIG, Os='linux', Architecture='amd64', RepoDigests=[IMAGE], Config=dict(Labels={'public.image.label': 'retained'}, Volumes={'/var/lib/postgresql/data': {}}))]).encode()
        if argv[:2] == ['container', 'ls']:
            return b'foreign' if (self.fault == 'collision' and not self.created) or (self.fault == 'still-listed' and self.removed) else b''
        if argv[0] == 'create':
            self.created = True
            if self.fault == 'lost-create':
                dev.refuse('images_cli', 'command_deadline')
            self.create = argv
            return ID.encode() + b'\n'
        if argv[:2] == ['container', 'inspect']:
            return json.dumps([dict(Id=ID, Name='/env-pg-bootstrap-' + RUN,
                Image=CONFIG if self.fault != 'replacement' else 'sha256:' + 'd' * 64,
                Config=dict(Image=IMAGE, Labels={'public.image.label': 'retained', 'io.agriplatform.env.run': RUN, 'io.agriplatform.env.proof': 'postgres-bootstrap'}),
                HostConfig=dict(NetworkMode='none', Binds=None, PortBindings={},
                                Tmpfs={'/var/lib/postgresql/data': 'rw,noexec,nosuid,size=1073741824'}, Privileged=False,
                                Memory=2147483648, MemorySwap=2147483648, NanoCpus=2000000000,
                                PidsLimit=256, LogConfig={'Type': 'none', 'Config': {}}),
                Mounts=[], NetworkSettings=dict(Networks={'none': {}}), State=dict(Status='exited' if self.stopped else 'running',
                    Running=not self.stopped, Dead=False, OOMKilled=False, Error='',
                    Pid=0 if self.stopped else 42, ExitCode=0,
                    StartedAt='2026-10-17T10:00:00.123456789Z',
                    FinishedAt='2026-10-17T10:00:01.123456790Z' if self.stopped else '0001-01-01T00:00:00Z'))]).encode()
        if argv[0] == 'cp':
            lifecycle.validate_archive(kwargs['input_data'])
            return b''
        if argv[0] == 'stop':
            self.stopped = True
            return ID.encode()
        if argv[0] == 'start':
            self.started = True
            return ID.encode()
        if argv[0] == 'rm':
            if self.fault == 'cleanup':
                dev.refuse('images_cli', 'command_refused')
            self.removed = True
            return ID.encode()
        if 'pg_isready' in argv:
            return b'accepting connections'
        if 'sha256sum' in argv:
            return b'wrong-policy' if self.fault == 'auth-policy' else b'a925911753f4975548eb4079177441c886aa22b6dd69f2b0cff98f779fb0b66a  /etc/postgresql/pg_hba.conf\n'
        if 'stat' in argv:
            return b'tmpfs\n'
        if 'PGPASSWORD=deliberately-wrong-public-password' in argv:
            if self.fault == 'auth-policy-execution':
                dev.refuse('images_cli', 'command_refused')
            return b'1\n'
        if 'psql' in argv:
            query = argv[-1]
            if query.startswith('SELECT json_object_agg'):
                return json.dumps({role: 'md5' + hashlib.md5(('postgres' + role).encode()).hexdigest()
                                   for role in lifecycle.ROLES}).encode() if self.fault != 'password' else b'{}'
            if query == 'SHOW data_directory':
                return b'/foreign/data' if self.fault == 'data-directory' else b'/var/lib/postgresql/data'
            if ((self.fault == 'jwt' and 'current_setting' in query)
                    or (self.fault == 'markers' and 'array_agg(version' in query)
                    or (self.fault == 'schemas' and 'pg_namespace' in query)):
                return b'f\n'
            if self.fault == 'sql':
                dev.refuse('images_cli', 'command_output_too_large')
            return b'1\n' if query == 'SELECT 1' else b't\n'
        if argv[:1] == ['exec']:
            return b'wrong-sensitive-key' if self.fault == 'key' else b'verified'
        raise AssertionError(argv)


class Matrix(unittest.TestCase):
    def test_success_stops_and_observes_clean_exit_before_removal(self):
        daemon = DockerDouble()
        result = lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, daemon)
        stop_index = next(i for i, call in enumerate(daemon.calls) if call[0] == 'stop')
        remove_index = next(i for i, call in enumerate(daemon.calls) if call[0] == 'rm')
        self.assertEqual(daemon.calls[stop_index], ['stop', '--timeout', '5', ID])
        self.assertTrue(any(call[:2] == ['container', 'inspect']
                            for call in daemon.calls[stop_index + 1:remove_index]))
        self.assertEqual(daemon.calls[remove_index], ['rm', ID])
        self.assertTrue(result['shutdown_verified'])
        self.assertFalse(result['forced_shutdown'])
        self.assertFalse(result['runtime_ready'])

    def test_success_requires_sql_key_and_cleanup_and_closed_create(self):
        daemon = DockerDouble()
        result = lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, daemon)
        self.assertTrue(result['initialized'])
        self.assertTrue(daemon.removed)
        self.assertFalse(result['runtime_ready'])
        self.assertFalse(result['loopback_password_required'])
        for option, value in [('--memory', '2147483648'), ('--memory-swap', '2147483648'),
                              ('--cpus', '2'), ('--pids-limit', '256'), ('--log-driver', 'none')]:
            self.assertEqual(daemon.create[daemon.create.index(option) + 1], value)
        self.assertIn('--network', daemon.create)
        self.assertEqual(daemon.create[daemon.create.index('--network') + 1], 'none')
        for forbidden in ['--publish', '-v', '--volume', '--privileged']:
            self.assertNotIn(forbidden, daemon.create)
        self.assertEqual(daemon.create[-1], (dev.ROOT / 'platform/deployment/fixtures/supabase-pg17-bootstrap.txt').read_text())
        self.assertEqual(sum(call[0] == 'cp' for call in daemon.calls), 1)

    def test_collision_and_uncertain_creation_never_adopt_or_delete(self):
        for fault in ['collision', 'lost-create']:
            daemon = DockerDouble(fault)
            with self.subTest(fault=fault), self.assertRaises(dev.Refusal):
                lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, daemon)
            self.assertFalse(any(call[0] in ('rm', 'exec', 'cp', 'start') for call in daemon.calls))

    def test_changed_ownership_refuses_execution_and_deletion(self):
        daemon = DockerDouble('replacement')
        with self.assertRaises(dev.Refusal) as error:
            lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, daemon)
        self.assertEqual(error.exception.code, 'cleanup_unresolved')
        self.assertFalse(any(call[0] in ('rm', 'exec', 'cp', 'start') for call in daemon.calls))

    def test_failed_sql_key_auth_and_cleanup_cannot_report_success(self):
        for fault in ['sql', 'key', 'password', 'auth-policy', 'auth-policy-execution', 'cleanup']:
            daemon = DockerDouble(fault)
            with self.subTest(fault=fault), self.assertRaises(dev.Refusal) as error:
                lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, daemon)
            if fault == 'cleanup':
                self.assertEqual(error.exception.code, 'cleanup_unresolved')
            else:
                self.assertTrue(error.exception.code.startswith('execution_failed_'))
            self.assertEqual(daemon.removed, fault != 'cleanup')
            self.assertNotIn('sensitive', error.exception.code)

    def test_inherited_anonymous_volumes_refuse_before_creation(self):
        original = DockerDouble()
        def command(argv, **kwargs):
            raw = original(argv, **kwargs)
            if argv[:2] == ['image', 'inspect']:
                rows = json.loads(raw)
                rows[0]['Config']['Volumes']['/foreign'] = {}
                return json.dumps(rows).encode()
            return raw
        with self.assertRaises(dev.Refusal) as error:
            lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
        self.assertEqual(error.exception.code, 'unsupported_image_volumes')
        self.assertEqual(len(original.calls), 1)

    def test_attached_foreign_network_refuses_execution_and_cleanup(self):
        original = DockerDouble()
        def command(argv, **kwargs):
            raw = original(argv, **kwargs)
            if argv[:2] == ['container', 'inspect']:
                rows = json.loads(raw)
                rows[0]['NetworkSettings']['Networks']['foreign'] = {}
                return json.dumps(rows).encode()
            return raw
        with self.assertRaises(dev.Refusal) as error:
            lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
        self.assertEqual(error.exception.code, 'cleanup_unresolved')
        self.assertFalse(any(c[0] in ('cp', 'start', 'exec', 'rm') for c in original.calls))

    def test_actual_password_verifier_and_public_archive(self):
        import hashlib
        import base64
        import hmac
        salt = b'public-test-salt'
        salted = hashlib.pbkdf2_hmac('sha256', b'postgres', salt, 4096)
        stored = hashlib.sha256(hmac.digest(salted, b'Client Key', 'sha256')).digest()
        server = hmac.digest(salted, b'Server Key', 'sha256')
        verifier = 'SCRAM-SHA-256$4096:' + base64.b64encode(salt).decode() + '$' + base64.b64encode(stored).decode() + ':' + base64.b64encode(server).decode()
        self.assertTrue(lifecycle.password_matches('postgres', verifier))
        self.assertFalse(lifecycle.password_matches('postgres', verifier.replace('4096', '4097')))
        self.assertTrue(lifecycle.validate_archive(lifecycle.public_archive())['content_verified'])


class ShutdownMatrix(unittest.TestCase):
    def test_final_cleanup_observation_cannot_complete_after_cleanup_deadline(self):
        from unittest.mock import patch
        daemon = DockerDouble()
        now = 0
        def command(argv, **kwargs):
            nonlocal now
            raw = daemon(argv, **kwargs)
            if daemon.removed and argv[:2] == ['container', 'ls']:
                now = 11
            return raw
        with patch.object(lifecycle.time, 'monotonic', side_effect=lambda: now), self.assertRaises(dev.Refusal) as error:
            lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
        self.assertEqual(error.exception.code, 'cleanup_unresolved')
        self.assertTrue(daemon.removed)
        self.assertEqual(sum(c[0] == 'rm' for c in daemon.calls), 1)

    def test_one_shot_malformed_ownership_cannot_be_restored_for_cleanup(self):
        for malformed in [b'{', b'[{"Id":"first","Id":"second"}]', b'[{"Id":NaN}]']:
            daemon = DockerDouble()
            observations = 0
            def command(argv, **kwargs):
                nonlocal observations
                raw = daemon(argv, **kwargs)
                if argv[:2] == ['container', 'inspect']:
                    observations += 1
                    if observations == 1:
                        return malformed
                return raw
            with self.subTest(malformed=malformed), self.assertRaises(dev.Refusal) as error:
                lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
            self.assertEqual(error.exception.code, 'cleanup_unresolved')
            self.assertEqual(observations, 1)
            self.assertFalse(any(c[0] in ('cp', 'start', 'exec', 'stop', 'rm') for c in daemon.calls))

    def test_interruption_in_poststop_observation_or_cleanup_never_succeeds(self):
        for interrupt_observation in [1, 2]:
            daemon = DockerDouble()
            stopped_observations = 0
            def command(argv, **kwargs):
                nonlocal stopped_observations
                raw = daemon(argv, **kwargs)
                if daemon.stopped and argv[:2] == ['container', 'inspect']:
                    stopped_observations += 1
                    if stopped_observations == interrupt_observation:
                        raise KeyboardInterrupt()
                return raw
            with self.subTest(interrupt_observation=interrupt_observation), self.assertRaises(KeyboardInterrupt):
                lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
            self.assertEqual(stopped_observations, 2)
            self.assertEqual(sum(c[0] == 'stop' for c in daemon.calls), 1)
            if interrupt_observation == 1:
                self.assertTrue(daemon.removed)
                self.assertIn(['rm', '--force', ID], daemon.calls)
            else:
                self.assertFalse(daemon.removed)
                self.assertFalse(any(c[0] == 'rm' for c in daemon.calls))

    def test_unclean_or_incomplete_poststop_state_never_qualifies(self):
        changes = [({'OOMKilled': True}, 'shutdown_oom'),
                   ({'ExitCode': 137}, 'shutdown_forced_exit'),
                   ({'ExitCode': 1}, 'shutdown_nonzero_exit'),
                   ({'Running': True}, 'shutdown_still_running'),
                   ({'Status': 'dead', 'Dead': True}, 'shutdown_invalid_state'),
                   ({'Error': 'sensitive-canary'}, 'shutdown_invalid_state'),
                   ({'Pid': 42}, 'shutdown_invalid_state'),
                   ({'Pid': False}, 'shutdown_invalid_state'),
                   ({'ExitCode': False}, 'shutdown_invalid_state'),
                   ({'OOMKilled': 0}, 'shutdown_invalid_state'),
                   ({'Running': 0}, 'shutdown_invalid_state'),
                   ({'Dead': 0}, 'shutdown_invalid_state'),
                   ({'Status': 'created'}, 'shutdown_invalid_state'),
                   ({'StartedAt': '2026-10-17T10:00:00.123456788Z'}, 'shutdown_invalid_state'),
                   ({'FinishedAt': '2026-10-17T10:00:00.123456789Z'}, 'shutdown_invalid_state'),
                   ({'FinishedAt': '2026-10-17T10:00:00.123456788Z'}, 'shutdown_invalid_state'),
                   ({'FinishedAt': '0001-01-01T00:00:00Z'}, 'shutdown_invalid_state'),
                   ({'FinishedAt': '2026-02-30T10:00:00Z'}, 'shutdown_invalid_state'),
                   ({'FinishedAt': '2026-10-17T12:00:00+02:00'}, 'shutdown_invalid_state'),
                   ({'FinishedAt': None}, 'shutdown_invalid_state')]
        for change, code in changes:
            daemon = DockerDouble()
            def command(argv, **kwargs):
                raw = daemon(argv, **kwargs)
                if daemon.stopped and argv[:2] == ['container', 'inspect']:
                    rows = json.loads(raw)
                    rows[0]['State'].update(change)
                    return json.dumps(rows).encode()
                return raw
            with self.subTest(change=change), self.assertRaises(dev.Refusal) as error:
                lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
            self.assertEqual(error.exception.code, code)
            self.assertTrue(daemon.removed)
            self.assertIn(['rm', '--force', ID], daemon.calls)
            self.assertNotIn('sensitive', error.exception.code)

    def test_before_stop_requires_verified_running_state(self):
        for change in [{'Status': 'exited'}, {'Pid': 0}, {'Pid': True},
                       {'StartedAt': '0001-01-01T00:00:00Z'}, {'StartedAt': None}]:
            daemon = DockerDouble()
            def command(argv, **kwargs):
                raw = daemon(argv, **kwargs)
                if any(c[0] == 'exec' and 'sh' in c for c in daemon.calls) and argv[:2] == ['container', 'inspect']:
                    rows = json.loads(raw)
                    rows[0]['State'].update(change)
                    return json.dumps(rows).encode()
                return raw
            with self.subTest(change=change), self.assertRaises(dev.Refusal) as error:
                lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
            self.assertEqual(error.exception.code, 'shutdown_invalid_state')
            self.assertFalse(daemon.stopped)
            self.assertTrue(daemon.removed)

    def test_stop_command_failure_or_timeout_cleans_without_claiming_shutdown(self):
        for code in ['command_deadline', 'command_refused', 'command_output_too_large']:
            daemon = DockerDouble()
            def command(argv, **kwargs):
                raw = daemon(argv, **kwargs)
                if argv[0] == 'stop':
                    dev.refuse('images_cli', code)
                return raw
            with self.subTest(code=code), self.assertRaises(dev.Refusal) as error:
                lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
            self.assertEqual(error.exception.code, 'shutdown_failed')
            self.assertIn(['rm', '--force', ID], daemon.calls)

    def test_changed_owner_before_or_after_stop_never_deletes_even_if_restored(self):
        for when in ['before', 'after']:
            for field in ['Id', 'Image', 'Labels', 'Networks', 'Memory']:
                daemon = DockerDouble()
                changed = False
                def command(argv, **kwargs):
                    nonlocal changed
                    raw = daemon(argv, **kwargs)
                    ready = any(c[0] == 'exec' and 'sh' in c for c in daemon.calls)
                    if not changed and ready and (when == 'before' or daemon.stopped) and argv[:2] == ['container', 'inspect']:
                        changed = True
                        rows = json.loads(raw)
                        row = rows[0]
                        if field in ('Id', 'Image'):
                            row[field] = 'foreign'
                        elif field == 'Labels':
                            row['Config']['Labels'] = {}
                        elif field == 'Networks':
                            row['NetworkSettings']['Networks']['foreign'] = {}
                        else:
                            row['HostConfig'][field] = 0
                        return json.dumps(rows).encode()
                    return raw
                with self.subTest(when=when, field=field), self.assertRaises(dev.Refusal) as error:
                    lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
                self.assertEqual(error.exception.code, 'cleanup_unresolved')
                self.assertEqual(daemon.stopped, when == 'after')
                self.assertFalse(daemon.removed)

    def test_shutdown_can_finish_after_initialization_deadline_with_its_own_budget(self):
        from unittest.mock import patch
        daemon = DockerDouble()
        now = 0
        def command(argv, **kwargs):
            nonlocal now
            raw = daemon(argv, **kwargs)
            if argv[0] == 'exec' and 'sh' in argv:
                now = 119
            if argv[0] == 'stop':
                now = 122
            if daemon.stopped and argv[:2] == ['container', 'inspect']:
                now = 123
            return raw
        with patch.object(lifecycle.time, 'monotonic', side_effect=lambda: now):
            result = lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
        self.assertEqual(now, 123)
        self.assertTrue(result['shutdown_verified'])
        self.assertFalse(result['forced_shutdown'])
        self.assertFalse(result['runtime_ready'])
        self.assertTrue(daemon.removed)
        self.assertIn(['stop', '--timeout', '5', ID], daemon.calls)
        self.assertIn(['rm', ID], daemon.calls)
        self.assertNotIn(['rm', '--force', ID], daemon.calls)

    def test_shutdown_has_separate_total_budget_and_cleanup_is_independent(self):
        from unittest.mock import patch
        for expire_at in ['before-stop', 'after-stop', 'after-observation']:
            daemon = DockerDouble()
            now = 0
            def command(argv, **kwargs):
                nonlocal now
                raw = daemon(argv, **kwargs)
                if argv[0] == 'exec' and 'sh' in argv:
                    now = 119
                if expire_at == 'before-stop' and argv[:2] == ['container', 'inspect'] and now == 119:
                    now = 135
                if expire_at == 'after-stop' and argv[0] == 'stop':
                    now = 135
                if expire_at == 'after-observation' and daemon.stopped and argv[:2] == ['container', 'inspect']:
                    now = 135
                return raw
            with self.subTest(expire_at=expire_at), patch.object(lifecycle.time, 'monotonic', side_effect=lambda: now), self.assertRaises(dev.Refusal) as error:
                lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
            self.assertEqual(error.exception.code, 'shutdown_deadline')
            self.assertTrue(daemon.removed)
            self.assertIn(['rm', '--force', ID], daemon.calls)

    def test_restart_after_key_cannot_qualify_a_different_started_instance(self):
        daemon = DockerDouble()
        def command(argv, **kwargs):
            raw = daemon(argv, **kwargs)
            if any(c[0] == 'exec' and 'sh' in c for c in daemon.calls) and argv[:2] == ['container', 'inspect']:
                rows = json.loads(raw)
                rows[0]['State']['StartedAt'] = '2026-10-17T10:00:00.123456790Z'
                return json.dumps(rows).encode()
            return raw
        with self.assertRaises(dev.Refusal) as error:
            lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
        self.assertEqual(error.exception.code, 'shutdown_instance_changed')
        self.assertFalse(daemon.stopped)
        self.assertIn(['rm', '--force', ID], daemon.calls)

    def test_nanosecond_completion_and_cleanup_state_recheck(self):
        daemon = DockerDouble()
        def command(argv, **kwargs):
            raw = daemon(argv, **kwargs)
            if daemon.stopped and argv[:2] == ['container', 'inspect']:
                rows = json.loads(raw)
                rows[0]['State']['FinishedAt'] = '2026-10-17T10:00:00.123456790Z'
                return json.dumps(rows).encode()
            return raw
        result = lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
        self.assertTrue(result['shutdown_verified'])
        self.assertIn(['rm', ID], daemon.calls)
        daemon = DockerDouble()
        stopped_observations = 0
        def changed_after_proof(argv, **kwargs):
            nonlocal stopped_observations
            raw = daemon(argv, **kwargs)
            if daemon.stopped and argv[:2] == ['container', 'inspect']:
                stopped_observations += 1
                if stopped_observations == 2:
                    rows = json.loads(raw)
                    rows[0]['State']['StartedAt'] = '2026-10-17T10:00:00.123456790Z'
                    return json.dumps(rows).encode()
            return raw
        with self.assertRaises(dev.Refusal) as error:
            lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, changed_after_proof)
        self.assertEqual(error.exception.code, 'cleanup_unresolved')
        self.assertFalse(daemon.removed)

    def test_final_key_overrun_cannot_reset_expired_initialization_budget(self):
        from unittest.mock import patch
        daemon = DockerDouble()
        now = 0
        def command(argv, **kwargs):
            nonlocal now
            raw = daemon(argv, **kwargs)
            if argv[0] == 'exec' and 'sh' in argv:
                now = 121
            return raw
        with patch.object(lifecycle.time, 'monotonic', side_effect=lambda: now), self.assertRaises(dev.Refusal) as error:
            lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
        self.assertEqual(error.exception.code, 'execution_failed_key')
        self.assertFalse(daemon.stopped)
        self.assertIn(['rm', '--force', ID], daemon.calls)

    def test_initialization_failure_or_interruption_never_requests_success_stop(self):
        for fault in ['key', 'sql']:
            daemon = DockerDouble(fault)
            with self.subTest(fault=fault), self.assertRaises(dev.Refusal):
                lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, daemon)
            self.assertFalse(daemon.stopped)
            self.assertIn(['rm', '--force', ID], daemon.calls)
        daemon = DockerDouble()
        def command(argv, **kwargs):
            raw = daemon(argv, **kwargs)
            if argv[0] == 'stop':
                raise KeyboardInterrupt()
            return raw
        with self.assertRaises(KeyboardInterrupt):
            lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
        self.assertIn(['rm', '--force', ID], daemon.calls)


class BoundedInput(unittest.TestCase):
    def test_input_is_streamed_while_output_is_drained(self):
        import images
        import tempfile
        # Input exceeds a pipe buffer. Reading all input before draining output deadlocks.
        code = 'import sys; sys.stdout.buffer.write(b"x"*32768); sys.stdout.flush(); data=sys.stdin.buffer.read(); print(len(data))'
        with tempfile.TemporaryDirectory() as work:
            output = images.bounded_command([sys.executable, '-c', code], work, {'PATH': '/usr/bin:/bin'},
                                            3, 65536, input_data=b'p' * 262144)
        self.assertEqual(output, b'x' * 32768 + b'262144\n')

    def test_stalled_input_and_excess_output_remain_bounded(self):
        import images
        import tempfile
        for code, timeout, limit, expected in [
            ('import time; time.sleep(5)', .1, 1024, 'command_deadline'),
            ('import sys; sys.stdout.buffer.write(b"sensitive"*2000)', 3, 1024, 'command_output_too_large')]:
            with tempfile.TemporaryDirectory() as work, self.subTest(expected=expected), self.assertRaises(dev.Refusal) as error:
                images.bounded_command([sys.executable, '-c', code], work, {'PATH': '/usr/bin:/bin'},
                                       timeout, limit, input_data=b'p' * 262144)
            self.assertEqual(error.exception.code, expected)

    def test_broken_input_refuses_without_raw_child_error(self):
        import images
        import tempfile
        with tempfile.TemporaryDirectory() as work, self.assertRaises(dev.Refusal) as error:
            images.bounded_command([sys.executable, '-c', 'import sys; sys.exit(7)'], work, {'PATH': '/usr/bin:/bin'},
                                   3, 1024, input_data=b'p' * 262144)
        self.assertIn(error.exception.code, ('command_input_refused', 'command_refused'))


class PublicPrerequisites(unittest.TestCase):
    def invoke(self, target, run_id=RUN):
        import contextlib
        import io
        import qualify_startup
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = qualify_startup.main(['--target', str(target), '--run-id', run_id,
                                          '--control', 'postgres-bootstrap'])
        self.assertEqual(code, 2)
        self.assertNotIn('sensitive-canary', output.getvalue())
        result = json.loads(output.getvalue())
        self.assertFalse(result['ok'])
        self.assertFalse(result['runtime_ready'])
        return result

    def test_invalid_uuid_refuses_before_read_or_execution(self):
        from unittest.mock import patch
        import images
        with patch.object(lifecycle, 'run_bootstrap') as run, patch.object(images, 'bounded_command') as command:
            result = self.invoke('/does-not-exist', 'sensitive-canary')
        self.assertEqual(result['code'], 'startup_proof_refused')
        run.assert_not_called()
        command.assert_not_called()

    def test_invalid_target_json_refuses_before_execution(self):
        import tempfile
        from unittest.mock import patch
        import images
        with tempfile.TemporaryDirectory() as work:
            target = Path(work) / 'target.json'
            target.write_text('{"sensitive-canary":')
            with patch.object(lifecycle, 'run_bootstrap') as run, patch.object(images, 'bounded_command') as command:
                result = self.invoke(target)
        self.assertIn(result['code'], ('invalid_json', 'startup_proof_refused'))
        run.assert_not_called()
        command.assert_not_called()

    def test_absent_prepared_run_refuses_without_creating_it(self):
        import uuid
        from unittest.mock import patch
        import images
        run_id = str(uuid.uuid4())
        run_path = dev.ROOT / 'platform/deployment/.local/kdg' / run_id
        self.assertFalse(run_path.exists())
        with patch.object(lifecycle, 'run_bootstrap') as run, patch.object(images, 'bounded_command') as command:
            result = self.invoke(dev.ROOT / 'platform/deployment/environments/kdg-local.json', run_id)
        self.assertEqual(result['code'], 'prepared_run_required')
        self.assertFalse(run_path.exists())
        run.assert_not_called()
        command.assert_not_called()

    def test_missing_owner_receipt_refuses_before_docker(self):
        from unittest.mock import patch
        import images
        import startup
        with patch.object(dev, 'validate_prepared'), \
             patch.object(startup, 'existing_images', side_effect=dev.Refusal('startup', 'existing_images_required')), \
             patch.object(lifecycle, 'run_bootstrap') as run, patch.object(images, 'bounded_command') as command:
            result = self.invoke(dev.ROOT / 'platform/deployment/environments/kdg-local.json')
        self.assertEqual(result['code'], 'existing_images_required')
        run.assert_not_called()
        command.assert_not_called()

    def test_postexecution_receipt_or_source_change_prevents_success(self):
        from unittest.mock import patch
        import images
        import startup
        owner = ('public-receipt', {'public.ecr.aws/supabase/postgres:17.11.0.004': IMAGE}, {}, {IMAGE: CONFIG})
        for changed in ['receipt', 'source']:
            with self.subTest(changed=changed), patch.object(dev, 'validate_prepared'), \
                 patch.object(startup, 'existing_images', side_effect=[owner, owner if changed == 'source' else ('changed',)]), \
                 patch.object(dev, 'source_evidence', side_effect=[{'source': 'initial'}, {'source': 'changed'}]), \
                 patch.object(lifecycle, 'run_bootstrap', return_value=lifecycle.bootstrap_success()) as run, \
                 patch.object(images, 'bounded_command') as command, patch('shutil.which', return_value='/usr/bin/docker'):
                result = self.invoke(dev.ROOT / 'platform/deployment/environments/kdg-local.json')
            self.assertEqual(result['code'], 'source_changed')
            self.assertNotIn('initialized', result)
            run.assert_called_once()
            command.assert_not_called()


class FailedInitialization(unittest.TestCase):
    def test_command_deadline_or_stopped_initialization_cleans_owned_container(self):
        for fault in ['deadline', 'stopped']:
            original = DockerDouble()
            def command(argv, **kwargs):
                raw = original(argv, **kwargs)
                if fault == 'deadline' and 'pg_isready' in argv:
                    dev.refuse('images_cli', 'command_deadline')
                if fault == 'stopped' and argv[:2] == ['container', 'inspect'] and any(c[0] == 'start' for c in original.calls):
                    rows = json.loads(raw)
                    rows[0]['State']['Running'] = False
                    return json.dumps(rows).encode()
                return raw
            with self.subTest(fault=fault), self.assertRaises(dev.Refusal) as error:
                lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
            self.assertEqual(error.exception.code, 'execution_failed_bootstrap_wait')
            self.assertTrue(original.removed)
            self.assertEqual(sum(c[0] == 'create' for c in original.calls), 1)
            self.assertEqual(sum(c[0] == 'rm' for c in original.calls), 1)

    def test_expired_total_budget_refuses_before_docker(self):
        from unittest.mock import patch
        original = DockerDouble()
        with patch.object(lifecycle, 'BOOTSTRAP_SECONDS', -1), self.assertRaises(dev.Refusal) as error:
            lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, original)
        self.assertEqual(error.exception.code, 'initialization_deadline')
        self.assertEqual(original.calls, [])


class ReviewFixes(unittest.TestCase):
    def test_configured_directory_and_independent_false_sql_checks_refuse(self):
        for fault, step in [('data-directory', 'storage'), ('jwt', 'jwt'),
                            ('markers', 'markers'), ('schemas', 'schemas')]:
            daemon = DockerDouble(fault)
            with self.subTest(fault=fault), self.assertRaises(dev.Refusal) as error:
                lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, daemon)
            self.assertEqual(error.exception.code, 'execution_failed_' + step)
            self.assertTrue(daemon.removed)
            if fault == 'data-directory':
                self.assertFalse(any('stat' in c for c in daemon.calls))

    def test_successful_remove_followed_by_still_listed_refuses(self):
        daemon = DockerDouble('still-listed')
        with self.assertRaises(dev.Refusal) as error:
            lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, daemon)
        self.assertTrue(daemon.removed)
        self.assertEqual(error.exception.code, 'cleanup_unresolved')
        self.assertEqual(sum(c[0] == 'rm' for c in daemon.calls), 1)

    def test_changed_resource_limits_and_log_driver_refuse_dispatch_and_cleanup(self):
        changes = [('Memory', 0), ('MemorySwap', -1), ('NanoCpus', 0),
                   ('PidsLimit', 0), ('LogConfig', {'Type': 'json-file', 'Config': {}})]
        for field, value in changes:
            daemon = DockerDouble()
            def command(argv, **kwargs):
                raw = daemon(argv, **kwargs)
                if argv[:2] == ['container', 'inspect']:
                    rows = json.loads(raw)
                    rows[0]['HostConfig'][field] = value
                    return json.dumps(rows).encode()
                return raw
            with self.subTest(field=field), self.assertRaises(dev.Refusal) as error:
                lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
            self.assertEqual(error.exception.code, 'cleanup_unresolved')
            self.assertFalse(any(c[0] in ('cp', 'start', 'exec', 'rm') for c in daemon.calls))

    def test_network_attached_during_hba_exec_blocks_next_exec_and_deletion(self):
        daemon = DockerDouble()
        changed = False
        def command(argv, **kwargs):
            nonlocal changed
            raw = daemon(argv, **kwargs)
            if 'sha256sum' in argv:
                changed = True
            if changed and argv[:2] == ['container', 'inspect']:
                rows = json.loads(raw)
                rows[0]['NetworkSettings']['Networks']['foreign'] = {}
                return json.dumps(rows).encode()
            return raw
        with self.assertRaises(dev.Refusal) as error:
            lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
        self.assertEqual(error.exception.code, 'cleanup_unresolved')
        hba_index = next(i for i,c in enumerate(daemon.calls) if 'sha256sum' in c)
        self.assertFalse(any(c[0] in ('exec', 'rm') for c in daemon.calls[hba_index + 1:]))

    def test_budget_expiry_after_creation_uses_independent_cleanup_budget(self):
        from unittest.mock import patch
        daemon = DockerDouble()
        now = 0
        def command(argv, **kwargs):
            nonlocal now
            raw = daemon(argv, **kwargs)
            if argv[0] == 'create':
                now = 121
            return raw
        with patch.object(lifecycle.time, 'monotonic', side_effect=lambda: now), self.assertRaises(dev.Refusal) as error:
            lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
        self.assertEqual(error.exception.code, 'execution_failed_ownership')
        self.assertTrue(daemon.removed)
        self.assertEqual(sum(c[0] == 'rm' and c[-1] == ID for c in daemon.calls), 1)
        self.assertFalse(any(c[0] in ('cp', 'start', 'exec') for c in daemon.calls))

    def test_interrupt_cleans_owned_resource_and_cleanup_refusal_is_explicit(self):
        for point in ['after-create', 'initialization']:
            for cleanup_refused in [False, True]:
                daemon = DockerDouble('cleanup' if cleanup_refused else None)
                interrupted = False
                def command(argv, **kwargs):
                    nonlocal interrupted
                    raw = daemon(argv, **kwargs)
                    if not interrupted and ((point == 'after-create' and argv[:2] == ['container', 'inspect'])
                                            or (point == 'initialization' and 'pg_isready' in argv)):
                        interrupted = True
                        raise KeyboardInterrupt()
                    return raw
                expected = dev.Refusal if cleanup_refused else KeyboardInterrupt
                with self.subTest(point=point, cleanup_refused=cleanup_refused), self.assertRaises(expected) as error:
                    lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
                if cleanup_refused:
                    self.assertEqual(error.exception.code, 'cleanup_unresolved')
                self.assertEqual(daemon.removed, not cleanup_refused)
                self.assertEqual(sum(c[0] == 'rm' and c[-1] == ID for c in daemon.calls), 1)

    def test_malformed_owned_descriptors_report_unresolved_cleanup(self):
        for value in [None, {'Config': None}, {'HostConfig': None}]:
            daemon = DockerDouble()
            def command(argv, **kwargs):
                raw = daemon(argv, **kwargs)
                if argv[:2] == ['container', 'inspect']:
                    if value is None:
                        return b'[null]'
                    rows = json.loads(raw)
                    rows[0].update(value)
                    return json.dumps(rows).encode()
                return raw
            with self.subTest(value=value), self.assertRaises(dev.Refusal) as error:
                lifecycle.run_bootstrap(IMAGE, CONFIG, RUN, command)
            self.assertEqual(error.exception.code, 'cleanup_unresolved')
            self.assertFalse(any(c[0] in ('cp', 'start', 'exec', 'rm') for c in daemon.calls))


if __name__ == '__main__':
    unittest.main()
