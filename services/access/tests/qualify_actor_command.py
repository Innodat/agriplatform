"""Actual restricted-login command proof on the existing private synthetic frame."""
import json
from hashlib import sha256
import time
from queue import Queue
from contextlib import contextmanager
from sqlalchemy import event
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import uuid
from urllib.parse import urlsplit

sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from qualify_operator_authority import AuthorityQualification, PREVIOUS_FILES as HEAD4_FILES, report_failure
from qualify_identity_baseline import baseline, engine, fixture, text
import identity_operator as operator

PREVIOUS_COMMIT='8472909ed59e7aa90f4784e50c2e1e717e68977e'
PREVIOUS_FILES=HEAD4_FILES | {'versions/0005_operator_authority.py','authority-reference.json'}
REQUIRED_CASES=frozenset({'command_reference','clean','legacy','previous','failure','unsafe','unknown','native'})


def document(**overrides):
    value=dict(schema_version=1,operation_id=str(uuid.uuid4()),command='actor.register_system',
       scope={'kind':'platform'},reason_code='synthetic_fixture',
       payload=dict(actor_id=str(uuid.uuid4()),kind='service',actor_key='synthetic:'+uuid.uuid4().hex,
                    display_name='Synthetic é\n\t\x0f🙂',expected_absent=True))
    value.update(overrides)
    return value


def encode(value):return json.dumps(value,ensure_ascii=False).encode()


class CommandQualification(AuthorityQualification):
    def validate_operator_urls(self, required_cases=REQUIRED_CASES):
        for group,login in [('operator_urls','identity_operator'),('owner_urls','identity_migrator'),('databases','postgres'),('runtime_urls','access_runtime')]:
            assert set(self.private.get(group,{}))==required_cases,'command_url_group_invalid'
            for case,url in self.private[group].items():
                parsed=urlsplit(url);owner=urlsplit(self.private['owner_urls'][case])
                assert parsed.scheme=='postgresql' and parsed.username==login,'command_login_invalid'
                assert (parsed.hostname,parsed.port,parsed.path,parsed.query,parsed.fragment)==(owner.hostname,owner.port,owner.path,'',''),'command_target_invalid'

    def snapshot(self,case):
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:return baseline.command_catalog_snapshot(c)
        finally:db.dispose()

    def invoke(self,value,case='clean',lookup=False,url=None):
        db=engine(url or self.private['operator_urls'][case])
        try:
            with db.connect() as c:
                login=urlsplit(url or self.private['operator_urls'][case]).username
                assert c.execute(text('SELECT session_user,current_user')).one()==(login,login)
                c.commit()
                return operator.outcome(c,value['operation_id']) if lookup else operator.execute(c,encode(value))
        finally:db.dispose()

    def deny(self,value,code='access_denied',lookup=False):
        before=self.data_state('clean')
        try:self.invoke(value,lookup=lookup)
        except operator.OperatorError as error:
            assert error.code==code,'command_wrong_safe_code'
            assert error.__context__ is None,'command_unsafe_exception_chain'
        else:raise AssertionError('command_unexpected_success')
        assert self.data_state('clean')==before,'command_failed_partial_effects'

    def waiting_invocation(self,value,url,ready,start,lookup=False):
        db=engine(url)
        try:
            with db.connect() as c:
                login=urlsplit(url).username
                pid,original,current=c.execute(text('SELECT pg_backend_pid(),session_user,current_user')).one()
                assert (original,current)==(login,login)
                c.commit();ready.put(pid)
                assert start.wait(timeout=2),'worker_start_not_released'
                try:return operator.outcome(c,value['operation_id']) if lookup else operator.execute(c,encode(value))
                except operator.OperatorError as error:return error.code
        finally:db.dispose()

    def witness_waiters(self,observer,pids,blocker,futures):
        deadline=time.monotonic()+1
        while time.monotonic()<deadline:
            observer.execute(text('SELECT pg_stat_clear_snapshot()'))
            count=observer.execute(text("""SELECT count(*) FROM unnest(CAST(:pids AS integer[])) expected(pid)
                JOIN pg_stat_activity a ON a.pid=expected.pid
                WHERE a.datname=current_database() AND a.usename IN ('identity_operator','access_runtime')
                AND :blocker=ANY(pg_blocking_pids(expected.pid))
                AND EXISTS(SELECT 1 FROM pg_locks l WHERE l.pid=expected.pid AND l.locktype='advisory' AND NOT l.granted)"""),
                {'pids':pids,'blocker':blocker}).scalar_one()
            if count==len(pids):return
            assert not any(future.done() for future in futures),'invocation_completed_before_lock_witness'
        raise AssertionError('actual_waiters_not_witnessed')

    def locked_race(self,first,second,urls,key):
        owner=engine(self.private['owner_urls']['clean']);ready=Queue();start=Event()
        try:
            with ThreadPoolExecutor(max_workers=2) as workers:
                with owner.begin() as c:
                    blocker=c.execute(text('SELECT pg_backend_pid()')).scalar_one()
                    c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
                    pending=[workers.submit(self.waiting_invocation,value,url,ready,start)
                             for value,url in zip([first,second],urls)]
                    try:
                        pids=[ready.get(timeout=1),ready.get(timeout=1)]
                        assert pids[0]!=pids[1],'race_reused_backend'
                        start.set();self.witness_waiters(c,pids,blocker,pending)
                    finally:start.set()
                return [future.result() for future in pending]
        finally:owner.dispose()

    @contextmanager
    def second_executor(self):
        """Temporary exact wrapper access on an existing synthetic LOGIN only."""
        signatures=['identity.register_system(uuid,uuid,text,text,text,text,text,bytea)',
                    'identity.system_actor_outcome(uuid)']
        acl_sql="SELECT p.oid::regprocedure::text,coalesce(p.proacl::text,'') FROM pg_proc p WHERE p.oid IN (to_regprocedure(:registration),to_regprocedure(:lookup)) ORDER BY 1"
        params={'registration':signatures[0],'lookup':signatures[1]}
        before=self.sql('clean',acl_sql,params)
        schema_before=self.sql('clean',"SELECT coalesce(nspacl::text,''),has_schema_privilege('access_runtime',oid,'USAGE') FROM pg_namespace WHERE nspname='identity'")[0]
        for signature in signatures:
            assert self.sql('clean',"SELECT has_function_privilege('access_runtime',:signature,'EXECUTE')",{'signature':signature})==[(False,)],'runtime_wrapper_access_preexisted'
        executor=str(uuid.uuid4());authority=str(uuid.uuid4())
        self.sql('clean',"INSERT INTO identity.actor(id,kind,display_name,created_by,updated_by) VALUES (:id,'service','Synthetic second command executor',:id,:id)",{'id':executor})
        self.sql('clean',"INSERT INTO identity.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by) VALUES ('access_runtime',:actor,true,:actor,:actor)",{'actor':executor})
        self.authority(executor,'actor.register_system',identifier=authority,database_login='access_runtime')
        owner=engine(self.private['owner_urls']['clean'])
        try:
            with owner.begin() as c:
                if not schema_before[1]:c.execute(text('GRANT USAGE ON SCHEMA identity TO access_runtime'))
                c.execute(text('SET LOCAL ROLE identity_command_owner'))
                c.execute(text('GRANT EXECUTE ON FUNCTION '+','.join(signatures)+' TO access_runtime'))
                c.execute(text('RESET ROLE'))
            yield executor,self.private['runtime_urls']['clean']
        finally:
            with owner.begin() as c:
                c.execute(text('SET LOCAL ROLE identity_command_owner'))
                c.execute(text('REVOKE EXECUTE ON FUNCTION '+','.join(signatures)+' FROM access_runtime'))
                c.execute(text('RESET ROLE'))
                if not schema_before[1]:c.execute(text('REVOKE USAGE ON SCHEMA identity FROM access_runtime'))
                c.execute(text("UPDATE identity.operator_authorities SET enabled=false WHERE id=:id"),{'id':authority})
                c.execute(text("UPDATE identity.operator_principals SET enabled=false WHERE database_login='access_runtime'"))
            owner.dispose()
            assert self.sql('clean',acl_sql,params)==before,'runtime_function_acl_not_restored'
            assert self.sql('clean',"SELECT coalesce(nspacl::text,''),has_schema_privilege('access_runtime',oid,'USAGE') FROM pg_namespace WHERE nspname='identity'")[0]==schema_before,'runtime_schema_acl_not_restored'

    def two_executor_matrix(self,actor):
        original=self.private['operator_urls']['clean']
        with self.second_executor() as (other_actor,runtime):
            same=document();same_id=same['operation_id']
            other=document(operation_id=same_id)
            # A held executor-A outcome lock cannot block executor B's same UUID.
            owner=engine(self.private['owner_urls']['clean']);ready=Queue();start=Event()
            try:
                with ThreadPoolExecutor(max_workers=1) as workers:
                    with owner.begin() as c:
                        blocker=c.execute(text('SELECT pg_backend_pid()')).scalar_one()
                        c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':operator.outcome_lock_key(actor,same_id)})
                        pending=workers.submit(self.waiting_invocation,same,original,ready,start)
                        try:
                            pid=ready.get(timeout=1);start.set();self.witness_waiters(c,[pid],blocker,[pending])
                            other_receipt=self.invoke(other,url=runtime)
                        finally:start.set()
                    first_receipt=pending.result()
            finally:owner.dispose()
            assert first_receipt.result.target.actor_id!=other_receipt.result.target.actor_id
            assert self.invoke(same,lookup=True)==first_receipt
            assert self.invoke(other,lookup=True,url=runtime)==other_receipt
            only_other=document();self.invoke(only_other,url=runtime)
            assert self.invoke(only_other,lookup=True) is None
            only_original=document();self.invoke(only_original)
            assert self.invoke(only_original,lookup=True,url=runtime) is None
            assert self.sql('clean','SELECT count(DISTINCT executor_actor_id) FROM identity.operation_outcome WHERE operation_id=:operation',{'operation':same_id})==[(2,)]
            assert self.sql('clean','SELECT executor_actor_id::text FROM identity.operation_outcome WHERE operation_id=:operation ORDER BY executor_actor_id',{'operation':same_id})==[(identifier,) for identifier in sorted([actor,other_actor])]
            same=document()
            results=self.locked_race(same,same,[original,original],operator.outcome_lock_key(actor,same['operation_id']))
            assert results[0]==results[1] and results[0].result.disposition=='created'
            assert self.sql('clean','SELECT count(*) FROM identity.operation_outcome WHERE operation_id=:operation',{'operation':same['operation_id']})==[(1,)]
            assert self.sql('clean','SELECT count(*) FROM identity.business_event WHERE target_key=:target',{'target':same['payload']['actor_id']})==[(1,)]
            for shape in ['same-target','shared-key','shared-id']:
                first=document();second={**first,'operation_id':str(uuid.uuid4()),'payload':dict(first['payload'])}
                if shape=='shared-key':second['payload']['actor_id']=str(uuid.uuid4())
                if shape=='shared-id':second['payload']['actor_key']='synthetic:'+uuid.uuid4().hex
                domain=('identity:actor-key:v1:'+first['payload']['actor_key'] if shape=='shared-key'
                        else 'identity:actor-id:v1:'+first['payload']['actor_id'])
                key=int.from_bytes(sha256(domain.encode()).digest()[:8],'big',signed=True)
                results=self.locked_race(first,second,[original,runtime],key)
                dispositions=sorted(result if isinstance(result,str) else result.result.disposition for result in results)
                assert dispositions==(['created','unchanged'] if shape=='same-target' else ['created','operation_conflict'])
                assert self.sql('clean','SELECT count(*) FROM identity.actor WHERE id IN (:first,:second)',
                    {'first':first['payload']['actor_id'],'second':second['payload']['actor_id']})==[(1,)]
                assert self.sql('clean','SELECT count(*) FROM identity.business_event WHERE target_key IN (:first,:second)',
                    {'first':first['payload']['actor_id'],'second':second['payload']['actor_id']})==[(1,)]
                assert self.sql('clean','SELECT count(*) FROM identity.operation_outcome WHERE operation_id IN (:first,:second)',
                    {'first':first['operation_id'],'second':second['operation_id']})==[(2 if shape=='same-target' else 1,)]
        self.passed('actor-command-two-executor-forced-races',existing_login_only=True,scoped_same_uuid=True,independent_outcome_locks=True,foreign_lookup_unresolved=True,
                    both_waiters_and_blocker=True,same_operation_once=True,distinct_operations_same_target=True,shared_key=True,shared_id=True,exact_grants_restored=True)

    def fingerprint_and_audit_fixtures(self):
        labels=['Quotes " and backslash \\', 'Controls \b\t\n\f\r\x01\x0b\x1f',
                'Separators \u2028\u2029', 'Supplementary 🙂 𐐷', 'Non-normalized e\u0301 Å\u030a']
        for label in labels:
            value=document(reason_code='setup_correction',evidence_ref='synthetic:actor/jcs-fixture')
            value['payload']['display_name']=label
            receipt=self.invoke(value)
            canonical=operator.canonical_command(operator.parse_command(encode(value)))
            assert self.sql('clean','SELECT fingerprint FROM identity.operation_outcome WHERE operation_id=:operation',{'operation':value['operation_id']})==[(sha256(canonical).digest(),)]
            assert self.sql('clean','SELECT reason_code,evidence_ref FROM identity.business_event WHERE event_id=:event',{'event':receipt.result.event_id})==[('setup_correction','synthetic:actor/jcs-fixture')]
            assert self.invoke(value)==receipt
        self.passed('actor-command-server-jcs-and-audit-fixtures',quotes_backslashes_controls=True,separators_supplementary_non_normalized=True,server_digest_equals_approved_python=True,exact_reason_evidence=True)

    def command_matrix(self):
        value=document()
        self.deny(value);self.deny(value,lookup=True)
        actor=self.authority_fixture();authority=self.authority(actor,'actor.register_system')
        receipt=self.invoke(value)
        assert receipt.result.disposition=='created' and receipt.result.event_id is not None and receipt.result.revision is None
        assert self.invoke(value)==receipt and self.invoke(value,lookup=True)==receipt
        assert self.sql('clean','SELECT created_by::text,updated_by::text,created_at=updated_at FROM identity.actor WHERE id=:id',{'id':value['payload']['actor_id']})==[(actor,actor,True)]
        assert self.sql('clean','SELECT count(*) FROM identity.operation_outcome')==[(1,)]
        assert self.sql('clean','SELECT count(*) FROM identity.business_event')==[(1,)]
        changed=json.loads(json.dumps(value));changed['payload']['display_name']='Changed'
        self.deny(changed,'operation_conflict')
        unchanged={**value,'operation_id':str(uuid.uuid4())}
        assert self.invoke(unchanged).result.disposition=='unchanged'
        assert self.sql('clean','SELECT count(*) FROM identity.business_event')==[(1,)]
        for key,replacement in [('actor_id',str(uuid.uuid4())),('kind','system'),('actor_key','synthetic:changed'),('display_name','Different')]:
            conflicting={**value,'operation_id':str(uuid.uuid4()),'payload':{**value['payload'],key:replacement}}
            self.deny(conflicting,'operation_conflict')
        # A later controlled owner edit never rewrites the original receipt.
        self.sql('clean','UPDATE identity.actor SET display_name=:name,updated_by=:actor WHERE id=:id',{'name':'Later controlled label','actor':actor,'id':value['payload']['actor_id']})
        assert self.invoke(value)==receipt and self.invoke(value,lookup=True)==receipt
        for table,where,args in [('operator_principals',"database_login='identity_operator'",{}),('operator_authorities','id=:id',{'id':authority})]:
            self.sql('clean','UPDATE identity.'+table+' SET enabled=false WHERE '+where,args)
            self.deny(value);self.deny(value,lookup=True)
            self.sql('clean','UPDATE identity.'+table+' SET enabled=true WHERE '+where,args)
        # A live mapped principal with another exact command has no registration
        # authority and cannot recover the existing registration receipt.
        self.authority(actor,'account_actor.ensure')
        self.sql('clean','UPDATE identity.operator_authorities SET enabled=false WHERE id=:id',{'id':authority})
        try:self.deny(value);self.deny(value,lookup=True)
        finally:self.sql('clean','UPDATE identity.operator_authorities SET enabled=true WHERE id=:id',{'id':authority})
        assert self.invoke(value,lookup=True)==receipt
        assert self.invoke(document(),lookup=True) is None
        system=document();system['payload']['kind']='system'
        system['operation_id']=system['operation_id'].upper();system['payload']['actor_id']=system['payload']['actor_id'].upper()
        system_receipt=self.invoke(system)
        assert system_receipt.result.disposition=='created' and system_receipt.result.target.actor_id==system['payload']['actor_id'].lower()
        assert self.invoke({**system,'operation_id':system['operation_id'].lower(),
            'payload':{**system['payload'],'actor_id':system['payload']['actor_id'].lower()}})==system_receipt
        self.two_executor_matrix(actor)
        self.fingerprint_and_audit_fixtures()
        self.passed('actor-command-registration-replay-recovery',actual_login=True,server_attribution=True,unicode_controls=True,no_op=True,conflicts=True,original_receipt=True,concurrent=True,current_authority=True)
        self.isolation_and_forgery(actor,value,receipt)
        self.timeouts_and_atomicity(actor)
        self.structural_evidence(actor,value)
        self.authority_serialization(actor,authority,value)
        self.failure_connection_reuse(actor,value,receipt)
        self.lost_acknowledgement()

    def isolation_and_forgery(self,actor,value,receipt):
        db=engine(self.private['operator_urls']['clean'])
        try:
            with db.connect() as c:
                # Busy work belongs to the caller and remains untouched.
                c.execute(text('SELECT 1'))
                try:operator.execute(c,encode(document()))
                except operator.OperatorError as error:assert error.code=='connection_busy' and c.in_transaction()
                else:raise AssertionError('busy_connection_accepted')
                c.rollback()
                # Commit/rollback removes every transaction-local timeout/context.
                defaults=c.execute(text("SELECT current_setting('statement_timeout'),current_setting('lock_timeout')")).one();c.commit()
                assert operator.outcome(c,value['operation_id'])==receipt
                assert c.execute(text("SELECT current_setting('statement_timeout'),current_setting('lock_timeout')")).one()==defaults;c.commit()
                with c.begin():
                    c.execute(text("SELECT set_config('app.actor_id',:actor,true)"),{'actor':str(uuid.uuid4())})
                    c.execute(text('SET LOCAL search_path=pg_temp,public,identity'))
                    c.execute(text('CREATE TEMP TABLE operation_outcome(result jsonb); CREATE TEMP TABLE actor(id uuid)'))
                    assert c.execute(text('SELECT * FROM identity.system_actor_outcome(CAST(:operation AS uuid))'),{'operation':value['operation_id']}).one()[0]['target']['actor_id']==value['payload']['actor_id']
                forbidden=['SELECT * FROM identity.actor','SELECT * FROM identity.operation_outcome','SELECT * FROM identity.business_event',
                    'INSERT INTO identity.actor DEFAULT VALUES','UPDATE identity.operation_outcome SET result=\'{}\'','DELETE FROM identity.business_event',
                    'TRUNCATE identity.operation_outcome,identity.business_event','SET ROLE identity_command_owner','SET ROLE identity_migrator',
                    'ALTER TABLE identity.operation_outcome ADD COLUMN forbidden text']
                for sql in forbidden:
                    with c.begin():
                        sp=c.begin_nested()
                        try:c.execute(text(sql))
                        except Exception as error:assert error.orig.sqlstate=='42501'
                        else:raise AssertionError('operator_excess_authority')
                        finally:sp.rollback()
                p=value['payload']
                with c.begin():
                    sp=c.begin_nested()
                    try:c.execute(text('SELECT * FROM identity.register_system(CAST(:op AS uuid),CAST(:id AS uuid),:kind,:key,:label,:reason,NULL,:canonical)'),
                      dict(op=str(uuid.uuid4()),id=p['actor_id'],kind=p['kind'],key=p['actor_key'],label=p['display_name'],reason='synthetic_fixture',canonical=b'forged digest'))
                    except Exception as error:assert error.orig.sqlstate=='IC005'
                    else:raise AssertionError('forged_canonical_accepted')
                    finally:sp.rollback()
            serial=db.connect().execution_options(isolation_level='SERIALIZABLE')
            try:
                try:operator.execute(serial,encode(document()))
                except operator.OperatorError as error:assert error.code=='isolation_unsupported'
                else:raise AssertionError('isolation_accepted')
            finally:serial.close()
            automatic=db.connect().execution_options(isolation_level='AUTOCOMMIT')
            try:
                before=self.data_state('clean')
                try:operator.execute(automatic,encode(document()))
                except operator.OperatorError as error:assert error.code=='isolation_unsupported' and not automatic.in_transaction()
                else:raise AssertionError('autocommit_accepted')
                assert self.data_state('clean')==before
            finally:automatic.close()
        finally:db.dispose()
        owner=engine(self.private['owner_urls']['clean'])
        try:
            with owner.begin() as c:
                c.execute(text('SET LOCAL ROLE identity_command_owner'))
                try:c.execute(text('SELECT * FROM identity.system_actor_outcome(CAST(:operation AS uuid))'),{'operation':value['operation_id']})
                except Exception as error:assert error.orig.sqlstate=='IC002'
                else:raise AssertionError('set_role_forged_login')
        finally:owner.dispose()
        self.passed('actor-command-privilege-isolation',raw_reads_writes_ddl_denied=True,canonical_forgery=True,guc_search_path=True,set_role=True,pool_reuse=True)

    def timeouts_and_atomicity(self,actor):
        # Hold real transaction locks while a separate LOGIN invokes the adapter.
        owner=engine(self.private['owner_urls']['clean'])
        try:
            for kind in ['outcome','domain','authority']:
                value=document()
                key=(operator.outcome_lock_key(actor,value['operation_id']) if kind=='outcome' else
                     int.from_bytes(__import__('hashlib').sha256(('identity:actor-id:v1:'+value['payload']['actor_id'] if kind=='domain' else 'identity:operator-authority:v1:identity_operator').encode()).digest()[:8],'big',signed=True))
                with owner.begin() as c:
                    c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
                    self.deny(value,'operation_busy' if kind=='outcome' else 'operation_unavailable')
                assert self.invoke(value).result.disposition=='created'
            for table in ['operation_outcome','business_event']:
                self.sql('clean',"CREATE FUNCTION identity.synthetic_command_failure() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_failure'; END $$; CREATE TRIGGER synthetic_command_failure BEFORE INSERT ON identity."+table+' FOR EACH ROW EXECUTE FUNCTION identity.synthetic_command_failure()')
                try:self.deny(document(),'operation_unavailable')
                finally:self.sql('clean','DROP TRIGGER synthetic_command_failure ON identity.'+table+'; DROP FUNCTION identity.synthetic_command_failure()')
        finally:owner.dispose()
        self.passed('actor-command-bounded-waits-and-atomicity',exact_outcome_busy=True,domain_and_authority_unavailable=True,outcome_event_failure_rollback=True)

    def structural_evidence(self,actor,value):
        owner=self.admin('clean')
        try:
            with owner.connect() as c:
                t=c.begin()
                try:
                    for table in ['operation_outcome','business_event']:
                        for command in ['UPDATE identity.'+table+' SET executor_actor_id=executor_actor_id','DELETE FROM identity.'+table]:
                            sp=c.begin_nested()
                            try:c.execute(text(command))
                            except Exception as error:assert error.orig.sqlstate=='23514'
                            else:raise AssertionError('immutable_evidence_changed')
                            finally:sp.rollback()
                    sp=c.begin_nested()
                    try:c.execute(text('TRUNCATE identity.operation_outcome,identity.business_event'))
                    except Exception as error:assert error.orig.sqlstate=='23514'
                    else:raise AssertionError('immutable_evidence_truncated')
                    finally:sp.rollback()
                    # Unsupported stored versions survive and fail closed, including lookup.
                    c.execute(text('ALTER TABLE identity.operation_outcome DISABLE TRIGGER operation_outcome_guard'))
                    c.execute(text('UPDATE identity.operation_outcome SET fingerprint_version=2 WHERE operation_id=:op'),{'op':value['operation_id']})
                    c.execute(text('ALTER TABLE identity.operation_outcome ENABLE TRIGGER operation_outcome_guard'))
                    t.commit()
                    self.deny(value,'operation_verification_unavailable');self.deny(value,'operation_verification_unavailable',lookup=True)
                finally:
                    if t.is_active:t.rollback()
            # Controlled qualification restores only its synthetic supported marker.
            with owner.begin() as c:
                c.execute(text('ALTER TABLE identity.operation_outcome DISABLE TRIGGER operation_outcome_guard'))
                c.execute(text('UPDATE identity.operation_outcome SET fingerprint_version=1 WHERE operation_id=:op'),{'op':value['operation_id']})
                c.execute(text('ALTER TABLE identity.operation_outcome ENABLE TRIGGER operation_outcome_guard'))
        finally:owner.dispose()
        self.passed('actor-command-immutable-unsupported-evidence',retained=True,verification_unavailable=True)
        # Controlled temporary privilege injection exercises guards under the actual
        # mapped original login even if someone accidentally granted owner assumption.
        admin=self.admin('clean');db=engine(self.private['operator_urls']['clean'])
        try:
            with admin.begin() as c:c.execute(text('GRANT identity_command_owner TO identity_operator'))
            with db.connect() as c:
                t=c.begin()
                try:
                    c.execute(text('SET LOCAL ROLE identity_command_owner'))
                    outcome=c.execute(text('SELECT to_jsonb(o) FROM identity.operation_outcome o ORDER BY committed_at LIMIT 1')).scalar_one()
                    event=c.execute(text('SELECT to_jsonb(e) FROM identity.business_event e ORDER BY created_at LIMIT 1')).scalar_one()
                    def reject_insert(table,row,expected,deferred=False):
                        sp=c.begin_nested()
                        try:
                            c.execute(text('INSERT INTO identity.'+table+' SELECT (jsonb_populate_record(NULL::identity.'+table+',CAST(:row AS jsonb))).*'),{'row':json.dumps(row)})
                            if deferred:c.execute(text('SET CONSTRAINTS ALL IMMEDIATE'))
                        except Exception as error:assert error.orig.sqlstate==expected,'alternate_evidence_wrong_refusal'
                        else:raise AssertionError('alternate_evidence_accepted')
                        finally:sp.rollback()
                    base={**outcome,'id':str(uuid.uuid4()),'operation_id':str(uuid.uuid4())}
                    reject_insert('operation_outcome',{**base,'executor_actor_id':str(uuid.uuid4())},'42501')
                    reject_insert('operation_outcome',{**base,'initiator_actor_id':str(uuid.uuid4())},'23514')
                    # FORCE RLS rejects this non-platform scope before the table
                    # CHECK runs. Prove that CHECK independently below as admin.
                    reject_insert('operation_outcome',{**base,'scope_id':str(uuid.uuid4())},'42501')
                    reject_insert('operation_outcome',{**base,'fingerprint':'\\x00'},'23514')
                    reject_insert('operation_outcome',{**base,'fingerprint_algorithm':'hmac-sha256','fingerprint_key_id':None},'23514')
                    reject_insert('operation_outcome',{**base,'result':{**outcome['result'],'unexpected':'forbidden'}},'23514')
                    reject_insert('operation_outcome',{**base,'result':{**outcome['result'],'event_id':str(uuid.uuid4())}},'23514',deferred=True)
                    # Each event starts with a fresh valid outcome and its exact
                    # reserved event ID. Change only the field under test, and
                    # require refusal during INSERT itself: a deferred missing-event
                    # check cannot stand in for the individual linkage guards.
                    for changes in [None,dict(event_id=str(uuid.uuid4())),dict(outcome_id=str(uuid.uuid4())),
                                    dict(target_key=str(uuid.uuid4())),dict(target={'actor_id':str(uuid.uuid4())}),
                                    dict(transition={'display_name':'forbidden'}),dict(executor_actor_id=str(uuid.uuid4()))]:
                        sp=c.begin_nested()
                        try:
                            reserved_event=str(uuid.uuid4());reserved_outcome=str(uuid.uuid4())
                            fresh_outcome={**outcome,'id':reserved_outcome,'operation_id':str(uuid.uuid4()),
                                'result':{**outcome['result'],'disposition':'created','event_id':reserved_event}}
                            c.execute(text('INSERT INTO identity.operation_outcome SELECT (jsonb_populate_record(NULL::identity.operation_outcome,CAST(:row AS jsonb))).*'),{'row':json.dumps(fresh_outcome)})
                            fresh_event={**event,'event_id':reserved_event,'outcome_id':reserved_outcome}
                            if changes is None:
                                # The unchanged control pair proves the setup is valid.
                                c.execute(text('INSERT INTO identity.business_event SELECT (jsonb_populate_record(NULL::identity.business_event,CAST(:row AS jsonb))).*'),{'row':json.dumps(fresh_event)})
                                c.execute(text('SET CONSTRAINTS ALL IMMEDIATE'))
                            else:
                                try:
                                    c.execute(text('INSERT INTO identity.business_event SELECT (jsonb_populate_record(NULL::identity.business_event,CAST(:row AS jsonb))).*'),{'row':json.dumps({**fresh_event,**changes})})
                                except Exception as error:
                                    assert error.orig.sqlstate==('42501' if 'executor_actor_id' in changes else '23514'),'isolated_event_field_wrong_refusal'
                                else:raise AssertionError('isolated_event_field_accepted')
                        finally:sp.rollback()
                finally:t.rollback()
        finally:
            with admin.begin() as c:c.execute(text('REVOKE identity_command_owner FROM identity_operator'))
            db.dispose();admin.dispose()
        # Each unsupported supported-storage marker is retained rather than missing.
        for column,new_value,old_value in [('command_version',2,1),('result_version',2,1),
                ('fingerprint_algorithm','hmac-sha256','sha256')]:
            extra=",fingerprint_key_id='synthetic:key'" if column=='fingerprint_algorithm' else ''
            admin=self.admin('clean')
            with admin.begin() as c:
                c.execute(text('ALTER TABLE identity.operation_outcome DISABLE TRIGGER operation_outcome_guard'))
                c.execute(text('UPDATE identity.operation_outcome SET '+column+'=:version'+extra+' WHERE operation_id=:op'),{'version':new_value,'op':value['operation_id']})
                c.execute(text('ALTER TABLE identity.operation_outcome ENABLE TRIGGER operation_outcome_guard'))
            try:
                self.deny(value,'operation_verification_unavailable');self.deny(value,'operation_verification_unavailable',lookup=True)
            finally:
                with admin.begin() as c:
                    c.execute(text('ALTER TABLE identity.operation_outcome DISABLE TRIGGER operation_outcome_guard'))
                    c.execute(text('UPDATE identity.operation_outcome SET '+column+'=:version'+(',fingerprint_key_id=NULL' if extra else '')+' WHERE operation_id=:op'),{'version':old_value,'op':value['operation_id']})
                    c.execute(text('ALTER TABLE identity.operation_outcome ENABLE TRIGGER operation_outcome_guard'))
                admin.dispose()
        self.passed('actor-command-alternate-evidence-linkage',wrong_executor_target_outcome_rejected=True,strict_result=True,missing_event=True,all_version_algorithm_markers=True)
        # Isolate physical FK enforcement from earlier guard/RLS refusals. Only
        # controlled synthetic admin transactions disable the INSERT guards; the
        # entire transaction rolls back, including that temporary trigger state.
        admin=self.admin('clean')
        try:
            with admin.connect() as c:
                transaction=c.begin()
                try:
                    outcome=c.execute(text('SELECT to_jsonb(o) FROM identity.operation_outcome o ORDER BY committed_at LIMIT 1')).scalar_one()
                    event=c.execute(text('SELECT to_jsonb(e) FROM identity.business_event e ORDER BY created_at LIMIT 1')).scalar_one()
                    c.execute(text('ALTER TABLE identity.operation_outcome DISABLE TRIGGER operation_outcome_guard'))
                    c.execute(text('ALTER TABLE identity.business_event DISABLE TRIGGER business_event_guard'))
                    def constraint_refusal(table,row,expected='23503'):
                        sp=c.begin_nested()
                        try:c.execute(text('INSERT INTO identity.'+table+' SELECT (jsonb_populate_record(NULL::identity.'+table+',CAST(:row AS jsonb))).*'),{'row':json.dumps(row)})
                        except Exception as error:assert error.orig.sqlstate==expected,'physical_constraint_not_enforced'
                        else:raise AssertionError('physical_constraint_accepted')
                        finally:sp.rollback()
                    base={**outcome,'id':str(uuid.uuid4()),'operation_id':str(uuid.uuid4()),
                        'result':{**outcome['result'],'disposition':'unchanged','event_id':None}}
                    constraint_refusal('operation_outcome',{**base,'scope_id':str(uuid.uuid4())},'23514')
                    constraint_refusal('operation_outcome',{**base,'executor_actor_id':str(uuid.uuid4())})
                    constraint_refusal('business_event',{**event,'event_id':str(uuid.uuid4()),'outcome_id':str(uuid.uuid4())})
                    # Use a distinct transition identity so its existing unique
                    # key cannot mask the missing-executor FK with 23505.
                    constraint_refusal('business_event',{**event,'event_id':str(uuid.uuid4()),
                        'target_key':str(uuid.uuid4()),'executor_actor_id':str(uuid.uuid4())})
                finally:transaction.rollback()
        finally:admin.dispose()
        self.passed('actor-command-physical-foreign-keys',actual_23503=True,scope_check_23514=True,missing_outcome=True,missing_outcome_executor=True,missing_event_executor=True,controlled_fixture_rolled_back=True)

    def authority_serialization(self,actor,authority,committed):
        owner=engine(self.private['owner_urls']['clean'])
        try:
            for table,where,args in [('operator_principals',"database_login='identity_operator'",{}),
                                     ('operator_authorities','id=:id',{'id':authority})]:
                for mode in ['new','replay','lookup']:
                    value=document() if mode=='new' else committed
                    before=self.data_state('clean')
                    try:
                        with ThreadPoolExecutor(max_workers=1) as workers:
                            with owner.begin() as c:
                                c.execute(text('UPDATE identity.'+table+' SET enabled=false WHERE '+where),args)
                                blocker=c.execute(text('SELECT pg_backend_pid()')).scalar_one()
                                ready=Queue();start=Event()
                                pending=workers.submit(self.waiting_invocation,value,self.private['operator_urls']['clean'],ready,start,mode=='lookup')
                                try:
                                    pid=ready.get(timeout=1);start.set()
                                    self.witness_waiters(c,[pid],blocker,[pending])
                                finally:start.set()
                            assert pending.result()=='access_denied','revoked_inflight_command_disclosed'
                    finally:self.sql('clean','UPDATE identity.'+table+' SET enabled=true WHERE '+where,args)
                    after=self.data_state('clean')
                    assert all(after[key]==data for key,data in before.items() if key not in ('operator_principals','operator_authorities')),'revocation_race_changed_evidence'
        finally:owner.dispose()
        self.passed('actor-command-authority-configuration-serialization',principal=True,authority=True,new_execution=True,replay=True,lookup=True,fresh_postlock_recheck=True)

    def failure_connection_reuse(self,actor,committed,receipt):
        db=engine(self.private['operator_urls']['clean']);owner=engine(self.private['owner_urls']['clean'])
        timeout_states=[]
        def observe_error(context):
            # Capture only the machine code, never statement/parameters/errors.
            if getattr(context.original_exception,'sqlstate',None)=='57014':timeout_states.append('57014')
        event.listen(db,'handle_error',observe_error)
        identity_sql="SELECT pg_backend_pid(),session_user,current_user,current_setting('statement_timeout'),current_setting('lock_timeout')"
        try:
            with db.connect() as c:
                original=c.execute(text(identity_sql)).one();c.commit()
                assert original[1:3]==('identity_operator','identity_operator')
                def healthy():
                    assert not c.in_transaction(),'failed_command_left_transaction'
                    assert c.execute(text(identity_sql)).one()==original,'failed_command_leaked_identity_or_settings'
                    assert c.execute(text('SELECT 1')).scalar_one()==1;c.commit()
                    assert operator.outcome(c,committed['operation_id'])==receipt
                    assert c.execute(text(identity_sql)).one()==original;c.commit()
                def failed(value,expected):
                    before=self.data_state('clean')
                    try:operator.execute(c,encode(value))
                    except operator.OperatorError as error:
                        assert error.code==expected and error.operation_id==value['operation_id']
                        assert error.__context__ is None
                    else:raise AssertionError('reuse_fixture_unexpected_success')
                    assert self.data_state('clean')==before,'failed_reused_command_partial_effects'
                    healthy()
                changed={**committed,'payload':{**committed['payload'],'display_name':'Conflicting reuse label'}}
                failed(changed,'operation_conflict')
                blocked=document()
                with owner.begin() as holder:
                    holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':operator.outcome_lock_key(actor,blocked['operation_id'])})
                    failed(blocked,'operation_busy')
                for mode in ['failure','slow']:
                    name='synthetic_command_reuse_'+mode
                    body=("RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_failure';" if mode=='failure'
                          else 'PERFORM pg_catalog.pg_sleep(6); RETURN NEW;')
                    self.sql('clean','CREATE FUNCTION identity.'+name+'() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN '+body+' END $$; CREATE TRIGGER '+name+' BEFORE INSERT ON identity.business_event FOR EACH ROW EXECUTE FUNCTION identity.'+name+'()')
                    try:failed(document(),'operation_unavailable')
                    finally:self.sql('clean','DROP TRIGGER '+name+' ON identity.business_event; DROP FUNCTION identity.'+name+'()')
                assert timeout_states==['57014'],'actual_statement_timeout_not_observed'
                healthy()
        finally:
            event.remove(db,'handle_error',observe_error);db.dispose();owner.dispose()
        self.passed('actor-command-actual-timeout-and-failure-connection-reuse',actual_sqlstate_57014_only=True,slow_trigger_atomic_rollback=True,
                    same_backend_after_conflict_lock_and_event_failure=True,defaults_identity_select_and_recovery=True)

    def lost_acknowledgement(self):
        # Actual PostgreSQL commits, then the transport surface loses its response.
        # No mocked command effects or migrator-role command success is substituted.
        db=engine(self.private['operator_urls']['clean']);value=document()
        class LostCommit:
            def __init__(self,transaction):self.transaction=transaction
            def __enter__(self):return self.transaction.__enter__()
            def __exit__(self,*args):
                result=self.transaction.__exit__(*args)
                if args[0] is None:raise ConnectionError('synthetic lost commit acknowledgement')
                return result
        class LostConnection:
            def __init__(self,connection):self.connection=connection
            def __getattr__(self,name):return getattr(self.connection,name)
            def begin(self):return LostCommit(self.connection.begin())
        try:
            with db.connect() as c:
                try:operator.execute(LostConnection(c),encode(value))
                except operator.OperatorError as error:
                    assert error.code=='operation_unavailable' and error.operation_id==value['operation_id']
                    assert error.__context__ is None
                else:raise AssertionError('lost_acknowledgement_reported_success')
            receipt=self.invoke(value,lookup=True)
            assert receipt is not None and self.invoke(value)==receipt
        finally:db.dispose()
        self.passed('actor-command-lost-commit-acknowledgement',actual_operator_commit=True,unknown_response=True,original_lookup_and_retry=True)

    def upgrades_and_failures(self):
        self.validate_operator_urls()
        self.prior_evidence(PREVIOUS_COMMIT,PREVIOUS_FILES,'identity_0005')
        self.command('command-clean','clean')
        assert self.sql('clean','SELECT count(*) FROM identity.actor')==[(0,)]
        self.command_matrix();self.command('command-repeat','clean')
        self.legacy('legacy');self.original_ledger('legacy');self.row_fixtures('legacy');self.row_fixtures('previous')
        for case in ['legacy','previous']:
            before,external=self.data_state(case),self.external_state(case)
            self.command('command-'+case,case,mode='adopt' if case=='legacy' else 'clean')
            after=self.data_state(case)
            assert all(after[key]==value for key,value in before.items() if key not in ('identity.alembic_version','org_member'))
            if case=='legacy':
                assert self.data_state(case,membership_without_revision=True)['org_member']==before['org_member']
            else:
                assert after['org_member']==before['org_member']
            assert self.external_state(case)==external
            self.command('command-'+case+'-repeat',case)
        self.sql('unknown',"UPDATE identity.alembic_version SET version_num='identity_unknown'")
        before=self.data_state('unknown');self.command('command-unknown-history','unknown',expected='identity_unknown_history');assert self.data_state('unknown')==before
        admin=self.admin('unsafe')
        try:
            with admin.begin() as c:c.execute(text('ALTER ROLE identity_command_owner LOGIN'))
            before=self.data_state('unsafe')
            try:self.command('command-unsafe-owner','unsafe',expected='identity_command_role_unsafe');assert self.data_state('unsafe')==before
            finally:
                with admin.begin() as c:c.execute(text('ALTER ROLE identity_command_owner NOLOGIN'))
        finally:admin.dispose()
        admin=self.admin('unsafe')
        try:
            with admin.begin() as c:
                database=c.execute(text('SELECT current_database()')).scalar_one()
                c.exec_driver_sql('GRANT CREATE ON DATABASE '+c.dialect.identifier_preparer.quote(database)+' TO PUBLIC')
            before=self.data_state('unsafe')
            try:self.command('command-public-database-create','unsafe',expected='identity_command_role_unsafe');assert self.data_state('unsafe')==before
            finally:
                with admin.begin() as c:c.exec_driver_sql('REVOKE CREATE ON DATABASE '+c.dialect.identifier_preparer.quote(database)+' FROM PUBLIC')
        finally:admin.dispose()
        # A controlled mid-revision failure must retain the prior catalog and state.
        admin=self.admin('failure')
        try:
            with admin.begin() as c:c.execute(text("CREATE FUNCTION public.synthetic_command_ddl_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN IF EXISTS(SELECT 1 FROM pg_event_trigger_ddl_commands() WHERE schema_name='identity' AND object_type='function' AND objid=to_regprocedure('identity.register_system(uuid,uuid,text,text,text,text,text,bytea)')) THEN RAISE EXCEPTION 'synthetic_command_ddl_failure'; END IF; END $$; CREATE EVENT TRIGGER synthetic_command_ddl_failure ON ddl_command_end WHEN TAG IN ('CREATE FUNCTION') EXECUTE FUNCTION public.synthetic_command_ddl_failure()"))
            before,catalog=self.data_state('failure'),self.snapshot('failure')
            self.command('command-mid-revision-rollback','failure',expected='identity_migration_failed_requires_reconciliation')
            assert self.data_state('failure')==before and self.snapshot('failure')==catalog
        finally:
            with admin.begin() as c:c.execute(text('DROP EVENT TRIGGER synthetic_command_ddl_failure; DROP FUNCTION public.synthetic_command_ddl_failure()'))
            admin.dispose()
        self.command('command-failure-reconciled','failure')
        self.sql('clean','GRANT UPDATE ON identity.operation_outcome TO identity_command_owner')
        before=self.data_state('clean')
        try:self.command('command-catalog-drift','clean',expected='identity_catalog_mismatch:');assert self.data_state('clean')==before
        finally:self.sql('clean','REVOKE UPDATE ON identity.operation_outcome FROM identity_command_owner')
        self.command('command-drift-reconciled','clean')
        self.passed('actor-command-migration-matrix',prior_head5=True,old_data_preserved=True,repeat=True,unsafe_unknown_drift_refused=True,atomic_failure=True)


def main():
    proof,private=fixture();CommandQualification(proof,private).upgrades_and_failures()


if __name__=='__main__':
    try:main()
    except Exception as error:
        report_failure(error)
        raise SystemExit(1) from None
