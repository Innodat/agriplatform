"""Source-bound synthetic Identity19→20 proof; no target reference export route."""
if not __debug__:
    raise RuntimeError('check_reader_bridge_optimized_python_prohibited')
import importlib.util
import json
import os
import re
import time
from pathlib import Path
import subprocess
import sys
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from sqlalchemy import text
sys.path.insert(0, str(Path(__file__).resolve().parent))
import qualify_grant_assign as assign
import qualify_grant_revoke as revoke
import qualify_entry_permission_register as entry
import qualify_application_set_enabled as enable
import qualify_organization_application_configure as configure
base, storage = assign.base, assign.storage
ROOT, ACCESS, ACTOR = assign.ROOT, assign.ACCESS, assign.ACTOR
CASES = frozenset(('reference', 'bridge'))
base.CASES = CASES
spec = importlib.util.spec_from_file_location('bridge_identity_baseline', ACCESS/'identity-migrations/identity_baseline.py')
baseline = importlib.util.module_from_spec(spec); spec.loader.exec_module(baseline)
OWNER = ACCESS/'identity-migrations'
CALL = 'SELECT account_id::text,org_id::text,membership_id,membership_revision,actor_id::text FROM identity.current_account_organization()'
NIL = '00000000-0000-0000-0000-000000000000'

# Final safe exception identifiers observed in the independent proof8 logs.
REFUSAL_CODES = {
    'unsafe-login':'identity_check_reader_role_unsafe',
    'unsafe-inherit':'identity_check_reader_role_unsafe',
    'incoming-membership':'identity_catalog_mismatch',
    'outgoing-membership':'identity_check_reader_role_unsafe',
    'nonempty-schema':'identity_catalog_mismatch',
    'public-raw-column':'identity_target_role_unsafe',
    'public-routine':'identity_target_role_unsafe',
    'ledger':'identity_unknown_history',
    'catalog-drift':'identity_catalog_mismatch',
    'injected-postcondition':'identity_test_postcondition_failure',
    'blocked-advisory':'identity_migration_busy',
    'blocked-ledger-lock':'identity_migration_failed_requires_reconciliation',
    'repeat20-drift':'identity_check_reader_dependencies_unsafe',
}
LOCK_PROBE_TIMEOUT = 15
LOCK_PROBE_ELAPSED_BOUND = 12


def final_identity_error(output):
    lines=output.rstrip().splitlines()
    match=re.fullmatch(rb'(?:[A-Za-z_][A-Za-z0-9_.]*\.)?BaselineError: (identity_[a-z_]+)(?::[a-z_,]+)?[ \t]*',lines[-1]) if lines else None
    return match[1].decode('ascii') if match else None


def qualification_logs(proof):
    return {p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(set(proof.glob('*.log'))|set(proof.glob('check-reader-*-refusal.json')))}


def verify_qualification_logs(proof, expected):
    assert type(expected) is dict and expected, 'qualification_logs_missing'
    assert qualification_logs(proof)==expected, 'qualification_log_custody_mismatch'


def source_snapshot(proof):
    # Fixed private inputs only. Never enumerate unrelated retained frames.
    paths = {Path(__file__), Path(__file__).with_name('test_check_reader_bridge.py'), ACCESS/'CHECK-READER-BRIDGE.md'}
    for pattern in ('*.py','migrations/*.py','migrations/versions/*.py','identity-migrations/*.py','identity-migrations/*.json','identity-migrations/versions/*.py','tools/*.sql'):
        paths.update(ACCESS.glob(pattern))
    paths.update(Path(__file__).parent.glob('qualify_*.py'))
    paths.update(ROOT/p for p in ('platform/deployment/dev.py','platform/deployment/native_cli.py','platform/deployment/images.py','platform/deployment/toolchain.py','platform/deployment/schema/development-target-v1.json','platform/deployment/environments/kdg-local.json'))
    paths.update(ACCESS/p for p in ('alembic.ini','identity-alembic.ini','identity-migrations/pyproject.toml','identity-migrations/uv.lock'))
    paths.update(proof/p for p in ('bootstrap.py','baseline-preparation-custody.json','auth-helper-definitions.json','credentials.json','run.json','runtime-credential.json','identity-operator-credential.json','actor-bootstrap-evidence.json'))
    # Preparation may use an exact historical owner tree to establish19 with
    # its original postcondition before the controlled20 qualification. Bind all
    # actually consumed helper bytes without inspecting unrelated private frames.
    for name in ('historical_identity19_driver.py','root_qualification_driver.py'):
        helper=proof/name
        if helper.exists():paths.add(helper)
    historical=proof/'historical-identity19'
    if historical.exists():paths.update(p for p in historical.rglob('*') if p.is_file())
    run = json.loads((proof/'run.json').read_text())
    paths.add(ROOT/'platform/deployment/.local/kdg'/run['run_id']/'supabase/config.toml')
    return {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


class Qualification(assign.Qualification):
    def __init__(self, proof, private):
        super().__init__(proof, private)
        self.targets = {}
        self.prior_commands = []
    def record(self, stage):
        self.results.append(stage)
        print(json.dumps({'stage': stage, 'status': 'passed'}), flush=True)
    def identity(self, label, *, success=True, injected=False):
        env = {'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8','IDENTITY_MIGRATION_DATABASE_URL':self.private['owner_urls']['bridge'].replace('postgresql://','postgresql+psycopg://',1)}
        if injected:
            code = '''import sys
sys.path.insert(0,OWNER)
import identity_baseline as b
from alembic.config import Config
from alembic import command
original=b.verify_owned_postcondition
def verify(c,require_head=False):
    original(c,require_head=require_head)
    if require_head: raise b.BaselineError('identity_test_postcondition_failure')
b.verify_owned_postcondition=verify
command.upgrade(Config(INI),'head')
'''.replace('OWNER',repr(str(OWNER))).replace('INI',repr(str(ACCESS/'identity-alembic.ini')))
            cmd = [sys.executable,'-I','-B','-c',code]
        else: cmd = [sys.executable,'-I','-B','-m','alembic','-c',str(ACCESS/'identity-alembic.ini'),'upgrade','head']
        lock_probe=label in ('blocked-advisory','blocked-ledger-lock')
        started=time.monotonic()
        result = subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,timeout=LOCK_PROBE_TIMEOUT if lock_probe else 90)
        elapsed=time.monotonic()-started
        path=self.proof/('check-reader-'+label+'.log')
        descriptor=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(descriptor,'wb') as output: output.write(result.stdout+result.stderr)
        assert (result.returncode==0)==success, 'identity_controlled_result_mismatch:'+label
        if not success:
            assert final_identity_error(result.stdout+result.stderr)==REFUSAL_CODES[label], 'identity_refusal_code_mismatch:'+label
        if lock_probe:assert elapsed<LOCK_PROBE_ELAPSED_BOUND, 'identity_lock_probe_exceeded_bound'
    def admin_sql(self, sql):
        db=self.admin('bridge')
        try:
            with db.begin() as c: c.exec_driver_sql(sql)
        finally: db.dispose()
    def catalog(self):
        db=self.db('bridge','owner_urls')
        try:
            with db.connect() as c: return baseline.check_reader_bridge_catalog_snapshot(c)
        finally: db.dispose()
    def check(self):
        db=self.db('bridge','owner_urls')
        try:
            with db.connect() as c:
                c.exec_driver_sql('SET TRANSACTION READ ONLY')
                baseline.verify_owned_postcondition(c,require_head=True)
        finally: db.dispose()
    def prepare(self):
        case='bridge'
        print(json.dumps(dict(stage='prepare-Access14',status='started')),flush=True)
        self.migrate(case,'access_0014'); self.seed(case)
        print(json.dumps(dict(stage='prepare-supported-Identity-fixtures',status='started')),flush=True)
        self.prepare_identity(case)
        print(json.dumps(dict(stage='prepare-prior-Access-command-receipts',status='started')),flush=True)
        for value in (base.document(),assign.strict.permission_document(),
                      entry.document(assign.PERMISSION),enable.document(False)):
            self.prior_commands.append((value,self.command(case,value)))
        value=configure.document(False)
        self.prior_commands.append((value,self.command(case,value)))
        assign.Qualification.authority(self,case)
        target=self.targets[case]
        value=assign.document(target['account'],target['member'])
        self.prior_commands.append((value,self.command(case,value)))
        self.parameter_sql(case,"INSERT INTO identity.member_role(member_id,role) VALUES(CAST(:member AS bigint),'employee')",dict(member=target['member']))
        self.record('supported-ensure-join-populated-Access14-prior-grant-receipt')
    def raw_catalog(self):
        """Observe deliberate invalid fixtures without approving/normalizing them."""
        db=self.db('bridge','owner_urls')
        try:
            with db.connect() as c:
                result=baseline.catalog_snapshot(c)
                current=c.exec_driver_sql('SELECT current_database()').scalar_one()
                for key,sql in baseline.CHECK_READER_ROLE_QUERIES.items():
                    rows=[list(row) for row in c.execute(text(sql))]
                    if key.endswith('_dependencies'):
                        for row in rows:
                            if row[0]==current:row[0]='current_database'
                    result[key]=sorted(rows,key=lambda row:json.dumps(row,sort_keys=True))
                for category in ('effective_tables','effective_columns','effective_functions','effective_schemas','effective_sequences'):
                    sql=baseline.QUERIES[category].replace("'identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin'", "'access_check_reader'")
                    sql=sql.replace(" AND c.relname<>'alembic_version'",'')
                    result['check_reader_'+category]=sorted([list(row) for row in c.execute(text(sql))],key=lambda row:json.dumps(row,sort_keys=True))
                return result
        finally:db.dispose()
    def refusal(self, label, change, restore):
        before=self.snapshot('bridge'); catalog=self.raw_catalog()
        witness=dict(stage=label,status='started')
        self.admin_sql(change)
        try:
            drift=self.snapshot('bridge'); drift_catalog=self.raw_catalog()
            witness['status']='drift-observed'
            self.identity(label,success=False)
            assert self.snapshot('bridge')==drift and self.raw_catalog()==drift_catalog, 'refusal_mutated_state'
            witness['status']='refusal-preserved-drift'
        finally:
            # Restoration is fixture cleanup, never production normalization.
            # Preserve the failed stage witness even when an observer/runner fails.
            try:
                self.admin_sql(restore)
                assert self.snapshot('bridge')==before and self.raw_catalog()==catalog, 'fixture_restore_changed_state'
                witness['restored']=True
            finally:
                path=self.proof/('check-reader-'+label+'-refusal.json')
                descriptor=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
                with os.fdopen(descriptor,'w') as output:json.dump(witness,output,sort_keys=True)
    def foreign_policy_dependency(self):
        before=self.snapshot('bridge'); catalog=self.raw_catalog()
        db=self.admin('bridge')
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    c.exec_driver_sql("SET LOCAL lock_timeout='2s'")
                    c.exec_driver_sql("SET LOCAL statement_timeout='5s'")
                    assert c.exec_driver_sql("SELECT to_regclass('public.check_reader_policy_fixture') IS NULL").scalar_one()
                    c.exec_driver_sql('CREATE TABLE public.check_reader_policy_fixture (id integer)')
                    c.exec_driver_sql('ALTER TABLE public.check_reader_policy_fixture ENABLE ROW LEVEL SECURITY')
                    c.exec_driver_sql('CREATE POLICY check_reader_foreign_policy ON public.check_reader_policy_fixture TO access_check_reader USING (true)')
                    try:baseline.verify_check_reader_role(c,staged=True,legacy=True)
                    except baseline.BaselineError as error:assert str(error)=='identity_check_reader_role_not_empty'
                    else:raise AssertionError('foreign_policy_dependency_not_refused')
                finally:tx.rollback()
            with db.connect() as c:
                assert c.exec_driver_sql("SELECT to_regclass('public.check_reader_policy_fixture') IS NULL").scalar_one()
                baseline.verify_check_reader_role(c,staged=True,legacy=True)
        finally:db.dispose()
        assert self.snapshot('bridge')==before and self.raw_catalog()==catalog, 'foreign_policy_fixture_not_restored'
        self.record('rollback-only-foreign-policy-role-dependency-refused-and-fully-restored')
    def before_upgrade(self):
        self.foreign_policy_dependency()
        for label,change,restore in (
            ('unsafe-login','ALTER ROLE access_check_reader LOGIN','ALTER ROLE access_check_reader NOLOGIN'),
            ('unsafe-inherit','ALTER ROLE access_check_reader INHERIT','ALTER ROLE access_check_reader NOINHERIT'),
            ('incoming-membership','GRANT access_check_reader TO access_runtime','REVOKE access_check_reader FROM access_runtime'),
            ('outgoing-membership','GRANT access_runtime TO access_check_reader','REVOKE access_runtime FROM access_check_reader'),
            ('nonempty-schema','GRANT USAGE ON SCHEMA identity TO access_check_reader','REVOKE USAGE ON SCHEMA identity FROM access_check_reader'),
            ('public-raw-column','GRANT SELECT(id) ON identity.org TO PUBLIC','REVOKE SELECT(id) ON identity.org FROM PUBLIC'),
            ('public-routine','GRANT EXECUTE ON FUNCTION identity.current_account_actor() TO PUBLIC','REVOKE EXECUTE ON FUNCTION identity.current_account_actor() FROM PUBLIC'),
            ('ledger','GRANT SELECT ON identity.alembic_version TO access_check_reader','REVOKE SELECT ON identity.alembic_version FROM access_check_reader'),
            ('catalog-drift','ALTER FUNCTION identity.current_account_organization() VOLATILE','ALTER FUNCTION identity.current_account_organization() STABLE'),
        ): self.refusal(label,change,restore)
        before=self.snapshot('bridge'); catalog=self.catalog()
        self.identity('injected-postcondition',success=False,injected=True)
        assert self.snapshot('bridge')==before and self.catalog()==catalog
        # Both lock failures must roll back, then the ordinary forward upgrade retries.
        for label,statement in (
            ('advisory',"SELECT pg_advisory_xact_lock(hashtextextended('identity-owned-migrations',0))"),
            ('ledger-lock','LOCK TABLE identity.alembic_version IN ACCESS EXCLUSIVE MODE')):
            owner=self.db('bridge','owner_urls')
            try:
                with owner.connect() as holder:
                    tx=holder.begin()
                    try:
                        holder.exec_driver_sql(statement)
                        with ThreadPoolExecutor(max_workers=1) as pool:
                            pool.submit(self.identity,'blocked-'+label,success=False).result(timeout=20)
                    finally:tx.rollback()
            finally:owner.dispose()
            assert self.snapshot('bridge')==before and self.catalog()==catalog, 'lock_refusal_changed_state'
        self.record('flags-bidirectional-memberships-dependencies-PUBLIC-ledger-catalog-refusals-atomic-postcondition-rollback')
    def context(self,c,**changes):
        target=self.targets['bridge']
        values=dict(context_kind='user',account_id=target['account'],org_id=assign.ORG1,actor_id=target['actor'])|changes
        for key,value in values.items():
            if value is not None: c.execute(text('SELECT set_config(:key,:value,true)'),dict(key='app.'+key,value=value))
    def restricted(self, changes, expected):
        db=self.admin('bridge')
        try:
            with db.begin() as c:
                c.exec_driver_sql('SET LOCAL SESSION AUTHORIZATION access_check_reader')
                assert c.exec_driver_sql('SELECT current_user').scalar_one()=='access_check_reader'
                self.context(c,**changes)
                assert c.exec_driver_sql(CALL).all()==expected, 'projection_context_wrong'
        finally: db.dispose()
    def read_matrix(self):
        t=self.targets['bridge']; expected=[(t['account'],assign.ORG1,int(t['member']),1,t['actor'])]
        before=self.snapshot('bridge'); catalog=self.catalog()
        self.restricted({},expected)
        self.restricted(dict(account_id=t['unmapped'],actor_id=ACTOR),[(t['unmapped'],assign.ORG1,int(t['unmapped_member']),1,None)])
        for key in ('account_id','org_id'):
            for value in (None,'','malformed',NIL,'33333333-3333-4333-8333-333333333333'):
                self.restricted({key:value},[])
        for value in (None,'','setup','invalid'): self.restricted(dict(context_kind=value),[])
        # Missing actor assertions do not alter the unchanged projection contract.
        for actor in (None,'','malformed',NIL): self.restricted(dict(actor_id=actor),expected)
        assert self.snapshot('bridge')==before and self.catalog()==catalog
        self.record('current-member-nullable-internal-actor-missing-malformed-setup-wrong-account-org-context')
        # Retire through the supported owner command, then prove no replacement lookup.
        self.invoke('bridge','membership.retire',dict(account_id=t['account'],membership_id=str(t['member']),expected_revision='1'),assign.ORG1)
        before=self.snapshot('bridge'); self.restricted({},[]); assert self.snapshot('bridge')==before
        self.record('retired-membership-fails-closed-with-unchanged-data')
        # Deleted profiles and organizations are temporary rolled-back fixture mutations.
        db=self.admin('bridge')
        try:
            for table,key,value in [('users','id',t['unmapped']),('org','id',assign.ORG1)]:
                with db.connect() as c:
                    tx=c.begin()
                    try:
                        c.execute(text('UPDATE identity.'+table+' SET deleted_at=now() WHERE '+key+'=CAST(:id AS uuid)'),{'id':value})
                        c.exec_driver_sql('SET LOCAL SESSION AUTHORIZATION access_check_reader')
                        self.context(c,account_id=t['unmapped'])
                        assert c.exec_driver_sql(CALL).all()==[]
                    finally: tx.rollback()
        finally: db.dispose()
        assert self.snapshot('bridge')==before
        self.record('deleted-profile-organization-fail-closed-rollback-preserves-complete-state')
    def privileges(self):
        db=self.admin('bridge')
        try:
            for statement in (
                "SELECT identity.custom_access_token_hook('{\"user_id\":\""+self.targets['bridge']['other']+"\",\"claims\":{}}'::jsonb)",
                "SELECT identity.create_user('synthetic-denied@example.invalid')",
                "SELECT identity.authorize('identity.users.admin')",
                'SELECT * FROM public.get_user_roles()',
                "SELECT identity.membership_join_profile_allowed('"+self.targets['bridge']['other']+"')",
                "SELECT identity.membership_join_org_allowed('"+assign.ORG1+"')",
                'SELECT * FROM identity.users','SELECT * FROM identity.org_member','SELECT * FROM identity.actor','SELECT * FROM identity.alembic_version','SELECT * FROM access.grants','SELECT * FROM access.alembic_version','SELECT * FROM identity.current_account_actor()','SELECT * FROM identity.organization_account_candidates(NULL::uuid)',"SELECT * FROM identity.organization_account_target('"+self.targets['bridge']['other']+"',"+str(self.targets['bridge']['other_member'])+")","SELECT * FROM identity.organization_target('11111111-1111-4111-8111-111111111111')",'UPDATE identity.org SET name=name','SET ROLE identity_account_projection_owner','SET ROLE identity_target_projection_owner','SET ROLE identity_migrator','SET ROLE access_command_owner'):
                with db.begin() as c:
                    c.exec_driver_sql('SET LOCAL SESSION AUTHORIZATION access_check_reader'); self.context(c)
                    assert c.exec_driver_sql("SELECT has_schema_privilege(current_user,'identity','USAGE')").scalar_one()
                    c.execute(text("SELECT set_config('request.jwt.claims',:claims,true)"),dict(claims=json.dumps(dict(role='authenticated',sub=self.targets['bridge']['other'],member_id=self.targets['bridge']['other_member'],user_roles=['admin']))))
                    savepoint=c.begin_nested()
                    try: c.exec_driver_sql(statement)
                    except Exception as error: assert getattr(getattr(error,'orig',None),'sqlstate',None)=='42501', 'unexpected_denial'
                    else: raise AssertionError('reader_authority_expanded')
                    finally: savepoint.rollback()
        finally: db.dispose()
        self.record('actual-private-role-raw-tables-both-ledgers-other-projections-writes-owner-escalation-denied')
    def supported_callers(self):
        t=self.targets['bridge']; before=self.snapshot('bridge'); catalog=self.catalog()
        db=self.admin('bridge')
        try:
            with db.connect() as c:
                profile_count=c.exec_driver_sql('SELECT count(*) FROM identity.users').scalar_one()
            # Authorized legacy Auth and Expense role lookup keep their useful results.
            for role in ('supabase_auth_admin','authenticated'):
                with db.begin() as c:
                    c.exec_driver_sql('SET LOCAL SESSION AUTHORIZATION '+role)
                    self.context(c)
                    claims=dict(role='authenticated',sub=t['account'],org_id=assign.ORG1,member_id=t['member'])
                    c.execute(text("SELECT set_config('request.jwt.claims',:claims,true)"),dict(claims=json.dumps(claims)))
                    if role=='supabase_auth_admin':
                        event=dict(user_id=t['account'],claims=dict(sub=t['account']))
                        result=c.execute(text('SELECT identity.custom_access_token_hook(CAST(:event AS jsonb))'),dict(event=json.dumps(event))).scalar_one()['claims']
                        assert result['member_id']==int(t['member']) and result['org_id']==assign.ORG1
                        assert result['user_roles']==['employee'] and result['sub']==t['account']
                    else:
                        assert c.exec_driver_sql('SELECT role FROM public.get_user_roles()').all()==[('employee',)]
                        # RLS policies do not imply SELECT. Existing8 deliberately
                        # grants only selected INSERT/UPDATE inputs to authenticated.
                        denied_select=c.begin_nested()
                        try:
                            try:c.exec_driver_sql('SELECT id FROM identity.users')
                            except Exception as error:assert getattr(getattr(error,'orig',None),'sqlstate',None)=='42501'
                            else:raise AssertionError('authenticated_profile_select_expanded')
                        finally:denied_select.rollback()
                        assert c.exec_driver_sql("SELECT identity.authorize('finance.purchase.read')").scalar_one() is False
                        # Roll back policy writes, preserving fixture and audit rows.
                        savepoint=c.begin_nested()
                        try:
                            assert c.exec_driver_sql("UPDATE identity.users SET username='Synthetic bridge self profile'").rowcount==1
                            claims['user_roles']=['admin']
                            c.execute(text("SELECT set_config('request.jwt.claims',:claims,true)"),dict(claims=json.dumps(claims)))
                            assert c.exec_driver_sql("SELECT identity.authorize('identity.users.admin')").scalar_one() is True
                            assert c.exec_driver_sql("UPDATE identity.users SET username='Synthetic bridge admin profile'").rowcount==profile_count
                        finally:savepoint.rollback()
            for jwt_role in (None,'authenticated'):
                for role in ('access_runtime','access_target_reader','access_command_owner','postgres','service_role'):
                    with db.begin() as c:
                        c.exec_driver_sql('SET LOCAL SESSION AUTHORIZATION '+role)
                        self.context(c)
                        claims=dict(sub=t['account'],member_id=t['member'],org_id=assign.ORG1)
                        if jwt_role is not None:claims['role']=jwt_role
                        elif role=='postgres':
                            # Without auth.role the legacy PUBLIC read policy needs
                            # explicit admin roles; the retained postgres column
                            # grant alone does not grant RLS admission.
                            claims['user_roles']=['admin']
                        c.execute(text("SELECT set_config('request.jwt.claims',:claims,true)"),dict(claims=json.dumps(claims)))
                        if role=='service_role':
                            assert c.exec_driver_sql("SELECT identity.authorize('identity.users.admin')").scalar_one() is False
                            claims['user_roles']=['admin']
                            c.execute(text("SELECT set_config('request.jwt.claims',:claims,true)"),dict(claims=json.dumps(claims)))
                            assert c.exec_driver_sql("SELECT identity.authorize('identity.users.admin')").scalar_one() is True
                        elif role=='access_runtime':
                            row=c.exec_driver_sql('SELECT account_id::text,actor_id::text FROM identity.current_account_actor()').one()
                            assert tuple(row)==(t['account'],t['actor'])
                            assert c.exec_driver_sql(CALL).all()==[(t['account'],assign.ORG1,int(t['member']),1,t['actor'])]
                        elif role in ('access_target_reader','access_command_owner'):
                            rows=c.execute(text('SELECT account_id::text,membership_id FROM identity.organization_account_target(CAST(:id AS uuid),CAST(:member AS bigint))'),dict(id=t['account'],member=t['member'])).all()
                            assert rows==[(t['account'],int(t['member']))]
                            if role=='access_target_reader':
                                candidates=c.exec_driver_sql('SELECT account_id::text FROM identity.organization_account_candidates(NULL::uuid)').scalars().all()
                                assert set(candidates)=={t['account'],t['other']}
                        else:
                            assert c.execute(text('SELECT id::text FROM identity.users WHERE id=CAST(:id AS uuid)'),dict(id=t['account'])).all()==[(t['account'],)]
        finally:db.dispose()
        assert self.snapshot('bridge')==before and self.catalog()==catalog
        self.record('authorized-Auth-hook-Expense-role-lookup-profile-current-account-target-postgres-callers-with-and-without-JWT-role')
        # Re-observation after20 exercises verifier and command profile RLS without
        # a JWT role, rather than relying on an authenticated-policy short circuit.
        self.invoke('bridge','account_actor.ensure',dict(account_id=t['account'],actor_id=t['actor'],display_name='Synthetic grant target',expected_absent=True))
        member=self.invoke('bridge','membership.join',dict(account_id=t['account'],expected_previous_membership_id=None,is_owner=False),assign.ORG2).result.target.membership_id
        # Existing org1 retire is exercised later by read_matrix; org2 join proves probe ACL.
        assert int(member)>0
        before=self.snapshot('bridge')
        for value,receipt in self.prior_commands:assert self.command('bridge',value)==receipt
        assert self.snapshot('bridge')==before
        revoke.Qualification.authority(self,'bridge')
        # Keep original assignment receipt and binding; revoke through the existing
        # current-authorized Access14 client, then verify exact recovery/replay.
        grant=self.prior_commands[-1][1].result.target.grant_id
        value=revoke.document(t['account'],t['member'],grant)
        receipt=self.command('bridge',value)
        assert receipt.result.disposition=='changed' and receipt.result.revision=='2'
        state=self.snapshot('bridge')
        assert self.command('bridge',value)==receipt
        engine=self.db('bridge','access_operator_urls')
        try:
            with engine.connect() as c:
                recovered=base.adapter.outcome(c,value['operation_id'],command='grant.revoke',org_id=assign.ORG1,grant_id=grant,account_id=t['account'],membership_id=t['member'],permission=assign.PERMISSION)
                assert recovered==receipt
        finally:engine.dispose()
        assert self.snapshot('bridge')==state
        self.record('supported-ensure-join-and-six-prior-Access14-clients-replay-revoke-and-exact-recovery')

    def all(self):
        marker=self.proof/'check-reader-source.json'
        assert not marker.exists(),'qualification_already_started'
        sources=source_snapshot(self.proof); marker.write_text(json.dumps(sources,sort_keys=True,indent=2)+'\n'); marker.chmod(0o600)
        self.prepare(); self.before_upgrade()
        before=self.snapshot('bridge')
        self.identity('controlled19-to20'); self.check()
        after=self.snapshot('bridge')
        old=before['identity'].pop('alembic_version'); new=after['identity'].pop('alembic_version')
        assert old==[{'version_num':'identity_0019'}] and new==[{'version_num':'identity_0020'}]
        assert before==after, 'business_or_Access_state_changed'
        self.record('exact-populated19-controlled20-only-Identity-history-and-approved-ACLs-change')
        before=self.snapshot('bridge');catalog=self.catalog()
        self.identity('repeat20'); assert self.snapshot('bridge')==before and self.catalog()==catalog
        self.refusal('repeat20-drift','GRANT EXECUTE ON FUNCTION identity.current_account_actor() TO access_check_reader','REVOKE EXECUTE ON FUNCTION identity.current_account_actor() FROM access_check_reader')
        self.record('repeat20-exact-preservation-and-drift-refusal-forward-retry')
        self.identity('forward-retry20'); self.check()
        self.supported_callers(); self.privileges(); self.read_matrix()
        assert source_snapshot(self.proof)==sources,'qualification_source_changed'
        retained=dict(sources=sources,logs=qualification_logs(self.proof),state=self.snapshot('bridge'),catalog=self.catalog(),stages=self.results)
        (self.proof/'check-reader-retained.json').write_text(json.dumps(retained,sort_keys=True,indent=2)+'\n')
        (self.proof/'check-reader-retained.json').chmod(0o600)
        self.verify_retained()
    def verify_retained(self):
        retained=json.loads((self.proof/'check-reader-retained.json').read_text())
        assert source_snapshot(self.proof)==retained['sources'],'qualification_source_changed'
        verify_qualification_logs(self.proof,retained['logs'])
        self.check()
        assert self.snapshot('bridge')==retained['state'] and self.catalog()==retained['catalog'],'retained_state_changed'
        self.record('independent-read-only-retained-state-and-source-inspection')


def main():
    assert sys.argv[1:] in (['--all'],['--verify-retained']), 'qualification_action_invalid'
    proof=Path(os.environ['IDENTITY_QUALIFICATION_DIR']).resolve()
    private,run=base.load_fixture(proof)
    q=Qualification(proof,private)
    if sys.argv[1:]==['--all']: q.all()
    else: q.verify_retained()


def run():
    try: main()
    except Exception as error:
        print('check_reader_bridge_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None


if __name__=='__main__': run()
