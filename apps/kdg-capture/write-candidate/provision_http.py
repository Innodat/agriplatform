"""Explicit candidate-only protected setup API: no exported app or active startup import.

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
import provision as recovery

write = recovery.write
protected = recovery.protected
PAIRS = {
    (401, 'authentication_required'), (403, 'access_denied'),
    (409, 'identity.actor_setup_required'), (422, 'validation_failed'),
    (503, 'authorization_unavailable'), (503, 'provision_unavailable'),
    (503, 'authorization_observation_expired'), (503, 'execution_timeout'),
    (500, 'invalid_write_context'), (500, 'internal_error'),
}


# Reuse the bounded write-capable engine and private response policy.
from edit_http import PrivateResponses, _engine as _read_engine

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


def create_candidate(*, org_id, questionnaire_id, access_url, service_key, database_url, transport=None):
    authority = recovery.ProvisionHandler(org_id=org_id, questionnaire_id=questionnaire_id, access_url=access_url,
        service_key=service_key, transport=transport)
    engine = _engine(database_url)  # Lazy ordinary engine; no connection/startup I/O.
    return _create_app(authority,engine,org_id,questionnaire_id)


def _create_app(authority,engine,org_id,questionnaire_id):
    """Shared route registration; export supplies no live collaborators."""
    @asynccontextmanager
    async def lifespan(app):
        try:
            yield
        finally:
            # The ASGI host drains requests before lifespan shutdown.
            if engine is not None:
                await run_in_threadpool(engine.dispose)

    app = FastAPI(title='KDG candidate protected setup', lifespan=lifespan, docs_url=None,
        redoc_url=None, openapi_url=None, redirect_slashes=False)
    from provision_openapi import schema_for
    app.openapi = lambda: schema_for(app,PAIRS)
    app.state.recovery_engine = engine
    install_safe_errors(app)
    app.add_middleware(PrivateResponses)

    @app.get('/api/v1/provision',
        response_model=recovery.Provision,
        responses={status:{'model':ErrorEnvelope} for status in (401,403,409,422,500,503)})
    async def provision_setup(request: Request):
        budget = write.Budget()
        try:
            items = list(request.query_params.multi_items())
            if items:
                return failure(422,'validation_failed')
            headers = request.headers.getlist('authorization')
            if len(headers) != 1 or not re.fullmatch(r'Bearer [A-Za-z0-9\-._~+/]+=*',headers[0],flags=re.IGNORECASE):
                return failure(401,'authentication_required')
            token = 'Bearer ' + headers[0].split(' ',1)[1]
            # Read ASGI messages directly: Request.stream() suppresses empty
            # more_body messages, which can starve timer callbacks indefinitely.
            async with asyncio.timeout(budget.remaining()):
                while True:
                    message=await request.receive()
                    budget.remaining()
                    if message['type']!='http.request' or message.get('body',b''):
                        return failure(422,'validation_failed')
                    if not message.get('more_body',False):break
            evidence, observed_at = await authority.authorize(token,budget)
            entry=evidence[0]
            context = write.VerifiedContext(org_id,entry.account_id,entry.actor_id,'own_write',observed_at)
            result = await protected._complete_worker(_pool_for(app),budget,context,questionnaire_id,evidence,
                _acquired_transaction)
            # Finish validation and UTF-8 serialization before the final budget
            # check. Returning Response bypasses FastAPI's later serialization.
            body=recovery.Provision.model_validate(result).model_dump_json().encode('utf-8')
            if len(body)>recovery.MAX_RESPONSE_BYTES:
                raise write.WriteError('provision_unavailable')
            reply=Response(content=body,media_type='application/json')
            budget.remaining()
            return reply
        except protected.HandlerError as error:
            return failure(error.status,error.error_id)
        except write.WriteError as error:
            code = str(error)
            if code == 'internal_error':
                code = 'provision_unavailable'
            return failure(recovery.STATUS.get(code,500),code)
        except (ValueError,TypeError,RecursionError):
            return failure(503,'provision_unavailable')
        except SQLAlchemyError:
            return failure(503,'provision_unavailable')
        except TimeoutError:
            return failure(503,'execution_timeout')

    return app
