"""Guarded synthetic Identity retained-display qualification; never uses retained targets.

All fixture inputs and raw failures remain private below the explicit proof directory.
Only this run's newly named container is started/stopped; no cleanup or downgrade.
"""
import argparse
import asyncio
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import time
from uuid import uuid4, UUID

ROOT = Path(__file__).resolve().parents[3]
ACCESS = ROOT/'services/access'
PYTHON = ACCESS/'.venv/bin/python'
ROLE = 'identity_actor_display_runtime'
PREDECESSOR_FRAME = None

def private(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.name!='private.json':
        path=path.with_name(path.stem+'-attempt-'+uuid4().hex+path.suffix)
    path.write_text(json.dumps(value, indent=2, default=str)+'\n'); path.chmod(0o600)

def command(argv, proof, label, env=None, cwd=ROOT, expected=0):
    result = subprocess.run([str(v) for v in argv], env=env, cwd=cwd, capture_output=True, timeout=180)
    log = proof/(label+'.log')
    if log.exists():log=proof/(label+'-attempt-'+uuid4().hex+'.log')
    log.write_bytes((b'private fixture metadata withheld\n' if label=='container-provenance' else result.stdout+result.stderr)); log.chmod(0o600)
    private(proof/(label+'.json'), {'argv': [str(v) for v in argv], 'exit_code': result.returncode, 'log_sha256': sha256(log.read_bytes()).hexdigest()})
    assert result.returncode == expected, label+'_failed_see_private_log'
    return result

def inputs(proof):
    path=proof/'private.json'
    assert path.stat().st_uid==os.getuid() and path.stat().st_mode & 0o077==0,'fixture_input_custody'
    value=json.loads(path.read_text())
    assert value['container'].startswith('identity-actor-native-') and value['database']=='actor_native_synthetic'
    return value

def conninfo(proof, role='postgres'):
    from psycopg.conninfo import make_conninfo
    p=inputs(proof)
    return make_conninfo(host='127.0.0.1', port=p['port'], dbname=p['database'], user=role, password=p['passwords'][role], application_name='actor-native-synthetic')

def connect(proof, role='postgres', **kwargs):
    import psycopg
    return psycopg.connect(conninfo(proof, role), **kwargs)

def url(proof):
    from sqlalchemy import URL
    p=inputs(proof)
    return URL.create('postgresql+psycopg',username='identity_migrator',password=p['passwords']['identity_migrator'],host='127.0.0.1',port=int(p['port']),database=p['database']).render_as_string(hide_password=False)

def upgrade(proof, source, label, expected=0):
    env={'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8','IDENTITY_MIGRATION_DATABASE_URL':url(proof),'PYTHONDONTWRITEBYTECODE':'1'}
    return command([PYTHON,'-I','-B','-m','alembic','-c',source/'services/access/identity-alembic.ini','upgrade','head'], proof,label,env=env,cwd=source,expected=expected)

def require_source27(capture):
    from alembic.script import ScriptDirectory
    migrations=capture/'services/access/identity-migrations'
    sys.path.insert(0,str(migrations))
    try:
        heads=ScriptDirectory(str(migrations)).get_heads()
    finally:
        sys.path.remove(str(migrations))
    assert heads==['identity_0027'],'captured_predecessor_head_must_be27'

def require_ledger27(proof):
    with connect(proof) as c:
        assert c.execute('SELECT version_num FROM identity.alembic_version').fetchall()==[('identity_0027',)],'qualified_predecessor_ledger_must_be27'

def record_predecessor27(proof):
    require_ledger27(proof)
    private(proof/'predecessor27.json',{'qualified_head':'identity_0027','fresh_synthetic':True,'auth_helpers':'scratch SQL stubs; not GoTrue/provider lifecycle'})

def prepare27(proof):
    assert not proof.exists(), 'proof_directory_must_be_new'
    proof.mkdir(parents=True,mode=0o700)
    capture=proof/'captured27'
    # Once28 exists, a fresh seeded repeat uses the already captured, independently
    # verified27 runner. The caller supplies that private frame explicitly.
    source_root=PREDECESSOR_FRAME/'captured27' if PREDECESSOR_FRAME else ROOT
    if PREDECESSOR_FRAME:assert (PREDECESSOR_FRAME/'predecessor27.json').is_file()
    source_access=source_root/'services/access'
    paths=list((source_access/'identity-migrations').rglob('*.py'))+list((source_access/'identity-migrations').glob('*.json'))+[source_access/'identity-alembic.ini',source_access/'tools/identity_bridge.sql']+list((source_root/'platform/supabase/migrations').glob('*.sql'))
    hashes={}
    for source in paths:
        target=capture/source.relative_to(source_root);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        hashes[str(source.relative_to(source_root))]=sha256(source.read_bytes()).hexdigest()
    private(proof/'captured27-sources.json',hashes)
    require_source27(capture)
    name='identity-actor-native-'+uuid4().hex[:16]
    # Historical ACL arrays follow grant-recipient OID order. Preserve the normal
    # Auth-before-owner preparation order without changing old catalogue evidence.
    roles=['postgres','anon','authenticated','service_role','supabase_auth_admin','identity_migrator','access_migrator',ROLE,'unauthorized_native','access_runtime','identity_operator','identity_studies_reader_runtime','identity_studies_setup_runtime','access_studies_runtime','identity_preferences_runtime','identity_people_setup_runtime']
    p={'container':name,'database':'actor_native_synthetic','passwords':{r:secrets.token_urlsafe(36) for r in roles}}
    private(proof/'private.json',p)
    envfile=proof/'postgres.env';envfile.write_text('POSTGRES_PASSWORD='+p['passwords']['postgres']+'\nPOSTGRES_DB='+p['database']+'\n');envfile.chmod(0o600)
    command(['docker','run','-d','--name',name,'--label','agriplatform.fixture=actor-native','--env-file',envfile,'-p','127.0.0.1::5432','postgres:17'],proof,'container-start')
    port=command(['docker','port',name,'5432/tcp'],proof,'container-port').stdout.decode().strip().split(':')[-1]
    p['port']=port;private(proof/'private.json',p)
    inspection=command(['docker','inspect',name],proof,'container-provenance')
    native=json.loads(inspection.stdout)[0]
    assert native['Config']['Labels']['agriplatform.fixture']=='actor-native'
    assert native['NetworkSettings']['Ports']['5432/tcp']==[{'HostIp':'127.0.0.1','HostPort':port}]
    p['container_id']=native['Id'];private(proof/'private.json',p)
    for _ in range(100):
        try:
            with connect(proof):pass
            break
        except Exception:time.sleep(.1)
    else:raise AssertionError('synthetic_postgres_not_ready')
    from psycopg import sql
    owners=['identity_account_projection_owner','identity_operator_authority_owner','identity_command_owner','identity_target_projection_owner','access_target_reader','access_setup_target_reader','access_command_owner','identity_account_verification_owner','access_check_reader','identity_studies_owner','access_studies_owner','access_capability_reader','identity_discovery_owner','access_discovery_owner']
    with connect(proof,autocommit=True) as c:
        for role in roles[1:]+owners:
            login=role in roles and role not in ('anon','authenticated','service_role')
            flags='{} {} NOSUPERUSER NOCREATEDB {} NOREPLICATION {}'.format('LOGIN' if login else 'NOLOGIN','INHERIT' if role in ('anon','authenticated','service_role') else 'NOINHERIT','CREATEROLE' if role=='supabase_auth_admin' else 'NOCREATEROLE','BYPASSRLS' if role=='service_role' else 'NOBYPASSRLS')
            c.execute(sql.SQL('CREATE ROLE {} {}').format(sql.Identifier(role),sql.SQL(flags)))
            if login:c.execute(sql.SQL('ALTER ROLE {} PASSWORD {}').format(sql.Identifier(role),sql.Literal(p['passwords'][role])))
        for owner in ['identity_account_projection_owner','identity_operator_authority_owner','identity_command_owner','identity_target_projection_owner','identity_account_verification_owner','identity_studies_owner','identity_discovery_owner']:
            c.execute(sql.SQL('GRANT {} TO identity_migrator WITH ADMIN FALSE,INHERIT FALSE,SET TRUE').format(sql.Identifier(owner)))
        for owner in ['access_capability_reader','access_discovery_owner','access_studies_owner']:
            c.execute(sql.SQL('GRANT {} TO access_migrator WITH ADMIN FALSE,INHERIT FALSE,SET TRUE').format(sql.Identifier(owner)))
        c.execute('GRANT identity_migrator TO postgres WITH ADMIN TRUE,INHERIT FALSE,SET FALSE')
        c.execute('CREATE SCHEMA auth;CREATE SCHEMA extensions;CREATE EXTENSION "uuid-ossp" WITH SCHEMA extensions')
        c.execute('CREATE TABLE auth.users(id uuid PRIMARY KEY,email text,raw_app_meta_data jsonb,raw_user_meta_data jsonb,created_at timestamptz,deleted_at timestamptz,email_confirmed_at timestamptz,banned_until timestamptz,is_anonymous boolean)')
        c.execute("CREATE FUNCTION auth.jwt() RETURNS jsonb LANGUAGE sql STABLE AS $$ SELECT coalesce(nullif(current_setting('request.jwt.claims',true),''),'{}')::jsonb $$")
        c.execute("CREATE FUNCTION auth.uid() RETURNS uuid LANGUAGE sql STABLE AS $$ SELECT nullif(auth.jwt()->>'sub','')::uuid $$")
        c.execute("CREATE FUNCTION auth.role() RETURNS text LANGUAGE sql STABLE AS $$ SELECT coalesce(auth.jwt()->>'role',current_user::text) $$")
        c.execute('GRANT USAGE ON SCHEMA auth,extensions TO identity_migrator;GRANT USAGE ON SCHEMA auth TO identity_migrator WITH GRANT OPTION;GRANT SELECT(id),REFERENCES(id),TRIGGER ON auth.users TO identity_migrator;GRANT CREATE,USAGE ON SCHEMA public TO identity_migrator')
        c.execute('GRANT USAGE ON SCHEMA auth TO identity_account_verification_owner;GRANT SELECT(id,deleted_at) ON auth.users TO identity_account_verification_owner;ALTER TABLE auth.users ENABLE ROW LEVEL SECURITY;CREATE POLICY identity_account_actor_verification ON auth.users FOR SELECT TO identity_account_verification_owner USING(true)')
        c.execute('GRANT USAGE ON SCHEMA auth TO identity_studies_owner;GRANT SELECT(id,deleted_at,email_confirmed_at,banned_until,is_anonymous) ON auth.users TO identity_studies_owner')
        c.execute("CREATE POLICY studies_current_account ON auth.users FOR SELECT TO identity_studies_owner USING(id::text=current_setting('app.account_id',true))")
        c.execute('CREATE SCHEMA identity AUTHORIZATION identity_migrator;CREATE SCHEMA access AUTHORIZATION access_migrator;SET ROLE access_migrator;GRANT USAGE ON SCHEMA access TO access_runtime;RESET ROLE')
        c.execute('REVOKE CREATE ON SCHEMA public FROM PUBLIC')
    upgrade(proof,capture,'predecessor27-upgrade')
    require_ledger27(proof)
    upgrade(proof,capture,'predecessor27-repeat')
    record_predecessor27(proof)

def red(proof):
    from psycopg.errors import UndefinedFunction
    # This schema usage is a fixture-only prerequisite so the missing function is
    # observable under the actual restricted LOGIN. Revoke before recording27.
    with connect(proof) as c:c.execute('GRANT USAGE ON SCHEMA identity TO '+ROLE)
    try:
        with connect(proof,ROLE) as c:c.execute('SELECT actor_id,display_name FROM identity.actor_displays(%s::uuid[])',([UUID(int=77)],))
    except UndefinedFunction as error:
        private(proof/'acceptance-red.json',{'selected_id':str(UUID(int=77)),'expected':[],'actual':'missing native function','sqlstate':error.sqlstate,'actual_login':ROLE})
    else:raise AssertionError('acceptance_red_not_observed')
    finally:
        with connect(proof) as c:c.execute('REVOKE USAGE ON SCHEMA identity FROM '+ROLE)
    print('actor_native_acceptance_RED_observed_42883')

def trigger_red(proof):
    assert (proof/'predecessor27.json').is_file()
    with connect(proof) as c:
        c.execute('GRANT USAGE ON SCHEMA identity TO '+ROLE)
        before=c.execute("SELECT count(*) FROM identity.audit_log WHERE table_name='actor_native_authority_probe'").fetchone()[0]
    try:
        with connect(proof,ROLE) as c:
            c.execute("SET LOCAL request.jwt.claims='{}'")
            c.execute('CREATE TEMP TABLE actor_native_authority_probe(id uuid)')
            c.execute('CREATE TRIGGER forged_audit AFTER INSERT ON actor_native_authority_probe FOR EACH ROW EXECUTE FUNCTION identity.log_audit()')
            c.execute('INSERT INTO actor_native_authority_probe VALUES(%s)',(UUID(int=731),))
        with connect(proof) as c:
            assert c.execute("SELECT count(*) FROM identity.audit_log WHERE table_name='actor_native_authority_probe'").fetchone()[0]==before+1
        private(proof/'trigger-authority-red.json',{'expected':'restricted runtime cannot write audit rows','actual':'PUBLIC trigger EXECUTE and database TEMP permit forged audit write','actual_login':ROLE,'qualifier_sha256':sha256(Path(__file__).read_bytes()).hexdigest()})
    finally:
        with connect(proof) as c:c.execute('REVOKE USAGE ON SCHEMA identity FROM '+ROLE)
    print('actor_native_trigger_authority_RED_observed')

def diagnose27(proof):
    """Replay captured sources unchanged, retaining private raw prerequisite evidence."""
    capture=proof/'captured27'
    driver=proof/'diagnose27.py'
    assert not driver.exists()
    driver.write_text('''import sys,json,os
from pathlib import Path
p=Path(__file__).parent
sys.path.insert(0,str(p/'captured27/services/access/identity-migrations'))
import identity_baseline as b
original=b.account_actor_catalog_snapshot
def observe(c):
 value=original(c)
 out=p/'diagnose27-catalog.json'
 out.write_text(json.dumps({k:value[k] for k in ('roles','role_memberships','relations')},indent=2))
 out.chmod(0o600)
 return value
b.account_actor_catalog_snapshot=observe
from alembic.config import main
main()
''');driver.chmod(0o600)
    env={'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8','IDENTITY_MIGRATION_DATABASE_URL':url(proof),'PYTHONDONTWRITEBYTECODE':'1'}
    command([PYTHON,'-I','-B',driver,'-c',capture/'services/access/identity-alembic.ini','upgrade','head'],proof,'predecessor27-diagnostic',env=env,cwd=capture,expected=1)

def reconcile27(proof):
    """Explicit synthetic prerequisites; never rewrite historical references."""
    assert (proof/'predecessor27-upgrade.json').is_file()
    assert not (proof/'predecessor27.json').exists()
    with connect(proof) as c:
        assert c.execute("SELECT to_regclass('identity.alembic_version') IS NULL AND to_regclass('identity.actor') IS NULL").fetchone()==(True,)
        for role in ('anon','authenticated'):
            c.execute('ALTER ROLE '+role+' NOLOGIN INHERIT')
        c.execute('ALTER ROLE service_role NOLOGIN INHERIT BYPASSRLS')
        c.execute('ALTER ROLE supabase_auth_admin LOGIN NOINHERIT CREATEROLE')
        c.execute('GRANT USAGE ON SCHEMA access TO access_runtime')
    private(proof/'reconciled27-prerequisites.json',{'synthetic_only':True,'historical_reference_bytes_changed':False,'role_flags':'historical source-bound role snapshot matched independently'})
    upgrade(proof,proof/'captured27','predecessor27-reconciled-upgrade')
    require_ledger27(proof)
    upgrade(proof,proof/'captured27','predecessor27-reconciled-repeat')
    record_predecessor27(proof)

def reference28(proof):
    assert (proof/'acceptance-red.json').is_file()
    upgrade(proof,proof/'captured27','predecessor27-before-reference28')
    sys.path.insert(0,str(ACCESS/'identity-migrations'))
    from sqlalchemy import create_engine
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    import identity_actor_display_catalog as catalog
    spec=importlib.util.spec_from_file_location('_actor_display_source',ACCESS/'identity-migrations/versions/0028_actor_displays.py')
    migration=importlib.util.module_from_spec(spec);spec.loader.exec_module(migration)
    db=create_engine(url(proof),hide_parameters=True)
    try:
        with db.connect() as c:
            transaction=c.begin()
            try:
                with Operations.context(MigrationContext.configure(c)):migration.upgrade()
                result=catalog.reference_document(c)
            finally:transaction.rollback()
    finally:db.dispose()
    upgrade(proof,proof/'captured27','predecessor27-after-reference28-rollback')
    result['_generated']='GENERATED by tests/qualify_actor_display_native.py reference28, exact source execution rollback-only on independently verified27; never hand-edit'
    path=ACCESS/'identity-migrations/actor-display-reference.json'
    if path.exists() and json.loads(path.read_text())!=result:
        # Retain a superseded candidate in this explicit developer source recorder;
        # historical predecessor references are never rewritten or re-recorded.
        previous=proof/('superseded28-reference-'+uuid4().hex+'.json')
        previous.write_bytes(path.read_bytes());previous.chmod(0o600)
        path.rename(proof/('superseded28-published-'+uuid4().hex+'.json'))
    if path.exists():
        assert json.loads(path.read_text())==result,'existing28_reference_differs_from_source_execution'
    else:
        with path.open('x') as output:json.dump(result,output,sort_keys=True,indent=2);output.write('\n')
    digest=sha256(path.read_bytes()).hexdigest()
    support=ACCESS/'identity-migrations/identity_actor_display_catalog.py'
    content=support.read_text()
    if 'REFERENCE_SHA256=None' in content:
        support.write_text(content.replace('REFERENCE_SHA256=None',"REFERENCE_SHA256='"+digest+"'"))
    else:
        import re
        support.write_text(re.sub(r"REFERENCE_SHA256='[a-f0-9]+'","REFERENCE_SHA256='"+digest+"'",content,count=1))
    private(proof/'reference28-source-execution.json',{'reference_sha256':digest,'rollback_only':True,'predecessor_verified_before_and_after':True,'migration_sha256':result['migration_sha256']})
    print('actor_native_reference28_rollback_source_execution_passed')

def upgrade28(proof):
    assert (proof/'reference28-source-execution.json').is_file()
    driver=proof/'injected-postcondition28.py'
    driver.write_text('''import sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'services/access/identity-migrations'))
import identity_baseline as b
original=b.verify_owned_postcondition
def injected(connection,require_head=False):
 original(connection,require_head=require_head)
 if require_head:raise b.BaselineError('actor_native_injected_postcondition_failure')
b.verify_owned_postcondition=injected
from alembic.config import main
main()
''');driver.chmod(0o600)
    with connect(proof) as c:
        before=c.execute("SELECT p.oid::regprocedure::text,p.proacl::text FROM pg_proc p WHERE p.oid IN ('identity.log_audit()'::regprocedure,'identity.set_audit_fields()'::regprocedure,'identity.handle_new_user()'::regprocedure) ORDER BY 1").fetchall()
    env={'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8','IDENTITY_MIGRATION_DATABASE_URL':url(proof),'PYTHONDONTWRITEBYTECODE':'1'}
    result=command([PYTHON,'-I','-B',driver,'-c',ACCESS/'identity-alembic.ini','upgrade','head'],proof,'injected28-upgrade-failure',env=env,expected=1)
    assert b'actor_native_injected_postcondition_failure' in result.stderr
    with connect(proof) as c:
        assert c.execute("SELECT version_num FROM identity.alembic_version").fetchone()==('identity_0027',)
        assert c.execute("SELECT to_regprocedure('identity.actor_displays(uuid[])') IS NULL").fetchone()==(True,)
        assert c.execute("SELECT p.oid::regprocedure::text,p.proacl::text FROM pg_proc p WHERE p.oid IN ('identity.log_audit()'::regprocedure,'identity.set_audit_fields()'::regprocedure,'identity.handle_new_user()'::regprocedure) ORDER BY 1").fetchall()==before
        assert not c.execute("SELECT has_schema_privilege(%s,'identity','USAGE')",(ROLE,)).fetchone()[0]
    upgrade(proof,proof/'captured27','predecessor27-after-failed28')
    private(proof/'failed28-rollback.json',{'activation_blocked':True,'schema_acl_ledger_rolled_back':True,'previous27_repeat_passed':True,'no_automatic_downgrade':True})
    upgrade(proof,ROOT,'explicit-forward-retry28')
    upgrade(proof,ROOT,'controlled28-repeat')
    private(proof/'upgrade28.json',{'head':'identity_0028','controlled_retry_and_repeat':True})
    print('actor_native_controlled_failure_rollback_retry28_passed')

def seed(proof):
    assert (proof/'predecessor27.json').is_file()
    values={'retained':UUID(int=101),'removed':UUID(int=102),'system':UUID(int=103),
            'migrate':UUID(int=104),'service':UUID(int=105),'unknown':UUID(int=106),
            'account':UUID(int=201),'removed_account':UUID(int=202)}
    names={'retained':'Retained original','removed':'Removed account retained',
           'system':'System','migrate':'Migrate','service':'Synthetic registration service'}
    with connect(proof,'identity_migrator') as c:
        existing=c.execute('SELECT id,display_name FROM identity.actor WHERE id=ANY(%s)',([values[k] for k in names],)).fetchall()
        assert not existing or dict(existing)=={values[k]:names[k] for k in names},'seed_checkpoint_mismatch'
        for index,key in enumerate(names) if not existing else ():
            actor=values[key];kind='account' if key in ('retained','removed') else ('service' if key=='service' else 'system')
            c.execute('INSERT INTO identity.actor(id,kind,display_name,actor_key,created_by,updated_by) VALUES(%s,%s,%s,%s,%s,%s)',
                      (actor,kind,names[key],'actor.native.'+key,actor,actor))
        for account,actor in ((values['account'],values['retained']),(values['removed_account'],values['removed'])) if not existing else ():
            c.execute("INSERT INTO identity.account_actor(account_id,actor_id,actor_kind,created_by) VALUES(%s,%s,'account',%s)",(account,actor,actor))
    # Native SQL stubs deliberately exercise FK/trigger retention only, not Auth.
    with connect(proof) as c:
        for key in ('account','removed_account','unknown'):
            c.execute('INSERT INTO auth.users(id,email) VALUES(%s,%s)',(values[key],key+'@example.invalid'))
        c.execute('DELETE FROM identity.users WHERE id=%s',(values['removed_account'],))
        c.execute('DELETE FROM auth.users WHERE id=%s',(values['removed_account'],))
        c.execute('CREATE TABLE access.actor_native_forbidden(id int);ALTER TABLE access.actor_native_forbidden OWNER TO access_migrator')
    # Historical consumer uses its existing login and projection, without granting
    # native display access. Identity schema USAGE is already owned by its lane.
    with connect(proof,'access_runtime') as c:
        c.execute("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',%s,true)",(str(values['account']),))
        before=c.execute('SELECT account_id,actor_id,display_name FROM identity.current_account_actor()').fetchall()
    assert before==[(values['account'],values['retained'],names['retained'])]
    private(proof/'seed.json',{'values':values,'names':names,'previous_consumer':before,'auth_helpers':'scratch SQL only; no GoTrue/provider lifecycle'})
    print('actor_native_seed_and_previous_consumer_passed')

def native(proof):
    import psycopg
    from psycopg.errors import InsufficientPrivilege,InvalidParameterValue
    seed_data=json.loads((proof/'seed.json').read_text());values={k:UUID(v) for k,v in seed_data['values'].items()};names=seed_data['names']
    selected=tuple(sorted((values[k] for k in ('retained','removed','system','migrate','service','unknown'))))
    expected={values[k]:names[k] for k in names}
    with connect(proof,'access_runtime') as c:
        c.execute("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',%s,true)",(str(values['account']),))
        prior_name='Retained renamed' if (proof/'native-sql.json').exists() else names['retained']
        assert c.execute('SELECT account_id,actor_id,display_name FROM identity.current_account_actor()').fetchall()==[(values['account'],values['retained'],prior_name)]
    with connect(proof,'identity_migrator') as c:
        c.execute('UPDATE identity.actor SET display_name=%s,updated_by=id WHERE id=%s',('Retained renamed',values['retained']))
    expected[values['retained']]='Retained renamed'
    with connect(proof,ROLE) as c:
        assert dict(c.execute('SELECT actor_id,display_name FROM identity.actor_displays(%s::uuid[])',(list(selected),)).fetchall())==expected
        assert dict(c.execute('SELECT actor_id,display_name FROM identity.actor_displays(%s::uuid[])',([UUID(int=i) for i in range(100,303)],)).fetchall())==expected
    invalid=[None,[],[None],[UUID(int=0)],[values['retained']]*2,[UUID(int=i) for i in range(1,205)],[[values['retained']],[values['removed']]]]
    for batch in invalid:
        try:
            with connect(proof,ROLE) as c:c.execute('SELECT * FROM identity.actor_displays(%s::uuid[])',(batch,)).fetchall()
        except InvalidParameterValue:pass
        else:raise AssertionError('native_invalid_array_accepted')
    denials=[]
    statements=[('raw_actor','SELECT * FROM identity.actor'),('raw_mapping','SELECT * FROM identity.account_actor'),
      ('profile','SELECT * FROM identity.users'),('ledger','SELECT * FROM identity.alembic_version'),
      ('actor_write',"INSERT INTO identity.actor(id) VALUES(gen_random_uuid())"),('actor_update',"UPDATE identity.actor SET display_name='forbidden'"),
      ('identity_ddl','CREATE TABLE identity.forbidden(id int)'),('public_ddl','CREATE TABLE public.forbidden(id int)'),
      ('database_ddl','CREATE SCHEMA forbidden'),('owner_set','SET ROLE identity_migrator'),
      ('other_projection','SELECT * FROM identity.current_account_actor()'),('operator',"SELECT identity.command_lock('forbidden')"),
      ('people_projection','SELECT * FROM identity.people_setup_references()'),('foreign_owner','SELECT * FROM access.actor_native_forbidden')]
    for label,statement in statements:
        try:
            with connect(proof,ROLE) as c:c.execute(statement).fetchall() if statement.startswith('SELECT') else c.execute(statement)
        except InsufficientPrivilege as error:denials.append({'case':label,'sqlstate':error.sqlstate})
        else:raise AssertionError('native_forbidden_operation_succeeded:'+label)
    for role in ('unauthorized_native','access_runtime','identity_people_setup_runtime','identity_operator'):
        try:
            with connect(proof,role) as c:c.execute('SELECT * FROM identity.actor_displays(%s::uuid[])',(list(selected),))
        except InsufficientPrivilege as error:denials.append({'case':'unauthorized_'+role,'sqlstate':error.sqlstate})
        else:raise AssertionError('native_unauthorized_projection_succeeded')
    for helper in ('log_audit','set_audit_fields','handle_new_user'):
        try:
            with connect(proof,ROLE) as c:
                c.execute('CREATE TEMP TABLE actor_native_denied_trigger(id uuid)')
                c.execute('CREATE TRIGGER denied BEFORE INSERT ON actor_native_denied_trigger FOR EACH ROW EXECUTE FUNCTION identity.'+helper+'()')
        except InsufficientPrivilege as error:denials.append({'case':'trigger_attachment_'+helper,'sqlstate':error.sqlstate})
        else:raise AssertionError('native_trigger_attachment_succeeded')
    # Existing Auth/profile and audit triggers still fire after direct EXECUTE
    # revocation; callers do not need attachment authority for installed triggers.
    with connect(proof) as c:
        account=uuid4();c.execute('INSERT INTO auth.users(id,email) VALUES(%s,%s)',(account,'compatibility@example.invalid'))
        assert c.execute('SELECT id FROM identity.users WHERE id=%s',(account,)).fetchone()==(account,)
        assert c.execute("SELECT count(*) FROM identity.audit_log WHERE record_id=%s AND table_name='users'",(str(account),)).fetchone()[0]>=1
    private(proof/'native-sql.json',{'ON-1':True,'ON-2':True,'invalid_arrays_denied_22023':len(invalid),'denials':denials,'old_consumer_and_data_preserved':True,'legacy_installed_triggers_compatible':True,'missing_account_not_inferred':True})
    native_guard_cases(proof)
    asyncio.run(native_async(proof,selected,expected))
    print('actor_native_ON1_ON2_ON3_ON4_ON5_passed')

def native_guard_cases(proof):
    from sqlalchemy import create_engine
    from psycopg.conninfo import conninfo_to_dict
    from sqlalchemy import URL
    sys.path.insert(0,str(ACCESS/'identity-migrations'))
    from identity_actor_display_catalog import verify_runtime
    from identity_baseline import BaselineError
    config=conninfo_to_dict(conninfo(proof));db=create_engine(URL.create('postgresql+psycopg',username=config['user'],password=config['password'],host=config['host'],port=int(config['port']),database=config['dbname']),hide_parameters=True)
    cases=[('inherit','ALTER ROLE '+ROLE+' INHERIT'),('membership','GRANT identity_migrator TO '+ROLE),
      ('incoming_membership','GRANT '+ROLE+' TO unauthorized_native'),
      ('schema_create','GRANT CREATE ON SCHEMA public TO '+ROLE),
      ('database_create','GRANT CREATE ON DATABASE actor_native_synthetic TO '+ROLE),
      ('raw_read','GRANT SELECT ON identity.actor TO '+ROLE),
      ('column_read','GRANT SELECT(id) ON identity.actor TO '+ROLE),
      ('legacy_trigger','GRANT EXECUTE ON FUNCTION identity.log_audit() TO PUBLIC')]
    try:
        for label,sql_text in cases:
            with db.connect() as c:
                transaction=c.begin()
                try:
                    c.exec_driver_sql(sql_text)
                    try:verify_runtime(c)
                    except BaselineError:pass
                    else:raise AssertionError('native_unsafe_prerequisite_accepted:'+label)
                finally:transaction.rollback()
        foreign_definer_guard(db)
    finally:db.dispose()
    with connect(proof) as c:
        if c.execute("SELECT to_regprocedure('public.actor_native_safe_helper()') IS NULL").fetchone()[0]:
            c.execute('CREATE FUNCTION public.actor_native_safe_helper() RETURNS int LANGUAGE sql AS $$SELECT 1$$')
    upgrade(proof,ROOT,'repeat28-unrelated-public-helper')
    private(proof/'native-guards.json',{'rollback_only_unsafe_cases':[v[0] for v in cases]+['foreign_owner_executable_definer'],'foreign_owner_definer_rollback_preserved':True,'unrelated_public_helper_does_not_require_identity_reference_change':True})

def foreign_definer_guard(db):
    """Make only foreign definer EXECUTE unsafe; rollback every fixture grant."""
    from sqlalchemy import text
    from identity_actor_display_catalog import verify_runtime
    from identity_baseline import BaselineError
    signature='access.actor_native_foreign_definer()'
    with db.connect() as c:
        transaction=c.begin()
        try:
            assert c.execute(text('SELECT to_regprocedure(:signature) IS NULL'),{'signature':signature}).scalar_one()
            before=c.execute(text("SELECT coalesce(nspacl::text,'') FROM pg_namespace WHERE nspname='access'")).scalar_one()
            c.exec_driver_sql('SET LOCAL ROLE access_migrator')
            c.exec_driver_sql("CREATE FUNCTION "+signature+" RETURNS int LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$SELECT 1$$")
            c.exec_driver_sql('REVOKE ALL ON FUNCTION '+signature+' FROM PUBLIC')
            c.exec_driver_sql('GRANT USAGE ON SCHEMA access TO '+ROLE)
            c.exec_driver_sql('GRANT EXECUTE ON FUNCTION '+signature+' TO '+ROLE)
            c.exec_driver_sql('RESET ROLE')
            reachable=c.execute(text("SELECT pg_get_userbyid(proowner),prosecdef,has_schema_privilege(:role,'access','USAGE'),has_function_privilege(:role,oid,'EXECUTE') FROM pg_proc WHERE oid=to_regprocedure(:signature)"),{'role':ROLE,'signature':signature}).one()
            assert tuple(reachable)==('access_migrator',True,True,True)
            c.exec_driver_sql('SET LOCAL ROLE '+ROLE)
            assert c.exec_driver_sql('SELECT '+signature).scalar_one()==1
            c.exec_driver_sql('RESET ROLE')
            try:verify_runtime(c)
            except BaselineError as error:assert str(error)=='identity_actor_display_privileges_unsafe'
            else:raise AssertionError('native_foreign_definer_accepted')
        finally:transaction.rollback()
        assert c.execute(text('SELECT to_regprocedure(:signature) IS NULL'),{'signature':signature}).scalar_one()
        assert c.execute(text("SELECT coalesce(nspacl::text,'') FROM pg_namespace WHERE nspname='access'")).scalar_one()==before

async def native_async(proof,selected,expected):
    sys.path.insert(0,str(ACCESS))
    import httpx
    from actor_display_native import NativeActorDisplayReader,PrivateConnection,NativeReadFailure
    from actor_display_http import create_app,ACTIVE,ORG
    reader=NativeActorDisplayReader(PrivateConnection(conninfo(proof,ROLE)))
    assert {r['actor_id']:r['display_name'] for r in await reader(selected,time.monotonic()+3)}==expected
    org=str(UUID(int=999));key='synthetic-only-'+'z'*40
    app=create_app({ACTIVE:key,ORG:org},reader)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as client:
        response=await client.post('/v2/identity/actor-displays',headers={'X-Service-Key':key},json={'org_id':org,'actor_ids':[str(v) for v in selected]})
        assert response.status_code==200 and response.headers['cache-control']=='private, no-store'
        labels=response.json()['labels'];assert [r['actor_id'] for r in labels]==[str(v) for v in selected]
        assert [r for r in labels if r['status']=='unavailable']==[{'actor_id':str(UUID(int=106)),'status':'unavailable'}]
        for headers,body,status in [({}, {'org_id':org,'actor_ids':[str(v) for v in selected]},403),({'X-Service-Key':key},{'org_id':str(UUID(int=998)),'actor_ids':[str(v) for v in selected]},403),({'X-Service-Key':key},{'org_id':org,'actor_ids':[]},422)]:
            denied=await client.post('/v2/identity/actor-displays',headers=headers,json=body)
            assert denied.status_code==status and denied.headers['cache-control']=='private, no-store'
    waits=[]
    with connect(proof) as blocker:
        blocker.execute('LOCK TABLE identity.actor IN ACCESS EXCLUSIVE MODE')
        start=time.monotonic()
        try:await reader(selected,start+.25)
        except (NativeReadFailure,TimeoutError):pass
        else:raise AssertionError('locked_native_read_succeeded')
        waits.append(time.monotonic()-start);assert waits[-1]<.65
        task=asyncio.create_task(reader(selected,time.monotonic()+3))
        await asyncio.sleep(.05)
        start=time.monotonic();task.cancel();task.cancel()
        try:await task
        except asyncio.CancelledError:pass
        else:raise AssertionError('cancelled_native_read_succeeded')
        waits.append(time.monotonic()-start);assert waits[-1]<.3
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as client:
            start=time.monotonic()
            unavailable=await client.post('/v2/identity/actor-displays',headers={'X-Service-Key':key},json={'org_id':org,'actor_ids':[str(v) for v in selected]})
            waits.append(time.monotonic()-start)
            assert unavailable.status_code==503 and waits[-1]<3.25
            assert unavailable.headers['cache-control']=='private, no-store'
            assert unavailable.json()=={'error_id':'identity.actor_display_unavailable','error':'Request could not be completed','details':{}}
    with connect(proof) as c:
        assert c.execute("SELECT count(*) FROM pg_stat_activity WHERE usename=%s AND datname=current_database()",(ROLE,)).fetchone()==(0,)
    # Acquisition consumes the same original budget and owns cancellation cleanup.
    acquired_cancelled=[]
    async def delayed_acquire():
        try:await asyncio.sleep(1)
        finally:acquired_cancelled.append(True)
    start=time.monotonic()
    try:await NativeActorDisplayReader(delayed_acquire)(selected,start+.08)
    except TimeoutError:pass
    else:raise AssertionError('late_acquisition_succeeded')
    assert acquired_cancelled==[True] and time.monotonic()-start<.3
    private(proof/'native-async-http.json',{'ON-3':True,'ON-5':True,'lock_deadline_and_cancel_seconds':waits,'remaining_runtime_sessions':0,'acquisition_original_budget':True,'http_exact_ids_order_missing_no_store':True})

def main():
    global PREDECESSOR_FRAME
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare27','diagnose27','reconcile27','red','trigger_red','reference28','upgrade28','seed','native']);parser.add_argument('--proof',type=Path,required=True);parser.add_argument('--predecessor-frame',type=Path);args=parser.parse_args()
    PREDECESSOR_FRAME=args.predecessor_frame.resolve() if args.predecessor_frame else None
    proof=args.proof.resolve();proof.mkdir(parents=True,exist_ok=True) if args.stage!='prepare27' else None
    if proof.exists():
        frame=proof/('invocation-'+args.stage+'-'+uuid4().hex);frame.mkdir(mode=0o700)
        paths=list((ACCESS/'identity-migrations').rglob('*.py'))+list((ACCESS/'identity-migrations').glob('*.json'))+[Path(__file__),ACCESS/'actor_display_native.py',ACCESS/'actor_display_http.py',ACCESS/'actor_display_contract.py']
        hashes={}
        for source in paths:
            if not source.is_file():continue
            target=frame/'sources'/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);target.chmod(0o600)
            hashes[str(source.relative_to(ROOT))]=sha256(source.read_bytes()).hexdigest()
        private(frame/'execution.json',{'argv':sys.argv,'sources':hashes})
    globals()[args.stage](args.proof.resolve())

if __name__=='__main__':
    try:main()
    except Exception as error:
        # Private diagnostic only; raw SQL/credentials never enter console.
        import traceback
        arg=sys.argv[sys.argv.index('--proof')+1] if '--proof' in sys.argv else '/tmp/actor-native-unconfigured'
        p=Path(arg);p.mkdir(parents=True,exist_ok=True);private(p/('failure-'+uuid4().hex+'.json'), {'type':type(error).__name__,'sqlstate':getattr(error,'sqlstate',None),'stage':sys.argv[1] if len(sys.argv)>1 else 'unconfigured'})
        print('actor_native_qualification_failed:'+type(error).__name__,file=sys.stderr);raise SystemExit(1) from None
