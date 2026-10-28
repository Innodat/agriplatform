"""Explicit fresh local Story3.1 HTTP qualification; no simulated Auth or SQL.

Consumes this delivery's private synthetic preparation, never provisions or deletes.
The optional --hold phase serves the same actual owners for subsequent browser proof.
"""
import argparse
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import signal
import socket
import ssl
import subprocess
import sys
import time
from uuid import uuid4

import httpx

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'platform/deployment/.local/kdg-story31-20261028'
PYTHON=ROOT/'services/access/.venv/bin/python'

class QualificationInterrupted(RuntimeError):
    def __init__(self,number):
        self.number=number
        super().__init__('supervisor_termination')

def _anon_token(values):
    """Local synthetic gateway key; no executable preparation-script dependency."""
    encode=lambda value:base64.urlsafe_b64encode(json.dumps(value,separators=(',',':')).encode()).decode().rstrip('=')
    now=int(time.time())
    signed=encode({'alg':'HS256','typ':'JWT'})+'.'+encode({
        'role':'anon','aud':'authenticated','iat':now-5,'exp':now+7200,
        'iss':f"http://127.0.0.1:{values['auth_port']}"})
    signature=hmac.new(values['jwt_secret'].encode(),signed.encode(),hashlib.sha256).digest()
    return signed+'.'+base64.urlsafe_b64encode(signature).decode().rstrip('=')

def require(value,code):
    if not value:raise RuntimeError(code)

def load(proof):
    require(proof.parent==BASE and proof.name.startswith('fresh-') and not proof.is_symlink(),'synthetic_proof_invalid')
    path=proof/'private.json';mode=path.stat()
    require(mode.st_uid==os.getuid() and mode.st_mode&0o077==0 and not path.is_symlink(),'private_input_invalid')
    v=json.loads(path.read_text())
    require(v['db_container'].startswith('kdg-story31-') and v['auth_container'].startswith('kdg-story31-'),'synthetic_resources_invalid')
    require(v['kdg_database'].startswith('kdg_schema_') and len(v['kdg_database'])==43,'synthetic_database_invalid')
    return v

def save(path,value):
    path.write_text(json.dumps(value,indent=2,default=str)+'\n');path.chmod(0o600)

def database(v,role,name='postgres'):
    from sqlalchemy import URL
    return URL.create('postgresql+psycopg',username=role,password=v['passwords'][role],host='127.0.0.1',port=v['db_port'],database=name).render_as_string(hide_password=False)

def serve(proof,kind,fd,run):
    v=load(proof);policy=json.loads((run/'policy.json').read_text())
    if kind=='auth':
        from fastapi import FastAPI,Request
        from fastapi.responses import Response
        app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
        @app.api_route('/auth/v1/{tail:path}',methods=['GET','POST','PUT','DELETE'])
        async def gateway(tail:str,request:Request):
            # Real GoTrue gateway only; no token verifier or generated decision.
            headers={k:val for k,val in request.headers.items() if k.lower() in ('authorization','apikey','content-type','x-client-info')}
            async with httpx.AsyncClient(trust_env=False,timeout=5,follow_redirects=False) as client:
                r=await client.request(request.method,f"http://127.0.0.1:{v['auth_port']}/"+tail,params=request.query_params,headers=headers,content=await request.body())
            return Response(r.content,status_code=r.status_code,headers={'Content-Type':r.headers.get('content-type','application/json'),'Cache-Control':'private, no-store','Access-Control-Allow-Origin':request.headers.get('origin','http://127.0.0.1:5177'),'Access-Control-Allow-Headers':'authorization,apikey,content-type,x-client-info','Access-Control-Allow-Methods':'GET,POST,PUT,DELETE,OPTIONS'})
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(CORSMiddleware,allow_origins=['http://127.0.0.1:5177'],allow_methods=['GET','POST','PUT','DELETE','OPTIONS'],allow_headers=['authorization','apikey','content-type','x-client-info'])
    elif kind=='access':
        from psycopg.conninfo import make_conninfo
        os.environ.update({'ACCESS_DATABASE_URL':database(v,'access_runtime'),'SUPABASE_URL':policy['auth_url'],'SUPABASE_ANON_KEY':policy['anon_key'],'KDG_SERVICE_KEY':policy['service_key'],'KDG_ORG_ID':v['org_id'],'KDG_ACTOR_DISPLAY_ORG_ID':v['org_id'],'KDG_ACTOR_DISPLAY_SERVICE_KEY':policy['display_key'],'IDENTITY_ACTOR_DISPLAY_DATABASE_URL':make_conninfo(host='127.0.0.1',port=v['db_port'],dbname='postgres',user='identity_actor_display_runtime',password=v['passwords']['identity_actor_display_runtime'])})
        sys.path.insert(0,str(ROOT/'services/access'))
        from main import app
    else:
        sys.path[:0]=[str(ROOT/'apps/kdg-capture/api'),str(ROOT/'apps/kdg-capture/write-candidate')]
        from runtime import create_app
        trust=ssl.create_default_context(cafile=run/'tls-cert.pem')
        factory=lambda:httpx.AsyncHTTPTransport(verify=trust,trust_env=False)
        app=create_app({'KDG_ORG_ID':v['org_id'],'KDG_ACCESS_URL':policy['owner_url'],'KDG_SERVICE_KEY':policy['service_key'],'KDG_ADMIN_READ_DATABASE_URL':database(v,'kdg_capture_runtime',v['kdg_database']),'KDG_IDENTITY_URL':policy['owner_url'],'KDG_ACTOR_DISPLAY_SERVICE_KEY':policy['display_key']},transport=factory(),identity_transport=factory())
        # Existing own-create owner is mounted only by this qualification host;
        # this does not activate administrative writes or a product create route.
        from create_http import create_candidate
        producer=create_candidate(org_id=v['org_id'],access_url=policy['owner_url'],service_key=policy['service_key'],database_url=database(v,'kdg_capture_runtime',v['kdg_database']),transport=factory())
        app.include_router(producer.router)
    import uvicorn
    channel=socket.socket(fileno=fd)
    require(channel.getsockname()[0]=='127.0.0.1','listener_not_loopback')
    tls={'ssl_certfile':str(run/'tls-cert.pem'),'ssl_keyfile':str(run/'tls-key.pem')} if kind=='access' else {}
    server=uvicorn.Server(uvicorn.Config(app,access_log=False,log_level='critical',timeout_graceful_shutdown=5,**tls))
    signal.signal(signal.SIGTERM,lambda signum,frame:None)
    server.run(sockets=[channel]);require(server.started,'server_not_started')

def source_binding(run):
    paths=[Path(__file__),*list((ROOT/'services/access').glob('*.py')),*list((ROOT/'apps/kdg-capture/api').glob('*.py')),*list((ROOT/'apps/kdg-capture/write-candidate').glob('*.py'))]
    paths += list((ROOT/'services/access/migrations').glob('*.py'))+list((ROOT/'services/access/migrations/versions').glob('*.py'))
    paths += list((ROOT/'services/access/identity-migrations').glob('*.py'))+list((ROOT/'services/access/identity-migrations/versions').glob('*.py'))
    # Every path is selected from owner source directories, never migration tests.
    result={}
    for path in paths:
        name=path.relative_to(ROOT).as_posix();data=path.read_bytes();result[name]=hashlib.sha256(data).hexdigest()
        target=run/'executed-sources'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    save(run/'source-binding.json',result);return result

def execute(proof,hold=False):
    os.umask(0o077);v=load(proof)
    for marker in ['resource-ready.json','owners-prepared.json','auth-identity-ready.json','access-seed-ready.json','kdg-parents-ready.json']:require((proof/marker).is_file(),'preparation_incomplete')
    run=proof/('http-'+uuid4().hex);run.mkdir(mode=0o700)
    from secrets import token_urlsafe
    sockets={};processes=[];checks=[];ok=False
    interruption=None;interruption_phase=None;phase='starting';stopping=False;starting_child=False
    previous_handlers={number:signal.getsignal(number) for number in (signal.SIGTERM,signal.SIGINT)}
    def terminate(number,frame):
        nonlocal interruption,interruption_phase
        if interruption is not None:return
        interruption=number;interruption_phase=phase
        # A first signal during shutdown records interruption without abandoning
        # another owned child. Further signals cannot interrupt bounded cleanup.
        if not stopping and not starting_child:raise QualificationInterrupted(number)
    for kind in ('auth','access','kdg'):
        c=socket.socket();c.bind(('127.0.0.1',0));c.listen(128);sockets[kind]=c
    policy={'auth_url':f"http://127.0.0.1:{sockets['auth'].getsockname()[1]}",'owner_url':f"https://127.0.0.1:{sockets['access'].getsockname()[1]}",'api_url':f"http://127.0.0.1:{sockets['kdg'].getsockname()[1]}",'anon_key':_anon_token(v),'service_key':token_urlsafe(36),'display_key':token_urlsafe(36)}
    save(run/'policy.json',policy)
    result=subprocess.run(['/usr/bin/openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(run/'tls-key.pem'),'-out',str(run/'tls-cert.pem'),'-days','2','-subj','/CN=localhost','-addext','subjectAltName=IP:127.0.0.1,DNS:localhost'],capture_output=True,timeout=15)
    require(result.returncode==0,'certificate_generation_failed');sources=source_binding(run)
    try:
        for number in previous_handlers:signal.signal(number,terminate)
        for kind,c in sockets.items():
            # Popen can create the OS child before returning its handle. Record
            # signals across creation/registration so cleanup cannot miss it.
            starting_child=True
            try:
                with (run/(kind+'.log')).open('xb') as log:
                    p=subprocess.Popen([str(PYTHON),'-I','-B',str(Path(__file__).resolve()),'--proof',str(proof),'--serve',kind,'--fd',str(c.fileno()),'--run',str(run)],cwd=ROOT,env={'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8'},pass_fds=(c.fileno(),),stdout=log,stderr=subprocess.STDOUT)
                processes.append((kind,p))
            finally:
                starting_child=False
            c.close()
            if interruption is not None:raise QualificationInterrupted(interruption)
        phase='http_checks'
        accounts=json.loads((proof/'accounts.json').read_text());data=json.loads((proof/'capture-inputs.json').read_text())
        with httpx.Client(trust_env=False,timeout=12,verify=ssl.create_default_context(cafile=run/'tls-cert.pem')) as client:
            deadline=time.monotonic()+15
            while True:
                require(all(p.poll() is None for _,p in processes),'server_exited')
                try:
                    r=client.get(policy['owner_url']+'/health')
                    k=client.get(policy['api_url']+'/api/v1/context')
                    if r.status_code==200 and k.status_code==401:break
                except httpx.HTTPError:pass
                require(time.monotonic()<deadline,'server_readiness_timeout');time.sleep(.05)
            def request(name,path,expected=200,method='GET',body=None):
                r=client.request(method,policy['api_url']+path,headers={'Authorization':'Bearer '+accounts[name]['session']['access_token']},json=body)
                require(r.status_code==expected,'http_'+name+'_'+str(r.status_code)+'_expected_'+str(expected))
                require(r.headers.get('cache-control')=='private, no-store','response_not_private')
                return r.json()
            history='/api/v1/admin/captures?from_date=2026-10-01&to_date=2026-10-31&limit=1'
            before=request('admin',history);checks.append('current-all-read-before-producer')
            require(request('capturer','/api/v1/context')['account_id']==accounts['capturer']['id'],'previous-own-context-consumer-broken');checks.append('previous-own-context-consumer')
            if not before['items']:checks.append('empty-history-before-first-sync')
            for name in ['capturer','other']:
                request(name,'/api/v1/captures',method='POST',body=data['commands'][name]);checks.append(name+'-real-http-create')
            seen=[];page=request('admin',history)
            while True:
                require(len(page['items'])<=1,'page_limit');seen.extend(row['capture_id'] for row in page['items'])
                if not page['next_cursor']:break
                from urllib.parse import quote
                page=request('admin',history+'&cursor='+quote(page['next_cursor'],safe=''))
            require(set(seen)=={x['capture_id'] for x in data['commands'].values()},'synchronized_history_incomplete');checks.append('two-owner-history-keyset-pages')
            capture=data['commands']['capturer']['capture_id'];path='/api/v1/admin/captures/'+capture
            detail=request('admin',path);require(detail['definition']==data['definition'] and detail['owner_account_id']==accounts['capturer']['id'],'original_definition_owner_changed')
            audit=request('admin',path+'/audit-details?limit=1')
            require(audit['audit']['owner_actor_id']==accounts['capturer']['actor_id'],'audit_owner_changed')
            require(audit['actor_display']['status']=='loaded','native_names_unavailable')
            require(audit['actor_display']['labels']==[{'actor_id':accounts['capturer']['actor_id'],'status':'resolved','display_name':'Synthetic Capturer'}],'native_selected_name_mismatch');checks.append('native-selected-retained-name-original-definition')
            for name in ['capturer','member','platform','foreign','nomember']:
                request(name,history,403);request(name,path,403);request(name,path+'/audit-details',403)
            checks.append('real-auth-current-role-matrix-denied-without-own-fallback')
            request('admin',path+'?org_id='+v['foreign_org_id'],422);checks.append('client-scope-selector-denied')
            require(request('admin',path+'/audit-details?limit=1')==audit,'retry-created-fictitious-audit');checks.append('read-retry-preserves-audit')
        save(run/'ready.json',{'api_url':policy['api_url'],'auth_url':policy['auth_url'],'owner_url':policy['owner_url'],'process_ids':{name:p.pid for name,p in processes},'actual_gotrue':True,'actual_native_owners':True})
        if hold:
            phase='hold'
            print(json.dumps({'ready':str(run/'ready.json')}),flush=True)
            while True:time.sleep(1)
        ok=True
    except BaseException as error:
        save(run/'failure.json',{'type':type(error).__name__,'safe_code':str(error) if type(error) is RuntimeError or isinstance(error,QualificationInterrupted) else None,
            'signal':error.number if isinstance(error,QualificationInterrupted) else None})
        raise
    finally:
        stopping=True;phase='shutdown'
        try:
            stopped=[]
            for name,p in reversed(processes):
                try:
                    if p.poll() is None:p.send_signal(signal.SIGTERM)
                except ProcessLookupError:pass
                forced=False
                try:code=p.wait(timeout=10)
                except subprocess.TimeoutExpired:p.kill();code=p.wait(timeout=3);forced=True
                stopped.append({'name':name,'exit_code':code,'forced':forced})
            for channel in sockets.values():channel.close()
            unchanged=all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest for name,digest in sources.items())
            if interruption is not None and not (run/'failure.json').exists():
                save(run/'failure.json',{'type':'QualificationInterrupted','safe_code':'supervisor_termination','signal':interruption})
            save(run/'result.json',{'passed':ok and interruption is None and unchanged and all(x['exit_code']==0 and not x['forced'] for x in stopped),'checks':checks,
                'interruption_signal':interruption,'interruption_phase':interruption_phase,'normal_owned_server_stop':stopped,'sources_unchanged':unchanged,'limits':['synthetic accounts on real local GoTrue; no external provider qualification','no physical device or release evidence'],'source_binding':str(run/'source-binding.json')})
        finally:
            for number,previous in previous_handlers.items():signal.signal(number,previous)
    if interruption is not None:raise QualificationInterrupted(interruption)
    require(ok and unchanged and all(x['exit_code']==0 and not x['forced'] for x in stopped),'qualification_or_shutdown_incomplete')
    print(json.dumps({'passed':True,'run':str(run),'checks':len(checks)}))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--proof',type=Path,required=True);parser.add_argument('--serve',choices=['auth','access','kdg']);parser.add_argument('--fd',type=int);parser.add_argument('--run',type=Path);parser.add_argument('--hold',action='store_true');args=parser.parse_args()
    try:
        if args.serve:serve(args.proof,args.serve,args.fd,args.run)
        else:execute(args.proof,args.hold)
    except QualificationInterrupted as error:
        print('story31_http_interrupted',file=sys.stderr);return 128+error.number
    except Exception as error:
        print('story31_http_failed_'+type(error).__name__,file=sys.stderr);return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
