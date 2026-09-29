"""Real PostgreSQL acceptance. Point ONLY at a fresh disposable local database."""
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
import pytest
import psycopg

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP / 'backend'))
sys.path.insert(0, str(APP / 'tools/py'))
from database import Database, DatabaseUnavailable
from import_bible import BibleImporter


def role_url(url, role):
    parsed = urlsplit(url)
    password = unquote(parsed.password or '')
    host = parsed.hostname
    if ':' in host:
        host = '[' + host + ']'
    netloc = quote(role, safe='') + ':' + quote(password, safe='') + '@' + host
    if parsed.port:
        netloc += ':' + str(parsed.port)
    return parsed._replace(netloc=netloc).geturl()


@pytest.fixture(scope='module')
def postgres():
    url = os.environ.get('SCRIBESWELL_TEST_DATABASE_URL')
    if not url:
        pytest.skip('Set SCRIBESWELL_TEST_DATABASE_URL to a disposable local PostgreSQL database')
    assert urlsplit(url).hostname in ('localhost', '127.0.0.1'), 'Local disposable database only'
    import uuid
    from psycopg import sql
    roles = ['anon', 'authenticated', 'service_role', 'scribeswell_runtime', 'scribeswell_import']
    created_roles = []
    name = 'scribeswell_test_' + uuid.uuid4().hex
    with psycopg.connect(url, autocommit=True) as control:
        # Read-only guard before CREATE DATABASE or any cluster-wide mutation.
        assert not control.execute('SELECT rolname FROM pg_roles WHERE rolname = ANY(%s)', (roles,)).fetchall(), 'Fixture roles must be absent; use a fresh disposable cluster'
        control.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(name)))
        try:
            db_url = urlsplit(url)._replace(path='/' + name).geturl()
            with psycopg.connect(db_url, autocommit=True) as admin:
                for role in roles[:3]:
                    admin.execute(sql.SQL('CREATE ROLE {}').format(sql.Identifier(role)))
                    created_roles.append(role)
                admin.execute('ALTER ROLE service_role BYPASSRLS')
                admin.execute((APP / 'supabase/migrations/20260614000000_scribeswell_create_schema.sql').read_text())
                admin.execute("""INSERT INTO scribeswell.book VALUES (1,'Gen','Genesis','א','old','torah',1);
                    INSERT INTO scribeswell.chapter VALUES (101,1,1);
                    INSERT INTO scribeswell.verse VALUES (201,101,1,1,1);
                    INSERT INTO scribeswell.word VALUES (301,201,1,'אָב','אָב','1','HNcmsa');
                    INSERT INTO scribeswell.morpheme(id,word_id,segment_index,language,part_of_speech,pos_code) VALUES (401,301,0,'hebrew','noun','Ncmsa')""")
                def legacy_rows():
                    with admin.transaction():
                        admin.execute('SET LOCAL ROLE service_role')
                        return {table: admin.execute(sql.SQL('SELECT * FROM scribeswell.{} ORDER BY id').format(sql.Identifier(table + '_read'))).fetchall() for table in ['book','chapter','verse','word','morpheme']}
                before = legacy_rows()
                bootstrap = (APP / 'deployment/bootstrap/001_direct_database_roles.sql').read_text()
                admin.execute(bootstrap)
                created_roles.extend(roles[3:])
                assert legacy_rows() == before
                admin.execute(bootstrap)
                assert legacy_rows() == before
                for role in roles[3:]:
                    admin.execute(sql.SQL('ALTER ROLE {} PASSWORD {}').format(sql.Identifier(role), sql.Literal(unquote(urlsplit(url).password or ''))))
                admin.execute('CREATE SCHEMA identity; CREATE TABLE identity.person(id int); INSERT INTO identity.person VALUES (1); CREATE SCHEMA pts; CREATE TABLE pts.note(id int); CREATE SCHEMA content; CREATE TABLE content.file(id int)')
                yield admin, db_url
        finally:
            control.execute(sql.SQL('DROP DATABASE {}').format(sql.Identifier(name)))
            for role in reversed(created_roles):
                control.execute(sql.SQL('DROP ROLE {}').format(sql.Identifier(role)))


@pytest.fixture
def databases(postgres):
    admin, url = postgres
    admin.execute('TRUNCATE scribeswell.book CASCADE')
    runtime = Database(role_url(url, 'scribeswell_runtime'), 'scribeswell_runtime')
    importer = BibleImporter(role_url(url, 'scribeswell_import'))
    runtime.open()
    try:
        importer.seed_books()
        yield admin, runtime, importer
    finally:
        runtime.close()
        importer.close()


def test_reader_import_audit_long_chapter_replay_and_unexposed_data_api(databases, monkeypatch):
    admin, runtime, importer = databases
    from services import bible_service, lexicon_service
    monkeypatch.setattr(bible_service, 'get_database', lambda: runtime)
    monkeypatch.setattr(lexicon_service, 'lemma_variants', lambda: {'1': ['1', 'c/1'] + [f'x{i}/1' for i in range(1000)]})
    # There is no Data API service in this fixture; no REST schema is available.
    source = [[[['אָב', '1' if i % 2 else 'c/1', 'HNcmsa'] for i in range(1201)]]]
    importer.import_book('Genesis', source)
    before = runtime.read('word')
    importer.import_book('Genesis', source)
    importer.import_book('Genesis', source, verify_only=True)
    assert runtime.read('word') == before
    verses = bible_service.get_verses('Gen', 1)
    assert verses.total == 1 and len(verses.data[0].words) == 1201
    assert [w.position for w in verses.data[0].words] == list(range(1, 1202))
    assert bible_service.get_book('Gen').chapters[0].chapter_num == 1
    assert bible_service.get_chapter('Gen', 1).verses[0].verse_num == 1
    word = bible_service.get_word_morphology(before[0]['id'])
    assert word.surface_he == 'אָב' and word.morphemes[0].part_of_speech == 'noun'
    result = bible_service.get_occurrences('1', book='Gen', offset=1199, limit=25)
    assert result['total'] == 1201 and result['verse_total'] == 1
    assert [w['position'] for w in result['data']] == [1200, 1201]
    assert bible_service.get_occurrences('1', book='Exod')['total'] == 0
    # Old runtime compatibility remains; stored views and service role retain authority.
    with admin.transaction():
        admin.execute('SET LOCAL ROLE service_role')
        assert admin.execute('SELECT count(*) FROM scribeswell.word_read').fetchone()[0] == 1201
        admin.execute('UPDATE scribeswell.word SET display_he=display_he')
    from fastapi.testclient import TestClient
    from main import app
    with TestClient(app) as client:
        assert client.get('/api/bible/books/Gen/chapters/1/verses').status_code == 200
        assert client.get('/api/bible/books/Missing').status_code == 404
        missing = client.get('/api/bible/words/999999/morphology')
        assert missing.status_code == 404
        assert missing.json() == {'error': "Word '999999' not found"}


def test_actual_roles_deny_other_owners_and_runtime_writes(databases):
    admin, runtime, importer = databases
    for db in [runtime, importer.db]:
        with db.pool.connection() as conn:
            for command in ['SELECT * FROM identity.person', 'INSERT INTO identity.person VALUES (2)', 'SELECT * FROM pts.note', 'SELECT * FROM content.file', 'SET ROLE service_role']:
                with pytest.raises(psycopg.errors.InsufficientPrivilege): conn.execute(command)
            assert conn.execute('SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user').fetchone() == {'rolsuper': False, 'rolbypassrls': False}
    with runtime.pool.connection() as conn:
        assert conn.execute("SELECT row_security_active('scribeswell.book') AS active").fetchone()['active']
        for command in ['UPDATE scribeswell.book SET name_en=name_en', 'DELETE FROM scribeswell.book', "INSERT INTO scribeswell.chapter(book_id,chapter_num) VALUES (1,1)"]:
            with pytest.raises(psycopg.errors.InsufficientPrivilege): conn.execute(command)
    with importer.db.pool.connection() as conn:
        with pytest.raises(psycopg.errors.InsufficientPrivilege): conn.execute('DELETE FROM scribeswell.book')
        assert conn.execute("SELECT row_security_active('scribeswell.book') AS active").fetchone()['active']


def test_interrupted_chapter_rolls_back_then_replays_and_extra_rows_fail(databases, monkeypatch):
    admin, runtime, importer = databases
    source = [[[['אָב', '1', 'HNcmsa']]]]
    original = importer._upsert
    def fail_morphs(table, rows, on_conflict):
        if table == 'morpheme': raise RuntimeError('injected interruption')
        original(table, rows, on_conflict)
    monkeypatch.setattr(importer, '_upsert', fail_morphs)
    with pytest.raises(RuntimeError, match='interruption'): importer.import_book('Genesis', source)
    assert runtime.read('word') == [] and runtime.read('verse') == []
    monkeypatch.setattr(importer, '_upsert', original)
    importer.import_book('Genesis', source)
    before = runtime.read('word')
    importer.import_book('Genesis', source)
    assert runtime.read('word') == before
    admin.execute("INSERT INTO scribeswell.word(verse_id,position,surface_he) VALUES (%s,2,'א')", (before[0]['verse_id'],))
    with pytest.raises(RuntimeError, match='unexpected 1'): importer.import_book('Genesis', source, verify_only=True)


def test_statement_pool_timeout_safe_release_and_reuse(databases, caplog):
    admin, runtime, importer = databases
    for db in (runtime, importer.db):
        with db.pool.connection() as conn:
            assert conn.execute('SHOW statement_timeout').fetchone()['statement_timeout'] == '15s'
            assert conn.execute('SHOW lock_timeout').fetchone()['lock_timeout'] == '3s'
            assert conn.execute('SHOW idle_in_transaction_session_timeout').fetchone()['idle_in_transaction_session_timeout'] == '15s'
    started = time.monotonic()
    with pytest.raises(DatabaseUnavailable):
        with runtime.connection() as conn:
            conn.execute("SET statement_timeout='30ms'")
            conn.execute("SELECT pg_sleep(1), 'sensitive-sql-content'")
    assert time.monotonic() - started < 2
    assert len(runtime.read('book')) == 39
    tiny = Database(runtime.pool.conninfo, 'scribeswell_runtime', max_size=1, timeout=0.1)
    tiny.open()
    try:
        with tiny.pool.connection():
            started = time.monotonic()
            with pytest.raises(DatabaseUnavailable): tiny.read('book')
            assert time.monotonic() - started < 1
        assert len(tiny.read('book')) == 39
    finally:
        tiny.close()
    assert 'sensitive-sql-content' not in caplog.text and 'fixture@' not in caplog.text


def test_bootstrap_rejects_existing_cross_owner_authority(databases):
    admin, runtime, importer = databases
    bootstrap = (APP / 'deployment/bootstrap/001_direct_database_roles.sql').read_text()
    admin.execute('GRANT SELECT ON identity.person TO scribeswell_runtime')
    try:
        with pytest.raises(psycopg.errors.RaiseException, match='Unexpected existing'):
            admin.execute(bootstrap)
    finally:
        admin.execute('ROLLBACK')
        admin.execute('REVOKE SELECT ON identity.person FROM scribeswell_runtime')
    admin.execute(bootstrap)


def test_multi_chapter_failure_preserves_committed_chapter_and_retry_ids(databases, monkeypatch):
    admin, runtime, importer = databases
    chapter = [[['אָב', '1', 'HNcmsa']]]
    source = [chapter, chapter, chapter]
    original = importer._upsert
    completed = {}
    def fail_second(table, rows, on_conflict):
        if table == 'chapter' and rows[0]['chapter_num'] == 2:
            completed.update({t: runtime.read(t) for t in ('chapter','verse','word','morpheme')})
        if table == 'morpheme' and completed:
            raise RuntimeError('second chapter interrupted')
        original(table, rows, on_conflict)
    monkeypatch.setattr(importer, '_upsert', fail_second)
    with pytest.raises(RuntimeError, match='second chapter interrupted'):
        importer.import_book('Genesis', source)
    assert [r['chapter_num'] for r in runtime.read('chapter')] == [1]
    assert {t: runtime.read(t) for t in completed} == completed
    monkeypatch.setattr(importer, '_upsert', original)
    importer.import_book('Genesis', source)
    for table, rows in completed.items():
        assert all(row in runtime.read(table) for row in rows)
    final = {t: runtime.read(t) for t in completed}
    importer.import_book('Genesis', source)
    importer.import_book('Genesis', source, verify_only=True)
    assert {t: runtime.read(t) for t in completed} == final


@pytest.mark.parametrize('grant,revoke', [
    ('ALTER ROLE scribeswell_runtime REPLICATION', 'ALTER ROLE scribeswell_runtime NOREPLICATION'),
    ('ALTER ROLE scribeswell_runtime NOLOGIN', 'ALTER ROLE scribeswell_runtime LOGIN'),
    ('GRANT SELECT(id) ON identity.person TO scribeswell_runtime', 'REVOKE SELECT(id) ON identity.person FROM scribeswell_runtime'),
    ('GRANT UPDATE(name_en) ON scribeswell.book TO scribeswell_runtime', 'REVOKE UPDATE(name_en) ON scribeswell.book FROM scribeswell_runtime'),
    ('GRANT USAGE ON SEQUENCE scribeswell.word_id_seq TO scribeswell_runtime', 'REVOKE USAGE ON SEQUENCE scribeswell.word_id_seq FROM scribeswell_runtime'),
    ('GRANT UPDATE ON SEQUENCE scribeswell.word_id_seq TO scribeswell_import', 'REVOKE UPDATE ON SEQUENCE scribeswell.word_id_seq FROM scribeswell_import'),
    ('GRANT CREATE ON SCHEMA identity TO scribeswell_import', 'REVOKE CREATE ON SCHEMA identity FROM scribeswell_import'),
    ('CREATE FUNCTION identity.owned() RETURNS int LANGUAGE sql AS $$SELECT 1$$; ALTER FUNCTION identity.owned() OWNER TO scribeswell_runtime', 'DROP FUNCTION identity.owned()'),
    ('CREATE FUNCTION identity.privileged() RETURNS int LANGUAGE sql SECURITY DEFINER AS $$SELECT 1$$; REVOKE ALL ON FUNCTION identity.privileged() FROM PUBLIC; GRANT EXECUTE ON FUNCTION identity.privileged() TO scribeswell_import', 'DROP FUNCTION identity.privileged()'),
])
def test_bootstrap_rejects_hidden_authority(databases, grant, revoke):
    admin, runtime, importer = databases
    bootstrap = (APP / 'deployment/bootstrap/001_direct_database_roles.sql').read_text()
    admin.execute(grant)
    try:
        with pytest.raises(psycopg.errors.RaiseException):
            admin.execute(bootstrap)
    finally:
        admin.execute('ROLLBACK')
        admin.execute(revoke)
    admin.execute(bootstrap)


def test_role_url_preserves_escaped_credentials_and_database():
    assert role_url('postgresql://admin:p%40ss%3Aword@127.0.0.1:55439/test?sslmode=disable', 'scribeswell_runtime') == 'postgresql://scribeswell_runtime:p%40ss%3Aword@127.0.0.1:55439/test?sslmode=disable'


def test_bootstrap_public_table_grants_require_schema_access(databases):
    admin, runtime, importer = databases
    bootstrap = (APP / 'deployment/bootstrap/001_direct_database_roles.sql').read_text()
    admin.execute('CREATE SCHEMA isolated_stats; CREATE TABLE isolated_stats.sample(id int); GRANT SELECT ON isolated_stats.sample TO PUBLIC')
    try:
        # Supabase extensions expose statistics through PUBLIC table ACLs, but the
        # dedicated roles have no schema USAGE and therefore cannot reach them.
        admin.execute(bootstrap)
        admin.execute('GRANT USAGE ON SCHEMA isolated_stats TO PUBLIC')
        with pytest.raises(psycopg.errors.RaiseException, match='Unexpected existing'):
            admin.execute(bootstrap)
    finally:
        admin.execute('ROLLBACK')
        admin.execute('DROP SCHEMA isolated_stats CASCADE')
