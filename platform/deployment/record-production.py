"""Bind the destination before publishing; record verified production success."""
import argparse
import json
import os
from pathlib import Path
import re
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

def verify(result,env,fetch,probe_api):
 site_id=env['NETLIFY_SITE_ID'];deploy_id=result.get('deploy_id','')
 if result.get('site_id')!=site_id or not re.fullmatch('[a-zA-Z0-9-]+',deploy_id):
  raise VerificationError('cli_site_mismatch')
 site=target(env,fetch)
 deploy=fetch('https://api.netlify.com/api/v1/deploys/'+deploy_id,True)
 if (site.get('published_deploy') or {}).get('id')!=deploy_id:
  raise VerificationError('deploy_not_published')
 if deploy.get('id')!=deploy_id or deploy.get('site_id')!=site_id or deploy.get('state')!='ready' or deploy.get('context')!='production':
  raise VerificationError('deploy_not_ready_production')
 identity=fetch(env['PUBLIC_SITE_ORIGIN']+'/release-identity.json',False)
 expected={'sha':env['RELEASE_SHA'],'environment':'production','site':env['PUBLIC_SITE_ORIGIN'],'api':env['PUBLIC_API_ORIGIN'],'supabase_url':env['VITE_SUPABASE_URL'],'release_attempt':env['GITHUB_RUN_ID']+'-'+env['GITHUB_RUN_ATTEMPT']}
 if identity!=expected:raise VerificationError('release_identity_mismatch')
 probe_api(env)
 return {'sha':env['RELEASE_SHA'],'environment':'production','complete':True,'netlify_site_id':site_id,'netlify_deploy_id':deploy_id,'frontend_origin':env['PUBLIC_SITE_ORIGIN'],'api_origin':env['PUBLIC_API_ORIGIN'],'run_id':env['GITHUB_RUN_ID'],'run_attempt':env['GITHUB_RUN_ATTEMPT']}

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
 parser=argparse.ArgumentParser();parser.add_argument('--preflight',action='store_true');args=parser.parse_args()
 stage='target_preflight' if args.preflight else 'published_release'
 def fetch(url,authenticated):
  headers={'Authorization':'Bearer '+os.environ['NETLIFY_AUTH_TOKEN']} if authenticated else {'Cache-Control':'no-cache'}
  with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=15) as response:return json.load(response)
 for attempt in range(6):
  try:
   if args.preflight:target(os.environ,fetch);return
   record=verify(json.loads(Path('netlify-deploy.json').read_text()),os.environ,fetch,probe_api)
   break
  except Exception as error:
   if attempt==5:raise SystemExit('Production verification failed: stage='+stage+' code='+error_code(error)+'; reconcile provider state before retrying') from None
   time.sleep(3)
 Path('production.json').write_text(json.dumps(record,indent=2)+'\n')
if __name__=='__main__':main()
