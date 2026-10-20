"""Synthetic restricted-login authority proof, within the existing qualification frame.

Root prepares roles/targets and exact prior-head evidence. This module never provisions
resources, credentials, authority in real data, command effects or reference pins.
"""
import sys
import uuid
from pathlib import Path
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parent))
from qualify_current_account_organization import OrganizationQualification, PREVIOUS_FILES as HEAD3_FILES
from qualify_identity_baseline import baseline, engine, fixture, text

PREVIOUS_COMMIT='85b26f38dd66b5f1ac96854f82402c93f4a58700'
PREVIOUS_FILES=HEAD3_FILES | {'versions/0004_current_account_organization.py','organization-reference.json'}
NIL='00000000-0000-0000-0000-000000000000'
REQUIRED_CASES=frozenset({'authority_reference','clean','legacy','previous','failure','unsafe','unknown','native'})
READ_SQL='SELECT executor_actor_id::text,principal_revision,authority_id::text,authority_revision FROM identity.current_operator_authority(:command,:scope,CAST(:org AS uuid),CAST(:target AS uuid))'


class AuthorityQualification(OrganizationQualification):
    def snapshot(self,case):
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:return baseline.authority_catalog_snapshot(c)
        finally:db.dispose()

    def validate_operator_urls(self):
        assert set(self.private.get('operator_urls',{}))==REQUIRED_CASES, 'authority_operator_url_group_invalid'
        for group in ['owner_urls','databases','runtime_urls']:
            assert set(self.private[group])==REQUIRED_CASES, 'authority_core_url_group_invalid'
        for case in REQUIRED_CASES:
            actual=urlsplit(self.private['operator_urls'][case]);owner=urlsplit(self.private['owner_urls'][case])
            assert actual.username=='identity_operator' and actual.scheme=='postgresql', 'authority_operator_login_invalid'
            assert (actual.hostname,actual.port,actual.path,actual.query,actual.fragment)==(owner.hostname,owner.port,owner.path,'',''), 'authority_operator_target_invalid'

    def operator_engine(self,case):
        self.validate_operator_urls()
        return engine(self.private['operator_urls'][case])

    def authority_fixture(self):
        actor=str(uuid.uuid4())
        self.sql('clean',"INSERT INTO identity.actor(id,kind,display_name,created_by,updated_by) VALUES (:id,'service','Synthetic authority executor',:id,:id)",{'id':actor})
        self.sql('clean',"INSERT INTO identity.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by) VALUES ('identity_operator',:actor,true,:actor,:actor)",{'actor':actor})
        return actor

    def authority(self,actor,command,scope='platform',org=None,target=None,identifier=None,database_login='identity_operator'):
        identifier=identifier or str(uuid.uuid4())
        self.sql('clean',"INSERT INTO identity.operator_authorities(id,database_login,command,scope_kind,org_id,target_account_id,enabled,created_by,updated_by) VALUES (:id,:login,:command,:scope,:org,:target,true,:actor,:actor)",{'id':identifier,'login':database_login,'command':command,'scope':scope,'org':org,'target':target,'actor':actor})
        return identifier

    def restricted_reads(self):
        db=self.operator_engine('clean')
        def arguments(command='actor.register_system',scope='platform',org=None,target=None):return dict(command=command,scope=scope,org=org,target=target)
        try:
            with db.connect() as c:
                assert c.execute(text('SELECT session_user,current_user')).one()==('identity_operator','identity_operator');c.commit()
                def query(**args):
                    with c.begin():return [tuple(row) for row in c.execute(text(READ_SQL),arguments(**args))]
                assert query()==[]  # unmapped login
                actor=self.authority_fixture()
                assert query()==[]  # enabled principal alone grants nothing
                registration=self.authority(actor,'actor.register_system')
                assert query()==[(actor,1,registration,1)]
                foreign_actor=str(uuid.uuid4());foreign_login='synthetic_other_operator'
                self.sql('clean',"INSERT INTO identity.actor(id,kind,display_name,created_by,updated_by) VALUES (:id,'service','Synthetic other executor',:id,:id)",{'id':foreign_actor})
                self.sql('clean',"INSERT INTO identity.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by) VALUES (:login,:actor,true,:actor,:actor)",{'login':foreign_login,'actor':foreign_actor})
                self.authority(foreign_actor,'actor.register_system',identifier='00000000-0000-0000-0000-000000000001',database_login=foreign_login)
                assert query()==[(actor,1,registration,1)]  # cannot borrow lower UUID or executor
                account,other,org,other_org=[str(uuid.uuid4()) for _ in range(4)]
                self.authority(foreign_actor,'membership.retire','organization',other_org,account,database_login=foreign_login)
                assert query(command='membership.retire',scope='organization',org=other_org,target=account)==[]
                ensure=self.authority(actor,'account_actor.ensure',target=account)
                assert query(command='account_actor.ensure',target=account)==[(actor,1,ensure,1)]
                assert query(command='account_actor.ensure',target=other)==[]
                wildcard=self.authority(actor,'account_actor.ensure',identifier='ffffffff-ffff-ffff-ffff-ffffffffffff')
                assert query(command='account_actor.ensure',target=account)==[(actor,1,min(ensure,wildcard),1)]
                assert query(command='account_actor.ensure',target=other)==[(actor,1,wildcard,1)]
                join=self.authority(actor,'membership.join','organization',org,account)
                assert query(command='membership.join',scope='organization',org=org,target=account)==[(actor,1,join,1)]
                assert query(command='membership.join_owner',scope='organization',org=org,target=account)==[]
                owner=self.authority(actor,'membership.join_owner','organization',org,account)
                assert query(command='membership.join_owner',scope='organization',org=org,target=account)==[(actor,1,owner,1)]
                retire=self.authority(actor,'membership.retire','organization',org)
                assert query(command='membership.retire',scope='organization',org=org,target=other)==[(actor,1,retire,1)]
                invalid=[arguments(command=v) for v in [None,'','actor.*','membership','application.register']]
                invalid += [arguments(scope=v) for v in [None,'','account','organization']]
                invalid += [arguments(org=v) for v in [NIL,org]]+[arguments(target=v) for v in [NIL,account]]
                invalid += [arguments(command='account_actor.ensure',target=v) for v in [None,NIL]]
                invalid += [arguments(command='membership.join',scope='organization',org=o,target=t) for o,t in [(None,account),(NIL,account),(org,None),(org,NIL),(other_org,account),(org,other)]]
                for args in invalid:
                    with c.begin():assert c.execute(text(READ_SQL),args).all()==[]
                # Same physical authenticated connection, fresh statements after committed changes.
                for table,key,value,read_args in [
                    ('operator_principals','database_login','identity_operator',{}),
                    ('operator_authorities','id',registration,{})]:
                    self.sql('clean','UPDATE identity.'+table+' SET enabled=false WHERE '+key+'=:key',{'key':value})
                    assert query(**read_args)==[]
                    self.sql('clean','UPDATE identity.'+table+' SET enabled=true WHERE '+key+'=:key',{'key':value})
                assert query()==[(actor,3,registration,3)]
                before=self.data_state('clean')
                with c.begin():
                    c.execute(text("SELECT set_config('app.actor_id',:actor,true),set_config('request.jwt.claims',:claims,true)"),{'actor':str(uuid.uuid4()),'claims':'{"role":"service_role","sub":"spoofed"}'})
                    c.execute(text('CREATE TEMP TABLE operator_principals(database_login name,executor_actor_id uuid); CREATE TEMP TABLE operator_authorities(id uuid); SET LOCAL search_path=pg_temp,public,identity'))
                    assert [tuple(row) for row in c.execute(text(READ_SQL),arguments())]==[(actor,3,registration,3)]
                forbidden=['SELECT * FROM identity.operator_principals','SELECT * FROM identity.operator_authorities','SELECT * FROM identity.actor',
                    'UPDATE identity.operator_principals SET enabled=false','UPDATE identity.operator_authorities SET enabled=false',
                    'INSERT INTO identity.actor DEFAULT VALUES','DELETE FROM identity.actor','TRUNCATE identity.operator_authorities',
                    'ALTER TABLE identity.operator_principals ADD COLUMN forbidden text','SET ROLE identity_operator_authority_owner','SET ROLE identity_migrator',
                    "CREATE FUNCTION identity.forbidden() RETURNS int LANGUAGE sql AS 'SELECT 1'",
                    "CREATE OR REPLACE FUNCTION identity.current_operator_authority(text,text,uuid,uuid) RETURNS TABLE(executor_actor_id uuid,principal_revision bigint,authority_id uuid,authority_revision bigint) LANGUAGE sql AS 'SELECT NULL::uuid,1::bigint,NULL::uuid,1::bigint'"]
                for statement in forbidden:
                    with c.begin():
                        sp=c.begin_nested()
                        try:c.execute(text(statement))
                        except Exception as error:assert error.orig.sqlstate=='42501'
                        else:raise AssertionError('operator_excess_authority')
                        finally:sp.rollback()
                assert self.data_state('clean')==before
                # SET ROLE cannot turn the migrator's original session into this principal.
                owner_db=engine(self.private['owner_urls']['clean'])
                try:
                    with owner_db.begin() as owner_c:
                        owner_c.execute(text('SET LOCAL ROLE identity_operator_authority_owner'))
                        assert owner_c.execute(text(READ_SQL),arguments()).all()==[]
                finally:owner_db.dispose()
                for role in ['access_runtime','anon','authenticated','service_role','supabase_auth_admin']:
                    # Legacy named authenticated/service_role defaults must not leak
                    # table or column privileges to either newly protected map.
                    assert self.sql('clean',"""SELECT NOT EXISTS (SELECT 1 FROM pg_class relation
                        JOIN pg_namespace namespace ON namespace.oid=relation.relnamespace
                        WHERE namespace.nspname='identity' AND relation.relname IN ('operator_principals','operator_authorities')
                          AND (has_table_privilege(:role,relation.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
                               OR has_any_column_privilege(:role,relation.oid,'SELECT,INSERT,UPDATE,REFERENCES')))""",{'role':role})==[(True,)]
                    assert self.sql('clean',"SELECT has_function_privilege(:role,'identity.current_operator_authority(text,text,uuid,uuid)','EXECUTE')",{'role':role})==[(False,)]
                runtime=engine(self.private['runtime_urls']['clean'])
                try:
                    with runtime.connect() as runtime_c:
                        for statement in ['SELECT * FROM identity.current_operator_authority(NULL,NULL,NULL,NULL)','SELECT * FROM identity.operator_principals','SELECT * FROM identity.operator_authorities']:
                            with runtime_c.begin():
                                try:runtime_c.execute(text(statement))
                                except Exception as error:assert error.orig.sqlstate=='42501'
                                else:raise AssertionError('runtime_authority_disclosure')
                finally:runtime.dispose()
                self.structure(actor,registration)
        finally:db.dispose()
        self.passed('operator-actual-login-matrix',session_identity_only=True,exact_and_wildcard=True,owner_join_independent=True,committed_revocation_same_connection=True,metadata_only=True,alternate_writes_denied=True)

    def structure(self,actor,authority):
        db=engine(self.private['owner_urls']['clean'])
        try:
            with db.connect() as c:
                t=c.begin()
                try:
                    def reject(sql,params,code):
                        sp=c.begin_nested()
                        try:c.execute(text(sql),params)
                        except Exception as error:assert error.orig.sqlstate==code
                        else:raise AssertionError('invalid_authority_structure_accepted')
                        finally:sp.rollback()
                    updater=str(uuid.uuid4())
                    c.execute(text("INSERT INTO identity.actor(id,kind,display_name,created_by,updated_by) VALUES (:id,'service','Synthetic alternate updater',:id,:id)"),{'id':updater})
                    principal=c.execute(text("""INSERT INTO identity.operator_principals(database_login,executor_actor_id,enabled,revision,created_by,updated_by,created_at,updated_at)
                        VALUES ('synthetic_insert_metadata',:actor,false,444,:actor,:updater,'2000-01-01T00:00:00Z','2000-01-01T00:00:00Z')
                        RETURNING revision,created_by::text,updated_by::text,created_at=statement_timestamp(),updated_at=statement_timestamp()"""),{'actor':actor,'updater':updater}).one()
                    assert tuple(principal)==(1,actor,actor,True,True)
                    metadata_id=str(uuid.uuid4())
                    inserted=c.execute(text("""INSERT INTO identity.operator_authorities(id,database_login,command,scope_kind,enabled,revision,created_by,updated_by,created_at,updated_at)
                        VALUES (:id,'synthetic_insert_metadata','actor.register_system','platform',false,444,:actor,:updater,'2000-01-01T00:00:00Z','2000-01-01T00:00:00Z')
                        RETURNING revision,created_by::text,updated_by::text,created_at=statement_timestamp(),updated_at=statement_timestamp()"""),{'id':metadata_id,'actor':actor,'updater':updater}).one()
                    assert tuple(inserted)==(1,actor,actor,True,True)
                    for table,where,params in [('operator_principals',"database_login='synthetic_insert_metadata'",{}),('operator_authorities','id=:id',{'id':metadata_id})]:
                        updated=c.execute(text('UPDATE identity.'+table+" SET enabled=true,updated_by=:updater,updated_at='2000-01-01T00:00:00Z' WHERE "+where+' RETURNING revision,updated_by::text,updated_at=statement_timestamp()'),{**params,'updater':updater}).one()
                        assert tuple(updated)==(2,updater,True)
                    insert="INSERT INTO identity.operator_authorities(id,database_login,command,scope_kind,org_id,application_id,target_account_id,created_by,updated_by) VALUES (:id,'identity_operator',:command,:scope,:org,:app,:target,:actor,:actor)"
                    base=dict(id=str(uuid.uuid4()),command='actor.register_system',scope='platform',org=None,app=None,target=None,actor=actor)
                    reject(insert,base,'23505') # NULLS NOT DISTINCT full tuple
                    for changes in [dict(id=NIL),dict(command='unknown'),dict(scope='account'),dict(org=NIL),dict(app='anything'),dict(target=NIL),dict(target=str(uuid.uuid4())),dict(command='membership.join',scope='organization'),dict(command='account_actor.ensure',scope='organization',org=str(uuid.uuid4()))]:
                        reject(insert,{**base,**changes},'23514')
                    reject(insert,{**base,'command':'account_actor.ensure','target':str(uuid.uuid4()),'actor':str(uuid.uuid4())},'23503')
                    reject("INSERT INTO identity.operator_principals(database_login,executor_actor_id,created_by,updated_by) VALUES ('unmapped',:missing,:actor,:actor)",{'actor':actor,'missing':str(uuid.uuid4())},'23503')
                    reject("INSERT INTO identity.operator_authorities(id,database_login,command,scope_kind,created_by,updated_by) VALUES (:id,'unmapped','actor.register_system','platform',:actor,:actor)",{'id':str(uuid.uuid4()),'actor':actor},'23503')
                    reject('UPDATE identity.operator_authorities SET command=\'account_actor.ensure\' WHERE id=:id',{'id':authority},'23514')
                    reject('UPDATE identity.operator_principals SET executor_actor_id=:id',{'id':str(uuid.uuid4())},'23514')
                    for table in ['operator_principals','operator_authorities']:
                        row=lambda:c.execute(text('SELECT to_jsonb(t) FROM identity.'+table+' t ORDER BY to_jsonb(t)::text')).scalars().all()
                        prior=row()
                        c.execute(text('UPDATE identity.'+table+" SET revision=0,updated_at='2000-01-01T00:00:00Z',updated_by=:actor"),{'actor':actor})
                        assert row()==prior
                        c.execute(text('UPDATE identity.'+table+' SET enabled=NOT enabled,revision=-1,updated_by=:actor'),{'actor':actor})
                        assert sorted(r['revision'] for r in row())==sorted(r['revision']+1 for r in prior)
                        reject('DELETE FROM identity.'+table,{},'23514')
                        # PostgreSQL checks inbound FK completeness before firing a
                        # principal-only TRUNCATE trigger. Both failures preserve rows.
                        before_retention=row()
                        reject('TRUNCATE identity.'+table,{},'0A000' if table=='operator_principals' else '23514')
                        assert row()==before_retention
                    retained={table:c.execute(text('SELECT to_jsonb(t) FROM identity.'+table+' t ORDER BY to_jsonb(t)::text')).scalars().all()
                              for table in ['operator_principals','operator_authorities']}
                    reject('TRUNCATE identity.operator_principals, identity.operator_authorities',{},'23514')
                    for table,rows in retained.items():
                        assert c.execute(text('SELECT to_jsonb(t) FROM identity.'+table+' t ORDER BY to_jsonb(t)::text')).scalars().all()==rows
                    # Controlled synthetic overflow fixture; never weaken production guards.
                    c.execute(text('ALTER TABLE identity.operator_authorities DISABLE TRIGGER operator_authorities_guard'))
                    c.execute(text('UPDATE identity.operator_authorities SET revision=9223372036854775807 WHERE id=:id'),{'id':authority})
                    c.execute(text('ALTER TABLE identity.operator_authorities ENABLE TRIGGER operator_authorities_guard'))
                    before=c.execute(text('SELECT to_jsonb(t) FROM identity.operator_authorities t ORDER BY id')).scalars().all()
                    reject('UPDATE identity.operator_authorities SET enabled=NOT enabled',{},'23514')
                    assert c.execute(text('SELECT to_jsonb(t) FROM identity.operator_authorities t ORDER BY id')).scalars().all()==before
                finally:t.rollback()
        finally:db.dispose()
        self.passed('operator-structural-guards',null_tuple_unique=True,foreign_actor_and_principal=True,immutable_tuple=True,server_revision_time=True,noop_stable=True,overflow_atomic=True)

    def upgrades_and_failures(self):
        self.validate_operator_urls()  # validate every target before any mutation
        self.prior_evidence(PREVIOUS_COMMIT,PREVIOUS_FILES,'identity_0004')
        self.command('authority-clean','clean')
        assert self.sql('clean','SELECT count(*) FROM identity.actor')==[(0,)]
        assert self.sql('clean','SELECT count(*) FROM identity.operator_principals')==[(0,)]
        self.restricted_reads();self.command('authority-repeat','clean')
        self.legacy('legacy');self.original_ledger('legacy');self.row_fixtures('legacy');self.row_fixtures('previous')
        for case in ['legacy','previous']:
            before,external=self.data_state(case),self.external_state(case)
            self.command('authority-'+case,case,mode='adopt' if case=='legacy' else 'clean')
            after=self.data_state(case)
            # Legacy gains only the preselected member revision; compare that separately.
            if case=='legacy':
                normalized=self.data_state(case,membership_without_revision=True)
                assert normalized['org_member']==before['org_member']
            assert all(after[key]==value for key,value in before.items() if key not in ('identity.alembic_version','org_member'))
            if case=='previous':assert after['org_member']==before['org_member']
            assert self.external_state(case)==external
            self.command('authority-'+case+'-repeat',case)
        admin=self.admin('unsafe')
        try:
            for label,unsafe,restore in [('bypass','ALTER ROLE identity_operator BYPASSRLS','ALTER ROLE identity_operator NOBYPASSRLS'),
                ('owner-login','ALTER ROLE identity_operator_authority_owner LOGIN','ALTER ROLE identity_operator_authority_owner NOLOGIN'),
                ('operator-member','GRANT identity_operator_authority_owner TO identity_operator','REVOKE identity_operator_authority_owner FROM identity_operator'),
                ('external-definer',"CREATE FUNCTION public.synthetic_external_definer() RETURNS int LANGUAGE sql SECURITY DEFINER AS 'SELECT 1'; GRANT EXECUTE ON FUNCTION public.synthetic_external_definer() TO PUBLIC",'DROP FUNCTION public.synthetic_external_definer()'),
                ('public-sequence-usage','CREATE SEQUENCE public.synthetic_authority_sequence; GRANT USAGE ON SEQUENCE public.synthetic_authority_sequence TO PUBLIC','DROP SEQUENCE public.synthetic_authority_sequence'),
                ('public-sequence-update','CREATE SEQUENCE public.synthetic_authority_sequence; GRANT UPDATE ON SEQUENCE public.synthetic_authority_sequence TO PUBLIC','DROP SEQUENCE public.synthetic_authority_sequence'),
                ('public-table-read','CREATE TABLE public.synthetic_authority_table(id int); GRANT SELECT ON public.synthetic_authority_table TO PUBLIC','DROP TABLE public.synthetic_authority_table'),
                ('public-table-write','CREATE TABLE public.synthetic_authority_table(id int); GRANT INSERT ON public.synthetic_authority_table TO PUBLIC','DROP TABLE public.synthetic_authority_table'),
                ('staged-dependency','CREATE SCHEMA synthetic_authority_dependency; GRANT USAGE ON SCHEMA synthetic_authority_dependency TO identity_operator_authority_owner','DROP SCHEMA synthetic_authority_dependency')]:
                with admin.begin() as c:c.execute(text(unsafe))
                before=self.data_state('unsafe')
                try:self.command('authority-unsafe-'+label,'unsafe',expected='identity_authority_role_not_empty' if label=='staged-dependency' else 'identity_authority_role_unsafe');assert self.data_state('unsafe')==before
                finally:
                    with admin.begin() as c:c.execute(text(restore))
        finally:admin.dispose()
        admin=self.admin('failure')
        try:
            with admin.begin() as c:c.execute(text("""CREATE FUNCTION public.synthetic_authority_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN IF EXISTS (SELECT 1 FROM pg_event_trigger_ddl_commands() WHERE schema_name='identity' AND object_type='function' AND objid=to_regprocedure('identity.current_operator_authority(text,text,uuid,uuid)')) THEN RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_authority_failure'; END IF; END $$; CREATE EVENT TRIGGER synthetic_authority_failure ON ddl_command_end WHEN TAG IN ('CREATE FUNCTION') EXECUTE FUNCTION public.synthetic_authority_failure();"""))
            before,catalog=self.data_state('failure'),self.snapshot('failure')
            self.command('authority-mid-write-rollback','failure',expected='identity_migration_failed_requires_reconciliation')
            assert self.data_state('failure')==before and self.snapshot('failure')==catalog
        finally:
            with admin.begin() as c:c.execute(text('DROP EVENT TRIGGER synthetic_authority_failure; DROP FUNCTION public.synthetic_authority_failure()'))
            admin.dispose()
        self.command('authority-failure-reconciled','failure')
        self.sql('unknown',"UPDATE identity.alembic_version SET version_num='identity_unknown'")
        before=self.data_state('unknown');self.command('authority-unknown-history','unknown',expected='identity_unknown_history');assert self.data_state('unknown')==before
        self.sql('clean','GRANT SELECT(created_at) ON identity.operator_authorities TO identity_operator_authority_owner')
        before=self.data_state('clean')
        try:self.command('authority-reader-drift','clean',expected='identity_catalog_mismatch:');assert self.data_state('clean')==before
        finally:self.sql('clean','REVOKE SELECT(created_at) ON identity.operator_authorities FROM identity_operator_authority_owner')
        self.command('authority-drift-reconciled','clean')
        self.passed('authority-foundation-matrix',prior_head4_compatible=True,legacy_rows_preserved=True,injected_failure_rollback=True,no_command_effects=True)


def report_failure(error):
    # Frame metadata only: never stringify the exception or print SQL, source,
    # locals, parameters or business values from the qualification process.
    frame=error.__traceback__
    while frame is not None and frame.tb_next is not None:frame=frame.tb_next
    location='' if frame is None else ':'+Path(frame.tb_frame.f_code.co_filename).name+':'+str(frame.tb_lineno)+':'+frame.tb_frame.f_code.co_name
    print('authority_qualification_failed:'+type(error).__name__+location,file=sys.stderr)


def main():
    proof,private=fixture();AuthorityQualification(proof,private).upgrades_and_failures()


if __name__=='__main__':
    try:main()
    except Exception as error:
        report_failure(error)
        raise SystemExit(1) from None
