"""Explicit candidate-only own-edit API: no exported app or active startup import.

One numeric database host excludes DNS/failover waits. Queue/driver phase bounds
are finite; cancellation/expiry waits for worker unwind rather than abandoning
connection ownership. No engine checkout occurs during construction or before Access.
"""
import asyncio
from contextlib import asynccontextmanager
from ipaddress import ip_address
import re

from fastapi import FastAPI, Request
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool
from starlette.concurrency import run_in_threadpool

from safe_errors import ErrorEnvelope, install_safe_errors, response
from starlette.responses import JSONResponse
from capture_commands import Revision, parse_edit, MAX_COMMAND_BYTES, CommandError
from context import canonical_uuid
import capture_edit_handler as handler

write = handler.write
protected = handler.protected
PAIRS = {
    (401, 'authentication_required'), (403, 'access_denied'),
    (409, 'identity.actor_setup_required'), (422, 'validation_failed'),
    (503, 'authorization_unavailable'), (503, 'operation_verification_unavailable'),
    (503, 'authorization_observation_expired'), (503, 'execution_timeout'),
    (500, 'invalid_write_context'), (500, 'internal_error'),
    (404, 'capture_unavailable'), (409, 'questionnaire_version_unavailable'),
    (409, 'kdg_capture.capture_revision_conflict'), (409, 'operation_busy'),
    (422, 'unsupported_command_version'),
}


class EditConflict(ErrorEnvelope):
    current_revision: Revision


class PrivateResponses:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        async def private_send(message):
            if message['type'] == 'http.response.start':
                message = dict(message, headers=[(key,value) for key,value in message.get('headers',[])
                    if key.lower() != b'cache-control'] + [(b'cache-control', b'private, no-store')])
            await send(message)
        await self.app(scope, receive, private_send)


def _engine(database_url):
    try:
        url = make_url(database_url)
        if (url.drivername not in ('postgresql','postgresql+psycopg') or url.query
            or not url.username or not url.password or not url.database or not url.host
            or (url.port is not None and not 1 <= url.port <= 65535)):
            raise ValueError('invalid_database_policy')
        ip_address(url.host)
        return create_engine(url.set(drivername='postgresql+psycopg'),
            poolclass=QueuePool, pool_size=5, max_overflow=0, pool_timeout=.25,
            pool_pre_ping=False, pool_recycle=-1, hide_parameters=True,
            isolation_level='READ COMMITTED', connect_args=dict(
                connect_timeout=3, hostaddr=url.host, port=url.port or 5432, passfile='/dev/null',
                options='-c statement_timeout=5000 -c lock_timeout=2000'))
    except (ValueError, TypeError, SQLAlchemyError):
        raise RuntimeError('kdg_edit_database_configuration_invalid') from None


def _pool_for(app):
    return app.state.edit_engine


def _acquired_transaction(engine, budget, context, proposal, evidence):
    budget.remaining()
    # Checkout, dialect setup, transaction and release all belong to this worker.
    # The existing helper refuses stale observations after slow acquisition.
    with engine.connect() as conn:
        budget.remaining()
        result = handler._transaction(conn, budget, context, proposal, evidence)
        budget.remaining()
    budget.remaining()
    return result


def failure(status, identifier):
    if (status, identifier) not in PAIRS:
        status, identifier = 500, 'internal_error'
    return response(status, identifier, 'The request could not be completed.',
        {'WWW-Authenticate':'Bearer'} if status == 401 else None)


def create_candidate(*, org_id, access_url, service_key, database_url, transport=None):
    authority = handler.EditHandler(org_id=org_id, access_url=access_url,
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

    app = FastAPI(title='KDG candidate own edit', lifespan=lifespan, docs_url=None,
        redoc_url=None, openapi_url=None, redirect_slashes=False)
    from edit_openapi import schema_for
    app.openapi = lambda: schema_for(app,PAIRS)
    app.state.edit_engine = engine
    install_safe_errors(app)
    app.add_middleware(PrivateResponses)

    @app.put('/api/v1/captures/{capture_id}',
        response_model=handler.edit.outcomes.CaptureReceipt,
        responses={status:{'model':ErrorEnvelope} for status in (401,403,404,409,422,500,503)})
    async def edit_capture(capture_id: str, request: Request):
        budget = write.Budget()
        try:
            if list(request.query_params.multi_items()):
                return failure(422,'validation_failed')
            try:
                canonical_uuid(capture_id)
            except (ValueError,TypeError):
                return failure(422,'validation_failed')
            headers = request.headers.getlist('authorization')
            if len(headers) != 1 or not re.fullmatch(r'Bearer [A-Za-z0-9\-._~+/]+=*',headers[0],flags=re.IGNORECASE):
                return failure(401,'authentication_required')
            token = 'Bearer ' + headers[0].split(' ',1)[1]
            media_types=request.headers.getlist('content-type')
            if len(media_types)!=1 or media_types[0].split(';',1)[0].strip().lower()!='application/json':
                return failure(422,'validation_failed')
            # The byte ceiling applies to the streamed body, not Content-Length.
            # Per-chunk checks also bound streams producing empty chunks without
            # yielding control to the event loop's deadline callback.
            raw=bytearray()
            async with asyncio.timeout(budget.remaining()):
                async for chunk in request.stream():
                    budget.remaining()
                    if len(raw)+len(chunk)>MAX_COMMAND_BYTES:
                        return failure(422,'validation_failed')
                    raw.extend(chunk)
            budget.remaining()
            command=parse_edit(bytes(raw))
            evidence, observed_at = await authority._authorize(token,budget)
            context = write.VerifiedContext(org_id,evidence.account_id,evidence.actor_id,'own_write',observed_at)
            result = await protected._complete_worker(_pool_for(app),budget,context,
                handler.EditProposal(capture_id,command),evidence,_acquired_transaction)
            budget.remaining()
            return result
        except handler.edit.RevisionConflict as error:
            return JSONResponse(status_code=409,content=EditConflict(
                error='The request could not be completed.',error_id='kdg_capture.capture_revision_conflict',
                current_revision=error.current_revision).model_dump(exclude_none=True))
        except protected.HandlerError as error:
            return failure(error.status,error.error_id)
        except (write.WriteError,CommandError) as error:
            code = str(error)
            return failure(handler.WRITE_STATUS.get(code,500),code)
        except SQLAlchemyError:
            return failure(500,'internal_error')
        except TimeoutError:
            return failure(503,'execution_timeout')

    return app
