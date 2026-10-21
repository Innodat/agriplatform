"""Source-bound Access9 synthetic acceptance; no general environment bootstrap."""
if not __debug__:
    raise RuntimeError('access_qualification_optimized_python_prohibited')
import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from hashlib import sha256
import importlib.util
import json,os,subprocess,sys,time
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_application_register as base
import qualify_organization_application_storage as storage
from sqlalchemy import create_engine,text
ROOT,ACCESS,ACTOR=base.ROOT,base.ACCESS,base.ACTOR
adapter,baseline=base.adapter,base.baseline
CASES=frozenset(('configure','authority','retry','guards','concurrency','upgrade','rollback','drift','cli'))
base.CASES=CASES
load_fixture=base.load_fixture
ORG1=storage.ORG1
ORG2=storage.ORG2
MISSING='33333333-3333-4333-8333-333333333333'
TABLES=(*storage.prior.TABLES,'organization_applications')
EXECUTE='SELECT * FROM access.configure_organization_application(CAST(:operation AS uuid),CAST(:org AS uuid),:app,:enabled,:absent,:revision,:reason,:evidence,:canonical)'


def source_snapshot(proof):
    paths=base.source_paths(proof)+[Path(__file__),*(Path(module.__file__).resolve() for module in (storage,storage.prior,storage.prior.prior,storage.prior.prior.prior))]
    captured={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths}
    manifest=proof/'previous-source.json'
    previous=json.loads(manifest.read_text())
    assert previous['baseline_commit']=='fd8248f43a3355b9494e031128d2ffdafd0a8fb0'
    for name,digest in previous['sources'].items():
        path=proof/'previous-root'/name
        assert path.resolve().is_relative_to((proof/'previous-root').resolve())
        assert sha256(path.read_bytes()).hexdigest()==digest,'previous_source_mismatch'
        captured[str(path.relative_to(ROOT))]=digest
    captured[str(manifest.relative_to(ROOT))]=sha256(manifest.read_bytes()).hexdigest()
    return captured


def document(enabled=True,revision=None,org=ORG1,app='synthetic_app',op=None):
    value=base.document(app,op)
    value['command']='organization_application.configure';value['scope']=dict(kind='organization',org_id=org)
    value['payload']=dict(app_id=app,enabled=enabled,**({'expected_absent':True} if revision is None else {'expected_revision':revision}))
    return value


def bound(value):
    command=base.parse_command(json.dumps(value).encode())
    return dict(operation=command.operation_id,org=command.scope.org_id,app=command.payload.app_id,enabled=command.payload.enabled,
        absent=getattr(command.payload,'expected_absent',False),revision=getattr(command.payload,'expected_revision',None),
        reason=command.reason_code,evidence=command.evidence_ref,canonical=adapter.canonical_command(command))


class Qualification(storage.Qualification):
    admin=storage.Qualification.admin
    snapshot=storage.Qualification.snapshot
    refused=storage.Qualification.refused
    def org_sql(self,case,sql):return self.execute_sql(case,sql,'owner_urls')
    def authority(self,case,org=ORG1,app=None):
        literal='NULL' if app is None else "'"+app+"'"
        self.execute_sql(case,f"INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,org_id,application_id,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_operator','organization_application.configure','organization','{org}',{literal},true,'{ACTOR}','{ACTOR}')")
    def prepare_cases(self):
        for case in CASES:
            self.migrate(case,'access_0008' if case in ('upgrade','rollback') else 'head')
            self.seed(case)
            self.command(case,base.document())
            for org in (ORG1,ORG2):self.org_sql(case,f"INSERT INTO identity.org(id,name,slug) VALUES('{org}','Synthetic configuration organization','synthetic-{org}')")
            if case not in ('upgrade','rollback'):self.authority(case)
        self.record('fresh-restricted-owner-command-fixtures-with-separate-Identity19-orgs')
    def lookup(self,case,value,org=None,app=None):
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:return adapter.outcome(c,value['operation_id'],command='organization_application.configure',org_id=org or value['scope']['org_id'],app_id=app or value['payload']['app_id'])
        finally:engine.dispose()
    def functional(self):
        case='configure';original=self.snapshot(case)
        values=[]
        for enabled,revision,disposition in ((True,None,'created'),(False,'1','changed'),(True,'2','changed'),(True,'3','unchanged')):
            before=self.snapshot(case);value=document(enabled,revision)
            result=self.command(case,value);values.append((value,result));after=self.snapshot(case)
            assert result.result.disposition==disposition and result.result.revision==('1' if revision is None else str(int(revision)+(disposition=='changed')))
            assert asdict(result.result.target)==dict(org_id=ORG1,app_id='synthetic_app')
            assert self.command(case,value)==self.lookup(case,value)==result
            if disposition=='unchanged':
                assert after['organization_applications']==before['organization_applications'] and after['business_event']==before['business_event']
            else:
                row=after['organization_applications'][0];event=next(r for r in after['business_event'] if r[0]==result.result.event_id)
                assert row[2:6]==[enabled,int(result.result.revision),ACTOR,ACTOR]
                assert event[1]=='access.organization_application_changed' and event[3:5]==['organization',ORG1]
                assert event[9]==dict(org_id=ORG1,app_id='synthetic_app')
                assert event[10]==dict(before=None if revision is None else dict(enabled=not enabled,revision=revision),after=dict(enabled=enabled,revision=result.result.revision))
                assert row[7]==event[-1]==str(result.committed_at)
                if revision is not None:assert row[4]==before['organization_applications'][0][4] and row[6]==before['organization_applications'][0][6]
            for table in ('applications','permissions','entry_permissions','grants'):assert after[table]==original[table]
        state=self.snapshot(case)
        for value,result in values:assert self.command(case,value)==self.lookup(case,value)==result
        for value in (document(),document(False,'1'),document(True,'1'),document(revision='1',app='missing_app')):
            self.denied(lambda:self.command(case,value),'operation_conflict')
        assert self.snapshot(case)==state
        self.authority(case,ORG2);op=str(uuid4())
        first_document=document(org=ORG2,op=op);second_document=document(revision='3',op=op)
        first=self.command(case,first_document);second=self.command(case,second_document)
        assert first.result.target.org_id==ORG2 and second.result.target.org_id==ORG1
        # Registration and configure share the operation UUID without substitution.
        assert self.command(case,base.document(op=op)).result.command=='application.register'
        for original,receipt in ((first_document,first),(second_document,second)):
            assert self.command(case,original)==self.lookup(case,original)==receipt
        self.record('create-change-disable-reenable-unchanged-attribution-history-compact-events-scope-command-namespace')
    def authority_and_identity(self):
        case='authority'
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='organization_application.configure'")
        before=self.snapshot(case)
        self.denied(lambda:self.command(case,document(org=MISSING)),'access_denied')
        self.denied(lambda:self.command(case,document()),'access_denied')
        assert self.snapshot(case)==before
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=true WHERE command='organization_application.configure'")
        self.authority(case,MISSING)
        self.denied(lambda:self.command(case,document(org=MISSING)),'operation_conflict')
        self.org_sql(case,f"UPDATE identity.org SET deleted_at=clock_timestamp() WHERE id='{ORG1}'")
        self.denied(lambda:self.command(case,document()),'operation_conflict')
        self.org_sql(case,f"UPDATE identity.org SET deleted_at=NULL WHERE id='{ORG1}'")
        value=document();receipt=self.command(case,value)
        self.org_sql(case,f"UPDATE identity.org SET deleted_at=clock_timestamp() WHERE id='{ORG1}'")
        assert self.lookup(case,value)==receipt
        self.denied(lambda:self.command(case,value),'operation_conflict')
        self.execute_sql(case,"UPDATE access.operator_principals SET enabled=false")
        self.denied(lambda:self.lookup(case,value),'access_denied')
        self.execute_sql(case,"UPDATE access.operator_principals SET enabled=true")
        # Exact app binding refuses another registered app; platform authority cannot substitute.
        self.command(case,base.document('other_app'))
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='organization_application.configure'")
        self.authority(case,ORG1,'synthetic_app')
        self.denied(lambda:self.command(case,document(org=ORG1,app='other_app')),'access_denied')
        self.record('authority-before-Identity-missing-deleted-org-refusal-current-authority-historical-lookup-without-eligibility')
    def retry_and_recovery(self):
        case='retry';value=document();receipt=self.command(case,value);state=self.snapshot(case)
        assert self.command(case,value)==self.lookup(case,value)==receipt
        self.denied(lambda:self.command(case,{**value,'evidence_ref':'synthetic:changed'}),'operation_conflict')
        self.denied(lambda:self.lookup(case,value,app='other_app'),'access_denied')
        assert self.lookup(case,document()) is None and self.snapshot(case)==state
        # Responding after COMMIT is deliberately lost; resolve the durable owner outcome.
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:
                later=document(False,'1');adapter.execute(c,json.dumps(later).encode())
            assert self.lookup(case,later).result.revision=='2'
        finally:engine.dispose()
        self.record('exact-replay-changed-fingerprint-refusal-target-lookup-response-loss-recovery')
    def guards(self):
        case='guards';self.command(case,document());state=self.snapshot(case)
        # Raw owner and actual restricted operator never gain unsupported table writes.
        for role in ('access_owner_urls','access_operator_urls'):
            for sql in ("UPDATE access.organization_applications SET enabled=false WHERE false", "DELETE FROM access.organization_applications WHERE false", "TRUNCATE access.organization_applications"):
                self.refused(case,sql,'42501' if role=='access_operator_urls' else ('55000' if not sql.startswith('UPDATE') else '42501'),role=role)
        parameters=bound(document(False))
        malformed=list(base.malformed_sql_cases())+[
            ('null_org',{'org':None}),('nil_org',{'org':storage.NIL}),('null_absent',{'absent':None}),
            ('bad_revision',{'revision':'0','absent':False}),('create_with_revision',{'revision':'1'}),
            ('missing_update_revision',{'revision':None,'absent':False}),
            ('argument_org_mismatch',{'org':ORG2}),('argument_enabled_mismatch',{'enabled':True}),
        ]
        for name,changes in malformed:
            changes=changes(parameters) if callable(changes) else changes
            if name=='changed_envelope_command':changes={'canonical':parameters['canonical'].replace(b'organization_application.configure',b'permission.register')}
            self.refused(case,EXECUTE,'AC005',parameters=parameters|changes,role='access_operator_urls',context=None)
        for isolation in ('REPEATABLE READ','SERIALIZABLE'):
            self.refused(case,EXECUTE,'AC005',parameters=parameters,role='access_operator_urls',context=None,prefix='SET TRANSACTION ISOLATION LEVEL '+isolation)
        assert self.snapshot(case)==state
        self.record('raw-owner-operator-noop-delete-truncate-and-malformed-direct-SQL-refusal')
    def concurrency(self):
        case='concurrency'
        values=[document(),document()]
        def run(value):
            try:return self.command(case,value)
            except adapter.OperatorError as error:return error.code
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,values))
        assert sum(not isinstance(r,str) for r in results)==1 and results.count('operation_conflict')==1
        values=[document(False,'1'),document(False,'1')]
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,values))
        assert sum(not isinstance(r,str) for r in results)==1 and results.count('operation_conflict')==1
        self.command(case,base.document('identical_app'))
        identical=document(app='identical_app');before=self.snapshot(case)
        owner=self.db(case)
        try:
            with owner.connect() as holder:
                tx=holder.begin()
                key=adapter.command_outcome_lock_key(ACTOR,base.parse_command(json.dumps(identical).encode()))
                holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=key))
                with ThreadPoolExecutor(max_workers=2) as pool:
                    futures=[pool.submit(self.command,case,identical) for _ in range(2)]
                    self.wait_for_retry_lock(holder,futures,count=2)
                    tx.rollback()
                    receipts=[future.result(timeout=5) for future in futures]
        finally:owner.dispose()
        assert receipts[0]==receipts[1] and receipts[0].result.disposition=='created'
        after=self.snapshot(case)
        for table in ('organization_applications','operation_outcome','business_event'):
            assert len(after[table])==len(before[table])+1,table
        assert self.lookup(case,identical)==receipts[0]
        value=document(True,'2');engine=self.db(case,'access_operator_urls')
        command=base.parse_command(json.dumps(value).encode())
        key=adapter.command_outcome_lock_key(ACTOR,command)
        try:
            with engine.begin() as c:
                c.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=key))
                self.denied(lambda:self.command(case,value),'operation_busy')
        finally:engine.dispose()
        # Business lock timeout is unavailable, never operation_busy.
        owner=self.db(case)
        try:
            with owner.begin() as c:
                c.execute(text("SELECT pg_advisory_xact_lock(access.command_lock(:key))"),dict(key='access:organization-application:v1:'+ORG1+':synthetic_app'))
                self.denied(lambda:self.command(case,value),'operation_unavailable')
        finally:owner.dispose()
        assert self.command(case,value).result.revision=='3'
        self.record('concurrent-create-update-revision-conflicts-operation-lock-busy-only-and-business-timeout-recovery')
    def wait_for_retry_lock(self,holder,future,*,advisory=True,count=1):
        pending=future if isinstance(future,list) else [future]
        blocker=holder.exec_driver_sql('SELECT pg_backend_pid()').scalar_one()
        deadline=time.monotonic()+3
        while True:
            holder.exec_driver_sql('SELECT pg_stat_clear_snapshot()')
            waiting=holder.execute(text("SELECT count(DISTINCT a.pid) FROM pg_locks l JOIN pg_stat_activity a ON a.pid=l.pid WHERE a.datname=current_database() AND a.usename='access_operator' AND NOT l.granted AND (:any_lock OR l.locktype='advisory') AND :blocker=ANY(pg_blocking_pids(a.pid))"),dict(blocker=blocker,any_lock=not advisory)).scalar_one()
            if waiting>=count:return
            assert not any(f.done() for f in pending),'retry_waiter_completed_before_observed'
            assert time.monotonic()<deadline,'retry_wait_not_observed'
            time.sleep(.01)
    def freshness_and_revocation(self):
        case='retry';value=document(True,'2');receipt=self.command(case,value)
        engine=self.db(case);operator=self.db(case,'access_operator_urls')
        try:
            for replay in (False,True):
                attempt=value if replay else document(False,'3')
                command=base.parse_command(json.dumps(attempt).encode())
                key=adapter.command_outcome_lock_key(ACTOR,command)
                with engine.connect() as holder:
                    tx=holder.begin();holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=key))
                    def delayed():
                        try:
                            with operator.begin() as c:
                                c.exec_driver_sql("SET LOCAL statement_timeout='9s'; SET LOCAL lock_timeout='8s'")
                                c.execute(text(EXECUTE),bound(attempt)).all()
                        except Exception as error:return getattr(getattr(error,'orig',None),'sqlstate',None)
                        return 'accepted'
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        future=pool.submit(delayed)
                        # Assert the actual restricted session reached the retry wait,
                        # so sleep cannot accidentally precede the Identity observation.
                        self.wait_for_retry_lock(holder,future)
                        time.sleep(5.1);tx.rollback()
                        assert future.result(timeout=5)=='AC004','expired_observation_accepted'
            # Revoke exact authority while an execution waits before that authority's
            # serialization lock; it must recheck after the retry lock is released.
            attempt=document(False,'3');command=base.parse_command(json.dumps(attempt).encode())
            with engine.connect() as holder:
                tx=holder.begin();holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=adapter.command_outcome_lock_key(ACTOR,command)))
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future=pool.submit(lambda:self.command(case,attempt))
                    self.wait_for_retry_lock(holder,future)
                    self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='organization_application.configure'")
                    tx.rollback()
                    try:future.result(timeout=5)
                    except adapter.OperatorError as error:assert error.code=='access_denied'
                    else:raise AssertionError('revocation_during_wait_accepted')
            self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=true WHERE command='organization_application.configure'")
            assert self.lookup(case,value)==receipt
        finally:engine.dispose();operator.dispose()
        self.record('five-second-total-observation-expiry-before-new-write-and-replay-authority-revocation-after-wait')
    def deferred_evidence_and_overflow(self):
        case='guards'
        self.execute_sql(case,f"INSERT INTO access.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by) VALUES('access_migrator','{ACTOR}',true,'{ACTOR}','{ACTOR}');INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,org_id,application_id,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_migrator','organization_application.configure','organization','{ORG1}','synthetic_app',true,'{ACTOR}','{ACTOR}')")
        # Command-owner assumption is an explicit synthetic negative test by the
        # migrator; the restricted operator cannot assume this role.
        prefix=f"SET LOCAL app.context_kind='setup';SET LOCAL app.org_id='{ORG1}';SET LOCAL app.actor_id='{ACTOR}';SET LOCAL app.account_id='';SET LOCAL ROLE access_command_owner;"
        self.refused(case,"UPDATE access.organization_applications SET enabled=false WHERE org_id='"+ORG1+"'",'23514',prefix=prefix,message='access_required_configuration_change_missing')
        self.refused(case,"UPDATE access.organization_applications SET enabled=enabled WHERE org_id='"+ORG1+"'",'23514',prefix=prefix,message='access_configuration_update_invalid')
        self.refused(case,"UPDATE access.organization_applications SET enabled=false WHERE false",'23514',prefix=prefix,message='access_configuration_statement_invalid')
        self.refused(case,"INSERT INTO access.organization_applications(org_id,app_id,enabled,created_by,updated_by,created_at,updated_at) VALUES('"+ORG1+"','synthetic_app',false,'"+ACTOR+"','"+ACTOR+"',statement_timestamp(),statement_timestamp()) ON CONFLICT(org_id,app_id) DO UPDATE SET enabled=false",'23514',prefix=prefix)
        before=self.snapshot(case)
        self.execute_sql(case,"CREATE FUNCTION access.fixture_skip_event() RETURNS trigger LANGUAGE plpgsql AS 'BEGIN RETURN NULL; END';REVOKE ALL ON FUNCTION access.fixture_skip_event() FROM PUBLIC;CREATE TRIGGER aa_fixture_skip_event BEFORE INSERT ON access.business_event FOR EACH ROW EXECUTE FUNCTION access.fixture_skip_event()")
        try:
            self.denied(lambda:self.command(case,document(False,'1')),'operation_unavailable')
        finally:self.execute_sql(case,'DROP TRIGGER aa_fixture_skip_event ON access.business_event;DROP FUNCTION access.fixture_skip_event()')
        assert self.snapshot(case)==before
        self.record('command-owner-noop-empty-upsert-and-deferred-missing-row-event-evidence-refusal')
    def context_and_login_boundaries(self):
        case='configure';value=document(False,'3');engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:
                # Commit forged session context so _run still owns a fresh transaction.
                c.execute(text("SELECT set_config('app.context_kind','user',false),set_config('app.org_id',:org,false),set_config('app.actor_id',:actor,false),set_config('app.account_id',:actor,false)"),dict(org=ORG2,actor=MISSING));c.commit()
                receipt=adapter.execute(c,json.dumps(value).encode())
                assert receipt.result.target.org_id==ORG1 and receipt.result.revision=='4'
        finally:engine.dispose()
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='organization_application.configure' AND org_id='"+ORG2+"'")
        before=self.snapshot(case)
        denied=document(org=ORG2)
        forged=f"SET LOCAL app.context_kind='setup';SET LOCAL app.org_id='{ORG1}';SET LOCAL app.actor_id='{ACTOR}';SET LOCAL app.account_id='';"
        self.refused(case,EXECUTE,'AC002',parameters=bound(denied),role='access_operator_urls',prefix=forged)
        lookup="SELECT * FROM access.organization_application_configuration_outcome(CAST(:operation AS uuid),CAST(:org AS uuid),:app)"
        self.refused(case,lookup,'AC002',parameters=dict(operation=value['operation_id'],org=ORG2,app='synthetic_app'),role='access_operator_urls',prefix=forged)
        # Existing migrator login copies the operator's context and assumes the
        # definer role through its existing migration edge; session_user stays migrator.
        copied=forged+'SET LOCAL ROLE access_command_owner;'
        self.refused(case,EXECUTE,'AC002',parameters=bound(document(True,'4')),prefix=copied)
        self.refused(case,lookup,'AC002',parameters=dict(operation=value['operation_id'],org=ORG1,app='synthetic_app'),prefix=copied)
        assert self.snapshot(case)==before and self.lookup(case,value)==receipt
        self.record('actual-login-forged-org-actor-account-context-cannot-create-authority-or-receipts-authorized-command-overwrites-context')
    def forged_evidence_and_merge(self):
        case='guards'
        # Reuse the synthetic mapped migrator's command-owner guard seam from
        # deferred evidence; each MERGE statement must roll back its entire attempt.
        prefix=f"SET LOCAL app.context_kind='setup';SET LOCAL app.org_id='{ORG1}';SET LOCAL app.actor_id='{ACTOR}';SET LOCAL app.account_id='';SET LOCAL ROLE access_command_owner;"
        for source in (f"SELECT '{ORG1}'::uuid AS org_id",f"SELECT '{ORG2}'::uuid AS org_id",f"SELECT '{ORG1}'::uuid AS org_id WHERE false"):
            merge=f"MERGE INTO access.organization_applications t USING ({source}) s ON t.org_id=s.org_id AND t.app_id='synthetic_app' WHEN MATCHED THEN UPDATE SET enabled=false WHEN NOT MATCHED THEN INSERT(org_id,app_id,enabled,created_by,updated_by,created_at,updated_at) VALUES(s.org_id,'synthetic_app',false,'{ACTOR}','{ACTOR}',statement_timestamp(),statement_timestamp())"
            # Nonmatching ORG2 is outside this exact authority; other paths reach
            # row/empty/deferred guards. All are safe refusals with unchanged state.
            self.refused(case,merge,'42501' if ORG2 in source else '23514',prefix=prefix)
        # Mutate NEW at an earlier synthetic fixture trigger, then require the
        # existing evidence guard to refuse. Never disable the production guards.
        mutations=[
            ('operation_outcome',"NEW.scope_id:='"+ORG2+"'::uuid;"),
            ('operation_outcome',"NEW.result:=jsonb_set(NEW.result,'{target,app_id}','\"other_app\"'::jsonb);"),
            ('operation_outcome',"NEW.executor_actor_id:='"+MISSING+"'::uuid;"),
            ('operation_outcome',"NEW.result:=jsonb_set(NEW.result,'{revision}','\"99\"'::jsonb);"),
            ('operation_outcome',"NEW.result:=jsonb_set(NEW.result,'{disposition}','\"created\"'::jsonb);"),
            ('business_event',"NEW.scope_id:='"+ORG2+"'::uuid;"),
            ('business_event',"NEW.target:=jsonb_set(NEW.target,'{org_id}',to_jsonb('"+ORG2+"'::text));"),
            ('business_event',"NEW.executor_actor_id:='"+MISSING+"'::uuid;"),
            ('business_event',"NEW.transition:='{}'::jsonb;"),
        ]
        for table,mutation in mutations:
            before=self.snapshot(case)
            self.execute_sql(case,"CREATE FUNCTION access.fixture_forge_evidence() RETURNS trigger LANGUAGE plpgsql AS $fixture$ BEGIN "+mutation+" RETURN NEW; END $fixture$;REVOKE ALL ON FUNCTION access.fixture_forge_evidence() FROM PUBLIC;CREATE TRIGGER aa_fixture_forge_evidence BEFORE INSERT ON access."+table+" FOR EACH ROW EXECUTE FUNCTION access.fixture_forge_evidence()")
            try:self.denied(lambda:self.command(case,document(False,'1')),'operation_unavailable')
            finally:self.execute_sql(case,'DROP TRIGGER aa_fixture_forge_evidence ON access.'+table+';DROP FUNCTION access.fixture_forge_evidence()')
            assert self.snapshot(case)==before,'forged_evidence_partial_effect'
        self.record('matching-nonmatching-empty-MERGE-and-forged-outcome-event-org-target-executor-revision-disposition-transition-refuse-atomically')
    def late_wait_expiry(self):
        case='retry';replay=document(True,'3');self.command(case,replay);before=self.snapshot(case)
        owner=self.db(case);operator=self.db(case,'access_operator_urls')
        def invoke(value):
            try:
                with operator.begin() as c:
                    c.exec_driver_sql("SET LOCAL statement_timeout='9s';SET LOCAL lock_timeout='8s'")
                    c.execute(text(EXECUTE),bound(value)).all()
            except Exception as error:return getattr(getattr(error,'orig',None),'sqlstate',None)
            return 'accepted'
        try:
            # A stale expected revision must not win over expired observation after
            # either the business advisory wait or the final row coordination wait.
            waits=[
                ("SELECT pg_advisory_xact_lock(access.command_lock('access:organization-application:v1:"+ORG1+":synthetic_app'))",document(False,'999')),
                (f"SET LOCAL app.org_id='{ORG1}';SELECT * FROM access.organization_applications WHERE org_id='{ORG1}' AND app_id='synthetic_app' FOR UPDATE",document(False,'999')),
                ('LOCK TABLE access.operation_outcome IN ACCESS EXCLUSIVE MODE',replay),
                ('LOCK TABLE access.operation_outcome IN ACCESS EXCLUSIVE MODE',{**replay,'evidence_ref':'synthetic:changed'}),
                ('LOCK TABLE access.applications IN ACCESS EXCLUSIVE MODE',document(app='missing_app')),
            ]
            for lock,attempt in waits:
                with owner.connect() as holder:
                    tx=holder.begin();holder.exec_driver_sql(lock)
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        future=pool.submit(invoke,attempt)
                        self.wait_for_retry_lock(holder,future,advisory=False)
                        time.sleep(5.1);tx.rollback()
                        assert future.result(timeout=5)=='AC004','expired_wait_conflict_precedence'
                assert self.snapshot(case)==before
            # The app read itself is nonlocking. Its FK insertion later waits on
            # the parent key, after the earlier observation/revision checks.
            self.command(case,base.document('late_fk_app'));before=self.snapshot(case)
            with owner.connect() as holder:
                tx=holder.begin();holder.exec_driver_sql("SELECT * FROM access.applications WHERE app_id='late_fk_app' FOR UPDATE")
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future=pool.submit(invoke,document(app='late_fk_app'))
                    self.wait_for_retry_lock(holder,future,advisory=False)
                    time.sleep(5.1);tx.rollback()
                    assert future.result(timeout=5)=='AC004','late_fk_expiry_accepted'
            assert self.snapshot(case)==before
            # The evidence insert can wait after the row and outcome have been
            # inserted; expiry must roll all three effects back together.
            event_key=719328546001
            self.execute_sql(case,"CREATE FUNCTION access.fixture_wait_event() RETURNS trigger LANGUAGE plpgsql AS 'BEGIN PERFORM pg_advisory_xact_lock("+str(event_key)+");RETURN NEW;END';REVOKE ALL ON FUNCTION access.fixture_wait_event() FROM PUBLIC;CREATE TRIGGER aa_fixture_wait_event BEFORE INSERT ON access.business_event FOR EACH ROW EXECUTE FUNCTION access.fixture_wait_event()")
            try:
                with owner.connect() as holder:
                    tx=holder.begin();holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=event_key))
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        future=pool.submit(invoke,document(False,'3'))
                        self.wait_for_retry_lock(holder,future)
                        time.sleep(5.1);tx.rollback()
                        assert future.result(timeout=5)=='AC004','late_evidence_expiry_accepted'
            finally:self.execute_sql(case,'DROP TRIGGER aa_fixture_wait_event ON access.business_event;DROP FUNCTION access.fixture_wait_event()')
            assert self.snapshot(case)==before
        finally:owner.dispose();operator.dispose()
        self.record('stale-business-row-wait-expiry-precedes-conflict-late-FK-and-event-waits-rollback-row-outcome-event')
    def previous8(self,case,values,label):
        code="""import sys,json,os
from dataclasses import asdict
sys.path.insert(0,os.environ['PREVIOUS_OWNER'])
import access_operator as a
from sqlalchemy import create_engine
engine=create_engine(os.environ['QUALIFICATION_URL'].replace('postgresql:','postgresql+psycopg:'),hide_parameters=True)
try:
 with engine.connect() as c:
  receipts=[]
  for value in json.loads(os.environ['QUALIFICATION_COMMANDS']):
   receipt=a.execute(c,json.dumps(value).encode())
   assert a.execute(c,json.dumps(value).encode())==receipt
   target=dict(command=value['command'],app_id=value['payload']['app_id'])
   if value['command'] in ('permission.register','entry_permission.register'):target['permission']=value['payload']['permission']
   assert a.outcome(c,value['operation_id'],**target)==receipt
   receipts.append(asdict(receipt))
  print(json.dumps(receipts,default=str))
finally:engine.dispose()
"""
        env=dict(PATH='/usr/bin:/bin',LANG='C.UTF-8',PREVIOUS_OWNER=str(self.proof/'previous-root/services/access'),QUALIFICATION_URL=self.private['access_operator_urls'][case],QUALIFICATION_COMMANDS=json.dumps(values))
        result=subprocess.run([sys.executable,'-I','-B','-c',code],cwd=ROOT,env=env,capture_output=True,timeout=30)
        (self.proof/('previous8-'+label+'.log')).write_bytes(result.stdout+result.stderr)
        assert result.returncode==0,'actual_previous8_adapter_failed'
        return json.loads(result.stdout)
    def previous8_documents(self,app):
        return [base.document(app),storage.prior.prior.prior.document('previous8.'+app,app=app),
                storage.prior.prior.document('previous8.'+app,app=app),storage.prior.document(app=app)]
    def upgrade_previous(self):
        case='upgrade';before=self.snapshot(case)
        assert before['alembic_version']==[['access_0008']]
        previous_values=self.previous8_documents('previous8_before')
        previous_receipts=self.previous8(case,previous_values,'before-upgrade')
        assert len(previous_receipts)==4 and all(r['result']['disposition'] in ('created','changed') for r in previous_receipts)
        # Populate8 through its actual owner storage path, preserving historical attribution.
        self.execute_sql(case,f"SET LOCAL app.org_id='{ORG1}'; INSERT INTO access.organization_applications(org_id,app_id,enabled,revision,created_by,updated_by,created_at,updated_at) VALUES('{ORG1}','synthetic_app',false,7,'{ACTOR}','{ACTOR}','2001-01-01Z','2002-01-01Z')")
        self.command(case,base.document('max_app'))
        self.execute_sql(case,f"SET LOCAL app.org_id='{ORG1}'; INSERT INTO access.organization_applications(org_id,app_id,enabled,revision,created_by,updated_by,created_at,updated_at) VALUES('{ORG1}','max_app',false,9223372036854775807,'{ACTOR}','{ACTOR}','2001-01-01Z','2002-01-01Z')")
        populated=self.snapshot(case);self.migrate(case);after=self.snapshot(case)
        assert populated['permissions'] and populated['entry_permissions']
        for table in TABLES:assert after[table]==populated[table],table
        assert self.previous8(case,previous_values,'retained-after-upgrade')==previous_receipts
        assert self.snapshot(case)==after
        new_receipts=self.previous8(case,self.previous8_documents('previous8_after'),'new-after-upgrade')
        assert len(new_receipts)==4 and all(r['result']['disposition'] in ('created','changed') for r in new_receipts)
        self.authority(case);receipt=self.command(case,document(revision='7'));assert receipt.result.revision=='8'
        unchanged=self.command(case,document(False,'9223372036854775807',app='max_app'))
        assert unchanged.result.disposition=='unchanged' and unchanged.result.event_id is None
        frozen=self.snapshot(case)
        self.denied(lambda:self.command(case,document(True,'9223372036854775807',app='max_app')),'operation_conflict')
        assert self.snapshot(case)==frozen
        self.migrate(case);assert self.snapshot(case)==frozen
        self.record('populated8-four-old-adapter-command-upgrade9-exact-rows-receipts-new-replay-lookup-and-overflow')
    def rollback_recovery(self):
        case='rollback';before=self.snapshot(case)
        engine=self.db(case)
        try:
            with engine.connect() as c:
                tx=c.begin()
                try:
                    c.exec_driver_sql(baseline.LOCK_SQL);started=time.monotonic();self.migrate(case,success=False)
                    assert time.monotonic()-started<15
                finally:tx.rollback()
        finally:engine.dispose()
        assert self.snapshot(case)==before
        env=dict(PATH='/usr/bin:/bin',LANG='C.UTF-8',ACCESS_MIGRATION_DATABASE_URL=self.private['access_owner_urls'][case])
        code="import sys;sys.path.insert(0,"+repr(str(ACCESS/'migrations'))+");import access_baseline as b;from alembic.config import Config;from alembic import command;b.verify_postcondition=lambda c:(_ for _ in ()).throw(b.BaselineError('access_test_postcondition_failure'));command.upgrade(Config("+repr(str(ACCESS/'alembic.ini'))+"),'head')"
        result=subprocess.run([sys.executable,'-I','-B','-c',code],cwd=ROOT,env=env,capture_output=True,timeout=40)
        log=result.stdout+result.stderr;(self.proof/'injected-postcondition.log').write_bytes(log)
        assert result.returncode!=0 and b'access_test_postcondition_failure' in log
        assert self.snapshot(case)==before
        self.migrate(case);self.authority(case);assert self.command(case,document()).result.disposition=='created'
        self.record('migration-lock-and-injected-postcondition-whole-transaction-rollback-explicit-forward-recovery9')
    def catalog_and_identity(self):
        case='drift';before=self.snapshot(case);engine=self.db(case)
        alterations=[
          'ALTER TABLE access.organization_applications NO FORCE ROW LEVEL SECURITY',
          'ALTER TABLE access.organization_applications DISABLE TRIGGER organization_application_required_change',
          'ALTER TABLE access.organization_applications DROP CONSTRAINT organization_applications_app_id_fkey',
          'GRANT UPDATE ON access.organization_applications TO access_command_owner',
          'GRANT SELECT ON access.organization_applications TO access_operator',
          "UPDATE access.alembic_version SET version_num='access_unknown'",
          "GRANT CREATE ON SCHEMA access TO access_operator_authority_owner;SET LOCAL ROLE access_operator_authority_owner;CREATE OR REPLACE FUNCTION access.organization_application_authority(p_org uuid,p_app text) RETURNS uuid LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS 'SELECT NULL::uuid';RESET ROLE;REVOKE CREATE ON SCHEMA access FROM access_operator_authority_owner",
        ]
        try:
            for sql in alterations:
                with engine.connect() as c:
                    tx=c.begin()
                    try:
                        c.exec_driver_sql(sql)
                        try:baseline.preflight(c)
                        except baseline.BaselineError:pass
                        else:raise AssertionError('catalog_drift_accepted')
                    finally:tx.rollback()
                assert self.snapshot(case)==before
        finally:engine.dispose()
        for case in CASES:
            before=self.snapshot(case)
            env=dict(PATH='/usr/bin:/bin',LANG='C.UTF-8',IDENTITY_MIGRATION_DATABASE_URL=self.private['owner_urls'][case].replace('postgresql:','postgresql+psycopg:'))
            result=subprocess.run([sys.executable,'-I','-B','-m','alembic','-c',str(ACCESS/'identity-alembic.ini'),'upgrade','head'],cwd=ROOT,env=env,capture_output=True,timeout=40)
            (self.proof/(case+'-identity19-repeat.log')).write_bytes(result.stdout+result.stderr)
            assert result.returncode==0,'identity19_repeat_after9_failed'
            assert self.snapshot(case)==before
        self.record('exact9-catalog-rls-trigger-fk-acl-history-function-drift-refusal-Identity19-metadata-only-repeat')
    def cli(self):
        from identity_operator_target import prepare_target,load_target
        case='cli';run=json.loads((self.proof/'run.json').read_text())
        path=prepare_target(ROOT/'platform/deployment/environments/kdg-local.json',run['run_id'],owner='access',namespace=run['operator_namespace'])
        assert load_target(path,owner='access').database==self.db(case).url.database
        value=document();command_path=self.proof/'cli-command.json';command_path.write_text(json.dumps(value));command_path.chmod(0o600)
        common=[sys.executable,'-I','-B',str(ACCESS/'operator_cli.py')]
        env=dict(PATH='/usr/bin:/bin',LANG='C.UTF-8',PGPASSWORD='ambient-ignored',PGSERVICE='ambient-ignored')
        execute=subprocess.run(common+['execute','--owner','access','--target',str(path),'--command-file',str(command_path)],env=env,capture_output=True,timeout=15)
        (self.proof/'cli-execute.json').write_bytes(execute.stdout)
        assert execute.returncode==0 and not execute.stderr,'cli_execute_failed'
        lookup=subprocess.run(common+['outcome','--owner','access','--target',str(path),'--command',value['command'],'--org-id',ORG1,'--app-id','synthetic_app','--operation-id',value['operation_id']],env=env,capture_output=True,timeout=15)
        assert lookup.returncode==0 and not lookup.stderr and json.loads(lookup.stdout)==json.loads(execute.stdout)
        self.record('actual-isolated-CLI-exact-org-target-execute-and-scoped-recovery-ambient-libpq-ignored')
    def retained(self):
        for case in CASES:
            engine=self.db(case)
            try:
                with engine.begin() as c:
                    c.exec_driver_sql('SET TRANSACTION READ ONLY');baseline.preflight(c);baseline.verify_postcondition(c)
            finally:engine.dispose()
        self.record('separate-read-only-exact9-retained-inspection')


def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all',action='store_true');group.add_argument('--verify-retained',action='store_true');args=parser.parse_args()
    raw=Path(os.environ['ACCESS_QUALIFICATION_DIR']);assert '..' not in raw.parts
    proof=Path(os.path.abspath(raw));private,run=load_fixture(proof)
    captured=source_snapshot(proof);witness=json.loads((proof/'bootstrap-source-custody.json').read_text())
    assert witness['status']=='passed' and witness['before']==witness['after']==captured
    for name,digest in witness['logs'].items():assert sha256((proof/name).read_bytes()).hexdigest()==digest
    q=Qualification(proof,private)
    if args.all:
        (proof/'all-started').open('x').close()
        for method in (q.prepare_cases,q.functional,q.authority_and_identity,q.retry_and_recovery,q.guards,q.deferred_evidence_and_overflow,q.forged_evidence_and_merge,q.concurrency,q.freshness_and_revocation,q.late_wait_expiry,q.context_and_login_boundaries,q.upgrade_previous,q.rollback_recovery,q.catalog_and_identity,q.cli,q.retained):method()
        (proof/'retained-state.json').write_text(json.dumps({case:q.snapshot(case) for case in CASES},indent=2)+'\n')
    else:
        results=json.loads((proof/'results.json').read_text())
        assert results['status']=='passed' and results['source']==captured
        assert json.loads((proof/'retained-state.json').read_text())=={case:q.snapshot(case) for case in CASES}
        q.retained()
    assert captured==source_snapshot(proof),'qualification_source_changed'
    (proof/('results.json' if args.all else 'retained-results.json')).write_text(json.dumps(dict(status='passed',steps=q.results,source=captured),indent=2)+'\n')
    print(json.dumps(dict(ok=True,steps=q.results)))


if __name__=='__main__':
    try:main()
    except Exception as error:
        storage.report_failure(error)
        raise SystemExit(1) from None
