"""Provider evidence must identify the live production site and exact release."""
import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('record_production',Path(__file__).parents[1]/'record-production.py')
record=importlib.util.module_from_spec(spec)
spec.loader.exec_module(record)
class ProductionRecord(unittest.TestCase):
 def fixtures(self):
  env={'NETLIFY_SITE_ID':'site-id','RELEASE_SHA':'a'*40,'PUBLIC_SITE_ORIGIN':'https://scribeswell.test','PUBLIC_API_ORIGIN':'https://api.scribeswell.test','VITE_SUPABASE_URL':'https://prod.supabase.co','GITHUB_RUN_ID':'42','GITHUB_RUN_ATTEMPT':'1'}
  result={'site_id':'site-id','deploy_id':'deploy-id'}
  data={'site':{'id':'site-id','custom_domain':'scribeswell.test','published_deploy':{'id':'deploy-id'}},'deploy':{'id':'deploy-id','site_id':'site-id','state':'ready','context':'production'},'identity':{'sha':'a'*40,'environment':'production','site':env['PUBLIC_SITE_ORIGIN'],'api':env['PUBLIC_API_ORIGIN'],'supabase_url':env['VITE_SUPABASE_URL'],'release_attempt':'42-1'}}
  def fetch(url,authenticated):
   if url.endswith('/release-identity.json'):
    self.assertFalse(authenticated);return data['identity']
   self.assertTrue(authenticated)
   return data['site'] if '/sites/' in url else data['deploy']
  return result,env,data,fetch
 def test_exact_published_release(self):
  result,env,data,fetch=self.fixtures()
  self.assertTrue(record.verify(result,env,fetch,lambda env:None)['complete'])
 def test_wrong_site_draft_unpublished_failed_or_stale_release_rejected(self):
  mutations=[('site','id','other'),('site','published_deploy',{'id':'old'}),('deploy','context','branch-deploy'),('deploy','state','error'),('deploy','site_id','other'),('deploy','id','other'),('identity','sha','b'*40),('identity','environment','staging'),('identity','release_attempt','42-0'),('identity','supabase_url','https://stage.supabase.co')]
  for group,key,value in mutations:
   with self.subTest(group=group,key=key):
    result,env,data,fetch=self.fixtures();data[group][key]=value
    with self.assertRaises(ValueError):record.verify(result,env,fetch,lambda env:None)
 def test_cli_site_mismatch_rejected_before_fetch(self):
  result,env,data,fetch=self.fixtures();result['site_id']='other'
  with self.assertRaises(ValueError):record.verify(result,env,lambda *args:self.fail('must not fetch'),lambda env:None)

 def test_target_domain_checked_before_publish(self):
  result,env,data,fetch=self.fixtures()
  data['site']['custom_domain']='another.test'
  with self.assertRaisesRegex(record.VerificationError,'site_origin_mismatch'):record.target(env,fetch)
 def test_public_api_failure_blocks_marker(self):
  result,env,data,fetch=self.fixtures()
  def probe(env):raise record.VerificationError('public_api_cors_mismatch')
  with self.assertRaisesRegex(record.VerificationError,'public_api_cors_mismatch'):record.verify(result,env,fetch,probe)
 def test_safe_error_codes(self):
  import urllib.error
  self.assertEqual(record.error_code(urllib.error.HTTPError('https://private.test',403,'secret body',{},None)),'http_auth_rejected')
  self.assertEqual(record.error_code(urllib.error.URLError('secret URL')),'network_or_tls_failed')
  self.assertEqual(record.error_code(ValueError('secret JSON')),'invalid_verification_data')
 def test_api_probe_requires_public_https_response_and_exact_cors(self):
  import io
  from unittest.mock import patch
  result,env,data,fetch=self.fixtures()
  class Response(io.StringIO):
   status=200
   headers={'Access-Control-Allow-Origin':env['PUBLIC_SITE_ORIGIN']}
   def geturl(self):return env['PUBLIC_API_ORIGIN']+'/directory/api/apps'
  with patch.object(record.urllib.request,'urlopen',return_value=Response('[]')) as call:
   record.probe_api(env)
   self.assertEqual(call.call_args.args[0].headers['Origin'],env['PUBLIC_SITE_ORIGIN'])
  for cors in [None,'*','https://other.test']:
   response=Response('[]');response.headers={'Access-Control-Allow-Origin':cors}
   with patch.object(record.urllib.request,'urlopen',return_value=response):
    with self.assertRaisesRegex(record.VerificationError,'public_api_cors_mismatch'):record.probe_api(env)
 def test_verification_failure_never_writes_success(self):
  from unittest.mock import patch
  import tempfile
  import os
  with tempfile.TemporaryDirectory() as directory:
   previous=Path.cwd()
   try:
    os.chdir(directory)
    Path('netlify-deploy.json').write_text('{}')
    with patch.object(record,'verify',side_effect=record.VerificationError('site_origin_mismatch')),patch.object(record.time,'sleep'),patch('sys.argv',['record-production.py']):
     with self.assertRaisesRegex(SystemExit,'stage=published_release code=site_origin_mismatch'):record.main()
    self.assertFalse(Path('production.json').exists())
   finally:os.chdir(previous)
