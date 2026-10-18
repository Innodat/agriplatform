"""No-socket acceptance of the retained owner's closed real dispatch."""
import sys
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import resources
import create_profile
import dev
from create_profile_fixtures import boundary_fixture, expected_request, expected_environment

class PinnedExecution(unittest.TestCase):
    def test_ordered_real_dispatch_records_actual_id_and_consumes_phases(self):
        fixture = boundary_fixture()
        session = Mock()
        guard = resources.FreshGuard({}, fixture['run_id'], session, lambda: None, 99, {}, {}, {}, None)
        guard.phase = 2
        guard.images = fixture['image_observations']
        guard.enable_execution()
        with patch.object(guard, 'joint'), patch.object(guard, 'owned', return_value={}), patch.object(dev, 'free_ports'):
            session.exchange.return_value = (404, None)
            actual = 'a' * 64
            session.exchange.side_effect = [(404, None), (200, {'Id': fixture['image_observations'][fixture['selection_plan'][fixture['postgres_image']]]['Id'], 'Config': {}}), (201, {'Id': actual, 'Warnings': []})]
            self.assertEqual(guard.container_create(expected_request(fixture), fixture, expected_environment(fixture)), actual)
            self.assertEqual(guard.container_id, actual)
            self.assertEqual(guard.phase, 3)
            with self.assertRaises(dev.Refusal):
                guard.container_create(expected_request(fixture), fixture, expected_environment(fixture))
        request = session.exchange.call_args.args
        self.assertEqual(request[0], 'POST')
        host = request[2]['HostConfig']
        self.assertEqual(host['RestartPolicy']['Name'], 'no')
        self.assertEqual((host['Memory'], host['NanoCpus'], host['PidsLimit']), (2147483648, 2000000000, 256))

    def make_guard(self, phase=2):
        fixture = boundary_fixture()
        guard = resources.FreshGuard({}, fixture['run_id'], Mock(), lambda: None, 99, {}, fixture['image_observations'], fixture['network'], None)
        guard.phase = 2
        guard.enable_execution()
        guard.phase = phase
        return guard, fixture

    def test_invalid_original_profile_never_dispatches(self):
        guard, fixture = self.make_guard()
        for defect in ['args', 'env']:
            args, env = expected_request(fixture), expected_environment(fixture)
            if defect == 'args':
                args[-1] += 'modified'
            else:
                env['DOCKER_CONTEXT'] = 'foreign'
            with self.subTest(defect=defect), self.assertRaises(dev.Refusal):
                guard.container_create(args, fixture, env)
            guard.session.exchange.assert_not_called()

    def test_existing_or_uncertain_create_is_consumed_without_adoption_or_replay(self):
        fixture = boundary_fixture()
        image = {'Id': fixture['image_observations'][fixture['selection_plan'][fixture['postgres_image']]]['Id'], 'Config': {}}
        for replies in [[(200, {})], [(500, None)], [(404, None), (200, image), (201, {})],
                        [(404, None), (200, image), (201, {'Id': 'a'*64, 'Warnings': ['unexpected']})]]:
            guard, fixture = self.make_guard()
            guard.session.exchange.side_effect = replies
            with patch.object(guard, 'joint'), patch.object(dev, 'free_ports'), self.assertRaises(dev.Refusal):
                guard.container_create(expected_request(fixture), fixture, expected_environment(fixture))
            self.assertEqual(guard.phase, -1)
            self.assertIsNone(guard.container_id)
            guard.session.exchange.reset_mock()
            with self.assertRaises(dev.Refusal):
                guard.container_create(expected_request(fixture), fixture, expected_environment(fixture))
            guard.session.exchange.assert_not_called()

    def test_copy_start_only_recorded_id_archive_and_exact_phase(self):
        import startup_lifecycle
        for phase, verb in [(2, 'cp'), (3, 'start'), (4, 'cp'), (5, 'start')]:
            guard, fixture = self.make_guard(phase)
            guard.container_id = 'a'*64
            with self.subTest(phase=phase, verb=verb), self.assertRaises(dev.Refusal):
                if verb == 'cp':
                    guard.container_copy(['cp', '-', 'a'*64+':/'], startup_lifecycle.public_archive())
                else:
                    guard.container_start(['start', 'a'*64])
            guard.session.exchange.assert_not_called()
        guard, _ = self.make_guard(3)
        guard.container_id = 'a'*64
        with self.assertRaises(dev.Refusal):
            guard.container_copy(['cp', '-', 'b'*64+':/'], startup_lifecycle.public_archive())
        with self.assertRaises(dev.Refusal):
            guard.container_copy(['cp', '-', 'a'*64+':/'], b'bad')
        guard.session.exchange.assert_not_called()
        with patch.object(guard, 'owned', return_value={'State': {'Status': 'created', 'Running': False}}):
            guard.session.exchange.return_value = (200, None)
            guard.container_copy(['cp', '-', 'a'*64+':/'], startup_lifecycle.public_archive())
            self.assertEqual(guard.phase, 4)
            guard.session.exchange.return_value = (204, None)
            guard.container_start(['start', 'a'*64])
            self.assertEqual(guard.phase, 5)
            with self.assertRaises(dev.Refusal):
                guard.container_start(['start', 'a'*64])

    def test_extra_volume_reference_latches_loss_before_later_cleanup(self):
        guard, fixture = self.make_guard()
        guard.container_id = 'a'*64
        guard.volume = {'Name': 'supabase_db_' + fixture['project']}
        guard.execution_input = {'body': {}}
        guard.session.exchange.return_value = (200, [{'Id': guard.container_id}, {'Id': 'b'*64}])
        with patch.object(guard, 'joint', side_effect=guard.references):
            with self.assertRaises(dev.Refusal):
                guard.owned()
        self.assertTrue(guard.ownership_lost)
        guard.session.exchange.reset_mock()
        with self.assertRaises(dev.Refusal):
            guard.cleanup_execution()
        guard.session.exchange.assert_not_called()

    def test_fixed_transport_and_empty_success_framing_without_socket(self):
        import startup_lifecycle
        ident = 'a'*64
        for method, path, body in [('PUT', '/v1.48/containers/'+ident+'/archive?path=%2F', startup_lifecycle.public_archive()),
                                   ('POST', '/v1.48/containers/'+ident+'/start', None),
                                   ('POST', '/v1.48/containers/'+ident+'/stop?t=5', None),
                                   ('DELETE', '/v1.48/containers/'+ident+'?force=false', None)]:
            raw = dev._docker_request(method, path, body, True)
            self.assertTrue(raw.startswith((method+' '+path+' HTTP/1.1').encode()))
        for path in ['/v1.48/containers/json', '/v1.48/containers/'+ident+'/exec', '/v1.48/containers/'+ident+'/stop?t=6']:
            with self.assertRaises(dev.Refusal):
                dev._docker_request('POST', path, None, True)
        for header in [b'Content-Length: 0\r\n', b'']:
            stream = Mock()
            stream.recv.return_value = b'HTTP/1.1 204 No Content\r\n'+header+b'\r\n'
            self.assertEqual(dev._docker_response(stream, lambda: None, float('inf'), True, '/v1.48/containers/'+ident+'/start'), (204, None))
        stream = Mock()
        stream.recv.return_value = b'HTTP/1.1 204 No Content\r\nContent-Length: 1\r\n\r\nx'
        with self.assertRaises(dev.Refusal):
            dev._docker_response(stream, lambda: None, float('inf'), True, '/v1.48/containers/'+ident+'/start')

    def test_chunked_fixed_route_fragmentation_and_ambiguous_framing(self):
        path = '/v1.48/images/sha256:' + 'a'*64 + '/json'
        raw = b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n1\r\n{\r\n1\r\n}\r\n0\r\n\r\n'
        for pieces in [[raw], [raw[i:i+1] for i in range(len(raw))], [raw[:51], raw[51:]]]:
            stream = Mock()
            stream.recv.side_effect = pieces
            self.assertEqual(dev._docker_response(stream, lambda: None, float('inf'), True, path), (200, {}))
        for body in [b'0\r\nX: y\r\n\r\n', b'0\r\n\r\nextra', b'2;x=y\r\n{}\r\n0\r\n\r\n',
                     b'2\r\n{}xx0\r\n\r\n', b'100000\r\n', b'2\r\n{', b'2\r\n{}\r\n']:
            stream = Mock()
            stream.recv.side_effect = [raw.split(b'\r\n\r\n')[0]+b'\r\n\r\n'+body, b'']
            with self.subTest(body=body), self.assertRaises(dev.Refusal):
                dev._docker_response(stream, lambda: None, float('inf'), True, path)
        for headers in [b'Transfer-Encoding: chunked\r\nContent-Length: 2',
                        b'Transfer-Encoding: gzip, chunked', b'Transfer-Encoding: chunked\r\nTransfer-Encoding: chunked',
                        b'Transfer-Encoding: chunked\r\nContent-Encoding: gzip']:
            stream = Mock()
            stream.recv.return_value = b'HTTP/1.1 200 OK\r\n'+headers+b'\r\n\r\n2\r\n{}\r\n0\r\n\r\n'
            with self.subTest(headers=headers), self.assertRaises(dev.Refusal):
                dev._docker_response(stream, lambda: None, float('inf'), True, path)

class OwnerDaemon:
    """Independent in-memory Docker protocol owner; no socket/process execution."""
    def __init__(self):
        import copy
        import startup
        import networks
        from create_profile_fixtures import target_fixture
        self.copy = copy.deepcopy
        self.target = target_fixture()
        self.fixture = boundary_fixture()
        self.network = {**networks.create_input(self.target, self.fixture['run_id']),
                        'Id': 'b'*64, 'Containers': {}, 'ConfigFrom': {'Network': ''}}
        self.fixture['network'] = {key: self.network[key] for key in startup.fixture_network(self.target, self.fixture['run_id'])}
        self.images = self.fixture['image_observations']
        self.volume = startup.fixture_volume(self.target, self.fixture['run_id'])
        self.row, self.events, self.hook = None, [], None
        self.closed = False
        self.deadline = float('inf')
        self.image = {'Env': ['PATH=/usr/bin:/bin', 'LANG=C'], 'Labels': {'publisher': 'selected'}, 'Volumes': {'/var/lib/postgresql/data': {}}}
        self.guard = resources.FreshGuard(self.target, self.fixture['run_id'], self, self.current, self.deadline,
                {ref: descriptor['Id'] for ref, descriptor in self.images.items()}, self.images,
                self.fixture['network'], None)
        self.guard.volume, self.guard.phase = self.copy(self.volume), 2
        self.guard.network_created = True
        self.guard.enable_execution()

    def current(self):
        import time
        if time.monotonic() >= self.deadline:
            dev.refuse('docker', 'docker_timeout')

    def idle(self):
        pass

    def budget(self):
        self.current()

    def exchange(self, method, path, body=None):
        self.current()
        self.events.append((method, path, self.copy(body)))
        if self.hook:
            self.hook(method, path)
        if '/images/' in path:
            ref = path.split('/images/')[1][:-5]
            descriptor = self.images.get(ref) or next(d for d in self.images.values() if d['Id'] == ref)
            return 200, {**descriptor, 'Config': self.copy(self.image)}
        if path.startswith('/v1.48/networks/'):
            if method == 'DELETE':
                self.network = None
                return 204, None
            return (200, self.copy(self.network)) if self.network else (404, None)
        if path.startswith('/v1.48/volumes/'):
            if method == 'DELETE':
                self.volume = None
                return 204, None
            return (200, self.copy(self.volume)) if self.volume else (404, None)
        if path.startswith('/v1.48/containers/json?'):
            return 200, [{'Id': self.row['Id']}] if self.row else []
        if path.startswith('/v1.48/containers/create?'):
            labels = {**self.image['Labels'], **body['Labels']}
            config = {key: self.copy(body[key]) for key in ['Image', 'Entrypoint', 'Cmd', 'Healthcheck']}
            config.update(Env=self.image['Env'] + body['Env'], Labels=labels)
            self.row = {'Id': 'a'*64, 'Name': '/' + self.volume['Name'],
                    'Image': self.images[body['Image']]['Id'], 'Config': config, 'HostConfig': self.copy(body['HostConfig']),
                    'Mounts': [{'Type': 'volume', 'Name': self.volume['Name'], 'Destination': '/var/lib/postgresql/data', 'RW': True}],
                    'NetworkSettings': {'Networks': {self.network['Name']: {'NetworkID': self.network['Id'], 'Aliases': ['db', 'db.supabase.internal', self.volume['Name'], 'a'*12]}}},
                    'State': {'Status': 'created', 'Running': False}}
            return 201, {'Id': self.row['Id'], 'Warnings': []}
        if path.endswith('/json'):
            return (200, self.copy(self.row)) if self.row else (404, None)
        if '/archive?' in path:
            import startup_lifecycle
            self.assert_archive = startup_lifecycle.validate_archive(body)
            return 200, None
        if path.endswith('/start'):
            self.row['State'] = {'Status': 'running', 'Running': True, 'Pid': 123, 'OOMKilled': False,
                    'Dead': False, 'Error': '', 'StartedAt': '2026-10-17T12:00:00.000000001Z',
                    'Health': {'Status': 'healthy'}}
            self.network['Containers'] = {self.row['Id']: {}}
            return 204, None
        if path.endswith('/stop?t=5'):
            self.row['State'].update(Status='exited', Running=False, Pid=0, ExitCode=0,
                    FinishedAt='2026-10-17T12:00:01.000000001Z')
            self.network['Containers'] = {}
            return 204, None
        if method == 'DELETE' and '/containers/' in path:
            self.row = None
            self.network['Containers'] = {}
            return 204, None
        raise AssertionError((method, path))

    def dispatch_cli(self):
        import startup_lifecycle
        f = self.fixture
        with patch.object(dev, 'free_ports'):
            actual = self.guard.container_create(expected_request(f), f, expected_environment(f))
        self.guard.container_copy(['cp', '-', actual+':/'], startup_lifecycle.public_archive())
        self.guard.container_start(['start', actual])

class FullRetainedOwner(unittest.TestCase):
    def test_named_volume_dispatch_health_strict_shutdown_and_proven_removal(self):
        daemon = OwnerDaemon()
        daemon.dispatch_cli()
        daemon.guard.finish_execution()
        self.assertEqual(daemon.guard.phase, 7)
        self.assertTrue(daemon.guard.cleaned)
        self.assertIsNone(daemon.row)
        self.assertIsNone(daemon.volume)
        self.assertIsNone(daemon.network)
        mutations = [(m, p) for m, p, _ in daemon.events if m != 'GET']
        self.assertEqual([m for m, _ in mutations], ['POST', 'PUT', 'POST', 'POST', 'DELETE', 'DELETE', 'DELETE'])
        self.assertTrue(mutations[0][1].startswith('/v1.48/containers/create?'))
        self.assertTrue(mutations[1][1].endswith('/'+'a'*64+'/archive?path=%2F'))
        self.assertTrue(mutations[3][1].endswith('/stop?t=5'))
        self.assertTrue(mutations[4][1].endswith('?force=false'))

    def test_existing_matching_bridge_is_preserved(self):
        daemon = OwnerDaemon()
        daemon.guard.network_created = False
        daemon.dispatch_cli()
        daemon.guard.finish_execution()
        self.assertIsNotNone(daemon.network)
        self.assertFalse(any(m == 'DELETE' and '/networks/' in p for m, p, _ in daemon.events))

    def test_every_selected_descriptor_drift_latches_deletion_refusal(self):
        mutations = [lambda d: d.row.update(Id='c'*64), lambda d: d.row.update(Name='/foreign'),
                     lambda d: d.row.update(Image='sha256:'+'f'*64),
                     lambda d: d.row['Config'].update(Image='foreign'),
                     lambda d: d.row['Config']['Env'].append('EXTRA=foreign'),
                     lambda d: d.row['Config']['Labels'].update(publisher='foreign'),
                     lambda d: d.row['HostConfig'].update(Memory=1),
                     lambda d: d.row['HostConfig'].update(Privileged=True),
                     lambda d: d.row['HostConfig'].update(CapAdd=['SYS_ADMIN']),
                     lambda d: d.row['Mounts'][0].update(Name='foreign'),
                     lambda d: d.row['NetworkSettings']['Networks'][d.network['Name']].update(NetworkID='c'*64),
                     lambda d: d.network['Containers'].update({'c'*64: {}}),
                     lambda d: d.volume['Labels'].update({'foreign': 'yes'})]
        for mutation in mutations:
            daemon = OwnerDaemon()
            daemon.dispatch_cli()
            original = daemon.copy(daemon.row)
            mutation(daemon)
            with self.subTest(mutation=mutation), self.assertRaises(dev.Refusal):
                daemon.guard.owned()
            self.assertTrue(daemon.guard.ownership_lost)
            daemon.row = original
            before = len(daemon.events)
            with self.assertRaises(dev.Refusal):
                daemon.guard.cleanup_execution()
            self.assertEqual(len(daemon.events), before)

    def test_unclean_state_and_restarted_instance_never_claim_clean_removal(self):
        for change in [dict(ExitCode=137), dict(ExitCode=1), dict(OOMKilled=True),
                       dict(FinishedAt='0001-01-01T00:00:00Z'), dict(StartedAt='2026-10-17T12:00:00.000000002Z')]:
            daemon = OwnerDaemon()
            daemon.dispatch_cli()
            def inject(method, path):
                if path.endswith('/json') and daemon.row['State'].get('Status') == 'exited':
                    daemon.row['State'].update(change)
            daemon.hook = inject
            with self.subTest(change=change), self.assertRaises(dev.Refusal):
                daemon.guard.finish_execution()
            self.assertFalse(daemon.guard.cleaned)
            self.assertFalse(any(m == 'DELETE' for m, _, _ in daemon.events))
            daemon.hook = None
            daemon.guard.cleanup_execution()
            self.assertTrue(any(m == 'DELETE' and p.endswith('force=true') for m, p, _ in daemon.events))

    def test_health_shutdown_and_cleanup_have_distinct_total_deadlines(self):
        for phase in ['health', 'shutdown', 'cleanup']:
            clock = [0.0]
            with patch.object(resources.time, 'monotonic', side_effect=lambda: clock[0]):
                daemon = OwnerDaemon()
                daemon.dispatch_cli()
                if phase == 'health':
                    daemon.row['State']['Health']['Status'] = 'starting'
                def expire(method, path):
                    at = (phase == 'health' and path.endswith('/json') and daemon.row is not None
                          or phase == 'shutdown' and path.endswith('/stop?t=5')
                          or phase == 'cleanup' and method == 'DELETE' and '/containers/' in path)
                    if at:
                        clock[0] = daemon.deadline + 1
                daemon.hook = expire
                with self.subTest(phase=phase), self.assertRaises(dev.Refusal) as caught:
                    daemon.guard.finish_execution()
                self.assertEqual(caught.exception.code, 'docker_timeout')
                self.assertFalse(daemon.guard.cleaned)
                self.assertFalse(daemon.guard.ownership_lost)
                if phase in ['health', 'shutdown']:
                    daemon.hook = None
                    daemon.guard.cleanup_execution()
                    self.assertTrue(daemon.guard.cleaned)
                    self.assertEqual(daemon.deadline, clock[0] + 10)
                    self.assertTrue(any(m == 'DELETE' and p.endswith('force=true') for m, p, _ in daemon.events))

    def test_interruption_retains_owned_cleanup_and_never_qualifies(self):
        daemon = OwnerDaemon()
        daemon.dispatch_cli()
        def interrupt(method, path):
            if path.endswith('/json'):
                raise KeyboardInterrupt()
        daemon.hook = interrupt
        with self.assertRaises(KeyboardInterrupt):
            daemon.guard.finish_execution()
        self.assertFalse(daemon.guard.cleaned)
        self.assertFalse(daemon.guard.ownership_lost)
        daemon.hook = None
        daemon.guard.cleanup_execution()
        self.assertTrue(daemon.guard.cleaned)
        self.assertFalse(any(p.endswith('/stop?t=5') for _, p, _ in daemon.events))

    def test_execution_opt_in_does_not_extend_five_second_volume_acquisition(self):
        import time
        import startup
        from create_profile_fixtures import target_fixture
        clock = [0.0]
        session = Mock()
        session.deadline = 5.0
        def current():
            if time.monotonic() >= session.deadline:
                dev.refuse('docker', 'docker_timeout')
        fixture = boundary_fixture()
        guard = resources.FreshGuard(target_fixture(), fixture['run_id'], session, current, 5.0, {}, {}, {}, None)
        with patch.object(resources.time, 'monotonic', side_effect=lambda: clock[0]), \
                patch.object(resources.volumes, 'require_absent'), patch.object(guard, 'joint'), \
                patch.object(resources.volumes, 'create_fresh_session', return_value={'volume': fixture['volume']}):
            guard.enable_execution()
            self.assertEqual((guard.deadline, session.deadline), (5.0, 5.0))
            guard.probe()
            clock[0] = 4.0
            guard.create()
            self.assertEqual(guard.phase, 2)
            self.assertEqual((guard.deadline, session.deadline), (5.0, 5.0))
            clock[0] = 6.0
            with self.assertRaises(dev.Refusal) as caught:
                guard.container_create(expected_request(fixture), fixture, expected_environment(fixture))
            self.assertEqual(caught.exception.code, 'docker_timeout')
            self.assertFalse(guard.execution_started)
            self.assertEqual((guard.deadline, session.deadline), (5.0, 5.0))
            session.exchange.assert_not_called()

class ExecutionEntry(unittest.TestCase):
    def test_internal_execution_control_reaches_existing_prerequisite_validator(self):
        import startup
        fixture = boundary_fixture()
        class AtPrerequisites(Exception):
            pass
        with patch.object(startup, 'validate_selection_plan', side_effect=AtPrerequisites), self.assertRaises(AtPrerequisites):
            startup.synthetic_probe('/not-executed', {}, fixture['run_id'], control='fresh-pinned-cli-postgres',
                    selection_plan=fixture['selection_plan'], image_observations=fixture['image_observations'],
                    _guarded_target=('/prepared-target', '/private-peer'))

    def test_out_of_band_start_refuses_copy_and_start_before_dispatch(self):
        import startup_lifecycle
        for phase in [3, 4]:
            daemon = OwnerDaemon()
            daemon.dispatch_cli()
            daemon.guard.phase = phase
            before = len(daemon.events)
            with self.subTest(phase=phase), self.assertRaises(dev.Refusal):
                if phase == 3:
                    daemon.guard.container_copy(['cp', '-', 'a'*64+':/'], startup_lifecycle.public_archive())
                else:
                    daemon.guard.container_start(['start', 'a'*64])
            self.assertFalse(any(m in ('PUT', 'POST') for m, _, _ in daemon.events[before:]))

    def pending_daemon(self, mutation=None):
        daemon = OwnerDaemon()
        original = daemon.exchange
        def exchange(method, path, body=None):
            result = original(method, path, body)
            if method == 'POST' and '/containers/create?' in path:
                daemon.row['NetworkSettings']['Networks'][daemon.network['Name']]['NetworkID'] = ''
                daemon.row['State'].update(Pid=0, Dead=False, OOMKilled=False, Error='', ExitCode=0,
                        StartedAt='0001-01-01T00:00:00Z', FinishedAt='0001-01-01T00:00:00Z')
                daemon.row['RestartCount'] = 0
                if mutation:
                    mutation(daemon)
            elif path.endswith('/start'):
                daemon.row['NetworkSettings']['Networks'][daemon.network['Name']]['NetworkID'] = daemon.network['Id']
            return result
        daemon.exchange = exchange
        return daemon

    def test_never_started_created_pending_network_allows_copy_and_start(self):
        daemon = self.pending_daemon()
        daemon.dispatch_cli()
        daemon.guard.finish_execution()
        self.assertTrue(daemon.guard.cleaned)

    def test_pending_network_refuses_foreign_ids_and_any_started_state(self):
        mutations = [lambda d: d.row['State'].update(StartedAt='2026-10-17T12:00:00Z'),
                     lambda d: d.row['State'].update(FinishedAt='2026-10-17T12:00:00Z'),
                     lambda d: d.row['State'].update(Running=True),
                     lambda d: d.row['State'].update(Pid=123),
                     lambda d: d.row['State'].update(Status='exited'),
                     lambda d: d.row.update(RestartCount=1),
                     lambda d: d.row['NetworkSettings']['Networks'][d.network['Name']].update(NetworkID='f'*64)]
        for mutation in mutations:
            daemon = self.pending_daemon(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(dev.Refusal):
                daemon.dispatch_cli()
            self.assertTrue(daemon.guard.ownership_lost)
            self.assertFalse(any(m == 'PUT' or p.endswith('/start') for m, p, _ in daemon.events))

    def test_empty_network_id_after_start_or_stop_is_always_refused(self):
        for stopped in [False, True]:
            daemon = self.pending_daemon()
            daemon.dispatch_cli()
            if stopped:
                daemon.row['State'].update(Status='exited', Running=False, Pid=0, ExitCode=0,
                        FinishedAt='2026-10-17T12:00:01Z')
            daemon.row['NetworkSettings']['Networks'][daemon.network['Name']]['NetworkID'] = ''
            with self.subTest(stopped=stopped), self.assertRaises(dev.Refusal):
                daemon.guard.owned()
            self.assertTrue(daemon.guard.ownership_lost)

class ExecutionEnvelope(unittest.TestCase):
    def inputs(self, phase):
        import base64
        import startup
        import startup_lifecycle
        fixture = boundary_fixture()
        fixture.update(images=list(fixture['selection_plan']), execute=True, lifecycle=True, fresh=True)
        fixture['planned_volume'] = fixture.pop('volume')
        facts = startup.selected_facts(dict(fixture, postgres_image=fixture['selection_plan'][fixture['postgres_image']]))
        facts.update(original_image=fixture['postgres_image'], immutable_selection_proven=True, create_request_proven=True)
        events = [{'kind': 'container_inspect'}] + [
            {'kind': 'image_inspect', 'image_index': i, 'descriptor': fixture['image_observations'][fixture['selection_plan'][tag]]}
            for i, tag in enumerate(fixture['images'])] + [
                {'kind': 'volume_missing'}, {'kind': 'network_inspect'}, {'kind': 'fresh_volume_create_acknowledged'}]
        if phase >= 3:
            events.append({'kind': 'postgres_create', 'facts': facts})
        if phase == 4:
            events.append(startup_lifecycle.transfer_event())
        full = expected_environment(fixture)
        routing = {k: full[k] for k in ('DOCKER_HOST', 'DOCKER_CONFIG')}
        request = {'token': 'a'*32, 'phase': {2: 'container_create', 3: 'container_copy', 4: 'container_start'}[phase],
                'args': {2: expected_request(fixture), 3: ['cp', '-', 'b'*64+':/'], 4: ['start', 'b'*64]}[phase],
                'environment': full if phase == 2 else routing}
        if phase == 3:
            request['archive'] = base64.b64encode(startup_lifecycle.public_archive()).decode()
        return fixture, events, request

    def test_parent_copy_start_accept_original_routing_only_envelopes(self):
        import startup
        import json
        for phase in [3, 4]:
            fixture, events, request = self.inputs(phase)
            with self.subTest(phase=phase):
                self.assertEqual(startup.validate_execution_handoff(json.dumps(request).encode(), 'a'*32, fixture, events, phase), request)

    def test_create_requires_all_four_public_inputs_and_all_phases_refuse_routing_drift(self):
        import startup
        import json
        for field in create_profile.CONTAINER_ENV:
            fixture, events, request = self.inputs(2)
            request['environment'].pop(field)
            with self.subTest(field=field), self.assertRaises(dev.Refusal):
                startup.validate_execution_handoff(json.dumps(request).encode(), 'a'*32, fixture, events, 2)
        for phase in [2, 3, 4]:
            for field in ['DOCKER_HOST', 'DOCKER_CONFIG', 'DOCKER_CONTEXT']:
                fixture, events, request = self.inputs(phase)
                request['environment'][field] = 'foreign'
                with self.subTest(phase=phase, field=field), self.assertRaises(dev.Refusal):
                    startup.validate_execution_handoff(json.dumps(request).encode(), 'a'*32, fixture, events, phase)

    def test_fake_socket_serialization_matches_exact_phase_specific_parent_envelopes(self):
        import startup
        import startup_lifecycle
        import struct
        import os
        import json
        for phase in [2, 3, 4]:
            fixture, events, expected = self.inputs(phase)
            peer = Mock()
            peer.getsockopt.return_value = struct.pack('3i', 12345, os.getuid(), 0)
            peer.recv.side_effect = [b'b'*64+b'\n' if phase == 2 else b'OK\n', b'']
            context = Mock()
            context.__enter__ = Mock(return_value=peer)
            context.__exit__ = Mock(return_value=False)
            env = {**expected_environment(fixture), 'ENV_PRIVATE_OWNER_TOKEN': 'a'*32, 'ENV_PRIVATE_OWNER_PID': '12345'}
            with patch.object(startup.socket, 'socket', return_value=context):
                startup.owner_handoff(fixture, expected['phase'], expected['args'], env,
                        archive=startup_lifecycle.public_archive() if phase == 3 else None)
            encoded = peer.sendall.call_args.args[0]
            self.assertEqual(json.loads(encoded), expected)
            startup.validate_execution_handoff(encoded, 'a'*32, fixture, events, phase)

class CleanupConsumeOnce(unittest.TestCase):
    def test_failed_cleanup_cannot_repeat_mutation_or_restart_deadline(self):
        for failure in ['timeout', 'refused', 'interrupted']:
            clock = [100.0]
            with patch.object(resources.time, 'monotonic', side_effect=lambda: clock[0]):
                daemon = OwnerDaemon()
                daemon.dispatch_cli()
                def refuse_delete(method, path):
                    if method == 'DELETE' and '/containers/' in path:
                        if failure == 'interrupted':
                            raise KeyboardInterrupt()
                        dev.refuse('docker', 'docker_timeout' if failure == 'timeout' else 'docker_response_invalid')
                daemon.hook = refuse_delete
                with self.assertRaises((dev.Refusal, KeyboardInterrupt)):
                    daemon.guard.cleanup_execution()
                deadline, before = daemon.guard.deadline, len(daemon.events)
                clock[0] = 109.0
                with self.assertRaises((dev.Refusal, KeyboardInterrupt)):
                    daemon.guard.cleanup_execution()
                with self.subTest(failure=failure):
                    self.assertEqual(len(daemon.events), before)
                    self.assertEqual((daemon.guard.deadline, daemon.deadline), (deadline, deadline))
                    self.assertEqual(sum(m == 'DELETE' for m, _, _ in daemon.events), 1)

    def test_completed_cleanup_cannot_restart_its_deadline(self):
        clock = [100.0]
        with patch.object(resources.time, 'monotonic', side_effect=lambda: clock[0]):
            daemon = OwnerDaemon()
            daemon.dispatch_cli()
            daemon.guard.cleanup_execution()
            before, deadline = len(daemon.events), daemon.guard.deadline
            clock[0] = 109.0
            with self.assertRaises(dev.Refusal):
                daemon.guard.cleanup_execution()
            self.assertEqual(len(daemon.events), before)
            self.assertEqual((daemon.guard.deadline, daemon.deadline), (deadline, deadline))

class RetainedExecutionTransport(unittest.TestCase):
    def test_execution_routes_require_persistent_owner_before_connect(self):
        import startup_lifecycle
        f = boundary_fixture()
        selected = dict(f, postgres_image=f['selection_plan'][f['postgres_image']])
        create = create_profile.disposable_execution_request(expected_request(selected), selected, expected_environment(f))
        ident = 'a'*64
        routes = [(create['method'], create['path'], create['body']),
                  ('GET', '/v1.48/containers/'+ident+'/json', None),
                  ('GET', '/v1.48/containers/supabase_db_'+f['project']+'/json', None),
                  ('PUT', '/v1.48/containers/'+ident+'/archive?path=%2F', startup_lifecycle.public_archive()),
                  ('POST', '/v1.48/containers/'+ident+'/start', None),
                  ('POST', '/v1.48/containers/'+ident+'/stop?t=5', None),
                  ('DELETE', '/v1.48/containers/'+ident+'?force=false', None),
                  ('DELETE', '/v1.48/containers/'+ident+'?force=true', None),
                  ('DELETE', '/v1.48/volumes/supabase_db_'+f['project'], None),
                  ('DELETE', '/v1.48/networks/'+ident, None)]
        for method, path, body in routes:
            with self.subTest(method=method, path=path):
                # An unexpected transport regression must never use a real socket.
                with patch.object(dev.socket, 'socket', side_effect=AssertionError('unexpected connection')), self.assertRaises(dev.Refusal) as caught:
                    dev.docker_exchange(method, path, body)
                self.assertEqual(caught.exception.code, 'docker_request_invalid')
                request = dev._docker_request(method, path, body, True)
                self.assertIn(b'Connection: keep-alive\r\n', request)


class EndpointAliases(unittest.TestCase):
    def test_reconnected_same_network_without_required_alias_refuses_and_latches(self):
        for missing in ['db', 'db.supabase.internal']:
            daemon = OwnerDaemon()
            daemon.dispatch_cli()
            endpoint = daemon.row['NetworkSettings']['Networks'][daemon.network['Name']]
            endpoint['Aliases'].remove(missing)
            with self.subTest(missing=missing), self.assertRaises(dev.Refusal):
                daemon.guard.owned()
            self.assertTrue(daemon.guard.ownership_lost)
            endpoint['Aliases'].append(missing)
            before = len(daemon.events)
            with self.assertRaises(dev.Refusal):
                daemon.guard.cleanup_execution()
            self.assertEqual(len(daemon.events), before)

    def test_requested_aliases_preserve_legitimate_docker_added_names(self):
        daemon = OwnerDaemon()
        daemon.dispatch_cli()
        endpoint = daemon.row['NetworkSettings']['Networks'][daemon.network['Name']]
        self.assertEqual(endpoint['Aliases'][:2], ['db', 'db.supabase.internal'])
        self.assertEqual(len(endpoint['Aliases']), 4)
        daemon.guard.owned()

class PersistenceAcceptance(unittest.TestCase):
    def test_distinct_owner_recreation_proves_same_volume_marker_and_clean_disposal(self):
        daemon = PersistenceDaemon()
        daemon.dispatch_cli()
        with patch.object(dev, 'free_ports'):
            daemon.guard.finish_execution()
        self.assertTrue(daemon.guard.persistence_verified)
        self.assertEqual(daemon.creates, 2)
        self.assertEqual(daemon.sql_modes, ['write', 'schemas', 'verify', 'schemas'])
        self.assertTrue(daemon.guard.cleaned)
        self.assertIsNone(daemon.volume)
        deletes = [p for m, p, _ in daemon.events if m == 'DELETE' and '/containers/' in p]
        self.assertEqual(deletes, ['/v1.48/containers/'+'a'*64+'?force=false',
                                   '/v1.48/containers/'+'c'*64+'?force=false'])

class InitializedCliAcceptance(unittest.TestCase):
    def test_initialized_cli_has_separate_probe_ensure_and_replacement_authority(self):
        daemon = PersistenceDaemon()
        guard = daemon.guard
        guard.enable_initialized_cli()
        daemon.dispatch_cli()
        guard.prepare_initialized_cli()
        self.assertEqual(guard.phase, 10)
        self.assertIsNone(daemon.row)
        self.assertIsNotNone(daemon.volume)
        guard.initialized_probe()
        guard.initialized_ensure()
        self.assertEqual(guard.phase, 9)
        with patch.object(dev, 'free_ports'):
            guard.container_create(expected_request(daemon.fixture), daemon.fixture,
                                   expected_environment(daemon.fixture), _replacement=True)
        import startup_lifecycle as lifecycle
        guard.container_copy(['cp', '-', guard.container_id + ':/'], lifecycle.public_archive())
        guard.container_start(['start', guard.container_id])
        guard.finish_execution()
        self.assertTrue(guard.persistence_verified)
        self.assertTrue(guard.cleaned)
        self.assertEqual(daemon.sql_modes, ['write', 'schemas', 'verify', 'schemas'])
        self.assertEqual(daemon.creates, 2)

    def prepared(self):
        daemon = PersistenceDaemon()
        daemon.guard.enable_initialized_cli()
        daemon.dispatch_cli()
        daemon.guard.prepare_initialized_cli()
        return daemon

    def test_wrong_phase_and_repeated_observations_never_dispatch_or_extend_budget(self):
        daemon = self.prepared()
        guard = daemon.guard
        deadline = guard.deadline
        before = len(daemon.events)
        with self.assertRaises(dev.Refusal):
            guard.initialized_ensure()
        self.assertEqual(len(daemon.events), before)
        guard.initialized_probe()
        before = len(daemon.events)
        with self.assertRaises(dev.Refusal):
            guard.initialized_probe()
        self.assertEqual(len(daemon.events), before)
        guard.initialized_ensure()
        before = len(daemon.events)
        for action in [guard.initialized_probe, guard.initialized_ensure, guard.prepare_initialized_cli, guard.enable_initialized_cli]:
            with self.assertRaises(dev.Refusal):
                action()
        self.assertEqual(len(daemon.events), before)
        self.assertEqual(guard.deadline, deadline)

    def test_missing_changed_used_volume_bridge_and_image_latch_loss_before_mutation(self):
        for defect in ['missing', 'changed', 'used', 'bridge', 'image']:
            daemon = self.prepared()
            guard = daemon.guard
            if defect == 'missing':
                daemon.volume = None
            elif defect == 'changed':
                daemon.volume['CreatedAt'] = 'changed'
            elif defect == 'used':
                original = daemon.exchange
                def foreign(method, path, body=None):
                    if '/containers/json?' in path:
                        return 200, [{'Id': 'f'*64}]
                    return original(method, path, body)
                daemon.exchange = foreign
            elif defect == 'bridge':
                daemon.network['Labels']['foreign'] = 'true'
            else:
                original = daemon.exchange
                def foreign(method, path, body=None):
                    result = original(method, path, body)
                    if '/images/' in path:
                        return 200, dict(result[1], Id='sha256:'+'f'*64)
                    return result
                daemon.exchange = foreign
            before = len([e for e in daemon.events if e[0] != 'GET'])
            with self.subTest(defect=defect), self.assertRaises(dev.Refusal):
                guard.initialized_probe()
            self.assertTrue(guard.ownership_lost)
            self.assertEqual(guard.phase, -1)
            self.assertEqual(len([e for e in daemon.events if e[0] != 'GET']), before)
            with self.assertRaises(dev.Refusal):
                guard.initialized_probe()
            self.assertFalse(guard.persistence_verified)

    def test_lost_probe_or_ensure_consumes_without_cleanup_adoption(self):
        for phase in ['probe', 'ensure']:
            daemon = self.prepared()
            guard = daemon.guard
            if phase == 'ensure':
                guard.initialized_probe()
            original = daemon.exchange
            def lost(method, path, body=None):
                if '/volumes/' in path:
                    dev.refuse('docker', 'docker_timeout')
                return original(method, path, body)
            daemon.exchange = lost
            action = guard.initialized_probe if phase == 'probe' else guard.initialized_ensure
            with self.assertRaises(dev.Refusal):
                action()
            self.assertEqual(guard.phase, -1)
            with self.assertRaises(dev.Refusal):
                action()
            with self.assertRaises(dev.Refusal):
                guard.cleanup_execution()
            self.assertIsNotNone(daemon.volume)
            self.assertFalse(guard.persistence_verified)

    def test_initialized_handoffs_require_exact_prefix_token_routing_and_archive(self):
        import startup, json, copy
        for phase in [2, 3, 4]:
            fixture, events, request = ExecutionEnvelope().inputs(phase)
            fixture['initialized'] = True
            fixture.pop('fresh')
            fixture['volume'] = fixture.pop('planned_volume')
            events[5] = {'kind': 'volume_inspect'}
            events[7] = {'kind': 'initialized_volume_ensure_acknowledged'}
            owner_phase = 9 if phase == 2 else phase
            startup.validate_execution_handoff(json.dumps(request).encode(), 'a'*32, fixture, events, owner_phase)
            for defect in ['token', 'routing', 'prefix', 'profile', 'archive']:
                if defect == 'archive' and phase != 3:
                    continue
                changed, observations = copy.deepcopy(request), copy.deepcopy(events)
                if defect == 'token':
                    changed['token'] = 'b'*32
                elif defect == 'routing':
                    changed['environment']['DOCKER_HOST'] = 'foreign'
                elif defect == 'prefix':
                    observations[7] = {'kind': 'existing_volume_create_refused'}
                elif defect == 'profile':
                    changed['args'] += ['extra']
                else:
                    changed['archive'] = 'bad'
                # Copy/start IDs are additionally checked by the closed owner.
                if defect == 'profile' and phase != 2:
                    continue
                with self.subTest(phase=phase, defect=defect), self.assertRaises(dev.Refusal):
                    startup.validate_execution_handoff(json.dumps(changed).encode(), 'a'*32, fixture, observations, owner_phase)

    def test_initialized_observation_handoffs_prove_both_exact_prefixes(self):
        import startup, json
        fixture, events, _ = ExecutionEnvelope().inputs(2)
        fixture['initialized'] = True
        fixture.pop('fresh')
        fixture['volume'] = fixture.pop('planned_volume')
        events[5] = {'kind': 'volume_inspect'}
        events[7] = {'kind': 'initialized_volume_ensure_acknowledged'}
        project = fixture['project']
        for phase, verb, prefix, args in [
                (10, 'initialized_probe', events[:5], ['volume', 'inspect', 'supabase_db_' + project]),
                (11, 'initialized_ensure', events[:7], ['volume', 'create', '--label', 'com.supabase.cli.project=' + project,
                    '--label', 'com.docker.compose.project=' + project, 'supabase_db_' + project])]:
            request = {'token': 'a'*32, 'phase': verb, 'args': args}
            startup.validate_owner_request(json.dumps(request).encode(), 'a'*32, fixture, prefix, phase)
            for bad in [prefix[1:], prefix + prefix[:1], list(reversed(prefix))]:
                with self.assertRaises(dev.Refusal):
                    startup.validate_owner_request(json.dumps(request).encode(), 'a'*32, fixture, bad, phase)

    def test_both_fixture_and_listener_custodies_are_checked_and_never_rebound(self):
        import startup
        guard = self.prepared().guard
        first, second = Path('/private/first'), Path('/private/second')
        with patch.object(startup, 'check_fixture_custody') as check:
            # Bind through the same closed fields as the supervisor without sockets.
            guard._fixture = (first, 11, {}, 'first-hash', {})
            guard._listener_identity = 'first-listener'
            guard.bind_second_fixture(second, 12, {}, 'second-hash', {})
            guard.bind_second_listener('second-listener')
            check.reset_mock()
            guard.current()
            self.assertEqual([call.args[0] for call in check.call_args_list], [first, second])
            self.assertEqual([call.kwargs['listener_identity'] for call in check.call_args_list], ['first-listener', 'second-listener'])
            for action in [lambda: guard.bind_fixture(first, 11, {}, '', {}),
                           lambda: guard.bind_listener('replacement'),
                           lambda: guard.bind_second_fixture(second, 12, {}, '', {}),
                           lambda: guard.bind_second_listener('replacement')]:
                with self.assertRaises(dev.Refusal):
                    action()
            check.side_effect = dev.Refusal('startup', 'fixture_changed')
            with self.assertRaises(dev.Refusal):
                guard.current()
            self.assertTrue(guard.ownership_lost)

    def test_uncertain_initialized_create_cannot_replay_or_adopt_container(self):
        daemon = self.prepared()
        guard = daemon.guard
        guard.initialized_probe()
        guard.initialized_ensure()
        original = daemon.exchange
        def lost(method, path, body=None):
            result = original(method, path, body)
            if '/containers/create?' in path:
                return 201, {}
            return result
        daemon.exchange = lost
        with patch.object(dev, 'free_ports'), self.assertRaises(dev.Refusal):
            guard.container_create(expected_request(daemon.fixture), daemon.fixture,
                                   expected_environment(daemon.fixture), _replacement=True)
        self.assertEqual(guard.phase, -1)
        self.assertIsNone(guard.container_id)
        self.assertIsNotNone(daemon.row)
        before = len(daemon.events)
        with self.assertRaises(dev.Refusal):
            guard.container_create(expected_request(daemon.fixture), daemon.fixture,
                                   expected_environment(daemon.fixture), _replacement=True)
        with self.assertRaises(dev.Refusal):
            guard.cleanup_execution()
        self.assertEqual(len(daemon.events), before)
        self.assertFalse(guard.persistence_verified)

    def test_initialized_deadline_and_interrupt_consume_phase_without_replay_or_reset(self):
        for phase in ['probe', 'ensure']:
            for failure in [dev.Refusal('docker', 'docker_timeout'), KeyboardInterrupt()]:
                daemon = self.prepared()
                guard = daemon.guard
                if phase == 'ensure':
                    guard.initialized_probe()
                deadline = guard.deadline
                action = guard.initialized_probe if phase == 'probe' else guard.initialized_ensure
                with patch.object(guard, '_current', side_effect=failure):
                    with self.subTest(phase=phase, failure=type(failure).__name__), self.assertRaises(type(failure)):
                        action()
                self.assertEqual(guard.phase, -1)
                self.assertEqual(guard.deadline, deadline)
                before = len(daemon.events)
                with self.assertRaises(dev.Refusal):
                    action()
                self.assertEqual(len(daemon.events), before)
                self.assertFalse(guard.persistence_verified)
                self.assertFalse(guard.cleanup_attempted)
                self.assertIsNone(daemon.row)
                self.assertIsNotNone(daemon.volume)

    def test_second_custody_failure_at_replacement_phases_is_not_hidden_by_first(self):
        import startup
        for phase in [3, 4, 5, 6, 7]:
            guard = self.prepared().guard
            first, second = Path('/private/first'), Path('/private/second')
            guard._fixture = (first, 11, {}, 'first-hash', {})
            guard._second_fixture = (second, 12, {}, 'second-hash', {})
            guard._listener_identity, guard._second_listener_identity = 'one', 'two'
            guard.phase = phase
            seen = []
            def check(work, *args, **kwargs):
                seen.append(work)
                if work == second:
                    dev.refuse('startup', 'fixture_changed')
            with patch.object(startup, 'check_fixture_custody', side_effect=check):
                with self.subTest(phase=phase), self.assertRaises(dev.Refusal):
                    guard.current()
            self.assertEqual(seen, [first, second])
            self.assertTrue(guard.ownership_lost)
            self.assertFalse(guard.persistence_verified)

    def test_initialized_private_envelope_parser_rejects_malformed_or_changed_fields(self):
        import startup, json
        fixture, events, _ = ExecutionEnvelope().inputs(2)
        fixture['initialized'] = True
        fixture.pop('fresh')
        fixture['volume'] = fixture.pop('planned_volume')
        events[5] = {'kind': 'volume_inspect'}
        for phase in [10, 11]:
            args = (['volume', 'inspect', 'supabase_db_' + fixture['project']] if phase == 10 else
                    ['volume', 'create', '--label', 'com.supabase.cli.project=' + fixture['project'],
                     '--label', 'com.docker.compose.project=' + fixture['project'], 'supabase_db_' + fixture['project']])
            request = {'token': 'a'*32, 'phase': 'initialized_probe' if phase == 10 else 'initialized_ensure', 'args': args}
            prefix = events[:5 if phase == 10 else 7]
            invalid = [b'{', b'null', b'[]', json.dumps(dict(request, token='b'*32)).encode(),
                       json.dumps(dict(request, phase='probe')).encode(),
                       json.dumps(dict(request, args=args+['extra'])).encode(),
                       json.dumps(dict(request, extra=True)).encode()]
            for raw in invalid:
                with self.subTest(phase=phase, raw=raw), self.assertRaises(dev.Refusal):
                    startup.validate_owner_request(raw, 'a'*32, fixture, prefix, phase)

    def test_initialized_private_probe_ensure_acknowledgements_are_exact(self):
        import startup, struct, os
        fixture = boundary_fixture()
        environment = dict(expected_environment(fixture), ENV_PRIVATE_OWNER_TOKEN='a'*32, ENV_PRIVATE_OWNER_PID='12345')
        for phase in ['initialized_probe', 'initialized_ensure']:
            for response in [b'', b'OK', b'OK\nextra', b'bad\n']:
                peer = Mock()
                peer.getsockopt.return_value = struct.pack('3i', 12345, os.getuid(), 0)
                peer.recv.side_effect = [response, b'']
                context = Mock()
                context.__enter__ = Mock(return_value=peer)
                context.__exit__ = Mock(return_value=False)
                with patch.object(startup.socket, 'socket', return_value=context), self.assertRaises(dev.Refusal):
                    startup.owner_handoff(fixture, phase, ['volume', 'inspect', 'supabase_db_' + fixture['project']], environment)
                self.assertEqual(peer.sendall.call_count, 1)

class PersistenceDaemon(OwnerDaemon):
    def __init__(self):
        super().__init__()
        self.creates = 0
        self.sql_modes = []
        self.executed_sql_modes = []
        self.exec_body = None
        self.exec_id = None
        self.exec_started = False
        self.exec_exit = None
        self.marker = None
        self.cluster = 'synthetic-postgres-cluster-1'
        self.initialization_markers = True
        self.guard.enable_persistence()

    def exchange(self, method, path, body=None):
        if path.endswith('/exec'):
            self.events.append((method, path, self.copy(body)))
            self.exec_body = body
            # Independent PostgreSQL model: writes commit only on exec-start;
            # recreation preserves volume facts, while predicates can fail.
            query = body['Cmd'][-1]
            mode = ('schemas' if body['Cmd'][body['Cmd'].index('-d') + 1] == '_supabase'
                    else 'write' if 'CREATE TABLE' in query else 'verify')
            self.sql_modes.append(mode)
            self.exec_started, self.exec_exit = False, None
            self.exec_id = format(len(self.sql_modes) + 10, '064x')
            return 201, {'Id': self.exec_id}
        if path.startswith('/v1.48/exec/'):
            self.events.append((method, path, self.copy(body)))
            if path.endswith('/start'):
                self.exec_started = True
                mode = self.sql_modes[-1]
                self.executed_sql_modes.append(mode)
                expected = (self.fixture['run_id'], self.cluster)
                write_valid = mode == 'write' and self.marker is None
                self.exec_exit = 0 if self.initialization_markers and (write_valid or mode == 'schemas' or mode == 'verify' and self.marker == expected) else 1
                if write_valid and self.exec_exit == 0:
                    self.marker = expected
                return 200, None
            return 200, {'ID': self.exec_id, 'ContainerID': self.row['Id'], 'Running': False,
                         'ExitCode': self.exec_exit, 'Pid': 321 if self.exec_started else 0,
                         'ProcessConfig': {'entrypoint': 'psql', 'arguments': self.exec_body['Cmd'][1:],
                                           'privileged': False, 'tty': False, 'user': 'postgres'}}
        result = super().exchange(method, path, body)
        if '/containers/create?' in path:
            self.creates += 1
            if self.creates == 2:
                self.row['Id'] = 'c'*64
                result = 201, {'Id': 'c'*64, 'Warnings': []}
        if path.endswith('/json') and '/containers/' in path and self.row is not None:
            reference = path.split('/containers/')[1][:-5]
            if reference in ['a'*64, 'c'*64] and reference != self.row['Id']:
                return 404, None
        return result

class PersistenceFailureMatrix(unittest.TestCase):
    def run_owner(self, daemon):
        daemon.dispatch_cli()
        with patch.object(dev, 'free_ports'):
            daemon.guard.finish_execution()

    def test_closed_sql_and_detached_routes_refuse_every_changed_operand(self):
        import startup_lifecycle as lifecycle
        import copy
        run = boundary_fixture()['run_id']
        for mode in ['write', 'verify', 'schemas']:
            body = lifecycle.persistence_exec(run, mode)
            path = '/v1.48/containers/'+'a'*64+'/exec'
            self.assertIn(b'keep-alive', dev._docker_request('POST', path, body, True))
            self.assertIn('IS NOT TRUE', body['Cmd'][-1])
            with self.assertRaises(dev.Refusal):
                dev._docker_request('POST', path, body, False)
            for key, value in [('AttachStdout', True), ('AttachStderr', True), ('AttachStdin', True),
                               ('Tty', True), ('Privileged', True), ('User', 'root'), ('Env', []),
                               ('Cmd', ['psql', '-c', 'SELECT true']), ('AttachStdout', 0)]:
                changed = copy.deepcopy(body)
                changed[key] = value
                with self.subTest(mode=mode, key=key), self.assertRaises(dev.Refusal):
                    dev._docker_request('POST', path, changed, True)
        write = lifecycle.persistence_exec(run, 'write')['Cmd'][-1]
        verify = lifecycle.persistence_exec(run, 'verify')['Cmd'][-1]
        self.assertIn('COMMIT;', write)
        self.assertIn('pg_control_system()', verify)
        self.assertIn(run, verify)
        self.assertNotIn('CREATE', verify)
        for body in [{'Detach': False, 'Tty': False}, {'Detach': True, 'Tty': True},
                     {'Detach': 1, 'Tty': False}, {'Detach': True, 'Tty': False, 'extra': False}]:
            with self.assertRaises(dev.Refusal):
                dev._docker_request('POST', '/v1.48/exec/'+'d'*64+'/start', body, True)

    def test_sql_nonzero_and_malformed_exec_cannot_prove_persistence(self):
        mutations = [lambda r: r.update(ExitCode=1), lambda r: r.update(ExitCode=True),
                     lambda r: r.update(ID='f'*64), lambda r: r.update(ContainerID='f'*64),
                     lambda r: r.update(Running=None), lambda r: r.update(Pid=True),
                     lambda r: r['ProcessConfig'].update(user='root'),
                     lambda r: r['ProcessConfig'].update(arguments=['-c', 'SELECT true'])]
        for mutation in mutations:
            daemon = PersistenceDaemon()
            exchange = daemon.exchange
            def changed(method, path, body=None):
                status, row = exchange(method, path, body)
                if path.startswith('/v1.48/exec/') and path.endswith('/json'):
                    mutation(row)
                return status, row
            daemon.exchange = changed
            with self.subTest(mutation=mutation), self.assertRaises(dev.Refusal):
                self.run_owner(daemon)
            self.assertFalse(daemon.guard.persistence_verified)
            self.assertFalse(any('/exec/' in p and p.endswith('/start') for _, p, _ in daemon.events))
            daemon.guard.cleanup_execution()
            self.assertTrue(daemon.guard.cleaned)

    def test_lost_marker_or_cluster_nonzero_after_replacement_fails_without_repair(self):
        for defect in ['marker', 'cluster', 'initialization']:
            daemon = PersistenceDaemon()
            exchange = daemon.exchange
            def missing(method, path, body=None):
                result = exchange(method, path, body)
                if '/containers/create?' in path and daemon.creates == 2:
                    if defect == 'marker':
                        daemon.marker = None
                    elif defect == 'cluster':
                        daemon.cluster = 'reinitialized-cluster'
                    else:
                        daemon.initialization_markers = False
                return result
            daemon.exchange = missing
            with self.subTest(defect=defect), self.assertRaises(dev.Refusal) as caught:
                self.run_owner(daemon)
            self.assertEqual(caught.exception.code, 'execution_sql_failed')
            self.assertEqual(daemon.sql_modes, ['write', 'schemas', 'verify'])
            self.assertEqual(daemon.executed_sql_modes, ['write', 'schemas', 'verify'])
            self.assertFalse(daemon.guard.persistence_verified)
            daemon.guard.cleanup_execution()
            self.assertTrue(daemon.guard.cleaned)

    def test_uncertain_intermediate_remove_consumed_and_never_retried(self):
        for failure in ['response', 'interruption']:
            daemon = PersistenceDaemon()
            exchange = daemon.exchange
            def lost(method, path, body=None):
                result = exchange(method, path, body)
                if method == 'DELETE' and '/containers/' in path:
                    if failure == 'interruption':
                        raise KeyboardInterrupt()
                    dev.refuse('docker', 'docker_response_invalid')
                return result
            daemon.exchange = lost
            with self.subTest(failure=failure), self.assertRaises((dev.Refusal, KeyboardInterrupt)):
                self.run_owner(daemon)
            before, deadline = len(daemon.events), daemon.guard.deadline
            with self.assertRaises(dev.Refusal):
                daemon.guard.finish_execution()
            with self.assertRaises(dev.Refusal):
                daemon.guard.cleanup_execution()
            self.assertEqual(len(daemon.events), before)
            self.assertFalse(daemon.guard.cleaned)

    def test_gap_foreign_reference_or_changed_volume_latches_custody_loss(self):
        for defect in ['volume', 'network', 'reference']:
            daemon = PersistenceDaemon()
            exchange = daemon.exchange
            def corrupt(method, path, body=None):
                result = exchange(method, path, body)
                if method == 'DELETE' and '/containers/' in path:
                    if defect == 'volume':
                        daemon.volume['Labels']['foreign'] = 'changed'
                    elif defect == 'network':
                        daemon.network['Containers'] = {'f'*64: {}}
                if defect == 'reference' and daemon.guard.old_container_id and '/containers/json?' in path:
                    return 200, [{'Id': 'f'*64}]
                return result
            daemon.exchange = corrupt
            with self.subTest(defect=defect), self.assertRaises(dev.Refusal):
                self.run_owner(daemon)
            self.assertTrue(daemon.guard.ownership_lost)
            self.assertEqual(daemon.creates, 1)
            self.assertFalse(daemon.guard.cleaned)

    def test_repeated_exec_and_finish_do_not_replay_or_reset_budget(self):
        daemon = PersistenceDaemon()
        daemon.dispatch_cli()
        started = daemon.guard.healthy_instance()
        daemon.guard.persistence_sql('write', started)
        before, deadline = len(daemon.events), daemon.guard.deadline
        with self.assertRaises(dev.Refusal):
            daemon.guard.persistence_sql('write', started)
        self.assertEqual(len(daemon.events), before)
        self.assertEqual(daemon.guard.deadline, deadline)

    def test_replacement_deadline_is_one_total_budget_and_failure_keeps_no_success(self):
        clock = [0.0]
        with patch.object(resources.time, 'monotonic', side_effect=lambda: clock[0]):
            daemon = PersistenceDaemon()
            exchange = daemon.exchange
            def expire(method, path, body=None):
                result = exchange(method, path, body)
                if daemon.creates == 2 and path.endswith('/start') and '/containers/' in path:
                    clock[0] = daemon.deadline + 1
                return result
            daemon.exchange = expire
            with self.assertRaises(dev.Refusal) as caught:
                self.run_owner(daemon)
            self.assertEqual(caught.exception.code, 'docker_timeout')
            self.assertFalse(daemon.guard.persistence_verified)
            self.assertFalse(daemon.guard.cleaned)
            daemon.guard.cleanup_execution()
            self.assertTrue(daemon.guard.cleaned)

class PersistenceUncertainty(unittest.TestCase):
    def test_lost_or_malformed_replacement_create_never_adopts_or_replays(self):
        for defect in ['lost', 'malformed', 'same-id']:
            daemon = PersistenceDaemon()
            exchange = daemon.exchange
            def uncertain(method, path, body=None):
                result = exchange(method, path, body)
                if '/containers/create?' in path and daemon.creates == 2:
                    if defect == 'lost':
                        dev.refuse('docker', 'docker_response_invalid')
                    return 201, {} if defect == 'malformed' else {'Id': 'a'*64, 'Warnings': []}
                return result
            daemon.exchange = uncertain
            daemon.dispatch_cli()
            with patch.object(dev, 'free_ports'), self.subTest(defect=defect), self.assertRaises(dev.Refusal):
                daemon.guard.finish_execution()
            self.assertIsNone(daemon.guard.container_id)
            self.assertEqual(daemon.guard.phase, -1)
            before = len(daemon.events)
            with self.assertRaises(dev.Refusal):
                daemon.guard.finish_execution()
            with self.assertRaises(dev.Refusal):
                daemon.guard.cleanup_execution()
            self.assertEqual(len(daemon.events), before)
            self.assertFalse(daemon.guard.persistence_verified)
            self.assertFalse(daemon.guard.cleaned)
            self.assertIsNotNone(daemon.volume)

    def test_uncertain_exec_create_or_start_consumes_probe_before_dispatch(self):
        for defect in ['create-lost', 'create-malformed', 'start-lost', 'start-malformed']:
            daemon = PersistenceDaemon()
            daemon.dispatch_cli()
            started = daemon.guard.healthy_instance()
            exchange = daemon.exchange
            def uncertain(method, path, body=None):
                result = exchange(method, path, body)
                target = path.endswith('/exec') if defect.startswith('create') else '/exec/' in path and path.endswith('/start')
                if target:
                    if defect.endswith('lost'):
                        dev.refuse('docker', 'docker_response_invalid')
                    return (201, {}) if defect.startswith('create') else (500, None)
                return result
            daemon.exchange = uncertain
            with self.subTest(defect=defect), self.assertRaises(dev.Refusal):
                daemon.guard.persistence_sql('write', started)
            before, deadline = len(daemon.events), daemon.guard.deadline
            with self.assertRaises(dev.Refusal):
                daemon.guard.persistence_sql('write', started)
            self.assertEqual(len(daemon.events), before)
            self.assertEqual(daemon.guard.deadline, deadline)
            self.assertFalse(daemon.guard.persistence_verified)
            daemon.guard.cleanup_execution()
            self.assertTrue(daemon.guard.cleaned)

    def test_exec_polling_rechecks_same_instance_and_never_restarts_budget(self):
        for defect in ['restart', 'deadline', 'running-bool-exit']:
            daemon = PersistenceDaemon()
            daemon.dispatch_cli()
            started = daemon.guard.healthy_instance()
            exchange = daemon.exchange
            inspections = [0]
            def invalid(method, path, body=None):
                result = exchange(method, path, body)
                if '/exec/' in path and path.endswith('/json'):
                    inspections[0] += 1
                    if inspections[0] == 2:
                        if defect == 'restart':
                            daemon.row['State']['StartedAt'] = '2026-10-17T12:00:00.000000002Z'
                        elif defect == 'deadline':
                            daemon.deadline = 0
                        else:
                            result[1].update(Running=True, ExitCode=True)
                return result
            daemon.exchange = invalid
            deadline = daemon.guard.deadline
            with self.subTest(defect=defect), self.assertRaises(dev.Refusal):
                daemon.guard.persistence_sql('write', started)
            self.assertEqual(daemon.guard.deadline, deadline)
            self.assertFalse(daemon.guard.persistence_verified)

    def test_wrong_order_and_repeated_lifecycle_operands_refuse_without_dispatch(self):
        daemon = PersistenceDaemon()
        daemon.dispatch_cli()
        started = daemon.guard.healthy_instance()
        before, deadline = len(daemon.events), daemon.guard.deadline
        with self.assertRaises(dev.Refusal):
            daemon.guard.persistence_sql('verify', started)
        with self.assertRaises(dev.Refusal):
            daemon.guard.persistence_sql('schemas', started)
        with self.assertRaises(dev.Refusal):
            daemon.guard.recreate(started)
        self.assertEqual(len(daemon.events), before)
        self.assertEqual(daemon.guard.deadline, deadline)
        daemon.guard.stop_instance(started)
        before, deadline = len(daemon.events), daemon.guard.deadline
        with self.assertRaises(dev.Refusal):
            daemon.guard.stop_instance(started)
        self.assertEqual(len(daemon.events), before)
        self.assertEqual(daemon.guard.deadline, deadline)

class DockerExecLifecycle(unittest.TestCase):
    """Moby v28 inspect preserves null ExitCode until the started exec exits."""
    def test_never_started_null_then_running_null_then_completed_zero_qualifies(self):
        daemon = PersistenceDaemon()
        daemon.dispatch_cli()
        started = daemon.guard.healthy_instance()
        exchange = daemon.exchange
        running_observations = []
        def observe(method, path, body=None):
            status, row = exchange(method, path, body)
            if '/exec/' in path and path.endswith('/json'):
                if not daemon.exec_started:
                    self.assertIsNone(row['ExitCode'])
                    self.assertEqual(row['Pid'], 0)
                elif not running_observations:
                    row.update(Running=True, ExitCode=None, Pid=321)
                    running_observations.append(True)
            return status, row
        daemon.exchange = observe
        with patch.object(resources.time, 'sleep'):
            daemon.guard.persistence_sql('write', started)
        self.assertEqual(running_observations, [True])
        self.assertEqual(daemon.executed_sql_modes, ['write'])
        self.assertEqual(sum('/exec/' in p and p.endswith('/start') for _, p, _ in daemon.events), 1)

    def test_missing_or_non_null_prestart_exit_or_nonzero_pid_never_starts_exec(self):
        for defect in ['missing', 'zero', 'bool', 'nonzero', 'pid', 'running']:
            daemon = PersistenceDaemon()
            daemon.dispatch_cli()
            started = daemon.guard.healthy_instance()
            exchange = daemon.exchange
            def invalid(method, path, body=None):
                status, row = exchange(method, path, body)
                if '/exec/' in path and path.endswith('/json'):
                    if defect == 'missing':
                        row.pop('ExitCode')
                    elif defect == 'pid':
                        row['Pid'] = 321
                    elif defect == 'running':
                        row['Running'] = True
                    else:
                        row['ExitCode'] = {'zero': 0, 'bool': False, 'nonzero': 1}[defect]
                return status, row
            daemon.exchange = invalid
            with self.subTest(defect=defect), self.assertRaises(dev.Refusal) as caught:
                daemon.guard.persistence_sql('write', started)
            self.assertEqual(caught.exception.code, 'execution_invalid_exec')
            self.assertEqual(daemon.executed_sql_modes, [])

    def test_completed_missing_null_bool_and_nonzero_never_qualify(self):
        for defect in ['missing', 'null', 'bool', 'nonzero']:
            daemon = PersistenceDaemon()
            daemon.dispatch_cli()
            started = daemon.guard.healthy_instance()
            exchange = daemon.exchange
            def invalid(method, path, body=None):
                status, row = exchange(method, path, body)
                if '/exec/' in path and path.endswith('/json') and daemon.exec_started:
                    if defect == 'missing':
                        row.pop('ExitCode')
                    else:
                        row['ExitCode'] = {'null': None, 'bool': False, 'nonzero': 1}[defect]
                return status, row
            daemon.exchange = invalid
            with self.subTest(defect=defect), self.assertRaises(dev.Refusal) as caught:
                daemon.guard.persistence_sql('write', started)
            self.assertEqual(caught.exception.code, 'execution_sql_failed' if defect == 'nonzero' else 'execution_invalid_exec')
            self.assertEqual(daemon.executed_sql_modes, ['write'])
            self.assertFalse(daemon.guard.persistence_verified)
            daemon.guard.cleanup_execution()
            self.assertTrue(daemon.guard.cleaned)

class PersistenceReviewCoverage(unittest.TestCase):
    def test_failed_write_does_not_commit_simulated_marker(self):
        daemon = PersistenceDaemon()
        daemon.initialization_markers = False
        daemon.dispatch_cli()
        with self.assertRaises(dev.Refusal) as caught:
            daemon.guard.finish_execution()
        self.assertEqual(caught.exception.code, 'execution_sql_failed')
        self.assertIsNone(daemon.marker)
        self.assertEqual(daemon.executed_sql_modes, ['write'])
        self.assertEqual(daemon.creates, 1)
        self.assertFalse(daemon.guard.persistence_verified)
        daemon.guard.cleanup_execution()
        self.assertTrue(daemon.guard.cleaned)

    def test_final_schema_predicate_failure_cannot_qualify_and_cleanup_runs_once(self):
        daemon = PersistenceDaemon()
        exchange = daemon.exchange
        def missing_schema(method, path, body=None):
            if path.startswith('/v1.48/exec/') and path.endswith('/start') and daemon.sql_modes == ['write', 'schemas', 'verify', 'schemas']:
                daemon.initialization_markers = False
            return exchange(method, path, body)
        daemon.exchange = missing_schema
        daemon.dispatch_cli()
        with patch.object(dev, 'free_ports'), self.assertRaises(dev.Refusal) as caught:
            daemon.guard.finish_execution()
        self.assertEqual(caught.exception.code, 'execution_sql_failed')
        self.assertEqual(daemon.executed_sql_modes, ['write', 'schemas', 'verify', 'schemas'])
        self.assertFalse(daemon.guard.persistence_verified)
        self.assertFalse(daemon.guard.cleaned)
        daemon.guard.cleanup_execution()
        before = len(daemon.events)
        with self.assertRaises(dev.Refusal):
            daemon.guard.cleanup_execution()
        self.assertEqual(len(daemon.events), before)
        self.assertTrue(daemon.guard.cleaned)

    def test_reused_exec_id_refuses_before_second_start_without_repair(self):
        daemon = PersistenceDaemon()
        exchange = daemon.exchange
        first_id = []
        def reused(method, path, body=None):
            status, row = exchange(method, path, body)
            if path.endswith('/exec'):
                if first_id:
                    row['Id'] = first_id[0]
                else:
                    first_id.append(row['Id'])
            return status, row
        daemon.exchange = reused
        daemon.dispatch_cli()
        with self.assertRaises(dev.Refusal) as caught:
            daemon.guard.finish_execution()
        self.assertEqual(caught.exception.code, 'execution_invalid_exec')
        self.assertEqual(daemon.executed_sql_modes, ['write'])
        self.assertEqual(sum('/exec/' in p and p.endswith('/start') for _, p, _ in daemon.events), 1)
        self.assertFalse(daemon.guard.persistence_verified)
        daemon.guard.cleanup_execution()
        self.assertTrue(daemon.guard.cleaned)

    def test_finish_replay_after_success_or_sql_failure_never_dispatches_or_resets_budget(self):
        for successful in [False, True]:
            daemon = PersistenceDaemon()
            daemon.initialization_markers = successful
            daemon.dispatch_cli()
            with patch.object(dev, 'free_ports'):
                if successful:
                    daemon.guard.finish_execution()
                else:
                    with self.assertRaises(dev.Refusal):
                        daemon.guard.finish_execution()
            before, deadline = len(daemon.events), daemon.guard.deadline
            with self.subTest(successful=successful), self.assertRaises(dev.Refusal):
                daemon.guard.finish_execution()
            self.assertEqual(len(daemon.events), before)
            self.assertEqual(daemon.guard.deadline, deadline)
            if not successful:
                daemon.guard.cleanup_execution()

    def test_uncertain_post_delete_inspection_preserves_gap_without_replay(self):
        for defect in ['lost', 'malformed', 'non-404']:
            daemon = PersistenceDaemon()
            exchange = daemon.exchange
            removed = []
            def uncertain(method, path, body=None):
                result = exchange(method, path, body)
                if method == 'DELETE' and '/containers/' in path:
                    removed.append(True)
                elif removed and path == '/v1.48/containers/'+'a'*64+'/json':
                    if defect in ('lost', 'malformed'):
                        dev.refuse('docker', 'docker_response_invalid')
                    return 200, {}
                return result
            daemon.exchange = uncertain
            daemon.dispatch_cli()
            with self.subTest(defect=defect), self.assertRaises(dev.Refusal):
                daemon.guard.finish_execution()
            self.assertEqual(daemon.creates, 1)
            self.assertEqual(sum(m == 'DELETE' for m, _, _ in daemon.events), 1)
            self.assertFalse(daemon.guard.persistence_verified)
            self.assertFalse(daemon.guard.cleaned)
            self.assertIsNotNone(daemon.volume)
            before = len(daemon.events)
            with self.assertRaises(dev.Refusal):
                daemon.guard.finish_execution()
            with self.assertRaises(dev.Refusal):
                daemon.guard.cleanup_execution()
            self.assertEqual(len(daemon.events), before)

class PoststartAuthBoundary(unittest.TestCase):
    def prepared(self):
        daemon = OwnerDaemon()
        daemon.fixture.update(origins=['http://localhost:5188', 'http://localhost:55481'])
        daemon.guard.enable_auth_boundary()
        daemon.dispatch_cli()
        return daemon

    def job(self, f):
        auth = next(tag for tag in f['selection_plan'] if '/gotrue:' in tag)
        env = {'API_EXTERNAL_URL': 'http://localhost:55481/auth/v1', 'GOTRUE_LOG_LEVEL': 'error',
               'GOTRUE_DB_DRIVER': 'postgres',
               'GOTRUE_DB_DATABASE_URL': 'postgresql://supabase_auth_admin:postgres@supabase_db_'+f['project']+':5432/postgres',
               'GOTRUE_SITE_URL': 'http://localhost:5188',
               'GOTRUE_JWT_SECRET': 'super-secret-jwt-token-with-at-least-32-characters-long',
               'DOCKER_HOST': 'unix://'+f['workdir']+'/no-daemon.sock', 'DOCKER_CONFIG': f['workdir']+'/docker'}
        args = ['run', '--rm', '--network', f['network']['Id'], '--add-host', 'host.docker.internal:host-gateway']
        for key in list(env)[:6]:
            args += ['-e', key]
        args += ['--label', 'com.supabase.cli.project='+f['project'], '--label', 'com.docker.compose.project='+f['project'], auth, 'gotrue', 'migrate']
        return args, env

    def test_real_health_then_exact_refused_auth_without_job_dispatch(self):
        daemon = self.prepared()
        state = daemon.guard.poststart_health()
        self.assertEqual(state, {'Status': 'running', 'Running': True, 'Health': {'Status': 'healthy'}})
        daemon.guard.refuse_auth_job(*self.job(daemon.fixture), daemon.fixture)
        daemon.guard.finish_execution()
        self.assertTrue(daemon.guard.cleaned)
        self.assertTrue(daemon.guard.auth_job_refused)
        self.assertEqual(sum('/containers/create?' in path for _, path, _ in daemon.events), 1)

    def test_health_only_selects_current_safe_fields_and_keeps_start_identity(self):
        daemon = self.prepared()
        daemon.row['State']['Health'].update(Status='starting', Log=[{'Output': 'private'}])
        deadline = daemon.guard.deadline
        self.assertEqual(daemon.guard.poststart_health()['Health'], {'Status': 'starting'})
        daemon.row['State']['Health']['Status'] = 'healthy'
        daemon.guard.poststart_health()
        self.assertEqual(daemon.guard.deadline, deadline)
        daemon.row['State']['StartedAt'] = '2026-10-17T12:00:00.000000002Z'
        with self.assertRaises(dev.Refusal):
            daemon.guard.poststart_health()

    def test_changed_auth_profile_or_early_job_never_dispatches(self):
        for defect in ['early', 'argv', 'env', 'routing', 'image', 'network']:
            daemon = self.prepared()
            if defect != 'early':
                daemon.guard.poststart_health()
            args, env = self.job(daemon.fixture)
            if defect == 'argv': args += ['extra']
            if defect == 'env': env['GOTRUE_SITE_URL'] = 'foreign'
            if defect == 'routing': env['DOCKER_CONTEXT'] = 'foreign'
            if defect == 'image': args[-3] = 'foreign'
            if defect == 'network': args[3] = 'foreign'
            before = len(daemon.events)
            with self.subTest(defect=defect), self.assertRaises(dev.Refusal):
                daemon.guard.refuse_auth_job(args, env, daemon.fixture)
            self.assertFalse(daemon.guard.auth_job_refused)
            self.assertFalse(any(m != 'GET' for m, _, _ in daemon.events[before:]))

    def test_terminal_job_consumed_once_and_finish_needs_boundary(self):
        daemon = self.prepared()
        with self.assertRaises(dev.Refusal): daemon.guard.finish_execution()
        daemon.guard.poststart_health()
        daemon.guard.refuse_auth_job(*self.job(daemon.fixture), daemon.fixture)
        before = len(daemon.events)
        with self.assertRaises(dev.Refusal): daemon.guard.refuse_auth_job(*self.job(daemon.fixture), daemon.fixture)
        self.assertEqual(len(daemon.events), before)

    def test_auth_job_profile_rejection_matrix(self):
        import copy
        fixture = boundary_fixture()
        fixture['origins'] = ['http://localhost:5188', 'http://localhost:55481']
        original_args, original_env = self.job(fixture)
        # The independent pinned-source oracle above must pass before any fault.
        create_profile.validate_auth_job(original_args, fixture, original_env)
        cases = []
        public_keys = ['API_EXTERNAL_URL', 'GOTRUE_LOG_LEVEL', 'GOTRUE_DB_DRIVER',
                       'GOTRUE_DB_DATABASE_URL', 'GOTRUE_SITE_URL', 'GOTRUE_JWT_SECRET']
        for key in public_keys:
            changed = dict(original_env, **{key: 'changed-public-input'})
            cases.append(('changed-value-' + key, original_args, changed))
            missing = dict(original_env)
            missing.pop(key)
            cases.append(('missing-value-' + key, original_args, missing))
            index = original_args.index(key)
            args = original_args[:index-1] + original_args[index+1:]
            cases.append(('missing-env-option-' + key, args, original_env))
            args = list(original_args)
            args[index] += '=' + original_env[key]
            cases.append(('inline-env-value-' + key, args, original_env))
        first = original_args.index('API_EXTERNAL_URL') - 1
        args = list(original_args)
        args[first:first+4] = args[first+2:first+4] + args[first:first+2]
        cases.append(('reordered-env-options', args, original_env))
        cases.append(('extra-env-option', original_args[:first] + ['-e', 'EXTRA'] + original_args[first:],
                      dict(original_env, EXTRA='public-extra')))
        for label in ['com.supabase.cli.project=', 'com.docker.compose.project=']:
            index = next(i for i, value in enumerate(original_args) if value.startswith(label))
            args = list(original_args)
            args[index] = label + 'foreign-project'
            cases.append(('changed-label-' + label, args, original_env))
            cases.append(('missing-label-' + label, original_args[:index-1] + original_args[index+1:], original_env))
        for name, options in [('mount', ['-v', 'foreign:/data']), ('port', ['-p', '5432:5432']),
                              ('entrypoint', ['--entrypoint', 'sh'])]:
            cases.append(('forbidden-' + name, original_args[:-3] + options + original_args[-3:], original_env))
        for name, args, env in cases:
            before = copy.deepcopy((args, env, fixture))
            with self.subTest(defect=name), self.assertRaises(dev.Refusal) as caught:
                create_profile.validate_auth_job(args, fixture, env)
            self.assertEqual(caught.exception.code, 'unsafe_create')
            self.assertEqual((args, env, fixture), before)

    def test_malformed_health_at_poll_and_terminal_refuses_safely(self):
        for site in ['poll', 'terminal']:
            for malformed in [None, [], 'healthy', {}, {'Status': None}]:
                daemon = self.prepared()
                guard = daemon.guard
                if site == 'terminal':
                    guard.poststart_health()
                deadline = guard.deadline
                daemon.row['State']['Health'] = malformed
                before = len(daemon.events)
                with self.subTest(site=site, malformed=malformed):
                    with self.assertRaises(dev.Refusal) as caught:
                        if site == 'poll':
                            guard.poststart_health()
                        else:
                            guard.refuse_auth_job(*self.job(daemon.fixture), daemon.fixture)
                    self.assertEqual(caught.exception.code, 'execution_invalid_health')
                    self.assertEqual(guard.deadline, deadline)
                    self.assertFalse(guard.auth_job_refused)
                    self.assertFalse(any(method != 'GET' for method, _, _ in daemon.events[before:]))

    def test_poststart_identity_and_state_regressions_at_poll_and_terminal(self):
        changes = [('restart', {'StartedAt': '2026-10-17T12:00:00.000000002Z'}, 'execution_instance_changed'),
                   ('exited', {'Status': 'exited', 'Running': False, 'Pid': 0}, 'shutdown_invalid_state'),
                   ('dead', {'Dead': True}, 'shutdown_invalid_state'),
                   ('oom', {'OOMKilled': True}, 'shutdown_oom')]
        for site in ['first-poll', 'terminal']:
            for defect, fields, code in changes:
                daemon = self.prepared()
                guard = daemon.guard
                if site == 'terminal': guard.poststart_health()
                deadline = guard.deadline
                daemon.row['State'].update(fields)
                before = len(daemon.events)
                with self.subTest(site=site, defect=defect), self.assertRaises(dev.Refusal) as caught:
                    if site == 'first-poll': guard.poststart_health()
                    else: guard.refuse_auth_job(*self.job(daemon.fixture), daemon.fixture)
                self.assertEqual(caught.exception.code, code)
                self.assertEqual(guard.deadline, deadline)
                self.assertFalse(guard.auth_job_refused)
                self.assertFalse(any(method != 'GET' for method, _, _ in daemon.events[before:]))

    def test_not_ready_poll_clears_admission_and_terminal_rechecks_last_healthy(self):
        for reported in [True, False]:
            for status in ['starting', 'unhealthy']:
                daemon = self.prepared()
                guard = daemon.guard
                guard.poststart_health()
                deadline = guard.deadline
                daemon.row['State']['Health']['Status'] = status
                if reported:
                    self.assertEqual(guard.poststart_health()['Health']['Status'], status)
                    self.assertFalse(guard.poststart_healthy)
                before = len(daemon.events)
                with self.subTest(reported=reported, status=status), self.assertRaises(dev.Refusal) as caught:
                    guard.refuse_auth_job(*self.job(daemon.fixture), daemon.fixture)
                self.assertEqual(caught.exception.code, 'invalid_owner_handoff' if reported else 'execution_invalid_health')
                self.assertEqual(guard.deadline, deadline)
                self.assertFalse(guard.auth_job_refused)
                self.assertFalse(any(method != 'GET' for method, _, _ in daemon.events[before:]))

    def test_failed_profile_consumes_terminal_before_valid_retry(self):
        daemon = self.prepared()
        guard = daemon.guard
        guard.poststart_health()
        deadline, before = guard.deadline, len(daemon.events)
        args, env = self.job(daemon.fixture)
        with self.assertRaises(dev.Refusal) as caught:
            guard.refuse_auth_job(args + ['extra'], env, daemon.fixture)
        self.assertEqual(caught.exception.code, 'unsafe_create')
        self.assertTrue(guard.auth_terminal_attempted)
        with self.assertRaises(dev.Refusal) as caught:
            guard.refuse_auth_job(args, env, daemon.fixture)
        self.assertEqual(caught.exception.code, 'invalid_owner_handoff')
        self.assertEqual(guard.deadline, deadline)
        self.assertEqual(len(daemon.events), before)
        self.assertFalse(guard.auth_job_refused)

class PoststartEnvelope(unittest.TestCase):
    def inputs(self, phase):
        import startup
        fixture, events, _ = ExecutionEnvelope().inputs(4)
        fixture.update(auth_boundary=True, origins=['http://localhost:5188', 'http://localhost:55481'])
        events += [{'kind': 'postgres_start_acknowledged'}]
        routing = {key: expected_environment(fixture)[key] for key in ('DOCKER_HOST', 'DOCKER_CONFIG')}
        if phase == 'poststart_health':
            args = ['container', 'inspect', 'supabase_db_'+fixture['project'], '--format', '{{json .State}}']
        else:
            events += [{'kind': 'postgres_health', 'health': 'healthy'}]
            auth = next(tag for tag in fixture['images'] if '/gotrue:' in tag)
            args = ['image', 'inspect', auth]
            if phase == 'auth_job':
                events += [{'kind': 'auth_image_inspect'}]
                args, routing = PoststartAuthBoundary().job(fixture)
        return fixture, events, {'token': 'a'*32, 'phase': phase, 'args': args, 'environment': routing}

    def test_exact_phase_token_operands_environment_and_prefix_required(self):
        import copy, json, startup
        for phase in ['poststart_health', 'poststart_image', 'auth_job']:
            fixture, events, request = self.inputs(phase)
            self.assertEqual(startup.validate_poststart_handoff(json.dumps(request).encode(), 'a'*32, fixture, events), request)
            for defect in ['token', 'phase', 'args', 'environment', 'extra', 'prefix', 'duplicate', 'malformed']:
                changed = copy.deepcopy(request)
                prefix = copy.deepcopy(events)
                if defect in ['token', 'phase']: changed[defect] = 'foreign'
                if defect == 'args': changed['args'].append('extra')
                if defect == 'environment': changed['environment']['DOCKER_CONTEXT'] = 'foreign'
                if defect == 'extra': changed['extra'] = True
                if defect == 'prefix': prefix[0]['kind'] = 'foreign'
                if defect == 'duplicate': prefix.append({'kind': 'auth_image_inspect'})
                raw = b'{' if defect == 'malformed' else json.dumps(changed).encode()
                with self.subTest(phase=phase, defect=defect), self.assertRaises(dev.Refusal):
                    startup.validate_poststart_handoff(raw, 'a'*32, fixture, prefix)

    def test_job_needs_healthy_then_single_current_auth_image_observation(self):
        import json, startup
        fixture, events, request = self.inputs('auth_job')
        for prefix in [events[:-1], events[:-2], events + [{'kind': 'auth_image_inspect'}]]:
            with self.assertRaises(dev.Refusal):
                startup.validate_poststart_handoff(json.dumps(request).encode(), 'a'*32, fixture, prefix)
        events[-2]['health'] = 'unhealthy'
        with self.assertRaises(dev.Refusal):
            startup.validate_poststart_handoff(json.dumps(request).encode(), 'a'*32, fixture, events)

    def test_health_lost_malformed_and_oversized_replies_refuse(self):
        import startup, struct, os, json
        fixture, _, request = self.inputs('poststart_health')
        env = dict(request['environment'], ENV_PRIVATE_OWNER_TOKEN='a'*32, ENV_PRIVATE_OWNER_PID='12345')
        valid = json.dumps({'Status': 'running', 'Running': True, 'Health': {'Status': 'healthy'}}).encode()
        for reply in [b'', b'OK\n', b'{}', b'x'*513, valid + b' '*(513-len(valid)),
                      json.dumps({'Status': 'running', 'Running': True, 'Health': {'Status': 'healthy', 'Log': []}}).encode()]:
            peer = Mock()
            peer.getsockopt.return_value = struct.pack('3i', 12345, os.getuid(), 0)
            peer.recv.side_effect = [reply, b'']
            context = Mock()
            context.__enter__ = Mock(return_value=peer)
            context.__exit__ = Mock(return_value=False)
            with self.subTest(reply=reply[:20]), patch.object(startup.socket, 'socket', return_value=context), self.assertRaises(dev.Refusal):
                startup.owner_handoff(fixture, 'poststart_health', request['args'], env)

class DepartedPrivatePeer(unittest.TestCase):
    def test_peer_departure_during_proc_parent_check_is_safe_refusal(self):
        import startup, struct, os
        guard = Mock()
        guard._second_fixture = None
        guard.execution = False
        guard.remaining.return_value = 1
        listener, peer, selector, process = Mock(), Mock(), Mock(), Mock()
        process.pid = 12345
        listener.accept.return_value = (peer, None)
        peer.getsockopt.return_value = struct.pack('3i', 23456, os.getuid(), 0)
        peer.__enter__ = Mock(return_value=peer)
        peer.__exit__ = Mock(return_value=False)
        selector.get_map.return_value = {1: None, 2: None}
        selector.select.return_value = [(Mock(fileobj=listener), None)]
        socket_context = Mock()
        socket_context.__enter__ = Mock(return_value=listener)
        socket_context.__exit__ = Mock(return_value=False)
        selector_context = Mock()
        selector_context.__enter__ = Mock(return_value=selector)
        selector_context.__exit__ = Mock(return_value=False)
        with patch.object(startup.socket, 'socket', return_value=socket_context), \
                patch.object(startup.selectors, 'DefaultSelector', return_value=selector_context), \
                patch.object(startup.subprocess, 'Popen', return_value=process), \
                patch.object(startup.os, 'set_blocking'), patch.object(startup.os, 'killpg') as kill, \
                patch.object(Path, 'chmod'), patch.object(Path, 'lstat'), \
                patch.object(Path, 'read_text', side_effect=FileNotFoundError()), self.assertRaises(dev.Refusal) as caught:
            startup.guarded_fixture_command(['selected-cli'], Path('/private'), {}, guard)
        self.assertEqual(caught.exception.code, 'invalid_owner_handoff')
        kill.assert_called_once()
        listener.accept.assert_called_once()


class FragmentedHealthReply(unittest.TestCase):
    def test_size_respecting_fragments_accept_exact_limit_and_reject_one_extra(self):
        import json, os, struct, startup
        fixture, _, request = PoststartEnvelope().inputs('poststart_health')
        env = dict(request['environment'], ENV_PRIVATE_OWNER_TOKEN='a'*32, ENV_PRIVATE_OWNER_PID='12345')
        state = {'Status': 'running', 'Running': True, 'Health': {'Status': 'healthy'}}
        valid = json.dumps(state).encode()
        for length in [512, 513]:
            for fragment in [1, 17, 512]:
                remaining = bytearray(valid + b' '*(length-len(valid)))
                sizes = []
                def recv(size):
                    self.assertGreater(size, 0)
                    sizes.append(size)
                    take = min(size, fragment, len(remaining))
                    chunk = bytes(remaining[:take])
                    del remaining[:take]
                    return chunk
                peer = Mock()
                peer.recv.side_effect = recv
                peer.getsockopt.return_value = struct.pack('3i', 12345, os.getuid(), 0)
                context = Mock()
                context.__enter__ = Mock(return_value=peer)
                context.__exit__ = Mock(return_value=False)
                with self.subTest(length=length, fragment=fragment), patch.object(startup.socket, 'socket', return_value=context):
                    if length == 512:
                        self.assertEqual(startup.owner_handoff(fixture, 'poststart_health', request['args'], env), state)
                    else:
                        with self.assertRaises(dev.Refusal) as caught:
                            startup.owner_handoff(fixture, 'poststart_health', request['args'], env)
                        self.assertEqual(caught.exception.code, 'invalid_owner_handoff')
                self.assertFalse(remaining)
                self.assertLessEqual(max(sizes), 513)
