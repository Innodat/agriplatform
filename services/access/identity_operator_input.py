"""Strict Identity setup input parsing only; these values convey no authority."""
from dataclasses import dataclass, field
import json
import math
import re
from typing import Literal


class CommandValidationError(ValueError):
    """Safe, fixed validation failure without submitted input or decoder text."""

    code = 'identity_operator_input_invalid'

    def __init__(self) -> None:
        super().__init__(self.code)


ReasonCode = Literal['initial_setup', 'synthetic_fixture', 'identity_adoption',
                     'access_change', 'setup_correction']


@dataclass(frozen=True, repr=False)
class PlatformScope:
    kind: Literal['platform'] = field(default='platform', init=False)


@dataclass(frozen=True, repr=False)
class OrganizationScope:
    org_id: str
    kind: Literal['organization'] = field(default='organization', init=False)


@dataclass(frozen=True, repr=False)
class RegisterSystemPayload:
    actor_id: str
    kind: Literal['system', 'service']
    actor_key: str
    display_name: str
    expected_absent: Literal[True]


@dataclass(frozen=True, repr=False)
class EnsureAccountActorPayload:
    account_id: str
    actor_id: str
    display_name: str
    expected_absent: Literal[True]


@dataclass(frozen=True, repr=False)
class JoinMembershipPayload:
    account_id: str
    expected_previous_membership_id: str | None
    is_owner: bool = False


@dataclass(frozen=True, repr=False)
class RetireMembershipPayload:
    account_id: str
    membership_id: str
    expected_revision: str


@dataclass(frozen=True, repr=False)
class _Envelope:
    schema_version: Literal[1]
    operation_id: str
    reason_code: ReasonCode
    evidence_ref: str | None


@dataclass(frozen=True, repr=False)
class RegisterSystemCommand(_Envelope):
    scope: PlatformScope
    payload: RegisterSystemPayload
    command: Literal['actor.register_system'] = field(default='actor.register_system', init=False)


@dataclass(frozen=True, repr=False)
class EnsureAccountActorCommand(_Envelope):
    scope: PlatformScope
    payload: EnsureAccountActorPayload
    command: Literal['account_actor.ensure'] = field(default='account_actor.ensure', init=False)


@dataclass(frozen=True, repr=False)
class JoinMembershipCommand(_Envelope):
    scope: OrganizationScope
    payload: JoinMembershipPayload
    command: Literal['membership.join'] = field(default='membership.join', init=False)


@dataclass(frozen=True, repr=False)
class RetireMembershipCommand(_Envelope):
    scope: OrganizationScope
    payload: RetireMembershipPayload
    command: Literal['membership.retire'] = field(default='membership.retire', init=False)


@dataclass(frozen=True, repr=False)
class CreatePersonPayload:
    person_id: str
    expected_absent: Literal[True]


@dataclass(frozen=True, repr=False)
class LinkPersonPayload:
    account_id: str
    person_id: str
    actor_id: str
    expected_absent: Literal[True] | None = None
    expected_revision: str | None = None


@dataclass(frozen=True, repr=False)
class CreatePersonCommand(_Envelope):
    scope: PlatformScope
    payload: CreatePersonPayload
    command: Literal['person.create'] = field(default='person.create', init=False)


@dataclass(frozen=True, repr=False)
class LinkPersonCommand(_Envelope):
    scope: PlatformScope
    payload: LinkPersonPayload
    command: Literal['account.link_person'] = field(default='account.link_person', init=False)


Command = CreatePersonCommand | LinkPersonCommand | RegisterSystemCommand | EnsureAccountActorCommand | JoinMembershipCommand | RetireMembershipCommand
_UUID = re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')
_DECIMAL = re.compile(r'[1-9][0-9]{0,18}')
_ACTOR_KEY = re.compile(r'[a-z][a-z0-9_.:-]{0,127}')
_EVIDENCE = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}')
_REASONS = frozenset(('initial_setup', 'synthetic_fixture', 'identity_adoption', 'access_change', 'setup_correction'))
# Exact Unicode White_Space set used by the actor database CHECK, not str.isspace().
_WHITE_SPACE = '\u0009\u000a\u000b\u000c\u000d\u0020\u0085\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000'


def _require(condition: bool) -> None:
    if not condition:
        raise CommandValidationError()


def _object(value: object, required: set[str], optional: set[str] = frozenset()) -> dict:
    _require(type(value) is dict)
    _require(required <= value.keys() <= required | optional)
    return value


def _uuid(value: object) -> str:
    _require(type(value) is str and _UUID.fullmatch(value) is not None)
    _require(value != '00000000-0000-0000-0000-000000000000')
    return value


def _decimal(value: object) -> str:
    _require(type(value) is str and _DECIMAL.fullmatch(value) is not None)
    _require(int(value) <= 9223372036854775807)
    return value


def _display(value: object) -> str:
    _require(type(value) is str and 1 <= len(value) <= 200 and bool(value.strip(_WHITE_SPACE)))
    return value


def _pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        _require(key not in result)
        result[key] = value
    return result


def _integer(value: str) -> int:
    # Bound conversion independently of the interpreter's configurable integer limit.
    _require(len(value.lstrip('-')) <= 19)
    return int(value)


def _nonfinite(value: str) -> None:
    raise CommandValidationError()


def _check_text(value: object) -> None:
    """Reject forbidden characters even in keys and otherwise rejected structures."""
    if type(value) is str:
        _require(not any(c == '\x00' or 0xD800 <= ord(c) <= 0xDFFF for c in value))
    elif type(value) is dict:
        for key, child in value.items():
            _check_text(key)
            _check_text(child)
    elif type(value) is list:
        for child in value:
            _check_text(child)
    elif type(value) is float:
        _require(math.isfinite(value))


def _decode(body: bytes) -> object:
    _require(type(body) is bytes and len(body) <= 65536)
    # Raise outside decoder exception handling so neither repr nor chained traceback
    # exposes JSONDecodeError's submitted document or UnicodeDecodeError's bytes.
    failed = False
    try:
        text = body.decode('utf-8', errors='strict')
        _require(not text.startswith('\ufeff'))
        decoded = json.loads(text, object_pairs_hook=_pairs, parse_int=_integer,
                             parse_constant=_nonfinite)
        _check_text(decoded)
    except (ValueError, RecursionError):
        failed = True
    if failed:
        raise CommandValidationError()
    return decoded


def parse_command(body: bytes) -> Command:
    """Parse one closed version-1 command; perform no I/O or authorization checks."""
    doc = _object(_decode(body), {'schema_version', 'operation_id', 'command', 'scope', 'payload', 'reason_code'}, {'evidence_ref'})
    _require(type(doc['schema_version']) is int and doc['schema_version'] == 1)
    operation_id = _uuid(doc['operation_id'])
    reason = doc['reason_code']
    _require(type(reason) is str and reason.isascii() and len(reason) <= 128 and reason in _REASONS)
    evidence = doc.get('evidence_ref')
    if 'evidence_ref' in doc:
        _require(type(evidence) is str and _EVIDENCE.fullmatch(evidence) is not None and '://' not in evidence)
    common = dict(schema_version=1, operation_id=operation_id, reason_code=reason, evidence_ref=evidence)
    name = doc['command']
    _require(type(name) is str)
    if name in ('person.create', 'account.link_person'):
        scope = _object(doc['scope'], {'kind'})
        _require(scope['kind'] == 'platform')
        scope = PlatformScope()
        if name == 'person.create':
            payload = _object(doc['payload'], {'person_id','expected_absent'})
            _require(payload['expected_absent'] is True)
            return CreatePersonCommand(**common, scope=scope, payload=CreatePersonPayload(_uuid(payload['person_id']),True))
        payload = _object(doc['payload'], {'account_id','person_id','actor_id'}, {'expected_absent','expected_revision'})
        _require(evidence is not None and (('expected_absent' in payload) != ('expected_revision' in payload)))
        absent = payload.get('expected_absent')
        revision = payload.get('expected_revision')
        if 'expected_absent' in payload:
            _require(absent is True)
        else:
            revision = _decimal(revision)
        return LinkPersonCommand(**common, scope=scope, payload=LinkPersonPayload(_uuid(payload['account_id']),_uuid(payload['person_id']),_uuid(payload['actor_id']),absent,revision))
    if name in ('actor.register_system', 'account_actor.ensure'):
        scope = _object(doc['scope'], {'kind'})
        _require(scope['kind'] == 'platform')
        scope = PlatformScope()
        if name == 'actor.register_system':
            payload = _object(doc['payload'], {'actor_id', 'kind', 'actor_key', 'display_name', 'expected_absent'})
            _require(type(payload['kind']) is str and payload['kind'] in ('system', 'service'))
            _require(type(payload['actor_key']) is str and _ACTOR_KEY.fullmatch(payload['actor_key']) is not None)
            _require(payload['expected_absent'] is True)
            typed = RegisterSystemPayload(_uuid(payload['actor_id']), payload['kind'], payload['actor_key'], _display(payload['display_name']), True)
            return RegisterSystemCommand(**common, scope=scope, payload=typed)
        payload = _object(doc['payload'], {'account_id', 'actor_id', 'display_name', 'expected_absent'})
        _require(evidence is not None and payload['expected_absent'] is True)
        typed = EnsureAccountActorPayload(_uuid(payload['account_id']), _uuid(payload['actor_id']), _display(payload['display_name']), True)
        return EnsureAccountActorCommand(**common, scope=scope, payload=typed)
    _require(name in ('membership.join', 'membership.retire'))
    scope = _object(doc['scope'], {'kind', 'org_id'})
    _require(scope['kind'] == 'organization')
    scope = OrganizationScope(_uuid(scope['org_id']))
    if name == 'membership.join':
        payload = _object(doc['payload'], {'account_id', 'expected_previous_membership_id'}, {'is_owner'})
        previous = payload['expected_previous_membership_id']
        if previous is not None:
            previous = _decimal(previous)
        is_owner = payload.get('is_owner', False)
        _require(type(is_owner) is bool)
        typed = JoinMembershipPayload(_uuid(payload['account_id']), previous, is_owner)
        return JoinMembershipCommand(**common, scope=scope, payload=typed)
    payload = _object(doc['payload'], {'account_id', 'membership_id', 'expected_revision'})
    typed = RetireMembershipPayload(_uuid(payload['account_id']), _decimal(payload['membership_id']), _decimal(payload['expected_revision']))
    return RetireMembershipCommand(**common, scope=scope, payload=typed)
