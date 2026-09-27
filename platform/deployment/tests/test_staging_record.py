import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('record',Path(__file__).parents[1]/'record-staging.py');record=importlib.util.module_from_spec(spec);spec.loader.exec_module(record)
class StagingRecord(unittest.TestCase):
 def fixtures(self):
  env={'NETLIFY_SITE_ID':'site-id','RELEASE_SHA':'a'*40,'PUBLIC_SITE_ORIGIN':'https://staging--example.netlify.app','PUBLIC_API_ORIGIN':'https://api.stage.test','VITE_SUPABASE_URL':'https://stage.supabase.co','GITHUB_RUN_ID':'42','GITHUB_RUN_ATTEMPT':'1'}
  result={'site_id':'site-id','site_name':'example','deploy_id':'deploy-id','deploy_url':'https://deploy-id--example.netlify.app'}
  site={'id':'site-id','name':'example','published_deploy':{'id':'prior-prod'}}
  deploy={'id':'deploy-id','site_id':'site-id','state':'ready','branch':'staging','context':'branch-deploy','deploy_ssl_url':result['deploy_url']}
  identity={'sha':env['RELEASE_SHA'],'environment':'staging','site':env['PUBLIC_SITE_ORIGIN'],'api':env['PUBLIC_API_ORIGIN'],'supabase_url':env['VITE_SUPABASE_URL'],'release_attempt':'42-1'}
  def fetch(url,authenticated):
   if '/sites/' in url:self.assertTrue(authenticated);return site
   if '/deploys/' in url:self.assertTrue(authenticated);return deploy
   self.assertFalse(authenticated);return identity
  return env,result,site,deploy,identity,fetch
 def test_immutable_cli_url_is_distinct_from_verified_alias(self):
  env,result,site,deploy,identity,fetch=self.fixtures();self.assertNotEqual(result['deploy_url'],env['PUBLIC_SITE_ORIGIN']);self.assertTrue(record.verify(result,env,fetch)['complete'])
 def test_wrong_site_production_and_stale_alias_never_create_success(self):
  for target,key,value in [('result','site_id','wrong'),('deploy','branch','main'),('result','url','https://production.test'),('identity','sha','b'*40),('identity','api','https://wrong.test')]:
   with self.subTest(target=target,key=key):
    env,result,site,deploy,identity,fetch=self.fixtures();{'result':result,'deploy':deploy,'identity':identity}[target][key]=value
    with self.assertRaises(ValueError):record.verify(result,env,fetch)
