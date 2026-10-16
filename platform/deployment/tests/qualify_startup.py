#!/usr/bin/env python3
"""Opt-in guarded pinned Supabase first-create proof. No real Docker dispatch."""
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


def main(argv=None):
    try:
        parser = dev.Parser(add_help=False)
        parser.add_argument('--target', required=True)
        parser.add_argument('--run-id', required=True)
        parser.add_argument('--control', choices=['positive', 'invalid-network', 'contaminated-workdir', 'reject-command', 'invalid-selection-plan',
                                                       'invalid-create-script', 'invalid-create-environment', 'invalid-create-routing', 'invalid-create-request',
                                                       'lifecycle-positive', 'invalid-lifecycle-target', 'invalid-lifecycle-archive', 'invalid-lifecycle-order'],
                            default='positive')
        args = parser.parse_args(argv)
        networks = volumes.networks
        networks.validate_run_id(args.run_id)
        target = dev.decode(dev.read(Path(args.target).absolute()))
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
