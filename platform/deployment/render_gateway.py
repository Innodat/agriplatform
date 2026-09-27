"""Render standalone APISIX YAML (JSON is a YAML subset) and Compose externally."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit
from release import ROOT, load_manifests
APISIX='apache/apisix:3.18.0-debian@sha256:84e6b5e787e9f889ebff88161cb9a16599bafcffa236c6b54c7f779a0655940d'

def require_compose():
 version=subprocess.check_output(['docker','compose','version','--short'],text=True).strip().lstrip('v')
 match=re.match(r'(\d+)\.(\d+)\.(\d+)',version)
 if not match or tuple(map(int,match.groups()))<(2,30,0):raise ValueError('Docker Compose >=2.30.0 required for literal raw env files')
 return version

def origin(value):
 u=urlsplit(value)
 if u.scheme!='https' or not u.hostname or u.username or u.password or u.path != '' or u.query or u.fragment:raise ValueError('HTTPS origin required')
 return u

def routes(host='api.scribeswell.com',site='https://scribeswell.com',manifests=None):
 result=[]
 for m in manifests or load_manifests():
  if 'public' not in m:continue
  prefix=m['public']['prefix']
  result.append({'id':m['id'],'host':host,'uris':[prefix+p for p in m['public']['paths']], 'methods':m['public']['methods'],'vars':[['scheme','==','https']], 'plugins':{'proxy-rewrite':{'regex_uri':['^'+prefix+'/(.*)','/$1']},'cors':{'allow_origins':site,'allow_methods':','.join(m['public']['methods']),'allow_headers':'Authorization,Content-Type,X-Org-ID','allow_credential':True,'max_age':600}},'upstream':{'type':'roundrobin','nodes':{m['id']+':8000':1},'timeout':{'connect':5,'send':30,'read':30}}})
 return result

def render(output,env_dir,images,site,api,cert,key,environment):
 origin(site);host=origin(api).hostname
 if environment not in ('staging','production'):raise ValueError('invalid environment')
 if environment=='staging' and (site=='https://scribeswell.com' or host=='api.scribeswell.com'):raise ValueError('production staging target rejected')
 if not output.is_absolute() or not env_dir.is_absolute() or output.resolve().is_relative_to(ROOT) or env_dir.resolve().is_relative_to(ROOT):raise ValueError('external absolute paths outside repository required')
 subprocess.run(['openssl','x509','-in',str(cert),'-noout','-checkhost',host],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 subprocess.run(['openssl','x509','-in',str(cert),'-noout','-checkend','86400'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 pubcert=subprocess.check_output(['openssl','x509','-in',str(cert),'-pubkey','-noout'])
 pubkey=subprocess.check_output(['openssl','pkey','-in',str(key),'-passin','pass:','-pubout'],stderr=subprocess.DEVNULL)
 if pubcert!=pubkey:raise ValueError('certificate key mismatch')
 manifests=load_manifests();services={}
 for m in manifests:
  image=images.get(m['id'],'')
  if not re.fullmatch(r'[a-zA-Z0-9./:_-]+@sha256:[0-9a-f]{64}',image):raise ValueError('immutable image digest required')
  if not (env_dir/m['env_file']).is_file():raise ValueError('missing runtime environment file')
  services[m['id']]={'image':image,'env_file':[{'path':str(env_dir/m['env_file']),'format':'raw'}],'restart':'unless-stopped','read_only':True,'tmpfs':['/tmp'],'cap_drop':['ALL'],'security_opt':['no-new-privileges:true'],'stop_grace_period':'30s','logging':{'driver':'json-file','options':{'max-size':'10m','max-file':'3'}}}
  services[m['id']]['healthcheck']={'test':['CMD','python','-c',"import urllib.request; urllib.request.urlopen("+repr('http://127.0.0.1:8000'+m['health_path'])+", timeout=3)"],'interval':'15s','timeout':'5s','start_period':'20s','retries':4}
  if m['depends_on']:services[m['id']]['depends_on']={d:{'condition':'service_healthy'} for d in m['depends_on']}
 output.mkdir(parents=True,exist_ok=True,mode=0o750)
 config={'apisix':{'node_listen':9080,'enable_admin':False,'enable_control':False,'ssl':{'enable':True,'listen':[{'port':9443}]}},'deployment':{'role':'data_plane','role_data_plane':{'config_provider':'yaml'}},'nginx_config':{'error_log':'/dev/null','http':{'enable_access_log':True,'access_log':'/dev/stdout','access_log_format':'{"service":"gateway","status":$status,"duration":$request_time,"request_id":"$request_id"}','access_log_format_escape':'json'}}}
 # Error logs are disabled at gateway: nginx upstream diagnostics include raw query URLs.
 (output/'config.yaml').write_text(json.dumps(config,indent=2)+'\n')
 document={'routes':routes(host,site,manifests),'ssls':[{'id':'api','snis':[host],'cert':cert.read_text(),'key':key.read_text()}]}
 secret=output/'apisix.yaml';secret.write_text(json.dumps(document,indent=2)+'\n#END\n');secret.chmod(0o640)
 services['gateway']={'image':APISIX,'restart':'unless-stopped','ports':['443:9443'],'volumes':[str(output/'config.yaml')+':/usr/local/apisix/conf/config.yaml:ro',str(secret)+':/usr/local/apisix/conf/apisix.yaml:ro'],'stop_grace_period':'30s','logging':{'driver':'json-file','options':{'max-size':'10m','max-file':'3'}},'depends_on':{m['id']:{'condition':'service_healthy'} for m in manifests if 'public' in m}}
 (output/'compose.json').write_text(json.dumps({'name':'agriplatform-'+environment,'services':services},indent=2)+'\n')
 return services

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--env-dir',type=Path,required=True);p.add_argument('--images',type=Path,required=True);p.add_argument('--site',required=True);p.add_argument('--api',required=True);p.add_argument('--cert',type=Path,required=True);p.add_argument('--key',type=Path,required=True);p.add_argument('--environment',choices=['staging','production'],required=True);a=p.parse_args()
 try:
  require_compose()
  render(a.output,a.env_dir,json.loads(a.images.read_text()),a.site,a.api,a.cert,a.key,a.environment)
 except Exception:raise SystemExit('Gateway rendering failed; verify inputs and certificate without logging secret contents') from None
