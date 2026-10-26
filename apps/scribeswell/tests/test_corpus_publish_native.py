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


def upgrade(url,monkeypatch,custody=None,*,capacity=False):
    monkeypatch.setenv('SCRIBESWELL_MIGRATION_DATABASE_URL',migration_url(url))
    config=Config(str(APP/'alembic.ini'))
    config.attributes['scribeswell_validation_profile']='publication-capacity-v1' if capacity else 'publication-v1'
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
    if getattr(request,'param',None)=='maximum':
        source={m['name_en']:[[[['אב','1','HNcmsa'] for _ in range(20)]]] for m in BOOK_METADATA}
        for name,count in [('Genesis',26400),('Exodus',23563)]:
            source[name]=[[[['אב','1','HNcmsa'] for _ in range(20)] for _ in range(min(176,count-offset))] for offset in range(0,count,176)]
        return json.dumps(source,ensure_ascii=False,separators=(',',':')).encode('utf8')
    if getattr(request,'param',None)=='artifact':return (APP/'scripts/hebrew.json').read_bytes()
    if getattr(request,'param',None)!='multi':return source_bytes()
    source=json.loads(source_bytes())
    source['Genesis']=[[[['שָׁ/אָב','1','HNcmsa']] for _ in range(100)] for _ in range(10)]
    return json.dumps(source,ensure_ascii=False).encode('utf8')


@pytest.fixture
def closed(native_database,monkeypatch,publication_source):
    admin,url=native_database
    upgrade(url,monkeypatch,capacity=len(publication_source)>1000000)
    if os.environ.get('SCRIBESWELL_CAPACITY_SQL_PHASES')=='1':
        revision=importlib.util.spec_from_file_location('capacity_owning_revision',APP/'migrations/versions/0006_publication_append_batches.py')
        module=importlib.util.module_from_spec(revision);revision.loader.exec_module(module)
        definition=module.DDL[module.DDL.index('CREATE OR REPLACE FUNCTION scribeswell.corpus_publication_internal'):]
        definition=definition[:definition.index('$body$;',definition.index('AS $body$')+10)+8]
        definition=definition.replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1).replace('DECLARE ', 'DECLARE phase_started timestamptz=clock_timestamp(); ',1)
        for marker,phase in [('    INSERT INTO scribeswell.corpus_manifest_batch','validation'),('    INSERT INTO scribeswell.corpus_manifest_verse','batch'),('    INSERT INTO scribeswell.corpus_manifest_word_identity','verses')]:
            definition=definition.replace(marker,"    RAISE NOTICE 'capacity_phase:"+phase+":%',EXTRACT(EPOCH FROM clock_timestamp()-phase_started);\n"+marker)
        admin.execute(definition)
    # Synthetic complete corpus is seeded only with dormant enforcement.
    if publication_source==(APP/'scripts/hebrew.json').read_bytes() and os.environ.get('SCRIBESWELL_CAPACITY_FIXTURE_COPY_ONLY')!='1':
        # Actual checked-in artifact through the supported importer, no hand-built rows.
        spec=importlib.util.spec_from_file_location('final_native_bible_importer',APP/'tools/py/import_bible.py')
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        parts=urlsplit(url)
        import_url=parts._replace(netloc='scribeswell_import:'+parts.netloc.split('@')[0].split(':',1)[1]+'@'+parts.netloc.split('@')[1]).geturl()
        import time
        import_started=time.monotonic()
        importer=module.BibleImporter(import_url)
        try:importer.run(APP/'scripts/hebrew.json')
        finally:importer.close()
        print('IMPORT_ARTIFACT_TIMING',round(time.monotonic()-import_started,3),flush=True)
    elif len(publication_source)>1000000:
        source=json.loads(publication_source)
        def coordinates():
            verse_id=0
            for meta in BOOK_METADATA:
                for chapter_number,verses in enumerate(source[meta['name_en']],1):
                    for verse_number,words in enumerate(verses,1):
                        verse_id+=1
                        yield verse_id,meta['id']*1000+chapter_number,meta['id'],chapter_number,verse_number,words
        with admin.cursor() as cursor:
            with cursor.copy('COPY scribeswell.book(id,osis_id,name_en,name_he,testament,division,book_order) FROM STDIN') as copy:
                for meta in BOOK_METADATA:copy.write_row(tuple(meta.values()))
            with cursor.copy('COPY scribeswell.chapter(id,book_id,chapter_num) FROM STDIN') as copy:
                for meta in BOOK_METADATA:
                    for ch in range(1,len(source[meta['name_en']])+1):copy.write_row((meta['id']*1000+ch,meta['id'],ch))
            with cursor.copy('COPY scribeswell.verse(id,chapter_id,book_id,chapter_num,verse_num) FROM STDIN') as copy:
                for row in coordinates():copy.write_row(row[:5])
            with cursor.copy('COPY scribeswell.word(id,verse_id,position,surface_he) FROM STDIN') as copy:
                word_id=0
                for verse_id,_,_,_,_,words in coordinates():
                    for position,word in enumerate(words,1):
                        from corpus_source import decode_word
                        surface=decode_word(word,'owned-capacity-fixture')[0]['surface_he']
                        word_id+=1;copy.write_row((word_id,verse_id,position,surface))
    else:
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
                    admin.execute('INSERT INTO scribeswell.verse(id,chapter_id,book_id,chapter_num,verse_num) VALUES (%s,%s,%s,%s,%s)',(next_id,chapter_id,meta['id'],chapter_number,verse_number))
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


@pytest.mark.parametrize('publication_source',['artifact','maximum'],indirect=True)
def test_native_checked_in_artifact_publication_capacity_timing_and_replay(closed,publication_source,monkeypatch,tmp_path):
    import time
    from corpus_evidence import build_source_candidate
    admin,url,seal,_=closed
    expected=build_source_candidate(publication_source,hashlib.sha256(publication_source).hexdigest(),source_id='tanakh',catalogue_version=seal['payload']['input']['catalogue_version'],versification_id=seal['payload']['input']['versification_id'],tokenization_version=seal['payload']['input']['tokenization_version'])
    counts=expected['counts']
    actual=admin.execute('SELECT (SELECT count(*) FROM scribeswell.book),(SELECT count(*) FROM scribeswell.chapter),(SELECT count(*) FROM scribeswell.verse),(SELECT count(*) FROM scribeswell.word)').fetchone()
    assert actual==tuple(counts[k] for k in ('books','chapters','verses','tokens'))
    import corpus_operator as supervised
    from test_postgres_acceptance import role_url
    target=supervised.OperatorTarget('local_disposable',role_url(url,'scribeswell_corpus_operator'),unquote(urlsplit(url).path[1:]))
    print('QUALIFIED_CAPACITY_SOURCE',json.dumps({'source_bytes':len(publication_source),'source_sha256':hashlib.sha256(publication_source).hexdigest(),'counts':counts},sort_keys=True),flush=True)
    if os.environ.get('SCRIBESWELL_CAPACITY_DIAGNOSTICS')=='1':
        probe=tmp_path/'capacity-probe.py';trace=tmp_path/'capacity-steps.jsonl'
        probe.write_text(CAPACITY_PROBE.replace('TRACE_PATH',repr(str(trace))))
        original_worker=supervised._worker_command
        def diagnostic_worker():
            command=original_worker()
            command[-1]=command[-1].replace('from corpus_operator import _worker_main;',"import runpy;runpy.run_path("+repr(str(probe))+");from corpus_operator import _worker_main;")
            return command
        monkeypatch.setattr(supervised,'_worker_command',diagnostic_worker)
    operation=str(uuid4());windows=[]
    def publication_window():
        started=time.monotonic();status='unknown'
        try:
            receipt=supervised.publish_closed_attempt(target,encode(seal),publication_source,operation_id=operation)
            status='published';return receipt
        except PublishError as error:
            status=error.code;raise
        finally:
            seconds=time.monotonic()-started
            windows.append({'status':status,'seconds':round(seconds,3)})
            print('SUPERVISED_PUBLICATION_WINDOW',json.dumps(windows[-1],sort_keys=True),flush=True)
            assert seconds<60, 'Each original-operation invocation retains its existing total budget'
    try:
        try:result=publication_window()
        except PublishError as first:
            if first.code!='corpus_publish.unknown_outcome':raise
            # Explicit caller rehearsal after a bounded unknown outcome. The
            # runtime never respawns/retries. Retain the same frozen operation.
            assert admin.execute('SELECT count(*) FROM scribeswell.corpus_publication_outcome').fetchone()[0]>0
            print('EXPLICIT_ORIGINAL_OPERATION_RECONCILIATION',operation,flush=True)
            result=supervised.lookup_publication(target,encode(seal),publication_source,operation_id=operation)
            if result is None:result=publication_window()
    finally:
        if os.environ.get('SCRIBESWELL_CAPACITY_DIAGNOSTICS')=='1' and trace.exists():print(trace.read_text(),flush=True)
        print('DURABLE_PUBLICATION_STEPS',admin.execute("SELECT semantic_command->>'command',count(*) FROM scribeswell.corpus_publication_outcome GROUP BY 1 ORDER BY 1").fetchall(),flush=True)
    with operator(url) as connection:
        assert lookup_publication(connection,encode(seal),publication_source,operation_id=operation)==result
        assert publish_closed_attempt(connection,encode(seal),publication_source,operation_id=operation)==result
    assert result.status=='published' and result.operation_id==operation
    assert all(window['seconds']<58 for window in windows if window['status']=='published')
    stored=admin.execute('SELECT verse_count,token_count FROM scribeswell.corpus_manifest_completion WHERE source_revision=%s',(result.source_revision,)).fetchone()
    assert stored==(counts['verses'],counts['tokens'])
    print('ACTUAL_ARTIFACT_PUBLICATION',json.dumps({'source_sha256':hashlib.sha256(publication_source).hexdigest(),'source_bytes':len(publication_source),'counts':counts,'supervised_publication_windows':windows,'operation_id':operation,'outer_budget_seconds':60,'work_budget_seconds':58,'statement_timeout_seconds':5},sort_keys=True))


@pytest.mark.parametrize('append_kind',['batch','verse','word_identity'])
def test_native_capacity_append_preserves_completion_header_serialization(closed,monkeypatch,append_kind):
    _,url,_,_=closed
    upgraded=upgrade(url,monkeypatch,CUSTODY,capacity=True)
    assert upgraded.attributes['scribeswell_before']=='scribeswell_0004'
    assert upgraded.attributes['scribeswell_after']=='scribeswell_0006'
    test_native_alternate_append_waits_for_completion_header_lock(closed,monkeypatch,append_kind)


@pytest.mark.parametrize('table',['batch','verse','word_identity'])
def test_native_capacity_append_retains_actor_checks(closed,monkeypatch,table):
    _,url,_,_=closed
    upgrade(url,monkeypatch,CUSTODY,capacity=True)
    test_native_alternate_constituent_actor_must_match_header(closed,monkeypatch,table)


def test_native_capacity_profile_replay_and_old_profiles_remain_pinned(native_database,monkeypatch):
    admin,url=native_database
    assert upgrade(url,monkeypatch).attributes['scribeswell_after']=='scribeswell_0004'
    capacity=upgrade(url,monkeypatch,capacity=True)
    assert capacity.attributes['scribeswell_before']=='scribeswell_0004'
    assert capacity.attributes['scribeswell_after']=='scribeswell_0006'
    assert upgrade(url,monkeypatch,capacity=True).attributes['scribeswell_after']=='scribeswell_0006'
    with pytest.raises(Exception):upgrade(url,monkeypatch)
    assert admin.execute('SELECT version_num FROM scribeswell.alembic_version').fetchone()==('scribeswell_0006',)


def test_native_capacity_migration_rollback_and_forward_retry(native_database,monkeypatch,tmp_path):
    import shutil
    admin,url=native_database
    upgrade(url,monkeypatch)
    history=tmp_path/'migrations';shutil.copytree(APP/'migrations',history)
    revision=history/'versions/0006_publication_append_batches.py'
    revision.write_text(revision.read_text().replace('def upgrade():op.get_bind().exec_driver_sql(DDL)',"def upgrade():\n op.get_bind().exec_driver_sql(DDL)\n raise RuntimeError('synthetic post-DDL failure')"))
    config=Config(str(APP/'alembic.ini'));config.set_main_option('script_location',str(history));config.attributes['scribeswell_validation_profile']='publication-capacity-v1'
    with pytest.raises(Exception,match='scribeswell_migration_failed_requires_reconciliation'):
        alembic_command.upgrade(config,'head')
    assert admin.execute('SELECT version_num FROM scribeswell.alembic_version').fetchone()==('scribeswell_0004',)
    assert not admin.execute("SELECT 1 FROM pg_trigger WHERE tgname='corpus_publication_append'").fetchone()
    assert config.attributes.get('scribeswell_validated_profile') is None
    assert upgrade(url,monkeypatch,capacity=True).attributes['scribeswell_after']=='scribeswell_0006'


def test_native_capacity_append_first_blocks_completion_then_rejects_inconsistent_inventory(closed,monkeypatch):
    from test_corpus_writer_fence import background,wait_blocked
    admin,url,_,_=closed
    upgrade(url,monkeypatch,CUSTODY,capacity=True)
    stage,batch,completion,_=planned_requests(closed,monkeypatch)
    execute_requests(url,[stage,batch]);revision=stage['source_revision']
    with psycopg.connect(url,autocommit=True) as appending,operator(url) as completing:
        with appending.transaction():
            appending.execute('INSERT INTO scribeswell.corpus_manifest_word_identity(source_revision,ordinal,position,word_id,created_by_actor_id) VALUES(%s,0,2,999,%s)',(revision,ACTOR))
            with background(completing,lambda:corpus_publish._acknowledge(completing,completion)) as future:
                wait_blocked(admin,completing.info.backend_pid,appending.info.backend_pid)
                appending.execute('COMMIT')
                with pytest.raises(PublishError,match='conflict'):future.result(timeout=5)
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_word_identity WHERE source_revision=%s',(revision,)).fetchone()==(40,)
    assert_unpublished(admin)


def test_native_capacity_multirow_actor_refusal_is_atomic_and_sets_server_time(closed,monkeypatch):
    admin,url,_,_=closed
    upgrade(url,monkeypatch,CUSTODY,capacity=True)
    stage,batch,_,_=planned_requests(closed,monkeypatch)
    execute_requests(url,[stage,batch]);revision=stage['source_revision'];wrong=str(uuid4())
    with pytest.raises(psycopg.Error) as failure:
        admin.execute('INSERT INTO scribeswell.corpus_manifest_word_identity(source_revision,ordinal,position,word_id,created_by_actor_id) VALUES(%s,0,2,999,%s),(%s,0,3,1000,%s)',(revision,ACTOR,revision,wrong))
    assert failure.value.sqlstate=='P0001'
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_word_identity WHERE source_revision=%s',(revision,)).fetchone()==(39,)
    admin.execute("INSERT INTO scribeswell.corpus_manifest_word_identity(source_revision,ordinal,position,word_id,created_by_actor_id,created_at) VALUES(%s,0,2,999,%s,'2000-01-01T00:00:00Z')",(revision,ACTOR))
    assert admin.execute('SELECT created_at>\'2026-01-01T00:00:00Z\'::timestamptz FROM scribeswell.corpus_manifest_word_identity WHERE source_revision=%s AND word_id=999',(revision,)).fetchone()==(True,)


# Explicit test-only observations, never worker protocol output or business content.
CAPACITY_PROBE = r"""
import json,os,time,psycopg,corpus_publish
trace_fd=os.open(TRACE_PATH,os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
def record(value):os.write(trace_fd,(json.dumps(value,separators=(',',':'))+'\n').encode())
original_execute=psycopg.Connection.execute
def execute(self,*args,**kwargs):
 if not getattr(self,'_capacity_notice',False):
  import re
  def notice(diag):
   if re.fullmatch(r'capacity_phase:[a-z]+:[0-9.]+',diag.message_primary or ''):record({'sql_phase':diag.message_primary})
  self.add_notice_handler(notice);self._capacity_notice=True
 try:return original_execute(self,*args,**kwargs)
 except Exception as error:
  import re
  locations=re.findall(r'function ([a-zA-Z0-9_.]+)\([^\n]*?\) line ([0-9]+)',getattr(getattr(error,'diag',None),'context','') or '')
  record({'driver_class':type(error).__name__,'sqlstate':getattr(error,'sqlstate',None),'routine_lines':locations})
  raise
psycopg.Connection.execute=execute
original_call=corpus_publish._call
def call(connection,request,*,lookup):
 started=time.monotonic()
 try:return original_call(connection,request,lookup=lookup)
 finally:record({'step':request['command'],'lookup':lookup,'batch_index':request.get('batch_index'),'seconds':round(time.monotonic()-started,3)})
corpus_publish._call=call
def timed(name):
 original=getattr(corpus_publish,name)
 def invoke(*args,**kwargs):
  started=time.monotonic()
  try:return original(*args,**kwargs)
  finally:record({'phase':name,'seconds':round(time.monotonic()-started,3)})
 return invoke
corpus_publish._prepare=timed('_prepare')
corpus_publish.audit_closed_attempt=timed('audit_closed_attempt')
"""


def test_native_capacity_inventory_projection_timing(native_database):
    admin,_=native_database
    inventory=[['Gen',1,1,'a'*64,20] for _ in range(50000)]
    request={'rows':[['Gen',1,1,'a'*64,[str(n) for n in range(1,21)]] for _ in range(1000)]}
    # Fixture-only microbenchmark of the observed generic PL/pgSQL projection;
    # this is not source, audit or publication proof.
    admin.execute('''CREATE FUNCTION scribeswell.capacity_projection_probe(inventory jsonb,request jsonb,cached boolean)
    RETURNS TABLE(seconds double precision,matched bigint) LANGUAGE plpgsql SET search_path=pg_catalog AS $$
    DECLARE started timestamptz=clock_timestamp();batch_length integer=jsonb_array_length(request->'rows');
    BEGIN
     IF cached THEN
      WITH expected AS MATERIALIZED(SELECT e.item,e.ordinal FROM jsonb_array_elements(inventory) WITH ORDINALITY e(item,ordinal)
       WHERE e.ordinal>0 AND e.ordinal<=batch_length) SELECT count(*) INTO matched FROM expected;
     ELSE
      WITH expected AS MATERIALIZED(SELECT e.item,e.ordinal FROM jsonb_array_elements(inventory) WITH ORDINALITY e(item,ordinal)
       WHERE e.ordinal>0 AND e.ordinal<=jsonb_array_length(request->'rows')) SELECT count(*) INTO matched FROM expected;
     END IF;
     seconds=EXTRACT(EPOCH FROM clock_timestamp()-started);RETURN NEXT;
    END $$''')
    before=admin.execute('SELECT * FROM scribeswell.capacity_projection_probe(%s,%s,false)',(Jsonb(inventory),Jsonb(request))).fetchone()
    after=admin.execute('SELECT * FROM scribeswell.capacity_projection_probe(%s,%s,true)',(Jsonb(inventory),Jsonb(request))).fetchone()
    assert before[1]==after[1]==1000
    print('INVENTORY_PROJECTION_TIMING',json.dumps({'inventory_rows':50000,'batch_rows':1000,'uncached_seconds':before[0],'cached_seconds':after[0]},sort_keys=True),flush=True)



def profile_capacity_insert(admin,revision):
    """Safe fixture-only EXPLAIN summary; roll back every diagnostic append."""
    index=admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_batch WHERE source_revision=%s',(revision,)).fetchone()[0]
    header=admin.execute('SELECT header FROM scribeswell.corpus_manifest_header WHERE source_revision=%s',(revision,)).fetchone()[0]
    if index>=header['batch_count']:return
    rows=admin.execute("""SELECT jsonb_agg(jsonb_build_array(r.book,r.chapter,r.verse,r.digest,r.ids) ORDER BY r.ordinal)
     FROM(SELECT e.ordinal,e.item->>0 AS book,(e.item->>1)::integer AS chapter,(e.item->>2)::integer AS verse,e.item->>3 AS digest,
      jsonb_agg(w.id::text ORDER BY w.position) AS ids
      FROM scribeswell.corpus_manifest_header h CROSS JOIN LATERAL jsonb_array_elements(h.header->'inventory') WITH ORDINALITY e(item,ordinal)
      JOIN scribeswell.book b ON b.osis_id=e.item->>0
      JOIN scribeswell.verse v ON v.book_id=b.id AND v.chapter_num=(e.item->>1)::integer AND v.verse_num=(e.item->>2)::integer
      JOIN scribeswell.word w ON w.verse_id=v.id
      WHERE h.source_revision=%s AND e.ordinal>%s AND e.ordinal<=%s
      GROUP BY e.ordinal,e.item) r""",(revision,index*1000,(index+1)*1000)).fetchone()[0]
    class RollbackProbe(Exception):pass
    before=admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_word_identity WHERE source_revision=%s',(revision,)).fetchone()[0]
    with pytest.raises(RollbackProbe):
        with admin.transaction():
            admin.execute("SET LOCAL statement_timeout='5s'")
            admin.execute('INSERT INTO scribeswell.corpus_manifest_batch(source_revision,batch_index,first_ordinal,rows,created_by_actor_id) VALUES(%s,%s,%s,%s,%s)',(revision,index,index*1000,Jsonb(rows),ACTOR))
            admin.execute('INSERT INTO scribeswell.corpus_manifest_verse(source_revision,ordinal,batch_index,book,chapter,verse,verse_token_digest,word_ids,created_by_actor_id) SELECT %s,%s+n::int-1,%s,r->>0,(r->>1)::int,(r->>2)::int,r->>3,r->4,%s FROM jsonb_array_elements(%s::jsonb) WITH ORDINALITY e(r,n)',(revision,index*1000,index,ACTOR,Jsonb(rows)))
            explained=admin.execute('EXPLAIN(ANALYZE,FORMAT JSON) INSERT INTO scribeswell.corpus_manifest_word_identity(source_revision,ordinal,position,word_id,created_by_actor_id) SELECT %s,%s+n::int-1,p::int,id::bigint,%s FROM jsonb_array_elements(%s::jsonb) WITH ORDINALITY e(r,n) CROSS JOIN LATERAL jsonb_array_elements_text(r->4) WITH ORDINALITY w(id,p)',(revision,index*1000,ACTOR,Jsonb(rows))).fetchone()[0][0]
            summary={'execution_ms':explained['Execution Time'],'triggers':[{k:entry.get(k) for k in ('Trigger Name','Constraint Name','Relation','Time','Calls')} for entry in explained.get('Triggers',[])]}
            print('CAPACITY_WORD_INSERT_PROFILE',json.dumps(summary,sort_keys=True),flush=True)
            raise RollbackProbe()
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_word_identity WHERE source_revision=%s',(revision,)).fetchone()[0]==before



def test_native_capacity_compactor_matches_historical_bytes_and_python_oracle(closed,monkeypatch):
    admin,url,_,_=closed
    nested='deep'
    for _ in range(16):nested=[nested]
    cases=[[],['שלום','line\nbreak','x,y : z','quote"backslash\\',' \t\n\r'],['\u2028\u2029','e\u0301','🪶',0,-1,9223372036854775807,[],['[]{}','1e3']],nested]
    expected=[json.dumps(value,ensure_ascii=False,separators=(',',':')) for value in cases]
    previous=[admin.execute('SELECT scribeswell.corpus_manifest_compact(%s)',(Jsonb(value),)).fetchone()[0] for value in cases]
    assert previous==expected
    header=['scribeswell.manifest.v1','auditor-v1','source,\n"\\','קטלוג','v','t','a'*64,'revision','actor','attempt','1']
    rows=[['אב \" \\ , space',1,2,'a'*64,['1',42,9223372036854775807]],['Gen',3,4,'b'*64,['line\nbreak','quote"backslash\\','e\u0301','comma, space','🪶']]]
    payload=[*header,rows];payload_expected=json.dumps(payload,ensure_ascii=False,separators=(',',':'))
    payload_previous=admin.execute('SELECT scribeswell.corpus_manifest_compact(%s)',(Jsonb(payload),)).fetchone()[0]
    assert payload_previous==payload_expected
    upgrade(url,monkeypatch,CUSTODY,capacity=True)
    stage,batch,_,_=planned_requests(closed,monkeypatch);execute_requests(url,[stage])
    batch=deepcopy(batch);batch['rows']=rows
    # Owner-only partial rows exercise the formatter's scalar escaping; they are
    # not a qualified catalogue/word-ID inventory and are never completed/published.
    insert_batch_evidence_formatter(admin,batch)
    encoded_rows=admin.execute('SELECT scribeswell.corpus_manifest_rows_compact(%s)',(stage['source_revision'],)).fetchone()[0]
    encoded_prefix=admin.execute('SELECT scribeswell.corpus_manifest_compact(%s)',(Jsonb(header),)).fetchone()[0]
    payload_actual=encoded_prefix[:-1]+','+encoded_rows+']'
    assert payload_actual==payload_previous==payload_expected
    assert_unpublished(admin)
    assert hashlib.sha256(payload_actual.encode()).hexdigest()==hashlib.sha256(payload_expected.encode()).hexdigest()
    actual=[admin.execute('SELECT scribeswell.corpus_manifest_compact(%s)',(Jsonb(value),)).fetchone()[0] for value in cases]
    assert actual==previous==expected
    assert [hashlib.sha256(value.encode()).hexdigest() for value in actual]==[hashlib.sha256(value.encode()).hexdigest() for value in expected]
    for invalid in [{},True,False,None,[[],None],[1,{'x':'y'}],['x',True]]:
        with pytest.raises(psycopg.Error) as failure:admin.execute('SELECT scribeswell.corpus_manifest_compact(%s)',(Jsonb(invalid),))
        assert failure.value.sqlstate=='22023' and failure.value.diag.message_primary=='corpus_publish.input_invalid'



def insert_batch_evidence_formatter(admin,request):
    revision=request['source_revision']
    admin.execute('INSERT INTO scribeswell.corpus_manifest_batch(source_revision,batch_index,first_ordinal,rows,created_by_actor_id) VALUES(%s,0,0,%s,%s)',(revision,Jsonb(request['rows']),ACTOR))
    for ordinal,row in enumerate(request['rows']):
        admin.execute('INSERT INTO scribeswell.corpus_manifest_verse(source_revision,ordinal,batch_index,book,chapter,verse,verse_token_digest,word_ids,created_by_actor_id) VALUES(%s,%s,0,%s,%s,%s,%s,%s,%s)',(revision,ordinal,*row[:4],Jsonb(row[4]),ACTOR))


@pytest.mark.parametrize('inconsistency',['rows','index','offset'])
def test_native_capacity_completion_rejects_inconsistent_normalized_batches(closed,monkeypatch,inconsistency):
    _,url,_,_=closed;upgrade(url,monkeypatch,CUSTODY,capacity=True)
    test_native_completion_rejects_complete_inconsistent_batch_evidence(closed,monkeypatch,inconsistency)


def test_native_capacity_digest_and_partial_completion_guards(closed,monkeypatch):
    _,url,_,_=closed;upgrade(url,monkeypatch,CUSTODY,capacity=True)
    test_native_full_digest_rejection_after_structurally_valid_batches(closed,monkeypatch)


@pytest.mark.parametrize('invalid',['0','01','9223372036854775808','1\n',1,True,None,[]])
def test_native_capacity_batch_id_validation_is_atomic_and_original_operation_retries(closed,monkeypatch,invalid):
    admin,url,_,_=closed;upgrade(url,monkeypatch,CUSTODY,capacity=True)
    stage,batch,_,_=planned_requests(closed,monkeypatch);execute_requests(url,[stage])
    changed=deepcopy(batch);changed['rows'][0][4][0]=invalid
    with operator(url) as connection:
        with pytest.raises(PublishError,match='input_invalid'):corpus_publish._acknowledge(connection,changed)
        assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_batch').fetchone()==(0,)
        assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_verse').fetchone()==(0,)
        assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_word_identity').fetchone()==(0,)
        original=corpus_publish._acknowledge(connection,batch)
        assert original==corpus_publish._acknowledge(connection,batch)
    assert admin.execute('SELECT count(*) FROM scribeswell.corpus_manifest_verse').fetchone()==(39,)
    assert_unpublished(admin)


@pytest.mark.parametrize('append_kind',['batch','verse','word_identity'])
def test_native_capacity_concurrent_alternate_appends_both_finish(closed,monkeypatch,append_kind):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    admin,url,_,_=closed;upgrade(url,monkeypatch,CUSTODY,capacity=True)
    stage,batch,_,_=planned_requests(closed,monkeypatch);execute_requests(url,[stage,batch])
    revision=stage['source_revision'];ready=Barrier(2)
    def append(position):
        with psycopg.connect(url) as db:
            db.execute("SET statement_timeout='8s'")
            # These compatible locks are acquired by the header FK before the
            # AFTER STATEMENT guard in alternate INSERT statements as well.
            db.execute('SELECT source_revision FROM scribeswell.corpus_manifest_header WHERE source_revision=%s FOR KEY SHARE',(revision,))
            ready.wait(timeout=5)
            row=batch['rows'][0]
            statement,parameters={
                'batch':('INSERT INTO scribeswell.corpus_manifest_batch(source_revision,batch_index,first_ordinal,rows,created_by_actor_id) VALUES(%s,%s,%s,%s,%s)',(revision,position,37+position,Jsonb([row]),ACTOR)),
                'verse':('INSERT INTO scribeswell.corpus_manifest_verse(source_revision,ordinal,batch_index,book,chapter,verse,verse_token_digest,word_ids,created_by_actor_id) VALUES(%s,%s,0,\'Gen\',2,%s,%s,%s,%s)',(revision,37+position,position,row[3],Jsonb([str(998+position)]),ACTOR)),
                'word_identity':('INSERT INTO scribeswell.corpus_manifest_word_identity(source_revision,ordinal,position,word_id,created_by_actor_id) VALUES(%s,0,%s,%s,%s)',(revision,position,998+position,ACTOR))}[append_kind]
            db.execute(statement,parameters)
        return position
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(append,i) for i in (2,3)]
        assert [f.result(timeout=12) for f in futures]==[2,3]
    table='corpus_manifest_'+append_kind
    expected=3 if append_kind=='batch' else 41
    assert admin.execute('SELECT count(*) FROM scribeswell.'+table+' WHERE source_revision=%s',(revision,)).fetchone()==(expected,)
    assert_unpublished(admin)


def test_native_capacity_batch_wrong_digest_atomic_refusal_and_original_retry(closed,monkeypatch):
    admin,url,_,_=closed;upgrade(url,monkeypatch,CUSTODY,capacity=True)
    stage,batch,_,_=planned_requests(closed,monkeypatch);execute_requests(url,[stage])
    changed=deepcopy(batch);changed['rows'][0][3]='f'*64 if batch['rows'][0][3]!='f'*64 else 'e'*64
    before=admin.execute('SELECT count(*) FROM scribeswell.corpus_publication_outcome').fetchone()
    with operator(url) as connection:
        with pytest.raises(PublishError,match='conflict'):corpus_publish._acknowledge(connection,changed)
        for table in ('corpus_manifest_batch','corpus_manifest_verse','corpus_manifest_word_identity'):
            assert admin.execute('SELECT count(*) FROM scribeswell.'+table).fetchone()==(0,)
        assert admin.execute('SELECT count(*) FROM scribeswell.corpus_publication_outcome').fetchone()==before
        original=corpus_publish._acknowledge(connection,batch)
        assert original==corpus_publish._acknowledge(connection,batch)
    assert_unpublished(admin)
