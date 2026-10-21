"""Bounded Identity owner adapter. The caller supplies an idle trusted connection."""
from dataclasses import asdict, dataclass, field
from datetime import datetime
from hashlib import sha256
import time
from typing import Literal
from uuid import UUID

import rfc8785
from sqlalchemy import text

from identity_operator_input import Command, RegisterSystemCommand, parse_command, CommandValidationError


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
class Receipt:
    operation_id: str
    result: RegisterResult
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


def _receipt(row, operation_id):
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


def _run(connection, operation_id, statement, parameters, deadline):
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
            receipt = _receipt(row, operation_id)
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


def outcome(connection, operation_id):
    deadline = time.monotonic() + 10
    invalid = False
    try:
        invalid = type(operation_id) is not str or UUID(operation_id).int == 0 or str(UUID(operation_id)) != operation_id.lower()
        if not invalid:
            operation_id = str(UUID(operation_id))
    except (ValueError, TypeError, AttributeError):
        invalid = True
    if invalid:
        raise OperatorError('command_invalid')
    return _run(connection, operation_id,
        'SELECT * FROM identity.system_actor_outcome(CAST(:operation AS uuid))',
        {'operation': operation_id}, deadline)
