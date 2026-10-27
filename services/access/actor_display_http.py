"""Isolated Identity display candidate: explicit policy and injected read-only I/O.

No environment, database, account lookup or active service mount is created here.
Readers must be cancellation-cooperative and may perform only their owned bounded
read/unwind. A short reserve keeps cooperative reader unwind inside the original
three-second operation budget; that budget is never restarted.
"""
import asyncio
import hmac
import time
from collections.abc import Awaitable, Callable, Iterable, Mapping
from dataclasses import dataclass
from uuid import UUID

from fastapi import APIRouter, FastAPI, Request, Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from actor_display_contract import (
    ActorDisplayRequest, ActorDisplayResponse, ActorDisplayDenied, ActorDisplayInvalid,
    ActorDisplayUnavailable, RESPONSE_BYTES, assemble, check_deadline, decode,
)

OPERATION_SECONDS = 3.0
UNWIND_RESERVE_SECONDS = 0.1
ACTIVE = 'KDG_ACTOR_DISPLAY_SERVICE_KEY'
PREVIOUS = 'KDG_ACTOR_DISPLAY_PREVIOUS_SERVICE_KEY'
ORG = 'KDG_ACTOR_DISPLAY_ORG_ID'
Reader = Callable[[tuple[UUID, ...], float], Awaitable[Iterable[dict]]]
NO_STORE = {'Cache-Control': 'private, no-store'}


class ActorDisplayPolicy:
    """Credential custody stays redacted, including disabled/invalid construction."""
    __slots__ = ('_active', '_previous', '_org')

    def __repr__(self):
        return '<ActorDisplayPolicy redacted>'

    def __init__(self, configuration: Mapping[str, str]):
        self._active = self._previous = self._org = None
        try:
            if not any(key in configuration for key in (ACTIVE, PREVIOUS, ORG)):
                return
            active, previous, org = configuration[ACTIVE], configuration.get(PREVIOUS), configuration[ORG]
            from actor_display_contract import canonical_uuid
            canonical_uuid(org)
            keys = [active] + ([previous] if PREVIOUS in configuration else [])
            for key in keys:
                if not isinstance(key, str) or not 32 <= len(key) <= 256 or any(not 33 <= ord(c) <= 126 for c in key):
                    raise ValueError()
            if previous is not None and hmac.compare_digest(active, previous):
                raise ValueError()
            for name, value in configuration.items():
                if name not in (ACTIVE, PREVIOUS) and name.endswith('_SERVICE_KEY') and isinstance(value, str):
                    if any(hmac.compare_digest(key.encode('ascii'), value.encode('utf-8')) for key in keys):
                        raise ValueError()
            self._active = active.encode('ascii')
            self._previous = previous.encode('ascii') if previous is not None else None
            self._org = org
        except Exception:
            raise RuntimeError('actor_display_configuration_invalid') from None

    def permits_headers(self, headers) -> bool:
        values = headers.getlist('x-service-key')
        if self._active is None or len(values) != 1 or 'authorization' in headers:
            return False
        if not 32 <= len(values[0]) <= 256:
            return False
        supplied = values[0].encode('utf-8')
        active = hmac.compare_digest(supplied, self._active)
        previous = hmac.compare_digest(supplied, self._previous or b'')
        return active or previous

    def permits_org(self, org: str) -> bool:
        return org == self._org


def error_response(status: int) -> JSONResponse:
    model = {403: ActorDisplayDenied, 422: ActorDisplayInvalid, 503: ActorDisplayUnavailable}[status]
    return JSONResponse(model().model_dump(), status_code=status, headers=NO_STORE)


@dataclass(frozen=True, repr=False)
class _ReadOutcome:
    rows: object = None
    error: Exception | None = None

    def __repr__(self):
        return '<_ReadOutcome private>'


async def _reader_outcome(reader: Reader, selected: tuple[UUID, ...], deadline: float):
    # Python3.15 shield logs raw task exceptions after outer cancellation, even
    # if the owner retrieves them later. The shielded task must finish privately.
    try:
        return _ReadOutcome(rows=await reader(selected, deadline))
    except Exception as error:
        return _ReadOutcome(error=error)


async def read_owned(reader: Reader, selected: tuple[UUID, ...], deadline: float):
    """Keep ownership through cancellation, including repeated caller cancellation.

    The original outer timeout remains active while cleanup is awaited. Readers
    must release on cancellation; at the absolute deadline a second cancellation
    interrupts a cleanup that exhausted the reserve. No detached read is allowed.
    """
    task = asyncio.create_task(_reader_outcome(reader, selected, deadline))
    try:
        outcome = await asyncio.shield(task)
    except asyncio.CancelledError:
        task.cancel()
        while not task.done():
            try:
                await asyncio.shield(task)
            except asyncio.CancelledError:
                if time.monotonic() >= deadline:
                    task.cancel()
        # Consume the private outcome without unwrapping a cancelled attempt.
        if task.done() and not task.cancelled():
            task.result()
        raise
    if outcome.error is not None:
        raise outcome.error from None
    return outcome.rows


def create_router(configuration: Mapping[str, str], reader: Reader) -> APIRouter:
    policy = ActorDisplayPolicy(configuration)
    router = APIRouter()

    @router.post('/v2/identity/actor-displays', response_model=ActorDisplayResponse,
                 operation_id='identity_actor_displays',
                 dependencies=[Security(APIKeyHeader(name='X-Service-Key', scheme_name='KdgActorDisplayKey', auto_error=False))],
                 responses={403: {'model': ActorDisplayDenied}, 422: {'model': ActorDisplayInvalid},
                            503: {'model': ActorDisplayUnavailable}})
    async def actor_displays(request: Request):
        deadline = time.monotonic() + OPERATION_SECONDS
        if not policy.permits_headers(request.headers):
            return error_response(403)
        try:
            async with asyncio.timeout_at(deadline):
                # Read cancellation and its owned unwind share the same total timer.
                async with asyncio.timeout_at(deadline - UNWIND_RESERVE_SECONDS):
                    if request.query_params or request.headers.get('content-type', '').split(';', 1)[0].strip().lower() != 'application/json':
                        return error_response(422)
                    try:
                        body = await decode(request, deadline)
                    except TimeoutError:
                        raise
                    except Exception:
                        return error_response(422)
                    if not policy.permits_org(body.org_id):
                        return error_response(403)
                    rows = await read_owned(reader, tuple(UUID(value) for value in body.actor_ids), deadline)
                    result = assemble(body, rows, deadline)
                    response = JSONResponse(result.model_dump(), headers=NO_STORE)
                    if len(response.body) > RESPONSE_BYTES:
                        raise ValueError('response')
                    check_deadline(deadline)
                    return response
        except Exception:
            return error_response(503)

    # Keep the body explicit without FastAPI's open validation-error envelope.
    schema = ActorDisplayRequest.model_json_schema()
    router.routes[0].openapi_extra = {'requestBody': {'required': True, 'content': {'application/json': {'schema': schema}}}}
    return router


def create_app(configuration: Mapping[str, str], reader: Reader) -> FastAPI:
    app = FastAPI(title='Identity historical actor display candidate', version='1.0.0',
                  docs_url=None, redoc_url=None, openapi_url=None)
    app.include_router(create_router(configuration, reader))
    return app
