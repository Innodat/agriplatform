import hashlib,json,os,subprocess,sys,time
from pathlib import Path
root=Path('/home/ck/repos/innodat/agriplatform');e=root/'apps/scribeswell/docs/evidence/final-integration/browser-verification';e.mkdir(parents=True,exist_ok=True)
paths=[p for directory in ['web/src','web/tests','backend','contracts'] for p in (root/'apps/scribeswell'/directory).rglob('*') if p.is_file() and p.suffix in ('.py','.ts','.tsx','.css','.json','.cjs') and '__pycache__' not in p.parts]
paths += [root/'apps/scribeswell/web/package.json',root/'apps/scribeswell/web/playwright.config.cjs']
def snap():return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}
before=snap();(e/'browser-before.json').write_text(json.dumps(before,indent=2)+'\n')
env=os.environ.copy()
for k in list(env):
 if k.startswith('PG') or 'NATIVE' in k or k in ('DATABASE_URL','PYTEST_ADDOPTS') or k.endswith('_DATABASE_URL') or k.endswith('_TEST_ADMIN_URL'):env.pop(k,None)
env['SCRIBESWELL_TEST_PYTHON']='/tmp/scribeswell-implementation-python/bin/python'
argv=['npm','run','test:browser','--workspace=apps/scribeswell/web','--','--workers=2','--fully-parallel']
start=time.monotonic()
with (e/'browser-full.log').open('w') as out:r=subprocess.run(argv,cwd=root,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=2400)
after=snap();(e/'browser-after.json').write_text(json.dumps(after,indent=2)+'\n');(e/'browser-results.json').write_text(json.dumps(dict(argv=argv,exit_code=r.returncode,seconds=round(time.monotonic()-start,2),selected_files=len(before),source_unchanged=before==after),indent=2)+'\n')
assert before==after
sys.exit(r.returncode)
