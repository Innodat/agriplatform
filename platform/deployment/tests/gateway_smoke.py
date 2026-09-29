"""Local disposable APISIX integration. No provider credentials/network data calls."""
import hashlib
from unittest.mock import patch
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.request
sys.path.insert(0,str(Path(__file__).parents[1]))
from render_gateway import render, require_compose
from release import load_manifests

def run(*cmd,**kwargs):return subprocess.run(cmd,check=True,**kwargs)
def freeport():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
require_compose()
with tempfile.TemporaryDirectory(prefix='gateway-smoke-') as d:
 root=Path(d);root.chmod(0o755);env=root/'env';env.mkdir();out=root/'rendered'
 cert=root/'cert.pem';key=root/'key.pem';port=freeport()
 run('openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','2','-keyout',str(key),'-out',str(cert),'-subj','/CN=api.scribeswell.test','-addext','subjectAltName=DNS:api.scribeswell.test',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 manifests=load_manifests();names=[m['id'] for m in manifests]
 for name in names:(env/(name+'.env')).write_text('FIXTURE=literal$dollar${UNSET_VALUE}$$\n')
 render(out,env,{name:'fixture@sha256:'+'0'*64 for name in names},'https://scribeswell.test','https://api.scribeswell.test',cert,key,'staging')
 spec=importlib.util.spec_from_file_location('tls_renewal',Path(__file__).parents[1]/'tls/renew.py')
 renewal=importlib.util.module_from_spec(spec);spec.loader.exec_module(renewal)
 def fixture_chown(path,uid,gid):
  # Actual production group/modes, using Docker root only on this owned fixture.
  run('docker','run','--rm','-v',str(root)+':/fixture','python:3.12-slim-bookworm','python','-c','import os,sys;os.chown(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]))','/fixture/'+str(Path(path).relative_to(root)),str(uid),str(gid),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 with patch.object(renewal.os,'chown',fixture_chown):renewal.protect_gateway(out)
 assert (out/'apisix.yaml').stat().st_gid==636 and (out/'apisix.yaml').stat().st_mode & 0o777==0o640
 compose=json.loads((out/'compose.json').read_text());compose['name']='smoke-'+root.name
 fixture=root/'fixture.py';fixture.write_text('''from http.server import BaseHTTPRequestHandler,HTTPServer
import json
class H(BaseHTTPRequestHandler):
 def do_GET(self):
  self.send_response(200);self.end_headers();self.wfile.write(json.dumps({'path':self.path,'auth':self.headers.get('Authorization'),'org':self.headers.get('X-Org-ID')}).encode())
 def log_message(self,*a):pass
HTTPServer(('0.0.0.0',8000),H).serve_forever()
''')
 for name in names:compose['services'][name]={'env_file':compose['services'][name]['env_file'],'image':'python:3.12-slim-bookworm','command':['python','/fixture.py'],'volumes':[str(fixture)+':/fixture.py:ro']}
 gateway=compose['services']['gateway'];gateway['ports']=[f'127.0.0.1:{port}:9443'];gateway.pop('depends_on')
 (out/'compose.json').write_text(json.dumps(compose));cmd=['docker','compose','-f',str(out/'compose.json')]
 def request(path,host='api.scribeswell.test',origin='https://scribeswell.test',method='GET'):
  return subprocess.run(['curl','--silent','--show-error','--cacert',str(cert),'--resolve',f'api.scribeswell.test:{port}:127.0.0.1','--noproxy','*','-D',str(root/'headers'),'-o',str(root/'body'),'-w','%{http_code}','-X',method,'-H','Host: '+host,'-H','Origin: '+origin,'-H','Authorization: Bearer fixture-secret','-H','X-Org-ID: fixture-org',f'https://api.scribeswell.test:{port}'+path],capture_output=True,text=True)
 try:
  run(*cmd,'up','-d')
  network=json.loads(subprocess.check_output(['docker','network','inspect',compose['name']+'_default'],text=True))[0]
  assert network['Driver']=='bridge' and network['EnableIPv6']
  assert {':' in pool['Subnet'] for pool in network['IPAM']['Config']}=={False,True}
  for name in names:
   identity=subprocess.check_output([*cmd,'ps','-q',name],text=True).strip()
   container=json.loads(subprocess.check_output(['docker','inspect',identity],text=True))[0]
   endpoint=container['NetworkSettings']['Networks'][compose['name']+'_default']
   assert endpoint['IPAddress'] and endpoint['GlobalIPv6Address']
   assert not any(container['NetworkSettings']['Ports'].values())
  for _ in range(60):
   response=request('/pts/api/poetry')
   if response.stdout=='200':break
   time.sleep(1)
  assert response.stdout=='200',response.stderr
  literal=subprocess.check_output([*cmd,'exec','-T',names[0],'python','-c',"import os;print(os.environ['FIXTURE'])"],text=True).strip()
  assert literal=='literal$dollar${UNSET_VALUE}$$'
  for manifest in manifests:
   if 'public' in manifest:
    for path in manifest['public']['paths']:
     assert request(manifest['public']['prefix']+path.replace('*','fixture')).stdout=='200'
  for path in ['/pts/api/poetry','/pts/api/poetry/abc','/pts/api/documents/abc','/pts/api/sources','/pts/api/exports','/directory/api/apps','/directory/api/me/apps','/directory/api/me/context','/scribeswell/api/bible/books']:
   assert request(path+'?private=fixture-query').stdout=='200',path
   body=json.loads((root/'body').read_text());assert body['auth']=='Bearer fixture-secret';assert body['org']=='fixture-org';assert body['path'].startswith('/api/')
   assert 'access-control-allow-origin: https://scribeswell.test' in (root/'headers').read_text().lower()
  for path in ['/','/health','/apisix/admin/routes','/v1/check','/pts/docs','/pts/api/poetry-extra','/directory/api/me/secret','/access/v1/check','/content/v1/objects']:
   assert request(path).stdout=='404',path
  assert request('/pts/api/poetry',host='wrong.test').stdout=='404'
  assert request('/pts/api/poetry',method='POST').stdout=='404'
  request('/pts/api/poetry',origin='https://evil.test');assert 'access-control-allow-origin:' not in (root/'headers').read_text().lower()
  assert request('/pts/api/poetry',method='OPTIONS').stdout in ('200','204')
  logs=subprocess.check_output([*cmd,'logs','gateway'],text=True)
  assert 'fixture-secret' not in logs and 'fixture-query' not in logs
  gateway_id=subprocess.check_output([*cmd,'ps','-q','gateway'],text=True).strip()
  run('docker','run','--rm','--network','container:'+gateway_id,'python:3.12-slim-bookworm','python','-c',"import socket; ports=[9180,9090]; results=[]; [(results.append(s.connect_ex(('127.0.0.1',p))),s.close()) for p in ports for s in [socket.socket()]]; assert all(results), results",stdout=subprocess.DEVNULL)
  # Actual production adoption + verifier; only root chown is delegated to a
  # disposable helper to let an unprivileged test runner exercise real gid636.
  from tls_fixture import certificates
  lineage=root/'lineage';lineage.mkdir()
  ca,newkey,leaf,newer,short=certificates(lineage,'api.scribeswell.test')
  trust=root/'trust.pem';trust.write_bytes(cert.read_bytes()+ca.read_bytes())
  state=root/'state';state.mkdir();(state/'current.json').write_text(json.dumps({'sha':'a'*40,'images':{},'compose':str(out/'compose.json'),'evidence':'fixture'}))
  ids={name:subprocess.check_output([*cmd,'ps','-q',name],text=True).strip() for name in names}
  config={'state_dir':str(state),'api':f'https://api.scribeswell.test:{port}','environment':'staging','cert':str(root/'installed.pem'),'key':str(root/'installed.key')}
  with patch.dict(os.environ,{'SSL_CERT_FILE':str(trust)}),patch.object(renewal.os,'chown',fixture_chown):
   assert renewal.install(config,newer,newkey)['outcome']=='activated'
   assert renewal.install(config,newer,newkey)['outcome']=='already_active'
   successful=json.loads((state/'current.json').read_text())
   directory=Path(successful['compose']).parent
   assert (directory/'apisix.yaml').stat().st_gid==636 and (directory/'apisix.yaml').stat().st_mode & 0o777==0o640
   assert directory.stat().st_gid==636 and directory.stat().st_mode & 0o777==0o750
   successful_id=subprocess.check_output([*cmd,'ps','-q','gateway'],text=True).strip()
   changed_chain=root/'changed-chain.pem';changed_chain.write_bytes(newer.read_bytes()+ca.read_bytes())
   assert renewal.install(config,changed_chain,newkey)['outcome']=='activated'
   assert subprocess.check_output([*cmd,'ps','-q','gateway'],text=True).strip()!=successful_id
   previous=json.loads((state/'current.json').read_text())
   prepare=renewal.prepare_gateway
   def broken_candidate(*args):
    candidate=prepare(*args)
    document=json.loads((candidate.parent/'apisix.yaml').read_text().removesuffix('\n#END\n'))
    document['routes']=[] # Inject a real 404 after candidate activation.
    (candidate.parent/'apisix.yaml').write_text(json.dumps(document)+'\n#END\n')
    return candidate
   with patch.object(renewal,'prepare_gateway',broken_candidate):
    try:renewal.install(config,newer,newkey)
    except renewal.Failure as failure:assert failure.code=='api_route_health'
    else:raise AssertionError('broken candidate unexpectedly accepted')
   assert json.loads((state/'current.json').read_text())==previous
   evidence=json.loads(sorted(state.glob('tls-*.json'))[-1].read_text())
   assert evidence['recovery']=='verified' and evidence['previous_compose']==previous['compose']
   assert Path(config['cert']).read_bytes()==changed_chain.read_bytes()
   renewal.verify_served(config['api'],renewal.leaf_fingerprint(changed_chain))
  for name,identity in ids.items():assert subprocess.check_output([*cmd,'ps','-q',name],text=True).strip()==identity
  assert subprocess.check_output([*cmd,'ps','-q','gateway'],text=True).strip()!=gateway_id
  print('Gateway smoke passed: production TLS verifier, gid636/0640, multi-PEM adoption, chain-only rotation, idempotence, failed-candidate recovery, unchanged API containers, allowlist, headers, CORS, private paths, logging, Admin/control closed')

 finally:run(*cmd,'down','--remove-orphans',stdout=subprocess.DEVNULL)
