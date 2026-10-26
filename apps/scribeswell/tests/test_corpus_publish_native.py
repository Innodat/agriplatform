"""DEFERRED: opt-in real PostgreSQL17 publication qualification. Not executed here.

Uses a newly created disposable fixture only. Requires both existing native DSN
and SCRIBESWELL_PUBLICATION_NATIVE=1; never targets retained KDG fixture ports.
These tests exercise actual restricted logins, not SET ROLE substitutes.
"""
from copy import deepcopy
import hashlib
import json
import importlib.util
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit,unquote
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb
import pytest
from alembic import command as alembic_command
from alembic.config import Config

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP/'backend'))
sys.path.insert(0,str(APP/'migrations'))
from generate_reference import prepared_fixture
from test_owned_migrations import invoke,migration_url,business_state
from test_corpus_publication import body,operator,execute,ACTOR
from test_corpus_publication_input import source_bytes,encode
from corpus_publication import lookup_outcome, execute_command
from corpus_source import BOOK_METADATA
from corpus_publish import publish_closed_attempt,lookup_publication,PublishError
import corpus_publish

CUSTODY=dict(schema_version=1,source_id='tanakh',executor_actor_id=ACTOR,actor_kind='service',
             actor_key='fixture.controller',preparation_evidence_ref='fixture:identity')


def upgrade(url,monkeypatch,custody=None):
    monkeypatch.setenv('SCRIBESWELL_MIGRATION_DATABASE_URL',migration_url(url))
    config=Config(str(APP/'alembic.ini'))
    config.attributes['scribeswell_validation_profile']='publication-v1'
    if custody is not None:config.attributes['scribeswell_prepared_actor']=custody
    alembic_command.upgrade(config,'head')
    return config


@pytest.fixture
def native_database(monkeypatch):
    url=os.environ.get('SCRIBESWELL_TEST_DATABASE_URL','')
    if os.environ.get('SCRIBESWELL_PUBLICATION_NATIVE')!='1' or not url:
        pytest.skip('deferred explicit publication native qualification')
    assert urlsplit(url).port not in (55481,55482),'retained KDG fixtures prohibited'
    with prepared_fixture() as (admin,url):
        assert invoke(url).returncode==0
        yield admin,url


@pytest.fixture
def publication_source(request):
    if getattr(request,'param',None)!='multi':return source_bytes()
    source=json.loads(source_bytes())
    source['Genesis']=[[[['שָׁ/אָב','1','HNcmsa']] for _ in range(100)] for _ in range(10)]
    return json.dumps(source,ensure_ascii=False).encode('utf8')


@pytest.fixture
def closed(native_database,monkeypatch,publication_source):
    admin,url=native_database
    upgrade(url,monkeypatch)
    # Synthetic complete corpus is seeded only with dormant enforcement.
    source=json.loads(publication_source);next_id=0
    for meta in BOOK_METADATA:
        columns=sql.SQL(',').join(map(sql.Identifier,meta))
        placeholders=sql.SQL(',').join(sql.Placeholder() for _ in meta)
        admin.execute(sql.SQL('INSERT INTO scribeswell.book ({}) VALUES ({})').format(columns,placeholders),tuple(meta.values()))
        for chapter_number,verses in enumerate(source[meta['name_en']],1):
            chapter_id=meta['id']*1000+chapter_number
            admin.execute('INSERT INTO scribeswell.chapter VALUES (%s,%s,%s)',(chapter_id,meta['id'],chapter_number))
            for verse_number,_ in enumerate(verses,1):
                next_id+=1
                admin.execute('INSERT INTO scribeswell.verse VALUES (%s,%s,%s,%s,%s)',(next_id,chapter_id,meta['id'],chapter_number,verse_number))
                admin.execute("INSERT INTO scribeswell.word(id,verse_id,position,surface_he,display_he,lemma_strong,morph_code) VALUES (%s,%s,1,'שָׁ/אָב','אב','1','HNcmsa')",(next_id,next_id))
    admin.execute('CREATE ROLE scribeswell_corpus_operator LOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOREPLICATION')
    try:
        admin.execute(sql.SQL('ALTER ROLE scribeswell_corpus_operator PASSWORD {}').format(sql.Literal(unquote(urlsplit(url).password or ''))))
        admin.execute('GRANT USAGE ON SCHEMA scribeswell TO scribeswell_corpus_operator')
        admin.execute('GRANT EXECUTE ON FUNCTION scribeswell.execute_corpus_command(jsonb),scribeswell.lookup_corpus_command_outcome(jsonb),scribeswell.execute_corpus_publication(jsonb),scribeswell.lookup_corpus_publication_outcome(jsonb) TO scribeswell_corpus_operator')
        for table in ('book','chapter','verse','word'):
            admin.execute(sql.SQL('CREATE POLICY corpus_operator_audit_read ON scribeswell.{} FOR SELECT TO scribeswell_corpus_operator USING (true)').format(sql.Identifier(table)))
        admin.execute('GRANT SELECT ON scribeswell.book,scribeswell.chapter,scribeswell.verse,scribeswell.word,scribeswell.corpus_fence_control,scribeswell.corpus_epoch,scribeswell.corpus_attempt,scribeswell.corpus_operator_principal,scribeswell.corpus_operator_authority TO scribeswell_corpus_operator')
        admin.execute("INSERT INTO scribeswell.corpus_operator_principal(database_login,enabled,revision,executor_actor_id,actor_kind,actor_key,preparation_evidence_ref,created_by_actor_id,updated_by_actor_id) VALUES ('scribeswell_corpus_operator',true,1,%s,'service','fixture.controller','fixture:identity',%s,%s)",(ACTOR,ACTOR,ACTOR))
        for variant in ('begin','recover','seal'):
            admin.execute("INSERT INTO scribeswell.corpus_operator_authority(database_login,source_id,command,enabled,revision,created_by_actor_id,updated_by_actor_id) VALUES ('scribeswell_corpus_operator','tanakh',%s,true,1,%s,%s)",('corpus.'+variant,ACTOR,ACTOR))
        admin.execute("INSERT INTO scribeswell.corpus_publication_authority(database_login,source_id,enabled,revision,created_by_actor_id,updated_by_actor_id) VALUES ('scribeswell_corpus_operator','tanakh',true,1,%s,%s)",(ACTOR,ACTOR))
        admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=true')
        with operator(url) as connection:
            initial=body()
            initial['payload']['input']['source_sha256']=hashlib.sha256(publication_source).hexdigest()
            started=execute_command(connection,encode(initial),publication_source)
            seal=body('seal',started)
            seal['payload']['input']['source_sha256']=initial['payload']['input']['source_sha256']
            receipt=execute_command(connection,encode(seal),publication_source)
        yield admin,url,seal,receipt
    finally:
        admin.execute('DROP OWNED BY scribeswell_corpus_operator')
        admin.execute('DROP ROLE scribeswell_corpus_operator')


def test_upgrade_repeat_preserves_old_controller_and_public_reads(native_database,monkeypatch):
    admin,url=native_database;before=business_state(admin)
    first=upgrade(url,monkeypatch);second=upgrade(url,monkeypatch)
    assert first.attributes['scribeswell_before']=='scribeswell_0003'
    assert first.attributes['scribeswell_after']==second.attributes['scribeswell_after']=='scribeswell_0004'
    assert business_state(admin)==before
    assert admin.execute('SELECT * FROM scribeswell.current_corpus_publication').fetchall()==[]


def test_native_complete_digest_activation_and_exact_retry(closed,monkeypatch):
    admin,url,seal,sealed=closed;operation=str(uuid4())
    with operator(url) as connection:
        result=publish_closed_attempt(connection,encode(seal),source_bytes(),operation_id=operation)
        assert result.status=='published'
        assert publish_closed_attempt(connection,encode(seal),source_bytes(),operation_id=operation)==result
        assert lookup_outcome(connection,encode(seal))==sealed
        assert admin.execute('SELECT source_revision::text FROM scribeswell.current_corpus_publication').fetchall()==[(result.source_revision,)]
        recovered=execute(connection,body('recover',sealed))
        assert recovered.generation=='2'
        assert admin.execute('SELECT * FROM scribeswell.current_corpus_publication').fetchall()==[]
        assert lookup_publication(connection,encode(seal),source_bytes(),operation_id=operation)==result
        assert publish_closed_attempt(connection,encode(seal),source_bytes(),operation_id=operation)==result
        assert admin.execute('SELECT * FROM scribeswell.current_corpus_publication').fetchall()==[]
    assert upgrade(url,monkeypatch,CUSTODY).attributes['scribeswell_after']=='scribeswell_0004'


@pytest.mark.parametrize('role',['anon','authenticated','service_role','scribeswell_runtime','scribeswell_import'])
def test_native_shipped_roles_cannot_publish_or_mutate(native_database,monkeypatch,role):
    admin,url=native_database;upgrade(url,monkeypatch)
    module=load_migration()
    for table in module.TABLES:
        assert admin.execute("SELECT has_table_privilege(%s,%s,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')",(role,'scribeswell.'+table)).fetchone()==(False,)
    for function in ('execute_corpus_publication(jsonb)','lookup_corpus_publication_outcome(jsonb)','corpus_publication_internal(jsonb,boolean)'):
        assert admin.execute("SELECT has_function_privilege(%s,%s,'EXECUTE')",(role,'scribeswell.'+function)).fetchone()==(False,)


@pytest.mark.parametrize('change',['authority','enforcement'])
def test_native_revocation_or_disable_blocks_new_publication(closed,change):
    admin,url,seal,sealed=closed
    if change=='authority':admin.execute('UPDATE scribeswell.corpus_publication_authority SET enabled=false,revision=revision+1')
    else:admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
    with operator(url) as connection:
        with pytest.raises(PublishError):publish_closed_attempt(connection,encode(seal),source_bytes(),operation_id=str(uuid4()))
    assert admin.execute('SELECT * FROM scribeswell.current_corpus_publication').fetchall()==[]


def test_native_recovery_rejects_missing_completion_and_retains_stage(closed,monkeypatch):
    admin,url,seal,sealed=closed;captured=[];original=corpus_publish._acknowledge
    def stop(connection,request):
        if request['command']=='publication.complete':
            captured.append(request);raise RuntimeError('intentional pre-completion stop')
        return original(connection,request)
    with operator(url) as connection:
        with monkeypatch.context() as scope:
            scope.setattr(corpus_publish,'_acknowledge',stop)
            with pytest.raises(RuntimeError):publish_closed_attempt(connection,encode(seal),source_bytes(),operation_id=str(uuid4()))
        execute(connection,body('recover',sealed))
        with pytest.raises(PublishError,match='conflict'):original(connection,captured[0])
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_header').fetchone()==(1,)
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_completion').fetchone()==(0,)
    assert admin.execute('SELECT * FROM scribeswell.current_corpus_publication').fetchall()==[]


def load_migration():
    spec=importlib.util.spec_from_file_location('publication_revision',APP/'migrations/versions/0004_corpus_publication.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def test_native_failed_ddl_rolls_back_additions_without_ledger_change(native_database):
    admin,url=native_database
    with psycopg.connect(migration_url(url),autocommit=True) as migration:
        with pytest.raises(RuntimeError):
            with migration.transaction():
                migration.execute(load_migration().DDL)
                raise RuntimeError('intentional failed release migration')
    assert admin.execute("SELECT to_regclass('scribeswell.corpus_manifest_header')").fetchone()==(None,)
    assert admin.execute('SELECT version_num FROM scribeswell.alembic_version').fetchone()==('scribeswell_0003',)


def test_native_partial_or_changed_manifest_cannot_complete(closed,monkeypatch):
    admin,url,seal,sealed=closed;requests=[];original=corpus_publish._acknowledge
    def stage_only(connection,request):
        if request['command']!='publication.stage':
            requests.append(request);raise RuntimeError('intentional stage-only stop')
        return original(connection,request)
    with operator(url) as connection:
        with monkeypatch.context() as scope:
            scope.setattr(corpus_publish,'_acknowledge',stage_only)
            with pytest.raises(RuntimeError):publish_closed_attempt(connection,encode(seal),source_bytes(),operation_id=str(uuid4()))
        batch=requests[0]
        header=admin.execute('SELECT header FROM scribeswell.corpus_manifest_header').fetchone()[0]
        completion={k:v for k,v in batch.items() if k in {'version','seal','source_revision'}}
        completion.update(operation_id=str(uuid4()),command='publication.complete',auditor_version=header['auditor_version'],
                          digest=header['digest'],verse_count=header['verse_count'],token_count=header['token_count'])
        with pytest.raises(PublishError,match='conflict'):original(connection,completion)
        changed=dict(batch,rows=batch['rows'][:-1])
        with pytest.raises(PublishError,match='conflict'):original(connection,changed)
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_completion').fetchone()==(0,)


@pytest.mark.parametrize('sql_command',[
    'UPDATE scribeswell.corpus_manifest_header SET header=header',
    'DELETE FROM scribeswell.corpus_manifest_header',
    'TRUNCATE scribeswell.corpus_manifest_header CASCADE'])
def test_native_alternate_writes_preserve_immutable_proof(closed,sql_command):
    admin,url,seal,sealed=closed
    with operator(url) as connection:
        publish_closed_attempt(connection,encode(seal),source_bytes(),operation_id=str(uuid4()))
    with pytest.raises(psycopg.errors.RaiseException):admin.execute(sql_command)
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_header').fetchone()==(1,)


# The following regressions are authored only; none are native qualification yet.
def planned_requests(closed,monkeypatch,raw=None):
    """Use the actual closed auditor, then retain its unpublished protocol plan."""
    _,url,seal,_=closed;requests=[]
    with monkeypatch.context() as scope:
        scope.setattr(corpus_publish,'_acknowledge',lambda connection,request:requests.append(deepcopy(request)))
        with operator(url) as connection:
            publish_closed_attempt(connection,encode(seal),raw or source_bytes(),operation_id=str(uuid4()))
    return requests


def execute_requests(url,requests):
    with operator(url) as connection:
        return [corpus_publish._acknowledge(connection,request) for request in requests]


def insert_batch_evidence(admin,request,*,batch_rows=None,batch_index=None,first_ordinal=None):
    """Alternate owner INSERT path; normalized rows retain the audited manifest."""
    revision=request['source_revision'];index=request['batch_index'] if batch_index is None else batch_index
    offset=request['first_ordinal'] if first_ordinal is None else first_ordinal
    admin.execute('INSERT INTO scribeswell.corpus_manifest_batch(source_revision,batch_index,first_ordinal,rows,created_by_actor_id) VALUES (%s,%s,%s,%s,%s)',
                  (revision,index,offset,Jsonb(request['rows'] if batch_rows is None else batch_rows),ACTOR))
    for ordinal,row in enumerate(request['rows'],request['first_ordinal']):
        admin.execute('INSERT INTO scribeswell.corpus_manifest_verse(source_revision,ordinal,batch_index,book,chapter,verse,verse_token_digest,word_ids,created_by_actor_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                      (revision,ordinal,index,*row[:4],Jsonb(row[4]),ACTOR))
        for position,word_id in enumerate(row[4],1):
            admin.execute('INSERT INTO scribeswell.corpus_manifest_word_identity(source_revision,ordinal,position,word_id,created_by_actor_id) VALUES (%s,%s,%s,%s,%s)',
                          (revision,ordinal,position,word_id,ACTOR))


def assert_unpublished(admin):
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_completion').fetchone()==(0,)
    assert admin.execute('SELECT * FROM scribeswell.current_corpus_publication').fetchall()==[]


@pytest.mark.parametrize('inconsistency',['rows','index','offset'])
def test_native_completion_rejects_complete_inconsistent_batch_evidence(closed,monkeypatch,inconsistency):
    admin,url,_,_=closed;requests=planned_requests(closed,monkeypatch)
    stage,batch,completion,_=requests
    execute_requests(url,[stage])
    options={}
    if inconsistency=='rows':
        changed=deepcopy(batch['rows']);changed[0][3]='0'*64;options['batch_rows']=changed
    elif inconsistency=='index':options['batch_index']=1
    else:options['first_ordinal']=1
    insert_batch_evidence(admin,batch,**options)
    # Every normalized verse/ID and the full manifest digest still match; only
    # persisted batch evidence disagrees. Count-only completion used to accept it.
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_verse').fetchone()==(39,)
    with operator(url) as connection:
        with pytest.raises(PublishError,match='conflict'):corpus_publish._acknowledge(connection,completion)
    assert_unpublished(admin)


@pytest.mark.parametrize('table',['batch','verse','word_identity','completion'])
def test_native_alternate_constituent_actor_must_match_header(closed,monkeypatch,table):
    admin,url,_,_=closed;stage,batch,completion,_=planned_requests(closed,monkeypatch)
    execute_requests(url,[stage])
    revision=stage['source_revision'];wrong_actor='77777777-7777-4777-8777-777777777777'
    if table=='completion':execute_requests(url,[batch])
    elif table in ('verse','word_identity'):
        admin.execute('INSERT INTO scribeswell.corpus_manifest_batch(source_revision,batch_index,first_ordinal,rows,created_by_actor_id) VALUES (%s,0,0,%s,%s)',(revision,Jsonb(batch['rows']),ACTOR))
        if table=='word_identity':
            row=batch['rows'][0]
            admin.execute('INSERT INTO scribeswell.corpus_manifest_verse(source_revision,ordinal,batch_index,book,chapter,verse,verse_token_digest,word_ids,created_by_actor_id) VALUES (%s,0,0,%s,%s,%s,%s,%s,%s)',(revision,*row[:4],Jsonb(row[4]),ACTOR))
    row=batch['rows'][0]
    statement,parameters={
        'batch':('INSERT INTO scribeswell.corpus_manifest_batch(source_revision,batch_index,first_ordinal,rows,created_by_actor_id) VALUES (%s,0,0,%s,%s)',(revision,Jsonb(batch['rows']),wrong_actor)),
        'verse':('INSERT INTO scribeswell.corpus_manifest_verse(source_revision,ordinal,batch_index,book,chapter,verse,verse_token_digest,word_ids,created_by_actor_id) VALUES (%s,0,0,%s,%s,%s,%s,%s,%s)',(revision,*row[:4],Jsonb(row[4]),wrong_actor)),
        'word_identity':('INSERT INTO scribeswell.corpus_manifest_word_identity(source_revision,ordinal,position,word_id,created_by_actor_id) VALUES (%s,0,1,%s,%s)',(revision,row[4][0],wrong_actor)),
        'completion':('INSERT INTO scribeswell.corpus_manifest_completion(source_revision,auditor_version,digest,verse_count,token_count,created_by_actor_id) VALUES (%s,%s,%s,%s,%s,%s)',(revision,completion['auditor_version'],completion['digest'],completion['verse_count'],completion['token_count'],wrong_actor))}[table]
    with pytest.raises(psycopg.errors.RaiseException,match='corpus_publish.conflict'):admin.execute(statement,parameters)
    assert_unpublished(admin)


def test_native_full_digest_rejection_after_structurally_valid_batches(closed,monkeypatch):
    admin,url,_,_=closed;stage,batch,completion,_=planned_requests(closed,monkeypatch)
    stage['header']['digest']='0'*64;completion['digest']='0'*64
    execute_requests(url,[stage,batch])
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_batch').fetchone()==(1,)
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_verse').fetchone()==(39,)
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_word_identity').fetchone()==(39,)
    with operator(url) as connection:
        with pytest.raises(PublishError,match='conflict'):corpus_publish._acknowledge(connection,completion)
    assert_unpublished(admin)


@pytest.mark.parametrize('append_kind',['batch','verse','word_identity'])
def test_native_alternate_append_waits_for_completion_header_lock(closed,monkeypatch,append_kind):
    from test_corpus_writer_fence import background,wait_blocked
    admin,url,_,_=closed;stage,batch,completion,_=planned_requests(closed,monkeypatch)
    execute_requests(url,[stage,batch])
    revision=stage['source_revision'];row=batch['rows'][0]
    statement,parameters={
        'batch':('INSERT INTO scribeswell.corpus_manifest_batch(source_revision,batch_index,first_ordinal,rows,created_by_actor_id) VALUES (%s,1,39,%s,%s)',(revision,Jsonb([row]),ACTOR)),
        'verse':('INSERT INTO scribeswell.corpus_manifest_verse(source_revision,ordinal,batch_index,book,chapter,verse,verse_token_digest,word_ids,created_by_actor_id) VALUES (%s,39,0,\'Gen\',2,1,%s,%s,%s)',(revision,row[3],Jsonb(['999']),ACTOR)),
        'word_identity':('INSERT INTO scribeswell.corpus_manifest_word_identity(source_revision,ordinal,position,word_id,created_by_actor_id) VALUES (%s,0,2,999,%s)',(revision,ACTOR))}[append_kind]
    from threading import Event
    start=Event()
    with psycopg.connect(url,autocommit=True,options='-c statement_timeout=6000') as completing,psycopg.connect(url,autocommit=True,options='-c statement_timeout=6000') as appending:
        def append():
            assert start.wait(5),'completion must reach its uncommitted barrier'
            return appending.execute(statement,parameters)
        with background(appending,append) as future:
            with completing.transaction():
                completing.execute('INSERT INTO scribeswell.corpus_manifest_completion(source_revision,auditor_version,digest,verse_count,token_count,created_by_actor_id) VALUES (%s,%s,%s,%s,%s,%s)',
                                   (revision,completion['auditor_version'],completion['digest'],completion['verse_count'],completion['token_count'],ACTOR))
                start.set()
                wait_blocked(admin,appending.info.backend_pid,completing.info.backend_pid)
                assert not future.done()
            with pytest.raises(psycopg.errors.RaiseException,match='corpus_publish.conflict'):future.result(timeout=5)
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_completion').fetchone()==(1,)
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_batch').fetchone()==(1,)
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_verse').fetchone()==(39,)
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_word_identity').fetchone()==(39,)


@pytest.mark.parametrize('publication_source',['multi'],indirect=True)
def test_native_multibatch_missing_order_and_exact_resume(closed,monkeypatch,publication_source):
    admin,url,seal,_=closed;requests=planned_requests(closed,monkeypatch,publication_source)
    stage,first,second,completion,activation=requests
    assert [len(first['rows']),len(second['rows'])]==[1000,38]
    execute_requests(url,[stage])
    with operator(url) as connection:
        with pytest.raises(PublishError,match='conflict'):corpus_publish._acknowledge(connection,second)
        with pytest.raises(PublishError,match='conflict'):corpus_publish._acknowledge(connection,completion)
    execute_requests(url,[first])
    before=admin.execute('SELECT count(*) FROM scribeswell.corpus_publication_outcome').fetchone()[0]
    assert execute_requests(url,[first])[0].status=='batched'
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_publication_outcome').fetchone()[0]==before
    with operator(url) as connection:
        with pytest.raises(PublishError,match='conflict'):corpus_publish._acknowledge(connection,completion)
    assert_unpublished(admin)
    result=execute_requests(url,[second,completion,activation])[-1]
    with operator(url) as connection:
        assert publish_closed_attempt(connection,encode(seal),publication_source,operation_id=activation['operation_id'])==result
    assert admin.execute('SELECT batch_index,first_ordinal,jsonb_array_length(rows) FROM scribeswell.corpus_manifest_batch ORDER BY batch_index').fetchall()==[(0,0,1000),(1,1000,38)]


@pytest.mark.parametrize('winner',['publication','recovery'])
def test_native_publication_recovery_serializes_at_observed_barrier(closed,monkeypatch,winner):
    from threading import Event
    from test_corpus_writer_fence import background,wait_blocked
    admin,url,seal,sealed=closed;requests=planned_requests(closed,monkeypatch)
    execute_requests(url,requests[:-1]);activation=requests[-1];recovery=body('recover',sealed)
    start=Event()
    with operator(url) as holding,operator(url) as waiting:
        def contender():
            assert start.wait(5),'winning transition must reach its uncommitted barrier'
            return (execute(waiting,recovery) if winner=='publication'
                    else corpus_publish._acknowledge(waiting,activation))
        with background(waiting,contender) as future:
            with holding.transaction():
                if winner=='publication':
                    holding.execute('SELECT scribeswell.execute_corpus_publication(%s)',(Jsonb(activation),))
                else:
                    holding.execute('SELECT scribeswell.execute_corpus_command(%s)',(Jsonb(recovery),))
                start.set()
                wait_blocked(admin,waiting.info.backend_pid,holding.info.backend_pid)
                assert not future.done()
            if winner=='publication':assert future.result(timeout=5).generation=='2'
            else:
                with pytest.raises(PublishError,match='conflict'):future.result(timeout=5)
    assert admin.execute('SELECT * FROM scribeswell.current_corpus_publication').fetchall()==[]
    with operator(url) as connection:
        original=lookup_publication(connection,encode(seal),source_bytes(),operation_id=activation['operation_id'])
        assert (original is not None)==(winner=='publication')
    assert admin.execute("SELECT generation,state FROM scribeswell.corpus_epoch").fetchone()==(2,'updating')


@pytest.mark.parametrize('boundary',['publication.stage','publication.batch','publication.complete','publication.activate'])
def test_native_postcommit_ack_loss_reconciles_each_original_operation(closed,monkeypatch,boundary):
    admin,url,seal,_=closed;operation=str(uuid4());original=corpus_publish._call;lost=[]
    def lose_after_commit(connection,request,*,lookup):
        result=original(connection,request,lookup=lookup)
        if not lookup and request['command']==boundary and not lost:
            # Separate connection visibility proves that loss is injected after
            # the durable boundary, rather than simulating a pre-commit failure.
            assert admin.execute('SELECT count(*) FROM scribeswell.corpus_publication_outcome WHERE operation_id=%s',(request['operation_id'],)).fetchone()==(1,)
            lost.append(request['operation_id'])
            raise PublishError('unknown_outcome')
        return result
    monkeypatch.setattr(corpus_publish,'_call',lose_after_commit)
    with operator(url) as connection:
        result=publish_closed_attempt(connection,encode(seal),source_bytes(),operation_id=operation)
        assert publish_closed_attempt(connection,encode(seal),source_bytes(),operation_id=operation)==result
    assert len(lost)==1 and result.status=='published'
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_publication_outcome').fetchone()==(4,)
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_header').fetchone()==(1,)
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_completion').fetchone()==(1,)


def test_native_supervised_stdout_discard_original_lookup_retry_and_revocation(closed, monkeypatch):
    """Authored only: deliberate child stdout discard, not a network fault claim."""
    import corpus_operator as supervised
    from test_postgres_acceptance import role_url
    admin, url, seal, sealed = closed
    target = supervised.OperatorTarget('local_disposable',
        role_url(url, 'scribeswell_corpus_operator'), unquote(urlsplit(url).path[1:]))
    operation = str(uuid4())
    raw, source = encode(seal), source_bytes()
    original = supervised._worker_command
    discarded = original()
    discarded[-1] = discarded[-1].replace('from corpus_operator import _worker_main;',
        "import os;sys.stdout=open(os.devnull,'w');from corpus_operator import _worker_main;")
    monkeypatch.setattr(supervised, '_worker_command', lambda: discarded)
    with pytest.raises(PublishError, match='unknown_outcome'):
        supervised.publish_closed_attempt(target, raw, source, operation_id=operation)
    # Native independent visibility, before any reconciliation or retry.
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_publication_outcome WHERE operation_id=%s',
                         (operation,)).fetchone() == (1,)
    monkeypatch.setattr(supervised, '_worker_command', original)
    result = supervised.lookup_publication(target, raw, source, operation_id=operation)
    assert result is not None and result.operation_id == operation
    assert supervised.publish_closed_attempt(target, raw, source, operation_id=operation) == result
    with operator(url) as connection:
        execute(connection, body('recover', sealed))
    assert supervised.lookup_publication(target, raw, source, operation_id=operation) == result
    assert supervised.publish_closed_attempt(target, raw, source, operation_id=operation) == result
    assert admin.execute('SELECT * FROM scribeswell.current_corpus_publication').fetchall() == []
    admin.execute('UPDATE scribeswell.corpus_publication_authority SET enabled=false,revision=revision+1')
    for invoke in (supervised.lookup_publication, supervised.publish_closed_attempt):
        with pytest.raises(PublishError, match='access_denied'):
            invoke(target, raw, source, operation_id=operation)
    assert (raw, source) == (encode(seal), source_bytes())
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_header').fetchone() == (1,)
