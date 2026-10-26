"""Caller-owned closed-attempt audit; no durable attestation or activation.

This adapter is a trusted producer of actual observations, not an input endpoint for
claimed audit JSON. Its unpublished result still requires protected durable staging
and a fresh activation CAS. No credentials, caller grants or supervisors live here.
"""
import time

from psycopg.rows import dict_row, tuple_row

from corpus_database_audit import (
    AuditError, MAX_COUNTS, WORKFLOW_SECONDS, _compare, _remaining, _timeout, _verify_visibility,
)
from corpus_evidence import EvidenceError, build_source_candidate
from corpus_manifest import ManifestError, build_manifest_candidate
from corpus_publication import PublicationError, _idle, lookup_outcome
from corpus_publication_input import CommandValidationError, _uuid, parse_command


# Bump when changing the correspondence contract consumed by durable manifests.
AUDITOR_CONTRACT_VERSION = 'scribeswell.closed_audit.v1'


class ClosedAuditError(RuntimeError):
    """Fixed safe identifier; never retains submitted or driver content."""
    def __init__(self, code):
        self.code = 'closed_corpus_audit.' + code
        super().__init__(self.code)


CLOSED_OBSERVATION = """
SELECT c.enforcement,e.source_id,e.attempt_id::text,e.generation::text,e.input_sha256,
       e.state AS epoch_state,a.state AS attempt_state,
       a.catalogue_version,a.versification_id,a.tokenization_version,
       p.executor_actor_id::text,p.enabled AS principal_enabled,u.enabled AS authority_enabled
FROM scribeswell.corpus_fence_control c
JOIN scribeswell.corpus_epoch e ON e.singleton=c.singleton
JOIN scribeswell.corpus_attempt a ON a.attempt_id=e.attempt_id AND a.source_id=e.source_id
     AND a.generation=e.generation AND a.input_sha256=e.input_sha256
JOIN scribeswell.corpus_operator_principal p ON p.database_login=session_user
JOIN scribeswell.corpus_operator_authority u ON u.database_login=p.database_login
     AND u.source_id=e.source_id AND u.command='corpus.seal'
WHERE c.singleton
LIMIT 2
"""


def _observe_closed(connection, command, receipt):
    rows = connection.execute(CLOSED_OBSERVATION).fetchall()
    if len(rows) != 1 or type(rows[0]) is not dict:
        raise ClosedAuditError('unavailable')
    row = rows[0]
    if row.get('principal_enabled') is not True or row.get('authority_enabled') is not True:
        raise ClosedAuditError('access_denied')
    if row.get('enforcement') is not True:
        raise ClosedAuditError('unavailable')
    identity = command.payload.input
    expected = dict(enforcement=True, source_id=command.scope.source_id,
                    attempt_id=command.payload.expected_attempt_id,
                    generation=command.payload.expected_generation,
                    input_sha256=identity.source_sha256, epoch_state='closed', attempt_state='closed',
                    catalogue_version=identity.catalogue_version, versification_id=identity.versification_id,
                    tokenization_version=identity.tokenization_version,
                    executor_actor_id=receipt.executor_actor_id, principal_enabled=True, authority_enabled=True)
    if row != expected:
        raise ClosedAuditError('conflict')


def _audit(connection, command_raw, source_raw, source_revision):
    deadline = time.monotonic() + WORKFLOW_SECONDS
    _idle(connection)
    _uuid(source_revision)
    command = parse_command(command_raw)
    if command.command != 'corpus.seal':
        raise ClosedAuditError('input_invalid')
    identity = command.payload.input
    labels = dict(source_id=command.scope.source_id, catalogue_version=identity.catalogue_version,
                  versification_id=identity.versification_id, tokenization_version=identity.tokenization_version)
    source = build_source_candidate(source_raw, identity.source_sha256, **labels)
    if any(source['counts'][key] > maximum for key, maximum in MAX_COUNTS.items()):
        raise ClosedAuditError('input_invalid')
    _remaining(deadline)
    factory = connection.row_factory
    try:
        # Existing controller receipt decoding intentionally expects a tuple row.
        connection.row_factory = tuple_row
        receipt = lookup_outcome(connection, command_raw)
        if receipt is None:
            raise ClosedAuditError('unavailable')
        _remaining(deadline)
        connection.row_factory = dict_row
        with connection.transaction():
            connection.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
            connection.execute("SET LOCAL lock_timeout='2s'")
            connection.execute("SET LOCAL idle_in_transaction_session_timeout='15s'")
            _timeout(connection, deadline)
            _observe_closed(connection, command, receipt)
            _verify_visibility(connection, deadline)
            observed = _compare(connection, source, deadline)
            _remaining(deadline)
    finally:
        # The caller may reuse its tuple/custom factory after success or failure.
        connection.row_factory = factory
    _remaining(deadline)
    manifest = build_manifest_candidate(
        source_raw, identity.source_sha256, **labels, source_revision=source_revision,
        executor_actor_id=receipt.executor_actor_id, attempt_id=receipt.attempt_id,
        generation=int(receipt.generation), expected_attempt_id=command.payload.expected_attempt_id,
        expected_generation=int(command.payload.expected_generation), observed=observed)
    _remaining(deadline)
    return manifest


def audit_closed_attempt(connection, command_raw, source_raw, *, source_revision):
    """Observe an acknowledged, current closed attempt and its complete corpus.

    Missing explicit read grants fail closed. No locks coordinate the full scan;
    later activation must reject recovery that races this snapshot. The60s execution
    budget and server waits are finite, but transport containment belongs to caller.
    """
    failure, result = None, None
    try:
        result = _audit(connection, command_raw, source_raw, source_revision)
    except ClosedAuditError as error:
        failure = error.code.rsplit('.', 1)[1]
    except PublicationError as error:
        failure = 'access_denied' if error.code.endswith('.access_denied') else 'unavailable'
    except AuditError as error:
        failure = {'corpus_mismatch': 'corpus_mismatch', 'deadline_exceeded': 'deadline_exceeded'}.get(
            error.code.rsplit('.', 1)[1], 'unavailable')
    except (CommandValidationError, EvidenceError):
        failure = 'input_invalid'
    except ManifestError:
        failure = 'corpus_mismatch'
    except Exception as error:
        failure = 'access_denied' if getattr(error, 'sqlstate', None) == '42501' else 'unavailable'
    if failure:
        # Raise outside the handler; driver contexts and source bytes do not escape.
        raise ClosedAuditError(failure)
    return result
