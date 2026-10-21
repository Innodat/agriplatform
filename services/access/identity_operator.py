"""Bounded Identity owner adapter. The caller supplies an idle trusted connection."""
from dataclasses import asdict, dataclass, field
from datetime import datetime
from hashlib import sha256
import time
from typing import Literal
from uuid import UUID

import rfc8785
from sqlalchemy import text

from identity_operator_input import Command, RegisterSystemCommand, RetireMembershipCommand, JoinMembershipCommand, parse_command, CommandValidationError


class OperatorError(RuntimeError):
    def __init__(self, code, operation_id=None):
        self.code = code
        self.operation_id = operation_id
        super().__init__(code)


@dataclass(frozen=True)
class ActorTarget:
    actor_id: str


@dataclass(frozen=True)
class RegisterResult:
    command: Literal['actor.register_system']
    target: ActorTarget
    disposition: Literal['created', 'unchanged']
    revision: None
    event_id: str | None


@dataclass(frozen=True)
class MembershipTarget:
    org_id: str
    account_id: str
    membership_id: str


@dataclass(frozen=True)
class RetireMembershipResult:
    command: Literal['membership.retire']
    target: MembershipTarget
    disposition: Literal['changed']
    revision: str
    event_id: str


@dataclass(frozen=True)
class JoinMembershipResult:
    command: Literal['membership.join']
    target: MembershipTarget
    disposition: Literal['created']
    revision: str
    event_id: str


@dataclass(frozen=True)
class Receipt:
    operation_id: str
    result: RegisterResult | RetireMembershipResult | JoinMembershipResult
    command_version: int
    result_version: int
    committed_at: datetime
    status: Literal['committed'] = field(default='committed', init=False)


def canonical_command(command: Command):
    """Complete parser-produced envelope; UUID wire aliases have one fingerprint.

    Pure identity preparation, not validation or execution authority.
    """
    value = asdict(command)
    value['operation_id'] = str(UUID(value['operation_id']))
    for name in ('actor_id', 'account_id'):
        if name in value['payload']:
            value['payload'][name] = str(UUID(value['payload'][name]))
    if value['scope']['kind'] == 'organization':
        value['scope']['org_id'] = str(UUID(value['scope']['org_id']))
    return rfc8785.dumps(value)


def _outcome_lock_key(executor_actor_id, operation_id, command_type, scope_kind, scope_id):
    canonical = rfc8785.dumps(dict(lock_version=1, owner_schema='identity',
        scope_kind=scope_kind, scope_id=scope_id, caller_kind='actor',
        caller_id=str(UUID(executor_actor_id)), command_type=command_type,
        operation_id=str(UUID(operation_id))))
    return int.from_bytes(sha256(canonical).digest()[:8], 'big', signed=True)


def outcome_lock_key(executor_actor_id, operation_id):
    """Compatible actor.register_system/platform key used by the delivered SQL."""
    return _outcome_lock_key(executor_actor_id, operation_id,
                             'actor.register_system', 'platform', None)


def command_outcome_lock_key(executor_actor_id, command: Command):
    """Retry namespace for a parser-produced command; conveys no authority.

    Payload belongs in the fingerprint, not the lock key: conflicting retries must
    serialize together. Future SQL commands must independently prove this tuple.
    """
    scope = command.scope
    scope_id = str(UUID(scope.org_id)) if scope.kind == 'organization' else None
    return _outcome_lock_key(executor_actor_id, command.operation_id,
                             command.command, scope.kind, scope_id)


def _remaining(deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise OperatorError('operation_unavailable')
    return max(1, int(remaining * 1000))


def _receipt(row, operation_id, command='actor.register_system'):
    if command in ('membership.retire', 'membership.join'):
        return _membership_receipt(row, operation_id, command)
    if row is None:
        return None  # unresolved, never a proof of failure
    result, command_version, result_version, committed_at = row
    valid = (type(command_version) is int and command_version == 1
        and type(result_version) is int and result_version == 1 and type(result) is dict
        and set(result) == {'target', 'disposition', 'revision', 'event_id'}
        and type(result['target']) is dict and set(result['target']) == {'actor_id'}
        and result['disposition'] in ('created', 'unchanged') and result['revision'] is None
        and ((result['disposition'] == 'created') == (result['event_id'] is not None))
        and isinstance(committed_at, datetime) and committed_at.tzinfo is not None)
    if not valid:
        raise OperatorError('operation_verification_unavailable', operation_id)
    try:
        target = str(UUID(result['target']['actor_id']))
        event = str(UUID(result['event_id'])) if result['event_id'] is not None else None
        valid = UUID(target).int != 0 and (event is None or UUID(event).int != 0)
    except (ValueError, TypeError, AttributeError):
        valid = False
    if not valid:
        raise OperatorError('operation_verification_unavailable', operation_id)
    return Receipt(operation_id, RegisterResult('actor.register_system', ActorTarget(target),
                   result['disposition'], None, event), 1, 1, committed_at)


def _membership_receipt(row, operation_id, command='membership.retire'):
    if row is None:
        return None
    valid = False
    try:
        result, cv, rv, instant = row
        valid = (type(cv) is int and cv == 1 and type(rv) is int and rv == 1
            and type(result) is dict and set(result) == {'target','disposition','revision','event_id'}
            and type(result['target']) is dict and set(result['target']) == {'org_id','account_id','membership_id'}
            and result['disposition'] == ('created' if command == 'membership.join' else 'changed') and isinstance(instant, datetime) and instant.tzinfo is not None)
        if valid:
            target = result['target']
            for name in ('org_id','account_id'):
                valid = valid and type(target[name]) is str and UUID(target[name]).int != 0 and str(UUID(target[name])) == target[name]
            for value in (target['membership_id'], result['revision']):
                valid = valid and type(value) is str and value.isascii() and value.isdecimal() and 1 <= len(value) <= 19 and value[0] != '0' and int(value) <= 9223372036854775807
            event = result['event_id']
            valid = valid and type(event) is str and UUID(event).int != 0 and str(UUID(event)) == event
    except (ValueError, TypeError, AttributeError, KeyError):
        valid = False
    if not valid:
        raise OperatorError('operation_verification_unavailable', operation_id)
    if command == 'membership.join' and result['revision'] != '1':
        raise OperatorError('operation_verification_unavailable', operation_id)
    model = JoinMembershipResult if command == 'membership.join' else RetireMembershipResult
    return Receipt(operation_id, model(command, MembershipTarget(**target),
        result['disposition'], result['revision'], event), 1, 1, instant)


def _run(connection, operation_id, statement, parameters, deadline, command='actor.register_system'):
    # Check before any SQL and leave caller-owned work untouched.
    if connection.in_transaction():
        raise OperatorError('connection_busy', operation_id)
    failure = None
    receipt = None
    try:
        driver = getattr(getattr(connection, 'connection', None), 'driver_connection', None)
        if (getattr(connection, 'get_execution_options', lambda: {})().get('isolation_level') == 'AUTOCOMMIT'
            or getattr(driver, 'autocommit', False)
            or connection.get_isolation_level().upper() != 'READ COMMITTED'):
            raise OperatorError('isolation_unsupported', operation_id)
        with connection.begin():
            for name, ceiling in [('statement_timeout', 5000), ('lock_timeout', 2000)]:
                connection.execute(text('SELECT pg_catalog.set_config(:name,:value,true)'),
                    {'name': name, 'value': str(min(ceiling, _remaining(deadline)))+'ms'})
            remaining = _remaining(deadline)
            connection.execute(text("SELECT pg_catalog.set_config('statement_timeout',:statement,true),"
                "pg_catalog.set_config('lock_timeout',:lock,true)"),
                {'statement':str(min(5000,remaining))+'ms','lock':str(min(2000,remaining))+'ms'})
            _remaining(deadline)
            row = connection.execute(text(statement), parameters).one_or_none()
            receipt = _receipt(row, operation_id, command)
            _remaining(deadline)
        # Only this point acknowledges a successfully returned commit.
    except OperatorError as error:
        failure = error.code
    except Exception as error:
        original = getattr(error, 'orig', None)
        state = getattr(original, 'sqlstate', None)
        failure = {'IC001': 'operation_busy', 'IC002': 'access_denied',
            'IC003': 'operation_conflict', 'IC004': 'operation_verification_unavailable',
            'IC005': 'command_invalid'}.get(state, 'operation_unavailable')
    if failure is not None:
        # Raised outside the handler: driver objects/SQL/values are not chained.
        raise OperatorError(failure, operation_id)
    return receipt


def execute(connection, body: bytes):
    deadline = time.monotonic() + 10
    command = parse_command(body)
    operation_id = str(UUID(command.operation_id))
    if isinstance(command, JoinMembershipCommand):
        return _run(connection, operation_id,
            'SELECT * FROM identity.join_membership(CAST(:operation AS uuid),CAST(:org AS uuid),'
            'CAST(:account AS uuid),CAST(:previous AS bigint),:owner,:reason,:evidence,:canonical)',
            dict(operation=operation_id, org=str(UUID(command.scope.org_id)),
                 account=str(UUID(command.payload.account_id)), previous=command.payload.expected_previous_membership_id,
                 owner=command.payload.is_owner, reason=command.reason_code,
                 evidence=command.evidence_ref, canonical=canonical_command(command)), deadline, 'membership.join')
    if isinstance(command, RetireMembershipCommand):
        return _run(connection, operation_id,
            'SELECT * FROM identity.retire_membership(CAST(:operation AS uuid),CAST(:org AS uuid),'
            'CAST(:account AS uuid),CAST(:member AS bigint),CAST(:revision AS bigint),:reason,:evidence,:canonical)',
            dict(operation=operation_id, org=str(UUID(command.scope.org_id)),
                 account=str(UUID(command.payload.account_id)), member=command.payload.membership_id,
                 revision=command.payload.expected_revision, reason=command.reason_code,
                 evidence=command.evidence_ref, canonical=canonical_command(command)), deadline, 'membership.retire')
    if not isinstance(command, RegisterSystemCommand):
        raise OperatorError('command_unsupported', operation_id)
    canonical = canonical_command(command)
    return _run(connection, operation_id,
        'SELECT * FROM identity.register_system(CAST(:operation AS uuid),CAST(:actor AS uuid),'
        ':kind,:key,:display,:reason,:evidence,:canonical)',
        dict(operation=operation_id, actor=str(UUID(command.payload.actor_id)),
             kind=command.payload.kind, key=command.payload.actor_key,
             display=command.payload.display_name, reason=command.reason_code,
             evidence=command.evidence_ref, canonical=canonical), deadline)


def outcome(connection, operation_id, *, command='actor.register_system', org_id=None, account_id=None):
    deadline = time.monotonic() + 10
    invalid = False
    try:
        invalid = type(operation_id) is not str or UUID(operation_id).int == 0 or str(UUID(operation_id)) != operation_id.lower()
        if not invalid:
            operation_id = str(UUID(operation_id))
    except (ValueError, TypeError, AttributeError):
        invalid = True
    if command in ('membership.retire', 'membership.join'):
        try:
            for value in (org_id, account_id):
                if type(value) is not str or str(UUID(value)) != value.lower() or not UUID(value).int:
                    invalid = True
            org_id, account_id = str(UUID(org_id)), str(UUID(account_id))
        except (ValueError, TypeError, AttributeError):
            invalid = True
    elif command != 'actor.register_system' or org_id is not None or account_id is not None:
        invalid = True
    if invalid:
        raise OperatorError('command_invalid')
    if command in ('membership.retire', 'membership.join'):
        return _run(connection, operation_id,
            ('SELECT * FROM identity.' + ('membership_join_outcome' if command == 'membership.join' else 'membership_retirement_outcome') + '(CAST(:operation AS uuid),CAST(:org AS uuid),CAST(:account AS uuid))'),
            dict(operation=operation_id, org=org_id, account=account_id), deadline, command)
    return _run(connection, operation_id,
        'SELECT * FROM identity.system_actor_outcome(CAST(:operation AS uuid))',
        {'operation': operation_id}, deadline)
