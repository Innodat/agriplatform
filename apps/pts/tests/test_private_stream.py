"""HTTP-only owner assertion, transport failure and owned resource teardown."""
import asyncio
from contextlib import asynccontextmanager
import hashlib
import http.client
import io
from uuid import uuid4
import httpx
import pytest
from fastapi import HTTPException
from starlette.requests import Request
from apps.pts.backend.private_stream import ContentClient,Capacity,prepare,BUFFER

ID=str(uuid4());ACCOUNT=str(uuid4());ACTOR=str(uuid4());OPERATION=str(uuid4())
HEADERS={'X-Content-ID':ID,'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff','ETag':'"'+'a'*64+'"','Content-Length':'3','Content-Type':'application/pdf'}


def test_bounded_native_http_reads_expose_truncated_length_without_always_raising():
    class Socket:
        def makefile(self,*args):
            return io.BytesIO(b'HTTP/1.1 200 OK\r\nContent-Length: 12\r\n\r\nabc')
    response=http.client.HTTPResponse(Socket());response.begin()
    assert response.read(8)==b'abc'
    assert response.read(8)==b''
    assert response.length==9


def test_content_http_assertion_is_application_owned_and_never_forwards_a_bearer():
    seen=[]
    def handler(request):
        seen.append(request)
        assert request.url.path=='/v2/objects/'+ID+'/bytes'
        assert dict(request.url.params)=={'application_id':'pts','kind':'application'}
        assert request.headers['x-initiator-account-id']==ACCOUNT and request.headers['x-initiator-actor-id']==ACTOR
        assert request.headers['x-operation-id']==OPERATION and request.headers['accept-encoding']=='identity'
        assert 'authorization' not in request.headers and 'x-org-id' not in request.headers
        return httpx.Response(200,headers=HEADERS,content=b'pdf')
    async def run():
        client=ContentClient('http://content.test','restricted',httpx.MockTransport(handler))
        async with client.read(ID,account_id=ACCOUNT,actor_id=ACTOR,operation_id=OPERATION) as response:
            assert await response.aread()==b'pdf'
    asyncio.run(run());assert len(seen)==1

@pytest.mark.parametrize('changed',[{'X-Content-ID':str(uuid4())},{'Cache-Control':'public'},{'ETag':'W/"weak"'},{'Content-Length':'unknown'},{'Content-Encoding':'gzip'}])
def test_foreign_identity_or_unsafe_representation_is_rejected_before_bytes(changed):
    async def run():
        client=ContentClient('http://content.test','restricted',httpx.MockTransport(lambda request:httpx.Response(200,headers={**HEADERS,**changed},content=b'pdf')))
        with pytest.raises(HTTPException) as failure:
            async with client.read(ID,account_id=ACCOUNT,actor_id=ACTOR,operation_id=OPERATION):pytest.fail('unsafe upstream escaped')
        assert failure.value.status_code==503
    asyncio.run(run())

class Failing(httpx.AsyncByteStream):
    def __init__(self,fail=True):self.fail=fail;self.closed=False
    async def __aiter__(self):
        yield b'a'*BUFFER;yield b'b'*BUFFER
        if self.fail:raise httpx.ReadError('synthetic upstream failed')
        yield b'c'*BUFFER
    async def aclose(self):self.closed=True

class Client:
    def __init__(self,stream):self.stream=stream
    @asynccontextmanager
    async def read(self,*args,**kwargs):
        response=httpx.Response(200,headers={**HEADERS,'Content-Length':str(BUFFER*3)},stream=self.stream)
        try:yield response
        finally:await response.aclose()


def test_partial_failure_aborts_binary_body_and_releases_owned_upstream_capacity():
    async def run():
        stream=Failing();capacity=Capacity();request=Request({'type':'http','method':'GET','headers':[]})
        response=await prepare(Client(stream),ID,{'account_id':ACCOUNT},ACTOR,OPERATION,request,'open','private.pdf',capacity)
        messages=[]
        async def send(message):messages.append(message)
        async def receive():await asyncio.sleep(10)
        with pytest.raises(httpx.ReadError):await response({'type':'http','asgi':{'spec_version':'2.4'}},receive,send)
        bodies=[value for value in messages if value['type']=='http.response.body']
        assert sum(len(value.get('body',b'')) for value in bodies)==BUFFER
        assert all(value.get('more_body') for value in bodies)
        assert stream.closed and capacity.active==0 and not capacity.accounts
    asyncio.run(run())


def test_downstream_failure_closes_source_and_recovers_capacity():
    async def run():
        stream=Failing(False);capacity=Capacity();request=Request({'type':'http','method':'GET','headers':[]})
        response=await prepare(Client(stream),ID,{'account_id':ACCOUNT},ACTOR,OPERATION,request,'download','bad\r\n/path.html',capacity)
        assert response.headers['content-disposition'].startswith('attachment;') and '\r' not in response.headers['content-disposition']
        async def send(message):
            if message['type']=='http.response.body':raise OSError('synthetic disconnected downstream')
        async def receive():await asyncio.sleep(10)
        with pytest.raises(Exception):await response({'type':'http','asgi':{'spec_version':'2.4'}},receive,send)
        assert stream.closed and capacity.active==0
    asyncio.run(run())
