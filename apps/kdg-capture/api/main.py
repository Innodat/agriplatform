"""Read-only KDG context API. Explicit configuration; no startup migration or grants."""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import json
import re
from urllib.parse import urlsplit

from fastapi import FastAPI, Request, Security
from fastapi.security import HTTPBearer
import httpx

from context import Context, PERMISSION, canonical_uuid
from safe_errors import ErrorEnvelope, install_safe_errors, response

REQUEST_SECONDS = 10.0
ACCESS_SECONDS = 3.0
MAX_RESPONSE_BYTES = 16384


def closed_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('invalid_response')
        result[key] = value
    return result


def create_app(*, org_id=None, access_url=None, service_key=None, transport=None):
    configured = any(value is not None for value in (org_id, access_url, service_key))
    if configured:
        try:
            canonical_uuid(org_id)
            url = urlsplit(access_url)
            if (url.scheme != 'https' or not url.hostname or url.username or url.password
                    or url.query or url.fragment or url.path not in ('', '/')
                    or url.netloc.endswith(':') or (url.port is not None and url.port == 0)
                    or not isinstance(service_key, str) or not service_key
                    or any(not 33 <= ord(c) <= 126 for c in service_key)):
                raise ValueError('configuration')
        except (ValueError, TypeError, AttributeError):
            raise RuntimeError('kdg_context_configuration_invalid') from None

    @asynccontextmanager
    async def lifespan(app):
        async with httpx.AsyncClient(transport=transport, timeout=ACCESS_SECONDS,
                                     follow_redirects=False, trust_env=False) as client:
            app.state.access_client = client
            yield

    app = FastAPI(title='KDG Capture context API', version='1.0.0', lifespan=lifespan,
                  docs_url=None, redoc_url=None, openapi_url=None)
    install_safe_errors(app)

    @app.middleware('http')
    async def private(request, call_next):
        result = await call_next(request)
        result.headers['Cache-Control'] = 'private, no-store'
        return result

    def failure(status, code):
        return response(status, code, 'The request could not be completed.',
                        {'WWW-Authenticate': 'Bearer'} if status == 401 else None)

    @app.get('/api/v1/context', response_model=Context, operation_id='current_context',
             dependencies=[Security(HTTPBearer(auto_error=False))],
             responses={status: {'model': ErrorEnvelope} for status in (401, 403, 409, 422, 500, 503)})
    async def current_context(request: Request):
        # No selectors, even unknown ones, and no request body on this GET boundary.
        if request.query_params:
            return failure(422, 'validation_failed')
        token = request.headers.get('authorization', '')
        if len(request.headers.getlist('authorization')) != 1 or not re.fullmatch(r'Bearer [\x21-\x7e]+', token, flags=re.IGNORECASE):
            return failure(401, 'authentication_required')
        token = 'Bearer ' + token.split(' ', 1)[1]
        if not configured:
            return failure(503, 'authorization_unavailable')
        try:
            async with asyncio.timeout(REQUEST_SECONDS):
                async for chunk in request.stream():
                    if chunk:
                        return failure(422, 'validation_failed')
                observed_start = datetime.now(timezone.utc)
                # A single wall-clock timeout bounds all transport/body waits together.
                async with asyncio.timeout(ACCESS_SECONDS):
                    async with app.state.access_client.stream('POST', access_url.rstrip('/')+'/v2/check',
                        headers={'Authorization': token, 'X-Service-Key': service_key, 'Accept-Encoding': 'identity'},
                        json={'permission': PERMISSION, 'authorization_scope': {'kind': 'organization', 'org_id': org_id}}) as upstream:
                        if upstream.headers.get('content-encoding', '').strip().lower() not in ('', 'identity'):
                            raise ValueError('unsupported_encoding')
                        raw = bytearray()
                        async for chunk in upstream.aiter_bytes():
                            raw.extend(chunk)
                            if len(raw) > MAX_RESPONSE_BYTES:
                                raise ValueError('invalid_response')
                        body = json.loads(raw.decode('utf-8'), object_pairs_hook=closed_object,
                                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError('invalid_response')))
                        if upstream.status_code != 200:
                            code = body.get('detail', {}).get('code') if isinstance(body, dict) and isinstance(body.get('detail'), dict) else None
                            allowed = {(401, 'authentication_required'), (403, 'access_denied'),
                                       (409, 'identity.actor_setup_required')}
                            if (upstream.status_code, code) in allowed:
                                return failure(upstream.status_code, code)
                            return failure(503, 'authorization_unavailable')
                evidence = Context.model_validate(body)
                now = datetime.now(timezone.utc)
                if (evidence.authorization_scope.org_id != org_id
                    or evidence.resource_scope.account_id != evidence.account_id
                    or not observed_start-timedelta(seconds=1) <= evidence.checked_at <= now+timedelta(seconds=1)):
                    raise ValueError('invalid_authority')
                return evidence
        except (httpx.HTTPError, TimeoutError, ValueError, TypeError, RecursionError):
            return failure(503, 'authorization_unavailable')

    return app


# Unconfigured imports/export are safe; an embedding owner explicitly supplies policy.
app = create_app()
