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

PREVIOUS_COMMIT='b790051bf93417640702ff450aff9d4e9b398575'
PREVIOUS_FILES=HEAD7_FILES | {'versions/0008_profile_fields.py','profile-reference.json','versions/0009_legacy_roles.py','legacy-role-reference.json'}
previous.PREVIOUS_PYTHON=Path(sys.executable)
REQUIRED_CASES=frozenset({'characterization','token_hook_reference','clean','legacy','previous','failure','unsafe','unknown','native'})
RPC='SELECT identity.custom_access_token_hook(CAST(:event AS jsonb))'
FUNCTION_ACL="""SELECT pg_get_userbyid(proowner),proacl::text,pg_get_function_identity_arguments(oid),pg_get_function_result(oid),prosecdef,provolatile
    FROM pg_proc WHERE oid='identity.custom_access_token_hook(jsonb)'::regprocedure"""
NIL='00000000-0000-0000-0000-000000000000'
HOOK_EDGE_SQL="""SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),pg_get_userbyid(grantor),admin_option,to_jsonb(pg_auth_members)->>'inherit_option',to_jsonb(pg_auth_members)->>'set_option' FROM pg_auth_members WHERE pg_get_userbyid(member)='access_runtime' AND pg_get_userbyid(roleid) IN ('supabase_auth_admin','service_role') ORDER BY 1,2,3"""


class TokenHookQualification(ProfileQualification):
    def validate_targets(self):
        for group in ['owner_urls','runtime_urls','databases']:
            assert set(self.private[group])==REQUIRED_CASES,'token_hook_cases_invalid'
        self.inputs=json.loads((self.proof/'token-hook-fixtures.json').read_text())
        assert set(self.inputs)=={'characterization','clean'}
        for row in self.inputs.values():
            assert set(row)=={'account','other','missing','org','other_org','member','other_member','other_org_member','role','deleted_role'}
            assert len({row[key] for key in ['account','other','missing','org','other_org']})==5
            for key in ['account','other','missing','org','other_org']:
                assert str(uuid.UUID(row[key]))==row[key] and uuid.UUID(row[key]).int
            for key in ['member','other_member','other_org_member','role','deleted_role']:
                assert isinstance(row[key],str) and row[key].isascii() and row[key].isdecimal() and 0<int(row[key])<=9223372036854775807

    @contextmanager
    def fixture_execution(self,case):
        """Exact absent-edge restoration; no inherited/browser login authority."""
        admin=self.admin(case)
        def edges():
            with admin.begin() as c:
                c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                return [tuple(r) for r in c.execute(text(HOOK_EDGE_SQL))]
        before=edges();assert before==[], 'token_hook_fixture_edges_already_present'
        self.witness('token-hook-role-restoration-required',{'case':case,'login':'access_runtime',
            'roles':['supabase_auth_admin','service_role'],'before':before,'temporary':'SET TRUE INHERIT FALSE ADMIN FALSE'})
        def change(grant):
            with admin.begin() as c:
                c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                c.execute(text('GRANT supabase_auth_admin, service_role TO access_runtime WITH INHERIT FALSE, SET TRUE' if grant
                               else 'REVOKE supabase_auth_admin, service_role FROM access_runtime'))
        def interrupted(signum,frame):raise RuntimeError('token_hook_fixture_interrupted')
        old={sig:signal.getsignal(sig) for sig in [signal.SIGINT,signal.SIGTERM]}
        for sig in old:signal.signal(sig,interrupted)
        try:
            try:
                change(True)
                current=edges()
                assert {r[0] for r in current}=={'supabase_auth_admin','service_role'}
                assert len(current)==2 and all(r[1]=='access_runtime' and r[3:]==(False,'false','true') for r in current)
                yield
            finally:
                for sig in old:signal.signal(sig,signal.SIG_IGN)
                change(False)
                assert edges()==before,'token_hook_fixture_edges_not_restored'
                self.witness('token-hook-role-restored',{'case':case,'before':before,'after':edges(),'exact_edges':True})
        finally:
            for sig,handler in old.items():signal.signal(sig,handler)
            admin.dispose()
        self.passed('token-hook-temporary-role-edges-restored',case=case,exact=True,provider_jwt_verification=False)

    def snapshot(self,case):
        db=engine(self.private['owner_urls'][case])
        try:
            with db.begin() as c:
                c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                return baseline.target_catalog_snapshot(c)
        finally:db.dispose()

    def auth_helper_parity(self,case):
        native=json.loads((self.proof/'auth-helper-definitions.json').read_text())['native']
        actual=self.sql(case,"SELECT pg_get_functiondef('auth.uid()'::regprocedure),pg_get_functiondef('auth.jwt()'::regprocedure)")
        assert len(native)==2 and len(actual)==1 and list(actual[0])==native,'token_hook_auth_helper_parity_mismatch'

    def event(self,v,org=True):
        result={'user_id':v['account'],'claims':{'unrelated':'preserved'},'unrelated_event':['preserved']}
        if org:result['user_metadata']={'current_org_id':v['org']}
        return result

    def invoke(self,c,event,expected=None,mutation=None,spoof=False,case='clean'):
        tx=c.begin()
        try:
            c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
            c.execute(text('SET LOCAL ROLE service_role' if mutation else 'SET LOCAL ROLE supabase_auth_admin'))
            if mutation:
                c.execute(text(mutation),self.inputs[case])
                c.execute(text('SET LOCAL ROLE supabase_auth_admin'))
            assert c.execute(text('SELECT session_user,current_user')).one()==('access_runtime','supabase_auth_admin')
            if spoof:
                c.execute(text("CREATE TEMP TABLE org_member(org_id uuid); CREATE TEMP TABLE member_role(role text); SET LOCAL search_path=pg_temp,public,identity"))
            try:result=c.execute(text(RPC),{'event':json.dumps(event)}).scalar_one()
            except Exception as error:
                state=getattr(getattr(error,'orig',error),'sqlstate',None)
                assert expected and state==expected,('token_hook_unexpected_sqlstate',state)
                return {'sqlstate':state}
            assert expected is None,'token_hook_expected_error_missing'
            assert {k:v for k,v in result.items() if k!='claims'}=={k:v for k,v in event.items() if k!='claims'}
            generated={'org_id','org_slug','member_id','user_roles','role_ids','org_ids','is_org_owner'}
            for key,value in event.get('claims',{}).items():
                if key not in generated:assert result['claims'][key]==value
            return result['claims']
        finally:tx.rollback()

    def characterize(self):
        case='characterization';v=self.inputs[case]
        self.auth_helper_parity(case)
        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0009',)]
        before=self.data_state(case);functions=self.snapshot(case)['functions'];observed=[]
        retire='UPDATE identity.org SET deleted_at=now() WHERE id=CAST(:org AS uuid)'
        with self.fixture_execution(case):
            db=engine(self.private['runtime_urls'][case])
            try:
                with db.connect() as c:
                    for kind,event in [('selected',self.event(v)),('fallback',self.event(v,False))]:
                        claims=self.invoke(c,event,mutation=retire,case=case)
                        observed.append({'case':kind,'claims':claims})
            finally:db.dispose()
        unchanged=self.data_state(case)==before
        self.witness('token-hook-head9-characterization',{'head':'identity_0009','observed':observed,'unchanged_data':unchanged,'functions':functions})
        assert unchanged
        selected=observed[0]['claims']
        assert selected['org_id']==v['org'] and selected['member_id']==int(v['member'])
        assert v['org'] in selected['org_ids'] and selected['user_roles']==['admin']
        assert observed[1]['claims']['org_id']==v['org'],'token_hook_unexpected_head9_fallback'
        self.passed('token-hook-head9-characterization',real_login='access_runtime',provider_jwt_verification=False)

    def reads(self):
        case='clean';v=self.inputs[case];event=self.event(v);before=self.data_state(case)
        self.auth_helper_parity(case)
        assert self.sql(case,'SELECT count(*) FROM identity.users WHERE id=CAST(:missing AS uuid)',v)==[(0,)]
        slug=self.sql(case,'SELECT slug FROM identity.org WHERE id=CAST(:org AS uuid)',v)[0][0]
        retire='UPDATE identity.org SET deleted_at=now() WHERE id=CAST(:org AS uuid)'
        with self.fixture_execution(case):
            db=engine(self.private['runtime_urls'][case])
            try:
                with db.connect() as c:
                    active=self.invoke(c,event)
                    assert active['member_id']==int(v['member']) and active['user_roles']==['admin']
                    assert active['role_ids']==[int(v['role'])] and active['is_org_owner'] is True
                    assert set(active['org_ids'])=={v['org'],v['other_org']}
                    assert self.invoke(c,event,spoof=True)==active
                    no_claims=dict(event);no_claims.pop('claims')
                    expected_generated={'org_id':v['org'],'org_slug':slug,'member_id':int(v['member']),
                        'user_roles':['admin'],'role_ids':[int(v['role'])],
                        'org_ids':active['org_ids'],'is_org_owner':True}
                    assert self.invoke(c,no_claims)==expected_generated
                    def denied(claims):
                        assert claims['member_id'] is None and claims['user_roles']==[] and claims['role_ids']==[] and claims['is_org_owner'] is False
                    retired=self.invoke(c,event,mutation=retire);denied(retired)
                    assert retired['org_id']==v['org'] and retired['org_slug'] is None and retired['org_ids']==[v['other_org']]
                    fallback=self.invoke(c,self.event(v,False),mutation=retire)
                    assert fallback['org_id']==v['other_org'] and fallback['member_id']==int(v['other_org_member'])
                    assert fallback['user_roles']==['employee'] and fallback['org_ids']==[v['other_org']]
                    all_retired='UPDATE identity.org SET deleted_at=now() WHERE id IN (SELECT org_id FROM identity.org_member WHERE user_id=CAST(:account AS uuid))'
                    empty=self.invoke(c,self.event(v,False),mutation=all_retired);denied(empty)
                    assert empty=={'unrelated':'preserved','org_id':None,'org_slug':None,'member_id':None,
                        'user_roles':[],'role_ids':[],'org_ids':[],'is_org_owner':False}
                    for metadata in [{},{'current_org_id':None}]:
                        assert self.invoke(c,dict(event,user_metadata=metadata))==active
                    # Nested claim metadata is not the hook's top-level selector.
                    nested=self.event(v,False);nested['claims']['user_metadata']={'current_org_id':v['other_org']}
                    assert self.invoke(c,nested)['org_id']==v['org']
                    for selected in [str(uuid.uuid4()),NIL]:
                        claims=self.invoke(c,dict(event,user_metadata={'current_org_id':selected}));denied(claims)
                        assert claims['org_id']==selected
                    foreign_selected=self.invoke(c,dict(event,user_id=v['other'],user_metadata={'current_org_id':v['other_org']}))
                    denied(foreign_selected)
                    assert foreign_selected['org_id']==v['other_org'] and foreign_selected['org_ids']==[v['org']]
                    # Owners precede older ordinary memberships; among ordinary members
                    # the original created_at ordering selects the oldest eligible row.
                    ordered="UPDATE identity.org_member SET is_owner=false,created_at=CASE WHEN id=CAST(:member AS bigint) THEN '2020-01-02'::timestamptz ELSE '2020-01-01'::timestamptz END WHERE user_id=CAST(:account AS uuid)"
                    assert self.invoke(c,self.event(v,False),mutation=ordered)['org_id']==v['other_org']
                    owner_priority=ordered.replace("is_owner=false", "is_owner=(id=CAST(:member AS bigint))")
                    assert self.invoke(c,self.event(v,False),mutation=owner_priority)['org_id']==v['org']
                    foreign=self.invoke(c,dict(event,user_id=v['missing']));denied(foreign)
                    assert foreign['org_id']==v['org'] and foreign['org_ids']==[]
                    for account in [None,NIL,v['missing']]:
                        claims=self.invoke(c,dict(event,user_id=account));denied(claims);assert claims['org_ids']==[]
                    absent=dict(event);absent.pop('user_id');denied(self.invoke(c,absent))
                    for candidate in [dict(event,user_id='malformed'),dict(event,user_metadata={'current_org_id':'malformed'})]:
                        assert self.invoke(c,candidate,expected='22P02')=={'sqlstate':'22P02'}
                    retire_member='UPDATE identity.org_member SET deleted_at=now() WHERE id=CAST(:member AS bigint)'
                    deleted_member=self.invoke(c,event,mutation=retire_member);denied(deleted_member)
                    assert deleted_member['org_id']==v['org'] and deleted_member['org_ids']==[v['other_org']]
                    member_fallback=self.invoke(c,self.event(v,False),mutation=retire_member)
                    assert member_fallback['org_id']==v['other_org'] and member_fallback['member_id']==int(v['other_org_member'])
                    assert member_fallback['user_roles']==['employee'] and member_fallback['org_ids']==[v['other_org']]
                    no_roles=self.invoke(c,event,mutation='UPDATE identity.member_role SET deleted_at=now() WHERE id=CAST(:role AS bigint)')
                    assert no_roles==dict(active,user_roles=[],role_ids=[])
                    # Existing profile lifecycle behavior is deliberately unchanged.
                    assert self.invoke(c,event,mutation='UPDATE identity.users SET deleted_at=now() WHERE id=CAST(:account AS uuid)')==active
                    multi=self.invoke(c,event,mutation='UPDATE identity.member_role SET deleted_at=NULL WHERE id=CAST(:deleted_role AS bigint)')
                    assert set(multi['user_roles'])=={'admin','employee'}
                    assert self.invoke(c,event)==active
                    backend=c.execute(text('SELECT pg_backend_pid()')).scalar_one();c.rollback()
                with db.connect() as c:
                    assert c.execute(text('SELECT pg_backend_pid()')).scalar_one()==backend
                    assert c.execute(text('SELECT session_user,current_user')).one()==('access_runtime','access_runtime')
                    c.rollback();denied(self.invoke(c,dict(event,user_id=v['missing'])))
                    assert self.invoke(c,event)==active
            finally:db.dispose()
        assert self.data_state(case)==before
        self.passed('token-hook-restricted-read-matrix',retired_selected_fallback_org_ids=True,top_level_metadata=True,
            typed_errors=True,pooled_reuse=True,search_path_spoof=True,full_data_hashes_unchanged=True)

    def compatibility(self):
        current=baseline.catalog_fingerprints(self.snapshot('clean'))
        prior=baseline.trusted_legacy_roles_reference();baseline.compare_catalog(current,baseline.trusted_token_hook_reference())
        assert prior.keys()==current.keys()
        assert {key for key in prior if prior[key]!=current[key]}=={'functions'}
        witnesses=sorted(self.proof.glob('token-hook-head9-characterization-*.json'),key=lambda path:path.stat().st_mtime_ns)
        assert witnesses,'token_hook_missing_head9_characterization'
        characterized=json.loads(witnesses[-1].read_text())
        assert characterized['head']=='identity_0009' and characterized['unchanged_data'] is True
        assert len(characterized['observed'])==2
        old_functions=characterized['functions'];new_functions=self.snapshot('clean')['functions']
        assert baseline.catalog_fingerprints({'functions':old_functions})['functions']==prior['functions']
        self.verify_function_delta(old_functions,new_functions)
        self.passed('token-hook-only-function-catalog-change',other_hooks_seeds_profile_acl_roles_unchanged=True,
            per_function_rows_compared=True,exact_helper_owner_acl_preserved=True)

    @staticmethod
    def verify_function_delta(old_rows,new_rows):
        old={tuple(row[:3]):row for row in old_rows};new={tuple(row[:3]):row for row in new_rows}
        assert old.keys()==new.keys(),'token_hook_function_set_changed'
        helper=('identity','custom_access_token_hook','event jsonb')
        assert {key for key in old if old[key]!=new[key]}=={helper},'token_hook_other_function_changed'
        before,after=old[helper],new[helper]
        assert before[:4]==after[:4] and before[5:]==after[5:],'token_hook_helper_owner_acl_changed'
        # pg_get_functiondef includes language/security/volatility/signature; remove
        # only the body and search_path line before comparing its declaration.
        def declaration(definition):
            header,delimiter,body=definition.partition('AS $function$')
            assert delimiter and '$function$' in body,'token_hook_function_definition_shape'
            return ([line for line in header.splitlines() if not line.lstrip().startswith('SET search_path TO ')],
                    body.rsplit('$function$',1)[1])
        assert declaration(before[4])==declaration(after[4]),'token_hook_helper_declaration_changed'

    def revoked_public(self):
        """Characterize a target-only revoked PUBLIC ACL without adopting that drift."""
        import importlib.util
        path=baseline.HERE/'versions/0010_token_hook.py'
        spec=importlib.util.spec_from_file_location('token_hook_source',path)
        revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
        before=self.data_state('clean');db=engine(self.private['owner_urls']['clean'])
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    canonical=c.execute(text(FUNCTION_ACL)).one()
                    c.execute(text('REVOKE EXECUTE ON FUNCTION identity.custom_access_token_hook(jsonb) FROM PUBLIC'))
                    revoked=c.execute(text(FUNCTION_ACL)).one()
                    assert revoked!=canonical
                    c.exec_driver_sql(revision.TOKEN_HOOK_SQL,execution_options={'no_parameters':True})
                    assert c.execute(text(FUNCTION_ACL)).one()==revoked
                    assert c.execute(text("SELECT has_function_privilege('anon','identity.custom_access_token_hook(jsonb)','EXECUTE'),has_function_privilege('authenticated','identity.custom_access_token_hook(jsonb)','EXECUTE')")).one()==(False,False)
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state('clean')==before
        self.passed('token-hook-revoked-public-preserved-rollback-only',adopted=False,normalized=False)

    @contextmanager
    def failure_fixture(self,case):
        state_sql="""SELECT 'function',p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.proname='synthetic_token_hook_failure'
            UNION ALL SELECT 'event_trigger',evtname FROM pg_event_trigger WHERE evtname='synthetic_token_hook_failure' ORDER BY 1,2"""
        before=self.admin_sql(case,state_sql);assert before==[],'token_hook_failure_fixture_already_exists'
        create="""CREATE FUNCTION public.synthetic_token_hook_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN
            IF EXISTS(SELECT 1 FROM pg_proc WHERE oid='identity.custom_access_token_hook(jsonb)'::regprocedure AND proconfig=ARRAY['search_path=pg_catalog, pg_temp']) THEN
                RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_token_hook_failure';
            END IF; END $$;
            CREATE EVENT TRIGGER synthetic_token_hook_failure ON ddl_command_end WHEN TAG IN ('CREATE FUNCTION') EXECUTE FUNCTION public.synthetic_token_hook_failure();"""
        cleanup='DROP EVENT TRIGGER IF EXISTS synthetic_token_hook_failure; DROP FUNCTION IF EXISTS public.synthetic_token_hook_failure()'
        self.witness('token-hook-event-restoration-required',{'case':case,'before':before,'create':create,'cleanup':cleanup})
        with self.restoration_signals():
            try:self.admin_sql(case,create);yield
            finally:
                for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,signal.SIG_IGN)
                self.admin_sql(case,cleanup)
                assert self.admin_sql(case,state_sql)==before,'token_hook_failure_fixture_not_restored'
                self.witness('token-hook-event-restored',{'case':case,'exact_objects':True})

    def upgrades_and_failures(self):
        self.validate_targets();self.prior_evidence(PREVIOUS_COMMIT,PREVIOUS_FILES,'identity_0009')
        self.command('token-hook-clean','clean');self.compatibility();self.reads();self.revoked_public();self.command('token-hook-repeat','clean')
        self.legacy('legacy');self.original_ledger('legacy')
        for case in ['legacy','previous']:
            self.row_fixtures(case)
            before=self.data_state(case,membership_without_revision=case=='legacy');external=self.external_state(case)
            acl=self.sql(case,FUNCTION_ACL)
            self.command('token-hook-'+case,case,mode='adopt' if case=='legacy' else 'clean')
            after=self.data_state(case,membership_without_revision=case=='legacy')
            assert all(after[key]==value for key,value in before.items() if key!='identity.alembic_version')
            assert self.sql(case,FUNCTION_ACL)==acl and self.external_state(case)==external
        with self.failure_fixture('failure'):
            before,catalog=self.data_state('failure'),self.snapshot('failure')
            self.command('token-hook-mid-revision-rollback','failure',expected='identity_migration_failed_requires_reconciliation')
            assert self.data_state('failure')==before and self.snapshot('failure')==catalog
            assert self.sql('failure','SELECT version_num FROM identity.alembic_version')==[('identity_0009',)]
        self.command('token-hook-after-rollback','failure');self.command('token-hook-unsafe-clean','unsafe')
        with self.acl_fixture('unsafe','GRANT INSERT ON identity.users TO authenticated','REVOKE INSERT ON identity.users FROM authenticated',
                'GRANT INSERT (id, username) ON identity.users TO authenticated'):
            before,catalog=self.data_state('unsafe'),self.snapshot('unsafe')
            self.command('token-hook-drift-refused','unsafe',expected='identity_profile_column_privileges_mismatch')
            assert self.data_state('unsafe')==before and self.snapshot('unsafe')==catalog
        self.command('token-hook-drift-reconciled','unsafe')
        self.sql('unknown',"UPDATE identity.alembic_version SET version_num='identity_unknown'")
        before=self.data_state('unknown');self.command('token-hook-unknown','unknown',expected='identity_unknown_history');assert self.data_state('unknown')==before
        self.passed('token-hook-migration-matrix',clean_adopt_head9_repeat=True,exact_acl_preservation=True,mid_revision_rollback=True,drift_and_unknown_refused=True)


def main():
    if not __debug__:raise RuntimeError('token_hook_qualification_optimized_python_prohibited')
    proof,private=fixture();q=TokenHookQualification(proof,private)
    if sys.argv[1:]==['--characterize']:q.validate_targets();q.characterize()
    elif not sys.argv[1:]:q.upgrades_and_failures()
    else:raise RuntimeError('token_hook_qualification_arguments_invalid')


if __name__=='__main__':
    try:main()
    except Exception as error:
        print('token_hook_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None
