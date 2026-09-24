import os
from uuid import UUID
from fastapi import FastAPI, Depends, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .collection import select, filters, citation, text_export
from .contracts import CollectionResponse, PoemResponse, DocumentResponse, FilterQuery
from .db import engine, scoped, load
from .clients import AccessClient, ContentClient

class Repository:
    def __init__(self, db): self.db=db
    def read(self, org, actor):
        with scoped(self.db,org,actor, consistent=True) as conn: return load(conn)
    def attachment(self, org, actor, document):
        with scoped(self.db,org,actor) as conn:
            return conn.execute(text('SELECT content_id FROM pts.attachments WHERE document_id=:id'),{'id':document}).scalar()


def create_app(access=None, repository=None, content=None):
    app=FastAPI(title='PtS Swahili Poetry',version='1.0.0')
    # No migrations, grant creation, or database connections on startup.
    access=access or AccessClient(os.environ.get('ACCESS_URL','http://localhost:8011'),os.environ.get('PTS_SERVICE_KEY',''))
    content=content or ContentClient(os.environ.get('CONTENT_URL','http://localhost:8012'),os.environ.get('PTS_SERVICE_KEY',''))
    repository=repository or Repository(engine(os.environ.get('PTS_DATABASE_URL','postgresql+psycopg://pts_runtime@localhost/pts')))
    app.add_middleware(CORSMiddleware,allow_origins=os.environ.get('PTS_CORS_ORIGINS','http://localhost:5179').split(','),allow_headers=['Authorization','X-Org-ID'],allow_methods=['GET'])

    @app.middleware('http')
    async def privacy(request, call_next):
        response=await call_next(request)
        response.headers['Cache-Control']='no-store'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['X-Content-Type-Options']='nosniff'
        return response

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request, error): return JSONResponse({'detail':{'code':'collection_unavailable'}},status_code=503)

    def authority(permission):
        def check(authorization: str = Header(default=''), x_org_id: UUID = Header()):
            context=access.verify(authorization,x_org_id,permission)
            return x_org_id,context['actor_id'],authorization
        return check

    @app.get('/health')
    def health(): return {'status':'running'}

    @app.get('/api/poetry',response_model=CollectionResponse)
    def collection(query: FilterQuery = Depends(), ctx=Depends(authority('pts.poetry.read'))):
        library=repository.read(ctx[0],ctx[1])
        result=select(library,**query.model_dump())
        return {**result,'total':len(result['poems']),'collection_total':len(library['poems']),
                'filters':filters(library),'citations':{p['id']:citation(p,library) for p in result['poems']}}

    @app.get('/api/poetry/{poem_id}',response_model=PoemResponse)
    def poem(poem_id: str,ctx=Depends(authority('pts.poetry.read'))):
        library=repository.read(ctx[0],ctx[1])
        p=next((p for p in library['poems'] if p['id']==poem_id),None)
        if p is None: raise HTTPException(404,{'code':'poem_missing'})
        evidence=select({**library,'poems':[p]},availability='all')
        return {'poem':p,'evidence':evidence,'citation':citation(p,library)}

    @app.get('/api/exports')
    def export(format: str=Query(pattern='^(json|text)$'),query: FilterQuery=Depends(),ctx=Depends(authority('pts.poetry.export'))):
        result=select(repository.read(ctx[0],ctx[1]),**query.model_dump())
        if format=='json': return JSONResponse(result,headers={'Content-Disposition':'attachment; filename="Swahili-poetry-selection.json"'})
        return Response(text_export(result),media_type='text/plain',headers={'Content-Disposition':'attachment; filename="Swahili-poetry-selection.txt"'})

    @app.get('/api/documents/{document_id}',response_model=DocumentResponse)
    def document(document_id: str,ctx=Depends(authority('pts.poetry.documents'))):
        library=repository.read(ctx[0],ctx[1])
        d=next((d for d in library['source_documents'] if d['id']==document_id),None)
        if not d: raise HTTPException(404,{'code':'document_missing'})
        if not d.get('local_path'):
            if not str(d.get('url','')).startswith(('https://','http://')): raise HTTPException(404,{'code':'document_missing'})
            return {'status':'link_only','url':d['url'],'document':d}
        content_id=repository.attachment(ctx[0],ctx[1],document_id)
        if not content_id: raise HTTPException(404,{'code':'document_not_uploaded'})
        capability=content.read(content_id,ctx[0],ctx[2])
        return {'status':'stored','url':capability['url'],'expires_in':capability['expires_in'],'document':d}
    return app

app=create_app()
