"""Direct database authority and connection lifecycle contracts."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))


def test_direct_database_url_requires_role_and_tls():
    from database import validate_url
    good = 'postgresql://scribeswell_runtime:secret@db.fixture.supabase.co/postgres?sslmode=require'
    assert validate_url(good, 'scribeswell_runtime', production=True) == good
    for bad in [good.replace('scribeswell_runtime', 'postgres'), good.replace('?sslmode=require', ''), good + '&options=-c%20role=postgres']:
        with pytest.raises(ValueError, match='database configuration'):
            validate_url(bad, 'scribeswell_runtime', production=True)


def test_sql_parameterization_and_connection_release():
    from database import Database
    from contextlib import contextmanager
    calls = []
    class Connection:
        def execute(self, query, values):
            calls.append((query.as_string(), values))
            return self
        def fetchall(self):
            return []
    class Pool:
        @contextmanager
        def connection(self):
            calls.append('acquired')
            try:
                yield Connection()
            finally:
                calls.append('released')
    db = Database('postgresql://scribeswell_runtime:fixture@localhost/postgres', 'scribeswell_runtime')
    db.pool = Pool()
    attack = "Gen'; DELETE FROM scribeswell.word; --"
    assert db.read('book_read', filters={'osis_id': attack}) == []
    assert calls[0] == 'acquired' and calls[-1] == 'released'
    assert attack not in calls[1][0] and calls[1][1] == [attack]
    assert 'scribeswell."book"' in calls[1][0]


def test_runtime_pool_lifecycle_and_safe_failure(monkeypatch):
    import database
    from main import app
    from fastapi.testclient import TestClient
    events = []
    class Pool:
        def __init__(self, *args, **kwargs):
            assert kwargs['min_size'] == 0 and kwargs['max_size'] == 8
            assert kwargs['timeout'] == 5 and kwargs['max_waiting'] == 32
        def open(self): events.append('open')
        def close(self): events.append('close')
    monkeypatch.setattr(database, 'ConnectionPool', Pool)
    with TestClient(app, raise_server_exceptions=False) as client:
        assert client.get('/health').status_code == 200
        assert database.get_database() is not None
    assert events == ['open', 'close']
    with pytest.raises(database.DatabaseUnavailable): database.get_database()


def test_obsolete_runtime_authority_is_rejected():
    from config import Settings
    from pydantic import ValidationError
    with pytest.raises(ValidationError, match='obsolete runtime service-key authority') as caught:
        Settings(_env_file=None, supabase_secret_key='sensitive-service-key-marker')
    assert 'sensitive-service-key-marker' not in str(caught.value)


def test_unavailable_database_is_bounded_safe_http_failure(monkeypatch, caplog):
    from database import Database
    from services import bible_service
    from main import app
    from fastapi.testclient import TestClient
    import time
    db = Database('postgresql://scribeswell_runtime:sensitive-password-marker@127.0.0.1:1/postgres', 'scribeswell_runtime', timeout=0.1)
    db.open()
    monkeypatch.setattr(bible_service, 'get_database', lambda: db)
    try:
        started = time.monotonic()
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get('/api/bible/books')
        assert time.monotonic() - started < 2
        assert response.status_code == 503
        assert response.json() == {'error': 'Database temporarily unavailable', 'code': 'database_unavailable'}
        assert 'sensitive-password-marker' not in caplog.text + response.text
        assert 'SELECT' not in caplog.text + response.text
    finally:
        db.close()
