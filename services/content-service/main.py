"""Private content control plane. Service identities narrowly delegated to PtS."""
import os
import secrets
from contextlib import contextmanager
from uuid import UUID,uuid4
import httpx
from fastapi import FastAPI,Header,HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field
from sqlalchemy import create_engine,text
from sqlalchemy.exc import SQLAlchemyError
from provider import Storage

class Upload(BaseModel):
    sha256:str=Field(pattern='^[a-f0-9]{64}$')
    size:int=Field(gt=0,le=134217728)
    media_type:str=Field(pattern='^(application/pdf|image/jpeg|image/png|text/plain|application/xml|text/html|application/json|application/octet-stream)$')

class Session(BaseModel):
    content_id:UUID
    state:str
    url:str|None=None
    expires_in:int|None=None
    media_type:str|None=None

@contextmanager
def scoped(db,org,actor):
    with db.begin() as c:
        c.execute(text("SELECT set_config('app.org_id',:org,true),set_config('app.actor_id',:actor,true),set_config('statement_timeout','5000',true)"),{'org':str(org),'actor':str(actor)})
        yield c


def create_app(db=None,storage=None,verify=None):
    app=FastAPI(title='Private Content Service',version='1.0.0')
    db=db or create_engine(os.environ.get('CONTENT_DATABASE_URL','postgresql+psycopg://content_runtime@localhost/pts'),pool_pre_ping=True,hide_parameters=True,connect_args={'connect_timeout':5})
    def provider(): return storage or Storage()
    def service(key,kind):
        expected=os.environ.get('PTS_IMPORT_SERVICE_KEY' if kind=='import' else 'PTS_SERVICE_KEY','')
        if not key or not expected or not secrets.compare_digest(key,expected): raise HTTPException(403,{'code':'service_denied'})
    def import_scope(key,org):
        service(key,'import')
        if str(org)!=os.environ.get('PTS_IMPORT_ORG_ID'): raise HTTPException(403,{'code':'scope_denied'})
    def access(token,org):
        if verify:return verify(token,org)
        try:
            r=httpx.post(os.environ['ACCESS_URL'].rstrip('/')+'/v1/check',headers={'Authorization':token,'X-Service-Key':os.environ['CONTENT_SERVICE_KEY']},json={'org_id':str(org),'permission':'pts.poetry.documents'},timeout=5)
            if r.status_code in (401,403):raise HTTPException(r.status_code,{'code':'access_denied'})
            r.raise_for_status();data=r.json()
            if data['org_id']!=str(org):raise ValueError()
            return data['actor_id']
        except (httpx.HTTPError,ValueError,KeyError):raise HTTPException(503,{'code':'access_unavailable'}) from None
    def audit(org,actor,content_id,operation):
        with scoped(db,org,actor) as c:
            c.execute(text('INSERT INTO content.events(org_id,id,content_id,operation) VALUES(:org,:id,:content,:operation)'),{'org':org,'id':uuid4(),'content':str(content_id),'operation':operation})
    @app.exception_handler(SQLAlchemyError)
    async def unavailable(request,error):return JSONResponse({'detail':{'code':'content_unavailable'}},status_code=503)
    @app.middleware('http')
    async def private(request,call_next):
        response=await call_next(request);response.headers['Cache-Control']='no-store';return response
    @app.post('/v1/objects',response_model=Session)
    def upload(body:Upload,x_org_id:UUID=Header(),x_service_key:str=Header(default='')):
        import_scope(x_service_key,x_org_id)
        with scoped(db,x_org_id,'service:pts-import') as c:
            c.execute(text("INSERT INTO content.objects(org_id,id,sha256,size,media_type) VALUES(:org,:id,:sha,:size,:mime) ON CONFLICT(org_id,sha256) DO NOTHING"),{'org':x_org_id,'id':str(uuid4()),'sha':body.sha256,'size':body.size,'mime':body.media_type})
            row=c.execute(text('SELECT * FROM content.objects WHERE sha256=:sha'),{'sha':body.sha256}).mappings().one()
        if row['size']!=body.size or row['media_type']!=body.media_type:raise HTTPException(409,{'code':'content_identity_conflict'})
        if row['state']=='ready':return {'content_id':row['id'],'state':'ready'}
        if row['state']=='finalizing':raise HTTPException(409,{'code':'finalization_in_progress'})
        try:url=provider().upload(f"{x_org_id}/staging/{row['id']}",body.media_type)
        except Exception:raise HTTPException(503,{'code':'upload_unavailable'}) from None
        audit(x_org_id,'service:pts-import',row['id'],'upload_issued')
        return {'content_id':row['id'],'state':'pending','url':url,'expires_in':900,'media_type':body.media_type}
    @app.post('/v1/objects/{content_id}/finalize',response_model=Session)
    def finalize(content_id:UUID,x_org_id:UUID=Header(),x_service_key:str=Header(default='')):
        import_scope(x_service_key,x_org_id)
        # No lease takeover: a crash requires explicit recovery, avoiding concurrent sealing.
        with scoped(db,x_org_id,'service:pts-import') as c:
            row=c.execute(text('SELECT * FROM content.objects WHERE id=:id'),{'id':str(content_id)}).mappings().one_or_none()
            if not row:raise HTTPException(404,{'code':'content_missing'})
            if row['state']=='ready':return {'content_id':content_id,'state':'ready'}
            claimed=c.execute(text("UPDATE content.objects SET state='finalizing',updated_at=clock_timestamp(),updated_by=current_setting('app.actor_id') WHERE id=:id AND state='pending' RETURNING id"),{'id':str(content_id)}).scalar()
            if not claimed:raise HTTPException(409,{'code':'finalization_in_progress'})
        try:provider().seal(f'{x_org_id}/staging/{content_id}',f'{x_org_id}/sealed/{content_id}',row['sha256'],row['size'])
        except Exception:
            raise HTTPException(503,{'code':'finalization_requires_recovery'}) from None
        with scoped(db,x_org_id,'service:pts-import') as c:
            c.execute(text("UPDATE content.objects SET state='ready',updated_at=clock_timestamp(),updated_by=current_setting('app.actor_id') WHERE id=:id AND state='finalizing'"),{'id':str(content_id)})
        audit(x_org_id,'service:pts-import',content_id,'finalized')
        return {'content_id':content_id,'state':'ready'}
    @app.post('/v1/objects/{content_id}/read')
    def read(content_id:UUID,x_org_id:UUID=Header(),x_service_key:str=Header(default=''),authorization:str=Header(default='')):
        service(x_service_key,'read');actor=access(authorization,x_org_id)
        with scoped(db,x_org_id,actor) as c:
            state=c.execute(text('SELECT state FROM content.objects WHERE id=:id'),{'id':str(content_id)}).scalar()
        if state!='ready':raise HTTPException(404,{'code':'content_missing'})
        try:url=provider().read(f'{x_org_id}/sealed/{content_id}')
        except Exception:raise HTTPException(503,{'code':'document_unavailable'}) from None
        audit(x_org_id,actor,content_id,'read_issued')
        return {'url':url,'expires_in':300}
    @app.get('/health')
    def health():return {'status':'running'}
    return app

app=create_app()
