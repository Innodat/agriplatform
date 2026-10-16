#!/usr/bin/env python3
"""Combined ENV proof on one private synthetic Unix peer; never real Docker."""
import copy
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dev
import startup
import qualify_daemon_images as images_proof
import qualify_networks as network_proof
import qualify_volumes as volume_proof

CONTROLS = ['positive', 'existing', 'image-missing', 'image-foreign', 'network-foreign',
            'network-replaced', 'volume-foreign', 'volume-changed', 'lost-network-response',
            'lost-volume-response', 'old-daemon', 'malformed', 'slow']
EXPECTED = {'image-missing': 'image_missing', 'image-foreign': 'image_identity_mismatch',
            'network-foreign': 'network_not_run_owned', 'network-replaced': 'network_replaced',
            'volume-foreign': 'volume_not_run_owned', 'volume-changed': 'volume_changed',
            'lost-network-response': 'docker_response_invalid',
            'lost-volume-response': 'docker_response_invalid', 'old-daemon': 'docker_28_required',
            'malformed': 'docker_response_invalid', 'slow': 'docker_timeout'}


class SyntheticDaemon(images_proof.SyntheticDaemon):
    def __init__(self, target, run_id, observations, control='positive', *, _network_conflict=False):
        super().__init__(observations, control)
        self.network = network_proof.SyntheticDaemon(target, run_id,
            {'existing': 'existing', 'network-foreign': 'foreign',
             'network-replaced': 'replacement'}.get(control, 'conflict' if _network_conflict else 'positive'))
        self.volume = volume_proof.SyntheticDaemon(target, run_id,
            {'existing': 'existing', 'volume-foreign': 'foreign',
             'volume-changed': 'changed'}.get(control, 'positive'))
        self.image_control = {'image-missing': 'missing', 'image-foreign': 'wrong-id'}.get(control, control)
        self.expected = self.expected_events()
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
        vol = [vol_name] + ([] if self.volume.present else [vol_create]) + [vol_name]
        return [('GET', '/version', None)] + child + config + net + vol + child + config + [net_id, net_name, net_id, vol_name]

    def validate_events(self, *, success=True):
        failures = {'old-daemon': 1, 'image-missing': 2, 'image-foreign': 2,
                    'network-foreign': 10, 'network-replaced': 11, 'volume-foreign': 16,
                    'volume-changed': 17, 'lost-network-response': 11,
                    'lost-volume-response': 17, 'malformed': 2, 'slow': 2}
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
            result = resources.acquire(args.target, args.run_id, _socket_path=endpoint, _handoff=construct)
        except dev.Refusal as error:
            if EXPECTED.get(args.control) != error.code or called:
                dev.refuse('resources', 'synthetic_outcome_mismatch')
            daemon.validate_events(success=False)
            raise
    daemon.validate_events()
    if args.control not in ['positive', 'existing'] or len(called) != 1 or result['images'] != expected or result['runtime_ready'] is not False:
        dev.refuse('resources', 'synthetic_handoff_mismatch')
    return {'ok': True, 'stage': 'resources', 'code': 'resources_synthetic_qualified',
            'runtime_ready': False, 'control': args.control,
            'network_id': result['network']['Id'], 'volume_name': result['volume']['Name'],
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
