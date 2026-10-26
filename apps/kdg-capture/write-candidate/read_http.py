"""Explicit candidate-only own-detail API: no exported app or active startup import.

One numeric database host excludes DNS/failover waits. Queue/driver phase bounds
are finite; cancellation/expiry waits for worker unwind rather than abandoning
connection ownership. No engine checkout occurs during construction or before Access.
"""
import asyncio
from contextlib import asynccontextmanager
import re

from fastapi import FastAPI, Request
from starlette.responses import Response
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool

from safe_errors import ErrorEnvelope, install_safe_errors, response
import capture_read as recovery

write = recovery.write
protected = recovery.protected
PAIRS = {
    (401, 'authentication_required'), (403, 'access_denied'),
    (409, 'identity.actor_setup_required'), (404, 'capture_unavailable'), (422, 'validation_failed'),
    (503, 'authorization_unavailable'), (503, 'capture_read_unavailable'),
    (503, 'authorization_observation_expired'), (503, 'execution_timeout'),
    (500, 'invalid_write_context'), (500, 'internal_error'),
}


# The existing recovery owner retains the read-only connection and cache policy.
from recovery_http import PrivateResponses, _engine as _read_engine

def _engine(database_url):
    return _read_engine(database_url,engine_factory=create_engine)


def _pool_for(app):
    return app.state.recovery_engine


def _acquired_transaction(engine, budget, context, lookup, evidence):
    budget.remaining()
    # Checkout, dialect setup, transaction and release all belong to this worker.
    # The existing helper refuses stale observations after slow acquisition.
    with engine.connect() as conn:
        budget.remaining()
        result = recovery._transaction(conn, budget, context, lookup, evidence)
        budget.remaining()
    budget.remaining()
    return result


def failure(status, identifier):
    if (status, identifier) not in PAIRS:
        status, identifier = 500, 'internal_error'
    return response(status, identifier, 'The request could not be completed.',
        {'WWW-Authenticate':'Bearer'} if status == 401 else None)


def create_candidate(*, org_id, access_url, service_key, database_url, transport=None):
    authority = recovery.ReadHandler(org_id=org_id, access_url=access_url,
        service_key=service_key, transport=transport)
    engine = _engine(database_url)  # Lazy ordinary engine; no connection/startup I/O.
    return _create_app(authority,engine,org_id)


def _create_app(authority,engine,org_id):
    """Shared route registration; export supplies no live collaborators."""
    @asynccontextmanager
    async def lifespan(app):
        try:
            yield
        finally:
            # The ASGI host drains requests before lifespan shutdown.
            if engine is not None:
                await run_in_threadpool(engine.dispose)

    app = FastAPI(title='KDG candidate current own detail', lifespan=lifespan, docs_url=None,
        redoc_url=None, openapi_url=None, redirect_slashes=False)
    from read_openapi import schema_for
    app.openapi = lambda: schema_for(app,PAIRS)
    app.state.recovery_engine = engine
    install_safe_errors(app)
    app.add_middleware(PrivateResponses)

    @app.get('/api/v1/captures/{capture_id}',
        response_model=recovery.CaptureDetail,
        responses={status:{'model':ErrorEnvelope} for status in (401,403,404,409,422,500,503)})
    async def read_capture(capture_id: str, request: Request):
        budget = write.Budget()
        try:
            items = list(request.query_params.multi_items())
            if items:
                return failure(422,'validation_failed')
            try:
                lookup = recovery.Lookup(capture_id=capture_id)
            except ValueError:
                return failure(422,'validation_failed')
            headers = request.headers.getlist('authorization')
            if len(headers) != 1 or not re.fullmatch(r'Bearer [A-Za-z0-9\-._~+/]+=*',headers[0],flags=re.IGNORECASE):
                return failure(401,'authentication_required')
            token = 'Bearer ' + headers[0].split(' ',1)[1]
            async with asyncio.timeout(budget.remaining()):
                async for chunk in request.stream():
                    if chunk:
                        return failure(422,'validation_failed')
            evidence, observed_at = await authority._authorize(token,budget)
            context = write.VerifiedContext(org_id,evidence.account_id,evidence.actor_id,'own_read',observed_at)
            result = await protected._complete_worker(_pool_for(app),budget,context,lookup,evidence,
                _acquired_transaction)
            # Finish validation and UTF-8 serialization before the final budget
            # check. Returning Response bypasses FastAPI's later serialization.
            body=recovery.CaptureDetail.model_validate(result).model_dump_json().encode('utf-8')
            if len(body)>recovery.MAX_RESPONSE_BYTES:
                raise write.WriteError('capture_read_unavailable')
            reply=Response(content=body,media_type='application/json')
            budget.remaining()
            return reply
        except protected.HandlerError as error:
            return failure(error.status,error.error_id)
        except write.WriteError as error:
            code = str(error)
            if code == 'internal_error':
                code = 'capture_read_unavailable'
            return failure(recovery.STATUS.get(code,500),code)
        except (ValueError,TypeError,RecursionError):
            return failure(503,'capture_read_unavailable')
        except SQLAlchemyError:
            return failure(503,'capture_read_unavailable')
        except TimeoutError:
            return failure(503,'execution_timeout')

    return app
