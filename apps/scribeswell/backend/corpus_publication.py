"""Bounded caller-owned connection adapter for the dormant corpus controller.

No credentials, transport, provisioning, CLI or runtime integration lives here.
"""
from dataclasses import asdict, dataclass
from typing import Literal

import psycopg
from psycopg.pq import TransactionStatus
from psycopg.types.json import Jsonb

from corpus_publication_input import (
    Command, _generation, _uuid, parse_command, prepare_command,
)


class PublicationError(RuntimeError):
    """Fixed safe identifier, without driver details or submitted values."""
    def __init__(self, code: str):
        self.code = 'corpus_publication.' + code
        super().__init__(self.code)


@dataclass(frozen=True, slots=True)
class CommandReceipt:
    version: Literal[1]
    operation_id: str
    command: str
    source_id: str
    executor_actor_id: str
    attempt_id: str
    generation: str
    state: Literal['updating', 'closed']


def _idle(connection) -> None:
    if (not isinstance(connection, psycopg.Connection) or connection.closed
            or connection.info.transaction_status != TransactionStatus.IDLE
            or connection.isolation_level not in (None, psycopg.IsolationLevel.READ_COMMITTED)
            or connection.read_only is True):
        raise PublicationError('unavailable')


def _receipt(value, command: Command) -> CommandReceipt:
    valid = False
    try:
        valid = (type(value) is dict and set(value) == {
            'version', 'operation_id', 'command', 'source_id', 'executor_actor_id',
            'attempt_id', 'generation', 'state'} and type(value['version']) is int
            and value['version'] == 1 and value['operation_id'] == command.operation_id
            and value['command'] == command.command and value['source_id'] == command.scope.source_id
            and value['state'] == ('closed' if command.command == 'corpus.seal' else 'updating'))
        if valid:
            _uuid(value['executor_actor_id'])
            _uuid(value['attempt_id'])
            _generation(value['generation'])
            if command.command == 'corpus.begin':
                valid = value['generation'] == '1'
            elif command.command == 'corpus.recover':
                valid = (int(value['generation']) == int(command.payload.expected_generation) + 1
                         and value['attempt_id'] != command.payload.expected_attempt_id)
            else:
                valid = (value['generation'] == command.payload.expected_generation
                         and value['attempt_id'] == command.payload.expected_attempt_id)
    except (ValueError, TypeError, KeyError):
        valid = False
    if not valid:
        raise PublicationError('unknown_outcome')
    return CommandReceipt(**value)


def _call(connection, command: Command, *, lookup: bool):
    failure = None
    result = None
    try:
        with connection.transaction():
            connection.execute('SET TRANSACTION ISOLATION LEVEL READ COMMITTED READ WRITE')
            connection.execute("SET LOCAL statement_timeout='5s'")
            connection.execute("SET LOCAL lock_timeout='2s'")
            connection.execute("SET LOCAL idle_in_transaction_session_timeout='5s'")
            # Fixed statements only. The semantic request is always a bound JSONB value.
            query = ('SELECT scribeswell.lookup_corpus_command_outcome(%s)' if lookup else
                     'SELECT scribeswell.execute_corpus_command(%s)')
            row = connection.execute(query, (Jsonb(asdict(command)),)).fetchone()
            if row is None or len(row) != 1 or (row[0] is None and not lookup):
                raise PublicationError('unknown_outcome')
            result = None if row[0] is None else _receipt(row[0], command)
        # Only successful transaction exit makes a returned value a durable receipt.
    except PublicationError as error:
        failure = error.code.rsplit('.', 1)[1]
    except Exception as error:
        failure = {'42501': 'access_denied', '22023': 'input_invalid',
                   'P0001': 'conflict', '55000': 'unavailable',
                   '55P03': 'unavailable', '57014': 'unavailable',
                   '25006': 'unavailable', '25001': 'unavailable'}.get(
                       getattr(error, 'sqlstate', None), 'unknown_outcome')
    if failure:
        # Raise outside the handler so neither driver context nor parameters escape.
        raise PublicationError(failure)
    return result


def execute_command(connection, raw: bytes, source_raw: bytes) -> CommandReceipt:
    """Requalify full source before SQL; return only after successful commit."""
    _idle(connection)
    prepared = prepare_command(raw, source_raw)
    return _call(connection, prepared.command, lookup=False)


def lookup_outcome(connection, raw: bytes) -> CommandReceipt | None:
    """Reconcile one semantic operation under current exact authority."""
    _idle(connection)
    return _call(connection, parse_command(raw), lookup=True)
