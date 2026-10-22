"""Read-only historical corpus comparison. This cannot establish publication readiness."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import psycopg
from psycopg.rows import dict_row

from corpus_evidence import (EvidenceError, build_source_candidate, serialize_candidate,
                             verse_token_digest)
from corpus_source import BOOK_METADATA
from database import validate_url

MAX_OUTPUT_BYTES = 64 * 1024 * 1024
MAX_COUNTS = dict(books=39, chapters=6000, verses=50000, tokens=1000000)
WORKFLOW_SECONDS = 60
BATCH_SIZE = 1000
LABELS = ('source_id', 'catalogue_version', 'versification_id', 'tokenization_version')


class AuditError(EvidenceError):
    def __init__(self, code):
        self.code = 'database_audit.' + code
        ValueError.__init__(self, self.code)


def _require(condition):
    if not condition:
        raise AuditError('corpus_mismatch')


def _positive(value):
    _require(type(value) is int and value > 0)
    return value


def _remaining(deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise AuditError('deadline_exceeded')
    return remaining


def _timeout(connection, deadline):
    milliseconds = max(1, int(min(15, _remaining(deadline)) * 1000))
    connection.execute("SELECT set_config('statement_timeout', %s, true)", (str(milliseconds),))
    _remaining(deadline)


def _text_projection(field):
    # Size check occurs in PostgreSQL; excessive text never crosses the connection.
    return f'CASE WHEN octet_length({field}) <= 2048 THEN {field} ELSE NULL END AS {field}'


def _rows(connection, table, fields, expected, deadline, order='id'):
    _timeout(connection, deadline)
    with connection.cursor(name='audit_' + table) as cursor:
        cursor.execute(f'SELECT {fields} FROM scribeswell.{table} ORDER BY {order} LIMIT %s',
                       (expected + 1,))
        seen = 0
        while True:
            _timeout(connection, deadline)
            batch = cursor.fetchmany(min(BATCH_SIZE, expected + 1 - seen))
            if not batch:
                break
            for row in batch:
                _remaining(deadline)
                seen += 1
                _require(seen <= expected)
                yield row
        _require(seen == expected)


def _compare(connection, source, deadline):
    counts = source['counts']
    metadata = {meta['id']: meta for meta in BOOK_METADATA}
    book_fields = ','.join(field if field in ('id', 'book_order') else _text_projection(field)
                           for field in BOOK_METADATA[0])
    seen_books = set()
    for row in _rows(connection, 'book', book_fields, counts['books'], deadline):
        identifier = _positive(row['id'])
        _require(identifier not in seen_books and row == metadata.get(identifier))
        seen_books.add(identifier)
    _require(seen_books == set(metadata))

    expected_verses = {(v['book'], v['chapter'], v['verse']): v for v in source['verses']}
    expected_chapters = {(v['book'], v['chapter']) for v in source['verses']}
    chapters = {}
    seen_chapters = set()
    for row in _rows(connection, 'chapter', 'id,book_id,chapter_num', counts['chapters'], deadline):
        identifier = _positive(row['id'])
        _require(row['book_id'] in metadata)
        _positive(row['chapter_num'])
        coordinate = (metadata[row['book_id']]['osis_id'], row['chapter_num'])
        _require(identifier not in chapters and coordinate in expected_chapters
                 and coordinate not in seen_chapters)
        chapters[identifier] = (row['book_id'], coordinate)
        seen_chapters.add(coordinate)
    _require(seen_chapters == expected_chapters)

    verses = {}
    observed = {}
    seen_verses = set()
    for row in _rows(connection, 'verse', 'id,chapter_id,book_id,chapter_num,verse_num', counts['verses'], deadline):
        identifier = _positive(row['id'])
        _require(row['chapter_id'] in chapters)
        book_id, chapter = chapters[row['chapter_id']]
        _require(row['book_id'] == book_id and row['chapter_num'] == chapter[1])
        _positive(row['verse_num'])
        coordinate = (*chapter, row['verse_num'])
        _require(identifier not in verses and coordinate in expected_verses
                 and coordinate not in seen_verses)
        verses[identifier] = coordinate
        seen_verses.add(coordinate)
    _require(seen_verses == set(expected_verses))

    labels = {key: source[key] for key in LABELS}
    seen_ids = set()
    current = None
    tokens, identifiers = [], []

    def finish():
        if current is None:
            return
        coordinate = verses[current]
        expected = expected_verses[coordinate]
        _require(len(tokens) == expected['token_count'])
        digest = verse_token_digest(**labels, book=coordinate[0], chapter=coordinate[1],
                                    verse=coordinate[2], tokens=tokens)
        _require(digest == expected['verse_token_digest'])
        observed[coordinate] = identifiers

    for row in _rows(connection, 'word', 'id,verse_id,position,' + _text_projection('surface_he'),
                     counts['tokens'], deadline, 'verse_id,position,id'):
        identifier = _positive(row['id'])
        _require(identifier not in seen_ids and row['verse_id'] in verses)
        seen_ids.add(identifier)
        if current != row['verse_id']:
            finish()
            current = row['verse_id']
            tokens, identifiers = [], []
        _require(type(row['position']) is int and row['position'] == len(tokens) + 1)
        _require(len(tokens) < expected_verses[verses[current]]['token_count'])
        tokens.append((row['position'], row['surface_he']))
        identifiers.append(str(identifier))
    finish()
    _require(set(observed) == set(expected_verses))
    _remaining(deadline)
    return observed


def _verify_visibility(connection, deadline):
    """Conservatively prove SELECT cannot hide rows under current effective roles.

    Controlled owner schema/policy DDL must remain stable during this observation.
    No policy expression is executed or accepted merely because it currently passes.
    """
    _timeout(connection, deadline)
    rows = connection.execute("""
        SELECT c.relname AS name, c.relkind = 'r' AS base_table,
               NOT pg_catalog.row_security_active(c.oid) OR (
                   EXISTS (
                       SELECT 1 FROM pg_catalog.pg_policy AS p
                       WHERE p.polrelid = c.oid AND p.polcmd IN ('r', '*')
                         AND p.polpermissive
                         AND pg_catalog.pg_get_expr(p.polqual, p.polrelid) = 'true'
                         AND EXISTS (
                             SELECT 1 FROM pg_catalog.unnest(p.polroles) AS roles(role_id)
                             WHERE CASE WHEN role_id = 0 THEN true ELSE
                                 pg_catalog.pg_has_role(current_user, role_id, 'USAGE') END))
                   AND NOT EXISTS (
                       SELECT 1 FROM pg_catalog.pg_policy AS p
                       WHERE p.polrelid = c.oid AND p.polcmd IN ('r', '*')
                         AND NOT p.polpermissive
                         AND EXISTS (
                             SELECT 1 FROM pg_catalog.unnest(p.polroles) AS roles(role_id)
                             WHERE CASE WHEN role_id = 0 THEN true ELSE
                                 pg_catalog.pg_has_role(current_user, role_id, 'USAGE') END))
               ) AS visible
        FROM pg_catalog.pg_class AS c
        JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname = 'scribeswell'
          AND c.relname IN ('book', 'chapter', 'verse', 'word')
        LIMIT 5
        """).fetchall()
    _remaining(deadline)
    if (len(rows) != 4 or {row['name'] for row in rows} != {'book', 'chapter', 'verse', 'word'}
            or any(not row['base_table'] or not row['visible'] for row in rows)):
        raise AuditError('visibility_unproven')


def _validated_url(database_url):
    try:
        if not isinstance(database_url, str):
            raise ValueError
        database_url.encode('utf-8')
        return validate_url(database_url, 'scribeswell_runtime')
    except (ValueError, TypeError):
        raise AuditError('configuration_invalid') from None


def _audit_snapshot(source, database_url, deadline):
    """The isolated worker owns exactly one connection and no filesystem output."""
    connection = None
    try:
        url = _validated_url(database_url)
        connection = psycopg.connect(url.replace('postgresql+psycopg://', 'postgresql://', 1),
                                     autocommit=True, row_factory=dict_row, connect_timeout=5,
                                     options='-c statement_timeout=15000 -c lock_timeout=3000 '
                                             '-c idle_in_transaction_session_timeout=15000')
        _remaining(deadline)
        connection.execute('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY')
        _timeout(connection, deadline)
        authority = connection.execute("""
            SELECT rolname AS role, rolsuper, rolbypassrls
            FROM pg_catalog.pg_roles WHERE rolname = current_user
            """).fetchone()
        if authority != {'role': 'scribeswell_runtime', 'rolsuper': False, 'rolbypassrls': False}:
            raise AuditError('authority_invalid')
        _verify_visibility(connection, deadline)
        observed = _compare(connection, source, deadline)
        _timeout(connection, deadline)
        connection.execute('ROLLBACK')
        _remaining(deadline)
    except AuditError:
        raise
    except EvidenceError:
        raise AuditError('corpus_mismatch') from None
    except (psycopg.Error, OSError, TimeoutError):
        raise AuditError('database_unavailable') from None
    finally:
        if connection is not None:
            # Closing also abandons any failed/open transaction without another SQL wait.
            connection.close()
    return [observed[(verse['book'], verse['chapter'], verse['verse'])]
            for verse in source['verses']]


def _worker_command():
    return [sys.executable, str(Path(__file__).resolve())]


def audit_database(raw, expected_source_sha256, *, database_url, source_id,
                   catalogue_version, versification_id, tokenization_version):
    """Qualify raw source first; supervise all database work with a hard deadline.

    A disposable child bounds even blocked DNS, connect and transport operations.
    Credentials travel only over private stdin. Only the parent publishes output.
    """
    source = build_source_candidate(raw, expected_source_sha256, source_id=source_id,
                                    catalogue_version=catalogue_version,
                                    versification_id=versification_id,
                                    tokenization_version=tokenization_version)
    if any(source['counts'][key] > maximum for key, maximum in MAX_COUNTS.items()):
        raise AuditError('source_counts_exceeded')
    source_hash = hashlib.sha256(serialize_candidate(source)).hexdigest()
    deadline = time.monotonic() + WORKFLOW_SECONDS
    database_url = _validated_url(database_url)
    request = json.dumps(dict(source=source, database_url=database_url,
                              deadline=deadline), ensure_ascii=False).encode('utf-8')
    process = None
    try:
        _remaining(deadline)
        worker_environment = {key: value for key, value in os.environ.items()
                              if not key.startswith('PG') and key != 'SCRIBESWELL_AUDIT_DATABASE_URL'}
        process = subprocess.Popen(_worker_command(), stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                   env=worker_environment)
        response, _ = process.communicate(request, timeout=_remaining(deadline))
        _remaining(deadline)
        if len(response) > MAX_OUTPUT_BYTES:
            raise AuditError('output_too_large')
        result = json.loads(response)
        if not isinstance(result, dict):
            raise AuditError('database_unavailable')
        if process.returncode != 0:
            code = result.get('error')
            if code not in ('configuration_invalid', 'authority_invalid', 'corpus_mismatch',
                            'database_unavailable', 'deadline_exceeded', 'output_too_large',
                            'visibility_unproven'):
                code = 'database_unavailable'
            raise AuditError(code)
        observed = result['observed']
        if not isinstance(observed, list):
            raise AuditError('database_unavailable')
        _require(len(observed) == len(source['verses']))
        for verse, identifiers in zip(source['verses'], observed):
            _remaining(deadline)
            _require(isinstance(identifiers, list) and len(identifiers) == verse['token_count'])
            _require(all(isinstance(value, str) and value.isascii() and value.isdecimal()
                         and not value.startswith('0') for value in identifiers))
        _remaining(deadline)
    except subprocess.TimeoutExpired:
        raise AuditError('deadline_exceeded') from None
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        if isinstance(exc, AuditError):
            raise
        raise AuditError('database_unavailable') from None
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.communicate()
    return dict(source, kind='scribeswell.database_audit_candidate',
                source_candidate_sha256=source_hash,
                verses=[dict(verse, observed_word_ids=identifiers)
                        for verse, identifiers in zip(source['verses'], observed)])


def _worker_main():
    # This private IPC entry point never accepts paths or claimed proof through CLI.
    try:
        request = json.loads(sys.stdin.buffer.read(MAX_OUTPUT_BYTES + 1))
        observed = _audit_snapshot(request['source'], request['database_url'], request['deadline'])
        response = serialize_candidate(dict(observed=observed))
        if len(response) > MAX_OUTPUT_BYTES:
            raise AuditError('output_too_large')
    except AuditError as exc:
        sys.stdout.buffer.write(serialize_candidate(dict(error=exc.code.removeprefix('database_audit.'))))
        return 1
    except Exception:
        sys.stdout.buffer.write(b'{"error":"database_unavailable"}\n')
        return 1
    sys.stdout.buffer.write(response)
    return 0


def serialize_audit_candidate(candidate):
    payload = serialize_candidate(candidate)
    if len(payload) > MAX_OUTPUT_BYTES:
        raise AuditError('output_too_large')
    return payload


if __name__ == '__main__':
    raise SystemExit(_worker_main())
