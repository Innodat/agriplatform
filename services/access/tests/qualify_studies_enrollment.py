"""Focused synthetic Studies qualification; fixed retained loopback run only.

No real account, deployment, general provisioning or historical fixture mutation.
Private URLs and synthetic provider credentials are never written to stdout.
"""
if not __debug__:
    raise RuntimeError('studies_qualification_optimized_python_prohibited')
import asyncio
import importlib.util
import json
import os
from pathlib import Path
import secrets
import sys
from uuid import uuid4
from hashlib import sha256
import psycopg
from psycopg import sql
from sqlalchemy import create_engine,text
from sqlalchemy.engine import make_url
ROOT=Path(__file__).resolve().parents[3]
ACCESS=ROOT/'services/access'
INITIAL_PROOF=ROOT/'platform/deployment/.local/identity-baseline/studies-enrollment-20261023'
PROOF=ROOT/'platform/deployment/.local/identity-baseline/studies-enrollment-review-20261023'
PRIOR=ROOT/'platform/deployment/.local/identity-baseline/organization-check-reviewed3-20261022'
RUN='99b7231c-0a5b-4bdb-98e8-3329564c526a'
ROLES=('identity_studies_owner','identity_studies_reader_runtime','identity_studies_setup_runtime','access_studies_owner','access_studies_runtime')

EXECUTED_SOURCES=None

def write_private(path,value):
    if path.name in ('current-first-use-race.json','boundaries.json','current-denials.json','confirmed-http-denials.json','current-cli-proof.json','current-clean-upgrade-proof.json','provider-proof.json','lock-eligibility.json'):
        if EXECUTED_SOURCES is None or EXECUTED_SOURCES!=source_hashes():raise ValueError('studies_stage_source_changed')
        value={**value,'executed_sources':EXECUTED_SOURCES}
    with path.open('x') as output:json.dump(value,output,sort_keys=True,indent=2,default=lambda item:__import__('dataclasses').asdict(item) if __import__('dataclasses').is_dataclass(item) else str(item))
    path.chmod(0o600)

def inputs():
    run=json.loads((PRIOR/'run.json').read_text())
    assert run['run_id']==RUN
    private=json.loads((PRIOR/'credentials.json').read_text())
    source=make_url(private['databases']['bridge'])
    assert source.host in ('127.0.0.1','localhost') and source.username=='postgres' and source.port!=54322
    assert source.database==run['database_namespace']+'bridge' and not source.query
    return source

def connect(url,autocommit=False):
    return psycopg.connect(url.render_as_string(hide_password=False),autocommit=autocommit,connect_timeout=3)

def engine(url):
    return create_engine(url.set(drivername='postgresql+psycopg'),hide_parameters=True,connect_args={'connect_timeout':3})

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def prepare():
    source=inputs();PROOF.mkdir(mode=0o700,parents=True,exist_ok=False)
    private={'source_database':source.database,'databases':{},'passwords':{role:secrets.token_urlsafe(24) for role in ROLES if role.endswith('_runtime')}}
    admin=source.set(username='supabase_admin',database='postgres')
    with connect(admin,True) as conn:
        for role in ROLES:
            assert not conn.execute('SELECT 1 FROM pg_roles WHERE rolname=%s',(role,)).fetchone(),'studies_role_already_exists'
            if role.endswith('_runtime'):
                conn.execute(sql.SQL('CREATE ROLE {} LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD {}').format(sql.Identifier(role),sql.Literal(private['passwords'][role])))
            else:
                conn.execute(sql.SQL('CREATE ROLE {} NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS').format(sql.Identifier(role)))
                owner=role.split('_',1)[0]+'_migrator'
                conn.execute(sql.SQL('GRANT {} TO {} WITH ADMIN FALSE, INHERIT FALSE, SET TRUE').format(sql.Identifier(role),sql.Identifier(owner)))
        for case in ('upgrade','failure'):
            name='ida_'+RUN.replace('-','')[:12]+'_studies_'+uuid4().hex[:10]+'_'+case
            conn.execute(sql.SQL('CREATE DATABASE {} WITH TEMPLATE {}').format(sql.Identifier(name),sql.Identifier(source.database)))
            private['databases'][case]=name
    write_private(PROOF/'private.json',private)
    bootstrap_auth()

def bootstrap_auth():
    source=inputs();private=json.loads((PROOF/'private.json').read_text())
    fields=('email_confirmed_at','banned_until','is_anonymous')
    with connect(source.set(username='supabase_admin',database='postgres')) as conn:
        actual=dict(conn.execute("SELECT a.attname,format_type(a.atttypid,a.atttypmod) FROM pg_attribute a WHERE a.attrelid='auth.users'::regclass AND a.attname=ANY(%s)",(list(fields),)).fetchall())
    assert set(actual)==set(fields),'live_provider_schema_missing'
    for name in private['databases'].values():
        with connect(source.set(username='supabase_admin',database=name)) as conn:
            for field in fields:
                conn.execute(sql.SQL('ALTER TABLE auth.users ADD COLUMN IF NOT EXISTS {} {}').format(sql.Identifier(field),sql.SQL(actual[field])))
            conn.execute('GRANT USAGE ON SCHEMA auth TO identity_studies_owner')
            conn.execute('GRANT SELECT(id,deleted_at,email_confirmed_at,banned_until,is_anonymous) ON auth.users TO identity_studies_owner')
            conn.execute("CREATE POLICY studies_current_account ON auth.users FOR SELECT TO identity_studies_owner USING(id::text=current_setting('app.account_id',true))")
    write_private(PROOF/'prepared.json',{'run_id':RUN,'databases':list(private['databases'].values()),'auth_selected_field_types':actual,'status':'prepared'})

def owner_url(case,owner):
    source=inputs();private=json.loads((PROOF/'private.json').read_text())
    prior=json.loads((PRIOR/'credentials.json').read_text())
    group='owner_urls' if owner=='identity' else 'access_owner_urls'
    database=json.loads((PROOF/'current-populated-database.json').read_text())['database'] if case=='current-populated' else private['databases'][case]
    return make_url(prior[group]['bridge']).set(database=database)

def upgrade_identity(case='upgrade',record=False):
    sys.path.insert(0,str(ACCESS/'identity-migrations'))
    import identity_baseline as baseline
    import identity_studies_catalog as catalog
    migration=load_module('_studies_identity_ddl',ACCESS/'identity-migrations/versions/0021_studies_account_setup.py')
    db=engine(owner_url(case,'identity'))
    try:
        with db.begin() as c:
            c.exec_driver_sql("SET LOCAL lock_timeout='1s'; SET LOCAL statement_timeout='20s'")
            baseline.preflight(c,'clean')
            from alembic.migration import MigrationContext
            from alembic.operations import Operations
            with Operations.context(MigrationContext.configure(c)):migration.upgrade()
            c.exec_driver_sql("UPDATE identity.alembic_version SET version_num='identity_0021'")
            if record:
                content={'migration_sha256':sha256((ACCESS/'identity-migrations/versions/0021_studies_account_setup.py').read_bytes()).hexdigest(),'catalog':baseline.catalog_fingerprints(catalog.snapshot(c))}
                path=ACCESS/'identity-migrations/studies-setup-reference.json'
                if path.exists():write_private(PROOF/('earlier-candidate-reference-'+uuid4().hex+'.json'),json.loads(path.read_bytes()))
                with path.open('w') as output:json.dump(content,output,sort_keys=True,indent=2);output.write('\n')
                digest=sha256(path.read_bytes()).hexdigest()
                support=ACCESS/'identity-migrations/identity_studies_catalog.py'
                support.write_text(__import__('re').sub(r"REFERENCE_SHA256=(?:None|'[a-f0-9]+')","REFERENCE_SHA256='"+digest+"'",support.read_text()))
                catalog.REFERENCE_SHA256=digest
            baseline.verify_owned_postcondition(c,require_head=True)
    finally:db.dispose()

def upgrade_access(case='upgrade'):
    sys.path.insert(0,str(ACCESS/'migrations'))
    import access_baseline as baseline
    migration=load_module('_studies_access_ddl',ACCESS/'migrations/versions/0016_studies_account_enrollment.py')
    db=engine(owner_url(case,'access'))
    try:
        with db.begin() as c:
            c.exec_driver_sql("SET LOCAL lock_timeout='1s'; SET LOCAL statement_timeout='20s'")
            baseline.preflight(c)
            from alembic.migration import MigrationContext
            from alembic.operations import Operations
            with Operations.context(MigrationContext.configure(c)):migration.upgrade()
            c.exec_driver_sql("UPDATE access.alembic_version SET version_num='access_0016'")
            baseline.verify_postcondition(c)
    finally:db.dispose()

def provider_fixture():
    import subprocess,httpx
    run_path=ROOT/'platform/deployment/.local/kdg'/RUN
    cli=ROOT/'platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase'
    result=subprocess.run([str(cli),'--workdir',str(run_path),'status','--output','json'],capture_output=True,timeout=30)
    if result.returncode:raise RuntimeError('provider_fixture_status_unavailable')
    status=json.loads(result.stdout)
    keys={key.lower():value for key,value in status.items()}
    api=keys['api_url'];assert api in ('http://127.0.0.1:55481','http://localhost:55481')
    service=keys['service_role_key'];anon=keys['anon_key']
    email='studies-'+uuid4().hex+'@example.invalid';password=secrets.token_urlsafe(32)
    with httpx.Client(timeout=3) as client:
        response=client.post(api+'/auth/v1/admin/users',headers={'apikey':service,'Authorization':'Bearer '+service},json={'email':email,'password':password,'email_confirm':True})
        assert response.status_code==200,'provider_synthetic_create_failed'
        account=response.json()['id']
        attempt=PROOF/('provider-attempt-'+uuid4().hex+'.json')
        write_private(attempt,{'account':account,'email':email,'password':password,'api':api,'anon_key':anon,'service_key':service})
        response=client.post(api+'/auth/v1/token?grant_type=password',headers={'apikey':anon},json={'email':email,'password':password})
        if response.status_code!=200:
            write_private(PROOF/('provider-sign-in-failure-'+uuid4().hex+'.json'),{'status':response.status_code,'body':response.json()})
            raise RuntimeError('provider_synthetic_sign_in_failed')
        token=response.json()['access_token']
        response=client.get(api+'/auth/v1/user',headers={'apikey':anon,'Authorization':'Bearer '+token})
        assert response.status_code==200 and response.json()['id']==account and response.json()['email_confirmed_at'],'provider_live_verification_failed'
        live=response.json()
    value={'api':api,'anon_key':anon,'service_key':service,'account':account,'email':email,'password':password,'token':token,'live':live}
    write_private(PROOF/'provider.json',value)
    # Actual provider-created account/profile hook proof remains separate from the
    # isolated owner DB fixture. Mirror only this synthetic account into its stub.
    source=inputs();private=json.loads((PROOF/'private.json').read_text())
    with connect(source.set(username='supabase_admin',database='postgres')) as c:
        native_hook=c.execute("SELECT EXISTS(SELECT 1 FROM pg_trigger t JOIN pg_proc p ON p.oid=t.tgfoid JOIN pg_namespace n ON n.oid=p.pronamespace WHERE t.tgrelid='auth.users'::regclass AND n.nspname='identity' AND t.tgenabled='O')").fetchone()[0]
        if native_hook:
            assert c.execute('SELECT id FROM identity.users WHERE id=%s',(account,)).fetchone(),'provider_profile_hook_did_not_run'
    isolated=source.set(username='supabase_admin',database=private['databases']['upgrade'])
    with connect(isolated) as c:
        c.execute('INSERT INTO auth.users(id,email,deleted_at,email_confirmed_at,banned_until,is_anonymous) VALUES(%s,%s,NULL,%s,NULL,false)',(account,email,live['email_confirmed_at']))
        profile=c.execute('SELECT id,username FROM identity.users WHERE id=%s',(account,)).fetchone()
        assert profile and str(profile[0])==account,'isolated_actual_profile_hook_failed'
        assert c.execute('SELECT count(*) FROM identity.org_member WHERE user_id=%s',(account,)).fetchone()[0]==0
    write_private(PROOF/'provider-proof.json',{'account':account,'native_identity_hook':native_hook,'isolated_profile_hook':True,'zero_memberships':True})

def provider_link():
    import httpx
    attempt=max(PROOF.glob('provider-attempt-*.json'),key=lambda path:path.stat().st_mtime)
    value=json.loads(attempt.read_text());api=value['api']
    with httpx.Client(timeout=3) as client:
        response=client.post(api+'/auth/v1/admin/generate_link',headers={'apikey':value['service_key'],'Authorization':'Bearer '+value['service_key']},json={'type':'magiclink','email':value['email']})
        write_private(PROOF/('provider-link-result-'+uuid4().hex+'.json'),{'status':response.status_code,'body':response.json()})
        assert response.status_code==200,'provider_generate_link_failed'
        payload=response.json();hashed=payload.get('hashed_token') or payload['properties']['hashed_token']
        response=client.post(api+'/auth/v1/verify',headers={'apikey':value['anon_key']},json={'type':'magiclink','token_hash':hashed})
        if response.status_code!=200:
            write_private(PROOF/('provider-verify-failure-'+uuid4().hex+'.json'),{'status':response.status_code,'body':response.json()})
            raise RuntimeError('provider_magiclink_sign_in_failed')
        value['token']=response.json()['access_token']
        response=client.get(api+'/auth/v1/user',headers={'apikey':value['anon_key'],'Authorization':'Bearer '+value['token']})
        assert response.status_code==200 and response.json()['id']==value['account']
        value['live']=response.json()
    write_private(PROOF/'provider.json',value)
    mirror_provider_account(value)

def mirror_provider_account(value):
    source=inputs();private=json.loads((PROOF/'private.json').read_text());account=value['account']
    with connect(source.set(username='supabase_admin',database='postgres')) as c:
        native_hook=c.execute("SELECT EXISTS(SELECT 1 FROM pg_trigger t JOIN pg_proc p ON p.oid=t.tgfoid JOIN pg_namespace n ON n.oid=p.pronamespace WHERE t.tgrelid='auth.users'::regclass AND n.nspname='identity' AND t.tgenabled='O')").fetchone()[0]
        if native_hook:assert c.execute('SELECT id FROM identity.users WHERE id=%s',(account,)).fetchone(),'provider_profile_hook_did_not_run'
    isolated=source.set(username='supabase_admin',database=private['databases']['upgrade'])
    with connect(isolated) as c:
        c.execute('INSERT INTO auth.users(id,email,deleted_at,email_confirmed_at,banned_until,is_anonymous) VALUES(%s,%s,NULL,%s,NULL,false)',(account,value['email'],value['live']['email_confirmed_at']))
        profile=c.execute('SELECT id,username FROM identity.users WHERE id=%s',(account,)).fetchone()
        assert profile and str(profile[0])==account,'isolated_actual_profile_hook_failed'
        assert c.execute('SELECT count(*) FROM identity.org_member WHERE user_id=%s',(account,)).fetchone()[0]==0
    write_private(PROOF/'provider-proof.json',{'account':account,'native_identity_hook':native_hook,'isolated_profile_hook':True,'zero_memberships':True,'authentication':'admin-generated-magic-link-no-delivery'})

def runtime_prepare():
    sys.path.insert(0,str(ACCESS))
    from access_operator import execute
    value={'service_actor':str(uuid4()),'service_key':secrets.token_urlsafe(32)}
    write_private(PROOF/'runtime.json',value)
    identity=engine(owner_url('upgrade','identity'))
    with identity.begin() as c:
        c.execute(text("INSERT INTO identity.actor(id,kind,display_name,actor_key,created_by,updated_by) VALUES(CAST(:actor AS uuid),'service','Studies synthetic service','studies_fixture.'||:key,CAST(:actor AS uuid),CAST(:actor AS uuid))"),{'actor':value['service_actor'],'key':uuid4().hex})
        assert c.execute(text("SELECT kind FROM identity.actor WHERE id=CAST(:actor AS uuid)"),{'actor':value['service_actor']}).scalar_one()=='service'
        c.execute(text("INSERT INTO identity.studies_runtime_principal(database_login,executor_actor_id,enabled,created_by,updated_by,operation_id) VALUES('identity_studies_setup_runtime',CAST(:actor AS uuid),true,CAST(:actor AS uuid),CAST(:actor AS uuid),gen_random_uuid())"),{'actor':value['service_actor']})
    identity.dispose()
    access=engine(owner_url('upgrade','access'))
    with access.begin() as c:
        c.execute(text("INSERT INTO access.studies_runtime_principal(database_login,executor_actor_id,enabled,created_by,updated_by,operation_id) VALUES('access_studies_runtime',CAST(:actor AS uuid),true,CAST(:actor AS uuid),CAST(:actor AS uuid),gen_random_uuid())"),{'actor':value['service_actor']})
        actor=c.exec_driver_sql("SELECT executor_actor_id FROM access.operator_principals WHERE database_login='access_operator' AND enabled").scalar_one()
        for command in ('application.register','permission.register','application.set_enabled'):
            c.execute(text("INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_operator',:command,'platform','scribeswell',true,:actor,:actor)"),{'command':command,'actor':actor})
    access.dispose()
    registry_prepare()

def registry_prepare():
    sys.path.insert(0,str(ACCESS))
    from access_operator import execute
    prior=json.loads((PRIOR/'credentials.json').read_text());database=json.loads((PROOF/'private.json').read_text())['databases']['upgrade']
    operator=engine(make_url(prior['access_operator_urls']['bridge']).set(database=database))
    for command,payload in (
        ('application.register',{'app_id':'scribeswell','expected_absent':True}),
        ('permission.register',{'app_id':'scribeswell','permission':'scribeswell.studies.use','scope_kind':'account','expected_absent':True}),
        ('application.set_enabled',{'app_id':'scribeswell','enabled':True,'expected_revision':'1'})):
        envelope={'schema_version':1,'operation_id':str(uuid4()),'command':command,'scope':{'kind':'platform'},'payload':payload,'reason_code':'synthetic_fixture','evidence_ref':'synthetic:studies-enrollment'}
        with operator.connect() as c:receipt=execute(c,json.dumps(envelope).encode())
        write_private(PROOF/(command+'-'+uuid4().hex+'.json'),{'command':envelope,'receipt':receipt})
    operator.dispose()

def runtime_urls():
    source=inputs();private=json.loads((PROOF/'private.json').read_text());database=private['databases']['upgrade']
    return {role:source.set(database=database,username=role,password=password).render_as_string(hide_password=False) for role,password in private['passwords'].items()}

def runtime_app():
    sys.path.insert(0,str(ACCESS))
    from unittest.mock import patch
    from main import create_app
    from studies_identity import AsyncDatabase
    provider=json.loads((PROOF/'provider.json').read_text());runtime=json.loads((PROOF/'runtime.json').read_text());urls=runtime_urls()
    env={'SCRIBESWELL_SERVICE_KEY':runtime['service_key'],'SUPABASE_URL':provider['api'],'SUPABASE_ANON_KEY':provider['anon_key']}
    with patch.dict(os.environ,env):
        return create_app(object(),studies_db=AsyncDatabase(urls['access_studies_runtime']),studies_identity_db=AsyncDatabase(urls['identity_studies_reader_runtime']),studies_setup_db=AsyncDatabase(urls['identity_studies_setup_runtime']))

async def runtime_checks():
    """Retained exploratory seven-request candidate; not the final qualification oracle.

    Its initial all-success failure remains historical. Final first-use proof uses
    first_use_race on a fresh subject and does not reinterpret that failure.
    """
    import httpx
    provider=json.loads((PROOF/'provider.json').read_text());runtime=json.loads((PROOF/'runtime.json').read_text())
    app=runtime_app();headers={'Authorization':'Bearer '+provider['token'],'X-Service-Key':runtime['service_key']}
    operation=str(uuid4())
    write_private(PROOF/('runtime-operation-'+uuid4().hex+'.json'),{'operation_id':operation})
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as client:
        # Both absent actor mapping and absent grant race on first use.
        operations=[operation]*3+[str(uuid4()) for _ in range(4)]
        initial=await asyncio.gather(*(client.post('/v2/enrollments/scribeswell-studies',headers=headers,json={'operation_id':item}) for item in operations))
        write_private(PROOF/('initial-concurrency-'+uuid4().hex+'.json'),{'operations':operations,'responses':[{'status':response.status_code,'body':response.json()} for response in initial]})
        assert all(response.status_code==200 for response in initial),'concurrent_first_enrollment_failed'
        assert initial[0].json()==initial[1].json()==initial[2].json(),'same_operation_race_changed_ack'
        created={item for item,response in zip(operations,initial) if response.json()['result']['disposition']=='created'}
        assert len(created)==1,'initial_assignment_not_unique'
        first=initial[0]
        write_private(PROOF/('runtime-first-'+uuid4().hex+'.json'),{'status':first.status_code,'body':first.json()})
        assert first.status_code==200,'zero_membership_enrollment_failed'
        assert first.json()['result']['account_id']==provider['account'] and first.json()['result']['actor_id']==provider['account']
        replay=await client.post('/v2/enrollments/scribeswell-studies',headers=headers,json={'operation_id':operation})
        assert replay.status_code==200 and replay.json()==first.json(),'original_receipt_not_retained'
        decision=await client.post('/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
        assert decision.status_code==200 and len(decision.json())==6,'canonical_account_check_failed'
        assert decision.headers['cache-control']=='private, no-store'
        concurrent=await asyncio.gather(*(client.post('/v2/enrollments/scribeswell-studies',headers=headers,json={'operation_id':str(uuid4())}) for _ in range(5)))
        assert all(response.status_code==200 and response.json()['result']['disposition']=='unchanged' for response in concurrent),'concurrent_enrollment_failed'
    write_private(PROOF/'runtime-success.json',{'account':provider['account'],'operation_id':operation,'zero_membership_enrollment':True,'replay':True,'canonical_check':True,'concurrent_distinct_operations':5,'concurrent_initial_same_operation_requests':3,'concurrent_initial_distinct_operations':5,'exactly_one_created_operation':True})

def refresh_candidate_reference():
    sys.path.insert(0,str(ACCESS/'identity-migrations'))
    import identity_baseline as baseline,identity_studies_catalog as catalog
    db=engine(owner_url('upgrade','identity'))
    with db.connect() as c:
        c.exec_driver_sql('SET TRANSACTION READ ONLY')
        content={'migration_sha256':sha256((ACCESS/'identity-migrations/versions/0021_studies_account_setup.py').read_bytes()).hexdigest(),'catalog':baseline.catalog_fingerprints(catalog.snapshot(c))}
    db.dispose()
    path=ACCESS/'identity-migrations/studies-setup-reference.json'
    old=path.read_bytes();write_private(PROOF/('prior-candidate-reference-'+uuid4().hex+'.json'),json.loads(old))
    path.write_text(json.dumps(content,sort_keys=True,indent=2)+'\n')
    digest=sha256(path.read_bytes()).hexdigest();support=ACCESS/'identity-migrations/identity_studies_catalog.py'
    import re
    support.write_text(re.sub(r"REFERENCE_SHA256='[a-f0-9]+'", "REFERENCE_SHA256='"+digest+"'",support.read_text()))
    catalog.REFERENCE_SHA256=digest
    db=engine(owner_url('upgrade','identity'))
    with db.connect() as c:
        c.exec_driver_sql('SET TRANSACTION READ ONLY');baseline.verify_owned_postcondition(c,require_head=True)
    db.dispose()

def cli_proofs(case='failure',prefix='cli'):
    import subprocess
    results=[]
    def run(owner,label,fail=False,expected=True):
        directory=ACCESS/('identity-migrations' if owner=='identity' else 'migrations')
        ini=ACCESS/('identity-alembic.ini' if owner=='identity' else 'alembic.ini')
        module='identity_baseline' if owner=='identity' else 'access_baseline'
        function='verify_owned_postcondition' if owner=='identity' else 'verify_postcondition'
        code="import sys;sys.path.insert(0,"+repr(str(directory))+");from alembic.config import Config;from alembic import command;"
        if fail:
            code+='import '+module+' as baseline;'
            code+='original=baseline.'+function+';'
            code+='exec('+repr("def fail(c,*args,**kwargs):\n original(c,*args,**kwargs)\n raise RuntimeError('synthetic_postcondition_failure')\n")+');'
            code+='baseline.'+function+'=fail;'
        code+=f"command.upgrade(Config({str(ini)!r}), 'head')"
        environment={'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8',owner.upper()+'_MIGRATION_DATABASE_URL':owner_url(case,owner).set(drivername='postgresql+psycopg').render_as_string(hide_password=False)}
        result=subprocess.run([sys.executable,'-I','-B','-c',code],env=environment,capture_output=True,timeout=45,cwd=ROOT)
        path=PROOF/(prefix+'-'+label+'.log');path.write_bytes(result.stdout+result.stderr);path.chmod(0o600)
        assert (result.returncode==0)==expected,'cli_result_mismatch:'+label
        results.append({'stage':label,'exit_code':result.returncode,'log_sha256':sha256(path.read_bytes()).hexdigest()})
    # Access refuses when the separately owned Identity prerequisite is absent.
    run('access','cli-access-before-identity',expected=False)
    run('identity','cli-identity-failure',fail=True,expected=False)
    db=engine(owner_url(case,'identity'))
    with db.connect() as c:assert c.exec_driver_sql('SELECT version_num FROM identity.alembic_version').scalar_one()=='identity_0020'
    db.dispose()
    run('identity','cli-identity-upgrade');run('identity','cli-identity-repeat')
    run('access','cli-access-failure',fail=True,expected=False)
    db=engine(owner_url(case,'access'))
    with db.connect() as c:assert c.exec_driver_sql('SELECT version_num FROM access.alembic_version').scalar_one()=='access_0015'
    db.dispose()
    run('access','cli-access-upgrade');run('access','cli-access-repeat')
    write_private(PROOF/(prefix+'-proof.json'),{'results':results,'activation_executed':False,'failure_ledgers_preserved':True,'source_populated_upgrade':True})

def prepare_final():
    source=inputs();PROOF.mkdir(mode=0o700,parents=True,exist_ok=False)
    original=json.loads((INITIAL_PROOF/'private.json').read_text())
    private={'source_database':source.database,'databases':{},'passwords':original['passwords']}
    with connect(source.set(username='supabase_admin',database='postgres'),True) as c:
        for role in ROLES:
            row=c.execute('SELECT rolsuper,rolinherit,rolcreatedb,rolcreaterole,rolcanlogin,rolreplication,rolbypassrls FROM pg_roles WHERE rolname=%s',(role,)).fetchone()
            assert row==(False,False,False,False,role.endswith('_runtime'),False,False)
        for case in ('upgrade','failure'):
            name='ida_'+RUN.replace('-','')[:12]+'_studies_final_'+uuid4().hex[:10]+'_'+case
            c.execute(sql.SQL('CREATE DATABASE {} WITH TEMPLATE {}').format(sql.Identifier(name),sql.Identifier(source.database)))
            private['databases'][case]=name
    write_private(PROOF/'private.json',private)
    attempt=max(INITIAL_PROOF.glob('provider-attempt-*.json'),key=lambda path:path.stat().st_mtime)
    write_private(PROOF/'provider-attempt-retained.json',json.loads(attempt.read_text()))
    bootstrap_auth()

async def boundaries():
    import time,httpx
    sys.path.insert(0,str(ACCESS))
    from studies_identity import AsyncDatabase,evidence,prepare,transaction,StudiesFailure
    provider=json.loads((PROOF/'provider.json').read_text());runtime=json.loads((PROOF/'runtime.json').read_text());urls=runtime_urls()
    subjects={name:str(uuid4()) for name in ('partial','adopted','collision','unverified','deleted')}
    write_private(PROOF/'boundary-subjects.json',subjects)
    source=inputs();private=json.loads((PROOF/'private.json').read_text());admin=source.set(username='supabase_admin',database=private['databases']['upgrade'])
    with connect(admin) as c:
        for name,account in subjects.items():
            verified=None if name=='unverified' else '2026-01-01T00:00:00Z'
            c.execute('INSERT INTO auth.users(id,email,deleted_at,email_confirmed_at,banned_until,is_anonymous) VALUES(%s,%s,NULL,%s,NULL,false)',(account,'studies-'+name+'-'+uuid4().hex+'@example.invalid',verified))
        c.execute('UPDATE auth.users SET deleted_at=statement_timestamp() WHERE id=%s',(subjects['deleted'],))
    db=engine(owner_url('upgrade','identity'));adopted=str(uuid4())
    with db.begin() as c:
        for actor,kind,key in ((adopted,'account',None),(subjects['collision'],'system','studies.collision.'+uuid4().hex)):
            c.execute(text('INSERT INTO identity.actor(id,kind,display_name,actor_key,created_by,updated_by) VALUES(CAST(:actor AS uuid),:kind,:display,:key,CAST(:executor AS uuid),CAST(:executor AS uuid))'),{'actor':actor,'kind':kind,'display':'Synthetic boundary actor','key':key,'executor':runtime['service_actor']})
        c.execute(text("INSERT INTO identity.account_actor(account_id,actor_id,actor_kind,created_by) VALUES(CAST(:account AS uuid),CAST(:actor AS uuid),'account',CAST(:executor AS uuid))"),{'account':subjects['adopted'],'actor':adopted,'executor':runtime['service_actor']})
    db.dispose()
    reader=AsyncDatabase(urls['identity_studies_reader_runtime']);setup=AsyncDatabase(urls['identity_studies_setup_runtime']);access=AsyncDatabase(urls['access_studies_runtime'])
    assert await evidence(reader,__import__('uuid').UUID(subjects['partial']),time.monotonic()+3) is None
    operation=uuid4();actor=await prepare(setup,__import__('uuid').UUID(subjects['partial']),operation,time.monotonic()+3)
    assert str(actor)==subjects['partial']
    absent=await transaction(access,actor,time.monotonic()+3,'SELECT account_id,actor_id FROM access.check_studies_permission(:actor)',{'actor':actor},readonly=True)
    assert absent is None,'actor_setup_granted_permission'
    assert await prepare(setup,actor,operation,time.monotonic()+3)==actor,'partial_actor_not_reused'
    account=__import__('uuid').UUID(subjects['adopted'])
    assert str(await evidence(reader,account,time.monotonic()+3))==adopted
    assert str(await prepare(setup,account,uuid4(),time.monotonic()+3))==adopted,'adopted_actor_replaced'
    for name in ('collision','unverified','deleted'):
        try:await evidence(reader,__import__('uuid').UUID(subjects[name]),time.monotonic()+3)
        except StudiesFailure:pass
        else:raise AssertionError('ineligible_evidence_accepted:'+name)
        try:await prepare(setup,__import__('uuid').UUID(subjects[name]),uuid4(),time.monotonic()+3)
        except StudiesFailure:pass
        else:raise AssertionError('ineligible_setup_accepted:'+name)
    # Actual cancellation must close dedicated socket inside the total deadline.
    started=time.monotonic()
    try:await transaction(access,actor,started+.1,'SELECT pg_sleep(10)',readonly=True)
    except StudiesFailure:pass
    else:raise AssertionError('native_timeout_acknowledged')
    elapsed=time.monotonic()-started
    assert elapsed<1,'native_deadline_cleanup_overrun'
    # Fresh connections cannot retain another account or organization context.
    fresh=await transaction(access,actor,time.monotonic()+3,"SELECT current_setting('app.account_id') AS account,current_setting('app.org_id') AS org,current_setting('statement_timeout') AS statement",readonly=True)
    assert fresh['account']==str(actor) and fresh['org']=='' and fresh['statement']!='0'
    denials=[]
    for role in ('identity_studies_reader_runtime','identity_studies_setup_runtime','access_studies_runtime'):
        for statement in ('SELECT * FROM identity.users','SELECT * FROM identity.account_actor','SELECT * FROM access.studies_account_grant','SET ROLE identity_studies_owner','SET ROLE access_studies_owner'):
            try:
                with connect(make_url(urls[role])) as c:c.execute(statement)
            except psycopg.Error as error:
                assert error.sqlstate=='42501';denials.append((role,statement.split()[0]))
            else:raise AssertionError('runtime_raw_authority_bypass')
    # Drop an actual committed transport response; retry original operation only.
    app=runtime_app();headers={'Authorization':'Bearer '+provider['token'],'X-Service-Key':runtime['service_key']};lost=str(uuid4())
    class LostResponse(httpx.ASGITransport):
        async def handle_async_request(self,request):
            await super().handle_async_request(request)
            raise httpx.ReadError('synthetic_lost_response')
    async with httpx.AsyncClient(transport=LostResponse(app=app),base_url='http://synthetic') as client:
        try:await client.post('/v2/enrollments/scribeswell-studies',headers=headers,json={'operation_id':lost})
        except httpx.ReadError:pass
        else:raise AssertionError('lost_response_not_exercised')
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as client:
        retry=await client.post('/v2/enrollments/scribeswell-studies',headers=headers,json={'operation_id':lost})
        assert retry.status_code==200 and retry.json()['result']['disposition']=='unchanged'
        # Controlled revocation records actor and operation; no regrant API exists.
        db=engine(owner_url('upgrade','access'))
        with db.begin() as c:
            c.execute(text("UPDATE access.studies_account_grant SET revoked_at=statement_timestamp(),revoked_by=CAST(:actor AS uuid),revocation_operation_id=CAST(:operation AS uuid) WHERE account_id=CAST(:account AS uuid) AND revoked_at IS NULL"),{'actor':runtime['service_actor'],'operation':str(uuid4()),'account':provider['account']})
        db.dispose()
        replay=await client.post('/v2/enrollments/scribeswell-studies',headers=headers,json={'operation_id':lost})
        check=await client.post('/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
        assert replay.status_code==check.status_code==403,'revoked_grant_resurrected'
    with connect(admin) as c:
        assert c.execute('SELECT count(*) FROM access.studies_account_grant WHERE account_id=%s',(provider['account'],)).fetchone()[0]==1
        assert c.execute('SELECT count(*) FROM access.studies_assignment_event WHERE account_id=%s',(provider['account'],)).fetchone()[0]==1
        assert c.execute('SELECT count(*) FROM identity.studies_setup_event WHERE account_id=%s',(provider['account'],)).fetchone()[0]==1
    write_private(PROOF/'boundaries.json',{'subjects':subjects,'adopted_actor':adopted,'partial_actor_without_grant':True,'collision_unverified_deleted_refused':True,'actual_sql_timeout_seconds':elapsed,'fresh_context':True,'restricted_role_denials':denials,'lost_response_retry':True,'revoked_replay_denied':True,'one_initial_grant_event':True})

async def first_use_race(prefix='race'):
    import httpx,time
    provider=json.loads((PROOF/'provider.json').read_text());runtime=json.loads((PROOF/'runtime.json').read_text())
    api=provider['api'];email='studies-race-'+uuid4().hex+'@example.invalid'
    async with httpx.AsyncClient(timeout=3) as client:
        headers={'apikey':provider['service_key'],'Authorization':'Bearer '+provider['service_key']}
        response=await client.post(api+'/auth/v1/admin/users',headers=headers,json={'email':email,'email_confirm':True})
        assert response.status_code==200;account=response.json()['id']
        write_private(PROOF/(prefix+'-provider-created.json'),{'account':account,'email':email})
        response=await client.post(api+'/auth/v1/admin/generate_link',headers=headers,json={'type':'magiclink','email':email})
        assert response.status_code==200;value=response.json();hashed=value.get('hashed_token') or value['properties']['hashed_token']
        response=await client.post(api+'/auth/v1/verify',headers={'apikey':provider['anon_key']},json={'type':'magiclink','token_hash':hashed})
        assert response.status_code==200;token=response.json()['access_token']
        response=await client.get(api+'/auth/v1/user',headers={'apikey':provider['anon_key'],'Authorization':'Bearer '+token})
        assert response.status_code==200 and response.json()['id']==account;verified=response.json()['email_confirmed_at']
    write_private(PROOF/(prefix+'-provider-private.json'),{'account':account,'email':email,'token':token})
    source=inputs();private=json.loads((PROOF/'private.json').read_text());admin=source.set(username='supabase_admin',database=private['databases']['upgrade'])
    with connect(admin) as c:
        c.execute('INSERT INTO auth.users(id,email,deleted_at,email_confirmed_at,banned_until,is_anonymous) VALUES(%s,%s,NULL,%s,NULL,false)',(account,email,verified))
        assert c.execute('SELECT count(*) FROM identity.account_actor WHERE account_id=%s',(account,)).fetchone()[0]==0
        assert c.execute('SELECT count(*) FROM access.studies_account_grant WHERE account_id=%s',(account,)).fetchone()[0]==0
    shared=str(uuid4());operations=[shared,shared,str(uuid4()),str(uuid4())]
    write_private(PROOF/(prefix+'-operation-inputs.json'),{'account':account,'operations':operations})
    app=runtime_app();headers={'Authorization':'Bearer '+token,'X-Service-Key':runtime['service_key']}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as client:
        started=time.monotonic()
        initial=await asyncio.gather(*(client.post('/v2/enrollments/scribeswell-studies',headers=headers,json={'operation_id':operation}) for operation in operations))
        write_private(PROOF/(prefix+'-initial-responses.json'),{'elapsed':time.monotonic()-started,'responses':[{'status':r.status_code,'body':r.json()} for r in initial]})
        assert all(response.status_code==200 for response in initial),'first_race_unavailable_requires_diagnosis'
        acknowledged=[]
        for operation in operations:
            response=await client.post('/v2/enrollments/scribeswell-studies',headers=headers,json={'operation_id':operation})
            assert response.status_code==200,'first_race_original_retry_failed'
            acknowledged.append(response.json())
        assert acknowledged[0]==acknowledged[1],'same_operation_race_different_result'
        assert len({value['operation_id'] for value in acknowledged if value['result']['disposition']=='created'})==1
        for first,ack in zip(initial,acknowledged):
            if first.status_code==200:assert first.json()==ack,'original_success_disposition_changed'
        decision=await client.post('/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
        assert decision.status_code==200 and decision.json()['actor_id']==account
    with connect(admin) as c:
        for table,column in (('access.studies_account_grant','account_id'),('access.studies_assignment_event','account_id'),('identity.studies_setup_event','account_id')):
            assert c.execute(sql.SQL('SELECT count(*) FROM {} WHERE {}=%s').format(sql.SQL(table),sql.Identifier(column)),(account,)).fetchone()[0]==1
        assert c.execute('SELECT count(*) FROM identity.org_member WHERE user_id=%s',(account,)).fetchone()[0]==0
    write_private(PROOF/('first-use-race.json' if prefix=='race' else 'current-first-use-race.json'),{'account':account,'initial_statuses':[response.status_code for response in initial],'original_acknowledgements':acknowledged,'first_use_absent_actor_and_grant':True,'one_initial_grant_event_and_actor_event':True,'zero_memberships':True,'canonical_check':True})

def clean_upgrade(label='clean'):
    import subprocess
    source=inputs();name='ida_'+RUN.replace('-','')[:12]+'_studies_clean_'+uuid4().hex[:10]
    write_private(PROOF/(label+'-database.json'),{'database':name,'run_id':RUN})
    with connect(source.set(username='supabase_admin',database='postgres'),True) as c:
        c.execute(sql.SQL('CREATE DATABASE {} OWNER postgres').format(sql.Identifier(name)))
        c.execute(sql.SQL('GRANT CREATE ON DATABASE {} TO identity_migrator').format(sql.Identifier(name)))
    admin=source.set(username='supabase_admin',database=name)
    helpers=json.loads((PRIOR/'auth-helper-definitions.json').read_text())['native']
    assert len(helpers)==2 and {definition.splitlines()[0] for definition in helpers}=={'CREATE OR REPLACE FUNCTION auth.uid()','CREATE OR REPLACE FUNCTION auth.jwt()'}
    with connect(admin) as c:
        c.execute('CREATE SCHEMA auth;CREATE SCHEMA extensions;CREATE EXTENSION "uuid-ossp" WITH SCHEMA extensions')
        c.execute('CREATE TABLE auth.users(id uuid PRIMARY KEY,email text,raw_app_meta_data jsonb,raw_user_meta_data jsonb,created_at timestamptz,deleted_at timestamptz,email_confirmed_at timestamptz,banned_until timestamptz,is_anonymous boolean)')
        c.execute("CREATE FUNCTION auth.jwt() RETURNS jsonb LANGUAGE sql STABLE AS $$ SELECT coalesce(nullif(current_setting('request.jwt.claims',true),''),'{}')::jsonb $$")
        c.execute("CREATE FUNCTION auth.uid() RETURNS uuid LANGUAGE sql STABLE AS $$ SELECT nullif(auth.jwt()->>'sub','')::uuid $$")
        c.execute("CREATE FUNCTION auth.role() RETURNS text LANGUAGE sql STABLE AS $$ SELECT coalesce(auth.jwt()->>'role',current_user::text) $$")
        for definition in helpers:c.execute(definition)
        c.execute('GRANT USAGE ON SCHEMA auth,extensions TO identity_migrator;GRANT USAGE ON SCHEMA auth TO identity_migrator WITH GRANT OPTION;GRANT SELECT(id),REFERENCES(id),TRIGGER ON auth.users TO identity_migrator;GRANT CREATE,USAGE ON SCHEMA public TO identity_migrator')
        c.execute('GRANT USAGE ON SCHEMA auth TO identity_account_verification_owner;GRANT SELECT(id,deleted_at) ON auth.users TO identity_account_verification_owner;ALTER TABLE auth.users ENABLE ROW LEVEL SECURITY;CREATE POLICY identity_account_actor_verification ON auth.users FOR SELECT TO identity_account_verification_owner USING(true)')
        c.execute('GRANT USAGE ON SCHEMA auth TO identity_studies_owner;GRANT SELECT(id,deleted_at,email_confirmed_at,banned_until,is_anonymous) ON auth.users TO identity_studies_owner')
        c.execute("CREATE POLICY studies_current_account ON auth.users FOR SELECT TO identity_studies_owner USING(id::text=current_setting('app.account_id',true))")
        c.execute('ALTER SCHEMA auth OWNER TO postgres;ALTER TABLE auth.users OWNER TO postgres')
        c.execute('CREATE SCHEMA access AUTHORIZATION access_migrator;SET ROLE access_migrator;GRANT USAGE ON SCHEMA access TO access_runtime;RESET ROLE')
    prior=json.loads((PRIOR/'credentials.json').read_text())
    identity=make_url(prior['owner_urls']['bridge']).set(database=name)
    with connect(identity) as c:c.execute('CREATE SCHEMA identity')
    with connect(source.set(username='supabase_admin',database='postgres'),True) as c:c.execute(sql.SQL('REVOKE CREATE ON DATABASE {} FROM identity_migrator').format(sql.Identifier(name)))
    results=[]
    for owner in ('identity','access'):
        url=make_url(prior['owner_urls' if owner=='identity' else 'access_owner_urls']['bridge']).set(database=name,drivername='postgresql+psycopg')
        config=ACCESS/('identity-alembic.ini' if owner=='identity' else 'alembic.ini')
        env={'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8',owner.upper()+'_MIGRATION_DATABASE_URL':url.render_as_string(hide_password=False)}
        result=subprocess.run([sys.executable,'-I','-B','-m','alembic','-c',str(config),'upgrade','head'],env=env,cwd=ROOT,capture_output=True,timeout=120)
        log=PROOF/(label+'-'+owner+'.log');log.write_bytes(result.stdout+result.stderr);log.chmod(0o600)
        assert result.returncode==0,'clean_owner_upgrade_failed:'+owner
        results.append({'owner':owner,'exit_code':0,'log_sha256':sha256(log.read_bytes()).hexdigest()})
    with connect(admin) as c:
        assert c.execute('SELECT version_num FROM identity.alembic_version').fetchone()[0]=='identity_0021'
        assert c.execute('SELECT version_num FROM access.alembic_version').fetchone()[0]=='access_0016'
        assert c.execute('SELECT count(*) FROM identity.actor').fetchone()[0]==0
        assert c.execute('SELECT count(*) FROM access.studies_account_grant').fetchone()[0]==0
    write_private(PROOF/(label+'-upgrade-proof.json'),{'database':name,'empty_owner_histories':True,'no_account_or_grant_seeds':True,'ordered_owner_results':results,'auth_helper_source_sha256':sha256((PRIOR/'auth-helper-definitions.json').read_bytes()).hexdigest()})

async def current_denials():
    import time,httpx
    sys.path.insert(0,str(ACCESS))
    from studies_identity import AsyncDatabase,evidence,prepare,transaction,StudiesFailure
    from access_operator import execute
    names=('banned','missing_profile','deleted_profile','system_profile','keyed_profile')
    subjects={name:str(uuid4()) for name in names};write_private(PROOF/'current-denial-subjects.json',subjects)
    source=inputs();private=json.loads((PROOF/'private.json').read_text());admin=source.set(username='supabase_admin',database=private['databases']['upgrade'])
    with connect(admin) as c:
        for name,account in subjects.items():
            c.execute('INSERT INTO auth.users(id,email,deleted_at,email_confirmed_at,banned_until,is_anonymous) VALUES(%s,%s,NULL,%s,NULL,false)',(account,'studies-current-'+uuid4().hex+'@example.invalid','2026-01-01T00:00:00Z'))
        c.execute("UPDATE auth.users SET banned_until='9999-01-01T00:00:00Z' WHERE id=%s",(subjects['banned'],))
    owner=engine(owner_url('upgrade','identity'))
    with owner.begin() as c:
        c.execute(text('DELETE FROM identity.users WHERE id=CAST(:account AS uuid)'),{'account':subjects['missing_profile']})
        c.execute(text('UPDATE identity.users SET deleted_at=statement_timestamp() WHERE id=CAST(:account AS uuid)'),{'account':subjects['deleted_profile']})
        c.execute(text('UPDATE identity.users SET is_system=true WHERE id=CAST(:account AS uuid)'),{'account':subjects['system_profile']})
        c.execute(text('UPDATE identity.users SET actor_key=:key WHERE id=CAST(:account AS uuid)'),{'account':subjects['keyed_profile'],'key':'studies.synthetic.'+uuid4().hex})
    owner.dispose();urls=runtime_urls();reader=AsyncDatabase(urls['identity_studies_reader_runtime']);setup=AsyncDatabase(urls['identity_studies_setup_runtime'])
    for name,account in subjects.items():
        for call in (lambda: evidence(reader,__import__('uuid').UUID(account),time.monotonic()+3),lambda:prepare(setup,__import__('uuid').UUID(account),uuid4(),time.monotonic()+3)):
            try:await call()
            except StudiesFailure:pass
            else:raise AssertionError('current_profile_refusal_missing:'+name)
    # Supported protected availability commands retain registry audit/outcomes.
    prior=json.loads((PRIOR/'credentials.json').read_text());operator=engine(make_url(prior['access_operator_urls']['bridge']).set(database=private['databases']['upgrade']))
    def enabled(value,revision):
        envelope={'schema_version':1,'operation_id':str(uuid4()),'command':'application.set_enabled','scope':{'kind':'platform'},'payload':{'app_id':'scribeswell','enabled':value,'expected_revision':revision},'reason_code':'synthetic_fixture','evidence_ref':'synthetic:studies-availability'}
        with operator.connect() as c:receipt=execute(c,json.dumps(envelope).encode())
        write_private(PROOF/('availability-'+uuid4().hex+'.json'),{'command':envelope,'receipt':receipt})
    provider=json.loads((PROOF/'provider.json').read_text());race=json.loads((PROOF/'race-provider-private.json').read_text());runtime=json.loads((PROOF/'runtime.json').read_text())
    app=runtime_app();headers={'Authorization':'Bearer '+race['token'],'X-Service-Key':runtime['service_key']}
    operation=json.loads((PROOF/'race-operation-inputs.json').read_text())['operations'][0]
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as client:
        baseline=await client.post('/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
        assert baseline.status_code==200,'availability_positive_precondition_failed'
        enabled(False,'2')
        try:
            for body in ({'operation_id':operation},{'operation_id':str(uuid4())}):
                response=await client.post('/v2/enrollments/scribeswell-studies',headers=headers,json=body)
                assert response.status_code==403 and response.json()['error_id']=='access_denied'
            response=await client.post('/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
            assert response.status_code==403
        finally:enabled(True,'3')
    operator.dispose()
    # A timeout while blocked at the SQL command boundary cannot create a receipt.
    partial=json.loads((PROOF/'boundary-subjects.json').read_text())['partial'];actor=__import__('uuid').UUID(partial);operation=uuid4();access=AsyncDatabase(urls['access_studies_runtime'])
    with connect(make_url(owner_url('upgrade','access'))) as blocker:
        blocker.execute("SELECT pg_advisory_xact_lock(hashtextextended('access:studies-account:v1:'||%s,0))",(partial,))
        started=time.monotonic()
        try:await transaction(access,actor,started+.2,'SELECT disposition,account_id,actor_id FROM access.enroll_studies_account(:operation,:actor)',{'operation':operation,'actor':actor})
        except StudiesFailure:pass
        else:raise AssertionError('blocked_command_acknowledged')
        elapsed=time.monotonic()-started;assert elapsed<1
    with connect(admin) as c:
        assert c.execute('SELECT count(*) FROM access.studies_enrollment_outcome WHERE account_id=%s AND operation_id=%s',(partial,operation)).fetchone()[0]==0
        assert c.execute('SELECT count(*) FROM access.studies_account_grant WHERE account_id=%s',(partial,)).fetchone()[0]==0
    assert await evidence(reader,actor,time.monotonic()+3)==actor
    retry=await transaction(access,actor,time.monotonic()+3,'SELECT disposition,account_id,actor_id FROM access.enroll_studies_account(:operation,:actor)',{'operation':operation,'actor':actor})
    assert retry['disposition']=='created'
    write_private(PROOF/'current-denials.json',{'subjects':subjects,'banned_missing_deleted_system_keyed_refused':True,'disabled_check_new_enrollment_replay_denied':True,'availability_restored_by_protected_command':True,'write_lock_timeout_seconds':elapsed,'uncommitted_outcome_and_grant_absent':True,'same_operation_retry_after_fresh_evidence':True})

def amend_refusal_contract():
    sys.path.insert(0,str(ACCESS/'identity-migrations'))
    migration=load_module('_studies_identity_refusal_ddl',ACCESS/'identity-migrations/versions/0021_studies_account_setup.py')
    import re
    db=engine(owner_url('upgrade','identity'))
    with db.begin() as c:
        c.exec_driver_sql('GRANT CREATE ON SCHEMA identity TO identity_studies_owner;SET LOCAL ROLE identity_studies_owner')
        for name in ('studies_account_evidence','prepare_studies_account'):
            definition=re.search(r'CREATE FUNCTION identity\.'+name+r'\(.*?\$f\$;',migration.SQL,re.S).group()
            c.exec_driver_sql(definition.replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1),execution_options={'no_parameters':True})
        c.exec_driver_sql('RESET ROLE;REVOKE CREATE ON SCHEMA identity FROM identity_studies_owner')
    db.dispose();refresh_candidate_reference()

async def confirmed_http_denials():
    import httpx
    provider=json.loads((PROOF/'provider.json').read_text());runtime=json.loads((PROOF/'runtime.json').read_text())
    source=inputs();private=json.loads((PROOF/'private.json').read_text());admin=source.set(username='supabase_admin',database=private['databases']['upgrade'])
    app=runtime_app();headers={'Authorization':'Bearer '+provider['token'],'X-Service-Key':runtime['service_key']};results=[]
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as client:
        # Local authoritative denial must override a still-valid live provider observation.
        for assignment,status,code in (("email_confirmed_at=NULL",403,'identity.verification_required'),("email_confirmed_at='2026-01-01T00:00:00Z',banned_until='9999-01-01T00:00:00Z'",403,'access_denied')):
            with connect(admin) as c:c.execute(sql.SQL('UPDATE auth.users SET '+assignment+' WHERE id=%s'),(provider['account'],))
            for path,body in (('/v2/enrollments/scribeswell-studies',{'operation_id':str(uuid4())}),('/v2/check',{'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})):
                response=await client.post(path,headers=headers,json=body)
                assert response.status_code==status and response.json()['error_id']==code,'confirmed_http_denial_mapping_failed'
                results.append({'path':path,'status':status,'error_id':code})
    write_private(PROOF/'confirmed-http-denials.json',{'results':results,'live_provider_still_verified':True,'local_current_auth_denial_precedes_retained_grant':True})

def current_source_upgrades():
    source=inputs();name='ida_'+RUN.replace('-','')[:12]+'_studies_current_'+uuid4().hex[:10]
    write_private(PROOF/'current-populated-database.json',{'database':name,'source_database':source.database,'run_id':RUN})
    with connect(source.set(username='supabase_admin',database='postgres'),True) as c:
        c.execute(sql.SQL('CREATE DATABASE {} WITH TEMPLATE {}').format(sql.Identifier(name),sql.Identifier(source.database)))
    with connect(source.set(username='supabase_admin',database=name)) as c:
        for field,type_ in (('email_confirmed_at','timestamp with time zone'),('banned_until','timestamp with time zone'),('is_anonymous','boolean')):
            c.execute(sql.SQL('ALTER TABLE auth.users ADD COLUMN IF NOT EXISTS {} {}').format(sql.Identifier(field),sql.SQL(type_)))
        c.execute('GRANT USAGE ON SCHEMA auth TO identity_studies_owner;GRANT SELECT(id,deleted_at,email_confirmed_at,banned_until,is_anonymous) ON auth.users TO identity_studies_owner')
        c.execute("CREATE POLICY studies_current_account ON auth.users FOR SELECT TO identity_studies_owner USING(id::text=current_setting('app.account_id',true))")
    cli_proofs(case='current-populated',prefix='current-cli')
    clean_upgrade(label='current-clean')

async def lock_eligibility():
    """Committed Auth changes during either existing advisory wait must deny."""
    import time
    from uuid import UUID
    sys.path.insert(0,str(ACCESS))
    from studies_identity import AsyncDatabase,prepare,StudiesFailure
    source=inputs();private=json.loads((PROOF/'private.json').read_text())
    admin=source.set(username='supabase_admin',database=private['databases']['upgrade'])
    setup=AsyncDatabase(runtime_urls()['identity_studies_setup_runtime'])
    results=[]
    for replay in (False,True):
        for namespace in ('account-actor','actor-id'):
            if replay and namespace=='actor-id':continue # adopted mapping takes only account lock
            for change in ('banned_until','deleted_at','email_confirmed_at'):
                account=uuid4();operation=uuid4()
                with connect(admin) as c:
                    c.execute('INSERT INTO auth.users(id,email,email_confirmed_at,is_anonymous) VALUES(%s,%s,statement_timestamp(),false)',(account,'studies-lock-'+uuid4().hex+'@example.invalid'))
                if replay:assert await prepare(setup,account,operation,time.monotonic()+3)==account
                with connect(admin) as holder:
                    holder.execute("SELECT pg_advisory_xact_lock(identity.command_lock(%s))",('identity:'+namespace+':v1:'+str(account),))
                    task=asyncio.create_task(prepare(setup,account,operation,time.monotonic()+3))
                    blocked=False
                    for _ in range(100):
                        await asyncio.sleep(.005)
                        with connect(admin,True) as observer:
                            blocked=observer.execute("SELECT EXISTS(SELECT 1 FROM pg_stat_activity WHERE usename='identity_studies_setup_runtime' AND wait_event='advisory' AND datname=current_database())").fetchone()[0]
                        if blocked:break
                    assert blocked,'setup_did_not_wait_on_expected_lock'
                    value=None if change=='email_confirmed_at' else ('2100-01-01T00:00:00Z' if change=='banned_until' else '2026-01-01T00:00:00Z')
                    holder.execute(sql.SQL('UPDATE auth.users SET {}=%s WHERE id=%s').format(sql.Identifier(change)),(value,account))
                    holder.commit()
                try:
                    await task
                    outcome='accepted'
                except StudiesFailure as error:outcome=error.error_id
                with connect(admin) as c:
                    counts=c.execute('SELECT (SELECT count(*) FROM identity.account_actor WHERE account_id=%s),(SELECT count(*) FROM identity.studies_setup_outcome WHERE account_id=%s)',(account,account)).fetchone()
                results.append({'lock':namespace,'change':change,'replay':replay,'wait_observed':blocked,'outcome':outcome,'counts':list(counts)})
    refused=all(row['outcome']==('identity.verification_required' if row['change']=='email_confirmed_at' else 'access_denied') for row in results)
    absent=all(row['counts']==([1,1] if row['replay'] else [0,0]) for row in results)
    write_private(PROOF/'lock-eligibility.json',{'results':results,'account_and_actor_locks_observed':all(row['wait_observed'] for row in results),'ban_delete_unverify_refused':refused,'no_actor_or_receipt_written':absent,'replay_denied':all(row['outcome']!='accepted' for row in results if row['replay'])})
    assert refused and absent,'auth_change_during_lock_wait_was_missed'

def source_hashes():
    sys.path.insert(0,str(ACCESS))
    from studies_readiness import source_hashes as authoritative_sources
    return authoritative_sources()

def retain_qualification():
    sys.path.insert(0,str(ACCESS))
    from studies_readiness import runtime_hashes
    from studies_readiness import STAGE_FIELDS,validate_stage_proofs
    sources=source_hashes()
    required=tuple(STAGE_FIELDS)
    proof={name:json.loads((PROOF/name).read_text()) for name in required}
    cases=validate_stage_proofs(proof,sources)
    record={'runtime_sources':runtime_hashes(),'sources':sources,'cases':cases,
        'proof_sha256':{name:sha256((PROOF/name).read_bytes()).hexdigest() for name in required},
        'logs_sha256':{path.name:sha256(path.read_bytes()).hexdigest() for path in sorted(PROOF.glob('*.log'))}}
    write_private(PROOF/'qualification.json',record)

async def readiness_proof():
    sys.path.insert(0,str(ACCESS))
    import httpx
    from unittest.mock import patch
    from studies_readiness import prepare as prepare_readiness
    from main import create_app
    artifact=prepare_readiness(owner_url('upgrade','identity').set(drivername='postgresql+psycopg').render_as_string(hide_password=False),owner_url('upgrade','access').set(drivername='postgresql+psycopg').render_as_string(hide_password=False),PROOF/'qualification.json','synthetic-studies-20261023')
    write_private(PROOF/'readiness.json',artifact)
    provider=json.loads((PROOF/'provider.json').read_text());race=json.loads((PROOF/'race-provider-private.json').read_text());runtime=json.loads((PROOF/'runtime.json').read_text());urls=runtime_urls()
    env={'SCRIBESWELL_SERVICE_KEY':runtime['service_key'],'SUPABASE_URL':provider['api'],'SUPABASE_ANON_KEY':provider['anon_key'],
        'STUDIES_ACCESS_DATABASE_URL':urls['access_studies_runtime'],'STUDIES_IDENTITY_DATABASE_URL':urls['identity_studies_reader_runtime'],'STUDIES_IDENTITY_SETUP_DATABASE_URL':urls['identity_studies_setup_runtime']}
    with patch.dict(os.environ,env):
        try:create_app()
        except RuntimeError:pass
        else:raise AssertionError('unprepared_default_activation_allowed')
    env['STUDIES_READINESS_JSON']=json.dumps(artifact)
    with patch.dict(os.environ,env):app=create_app()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as client:
        headers={'X-Service-Key':runtime['service_key'],'Authorization':'Bearer '+race['token']}
        response=await client.post('/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
        assert response.status_code==200 and len(response.json())==6,'prepared_default_account_check_failed'
        headers['Authorization']='Bearer '+provider['token']
        response=await client.post('/v2/check',headers=headers,json={'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
        assert response.status_code==403 and response.json()['error_id']=='access_denied'
    write_private(PROOF/'readiness-proof.json',{'default_unprepared_activation_refused':True,'owner_readiness_matched_service_executor':True,'prepared_default_six_field_check':True,'confirmed_auth_denial':True,'runtime_sources':artifact['runtime_sources']})

def verify_retained():
    record=json.loads((PROOF/'qualification.json').read_text())
    from studies_readiness import validate_qualification
    validate_qualification(record,PROOF)
    for name,digest in record['proof_sha256'].items():assert sha256((PROOF/name).read_bytes()).hexdigest()==digest,'qualification_proof_changed'
    for name,digest in record['logs_sha256'].items():assert sha256((PROOF/name).read_bytes()).hexdigest()==digest,'qualification_log_changed'
    # Independent SQL inspection uses owner-authorized read-only transactions;
    # it never trusts the HTTP responses as grant/attribution evidence.
    private=json.loads((PROOF/'private.json').read_text());source=inputs()
    with connect(source.set(username='supabase_admin',database=private['databases']['upgrade'])) as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT version_num FROM identity.alembic_version').fetchone()[0]=='identity_0021'
        assert c.execute('SELECT version_num FROM access.alembic_version').fetchone()[0]=='access_0016'
        assert c.execute("SELECT count(*) FROM access.studies_account_grant g JOIN access.studies_assignment_event e USING(account_id) WHERE g.actor_id<>e.actor_id OR g.executor_actor_id<>e.executor_actor_id OR g.initiator_actor_id<>e.initiator_actor_id").fetchone()[0]==0
        assert c.execute("SELECT count(*) FROM access.studies_account_grant g WHERE NOT EXISTS(SELECT 1 FROM access.studies_assignment_event e WHERE e.account_id=g.account_id)").fetchone()[0]==0
        assert c.execute("SELECT count(*) FROM identity.studies_setup_event e JOIN identity.account_actor a USING(account_id) WHERE e.actor_id<>a.actor_id OR e.initiator_actor_id<>a.actor_id").fetchone()[0]==0
        assert c.execute("SELECT executor_actor_id FROM identity.studies_runtime_principal WHERE enabled").fetchone()==c.execute("SELECT executor_actor_id FROM access.studies_runtime_principal WHERE enabled").fetchone()
    return True

def main():
    global EXECUTED_SOURCES
    EXECUTED_SOURCES=source_hashes()
    assert __debug__ and sys.argv[1:] in (['--prepare-final'],['--prepare'],['--resume-auth-bootstrap'],['--identity-reference'],['--access'],['--provider'],['--provider-link'],['--runtime-prepare'],['--registry-resume'],['--runtime'],['--refresh-candidate-reference'],['--cli-proofs'],['--boundaries'],['--first-use-race'],['--clean-upgrade'],['--current-denials'],['--amend-refusal-contract'],['--confirmed-http-denials'],['--current-source-upgrades'],['--retain-qualification'],['--readiness-proof'],['--verify-retained'],['--current-first-use-race'],['--lock-eligibility'])
    if sys.argv[1:]==['--prepare-final']:prepare_final()
    elif sys.argv[1:]==['--prepare']:prepare()
    elif sys.argv[1:]==['--resume-auth-bootstrap']:bootstrap_auth()
    elif sys.argv[1:]==['--identity-reference']:upgrade_identity(record=True)
    elif sys.argv[1:]==['--provider']:provider_fixture()
    elif sys.argv[1:]==['--provider-link']:provider_link()
    elif sys.argv[1:]==['--runtime-prepare']:runtime_prepare()
    elif sys.argv[1:]==['--registry-resume']:registry_prepare()
    elif sys.argv[1:]==['--runtime']:asyncio.run(runtime_checks())
    elif sys.argv[1:]==['--refresh-candidate-reference']:refresh_candidate_reference()
    elif sys.argv[1:]==['--cli-proofs']:cli_proofs()
    elif sys.argv[1:]==['--boundaries']:asyncio.run(boundaries())
    elif sys.argv[1:]==['--first-use-race']:asyncio.run(first_use_race())
    elif sys.argv[1:]==['--clean-upgrade']:clean_upgrade()
    elif sys.argv[1:]==['--current-denials']:asyncio.run(current_denials())
    elif sys.argv[1:]==['--amend-refusal-contract']:amend_refusal_contract()
    elif sys.argv[1:]==['--confirmed-http-denials']:asyncio.run(confirmed_http_denials())
    elif sys.argv[1:]==['--current-source-upgrades']:current_source_upgrades()
    elif sys.argv[1:]==['--retain-qualification']:retain_qualification()
    elif sys.argv[1:]==['--readiness-proof']:asyncio.run(readiness_proof())
    elif sys.argv[1:]==['--verify-retained']:verify_retained()
    elif sys.argv[1:]==['--lock-eligibility']:asyncio.run(lock_eligibility())
    elif sys.argv[1:]==['--current-first-use-race']:asyncio.run(first_use_race(prefix='current-race'))
    else:upgrade_access()
    print('studies_qualification_stage_passed')
if __name__=='__main__':
    try:main()
    except Exception as error:
        import traceback
        path=PROOF/('failure-'+uuid4().hex+'.log')
        PROOF.mkdir(parents=True,exist_ok=True)
        path.write_text(''.join(traceback.format_exception(error)));path.chmod(0o600)
        print('studies_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None
