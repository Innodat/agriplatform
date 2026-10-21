"""Bounded Access registration adapter; idle trusted READ COMMITTED connection only."""
from dataclasses import asdict, dataclass, field
from datetime import datetime
from hashlib import sha256
import re
import time
from typing import Literal
from uuid import UUID
import rfc8785
from sqlalchemy import text
from identity_operator import OperatorError
from access_operator_input import parse_command, RegisterApplicationCommand

@dataclass(frozen=True)
class ApplicationTarget:
    app_id: str

@dataclass(frozen=True)
class RegisterApplicationResult:
    command: Literal['application.register']
    target: ApplicationTarget
    disposition: Literal['created', 'unchanged']
    revision: str
    event_id: str | None

@dataclass(frozen=True)
class Receipt:
    operation_id: str
    result: RegisterApplicationResult
    command_version: int
    result_version: int
    committed_at: datetime
    status: Literal['committed'] = field(default='committed', init=False)


def canonical_command(command):
    value = asdict(command)
    value['operation_id'] = str(UUID(value['operation_id']))
    return rfc8785.dumps(value)


def command_outcome_lock_key(executor_actor_id, command):
    canonical = rfc8785.dumps(dict(lock_version=1, owner_schema='access',
        scope_kind='platform', scope_id=None, caller_kind='actor',
        caller_id=str(UUID(executor_actor_id)), command_type='application.register',
        operation_id=str(UUID(command.operation_id))))
    return int.from_bytes(sha256(canonical).digest()[:8], 'big', signed=True)


def _receipt(row, operation_id, command='application.register'):
    if row is None:
        return None
    valid = False
    try:
        result, cv, rv, instant = row
        valid = (command == 'application.register' and type(cv) is int and cv == 1
            and type(rv) is int and rv == 1 and type(result) is dict
            and set(result) == {'target','disposition','revision','event_id'}
            and type(result['target']) is dict and set(result['target']) == {'app_id'}
            and type(result['target']['app_id']) is str
            and re.fullmatch(r'[a-z][a-z0-9_]{1,63}',result['target']['app_id']) is not None
            and result['disposition'] in ('created','unchanged')
            and isinstance(instant,datetime) and instant.tzinfo is not None)
        revision = result['revision']
        valid = valid and type(revision) is str and re.fullmatch(r'[1-9][0-9]{0,18}',revision) is not None and int(revision) <= 9223372036854775807
        event = result['event_id']
        valid = valid and ((result['disposition'] == 'created' and revision == '1'
            and type(event) is str and UUID(event).int != 0 and str(UUID(event)) == event)
            or (result['disposition'] == 'unchanged' and event is None))
    except (ValueError,TypeError,AttributeError,KeyError):
        valid = False
    if not valid:
        raise OperatorError('operation_verification_unavailable',operation_id)
    return Receipt(operation_id,RegisterApplicationResult(command,ApplicationTarget(**result['target']),
        result['disposition'],revision,event),1,1,instant)

def _remaining(deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise OperatorError('operation_unavailable')
    return max(1, int(remaining * 1000))


def _run(connection, operation_id, statement, parameters, deadline, command='application.register'):
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
            # Rearm the server's next statement budget for COMMIT, including deferred
            # evidence checks. The client clock cannot cancel a blocked network COMMIT.
            connection.execute(text("SELECT pg_catalog.set_config('statement_timeout',:statement,true)"),
                {'statement':str(min(5000,_remaining(deadline)))+'ms'})
            _remaining(deadline)
        # A late returned COMMIT is durable but not acknowledged here; resolve its
        # receipt under current authority, as for other uncertain completion.
        _remaining(deadline)
    except OperatorError as error:
        failure = error.code
    except Exception as error:
        original = getattr(error, 'orig', None)
        state = getattr(original, 'sqlstate', None)
        failure = {'AC001': 'operation_busy', 'AC002': 'access_denied',
            'AC003': 'operation_conflict', 'AC004': 'operation_verification_unavailable',
            'AC005': 'command_invalid'}.get(state, 'operation_unavailable')
    if failure is not None:
        # Raised outside the handler: driver objects/SQL/values are not chained.
        raise OperatorError(failure, operation_id)
    return receipt


def execute(connection, body: bytes):
    deadline = time.monotonic() + 10
    command = parse_command(body)
    operation_id = str(UUID(command.operation_id))
    if not isinstance(command,RegisterApplicationCommand):
        raise OperatorError('command_unsupported',operation_id)
    return _run(connection,operation_id,
        'SELECT * FROM access.register_application(CAST(:operation AS uuid),:app,:reason,:evidence,:canonical)',
        dict(operation=operation_id,app=command.payload.app_id,reason=command.reason_code,
            evidence=command.evidence_ref,canonical=canonical_command(command)),deadline,'application.register')


def outcome(connection, operation_id, *, command='application.register', app_id=None):
    invalid = False
    try:
        invalid = (command != 'application.register' or type(operation_id) is not str
            or UUID(operation_id).int == 0 or str(UUID(operation_id)) != operation_id.lower()
            or type(app_id) is not str or re.fullmatch(r'[a-z][a-z0-9_]{1,63}',app_id) is None)
    except (ValueError,TypeError,AttributeError):
        invalid = True
    if invalid:
        raise OperatorError('command_invalid')
    operation_id = str(UUID(operation_id))
    return _run(connection,operation_id,
        'SELECT * FROM access.application_registration_outcome(CAST(:operation AS uuid),:app)',
        dict(operation=operation_id,app=app_id),time.monotonic()+10,'application.register')
