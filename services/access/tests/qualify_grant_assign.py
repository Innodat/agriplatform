"""Source-bound, single-use synthetic Access13 protected grant assignment proof."""
if not __debug__:
    raise RuntimeError('access_qualification_optimized_python_prohibited')
import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from hashlib import sha256
import importlib.util
import json,os,re,subprocess,sys,time
from pathlib import Path
from uuid import uuid4
from sqlalchemy import create_engine,text
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_strict_grant_integrity as strict
import qualify_identity_pregrant_target as pregrant
configure,base,storage=strict.configure,strict.base,strict.storage
ROOT,ACCESS,ACTOR=strict.ROOT,strict.ACCESS,strict.ACTOR
adapter,baseline=base.adapter,base.baseline
CASES=frozenset(('assign','authority','retry','guards','concurrency','upgrade','rollback','drift','cli'))
base.CASES=CASES
load_fixture=base.load_fixture
ORG1,ORG2=configure.ORG1,configure.ORG2
PERMISSION='kdg_capture.read.own'
OTHER_PERMISSION='synthetic.organization.second'
PREVIOUS_HASH='2921c87cc7504bcaa59b1aa784991c91023378a39ddd5b5b0e724d5c62075361'
EXECUTE='SELECT * FROM access.assign_organization_grant(CAST(:operation AS uuid),CAST(:org AS uuid),CAST(:account AS uuid),CAST(:member AS bigint),:permission,:absent,:revision,:reason,:evidence,:canonical)'


def previous_adapter(proof):
    path=proof/'previous12_access_operator.py'
    assert sha256(path.read_bytes()).hexdigest()==PREVIOUS_HASH,'previous12_adapter_source_mismatch'
    spec=importlib.util.spec_from_file_location('_previous12_access_operator',path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module


def source_snapshot(proof):
    paths={Path(__file__),Path(__file__).with_name('test_grant_assign.py'),Path(__file__).with_name('test_grant_assign_adapter.py'),Path(__file__).with_name('test_grant_assign_input.py'),ACCESS/'GRANT-ASSIGN.md',proof/'identity-operator-credential.json',proof/'previous12_access_operator.py'}
    # Reuse strict storage custody, including every consumed helper, root driver,
    # protected bootstrap dependency and original native run configuration.
    previous_adapter(proof)
    return strict.source_snapshot(proof)|{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths}


def qualification_logs(proof):
    patterns=[re.escape(case)+r'-(?:(?:head|access_[0-9]{4})-[0-9]+|identity19-repeat)\.log' for case in CASES]
    patterns += [r'injected-postcondition\.log',r'cli-(?:execute|outcome)\.json',r'rollback-(?:advisory|relation)-refusal\.json']
    return {p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(proof.iterdir()) if any(re.fullmatch(pattern,p.name) for pattern in patterns)}


def verify_qualification_logs(proof,expected):
    assert type(expected) is dict and expected,'qualification_logs_missing'
    assert qualification_logs(proof)==expected,'qualification_log_custody_mismatch'


def document(account,member,revision=None,permission=PERMISSION,org=ORG1,op=None):
    value=base.document(op=op);value['command']='grant.assign';value['scope']=dict(kind='organization',org_id=org)
    value['payload']=dict(account_id=account,membership_id=str(member),permission=permission,**({'expected_absent':True} if revision is None else {'expected_revision':str(revision)}))
    return value


def bound(value):
    command=base.parse_command(json.dumps(value).encode())
    return dict(operation=command.operation_id,org=command.scope.org_id,account=command.payload.account_id,member=command.payload.membership_id,permission=command.payload.permission,
        absent=getattr(command.payload,'expected_absent',False),revision=getattr(command.payload,'expected_revision',None),
        reason=command.reason_code,evidence=command.evidence_ref,canonical=adapter.canonical_command(command))


class Qualification(strict.Qualification):
    def migrate(self,case,head='access_0013',success=True):
        return storage.Qualification.migrate(self,case,'access_0013' if head=='head' else head,success)
    wait_for_retry_lock=configure.Qualification.wait_for_retry_lock
    def parameter_sql(self,case,sql,parameters=None,role='owner_urls'):
        engine=self.db(case,role)
        try:
            with engine.begin() as c:
                result=c.execute(text(sql),parameters or {})
                return result.all() if result.returns_rows else None
        finally:engine.dispose()
    def auxiliary_db(self,case,role='identity_operator'):
        filename={'identity_operator':'identity-operator-credential.json','access_runtime':'runtime-credential.json'}[role]
        source=self.db(case);url=source.url.set(username=role,password=pregrant.credential(self.proof,filename));source.dispose()
        return create_engine(url,hide_parameters=True,connect_args=base.CONNECTION_ARGS)
    def invoke(self,case,command,payload,org=None):
        import identity_operator
        value=dict(schema_version=1,operation_id=str(uuid4()),command=command,scope=dict(kind='platform') if org is None else dict(kind='organization',org_id=org),payload=payload,reason_code='synthetic_fixture',evidence_ref='synthetic:grant/target')
        engine=self.auxiliary_db(case)
        try:
            with engine.connect() as c:return identity_operator.execute(c,json.dumps(value).encode())
        finally:engine.dispose()
    def prepare_identity(self,case):
        self.parameter_sql(case,"INSERT INTO identity.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by) VALUES('identity_operator',:actor,true,:actor,:actor)",dict(actor=ACTOR))
        for org in (ORG1,ORG2):
            self.parameter_sql(case,"INSERT INTO identity.org(id,name,slug) VALUES(CAST(:id AS uuid),'Synthetic grant organization',:slug)",dict(id=org,slug='synthetic-grant-'+org))
        for command,org in [('account_actor.ensure',None),('membership.join',ORG1),('membership.join',ORG2),('membership.retire',ORG1)]:
            self.parameter_sql(case,"INSERT INTO identity.operator_authorities(id,database_login,command,scope_kind,org_id,enabled,created_by,updated_by) VALUES(:id,'identity_operator',:command,:scope,CAST(:org AS uuid),true,:actor,:actor)",dict(id=str(uuid4()),command=command,scope='platform' if org is None else 'organization',org=org,actor=ACTOR))
        accounts=[str(uuid4()) for _ in range(3)];actors=[str(uuid4()) for _ in range(2)]
        for account in accounts:
            self.parameter_sql(case,'INSERT INTO auth.users(id,email) VALUES(CAST(:id AS uuid),:email)',dict(id=account,email='synthetic-'+account+'@example.invalid'),role='databases')
        for account,actor in zip(accounts,actors):
            self.invoke(case,'account_actor.ensure',dict(account_id=account,actor_id=actor,display_name='Synthetic grant target',expected_absent=True))
        members=[self.invoke(case,'membership.join',dict(account_id=a,expected_previous_membership_id=None,is_owner=False),ORG1).result.target.membership_id for a in accounts]
        self.targets[case]=dict(account=accounts[0],member=members[0],actor=actors[0],other=accounts[1],other_member=members[1],unmapped=accounts[2],unmapped_member=members[2])
    def authority(self,case,org=ORG1,app=None,account=None,login='access_operator'):
        authority_id=str(uuid4())
        self.parameter_sql(case,"INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,org_id,application_id,target_account_id,enabled,created_by,updated_by) VALUES(:id,:login,'grant.assign','organization',CAST(:org AS uuid),:app,CAST(:account AS uuid),true,:actor,:actor)",dict(id=authority_id,login=login,org=org,app=app,account=account,actor=ACTOR),role='access_owner_urls')
        return authority_id
    def prepare_cases(self):
        self.targets={}
        for case in CASES:
            self.migrate(case,'access_0012' if case in ('upgrade','rollback') else 'head')
            self.seed(case);self.prepare_identity(case)
            self.command(case,base.document());self.command(case,strict.permission_document())
            self.command(case,strict.permission_document(OTHER_PERMISSION));self.command(case,strict.permission_document('account.only','account'))
            if case not in ('upgrade','rollback'):self.authority(case)
        self.record('nine-fresh-synthetic-Identity19-current-mapped-and-unmapped-exact-members-supported-ensure-join-Access12-and13')
    def target_document(self,case,revision=None,**kwargs):
        target=self.targets[case]
        return document(target['account'],target['member'],revision,**kwargs)
    def lookup(self,case,value,**overrides):
        args=dict(command='grant.assign',org_id=value['scope']['org_id'],account_id=value['payload']['account_id'],membership_id=value['payload']['membership_id'],permission=value['payload']['permission'])|overrides
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:return adapter.outcome(c,value['operation_id'],**args)
        finally:engine.dispose()
    def snapshot(self,case):
        value=super().snapshot(case)
        engine=self.admin(case)
        try:
            with engine.begin() as c:
                c.exec_driver_sql('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
                tables=c.exec_driver_sql("SELECT tablename FROM pg_tables WHERE schemaname='identity' ORDER BY tablename").scalars().all()
                value['identity']={name:c.exec_driver_sql('SELECT to_jsonb(t) FROM identity."'+name+'" t ORDER BY to_jsonb(t)::text').scalars().all() for name in tables}
                value['identity_sequences']=[list(r) for r in c.exec_driver_sql("SELECT sequencename,last_value FROM pg_sequences WHERE schemaname='identity' ORDER BY sequencename")]
        finally:engine.dispose()
        return json.loads(json.dumps(value,default=str))
    def unchanged_refusal(self,case,value,code):
        before=self.snapshot(case);self.denied(lambda:self.command(case,value),code);assert self.snapshot(case)==before
    def functional(self):
        case='assign';value=self.target_document(case);before=self.snapshot(case)
        receipt=self.command(case,value);after=self.snapshot(case);result=receipt.result
        assert result.disposition=='created' and result.revision=='1' and result.target.account_id==value['payload']['account_id']
        assert result.target.membership_id==value['payload']['membership_id'] and result.target.org_id==ORG1
        assert str(__import__('uuid').UUID(result.target.grant_id))==result.target.grant_id
        assert after['identity']==before['identity'] and after['identity_sequences']==before['identity_sequences']
        assert after['organization_applications']==[] and all(row[1] is False for row in after['applications'])
        assert len(after['grants'])==1 and len(after['operation_outcome'])==len(before['operation_outcome'])+1
        assert len(after['business_event'])==len(before['business_event'])+1
        outcome=next(row for row in after['operation_outcome'] if row[2]==value['operation_id'])
        assert outcome[-3:][0]==1 and outcome[-2]==self.targets[case]['actor'] and outcome[-1] is not None
        assert self.command(case,value)==receipt and self.lookup(case,value)==receipt and self.snapshot(case)==after
        noop=self.target_document(case,'1');unchanged=self.command(case,noop);current=self.snapshot(case)
        assert unchanged.result.disposition=='unchanged' and unchanged.result.event_id is None
        assert current['grants']==after['grants'] and current['business_event']==after['business_event']
        self.unchanged_refusal(case,self.target_document(case),'operation_conflict')
        self.unchanged_refusal(case,self.target_document(case,'2'),'operation_conflict')
        self.unchanged_refusal(case,self.target_document(case,permission='account.only'),'operation_conflict')
        self.unchanged_refusal(case,self.target_document(case,permission='unregistered'),'operation_conflict')
        literal='synthetic.literal:"\\\n\t\x01'
        self.command(case,strict.permission_document(literal))
        literal_value=self.target_document(case,permission=literal)
        literal_receipt=self.command(case,literal_value)
        assert literal_receipt.result.target.permission==literal and literal_receipt.result.disposition=='created'
        literal_state=self.snapshot(case)
        assert self.command(case,literal_value)==literal_receipt and self.lookup(case,literal_value)==literal_receipt
        assert self.snapshot(case)==literal_state
        self.record('exact-first-grant-disabled-admission-server-attribution-private-observation-atomic-event-replay-lookup-expected-before-noop-no-extra-event-literal-ASCII-quote-backslash-controls-canonical-agreement')
    def authority_and_identity(self):
        case='authority';target=self.targets[case];value=self.target_document(case)
        for field in ('enabled','principal'):
            table='operator_principals' if field=='principal' else 'operator_authorities'
            where="database_login='access_operator'"+(" AND command='grant.assign'" if field=='enabled' else '')
            self.execute_sql(case,'UPDATE access.'+table+' SET enabled=false WHERE '+where)
            self.unchanged_refusal(case,value,'access_denied')
            self.execute_sql(case,'UPDATE access.'+table+' SET enabled=true WHERE '+where)
        broad="command='grant.assign' AND application_id IS NULL AND target_account_id IS NULL"
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE "+broad)
        wrong_app=self.authority(case,app='other_app')
        self.unchanged_refusal(case,value,'access_denied')
        self.parameter_sql(case,'UPDATE access.operator_authorities SET enabled=false WHERE id=CAST(:id AS uuid)',dict(id=wrong_app),role='access_owner_urls')
        wrong_account=self.authority(case,app='synthetic_app',account=target['other'])
        self.unchanged_refusal(case,value,'access_denied')
        self.parameter_sql(case,'UPDATE access.operator_authorities SET enabled=false WHERE id=CAST(:id AS uuid)',dict(id=wrong_account),role='access_owner_urls')
        exact_account=self.authority(case,app='synthetic_app',account=target['account'])
        self.unchanged_refusal(case,self.target_document(case,org=ORG2),'access_denied')
        self.unchanged_refusal(case,document(target['other'],target['other_member']),'access_denied')
        receipt=self.command(case,value)
        assert receipt.result.disposition=='created'
        assert self.command(case,value)==receipt and self.lookup(case,value)==receipt
        self.blocked_identity_projection(case,value,document(target['other'],target['other_member']))
        self.inactive_identity_targets(case,value)
        self.parameter_sql(case,'UPDATE access.operator_authorities SET enabled=false WHERE id=CAST(:id AS uuid)',dict(id=exact_account),role='access_owner_urls')
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=true WHERE "+broad)
        self.unchanged_refusal(case,document(target['unmapped'],target['unmapped_member']),'operation_conflict')
        self.unchanged_refusal(case,document(target['account'],target['other_member']),'operation_conflict')
        self.unchanged_refusal(case,document(str(uuid4()),'9223372036854775807'),'operation_conflict')
        self.refused(case,"INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,org_id,target_account_id,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_operator','grant.assign','organization','"+ORG1+"','00000000-0000-0000-0000-000000000000',true,'"+ACTOR+"','"+ACTOR+"')",'23514',constraint='operator_authorities_target_account_id_check')
        assert self.command(case,value)==receipt
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='grant.assign'")
        self.denied(lambda:self.lookup(case,value),'access_denied');self.unchanged_refusal(case,value,'access_denied')
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=true WHERE "+broad)
        assert self.lookup(case,value)==receipt
        self.record('exact-command-principal-org-app-account-current-authority-null-explicit-all-unmapped-wrong-member-missing-target-nil-policy-restricted-positive-execute-replay-recovery-preprojection-denial-bounded-projection-failure-inactive-org-profile-and-revoked-receipt-denial')
    def blocked_identity_projection(self,case,authorized,unauthorized):
        before=self.snapshot(case);owner=self.db(case,'owner_urls')
        def attempt():
            try:self.command(case,authorized)
            except adapter.OperatorError as error:return error.code
            return 'accepted'
        try:
            with owner.connect() as holder:
                transaction=holder.begin()
                try:
                    holder.exec_driver_sql('LOCK TABLE identity.org_member IN ACCESS EXCLUSIVE MODE')
                    started=time.monotonic()
                    self.denied(lambda:self.command(case,unauthorized),'access_denied')
                    assert time.monotonic()-started<2,'unauthorized_request_entered_blocked_projection'
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        started=time.monotonic();future=pool.submit(attempt)
                        self.wait_for_retry_lock(holder,future,advisory=False)
                        assert future.result(timeout=6)=='operation_verification_unavailable','blocked_projection_wrong_failure'
                        assert time.monotonic()-started<6,'blocked_projection_unbounded'
                finally:transaction.rollback()
        finally:owner.dispose()
        # The snapshot itself reads Identity, so inspect only after releasing the lock.
        assert self.snapshot(case)==before,'blocked_projection_probe_changed_state'
    def inactive_identity_targets(self,case,value):
        target=self.targets[case];receipt=self.lookup(case,value)
        for table,key in [('users',target['account']),('org',ORG1)]:
            original=self.snapshot(case)
            self.parameter_sql(case,'UPDATE identity.'+table+' SET deleted_at=statement_timestamp() WHERE id=CAST(:id AS uuid)',dict(id=key))
            try:
                pregrant.verify_fixture_reference(original,self.snapshot(case),table,key,deleted=True)
                self.unchanged_refusal(case,value,'operation_conflict')
            finally:
                self.parameter_sql(case,'UPDATE identity.'+table+' SET deleted_at=NULL WHERE id=CAST(:id AS uuid)',dict(id=key))
            restored=self.snapshot(case)
            pregrant.verify_fixture_reference(original,restored,table,key,deleted=False)
            for name in ('grants','operation_outcome','business_event','applications','permissions','entry_permissions','organization_applications'):
                assert restored[name]==original[name],'inactive_fixture_changed_access:'+name
            assert self.lookup(case,value)==receipt
    def retry_and_recovery(self):
        case='retry';value=self.target_document(case);receipt=self.command(case,value)
        assert self.lookup(case,value)==receipt
        changed=json.loads(json.dumps(value));changed['reason_code']='setup_correction'
        self.unchanged_refusal(case,changed,'operation_conflict')
        self.denied(lambda:self.lookup(case,value,membership_id=self.targets[case]['other_member']),'access_denied')
        missing=self.target_document(case,'1');assert self.lookup(case,missing) is None
        self.record('lost-response-same-operation-recovery-payload-conflict-exact-target-selector-missing-unresolved')
    def guards(self):
        case='guards';value=self.target_document(case);target=self.targets[case];receipt=self.command(case,value)
        # Runtime and operator have no raw DML or command-owner assumption.
        self.refused(case,'UPDATE access.grants SET membership_id=membership_id','42501',role='access_operator_urls')
        self.refused(case,'SET ROLE access_command_owner','42501',role='access_operator_urls')
        self.refused(case,'UPDATE access.grants SET membership_id=membership_id','42501')
        for sql in ('DELETE FROM access.grants WHERE false','TRUNCATE access.grants'):
            self.refused(case,sql,'55000',message='access_registry_storage_immutable')
        self.parameter_sql(case,"INSERT INTO access.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by) VALUES('access_migrator',:actor,true,:actor,:actor)",dict(actor=ACTOR),role='access_owner_urls')
        self.authority(case,login='access_migrator')
        prefix=f"SET LOCAL app.context_kind='setup';SET LOCAL app.org_id='{ORG1}';SET LOCAL app.actor_id='{ACTOR}';SET LOCAL app.account_id='';SET LOCAL ROLE access_command_owner;"
        self.refused(case,'UPDATE access.grants SET membership_id=membership_id','23514',prefix=prefix,message='access_grant_update_invalid')
        self.refused(case,'UPDATE access.grants SET revoked_at=NULL WHERE false','23514',prefix=prefix,message='access_grant_statement_invalid')
        self.refused(case,'UPDATE access.grants SET membership_id='+target['other_member'],'23514',prefix=prefix,message='access_required_grant_change_missing')
        insert="INSERT INTO access.grants(org_id,id,user_id,permission,created_at,created_by,membership_id,created_actor_id,updated_actor_id,updated_at) VALUES('"+ORG1+"',gen_random_uuid()::text,'"+target['other']+"','"+PERMISSION+"',statement_timestamp(),'"+ACTOR+"',"+target['other_member']+",'"+ACTOR+"','"+ACTOR+"',statement_timestamp())"
        self.refused(case,insert,'23514',prefix=prefix,message='access_required_grant_change_missing')
        self.refused(case,insert+",('"+ORG1+"',gen_random_uuid()::text,'"+target['unmapped']+"','"+PERMISSION+"',statement_timestamp(),'"+ACTOR+"',"+target['unmapped_member']+",'"+ACTOR+"','"+ACTOR+"',statement_timestamp())",'23514',prefix=prefix,message='access_grant_statement_invalid')
        for changes in ({'account':None},{'account':storage.NIL},{'member':0},{'member':None},{'permission':None},{'permission':'é'},{'revision':'0','absent':False},{'absent':None},{'canonical':b'{}'},{'canonical':bound(value)['canonical']+b' '},{'operation':None}):
            self.refused(case,EXECUTE,'AC005',bound(value)|changes,role='access_operator_urls')
        self.refused(case,EXECUTE,'AC005',bound(value),role='access_operator_urls',context=None,prefix='SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')
        before=self.snapshot(case)
        self.execute_sql(case,"CREATE FUNCTION access.fixture_skip_grant_event() RETURNS trigger LANGUAGE plpgsql AS 'BEGIN RETURN NULL; END';REVOKE ALL ON FUNCTION access.fixture_skip_grant_event() FROM PUBLIC;CREATE TRIGGER aa_fixture_skip_grant_event BEFORE INSERT ON access.business_event FOR EACH ROW EXECUTE FUNCTION access.fixture_skip_grant_event()")
        try:self.denied(lambda:self.command(case,self.target_document(case,permission=OTHER_PERMISSION)),'operation_unavailable')
        finally:self.execute_sql(case,'DROP TRIGGER aa_fixture_skip_grant_event ON access.business_event;DROP FUNCTION access.fixture_skip_grant_event()')
        assert self.snapshot(case)==before
        forged="INSERT INTO access.operation_outcome(id,executor_actor_id,operation_id,command_type,scope_kind,scope_id,command_version,fingerprint_version,fingerprint_algorithm,fingerprint,result_version,result,verified_membership_revision,verified_account_actor_id,target_observed_at) SELECT gen_random_uuid(),executor_actor_id,gen_random_uuid(),command_type,scope_kind,scope_id,command_version,fingerprint_version,fingerprint_algorithm,fingerprint,result_version,result||jsonb_build_object('disposition','unchanged','event_id',NULL),:verified_revision,CAST(:verified_actor AS uuid),CASE :observed WHEN 'current' THEN clock_timestamp() WHEN 'future' THEN clock_timestamp()+interval '1 hour' ELSE CAST(NULLIF(NULLIF(:observed,'current'),'future') AS timestamptz) END FROM access.operation_outcome WHERE command_type='grant.assign' LIMIT 1"
        observation=dict(verified_revision=1,verified_actor=target['actor'],observed='current')
        for invalid in (dict(verified_revision=None),dict(verified_revision=0),dict(verified_revision=-1),dict(verified_actor=None),dict(verified_actor=storage.NIL),dict(observed=None),dict(observed='2001-01-01Z'),dict(observed='future'),dict(observed='infinity'),dict(observed='-infinity')):
            self.refused(case,forged,'23514',observation|invalid,prefix=prefix,message='access_grant_result_invalid')
        runtime=self.auxiliary_db(case,'access_runtime')
        try:
            try:
                with runtime.begin() as c:c.execute(text(EXECUTE),bound(value)).all()
            except Exception as error:assert getattr(getattr(error,'orig',None),'sqlstate',None)=='42501'
            else:raise AssertionError('runtime_command_accepted')
        finally:runtime.dispose()
        self.record('raw-runtime-operator-migrator-spoof-role-noop-empty-multirow-immutable-retention-required-paired-evidence-and-malformed-sql-rollback')
    def deferred_observation_commit(self):
        case='guards';target=self.targets[case]
        values=[document(target['other'],target['other_member']),self.target_document(case,'1')]
        engine=self.db(case,'access_operator_urls')
        try:
            for value in values:
                before=self.snapshot(case)
                try:
                    with engine.begin() as c:
                        assert c.exec_driver_sql('SHOW statement_timeout').scalar_one()=='5s'
                        result=c.execute(text(EXECUTE),bound(value)).one()
                        assert result[0]['disposition']==('created' if 'expected_absent' in value['payload'] else 'unchanged')
                        # Each statement remains within the existing5s SQL budget;
                        # their total exceeds the one observation lifetime.
                        c.exec_driver_sql('SELECT pg_sleep(2.6)')
                        c.exec_driver_sql('SELECT pg_sleep(2.6)')
                except Exception as error:
                    assert getattr(getattr(error,'orig',None),'sqlstate',None)=='AC004','delayed_grant_commit_wrong_refusal'
                else:raise AssertionError('expired_grant_observation_committed')
                assert self.snapshot(case)==before,'expired_grant_commit_changed_state'
        finally:engine.dispose()
        self.record('created-and-unchanged-no-event-delayed-commit-total-observation-deadline-AC004-entire-transaction-rollback-default-statement-budgets')
    def concurrency(self):
        case='concurrency';target=self.targets[case];value=self.target_document(case)
        owner=self.db(case)
        def attempt(v):
            try:return self.command(case,v)
            except adapter.OperatorError as error:return error.code
        try:
            # Hold retry serialization so both sessions have observed Identity before
            # waiting. Identical operations produce one durable result/event.
            key=adapter.command_outcome_lock_key(ACTOR,base.parse_command(json.dumps(value).encode()))
            with owner.connect() as holder:
                tx=holder.begin();holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=key))
                with ThreadPoolExecutor(max_workers=2) as pool:
                    futures=[pool.submit(attempt,value) for _ in range(2)]
                    self.wait_for_retry_lock(holder,futures,count=2);tx.rollback()
                    receipts=[f.result(timeout=10) for f in futures]
            assert receipts[0]==receipts[1] and not isinstance(receipts[0],str)
            before=self.snapshot(case)
            values=[document(target['other'],target['other_member']) for _ in range(2)]
            with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(attempt,values))
            assert sum(isinstance(r,str) and r=='operation_conflict' for r in results)==1
            after=self.snapshot(case)
            assert len(after['grants'])==len(before['grants'])+1 and len(after['business_event'])==len(before['business_event'])+1
            original=next(row for row in after['grants'] if row[2]==target['other'])
            self.invoke(case,'membership.retire',dict(account_id=target['other'],membership_id=target['other_member'],expected_revision='1'),ORG1)
            replacement=self.invoke(case,'membership.join',dict(account_id=target['other'],expected_previous_membership_id=target['other_member'],is_owner=False),ORG1).result.target.membership_id
            before_rebind=self.snapshot(case)
            rebinds=[document(target['other'],replacement,'1') for _ in range(2)]
            with owner.connect() as holder:
                transaction=holder.begin()
                # Gate both operations before their shared authority/business
                # serialization, so each has observed the supplied replacement.
                for rebind in rebinds:
                    key=adapter.command_outcome_lock_key(ACTOR,base.parse_command(json.dumps(rebind).encode()))
                    holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=key))
                try:
                    with ThreadPoolExecutor(max_workers=2) as pool:
                        futures=[pool.submit(attempt,rebind) for rebind in rebinds]
                        self.wait_for_retry_lock(holder,futures,count=2)
                        transaction.rollback()
                        results=[future.result(timeout=6) for future in futures]
                finally:
                    if transaction.is_active:transaction.rollback()
            conflicts=[result for result in results if isinstance(result,str)]
            changed=[result for result in results if not isinstance(result,str)]
            assert conflicts==['operation_conflict'] and len(changed)==1
            assert changed[0].result.disposition=='changed' and changed[0].result.revision=='2'
            assert changed[0].result.target.grant_id==original[1] and changed[0].result.target.membership_id==replacement
            after_rebind=self.snapshot(case)
            rebound=next(row for row in after_rebind['grants'] if row[1]==original[1])
            assert rebound[:6]==original[:6] and rebound[10]==original[10]
            assert len(after_rebind['grants'])==len(before_rebind['grants'])
            assert len(after_rebind['operation_outcome'])==len(before_rebind['operation_outcome'])+1
            assert len(after_rebind['business_event'])==len(before_rebind['business_event'])+1
            # Only the operation retry lock has the typed busy mapping.
            next_value=self.target_document(case,'1')
            locks=[('operation',adapter.command_outcome_lock_key(ACTOR,base.parse_command(json.dumps(next_value).encode())),'operation_busy'),
                ('authority',None,'operation_unavailable'),('business',None,'operation_unavailable'),('row',None,'operation_unavailable')]
            for kind,key,code in locks:
                before=self.snapshot(case)
                with owner.connect() as holder:
                    tx=holder.begin()
                    if kind=='row':
                        holder.execute(text("SELECT set_config('app.org_id',:org,true)"),dict(org=ORG1))
                        holder.execute(text('SELECT id FROM access.grants WHERE user_id=CAST(:account AS uuid) FOR UPDATE'),dict(account=target['account'])).all()
                    elif kind=='operation':holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=key))
                    else:
                        label='access:operator-authority:v1:access_operator' if kind=='authority' else 'access:organization-grant:v1:'+ORG1+':'+target['account']+':'+PERMISSION
                        holder.execute(text('SELECT pg_advisory_xact_lock(access.command_lock(:label))'),dict(label=label))
                    started=time.monotonic()
                    try:assert attempt(next_value)==code
                    finally:tx.rollback()
                    assert time.monotonic()-started<6
                assert self.snapshot(case)==before
        finally:owner.dispose()
        self.record('identical-concurrent-retry-one-event-independent-expected-absence-and-changed-rebind-races-one-winner-preserved-ID-creation-bounded-operation-authority-business-locks')
    def freshness_and_retirement(self):
        case='retry';target=self.targets[case];owner=self.db(case);operator=self.db(case,'access_operator_urls')
        def sql_attempt(value):
            try:
                with operator.begin() as c:
                    c.exec_driver_sql("SET LOCAL statement_timeout='9s'; SET LOCAL lock_timeout='8s'")
                    return c.execute(text(EXECUTE),bound(value)).all()
            except Exception as error:return getattr(getattr(error,'orig',None),'sqlstate',None)
        try:
            # Expiry includes waits on new operations and same-operation replay.
            original=self.target_document(case,'1');receipt=self.command(case,original)
            for value in (self.target_document(case,'1'),original):
                before=self.snapshot(case);key=adapter.command_outcome_lock_key(ACTOR,base.parse_command(json.dumps(value).encode()))
                with owner.connect() as holder:
                    tx=holder.begin();holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=key))
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        future=pool.submit(sql_attempt,value);self.wait_for_retry_lock(holder,future)
                        time.sleep(5.1);tx.rollback();assert future.result(timeout=5)=='AC004'
                assert self.snapshot(case)==before
            # Exact authority revoked during the wait is checked before replay/effects.
            value=self.target_document(case,'1');key=adapter.command_outcome_lock_key(ACTOR,base.parse_command(json.dumps(value).encode()))
            with owner.connect() as holder:
                tx=holder.begin();holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=key))
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future=pool.submit(sql_attempt,value);self.wait_for_retry_lock(holder,future)
                    self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='grant.assign'")
                    tx.rollback();assert future.result(timeout=5)=='AC002'
            self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=true WHERE command='grant.assign'")
            assert self.lookup(case,original)==receipt
            # Retirement after observation preserves that exact observed binding; a
            # replacement receives nothing without an explicit fresh verified regrant.
            race=document(target['other'],target['other_member']);key=adapter.command_outcome_lock_key(ACTOR,base.parse_command(json.dumps(race).encode()))
            with owner.connect() as holder:
                tx=holder.begin();holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=key))
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future=pool.submit(sql_attempt,race);self.wait_for_retry_lock(holder,future)
                    self.invoke(case,'membership.retire',dict(account_id=target['other'],membership_id=target['other_member'],expected_revision='1'),ORG1)
                    replacement=self.invoke(case,'membership.join',dict(account_id=target['other'],expected_previous_membership_id=target['other_member'],is_owner=False),ORG1).result.target.membership_id
                    tx.rollback();assert isinstance(future.result(timeout=5),list)
            race_receipt=self.lookup(case,race);assert race_receipt.result.target.membership_id==target['other_member']
            self.unchanged_refusal(case,race,'operation_conflict')
            regrant=document(target['other'],replacement,'1');changed=self.command(case,regrant)
            assert changed.result.disposition=='changed' and changed.result.revision=='2'
            assert changed.result.target.grant_id==race_receipt.result.target.grant_id
            assert self.lookup(case,race)==race_receipt
        finally:owner.dispose();operator.dispose()
        self.record('five-second-total-observation-expiry-new-and-replay-revocation-after-wait-retire-rejoin-race-exact-old-binding-deliberate-regrant-no-replacement-inference')
    def upgrade_previous(self):
        case='upgrade';target=self.targets[case];prior=previous_adapter(self.proof)
        entry=base.document();entry['command']='entry_permission.register';entry['payload']['permission']=PERMISSION
        enable=base.document();enable['command']='application.set_enabled';enable['payload']=dict(app_id='synthetic_app',enabled=False,expected_revision='1')
        values=[base.document(),strict.permission_document(),entry,enable,configure.document(False)]
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:receipts=[prior.execute(c,json.dumps(v).encode()) for v in values]
        finally:engine.dispose()
        # Exact historical records are created under12 before the protected writer
        # is installed, including opaque ID, partial creator and overflow cases.
        self.explicit_insert(case,strict.values()|dict(id='opaque é historical',user=target['account'],membership_id=int(target['member']),revoked_at='2001-01-01Z',revision=7))
        self.explicit_insert(case,strict.values()|dict(id='',user=target['other'],membership_id=int(target['other_member']),revision=9223372036854775807))
        self.explicit_insert(case,strict.values(complete=False)|dict(id='unknown-history',user=target['account'],permission=OTHER_PERMISSION,revoked_at='2001-01-01Z'))
        before=self.snapshot(case);self.identity_repeat(case);self.migrate(case);after=self.snapshot(case)
        assert after['alembic_version']==[['access_0013']] and after['grants']==before['grants']
        for name in ('applications','permissions','entry_permissions','organization_applications','business_event','identity','identity_sequences'):
            assert after[name]==before[name],name
        assert [row[:-3] for row in after['operation_outcome']]==before['operation_outcome']
        assert all(row[-3:]==[None,None,None] for row in after['operation_outcome'])
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:
                for value,receipt in zip(values,receipts):
                    assert prior.execute(c,json.dumps(value).encode())==receipt
                    args=dict(command=value['command'],app_id=value['payload']['app_id'])
                    if 'permission' in value['payload']:args['permission']=value['payload']['permission']
                    if value['scope']['kind']=='organization':args['org_id']=ORG1
                    assert prior.outcome(c,value['operation_id'],**args)==receipt
                fresh_app='previous12_fresh'
                fresh_permission='synthetic.previous12.fresh'
                fresh_registration=base.document(fresh_app)
                fresh_permission_doc=strict.permission_document(fresh_permission);fresh_permission_doc['payload']['app_id']=fresh_app
                fresh_entry=base.document(fresh_app);fresh_entry['command']='entry_permission.register';fresh_entry['payload']['permission']=fresh_permission
                fresh_enabled=base.document(fresh_app);fresh_enabled['command']='application.set_enabled';fresh_enabled['payload']=dict(app_id=fresh_app,enabled=True,expected_revision='1')
                fresh_configured=configure.document(True,'1')
                fresh_values=[fresh_registration,fresh_permission_doc,fresh_entry,fresh_enabled,fresh_configured]
                fresh_receipts=[prior.execute(c,json.dumps(value).encode()) for value in fresh_values]
                assert [receipt.result.disposition for receipt in fresh_receipts]==['created','created','created','changed','changed']
                assert fresh_receipts[3].result.revision=='2' and fresh_receipts[4].result.revision=='2'
                for value,receipt in [*zip(fresh_values,fresh_receipts),*zip(values,receipts)]:
                    assert prior.execute(c,json.dumps(value).encode())==receipt
                    args=dict(command=value['command'],app_id=value['payload']['app_id'])
                    if 'permission' in value['payload']:args['permission']=value['payload']['permission']
                    if value['scope']['kind']=='organization':args['org_id']=ORG1
                    assert prior.outcome(c,value['operation_id'],**args)==receipt
        finally:engine.dispose()
        self.authority(case)
        changed=self.command(case,self.target_document(case,'7'))
        assert changed.result.target.grant_id=='opaque é historical' and changed.result.revision=='8'
        row=next(r for r in self.snapshot(case)['grants'] if r[1]=='opaque é historical')
        original=next(r for r in before['grants'] if r[1]=='opaque é historical')
        assert row[:6]==original[:6] and row[10]==original[10]
        maximum=self.command(case,document(target['other'],target['other_member'],'9223372036854775807'))
        assert maximum.result.disposition=='unchanged' and maximum.result.target.grant_id=='' and maximum.result.event_id is None
        self.invoke(case,'membership.retire',dict(account_id=target['other'],membership_id=target['other_member'],expected_revision='1'),ORG1)
        replacement=self.invoke(case,'membership.join',dict(account_id=target['other'],expected_previous_membership_id=target['other_member'],is_owner=False),ORG1).result.target.membership_id
        self.unchanged_refusal(case,document(target['other'],replacement,'9223372036854775807'),'operation_conflict')
        self.unchanged_refusal(case,self.target_document(case,'1',permission=OTHER_PERMISSION),'operation_conflict')
        state=self.snapshot(case);self.migrate(case);assert self.snapshot(case)==state
        self.identity_repeat(case)
        self.record('populated12-to13-opaque-empty-IDs-original-creation-partial-history-overflow-five-actual-previous-client-fresh-commands-real-enablement-configuration-changes-original-and-new-receipt-replays-lookups-exact13-repeat-Identity19-metadata-only')
    def rollback_recovery(self):
        case='rollback'
        # Reuse controlled migration helper with an injected final assertion. The
        # migration transaction must retain exact12, then succeed by forward retry.
        before=self.snapshot(case)
        env=dict(PATH='/usr/bin:/bin',LANG='C.UTF-8',ACCESS_MIGRATION_DATABASE_URL=self.private['access_owner_urls'][case])
        code="import sys;sys.path.insert(0,"+repr(str(ACCESS/'migrations'))+");import access_baseline as b;from alembic.config import Config;from alembic import command;b.verify_postcondition=lambda c:(_ for _ in ()).throw(b.BaselineError('access_test_postcondition_failure'));command.upgrade(Config("+repr(str(ACCESS/'alembic.ini'))+"),'access_0013')"
        result=subprocess.run([sys.executable,'-I','-B','-c',code],cwd=ROOT,env=env,capture_output=True,timeout=40)
        path=self.proof/'injected-postcondition.log';path.write_bytes(result.stdout+result.stderr);path.chmod(0o600)
        assert result.returncode!=0 and b'access_test_postcondition_failure' in path.read_bytes()
        assert self.snapshot(case)==before
        self.migrate(case);self.authority(case);receipt=self.command(case,self.target_document(case))
        assert receipt.result.disposition=='created'
        self.record('injected-postcondition-atomic-migration-rollback-exact12-retained-controlled-forward-retry')
    def catalog_and_identity(self):
        case='drift';before=self.snapshot(case);engine=self.db(case)
        alterations=['ALTER TABLE access.grants DISABLE TRIGGER grant_required_change',
            'ALTER TABLE access.grants NO FORCE ROW LEVEL SECURITY','GRANT UPDATE(permission) ON access.grants TO access_command_owner',
            'ALTER TABLE access.operation_outcome DROP COLUMN target_observed_at',
            "UPDATE access.alembic_version SET version_num='access_unknown'",
            'DROP POLICY command_org_scope ON access.grants',
            'ALTER FUNCTION access.assign_organization_grant(uuid,uuid,uuid,bigint,text,boolean,text,text,text,bytea) RESET search_path']
        try:
            for sql in alterations:
                with engine.connect() as c:
                    tx=c.begin()
                    try:
                        function_owner=sql.startswith('ALTER FUNCTION access.assign_organization_grant(')
                        if function_owner:c.exec_driver_sql('SET LOCAL ROLE access_command_owner')
                        c.exec_driver_sql(sql)
                        if function_owner:c.exec_driver_sql('RESET ROLE')
                        try:baseline.preflight(c)
                        except baseline.BaselineError:pass
                        else:raise AssertionError('assignment_catalog_drift_accepted')
                    finally:tx.rollback()
                assert self.snapshot(case)==before
        finally:engine.dispose()
        for case in CASES:self.identity_repeat(case)
        self.record('trigger-RLS-column-ACL-evidence-shape-history-policy-function-drift-refused-without-normalization-all-Identity19-repeats')
    def cli(self):
        from identity_operator_target import prepare_target,load_target
        case='cli';run=json.loads((self.proof/'run.json').read_text())
        path=prepare_target(ROOT/'platform/deployment/environments/kdg-local.json',run['run_id'],owner='access',namespace=run['operator_namespace'])
        target=load_target(path,owner='access');engine=self.db(case)
        try:assert target.database==engine.url.database
        finally:engine.dispose()
        value=self.target_document(case);command_path=self.proof/'cli-command.json';command_path.write_text(json.dumps(value));command_path.chmod(0o600)
        env=dict(PATH='/usr/bin:/bin',LANG='C.UTF-8',PGPASSWORD='ambient-ignored',PGSERVICE='ambient-ignored')
        common=[sys.executable,'-I','-B',str(ACCESS/'operator_cli.py')]
        child=subprocess.run(common+['execute','--owner','access','--target',str(path),'--command-file',str(command_path)],env=env,capture_output=True,timeout=15)
        assert child.returncode==0 and not child.stderr,'grant_cli_execute_failed'
        receipt=json.loads(child.stdout);assert receipt['result']['target']['account_id']==value['payload']['account_id']
        (self.proof/'cli-execute.json').write_bytes(child.stdout)
        lookup=subprocess.run(common+['outcome','--owner','access','--target',str(path),'--command','grant.assign','--org-id',ORG1,'--account-id',value['payload']['account_id'],'--membership-id',value['payload']['membership_id'],'--permission',PERMISSION,'--operation-id',value['operation_id']],env=env,capture_output=True,timeout=15)
        assert lookup.returncode==0 and not lookup.stderr and json.loads(lookup.stdout)==receipt,'grant_cli_outcome_failed'
        (self.proof/'cli-outcome.json').write_bytes(lookup.stdout)
        self.record('real-closed-owner-bound-cli-execute-exact-account-member-receipt-recovery-ambient-libpq-ignored')
    def retained(self):
        for case in CASES:
            engine=self.db(case)
            try:
                with engine.begin() as c:
                    c.exec_driver_sql('SET TRANSACTION READ ONLY');baseline.preflight(c);baseline.verify_catalog(c,'access_0013')
                    assert c.exec_driver_sql('SELECT version_num FROM access.alembic_version').all()==[('access_0013',)]
            finally:engine.dispose()
        self.record('separate-read-only-all-nine-exact13-retained-inspection')


def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all',action='store_true');group.add_argument('--verify-retained',action='store_true');args=parser.parse_args()
    raw=Path(os.environ['ACCESS_QUALIFICATION_DIR']);assert '..' not in raw.parts
    proof=Path(os.path.abspath(raw));private,run=load_fixture(proof)
    captured=source_snapshot(proof);witness=json.loads((proof/'bootstrap-source-custody.json').read_text())
    assert witness['status']=='passed' and witness['before']==witness['after']==captured,'bootstrap_source_custody_mismatch'
    assert set(witness['generated_inputs'])=={'credentials.json','run.json'},'generated_input_inventory_mismatch'
    for name,digest in witness['generated_inputs'].items():assert sha256((proof/name).read_bytes()).hexdigest()==digest,'generated_input_custody_mismatch'
    assert witness['logs'] and all(Path(name).name==name and name.startswith('bootstrap') and name.endswith('.log') for name in witness['logs'])
    for name,digest in witness['logs'].items():assert sha256((proof/name).read_bytes()).hexdigest()==digest,'bootstrap_log_custody_mismatch'
    if not args.all:
        result=json.loads((proof/'results.json').read_text());assert result['status']=='passed' and result['source']==captured,'result_source_custody_mismatch'
        verify_qualification_logs(proof,result['logs'])
        assert sha256((proof/'retained-state.json').read_bytes()).hexdigest()==result['retained_state_sha256'],'retained_state_custody_mismatch'
    q=Qualification(proof,private)
    if args.all:
        (proof/'all-started').open('x').close()
        for method in (q.prepare_cases,q.functional,q.authority_and_identity,q.retry_and_recovery,q.guards,q.deferred_observation_commit,q.concurrency,q.freshness_and_retirement,q.upgrade_previous,q.rollback_recovery,q.catalog_and_identity,q.cli,q.retained):method()
        (proof/'retained-state.json').write_text(json.dumps({case:q.snapshot(case) for case in CASES},indent=2)+'\n')
    else:
        assert json.loads((proof/'retained-state.json').read_text())=={case:q.snapshot(case) for case in CASES},'retained_state_changed'
        q.retained()
    assert captured==source_snapshot(proof),'qualification_source_changed'
    path=proof/('results.json' if args.all else 'retained-results.json')
    path.write_text(json.dumps(dict(status='passed',steps=q.results,source=captured,logs=qualification_logs(proof),retained_state_sha256=sha256((proof/'retained-state.json').read_bytes()).hexdigest()),indent=2)+'\n')
    print(json.dumps(dict(ok=True,steps=q.results)))


if __name__=='__main__':
    try:main()
    except Exception as error:
        storage.report_failure(error)
        raise SystemExit(1) from None
