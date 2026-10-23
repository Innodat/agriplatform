#!/usr/bin/env python3
"""Reproduce the unmounted personal-notes contract; --check never writes."""
import argparse
import json
import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(APP.parents[1]))
from apps.scribeswell.backend.personal_notes_contract import openapi_contract


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = APP / 'contracts/personal-notes-v1.openapi.json'
    expected = (json.dumps(openapi_contract(), ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')
    if args.check:
        if not target.is_file() or target.read_bytes() != expected:
            parser.exit(1, 'Personal-notes contract is stale; run the exporter without --check.\n')
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(expected)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
