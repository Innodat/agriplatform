"""Source-bound additive index qualification; root alone executes prepared databases."""
from contextlib import contextmanager
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import json
import signal
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_membership_retirement as retirement
from qualify_identity_baseline import baseline,engine,fixture,text

PREVIOUS_COMMIT='0e460f65afd8e92c32b974412d0ea648f915eced'
PREVIOUS_FILES=retirement.PREVIOUS_FILES | {'versions/0013_membership_retirement.py','membership-retirement-reference.json'}
REQUIRED_CASES=(retirement.REQUIRED_CASES-{'membership_retirement_reference'})|{'active_membership_index_reference'}
INDEX_NAME='org_member_active_org_user_uidx'
FULL_NAME='org_member_org_id_user_id_key'
INDEX_RELATION_ROW=['org_member_active_org_user_uidx','i','identity_migrator',False,False,'','']
INDEX_ROW=['org_member','CREATE UNIQUE INDEX org_member_active_org_user_uidx ON identity.org_member USING btree (org_id, user_id) WHERE (deleted_at IS NULL)',True,True]
INSERT='INSERT INTO identity.org_member(org_id,user_id,deleted_at) VALUES(CAST(:org AS uuid),CAST(:account AS uuid),NULL)'
FULL_SQL="""SELECT k.conname,pg_get_constraintdef(k.oid,true),pg_get_indexdef(k.conindid),
    (SELECT jsonb_agg(jsonb_build_array(d.classid::regclass::text,d.objsubid,d.refclassid::regclass::text,d.refobjsubid,d.deptype,pg_describe_object(d.classid,d.objid,d.objsubid),pg_describe_object(d.refclassid,d.refobjid,d.refobjsubid)) ORDER BY d.classid,d.objid,d.objsubid,d.refclassid,d.refobjid,d.refobjsubid,d.deptype)
     FROM pg_depend d WHERE (d.classid='pg_constraint'::regclass AND d.objid=k.oid) OR (d.refclassid='pg_constraint'::regclass AND d.refobjid=k.oid) OR (d.classid='pg_class'::regclass AND d.objid=k.conindid) OR (d.refclassid='pg_class'::regclass AND d.refobjid=k.conindid))
    FROM pg_constraint k WHERE k.conrelid='identity.org_member'::regclass AND k.conname='org_member_org_id_user_id_key'"""


class ActiveMembershipIndexQualification(retirement.MembershipRetirementQualification):
    required_cases=REQUIRED_CASES

    def full_unique(self,case,administrator=False):
        """Normalize driver Rows before publishing JSON witnesses or comparing them."""
        read=self.admin_sql if administrator else self.sql
        return [list(row) for row in read(case,FULL_SQL)]

    @staticmethod
    def unique_reject(c,statement,v,constraint):
        before=retirement.MembershipRetirementQualification.state(c);nested=c.begin_nested()
        try:c.execute(text(statement),v)
        except Exception as error:
            original=getattr(error,'orig',error)
            assert original.sqlstate=='23505' and original.diag.constraint_name==constraint
        else:raise AssertionError('active_membership_expected_unique_refusal_missing')
        finally:nested.rollback()
        assert retirement.MembershipRetirementQualification.state(c)==before

    def characterize(self):
        case='characterization';v=self.inputs[case];self.fixture_rows(case)
        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0013',)]
        catalog=self.snapshot(case)
        baseline.compare_catalog(baseline.catalog_fingerprints(catalog),baseline.trusted_membership_retirement_reference())
        assert not any(INDEX_NAME in row[1] for row in catalog['indexes'])
        full=self.full_unique(case);assert len(full)==1 and full[0][1]=='UNIQUE (org_id, user_id)'
        before=self.data_state(case)
        with self.fixture_execution(case):
            db=engine(self.private['runtime_urls'][case])
            try:
                with db.connect() as c:
                    with self.execution(c,v):
                        c.execute(text("UPDATE identity.org_member SET deleted_at='2001-01-01'::timestamptz WHERE id=CAST(:member AS bigint)"),v)
                        for deleted in ['NULL',"'2000-01-01'::timestamptz"]:
                            self.unique_reject(c,INSERT.replace('NULL)',deleted+')'),v,FULL_NAME)
                    self.seed_compatibility(c,v)
            finally:db.dispose()
        assert self.data_state(case)==before
        self.witness('active-membership-index-head13-characterization',{'binding':self.characterization_binding(),
            'head':'identity_0013','unchanged_data':True,'catalog':catalog,'full_unique':full,
            'retired_duplicates_refused':True,'active_seed_preserved':True})
        self.passed('active-membership-index-head13-characterization',rollback_only=True)

    def verify_characterization(self,witness):
        assert witness['binding']==self.characterization_binding(),'active_membership_index_characterization_stale_fixture'
        assert witness['head']=='identity_0013' and witness['unchanged_data'] is True
        assert witness['retired_duplicates_refused'] is True and witness['active_seed_preserved'] is True
        assert len(witness['full_unique'])==1 and witness['full_unique'][0][1]=='UNIQUE (org_id, user_id)'
        baseline.compare_catalog(baseline.catalog_fingerprints(witness['catalog']),baseline.trusted_membership_retirement_reference())

    def compatibility(self):
        current=self.snapshot('clean')
        baseline.compare_catalog(baseline.catalog_fingerprints(current),baseline.trusted_active_membership_index_reference())
        paths=sorted(self.proof.glob('active-membership-index-head13-characterization-*.json'),key=lambda p:p.stat().st_mtime_ns)
        assert paths,'active_membership_index_missing_head13_characterization'
        witness=json.loads(paths[-1].read_text());self.verify_characterization(witness);old=witness['catalog']
        assert old.keys()==current.keys() and {key for key in old if old[key]!=current[key]}=={'indexes','relations'}
        assert sorted(current['indexes'])==sorted(old['indexes']+[INDEX_ROW])
        assert sorted(current['relations'])==sorted(old['relations']+[INDEX_RELATION_ROW])
        assert self.full_unique('clean')==witness['full_unique']
        self.passed('active-membership-index-exact-single-index-delta',full_unique_definition_dependencies_preserved=True)

    def index_isolation(self):
        """Administrator-owned DDL rollback isolates the partial index, never runtime DDL."""
        case='clean';v=self.inputs[case];before,catalog=self.data_state(case),self.snapshot(case)
        full=self.full_unique(case,administrator=True);admin=self.admin(case)
        self.witness('active-membership-index-isolation-restoration-required',{'case':case,
            'full_unique':full,'catalog':catalog,'data':before,'administrator_rollback_only':True})
        with self.restoration_signals():
            try:
                with admin.connect() as c:
                    tx=c.begin()
                    try:
                        c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                        c.execute(text('ALTER TABLE identity.org_member DROP CONSTRAINT '+FULL_NAME))
                        c.execute(text('SET LOCAL ROLE service_role'))
                        original=self.state(c);roles=original['member_role']
                        self.reject(c,self.seed_statement(),v,'42P10',None,None)
                        self.unique_reject(c,INSERT,v,INDEX_NAME)
                        multirow=INSERT.replace('VALUES(CAST(:org AS uuid),CAST(:account AS uuid),NULL)',
                            'VALUES(CAST(:spare_org AS uuid),CAST(:spare AS uuid),NULL),(CAST(:org AS uuid),CAST(:account AS uuid),NULL)')
                        self.unique_reject(c,multirow,v,INDEX_NAME)
                        c.execute(text("UPDATE identity.org_member SET deleted_at='2001-01-01'::timestamptz WHERE id=CAST(:member AS bigint)"),v)
                        for date in ['2002-01-01','2003-01-01']:
                            c.execute(text(INSERT.replace('NULL)',"'"+date+"'::timestamptz)")),v)
                        active=c.execute(text(INSERT+' RETURNING id'),v).scalar_one()
                        self.unique_reject(c,INSERT,v,INDEX_NAME)
                        c.execute(text("UPDATE identity.org_member SET deleted_at='2004-01-01'::timestamptz WHERE id=:id"),{'id':active})
                        replacement=c.execute(text(INSERT+' RETURNING id'),v).scalar_one()
                        assert replacement!=active
                        histories=list(c.execute(text('SELECT id,deleted_at IS NULL FROM identity.org_member WHERE org_id=CAST(:org AS uuid) AND user_id=CAST(:account AS uuid) ORDER BY id'),v))
                        assert len(histories)==5 and sum(row[1] for row in histories)==1
                        assert (replacement,True) in histories and (active,False) in histories and (int(v['member']),False) in histories
                        c.execute(text(INSERT),dict(v,org=v['spare_org']))
                        c.execute(text(INSERT),dict(v,account=v['spare']))
                        assert self.state(c)['member_role']==roles
                        assert c.execute(text('SELECT count(*) FROM identity.member_role WHERE member_id=:id'),{'id':active}).scalar_one()==0
                    finally:tx.rollback()
            finally:admin.dispose()
        assert self.data_state(case)==before and self.snapshot(case)==catalog and self.full_unique(case,administrator=True)==full
        self.witness('active-membership-index-isolation-restored',{'case':case,'administrator_rollback_only':True,
            'named_partial_index_23505':INDEX_NAME,'exact_catalog_rows_dependencies_restored':True,'roles_preserved':True})
        self.passed('active-membership-index-isolation',administrator_ddl_only=True,restricted_login_ddl=False,rollback_only=True)

    def concurrency(self):
        """Two independent restricted-login connections; observe the loser's lock wait."""
        case='clean';v=dict(self.inputs[case]);v.update(org=v['spare_org'],account=v['spare'])
        before=self.data_state(case);catalog=self.snapshot(case)
        original_members=self.sql(case,'SELECT to_jsonb(t) FROM identity.org_member t ORDER BY id')
        assert self.sql(case,'SELECT count(*) FROM identity.org_member WHERE org_id=CAST(:org AS uuid) AND user_id=CAST(:account AS uuid)',v)==[(0,)]
        started=Event();pids={};result={};blocked=False
        with self.fixture_execution(case):
            db=engine(self.private['runtime_urls'][case]);admin=self.admin(case)
            try:
                with db.connect() as winner:
                    tx=winner.begin()
                    try:
                        winner.execute(text("SET LOCAL statement_timeout='10s'; SET LOCAL lock_timeout='8s'; SET LOCAL ROLE service_role"))
                        assert winner.execute(text('SELECT session_user,current_user')).one()==('access_runtime','service_role')
                        winner_pid=winner.execute(text('SELECT pg_backend_pid()')).scalar_one()
                        member=winner.execute(text(INSERT+' RETURNING id'),v).scalar_one()
                        def lose():
                            try:
                                with db.connect() as loser:
                                    lt=loser.begin()
                                    try:
                                        loser.execute(text("SET LOCAL statement_timeout='10s'; SET LOCAL lock_timeout='8s'; SET LOCAL ROLE service_role"))
                                        assert loser.execute(text('SELECT session_user,current_user')).one()==('access_runtime','service_role')
                                        pids['loser']=loser.execute(text('SELECT pg_backend_pid()')).scalar_one();started.set()
                                        try:loser.execute(text(INSERT),v)
                                        except Exception as error:
                                            original=getattr(error,'orig',error)
                                            assert getattr(original,'sqlstate',None)=='23505'
                                            assert original.diag.constraint_name in {FULL_NAME,INDEX_NAME}
                                            result.update(sqlstate='23505',constraint=original.diag.constraint_name)
                                        else:result.update(rolled_back_insert=True)
                                    finally:lt.rollback()
                            finally:started.set()
                        with ThreadPoolExecutor(max_workers=1) as pool:
                            future=pool.submit(lose)
                            try:
                                assert started.wait(3),'active_membership_concurrent_start_timeout'
                                if future.done():future.result()
                                assert 'loser' in pids,'active_membership_concurrent_start_failed'
                                deadline=time.monotonic()+3
                                with admin.connect() as observer:
                                    observer.execute(text("SET statement_timeout='2s'"))
                                    while time.monotonic()<deadline:
                                        blocked=observer.execute(text('SELECT :winner=ANY(pg_blocking_pids(:loser))'),dict(winner=winner_pid,loser=pids['loser'])).scalar_one()
                                        if blocked:break
                                        # The database blocking relation proves ordering; this only bounds polling load.
                                        time.sleep(min(.02,max(0,deadline-time.monotonic())))
                                assert blocked,'active_membership_concurrent_block_not_observed'
                                self.witness('active-membership-index-concurrent-retention-required',{'case':case,'member':member,'org':v['org'],'account':v['account'],'synthetic_retained_winner':True})
                                tx.commit()
                            finally:
                                if tx.is_active:tx.rollback()
                                future.result(timeout=12)
                    finally:
                        if tx.is_active:tx.rollback()
            finally:db.dispose();admin.dispose()
        assert blocked and result['sqlstate']=='23505'
        after=self.data_state(case)
        new_members=self.sql(case,'SELECT to_jsonb(t) FROM identity.org_member t ORDER BY id')
        assert len(new_members)==len(original_members)+1 and all(row in new_members for row in original_members)
        assert all(after[key]==value for key,value in before.items() if key!='org_member')
        assert self.snapshot(case)==catalog
        rows=self.sql(case,'SELECT id,deleted_at FROM identity.org_member WHERE org_id=CAST(:org AS uuid) AND user_id=CAST(:account AS uuid)',v)
        assert rows==[(member,None)]
        self.witness('active-membership-index-concurrent-result',dict(result,observed_blocking=True,member=member,
            original_rows_roles_retained=True,both_unique_protections_present=True,synthetic_winner_retained=True,
            join_audit_receipt_safety_claimed=False))
        self.passed('active-membership-index-concurrent-legacy-inserts',observed_blocking=True,committed_count=1,loser_sqlstate='23505',constraint=result['constraint'],synthetic_winner_retained=True)

    @contextmanager
    def failure_fixture(self,case):
        state_sql="""SELECT 'function',p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.proname='synthetic_active_membership_index_failure'
            UNION ALL SELECT 'event_trigger',evtname FROM pg_event_trigger WHERE evtname='synthetic_active_membership_index_failure'
            UNION ALL SELECT 'sequence',c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relname='synthetic_active_membership_index_failure_marker' ORDER BY 1,2"""
        before=self.admin_sql(case,state_sql);assert before==[],'active_membership_index_failure_fixture_already_exists'
        marker_sql='SELECT last_value,is_called FROM public.synthetic_active_membership_index_failure_marker'
        create="""CREATE SEQUENCE public.synthetic_active_membership_index_failure_marker START WITH 1;
            REVOKE ALL ON SEQUENCE public.synthetic_active_membership_index_failure_marker FROM PUBLIC,anon,authenticated,service_role,access_runtime;
            GRANT USAGE ON SEQUENCE public.synthetic_active_membership_index_failure_marker TO identity_migrator;
            CREATE FUNCTION public.synthetic_active_membership_index_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN
            IF to_regclass('identity.org_member_active_org_user_uidx') IS NOT NULL THEN
                PERFORM pg_catalog.nextval('public.synthetic_active_membership_index_failure_marker'::regclass);
                RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_active_membership_index_failure';
            END IF; END $$;
            CREATE EVENT TRIGGER synthetic_active_membership_index_failure ON ddl_command_end WHEN TAG IN ('CREATE INDEX') EXECUTE FUNCTION public.synthetic_active_membership_index_failure();"""
        cleanup='DROP EVENT TRIGGER IF EXISTS synthetic_active_membership_index_failure; DROP FUNCTION IF EXISTS public.synthetic_active_membership_index_failure(); DROP SEQUENCE IF EXISTS public.synthetic_active_membership_index_failure_marker'
        self.witness('active-membership-index-event-restoration-required',{'case':case,'before':before,'create':create,'cleanup':cleanup})
        verified=False
        def verify_fired():
            nonlocal verified
            marker=self.admin_sql(case,marker_sql)
            assert marker==[(1,True)],'active_membership_index_failure_fixture_not_fired'
            if not verified:
                self.witness('active-membership-index-event-fired',{'case':case,'marker_before':[1,False],'marker_after':list(marker[0]),'new_index_observed':True})
                verified=True
        with self.restoration_signals():
            try:
                self.admin_sql(case,create)
                assert self.admin_sql(case,marker_sql)==[(1,False)],'active_membership_index_failure_marker_initially_called'
                yield verify_fired
                verify_fired()
            finally:
                for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,signal.SIG_IGN)
                self.admin_sql(case,cleanup)
                assert self.admin_sql(case,state_sql)==before,'active_membership_index_failure_fixture_not_restored'
                self.witness('active-membership-index-event-restored',{'case':case,'exact_objects':True})


    def function_drift_refusal(self):
        case='unknown';before,catalog=self.data_state(case),self.snapshot(case)
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    assert c.execute(text('SELECT version_num FROM identity.alembic_version')).scalar_one()=='identity_0013'
                    rows=self.state(c)
                    definition=next(row[4] for row in catalog['functions'] if row[:3]==['identity','guard_org_member_revision',''])
                    c.exec_driver_sql(definition.replace('BEGIN\n','BEGIN\n    -- synthetic source drift\n',1),execution_options={'no_parameters':True})
                    changed=baseline.target_catalog_snapshot(c)
                    assert {key for key in catalog if catalog[key]!=changed[key]}=={'functions'}
                    try:baseline.preflight(c,'clean')
                    except baseline.BaselineError as error:assert str(error)=='identity_catalog_mismatch:functions'
                    else:raise AssertionError('active_membership_index_function_drift_accepted')
                    assert baseline.target_catalog_snapshot(c)==changed and self.state(c)==rows
                    assert c.execute(text('SELECT version_num FROM identity.alembic_version')).scalar_one()=='identity_0013'
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state(case)==before and self.snapshot(case)==catalog
        self.passed('active-membership-index-function-drift-refused',rollback_only=True,no_normalization=True)

    def blocked_index_ddl(self):
        case='failure';before,catalog=self.data_state(case),self.snapshot(case)
        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0013',)]
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as holder:
                tx=holder.begin()
                try:
                    holder.execute(text("SET LOCAL statement_timeout='15s'; SET LOCAL lock_timeout='2s'"))
                    holder.execute(text('LOCK TABLE identity.org_member IN ROW EXCLUSIVE MODE'))
                    started=time.monotonic()
                    self.command('active-membership-index-blocked-ddl-refused',case,expected='identity_migration_failed_requires_reconciliation')
                    elapsed=time.monotonic()-started
                    assert 4<=elapsed<30,'active_membership_index_blocked_ddl_bound'
                    assert self.data_state(case)==before and self.snapshot(case)==catalog
                    assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0013',)]
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state(case)==before and self.snapshot(case)==catalog
        self.witness('active-membership-index-blocked-ddl-restored',{'case':case,'elapsed_seconds':round(elapsed,3),
            'lock_mode':'ROW EXCLUSIVE','migration_lock_timeout_seconds':5,'old_catalog_history_data_preserved':True})
        self.passed('active-membership-index-blocked-ddl',bounded_refusal=True,owner_lock_released=True)

    def index_drift_refusal(self):
        case='unsafe';before,catalog=self.data_state(case),self.snapshot(case)
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:
                for form in ['missing','wrong_predicate']:
                    tx=c.begin()
                    try:
                        c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                        assert c.execute(text('SELECT version_num FROM identity.alembic_version')).scalar_one()=='identity_0014'
                        rows=self.state(c)
                        c.execute(text('DROP INDEX identity.'+INDEX_NAME))
                        if form=='wrong_predicate':
                            c.execute(text('CREATE UNIQUE INDEX '+INDEX_NAME+' ON identity.org_member USING btree (org_id,user_id) WHERE deleted_at IS NOT NULL'))
                        changed=baseline.target_catalog_snapshot(c)
                        assert {key for key in catalog if catalog[key]!=changed[key]}==({'indexes','relations'} if form=='missing' else {'indexes'})
                        try:baseline.preflight(c,'clean')
                        except baseline.BaselineError as error:
                            assert str(error)==('identity_catalog_mismatch:indexes,relations' if form=='missing' else 'identity_catalog_mismatch:indexes')
                        else:raise AssertionError('active_membership_index_drift_accepted')
                        assert baseline.target_catalog_snapshot(c)==changed and self.state(c)==rows
                        assert c.execute(text('SELECT version_num FROM identity.alembic_version')).scalar_one()=='identity_0014'
                    finally:tx.rollback()
                    assert baseline.target_catalog_snapshot(c)==catalog and self.state(c)==rows
                    c.rollback()
        finally:db.dispose()
        assert self.data_state(case)==before and self.snapshot(case)==catalog
        self.passed('active-membership-index-drift-preflight-refused',missing_and_wrong_predicate=True,
            direct_preflight_only=True,rollback_only=True,no_normalization=True)

    def upgrades_and_failures(self):
        self.validate_targets();self.prior_evidence(PREVIOUS_COMMIT,PREVIOUS_FILES,'identity_0013')
        self.command('active-membership-index-clean','clean');self.compatibility();self.writes();self.index_isolation();self.concurrency();self.command('active-membership-index-repeat','clean')
        self.legacy('legacy');self.original_ledger('legacy')
        for case in ['legacy','previous']:
            self.row_fixtures(case)
            before=self.data_state(case,membership_without_revision=case=='legacy');external=self.external_state(case)
            acl=self.sql(case,retirement.retention.FUNCTION_ACL) if case=='previous' else None
            self.command('active-membership-index-'+case,case,mode='adopt' if case=='legacy' else 'clean')
            after=self.data_state(case,membership_without_revision=case=='legacy')
            assert all(after[key]==value for key,value in before.items() if key!='identity.alembic_version')
            assert (acl is None or self.sql(case,retirement.retention.FUNCTION_ACL)==acl) and self.external_state(case)==external
        self.blocked_index_ddl()
        with self.failure_fixture('failure') as verify_fired:
            before,catalog=self.data_state('failure'),self.snapshot('failure')
            self.command('active-membership-index-create-index-rollback','failure',expected='identity_migration_failed_requires_reconciliation')
            verify_fired()
            assert self.data_state('failure')==before and self.snapshot('failure')==catalog
            assert self.sql('failure','SELECT version_num FROM identity.alembic_version')==[('identity_0013',)]
        self.command('active-membership-index-after-rollback','failure');self.command('active-membership-index-unsafe-clean','unsafe')
        with self.acl_fixture('unsafe','GRANT INSERT ON identity.users TO authenticated','REVOKE INSERT ON identity.users FROM authenticated','GRANT INSERT (id, username) ON identity.users TO authenticated'):
            before,catalog=self.data_state('unsafe'),self.snapshot('unsafe')
            self.command('active-membership-index-drift-refused','unsafe',expected='identity_profile_column_privileges_mismatch')
            assert self.data_state('unsafe')==before and self.snapshot('unsafe')==catalog
        self.command('active-membership-index-drift-reconciled','unsafe');self.index_drift_refusal();self.function_drift_refusal()
        before,catalog=self.data_state('unknown'),self.snapshot('unknown')
        db=engine(self.private['owner_urls']['unknown'])
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    c.execute(text("UPDATE identity.alembic_version SET version_num='identity_unknown'"))
                    try:baseline.preflight(c,'clean')
                    except baseline.BaselineError as error:assert str(error)=='identity_unknown_history'
                    else:raise AssertionError('active_membership_index_unknown_history_accepted')
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state('unknown')==before and self.snapshot('unknown')==catalog
        self.passed('active-membership-index-migration-matrix',clean_adopt_exact13_repeat=True,exact_acl_preservation=True,
            after_create_index_rollback_recovery=True,drift_unknown_refused=True)


def main():
    if not __debug__:raise RuntimeError('active_membership_index_qualification_optimized_python_prohibited')
    proof,private=fixture();q=ActiveMembershipIndexQualification(proof,private)
    if sys.argv[1:]==['--characterize']:q.validate_targets();q.characterize()
    elif not sys.argv[1:]:q.upgrades_and_failures()
    else:raise RuntimeError('active_membership_index_qualification_arguments_invalid')


if __name__=='__main__':
    try:main()
    except Exception as error:
        print('active_membership_index_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None
