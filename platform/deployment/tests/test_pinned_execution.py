"""No-socket acceptance of the retained owner's closed real dispatch."""
import sys
from pathlib import Path
import unittest
import json
import itertools
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

class AuthMigrationExecution(unittest.TestCase):
    def prepared(self):
        daemon = PoststartAuthBoundary().prepared()
        guard = daemon.guard
        guard.auth_migration = True
        guard.poststart_health()
        return daemon

    def test_actual_job_requires_admission_then_terminated_cli_and_preserves_budget(self):
        daemon = self.prepared()
        args, env = PoststartAuthBoundary().job(daemon.fixture)
        deadline = daemon.guard.deadline
        daemon.guard.admit_auth_job(args, env, daemon.fixture)
        self.assertFalse(daemon.guard.auth_job_dispatched)
        with self.assertRaises(dev.Refusal): daemon.guard.execute_auth_job()
        self.assertEqual(daemon.guard.deadline, deadline)
        self.assertEqual(sum('/containers/create?' in p for _, p, _ in daemon.events), 1)

class AuthJobDaemon(OwnerDaemon):
    """Independent detached job fixture; PG volume-use list never contains job."""
    def __init__(self):
        super().__init__()
        self.fixture.update(origins=['http://localhost:5188', 'http://localhost:55481'])
        self.guard.enable_auth_migration()
        self.job_row = None
        self.job_fault = None
        self.kong_config = json.loads((dev.ROOT / 'platform/deployment/fixtures/supabase-kong-image-api-config.json').read_text())
        self.auth_config = {'User': 'supabase', 'WorkingDir': '/', 'ArgsEscaped': True, 'Cmd': ['auth'],
                'Env': ['PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                        'GOTRUE_DB_MIGRATIONS_PATH=/usr/local/etc/auth/migrations'],
                'AttachStderr': False, 'AttachStdin': False, 'AttachStdout': False,
                'Domainname': '', 'Entrypoint': None, 'Hostname': '', 'Image': '',
                'Labels': None, 'OnBuild': None, 'OpenStdin': False, 'StdinOnce': False,
                'Tty': False, 'Volumes': None}
        self.dispatch_cli()
        self.guard.poststart_health()
        args, env = PoststartAuthBoundary().job(self.fixture)
        self.guard.admit_auth_job(args, env, self.fixture)
        self.guard.auth_cli_terminated = True

    def exchange(self, method, path, body=None):
        if '/images/public.ecr.aws/supabase/kong@' in path:
            status, row = super().exchange(method, path, body)
            row['Config'] = self.copy(self.kong_config)
            return status, row
        if '/images/public.ecr.aws/supabase/gotrue@' in path:
            status, row = super().exchange(method, path, body)
            row['Config'] = self.copy(self.auth_config)
            return status, row
        if ('supabase_auth_migrate_' in path or '/containers/' + 'c'*64 in path):
            self.current()
            self.events.append((method, path, self.copy(body)))
            if self.job_fault:
                result = self.job_fault(method, path, body)
                if result is not None: return result
            if '/create?' in path:
                self.job_row = {'Id': 'c'*64, 'Name': '/supabase_auth_migrate_' + self.fixture['project'],
                        'Image': self.images[body['Image']]['Id'], 'Path': 'gotrue', 'Args': ['migrate'], 'Config': {**self.copy(self.auth_config),
                            'Image': body['Image'], 'Cmd': ['gotrue', 'migrate'], 'ArgsEscaped': False,
                            'Env': body['Env'] + self.auth_config['Env'], 'Labels': self.copy(body['Labels'])},
                        'HostConfig': {**self.copy(body['HostConfig']), 'IpcMode': 'private'}, 'Mounts': [], 'RestartCount': 0, 'Platform': 'linux',
                        'NetworkSettings': {'Networks': {self.network['Name']: {'NetworkID': self.network['Id']}}},
                        'State': {'Status': 'created', 'Running': False, 'Paused': False, 'Restarting': False, 'Pid': 0, 'ExitCode': 0,
                                  'OOMKilled': False, 'Dead': False, 'Error': '',
                                  'StartedAt': '0001-01-01T00:00:00Z', 'FinishedAt': '0001-01-01T00:00:00Z'}}
                self.job_row['Config'].pop('ArgsEscaped')
                return 201, {'Id': 'c'*64, 'Warnings': []}
            if method == 'DELETE':
                self.job_row = None
                self.network['Containers'].pop('c'*64, None)
                return 204, None
            if path.endswith('/start'):
                self.job_row['State'].update(Status='exited', ExitCode=0,
                        StartedAt='2026-10-17T12:00:00.000000002Z', FinishedAt='2026-10-17T12:00:01.000000002Z')
                return 204, None
            return (200, self.copy(self.job_row)) if self.job_row else (404, None)
        return super().exchange(method, path, body)


class AuthJobExecutionMatrix(unittest.TestCase):
    def test_fast_zero_exit_then_job_disposal_precedes_pg_shutdown_and_disposal(self):
        d = AuthJobDaemon()
        deadline = d.guard.deadline
        d.guard.execute_auth_job()
        self.assertEqual(d.guard.deadline, deadline)
        self.assertTrue(d.guard.auth_job_exit_verified)
        self.assertTrue(d.guard.auth_job_disposed)
        d.guard.finish_execution()
        self.assertTrue(d.guard.cleaned)
        writes = [(m,p) for m,p,_ in d.events if m != 'GET']
        self.assertLess(writes.index(('DELETE', '/v1.48/containers/'+'c'*64+'?force=false')),
                        writes.index(('POST', '/v1.48/containers/'+'a'*64+'/stop?t=5')))
        self.assertEqual(sum(m == 'POST' and 'supabase_auth_migrate_' in p for m,p in writes), 1)
        with self.assertRaises(dev.Refusal): d.guard.execute_auth_job()

    def test_changed_image_defaults_refuse_before_create(self):
        for key, value in [('Entrypoint', ['sh']), ('Volumes', {'/data': {}}), ('User', 'root'),
                           ('Env', ['PATH=/evil']), ('WorkingDir', '/tmp'), ('Healthcheck', {'Test':['CMD','evil']}), ('OnBuild', ['RUN evil'])]:
            with self.subTest(key=key):
                d = AuthJobDaemon()
                d.auth_config[key] = value
                with self.assertRaises(dev.Refusal): d.guard.execute_auth_job()
                self.assertFalse(any(m=='POST' and 'auth_migrate_' in p for m,p,_ in d.events))
                self.assertTrue(d.guard.auth_job_create_attempted)

    def test_invalid_effective_configuration_or_state_permanently_revokes_cleanup(self):
        defects = [lambda r: r['Config'].update(User='root'), lambda r: r['Config'].update(Entrypoint=['sh']),
                lambda r: r['Config']['Env'].append('LD_PRELOAD=/evil'), lambda r: r.update(Mounts=[{'Type':'volume'}]),
                lambda r: r['HostConfig'].update(PortBindings={'80/tcp':[]}), lambda r:r['HostConfig'].update(Privileged=True),
                lambda r: r['State'].update(OOMKilled=True), lambda r:r['State'].update(Dead=True),
                lambda r: r['State'].update(ExitCode=False), lambda r:r.update(RestartCount=1),
                lambda r: r['State'].update(Status='dead'), lambda r:r['State'].update(Pid=-1),
                lambda r:r['NetworkSettings']['Networks'].update(foreign={})]
        for defect in defects:
            with self.subTest(defect=defect):
                d=AuthJobDaemon()
                def fault(method,path,body):
                    if method=='GET' and d.job_row is not None:
                        defect(d.job_row)
                    return None
                d.job_fault=fault
                with self.assertRaises(dev.Refusal): d.guard.execute_auth_job()
                self.assertTrue(d.guard.ownership_lost)
                count=len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
                self.assertEqual(len(d.events), count)

    def test_nonzero_exit_does_not_claim_success_but_cleans_owned_job_first(self):
        d=AuthJobDaemon()
        def fault(method,path,body):
            if method=='GET' and d.job_row and d.job_row['State']['Status']=='exited':
                d.job_row['State']['ExitCode']=1
        d.job_fault=fault
        with self.assertRaises(dev.Refusal) as error: d.guard.execute_auth_job()
        self.assertEqual(error.exception.code, 'execution_auth_job_failed')
        self.assertFalse(d.guard.auth_job_exit_verified)
        d.guard.cleanup_execution()
        self.assertTrue(d.guard.cleaned)
        deletes=[p for m,p,_ in d.events if m=='DELETE' and '/containers/' in p]
        self.assertEqual(deletes, ['/v1.48/containers/'+'c'*64+'?force=true', '/v1.48/containers/'+'a'*64+'?force=true'])

    def test_uncertain_create_start_delete_never_replays_and_preserves_unknowns(self):
        for stage in ('create','start','delete'):
            with self.subTest(stage=stage):
                d=AuthJobDaemon()
                def fault(method,path,body):
                    if stage=='create' and method=='POST' and '/create?' in path: return 201, {}
                    if stage=='start' and path.endswith('/start'): return 500,None
                    if stage=='delete' and method=='DELETE': return 500,None
                d.job_fault=fault
                with self.assertRaises(dev.Refusal): d.guard.execute_auth_job()
                count=len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.execute_auth_job()
                self.assertEqual(len(d.events),count)
                if stage in ('create','delete'):
                    with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
                    self.assertFalse(d.guard.cleaned)
                else:
                    d.job_fault=None
                    d.guard.cleanup_execution()
                    self.assertTrue(d.guard.cleaned)

    def test_transport_is_exact_persistent_job_route_and_request(self):
        d=AuthJobDaemon()
        request=d.guard.auth_job_input
        dev._docker_request(request['method'], request['path'], request['body'], True)
        for mutation in ('mount','port','env','image','auto','name','platform','persist'):
            r=d.copy(request)
            persistent=True
            if mutation=='mount':r['body']['HostConfig']['Binds']=['x:/data']
            if mutation=='port':r['body']['HostConfig']['PortBindings']={'80/tcp':[]}
            if mutation=='env':r['body']['Env'][1]='GOTRUE_LOG_LEVEL=debug'
            if mutation=='image':r['body']['Image']='public.ecr.aws/supabase/gotrue:latest'
            if mutation=='auto':r['body']['HostConfig']['AutoRemove']=True
            if mutation=='name':r['path']=r['path'].replace('auth_migrate_', 'auth_')
            if mutation=='platform':r['path']=r['path'].replace('amd64','arm64')
            if mutation=='persist':persistent=False
            with self.subTest(mutation=mutation), self.assertRaises(dev.Refusal):
                dev._docker_request(r['method'],r['path'],r['body'],persistent)

class AuthJobCustodyAndUncertainty(unittest.TestCase):
    def test_changed_pg_instance_health_bridge_and_volume_reference_refuse_before_job_create(self):
        for defect in ('instance', 'health', 'bridge', 'volume', 'custody'):
            with self.subTest(defect=defect):
                d=AuthJobDaemon()
                if defect=='instance':d.row['State']['StartedAt']='2026-10-17T12:00:00.000000003Z'
                if defect=='health':d.row['State']['Health']['Status']='unhealthy'
                if defect=='bridge':d.network['Containers']['d'*64]={}
                if defect=='volume':
                    original=d.exchange
                    def exchange(method,path,body=None):
                        if '/containers/json?' in path:return 200,[{'Id':'a'*64},{'Id':'c'*64}]
                        return original(method,path,body)
                    d.exchange=exchange
                if defect=='custody':d.guard._current=lambda: dev.refuse('startup','fixture_changed')
                with self.assertRaises(dev.Refusal):d.guard.execute_auth_job()
                self.assertFalse(any(m=='POST' and 'auth_migrate_' in p for m,p,_ in d.events))

    def test_interrupted_create_preserves_ambiguity_without_pg_mutation(self):
        for exception in (KeyboardInterrupt(), dev.Refusal('docker','docker_response_invalid')):
            with self.subTest(exception=type(exception).__name__):
                d=AuthJobDaemon()
                def fault(method,path,body):
                    if method=='POST' and '/create?' in path:raise exception
                d.job_fault=fault
                with self.assertRaises(type(exception)):d.guard.execute_auth_job()
                self.assertTrue(d.guard.auth_job_creation_uncertain)
                count=len(d.events)
                with self.assertRaises(dev.Refusal):d.guard.cleanup_execution()
                self.assertEqual(len(d.events),count)

    def test_running_job_timeout_uses_only_one_final_cleanup_budget(self):
        d=AuthJobDaemon()
        original=d.exchange
        def exchange(method,path,body=None):
            result=original(method,path,body)
            if path.endswith('/start') and 'c'*64 in path:
                d.job_row['State'].update(Status='running',Running=True,Pid=456,FinishedAt='0001-01-01T00:00:00Z')
            return result
        d.exchange=exchange
        with patch.object(d.guard,'remaining',side_effect=dev.Refusal('docker','docker_timeout')):
            with self.assertRaises(dev.Refusal) as error:d.guard.execute_auth_job()
        self.assertEqual(error.exception.code,'docker_timeout')
        self.assertFalse(d.guard.auth_job_exit_verified)
        d.guard.cleanup_execution()
        self.assertTrue(d.guard.cleaned)
        count=len(d.events)
        with self.assertRaises(dev.Refusal):d.guard.cleanup_execution()
        self.assertEqual(len(d.events),count)

    def test_timestamp_change_malformed_state_and_restarted_instance_refuse(self):
        for key,value in [('StartedAt','invalid'),('FinishedAt','invalid'),('Running',1),('OOMKilled',0)]:
            with self.subTest(key=key):
                d=AuthJobDaemon()
                def fault(method,path,body):
                    if method=='GET' and d.job_row and d.job_row['State']['Status']=='exited':
                        d.job_row['State'][key]=value
                d.job_fault=fault
                with self.assertRaises(dev.Refusal):d.guard.execute_auth_job()
                self.assertFalse(d.guard.auth_job_exit_verified)
                self.assertTrue(d.guard.ownership_lost)

class AuthJobReviewBoundaries(unittest.TestCase):
    def test_malformed_pg_health_refuses_before_job_mutation(self):
        for value in (None, [], 'healthy'):
            with self.subTest(value=value):
                d=AuthJobDaemon()
                d.row['State']['Health']=value
                with self.assertRaises(dev.Refusal):d.guard.execute_auth_job()
                self.assertFalse(any(m=='POST' and 'auth_migrate_' in p for m,p,_ in d.events))

    def test_started_job_needs_current_bridge_attachment(self):
        d=AuthJobDaemon()
        def fault(method,path,body):
            if method=='GET' and d.job_row and d.job_row['State']['Status']=='exited':
                d.job_row['NetworkSettings']['Networks'][d.network['Name']]['NetworkID']=''
        d.job_fault=fault
        with self.assertRaises(dev.Refusal):d.guard.execute_auth_job()
        self.assertFalse(d.guard.auth_job_exit_verified)

    def test_job_finish_timestamp_must_follow_start(self):
        d=AuthJobDaemon()
        def fault(method,path,body):
            if method=='GET' and d.job_row and d.job_row['State']['Status']=='exited':
                d.job_row['State']['FinishedAt']=d.job_row['State']['StartedAt']
        d.job_fault=fault
        with self.assertRaises(dev.Refusal):d.guard.execute_auth_job()
        self.assertFalse(d.guard.auth_job_exit_verified)

class AuthJobMalformedImageResponse(unittest.TestCase):
    def test_nonobject_image_response_refuses_before_job_creation(self):
        for image in (None, [], 'invalid', False):
            with self.subTest(image=image):
                d = AuthJobDaemon()
                original = d.exchange
                def exchange(method, path, body=None):
                    if '/images/public.ecr.aws/supabase/gotrue@' in path:
                        return 200, image
                    return original(method, path, body)
                d.exchange = exchange
                with patch.object(resources.daemon_images, 'observe_session', return_value=d.images), self.assertRaises(dev.Refusal) as error:
                    d.guard.execute_auth_job()
                self.assertEqual(error.exception.code, 'execution_image_changed')
                self.assertFalse(any(m == 'POST' and 'auth_migrate_' in p for m, p, _ in d.events))

class AuthJobInspectDeleteUncertainty(unittest.TestCase):
    def test_lost_or_malformed_job_inspect_never_replays_or_disposes_unproven_job(self):
        for response in (None, [], {}, 'invalid', 'lost', 'closed'):
            with self.subTest(response=response):
                d = AuthJobDaemon()
                def fault(method, path, body):
                    if method == 'GET' and d.job_row is not None:
                        if response in ('lost', 'closed'):
                            d.closed = True
                            dev.refuse('docker', 'docker_response_invalid')
                        return 200, response
                d.job_fault = fault
                with self.assertRaises(dev.Refusal):
                    d.guard.execute_auth_job()
                self.assertFalse(d.guard.auth_job_exit_verified)
                self.assertFalse(d.guard.auth_job_disposed)
                count = len(d.events)
                with self.assertRaises(dev.Refusal):
                    d.guard.execute_auth_job()
                with self.assertRaises(dev.Refusal):
                    d.guard.cleanup_execution()
                self.assertEqual(len(d.events), count)
                self.assertFalse(any(method == 'DELETE' for method, _, _ in d.events))

    def test_lost_delete_ack_or_missing_absence_proof_preserves_unresolved_resources(self):
        for response in ('lost_ack', 'bad_ack', 'lost_absence', 'null_absence', 'present_absence'):
            with self.subTest(response=response):
                d = AuthJobDaemon()
                attempted = False
                def fault(method, path, body):
                    nonlocal attempted
                    if method == 'DELETE':
                        attempted = True
                        if response == 'lost_ack':
                            d.closed = True
                            dev.refuse('docker', 'docker_response_invalid')
                        if response == 'bad_ack':
                            return 200, {'unexpected': True}
                    elif method == 'GET' and attempted:
                        if response == 'lost_absence':
                            d.closed = True
                            dev.refuse('docker', 'docker_response_invalid')
                        if response == 'null_absence':
                            return 200, None
                        if response == 'present_absence':
                            return 200, {'Id': 'c' * 64}
                d.job_fault = fault
                with self.assertRaises(dev.Refusal):
                    d.guard.execute_auth_job()
                self.assertTrue(d.guard.auth_job_exit_verified)
                self.assertFalse(d.guard.auth_job_disposed)
                self.assertTrue(d.guard.auth_job_delete_attempted)
                self.assertEqual(d.guard.auth_job_id, 'c' * 64)
                count = len(d.events)
                with self.assertRaises(dev.Refusal):
                    d.guard.execute_auth_job()
                with self.assertRaises(dev.Refusal):
                    d.guard.cleanup_execution()
                self.assertEqual(len(d.events), count)
                self.assertEqual(sum(method == 'DELETE' for method, _, _ in d.events), 1)
                self.assertIsNotNone(d.row)
                self.assertIsNotNone(d.volume)
                self.assertIsNotNone(d.network)

class AuthJobActualImageApiDefaults(unittest.TestCase):
    def test_exact_api_defaults_accepted_and_changed_or_missing_defaults_refused(self):
        d = AuthJobDaemon()
        create_profile.validate_auth_image_config(d.auth_config)
        mutations = [('AttachStderr', True), ('AttachStdin', True), ('AttachStdout', True),
                ('Domainname', 'foreign'), ('Entrypoint', ['sh']), ('Hostname', 'foreign'),
                ('Image', 'foreign'), ('Labels', {}), ('OnBuild', []), ('OpenStdin', True),
                ('StdinOnce', True), ('Tty', True), ('Volumes', {}),
                ('AttachStderr', 0), ('Unknown', None)]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                config = d.copy(d.auth_config)
                config[key] = value
                with self.assertRaises(dev.Refusal):
                    create_profile.validate_auth_image_config(config)
        for key in d.auth_config:
            with self.subTest(missing=key):
                config = d.copy(d.auth_config)
                del config[key]
                with self.assertRaises(dev.Refusal):
                    create_profile.validate_auth_image_config(config)

class AuthJobEffectiveDockerMerge(unittest.TestCase):
    def test_effective_config_requires_false_argsescaped_and_supplied_first_env(self):
        for mutation in ('args_true', 'args_int', 'args_null', 'args_string', 'env_image_first', 'env_reordered', 'env_missing', 'env_extra', 'user', 'workingdir'):
            with self.subTest(mutation=mutation):
                d = AuthJobDaemon()
                def fault(method, path, body):
                    if method == 'GET' and d.job_row is not None:
                        config = d.job_row['Config']
                        if mutation == 'args_true': config['ArgsEscaped'] = True
                        if mutation == 'args_int': config['ArgsEscaped'] = 0
                        if mutation == 'args_null': config['ArgsEscaped'] = None
                        if mutation == 'args_string': config['ArgsEscaped'] = 'false'
                        if mutation == 'env_image_first': config['Env'] = config['Env'][-2:] + config['Env'][:-2]
                        if mutation == 'env_reordered': config['Env'] = list(reversed(config['Env']))
                        if mutation == 'env_missing': config['Env'] = config['Env'][:-1]
                        if mutation == 'env_extra': config['Env'] = config['Env'] + ['EXTRA=unexpected']
                        if mutation == 'user': config['User'] = 'root'
                        if mutation == 'workingdir': config['WorkingDir'] = '/tmp'
                d.job_fault = fault
                with self.assertRaises(dev.Refusal):
                    d.guard.execute_auth_job()
                self.assertTrue(d.guard.ownership_lost)
                self.assertFalse(d.guard.auth_job_dispatched)
                self.assertFalse(d.guard.auth_job_exit_verified)
                self.assertFalse(any(path.endswith('/start') and 'c' * 64 in path for _, path, _ in d.events))


class AuthJobArgsEscapedApiNormalization(unittest.TestCase):
    def test_omitted_and_explicit_false_effective_argsescaped_are_valid(self):
        for present in (False, True):
            with self.subTest(present=present):
                d = AuthJobDaemon()
                def fault(method, path, body):
                    if method == 'GET' and d.job_row is not None and present:
                        d.job_row['Config']['ArgsEscaped'] = False
                d.job_fault = fault
                d.guard.execute_auth_job()
                self.assertTrue(d.guard.auth_job_exit_verified)
                self.assertTrue(d.guard.auth_job_disposed)
                self.assertNotIn('ArgsEscaped', d.guard.auth_job_input['body'])
                self.assertIs(d.auth_config['ArgsEscaped'], True)

class AuthJobFinalReview(unittest.TestCase):
    def assert_mutation_refused(self, mutate):
        d = AuthJobDaemon()
        def fault(method, path, body):
            if method == 'GET' and d.job_row is not None:
                mutate(d.job_row)
        d.job_fault = fault
        with self.assertRaises(dev.Refusal): d.guard.execute_auth_job()
        self.assertTrue(d.guard.ownership_lost)
        self.assertFalse(d.guard.auth_job_disposed)
        self.assertFalse(any(m == 'DELETE' for m, _, _ in d.events))

    def test_effective_interactive_flags_require_typed_default_false(self):
        for key in ('Tty', 'OpenStdin', 'StdinOnce', 'AttachStdin', 'AttachStdout', 'AttachStderr'):
            for value in (True, None, 0, 1, 'false', [], {}):
                with self.subTest(key=key, value=value):
                    self.assert_mutation_refused(lambda row: row['Config'].update({key: value}))

    def test_effective_interactive_flags_allow_omitted_or_typed_false(self):
        for omitted in (False, True):
            with self.subTest(omitted=omitted):
                d = AuthJobDaemon()
                def fault(method, path, body):
                    if method == 'GET' and d.job_row is not None:
                        for key in ('Tty', 'OpenStdin', 'StdinOnce', 'AttachStdin', 'AttachStdout', 'AttachStderr'):
                            if omitted: d.job_row['Config'].pop(key, None)
                            else: d.job_row['Config'][key] = False
                d.job_fault = fault
                d.guard.execute_auth_job()
                self.assertTrue(d.guard.auth_job_exit_verified)
                self.assertTrue(d.guard.auth_job_disposed)

    def test_cgroup_namespace_request_and_effective_private_are_required(self):
        d = AuthJobDaemon()
        self.assertEqual(d.guard.auth_job_input['body']['HostConfig'].get('CgroupnsMode'), 'private')
        for value in ('host', None, False, 0, [], {}):
            with self.subTest(value=value):
                self.assert_mutation_refused(lambda row: row['HostConfig'].update(CgroupnsMode=value))
        self.assert_mutation_refused(lambda row: row['HostConfig'].pop('CgroupnsMode', None))
        for value in ('host', None, False):
            request = d.copy(d.guard.auth_job_input)
            request['body']['HostConfig']['CgroupnsMode'] = value
            with self.subTest(transport=value), self.assertRaises(dev.Refusal):
                dev._docker_request(request['method'], request['path'], request['body'], True)
        request = d.copy(d.guard.auth_job_input)
        del request['body']['HostConfig']['CgroupnsMode']
        with self.assertRaises(dev.Refusal):
            dev._docker_request(request['method'], request['path'], request['body'], True)

    def test_top_level_command_must_match_exact_typed_gotrue_migrate(self):
        for key, value in [('Path', 'sh'), ('Path', None), ('Path', ['gotrue']),
                           ('Args', ['-c', 'false']), ('Args', 'migrate'), ('Args', [1]), ('Args', None)]:
            with self.subTest(key=key, value=value):
                self.assert_mutation_refused(lambda row: row.update({key: value}))
        for key in ('Path', 'Args'):
            self.assert_mutation_refused(lambda row: row.pop(key))

    def test_paused_or_restarting_or_malformed_state_cannot_qualify(self):
        for key in ('Paused', 'Restarting'):
            for value in (True, None, 0, 1, 'false', []):
                with self.subTest(key=key, value=value):
                    def mutate(row):
                        if row['State']['Status'] == 'exited': row['State'][key] = value
                    self.assert_mutation_refused(mutate)
            self.assert_mutation_refused(lambda row: row['State'].pop(key, None))

    def test_predelete_ownership_timeout_leaves_delete_for_bounded_cleanup(self):
        d = AuthJobDaemon()
        def fault(method, path, body):
            if method == 'GET' and d.job_row is not None and d.guard.auth_job_exit_verified:
                dev.refuse('docker', 'docker_timeout')
        d.job_fault = fault
        with self.assertRaises(dev.Refusal) as error: d.guard.execute_auth_job()
        self.assertEqual(error.exception.code, 'docker_timeout')
        self.assertFalse(d.guard.auth_job_delete_attempted)
        self.assertFalse(any(m == 'DELETE' for m, _, _ in d.events))
        d.job_fault = None
        d.guard.cleanup_execution()
        self.assertTrue(d.guard.cleaned)
        deletes = [p for m, p, _ in d.events if m == 'DELETE' and '/containers/' in p]
        self.assertEqual(deletes, ['/v1.48/containers/' + 'c'*64 + '?force=true', '/v1.48/containers/' + 'a'*64 + '?force=true'])
        count = len(d.events)
        with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
        with self.assertRaises(dev.Refusal): d.guard.execute_auth_job()
        self.assertEqual(len(d.events), count)

    def test_repeated_running_observations_keep_identity_deadline_and_order(self):
        d = AuthJobDaemon()
        deadline = d.guard.deadline
        observations = []
        def fault(method, path, body):
            if method == 'GET' and d.job_row is not None and d.guard.auth_job_start_attempted:
                state = d.job_row['State']
                if len(observations) < 2:
                    state.update(Status='running', Running=True, Pid=456, FinishedAt='0001-01-01T00:00:00Z')
                else:
                    state.update(Status='exited', Running=False, Pid=0, FinishedAt='2026-10-17T12:00:01.000000002Z')
                observations.append(state['Status'])
        d.job_fault = fault
        with patch.object(resources.time, 'sleep') as sleep:
            d.guard.execute_auth_job()
        self.assertEqual(observations, ['running', 'running', 'exited', 'exited'])
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual(d.guard.deadline, deadline)
        self.assertTrue(d.guard.auth_job_exit_verified)
        self.assertTrue(d.guard.auth_job_disposed)
        d.guard.finish_execution()
        deletes = [p for m, p, _ in d.events if m == 'DELETE' and '/containers/' in p]
        self.assertEqual(deletes, ['/v1.48/containers/' + 'c'*64 + '?force=false', '/v1.48/containers/' + 'a'*64 + '?force=false'])

    def test_daemon_started_then_lost_start_ack_never_replays_or_cleans_closed_peer(self):
        d = AuthJobDaemon()
        def fault(method, path, body):
            if method == 'POST' and path.endswith('/start'):
                d.job_row['State'].update(Status='running', Running=True, Pid=456,
                        StartedAt='2026-10-17T12:00:00.000000002Z')
                d.network['Containers']['c'*64] = {}
                d.closed = True
                dev.refuse('docker', 'docker_response_invalid')
        d.job_fault = fault
        with self.assertRaises(dev.Refusal): d.guard.execute_auth_job()
        self.assertEqual(d.job_row['State']['Status'], 'running')
        count = len(d.events)
        with self.assertRaises(dev.Refusal): d.guard.execute_auth_job()
        with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
        self.assertEqual(len(d.events), count)
        self.assertEqual(sum(p.endswith('/start') and 'c'*64 in p for _, p, _ in d.events), 1)
        self.assertFalse(any(m == 'DELETE' for m, _, _ in d.events))
        self.assertTrue(d.row and d.volume and d.network)

    def test_valid_finished_timestamp_drift_revokes_completion_before_disposal(self):
        d = AuthJobDaemon()
        def fault(method, path, body):
            if method == 'GET' and d.job_row is not None and d.guard.auth_job_exit_verified:
                d.job_row['State']['FinishedAt'] = '2026-10-17T12:00:02.000000002Z'
        d.job_fault = fault
        with self.assertRaises(dev.Refusal): d.guard.execute_auth_job()
        self.assertTrue(d.guard.ownership_lost)
        self.assertFalse(d.guard.auth_job_exit_verified)
        self.assertFalse(d.guard.auth_job_disposed)
        self.assertFalse(any(m == 'DELETE' for m, _, _ in d.events))

    def test_running_start_identity_drift_revokes_downstream_deletion(self):
        d = AuthJobDaemon()
        observations = 0
        def fault(method, path, body):
            nonlocal observations
            if method == 'GET' and d.job_row is not None and d.guard.auth_job_start_attempted:
                observations += 1
                d.job_row['State'].update(Status='running', Running=True, Pid=456,
                        FinishedAt='0001-01-01T00:00:00Z',
                        StartedAt='2026-10-17T12:00:00.00000000' + str(min(observations + 1, 9)) + 'Z')
        d.job_fault = fault
        with patch.object(resources.time, 'sleep'), self.assertRaises(dev.Refusal): d.guard.execute_auth_job()
        self.assertEqual(observations, 2)
        self.assertTrue(d.guard.ownership_lost)
        self.assertFalse(d.guard.auth_job_exit_verified)
        count = len(d.events)
        with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
        self.assertEqual(len(d.events), count)
        self.assertFalse(any(m == 'DELETE' for m, _, _ in d.events))

    def test_existing_name_or_unexpected_status_refuses_without_auth_adoption(self):
        for status in (200, 500):
            with self.subTest(status=status):
                d = AuthJobDaemon()
                def fault(method, path, body):
                    if method == 'GET' and 'supabase_auth_migrate_' in path:
                        return status, {'Id': 'd'*64}
                d.job_fault = fault
                with self.assertRaises(dev.Refusal) as error: d.guard.execute_auth_job()
                self.assertEqual(error.exception.code, 'execution_existing_container')
                self.assertIsNone(d.guard.auth_job_id)
                self.assertFalse(any(m != 'GET' and ('auth_migrate_' in p or 'c'*64 in p) for m, p, _ in d.events))

class AuthCatalogDaemon(AuthJobDaemon):
    def __init__(self):
        super().__init__()
        self.guard.auth_catalog = True
        self.catalog_modes = []
        self.exec_body = None
        self.exec_exit = None
        self.exec_started = False
        self.catalog_valid = True

    def exchange(self, method, path, body=None):
        if path.endswith('/exec'):
            self.events.append((method, path, self.copy(body)))
            self.exec_body = body
            query = body['Cmd'][-1]
            self.catalog_modes.append('apply' if 'api default privileges delta failed' in query else
                                      'verify' if 'api default privileges verification failed' in query else
                                      'pre' if 'fresh auth precondition failed' in query else 'post')
            self.exec_ident = format(len(self.catalog_modes) + 32, '064x')
            self.exec_started, self.exec_exit = False, None
            return 201, {'Id': self.exec_ident}
        if path.startswith('/v1.48/exec/'):
            self.events.append((method, path, self.copy(body)))
            if path.endswith('/start'):
                self.exec_started = True
                self.exec_exit = 0 if self.catalog_valid else 1
                return 200, None
            return 200, {'ID': self.exec_ident, 'ContainerID': self.row['Id'], 'Running': False,
                         'ExitCode': self.exec_exit, 'Pid': 321 if self.exec_started else 0,
                         'ProcessConfig': {'entrypoint': 'psql', 'arguments': self.exec_body['Cmd'][1:],
                                           'privileged': False, 'tty': False, 'user': 'postgres'}}
        return super().exchange(method, path, body)

class AuthCatalogExecutionMatrix(unittest.TestCase):
    def test_api_default_privileges_semantic_fixture_acceptance(self):
        import qualify_startup
        body, count = qualify_startup._api_default_privileges_semantic_exec('post')
        self.assertEqual(count, 6)
        self.assertEqual(body['Cmd'][body['Cmd'].index('-U') + 1], 'supabase_admin')
        self.assertIn('exact default ACL delta failed', body['Cmd'][-1])
        self.assertIn('rollback witness failed', body['Cmd'][-1])
        self.assertIn('SET LOCAL ROLE postgres;', body['Cmd'][-1])

    def test_api_default_privileges_semantic_fixture_preserves_bounds_and_closed_cases(self):
        import qualify_startup
        import startup_lifecycle as lifecycle
        original = qualify_startup._original_auth_catalog_exec('post')
        predicate = original['Cmd'][-1].split("SET LOCAL idle_in_transaction_session_timeout = '5s'; ", 1)[1][:-len(' COMMIT;')]
        for case in ('apply', 'omitted', 'extra'):
            with self.subTest(case=case):
                body, count = qualify_startup._api_default_privileges_semantic_exec('post', case)
                self.assertEqual(count, 6)
                query = body['Cmd'][-1]
                self.assertTrue(query.startswith("BEGIN; SET LOCAL statement_timeout = '5s'; SET LOCAL lock_timeout = '1s'; SET LOCAL idle_in_transaction_session_timeout = '5s'; "))
                self.assertTrue(query.endswith('SET LOCAL ROLE postgres; ' + predicate + ' ROLLBACK;'))
                self.assertEqual(lifecycle.API_DEFAULT_PRIVILEGES_SQL in query, case != 'omitted')
                self.assertEqual('REVOKE TRUNCATE ON TABLES FROM anon;' in query, case == 'extra')
                self.assertIn('EXCEPTION WHEN SQLSTATE \'ZX001\' THEN NULL;', query)
                self.assertNotIn('WHEN OTHERS', query)
                self.assertIn('seeded target ACL precondition failed', query)
                self.assertIn("('r','SELECT'),('r','INSERT'),('r','UPDATE'),('r','DELETE'),('S','USAGE'),('S','SELECT'),('f','EXECUTE')", query)
                self.assertIn('false AS is_grantable', query)
                self.assertIn('WITH GRANT OPTION', query)
                self.assertEqual(query.count('insensitive ACL oracle'), 5)
                self.assertEqual(qualify_startup._api_default_privileges_semantic_exec('post', case), (body, count))
        self.assertEqual(qualify_startup._api_default_privileges_semantic_exec('pre'), (qualify_startup._original_auth_catalog_exec('pre'), 0))
        for mode, case in [('arbitrary', 'apply'), ('post', 'arbitrary'), (None, 'apply'), ('post', True)]:
            with self.assertRaises(dev.Refusal): qualify_startup._api_default_privileges_semantic_exec(mode, case)

    def test_api_default_privileges_semantic_fixture_only_admitted_inside_exact_test_hook(self):
        import qualify_startup
        import startup_lifecycle as lifecycle
        import copy
        route = '/v1.48/containers/' + 'a'*64 + '/exec'
        for case in ('apply', 'omitted', 'extra'):
            body, _ = qualify_startup._api_default_privileges_semantic_exec('post', case)
            with self.assertRaises(dev.Refusal): dev._docker_request('POST', route, body, True)
            with patch.object(lifecycle, 'auth_catalog_exec', side_effect=lambda mode: qualify_startup._api_default_privileges_semantic_exec(mode, case)[0]):
                self.assertLess(len(dev._docker_request('POST', route, body, True)), 16384)
                with self.assertRaises(dev.Refusal): dev._docker_request('POST', route, lifecycle.api_default_privileges_exec(), True)
                for key, value in [('User', 'root'), ('AttachStdout', True), ('Cmd', body['Cmd'] + ['unexpected'])]:
                    changed = copy.deepcopy(body)
                    changed[key] = value
                    with self.assertRaises(dev.Refusal): dev._docker_request('POST', route, changed, True)
            with self.assertRaises(dev.Refusal): dev._docker_request('POST', route, body, True)

    def test_api_default_privileges_runbook_annotation_requires_qualified_result(self):
        import qualify_startup
        import re, json, io, contextlib
        text = (Path(__file__).resolve().parents[1] / 'DEVELOPMENT.md').read_text()
        block = next(c for c in re.findall(r'```sh\n(.*?)```', text, re.S) if c.startswith('KDG_ACL_CASE=apply\n'))
        program = block.split("<<'PY'\n", 1)[1].rsplit('\nPY', 1)[0]
        good = {'ok': True, 'code': 'qualified', 'stage': 'pinned_cli_postgres_auth_catalog',
                'auth_catalog_verified': True, 'api_default_privileges_request_refused': True,
                'cli_terminated_before_dispatch': True, 'cleanup_verified': True,
                'runtime_ready': False, 'fresh_setup_completed': False}
        for case, payload, code, valid in [('apply', good, 0, True), ('extra', good, 0, False),
                ('apply', dict(good, cleanup_verified=False), 0, False),
                ('apply', dict(good, auth_catalog_verified=1), 0, False),
                ('omitted', {'ok': False, 'code': 'execution_sql_failed'}, 2, True)]:
            with self.subTest(case=case, code=code, valid=valid):
                output = io.StringIO()
                def qualify(*args):
                    print(json.dumps(payload))
                    return code
                with patch.object(sys, 'argv', ['fixture', '00000000-0000-0000-0000-000000000000', case]), \
                        patch.object(qualify_startup, 'main', side_effect=qualify), \
                        patch.object(qualify_startup, '_api_default_privileges_semantic_exec', return_value=({}, 9)), \
                        contextlib.redirect_stdout(output):
                    with self.assertRaises(SystemExit) as error: exec(compile(program, '<tracked-acl-command>', 'exec'), {})
                self.assertEqual(error.exception.code, code if valid else 'Unexpected successful ACL qualification result')
                if valid:
                    self.assertEqual(json.loads(output.getvalue())['semantic_invariants_verified'], 9 if code == 0 else 0)
                else:
                    self.assertEqual(output.getvalue(), '')
    def run_catalog(self, d):
        d.guard.auth_catalog_sql('pre')
        d.guard.execute_auth_job()
        d.guard.auth_catalog_sql('post')

    def test_independent_pre_job_post_then_same_pg_cleanup(self):
        d = AuthCatalogDaemon()
        self.run_catalog(d)
        self.assertTrue(d.guard.auth_catalog_precondition_verified)
        self.assertTrue(d.guard.auth_catalog_verified)
        self.assertEqual(d.catalog_modes, ['pre', 'post'])
        with patch.object(dev, 'free_ports'): d.guard.finish_execution()
        self.assertTrue(d.guard.cleaned)

    def test_post_auth_default_privileges_request_acceptance_without_dispatch(self):
        d = AuthCatalogDaemon()
        self.run_catalog(d)
        self.assertTrue(d.guard.api_default_privileges_request_refused)
        self.assertEqual(d.catalog_modes, ['pre', 'post'])
        self.assertFalse(any('alter default privileges' in str(body)
                             for _, _, body in d.events))
        with patch.object(dev, 'free_ports'): d.guard.finish_execution()
        self.assertTrue(d.guard.cleaned)

    def test_default_privileges_request_matches_pinned_sql_and_closed_envelope(self):
        import startup_lifecycle as lifecycle
        body = lifecycle.api_default_privileges_exec()
        expected_sql = '''
alter default privileges for role postgres in schema public
  revoke select, insert, update, delete on tables from anon, authenticated, service_role;
alter default privileges for role postgres in schema public
  revoke usage, select on sequences from anon, authenticated, service_role;
alter default privileges for role postgres in schema public
  revoke execute on functions from anon, authenticated, service_role;
'''
        expected = {'AttachStdin': False, 'AttachStdout': False, 'AttachStderr': False,
                    'Tty': False, 'Privileged': False, 'User': 'postgres', 'Env': ['PGPASSWORD=postgres'],
                    'Cmd': ['psql', '-X', '-A', '-t', '-v', 'ON_ERROR_STOP=1', '-h', '127.0.0.1',
                            '-U', 'postgres', '-d', 'postgres', '-c', expected_sql]}
        self.assertEqual(body, expected)
        self.assertTrue(lifecycle.valid_api_default_privileges_exec(body))
        # Construction must not silently authorize either persistent or one-shot dispatch.
        for persistent in (False, True):
            with self.assertRaises(dev.Refusal) as error:
                dev._docker_request('POST', '/v1.48/containers/'+'a'*64+'/exec', body, persistent)
            self.assertEqual((error.exception.stage, error.exception.code), ('docker', 'docker_request_invalid'))

    def test_default_privileges_request_rejects_envelope_and_sql_mutations(self):
        import startup_lifecycle as lifecycle
        import copy
        original = lifecycle.api_default_privileges_exec()
        candidates = [None, [], {}, dict(original, Unexpected=False)]
        for key, value in original.items():
            changed = copy.deepcopy(original)
            del changed[key]
            candidates.append(changed)
            changed = copy.deepcopy(original)
            changed[key] = 0 if type(value) is bool else None
            candidates.append(changed)
        for index, value in enumerate(original['Cmd']):
            changed = copy.deepcopy(original)
            changed['Cmd'][index] = value + ' unexpected'
            candidates.append(changed)
        candidates.append(dict(original, Env=['PGPASSWORD=other']))
        candidates.append(dict(original, Cmd=tuple(original['Cmd'])))
        for body in candidates:
            with self.subTest(body=body):
                self.assertFalse(lifecycle.valid_api_default_privileges_exec(body))
        original['Cmd'][-1] = 'SELECT true;'
        self.assertTrue(lifecycle.valid_api_default_privileges_exec(lifecycle.api_default_privileges_exec()))

    def test_default_privileges_bad_construction_cannot_qualify_or_replay(self):
        import startup_lifecycle as lifecycle
        d = AuthCatalogDaemon()
        d.guard.auth_catalog_sql('pre')
        d.guard.execute_auth_job()
        body = lifecycle.api_default_privileges_exec()
        body['Cmd'][-1] += ' SELECT true;'
        with patch.object(lifecycle, 'api_default_privileges_exec', return_value=body):
            with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql('post')
        self.assertFalse(d.guard.auth_catalog_verified or d.guard.api_default_privileges_request_refused)
        with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql('post')
        with self.assertRaises(dev.Refusal): d.guard.finish_execution()
        self.assertEqual(d.catalog_modes, ['pre', 'post'])

    def test_default_privileges_accidental_admission_cannot_qualify(self):
        d = AuthCatalogDaemon()
        d.guard.auth_catalog_sql('pre')
        d.guard.execute_auth_job()
        with patch.object(dev, '_docker_request', return_value=b'not transmitted'):
            with self.assertRaises(dev.Refusal) as error: d.guard.auth_catalog_sql('post')
        self.assertEqual(error.exception.code, 'invalid_owner_handoff')
        self.assertFalse(d.guard.auth_catalog_verified or d.guard.api_default_privileges_request_refused)
        self.assertEqual(d.catalog_modes, ['pre', 'post'])
        before = list(d.events)
        with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql('post')
        with self.assertRaises(dev.Refusal): d.guard.finish_execution()
        self.assertEqual(d.events, before)

    def test_default_privileges_wrong_refusal_cannot_qualify(self):
        d = AuthCatalogDaemon()
        d.guard.auth_catalog_sql('pre')
        d.guard.execute_auth_job()
        original = dev.Refusal('docker', 'docker_timeout')
        with patch.object(dev, '_docker_request', side_effect=original):
            with self.assertRaises(dev.Refusal) as error: d.guard.auth_catalog_sql('post')
        self.assertIs(error.exception, original)
        self.assertFalse(d.guard.auth_catalog_verified or d.guard.api_default_privileges_request_refused)
        before = list(d.events)
        with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql('post')
        with self.assertRaises(dev.Refusal): d.guard.finish_execution()
        self.assertEqual(d.events, before)

    def test_default_privileges_health_change_during_construction_blocks_success(self):
        import startup_lifecycle as lifecycle
        d = AuthCatalogDaemon()
        d.guard.auth_catalog_sql('pre')
        d.guard.execute_auth_job()
        construct = lifecycle.api_default_privileges_exec
        def changed():
            d.row['State']['Health']['Status'] = 'unhealthy'
            return construct()
        with patch.object(lifecycle, 'api_default_privileges_exec', side_effect=changed):
            with self.assertRaises(dev.Refusal) as error: d.guard.auth_catalog_sql('post')
        self.assertEqual(error.exception.code, 'execution_invalid_health')
        self.assertFalse(d.guard.auth_catalog_verified or d.guard.api_default_privileges_request_refused)
        before = list(d.events)
        with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql('post')
        with self.assertRaises(dev.Refusal): d.guard.finish_execution()
        self.assertEqual(d.events, before)

    def test_default_privileges_failed_catalog_never_constructs_request(self):
        import startup_lifecycle as lifecycle
        d = AuthCatalogDaemon()
        d.guard.auth_catalog_sql('pre')
        d.guard.execute_auth_job()
        d.catalog_valid = False
        with patch.object(lifecycle, 'api_default_privileges_exec', side_effect=AssertionError('unreachable')):
            with self.assertRaises(dev.Refusal) as error: d.guard.auth_catalog_sql('post')
        self.assertEqual(error.exception.code, 'execution_sql_failed')
        self.assertFalse(d.guard.auth_catalog_verified or d.guard.api_default_privileges_request_refused)

    def test_default_privileges_missing_fact_blocks_finish(self):
        d = AuthCatalogDaemon()
        self.run_catalog(d)
        d.guard.api_default_privileges_request_refused = False
        before = len(d.events)
        with self.assertRaises(dev.Refusal): d.guard.finish_execution()
        self.assertEqual(len(d.events), before)

    def test_precondition_failure_never_dispatches_job_or_replays(self):
        d = AuthCatalogDaemon()
        d.catalog_valid = False
        with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql('pre')
        with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql('pre')
        with self.assertRaises(dev.Refusal): d.guard.execute_auth_job()
        self.assertEqual(d.catalog_modes, ['pre'])
        self.assertFalse(d.guard.auth_job_dispatched)
        self.assertFalse(d.guard.auth_catalog_verified)

    def test_closed_read_only_sql_has_source_ledger_and_no_generic_route(self):
        import startup_lifecycle as lifecycle
        self.assertEqual(len(lifecycle.AUTH_MIGRATION_VERSIONS), 75)
        self.assertEqual(lifecycle.AUTH_MIGRATION_VERSIONS[0], '00')
        for mode in ['pre', 'post']:
            body = lifecycle.auth_catalog_exec(mode)
            query = body['Cmd'][-1]
            self.assertIn('BEGIN READ ONLY;', query)
            self.assertIn('IS NOT TRUE', query)
            self.assertIn('statement_timeout', query)
            self.assertTrue(lifecycle.valid_auth_catalog_exec(body))
            dev._docker_request('POST', '/v1.48/containers/'+'a'*64+'/exec', body, True)
            changed = __import__('copy').deepcopy(body)
            changed['Cmd'][-1] += ' SELECT true;'
            self.assertFalse(lifecycle.valid_auth_catalog_exec(changed))
            with self.assertRaises(dev.Refusal): dev._docker_request('POST', '/v1.48/containers/'+'a'*64+'/exec', changed, True)

    def test_postcondition_failure_cannot_finish_or_replay(self):
        d = AuthCatalogDaemon()
        d.guard.auth_catalog_sql('pre')
        d.guard.execute_auth_job()
        d.catalog_valid = False
        with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql('post')
        with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql('post')
        with self.assertRaises(dev.Refusal): d.guard.finish_execution()
        self.assertFalse(d.guard.auth_catalog_verified)
        self.assertEqual(d.catalog_modes, ['pre', 'post'])

    def test_exec_uncertainty_consumes_attempt_and_never_replays(self):
        for mode in ['pre', 'post']:
            for fault in ['create_lost', 'create_bad', 'create_id', 'inspect_bad', 'start_lost', 'start_bad', 'exit_bad', 'interrupt']:
                with self.subTest(mode=mode, fault=fault):
                    d = AuthCatalogDaemon()
                    if mode == 'post':
                        d.guard.auth_catalog_sql('pre')
                        d.guard.execute_auth_job()
                    exchange = d.exchange
                    def broken(method, path, body=None):
                        if path.endswith('/exec'):
                            if fault == 'create_lost': raise dev.Refusal('startup', 'lost')
                            if fault == 'create_bad': return 500, None
                            if fault == 'create_id': return 201, {'Id': 'invalid'}
                        result = exchange(method, path, body)
                        if path.startswith('/v1.48/exec/'):
                            if path.endswith('/start'):
                                if fault == 'start_lost': raise dev.Refusal('startup', 'lost')
                                if fault == 'interrupt': raise KeyboardInterrupt()
                                if fault == 'start_bad': return 500, None
                            elif path.endswith('/json'):
                                if fault == 'inspect_bad': result[1]['ProcessConfig']['user'] = 'root'
                                if fault == 'exit_bad' and d.exec_started: result[1]['ExitCode'] = 1
                        return result
                    d.exchange = broken
                    with self.assertRaises((dev.Refusal, KeyboardInterrupt)): d.guard.auth_catalog_sql(mode)
                    count = len(d.events)
                    with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql(mode)
                    self.assertEqual(len(d.events), count)
                    self.assertFalse(d.guard.auth_catalog_verified)
                    if mode == 'pre':
                        with self.assertRaises(dev.Refusal): d.guard.execute_auth_job()
                        self.assertFalse(d.guard.auth_job_dispatched)

    def test_current_pg_checks_surround_each_exchange_before_next_mutation(self):
        for mode in ['pre', 'post']:
            for mutation in ['instance', 'health', 'image', 'fixture', 'network', 'volume']:
                for boundary in ['create', 'inspect', 'start']:
                    with self.subTest(mode=mode, mutation=mutation, boundary=boundary):
                        d = AuthCatalogDaemon()
                        if mode == 'post':
                            d.guard.auth_catalog_sql('pre')
                            d.guard.execute_auth_job()
                        exchange = d.exchange
                        changed = False
                        mutation_event_count = None
                        def mutate(method, path, body=None):
                            nonlocal changed, mutation_event_count
                            result = exchange(method, path, body)
                            hit = (boundary == 'create' and path.endswith('/exec')
                                   or boundary == 'inspect' and path.startswith('/v1.48/exec/') and path.endswith('/json')
                                   or boundary == 'start' and path.startswith('/v1.48/exec/') and path.endswith('/start'))
                            if hit and not changed:
                                changed = True
                                mutation_event_count = len(d.events)
                                if mutation == 'instance': d.row['State']['StartedAt'] = '2026-10-18T00:00:00Z'
                                elif mutation == 'health': d.row['State']['Health']['Status'] = 'unhealthy'
                                elif mutation == 'image': d.row['Image'] = 'sha256:' + 'f'*64
                                elif mutation == 'fixture': d.hook = lambda: dev.refuse('startup', 'fixture_changed')
                                elif mutation == 'network': d.network['Id'] = 'f'*64
                                elif mutation == 'volume': d.volume['Labels']['foreign'] = 'true'
                            return result
                        d.exchange = mutate
                        with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql(mode)
                        self.assertEqual(d.guard.auth_catalog_precondition_verified, mode == 'post')
                        self.assertEqual(d.guard.auth_job_dispatched, mode == 'post')
                        self.assertFalse(d.guard.auth_catalog_verified)
                        self.assertIsNotNone(mutation_event_count)
                        self.assertTrue(all(method == 'GET' for method, _, _ in d.events[mutation_event_count:]))

    def test_invalid_order_disabled_early_cli_and_duplicate_exec_id_refuse(self):
        d = AuthCatalogDaemon()
        for change in ['disabled', 'cli', 'post']:
            with self.subTest(change=change):
                d.guard.auth_catalog = change != 'disabled'
                d.guard.auth_cli_terminated = change != 'cli'
                with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql('post' if change == 'post' else 'pre')
        d.guard.auth_catalog = d.guard.auth_cli_terminated = True
        d.guard.auth_catalog_sql('pre')
        d.guard.execute_auth_job()
        exchange = d.exchange
        def duplicate(method, path, body=None):
            result = exchange(method, path, body)
            if path.endswith('/exec'): return 201, {'Id': next(iter(d.guard.exec_ids))}
            return result
        d.exchange = duplicate
        with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql('post')
        self.assertFalse(d.guard.auth_catalog_verified)

    def test_running_exec_then_success_and_deadline_preserve_one_start(self):
        for result in ['success', 'deadline']:
            d = AuthCatalogDaemon()
            exchange = d.exchange
            running_observed = False
            def running(method, path, body=None):
                nonlocal running_observed
                response = exchange(method, path, body)
                if path.startswith('/v1.48/exec/') and path.endswith('/json') and d.exec_started and not running_observed:
                    running_observed = True
                    response[1].update(Running=True, ExitCode=None)
                    if result == 'deadline': d.deadline = d.guard.deadline = 0
                return response
            d.exchange = running
            with patch.object(resources.time, 'sleep'):
                if result == 'success':
                    d.guard.auth_catalog_sql('pre')
                    self.assertTrue(d.guard.auth_catalog_precondition_verified)
                else:
                    with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql('pre')
                    self.assertFalse(d.guard.auth_catalog_precondition_verified)
            self.assertEqual(sum(p.startswith('/v1.48/exec/') and p.endswith('/start') for _, p, _ in d.events), 1)

    def test_malformed_exec_lifecycle_and_config_never_start_or_qualify(self):
        mutations = [lambda r: r.update(ID='f'*64), lambda r: r.update(ContainerID='f'*64),
                     lambda r: r.update(Running=None), lambda r: r.update(ExitCode=True),
                     lambda r: r.update(Pid=True), lambda r: r.update(Pid=-1),
                     lambda r: r.update(ExitCode=0), lambda r: r.update(Running=True),
                     lambda r: r.update(ProcessConfig=None),
                     lambda r: r['ProcessConfig'].update(entrypoint='sh'),
                     lambda r: r['ProcessConfig'].update(arguments=['-c', 'SELECT true']),
                     lambda r: r['ProcessConfig'].update(privileged=True),
                     lambda r: r['ProcessConfig'].update(tty=True),
                     lambda r: r['ProcessConfig'].update(user='root')]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                d = AuthCatalogDaemon()
                exchange = d.exchange
                def malformed(method, path, body=None):
                    response = exchange(method, path, body)
                    if path.startswith('/v1.48/exec/') and path.endswith('/json'): mutation(response[1])
                    return response
                d.exchange = malformed
                with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql('pre')
                self.assertFalse(any(p.startswith('/v1.48/exec/') and p.endswith('/start') for _, p, _ in d.events))
                self.assertFalse(d.guard.auth_catalog_precondition_verified)

    def test_closed_exec_rejects_type_confusion_extra_keys_and_changed_flags(self):
        import startup_lifecycle as lifecycle
        import copy
        for mode in ['pre', 'post']:
            for key, value in [('AttachStdout', True), ('AttachStderr', True), ('AttachStdin', 0),
                               ('Tty', 0), ('Privileged', 0), ('User', 'root'), ('Env', []), ('extra', False)]:
                with self.subTest(mode=mode, key=key):
                    body = copy.deepcopy(lifecycle.auth_catalog_exec(mode))
                    body[key] = value
                    self.assertFalse(lifecycle.valid_auth_catalog_exec(body))
        with self.assertRaises(dev.Refusal): lifecycle.auth_catalog_exec('arbitrary')

    def test_terminal_exit_while_running_and_completed_zero_pid_refuse(self):
        for defect in ['running_terminal', 'completed_zero_pid']:
            d = AuthCatalogDaemon()
            exchange = d.exchange
            def malformed(method, path, body=None):
                response = exchange(method, path, body)
                if path.startswith('/v1.48/exec/') and path.endswith('/json') and d.exec_started:
                    if defect == 'running_terminal':
                        response[1].update(Running=True, ExitCode=0)
                        d.exec_started = False  # One bad running observation, then eventual success.
                    else: response[1]['Pid'] = 0
                return response
            d.exchange = malformed
            with self.subTest(defect=defect), patch.object(resources.time, 'sleep'), self.assertRaises(dev.Refusal):
                d.guard.auth_catalog_sql('pre')

    def test_starting_zero_pid_then_running_then_completed_qualifies(self):
        d = AuthCatalogDaemon()
        exchange = d.exchange
        states = iter([(True, 0, None), (True, 321, None), (False, 321, 0)])
        def sequence(method, path, body=None):
            response = exchange(method, path, body)
            if path.startswith('/v1.48/exec/') and path.endswith('/json') and d.exec_started:
                running, pid, exit_code = next(states)
                response[1].update(Running=running, Pid=pid, ExitCode=exit_code)
            return response
        d.exchange = sequence
        with patch.object(resources.time, 'sleep'): d.guard.auth_catalog_sql('pre')
        self.assertTrue(d.guard.auth_catalog_precondition_verified)

    def test_tracked_corruption_builder_is_closed_bounded_role_scoped_and_rollback_only(self):
        import qualify_startup
        import startup_lifecycle as lifecycle
        for mode, count in [('pre', 14), ('post', 95)]:
            body, actual_count = qualify_startup._auth_catalog_corruption_exec(mode)
            self.assertEqual(actual_count, count)
            self.assertEqual(body['Cmd'][body['Cmd'].index('-h') + 1], '/var/run/postgresql')
            self.assertEqual(body['Cmd'][body['Cmd'].index('-U') + 1], 'supabase_admin')
            query = body['Cmd'][-1]
            self.assertTrue(query.startswith("BEGIN; SET LOCAL statement_timeout = '5s'; SET LOCAL lock_timeout = '1s'; SET LOCAL idle_in_transaction_session_timeout = '5s'; "))
            self.assertTrue(query.endswith(' ROLLBACK;'))
            self.assertNotIn('COMMIT;', query)
            self.assertIn("EXECUTE 'SET LOCAL ROLE postgres'", query)
            self.assertIn("EXECUTE 'RESET ROLE'", query)
            self.assertIn("EXCEPTION WHEN raise_exception THEN rejected := true", query)
            self.assertIn("EXCEPTION WHEN SQLSTATE 'ZX001' THEN NULL", query)
            self.assertFalse(lifecycle.valid_auth_catalog_exec(body))
            expected_body = lifecycle.auth_catalog_exec(mode)
            expected_body['Cmd'][-1] = query
            expected_body['Cmd'][expected_body['Cmd'].index('-h') + 1] = '/var/run/postgresql'
            expected_body['Cmd'][expected_body['Cmd'].index('-U') + 1] = 'supabase_admin'
            self.assertEqual(body, expected_body)
            import re
            array = query.split('FOREACH mutation IN ARRAY ARRAY[', 1)[1].split(']::text[] LOOP', 1)[0]
            mutations = [value.replace("''", "'") for value in re.findall(r"'((?:[^']|'')*)'", array)]
            self.assertEqual(len(mutations), count)
            inventory = __import__('json').loads((Path(__file__).resolve().parents[1] / 'fixtures/supabase-auth-catalog-v2.197.0.json').read_text())
            versions = inventory['postgres_baseline_versions' if mode == 'pre' else 'catalog_versions']
            self.assertEqual([m for m in mutations if m.startswith('DELETE')],
                             ["DELETE FROM auth.schema_migrations WHERE version='" + v + "'" for v in versions])
            self.assertIn('INSERT INTO auth.schema_migrations(version) VALUES (NULL)', mutations[-1] if mode == 'pre' else mutations[len(versions) + 2])
            with patch.object(lifecycle, 'auth_catalog_exec', side_effect=AssertionError('recursive builder')):
                self.assertEqual(qualify_startup._auth_catalog_corruption_exec(mode), (body, count))
        with self.assertRaises(dev.Refusal): qualify_startup._auth_catalog_corruption_exec('arbitrary')

    def test_static_source_inventory_independently_matches_baseline_auth_and_exact_union(self):
        import json
        import startup_lifecycle as lifecycle
        fixture = json.loads((Path(__file__).resolve().parents[1] / 'fixtures/supabase-auth-catalog-v2.197.0.json').read_text())
        auth, baseline, catalog = (fixture[key] for key in ('auth_versions', 'postgres_baseline_versions', 'catalog_versions'))
        self.assertEqual((len(auth), len(baseline), len(catalog)), (75, 7, 82))
        self.assertEqual(auth[0], '00')
        self.assertEqual(catalog, sorted(set(auth + baseline)))
        self.assertEqual(tuple(auth), lifecycle.AUTH_MIGRATION_VERSIONS)
        self.assertEqual(tuple(baseline), lifecycle.AUTH_POSTGRES_BASELINE_VERSIONS)
        self.assertEqual(tuple(catalog), lifecycle.AUTH_CATALOG_VERSIONS)
        for source in fixture['sources']:
            self.assertRegex(source['commit'], '^[0-9a-f]{40}$')
            self.assertRegex(source['sha256'], '^[0-9a-f]{64}$')
            self.assertTrue(source['path'])

class CliDbBackendExecutionMatrix(unittest.TestCase):
    def daemon(self):
        d = AuthCatalogDaemon()
        d.guard.cli_db_backend = True
        d.guard.auth_cli_terminated = False
        return d

    def test_presence_departure_catalog_job_and_cleanup(self):
        d = self.daemon()
        process = Mock()
        process.poll.return_value = None
        d.guard.cli_db_backend_sql('present', process)
        self.assertTrue(d.guard.cli_db_backend_present_verified)
        d.guard.auth_cli_terminated = True
        d.guard.cli_db_backend_sql('departed')
        self.assertTrue(d.guard.cli_db_backend_departure_verified)
        d.guard.auth_catalog_sql('pre')
        d.guard.execute_auth_job()
        d.guard.auth_catalog_sql('post')
        with patch.object(dev, 'free_ports'): d.guard.finish_execution()
        self.assertTrue(d.guard.cleaned)

    def test_closed_predicates_and_exact_transport_allowlist(self):
        import copy
        import startup_lifecycle as lifecycle
        for mode in ('present', 'departed'):
            body = lifecycle.cli_db_backend_exec(mode)
            self.assertTrue(lifecycle.valid_cli_db_backend_exec(body))
            dev._docker_request('POST', '/v1.48/containers/'+'a'*64+'/exec', body, True)
            query = body['Cmd'][-1]
            for required in ('BEGIN READ ONLY', "statement_timeout = '5s'", "lock_timeout = '1s'",
                             "idle_in_transaction_session_timeout = '5s'", "backend_type = 'client backend'",
                             'pid <> pg_backend_pid()', 'client_addr IS NOT NULL', "'127.0.0.0/8'", "'::1'"):
                self.assertIn(required, query)
            if mode == 'present':
                for required in ('count(*) = 1', 'bool_and', "usename = 'postgres'", "datname = 'postgres'",
                                 'client_port > 0', "state = 'idle'", 'IS TRUE', 'IS NOT TRUE'):
                    self.assertIn(required, query)
                # Wrong user/database/state remain members of the counted external set.
                self.assertNotIn('usename', query[query.index('FROM pg_stat_activity'):])
            else:
                self.assertIn('count(*) = 0', query)
                self.assertIn("interval '3 seconds'", query)
                self.assertEqual(query.count('pg_stat_clear_snapshot()'), 1)
                self.assertLess(query.index('LOOP'), query.index('pg_stat_clear_snapshot()'))
                self.assertLess(query.index('pg_stat_clear_snapshot()'), query.index('FROM pg_stat_activity'))
                self.assertNotIn('pg_stat_reset', query)
            for field, value in [('AttachStdout', True), ('Privileged', 1), ('User', 'root'), ('Env', []),
                                 ('Cmd', body['Cmd'] + ['SELECT true'])]:
                changed = copy.deepcopy(body)
                changed[field] = value
                self.assertFalse(lifecycle.valid_cli_db_backend_exec(changed))
                with self.assertRaises(dev.Refusal):
                    dev._docker_request('POST', '/v1.48/containers/'+'a'*64+'/exec', changed, True)
        with self.assertRaises(dev.Refusal): lifecycle.cli_db_backend_exec('arbitrary')

    def test_predicate_failures_consume_attempt_and_block_job_catalog_finish(self):
        for mode in ('present', 'departed'):
            with self.subTest(mode=mode):
                d = self.daemon()
                process = Mock(poll=Mock(return_value=None))
                if mode == 'departed':
                    d.guard.cli_db_backend_sql('present', process)
                    d.guard.auth_cli_terminated = True
                d.catalog_valid = False
                with self.assertRaises(dev.Refusal): d.guard.cli_db_backend_sql(mode, process)
                count = len(d.catalog_modes)
                with self.assertRaises(dev.Refusal): d.guard.cli_db_backend_sql(mode, process)
                self.assertEqual(len(d.catalog_modes), count)
                with self.assertRaises(dev.Refusal): d.guard.auth_catalog_sql('pre')
                with self.assertRaises(dev.Refusal): d.guard.execute_auth_job()
                with self.assertRaises(dev.Refusal): d.guard.finish_execution()
                self.assertFalse(d.guard.cli_db_backend_departure_verified)
                self.assertFalse(d.guard.auth_job_dispatched)

    def test_required_phase_job_input_live_cli_and_termination_gates(self):
        for change in ('disabled', 'catalog', 'phase', 'job-input', 'admission', 'terminated', 'dead', 'absent', 'departed-first'):
            with self.subTest(change=change):
                d = self.daemon()
                process = Mock(poll=Mock(return_value=None))
                if change == 'disabled': d.guard.cli_db_backend = False
                if change == 'catalog': d.guard.auth_catalog = False
                if change == 'phase': d.guard.phase = 6
                if change == 'job-input': d.guard.auth_job_input = None
                if change == 'admission': d.guard.auth_terminal_attempted = False
                if change == 'terminated': d.guard.auth_cli_terminated = True
                if change == 'dead': process.poll.return_value = 0
                if change == 'absent': process = None
                with self.assertRaises(dev.Refusal):
                    d.guard.cli_db_backend_sql('departed' if change == 'departed-first' else 'present', process)
                self.assertFalse(d.catalog_modes)

    def test_custody_and_exec_faults_never_replay_or_claim_observation(self):
        for mode in ('present', 'departed'):
            for fault in ('create-lost', 'create-malformed', 'start-lost', 'inspect-malformed', 'bool-exit',
                          'running-exit', 'wrong-config', 'duplicate-id', 'custody', 'interrupted', 'dead-cli'):
                with self.subTest(mode=mode, fault=fault):
                    d = self.daemon()
                    process = Mock(poll=Mock(return_value=None))
                    if mode == 'departed':
                        d.guard.cli_db_backend_sql('present', process)
                        d.guard.auth_cli_terminated = True
                    original = d.exchange
                    def exchange(method, path, body=None):
                        if path.endswith('/exec'):
                            if fault == 'create-lost': raise dev.Refusal('docker', 'docker_timeout')
                            if fault == 'create-malformed': return 201, {'Id': None}
                            if fault == 'interrupted': raise KeyboardInterrupt()
                        status, row = original(method, path, body)
                        if path.endswith('/exec'):
                            if fault == 'duplicate-id': d.guard.exec_ids.add(row['Id'])
                            if fault == 'custody': d.row['State']['Health']['Status'] = 'unhealthy'
                            if fault == 'dead-cli' and mode == 'present': process.poll.return_value = 0
                        if '/exec/' in path and path.endswith('/start') and fault == 'start-lost':
                            raise dev.Refusal('docker', 'docker_timeout')
                        if '/exec/' in path and method == 'GET':
                            if fault == 'inspect-malformed': return 200, None
                            if fault == 'bool-exit': row['ExitCode'] = False
                            if fault == 'running-exit': row['Running'], row['ExitCode'] = True, 0
                            if fault == 'wrong-config': row['ProcessConfig']['user'] = 'root'
                        return status, row
                    if mode == 'departed' and fault == 'dead-cli': continue
                    d.guard.session.exchange = exchange
                    with self.assertRaises((dev.Refusal, KeyboardInterrupt)):
                        d.guard.cli_db_backend_sql(mode, process)
                    count = len(d.catalog_modes)
                    with self.assertRaises(dev.Refusal): d.guard.cli_db_backend_sql(mode, process)
                    self.assertEqual(count, len(d.catalog_modes))
                    self.assertFalse(d.guard.cli_db_backend_departure_verified)
                    if mode == 'present': self.assertFalse(d.guard.cli_db_backend_present_verified)
                    self.assertFalse(d.guard.auth_job_dispatched)

    def test_live_cli_rechecked_after_successful_exec_exit(self):
        d = self.daemon()
        process = Mock(poll=Mock(return_value=None))
        original = d.exchange
        def exchange(method, path, body=None):
            response = original(method, path, body)
            if '/exec/' in path and method == 'GET' and d.exec_started:
                process.poll.return_value = 0
            return response
        d.guard.session.exchange = exchange
        with self.assertRaises(dev.Refusal): d.guard.cli_db_backend_sql('present', process)
        self.assertFalse(d.guard.cli_db_backend_present_verified)
        self.assertIn('present', d.guard.cli_db_backend_attempts)

    def test_observer_visibility_is_required_before_either_external_count(self):
        import copy
        import startup_lifecycle as lifecycle
        for mode in ('present', 'departed'):
            with self.subTest(mode=mode):
                body = lifecycle.cli_db_backend_exec(mode)
                query = body['Cmd'][-1]
                guard = "IF pg_has_role(current_user, 'pg_read_all_stats', 'USAGE') IS NOT TRUE THEN RAISE EXCEPTION 'cli db backend visibility failed'; END IF; "
                self.assertIn(guard, query)
                self.assertLess(query.index(guard), query.index('FROM pg_stat_activity'))
                changed = copy.deepcopy(body)
                changed['Cmd'][-1] = query.replace(guard, '')
                self.assertFalse(lifecycle.valid_cli_db_backend_exec(changed))
                with self.assertRaises(dev.Refusal):
                    dev._docker_request('POST', '/v1.48/containers/'+'a'*64+'/exec', changed, True)

    def test_internal_semantic_fixture_preserves_predicates_and_is_not_public_exec(self):
        import qualify_startup
        import startup_lifecycle as lifecycle
        for mode, expected_count in [('present', 20), ('departed', 4)]:
            body, count = qualify_startup._cli_db_backend_semantic_exec(mode)
            self.assertEqual(count, expected_count)
            query = body['Cmd'][-1]
            self.assertTrue(query.startswith("BEGIN READ ONLY; SET LOCAL statement_timeout = '5s';"))
            self.assertTrue(query.endswith(' ROLLBACK;'))
            self.assertEqual(query.count('FROM pg_stat_activity'), 1)
            self.assertIn("replace(production_predicate, 'pg_stat_activity', source)", query)
            self.assertIn("EXCEPTION WHEN SQLSTATE 'P0001'", query)
            self.assertNotIn('WHEN OTHERS', query)
            self.assertIn('semantic predicate result mismatch', query)
            self.assertIn("replace(predicate, 'current_user', '''anon''')", query)
            self.assertIn('::inet', query)
            self.assertFalse(lifecycle.valid_cli_db_backend_exec(body))
            with self.assertRaises(dev.Refusal):
                dev._docker_request('POST', '/v1.48/containers/'+'a'*64+'/exec', body, True)
            expected = lifecycle.cli_db_backend_exec(mode)
            expected['Cmd'][-1] = query
            self.assertEqual(expected, body)
            with patch.object(lifecycle, 'cli_db_backend_exec', side_effect=AssertionError('recursive builder')):
                self.assertEqual(qualify_startup._cli_db_backend_semantic_exec(mode), (body, count))
        with self.assertRaises(dev.Refusal): qualify_startup._cli_db_backend_semantic_exec('arbitrary')

    def test_backend_current_custody_surrounds_each_exchange(self):
        for mode in ('present', 'departed'):
            for mutation in ('instance', 'health', 'image', 'fixture', 'network', 'volume'):
                for boundary in ('create', 'inspect', 'start'):
                    with self.subTest(mode=mode, mutation=mutation, boundary=boundary):
                        d = self.daemon()
                        process = Mock(poll=Mock(return_value=None))
                        if mode == 'departed':
                            d.guard.cli_db_backend_sql('present', process)
                            d.guard.auth_cli_terminated = True
                        original = d.exchange
                        detected_after = None
                        def exchange(method, path, body=None):
                            nonlocal detected_after
                            response = original(method, path, body)
                            hit = (boundary == 'create' and path.endswith('/exec')
                                   or boundary == 'inspect' and path.startswith('/v1.48/exec/') and path.endswith('/json')
                                   or boundary == 'start' and path.startswith('/v1.48/exec/') and path.endswith('/start'))
                            if hit and detected_after is None:
                                detected_after = len(d.events)
                                if mutation == 'instance': d.row['State']['StartedAt'] = '2026-10-18T00:00:00Z'
                                elif mutation == 'health': d.row['State']['Health']['Status'] = 'unhealthy'
                                elif mutation == 'image': d.row['Image'] = 'sha256:' + 'f'*64
                                elif mutation == 'fixture': d.hook = lambda: dev.refuse('startup', 'fixture_changed')
                                elif mutation == 'network': d.network['Id'] = 'f'*64
                                elif mutation == 'volume': d.volume['Labels']['foreign'] = 'true'
                            return response
                        d.guard.session.exchange = exchange
                        with self.assertRaises(dev.Refusal): d.guard.cli_db_backend_sql(mode, process)
                        self.assertIsNotNone(detected_after)
                        self.assertTrue(all(method == 'GET' for method, _, _ in d.events[detected_after:]))
                        self.assertEqual(d.guard.cli_db_backend_present_verified, mode == 'departed')
                        self.assertFalse(d.guard.cli_db_backend_departure_verified)
                        self.assertFalse(d.guard.auth_job_dispatched)

    def test_backend_running_transitions_completed_zero_pid_and_deadline(self):
        for mode in ('present', 'departed'):
            for outcome in ('success', 'completed-zero-pid', 'deadline'):
                with self.subTest(mode=mode, outcome=outcome):
                    d = self.daemon()
                    process = Mock(poll=Mock(return_value=None))
                    if mode == 'departed':
                        d.guard.cli_db_backend_sql('present', process)
                        d.guard.auth_cli_terminated = True
                    original = d.exchange
                    states = iter([(True, 0, None), (True, 321, None),
                                   (False, 0 if outcome == 'completed-zero-pid' else 321, 0)])
                    observed = 0
                    def exchange(method, path, body=None):
                        nonlocal observed
                        response = original(method, path, body)
                        if path.startswith('/v1.48/exec/') and path.endswith('/json') and d.exec_started:
                            running, pid, exit_code = next(states)
                            observed += 1
                            response[1].update(Running=running, Pid=pid, ExitCode=exit_code)
                            if outcome == 'deadline': d.deadline = d.guard.deadline = 0
                        return response
                    d.guard.session.exchange = exchange
                    count_before = sum(p.endswith('/start') and '/exec/' in p for _, p, _ in d.events)
                    with patch.object(resources.time, 'sleep'):
                        if outcome == 'success': d.guard.cli_db_backend_sql(mode, process)
                        else:
                            with self.assertRaises(dev.Refusal): d.guard.cli_db_backend_sql(mode, process)
                    self.assertEqual(sum(p.endswith('/start') and '/exec/' in p for _, p, _ in d.events) - count_before, 1)
                    self.assertEqual(observed, 1 if outcome == 'deadline' else 3)
                    self.assertEqual(d.guard.cli_db_backend_departure_verified, mode == 'departed' and outcome == 'success')
                    self.assertEqual(d.guard.cli_db_backend_present_verified, mode == 'departed' or outcome == 'success')

    def test_semantic_fixture_fits_existing_encoded_docker_request_limit(self):
        import qualify_startup
        import startup_lifecycle as lifecycle
        for mode in ('present', 'departed'):
            with self.subTest(mode=mode):
                body, _ = qualify_startup._cli_db_backend_semantic_exec(mode)
                with patch.object(lifecycle, 'cli_db_backend_exec', return_value=body):
                    encoded = dev._docker_request('POST', '/v1.48/containers/'+'a'*64+'/exec', body, True)
                self.assertLessEqual(len(encoded), 16384)
                self.assertIn(b'Content-Type: application/json', encoded)

    def test_departure_checks_deadline_after_zero_observation_before_exit(self):
        import startup_lifecycle as lifecycle
        query = lifecycle.cli_db_backend_exec('departed')['Cmd'][-1]
        zero_branch = query.split(') IS TRUE THEN ', 1)[1].split('EXIT;', 1)[0]
        self.assertIn('IF clock_timestamp() >= deadline THEN', zero_branch)
        self.assertIn("RAISE EXCEPTION 'cli db backend departure failed'", zero_branch)

    def test_late_zero_fixture_preserves_original_predicate_and_transport_bound(self):
        import qualify_startup
        import startup_lifecycle as lifecycle
        body = qualify_startup._cli_db_backend_late_zero_exec()
        query = body['Cmd'][-1]
        self.assertTrue(query.startswith("BEGIN READ ONLY; SET LOCAL statement_timeout = '5s';"))
        self.assertTrue(query.endswith(' ROLLBACK;'))
        self.assertIn('AS MATERIALIZED (SELECT pg_sleep(3.05) AS slept)', query)
        self.assertIn("NULLIF(delay.slept::text,'''')::inet", query)
        self.assertIn("EXCEPTION WHEN SQLSTATE 'P0001'", query)
        self.assertIn('late zero predicate accepted', query)
        self.assertNotIn('WHEN OTHERS', query)
        self.assertFalse(lifecycle.valid_cli_db_backend_exec(body))
        with self.assertRaises(dev.Refusal):
            dev._docker_request('POST', '/v1.48/containers/'+'a'*64+'/exec', body, True)
        expected = lifecycle.cli_db_backend_exec('departed')
        import re
        captured = re.search(r"BEGIN EXECUTE '((?:[^']|'')*)';", query).group(1).replace("''", "'")
        source = captured.split('FROM ', 1)[1].split(' WHERE pid <> pg_backend_pid()', 1)[0]
        prefix = "BEGIN READ ONLY; SET LOCAL statement_timeout = '5s'; SET LOCAL lock_timeout = '1s'; SET LOCAL idle_in_transaction_session_timeout = '5s'; "
        original = expected['Cmd'][-1][len(prefix):-len(' COMMIT;')]
        self.assertEqual(captured, original.replace('pg_stat_activity', source))
        expected['Cmd'][-1] = query
        self.assertEqual(body, expected)
        with patch.object(lifecycle, 'cli_db_backend_exec', return_value=body):
            self.assertLessEqual(len(dev._docker_request('POST', '/v1.48/containers/'+'a'*64+'/exec', body, True)), 16384)
        with patch.object(lifecycle, 'cli_db_backend_exec', side_effect=AssertionError('recursive builder')):
            self.assertEqual(qualify_startup._cli_db_backend_late_zero_exec(), body)

    def test_generated_wrapper_alarm_raises_caught_timeout_and_stops_held_parent(self):
        import ast
        import os
        import signal
        import tempfile
        import startup
        from create_profile_fixtures import target_fixture, test_plan, test_observations, RUN
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            target = target_fixture()
            startup.initialize_workdir(work, target, RUN)
            startup.install_fixture(work, target, RUN, startup.fixture_network(target, RUN),
                                    selection_plan=test_plan(), image_observations=test_observations(),
                                    profile_control='lifecycle-positive')
            self.assertEqual(startup.FIXTURE_SECONDS, 5)
            for runtime in ('docker', 'podman'):
                with self.subTest(runtime=runtime):
                    tree = ast.parse((work / 'bin' / runtime).read_text())
                    handlers = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                                and node.name == '_fixture_alarm']
                    self.assertEqual(len(handlers), 1)
                    functions = {}
                    exec(compile(ast.Module(body=handlers, type_ignores=[]), '<fixture-alarm-handler>', 'exec'), functions)
                    handler = functions['_fixture_alarm']
                    with self.assertRaises(TimeoutError): handler(signal.SIGALRM, None)
                    registration = next(node for node in tree.body if isinstance(node, ast.Expr)
                                        and isinstance(node.value, ast.Call)
                                        and ast.unparse(node.value.func) == 'signal.signal')
                    alarm = next(node for node in tree.body if isinstance(node, ast.Expr)
                                 and isinstance(node.value, ast.Call)
                                 and ast.unparse(node.value.func) == 'signal.alarm')
                    self.assertEqual(ast.unparse(registration.value), 'signal.signal(signal.SIGALRM, _fixture_alarm)')
                    self.assertEqual(ast.unparse(alarm.value), 'signal.alarm(5)')
                    self.assertLess(registration.lineno, alarm.lineno)
                    parent_fd = os.open('/dev/null', os.O_RDONLY)
                    def expire(*args, **kwargs): handler(signal.SIGALRM, None)
                    with patch.object(startup, 'parent_identity', return_value=parent_fd), \
                            patch.object(startup, 'fixture_command', side_effect=expire), \
                            patch.object(startup.signal, 'pidfd_send_signal') as stop_parent:
                        self.assertEqual(startup.fixture_main(runtime, ['version'], work, stop_parent=True), 125)
                    stop_parent.assert_called_once_with(parent_fd, signal.SIGKILL)
                    with self.assertRaises(OSError): os.fstat(parent_fd)

    def test_temporal_fixture_forces_nonzero_then_timely_or_late_zero(self):
        import re
        import qualify_startup
        import startup_lifecycle as lifecycle
        for late in (False, True):
            with self.subTest(late=late):
                body = qualify_startup._cli_db_backend_transition_exec(late)
                query = body['Cmd'][-1]
                self.assertTrue(query.startswith("BEGIN READ ONLY; SET LOCAL statement_timeout = '5s';"))
                self.assertTrue(query.endswith(' ROLLBACK;'))
                self.assertIn("set_config('env.backend_observations', '0', true)", query)
                self.assertIn("GET STACKED DIAGNOSTICS observed_count = PG_EXCEPTION_DETAIL", query)
                self.assertIn("observed_count IS DISTINCT FROM '2'", query)
                self.assertIn('EXCEPTION WHEN SQLSTATE \'P0001\'', query)
                self.assertIn('temporal predicate result mismatch', query)
                self.assertNotIn('WHEN OTHERS', query)
                captured = re.search(r"BEGIN EXECUTE '((?:[^']|'')*)';", query).group(1).replace("''", "'")
                source = captured.split('FROM ', 1)[1].split(' WHERE pid <> pg_backend_pid()', 1)[0]
                self.assertIn('observation AS MATERIALIZED', source)
                self.assertIn("CASE WHEN n = 1 THEN '192.0.2.1'::inet", source)
                self.assertIn('pg_sleep(CASE WHEN n = 2 THEN ' + ('3.05' if late else '0') + ' ELSE 0 END)', source)
                expected = lifecycle.cli_db_backend_exec('departed')
                prefix = "BEGIN READ ONLY; SET LOCAL statement_timeout = '5s'; SET LOCAL lock_timeout = '1s'; SET LOCAL idle_in_transaction_session_timeout = '5s'; "
                original = expected['Cmd'][-1][len(prefix):-len(' COMMIT;')]
                detail = " USING DETAIL = current_setting('env.backend_observations')"
                self.assertEqual(captured.count(detail), 2)
                self.assertEqual(captured.replace(detail, ''), original.replace('pg_stat_activity', source))
                expected['Cmd'][-1] = query
                self.assertEqual(body, expected)
                self.assertFalse(lifecycle.valid_cli_db_backend_exec(body))
                with self.assertRaises(dev.Refusal):
                    dev._docker_request('POST', '/v1.48/containers/'+'a'*64+'/exec', body, True)
                with patch.object(lifecycle, 'cli_db_backend_exec', return_value=body):
                    self.assertLessEqual(len(dev._docker_request('POST', '/v1.48/containers/'+'a'*64+'/exec', body, True)), 16384)
                with patch.object(lifecycle, 'cli_db_backend_exec', side_effect=AssertionError('recursive builder')):
                    self.assertEqual(qualify_startup._cli_db_backend_transition_exec(late), body)
        with self.assertRaises(dev.Refusal): qualify_startup._cli_db_backend_transition_exec(1)

class ApiDefaultPrivilegesOwner(unittest.TestCase):
    def prepared(self):
        d = CliDbBackendExecutionMatrix().daemon()
        d.guard.api_default_privileges = True
        process = Mock(); process.poll.return_value = None
        d.guard.cli_db_backend_sql('present', process)
        d.guard.auth_cli_terminated = True
        d.guard.cli_db_backend_sql('departed')
        AuthCatalogExecutionMatrix().run_catalog(d)
        return d

    def test_guarded_default_privileges_acceptance(self):
        d = self.prepared()
        d.guard.api_default_privileges_sql()
        self.assertTrue(d.guard.api_default_privileges_verified)
        self.assertEqual(d.catalog_modes[-2:], ['apply', 'verify'])
        with self.assertRaises(dev.Refusal): d.guard.api_default_privileges_sql()
        with patch.object(dev, 'free_ports'): d.guard.finish_execution()
        self.assertTrue(d.guard.cleaned)

    def test_closed_bounded_profiles_preserve_exact_source_and_all_other_tuples(self):
        import copy
        import startup_lifecycle as lifecycle
        route = '/v1.48/containers/' + 'a'*64 + '/exec'
        for mode in ('apply', 'verify'):
            body = lifecycle.api_default_privileges_bounded_exec(mode)
            self.assertTrue(lifecycle.valid_api_default_privileges_bounded_exec(body))
            dev._docker_request('POST', route, body, True)
            query = body['Cmd'][-1]
            for required in ("statement_timeout = '5s'", "lock_timeout = '1s'",
                             "idle_in_transaction_session_timeout = '5s'", 'aclexplode',
                             "d.defaclrole = 'postgres'::regrole", "d.defaclnamespace = 'public'::regnamespace"):
                self.assertIn(required, query)
            if mode == 'apply':
                self.assertEqual(query.count(lifecycle.API_DEFAULT_PRIVILEGES_SQL), 1)
                self.assertIn('observed IS DISTINCT FROM expected', query)
                self.assertLess(query.index('INTO expected'), query.index(lifecycle.API_DEFAULT_PRIVILEGES_SQL))
                self.assertLess(query.index(lifecycle.API_DEFAULT_PRIVILEGES_SQL), query.index('INTO observed'))
                for field in ('defaclrole', 'defaclnamespace', 'defaclobjtype', 'grantor', 'grantee', 'privilege_type', 'is_grantable'):
                    self.assertIn(field, query)
                self.assertIn('WHERE NOT (', query)
            else:
                self.assertTrue(query.startswith('BEGIN READ ONLY;'))
                self.assertNotIn(lifecycle.API_DEFAULT_PRIVILEGES_SQL, query)
                self.assertIn('IF EXISTS (SELECT 1', query)
            for field, value in [('AttachStdin', 0), ('AttachStdout', True), ('AttachStderr', True),
                                 ('Tty', 0), ('Privileged', 0), ('User', 'root'), ('Env', []),
                                 ('Cmd', body['Cmd'] + ['SELECT true']), ('extra', False)]:
                changed = copy.deepcopy(body); changed[field] = value
                self.assertFalse(lifecycle.valid_api_default_privileges_bounded_exec(changed))
                with self.assertRaises(dev.Refusal): dev._docker_request('POST', route, changed, True)
            changed = copy.deepcopy(body); changed['Cmd'][-1] += ' '
            self.assertFalse(lifecycle.valid_api_default_privileges_bounded_exec(changed))
            with self.assertRaises(dev.Refusal): dev._docker_request('POST', route, changed, True)
        with self.assertRaises(dev.Refusal): dev._docker_request('POST', route, lifecycle.api_default_privileges_exec(), True)
        with self.assertRaises(dev.Refusal): lifecycle.api_default_privileges_bounded_exec('post')

    def test_missing_prerequisite_and_ordinary_control_never_dispatch(self):
        for flag in ('api_default_privileges', 'cli_db_backend', 'cli_db_backend_present_verified',
                     'cli_db_backend_departure_verified', 'auth_cli_terminated', 'auth_catalog',
                     'auth_catalog_precondition_verified', 'auth_catalog_verified',
                     'api_default_privileges_request_refused', 'auth_job_exit_verified', 'auth_job_disposed'):
            with self.subTest(flag=flag):
                d = self.prepared(); setattr(d.guard, flag, False)
                count = len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.api_default_privileges_sql()
                self.assertEqual(len(d.events), count)
                self.assertFalse(d.guard.api_default_privileges_verified)
        d = self.prepared()
        with self.assertRaises(dev.Refusal): d.guard.finish_execution()
        self.assertFalse(d.guard.cleaned)

    def test_failed_finish_blocks_all_auth_sql_even_while_phase_five(self):
        d = self.prepared(); d.guard.api_default_privileges_sql()
        with patch.object(d.guard, 'healthy_instance', side_effect=dev.Refusal('startup', 'lost')):
            with self.assertRaises(dev.Refusal): d.guard.finish_execution()
        self.assertEqual(d.guard.phase, 5)
        d.guard.auth_catalog_attempts.clear(); d.guard.cli_db_backend_attempts.clear()
        d.guard.api_default_privileges_attempted = False
        for action in (d.guard.api_default_privileges_sql, lambda: d.guard.auth_catalog_sql('pre'),
                       lambda: d.guard.cli_db_backend_sql('departed')):
            count = len(d.events)
            with self.assertRaises(dev.Refusal): action()
            self.assertEqual(len(d.events), count)

    def test_bad_internal_builder_cannot_dispatch_or_replay(self):
        import startup_lifecycle as lifecycle
        for mode in ('apply', 'verify'):
            d = self.prepared(); original = lifecycle.api_default_privileges_bounded_exec
            def changed(selected):
                body = original(selected)
                if selected == mode: body['Cmd'][-1] += ' '
                return body
            with patch.object(lifecycle, 'api_default_privileges_bounded_exec', side_effect=changed):
                with self.assertRaises(dev.Refusal): d.guard.api_default_privileges_sql()
            self.assertNotIn(mode, d.catalog_modes)
            count = len(d.events)
            with self.assertRaises(dev.Refusal): d.guard.api_default_privileges_sql()
            with self.assertRaises(dev.Refusal): d.guard.finish_execution()
            self.assertEqual(len(d.events), count)
            self.assertFalse(d.guard.api_default_privileges_verified)

    def test_exec_failures_consume_pair_without_fact_finish_or_replay(self):
        for mode in ('apply', 'verify'):
            for fault in ('create_lost', 'create_bad', 'create_id', 'inspect_bad', 'start_lost',
                          'start_bad', 'exit_bad', 'interrupt', 'reused_id'):
                with self.subTest(mode=mode, fault=fault):
                    d = self.prepared(); exchange = d.exchange
                    def broken(method, path, body=None):
                        selected = (mode == 'apply' if path.endswith('/exec') else d.catalog_modes[-1] == mode)
                        if path.endswith('/exec'):
                            selected = ('delta failed' if mode == 'apply' else 'verification failed') in body['Cmd'][-1]
                            if selected:
                                if fault == 'create_lost': raise dev.Refusal('startup', 'lost')
                                if fault == 'create_bad': return 500, None
                                if fault == 'create_id': return 201, {'Id': 'invalid'}
                                if fault == 'reused_id': return 201, {'Id': next(iter(d.guard.exec_ids))}
                        result = exchange(method, path, body)
                        if selected and path.startswith('/v1.48/exec/'):
                            if path.endswith('/start'):
                                if fault == 'start_lost': raise dev.Refusal('startup', 'lost')
                                if fault == 'interrupt': raise KeyboardInterrupt()
                                if fault == 'start_bad': return 500, None
                            elif path.endswith('/json'):
                                if fault == 'inspect_bad': result[1]['ProcessConfig']['user'] = 'root'
                                if fault == 'exit_bad' and d.exec_started: result[1]['ExitCode'] = 1
                        return result
                    d.exchange = broken
                    with self.assertRaises((dev.Refusal, KeyboardInterrupt)): d.guard.api_default_privileges_sql()
                    count = len(d.events)
                    with self.assertRaises(dev.Refusal): d.guard.api_default_privileges_sql()
                    with self.assertRaises(dev.Refusal): d.guard.finish_execution()
                    self.assertEqual(len(d.events), count)
                    self.assertFalse(d.guard.api_default_privileges_verified)
                    if mode == 'apply': self.assertNotIn('verify', d.catalog_modes)

    def test_custody_change_at_each_new_exchange_cannot_publish_or_replay(self):
        # Each proof uses create, pre-start inspect, detached start, final inspect.
        for mode in ('apply', 'verify'):
            for boundary in range(1, 5):
                for defect in ('health', 'instance', 'deadline'):
                    with self.subTest(mode=mode, boundary=boundary, defect=defect):
                        d = self.prepared(); exchange = d.exchange; count = 0
                        def changed(method, path, body=None):
                            nonlocal count
                            selected = (('delta failed' if mode == 'apply' else 'verification failed') in body['Cmd'][-1]
                                        if path.endswith('/exec') else d.catalog_modes[-1] == mode)
                            result = exchange(method, path, body)
                            if selected and (path.endswith('/exec') or path.startswith('/v1.48/exec/')):
                                count += 1
                                if count == boundary:
                                    if defect == 'health': d.row['State']['Health']['Status'] = 'unhealthy'
                                    elif defect == 'instance': d.row['State']['StartedAt'] = '2026-10-19T00:00:00Z'
                                    else: d.deadline = d.guard.deadline = 0
                            return result
                        d.exchange = changed
                        with self.assertRaises(dev.Refusal): d.guard.api_default_privileges_sql()
                        total = len(d.events)
                        with self.assertRaises(dev.Refusal): d.guard.api_default_privileges_sql()
                        with self.assertRaises(dev.Refusal): d.guard.finish_execution()
                        self.assertEqual(len(d.events), total)
                        self.assertFalse(d.guard.api_default_privileges_verified)

    def test_new_owner_semantic_matrix_acceptance(self):
        import qualify_startup
        body, count = qualify_startup._api_default_privileges_owner_semantic_exec('post')
        self.assertEqual(count, 11)
        self.assertIn('owner ACL rollback failed', body['Cmd'][-1])

    def test_new_owner_semantic_matrix_preserves_bounds_and_production_predicates(self):
        import qualify_startup
        import startup_lifecycle as lifecycle
        body, count = qualify_startup._api_default_privileges_owner_semantic_exec('post')
        query = body['Cmd'][-1]
        self.assertEqual(count, 11)
        self.assertTrue(query.startswith("BEGIN; SET LOCAL statement_timeout = '5s'; SET LOCAL lock_timeout = '1s'; SET LOCAL idle_in_transaction_session_timeout = '5s'; "))
        original = qualify_startup._original_auth_catalog_exec('post')['Cmd'][-1]
        predicate = original[original.index('DO $$'): -len(' COMMIT;')]
        self.assertTrue(query.endswith(predicate + ' ROLLBACK;'))
        self.assertIn('SET LOCAL ROLE postgres;', query)
        self.assertIn('GRANT EXECUTE ON FUNCTIONS TO anon;', query)
        self.assertIn('d.defaclnamespace=0', query)
        self.assertIn("EXCEPTION WHEN SQLSTATE 'ZX001' THEN NULL", query)
        self.assertEqual(query.count("EXCEPTION WHEN SQLSTATE 'P0001'"), 5)
        self.assertNotIn('WHEN OTHERS', query)
        unquoted = query.replace("''", "'")
        for mode, copies in [('apply', 1), ('verify', 1)]:
            command = lifecycle.api_default_privileges_bounded_exec(mode)['Cmd'][-1]
            block = command[command.index('DO $api_defaults$'):-len(' COMMIT;')]
            self.assertEqual(unquoted.count(block), copies)
        self.assertIn('global target grant lost', query)
        self.assertIn('owner ACL oracle insensitive', query)
        self.assertEqual(qualify_startup._api_default_privileges_owner_semantic_exec('pre'),
                         (qualify_startup._original_auth_catalog_exec('pre'), 0))
        self.assertEqual(qualify_startup._api_default_privileges_owner_semantic_exec('post'), (body, count))
        with self.assertRaises(dev.Refusal): qualify_startup._api_default_privileges_owner_semantic_exec('apply')

    def test_new_owner_semantic_matrix_requires_exact_existing_qualifier_hook(self):
        import qualify_startup
        import startup_lifecycle as lifecycle
        route = '/v1.48/containers/' + 'a'*64 + '/exec'
        body, _ = qualify_startup._api_default_privileges_owner_semantic_exec('post')
        with self.assertRaises(dev.Refusal): dev._docker_request('POST', route, body, True)
        with patch.object(lifecycle, 'auth_catalog_exec', side_effect=lambda mode: qualify_startup._api_default_privileges_owner_semantic_exec(mode)[0]):
            raw = dev._docker_request('POST', route, body, True)
            self.assertLess(len(raw), 16384)
            with self.assertRaises(dev.Refusal):
                dev._docker_request('POST', route, lifecycle.api_default_privileges_exec(), True)
        with self.assertRaises(dev.Refusal): dev._docker_request('POST', route, body, True)

    def test_prerequisite_finish_is_terminal_for_each_auth_sql_method(self):
        for selected in ('api', 'catalog', 'backend'):
            with self.subTest(method=selected):
                d = self.prepared(); d.guard.auth_job_disposed = False
                count = len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.finish_execution()
                self.assertEqual(len(d.events), count)
                d.guard.auth_job_disposed = True
                d.guard.auth_catalog_attempts.clear()
                d.guard.cli_db_backend_attempts.clear()
                d.guard.auth_job_create_attempted = False
                action = {'api': d.guard.api_default_privileges_sql,
                          'catalog': lambda: d.guard.auth_catalog_sql('post'),
                          'backend': lambda: d.guard.cli_db_backend_sql('departed')}[selected]
                with self.assertRaises(dev.Refusal): action()
                self.assertEqual(len(d.events), count)
                self.assertTrue(d.guard._finish_attempted)
                self.assertFalse(d.guard.api_default_privileges_verified)

    def test_owner_matrix_proves_grantability_and_unrelated_schema_preservation(self):
        import qualify_startup
        body, count = qualify_startup._api_default_privileges_owner_semantic_exec('post')
        self.assertEqual(count, 11)
        query = body['Cmd'][-1]
        for required in ('WITH GRANT OPTION', 'REVOKE GRANT OPTION FOR EXECUTE',
                         'FOR ROLE postgres IN SCHEMA env_owner_acl_other',
                         'preserved grantability lost', 'unrelated schema grant lost'):
            self.assertIn(required, query)
        self.assertEqual(query.count("EXCEPTION WHEN SQLSTATE 'P0001'"), 5)


class PostAuthSetupTailOwner(unittest.TestCase):
    """Real private filesystem plus existing independent owner/SQL daemon."""
    def prepared(self):
        import os
        import tempfile
        import startup
        d = ApiDefaultPrivilegesOwner().prepared()
        d.guard.api_default_privileges_sql()
        d.guard.post_auth_setup_tail = True
        temporary = tempfile.TemporaryDirectory(prefix='env-owner-tail-')
        self.addCleanup(temporary.cleanup)
        work = Path(temporary.name)
        startup.initialize_workdir(work, d.target, d.fixture['run_id'])
        (work / 'fixture.json').write_bytes(b'{}')
        (work / 'events.json').write_bytes(b'[]')
        for name in ('docker', 'podman'):
            (work / 'bin' / name).write_bytes(b'fixture')
            (work / 'bin' / name).chmod(0o700)
        root = os.open(work, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        self.addCleanup(os.close, root)
        d.guard._fixture = (work, root, startup.source_snapshot(), dev.digest(b'{}'),
                            {name: dev.digest(b'fixture') for name in ('docker', 'podman')})
        return d, work

    def test_selected_tail_exact_bytes_no_sql_and_fact_only_after_cleanup(self):
        import startup
        d, work = self.prepared()
        deadline = d.guard.deadline
        modes = list(d.catalog_modes)
        d.guard.complete_post_auth_setup_tail()
        marker = work / 'supabase/.branches/_current_branch'
        self.assertEqual(marker.read_bytes(), b'main')
        self.assertEqual(marker.stat().st_mode & 0o777, 0o644)
        self.assertEqual(marker.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(d.guard.deadline, deadline)
        self.assertEqual(d.catalog_modes, modes)
        self.assertFalse(d.guard.owner_post_auth_setup_tail_verified)
        with self.assertRaises(dev.Refusal): startup.check_workdir(work, d.target, d.fixture['run_id'], after=True, fixture=True)
        with self.assertRaises(dev.Refusal): d.guard.complete_post_auth_setup_tail()
        with patch.object(dev, 'free_ports'): d.guard.finish_execution()
        self.assertTrue(d.guard.cleaned and d.guard.owner_post_auth_setup_tail_verified)
        with self.assertRaises(dev.Refusal): d.guard.finish_execution()

    def test_missing_prerequisites_phase_and_terminal_finish_never_mutate(self):
        for flag in ('post_auth_setup_tail', 'api_default_privileges', 'api_default_privileges_verified',
                     'auth_cli_terminated', 'cli_db_backend', 'auth_catalog', 'cli_db_backend_present_verified', 'cli_db_backend_departure_verified',
                     'auth_catalog_precondition_verified', 'auth_catalog_verified', 'api_default_privileges_request_refused',
                     'auth_job_exit_verified', 'auth_job_disposed', '_fixture', 'phase', '_finish_attempted'):
            with self.subTest(flag=flag):
                d, work = self.prepared()
                original = getattr(d.guard, flag, False)
                setattr(d.guard, flag, True if flag == '_finish_attempted' else None if flag == '_fixture' else False)
                with self.assertRaises(dev.Refusal): d.guard.complete_post_auth_setup_tail()
                if flag != '_finish_attempted': setattr(d.guard, flag, original)
                with self.assertRaises(dev.Refusal): d.guard.complete_post_auth_setup_tail()
                self.assertFalse((work / 'supabase/.branches').exists())
                self.assertFalse(d.guard.owner_post_auth_setup_tail_verified)

    def test_preexisting_config_roles_and_branch_contamination_not_adopted(self):
        for fault in ('config', 'roles', 'branch', 'branch-symlink'):
            with self.subTest(fault=fault):
                d, work = self.prepared()
                if fault == 'config': (work / 'supabase/config.toml').write_bytes(b'changed')
                elif fault == 'roles': (work / 'supabase/roles.sql').write_bytes(b'')
                elif fault == 'branch': (work / 'supabase/.branches').mkdir(mode=0o700)
                else: (work / 'supabase/.branches').symlink_to(work / 'tmp', target_is_directory=True)
                with self.assertRaises(dev.Refusal): d.guard.complete_post_auth_setup_tail()
                self.assertTrue(d.guard.post_auth_setup_tail_attempted)
                with self.assertRaises(dev.Refusal): d.guard.complete_post_auth_setup_tail()
                self.assertFalse(d.guard.owner_post_auth_setup_tail_verified)

    def test_changed_replaced_unsafe_or_extra_artifacts_block_custody_and_cleanup(self):
        import os
        for fault in ('bytes', 'file-replace', 'directory-replace', 'parent-replace', 'file-mode',
                      'directory-mode', 'extra', 'symlink', 'hardlink', 'config', 'roles'):
            with self.subTest(fault=fault):
                d, work = self.prepared()
                d.guard.complete_post_auth_setup_tail()
                branch = work / 'supabase/.branches'
                marker = branch / '_current_branch'
                if fault == 'bytes': marker.write_bytes(b'main\n')
                elif fault == 'file-replace':
                    marker.rename(work / 'tmp/old'); marker.write_bytes(b'main'); marker.chmod(0o644)
                elif fault == 'directory-replace':
                    branch.rename(work / 'tmp/old'); branch.mkdir(mode=0o700)
                    marker.write_bytes(b'main'); marker.chmod(0o644)
                elif fault == 'parent-replace':
                    (work / 'supabase').rename(work / 'tmp/old')
                    (work / 'supabase').mkdir(mode=0o700)
                    (work / 'supabase/config.toml').write_bytes(dev.configuration(d.target, d.fixture['run_id']))
                    (work / 'supabase/config.toml').chmod(0o600)
                    (work / 'tmp/old/.branches').rename(branch)
                elif fault == 'file-mode': marker.chmod(0o600)
                elif fault == 'directory-mode': branch.chmod(0o755)
                elif fault == 'extra': (branch / 'extra').write_bytes(b'')
                elif fault == 'symlink':
                    marker.rename(work / 'tmp/old'); marker.symlink_to(work / 'tmp/old')
                elif fault == 'hardlink': os.link(marker, work / 'tmp/link')
                elif fault == 'config': (work / 'supabase/config.toml').write_bytes(b'changed')
                else: (work / 'supabase/roles.sql').write_bytes(b'')
                with self.assertRaises((dev.Refusal, OSError)): d.guard.current()
                before = len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
                self.assertEqual(len(d.events), before)
                self.assertFalse(d.guard.owner_post_auth_setup_tail_verified)

    def test_deadline_and_interrupted_write_consume_attempt_without_retry(self):
        import os
        for fault in ('expired', 'write-interrupt', 'late-write'):
            with self.subTest(fault=fault):
                d, work = self.prepared()
                original = os.fsync
                def fsync(fd):
                    if fault == 'write-interrupt': raise KeyboardInterrupt()
                    original(fd)
                    d.deadline = d.guard.deadline = 0
                if fault == 'expired': d.deadline = d.guard.deadline = 0
                with patch.object(os, 'fsync', side_effect=fsync):
                    with self.assertRaises((dev.Refusal, KeyboardInterrupt)): d.guard.complete_post_auth_setup_tail()
                self.assertTrue(d.guard.post_auth_setup_tail_attempted)
                self.assertFalse(d.guard.owner_post_auth_setup_tail_verified)
                before = len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.complete_post_auth_setup_tail()
                with self.assertRaises(dev.Refusal): d.guard.finish_execution()
                self.assertEqual(len(d.events), before)
                if fault == 'expired': self.assertFalse((work / 'supabase/.branches').exists())
                else: self.assertTrue(d.guard.ownership_lost)

    def test_missing_tail_completion_blocks_terminal_finish_and_replay(self):
        d, work = self.prepared()
        before = len(d.events)
        with self.assertRaises(dev.Refusal): d.guard.finish_execution()
        with self.assertRaises(dev.Refusal): d.guard.complete_post_auth_setup_tail()
        self.assertEqual(len(d.events), before)
        self.assertFalse((work / 'supabase/.branches').exists())

    def test_final_cleanup_observation_cannot_publish_changed_artifact(self):
        d, work = self.prepared()
        d.guard.complete_post_auth_setup_tail()
        exchange = d.exchange
        def changed(method, path, body=None):
            result = exchange(method, path, body)
            if method == 'GET' and path == '/v1.48/networks/' + 'b'*64 and result[0] == 404:
                (work / 'supabase/.branches/_current_branch').write_bytes(b'evil')
            return result
        d.exchange = changed
        with patch.object(dev, 'free_ports'):
            with self.assertRaises(dev.Refusal): d.guard.finish_execution()
        self.assertTrue(d.guard.cleaned)
        self.assertFalse(d.guard.owner_post_auth_setup_tail_verified)
        with self.assertRaises(dev.Refusal): d.guard.finish_execution()

    def test_artifact_owner_mismatch_refuses_custody(self):
        import os
        for component in ('.branches', '.branches/_current_branch'):
            with self.subTest(component=component):
                d, work = self.prepared()
                d.guard.complete_post_auth_setup_tail()
                original = os.fstat
                inode = (work / 'supabase' / component).stat().st_ino
                def wrong_owner(fd):
                    info = original(fd)
                    if info.st_ino != inode: return info
                    values = list(info); values[4] = os.getuid() + 1
                    return os.stat_result(values)
                with patch.object(os, 'fstat', side_effect=wrong_owner):
                    with self.assertRaises(dev.Refusal): d.guard.current()
                self.assertTrue(d.guard.ownership_lost)
                self.assertFalse(d.guard.owner_post_auth_setup_tail_verified)

    def test_tail_refuses_directory_replacement_at_creation_boundary(self):
        import os
        d, work = self.prepared()
        original = os.mkdir
        raced = []
        branch = work / 'supabase/.branches'
        def replace(name, mode=0o777, *, dir_fd=None):
            result = original(name, mode, dir_fd=dir_fd)
            if str(name) == '.branches' or Path(name).name.startswith('.owner-tail-'):
                if branch.exists(): branch.rename(work / 'tmp/displaced-branch')
                original(branch, 0o700)
                raced.append(branch.stat().st_ino)
            return result
        with patch.object(os, 'mkdir', side_effect=replace):
            with self.assertRaises((dev.Refusal, OSError)): d.guard.complete_post_auth_setup_tail()
        self.assertEqual(len(raced), 1)
        self.assertEqual(branch.stat().st_ino, raced[0])
        self.assertEqual(list(branch.iterdir()), [])
        self.assertFalse(d.guard.owner_post_auth_setup_tail_verified)
        with self.assertRaises(dev.Refusal): d.guard.complete_post_auth_setup_tail()

    def test_tail_refuses_parent_replacement_after_final_validation(self):
        d, work = self.prepared()
        health, check = d.guard.auth_pg_current, d.guard.check
        armed = [False]
        raced = []
        def observe_health():
            result = health()
            armed[0] = True
            return result
        def replace_after_check():
            result = check()
            if armed[0] and not raced:
                parent = work / 'supabase'
                parent.rename(work / 'tmp/displaced-parent')
                parent.mkdir(mode=0o700)
                config = parent / 'config.toml'
                config.write_bytes(dev.configuration(d.target, d.fixture['run_id']))
                config.chmod(0o600)
                raced.append(parent.stat().st_ino)
            return result
        with patch.object(d.guard, 'check', side_effect=replace_after_check), \
                patch.object(d.guard, 'auth_pg_current', side_effect=observe_health):
            with self.assertRaises(dev.Refusal): d.guard.complete_post_auth_setup_tail()
        self.assertEqual(len(raced), 1)
        self.assertFalse((work / 'supabase/.branches').exists())
        self.assertFalse((work / 'tmp/displaced-parent/.branches').exists())
        self.assertFalse(d.guard.owner_post_auth_setup_tail_verified)
        with self.assertRaises(dev.Refusal): d.guard.complete_post_auth_setup_tail()

    def test_tail_publication_refuses_destination_created_at_atomic_publish(self):
        import ctypes
        import errno
        from types import SimpleNamespace
        for nonempty in (False, True):
            with self.subTest(nonempty=nonempty):
                d, work = self.prepared()
                library = ctypes.CDLL(None, use_errno=True)
                publish = library.renameat2
                publish.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
                publish.restype = ctypes.c_int
                branch = work / 'supabase/.branches'
                rival = []
                def race(*args):
                    branch.mkdir(mode=0o700)
                    if nonempty: (branch / 'unowned').write_bytes(b'preserve')
                    rival.append(branch.stat().st_ino)
                    return publish(*args)
                with patch.object(resources.ctypes, 'CDLL', return_value=SimpleNamespace(renameat2=Mock(side_effect=race))):
                    with self.assertRaises(OSError) as caught: d.guard.complete_post_auth_setup_tail()
                self.assertEqual(caught.exception.errno, errno.EEXIST)
                self.assertEqual(branch.stat().st_ino, rival[0])
                self.assertEqual([entry.name for entry in branch.iterdir()], ['unowned'] if nonempty else [])
                if nonempty: self.assertEqual((branch / 'unowned').read_bytes(), b'preserve')
                self.assertTrue(d.guard.post_auth_setup_tail_attempted and d.guard.ownership_lost)
                self.assertFalse(d.guard.owner_post_auth_setup_tail_verified)
                before = len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.complete_post_auth_setup_tail()
                with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
                self.assertEqual(len(d.events), before)

    def test_tail_oserrors_preserve_original_failure_and_uncertain_cleanup(self):
        import errno
        import os
        for boundary in ('mkdir', 'directory-open', 'open', 'write', 'file-sync', 'directory-sync'):
            with self.subTest(boundary=boundary):
                d, work = self.prepared()
                deadline = d.guard.deadline
                failure = OSError(errno.EIO, 'injected owner artifact operation')
                mkdir, open_file, fdopen, sync = os.mkdir, os.open, os.fdopen, os.fsync
                def fail_mkdir(name, *args, **kwargs):
                    if Path(name).name.startswith('.owner-tail-'): raise failure
                    return mkdir(name, *args, **kwargs)
                def fail_open(name, *args, **kwargs):
                    if ((boundary == 'open' and name == '_current_branch')
                            or (boundary == 'directory-open' and Path(name).name.startswith('.owner-tail-'))):
                        raise failure
                    return open_file(name, *args, **kwargs)
                class FailingWrite:
                    def __init__(self, stream): self.stream = stream
                    def __enter__(self): self.stream.__enter__(); return self
                    def __exit__(self, *args): return self.stream.__exit__(*args)
                    def fileno(self): return self.stream.fileno()
                    def write(self, raw): raise failure
                def fail_fdopen(*args, **kwargs):
                    stream = fdopen(*args, **kwargs)
                    return FailingWrite(stream) if len(args) > 1 and args[1] == 'wb' else stream
                calls = []
                def fail_sync(fd):
                    calls.append(fd)
                    if len(calls) == (1 if boundary == 'file-sync' else 2): raise failure
                    return sync(fd)
                name, replacement = (('mkdir', fail_mkdir) if boundary == 'mkdir' else
                                     ('open', fail_open) if boundary in ('open', 'directory-open') else
                                     ('fdopen', fail_fdopen) if boundary == 'write' else ('fsync', fail_sync))
                with patch.object(os, name, side_effect=replacement):
                    with self.assertRaises(OSError) as caught: d.guard.complete_post_auth_setup_tail()
                self.assertIs(caught.exception, failure)
                self.assertEqual(d.guard.deadline, deadline)
                self.assertTrue(d.guard.post_auth_setup_tail_attempted and d.guard.ownership_lost)
                self.assertFalse(d.guard._tail_completed or d.guard.owner_post_auth_setup_tail_verified)
                before = len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.complete_post_auth_setup_tail()
                with self.assertRaises(dev.Refusal): d.guard.finish_execution()
                with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
                self.assertEqual(len(d.events), before)
                self.assertIsNotNone(d.row)

    def test_tail_tmp_substitution_after_validation_creates_no_foreign_artifact(self):
        import tempfile
        for symlink in (False, True):
            with self.subTest(symlink=symlink):
                d, work = self.prepared()
                foreign = tempfile.TemporaryDirectory(prefix='env-tail-foreign-')
                self.addCleanup(foreign.cleanup)
                outside = Path(foreign.name)
                destination = outside / 'destination'
                destination.mkdir(mode=0o700)
                health, check = d.guard.auth_pg_current, d.guard.check
                armed, raced = [False], []
                def observe_health():
                    result = health()
                    armed[0] = True
                    return result
                def replace_after_check():
                    result = check()
                    if armed[0] and not raced:
                        (work / 'tmp').rename(outside / 'retained-tmp')
                        if symlink: (work / 'tmp').symlink_to(destination, target_is_directory=True)
                        else: (work / 'tmp').mkdir(mode=0o700)
                        raced.append(True)
                    return result
                with patch.object(d.guard, 'check', side_effect=replace_after_check), \
                        patch.object(d.guard, 'auth_pg_current', side_effect=observe_health):
                    with self.assertRaises((dev.Refusal, OSError)): d.guard.complete_post_auth_setup_tail()
                self.assertEqual(raced, [True])
                self.assertEqual(list(destination.iterdir()), [])
                self.assertEqual(list((outside / 'retained-tmp').iterdir()), [])
                if not symlink: self.assertEqual(list((work / 'tmp').iterdir()), [])
                self.assertFalse((work / 'supabase/.branches').exists())
                self.assertTrue(d.guard.post_auth_setup_tail_attempted and d.guard.ownership_lost)
                self.assertFalse(d.guard._tail_completed or d.guard.owner_post_auth_setup_tail_verified)
                before = len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.complete_post_auth_setup_tail()
                with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
                self.assertEqual(len(d.events), before)
                self.assertIsNotNone(d.row)

    def test_tail_staging_mutation_and_publication_use_retained_tmp_descriptor(self):
        import ctypes
        import os
        import tempfile
        from types import SimpleNamespace
        for boundary in ('mkdir', 'publish'):
            with self.subTest(boundary=boundary):
                d, work = self.prepared()
                foreign = tempfile.TemporaryDirectory(prefix='env-tail-foreign-')
                self.addCleanup(foreign.cleanup)
                outside = Path(foreign.name)
                destination = outside / 'destination'
                destination.mkdir(mode=0o700)
                raced = []
                def substitute():
                    (work / 'tmp').rename(outside / 'retained-tmp')
                    (work / 'tmp').symlink_to(destination, target_is_directory=True)
                    raced.append(True)
                mkdir = os.mkdir
                def race_mkdir(name, *args, **kwargs):
                    if Path(name).name.startswith('.owner-tail-'):
                        self.assertIn('dir_fd', kwargs)
                        substitute()
                    return mkdir(name, *args, **kwargs)
                library = ctypes.CDLL(None, use_errno=True)
                publish = library.renameat2
                publish.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
                publish.restype = ctypes.c_int
                def race_publish(source_fd, source, destination_fd, destination_name, flags):
                    self.assertGreaterEqual(source_fd, 0)
                    self.assertGreaterEqual(destination_fd, 0)
                    substitute()
                    return publish(source_fd, source, destination_fd, destination_name, flags)
                context = (patch.object(os, 'mkdir', side_effect=race_mkdir) if boundary == 'mkdir' else
                           patch.object(resources.ctypes, 'CDLL', return_value=SimpleNamespace(renameat2=Mock(side_effect=race_publish))))
                with context:
                    with self.assertRaises((dev.Refusal, OSError)): d.guard.complete_post_auth_setup_tail()
                self.assertEqual(raced, [True])
                self.assertEqual(list(destination.iterdir()), [])
                self.assertTrue(d.guard.post_auth_setup_tail_attempted and d.guard.ownership_lost)
                self.assertFalse(d.guard._tail_completed or d.guard.owner_post_auth_setup_tail_verified)
                before = len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.complete_post_auth_setup_tail()
                with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
                self.assertEqual(len(d.events), before)
                self.assertIsNotNone(d.row)


class KongBoundaryOwner(unittest.TestCase):
    def prepared(self):
        owner = PostAuthSetupTailOwner()
        d, work = owner.prepared()
        self.addCleanup(owner.doCleanups)
        d.guard.complete_post_auth_setup_tail()
        d.guard.kong_boundary = True
        return d, work

    def test_boundary_no_sql_no_kong_dispatch_fact_after_cleanup_only(self):
        d, work = self.prepared()
        deadline, modes = d.guard.deadline, list(d.catalog_modes)
        d.guard.verify_kong_boundary()
        self.assertEqual(d.guard.deadline, deadline)
        self.assertEqual(d.catalog_modes, modes)
        self.assertFalse(d.guard.owner_kong_boundary_verified)
        self.assertTrue(d.guard._kong_boundary_completed)
        self.assertFalse(any('supabase_kong_' in path for _, path, _ in d.events))
        before = len(d.events)
        with self.assertRaises(dev.Refusal): d.guard.verify_kong_boundary()
        self.assertEqual(len(d.events), before)
        with patch.object(dev, 'free_ports'): d.guard.finish_execution()
        self.assertTrue(d.guard.cleaned and d.guard.owner_kong_boundary_verified)

    def test_current_image_and_both_closed_profiles_checked_without_exchange(self):
        import create_profile
        d, _ = self.prepared()
        selected = next(ref for ref in d.images if '/kong@' in ref)
        before = len(d.events)
        with patch.object(create_profile, 'validate_kong_image_config', wraps=create_profile.validate_kong_image_config) as config_validator, patch.object(dev, '_docker_request', wraps=dev._docker_request) as classifier:
            d.guard.verify_kong_boundary()
        self.assertGreaterEqual(sum(path == '/v1.48/images/' + selected + '/json'
                             for _, path, _ in d.events[before:]), 1)
        self.assertEqual(config_validator.call_count, 1)
        creates = [call.args for call in classifier.call_args_list
                   if call.args[0] == 'POST' and '/containers/create?' in call.args[1]]
        self.assertEqual(len(creates), 2)
        self.assertEqual([item[2]['HostConfig']['RestartPolicy']['Name'] for item in creates],
                         ['unless-stopped', 'no'])

    def test_image_default_and_disposable_corruption_consume_attempt_without_disclosure(self):
        import create_profile
        for seam in ('env', 'label', 'health', 'shell', 'missing', 'profile'):
            with self.subTest(seam=seam):
                d, _ = self.prepared()
                if seam == 'env': d.kong_config['Env'].append('private-input-sentinel')
                elif seam == 'label': d.kong_config['Labels']['extra'] = 'private-input-sentinel'
                elif seam == 'health': d.kong_config['Healthcheck']['Retries'] = True
                elif seam == 'shell': d.kong_config['Shell'] = ['private-input-sentinel']
                elif seam == 'missing': d.kong_config.pop('Volumes')
                original = create_profile.kong_disposable_execution_request
                def changed(*args):
                    request = original(*args)
                    if seam == 'profile': request['body']['HostConfig']['Privileged'] = True
                    return request
                with patch.object(create_profile, 'kong_disposable_execution_request', side_effect=changed), self.assertRaises(dev.Refusal) as refused:
                    d.guard.verify_kong_boundary()
                self.assertEqual(refused.exception.code, 'unsafe_create')
                self.assertNotIn('private-input-sentinel', str(refused.exception))
                self.assertTrue(d.guard.kong_boundary_attempted)
                self.assertFalse(d.guard._kong_boundary_completed or d.guard.owner_kong_boundary_verified)
                before = len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.verify_kong_boundary()
                self.assertEqual(len(d.events), before)
                self.assertFalse(any('supabase_kong_' in path for _, path, _ in d.events))

    def test_pg_checks_surround_image_profile_and_classifier_validation(self):
        import create_profile
        d, _ = self.prepared()
        order = []
        pg, image, profile, classify = (d.guard.auth_pg_current, create_profile.validate_kong_image_config,
                                      create_profile.validate_kong_disposable_execution_request, dev._docker_request)
        def checked_pg(): order.append('pg'); return pg()
        def checked_image(value): order.append('image'); return image(value)
        def checked_profile(*args): order.append('profile'); return profile(*args)
        def checked_classify(*args): order.append('classifier'); return classify(*args)
        with patch.object(d.guard, 'auth_pg_current', side_effect=checked_pg), patch.object(create_profile, 'validate_kong_image_config', side_effect=checked_image), patch.object(create_profile, 'validate_kong_disposable_execution_request', side_effect=checked_profile), patch.object(dev, '_docker_request', side_effect=checked_classify):
            d.guard.verify_kong_boundary()
        self.assertEqual(order, ['pg', 'image', 'profile', 'pg', 'classifier', 'classifier', 'pg'])

    def explicit_image_exchange(self, daemon, effect, reached):
        # Direct caller identity isolates the new read from existing descriptor custody
        # inspections, which must keep receiving their unmodified responses.
        import sys
        original = daemon.exchange
        code = resources.FreshGuard.verify_kong_boundary.__code__
        def exchange(method, path, body=None):
            direct_boundary = sys._getframe(1).f_code is code
            status, row = original(method, path, body)
            if direct_boundary and method == 'GET' and '/images/' in path:
                reached.append(True)
                return effect(status, row)
            return status, row
        return patch.object(daemon, 'exchange', new=exchange)

    def assert_terminal_kong_failure(self, daemon):
        self.assertTrue(daemon.guard.kong_boundary_attempted)
        self.assertFalse(daemon.guard._kong_boundary_completed or daemon.guard.owner_kong_boundary_verified)
        before = len(daemon.events)
        with self.assertRaises(dev.Refusal) as replay:
            daemon.guard.verify_kong_boundary()
        self.assertEqual(replay.exception.code, 'invalid_owner_handoff')
        self.assertEqual(len(daemon.events), before)
        self.assertFalse(any('supabase_kong_' in path for _, path, _ in daemon.events))

    def test_explicit_image_response_refusals_preserve_prior_descriptor_custody(self):
        for case in ('status', 'type', 'id', 'os', 'architecture', 'variant'):
            with self.subTest(case=case):
                d, _ = self.prepared()
                reached = []
                def changed(status, row):
                    if case == 'status': return 404, row
                    if case == 'type': return status, []
                    key = {'id': 'Id', 'os': 'Os', 'architecture': 'Architecture', 'variant': 'Variant'}[case]
                    row[key] = 'private-input-sentinel'
                    return status, row
                with self.explicit_image_exchange(d, changed, reached), self.assertRaises(dev.Refusal) as refused:
                    d.guard.verify_kong_boundary()
                self.assertEqual(reached, [True])
                self.assertEqual((refused.exception.stage, refused.exception.code), ('startup', 'execution_image_changed'))
                self.assertNotIn('private-input-sentinel', str(refused.exception))
                self.assert_terminal_kong_failure(d)

    def test_explicit_image_exchange_errors_propagate_and_consume_attempt(self):
        for error in (KeyboardInterrupt(), dev.Refusal('docker', 'docker_timeout'),
                      dev.Refusal('docker', 'docker_unavailable')):
            with self.subTest(kind=type(error).__name__, code=getattr(error, 'code', None)):
                d, _ = self.prepared()
                reached = []
                def failed(status, row): raise error
                with self.explicit_image_exchange(d, failed, reached), self.assertRaises(type(error)) as caught:
                    d.guard.verify_kong_boundary()
                self.assertIs(caught.exception, error)
                self.assertEqual(reached, [True])
                self.assert_terminal_kong_failure(d)

    def test_second_disposable_classifier_success_and_unexpected_refusal_are_terminal(self):
        for unexpected in (None, dev.Refusal('docker', 'private-classifier-failure')):
            with self.subTest(kind='success' if unexpected is None else 'refusal'):
                d, _ = self.prepared()
                original = dev._docker_request
                calls = []
                def classifier(*args):
                    calls.append(args[2]['HostConfig']['RestartPolicy']['Name'])
                    if len(calls) == 1: return original(*args)
                    if unexpected is not None: raise unexpected
                    return None
                with patch.object(dev, '_docker_request', side_effect=classifier), self.assertRaises(dev.Refusal) as caught:
                    d.guard.verify_kong_boundary()
                self.assertEqual(calls, ['unless-stopped', 'no'])
                if unexpected is not None: self.assertIs(caught.exception, unexpected)
                else: self.assertEqual(caught.exception.code, 'invalid_owner_handoff')
                self.assert_terminal_kong_failure(d)

    def test_missing_prerequisites_terminal_and_repaired_replay_refused(self):
        for flag in ('kong_boundary', 'post_auth_setup_tail', '_tail_completed', 'api_default_privileges_verified',
                     'auth_cli_terminated', 'cli_db_backend_present_verified', 'cli_db_backend_departure_verified',
                     'auth_catalog_precondition_verified', 'auth_catalog_verified',
                     'api_default_privileges_request_refused', 'auth_job_exit_verified', 'auth_job_disposed'):
            with self.subTest(flag=flag):
                d, _ = self.prepared()
                setattr(d.guard, flag, False)
                before = len(d.events)
                with self.assertRaises(dev.Refusal) as caught: d.guard.verify_kong_boundary()
                self.assertEqual(caught.exception.code, 'invalid_owner_handoff')
                setattr(d.guard, flag, True)
                with self.assertRaises(dev.Refusal): d.guard.verify_kong_boundary()
                self.assertEqual(len(d.events), before)
                self.assertFalse(d.guard.owner_kong_boundary_verified or d.guard._kong_boundary_completed)
        for field, value in [('phase', 7), ('_finish_attempted', True), ('_fixture', None), ('_tail_custody', None)]:
            d, _ = self.prepared(); setattr(d.guard, field, value)
            with self.assertRaises(dev.Refusal): d.guard.verify_kong_boundary()
            self.assertTrue(d.guard.kong_boundary_attempted)

    def test_altered_request_archive_allowlist_expansion_and_cleanup_failure_no_fact(self):
        import create_profile
        import startup_lifecycle
        import copy
        for seam in ('request', 'files', 'archive', 'allowlist', 'cleanup'):
            d, _ = self.prepared()
            if seam == 'cleanup':
                d.guard.verify_kong_boundary()
                with patch.object(d.guard, 'cleanup_execution', side_effect=dev.Refusal('startup', 'execution_cleanup_unresolved')):
                    with self.assertRaises(dev.Refusal): d.guard.finish_execution()
            else:
                if seam == 'request':
                    original = create_profile.kong_execution_request
                    def changed(f):
                        body = original(f); body['body']['HostConfig']['PortBindings']['8000/tcp'][0]['HostIp'] = '0.0.0.0'; return body
                    context = patch.object(create_profile, 'kong_execution_request', side_effect=changed)
                    # Validator has its own closed expected profile, so corrupt at owner handoff only.
                    count = [0]
                    def once(f):
                        count[0] += 1
                        return changed(f) if count[0] == 1 else original(f)
                    context = patch.object(create_profile, 'kong_execution_request', side_effect=once)
                elif seam == 'files':
                    original = create_profile.kong_transfer_files; count = [0]
                    def changed(f):
                        count[0] += 1; files = original(f)
                        if count[0] == 1: files['home/kong/localhost.key'] = b'private-input-sentinel'
                        return files
                    context = patch.object(create_profile, 'kong_transfer_files', side_effect=changed)
                elif seam == 'archive': context = patch.object(startup_lifecycle, 'kong_archive', return_value=b'private-input-sentinel')
                else: context = patch.object(dev, '_docker_request', return_value=None)
                with context, self.assertRaises(dev.Refusal): d.guard.verify_kong_boundary()
                self.assertFalse(d.guard._kong_boundary_completed)
                with self.assertRaises(dev.Refusal): d.guard.verify_kong_boundary()
                with self.assertRaises(dev.Refusal): d.guard.finish_execution()
            self.assertFalse(d.guard.owner_kong_boundary_verified)
            self.assertFalse(any('supabase_kong_' in path for _, path, _ in d.events))

    def test_deadline_cancellation_custody_and_selected_image_change_consume_attempt(self):
        import create_profile
        import time
        for seam in ('deadline', 'cancel', 'fixture', 'image', 'pg'):
            d, work = self.prepared()
            if seam == 'deadline':
                d.deadline = d.guard.deadline = time.monotonic() - 1
                context = patch.object(create_profile, 'kong_request', wraps=create_profile.kong_request)
            elif seam == 'cancel': context = patch.object(create_profile, 'kong_request', side_effect=KeyboardInterrupt())
            elif seam == 'fixture':
                (work / 'bin/docker').write_bytes(b'changed')
                context = patch.object(create_profile, 'kong_request', wraps=create_profile.kong_request)
            elif seam == 'image':
                selected = next(ref for ref in d.guard.plan if '/kong@' in ref)
                d.guard.plan = dict(d.guard.plan, **{selected: 'sha256:' + '0'*64})
                context = patch.object(create_profile, 'kong_request', wraps=create_profile.kong_request)
            else:
                d.row['State']['Health']['Status'] = 'unhealthy'
                context = patch.object(create_profile, 'kong_request', wraps=create_profile.kong_request)
            with context, self.assertRaises((dev.Refusal, KeyboardInterrupt)): d.guard.verify_kong_boundary()
            self.assertTrue(d.guard.kong_boundary_attempted)
            self.assertFalse(d.guard._kong_boundary_completed or d.guard.owner_kong_boundary_verified)
            with self.assertRaises(dev.Refusal): d.guard.verify_kong_boundary()

class KongExecutionOwner(unittest.TestCase):
    def prepared(self):
        owner = KongBoundaryOwner()
        d, work = owner.prepared()
        self.addCleanup(owner.doCleanups)
        d.guard.verify_kong_boundary()
        d.guard.kong_execution = True
        install_kong_peer(d)
        return d, work

    def test_owned_kong_lifecycle_normal_cleanup_precedes_separate_fact(self):
        d, _ = self.prepared()
        deadline = d.guard.deadline
        with patch.object(dev, 'free_ports'):
            d.guard.execute_kong()
        self.assertEqual(d.guard.deadline, deadline)
        self.assertFalse(d.guard.owner_kong_execution_verified)
        self.assertTrue(d.guard.kong_healthy_verified)
        with patch.object(dev, 'free_ports'): d.guard.finish_execution()
        self.assertTrue(d.guard.cleaned and d.guard.owner_kong_execution_verified)
        mutations = [(method, path) for method, path, _ in d.events
                     if method in ('POST', 'PUT', 'DELETE') and ('supabase_kong_disposable_' in path or 'd'*64 in path)]
        self.assertEqual([method for method, _ in mutations], ['POST', 'PUT', 'POST', 'POST', 'DELETE'])
        self.assertTrue(mutations[-1][1].endswith('?force=false'))
        deletes = [path for method, path, _ in d.events if method == 'DELETE']
        self.assertLess(deletes.index('/v1.48/containers/'+'d'*64+'?force=false'),
                        deletes.index('/v1.48/containers/'+'a'*64+'?force=false'))

    def test_only_identified_empty_api_normalizations_are_accepted(self):
        d, _ = self.prepared()
        original = d.exchange
        def exchange(method, path, body=None, **kwargs):
            result = original(method, path, body, **kwargs)
            if method == 'GET' and '/containers/'+'d'*64 in path and result[0] == 200:
                row = result[1]
                row['HostConfig'].pop('Mounts')
                row['HostConfig']['Binds'] = None
                row['HostConfig']['LogConfig']['Config'] = None
                row['HostConfig']['Init'] = None
                row['Config']['Healthcheck'].update(StartPeriod=0, StartInterval=0)
                row['Config']['ArgsEscaped'] = False
            return result
        d.exchange = exchange
        with patch.object(dev, 'free_ports'):
            d.guard.execute_kong()
            d.guard.finish_execution()
        self.assertTrue(d.guard.owner_kong_execution_verified)

    def test_observed_null_omission_and_protection_order_complete_owned_lifecycle(self):
        for observation in ('onbuild', 'masked-order', 'readonly-order', 'combined'):
            with self.subTest(observation=observation):
                d, _ = self.prepared()
                original, states = d.exchange, set()
                def exchange(method, path, body=None, **kwargs):
                    result = original(method, path, body, **kwargs)
                    if method == 'GET' and path == '/v1.48/containers/'+'d'*64+'/json' and result[0] == 200:
                        row = result[1]
                        states.add(row['State']['Status'])
                        if observation in ('onbuild', 'combined'): row['Config'].pop('OnBuild', None)
                        if observation in ('masked-order', 'combined'):
                            row['HostConfig']['MaskedPaths'] = sorted(row['HostConfig']['MaskedPaths'])
                        if observation in ('readonly-order', 'combined'):
                            row['HostConfig']['ReadonlyPaths'].reverse()
                    return result
                d.exchange = exchange
                with patch.object(dev, 'free_ports'):
                    d.guard.execute_kong()
                    d.guard.finish_execution()
                self.assertEqual(states, {'created', 'running', 'exited'})
                self.assertTrue(d.guard.cleaned and d.guard.owner_kong_execution_verified)
                self.assertIsNone(d.kong_row)

    def test_projection_normalizations_keep_nonnull_and_invalid_protections_closed(self):
        mutations = {}
        for value in ([], ['RUN private-input-sentinel'], {}, '', False, 0):
            mutations['onbuild-'+repr(value)] = lambda row, value=value: row['Config'].update(OnBuild=value)
        mutations['other-null-absent'] = lambda row: row['Config'].pop('Volumes')
        for key in ('MaskedPaths', 'ReadonlyPaths'):
            mutations[key+'-missing'] = lambda row, key=key: row['HostConfig'][key].pop()
            mutations[key+'-extra'] = lambda row, key=key: row['HostConfig'][key].append('/unexpected')
            mutations[key+'-duplicate'] = lambda row, key=key: row['HostConfig'][key].append(row['HostConfig'][key][0])
            mutations[key+'-replacement'] = lambda row, key=key: row['HostConfig'][key].__setitem__(0, '/unexpected')
            for container in (tuple, set, dict.fromkeys):
                mutations[key+'-full-'+str(container)] = lambda row, key=key, container=container: row['HostConfig'].update({key: container(row['HostConfig'][key])})
            for value in (None, [], '', {}, (), [1], [[]]):
                mutations[key+'-type-'+repr(value)] = lambda row, key=key, value=value: row['HostConfig'].update({key: value})
        for fault, mutate in mutations.items():
            with self.subTest(fault=fault):
                d, _ = self.prepared()
                original = d.exchange
                def exchange(method, path, body=None, **kwargs):
                    result = original(method, path, body, **kwargs)
                    if method == 'GET' and path == '/v1.48/containers/'+'d'*64+'/json' and result[0] == 200:
                        mutate(result[1])
                    return result
                d.exchange = exchange
                with patch.object(dev, 'free_ports'), self.assertRaises(dev.Refusal): d.guard.execute_kong()
                self.assertTrue(d.guard.ownership_lost)
                before = len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
                self.assertEqual(before, len(d.events))
                with self.assertRaises(dev.Refusal): d.guard.execute_kong()
                self.assertEqual(before, len(d.events))
                self.assertFalse(d.guard.owner_kong_execution_verified)

    def test_normalized_projection_still_loses_custody_on_late_hostile_content(self):
        for stage in ('running', 'exited'):
            for fault in ('onbuild', 'masked', 'config', 'host'):
                with self.subTest(stage=stage, fault=fault):
                    d, _ = self.prepared()
                    original, injected = d.exchange, []
                    def exchange(method, path, body=None, **kwargs):
                        result = original(method, path, body, **kwargs)
                        if method == 'GET' and path == '/v1.48/containers/'+'d'*64+'/json' and result[0] == 200:
                            row = result[1]
                            row['Config'].pop('OnBuild', None)
                            row['HostConfig']['MaskedPaths'] = sorted(row['HostConfig']['MaskedPaths'])
                            if row['State']['Status'] == stage:
                                injected.append(stage)
                                if fault == 'onbuild': row['Config']['OnBuild'] = []
                                elif fault == 'masked': row['HostConfig']['MaskedPaths'][0] = '/unexpected'
                                elif fault == 'config': row['Config']['Unknown'] = None
                                else: row['HostConfig']['Memory'] = 0
                        return result
                    d.exchange = exchange
                    with patch.object(dev, 'free_ports'):
                        if stage == 'exited': d.guard.execute_kong()
                        with self.assertRaises(dev.Refusal):
                            d.guard.execute_kong() if stage == 'running' else d.guard.finish_execution()
                    self.assertTrue(injected and d.guard.ownership_lost)
                    before = len(d.events)
                    with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
                    self.assertEqual(before, len(d.events))
                    self.assertFalse(d.guard.owner_kong_execution_verified)
                    self.assertIsNotNone(d.kong_row)
                    later_mutations = [path for method, path, _ in d.events if method in ('POST', 'DELETE')]
                    self.assertNotIn('/v1.48/containers/'+'d'*64+'?force=false', later_mutations)
                    self.assertNotIn('/v1.48/containers/'+'a'*64+'/stop?t=5', later_mutations)

    def test_recorded_poststart_null_oom_projection_accepts_offline(self):
        fixture = json.loads((dev.ROOT / 'platform/deployment/fixtures/supabase-kong-observed-container-api-projection.json').read_text())
        self.assertEqual(fixture['schema_version'], 1)
        self.assertEqual(fixture['capture']['resource_phase'], 'running')
        self.assertIsNone(fixture['host_config']['OomKillDisable'])
        d, _ = self.prepared()
        with patch.object(dev, 'free_ports'): d.guard.execute_kong()
        row = d.copy(d.kong_row)
        create_profile.validate_kong_container(row, 'd'*64, d.guard.kong_fixture, started=True)
        for key in fixture['omitted_config_keys']: row['Config'].pop(key, None)
        row['HostConfig'].update(d.copy(fixture['host_config']))
        for form in ('null', 'false', 'absent'):
            with self.subTest(form=form):
                if form == 'absent': row['HostConfig'].pop('OomKillDisable')
                else: row['HostConfig']['OomKillDisable'] = None if form == 'null' else False
                before = d.copy(row)
                create_profile.validate_kong_container(row, 'd'*64, d.guard.kong_fixture, started=True)
                self.assertEqual(row, before)
        row['HostConfig']['OomKillDisable'] = None
        for fault in ('memory', 'config', 'protection'):
            with self.subTest(fault=fault):
                hostile = d.copy(row)
                if fault == 'memory': hostile['HostConfig']['Memory'] //= 2
                elif fault == 'config': hostile['Config']['Unexpected'] = True
                else: hostile['HostConfig']['MaskedPaths'].pop()
                with self.assertRaises(dev.Refusal) as caught:
                    create_profile.validate_kong_container(hostile, 'd'*64, d.guard.kong_fixture, started=True)
                self.assertEqual((caught.exception.stage, caught.exception.code), ('startup', 'unsafe_create'))

    def test_null_oom_default_completes_all_lifecycle_observation_phases(self):
        for form, phase in itertools.product(('null', 'false', 'absent'), ('all', 'created', 'running', 'exited')):
            with self.subTest(form=form, phase=phase):
                d, _ = self.prepared()
                original, seen = d.exchange, set()
                def exchange(method, path, body=None, **kwargs):
                    result = original(method, path, body, **kwargs)
                    if method == 'GET' and path == '/v1.48/containers/'+'d'*64+'/json' and result[0] == 200:
                        row = result[1]
                        if phase == 'all' or row['State']['Status'] == phase:
                            if form == 'absent': row['HostConfig'].pop('OomKillDisable', None)
                            else: row['HostConfig']['OomKillDisable'] = None if form == 'null' else False
                            seen.add(row['State']['Status'])
                    return result
                d.exchange = exchange
                with patch.object(dev, 'free_ports'):
                    d.guard.execute_kong()
                    d.guard.finish_execution()
                self.assertEqual(seen, {'created', 'running', 'exited'} if phase == 'all' else {phase})
                self.assertTrue(d.guard.cleaned and d.guard.owner_kong_execution_verified)

    def test_oom_true_and_wrong_types_lose_custody_without_replay(self):
        for phase in ('created', 'running', 'exited'):
            for value in (True, 0, 1, 0.0, 'false', [], {}):
                with self.subTest(phase=phase, value=value):
                    d, _ = self.prepared()
                    original, injected = d.exchange, []
                    def exchange(method, path, body=None, **kwargs):
                        result = original(method, path, body, **kwargs)
                        if method == 'GET' and path == '/v1.48/containers/'+'d'*64+'/json' and result[0] == 200:
                            row = result[1]
                            row['Config'].pop('OnBuild', None)
                            row['HostConfig']['MaskedPaths'] = sorted(row['HostConfig']['MaskedPaths'])
                            if row['State']['Status'] == phase:
                                row['HostConfig']['OomKillDisable'] = value
                                injected.append(phase)
                        return result
                    d.exchange = exchange
                    with patch.object(dev, 'free_ports'):
                        if phase == 'exited': d.guard.execute_kong()
                        with self.assertRaises(dev.Refusal):
                            d.guard.finish_execution() if phase == 'exited' else d.guard.execute_kong()
                    self.assertTrue(injected and d.guard.ownership_lost)
                    before = len(d.events)
                    with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
                    with self.assertRaises(dev.Refusal): d.guard.execute_kong()
                    self.assertEqual(before, len(d.events))
                    self.assertFalse(d.guard.owner_kong_execution_verified)

    def test_premature_and_replayed_execution_consume_before_observation(self):
        d, _ = self.prepared()
        d.guard._kong_boundary_completed = False
        before = len(d.events)
        for _ in range(2):
            with self.assertRaises(dev.Refusal): d.guard.execute_kong()
        self.assertEqual(before, len(d.events))
        self.assertTrue(d.guard.kong_create_attempted)
        self.assertFalse(d.guard.owner_kong_execution_verified)

    def test_existing_unknown_colliding_and_lost_create_preserve_all_resources(self):
        for fault in ('existing', 'malformed', 'pg-collision', 'auth-collision', 'warning', 'lost'):
            with self.subTest(fault=fault):
                d, _ = self.prepared()
                original = d.exchange
                def exchange(method, path, body=None, **kwargs):
                    if 'supabase_kong_disposable_' in path:
                        if method == 'GET' and fault == 'existing': return 200, {}
                        if method == 'POST':
                            result = original(method, path, body, **kwargs)
                            if fault == 'malformed': return 201, {'Id': 'private-input-sentinel', 'Warnings': []}
                            if fault == 'pg-collision': return 201, {'Id': 'a'*64, 'Warnings': []}
                            if fault == 'auth-collision': return 201, {'Id': 'c'*64, 'Warnings': []}
                            if fault == 'warning': return 201, {'Id': 'd'*64, 'Warnings': ['private-input-sentinel']}
                            if fault == 'lost':
                                d.closed = True
                                raise dev.Refusal('docker', 'docker_response_invalid')
                            return result
                    return original(method, path, body, **kwargs)
                d.exchange = exchange
                with patch.object(dev, 'free_ports'), self.assertRaises(dev.Refusal) as error:
                    d.guard.execute_kong()
                self.assertNotIn('private-input-sentinel', str(error.exception))
                self.assertTrue(d.guard.kong_creation_uncertain)
                before = len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.execute_kong()
                with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
                self.assertEqual(before, len(d.events))
                self.assertIsNotNone(d.row)
                self.assertIsNotNone(d.volume)
                self.assertIsNotNone(d.network)

    def test_effective_config_state_network_and_mount_faults_latch_custody_loss(self):
        changes = {
            'env': lambda row: row['Config']['Env'].append('private-input-sentinel'),
            'extra-config': lambda row: row['Config'].update(Shell=['private-input-sentinel']),
            'user': lambda row: row['Config'].update(User='root'),
            'labels': lambda row: row['Config']['Labels'].update({'com.supabase.cli.project': 'foreign'}),
            'compose-label': lambda row: row['Config']['Labels'].update({'com.docker.compose.project': 'foreign'}),
            'workdir-label': lambda row: row['Config']['Labels'].update({'com.supabase.cli.workdir': '/foreign'}),
            'maintainer-label': lambda row: row['Config']['Labels'].update(maintainer='foreign'),
            'workdir': lambda row: row['Config'].update(WorkingDir='/tmp'),
            'stop-signal': lambda row: row['Config'].update(StopSignal='SIGKILL'),
            'restart-policy': lambda row: row['HostConfig']['RestartPolicy'].update(Name='always'),
            'memory': lambda row: row['HostConfig'].update(Memory=0),
            'memory-swap': lambda row: row['HostConfig'].update(MemorySwap=0),
            'cpu': lambda row: row['HostConfig'].update(NanoCpus=0),
            'pids': lambda row: row['HostConfig'].update(PidsLimit=0),
            'host-port': lambda row: row['HostConfig']['PortBindings']['8000/tcp'][0].update(HostIp='0.0.0.0'),

            'command': lambda row: row['Args'].append('private-input-sentinel'),
            'ports': lambda row: row['Config']['ExposedPorts'].update({'9999/tcp': {}}),
            'health': lambda row: row['Config']['Healthcheck'].update(Retries=True),
            'mount': lambda row: row['Mounts'].append({'Type': 'bind'}),
            'host': lambda row: row['HostConfig'].update(CapAdd=['SYS_ADMIN']),
            'alias': lambda row: next(iter(row['NetworkSettings']['Networks'].values()))['Aliases'].append('foreign'),
            'network': lambda row: next(iter(row['NetworkSettings']['Networks'].values())).update(NetworkID='f'*64),
            'restart': lambda row: row.update(RestartCount=True),
            'state': lambda row: row['State'].update(Pid=True),
            'image': lambda row: row.update(Image='sha256:'+'f'*64),
            'name': lambda row: row.update(Name='/foreign'),
            'timestamp': lambda row: row['State'].update(StartedAt='private-input-sentinel'),
        }
        for fault, change in changes.items():
            with self.subTest(fault=fault):
                d, _ = self.prepared()
                original = d.exchange
                def exchange(method, path, body=None, **kwargs):
                    result = original(method, path, body, **kwargs)
                    if method == 'GET' and '/containers/'+'d'*64 in path and result[0] == 200:
                        change(result[1])
                    return result
                d.exchange = exchange
                with patch.object(dev, 'free_ports'), self.assertRaises(dev.Refusal) as error: d.guard.execute_kong()
                self.assertNotIn('private-input-sentinel', str(error.exception))
                self.assertTrue(d.guard.ownership_lost)
                before = len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
                self.assertEqual(before, len(d.events))
                self.assertFalse(d.guard.owner_kong_execution_verified)

    def test_copy_start_health_expiry_and_cancellation_never_replay(self):
        for fault in ('copy', 'start', 'health', 'instance', 'expiry', 'cancel'):
            with self.subTest(fault=fault):
                d, _ = self.prepared()
                original = d.exchange
                def exchange(method, path, body=None, **kwargs):
                    result = original(method, path, body, **kwargs)
                    if '/containers/'+'d'*64 in path:
                        if '/archive?' in path:
                            if fault == 'copy': return 500, None
                            if fault == 'expiry': d.deadline = d.guard.deadline = 0
                            if fault == 'cancel': raise KeyboardInterrupt()
                        if path.endswith('/start') and fault == 'start': return 500, None
                        if method == 'GET' and result[0] == 200 and result[1]['State']['Status'] == 'running':
                            if fault == 'health': result[1]['State']['Health']['Status'] = 'private-input-sentinel'
                            if fault == 'instance':
                                d.kong_row['State']['Health']['Status'] = 'starting'
                                result[1]['State']['Health']['Status'] = 'starting'
                                if d.guard.kong_started_at:
                                    result[1]['State']['StartedAt'] = '2026-10-19T12:00:00.000000002Z'
                    return result
                d.exchange = exchange
                deadline = d.guard.deadline
                with patch.object(dev, 'free_ports'), self.assertRaises((dev.Refusal, KeyboardInterrupt)): d.guard.execute_kong()
                if fault != 'expiry': self.assertEqual(d.guard.deadline, deadline)
                before = len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.execute_kong()
                with self.assertRaises(dev.Refusal): d.guard.finish_execution()
                self.assertEqual(before, len(d.events))
                self.assertFalse(d.guard.owner_kong_execution_verified)

    def test_unhealthy_is_terminal_before_later_same_instance_recovery(self):
        d, _ = self.prepared()
        original = d.exchange
        observed = []
        health_sequence = ('starting', 'unhealthy', 'healthy')
        def exchange(method, path, body=None, **kwargs):
            result = original(method, path, body, **kwargs)
            if (method == 'GET' and path == '/v1.48/containers/'+'d'*64+'/json'
                    and result[0] == 200 and result[1]['State']['Status'] == 'running'):
                health = health_sequence[min(len(observed), len(health_sequence)-1)]
                observed.append(health)
                result[1]['State']['Health']['Status'] = health
            return result
        d.exchange = exchange
        deadline = d.guard.deadline
        with patch.object(dev, 'free_ports'), self.assertRaises(dev.Refusal) as error:
            d.guard.execute_kong()
        self.assertEqual((error.exception.stage, error.exception.code), ('startup', 'execution_invalid_health'))
        self.assertEqual(observed, ['starting', 'unhealthy'])
        self.assertEqual(d.guard.deadline, deadline)
        self.assertFalse(d.guard.kong_healthy_verified or d.guard.owner_kong_execution_verified)
        before = len(d.events)
        with self.assertRaises(dev.Refusal): d.guard.execute_kong()
        with self.assertRaises(dev.Refusal): d.guard.finish_execution()
        self.assertEqual(len(d.events), before)
        # Known current ownership still permits bounded failure disposal.
        with patch.object(dev, 'free_ports'): d.guard.cleanup_execution()
        self.assertTrue(d.guard.cleaned)
        self.assertFalse(d.guard.owner_kong_execution_verified)

    def test_shutdown_shares_budget_and_cleanup_has_single_ten_second_budget(self):
        import time
        d, _ = self.prepared()
        with patch.object(dev, 'free_ports'): d.guard.execute_kong()
        original = d.exchange
        budgets = []
        def exchange(method, path, body=None, **kwargs):
            if method in ('POST', 'DELETE') and ('/stop?' in path or method == 'DELETE'):
                budgets.append((method, path, d.guard.deadline, time.monotonic()))
            return original(method, path, body, **kwargs)
        d.exchange = exchange
        with patch.object(dev, 'free_ports'): d.guard.finish_execution()
        stops = [row for row in budgets if '/stop?' in row[1]]
        deletes = [row for row in budgets if row[0] == 'DELETE']
        self.assertEqual(len(stops), 2)
        self.assertEqual(stops[0][2], stops[1][2])
        self.assertLessEqual(stops[0][2] - stops[0][3], 15)
        self.assertEqual(len(set(row[2] for row in deletes)), 1)
        self.assertLessEqual(deletes[0][2] - deletes[0][3], 10)

    def test_changed_stopped_pg_blocks_kong_disposal_and_final_fact(self):
        d, _ = self.prepared()
        with patch.object(dev, 'free_ports'): d.guard.execute_kong()
        original = d.exchange
        def exchange(method, path, body=None, **kwargs):
            result = original(method, path, body, **kwargs)
            if path == '/v1.48/containers/'+'a'*64+'/stop?t=5':
                d.row['State']['StartedAt'] = '2026-10-17T12:00:00.000000002Z'
            return result
        d.exchange = exchange
        with patch.object(dev, 'free_ports'), self.assertRaises(dev.Refusal): d.guard.finish_execution()
        with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
        self.assertIsNotNone(d.kong_row)
        self.assertFalse(any(method == 'DELETE' and 'd'*64 in path for method, path, _ in d.events))
        self.assertFalse(d.guard.owner_kong_execution_verified)

    def test_effective_protections_ports_and_endpoint_options_are_closed(self):
        def endpoint(row): return next(iter(row['NetworkSettings']['Networks'].values()))
        mutations = {
            'masked-absent': lambda r: r['HostConfig'].pop('MaskedPaths'),
            'masked-empty': lambda r: r['HostConfig'].update(MaskedPaths=[]),
            'masked-null': lambda r: r['HostConfig'].update(MaskedPaths=None),
            'readonly-absent': lambda r: r['HostConfig'].pop('ReadonlyPaths'),
            'readonly-empty': lambda r: r['HostConfig'].update(ReadonlyPaths=[]),
            'readonly-null': lambda r: r['HostConfig'].update(ReadonlyPaths=None),
            'readonly-changed': lambda r: r['HostConfig']['ReadonlyPaths'].pop(),
            'ports-missing': lambda r: r['NetworkSettings'].pop('Ports'),
            'ports-extra': lambda r: r['NetworkSettings']['Ports'].update({'9000/tcp': None}),
            'ports-nonloopback': lambda r: r['NetworkSettings']['Ports']['8000/tcp'][0].update(HostIp='0.0.0.0'),
            'ports-wrong': lambda r: r['NetworkSettings']['Ports']['8000/tcp'][0].update(HostPort='55482'),
            'endpoint-links': lambda r: endpoint(r).update(Links=['foreign']),
            'endpoint-ipam': lambda r: endpoint(r).update(IPAMConfig={'IPv4Address': '172.20.0.9'}),
            'endpoint-driver': lambda r: endpoint(r).update(DriverOpts={'option': 'foreign'}),
            'endpoint-priority': lambda r: endpoint(r).update(GwPriority=1),
            'endpoint-extra': lambda r: endpoint(r).update(UnknownOption=True),
        }
        for fault, mutate in mutations.items():
            with self.subTest(fault=fault):
                d, _ = self.prepared()
                original = d.exchange
                def exchange(method, path, body=None, **kwargs):
                    result = original(method, path, body, **kwargs)
                    if (method == 'GET' and path == '/v1.48/containers/'+'d'*64+'/json'
                            and result[0] == 200 and result[1]['State']['Status'] == 'running'):
                        mutate(result[1])
                    return result
                d.exchange = exchange
                with patch.object(dev, 'free_ports'), self.assertRaises(dev.Refusal): d.guard.execute_kong()
                self.assertTrue(d.guard.ownership_lost)
                before = len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
                self.assertEqual(before, len(d.events))
                self.assertFalse(d.guard.owner_kong_execution_verified)

    def test_safe_dynamic_endpoint_fields_and_inactive_port_normalizations(self):
        d, _ = self.prepared()
        original = d.exchange
        def exchange(method, path, body=None, **kwargs):
            result = original(method, path, body, **kwargs)
            if method == 'GET' and path == '/v1.48/containers/'+'d'*64+'/json' and result[0] == 200:
                row = result[1]
                endpoint = next(iter(row['NetworkSettings']['Networks'].values()))
                endpoint.update(Links=None, IPAMConfig=None, DriverOpts=None, GwPriority=0, Priority=0,
                    EndpointID='e'*64, MacAddress='02:42:ac:14:00:02', Gateway='172.20.0.1',
                    IPAddress='172.20.0.2', IPPrefixLen=16, IPv6Gateway='', GlobalIPv6Address='',
                    GlobalIPv6PrefixLen=0, DNSNames=['kong', 'api.supabase.internal', 'd'*12])
                if row['State']['Status'] == 'created': row['NetworkSettings'].pop('Ports')
                elif row['State']['Status'] == 'exited':
                    row['NetworkSettings']['Ports'] = {port: None for port in ('8000/tcp', '8001/tcp', '8088/tcp', '8443/tcp', '8444/tcp')}
            return result
        d.exchange = exchange
        with patch.object(dev, 'free_ports'):
            d.guard.execute_kong()
            d.guard.finish_execution()
        self.assertTrue(d.guard.owner_kong_execution_verified)

    def test_shutdown_deadline_expires_during_kong_stop_and_between_service_stops(self):
        for boundary in ('kong-stop', 'between-stops'):
            with self.subTest(boundary=boundary):
                d, _ = self.prepared()
                with patch.object(dev, 'free_ports'): d.guard.execute_kong()
                original_exchange, original_stop = d.exchange, d.guard.stop_instance
                clock, deadline = [100.0], []
                def exchange(method, path, body=None, **kwargs):
                    result = original_exchange(method, path, body, **kwargs)
                    if path == '/v1.48/containers/'+'d'*64+'/stop?t=5' and boundary == 'kong-stop':
                        deadline.append(d.guard.deadline)
                        clock[0] = d.guard.deadline
                    return result
                def stop(started):
                    if boundary == 'between-stops':
                        deadline.append(d.guard.deadline)
                        clock[0] = d.guard.deadline
                    return original_stop(started)
                d.exchange = exchange
                with patch.object(resources.time, 'monotonic', side_effect=lambda: clock[0]), \
                        patch.object(d.guard, 'stop_instance', side_effect=stop), self.assertRaises(dev.Refusal) as error:
                    d.guard.finish_execution()
                self.assertEqual(error.exception.code, 'docker_timeout')
                self.assertEqual(deadline, [115.0])
                self.assertEqual(d.guard.deadline, 115.0)
                self.assertFalse(any(method == 'POST' and path == '/v1.48/containers/'+'a'*64+'/stop?t=5'
                                     or method == 'DELETE' for method, path, _ in d.events
                                     if 'c'*64 not in path))
                self.assertFalse(d.guard.owner_kong_execution_verified or d.guard.cleaned)

    def test_health_deterioration_before_finish_refuses_without_normal_stop(self):
        d, _ = self.prepared()
        with patch.object(dev, 'free_ports'): d.guard.execute_kong()
        d.kong_row['State']['Health']['Status'] = 'unhealthy'
        before = len(d.events)
        with self.assertRaises(dev.Refusal) as error: d.guard.finish_execution()
        self.assertEqual(error.exception.code, 'execution_invalid_health')
        self.assertFalse(any(method == 'POST' and '/stop?' in path for method, path, _ in d.events[before:]))
        self.assertFalse(d.guard.owner_kong_execution_verified)

    def test_cleanup_fault_and_final_custody_never_publish_success(self):
        for fault in ('delete', 'absence', 'final-custody'):
            with self.subTest(fault=fault):
                d, work = self.prepared()
                with patch.object(dev, 'free_ports'): d.guard.execute_kong()
                original = d.exchange
                def exchange(method, path, body=None, **kwargs):
                    if 'd'*64 in path and method == 'DELETE' and fault == 'delete': return 500, None
                    result = original(method, path, body, **kwargs)
                    if path == '/v1.48/containers/'+'d'*64+'/json' and result[0] == 404 and fault == 'absence':
                        return 200, {}
                    if method == 'GET' and path == '/v1.48/networks/'+'b'*64 and result[0] == 404 and fault == 'final-custody':
                        (work / 'supabase/.branches/_current_branch').write_bytes(b'private-input-sentinel')
                    return result
                d.exchange = exchange
                with patch.object(dev, 'free_ports'), self.assertRaises(dev.Refusal): d.guard.finish_execution()
                self.assertFalse(d.guard.owner_kong_execution_verified)
                before = len(d.events)
                with self.assertRaises(dev.Refusal): d.guard.cleanup_execution()
                self.assertEqual(before, len(d.events))
                if fault != 'final-custody': self.assertIsNotNone(d.row)


def install_kong_peer(d):
    d.kong_row = None
    original = d.exchange
    def exchange(method, path, body=None, *, _kong_fixture=None):
        if 'supabase_kong_disposable_' not in path and '/containers/' + 'd'*64 not in path:
            return original(method, path, body)
        d.current()
        # Run the real classifier even in the in-memory independent peer.
        if _kong_fixture is not None:
            dev._docker_request(method, path, body, True, _kong_fixture=_kong_fixture)
        d.events.append((method, path, d.copy(body)))
        if '/create?' in path:
            d.kong_transfer_fixture = {**d.fixture, 'workdir': body['Labels']['com.supabase.cli.workdir'], 'network': d.guard.network if _kong_fixture else d.network}
            config = {key: d.copy(value) for key, value in body.items()
                      if key not in ('HostConfig', 'NetworkingConfig')}
            config.update(Hostname='d'*12, Domainname='', AttachStdin=False, AttachStdout=False,
                          AttachStderr=False, Tty=False, OpenStdin=False, StdinOnce=False,
                          Volumes=None, OnBuild=None)
            d.kong_row = {'Id': 'd'*64, 'Name': '/supabase_kong_disposable_' + d.fixture['project'],
                'Image': d.images[body['Image']]['Id'], 'Config': config, 'Path': 'sh',
                'Args': d.copy(body['Cmd']), 'HostConfig': {**d.copy(body['HostConfig']), 'IpcMode': 'private',
                    'MaskedPaths': ['/proc/asound', '/proc/acpi', '/proc/interrupts', '/proc/kcore',
                        '/proc/keys', '/proc/latency_stats', '/proc/timer_list', '/proc/timer_stats',
                        '/proc/sched_debug', '/proc/scsi', '/sys/firmware', '/sys/devices/virtual/powercap'],
                    'ReadonlyPaths': ['/proc/bus', '/proc/fs', '/proc/irq', '/proc/sys', '/proc/sysrq-trigger']},
                'Mounts': [], 'RestartCount': 0, 'Platform': 'linux',
                'NetworkSettings': {'Ports': {}, 'Networks': {d.network['Name']: {'NetworkID': '',
                    'Aliases': ['kong', 'api.supabase.internal']}}},
                'State': {'Status': 'created', 'Running': False, 'Paused': False, 'Restarting': False,
                    'Pid': 0, 'ExitCode': 0, 'Dead': False, 'OOMKilled': False, 'Error': '',
                    'StartedAt': '0001-01-01T00:00:00Z', 'FinishedAt': '0001-01-01T00:00:00Z'}}
            return 201, {'Id': 'd'*64, 'Warnings': []}
        if method == 'DELETE':
            d.kong_row = None
            d.network['Containers'].pop('d'*64, None)
            return 204, None
        if '/archive?' in path:
            import startup_lifecycle
            startup_lifecycle.validate_kong_archive(body, d.kong_transfer_fixture)
            return 200, None
        if path.endswith('/start'):
            d.kong_row['State'].update(Status='running', Running=True, Pid=456,
                StartedAt='2026-10-19T12:00:00.000000001Z', Health={'Status': 'healthy'})
            d.kong_row['NetworkSettings']['Networks'][d.network['Name']]['NetworkID'] = d.network['Id']
            d.kong_row['NetworkSettings']['Ports'] = {
                '8000/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '55481'}],
                '8001/tcp': None, '8088/tcp': None, '8443/tcp': None, '8444/tcp': None}
            d.network['Containers']['d'*64] = {}
            return 204, None
        if path.endswith('/stop?t=5'):
            d.kong_row['NetworkSettings']['Ports'] = {}
            d.kong_row['State'].update(Status='exited', Running=False, Pid=0,
                FinishedAt='2026-10-19T12:00:01.000000001Z')
            return 204, None
        return (200, d.copy(d.kong_row)) if d.kong_row else (404, None)
    d.exchange = exchange


class KongDaemon(AuthCatalogDaemon):
    def __init__(self):
        super().__init__()
        install_kong_peer(self)


class GotrueServiceBoundaryOwner(unittest.TestCase):
    def prepared(self):
        owner = KongExecutionOwner()
        daemon, work = owner.prepared()
        self.addCleanup(owner.doCleanups)
        with patch.object(dev, 'free_ports'):
            daemon.guard.execute_kong()
        return daemon, work

    def test_current_owner_boundary_refuses_create_without_dispatch(self):
        d, _ = self.prepared()
        before, deadline, modes = len(d.events), d.guard.deadline, list(d.catalog_modes)
        action = getattr(d.guard, 'verify_gotrue_service_boundary', lambda: None)
        action()
        self.assertTrue(getattr(d.guard, '_gotrue_boundary_completed', False),
                        'GoTrue needs a current owner pre-start refusal boundary')
        self.assertEqual(deadline, d.guard.deadline)
        self.assertEqual(modes, d.catalog_modes)
        self.assertTrue(all(method == 'GET' for method, _, _ in d.events[before:]))
        self.assertFalse(d.guard.cleaned or d.guard.owner_kong_execution_verified)

    def refused_once(self, d, context=None, exception=dev.Refusal):
        from contextlib import nullcontext
        with context or nullcontext():
            with self.assertRaises(exception) as caught:
                d.guard.verify_gotrue_service_boundary()
        self.assertTrue(d.guard.gotrue_boundary_attempted)
        self.assertFalse(d.guard._gotrue_boundary_completed)
        self.assertNotIn('private-input-sentinel', str(caught.exception))
        before = len(d.events)
        with self.assertRaises(dev.Refusal): d.guard.verify_gotrue_service_boundary()
        self.assertEqual(len(d.events), before)

    def test_attempt_consumed_before_every_prerequisite(self):
        cases = [(name, False) for name in ('execution', 'kong_execution', '_kong_boundary_completed',
            '_tail_completed', 'kong_healthy_verified', 'auth_cli_terminated', 'api_default_privileges_verified',
            'auth_job_exit_verified', 'auth_job_disposed', 'cli_db_backend_present_verified',
            'cli_db_backend_departure_verified', 'auth_catalog_precondition_verified', 'auth_catalog_verified',
            'api_default_privileges_request_refused')]
        cases += [(name, True) for name in ('_finish_attempted', 'cleaned', 'ownership_lost',
                    'kong_stop_attempted', 'kong_shutdown_verified', 'kong_disposed')]
        cases += [(name, None) for name in ('_fixture', '_tail_custody', 'kong_id', 'kong_started_at')]
        cases += [('phase', 4)]
        for name, value in cases:
            with self.subTest(gate=name):
                d, _ = self.prepared(); before = len(d.events)
                setattr(d.guard, name, value)
                self.refused_once(d)
                self.assertEqual(len(d.events), before)

    def test_selected_image_current_defaults_and_classifier_are_checked(self):
        d, _ = self.prepared(); before = len(d.events)
        with patch.object(create_profile, 'validate_auth_image_config', wraps=create_profile.validate_auth_image_config) as validator, patch.object(dev, '_docker_request', wraps=dev._docker_request) as classifier:
            d.guard.verify_gotrue_service_boundary()
        self.assertEqual(validator.call_count, 1)
        selected = next(ref for ref in d.images if '/gotrue@' in ref)
        self.assertTrue(any(path == '/v1.48/images/' + selected + '/json' for _, path, _ in d.events[before:]))
        creates = [call.args for call in classifier.call_args_list if call.args[0] == 'POST']
        self.assertEqual(len(creates), 1)
        self.assertEqual(creates[0][2]['HostConfig']['RestartPolicy']['Name'], 'unless-stopped')
        self.assertNotIn('PortBindings', creates[0][2]['HostConfig'])
        self.assertFalse(any(method != 'GET' for method, _, _ in d.events[before:]))
        before = len(d.events)
        with self.assertRaises(dev.Refusal): d.guard.verify_gotrue_service_boundary()
        self.assertEqual(before, len(d.events))

    def test_current_image_identity_platform_and_config_refuse(self):
        for fault in ('Id', 'Os', 'Architecture', 'Variant', 'missing', 'command', 'env', 'extra'):
            with self.subTest(fault=fault):
                d, _ = self.prepared(); original = d.exchange
                def exchange(method, path, body=None, **kwargs):
                    status, row = original(method, path, body, **kwargs)
                    if '/images/public.ecr.aws/supabase/gotrue@' in path:
                        if fault in ('Id', 'Os', 'Architecture', 'Variant'): row[fault] = 'private-input-sentinel'
                        elif fault == 'missing': row['Config'].pop('Volumes')
                        elif fault == 'command': row['Config']['Cmd'] = ['sh']
                        elif fault == 'env': row['Config']['Env'].append('private-input-sentinel')
                        else: row['Config']['Unexpected'] = True
                    return status, row
                d.exchange = exchange
                self.refused_once(d)

    def test_missing_ambiguous_and_changed_selection_refuse(self):
        for fault in ('missing', 'ambiguous', 'plan'):
            with self.subTest(fault=fault):
                d, _ = self.prepared()
                selected = next(ref for ref in d.images if '/gotrue@' in ref)
                d.guard.images = d.copy(d.guard.images)
                if fault == 'missing': del d.guard.images[selected]
                elif fault == 'ambiguous': d.guard.images['public.ecr.aws/supabase/gotrue@sha256:'+'e'*64] = d.copy(d.images[selected])
                else: d.guard.plan[selected] = 'sha256:'+'e'*64
                self.refused_once(d)

    def test_changed_intents_and_constructor_fixture_mutation_refuse(self):
        for name in ('gotrue_service_request', 'gotrue_service_environment', 'gotrue_service_execution_request', 'fixture'):
            with self.subTest(seam=name):
                d, _ = self.prepared()
                function = 'gotrue_service_request' if name == 'fixture' else name
                original = getattr(create_profile, function)
                def corrupt(fixture):
                    value = original(fixture)
                    if name == 'fixture': fixture['workdir'] = '/private-input-sentinel'
                    elif name == 'gotrue_service_request': value.append('private-input-sentinel')
                    elif name == 'gotrue_service_environment': value['GOTRUE_JWT_SECRET'] = 'private-input-sentinel'
                    else: value['body']['HostConfig']['Privileged'] = True
                    return value
                self.refused_once(d, patch.object(create_profile, function, side_effect=corrupt))

    def test_current_pg_and_kong_health_rechecked_after_profile_and_classifier(self):
        for seam in ('profile', 'classifier'):
            for service in ('pg', 'kong'):
                with self.subTest(seam=seam, service=service):
                    d, _ = self.prepared()
                    def change():
                        row = d.row if service == 'pg' else d.kong_row
                        row['State']['Health']['Status'] = 'unhealthy'
                    if seam == 'profile':
                        original = create_profile.gotrue_service_execution_request
                        def changed(*args):
                            result = original(*args); change(); return result
                        context = patch.object(create_profile, 'gotrue_service_execution_request', side_effect=changed)
                    else:
                        original = dev._docker_request
                        def changed(*args, **kwargs):
                            if args[0] == 'POST': change()
                            return original(*args, **kwargs)
                        context = patch.object(dev, '_docker_request', side_effect=changed)
                    self.refused_once(d, context)

    def test_expiry_cancellation_custody_and_unexpected_admission_never_complete(self):
        import time
        for fault in ('deadline', 'cancel', 'fixture', 'admission', 'classifier-error'):
            with self.subTest(fault=fault):
                d, work = self.prepared()
                if fault == 'deadline':
                    d.deadline = d.guard.deadline = time.monotonic() - 1
                    context = None
                elif fault == 'fixture':
                    (work / 'bin/docker').write_bytes(b'changed')
                    context = None
                elif fault == 'cancel': context = patch.object(create_profile, 'gotrue_service_request', side_effect=KeyboardInterrupt())
                elif fault == 'admission': context = patch.object(dev, '_docker_request', return_value={})
                else: context = patch.object(dev, '_docker_request', side_effect=dev.Refusal('docker', 'other'))
                self.refused_once(d, context, KeyboardInterrupt if fault == 'cancel' else dev.Refusal)

    def test_owner_target_origin_and_callback_changes_refuse(self):
        for key in ('target_id', 'origins', 'callback_urls'):
            with self.subTest(key=key):
                d, _ = self.prepared()
                if key == 'target_id': d.guard.target[key] = 'foreign'
                else:
                    d.guard.target[key] = list(d.guard.target[key])
                    d.guard.target[key][0] = 'https://foreign.invalid'
                self.refused_once(d)

    def test_boundary_adds_no_public_cleanup_fact(self):
        d, _ = self.prepared()
        d.guard.verify_gotrue_service_boundary()
        with patch.object(dev, 'free_ports'): d.guard.finish_execution()
        self.assertTrue(d.guard.cleaned and d.guard.owner_kong_execution_verified)
        self.assertFalse(hasattr(d.guard, 'owner_gotrue_boundary_verified'))

    def test_late_expiry_and_cancellation_cannot_complete(self):
        import time
        for seam in ('profile', 'classifier'):
            for fault in ('deadline', 'cancel'):
                with self.subTest(seam=seam, fault=fault):
                    d, _ = self.prepared()
                    def change():
                        if fault == 'cancel': raise KeyboardInterrupt()
                        d.deadline = d.guard.deadline = time.monotonic() - 1
                    if seam == 'profile':
                        original = create_profile.gotrue_service_execution_request
                        def changed(*args):
                            result = original(*args); change(); return result
                        context = patch.object(create_profile, 'gotrue_service_execution_request', side_effect=changed)
                    else:
                        original = dev._docker_request
                        def changed(*args, **kwargs):
                            if args[0] == 'POST': change()
                            return original(*args, **kwargs)
                        context = patch.object(dev, '_docker_request', side_effect=changed)
                    self.refused_once(d, context, KeyboardInterrupt if fault == 'cancel' else dev.Refusal)

    def test_healthy_replacement_instances_refuse_after_profile_and_classifier(self):
        for seam in ('profile', 'classifier'):
            for service in ('pg', 'kong'):
                with self.subTest(seam=seam, service=service):
                    d, _ = self.prepared()
                    def change():
                        row = d.row if service == 'pg' else d.kong_row
                        row['State']['StartedAt'] = '2026-10-20T12:00:00.000000001Z'
                    if seam == 'profile':
                        original = create_profile.gotrue_service_execution_request
                        def changed(*args):
                            result = original(*args); change(); return result
                        context = patch.object(create_profile, 'gotrue_service_execution_request', side_effect=changed)
                    else:
                        original = dev._docker_request
                        def changed(*args, **kwargs):
                            if args[0] == 'POST': change()
                            return original(*args, **kwargs)
                        context = patch.object(dev, '_docker_request', side_effect=changed)
                    self.refused_once(d, context)

    def test_bad_current_image_observations_refuse_safely(self):
        for fault in ('status', 'missing', 'list', 'config'):
            with self.subTest(fault=fault):
                d, _ = self.prepared(); original = d.exchange
                # Earlier joint custody sees real image metadata; fault only the
                # boundary's dedicated Config observation, not the independent peer.
                def exchange(method, path, body=None, **kwargs):
                    result = original(method, path, body, **kwargs)
                    import inspect
                    dedicated = any(frame.function == 'verify_gotrue_service_boundary'
                                    and frame.filename == resources.__file__
                                    for frame in inspect.stack()[:2])
                    if dedicated and '/images/public.ecr.aws/supabase/gotrue@' in path:
                        if fault == 'status': return 503, None
                        if fault == 'missing': return 200, None
                        if fault == 'list': return 200, []
                        result[1].pop('Config')
                    return result
                d.exchange = exchange
                self.refused_once(d)
