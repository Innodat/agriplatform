"""Synthetic ID-B persistence proof, reusing the existing Identity qualification owner.

No Docker lifecycle, provisioning command, runtime service or real-account adoption.
Prepare fresh explicit mappings through IDENTITY_QUALIFICATION_DIR first.
"""
import json
import ast
from urllib.parse import urlsplit, urlunsplit, quote
import os
from pathlib import Path
import subprocess
import sys
import uuid
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qualify_identity_baseline import Qualification, ROOT, baseline, engine, fixture, sha, text


PREVIOUS_COMMIT = 'e4723c5ca371df01779af3964d306d0fcd38bc0c'
PREVIOUS_FILES = ('identity_baseline.py', 'env.py', 'versions/0001_baseline.py',
                  'source-pins.json', 'reference.json')
PREVIOUS_LAUNCHER = """
import sys
from pathlib import Path
from alembic.config import Config
from alembic import command
owner = Path(sys.argv[1])
sys.path.insert(0, str(owner))
import identity_baseline
identity_baseline.ROOT = Path(sys.argv[2])
config = Config()
config.set_main_option('script_location', str(owner))
config.set_main_option('prepend_sys_path', str(owner))
command.upgrade(config, 'head')
"""


class ActorQualification(Qualification):
    def record(self, label, **facts):
        self.records.append({'label': label, 'status': 'passed', **facts})
        self.persist()
        print(label, 'PASS', flush=True)

    def previous_sources(self):
        owner = self.proof/'previous-owner'
        assert {path.relative_to(owner).as_posix() for path in owner.rglob('*') if path.is_file()} == set(PREVIOUS_FILES)
        hashes = {}
        for path in PREVIOUS_FILES:
            committed = subprocess.run(
                ['git', 'show', PREVIOUS_COMMIT+':services/access/identity-migrations/'+path],
                cwd=ROOT, capture_output=True, check=True, timeout=10).stdout
            assert (owner/path).read_bytes() == committed, 'previous_source_not_exact_committed_release'
            hashes[path] = sha(committed)
        return hashes

    def previous_upgrade(self, case):
        # Pin every executable owner source/reference to the actual prior commit,
        # never to a private self-supplied manifest or private launcher.
        hashes = self.previous_sources()
        env = {'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8',
               'IDENTITY_MIGRATION_DATABASE_URL':self.private['owner_urls'][case].replace('postgresql://','postgresql+psycopg://',1)}
        result = subprocess.run([sys.executable,'-I','-B','-c',PREVIOUS_LAUNCHER,
                                 str(self.proof/'previous-owner'),str(ROOT)],
                                cwd=ROOT,env=env,capture_output=True,timeout=90)
        log = result.stdout+result.stderr
        output = self.proof/('previous-'+case+'.log')
        with output.open('xb') as handle:
            output.chmod(0o600)
            handle.write(log)
        assert result.returncode == 0
        self.record('previous-code-upgrade-'+case, revision=PREVIOUS_COMMIT,
                    source_sha256=hashes, launcher_sha256=sha(PREVIOUS_LAUNCHER.encode()),
                    log_sha256=sha(log))

    def refused(self, statement, values=None, state='23514'):
        db = engine(self.private['owner_urls']['clean'])
        try:
            with db.connect() as connection:
                transaction = connection.begin()
                try:
                    connection.execute(text(statement),values or {})
                except Exception as error:
                    assert getattr(getattr(error,'orig',error),'sqlstate',None) == state
                else:
                    raise AssertionError('actor_invalid_mutation_accepted')
                finally:
                    transaction.rollback()
        finally:
            db.dispose()

    def structure(self):
        system, account_actor, service, account = [str(uuid.uuid4()) for _ in range(4)]
        suffix=str(uuid.uuid4())
        # Controlled synthetic attribution; no automatic legacy classification.
        insert = "INSERT INTO identity.actor(id,kind,display_name,actor_key,created_by,updated_by) VALUES (:id,:kind,:label,:key,:executor,:executor)"
        self.sql('clean',insert,{'id':system,'kind':'system','label':'Synthetic System','key':'synthetic.system.'+suffix,'executor':system})
        self.sql('clean',insert,{'id':account_actor,'kind':'account','label':'Synthetic account actor','key':None,'executor':system})
        self.sql('clean',insert,{'id':service,'kind':'service','label':'Synthetic worker','key':'synthetic.worker.'+suffix,'executor':system})
        # Caller metadata is not server attribution, even for direct owner fixtures.
        server_before = self.sql('clean', 'SELECT clock_timestamp()')[0][0]
        spoofed = str(uuid.uuid4())
        self.sql('clean', """INSERT INTO identity.actor
            (id,kind,display_name,created_by,updated_by,created_at,updated_at)
            VALUES (:id,'system','Synthetic metadata override',:creator,:other,'2000-01-01','2001-01-01')""",
            {'id':spoofed,'creator':system,'other':service})
        assert self.sql('clean', """SELECT created_by::text,updated_by::text,
            created_at=updated_at,created_at>=:before AND created_at<=statement_timestamp()
            FROM identity.actor WHERE id=:id""", {'id':spoofed,'before':server_before}) == [(system,system,True,True)]
        unmapped_account_actor = str(uuid.uuid4())
        self.sql('clean',insert,{'id':unmapped_account_actor,'kind':'account','label':'Unmapped account actor','key':None,'executor':system})
        boundary_actor = str(uuid.uuid4())
        self.sql('clean',insert,{'id':boundary_actor,'kind':'system','label':'漢'*200,
                                'key':'a'*128,'executor':system})
        assert self.sql('clean', 'SELECT char_length(display_name),octet_length(display_name),char_length(actor_key) FROM identity.actor WHERE id=:id',
                        {'id':boundary_actor}) == [(200,600,128)]
        mapping="INSERT INTO identity.account_actor(account_id,actor_id,actor_kind,created_by,created_at) VALUES (:account,:actor,'account',:executor,'2000-01-01')"
        self.sql('clean',mapping,{'account':account,'actor':account_actor,'executor':system})
        assert self.sql('clean', 'SELECT created_by::text,created_at>=:before AND created_at<=statement_timestamp() FROM identity.account_actor WHERE account_id=:account',
                        {'account':account,'before':server_before}) == [(system,True)]
        assert self.sql('clean','SELECT count(*) FROM auth.users',role='databases') == [(0,)]
        assert self.sql('clean','SELECT count(*) FROM identity.org') == [(0,)]
        before = self.data_state('clean')
        self.refused(insert,{'id':str(uuid.uuid4()),'kind':'other','label':'Invalid','key':None,'executor':system})
        self.refused(insert,{'id':'00000000-0000-0000-0000-000000000000','kind':'system','label':'Invalid','key':None,'executor':system})
        for label,key in [('   ',None),('\u00a0',None),('\u2003',None),('\t\u00a0\u2003\u3000\n',None),('漢'*201,None),('Invalid','Uppercase'),('Invalid','x'*129),('Invalid','álpha')]:
            self.refused(insert,{'id':str(uuid.uuid4()),'kind':'system','label':label,'key':key,'executor':system})
        self.refused(insert,{'id':str(uuid.uuid4()),'kind':'system','label':'Duplicate key',
                             'key':'a'*128,'executor':system},state='23505')
        absent_actor = str(uuid.uuid4())
        self.refused(insert,{'id':str(uuid.uuid4()),'kind':'system','label':'Absent creator',
                             'key':None,'executor':absent_actor},state='23503')
        self.refused("UPDATE identity.actor SET display_name='Missing updater',updated_by=:executor WHERE id=:id",
                     {'id':account_actor,'executor':absent_actor},state='23503')
        self.refused(mapping,{'account':str(uuid.uuid4()),'actor':unmapped_account_actor,'executor':absent_actor},state='23503')
        self.refused(mapping,{'account':str(uuid.uuid4()),'actor':absent_actor,'executor':system},state='23503')
        self.refused(mapping,{'account':str(uuid.uuid4()),'actor':service,'executor':system},state='23503')
        self.refused(mapping,{'account':'00000000-0000-0000-0000-000000000000','actor':account_actor,'executor':system})
        self.refused(mapping,{'account':str(uuid.uuid4()),'actor':account_actor,'executor':system},state='23505')
        self.refused(mapping,{'account':account,'actor':account_actor,'executor':system},state='23505')
        for field,value in [('id',str(uuid.uuid4())),('kind','service'),('actor_key','replacement'),('created_by',service),('created_at','2000-01-01T00:00:00Z')]:
            self.refused('UPDATE identity.actor SET '+field+'=:value WHERE id=:id',{'value':value,'id':system})
        self.refused('DELETE FROM identity.actor WHERE id=:id',{'id':service})
        self.refused('TRUNCATE identity.actor,identity.account_actor')
        self.refused('TRUNCATE identity.account_actor')
        self.refused('DELETE FROM identity.account_actor WHERE account_id=:id',{'id':account})
        self.refused('UPDATE identity.account_actor SET actor_id=:actor WHERE account_id=:id',{'actor':service,'id':account})
        assert self.data_state('clean') == before
        self.sql('clean',"UPDATE identity.actor SET actor_key=:key,display_name='Renamed synthetic actor',updated_by=:executor,updated_at='2000-01-01' WHERE id=:id",{'key':'synthetic.account.'+suffix,'executor':system,'id':account_actor})
        assert self.sql('clean',"SELECT display_name,updated_at>'2026-01-01'::timestamptz,created_by::text,updated_by::text FROM identity.actor WHERE id=:id",{'id':account_actor}) == [('Renamed synthetic actor',True,system,system)]
        self.refused("UPDATE identity.actor SET actor_key='another.key' WHERE id=:id",{'id':account_actor})
        renamed_state = self.data_state('clean')
        self.sql('clean', "UPDATE identity.actor SET updated_by=:other,updated_at='2000-01-01' WHERE id=:id",
                 {'id':account_actor,'other':service})
        assert self.data_state('clean') == renamed_state
        assert self.sql('clean', "SELECT count(*) FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_class target ON target.oid=k.confrelid JOIN pg_namespace n ON n.oid=target.relnamespace WHERE c.oid IN ('identity.actor'::regclass,'identity.account_actor'::regclass) AND k.contype='f' AND n.nspname<>'identity'") == [(0,)]
        # Actor existence has no effect on the old scoped runtime projection.
        assert self.sql('clean','SELECT id FROM identity.org',role='runtime_urls') == []
        for role in ['anon','authenticated','service_role','supabase_auth_admin','access_runtime']:
            for table in ['actor','account_actor']:
                assert self.sql('clean',"SELECT has_table_privilege(:role,'identity."+table+"','SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')",{'role':role}) == [(False,)]
        for role in ['anon','authenticated','service_role','supabase_auth_admin','access_runtime']:
            for function in ['guard_actor','guard_account_actor']:
                assert self.sql('clean',"SELECT has_function_privilege(:role,'identity."+function+"()','EXECUTE')",{'role':role}) == [(False,)]
        db = engine(self.private['runtime_urls']['clean'])
        try:
            for statement in ['SELECT * FROM identity.actor','SELECT * FROM identity.account_actor',"INSERT INTO identity.actor DEFAULT VALUES"]:
                with db.connect() as connection:
                    transaction = connection.begin()
                    try:
                        connection.execute(text(statement))
                    except Exception as error:
                        assert getattr(getattr(error,'orig',error),'sqlstate',None) == '42501'
                    else:
                        raise AssertionError('runtime_actor_authority_exposed')
                    finally:
                        transaction.rollback()
        finally:
            db.dispose()
        self.record('actor-mapping-structure-retention-attribution-and-runtime-denial', accounts_created=0, organizations_created=0)
        self.mapping_contention(system)
        self.command('populated-actor-repeat','clean')

    def mapping_contention(self, executor):
        actors = [str(uuid.uuid4()), str(uuid.uuid4())]
        account = str(uuid.uuid4())
        for actor in actors:
            self.sql('clean', "INSERT INTO identity.actor(id,kind,display_name,created_by,updated_by) VALUES (:id,'account','Synthetic contended actor',:executor,:executor)",
                     {'id':actor,'executor':executor})
        statement = text("INSERT INTO identity.account_actor(account_id,actor_id,actor_kind,created_by) VALUES (:account,:actor,'account',:executor)")
        db = engine(self.private['owner_urls']['clean'])
        ready, finished = threading.Event(), threading.Event()
        loser = {}
        def competing_insert():
            try:
                with db.connect() as connection:
                    transaction = connection.begin()
                    try:
                        connection.exec_driver_sql("SET LOCAL lock_timeout='5s'")
                        connection.exec_driver_sql("SET LOCAL statement_timeout='8s'")
                        loser['pid'] = connection.execute(text('SELECT pg_backend_pid()')).scalar_one()
                        ready.set()
                        connection.execute(statement, {'account':account,'actor':actors[1],'executor':executor})
                        loser['state'] = 'unexpected_success'
                    except Exception as error:
                        loser['state'] = getattr(getattr(error,'orig',error),'sqlstate',None)
                    finally:
                        transaction.rollback()
            except Exception:
                # Never emit connection exceptions or payloads from a worker thread.
                loser['state'] = 'connection_failed'
            finally:
                finished.set()
        thread = threading.Thread(target=competing_insert, daemon=True)
        try:
            with db.connect() as winner:
                transaction = winner.begin()
                try:
                    winner.exec_driver_sql("SET LOCAL statement_timeout='8s'")
                    winner_pid = winner.execute(text('SELECT pg_backend_pid()')).scalar_one()
                    winner.execute(statement, {'account':account,'actor':actors[0],'executor':executor})
                    thread.start()
                    assert ready.wait(3), 'mapping_contender_not_ready'
                    deadline = time.monotonic()+3
                    blocked = False
                    while time.monotonic() < deadline and not finished.is_set():
                        blockers = winner.execute(text('SELECT pg_blocking_pids(:pid)'), {'pid':loser['pid']}).scalar_one()
                        if winner_pid in blockers:
                            blocked = True
                            break
                        time.sleep(0.02)
                    assert blocked and not finished.is_set(), 'mapping_contender_did_not_block'
                    transaction.commit()
                finally:
                    if transaction.is_active:
                        transaction.rollback()
            assert finished.wait(6), 'mapping_contender_did_not_finish'
            thread.join(timeout=1)
            assert loser['state'] == '23505', 'mapping_contender_not_unique_conflict'
            assert self.sql('clean', 'SELECT actor_id::text FROM identity.account_actor WHERE account_id=:account',
                            {'account':account}) == [(actors[0],)]
            assert self.sql('clean', 'SELECT count(*) FROM identity.account_actor WHERE actor_id=:actor',
                            {'actor':actors[1]}) == [(0,)]
        finally:
            if thread.ident is not None:
                thread.join(timeout=6)
            db.dispose()
        self.record('actor-account-mapping-contention', contenders=2, loser_sqlstate='23505',
                    blocked_until_winner_commit=True, winning_mapping_preserved=True)

    def verify_actors(self):
        self.command('actor-clean','clean')
        self.command('actor-clean-repeat','clean')
        self.structure()
        self.verify_compatibility()

    def verify_compatibility(self):
        self.legacy('legacy')
        ids = self.row_fixtures('legacy')
        self.original_ledger('legacy')
        before,external=self.data_state('legacy'),self.external_state('legacy')
        self.command('actor-legacy-adopt','legacy',mode='adopt')
        after=self.data_state('legacy')
        assert all(after[k]==v for k,v in before.items() if k!='identity.alembic_version')
        assert self.external_state('legacy')==external
        self.runtime('legacy',ids)
        # Auth-owned profile hook still creates account profiles on its original path.
        new_account=str(uuid.uuid4())
        self.sql('legacy','INSERT INTO auth.users(id,email) VALUES (:id,:email)',{'id':new_account,'email':'synthetic-'+new_account+'@example.invalid'},role='databases')
        assert self.sql('legacy','SELECT id::text FROM identity.users WHERE id=:id',{'id':new_account})==[(new_account,)]
        self.previous_upgrade('previous')
        old_ids=self.row_fixtures('previous')
        # The legacy fixture temporarily revokes postgres FK/schema privileges.
        # Restore the exact original revision1 integration before testing upgrade.
        previous_tree=ast.parse((self.proof/'previous-owner/versions/0001_baseline.py').read_text())
        integration=next(ast.literal_eval(node.value) for node in previous_tree.body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='LEGACY_INTEGRATION_SQL' for target in node.targets))
        self.sql('previous',integration)
        before,external=self.data_state('previous'),self.external_state('previous')
        self.command('actor-from-previous-head','previous')
        after=self.data_state('previous')
        assert all(after[k]==v for k,v in before.items() if k!='identity.alembic_version')
        assert self.external_state('previous')==external
        self.runtime('previous',old_ids)
        self.command('actor-previous-repeat','previous')
        # Unknown catalog/revision and post-write failure preserve the old head.
        self.previous_upgrade('failure')
        parsed=urlsplit(self.private['databases']['failure'])
        admin_url=urlunsplit(parsed._replace(netloc='supabase_admin:'+quote(parsed.password or '',safe='')+'@'+parsed.hostname+':'+str(parsed.port)))
        admin=engine(admin_url)
        try:
            with admin.begin() as connection:
                connection.execute(text("""CREATE FUNCTION public.synthetic_actor_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN
                  IF EXISTS (SELECT 1 FROM pg_event_trigger_ddl_commands() WHERE object_identity='identity.account_actor') THEN
                    RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_actor_failure';
                  END IF;
                END $$;
                CREATE EVENT TRIGGER synthetic_actor_failure ON ddl_command_end WHEN TAG IN ('CREATE TABLE') EXECUTE FUNCTION public.synthetic_actor_failure();"""))
            before,catalog=self.data_state('failure'),self.snapshot('failure')
            self.command('actor-mid-write-rollback','failure',expected='identity_migration_failed_requires_reconciliation')
            assert self.data_state('failure')==before and self.snapshot('failure')==catalog
        finally:
            with admin.begin() as connection:
                connection.execute(text('DROP EVENT TRIGGER synthetic_actor_failure; DROP FUNCTION public.synthetic_actor_failure()'))
            admin.dispose()
        self.command('actor-failure-reconciled','failure')
        # A corrupted current catalog refuses before any ledger or data change.
        self.sql('failure','GRANT SELECT ON identity.actor TO anon')
        before,catalog=self.data_state('failure'),self.snapshot('failure')
        self.command('actor-unknown-catalog-refuse','failure',expected='identity_catalog_mismatch')
        assert self.data_state('failure')==before and self.snapshot('failure')==catalog
        self.previous_upgrade('unknown')
        self.sql('unknown',"UPDATE identity.alembic_version SET version_num='identity_unknown'")
        before=self.data_state('unknown')
        self.command('actor-unknown-revision-refuse','unknown',expected='identity_unknown_history')
        assert self.data_state('unknown')==before
        self.record('actor-foundation-matrix', legacy_rows_and_external_refs_preserved=True, restricted_logins=True)


def main():
    proof,private=fixture()
    runner=ActorQualification(proof,private)
    runner.verify_actors()


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        print('actor_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None
