#!/usr/bin/env python3
"""Explicit qualification against a new isolated synthetic PostgreSQL17+ fixture.

This command never discovers credentials or provisions a retained environment.
The caller supplies SCRIBESWELL_NOTES_TEST_ADMIN_URL for a fresh loopback cluster.
Test fixtures allocate/drop only their own random database and previously absent roles.
No production activation, Identity/Access-owner or physical-device claim is made.
"""
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[4]
if not os.environ.get('SCRIBESWELL_NOTES_TEST_ADMIN_URL'):
    raise SystemExit('An explicitly isolated PostgreSQL17+ fixture is required')
raise SystemExit(subprocess.call([sys.executable,'-m','pytest',str(ROOT/'apps/scribeswell/tests/test_personal_notes_storage.py'),'-q'],cwd=ROOT))
