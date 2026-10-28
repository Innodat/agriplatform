"""Unmounted candidate audit display endpoint; explicit collaborators only."""
import asyncio
from contextlib import asynccontextmanager
import re
from fastapi import FastAPI, Request
from starlette.responses import Response
from starlette.concurrency import run_in_threadpool
from sqlalchemy.exc import SQLAlchemyError
from safe_errors import ErrorEnvelope, install_safe_errors
import audit_http as source
from audit_display import AuditDetails, MAX_RESPONSE_BYTES, compose
from identity_actor_display import IdentityDisplays

audit=source.recovery


def create_candidate(*,org_id,access_url,service_key,database_url,identity_url,identity_service_key,transport=None,identity_transport=None):
    authority=audit.AuditReadHandler(org_id=org_id,access_url=access_url,service_key=service_key,transport=transport)
    identity=IdentityDisplays(base_url=identity_url,service_key=identity_service_key,access_service_key=service_key,transport=identity_transport)
    engine=source._engine(database_url)
    return _create_app(authority,engine,identity,org_id)


def _create_app(authority,engine,identity,org_id):
    @asynccontextmanager
    async def lifespan(app):
        try:yield
        finally:
            if engine is not None:await run_in_threadpool(engine.dispose)
    app=FastAPI(title='KDG candidate audit display composition',lifespan=lifespan,docs_url=None,redoc_url=None,openapi_url=None,redirect_slashes=False)
    from audit_display_openapi import schema_for
    app.openapi=lambda:schema_for(app,source.PAIRS)
    app.state.recovery_engine=engine
    install_safe_errors(app)
    app.add_middleware(source.PrivateResponses)
    errors={status:{'model':ErrorEnvelope} for status in (401,403,404,409,422,500,503)}

    @app.get('/api/v1/admin/captures/{capture_id}/audit-details',response_model=AuditDetails,responses=errors)
    async def audit_details(capture_id:str,request:Request):
        budget=audit.write.Budget()
        try:
            if len(request.scope.get('query_string',b''))>8192:return source.failure(422,'validation_failed')
            query=audit.parse_query(capture_id,list(request.query_params.multi_items()))
            headers=request.headers.getlist('authorization')
            if len(headers)!=1 or not re.fullmatch(r'Bearer [A-Za-z0-9\-._~+/]+=*',headers[0],flags=re.IGNORECASE):return source.failure(401,'authentication_required')
            if 'x-service-key' in request.headers:return source.failure(422,'validation_failed')
            token='Bearer '+headers[0].split(' ',1)[1]
            async with asyncio.timeout(budget.remaining()):
                async for chunk in request.stream():
                    if chunk:return source.failure(422,'validation_failed')
            result=await compose(authority,app.state.recovery_engine,identity,token,org_id,query,budget)
            body=AuditDetails.model_validate(result).model_dump_json().encode('utf-8')
            if len(body)>MAX_RESPONSE_BYTES:raise audit.write.WriteError('capture_read_unavailable')
            reply=Response(content=body,media_type='application/json')
            budget.remaining()
            return reply
        except audit.protected.HandlerError as error:return source.failure(error.status,error.error_id)
        except audit.write.WriteError as error:
            code=str(error)
            if code=='internal_error':code='capture_read_unavailable'
            return source.failure(audit.STATUS.get(code,500),code)
        except (ValueError,TypeError,RecursionError,SQLAlchemyError):return source.failure(503,'capture_read_unavailable')
        except TimeoutError:return source.failure(503,'execution_timeout')
    return app
