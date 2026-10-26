"""Run from repository root; no native collection. Optional explicit pytest node IDs."""
import json
import os
from pathlib import Path
import subprocess
import sys

folder = Path(__file__).resolve().parent
nodes = sys.argv[1:] or ['apps/scribeswell/tests/test_corpus_operator_publish.py']
argv = ['/tmp/scribeswell-implementation-python/bin/python', '-m', 'pytest', '-q', *nodes]
env = {key:value for key,value in os.environ.items()
       if not (key.startswith('PG') or key.startswith('SUPABASE')
               or 'DATABASE' in key or 'NATIVE' in key)}
# Record the filtering rule, never ambient values or credential-bearing payloads.
print(json.dumps({'argv':argv, 'environment_filter':
    'remove keys starting PG or SUPABASE, or containing DATABASE or NATIVE'}, indent=2), flush=True)
result = subprocess.run(argv, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
print(result.stdout, end='')
raise SystemExit(result.returncode)
