"""Fresh Access7 synthetic matrix with source custody and retained verification."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from hashlib import sha256
import importlib.util
import json,os,subprocess,sys,time
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_entry_permission_register as prior
from sqlalchemy import create_engine,text
ROOT,ACCESS,ACTOR=prior.ROOT,prior.ACCESS,prior.ACTOR
adapter,baseline,parse_command=prior.adapter,prior.baseline,prior.parse_command
CASES=prior.CASES|{'exact7','sboundary','sauthority','sconcurrent','srecovery','sfailure','smax','slegacy'}
prior.prior.prior.CASES=CASES
PREVIOUS_FILE='bootstrap_previous_entry_adapter.py'
PREVIOUS_HASH='94d2849aebed1f8a6edb436b526397e80a422d27328781339b2e5814e1462d13'

def previous_adapter(proof):
    path=proof/PREVIOUS_FILE
    assert sha256(path.read_bytes()).hexdigest()==PREVIOUS_HASH,'previous_entry_adapter_source_mismatch'
    spec=importlib.util.spec_from_file_location('_previous_entry_adapter',path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module

def source_snapshot(proof):
    previous_adapter(proof)
    return {**prior.source_snapshot(proof),str(Path(__file__).resolve().relative_to(ROOT)):sha256(Path(__file__).read_bytes()).hexdigest()}

def document(enabled=True,revision='1',app='synthetic_app',op=None):
    value=prior.prior.prior.document(app,op);value['command']='application.set_enabled'
    value['payload']=dict(app_id=app,enabled=enabled,expected_revision=revision)
    return value

def bound(value):
    command=parse_command(json.dumps(value).encode())
    return dict(operation=command.operation_id,app=command.payload.app_id,enabled=command.payload.enabled,revision=command.payload.expected_revision,
        reason=command.reason_code,evidence=command.evidence_ref,canonical=adapter.canonical_command(command))
EXECUTE='SELECT * FROM access.set_application_enabled(CAST(:operation AS uuid),:app,:enabled,:revision,:reason,:evidence,:canonical)'
LOOKUP='SELECT * FROM access.application_enablement_outcome(CAST(:operation AS uuid),:app)'
TABLES=('grants','applications','permissions','entry_permissions','operator_principals','operator_authorities','operation_outcome','business_event')

class Qualification(prior.Qualification):
    def seed(self,case,app=None):
        super().seed(case,app)
        literal='NULL' if app is None else "'"+app+"'"
        self.execute_sql(case,f"INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_operator','application.set_enabled','platform',{literal},true,'{ACTOR}','{ACTOR}')")
    def prepare_cases(self):
        # Parent explicitly prepares1..5; reserve actual6 for populated pre-upgrade proof.
        for case,head in (('exact6','access_0006'),('smax','access_0003'),('slegacy','access_0003')):self.migrate(case,head)
        prior.prior.prior.Qualification.seed(self,'exact6')
        for cmd in ('permission.register','entry_permission.register'):
            self.execute_sql('exact6',f"INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_operator','{cmd}','platform',true,'{ACTOR}','{ACTOR}')")
        self.previous6_values=[prior.prior.prior.document(),prior.prior.document(),prior.document()]
        self.previous6_receipts=[self.command('exact6',v) for v in self.previous6_values]
        self.populated6=self.snapshot('exact6')
        assert self.populated6['alembic_version']==[['access_0006']]
        for case,revision in (('smax',9223372036854775807),('slegacy',7)):
            self.execute_sql(case,f"INSERT INTO access.applications(app_id,revision,created_by,updated_by,created_at,updated_at) VALUES('synthetic_app',{revision},'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb','cccccccc-cccc-4ccc-8ccc-cccccccccccc','2001-01-01Z','2002-01-01Z')")
        # Parent's default-head iteration upgrades these already populated cases.
        super().prepare_cases()
        after=self.snapshot('exact6')
        for table in TABLES:assert after[table]==self.populated6[table],table
        for v,r in zip(self.previous6_values,self.previous6_receipts):assert self.command('exact6',v)==r
        self.record('actual-populated6-upgrade7-retains-all-rows-and-three-command-receipts')
    def s_outcome(self,case,value,app=None):
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:return adapter.outcome(c,value['operation_id'],command='application.set_enabled',app_id=app or value['payload']['app_id'])
        finally:engine.dispose()
    def s_setup(self,case):
        self.seed(case);self.command(case,prior.prior.prior.document());self.command(case,prior.prior.document());self.command(case,prior.document())
    def sql_refusal(self,case,sql,parameters,state,message=None,role='access_operator_urls',isolation=None,force_event=False):
        engine=self.db(case,role)
        try:
            try:
                with engine.begin() as c:
                    if isolation:c.exec_driver_sql('SET TRANSACTION ISOLATION LEVEL '+isolation)
                    c.execute(text(sql),parameters).all()
                    if force_event:c.exec_driver_sql('SET CONSTRAINTS access.operation_outcome_required_event IMMEDIATE')
            except Exception as error:
                assert getattr(getattr(error,'orig',None),'sqlstate',None)==state,(message,'unexpected_sqlstate')
                if message:assert error.orig.diag.message_primary==message,(message,'unexpected_guard')
            else:raise AssertionError('expected_refusal_missing:'+str(message))
        finally:engine.dispose()
    def enablement_functional(self):
        case='sboundary';self.s_setup(case)
        self.execute_sql(case,"SET LOCAL app.org_id='11111111-1111-4111-8111-111111111111'; SET LOCAL app.actor_id='historical_synthetic'; INSERT INTO access.grants(org_id,id,user_id,permission,membership_id) VALUES('11111111-1111-4111-8111-111111111111','availability_preserved','22222222-2222-4222-8222-222222222222','pts.poetry.read',1)")
        original=self.snapshot(case);before=original
        assert len(original['grants'])==1 and original['grants'][0][1]=='availability_preserved'
        receipts=[]
        for enabled,revision in ((True,'1'),(False,'2'),(True,'3')):
            value=document(enabled,revision);value.update(reason_code='setup_correction',evidence_ref='synthetic:set-enabled')
            receipt=self.command(case,value);assert receipt.result.disposition=='changed' and receipt.result.revision==str(int(revision)+1)
            state=self.snapshot(case);old=before['applications'][0];app=state['applications'][0]
            assert app[0]==old[0] and app[1:3]==[enabled,int(revision)+1] and app[3]==old[3] and app[4]==ACTOR and app[5]==old[5]
            event=next(r for r in state['business_event'] if r[0]==receipt.result.event_id)
            outcome=next(r for r in state['operation_outcome'] if r[0]==event[8])
            assert app[6]==event[-1]==outcome[-1]==str(receipt.committed_at)
            assert event[1]=='access.application_availability_changed' and event[9]=={'app_id':'synthetic_app'}
            assert event[10]=={'before':{'enabled':not enabled,'revision':revision},'after':{'enabled':enabled,'revision':receipt.result.revision}}
            assert event[-3:-1]==[value['reason_code'],value['evidence_ref']]
            for table in ('grants','permissions','entry_permissions'):assert state[table]==original[table]
            assert self.command(case,value)==self.s_outcome(case,value)==receipt and self.snapshot(case)==state
            self.denied(lambda:self.command(case,{**value,'evidence_ref':'synthetic:changed'}),'operation_conflict')
            receipts.append((value,receipt));before=state
        # Older successful retry precedes current revision; targeted receipt stays original.
        for value,receipt in receipts:assert self.command(case,value)==self.s_outcome(case,value)==receipt
        state=self.snapshot(case)
        unchanged=self.command(case,document(True,'4'));after=self.snapshot(case)
        assert unchanged.result.disposition=='unchanged' and unchanged.result.revision=='4' and unchanged.result.event_id is None
        for table in ('applications','business_event','grants','permissions','entry_permissions'):assert after[table]==state[table]
        state=after
        for value in (document(True,'1'),document(False,'1'),document(app='missing_app')):self.denied(lambda:self.command(case,value),'operation_conflict')
        assert self.snapshot(case)==state
        assert self.s_outcome(case,document()) is None
        self.denied(lambda:self.s_outcome(case,receipts[0][0],'other_app'),'access_denied')
        # All four independent namespaces, both orders, one shared operation UUID.
        for order in ('forward','reverse'):
            op=str(uuid4());app='reuse_'+order;permission='reuse.'+order
            self.command(case,prior.prior.prior.document(app));self.command(case,prior.prior.document(permission,app=app))
            values=[prior.prior.prior.document(app,op),prior.prior.document(permission,app=app,op=op),prior.document(permission,app=app,op=op),document(app=app,op=op)]
            results={}
            for v in (values if order=='forward' else reversed(values)):results[v['command']]=self.command(case,v)
            frozen=self.snapshot(case)
            engine=self.db(case,'access_operator_urls')
            try:
                with engine.connect() as c:
                    for v in values:
                        assert self.command(case,v)==results[v['command']]
                        kwargs=dict(command=v['command'],app_id=app)
                        if v['command'] in ('permission.register','entry_permission.register'):kwargs['permission']=permission
                        assert adapter.outcome(c,op,**kwargs)==results[v['command']]
            finally:engine.dispose()
            assert self.snapshot(case)==frozen
        assert self.snapshot(case)['grants']==original['grants']
        self.record('enable-disable-reenable-populated-grant-preservation-unchanged-stale-missing-exact-transition-attribution-four-command-uuid-both-orders')
    def enablement_legacy_max_previous(self):
        for case in ('smax','slegacy'):self.seed(case)
        before=self.snapshot('slegacy')['applications'][0]
        receipt=self.command('slegacy',document(revision='7'));after=self.snapshot('slegacy')['applications'][0]
        assert receipt.result.revision=='8' and after[3]==before[3] and after[5]==before[5] and after[4]==ACTOR
        before=self.snapshot('smax');receipt=self.command('smax',document(False,'9223372036854775807'))
        assert receipt.result.disposition=='unchanged' and self.snapshot('smax')['applications']==before['applications']
        state=self.snapshot('smax');self.denied(lambda:self.command('smax',document(True,'9223372036854775807')),'operation_conflict');assert self.snapshot('smax')==state
        previous=previous_adapter(self.proof);previous5=prior.previous_adapter(self.proof);case='exact6'
        before5=self.snapshot(case)['operation_outcome'];value5=prior.prior.document('previous5.permission')
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:
                receipt5=previous5.execute(c,json.dumps(value5).encode())
                assert receipt5.result.disposition=='created'
                assert previous5.execute(c,json.dumps(value5).encode())==receipt5
                assert previous5.outcome(c,value5['operation_id'],command='permission.register',app_id='synthetic_app',permission='previous5.permission')==receipt5
        finally:engine.dispose()
        assert all(row in self.snapshot(case)['operation_outcome'] for row in before5)
        # Actual captured previous6 client creates/replays/looks up an entry at7.
        self.command(case,prior.prior.document('previous6.entry'))
        value=prior.document('previous6.entry');engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:
                receipt=previous.execute(c,json.dumps(value).encode())
                assert previous.execute(c,json.dumps(value).encode())==receipt
                assert previous.outcome(c,value['operation_id'],command='entry_permission.register',app_id='synthetic_app',permission='previous6.entry')==receipt
        finally:engine.dispose()
        original_rows=self.snapshot(case)['operation_outcome']
        self.execute_sql(case,f"INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_operator','application.set_enabled','platform',true,'{ACTOR}','{ACTOR}')")
        for enabled,expected in ((True,'1'),(False,'2')):
            self.command(case,document(enabled,expected))
            current=str(int(expected)+1);new_operation=prior.prior.prior.document()
            engine=self.db(case,'access_operator_urls')
            try:
                with engine.connect() as c:
                    receipt=previous.execute(c,json.dumps(new_operation).encode())
                    assert receipt.result.disposition=='unchanged' and receipt.result.revision==current and receipt.result.event_id is None
                    assert previous.execute(c,json.dumps(new_operation).encode())==receipt
                    assert previous.outcome(c,new_operation['operation_id'],app_id='synthetic_app')==receipt
                    for v,r in zip(self.previous6_values,self.previous6_receipts):
                        assert asdict(previous.execute(c,json.dumps(v).encode()))==asdict(r)
                        kwargs=dict(command=v['command'],app_id='synthetic_app')
                        if v['command']!='application.register':kwargs['permission']=v['payload']['permission']
                        assert asdict(previous.outcome(c,v['operation_id'],**kwargs))==asdict(r)
            finally:engine.dispose()
            now=self.snapshot(case)['operation_outcome']
            assert all(row in now for row in original_rows),'original6_receipt_bytes_changed'
        state=self.snapshot(case);self.migrate(case);assert self.snapshot(case)==state
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:
                assert previous5.execute(c,json.dumps(value5).encode())==receipt5
                assert previous5.outcome(c,value5['operation_id'],command='permission.register',app_id='synthetic_app',permission='previous5.permission')==receipt5
        finally:engine.dispose()
        assert self.snapshot(case)==state
        self.seed('exact7');self.command('exact7',prior.prior.prior.document());value=document();receipt=self.command('exact7',value)
        state=self.snapshot('exact7');self.migrate('exact7');assert self.snapshot('exact7')==state and self.s_outcome('exact7',value)==receipt
        self.record('legacy-attribution-max-unchanged-overflow-conflict-actual-previous5-and6-clients-populated7-repeat')
    def enablement_authority(self):
        case='sauthority';self.s_setup(case);value=document();receipt=self.command(case,value)
        for sql in ("UPDATE access.operator_authorities SET enabled=false WHERE command='application.set_enabled'", "UPDATE access.operator_authorities SET enabled=true; UPDATE access.operator_principals SET enabled=false"):
            self.execute_sql(case,sql);state=self.snapshot(case)
            for fn in (lambda:self.command(case,value),lambda:self.s_outcome(case,value),lambda:self.command(case,document(False,'2'))):self.denied(fn,'access_denied')
            assert self.snapshot(case)==state
        self.execute_sql(case,"UPDATE access.operator_principals SET enabled=true; UPDATE access.operator_authorities SET enabled=false WHERE command='application.set_enabled'")
        for app in ('other_app','synthetic_app'):
            self.execute_sql(case,f"INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_operator','application.set_enabled','platform','{app}',true,'{ACTOR}','{ACTOR}')")
            if app=='other_app':
                for fn in (lambda:self.command(case,value),lambda:self.s_outcome(case,value)):self.denied(fn,'access_denied')
            else:assert self.command(case,value)==self.s_outcome(case,value)==receipt
        # Wrong original login under assumed/inherited EXECUTE cannot choose an executor.
        url=self.db(case,'databases').url.set(username='supabase_admin');engine=create_engine(url,hide_parameters=True,connect_args=prior.prior.CONNECTION_ARGS)
        try:
            for mode in ('assumed','inherited'):
                for statement,parameters in ((EXECUTE,bound(value)),(LOOKUP,dict(operation=value['operation_id'],app='synthetic_app'))):
                    try:
                        with engine.begin() as c:
                            if mode=='inherited':c.exec_driver_sql('GRANT access_operator TO postgres WITH ADMIN FALSE, INHERIT TRUE, SET TRUE')
                            c.exec_driver_sql('SET LOCAL ROLE '+('access_operator' if mode=='assumed' else 'postgres'))
                            c.execute(text(statement),parameters).all()
                    except Exception as error:assert error.orig.sqlstate=='AC002'
                    else:raise AssertionError('wrong_original_login_accepted')
        finally:engine.dispose()
        self.record('command-specific-narrow-wildcard-app-principal-revoked-original-session-authority')
    def owner_command(self,case,value):
        # Reuse the existing migrator login and SET-only command-owner edge. Its
        # explicit principal/authority exists only in this synthetic fixture DB.
        engine=self.db(case)
        try:
            with engine.connect() as c:
                c.exec_driver_sql('SET ROLE access_command_owner')
                assert tuple(c.exec_driver_sql('SELECT session_user,current_user').one())==('access_migrator','access_command_owner')
                c.commit()
                return adapter.execute(c,json.dumps(value).encode())
        finally:engine.dispose()
    def wait_for_advisory_waiters(self,case,key,logins):
        engine=self.db(case,'databases');unsigned=key & ((1<<64)-1)
        expected={login:logins.count(login) for login in set(logins)}
        try:
            deadline=time.monotonic()+1.5
            while time.monotonic()<deadline:
                with engine.connect() as c:
                    rows=c.execute(text("SELECT a.usename,count(*) FROM pg_stat_activity a JOIN pg_locks l ON l.pid=a.pid WHERE a.datname=current_database() AND l.locktype='advisory' AND NOT l.granted AND l.classid::bigint=:high AND l.objid::bigint=:low AND l.objsubid=1 GROUP BY a.usename"),dict(high=unsigned>>32,low=unsigned & ((1<<32)-1))).all()
                counts=dict(rows)
                if all(counts.get(login,0)>=count for login,count in expected.items()):return
                time.sleep(.02)
            raise AssertionError('exact_advisory_wait_overlap_not_witnessed')
        finally:engine.dispose()
    def enablement_concurrency_recovery(self):
        case='sconcurrent';self.s_setup(case)
        self.execute_sql(case,f"INSERT INTO access.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by) VALUES('access_migrator','{ACTOR}',true,'{ACTOR}','{ACTOR}'); INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_migrator','application.set_enabled','platform','synthetic_app',true,'{ACTOR}','{ACTOR}')")
        # Release an existing app lock only after both commands are witnessed waiting.
        key=int.from_bytes(sha256(b'access:application:v1:synthetic_app').digest()[:8],'big',signed=True)
        # Authority lock serializes this login before the application lock, so witness2
        # includes one app waiter and one authority waiter.
        for mode in ('duplicate','distinct','changed_retry'):
            state=self.snapshot(case);app=state['applications'][0];v=document(not app[1],str(app[2]));values=[v,v if mode=='duplicate' else (document(not app[1],str(app[2])) if mode=='distinct' else {**v,'evidence_ref':'synthetic:changed'})]
            engine=self.db(case);c=engine.connect();transaction=c.begin()
            try:
                c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
                with ThreadPoolExecutor(max_workers=2) as pool:
                    pending=[pool.submit(self.command,case,x) for x in values];self.wait_for_operator_lock(case,2);transaction.rollback();results=[]
                    for f in pending:
                        try:results.append(f.result(timeout=5))
                        except adapter.OperatorError as error:results.append(error.code)
                if mode=='duplicate':assert results[0]==results[1]
                else:assert results.count('operation_conflict')==1
                after=self.snapshot(case);assert after['applications'][0][2]==app[2]+1 and len(after['business_event'])==len(state['business_event'])+1
            finally:
                if transaction.is_active:transaction.rollback()
                c.close();engine.dispose()
        # Independent original logins reach the same held application lock; neither
        # waits behind the other's authority lock. Same revision admits one change.
        state=self.snapshot(case);app=state['applications'][0]
        values=[document(not app[1],str(app[2])),document(not app[1],str(app[2]))]
        engine=self.db(case);c=engine.connect();transaction=c.begin()
        try:
            c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
            with ThreadPoolExecutor(max_workers=2) as pool:
                pending=[pool.submit(action,case,v) for action,v in zip((self.command,self.owner_command),values)]
                self.wait_for_advisory_waiters(case,key,['access_operator','access_migrator']);transaction.rollback();results=[]
                for future in pending:
                    try:results.append(future.result(timeout=5))
                    except adapter.OperatorError as error:results.append(error.code)
            assert results.count('operation_conflict')==1
            assert len([r for r in results if not isinstance(r,str) and r.result.disposition=='changed'])==1
            after=self.snapshot(case)
            assert after['applications'][0][2]==app[2]+1 and len(after['business_event'])==len(state['business_event'])+1
        finally:
            if transaction.is_active:transaction.rollback()
            c.close();engine.dispose()
        # Matching-state distinct commands preserve every application/event field.
        before=self.snapshot(case);app=before['applications'][0]
        values=[document(app[1],str(app[2])),document(app[1],str(app[2]))]
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda v:self.command(case,v),values))
        assert all(r.result.disposition=='unchanged' for r in results)
        after=self.snapshot(case)
        assert after['applications']==before['applications'] and after['business_event']==before['business_event']
        # Register and enable use independent authority locks and both wait on the
        # existing app lock before release, proving overlap rather than scheduling.
        app=after['applications'][0];registration=prior.prior.prior.document();enablement=document(not app[1],str(app[2]))
        engine=self.db(case);c=engine.connect();transaction=c.begin()
        try:
            c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
            with ThreadPoolExecutor(max_workers=2) as pool:
                pending=[pool.submit(self.command,case,registration),pool.submit(self.owner_command,case,enablement)]
                self.wait_for_advisory_waiters(case,key,['access_operator','access_migrator']);transaction.rollback()
                results=[future.result(timeout=5) for future in pending]
            assert results[0].result.disposition=='unchanged' and results[1].result.disposition=='changed'
        finally:
            if transaction.is_active:transaction.rollback()
            c.close();engine.dispose()
        value=document();command=parse_command(json.dumps(value).encode())
        retry=adapter.command_outcome_lock_key(ACTOR,command);authority=int.from_bytes(sha256(b'access:operator-authority:v1:access_operator').digest()[:8],'big',signed=True)
        for action in (self.command,self.s_outcome):
            for lock,code in ((retry,'operation_busy'),(authority,'operation_unavailable'),*(([(key,'operation_unavailable')]) if action==self.command else [])):
                state=self.snapshot(case);engine=self.db(case);c=engine.connect();t=c.begin()
                try:
                    c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':lock});self.denied(lambda:action(case,value),code)
                finally:t.rollback();c.close();engine.dispose()
                assert self.snapshot(case)==state
        case='srecovery';self.s_setup(case);value=document()
        class LostCommit:
            def __init__(self,t):self.t=t
            def __enter__(self):return self.t.__enter__()
            def __exit__(self,*args):
                answer=self.t.__exit__(*args)
                if args[0] is None:raise RuntimeError('synthetic_lost_commit_response')
                return answer
        class Connection:
            def __init__(self,c):self.c=c
            def __getattr__(self,name):return getattr(self.c,name)
            def begin(self):return LostCommit(self.c.begin())
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:self.denied(lambda:adapter.execute(Connection(c),json.dumps(value).encode()),'operation_unavailable')
        finally:engine.dispose()
        assert self.command(case,value)==self.s_outcome(case,value)
        for column,where in (('operator_authorities'," WHERE command='application.set_enabled'"),('operator_principals','')):
            for action,v in ((self.command,document(False,'2')),(self.s_outcome,value)):
                self.execute_sql(case,'UPDATE access.'+column+' SET enabled=true'+where)
                retry=adapter.command_outcome_lock_key(ACTOR,parse_command(json.dumps(v).encode()));engine=self.db(case);c=engine.connect();t=c.begin()
                try:
                    c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':retry})
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        pending=pool.submit(action,case,v);self.wait_for_operator_lock(case)
                        self.execute_sql(case,'UPDATE access.'+column+' SET enabled=false'+where);revoked=self.snapshot(case);t.rollback()
                        self.denied(lambda:pending.result(timeout=5),'access_denied')
                    assert self.snapshot(case)==revoked
                finally:
                    if t.is_active:t.rollback()
                    c.close();engine.dispose()
            self.execute_sql(case,'UPDATE access.'+column+' SET enabled=true'+where)
        # Pending revocation holds the authority serialization lock. The caller
        # initially sees the committed enabled mapping, then must recheck after wait.
        # Committed revocation during an application wait is unreachable because the
        # command already owns this authority lock at that stage.
        for column,where in (('operator_authorities'," WHERE command='application.set_enabled'"),('operator_principals','')):
            for action,v in ((self.command,document(False,'2')),(self.s_outcome,value)):
                self.execute_sql(case,'UPDATE access.'+column+' SET enabled=true'+where)
                before=self.snapshot(case);engine=self.db(case);c=engine.connect();t=c.begin()
                try:
                    c.exec_driver_sql('UPDATE access.'+column+' SET enabled=false'+where)
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        pending=pool.submit(action,case,v)
                        self.wait_for_advisory_waiters(case,authority,['access_operator']);t.commit()
                        self.denied(lambda:pending.result(timeout=5),'access_denied')
                    after=self.snapshot(case)
                    for table in ('applications','grants','permissions','entry_permissions','operation_outcome','business_event'):assert after[table]==before[table]
                finally:
                    if t.is_active:t.rollback()
                    c.close();engine.dispose()
            self.execute_sql(case,'UPDATE access.'+column+' SET enabled=true'+where)
        self.record('witnessed-independent-login-same-revision-duplicate-register-overlap-unchanged-preservation-lock-classification-lost-commit-retry-and-authority-wait-revocation')
    def enablement_attacks(self):
        case='sfailure';self.s_setup(case);value=document();before=self.snapshot(case)
        malformed=[(label,change) for label,change in prior.prior.prior.malformed_sql_cases() if label!='changed_expected_absence']
        malformed += [('boolean_number',lambda p:{'canonical':p['canonical'].replace(b'"enabled":true',b'"enabled":1')}),
            ('boolean_string',lambda p:{'canonical':p['canonical'].replace(b'"enabled":true',b'"enabled":"true"')}),
            ('revision_number',lambda p:{'canonical':p['canonical'].replace(b'"expected_revision":"1"',b'"expected_revision":1')}),
            ('argument_reason_mismatch',{'reason':'access_change'}),('argument_evidence_mismatch',{'evidence':'synthetic:other'}),('null_enabled',{'enabled':None}),('null_revision',{'revision':None}),*[(f'revision_{i}',{'revision':r}) for i,r in enumerate(('','0','01','+1',' 1','1\n','9223372036854775808','1'*20,'١'))]]
        for label,change in malformed:
            parameters=bound(value)
            if label=='changed_envelope_command':change={'canonical':parameters['canonical'].replace(b'application.set_enabled',b'application.register')}
            parameters.update(change(parameters) if callable(change) else change)
            self.sql_refusal(case,EXECUTE,parameters,'AC005','access_command_invalid');assert self.snapshot(case)==before
        for isolation in ('REPEATABLE READ','SERIALIZABLE'):
            self.sql_refusal(case,EXECUTE,bound(value),'AC005','access_command_invalid',isolation=isolation)
            self.sql_refusal(case,LOOKUP,dict(operation=value['operation_id'],app='synthetic_app'),'AC005','access_command_invalid',isolation=isolation)
        for change in ({'operation':None},{'operation':'00000000-0000-0000-0000-000000000000'},{'app':None},{'app':'a'},{'app':'Uppercase'},{'app':'a'*65}):
            self.sql_refusal(case,LOOKUP,dict(operation=value['operation_id'],app='synthetic_app')|change,'AC005','access_command_invalid')
        # Each injection is independent and reaches the named guard, never an earlier
        # unrelated check. Failed transactions leave no outcome/event/row mutation.
        injections=[
            ('applications','aaa_inject','BEFORE UPDATE',"NEW.app_id:='forged_app';",'access_application_update_invalid'),
            ('applications','aaa_inject','BEFORE UPDATE',"NEW.created_by:='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';",'access_application_update_invalid'),
            ('applications','aaa_inject','BEFORE UPDATE',"NEW.created_at:='2000-01-01Z';",'access_application_update_invalid'),
            ('applications','aaa_inject','BEFORE UPDATE',"NEW.revision:=88;",'access_application_update_invalid'),
            ('applications','aaa_inject','BEFORE UPDATE',"NEW.updated_by:='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';",'access_application_update_invalid'),
            ('applications','aaa_inject','BEFORE UPDATE',"NEW.updated_at:='2000-01-01Z';",'access_application_update_invalid'),
            ('operation_outcome','aaa_inject','BEFORE INSERT',"NEW.result:=jsonb_set(NEW.result,'{revision}','\"999\"');",'access_enablement_result_invalid'),
            ('operation_outcome','aaa_inject','BEFORE INSERT',"NEW.result:=jsonb_set(NEW.result,'{disposition}','\"created\"');",'access_enablement_result_invalid'),
            ('operation_outcome','aaa_inject','BEFORE INSERT',"NEW.executor_actor_id:='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';",'access_enablement_result_invalid'),
            ('operation_outcome','aaa_inject','BEFORE INSERT',"NEW.result:=jsonb_set(NEW.result,'{event_id}','null');",'access_changed_result_invalid'),
            ('business_event','aaa_inject','BEFORE INSERT',"NEW.event_type:='access.application_registered';",'access_event_invalid'),
            ('business_event','aaa_inject','BEFORE INSERT',"NEW.transition:=jsonb_set(NEW.transition,'{before,revision}','\"999\"');",'access_event_invalid'),
            ('business_event','aaa_inject','BEFORE INSERT',"NEW.transition:=jsonb_set(NEW.transition,'{before,enabled}','true');",'access_event_invalid'),
            ('business_event','aaa_inject','BEFORE INSERT',"NEW.transition:=jsonb_set(NEW.transition,'{after,revision}','2');",'access_event_invalid'),
            ('business_event','aaa_inject','BEFORE INSERT',"NEW.transition:=jsonb_set(NEW.transition,'{after,enabled}','false');",'access_event_invalid'),
            ('business_event','aaa_inject','BEFORE INSERT',"NEW.transition:=jsonb_set(NEW.transition,'{after,revision}','\"999\"');",'access_event_invalid'),
            ('business_event','aaa_inject','BEFORE INSERT',"NEW.operation_id:='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';",'access_event_invalid'),
            ('business_event','aaa_inject','BEFORE INSERT',"NEW.scope_kind:='organization';",'access_event_invalid'),
            ('business_event','aaa_inject','BEFORE INSERT',"NEW.scope_id:='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';",'access_event_invalid'),
            ('business_event','aaa_inject','BEFORE INSERT',"SELECT o.id INTO NEW.outcome_id FROM access.operation_outcome o WHERE o.command_type='application.register' AND o.result->>'disposition'='created' LIMIT 1;",'access_event_invalid'),
            ('business_event','aaa_inject','BEFORE INSERT',"NEW.target:='{}';",'access_event_invalid'),
            ('business_event','aaa_inject','BEFORE INSERT',"NEW.executor_actor_id:='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';",'access_event_invalid'),
            ('business_event','aaa_inject','BEFORE INSERT',"RETURN NULL;",'access_required_event_missing'),
        ]
        for table,name,timing,body,message in injections:
            self.execute_sql(case,f"CREATE FUNCTION access.inject_enablement() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN {body} RETURN NEW; END $$; CREATE TRIGGER {name} {timing} ON access.{table} FOR EACH ROW EXECUTE FUNCTION access.inject_enablement()")
            self.sql_refusal(case,EXECUTE,bound(value),'23514',message,force_event=(message=='access_required_event_missing'))
            self.execute_sql(case,f'DROP TRIGGER {name} ON access.{table}; DROP FUNCTION access.inject_enablement()');assert self.snapshot(case)==before
        for sql in ("UPDATE access.applications SET enabled=true", "UPDATE access.applications SET enabled=enabled WHERE false",'SELECT * FROM access.applications','SET ROLE access_command_owner'):
            self.sql_refusal(case,sql,{},'42501')
        # Original-session GUC spoofing cannot replace server-derived attribution.
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.begin() as c:
                c.exec_driver_sql("SET LOCAL app.actor_id='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'; SET LOCAL app.org_id='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'")
                c.execute(text(EXECUTE),bound(value)).all()
        finally:engine.dispose()
        assert self.snapshot(case)['applications'][0][4]==ACTOR
        # Rollback-only controlled principal mapping lets the actual command owner
        # make a valid update without a routine/outcome; the deferred row guard must
        # reject exactly its missing change evidence.
        url=self.db(case,'databases').url.set(username='supabase_admin');engine=create_engine(url,hide_parameters=True,connect_args=prior.prior.CONNECTION_ARGS)
        try:
            try:
                with engine.begin() as c:
                    c.exec_driver_sql(f"SET LOCAL ROLE access_migrator; INSERT INTO access.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by) VALUES('supabase_admin','{ACTOR}',true,'{ACTOR}','{ACTOR}'); INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'supabase_admin','application.set_enabled','platform',true,'{ACTOR}','{ACTOR}'); RESET ROLE; SET LOCAL ROLE access_command_owner")
                    c.exec_driver_sql("UPDATE access.applications SET enabled=false WHERE app_id='synthetic_app'")
            except Exception as error:assert error.orig.sqlstate=='23514' and error.orig.diag.message_primary=='access_required_change_missing'
            else:raise AssertionError('owner_update_without_evidence_accepted')
        finally:engine.dispose()
        self.record('independent-row-outcome-event-forgeries-required-event-change-atomic-rollback-strict-native-input-isolation-guc-raw-dml')
    def enablement_catalog(self):
        for mutation in (
            'GRANT UPDATE(revision) ON access.applications TO access_command_owner',
            'ALTER TABLE access.applications DISABLE TRIGGER application_required_change',
            'ALTER TABLE access.applications DISABLE TRIGGER application_update_guard',
            'SET LOCAL ROLE access_command_owner; ALTER FUNCTION access.set_application_enabled(uuid,text,boolean,text,text,text,bytea) SECURITY INVOKER; RESET ROLE',
            'ALTER FUNCTION access.guard_application_update() SET search_path=public',
        ):
            before=self.snapshot('clean');engine=self.db('clean')
            try:
                with engine.connect() as c:
                    t=c.begin()
                    try:
                        c.exec_driver_sql(mutation)
                        try:baseline.preflight(c)
                        except baseline.BaselineError:pass
                        else:raise AssertionError('enablement_catalog_drift_accepted')
                    finally:t.rollback()
            finally:engine.dispose()
            assert self.snapshot('clean')==before
        self.record('exact7-extra-column-acl-trigger-function-search-path-security-drift-refusal')
    def enablement_cli(self):
        run=json.loads((self.proof/'run.json').read_text());target=ROOT/'platform/deployment/.local/kdg'/run['run_id']/('access-operator-'+run['operator_namespace']+'.json')
        value=document(app='cli_app');path=self.proof/'set-enabled-cli-command.json';path.write_text(json.dumps(value));path.chmod(0o600)
        common=[sys.executable,'-I','-B',str(ACCESS/'operator_cli.py')];env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'}
        result=subprocess.run(common+['execute','--owner','access','--target',str(target),'--command-file',str(path)],env=env,capture_output=True,timeout=15)
        assert result.returncode==0 and not result.stderr,'set_enabled_cli_execute_failed'
        receipt=json.loads(result.stdout);assert receipt['result']['command']=='application.set_enabled' and receipt['result']['revision']=='2' and receipt['result']['disposition']=='changed'
        lookup=subprocess.run(common+['outcome','--owner','access','--target',str(target),'--command','application.set_enabled','--operation-id',value['operation_id'],'--app-id','cli_app'],env=env,capture_output=True,timeout=15)
        assert lookup.returncode==0 and json.loads(lookup.stdout)==receipt
        (self.proof/'set-enabled-cli-receipt.json').write_bytes(result.stdout)
        self.record('real-isolated-enable-cli-and-current-authorized-targeted-receipt-recovery')

def main():
    if not __debug__:raise RuntimeError('access_qualification_optimized_python_prohibited')
    parser=argparse.ArgumentParser();g=parser.add_mutually_exclusive_group(required=True);g.add_argument('--all',action='store_true');g.add_argument('--verify-retained',action='store_true');args=parser.parse_args()
    raw=Path(os.environ['ACCESS_QUALIFICATION_DIR']);assert '..' not in raw.parts
    proof=Path(os.path.abspath(raw));private,run=prior.prior.load_fixture(proof)
    witness=json.loads((proof/'bootstrap-source-custody.json').read_text());captured=source_snapshot(proof)
    assert witness['status']=='passed' and witness['before']==witness['after']==captured
    for name,digest in witness['logs'].items():assert sha256((proof/name).read_bytes()).hexdigest()==digest
    q=Qualification(proof,private)
    if args.all:
        (proof/'all-started').open('x').close()
        inherited=(q.prepare_cases,q.functional,q.concurrency,q.response_loss_and_authority_wait,q.malformed_sql,q.attacks,q.drift,q.catalog_adversaries,q.foreign_privilege_adversaries,q.cli,q.permission_functional,q.permission_authority_boundaries,q.previous_application_adapter,q.permission_concurrency,q.permission_recovery,q.permission_attacks,q.permission_cli,q.entry_functional,q.entry_concurrency,q.entry_recovery,q.entry_attacks,q.entry_authority,q.entry_cli)
        for method in (*inherited,q.enablement_functional,q.enablement_legacy_max_previous,q.enablement_authority,q.enablement_concurrency_recovery,q.enablement_attacks,q.enablement_catalog,q.enablement_cli,q.integration,q.retained):method()
        (proof/'retained-state.json').write_text(json.dumps({case:q.snapshot(case) for case in private['databases']},indent=2)+'\n')
    else:
        prior.require_aggregate_source(json.loads((proof/'results.json').read_text()),captured)
        assert json.loads((proof/'retained-state.json').read_text())=={case:q.snapshot(case) for case in private['databases']}
        q.retained()
    assert captured==source_snapshot(proof),'qualification_source_changed'
    (proof/('results.json' if args.all else 'retained-results.json')).write_text(json.dumps(dict(status='passed',steps=q.results,source=captured),indent=2)+'\n')
    print(json.dumps(dict(ok=True,steps=q.results)))

if __name__=='__main__':
    try:main()
    except Exception as error:
        import traceback
        # Stack frames only: never render SQLAlchemy SQL, URL, parameters or chained
        # driver exceptions. The private proof directory retains a useful failure.
        proof=Path(os.environ['ACCESS_QUALIFICATION_DIR'])
        (proof/'failure-frames.json').write_text(json.dumps(dict(type=type(error).__name__,
            assertion=str(error) if type(error) is AssertionError else None,
            frames=traceback.format_tb(error.__traceback__)),indent=2)+'\n')
        print(json.dumps(dict(ok=False,code='access_qualification_failed_requires_inspection')))
        raise SystemExit(1) from None
