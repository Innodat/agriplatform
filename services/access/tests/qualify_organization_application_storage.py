"""Synthetic Access8 staging through the existing native owner qualification seam."""
if not __debug__:
    raise RuntimeError('access_qualification_optimized_python_prohibited')
import argparse
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
from uuid import uuid4
from hashlib import sha256
import importlib.util
import json,os,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_application_set_enabled as prior
from sqlalchemy import create_engine,text
ROOT,ACCESS,ACTOR=prior.ROOT,prior.ACCESS,prior.ACTOR
baseline=prior.baseline
base=prior.prior.prior.prior
CASES=prior.CASES|{'exact8','orgboundary','orglocks','orgfailure'}
base.CASES=CASES
load_fixture=base.load_fixture
ORG1='11111111-1111-4111-8111-111111111111'
ORG2='22222222-2222-4222-8222-222222222222'
NIL='00000000-0000-0000-0000-000000000000'
PREVIOUS_FILE='bootstrap_previous_enablement_adapter.py'
PREVIOUS_HASH='e68a079128ed9631b75dac9925a798441934b90e0b98e90c6802d32a2d7955b6'
TABLE='organization_applications'
INSERT="INSERT INTO access.organization_applications(org_id,app_id,created_by,updated_by,created_at,updated_at) VALUES(CAST(:org AS uuid),:app,CAST(:created_by AS uuid),CAST(:updated_by AS uuid),CAST(:created_at AS timestamptz),CAST(:updated_at AS timestamptz))"


def previous_adapter(proof):
    path=proof/PREVIOUS_FILE
    assert sha256(path.read_bytes()).hexdigest()==PREVIOUS_HASH,'previous_enablement_adapter_source_mismatch'
    spec=importlib.util.spec_from_file_location('_previous_enablement_adapter',path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module


def source_snapshot(proof):
    previous_adapter(proof)
    return {**prior.source_snapshot(proof),str(Path(__file__).resolve().relative_to(ROOT)):sha256(Path(__file__).read_bytes()).hexdigest()}


def parameters(org=ORG1,app='synthetic_app'):
    # Synthetic references deliberately make no organization/actor verification claim.
    return dict(org=org,app=app,created_by=ACTOR,updated_by=ACTOR,created_at='2001-01-01Z',updated_at='2002-01-01Z')


class Qualification(prior.Qualification):
    def admin(self,case):
        return create_engine(self.db(case,'databases').url.set(username='supabase_admin'),hide_parameters=True,connect_args=base.CONNECTION_ARGS)
    def snapshot(self,case):
        value=super().snapshot(case)
        # Explicit privileged observation, never a runtime or owner RLS bypass claim.
        engine=self.admin(case)
        try:
            with engine.begin() as c:
                c.exec_driver_sql('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
                for name in (*prior.TABLES,TABLE):
                    if c.execute(text('SELECT to_regclass(:name)'),{'name':'access.'+name}).scalar_one():
                        value[name]=[list(r) for r in c.exec_driver_sql('SELECT * FROM access.'+name+' ORDER BY 1,2')]
                for label,sql in {
                    'catalog_policies':"SELECT c.relname,p.polname,p.polcmd,p.polpermissive,p.polroles::text,pg_get_expr(p.polqual,p.polrelid),pg_get_expr(p.polwithcheck,p.polrelid) FROM pg_policy p JOIN pg_class c ON c.oid=p.polrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' ORDER BY 1,2",
                    'catalog_indexes':"SELECT c.relname,pg_get_indexdef(i.indexrelid),i.indisvalid,i.indisready,i.indislive FROM pg_index i JOIN pg_class c ON c.oid=i.indrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' ORDER BY 1,2",
                    'catalog_inheritance':"SELECT inhrelid::regclass::text,inhparent::regclass::text FROM pg_inherits WHERE inhrelid IN (SELECT c.oid FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access') OR inhparent IN (SELECT c.oid FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access') ORDER BY 1,2",
                }.items():value[label]=[list(r) for r in c.exec_driver_sql(sql)]
        finally:engine.dispose()
        return json.loads(json.dumps(value,default=str))
    def migrate(self,case,head='head',success=True):
        if getattr(self,'preparing_storage',False) and case in ('orglocks','orgfailure') and head=='head':head='access_0007'
        return super().migrate(case,head,success)
    def prepare_cases(self):
        self.preparing_storage=True
        self.migrate('exact7','access_0007');self.seed('exact7')
        values=[base.document(),prior.prior.prior.document(),prior.prior.document(),prior.document()]
        receipts=[self.command('exact7',v) for v in values]
        self.execute_sql('exact7',f"SET LOCAL app.org_id='{ORG1}'; SET LOCAL app.actor_id='historical'; INSERT INTO access.grants(org_id,id,user_id,permission,membership_id) VALUES('{ORG1}','preserved7','{ORG2}','pts.poetry.read',1)")
        before=self.snapshot('exact7');assert TABLE not in before
        super().prepare_cases()
        self.preparing_storage=False
        after=self.snapshot('exact7')
        assert after['alembic_version']==[['access_0008']] and after[TABLE]==[]
        for table in prior.TABLES:assert before[table]==after[table],table
        for v,r in zip(values,receipts):assert self.command('exact7',v)==r
        self.previous7_values,self.previous7_receipts=values,receipts
        for case in self.private['databases']:
            if case not in ('default','orglocks','orgfailure'):assert self.snapshot(case)[TABLE]==[]
        self.record('clean-exact1-through7-populated-upgrade8-empty-storage-preserves-prior-rows-and-four-command-receipts')
    def insert(self,case,values=None,context=ORG1):
        engine=self.db(case)
        try:
            with engine.begin() as c:
                if context is not None:c.execute(text("SELECT set_config('app.org_id',:org,true)"),{'org':context})
                c.execute(text(INSERT),values or parameters())
        finally:engine.dispose()
    def refused(self,case,sql,state,parameters=None,message=None,constraint=None,context=ORG1,role='access_owner_urls',prefix=None):
        before=self.snapshot(case);engine=self.db(case,role)
        try:
            try:
                with engine.begin() as c:
                    if context is not None:c.execute(text("SELECT set_config('app.org_id',:org,true)"),{'org':context})
                    if prefix:c.exec_driver_sql(prefix)
                    c.execute(text(sql),parameters or {})
            except Exception as error:
                original=getattr(error,'orig',None)
                assert getattr(original,'sqlstate',None)==state,'unexpected_storage_sqlstate'
                if message:assert original.diag.message_primary==message,'unexpected_storage_guard'
                if constraint:assert original.diag.constraint_name==constraint,'unexpected_storage_constraint'
            else:raise AssertionError('storage_refusal_missing')
        finally:engine.dispose()
        assert self.snapshot(case)==before,'storage_refusal_changed_catalog_or_data'
    def storage_functional(self):
        case='orgboundary';self.seed(case)
        for app in ('synthetic_app','other_app'):self.command(case,base.document(app))
        before=self.snapshot(case)
        for org,app in ((ORG1,'synthetic_app'),(ORG2,'synthetic_app'),(ORG1,'other_app')):self.insert(case,parameters(org,app),org)
        after=self.snapshot(case);assert len(after[TABLE])==3
        assert {(r[0],r[1]) for r in after[TABLE]}=={(ORG1,'synthetic_app'),(ORG2,'synthetic_app'),(ORG1,'other_app')}
        assert all(r[2:6]==[False,1,ACTOR,ACTOR] for r in after[TABLE])
        for table in prior.TABLES:assert after[table]==before[table]
        engine=self.db(case)
        try:
            with engine.connect() as c:
                for context,expected in ((None,0),(ORG2,1),(ORG1,2),('33333333-3333-4333-8333-333333333333',0)):
                    with c.begin():
                        if context is not None:c.execute(text("SELECT set_config('app.org_id',:org,true)"),{'org':context})
                        assert len(c.exec_driver_sql('SELECT * FROM access.organization_applications').all())==expected
                # A completed transaction's LOCAL context cannot leak into reused connection.
                with c.begin():assert not c.exec_driver_sql('SELECT * FROM access.organization_applications').all()
        finally:engine.dispose()
        for context in (None,ORG2):self.refused(case,INSERT,'42501',parameters(),context=context)
        self.refused(case,INSERT,'23505',parameters(),constraint='organization_applications_pkey')
        self.refused(case,INSERT,'23503',parameters(app='missing_app'),constraint='organization_applications_app_id_fkey')
        self.refused(case,INSERT,'42501',parameters(app='other_app')|{'org':None})
        # The owner encounters WITH CHECK RLS before NOT NULL. A separate bounded
        # administrator observation proves the underlying structural constraint.
        before=self.snapshot(case);engine=self.admin(case)
        try:
            try:
                with engine.begin() as c:
                    c.execute(text(INSERT),parameters(app='other_app')|{'org':None})
            except Exception as error:
                original=getattr(error,'orig',None)
                assert getattr(original,'sqlstate',None)=='23502','unexpected_admin_null_org_sqlstate'
                assert original.diag.column_name=='org_id','unexpected_admin_null_org_column'
            else:raise AssertionError('admin_null_org_constraint_refusal_missing')
        finally:engine.dispose()
        assert self.snapshot(case)==before,'admin_null_org_refusal_changed_catalog_or_data'
        for column in ('created_by','updated_by','created_at','updated_at'):
            p=parameters(app='other_app');p[column]=None
            self.refused(case,INSERT,'23502',p)
        for column in ('org','created_by','updated_by'):
            p=parameters(app='other_app');p[column]=NIL
            self.refused(case,INSERT,'23514',p,constraint='organization_applications_'+('org_id' if column=='org' else column)+'_non_nil',context=NIL if column=='org' else ORG1)
        for column in ('created_at','updated_at'):
            for instant in ('infinity','-infinity'):
                p=parameters(app='other_app');p[column]=instant
                self.refused(case,INSERT,'23514',p,constraint='organization_applications_'+column+'_finite')
        full=INSERT.replace('updated_at) VALUES','updated_at,revision,enabled) VALUES').replace('CAST(:updated_at AS timestamptz))','CAST(:updated_at AS timestamptz),:revision,:enabled)')
        for revision,state in ((0,'23514'),(-1,'23514'),(None,'23502'),(9223372036854775808,'22003')):
            self.refused(case,full,state,parameters(app='other_app')|dict(revision=revision,enabled=False),constraint='organization_applications_revision_positive' if state=='23514' else None)
        self.refused(case,full,'23502',parameters(app='other_app')|dict(revision=1,enabled=None))
        self.refused(case,INSERT,'23502',parameters(app=None))
        state=self.snapshot(case);self.migrate(case);assert self.snapshot(case)==state
        self.record('cross-organization-composite-key-defaults-transaction-local-forced-rls-null-nil-time-revision-fk-duplicate-rollback-populated8-repeat')
    def storage_concurrency(self):
        case='orgboundary'
        for app in ('storage_race_same','storage_race_cross'):self.command(case,base.document(app))
        before=self.snapshot(case);ready=Event();backend={}
        def competing():
            engine=self.db(case)
            try:
                try:
                    with engine.begin() as c:
                        c.execute(text("SELECT set_config('app.org_id',:org,true)"),{'org':ORG1})
                        backend['pid']=c.exec_driver_sql('SELECT pg_backend_pid()').scalar_one();ready.set()
                        c.execute(text(INSERT),parameters(app='storage_race_same'))
                except Exception as error:
                    original=getattr(error,'orig',None)
                    assert getattr(original,'sqlstate',None)=='23505','competing_insert_unexpected_sqlstate'
                    assert original.diag.constraint_name=='organization_applications_pkey','competing_insert_unexpected_constraint'
                    return 'unique_refusal'
                raise AssertionError('competing_insert_unexpected_success')
            finally:engine.dispose()
        engine=self.db(case)
        try:
            with engine.connect() as c:
                transaction=c.begin()
                try:
                    c.execute(text("SELECT set_config('app.org_id',:org,true)"),{'org':ORG1})
                    c.execute(text(INSERT),parameters(app='storage_race_same'))
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        pending=pool.submit(competing)
                        try:
                            assert ready.wait(1),'competing_insert_backend_not_ready'
                            observer=self.admin(case)
                            try:
                                deadline=time.monotonic()+1.5
                                with observer.connect() as observation:
                                    while True:
                                        waiting=observation.execute(text("SELECT EXISTS(SELECT 1 FROM pg_locks WHERE pid=:pid AND NOT granted AND locktype='transactionid')"),backend).scalar_one()
                                        if waiting:break
                                        assert time.monotonic()<deadline,'competing_insert_overlap_not_witnessed'
                                        time.sleep(.01)
                            finally:observer.dispose()
                        finally:
                            transaction.commit()
                        assert pending.result(timeout=5)=='unique_refusal'
                finally:
                    if transaction.is_active:transaction.rollback()
        finally:engine.dispose()
        barrier=Barrier(2)
        def distinct(org):
            engine=self.db(case)
            try:
                with engine.begin() as c:
                    c.execute(text("SELECT set_config('app.org_id',:org,true)"),{'org':org})
                    c.execute(text(INSERT),parameters(org=org,app='storage_race_cross'))
                    # Both inserts must complete before either transaction commits.
                    barrier.wait(timeout=1.5)
                return org
            finally:engine.dispose()
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(distinct,org) for org in (ORG1,ORG2)]
            assert {future.result(timeout=5) for future in futures}=={ORG1,ORG2}
        after=self.snapshot(case)
        for key,value in before.items():
            if key!=TABLE:assert after[key]==value,key
        old=before[TABLE];assert all(row in after[TABLE] for row in old)
        added=[row for row in after[TABLE] if row not in old]
        assert {(row[0],row[1]) for row in added}=={(ORG1,'storage_race_same'),(ORG1,'storage_race_cross'),(ORG2,'storage_race_cross')}
        assert len(added)==3
        self.record('witnessed-same-org-app-overlap-one-commit-exact-unique-refusal-and-different-org-concurrent-success-preserves-old-state')
    def identity_storage_refusal(self):
        case='integration';before=self.snapshot(case)
        spec=importlib.util.spec_from_file_location('_storage_identity_native',ACCESS/'identity-migrations/identity_baseline.py')
        identity=importlib.util.module_from_spec(spec);spec.loader.exec_module(identity)
        engine=self.admin(case)
        try:
            with engine.connect() as c:
                transaction=c.begin()
                try:
                    trigger=c.exec_driver_sql("SELECT quote_ident(t.tgname) FROM pg_trigger t JOIN pg_class r ON r.oid=t.tgrelid JOIN pg_namespace n ON n.oid=r.relnamespace JOIN pg_constraint k ON k.oid=t.tgconstraint JOIN pg_proc p ON p.oid=t.tgfoid WHERE n.nspname='access' AND r.relname='organization_applications' AND k.conname='organization_applications_app_id_fkey' AND p.proname='RI_FKey_check_ins'").scalar_one()
                    c.exec_driver_sql('ALTER TABLE access.organization_applications DISABLE TRIGGER '+trigger)
                    c.exec_driver_sql('SET LOCAL ROLE identity_migrator')
                    try:identity.verify_catalog(c,'account_actor_ensure')
                    except identity.BaselineError as error:assert str(error)=='identity_target_role_unsafe','unexpected_identity_storage_refusal'
                    else:raise AssertionError('identity_malformed_storage_accepted')
                finally:transaction.rollback()
        finally:engine.dispose()
        assert self.snapshot(case)==before
        self.record('genuine-identity18-rejects-disabled-org-fk-under-identity-role-without-access-schema-grants-rollback-preserved')
    def immutable_storage(self):
        statements=[
            'UPDATE access.organization_applications SET enabled=true',
            'UPDATE access.organization_applications SET enabled=enabled WHERE false',
            'DELETE FROM access.organization_applications',
            'DELETE FROM access.organization_applications WHERE false',
            'TRUNCATE access.organization_applications',
            INSERT+' ON CONFLICT(org_id,app_id) DO UPDATE SET enabled=excluded.enabled',
            "MERGE INTO access.organization_applications t USING (SELECT CAST(:org AS uuid) org_id,:app app_id) s ON t.org_id=s.org_id AND t.app_id=s.app_id WHEN MATCHED THEN UPDATE SET enabled=true",
            "MERGE INTO access.organization_applications t USING (SELECT CAST(:org AS uuid) org_id,:app app_id WHERE false) s ON t.org_id=s.org_id AND t.app_id=s.app_id WHEN MATCHED THEN UPDATE SET enabled=true",
        ]
        for case in ('orgboundary','exact8'):
            for sql in statements:self.refused(case,sql,'55000',parameters(),message='access_registry_storage_immutable')
        # Even an earlier successful insert is rolled back by the statement refusal.
        prefix=f"INSERT INTO access.organization_applications(org_id,app_id,created_by,updated_by,created_at,updated_at) VALUES('{ORG2}','other_app','{ACTOR}','{ACTOR}',now(),now())"
        self.refused('orgboundary',statements[1],'55000',message='access_registry_storage_immutable',context=ORG2,prefix=prefix)
        self.record('immutable-populated-and-empty-update-delete-truncate-noop-upsert-merge-update-arms-and-prior-write-atomic-rollback')
    def storage_privileges(self):
        # Actual restricted logins, plus rollback-only controlled SET ROLE observation
        # for roles that deliberately have no login or local credential.
        for role in ('access_operator_urls',):
            for sql in ('SELECT * FROM access.organization_applications',INSERT,'UPDATE access.organization_applications SET enabled=true','DELETE FROM access.organization_applications','TRUNCATE access.organization_applications','ALTER TABLE access.organization_applications ADD COLUMN forbidden text','SET ROLE access_migrator'):
                self.refused('orgboundary',sql,'42501',parameters(),role=role)
        engine=self.admin('orgboundary');before=self.snapshot('orgboundary')
        try:
            for role in ('access_runtime','access_command_owner','access_operator_authority_owner','anon','authenticated','service_role'):
                for sql in ('SELECT * FROM access.organization_applications',INSERT,'UPDATE access.organization_applications SET enabled=true','DELETE FROM access.organization_applications','TRUNCATE access.organization_applications','ALTER TABLE access.organization_applications ADD COLUMN forbidden text'):
                    try:
                        with engine.begin() as c:
                            c.exec_driver_sql('SET LOCAL ROLE '+role);c.execute(text(sql),parameters())
                    except Exception as error:assert error.orig.sqlstate=='42501','unexpected_nonowner_refusal'
                    else:raise AssertionError('nonowner_storage_authority_added')
        finally:engine.dispose()
        assert self.snapshot('orgboundary')==before
        self.record('restricted-operator-runtime-browser-command-owner-read-write-ddl-denial-no-effective-authority')
    def storage_catalog(self):
        mutations=[
            'ALTER TABLE access.organization_applications DISABLE ROW LEVEL SECURITY',
            'ALTER TABLE access.organization_applications NO FORCE ROW LEVEL SECURITY',
            'ALTER POLICY org_scope ON access.organization_applications TO PUBLIC',
            'ALTER POLICY org_scope ON access.organization_applications USING (true)',
            'ALTER POLICY org_scope ON access.organization_applications WITH CHECK (true)',
            'GRANT SELECT ON access.organization_applications TO access_runtime',
            'GRANT SELECT(org_id) ON access.organization_applications TO access_command_owner',
            'ALTER TABLE access.organization_applications ALTER COLUMN enabled SET DEFAULT true',
            'ALTER TABLE access.organization_applications ALTER COLUMN revision SET DEFAULT 2',
            'ALTER TABLE access.organization_applications DISABLE TRIGGER registry_storage_immutable',
            'ALTER TABLE access.organization_applications ENABLE ALWAYS TRIGGER registry_storage_immutable',
            'DROP TRIGGER registry_storage_immutable ON access.organization_applications; CREATE TRIGGER registry_storage_immutable BEFORE UPDATE OR DELETE ON access.organization_applications FOR EACH ROW EXECUTE FUNCTION access.registry_storage_immutable()',
            'ALTER TABLE access.organization_applications DROP CONSTRAINT organization_applications_app_id_fkey',
            'ALTER TABLE access.organization_applications DROP CONSTRAINT organization_applications_org_id_non_nil',
            'ALTER TABLE access.organization_applications SET UNLOGGED',
            "UPDATE access.alembic_version SET version_num='access_unknown'",
        ]
        engine=self.admin('clean')
        try:
            with engine.connect() as c:
                internals=[r[0] for r in c.exec_driver_sql("SELECT quote_ident(t.tgname) FROM pg_trigger t JOIN pg_constraint k ON k.oid=t.tgconstraint WHERE k.conrelid='access.organization_applications'::regclass AND t.tgisinternal")];c.rollback()
                assert len(internals)==4
                for trigger in internals:
                    relation='access.applications' if trigger.startswith('"RI_ConstraintTrigger_a_') else 'access.organization_applications'
                    mutations.append('ALTER TABLE '+relation+' DISABLE TRIGGER '+trigger)
                for mutation in mutations:
                    before=self.snapshot('clean');transaction=c.begin()
                    try:
                        c.exec_driver_sql(mutation);c.exec_driver_sql('SET LOCAL ROLE access_migrator')
                        try:baseline.preflight(c)
                        except baseline.BaselineError:pass
                        else:raise AssertionError('organization_storage_drift_accepted')
                    finally:transaction.rollback()
                    assert self.snapshot('clean')==before
        finally:engine.dispose()
        self.record('exact8-rls-policy-table-column-acl-default-guard-binding-enablement-fk-four-internal-triggers-persistence-history-drift-refuses-without-repair')
    def storage_recovery(self):
        case='orglocks';before=self.snapshot(case)
        assert before['alembic_version']==[['access_0007']] and TABLE not in before
        for lock in (baseline.LOCK_SQL,'LOCK TABLE access.applications IN ACCESS EXCLUSIVE MODE'):
            engine=self.db(case)
            try:
                with engine.connect() as c:
                    transaction=c.begin()
                    try:
                        c.exec_driver_sql(lock);started=time.monotonic();self.migrate(case,success=False)
                        assert time.monotonic()-started<15
                    finally:transaction.rollback()
            finally:engine.dispose()
            assert self.snapshot(case)==before
        self.migrate(case);assert self.snapshot(case)[TABLE]==[]
        case='orgfailure';before=self.snapshot(case)
        env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','ACCESS_MIGRATION_DATABASE_URL':self.private['access_owner_urls'][case]}
        code="import sys;sys.path.insert(0,"+repr(str(ACCESS/'migrations'))+");import access_baseline as b;from alembic.config import Config;from alembic import command;defect=lambda c:(_ for _ in ()).throw(b.BaselineError('access_test_postcondition_failure'));b.verify_postcondition=defect;command.upgrade(Config("+repr(str(ACCESS/'alembic.ini'))+"),'head')"
        result=subprocess.run([sys.executable,'-I','-B','-c',code],cwd=ROOT,env=env,capture_output=True,timeout=40)
        log=result.stdout+result.stderr;(self.proof/'storage-injected-postcondition.log').write_bytes(log)
        assert result.returncode!=0 and b'access_test_postcondition_failure' in log
        assert self.snapshot(case)==before
        self.migrate(case);assert self.snapshot(case)[TABLE]==[]
        self.record('exact7-upgrade-bounded-serialization-ddl-lock-and-injected-postcondition-rollback-explicit-recovery8')
    def previous7(self):
        previous=previous_adapter(self.proof);case='exact7';engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:
                from dataclasses import asdict
                for v,r in zip(self.previous7_values,self.previous7_receipts):
                    assert asdict(previous.execute(c,json.dumps(v).encode()))==asdict(r)
                value=prior.document(False,'2');receipt=previous.execute(c,json.dumps(value).encode())
                assert receipt.result.disposition=='changed' and receipt.result.revision=='3'
                assert previous.execute(c,json.dumps(value).encode())==receipt
                assert previous.outcome(c,value['operation_id'],command='application.set_enabled',app_id='synthetic_app')==receipt
        finally:engine.dispose()
        self.record('actual-previous7-adapter-original-four-command-replay-and-new-enable-write-lookup-on8')


def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all',action='store_true');group.add_argument('--verify-retained',action='store_true');args=parser.parse_args()
    raw=Path(os.environ['ACCESS_QUALIFICATION_DIR']);assert '..' not in raw.parts
    proof=Path(os.path.abspath(raw));private,run=load_fixture(proof)
    witness=json.loads((proof/'bootstrap-source-custody.json').read_text());captured=source_snapshot(proof)
    assert witness['status']=='passed' and witness['before']==witness['after']==captured
    for name,digest in witness['logs'].items():assert sha256((proof/name).read_bytes()).hexdigest()==digest
    q=Qualification(proof,private)
    if args.all:
        (proof/'all-started').open('x').close()
        # Current storage obligations reuse the owner helpers and one existing
        # enablement behavior matrix; historical command matrices retain their frames.
        for method in (q.prepare_cases,q.storage_functional,q.storage_concurrency,q.immutable_storage,q.storage_privileges,q.storage_catalog,q.storage_recovery,q.previous7,q.enablement_functional,q.enablement_catalog,q.integration,q.identity_storage_refusal,q.retained):method()
        (proof/'retained-state.json').write_text(json.dumps({case:q.snapshot(case) for case in private['databases']},indent=2)+'\n')
    else:
        prior.prior.require_aggregate_source(json.loads((proof/'results.json').read_text()),captured)
        assert json.loads((proof/'retained-state.json').read_text())=={case:q.snapshot(case) for case in private['databases']}
        q.retained()
    assert captured==source_snapshot(proof),'qualification_source_changed'
    (proof/('results.json' if args.all else 'retained-results.json')).write_text(json.dumps(dict(status='passed',steps=q.results,source=captured),indent=2)+'\n')
    print(json.dumps(dict(ok=True,steps=q.results)))


def report_failure(error):
    # Diagnostics never include exception text, SQL, parameters or driver payloads.
    # A refused rerun must preserve every earlier diagnostic byte.
    try:
        import traceback
        frames=[dict(file=frame.filename,line=frame.lineno,function=frame.name)
                for frame in traceback.extract_tb(error.__traceback__)]
        proof=Path(os.environ['ACCESS_QUALIFICATION_DIR'])
        path=proof/('failure-frames-'+uuid4().hex+'.json')
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'w') as output:
            json.dump(dict(type=type(error).__name__,frames=frames),output,indent=2)
            output.write('\n')
    except Exception:
        # Missing/unwritable private storage cannot prevent the safe fixed result.
        pass
    print(json.dumps(dict(ok=False,code='access_qualification_failed_requires_inspection')))


if __name__=='__main__':
    try:main()
    except Exception as error:
        report_failure(error)
        raise SystemExit(1) from None
