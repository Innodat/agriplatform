#!/usr/bin/env python3
"""Guarded synthetic startup proofs and explicit real postgres-bootstrap control."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dev
import startup
import volumes
import qualify_volumes
import qualify_daemon_images
import daemon_images
import qualify_resources

BOOTSTRAP_CONTROLS = ['postgres-bootstrap']
EXECUTION_CONTROLS = ['pinned-cli-postgres']

GUARDED_CONTROLS = ['guarded-fresh'] + ['guarded-' + name for name in qualify_resources.GUARDED_FAILURES]


def guarded_qualify(args, target):
    """One private peer connects the pinned CLI to the real retained ENV owner."""
    startup.existing_images(args)
    observations = qualify_daemon_images.expected_images(args.run_id)
    scenario = 'positive' if args.control == 'guarded-fresh' else args.control.removeprefix('guarded-')
    daemon = qualify_resources.GuardedDaemon(target, args.run_id, observations, scenario)
    args._image_observations = observations
    args._profile_control = 'fresh-lifecycle-positive'
    with daemon.serve() as endpoint:
        args._guarded_target = (args.target, endpoint)
        try:
            result = startup.qualify(args)
        except dev.Refusal as error:
            if qualify_resources.GUARDED_FAILURES.get(scenario, (None,))[0] != error.code:
                raise
            daemon.validate_events(success=False)
            raise
    daemon.validate_events()
    if scenario != 'positive' or result.get('guarded_volume_owner_proven') is not True:
        startup.fail('boundary_not_proven')
    result['api_events'] = [{'method': method, 'path': path} for method, path, _ in daemon.events]
    return result


def main(argv=None):
    try:
        parser = dev.Parser(add_help=False, allow_abbrev=False)
        parser.add_argument('--target', required=True)
        parser.add_argument('--run-id', required=True)
        parser.add_argument('--control', choices=['positive', 'invalid-network', 'contaminated-workdir', 'reject-command', 'invalid-selection-plan',
                                                       'invalid-create-script', 'invalid-create-environment', 'invalid-create-routing', 'invalid-create-request',
                                                       'lifecycle-positive', 'invalid-lifecycle-target', 'invalid-lifecycle-archive', 'invalid-lifecycle-order',
                                                       'fresh-lifecycle-positive', 'fresh-existing', 'fresh-racing', 'fresh-invalid-lifecycle-target',
                                                       'fresh-invalid-lifecycle-archive', 'fresh-invalid-lifecycle-order'] + GUARDED_CONTROLS + BOOTSTRAP_CONTROLS + EXECUTION_CONTROLS,
                            default='positive')
        args = parser.parse_args(argv)
        if args.control in BOOTSTRAP_CONTROLS:
            import startup_lifecycle
            print(json.dumps(startup_lifecycle.qualify_bootstrap(args), sort_keys=True))
            return 0
        if args.control in EXECUTION_CONTROLS:
            print(json.dumps(startup.qualify(args), sort_keys=True))
            return 0
        networks = volumes.networks
        networks.validate_run_id(args.run_id)
        target = dev.decode(dev.read(Path(args.target).absolute()))
        if args.control in GUARDED_CONTROLS:
            print(json.dumps(guarded_qualify(args, target), sort_keys=True))
            return 0
        if not args.control.startswith('fresh-'):
            daemon = qualify_volumes.SyntheticDaemon(target, args.run_id)
            with daemon.serve() as endpoint:
                acquired = volumes.acquire(args.target, args.run_id, _socket_path=endpoint)
            daemon.validate_events()
            args._volume = acquired['volume']
        startup.existing_images(args)
        image_daemon = qualify_daemon_images.SyntheticDaemon(qualify_daemon_images.expected_images(args.run_id))
        with image_daemon.serve() as endpoint:
            args._image_observations = daemon_images.acquire(args.target, args.run_id, _socket_path=endpoint)
        image_daemon.validate_events()
        result = startup.qualify(args)
        print(json.dumps(result, sort_keys=True))
        return 0
    except dev.Refusal as error:
        print(json.dumps({'ok': False, 'runtime_ready': False, 'stage': error.stage, 'code': error.code}))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        print(json.dumps({'ok': False, 'runtime_ready': False, 'stage': 'startup', 'code': 'startup_proof_refused'}))
    except KeyboardInterrupt:
        print(json.dumps({'ok': False, 'runtime_ready': False, 'stage': 'startup', 'code': 'interrupted'}))
    return 2


if __name__ == '__main__':
    sys.exit(main())
