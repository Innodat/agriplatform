"""Bind the destination before publishing; record verified production success."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.request
from urllib.parse import quote, urlsplit

class VerificationError(ValueError):
 pass

def target(env,fetch):
 site_id=env['NETLIFY_SITE_ID']
 site=fetch('https://api.netlify.com/api/v1/sites/'+quote(site_id,safe=''),True)
 intended=urlsplit(env['PUBLIC_SITE_ORIGIN'])
 if intended.scheme!='https' or not intended.hostname or intended.path or intended.query or intended.fragment or intended.username or intended.port:
  raise VerificationError('invalid_site_origin')
 domains={site.get('custom_domain'),*(site.get('domain_aliases') or [])}
 for key in ('ssl_url','url'):
  if site.get(key):domains.add(urlsplit(site[key]).hostname)
 if site.get('id')!=site_id or intended.hostname not in domains:
  raise VerificationError('site_origin_mismatch')
 return site

ROOT=Path(__file__).resolve().parents[2]
DETECTOR=Path(__file__).with_name('frontend-inputs.mjs')

def fingerprint(env):
 # The same Node implementation writes the build identity and selects releases.
 public={key:env[key] for key in ('DEPLOY_ENV','PUBLIC_SITE_ORIGIN','PUBLIC_API_ORIGIN','VITE_SUPABASE_URL','VITE_SUPABASE_ANON_KEY')}
 result=subprocess.run(['node',str(DETECTOR),'fingerprint'],env={'PATH':os.environ.get('PATH',''),**public},capture_output=True,text=True,check=True)
 return result.stdout.strip()

def changes(baseline,current):
 result=subprocess.run(['node',str(DETECTOR),baseline,current],cwd=ROOT,capture_output=True,text=True,check=True)
 decision=json.loads(result.stdout)
 if type(decision.get('build')) is not bool:raise VerificationError('invalid_change_decision')
 return decision

def configuration(env):
 return {'environment':'production','site':env['PUBLIC_SITE_ORIGIN'],'api':env['PUBLIC_API_ORIGIN'],'supabase_url':env['VITE_SUPABASE_URL'],'public_build_fingerprint':fingerprint(env)}

def published(env,fetch):
 site=target(env,fetch)
 deploy_id=(site.get('published_deploy') or {}).get('id','')
 if not isinstance(deploy_id,str) or not re.fullmatch('[a-zA-Z0-9-]+',deploy_id):raise VerificationError('missing_published_deploy')
 deploy=fetch('https://api.netlify.com/api/v1/deploys/'+deploy_id,True)
 if deploy.get('id')!=deploy_id or deploy.get('site_id')!=env['NETLIFY_SITE_ID'] or deploy.get('state')!='ready' or deploy.get('context')!='production':
  raise VerificationError('deploy_not_ready_production')
 # Bind the identity to both this immutable deploy and the public destination.
 # deploy_ssl_url may be a mutable branch alias even for production deploys.
 # Netlify's immutable deploy subdomain is <deploy-id>--<site-name>.netlify.app.
 site_name=site.get('name')
 if not isinstance(site_name,str) or not re.fullmatch('[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?',site_name):
  raise VerificationError('invalid_site_name')
 permalink='https://'+deploy_id+'--'+site_name+'.netlify.app'
 immutable=fetch(permalink+'/release-identity.json',False)
 identity=fetch(env['PUBLIC_SITE_ORIGIN']+'/release-identity.json',False)
 if not isinstance(identity,dict) or identity!=immutable:raise VerificationError('published_identity_mismatch')
 expected=configuration(env)
 if set(identity)!=set(expected)|{'sha','release_attempt'} or any(identity.get(key)!=value for key,value in expected.items()):raise VerificationError('release_configuration_mismatch')
 if not isinstance(identity.get('sha'),str) or not re.fullmatch('[a-f0-9]{40}',identity['sha']):raise VerificationError('invalid_frontend_revision')
 if not isinstance(identity.get('release_attempt'),str) or not re.fullmatch('[0-9]+-[0-9]+',identity['release_attempt']):raise VerificationError('invalid_frontend_attempt')
 # A publish between the first provider lookup and asset requests is not a baseline.
 if (target(env,fetch).get('published_deploy') or {}).get('id')!=deploy_id:raise VerificationError('published_deploy_changed')
 return {'site_id':env['NETLIFY_SITE_ID'],'deploy_id':deploy_id,'identity':identity}

def select_frontend(env,fetch):
 plan={'version':1,'backend_sha':env['RELEASE_SHA'],'release_attempt':env['GITHUB_RUN_ID']+'-'+env['GITHUB_RUN_ATTEMPT'],'build':True,'reason':'uncertain_published_baseline'}
 if env.get('FORCE_FRONTEND_BUILD','').lower()=='true':return {**plan,'reason':'manual_force'}
 try:
  baseline=published(env,fetch)
  decision=changes(baseline['identity']['sha'],env['RELEASE_SHA'])
  return {**plan,**decision,'baseline':baseline}
 except Exception as error:
  # Missing history, old identities and unavailable provider data only cause builds.
  return {**plan,'error_code':error_code(error)}

def evidence(env,baseline,retained):
 return {'sha':env['RELEASE_SHA'],'backend_sha':env['RELEASE_SHA'],'environment':'production','complete':True,'netlify_site_id':baseline['site_id'],'netlify_deploy_id':baseline['deploy_id'],'frontend_sha':baseline['identity']['sha'],'frontend_release_attempt':baseline['identity']['release_attempt'],'public_build_fingerprint':baseline['identity']['public_build_fingerprint'],'frontend_retained':retained,'frontend_origin':env['PUBLIC_SITE_ORIGIN'],'api_origin':env['PUBLIC_API_ORIGIN'],'run_id':env['GITHUB_RUN_ID'],'run_attempt':env['GITHUB_RUN_ATTEMPT']}

def verify(result,env,fetch,probe_api):
 site_id=env['NETLIFY_SITE_ID'];deploy_id=result.get('deploy_id','')
 if result.get('site_id')!=site_id or not isinstance(deploy_id,str) or not re.fullmatch('[a-zA-Z0-9-]+',deploy_id):raise VerificationError('cli_site_mismatch')
 baseline=published(env,fetch)
 if baseline['deploy_id']!=deploy_id:raise VerificationError('deploy_not_published')
 expected={**configuration(env),'sha':env['RELEASE_SHA'],'release_attempt':env['GITHUB_RUN_ID']+'-'+env['GITHUB_RUN_ATTEMPT']}
 if baseline['identity']!=expected:raise VerificationError('release_identity_mismatch')
 probe_api(env)
 if published(env,fetch)!=baseline:raise VerificationError('published_deploy_changed')
 return evidence(env,baseline,False)

def verify_retained(plan,env,fetch,probe_api):
 if plan.get('version')!=1 or plan.get('build') is not False or plan.get('backend_sha')!=env['RELEASE_SHA'] or plan.get('release_attempt')!=env['GITHUB_RUN_ID']+'-'+env['GITHUB_RUN_ATTEMPT']:
  raise VerificationError('invalid_retention_plan')
 baseline=published(env,fetch)
 if baseline!=plan.get('baseline'):raise VerificationError('retained_frontend_changed')
 probe_api(env)
 if published(env,fetch)!=baseline:raise VerificationError('retained_frontend_changed')
 return evidence(env,baseline,True)

def probe_api(env):
 url=env['PUBLIC_API_ORIGIN']+'/directory/api/apps'
 request=urllib.request.Request(url,headers={'Origin':env['PUBLIC_SITE_ORIGIN']})
 with urllib.request.urlopen(request,timeout=15) as response:
  if response.status!=200 or response.geturl()!=url:raise VerificationError('public_api_status_or_redirect')
  if response.headers.get('Access-Control-Allow-Origin')!=env['PUBLIC_SITE_ORIGIN']:
   raise VerificationError('public_api_cors_mismatch')
  if not isinstance(json.load(response),list):raise VerificationError('public_api_invalid_directory')

def error_code(error):
 if isinstance(error,VerificationError):return str(error)
 if isinstance(error,urllib.error.HTTPError):return 'http_auth_rejected' if error.code in (401,403) else 'http_request_failed'
 if isinstance(error,(urllib.error.URLError,TimeoutError)):return 'network_or_tls_failed'
 if isinstance(error,(json.JSONDecodeError,KeyError,TypeError,ValueError)):return 'invalid_verification_data'
 return 'verification_failed'

def main():
 parser=argparse.ArgumentParser();mode=parser.add_mutually_exclusive_group();mode.add_argument('--preflight',action='store_true');mode.add_argument('--select',action='store_true');mode.add_argument('--retained',action='store_true');args=parser.parse_args()
 stage='target_preflight' if args.preflight else ('retained_frontend' if args.retained else 'published_release')
 def fetch(url,authenticated):
  headers={'Authorization':'Bearer '+os.environ['NETLIFY_AUTH_TOKEN']} if authenticated else {'Cache-Control':'no-cache'}
  with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=15) as response:
   if response.geturl()!=url:raise VerificationError('verification_redirect')
   return json.load(response)
 if args.select:
  plan=select_frontend(os.environ,fetch)
  Path('frontend-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
  if os.environ.get('GITHUB_OUTPUT'):
   with open(os.environ['GITHUB_OUTPUT'],'a') as output:output.write('build='+str(plan['build']).lower()+'\n')
  print('Frontend decision: '+plan['reason']+(' code='+plan['error_code'] if 'error_code' in plan else ''))
  return
 for attempt in range(6):
  try:
   if args.preflight:target(os.environ,fetch);return
   record=verify_retained(json.loads(Path('frontend-plan.json').read_text()),os.environ,fetch,probe_api) if args.retained else verify(json.loads(Path('netlify-deploy.json').read_text()),os.environ,fetch,probe_api)
   break
  except Exception as error:
   if attempt==5:raise SystemExit('Production verification failed: stage='+stage+' code='+error_code(error)+'; reconcile provider state before retrying') from None
   time.sleep(3)
 Path('production.json').write_text(json.dumps(record,indent=2)+'\n')
if __name__=='__main__':main()
