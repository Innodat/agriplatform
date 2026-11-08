"""Boundary checks; provider/native-browser evidence is recorded separately."""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime,timedelta,timezone
import hashlib
from uuid import uuid4
import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from apps.pts.backend.main import create_app
from apps.pts.backend.clients import CurrentSessionClient
from apps.pts.backend.private_stream import ContentClient,Capacity
from apps.pts.tests.test_account_adoption import AccountAccess,AccountRepo,ACCOUNT,ACTOR

SESSION='55555555-5555-4555-8555-555555555555'
FILE='https://files.pts.fixture.test'
FRONTEND='https://pts.fixture.test'
ENV={'PTS_FILE_ORIGIN':FILE,'PTS_FILE_FRONTEND_ORIGIN':FRONTEND,'PTS_CORS_ORIGINS':FRONTEND}
CONTENT=str(uuid4())
PDF=b'%PDF-1.7\n'+b'a'*4096
ETAG='"'+hashlib.sha256(PDF).hexdigest()+'"'

class Sessions:
    account=ACCOUNT;session=SESSION;active=True;outage=False
    async def verify(self,authorization):
        if self.outage:raise HTTPException(503,{'code':'identity.current_session_unavailable'})
        if not self.active or authorization!='Bearer current':raise HTTPException(401,{'code':'authentication_required'})
        expires=datetime.now(timezone.utc)+timedelta(minutes=10)
        return dict(account_id=self.account,session_id=self.session,credential_expires_at=expires.isoformat(),expires_at=expires)
    async def prepare_cleanup(self,authorization):return await self.verify(authorization)
    async def cleanup(self,authorization):
        if self.outage:raise HTTPException(503,{'code':'identity.current_session_unavailable'})
        if authorization!='Bearer current':raise HTTPException(401,{'code':'authentication_required'})
        return dict(account_id=self.account,session_id=self.session,provider_session='present' if self.active else 'absent')

class Files(AccountRepo):
    def __init__(self):super().__init__();self.contexts={}
    def attachment(self,actor,document):return CONTENT if document=='DOC-VELTEN' else None
    def create_file_context(self,session,actor,document,presentation):
        identity=uuid4();self.contexts[str(identity)]={**session,'document_id':document,'presentation':presentation};return identity
    def file_context(self,session,identity):
        value=self.contexts.get(str(identity))
        return value if value and all(value[k]==session[k] for k in ('account_id','session_id')) else None
    def clear_file_contexts(self,session):
        self.contexts={key:value for key,value in self.contexts.items() if value['account_id']!=session['account_id'] or value['session_id']!=session['session_id']}

class ByteStream(httpx.AsyncByteStream):
    def __init__(self,data):self.data=data;self.closed=False
    async def __aiter__(self):yield self.data
    async def aclose(self):self.closed=True

class Content:
    def __init__(self):self.calls=[];self.streams=[]
    @asynccontextmanager
    async def read(self,identity,**kwargs):
        self.calls.append((identity,kwargs));data=PDF;status=200;extra={}
        if kwargs['range_header'] and kwargs['method']!='HEAD' and kwargs['if_range'] in (None,ETAG):
            if kwargs['range_header']=='bytes=0-8':data=data[:9];status=206;extra={'Content-Range':f'bytes 0-8/{len(PDF)}'}
            elif kwargs['range_header']=='bytes=-9':data=data[-9:];status=206;extra={'Content-Range':f'bytes {len(PDF)-9}-{len(PDF)-1}/{len(PDF)}'}
            else:raise HTTPException(416,{'code':'content.range_not_satisfiable'})
        stream=ByteStream(data);self.streams.append(stream)
        response=httpx.Response(status,headers={'Content-Type':'application/pdf','Content-Length':str(len(data)),'ETag':ETAG,'Accept-Ranges':'bytes',**extra},stream=stream)
        try:yield response
        finally:await response.aclose()

def fixture():
    sessions=Sessions();access=AccountAccess();access.allowed.add('pts.poetry.documents');files=Files();content=Content()
    app=create_app(access=access,repository=files,content=content,sessions=sessions,environment=ENV)
    return TestClient(app,base_url=FILE),sessions,access,files,content

def establish(client):
    result=client.post('/api/file-session',headers={'Origin':FRONTEND,'Authorization':'Bearer current'})
    assert result.status_code==200
    return result

def context(client,presentation='open'):
    result=client.post('/api/file-contexts/DOC-VELTEN?presentation='+presentation,headers={'Origin':FRONTEND,'Authorization':'Bearer current'})
    assert result.status_code==200
    return result.json()['url']

def test_cookie_setup_is_exact_origin_bearer_only_and_host_isolated():
    client,_,_,_,content=fixture()
    for headers in ({'Origin':'https://evil.test','Authorization':'Bearer current'},{'Origin':FRONTEND},{'Authorization':'Bearer current'}):
        assert client.post('/api/file-session',headers=headers).status_code in (401,403)
    assert client.post('/api/file-session',headers={'Origin':FRONTEND,'Authorization':'Bearer current'},json={'account_id':ACCOUNT}).status_code==422
    response=establish(client);cookie=response.headers['set-cookie']
    assert '__Host-pts-file=current' in cookie and 'Secure' in cookie and 'HttpOnly' in cookie and 'SameSite=lax' in cookie and 'Domain' not in cookie
    assert client.get('https://other.pts.fixture.test/api/files/'+str(uuid4())).status_code==403
    assert not content.calls

def test_native_pdf_download_head_range_and_current_rechecks_before_metadata():
    client,sessions,access,files,content=fixture();establish(client);url=context(client)
    response=client.get(url)
    assert response.status_code==200 and response.content==PDF
    assert response.headers['content-disposition'].startswith('inline;')
    assert response.headers['cache-control']=='private, no-store'
    assert client.get(url,headers={'Range':'bytes=0-8','If-Range':ETAG}).content==PDF[:9]
    assert client.get(url,headers={'Range':'bytes=-9'}).status_code==206
    assert client.get(url,headers={'Range':'bytes=0-8','If-Range':'"different"'}).content==PDF
    assert client.get(url,headers={'Range':'bytes=999999-'}).status_code==416
    head=client.head(url);assert head.status_code==200 and head.content==b'' and int(head.headers['content-length'])==len(PDF)
    download=client.get(context(client,'download'));assert download.headers['content-disposition'].startswith('attachment;')
    assert all(stream.closed for stream in content.streams)
    for method in ('get','head'):
        access.allowed.remove('pts.poetry.documents');before=len(content.calls)
        denied=getattr(client,method)(url,headers={'Range':'bytes=0-8'})
        assert denied.status_code==403 and 'content-range' not in denied.headers and len(content.calls)==before
        access.allowed.add('pts.poetry.documents')
    sessions.outage=True;assert client.head(url).status_code==503
    sessions.outage=False;sessions.active=False
    assert client.get(url).status_code==401
    assert client.get('/api/documents/DOC-VELTEN',headers={'Authorization':'Bearer current'}).status_code==401
    assert client.post('/api/file-session',headers={'Origin':FRONTEND,'Authorization':'Bearer current'}).status_code==401

def test_context_is_not_authority_and_logout_invalidation_prevents_reuse():
    client,sessions,access,files,content=fixture();establish(client);url=context(client)
    client.cookies.clear();assert client.get(url).status_code==401
    establish(client);sessions.session=str(uuid4())
    assert client.get(url).status_code==404
    sessions.session=SESSION
    assert client.post('/api/file-session/clear',headers={'Origin':FRONTEND,'Authorization':'Bearer current'}).status_code==200
    establish(client);assert client.get(url).status_code==404
    assert client.app.state.file_capacity.active==0

def test_capacity_enforces_two_per_account_and_sixteen_total_with_release():
    capacity=Capacity();held=[]
    for index in range(8):held.extend([capacity.acquire(str(index)),capacity.acquire(str(index))])
    with pytest.raises(HTTPException) as rejected:capacity.acquire('ninth')
    assert rejected.value.status_code==429
    held.pop()();held.pop()()
    with pytest.raises(HTTPException):capacity.acquire('0')
    for release in held:release();release()
    assert capacity.active==0 and capacity.accounts=={}

def test_identity_adapter_closed_evidence_and_outage_mapping():
    def handler(request):
        assert request.url.path=='/v2/identity/current-session' and request.content==b''
        return httpx.Response(200,json=dict(account_id=ACCOUNT,session_id=SESSION,credential_expires_at=(datetime.now(timezone.utc)+timedelta(minutes=1)).isoformat(),observed_at=datetime.now(timezone.utc).isoformat()))
    value=asyncio.run(CurrentSessionClient('http://identity.test','restricted',httpx.MockTransport(handler)).verify('Bearer current'))
    assert value['account_id']==ACCOUNT
    for status,wanted in ((401,401),(403,403),(500,503)):
        adapter=CurrentSessionClient('http://identity.test','restricted',httpx.MockTransport(lambda request:httpx.Response(status)))
        with pytest.raises(HTTPException) as failure:asyncio.run(adapter.verify('Bearer current'))
        assert failure.value.status_code==wanted

def test_private_head_errors_keep_safe_typed_code_and_existing_headers(monkeypatch):
    client,sessions,access,files,_=fixture();establish(client);url=context(client)
    sessions.outage=True
    response=client.head(url,headers={'Origin':FRONTEND})
    assert response.status_code==503 and response.content==b''
    assert response.headers['x-pts-error-code']=='identity.current_session_unavailable'
    assert 'X-PtS-Error-Code' in response.headers['access-control-expose-headers']
    assert response.headers['cache-control']=='private, no-store'
    assert 'content-range' not in response.headers and 'content-disposition' not in response.headers
    assert client.get(url).json()=={'detail':{'code':'identity.current_session_unavailable'}}
    sessions.outage=False;access.allowed.remove('pts.poetry.documents')
    assert client.head(url).headers['x-pts-error-code']=='access_denied'
    declaration=client.app.openapi()['paths']['/api/files/{context_id}']['head']['responses']['503']
    assert 'X-PtS-Error-Code' in declaration['headers']
    validation=client.head('/api/files/not-a-uuid')
    assert validation.status_code==422 and validation.content==b'' and validation.headers['x-pts-error-code']=='validation_failed'
    validation_get=client.get('/api/files/not-a-uuid')
    assert isinstance(validation_get.json()['detail'],list)
    assert 'X-PtS-Error-Code' in client.app.openapi()['paths']['/api/files/{context_id}']['head']['responses']['422']['headers']
    from sqlalchemy.exc import SQLAlchemyError
    def unavailable(*args):raise SQLAlchemyError('synthetic fixture database failure')
    access.allowed.add('pts.poetry.documents');monkeypatch.setattr(files,'file_context',unavailable)
    database=client.head(url)
    assert database.status_code==503 and database.content==b'' and database.headers['x-pts-error-code']=='collection_unavailable'
    assert client.get(url).json()=={'detail':{'code':'collection_unavailable'}}
