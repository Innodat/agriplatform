"""Source-bound synthetic target projection proof using prepared private fixtures.

No infrastructure, roles or credentials are provisioned. Temporary runtime EXECUTE
is fixture-only, restored byte-for-byte, and does not deliver Access authorization.
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
from qualify_actor_command import PREVIOUS_FILES as HEAD5_FILES
from qualify_identity_baseline import baseline, engine, fixture, text

PREVIOUS_COMMIT='48b95c9bfc8a199a84d3746c431312439b1a93e9'
PREVIOUS_FILES=HEAD5_FILES | {'versions/0006_actor_command.py','command-reference.json'}
previous.PREVIOUS_PYTHON=Path(sys.executable)
REQUIRED_CASES=frozenset({'target_reference','clean','legacy','previous','failure','unsafe','unknown','native'})
NIL='00000000-0000-0000-0000-000000000000'
LIST='identity.organization_account_candidates(uuid)'
POINT='identity.organization_account_target(uuid,bigint)'
COLUMNS='account_id::text,membership_id,membership_revision,actor_id::text,display_name'
LIST_SQL='SELECT '+COLUMNS+' FROM identity.organization_account_candidates(CAST(:after AS uuid))'
POINT_SQL='SELECT '+COLUMNS+' FROM identity.organization_account_target(CAST(:target AS uuid),CAST(:member AS bigint))'
ACL_SQL="SELECT p.oid::regprocedure::text,p.proacl::text FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity' AND p.proname IN ('organization_account_candidates','organization_account_target') ORDER BY 1"


class TargetQualification(ProjectionQualification):
    def validate_targets(self):
        for group in ['owner_urls','runtime_urls','databases']:
            assert set(self.private[group])==REQUIRED_CASES,'target_cases_invalid'

    def snapshot(self,case):
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:return baseline.target_catalog_snapshot(c)
        finally:db.dispose()

    @contextmanager
    def fixture_execution(self,case):
        """Bounded fixture grant with durable restoration evidence, never authorization."""
        before=self.sql(case,ACL_SQL)
        assert len(before)==2
        assert self.sql(case,"SELECT has_function_privilege('access_runtime',:list,'EXECUTE'),has_function_privilege('access_runtime',:point,'EXECUTE')",{'list':LIST,'point':POINT})==[(False,False)]
        def witness(name,value):
            path=self.proof/(name+'-'+str(uuid.uuid4())+'.json')
            with path.open('x',encoding='utf-8') as output:
                os.chmod(path,0o600)
                json.dump(value,output,sort_keys=True);output.flush();os.fsync(output.fileno())
        witness('target-acl-restoration-required',{'case':case,'role':'access_runtime','before':[list(r) for r in before],'routines':[LIST,POINT]})
        def change(verb):
            db=engine(self.private['owner_urls'][case])
            try:
                with db.begin() as c:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    c.execute(text('SET LOCAL ROLE identity_target_projection_owner'))
                    c.execute(text(verb+' EXECUTE ON FUNCTION '+LIST+', '+POINT+' '+('TO' if verb=='GRANT' else 'FROM')+' access_runtime'))
            finally:db.dispose()
        def interrupted(signum,frame):
            raise RuntimeError('target_fixture_interrupted')
        old={sig:signal.getsignal(sig) for sig in [signal.SIGINT,signal.SIGTERM]}
        for sig in old:signal.signal(sig,interrupted)
        try:
            try:
                change('GRANT')
                yield
            finally:
                # Block a second termination while bounded restoration unwinds.
                for sig in old:signal.signal(sig,signal.SIG_IGN)
                change('REVOKE')
                after=self.sql(case,ACL_SQL)
                assert after==before,'target_fixture_acl_not_restored'
                witness('target-acl-restored',{'case':case,'after':[list(r) for r in after],'exact_acl_bytes':True})
        finally:
            for sig,handler in old.items():signal.signal(sig,handler)
        self.passed('target-fixture-only-invocation-restored',case=case,exact_acl_bytes=True,access_wrappers_delivered=False)

    def permissions(self):
        for role,allowed in [('access_target_reader',(True,True)),('access_setup_target_reader',(False,True)),('access_command_owner',(False,True)),('access_runtime',(False,False)),('identity_operator',(False,False)),('anon',(False,False)),('authenticated',(False,False)),('service_role',(False,False)),('supabase_auth_admin',(False,False))]:
            assert self.sql('clean',"SELECT has_function_privilege(:role,:list,'EXECUTE'),has_function_privilege(:role,:point,'EXECUTE')",{'role':role,'list':LIST,'point':POINT})==[allowed]
        db=engine(self.private['runtime_urls']['clean'])
        try:
            with db.connect() as c:
                assert c.execute(text('SELECT session_user,current_user')).one()==('access_runtime','access_runtime');c.commit()
                for statement in [LIST_SQL,POINT_SQL,'SELECT * FROM identity.users','SELECT * FROM identity.org','SELECT * FROM identity.org_member','SELECT * FROM identity.account_actor','SELECT * FROM identity.actor',*[('SET ROLE '+role) for role in baseline.TARGET_ROLES],"CREATE FUNCTION identity.synthetic_target() RETURNS integer LANGUAGE sql AS 'SELECT 1'"]:
                    with c.begin():
                        sp=c.begin_nested()
                        try:c.execute(text(statement),{'after':None,'target':None,'member':None})
                        except Exception as error:assert error.orig.sqlstate=='42501'
                        else:raise AssertionError('target_runtime_authority_broadened')
                        finally:sp.rollback()
        finally:db.dispose()
        self.passed('target-exact-caller-acls-and-runtime-denials',raw_tables=False,role_assumption=False)

    def reads(self):
        accounts,actors,system=self.profiles()
        # Two active mapped profiles, one deleted, one unmapped; two organizations.
        orgs=[str(uuid.uuid4()) for _ in range(2)]
        for org in orgs:
            self.sql('clean',"INSERT INTO identity.org(id,name,slug) VALUES (:id,'Synthetic target organization',:slug)",{'id':org,'slug':'synthetic-'+org})
        members={}
        for index in range(4):
            members[index]=self.sql('clean','INSERT INTO identity.org_member(org_id,user_id) VALUES (:org,:account) RETURNING id',{'org':orgs[0],'account':accounts[index]})[0][0]
        other=self.sql('clean','INSERT INTO identity.org_member(org_id,user_id) VALUES (:org,:account) RETURNING id',{'org':orgs[1],'account':accounts[0]})[0][0]
        # More than 100 eligible mapped members detects accidental raw-list limits.
        extras=[{'account':str(uuid.uuid4()),'actor':str(uuid.uuid4())} for _ in range(101)]
        extra_values={'rows':json.dumps(extras),'executor':system,'org':orgs[0]}
        self.sql('clean',"INSERT INTO auth.users(id,email) SELECT account,account::text||'@example.invalid' FROM jsonb_to_recordset(CAST(:rows AS jsonb)) AS x(account uuid,actor uuid)",extra_values,role='databases')
        self.sql('clean',"INSERT INTO identity.actor(id,kind,display_name,created_by,updated_by) SELECT actor,'account','Synthetic extra',CAST(:executor AS uuid),CAST(:executor AS uuid) FROM jsonb_to_recordset(CAST(:rows AS jsonb)) AS x(account uuid,actor uuid)",extra_values)
        self.sql('clean',"INSERT INTO identity.account_actor(account_id,actor_id,actor_kind,created_by) SELECT account,actor,'account',CAST(:executor AS uuid) FROM jsonb_to_recordset(CAST(:rows AS jsonb)) AS x(account uuid,actor uuid)",extra_values)
        extra_members=self.sql('clean',"INSERT INTO identity.org_member(org_id,user_id) SELECT CAST(:org AS uuid),account FROM jsonb_to_recordset(CAST(:rows AS jsonb)) AS x(account uuid,actor uuid) RETURNING user_id::text,id",extra_values)
        member_map=dict(extra_members)
        expected=sorted([(accounts[i],members[i],1,actors[i],'Synthetic actor '+str(i)) for i in [0,1]]+[(row['account'],member_map[row['account']],1,row['actor'],'Synthetic extra') for row in extras])
        before=self.data_state('clean')
        with self.fixture_execution('clean'):
            db=engine(self.private['runtime_urls']['clean'])
            try:
                with db.connect() as c:
                    assert c.execute(text('SELECT session_user,current_user')).one()==('access_runtime','access_runtime');c.commit()
                    def query(kind='user',account=accounts[0],actor=actors[0],org=orgs[0],after=None,target=None,member=None,point=False):
                        with c.begin():
                            for key,value in [('app.context_kind',kind),('app.account_id',account),('app.actor_id',actor),('app.org_id',org)]:
                                if value is not None:c.execute(text('SELECT set_config(:key,:value,true)'),{'key':key,'value':value})
                            return [tuple(r) for r in c.execute(text(POINT_SQL if point else LIST_SQL),{'after':after,'target':target,'member':member})]
                    assert query()==expected
                    assert query(after=expected[0][0])==expected[1:]
                    assert query(after=expected[-1][0])==[]
                    assert query(after=NIL)==[]
                    assert query(account=accounts[0].upper(),actor=actors[0].upper(),org=orgs[0].upper())==expected
                    assert query(org=orgs[1])==[(accounts[0],other,1,actors[0],'Synthetic actor 0')]
                    for i in [0,1]:
                        row=[r for r in expected if r[0]==accounts[i]]
                        assert query(point=True,target=accounts[i],member=members[i])==row
                        assert query(kind='setup',account=None,actor=system,point=True,target=accounts[i],member=members[i])==row
                    assert query(kind='setup',account=None,actor=system)==[]
                    assert query(kind='setup',account=accounts[0],actor=system,point=True,target=accounts[0],member=members[0])==[]
                    for key in ['kind','account','actor','org']:
                        for invalid in [None,'','malformed',NIL,'{'+accounts[0]+'}']:
                            assert query(**{key:invalid})==[]
                            assert query(point=True,target=accounts[0],member=members[0],**{key:invalid})==[]
                    for target,member in [(None,members[0]),(NIL,members[0]),(accounts[0],None),(accounts[0],0),(accounts[0],-1),(accounts[0],members[1]),(accounts[0],other),(accounts[2],members[2]),(accounts[3],members[3]),(str(uuid.uuid4()),members[0])]:
                        assert query(point=True,target=target,member=member)==[]
                    # Typed malformed arguments are rejected before the routine; never rows.
                    for statement,values in [(LIST_SQL,{'after':'malformed'}),(POINT_SQL,{'target':'malformed','member':members[0]})]:
                        with c.begin():
                            sp=c.begin_nested()
                            try:c.execute(text(statement),values)
                            except Exception as error:assert error.orig.sqlstate=='22P02'
                            else:raise AssertionError('malformed_uuid_not_refused')
                            finally:sp.rollback()
                    # SET LOCAL cannot leak on commit, rollback or statement failure.
                    for kind,failure in [('user',False),('setup',False),('user',True),('setup',True)]:
                        t=c.begin()
                        try:
                            c.execute(text("SELECT set_config('app.context_kind',:kind,true),set_config('app.account_id',:account,true),set_config('app.actor_id',:actor,true),set_config('app.org_id',:org,true)"),{'kind':kind,'account':accounts[0] if kind=='user' else '', 'actor':actors[0] if kind=='user' else system,'org':orgs[0]})
                            assert [tuple(r) for r in c.execute(text(POINT_SQL),{'target':accounts[0],'member':members[0]})]==[r for r in expected if r[0]==accounts[0]]
                            assert [tuple(r) for r in c.execute(text(LIST_SQL),{'after':None})]==(expected if kind=='user' else [])
                            if failure:
                                try:c.execute(text('SELECT 1/0'))
                                except Exception as error:assert error.orig.sqlstate=='22012'
                                else:raise AssertionError('missing_injected_failure')
                        finally:t.rollback()
                        assert query(kind=None,account=None,actor=None,org=None)==[]
                        assert query()==expected
                        assert query(kind='setup',account=None,actor=system,point=True,target=accounts[0],member=members[0])==[r for r in expected if r[0]==accounts[0]]
                        assert query(kind=None,account=None,actor=None,org=None)==[]
                    with c.begin():
                        c.execute(text('CREATE TEMP TABLE users(id uuid); CREATE TEMP TABLE org(id uuid); CREATE TEMP TABLE org_member(id bigint); CREATE TEMP TABLE actor(id uuid); CREATE TEMP TABLE account_actor(account_id uuid)'))
                        c.execute(text('SET LOCAL search_path=pg_temp,public,identity'))
                        c.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true),set_config('app.actor_id',:actor,true),set_config('app.org_id',:org,true),set_config('request.jwt.claims','{\"role\":\"service_role\"}',true)"),{'account':accounts[0],'actor':actors[0],'org':orgs[0]})
                        assert [tuple(r) for r in c.execute(text(LIST_SQL),{'after':None})]==expected
                    assert query(kind=None,account=None,actor=None,org=None)==[]
                    assert self.data_state('clean')==before
                    # Same connection, fresh statement observes revisions and retirement.
                    self.sql('clean','UPDATE identity.org_member SET is_owner=true WHERE id=:id',{'id':members[0]})
                    row=(accounts[0],members[0],2,actors[0],'Synthetic actor 0')
                    assert query(point=True,target=accounts[0],member=members[0])==[row]
                    self.sql('clean','UPDATE identity.org_member SET deleted_at=now() WHERE id=:id',{'id':members[0]})
                    assert query(point=True,target=accounts[0],member=members[0])==[]
                    self.sql('clean','UPDATE identity.org_member SET deleted_at=NULL WHERE id=:id',{'id':members[0]})
                    assert query(point=True,target=accounts[0],member=members[0])==[(accounts[0],members[0],4,actors[0],'Synthetic actor 0')]
                    self.sql('clean','UPDATE identity.org SET deleted_at=now() WHERE id=:id',{'id':orgs[0]})
                    assert query()==[]
                    self.sql('clean','UPDATE identity.org SET deleted_at=NULL WHERE id=:id',{'id':orgs[0]})
                    self.sql('clean','UPDATE identity.users SET deleted_at=now() WHERE id=:id',{'id':accounts[0]})
                    assert query(point=True,target=accounts[0],member=members[0])==[]
                    self.sql('clean','UPDATE identity.users SET deleted_at=NULL WHERE id=:id',{'id':accounts[0]})
            finally:db.dispose()
        # Exact direct definer RLS resists old permissive PUBLIC policies.
        db=engine(self.private['owner_urls']['clean'])
        try:
            with db.connect() as c:
                t=c.begin()
                try:
                    c.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true),set_config('app.actor_id',:actor,true),set_config('app.org_id',:org,true),set_config('request.jwt.claims','{\"role\":\"service_role\"}',true)"),{'account':accounts[0],'actor':actors[0],'org':orgs[0]})
                    c.execute(text('SET LOCAL ROLE identity_target_projection_owner'))
                    assert set(c.execute(text('SELECT id FROM identity.org_member')).scalars())==set(members.values())|set(member_map.values())
                    assert c.execute(text('SELECT id::text FROM identity.org')).scalars().all()==[orgs[0]]
                    assert set(c.execute(text('SELECT id::text FROM identity.users')).scalars())=={accounts[0],accounts[1],accounts[3]}|{row['account'] for row in extras}
                    c.execute(text("SELECT set_config('app.actor_id','malformed',true)"))
                    assert c.execute(text('SELECT id FROM identity.org_member')).all()==[]
                    assert c.execute(text('SELECT id FROM identity.users')).all()==[]
                finally:t.rollback()
        finally:db.dispose()
        self.index_and_replacement(accounts[0],actors[0],orgs[0],members[0])
        self.passed('selected-organization-target-read-matrix',complete_ordered_keyset=True,exact_member=True,setup_point_only=True,invalid_context_empty=True,currentness=True,search_path=True,connection_reuse=True,direct_rls=True,no_read_writes=True)

    def index_and_replacement(self,account,actor,org,member):
        before=self.data_state('clean')
        db=engine(self.private['owner_urls']['clean'])
        try:
            with db.connect() as c:
                t=c.begin()
                try:
                    c.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true),set_config('app.actor_id',:actor,true),set_config('app.org_id',:org,true)"),{'account':account,'actor':actor,'org':org})
                    # Only this qualifier's newly inserted synthetic member is replaced.
                    c.execute(text('DELETE FROM identity.org_member WHERE id=:id'),{'id':member})
                    replacement=c.execute(text('INSERT INTO identity.org_member(org_id,user_id) VALUES (:org,:account) RETURNING id'),{'org':org,'account':account}).scalar_one()
                    assert replacement!=member
                    c.execute(text('SET LOCAL ROLE identity_target_projection_owner'))
                    assert c.execute(text(POINT_SQL),{'target':account,'member':member}).all()==[]
                    row=c.execute(text(POINT_SQL),{'target':account,'member':replacement}).one()
                    assert row[:4]==(account,replacement,1,actor)
                    c.execute(text('SET LOCAL enable_seqscan=off'))
                    plan=c.execute(text('EXPLAIN (FORMAT JSON) SELECT id FROM identity.org_member')).scalar_one()
                    def index_conditions(node):
                        return [node.get('Index Cond','')]+[value for child in node.get('Plans',[]) for value in index_conditions(child)]
                    conditions=index_conditions(plan[0]['Plan'])
                    assert any('org_id =' in value and '(org_id)::text' not in value and 'org_id::text' not in value for value in conditions),'target_org_uuid_index_condition_missing'
                    self.passed('target-uuid-index-condition',actual_role='identity_target_projection_owner',uuid_org_index=True,index_conditions=conditions)
                finally:t.rollback()
        finally:db.dispose()
        assert self.data_state('clean')==before
        self.passed('target-exact-replacement-member',old_empty=True,new_exact=True,rollback_rows_unchanged=True)

    def named_defaults(self,case):
        import importlib.util
        path=baseline.HERE/'versions/0007_organization_targets.py'
        spec=importlib.util.spec_from_file_location('target_default_fixture',path)
        revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
        before=self.data_state(case)
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:
                t=c.begin()
                try:
                    baseline.verify_owned_postcondition(c)
                    catalog=baseline.command_catalog_snapshot(c)
                    c.execute(text('ALTER DEFAULT PRIVILEGES IN SCHEMA identity GRANT EXECUTE ON FUNCTIONS TO pg_read_all_settings'))
                    try:baseline.preflight(c,'clean')
                    except baseline.BaselineError as error:assert str(error).startswith('identity_catalog_mismatch:')
                    else:raise AssertionError('unexpected_named_default_preflight_accepted')
                    c.exec_driver_sql(revision.TARGET_SCHEMA_SQL,execution_options={'no_parameters':True})
                    for routine in [LIST,POINT]:
                        assert not c.execute(text("SELECT has_function_privilege('pg_read_all_settings',:routine,'EXECUTE')"),{'routine':routine}).scalar_one()
                    assert c.execute(text("SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace CROSS JOIN LATERAL aclexplode(p.proacl) a WHERE n.nspname='identity' AND p.proname IN ('organization_account_candidates','organization_account_target') AND a.grantee=0")).scalar_one()==0
                finally:t.rollback()
                assert baseline.command_catalog_snapshot(c)==catalog
        finally:db.dispose()
        assert self.data_state(case)==before
        self.passed('target-named-default-acl-stripping',unexpected_named_grantee=True,public_absent=True,rollback_defaults_and_catalog=True)

    def recipient_unsafe(self):
        self.command('target-unsafe-clean','unsafe')
        admin=self.admin('unsafe')
        try:
            mutations=[
                ('recipient-member','GRANT access_target_reader TO access_runtime','REVOKE access_target_reader FROM access_runtime'),
                ('recipient-create','GRANT CREATE ON SCHEMA identity TO access_setup_target_reader','REVOKE CREATE ON SCHEMA identity FROM access_setup_target_reader'),
                ('recipient-column','GRANT SELECT (id) ON identity.users TO access_command_owner','REVOKE SELECT (id) ON identity.users FROM access_command_owner'),
                ('recipient-definer',"CREATE FUNCTION public.synthetic_target_external() RETURNS integer LANGUAGE sql SECURITY DEFINER AS 'SELECT 1'; REVOKE ALL ON FUNCTION public.synthetic_target_external() FROM PUBLIC; GRANT EXECUTE ON FUNCTION public.synthetic_target_external() TO access_target_reader",'DROP FUNCTION public.synthetic_target_external()')]
            for label,mutate,restore in mutations:
                before=self.data_state('unsafe')
                with admin.begin() as c:c.execute(text(mutate))
                try:
                    self.command('target-'+label,'unsafe',expected='identity_target_role_unsafe')
                    assert self.data_state('unsafe')==before
                finally:
                    with admin.begin() as c:c.execute(text(restore))
                self.command('target-'+label+'-reconciled','unsafe')
        finally:admin.dispose()
        self.passed('target-recipient-effective-privilege-refusal',membership=True,schema_create=True,column_read=True,external_definer=True,restored=True)

    def upgrades_and_failures(self):
        self.validate_targets()
        self.prior_evidence(PREVIOUS_COMMIT,PREVIOUS_FILES,'identity_0006')
        self.command('target-clean','clean');self.permissions();self.reads();self.command('target-repeat','clean')
        self.legacy('legacy');self.original_ledger('legacy')
        for case in ['legacy','previous']:
            self.row_fixtures(case)
            if case=='previous':self.named_defaults(case)
            before,external=self.data_state(case,membership_without_revision=case=='legacy'),self.external_state(case)
            self.command('target-'+case,case,mode='adopt' if case=='legacy' else 'clean')
            after=self.data_state(case,membership_without_revision=case=='legacy')
            assert all(after[key]==value for key,value in before.items() if key!='identity.alembic_version')
            assert self.external_state(case)==external
        admin=self.admin('unsafe')
        try:
            for label,unsafe,restore in [
                ('bypass','ALTER ROLE identity_target_projection_owner BYPASSRLS','ALTER ROLE identity_target_projection_owner NOBYPASSRLS'),
                ('runtime-member','GRANT identity_target_projection_owner TO access_runtime','REVOKE identity_target_projection_owner FROM access_runtime')]:
                with admin.begin() as c:c.execute(text(unsafe))
                before=self.data_state('unsafe')
                try:
                    self.command('target-unsafe-'+label,'unsafe',expected='identity_target_role_unsafe')
                    assert self.data_state('unsafe')==before
                finally:
                    with admin.begin() as c:c.execute(text(restore))
        finally:admin.dispose()
        self.recipient_unsafe()
        admin=self.admin('failure')
        try:
            with admin.begin() as c:
                c.execute(text("""CREATE FUNCTION public.synthetic_target_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN IF EXISTS (SELECT 1 FROM pg_event_trigger_ddl_commands() d JOIN pg_proc p ON d.classid='pg_proc'::regclass AND p.oid=d.objid JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity' AND p.proname='organization_account_target') THEN RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_target_failure'; END IF; END $$; CREATE EVENT TRIGGER synthetic_target_failure ON ddl_command_end WHEN TAG IN ('CREATE FUNCTION') EXECUTE FUNCTION public.synthetic_target_failure();"""))
            before,catalog=self.data_state('failure'),self.snapshot('failure')
            self.command('target-mid-write-rollback','failure',expected='identity_migration_failed_requires_reconciliation')
            assert self.data_state('failure')==before and self.snapshot('failure')==catalog
            assert self.sql('failure','SELECT version_num FROM identity.alembic_version')==[('identity_0006',)]
        finally:
            with admin.begin() as c:c.execute(text('DROP EVENT TRIGGER synthetic_target_failure; DROP FUNCTION public.synthetic_target_failure()'))
            admin.dispose()
        self.command('target-after-rollback','failure')
        self.sql('unknown',"UPDATE identity.alembic_version SET version_num='identity_unknown'")
        before=self.data_state('unknown');self.command('target-unknown','unknown',expected='identity_unknown_history');assert self.data_state('unknown')==before
        self.sql('clean','GRANT SELECT (is_owner) ON identity.org_member TO identity_target_projection_owner')
        before=self.data_state('clean')
        try:self.command('target-reader-drift','clean',expected='identity_catalog_mismatch:');assert self.data_state('clean')==before
        finally:self.sql('clean','REVOKE SELECT (is_owner) ON identity.org_member FROM identity_target_projection_owner')
        self.command('target-drift-reconciled','clean')
        self.passed('target-migration-matrix',clean=True,legacy_adopt=True,head6_upgrade=True,repeat=True,old_rows_preserved=True,rollback=True,unknown_refused=True,drift_refused=True)


def main():
    if not __debug__:
        raise RuntimeError('target_qualification_optimized_python_prohibited')
    proof,private=fixture();TargetQualification(proof,private).upgrades_and_failures()


if __name__=='__main__':
    try:main()
    except Exception as error:
        print('target_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None
