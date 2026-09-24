"""Current access owner. Auth tokens establish identity only; never trust role claims."""
import os
import secrets
from uuid import UUID
import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class Check(BaseModel):
    org_id: UUID
    permission: str

class Decision(BaseModel):
    org_id: UUID
    actor_id: UUID


def create_app(db=None, authenticate=None):
    app=FastAPI(title='Shared current access',version='1.0.0')
    db=db or create_engine(os.environ.get('ACCESS_DATABASE_URL','postgresql+psycopg://access_runtime@localhost/pts'),pool_pre_ping=True,hide_parameters=True,connect_args={'connect_timeout':5})

    def auth(token):
        if not token.startswith('Bearer '): raise HTTPException(401,{'code':'authentication_required'})
        try:
            r=httpx.get(os.environ['SUPABASE_URL'].rstrip('/')+'/auth/v1/user',headers={'Authorization':token,'apikey':os.environ['SUPABASE_ANON_KEY']},timeout=5)
            if r.status_code in (401,403): raise HTTPException(401,{'code':'authentication_required'})
            r.raise_for_status()
            return UUID(r.json()['id'])
        except (httpx.HTTPError,ValueError,KeyError): raise HTTPException(503,{'code':'authentication_unavailable'}) from None

    @app.exception_handler(SQLAlchemyError)
    async def unavailable(request,error): return JSONResponse({'detail':{'code':'access_unavailable'}},status_code=503)

    @app.post('/v1/check',response_model=Decision)
    def check(body: Check,authorization: str=Header(default=''),x_service_key: str=Header(default='')):
        allowed=[os.environ.get('PTS_SERVICE_KEY',''),os.environ.get('CONTENT_SERVICE_KEY','')]
        if not x_service_key or not any(k and secrets.compare_digest(k,x_service_key) for k in allowed):
            raise HTTPException(403,{'code':'service_denied'})
        if body.permission not in {'pts.poetry.read','pts.poetry.export','pts.poetry.documents'}:
            raise HTTPException(403,{'code':'permission_denied'})
        actor=(authenticate or auth)(authorization)
        with db.begin() as conn:
            conn.execute(text("SELECT set_config('app.org_id',:org,true),set_config('app.actor_id',:actor,true),set_config('statement_timeout','5000',true)"),{'org':str(body.org_id),'actor':str(actor)})
            granted=conn.execute(text('''SELECT EXISTS(SELECT 1 FROM identity.org_member m JOIN identity.org o ON o.id=m.org_id
              JOIN access.grants g ON g.org_id=m.org_id AND g.user_id=m.user_id
              WHERE m.org_id=:org AND m.user_id=:actor AND m.deleted_at IS NULL AND o.deleted_at IS NULL AND g.permission=:permission)'''),
              {'org':body.org_id,'actor':actor,'permission':body.permission}).scalar()
        if not granted: raise HTTPException(403,{'code':'access_denied'})
        return {'org_id':body.org_id,'actor_id':actor}

    @app.get('/health')
    def health(): return {'status':'running'}
    return app

app=create_app()
