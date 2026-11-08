"""Isolated same-site TLS/APISIX and genuine provider browser composition.

The generator owns route policy. Only fixture process upstream addresses/listen ports
are substituted here; no DNS, host trust store or deployed certificate is modified.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import httpx
from apps.pts.tests.integration_fixture import ROOT,private,module

NODE=ROOT/'platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node'


def http_listener_port(tls_port):
    # The unused HTTP listener cannot assume tls_port+1 is available: real
    # qualification observed an ephemeral-client collision on that adjacent port.
    for _ in range(10):
        with socket.socket() as selected:
            selected.bind(('127.0.0.1',0));port=selected.getsockname()[1]
        if port!=tls_port:return port
    raise AssertionError('fresh_gateway_HTTP_port_unavailable')

def viewer_probe(f):
    from apps.pts.tests.native_acceptance import synthetic_pdf
    (f.out/'synthetic.pdf').write_bytes(synthetic_pdf())
    f.command(['xvfb-run','-a','--server-args=-screen 0 1440x1000x24',NODE,ROOT/'apps/pts/tests/viewer_probe.cjs',f.out],'viewer-probe',env={**os.environ,'PATH':str(NODE.parent)+':'+os.environ.get('PATH','')})
    f.checks.append('headed-native-viewer-header-policy-probe-only')


def launch_gateway(f,gateway,document,port):
    import render_gateway
    apisix=gateway/'apisix.yaml';apisix.write_text(json.dumps(document)+'\n#END\n')
    http_port=http_listener_port(port)
    # APISIX3.18's configuration supports ip/port objects for both listeners:
    # https://github.com/apache/apisix/blob/3.18.0/conf/config.yaml.example
    settings={'apisix':{'node_listen':[{'ip':'127.0.0.1','port':http_port}],'enable_ipv6':False,'enable_admin':False,'enable_control':False,'ssl':{'enable':True,'listen':[{'ip':'127.0.0.1','port':port}]}},'deployment':{'role':'data_plane','role_data_plane':{'config_provider':'yaml'}},'nginx_config':{'error_log':'/dev/null','http':{'enable_access_log':False,'send_timeout':'60s'}}}
    (gateway/'config.yaml').write_text(json.dumps(settings))
    for path in (gateway/'config.yaml',apisix):path.chmod(0o640)
    container='pts-adopt-gateway-'+f.nonce[:16]
    # Separate creation from startup so every created container has custody even
    # when startup fails (including logging-driver and config failures).
    identity=f.docker('create','--name',container,'--label','agriplatform.pts-adoption='+f.nonce,'--group-add',os.getgid(),'--network','host','--restart','no','--log-driver','local','--log-opt','max-size=1m','--log-opt','max-file=2','-v',str(gateway/'config.yaml')+':/usr/local/apisix/conf/config.yaml:ro','-v',str(apisix)+':/usr/local/apisix/conf/apisix.yaml:ro',render_gateway.APISIX)
    f.containers.append(container);private(f.out/'gateway-container-custody.json',{'container_id':identity,'name':container,'phase':'created',
        'listeners':{'http':{'ip':'127.0.0.1','port':http_port},'https':{'ip':'127.0.0.1','port':port}}})
    f.docker('start',container)
    return container


def gateway_startup(f):
    """Cheap fresh TLS/config startup RED/GREEN; no owner/browser claim."""
    f.guard();sys.path.insert(0,str(ROOT/'platform/deployment'));import render_gateway
    with socket.socket() as selected:selected.bind(('127.0.0.1',0));port=selected.getsockname()[1]
    gateway=f.out/'gateway';gateway.mkdir();cert=gateway/'cert.pem';key=gateway/'key.pem'
    f.command(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','2','-keyout',key,'-out',cert,'-subj','/CN=pts.fixture.test','-addext','subjectAltName=DNS:pts.fixture.test,DNS:files.pts.fixture.test'],'tls-certificate')
    site='https://pts.fixture.test:'+str(port);files='https://files.pts.fixture.test:'+str(port)
    manifest=json.loads((ROOT/'apps/pts/deployment/manifest.json').read_text());configuration={'pts':{'origin':files,'frontend_origin':site,'cert':str(cert),'key':str(key)}}
    routes=render_gateway.routes('pts.fixture.test',site,[manifest],file_origins=configuration)
    for route in routes:route['upstream']['nodes']={'127.0.0.1:9':1}
    document={'routes':routes,'ssls':[{'id':'fixture','snis':['pts.fixture.test','files.pts.fixture.test'],'cert':cert.read_text(),'key':key.read_text()}]}
    container=launch_gateway(f,gateway,document,port)
    for _ in range(100):
        response=subprocess.run(['curl','--silent','--noproxy','*','--cacert',str(cert),'--resolve',f'files.pts.fixture.test:{port}:127.0.0.1','-o','/dev/null','-w','%{http_code}',files+'/api/files/11111111-1111-4111-8111-111111111111'],capture_output=True)
        if response.stdout==b'502':break
        time.sleep(.1)
    else:
        f.command(['docker','logs',container],'gateway-startup-diagnostics');raise AssertionError('generated_TLS_startup_unavailable')
    private(f.out/'gateway-startup-proof.json',{'tls_verified':True,'generated_route_status':502,'intentionally_unavailable_upstream':True,'owner_and_browser_claim':False})
    f.checks.append('fresh-generated-TLS-gateway-startup-only')


def qualify(f):
    f.guard();sys.path.insert(0,str(ROOT/'platform/deployment'))
    import render_gateway
    # Fresh process consumes actual Access discovery with a separate caller key.
    directory=f.start_owner('services/app-directory',{'ACCESS_URL':f.services['access']['origin'],'DIRECTORY_SERVICE_KEY':f.directory_key,'APP_URL_PTS':f.frontend_origin,'APP_URL_SCRIBESWELL':f.frontend_origin+'/scribeswell','CORS_ORIGINS':json.dumps([f.frontend_origin])},'directory',python=ROOT/'services/app-directory/.venv/bin/python')
    f.services['directory']=directory
    with httpx.Client(timeout=10,trust_env=False) as client:
        response=client.get(directory['origin']+'/api/v2/me/apps',headers={'Authorization':'Bearer '+f.subjects[0]['access_token']})
        assert response.status_code==200 and response.json()['protected_access_status']=='complete' and {row['id'] for row in response.json()['apps']}=={'pts','scribeswell'}
    f.checks.append('actual-Directory-account-discovery-with-zero-memberships')
    gateway=f.out/'gateway';gateway.mkdir()
    cert=gateway/'cert.pem';key=gateway/'key.pem'
    f.command(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','2','-keyout',key,'-out',cert,'-subj','/CN=pts.fixture.test','-addext','subjectAltName=DNS:pts.fixture.test,DNS:files.pts.fixture.test,DNS:api.pts.fixture.test'],'tls-certificate')
    pub=subprocess.check_output(['openssl','x509','-in',str(cert),'-pubkey','-noout'],stderr=subprocess.DEVNULL)
    der=subprocess.run(['openssl','pkey','-pubin','-outform','DER'],input=pub,capture_output=True,check=True).stdout
    spki=base64.b64encode(hashlib.sha256(der).digest()).decode()
    # Freeze an actual production UI build with this isolated provider/owner ingress.
    ui=f.out/'web';environment={**os.environ,'PATH':str(NODE.parent)+':'+os.environ.get('PATH',''),'VITE_SUPABASE_URL':f.frontend_origin,'VITE_SUPABASE_ANON_KEY':'synthetic-public-key','VITE_PTS_API_URL':f.frontend_origin+'/pts','VITE_APP_DIRECTORY_URL':f.frontend_origin+'/directory','VITE_PTS_FILE_ORIGIN':f.file_origin,'VITE_MICROSOFT_SIGN_IN_ENABLED':'false'}
    f.command([NODE,ROOT/'node_modules/vite/bin/vite.js','build',ROOT/'apps/pts/web','--outDir',ui],'actual-web-build',env=environment)
    if getattr(f,'cleanup_matrix',False):(ui/'cleanup-probe.html').write_text('<!doctype html><title>Disposable cleanup observation</title>')
    static=f.out/'static_ui.py';static.write_text('from fastapi import FastAPI\nfrom fastapi.staticfiles import StaticFiles\napp=FastAPI(docs_url=None,openapi_url=None)\n@app.get("/health")\ndef health():return {"status":"running"}\napp.mount("/",StaticFiles(directory='+repr(str(ui))+',html=True))\n')
    web=f.start_owner(f.out.relative_to(ROOT),{},'static-ui','static_ui:app')
    manifest=json.loads((ROOT/'apps/pts/deployment/manifest.json').read_text())
    config={'pts':{'origin':f.file_origin,'frontend_origin':f.frontend_origin,'cert':str(cert),'key':str(key)}}
    routes=render_gateway.routes('pts.fixture.test',f.frontend_origin,[manifest],file_origins=config)
    for route in routes:route['upstream']['nodes']={'127.0.0.1:'+str(f.services['pts']['port']):1}
    if getattr(f,'jwt_expiry_seconds',3600)==60:
        control=f.out/'response-gate';control.mkdir()
        gate=f.start_owner('.',{'PTS_FIXTURE_GATE_UPSTREAM':f.services['pts']['origin'],'PTS_FIXTURE_GATE_CONTROL':str(control)},'response-gate','apps.pts.tests.response_gate:app')
        for route in routes:
            if route['id']=='pts-file-session':route['upstream']['nodes']={'127.0.0.1:'+str(gate['port']):1}
    def proxy(identity,paths,upstream,prefix=None,methods=None):
        plugins={}
        if prefix:plugins['proxy-rewrite']={'regex_uri':['^'+prefix+'/(.*)','/$1']}
        return {'id':identity,'host':'pts.fixture.test','uris':paths,'methods':methods or ['GET','POST','PUT','OPTIONS'],'vars':[['scheme','==','https']],'plugins':plugins,'upstream':{'type':'roundrobin','nodes':{'127.0.0.1:'+str(upstream['port']):1},'timeout':{'connect':5,'send':30,'read':30}}}
    routes.extend([proxy('fixture-provider',['/auth/v1/*'],f.services['auth_proxy']),proxy('fixture-directory',['/directory/*'],directory,'/directory'),proxy('fixture-ui',['/*'],web,methods=['GET'])])
    port=httpx.URL(f.frontend_origin).port
    # Runtime source-process address adapters are explicit in custody; routes,
    # methods, CORS, privacy, buffering and timeout policy remain generated.
    document={'routes':routes,'ssls':[{'id':'fixture-tls','snis':['pts.fixture.test','files.pts.fixture.test','api.pts.fixture.test'],'cert':cert.read_text(),'key':key.read_text()}]}
    container=launch_gateway(f,gateway,document,port);f.gateway_container=container;apisix=gateway/'apisix.yaml'
    # curl explicitly trusts only the new fixture certificate and binds DNS/SNI.
    for _ in range(100):
        result=subprocess.run(['curl','--silent','--noproxy','*','--cacert',str(cert),'--resolve',f'pts.fixture.test:{port}:127.0.0.1','-o','/dev/null','-w','%{http_code}',f.frontend_origin+'/'],capture_output=True)
        if result.stdout==b'200':break
        time.sleep(.1)
    else:
        f.command(['docker','logs',container],'gateway-startup-diagnostics')
        raise AssertionError('generated_TLS_ingress_unavailable')
    recovery_command=None
    if getattr(f,'cleanup_matrix',False):
        from apps.pts.tests.integration_fixture import mint
        recovery_input=f.out/'recovery-input-private.json';recovery_output=f.out/'recovery-session-private.json'
        private(recovery_input,{'origin':f.frame['origin'],'admin':mint(f.frame['secret'],f.frame['issuer'],aud='authenticated',role='service_role'),
            'email':f.subjects[0]['email'],'account':f.subjects[0]['account']})
        recovery_command=[str(sys.executable),'-B','-m','apps.pts.tests.cleanup_acceptance','--recovery-input',str(recovery_input),'--recovery-output',str(recovery_output)]
    private(f.out/'tls-browser-input-private.json',{'frontend':f.frontend_origin,'files':f.file_origin,'spki':spki,'subjects':f.subjects,'document':f.document,'pdf_sha256':hashlib.sha256(f.pdf).hexdigest(),'output':str(f.out),'session_races':getattr(f,'jwt_expiry_seconds',3600)==60,'gate_control':str(f.out/'response-gate'),'provider_container':f.frame['container'],'provider_jwt_expiry_seconds':f.frame['jwt_expiry_seconds'],'recovery_command':recovery_command})
    from apps.pts.tests.native_acceptance import provider_outage
    provider_outage(f)
    browser='native_cleanup_browser.cjs' if getattr(f,'cleanup_matrix',False) else 'native_browser.cjs'
    f.command(['xvfb-run','-a','--server-args=-screen 0 1440x1000x24',NODE,ROOT/'apps/pts/tests'/browser,f.out/'tls-browser-input-private.json'],'native-browser',env={**os.environ,'PATH':str(NODE.parent)+':'+os.environ.get('PATH','')},timeout=390 if getattr(f,'cleanup_matrix',False) else 300)
    private(f.out/'gateway-binding.json',{'image_id':json.loads(f.docker('inspect',container))[0]['Image'],'renderer_sha256':hashlib.sha256((ROOT/'platform/deployment/render_gateway.py').read_bytes()).hexdigest(),'routes_sha256':hashlib.sha256(apisix.read_bytes()).hexdigest(),'ui_files':{str(p.relative_to(ui)):hashlib.sha256(p.read_bytes()).hexdigest() for p in ui.rglob('*') if p.is_file()},'pts_runtime_mode':'frozen_image' if hasattr(f,'runtime_image') else 'source_process','access_runtime_mode':'frozen_image' if getattr(f,'access_image',None) else 'source_process','boundary':'Actual APISIX and production UI build; PtS '+('frozen packaged image' if hasattr(f,'runtime_image') else 'source process')+'; Access/Identity '+('frozen packaged image' if getattr(f,'access_image',None) else 'source process')+'; Content and Directory source processes, with explicit loopback address adapters. Isolated fixture TLS trust only; no hosted DNS/certificate claim.'})
    f.checks.append('actual-same-site-TLS-generated-private-ingress-and-native-browser-provider-journeys')
    if getattr(f,'resource_matrix',False):
        from apps.pts.tests.resource_acceptance import qualify as resources
        resources(f)
    if getattr(f,'resource_probe',False):
        from apps.pts.tests.resource_acceptance import probe
        probe(f)
