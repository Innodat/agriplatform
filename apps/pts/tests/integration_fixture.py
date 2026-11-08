"""Fresh guarded provider/Storage/owner composition for PtS qualification.

Nothing starts on import. Credentials stay in the new private output; retained source
and closed proofs are read-only. Helpers are test infrastructure, not runtime imports.
"""
import argparse
import base64
from datetime import datetime,timezone
import hashlib
import hmac
import importlib.util
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time
from types import SimpleNamespace
from uuid import uuid4
import httpx
import psycopg
from psycopg import sql
from sqlalchemy import create_engine,text
from sqlalchemy.engine import make_url

ROOT=Path(__file__).resolve().parents[3]
RUN='88a737dd-ad7b-429a-a83c-5d103716d659'
STORAGE='public.ecr.aws/supabase/storage-api@sha256:528ec49c3c32561908b07ee91bced7f8456f3b688164e341eaa422441767a0bd'


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value);return value

def private(path,value):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as out:json.dump(value,out,indent=2,default=str);out.write('\n')

def raw(url):return url.replace('postgresql+psycopg:','postgresql:')

def mint(secret,issuer,**claims):
    encode=lambda value:base64.urlsafe_b64encode(json.dumps(value,separators=(',',':')).encode()).rstrip(b'=').decode()
    data=encode({'alg':'HS256','typ':'JWT'})+'.'+encode({'iss':issuer,'iat':int(time.time()),'exp':int(time.time())+3600,**claims})
    return data+'.'+base64.urlsafe_b64encode(hmac.digest(secret.encode(),data.encode(),'sha256')).rstrip(b'=').decode()


class Fixture:
    def __init__(self,output):
        os.umask(0o077);self.out=Path(output).resolve()
        if not self.out.is_relative_to(ROOT/'platform/deployment/.local/e1-pts-adoption') or self.out.exists():raise ValueError('new_private_output_required')
        self.out.mkdir(parents=True,mode=0o700);self.nonce=uuid4().hex;self.containers=[];self.processes=[];self.checks=[]
        sys.path[:0]=[str(ROOT/'services/access/tests'),str(ROOT/'services/access'),str(ROOT/'services/access/identity-migrations'),str(ROOT/'platform/builder-cli/examples/owner-fixtures')]
        self.session_owner=module('_pts_session_fixture',ROOT/'services/access/tests/qualify_current_session.py')
        self.guard=self.session_owner.guard;self.guard()

    def command(self,argv,label,expected=0,env=None,timeout=180):
        result=subprocess.run([str(v) for v in argv],cwd=ROOT,env=env,capture_output=True,timeout=timeout)
        # Tool output may contain provider/SQL credentials; it never enters chat/public evidence.
        for channel in ('stdout','stderr'):
            target=self.out/(label+'.'+channel);target.write_bytes(getattr(result,channel));target.chmod(0o600)
        private(self.out/(label+'.json'),{'exit_code':result.returncode,'stdout_sha256':hashlib.sha256(result.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(result.stderr).hexdigest()})
        if result.returncode!=expected:raise AssertionError(label+'_failed')
        return result

    def docker(self,*argv):
        return subprocess.check_output(['docker',*[str(v) for v in argv]],stderr=subprocess.DEVNULL,text=True,timeout=30).strip()

    def wait(self,origin,path='/health',headers=None,startup_seconds=10):
        deadline=time.monotonic()+startup_seconds
        with httpx.Client(timeout=1,trust_env=False) as client:
            while time.monotonic()<deadline:
                try:
                    if client.get(origin+path,headers=headers).status_code==200:return
                except httpx.HTTPError:pass
                time.sleep(.1)
        raise AssertionError('fresh_service_health_failed')

    def provider(self):
        output=ROOT/'platform/deployment/.local/e1-current-session'/('pts-adopt-'+self.nonce)
        self.provider_out=output
        args=SimpleNamespace(output=str(output),auth_baseline=str(ROOT/'platform/deployment/.local/e1-session-coordinator/00_init_auth_schema.up.sql'),image=None,jwt_expiry_seconds=getattr(self,'jwt_expiry_seconds',3600))
        self.provider_out,self.frame,self.session_roles=self.session_owner.prepare(args)
        self.containers.append(self.frame['container']);self.wait(self.frame['origin'])
        with psycopg.connect(raw(self.frame['urls']['admin']),autocommit=True) as connection:
            connection.execute(sql.SQL('REVOKE CREATE ON DATABASE {} FROM {}').format(sql.Identifier(self.frame['database']),sql.Identifier(self.frame['provider_role'])))
            for name in ('deleted_at','email_confirmed_at','banned_until','is_anonymous'):
                connection.execute(sql.SQL('UPDATE auth.users SET {}={}').format(sql.Identifier(name),sql.Identifier('fixture_legacy_'+name)))
            grants=json.loads((self.provider_out/'legacy-auth-column-grants.json').read_text())
            for name,recipient,privilege,grantable in grants:
                connection.execute(sql.SQL('GRANT {}({}) ON auth.users TO {}'+(' WITH GRANT OPTION' if grantable else '')).format(sql.SQL(privilege),sql.Identifier(name),sql.Identifier(recipient)))
            for name in ('deleted_at','email_confirmed_at','banned_until','is_anonymous'):
                connection.execute(sql.SQL('ALTER TABLE auth.users DROP COLUMN {}').format(sql.Identifier('fixture_legacy_'+name)))
            connection.execute((ROOT/'services/access/tools/prepare_identity_session_auth.sql').read_text())
        from services.access.tests.prepare_file_cleanup_reference import prepare
        prepare(self.frame['urls']['identity'],self.out/'identity30-reference-rollback.json',regenerate=getattr(self,'refresh_cleanup_reference',False))
        session_url=make_url(self.frame['urls']['admin']).set(username=self.session_owner.RUNTIME,password=self.session_roles[self.session_owner.RUNTIME]).render_as_string(hide_password=False)
        proof_environment={'PATH':'/usr/bin:/bin','PYTHONDONTWRITEBYTECODE':'1','IDENTITY_CURRENT_SESSION_DATABASE_URL':raw(session_url)}
        self.command([sys.executable,'-B',ROOT/'services/access/file_cleanup_preflight.py'],'identity30-prerequisite-missing-RED',expected=1,env=proof_environment)
        self.session_owner.upgrade(self.frame['urls']['identity'],self.provider_out,'pts-identity30-upgrade')
        self.session_owner.upgrade(self.frame['urls']['identity'],self.provider_out,'pts-identity30-repeat')
        self.command([sys.executable,'-B',ROOT/'services/access/file_cleanup_preflight.py'],'identity30-prerequisite-GREEN',env=proof_environment)
        self.subjects=[];admin_token=mint(self.frame['secret'],self.frame['issuer'],aud='authenticated',role='service_role')
        with httpx.Client(timeout=5,trust_env=False) as client:
            granted_count=getattr(self,'subject_count',2)
            for index in range(granted_count+1):
                email='pts-'+self.nonce+'-'+str(index)+'@example.invalid';password=secrets.token_urlsafe(32)
                created=client.post(self.frame['origin']+'/admin/users',headers={'Authorization':'Bearer '+admin_token},json={'email':email,'password':password,'email_confirm':True})
                assert created.status_code==200,'provider_create_failed'
                signed=client.post(self.frame['origin']+'/token?grant_type=password',json={'email':email,'password':password})
                assert signed.status_code==200,'provider_signin_failed'
                self.subjects.append({'account':signed.json()['user']['id'],'email':email,'password':password,'absent_grants':index==granted_count,**signed.json()})
        private(self.out/'provider-subjects-private.json',self.subjects)
        self.checks.append('fresh-genuine-provider-and-Identity30-same-clone')
        private(self.out/'provider-binding-private.json',self.frame)
        return self.frame

    def accounts(self):
        from dataclasses import asdict
        import identity_operator,access_operator
        with psycopg.connect(raw(self.frame['urls']['admin'])) as connection:
            executor=connection.execute("SELECT executor_actor_id FROM identity.operator_principals WHERE database_login='identity_operator'").fetchone()[0]
            access_executor=connection.execute("SELECT executor_actor_id FROM access.operator_principals WHERE database_login='access_operator'").fetchone()[0]
            assert connection.execute('SELECT count(*) FROM identity.org_member WHERE user_id=ANY(%s::uuid[])',([subject['account'] for subject in self.subjects],)).fetchone()[0]==0
        for index,subject in enumerate(self.subjects):
            with psycopg.connect(raw(self.frame['urls']['identity'])) as connection:
                connection.execute("INSERT INTO identity.operator_authorities(id,database_login,command,scope_kind,target_account_id,enabled,created_by,updated_by) VALUES(%s,'identity_operator','account_actor.ensure','platform',%s,true,%s,%s)",(uuid4(),subject['account'],executor,executor))
            envelope=dict(schema_version=1,operation_id=str(uuid4()),command='account_actor.ensure',scope={'kind':'platform'},reason_code='synthetic_fixture',evidence_ref='fixture:pts-adoption:'+self.nonce,
                payload=dict(account_id=subject['account'],actor_id=str(uuid4()),display_name='Synthetic PtS reader '+str(index),expected_absent=True))
            db=create_engine(self.frame['urls']['identity_operator'],hide_parameters=True)
            try:
                with db.connect() as connection:receipt=identity_operator.execute(connection,json.dumps(envelope).encode())
            finally:db.dispose()
            subject['actor_id']=receipt.result.target.actor_id
            private(self.out/('account-actor-'+str(index)+'.json'),{'command':envelope,'receipt':asdict(receipt)})
            with psycopg.connect(raw(self.frame['urls']['access'])) as connection:
                for command in ('account_grant.assign','account_grant.revoke'):
                    connection.execute("INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,application_id,target_account_id,enabled,created_by,updated_by) VALUES(%s,'access_operator',%s,'platform','pts',%s,true,%s,%s)",(uuid4(),command,subject['account'],access_executor,access_executor))
            if not subject['absent_grants']:
                for permission in ('pts.poetry.read','pts.poetry.export','pts.poetry.documents'):self.grant(subject['account'],permission)
        with psycopg.connect(raw(self.frame['urls']['access'])) as connection:
            existing=connection.execute("SELECT enabled FROM access.operator_authorities WHERE database_login='access_operator' AND command='application.set_enabled' AND application_id='pts' AND target_account_id IS NULL").fetchall()
            if not existing:connection.execute("INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by) VALUES(%s,'access_operator','application.set_enabled','platform','pts',true,%s,%s)",(uuid4(),access_executor,access_executor))
        self.app_enabled(True);private(self.out/'subjects-with-actors-private.json',self.subjects)
        self.checks.append('explicit-account-actor-and-three-independent-grants-with-zero-memberships')

    def refresh_subject_credentials(self,phase):
        """Fresh provider evidence for short-lived fixture baseline credentials.

        This is test setup, not browser renewal or a production refresh owner.
        Keep startup duration separate from the named behavior under test.
        """
        self.guard();observations=[]
        def claims(token):return json.loads(base64.urlsafe_b64decode(token.split('.')[1]+'='*(-len(token.split('.')[1])%4)))
        with httpx.Client(timeout=5,trust_env=False) as client:
            for subject in self.subjects:
                before=claims(subject['access_token'])
                response=client.post(self.frame['origin']+'/token?grant_type=refresh_token',json={'refresh_token':subject['refresh_token']})
                assert response.status_code==200,'fixture_baseline_refresh_failed'
                refreshed=response.json();verified=client.get(self.frame['origin']+'/user',headers={'Authorization':'Bearer '+refreshed['access_token']})
                assert verified.status_code==200 and verified.json()['id']==subject['account'],'fixture_baseline_user_verification_failed'
                after=claims(refreshed['access_token'])
                assert after['sub']==subject['account'] and after['session_id']==before['session_id'],'fixture_baseline_session_changed'
                with psycopg.connect(raw(self.frame['urls']['admin'])) as connection:
                    present=connection.execute('SELECT EXISTS(SELECT 1 FROM auth.sessions WHERE id=%s AND user_id=%s)',(after['session_id'],subject['account'])).fetchone()[0]
                assert present,'fixture_baseline_session_absent'
                subject.update(refreshed)
                observations.append({'refresh_status':response.status_code,'verification_status':verified.status_code,'same_account_and_session':True,'exact_provider_session_present':True,'credential_expired':after['exp']<=time.time()})
        private(self.out/('baseline-credentials-'+phase+'-private.json'),self.subjects)
        private(self.out/('baseline-refresh-'+phase+'-proof.json'),{'phase':phase,'observations':observations,'scope':'Fresh synthetic baseline credentials; not browser renewal acceptance.'})

    def access_command(self,command,payload):
        import access_operator
        from dataclasses import asdict
        envelope=dict(schema_version=1,operation_id=str(uuid4()),command=command,scope={'kind':'platform'},reason_code='synthetic_fixture',evidence_ref='fixture:pts-adoption:'+self.nonce,payload=payload)
        db=create_engine(self.frame['urls']['access_operator'],hide_parameters=True)
        try:
            with db.connect() as connection:receipt=access_operator.execute(connection,json.dumps(envelope).encode())
        finally:db.dispose()
        private(self.out/('access-operation-'+envelope['operation_id']+'.json'),{'command':envelope,'receipt':asdict(receipt)})
        return receipt

    def grant(self,account,permission,enabled=True):
        with psycopg.connect(raw(self.frame['urls']['admin'])) as connection:
            row=connection.execute('SELECT id,revision FROM access.account_grants WHERE account_id=%s AND permission=%s',(account,permission)).fetchone()
        payload={'account_id':account,'permission':permission}
        payload.update({'grant_id':str(row[0]),'expected_revision':str(row[1])} if row else {'expected_absent':True})
        return self.access_command('account_grant.assign' if enabled else 'account_grant.revoke',payload)

    def app_enabled(self,enabled):
        with psycopg.connect(raw(self.frame['urls']['admin'])) as connection:revision=connection.execute("SELECT revision FROM access.applications WHERE app_id='pts'").fetchone()[0]
        return self.access_command('application.set_enabled',{'app_id':'pts','enabled':enabled,'expected_revision':str(revision)})

    def storage(self):
        self.guard();admin=make_url(self.frame['urls']['admin']);name='pts_storage_'+self.nonce[:12];database='pst_88a737ddad7b_'+self.nonce[:8]
        role='pst_storage_'+self.nonce[:12];anon_role='pst_anon_'+self.nonce[:12];authenticated_role='pst_auth_'+self.nonce[:12];password=secrets.token_urlsafe(36);secret=secrets.token_urlsafe(48)
        with psycopg.connect(raw(self.frame['urls']['admin']),autocommit=True) as connection:
            connection.execute(sql.SQL('CREATE ROLE {} LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD {}').format(sql.Identifier(role),sql.Literal(password)))
            connection.execute(sql.SQL('COMMENT ON ROLE {} IS {}').format(sql.Identifier(role),sql.Literal('e1-pts-adoption:'+self.nonce)))
            for restricted in (anon_role,authenticated_role):
                connection.execute(sql.SQL('CREATE ROLE {} NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS').format(sql.Identifier(restricted)))
                connection.execute(sql.SQL('COMMENT ON ROLE {} IS {}').format(sql.Identifier(restricted),sql.Literal('e1-pts-adoption:'+self.nonce)))
            connection.execute(sql.SQL('CREATE DATABASE {} OWNER {}').format(sql.Identifier(database),sql.Identifier(role)))
        host='supabase_db_'+__import__('dev').project_identity(self.guard()[0],RUN)
        local=admin.set(database=database)
        with psycopg.connect(raw(local.render_as_string(hide_password=False)),autocommit=True) as connection:
            connection.execute(sql.SQL('CREATE SCHEMA auth AUTHORIZATION {}').format(sql.Identifier(role)))
            connection.execute(sql.SQL('CREATE TABLE auth.users(id uuid PRIMARY KEY);ALTER TABLE auth.users OWNER TO {}').format(sql.Identifier(role)))
            connection.execute(sql.SQL('GRANT USAGE ON SCHEMA auth TO {},{};GRANT SELECT ON auth.users TO {},{}').format(sql.Identifier(anon_role),sql.Identifier(authenticated_role),sql.Identifier(anon_role),sql.Identifier(authenticated_role)))
        provider_url=local.set(username=role,password=password,host=host,port=5432,drivername='postgresql').render_as_string(hide_password=False)
        environment={'DATABASE_URL':provider_url,'DATABASE_POOL_URL':provider_url,'AUTH_JWT_SECRET':secret,
            'ANON_KEY':mint(secret,'supabase',role=anon_role),'SERVICE_KEY':mint(secret,'supabase',role=role),
            'DB_ANON_ROLE':anon_role,'DB_AUTHENTICATED_ROLE':authenticated_role,'DB_SERVICE_ROLE':role,'DB_SUPER_USER':role,
            'TENANT_ID':'pts-'+self.nonce,'STORAGE_BACKEND':'file','STORAGE_FILE_BACKEND_PATH':'/var/lib/storage','FILE_STORAGE_BACKEND_PATH':'/var/lib/storage',
            'S3_PROTOCOL_ACCESS_KEY_ID':secrets.token_hex(16),'S3_PROTOCOL_ACCESS_KEY_SECRET':secrets.token_hex(32),'REGION':'local','SERVER_REGION':'local',
            'SERVER_HOST':'0.0.0.0','SERVER_PORT':'5000','DB_INSTALL_ROLES':'false','UPLOAD_FILE_SIZE_LIMIT':'134217728','UPLOAD_FILE_SIZE_LIMIT_STANDARD':'134217728',
            'FILE_SIZE_LIMIT':'134217728','LOG_LEVEL':'fatal','IMAGE_TRANSFORMATION_ENABLED':'false','OTEL_METRICS_ENABLED':'false','PG_QUEUE_ENABLE':'false'}
        envfile=self.out/'storage.env';envfile.write_text(''.join(k+'='+v+'\n' for k,v in environment.items()));envfile.chmod(0o600)
        container='pts-adopt-storage-'+self.nonce[:16];volume=container+'-bytes'
        identity=self.docker('run','-d','--name',container,'--label','agriplatform.pts-adoption='+self.nonce,'--label','agriplatform.run='+RUN,'--network',self.frame['network'],'--restart','no','--log-driver','local','--log-opt','max-size=1m','--log-opt','max-file=2','--env-file',envfile,'-p','127.0.0.1::5000','-v',volume+':/var/lib/storage',STORAGE)
        self.containers.append(container);native=json.loads(self.docker('inspect',container))[0]
        assert native['Id']==identity and native['Config']['Labels']['agriplatform.pts-adoption']==self.nonce
        port=native['NetworkSettings']['Ports']['5000/tcp'][0]['HostPort'];origin='http://127.0.0.1:'+port
        self.storage_frame={'database':database,'role':role,'container':container,'container_id':identity,'image_id':native['Image'],'volume':volume,'origin':origin,'env':environment}
        private(self.out/'storage-private.json',self.storage_frame)
        try:self.wait(origin,'/status',startup_seconds=60)
        except AssertionError:
            self.command(['docker','logs',container],'storage-startup-diagnostics')
            raise
        with httpx.Client(timeout=10,trust_env=False) as client:
            result=client.post(origin+'/bucket',headers={'Authorization':'Bearer '+environment['SERVICE_KEY']},json={'id':'pts-adoption-private','name':'pts-adoption-private','public':False})
            if result.status_code not in (200,201):
                body=result.text.lower()
                private(self.out/'bucket-failure.json',{'status':result.status_code,'permission_category':'permission' in body,'role_category':'role' in body,'jwt_category':'jwt' in body,'schema_category':'schema' in body})
                raise AssertionError('storage_bucket_creation_failed')
        self.checks.append('fresh-image-bound-Storage-separate-database-and-private-bucket')
        return self.storage_frame

    def owners(self):
        self.guard()
        custody=ROOT/'platform/deployment/.local/e1-pts-adoption-role-custody.json'
        roles=('pts_migrator','pts_runtime','pts_import','pts_account_runtime','pts_corpus_import')
        if custody.exists():
            selected=json.loads(custody.read_text());assert selected['run']==RUN and set(selected['roles'])==set(roles),'pts_role_custody_invalid'
        else:
            selected={'run':RUN,'roles':{role:secrets.token_urlsafe(36) for role in roles}}
            private(custody,selected)
        self.pts_urls={role:make_url(self.frame['urls']['admin']).set(username=role,password=selected['roles'][role]).render_as_string(hide_password=False) for role in roles}
        content_roles=json.loads((ROOT/'.local/leave-content-read-20261027/roles.json').read_text())['roles']
        self.content_urls={role:make_url(self.frame['urls']['admin']).set(username=role,password=password).render_as_string(hide_password=False) for role,password in content_roles.items()}
        with psycopg.connect(raw(self.frame['urls']['admin'])) as connection:
            for role in roles:
                found=connection.execute("SELECT shobj_description(oid,'pg_authid'),rolsuper,rolbypassrls,rolcreatedb,rolcreaterole,rolreplication,rolinherit,rolcanlogin FROM pg_roles WHERE rolname=%s",(role,)).fetchone()
                if found:assert found==('e1-pts-adoption:'+RUN,False,False,False,False,False,False,True),'pts_role_custody_changed'
                else:
                    connection.execute(sql.SQL('CREATE ROLE {} LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD {}').format(sql.Identifier(role),sql.Literal(selected['roles'][role])))
                    connection.execute(sql.SQL('COMMENT ON ROLE {} IS {}').format(sql.Identifier(role),sql.Literal('e1-pts-adoption:'+RUN)))
                assert not connection.execute('SELECT 1 FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname=%s)',(role,)).fetchall(),'pts_role_has_unrelated_membership'
            assert connection.execute("SELECT to_regnamespace('pts'),to_regnamespace('content')").fetchone()==(None,None),'fresh_owner_schemas_required'
            connection.execute('CREATE SCHEMA pts AUTHORIZATION pts_migrator;REVOKE ALL ON SCHEMA pts FROM PUBLIC;GRANT USAGE ON SCHEMA pts TO pts_runtime,pts_import,pts_account_runtime,pts_corpus_import;CREATE SCHEMA content AUTHORIZATION content_migrator;REVOKE ALL ON SCHEMA content FROM PUBLIC;GRANT USAGE ON SCHEMA content TO content_runtime,content_operator')
        self.upgrade_owner('pts','pts_0001');self.upgrade_owner('content','content_0004')
        self.checks.append('fresh-owner-predecessor-schemas-with-restricted-independent-credentials')
        private(self.out/'owner-urls-private.json',{'pts':self.pts_urls,'content':self.content_urls})

    def upgrade_owner(self,owner,revision='head'):
        path=ROOT/('apps/pts/alembic.ini' if owner=='pts' else 'services/content-service/alembic.ini')
        urls=self.pts_urls if owner=='pts' else self.content_urls
        environment={'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1',owner.upper()+'_MIGRATION_DATABASE_URL':urls[owner+'_migrator']}
        self.command([sys.executable,'-B','-m','alembic','-c',path,'upgrade',revision],owner+'-upgrade-'+revision+'-'+uuid4().hex,env=environment)

    def start_owner(self,folder,environment,label,module='main:app',python=None,port=None):
        if port is None:
            with socket.socket() as selected:selected.bind(('127.0.0.1',0));port=selected.getsockname()[1]
        log=open(self.out/(label+'.log'),'xb')
        process=subprocess.Popen([str(python or sys.executable),'-B','-m','uvicorn',module,'--host','127.0.0.1','--port',str(port),'--no-access-log','--log-level','critical','--timeout-graceful-shutdown','20'],cwd=ROOT/folder,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1',**environment},stdout=log,stderr=log)
        self.processes.append((process,log));origin='http://127.0.0.1:'+str(port)
        for _ in range(100):
            if process.poll() is not None:raise AssertionError(label+'_owner_start_failed')
            try:
                with httpx.Client(timeout=.5,trust_env=False) as client:
                    if client.get(origin+'/health').status_code==200:return {'origin':origin,'port':port,'pid':process.pid}
            except httpx.HTTPError:pass
            time.sleep(.05)
        raise AssertionError(label+'_owner_health_failed')

    def auth_proxy(self):
        # A transparent path adapter for Access's existing Supabase /auth/v1 URL.
        # Provider decisions and credentials pass unchanged; no identity is fabricated.
        path=self.out/'provider_proxy.py'
        path.write_text("""from fastapi import FastAPI,Request
from fastapi.responses import Response
from hashlib import sha256
from pathlib import Path
import httpx
app=FastAPI(docs_url=None,openapi_url=None)
refreshed=set()
@app.get('/health')
def health():return {'status':'running'}
@app.api_route('/auth/v1/{path:path}',methods=['GET','POST','PUT','OPTIONS'])
async def proxy(path:str,request:Request):
 authorization=request.headers.get('authorization','')
 if path=='logout' and Path("""+repr(str(self.out/'response-gate/fail-logout-after-refresh'))+""").exists() and sha256(authorization.encode()).hexdigest() in refreshed:
  return Response('{"code":"fixture_provider_unavailable"}',status_code=503,headers={'Content-Type':'application/json'})
 async with httpx.AsyncClient(trust_env=False,follow_redirects=False,timeout=5) as client:
  response=await client.request(request.method,"""+repr(self.frame['origin'])+"""+'/'+path,params=request.query_params,content=await request.body(),headers={k:v for k,v in request.headers.items() if k.lower() in ('authorization','apikey','content-type')})
 if path=='token' and request.query_params.get('grant_type')=='refresh_token' and response.status_code==200:
  refreshed.add(sha256(('Bearer '+response.json()['access_token']).encode()).hexdigest())
 return Response(response.content,status_code=response.status_code,headers={k:v for k,v in response.headers.items() if k.lower() in ('content-type','cache-control')})
""")
        return self.start_owner(self.out.relative_to(ROOT),{},'auth-proxy','provider_proxy:app')

    def start_services(self,file_origin,frontend_origin):
        self.file_origin=file_origin;self.frontend_origin=frontend_origin
        proxy=self.auth_proxy();self.pts_key=secrets.token_urlsafe(36);session_key=secrets.token_urlsafe(36);self.directory_key=secrets.token_urlsafe(36)
        session_url=make_url(self.frame['urls']['admin']).set(username=self.session_owner.RUNTIME,password=self.session_roles[self.session_owner.RUNTIME]).render_as_string(hide_password=False)
        access_environment={'ACCESS_DATABASE_URL':self.frame['urls']['runtime'],'CAPABILITY_ACCESS_DATABASE_URL':self.frame['urls']['runtime'],'PTS_SERVICE_KEY':self.pts_key,'SUPABASE_URL':proxy['origin'],'SUPABASE_ANON_KEY':'synthetic-public-key',
            'DIRECTORY_SERVICE_KEY':self.directory_key,'PTS_CURRENT_SESSION_SERVICE_KEY':session_key,'IDENTITY_CURRENT_SESSION_DATABASE_URL':raw(session_url),'IDENTITY_CURRENT_SESSION_AUTH_URL':self.frame['origin'],'IDENTITY_CURRENT_SESSION_ISSUER':self.frame['issuer'],'IDENTITY_CURRENT_SESSION_AUDIENCE':'authenticated','IDENTITY_CURRENT_SESSION_POLICY':'supabase-auth-2.197.0-default'}
        if getattr(self,'access_image',None):
            from apps.pts.tests.image_acceptance import start_access
            access=start_access(self,access_environment)
        else:access=self.start_owner('services/access',access_environment,'access')
        # PtS's existing calling credential identifies that app at each HTTP owner.
        content_key=self.pts_key;self.content_key=content_key;self.content_executor=self.register_service_actor();policy=self.out/'content-policy-private.json'
        private(policy,{'version':1,'services':[{'key':content_key,'application_id':'pts','executor_actor_id':self.content_executor,'operations':['create','finalize','metadata','read'],'scope_kinds':['application']}]})
        storage=self.storage_frame
        content=self.start_owner('services/content-service',{'CONTENT_DATABASE_URL':self.content_urls['content_runtime'],'CONTENT_SERVICE_POLICY_FILE':str(policy),'CONTENT_BUCKET':'pts-adoption-private','CONTENT_S3_ENDPOINT':storage['origin']+'/s3','CONTENT_S3_REGION':'local','CONTENT_S3_ACCESS_KEY':storage['env']['S3_PROTOCOL_ACCESS_KEY_ID'],'CONTENT_S3_SECRET_KEY':storage['env']['S3_PROTOCOL_ACCESS_KEY_SECRET']},'content')
        pts_environment={'PTS_DATABASE_URL':self.pts_urls['pts_account_runtime'],'ACCESS_URL':access['origin'],'IDENTITY_URL':access['origin'],'CONTENT_URL':content['origin'],'PTS_SERVICE_KEY':self.pts_key,'PTS_CURRENT_SESSION_SERVICE_KEY':session_key,'PTS_CORS_ORIGINS':frontend_origin,'PTS_FILE_ORIGIN':file_origin,'PTS_FILE_FRONTEND_ORIGIN':frontend_origin}
        self.pts_environment=pts_environment
        if hasattr(self,'runtime_image'):
            from apps.pts.tests.image_acceptance import start_pts
            pts=start_pts(self,pts_environment)
        else:pts=self.start_owner('.',pts_environment,'pts','apps.pts.backend.main:app')
        self.services={'access':access,'content':content,'pts':pts,'auth_proxy':proxy};private(self.out/'services-private.json',self.services)
        self.checks.append('actual-Access-'+('runtime-image' if getattr(self,'access_image',None) else 'source-process')+'-Content-source-process-and-PtS-'+('runtime-image' if hasattr(self,'runtime_image') else 'source-process')+'-health')
        return self.services

    def register_service_actor(self):
        import identity_operator
        from dataclasses import asdict
        with psycopg.connect(raw(self.frame['urls']['identity'])) as connection:
            executor=connection.execute("SELECT executor_actor_id FROM identity.operator_principals WHERE database_login='identity_operator'").fetchone()[0]
            existing=connection.execute("SELECT enabled FROM identity.operator_authorities WHERE database_login='identity_operator' AND command='actor.register_system' AND scope_kind='platform' AND target_account_id IS NULL").fetchall()
            if not existing:
                connection.execute("INSERT INTO identity.operator_authorities(id,database_login,command,scope_kind,enabled,created_by,updated_by) VALUES(%s,'identity_operator','actor.register_system','platform',true,%s,%s)",(uuid4(),executor,executor))
            else:assert existing==[(True,)],'actor_registration_not_authorized'
        envelope=dict(schema_version=1,operation_id=str(uuid4()),command='actor.register_system',scope={'kind':'platform'},reason_code='synthetic_fixture',evidence_ref='fixture:pts-adoption:'+self.nonce,
            payload=dict(actor_id=str(uuid4()),kind='service',actor_key='pts.fixture.'+self.nonce,display_name='Synthetic PtS fixture executor',expected_absent=True))
        db=create_engine(self.frame['urls']['identity_operator'],hide_parameters=True)
        try:
            with db.connect() as connection:receipt=identity_operator.execute(connection,json.dumps(envelope).encode())
        finally:db.dispose()
        private(self.out/'service-actor-receipt.json',{'command':envelope,'receipt':asdict(receipt)})
        return receipt.result.target.actor_id

    def owner_checkpoint(self):
        # No corpus selection or byte-adoption claim at this startup boundary.
        subject=self.subjects[0];authorization='Bearer '+subject['access_token'];observations=[]
        with httpx.Client(timeout=10,trust_env=False) as client:
            for permission in ('pts.poetry.read','pts.poetry.export','pts.poetry.documents'):
                response=client.post(self.services['access']['origin']+'/v2/check',headers={'Authorization':authorization,'X-Service-Key':self.pts_key},json={'permission':permission,'authorization_scope':{'kind':'account'}})
                observations.append({'operation':'account-capability','permission':permission,'status':response.status_code})
                assert response.status_code==200 and response.json()['account_id']==subject['account'] and response.json()['actor_id']==subject['actor_id'],'actual_account_capability_failed'
            response=client.post(self.services['pts']['origin']+'/api/file-session',headers={'Host':httpx.URL(self.file_origin).netloc.decode(),'Origin':self.frontend_origin,'Authorization':authorization})
            observations.append({'operation':'current-session-and-file-cookie-setup-over-loopback','status':response.status_code})
            assert response.status_code==200,'actual_current_session_cookie_setup_failed'
            cookie=response.headers['set-cookie'];assert '__Host-pts-file=' in cookie and 'HttpOnly' in cookie and 'Secure' in cookie and 'SameSite=lax' in cookie
            response=client.get(self.services['pts']['origin']+'/api/poetry',headers={'Authorization':authorization})
            observations.append({'operation':'unverified-corpus-activation-block','status':response.status_code})
            assert response.status_code==503,'unbound_corpus_not_blocked'
            response=client.get(self.services['content']['origin']+'/v2/objects/'+str(uuid4()),params={'application_id':'pts','kind':'application'},headers={'X-Service-Key':self.content_key})
            observations.append({'operation':'owned-content-missing-object','status':response.status_code})
            assert response.status_code==404,'actual_content_owner_route_failed'
        private(self.out/'owner-startup-observations.json',observations)
        self.checks.append('actual-account-capabilities-and-current-session-cookie-setup')
        self.checks.append('unverified-corpus-activation-block-and-owned-Content-route')

    def source_binding(self):
        selected=set()
        for folder in ('apps/pts/backend','apps/pts/migrations','apps/pts/tools','apps/pts/tests','apps/pts/deployment','apps/pts/web/src','apps/pts/web/tests','platform/ui-business/src','platform/app-directory-client/src','services/access','services/content-service','services/app-directory'):
            for path in (ROOT/folder).rglob('*'):
                relative=path.relative_to(ROOT)
                if any(part.startswith('.') or part in ('node_modules','build','dist','__pycache__','runtime-bundle') or part.startswith('runtime-bundle.') for part in relative.parts):continue
                if path.is_file() and (path.suffix in ('.py','.sql','.json','.toml','.ini','.lock','.ts','.tsx','.cjs','.mjs','.css') or path.name.endswith('Dockerfile') or path.name.endswith('dockerignore')):selected.add(path)
        for name in ('apps/pts/reference/poetry-library/library.json','apps/pts/pyproject.toml','apps/pts/uv.lock','apps/pts/alembic.ini',
            'package.json','package-lock.json','apps/pts/web/package.json','apps/pts/web/index.html','apps/pts/web/tsconfig.json','apps/pts/web/vite.config.ts','apps/pts/web/playwright.config.cjs',
            'platform/ui-business/package.json','platform/ui-business/tsconfig.json','platform/app-directory-client/package.json','platform/app-directory-client/tsconfig.json',
            '.github/workflows/production.yml','platform/deployment/ci-deploy.sh','platform/deployment/render_gateway.py','platform/deployment/release.py','platform/deployment/host-release.py',
            'platform/deployment/build-release.mjs','platform/deployment/frontend-inputs.mjs','platform/deployment/install-frontends.py','platform/deployment/check-ci-inputs.py','platform/deployment/content_policy.py',
            'platform/deployment/prepare-runtime-bundles.py','platform/deployment/ci-build.py','platform/deployment/tls/renew.py','platform/deployment/tests/gateway_smoke.py',
            'apps/pts/deployment/manifest.json','services/access/identity-migrations/current-session-reference.json'):
            selected.add(ROOT/name)
        private(self.out/'source-binding.json',{'schema_version':1,'python':sys.version,'sources':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(selected)},
            'absent_workspace_inputs':[name for name in ('apps/pts/web/package-lock.json',) if not (ROOT/name).exists()],
            'boundary':'Source custody only, including frontend workspace/build inputs, shared clients, actual Directory owner and coordinated release tooling. Consult named phase results for actual behavior; no hosted-production/human-device claim.'})

    def finish(self):
        stops=[]
        for process,log in reversed(self.processes):
            process.terminate()
            try:code=process.wait(timeout=25)
            except subprocess.TimeoutExpired:process.kill();code=process.wait(timeout=5)
            log.close();stops.append({'pid':process.pid,'exit_code':code,'forced':code==-9})
        for container in reversed(self.containers):
            self.docker('stop','--time','20',container);value=json.loads(self.docker('inspect',container))[0]
            stops.append({'container_id':value['Id'],'exit_code':value['State']['ExitCode'],'forced':value['State']['ExitCode']==137 or value['State']['OOMKilled']})
        attached=self.session_owner.ATTACHED_PROVIDER
        if attached is not None:
            attached.communicate(timeout=5)
            stops.append({'provider_attach_exit_code':attached.returncode,'forced':False})
        private(self.out/'cleanup.json',{'stops':stops})
        private(self.out/'fixture-state.json',{'checks':self.checks,'provider_output':str(self.provider_out.relative_to(ROOT)) if hasattr(self,'provider_out') else None,'nonce':self.nonce})
        return stops

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--runtime-image-binding');parser.add_argument('--access-image');parser.add_argument('--refresh-cleanup-reference',action='store_true');parser.add_argument('--phase',choices=('provider-storage','cleanup','cleanup-owners','owners','acceptance','browser','gateway','image-browser','image-resources','image-session-races','session-races','resources','resource-probe','viewer'),default='provider-storage');args=parser.parse_args();fixture=Fixture(args.output);fixture.refresh_cleanup_reference=args.refresh_cleanup_reference;fixture.access_image=args.access_image
    try:
        fixture.source_binding()
        from apps.pts.tests.image_acceptance import prepare,reuse,runtime_image_mode
        mode=runtime_image_mode(args.phase,args.runtime_image_binding)
        if mode:
            if mode=='reuse':reuse(fixture,args.runtime_image_binding)
            else:prepare(fixture)
        if args.phase in ('cleanup','cleanup-owners','session-races','image-session-races'):fixture.jwt_expiry_seconds=60
        if args.phase=='cleanup':fixture.cleanup_matrix=True
        if args.phase in ('resources','image-resources'):fixture.subject_count=9;fixture.resource_matrix=True
        if args.phase=='resource-probe':fixture.subject_count=9;fixture.resource_probe=True
        if args.phase=='viewer':
            from apps.pts.tests.tls_acceptance import viewer_probe
            viewer_probe(fixture)
        elif args.phase=='gateway':
            from apps.pts.tests.tls_acceptance import gateway_startup
            gateway_startup(fixture)
        else:fixture.provider();fixture.accounts();fixture.storage()
        if args.phase in ('cleanup','cleanup-owners','owners','acceptance','browser','image-browser','image-resources','image-session-races','session-races','resources','resource-probe'):
            fixture.owners();fixture.upgrade_owner('pts');fixture.upgrade_owner('content')
            suffix=''
            if args.phase in ('cleanup','browser','image-browser','image-resources','image-session-races','session-races','resources','resource-probe'):
                with socket.socket() as selected:selected.bind(('127.0.0.1',0));suffix=':'+str(selected.getsockname()[1])
            fixture.start_services('https://files.pts.fixture.test'+suffix,'https://pts.fixture.test'+suffix)
            fixture.refresh_subject_credentials('owner-checkpoint');fixture.owner_checkpoint()
        if args.phase=='cleanup':
            from apps.pts.tests.cleanup_acceptance import unmapped_account
            unmapped_account(fixture)
        if args.phase in ('cleanup','cleanup-owners','acceptance','browser','image-browser','image-resources','image-session-races','session-races','resources','resource-probe'):
            from apps.pts.tests.native_acceptance import qualify
            qualify(fixture)
        if args.phase in ('cleanup','browser','image-browser','image-resources','image-session-races','session-races','resources','resource-probe'):
            from apps.pts.tests.tls_acceptance import qualify
            qualify(fixture)
        if args.phase in ('cleanup','cleanup-owners'):
            from apps.pts.tests.cleanup_acceptance import qualify
            qualify(fixture)
    finally:fixture.finish()
    print(json.dumps({'checks':len(fixture.checks),'complete':True}))
