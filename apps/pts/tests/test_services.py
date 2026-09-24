import importlib.util
import io
import hashlib
import os
from pathlib import Path
import sys
import uuid
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import text
from apps.pts.backend.db import engine,scoped

ROOT=Path(__file__).resolve().parents[3]
ORG='11111111-1111-1111-1111-111111111111'
ACTOR='33333333-3333-3333-3333-333333333333'

def module(name,folder,file='main.py'):
    sys.path.insert(0,str(ROOT/folder))
    spec=importlib.util.spec_from_file_location(name,ROOT/folder/file)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def test_current_access_membership_grant_revocation(monkeypatch):
    db=engine(os.environ['PTS_TEST_DATABASE_URL'])
    runtime=engine(os.environ['PTS_TEST_DATABASE_URL'].replace('postgres:pts-disposable','access_runtime:pts-disposable'))
    monkeypatch.setenv('PTS_SERVICE_KEY','pts-test')
    with scoped(db,ORG,ACTOR) as c:
        c.execute(text('INSERT INTO identity.org(id) VALUES(:org) ON CONFLICT DO NOTHING'),{'org':ORG})
        c.execute(text('DELETE FROM identity.org_member WHERE org_id=:org'),{'org':ORG})
        c.execute(text('INSERT INTO identity.org_member(org_id,user_id) VALUES(:org,:actor)'),{'org':ORG,'actor':ACTOR})
        c.execute(text('DELETE FROM access.grants WHERE org_id=:org'),{'org':ORG})
    access=module('access_test','services/access')
    client=TestClient(access.create_app(db=runtime,authenticate=lambda token:uuid.UUID(ACTOR)))
    headers={'X-Service-Key':'pts-test','Authorization':'Bearer admin-claims-ignored'}
    body={'org_id':ORG,'permission':'pts.poetry.read'}
    assert client.post('/v1/check',json=body,headers=headers).status_code==403
    with scoped(db,ORG,ACTOR) as c:
        c.execute(text("INSERT INTO access.grants(org_id,id,user_id,permission) VALUES(:org,:id,:actor,'pts.poetry.read')"),{'org':ORG,'id':str(uuid.uuid4()),'actor':ACTOR})
    assert client.post('/v1/check',json=body,headers=headers).status_code==200
    assert client.post('/v1/check',json={**body,'org_id':str(uuid.uuid4())},headers=headers).status_code==403
    with scoped(db,ORG,ACTOR) as c:c.execute(text('UPDATE identity.org_member SET deleted_at=clock_timestamp() WHERE org_id=:org'),{'org':ORG})
    assert client.post('/v1/check',json=body,headers=headers).status_code==403


class Provider:
    def __init__(self):self.sealed={};self.staging=b'original'
    def upload(self,key,media_type):return 'https://storage.invalid/staging-only'
    def seal(self,staging,sealed,sha,size):
        if sealed not in self.sealed:self.sealed[sealed]=self.staging
        assert hashlib.sha256(self.sealed[sealed]).hexdigest()==sha
        assert len(self.sealed[sealed])==size
    def read(self,key):return 'https://storage.invalid/'+key


def test_content_idempotency_scope_and_current_reads(monkeypatch):
    db=engine(os.environ['PTS_TEST_DATABASE_URL'].replace('postgres:pts-disposable','content_runtime:pts-disposable'))
    for k,v in {'PTS_IMPORT_ORG_ID':ORG,'PTS_IMPORT_SERVICE_KEY':'import-test','PTS_SERVICE_KEY':'pts-test'}.items():monkeypatch.setenv(k,v)
    content=module('content_test','services/content-service');provider=Provider()
    allowed=[True]
    def verify(token,org):
        if not allowed[0]:raise HTTPException(403,{'code':'access_denied'})
        return ACTOR
    client=TestClient(content.create_app(db=db,storage=provider,verify=verify))
    headers={'X-Org-ID':ORG,'X-Service-Key':'import-test'}
    body={'sha256':hashlib.sha256(b'original').hexdigest(),'size':8,'media_type':'application/pdf'}
    first=client.post('/v1/objects',json=body,headers=headers)
    assert first.status_code==200
    identity=first.json()['content_id']
    again=client.post('/v1/objects',json=body,headers=headers).json()
    assert again['content_id']==identity
    assert client.post('/v1/objects',json=body,headers={**headers,'X-Org-ID':str(uuid.uuid4())}).status_code==403
    assert client.post('/v1/objects/'+identity+'/finalize',headers=headers).json()['state']=='ready'
    provider.staging=b'replayed malicious replacement'
    assert client.post('/v1/objects/'+identity+'/finalize',headers=headers).json()['state']=='ready'
    read_headers={**headers,'X-Service-Key':'pts-test','Authorization':'Bearer current'}
    result=client.post('/v1/objects/'+identity+'/read',headers=read_headers)
    assert result.status_code==200 and result.json()['expires_in']==300
    assert '/sealed/' in result.json()['url']
    allowed[0]=False
    assert client.post('/v1/objects/'+identity+'/read',headers=read_headers).status_code==403


def test_s3_sealed_identity_ignores_replayed_staging():
    mod=module('content_provider_test','services/content-service','provider.py')
    class S3:
        objects={'sealed':b'original','staging':b'replayed replacement'}
        def head_object(self,**kw):return {}
        def get_object(self,**kw):
            data=self.objects[kw['Key']];return {'Body':io.BytesIO(data),'ContentLength':len(data)}
        def copy_object(self,**kw):raise AssertionError('must never overwrite existing sealed bytes')
    adapter=object.__new__(mod.Storage);adapter.client=S3();adapter.bucket='private'
    adapter.seal('staging','sealed',hashlib.sha256(b'original').hexdigest(),8)


def test_stored_document_through_pts_and_real_content_client(monkeypatch):
    from apps.pts.backend.main import create_app,Repository
    from apps.pts.backend.clients import ContentClient
    from apps.pts.tests.test_api import Access
    admin=engine(os.environ['PTS_TEST_DATABASE_URL'])
    runtime=engine(os.environ['PTS_TEST_DATABASE_URL'].replace('postgres:pts-disposable','pts_runtime:pts-disposable'))
    content_db=engine(os.environ['PTS_TEST_DATABASE_URL'].replace('postgres:pts-disposable','content_runtime:pts-disposable'))
    monkeypatch.setenv('PTS_SERVICE_KEY','pts-test')
    content=module('content_integration_test','services/content-service')
    allowed=[True]
    def verify(token,org):
        assert token=='Bearer current' and str(org)==ORG
        if not allowed[0]:raise HTTPException(403,{'code':'access_denied'})
        return ACTOR
    content_client=TestClient(content.create_app(db=content_db,storage=Provider(),verify=verify))
    content_id=str(uuid.uuid4())
    with scoped(admin,ORG,ACTOR) as c:
        c.execute(text("INSERT INTO content.objects(org_id,id,sha256,size,media_type,state) VALUES(:org,:id,:sha,8,'application/pdf','ready')"),{'org':ORG,'id':content_id,'sha':uuid.uuid4().hex+uuid.uuid4().hex})
        c.execute(text("INSERT INTO pts.attachments(org_id,id,document_id,content_id) VALUES(:org,'DOC-VELTEN','DOC-VELTEN',:content) ON CONFLICT(org_id,id) DO UPDATE SET content_id=excluded.content_id"),{'org':ORG,'content':content_id})
    import httpx
    monkeypatch.setattr(httpx,'post',lambda url,**kwargs:content_client.post(url.removeprefix('http://content.test'),headers=kwargs['headers']))
    pts=TestClient(create_app(access=Access(),repository=Repository(runtime),content=ContentClient('http://content.test','pts-test')))
    headers={'Authorization':'Bearer current','X-Org-ID':ORG}
    response=pts.get('/api/documents/DOC-VELTEN',headers=headers)
    assert response.status_code==200 and response.json()['expires_in']==300
    assert content_id in response.json()['url']
    allowed[0]=False
    assert pts.get('/api/documents/DOC-VELTEN',headers=headers).status_code==403


def test_finalized_audit_is_atomic_and_failed_identity_can_be_replaced(monkeypatch):
    admin=engine(os.environ['PTS_TEST_DATABASE_URL'])
    content_db=engine(os.environ['PTS_TEST_DATABASE_URL'].replace('postgres:pts-disposable','content_runtime:pts-disposable'))
    for key,value in {'PTS_IMPORT_ORG_ID':ORG,'PTS_IMPORT_SERVICE_KEY':'import-test'}.items():monkeypatch.setenv(key,value)
    content=module('content_atomic_test','services/content-service')
    provider=Provider();provider.staging=uuid.uuid4().bytes
    client=TestClient(content.create_app(db=content_db,storage=provider))
    headers={'X-Org-ID':ORG,'X-Service-Key':'import-test'}
    body={'sha256':hashlib.sha256(provider.staging).hexdigest(),'size':16,'media_type':'application/pdf'}
    identity=client.post('/v1/objects',json=body,headers=headers).json()['content_id']
    # Revoke audit INSERT to make completion's audit fail after sealing.
    with admin.begin() as c:c.execute(text('REVOKE INSERT ON content.events FROM content_runtime'))
    try:
        assert client.post('/v1/objects/'+identity+'/finalize',headers=headers).status_code==503
    finally:
        with admin.begin() as c:c.execute(text('GRANT INSERT ON content.events TO content_runtime'))
    with scoped(admin,ORG,ACTOR) as c:
        assert c.execute(text('SELECT state FROM content.objects WHERE id=:id'),{'id':identity}).scalar()=='finalizing'
    recovery=module('content_recovery_test','services/content-service','recover_failed.py')
    owner=engine(os.environ['PTS_TEST_DATABASE_URL'].replace('postgres:pts-disposable','content_migrator:pts-disposable'))
    with owner.begin() as c:recovery.abandon(c,uuid.UUID(ORG),uuid.UUID(identity),'test:recovery')
    replacement=client.post('/v1/objects',json=body,headers=headers).json()['content_id']
    assert replacement!=identity
    assert client.post('/v1/objects/'+replacement+'/finalize',headers=headers).json()['state']=='ready'
    with scoped(admin,ORG,ACTOR) as c:
        assert c.execute(text("SELECT count(*) FROM content.events WHERE content_id=:id AND operation='finalized'"),{'id':replacement}).scalar()==1
        assert c.execute(text('SELECT state FROM content.objects WHERE id=:id'),{'id':identity}).scalar()=='failed'
