"""Source-bound one-way retirement proof; database execution belongs to root."""
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime,timedelta
import json
import signal
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_membership_retention as retention
from qualify_identity_baseline import baseline,engine,fixture,text

PREVIOUS_COMMIT='c70a5d02096c3c22d582d3bd277134962bd02e51'
PREVIOUS_FILES=retention.PREVIOUS_FILES | {'versions/0012_membership_retention.py','membership-retention-reference.json'}
REQUIRED_CASES=(retention.REQUIRED_CASES-{'membership_retention_reference'})|{'membership_retirement_reference'}
RETIREMENT_CHECK="""    IF TG_OP = 'UPDATE' AND OLD.deleted_at IS NOT NULL
        AND NEW.deleted_at IS DISTINCT FROM OLD.deleted_at THEN
        RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'identity_membership_retirement_immutable',
            CONSTRAINT = 'org_member_retirement_immutable';
    END IF;
"""


class MembershipRetirementQualification(retention.MembershipRetentionQualification):
    required_cases=REQUIRED_CASES

    @staticmethod
    def retirement_statements():
        return {'clear':'UPDATE identity.org_member SET deleted_at=NULL WHERE id=CAST(:member AS bigint)',
            'retime':"UPDATE identity.org_member SET deleted_at=deleted_at+interval '1 second' WHERE id=CAST(:member AS bigint)",
            'backward':"UPDATE identity.org_member SET deleted_at=deleted_at-interval '1 second' WHERE id=CAST(:member AS bigint)",
            'subsecond':"UPDATE identity.org_member SET deleted_at=deleted_at+interval '1 microsecond' WHERE id=CAST(:member AS bigint)"}

    def characterize(self):
        case='characterization';v=self.inputs[case];self.fixture_rows(case)
        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0012',)]
        catalog=self.snapshot(case)
        baseline.compare_catalog(baseline.catalog_fingerprints(catalog),baseline.trusted_membership_retention_reference())
        before=self.data_state(case);observed=[]
        with self.fixture_execution(case):
            db=engine(self.private['runtime_urls'][case])
            try:
                with db.connect() as c:
                    for path in ['clear','retime']:
                        statement=self.retirement_statements()[path]
                        with self.execution(c,v):
                            c.execute(text("UPDATE identity.org_member SET deleted_at='2001-01-01'::timestamptz WHERE id=CAST(:member AS bigint)"),v)
                            original=c.execute(text('SELECT to_jsonb(t) FROM identity.org_member t WHERE id=CAST(:member AS bigint)'),v).scalar_one()
                            changed=c.execute(text(statement+' RETURNING to_jsonb(org_member)'),v).scalar_one()
                            assert changed['deleted_at']!=original['deleted_at'] and changed['revision']==original['revision']+1
                            observed.append({'path':path,'before':original,'after':changed})
            finally:db.dispose()
        assert self.data_state(case)==before
        self.witness('membership-retirement-head12-characterization',{'binding':self.characterization_binding(),
            'head':'identity_0012','unchanged_data':True,'observed':observed,'catalog':catalog})
        self.passed('membership-retirement-head12-characterization',real_login='access_runtime',clear_and_retime_accepted=True,rollback_only=True)

    def verify_characterization(self,witness):
        assert witness['binding']==self.characterization_binding(),'membership_retirement_characterization_stale_fixture'
        assert witness['head']=='identity_0012' and witness['unchanged_data'] is True
        assert len(witness['observed'])==2 and {row['path'] for row in witness['observed']}=={'clear','retime'}
        v=self.inputs['characterization']
        for row in witness['observed']:
            before,after=row['before'],row['after']
            assert (before['id'],before['user_id'],before['org_id'])==(int(v['member']),v['account'],v['org'])
            assert before['deleted_at'] is not None and before['deleted_at']!=after['deleted_at']
            assert (after['deleted_at'] is None)==(row['path']=='clear')
            if row['path']=='retime':assert datetime.fromisoformat(after['deleted_at'])==datetime.fromisoformat(before['deleted_at'])+timedelta(seconds=1)
            assert after==dict(before,deleted_at=after['deleted_at'],revision=before['revision']+1)
        baseline.compare_catalog(baseline.catalog_fingerprints(witness['catalog']),baseline.trusted_membership_retention_reference())

    def compatibility(self):
        current=self.snapshot('clean')
        baseline.compare_catalog(baseline.catalog_fingerprints(current),baseline.trusted_membership_retirement_reference())
        witnesses=sorted(self.proof.glob('membership-retirement-head12-characterization-*.json'),key=lambda p:p.stat().st_mtime_ns)
        assert witnesses,'membership_retirement_missing_head12_characterization'
        witness=json.loads(witnesses[-1].read_text());self.verify_characterization(witness);old=witness['catalog']
        assert old.keys()==current.keys() and {key for key in old if old[key]!=current[key]}=={'functions'}
        self.verify_function_delta(old['functions'],current['functions'])
        guard=lambda rows:next(row[4] for row in rows if row[:3]==['identity','guard_org_member_revision',''])
        assert guard(current['functions'])==guard(old['functions']).replace("    IF TG_OP = 'INSERT' THEN",RETIREMENT_CHECK+"    IF TG_OP = 'INSERT' THEN",1)
        self.passed('membership-retirement-exact-function-only-delta',original_owner_acl_declaration_triggers_constraints_preserved=True)

    def retirement_reject(self,c,statement,v):
        before=self.state(c)
        self.reject(c,statement,v,'23514','identity_membership_retirement_immutable','org_member_retirement_immutable')
        assert self.state(c)==before,'membership_retirement_partial_effects'

    @staticmethod
    def seed_statement():
        return 'INSERT INTO identity.org_member(org_id,user_id,is_owner,deleted_at) VALUES(CAST(:org AS uuid),CAST(:account AS uuid),true,NULL) ON CONFLICT(org_id,user_id) DO UPDATE SET is_owner=excluded.is_owner,deleted_at=excluded.deleted_at'

    def seed_compatibility(self,c,v):
        with self.execution(c,v):
            original=c.execute(text('SELECT to_jsonb(t) FROM identity.org_member t WHERE id=CAST(:member AS bigint)'),v).scalar_one()
            roles=list(c.execute(text('SELECT to_jsonb(t) FROM identity.member_role t ORDER BY id')))
            row=c.execute(text(self.seed_statement()+' RETURNING to_jsonb(org_member)'),v).scalar_one()
            assert row==dict(original,is_owner=True,revision=original['revision']+(not original['is_owner']))
            assert c.execute(text(self.seed_statement()+' RETURNING to_jsonb(org_member)'),v).scalar_one()==row
            assert c.execute(text('SELECT id FROM identity.org_member WHERE org_id=CAST(:org AS uuid) AND user_id=CAST(:account AS uuid)'),v).scalar_one()==original['id']
            c.execute(text('UPDATE identity.org_member SET deleted_at=now() WHERE id=CAST(:member AS bigint)'),v)
            self.retirement_reject(c,self.seed_statement(),v)
            assert list(c.execute(text('SELECT to_jsonb(t) FROM identity.member_role t ORDER BY id')))==roles
        self.passed('membership-retirement-seed-compatibility',active_upsert_noop_lookup_preserved=True,retired_upsert_refused=True,rollback_only=True)

    def writes(self):
        case='clean';v=self.inputs[case];self.fixture_rows(case);before=self.data_state(case)
        with self.fixture_execution(case):
            db=engine(self.private['runtime_urls'][case])
            try:
                with db.connect() as c:
                    for retired in [False,True]:
                        with self.execution(c,v):
                            if retired:c.execute(text("UPDATE identity.org_member SET deleted_at='2001-01-01'::timestamptz WHERE id=CAST(:member AS bigint)"),v)
                            for field,value in [('id','id+1000000'),('org_id','CAST(:spare_org AS uuid)'),('user_id','CAST(:spare AS uuid)')]:
                                self.reject(c,'UPDATE identity.org_member SET '+field+'='+value+' WHERE id=CAST(:member AS bigint)',v)
                                if retired:self.reject(c,'UPDATE identity.org_member SET '+field+'='+value+',deleted_at=NULL WHERE id=CAST(:member AS bigint)',v)
                            for roleless in [False,True]:
                                nested=c.begin_nested()
                                try:
                                    if roleless:c.execute(text('DELETE FROM identity.member_role WHERE member_id=CAST(:member AS bigint)'),v)
                                    self.retention_reject(c,self.destructive_statements()['member'],v)
                                finally:nested.rollback()
                            for path,fk in [('organization','org_member_org_id_fkey'),('profile','org_member_user_id_fkey')]:
                                self.retention_reject(c,self.destructive_statements()[path],v,'23503',fk)
                            if retired:
                                for statement in self.retirement_statements().values():
                                    self.retirement_reject(c,statement,v)
                                    self.retirement_reject(c,statement.replace('SET deleted_at=','SET is_owner=NOT is_owner,deleted_at='),v)
                                for value in ['NULL',"deleted_at+interval '1 second'"]:
                                    self.retirement_reject(c,"UPDATE identity.org_member SET is_owner=NOT is_owner,deleted_at=CASE WHEN id=CAST(:member AS bigint) THEN "+value+" ELSE deleted_at END WHERE id IN(CAST(:member AS bigint),CAST(:other_member AS bigint))",v)
                                    self.retirement_reject(c,"WITH changed AS (UPDATE identity.org_member SET is_owner=NOT is_owner WHERE id=CAST(:other_member AS bigint) RETURNING id) UPDATE identity.org_member SET deleted_at="+value+" WHERE id=CAST(:member AS bigint) AND EXISTS(SELECT 1 FROM changed)",v)
                                self.retirement_reject(c,self.seed_statement(),v)
                            row=c.execute(text('SELECT to_jsonb(t) FROM identity.org_member t WHERE id=CAST(:member AS bigint)'),v).scalar_one()
                            assert c.execute(text('UPDATE identity.org_member SET id=id,org_id=org_id,user_id=user_id,deleted_at=deleted_at,revision=999 WHERE id=CAST(:member AS bigint) RETURNING to_jsonb(org_member)'),v).scalar_one()==row
                            if retired:
                                # Same instant as the retained 2001-01-01 UTC fixture, with a different offset.
                                assert c.execute(text("UPDATE identity.org_member SET deleted_at='2001-01-01 02:00:00+02'::timestamptz,revision=999 WHERE id=CAST(:member AS bigint) RETURNING to_jsonb(org_member)"),v).scalar_one()==row
                            for change in ['is_owner=NOT is_owner','updated_by=CAST(:other AS uuid)',"updated_at='2001-01-01'::timestamptz"]:
                                changed=c.execute(text('UPDATE identity.org_member SET '+change+' WHERE id=CAST(:member AS bigint) RETURNING to_jsonb(org_member)'),v).scalar_one()
                                assert changed['revision']==row['revision']+1 and changed['deleted_at']==row['deleted_at'];row=changed
                            if not retired:
                                changed=c.execute(text("UPDATE identity.org_member SET deleted_at='2002-01-01'::timestamptz WHERE id=CAST(:member AS bigint) RETURNING to_jsonb(org_member)"),v).scalar_one()
                                assert changed['revision']==row['revision']+1 and changed['deleted_at'].startswith('2002-01-01')
                    with self.execution(c,v):
                        row=c.execute(text("INSERT INTO identity.org_member(id,org_id,user_id,deleted_at,revision) VALUES(CAST(:member AS bigint)+1000000,CAST(:spare_org AS uuid),CAST(:spare AS uuid),'2000-01-01'::timestamptz,999) RETURNING to_jsonb(org_member)"),v).scalar_one()
                        assert row['revision']==1 and row['deleted_at'].startswith('2000-01-01')
                        assert c.execute(text('UPDATE identity.org_member SET deleted_at=deleted_at,revision=999 WHERE id=CAST(:member AS bigint)+1000000 RETURNING to_jsonb(org_member)'),v).scalar_one()==row
                        self.retirement_reject(c,'UPDATE identity.org_member SET deleted_at=NULL WHERE id=CAST(:member AS bigint)+1000000',v)
                        self.service_truncate_denial(c,v)
                    self.seed_compatibility(c,v);self.read_compatibility(c,v)
                    for role in ['authenticated','access_runtime']:
                        with self.execution(c,v,role):
                            for statement in ['UPDATE identity.org_member SET deleted_at=NULL','UPDATE identity.org_member SET deleted_at=now()',self.seed_statement(),'DELETE FROM identity.org_member','TRUNCATE identity.org_member CASCADE']:
                                self.reject(c,statement,v,'42501',None,None)
            finally:db.dispose()
        self.auth_truncation(case,v);self.admin_restart_truncation(case);self.auth_fk_refusal(case,v);self.overflow(v)
        assert self.data_state(case)==before
        self.passed('membership-retirement-write-matrix',one_way_direct_multirow_cte_upsert=True,unchanged_rows_roles_audit=True,
            active_mutable_insert_legacy_timestamp_noop_revision=True,readers_binding_retention=True,browser_runtime_denied=True,rollback_only=True)

    def overflow(self,v):
        db=engine(self.private['owner_urls']['clean'])
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    import importlib.util
                    path=baseline.HERE/'versions/0013_membership_retirement.py'
                    spec=importlib.util.spec_from_file_location('retirement_overflow_source',path)
                    revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
                    sql=revision.MEMBERSHIP_RETIREMENT_SQL
                    c.exec_driver_sql(sql.replace('NEW.revision := OLD.revision;','NEW.revision := 9223372036854775807;'),execution_options={'no_parameters':True})
                    c.execute(text('UPDATE identity.org_member SET revision=revision WHERE id=CAST(:member AS bigint)'),v)
                    c.exec_driver_sql(sql,execution_options={'no_parameters':True})
                    assert c.execute(text('UPDATE identity.org_member SET revision=1 WHERE id=CAST(:member AS bigint) RETURNING revision'),v).scalar_one()==9223372036854775807
                    for statement in ['UPDATE identity.org_member SET is_owner=NOT is_owner WHERE id=CAST(:member AS bigint)','UPDATE identity.org_member SET deleted_at=now() WHERE id=CAST(:member AS bigint)']:
                        self.reject(c,statement,v,'23514','identity_membership_revision_exhausted','org_member_revision_positive')
                finally:tx.rollback()
        finally:db.dispose()

    @contextmanager
    def failure_fixture(self,case):
        state_sql="""SELECT 'function',p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.proname='synthetic_membership_retirement_failure'
            UNION ALL SELECT 'event_trigger',evtname FROM pg_event_trigger WHERE evtname='synthetic_membership_retirement_failure'
            UNION ALL SELECT 'sequence',c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relname='synthetic_membership_retirement_failure_marker' ORDER BY 1,2"""
        before=self.admin_sql(case,state_sql);assert before==[],'membership_retirement_failure_fixture_already_exists'
        marker_sql='SELECT last_value,is_called FROM public.synthetic_membership_retirement_failure_marker'
        create="""CREATE SEQUENCE public.synthetic_membership_retirement_failure_marker START WITH 1;
            REVOKE ALL ON SEQUENCE public.synthetic_membership_retirement_failure_marker FROM PUBLIC,anon,authenticated,service_role,access_runtime;
            GRANT USAGE ON SEQUENCE public.synthetic_membership_retirement_failure_marker TO identity_migrator;
            CREATE FUNCTION public.synthetic_membership_retirement_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN
            IF position('identity_membership_retirement_immutable' IN pg_get_functiondef('identity.guard_org_member_revision()'::regprocedure))>0 THEN
                PERFORM pg_catalog.nextval('public.synthetic_membership_retirement_failure_marker'::regclass);
                RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_membership_retirement_failure';
            END IF; END $$;
            CREATE EVENT TRIGGER synthetic_membership_retirement_failure ON ddl_command_end WHEN TAG IN ('CREATE FUNCTION') EXECUTE FUNCTION public.synthetic_membership_retirement_failure();"""
        cleanup='DROP EVENT TRIGGER IF EXISTS synthetic_membership_retirement_failure; DROP FUNCTION IF EXISTS public.synthetic_membership_retirement_failure(); DROP SEQUENCE IF EXISTS public.synthetic_membership_retirement_failure_marker'
        self.witness('membership-retirement-event-restoration-required',{'case':case,'before':before,'create':create,'cleanup':cleanup})
        verified=False
        def verify_fired():
            nonlocal verified
            marker=self.admin_sql(case,marker_sql)
            assert marker==[(1,True)],'membership_retirement_failure_fixture_not_fired'
            if not verified:
                self.witness('membership-retirement-event-fired',{'case':case,'marker_before':[1,False],'marker_after':list(marker[0]),'new_guard_observed':True})
                verified=True
        with self.restoration_signals():
            try:
                self.admin_sql(case,create)
                assert self.admin_sql(case,marker_sql)==[(1,False)],'membership_retirement_failure_marker_initially_called'
                yield verify_fired
                verify_fired()
            finally:
                for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,signal.SIG_IGN)
                self.admin_sql(case,cleanup)
                assert self.admin_sql(case,state_sql)==before,'membership_retirement_failure_fixture_not_restored'
                self.witness('membership-retirement-event-restored',{'case':case,'exact_objects':True})

    def function_drift_refusal(self):
        case='unknown';before,catalog=self.data_state(case),self.snapshot(case)
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    assert c.execute(text('SELECT version_num FROM identity.alembic_version')).scalar_one()=='identity_0012'
                    rows=self.state(c)
                    definition=next(row[4] for row in catalog['functions'] if row[:3]==['identity','guard_org_member_revision',''])
                    c.exec_driver_sql(definition.replace('BEGIN\n','BEGIN\n    -- synthetic source drift\n',1),execution_options={'no_parameters':True})
                    changed=baseline.target_catalog_snapshot(c)
                    assert {key for key in catalog if catalog[key]!=changed[key]}=={'functions'}
                    try:baseline.preflight(c,'clean')
                    except baseline.BaselineError as error:assert str(error)=='identity_catalog_mismatch:functions'
                    else:raise AssertionError('membership_retirement_function_drift_accepted')
                    assert baseline.target_catalog_snapshot(c)==changed and self.state(c)==rows
                    assert c.execute(text('SELECT version_num FROM identity.alembic_version')).scalar_one()=='identity_0012'
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state(case)==before and self.snapshot(case)==catalog
        self.passed('membership-retirement-function-drift-refused',rollback_only=True,no_normalization=True)

    def upgrades_and_failures(self):
        self.validate_targets();self.prior_evidence(PREVIOUS_COMMIT,PREVIOUS_FILES,'identity_0012')
        self.command('membership-retirement-clean','clean');self.compatibility();self.writes();self.command('membership-retirement-repeat','clean')
        self.legacy('legacy');self.original_ledger('legacy')
        for case in ['legacy','previous']:
            self.row_fixtures(case)
            before=self.data_state(case,membership_without_revision=case=='legacy');external=self.external_state(case)
            acl=self.sql(case,retention.FUNCTION_ACL) if case=='previous' else None
            self.command('membership-retirement-'+case,case,mode='adopt' if case=='legacy' else 'clean')
            after=self.data_state(case,membership_without_revision=case=='legacy')
            assert all(after[key]==value for key,value in before.items() if key!='identity.alembic_version')
            assert (acl is None or self.sql(case,retention.FUNCTION_ACL)==acl) and self.external_state(case)==external
        with self.failure_fixture('failure') as verify_fired:
            before,catalog=self.data_state('failure'),self.snapshot('failure')
            self.command('membership-retirement-create-function-rollback','failure',expected='identity_migration_failed_requires_reconciliation')
            verify_fired()
            assert self.data_state('failure')==before and self.snapshot('failure')==catalog
            assert self.sql('failure','SELECT version_num FROM identity.alembic_version')==[('identity_0012',)]
        self.command('membership-retirement-after-rollback','failure');self.command('membership-retirement-unsafe-clean','unsafe')
        with self.acl_fixture('unsafe','GRANT INSERT ON identity.users TO authenticated','REVOKE INSERT ON identity.users FROM authenticated','GRANT INSERT (id, username) ON identity.users TO authenticated'):
            before,catalog=self.data_state('unsafe'),self.snapshot('unsafe')
            self.command('membership-retirement-drift-refused','unsafe',expected='identity_profile_column_privileges_mismatch')
            assert self.data_state('unsafe')==before and self.snapshot('unsafe')==catalog
        self.command('membership-retirement-drift-reconciled','unsafe');self.function_drift_refusal()
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
                    else:raise AssertionError('membership_retirement_unknown_history_accepted')
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state('unknown')==before and self.snapshot('unknown')==catalog
        self.passed('membership-retirement-migration-matrix',clean_adopt_exact12_repeat=True,exact_acl_preservation=True,
            after_create_function_rollback_recovery=True,drift_unknown_refused=True)


def main():
    if not __debug__:raise RuntimeError('membership_retirement_qualification_optimized_python_prohibited')
    proof,private=fixture();q=MembershipRetirementQualification(proof,private)
    if sys.argv[1:]==['--characterize']:q.validate_targets();q.characterize()
    elif not sys.argv[1:]:q.upgrades_and_failures()
    else:raise RuntimeError('membership_retirement_qualification_arguments_invalid')


if __name__=='__main__':
    try:main()
    except Exception as error:
        print('membership_retirement_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None
