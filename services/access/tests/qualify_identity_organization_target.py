"""Source-bound synthetic Identity19 proof; uses existing native fixture/owner route."""
if not __debug__:
    raise RuntimeError('organization_target_qualification_optimized_python_prohibited')
import json
import os
from pathlib import Path
import subprocess
import sys
from hashlib import sha256
from dataclasses import asdict
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit
from sqlalchemy.engine import make_url
sys.path.insert(0,str(Path(__file__).resolve().parent))
from qualify_actor_command import document, encode, operator
from qualify_identity_baseline import Qualification as Existing, fixture, engine, baseline, ROOT, OWNER, text

CASES={'clean','previous','failure','locks','defaults','drift'}
ORG='A1234567-1234-4234-8234-123456789ABC'
OTHER='b2345678-2345-4345-8345-23456789abcd'
ACTOR='c3456789-3456-4456-8456-3456789abcde'
RETIRED='d456789a-4567-4567-8567-456789abcdef'
MISSING='e56789ab-5678-4678-8678-56789abcdef0'
NIL='00000000-0000-0000-0000-000000000000'
CALL='SELECT org_id::text FROM identity.organization_target(CAST(:org AS uuid))'


def digest(path):return sha256(path.read_bytes()).hexdigest()


def previous_sources(proof):
    location=Path(json.loads((proof/'run.json').read_text()).get('previous_source_dir',str(proof))).resolve()
    assert location.is_relative_to(ROOT/'platform/deployment/.local/identity-baseline')
    manifest=json.loads((location/'previous-source.json').read_text())
    assert manifest['commit']=='b6c8b22abbb4318cba452a308eef80d716718aa0'
    files=manifest.get('sources',manifest.get('sha256',manifest.get('files')))
    assert type(files) is dict and files
    root=location/'previous-root'
    for name,value in files.items():
        path=root/name
        assert path.resolve().is_relative_to(root) and not path.is_symlink()
        expected=value['sha256'] if isinstance(value,dict) else value
        assert digest(path)==expected,'previous_source_changed'
    return root,manifest


def source_snapshot(proof):
    root,manifest=previous_sources(proof)
    paths=set(OWNER.rglob('*.py'))|set(OWNER.glob('*.json'))|set((ROOT/'services/access/migrations').rglob('*.py'))|set((ROOT/'services/access/migrations').glob('*.json'))
    paths|=set((ROOT/'services/access').glob('*.py'))|set((ROOT/'services/access/tools').glob('*.sql'))|set(Path(__file__).parent.glob('qualify_*.py'))
    paths|={proof/'bootstrap.py',proof/'bootstrap_run.py',proof/'auth-helper-definitions.json',ROOT/'platform/deployment/dev.py',ROOT/'platform/deployment/native_cli.py',ROOT/'services/access/identity-alembic.ini',ROOT/'services/access/alembic.ini',Path(__file__).resolve(),Path(__file__).with_name('qualify_identity_baseline.py')}
    # Concrete private inputs consumed by this root-prepared synthetic bootstrap.
    # Retain hashes only; credentials never enter qualification output.
    prior_frame=proof.parent/'account-ensure-j9ial0p1'
    paths|={prior_frame/'credentials.json',prior_frame/'run.json',proof.parent/'org-storage-reviewed-20261021/credentials.json'}
    native=json.loads((prior_frame/'run.json').read_text())
    target=Path(native['target'])
    if not target.is_absolute():target=ROOT/target
    paths|={target,ROOT/'platform/deployment/schema/development-target-v1.json'}
    native_frame=ROOT/'platform/deployment/.local/kdg'/native['run_id']
    paths|={native_frame/'supabase/config.toml'}
    return {'files':{str(p.relative_to(ROOT)):digest(p) for p in sorted(paths)},'previous':manifest}


class Qualification(Existing):
    def record(self,label):
        self.records.append({'label':label,'status':'passed'});self.persist();print(label,'PASS',flush=True)
    def access_migrate(self,case):
        env={'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8','ACCESS_MIGRATION_DATABASE_URL':self.private['access_owner_urls'][case].replace('postgresql://','postgresql+psycopg://',1)}
        result=subprocess.run([sys.executable,'-I','-B','-m','alembic','-c',str(ROOT/'services/access/alembic.ini'),'upgrade','head'],cwd=ROOT,env=env,capture_output=True,timeout=90)
        assert result.returncode==0,'access8_compatibility_refused'
    def previous(self,case):
        previous_sources(self.proof)
        root,_=previous_sources(self.proof)
        env={'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8','IDENTITY_MIGRATION_DATABASE_URL':self.private['owner_urls'][case].replace('postgresql://','postgresql+psycopg://',1)}
        result=subprocess.run([sys.executable,'-I','-B','-m','alembic','-c',str(root/'services/access/identity-alembic.ini'),'upgrade','head'],cwd=root,env=env,capture_output=True,timeout=90)
        assert result.returncode==0,'previous18_controlled_upgrade_refused'
        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0018',)]
    def receipt(self,value,lookup=False):
        db=engine(self.private['operator_urls']['previous'])
        try:
            with db.connect() as c:
                assert tuple(c.exec_driver_sql('SELECT session_user,current_user').one())==('identity_operator','identity_operator');c.commit()
                result=operator.outcome(c,value['operation_id'],command='actor.register_system') if lookup else operator.execute(c,encode(value))
                return json.loads(json.dumps(asdict(result),default=str))
        finally:db.dispose()
    def seed_receipt(self):
        self.sql('previous',"INSERT INTO identity.actor(id,kind,display_name,created_by,updated_by) VALUES (:actor,'service','Synthetic historical executor',:actor,:actor)",{'actor':ACTOR})
        self.sql('previous',"INSERT INTO identity.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by) VALUES ('identity_operator',:actor,true,:actor,:actor)",{'actor':ACTOR})
        self.sql('previous',"INSERT INTO identity.operator_authorities(id,database_login,command,scope_kind,enabled,created_by,updated_by) VALUES (:id,'identity_operator','actor.register_system','platform',true,:actor,:actor)",{'id':str(uuid4()),'actor':ACTOR})
        value=document();receipt=self.receipt(value)
        (self.proof/'organization-target-prior-receipt.json').write_text(json.dumps({'value':value,'receipt':receipt},sort_keys=True,indent=2)+'\n')
        return value,receipt
    def check(self,case='clean'):
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:
                c.exec_driver_sql('SET TRANSACTION READ ONLY')
                baseline.verify_owned_postcondition(c,require_head=True)
        finally:db.dispose()
    def context(self,c,org=ORG,actor=ACTOR,kind='setup',account=''):
        for name,value in [('org_id',org),('actor_id',actor),('context_kind',kind),('account_id',account)]:
            if value is not None:c.execute(text('SELECT set_config(:name,:value,true)'),{'name':'app.'+name,'value':value})
    def point(self,c,org=ORG):return c.execute(text(CALL),{'org':org}).all()
    def read_matrix(self):
        case='clean';before=self.data_state(case)
        self.sql(case,"INSERT INTO identity.org(id,name,slug) VALUES (:id,'Synthetic account-free org','synthetic-target')",{'id':ORG})
        self.sql(case,"INSERT INTO identity.org(id,name,slug,deleted_at) VALUES (:id,'Synthetic retired org','synthetic-retired',now())",{'id':RETIRED})
        self.sql(case,"INSERT INTO identity.org(id,name,slug) VALUES (:id,'Other active synthetic org','synthetic-other-active')",{'id':OTHER})
        assert self.sql(case,'SELECT count(*) FROM identity.org_member')==[(0,)]
        assert self.sql(case,'SELECT count(*) FROM identity.users')==[(0,)]
        before=self.data_state(case)
        db=engine(self.private['access_owner_urls'][case])
        try:
            with db.connect() as c:
                with c.begin():
                    # First connection of this new engine has never set account context.
                    assert c.exec_driver_sql("SELECT current_setting('app.account_id',true)").scalar_one() is None
                    c.exec_driver_sql('SET LOCAL ROLE access_command_owner')
                    self.context(c,account=None)
                    assert c.exec_driver_sql("SELECT current_setting('app.account_id',true)").scalar_one() is None
                    assert self.point(c)==[(ORG.lower(),)]
                for change,argument,expected in [({},ORG,[(ORG.lower(),)]),({},ORG.lower(),[(ORG.lower(),)]),({},OTHER,[]),({},RETIRED,[]),({},MISSING,[]),({'org':OTHER},OTHER,[(OTHER,)]),({'org':RETIRED},RETIRED,[]),({'org':MISSING},MISSING,[]),({},None,[]),({},NIL,[]),({'org':None},ORG,[]),({'org':''},ORG,[]),({'org':'malformed'},ORG,[]),({'org':NIL},ORG,[]),({'actor':None},ORG,[]),({'actor':''},ORG,[]),({'actor':'malformed'},ORG,[]),({'actor':NIL},ORG,[]),({'kind':'user'},ORG,[]),({'kind':None},ORG,[]),({'kind':''},ORG,[]),({'account':ACTOR},ORG,[]),({'account':'invalid'},ORG,[]),({'account':NIL},ORG,[])]:
                    with c.begin():
                        c.exec_driver_sql('SET LOCAL ROLE access_command_owner')
                        self.context(c,**change)
                        assert self.point(c,argument)==expected,'organization_target_context_wrong'
                with c.begin():
                    c.exec_driver_sql('SET LOCAL ROLE access_command_owner')
                    assert self.point(c)==[],'local_context_leaked'
        finally:db.dispose()
        assert self.data_state(case)==before,'point_check_changed_data'
        self.record('exact-account-free-setup-context-matrix-and-pooled-local-reset')
        self.privileges()
    def privileges(self):
        roles=['access_runtime','access_target_reader','access_setup_target_reader','identity_operator','access_operator','anon','authenticated','service_role']
        for role in roles:
            assert self.sql('clean',"SELECT has_function_privilege(:role,'identity.organization_target(uuid)','EXECUTE')",{'role':role})==[(False,)],role
        assert self.sql('clean',"SELECT has_function_privilege('access_command_owner','identity.organization_target(uuid)','EXECUTE')")==[(True,)]
        for group in ('runtime_urls','operator_urls','target_urls','setup_target_urls'):
            if group not in self.private:continue
            db=engine(self.private[group]['clean'])
            try:
                if group=='runtime_urls':
                    with db.begin() as c:
                        assert tuple(c.exec_driver_sql('SELECT session_user,current_user').one())==('access_runtime','access_runtime')
                        self.context(c)
                        # Existing bridge reads remain scoped; no member matches this actor.
                        assert c.exec_driver_sql('SELECT id FROM identity.org').all()==[]
                        assert c.exec_driver_sql('SELECT user_id FROM identity.org_member').all()==[]
                forbidden=[CALL,'SET ROLE identity_target_projection_owner','SET ROLE access_command_owner']
                if group!='runtime_urls':forbidden.append('SELECT id FROM identity.org')
                for statement in forbidden:
                    with db.connect() as c:
                        login=urlsplit(self.private[group]['clean']).username
                        assert tuple(c.exec_driver_sql('SELECT session_user,current_user').one())==(login,login);c.commit()
                        try:
                            with c.begin():self.context(c);c.execute(text(statement),{'org':ORG})
                        except Exception as e:assert getattr(getattr(e,'orig',None),'sqlstate',None)=='42501','unexpected_role_denial'
                        else:raise AssertionError('unprivileged_call_succeeded')
            finally:db.dispose()
        # Existing NOLOGIN readers/browser roles are observed via explicit admin
        # role selection, separately from the actual restricted login assertions.
        admin_url=make_url(self.private['admin_url']).set(username='supabase_admin')
        # Use the same explicit administrator identity as existing synthetic bootstrap.
        # Retarget only to this already validated synthetic case database.
        admin_url=admin_url.set(database=urlsplit(self.private['databases']['clean']).path[1:])
        db=engine(admin_url.render_as_string(hide_password=False))
        try:
            for role in ('access_target_reader','access_setup_target_reader','anon','authenticated','service_role'):
                with db.connect() as c:
                    with c.begin():
                        assert c.exec_driver_sql('SELECT current_user').scalar_one()=='supabase_admin'
                        c.exec_driver_sql('SET LOCAL ROLE '+role)
                        assert c.exec_driver_sql('SELECT current_user').scalar_one()==role
                        self.context(c)
                        savepoint=c.begin_nested()
                        try:self.point(c)
                        except Exception as e:assert getattr(getattr(e,'orig',None),'sqlstate',None)=='42501'
                        else:raise AssertionError('nonlogin_role_point_call_succeeded')
                        finally:savepoint.rollback()
        finally:db.dispose()
        self.record('exact-execute-acl-actual-restricted-logins-and-controlled-nonlogin-denials')
    def drift_mutation(self,c,sql):
        # Only the fixed synthetic defect/restore statements call this helper.
        # NOINHERIT migrator must explicitly assume the routine's existing owner;
        # restore its restricted identity before any verification observation.
        assert tuple(c.exec_driver_sql('SELECT session_user,current_user').one())==('identity_migrator','identity_migrator')
        routine=sql.startswith(('ALTER FUNCTION','GRANT EXECUTE ON FUNCTION'))
        if routine:
            c.exec_driver_sql('SET LOCAL ROLE identity_target_projection_owner')
            assert c.exec_driver_sql('SELECT current_user').scalar_one()=='identity_target_projection_owner'
        c.exec_driver_sql(sql)
        if routine:c.exec_driver_sql('RESET ROLE')
        assert c.exec_driver_sql('SELECT current_user').scalar_one()=='identity_migrator'
    def committed_drift_mutation(self,sql):
        db=engine(self.private['owner_urls']['drift'])
        try:
            with db.begin() as c:self.drift_mutation(c,sql)
        finally:db.dispose()
    def drift(self):
        assert self.sql('drift',"SELECT relrowsecurity,relforcerowsecurity FROM pg_class WHERE oid='identity.org'::regclass")==[(True,False)]
        changes=["ALTER FUNCTION identity.organization_target(uuid) VOLATILE","ALTER FUNCTION identity.organization_target(uuid) SET search_path=public",'GRANT EXECUTE ON FUNCTION identity.organization_target(uuid) TO access_runtime','ALTER TABLE identity.org DISABLE ROW LEVEL SECURITY',"UPDATE identity.alembic_version SET version_num='identity_unknown'"]
        db=engine(self.private['owner_urls']['drift'])
        try:
            for sql in changes:
                with db.connect() as c:
                    tx=c.begin()
                    try:
                        self.drift_mutation(c,sql)
                        if sql=='ALTER TABLE identity.org DISABLE ROW LEVEL SECURITY':
                            assert c.exec_driver_sql("SELECT relrowsecurity FROM pg_class WHERE oid='identity.org'::regclass").scalar_one() is False
                        try:baseline.verify_owned_postcondition(c,require_head=True)
                        except baseline.BaselineError:pass
                        else:raise AssertionError('drift_accepted')
                    finally:tx.rollback()
        finally:db.dispose()
        # Commit one synthetic catalog defect, then prove the actual controlled
        # owner route refuses and leaves both catalog and business state untouched.
        original_catalog=self.snapshot('drift');original_data=self.data_state('drift')
        self.committed_drift_mutation('ALTER FUNCTION identity.organization_target(uuid) VOLATILE')
        drift_catalog=self.snapshot('drift');drift_data=self.data_state('drift')
        self.command('committed-routine-drift-controlled-refusal','drift',expected='identity_target_role_unsafe')
        assert self.snapshot('drift')==drift_catalog and self.data_state('drift')==drift_data
        self.committed_drift_mutation('ALTER FUNCTION identity.organization_target(uuid) STABLE')
        assert self.snapshot('drift')==original_catalog and self.data_state('drift')==original_data
        self.check('drift');self.record('routine-acl-search-path-rls-history-drift-refuses-without-repair')
    def rollback_and_defaults(self):
        for case in ('failure','locks','defaults'):self.previous(case)
        before=self.data_state('failure');catalog=self.snapshot('failure')
        path=OWNER/'versions/0019_organization_target.py';module={};exec(compile(path.read_bytes(),str(path),'exec'),module)
        # Fail the actual controlled Alembic transaction after its postcondition
        # has observed both the new routine and updated19 history. Preflight18
        # still runs the real verifier without injection.
        code="""import sys
sys.path.insert(0,OWNER_PATH)
import identity_baseline as b
from alembic.config import Config
from alembic import command
original=b.verify_owned_postcondition
def injected(connection,require_head=False):
    original(connection,require_head=require_head)
    if require_head:
        assert b.verify_owned_history(connection)==b.ORGANIZATION_TARGET_REVISION
        assert connection.exec_driver_sql("SELECT to_regprocedure('identity.organization_target(uuid)') IS NOT NULL").scalar_one()
        raise b.BaselineError('identity_test_postcondition_failure')
b.verify_owned_postcondition=injected
command.upgrade(Config(INI_PATH),'head')
""".replace('OWNER_PATH',repr(str(OWNER))).replace('INI_PATH',repr(str(ROOT/'services/access/identity-alembic.ini')))
        env={'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8','IDENTITY_MIGRATION_DATABASE_URL':self.private['owner_urls']['failure'].replace('postgresql://','postgresql+psycopg://',1)}
        result=subprocess.run([sys.executable,'-I','-B','-c',code],cwd=ROOT,env=env,capture_output=True,timeout=90)
        log=result.stdout+result.stderr
        log_path=self.proof/'organization-target-injected-postcondition.log'
        descriptor=os.open(log_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(descriptor,'wb') as output:output.write(log)
        assert result.returncode!=0 and b'identity_test_postcondition_failure' in log
        assert self.data_state('failure')==before and self.snapshot('failure')==catalog
        assert self.sql('failure','SELECT version_num FROM identity.alembic_version')==[('identity_0018',)]
        assert self.sql('failure',"SELECT to_regprocedure('identity.organization_target(uuid)')")==[(None,)]
        db=engine(self.private['owner_urls']['locks'])
        try:
            with db.begin() as c:
                c.exec_driver_sql('LOCK TABLE identity.alembic_version IN ACCESS EXCLUSIVE MODE')
                with ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(self.command,'held-owner-lock-bounded-refusal','locks',expected='identity_migration_failed_requires_reconciliation').result(timeout=80)
        finally:db.dispose()
        assert self.sql('locks',"SELECT to_regprocedure('identity.organization_target(uuid)')")==[(None,)]
        self.sql('defaults','ALTER DEFAULT PRIVILEGES IN SCHEMA identity GRANT EXECUTE ON FUNCTIONS TO access_runtime')
        # Defaults are catalog-protected and are not automatically normalized.
        state=self.data_state('defaults');self.command('unlisted-default-drift-refuses','defaults',expected='identity_catalog_mismatch');assert self.data_state('defaults')==state
        self.sql('defaults','ALTER DEFAULT PRIVILEGES IN SCHEMA identity REVOKE EXECUTE ON FUNCTIONS FROM access_runtime')
        # Exercise creation in rollback with an extra default grant, proving stripping
        # independently of the controlled route's earlier drift refusal.
        db=engine(self.private['owner_urls']['defaults'])
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    assert tuple(c.exec_driver_sql('SELECT session_user,current_user').one())==('identity_migrator','identity_migrator')
                    c.exec_driver_sql('ALTER DEFAULT PRIVILEGES IN SCHEMA identity GRANT EXECUTE ON FUNCTIONS TO access_runtime')
                    defaults=c.exec_driver_sql('SELECT oid,defaclacl::text FROM pg_default_acl ORDER BY oid').all()
                    c.exec_driver_sql(module['ORGANIZATION_TARGET_SQL'],execution_options={'no_parameters':True})
                    assert c.exec_driver_sql("SELECT pg_get_userbyid(proowner) FROM pg_proc WHERE oid='identity.organization_target(uuid)'::regprocedure").scalar_one()=='identity_target_projection_owner'
                    assert c.exec_driver_sql("SELECT has_function_privilege('access_runtime','identity.organization_target(uuid)','EXECUTE')").scalar_one() is False
                    assert c.exec_driver_sql('SELECT oid,defaclacl::text FROM pg_default_acl ORDER BY oid').all()==defaults
                finally:tx.rollback()
        finally:db.dispose()
        for case in ('failure','locks','defaults'):self.command('controlled-forward-recovery-'+case,case);self.check(case)
        self.record('injected-failure-lock-timeout-default-grants-atomicity-and-controlled-recovery')
    def all(self):
        marker=self.proof/'organization-target-source.json'
        assert not marker.exists(),'qualification_already_started'
        captured=source_snapshot(self.proof)
        marker.write_text(json.dumps(captured,sort_keys=True,indent=2)+'\n');marker.chmod(0o600)
        self.command('organization-target-clean-upgrade','clean')
        self.previous('previous')
        self.row_fixtures('previous')
        self.access_migrate('previous')
        value,receipt=self.seed_receipt()
        before=self.data_state('previous');external=self.external_state('previous')
        self.command('organization-target-populated18-upgrade19','previous')
        after=self.data_state('previous')
        assert self.external_state('previous')==external,'external_consumer_rows_or_fks_changed'
        assert {k:v for k,v in before.items() if k!='identity.alembic_version'}=={k:v for k,v in after.items() if k!='identity.alembic_version'}
        assert self.receipt(value)==receipt and self.receipt(value,lookup=True)==receipt
        self.command('organization-target-repeat19','previous');assert self.data_state('previous')==after
        assert self.external_state('previous')==external,'external_consumer_rows_or_fks_changed'
        self.command('organization-target-drift-case','drift')
        self.read_matrix();self.drift();self.rollback_and_defaults()
        self.access_migrate('clean');self.check('clean')
        assert source_snapshot(self.proof)==captured,'qualification_source_changed'
        retained={case:self.data_state(case) for case in sorted(CASES)}
        retained['external_previous']=external
        (self.proof/'organization-target-retained.json').write_text(json.dumps(retained,sort_keys=True,indent=2)+'\n')
        self.verify_retained();self.record('organization-target-all-matrix')
    def verify_retained(self):
        expected=json.loads((self.proof/'organization-target-source.json').read_text())
        assert source_snapshot(self.proof)==expected,'qualification_source_changed'
        retained=json.loads((self.proof/'organization-target-retained.json').read_text())
        for case in sorted(CASES):
            self.check(case);assert self.data_state(case)==retained[case],'retained_data_changed'
        assert self.external_state('previous')==retained['external_previous'],'retained_external_rows_or_fks_changed'
        historical=json.loads((self.proof/'organization-target-prior-receipt.json').read_text())
        assert self.receipt(historical['value'],lookup=True)==historical['receipt']
        assert source_snapshot(self.proof)==expected
        print('organization-target-retained PASS',flush=True)


def main():
    assert sys.argv[1:] in (['--all'],['--verify-retained']),'qualification_action_invalid'
    proof,private=fixture()
    assert CASES <= set(private['databases'])
    for group,login in [('access_owner_urls','access_migrator'),('operator_urls','identity_operator')]:
        assert group in private,'qualification_restricted_role_urls_missing'
        for case in CASES:
            parsed=urlsplit(private[group][case]);owner=urlsplit(private['owner_urls'][case])
            assert (parsed.scheme,parsed.username,parsed.hostname,parsed.port,parsed.path,parsed.query,parsed.fragment)==('postgresql',login,owner.hostname,owner.port,owner.path,'','')
    witness=json.loads((proof/'bootstrap-source-custody.json').read_text())
    assert witness['status']=='passed' and witness['before']==witness['after']==source_snapshot(proof),'bootstrap_execution_custody_required'
    assert witness['steps']==['bootstrap.py']
    assert set(witness['logs'])=={'bootstrap.log'}
    assert digest(proof/'bootstrap.log')==witness['logs']['bootstrap.log']
    q=Qualification(proof,private)
    if sys.argv[1:]==['--all']:q.all()
    else:q.verify_retained()


def run():
    try:main()
    except Exception as error:
        print('organization_target_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None


if __name__=='__main__':run()
