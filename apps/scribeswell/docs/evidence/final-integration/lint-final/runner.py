import hashlib,json,os,subprocess,sys,time
from pathlib import Path
root=Path('/home/ck/repos/innodat/agriplatform'); evidence=root/'apps/scribeswell/docs/evidence/final-integration/lint-final';evidence.mkdir(parents=True,exist_ok=True)
py='/tmp/scribeswell-implementation-python/bin/python';node=str(root/'platform/deployment/.local/kdg-toolchains/2cb59147-0378-4fff-bf09-ba3f9e353aa0/payload/node/bin/node')
commands=[('lint',['npm','run','lint','--workspace=apps/scribeswell/web'])]
def snapshot():
 paths=[p for d in ['backend','tests','migrations','studies-migrations','contracts','tools','deployment','web/src','web/tests'] for p in (root/'apps/scribeswell'/d).rglob('*') if p.is_file() and p.suffix in ('.py','.sql','.json','.mjs','.ts','.tsx','.css','.cjs') and '__pycache__' not in p.parts]
 return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
before=snapshot();(evidence/'before.json').write_text(json.dumps(before,indent=2)+'\n');results=[]
for name,argv in commands:
 start=time.monotonic()
 with (evidence/(name+'.log')).open('w') as out:r=subprocess.run(argv,cwd=root,stdout=out,stderr=subprocess.STDOUT,timeout=300)
 results.append(dict(name=name,argv=argv,exit_code=r.returncode,seconds=round(time.monotonic()-start,2)));print(name,r.returncode,flush=True)
after=snapshot();(evidence/'after.json').write_text(json.dumps(after,indent=2)+'\n');(evidence/'results.json').write_text(json.dumps(dict(results=results,source_unchanged=before==after),indent=2)+'\n')
assert before==after
sys.exit(0 if all(r['exit_code']==0 for r in results) else 1)
