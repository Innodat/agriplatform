"""Production retention is bound to provider, artifact, configuration and history."""
import copy
import importlib.util
import contextlib
import io
import json
import os
import subprocess
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('frontend_record',Path(__file__).parents[1]/'record-production.py')
record=importlib.util.module_from_spec(spec);spec.loader.exec_module(record)
class Selection(unittest.TestCase):
 def fixture(self):
  env={'DEPLOY_ENV':'production','NETLIFY_SITE_ID':'site-id','RELEASE_SHA':'b'*40,'PUBLIC_SITE_ORIGIN':'https://site.test','PUBLIC_API_ORIGIN':'https://api.test','VITE_SUPABASE_URL':'https://db.test','VITE_SUPABASE_ANON_KEY':'sb_publishable_fixture','GITHUB_RUN_ID':'43','GITHUB_RUN_ATTEMPT':'1'}
  identity={'sha':'a'*40,'environment':'production','site':env['PUBLIC_SITE_ORIGIN'],'api':env['PUBLIC_API_ORIGIN'],'supabase_url':env['VITE_SUPABASE_URL'],'release_attempt':'42-1','public_build_fingerprint':'f'*64}
  data={'site':{'id':'site-id','name':'boabab','custom_domain':'site.test','published_deploy':{'id':'deploy-id'}},'deploy':{'id':'deploy-id','site_id':'site-id','state':'ready','context':'production','deploy_ssl_url':'https://deploy-id--fixture.netlify.app'},'identity':identity,'immutable':copy.deepcopy(identity)}
  def fetch(url,authenticated):
   if url.endswith('/release-identity.json'):return data['identity'] if url.startswith(env['PUBLIC_SITE_ORIGIN']) else data['immutable']
   return data['site'] if '/sites/' in url else data['deploy']
  return env,data,fetch
 def select(self,env,fetch):
  with patch.object(record,'fingerprint',return_value='f'*64),patch.object(record,'changes',return_value={'build':False,'reason':'no_frontend_inputs_changed'}):return record.select_frontend(env,fetch)
 def test_backend_release_retains_frontend_and_records_separate_sha(self):
  env,data,fetch=self.fixture();plan=self.select(env,fetch);self.assertFalse(plan['build'])
  with patch.object(record,'fingerprint',return_value='f'*64):
   evidence=record.verify_retained(plan,env,fetch,lambda env:None)
  self.assertEqual(evidence['sha'],'b'*40);self.assertEqual(evidence['frontend_sha'],'a'*40);self.assertEqual(evidence['frontend_release_attempt'],'42-1')
 def test_uncertain_missing_wrong_provider_identity_and_config_rebuild(self):
  for group,key,value in [('site','published_deploy',None),('deploy','site_id','wrong'),('identity','sha','invalid'),('identity','public_build_fingerprint','old'),('identity','release_attempt',None),('immutable','sha','c'*40)]:
   with self.subTest(group=group,key=key):
    env,data,fetch=self.fixture();data[group][key]=value;self.assertTrue(self.select(env,fetch)['build'])
  env,data,fetch=self.fixture();self.assertTrue(self.select(env,lambda *args:(_ for _ in ()).throw(TimeoutError()))['build'])
 def test_force_build_and_changed_configuration(self):
  env,data,fetch=self.fixture();env['FORCE_FRONTEND_BUILD']='true';self.assertTrue(self.select(env,fetch)['build'])
  env,data,fetch=self.fixture()
  with patch.object(record,'fingerprint',return_value='e'*64):self.assertTrue(record.select_frontend(env,fetch)['build'])
 def test_baseline_race_identity_config_and_attempt_rejected(self):
  for group,key,value in [('site','published_deploy',{'id':'other'}),('deploy','site_id','wrong'),('identity','sha','c'*40),('identity','release_attempt','42-2'),('identity','public_build_fingerprint','old')]:
   with self.subTest(group=group,key=key):
    env,data,fetch=self.fixture();plan=self.select(env,fetch);data[group][key]=value
    with patch.object(record,'fingerprint',return_value='f'*64),self.assertRaises(record.VerificationError):record.verify_retained(plan,env,fetch,lambda env:None)
 def test_race_during_api_probe_rejected(self):
  env,data,fetch=self.fixture();plan=self.select(env,fetch)
  def probe(env):data['site']['published_deploy']={'id':'other'}
  with patch.object(record,'fingerprint',return_value='f'*64),self.assertRaises(record.VerificationError):record.verify_retained(plan,env,fetch,probe)
 def test_public_key_rotation_changes_real_fingerprint(self):
  env,data,fetch=self.fixture();before=record.fingerprint(env)
  env['VITE_SUPABASE_ANON_KEY']='sb_publishable_rotated'
  self.assertNotEqual(before,record.fingerprint(env))
 def test_plan_is_run_bound_and_contains_no_public_key_or_token(self):
  env,data,fetch=self.fixture();env['NETLIFY_AUTH_TOKEN']='private-fixture-token';plan=self.select(env,fetch)
  import json
  encoded=json.dumps(plan)
  self.assertNotIn(env['VITE_SUPABASE_ANON_KEY'],encoded);self.assertNotIn(env['NETLIFY_AUTH_TOKEN'],encoded)
  for key,value in [('RELEASE_SHA','c'*40),('GITHUB_RUN_ATTEMPT','2'),('NETLIFY_SITE_ID','other')]:
   with self.subTest(key=key),patch.object(record,'fingerprint',return_value='f'*64),self.assertRaises(record.VerificationError):record.verify_retained(plan,{**env,key:value},fetch,lambda env:None)
 def test_retained_config_change_and_api_failure_prevent_evidence(self):
  env,data,fetch=self.fixture();plan=self.select(env,fetch)
  with patch.object(record,'fingerprint',return_value='e'*64),self.assertRaises(record.VerificationError):record.verify_retained(plan,env,fetch,lambda env:None)
  def failed(env):raise record.VerificationError('public_api_cors_mismatch')
  with patch.object(record,'fingerprint',return_value='f'*64),self.assertRaisesRegex(record.VerificationError,'public_api_cors_mismatch'):record.verify_retained(plan,env,fetch,failed)

 def test_initial_provider_race_rebuilds_with_safe_diagnostic(self):
  env,data,fetch=self.fixture();site_calls=0
  def racing_fetch(url,authenticated):
   nonlocal site_calls
   if '/sites/' in url:
    site_calls+=1
    if site_calls==2:return {**data['site'],'published_deploy':{'id':'other'}}
   return fetch(url,authenticated)
  plan=self.select(env,racing_fetch)
  self.assertTrue(plan['build']);self.assertEqual(plan['error_code'],'published_deploy_changed');self.assertEqual(site_calls,2)
 def test_fallback_diagnostic_never_includes_transport_details(self):
  env,data,fetch=self.fixture()
  def unavailable(*args):raise record.urllib.error.URLError('credential=private-fixture-token payload=secret')
  plan=self.select(env,unavailable)
  self.assertTrue(plan['build']);self.assertEqual(plan['error_code'],'network_or_tls_failed')
  self.assertNotIn('private-fixture-token',json.dumps(plan));self.assertNotIn('payload',json.dumps(plan))
 @contextlib.contextmanager
 def real_history(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory)
   def git(*args):return subprocess.run(['git',*args],cwd=root,capture_output=True,text=True,check=True).stdout.strip()
   def commit(name,contents):
    file=root/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(contents)
    git('add','-A');git('commit','-qm','fixture');return git('rev-parse','HEAD')
   git('init','-q');git('config','user.email','fixture@example.test');git('config','user.name','Fixture')
   commit('apps/demo/deployment/manifest.json',json.dumps({'frontend':{'path':'apps/demo/web'}}))
   commit('platform/deployment/registry.json',json.dumps({'manifests':['apps/demo/deployment/manifest.json']}))
   baseline=commit('apps/demo/web/main.js','initial frontend')
   env,data,fetch=self.fixture()
   data['identity']['sha']=baseline;data['identity']['public_build_fingerprint']=record.fingerprint(env)
   data['immutable']=copy.deepcopy(data['identity'])
   with patch.object(record,'ROOT',root):yield env,data,fetch,commit
 def test_real_git_selection_retains_backend_and_rebuilds_unpublished_frontend(self):
  with self.real_history() as (env,data,fetch,commit):
   env['RELEASE_SHA']=commit('services/demo/main.py','backend v1')
   plan=record.select_frontend(env,fetch)
   self.assertFalse(plan['build']);self.assertEqual(plan['reason'],'no_frontend_inputs_changed')
   self.assertEqual(plan['baseline']['identity']['sha'],data['identity']['sha'])
   commit('apps/demo/web/main.js','unpublished frontend v2')
   env['RELEASE_SHA']=commit('services/demo/main.py','backend v2')
   plan=record.select_frontend(env,fetch)
   self.assertTrue(plan['build']);self.assertEqual(plan['reason'],'frontend_inputs_changed')
 def transport(self,env,fetch):
  class Response(io.StringIO):
   status=200
   def __init__(self,url,payload):
    super().__init__(json.dumps(payload));self.url=url;self.headers={'Access-Control-Allow-Origin':env['PUBLIC_SITE_ORIGIN']}
   def geturl(self):return self.url
  def urlopen(request,timeout):
   url=request.full_url
   payload=[] if url.endswith('/directory/api/apps') else fetch(url,request.has_header('Authorization'))
   return Response(url,payload)
  return urlopen
 def test_selection_cli_persists_plan_and_lowercase_actions_output(self):
  with self.real_history() as (env,data,fetch,commit):
   env['RELEASE_SHA']=commit('services/demo/main.py','backend v1');env['NETLIFY_AUTH_TOKEN']='private-fixture-token'
   for force,expected in [('false',False),('true',True)]:
    with self.subTest(force=force),tempfile.TemporaryDirectory() as directory,contextlib.chdir(directory):
     env.update(FORCE_FRONTEND_BUILD=force,GITHUB_OUTPUT=str(Path(directory)/'actions-output'))
     expected_plan=record.select_frontend(env,fetch)
     with patch.dict(os.environ,env),patch('sys.argv',['record-production.py','--select']),patch.object(record.urllib.request,'urlopen',side_effect=self.transport(env,fetch)),contextlib.redirect_stdout(io.StringIO()):record.main()
     plan=json.loads(Path('frontend-plan.json').read_text())
     self.assertEqual(plan,expected_plan);self.assertIs(plan['build'],expected)
     self.assertEqual(Path(env['GITHUB_OUTPUT']).read_text(),'build='+str(expected).lower()+'\n')
     self.assertFalse(Path('production.json').exists())
 def test_retained_cli_reloads_plan_and_failure_never_writes_success(self):
  with self.real_history() as (env,data,fetch,commit):
   env['RELEASE_SHA']=commit('services/demo/main.py','backend v1');env['NETLIFY_AUTH_TOKEN']='private-fixture-token'
   plan=record.select_frontend(env,fetch);self.assertFalse(plan['build'])
   for changed in [False,True]:
    with self.subTest(changed=changed),tempfile.TemporaryDirectory() as directory,contextlib.chdir(directory):
     Path('frontend-plan.json').write_text(json.dumps(plan))
     if changed:data['site']['published_deploy']={'id':'other'}
     with patch.dict(os.environ,env),patch('sys.argv',['record-production.py','--retained']),patch.object(record.urllib.request,'urlopen',side_effect=self.transport(env,fetch)),patch.object(record.time,'sleep'):
      if changed:
       with self.assertRaisesRegex(SystemExit,'stage=retained_frontend'):record.main()
       self.assertFalse(Path('production.json').exists())
      else:
       record.main();evidence=json.loads(Path('production.json').read_text())
       self.assertTrue(evidence['complete']);self.assertTrue(evidence['frontend_retained'])
       self.assertEqual(evidence['backend_sha'],env['RELEASE_SHA']);self.assertEqual(evidence['frontend_sha'],data['identity']['sha'])

 def test_selection_cli_reports_only_safe_fallback_code(self):
  env,data,fetch=self.fixture();env['NETLIFY_AUTH_TOKEN']='private-fixture-token'
  with tempfile.TemporaryDirectory() as directory,contextlib.chdir(directory):
   output=io.StringIO()
   error=record.urllib.error.URLError('credential=private-fixture-token payload=secret')
   with patch.dict(os.environ,env),patch('sys.argv',['record-production.py','--select']),patch.object(record.urllib.request,'urlopen',side_effect=error),contextlib.redirect_stdout(output):record.main()
   self.assertEqual(output.getvalue(),'Frontend decision: uncertain_published_baseline code=network_or_tls_failed\n')
   plan=json.loads(Path('frontend-plan.json').read_text())
   self.assertTrue(plan['build']);self.assertEqual(plan['error_code'],'network_or_tls_failed')
   self.assertNotIn('private-fixture-token',json.dumps(plan))

 def test_immutable_url_uses_authenticated_site_name_not_deploy_alias(self):
  for alias in ['https://main--boabab.netlify.app',None]:
   with self.subTest(alias=alias):
    env,data,fetch=self.fixture();requests=[]
    if alias is None:data['deploy'].pop('deploy_ssl_url')
    else:data['deploy']['deploy_ssl_url']=alias
    def capture(url,authenticated):
     requests.append((url,authenticated));return fetch(url,authenticated)
    plan=self.select(env,capture)
    self.assertFalse(plan['build'])
    self.assertIn(('https://deploy-id--boabab.netlify.app/release-identity.json',False),requests)
    self.assertFalse(any('main--' in url for url,authenticated in requests))
 def test_malformed_site_name_cannot_construct_immutable_url(self):
  for name in [None,'','../other','wrong.example','name/path','name@evil','-leading','trailing-','a'*64]:
   with self.subTest(name=name):
    env,data,fetch=self.fixture();data['site']['name']=name;requests=[]
    def capture(url,authenticated):
     requests.append(url);return fetch(url,authenticated)
    plan=self.select(env,capture)
    self.assertTrue(plan['build']);self.assertEqual(plan['error_code'],'invalid_site_name')
    self.assertFalse(any(url.endswith('/release-identity.json') for url in requests))
