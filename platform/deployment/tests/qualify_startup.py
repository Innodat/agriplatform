#!/usr/bin/env python3
"""Opt-in guarded pinned Supabase first-create proof. No real Docker dispatch."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dev
import startup


def main(argv=None):
    try:
        parser = dev.Parser(add_help=False)
        parser.add_argument('--target', required=True)
        parser.add_argument('--run-id', required=True)
        parser.add_argument('--control', choices=['positive', 'invalid-network', 'contaminated-workdir', 'reject-command'],
                            default='positive')
        result = startup.qualify(parser.parse_args(argv))
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
