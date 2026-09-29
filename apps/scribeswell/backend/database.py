"""Scribeswell-only PostgreSQL repository. No HTTP/Data API fallback."""
import logging
from contextlib import contextmanager
from contextvars import ContextVar
from urllib.parse import parse_qs, unquote, urlsplit

import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

class SafePoolLogs(logging.Filter):
    def filter(self, record):
        record.msg = '{"service":"scribeswell","action":"pool","code":"database_connection_event"}'
        record.args = ()
        record.exc_info = None
        record.exc_text = None
        return True


logging.getLogger('psycopg.pool').addFilter(SafePoolLogs())
logging.getLogger('psycopg').addFilter(SafePoolLogs())

TABLES = {'book', 'chapter', 'verse', 'word', 'morpheme'}


class DatabaseUnavailable(RuntimeError):
    def __init__(self):
        super().__init__('Database temporarily unavailable')


def validate_url(value, role, production=False):
    try:
        url = urlsplit(value)
        query = parse_qs(url.query, keep_blank_values=True)
        username = unquote(url.username or '')
        host = url.hostname or ''
        valid_role = username == role or (host.endswith('.pooler.supabase.com') and username.startswith(role + '.') and len(username) > len(role) + 1)
        if (url.scheme not in ('postgresql', 'postgresql+psycopg') or not host or not url.password or not valid_role
                or not url.path or url.fragment or set(query) - {'sslmode', 'connect_timeout'}
                or ((production or host not in ('127.0.0.1', 'localhost', '::1')) and query.get('sslmode') not in (['require'], ['verify-full']))):
            raise ValueError
        if 'connect_timeout' in query and (len(query['connect_timeout']) != 1 or not 1 <= int(query['connect_timeout'][0]) <= 10):
            raise ValueError
        return value
    except (ValueError, TypeError):
        raise ValueError('Invalid database configuration') from None


class Database:
    def __init__(self, url, role, *, production=False, max_size=8, timeout=5):
        self.pool = ConnectionPool(
            validate_url(url, role, production).replace('postgresql+psycopg://', 'postgresql://', 1), min_size=0, max_size=max_size,
            timeout=timeout, max_waiting=32, reconnect_timeout=5, open=False,
            kwargs={'row_factory': dict_row, 'connect_timeout': 5, 'autocommit': True,
                    'options': '-c statement_timeout=15000 -c lock_timeout=3000 -c idle_in_transaction_session_timeout=15000'},
            # Suppress libpq errors (may contain addresses or SQL) at the source.
            name='scribeswell',
        )
        self._connection = ContextVar('scribeswell_connection', default=None)

    def open(self):
        self.pool.open()

    def close(self):
        self.pool.close()

    @contextmanager
    def connection(self):
        current = self._connection.get()
        if current is not None:
            yield current
            return
        try:
            with self.pool.connection() as connection:
                yield connection
        except (psycopg.Error, TimeoutError):
            raise DatabaseUnavailable() from None

    @contextmanager
    def transaction(self):
        with self.connection() as connection:
            token = self._connection.set(connection)
            try:
                with connection.transaction():
                    yield
            finally:
                self._connection.reset(token)

    def read(self, table, *, columns='*', filters=None, in_filters=None, order=('id',)):
        if table.removesuffix('_read') not in TABLES:
            raise ValueError('Unknown Scribeswell table')
        table = table.removesuffix('_read')
        fields = sql.SQL('*') if columns == '*' else sql.SQL(',').join(map(sql.Identifier, columns.split(',')))
        predicates, values = [], []
        for key, value in (filters or {}).items():
            predicates.append(sql.SQL('{} = %s').format(sql.Identifier(key)))
            values.append(value)
        for key, value in (in_filters or {}).items():
            predicates.append(sql.SQL('{} = ANY(%s)').format(sql.Identifier(key)))
            values.append(list(value))
        query = sql.SQL('SELECT {} FROM scribeswell.{}').format(fields, sql.Identifier(table))
        if predicates:
            query += sql.SQL(' WHERE ') + sql.SQL(' AND ').join(predicates)
        if order:
            query += sql.SQL(' ORDER BY ') + sql.SQL(',').join(map(sql.Identifier, order))
        with self.connection() as connection:
            return connection.execute(query, values).fetchall()

    def one(self, table, **kwargs):
        rows = self.read(table, **kwargs)
        return rows[0] if rows else None

    def upsert(self, table, rows, conflict):
        if table not in TABLES:
            raise ValueError('Unknown Scribeswell table')
        if not rows:
            return
        fields = list(rows[0])
        keys = conflict.split(',')
        updates = [key for key in fields if key not in keys] or [keys[0]]
        query = sql.SQL('INSERT INTO scribeswell.{} ({}) VALUES ({}) ON CONFLICT ({}) DO UPDATE SET {}').format(
            sql.Identifier(table), sql.SQL(',').join(map(sql.Identifier, fields)),
            sql.SQL(',').join(sql.Placeholder() for _ in fields),
            sql.SQL(',').join(map(sql.Identifier, keys)),
            sql.SQL(',').join(sql.SQL('{} = EXCLUDED.{}').format(sql.Identifier(key), sql.Identifier(key)) for key in updates))
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, [[row[key] for key in fields] for row in rows])


_runtime = None


def get_database():
    if _runtime is None:
        raise DatabaseUnavailable()
    return _runtime


def open_database():
    global _runtime
    from config import settings
    _runtime = Database(settings.scribeswell_database_url.get_secret_value(), 'scribeswell_runtime', production=settings.app_env == 'production')
    _runtime.open()


def close_database():
    global _runtime
    if _runtime is not None:
        _runtime.close()
        _runtime = None
