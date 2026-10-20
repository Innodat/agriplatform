"""Actual restricted-login ID-B selected organization and legacy revision proof.

Only the validated existing qualification frame is consumed. No environment resources
or roles are created, and all writes are isolated synthetic fixture mutations.
"""
import json
from pathlib import Path
import sys
import threading
import time
import uuid
from urllib.parse import quote, urlsplit, urlunsplit

sys.path.insert(0,str(Path(__file__).resolve().parent))
from qualify_current_account_actor import ProjectionQualification, PREVIOUS_FILES as ACTOR_FILES
from qualify_identity_baseline import baseline, engine, fixture, text

PREVIOUS_COMMIT='18c5b94566045dcca9973ce3365ea1af95e6287d'
PREVIOUS_FILES=ACTOR_FILES | {'versions/0003_current_account_actor.py','projection-reference.json'}
READ_SQL='SELECT account_id::text,org_id::text,membership_id,membership_revision,actor_id::text FROM identity.current_account_organization()'
NIL='00000000-0000-0000-0000-000000000000'


class OrganizationQualification(ProjectionQualification):
    def old_rows(self,case):
        # Revision is the sole additive business-row field. Preserve every old value.
        return self.sql(case,"SELECT to_jsonb(m)-'revision' FROM identity.org_member m ORDER BY id")

    def reads(self):
        accounts,actors,system=self.profiles()
        orgs=[str(uuid.uuid4()) for _ in range(3)]
        for org in orgs:
            self.sql('clean',"INSERT INTO identity.org(id,name,slug) VALUES (:id,'Synthetic selected organization',:slug)",{'id':org,'slug':'synthetic-'+org})
        members=[]
        for account,org in [(accounts[0],orgs[0]),(accounts[1],orgs[1]),(accounts[2],orgs[0]),(accounts[3],orgs[0]),(accounts[0],orgs[2])]:
            members.append(self.sql('clean','INSERT INTO identity.org_member(org_id,user_id,revision) VALUES (:org,:account,999) RETURNING id,revision',{'org':org,'account':account})[0][0])
        self.sql('clean','UPDATE identity.org SET deleted_at=now() WHERE id=:id',{'id':orgs[2]})
        before=self.data_state('clean')
        db=engine(self.private['runtime_urls']['clean'])
        try:
            with db.connect() as connection:
                assert connection.execute(text('SELECT session_user,current_user')).one()==('access_runtime','access_runtime');connection.commit()
                def query(kind=None,account=None,org=None,actor=None,claims=None):
                    with connection.begin():
                        for key,value in [('app.context_kind',kind),('app.account_id',account),('app.org_id',org),('app.actor_id',actor),('request.jwt.claims',claims)]:
                            if value is not None:connection.execute(text('SELECT set_config(:key,:value,true)'),{'key':key,'value':value})
                        return [tuple(row) for row in connection.execute(text(READ_SQL))]
                expected=[(accounts[0],orgs[0],members[0],1,actors[0])]
                assert query()==[]
                assert query('user',accounts[0],orgs[0],actors[1],json.dumps({'role':'service_role','sub':accounts[1]}))==expected
                assert query()==[]
                assert query('user',accounts[0].upper(),orgs[0].upper())==expected
                assert query('user',accounts[3],orgs[0])==[(accounts[3],orgs[0],members[3],1,None)]
                assert query('user',accounts[1],orgs[1])==[(accounts[1],orgs[1],members[1],1,actors[1])]
                for account,org in [(accounts[0],orgs[1]),(accounts[1],orgs[0]),(accounts[2],orgs[0]),(accounts[0],orgs[2]),(str(uuid.uuid4()),orgs[0]),(accounts[0],str(uuid.uuid4()))]:
                    assert query('user',account,org)==[]
                for kind in [None,'','setup','worker']:
                    assert query(kind,accounts[0],orgs[0])==[]
                for invalid in [None,'','bad-uuid',NIL,'{'+accounts[0]+'}']:
                    assert query('user',invalid,orgs[0],actors[0])==[]
                    assert query('user',accounts[0],invalid,actors[0])==[]
                # Rollback and statement failure release SET LOCAL on this physical connection.
                for fail in [False,True]:
                    transaction=connection.begin()
                    try:
                        connection.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true),set_config('app.org_id',:org,true)"),{'account':accounts[0],'org':orgs[0]})
                        assert [tuple(row) for row in connection.execute(text(READ_SQL))]==expected
                        if fail:
                            try:connection.execute(text('SELECT 1/0'))
                            except Exception as error:assert error.orig.sqlstate=='22012'
                            else:raise AssertionError('missing_synthetic_failure')
                    finally:transaction.rollback()
                    assert query()==[]
                for statement in ['SELECT * FROM identity.org','SELECT * FROM identity.org_member','SELECT revision FROM identity.org_member','SELECT * FROM identity.users','SELECT * FROM identity.account_actor','UPDATE identity.org_member SET is_owner=true','SET ROLE identity_account_projection_owner',"CREATE OR REPLACE FUNCTION identity.current_account_organization() RETURNS TABLE(account_id uuid,org_id uuid,membership_id bigint,membership_revision bigint,actor_id uuid) LANGUAGE sql AS 'SELECT NULL::uuid,NULL::uuid,NULL::bigint,NULL::bigint,NULL::uuid'"]:
                    with connection.begin():
                        savepoint=connection.begin_nested()
                        try:connection.execute(text(statement))
                        except Exception as error:assert error.orig.sqlstate=='42501'
                        else:raise AssertionError('runtime_authority_broadened')
                        finally:savepoint.rollback()
                with connection.begin():
                    connection.execute(text('CREATE TEMP TABLE org(id uuid,deleted_at timestamptz); CREATE TEMP TABLE org_member(id bigint,org_id uuid,user_id uuid,deleted_at timestamptz,revision bigint)'))
                    connection.execute(text('INSERT INTO org VALUES (:org,NULL)'),{'org':orgs[0]})
                    connection.execute(text('INSERT INTO org_member VALUES (999,:org,:account,NULL,999)'),{'org':orgs[0],'account':accounts[0]})
                    connection.execute(text('SET LOCAL search_path=pg_temp,public,identity'))
                    connection.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true),set_config('app.org_id',:org,true)"),{'account':accounts[0],'org':orgs[0]})
                    assert [tuple(row) for row in connection.execute(text(READ_SQL))]==expected
                assert query()==[]
        finally:db.dispose()
        assert self.data_state('clean')==before
        # Direct reader-role RLS must resist legacy PUBLIC claims too.
        db=engine(self.private['owner_urls']['clean'])
        try:
            with db.connect() as c:
                t=c.begin()
                try:
                    c.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true),set_config('app.org_id',:org,true),set_config('request.jwt.claims',:claims,true)"),{'account':accounts[0],'org':orgs[0],'claims':json.dumps({'role':'service_role','sub':accounts[1]})})
                    c.execute(text('SET LOCAL ROLE identity_account_projection_owner'))
                    assert c.execute(text('SELECT id FROM identity.org_member')).scalars().all()==[members[0]]
                    assert c.execute(text('SELECT id::text FROM identity.org')).scalars().all()==[orgs[0]]
                    c.execute(text("SELECT set_config('app.account_id','',true)"))
                    assert c.execute(text('SELECT id FROM identity.org_member')).all()==[]
                finally:t.rollback()
        finally:db.dispose()
        for role in ['anon','authenticated','service_role','supabase_auth_admin']:
            assert self.sql('clean',"SELECT has_function_privilege(:role,'identity.current_account_organization()','EXECUTE'),has_function_privilege(:role,'identity.guard_org_member_revision()','EXECUTE')",{'role':role})==[(False,False)]
        self.sql('clean','UPDATE identity.org_member SET deleted_at=now() WHERE id=:id',{'id':members[0]})
        db=engine(self.private['runtime_urls']['clean'])
        try:
            with db.begin() as c:
                c.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true),set_config('app.org_id',:org,true)"),{'account':accounts[0],'org':orgs[0]})
                assert c.execute(text(READ_SQL)).all()==[]
        finally:db.dispose()
        self.sql('clean','UPDATE identity.org_member SET deleted_at=NULL WHERE id=:id',{'id':members[0]})
        self.revisions(accounts,orgs,members)
        self.token_hook('clean',accounts[0],orgs[0],members[0])
        self.projected_revision(accounts[0],orgs[0],members[0],actors[0])
        self.revision_contention(members[1])
        self.seed_writer(accounts,orgs)
        self.passed('restricted-selected-organization-matrix',mapped=True,unmapped_nullable=True,no_read_writes=True,reader_rls=True,connection_reuse=True,search_path=True,legacy_runtime_unchanged=True)

    def projected_revision(self,account,org,member,actor):
        prior=self.sql('clean','SELECT revision FROM identity.org_member WHERE id=:id',{'id':member})[0][0]
        self.sql('clean','UPDATE identity.org_member SET is_owner=true WHERE id=:id',{'id':member})
        def actual_projection():
            db=engine(self.private['runtime_urls']['clean'])
            try:
                with db.begin() as c:
                    assert c.execute(text('SELECT session_user,current_user')).one()==('access_runtime','access_runtime')
                    c.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true),set_config('app.org_id',:org,true)"),{'account':account,'org':org})
                    return [tuple(row) for row in c.execute(text(READ_SQL))]
            finally:db.dispose()
        expected=[(account,org,member,prior+1,actor)]
        assert actual_projection()==expected
        self.sql('clean','UPDATE identity.org_member SET is_owner=true,revision=1 WHERE id=:id',{'id':member})
        assert actual_projection()==expected
        self.passed('committed-membership-revision-projection',changed_advanced=True,committed_noop_stable=True,actual_login='access_runtime')

    def revision_contention(self,member):
        prior=self.sql('clean','SELECT revision FROM identity.org_member WHERE id=:id',{'id':member})[0][0]
        db=engine(self.private['owner_urls']['clean'])
        ready,finished=threading.Event(),threading.Event();contender={}
        def competing_update():
            try:
                with db.connect() as c:
                    t=c.begin()
                    try:
                        c.exec_driver_sql("SET LOCAL lock_timeout='5s'")
                        c.exec_driver_sql("SET LOCAL statement_timeout='8s'")
                        contender['pid']=c.execute(text('SELECT pg_backend_pid()')).scalar_one();ready.set()
                        contender['revision']=c.execute(text("UPDATE identity.org_member SET updated_at='2026-01-02T00:00:00Z' WHERE id=:id RETURNING revision"),{'id':member}).scalar_one()
                        t.commit();contender['state']='committed'
                    except Exception as error:
                        contender['state']=getattr(getattr(error,'orig',error),'sqlstate',None)
                    finally:
                        if t.is_active:t.rollback()
            except Exception:contender['state']='connection_failed'
            finally:finished.set()
        thread=threading.Thread(target=competing_update,daemon=True)
        try:
            with db.connect() as winner:
                t=winner.begin()
                try:
                    winner.exec_driver_sql("SET LOCAL statement_timeout='8s'")
                    winner_pid=winner.execute(text('SELECT pg_backend_pid()')).scalar_one()
                    assert winner.execute(text('UPDATE identity.org_member SET is_owner=true WHERE id=:id RETURNING revision'),{'id':member}).scalar_one()==prior+1
                    thread.start();assert ready.wait(3), 'revision_contender_not_ready'
                    deadline=time.monotonic()+3;blocked=False
                    while time.monotonic()<deadline and not finished.is_set():
                        if winner_pid in winner.execute(text('SELECT pg_blocking_pids(:pid)'),{'pid':contender['pid']}).scalar_one():
                            blocked=True;break
                        time.sleep(0.02)
                    assert blocked and not finished.is_set(), 'revision_contender_did_not_block'
                    t.commit()
                finally:
                    if t.is_active:t.rollback()
            assert finished.wait(6), 'revision_contender_did_not_finish'
            thread.join(timeout=1)
            assert contender.get('state')=='committed', 'revision_contender_not_committed'
            assert contender['revision']==prior+2
            assert self.sql('clean',"SELECT revision,is_owner,updated_at='2026-01-02T00:00:00Z'::timestamptz FROM identity.org_member WHERE id=:id",{'id':member})==[(prior+2,True,True)]
        finally:
            if thread.is_alive():thread.join(timeout=9)
            db.dispose()
        self.passed('membership-revision-competing-commits',two_connections=True,blocked_writer_observed=True,two_committed_changes=True,no_lost_increment=True)

    def seed_writer(self,accounts,orgs):
        # Vendor postgres is the privileged retained SQL-seed principal. Record its
        # actual owner membership/inheritance; neither implies a service_role or
        # PostgREST endpoint qualification.
        db=engine(self.private['databases']['clean'])
        try:
            with db.connect() as c:
                t=c.begin()
                try:
                    assert c.execute(text('SELECT session_user,current_user')).one()==('postgres','postgres')
                    inherited=c.execute(text("SELECT pg_has_role(current_user,'identity_migrator','USAGE')")).scalar_one()
                    membership=c.execute(text("SELECT pg_has_role(current_user,'identity_migrator','MEMBER')")).scalar_one()
                    first=c.execute(text('INSERT INTO identity.org_member(org_id,user_id) VALUES (:org,:account) RETURNING id,revision'),{'org':orgs[1],'account':accounts[3]}).one()
                    second=c.execute(text('INSERT INTO identity.org_member(org_id,user_id,revision) VALUES (:org,:account,999) RETURNING id,revision'),{'org':orgs[1],'account':accounts[0]}).one()
                    assert first[1]==second[1]==1
                    assert c.execute(text('UPDATE identity.org_member SET is_owner=true,revision=999 WHERE id=:id RETURNING revision'),{'id':first[0]}).scalar_one()==2
                    assert c.execute(text('UPDATE identity.org_member SET is_owner=true WHERE id=:id RETURNING revision'),{'id':first[0]}).scalar_one()==2
                    assert c.execute(text('UPDATE identity.org_member SET revision=0 WHERE id=:id RETURNING revision'),{'id':first[0]}).scalar_one()==2
                finally:t.rollback()
        finally:db.dispose()
        self.passed('retained-sql-seed-postgres-writer',actual_login='postgres',vendor_owner_membership=membership,vendor_owner_inheritance=inherited,default_and_forged_insert=True,changed_noop_forged_update=True,service_role_or_postgrest_qualified=False,grant_changes=False)

    def token_hook(self,case,account,org,member):
        role_id=self.sql(case,"INSERT INTO identity.member_role(member_id,role) VALUES (:member,'employee') RETURNING id",{'member':member})[0][0]
        slug=self.sql(case,'SELECT slug FROM identity.org WHERE id=:org',{'org':org})[0][0]
        parsed=urlsplit(self.private['databases'][case])
        auth_url=urlunsplit(parsed._replace(netloc='supabase_auth_admin:'+quote(parsed.password or '',safe='')+'@'+parsed.hostname+':'+str(parsed.port)))
        db=engine(auth_url)
        try:
            with db.begin() as c:
                assert c.execute(text('SELECT session_user,current_user')).one()==('supabase_auth_admin','supabase_auth_admin')
                event={'user_id':account,'user_metadata':{'current_org_id':org},'claims':{'sub':account,'synthetic_preserved':True}}
                result=c.execute(text('SELECT identity.custom_access_token_hook(CAST(:event AS jsonb))'),{'event':json.dumps(event)}).scalar_one()
                claims=result['claims']
                assert result['user_id']==account and claims['sub']==account and claims['synthetic_preserved'] is True
                assert claims['org_id']==org and claims['org_slug']==slug and claims['member_id']==member
                assert claims['user_roles']==['employee'] and claims['role_ids']==[role_id]
                assert org in claims['org_ids'] and claims['is_org_owner'] is False
        finally:db.dispose()
        self.passed('legacy-token-hook-with-membership',actual_login='supabase_auth_admin',vendor_jwt_pipeline=False,profile_account_unchanged=True)

    def revisions(self,accounts,orgs,members):
        db=engine(self.private['owner_urls']['clean'])
        try:
            with db.connect() as c:
                t=c.begin()
                try:
                    member=members[0]
                    def row():return c.execute(text('SELECT to_jsonb(m) FROM identity.org_member m WHERE id=:id'),{'id':member}).scalar_one()
                    original=row();expected=original['revision']
                    # Caller-supplied revisions cannot forge or decrement; no-op is stable.
                    for forged in [0,-1,999999,None]:
                        c.execute(text('UPDATE identity.org_member SET revision=:revision WHERE id=:id'),{'revision':forged,'id':member})
                        assert row()==original
                    # Every persisted legacy field participates, including identity/attribution/time.
                    for field,value in [('is_owner',True),('created_by',accounts[0]),('updated_by',accounts[1]),('created_at','2026-01-01T00:00:00Z'),('updated_at','2026-02-01T00:00:00Z'),('deleted_at','2026-03-01T00:00:00Z'),('deleted_at',None),('org_id',orgs[1]),('org_id',orgs[0]),('user_id',accounts[1]),('user_id',accounts[0])]:
                        c.execute(text('UPDATE identity.org_member SET '+field+'=:value,revision=777 WHERE id=:id'),{'value':value,'id':member})
                        expected+=1;assert row()['revision']==expected
                    changed_id=member+100000
                    c.execute(text('UPDATE identity.org_member SET id=:new WHERE id=:id'),{'new':changed_id,'id':member});member=changed_id;expected+=1
                    assert row()['revision']==expected
                    c.execute(text('UPDATE identity.org_member SET id=:new WHERE id=:id'),{'new':members[0],'id':member});member=members[0];expected+=1
                    assert row()['revision']==expected
                    # Reproduce supported seed ON CONFLICT and unretire exactly.
                    sql='INSERT INTO identity.org_member(org_id,user_id,is_owner,deleted_at) VALUES (:org,:account,:owner,NULL) ON CONFLICT(org_id,user_id) DO UPDATE SET is_owner=EXCLUDED.is_owner,deleted_at=EXCLUDED.deleted_at RETURNING id,revision'
                    assert tuple(c.execute(text(sql),{'org':orgs[0],'account':accounts[0],'owner':True}).one())==(member,expected)
                    c.execute(text('UPDATE identity.org_member SET deleted_at=now() WHERE id=:id'),{'id':member});expected+=1
                    assert tuple(c.execute(text(sql),{'org':orgs[0],'account':accounts[0],'owner':False}).one())==(member,expected+1)
                    # Synthetic owner-only maximum fixture; production writes never bypass guard.
                    c.execute(text('ALTER TABLE identity.org_member DISABLE TRIGGER org_member_revision_guard'))
                    c.execute(text('UPDATE identity.org_member SET revision=9223372036854775807 WHERE id=:id'),{'id':member})
                    c.execute(text('ALTER TABLE identity.org_member ENABLE TRIGGER org_member_revision_guard'))
                    before=row();sp=c.begin_nested()
                    try:c.execute(text('UPDATE identity.org_member SET is_owner=true WHERE id=:id'),{'id':member})
                    except Exception as error:
                        assert error.orig.sqlstate=='23514'
                        assert error.orig.diag.message_primary=='identity_membership_revision_exhausted'
                    else:raise AssertionError('overflow_change_allowed')
                    finally:sp.rollback()
                    assert row()==before
                    c.execute(text('UPDATE identity.org_member SET revision=1 WHERE id=:id'),{'id':member})
                    assert row()==before
                    ids={'first':member,'second':members[1]}
                    pair=text('SELECT to_jsonb(m) FROM identity.org_member m WHERE id IN (:first,:second) ORDER BY id')
                    before_pair=c.execute(pair,ids).scalars().all();sp=c.begin_nested()
                    try:c.execute(text('UPDATE identity.org_member SET is_owner=NOT is_owner WHERE id IN (:first,:second)'),ids)
                    except Exception as error:
                        assert error.orig.sqlstate=='23514'
                        assert error.orig.diag.message_primary=='identity_membership_revision_exhausted'
                    else:raise AssertionError('multirow_overflow_change_allowed')
                    finally:sp.rollback()
                    assert c.execute(pair,ids).scalars().all()==before_pair

                finally:t.rollback()
        finally:db.dispose()
        self.passed('membership-revision-and-legacy-upsert',all_persisted_fields=True,insert_one=True,noop_stable=True,forgery_denied=True,overflow_atomic=True,multirow_overflow_atomic=True,unretire_supported=True)

    def upgrades_and_failures(self):
        self.prior_evidence(PREVIOUS_COMMIT,PREVIOUS_FILES,'identity_0003')
        self.command('organization-clean','clean');self.reads();self.command('organization-repeat','clean')
        self.legacy('legacy');self.original_ledger('legacy');ids=self.row_fixtures('legacy')
        previous_ids=self.row_fixtures('previous')
        for case,case_ids in [('legacy',ids),('previous',previous_ids)]:
            old_members=self.old_rows(case);before=self.data_state(case);external=self.external_state(case)
            self.command('organization-'+case,case,mode='adopt' if case=='legacy' else 'clean')
            after=self.data_state(case)
            assert all(after[key]==value for key,value in before.items() if key not in ('identity.alembic_version','org_member'))
            assert self.old_rows(case)==old_members and self.external_state(case)==external
            assert self.sql(case,'SELECT DISTINCT revision FROM identity.org_member')==[(1,)]
            self.runtime(case,case_ids)
            account=str(uuid.uuid4());self.sql(case,'INSERT INTO auth.users(id,email) VALUES (:id,:email)',{'id':account,'email':'synthetic-'+account+'@example.invalid'},role='databases')
            assert self.sql(case,'SELECT id::text FROM identity.users WHERE id=:id',{'id':account})==[(account,)]
        admin=self.admin('unsafe')
        try:
            for label,unsafe,restore in [('bypass','ALTER ROLE identity_account_projection_owner BYPASSRLS','ALTER ROLE identity_account_projection_owner NOBYPASSRLS'),('runtime-member','GRANT identity_account_projection_owner TO access_runtime','REVOKE identity_account_projection_owner FROM access_runtime')]:
                with admin.begin() as c:c.execute(text(unsafe))
                before=self.data_state('unsafe')
                try:self.command('organization-unsafe-'+label,'unsafe',expected='identity_projection_role_unsafe');assert self.data_state('unsafe')==before
                finally:
                    with admin.begin() as c:c.execute(text(restore))
        finally:admin.dispose()
        admin=self.admin('failure')
        try:
            with admin.begin() as c:c.execute(text("""CREATE FUNCTION public.synthetic_organization_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN IF EXISTS (SELECT 1 FROM pg_event_trigger_ddl_commands() WHERE object_identity='identity.current_account_organization()') THEN RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_organization_failure'; END IF; END $$; CREATE EVENT TRIGGER synthetic_organization_failure ON ddl_command_end WHEN TAG IN ('CREATE FUNCTION') EXECUTE FUNCTION public.synthetic_organization_failure();"""))
            before,catalog=self.data_state('failure'),self.snapshot('failure')
            self.command('organization-mid-write-rollback','failure',expected='identity_migration_failed_requires_reconciliation')
            assert self.data_state('failure')==before and self.snapshot('failure')==catalog
        finally:
            with admin.begin() as c:c.execute(text('DROP EVENT TRIGGER synthetic_organization_failure; DROP FUNCTION public.synthetic_organization_failure()'))
            admin.dispose()
        self.command('organization-failure-reconciled','failure')
        self.sql('unknown',"UPDATE identity.alembic_version SET version_num='identity_unknown'")
        before=self.data_state('unknown');self.command('organization-unknown-history','unknown',expected='identity_unknown_history');assert self.data_state('unknown')==before
        # Current-head drift must refuse without fixing or broadening authority.
        self.sql('clean','GRANT SELECT (is_owner) ON identity.org_member TO identity_account_projection_owner')
        before=self.data_state('clean')
        try:self.command('organization-reader-drift','clean',expected='identity_catalog_mismatch:');assert self.data_state('clean')==before
        finally:self.sql('clean','REVOKE SELECT (is_owner) ON identity.org_member FROM identity_account_projection_owner')
        self.command('organization-drift-reconciled','clean')
        self.passed('organization-foundation-matrix',prior_head3_compatible=True,old_rows_preserved=True,rollback_verified=True,unsafe_role_refused=True)


def main():
    proof,private=fixture();OrganizationQualification(proof,private).upgrades_and_failures()


if __name__=='__main__':
    try:main()
    except Exception as error:
        print('organization_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None
