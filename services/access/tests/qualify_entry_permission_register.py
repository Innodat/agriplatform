"""Fresh synthetic Access0006 proof; fixed custody and retained-state inspection."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import importlib.util
import json,os,sys,time
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_permission_register as prior
from sqlalchemy import create_engine,text
ROOT,ACCESS,ACTOR=prior.ROOT,prior.ACCESS,prior.ACTOR
adapter,baseline,parse_command=prior.adapter,prior.baseline,prior.parse_command
CASES=prior.CASES|{'exact6','eboundary','econcurrent','erecovery','efailure','elocks'}
prior.prior.CASES=CASES
PREVIOUS_ADAPTER_FILE='bootstrap_previous_permission_adapter.py'
PREVIOUS_ADAPTER_SHA256='f06e04098b759efcbeb900b4afe2d47b053414e2bec40d322773d0841d060791'

def previous_adapter(proof):
    path=proof/PREVIOUS_ADAPTER_FILE
    assert sha256(path.read_bytes()).hexdigest()==PREVIOUS_ADAPTER_SHA256,'previous_permission_adapter_source_mismatch'
    spec=importlib.util.spec_from_file_location('_previous_permission_adapter',path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module

def source_snapshot(proof):
    previous_adapter(proof)
    return {**prior.source_snapshot(proof),str(Path(__file__).resolve().relative_to(ROOT)):sha256(Path(__file__).read_bytes()).hexdigest()}

def document(permission='synthetic.read',app='synthetic_app',op=None):
    value=prior.prior.document(app,op);value['command']='entry_permission.register';value['payload']['permission']=permission
    return value

def require_aggregate_source(result,captured):
    assert result['status']=='passed' and result['source']==captured,'aggregate_source_mismatch'

def malformed_lookup_cases():
    return (
        ('null_operation',{'operation':None}),('nil_operation',{'operation':'00000000-0000-0000-0000-000000000000'}),
        ('null_app',{'app':None}),('invalid_app',{'app':'Uppercase'}),
        ('short_app',{'app':'a'}),('long_app',{'app':'a'*65}),
        ('null_permission',{'permission':None}),('empty_permission',{'permission':''}),
        ('nonascii_permission',{'permission':'é'}),('long_permission',{'permission':'a'*201}),
    )

class Qualification(prior.Qualification):
    def record(self,label):
        super().record(label)
        print(json.dumps(dict(stage=label,status="passed")),flush=True)
    def seed(self,case,app=None):
        super().seed(case,app)
        literal='NULL' if app is None else "'"+app+"'"
        self.execute_sql(case,f"INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_operator','entry_permission.register','platform',{literal},true,'{ACTOR}','{ACTOR}')")
    def e_outcome(self,case,value,**changes):
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:return adapter.outcome(c,value['operation_id'],command='entry_permission.register',app_id=changes.get('app',value['payload']['app_id']),permission=changes.get('permission',value['payload']['permission']))
        finally:engine.dispose()
    def setup_entry(self,case):
        self.setup_permission(case)
        self.command(case,prior.document())
    def entry_functional(self):
        case='eboundary';self.setup_entry(case)
        for literal,scope in (('a','account'),('a'*200,'organization'),(' \t\b\f\n\r\x01\x1f\x7f\\"/','organization')):
            self.command(case,prior.document(literal,scope=scope))
            value=document(literal);value.update(reason_code='setup_correction',evidence_ref='synthetic:entry-distinct')
            receipt=self.command(case,value);state=self.snapshot(case)
            assert receipt.result.disposition=='created' and receipt.result.revision is None
            row=next(r for r in state['entry_permissions'] if r[:2]==['synthetic_app',literal]);assert row[2]==ACTOR
            event=next(r for r in state['business_event'] if r[0]==receipt.result.event_id)
            outcome=next(r for r in state['operation_outcome'] if r[0]==event[8])
            assert row[3]==event[-1]==outcome[-1]==str(receipt.committed_at)
            assert event[1]=='access.entry_permission_registered' and event[9]=={'app_id':'synthetic_app','permission':literal} and event[10]=={} and event[-3:-1]==[value['reason_code'],value['evidence_ref']]
            assert self.command(case,value)==self.e_outcome(case,value)==receipt and self.snapshot(case)==state
            self.denied(lambda:self.command(case,{**value,'evidence_ref':'synthetic:changed'}),'operation_conflict')
            for changes in ({'app':'other_app'},{'permission':'wrong'}):self.denied(lambda:self.e_outcome(case,value,**changes),'access_denied')
            unchanged=self.command(case,document(literal));assert unchanged.result.disposition=='unchanged' and unchanged.result.event_id is None
            assert len(self.snapshot(case)['business_event'])==len(state['business_event'])
        before=self.snapshot(case)
        for value in (document('missing'),document(app='other_app'),document(app='missing_app')):self.denied(lambda:self.command(case,value),'operation_conflict')
        assert self.snapshot(case)==before
        assert self.e_outcome(case,document('unresolved')) is None
        # All three commands independently recover the same UUID, in both orders.
        for order in ('forward','reverse'):
            operation=str(uuid4());app='reuse_'+order;permission='reuse.'+order
            if order=='reverse':
                self.command(case,prior.prior.document(app));self.command(case,prior.document(permission,app=app))
            values=[prior.prior.document(app,operation),prior.document(permission,app=app,op=operation),document(permission,app=app,op=operation)]
            receipts={}
            for value in (values if order=='forward' else reversed(values)):receipts[value['command']]=self.command(case,value)
            state=self.snapshot(case)
            for value in values:
                assert self.command(case,value)==receipts[value['command']]
                engine=self.db(case,'access_operator_urls')
                try:
                    with engine.connect() as c:
                        kwargs={'command':value['command'],'app_id':app}
                        if value['command']!='application.register':kwargs['permission']=permission
                        assert adapter.outcome(c,operation,**kwargs)==receipts[value['command']]
                finally:engine.dispose()
            assert self.snapshot(case)==state
        self.record('entry-literal-bounds-both-scopes-multiple-bindings-atomic-evidence-three-command-uuid-both-orders')
    def entry_authority(self):
        case='elocks';self.setup_entry(case);value=document();receipt=self.command(case,value)
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='entry_permission.register'")
        before=self.snapshot(case)
        for fn in (lambda:self.command(case,value),lambda:self.e_outcome(case,value)):self.denied(fn,'access_denied')
        assert self.snapshot(case)==before
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=true; UPDATE access.operator_principals SET enabled=false")
        before=self.snapshot(case)
        for fn in (lambda:self.command(case,value),lambda:self.e_outcome(case,value)):self.denied(fn,'access_denied')
        assert self.snapshot(case)==before
        self.execute_sql(case,f"UPDATE access.operator_principals SET enabled=true; UPDATE access.operator_authorities SET enabled=false WHERE command='entry_permission.register'; INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_operator','entry_permission.register','platform','other_app',true,'{ACTOR}','{ACTOR}')")
        for fn in (lambda:self.command(case,value),lambda:self.e_outcome(case,value)):self.denied(fn,'access_denied')
        self.execute_sql(case,f"INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_operator','entry_permission.register','platform','synthetic_app',true,'{ACTOR}','{ACTOR}')")
        self.command(case,prior.document('scoped.only'))
        scoped=document('scoped.only');scoped_receipt=self.command(case,scoped)
        assert scoped_receipt.result.disposition=='created'
        state=self.snapshot(case)
        assert self.command(case,scoped)==self.e_outcome(case,scoped)==scoped_receipt
        assert self.snapshot(case)==state
        assert not any(r[2]=='entry_permission.register' and r[5] is None and r[7] for r in state['operator_authorities'])
        # Rollback-only role edges exercise assumed and inherited operator rights;
        # neither replaces the unregistered original session login.
        command=parse_command(json.dumps(scoped).encode())
        bound=dict(operation=command.operation_id,app='synthetic_app',permission='scoped.only',reason=command.reason_code,evidence=command.evidence_ref,canonical=adapter.canonical_command(command))
        statements=(('SELECT * FROM access.register_entry_permission(CAST(:operation AS uuid),:app,:permission,:reason,:evidence,:canonical)',bound),
            ('SELECT * FROM access.entry_permission_registration_outcome(CAST(:operation AS uuid),:app,:permission)',{k:bound[k] for k in ('operation','app','permission')}))
        url=self.db(case,'databases').url.set(username='supabase_admin')
        for mode in ('assumed','inherited'):
            for statement,parameters in statements:
                engine=create_engine(url,hide_parameters=True,connect_args=prior.CONNECTION_ARGS)
                try:
                    try:
                        with engine.begin() as c:
                            assert not c.exec_driver_sql("SELECT EXISTS(SELECT 1 FROM access.operator_principals WHERE database_login=session_user)").scalar_one()
                            if mode=='inherited':c.exec_driver_sql('GRANT access_operator TO postgres WITH ADMIN FALSE, INHERIT TRUE, SET TRUE')
                            c.exec_driver_sql('SET LOCAL ROLE '+('access_operator' if mode=='assumed' else 'postgres'))
                            assert c.exec_driver_sql("SELECT has_function_privilege(current_user,'access.entry_permission_registration_outcome(uuid,text,text)','EXECUTE')").scalar_one()
                            c.execute(text(statement),parameters).all()
                    except Exception as error:assert error.orig.sqlstate=='AC002' and error.orig.diag.message_primary=='access_denied'
                    else:raise AssertionError('entry_wrong_original_login_accepted')
                finally:engine.dispose()
                assert self.snapshot(case)==state
        self.record('entry-command-app-disabled-principal-execute-replay-lookup-authority-refusals')
    def entry_previous_and_repeat(self):
        case='exact6';self.seed(case);self.command(case,prior.prior.document());self.command(case,prior.document())
        value=document();receipt=self.command(case,value);state=self.snapshot(case);self.migrate(case)
        assert self.snapshot(case)==state and self.e_outcome(case,value)==receipt
        previous=previous_adapter(self.proof);value=prior.document('previous.permission')
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:receipt=previous.execute(c,json.dumps(value).encode())
            state=self.snapshot(case)
            with engine.connect() as c:
                assert previous.execute(c,json.dumps(value).encode())==receipt
                assert previous.outcome(c,value['operation_id'],command='permission.register',app_id='synthetic_app',permission='previous.permission')==receipt
            assert self.snapshot(case)==state
        finally:engine.dispose()
        self.record('populated6-repeat-and-actual-previous0005-adapter-create-replay-lookup')
    def entry_attacks(self):
        case='efailure';self.setup_entry(case);value=document();before=self.snapshot(case)
        self.execute_sql(case,"CREATE FUNCTION access.inject_failure() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic'; END $$; CREATE TRIGGER inject_failure BEFORE INSERT ON access.business_event FOR EACH ROW EXECUTE FUNCTION access.inject_failure()")
        self.denied(lambda:self.command(case,value),'operation_unavailable')
        self.execute_sql(case,'DROP TRIGGER inject_failure ON access.business_event; DROP FUNCTION access.inject_failure()');assert self.snapshot(case)==before
        try:self.execute_sql(case,f"INSERT INTO access.entry_permissions(app_id,permission,created_by,created_at) VALUES('synthetic_app','synthetic.read','{ACTOR}',statement_timestamp())")
        except Exception as error:
            assert error.orig.sqlstate=='23514' and error.orig.diag.message_primary=='access_required_registration_missing'
        else:raise AssertionError('missing_entry_evidence_accepted')
        assert self.snapshot(case)==before
        changes=list(prior.malformed_permission_sql_cases())
        changes=[(label,change) for label,change in changes if label not in ('null_scope','bad_scope')]
        for label,change in changes:
            value=document('malformed.sql');command=parse_command(json.dumps(value).encode())
            parameters=dict(operation=value['operation_id'],app='synthetic_app',permission='malformed.sql',reason=command.reason_code,evidence=command.evidence_ref,canonical=adapter.canonical_command(command))
            if label=='changed_envelope_command':change={'canonical':parameters['canonical'].replace(b'entry_permission.register',b'permission.register')}
            parameters.update(change(parameters) if callable(change) else change)
            engine=self.db(case,'access_operator_urls')
            try:
                try:
                    with engine.begin() as c:c.execute(text('SELECT * FROM access.register_entry_permission(CAST(:operation AS uuid),:app,:permission,:reason,:evidence,:canonical)'),parameters).all()
                except Exception as error:assert error.orig.sqlstate=='AC005' and error.orig.diag.message_primary=='access_command_invalid',label
                else:raise AssertionError('malformed_entry_sql_accepted:'+label)
            finally:engine.dispose()
            assert self.snapshot(case)==before
        for role in ('access_operator_urls',):
            for sql in ('SELECT * FROM access.entry_permissions','SET ROLE access_command_owner','INSERT INTO access.entry_permissions DEFAULT VALUES'):
                engine=self.db(case,role)
                try:
                    try:
                        with engine.begin() as c:c.exec_driver_sql(sql)
                    except Exception as error:assert error.orig.sqlstate=='42501'
                    else:raise AssertionError('raw_entry_attack_accepted')
                finally:engine.dispose()
        # Exact command authority cannot be supplied by SET ROLE or context settings.
        command=parse_command(json.dumps(document()).encode())
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.begin() as c:
                c.exec_driver_sql("SET LOCAL app.actor_id='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'")
                result=c.execute(text('SELECT * FROM access.register_entry_permission(CAST(:operation AS uuid),:app,:permission,:reason,:evidence,:canonical)'),dict(operation=command.operation_id,app='synthetic_app',permission='synthetic.read',reason=command.reason_code,evidence=command.evidence_ref,canonical=adapter.canonical_command(command))).one()
            assert next(r for r in self.snapshot(case)['entry_permissions'] if r[1]=='synthetic.read')[2]==ACTOR
        finally:engine.dispose()
        for forged in ('missing','transition','target','type','executor','operation','outcome'):
            self.command(case,prior.document('forged.'+str(forged)))
            outcome_id,event_id,operation_id=[str(uuid4()) for _ in range(3)]
            sql=f"""INSERT INTO access.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by)
            VALUES('access_migrator','{ACTOR}',true,'{ACTOR}','{ACTOR}');
            INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by)
            VALUES(gen_random_uuid(),'access_migrator','entry_permission.register','platform','synthetic_app',true,'{ACTOR}','{ACTOR}');
            SET LOCAL ROLE access_command_owner;
            INSERT INTO access.entry_permissions(app_id,permission,created_by,created_at) VALUES('synthetic_app','forged.{forged}','{ACTOR}',statement_timestamp());
            INSERT INTO access.operation_outcome(id,executor_actor_id,operation_id,command_type,scope_kind,command_version,fingerprint_version,fingerprint_algorithm,fingerprint,result_version,result)
            VALUES('{outcome_id}','{ACTOR}','{operation_id}','entry_permission.register','platform',1,1,'sha256',sha256('synthetic'::bytea),1,
            jsonb_build_object('target',jsonb_build_object('app_id','synthetic_app','permission','forged.{forged}'),'disposition','created','revision',NULL,'event_id','{event_id}'));
            """
            if forged!='missing':
                fields=dict(target="jsonb_build_object('app_id','synthetic_app','permission','forged."+forged+"')",event_type="'access.entry_permission_registered'",executor="'"+ACTOR+"'",operation="'"+operation_id+"'",outcome="'"+outcome_id+"'",transition="'{}'::jsonb")
                fields.update({
                    'transition':{'transition':"jsonb_build_object('scope_kind','account')"},
                    'target':{'target':"jsonb_build_object('app_id','other_app','permission','forged.target')"},
                    'type':{'event_type':"'access.permission_registered'"},
                    'executor':{'executor':"'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'"},
                    'operation':{'operation':"'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'"},
                    'outcome':{'outcome':"'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'"},
                }[forged])
                sql+=f"""INSERT INTO access.business_event(event_id,event_type,event_version,executor_actor_id,operation_id,outcome_id,target,transition,reason_code)
            VALUES('{event_id}',{fields['event_type']},1,{fields['executor']},{fields['operation']},{fields['outcome']},{fields['target']},{fields['transition']},'synthetic_fixture');"""
            if forged=='missing':sql+='SET CONSTRAINTS access.operation_outcome_required_event IMMEDIATE;'
            before=self.snapshot(case)
            try:self.execute_sql(case,sql)
            except Exception as error:
                assert error.orig.sqlstate=='23514'
                assert error.orig.diag.message_primary==('access_required_event_missing' if forged=='missing' else 'access_event_invalid')
            else:raise AssertionError('forged_or_missing_entry_evidence_accepted')
            assert self.snapshot(case)==before
        self.record('entry-evidence-injection-missing-evidence-atomic-rollback-malformed-canonical-and-raw-privilege-refusals')

    def entry_recovery(self):
        case='erecovery';self.setup_entry(case)
        for permission in ('lost.response','wait.revocation','lookup.wait.revocation'):self.command(case,prior.document(permission))
        value=document('lost.response')
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
        assert self.e_outcome(case,value)==self.command(case,value)
        value=document('wait.revocation');key=adapter.command_outcome_lock_key(ACTOR,parse_command(json.dumps(value).encode()))
        engine=self.db(case);connection=engine.connect();transaction=connection.begin()
        try:
            connection.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
            with ThreadPoolExecutor(max_workers=1) as pool:
                pending=pool.submit(self.command,case,value);self.wait_for_operator_lock(case)
                self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='entry_permission.register'")
                transaction.rollback();self.denied(lambda:pending.result(timeout=5),'access_denied')
        finally:
            if transaction.is_active:transaction.rollback()
            connection.close();engine.dispose()
        assert not any(row[1]=='wait.revocation' for row in self.snapshot(case)['entry_permissions'])
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=true WHERE command='entry_permission.register'")
        lookup_value=document('lookup.wait.revocation');lookup_receipt=self.command(case,lookup_value)
        assert lookup_receipt.result.disposition=='created'
        key=adapter.command_outcome_lock_key(ACTOR,parse_command(json.dumps(lookup_value).encode()))
        engine=self.db(case);connection=engine.connect();transaction=connection.begin()
        try:
            connection.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
            with ThreadPoolExecutor(max_workers=1) as pool:
                pending=pool.submit(self.e_outcome,case,lookup_value);self.wait_for_operator_lock(case)
                self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='entry_permission.register'")
                revoked=self.snapshot(case)
                transaction.rollback();self.denied(lambda:pending.result(timeout=5),'access_denied')
        finally:
            if transaction.is_active:transaction.rollback()
            connection.close();engine.dispose()
        assert self.snapshot(case)==revoked
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=true WHERE command='entry_permission.register'")
        self.command(case,prior.document('principal.wait.execute'))
        lookup=document('principal.wait.lookup');self.command(case,prior.document('principal.wait.lookup'));self.command(case,lookup)
        for action,value in ((self.command,document('principal.wait.execute')),(self.e_outcome,lookup)):
            self.execute_sql(case,'UPDATE access.operator_principals SET enabled=true')
            key=adapter.command_outcome_lock_key(ACTOR,parse_command(json.dumps(value).encode()))
            engine=self.db(case);c=engine.connect();transaction=c.begin()
            try:
                c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
                with ThreadPoolExecutor(max_workers=1) as pool:
                    pending=pool.submit(action,case,value);self.wait_for_operator_lock(case)
                    self.execute_sql(case,'UPDATE access.operator_principals SET enabled=false')
                    revoked=self.snapshot(case)
                    transaction.rollback();self.denied(lambda:pending.result(timeout=5),'access_denied')
            finally:
                if transaction.is_active:transaction.rollback()
                c.close();engine.dispose()
            assert self.snapshot(case)==revoked
        self.record('entry-real-commit-response-loss-and-witnessed-command-and-principal-execute-lookup-revocation')

    def entry_concurrency(self):
        case='econcurrent';self.setup_entry(case);value=document()
        key=adapter.command_outcome_lock_key(ACTOR,parse_command(json.dumps(value).encode()))
        self.command(case,prior.document('distinct.race'))
        for values in ([value,value],[document('distinct.race'),document('distinct.race')],[document(),None]):
            if values[1] is None:values[1]={**values[0],'evidence_ref':'synthetic:changed'}
            key=adapter.command_outcome_lock_key(ACTOR,parse_command(json.dumps(values[0]).encode()))
            if values[0]['operation_id']!=values[1]['operation_id']:
                domain='access:entry-permission:v1:'+json.dumps(['synthetic_app',values[0]['payload']['permission']])
                key=int.from_bytes(sha256(domain.encode()).digest()[:8],'big',signed=True)
                assert not any(r[1]=='distinct.race' for r in self.snapshot(case)['entry_permissions'])
            engine=self.db(case);c=engine.connect();transaction=c.begin()
            try:
                c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
                with ThreadPoolExecutor(max_workers=2) as pool:
                    futures=[pool.submit(self.command,case,v) for v in values]
                    self.wait_for_operator_lock(case,2);transaction.rollback();results=[]
                    for future in futures:
                        try:results.append(future.result(timeout=5))
                        except adapter.OperatorError as error:results.append(error.code)
                if values[0]==values[1]:assert results[0]==results[1]
                elif values[0]['operation_id']==values[1]['operation_id']:assert results.count('operation_conflict')==1
                else:
                    assert sorted(r.result.disposition for r in results)==['created','unchanged']
                    state=self.snapshot(case)
                    assert len([r for r in state['entry_permissions'] if r[:2]==['synthetic_app','distinct.race']])==1
                    assert len([r for r in state['business_event'] if r[1]=='access.entry_permission_registered' and r[9]=={'app_id':'synthetic_app','permission':'distinct.race'}])==1
                    assert len([r for r in state['operation_outcome'] if r[3]=='entry_permission.register' and r[-2]['target']=={'app_id':'synthetic_app','permission':'distinct.race'}])==2
                    for v,r in zip(values,results):assert self.command(case,v)==self.e_outcome(case,v)==r
                    assert self.snapshot(case)==state
            finally:
                if transaction.is_active:transaction.rollback()
                c.close();engine.dispose()
        value=document();command=parse_command(json.dumps(value).encode())
        domain='access:entry-permission:v1:'+json.dumps(['synthetic_app','synthetic.read'])
        for key,code in ((adapter.command_outcome_lock_key(ACTOR,command),'operation_busy'),(int.from_bytes(sha256(b'access:operator-authority:v1:access_operator').digest()[:8],'big',signed=True),'operation_unavailable'),(int.from_bytes(sha256(domain.encode()).digest()[:8],'big',signed=True),'operation_unavailable')):
            engine=self.db(case);c=engine.connect();transaction=c.begin()
            try:
                c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
                self.denied(lambda:self.command(case,value),code)
            finally:transaction.rollback();c.close();engine.dispose()
        for key,code in ((adapter.command_outcome_lock_key(ACTOR,command),'operation_busy'),(int.from_bytes(sha256(b'access:operator-authority:v1:access_operator').digest()[:8],'big',signed=True),'operation_unavailable')):
            before=self.snapshot(case);engine=self.db(case);c=engine.connect();transaction=c.begin()
            try:
                c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
                self.denied(lambda:self.e_outcome(case,value),code)
            finally:transaction.rollback();c.close();engine.dispose()
            assert self.snapshot(case)==before
        before=self.snapshot(case)
        for label,changes in (*malformed_lookup_cases(),('repeatable_read',{}),('serializable',{})):
            bound=dict(operation=value['operation_id'],app='synthetic_app',permission='synthetic.read');bound.update(changes)
            engine=self.db(case,'access_operator_urls')
            try:
                try:
                    with engine.begin() as c:
                        if label in ('repeatable_read','serializable'):c.exec_driver_sql('SET TRANSACTION ISOLATION LEVEL '+{'repeatable_read':'REPEATABLE READ','serializable':'SERIALIZABLE'}[label])
                        c.execute(text('SELECT * FROM access.entry_permission_registration_outcome(CAST(:operation AS uuid),:app,:permission)'),bound).all()
                except Exception as error:assert error.orig.sqlstate=='AC005' and error.orig.diag.message_primary=='access_command_invalid',label
                else:raise AssertionError('malformed_entry_lookup_accepted:'+label)
            finally:engine.dispose()
            assert self.snapshot(case)==before
        self.record('entry-witnessed-concurrent-duplicates-distinct-changed-retries-bounded-exact-lock-classification')
    def entry_cli(self):
        import subprocess
        from identity_operator_target import load_target
        run=json.loads((self.proof/'run.json').read_text())
        target=ROOT/'platform/deployment/.local/kdg'/run['run_id']/('access-operator-'+run['operator_namespace']+'.json')
        self.command('cli',prior.document('--owner',app='cli_app'))
        value=document('--owner',app='cli_app');path=self.proof/'entry-cli-command.json';path.write_text(json.dumps(value));path.chmod(0o600)
        common=[sys.executable,'-I','-B',str(ACCESS/'operator_cli.py')]
        env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'}
        result=subprocess.run(common+['execute','--owner','access','--target',str(target),'--command-file',str(path)],env=env,capture_output=True,timeout=15)
        assert result.returncode==0 and not result.stderr,'entry_cli_execute_failed'
        receipt=json.loads(result.stdout);assert receipt['result']['command']=='entry_permission.register' and receipt['result']['revision'] is None
        lookup=subprocess.run(common+['outcome','--owner','access','--target',str(target),'--command','entry_permission.register','--operation-id',value['operation_id'],'--app-id','cli_app','--permission=--owner'],env=env,capture_output=True,timeout=15)
        assert lookup.returncode==0 and json.loads(lookup.stdout)==receipt
        (self.proof/'entry-cli-receipt.json').write_bytes(result.stdout)
        self.record('real-isolated-entry-cli-typed-execute-and-literal-target-recovery')

def main():
    if not __debug__:raise RuntimeError('access_qualification_optimized_python_prohibited')
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True);group.add_argument('--all',action='store_true');group.add_argument('--verify-retained',action='store_true');args=parser.parse_args()
    raw=Path(os.environ['ACCESS_QUALIFICATION_DIR']);assert '..' not in raw.parts
    proof=Path(os.path.abspath(raw));private,run=prior.load_fixture(proof)
    witness=json.loads((proof/'bootstrap-source-custody.json').read_text());captured=source_snapshot(proof)
    assert witness['status']=='passed' and witness['before']==witness['after']==captured
    for name,digest in witness['logs'].items():assert sha256((proof/name).read_bytes()).hexdigest()==digest
    q=Qualification(proof,private)
    if args.all:
        (proof/'all-started').open('x').close()
        for method in (q.prepare_cases,q.functional,q.concurrency,q.response_loss_and_authority_wait,q.malformed_sql,q.attacks,q.drift,q.catalog_adversaries,q.foreign_privilege_adversaries,q.cli,q.permission_functional,q.permission_authority_boundaries,q.previous_application_adapter,q.permission_concurrency,q.permission_recovery,q.permission_attacks,q.permission_cli,q.entry_functional,q.entry_concurrency,q.entry_recovery,q.entry_attacks,q.entry_authority,q.entry_previous_and_repeat,q.entry_cli,q.integration,q.retained):method()
        (proof/'retained-state.json').write_text(json.dumps({case:q.snapshot(case) for case in private['databases']},indent=2)+'\n')
    else:
        require_aggregate_source(json.loads((proof/'results.json').read_text()),captured)
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
