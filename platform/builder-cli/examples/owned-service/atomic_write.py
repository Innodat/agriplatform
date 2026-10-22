"""Copyable account-command WRITE primitives; domain orchestration stays with owner.

Requires SQLAlchemy and the copied sibling command_fingerprint.py. Inputs are verified
backend assertions, never request fields. No HTTP, SQL domain model or secret loader.
See tests/atomic_write_sample.py for an explicit owner-local transaction sequence.
"""
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
import math
import re
import time
from uuid import UUID

import rfc8785
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from command_fingerprint import FingerprintError, verify_fingerprint


class WriteError(Exception):
    """Safe identifier only; framework adapters must not expose exception locals."""


def _uuid(value):
    try:
        if type(value) is str and UUID(value).int and str(UUID(value)) == value:
            return value
    except (ValueError, AttributeError):
        pass
    raise WriteError('invalid_write_context') from None


@dataclass(frozen=True, repr=False)
class VerifiedContext:
    org_id: str
    account_id: str
    actor_id: str
    mode: str
    observed_at: float

    def __post_init__(self):
        for value in (self.org_id, self.account_id, self.actor_id):
            _uuid(value)
        if (self.mode not in ('own_read', 'own_write', 'all_read', 'all_write')
                or type(self.observed_at) not in (int, float)
                or not math.isfinite(self.observed_at)):
            raise WriteError('invalid_write_context')

    def __repr__(self):
        return '<VerifiedContext redacted>'


@dataclass(frozen=True)
class OutcomeKey:
    owner_schema: str
    org_id: str
    account_id: str
    command_type: str
    operation_id: str

    def __post_init__(self):
        for value in (self.org_id, self.account_id, self.operation_id):
            _uuid(value)
        if (type(self.owner_schema) is not str
                or re.fullmatch('[a-z][a-z0-9_]{0,62}', self.owner_schema) is None
                or type(self.command_type) is not str
                or re.fullmatch('[a-z][a-z0-9_.]{0,199}', self.command_type) is None):
            raise WriteError('invalid_write_context')


def outcome_lock_key(key):
    """Stable v1 JCS SHA256→signed big-endian64, account organization variant."""
    if type(key) is not OutcomeKey:
        raise WriteError('invalid_write_context')
    canonical = rfc8785.dumps(dict(lock_version=1, owner_schema=key.owner_schema,
        scope_kind='organization', scope_id=key.org_id, caller_kind='account',
        caller_id=key.account_id, command_type=key.command_type,
        operation_id=key.operation_id))
    return int.from_bytes(sha256(canonical).digest()[:8], 'big', signed=True)


class Budget:
    """One monotonic ten-second budget, created before external authorization.

    The owner caps its external authorization timeout at min(3, remaining()). A
    restart retains this object; a new request starts a new budget and authorization.
    """
    def __init__(self):
        self.started_at = time.monotonic()
        self.deadline = self.started_at + 10

    def remaining(self):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise WriteError('execution_timeout')
        return remaining

    def milliseconds(self, cap):
        value = int(min(cap, self.remaining()) * 1000)
        if value < 1:
            raise WriteError('execution_timeout')
        return value

    def local_start(self, context):
        self.remaining()
        now = time.monotonic()
        if not self.started_at <= context.observed_at <= now or now - context.observed_at > 1:
            raise WriteError('authorization_observation_expired')


def _limits(conn, budget):
    conn.execute(text("SELECT set_config('statement_timeout', :statement, true), "
                      "set_config('lock_timeout', :lock, true)"),
                 dict(statement=str(budget.milliseconds(5)), lock=str(budget.milliseconds(2))))


def execute(conn, budget, statement, parameters=None):
    """Execute owner SQL with waits capped by the remaining execution budget.

    Only the dedicated outcome_lock function classifies its lock timeout as busy.
    Domain/statement failures retain the generic safe failure path here. Owners may
    map specific named domain constraints at their boundary after full rollback.
    """
    try:
        _limits(conn, budget)
        result = conn.execute(text(statement), parameters or {})
        budget.remaining()
        return result
    except SQLAlchemyError:
        raise WriteError('internal_error') from None


def outcome_lock(conn, budget, key, context):
    if (key.org_id, key.account_id) != (context.org_id, context.account_id):
        raise WriteError('invalid_write_context')
    try:
        _limits(conn, budget)
        conn.execute(text('SELECT pg_advisory_xact_lock(:key)'), {'key': outcome_lock_key(key)})
        budget.remaining()
    except SQLAlchemyError as error:
        code = getattr(getattr(error, 'orig', None), 'sqlstate', None)
        raise WriteError('operation_busy' if code == '55P03' else 'internal_error') from None


@contextmanager
def transaction(conn, budget, context):
    """Own a fresh transaction, clear context on commit/rollback; never nest.

    The owner performs all network checks before entering. It binds the exact stored
    target to that authority before receipt disclosure; a different target requires
    rollback and a fresh external check outside locks within the original budget.
    All owner SQL uses execute(). Acknowledgements leave only after this scope exits.
    """
    if type(context) is not VerifiedContext or conn.in_transaction():
        raise WriteError('invalid_write_context')
    try:
        if (conn.get_execution_options().get('isolation_level') == 'AUTOCOMMIT'
                or conn.connection.driver_connection.autocommit
                or conn.get_isolation_level() != 'READ COMMITTED'):
            raise WriteError('invalid_write_context')
        budget.local_start(context)
        with conn.begin():
            _limits(conn, budget)
            # PostgreSQL17+ transaction deadline also bounds commit and idle owner
            # code, independently of individual statements. Owners require this DB.
            conn.execute(text("SELECT set_config('transaction_timeout', :total, true), "
                "set_config('app.org_id', :org, true), set_config('app.account_id', :account, true), "
                "set_config('app.actor_id', :actor, true), set_config('app.mode', :mode, true)"),
                dict(total=str(budget.milliseconds(10)), org=context.org_id,
                     account=context.account_id, actor=context.actor_id, mode=context.mode))
            yield conn
            _limits(conn, budget)
            budget.remaining()
        # A commit may succeed while its acknowledgement arrives after deadline.
        # Refuse a timely-success claim; the original operation remains uncertain.
        budget.remaining()
    except SQLAlchemyError:
        raise WriteError('internal_error') from None


def verify_existing(document, fingerprint, *, keys, command_version, result_version):
    """Owner has already checked exact stored target/current authority.

    Owner must validate its compact result DTO separately, including the supported
    command type. Unknown metadata is preserved and fails closed, never re-executed.
    """
    if type(command_version) is not int or command_version != 1 or type(result_version) is not int or result_version != 1:
        raise WriteError('operation_verification_unavailable')
    try:
        match = verify_fingerprint(document, fingerprint, keys=keys)
    except FingerprintError:
        raise WriteError('operation_verification_unavailable') from None
    if not match:
        raise WriteError('operation_payload_mismatch')
