"""Synthetic legacy RPC proof on root-prepared fixtures; no provider/HTTP claim."""
from contextlib import contextmanager
from pathlib import Path
import json
import signal
import sys
import uuid

sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_current_account_actor as previous
from qualify_profile_fields import ProfileQualification, PREVIOUS_FILES as HEAD7_FILES
from qualify_identity_baseline import baseline, engine, fixture, text

PREVIOUS_COMMIT='f52352fc31337f5f15b1f249775e2dcebaf134b7'
PREVIOUS_FILES=HEAD7_FILES | {'versions/0008_profile_fields.py','profile-reference.json'}
previous.PREVIOUS_PYTHON=Path(sys.executable)
REQUIRED_CASES=frozenset({'characterization','legacy_roles_reference','clean','legacy','previous','failure','unsafe','unknown','native'})
RPC='SELECT role FROM public.get_user_roles() ORDER BY role'
FUNCTION_ACL="""SELECT pg_get_userbyid(proowner),proacl::text,pg_get_function_identity_arguments(oid),pg_get_function_result(oid),prosecdef,provolatile
    FROM pg_proc WHERE oid='public.get_user_roles()'::regprocedure"""
NIL='00000000-0000-0000-0000-000000000000'
SPOOF_ROLE='synthetic_search_path_spoof_role'
CLAIM_SETTINGS=('request.jwt.claim.sub','request.jwt.claim','request.jwt.claims')
CHARACTERIZATION_EXPECTED=[{'case':kind,'sqlstate':'42702'} for kind in ['own','foreign_member','foreign_org']]


class LegacyRolesQualification(ProfileQualification):
    def validate_targets(self):
        for group in ['owner_urls','runtime_urls','databases']:
            assert set(self.private[group])==REQUIRED_CASES,'legacy_roles_cases_invalid'
        self.inputs=json.loads((self.proof/'role-fixtures.json').read_text())
        assert set(self.inputs)=={'characterization','clean'}
        for row in self.inputs.values():
            assert set(row)=={'account','other','org','other_org','member','other_member','other_org_member','role','deleted_role'}
            assert len({row[key] for key in ['account','other','org','other_org']})==4
            for key in ['account','other','org','other_org']:
                assert str(uuid.UUID(row[key]))==row[key] and uuid.UUID(row[key]).int
            for key in ['member','other_member','other_org_member','role','deleted_role']:
                assert isinstance(row[key],str) and row[key].isascii() and row[key].isdecimal() and 0<int(row[key])<=9223372036854775807

    def auth_helper_parity(self,case):
        native=json.loads((self.proof/'auth-helper-definitions.json').read_text())['native']
        actual=self.sql(case,"SELECT pg_get_functiondef('auth.uid()'::regprocedure),pg_get_functiondef('auth.jwt()'::regprocedure)")
        assert len(native)==2 and len(actual)==1 and list(actual[0])==native,'legacy_roles_auth_helper_parity_mismatch'

    def claims(self,values):
        return {'sub':values['account'],'org_id':values['org'],'member_id':values['member'],
                'role':'authenticated','user_roles':['admin']}

    def invoke(self,c,claims,expected=None,mutation=None,spoof=False,claim_settings=None):
        """Every read/fixture mutation is rollback-only on the actual restricted login."""
        transaction=c.begin()
        try:
            c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
            c.execute(text('SET LOCAL ROLE service_role' if mutation else 'SET LOCAL ROLE authenticated'))
            c.execute(text("SELECT set_config('request.jwt.claims',:claims,true),set_config('app.context_kind','user',true),set_config('app.account_id',:account,true),set_config('app.org_id',:org,true)"),
                {'claims':json.dumps(claims),'account':self.inputs['clean']['account'],'org':self.inputs['clean']['org']})
            # Match native helper precedence. These are fixture-only settings, not a
            # new authentication protocol; each execution explicitly clears absent forms.
            settings={key:'' for key in CLAIM_SETTINGS};settings['request.jwt.claims']=json.dumps(claims)
            if claim_settings:
                assert set(claim_settings)<=set(CLAIM_SETTINGS)
                settings.update(claim_settings)
            for key,value in settings.items():
                c.execute(text('SELECT set_config(:key,:value,true)'),{'key':key,'value':value})
            if mutation:
                c.execute(text(mutation),self.inputs['clean'])
                c.execute(text('SET LOCAL ROLE authenticated'))
            assert c.execute(text('SELECT session_user,current_user')).one()==('access_runtime','authenticated')
            if spoof:
                c.execute(text("CREATE TEMP TABLE member_role(role text); INSERT INTO member_role VALUES ('synthetic_search_path_spoof_role'); SET LOCAL search_path=pg_temp,public,identity"))
            try:rows=[tuple(row) for row in c.execute(text(RPC))]
            except Exception as error:
                state=getattr(getattr(error,'orig',error),'sqlstate',None)
                assert expected and state==expected,('legacy_roles_unexpected_sqlstate',state)
                return {'sqlstate':state}
            assert expected is None,'legacy_roles_expected_error_missing'
            if spoof:assert (SPOOF_ROLE,) not in rows,'legacy_roles_search_path_spoof_leaked'
            return rows
        finally:transaction.rollback()

    def characterize(self):
        case='characterization';v=self.inputs[case]
        self.auth_helper_parity(case)
        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0008',)]
        before=self.data_state(case);observed=[]
        functions=self.snapshot(case)['functions']
        with self.fixture_execution(case):
            db=engine(self.private['runtime_urls'][case])
            try:
                with db.connect() as c:
                    for kind,change in [('own',{}),('foreign_member',{'member_id':v['other_member']}),('foreign_org',{'org_id':v['other_org']})]:
                        claims=self.claims(v);claims.update(change)
                        # Record the actual old helper result, including its known ambiguity.
                        tx=c.begin()
                        try:
                            c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'; SET LOCAL ROLE authenticated"))
                            c.execute(text("SELECT set_config('request.jwt.claims',:claims,true)"),{'claims':json.dumps(claims)})
                            try:result={'rows':[list(r) for r in c.execute(text(RPC))]}
                            except Exception as error:result={'sqlstate':getattr(getattr(error,'orig',error),'sqlstate',None)}
                            observed.append({'case':kind,**result})
                        finally:tx.rollback()
            finally:db.dispose()
        unchanged=self.data_state(case)==before
        self.witness('legacy-roles-head8-characterization',{'head':'identity_0008','observed':observed,
            'unchanged_data':unchanged,'functions':functions})
        assert unchanged,'legacy_roles_characterization_data_changed'
        assert observed==CHARACTERIZATION_EXPECTED,'legacy_roles_unexpected_head8_observations'
        self.passed('legacy-roles-head8-characterization',observed=observed,real_login='access_runtime',provider_jwt_verification=False)

    def reads(self):
        case='clean';v=self.inputs[case];claims=self.claims(v);before=self.data_state(case)
        self.auth_helper_parity(case)
        assert self.sql(case,'SELECT count(*) FROM identity.account_actor WHERE account_id IN (CAST(:account AS uuid),CAST(:other AS uuid))',v)==[(0,)]
        with self.fixture_execution(case):
            db=engine(self.private['runtime_urls'][case])
            try:
                with db.connect() as c:
                    assert self.invoke(c,claims)==[('admin',)]
                    assert self.invoke(c,claims,spoof=True)==[('admin',)]
                    assert self.invoke(c,claims,mutation='UPDATE identity.member_role SET deleted_at=NULL WHERE id=CAST(:deleted_role AS bigint)')==[('admin',),('employee',)]
                    assert self.invoke(c,claims)==[('admin',)]
                    for user_roles in [None,[],['unrelated_role']]:
                        candidate=dict(claims)
                        if user_roles is None:candidate.pop('user_roles')
                        else:candidate['user_roles']=user_roles
                        assert self.invoke(c,candidate)==[('admin',)]
                    # Native auth.uid prioritizes the singular sub setting; auth.jwt
                    # prioritizes singular JSON claim. Conflicting helpers cannot join.
                    other=dict(claims,sub=v['other'],member_id=v['other_member'])
                    assert self.invoke(c,claims,claim_settings={'request.jwt.claim.sub':v['other']})==[]
                    assert self.invoke(c,claims,claim_settings={'request.jwt.claim':json.dumps(other)})==[]
                    assert self.invoke(c,other,claim_settings={'request.jwt.claim':json.dumps(claims)})==[]
                    assert self.invoke(c,{},claim_settings={'request.jwt.claim.sub':v['other'],
                        'request.jwt.claim':json.dumps(other),'request.jwt.claims':''})==[('employee',)]
                    # Coherent legacy forms take precedence over conflicting plural JSON.
                    assert self.invoke(c,claims,claim_settings={'request.jwt.claim.sub':v['other'],
                        'request.jwt.claim':json.dumps(other)})==[('employee',)]
                    variants=[{}, {'sub':v['other']}, {'org_id':v['other_org']},{'member_id':v['other_member']},
                        {'member_id':v['other_org_member']},{'sub':str(uuid.uuid4())},{'org_id':str(uuid.uuid4())},
                        {'member_id':'9223372036854775807'},{'member_id':'0'},{'member_id':'-1'}]
                    for key in ['sub','org_id','member_id']:
                        variants.extend([{key:None},{key:''}])
                    variants.extend([{'sub':NIL},{'org_id':NIL}])
                    for variant in variants:
                        candidate={} if variant=={} else dict(claims,**variant)
                        assert self.invoke(c,candidate)==[]
                    # Missing each individual claim must fail closed despite app GUCs and stale admin arrays.
                    for key in ['sub','org_id','member_id']:
                        candidate=dict(claims);candidate.pop(key)
                        assert self.invoke(c,candidate)==[]
                    for key in ['sub','org_id','member_id']:
                        assert self.invoke(c,dict(claims,**{key:'not-typed'}),expected='22P02')=={'sqlstate':'22P02'}
                    assert self.invoke(c,dict(claims,member_id='9223372036854775808'),expected='22003')=={'sqlstate':'22003'}
                    for mutation in [
                        'UPDATE identity.users SET deleted_at=now() WHERE id=CAST(:account AS uuid)',
                        'UPDATE identity.org SET deleted_at=now() WHERE id=CAST(:org AS uuid)',
                        'UPDATE identity.org_member SET deleted_at=now() WHERE id=CAST(:member AS bigint)',
                        'UPDATE identity.member_role SET deleted_at=now() WHERE id=CAST(:role AS bigint)']:
                        assert self.invoke(c,claims,mutation=mutation)==[]
                        assert self.invoke(c,claims)==[('admin',)]
                    # Distinct legitimate exact bindings return their own role, never the original admin role.
                    assert self.invoke(c,dict(claims,sub=v['other'],member_id=v['other_member']))==[('employee',)]
                    assert self.invoke(c,dict(claims,org_id=v['other_org'],member_id=v['other_org_member']))==[('employee',)]
                    backend=c.execute(text('SELECT pg_backend_pid()')).scalar_one();c.rollback()
                with db.connect() as c:
                    assert c.execute(text('SELECT pg_backend_pid()')).scalar_one()==backend
                    assert c.execute(text('SELECT session_user,current_user')).one()==('access_runtime','access_runtime')
                    for key in [*CLAIM_SETTINGS,'app.account_id','app.org_id','app.context_kind']:
                        assert c.execute(text("SELECT nullif(current_setting(:key,true),'')"),{'key':key}).scalar_one() is None
                    c.rollback();assert self.invoke(c,{})==[]
                    assert self.invoke(c,dict(claims,sub=v['other'],member_id=v['other_member']))==[('employee',)]
            finally:db.dispose()
        assert self.data_state(case)==before
        self.passed('legacy-roles-restricted-read-matrix',exact_active=True,deleted_role_excluded=True,no_actor_prerequisite=True,
            foreign_missing_nil_retired_denied=True,typed_errors=True,pooled_reuse=True,search_path_spoof=True,full_data_hashes_unchanged=True)

    def compatibility(self):
        current=baseline.catalog_fingerprints(self.snapshot('clean'))
        prior=baseline.trusted_profile_reference();baseline.compare_catalog(current,baseline.trusted_legacy_roles_reference())
        assert prior.keys()==current.keys()
        assert {key for key in prior if prior[key]!=current[key]}=={'functions'}
        witnesses=sorted(self.proof.glob('legacy-roles-head8-characterization-*.json'),key=lambda path:path.stat().st_mtime_ns)
        assert witnesses,'legacy_roles_missing_head8_characterization'
        characterized=json.loads(witnesses[-1].read_text())
        assert characterized['head']=='identity_0008' and characterized['unchanged_data'] is True
        assert characterized['observed']==CHARACTERIZATION_EXPECTED,'legacy_roles_unexpected_head8_observations'
        old_functions=characterized['functions'];new_functions=self.snapshot('clean')['functions']
        assert baseline.catalog_fingerprints({'functions':old_functions})['functions']==prior['functions']
        self.verify_function_delta(old_functions,new_functions)
        self.passed('legacy-roles-only-function-catalog-change',hooks_seeds_profile_acl_roles_unchanged=True,
            per_function_rows_compared=True,exact_helper_owner_acl_preserved=True)

    @staticmethod
    def verify_function_delta(old_rows,new_rows):
        old={tuple(row[:3]):row for row in old_rows};new={tuple(row[:3]):row for row in new_rows}
        assert old.keys()==new.keys(),'legacy_roles_function_set_changed'
        helper=('public','get_user_roles','')
        assert {key for key in old if old[key]!=new[key]}=={helper},'legacy_roles_other_function_changed'
        before,after=old[helper],new[helper]
        assert before[:4]==after[:4] and before[5:]==after[5:],'legacy_roles_helper_owner_acl_changed'
        # pg_get_functiondef includes language/security/volatility/signature; remove
        # only the body and search_path line before comparing its declaration.
        def declaration(definition):
            header,delimiter,body=definition.partition('AS $function$')
            assert delimiter and '$function$' in body,'legacy_roles_function_definition_shape'
            return ([line for line in header.splitlines() if not line.lstrip().startswith('SET search_path TO ')],
                    body.rsplit('$function$',1)[1])
        assert declaration(before[4])==declaration(after[4]),'legacy_roles_helper_declaration_changed'

    def revoked_public(self):
        """Characterize a target-only revoked PUBLIC ACL without adopting that drift."""
        import importlib.util
        path=baseline.HERE/'versions/0009_legacy_roles.py'
        spec=importlib.util.spec_from_file_location('legacy_roles_source',path)
        revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
        before=self.data_state('clean');db=engine(self.private['owner_urls']['clean'])
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    canonical=c.execute(text(FUNCTION_ACL)).one()
                    c.execute(text('REVOKE EXECUTE ON FUNCTION public.get_user_roles() FROM PUBLIC'))
                    revoked=c.execute(text(FUNCTION_ACL)).one()
                    assert revoked!=canonical
                    c.exec_driver_sql(revision.LEGACY_ROLES_SQL,execution_options={'no_parameters':True})
                    assert c.execute(text(FUNCTION_ACL)).one()==revoked
                    assert c.execute(text("SELECT has_function_privilege('anon','public.get_user_roles()','EXECUTE'),has_function_privilege('authenticated','public.get_user_roles()','EXECUTE')")).one()==(False,True)
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state('clean')==before
        self.passed('legacy-roles-revoked-public-preserved-rollback-only',adopted=False,normalized=False)

    @contextmanager
    def failure_fixture(self,case):
        state_sql="""SELECT 'function',p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.proname='synthetic_legacy_roles_failure'
            UNION ALL SELECT 'event_trigger',evtname FROM pg_event_trigger WHERE evtname='synthetic_legacy_roles_failure' ORDER BY 1,2"""
        before=self.admin_sql(case,state_sql);assert before==[],'legacy_roles_failure_fixture_already_exists'
        create="""CREATE FUNCTION public.synthetic_legacy_roles_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN
            IF EXISTS(SELECT 1 FROM pg_proc WHERE oid='public.get_user_roles()'::regprocedure AND proconfig=ARRAY['search_path=pg_catalog, pg_temp']) THEN
                RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_legacy_roles_failure';
            END IF; END $$;
            CREATE EVENT TRIGGER synthetic_legacy_roles_failure ON ddl_command_end WHEN TAG IN ('CREATE FUNCTION') EXECUTE FUNCTION public.synthetic_legacy_roles_failure();"""
        cleanup='DROP EVENT TRIGGER IF EXISTS synthetic_legacy_roles_failure; DROP FUNCTION IF EXISTS public.synthetic_legacy_roles_failure()'
        self.witness('legacy-roles-event-restoration-required',{'case':case,'before':before,'create':create,'cleanup':cleanup})
        with self.restoration_signals():
            try:self.admin_sql(case,create);yield
            finally:
                for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,signal.SIG_IGN)
                self.admin_sql(case,cleanup)
                assert self.admin_sql(case,state_sql)==before,'legacy_roles_failure_fixture_not_restored'
                self.witness('legacy-roles-event-restored',{'case':case,'exact_objects':True})

    def upgrades_and_failures(self):
        self.validate_targets();self.prior_evidence(PREVIOUS_COMMIT,PREVIOUS_FILES,'identity_0008')
        self.command('legacy-roles-clean','clean');self.compatibility();self.reads();self.revoked_public();self.command('legacy-roles-repeat','clean')
        self.legacy('legacy');self.original_ledger('legacy')
        for case in ['legacy','previous']:
            self.row_fixtures(case)
            before=self.data_state(case,membership_without_revision=case=='legacy');external=self.external_state(case)
            acl=self.sql(case,FUNCTION_ACL)
            self.command('legacy-roles-'+case,case,mode='adopt' if case=='legacy' else 'clean')
            after=self.data_state(case,membership_without_revision=case=='legacy')
            assert all(after[key]==value for key,value in before.items() if key!='identity.alembic_version')
            assert self.sql(case,FUNCTION_ACL)==acl and self.external_state(case)==external
        with self.failure_fixture('failure'):
            before,catalog=self.data_state('failure'),self.snapshot('failure')
            self.command('legacy-roles-mid-revision-rollback','failure',expected='identity_migration_failed_requires_reconciliation')
            assert self.data_state('failure')==before and self.snapshot('failure')==catalog
            assert self.sql('failure','SELECT version_num FROM identity.alembic_version')==[('identity_0008',)]
        self.command('legacy-roles-after-rollback','failure');self.command('legacy-roles-unsafe-clean','unsafe')
        with self.acl_fixture('unsafe','GRANT INSERT ON identity.users TO authenticated','REVOKE INSERT ON identity.users FROM authenticated',
                'GRANT INSERT (id, username) ON identity.users TO authenticated'):
            before,catalog=self.data_state('unsafe'),self.snapshot('unsafe')
            self.command('legacy-roles-drift-refused','unsafe',expected='identity_profile_column_privileges_mismatch')
            assert self.data_state('unsafe')==before and self.snapshot('unsafe')==catalog
        self.command('legacy-roles-drift-reconciled','unsafe')
        self.sql('unknown',"UPDATE identity.alembic_version SET version_num='identity_unknown'")
        before=self.data_state('unknown');self.command('legacy-roles-unknown','unknown',expected='identity_unknown_history');assert self.data_state('unknown')==before
        self.passed('legacy-roles-migration-matrix',clean_adopt_head8_repeat=True,exact_acl_preservation=True,mid_revision_rollback=True,drift_and_unknown_refused=True)


def main():
    if not __debug__:raise RuntimeError('legacy_roles_qualification_optimized_python_prohibited')
    proof,private=fixture();q=LegacyRolesQualification(proof,private)
    if sys.argv[1:]==['--characterize']:q.validate_targets();q.characterize()
    elif not sys.argv[1:]:q.upgrades_and_failures()
    else:raise RuntimeError('legacy_roles_qualification_arguments_invalid')


if __name__=='__main__':
    try:main()
    except Exception as error:
        print('legacy_roles_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None
