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
