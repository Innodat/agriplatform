"""Strict Access registry inputs only; parsed values convey no authority."""
from dataclasses import dataclass, field
import re
from typing import Literal

from identity_operator_input import (
    CommandValidationError as _IdentityValidationError,
    PlatformScope, _Envelope, _EVIDENCE, _REASONS,
    _decode, _decimal, _object, _require, _uuid,
)


class CommandValidationError(ValueError):
    """Fixed safe refusal, without submitted values or decoder exceptions."""

    code = 'access_operator_input_invalid'

    def __init__(self) -> None:
        super().__init__(self.code)


@dataclass(frozen=True, repr=False)
class RegisterApplicationPayload:
    app_id: str
    expected_absent: Literal[True]


@dataclass(frozen=True, repr=False)
class RegisterPermissionPayload:
    app_id: str
    permission: str
    scope_kind: Literal['account', 'organization']
    expected_absent: Literal[True]


@dataclass(frozen=True, repr=False)
class RegisterEntryPermissionPayload:
    app_id: str
    permission: str
    expected_absent: Literal[True]


@dataclass(frozen=True, repr=False)
class SetApplicationEnabledPayload:
    app_id: str
    enabled: bool
    expected_revision: str


@dataclass(frozen=True, repr=False)
class RegisterApplicationCommand(_Envelope):
    scope: PlatformScope
    payload: RegisterApplicationPayload
    command: Literal['application.register'] = field(default='application.register', init=False)


@dataclass(frozen=True, repr=False)
class RegisterPermissionCommand(_Envelope):
    scope: PlatformScope
    payload: RegisterPermissionPayload
    command: Literal['permission.register'] = field(default='permission.register', init=False)


@dataclass(frozen=True, repr=False)
class RegisterEntryPermissionCommand(_Envelope):
    scope: PlatformScope
    payload: RegisterEntryPermissionPayload
    command: Literal['entry_permission.register'] = field(default='entry_permission.register', init=False)


@dataclass(frozen=True, repr=False)
class SetApplicationEnabledCommand(_Envelope):
    scope: PlatformScope
    payload: SetApplicationEnabledPayload
    command: Literal['application.set_enabled'] = field(default='application.set_enabled', init=False)


Command = RegisterApplicationCommand | RegisterPermissionCommand | RegisterEntryPermissionCommand | SetApplicationEnabledCommand
_APP_ID = re.compile(r'[a-z][a-z0-9_]{1,63}')


def _parse(body: bytes) -> Command:
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
    _require(type(name) is str and name in ('application.register', 'permission.register', 'entry_permission.register', 'application.set_enabled'))
    scope = _object(doc['scope'], {'kind'})
    _require(scope['kind'] == 'platform')
    scope = PlatformScope()
    if name == 'application.set_enabled':
        payload = _object(doc['payload'], {'app_id', 'enabled', 'expected_revision'})
        app_id = payload['app_id']
        _require(type(app_id) is str and _APP_ID.fullmatch(app_id) is not None)
        _require(type(payload['enabled']) is bool)
        revision = _decimal(payload['expected_revision'])
        typed = SetApplicationEnabledPayload(app_id, payload['enabled'], revision)
        return SetApplicationEnabledCommand(**common, scope=scope, payload=typed)
    required = {'app_id', 'expected_absent'}
    if name != 'application.register':
        required.add('permission')
    if name == 'permission.register':
        required.add('scope_kind')
    payload = _object(doc['payload'], required)
    app_id = payload['app_id']
    _require(type(app_id) is str and _APP_ID.fullmatch(app_id) is not None)
    _require(payload['expected_absent'] is True)
    if name == 'application.register':
        return RegisterApplicationCommand(**common, scope=scope, payload=RegisterApplicationPayload(app_id, True))
    permission = payload['permission']
    _require(type(permission) is str and permission.isascii() and 1 <= len(permission) <= 200)
    if name == 'permission.register':
        kind = payload['scope_kind']
        _require(type(kind) is str and kind in ('account', 'organization'))
        typed = RegisterPermissionPayload(app_id, permission, kind, True)
        return RegisterPermissionCommand(**common, scope=scope, payload=typed)
    typed = RegisterEntryPermissionPayload(app_id, permission, True)
    return RegisterEntryPermissionCommand(**common, scope=scope, payload=typed)


def parse_command(body: bytes) -> Command:
    """Parse a closed version1 registry command without I/O or authority checks."""
    try:
        return _parse(body)
    except _IdentityValidationError:
        pass
    # Outside the handler: retain neither submitted-input errors nor their context.
    raise CommandValidationError()
