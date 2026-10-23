"""Pure preparation declarations; parsing confers no owner admission or authority."""
from dataclasses import dataclass
import json
import re
from typing import Literal
from uuid import UUID

from apps.scribeswell.migrations.release_profile import validate_custody

MAX_REQUEST_BYTES = 8192
MAX_DEPTH = 4
_FIELDS = frozenset(('schema_version', 'command', 'run_id', 'custody', 'preparer_actor_id',
                    'target_plan_ref', 'identity_observation_ref', 'session_authorization_ref',
                    'release_binding_ref'))
_REFERENCES = ('target_plan_ref', 'identity_observation_ref', 'session_authorization_ref', 'release_binding_ref')
_REFERENCE = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}', re.ASCII)


class PreparationRequestError(ValueError):
    """One safe code for invalid declarations, with no input/decoder context."""
    code = 'scribeswell_preparation_request_invalid'

    def __init__(self):
        super().__init__(self.code)


@dataclass(frozen=True, slots=True, repr=False)
class PreparationCustody:
    schema_version: Literal[1]
    source_id: str
    executor_actor_id: str
    actor_kind: Literal['service']
    actor_key: str
    preparation_evidence_ref: str


@dataclass(frozen=True, slots=True, repr=False)
class PreparationRequest:
    schema_version: Literal[1]
    command: Literal['caller.prepare_initial']
    run_id: str
    custody: PreparationCustody
    preparer_actor_id: str
    target_plan_ref: str
    identity_observation_ref: str
    session_authorization_ref: str
    release_binding_ref: str


def _require(condition):
    if not condition:
        raise ValueError()


def _pairs(items):
    value = {}
    for key, item in items:
        _require(key not in value)
        value[key] = item
    return value


def _reject_number(raw):
    raise ValueError()


def _integer(raw):
    # The only numeric fields admitted by this request are integer version 1.
    _require(raw == '1')
    return 1


def _uuid(value):
    _require(type(value) is str)
    identity = UUID(value)
    _require(identity.int != 0 and str(identity) == value)


def _depth(value):
    pending = [(value, 1)]
    while pending:
        item, depth = pending.pop()
        if type(item) in (dict, list):
            _require(depth <= MAX_DEPTH)
            pending.extend((child, depth+1) for child in
                           (item.values() if type(item) is dict else item))


def _parse(raw):
    _require(type(raw) is bytes and len(raw) <= MAX_REQUEST_BYTES)
    text = raw.decode('utf-8', errors='strict')
    _require(not text.startswith('\ufeff'))
    value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_reject_number,
                       parse_float=_reject_number, parse_int=_integer)
    _depth(value)
    _require(type(value) is dict and value.keys() == _FIELDS)
    _require(type(value['schema_version']) is int and value['schema_version'] == 1)
    _require(type(value['command']) is str and value['command'] == 'caller.prepare_initial')
    _uuid(value['run_id'])
    _uuid(value['preparer_actor_id'])
    for key in _REFERENCES:
        _require(type(value[key]) is str and _REFERENCE.fullmatch(value[key]) is not None)
    custody = PreparationCustody(**validate_custody(value['custody']))
    return PreparationRequest(**(value | {'custody':custody}))


def parse_preparation_request(raw: bytes) -> PreparationRequest:
    """Validate/freeze v1 syntax only; no references are resolved or authenticated."""
    try:
        return _parse(raw)
    except (ValueError, TypeError, RecursionError, OverflowError):
        pass
    # Outside the handler: JSON/Unicode/custody exceptions can retain raw input.
    try:
        raise PreparationRequestError() from None
    except PreparationRequestError as error:
        # Even outside our handler, Python attaches a caller's active exception.
        # Clear the real link, then bare-reraise without attaching it again.
        error.__context__ = None
        raise
