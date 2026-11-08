import os
import re
from uuid import UUID
from fastapi import FastAPI, Depends, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler,request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .collection import select, filters, citation, text_export
from .contracts import CollectionResponse, PoemResponse, DocumentResponse, FilterQuery, SourcesResponse
from .db import engine, corpus, file_scope, load
from .clients import AccessClient, ContentClient, CurrentSessionClient
from .file_auth import install,FilePolicy
from .reader_cache import conditional_json
from uuid import uuid4
from starlette.concurrency import run_in_threadpool

class Repository:
    def __init__(self, db): self.db=db
    def read(self, actor):
        with corpus(self.db,actor, consistent=True) as conn: return load(conn)
    def sources(self, actor):
        with corpus(self.db,actor,consistent=True) as conn:
            return {kind:list(conn.execute(text(f'SELECT payload FROM pts.{kind} ORDER BY ordinal, id')).scalars())
                    for kind in ('sources','rights','source_documents')}
    def attachment(self, actor, document):
        with corpus(self.db,actor) as conn:
            return conn.execute(text('SELECT content_id FROM pts.attachments WHERE document_id=:id'),{'id':document}).scalar()

    def create_file_context(self,session,actor,document,presentation):
        identity=uuid4()
        # One fixed owner-local batch per authorized creation. The separate short
        # transaction cannot widen the following exact account/session operation.
        with self.db.begin() as conn:
            conn.execute(text("SELECT set_config('statement_timeout','1000',true)"))
            conn.execute(text('SELECT pts.reclaim_expired_file_contexts()'))
        with file_scope(self.db,session['account_id'],session['session_id'],actor) as conn:
            conn.execute(text('INSERT INTO pts.file_contexts(id,account_id,session_id,document_id,presentation,expires_at) VALUES(:id,:account,:session,:document,:presentation,:expires)'),
                {'id':identity,'account':session['account_id'],'session':session['session_id'],'document':document,'presentation':presentation,'expires':session['expires_at']})
        return identity

    def file_context(self,session,identity):
        with file_scope(self.db,session['account_id'],session['session_id'],session['account_id']) as conn:
            return conn.execute(text('SELECT document_id,presentation FROM pts.file_contexts WHERE id=:id AND expires_at>clock_timestamp()'),{'id':identity}).mappings().first()

    def clear_file_contexts(self,session):
        with file_scope(self.db,session['account_id'],session['session_id'],session['account_id']) as conn:conn.execute(text('DELETE FROM pts.file_contexts'))


def create_app(access=None, repository=None, content=None, sessions=None, environment=None):
    environment=os.environ if environment is None else environment
    app=FastAPI(title='PtS Swahili Poetry',version='1.0.0')
    # No migrations, grant creation, or database connections on startup.
    access=access or AccessClient(os.environ.get('ACCESS_URL','http://localhost:8011'),os.environ.get('PTS_SERVICE_KEY',''))
    content=content or ContentClient(os.environ.get('CONTENT_URL','http://localhost:8012'),os.environ.get('PTS_SERVICE_KEY',''))
    repository=repository or Repository(engine(environment.get('PTS_DATABASE_URL','postgresql+psycopg://pts_account_runtime@localhost/pts')))
    policy=FilePolicy(environment)
    sessions=sessions or CurrentSessionClient(environment.get('IDENTITY_URL',environment.get('ACCESS_URL','http://localhost:8011')),environment.get('PTS_CURRENT_SESSION_SERVICE_KEY',''))
    app.add_middleware(CORSMiddleware,allow_origins=environment.get('PTS_CORS_ORIGINS','http://localhost:5179').split(','),allow_headers=['Authorization','Content-Type','If-None-Match'],allow_methods=['GET','HEAD','POST'],allow_credentials=True,expose_headers=['X-PtS-Error-Code','ETag'])

    @app.exception_handler(StarletteHTTPException)
    async def private_http_error(request,error):
        response=await http_exception_handler(request,error)
        # HEAD carries no JSON body. Preserve the existing detail.code contract
        # and make its safe identifier available without revealing file metadata.
        if request.url.path.startswith(('/api/files/','/api/file-session','/api/file-contexts/')):
            code=error.detail.get('code') if isinstance(error.detail,dict) else None
            if isinstance(code,str) and re.fullmatch(r'[a-z][a-z0-9_.]{0,95}',code):
                response.headers['X-PtS-Error-Code']=code
        return response

    @app.exception_handler(RequestValidationError)
    async def private_validation_error(request,error):
        response=await request_validation_exception_handler(request,error)
        if request.url.path.startswith(('/api/files/','/api/file-session','/api/file-contexts/')):
            response.headers['X-PtS-Error-Code']='validation_failed'
        return response

    @app.middleware('http')
    async def privacy(request, call_next):
        response=await call_next(request)
        response.headers['Cache-Control']='private, no-store' if request.url.path.startswith(('/api/file','/api/documents/')) else 'no-store'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['X-Content-Type-Options']='nosniff'
        return response

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request, error):
        headers={'X-PtS-Error-Code':'collection_unavailable'} if request.url.path.startswith(('/api/files/','/api/file-session','/api/file-contexts/')) else None
        return JSONResponse({'detail':{'code':'collection_unavailable'}},status_code=503,headers=headers)

    def authority(permission):
        def check(authorization: str = Header(default='')):
            context=access.verify(authorization,permission)
            return context['actor_id'],authorization,context['account_id']
        return check

    @app.get('/health')
    def health(): return {'status':'running'}

    @app.get('/api/sources',response_model=SourcesResponse)
    def sources(request: Request,response: Response,ctx=Depends(authority('pts.poetry.read'))):
        from .research_use import source_usage, PURPOSE, FUTURE_USE
        result=repository.sources(ctx[0])
        from .acquisition import acquisition_catalogue
        result={**result,'research_purpose':PURPOSE+' '+FUTURE_USE,'research_usage':source_usage(result),**acquisition_catalogue(result['sources'])}
        return conditional_json(request,response,SourcesResponse,result,ctx[2],'sources')

    @app.get('/api/poetry',response_model=CollectionResponse)
    def collection(request: Request,response: Response,query: FilterQuery = Depends(), lean: bool=False,ctx=Depends(authority('pts.poetry.read'))):
        library=repository.read(ctx[0])
        result=select(library,**query.model_dump())
        result={**result,'total':len(result['poems']),'collection_total':len(library['poems']),
                'filters':filters(library),'citations':{} if lean else {p['id']:citation(p,library) for p in result['poems']}}
        return conditional_json(request,response,CollectionResponse,result,ctx[2],['collection',query.model_dump(),lean])

    @app.get('/api/poetry/{poem_id}',response_model=PoemResponse)
    def poem(poem_id: str,request: Request,response: Response,ctx=Depends(authority('pts.poetry.read'))):
        library=repository.read(ctx[0])
        p=next((p for p in library['poems'] if p['id']==poem_id),None)
        if p is None: raise HTTPException(404,{'code':'poem_missing'})
        evidence=select({**library,'poems':[p]},availability='all')
        return conditional_json(request,response,PoemResponse,{'poem':p,'evidence':evidence,'citation':citation(p,library)},ctx[2],['poem',poem_id])

    @app.get('/api/exports')
    def export(format: str=Query(pattern='^(json|text)$'),query: FilterQuery=Depends(),ctx=Depends(authority('pts.poetry.export'))):
        result=select(repository.read(ctx[0]),**query.model_dump())
        if format=='json': return JSONResponse(result,headers={'Content-Disposition':'attachment; filename="Swahili-poetry-selection.json"'})
        return Response(text_export(result),media_type='text/plain',headers={'Content-Disposition':'attachment; filename="Swahili-poetry-selection.txt"'})

    @app.get('/api/documents/{document_id}',response_model=DocumentResponse)
    async def document(document_id: str,ctx=Depends(authority('pts.poetry.documents'))):
        session=await sessions.verify(ctx[1])
        if session['account_id']!=ctx[2]:raise HTTPException(401,{'code':'authentication_required'})
        library=await run_in_threadpool(repository.read,ctx[0])
        d=next((d for d in library['source_documents'] if d['id']==document_id),None)
        if not d: raise HTTPException(404,{'code':'document_missing'})
        if not d.get('local_path'):
            if not str(d.get('url','')).startswith(('https://','http://')): raise HTTPException(404,{'code':'document_missing'})
            return {'status':'link_only','url':d['url'],'document':d}
        content_id=await run_in_threadpool(repository.attachment,ctx[0],document_id)
        if not content_id: raise HTTPException(404,{'code':'document_not_uploaded'})
        return {'status':'stored','document':d}
    install(app,policy,sessions,repository,access,content)
    return app

app=create_app()
