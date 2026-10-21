"""Actual staged actor-reference proof through existing Identity fixture tooling."""
from contextlib import contextmanager
from pathlib import Path
from hashlib import sha256
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import sys
import signal
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qualify_active_membership_index as previous
from qualify_identity_baseline import baseline, engine, fixture, text, OWNER

PREVIOUS_COMMIT='f885abf5b782af09d845af4eefcd9c170faa7bab'
PREVIOUS_FILES=previous.PREVIOUS_FILES | {'versions/0014_active_membership_index.py','active-membership-index-reference.json'}
REQUIRED_CASES=(previous.REQUIRED_CASES-{'active_membership_index_reference'})|{'membership_actor_attribution_reference'}
FIELDS=('created_actor_id','updated_actor_id')
# Exact previously qualified PostgreSQL definition; behavioral checks establish its semantics.
GUARD_FUNCTION_SHA256='bf0137360f9ed9eff527ec27a0918d10ca252092f2dec1c340a64e0e26aee5ab'


class MembershipActorAttributionQualification(previous.ActiveMembershipIndexQualification):
    required_cases=REQUIRED_CASES

    def characterize(self):
        case='characterization';self.fixture_rows(case)
        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0014',)]
        catalog=self.snapshot(case)
        baseline.compare_catalog(baseline.catalog_fingerprints(catalog),baseline.trusted_active_membership_index_reference())
        before=self.data_state(case)
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:
                try:c.execute(text('SELECT created_actor_id,updated_actor_id FROM identity.org_member'))
                except Exception as error:assert error.orig.sqlstate=='42703'
                else:raise AssertionError('expected_missing_membership_actor_columns')
                finally:c.rollback()
        finally:db.dispose()
        assert self.data_state(case)==before
        self.witness('membership-actor-attribution-head14-characterization',{
            'binding':self.characterization_binding(),'catalog':catalog,'head':'identity_0014',
            'missing_columns':list(FIELDS),'unchanged_data':True})
        self.passed('membership-actor-attribution-head14-characterization',expected_sqlstate='42703')

    def compatibility(self):
        paths=sorted(self.proof.glob('membership-actor-attribution-head14-characterization-*.json'),key=lambda p:p.stat().st_mtime_ns)
        assert paths
        witness=json.loads(paths[-1].read_text())
        assert witness['binding']==self.characterization_binding() and witness['head']=='identity_0014'
        assert witness['unchanged_data'] and witness['missing_columns']==list(FIELDS)
        old=witness['catalog'];current=self.snapshot('clean')
        baseline.compare_catalog(baseline.catalog_fingerprints(old),baseline.trusted_active_membership_index_reference())
        baseline.compare_catalog(baseline.catalog_fingerprints(current),baseline.trusted_membership_actor_attribution_reference())
        self.verify_catalog_delta(old,current)
        assert self.sql('clean',"SELECT pg_get_userbyid(proowner),prosecdef,provolatile,proconfig::text FROM pg_proc WHERE oid='identity.guard_org_member_actor_attribution()'::regprocedure")==[('identity_migrator',False,'v','{\"search_path=pg_catalog, pg_temp\"}')]
        for name in FIELDS:
            assert self.sql('clean',"SELECT is_nullable,column_default FROM information_schema.columns WHERE table_schema='identity' AND table_name='org_member' AND column_name=:name",{'name':name})==[('YES',None)]
        constraints=self.sql('clean',"SELECT conname,pg_get_constraintdef(oid,true),convalidated FROM pg_constraint WHERE conrelid='identity.org_member'::regclass AND conname IN ('org_member_created_actor_fk','org_member_updated_actor_fk') ORDER BY conname")
        assert constraints==[(f'org_member_{prefix}_actor_fk',f'FOREIGN KEY ({prefix}_actor_id) REFERENCES identity.actor(id) ON DELETE RESTRICT',True) for prefix in ['created','updated']]
        self.passed('membership-actor-attribution-exact-additive-delta',legacy_catalog_preserved=True)

    @staticmethod
    def verify_catalog_delta(old,current):
        structural={'columns','constraints','functions','triggers'}
        prefixes=('', 'authority_', 'command_', 'projection_', 'target_')
        effective={prefix+'effective_'+kind for prefix in prefixes for kind in ('columns','functions')}
        changed={key for key in old if old[key]!=current[key]}
        assert old.keys()==current.keys() and changed==structural|effective
        for category in changed:
            assert all(row in current[category] for row in old[category]), category
        # New catalogue observation rows do not imply new grants. Column rights
        # inherit the unchanged table rights, not unrelated explicit column ACLs.
        for prefix in prefixes:
            category=prefix+'effective_columns'
            expected=[[role,table,field,permission,allowed]
                for role,table,permission,allowed in old[prefix+'effective_tables']
                if table=='org_member' and permission in ('INSERT','REFERENCES','SELECT','UPDATE')
                for field in FIELDS]
            assert sorted(current[category])==sorted(old[category]+expected)
            category=prefix+'effective_functions'
            roles={row[0] for row in old[category]}
            expected=[[role,'identity','guard_org_member_actor_attribution','',role=='identity_migrator'] for role in roles]
            assert sorted(current[category])==sorted(old[category]+expected)
        expected_columns=[['org_member',name,11+i,'uuid',False,'','','','',''] for i,name in enumerate(FIELDS)]
        expected_constraints=[['org_member',f'org_member_{prefix}_actor_fk',
            f'FOREIGN KEY ({prefix}_actor_id) REFERENCES identity.actor(id) ON DELETE RESTRICT',True,False,False]
            for prefix in ('created','updated')]
        expected_trigger=['identity','org_member','org_member_actor_attribution_guard',
            'CREATE TRIGGER org_member_actor_attribution_guard BEFORE INSERT OR UPDATE ON identity.org_member FOR EACH ROW EXECUTE FUNCTION identity.guard_org_member_actor_attribution()','O']
        for category,expected in [('columns',expected_columns),('constraints',expected_constraints),('triggers',[expected_trigger])]:
            assert sorted(current[category])==sorted(old[category]+expected)
        functions=[row for row in current['functions'] if row not in old['functions']]
        assert len(functions)==1
        function=functions[0]
        assert function[:4]==['identity','guard_org_member_actor_attribution','','identity_migrator']
        assert function[5]=='{identity_migrator=X/identity_migrator}'
        assert sha256(function[4].encode()).hexdigest()==GUARD_FUNCTION_SHA256

    def attribution_writes(self):
        case='clean';v=dict(self.inputs[case]);self.fixture_rows(case)
        v.update(actor='c1234567-1234-1234-1234-123456789abc',other_actor='d1234567-1234-1234-1234-123456789abc')
        before=self.data_state(case);catalog=self.snapshot(case)
        with self.fixture_execution(case):
            db=engine(self.private['runtime_urls'][case])
            try:
                with db.connect() as c:
                    for field in FIELDS:
                        with self.execution(c,v):
                            for statement in [
                                f'UPDATE identity.org_member SET {field}=CAST(:actor AS uuid) WHERE id=CAST(:member AS bigint)',
                                f'INSERT INTO identity.org_member(org_id,user_id,{field}) VALUES(CAST(:spare_org AS uuid),CAST(:spare AS uuid),CAST(:actor AS uuid))',
                                f'INSERT INTO identity.org_member(org_id,user_id,{field}) VALUES(CAST(:org AS uuid),CAST(:account AS uuid),CAST(:actor AS uuid)) ON CONFLICT(org_id,user_id) DO UPDATE SET {field}=EXCLUDED.{field}',
                                f'INSERT INTO identity.org_member(org_id,user_id) VALUES(CAST(:org AS uuid),CAST(:account AS uuid)) ON CONFLICT(org_id,user_id) DO UPDATE SET {field}=CAST(:actor AS uuid)',
                                f'WITH permitted AS (UPDATE identity.org_member SET is_owner=NOT is_owner WHERE id=CAST(:other_member AS bigint) RETURNING id) UPDATE identity.org_member SET {field}=CAST(:actor AS uuid) WHERE id=CAST(:member AS bigint) AND EXISTS(SELECT 1 FROM permitted)',
                                f'UPDATE identity.org_member SET is_owner=NOT is_owner,{field}=CASE WHEN id=CAST(:member AS bigint) THEN CAST(:actor AS uuid) ELSE NULL END WHERE org_id=CAST(:org AS uuid)',
                            ]:
                                self.reject(c,statement,v,'23514','identity_membership_actor_owner_required','org_member_actor_owner_required')
                    self.seed_compatibility(c,v)
            finally:db.dispose()
        # Explicit synthetic adoption only, under the actual owner. All rows restored.
        db=self.admin(case)
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    c.execute(text('SET LOCAL ROLE identity_migrator'))
                    assert c.execute(text('SELECT current_user')).scalar_one()=='identity_migrator'
                    for key in ['actor','other_actor']:
                        c.execute(text("INSERT INTO identity.actor(id,kind,actor_key,display_name,created_by,updated_by) VALUES(CAST(:id AS uuid),'service',:key,'Synthetic verified actor',CAST(:id AS uuid),CAST(:id AS uuid))"),{'id':v[key],'key':'synthetic:'+key})
                    original=c.execute(text('SELECT to_jsonb(m) FROM identity.org_member m WHERE id=CAST(:member AS bigint)'),v).scalar_one()
                    for field in FIELDS:
                        for invalid in ['00000000-0000-0000-0000-000000000000','e1234567-1234-1234-1234-123456789abc']:
                            self.reject(c,f'UPDATE identity.org_member SET {field}=CAST(:invalid AS uuid) WHERE id=CAST(:member AS bigint)',dict(v,invalid=invalid),'23503',None,'org_member_'+field.replace('_id','')+'_fk')
                    inserted_sql="""INSERT INTO identity.org_member(org_id,user_id,is_owner,created_by,created_at,updated_by,updated_at,
                        revision,created_actor_id,updated_actor_id) VALUES(CAST(:spare_org AS uuid),CAST(:spare AS uuid),false,
                        CAST(:account AS uuid),'2000-01-01'::timestamptz,CAST(:other AS uuid),'2001-01-01'::timestamptz,
                        999,CAST(:actor AS uuid),CAST(:other_actor AS uuid))"""
                    inserted_tx=c.begin_nested()
                    try:
                        inserted=c.execute(text(inserted_sql+' RETURNING to_jsonb(org_member)'),v).scalar_one()
                        assert inserted['id']>0 and inserted['revision']==1
                        assert inserted['created_actor_id']==v['actor'] and inserted['updated_actor_id']==v['other_actor']
                        assert inserted['created_by']==v['account'] and inserted['updated_by']==v['other']
                        assert inserted['created_at']=='2000-01-01T00:00:00+00:00' and inserted['updated_at']=='2001-01-01T00:00:00+00:00'
                        assert inserted['org_id']==v['spare_org'] and inserted['user_id']==v['spare'] and inserted['is_owner'] is False
                    finally:inserted_tx.rollback()
                    for field,key in [('created_actor_id','actor'),('updated_actor_id','other_actor')]:
                        for invalid in ['00000000-0000-0000-0000-000000000000','e1234567-1234-1234-1234-123456789abc']:
                            self.reject(c,inserted_sql,dict(v,**{key:invalid}),'23503',None,'org_member_'+field.replace('_id','')+'_fk')
                    changed=c.execute(text('UPDATE identity.org_member SET created_actor_id=CAST(:actor AS uuid),updated_actor_id=CAST(:actor AS uuid) WHERE id=CAST(:member AS bigint) RETURNING to_jsonb(org_member)'),v).scalar_one()
                    assert changed==dict(original,created_actor_id=v['actor'],updated_actor_id=v['actor'],revision=original['revision']+1)
                    for replacement in ['NULL','CAST(:other_actor AS uuid)']:
                        self.reject(c,'UPDATE identity.org_member SET created_actor_id='+replacement+' WHERE id=CAST(:member AS bigint)',v,'23514','identity_membership_creation_actor_immutable','org_member_creation_actor_immutable')
                    noop=c.execute(text('UPDATE identity.org_member SET created_actor_id=created_actor_id,updated_actor_id=updated_actor_id,revision=999 WHERE id=CAST(:member AS bigint) RETURNING to_jsonb(org_member)'),v).scalar_one()
                    assert noop==changed
                    updated=c.execute(text('UPDATE identity.org_member SET updated_actor_id=CAST(:other_actor AS uuid) WHERE id=CAST(:member AS bigint) RETURNING to_jsonb(org_member)'),v).scalar_one()
                    assert updated==dict(changed,updated_actor_id=v['other_actor'],revision=changed['revision']+1)
                    c.execute(text('SET LOCAL ROLE service_role'))
                    for field in FIELDS:
                        for replacement in ['NULL','CAST(:other_actor AS uuid)']:
                            # For update attribution, use the other existing actor rather than a no-op.
                            if field=='updated_actor_id' and replacement!='NULL':replacement='CAST(:actor AS uuid)'
                            message='identity_membership_creation_actor_immutable' if field=='created_actor_id' else 'identity_membership_actor_owner_required'
                            constraint='org_member_creation_actor_immutable' if field=='created_actor_id' else 'org_member_actor_owner_required'
                            self.reject(c,f'UPDATE identity.org_member SET {field}={replacement} WHERE id=CAST(:member AS bigint)',v,'23514',message,constraint)
                    preserved=c.execute(text('UPDATE identity.org_member SET is_owner=NOT is_owner,created_actor_id=created_actor_id,updated_actor_id=updated_actor_id WHERE id=CAST(:member AS bigint) RETURNING to_jsonb(org_member)'),v).scalar_one()
                    assert preserved==dict(updated,is_owner=not updated['is_owner'],revision=updated['revision']+1)
                    c.execute(text(self.seed_statement()),v)
                    seeded=c.execute(text('SELECT to_jsonb(m) FROM identity.org_member m WHERE id=CAST(:member AS bigint)'),v).scalar_one()
                    assert seeded['created_actor_id']==v['actor'] and seeded['updated_actor_id']==v['other_actor']
                    c.execute(text("UPDATE identity.org_member SET deleted_at='2002-01-01'::timestamptz WHERE id=CAST(:member AS bigint)"),v)
                    retired=c.execute(text('SELECT to_jsonb(m) FROM identity.org_member m WHERE id=CAST(:member AS bigint)'),v).scalar_one()
                    assert retired==dict(seeded,deleted_at='2002-01-01T00:00:00+00:00',revision=seeded['revision']+1)
                    for replacement in ['NULL',"deleted_at+interval '1 second'"]:
                        self.reject(c,'UPDATE identity.org_member SET deleted_at='+replacement+' WHERE id=CAST(:member AS bigint)',v,
                            '23514','identity_membership_retirement_immutable','org_member_retirement_immutable')
                    c.execute(text('RESET ROLE'))
                    c.execute(text('SET LOCAL ROLE identity_migrator'))
                    # Rollback-only owner preparation exercises exhaustion without changing production guard code.
                    c.execute(text('ALTER TABLE identity.org_member DISABLE TRIGGER org_member_revision_guard'))
                    c.execute(text('UPDATE identity.org_member SET revision=9223372036854775807 WHERE id=CAST(:member AS bigint)'),v)
                    c.execute(text('ALTER TABLE identity.org_member ENABLE TRIGGER org_member_revision_guard'))
                    self.reject(c,'UPDATE identity.org_member SET updated_actor_id=CAST(:actor AS uuid) WHERE id=CAST(:member AS bigint)',v,'23514','identity_membership_revision_exhausted','org_member_revision_positive')
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state(case)==before and self.snapshot(case)==catalog
        self.passed('membership-actor-attribution-writes',owner_prepared_adoption=True,actual_restricted_login_null_columns=True,adopted_fields_set_role_service_role=True,legacy_fields_times_preserved=True,rollback_only=True)

    def preserved_upgrade(self,case,legacy=False):
        before=self.data_state(case,membership_without_revision=legacy)
        members=self.sql(case,'SELECT to_jsonb(m) FROM identity.org_member m ORDER BY id')
        external=self.external_state(case) if case!='clean' else None
        self.command('membership-actor-attribution-'+case,case,mode='adopt' if legacy else 'clean')
        after=self.data_state(case,membership_without_revision=legacy)
        assert all(after[key]==value for key,value in before.items() if key not in {'identity.alembic_version','org_member'})
        new=self.sql(case,'SELECT to_jsonb(m) FROM identity.org_member m ORDER BY id')
        assert len(new)==len(members)
        for (old,), (row,) in zip(members,new):
            assert row['created_actor_id'] is None and row['updated_actor_id'] is None
            normalized={k:v for k,v in row.items() if k not in FIELDS and not (legacy and k=='revision')}
            assert normalized==old
        assert external is None or self.external_state(case)==external

    @contextmanager
    def failure_fixture(self,case):
        state_sql="""SELECT 'function',p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.proname='synthetic_membership_actor_attribution_failure'
            UNION ALL SELECT 'event_trigger',evtname FROM pg_event_trigger WHERE evtname='synthetic_membership_actor_attribution_failure'
            UNION ALL SELECT 'sequence',c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relname='synthetic_membership_actor_attribution_failure_marker' ORDER BY 1,2"""
        before=self.admin_sql(case,state_sql);assert before==[],'membership_actor_attribution_failure_fixture_already_exists'
        marker_sql='SELECT last_value,is_called FROM public.synthetic_membership_actor_attribution_failure_marker'
        create="""CREATE SEQUENCE public.synthetic_membership_actor_attribution_failure_marker START WITH 1;
            REVOKE ALL ON SEQUENCE public.synthetic_membership_actor_attribution_failure_marker FROM PUBLIC,anon,authenticated,service_role,access_runtime;
            GRANT USAGE ON SEQUENCE public.synthetic_membership_actor_attribution_failure_marker TO identity_migrator;
            CREATE FUNCTION public.synthetic_membership_actor_attribution_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN
            IF to_regprocedure('identity.guard_org_member_actor_attribution()') IS NOT NULL THEN
                PERFORM pg_catalog.nextval('public.synthetic_membership_actor_attribution_failure_marker'::regclass);
                RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_membership_actor_attribution_failure';
            END IF; END $$;
            CREATE EVENT TRIGGER synthetic_membership_actor_attribution_failure ON ddl_command_end WHEN TAG IN ('CREATE TRIGGER') EXECUTE FUNCTION public.synthetic_membership_actor_attribution_failure();"""
        cleanup='DROP EVENT TRIGGER IF EXISTS synthetic_membership_actor_attribution_failure; DROP FUNCTION IF EXISTS public.synthetic_membership_actor_attribution_failure(); DROP SEQUENCE IF EXISTS public.synthetic_membership_actor_attribution_failure_marker'
        self.witness('membership-actor-attribution-event-restoration-required',{'case':case,'before':before,'create':create,'cleanup':cleanup})
        verified=False
        def verify_fired():
            nonlocal verified
            marker=self.admin_sql(case,marker_sql)
            assert marker==[(1,True)],'membership_actor_attribution_failure_fixture_not_fired'
            if not verified:
                self.witness('membership-actor-attribution-event-fired',{'case':case,'marker_before':[1,False],'marker_after':list(marker[0]),'new_guard_observed':True})
                verified=True
        with self.restoration_signals():
            try:
                self.admin_sql(case,create)
                assert self.admin_sql(case,marker_sql)==[(1,False)],'membership_actor_attribution_failure_marker_initially_called'
                yield verify_fired
                verify_fired()
            finally:
                for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,signal.SIG_IGN)
                self.admin_sql(case,cleanup)
                assert self.admin_sql(case,state_sql)==before,'membership_actor_attribution_failure_fixture_not_restored'
                self.witness('membership-actor-attribution-event-restored',{'case':case,'exact_objects':True})


    def blocked_index_ddl(self):
        case='failure';before,catalog=self.data_state(case),self.snapshot(case)
        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0014',)]
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as holder:
                tx=holder.begin()
                try:
                    holder.execute(text("SET LOCAL statement_timeout='15s'; SET LOCAL lock_timeout='2s'"))
                    holder.execute(text('LOCK TABLE identity.org_member IN ROW EXCLUSIVE MODE'))
                    started=time.monotonic()
                    self.command('membership-actor-attribution-blocked-ddl-refused',case,expected='identity_migration_failed_requires_reconciliation')
                    elapsed=time.monotonic()-started
                    assert 4<=elapsed<30,'membership_actor_attribution_blocked_ddl_bound'
                    assert self.data_state(case)==before and self.snapshot(case)==catalog
                    assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0014',)]
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state(case)==before and self.snapshot(case)==catalog
        self.witness('membership-actor-attribution-blocked-ddl-restored',{'case':case,'elapsed_seconds':round(elapsed,3),
            'lock_mode':'ROW EXCLUSIVE','migration_lock_timeout_seconds':5,'old_catalog_history_data_preserved':True})
        self.passed('membership-actor-attribution-blocked-ddl',bounded_refusal=True,owner_lock_released=True)

    def function_drift_refusal(self):
        case='unknown';before,catalog=self.data_state(case),self.snapshot(case)
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    assert c.execute(text('SELECT version_num FROM identity.alembic_version')).scalar_one()=='identity_0014'
                    rows=self.state(c)
                    definition=next(row[4] for row in catalog['functions'] if row[:3]==['identity','guard_org_member_revision',''])
                    c.exec_driver_sql(definition.replace('BEGIN\n','BEGIN\n    -- synthetic source drift\n',1),execution_options={'no_parameters':True})
                    changed=baseline.target_catalog_snapshot(c)
                    assert {key for key in catalog if catalog[key]!=changed[key]}=={'functions'}
                    try:baseline.preflight(c,'clean')
                    except baseline.BaselineError as error:assert str(error)=='identity_catalog_mismatch:functions'
                    else:raise AssertionError('membership_actor_attribution_function_drift_accepted')
                    assert baseline.target_catalog_snapshot(c)==changed and self.state(c)==rows
                    assert c.execute(text('SELECT version_num FROM identity.alembic_version')).scalar_one()=='identity_0014'
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state(case)==before and self.snapshot(case)==catalog
        self.passed('membership-actor-attribution-function-drift-refused',rollback_only=True,no_normalization=True)

    def default_grantee_refusal(self):
        """Extra existing-role default grant; all DDL/default changes roll back."""
        case='characterization';before,catalog=self.data_state(case),self.snapshot(case)
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    c.execute(text('ALTER DEFAULT PRIVILEGES IN SCHEMA identity GRANT EXECUTE ON FUNCTIONS TO access_target_reader'))
                    defaults=list(c.execute(text(baseline.QUERIES['default_privileges'])))
                    c.execute(text("CREATE FUNCTION identity.synthetic_member_actor_default_probe() RETURNS integer LANGUAGE sql AS 'SELECT 1'"))
                    probe=c.execute(text("SELECT proacl::text FROM pg_proc WHERE oid='identity.synthetic_member_actor_default_probe()'::regprocedure")).scalar_one()
                    assert c.execute(text("SELECT has_function_privilege('access_target_reader','identity.synthetic_member_actor_default_probe()','EXECUTE')")).scalar_one() is True
                    source=OWNER/'versions/0015_membership_actor_attribution.py'
                    spec=importlib.util.spec_from_file_location('membership_actor_acl_source',source)
                    revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
                    c.exec_driver_sql(revision.MEMBERSHIP_ACTOR_ATTRIBUTION_SQL,execution_options={'no_parameters':True})
                    assert c.execute(text("SELECT has_function_privilege('access_target_reader','identity.guard_org_member_actor_attribution()','EXECUTE')")).scalar_one() is False
                    assert c.execute(text("SELECT bool_and(a.grantee=p.proowner) FROM pg_proc p,LATERAL aclexplode(p.proacl) a WHERE p.oid='identity.guard_org_member_actor_attribution()'::regprocedure")).scalar_one() is True
                    assert list(c.execute(text(baseline.QUERIES['default_privileges'])))==defaults
                    assert c.execute(text("SELECT proacl::text FROM pg_proc WHERE oid='identity.synthetic_member_actor_default_probe()'::regprocedure")).scalar_one()==probe
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state(case)==before and self.snapshot(case)==catalog
        self.passed('membership-actor-attribution-extra-default-grantee',extra_role='access_target_reader',default_acl_and_probe_preserved=True,rollback_only=True)

    def current_guard_drift_refusal(self):
        case='clean';before,catalog=self.data_state(case),self.snapshot(case)
        definition=next(row[4] for row in catalog['functions'] if row[:3]==['identity','guard_org_member_actor_attribution',''])
        assert definition.count("current_user <> 'identity_migrator'")==1
        forms=[('functions',definition.replace("current_user <> 'identity_migrator'",'FALSE',1)),
               ('triggers','ALTER TABLE identity.org_member DISABLE TRIGGER org_member_actor_attribution_guard')]
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as c:
                for category,statement in forms:
                    tx=c.begin()
                    try:
                        c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                        c.exec_driver_sql(statement,execution_options={'no_parameters':True})
                        changed=baseline.target_catalog_snapshot(c)
                        assert {key for key in catalog if catalog[key]!=changed[key]}=={category}
                        rows=self.state(c)
                        try:baseline.preflight(c,'clean')
                        except baseline.BaselineError as error:assert str(error)=='identity_catalog_mismatch:'+category
                        else:raise AssertionError('membership_actor_current_guard_drift_accepted')
                        assert baseline.target_catalog_snapshot(c)==changed and self.state(c)==rows
                        assert c.execute(text('SELECT version_num FROM identity.alembic_version')).scalar_one()=='identity_0015'
                    finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state(case)==before and self.snapshot(case)==catalog
        self.passed('membership-actor-attribution-current-guard-drift',changed_and_disabled_guard=True,no_normalization=True,rollback_only=True)

    def repeat_preservation(self):
        """Retain one extra attributed synthetic member; never modify original rows."""
        case='clean';v=self.inputs[case];actor=str(uuid.uuid4())
        before=self.data_state(case)
        original_members=self.sql(case,'SELECT to_jsonb(m) FROM identity.org_member m ORDER BY id')
        original_actors=self.sql(case,'SELECT to_jsonb(a) FROM identity.actor a ORDER BY id')
        self.witness('membership-actor-attribution-repeat-fixture-intent',{'case':case,
            'actor_id':actor,'org_id':v['spare_org'],'account_id':v['spare'],
            'new_synthetic_rows_retained':True,'original_rows_must_remain':True})
        db=engine(self.private['owner_urls'][case])
        try:
            with db.begin() as c:
                c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                assert c.execute(text('SELECT current_user')).scalar_one()=='identity_migrator'
                c.execute(text("INSERT INTO identity.actor(id,kind,actor_key,display_name,created_by,updated_by) VALUES(CAST(:actor AS uuid),'service',:key,'Synthetic repeat fixture',CAST(:actor AS uuid),CAST(:actor AS uuid))"),{'actor':actor,'key':'synthetic:membership-repeat:'+actor})
                member=c.execute(text('INSERT INTO identity.org_member(org_id,user_id,created_actor_id,updated_actor_id) VALUES(CAST(:org AS uuid),CAST(:account AS uuid),CAST(:actor AS uuid),CAST(:actor AS uuid)) RETURNING to_jsonb(org_member)'),
                    {'actor':actor,'org':v['spare_org'],'account':v['spare']}).scalar_one()
                assert member['revision']==1 and member['created_actor_id']==actor and member['updated_actor_id']==actor
        finally:db.dispose()
        assert self.sql(case,'SELECT to_jsonb(m) FROM identity.org_member m WHERE id<>:id ORDER BY id',{'id':member['id']})==original_members
        assert self.sql(case,'SELECT to_jsonb(a) FROM identity.actor a WHERE id<>CAST(:actor AS uuid) ORDER BY id',{'actor':actor})==original_actors
        prepared=self.data_state(case)
        assert all(prepared[key]==value for key,value in before.items() if key not in {'actor','org_member'})
        catalog=self.snapshot(case)
        self.command('membership-actor-attribution-repeat',case)
        assert self.snapshot(case)==catalog and self.data_state(case)==prepared
        assert self.sql(case,'SELECT to_jsonb(m) FROM identity.org_member m WHERE id=:id',{'id':member['id']})==[(member,)]
        self.witness('membership-actor-attribution-repeat-preserved',{'case':case,
            'actor_id':actor,'membership_id':str(member['id']),'catalogue_and_all_rows_unchanged':True,
            'synthetic_fixture_retained':True})
        self.passed('membership-actor-attribution-repeat-preserved',populated_actor_references=True,original_rows_preserved=True)

    def unknown_history_refusal(self):
        db=engine(self.private['owner_urls']['unknown']);before,catalog=self.data_state('unknown'),self.snapshot('unknown')
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
                    c.execute(text("UPDATE identity.alembic_version SET version_num='identity_unknown'"))
                    try:baseline.preflight(c,'clean')
                    except baseline.BaselineError as error:assert str(error)=='identity_unknown_history'
                    else:raise AssertionError('unknown_history_accepted')
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state('unknown')==before and self.snapshot('unknown')==catalog

    def unknown_history_lock_refusal(self):
        case='unknown';before,catalog=self.data_state(case),self.snapshot(case)
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as holder:
                tx=holder.begin()
                try:
                    holder.execute(text("SET LOCAL statement_timeout='15s'; SET LOCAL lock_timeout='2s'"))
                    holder.execute(text('LOCK TABLE identity.alembic_version IN SHARE MODE'))
                    started=time.monotonic()
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        future=pool.submit(self.unknown_history_refusal)
                        try:future.result(timeout=12)
                        except Exception as error:assert getattr(getattr(error,'orig',None),'sqlstate',None)=='55P03'
                        else:raise AssertionError('unknown_history_lock_wait_not_refused')
                    assert 1.5<=time.monotonic()-started<12
                finally:tx.rollback()
        finally:db.dispose()
        assert self.data_state(case)==before and self.snapshot(case)==catalog
        self.passed('membership-actor-attribution-unknown-history-lock',bounded_refusal=True,rollback_only=True)

    def upgrades_and_failures(self):
        self.validate_targets();self.prior_evidence(PREVIOUS_COMMIT,PREVIOUS_FILES,'identity_0014')
        self.default_grantee_refusal()
        self.preserved_upgrade('clean');self.compatibility();self.attribution_writes();self.writes()
        self.repeat_preservation();self.current_guard_drift_refusal()
        self.legacy('legacy');self.original_ledger('legacy')
        for case in ['legacy','previous']:
            self.row_fixtures(case);self.preserved_upgrade(case,legacy=case=='legacy')
        self.blocked_index_ddl()
        with self.failure_fixture('failure') as fired:
            before,catalog=self.data_state('failure'),self.snapshot('failure')
            self.command('membership-actor-attribution-ddl-rollback','failure',expected='identity_migration_failed_requires_reconciliation')
            fired();assert self.data_state('failure')==before and self.snapshot('failure')==catalog
            assert self.sql('failure','SELECT version_num FROM identity.alembic_version')==[('identity_0014',)]
        self.command('membership-actor-attribution-after-rollback','failure')
        self.command('membership-actor-attribution-unsafe-clean','unsafe')
        with self.acl_fixture('unsafe','GRANT INSERT ON identity.users TO authenticated','REVOKE INSERT ON identity.users FROM authenticated','GRANT INSERT (id, username) ON identity.users TO authenticated'):
            before,catalog=self.data_state('unsafe'),self.snapshot('unsafe')
            self.command('membership-actor-attribution-drift-refused','unsafe',expected='identity_profile_column_privileges_mismatch')
            assert self.data_state('unsafe')==before and self.snapshot('unsafe')==catalog
        self.command('membership-actor-attribution-drift-reconciled','unsafe')
        self.function_drift_refusal()
        self.unknown_history_refusal();self.unknown_history_lock_refusal()
        self.passed('membership-actor-attribution-migration-matrix',clean_adopt_exact14_repeat=True,rollback_recovery=True,drift_unknown_refused=True)


def main():
    if not __debug__:raise RuntimeError('membership_actor_attribution_qualification_optimized_python_prohibited')
    proof,private=fixture();q=MembershipActorAttributionQualification(proof,private)
    if sys.argv[1:]==['--characterize']:q.validate_targets();q.characterize()
    elif not sys.argv[1:]:q.upgrades_and_failures()
    else:raise RuntimeError('qualification_arguments_invalid')
    q.persist()


def entrypoint():
    try:
        main()
    except Exception:
        print('membership_actor_attribution_qualification_failed',file=sys.stderr)
        return 1
    return 0


if __name__=='__main__':raise SystemExit(entrypoint())
