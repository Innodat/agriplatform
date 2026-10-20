"""Synthetic restricted current-account projection proof; no live provisioning.

Uses prepared private fixtures and the existing Identity qualification/lifecycle owners.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
from urllib.parse import quote,urlsplit,urlunsplit

sys.path.insert(0,str(Path(__file__).resolve().parent))
from qualify_identity_baseline import Qualification,ROOT,baseline,engine,fixture,text


PREVIOUS_COMMIT = '814bf94362a38f2687c0dc732bffac3b405b188f'
PREVIOUS_FILES = frozenset({'identity_baseline.py', 'env.py', 'source-pins.json',
    'reference.json', 'actor-reference.json', 'versions/0001_baseline.py',
    'versions/0002_actor_registry.py'})
PREVIOUS_PYTHON = ROOT/'platform/deployment/.local/identity-baseline/qualification-im60qj1l/owner-env-djguxc78/offline-venv/bin/python'
# Exact inner launcher from the retained previous-setup.py qualification source.
PREVIOUS_LAUNCHER = """import sys
from pathlib import Path
from alembic.config import Config
from alembic import command
sys.path.insert(0,sys.argv[1])
import identity_baseline
identity_baseline.ROOT=Path(sys.argv[2])
c=Config();c.set_main_option('script_location',sys.argv[1]);c.set_main_option('prepend_sys_path',sys.argv[1]);command.upgrade(c,'head')
"""


class ProjectionQualification(Qualification):
    def passed(self,label,**facts):
        self.records.append({'label':label,'status':'passed',**facts});self.persist();print(label,'PASS',flush=True)

    def prior_evidence(self):
        manifest=json.loads((self.proof/'previous-source.json').read_text())
        assert manifest['commit']==PREVIOUS_COMMIT
        assert set(manifest['sha256'])==PREVIOUS_FILES
        owner=self.proof/'previous-owner'
        assert {str(path.relative_to(owner)) for path in owner.rglob('*') if path.is_file()}==PREVIOUS_FILES
        for name,digest in manifest['sha256'].items():
            data=(self.proof/'previous-owner'/name).read_bytes()
            assert hashlib.sha256(data).hexdigest()==digest
            assert data==subprocess.run(['git','show',manifest['commit']+':services/access/identity-migrations/'+name],cwd=ROOT,capture_output=True,check=True,timeout=10).stdout
        executions=json.loads((self.proof/'previous-execution.json').read_text())
        assert len(executions)==3
        assert {row['case'] for row in executions}=={'previous','failure','unknown'}
        expected_command=[str(PREVIOUS_PYTHON),'-I','-B','-c',PREVIOUS_LAUNCHER,str(owner),str(ROOT)]
        for row in executions:
            assert row['command']==expected_command
            assert row['log_sha256']==hashlib.sha256((self.proof/('previous-'+row['case']+'.log')).read_bytes()).hexdigest()
        assert all(row['exit_code']==0 and row['commit']==manifest['commit'] and row['head']=='identity_0002' for row in executions)
        for case in ['previous','failure','unknown']:
            assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0002',)]
        self.passed('previous-head2-source-and-execution-evidence',commit=manifest['commit'])

    def snapshot(self,case):
        db=engine(self.private['owner_urls'][case])
        try:
            with db.connect() as connection:
                return baseline.projection_catalog_snapshot(connection)
        finally:db.dispose()

    def admin(self,case):
        parsed=urlsplit(self.private['databases'][case])
        return engine(urlunsplit(parsed._replace(netloc='supabase_admin:'+quote(parsed.password or '',safe='')+'@'+parsed.hostname+':'+str(parsed.port))))

    def profiles(self):
        accounts=[str(uuid.uuid4()) for _ in range(4)]
        system=str(uuid.uuid4());actors=[str(uuid.uuid4()) for _ in range(3)]
        insert="INSERT INTO identity.actor(id,kind,display_name,created_by,updated_by) VALUES (:id,:kind,:label,:executor,:executor)"
        self.sql('clean',insert,{'id':system,'kind':'system','label':'Synthetic projection executor','executor':system})
        for index,account in enumerate(accounts):
            self.sql('clean','INSERT INTO auth.users(id,email) VALUES (:id,:email)',{'id':account,'email':'synthetic-'+account+'@example.invalid'},role='databases')
            if index<3:
                self.sql('clean',insert,{'id':actors[index],'kind':'account','label':'Synthetic actor '+str(index),'executor':system})
                self.sql('clean',"INSERT INTO identity.account_actor(account_id,actor_id,actor_kind,created_by) VALUES (:account,:actor,'account',:executor)",{'account':account,'actor':actors[index],'executor':system})
        self.sql('clean','UPDATE identity.users SET deleted_at=now() WHERE id=:id',{'id':accounts[2]})
        assert self.sql('clean','SELECT count(*) FROM identity.org')==[(0,)]
        return accounts,actors,system

    def reads(self):
        accounts,actors,system=self.profiles();before=self.data_state('clean')
        db=engine(self.private['runtime_urls']['clean'])
        try:
            with db.connect() as connection:
                assert connection.execute(text('SELECT session_user,current_user')).one()==('access_runtime','access_runtime');connection.commit()
                def query(kind=None,account=None,actor=None,org=None):
                    with connection.begin():
                        for key,value in [('app.context_kind',kind),('app.account_id',account),('app.actor_id',actor),('app.org_id',org)]:
                            if value is not None:connection.execute(text('SELECT set_config(:key,:value,true)'),{'key':key,'value':value})
                        return [tuple(row) for row in connection.execute(text('SELECT account_id::text,actor_id::text,display_name FROM identity.current_account_actor()'))]
                assert query()==[]
                assert query('user',accounts[0],actors[1],str(uuid.uuid4()))==[(accounts[0],actors[0],'Synthetic actor 0')]
                assert query()==[]  # same physical connection, transaction-local cleanup
                # Reuse this physical connection after explicit rollback and after
                # a failed statement, not only successful context-manager commits.
                for fail_statement in (False, True):
                    transaction=connection.begin()
                    try:
                        connection.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true)"),{'account':accounts[0]})
                        assert connection.execute(text('SELECT account_id::text FROM identity.current_account_actor()')).scalars().all()==[accounts[0]]
                        if fail_statement:
                            try:connection.execute(text('SELECT 1/0'))
                            except Exception as error:assert getattr(getattr(error,'orig',error),'sqlstate',None)=='22012'
                            else:raise AssertionError('expected_statement_failure_missing')
                    finally:transaction.rollback()
                    assert query()==[]
                assert query('user',accounts[1])==[(accounts[1],actors[1],'Synthetic actor 1')]
                assert query('user',accounts[3])==[(accounts[3],None,None)]
                assert query('user',accounts[2])==[]
                assert query('user',str(uuid.uuid4()))==[]
                assert query('user',accounts[0].upper())==[(accounts[0],actors[0],'Synthetic actor 0')]
                for kind,account in [(None,accounts[0]),('setup',accounts[0]),('',accounts[0]),('user',None),('user',''),('user','bad-uuid'),('user','00000000-0000-0000-0000-000000000000')]:
                    assert query(kind,account)==[]
                for statement in ['SELECT * FROM identity.actor','SELECT * FROM identity.account_actor','SELECT * FROM identity.users',"UPDATE identity.users SET is_platform_admin=true","INSERT INTO identity.actor DEFAULT VALUES","SET ROLE identity_account_projection_owner", "CREATE OR REPLACE FUNCTION identity.current_account_actor() RETURNS TABLE(account_id uuid,actor_id uuid,display_name text) LANGUAGE sql AS 'SELECT NULL::uuid,NULL::uuid,NULL::text'"]:
                    with connection.begin():
                        savepoint=connection.begin_nested()
                        try:connection.execute(text(statement))
                        except Exception as error:assert getattr(getattr(error,'orig',error),'sqlstate',None)=='42501'
                        else:raise AssertionError('projection_runtime_authority_broadened')
                        finally:savepoint.rollback()
                # The caller's path/temp objects cannot replace qualified owner data.
                with connection.begin():
                    connection.execute(text('CREATE TEMP TABLE users(id uuid,deleted_at timestamptz); CREATE TEMP TABLE actor(id uuid,kind text,display_name text); CREATE TEMP TABLE account_actor(account_id uuid,actor_id uuid,actor_kind text)'))
                    connection.execute(text("INSERT INTO users VALUES (:account,NULL)"),{'account':accounts[0]})
                    connection.execute(text("INSERT INTO actor VALUES (:actor,'account','Forged label')"),{'actor':actors[1]})
                    connection.execute(text("INSERT INTO account_actor VALUES (:account,:actor,'account')"),{'account':accounts[0],'actor':actors[1]})
                    connection.execute(text('SET LOCAL search_path=pg_temp,public,identity'))
                    connection.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true)"),{'account':accounts[0]})
                    assert [tuple(row) for row in connection.execute(text('SELECT account_id::text,actor_id::text,display_name FROM identity.current_account_actor()'))]==[(accounts[0],actors[0],'Synthetic actor 0')]
                assert query()==[]
        finally:db.dispose()
        assert self.data_state('clean')==before
        # The dedicated definer's profile SELECT is itself bounded by RLS, even with
        # legacy PUBLIC policies. Assume it only through the migration owner for proof.
        owner=engine(self.private['owner_urls']['clean'])
        try:
            with owner.connect() as connection:
                transaction=connection.begin()
                try:
                    connection.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true)"),{'account':accounts[0]})
                    connection.execute(text("SELECT set_config('request.jwt.claims',:claims,true)"),{'claims':json.dumps({'role':'service_role','sub':accounts[1]})})
                    connection.execute(text('SET LOCAL ROLE identity_account_projection_owner'))
                    assert connection.execute(text('SELECT id::text FROM identity.users')).scalars().all()==[accounts[0]]
                    savepoint=connection.begin_nested()
                    try:connection.execute(text('SELECT id FROM auth.users'))
                    except Exception as error:assert getattr(getattr(error,'orig',error),'sqlstate',None)=='42501'
                    else:raise AssertionError('projection_reader_auth_table_authority')
                    finally:savepoint.rollback()
                finally:transaction.rollback()
        finally:owner.dispose()
        for role in ['anon','authenticated','service_role','supabase_auth_admin']:
            assert self.sql('clean',"SELECT has_function_privilege(:role,'identity.current_account_actor()','EXECUTE')",{'role':role})==[(False,)]
        assert self.sql('clean',"SELECT pg_has_role('access_runtime','identity_account_projection_owner','MEMBER'),has_schema_privilege('identity_account_projection_owner','identity','CREATE'),has_schema_privilege('access_runtime','identity','CREATE')")==[(False,False,False)]
        self.passed('restricted-current-account-reads-and-denials',mapped=True,unmapped_nullable=True,deleted_and_invalid_empty=True,person_organization_required=False,connection_reuse=True,search_path_spoofing_rejected=True,reader_rls=True)

    def upgrades_and_failures(self):
        self.prior_evidence()
        self.command('projection-clean','clean');self.reads();self.command('projection-repeat','clean')
        self.legacy('legacy');self.original_ledger('legacy');ids=self.row_fixtures('legacy')
        before,external=self.data_state('legacy'),self.external_state('legacy')
        self.command('projection-legacy-adopt','legacy',mode='adopt')
        after=self.data_state('legacy');assert all(after[key]==value for key,value in before.items() if key!='identity.alembic_version');assert self.external_state('legacy')==external;self.runtime('legacy',ids)
        previous_ids=self.row_fixtures('previous')
        source=ast.parse((self.proof/'previous-owner/versions/0001_baseline.py').read_text())
        integration=next(ast.literal_eval(node.value) for node in source.body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='LEGACY_INTEGRATION_SQL' for target in node.targets))
        self.sql('previous',integration);before,external=self.data_state('previous'),self.external_state('previous')
        self.command('projection-from-head2','previous');after=self.data_state('previous');assert all(after[key]==value for key,value in before.items() if key!='identity.alembic_version');assert self.external_state('previous')==external;self.runtime('previous',previous_ids)
        account=str(uuid.uuid4());self.sql('previous','INSERT INTO auth.users(id,email) VALUES (:id,:email)',{'id':account,'email':'synthetic-'+account+'@example.invalid'},role='databases');assert self.sql('previous','SELECT id::text FROM identity.users WHERE id=:id',{'id':account})==[(account,)]
        # Unsafe reader flags / runtime assumption are independently refused unchanged.
        admin=self.admin('unsafe')
        try:
            for label,unsafe,restore in [('bypass','ALTER ROLE identity_account_projection_owner BYPASSRLS','ALTER ROLE identity_account_projection_owner NOBYPASSRLS'),('runtime-member','GRANT identity_account_projection_owner TO access_runtime','REVOKE identity_account_projection_owner FROM access_runtime')]:
                with admin.begin() as c:c.execute(text(unsafe))
                before=self.data_state('unsafe')
                try:self.command('projection-unsafe-'+label,'unsafe',expected='identity_projection_role_unsafe');assert self.data_state('unsafe')==before
                finally:
                    with admin.begin() as c:c.execute(text(restore))
        finally:admin.dispose()
        # Inject failure after grants/policies are written, during routine creation.
        admin=self.admin('failure')
        try:
            with admin.begin() as c:c.execute(text("""CREATE FUNCTION public.synthetic_projection_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN IF EXISTS (SELECT 1 FROM pg_event_trigger_ddl_commands() WHERE object_identity='identity.current_account_actor()') THEN RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_projection_failure'; END IF; END $$; CREATE EVENT TRIGGER synthetic_projection_failure ON ddl_command_end WHEN TAG IN ('CREATE FUNCTION') EXECUTE FUNCTION public.synthetic_projection_failure();"""))
            before,catalog=self.data_state('failure'),self.snapshot('failure')
            self.command('projection-mid-write-rollback','failure',expected='identity_migration_failed_requires_reconciliation')
            assert self.data_state('failure')==before and self.snapshot('failure')==catalog
        finally:
            with admin.begin() as c:c.execute(text('DROP EVENT TRIGGER synthetic_projection_failure; DROP FUNCTION public.synthetic_projection_failure()'))
            admin.dispose()
        self.command('projection-failure-reconciled','failure')
        self.sql('unknown',"UPDATE identity.alembic_version SET version_num='identity_unknown'");before=self.data_state('unknown');self.command('projection-unknown-history','unknown',expected='identity_unknown_history');assert self.data_state('unknown')==before
        self.passed('projection-foundation-matrix',prior_consumer_compatible=True,rollback_verified=True,unsafe_role_refused=True)


def main():
    proof,private=fixture();ProjectionQualification(proof,private).upgrades_and_failures()


if __name__=='__main__':
    try:main()
    except Exception as error:
        print('projection_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None
