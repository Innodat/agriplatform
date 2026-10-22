"""KDG's closed current-entry DTO. This evidence is never an offline lease."""
from datetime import datetime, timezone
import re
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

PERMISSION = 'kdg_capture.capture.read.own'
_UUID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z')


def canonical_uuid(value):
    if not isinstance(value, str) or not _UUID.fullmatch(value) or not UUID(value).int:
        raise ValueError('invalid_identifier')
    return value


class Closed(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, hide_input_in_errors=True)


Identifier = Annotated[str, Field(json_schema_extra={
    'format': 'uuid', 'pattern': _UUID.pattern.removesuffix(r'\Z') + '$',
    'not': {'const': '00000000-0000-0000-0000-000000000000'}})]


def positive_bigint_pattern():
    # All shorter positive decimals, then each first differing lower digit of max.
    maximum = '9223372036854775807'
    choices = [r'[1-9][0-9]{0,17}', maximum]
    for index, digit in enumerate(maximum):
        low, high = (1 if index == 0 else 0), int(digit)-1
        if high >= low:
            choices.append(maximum[:index] + f'[{low}-{high}]' + f'[0-9]{{{18-index}}}')
    return '^(?:' + '|'.join(choices) + ')$'


MEMBERSHIP_PATTERN = positive_bigint_pattern()


class OrganizationScope(Closed):
    kind: Literal['organization']
    org_id: Identifier
    _id = field_validator('org_id')(canonical_uuid)


class OwnAccountScope(Closed):
    kind: Literal['own_account']
    account_id: Identifier
    _id = field_validator('account_id')(canonical_uuid)


class Context(Closed):
    account_id: Identifier
    actor_id: Identifier
    membership_id: Annotated[str, Field(strict=True, pattern=MEMBERSHIP_PATTERN)]
    authorization_scope: OrganizationScope
    resource_scope: OwnAccountScope
    permission: Literal['kdg_capture.capture.read.own']
    decision_id: Identifier
    checked_at: Annotated[datetime, Field(strict=False)]
    _ids = field_validator('account_id', 'actor_id', 'decision_id')(canonical_uuid)

    @field_validator('membership_id')
    @classmethod
    def member(cls, value):
        if not re.fullmatch(r'[1-9][0-9]{0,18}', value) or int(value) > 9223372036854775807:
            raise ValueError('invalid_membership')
        return value

    @field_validator('checked_at', mode='before')
    @classmethod
    def utc_time(cls, value):
        if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z', value):
            raise ValueError('invalid_time')
        parsed = datetime.fromisoformat(value)
        if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
            raise ValueError('invalid_time')
        return parsed
