#!/usr/bin/env python3
"""Combined ENV proof on one private synthetic Unix peer; never real Docker."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dev
import startup
import qualify_daemon_images as images_proof
import qualify_networks as network_proof
import qualify_volumes as volume_proof

FRESH_CONTROLS = ['fresh', 'fresh-existing', 'fresh-foreign', 'fresh-error', 'fresh-late']
CONTROLS = FRESH_CONTROLS + ['positive', 'existing', 'image-missing', 'image-foreign', 'network-foreign',
            'network-replaced', 'volume-foreign', 'volume-changed', 'lost-network-response',
            'lost-volume-response', 'old-daemon', 'malformed', 'slow', 'use-late'] + [name for name in volume_proof.CONTROLS if name.startswith('use-')]
EXPECTED = {'image-missing': 'image_missing', 'image-foreign': 'image_identity_mismatch',
            'network-foreign': 'network_not_run_owned', 'network-replaced': 'network_replaced',
            'volume-foreign': 'volume_not_run_owned', 'volume-changed': 'volume_changed',
            'lost-network-response': 'docker_response_invalid',
            'lost-volume-response': 'docker_response_invalid', 'old-daemon': 'docker_28_required',
            'malformed': 'docker_response_invalid', 'slow': 'docker_timeout'}

EXPECTED.update({name: code for name, code in volume_proof.EXPECTED.items() if name.startswith('use-')})
EXPECTED['use-late'] = 'volume_in_use'
EXPECTED.update({name: 'volume_reuse_unsupported' for name in ['fresh-existing', 'fresh-foreign', 'fresh-late']})
EXPECTED['fresh-error'] = 'volume_inspection_failed'


class SyntheticDaemon(images_proof.SyntheticDaemon):
    def __init__(self, target, run_id, observations, control='positive', *, _network_conflict=False):
        super().__init__(observations, control)
        self.network = network_proof.SyntheticDaemon(target, run_id,
            {'existing': 'existing', 'network-foreign': 'foreign',
             'network-replaced': 'replacement'}.get(control, 'conflict' if _network_conflict else 'positive'))
        self.volume = volume_proof.SyntheticDaemon(target, run_id,
            {'existing': 'existing', 'volume-foreign': 'foreign',
             'volume-changed': 'changed'}.get(control, control if control.startswith('use-') and control != 'use-late' else 'positive'))
        if control in FRESH_CONTROLS:
            self.volume.present = control in ['fresh-existing', 'fresh-foreign']
        self.absent_count = 0
        self.use_count = 0
        self.image_control = {'image-missing': 'missing', 'image-foreign': 'wrong-id'}.get(control, control)
        self.expected = self.expected_events()
        if control in ['use-truncated', 'use-eof']:
            at = next(i for i, event in enumerate(self.expected, 1) if event[1] == volume_proof.expected_use_path(self.volume.name))
            setattr(self, 'truncated_at' if control == 'use-truncated' else 'disconnect_at', at)
        # Transport fault injection uses the existing private transport oracle.
        if control in ['lost-network-response', 'lost-volume-response']:
            route = '/v1.48/' + ('networks' if control == 'lost-network-response' else 'volumes') + '/create'
            self.disconnect_at = next(i for i, event in enumerate(self.expected, 1) if event[1] == route)

    def dispatch(self, method, path, body):
        self.events.append((method, path, body))
        if self.hook:
            self.hook(method, path)
        if path.startswith('/v1.48/networks/'):
            return self.network.dispatch(method, path, body)
        if path == volume_proof.expected_use_path(self.volume.name):
            self.use_count += 1
            if self.control == 'use-late' and self.use_count == 2:
                return 200, [{'Id': 'sensitive-container-marker'}]
            return self.volume.dispatch(method, path, body)
        if path.startswith('/v1.48/volumes/') and self.control in FRESH_CONTROLS:
            self.absent_count += 1
            if self.control == 'fresh-error':
                return 500, {'message': 'sensitive-marker'}
            if self.control == 'fresh-late' and self.absent_count == 2:
                self.volume.present = True
            if self.control == 'fresh-foreign':
                self.volume.volume['Labels'] = {}
        if path.startswith('/v1.48/volumes/'):
            return self.volume.dispatch(method, path, body)
        # Reuse image oracle without duplicating its outer event/hook.
        original_events, original_hook, original_control = self.events, self.hook, self.control
        try:
            self.events, self.hook, self.control = original_events[:-1], None, self.image_control
            return super().dispatch(method, path, body)
        finally:
            self.events, self.hook, self.control = original_events, original_hook, original_control

    def expected_events(self):
        child = [('GET', '/v1.48/images/' + key + '/json', None) for key in self.observations]
        config = [('GET', '/v1.48/images/' + value['Id'] + '/json', None) for value in self.observations.values()]
        net_name = ('GET', '/v1.48/networks/' + self.network.name, None)
        net_id = ('GET', '/v1.48/networks/' + self.network.network_id, None)
        net_create = ('POST', '/v1.48/networks/create', network_proof.expected_request(self.network.target, self.network.run_id))
        vol_name = ('GET', '/v1.48/volumes/' + self.volume.name, None)
        vol_create = ('POST', '/v1.48/volumes/create', volume_proof.expected_request(self.volume.target, self.volume.run_id))
        recovery = net_name if self.network.control == 'conflict' else net_id
        net = [net_name] + ([] if self.network.present else [net_create, recovery]) + [net_id, net_name, net_id]
        if self.control in FRESH_CONTROLS:
            return [('GET', '/version', None)] + child + config + [vol_name] + net + child + config + [net_id, net_name, net_id, vol_name]
        vol = [vol_name] + ([] if self.volume.present else [vol_create]) + [vol_name, ('GET', volume_proof.expected_use_path(self.volume.name), None)]
        return [('GET', '/version', None)] + child + config + net + vol + child + config + [net_id, net_name, net_id, vol_name, ('GET', volume_proof.expected_use_path(self.volume.name), None)]

    def validate_events(self, *, success=True):
        failures = {'old-daemon': 1, 'image-missing': 2, 'image-foreign': 2,
                    'network-foreign': 10, 'network-replaced': 11, 'volume-foreign': 16,
                    'volume-changed': 17, 'lost-network-response': 11,
                    'lost-volume-response': 17, 'malformed': 2, 'slow': 2}
        if self.control.startswith('use-'):
            failures[self.control] = (len(self.expected) if self.control == 'use-late' else
                                      next(i for i, event in enumerate(self.expected, 1)
                                           if event[1] == volume_proof.expected_use_path(self.volume.name)))
        failures.update({'fresh-existing': 10, 'fresh-foreign': 10, 'fresh-error': 10, 'fresh-late': len(self.expected)})
        count = len(self.expected) if success else failures.get(self.control)
        if (self.connections != 1 or self.errors or self.network.errors or self.volume.errors
                or self.events != self.expected[:len(self.events)]
                or count is not None and len(self.events) != count):
            dev.refuse('resources', 'synthetic_event_mismatch')


def qualify(args):
    import resources
    startup.existing_images(args)
    target = dev.decode(dev.read(Path(args.target).absolute()))
    expected = images_proof.expected_images(args.run_id)
    daemon = SyntheticDaemon(target, args.run_id, expected, args.control)
    with daemon.serve() as endpoint, tempfile.TemporaryDirectory(prefix='env-resource-work-') as temporary:
        work = Path(temporary)
        startup.initialize_workdir(work, target, args.run_id)
        called = []
        def construct(current_target, result):
            called.append(copy.deepcopy(result))
            argv, env = startup.invocation('/synthetic/not-executed/supabase', work,
                                           current_target, args.run_id, result['network'])
            if argv[-2:] != ['--network-id', daemon.network.network_id] or env['DOCKER_HOST'] != 'unix:///var/run/docker.sock':
                dev.refuse('resources', 'synthetic_handoff_mismatch')
            return result
        try:
            if args.control in FRESH_CONTROLS:
                constructor = startup.invocation
                expected_request = network_proof.expected_request(target, args.run_id)
                expected_network = {key: expected_request[key] for key in ['Name', 'Driver', 'Scope', 'Internal', 'Options', 'Labels']} | {
                    'Id': daemon.network.network_id, 'Containers': {}}
                def fresh_construct(executable, current_work, current_target, current_run, network):
                    actual = copy.deepcopy({'target': current_target, 'run_id': current_run, 'network': network})
                    called.append(actual)
                    if (executable != '/synthetic/not-executed/supabase' or current_work != work
                            or actual != {'target': target, 'run_id': args.run_id, 'network': expected_network}):
                        dev.refuse('resources', 'synthetic_handoff_mismatch')
                    return constructor(executable, current_work, current_target, current_run, network)
                with patch.object(startup, 'invocation', side_effect=fresh_construct):
                    argv, env = resources.invocation(args.target, args.run_id, '/synthetic/not-executed/supabase', work, _socket_path=endpoint)
                if argv[-2:] != ['--network-id', daemon.network.network_id] or env['DOCKER_HOST'] != 'unix:///var/run/docker.sock':
                    dev.refuse('resources', 'synthetic_handoff_mismatch')
                if daemon.volume.present:
                    dev.refuse('resources', 'synthetic_handoff_mismatch')
                if len(called) != 1:
                    dev.refuse('resources', 'synthetic_handoff_mismatch')
                result = {'network': called[0]['network'],
                          'images': expected, 'runtime_ready': False}
            else:
                result = resources.acquire(args.target, args.run_id, _socket_path=endpoint, _handoff=construct)
        except dev.Refusal as error:
            if EXPECTED.get(args.control) != error.code or called:
                dev.refuse('resources', 'synthetic_outcome_mismatch')
            daemon.validate_events(success=False)
            raise
    daemon.validate_events()
    if args.control not in ['positive', 'existing', 'fresh'] or len(called) != 1 or result['images'] != expected or result['runtime_ready'] is not False:
        dev.refuse('resources', 'synthetic_handoff_mismatch')
    return {'ok': True, 'stage': 'resources', 'code': 'resources_synthetic_qualified',
            'runtime_ready': False, 'control': args.control,
            'network_id': result['network']['Id'], 'volume_name': daemon.volume.name,
            'api_events': [{'method': method, 'path': path} for method, path, _ in daemon.events]}


def main(argv=None):
    try:
        parser = dev.Parser(add_help=False, allow_abbrev=False)
        parser.add_argument('--target', required=True)
        parser.add_argument('--run-id', required=True)
        parser.add_argument('--control', choices=CONTROLS, default='positive')
        print(json.dumps(qualify(parser.parse_args(argv)), sort_keys=True))
        return 0
    except dev.Refusal as error:
        result = {'ok': False, 'runtime_ready': False, 'stage': error.stage, 'code': error.code}
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        result = {'ok': False, 'runtime_ready': False, 'stage': 'resources', 'code': 'resource_proof_refused'}
    print(json.dumps(result, sort_keys=True))
    return 2


if __name__ == '__main__':
    sys.exit(main())
