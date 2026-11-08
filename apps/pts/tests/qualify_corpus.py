"""Fresh isolated PostgreSQL17 adoption/recovery qualification; no retained fixture writes."""
import argparse
from concurrent.futures import ThreadPoolExecutor,TimeoutError as FutureTimeout
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
from uuid import uuid4
from unittest.mock import patch
from contextlib import contextmanager,nullcontext
import psycopg
from psycopg import sql
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from apps.pts.backend.db import engine,scoped,corpus,load
from apps.pts.backend.main import Repository
from apps.pts.tools.import_library import import_library
from apps.pts.tools.bind_corpus import inventory,bind
ROOT=Path(__file__).resolve().parents[3]
ORG='11111111-1111-4111-8111-111111111111'
OTHER='22222222-2222-4222-8222-222222222222'
ACTOR='33333333-3333-4333-8333-333333333333'


def qualify(output,bypass_binding_gate=False):
    os.umask(0o077);output=output.resolve()
    if not output.is_relative_to(ROOT/'platform/deployment/.local/e1-pts-adoption') or output.exists():raise ValueError('new_private_output_required')
    output.mkdir(parents=True,mode=0o700);nonce=uuid4().hex;container='e1-pts-corpus-'+nonce[:16];password=secrets.token_urlsafe(36)
    envfile=output/'postgres.env';envfile.write_text('POSTGRES_PASSWORD='+password+'\n');envfile.chmod(0o600)
    def docker(*args):return subprocess.check_output(['docker',*args],stderr=subprocess.DEVNULL,text=True,timeout=30).strip()
    image=json.loads(docker('image','inspect','postgres:17'))[0]
    identity=docker('run','-d','--name',container,'--label','agriplatform.pts-corpus='+nonce,'--network','bridge','--restart','no','--log-driver','none','--env-file',str(envfile),'-p','127.0.0.1::5432',image['Id'])
    frame=json.loads(docker('inspect',container))[0];port=frame['NetworkSettings']['Ports']['5432/tcp'][0]['HostPort']
    assert frame['Id']==identity and frame['HostConfig']['RestartPolicy']['Name']=='no'
    admin=f'postgresql+psycopg://postgres:{password}@127.0.0.1:{port}/postgres'
    (output/'private.json').write_text(json.dumps({'container':container,'container_id':identity,'image_id':image['Id'],'admin':admin,'nonce':nonce},indent=2)+'\n')
    urls={role:admin.replace('postgres:',role+':',1) for role in ('pts_migrator','pts_runtime','pts_import','pts_account_runtime','pts_corpus_import')}
    def connect(url=admin):return psycopg.connect(url.replace('postgresql+psycopg:','postgresql:'))
    checks=[];stopped=False
    try:
        for _ in range(100):
            try:
                with connect():break
            except psycopg.OperationalError:time.sleep(.1)
        else:raise AssertionError('fresh_postgres_not_ready')
        with connect() as conn:
            for role in ('pts_migrator','pts_runtime','pts_import','pts_account_runtime','pts_corpus_import'):
                conn.execute(sql.SQL('CREATE ROLE {} LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD {}').format(sql.Identifier(role),sql.Literal(password)))
            conn.execute('CREATE SCHEMA pts AUTHORIZATION pts_migrator;REVOKE ALL ON SCHEMA pts FROM PUBLIC;GRANT USAGE ON SCHEMA pts TO pts_runtime,pts_import,pts_account_runtime,pts_corpus_import')
        def upgrade(revision='head',expected=0):
            result=subprocess.run([sys.executable,'-B','-m','alembic','-c','apps/pts/alembic.ini','upgrade',revision],cwd=ROOT,env={**os.environ,'PTS_MIGRATION_DATABASE_URL':urls['pts_migrator']},capture_output=True,timeout=30)
            if result.returncode!=expected:
                (output/('migration-unexpected-'+uuid4().hex+'.log')).write_bytes(result.stdout+result.stderr)
                raise AssertionError('migration_result_unexpected')
        upgrade('pts_0001');legacy=engine(urls['pts_import']);old=engine(urls['pts_runtime']);owner=engine(urls['pts_migrator']);reader=engine(urls['pts_account_runtime']);importer=engine(urls['pts_corpus_import'])
        library=json.loads((ROOT/'apps/pts/reference/poetry-library/library.json').read_text())
        for partition in (ORG,OTHER):
            with scoped(legacy,partition,'service:pts-import') as conn:
                import_library(conn,library)
                conn.execute(text("INSERT INTO pts.attachments(org_id,id,document_id,content_id) VALUES(:org,'DOC-VELTEN','DOC-VELTEN',:content)"),{'org':partition,'content':str(uuid4())})
        before={}
        for partition in (ORG,OTHER):
            with scoped(owner,partition,ACTOR) as conn:before[partition]=inventory(conn)
        try:Repository(reader).read(ACTOR)
        except DBAPIError:checks.append('native-successor-missing-binding-table-RED')
        else:raise AssertionError('native_RED_missing')
        # Missing controlled prerequisite causes real transactional migration failure.
        with connect() as conn:conn.execute('ALTER ROLE pts_corpus_import RENAME TO fixture_missing_pts_importer')
        try:upgrade(expected=1)
        finally:
            with connect() as conn:conn.execute('ALTER ROLE fixture_missing_pts_importer RENAME TO pts_corpus_import')
        with connect() as conn:
            assert conn.execute('SELECT version_num FROM pts.alembic_version').fetchall()==[('pts_0001',)]
            assert conn.execute("SELECT to_regclass('pts.corpus_binding')").fetchone()==(None,)
        checks.append('failed-upgrade-rollback-keeps-predecessor-and-blocks-activation')
        upgrade('pts_0002')
        from datetime import datetime,timezone,timedelta
        from apps.pts.backend.db import file_scope
        predecessor_session={'account_id':ACTOR,'session_id':str(uuid4()),'expires_at':datetime.now(timezone.utc)+timedelta(hours=1)}
        predecessor_context=uuid4()
        # Previous native consumer's exact-session INSERT/read is supported on
        # 0002 and remains valid after the additive expiry function migration.
        with file_scope(reader,ACTOR,predecessor_session['session_id'],ACTOR) as conn:
            conn.execute(text("INSERT INTO pts.file_contexts(id,account_id,session_id,document_id,presentation,expires_at) VALUES(:id,:account,:session,'DOC-VELTEN','open',:expires)"),
                {'id':predecessor_context,'account':ACTOR,'session':predecessor_session['session_id'],'expires':predecessor_session['expires_at']})
        assert Repository(reader).file_context(predecessor_session,predecessor_context)
        upgrade();upgrade()
        assert Repository(reader).file_context(predecessor_session,predecessor_context)
        checks.append('ordinary-upgrade-repeat-and-0002-live-context-predecessor-compatibility')
        # Native exclusive-lock acceptance: the existing ten-second query budget
        # must cover the FIRST binding lookup, and return the pooled connection.
        with connect() as blocker:
            blocker.execute('LOCK TABLE pts.corpus_binding IN ACCESS EXCLUSIVE MODE')
            with ThreadPoolExecutor(max_workers=1) as executor:
                started=time.monotonic();waiting=executor.submit(Repository(reader).read,ACTOR)
                try:
                    try:waiting.result(timeout=11.5)
                    except FutureTimeout:raise AssertionError('binding_lookup_exceeded_existing_query_budget') from None
                    except DBAPIError as error:
                        assert error.orig.sqlstate=='57014','binding_wait_failed_for_wrong_reason'
                        assert 9<=time.monotonic()-started<11.5
                    else:raise AssertionError('binding_lookup_did_not_wait_for_native_exclusive_lock')
                finally:blocker.rollback()
        assert reader.pool.checkedout()==0,'timed_out_binding_connection_not_released'
        checks.append('native-exclusive-binding-lock-bounded-by-existing-query-timeout-and-pool-release')
        try:Repository(reader).read(ACTOR)
        except Exception as error:assert getattr(error,'status_code',None)==503
        else:raise AssertionError('unverified_binding_not_unavailable')
        document={'schema_version':1,'executor_actor_id':ACTOR,'legacy_partition_id':ORG,'inventory_sha256':'a'*64,'release_reference':'isolated-synthetic-'+nonce,**before[ORG]}
        # Execute the production adapter's PtS stage, actual Alembic and native
        # binding queries. The other owners and production host validation have
        # independent fixtures; this explicitly isolates only this owner stage.
        import importlib.util
        spec=importlib.util.spec_from_file_location('pts_native_deployment_adapter',ROOT/'apps/pts/deployment/migrate.py')
        adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
        @contextmanager
        def native_lock():
            with connect(urls['pts_migrator']) as conn:
                conn.execute("SET lock_timeout='1000ms'")
                conn.execute("SELECT pg_advisory_xact_lock(hashtextextended('pts-native-release-fixture',0))")
                yield
        def native_inspect(selected):
            assert selected=='pts'
            with connect(urls['pts_migrator']) as conn:return [row[0] for row in conn.execute('SELECT version_num FROM pts.alembic_version ORDER BY version_num')]
        def native_target(value,project,role):
            assert value==urls['pts_migrator'] and project=='https://synthetic.supabase.co' and role=='pts_migrator'
        def actual_migration(command,**kwargs):
            result=subprocess.run(command,cwd=ROOT,**kwargs)
            assert result.returncode==0
            return result
        environment={'SUPABASE_URL':'https://synthetic.supabase.co','PTS_MIGRATION_DATABASE_URL':urls['pts_migrator']}
        with patch.object(adapter,'OWNERS',[('pts','apps/pts')]),patch.object(adapter,'database_url',side_effect=native_target):
            mutation=patch.object(adapter,'corpus_ready',return_value={}) if bypass_binding_gate else nullcontext()
            with mutation:
                try:adapter.main(output/'adapter-unbound.json',run=actual_migration,acquire_lock=native_lock,inspect=native_inspect,environ=dict(environment))
                except SystemExit as error:assert error.code==1
                else:raise AssertionError('actual_adapter_reported_complete_without_verified_corpus_binding')
            failed=json.loads((output/'adapter-unbound.json').read_text())
            assert failed['complete'] is False and failed['owners']['pts']['status']=='failed'
            assert failed['owners']['pts']['before']==failed['owners']['pts']['after']==native_inspect('pts')
            adapter.main(output/'adapter-reviewed.json',run=actual_migration,acquire_lock=native_lock,inspect=native_inspect,
                environ={**environment,'PTS_CORPUS_ADOPTION_INPUT_JSON':json.dumps(document)})
            succeeded=json.loads((output/'adapter-reviewed.json').read_text())
            assert succeeded['complete'] is True and succeeded['owners']['pts']['status']=='succeeded'
            assert succeeded['owners']['pts']['corpus_binding']=={key:document[key] for key in ('inventory_sha256','release_reference')}
        assert bind(owner,document)=={'status':'unchanged'}
        checks.append('actual-deployment-PtS-stage-native-migration-missing-binding-failure-and-reviewed-binding-evidence')
        try:bind(owner,{**document,'legacy_partition_id':OTHER,**before[OTHER]})
        except ValueError:pass
        else:raise AssertionError('binding_replacement_not_refused')
        for partition in (ORG,OTHER):
            with scoped(owner,partition,ACTOR) as conn:assert inventory(conn)==before[partition]
        checks.append('reviewed-singleton-binding-with-exact-payload-order-history-association-attribution-preservation')
        for forged in (ORG,OTHER,str(uuid4())):
            with scoped(reader,forged,ACTOR) as conn:
                assert load(conn)==library
                assert conn.execute(text('SELECT DISTINCT org_id FROM pts.poems')).scalars().all()==[__import__('uuid').UUID(ORG)]
        for partition in (ORG,OTHER):
            with scoped(old,partition,ACTOR) as conn:assert load(conn)==library
        assert Repository(reader).read(ACTOR)==library
        checks.append('actual-new-role-binding-isolation-forged-GUC-and-predecessor-partition-compatibility')
        for statement in ('CREATE TABLE pts.forbidden(id int)','SELECT * FROM pts.alembic_version','SELECT * FROM auth.users','SET ROLE pts_migrator','SET ROLE pts_runtime','UPDATE pts.poems SET ordinal=0','DELETE FROM pts.corpus_binding'):
            try:
                with reader.begin() as conn:conn.execute(text(statement))
            except DBAPIError:pass
            else:raise AssertionError('restricted_login_permitted_forbidden_operation')
        try:
            with corpus(importer,ACTOR) as conn:conn.execute(text("INSERT INTO pts.poems(org_id,id,payload,ordinal) VALUES(:org,'FOREIGN','{}',0)"),{'org':OTHER})
        except DBAPIError:pass
        else:raise AssertionError('importer_foreign_insert_not_refused')
        checks.append('restricted-successor-native-DDL-ledger-Auth-role-escalation-write-and-cross-partition-denials')
        with corpus(importer,ACTOR) as conn:
            assert import_library(conn,library)['replayed']
        changed=json.loads(json.dumps(library));changed['poems'][0]['text']='reviewed incoming conflict'
        def run_import(index):
            with corpus(importer,ACTOR) as conn:
                conn.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(current_setting('app.org_id'),0))"))
                return import_library(conn,changed)
        with ThreadPoolExecutor(max_workers=2) as executor:results=list(executor.map(run_import,range(2)))
        assert sum(bool(value.get('replayed')) for value in results)==1
        assert Repository(reader).read(ACTOR)==library
        checks.append('successor-import-replay-conflict-and-concurrent-lock-compatibility')
        # Normal successor imports remain valid. Reapplying the original reviewed
        # adoption input must still reconcile the now-changed inventory.
        try:bind(owner,document)
        except ValueError as error:assert str(error)=='corpus_inventory_changed'
        else:raise AssertionError('stale_reviewed_binding_accepted_after_normal_import')
        checks.append('repeated-reviewed-binding-refuses-current-inventory-drift-after-valid-import')
        session={'account_id':ACTOR,'session_id':str(uuid4()),'expires_at':__import__('datetime').datetime.now(__import__('datetime').timezone.utc)+__import__('datetime').timedelta(minutes=1)}
        repository=Repository(reader);context=repository.create_file_context(session,ACTOR,'DOC-VELTEN','open')
        assert repository.file_context(session,context)
        assert not repository.file_context({**session,'account_id':str(uuid4())},context)
        assert not repository.file_context({**session,'session_id':str(uuid4())},context)
        repository.clear_file_contexts(session);assert not repository.file_context(session,context)
        checks.append('native-persisted-context-account-session-isolation-and-confirmed-invalidation')
        # Departed sessions are unreachable through exact-session RLS. Exercise
        # actual runtime reclamation, fixed batches, retry and live foreign rows.
        from datetime import datetime,timezone,timedelta
        from apps.pts.backend.db import file_scope
        departed={'account_id':str(uuid4()),'session_id':str(uuid4())}
        foreign_ids=[str(uuid4()) for _ in range(260)];live_id=str(uuid4())
        with file_scope(reader,departed['account_id'],departed['session_id'],ACTOR) as conn:
            conn.execute(text("INSERT INTO pts.file_contexts(id,account_id,session_id,document_id,presentation,expires_at) VALUES(:id,:account,:session,'DOC-VELTEN','open',:expires)"),
                [{'id':identity,'account':departed['account_id'],'session':departed['session_id'],'expires':datetime.now(timezone.utc)-timedelta(minutes=1)} for identity in foreign_ids]+
                [{'id':live_id,'account':departed['account_id'],'session':departed['session_id'],'expires':datetime.now(timezone.utc)+timedelta(hours=1)}])
        with file_scope(reader,session['account_id'],session['session_id'],ACTOR) as conn:
            assert conn.execute(text('SELECT count(*) FROM pts.file_contexts')).scalar_one()==0
            assert conn.execute(text('DELETE FROM pts.file_contexts')).rowcount==0
        for expected in (133,5,1,1):
            repository.create_file_context(session,ACTOR,'DOC-VELTEN','open')
            with file_scope(reader,departed['account_id'],departed['session_id'],ACTOR) as conn:
                assert conn.execute(text('SELECT count(*) FROM pts.file_contexts')).scalar_one()==expected,'expired_departed_contexts_not_reclaimed_in_bounded_batches'
                assert conn.execute(text('SELECT count(*) FROM pts.file_contexts WHERE id=:id'),{'id':live_id}).scalar_one()==1,'live_foreign_context_deleted'
        assert reader.pool.checkedout()==0
        for denied in (old,importer):
            try:
                with denied.begin() as conn:conn.execute(text('SELECT pts.reclaim_expired_file_contexts()'))
            except DBAPIError as error:assert error.orig.sqlstate=='42501','reclaimer_forbidden_caller_failed_for_wrong_reason'
            else:raise AssertionError('reclaimer_execution_granted_to_predecessor_or_importer')
        with connect() as blocker:
            blocker.execute('LOCK TABLE pts.file_contexts IN ACCESS EXCLUSIVE MODE')
            started=time.monotonic()
            try:repository.create_file_context(session,ACTOR,'DOC-VELTEN','open')
            except DBAPIError as error:
                assert error.orig.sqlstate=='55P03','reclaimer_lock_failed_for_wrong_reason'
                assert time.monotonic()-started<1.5,'reclaimer_lock_deadline_exceeded'
            else:raise AssertionError('reclaimer_ignored_native_table_lock')
        assert reader.pool.checkedout()==0,'reclaimer_lock_failure_retained_connection'
        repository.create_file_context(session,ACTOR,'DOC-VELTEN','open')
        checks.append('restricted-owner-expiry-reclamation-departed-sessions-fixed-128-batches-retry-and-live-foreign-preservation')
        checks.append('reclaimer-native-predecessor-importer-execute-denials-lock-deadline-pool-release-and-retry')
        # Retain the predecessor's distinct alternate-write FK coverage using
        # actual successor credentials; permission errors cannot pass this oracle.
        for statement,parameters in (
            ("INSERT INTO pts.witnesses(org_id,id,payload,ordinal) VALUES(:org,'FK-BAD-WITNESS',CAST(:payload AS jsonb),0)",
             {'org':ORG,'payload':json.dumps({'id':'FK-BAD-WITNESS','source_id':'missing-source','poem_id':library['poems'][0]['id']})}),
            ("INSERT INTO pts.source_documents(org_id,id,payload,ordinal) VALUES(:org,'FK-BAD-DOCUMENT',CAST(:payload AS jsonb),0)",
             {'org':ORG,'payload':json.dumps({'id':'FK-BAD-DOCUMENT','source_id':'missing-source'})}),
            ("INSERT INTO pts.attachments(org_id,id,document_id,content_id) VALUES(:org,'FK-BAD-ATTACHMENT','missing-document',:content)",
             {'org':ORG,'content':str(uuid4())})):
            try:
                with corpus(importer,ACTOR) as conn:conn.execute(text(statement),parameters)
            except DBAPIError as error:assert error.orig.sqlstate=='23503','alternate_write_failed_for_wrong_reason'
            else:raise AssertionError('alternate_write_foreign_key_not_enforced')
        checks.append('successor-alternate-write-witness-source-document-and-attachment-native-FK-denials')
        from apps.pts.tools import upload_sources
        document=next(row for row in library['source_documents'] if row['id']=='DOC-VELTEN')
        retained=str(repository.attachment(ACTOR,document['id']))
        with patch.dict(os.environ,{'PTS_IMPORT_ACTOR_ID':ACTOR}):
            with patch.object(upload_sources,'upload',side_effect=AssertionError('conflicting_catalogue_reached_external_upload')) as external:
                try:upload_sources.attach_document(importer,{**document,'sha256':'0'*64},Path('.'),None)
                except ValueError as error:assert 'differs from retained' in str(error)
                else:raise AssertionError('conflicting_catalogue_was_not_rejected')
                assert external.call_count==0
            with patch.object(upload_sources,'upload',return_value=retained):
                assert upload_sources.attach_document(importer,document,Path('.'),None)==retained
            with patch.object(upload_sources,'upload',return_value=str(uuid4())):
                try:upload_sources.attach_document(importer,document,Path('.'),None)
                except ValueError as error:assert 'attachment conflict' in str(error)
                else:raise AssertionError('existing_attachment_identity_was_replaced')
        assert str(repository.attachment(ACTOR,document['id']))==retained
        with corpus(reader,ACTOR) as conn:
            assert conn.execute(text('SELECT count(*) FROM pts.attachments WHERE document_id=:id'),{'id':document['id']}).scalar_one()==1
        checks.append('successor-conflicting-catalogue-before-upload-and-attachment-replay-replacement-protection')
        # Synchronize a genuine restricted writer between collection queries.
        # The hook controls timing only; Repository and all SQL run unchanged.
        source={**library['sources'][0],'id':'SOURCE-SNAPSHOT-PROBE'}
        poem={**library['poems'][0],'id':'POEM-SNAPSHOT-PROBE','source_id':source['id']}
        def synchronized_load(conn):
            assert conn.execute(text('SELECT count(*) FROM pts.sources')).scalar_one()==len(library['sources'])
            with corpus(importer,ACTOR) as writer:
                for kind,row in (('sources',source),('poems',poem)):
                    writer.execute(text(f'INSERT INTO pts.{kind}(org_id,id,payload,ordinal) VALUES(:org,:id,CAST(:payload AS jsonb),:ordinal)'),
                        {'org':ORG,'id':row['id'],'payload':json.dumps(row),'ordinal':len(library[kind])})
            return load(conn)
        with patch('apps.pts.backend.main.load',side_effect=synchronized_load):
            assert Repository(reader).read(ACTOR)==library,'collection_read_mixed_committed_snapshots'
        after=Repository(reader).read(ACTOR)
        assert after['sources']==library['sources']+[source] and after['poems']==library['poems']+[poem]
        checks.append('successor-Repository-collection-one-snapshot-across-mid-read-committed-append-and-next-read-visibility')
        docker('stop','--time','20',container);final=json.loads(docker('inspect',container))[0]
        assert final['State']['ExitCode']==0 and not final['State']['OOMKilled'];stopped=True
        bound=[ROOT/'apps/pts'/name for name in ('alembic.ini','reference/poetry-library/library.json')]
        bound += [path for folder in ('backend','migrations','tools','tests') for path in (ROOT/'apps/pts'/folder).rglob('*.py') if '__pycache__' not in path.parts]
        bound += list((ROOT/'apps/pts/tools').glob('*.sql'))
        sources={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(bound)}
        report={'schema_version':1,'complete':True,'checks':checks,'postgres_image_id':image['Id'],'container_id':identity,'stop_exit_code':0,'forced':False,'sources':sources}
        (output/'corpus-native-proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checks':len(checks),'complete':True,'stop_exit_code':0}))
    finally:
        if not stopped:
            try:docker('stop','--time','20',container)
            except Exception:pass

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--bypass-binding-gate',action='store_true',help='Explicit mutation diagnostic: acceptance must fail');args=parser.parse_args();qualify(args.output,args.bypass_binding_gate)
