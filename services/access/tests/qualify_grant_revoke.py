"""Source-bound single-use native Access14 exact retained grant revocation proof."""
if not __debug__:
    raise RuntimeError('access_qualification_optimized_python_prohibited')
import argparse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import importlib.util
import json,os,re,subprocess,sys,time
from pathlib import Path
from uuid import uuid4
from sqlalchemy import text
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_grant_assign as assign
base,strict,configure,storage=assign.base,assign.strict,assign.configure,assign.storage
ROOT,ACCESS,ACTOR=assign.ROOT,assign.ACCESS,assign.ACTOR
adapter,baseline=assign.adapter,assign.baseline
ORG1,ORG2=assign.ORG1,assign.ORG2
PERMISSION,OTHER_PERMISSION=assign.PERMISSION,assign.OTHER_PERMISSION
CASES=assign.CASES
base.CASES=CASES
load_fixture=assign.load_fixture
qualification_logs,verify_qualification_logs=assign.qualification_logs,assign.verify_qualification_logs
PREVIOUS_HASH='0df72ca03c50d5a218268f95005e7c6554ce11f69629b4cc8ac927ecee238ced'
EXECUTE='SELECT * FROM access.revoke_organization_grant(CAST(:operation AS uuid),CAST(:org AS uuid),:grant,CAST(:account AS uuid),CAST(:member AS bigint),:permission,:revision,:reason,:evidence,:canonical)'


def previous_adapter(proof):
    path=proof/'previous13_access_operator.py'
    assert sha256(path.read_bytes()).hexdigest()==PREVIOUS_HASH,'previous13_adapter_source_mismatch'
    spec=importlib.util.spec_from_file_location('_previous13_access_operator',path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module


def source_snapshot(proof):
    previous_adapter(proof)
    paths=[Path(__file__),Path(__file__).with_name('test_grant_revoke.py'),Path(__file__).with_name('test_grant_revoke_adapter.py'),Path(__file__).with_name('test_grant_revoke_input.py'),ACCESS/'GRANT-REVOKE.md',proof/'previous13_access_operator.py']
    return assign.source_snapshot(proof)|{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths}


def document(account,member,grant,revision='1',permission=PERMISSION,org=ORG1,op=None):
    value=assign.document(account,member,revision,permission,org,op);value['command']='grant.revoke'
    value['payload']['grant_id']=grant
    return value


def bound(value):
    command=base.parse_command(json.dumps(value,ensure_ascii=False,separators=(',',':')).encode())
    return dict(operation=command.operation_id,org=command.scope.org_id,grant=command.payload.grant_id,account=command.payload.account_id,member=command.payload.membership_id,permission=command.payload.permission,revision=command.payload.expected_revision,reason=command.reason_code,evidence=command.evidence_ref,canonical=adapter.canonical_command(command))


def cli_child_ok(child,stage):
    if child.returncode==0 and not child.stderr:
        return True
    from operator_cli import CODES
    code='operation_unavailable'
    try:
        value=json.loads(child.stdout)
        if type(value) is dict and value.get('code') in CODES:code=value['code']
    except (ValueError,TypeError):pass
    print(json.dumps(dict(stage=stage,returncode=child.returncode,code=code,stderr_bytes=len(child.stderr))),flush=True)
    return False


class Qualification(assign.Qualification):
    def migrate(self,case,head='access_0014',success=True):
        return storage.Qualification.migrate(self,case,'access_0014' if head=='head' else head,success)
    def authority(self,case,org=ORG1,app=None,account=None,login='access_operator'):
        identifier=str(uuid4())
        self.parameter_sql(case,"INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,org_id,application_id,target_account_id,enabled,created_by,updated_by) VALUES(:id,:login,'grant.revoke','organization',CAST(:org AS uuid),:app,CAST(:account AS uuid),true,:actor,:actor)",dict(id=identifier,login=login,org=org,app=app,account=account,actor=ACTOR),role='access_owner_urls')
        return identifier
    def prepare_cases(self):
        self.targets={};self.grants={};self.boundary_grants={}
        for case in CASES:
            self.migrate(case,'access_0012');self.seed(case);self.prepare_identity(case)
            self.command(case,base.document());self.command(case,strict.permission_document())
            self.command(case,strict.permission_document(OTHER_PERMISSION));self.command(case,strict.permission_document('account.only','account'))
            target=self.targets[case]
            if case in ('cli','upgrade'):
                opaque=''
                if case=='cli':
                    sample=document(target['account'],target['member'],'');sample.pop('evidence_ref',None)
                    overhead=len(adapter.canonical_command(base.parse_command(json.dumps(sample).encode())))
                    prefix='-é🙂\t"\\'
                    remaining=65556-overhead-len(json.dumps(prefix,ensure_ascii=False).encode())+2
                    opaque=prefix+'é'*(remaining//2)+'x'*(remaining%2)
                self.explicit_insert(case,strict.values()|dict(id=opaque,user=target['account'],membership_id=int(target['member'])))
                self.grants[case]=opaque
            if case=='cli':
                self.boundary_grants={}
                for name,permission,evidence,size in (('oversize',PERMISSION,None,65557),('nonnull',OTHER_PERMISSION,'e',65536)):
                    sample=document(target['other'],target['other_member'],'',permission=permission)
                    if evidence is None:sample.pop('evidence_ref',None)
                    else:sample['evidence_ref']=evidence
                    overhead=len(bound(sample)['canonical']);prefix='-'+name+'é🙂\t"\\'
                    remaining=size-overhead-len(json.dumps(prefix,ensure_ascii=False).encode())+2
                    opaque=prefix+'é'*(remaining//2)+'x'*(remaining%2)
                    self.explicit_insert(case,strict.values(permission)|dict(id=opaque,user=target['other'],membership_id=int(target['other_member'])))
                    self.boundary_grants[name]=opaque
            if case=='upgrade':
                self.explicit_insert(case,strict.values()|dict(id='overflow-active',user=target['other'],membership_id=int(target['other_member']),revision=9223372036854775807))
                self.explicit_insert(case,strict.values()|dict(id='overflow-revoked',user=target['other'],permission=OTHER_PERMISSION,membership_id=int(target['other_member']),revision=9223372036854775807,revoked_at='2001-01-01Z'))
            self.migrate(case,'access_0013');assign.Qualification.authority(self,case)
            if case not in ('cli','upgrade'):
                self.grants[case]=self.command(case,assign.document(target['account'],target['member'])).result.target.grant_id
            if case not in ('upgrade','rollback'):
                self.migrate(case);self.authority(case)
        self.record('nine-fresh-source-bound-Identity19-Access13-populated-grants-controlled14-no-consumer-activation')
    def target_document(self,case,revision='1',**kwargs):
        target=self.targets[case]
        return document(target['account'],target['member'],self.grants[case],revision,**kwargs)
    def lookup(self,case,value,**overrides):
        p=value['payload'];args=dict(command='grant.revoke',org_id=value['scope']['org_id'],grant_id=p['grant_id'],account_id=p['account_id'],membership_id=p['membership_id'],permission=p['permission'])|overrides
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:return adapter.outcome(c,value['operation_id'],**args)
        finally:engine.dispose()
    def functional(self):
        case='assign';value=self.target_document(case);value.update(reason_code='access_change',evidence_ref='synthetic:revoke/exact-provenance');before=self.snapshot(case)
        receipt=self.command(case,value);after=self.snapshot(case)
        assert receipt.result.disposition=='changed' and receipt.result.revision=='2'
        assert receipt.result.target.grant_id==self.grants[case]
        assert after['identity']==before['identity'] and after['identity_sequences']==before['identity_sequences']
        assert len(after['business_event'])==len(before['business_event'])+1 and len(after['operation_outcome'])==len(before['operation_outcome'])+1
        row=after['grants'][0];old=before['grants'][0]
        assert row[:8]==old[:8] and row[9] is not None and row[10]==old[10] and row[11]==ACTOR
        outcome=next(r for r in after['operation_outcome'] if r[2]==value['operation_id']);assert outcome[-3:]==[None,None,None]
        event=next(r for r in after['business_event'] if r[0]==receipt.result.event_id)
        assert event[-3:-1]==[value['reason_code'],value['evidence_ref']]
        assert self.command(case,value)==receipt and self.lookup(case,value)==receipt and self.snapshot(case)==after
        noop=self.target_document(case,'2');unchanged=self.command(case,noop);state=self.snapshot(case)
        assert unchanged.result.disposition=='unchanged' and unchanged.result.event_id is None and state['grants']==after['grants'] and state['business_event']==after['business_event']
        for key,bad in [('grant_id','replacement'),('membership_id',self.targets[case]['other_member']),('account_id',self.targets[case]['other']),('expected_revision','1'),('permission',OTHER_PERMISSION)]:
            wrong=self.target_document(case,'2');wrong['payload'][key]=bad;self.unchanged_refusal(case,wrong,'operation_conflict')
        self.record('exact-active-change-server-attribution-creation-preserved-atomic-event-outcome-replay-noop-stale-wrong-all-selectors-no-effects')
    def authority_and_identity(self):
        case='authority';value=self.target_document(case)
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='grant.revoke'")
        self.unchanged_refusal(case,value,'access_denied')
        self.authority(case,app='other_app');self.authority(case,app='synthetic_app',account=self.targets[case]['other'])
        self.unchanged_refusal(case,value,'access_denied')
        exact=self.authority(case,app='synthetic_app',account=self.targets[case]['account'])
        # No Identity observation: a locked target table cannot delay removal.
        owner=self.db(case,'owner_urls');before=self.snapshot(case)
        try:
            with owner.connect() as holder:
                tx=holder.begin();holder.exec_driver_sql('LOCK TABLE identity.org_member IN ACCESS EXCLUSIVE MODE')
                receipt=self.command(case,value);assert self.lookup(case,value)==receipt;tx.rollback()
        finally:owner.dispose()
        assert self.snapshot(case)['identity']==before['identity']
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='grant.revoke'")
        self.denied(lambda:self.lookup(case,value),'access_denied');self.unchanged_refusal(case,value,'access_denied')
        self.execute_sql(case,"UPDATE access.operator_principals SET enabled=false WHERE database_login='access_operator'")
        self.denied(lambda:self.lookup(case,value),'access_denied')
        self.execute_sql(case,"UPDATE access.operator_principals SET enabled=true WHERE database_login='access_operator'")
        self.parameter_sql(case,'UPDATE access.operator_authorities SET enabled=true WHERE id=CAST(:id AS uuid)',dict(id=exact),role='access_owner_urls')
        assert self.lookup(case,value)==receipt
        self.refused(case,"INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,org_id,target_account_id,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_operator','grant.revoke','organization','"+ORG1+"','00000000-0000-0000-0000-000000000000',true,'"+ACTOR+"','"+ACTOR+"')",'23514',constraint='operator_authorities_target_account_id_check')
        self.record('independent-current-original-session-command-org-app-account-authority-no-Identity-projection-nil-policy-denial-disabled-principal-recovery-denial')
    def retry_and_recovery(self):
        case='retry';value=self.target_document(case);receipt=self.command(case,value);before=self.snapshot(case)
        assert self.command(case,value)==receipt and self.lookup(case,value)==receipt
        changed=json.loads(json.dumps(value));changed['reason_code']='setup_correction';self.unchanged_refusal(case,changed,'operation_conflict')
        for key,bad in [('grant_id','replacement'),('membership_id',self.targets[case]['other_member']),('account_id',self.targets[case]['other']),('permission',OTHER_PERMISSION),('org_id',ORG2)]:
            self.denied(lambda key=key,bad=bad:self.lookup(case,value,**{key:bad}),'access_denied' if key!='org_id' else 'access_denied')
        assert self.snapshot(case)==before
        # Assignment and revoke may reuse operation UUID because command namespaces differ.
        target=self.targets[case];regrant=assign.document(target['account'],target['member'],'2',op=value['operation_id'])
        assigned=self.command(case,regrant);assert assigned.result.revision=='3'
        assert self.lookup(case,value)==receipt
        self.unchanged_refusal(case,self.target_document(case,'2'),'operation_conflict')
        self.record('same-changed-retry-exact-six-selector-recovery-historical-receipt-command-namespace-isolated-regrant-stale-revoke')
    def retired_targets(self):
        case='guards';target=self.targets[case]
        self.invoke(case,'membership.retire',dict(account_id=target['account'],membership_id=target['member'],expected_revision='1'),ORG1)
        replacement=self.invoke(case,'membership.join',dict(account_id=target['account'],expected_previous_membership_id=target['member'],is_owner=False),ORG1).result.target.membership_id
        wrong=self.target_document(case);wrong['payload']['membership_id']=replacement;self.unchanged_refusal(case,wrong,'operation_conflict')
        self.parameter_sql(case,'UPDATE identity.org SET deleted_at=statement_timestamp() WHERE id=CAST(:id AS uuid)',dict(id=ORG1))
        self.parameter_sql(case,'UPDATE identity.users SET deleted_at=statement_timestamp() WHERE id=CAST(:id AS uuid)',dict(id=target['account']))
        before=self.snapshot(case);receipt=self.command(case,self.target_document(case));after=self.snapshot(case)
        assert receipt.result.target.membership_id==target['member'] and receipt.result.revision=='2'
        assert after['identity']==before['identity'] and after['identity_sequences']==before['identity_sequences']
        self.record('retire-rejoin-deleted-organization-profile-original-binding-removable-no-replacement-authority')
    def evidence_mutations(self,case,value,prefix):
        # Each fixture and the attempted command share one rollback-only owner
        # transaction, so forged evidence never escapes into retained state.
        mutations=(
            ('operation_outcome',"NEW.result:=jsonb_set(NEW.result,'{target,account_id}',to_jsonb('"+ORG2+"'::text));",'access_grant_result_invalid'),
            ('operation_outcome',"NEW.executor_actor_id:='"+ORG2+"';",'access_grant_result_invalid'),
            ('operation_outcome',"NEW.result:=jsonb_set(NEW.result,'{disposition}','\"created\"'::jsonb);",'access_grant_result_invalid'),
            ('business_event',"NEW.target:=jsonb_set(NEW.target,'{membership_id}','\"999999\"'::jsonb);",'access_event_invalid'),
            ('business_event',"NEW.executor_actor_id:='"+ORG2+"';",'access_event_invalid'),
            ('business_event',"NEW.event_type:='access.organization_grant_assigned';",'access_event_invalid'),
            ('business_event',"NEW.transition:=jsonb_set(NEW.transition,'{before,membership_id}','\"999999\"'::jsonb);",'access_event_invalid'),
            ('business_event',"NEW.transition:=jsonb_set(NEW.transition,'{before,revoked_at}','\"2001-01-01T00:00:00Z\"'::jsonb);",'access_event_invalid'),
            ('business_event',"NEW.transition:=jsonb_set(NEW.transition,'{before,revision}','\"999999\"'::jsonb);",'access_event_invalid'),
            ('business_event',"NEW.transition:=jsonb_set(NEW.transition,'{after,membership_id}','\"999999\"'::jsonb);",'access_event_invalid'),
            ('business_event',"NEW.transition:=jsonb_set(NEW.transition,'{after,revoked_at}','null'::jsonb);",'access_event_invalid'),
            ('business_event',"NEW.transition:=jsonb_set(NEW.transition,'{after,revision}','\"999999\"'::jsonb);",'access_event_invalid'))
        for table,mutation,message in mutations:
            fixture="CREATE FUNCTION access.fixture_mutate_revoke_evidence() RETURNS trigger LANGUAGE plpgsql AS $fixture$ BEGIN "+mutation+" RETURN NEW; END $fixture$; REVOKE ALL ON FUNCTION access.fixture_mutate_revoke_evidence() FROM PUBLIC; CREATE TRIGGER aa_fixture_mutate_revoke_evidence BEFORE INSERT ON access."+table+" FOR EACH ROW EXECUTE FUNCTION access.fixture_mutate_revoke_evidence();"
            self.refused(case,EXECUTE,'23514',bound(value),prefix=fixture+prefix,message=message)
        self.record('rollback-only-revoke-outcome-target-executor-disposition-and-event-target-executor-type-before-after-adversaries')
    def forged_unchanged(self,case,prefix):
        forged="INSERT INTO access.operation_outcome(id,executor_actor_id,operation_id,command_type,scope_kind,scope_id,command_version,fingerprint_version,fingerprint_algorithm,fingerprint,result_version,result) SELECT gen_random_uuid(),executor_actor_id,gen_random_uuid(),command_type,scope_kind,scope_id,command_version,fingerprint_version,fingerprint_algorithm,fingerprint,result_version,jsonb_set(result||jsonb_build_object('disposition','unchanged','event_id',NULL),CAST(:path AS text[]),CAST(:value AS jsonb)) FROM access.operation_outcome WHERE command_type='grant.revoke' LIMIT 1"
        for path,value in (('{revision}','"999999"'),('{target,membership_id}','"999999"'),('{target,account_id}','"'+ORG2+'"'),('{target,grant_id}','"wrong-retained-binding"')):
            self.refused(case,forged,'23514',dict(path=path,value=value),prefix=prefix,message='access_grant_result_invalid')
        self.record('rollback-only-command-owner-forged-unchanged-revision-account-member-grant-binding-refused')
    def guards(self):
        case='guards';value=self.target_document(case);parameters=bound(value)
        for change,state in (({'grant':None},'AC005'),({'revision':'0'},'AC005'),({'account':'00000000-0000-0000-0000-000000000000'},'AC005'),({'canonical':parameters['canonical']+b' '},'AC005'),({'canonical':parameters['canonical'].replace(b'"grant.revoke"',b'"grant.assign"')},'AC005'),({'grant':'forged'},'AC005')):
            self.refused(case,EXECUTE,state,parameters|change,role='access_operator_urls')
        lookup='SELECT * FROM access.organization_grant_revocation_outcome(CAST(:operation AS uuid),CAST(:org AS uuid),:grant,CAST(:account AS uuid),CAST(:member AS bigint),:permission)'
        self.refused(case,lookup,'AC005',{k:v for k,v in parameters.items() if k in ('operation','org','grant','account','member','permission')}|dict(grant='é'*32769),role='access_operator_urls')
        for sql in ("UPDATE access.grants SET revoked_at=statement_timestamp()", "DELETE FROM access.grants", "TRUNCATE access.grants"):
            self.refused(case,sql,'55000' if sql.startswith(('DELETE','TRUNCATE')) else '42501')
        self.parameter_sql(case,"INSERT INTO access.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by) VALUES('access_migrator',:actor,true,:actor,:actor)",dict(actor=ACTOR),role='access_owner_urls')
        self.authority(case,login='access_migrator')
        prefix="SET LOCAL app.context_kind='setup'; SET LOCAL app.org_id='"+ORG1+"'; SET LOCAL app.actor_id='"+ACTOR+"'; SET LOCAL app.account_id=''; SET LOCAL ROLE access_command_owner;"
        self.refused(case,'UPDATE access.grants SET revoked_at=statement_timestamp()','23514',prefix=prefix,message='access_required_grant_change_missing')
        self.refused(case,"UPDATE access.grants SET revoked_at=statement_timestamp() WHERE false",'23514',prefix=prefix,message='access_grant_statement_invalid')
        self.refused(case,"UPDATE access.grants SET revoked_at=statement_timestamp()-interval '1 second'",'23514',prefix=prefix,message='access_grant_update_invalid')
        self.evidence_mutations(case,value,prefix)
        # Drop required event via an isolated fixture trigger: the entire change rolls back.
        before=self.snapshot(case)
        self.execute_sql(case,"CREATE FUNCTION access.fixture_skip_revoke_event() RETURNS trigger LANGUAGE plpgsql AS 'BEGIN RETURN NULL; END'; REVOKE ALL ON FUNCTION access.fixture_skip_revoke_event() FROM PUBLIC; CREATE TRIGGER aa_fixture_skip_revoke_event BEFORE INSERT ON access.business_event FOR EACH ROW EXECUTE FUNCTION access.fixture_skip_revoke_event()")
        try:self.denied(lambda:self.command(case,value),'operation_unavailable')
        finally:self.execute_sql(case,'DROP TRIGGER aa_fixture_skip_revoke_event ON access.business_event; DROP FUNCTION access.fixture_skip_revoke_event()')
        assert self.snapshot(case)==before
        target=self.targets[case]
        self.command(case,assign.document(target['other'],target['other_member']))
        self.refused(case,'UPDATE access.grants SET revoked_at=statement_timestamp()','23514',prefix=prefix,message='access_grant_statement_invalid')
        self.retired_targets()
        self.forged_unchanged(case,prefix)
        self.record('raw-malformed-canonical-selector-SQL-owner-DML-paired-evidence-rollback')
    def recovery_waits(self,case,value):
        def attempt():
            try:return self.lookup(case,value)
            except adapter.OperatorError as error:return error.code
        retry=adapter.command_outcome_lock_key(ACTOR,base.parse_command(json.dumps(value).encode()))
        owner=self.db(case)
        try:
            for kind,code in (('retry','operation_busy'),('authority','operation_unavailable')):
                before=self.snapshot(case)
                with owner.connect() as holder:
                    tx=holder.begin()
                    if kind=='retry':holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=retry))
                    else:holder.exec_driver_sql("SELECT pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:access_operator'))")
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        future=pool.submit(attempt);self.wait_for_retry_lock(holder,future)
                        assert future.result(timeout=5)==code
                    tx.rollback()
                assert self.snapshot(case)==before
            for kind in ('retry','authority'):
                before=self.snapshot(case)
                with owner.connect() as holder:
                    tx=holder.begin()
                    if kind=='retry':holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=retry))
                    else:holder.exec_driver_sql("SELECT pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:access_operator'))")
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        future=pool.submit(attempt);self.wait_for_retry_lock(holder,future)
                        if kind=='retry':
                            self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='grant.revoke'")
                            tx.rollback()
                        else:
                            # Holder owns this same authority lock, so the ordinary
                            # guarded update is reentrant and commits on release.
                            holder.exec_driver_sql("UPDATE access.operator_authorities SET enabled=false WHERE command='grant.revoke'")
                            tx.commit()
                        assert future.result(timeout=5)=='access_denied'
                after=self.snapshot(case)
                for name in before:
                    if name!='operator_authorities':assert after[name]==before[name],name
                self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=true WHERE command='grant.revoke'")
        finally:owner.dispose()
        self.record('lookup-witnessed-retry-only-busy-authority-timeout-released-retry-and-authority-current-denial-no-business-evidence-Identity-effects')
    def concurrency(self):
        case='concurrency';value=self.target_document(case)
        with ThreadPoolExecutor(max_workers=2) as pool:
            receipts=list(pool.map(lambda _:self.command(case,value),range(2)))
        assert receipts[0]==receipts[1]
        current=self.target_document(case,'2');assert self.command(case,current).result.disposition=='unchanged'
        target=self.targets[case];regrant=assign.document(target['account'],target['member'],'2');self.command(case,regrant)
        # Both intents would change revision3. The replacement is current only for
        # assignment; revoke must retain the original historical membership.
        self.invoke(case,'membership.retire',dict(account_id=target['account'],membership_id=target['member'],expected_revision='1'),ORG1)
        replacement=self.invoke(case,'membership.join',dict(account_id=target['account'],expected_previous_membership_id=target['member'],is_owner=False),ORG1).result.target.membership_id
        revoke=self.target_document(case,'3');assign_value=assign.document(target['account'],replacement,'3')
        def attempt(v):
            try:return self.command(case,v)
            except adapter.OperatorError as error:return error.code
        before=self.snapshot(case);owner=self.db(case)
        try:
            with owner.connect() as holder:
                tx=holder.begin()
                label='access:organization-grant:v1:'+ORG1+':'+target['account']+':'+PERMISSION
                holder.execute(text('SELECT pg_advisory_xact_lock(access.command_lock(:label))'),dict(label=label))
                with ThreadPoolExecutor(max_workers=2) as pool:
                    first=pool.submit(attempt,revoke);self.wait_for_retry_lock(holder,first)
                    second=pool.submit(attempt,assign_value)
                    deadline=time.monotonic()+1
                    while True:
                        holder.exec_driver_sql('SELECT pg_stat_clear_snapshot()')
                        waiting=holder.exec_driver_sql("SELECT count(DISTINCT l.pid) FROM pg_locks l JOIN pg_stat_activity a ON a.pid=l.pid WHERE a.datname=current_database() AND a.usename='access_operator' AND NOT l.granted AND l.locktype='advisory'").scalar_one()
                        if waiting>=2:break
                        assert not first.done() and not second.done() and time.monotonic()<deadline,'two_changed_race_waiters_not_observed'
                        time.sleep(.01)
                    tx.rollback();results=[first.result(timeout=5),second.result(timeout=5)]
        finally:owner.dispose()
        changed=[r for r in results if not isinstance(r,str)]
        assert len(changed)==1 and changed[0].result.disposition=='changed' and changed[0].result.revision=='4'
        assert results.count('operation_conflict')==1
        after=self.snapshot(case)
        assert len(after['operation_outcome'])==len(before['operation_outcome'])+1 and len(after['business_event'])==len(before['business_event'])+1
        if changed[0].result.command=='grant.assign':self.targets[case]['member']=replacement
        # Retry lock alone maps busy; authority revoked during a wait denies effects.
        fresh=self.target_document(case,'4')
        key=adapter.command_outcome_lock_key(ACTOR,base.parse_command(json.dumps(fresh).encode()))
        owner=self.db(case)
        try:
            with owner.connect() as holder:
                tx=holder.begin();holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=key))
                self.denied(lambda:self.command(case,fresh),'operation_busy');tx.rollback()
            with owner.connect() as holder:
                tx=holder.begin();holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),dict(key=key))
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future=pool.submit(attempt,fresh);self.wait_for_retry_lock(holder,future)
                    self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=false WHERE command='grant.revoke'")
                    tx.rollback();assert future.result(timeout=5)=='access_denied'
        finally:owner.dispose()
        self.execute_sql(case,"UPDATE access.operator_authorities SET enabled=true WHERE command='grant.revoke'")
        # Authority, business coordination and row waits use the adapter's bounded
        # unavailable mapping; only the exact retry namespace produces busy.
        owner=self.db(case)
        try:
            for kind in ('authority','business','row'):
                fresh=self.target_document(case,'4');before=self.snapshot(case)
                with owner.connect() as holder:
                    tx=holder.begin();holder.execute(text("SELECT set_config('app.org_id',:org,true)"),dict(org=ORG1))
                    if kind=='row':holder.execute(text('SELECT id FROM access.grants WHERE org_id=CAST(:org AS uuid) AND id=:grant FOR UPDATE'),dict(org=ORG1,grant=self.grants[case])).all()
                    else:
                        label='access:operator-authority:v1:access_operator' if kind=='authority' else 'access:organization-grant:v1:'+ORG1+':'+target['account']+':'+PERMISSION
                        holder.execute(text('SELECT pg_advisory_xact_lock(access.command_lock(:label))'),dict(label=label))
                    self.denied(lambda:self.command(case,fresh),'operation_unavailable');tx.rollback()
                assert self.snapshot(case)==before
        finally:owner.dispose()
        self.recovery_waits(case,value)
        self.record('concurrent-identical-once-shared-assignment-revoke-revision-serialization-retry-busy-authority-business-row-bounded-unavailable-recheck-after-wait')
    def upgrade_previous(self):
        case='upgrade';prior=previous_adapter(self.proof);target=self.targets[case]
        entry=base.document();entry['command']='entry_permission.register';entry['payload']['permission']=PERMISSION
        enable=base.document();enable['command']='application.set_enabled';enable['payload']=dict(app_id='synthetic_app',enabled=False,expected_revision='1')
        values=[base.document(),strict.permission_document(),entry,enable,configure.document(False),assign.document(target['account'],target['member'],'1')]
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:receipts=[prior.execute(c,json.dumps(v).encode()) for v in values]
        finally:engine.dispose()
        before=self.snapshot(case);self.migrate(case);after=self.snapshot(case)
        for name in ('grants','operation_outcome','business_event','identity','identity_sequences'):assert after[name]==before[name],name
        self.authority(case);self.identity_repeat(case)
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:
                fresh_app='previous13_fresh';fresh_permission='synthetic.previous13.fresh'
                registration=base.document(fresh_app)
                permission=strict.permission_document(fresh_permission);permission['payload']['app_id']=fresh_app
                entry=base.document(fresh_app);entry['command']='entry_permission.register';entry['payload']['permission']=fresh_permission
                enabled=base.document(fresh_app);enabled['command']='application.set_enabled';enabled['payload']=dict(app_id=fresh_app,enabled=True,expected_revision='1')
                configured=configure.document(True,'1')
                granted=assign.document(target['account'],target['member'],permission=OTHER_PERMISSION)
                fresh=[registration,permission,entry,enabled,configured,granted]
                fresh_receipts=[prior.execute(c,json.dumps(v).encode()) for v in fresh]
                assert [r.result.disposition for r in fresh_receipts]==['created','created','created','changed','changed','created']
                for value,receipt in [*zip(values,receipts),*zip(fresh,fresh_receipts)]:
                    assert prior.execute(c,json.dumps(value).encode())==receipt
                    args=dict(command=value['command'])
                    if value['command']=='grant.assign':args.update(org_id=ORG1,account_id=value['payload']['account_id'],membership_id=value['payload']['membership_id'],permission=value['payload']['permission'])
                    else:
                        args['app_id']=value['payload']['app_id']
                        if 'permission' in value['payload']:args['permission']=value['payload']['permission']
                        if value['scope']['kind']=='organization':args['org_id']=ORG1
                    assert prior.outcome(c,value['operation_id'],**args)==receipt
        finally:engine.dispose()
        revoked=self.command(case,self.target_document(case));assert revoked.result.revision=='2' and revoked.result.target.grant_id==''
        regrant=assign.document(target['account'],target['member'],'2')
        engine=self.db(case,'access_operator_urls')
        try:
            with engine.connect() as c:assert prior.execute(c,json.dumps(regrant).encode()).result.revision=='3'
        finally:engine.dispose()
        self.unchanged_refusal(case,document(target['other'],target['other_member'],'overflow-active','9223372036854775807'),'operation_conflict')
        noop=self.command(case,document(target['other'],target['other_member'],'overflow-revoked','9223372036854775807',OTHER_PERMISSION))
        assert noop.result.disposition=='unchanged' and noop.result.revision=='9223372036854775807'
        for key,bad in (('grant_id','wrong-overflow'),('account_id',target['account']),('membership_id',target['member']),('permission',PERMISSION),('expected_revision','9223372036854775806')):
            wrong=document(target['other'],target['other_member'],'overflow-revoked','9223372036854775807',OTHER_PERMISSION)
            wrong['payload'][key]=bad;self.unchanged_refusal(case,wrong,'operation_conflict')
        before=self.snapshot(case);self.migrate(case);assert self.snapshot(case)==before
        self.record('populated13-to14-exact-history-identity-preservation-six-previous13-clients-fresh-replay-recovery-deliberate-regrant-opaque-empty-overflow-change-only-repeat')
    def rollback_recovery(self):
        case='rollback';before=self.snapshot(case)
        code="import sys;sys.path.insert(0,"+repr(str(ACCESS/'migrations'))+");import access_baseline as b;from alembic.config import Config;from alembic import command;b.verify_postcondition=lambda c:(_ for _ in ()).throw(b.BaselineError('access_test_postcondition_failure'));command.upgrade(Config("+repr(str(ACCESS/'alembic.ini'))+"),'access_0014')"
        env=dict(PATH='/usr/bin:/bin',LANG='C.UTF-8',ACCESS_MIGRATION_DATABASE_URL=self.private['access_owner_urls'][case])
        child=subprocess.run([sys.executable,'-I','-B','-c',code],cwd=ROOT,env=env,capture_output=True,timeout=40)
        (self.proof/'injected-postcondition.log').write_bytes(child.stdout+child.stderr)
        assert child.returncode and b'access_test_postcondition_failure' in child.stderr and self.snapshot(case)==before
        self.migrate(case);self.authority(case);assert self.command(case,self.target_document(case)).result.revision=='2'
        self.record('failed14-postcondition-full-rollback-preserved13-forward-controlled-recovery')
    def catalog_and_identity(self):
        case='drift';engine=self.db(case);before=self.snapshot(case)
        drifts=["ALTER TABLE access.grants DISABLE ROW LEVEL SECURITY","ALTER TABLE access.grants DISABLE TRIGGER grant_write_guard","GRANT UPDATE ON access.grants TO access_operator","ALTER FUNCTION access.grant_revocation_authority(uuid,text,uuid) RESET search_path","ALTER TABLE access.operator_authorities DROP CONSTRAINT operator_authorities_command_check"]
        try:
            with engine.connect() as c:
                for sql in drifts:
                    tx=c.begin()
                    try:
                        authority=sql.startswith('ALTER FUNCTION access.grant_revocation_authority(')
                        if authority:c.exec_driver_sql('SET LOCAL ROLE access_operator_authority_owner')
                        c.exec_driver_sql(sql)
                        if authority:c.exec_driver_sql('RESET ROLE')
                        try:baseline.preflight(c)
                        except baseline.BaselineError:pass
                        else:raise AssertionError('revoke_catalog_drift_accepted')
                    finally:tx.rollback()
        finally:engine.dispose()
        assert self.snapshot(case)==before
        for case in CASES:self.identity_repeat(case)
        self.record('exact14-catalog-RLS-trigger-ACL-function-policy-drift-refused-without-normalization-Identity19-repeat')
    def cli(self):
        from identity_operator_target import prepare_target,load_target
        case='cli';run=json.loads((self.proof/'run.json').read_text())
        path=prepare_target(ROOT/'platform/deployment/environments/kdg-local.json',run['run_id'],owner='access',namespace=run['operator_namespace'])
        value=self.target_document(case);value.pop('evidence_ref',None);command_path=self.proof/'cli-command.json';command_path.write_text(json.dumps(value,ensure_ascii=False,separators=(',',':')));command_path.chmod(0o600)
        assert len(command_path.read_bytes())==65536 and len(bound(value)['canonical'])==65556
        # Exact retained selectors and matching canonical arguments isolate the size
        # check: without it these commands have valid current target/revision state.
        target=self.targets[case]
        oversized=document(target['other'],target['other_member'],self.boundary_grants['oversize']);oversized.pop('evidence_ref',None)
        short=json.loads(json.dumps(oversized));short['payload']['grant_id']=short['payload']['grant_id'][:-1]
        oversized_params=bound(short);oversized_params['grant']=oversized['payload']['grant_id']
        oversized_params['canonical']=oversized_params['canonical'].replace(json.dumps(short['payload']['grant_id'],ensure_ascii=False).encode(),json.dumps(oversized_params['grant'],ensure_ascii=False).encode(),1)
        assert len(oversized_params['canonical'])==65557
        self.refused(case,EXECUTE,'AC005',oversized_params,role='access_operator_urls')
        explicit=document(target['other'],target['other_member'],self.boundary_grants['nonnull'],permission=OTHER_PERMISSION);explicit['evidence_ref']='e'
        parameters=bound(explicit);assert len(parameters['canonical'])==65536
        rows=self.parameter_sql(case,EXECUTE,parameters,role='access_operator_urls');assert rows[0][0]['revision']=='2'
        explicit['operation_id']=str(uuid4());explicit['payload']['expected_revision']='2'
        parameters=bound(explicit);parameters['evidence']='ee'
        parameters['canonical']=parameters['canonical'].replace(b'"evidence_ref":"e"',b'"evidence_ref":"ee"',1)
        assert len(parameters['canonical'])==65537
        self.refused(case,EXECUTE,'AC005',parameters,role='access_operator_urls')
        env=dict(PATH='/usr/bin:/bin',LANG='C.UTF-8',PGPASSWORD='ambient-ignored',PGSERVICE='ambient-ignored')
        common=[sys.executable,'-I','-B',str(ACCESS/'operator_cli.py')]
        child=subprocess.run(common+['execute','--owner','access','--target',str(path),'--command-file',str(command_path)],env=env,capture_output=True,timeout=15)
        assert cli_child_ok(child,'revoke_cli_execute'),'revoke_cli_execute_failed';receipt=json.loads(child.stdout)
        assert len(child.stdout)>8192 and receipt['result']['target']['grant_id']==value['payload']['grant_id']
        (self.proof/'cli-execute.json').write_bytes(child.stdout)
        p=value['payload'];lookup=subprocess.run(common+['outcome','--owner','access','--target',str(path),'--command','grant.revoke','--org-id',ORG1,'--grant-id='+p['grant_id'],'--account-id',p['account_id'],'--membership-id',p['membership_id'],'--permission='+p['permission'],'--operation-id',value['operation_id']],env=env,capture_output=True,timeout=15)
        assert cli_child_ok(lookup,'revoke_cli_outcome') and json.loads(lookup.stdout)==receipt,'revoke_cli_outcome_failed'
        (self.proof/'cli-outcome.json').write_bytes(lookup.stdout)
        self.record('real-closed-cli-execute-six-selector-current-authorized-recovery-ambient-ignored')
    def retained(self):
        for case in CASES:
            engine=self.db(case)
            try:
                with engine.begin() as c:
                    c.exec_driver_sql('SET TRANSACTION READ ONLY');baseline.preflight(c);baseline.verify_postcondition(c)
                    assert c.exec_driver_sql('SELECT version_num FROM access.alembic_version').all()==[('access_0014',)]
            finally:engine.dispose()
        self.record('separate-read-only-all-nine-exact14-retained-inspection')


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
        for method in (q.prepare_cases,q.functional,q.authority_and_identity,q.retry_and_recovery,q.guards,q.concurrency,q.upgrade_previous,q.rollback_recovery,q.catalog_and_identity,q.cli,q.retained):method()
        (proof/'retained-state.json').write_text(json.dumps({case:q.snapshot(case) for case in CASES},indent=2)+'\n')
    else:
        assert json.loads((proof/'retained-state.json').read_text())=={case:q.snapshot(case) for case in CASES},'retained_state_changed';q.retained()
    assert captured==source_snapshot(proof),'qualification_source_changed'
    path=proof/('results.json' if args.all else 'retained-results.json')
    path.write_text(json.dumps(dict(status='passed',steps=q.results,source=captured,logs=qualification_logs(proof),retained_state_sha256=sha256((proof/'retained-state.json').read_bytes()).hexdigest()),indent=2)+'\n')
    print(json.dumps(dict(ok=True,steps=q.results)))


if __name__=='__main__':
    try:main()
    except Exception as error:
        storage.report_failure(error)
        raise SystemExit(1) from None
