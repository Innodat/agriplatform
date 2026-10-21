"""Synthetic stable membership binding proof on root-prepared rollback fixtures."""
from contextlib import contextmanager
from pathlib import Path
import json
from hashlib import sha256
import signal
import sys
import uuid

sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_current_account_actor as previous
from qualify_profile_fields import ProfileQualification, PREVIOUS_FILES as HEAD7_FILES
from qualify_identity_baseline import baseline, engine, fixture, text

PREVIOUS_COMMIT='e8754cc9e53fc57cbc6b45d96725b5bc267b204a'
PREVIOUS_FILES=HEAD7_FILES | {'versions/0008_profile_fields.py','profile-reference.json','versions/0009_legacy_roles.py','legacy-role-reference.json','versions/0010_token_hook.py','token-hook-reference.json'}
previous.PREVIOUS_PYTHON=Path(sys.executable)
REQUIRED_CASES=frozenset({'characterization','membership_binding_reference','clean','legacy','previous','failure','unsafe','unknown','native'})
FUNCTION_ACL="""SELECT pg_get_userbyid(proowner),proacl::text,pg_get_function_identity_arguments(oid),pg_get_function_result(oid),prosecdef,provolatile
    FROM pg_proc WHERE oid='identity.guard_org_member_revision()'::regprocedure"""
NIL='00000000-0000-0000-0000-000000000000'
HOOK_EDGE_SQL="""SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),pg_get_userbyid(grantor),admin_option,to_jsonb(pg_auth_members)->>'inherit_option',to_jsonb(pg_auth_members)->>'set_option' FROM pg_auth_members WHERE pg_get_userbyid(member)='access_runtime' AND pg_get_userbyid(roleid) IN ('authenticated','service_role') ORDER BY 1,2,3"""


class MembershipBindingQualification(ProfileQualification):
    def validate_targets(self):
        for group in ['owner_urls','runtime_urls','databases']:
            assert set(self.private[group])==REQUIRED_CASES,'membership_binding_cases_invalid'
        self.inputs=json.loads((self.proof/'member-binding-fixtures.json').read_text())
        assert set(self.inputs)=={'characterization','clean'}
        for row in self.inputs.values():
            assert set(row)=={'account','other','spare','org','other_org','spare_org','member','other_member','other_org_member','role','deleted_role'}
            assert len({row[key] for key in ['account','other','spare','org','other_org','spare_org']})==6
            for key in ['account','other','spare','org','other_org','spare_org']:
                assert str(uuid.UUID(row[key]))==row[key] and uuid.UUID(row[key]).int
            for key in ['member','other_member','other_org_member','role','deleted_role']:
                assert isinstance(row[key],str) and row[key].isascii() and row[key].isdecimal() and 0<int(row[key])<=9223372036854775807

            assert len({int(row[key]) for key in ['member','other_member','other_org_member']})==3,'membership_binding_fixture_members_not_distinct'
            assert int(row['member'])<=9223372036854775807-1000000,'membership_binding_fixture_id_headroom'

    def fixture_rows(self,case):
        v=self.inputs[case]
        rows=self.sql(case,"SELECT id::text,user_id::text,org_id::text FROM identity.org_member WHERE id IN (CAST(:member AS bigint),CAST(:other_member AS bigint),CAST(:other_org_member AS bigint),CAST(:member AS bigint)+1000000)",v)
        expected={(str(int(v['member'])),v['account'],v['org']),
                  (str(int(v['other_member'])),v['other'],v['org']),
                  (str(int(v['other_org_member'])),v['account'],v['other_org'])}
        assert len(rows)==3 and set(map(tuple,rows))==expected,'membership_binding_fixture_rows_mismatch_or_id_collision'

    def characterization_binding(self):
        return {'proof':str(self.proof.resolve()),
                'run_id':json.loads((self.proof/'run.json').read_text())['run_id'],
                'fixture_sha256':sha256((self.proof/'member-binding-fixtures.json').read_bytes()).hexdigest()}

    def verify_characterization(self,characterized):
        assert characterized['binding']==self.characterization_binding(),'membership_binding_characterization_stale_fixture'
        assert characterized['head']=='identity_0010' and characterized['unchanged_data'] is True
        observed=characterized['observed'];v=self.inputs['characterization']
        assert len(observed)==3 and {row['field'] for row in observed}=={'id','org_id','user_id'},'membership_binding_characterization_fields'
        replacements={'id':int(v['member'])+1000000,'org_id':v['spare_org'],'user_id':v['spare']}
        for row in observed:
            before,after,field=row['before'],row['after'],row['field']
            assert (before['id'],before['org_id'],before['user_id'])==(int(v['member']),v['org'],v['account']),'membership_binding_characterization_original'
            assert after==dict(before,**{field:replacements[field],'revision':before['revision']+1}),'membership_binding_characterization_transition'
            assert row['dependent_roles_removed_rollback_only'] is (field=='id')

    @contextmanager
    def fixture_execution(self,case):
        """Exact absent-edge restoration; no inherited/browser login authority."""
        admin=self.admin(case)
        def edges():
            with admin.begin() as c:
                c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                return [tuple(r) for r in c.execute(text(HOOK_EDGE_SQL))]
        before=edges();assert before==[], 'membership_binding_fixture_edges_already_present'
        self.witness('membership-binding-role-restoration-required',{'case':case,'login':'access_runtime',
            'roles':['authenticated','service_role'],'before':before,'temporary':'SET TRUE INHERIT FALSE ADMIN FALSE'})
        def change(grant):
            with admin.begin() as c:
                c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                c.execute(text('GRANT authenticated, service_role TO access_runtime WITH INHERIT FALSE, SET TRUE' if grant
                               else 'REVOKE authenticated, service_role FROM access_runtime'))
        def interrupted(signum,frame):raise RuntimeError('membership_binding_fixture_interrupted')
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
                assert edges()==before,'membership_binding_fixture_edges_not_restored'
                self.witness('membership-binding-role-restored',{'case':case,'before':before,'after':edges(),'exact_edges':True})
        finally:
            for sig,handler in old.items():signal.signal(sig,handler)
            admin.dispose()
        self.passed('membership-binding-temporary-role-edges-restored',case=case,exact=True,provider_jwt_verification=False)

    def snapshot(self,case):
        db=engine(self.private['owner_urls'][case])
        try:
            with db.begin() as c:
                c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                return baseline.target_catalog_snapshot(c)
        finally:db.dispose()

    @staticmethod
    def state(c):
        """Include every membership, role and audit row, including unrelated rows."""
        return {table:[row[0] for row in c.execute(text('SELECT to_jsonb(t) FROM identity.'+table+' t ORDER BY id'))]
                for table in ['org_member','member_role','audit_log']}

    @contextmanager
    def execution(self,c,v,role='service_role'):
        tx=c.begin()
        try:
            c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
            if role!='access_runtime':c.execute(text('SET LOCAL ROLE '+role))
            c.execute(text("SELECT set_config('request.jwt.claims',:claims,true),set_config('app.context_kind','user',true),set_config('app.account_id',:account,true),set_config('app.org_id',:org,true)"),
                      dict(v,claims=json.dumps({'sub':v['account'],'role':role,'user_roles':['admin'],'org_id':v['org'],'member_id':v['member']})))
            assert c.execute(text('SELECT session_user,current_user')).one()==('access_runtime',role)
            yield
        finally:tx.rollback()

    @staticmethod
    def reject(c,statement,v,state='23514',message='identity_membership_binding_immutable',constraint='org_member_binding_immutable'):
        before=MembershipBindingQualification.state(c) if state!='42501' else None
        savepoint=c.begin_nested()
        try:c.execute(text(statement),v)
        except Exception as error:
            original=getattr(error,'orig',error)
            assert getattr(original,'sqlstate',None)==state
            if message:assert original.diag.message_primary==message
            if constraint:assert original.diag.constraint_name==constraint
        else:raise AssertionError('membership_binding_expected_refusal_missing')
        finally:savepoint.rollback()
        if before is not None:assert MembershipBindingQualification.state(c)==before,'membership_binding_partial_effects'

    def characterize(self):
        case='characterization';v=self.inputs[case]
        self.fixture_rows(case)
        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0010',)]
        before=self.data_state(case);functions=self.snapshot(case)['functions'];observed=[]
        with self.fixture_execution(case):
            db=engine(self.private['runtime_urls'][case])
            try:
                with db.connect() as c:
                    # Original FK prevents changing referenced IDs. Removing synthetic
                    # dependent roles inside this rollback scope isolates the old guard.
                    for field,value in [('id','id+1000000'),('org_id','CAST(:spare_org AS uuid)'),('user_id','CAST(:spare AS uuid)')]:
                        with self.execution(c,v):
                            if field=='id':c.execute(text('DELETE FROM identity.member_role WHERE member_id=CAST(:member AS bigint)'),v)
                            original=c.execute(text('SELECT to_jsonb(t) FROM identity.org_member t WHERE id=CAST(:member AS bigint)'),v).scalar_one()
                            changed=c.execute(text('UPDATE identity.org_member SET '+field+'='+value+' WHERE id=CAST(:member AS bigint) RETURNING to_jsonb(org_member)'),v).scalar_one()
                            assert changed[field]!=original[field] and changed['revision']==original['revision']+1
                            observed.append({'field':field,'before':original,'after':changed,'dependent_roles_removed_rollback_only':field=='id'})
            finally:db.dispose()
        unchanged=self.data_state(case)==before
        self.witness('membership-binding-head10-characterization',{'binding':self.characterization_binding(),'head':'identity_0010','observed':observed,'unchanged_data':unchanged,'functions':functions})
        assert unchanged
        self.passed('membership-binding-head10-characterization',real_login='access_runtime',all_three_fields_accepted=True,rollback_only=True)

    def writes(self):
        case='clean';v=self.inputs[case];self.fixture_rows(case);before=self.data_state(case)
        bindings={'id':'id+1000000','org_id':'CAST(:spare_org AS uuid)','user_id':'CAST(:spare AS uuid)'}
        with self.fixture_execution(case):
            db=engine(self.private['runtime_urls'][case])
            try:
                with db.connect() as c:
                    for retired in [False,True]:
                        with self.execution(c,v):
                            if retired:c.execute(text('UPDATE identity.org_member SET deleted_at=now() WHERE id=CAST(:member AS bigint)'),v)
                            for field,value in bindings.items():
                                for suffix in ['',',is_owner=NOT is_owner']:
                                    self.reject(c,'UPDATE identity.org_member SET '+field+'='+value+suffix+' WHERE id=CAST(:member AS bigint)',v)
                            assignments=[field+'=NULL' for field in bindings]
                            assignments += ['id=id+1000000,org_id=CAST(:spare_org AS uuid)',
                                            'id=id+1000000,user_id=CAST(:spare AS uuid)',
                                            'org_id=CAST(:spare_org AS uuid),user_id=CAST(:spare AS uuid)',
                                            'id=id+1000000,org_id=CAST(:spare_org AS uuid),user_id=CAST(:spare AS uuid)']
                            for assignment in assignments:
                                self.reject(c,'UPDATE identity.org_member SET '+assignment+' WHERE id=CAST(:member AS bigint)',v)
                            self.reject(c,"WITH permitted AS (UPDATE identity.org_member SET is_owner=NOT is_owner WHERE id=CAST(:other_member AS bigint) RETURNING id) UPDATE identity.org_member SET user_id=CAST(:spare AS uuid) WHERE id=CAST(:member AS bigint) AND EXISTS(SELECT 1 FROM permitted)",v)
                            self.reject(c,"UPDATE identity.org_member SET is_owner=NOT is_owner,user_id=CASE WHEN id=CAST(:member AS bigint) THEN CAST(:spare AS uuid) ELSE user_id END WHERE id IN (CAST(:member AS bigint),CAST(:other_member AS bigint))",v)
                    with self.execution(c,v):
                        original=c.execute(text('SELECT to_jsonb(t) FROM identity.org_member t WHERE id=CAST(:member AS bigint)'),v).scalar_one()
                        row=c.execute(text('UPDATE identity.org_member SET id=id,org_id=org_id,user_id=user_id,revision=999 WHERE id=CAST(:member AS bigint) RETURNING to_jsonb(org_member)'),v).scalar_one()
                        assert row==original
                        for change in ['is_owner=NOT is_owner','updated_by=CAST(:other AS uuid)',"updated_at='2001-01-01'::timestamptz",'deleted_at=now()','deleted_at=NULL']:
                            updated=c.execute(text('UPDATE identity.org_member SET '+change+' WHERE id=CAST(:member AS bigint) RETURNING revision'),v).scalar_one()
                            assert updated==row['revision']+1
                            row=c.execute(text('SELECT to_jsonb(t) FROM identity.org_member t WHERE id=CAST(:member AS bigint)'),v).scalar_one()
                        inserted=c.execute(text('INSERT INTO identity.org_member(id,org_id,user_id,is_owner,revision) VALUES (CAST(:member AS bigint)+1000000,CAST(:spare_org AS uuid),CAST(:spare AS uuid),false,999) RETURNING id,revision'),v).one()
                        assert inserted==(int(v['member'])+1000000,1)
                    self.seed_compatibility(c,v)
                    self.read_compatibility(c,v)
                    for role in ['authenticated','access_runtime']:
                        with self.execution(c,v,role):
                            for statement in ['UPDATE identity.org_member SET is_owner=false','UPDATE identity.org_member SET user_id=CAST(:spare AS uuid)',
                                              'INSERT INTO identity.org_member(org_id,user_id) VALUES(CAST(:spare_org AS uuid),CAST(:spare AS uuid))']:
                                self.reject(c,statement,v,'42501',None,None)
            finally:db.dispose()
        self.overflow(v)
        assert self.data_state(case)==before
        self.passed('membership-binding-write-matrix',active_retired_mixed_multirow=True,unchanged_row_roles_audit=True,
            mutable_noop_insert_revision=True,seed_upsert_lookup=True,browser_runtime_denied=True,overflow=True,rollback_only=True)

    def seed_compatibility(self,c,v):
        with self.execution(c,v):
            # scripts/seed.py's exact supported conflict target and mutable payload.
            original=c.execute(text('SELECT to_jsonb(t) FROM identity.org_member t WHERE id=CAST(:member AS bigint)'),v).scalar_one()
            roles=list(c.execute(text('SELECT to_jsonb(t) FROM identity.member_role t ORDER BY id')))
            c.execute(text('UPDATE identity.org_member SET deleted_at=now() WHERE id=CAST(:member AS bigint)'),v)
            retired=c.execute(text('SELECT revision FROM identity.org_member WHERE id=CAST(:member AS bigint)'),v).scalar_one()
            row=c.execute(text('INSERT INTO identity.org_member(org_id,user_id,is_owner,deleted_at) VALUES(CAST(:org AS uuid),CAST(:account AS uuid),true,NULL) ON CONFLICT(org_id,user_id) DO UPDATE SET is_owner=excluded.is_owner,deleted_at=excluded.deleted_at RETURNING to_jsonb(org_member)'),v).scalar_one()
            assert row['id']==original['id'] and row['deleted_at'] is None and row['revision']==retired+1
            # Retained SQL seed lookup intentionally has no active-only predicate.
            lookup='SELECT id FROM identity.org_member WHERE org_id=CAST(:org AS uuid) AND user_id=CAST(:account AS uuid)'
            assert c.execute(text(lookup),v).scalar_one()==original['id']
            assert list(c.execute(text('SELECT to_jsonb(t) FROM identity.member_role t ORDER BY id')))==roles
            # Existing token/public role readers and exact current account projections
            # remain exercised by unchanged historical qualification/source custody.
            self.witness('membership-binding-seed-compatibility',{'original_id':original['id'],'revision_after_upsert':row['revision'],'retired_seed_unretired':True,'roles_unchanged':True})

    def read_compatibility(self,c,v):
        with self.execution(c,v,'authenticated'):
            assert [r[0] for r in c.execute(text('SELECT role FROM public.get_user_roles()'))]==['admin']
        with self.execution(c,v):
            event={'user_id':v['account'],'claims':{},'user_metadata':{'current_org_id':v['org']}}
            claims=c.execute(text('SELECT identity.custom_access_token_hook(CAST(:event AS jsonb))'),{'event':json.dumps(event)}).scalar_one()['claims']
            assert claims['member_id']==int(v['member']) and claims['role_ids']==[int(v['role'])] and claims['user_roles']==['admin']
        with self.execution(c,v,'access_runtime'):
            row=c.execute(text('SELECT account_id::text,org_id::text,membership_id FROM identity.current_account_organization()')).one()
            assert row==(v['account'],v['org'],int(v['member']))
        for role in ['authenticated','service_role','access_runtime']:
            with self.execution(c,v,role):
                c.execute(text('SET LOCAL ROLE service_role'))
                c.execute(text('UPDATE identity.org_member SET deleted_at=now() WHERE id=CAST(:member AS bigint)'),v)
                c.execute(text('SET LOCAL ROLE '+role))
                if role=='authenticated':
                    assert list(c.execute(text('SELECT role FROM public.get_user_roles()')))==[]
                elif role=='service_role':
                    event={'user_id':v['account'],'claims':{},'user_metadata':{'current_org_id':v['org']}}
                    claims=c.execute(text('SELECT identity.custom_access_token_hook(CAST(:event AS jsonb))'),{'event':json.dumps(event)}).scalar_one()['claims']
                    assert claims['member_id'] is None and claims['role_ids']==[] and claims['user_roles']==[] and claims['is_org_owner'] is False
                else:
                    assert list(c.execute(text('SELECT * FROM identity.current_account_organization()')))==[]
        self.passed('membership-binding-restricted-read-compatibility',legacy_roles=True,token_hook=True,current_account=True,provider_authentication_claim=False)

    def overflow(self,v):
        """Only rollback fixture DDL supplies unreachable max revision test input."""
        db=engine(self.private['owner_urls']['clean'])
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    import importlib.util
                    path=baseline.HERE/'versions/0011_membership_binding.py'
                    spec=importlib.util.spec_from_file_location('binding_overflow_source',path)
                    revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
                    seed_sql=revision.MEMBERSHIP_BINDING_SQL.replace('NEW.revision := OLD.revision;', 'NEW.revision := 9223372036854775807;')
                    c.exec_driver_sql(seed_sql,execution_options={'no_parameters':True})
                    c.execute(text('UPDATE identity.org_member SET revision=revision WHERE id=CAST(:member AS bigint)'),v)
                    c.exec_driver_sql(revision.MEMBERSHIP_BINDING_SQL,execution_options={'no_parameters':True})
                    assert c.execute(text('UPDATE identity.org_member SET id=id,revision=1 WHERE id=CAST(:member AS bigint) RETURNING revision'),v).scalar_one()==9223372036854775807
                    for statement in ['UPDATE identity.org_member SET is_owner=NOT is_owner WHERE id=CAST(:member AS bigint)',
                                      'UPDATE identity.org_member SET is_owner=NOT is_owner WHERE id IN(CAST(:member AS bigint),CAST(:other_member AS bigint))']:
                        self.reject(c,statement,v,'23514','identity_membership_revision_exhausted','org_member_revision_positive')
                    self.reject(c,'UPDATE identity.org_member SET user_id=CAST(:spare AS uuid) WHERE id=CAST(:member AS bigint)',v)
                finally:tx.rollback()
        finally:db.dispose()

    def compatibility(self):
        current=baseline.catalog_fingerprints(self.snapshot('clean'))
        prior=baseline.trusted_token_hook_reference();baseline.compare_catalog(current,baseline.trusted_membership_binding_reference())
        assert prior.keys()==current.keys()
        assert {key for key in prior if prior[key]!=current[key]}=={'functions'}
        witnesses=sorted(self.proof.glob('membership-binding-head10-characterization-*.json'),key=lambda path:path.stat().st_mtime_ns)
        assert witnesses,'membership_binding_missing_head10_characterization'
        characterized=json.loads(witnesses[-1].read_text())
        self.verify_characterization(characterized)
        old_functions=characterized['functions'];new_functions=self.snapshot('clean')['functions']
        assert baseline.catalog_fingerprints({'functions':old_functions})['functions']==prior['functions']
        self.verify_function_delta(old_functions,new_functions)
        self.passed('membership-binding-only-function-catalog-change',other_hooks_seeds_profile_acl_roles_unchanged=True,
            per_function_rows_compared=True,exact_helper_owner_acl_preserved=True)

    @staticmethod
    def verify_function_delta(old_rows,new_rows):
        old={tuple(row[:3]):row for row in old_rows};new={tuple(row[:3]):row for row in new_rows}
        assert old.keys()==new.keys(),'membership_binding_function_set_changed'
        helper=('identity','guard_org_member_revision','')
        assert {key for key in old if old[key]!=new[key]}=={helper},'membership_binding_other_function_changed'
        before,after=old[helper],new[helper]
        assert before[:4]==after[:4] and before[5:]==after[5:],'membership_binding_helper_owner_acl_changed'
        # pg_get_functiondef includes language/security/volatility/signature; remove
        # only the body before comparing its exact declaration, including search_path.
        def declaration(definition):
            header,delimiter,body=definition.partition('AS $function$')
            assert delimiter and '$function$' in body,'membership_binding_function_definition_shape'
            return (header,
                    body.rsplit('$function$',1)[1])
        assert declaration(before[4])==declaration(after[4]),'membership_binding_helper_declaration_changed'

    @contextmanager
    def failure_fixture(self,case):
        state_sql="""SELECT 'function',p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.proname='synthetic_membership_binding_failure'
            UNION ALL SELECT 'event_trigger',evtname FROM pg_event_trigger WHERE evtname='synthetic_membership_binding_failure' ORDER BY 1,2"""
        before=self.admin_sql(case,state_sql);assert before==[],'membership_binding_failure_fixture_already_exists'
        create="""CREATE FUNCTION public.synthetic_membership_binding_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN
            IF EXISTS(SELECT 1 FROM pg_proc WHERE oid='identity.guard_org_member_revision()'::regprocedure AND prosrc LIKE '%identity_membership_binding_immutable%') THEN
                RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_membership_binding_failure';
            END IF; END $$;
            CREATE EVENT TRIGGER synthetic_membership_binding_failure ON ddl_command_end WHEN TAG IN ('CREATE FUNCTION') EXECUTE FUNCTION public.synthetic_membership_binding_failure();"""
        cleanup='DROP EVENT TRIGGER IF EXISTS synthetic_membership_binding_failure; DROP FUNCTION IF EXISTS public.synthetic_membership_binding_failure()'
        self.witness('membership-binding-event-restoration-required',{'case':case,'before':before,'create':create,'cleanup':cleanup})
        with self.restoration_signals():
            try:self.admin_sql(case,create);yield
            finally:
                for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,signal.SIG_IGN)
                self.admin_sql(case,cleanup)
                assert self.admin_sql(case,state_sql)==before,'membership_binding_failure_fixture_not_restored'
                self.witness('membership-binding-event-restored',{'case':case,'exact_objects':True})

    def upgrades_and_failures(self):
        self.validate_targets();self.prior_evidence(PREVIOUS_COMMIT,PREVIOUS_FILES,'identity_0010')
        self.command('membership-binding-clean','clean');self.compatibility();self.writes();self.command('membership-binding-repeat','clean')
        self.legacy('legacy');self.original_ledger('legacy')
        for case in ['legacy','previous']:
            self.row_fixtures(case)
            before=self.data_state(case,membership_without_revision=case=='legacy');external=self.external_state(case)
            acl=self.sql(case,FUNCTION_ACL) if case=='previous' else None
            self.command('membership-binding-'+case,case,mode='adopt' if case=='legacy' else 'clean')
            after=self.data_state(case,membership_without_revision=case=='legacy')
            assert all(after[key]==value for key,value in before.items() if key!='identity.alembic_version')
            assert (acl is None or self.sql(case,FUNCTION_ACL)==acl) and self.external_state(case)==external
        with self.failure_fixture('failure'):
            before,catalog=self.data_state('failure'),self.snapshot('failure')
            self.command('membership-binding-mid-revision-rollback','failure',expected='identity_migration_failed_requires_reconciliation')
            assert self.data_state('failure')==before and self.snapshot('failure')==catalog
            assert self.sql('failure','SELECT version_num FROM identity.alembic_version')==[('identity_0010',)]
        self.command('membership-binding-after-rollback','failure');self.command('membership-binding-unsafe-clean','unsafe')
        with self.acl_fixture('unsafe','GRANT INSERT ON identity.users TO authenticated','REVOKE INSERT ON identity.users FROM authenticated',
                'GRANT INSERT (id, username) ON identity.users TO authenticated'):
            before,catalog=self.data_state('unsafe'),self.snapshot('unsafe')
            self.command('membership-binding-drift-refused','unsafe',expected='identity_profile_column_privileges_mismatch')
            assert self.data_state('unsafe')==before and self.snapshot('unsafe')==catalog
        self.command('membership-binding-drift-reconciled','unsafe')
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
        self.passed('membership-binding-unknown-direct-owner-preflight',rollback_only=True,subprocess_migration_claim=False)
        self.passed('membership-binding-migration-matrix',clean_adopt_head10_repeat=True,exact_acl_preservation=True,mid_revision_rollback=True,drift_and_unknown_refused=True)


def main():
    if not __debug__:raise RuntimeError('membership_binding_qualification_optimized_python_prohibited')
    proof,private=fixture();q=MembershipBindingQualification(proof,private)
    if sys.argv[1:]==['--characterize']:q.validate_targets();q.characterize()
    elif not sys.argv[1:]:q.upgrades_and_failures()
    else:raise RuntimeError('membership_binding_qualification_arguments_invalid')


if __name__=='__main__':
    try:main()
    except Exception as error:
        print('membership_binding_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None
