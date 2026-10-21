"""Fresh synthetic Access0005 proof, reusing fixed Access registration custody."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from hashlib import sha256
import importlib.util
import json,os,sys,time
from pathlib import Path
import subprocess
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_application_register as prior
from sqlalchemy import create_engine,text
ROOT,ACCESS,ACTOR=prior.ROOT,prior.ACCESS,prior.ACTOR
adapter,baseline,parse_command,dev=prior.adapter,prior.baseline,prior.parse_command,prior.dev
CASES=prior.CASES|{'exact4','exact5','pboundary','plocks','pconcurrent','precovery','pfailure'}
prior.CASES=CASES
GROUP_LOGINS=prior.GROUP_LOGINS
CONNECTION_ARGS=prior.CONNECTION_ARGS
validate_fixture,load_fixture=prior.validate_fixture,prior.load_fixture

PREVIOUS_APPLICATION_ADAPTER_SHA256='36a93ba836dbe873ca8080d5694762d05b4cd8fa49a0c3a279e7a06536a6ddcb'
PREVIOUS_APPLICATION_ADAPTER_FILE='bootstrap_previous_application_adapter.py'

def previous_application_adapter_source(proof):
    # Captured from commit45ab5dfa before bootstrap custody, never from a target.
    path=proof/PREVIOUS_APPLICATION_ADAPTER_FILE
    assert sha256(path.read_bytes()).hexdigest()==PREVIOUS_APPLICATION_ADAPTER_SHA256,'previous_application_adapter_source_mismatch'
    return path

def load_previous_application_adapter(proof):
    path=previous_application_adapter_source(proof)
    spec=importlib.util.spec_from_file_location('_previous_application_adapter',path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module

def source_snapshot(proof):
    previous_application_adapter_source(proof)
    return {**prior.source_snapshot(proof),str(Path(__file__).resolve().relative_to(ROOT)):sha256(Path(__file__).read_bytes()).hexdigest()}

def document(permission='synthetic.read',app='synthetic_app',scope='account',op=None):
    value=prior.document(app,op)
    value['command']='permission.register';value['payload'].update(permission=permission,scope_kind=scope)
    return value

def malformed_permission_sql_cases():
    return tuple(prior.malformed_sql_cases())+(
        ('null_permission',{'permission':None}),('empty_permission',{'permission':''}),
        ('nonascii_permission',{'permission':'é'}),('long_permission',{'permission':'a'*201}),
        ('null_scope',{'scope':None}),('bad_scope',{'scope':'platform'}),
        ('escaped_nul',lambda parameters:{'canonical':parameters['canonical'].replace(b'malformed.sql',b'\\u0000')}))

class Qualification(prior.Qualification):
    def seed(self,case,app=None):
        super().seed(case,app)
        literal='NULL' if app is None else "'"+app+"'"
        self.execute_sql(case,f"INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_operator','permission.register','platform',{literal},true,'{ACTOR}','{ACTOR}')")
    def prepare_cases(self):
        for case,head in (('exact1','access_0001'),('exact2','access_0002'),('exact3','access_0003'),('exact4','access_0004'),('exact5','access_0005')):
            self.migrate(case,head)
            self.execute_sql(case,"SET LOCAL app.org_id='11111111-1111-4111-8111-111111111111'; SET LOCAL app.actor_id='historical'; INSERT INTO access.grants(org_id,id,user_id,permission) VALUES('11111111-1111-4111-8111-111111111111','preserved','22222222-2222-4222-8222-222222222222','pts.poetry.read')")
            if case=='exact3':self.execute_sql(case,f"INSERT INTO access.applications(app_id,revision,created_by,updated_by,created_at,updated_at) VALUES('exact_app',7,'{ACTOR}','{ACTOR}',statement_timestamp(),statement_timestamp())")
            if case in ('exact4','exact5'):
                super().seed(case)
                self.command(case,prior.document('preserved_app'))
                if case=='exact5':
                    self.execute_sql(case,f"INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_operator','permission.register','platform',true,'{ACTOR}','{ACTOR}')")
                    permission_command=document('preserved.permission',app='preserved_app',scope='organization')
                    permission_receipt=self.command(case,permission_command)
                    assert permission_receipt.result.disposition=='created' and permission_receipt.result.event_id is not None
                if case=='exact4':self.execute_sql(case,f"INSERT INTO access.permissions(permission,app_id,scope_kind,created_by,created_at) VALUES('preserved.permission','preserved_app','organization','{ACTOR}',statement_timestamp())")
            before=self.snapshot(case);self.migrate(case);after=self.snapshot(case)
            assert (after['grants']==before['grants'] if head!='access_0001' else [r[:-1] for r in after['grants']]==before['grants'])
            if case=='exact5':
                assert self.p_outcome(case,permission_command)==permission_receipt
                assert self.command(case,permission_command)==permission_receipt
                assert self.snapshot(case)==after
            for table in ('applications','permissions','entry_permissions','operator_principals','operator_authorities','operation_outcome','business_event'):
                if table in before:assert before[table]==after[table],table
        for case in self.private['databases']:
            if case=='default':self.migrate(case,'access_0003')
            elif case not in ('exact1','exact2','exact3','exact4','exact5'):self.migrate(case)
        self.record('clean-exact1-2-3-populated4-5-upgrade-repeat-preserve-all-prior-rows-and-receipts')
    def p_outcome(self,case,value,app=None,permission=None):
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as connection:return adapter.outcome(connection,value['operation_id'],command='permission.register',app_id=app or value['payload']['app_id'],permission=permission if permission is not None else value['payload']['permission'])
        finally:engine.dispose()
    def setup_permission(self,case):
        self.seed(case);self.command(case,prior.document());self.command(case,prior.document('other_app'))
    def permission_functional(self):
        case='pboundary';self.setup_permission(case)
        for literal,scope in (('a','account'),('a'*200,'organization'),(' \t\b\f\n\r\x01\x1f\x7f\\"/','organization')):
            value=document(literal,scope=scope);value.update(reason_code='setup_correction',evidence_ref='synthetic:permission-distinct')
            receipt=self.command(case,value);assert receipt.result.revision is None and receipt.result.disposition=='created'
            assert receipt.result.target.permission==literal
            state=self.snapshot(case);row=next(r for r in state['permissions'] if r[0]==literal)
            assert row[:4]==[literal,'synthetic_app',scope,ACTOR]
            event=next(r for r in state['business_event'] if r[0]==receipt.result.event_id)
            assert event[1]=='access.permission_registered' and event[9]=={'app_id':'synthetic_app','permission':literal} and event[10]=={'scope_kind':scope} and event[-3:-1]==[value['reason_code'],value['evidence_ref']]
            assert self.command(case,value)==self.p_outcome(case,value)==receipt and self.snapshot(case)==state
            self.denied(lambda:self.command(case,{**value,'evidence_ref':'synthetic:changed'}),'operation_conflict')
            self.denied(lambda:self.command(case,document(literal,app='other_app',scope=scope)),'operation_conflict')
            self.denied(lambda:self.command(case,document(literal,scope='organization' if scope=='account' else 'account')),'operation_conflict')
            assert self.snapshot(case)==state
            self.denied(lambda:self.p_outcome(case,value,app='other_app'),'access_denied')
            self.denied(lambda:self.p_outcome(case,value,permission='wrong.permission'),'access_denied')
            assert self.p_outcome(case,document('unresolved')) is None
            unchanged=self.command(case,document(literal,scope=scope));assert unchanged.result.disposition=='unchanged' and unchanged.result.event_id is None
            assert len(self.snapshot(case)['business_event'])==len(state['business_event'])
        self.denied(lambda:self.command(case,document(app='missing_app')),'operation_conflict')
        # The same operation belongs independently to each exact command.
        operation=str(uuid4());app=prior.document('cross_command',operation);app_receipt=self.command(case,app)
        value=document('cross.command',app='cross_command',op=operation);permission_receipt=self.command(case,value)
        assert self.outcome(case,operation,'cross_command')==app_receipt and self.p_outcome(case,value)==permission_receipt
        assert self.command(case,app)==app_receipt and self.command(case,value)==permission_receipt
        # Reverse the order against an already registered app: a permission outcome
        # must not be mistaken for the following application no-op receipt.
        reverse_operation=str(uuid4());reverse_permission=document('permission.first',op=reverse_operation)
        reverse_permission_receipt=self.command(case,reverse_permission)
        reverse_app=prior.document('synthetic_app',reverse_operation)
        reverse_app_receipt=self.command(case,reverse_app)
        assert reverse_permission_receipt.result.disposition=='created' and reverse_app_receipt.result.disposition=='unchanged'
        state=self.snapshot(case)
        assert self.command(case,reverse_permission)==reverse_permission_receipt
        assert self.command(case,reverse_app)==reverse_app_receipt
        assert self.p_outcome(case,reverse_permission)==reverse_permission_receipt
        assert self.outcome(case,reverse_operation,'synthetic_app')==reverse_app_receipt
        assert self.snapshot(case)==state
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='permission.register'")
        before=self.snapshot(case)
        self.denied(lambda:self.command(case,value),'access_denied');self.denied(lambda:self.p_outcome(case,value),'access_denied')
        assert self.snapshot(case)==before
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=true; UPDATE access.operator_principals SET enabled=false")
        before=self.snapshot(case)
        for fn in (lambda:self.command(case,value),lambda:self.command(case,document('new')),lambda:self.p_outcome(case,value)):self.denied(fn,'access_denied')
        assert self.snapshot(case)==before
        exact=document('exact.permission',app='exact_app');self.command('exact3',exact)
        self.denied(lambda:self.command('exact3',document('wrong.application',app='other_app')),'access_denied')
        self.record('literal-ascii-bounds-both-scopes-atomic-attribution-event-immutable-mapping-command-isolation-current-authority-recovery')
    def previous_application_adapter(self):
        previous=load_previous_application_adapter(self.proof)
        case='exact5';value=prior.document('previous_adapter_app')
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as connection:receipt=previous.execute(connection,json.dumps(value).encode())
            assert receipt.result.disposition=='created'
            state=self.snapshot(case)
            with engine.connect() as connection:
                assert previous.execute(connection,json.dumps(value).encode())==receipt
                assert previous.outcome(connection,value['operation_id'],app_id='previous_adapter_app')==receipt
            assert self.snapshot(case)==state
            # Both versions also recover the original populated5 application receipt.
            original=next(row for row in state['operation_outcome'] if row[3]=='application.register' and row[13]['target']=={'app_id':'preserved_app'})
            with engine.connect() as connection:old_receipt=previous.outcome(connection,original[2],app_id='preserved_app')
            assert asdict(old_receipt)==asdict(self.outcome(case,original[2],'preserved_app'))
            assert self.snapshot(case)==state
        finally:engine.dispose()
        self.record('actual-fixed-sha-45ab5dfa-application-adapter-execute-replay-lookup-on5-original-receipt-preserved')
    def permission_authority_boundaries(self):
        case='exact4';value=document('application.only',app='preserved_app')
        before=self.snapshot(case)
        assert before['operator_principals'][0][2] is True
        assert {row[2] for row in before['operator_authorities']}=={'application.register'}
        for fn in (lambda:self.command(case,value),lambda:self.p_outcome(case,value)):self.denied(fn,'access_denied')
        assert self.snapshot(case)==before
        # A callable definer/current role and an enabled mapping for another login
        # cannot replace original-session identity. The migrator has no principal here.
        command=parse_command(json.dumps(value).encode())
        parameters=dict(operation=value['operation_id'],app='preserved_app',permission='application.only',scope='account',reason=command.reason_code,evidence=command.evidence_ref,canonical=adapter.canonical_command(command))
        statements=(
            ('SELECT * FROM access.register_permission(CAST(:operation AS uuid),:app,:permission,:scope,:reason,:evidence,:canonical)',parameters),
            ('SELECT * FROM access.permission_registration_outcome(CAST(:operation AS uuid),:app,:permission)',{k:parameters[k] for k in ('operation','app','permission')}))
        for statement,bound in statements:
            engine=self.db(case)
            try:
                try:
                    with engine.begin() as connection:
                        connection.exec_driver_sql('SET LOCAL ROLE access_command_owner')
                        connection.execute(text(statement),bound).all()
                except Exception as error:
                    original=getattr(error,'orig',None)
                    assert getattr(original,'sqlstate',None)=='AC002' and original.diag.message_primary=='access_denied'
                else:raise AssertionError('wrong_original_login_accepted')
            finally:engine.dispose()
            assert self.snapshot(case)==before
        self.record('application-only-authority-and-enabled-other-principal-wrong-original-login-execute-lookup-denied')
    def permission_concurrency(self):
        case='pconcurrent';self.setup_permission(case)
        def overlap(values,key):
            engine=self.db(case);connection=engine.connect();transaction=connection.begin()
            try:
                connection.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
                with ThreadPoolExecutor(max_workers=2) as pool:
                    futures=[pool.submit(self.command,case,value) for value in values]
                    self.wait_for_operator_lock(case,2);transaction.rollback();results=[]
                    for future in futures:
                        try:results.append(future.result(timeout=5))
                        except adapter.OperatorError as error:assert error.code=='operation_conflict';results.append(error.code)
                    return results
            finally:
                if transaction.is_active:transaction.rollback()
                connection.close();engine.dispose()
        value=document('same.operation');key=adapter.command_outcome_lock_key(ACTOR,parse_command(json.dumps(value).encode()))
        results=overlap([value,value],key);assert results[0]==results[1]
        for permission,values in (
            ('different.operations',[document('different.operations'),document('different.operations')]),
            ('cross.app',[document('cross.app'),document('cross.app',app='other_app')]),
            ('cross.scope',[document('cross.scope'),document('cross.scope',scope='organization')])):
            key=int.from_bytes(sha256(('access:permission:v1:'+permission).encode()).digest()[:8],'big',signed=True)
            results=overlap(values,key)
            if permission=='different.operations':assert sorted(r.result.disposition for r in results)==['created','unchanged']
            else:assert results.count('operation_conflict')==1
        value=document('changed.retry');other={**value,'evidence_ref':'synthetic:changed'}
        results=overlap([value,other],adapter.command_outcome_lock_key(ACTOR,parse_command(json.dumps(value).encode())))
        assert results.count('operation_conflict')==1
        self.setup_permission('plocks');value=document();command=parse_command(json.dumps(value).encode())
        for key,code in ((adapter.command_outcome_lock_key(ACTOR,command),'operation_busy'),(int.from_bytes(sha256(b'access:operator-authority:v1:access_operator').digest()[:8],'big',signed=True),'operation_unavailable'),(int.from_bytes(sha256(b'access:permission:v1:synthetic.read').digest()[:8],'big',signed=True),'operation_unavailable')):
            engine=self.db('plocks');connection=engine.connect();transaction=connection.begin()
            try:
                connection.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
                started=time.monotonic();self.denied(lambda:self.command('plocks',value),code);assert time.monotonic()-started<7
            finally:transaction.rollback();connection.close();engine.dispose()
        assert not self.snapshot('plocks')['permissions']
        self.record('witnessed-permission-retry-change-app-scope-collisions-and-exact-busy-vs-authority-domain-timeout')
    def permission_recovery(self):
        case='precovery';self.setup_permission(case);value=document('lost.response')
        class LostCommit:
            def __init__(self,transaction):self.transaction=transaction
            def __enter__(self):return self.transaction.__enter__()
            def __exit__(self,*args):
                answer=self.transaction.__exit__(*args)
                if args[0] is None:raise RuntimeError('synthetic_lost_response')
                return answer
        class Connection:
            def __init__(self,connection):self.wrapped=connection
            def __getattr__(self,name):return getattr(self.wrapped,name)
            def begin(self):return LostCommit(self.wrapped.begin())
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as connection:self.denied(lambda:adapter.execute(Connection(connection),json.dumps(value).encode()),'operation_unavailable')
        finally:engine.dispose()
        assert self.p_outcome(case,value)==self.command(case,value)
        value=document('wait.revocation');key=adapter.command_outcome_lock_key(ACTOR,parse_command(json.dumps(value).encode()))
        engine=self.db(case);connection=engine.connect();transaction=connection.begin()
        try:
            connection.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
            with ThreadPoolExecutor(max_workers=1) as pool:
                pending=pool.submit(self.command,case,value);self.wait_for_operator_lock(case)
                self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='permission.register'")
                transaction.rollback();self.denied(lambda:pending.result(timeout=5),'access_denied')
        finally:
            if transaction.is_active:transaction.rollback()
            connection.close();engine.dispose()
        assert not any(row[0]=='wait.revocation' for row in self.snapshot(case)['permissions'])
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=true WHERE command='permission.register'")
        lookup_value=document('lookup.wait.revocation');lookup_receipt=self.command(case,lookup_value)
        assert lookup_receipt.result.disposition=='created'
        key=adapter.command_outcome_lock_key(ACTOR,parse_command(json.dumps(lookup_value).encode()))
        engine=self.db(case);connection=engine.connect();transaction=connection.begin()
        try:
            connection.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
            with ThreadPoolExecutor(max_workers=1) as pool:
                pending=pool.submit(self.p_outcome,case,lookup_value);self.wait_for_operator_lock(case)
                self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='permission.register'")
                revoked=self.snapshot(case)
                transaction.rollback();self.denied(lambda:pending.result(timeout=5),'access_denied')
        finally:
            if transaction.is_active:transaction.rollback()
            connection.close();engine.dispose()
        assert self.snapshot(case)==revoked
        self.record('permission-real-commit-response-loss-and-witnessed-execute-and-lookup-revocation-after-wait')
    def permission_attacks(self):
        case='pfailure';self.setup_permission(case);value=document()
        self.execute_sql(case,"CREATE FUNCTION access.inject_failure() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic'; END $$; CREATE TRIGGER inject_failure BEFORE INSERT ON access.business_event FOR EACH ROW EXECUTE FUNCTION access.inject_failure()")
        before=self.snapshot(case);self.denied(lambda:self.command(case,value),'operation_unavailable');assert self.snapshot(case)==before
        self.execute_sql(case,'DROP TRIGGER inject_failure ON access.business_event; DROP FUNCTION access.inject_failure()')
        before=self.snapshot(case)
        try:self.execute_sql(case,f"INSERT INTO access.permissions(permission,app_id,scope_kind,created_by,created_at) VALUES('missing.evidence','synthetic_app','account','{ACTOR}',statement_timestamp())")
        except Exception as error:assert getattr(getattr(error,'orig',None),'sqlstate',None)=='23514'
        else:raise AssertionError('permission_missing_evidence_accepted')
        assert self.snapshot(case)==before
        # Direct SQL uses the same full-envelope boundary as the adapter.
        cases=malformed_permission_sql_cases()
        for label,changes in cases:
            value=document('malformed.sql');command=parse_command(json.dumps(value).encode())
            parameters=dict(operation=value['operation_id'],app='synthetic_app',permission='malformed.sql',scope='account',reason=command.reason_code,evidence=command.evidence_ref,canonical=adapter.canonical_command(command))
            # Prior command mutation must change the permission command in this slice.
            if label=='changed_envelope_command':changes={'canonical':parameters['canonical'].replace(b'permission.register',b'application.register')}
            parameters.update(changes(parameters) if callable(changes) else changes)
            engine=self.db(case,'access_operator_urls')
            try:
                try:
                    with engine.begin() as connection:connection.execute(text('SELECT * FROM access.register_permission(CAST(:operation AS uuid),:app,:permission,:scope,:reason,:evidence,:canonical)'),parameters).all()
                except Exception as error:
                    original=getattr(error,'orig',None)
                    assert getattr(original,'sqlstate',None)=='AC005' and original.diag.message_primary=='access_command_invalid',label
                else:raise AssertionError('malformed_permission_sql_accepted:'+label)
            finally:engine.dispose()
            assert self.snapshot(case)==before,label
        # GUCs cannot select the executor; SET ROLE/raw SQL privileges remain closed.
        value=document('guc.proof');command=parse_command(json.dumps(value).encode());engine=self.db(case,'access_operator_urls')
        try:
            with engine.begin() as connection:
                connection.exec_driver_sql("SET LOCAL app.actor_id='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'")
                connection.execute(text('SELECT * FROM access.register_permission(CAST(:operation AS uuid),:app,:permission,:scope,:reason,:evidence,:canonical)'),dict(operation=value['operation_id'],app='synthetic_app',permission='guc.proof',scope='account',reason=command.reason_code,evidence=command.evidence_ref,canonical=adapter.canonical_command(command))).all()
        finally:engine.dispose()
        assert next(row for row in self.snapshot(case)['permissions'] if row[0]=='guc.proof')[3]==ACTOR
        for case_role in ('access_operator_urls',):
            for sql in ('SELECT * FROM access.permissions','SET ROLE access_command_owner','SET ROLE access_operator_authority_owner','INSERT INTO access.permissions DEFAULT VALUES'):
                engine=self.db(case,case_role)
                try:
                    try:
                        with engine.begin() as connection:connection.exec_driver_sql(sql)
                    except Exception as error:assert getattr(getattr(error,'orig',None),'sqlstate',None)=='42501'
                    else:raise AssertionError('permission_operator_privilege_attack_succeeded')
                finally:engine.dispose()
        for forged in (False,True):
            outcome_id,event_id,operation_id=[str(uuid4()) for _ in range(3)]
            sql=f"""INSERT INTO access.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by)
            VALUES('access_migrator','{ACTOR}',true,'{ACTOR}','{ACTOR}');
            INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by)
            VALUES(gen_random_uuid(),'access_migrator','permission.register','platform','synthetic_app',true,'{ACTOR}','{ACTOR}');
            SET LOCAL ROLE access_command_owner;
            INSERT INTO access.permissions(permission,app_id,scope_kind,created_by,created_at) VALUES('forged.evidence','synthetic_app','account','{ACTOR}',statement_timestamp());
            INSERT INTO access.operation_outcome(id,executor_actor_id,operation_id,command_type,scope_kind,command_version,fingerprint_version,fingerprint_algorithm,fingerprint,result_version,result)
            VALUES('{outcome_id}','{ACTOR}','{operation_id}','permission.register','platform',1,1,'sha256',sha256('synthetic'::bytea),1,
            jsonb_build_object('target',jsonb_build_object('app_id','synthetic_app','permission','forged.evidence'),'disposition','created','revision',NULL,'event_id','{event_id}'));
            """
            if forged:sql+=f"""INSERT INTO access.business_event(event_id,event_type,event_version,executor_actor_id,operation_id,outcome_id,target,transition,reason_code)
            VALUES('{event_id}','access.application_registered',1,'{ACTOR}','{operation_id}','{outcome_id}',jsonb_build_object('app_id','synthetic_app','permission','forged.evidence'),jsonb_build_object('scope_kind','account'),'synthetic_fixture');"""
            if not forged:sql+='SET CONSTRAINTS access.operation_outcome_required_event IMMEDIATE;'
            before=self.snapshot(case)
            try:self.execute_sql(case,sql)
            except Exception as error:
                original=getattr(error,'orig',None)
                assert getattr(original,'sqlstate',None)=='23514'
                assert original.diag.message_primary==('access_event_invalid' if forged else 'access_required_event_missing')
            else:raise AssertionError('forged_or_missing_permission_evidence_accepted')
            assert self.snapshot(case)==before
        self.record('permission-evidence-failure-atomic-rollback-missing-evidence-direct-sql-closure-and-guc-attribution')
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
            'GRANT UPDATE ON access.entry_permissions TO access_command_owner',
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

    def permission_cli(self):
        from identity_operator_target import load_target
        case='cli';run=json.loads((self.proof/'run.json').read_text())
        target=ROOT/'platform/deployment/.local/kdg'/run['run_id']/('access-operator-'+run['operator_namespace']+'.json')
        assert load_target(target,owner='access').database==self.db(case).url.database
        value=document('--owner',app='cli_app');path=self.proof/'permission-cli-command.json';path.write_text(json.dumps(value));path.chmod(0o600)
        common=[sys.executable,'-I','-B',str(ACCESS/'operator_cli.py')];env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','PGPASSWORD':'ambient-ignored','PGSERVICE':'ambient-ignored'}
        result=subprocess.run(common+['execute','--owner','access','--target',str(target),'--command-file',str(path)],env=env,capture_output=True,timeout=15)
        assert result.returncode==0 and not result.stderr,'permission_cli_execute_failed'
        receipt=json.loads(result.stdout);assert receipt['result']['target']=={'app_id':'cli_app','permission':'--owner'} and receipt['result']['revision'] is None
        lookup=subprocess.run(common+['outcome','--owner','access','--target',str(target),'--command','permission.register','--operation-id',value['operation_id'],'--app-id','cli_app','--permission=--owner'],env=env,capture_output=True,timeout=15)
        assert lookup.returncode==0 and json.loads(lookup.stdout)==receipt
        (self.proof/'permission-cli-receipt.json').write_bytes(result.stdout)
        self.record('real-isolated-permission-cli-typed-execute-and-exact-target-recovery')

def main():
    if not __debug__:raise RuntimeError('access_qualification_optimized_python_prohibited')
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True);group.add_argument('--all',action='store_true');group.add_argument('--verify-retained',action='store_true');args=parser.parse_args()
    raw=Path(os.environ['ACCESS_QUALIFICATION_DIR']);assert '..' not in raw.parts
    proof=Path(os.path.abspath(raw));private,run=load_fixture(proof)
    witness=json.loads((proof/'bootstrap-source-custody.json').read_text());captured=source_snapshot(proof)
    assert witness['status']=='passed' and witness['before']==witness['after']==captured
    for name,digest in witness['logs'].items():assert sha256((proof/name).read_bytes()).hexdigest()==digest
    q=Qualification(proof,private)
    if args.all:
        (proof/'all-started').open('x').close()
        for method in (q.prepare_cases,q.functional,q.concurrency,q.response_loss_and_authority_wait,q.malformed_sql,q.attacks,q.drift,q.catalog_adversaries,q.foreign_privilege_adversaries,q.cli,q.permission_functional,q.permission_authority_boundaries,q.previous_application_adapter,q.permission_concurrency,q.permission_recovery,q.permission_attacks,q.permission_cli,q.integration,q.retained):method()
        (proof/'retained-state.json').write_text(json.dumps({case:q.snapshot(case) for case in private['databases']},indent=2)+'\n')
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
