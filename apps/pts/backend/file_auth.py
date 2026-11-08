"""Short-lived native-file transport; existing browser auth owns refresh/logout."""
from datetime import datetime,timezone
from urllib.parse import urlsplit
from uuid import UUID,uuid4
import asyncio
from fastapi import HTTPException,Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from .private_stream import Capacity,prepare
from .contracts import FileContextResponse,FileSessionResponse,FileCleanupResponse,FilePreparationResponse

COOKIE='__Host-pts-file'

class FilePolicy:
    def __init__(self,environment):
        self.origin=environment.get('PTS_FILE_ORIGIN','');self.frontend=environment.get('PTS_FILE_FRONTEND_ORIGIN','')
        self.enabled=bool(self.origin or self.frontend)
        if not self.enabled:return
        file=urlsplit(self.origin);web=urlsplit(self.frontend)
        if any(u.scheme!='https' or not u.hostname or u.username or u.password or u.path or u.query or u.fragment for u in (file,web)):
            raise RuntimeError('file_origin_configuration_invalid')
        # The approved hosting has a dedicated child hostname of the frontend site.
        if not file.hostname.endswith('.'+web.hostname) or file.port!=web.port:raise RuntimeError('file_same_site_configuration_required')
        self.host=file.netloc

    def check(self,request,setup=False):
        if not self.enabled:raise HTTPException(503,{'code':'file_origin_unavailable'})
        if request.headers.get('host','')!=self.host:raise HTTPException(403,{'code':'file_origin_denied'})
        if request.headers.get('sec-fetch-site')=='cross-site':raise HTTPException(403,{'code':'file_origin_denied'})
        origins=request.headers.getlist('origin')
        if setup and origins!=[self.frontend]:raise HTTPException(403,{'code':'file_origin_denied'})
        if not setup and origins and origins not in ([self.frontend],[self.origin]):raise HTTPException(403,{'code':'file_origin_denied'})

async def empty(request):
    if request.query_params:raise HTTPException(422,{'code':'validation_failed'})
    await empty_body(request)

async def empty_body(request):
    try:
        async with asyncio.timeout(2):
            async for part in request.stream():
                if part:raise HTTPException(422,{'code':'validation_failed'})
    except TimeoutError:
        raise HTTPException(422,{'code':'validation_failed'}) from None

async def credential(request,sessions,bearer=False):
    if bearer:
        values=request.headers.getlist('authorization')
        if len(values)!=1:raise HTTPException(401,{'code':'authentication_required'})
        authorization=values[0]
    else:
        # Duplicate cookie names are ambiguous and must not choose an account.
        values=[part.strip()[len(COOKIE)+1:] for value in request.headers.getlist('cookie') for part in value.split(';') if part.strip().startswith(COOKIE+'=')]
        if len(values)!=1:raise HTTPException(401,{'code':'authentication_required'})
        authorization='Bearer '+values[0]
    result=await sessions.verify(authorization)
    return result,authorization


def install(app,policy,sessions,repository,access,content):
    capacity=Capacity();app.state.file_capacity=capacity

    @app.post('/api/file-session/prepare',response_model=FilePreparationResponse)
    async def prepare_cleanup(request:Request):
        policy.check(request,True);await empty(request)
        authorization=request.headers.getlist('authorization')
        if len(authorization)!=1:raise HTTPException(401,{'code':'authentication_required'})
        session=await sessions.prepare_cleanup(authorization[0])
        return JSONResponse({'status':'prepared',**{field:session[field] for field in ('account_id','session_id')}},headers={'Cache-Control':'private, no-store'})

    @app.post('/api/file-session',response_model=FileSessionResponse)
    async def establish(request:Request):
        policy.check(request,True);await empty(request)
        session,authorization=await credential(request,sessions,True)
        prepared=await sessions.prepare_cleanup(authorization)
        if any(prepared[field]!=session[field] for field in ('account_id','session_id')):raise HTTPException(401,{'code':'authentication_required'})
        # Establishment is still an exact document action, independent of read/export.
        decision=await run_in_threadpool(access.verify,authorization,'pts.poetry.documents')
        if decision['account_id']!=session['account_id']:raise HTTPException(401,{'code':'authentication_required'})
        expires=session['expires_at'];remaining=int((expires-datetime.now(timezone.utc)).total_seconds())
        if remaining<=0:raise HTTPException(401,{'code':'authentication_required'})
        response=JSONResponse({'status':'ready'},headers={'Cache-Control':'private, no-store'})
        response.set_cookie(COOKIE,authorization[7:],max_age=remaining,expires=expires,path='/',secure=True,httponly=True,samesite='lax')
        return response

    @app.post('/api/file-session/clear',response_model=FileCleanupResponse)
    async def clear(request:Request):
        policy.check(request,True);await empty(request)
        values=request.headers.getlist('authorization')
        if len(values)!=1:raise HTTPException(401,{'code':'authentication_required'})
        # Historical exact-credential proof can invalidate only the original pair.
        # Missing receipts are denial, never evidence of provider revocation.
        session=await sessions.cleanup(values[0])
        await run_in_threadpool(repository.clear_file_contexts,session)
        response=JSONResponse({'status':'cleared',**{field:session[field] for field in ('account_id','session_id','provider_session')}},headers={'Cache-Control':'private, no-store'})
        response.delete_cookie(COOKIE,path='/',secure=True,httponly=True,samesite='lax')
        return response

    @app.post('/api/file-contexts/{document_id}',response_model=FileContextResponse)
    async def context(document_id:str,request:Request,presentation:str='open'):
        policy.check(request,True)
        if set(request.query_params)-{'presentation'} or presentation not in ('open','download'):raise HTTPException(422,{'code':'validation_failed'})
        await empty_body(request)
        session,authorization=await credential(request,sessions,True)
        prepared=await sessions.prepare_cleanup(authorization)
        if any(prepared[field]!=session[field] for field in ('account_id','session_id')):raise HTTPException(401,{'code':'authentication_required'})
        decision=await run_in_threadpool(access.verify,authorization,'pts.poetry.documents')
        if decision['account_id']!=session['account_id']:raise HTTPException(401,{'code':'authentication_required'})
        library=await run_in_threadpool(repository.read,decision['actor_id'])
        document=next((d for d in library['source_documents'] if d['id']==document_id),None)
        if not document or not document.get('local_path'):raise HTTPException(404,{'code':'document_missing'})
        identity=await run_in_threadpool(repository.attachment,decision['actor_id'],document_id)
        if not identity:raise HTTPException(404,{'code':'document_not_uploaded'})
        value=await run_in_threadpool(repository.create_file_context,session,decision['actor_id'],document_id,presentation)
        return {'url':policy.origin+'/api/files/'+str(value),'expires_at':session['credential_expires_at']}

    errors={status:{'description':'Safe private-file error; HEAD has no body',
        'headers':{'X-PtS-Error-Code':{'description':'Safe private-file identifier: typed errors use JSON detail.code; structural validation uses validation_failed and retains existing validation details. Available on bodyless HEAD errors.','schema':{'type':'string'}}}}
        for status in (400,401,403,404,409,416,422,429,503)}
    @app.head('/api/files/{context_id}',operation_id='pts_file_head',responses=errors)
    @app.get('/api/files/{context_id}',operation_id='pts_file_read',responses=errors)
    async def read(context_id:UUID,request:Request):
        policy.check(request)
        if request.query_params:raise HTTPException(422,{'code':'validation_failed'})
        session,authorization=await credential(request,sessions)
        decision=await run_in_threadpool(access.verify,authorization,'pts.poetry.documents')
        if decision['account_id']!=session['account_id']:raise HTTPException(401,{'code':'authentication_required'})
        context=await run_in_threadpool(repository.file_context,session,context_id)
        if not context:raise HTTPException(404,{'code':'file_context_unavailable'})
        # Re-resolve the current protected association after releasing context SQL.
        library=await run_in_threadpool(repository.read,decision['actor_id'])
        document=next((d for d in library['source_documents'] if d['id']==context['document_id'] and d.get('local_path')),None)
        if not document:raise HTTPException(404,{'code':'document_missing'})
        identity=await run_in_threadpool(repository.attachment,decision['actor_id'],document['id'])
        if not identity:raise HTTPException(404,{'code':'document_not_uploaded'})
        for name in ('if-match','if-none-match','if-modified-since','if-unmodified-since'):
            if name in request.headers:raise HTTPException(400,{'code':'unsupported_condition'})
        filename=document.get('local_path','document').split('/')[-1]
        return await prepare(content,identity,session,decision['actor_id'],uuid4(),request,context['presentation'],filename,capacity)
