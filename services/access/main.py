"""Current access owner. Auth tokens establish identity only; never trust role claims."""
import os
from uuid import UUID
import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from organization_check import router as organization_router
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

class Check(BaseModel):
    org_id: UUID
    permission: str

class Decision(BaseModel):
    org_id: UUID
    actor_id: UUID


def create_app(db=None, authenticate=None):
    app=FastAPI(title='Shared current access',version='1.0.0')
    db=db or create_engine(os.environ.get('ACCESS_DATABASE_URL','postgresql+psycopg://access_runtime@localhost/pts'),pool_pre_ping=True,pool_timeout=5,hide_parameters=True,connect_args={'connect_timeout':5})

    def auth(token):
        if not token.startswith('Bearer '): raise HTTPException(401,{'code':'authentication_required'})
        try:
            r=httpx.get(os.environ['SUPABASE_URL'].rstrip('/')+'/auth/v1/user',headers={'Authorization':token,'apikey':os.environ['SUPABASE_ANON_KEY']},timeout=5)
            if r.status_code in (401,403): raise HTTPException(401,{'code':'authentication_required'})
            r.raise_for_status()
            account_id = r.json()['id']
            if not isinstance(account_id, str):
                raise ValueError('account_id')
            return UUID(account_id)
        except (httpx.HTTPError,ValueError,KeyError,TypeError): raise HTTPException(503,{'code':'authorization_unavailable'}) from None

    @app.middleware('http')
    async def no_store(request, call_next):
        response = await call_next(request)
        if request.url.path == '/v2/check':
            response.headers['Cache-Control'] = 'no-store'
        return response

    app.include_router(organization_router(db, authenticate or auth, os.environ))

    # FastAPI gathers separate security dependencies as alternatives; this operation
    # requires their conjunction. Keep its ordinary security scheme definitions.
    original_openapi = app.openapi
    def openapi():
        schema = original_openapi()
        schema['paths']['/v2/check']['post']['security'] = [{'KdgBearer': [], 'KdgServiceKey': []}]
        return schema
    app.openapi = openapi

    @app.exception_handler(SQLAlchemyError)
    async def unavailable(request,error): return JSONResponse({'detail':{'code':'access_unavailable'}},status_code=503)

    @app.post('/v1/check',response_model=Decision)
    def check(body: Check,authorization: str=Header(default=''),x_service_key: str=Header(default='')):
        # Legacy PtS organization checks cannot authorize under the new model.
        # Coordinated typed account adoption is a separate, gated delivery.
        raise HTTPException(503,{'code':'authorization_unavailable'})

    @app.get('/health')
    def health(): return {'status':'running'}
    return app

app=create_app()
