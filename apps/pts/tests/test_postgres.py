"""Run only against the explicitly configured disposable PostgreSQL database."""
import json
import os
from pathlib import Path
import uuid
import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from apps.pts.backend.db import engine,scoped,load
from apps.pts.tools.import_library import import_library

ORG='11111111-1111-1111-1111-111111111111'
OTHER='22222222-2222-2222-2222-222222222222'
ACTOR='33333333-3333-3333-3333-333333333333'

@pytest.fixture
def db():
    return engine(os.environ['PTS_TEST_DATABASE_URL'])


def test_actual_restricted_roles_import_replay_conflict_rls(db):
    library=json.loads((Path(__file__).parents[1]/'reference/poetry-library/library.json').read_text())
    with scoped(db,ORG,'service:pts-import') as c:
        c.execute(text('SET LOCAL ROLE pts_import'))
        first=import_library(c,library)
        replay=import_library(c,library)
        assert replay['replayed'] and replay['inserted']==0
        assert load(c)==library
    changed=json.loads(json.dumps(library)); changed['poems'][0]['text']='incoming reviewed change'
    with scoped(db,ORG,'service:pts-import') as c:
        c.execute(text('SET LOCAL ROLE pts_import'))
        conflict=import_library(c,changed)
        assert conflict['conflicts']==1
        assert load(c)['poems'][0]['text']==library['poems'][0]['text']
        assert c.execute(text('SELECT incoming FROM pts.conflicts WHERE record_id=\'SWA-001\'')).scalar()['text']=='incoming reviewed change'
    with scoped(db,ORG,ACTOR) as c:
        c.execute(text('SET LOCAL ROLE pts_runtime'))
        assert len(load(c)['poems'])==312
    with scoped(db,OTHER,ACTOR) as c:
        c.execute(text('SET LOCAL ROLE pts_runtime'))
        assert load(c)['poems']==[]
    with db.begin() as c:
        c.execute(text('SET LOCAL ROLE pts_runtime'))
        assert c.execute(text('SELECT count(*) FROM pts.poems')).scalar()==0
    for forbidden in ['CREATE TABLE pts.bad(id integer)','SELECT * FROM access.grants','UPDATE pts.poems SET payload=\'{}\'','SET ROLE pts_migrator']:
        # Separate actual login below tests escalation; SET LOCAL ROLE on admin could assume owner.
        if forbidden.startswith('SET ROLE'): continue
        with pytest.raises(DBAPIError):
            with scoped(db,ORG,ACTOR) as c:
                c.execute(text('SET LOCAL ROLE pts_runtime'));c.execute(text(forbidden))


def test_runtime_login_cannot_assume_privileged_role():
    runtime=engine(os.environ['PTS_TEST_RUNTIME_URL'])
    with pytest.raises(DBAPIError):
        with runtime.begin() as c: c.execute(text('SET ROLE pts_migrator'))
    with pytest.raises(RuntimeError):
        with scoped(runtime,ORG,ACTOR) as c:
            assert c.execute(text('SELECT count(*) FROM pts.poems')).scalar()==312
            raise RuntimeError('rollback')
    with runtime.begin() as c:
        assert c.execute(text('SELECT count(*) FROM pts.poems')).scalar()==0


def test_concurrent_scope_and_alternate_write_integrity():
    from concurrent.futures import ThreadPoolExecutor
    runtime=engine(os.environ['PTS_TEST_RUNTIME_URL'])
    def count(org):
        with scoped(runtime,org,ACTOR) as c:return c.execute(text('SELECT count(*) FROM pts.poems')).scalar_one()
    with ThreadPoolExecutor(max_workers=4) as executor:
        assert list(executor.map(count,[ORG,OTHER,ORG,OTHER]))==[312,0,312,0]
    importer=engine(os.environ['PTS_TEST_RUNTIME_URL'].replace('pts_runtime:','pts_import:'))
    with pytest.raises(DBAPIError):
        with scoped(importer,ORG,'service:pts-import') as c:
            c.execute(text("INSERT INTO pts.witnesses(org_id,id,payload,ordinal) VALUES(:org,'BAD-TEST','{\"id\":\"BAD-TEST\",\"source_id\":\"missing\",\"poem_id\":\"SWA-001\"}',0)"),{'org':ORG})
    content=engine(os.environ['PTS_TEST_RUNTIME_URL'].replace('pts_runtime:','content_runtime:'))
    test_id=str(uuid.uuid4())
    with scoped(content,ORG,'service:pts-import') as c:
        c.execute(text("INSERT INTO content.objects(org_id,id,sha256,size,media_type,state) VALUES(:org,:id,:sha,1,'text/plain','ready')"),{'org':ORG,'id':test_id,'sha':uuid.uuid4().hex+uuid.uuid4().hex})
    with pytest.raises(DBAPIError):
        with scoped(content,ORG,'service:pts-import') as c:
            c.execute(text("UPDATE content.objects SET sha256=repeat('a',64) WHERE id=:id"),{'id':test_id})


def test_conflicting_document_cannot_upload_or_attach(monkeypatch):
    from apps.pts.tools import upload_sources
    importer=engine(os.environ['PTS_TEST_RUNTIME_URL'].replace('pts_runtime:','pts_import:'))
    library=json.loads((Path(__file__).parents[1]/'reference/poetry-library/library.json').read_text())
    doc=dict(next(d for d in library['source_documents'] if d.get('local_path')))
    doc['sha256']='0'*64
    monkeypatch.setattr(upload_sources,'upload',lambda *args:pytest.fail('conflict must fail before external upload'))
    with pytest.raises(ValueError,match='differs from retained'):
        upload_sources.attach_document(importer,ORG,doc,Path('.'),None)


def test_collection_read_uses_one_snapshot(db):
    org=str(uuid.uuid4())
    library=json.loads((Path(__file__).parents[1]/'reference/poetry-library/library.json').read_text())
    with scoped(db,org,ACTOR,consistent=True) as reader:
        reader.execute(text('SET LOCAL ROLE pts_runtime'))
        assert reader.execute(text('SELECT count(*) FROM pts.sources')).scalar()==0
        with scoped(db,org,'service:pts-import') as writer:
            writer.execute(text('SET LOCAL ROLE pts_import'))
            import_library(writer,library)
        assert load(reader)['poems']==[]
    with scoped(db,org,ACTOR,consistent=True) as reader:
        reader.execute(text('SET LOCAL ROLE pts_runtime'))
        assert len(load(reader)['poems'])==312
