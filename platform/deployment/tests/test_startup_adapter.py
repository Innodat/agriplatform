"""Guarded invocation acceptance and hostile synthetic-boundary controls."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'platform/deployment'))
import dev
import startup
from create_profile_fixtures import (expected_request, expected_environment, boundary_fixture,
                                     target_fixture, test_plan, test_observations, RUN, SYNTHETIC_CLI_SOURCE)

class StartupAcceptance(unittest.TestCase):
    def test_missing_preparation_fails_before_execution(self):
        result = subprocess.run([sys.executable, str(ROOT / 'platform/deployment/tests/qualify_startup.py'),
                                 '--target', str(ROOT / 'platform/deployment/environments/kdg-local.json'),
                                 '--run-id', str(uuid.uuid4())],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, '')
        self.assertEqual(json.loads(result.stdout)['code'], 'prepared_run_required')


class InvocationGuards(unittest.TestCase):
    def setUp(self):
        self.target = dev.decode(dev.read(ROOT / 'platform/deployment/environments/kdg-local.json'))
        self.network = startup.fixture_network(self.target, RUN)

    def test_closed_network_contract(self):
        self.assertEqual(startup.validate_network(self.network, self.target, RUN), self.network['Id'])
        cases = [('Name', 'foreign'), ('Id', ''), ('Driver', 'overlay'), ('Scope', 'swarm'),
                 ('Internal', True), ('Containers', {'foreign': {}}), ('Options', {}), ('Labels', {})]
        for key, value in cases:
            changed = copy.deepcopy(self.network)
            changed[key] = value
            with self.subTest(key=key), self.assertRaises(dev.Refusal):
                startup.validate_network(changed, self.target, RUN)
        changed = copy.deepcopy(self.network)
        changed['Labels']['unexpected'] = 'sensitive'
        with self.assertRaises(dev.Refusal):
            startup.validate_network(changed, self.target, RUN)

    def test_private_invocation_ignores_ambient_and_detects_contamination(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            startup.initialize_workdir(work, self.target, RUN)
            with patch.dict(os.environ, {'SUPABASE_DB_PASSWORD': 'sensitive', 'DOCKER_CONTEXT': 'foreign',
                                         'SUPABASE_INTERNAL_IMAGE_REGISTRY': 'foreign'}):
                command, env = startup.invocation(Path('/verified/supabase'), work, self.target, RUN, self.network)
            self.assertEqual(env['PATH'], '/usr/bin:/bin')
            self.assertEqual(env['DOCKER_HOST'], 'unix:///var/run/docker.sock')
            self.assertNotIn('SUPABASE_DB_PASSWORD', env)
            self.assertNotIn('DOCKER_CONTEXT', env)
            self.assertEqual(env['SUPABASE_INTERNAL_IMAGE_REGISTRY'], 'public.ecr.aws')
            self.assertEqual(command[-2:], ['--network-id', self.network['Id']])
            self.assertEqual(env['SUPABASE_EXPERIMENTAL_STACK'], '0')
            (work / '.env').write_text('sensitive')
            with self.assertRaises(dev.Refusal):
                startup.invocation(Path('/verified/supabase'), work, self.target, RUN, self.network)

    def test_missing_image_receipt_never_qualifies_or_installs(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as directory, patch.object(dev, 'ROOT', Path(directory)), \
                patch.object(startup.images, 'qualify') as qualify:
            with self.assertRaises(dev.Refusal):
                startup.existing_images(SimpleNamespace(target='unused', run_id=RUN))
            qualify.assert_not_called()


class EvidenceReceiptGuards(unittest.TestCase):
    def test_snapshot_replacement_during_read_refuses(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            startup.write_private(root / 'receipt.json', b'old')
            original = startup.os.read
            replaced = False
            def replace(fd, count):
                nonlocal replaced
                raw = original(fd, count)
                if not replaced:
                    replaced = True
                    (root / 'receipt.json').rename(root / 'preserved')
                    startup.write_private(root / 'receipt.json', b'new')
                return raw
            with dev.directory(root) as fd, patch.object(startup.os, 'read', side_effect=replace):
                with self.assertRaises(dev.Refusal) as caught:
                    startup.evidence_snapshot(fd)
            self.assertEqual(caught.exception.code, 'image_verification_refused')

    def test_changed_existing_receipt_refuses_without_starting_cli(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / 'platform/deployment/.local/kdg-base-images' / RUN
            run.mkdir(parents=True, mode=0o700)
            receipt = run / 'receipt.json'
            startup.write_private(receipt, b'{"base_identities_ready":true}')
            def changed(_, **kwargs):
                receipt.write_bytes(b'{"base_identities_ready":true,"changed":true}')
                return {'base_identities_ready': True}
            with patch.object(dev, 'ROOT', root), patch.object(startup.images, 'qualify', side_effect=changed), \
                    patch.object(startup, 'synthetic_probe') as probe:
                with self.assertRaises(dev.Refusal) as caught:
                    startup.existing_images(SimpleNamespace(target='unused', run_id=RUN))
                self.assertEqual(caught.exception.code, 'image_verification_refused')
                probe.assert_not_called()

    def test_incomplete_evidence_never_calls_owner(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / 'platform/deployment/.local/kdg-base-images' / RUN
            run.mkdir(parents=True, mode=0o700)
            startup.write_private(run / 'receipt.json', b'{"base_identities_ready":true}')
            startup.write_private(run / '.qualify.lock', b'')
            with patch.object(dev, 'ROOT', root), patch.object(startup.images, 'qualify') as owner:
                with self.assertRaises(dev.Refusal):
                    startup.existing_images(SimpleNamespace(target='unused', run_id=RUN))
                owner.assert_not_called()

    def test_replaced_image_run_cannot_enter_fresh_collection(self):
        import test_images
        owner = test_images.PersistenceGuards(methodName='runTest')
        owner.setUp()
        try:
            owner.qualify()
            original = startup.images.qualify
            def replace(args, *, existing_only=False):
                self.assertTrue(existing_only)
                owner.run.rename(owner.run.with_name('preserved-original'))
                return original(args, existing_only=existing_only)
            with patch.object(startup.images, 'qualify', side_effect=replace), \
                    patch.object(startup.images, 'collect') as collect, \
                    patch.object(startup.images, 'capture_services') as capture:
                with self.assertRaises(dev.Refusal):
                    startup.existing_images(owner.args)
                collect.assert_not_called()
                capture.assert_not_called()
                self.assertFalse(owner.run.exists())
        finally:
            owner.doCleanups()


class BoundaryControls(unittest.TestCase):
    def setUp(self):
        self.target = dev.decode(dev.read(ROOT / 'platform/deployment/environments/kdg-local.json'))
        self.project = dev.project_identity(self.target, RUN)
        self.network = startup.fixture_network(self.target, RUN)
        self.fixture = boundary_fixture()
        self.args = expected_request(self.fixture)
        self.env = expected_environment(self.fixture)

    def test_create_refuses_missing_or_foreign_volume_before_event(self):
        for volume in [None, dict(self.fixture['volume'], Name='foreign')]:
            events = []
            with self.subTest(volume=volume), self.assertRaises(dev.Refusal):
                startup.fixture_command('docker', self.args, dict(self.fixture, volume=volume), events, environment=self.env)
            self.assertEqual(events, [])

    def test_first_create_selects_child_and_preserves_every_other_operand(self):
        plan = test_plan()
        original = self.args.copy()
        transformed = startup.immutable_first_create(self.args, self.fixture, plan, environment=self.env)
        index = self.args.index(self.fixture['postgres_image'])
        self.assertEqual(transformed[index], plan[self.fixture['postgres_image']])
        self.assertEqual(transformed[:index], original[:index])
        self.assertEqual(transformed[index + 1:], original[index + 1:])
        self.assertEqual(self.args, original)
        for change in [dict(list(plan.items())[1:]), {**plan, 'foreign:tag': 'foreign@sha256:' + '1' * 64},
                       {**plan, self.fixture['postgres_image']: 'foreign@sha256:' + '1' * 64}]:
            with self.assertRaises(dev.Refusal):
                startup.immutable_first_create(self.args, self.fixture, change, environment=self.env)

    def test_ambiguous_create_is_rejected_before_selection(self):
        index = self.args.index(self.fixture['postgres_image'])
        variants = [['run', *self.args[1:]], [*self.args[:index], None, *self.args[index + 1:]],
                    self.args[:index] + ['--entrypoint', 'sh'] + self.args[index:],
                    self.args[:index] + ['--label', 'com.supabase.cli.project=' + self.project] + self.args[index:],
                    self.args[:index] + ['--privileged', 'true'] + self.args[index:]]
        for ref in ['public.ecr.aws/supabase/postgres:latest', test_plan()[self.fixture['postgres_image']],
                    'public.ecr.aws/supabase/postgres@sha256:' + '0' * 64]:
            variants.append(self.args[:index] + [ref] + self.args[index + 1:])
        changed = dict(self.fixture, postgres_image=next(tag for tag in test_plan() if 'gotrue' in tag))
        with self.assertRaises(dev.Refusal):
            startup.immutable_first_create(self.args[:index] + [changed['postgres_image']] + self.args[index + 1:],
                                           changed, test_plan(), environment=self.env)
        for args in variants:
            events = []
            with self.assertRaises(dev.Refusal):
                if all(type(arg) is str for arg in args):
                    startup.fixture_command('docker', args, self.fixture, events, environment=self.env)
                else:
                    startup.immutable_first_create(args, self.fixture, test_plan(), environment=self.env)
            self.assertEqual(events, [])

    def test_transformer_cannot_change_other_arguments_or_mutate_original(self):
        original = startup.immutable_first_create
        for inplace in [False, True]:
            args = self.args.copy()
            def corrupt(argv, fixture, plan, *, environment):
                selected = original(argv, fixture, plan, environment=environment)
                selected[selected.index('--health-timeout') + 1] = '999s'
                if inplace:
                    argv[argv.index('--health-timeout') + 1] = '999s'
                return selected
            events = []
            with patch.object(startup, 'immutable_first_create', side_effect=corrupt), self.assertRaises(dev.Refusal):
                startup.fixture_command('docker', args, self.fixture, events, environment=self.env)
            self.assertEqual(events, [])

    def test_create_is_refused_with_only_selected_safe_facts(self):
        events = []
        code, output, error = startup.fixture_command('docker', self.args, self.fixture, events, environment=self.env)
        self.assertEqual(code, 125)
        self.assertTrue(events[0]['facts']['create_refused'])
        self.assertNotIn(self.args[-1], json.dumps(events))
        self.assertEqual(set(events[0]['facts']), {'image', 'name', 'network', 'publish',
                         'database_volume', 'host_bind_mounts', 'create_refused',
                         'complete_create_profile_proven', 'original_image', 'immutable_selection_proven'})
        self.assertNotIn('POSTGRES_PASSWORD', json.dumps(events))
        self.assertFalse(events[0]['facts']['host_bind_mounts'])

    def test_duplicate_volume_is_only_a_closed_nonzero_refusal(self):
        args = ['volume', 'create', '--label', 'com.supabase.cli.project=' + self.project,
                '--label', 'com.docker.compose.project=' + self.project, 'supabase_db_' + self.project]
        events = []
        code, _, error = startup.fixture_command('docker', args, self.fixture, events, environment=self.env)
        self.assertEqual(code, 1)
        self.assertEqual(error, 'volume already exists')
        self.assertEqual(events, [{'kind': 'existing_volume_create_refused'}])
        for index in [3, 5, 6]:
            changed = args.copy()
            changed[index] = 'foreign'
            with self.subTest(index=index), self.assertRaises(dev.Refusal):
                startup.fixture_command('docker', changed, self.fixture, [], environment=self.env)

    def test_nonisolated_parent_cannot_be_signaled(self):
        with self.assertRaises(dev.Refusal):
            startup.parent_identity(self.fixture)

    def test_unsafe_create_variants_refuse(self):
        for old, new in [('55482:5432', '0.0.0.0:55482:5432'),
                         (self.fixture['postgres_image'], 'docker.io/foreign:latest'),
                         ('POSTGRES_PASSWORD', 'POSTGRES_PASSWORD=sensitive'),
                         ('supabase_db_' + self.project + ':/var/lib/postgresql/data', '/repo:/sql'),
                         (self.network['Id'], 'foreign')]:
            args = [new if value == old else value for value in self.args]
            with self.subTest(new=new), self.assertRaises(dev.Refusal):
                startup.fixture_command('docker', args, self.fixture, [], environment=self.env)

    def test_every_unexpected_command_and_fallback_refuse(self):
        for runtime, args in [('podman', ['container', 'inspect', 'anything']), ('docker', ['run', 'x']),
                              ('docker', ['pull', self.fixture['postgres_image']]),
                              ('docker', ['network', 'create', 'x']), ('docker', ['start', 'x']),
                              ('docker', ['create', 'x' * (startup.LIMIT + 1)])]:
            with self.subTest(runtime=runtime, command=args[0]), self.assertRaises(dev.Refusal):
                startup.fixture_command(runtime, args, self.fixture, [], environment=self.env)

    def test_malformed_oversized_and_linked_fixture_input_refuse(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            for raw in [b'{', b'x' * (startup.LIMIT + 1)]:
                path = work / 'input'
                startup.write_private(path, raw)
                with self.assertRaises((ValueError, dev.Refusal)):
                    startup.decode_fixture(path)
                path.unlink()
            (work / 'input').symlink_to('/etc/passwd')
            with self.assertRaises((OSError, dev.Refusal)):
                startup.decode_fixture(work / 'input')

    def test_fixture_malformed_state_is_bounded_safe_failure(self):
        for raw in [b'{', b'{}', b'x' * (startup.LIMIT + 1), b'[]' * 64]:
            with self.subTest(size=len(raw)), tempfile.TemporaryDirectory() as directory:
                work = Path(directory)
                startup.write_private(work / 'fixture.json', json.dumps(self.fixture).encode())
                startup.write_private(work / 'events.json', raw)
                self.assertEqual(startup.fixture_main('docker', ['run', 'x'], work), 125)

    def test_hang_and_output_flood_are_bounded_and_descendants_killed(self):
        import time
        for source, limit, expected in [('import time; time.sleep(60)', 1024, 'command_deadline'),
                                        ('import os; os.write(1,b"x"*65536)', 128, 'command_output_too_large')]:
            with tempfile.TemporaryDirectory() as directory:
                before = time.monotonic()
                with self.assertRaises(dev.Refusal) as caught:
                    startup.images.bounded_command([sys.executable, '-c', source], Path(directory),
                                                   {'PATH': '/nonexistent'}, .2, limit)
                self.assertEqual(caught.exception.code, expected)
                self.assertLess(time.monotonic() - before, 3)

    def test_interruption_cleans_process_group(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(startup.images.selectors.DefaultSelector, 'select', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                startup.images.bounded_command([sys.executable, '-c', 'import time; time.sleep(60)'],
                                               Path(directory), {}, 10, 1024)


class SyntheticProbeAcceptance(unittest.TestCase):
    def test_isolated_process_boundary_records_selected_facts_and_refuses_create(self):
        target = dev.decode(dev.read(ROOT / 'platform/deployment/environments/kdg-local.json'))
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / 'synthetic-cli'
            source = SYNTHETIC_CLI_SOURCE
            executable.write_text('#!' + sys.executable + '\n' + source)
            executable.chmod(0o700)
            with patch.dict(os.environ, {'DOCKER_CONTEXT': 'hostile', 'SUPABASE_DB_PASSWORD': 'sensitive'}):
                result = startup.synthetic_probe(executable, target, RUN, selection_plan=test_plan(), image_observations=test_observations())
            self.assertTrue(result['ok'])
            self.assertFalse(result['runtime_ready'])
            self.assertTrue(result['facts']['create_refused'])
            original = 'public.ecr.aws/supabase/postgres:17.11.0.004'
            self.assertEqual(result['facts']['original_image'], original)
            self.assertEqual(result['facts']['image'], test_plan()[original])
            self.assertTrue(result['facts']['immutable_selection_proven'])
            self.assertNotIn('generated secret SQL', json.dumps(result))
            self.assertNotIn('sensitive', json.dumps(result))

    def test_invalid_mapping_shapes_refuse_before_cli(self):
        plan = test_plan()
        tag, other = list(plan)[:2]
        repository = plan[tag].split('@')[0]
        for value in [repository + '@' + plan[other].split('@')[1], repository + '@sha256:bad', 17]:
            with self.subTest(value=value), patch.object(startup.images, 'bounded_command') as command:
                with self.assertRaises(dev.Refusal) as caught:
                    startup.synthetic_probe(Path('/unused'), target_fixture(), RUN,
                                            selection_plan={**plan, tag: value})
                self.assertEqual(caught.exception.code, 'invalid_selection_plan')
                command.assert_not_called()

    def test_negative_controls_never_start_cli_for_invalid_inputs(self):
        target = dev.decode(dev.read(ROOT / 'platform/deployment/environments/kdg-local.json'))
        for control in ['invalid-network', 'contaminated-workdir', 'invalid-selection-plan']:
            with self.subTest(control=control), patch.object(startup.images, 'bounded_command') as command:
                with self.assertRaises(dev.Refusal) as caught:
                    startup.synthetic_probe(Path('/nonexistent'), target, RUN, control=control, selection_plan=test_plan(), image_observations=test_observations())
                self.assertEqual(caught.exception.code, {'invalid-network': 'network_not_run_owned',
                                 'contaminated-workdir': 'workdir_contaminated',
                                 'invalid-selection-plan': 'invalid_selection_plan'}[control])
                command.assert_not_called()
        with self.assertRaises(dev.Refusal) as caught:
            startup.synthetic_probe(Path('/nonexistent'), target, RUN, control='reject-command', selection_plan=test_plan(), image_observations=test_observations())
        self.assertEqual(caught.exception.code, 'expected_command_rejected')


class ProcessGroupRecovery(unittest.TestCase):
    def test_timeout_leaves_no_running_grandchild(self):
        import time
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            pidfile = work / 'child.pid'
            source = ("import os,time; pid=os.fork(); "
                      "open('child.pid','w').write(str(os.getpid())) if pid==0 else None; time.sleep(60)")
            with self.assertRaises(dev.Refusal):
                startup.images.bounded_command([sys.executable, '-c', source], work, {}, .3, 1024)
            self.assertTrue(pidfile.exists())
            pid = int(pidfile.read_text())
            process = Path('/proc') / str(pid) / 'stat'
            for _ in range(50):
                try:
                    stopped = process.read_text().split()[2] == 'Z'
                except (FileNotFoundError, ProcessLookupError):
                    stopped = True
                if stopped:
                    break
                time.sleep(.01)
            else:
                self.fail('running descendant remains after bounded refusal')


def proof_events(fixture):
    return ([{'kind': 'container_inspect'}]
            + [{'kind': 'image_inspect', 'image_index': index} for index in range(4)]
            + [{'kind': 'volume_inspect'}, {'kind': 'network_inspect'},
               {'kind': 'existing_volume_create_refused'},
               {'kind': 'postgres_create', 'facts': startup.selected_facts(fixture)}])


class WorkdirAndStateHardening(unittest.TestCase):
    def test_root_mode_owner_symlink_and_replacement_refuse(self):
        target = target_fixture()
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            work = parent / 'work'
            work.mkdir(mode=0o700)
            startup.initialize_workdir(work, target, RUN)
            work.chmod(0o777)
            with self.assertRaises(dev.Refusal):
                startup.invocation(Path('/verified'), work, target, RUN, startup.fixture_network(target, RUN))
            work.chmod(0o700)
            with patch.object(startup.os, 'getuid', return_value=os.getuid() + 1), self.assertRaises(dev.Refusal):
                startup.check_workdir(work, target, RUN)
            link = parent / 'link'
            link.symlink_to(work)
            with self.assertRaises((OSError, dev.Refusal)):
                startup.check_workdir(link, target, RUN)
            with self.assertRaises(dev.Refusal):
                with startup.work_anchor(work):
                    work.rename(parent / 'saved')
                    work.mkdir(mode=0o700)

    def test_mutation_during_probe_refuses(self):
        for mutation in ['permissions', 'identity']:
            def mutate(command, work, env, timeout, limit):
                if mutation == 'permissions':
                    work.chmod(0o777)
                else:
                    work.rename(work.with_name(work.name + '-saved'))
                    work.mkdir(mode=0o700)
                    # Restore the held directory before TemporaryDirectory cleanup, after check_root detects replacement.
                    saved.append(work.with_name(work.name + '-saved'))
                raise dev.Refusal('images_cli', 'command_refused')
            saved = []
            with self.subTest(mutation=mutation), patch.object(startup.images, 'bounded_command', side_effect=mutate):
                try:
                    with self.assertRaises(dev.Refusal):
                        startup.synthetic_probe(Path('/unused'), target_fixture(), RUN, selection_plan=test_plan(), image_observations=test_observations())
                finally:
                    import shutil
                    for path in saved:
                        shutil.rmtree(path)

    def test_state_hardlink_fifo_and_permissions_cannot_change_unrelated_bytes(self):
        import time
        for kind in ['hardlink', 'fifo', 'permissions']:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                work = Path(directory)
                unrelated = work / 'unrelated'
                startup.write_private(unrelated, b'[]')
                state = work / 'events.json'
                if kind == 'hardlink':
                    os.link(unrelated, state)
                elif kind == 'fifo':
                    os.mkfifo(state, 0o600)
                else:
                    startup.write_private(state, b'[]')
                    state.chmod(0o666)
                startup.write_private(work / 'fixture.json', b'{}')
                before = time.monotonic()
                self.assertEqual(startup.fixture_main('docker', ['run', 'x'], work), 125)
                self.assertLess(time.monotonic() - before, .2)
                self.assertEqual(unrelated.read_bytes(), b'[]')

    def test_state_lock_is_bounded_and_replacement_refuses_before_write(self):
        import fcntl
        import time
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            startup.write_private(work / 'fixture.json', b'{}')
            startup.write_private(work / 'events.json', b'[]')
            with open(work / 'events.json', 'r+b') as holder:
                fcntl.flock(holder, fcntl.LOCK_EX)
                before = time.monotonic()
                self.assertEqual(startup.fixture_main('docker', ['run', 'x'], work), 125)
                self.assertLess(time.monotonic() - before, 1)
            def replace(*args, **kwargs):
                (work / 'events.json').rename(work / 'saved')
                startup.write_private(work / 'events.json', b'[]')
                return 125, '', ''
            with patch.object(startup, 'fixture_command', side_effect=replace):
                self.assertEqual(startup.fixture_main('docker', ['run', 'x'], work), 125)
            self.assertEqual((work / 'saved').read_bytes(), b'[]')
            self.assertEqual((work / 'events.json').read_bytes(), b'[]')


class ParentHandleHardening(unittest.TestCase):
    def test_pidfd_precedes_observations_and_closes_on_death_or_mismatch(self):
        from types import SimpleNamespace
        from unittest.mock import mock_open
        fixture = {'executable': '/verified-cli', 'workdir': '/private', 'network': {'Id': 'fixture'}}
        expected = ['/verified-cli', 'start', '--agent', 'no', '--workdir', '/private', '--network-id', 'fixture']
        for kind in ['success', 'identity', 'reparented', 'dead', 'disappeared']:
            observations = []
            def opened(parent):
                observations.append('pidfd')
                return 999
            def metadata(path, **kwargs):
                observations.append('metadata')
                if kind == 'disappeared':
                    raise FileNotFoundError
                return SimpleNamespace(st_uid=os.getuid())
            argv = expected if kind != 'identity' else ['wrong']
            parents = [123, 124] if kind == 'reparented' else [123, 123]
            with self.subTest(kind=kind), \
                    patch.object(startup.os, 'getppid', side_effect=parents), \
                    patch.object(startup.os, 'pidfd_open', side_effect=opened), \
                    patch.object(startup.os, 'stat', side_effect=metadata), \
                    patch.object(startup.os, 'getsid', return_value=123), \
                    patch.object(startup.os, 'getpgid', return_value=123), \
                    patch.object(startup.os, 'readlink', return_value='/verified-cli'), \
                    patch('builtins.open', mock_open(read_data=b'\0'.join(a.encode() for a in argv) + b'\0')), \
                    patch.object(startup.signal, 'pidfd_send_signal', side_effect=ProcessLookupError if kind == 'dead' else None) as signal_call, \
                    patch.object(startup.os, 'close') as close:
                if kind == 'success':
                    self.assertEqual(startup.parent_identity(fixture), 999)
                    close.assert_not_called()
                    signal_call.assert_called_once_with(999, 0)
                else:
                    with self.assertRaises((OSError, dev.Refusal)):
                        startup.parent_identity(fixture)
                    close.assert_called_once_with(999)
                self.assertEqual(observations[0], 'pidfd')


class ObservationAndSourceHardening(unittest.TestCase):
    def test_missing_duplicate_and_reordered_prerequisites_refuse(self):
        fixture = {'project': 'safe', 'network': {'Id': 'network'}, 'database_port': 55482,
                   'postgres_image': 'public.ecr.aws/supabase/postgres:17.11.0.004'}
        valid = proof_events(fixture)
        startup.validate_observations(valid, startup.selected_facts(fixture))
        variants = [valid[-1:], valid[1:], valid + [valid[-1]], [valid[0], valid[1], valid[1], *valid[3:]]]
        reordered = valid.copy()
        reordered[5], reordered[6] = reordered[6], reordered[5]
        variants.append(reordered)
        for events in variants:
            with self.subTest(count=len(events)), self.assertRaises(dev.Refusal):
                startup.validate_observations(events, startup.selected_facts(fixture))
        self.assertNotIn('repository_sql_inputs', startup.selected_facts(fixture))

    def test_source_changed_during_probe_refuses_with_only_temporary_sources(self):
        import shutil
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in set(startup.PROOF_SOURCES + dev.SOURCES):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, path)
            target = target_fixture()
            def mutate(command, work, env, timeout, limit):
                (root / 'platform/deployment/dev.py').write_text('temporary mutation')
                raise dev.Refusal('images_cli', 'command_refused')
            with patch.object(dev, 'ROOT', root), patch.object(startup.images, 'bounded_command', side_effect=mutate):
                with self.assertRaises(dev.Refusal) as caught:
                    startup.synthetic_probe(Path('/unused'), target, RUN, selection_plan=test_plan(), image_observations=test_observations())
                self.assertEqual(caught.exception.code, 'proof_source_changed')

    def test_direct_control_requires_exact_rejection_event(self):
        for expected in [True, False]:
            def execute(command, work, env, timeout, limit):
                events = [startup.rejected_event(['run', 'forbidden'], 'unexpected_container_command')] if expected else []
                (work / 'events.json').write_bytes(json.dumps(events).encode())
                raise dev.Refusal('images_cli', 'command_refused')
            with self.subTest(expected=expected), patch.object(startup.images, 'bounded_command', side_effect=execute):
                with self.assertRaises(dev.Refusal) as caught:
                    startup.synthetic_probe(Path('/unused'), target_fixture(), RUN, control='reject-command', selection_plan=test_plan(), image_observations=test_observations())
                self.assertEqual(caught.exception.code, 'expected_command_rejected' if expected else 'boundary_not_proven')

    def test_synthetic_cli_unexpected_command_refuses_without_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / 'unexpected-cli'
            executable.write_text('#!' + sys.executable + '\n' + '''import subprocess,sys
# A started fixture returning nonzero must not trigger runtime fallback.
code = subprocess.run(['docker','run','forbidden'], start_new_session=True).returncode
sys.exit(code)
'''.replace('__PROFILE_TESTS__', repr(str(ROOT / 'platform/deployment/tests'))))
            executable.chmod(0o700)
            observed = []
            original = startup.decode_fixture
            def decode(path):
                value = original(path)
                if path.name == 'events.json':
                    observed.extend(value)
                return value
            with patch.object(startup, 'decode_fixture', side_effect=decode):
                with self.assertRaises(dev.Refusal) as caught:
                    startup.synthetic_probe(executable, target_fixture(), RUN, selection_plan=test_plan(), image_observations=test_observations())
            self.assertEqual(caught.exception.code, 'boundary_not_proven')
            self.assertEqual(observed, [startup.rejected_event(['run', 'forbidden'], 'unexpected_container_command')])


class IntegratedOwnerSelectionAcceptance(unittest.TestCase):
    def test_public_acquired_volume_reaches_cli_and_refusal_stops_startup(self):
        import io
        import shutil
        from contextlib import redirect_stdout
        import test_images
        import qualify_startup
        import qualify_volumes
        owner = test_images.PersistenceGuards(methodName='runTest')
        owner.setUp()
        try:
            for name in startup.PROOF_SOURCES:
                path = owner.root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, path)
            target = dev.decode(dev.read(Path(owner.args.target)))
            expected = qualify_volumes.SyntheticDaemon(target, owner.args.run_id).volume
            expected.pop('Mountpoint')
            expected['CreatedAt'] = '2026-10-14T12:34:56Z'
            original_daemon = qualify_volumes.SyntheticDaemon
            def daemon(*args):
                result = original_daemon(*args)
                result.volume['CreatedAt'] = expected['CreatedAt']
                return result
            source = SYNTHETIC_CLI_SOURCE.replace(
                "    subprocess.run(['docker',*command], start_new_session=True)",
                "    observed = subprocess.run(['docker',*command], start_new_session=True, capture_output=True)\n"
                "    if command[:2] == ['volume','inspect']:\n"
                "        assert json.loads(observed.stdout) == " + repr([expected]) + "\n"
                "    if command[:2] == ['image','inspect']:\n"
                "        assert json.loads(observed.stdout) == [" + repr(test_observations()) + "[" + repr(test_plan()) + "[command[-1]]]]")
            self.assertNotEqual(source, SYNTHETIC_CLI_SOURCE)
            executable = owner.payload / 'supabase/supabase'
            executable.parent.mkdir(mode=0o700)
            executable.write_text('#!' + sys.executable + '\n' + source)
            executable.chmod(0o700)
            owner.tool_receipt.write_bytes(test_images.encoded({'toolchain_ready': True,
                'payload': startup.toolchain.payload_fingerprint(owner.payload)}))
            argv = ['--target', owner.args.target, '--run-id', owner.args.run_id]
            with patch.object(startup.images, 'existing_tools', return_value=(owner.payload,
                              dev.digest(owner.tool_receipt.read_bytes()))):
                owner.qualify()
                output = io.StringIO()
                with patch.object(qualify_volumes, 'SyntheticDaemon', side_effect=daemon), redirect_stdout(output):
                    status = qualify_startup.main(argv)
                self.assertEqual(status, 0, output.getvalue())
                self.assertTrue(json.loads(output.getvalue())['facts']['create_refused'])
                self.assertEqual(json.loads(output.getvalue())['image_observations'], test_observations())
                # Independently remove each forwarding hop. Neither may fall back
                # to fixture-invented IDs while still claiming successful proof.
                for name in ['synthetic_probe', 'install_fixture']:
                    original = getattr(startup, name)
                    def omit(*args, _original=original, **kwargs):
                        kwargs.pop('image_observations', None)
                        return _original(*args, **kwargs)
                    omitted = io.StringIO()
                    with patch.object(startup, name, side_effect=omit), redirect_stdout(omitted):
                        self.assertEqual(qualify_startup.main(argv), 2)
                    self.assertEqual(json.loads(omitted.getvalue())['code'], 'invalid_image_observations')
                with patch.object(qualify_startup.volumes, 'acquire', side_effect=dev.Refusal('volume', 'volume_not_run_owned')), \
                        patch.object(startup, 'qualify') as invoked, redirect_stdout(io.StringIO()):
                    self.assertEqual(qualify_startup.main(argv), 2)
                invoked.assert_not_called()
        finally:
            owner.doCleanups()

    def test_owner_plan_reaches_actual_synthetic_cli_with_retained_child_identity(self):
        import shutil
        import test_images
        owner = test_images.PersistenceGuards(methodName='runTest')
        owner.setUp()
        try:
            for name in startup.PROOF_SOURCES:
                path = owner.root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, path)
            executable = owner.payload / 'supabase/supabase'
            executable.parent.mkdir(mode=0o700)
            executable.write_text('#!' + sys.executable + '\n' + SYNTHETIC_CLI_SOURCE)
            executable.chmod(0o700)
            owner.tool_receipt.write_bytes(test_images.encoded({'toolchain_ready': True,
                'payload': startup.toolchain.payload_fingerprint(owner.payload)}))
            with patch.object(startup.images, 'existing_tools', return_value=(owner.payload,
                              dev.digest(owner.tool_receipt.read_bytes()))):
                owner.qualify()
                child = (owner.run / 'postgres-linux-amd64.json').read_bytes()
                index = (owner.run / 'postgres-index.json').read_bytes()
                expected = 'public.ecr.aws/supabase/postgres@sha256:' + dev.digest(child)
                self.assertNotEqual(dev.digest(child), dev.digest(index))
                self.assertNotEqual('sha256:' + dev.digest(child), json.loads(child)['config']['digest'])
                owner.args._image_observations = test_observations()
                result = startup.qualify(owner.args)
                self.assertEqual(result['facts']['image'], expected)
                self.assertTrue(result['facts']['immutable_selection_proven'])
                self.assertFalse(result['container_executed'])
                # All keys and platform fields remain valid: only owner config
                # provenance distinguishes this descriptor from the real one.
                owner.args._image_observations[expected]['Id'] = 'sha256:' + 'f' * 64
                with patch.object(startup, 'synthetic_probe') as probe, \
                        patch.object(startup.images, 'bounded_command') as process:
                    with self.assertRaises(dev.Refusal) as caught:
                        startup.qualify(owner.args)
                self.assertEqual(caught.exception.code, 'invalid_image_observations')
                probe.assert_not_called()
                process.assert_not_called()
        finally:
            owner.doCleanups()


class FullQualificationMutationHardening(unittest.TestCase):
    def test_unchanged_inputs_succeed_and_mid_probe_mutations_refuse(self):
        import shutil
        import test_images
        for mutation in ['unchanged', 'receipt', 'manifest', 'manifest-identity', 'tool-receipt', 'payload', 'preparation', 'inventory']:
            with self.subTest(mutation=mutation):
                owner = test_images.PersistenceGuards(methodName='runTest')
                owner.setUp()
                try:
                    for name in startup.PROOF_SOURCES:
                        path = owner.root / name
                        path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(ROOT / name, path)
                    owner.qualify()
                    def probe(*args, **kwargs):
                        if mutation == 'receipt':
                            (owner.run / 'receipt.json').write_bytes(b'{}')
                        elif mutation in ['manifest', 'manifest-identity']:
                            path = owner.run / 'postgres-linux-amd64.json'
                            raw = path.read_bytes()
                            if mutation == 'manifest-identity':
                                path.rename(owner.run / 'retained-original')
                                startup.write_private(path, raw)
                                (owner.run / 'retained-original').unlink()
                            else:
                                path.write_bytes(b'{}')
                        elif mutation == 'tool-receipt':
                            owner.tool_receipt.write_bytes(b'{}')
                        elif mutation == 'inventory':
                            prepared = owner.root / 'platform/deployment/.local/kdg' / RUN / 'inventory.json'
                            prepared.write_bytes(b'{}')
                        elif mutation == 'payload':
                            startup.write_private(owner.payload / 'injected', b'mutation')
                        elif mutation == 'preparation':
                            prepared = owner.root / 'platform/deployment/.local/kdg' / RUN / 'supabase/config.toml'
                            prepared.write_bytes(b'mutation')
                        return {'ok': True, 'runtime_ready': False}
                    owner.args._image_observations = test_observations()
                    with patch.object(startup, 'synthetic_probe', side_effect=probe):
                        if mutation == 'unchanged':
                            self.assertTrue(startup.qualify(owner.args)['ok'])
                        else:
                            with self.assertRaises((OSError, ValueError, KeyError, dev.Refusal)):
                                startup.qualify(owner.args)
                finally:
                    owner.doCleanups()


class DetachedFixtureLifetimeHardening(unittest.TestCase):
    def test_separate_session_fixture_dies_after_timeout_and_interruption(self):
        import time
        original_select = startup.images.selectors.DefaultSelector.select
        for interrupted in [False, True]:
            with self.subTest(interrupted=interrupted), tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                work = base / 'work'
                work.mkdir(mode=0o700)
                target = target_fixture()
                startup.initialize_workdir(work, target, RUN)
                executable = base / 'stalled-cli'
                pidfile = base / 'fixture.pid'
                executable.write_text('#!' + sys.executable + '\n' + '''import fcntl,subprocess,sys,time
from pathlib import Path
work = Path(sys.argv[sys.argv.index('--workdir')+1])
lock = open(work/'events.json','r+b')
fcntl.flock(lock,fcntl.LOCK_EX)
p = subprocess.Popen(['docker','container','inspect','supabase_db_''' + dev.project_identity(target, RUN) + "''','--format','{{json .State}}'],start_new_session=True)\n" +
                    'Path(' + repr(str(pidfile)) + ').write_text(str(p.pid))\ntime.sleep(60)\n')
                executable.chmod(0o700)
                command, env = startup.invocation(executable, work, target, RUN, startup.fixture_network(target, RUN))
                startup.install_fixture(work, target, RUN, startup.fixture_network(target, RUN), executable, selection_plan=test_plan(), image_observations=test_observations())
                env['PATH'] = str(work / 'bin')
                def stop(selector, timeout=None):
                    if not pidfile.exists():
                        return original_select(selector, min(timeout or .02, .02))
                    time.sleep(.1)
                    raise KeyboardInterrupt
                context = patch.object(startup.images.selectors.DefaultSelector, 'select', side_effect=stop, autospec=True)
                if interrupted:
                    with context, self.assertRaises(KeyboardInterrupt):
                        startup.images.bounded_command(command, work, env, 2, 1024)
                else:
                    with self.assertRaises(dev.Refusal):
                        startup.images.bounded_command(command, work, env, .3, 1024)
                self.assertTrue(pidfile.exists())
                process = Path('/proc') / pidfile.read_text() / 'stat'
                for _ in range(100):
                    try:
                        stopped = process.read_text().split()[2] == 'Z'
                    except (FileNotFoundError, ProcessLookupError):
                        stopped = True
                    if stopped:
                        break
                    time.sleep(.01)
                else:
                    self.fail('live detached fixture after CLI termination')


if __name__ == '__main__':
    unittest.main()
