"""Explicit candidate-only recovery API: no exported app or active startup import.

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
import operation_recovery as recovery

write = recovery.write
protected = recovery.protected
PAIRS = {
    (401, 'authentication_required'), (403, 'access_denied'),
    (409, 'identity.actor_setup_required'), (422, 'validation_failed'),
    (503, 'authorization_unavailable'), (503, 'operation_verification_unavailable'),
    (503, 'authorization_observation_expired'), (503, 'execution_timeout'),
    (500, 'invalid_write_context'), (500, 'internal_error'),
}


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
                options='-c default_transaction_read_only=on -c statement_timeout=5000 -c lock_timeout=2000'))
    except (ValueError, TypeError, SQLAlchemyError):
        raise RuntimeError('kdg_recovery_database_configuration_invalid') from None


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
    authority = recovery.RecoveryHandler(org_id=org_id, access_url=access_url,
        service_key=service_key, transport=transport)
    engine = _engine(database_url)  # Lazy ordinary engine; no connection/startup I/O.
    @asynccontextmanager
    async def lifespan(app):
        try:
            yield
        finally:
            # The ASGI host drains requests before lifespan shutdown.
            await run_in_threadpool(engine.dispose)

    app = FastAPI(title='KDG candidate operation recovery', lifespan=lifespan, docs_url=None,
        redoc_url=None, openapi_url=None, redirect_slashes=False)
    app.state.recovery_engine = engine
    install_safe_errors(app)
    app.add_middleware(PrivateResponses)

    @app.get('/api/v1/operations/{operation_id}',
        response_model=recovery.outcomes.CaptureReceipt | recovery.Unresolved,
        responses={status:{'model':ErrorEnvelope} for status in (401,403,409,422,500,503)})
    async def recover(operation_id: str, request: Request):
        budget = write.Budget()
        try:
            items = list(request.query_params.multi_items())
            if len(items) != 1 or items[0][0] != 'command_type':
                return failure(422,'validation_failed')
            try:
                lookup = recovery.Lookup(operation_id=operation_id,command_type=items[0][1])
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
            budget.remaining()
            return result
        except protected.HandlerError as error:
            return failure(error.status,error.error_id)
        except write.WriteError as error:
            code = str(error)
            if code == 'internal_error':
                code = 'operation_verification_unavailable'
            return failure(protected.WRITE_STATUS.get(code,500),code)
        except SQLAlchemyError:
            return failure(503,'operation_verification_unavailable')
        except TimeoutError:
            return failure(503,'execution_timeout')

    return app
