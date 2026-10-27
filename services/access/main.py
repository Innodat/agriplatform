"""Current access owner. Auth tokens establish identity only; never trust role claims."""
import os
from uuid import UUID
import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from organization_check import router as organization_router
from pydantic import BaseModel
from sqlalchemy import create_engine
from studies_identity import AsyncDatabase
from studies_access import StudiesAccess
from sqlalchemy.exc import SQLAlchemyError

class Check(BaseModel):
    org_id: UUID
    permission: str

class Decision(BaseModel):
    org_id: UUID
    actor_id: UUID


def create_app(db=None, authenticate=None, *, studies_provider=None, studies_identity_db=None, studies_setup_db=None, studies_db=None, preferences_db=None, capability_db=None, capability_provider=None):
    app=FastAPI(title='Shared current access',version='1.0.0')
    db=db or create_engine(os.environ.get('ACCESS_DATABASE_URL','postgresql+psycopg://access_runtime@localhost/pts'),pool_pre_ping=True,pool_timeout=5,hide_parameters=True,connect_args={'connect_timeout':5})

    def optional_pool(name,role):
        url=os.environ.get(name)
        if not url:return None
        from sqlalchemy.engine import make_url
        try:
            parsed=make_url(url)
            if parsed.username!=role or parsed.drivername not in ('postgresql','postgresql+psycopg'):raise ValueError('role')
        except (ValueError,TypeError,SQLAlchemyError):raise RuntimeError('studies_configuration_invalid') from None
        return AsyncDatabase(url)
    studies=StudiesAccess(studies_db if studies_db is not None else optional_pool('STUDIES_ACCESS_DATABASE_URL','access_studies_runtime'),
        studies_identity_db if studies_identity_db is not None else optional_pool('STUDIES_IDENTITY_DATABASE_URL','identity_studies_reader_runtime'),
        studies_setup_db if studies_setup_db is not None else optional_pool('STUDIES_IDENTITY_SETUP_DATABASE_URL','identity_studies_setup_runtime'),
        os.environ,studies_provider)
    if any(name in os.environ for name in ('SCRIBESWELL_SERVICE_KEY','STUDIES_ACCESS_DATABASE_URL','STUDIES_IDENTITY_DATABASE_URL','STUDIES_IDENTITY_SETUP_DATABASE_URL','STUDIES_READINESS_JSON')):
        if not studies.key:raise RuntimeError('studies_configuration_invalid')
        if any(value is None for value in (studies.db,studies.identity_db,studies.setup_db)):
            raise RuntimeError('studies_configuration_invalid')
        if studies_db is None or studies_identity_db is None or studies_setup_db is None:
            from studies_readiness import validate_artifact
            try:validate_artifact(os.environ.get('STUDIES_READINESS_JSON',''))
            except ValueError:raise RuntimeError('studies_configuration_invalid') from None

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
        if request.url.path in ('/v2/organizations','/v2/applications'):
            response.headers['Cache-Control']='private, no-store'
        if request.url.path == '/v2/enrollments/scribeswell-studies' or (request.url.path == '/v2/check' and studies.matches(request.headers.get('x-service-key',''))):
            response.headers['Cache-Control'] = 'private, no-store'
        elif request.url.path == '/v2/check' or request.url.path == '/v2/identity/organization-context':
            response.headers.setdefault('Cache-Control', 'private, no-store' if capabilities.matches(request.headers.get('x-service-key','')) or request.url.path.endswith('organization-context') else 'no-store')
        return response

    from capability_check import CapabilityAccess
    capabilities=CapabilityAccess(capability_db if capability_db is not None else optional_pool('CAPABILITY_ACCESS_DATABASE_URL','access_runtime'),os.environ,capability_provider)
    if capabilities.policy.callers and capabilities.db is None:
        raise RuntimeError('capability_configuration_invalid')
    app.include_router(organization_router(db, authenticate or auth, os.environ, studies, capabilities))
    app.include_router(capabilities.router())
    from discovery import Discovery
    app.include_router(Discovery(capabilities.db,os.environ,capability_provider).router())

    app.include_router(studies.router())

    from identity_preferences import router as preferences_router,configured_database
    app.include_router(preferences_router(preferences_db if preferences_db is not None else configured_database(os.environ),authenticate or auth,os.environ))

    # FastAPI gathers separate security dependencies as alternatives; this operation
    # requires their conjunction. Keep its ordinary security scheme definitions.
    original_openapi = app.openapi
    def openapi():
        schema = original_openapi()
        for path in ('/v2/check','/v2/enrollments/scribeswell-studies','/v2/identity/organization-context'):
            schema['paths'][path]['post']['security'] = [{'KdgBearer': [], 'KdgServiceKey': []}]
        from identity_preferences import SECURITY as preference_security
        for method in ('get','put'):
            schema['paths']['/v2/me/preferences/language'][method]['security']=preference_security
        for path in ('/v2/organizations','/v2/applications'):
            schema['paths'][path]['get']['security']=[{'KdgBearer': [], 'KdgServiceKey': []}]
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
