"""Closed canonical Access contracts; no account selectors or replayable authority."""
import asyncio
import json
from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator

class Closed(BaseModel):
    model_config=ConfigDict(extra='forbid')

class CapabilityAccountScope(Closed):
    kind: Literal['account']

class CapabilityOrganizationScope(Closed):
    kind: Literal['organization']
    org_id: UUID
    @field_validator('org_id')
    @classmethod
    def nonzero(cls,value):
        if not value.int:raise ValueError('scope')
        return value

Scope=Annotated[CapabilityAccountScope | CapabilityOrganizationScope,Field(discriminator='kind')]
class CapabilityCheck(Closed):
    permission: Annotated[str,Field(strict=True,min_length=1,max_length=200)]
    authorization_scope: Scope

class OwnResource(Closed):
    kind: Literal['own']
    person_id: UUID

class CommonDecision(Closed):
    account_id: UUID
    actor_id: UUID
    permission: str
    authorization_scope: Scope
    decision_id: UUID
    checked_at: datetime

class CapabilityAccountDecision(CommonDecision):
    authorization_scope: CapabilityAccountScope

class OwnDecision(CommonDecision):
    authorization_scope: CapabilityOrganizationScope
    person_id: UUID
    membership_id: Annotated[str,Field(pattern=r'^[1-9][0-9]{0,18}$')]
    resource_scope: OwnResource

class CapabilityOrganizationDecision(CommonDecision):
    authorization_scope: CapabilityOrganizationScope
    membership_id: Annotated[str,Field(pattern=r'^[1-9][0-9]{0,18}$')]
    resource_scope: CapabilityOrganizationScope

class ContextInput(Closed):
    org_id: UUID
    @field_validator('org_id')
    @classmethod
    def nonzero(cls,value):
        if not value.int:raise ValueError('scope')
        return value

class OrganizationContext(Closed):
    account_id: UUID
    actor_id: UUID
    org_id: UUID
    membership_id: Annotated[str,Field(pattern=r'^[1-9][0-9]{0,18}$')]
    person_id: UUID | None
    observation_id: UUID
    checked_at: datetime

class CapabilityError(Closed):
    error_id: Literal['authentication_required','service_access_denied','access_denied',
        'validation_failed','identity.actor_setup_required','identity.person_link_required',
        'identity.verification_required','authorization_unavailable']
    error: str='Request could not be completed'
    details: Closed=Field(default_factory=Closed)


def closed_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate')
        result[key]=value
    return result

BODY_RECEIVE_SECONDS=3.0

async def decode(request,model):
    raw=bytearray()
    async with asyncio.timeout(BODY_RECEIVE_SECONDS):
        async for chunk in request.stream():
            raw.extend(chunk)
            if len(raw)>65536:raise ValueError('body')
    value=json.loads(raw.decode('utf-8'),object_pairs_hook=closed_object,
        parse_constant=lambda _:(_ for _ in ()).throw(ValueError('constant')))
    return model.model_validate(value)
