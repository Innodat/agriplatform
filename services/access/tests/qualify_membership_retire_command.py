"""Synthetic-only restricted-login retirement proof; receipts and fixtures retained."""
from pathlib import Path
import sys,json,uuid
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parent))
from qualify_actor_command import CommandQualification, encode, operator, engine, fixture, text
from qualify_identity_baseline import baseline


class RetirementQualification(CommandQualification):
    def snapshot(self,case):
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:return baseline.target_catalog_snapshot(c)
        finally:db.dispose()

    def invoke(self,value,case='clean',lookup=False,url=None):
        db=engine(url or self.private['operator_urls'][case])
        try:
            with db.connect() as c:
                return (operator.outcome(c,value['operation_id'],command='membership.retire',
                    org_id=value['scope']['org_id'],account_id=value['payload']['account_id'])
                    if lookup else operator.execute(c,encode(value)))
        finally:db.dispose()

    def waiting_invocation(self,value,url,ready,start,lookup=False):
        db=engine(url)
        try:
            with db.connect() as c:
                ready.put(c.execute(text('SELECT pg_backend_pid()')).scalar_one());c.commit()
                assert start.wait(timeout=2)
                try:return (operator.outcome(c,value['operation_id'],command='membership.retire',org_id=value['scope']['org_id'],account_id=value['payload']['account_id']) if lookup else operator.execute(c,encode(value)))
                except operator.OperatorError as error:return error.code
        finally:db.dispose()

    def value(self,ids=None):
        v=ids or self.ids
        return dict(schema_version=1,operation_id=str(uuid.uuid4()),command='membership.retire',
            scope=dict(kind='organization',org_id=v['org']),reason_code='synthetic_fixture',evidence_ref='synthetic:retire/qualification',
            payload=dict(account_id=v['account'],membership_id=v['member'],expected_revision='1'))

    def run(self):
        self.ids=json.loads((self.proof/'member-retention-fixtures.json').read_text())['clean']
        old=self.data_state('clean');catalog=self.snapshot('clean')
        assert self.sql('clean','SELECT version_num FROM identity.alembic_version')==[('identity_0015',)]
        self.command('retire-exact15-upgrade','clean')
        now=self.data_state('clean')
        assert all(now[k]==v for k,v in old.items() if k!='identity.alembic_version')
        baseline.compare_catalog(baseline.catalog_fingerprints(self.snapshot('clean')),baseline.trusted_membership_retire_command_reference())
        value=self.value();self.deny(value);self.deny(value,lookup=True)
        actor=self.authority_fixture()
        authority=self.authority(actor,'membership.retire','organization',self.ids['org'],self.ids['account'])
        for field,replacement in [('membership_id','9223372036854775807'),('expected_revision','2')]:
            wrong=deepcopy(value);wrong['payload'][field]=replacement;self.deny(wrong,'operation_conflict')
        for path,replacement in [('account',self.ids['other']),('org',self.ids['other_org'])]:
            wrong=deepcopy(value)
            if path=='account':wrong['payload']['account_id']=replacement
            else:wrong['scope']['org_id']=replacement
            self.deny(wrong);self.deny(wrong,lookup=True)
        before=self.sql('clean','SELECT to_jsonb(m) FROM identity.org_member m WHERE id=CAST(:id AS bigint)',{'id':self.ids['member']})[0][0]
        roles=self.sql('clean','SELECT to_jsonb(r) FROM identity.member_role r ORDER BY id')
        receipt=self.invoke(value)
        after=self.sql('clean','SELECT to_jsonb(m) FROM identity.org_member m WHERE id=CAST(:id AS bigint)',{'id':self.ids['member']})[0][0]
        assert receipt.result.revision=='2' and receipt.result.target.membership_id==self.ids['member']
        assert after['updated_actor_id']==actor and after['revision']==2 and after['deleted_at']==after['updated_at']
        assert all(after[k]==v for k,v in before.items() if k not in {'revision','deleted_at','updated_at','updated_actor_id'})
        assert self.sql('clean','SELECT to_jsonb(r) FROM identity.member_role r ORDER BY id')==roles
        assert self.invoke(value)==receipt and self.invoke(value,lookup=True)==receipt
        changed=deepcopy(value);changed['reason_code']='setup_correction';self.deny(changed,'operation_conflict')
        retired=self.value();self.deny(retired,'operation_conflict')
        self.sql('clean','UPDATE identity.operator_authorities SET enabled=false WHERE id=:id',{'id':authority})
        self.deny(value);self.deny(value,lookup=True)
        self.sql('clean','UPDATE identity.operator_authorities SET enabled=true WHERE id=:id',{'id':authority})
        assert self.invoke(value)==receipt
        # Force identical and changed retries behind their actual outcome lock.
        key=operator.command_outcome_lock_key(actor,operator.parse_command(encode(value)))
        url=self.private['operator_urls']['clean']
        race=self.locked_race(value,value,[url,url],key);assert race==[receipt,receipt]
        race=self.locked_race(value,changed,[url,url],key);assert receipt in race and 'operation_conflict' in race
        assert self.sql('clean','SELECT count(*) FROM identity.business_event WHERE event_id=CAST(:id AS uuid)',{'id':receipt.result.event_id})==[(1,)]
        # Current authority cannot recover a receipt under another target account.
        self.authority(actor,'membership.retire','organization',self.ids['org'],self.ids['other'])
        wrong=deepcopy(value);wrong['payload']['account_id']=self.ids['other']
        assert self.invoke(wrong,lookup=True) is None
        self.deny(wrong,'operation_conflict')
        self.passed('membership-retirement-restricted-commit-replay-conflict',exact_target=True,revision_actor_server_time=True,legacy_roles_preserved=True,current_authority=True,forced_concurrent_retries=True,scoped_lookup=True)
        prepared=self.data_state('clean');self.command('retire-repeat','clean');assert self.data_state('clean')==prepared
        self.persist()
        (self.proof/'membership-retirement-receipt.json').write_text(json.dumps(__import__('dataclasses').asdict(receipt),default=str,indent=2)+'\n')


    def additional(self):
        self.ids=json.loads((self.proof/'member-retention-fixtures.json').read_text())['clean']
        actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        value=self.value();value['payload'].update(account_id=self.ids['other'],membership_id=self.ids['other_member'])
        authority=self.sql('clean',"SELECT id::text FROM identity.operator_authorities WHERE database_login='identity_operator' AND command='membership.retire' AND target_account_id=CAST(:account AS uuid)",{'account':self.ids['other']})[0][0]
        # Owner-bound guard refuses ordinary UPDATE/upsert/INSERT atomically.
        catalog=self.snapshot('clean');before=self.data_state('clean')
        db=engine(self.private['databases']['clean'])
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text('SET LOCAL ROLE service_role'))
                    statements=[
                        'UPDATE identity.org_member SET deleted_at=now() WHERE id=CAST(:member AS bigint)',
                        'UPDATE identity.org_member SET deleted_at=now() WHERE org_id=CAST(:org AS uuid)',
                        'INSERT INTO identity.org_member(org_id,user_id,deleted_at) VALUES(CAST(:spare_org AS uuid),CAST(:spare AS uuid),now())',
                        'INSERT INTO identity.org_member(org_id,user_id,deleted_at) VALUES(CAST(:org AS uuid),CAST(:other AS uuid),now()) ON CONFLICT(org_id,user_id) DO UPDATE SET deleted_at=EXCLUDED.deleted_at']
                    for sql in statements:
                        nested=c.begin_nested()
                        try:
                            c.execute(text(sql),dict(self.ids,member=self.ids['other_member']))
                        except Exception as e:
                            assert e.orig.sqlstate=='23514' and e.orig.diag.message_primary=='identity_membership_retirement_owner_required'
                        else:raise AssertionError('ordinary_retirement_accepted')
                        finally:nested.rollback()
                    c.execute(text('UPDATE identity.org_member SET deleted_at=deleted_at WHERE org_id=CAST(:org AS uuid)'),self.ids)
                    c.execute(text('INSERT INTO identity.org_member(org_id,user_id) VALUES(CAST(:spare_org AS uuid),CAST(:spare AS uuid)) ON CONFLICT(org_id,user_id) DO UPDATE SET is_owner=false'),self.ids)
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state('clean')==before and self.snapshot('clean')==catalog
        # Force required event failure after membership/outcome statements; all roll back.
        create="""CREATE FUNCTION identity.synthetic_retire_event_failure() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_event_failure'; END $$;
        REVOKE ALL ON FUNCTION identity.synthetic_retire_event_failure() FROM PUBLIC;
        CREATE TRIGGER synthetic_retire_event_failure BEFORE INSERT ON identity.business_event FOR EACH ROW EXECUTE FUNCTION identity.synthetic_retire_event_failure();"""
        try:
            self.sql('clean',create)
            self.deny(value,'operation_unavailable')
        finally:
            self.sql('clean','DROP TRIGGER IF EXISTS synthetic_retire_event_failure ON identity.business_event; DROP FUNCTION IF EXISTS identity.synthetic_retire_event_failure()')
        assert self.data_state('clean')==before and self.snapshot('clean')==catalog
        # Revoke while an actual original-session invocation waits on retry namespace.
        from queue import Queue
        from threading import Event
        ready=Queue();start=Event();owner=engine(self.private['owner_urls']['clean'])
        key=operator.command_outcome_lock_key(actor,operator.parse_command(encode(value)))
        try:
            with ThreadPoolExecutor(max_workers=1) as pool:
                with owner.begin() as holder:
                    pid=holder.execute(text('SELECT pg_backend_pid()')).scalar_one()
                    holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
                    pending=pool.submit(self.waiting_invocation,value,self.private['operator_urls']['clean'],ready,start)
                    otherpid=ready.get(timeout=1);start.set();self.witness_waiters(holder,[otherpid],pid,[pending])
                    self.sql('clean','UPDATE identity.operator_authorities SET enabled=false WHERE id=CAST(:id AS uuid)',{'id':authority})
                assert pending.result()=='access_denied'
        finally:
            owner.dispose()
            self.sql('clean','UPDATE identity.operator_authorities SET enabled=true WHERE id=CAST(:id AS uuid)',{'id':authority})
        assert self.invoke(value,lookup=True) is None
        # Missing receipt stays unresolved; successful retry after reauthorization commits once.
        receipt=self.invoke(value);assert self.invoke(value)==receipt
        self.passed('membership-retirement-direct-writer-atomic-refusal-event-rollback-and-revocation',insert_update_upsert_multirow=True,active_seed_noop=True,event_failure_rolls_back=True,actual_waiter=True,current_authority_rechecked=True)
        self.persist()


    def migration_matrix(self):
        # Clean and legacy/adopt upgrades preserve source data and foreign owners.
        for case in ['unsafe','legacy','previous']:
            if case=='legacy':self.legacy(case);self.original_ledger(case)
            if case!='unsafe':self.row_fixtures(case)
            before=self.data_state(case)
            rows={table:self.sql(case,'SELECT to_jsonb(t) FROM identity.'+table+' t ORDER BY id')
                  for table in ['users','org','org_member','member_role']} if case!='unsafe' else {}
            external=self.external_state(case) if case!='unsafe' else None
            self.command('retire-'+case+'-upgrade',case,mode='adopt' if case=='legacy' else 'clean')
            for table,oldrows in rows.items():
                newrows=self.sql(case,'SELECT to_jsonb(t) FROM identity.'+table+' t ORDER BY id')
                if case=='legacy' and table=='org_member':
                    newrows=[({k:v for k,v in row.items() if k not in {'revision','created_actor_id','updated_actor_id'}},) for row, in newrows]
                assert newrows==oldrows,table
            after=self.data_state(case)
            if case=='previous':assert all(after[k]==v for k,v in before.items() if k!='identity.alembic_version')
            if case=='legacy':assert after['supabase_migrations.schema_migrations']==before['supabase_migrations.schema_migrations']
            if external:assert self.external_state(case)==external
            baseline.compare_catalog(baseline.catalog_fingerprints(self.snapshot(case)),baseline.trusted_membership_retire_command_reference())
        # Unknown history and drift remain untouched after rollback-only refusal.
        for form in ['history','function']:
            case='unknown';before=self.data_state(case);catalog=self.snapshot(case);db=engine(self.private['owner_urls'][case])
            try:
                with db.connect() as c:
                    tx=c.begin()
                    try:
                        if form=='history':c.execute(text("UPDATE identity.alembic_version SET version_num='identity_unknown'"))
                        else:
                            definition=next(r[4] for r in catalog['functions'] if r[:3]==['identity','guard_org_member_revision',''])
                            c.exec_driver_sql(definition.replace('BEGIN\n','BEGIN\n -- synthetic drift\n',1),execution_options={'no_parameters':True})
                        changed=baseline.target_catalog_snapshot(c)
                        try:baseline.preflight(c,'clean')
                        except baseline.BaselineError as e:assert str(e)==('identity_unknown_history' if form=='history' else 'identity_catalog_mismatch:functions')
                        else:raise AssertionError('drift_or_unknown_history_accepted')
                        assert baseline.target_catalog_snapshot(c)==changed
                    finally:tx.rollback()
            finally:db.dispose()
            assert self.data_state(case)==before and self.snapshot(case)==catalog
        # Inject a DDL failure after a new retirement function exists; nextval is a durable witness.
        case='failure';before=self.data_state(case);catalog=self.snapshot(case)
        create="""CREATE SEQUENCE public.synthetic_retire_ddl_marker;
        CREATE FUNCTION public.synthetic_retire_ddl_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN
         IF to_regprocedure('identity.guard_org_member_retirement_owner()') IS NOT NULL THEN
          PERFORM nextval('public.synthetic_retire_ddl_marker');
          RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_retire_ddl_failure'; END IF; END $$;
        CREATE EVENT TRIGGER synthetic_retire_ddl_failure ON ddl_command_end WHEN TAG IN ('CREATE FUNCTION') EXECUTE FUNCTION public.synthetic_retire_ddl_failure();
        GRANT USAGE ON SEQUENCE public.synthetic_retire_ddl_marker TO identity_migrator;"""
        try:
            self.sql(case,create,role='databases')
            self.command('retire-injected-ddl-rollback',case,expected='identity_migration_failed_requires_reconciliation')
            assert self.sql(case,'SELECT last_value,is_called FROM public.synthetic_retire_ddl_marker',role='databases')==[(1,True)]
        finally:
            self.sql(case,'DROP EVENT TRIGGER IF EXISTS synthetic_retire_ddl_failure; DROP FUNCTION IF EXISTS public.synthetic_retire_ddl_failure(); DROP SEQUENCE IF EXISTS public.synthetic_retire_ddl_marker',role='databases')
        assert self.data_state(case)==before and self.snapshot(case)==catalog
        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0015',)]
        self.command('retire-after-ddl-recovery',case)
        # Existing registration command still works via actual restricted original login.
        from qualify_actor_command import document as actor_document, CommandQualification
        actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        self.authority(actor,'actor.register_system')
        value=actor_document();old=CommandQualification(self.proof,self.private)
        receipt=old.invoke(value);assert old.invoke(value)==receipt and old.invoke(value,lookup=True)==receipt
        assert receipt.result.disposition=='created'
        self.passed('membership-retirement-clean-adopt-exact15-ddl-rollback-drift-and-actor-regression',all_original_rows_preserved=True,external_owner_references_preserved=True,previous_command_actual_replay_lookup=True,independent_catalog=True)
        self.persist()


    def recovery_and_isolation(self):
        self.ids=json.loads((self.proof/'member-retention-fixtures.json').read_text())['clean']
        actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        member=self.sql('clean','INSERT INTO identity.org_member(org_id,user_id) VALUES(CAST(:org AS uuid),CAST(:account AS uuid)) RETURNING id',{'org':self.ids['spare_org'],'account':self.ids['spare']})[0][0]
        self.authority(actor,'membership.retire','organization',self.ids['spare_org'],self.ids['spare'])
        value=self.value({'org':self.ids['spare_org'],'account':self.ids['spare'],'member':str(member)})
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
        db=engine(self.private['operator_urls']['clean'])
        try:
            with db.connect() as c:
                try:operator.execute(LostConnection(c),encode(value))
                except operator.OperatorError as e:assert e.code=='operation_unavailable' and e.__context__ is None
                else:raise AssertionError('uncertain_commit_reported_success')
            receipt=self.invoke(value,lookup=True);assert receipt is not None and self.invoke(value)==receipt
            with db.connect() as c:
                with c.begin():
                    c.execute(text("SELECT set_config('app.actor_id',:actor,true),set_config('app.org_id',:org,true)"),{'actor':str(uuid.uuid4()),'org':str(uuid.uuid4())})
                    c.execute(text('SET LOCAL search_path=pg_temp,public,identity'))
                    result=c.execute(text('SELECT * FROM identity.membership_retirement_outcome(CAST(:op AS uuid),CAST(:org AS uuid),CAST(:account AS uuid))'),dict(op=value['operation_id'],org=value['scope']['org_id'],account=value['payload']['account_id'])).one()
                    assert result[0]['target']['membership_id']==str(member)
                for sql in ['SELECT * FROM identity.org_member','SELECT * FROM identity.operation_outcome','SELECT * FROM identity.business_event',
                    'UPDATE identity.org_member SET deleted_at=now()','SET ROLE identity_command_owner','SET ROLE identity_migrator']:
                    with c.begin():
                        sp=c.begin_nested()
                        try:c.execute(text(sql))
                        except Exception as e:assert e.orig.sqlstate=='42501'
                        else:raise AssertionError('operator_excess_authority')
                        finally:sp.rollback()
                with c.begin():
                    sp=c.begin_nested()
                    try:c.execute(text('SELECT * FROM identity.retire_membership(CAST(:op AS uuid),CAST(:org AS uuid),CAST(:account AS uuid),:member,1,\'synthetic_fixture\',NULL,:canonical)'),
                        dict(op=str(uuid.uuid4()),org=value['scope']['org_id'],account=value['payload']['account_id'],member=member,canonical=b'forged canonical'))
                    except Exception as e:assert e.orig.sqlstate=='IC005'
                    else:raise AssertionError('forged_canonical_accepted')
                    finally:sp.rollback()
        finally:db.dispose()
        owner=engine(self.private['owner_urls']['clean'])
        try:
            with owner.begin() as holder:
                holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':operator.command_outcome_lock_key(actor,operator.parse_command(encode(value)))})
                self.deny(value,'operation_busy')
                self.deny(value,'operation_busy',lookup=True)
        finally:owner.dispose()
        self.sql('clean',"UPDATE identity.operator_principals SET enabled=false WHERE database_login='identity_operator'")
        try:self.deny(value);self.deny(value,lookup=True)
        finally:self.sql('clean',"UPDATE identity.operator_principals SET enabled=true WHERE database_login='identity_operator'")
        assert self.invoke(value,lookup=True)==receipt
        self.passed('membership-retirement-lost-commit-recovery-and-isolation',actual_restricted_commit=True,same_operation_recovery=True,no_raw_authority=True,guc_and_role_spoofing_denied=True,direct_canonical_refusal=True,bounded_busy=True,disabled_principal_denied=True)
        self.persist()


    def fresh_race(self):
        self.ids=json.loads((self.proof/'member-retention-fixtures.json').read_text())['clean']
        actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        self.authority(actor,'membership.retire','organization',self.ids['other_org'],self.ids['account'])
        value=self.value({'org':self.ids['other_org'],'account':self.ids['account'],'member':self.ids['other_org_member']})
        before=self.sql('clean','SELECT revision,deleted_at FROM identity.org_member WHERE id=CAST(:member AS bigint)',{'member':self.ids['other_org_member']});assert before==[(1,None)]
        url=self.private['operator_urls']['clean'];key=operator.command_outcome_lock_key(actor,operator.parse_command(encode(value)))
        results=self.locked_race(value,value,[url,url],key)
        assert results[0]==results[1] and results[0].result.revision=='2'
        assert self.sql('clean','SELECT count(*) FROM identity.operation_outcome WHERE operation_id=CAST(:op AS uuid)',{'op':value['operation_id']})==[(1,)]
        assert self.sql('clean','SELECT count(*) FROM identity.business_event WHERE event_id=CAST(:id AS uuid)',{'id':results[0].result.event_id})==[(1,)]
        assert self.invoke(value,lookup=True)==results[0]
        self.passed('membership-retirement-fresh-concurrent-once',actual_waiters=True,one_revision_event_outcome=True)
        self.persist()

    def fresh_fixture(self,case='clean'):
        ids={name:str(uuid.uuid4()) for name in ['account','org']}
        self.sql(case,'INSERT INTO auth.users(id,email) VALUES(CAST(:account AS uuid),:email)',dict(ids,email='synthetic-'+ids['account']+'@example.invalid'),role='databases')
        self.sql(case,"INSERT INTO identity.org(id,name,slug) VALUES(CAST(:org AS uuid),'Synthetic retirement review',:slug)",dict(ids,slug='synthetic-'+ids['org']))
        ids['member']=str(self.sql(case,'INSERT INTO identity.org_member(org_id,user_id) VALUES(CAST(:org AS uuid),CAST(:account AS uuid)) RETURNING id',ids)[0][0])
        return ids

    def review_boundaries(self):
        from queue import Queue
        from threading import Event
        from hashlib import sha256
        from dataclasses import asdict
        self.ids=json.loads((self.proof/'member-retention-fixtures.json').read_text())['clean']
        actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        # A committed receipt lookup must recheck the revoked exact authority after waiting.
        receipt=json.loads((self.proof/'membership-retirement-receipt.json').read_text())
        value=self.value();value['operation_id']=receipt['operation_id']
        authority=self.sql('clean',"SELECT id::text FROM identity.operator_authorities WHERE database_login='identity_operator' AND command='membership.retire' AND org_id=CAST(:org AS uuid) AND target_account_id=CAST(:account AS uuid)",self.ids)[0][0]
        before=self.data_state('clean');owner=engine(self.private['owner_urls']['clean']);ready=Queue();start=Event()
        try:
            with ThreadPoolExecutor(max_workers=1) as pool:
                with owner.begin() as holder:
                    blocker=holder.execute(text('SELECT pg_backend_pid()')).scalar_one()
                    holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':operator.command_outcome_lock_key(actor,operator.parse_command(encode(value)))})
                    pending=pool.submit(self.waiting_invocation,value,self.private['operator_urls']['clean'],ready,start,True)
                    pid=ready.get(timeout=1);start.set();self.witness_waiters(holder,[pid],blocker,[pending])
                    self.sql('clean','UPDATE identity.operator_authorities SET enabled=false WHERE id=CAST(:id AS uuid)',{'id':authority})
                assert pending.result()=='access_denied'
        finally:
            start.set();owner.dispose()
            self.sql('clean','UPDATE identity.operator_authorities SET enabled=true WHERE id=CAST(:id AS uuid)',{'id':authority})
        after=self.data_state('clean')
        assert all(after[k]==v for k,v in before.items() if k!='operator_authorities')
        assert self.invoke(value,lookup=True).result.event_id==receipt['result']['event_id']
        self.passed('membership-retirement-lookup-revoked-while-blocked',actual_committed_receipt=True,no_business_or_evidence_effect=True,synthetic_authority_only_restored=True)
        # Exact alternative scope is authorized, but the original member cannot move to it.
        alternative=self.fresh_fixture()
        self.authority(actor,'membership.retire','organization',alternative['org'],alternative['account'])
        for ids in [{'org':self.ids['org'],'account':self.ids['other'],'member':self.ids['member']},
                    {'org':self.ids['other_org'],'account':self.ids['account'],'member':self.ids['member']}]:
            wrong=self.value(ids);self.deny(wrong,'operation_conflict')
        self.passed('membership-retirement-authorized-wrong-row-binding',fresh_operations=True,wrong_org_and_account=True,full_state_unchanged=True)
        # Different operations contend on shared member history, not a common operation lock.
        first=self.value(alternative);second=deepcopy(first);second['operation_id']=str(uuid.uuid4())
        lock='identity:membership:v1:'+alternative['org']+':'+alternative['account']
        key=int.from_bytes(sha256(lock.encode()).digest()[:8],'big',signed=True)
        url=self.private['operator_urls']['clean'];results=self.locked_race(first,second,[url,url],key)
        assert sum(not isinstance(r,str) for r in results)==1 and results.count('operation_conflict')==1
        winner=next(r for r in results if not isinstance(r,str));loser=next(v for v,r in zip([first,second],results) if isinstance(r,str))
        assert winner.result.revision=='2'
        assert self.sql('clean','SELECT count(*) FROM identity.operation_outcome WHERE operation_id IN (CAST(:first AS uuid),CAST(:second AS uuid))',{'first':first['operation_id'],'second':second['operation_id']})==[(1,)]
        assert self.sql('clean','SELECT count(*) FROM identity.business_event WHERE target_key=:member AND event_type=\'identity.membership_retired\'',alternative)==[(1,)]
        assert self.invoke(loser,lookup=True) is None
        self.write_review_artifact('review-race-receipt-'+uuid.uuid4().hex+'.json',asdict(winner))
        self.passed('membership-retirement-distinct-first-operation-race',one_transition=True,loser_no_event_or_outcome=True,fixtures_retained=True)
        self.persist()

    def review_fixes(self):
        self.review_boundaries();self.maximum_revision();self.actual_cli_retirement();self.persist()

    def maximum_revision(self):
        actor=self.sql('clean',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
        # The maximum revision fixture is prepared and exercised in one rolled-back transaction.
        maximum=self.fresh_fixture();self.authority(actor,'membership.retire','organization',maximum['org'],maximum['account'])
        before=self.data_state('clean');catalog=self.snapshot('clean');admin=self.admin('clean')
        try:
            with admin.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text('SET LOCAL ROLE identity_migrator'))
                    c.execute(text('ALTER TABLE identity.org_member DISABLE TRIGGER org_member_revision_guard'))
                    c.execute(text('UPDATE identity.org_member SET revision=9223372036854775807 WHERE id=CAST(:member AS bigint)'),maximum)
                    c.execute(text('ALTER TABLE identity.org_member ENABLE TRIGGER org_member_revision_guard'))
                    prepared={t:list(c.execute(text('SELECT to_jsonb(t) FROM identity.'+t+' t ORDER BY 1'))) for t in ['org_member','member_role','operation_outcome','business_event']}
                    c.execute(text('RESET ROLE'));c.execute(text('SET LOCAL SESSION AUTHORIZATION identity_operator'))
                    assert c.execute(text('SELECT session_user,current_user')).one()==('identity_operator','identity_operator')
                    command=self.value(maximum);command['payload']['expected_revision']='9223372036854775807'
                    sp=c.begin_nested()
                    try:
                        c.execute(text('SELECT * FROM identity.retire_membership(CAST(:op AS uuid),CAST(:org AS uuid),CAST(:account AS uuid),CAST(:member AS bigint),9223372036854775807,\'synthetic_fixture\',:evidence,:canonical)'),dict(maximum,op=command['operation_id'],evidence=command['evidence_ref'],canonical=operator.canonical_command(operator.parse_command(encode(command)))))
                    except Exception as e:assert e.orig.sqlstate=='IC003'
                    else:raise AssertionError('maximum_revision_retirement_accepted')
                    finally:sp.rollback()
                    c.execute(text('RESET SESSION AUTHORIZATION'));c.execute(text('SET LOCAL ROLE identity_migrator'))
                    assert prepared=={t:list(c.execute(text('SELECT to_jsonb(t) FROM identity.'+t+' t ORDER BY 1'))) for t in prepared}
                finally:tx.rollback()
        finally:admin.dispose()
        assert self.data_state('clean')==before and self.snapshot('clean')==catalog
        self.passed('membership-retirement-maximum-revision',rollback_only_preparation=True,conflict=True,member_roles_evidence_unchanged=True)
        self.persist()

    def write_review_artifact(self,name,value):
        import os
        fd=os.open(self.proof/name,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(fd,'w') as output:json.dump(value,output,default=str,sort_keys=True,indent=2);output.write('\n')

    def actual_cli_retirement(self):
        # Consume the existing prepared native target and private owner fixture unchanged.
        import operator_cli as cli
        from identity_operator_target import load_target,ROOT
        from urllib.parse import urlsplit,urlunsplit
        run=json.loads((self.proof/'run.json').read_text())
        target=load_target(ROOT/'platform/deployment/.local/kdg'/run['run_id']/'identity-operator.json')
        native_fixture=ROOT/'platform/deployment/.local/identity-baseline/operator-target-gf2ef2d8/qualification-fixture.json'
        with cli.dev.directory(native_fixture.parent) as fd:
            stored=cli.dev.decode(cli.dev.read_at(fd,native_fixture.name,protected=True))
        assert stored['run_id']==target.run_id and stored['database']==target.database
        owner_url=stored['owner_url'];parsed=urlsplit(owner_url)
        assert parsed.username=='identity_migrator' and parsed.hostname=='127.0.0.1' and parsed.port==target.port and parsed.path=='/'+target.database
        # Reuse the established migration runner; the prepared target remains immutable.
        self.private['owner_urls']['cli']=owner_url
        self.private['databases']['cli']=urlunsplit(urlsplit(self.private['admin_url'])._replace(path='/'+target.database))
        try:
            self.command('retire-review-native-cli-upgrade','cli')
            ids=self.fresh_fixture('cli')
            actor=self.sql('cli',"SELECT executor_actor_id::text FROM identity.operator_principals WHERE database_login='identity_operator'")[0][0]
            self.sql('cli',"INSERT INTO identity.operator_authorities(id,database_login,command,scope_kind,org_id,target_account_id,enabled,created_by,updated_by) VALUES(CAST(:id AS uuid),'identity_operator','membership.retire','organization',CAST(:org AS uuid),CAST(:account AS uuid),true,CAST(:actor AS uuid),CAST(:actor AS uuid))",dict(ids,id=str(uuid.uuid4()),actor=actor))
            value=self.value(ids);work=target.path.parent/('retire-review-'+uuid.uuid4().hex);work.mkdir(mode=0o700)
            with cli.dev.directory(work) as fd:__import__('native_cli').write_private(fd,'command.json',encode(value))
            base=['--owner','identity','--target',str(target.path)]
            # Same bounded public-main launcher used by qualify_operator_target.
            launcher="import contextlib,io,json,sys;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1]).parent));import operator_cli as c;output=io.StringIO()\nwith contextlib.redirect_stdout(output):status=c.main(sys.argv[2:])\nprint(json.dumps({'exit_status':status,'result':json.loads(output.getvalue())}))"
            def invoke(args):
                raw=cli.images.bounded_command([sys.executable,'-I','-B','-c',launcher,str(ROOT/'services/access/operator_cli.py'),*args],ROOT,{'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},16,8192)
                envelope=cli.dev.decode(raw);assert envelope['exit_status']==0
                return cli._receipt(envelope['result'],value['operation_id'],'membership.retire')
            args=['execute',*base,'--command-file',str(work/'command.json')]
            receipt=invoke(args);assert invoke(args)==receipt
            assert invoke(['outcome',*base,'--command','membership.retire','--operation-id',value['operation_id'],'--org-id',ids['org'],'--account-id',ids['account']])==receipt
            self.verify_all_retirements('cli')
            self.write_review_artifact('review-cli-receipt.json',dict(receipt=receipt,fixture=ids,target=str(target.path),command_file=str(work/'command.json')))
            self.passed('membership-retirement-actual-native-cli',execute_replay_lookup_identical=True,prepared_target_unchanged=True,committed_consistency=True)
        finally:
            self.private['owner_urls'].pop('cli',None);self.private['databases'].pop('cli',None)

    def verify_all_retirements(self,case):
        from dataclasses import asdict
        rows=self.sql(case,"""SELECT o.operation_id::text,o.result,o.command_version,o.result_version,o.committed_at,
         o.executor_actor_id::text,o.scope_id::text,e.event_id::text,e.event_type,e.event_version,e.created_at,
         e.executor_actor_id::text,e.scope_id::text,e.target,e.target_key,e.transition,
         m.id::text,m.org_id::text,m.user_id::text,m.revision,m.deleted_at,m.updated_at,m.updated_actor_id::text,
         (SELECT count(*) FROM identity.business_event all_events WHERE all_events.outcome_id=o.id)
         FROM identity.operation_outcome o LEFT JOIN identity.business_event e ON e.outcome_id=o.id
         LEFT JOIN identity.org_member m ON m.id::text=o.result->'target'->>'membership_id'
         WHERE o.command_type='membership.retire' ORDER BY o.operation_id""")
        receipts=[]
        for row in rows:
            op,result,cv,rv,instant,executor,scope,event_id,event_type,event_version,event_time,event_executor,event_scope,target,key,transition,member,org,account,revision,deleted,updated,update_actor,event_count=row
            receipt=operator._receipt((result,cv,rv,instant),op,'membership.retire')
            assert result['target']==target=={'org_id':org,'account_id':account,'membership_id':member}
            assert result['event_id']==event_id and result['revision']==str(revision) and revision==2
            assert transition=={'before':{'revision':'1','retired':False},'after':{'revision':'2','retired':True}}
            assert event_type=='identity.membership_retired' and event_version==1 and key==member and event_count==1
            assert executor==event_executor==update_actor and scope==event_scope==org
            assert instant==event_time==deleted==updated
            receipts.append(asdict(receipt))
        return receipts

    def verify_retained(self):
        self.ids=json.loads((self.proof/'member-retention-fixtures.json').read_text())['clean']
        receipts=self.verify_all_retirements('clean')
        saved=json.loads((self.proof/'membership-retirement-receipt.json').read_text())
        original=next(r for r in receipts if r['operation_id']==saved['operation_id'])
        assert original['result']==saved['result'] and str(original['committed_at'])==saved['committed_at']
        artifacts=[*sorted(self.proof.glob('review-race-receipt*.json')),self.proof/'review-cli-receipt.json']
        for path in artifacts:
            name=path.name
            if not path.exists():continue
            artifact=json.loads(path.read_text())
            if name=='review-cli-receipt.json':
                from urllib.parse import urlsplit,urlunsplit
                stored=json.loads((Path(__file__).resolve().parents[3]/'platform/deployment/.local/identity-baseline/operator-target-gf2ef2d8/qualification-fixture.json').read_text())
                self.private['owner_urls']['cli']=stored['owner_url']
                try:
                    current=self.verify_all_retirements('cli')
                    baseline.compare_catalog(baseline.catalog_fingerprints(self.snapshot('cli')),baseline.trusted_membership_retire_command_reference())
                finally:self.private['owner_urls'].pop('cli',None)
                expected=artifact['receipt']
            else:current=receipts;expected=artifact
            actual=next(r for r in current if r['operation_id']==expected['operation_id'])
            from datetime import datetime
            assert actual['committed_at']==datetime.fromisoformat(expected['committed_at'])
            assert {k:v for k,v in actual.items() if k!='committed_at'}=={k:v for k,v in expected.items() if k!='committed_at'}
        for case in ['clean','legacy','previous','unsafe','failure']:
            baseline.compare_catalog(baseline.catalog_fingerprints(self.snapshot(case)),baseline.trusted_membership_retire_command_reference())
        self.write_review_artifact('verified-retirement-receipts-'+uuid.uuid4().hex+'.json',receipts)
        self.passed('membership-retirement-final-retained-state',independent_catalogs=True,all_committed_retirements_checked=len(receipts),exact_transition_identity_executor_and_time=True,no_fixture_reset=True)
        self.persist()


def main():
    if not __debug__:raise RuntimeError('qualification_optimized_python_prohibited')
    proof,private=fixture();q=RetirementQualification(proof,private)
    from hashlib import sha256
    import os
    root=Path(__file__).resolve().parents[3]
    paths=[*sorted((root/'services/access/identity-migrations').glob('*.py')),
        *sorted((root/'services/access/identity-migrations/versions').glob('*.py')),
        *sorted((root/'services/access/identity-migrations').glob('*reference.json')),
        root/'services/access/tests/qualify_membership_retire_command.py',
        root/'services/access/tests/qualify_identity_baseline.py',root/'services/access/identity_operator.py',root/'services/access/operator_cli.py']
    paths.extend(sorted((root/'services/access/tests').glob('qualify_*.py')))
    paths.extend(root/'services/access'/name for name in ['identity_operator_input.py','identity_operator_target.py','identity-alembic.ini'])
    paths.extend(sorted((root/'platform/deployment').glob('*.py')))
    paths.extend(sorted((root/'platform/deployment').glob('*.json')))
    paths.extend(sorted((root/'platform/deployment/schema').glob('*.json')))
    paths.extend(sorted((root/'platform/deployment/environments').glob('*.json')))
    paths.append(root/'services/access/identity-migrations/source-pins.json')
    paths.extend(sorted((root/'platform/supabase/migrations').glob('*.sql')))
    import dev
    paths.extend(root/name for name in dev.SOURCES)
    paths.extend(root/name for name in baseline.SOURCES)
    paths.extend(root/'services/access/identity-migrations'/name for name in ['uv.lock','pyproject.toml'])
    paths=sorted(set(paths))
    captured={str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in paths}
    witness=proof/('source-capture-'+uuid.uuid4().hex+'.json')
    witness.write_text(json.dumps({'stage':sys.argv[1:] or ['initial'],'before':captured,'status':'started'},indent=2)+'\n');witness.chmod(0o600)
    if sys.argv[1:]==['--additional']:q.additional()
    elif sys.argv[1:]==['--matrix']:q.migration_matrix()
    elif sys.argv[1:]==['--recovery']:q.recovery_and_isolation()
    elif sys.argv[1:]==['--fresh-race']:q.fresh_race()
    elif sys.argv[1:]==['--verify-retained']:q.verify_retained()
    elif sys.argv[1:]==['--review-fixes']:q.review_fixes()
    elif sys.argv[1:]==['--review-boundaries']:q.review_boundaries()
    elif sys.argv[1:]==['--review-remaining']:q.maximum_revision();q.actual_cli_retirement();q.persist()
    elif not sys.argv[1:]:q.run()
    else:raise RuntimeError('qualification_arguments_invalid')
    assert captured=={str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in paths},'qualification_source_changed'
    witness.write_text(json.dumps({'stage':sys.argv[1:] or ['initial'],'before':captured,'after':captured,'status':'passed'},indent=2)+'\n')

if __name__=='__main__':
    try:main()
    except Exception as error:
        import traceback
        trace=traceback.extract_tb(error.__traceback__)
        print('membership_retire_qualification_failed',json.dumps({'type':type(error).__name__,'sqlstate':getattr(getattr(error,'orig',None),'sqlstate',None),'frames':[(Path(t.filename).name,t.name,t.lineno) for t in trace]}),file=sys.stderr)
        raise SystemExit(1)
