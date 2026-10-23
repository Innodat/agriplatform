"""KDG's current selected-organization check. No decision is reusable authority."""
import asyncio
import json
import secrets
from datetime import datetime, timezone
from typing import Annotated, Literal
from uuid import UUID, uuid4

from starlette.concurrency import run_in_threadpool
from fastapi import APIRouter, Header, HTTPException, Request, Security
from fastapi.security import APIKeyHeader, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from studies_contract import AccountCheck, AccountDecision, StudiesError, inline_schema
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

OWN_PERMISSIONS = frozenset('kdg_capture.' + suffix for suffix in (
    'capture.create.assigned', 'capture.create.all', 'capture.read.own', 'capture.edit.own'))
ORG_PERMISSIONS = frozenset('kdg_capture.' + suffix for suffix in (
    'capture.read.all', 'capture.edit.all', 'questionnaire.manage', 'child.manage', 'assignment.manage'))
PERMISSIONS = OWN_PERMISSIONS | ORG_PERMISSIONS
BODY_RECEIVE_TIMEOUT = 3.0

class Closed(BaseModel):
    model_config = ConfigDict(extra='forbid')

class OrganizationScope(Closed):
    kind: Literal['organization']
    org_id: UUID

class OwnAccountScope(Closed):
    kind: Literal['own_account']
    account_id: UUID

class OrganizationCheck(Closed):
    permission: Annotated[str, Field(strict=True, min_length=1, max_length=200)]
    authorization_scope: OrganizationScope

class OrganizationDecision(Closed):
    account_id: UUID
    actor_id: UUID
    permission: str
    authorization_scope: OrganizationScope
    decision_id: UUID
    checked_at: datetime
    membership_id: Annotated[str, Field(pattern=r'^[1-9][0-9]{0,18}$')]
    resource_scope: Annotated[OwnAccountScope | OrganizationScope, Field(discriminator='kind')]

class ErrorDetails(Closed):
    code: str

class CheckError(Closed):
    detail: ErrorDetails


def _closed_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate')
        result[key] = value
    return result


def router(db, authenticate, environment, studies=None):
    routes = APIRouter()
    key, org = environment.get('KDG_SERVICE_KEY', ''), environment.get('KDG_ORG_ID', '')
    configured_org = None
    if key or org:
        try:
            configured_org = UUID(org)
            if not key or not configured_org.int or any(not 33 <= ord(c) <= 126 for c in key):
                raise ValueError('configuration')
        except (ValueError, TypeError):
            raise RuntimeError('kdg_check_configuration_invalid') from None
        if key in (environment.get('PTS_SERVICE_KEY'), environment.get('CONTENT_SERVICE_KEY')):
            raise RuntimeError('kdg_check_configuration_invalid')

    @routes.post('/v2/check', response_model=OrganizationDecision | AccountDecision,
        dependencies=[Security(HTTPBearer(scheme_name='KdgBearer', auto_error=False)),
                      Security(APIKeyHeader(name='X-Service-Key', scheme_name='KdgServiceKey', auto_error=False))],
        responses={status: {'model': CheckError | StudiesError} for status in (401, 403, 409, 422, 503)})
    async def check(request: Request, authorization: str = Header(default=''), x_service_key: str = Header(default='')):
        if studies is not None and studies.matches(x_service_key):
            return await studies.handle(request, authorization, x_service_key)
        if not key or not x_service_key or not secrets.compare_digest(key.encode('utf-8'), x_service_key.encode('utf-8')):
            raise HTTPException(403, {'code': 'service_access_denied'})
        try:
            raw = bytearray()
            async with asyncio.timeout(BODY_RECEIVE_TIMEOUT):
                async for chunk in request.stream():
                    raw.extend(chunk)
                    if len(raw) > 65536:
                        raise ValueError('body')
            value = json.loads(raw.decode('utf-8'), object_pairs_hook=_closed_object,
                parse_constant=lambda _: (_ for _ in ()).throw(ValueError('constant')))
            body = OrganizationCheck.model_validate(value)
            if not body.authorization_scope.org_id.int:
                raise ValueError('scope')
        except (ValueError, ValidationError, UnicodeError, RecursionError, TimeoutError):
            raise HTTPException(422, {'code': 'validation_failed'}) from None
        if body.permission not in PERMISSIONS or body.authorization_scope.org_id != configured_org:
            raise HTTPException(403, {'code': 'service_access_denied'})
        return await run_in_threadpool(execute, body, authorization)

    def execute(body, authorization):
        account = authenticate(authorization)
        try:
            with db.begin() as conn:
                conn.execute(text('SET TRANSACTION READ ONLY'))
                conn.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true),set_config('app.actor_id','',true),set_config('app.org_id',:org,true),set_config('statement_timeout','3000',true),set_config('lock_timeout','1000',true),set_config('idle_in_transaction_session_timeout','5000',true)"),
                    {'account': str(account), 'org': str(configured_org)})
                row = conn.execute(text('SELECT account_id,org_id,membership_id,actor_id FROM access.check_organization_permission(:permission)'), {'permission': body.permission}).mappings().one_or_none()
        except SQLAlchemyError:
            raise HTTPException(503, {'code': 'authorization_unavailable'}) from None
        if row is None:
            raise HTTPException(403, {'code': 'access_denied'})
        # Never turn a malformed/foreign owner response into usable authority.
        try:
            if UUID(str(row['account_id'])) != account or UUID(str(row['org_id'])) != configured_org:
                raise ValueError('binding')
            member = int(row['membership_id'])
            if type(row['membership_id']) is not int or not 0 < member <= 9223372036854775807:
                raise ValueError('membership')
            actor = row['actor_id']
            if actor is not None and not UUID(str(actor)).int:
                raise ValueError('actor')
        except (ValueError, TypeError, KeyError):
            raise HTTPException(503, {'code': 'authorization_unavailable'}) from None
        if actor is None:
            raise HTTPException(409, {'code': 'identity.actor_setup_required'})
        return OrganizationDecision(account_id=account, actor_id=actor, permission=body.permission,
            authorization_scope=body.authorization_scope, membership_id=str(member),
            decision_id=uuid4(), checked_at=datetime.now(timezone.utc),
            resource_scope=OwnAccountScope(kind='own_account', account_id=account) if body.permission in OWN_PERMISSIONS else body.authorization_scope)

    # Request decoding is deliberately strict; publish the same explicit owner DTO.
    check.__annotations__['return'] = OrganizationDecision
    schema = OrganizationCheck.model_json_schema()
    definitions = schema.pop('$defs', {})
    def inline(value):
        if isinstance(value, dict):
            if '$ref' in value:
                return inline(definitions[value['$ref'].rsplit('/', 1)[1]])
            return {name: inline(item) for name, item in value.items()}
        if isinstance(value, list):
            return [inline(item) for item in value]
        return value
    request_schema=inline(schema)
    if studies is not None:
        request_schema={'oneOf':[request_schema,inline_schema(AccountCheck)]}
    routes.routes[0].openapi_extra = {'requestBody': {'required': True, 'content': {'application/json': {'schema': request_schema}}}}
    return routes
