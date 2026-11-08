"""PtS-to-Content HTTP bytes adapter. No provider paths or server imports."""
import asyncio
from contextlib import asynccontextmanager
import re
from threading import Lock
import time
from urllib.parse import quote
from uuid import UUID
import anyio
import httpx
from fastapi import HTTPException
from fastapi.responses import Response, StreamingResponse

BUFFER=1024*1024
TOTAL_SECONDS=900

class ContentClient:
    def __init__(self,base_url,service_key,transport=None):
        self.base_url=base_url.rstrip('/');self.key=service_key;self.transport=transport

    @asynccontextmanager
    async def read(self,identity,*,account_id,actor_id,operation_id,method='GET',range_header=None,if_range=None):
        identity=str(UUID(str(identity)))
        headers={'X-Service-Key':self.key,'X-Initiator-Account-Id':str(account_id),
                 'X-Initiator-Actor-Id':str(actor_id),'X-Operation-Id':str(operation_id),'Accept-Encoding':'identity'}
        if range_header is not None:headers['Range']=range_header
        if if_range is not None:headers['If-Range']=if_range
        async with httpx.AsyncClient(transport=self.transport,timeout=httpx.Timeout(connect=5,read=30,write=30,pool=5),trust_env=False,follow_redirects=False) as client:
            try:
                async with client.stream(method,self.base_url+'/v2/objects/'+identity+'/bytes',params={'application_id':'pts','kind':'application'},headers=headers) as response:
                    if response.status_code not in (200,206):
                        code=response.headers.get('x-content-error-id','')
                        if method!='HEAD':
                            body=bytearray()
                            async for part in response.aiter_bytes(4096):
                                body.extend(part)
                                if len(body)>65536:raise ValueError()
                            import json
                            code=json.loads(body).get('error_id','')
                        if not isinstance(code,str) or re.fullmatch(r'content\.[a-z][a-z0-9_]{0,95}',code) is None:raise ValueError()
                        status=response.status_code if response.status_code in (400,403,404,409,416,429,503) else 503
                        extra={'Retry-After':'1'} if status==429 else {}
                        if status==416 and re.fullmatch(r'bytes \*/[0-9]{1,19}',response.headers.get('content-range','')):extra['Content-Range']=response.headers['content-range']
                        raise HTTPException(status,{'code':code},headers=extra)
                    if (response.headers.get('x-content-id')!=identity or response.headers.get('cache-control')!='private, no-store'
                        or response.headers.get('content-encoding','identity')!='identity'
                        or response.headers.get('x-content-type-options')!='nosniff'
                        or not re.fullmatch(r'"[a-f0-9]{64}"',response.headers.get('etag',''))
                        or not re.fullmatch(r'[0-9]{1,19}',response.headers.get('content-length',''))
                        or response.status_code==206 and not re.fullmatch(r'bytes [0-9]+-[0-9]+/[0-9]+',response.headers.get('content-range',''))):raise ValueError()
                    yield response
            except (httpx.HTTPError,ValueError,KeyError,TypeError):raise HTTPException(503,{'code':'document_unavailable'}) from None

class Capacity:
    def __init__(self,total=16,per_account=2):self.total=total;self.per_account=per_account;self.active=0;self.accounts={};self.lock=Lock()
    def acquire(self,account):
        with self.lock:
            if self.active>=self.total or self.accounts.get(account,0)>=self.per_account:raise HTTPException(429,{'code':'file_capacity_exceeded'},headers={'Retry-After':'1'})
            self.active+=1;self.accounts[account]=self.accounts.get(account,0)+1
        released=False
        def release():
            nonlocal released
            with self.lock:
                if released:return
                released=True;self.active-=1;self.accounts[account]-=1
                if not self.accounts[account]:del self.accounts[account]
        return release

class ManagedResponse(StreamingResponse):
    def __init__(self,iterator,cleanup,deadline,**kwargs):super().__init__(iterator,**kwargs);self.cleanup=cleanup;self.deadline=deadline
    async def __call__(self,scope,receive,send):
        try:
            async with asyncio.timeout_at(self.deadline):await super().__call__(scope,receive,send)
        finally:
            with anyio.CancelScope(shield=True):
                try:await self.body_iterator.aclose()
                finally:await self.cleanup()

async def prepare(content,identity,session,actor,operation,request,presentation,filename,capacity):
    release=capacity.acquire(session['account_id']);context=None;entered=False;closed=False
    deadline=time.monotonic()+TOTAL_SECONDS
    async def cleanup():
        nonlocal closed
        if closed:return
        closed=True
        try:
            if entered:
                async with asyncio.timeout(5):await context.__aexit__(None,None,None)
        finally:release()
    try:
        context=content.read(identity,account_id=session['account_id'],actor_id=actor,operation_id=operation,
            method=request.method,range_header=request.headers.get('range'),if_range=request.headers.get('if-range'))
        async with asyncio.timeout(min(30,max(.001,deadline-time.monotonic()))):
            upstream=await context.__aenter__();entered=True
            headers={name:upstream.headers[name] for name in ('Content-Type','Content-Length','ETag','Accept-Ranges','Content-Range') if name in upstream.headers}
            media=headers.get('Content-Type','application/octet-stream').split(';')[0]
            if media not in ('application/pdf','image/jpeg','image/png','text/plain','application/xml','text/html','application/json','application/octet-stream'):media='application/octet-stream'
            headers['Content-Type']=media
            filename=''.join(c for c in filename if ord(c)>=32 and c not in '\r\n\x00').replace('/','_').replace('\\','_')[:180] or 'document'
            ascii_name=re.sub(r'[^a-zA-Z0-9._ -]','_',filename).strip(' .') or 'document'
            kind='inline' if presentation=='open' and media=='application/pdf' else 'attachment'
            headers.update({'Content-Disposition':kind+'; filename="'+ascii_name+'"; filename*=UTF-8\'\''+quote(filename,safe=''),
                'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff','Content-Security-Policy':"sandbox; default-src 'none'",'Referrer-Policy':'no-referrer'})
            if request.method=='HEAD':
                await cleanup();return Response(status_code=200,headers=headers)
            length=int(headers['Content-Length']);iterator=upstream.aiter_raw(chunk_size=BUFFER)
            first=await anext(iterator,b'')
            if not first or len(first)>length:raise ValueError()
        async def chunks():
            read=0;chunk=first
            while chunk:
                read+=len(chunk)
                if read>length:raise RuntimeError('file_transfer_incomplete')
                following=await anext(iterator,b'')
                if not following and read!=length:raise RuntimeError('file_transfer_incomplete')
                yield chunk;chunk=following
        return ManagedResponse(chunks(),cleanup,deadline,status_code=upstream.status_code,headers=headers)
    except BaseException as error:
        with anyio.CancelScope(shield=True):await cleanup()
        if isinstance(error,(HTTPException,asyncio.CancelledError)):raise
        raise HTTPException(503,{'code':'document_unavailable'}) from None
