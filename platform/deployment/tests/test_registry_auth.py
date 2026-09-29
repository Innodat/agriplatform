import importlib.util
import json
import io
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch, Mock

PATH=Path(__file__).resolve().parents[1]/'registry-deploy.py'
spec=importlib.util.spec_from_file_location('registry_deploy',PATH)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class RegistryTests(unittest.TestCase):
 def test_cleanup_for_login_and_deployment_failure_and_success(self):
  original=tempfile.TemporaryDirectory
  for login_failure,exit_code in [(True,0),(False,1),(False,0)]:
   with self.subTest(login_failure=login_failure,exit_code=exit_code),original() as directory:
    existing=Path(directory)/'config.json';existing.write_text('existing-credential');configs=[]
    def login(args,**kw):
     if args[:2]==['docker','compose']:return Mock(stdout=b'2.39.4\n')
     configs.append(Path(kw['env']['DOCKER_CONFIG']))
     self.assertEqual(configs[-1].stat().st_mode & 0o777,0o700)
     self.assertEqual(kw['input'],b'temporary_secret\n');self.assertNotIn('temporary_secret',str(args))
     if login_failure:raise RuntimeError()
    def child(args,**kw):
     self.assertEqual(kw['env']['DOCKER_CONFIG'],str(configs[0]))
     self.assertNotIn('REGISTRY_TOKEN',kw['env']);self.assertTrue(kw['start_new_session'])
     return Mock(wait=Mock(return_value=exit_code))
    with patch.dict(os.environ,{'DOCKER_CONFIG':directory,'REGISTRY_TOKEN':'temporary_secret'}),patch.object(module.tempfile,'TemporaryDirectory',side_effect=lambda **kw: original(prefix=kw['prefix'])),patch.object(module.os,'geteuid',return_value=0),patch.object(module.subprocess,'run',side_effect=login),patch.object(module.subprocess,'Popen',side_effect=child) as popen:
     if login_failure or exit_code:
      with self.assertRaises(RuntimeError):module.deploy('actor','temporary_secret',['deploy'])
     else:module.deploy('actor','temporary_secret',['deploy'])
     if login_failure:popen.assert_not_called()
    self.assertFalse(configs[0].exists());self.assertEqual(existing.read_text(),'existing-credential')
 def test_invalid_no_subprocess(self):
  with patch.object(module.subprocess,'run') as run:
   with self.assertRaises(ValueError):module.deploy('bad actor','secret',[])
   run.assert_not_called()
 def test_transport_input_validation(self):
  script=(PATH.parent/'ci-deploy.sh').read_text().split(': "${DEPLOY_ENV:?}"')[0]
  env={**os.environ,'REGISTRY_ACTOR':'github-actions[bot]','REGISTRY_TOKEN':'ghs_test','GITHUB_RUN_ID':'1','GITHUB_RUN_ATTEMPT':'1'}
  self.assertEqual(subprocess.run(['bash','-c',script],env=env,capture_output=True).returncode,0)
  for value in ('','bad actor','actor;cmd'):
   self.assertNotEqual(subprocess.run(['bash','-c',script],env={**env,'REGISTRY_ACTOR':value},capture_output=True).returncode,0)
 def test_stateless_token_transport_validation(self):
  script=(PATH.parent/'ci-deploy.sh').read_text().split(': "${DEPLOY_ENV:?}"')[0]
  token='ghs_123_eyJhbGciOiJSUzI1NiJ9.eyJpYXQiOjEyM30.signature-with_dash'
  env={**os.environ,'REGISTRY_ACTOR':'Blankyc','REGISTRY_TOKEN':token,'GITHUB_RUN_ID':'1','GITHUB_RUN_ATTEMPT':'1'}
  result=subprocess.run(['bash','-c',script],env=env,capture_output=True,text=True)
  self.assertEqual(result.returncode,0,result.stderr)
  self.assertNotIn(token,result.stdout+result.stderr)
  with patch.object(module.os,'geteuid',return_value=1000):
   with self.assertRaisesRegex(ValueError,'root wrapper required'):module.deploy('Blankyc',token,['deploy'])
 def test_unsafe_token_rejected_without_disclosure(self):
  script=(PATH.parent/'ci-deploy.sh').read_text().split(': "${DEPLOY_ENV:?}"')[0]
  for token in ('secret with space','secret\nsecond-line','secret;command','x'*4097):
   env={**os.environ,'REGISTRY_ACTOR':'Blankyc','REGISTRY_TOKEN':token,'GITHUB_RUN_ID':'1','GITHUB_RUN_ATTEMPT':'1'}
   result=subprocess.run(['bash','-c',script],env=env,capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0)
   self.assertIn('Invalid registry credentials',result.stderr)
   self.assertNotIn(token,result.stdout+result.stderr)
   with patch.object(module.subprocess,'run') as run:
    with self.assertRaises(ValueError):module.deploy('Blankyc',token,['deploy'])
    run.assert_not_called()
 def test_maximum_token_survives_shell_and_main_reader(self):
  token='x'*4096
  script=(PATH.parent/'ci-deploy.sh').read_text().split(': "${DEPLOY_ENV:?}"')[0]
  env={**os.environ,'REGISTRY_ACTOR':'actor','REGISTRY_TOKEN':token,'GITHUB_RUN_ID':'1','GITHUB_RUN_ATTEMPT':'1'}
  self.assertEqual(subprocess.run(['bash','-c',script],env=env,capture_output=True).returncode,0)
  with patch.object(module.sys,'stdin',io.StringIO('actor\n'+token+'\n')),patch.object(module.signal,'signal'),patch.object(module,'deploy') as deploy:
   module.main()
   self.assertEqual(deploy.call_args.args[:2],('actor',token))
 def test_run_identifiers_fail_with_safe_diagnostic(self):
  script=(PATH.parent/'ci-deploy.sh').read_text().split(': "${DEPLOY_ENV:?}"')[0]
  base={**os.environ,'REGISTRY_ACTOR':'actor','REGISTRY_TOKEN':'ghs_private_fixture','GITHUB_RUN_ID':'1','GITHUB_RUN_ATTEMPT':'1'}
  for name in ('GITHUB_RUN_ID','GITHUB_RUN_ATTEMPT'):
   for value in (None,'','not-a-number'):
    env=base.copy()
    if value is None:env.pop(name,None)
    else:env[name]=value
    result=subprocess.run(['bash','-c',script],env=env,capture_output=True,text=True)
    self.assertNotEqual(result.returncode,0)
    self.assertIn('Invalid GitHub run identifiers',result.stderr)
    self.assertNotIn(base['REGISTRY_TOKEN'],result.stdout+result.stderr)
 def test_real_process_cancellation_drains_lock_owner_before_cleanup(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);fixture=root/'fixture.py';runner=root/'runner.py'
   fixture.write_text('''import fcntl,json,os,time
from pathlib import Path
root=Path(__file__).parent
with (root/'release.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 (root/'running.json').write_text(json.dumps({'pid':os.getpid(),'config':os.environ['DOCKER_CONFIG']}))
 while not (root/'finish').exists():time.sleep(.02)
 assert Path(os.environ['DOCKER_CONFIG']).is_dir()
 (root/'drained').write_text('yes')
''')
   runner.write_text('''import importlib.util,signal,sys,tempfile
from pathlib import Path
spec=importlib.util.spec_from_file_location('registry',sys.argv[1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
original=tempfile.TemporaryDirectory
m.tempfile.TemporaryDirectory=lambda **kw:original(prefix=kw['prefix'])
m.os.geteuid=lambda:0
from types import SimpleNamespace
m.subprocess.run=lambda *a,**kw:SimpleNamespace(stdout=b'2.39.4')
control=m.Control()
for sig in (signal.SIGTERM,signal.SIGHUP,signal.SIGINT):signal.signal(sig,control.stop)
try:m.deploy('actor','temporary_secret',[sys.executable,str(Path(__file__).with_name('fixture.py'))],control)
except RuntimeError:sys.exit(1)
''')
   process=subprocess.Popen([sys.executable,str(runner),str(PATH)],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   try:
    limit=time.monotonic()+5
    while not (root/'running.json').exists() and time.monotonic()<limit:time.sleep(.02)
    child=json.loads((root/'running.json').read_text());config=Path(child['config'])
    os.killpg(process.pid,signal.SIGTERM);time.sleep(.1)
    self.assertIsNone(process.poll());self.assertTrue(config.exists())
    import fcntl
    with (root/'release.lock').open('a') as lock:
     with self.assertRaises(BlockingIOError):fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    (root/'finish').touch()
    self.assertEqual(process.wait(timeout=5),1);self.assertTrue((root/'drained').exists());self.assertFalse(config.exists())
   finally:
    (root/'finish').touch()
    if process.poll() is None:process.kill();process.wait()

 def test_missing_system_compose_blocks_login_and_deployment(self):
  original=tempfile.TemporaryDirectory
  with patch.object(module.tempfile,'TemporaryDirectory',side_effect=lambda **kw: original(prefix=kw['prefix'])),patch.object(module.os,'geteuid',return_value=0),patch.object(module.subprocess,'run',side_effect=subprocess.CalledProcessError(1,['docker','compose'])) as run,patch.object(module.subprocess,'Popen') as popen:
   with self.assertRaises(subprocess.CalledProcessError):module.deploy('actor','temporary_secret',['deploy'])
  self.assertEqual(run.call_count,1);self.assertEqual(run.call_args.args[0],['docker','compose','version','--short']);popen.assert_not_called()
  self.assertFalse(Path(run.call_args.kwargs['env']['DOCKER_CONFIG']).exists())
 def test_complete_ci_shell_transports_frame_into_real_main_parser(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);binpath=root/'bin';binpath.mkdir()
   driver=root/'parse.py'
   driver.write_text('''import hashlib,importlib.util,json,os,sys
from pathlib import Path
path=Path(os.environ['WRAPPER_PATH'])
spec=importlib.util.spec_from_file_location('registry',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def deployment(actor,token,command,control):
 assert actor=='fixture-actor'
 assert token=='ghs_123_fixture.payload.signature-with_dash'
 assert token not in str(command)
 Path(os.environ['CAPTURE']).write_text(json.dumps({'actor':actor,'token_hash':hashlib.sha256(token.encode()).hexdigest(),'command':command}))
module.deploy=deployment
sys.argv=[str(path),*sys.argv[1:]]
module.main()
''')
   transport='''#!'''+sys.executable+'''
import json,os,shlex,subprocess,sys
from pathlib import Path
name=Path(sys.argv[0]).name
with open(os.environ['TRANSPORT_LOG'],'a') as log:log.write(json.dumps({'tool':name,'argv':sys.argv[1:]})+'\\n')
if name=='git':sys.stdout.write('fixture archive')
elif name=='ssh' and 'registry-deploy.py' in sys.argv[-1]:
 parts=shlex.split(sys.argv[-1]);index=next(i for i,p in enumerate(parts) if p.endswith('/registry-deploy.py'))
 sys.exit(subprocess.run([sys.executable,os.environ['PARSER_DRIVER'],*parts[index+1:]],stdin=sys.stdin.buffer).returncode)
'''
   for name in ('git','ssh','scp'):
    path=binpath/name;path.write_text(transport);path.chmod(0o755)
   env={**os.environ,'PATH':str(binpath)+os.pathsep+os.environ['PATH'],'REGISTRY_ACTOR':'fixture-actor','REGISTRY_TOKEN':'ghs_123_fixture.payload.signature-with_dash','GITHUB_RUN_ID':'123','GITHUB_RUN_ATTEMPT':'2','DEPLOY_ENV':'staging','RELEASE_SHA':'a'*40,'DEPLOY_HOST':'host.test','DEPLOY_USER':'root','SSH_PRIVATE_KEY':'fixture-key','SSH_KNOWN_HOSTS':'fixture-known-host','PUBLIC_SITE_ORIGIN':'https://site.test','PUBLIC_API_ORIGIN':'https://api.test','VITE_SUPABASE_URL':'https://project.test','WRAPPER_PATH':str(PATH),'PARSER_DRIVER':str(driver),'CAPTURE':str(root/'captured.json'),'TRANSPORT_LOG':str(root/'transport.jsonl')}
   archive=Path('/tmp/release-source.tar');before=archive.read_bytes() if archive.exists() else None
   try:
    result=subprocess.run(['bash',str(PATH.parent/'ci-deploy.sh')],cwd=root,env=env,capture_output=True,text=True,timeout=10)
   finally:
    if before is None:archive.unlink(missing_ok=True)
    else:archive.write_bytes(before)
   self.assertEqual(result.returncode,0,result.stderr)
   import hashlib
   capture=json.loads((root/'captured.json').read_text());self.assertEqual(capture['actor'],'fixture-actor');self.assertEqual(capture['token_hash'],hashlib.sha256(b'ghs_123_fixture.payload.signature-with_dash').hexdigest())
   command=capture['command'];self.assertTrue(command[1].endswith('/host-release.py'))
   self.assertEqual(command[command.index('--environment')+1],'staging');self.assertEqual(command[command.index('--sha')+1],'a'*40)
   self.assertEqual(command[command.index('--release-dir')+1],'/srv/agriplatform/releases/'+'a'*40+'-123-2')
   transport_text=(root/'transport.jsonl').read_text()
   for secret in ('ghs_123_fixture.payload.signature-with_dash','fixture-key'):
    self.assertNotIn(secret,transport_text);self.assertNotIn(secret,result.stdout+result.stderr+str(command))
   for entry in map(json.loads,transport_text.splitlines()):
    if entry['tool']=='ssh':self.assertIn('StrictHostKeyChecking=yes',entry['argv'])
