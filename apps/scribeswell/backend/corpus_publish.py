"""Controlled owner publication. Never expose this producer as a claimed-audit endpoint.

The caller owns connection custody and transport containment. Each restricted write
is a short transaction; only the closed auditor observes corpus text.
"""
from dataclasses import asdict, dataclass
import hashlib
import json
from uuid import UUID, uuid5

from psycopg.rows import tuple_row
from psycopg.types.json import Jsonb

from closed_corpus_audit import AUDITOR_CONTRACT_VERSION, ClosedAuditError, audit_closed_attempt
from corpus_evidence import EvidenceError
from corpus_publication import PublicationError, _idle
from corpus_publication_input import CommandValidationError, _uuid, prepare_command

AUDITOR_VERSION = AUDITOR_CONTRACT_VERSION
MAX_MANIFEST_BYTES = 64 * 1024 * 1024
BATCH_SIZE = 1000


class PublishError(RuntimeError):
    def __init__(self, code):
        self.code = 'corpus_publish.' + code
        super().__init__(self.code)


@dataclass(frozen=True, slots=True)
class PublicationReceipt:
    version: int
    operation_id: str
    command: str
    source_revision: str
    source_id: str
    attempt_id: str
    generation: str
    executor_actor_id: str
    status: str


def suboperation_id(operation_id, name):
    _uuid(operation_id)
    return str(uuid5(UUID(operation_id), 'scribeswell.publication.v1:' + name))


def manifest_rows(candidate):
    return [[v.book, v.chapter, v.verse, v.verse_token_digest, list(v.observed_word_ids)]
            for v in candidate.verses]


def encode_manifest(candidate):
    """The auditor-version-bound compact UTF-8 encoding, without source text."""
    value = ['scribeswell.manifest.v1', AUDITOR_VERSION, candidate.source_id,
             candidate.catalogue_version, candidate.versification_id, candidate.tokenization_version,
             candidate.source_sha256, candidate.source_revision, candidate.executor_actor_id,
             candidate.attempt_id, str(candidate.generation), manifest_rows(candidate)]
    encoded = json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf8')
    if len(encoded) > MAX_MANIFEST_BYTES:
        raise PublishError('input_invalid')
    return encoded


def _activation(command, operation_id):
    return dict(version=1, operation_id=operation_id, command='publication.activate',
                source_revision=suboperation_id(operation_id, 'revision'), seal=asdict(command))


def _receipt(value, request):
    expected = dict(version=1, operation_id=request['operation_id'], command=request['command'],
                    source_revision=request['source_revision'], source_id=request['seal']['scope']['source_id'],
                    attempt_id=request['seal']['payload']['expected_attempt_id'],
                    generation=request['seal']['payload']['expected_generation'])
    keys = set(expected) | {'executor_actor_id', 'status'}
    valid = type(value) is dict and set(value) == keys
    if valid:
        valid = all(type(value[k]) is type(v) and value[k] == v for k, v in expected.items())
        valid = valid and value['status'] == {'publication.stage':'staged', 'publication.batch':'batched',
                                            'publication.complete':'complete', 'publication.activate':'published'}[request['command']]
        try:
            _uuid(value['executor_actor_id'])
        except CommandValidationError:
            valid = False
    if not valid:
        raise PublishError('unknown_outcome')
    return PublicationReceipt(**value)


def _call(connection, request, *, lookup):
    failure, result = None, None
    original_factory = connection.row_factory
    try:
        _idle(connection)
        connection.row_factory = tuple_row
        with connection.transaction():
            connection.execute('SET TRANSACTION ISOLATION LEVEL READ COMMITTED READ WRITE')
            connection.execute("SET LOCAL statement_timeout='5s'")
            connection.execute("SET LOCAL lock_timeout='2s'")
            connection.execute("SET LOCAL idle_in_transaction_session_timeout='5s'")
            statement = ('SELECT scribeswell.lookup_corpus_publication_outcome(%s)' if lookup else
                         'SELECT scribeswell.execute_corpus_publication(%s)')
            row = connection.execute(statement, (Jsonb(request),)).fetchone()
            if row is None or len(row) != 1 or (row[0] is None and not lookup):
                raise PublishError('unknown_outcome')
            result = None if row[0] is None else _receipt(row[0], request)
    except PublishError as error:
        failure = error.code.rsplit('.', 1)[1]
    except Exception as error:
        failure = {'42501':'access_denied', '22023':'input_invalid', 'P0001':'conflict',
                   '55000':'unavailable', '55P03':'unavailable', '57014':'unavailable',
                   '25006':'unavailable', '25001':'unavailable'}.get(getattr(error, 'sqlstate', None), 'unknown_outcome')
    finally:
        connection.row_factory = original_factory
    if failure:
        raise PublishError(failure)
    return result


def _acknowledge(connection, request):
    # Lookup first also reconciles a previous process's lost commit acknowledgement.
    previous = _call(connection, request, lookup=True)
    if previous is not None:
        return previous
    try:
        return _call(connection, request, lookup=False)
    except PublishError as error:
        if not error.code.endswith('.unknown_outcome'):
            raise
    recovered = _call(connection, request, lookup=True)
    if recovered is None:
        raise PublishError('unknown_outcome')
    return recovered


def _prepare(command_raw, source_raw, operation_id):
    _uuid(operation_id)
    prepared = prepare_command(command_raw, source_raw)
    if prepared.command.command != 'corpus.seal':
        raise PublishError('input_invalid')
    return prepared.command


def lookup_publication(connection, command_raw, source_raw, *, operation_id):
    """Reconcile the original activation under current authority, without auditing."""
    failure, result = None, None
    try:
        _idle(connection)
        command = _prepare(command_raw, source_raw, operation_id)
        result = _call(connection, _activation(command, operation_id), lookup=True)
    except PublicationError as error:
        failure = error.code.rsplit('.', 1)[1]
    except (CommandValidationError, EvidenceError):
        failure = 'input_invalid'
    if failure:
        raise PublishError(failure)
    return result


def publish_closed_attempt(connection, command_raw, source_raw, *, operation_id):
    """Audit actual rows internally, stage immutable proof, complete, then activate.

    The operation UUID and original seal/source must be retained by the controlled
    caller for recovery. No external candidate or claimed audit is accepted.
    """
    failure, result = None, None
    try:
        _idle(connection)
        command = _prepare(command_raw, source_raw, operation_id)
        activation = _activation(command, operation_id)
        result = _call(connection, activation, lookup=True)
        if result is not None:
            return result
        candidate = audit_closed_attempt(connection, command_raw, source_raw,
                                         source_revision=activation['source_revision'])
        encoded = encode_manifest(candidate)
        rows = manifest_rows(candidate)
        header = dict(auditor_version=AUDITOR_VERSION, executor_actor_id=candidate.executor_actor_id,
                      catalogue_version=candidate.catalogue_version, versification_id=candidate.versification_id,
                      tokenization_version=candidate.tokenization_version, source_sha256=candidate.source_sha256,
                      digest=hashlib.sha256(encoded).hexdigest(), verse_count=len(rows),
                      token_count=sum(len(row[4]) for row in rows), encoded_bytes=len(encoded),
                      batch_count=(len(rows) + BATCH_SIZE - 1) // BATCH_SIZE,
                      inventory=[[r[0], r[1], r[2], r[3], len(r[4])] for r in rows])
        def request(kind, name, **payload):
            return dict(activation, command='publication.' + kind,
                        operation_id=suboperation_id(operation_id, name), **payload)
        _acknowledge(connection, request('stage', 'stage', header=header))
        for index, offset in enumerate(range(0, len(rows), BATCH_SIZE)):
            _acknowledge(connection, request('batch', 'batch:' + str(index),
                                            batch_index=index, first_ordinal=offset,
                                            rows=rows[offset:offset + BATCH_SIZE]))
        _acknowledge(connection, request('complete', 'complete', digest=header['digest'],
                                        auditor_version=AUDITOR_VERSION, verse_count=len(rows),
                                        token_count=header['token_count']))
        result = _acknowledge(connection, activation)
    except PublicationError as error:
        failure = error.code.rsplit('.', 1)[1]
    except (CommandValidationError, EvidenceError):
        failure = 'input_invalid'
    except ClosedAuditError as error:
        failure = error.code.rsplit('.', 1)[1]
    if failure:
        raise PublishError(failure)
    return result
