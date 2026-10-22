"""Bounded independent corpus observation; PostgreSQL fixtures own disposable data only."""
import hashlib
import json
import sys
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP / 'backend'))
sys.path.insert(0, str(APP / 'tools/py'))


def test_audit_cli_and_library_exist():
    import corpus_database_audit
    assert callable(corpus_database_audit.audit_database)
    assert (APP / 'tools/py/audit_corpus_database.py').is_file()

import os
import subprocess
import time
import psycopg
import corpus_database_audit as audit
from corpus_evidence import EvidenceError, build_source_candidate, serialize_candidate
from corpus_source import BOOK_METADATA, decode_word
from test_postgres_acceptance import postgres, role_url

LABELS = dict(source_id='oshb-test', catalogue_version='test-v1',
              versification_id='test-v1', tokenization_version='test-v1')


def synthetic():
    return json.dumps({meta['name_en']: [[[["אָב", "1", "HNcmsa"],
                                         ["בֵּן", "2", "HNcmsa"]]]]
                       for meta in BOOK_METADATA}, ensure_ascii=False).encode()


def invoke(raw, url):
    return audit.audit_database(raw, hashlib.sha256(raw).hexdigest(), database_url=url, **LABELS)


def invoke_local(raw, url):
    source = build_source_candidate(raw, hashlib.sha256(raw).hexdigest(), **LABELS)
    identifiers = audit._audit_snapshot(source, url, time.monotonic() + audit.WORKFLOW_SECONDS)
    return dict(source, verses=[dict(verse, observed_word_ids=ids)
                                for verse, ids in zip(source['verses'], identifiers)])


def seed(admin, raw):
    """Fixture-admin COPY avoids importer/morpheme overhead for the full artifact."""
    data = json.loads(raw)
    admin.execute("SET statement_timeout='15s'")
    admin.execute('TRUNCATE scribeswell.book CASCADE')
    with admin.transaction():
        with admin.cursor().copy('COPY scribeswell.book FROM STDIN') as copy:
            for meta in BOOK_METADATA:
                copy.write_row(tuple(meta.values()))
        chapters, verses, words = [], [], []
        for meta in BOOK_METADATA:
            for c, chapter in enumerate(data[meta['name_en']], 1):
                chapter_id = len(chapters) + 1
                chapters.append((chapter_id, meta['id'], c))
                for v, verse in enumerate(chapter, 1):
                    verse_id = len(verses) + 1
                    verses.append((verse_id, chapter_id, v, meta['id'], c))
                    for position, word in enumerate(verse, 1):
                        surface = decode_word(word, 'fixture')[0]['surface_he']
                        words.append((len(words) + 1, verse_id, position, surface))
        for table, fields, rows in [('chapter', 'id,book_id,chapter_num', chapters),
                                    ('verse', 'id,chapter_id,verse_num,book_id,chapter_num', verses),
                                    ('word', 'id,verse_id,position,surface_he', words)]:
            with admin.cursor().copy(f'COPY scribeswell.{table} ({fields}) FROM STDIN') as copy:
                for row in rows:
                    copy.write_row(row)


@pytest.fixture
def corpus(postgres):
    admin, url = postgres
    raw = synthetic()
    seed(admin, raw)
    return admin, role_url(url, 'scribeswell_runtime'), raw


def test_complete_synthetic_and_id_regeneration(corpus):
    admin, url, raw = corpus
    before = admin.execute('SELECT * FROM scribeswell.word ORDER BY id').fetchall()
    first = invoke(raw, url)
    assert first == invoke(raw, url)
    assert admin.execute('SELECT * FROM scribeswell.word ORDER BY id').fetchall() == before
    assert first['kind'] == 'scribeswell.database_audit_candidate'
    assert first['publication'] is False
    assert first['counts'] == dict(books=39, chapters=39, verses=39, tokens=78)
    source = build_source_candidate(raw, hashlib.sha256(raw).hexdigest(), **LABELS)
    assert first['source_candidate_sha256'] == hashlib.sha256(serialize_candidate(source)).hexdigest()
    assert set(first) == set(source) | {'source_candidate_sha256'}
    assert first['verses'][0]['observed_word_ids'] == ['1', '2']
    admin.execute('UPDATE scribeswell.word SET id=id+1000')
    changed = invoke(raw, url)
    assert changed['verses'][0]['observed_word_ids'] == ['1001', '1002']
    assert changed['verses'][0]['verse_token_digest'] == first['verses'][0]['verse_token_digest']


@pytest.mark.parametrize('change', [
    'DELETE FROM scribeswell.word WHERE id=1',
    'DELETE FROM scribeswell.word WHERE verse_id=1; DELETE FROM scribeswell.verse WHERE id=1',
    'DELETE FROM scribeswell.word WHERE verse_id=1; DELETE FROM scribeswell.verse WHERE id=1; DELETE FROM scribeswell.chapter WHERE id=1',
    "INSERT INTO scribeswell.book VALUES (40,'Extra','Extra','א','old','torah',40)",
    'INSERT INTO scribeswell.chapter VALUES (1000,1,2)',
    'INSERT INTO scribeswell.verse VALUES (1000,1,2,1,1)',
    "INSERT INTO scribeswell.word(id,verse_id,position,surface_he) VALUES (1000,1,3,'א')",
    "UPDATE scribeswell.word SET surface_he='אָח' WHERE id=1",
    "UPDATE scribeswell.word SET surface_he='' WHERE id=1",
    "UPDATE scribeswell.word SET surface_he=repeat('א',1025) WHERE id=1",
    "UPDATE scribeswell.book SET name_he=repeat('א',1025) WHERE id=1",
    "UPDATE scribeswell.book SET name_en='Wrong' WHERE id=1",
    'UPDATE scribeswell.word SET id=-1 WHERE id=1',
    'UPDATE scribeswell.word SET position=0 WHERE id=1',
    'UPDATE scribeswell.word SET position=3 WHERE id=2',
    'UPDATE scribeswell.verse SET book_id=2 WHERE id=1',
    'UPDATE scribeswell.verse SET chapter_num=2 WHERE id=1',
    'UPDATE scribeswell.chapter SET chapter_num=0 WHERE id=1',
    'UPDATE scribeswell.verse SET verse_num=0 WHERE id=1',
])
def test_inventory_surface_and_denormalization_fail(corpus, change):
    admin, url, raw = corpus
    admin.execute(change)
    with pytest.raises(audit.AuditError, match='database_audit.corpus_mismatch'):
        invoke(raw, url)


@pytest.mark.parametrize('change', [
    'UPDATE scribeswell.word SET verse_id=99999 WHERE id=1',
    'UPDATE scribeswell.verse SET chapter_id=99999 WHERE id=1',
    'UPDATE scribeswell.chapter SET book_id=99 WHERE id=1',
    'UPDATE scribeswell.chapter SET id=-1 WHERE id=1',
    'UPDATE scribeswell.verse SET id=-1 WHERE id=1',
])
def test_orphans_and_nonpositive_parents_not_hidden(corpus, change):
    admin, url, raw = corpus
    with admin.transaction():
        admin.execute("SET LOCAL session_replication_role='replica'")
        admin.execute(change)
    with pytest.raises(audit.AuditError):
        invoke(raw, url)


def test_snapshot_concurrent_write_and_read_only(corpus, monkeypatch):
    admin, url, raw = corpus
    original = audit._rows
    observations = []
    def rows(connection, table, *args, **kwargs):
        if table == 'book':
            observations.append(connection.execute('SHOW transaction_isolation').fetchone())
            observations.append(connection.execute('SHOW transaction_read_only').fetchone())
            # This write commits after the runtime's snapshot began; no audit lock blocks it.
            admin.execute("SET statement_timeout='1s'")
            admin.execute("UPDATE scribeswell.word SET surface_he='אָח' WHERE id=1")
        yield from original(connection, table, *args, **kwargs)
    monkeypatch.setattr(audit, '_rows', rows)
    assert invoke_local(raw, url)['publication'] is False
    assert observations == [{'transaction_isolation': 'repeatable read'}, {'transaction_read_only': 'on'}]
    monkeypatch.setattr(audit, '_rows', original)
    with pytest.raises(audit.AuditError):
        invoke_local(raw, url)
    # Runtime lacks DML privileges too; use a temporary-table write to prove READ ONLY itself.
    def prove_read_only(connection, *args):
        with pytest.raises(psycopg.errors.ReadOnlySqlTransaction):
            connection.execute('CREATE TABLE scribeswell.audit_forbidden(id int)')
        raise audit.AuditError('readonly_proven')
    monkeypatch.setattr(audit, '_compare', prove_read_only)
    with pytest.raises(audit.AuditError, match='readonly_proven'):
        invoke_local(raw, url)


def test_deadline_cancellation_and_connection_release(corpus, monkeypatch):
    admin, url, raw = corpus
    monkeypatch.setattr(audit, 'WORKFLOW_SECONDS', 0.15)
    def wait(connection, source, deadline):
        audit._timeout(connection, deadline)
        connection.execute('SELECT pg_sleep(2)')
    monkeypatch.setattr(audit, '_compare', wait)
    start = time.monotonic()
    with pytest.raises(audit.AuditError, match='database_unavailable'):
        invoke_local(raw, url)
    assert time.monotonic() - start < 1
    assert admin.execute("SELECT count(*) FROM pg_stat_activity WHERE usename='scribeswell_runtime' AND state='idle in transaction'").fetchone()[0] == 0


def test_expired_deadline_releases_connection(corpus, monkeypatch):
    admin, url, raw = corpus
    monkeypatch.setattr(audit, 'WORKFLOW_SECONDS', 0)
    with pytest.raises(audit.AuditError, match='deadline_exceeded'):
        invoke_local(raw, url)


def test_actual_login_and_runtime_configuration(corpus, postgres, monkeypatch):
    admin, url, raw = corpus
    for wrong in [None, '', postgres[1], role_url(postgres[1], 'scribeswell_import'),
                  url + '?sslmode=disable&options=unsafe']:
        with pytest.raises(audit.AuditError, match='configuration_invalid'):
            invoke_local(raw, wrong)
    original = audit.psycopg.connect
    def unexpected_login(*args, **kwargs):
        return original(postgres[1], **kwargs)
    monkeypatch.setattr(audit.psycopg, 'connect', unexpected_login)
    with pytest.raises(audit.AuditError, match='authority_invalid'):
        invoke_local(raw, url)


def test_source_qualified_and_counts_checked_before_connect(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('must not connect')
    monkeypatch.setattr(audit.psycopg, 'connect', forbidden)
    raw = synthetic()
    with pytest.raises(EvidenceError, match='checksum_mismatch'):
        audit.audit_database(raw, '0' * 64, database_url=None, **LABELS)
    monkeypatch.setitem(audit.MAX_COUNTS, 'tokens', 1)
    with pytest.raises(audit.AuditError, match='source_counts_exceeded'):
        invoke(raw, None)


def test_output_bound(monkeypatch):
    monkeypatch.setattr(audit, 'MAX_OUTPUT_BYTES', 1)
    with pytest.raises(audit.AuditError, match='output_too_large'):
        audit.serialize_audit_candidate({'value': 'safe'})


def test_cli_determinism_safe_failures_and_create_only(corpus, tmp_path):
    admin, url, raw = corpus
    source = tmp_path / 'source.json'
    source.write_bytes(raw)
    output = tmp_path / 'candidate.json'
    env = dict(os.environ, SCRIBESWELL_AUDIT_DATABASE_URL=url)
    command = [sys.executable, str(APP / 'tools/py/audit_corpus_database.py'),
               '--source', str(source), '--expected-source-sha256', hashlib.sha256(raw).hexdigest()]
    for key, value in LABELS.items():
        command.extend(['--' + key.replace('_', '-'), value])
    def run(destination=output, environment=env):
        return subprocess.run(command + ['--output', str(destination)], env=environment,
                              capture_output=True, timeout=10)
    assert run().returncode == 0
    payload = output.read_bytes()
    second = tmp_path / 'second.json'
    assert run(second).returncode == 0
    assert second.read_bytes() == payload
    assert source.read_bytes() == raw
    assert run().stderr == b'source_evidence.output_exists\n'
    assert output.read_bytes() == payload
    link = tmp_path / 'link.json'
    link.symlink_to(output)
    assert run(link).stderr == b'source_evidence.output_exists\n'
    bad = tmp_path / 'failed.json'
    admin.execute("UPDATE scribeswell.word SET surface_he='wrong' WHERE id=1")
    result = run(bad)
    assert result.returncode == 1 and result.stderr == b'database_audit.corpus_mismatch\n'
    assert not bad.exists()
    assert not list(tmp_path.glob('.source-evidence-*'))
    result = run(bad, dict(env, SCRIBESWELL_AUDIT_DATABASE_URL='sensitive-secret'))
    assert result.stderr == b'database_audit.configuration_invalid\n'


def test_full_checked_in_source_match(postgres):
    admin, url = postgres
    raw = (APP / 'scripts/hebrew.json').read_bytes()
    seed(admin, raw)
    result = invoke(raw, role_url(url, 'scribeswell_runtime'))
    assert result['counts'] == dict(books=39, chapters=929, verses=23213, tokens=306785)
    assert len(result['verses']) == 23213
    assert len(audit.serialize_audit_candidate(result)) < audit.MAX_OUTPUT_BYTES


def test_supervised_worker_timeout_kills_and_reaps(monkeypatch):
    processes = []
    original = audit.subprocess.Popen
    def launch(*args, **kwargs):
        process = original(*args, **kwargs)
        processes.append(process)
        return process
    monkeypatch.setattr(audit.subprocess, 'Popen', launch)
    monkeypatch.setattr(audit, '_worker_command', lambda: [sys.executable, '-c', 'import time; time.sleep(20)'])
    monkeypatch.setattr(audit, 'WORKFLOW_SECONDS', 0.15)
    start = time.monotonic()
    with pytest.raises(audit.AuditError, match='deadline_exceeded'):
        invoke(synthetic(), 'postgresql://scribeswell_runtime:secret-never-in-argv@localhost/test')
    assert time.monotonic() - start < 1
    assert len(processes) == 1 and processes[0].poll() is not None
    assert 'secret-never-in-argv' not in str(processes[0].args)


def test_bounded_fetch_and_projection(corpus, monkeypatch):
    admin, url, raw = corpus
    original = audit._rows
    seen = []
    def rows(connection, table, fields, expected, deadline, order='id'):
        if table in ('word', 'book'):
            assert 'octet_length(' in fields and '<= 2048' in fields
        seen.append((table, expected))
        yield from original(connection, table, fields, expected, deadline, order)
    monkeypatch.setattr(audit, '_rows', rows)
    monkeypatch.setattr(audit, 'BATCH_SIZE', 1)
    invoke_local(raw, url)
    assert seen == [('book', 39), ('chapter', 39), ('verse', 39), ('word', 78)]


def test_output_reuses_cleanup_reconciliation(corpus, tmp_path, monkeypatch):
    import audit_corpus_database as cli
    admin, url, raw = corpus
    source = tmp_path / 'source.json'
    source.write_bytes(raw)
    destination = tmp_path / 'candidate.json'
    args = ['audit', '--source', str(source), '--output', str(destination),
            '--expected-source-sha256', hashlib.sha256(raw).hexdigest()]
    for key, value in LABELS.items():
        args.extend(['--' + key.replace('_', '-'), value])
    monkeypatch.setattr(sys, 'argv', args)
    monkeypatch.setenv('SCRIBESWELL_AUDIT_DATABASE_URL', url)
    original = Path.unlink
    def fail_temporary(path, *args, **kwargs):
        if path.name.startswith('.source-evidence-'):
            raise OSError('private-error')
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'unlink', fail_temporary)
    assert cli.main() == 1
    assert destination.read_bytes() == audit.serialize_audit_candidate(invoke(raw, url))


def test_stream_has_expected_plus_one_and_bounded_batches(monkeypatch):
    class Cursor:
        def __init__(self, count):
            self.count = count
            self.requests = []
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def execute(self, query, values):
            assert 'LIMIT %s' in query and values == (1002,)
        def fetchmany(self, count):
            assert 1 <= count <= 1000
            self.requests.append(count)
            returned = min(count, self.count)
            self.count -= returned
            return [{}] * returned
    class Connection:
        def __init__(self, count):
            self.stream = Cursor(count)
        def cursor(self, **kwargs):
            assert kwargs == dict(name='audit_word')
            return self.stream
        def execute(self, *args):
            pass
    connection = Connection(1001)
    assert len(list(audit._rows(connection, 'word', 'id', 1001, time.monotonic() + 1))) == 1001
    assert connection.stream.requests == [1000, 2, 1]
    with pytest.raises(audit.AuditError, match='corpus_mismatch'):
        list(audit._rows(Connection(1002), 'word', 'id', 1001, time.monotonic() + 1))


def test_duplicate_word_ids_fail_even_without_database_constraint(corpus, monkeypatch):
    admin, url, raw = corpus
    original = audit._rows
    def rows(connection, table, *args, **kwargs):
        for row in original(connection, table, *args, **kwargs):
            if table == 'word':
                row['id'] = 1
            yield row
    monkeypatch.setattr(audit, '_rows', rows)
    with pytest.raises(audit.AuditError, match='corpus_mismatch'):
        invoke_local(raw, url)


def test_worker_failure_never_forwards_arbitrary_output(monkeypatch):
    monkeypatch.setattr(audit, '_worker_command', lambda: [sys.executable, '-c',
        'import sys; print("sensitive credentials"); print("private SQL", file=sys.stderr); sys.exit(1)'])
    with pytest.raises(audit.AuditError) as error:
        invoke(synthetic(), 'postgresql://scribeswell_runtime:private-url@localhost/test')
    assert str(error.value) == 'database_audit.database_unavailable'


def test_restrictive_policy_cannot_hide_extra_word(corpus):
    admin, url, raw = corpus
    admin.execute("INSERT INTO scribeswell.word(id,verse_id,position,surface_he) VALUES (99999,1,3,'א')")
    admin.execute('CREATE POLICY audit_hidden_word ON scribeswell.word AS RESTRICTIVE FOR SELECT TO PUBLIC USING (position <= 2)')
    try:
        with pytest.raises(audit.AuditError, match='visibility_unproven'):
            invoke(raw, url)
    finally:
        admin.execute('DROP POLICY audit_hidden_word ON scribeswell.word')
        admin.execute('DELETE FROM scribeswell.word WHERE id=99999')
    assert invoke(raw, url)['counts']['tokens'] == 78


def test_surrogate_url_fails_safely_before_worker_launch(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('invalid URL must fail before worker launch')
    monkeypatch.setattr(audit.subprocess, 'Popen', forbidden)
    with pytest.raises(audit.AuditError, match='configuration_invalid'):
        invoke(synthetic(), 'postgresql://scribeswell_runtime:private\udcff@localhost/test')


def test_worker_environment_excludes_audit_url(monkeypatch):
    monkeypatch.setenv('SCRIBESWELL_AUDIT_DATABASE_URL', 'environment-secret')
    original = audit.subprocess.Popen
    def launch(*args, **kwargs):
        assert 'SCRIBESWELL_AUDIT_DATABASE_URL' not in kwargs['env']
        return original(*args, **kwargs)
    monkeypatch.setattr(audit.subprocess, 'Popen', launch)
    monkeypatch.setattr(audit, '_worker_command', lambda: [sys.executable, '-c',
        'import json, os, sys; request=json.load(sys.stdin); '
        'assert "SCRIBESWELL_AUDIT_DATABASE_URL" not in os.environ; '
        'assert request["database_url"].endswith("/private"); '
        'print(json.dumps({"error":"authority_invalid"})); sys.exit(1)'])
    with pytest.raises(audit.AuditError, match='authority_invalid'):
        invoke(synthetic(), 'postgresql://scribeswell_runtime:stdin-secret@localhost/private')


@pytest.mark.parametrize('payload,exit_code', [
    ('[]', 1), ('null', 1), ('"private-value"', 1),
    ('[' * 2000 + '0' + ']' * 2000, 1),
    ('{"observed": null}', 0), ('{"observed": 1}', 0),
])
def test_malformed_worker_response_is_safe(monkeypatch, payload, exit_code):
    monkeypatch.setattr(audit, '_worker_command', lambda: [sys.executable, '-c',
        f'import sys; sys.stdout.write({payload!r}); sys.exit({exit_code})'])
    with pytest.raises(audit.AuditError, match='^database_audit.database_unavailable$'):
        invoke(synthetic(), 'postgresql://scribeswell_runtime:private@localhost/test')


@pytest.mark.parametrize('attribute,restore', [('SUPERUSER', 'NOSUPERUSER'), ('BYPASSRLS', 'NOBYPASSRLS')])
def test_runtime_elevated_authority_is_rejected(corpus, attribute, restore):
    admin, url, raw = corpus
    admin.execute(f'ALTER ROLE scribeswell_runtime {attribute}')
    try:
        with pytest.raises(audit.AuditError, match='authority_invalid'):
            invoke(raw, url)
    finally:
        admin.execute(f'ALTER ROLE scribeswell_runtime {restore}')
    assert invoke(raw, url)['counts']['tokens'] == 78


def test_hostile_libpq_environment_cannot_redirect_audit(corpus, monkeypatch):
    admin, url, raw = corpus
    monkeypatch.setenv('PGHOSTADDR', '192.0.2.1')
    monkeypatch.setenv('PGPORT', '1')
    monkeypatch.setenv('PGOPTIONS', '-c default_transaction_read_only=off')
    original = audit.subprocess.Popen
    def launch(*args, **kwargs):
        assert not any(key.startswith('PG') for key in kwargs['env'])
        return original(*args, **kwargs)
    monkeypatch.setattr(audit.subprocess, 'Popen', launch)
    assert invoke(raw, url)['counts']['tokens'] == 78


def test_permissive_filter_cannot_hide_extra_word(corpus):
    admin, url, raw = corpus
    # direct_read is the only applicable permissive SELECT policy for this login.
    admin.execute("INSERT INTO scribeswell.word(id,verse_id,position,surface_he) VALUES (99999,1,3,'א')")
    admin.execute('ALTER POLICY direct_read ON scribeswell.word USING (position <= 2)')
    try:
        with pytest.raises(audit.AuditError, match='visibility_unproven'):
            invoke(raw, url)
    finally:
        admin.execute('ALTER POLICY direct_read ON scribeswell.word USING (true)')
        admin.execute('DELETE FROM scribeswell.word WHERE id=99999')
    assert invoke(raw, url)['counts']['tokens'] == 78


def test_effective_inherited_role_restrictive_policy(corpus):
    admin, url, raw = corpus
    # All roles are owned by the guarded fixture; restore both membership and NOINHERIT.
    admin.execute('ALTER ROLE scribeswell_runtime INHERIT')
    admin.execute('GRANT authenticated TO scribeswell_runtime')
    admin.execute('CREATE POLICY audit_inherited_filter ON scribeswell.word AS RESTRICTIVE FOR SELECT TO authenticated USING (position <= 2)')
    try:
        with pytest.raises(audit.AuditError, match='visibility_unproven'):
            invoke(raw, url)
    finally:
        admin.execute('DROP POLICY audit_inherited_filter ON scribeswell.word')
        admin.execute('REVOKE authenticated FROM scribeswell_runtime')
        admin.execute('ALTER ROLE scribeswell_runtime NOINHERIT')
    assert invoke(raw, url)['counts']['tokens'] == 78


def test_irrelevant_role_restrictive_policy_does_not_block_audit(corpus):
    admin, url, raw = corpus
    admin.execute('CREATE POLICY audit_irrelevant_filter ON scribeswell.word AS RESTRICTIVE FOR SELECT TO authenticated USING (false)')
    try:
        assert invoke(raw, url)['counts']['tokens'] == 78
    finally:
        admin.execute('DROP POLICY audit_irrelevant_filter ON scribeswell.word')


def test_replacement_view_is_not_an_owning_table(corpus):
    admin, url, raw = corpus
    admin.execute('ALTER TABLE scribeswell.word RENAME TO audit_original_word')
    try:
        admin.execute('CREATE VIEW scribeswell.word AS SELECT * FROM scribeswell.audit_original_word')
        admin.execute('GRANT SELECT ON scribeswell.word TO scribeswell_runtime')
        with pytest.raises(audit.AuditError, match='visibility_unproven'):
            invoke(raw, url)
    finally:
        admin.execute('DROP VIEW IF EXISTS scribeswell.word')
        admin.execute('ALTER TABLE scribeswell.audit_original_word RENAME TO word')
    assert invoke(raw, url)['counts']['tokens'] == 78


def test_supervised_timeout_releases_real_readonly_session(corpus, monkeypatch):
    admin, url, raw = corpus
    # Readiness exposes only backend PID and fixed transaction flags, never DSN/text.
    worker = '''import json, sys, time
import psycopg
request = json.load(sys.stdin)
connection = psycopg.connect(request['database_url'], autocommit=True)
connection.execute('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY')
connection.execute('SELECT 1 FROM scribeswell.book LIMIT 1')
pid = connection.execute('SELECT pg_backend_pid()').fetchone()[0]
isolation = connection.execute('SHOW transaction_isolation').fetchone()[0]
readonly = connection.execute('SHOW transaction_read_only').fetchone()[0]
print(json.dumps(dict(pid=pid, isolation=isolation, readonly=readonly)), flush=True)
time.sleep(30)
'''
    monkeypatch.setattr(audit, '_worker_command', lambda: [sys.executable, '-c', worker])
    monkeypatch.setattr(audit, 'WORKFLOW_SECONDS', 2)
    processes, readiness = [], []
    original = audit.subprocess.Popen
    def launch(*args, **kwargs):
        process = original(*args, **kwargs)
        processes.append(process)
        communicate = process.communicate
        def capture(*values, **options):
            try:
                return communicate(*values, **options)
            except subprocess.TimeoutExpired as exc:
                readiness.append(json.loads(exc.output.splitlines()[0]))
                raise
        process.communicate = capture
        return process
    monkeypatch.setattr(audit.subprocess, 'Popen', launch)
    with pytest.raises(audit.AuditError, match='deadline_exceeded'):
        invoke(raw, url)
    assert processes[0].poll() is not None
    assert len(readiness) == 1
    assert readiness[0]['isolation'] == 'repeatable read' and readiness[0]['readonly'] == 'on'
    pid = readiness[0]['pid']
    assert type(pid) is int and pid > 0
    until = time.monotonic() + 3
    while admin.execute('SELECT EXISTS(SELECT 1 FROM pg_stat_activity WHERE pid=%s)', (pid,)).fetchone()[0]:
        assert time.monotonic() < until, 'Timed-out worker backend must disappear'
        time.sleep(0.02)
