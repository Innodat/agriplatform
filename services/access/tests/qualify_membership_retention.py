"""Source-bound synthetic history retention proof; database execution belongs to root."""
from pathlib import Path
from contextlib import contextmanager
from hashlib import sha256
import json
import signal
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_membership_binding as binding
from qualify_identity_baseline import baseline,engine,fixture,text

PREVIOUS_COMMIT='e124da80b9c0a3bbd3951d4ec1f248009502ac7d'
PREVIOUS_FILES=binding.PREVIOUS_FILES | {'versions/0011_membership_binding.py','membership-binding-reference.json'}
FUNCTION_ACL=binding.FUNCTION_ACL
REQUIRED_CASES=frozenset({'characterization','membership_retention_reference','clean','legacy','previous','failure','unsafe','unknown','native'})
FK_DEFINITIONS={
    ('org_member','org_member_org_id_fkey'):'FOREIGN KEY (org_id) REFERENCES identity.org(id) ON DELETE CASCADE',
    ('org_member','org_member_user_id_fkey'):'FOREIGN KEY (user_id) REFERENCES identity.users(id) ON DELETE CASCADE',
    ('member_role','member_role_member_id_fkey'):'FOREIGN KEY (member_id) REFERENCES identity.org_member(id) ON DELETE CASCADE',
}


class MembershipRetentionQualification(binding.MembershipBindingQualification):
    def validate_targets(self):
        # Reuse exact numeric/UUID/headroom validation without publishing another fixture.
        for group in ['owner_urls','runtime_urls','databases']:
            assert set(self.private[group])==REQUIRED_CASES,'membership_retention_cases_invalid'
        self.inputs=json.loads((self.proof/'member-retention-fixtures.json').read_text())
        assert set(self.inputs)=={'characterization','clean'}
        for row in self.inputs.values():
            assert set(row)=={'account','other','spare','org','other_org','spare_org','member','other_member','other_org_member','role','deleted_role'}
            keys=['account','other','spare','org','other_org','spare_org']
            assert len({row[k] for k in keys})==6
            for key in keys:assert str(binding.uuid.UUID(row[key]))==row[key] and binding.uuid.UUID(row[key]).int
            for key in ['member','other_member','other_org_member','role','deleted_role']:
                assert isinstance(row[key],str) and row[key].isascii() and row[key].isdecimal() and 0<int(row[key])<=9223372036854775807
            assert int(row['role'])!=int(row['deleted_role']),'membership_retention_fixture_roles_not_distinct'
            assert len({int(row[k]) for k in ['member','other_member','other_org_member']})==3
            assert int(row['member'])<=9223372036854775807-1000000

    @staticmethod
    def state(c):
        rows=binding.MembershipBindingQualification.state(c)
        rows.update({table:[row[0] for row in c.execute(text('SELECT to_jsonb(t) FROM identity.'+table+' t ORDER BY id'))]
            for table in ['org','users']})
        return rows

    def fixture_rows(self,case):
        super().fixture_rows(case)
        v=self.inputs[case]
        rows=self.sql(case,"SELECT id::text,member_id::text,role::text,deleted_at IS NULL FROM identity.member_role WHERE id IN(CAST(:role AS bigint),CAST(:deleted_role AS bigint))",v)
        expected={(str(int(v['role'])),str(int(v['member'])),'admin',True),
            (str(int(v['deleted_role'])),str(int(v['member'])),'employee',False)}
        assert len(rows)==2 and set(map(tuple,rows))==expected,'membership_retention_fixture_role_rows_mismatch'

    def characterization_binding(self):
        return {'proof':str(self.proof.resolve()),'run_id':json.loads((self.proof/'run.json').read_text())['run_id'],
            'fixture_sha256':sha256((self.proof/'member-retention-fixtures.json').read_bytes()).hexdigest()}

    @staticmethod
    def verify_constraints(rows,restrict=False):
        by_key={tuple(row[:2]):row for row in rows}
        for key,definition in FK_DEFINITIONS.items():
            expected=definition.replace('ON DELETE CASCADE','ON DELETE RESTRICT') if restrict else definition
            assert list(by_key[key][2:])==[expected,True,False,False],'membership_retention_prior_fk_definition_mismatch'

    def characterize(self):
        case='characterization';v=self.inputs[case];self.fixture_rows(case)
        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0011',)]
        catalog=self.snapshot(case);self.verify_constraints(catalog['constraints'])
        baseline.compare_catalog(baseline.catalog_fingerprints(catalog),baseline.trusted_membership_binding_reference())
        before=self.data_state(case);observed=[]
        with self.fixture_execution(case):
            db=engine(self.private['runtime_urls'][case])
            try:
                with db.connect() as c:
                    for label,statement in self.destructive_statements().items():
                        if label=='truncate':continue
                        with self.execution(c,v):
                            original=self.state(c)
                            c.execute(text(statement),v)
                            after=self.state(c)
                            lost={row['id'] for row in original['org_member']}-{row['id'] for row in after['org_member']}
                            roles_lost={row['id'] for row in original['member_role']}-{row['id'] for row in after['member_role']}
                            assert int(v['member']) in lost and int(v['role']) in roles_lost
                            observed.append({'path':label,'lane':'restricted_service_role','members_lost':sorted(lost),'roles_lost':sorted(roles_lost)})
                    with self.execution(c,v):self.service_truncate_denial(c,v)
            finally:db.dispose()
        observed.extend(self.auth_truncation(case,v,characterize=True))
        assert self.data_state(case)==before
        self.witness('membership-retention-head11-characterization',{'binding':self.characterization_binding(),
            'head':'identity_0011','unchanged_data':True,'observed':observed,'catalog':catalog})
        self.passed('membership-retention-head11-characterization',real_login='access_runtime',service_role_delete=True,auth_role_truncate=True,service_role_truncate_denied=True,rollback_only=True)

    @staticmethod
    def destructive_statements():
        return {'member':'DELETE FROM identity.org_member WHERE id=CAST(:member AS bigint)',
            'organization':'DELETE FROM identity.org WHERE id=CAST(:org AS uuid)',
            'profile':'DELETE FROM identity.users WHERE id=CAST(:account AS uuid)',
            'truncate':'TRUNCATE identity.org_member CASCADE'}

    def verify_characterization(self,witness):
        assert witness['binding']==self.characterization_binding(),'membership_retention_characterization_stale_fixture'
        assert witness['head']=='identity_0011' and witness['unchanged_data'] is True
        rows=witness['observed'];assert len(rows)==4 and {r['path'] for r in rows}==set(self.destructive_statements())
        v=self.inputs['characterization']
        for row in rows:
            assert row['lane']==('owner_prepared_supabase_auth_admin' if row['path']=='truncate' else 'restricted_service_role')
            assert int(v['member']) in row['members_lost'] and int(v['role']) in row['roles_lost']
        self.verify_constraints(witness['catalog']['constraints'])
        baseline.compare_catalog(baseline.catalog_fingerprints(witness['catalog']),baseline.trusted_membership_binding_reference())

    def compatibility(self):
        current=self.snapshot('clean')
        baseline.compare_catalog(baseline.catalog_fingerprints(current),baseline.trusted_membership_retention_reference())
        witnesses=sorted(self.proof.glob('membership-retention-head11-characterization-*.json'),key=lambda p:p.stat().st_mtime_ns)
        assert witnesses,'membership_retention_missing_head11_characterization'
        witness=json.loads(witnesses[-1].read_text());self.verify_characterization(witness);old=witness['catalog']
        assert old.keys()==current.keys()
        assert {k for k in old if old[k]!=current[k]}=={'constraints','functions','triggers'}
        self.verify_constraints(current['constraints'],True)
        expected=[list(row) for row in old['constraints']]
        for row in expected:
            if tuple(row[:2]) in FK_DEFINITIONS:row[2]=row[2].replace('ON DELETE CASCADE','ON DELETE RESTRICT')
        assert sorted(expected)==sorted(current['constraints']),'membership_retention_unrelated_constraint_changed'
        self.verify_function_delta(old['functions'],current['functions'])
        expected=[list(row) for row in old['triggers']]
        row=next(r for r in expected if r[:3]==['identity','org_member','org_member_revision_guard'])
        row[3]=row[3].replace('BEFORE INSERT OR UPDATE','BEFORE INSERT OR DELETE OR UPDATE')
        expected.append(['identity','org_member','org_member_history_truncate_guard',
            'CREATE TRIGGER org_member_history_truncate_guard BEFORE TRUNCATE ON identity.org_member FOR EACH STATEMENT EXECUTE FUNCTION identity.guard_org_member_revision()','O'])
        assert sorted(expected)==sorted(current['triggers']),'membership_retention_unrelated_trigger_changed'
        # Exact body delta, not merely a changed function fingerprint.
        helper=lambda rows:next(r[4] for r in rows if r[:3]==['identity','guard_org_member_revision',''])
        insertion="    IF TG_OP IN ('DELETE', 'TRUNCATE') THEN\n        RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'identity_membership_history_retained',\n            CONSTRAINT = 'org_member_history_retained';\n    END IF;\n"
        assert helper(current['functions'])==helper(old['functions']).replace('BEGIN\n','BEGIN\n'+insertion,1)
        self.passed('membership-retention-exact-catalog-delta',only_three_fks_guard_body_row_and_truncate_trigger=True,original_auth_fk_unchanged=True)

    def retention_reject(self,c,statement,v,state='23514',constraint='org_member_history_retained'):
        before=self.state(c)
        self.reject(c,statement,v,state,'identity_membership_history_retained' if state=='23514' else None,constraint)
        if state=='23503':
            # A second savepoint captures the actual named RESTRICT error safely.
            savepoint=c.begin_nested()
            try:c.execute(text(statement),v)
            except Exception as error:assert error.orig.diag.constraint_name==constraint
            else:raise AssertionError('membership_retention_parent_refusal_missing')
            finally:savepoint.rollback()
        assert self.state(c)==before

    def writes(self):
        case='clean';v=self.inputs[case];self.fixture_rows(case);before=self.data_state(case)
        with self.fixture_execution(case):
            db=engine(self.private['runtime_urls'][case])
            try:
                with db.connect() as c:
                    for retired in [False,True]:
                        for roleless in [False,True]:
                            with self.execution(c,v):
                                if retired:c.execute(text('UPDATE identity.org_member SET deleted_at=now() WHERE id=CAST(:member AS bigint)'),v)
                                if roleless:c.execute(text('DELETE FROM identity.member_role WHERE member_id=CAST(:member AS bigint)'),v)
                                for statement in [self.destructive_statements()['member'],
                                    'DELETE FROM identity.org_member WHERE id IN(CAST(:member AS bigint),CAST(:other_member AS bigint))',
                                    'WITH changed AS (UPDATE identity.org_member SET is_owner=NOT is_owner WHERE id=CAST(:other_member AS bigint) RETURNING id) DELETE FROM identity.org_member WHERE id=CAST(:member AS bigint) AND EXISTS(SELECT 1 FROM changed)']:
                                    self.retention_reject(c,statement,v)
                                for path,fk in [('organization','org_member_org_id_fkey'),('profile','org_member_user_id_fkey')]:
                                    self.retention_reject(c,self.destructive_statements()[path],v,'23503',fk)
                    with self.execution(c,v):self.service_truncate_denial(c,v)
                    for role in ['authenticated','access_runtime']:
                        with self.execution(c,v,role):
                            for statement in ['DELETE FROM identity.org_member','TRUNCATE identity.org_member CASCADE']:
                                self.reject(c,statement,v,'42501',None,None)
            finally:db.dispose()
        self.auth_truncation(case,v)
        self.admin_restart_truncation(case)
        self.auth_fk_refusal(case,v)
        assert self.data_state(case)==before
        # Reuse all actual binding, revision overflow, seed/unretirement, mutable and reader proofs.
        super().writes()
        self.passed('membership-retention-destructive-matrix',active_retired_roleless_multirow=True,parents_restrict=True,
            truncate_cascade=True,unchanged_rows_roles_audit=True,rollback_only=True,standalone_legacy_role_dml_preserved=True)

    def service_truncate_denial(self,c,v):
        assert c.execute(text("SELECT current_user,has_table_privilege(current_user,'identity.org_member','TRUNCATE')")).one()==('service_role',False)
        self.reject(c,'TRUNCATE identity.org_member CASCADE',v,'42501',None,None)

    def auth_truncation(self,case,v,characterize=False):
        """Existing Auth-role TRUNCATE privilege; no runtime edge or privilege grant."""
        db=self.admin(case);observed=[]
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    administrator=c.execute(text('SELECT current_user')).scalar_one()
                    for retired in ([False] if characterize else [False,True]):
                        for roleless in ([False] if characterize else [False,True]):
                            preparation=c.begin_nested()
                            try:
                                if retired:c.execute(text('UPDATE identity.org_member SET deleted_at=now() WHERE id=CAST(:member AS bigint)'),v)
                                if roleless:c.execute(text('DELETE FROM identity.member_role WHERE member_id=CAST(:member AS bigint)'),v)
                                forms=[('org_member','TRUNCATE identity.org_member CASCADE')] if characterize else [
                                    ('org_member','TRUNCATE identity.org_member CASCADE'),
                                    ('org','TRUNCATE identity.org CASCADE'),
                                    ('org','TRUNCATE identity.org, identity.org_member, identity.member_role CONTINUE IDENTITY CASCADE')]
                                for table,statement in forms:
                                    before=self.state(c);sequences=self.sequence_state(c);savepoint=c.begin_nested()
                                    try:
                                        c.execute(text('SET LOCAL ROLE supabase_auth_admin'))
                                        assert c.execute(text('SELECT current_user')).scalar_one()=='supabase_auth_admin'
                                        for target in {table,'org_member','member_role'}:
                                            assert c.execute(text("SELECT has_table_privilege(current_user,:table,'TRUNCATE')"),{'table':'identity.'+target}).scalar_one() is True
                                        try:c.execute(text(statement))
                                        except Exception as error:
                                            if characterize:raise
                                            assert error.orig.sqlstate=='23514'
                                            assert error.orig.diag.message_primary=='identity_membership_history_retained'
                                            assert error.orig.diag.constraint_name=='org_member_history_retained'
                                        else:
                                            assert characterize,'membership_retention_truncate_refusal_missing'
                                            after={name:[r[0] for r in c.execute(text('SELECT to_jsonb(t) FROM identity.'+name+' t ORDER BY id'))]
                                                for name in ['org_member','member_role']}
                                            lost={r['id'] for r in before['org_member']}-{r['id'] for r in after['org_member']}
                                            roles_lost={r['id'] for r in before['member_role']}-{r['id'] for r in after['member_role']}
                                            assert int(v['member']) in lost and int(v['role']) in roles_lost
                                            observed.append({'path':'truncate','lane':'owner_prepared_supabase_auth_admin','members_lost':sorted(lost),'roles_lost':sorted(roles_lost)})
                                    finally:savepoint.rollback()
                                    assert c.execute(text('SELECT current_user')).scalar_one()==administrator
                                    assert self.state(c)==before,'membership_retention_auth_truncate_partial_effects'
                                    assert self.sequence_state(c)==sequences,'membership_retention_auth_truncate_sequence_changed'
                            finally:preparation.rollback()
                    before=self.state(c);savepoint=c.begin_nested()
                    try:
                        c.execute(text('SET LOCAL ROLE supabase_auth_admin'))
                        assert c.execute(text('SELECT current_user')).scalar_one()=='supabase_auth_admin'
                        assert c.execute(text("SELECT has_table_privilege(current_user,'identity.users','TRUNCATE')")).scalar_one() is False
                        try:c.execute(text('TRUNCATE identity.users CASCADE'))
                        except Exception as error:assert error.orig.sqlstate=='42501'
                        else:raise AssertionError('membership_retention_auth_profile_truncate_permission_changed')
                    finally:savepoint.rollback()
                    assert c.execute(text('SELECT current_user')).scalar_one()==administrator
                    assert self.state(c)==before
                finally:tx.rollback()
        finally:db.dispose()
        self.passed('membership-retention-owner-prepared-auth-role-truncate',characterization=characterize,
            existing_effective_privilege=True,no_runtime_authority_claim=True,rollback_only=True)
        return observed

    @staticmethod
    def sequence_state(c):
        names=[r[0] for r in c.execute(text("SELECT format('%I.%I',n.nspname,c.relname) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='identity' AND c.relkind='S' ORDER BY c.relname"))]
        return {name:tuple(c.execute(text('SELECT last_value,is_called FROM '+name)).one()) for name in names}

    def admin_restart_truncation(self,case):
        """Owner administrator lane: RESTART requires sequence ownership beyond Auth role."""
        db=self.admin(case)
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    assert c.execute(text('SELECT current_user')).scalar_one()=='supabase_admin'
                    before=self.state(c);sequences=self.sequence_state(c)
                    for statement in ['TRUNCATE identity.org_member RESTART IDENTITY CASCADE',
                        'TRUNCATE identity.org, identity.org_member, identity.member_role RESTART IDENTITY CASCADE']:
                        self.retention_reject(c,statement,{})
                        assert self.state(c)==before and self.sequence_state(c)==sequences
                finally:tx.rollback()
        finally:db.dispose()
        self.passed('membership-retention-owner-admin-restart-identity',runtime_authority_claim=False,
            rows_and_sequences_unchanged=True,rollback_only=True)

    def overflow(self,v):
        """Only rollback fixture DDL supplies unreachable max revision test input."""
        db=engine(self.private['owner_urls']['clean'])
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    import importlib.util
                    path=baseline.HERE/'versions/0012_membership_retention.py'
                    spec=importlib.util.spec_from_file_location('binding_overflow_source',path)
                    revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
                    guard_sql='CREATE OR REPLACE FUNCTION'+revision.MEMBERSHIP_RETENTION_SQL.split('CREATE OR REPLACE FUNCTION',1)[1].split('$revision_guard$;',1)[0]+'$revision_guard$;'
                    seed_sql=guard_sql.replace('NEW.revision := OLD.revision;', 'NEW.revision := 9223372036854775807;')
                    c.exec_driver_sql(seed_sql,execution_options={'no_parameters':True})
                    c.execute(text('UPDATE identity.org_member SET revision=revision WHERE id=CAST(:member AS bigint)'),v)
                    c.exec_driver_sql(guard_sql,execution_options={'no_parameters':True})
                    assert c.execute(text('UPDATE identity.org_member SET id=id,revision=1 WHERE id=CAST(:member AS bigint) RETURNING revision'),v).scalar_one()==9223372036854775807
                    for statement in ['UPDATE identity.org_member SET is_owner=NOT is_owner WHERE id=CAST(:member AS bigint)',
                                      'UPDATE identity.org_member SET is_owner=NOT is_owner WHERE id IN(CAST(:member AS bigint),CAST(:other_member AS bigint))']:
                        self.reject(c,statement,v,'23514','identity_membership_revision_exhausted','org_member_revision_positive')
                    self.reject(c,'UPDATE identity.org_member SET user_id=CAST(:spare AS uuid) WHERE id=CAST(:member AS bigint)',v)
                finally:tx.rollback()
        finally:db.dispose()

    def auth_fk_refusal(self,case,v):
        """Original NO ACTION FK checked by administrator, never runtime authority."""
        db=self.admin(case)
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    self.retention_reject(c,'DELETE FROM auth.users WHERE id=CAST(:account AS uuid)',v,'23503','users_id_fkey')
                finally:tx.rollback()
        finally:db.dispose()
        self.passed('membership-retention-original-auth-fk-owner-only',original_no_action=True,
            rollback_only=True,runtime_authority_claim=False)

    @contextmanager
    def failure_fixture(self,case,phase='first_fk'):
        assert phase in {'first_fk','late_trigger'},'membership_retention_failure_phase_invalid'
        state_sql="""SELECT 'function',p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.proname='synthetic_membership_retention_failure'
            UNION ALL SELECT 'event_trigger',evtname FROM pg_event_trigger WHERE evtname='synthetic_membership_retention_failure' ORDER BY 1,2"""
        before=self.admin_sql(case,state_sql);assert before==[],'membership_retention_failure_fixture_already_exists'
        create="""CREATE FUNCTION public.synthetic_membership_retention_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN
            IF EXISTS(SELECT 1 FROM pg_constraint WHERE conrelid='identity.org_member'::regclass AND conname='org_member_org_id_fkey' AND confdeltype='r') THEN
                RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_membership_retention_failure';
            END IF; END $$;
            CREATE EVENT TRIGGER synthetic_membership_retention_failure ON ddl_command_end WHEN TAG IN ('ALTER TABLE') EXECUTE FUNCTION public.synthetic_membership_retention_failure();"""
        if phase=='late_trigger':
            create=create.replace("EXISTS(SELECT 1 FROM pg_constraint WHERE conrelid='identity.org_member'::regclass AND conname='org_member_org_id_fkey' AND confdeltype='r')",
                "EXISTS(SELECT 1 FROM pg_trigger WHERE tgrelid='identity.org_member'::regclass AND tgname='org_member_history_truncate_guard' AND NOT tgisinternal)").replace("WHEN TAG IN ('ALTER TABLE')","WHEN TAG IN ('CREATE TRIGGER')")
        cleanup='DROP EVENT TRIGGER IF EXISTS synthetic_membership_retention_failure; DROP FUNCTION IF EXISTS public.synthetic_membership_retention_failure()'
        self.witness('membership-retention-event-restoration-required',{'case':case,'phase':phase,'before':before,'create':create,'cleanup':cleanup})
        with self.restoration_signals():
            try:self.admin_sql(case,create);yield
            finally:
                for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,signal.SIG_IGN)
                self.admin_sql(case,cleanup)
                assert self.admin_sql(case,state_sql)==before,'membership_retention_failure_fixture_not_restored'
                self.witness('membership-retention-event-restored',{'case':case,'phase':phase,'exact_objects':True})

    def conflicting_reader_lock(self):
        case='failure';before,catalog=self.data_state(case),self.snapshot(case)
        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0011',)]
        db=engine(self.private['owner_urls'][case]);elapsed=None
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'; SET LOCAL idle_in_transaction_session_timeout='30s'"))
                    c.execute(text('LOCK TABLE identity.org_member IN ACCESS SHARE MODE'))
                    started=time.monotonic()
                    self.command('membership-retention-conflicting-reader-lock',case,expected='identity_migration_failed_requires_reconciliation')
                    elapsed=time.monotonic()-started
                    assert 0<elapsed<25,'membership_retention_lock_refusal_not_bounded'
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state(case)==before and self.snapshot(case)==catalog
        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0011',)]
        self.passed('membership-retention-conflicting-reader-lock-preserved',elapsed_seconds=elapsed,
            bounded_seconds=25,lock_released=True,unchanged_data_catalog_history=True)

    def fk_drift_refusal(self):
        case='unknown';before,catalog=self.data_state(case),self.snapshot(case)
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    assert c.execute(text('SELECT version_num FROM identity.alembic_version')).scalar_one()=='identity_0011'
                    rows=self.state(c)
                    c.execute(text('ALTER TABLE identity.org_member DROP CONSTRAINT org_member_org_id_fkey'))
                    c.execute(text('ALTER TABLE identity.org_member ADD CONSTRAINT org_member_org_id_fkey FOREIGN KEY(org_id) REFERENCES identity.org(id) ON DELETE RESTRICT'))
                    changed=baseline.target_catalog_snapshot(c)
                    assert {key for key in catalog if catalog[key]!=changed[key]}=={'constraints'}
                    try:baseline.preflight(c,'clean')
                    except baseline.BaselineError as error:assert str(error)=='identity_catalog_mismatch:constraints'
                    else:raise AssertionError('membership_retention_fk_drift_accepted')
                    assert baseline.target_catalog_snapshot(c)==changed and self.state(c)==rows
                    assert c.execute(text('SELECT version_num FROM identity.alembic_version')).scalar_one()=='identity_0011'
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state(case)==before and self.snapshot(case)==catalog
        self.passed('membership-retention-actual-fk-drift-refused',rollback_only=True,
            subprocess_migration_claim=False,no_normalization=True)

    def upgrades_and_failures(self):
        self.validate_targets();self.prior_evidence(PREVIOUS_COMMIT,PREVIOUS_FILES,'identity_0011')
        self.command('membership-retention-clean','clean');self.compatibility();self.writes();self.command('membership-retention-repeat','clean')
        self.legacy('legacy');self.original_ledger('legacy')
        for case in ['legacy','previous']:
            self.row_fixtures(case)
            before=self.data_state(case,membership_without_revision=case=='legacy');external=self.external_state(case)
            acl=self.sql(case,FUNCTION_ACL) if case=='previous' else None
            self.command('membership-retention-'+case,case,mode='adopt' if case=='legacy' else 'clean')
            after=self.data_state(case,membership_without_revision=case=='legacy')
            assert all(after[key]==value for key,value in before.items() if key!='identity.alembic_version')
            assert (acl is None or self.sql(case,FUNCTION_ACL)==acl) and self.external_state(case)==external
        self.conflicting_reader_lock()
        for phase in ['first_fk','late_trigger']:
            with self.failure_fixture('failure',phase):
                before,catalog=self.data_state('failure'),self.snapshot('failure')
                self.command('membership-retention-'+phase+'-rollback','failure',expected='identity_migration_failed_requires_reconciliation')
                assert self.data_state('failure')==before and self.snapshot('failure')==catalog
                assert self.sql('failure','SELECT version_num FROM identity.alembic_version')==[('identity_0011',)]
        self.command('membership-retention-after-rollback','failure');self.command('membership-retention-unsafe-clean','unsafe')
        with self.acl_fixture('unsafe','GRANT INSERT ON identity.users TO authenticated','REVOKE INSERT ON identity.users FROM authenticated',
                'GRANT INSERT (id, username) ON identity.users TO authenticated'):
            before,catalog=self.data_state('unsafe'),self.snapshot('unsafe')
            self.command('membership-retention-drift-refused','unsafe',expected='identity_profile_column_privileges_mismatch')
            assert self.data_state('unsafe')==before and self.snapshot('unsafe')==catalog
        self.command('membership-retention-drift-reconciled','unsafe')
        self.fk_drift_refusal()
        before=self.data_state('unknown');catalog=self.snapshot('unknown')
        db=engine(self.private['owner_urls']['unknown'])
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    c.execute(text("UPDATE identity.alembic_version SET version_num='identity_unknown'"))
                    try:baseline.preflight(c,'clean')
                    except baseline.BaselineError as error:assert str(error)=='identity_unknown_history'
                    else:raise AssertionError('membership_binding_unknown_history_accepted')
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state('unknown')==before and self.snapshot('unknown')==catalog
        self.passed('membership-retention-unknown-direct-owner-preflight',rollback_only=True,subprocess_migration_claim=False)
        self.passed('membership-retention-migration-matrix',clean_adopt_head11_repeat=True,exact_acl_preservation=True,mid_revision_rollback=True,drift_and_unknown_refused=True)


def main():
    if not __debug__:raise RuntimeError('membership_retention_qualification_optimized_python_prohibited')
    proof,private=fixture();q=MembershipRetentionQualification(proof,private)
    if sys.argv[1:]==['--characterize']:q.validate_targets();q.characterize()
    elif not sys.argv[1:]:q.upgrades_and_failures()
    else:raise RuntimeError('membership_retention_qualification_arguments_invalid')


if __name__=='__main__':
    try:main()
    except Exception as error:
        print('membership_retention_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None
