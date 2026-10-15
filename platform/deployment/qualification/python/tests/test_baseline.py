"""ENV compatibility proof only; no app/owner server, database or real identity."""
from datetime import datetime, timedelta, timezone
from importlib.metadata import version
import io
import platform
import socket
import sys
import sysconfig
import threading
import time
from uuid import UUID

import httpx
import jwt
import psycopg
from psycopg import pq, sql
import pydantic
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import pytest
import rfc8785
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi import FastAPI
import uvicorn


def test_selected_runtime_and_exact_direct_packages():
    assert sys.version_info[:3] == (3, 15, 0)
    assert platform.python_implementation() == 'CPython'
    assert platform.system() == 'Linux' and platform.machine() == 'x86_64'
    assert platform.libc_ver()[0] == 'glibc'
    assert not sysconfig.get_config_var('Py_GIL_DISABLED')
    assert sys._is_gil_enabled()
    expected = {'fastapi': '0.143.0', 'uvicorn': '0.54.0', 'pydantic': '2.14.1',
                'pydantic-settings': '2.15.0', 'SQLAlchemy': '2.1.4', 'psycopg': '3.3.6',
                'psycopg-binary': '3.3.6', 'alembic': '1.20.0', 'httpx': '0.28.1',
                'pydantic-core': '2.50.1',
                'rfc8785': '0.1.4', 'PyJWT': '2.15.1', 'pytest': '9.1.1'}
    assert {name: version(name) for name in expected} == expected


def test_native_validation_and_psycopg_binary_calls():
    class Value(BaseModel):
        item_id: UUID
        amount: int = Field(gt=0, strict=True)
    item = Value.model_validate_json('{"item_id":"00000000-0000-4000-8000-000000000001","amount":42}')
    assert item.amount == 42
    with pytest.raises(pydantic.ValidationError):
        Value(item_id=item.item_id, amount=True)
    assert pq.__impl__ == 'binary'
    assert pq.version() > 0  # Actual bundled libpq FFI, no database connection.
    assert sql.SQL('SELECT {}').format(sql.Identifier('probe"column')).as_string() == 'SELECT "probe""column"'


def test_real_uvicorn_httpx_valid_and_rejected_request():
    class Input(BaseModel):
        amount: int = Field(gt=0, strict=True)
    app = FastAPI()
    @app.post('/probe')
    async def probe(value: Input):
        return {'amount': value.amount}
    server = uvicorn.Server(uvicorn.Config(app, log_config=None, access_log=False,
                                          lifespan='off', timeout_graceful_shutdown=1))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(('127.0.0.1', 0))
        listener.listen()
        port = listener.getsockname()[1]
        errors = []
        def serve():
            try:
                server.run(sockets=[listener])
            except BaseException as error:
                errors.append(type(error).__name__)
        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 5
            while not server.started and thread.is_alive() and time.monotonic() < deadline:
                time.sleep(0.01)
            assert server.started and not errors
            with httpx.Client(base_url=f'http://127.0.0.1:{port}', timeout=2, trust_env=False) as client:
                result = client.post('/probe', json={'amount': 42})
                assert result.status_code == 200 and result.json() == {'amount': 42}
                assert client.post('/probe', json={'amount': 0}).status_code == 422
                assert client.post('/probe', json={'amount': True}).status_code == 422
        finally:
            server.should_exit = True
            thread.join(timeout=5)
            if thread.is_alive():
                server.force_exit = True
                thread.join(timeout=2)
        assert not thread.is_alive() and not errors


def test_settings_validate_explicit_synthetic_environment(monkeypatch):
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(env_prefix='ENV_QUALIFICATION_', env_file=None)
        limit: int = Field(gt=0)
    monkeypatch.setenv('ENV_QUALIFICATION_LIMIT', '42')
    assert Settings().limit == 42
    monkeypatch.setenv('ENV_QUALIFICATION_LIMIT', 'invalid')
    with pytest.raises(pydantic.ValidationError):
        Settings()


def test_jwt_signature_issuer_audience_and_expiry_are_checked():
    key = 'synthetic-qualification-key-only-32-bytes-minimum'
    claims = {'sub': 'synthetic', 'iss': 'env-fixture', 'aud': 'env-qualification',
              'exp': datetime.now(timezone.utc) + timedelta(minutes=2)}
    token = jwt.encode(claims, key, algorithm='HS256')
    options = {'algorithms': ['HS256'], 'issuer': 'env-fixture', 'audience': 'env-qualification'}
    assert jwt.decode(token, key, **options)['sub'] == 'synthetic'
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, 'different-synthetic-key-at-least-32-bytes', **options)
    for field, invalid, error in [('iss', 'other', jwt.InvalidIssuerError),
                                  ('aud', 'other', jwt.InvalidAudienceError),
                                  ('exp', 1, jwt.ExpiredSignatureError)]:
        changed = jwt.encode({**claims, field: invalid}, key, algorithm='HS256')
        with pytest.raises(error):
            jwt.decode(changed, key, **options)
    unsigned = jwt.encode(claims, key='', algorithm='none')
    with pytest.raises(jwt.InvalidAlgorithmError):
        jwt.decode(unsigned, key, **options)


def test_canonical_json_bytes_and_nonfinite_rejection():
    assert rfc8785.dumps({'z': 1, 'a': [True, 2]}) == b'{"a":[true,2],"z":1}'
    assert rfc8785.dumps({'small': 0.000001, 'n': 1e30, 'negative_zero': -0.0}) == b'{"n":1e+30,"negative_zero":0,"small":0.000001}'
    # RFC8785 sorts keys as UTF-16 code units, not Unicode scalar values.
    assert rfc8785.dumps({'\ue000': 2, '\U0001f600': 1}) == '{"\U0001f600":1,"\ue000":2}'.encode()
    assert rfc8785.dumps(2**53 - 1) == b'9007199254740991'
    for outside in [2**53, -(2**53)]:
        with pytest.raises(rfc8785.IntegerDomainError):
            rfc8785.dumps(outside)
    with pytest.raises(rfc8785.FloatDomainError):
        rfc8785.dumps({'value': float('nan')})


def test_postgres_sql_and_alembic_offline_output_without_database(monkeypatch):
    def forbidden_connection(*args, **kwargs):
        pytest.fail('Offline qualification must never open a database connection')
    monkeypatch.setattr(psycopg, 'connect', forbidden_connection)
    engine = sa.create_engine('postgresql+psycopg://')  # Lazy adapter construction only.
    try:
        assert engine.dialect.driver == 'psycopg' and engine.dialect.dbapi is psycopg
        statement = sa.select(sa.literal(42).label('answer'))
        assert str(statement.compile(dialect=engine.dialect, compile_kwargs={'literal_binds': True})) == 'SELECT 42 AS answer'
        bound = sa.select(sa.bindparam('answer', value=42))
        compiled = bound.compile(dialect=engine.dialect)
        assert compiled.params == {'answer': 42} and '%(answer)s' in str(compiled)
        output = io.StringIO()
        context = MigrationContext.configure(dialect=engine.dialect,
            opts={'as_sql': True, 'output_buffer': output, 'transactional_ddl': True})
        with context.begin_transaction():
            Operations(context).create_table('probe',
                sa.Column('id', sa.Integer, sa.Identity(), primary_key=True), schema='env_qualification')
        generated = output.getvalue()
        assert generated.startswith('BEGIN;') and generated.rstrip().endswith('COMMIT;')
        assert 'CREATE TABLE env_qualification.probe' in generated
        assert 'GENERATED BY DEFAULT AS IDENTITY' in generated and 'PRIMARY KEY (id)' in generated
    finally:
        engine.dispose()
