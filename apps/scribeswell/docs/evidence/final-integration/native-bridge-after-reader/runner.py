"""Final-phase runner; defining this file does not start a fixture."""
import hashlib,json,os,secrets,signal,subprocess,sys,time
from pathlib import Path
ROOT=Path('/home/ck/repos/innodat/agriplatform')
PYTHON='/tmp/scribeswell-implementation-python/bin/python'
def main():
 evidence=ROOT/'apps/scribeswell/docs/evidence/final-integration/native-bridge-after-reader';evidence.mkdir(parents=True,exist_ok=True)
 name='scribeswell-final-'+secrets.token_hex(6)
 owned=False;results=[]
 def snapshot():
  paths=[p for d in ['backend','tests','migrations','studies-migrations','contracts','tools','deployment','web/src','web/tests'] for p in (ROOT/'apps/scribeswell'/d).rglob('*') if p.is_file() and p.suffix in ('.py','.sql','.json','.mjs','.ts','.tsx','.css','.cjs') and '__pycache__' not in p.parts]
  return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
 before=snapshot();(evidence/'native-before.json').write_text(json.dumps(before,indent=2)+'\n')
 try:
  subprocess.run(['docker','run','-d','--name',name,'--label','scribeswell.fixture='+name,'-e','POSTGRES_PASSWORD=synthetic-only','-p','127.0.0.1::5432','postgres:17'],check=True,stdout=subprocess.DEVNULL)
  owned=True
  port=json.loads(subprocess.check_output(['docker','inspect',name]))[0]['NetworkSettings']['Ports']['5432/tcp'][0]['HostPort']
  assert int(port) not in (55481,55482)
  inspected=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
  resource={'logical_cpus':os.cpu_count(),'process_cpu_affinity_count':len(os.sched_getaffinity(0)),'load_average':os.getloadavg(),'fixture_image':inspected['Image'],'fixture_limits':{k:inspected['HostConfig'].get(k) for k in ('NanoCpus','CpuQuota','CpuPeriod','Memory','MemorySwap')}}
  for resource_file in ('/sys/fs/cgroup/cpu.max','/sys/fs/cgroup/memory.max'):
   candidate=Path(resource_file)
   if candidate.is_file():resource[resource_file]=candidate.read_text().strip()
  (evidence/'resource-observation.json').write_text(json.dumps(resource,indent=2)+'\n')
  deadline=time.monotonic()+45
  while subprocess.run(['docker','exec',name,'pg_isready','-U','postgres'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:
   if time.monotonic()>deadline:raise RuntimeError('owned_postgres_not_ready')
   time.sleep(.2)
  env=os.environ.copy()
  for k in list(env):
   if k.startswith('PG') or 'NATIVE' in k or k in ('DATABASE_URL','PYTEST_ADDOPTS') or k.endswith('_DATABASE_URL') or k.endswith('_TEST_ADMIN_URL'):env.pop(k,None)
  url='postgresql://postgres:synthetic-only@127.0.0.1:'+port+'/postgres'
  env.update(SCRIBESWELL_TEST_DATABASE_URL=url,SCRIBESWELL_NOTES_TEST_ADMIN_URL=url,SCRIBESWELL_PUBLICATION_NATIVE='1',SCRIBESWELL_OWN_HIGHLIGHTS_NATIVE='1',SCRIBESWELL_OWN_COPIES_NATIVE='1',SCRIBESWELL_STUDY_DETAILS_NATIVE='1',SCRIBESWELL_NOTES_BROWSER_QUALIFY='true',SCRIBESWELL_TEST_PYTHON=PYTHON)
  argv=[PYTHON,'-m','pytest','-q','apps/scribeswell/tests/test_personal_notes_storage.py::test_native_browser_create_write_reopen','-rs']
  print('Owned isolated PostgreSQL17 ready; port '+port+'; KDG ports untouched',flush=True)
  start=time.monotonic()
  with (evidence/'native-full.log').open('w') as out:r=subprocess.run(argv,cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=1800)
  results.append(dict(argv=argv,exit_code=r.returncode,seconds=round(time.monotonic()-start,2)))
 finally:
  if owned:
   stopped=subprocess.run(['docker','stop','--time','10',name],stdout=subprocess.DEVNULL).returncode==0
   running=json.loads(subprocess.check_output(['docker','inspect',name]))[0]['State']['Running']
   assert stopped and not running,'owned_fixture_stop_unverified'
   print('Owned PostgreSQL fixture stopped; its port released; KDG ports untouched',flush=True)
  after=snapshot();(evidence/'native-after.json').write_text(json.dumps(after,indent=2)+'\n')
  (evidence/'native-results.json').write_text(json.dumps(dict(results=results,container=name,stopped=owned and stopped,source_unchanged=before==after),indent=2)+'\n')
  assert before==after,'source_changed_during_native_run'
 return 0 if results and all(r['exit_code']==0 for r in results) else 1
if __name__=='__main__':
 signal.signal(signal.SIGTERM,lambda *_:(_ for _ in ()).throw(KeyboardInterrupt()))
 sys.exit(main())
