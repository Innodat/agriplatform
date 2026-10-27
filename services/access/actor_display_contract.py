"""Closed, bounded historical display wire contract, independent of account state."""
import json
import time
import unicodedata
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, AfterValidator

REQUEST_BYTES = 16 * 1024
RESPONSE_BYTES = 256 * 1024
MAX_ACTORS = 203


def canonical_uuid(value: str) -> str:
    parsed = UUID(value)
    if not parsed.int or str(parsed) != value:
        raise ValueError('uuid')
    return value


ActorUUID = Annotated[str, Field(strict=True, pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'), AfterValidator(canonical_uuid)]


def display_name(value: str) -> str:
    if not value.strip() or any(unicodedata.category(c) in ('Cc', 'Cs') for c in value):
        raise ValueError('display_name')
    if len(value.encode('utf-8')) > 1024:
        raise ValueError('display_name')
    return value


DisplayName = Annotated[str, Field(strict=True, min_length=1, max_length=256), AfterValidator(display_name)]


class Closed(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, json_schema_serialization_defaults_required=True)


def ordered_unique(ids: list[str]) -> list[str]:
    if ids != sorted(set(ids)):
        raise ValueError('actor_ids')
    return ids


class ActorDisplayRequest(Closed):
    org_id: ActorUUID
    actor_ids: Annotated[list[ActorUUID], Field(min_length=1, max_length=MAX_ACTORS), AfterValidator(ordered_unique)]


class ResolvedActorDisplay(Closed):
    actor_id: ActorUUID
    status: Literal['resolved']
    display_name: DisplayName


class UnavailableActorDisplay(Closed):
    actor_id: ActorUUID
    status: Literal['unavailable']


ActorLabel = Annotated[ResolvedActorDisplay | UnavailableActorDisplay, Field(discriminator='status')]


class ActorDisplayResponse(Closed):
    org_id: ActorUUID
    labels: Annotated[list[ActorLabel], Field(min_length=1, max_length=MAX_ACTORS)]


class DisplayError(Closed):
    error: Literal['Request could not be completed'] = 'Request could not be completed'
    details: Closed = Field(default_factory=Closed)


class ActorDisplayDenied(DisplayError):
    error_id: Literal['service_access_denied'] = 'service_access_denied'


class ActorDisplayInvalid(DisplayError):
    error_id: Literal['validation_failed'] = 'validation_failed'


class ActorDisplayUnavailable(DisplayError):
    error_id: Literal['identity.actor_display_unavailable'] = 'identity.actor_display_unavailable'


def check_deadline(deadline: float) -> None:
    if time.monotonic() >= deadline:
        raise TimeoutError()


def closed_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate')
        result[key] = value
    return result


def reject_constant(_):
    raise ValueError('constant')


async def decode(request, deadline: float) -> ActorDisplayRequest:
    """Caller owns the original timeout; no per-phase timer is started here."""
    raw = bytearray()
    async for chunk in request.stream():
        check_deadline(deadline)
        if len(raw) + len(chunk) > REQUEST_BYTES:
            raise ValueError('body')
        raw.extend(chunk)
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=closed_object, parse_constant=reject_constant)
    result = ActorDisplayRequest.model_validate(value)
    check_deadline(deadline)
    return result


def assemble(body: ActorDisplayRequest, rows, deadline: float) -> ActorDisplayResponse:
    """Bound even a lazy projection and reject every row outside its narrow shape."""
    found = {}
    requested = set(body.actor_ids)
    iterator = iter(rows)
    try:
        for index, row in enumerate(iterator):
            check_deadline(deadline)
            if index >= len(requested) or type(row) is not dict or set(row) != {'actor_id', 'display_name'}:
                raise ValueError('projection')
            actor = row['actor_id']
            if not isinstance(actor, UUID) or not actor.int:
                raise ValueError('projection')
            actor_id = str(actor)
            if actor_id not in requested or actor_id in found:
                raise ValueError('projection')
            found[actor_id] = ResolvedActorDisplay(actor_id=actor_id, status='resolved', display_name=row['display_name'])
    finally:
        close = getattr(iterator, 'close', None)
        if close is not None:
            close()
    check_deadline(deadline)
    return ActorDisplayResponse(org_id=body.org_id, labels=[
        found.get(actor_id) or UnavailableActorDisplay(actor_id=actor_id, status='unavailable')
        for actor_id in body.actor_ids
    ])
