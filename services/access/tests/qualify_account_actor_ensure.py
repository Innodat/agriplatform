"""Synthetic actual-login account mapping matrix; no Docker lifecycle or real accounts."""
from pathlib import Path
import sys,json,uuid,os,subprocess,time
from copy import deepcopy
from dataclasses import asdict
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Event
from hashlib import sha256
from contextlib import contextmanager
from urllib.parse import urlsplit,urlunsplit,quote
sys.path.insert(0,str(Path(__file__).resolve().parent))
from qualify_actor_command import CommandQualification,operator,engine,fixture,text,encode
from qualify_identity_baseline import baseline,ROOT,OWNER


def load_cli_owner_fixture(path,target):
    """Explicit root-prepared private input; no historical-frame discovery."""
    import operator_cli as cli
    path=Path(path).absolute()
    with cli.dev.directory(path.parent) as fd:
        cli.dev.check_private(fd)
        stored=cli.dev.decode(cli.dev.read_at(fd,path.name,protected=True))
    if type(stored) is not dict or set(stored)!={'owner_url','run_id','database'}:
        raise ValueError('qualification_owner_fixture_invalid')
    if (stored['run_id'],stored['database'])!=(target.run_id,target.database):
        raise ValueError('qualification_owner_binding_invalid')
    parsed=urlsplit(stored['owner_url'])
    if (parsed.scheme,parsed.hostname,parsed.port,parsed.path,parsed.username,parsed.query,parsed.fragment)!=(
        'postgresql','127.0.0.1',target.port,'/'+target.database,'identity_migrator','',''):
        raise ValueError('qualification_owner_url_invalid')
    return stored


class AccountQualification(CommandQualification):
    def snapshot(self,case):
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:return baseline.account_actor_catalog_snapshot(c)
        finally:db.dispose()

    def invoke(self,value,case='clean',lookup=False,url=None):
        assert url is None or url in (self.private['operator_urls'][case],self.private['runtime_urls'][case]),'qualification_invocation_url_invalid'
        db=engine(url or self.private['operator_urls'][case])
        try:
            with db.connect() as c:
                login=urlsplit(url or self.private['operator_urls'][case]).username
                assert tuple(c.execute(text('SELECT session_user,current_user')).one())==(login,login)
                c.commit()
                return operator.outcome(c,value['operation_id'],command='account_actor.ensure',account_id=value['payload']['account_id']) if lookup else operator.execute(c,encode(value))
        finally:db.dispose()

    def waiting_invocation(self,value,url,ready,start,lookup=False):
        assert url in (self.private['operator_urls']['clean'],self.private['runtime_urls']['clean']),'qualification_invocation_url_invalid'
        db=engine(url)
        try:
            with db.connect() as c:
                ready.put(c.execute(text('SELECT pg_backend_pid()')).scalar_one());c.commit()
                assert start.wait(timeout=2)
                try:return operator.outcome(c,value['operation_id'],command='account_actor.ensure',account_id=value['payload']['account_id']) if lookup else operator.execute(c,encode(value))
                except operator.OperatorError as e:return e.code
        finally:db.dispose()

    def account(self,case='clean'):
        account=str(uuid.uuid4())
        self.sql(case,'INSERT INTO auth.users(id,email) VALUES (:id,:email)',dict(id=account,email='synthetic-'+account+'@example.invalid'),role='databases')
        return account

    def value(self,account=None,actor=None,authorize=True):
        account=account or self.account()
        if authorize:self.authority(self.actor,'account_actor.ensure',target=account)
        return dict(schema_version=1,command='account_actor.ensure',operation_id=str(uuid.uuid4()),scope=dict(kind='platform'),
            reason_code='synthetic_fixture',evidence_ref='synthetic:classified-human/ensure',
            payload=dict(account_id=account,actor_id=actor or str(uuid.uuid4()),display_name='Synthetic é\n\t🙂',expected_absent=True))

    def prepare_previous(self,case):
        """Build known17 from exact baseline-commit bytes, never mutate old fixtures."""
        commit='e0d116eb083cba00367a1757e373a15fdaa39340'
        constants=['ACTOR_SCHEMA_SQL','PROJECTION_SCHEMA_SQL','ORGANIZATION_SCHEMA_SQL','AUTHORITY_SCHEMA_SQL','COMMAND_SCHEMA_SQL','TARGET_SCHEMA_SQL','PROFILE_FIELDS_SQL','LEGACY_ROLES_SQL','TOKEN_HOOK_SQL','MEMBERSHIP_BINDING_SQL','MEMBERSHIP_RETENTION_SQL','MEMBERSHIP_RETIREMENT_SQL','ACTIVE_MEMBERSHIP_INDEX_SQL','MEMBERSHIP_ACTOR_ATTRIBUTION_SQL','MEMBERSHIP_RETIRE_COMMAND_SQL','MEMBERSHIP_JOIN_COMMAND_SQL']
        kinds=['actor','projection','organization','authority','command','target','profile','legacy_roles','token_hook','membership_binding','membership_retention','membership_retirement','active_membership_index','membership_actor_attribution','membership_retire_command','membership_join_command']
        paths=sorted((OWNER/'versions').glob('*.py'))[:17]
        captured={str(p.relative_to(ROOT)):subprocess.run(['git','show',commit+':'+str(p.relative_to(ROOT))],check=True,capture_output=True).stdout for p in paths}
        work=self.proof/'previous-owner';work.mkdir(mode=0o700,exist_ok=True)
        for p,data in captured.items():(work/Path(p).name).write_bytes(data)
        modules=[]
        for name,data in captured.items():
            module={};exec(compile(data,name,'exec'),module);modules.append(module)
        db=engine(self.private['owner_urls'][case])
        try:
            with db.begin() as c:
                c.execute(text("SET LOCAL statement_timeout='60s'; SET LOCAL lock_timeout='5s'"))
                assert baseline.preflight(c,'clean')=='clean'
                for source in baseline.source_sql():c.exec_driver_sql(source)
                c.exec_driver_sql(modules[0]['LEGACY_INTEGRATION_SQL'])
                baseline.verify_catalog(c,'owned')
                for module,constant,kind in zip(modules[1:],constants,kinds):
                    c.exec_driver_sql(module[constant],execution_options={'no_parameters':True});baseline.verify_catalog(c,kind)
                c.execute(text("CREATE TABLE identity.alembic_version(version_num varchar(32) NOT NULL PRIMARY KEY); INSERT INTO identity.alembic_version VALUES ('identity_0017'); REVOKE ALL ON identity.alembic_version FROM PUBLIC,anon,authenticated,service_role,supabase_auth_admin,access_runtime"))
                baseline.verify_owned_postcondition(c)
                c.execute(text("INSERT INTO identity.actor(id,kind,display_name,created_by,updated_by) VALUES ('11111111-1111-4111-8111-111111111111','system','Synthetic retained17','11111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111')"))
        finally:db.dispose()
        (self.proof/('previous-'+case+'.json')).write_text(json.dumps(dict(commit=commit,sha256={p:sha256(b).hexdigest() for p,b in captured.items()}),indent=2)+'\n')

    def run(self):
        self.command('ensure-clean-upgrade','clean')
        for case in ('previous','failure','unsafe'):
            self.prepare_previous(case)
            before=self.data_state(case)
            self.command('ensure-exact17-upgrade-'+case,case)
            after=self.data_state(case)
            assert {k:v for k,v in before.items() if k!='identity.alembic_version'}=={k:v for k,v in after.items() if k!='identity.alembic_version'}
        before=self.data_state('clean');self.command('ensure-repeat','clean');assert before==self.data_state('clean')
        rows=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")
        self.actor=rows[0][0] if rows else self.authority_fixture()
        value=self.value();first=self.invoke(value)
        assert first.result.disposition=='created' and first.result.target.account_id==value['payload']['account_id']
        assert self.invoke(value)==first and self.invoke(value,lookup=True)==first
        self.receipts=[asdict(first)]
        unchanged=deepcopy(value);unchanged['operation_id']=str(uuid.uuid4());r=self.invoke(unchanged)
        assert r.result.disposition=='unchanged' and r.result.event_id is None
        for field,new in [('actor_id',str(uuid.uuid4())),('display_name','Changed')]:
            changed=deepcopy(value);changed['payload'][field]=new;self.deny(changed,'operation_conflict')
            changed['operation_id']=str(uuid.uuid4());self.deny(changed,'operation_conflict')
        changed=deepcopy(value);changed['evidence_ref']='synthetic:other';self.deny(changed,'operation_conflict')
        # Exact scoped authority, independent of GUCs and other command rights.
        unauthorized=self.value(authorize=False);self.deny(unauthorized);self.deny(unauthorized,lookup=True)
        wrong=deepcopy(value);wrong['payload']['account_id']=unauthorized['payload']['account_id'];self.deny(wrong)
        self.legacy_matrix()
        self.ineligible_matrix(value,first)
        self.races(value)
        self.refusal_atomicity()
        self.catalog_matrix()
        assert self.sql('clean','SELECT count(*) FROM identity.org_member')==[(0,)]
        assert self.sql('clean',"SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('people','access')")==[(0,)]
        self.passed('ensure-no-person-membership-employment-or-grant-effects')
        self.persist();(self.proof/'account-ensure-receipts.json').write_text(json.dumps(self.receipts,default=str,indent=2)+'\n')

    def legacy_matrix(self):
        for existing in (False,True):
            account=self.account();value=self.value(account,account)
            if existing:self.sql('clean',"INSERT INTO identity.actor(id,kind,display_name,created_by,updated_by) VALUES (:id,'account',:label,:actor,:actor)",dict(id=account,label=value['payload']['display_name'],actor=self.actor))
            before=self.sql('clean','SELECT to_jsonb(a) FROM identity.actor a WHERE id=:id',{'id':account})
            r=self.invoke(value);assert r.result.target.actor_id==account
            if existing:assert self.sql('clean','SELECT to_jsonb(a) FROM identity.actor a WHERE id=:id',{'id':account})==before
        foreign=self.account();self.deny(self.value(actor=foreign),'operation_conflict')
        arbitrary=str(uuid.uuid4());self.sql('clean',"INSERT INTO identity.actor(id,kind,display_name,created_by,updated_by) VALUES (:id,'account','Synthetic é\n\t🙂',:actor,:actor)",dict(id=arbitrary,actor=self.actor))
        self.deny(self.value(actor=arbitrary),'operation_conflict')
        for kind,key in [('system','synthetic:system-'+uuid.uuid4().hex),('service','synthetic:service-'+uuid.uuid4().hex),('account','synthetic:keyed-'+uuid.uuid4().hex)]:
            account=self.account();self.sql('clean','INSERT INTO identity.actor(id,kind,actor_key,display_name,created_by,updated_by) VALUES (:id,:kind,:key,\'Synthetic\',:actor,:actor)',dict(id=account,kind=kind,key=key,actor=self.actor));self.deny(self.value(account,account),'operation_conflict')
        account=self.account();self.sql('clean',"INSERT INTO identity.actor(id,kind,display_name,created_by,updated_by) VALUES (:id,'account','Legacy',:actor,:actor)",dict(id=account,actor=self.actor));self.deny(self.value(account),'operation_conflict')
        self.passed('ensure-legacy-preservation-foreign-system-keyed-arbitrary-and-own-legacy-bypass-refusals')

    def ineligible_matrix(self,value,first):
        for table,column,setting in [('identity.users','deleted_at','statement_timestamp()'),('auth.users','deleted_at','statement_timestamp()'),('identity.users','is_system','true'),('identity.users','actor_key',"'synthetic:profile-key'")]:
            role='databases' if table.startswith('auth') else 'owner_urls'
            self.sql('clean','UPDATE '+table+' SET '+column+'='+setting+' WHERE id=:id',dict(id=value['payload']['account_id']),role=role)
            self.deny(value,'operation_conflict')
            # Recovery retains evidence even when the target is no longer live.
            assert self.invoke(value,lookup=True)==first
            restore='false' if column=='is_system' else 'NULL'
            self.sql('clean','UPDATE '+table+' SET '+column+'='+restore+' WHERE id=:id',dict(id=value['payload']['account_id']),role=role)
        missing=str(uuid.uuid4());self.deny(self.value(missing),'operation_conflict')
        absent_profile=self.account();self.sql('clean','DELETE FROM identity.users WHERE id=:id',dict(id=absent_profile))
        self.deny(self.value(absent_profile),'operation_conflict')
        # New account cannot appropriate a historical actor even after deletion.
        self.sql('clean','UPDATE auth.users SET deleted_at=statement_timestamp() WHERE id=:id',dict(id=value['payload']['account_id']),role='databases')
        self.deny(self.value(actor=value['payload']['actor_id']),'operation_conflict')
        self.passed('ensure-live-profile-auth-system-keyed-missing-and-new-account-reuse-matrix')

    def races(self,old):
        value=self.value();url=self.private['operator_urls']['clean'];key=operator.command_outcome_lock_key(self.actor,operator.parse_command(encode(value)))
        results=self.locked_race(value,value,[url,url],key);assert results[0]==results[1]
        changed=deepcopy(value);changed['payload']['display_name']='Changed'
        results=self.locked_race(value,changed,[url,url],key);assert sum(r=='operation_conflict' for r in results)==1
        # Distinct operation IDs racing on an absent mapping share business coordination.
        value=self.value();other=deepcopy(value);other['operation_id']=str(uuid.uuid4())
        key=self.sql('clean','SELECT identity.command_lock(:value)',{'value':'identity:account-actor:v1:'+value['payload']['account_id']})[0][0]
        results=self.locked_business_race(value,other,[url,url],key)
        assert sorted(r.result.disposition for r in results)==['created','unchanged']
        value=self.value();other=deepcopy(value);other['operation_id']=str(uuid.uuid4());other['payload']['actor_id']=str(uuid.uuid4())
        key=self.sql('clean','SELECT identity.command_lock(:value)',{'value':'identity:account-actor:v1:'+value['payload']['account_id']})[0][0]
        results=self.locked_business_race(value,other,[url,url],key)
        assert sum(r=='operation_conflict' for r in results)==1
        # Business lock waits are unavailable; only retry namespace waits are busy.
        db=engine(self.private['owner_urls']['clean'])
        try:
            for prefix,code in [('identity:account-actor:v1:','operation_unavailable'),(None,'operation_busy')]:
                value=self.value();lock=operator.command_outcome_lock_key(self.actor,operator.parse_command(encode(value))) if prefix is None else self.sql('clean','SELECT identity.command_lock(:value)',{'value':prefix+value['payload']['account_id']})[0][0]
                with db.begin() as c:
                    c.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=lock));self.deny(value,code)
        finally:db.dispose()
        self.passed('ensure-concurrent-identical-conflict-recovery-and-lock-classification')

    def locked_business_race(self,first,second,urls,key):
        # Protected authority serialization can put the second backend behind the first.
        db=engine(self.private['owner_urls']['clean']);ready=Queue();start=Event()
        try:
            with ThreadPoolExecutor(max_workers=2) as pool:
                with db.begin() as c:
                    blocker=c.execute(text('SELECT pg_backend_pid()')).scalar_one();c.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=key))
                    pending=[pool.submit(self.waiting_invocation,v,u,ready,start) for v,u in zip((first,second),urls)]
                    pids=[ready.get(timeout=2),ready.get(timeout=2)];start.set();deadline=time.monotonic()+1
                    while True:
                        c.execute(text('SELECT pg_stat_clear_snapshot()'))
                        rows=c.execute(text("SELECT pid,pg_blocking_pids(pid) FROM pg_stat_activity WHERE pid=ANY(CAST(:pids AS integer[])) AND EXISTS(SELECT 1 FROM pg_locks l WHERE l.pid=pg_stat_activity.pid AND l.locktype='advisory' AND NOT l.granted)"),dict(pids=pids)).all()
                        if len(rows)==2 and any(blocker in r[1] for r in rows) and all(set(r[1]) & {blocker,*pids} for r in rows):break
                        assert time.monotonic()<deadline and not any(f.done() for f in pending),'actual_business_wait_chain_not_witnessed'
                return [f.result() for f in pending]
        finally:db.dispose()

    def refusal_atomicity(self):
        value=self.value();before=self.data_state('clean')
        self.sql('clean',"CREATE FUNCTION identity.synthetic_ensure_failure() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic'; END $$; CREATE TRIGGER synthetic_ensure_failure BEFORE INSERT ON identity.business_event FOR EACH ROW EXECUTE FUNCTION identity.synthetic_ensure_failure()")
        try:self.deny(value,'operation_unavailable')
        finally:self.sql('clean','DROP TRIGGER synthetic_ensure_failure ON identity.business_event; DROP FUNCTION identity.synthetic_ensure_failure()')
        assert before==self.data_state('clean')
        # Raw writes/role assumption and spoofed context do not activate authority.
        db=engine(self.private['operator_urls']['clean'])
        try:
            for sql in ['SET ROLE identity_command_owner','SET ROLE identity_account_verification_owner',"INSERT INTO identity.account_actor(account_id,actor_id,actor_kind,created_by) VALUES (gen_random_uuid(),gen_random_uuid(),'account',gen_random_uuid())",'SELECT * FROM identity.users','SELECT * FROM auth.users']:
                with db.connect() as c:
                    try:c.execute(text(sql))
                    except Exception as e:assert getattr(getattr(e,'orig',None),'sqlstate',None)=='42501'
                    else:raise AssertionError('raw_authority_exposed')
            with db.connect() as c:
                c.execute(text("SELECT set_config('app.account_verified','true',false),set_config('app.actor_id',:actor,false)"),dict(actor=self.actor));c.commit()
                denied=self.value(authorize=False)
                try:operator.execute(c,encode(denied))
                except operator.OperatorError as e:assert e.code=='access_denied'
                else:raise AssertionError('spoofed_guc_authorized')
        finally:db.dispose()
        self.passed('ensure-event-failure-rollback-raw-write-role-and-guc-denials')

    def catalog_matrix(self):
        for case in ('clean','previous','failure','unsafe'):
            db=engine(self.private['owner_urls'][case])
            try:
                with db.connect() as c:baseline.verify_owned_postcondition(c,require_head=True)
            finally:db.dispose()
        for sql in ["UPDATE identity.alembic_version SET version_num='identity_unknown'",'GRANT SELECT ON identity.actor TO identity_operator']:
            db=engine(self.private['owner_urls']['clean'])
            try:
                with db.connect() as c:
                    tx=c.begin()
                    try:
                        c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                        c.execute(text(sql));changed=self.snapshot_in(c)
                        try:baseline.preflight(c,'clean')
                        except baseline.BaselineError:pass
                        else:raise AssertionError('drift_accepted')
                        assert self.snapshot_in(c)==changed
                    finally:tx.rollback()
            finally:db.dispose()
        self.passed('ensure-clean-exact17-repeat-unknown-and-catalog-drift-refusal')

    def snapshot_in(self,c):return baseline.account_actor_catalog_snapshot(c)

    def recovery_and_migration_failure(self):
        self.actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        value=self.value();db=engine(self.private['operator_urls']['clean'])
        class LostCommit:
            def __init__(self,t):self.t=t
            def __enter__(self):return self.t.__enter__()
            def __exit__(self,*args):
                result=self.t.__exit__(*args)
                if args[0] is None:raise ConnectionError('synthetic acknowledgement loss')
                return result
        class LostConnection:
            def __init__(self,c):self.c=c
            def __getattr__(self,name):return getattr(self.c,name)
            def begin(self):return LostCommit(self.c.begin())
        try:
            with db.connect() as c:
                try:operator.execute(LostConnection(c),encode(value))
                except operator.OperatorError as e:assert e.code=='operation_unavailable'
                else:raise AssertionError('receipt_before_acknowledged_commit')
            receipt=self.invoke(value,lookup=True);assert receipt is not None and self.invoke(value)==receipt
        finally:db.dispose()
        case='characterization';self.prepare_previous(case);before=self.data_state(case)
        catalog=self.sql(case,"SELECT pg_get_functiondef('identity.guard_actor()'::regprocedure)")
        self.sql(case,"""CREATE SEQUENCE public.synthetic_ensure_ddl_witness;
         CREATE FUNCTION public.synthetic_ensure_ddl_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN
         IF to_regprocedure('identity.ensure_account_actor(uuid,uuid,uuid,text,text,text,bytea)') IS NOT NULL THEN
          PERFORM nextval('public.synthetic_ensure_ddl_witness'); RAISE EXCEPTION 'synthetic'; END IF; END $$;
         CREATE EVENT TRIGGER synthetic_ensure_ddl_failure ON ddl_command_end WHEN TAG IN ('CREATE FUNCTION') EXECUTE FUNCTION public.synthetic_ensure_ddl_failure();
         GRANT USAGE ON SEQUENCE public.synthetic_ensure_ddl_witness TO identity_migrator;""",role='databases')
        try:
            self.command('ensure-injected-migration-failure',case,expected='identity_migration_failed_requires_reconciliation')
            assert self.sql(case,'SELECT last_value,is_called FROM public.synthetic_ensure_ddl_witness',role='databases')==[(1,True)]
        finally:self.sql(case,'DROP EVENT TRIGGER synthetic_ensure_ddl_failure; DROP FUNCTION public.synthetic_ensure_ddl_failure(); DROP SEQUENCE public.synthetic_ensure_ddl_witness',role='databases')
        assert self.data_state(case)==before and self.sql(case,"SELECT pg_get_functiondef('identity.guard_actor()'::regprocedure)")==catalog
        self.command('ensure-explicit-migration-recovery',case)
        self.passed('ensure-committed-response-loss-scoped-recovery-and-migration-atomic-rollback')

    def closure(self):
        self.actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        account=self.account();value=self.value(account)
        self.sql('clean','DELETE FROM identity.users WHERE id=:id',dict(id=account))
        self.deny(value,'operation_conflict')
        known=self.value();receipt=self.invoke(known)
        canonical=json.dumps(known,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        observed=self.sql('clean',"""SELECT o.fingerprint,a.created_by::text,a.updated_by::text,a.created_at,a.updated_at,
         m.created_by::text,m.created_at,o.committed_at,e.created_at,e.executor_actor_id::text
         FROM identity.operation_outcome o JOIN identity.account_actor m ON m.account_id=(o.result->'target'->>'account_id')::uuid
         JOIN identity.actor a ON a.id=m.actor_id JOIN identity.business_event e ON e.outcome_id=o.id WHERE o.operation_id=:op""",dict(op=known['operation_id']))[0]
        fingerprint,created_actor,updated_actor,created,updated,map_actor,mapped,committed,event_at,event_actor=observed
        assert fingerprint==sha256(canonical).digest()
        assert created_actor==updated_actor==map_actor==event_actor==self.actor
        assert created==updated==mapped==committed==event_at==receipt.committed_at
        # Inspect exact creation attribution, evidence/event linkage and fingerprints.
        rows=self.sql('clean',"""SELECT o.operation_id::text,o.result,o.executor_actor_id::text,o.committed_at,o.fingerprint,
         m.created_by::text,m.created_at,a.kind,a.actor_key,e.created_at,e.executor_actor_id::text,e.target,e.transition,e.evidence_ref,
         (SELECT count(*) FROM identity.business_event x WHERE x.outcome_id=o.id)
         FROM identity.operation_outcome o JOIN identity.account_actor m ON m.account_id=(o.result->'target'->>'account_id')::uuid
         JOIN identity.actor a ON a.id=m.actor_id LEFT JOIN identity.business_event e ON e.outcome_id=o.id
         WHERE o.command_type='account_actor.ensure'""")
        assert rows
        for op,result,executor,instant,fingerprint,created_by,created_at,kind,key,event_at,event_actor,target,transition,evidence,count in rows:
            assert kind=='account' and key is None and len(fingerprint)==32
            if result['disposition']=='created':
                assert executor==created_by and count==1 and event_at==created_at==instant and event_actor==executor
                assert target==result['target'] and transition==dict(kind='account') and evidence
            else:assert count==0 and result['event_id'] is None
        before=self.data_state('clean');db=engine(self.private['owner_urls']['clean'])
        try:
            with db.connect() as c:
                for sql in ["UPDATE identity.account_actor SET actor_id=gen_random_uuid()",'DELETE FROM identity.account_actor','TRUNCATE identity.account_actor']:
                    tx=c.begin()
                    try:
                        c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                        try:c.execute(text(sql))
                        except Exception as e:assert getattr(getattr(e,'orig',None),'sqlstate',None)=='23514'
                        else:raise AssertionError('mapping_history_mutated')
                    finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state('clean')==before
        self.passed('ensure-missing-profile-server-attribution-and-immutable-mapping-closure')

    def populated_repeat(self):
        before=self.data_state('clean');catalog=self.snapshot('clean')
        assert self.sql('clean','SELECT count(*) FROM identity.account_actor')[0][0]>0
        assert self.sql('clean','SELECT count(*) FROM identity.operation_outcome')[0][0]>0
        rows=self.sql('clean','SELECT to_jsonb(u) FROM auth.users u ORDER BY id',role='databases')
        auth=sha256(json.dumps(rows,sort_keys=True,default=str).encode()).hexdigest()
        self.command('ensure-populated-mappings-history-receipts-repeat','clean')
        assert self.data_state('clean')==before and self.snapshot('clean')==catalog
        assert sha256(json.dumps(self.sql('clean','SELECT to_jsonb(u) FROM auth.users u ORDER BY id',role='databases'),sort_keys=True,default=str).encode()).hexdigest()==auth
        (self.proof/'ensure-populated-repeat.json').write_text(json.dumps(dict(before=before,after=self.data_state('clean'),auth_sha256=auth,catalog_unchanged=True),indent=2)+'\n')
        self.passed('ensure-populated-legacy-mapping-outcome-event-auth-catalog-repeat-preserved')

    def verify_retained(self):
        for case in ('clean','previous','failure','unsafe','characterization'):
            db=engine(self.private['owner_urls'][case])
            try:
                with db.connect() as c:
                    c.execute(text("SET LOCAL statement_timeout='10s'; SET LOCAL lock_timeout='2s'"))
                    baseline.verify_owned_postcondition(c,require_head=True)
            finally:db.dispose()
        rows=self.sql('clean',"SELECT operation_id::text,result,command_version,result_version,committed_at FROM identity.operation_outcome WHERE command_type='account_actor.ensure'")
        assert rows
        receipts=[]
        for op,result,cv,rv,instant in rows:
            receipts.append(asdict(operator._receipt((result,cv,rv,instant),op,'account_actor.ensure')))
            count=self.sql('clean',"SELECT count(*) FROM identity.business_event WHERE event_type='identity.account_actor_ensured' AND event_id=CAST(:id AS uuid)",dict(id=result['event_id']))[0][0]
            assert count==(1 if result['disposition']=='created' else 0)
        (self.proof/('ensure-retained-'+uuid.uuid4().hex+'.json')).write_text(json.dumps(dict(receipts=receipts,exact_catalog=True,checked_outcomes=len(rows)),default=str,indent=2)+'\n')
        self.passed('ensure-retained-exact-catalog-outcome-event-receipt-verification')

    def retained_commands(self):
        from qualify_actor_command import document
        self.actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        self.authority(self.actor,'actor.register_system')
        value=document()
        db=engine(self.private['operator_urls']['clean'])
        try:
            with db.connect() as c:
                registered=operator.execute(c,encode(value));assert operator.execute(c,encode(value))==registered
                assert operator.outcome(c,value['operation_id'])==registered
        finally:db.dispose()
        account=self.account();org=str(uuid.uuid4())
        self.sql('clean',"INSERT INTO identity.org(id,name,slug) VALUES (:id,'Synthetic retained commands',:slug)",dict(id=org,slug='synthetic-'+org))
        for command in ('membership.join','membership.retire'):self.authority(self.actor,command,'organization',org,account)
        join=dict(schema_version=1,operation_id=str(uuid.uuid4()),command='membership.join',scope=dict(kind='organization',org_id=org),reason_code='synthetic_fixture',payload=dict(account_id=account,expected_previous_membership_id=None))
        db=engine(self.private['operator_urls']['clean'])
        try:
            with db.connect() as c:
                joined=operator.execute(c,encode(join));assert operator.execute(c,encode(join))==joined
                retire={**join,'operation_id':str(uuid.uuid4()),'command':'membership.retire','payload':dict(account_id=account,membership_id=joined.result.target.membership_id,expected_revision='1')}
                retired=operator.execute(c,encode(retire));assert operator.execute(c,encode(retire))==retired
                assert operator.outcome(c,join['operation_id'],command='membership.join',org_id=org,account_id=account)==joined
                assert operator.outcome(c,retire['operation_id'],command='membership.retire',org_id=org,account_id=account)==retired
        finally:db.dispose()
        self.passed('ensure-head18-register-system-join-retire-execute-replay-recovery-regression')

    def boundaries(self):
        self.actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        url=self.private['operator_urls']['clean'];db=engine(self.private['owner_urls']['clean'])
        try:
            for mutation in ('authority','profile'):
                value=self.value();key=operator.command_outcome_lock_key(self.actor,operator.parse_command(encode(value)));ready=Queue();start=Event()
                with ThreadPoolExecutor(max_workers=1) as pool:
                    with db.begin() as c:
                        blocker=c.execute(text('SELECT pg_backend_pid()')).scalar_one();c.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=key))
                        pending=pool.submit(self.waiting_invocation,value,url,ready,start)
                        pid=ready.get(timeout=2);start.set();self.witness_waiters(c,[pid],blocker,[pending])
                        if mutation=='authority':self.sql('clean',"UPDATE identity.operator_authorities SET enabled=false WHERE command='account_actor.ensure' AND target_account_id=:id",dict(id=value['payload']['account_id']))
                        else:self.sql('clean','UPDATE identity.users SET deleted_at=statement_timestamp() WHERE id=:id',dict(id=value['payload']['account_id']))
                    assert pending.result()==('access_denied' if mutation=='authority' else 'operation_conflict')
        finally:db.dispose()
        value=self.value();role='identity_account_verification_owner'
        self.sql('clean','REVOKE SELECT(deleted_at) ON auth.users FROM '+role,role='databases')
        try:self.deny(value,'operation_verification_unavailable')
        finally:self.sql('clean','GRANT SELECT(deleted_at) ON auth.users TO '+role,role='databases')
        self.sql('clean','GRANT SELECT(email) ON auth.users TO '+role,role='databases')
        try:self.deny(value,'operation_verification_unavailable')
        finally:self.sql('clean','REVOKE SELECT(email) ON auth.users FROM '+role,role='databases')
        self.sql('clean',"CREATE POLICY synthetic_ensure_restrictive ON auth.users AS RESTRICTIVE FOR SELECT TO PUBLIC USING(false)",role='databases')
        try:self.deny(value,'operation_verification_unavailable')
        finally:self.sql('clean','DROP POLICY synthetic_ensure_restrictive ON auth.users',role='databases')
        self.passed('ensure-authority-profile-rechecked-after-wait-missing-and-excess-auth-reader-refused')

    def cli(self):
        import operator_cli as cli
        from identity_operator_target import load_target
        from urllib.parse import urlsplit,urlunsplit,quote
        import psycopg
        run=json.loads((self.proof/'run.json').read_text())
        target=load_target(ROOT/'platform/deployment/.local/kdg'/run['run_id']/'identity-operator.json')
        stored=load_cli_owner_fixture(self.private['cli_owner_fixture_path'],target)
        self.private['owner_urls']['cli']=stored['owner_url']
        u=urlsplit(self.private['admin_url'])
        self.private['databases']['cli']=urlunsplit(u._replace(path='/'+target.database))
        auth_sql=(ROOT/'services/access/tools/prepare_identity_account_verification_auth.sql').read_text()
        self.command('ensure-cli-head17-upgrade','cli')
        account=self.account('cli');actor=self.sql('cli',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        authority=str(uuid.uuid4())
        self.sql('cli',"INSERT INTO identity.operator_authorities(id,database_login,command,scope_kind,target_account_id,enabled,created_by,updated_by) VALUES (:id,'identity_operator','account_actor.ensure','platform',:account,true,:actor,:actor)",dict(id=authority,account=account,actor=actor))
        value=self.value(account,authorize=False);work=target.path.parent/('ensure-'+uuid.uuid4().hex);work.mkdir(mode=0o700)
        with cli.dev.directory(work) as fd:__import__('native_cli').write_private(fd,'command.json',encode(value))
        launcher="import contextlib,io,json,sys;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1]).parent));import operator_cli as c;output=io.StringIO()\nwith contextlib.redirect_stdout(output):status=c.main(sys.argv[2:])\nprint(json.dumps({'exit_status':status,'result':json.loads(output.getvalue())}))"
        base=['--owner','identity','--target',str(target.path)]
        def invoke(args,committed=True):
            raw=cli.images.bounded_command([sys.executable,'-I','-B','-c',launcher,str(ROOT/'services/access/operator_cli.py'),*args],ROOT,{'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},16,8192)
            result=cli.dev.decode(raw);assert result['exit_status']==(0 if committed else 2),result
            return result['result']
        args=['execute',*base,'--command-file',str(work/'command.json')]
        receipt=invoke(args);assert invoke(args)==receipt
        recovery=['outcome',*base,'--command','account_actor.ensure','--operation-id',value['operation_id'],'--account-id',account]
        assert invoke(recovery)==receipt
        other=self.account('cli');assert invoke(recovery[:-1]+[other],False)['code']=='access_denied'
        (self.proof/'ensure-native-cli.json').write_text(json.dumps(dict(receipt=receipt,command=value,target=str(target.path),command_file=str(work/'command.json'),auth_preparation_sha256=sha256(auth_sql.encode()).hexdigest()),indent=2)+'\n')
        self.private['owner_urls'].pop('cli');self.private['databases'].pop('cli')
        self.passed('ensure-actual-cli-execute-replay-targeted-recovery-and-wrong-account-denial')

    def raw_invocation(self,value,ready=None,start=None):
        """Actual restricted SQL with a larger but explicit bound to inspect expiry SQLSTATE."""
        db=engine(self.private['operator_urls']['clean'])
        try:
            with db.connect() as c:
                if ready is not None:
                    ready.put(c.execute(text('SELECT pg_backend_pid()')).scalar_one());c.commit()
                    assert start.wait(timeout=2)
                try:
                    with c.begin():
                        c.execute(text("SET LOCAL statement_timeout='9s'; SET LOCAL lock_timeout='8s'"))
                        p=value['payload']
                        return c.execute(text('SELECT * FROM identity.ensure_account_actor(CAST(:op AS uuid),CAST(:account AS uuid),CAST(:actor AS uuid),:display,:reason,:evidence,:canonical)'),
                            dict(op=value['operation_id'],account=p['account_id'],actor=p['actor_id'],display=p['display_name'],reason=value['reason_code'],evidence=value['evidence_ref'],canonical=operator.canonical_command(operator.parse_command(encode(value))))).one()
                except Exception as e:return getattr(getattr(e,'orig',None),'sqlstate',None)
        finally:db.dispose()

    @contextmanager
    def observation_delays(self):
        names=['identity.verify_account_actor_account(uuid)','identity.account_actor_uuid_available(uuid,uuid)']
        definitions=[self.sql('clean','SELECT pg_get_functiondef(CAST(:name AS regprocedure))',dict(name=n))[0][0] for n in names]
        before=self.snapshot('clean');db=engine(self.private['owner_urls']['clean'])
        def install(values):
            with db.begin() as c:
                c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'; GRANT CREATE ON SCHEMA identity TO identity_account_verification_owner; SET LOCAL ROLE identity_account_verification_owner"))
                for d in values:c.exec_driver_sql(d,execution_options={'no_parameters':True})
                c.execute(text('RESET ROLE; REVOKE CREATE ON SCHEMA identity FROM identity_account_verification_owner'))
        try:
            install([d.replace('BEGIN\n','BEGIN\n PERFORM pg_sleep(3);\n',1) for d in definitions]);yield
        finally:
            install(definitions);db.dispose()
            assert self.snapshot('clean')==before

    def administrator(self):
        import psycopg
        u=urlsplit(self.private['admin_url'])
        url=urlunsplit(u._replace(netloc='supabase_admin:'+quote(u.password or '',safe='')+'@'+u.hostname+':'+str(u.port)))
        return psycopg.connect(url,autocommit=True)

    def review_boundaries(self):
        self.actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        # Staged and active-head validation reject disabled Auth RLS without mutation.
        for case,staged in [('account_actor_ensure_reference',True),('clean',False)]:
            db=engine(self.private['databases'][case])
            try:
                with db.connect() as c:
                    tx=c.begin()
                    try:
                        c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'; ALTER TABLE auth.users DISABLE ROW LEVEL SECURITY"))
                        try:baseline.verify_account_verification_role(c,staged=staged)
                        except baseline.BaselineError as e:assert str(e)=='identity_account_verification_auth_rls_required'
                        else:raise AssertionError('disabled_auth_rls_accepted')
                        assert c.execute(text("SELECT relrowsecurity FROM pg_class WHERE oid='auth.users'::regclass")).scalar_one() is False
                    finally:tx.rollback()
            finally:db.dispose()
        value=self.value();first=self.invoke(value);before=self.data_state('clean')
        key=operator.command_outcome_lock_key(self.actor,operator.parse_command(encode(value)));ready=Queue();start=Event();db=engine(self.private['owner_urls']['clean'])
        try:
            with ThreadPoolExecutor(max_workers=1) as pool:
                with db.begin() as c:
                    blocker=c.execute(text('SELECT pg_backend_pid()')).scalar_one();c.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=key))
                    pending=pool.submit(self.raw_invocation,value,ready,start);pid=ready.get(timeout=2);start.set()
                    self.witness_waiters(c,[pid],blocker,[pending]);time.sleep(5.2)
                assert pending.result()=='IC004'
        finally:db.dispose()
        assert self.data_state('clean')==before and self.invoke(value,lookup=True)==first
        delayed=self.value();before=self.data_state('clean')
        with self.observation_delays():
            started=time.monotonic();assert self.raw_invocation(delayed)=='IC004';assert 5<=time.monotonic()-started<9
        assert self.data_state('clean')==before
        role='identity_account_verification_owner'
        with self.administrator() as c:
            assert c.execute("SELECT count(*) FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname=%s)",(role,)).fetchone()[0]==0
            c.execute('GRANT authenticated TO identity_account_verification_owner WITH ADMIN FALSE,INHERIT TRUE,SET FALSE')
        try:
            self.sql('clean','CREATE POLICY synthetic_inherited_ensure_policy ON auth.users AS RESTRICTIVE FOR SELECT TO authenticated USING(false)',role='databases')
            try:self.deny(self.value(),'operation_verification_unavailable')
            finally:self.sql('clean','DROP POLICY synthetic_inherited_ensure_policy ON auth.users',role='databases')
        finally:
            with self.administrator() as c:c.execute('REVOKE authenticated FROM identity_account_verification_owner')
        self.passed('ensure-disabled-auth-rls-replay-expiry-delayed-observation-and-inherited-policy-refusal')

    @contextmanager
    def account_second_executor(self,account):
        # Existing synthetic access_runtime login, temporary wrapper ACLs only.
        signatures=['identity.ensure_account_actor(uuid,uuid,uuid,text,text,text,bytea)','identity.account_actor_outcome(uuid,uuid)']
        acl_sql="SELECT p.oid::regprocedure::text,coalesce(p.proacl::text,'') FROM pg_proc p WHERE p.oid IN (to_regprocedure(:execute),to_regprocedure(:lookup)) ORDER BY 1"
        params=dict(execute=signatures[0],lookup=signatures[1]);before=self.sql('clean',acl_sql,params)
        schema_before=self.sql('clean',"SELECT coalesce(nspacl::text,''),has_schema_privilege('access_runtime',oid,'USAGE') FROM pg_namespace WHERE nspname='identity'")[0]
        executor=str(uuid.uuid4());authority=str(uuid.uuid4())
        self.sql('clean',"INSERT INTO identity.actor(id,kind,display_name,created_by,updated_by) VALUES (:id,'service','Synthetic alternate executor',:id,:id)",dict(id=executor))
        self.sql('clean',"INSERT INTO identity.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by) VALUES ('access_runtime',:actor,true,:actor,:actor)",dict(actor=executor))
        self.authority(executor,'account_actor.ensure',target=account,identifier=authority,database_login='access_runtime')
        db=engine(self.private['owner_urls']['clean'])
        try:
            with db.begin() as c:
                if not schema_before[1]:c.execute(text('GRANT USAGE ON SCHEMA identity TO access_runtime'))
                c.execute(text('SET LOCAL ROLE identity_command_owner'));c.execute(text('GRANT EXECUTE ON FUNCTION '+','.join(signatures)+' TO access_runtime'));c.execute(text('RESET ROLE'))
            yield executor,self.private['runtime_urls']['clean']
        finally:
            with db.begin() as c:
                c.execute(text('SET LOCAL ROLE identity_command_owner'));c.execute(text('REVOKE EXECUTE ON FUNCTION '+','.join(signatures)+' FROM access_runtime'));c.execute(text('RESET ROLE'))
                if not schema_before[1]:c.execute(text('REVOKE USAGE ON SCHEMA identity FROM access_runtime'))
                c.execute(text('UPDATE identity.operator_authorities SET enabled=false WHERE id=:id'),dict(id=authority))
                c.execute(text("UPDATE identity.operator_principals SET enabled=false WHERE database_login='access_runtime'"))
            db.dispose()
            assert self.sql('clean',acl_sql,params)==before
            assert self.sql('clean',"SELECT coalesce(nspacl::text,''),has_schema_privilege('access_runtime',oid,'USAGE') FROM pg_namespace WHERE nspname='identity'")[0]==schema_before

    def alternate_executor(self):
        self.actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        value=self.value();url=self.private['operator_urls']['clean'];owner=engine(self.private['owner_urls']['clean'])
        with self.account_second_executor(value['payload']['account_id']) as (other,runtime):
            key=operator.command_outcome_lock_key(self.actor,operator.parse_command(encode(value)));ready=Queue();start=Event()
            try:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    with owner.begin() as c:
                        blocker=c.execute(text('SELECT pg_backend_pid()')).scalar_one();c.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=key))
                        pending=pool.submit(self.waiting_invocation,value,url,ready,start);pid=ready.get(timeout=2);start.set();self.witness_waiters(c,[pid],blocker,[pending])
                        second=self.invoke(value,url=runtime)
                    first=pending.result()
            finally:owner.dispose()
            assert first.result.disposition=='unchanged' and second.result.disposition=='created'
            assert self.invoke(value,lookup=True)==first and self.invoke(value,lookup=True,url=runtime)==second
            only_other=deepcopy(value);only_other['operation_id']=str(uuid.uuid4());self.invoke(only_other,url=runtime)
            assert self.invoke(only_other,lookup=True) is None
            only_primary=deepcopy(value);only_primary['operation_id']=str(uuid.uuid4());self.invoke(only_primary)
            assert self.invoke(only_primary,lookup=True,url=runtime) is None
            assert self.sql('clean','SELECT count(DISTINCT executor_actor_id) FROM identity.operation_outcome WHERE operation_id=:op',dict(op=value['operation_id']))==[(2,)]
        self.passed('ensure-alternate-executor-namespace-foreign-recovery-denial-and-acl-restoration')

    def physical_lifecycle(self):
        self.actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        value=self.value();receipt=self.invoke(value);account=value['payload']['account_id']
        evidence=self.sql('clean',"SELECT to_jsonb(o),to_jsonb(e),to_jsonb(m),to_jsonb(a) FROM identity.operation_outcome o JOIN identity.business_event e ON e.outcome_id=o.id JOIN identity.account_actor m ON m.account_id=(o.result->'target'->>'account_id')::uuid JOIN identity.actor a ON a.id=m.actor_id WHERE o.operation_id=:op",dict(op=value['operation_id']))
        self.sql('clean','DELETE FROM identity.users WHERE id=:id',dict(id=account))
        self.sql('clean','DELETE FROM auth.users WHERE id=:id',dict(id=account),role='databases')
        assert self.invoke(value,lookup=True)==receipt;self.deny(value,'operation_conflict')
        replacement=self.account();self.deny(self.value(replacement,value['payload']['actor_id']),'operation_conflict')
        assert self.sql('clean',"SELECT to_jsonb(o),to_jsonb(e),to_jsonb(m),to_jsonb(a) FROM identity.operation_outcome o JOIN identity.business_event e ON e.outcome_id=o.id JOIN identity.account_actor m ON m.account_id=(o.result->'target'->>'account_id')::uuid JOIN identity.actor a ON a.id=m.actor_id WHERE o.operation_id=:op",dict(op=value['operation_id']))==evidence
        foreign=self.account();self.sql('clean','UPDATE auth.users SET deleted_at=statement_timestamp() WHERE id=:id',dict(id=foreign),role='databases')
        assert self.sql('clean','SELECT count(*) FROM identity.actor WHERE id=:id',dict(id=foreign))==[(0,)]
        assert self.sql('clean','SELECT count(*) FROM identity.account_actor WHERE account_id=:id OR actor_id=:id',dict(id=foreign))==[(0,)]
        self.deny(self.value(actor=foreign),'operation_conflict')
        self.passed('ensure-physical-auth-deletion-new-account-reuse-and-deleted-unmapped-foreign-uuid-refusal')

    def all(self):
        # Fresh scratch cases plus explicit root-prepared protected CLI owner fixture.
        self.run()
        self.boundaries()
        self.review_boundaries()
        self.alternate_executor()
        self.physical_lifecycle()
        self.recovery_and_migration_failure()
        self.retained_commands()
        self.closure()
        self.cli()
        self.populated_repeat()
        self.verify_retained()
        self.passed('ensure-all-acceptance-stages')


def main():
    if not __debug__:raise RuntimeError('qualification_optimized_python_prohibited')
    proof,private=fixture();q=AccountQualification(proof,private)
    q.validate_operator_urls(required_cases=frozenset(private['databases']))
    import dev
    paths=[*OWNER.glob('*.py'),*OWNER.glob('versions/*.py'),*OWNER.glob('*reference.json'),OWNER/'source-pins.json',
        ROOT/'services/access/tests/qualify_account_actor_ensure.py',ROOT/'services/access/tests/qualify_identity_baseline.py',
        *list((ROOT/'services/access/tools').glob('prepare_identity_account_verification_*.sql')),
        *list((ROOT/'services/access/tests').glob('qualify_*.py')),
        *[ROOT/n for n in baseline.SOURCES],OWNER/'pyproject.toml',OWNER/'uv.lock',
        *list((ROOT/'platform/deployment').glob('*.py')),
        *[ROOT/'services/access'/n for n in ('identity_operator.py','identity_operator_input.py','identity_operator_target.py','operator_cli.py')],proof/'bootstrap.py']
    paths.extend((ROOT/'platform/deployment').glob('*.json'))
    paths.extend((ROOT/'platform/deployment/schema').glob('*.json'))
    paths.extend((ROOT/'platform/deployment/environments').glob('*.json'))
    paths.extend((ROOT/'platform/supabase/migrations').glob('*.sql'))
    paths.extend(ROOT/n for n in dev.SOURCES)
    paths.extend([ROOT/'scripts/seed.py',ROOT/'tools/py/run_compose_supabase.py'])
    paths.extend((ROOT/'platform/supabase/seeds').rglob('*.sql'));paths=sorted(set(paths))
    captured={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths}
    witness=proof/('ensure-source-capture-'+uuid.uuid4().hex+'.json')
    witness.write_text(json.dumps(dict(before=captured,status='started'),indent=2)+'\n')
    if sys.argv[1:]==['--remaining']:
        q.actor=q.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        q.races(None);q.refusal_atomicity();q.catalog_matrix()
    elif sys.argv[1:]==['--additional']:
        q.boundaries();q.recovery_and_migration_failure();q.retained_commands()
    elif sys.argv[1:]==['--all']:q.all()
    elif sys.argv[1:]==['--review-boundaries']:q.review_boundaries()
    elif sys.argv[1:]==['--alternate-executor']:q.alternate_executor()
    elif sys.argv[1:]==['--physical-lifecycle']:q.physical_lifecycle()
    elif sys.argv[1:]==['--cli']:q.cli()
    elif sys.argv[1:]==['--verify-retained']:q.verify_retained()
    elif sys.argv[1:]==['--closure']:q.closure()
    elif sys.argv[1:]==['--populated-repeat']:q.populated_repeat()
    elif not sys.argv[1:]:q.run()
    else:raise RuntimeError('qualification_arguments_invalid')
    assert captured=={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths},'qualification_source_changed'
    witness.write_text(json.dumps(dict(before=captured,after=captured,status='passed'),indent=2)+'\n')


if __name__=='__main__':
    try:main()
    except Exception:
        print('account_actor_ensure_qualification_failed',file=sys.stderr)
        raise SystemExit(1) from None
