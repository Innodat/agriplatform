"""Synthetic profile column proof, consuming root-prepared Auth/profile fixtures.

Temporary SET-only role edges model PostgREST database execution, not JWT/provider
verification. No infrastructure, login, credential or Auth account is created here.
"""
from contextlib import contextmanager
from pathlib import Path
import sys
import uuid
import json
import signal
import os

sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_current_account_actor as previous
from qualify_current_account_actor import ProjectionQualification
from qualify_organization_targets import PREVIOUS_FILES as HEAD6_FILES
from qualify_identity_baseline import baseline, engine, fixture, text, sha

PREVIOUS_COMMIT='630d1ae86db175c10806a3c3e3662962052aa978'
PREVIOUS_FILES=HEAD6_FILES | {'versions/0007_organization_targets.py','target-reference.json'}
previous.PREVIOUS_PYTHON=Path(sys.executable)
REQUIRED_CASES=frozenset({'characterization','profile_reference','clean','legacy','previous','failure','unsafe','unknown','native'})
EDGE_SQL="""SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),pg_get_userbyid(grantor),admin_option,
    to_jsonb(pg_auth_members)->>'inherit_option',to_jsonb(pg_auth_members)->>'set_option'
    FROM pg_auth_members WHERE pg_get_userbyid(member)='access_runtime'
    AND pg_get_userbyid(roleid) IN ('authenticated','service_role') ORDER BY 1,2,3"""
PROFILE_SQL='SELECT to_jsonb(t) FROM identity.users t WHERE id=CAST(:id AS uuid)'
PROFILE_ACL_SQL="""SELECT 'table',relacl::text FROM pg_class WHERE oid='identity.users'::regclass
    UNION ALL SELECT attname,attacl::text FROM pg_attribute
    WHERE attrelid='identity.users'::regclass AND attnum>0 AND NOT attisdropped ORDER BY 1"""
PROTECTED={'id':'CAST(:other AS uuid)','actor_key':"'synthetic-profile-key'",'is_system':'true',
    'is_platform_admin':'true','created_by':'CAST(:account AS uuid)','created_at':'now()',
    'updated_by':'CAST(:account AS uuid)','updated_at':'now()'}


class ProfileQualification(ProjectionQualification):
    def validate_targets(self):
        for group in ['owner_urls','runtime_urls','databases']:
            assert set(self.private[group])==REQUIRED_CASES,'profile_cases_invalid'
        self.inputs=json.loads((self.proof/'profile-fixtures.json').read_text())
        assert set(self.inputs)=={'characterization','clean'}
        for row in self.inputs.values():
            assert set(row)=={'account','other','missing'}
            assert len(set(row.values()))==3
            assert all(str(uuid.UUID(value))==value and uuid.UUID(value).int for value in row.values())

    def witness(self,name,value):
        path=self.proof/(name+'-'+str(uuid.uuid4())+'.json')
        with path.open('x',encoding='utf-8') as output:
            os.chmod(path,0o600);json.dump(value,output,sort_keys=True)
            output.flush();os.fsync(output.fileno())
        return path

    def _bounded_sql(self,db,statement,values=None):
        try:
            with db.begin() as c:
                c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                result=c.execute(text(statement),values or {})
                return result.fetchall() if result.returns_rows else []
        finally:db.dispose()

    def sql(self,case,statement,values=None,role='owner_urls'):
        return self._bounded_sql(engine(self.private[role][case]),statement,values)

    def admin_sql(self,case,statement,values=None):
        return self._bounded_sql(self.admin(case),statement,values)

    @contextmanager
    def restoration_signals(self):
        def interrupted(signum,frame):raise RuntimeError('profile_fixture_interrupted')
        old={sig:signal.getsignal(sig) for sig in [signal.SIGINT,signal.SIGTERM]}
        for sig in old:signal.signal(sig,interrupted)
        try:yield
        finally:
            for sig,handler in old.items():signal.signal(sig,handler)

    @contextmanager
    def acl_fixture(self,case,grant,revoke,restore=None):
        before=self.sql(case,PROFILE_ACL_SQL)
        self.witness('profile-acl-restoration-required',{'case':case,'before':[list(r) for r in before],
            'grant':grant,'revoke':revoke,'restore':restore})
        with self.restoration_signals():
            try:
                self.sql(case,grant)
                yield
            finally:
                for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,signal.SIG_IGN)
                self.sql(case,revoke)
                if restore:self.sql(case,restore)
                after=self.sql(case,PROFILE_ACL_SQL)
                assert after==before,'profile_fixture_acl_not_restored'
                self.witness('profile-acl-restored',{'case':case,'after':[list(r) for r in after],'exact_acl':True})

    @contextmanager
    def failure_fixture(self,case):
        state_sql="""SELECT 'function',p.oid::regprocedure::text FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
            WHERE n.nspname='public' AND p.proname='synthetic_profile_failure'
            UNION ALL SELECT 'event_trigger',evtname FROM pg_event_trigger WHERE evtname='synthetic_profile_failure' ORDER BY 1,2"""
        before=self.admin_sql(case,state_sql)
        assert before==[],'profile_failure_fixture_already_exists'
        create="""CREATE FUNCTION public.synthetic_profile_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN
            IF NOT has_table_privilege('authenticated','identity.users','UPDATE') THEN
                RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_profile_failure';
            END IF; END $$;
            CREATE EVENT TRIGGER synthetic_profile_failure ON ddl_command_end WHEN TAG IN ('REVOKE') EXECUTE FUNCTION public.synthetic_profile_failure();"""
        cleanup='DROP EVENT TRIGGER IF EXISTS synthetic_profile_failure; DROP FUNCTION IF EXISTS public.synthetic_profile_failure()'
        self.witness('profile-event-restoration-required',{'case':case,'before':before,'create':create,'cleanup':cleanup})
        with self.restoration_signals():
            try:
                self.admin_sql(case,create)
                yield
            finally:
                for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,signal.SIG_IGN)
                self.admin_sql(case,cleanup)
                after=self.admin_sql(case,state_sql)
                assert after==before,'profile_failure_fixture_not_restored'
                self.witness('profile-event-restored',{'case':case,'after':after,'exact_objects':True})

    def snapshot(self,case):
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:return baseline.target_catalog_snapshot(c)
        finally:db.dispose()

    @contextmanager
    def fixture_execution(self,case):
        """Exact absent-edge restoration; no inherited/browser login authority."""
        admin=self.admin(case)
        def edges():
            with admin.begin() as c:return [tuple(r) for r in c.execute(text(EDGE_SQL))]
        before=edges();assert before==[], 'profile_fixture_edges_already_present'
        self.witness('profile-role-restoration-required',{'case':case,'login':'access_runtime',
            'roles':['authenticated','service_role'],'before':before,'temporary':'SET TRUE INHERIT FALSE ADMIN FALSE'})
        def change(grant):
            with admin.begin() as c:
                c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                c.execute(text('GRANT authenticated, service_role TO access_runtime WITH INHERIT FALSE, SET TRUE' if grant
                               else 'REVOKE authenticated, service_role FROM access_runtime'))
        def interrupted(signum,frame):raise RuntimeError('profile_fixture_interrupted')
        old={sig:signal.getsignal(sig) for sig in [signal.SIGINT,signal.SIGTERM]}
        for sig in old:signal.signal(sig,interrupted)
        try:
            try:
                change(True)
                current=edges()
                assert {r[0] for r in current}=={'authenticated','service_role'}
                assert len(current)==2 and all(r[1]=='access_runtime' and r[3:]==(False,'false','true') for r in current)
                yield
            finally:
                for sig in old:signal.signal(sig,signal.SIG_IGN)
                change(False)
                assert edges()==before,'profile_fixture_edges_not_restored'
                self.witness('profile-role-restored',{'case':case,'before':before,'after':edges(),'exact_edges':True})
        finally:
            for sig,handler in old.items():signal.signal(sig,handler)
            admin.dispose()
        self.passed('profile-temporary-role-edges-restored',case=case,exact=True,provider_jwt_verification=False)

    @contextmanager
    def role(self,c,account,role='authenticated',admin_claim=False):
        with c.begin():
            c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
            c.execute(text('SET LOCAL ROLE '+role))
            c.execute(text("SELECT set_config('request.jwt.claims',:claims,true),set_config('app.context_kind','user',true),set_config('app.account_id',:account,true)"),
                      {'claims':json.dumps({'sub':account,'role':role,'user_roles':['admin'] if admin_claim else []}), 'account':account})
            assert c.execute(text('SELECT session_user,current_user')).one()==('access_runtime',role)
            yield

    def denied(self,c,statement,values):
        savepoint=c.begin_nested()
        try:c.execute(text(statement),values)
        except Exception as error:assert getattr(getattr(error,'orig',error),'sqlstate',None)=='42501'
        else:raise AssertionError('profile_protected_write_allowed')
        finally:savepoint.rollback()

    def characterize(self):
        """Record actual old behavior before root upgrades any protected source."""
        case='characterization';values=self.inputs[case];account=values['account']
        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0007',)]
        before=self.data_state(case)
        observed=[]
        with self.fixture_execution(case):
            db=engine(self.private['runtime_urls'][case])
            try:
                with db.connect() as c:
                    for statement in ["UPDATE identity.users SET username='synthetic characterization'",
                                      'UPDATE identity.users SET deleted_at=now()',
                                      'UPDATE identity.users SET is_platform_admin=true',
                                      "INSERT INTO identity.users(id,username) VALUES (CAST(:missing AS uuid),'synthetic missing')",
                                      "INSERT INTO identity.users(id,username,is_platform_admin,created_at) VALUES (CAST(:missing AS uuid),'synthetic forge',true,'2000-01-01'::timestamptz)"]:
                        claim=values['missing'] if statement.startswith('INSERT') else account
                        with self.role(c,claim):
                            sp=c.begin_nested()
                            try:
                                result=c.execute(text(statement),values)
                                observed.append({'operation':statement.split()[0], 'protected':'is_platform_admin' in statement,
                                                 'sqlstate':None,'rowcount':result.rowcount})
                            except Exception as error:
                                observed.append({'operation':statement.split()[0], 'protected':'is_platform_admin' in statement,
                                                 'sqlstate':getattr(getattr(error,'orig',error),'sqlstate',None)})
                            finally:sp.rollback()
                    with self.role(c,account):self.denied(c,'SELECT id FROM identity.users',values)
            finally:db.dispose()
        assert self.data_state(case)==before
        rights=self.sql(case,"SELECT has_table_privilege('authenticated','identity.users','INSERT'),has_table_privilege('authenticated','identity.users','UPDATE'),has_any_column_privilege('authenticated','identity.users','SELECT')")
        assert rights==[(True,True,False)]
        assert observed==[{'operation':'UPDATE','protected':False,'sqlstate':None,'rowcount':1},
                          {'operation':'UPDATE','protected':False,'sqlstate':None,'rowcount':1},
                          {'operation':'UPDATE','protected':True,'sqlstate':None,'rowcount':1},
                          {'operation':'INSERT','protected':False,'sqlstate':None,'rowcount':1},
                          {'operation':'INSERT','protected':True,'sqlstate':None,'rowcount':1}]
        self.witness('profile-head7-characterization',{'case':case,'head':'identity_0007','rights':[list(r) for r in rights],
            'observations':observed,'rolled_back':True,'session_user':'access_runtime','current_user':'authenticated'})
        self.passed('profile-head7-characterization',observations=observed,real_login='access_runtime',select_remained_denied=True)

    def writes(self):
        case='clean';values=self.inputs[case];account=values['account'];missing=values['missing']
        # Root-created scratch Auth stub exercises the profile hook; missing has Auth only.
        assert self.sql(case,'SELECT count(*) FROM identity.users WHERE id=CAST(:missing AS uuid)',values)==[(0,)]
        original=self.sql(case,PROFILE_SQL,{'id':account})[0][0]
        audit_sql="SELECT id::text,operation,actor_id::text,record_id FROM identity.audit_log WHERE table_name='users' AND record_id IN (:account,:missing)"
        audit_before={row[0] for row in self.sql(case,audit_sql,values)}
        same_types={'id':'uuid','actor_key':'text','is_system':'boolean','is_platform_admin':'boolean',
                    'created_by':'uuid','created_at':'timestamptz','updated_by':'uuid','updated_at':'timestamptz'}
        with self.fixture_execution(case):
            db=engine(self.private['runtime_urls'][case])
            try:
                with db.connect() as c:
                    before=self.data_state(case)
                    for admin_claim in [False,True]:
                        with self.role(c,account,admin_claim=admin_claim):
                            for field,value in PROTECTED.items():
                                self.denied(c,'UPDATE identity.users SET '+field+'='+value,values)
                                self.denied(c,"UPDATE identity.users SET username='mixed',"+field+'='+value,values)
                            for field,kind in same_types.items():
                                self.denied(c,'UPDATE identity.users SET '+field+'=CAST(:same AS '+kind+')',{'same':original[field]})
                            for statement in ['SELECT id FROM identity.users',"UPDATE identity.users SET username='filtered' WHERE id=CAST(:account AS uuid)",
                                "INSERT INTO identity.users(id,username) VALUES (CAST(:account AS uuid),'upsert') ON CONFLICT(id) DO UPDATE SET is_platform_admin=true",
                                "INSERT INTO identity.users(id,username) VALUES (CAST(:account AS uuid),'upsert') ON CONFLICT(id) DO UPDATE SET username=excluded.username",
                                "INSERT INTO identity.users(id,username) VALUES (CAST(:account AS uuid),'nothing') ON CONFLICT(id) DO NOTHING"]:
                                self.denied(c,statement,values)
                        with self.role(c,missing,admin_claim=admin_claim):
                            for field,value in {**{k:v for k,v in PROTECTED.items() if k!='id'},'deleted_at':'NULL'}.items():
                                self.denied(c,"INSERT INTO identity.users(id,username,"+field+") VALUES (CAST(:missing AS uuid),'forged',"+value+')',values)
                    for spoof in [{'app.context_kind':'setup'}, {'app.account_id':values['other']},
                                  {'app.actor_id':values['other']},
                                  {'app.context_kind':'service','app.account_id':values['other'],
                                   'app.actor_id':values['other'],'app.is_platform_admin':'true'}]:
                        with self.role(c,account):
                            for key,value in spoof.items():
                                c.execute(text('SELECT set_config(:key,:value,true)'),{'key':key,'value':value})
                            self.denied(c,'UPDATE identity.users SET is_platform_admin=true',values)
                            self.denied(c,"INSERT INTO identity.users(id,username,is_system) VALUES (CAST(:missing AS uuid),'spoofed',true)",values)
                    # An existing other profile reaches unique-key arbitration (23505)
                    # before RLS, so use the root-prepared missing profile for this case.
                    with self.role(c,account):
                        self.denied(c,"INSERT INTO identity.users(id,username) VALUES (CAST(:missing AS uuid),'wrong account')",values)
                    # Preserve existing legacy admin RLS authority for supported columns;
                    # JWT role assertions are fixture input, not provider verification.
                    with self.role(c,account,admin_claim=True):
                        sp=c.begin_nested()
                        try:assert c.execute(text("INSERT INTO identity.users(id,username) VALUES (CAST(:missing AS uuid),'legacy admin')"),values).rowcount==1
                        finally:sp.rollback()
                    assert self.data_state(case)==before,'profile_denial_partial_effects'
                    with self.role(c,missing,'service_role'):
                        sp=c.begin_nested()
                        try:
                            service_audit={r[0] for r in c.execute(text(audit_sql),values)}
                            inserted=c.execute(text("INSERT INTO identity.users(id,username,is_system,is_platform_admin,actor_key,created_at,created_by) VALUES (CAST(:missing AS uuid),'Synthetic service profile',true,true,:key,'2000-01-01'::timestamptz,CAST(:missing AS uuid)) RETURNING to_jsonb(users)"),
                                {**values,'key':'synthetic-service-'+missing}).scalar_one()
                            assert inserted['is_system'] is True and inserted['is_platform_admin'] is True
                            assert inserted['actor_key']=='synthetic-service-'+missing
                            assert inserted['created_at'].startswith('2000-01-01') and inserted['created_by']==missing
                            assert inserted['updated_by']==missing and inserted['updated_at'] and inserted['deleted_at'] is None
                            new_audit=[tuple(r) for r in c.execute(text(audit_sql),values) if r[0] not in service_audit]
                            assert len(new_audit)==1 and new_audit[0][1:]==('INSERT',missing,missing)
                        finally:sp.rollback()
                    assert self.data_state(case)==before,'profile_service_insert_not_rolled_back'
                    for statement in ["UPDATE identity.users SET username='Synthetic ordinary profile'",'UPDATE identity.users SET deleted_at=now()','UPDATE identity.users SET deleted_at=NULL']:
                        with self.role(c,account):assert c.execute(text(statement),values).rowcount==1
                        assert c.execute(text('SELECT session_user,current_user')).one()==('access_runtime','access_runtime');c.rollback()
                    with self.role(c,missing):
                        assert c.execute(text("INSERT INTO identity.users(id,username) VALUES (CAST(:missing AS uuid),'Synthetic missing profile')"),values).rowcount==1
                    # No claim leakage on the same connection after commit/rollback/error.
                    for fail in [False,True]:
                        try:
                            with self.role(c,account):
                                c.execute(text('UPDATE identity.users SET username=NULL'))
                                if fail:c.execute(text('SELECT 1/0'))
                                raise RuntimeError('synthetic_rollback')
                        except RuntimeError:pass
                        except Exception as error:assert getattr(error.orig,'sqlstate',None)=='22012'
                        assert c.execute(text('SELECT session_user,current_user')).one()==('access_runtime','access_runtime')
                        assert c.execute(text("SELECT nullif(current_setting('request.jwt.claims',true),'')")).scalar_one() is None;c.rollback()
                    # RLS targets only the claim's profile even without a SELECT grant.
                    other_before=self.sql(case,PROFILE_SQL,{'id':values['other']})
                    with self.role(c,account):
                        sp=c.begin_nested();assert c.execute(text("UPDATE identity.users SET username='self only'"),values).rowcount==1;sp.rollback()
                    assert self.sql(case,PROFILE_SQL,{'id':values['other']})==other_before
                    # Trusted legacy service role retains its protected-column authority.
                    with self.role(c,account,'service_role'):
                        sp=c.begin_nested();assert c.execute(text('UPDATE identity.users SET is_platform_admin=true WHERE id=CAST(:account AS uuid)'),values).rowcount==1;sp.rollback()
                    with self.role(c,account):self.denied(c,"SELECT identity.create_user('unused-synthetic@example.invalid')",values)
                    backend=c.execute(text('SELECT pg_backend_pid()')).scalar_one();c.rollback()
                # Release to the existing pool, then recheckout for a different account.
                pool_before=self.data_state(case)
                with db.connect() as c:
                    assert c.execute(text('SELECT pg_backend_pid()')).scalar_one()==backend
                    assert c.execute(text('SELECT session_user,current_user')).one()==('access_runtime','access_runtime')
                    keys=['request.jwt.claims','app.context_kind','app.account_id','app.actor_id','app.is_platform_admin']
                    for key in keys:
                        assert c.execute(text("SELECT nullif(current_setting(:key,true),'')"),{'key':key}).scalar_one() is None
                    c.rollback()
                    with self.role(c,values['other']):
                        sp=c.begin_nested()
                        try:assert c.execute(text("UPDATE identity.users SET username='Synthetic other pooled profile'")).rowcount==1
                        finally:sp.rollback()
                    for key in keys:
                        assert c.execute(text("SELECT nullif(current_setting(:key,true),'')"),{'key':key}).scalar_one() is None
                    c.rollback()
                assert self.data_state(case)==pool_before
            finally:db.dispose()
        row=self.sql(case,PROFILE_SQL,{'id':missing})[0][0]
        assert row['created_by']==missing and row['updated_by']==missing
        assert row['actor_key'] is None and row['is_system'] is False and row['is_platform_admin'] is False and row['deleted_at'] is None
        assert row['created_at'] and row['updated_at']
        existing=self.sql(case,PROFILE_SQL,{'id':account})[0][0]
        assert existing['username']=='Synthetic ordinary profile' and existing['updated_by']==account and existing['deleted_at'] is None
        assert (existing['created_by'],existing['created_at'])==(original['created_by'],original['created_at'])
        assert self.sql(case,'SELECT updated_at > CAST(:old AS timestamptz) FROM identity.users WHERE id=CAST(:id AS uuid)',
                        {'old':original['updated_at'],'id':account})==[(True,)]
        new_audit=[tuple(r) for r in self.sql(case,audit_sql,values) if r[0] not in audit_before]
        assert len(new_audit)==4 and len({r[0] for r in new_audit})==4
        assert sorted(r[1:] for r in new_audit)==sorted([('UPDATE',account,account)]*3+[('INSERT',missing,missing)])
        assert self.sql(case,"SELECT has_any_column_privilege('authenticated','identity.users','SELECT'),has_table_privilege('authenticated','identity.users','DELETE'),has_table_privilege('identity_migrator','auth.users','INSERT')")==[(False,False,False)]
        self.passed('profile-protected-and-supported-writes',protected_update_columns=list(PROTECTED),protected_insert=True,
            mixed_same_value_upsert_denied=True,admin_claim_no_elevation=True,no_partial_effects=True,server_attribution=True,
            soft_delete_unretire=True,no_new_select=True,service_role_compatible=True,pooled_reuse=True,auth_helper_still_denied=True)

    def compatibility(self):
        """Live head8 differs from pinned head7 only in profile ACL categories."""
        current=baseline.catalog_fingerprints(self.snapshot('clean'))
        baseline.compare_catalog(current,baseline.trusted_profile_reference())
        prior=baseline.trusted_target_reference()
        assert prior.keys()==current.keys()
        assert {key for key in prior if prior[key]!=current[key]}=={
            'relations','columns','effective_tables','effective_columns'}
        self.passed('profile-live-canonical-compatibility',
            changed_categories=['columns','effective_columns','effective_tables','relations'],
            hooks_audit_defaults_policies_projections_unchanged=True,
            native_auth_or_seed_sequence_reexecuted=False)

    def effective_acl_refuses(self,case):
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:
                try:baseline.verify_profile_privileges(c)
                except baseline.BaselineError as error:
                    assert str(error)=='identity_profile_column_privileges_mismatch'
                else:raise AssertionError('profile_effective_acl_drift_not_refused')
        finally:db.dispose()

    def inherited_privilege(self):
        """An actual inherited grant is refused without repairing its owner."""
        case='unsafe';admin=self.admin(case)
        edge_sql="""SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),pg_get_userbyid(grantor),admin_option,
            to_jsonb(pg_auth_members)->>'inherit_option',to_jsonb(pg_auth_members)->>'set_option'
            FROM pg_auth_members WHERE pg_get_userbyid(roleid)='anon' AND pg_get_userbyid(member)='authenticated' ORDER BY 1,2,3"""
        acl_sql="SELECT attacl::text FROM pg_attribute WHERE attrelid='identity.users'::regclass AND attname='is_system'"
        before_acl=self.sql(case,acl_sql)
        def edges():
            with admin.begin() as c:return [tuple(r) for r in c.execute(text(edge_sql))]
        before=edges();assert before==[]
        self.witness('profile-inheritance-restoration-required',{'case':case,'before':before,'column_acl':[list(r) for r in before_acl],
            'role':'anon','member':'authenticated','privilege':'UPDATE(is_system)'})
        def interrupted(signum,frame):raise RuntimeError('profile_inheritance_fixture_interrupted')
        old={sig:signal.getsignal(sig) for sig in [signal.SIGINT,signal.SIGTERM]}
        for sig in old:signal.signal(sig,interrupted)
        try:
            self.sql(case,'GRANT UPDATE (is_system) ON identity.users TO anon')
            with admin.begin() as c:
                c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                c.execute(text('GRANT anon TO authenticated WITH INHERIT TRUE, SET FALSE'))
            self.effective_acl_refuses(case)
            before_data=self.data_state(case)
            self.command('profile-inherited-effective-drift',case,expected='identity_profile_column_privileges_mismatch')
            assert self.data_state(case)==before_data
        finally:
            try:
                for sig in old:signal.signal(sig,signal.SIG_IGN)
                with admin.begin() as c:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    c.execute(text('REVOKE anon FROM authenticated'))
                self.sql(case,'REVOKE UPDATE (is_system) ON identity.users FROM anon')
                assert edges()==before and self.sql(case,acl_sql)==before_acl
                self.witness('profile-inheritance-restored',{'case':case,'exact_edges_and_acl':True})
            finally:
                for sig,handler in old.items():signal.signal(sig,handler)
                admin.dispose()
        self.command('profile-inheritance-reconciled',case)
        self.passed('profile-effective-inherited-privilege-refused',exact_restoration=True)

    def upgrades_and_failures(self):
        self.validate_targets()
        self.prior_evidence(PREVIOUS_COMMIT,PREVIOUS_FILES,'identity_0007')
        self.command('profile-clean','clean');self.compatibility();self.writes();self.command('profile-repeat','clean')
        self.legacy('legacy');self.original_ledger('legacy')
        for case in ['legacy','previous']:
            self.row_fixtures(case)
            before,external=self.data_state(case,membership_without_revision=case=='legacy'),self.external_state(case)
            self.command('profile-'+case,case,mode='adopt' if case=='legacy' else 'clean')
            after=self.data_state(case,membership_without_revision=case=='legacy')
            assert all(after[key]==value for key,value in before.items() if key!='identity.alembic_version')
            assert self.external_state(case)==external
        # Enter recovery scope before committed mutations or subsequent reads.
        with self.acl_fixture('failure','GRANT UPDATE (is_system) ON identity.users TO PUBLIC',
                              'REVOKE UPDATE (is_system) ON identity.users FROM PUBLIC'):
            before,catalog=self.data_state('failure'),self.snapshot('failure')
            self.effective_acl_refuses('failure')
            self.command('profile-public-rights-preflight','failure',expected='identity_authority_role_unsafe')
            assert self.data_state('failure')==before and self.snapshot('failure')==catalog
        with self.failure_fixture('failure'):
            before,catalog=self.data_state('failure'),self.snapshot('failure')
            self.command('profile-mid-revision-rollback','failure',expected='identity_migration_failed_requires_reconciliation')
            assert self.data_state('failure')==before and self.snapshot('failure')==catalog
            assert self.sql('failure','SELECT version_num FROM identity.alembic_version')==[('identity_0007',)]
        self.command('profile-after-rollback','failure')
        self.command('profile-unsafe-clean','unsafe')
        for grant,revoke,expected in [('GRANT UPDATE (is_system) ON identity.users TO PUBLIC','REVOKE UPDATE (is_system) ON identity.users FROM PUBLIC','identity_authority_role_unsafe'),
                             ('GRANT INSERT ON identity.users TO authenticated','REVOKE INSERT ON identity.users FROM authenticated','identity_profile_column_privileges_mismatch')]:
            restore='GRANT INSERT (id, username) ON identity.users TO authenticated' if grant=='GRANT INSERT ON identity.users TO authenticated' else None
            with self.acl_fixture('unsafe',grant,revoke,restore):
                before=self.data_state('unsafe')
                self.effective_acl_refuses('unsafe')
                self.command('profile-effective-drift','unsafe',expected=expected)
                assert self.data_state('unsafe')==before
            self.command('profile-drift-reconciled','unsafe')
        self.inherited_privilege()
        self.sql('unknown',"UPDATE identity.alembic_version SET version_num='identity_unknown'")
        before=self.data_state('unknown');self.command('profile-unknown','unknown',expected='identity_unknown_history');assert self.data_state('unknown')==before
        self.passed('profile-migration-matrix',clean=True,adopt=True,head7_upgrade=True,repeat=True,old_rows_preserved=True,
                    mid_revision_rollback=True,public_rights_fail_closed=True,unknown_refused=True)


def main():
    if not __debug__:raise RuntimeError('profile_qualification_optimized_python_prohibited')
    proof,private=fixture();q=ProfileQualification(proof,private)
    if sys.argv[1:]==['--characterize']:q.validate_targets();q.characterize()
    elif not sys.argv[1:]:q.upgrades_and_failures()
    else:raise RuntimeError('profile_qualification_arguments_invalid')


if __name__=='__main__':
    try:main()
    except Exception as error:
        print('profile_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None
