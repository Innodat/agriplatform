"""Verify the CLI result, provider target and actual alias before recording success.

CLI23.6.0 deploy.js lines405-406 send alias as branch;475 and563-568 expose
API deploy_ssl_url as JSON deploy_url, which need not be the stable alias.
"""
import json
import os
from pathlib import Path
import re
import time
import urllib.request
from urllib.parse import quote

def verify(result,env,fetch):
 site_id=env['NETLIFY_SITE_ID'];deploy_id=result.get('deploy_id','')
 if result.get('site_id')!=site_id or not re.fullmatch('[a-zA-Z0-9-]+',deploy_id) or 'url' in result:raise ValueError('CLI result does not identify a nonproduction deployment for this site')
 site=fetch('https://api.netlify.com/api/v1/sites/'+quote(site_id,safe=''),True)
 deploy=fetch('https://api.netlify.com/api/v1/deploys/'+deploy_id,True)
 alias='https://staging--'+site['name']+'.netlify.app'
 if env['PUBLIC_SITE_ORIGIN']!=alias or site['id']!=site_id or result.get('site_name')!=site['name']:raise ValueError('staging alias/site mismatch')
 if deploy.get('id')!=deploy_id or deploy.get('site_id')!=site_id or deploy.get('state')!='ready' or deploy.get('branch')!='staging':raise ValueError('deployment is not ready for this staging alias')
 if (site.get('published_deploy') or {}).get('id')==deploy_id:raise ValueError('production deployment cannot be staging evidence')
 if result.get('deploy_url')!=(deploy.get('deploy_ssl_url') or deploy.get('deploy_url')):raise ValueError('CLI deploy URL mismatch')
 identity=fetch(alias+'/release-identity.json',False)
 expected={'sha':env['RELEASE_SHA'],'environment':'staging','site':alias,'api':env['PUBLIC_API_ORIGIN'],'supabase_url':env['VITE_SUPABASE_URL'],'release_attempt':env['GITHUB_RUN_ID']+'-'+env['GITHUB_RUN_ATTEMPT']}
 if identity!=expected:raise ValueError('stable alias does not serve this release and public configuration')
 return {'sha':env['RELEASE_SHA'],'environment':'staging','complete':True,'netlify_site_id':site_id,'netlify_deploy_id':deploy_id,'netlify_deploy_url':result['deploy_url'],'frontend_origin':alias,'api_origin':env['PUBLIC_API_ORIGIN'],'run_id':env['GITHUB_RUN_ID']}

def main():
 def fetch(url,authenticated):
  headers={'Authorization':'Bearer '+os.environ['NETLIFY_AUTH_TOKEN']} if authenticated else {'Cache-Control':'no-cache'}
  with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=15) as response:return json.load(response)
 result=json.loads(Path('netlify-deploy.json').read_text())
 for attempt in range(6):
  try:record=verify(result,os.environ,fetch);break
  except Exception:
   if attempt==5:raise SystemExit('Staging provider/alias verification failed; no success marker written') from None
   time.sleep(3)
 Path('staged.json').write_text(json.dumps(record,indent=2)+'\n')
if __name__=='__main__':main()
