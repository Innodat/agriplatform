"""Fixed synthetic Access0004 native proof. Preparation is explicit and separate."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from hashlib import sha256
import importlib.util
import json,os,re
from pathlib import Path
import subprocess,sys,time
from uuid import UUID,uuid4
from urllib.parse import urlsplit
from sqlalchemy import create_engine,text
ROOT=Path(__file__).resolve().parents[3]
ACCESS=ROOT/'services/access'
sys.path[:0]=[str(ACCESS),str(ACCESS/'migrations')]
import access_operator as adapter
import access_baseline as baseline
from access_operator_input import parse_command
from identity_operator_target import load_target,dev
ACTOR='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'


def source_paths(proof):
    return sorted(set([*ACCESS.glob('*.py'),*ACCESS.glob('migrations/*.py'),*ACCESS.glob('migrations/versions/*.py'),
        ACCESS/'tools/prepare_access_operator_roles.sql',Path(__file__),*proof.glob('bootstrap*.py'),*proof.glob('auth-helper-definitions.json'),
        *ACCESS.glob('identity-migrations/*.py'),*ACCESS.glob('identity-migrations/*.json'),*ACCESS.glob('identity-migrations/versions/*.py'),
        ACCESS/'identity-migrations/pyproject.toml',ACCESS/'identity-migrations/uv.lock',ACCESS/'alembic.ini',ACCESS/'identity-alembic.ini',
        ROOT/'platform/deployment/dev.py',ROOT/'platform/deployment/native_cli.py',ROOT/'platform/deployment/images.py',ROOT/'platform/deployment/toolchain.py',ROOT/dev.SCHEMA,
        ROOT/'platform/deployment/environments/kdg-local.json']))


def source_snapshot(proof):
    return {str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in source_paths(proof)}


CASES=frozenset(('clean','exact1','exact2','exact3','boundary','drift','failure','locks','concurrent','recovery','cli','integration','default'))
GROUP_LOGINS={'databases':'postgres','access_owner_urls':'access_migrator','access_operator_urls':'access_operator','owner_urls':'identity_migrator'}
CONNECTION_ARGS={'connect_timeout':3,'options':'-c statement_timeout=5000 -c lock_timeout=2000 -c idle_in_transaction_session_timeout=10000 -c transaction_timeout=30000'}


def validate_fixture(private,run,target,proof):
    assert type(private) is dict and set(private)==set(GROUP_LOGINS),'fixture_groups_invalid'
    run_id=run['run_id'];namespace=run['operator_namespace']
    assert type(run_id) is str and str(UUID(run_id))==run_id and UUID(run_id).int
    assert type(namespace) is str and re.fullmatch('[0-9a-f]{8}',namespace)
    expected_prefix='acreg_'+UUID(run_id).hex[:12]+'_'+namespace+'_'
    assert run['proof']==str(proof) and run['database_namespace']==expected_prefix
    assert run['target']==str(ROOT/'platform/deployment/environments/kdg-local.json')
    for group,login in GROUP_LOGINS.items():
        assert type(private[group]) is dict and set(private[group])==CASES,'fixture_case_inventory_invalid'
        for case,value in private[group].items():
            assert type(value) is str
            url=urlsplit(value)
            database='acop_'+UUID(run_id).hex+'_'+namespace if case=='cli' else expected_prefix+case
            assert (url.scheme,url.hostname,url.port,url.username,url.path)==('postgresql','127.0.0.1',target['ports']['database'],login,'/'+database),'fixture_target_invalid'
            assert url.password and not url.query and not url.fragment and '\\' not in value,'fixture_url_options_invalid'


def load_fixture(proof):
    assert proof.parent==ROOT/'platform/deployment/.local/identity-baseline'
    with dev.directory(proof) as directory:
        dev.check_private(directory)
        private=dev.decode(dev.read_at(directory,'credentials.json',protected=True))
        run=dev.decode(dev.read_at(directory,'run.json',protected=True))
    from identity_operator_target import _binding,ENV_REF
    target=dev.decode(dev.read(ROOT/ENV_REF))
    validate_fixture(private,run,target,proof)
    _binding(ROOT/ENV_REF,run['run_id'],'access',run['operator_namespace'])
    return private,run


def document(app='synthetic_app',op=None):
    return dict(schema_version=1,operation_id=op or str(uuid4()),command='application.register',scope={'kind':'platform'},
        payload=dict(app_id=app,expected_absent=True),reason_code='synthetic_fixture',evidence_ref='synthetic:register')


def malformed_sql_cases():
    return (
        ('null_operation',{'operation':None}),
        ('nil_operation',{'operation':'00000000-0000-0000-0000-000000000000'}),
        ('null_app',{'app':None}),('invalid_app',{'app':'Uppercase_invalid'}),
        ('null_reason',{'reason':None}),('invalid_reason',{'reason':'submitted_private_reason'}),
        ('invalid_evidence',{'evidence':'https://submitted-private.invalid/token'}),
        ('null_canonical',{'canonical':None}),('invalid_utf8',{'canonical':b'\xff'}),
        ('nul_utf8',{'canonical':b'\x00'}),('invalid_json',{'canonical':b'{'}),
        ('oversize',{'canonical':b' '*65537}),
        ('noncanonical_whitespace',lambda p:{'canonical':p['canonical']+b' '}),
        ('duplicate_key',lambda p:{'canonical':p['canonical'].replace(b'{',b'{"command":"application.register",',1)}),
        ('changed_envelope_command',lambda p:{'canonical':p['canonical'].replace(b'application.register',b'permission.register')}),
        ('changed_expected_absence',lambda p:{'canonical':p['canonical'].replace(b'"expected_absent":true',b'"expected_absent":false')}),
        ('extra_executor',lambda p:{'canonical':p['canonical'].replace(b'{',b'{"executor_actor_id":"aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",',1)}),
        ('argument_envelope_mismatch',{'app':'different_sql_app'}),
    )


class Qualification:
    def __init__(self,proof,private):self.proof,self.private,self.results=proof,private,[]
    def db(self,case,role='access_owner_urls'):
        return create_engine(self.private[role][case].replace('postgresql:','postgresql+psycopg:'),hide_parameters=True,connect_args=CONNECTION_ARGS)
    def execute_sql(self,case,sql,role='access_owner_urls'):
        e=self.db(case,role)
        try:
            with e.begin() as c:
                c.exec_driver_sql("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'")
                return c.exec_driver_sql(sql).all() if sql.lstrip().upper().startswith('SELECT') else c.exec_driver_sql(sql)
        finally:e.dispose()
    def record(self,label):self.results.append(label)
    def migrate(self,case,head='head',success=True):
        env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','ACCESS_MIGRATION_DATABASE_URL':self.private['access_owner_urls'][case]}
        result=subprocess.run([sys.executable,'-I','-B','-m','alembic','-c',str(ACCESS/'alembic.ini'),'upgrade',head],cwd=ROOT,env=env,capture_output=True,timeout=40)
        label=case+'-'+head+'-'+str(time.time_ns());log=self.proof/(label+'.log')
        log.write_bytes(result.stdout+result.stderr);log.chmod(0o600)
        assert (result.returncode==0)==success, 'migration_result_mismatch:'+case
    def snapshot(self,case):
        e=self.db(case)
        try:
            with e.begin() as c:
                c.exec_driver_sql("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                c.exec_driver_sql("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'; SET LOCAL app.org_id='11111111-1111-4111-8111-111111111111'")
                value={}
                for name in ('alembic_version','grants','applications','permissions','entry_permissions','operator_principals','operator_authorities','operation_outcome','business_event'):
                    if c.execute(text('SELECT to_regclass(:name)'),{'name':'access.'+name}).scalar_one():
                        value[name]=[list(r) for r in c.exec_driver_sql('SELECT * FROM access.'+name+' ORDER BY 1')]
                for label,sql in {
                    'catalog_relations':"SELECT c.relname,c.relkind,c.relpersistence,c.relrowsecurity,c.relforcerowsecurity,c.relacl::text FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' ORDER BY c.relname",
                    'catalog_columns':"SELECT c.relname,a.attname,format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attacl::text,pg_get_expr(d.adbin,d.adrelid) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_attribute a ON a.attrelid=c.oid LEFT JOIN pg_attrdef d ON d.adrelid=c.oid AND d.adnum=a.attnum WHERE n.nspname='access' AND a.attnum>0 ORDER BY c.relname,a.attnum",
                    'catalog_constraints':"SELECT c.relname,k.conname,pg_get_constraintdef(k.oid),k.convalidated FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' ORDER BY c.relname,k.conname",
                    'catalog_triggers':"SELECT c.relname,t.tgname,t.tgenabled,t.tgisinternal,pg_get_triggerdef(t.oid) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' ORDER BY c.relname,t.tgname",
                    'catalog_functions':"SELECT p.proname,pg_get_function_identity_arguments(p.oid),pg_get_function_result(p.oid),pg_get_userbyid(p.proowner),p.proacl::text,p.prosrc,p.proconfig FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' ORDER BY p.proname",
                    'catalog_role_edges':"SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,inherit_option,set_option FROM pg_auth_members WHERE roleid IN(SELECT oid FROM pg_roles WHERE rolname IN('access_operator','access_operator_authority_owner','access_command_owner')) OR member IN(SELECT oid FROM pg_roles WHERE rolname IN('access_operator','access_operator_authority_owner','access_command_owner')) ORDER BY 1,2",
                    'catalog_role_flags':"SELECT rolname,rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,rolreplication,rolbypassrls FROM pg_roles WHERE rolname IN('access_operator','access_operator_authority_owner','access_command_owner') ORDER BY rolname",
                    'catalog_defaults':"SELECT pg_get_userbyid(defaclrole),coalesce(n.nspname,''),defaclobjtype,defaclacl::text FROM pg_default_acl d LEFT JOIN pg_namespace n ON n.oid=d.defaclnamespace WHERE n.nspname='access' OR defaclrole=(SELECT oid FROM pg_roles WHERE rolname='access_migrator') ORDER BY 1,2,3",
                    'catalog_schema':"SELECT pg_get_userbyid(nspowner),nspacl::text FROM pg_namespace WHERE nspname='access'",
                }.items():value[label]=[list(r) for r in c.exec_driver_sql(sql)]
                return json.loads(json.dumps(value,default=str))
        finally:e.dispose()
    def seed(self,case,app=None):
        evidence=json.loads((self.proof/'actor-bootstrap-evidence.json').read_text())
        assert evidence==dict(actor_id=ACTOR,kind='service',actor_key='qualification.access_operator',verified=True)
        app='NULL' if app is None else "'"+app+"'"
        self.execute_sql(case,f"INSERT INTO access.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by) VALUES('access_operator','{ACTOR}',true,'{ACTOR}','{ACTOR}'); INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_operator','application.register','platform',{app},true,'{ACTOR}','{ACTOR}')")
    def command(self,case,value):
        e=self.db(case,'access_operator_urls')
        try:
            with e.connect() as c:return adapter.execute(c,json.dumps(value).encode())
        finally:e.dispose()
    def outcome(self,case,op,app):
        e=self.db(case,'access_operator_urls')
        try:
            with e.connect() as c:return adapter.outcome(c,op,app_id=app)
        finally:e.dispose()
    def denied(self,fn,code):
        try:fn()
        except adapter.OperatorError as e:assert e.code==code,(e.code,code)
        else:raise AssertionError('expected_safe_refusal')
    def prepare_cases(self):
        for case,head in (('exact1','access_0001'),('exact2','access_0002'),('exact3','access_0003')):
            self.migrate(case,head)
            self.execute_sql(case,"SET LOCAL app.org_id='11111111-1111-4111-8111-111111111111'; SET LOCAL app.actor_id='historical'; INSERT INTO access.grants(org_id,id,user_id,permission) VALUES('11111111-1111-4111-8111-111111111111','preserved','22222222-2222-4222-8222-222222222222','pts.poetry.read')")
            before=self.snapshot(case)['grants'];assert len(before)==1
            if case=='exact3':self.execute_sql(case,f"INSERT INTO access.applications(app_id,revision,created_by,updated_by,created_at,updated_at) VALUES('exact_app',7,'{ACTOR}','{ACTOR}',statement_timestamp(),statement_timestamp())")
            self.migrate(case);after=self.snapshot(case)['grants']
            assert (after==before if head!='access_0001' else [r[:-1] for r in after]==before)
        for case in self.private['databases']:
            if case=='default':self.migrate(case,'access_0003')
            elif case not in ('exact1','exact2','exact3'):self.migrate(case)
        self.record('clean-exact1-exact2-exact3-upgrades-preserve-grants')
    def functional(self):
        case='boundary';self.seed(case);value=document()
        value.update(reason_code='setup_correction',evidence_ref='synthetic:distinct-registration-evidence')
        receipt=self.command(case,value)
        assert receipt.result.disposition=='created' and receipt.result.revision=='1'
        state=self.snapshot(case);app=state['applications'][0]
        assert app[0:3]==['synthetic_app',False,1] and app[3:5]==[ACTOR,ACTOR] and app[5]==app[6]
        assert len(state['operation_outcome'])==len(state['business_event'])==1
        assert state['business_event'][0][-3:-1]==[value['reason_code'],value['evidence_ref']]
        assert self.command(case,value)==receipt and self.snapshot(case)==state
        assert self.outcome(case,value['operation_id'],'synthetic_app')==receipt
        assert self.outcome(case,str(uuid4()),'synthetic_app') is None
        self.denied(lambda:self.outcome(case,value['operation_id'],'other_app'),'access_denied')
        changed={**value,'evidence_ref':'synthetic:changed'}
        self.denied(lambda:self.command(case,changed),'operation_conflict');assert self.snapshot(case)==state
        unchanged=self.command(case,document());assert unchanged.result.disposition=='unchanged' and unchanged.result.event_id is None
        assert len(self.snapshot(case)['business_event'])==1
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false")
        self.denied(lambda:self.command(case,value),'access_denied');self.denied(lambda:self.outcome(case,value['operation_id'],'synthetic_app'),'access_denied')
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=true; UPDATE access.operator_principals SET enabled=false")
        before=self.snapshot(case)
        self.denied(lambda:self.command(case,value),'access_denied')  # committed replay
        self.denied(lambda:self.command(case,document('principal_closed')),'access_denied')
        self.denied(lambda:self.outcome(case,value['operation_id'],'synthetic_app'),'access_denied')
        assert self.snapshot(case)==before
        self.record('atomic-disabled-registration-replay-conflict-unchanged-lookup-and-revocation')
        self.seed('exact3','exact_app')
        existing=self.command('exact3',document('exact_app'));assert existing.result.disposition=='unchanged' and existing.result.revision=='7' and existing.result.event_id is None
        self.denied(lambda:self.command('exact3',document('wrong_app')),'access_denied')
        self.record('exact-and-wildcard-application-authority')
    def concurrency(self):
        case='concurrent';self.seed(case);value=document()
        def overlap(values,app):
            e=self.db(case);c=e.connect();transaction=c.begin()
            try:
                key=int.from_bytes(sha256(('access:application:v1:'+app).encode()).digest()[:8],'big',signed=True)
                c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
                with ThreadPoolExecutor(max_workers=2) as pool:
                    futures=[pool.submit(self.command,case,v) for v in values]
                    self.wait_for_operator_lock(case,count=2)
                    transaction.rollback()
                    return [f.result(timeout=5) for f in futures]
            finally:
                if transaction.is_active:transaction.rollback()
                c.close();e.dispose()
        results=overlap([value,value],'synthetic_app');assert results[0]==results[1]
        results=overlap([document('same_app'),document('same_app')],'same_app')
        assert sorted(r.result.disposition for r in results)==['created','unchanged']
        shared=str(uuid4());left=document('race_app_left',shared);right=document('race_app_right',shared)
        before=self.snapshot(case);e=self.db(case);c=e.connect();transaction=c.begin()
        try:
            c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':adapter.command_outcome_lock_key(ACTOR,parse_command(json.dumps(left).encode()))})
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures=[pool.submit(self.command,case,v) for v in (left,right)]
                self.wait_for_operator_lock(case,count=2);transaction.rollback()
                results=[]
                for future in futures:
                    try:results.append(future.result(timeout=5))
                    except adapter.OperatorError as error:
                        assert error.code=='operation_conflict';results.append(error)
        finally:
            if transaction.is_active:transaction.rollback()
            c.close();e.dispose()
        winners=[r for r in results if not isinstance(r,adapter.OperatorError)]
        assert len(winners)==1 and winners[0].result.disposition=='created'
        after=self.snapshot(case);winner=winners[0].result.target.app_id
        assert [r[0] for r in after['applications'] if r[0] in ('race_app_left','race_app_right')]==[winner]
        assert len(after['operation_outcome'])==len(before['operation_outcome'])+1
        assert len(after['business_event'])==len(before['business_event'])+1
        self.record('witnessed-same-operation-changed-input-race-one-commit-one-conflict-no-loser-effect')
        self.seed('locks');value=document();cmd=parse_command(json.dumps(value).encode())
        for key,code in ((adapter.command_outcome_lock_key(ACTOR,cmd),'operation_busy'),
                         (int.from_bytes(sha256(b'access:operator-authority:v1:access_operator').digest()[:8],'big',signed=True),'operation_unavailable'),
                         (int.from_bytes(sha256(b'access:application:v1:synthetic_app').digest()[:8],'big',signed=True),'operation_unavailable')):
            e=self.db('locks');c=e.connect();t=c.begin()
            try:
                c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
                started=time.monotonic();self.denied(lambda:self.command('locks',value),code);assert time.monotonic()-started<7
            finally:t.rollback();c.close();e.dispose()
        assert not self.snapshot('locks')['applications']
        self.record('concurrent-retries-apps-and-bounded-retry-authority-app-lock-classification')
    def wait_for_operator_lock(self,case,count=1):
        e=self.db(case,'databases')
        try:
            deadline=time.monotonic()+3
            while time.monotonic()<deadline:
                with e.connect() as c:
                    waiting=c.exec_driver_sql("SELECT count(*) FROM pg_stat_activity WHERE usename='access_operator' AND datname=current_database() AND wait_event='advisory'").scalar_one()
                if waiting>=count:return
                time.sleep(.02)
            raise AssertionError('operator_lock_overlap_not_witnessed')
        finally:e.dispose()
    def response_loss_and_authority_wait(self):
        case='recovery';self.seed(case);value=document('lost_response')
        e=self.db(case,'access_operator_urls')
        class LostCommit:
            def __init__(self,transaction):self.transaction=transaction
            def __enter__(self):return self.transaction.__enter__()
            def __exit__(self,*args):
                answer=self.transaction.__exit__(*args)
                if args[0] is None:raise RuntimeError('synthetic_response_lost_after_real_commit')
                return answer
        class Connection:
            def __init__(self,connection):self.wrapped=connection
            def __getattr__(self,name):return getattr(self.wrapped,name)
            def begin(self):return LostCommit(self.wrapped.begin())
        try:
            with e.connect() as c:self.denied(lambda:adapter.execute(Connection(c),json.dumps(value).encode()),'operation_unavailable')
        finally:e.dispose()
        receipt=self.outcome(case,value['operation_id'],'lost_response')
        assert receipt is not None and receipt.result.disposition=='created'
        assert self.command(case,value)==receipt
        value=document('wait_revocation');cmd=parse_command(json.dumps(value).encode())
        e=self.db(case);c=e.connect();t=c.begin()
        try:
            c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':adapter.command_outcome_lock_key(ACTOR,cmd)})
            with ThreadPoolExecutor(max_workers=1) as pool:
                pending=pool.submit(self.command,case,value)
                self.wait_for_operator_lock(case)
                self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false")
                t.rollback()
                self.denied(lambda:pending.result(timeout=5),'access_denied')
        finally:
            if t.is_active:t.rollback()
            c.close();e.dispose()
        assert not any(r[0]=='wait_revocation' for r in self.snapshot(case)['applications'])
        self.record('real-postcommit-response-loss-recovery-and-witnessed-revocation-during-retry-wait')
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=true")
        value=document('guc_proof');command=parse_command(json.dumps(value).encode())
        e=self.db(case,'access_operator_urls')
        try:
            with e.begin() as c:
                c.exec_driver_sql("SET LOCAL app.actor_id='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'; SET LOCAL app.account_id='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'; SET LOCAL app.org_id='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'")
                c.execute(text('SELECT * FROM access.register_application(CAST(:op AS uuid),:app,:reason,:evidence,:canonical)'),
                    dict(op=value['operation_id'],app=command.payload.app_id,reason=command.reason_code,evidence=command.evidence_ref,canonical=adapter.canonical_command(command))).all()
        finally:e.dispose()
        assert [r for r in self.snapshot(case)['applications'] if r[0]=='guc_proof'][0][3:5]==[ACTOR,ACTOR]
        self.record('guc-overrides-cannot-spoof-original-session-executor')
    def attacks(self):
        case='failure';self.seed(case);value=document()
        self.execute_sql(case,"CREATE FUNCTION access.inject_failure() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic'; END $$; CREATE TRIGGER inject_failure BEFORE INSERT ON access.business_event FOR EACH ROW EXECUTE FUNCTION access.inject_failure()")
        before=self.snapshot(case);self.denied(lambda:self.command(case,value),'operation_unavailable');assert self.snapshot(case)==before
        self.execute_sql(case,'DROP TRIGGER inject_failure ON access.business_event; DROP FUNCTION access.inject_failure()')
        self.command(case,value);before=self.snapshot(case)
        for sql in ('SET ROLE access_command_owner','SET ROLE access_operator_authority_owner','SELECT * FROM access.operator_principals','SELECT * FROM access.operation_outcome',
                    'UPDATE access.applications SET enabled=true','DELETE FROM access.operation_outcome','TRUNCATE access.business_event','INSERT INTO access.applications DEFAULT VALUES',
                    "CREATE TABLE access.forbidden(id int)"):
            e=self.db(case,'access_operator_urls')
            try:
                try:
                    with e.begin() as c:c.exec_driver_sql(sql)
                except Exception as error:assert getattr(getattr(error,'orig',None),'sqlstate',None)=='42501','wrong_privilege_refusal'
                else:raise AssertionError('attack_succeeded')
            finally:e.dispose()
        assert self.snapshot(case)==before
        for table in ('applications','permissions','entry_permissions','operation_outcome','business_event'):
            for action in ('UPDATE access.'+table+' SET created_at=created_at' if table!='operation_outcome' else 'UPDATE access.operation_outcome SET committed_at=committed_at','DELETE FROM access.'+table,'TRUNCATE access.'+table+' CASCADE'):
                try:self.execute_sql(case,action)
                except Exception as error:assert getattr(getattr(error,'orig',None),'sqlstate',None) in ('23514','55000','0A000'),'wrong_immutability_refusal'
                else:raise AssertionError('immutability_attack_succeeded')
        try:self.execute_sql(case,f"INSERT INTO access.applications(app_id,created_by,updated_by,created_at,updated_at) VALUES('missing_evidence','{ACTOR}','{ACTOR}',statement_timestamp(),statement_timestamp())")
        except Exception as error:assert getattr(getattr(error,'orig',None),'sqlstate',None)=='23514'
        else:raise AssertionError('application_without_evidence_committed')
        assert self.snapshot(case)==before
        self.record('injected-event-failure-atomic-rollback-and-raw-dml-role-evidence-immutability-denial')
    def drift(self):
        case='drift'
        self.execute_sql(case,"ALTER TABLE access.operation_outcome DROP CONSTRAINT operation_outcome_command_type_check; ALTER TABLE access.operation_outcome ADD CONSTRAINT operation_outcome_command_type_check CHECK(command_type='APPLICATION.REGISTER')")
        before=self.snapshot(case);self.migrate(case,success=False);assert self.snapshot(case)==before
        self.record('exact-literal-drift-refuses-without-normalization')
        self.execute_sql(case,"UPDATE access.alembic_version SET version_num='access_unknown'")
        before=self.snapshot(case);self.migrate(case,success=False);assert self.snapshot(case)==before
        self.record('unknown-history-refuses-without-normalization')
    def catalog_adversaries(self):
        case='default';before=self.snapshot(case)
        e=self.db(case)
        try:
            with e.connect() as c:
                transaction=c.begin()
                try:
                    c.exec_driver_sql('ALTER DEFAULT PRIVILEGES IN SCHEMA access GRANT SELECT ON TABLES TO access_runtime; ALTER DEFAULT PRIVILEGES IN SCHEMA access GRANT EXECUTE ON FUNCTIONS TO access_runtime')
                    defaults=c.exec_driver_sql("SELECT defaclobjtype,defaclacl::text FROM pg_default_acl WHERE defaclnamespace=(SELECT oid FROM pg_namespace WHERE nspname='access') ORDER BY 1").all()
                    spec=importlib.util.spec_from_file_location('candidate4',ACCESS/'migrations/versions/0004_application_register.py')
                    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                    c.exec_driver_sql(module.SQL,execution_options={'no_parameters':True})
                    baseline.verify_catalog(c,'access_0004')
                    assert c.exec_driver_sql("SELECT defaclobjtype,defaclacl::text FROM pg_default_acl WHERE defaclnamespace=(SELECT oid FROM pg_namespace WHERE nspname='access') ORDER BY 1").all()==defaults
                finally:transaction.rollback()
        finally:e.dispose()
        assert self.snapshot(case)==before
        self.execute_sql(case,'ALTER DEFAULT PRIVILEGES IN SCHEMA access GRANT SELECT ON TABLES TO access_runtime')
        before=self.snapshot(case);self.migrate(case,success=False);assert self.snapshot(case)==before
        self.record('rollback-only-candidate-default-grantee-stripping-and-controlled-route-default-acl-refusal')
        for mutation in (
            'DROP TRIGGER operation_outcome_guard ON access.operation_outcome; CREATE TRIGGER operation_outcome_guard BEFORE INSERT OR UPDATE OR DELETE ON access.operation_outcome FOR EACH ROW EXECUTE FUNCTION access.registry_storage_immutable()',
            'SET LOCAL ROLE access_command_owner; ALTER FUNCTION access.register_application(uuid,text,text,text,bytea) SECURITY INVOKER; RESET ROLE',
            'GRANT UPDATE ON access.permissions TO access_command_owner',
        ):
            before=self.snapshot('clean');e=self.db('clean')
            try:
                with e.connect() as c:
                    transaction=c.begin()
                    try:
                        c.exec_driver_sql(mutation)
                        try:baseline.preflight(c)
                        except baseline.BaselineError:pass
                        else:raise AssertionError('catalog_drift_accepted')
                    finally:transaction.rollback()
            finally:e.dispose()
            assert self.snapshot('clean')==before
        self.record('rollback-trigger-binding-function-security-and-command-owner-extra-table-acl-refusals')
        spec=importlib.util.spec_from_file_location('identity_catalog_guard',ACCESS/'identity-migrations/identity_baseline.py')
        identity=importlib.util.module_from_spec(spec);spec.loader.exec_module(identity)
        url=self.db('integration','databases').url.set(username='supabase_admin')
        for mutation in ('GRANT access_command_owner TO access_operator WITH ADMIN FALSE, INHERIT FALSE, SET TRUE',
                         'CREATE SCHEMA access_evil; GRANT USAGE ON SCHEMA access_evil TO access_command_owner'):
            before=self.snapshot('integration');e=create_engine(url,hide_parameters=True,connect_args=CONNECTION_ARGS)
            try:
                with e.connect() as c:
                    transaction=c.begin()
                    try:
                        c.exec_driver_sql(mutation)
                        c.exec_driver_sql('SET LOCAL ROLE identity_migrator')
                        try:identity.verify_catalog(c,'account_actor_ensure')
                        except identity.BaselineError:pass
                        else:raise AssertionError('foreign-role-authority-accepted')
                    finally:transaction.rollback()
            finally:e.dispose()
            assert self.snapshot('integration')==before
        self.record('rollback-extra-role-edge-and-foreign-schema-usage-rejected-by-genuine-identity18-catalog')

    def malformed_sql(self):
        case='recovery';before=self.snapshot(case)
        for label,changes in malformed_sql_cases():
            value=document('malformed_sql');command=parse_command(json.dumps(value).encode())
            parameters=dict(operation=value['operation_id'],app=command.payload.app_id,reason=command.reason_code,
                evidence=command.evidence_ref,canonical=adapter.canonical_command(command))
            parameters.update(changes(parameters) if callable(changes) else changes)
            e=self.db(case,'access_operator_urls')
            try:
                try:
                    with e.begin() as c:
                        c.execute(text('SELECT * FROM access.register_application(CAST(:operation AS uuid),:app,:reason,:evidence,:canonical)'),parameters).all()
                except Exception as error:
                    original=getattr(error,'orig',None)
                    assert getattr(original,'sqlstate',None)=='AC005',label
                    assert original.diag.message_primary=='access_command_invalid',label
                else:raise AssertionError('malformed_sql_accepted:'+label)
            finally:e.dispose()
            assert self.snapshot(case)==before,label
        self.record('parameterized-direct-sql-malformed-arguments-utf8-envelope-canonical-duplicate-oversize-ac005-no-effects')

    def foreign_privilege_adversaries(self):
        case='integration';before=self.snapshot(case)
        url=self.db(case,'databases').url.set(username='supabase_admin')
        for role in ('access_operator','access_operator_authority_owner','access_command_owner'):
            for kind in ('schema','table','column','sequence','function'):
                e=create_engine(url,hide_parameters=True,connect_args=CONNECTION_ARGS)
                try:
                    with e.connect() as c:
                        transaction=c.begin()
                        try:
                            baseline.verify_operator_roles(c)
                            c.exec_driver_sql("CREATE SCHEMA access_foreign_fixture; CREATE TABLE access_foreign_fixture.secret(id integer,value text); CREATE SEQUENCE access_foreign_fixture.counter; CREATE FUNCTION access_foreign_fixture.privileged() RETURNS integer LANGUAGE sql SECURITY DEFINER AS 'SELECT 1'; REVOKE ALL ON FUNCTION access_foreign_fixture.privileged() FROM PUBLIC")
                            grants={
                                'schema':f'GRANT USAGE ON SCHEMA access_foreign_fixture TO {role}',
                                'table':f'GRANT SELECT ON access_foreign_fixture.secret TO {role}',
                                'column':f'GRANT SELECT(value) ON access_foreign_fixture.secret TO {role}',
                                'sequence':f'GRANT USAGE ON SEQUENCE access_foreign_fixture.counter TO {role}',
                                'function':f'GRANT USAGE ON SCHEMA access_foreign_fixture TO {role}; GRANT EXECUTE ON FUNCTION access_foreign_fixture.privileged() TO {role}',
                            }
                            c.exec_driver_sql(grants[kind])
                            try:baseline.verify_operator_roles(c)
                            except baseline.BaselineError as error:assert str(error)=='access_operator_roles_invalid'
                            else:raise AssertionError('foreign_privilege_accepted:'+role+':'+kind)
                        finally:transaction.rollback()
                        assert not c.exec_driver_sql("SELECT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname='access_foreign_fixture')").scalar_one()
                finally:e.dispose()
                assert self.snapshot(case)==before
        self.record('rollback-only-foreign-schema-table-column-sequence-privileged-function-denial-for-all-restricted-access-roles')

    def cli(self):
        from identity_operator_target import prepare_target
        case='cli';self.seed(case,'cli_app');run=json.loads((self.proof/'run.json').read_text())
        target_path=prepare_target(ROOT/'platform/deployment/environments/kdg-local.json',run['run_id'],owner='access',namespace=run['operator_namespace'])
        target=load_target(target_path,owner='access');assert target.database==self.db(case).url.database
        value=document('cli_app');command_path=self.proof/'cli-command.json';command_path.write_text(json.dumps(value));command_path.chmod(0o600)
        env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','PGPASSWORD':'ambient-ignored','PGSERVICE':'ambient-ignored'}
        common=[sys.executable,'-I','-B',str(ACCESS/'operator_cli.py')]
        execute=subprocess.run(common+['execute','--owner','access','--target',str(target_path),'--command-file',str(command_path)],env=env,capture_output=True,timeout=15)
        assert execute.returncode==0 and not execute.stderr,'cli_execute_failed'
        receipt=json.loads(execute.stdout);assert receipt['result']['target']=={'app_id':'cli_app'} and receipt['result']['revision']=='1'
        lookup=subprocess.run(common+['outcome','--owner','access','--target',str(target_path),'--command','application.register','--app-id','cli_app','--operation-id',value['operation_id']],env=env,capture_output=True,timeout=15)
        assert lookup.returncode==0 and json.loads(lookup.stdout)==receipt
        (self.proof/'cli-receipt.json').write_bytes(execute.stdout)
        self.record('owner-bound-real-isolated-cli-execute-and-recovery-with-ambient-libpq-ignored')
    def integration(self):
        case='integration';before=self.snapshot(case)
        env={'PATH':'/usr/bin:/bin','IDENTITY_MIGRATION_DATABASE_URL':self.private['owner_urls'][case].replace('postgresql:','postgresql+psycopg:')}
        result=subprocess.run([sys.executable,'-I','-B','-m','alembic','-c',str(ACCESS/'identity-alembic.ini'),'upgrade','head'],cwd=ROOT,env=env,capture_output=True,timeout=40)
        (self.proof/'identity18-after-access4.log').write_bytes(result.stdout+result.stderr)
        assert result.returncode==0,'genuine_identity18_repeat_after_access4_failed'
        assert self.snapshot(case)==before
        self.record('genuine-identity18-controlled-repeat-after-access4-without-raw-cross-owner-grants')
    def retained(self):
        for case in self.private['databases']:
            if case in ('drift','default'):continue
            e=self.db(case)
            try:
                with e.begin() as c:
                    c.exec_driver_sql('SET TRANSACTION READ ONLY');baseline.preflight(c);baseline.verify_postcondition(c)
            finally:e.dispose()
        self.record('retained-known-head-inspection')


def main():
    if not __debug__:raise RuntimeError('access_qualification_optimized_python_prohibited')
    parser=argparse.ArgumentParser();g=parser.add_mutually_exclusive_group(required=True);g.add_argument('--all',action='store_true');g.add_argument('--verify-retained',action='store_true');args=parser.parse_args()
    raw=Path(os.environ['ACCESS_QUALIFICATION_DIR'])
    assert '..' not in raw.parts
    proof=Path(os.path.abspath(raw))
    private,run=load_fixture(proof)
    witness=json.loads((proof/'bootstrap-source-custody.json').read_text());captured=source_snapshot(proof)
    assert witness['status']=='passed' and witness['before']==witness['after']==captured
    for name,digest in witness['logs'].items():assert sha256((proof/name).read_bytes()).hexdigest()==digest
    q=Qualification(proof,private)
    if args.all:
        (proof/'all-started').open('x').close()
        for method in (q.prepare_cases,q.functional,q.concurrency,q.response_loss_and_authority_wait,q.malformed_sql,q.attacks,q.drift,q.catalog_adversaries,q.foreign_privilege_adversaries,q.cli,q.integration,q.retained):method()
        states={case:q.snapshot(case) for case in private['databases']}
        (proof/'retained-state.json').write_text(json.dumps(states,indent=2)+'\n')
    else:
        assert json.loads((proof/'results.json').read_text())['status']=='passed'
        assert json.loads((proof/'retained-state.json').read_text())=={case:q.snapshot(case) for case in private['databases']}
        q.retained()
    assert captured==source_snapshot(proof),'qualification_source_changed'
    (proof/('results.json' if args.all else 'retained-results.json')).write_text(json.dumps(dict(status='passed',steps=q.results,source=captured),indent=2)+'\n')
    print(json.dumps(dict(ok=True,steps=q.results)))

if __name__=='__main__':
    try:main()
    except Exception:
        print(json.dumps(dict(ok=False,code='access_qualification_failed_requires_inspection')))
        raise SystemExit(1) from None
