"""Custody adapter for the approved retained fixture. Never prepares resources."""
from contextlib import contextmanager
from hashlib import sha256
import os
from pathlib import Path
import sys
from uuid import uuid4
from unittest.mock import patch

from alembic.config import Config
from sqlalchemy import create_engine, pool, text
from sqlalchemy.engine import make_url

sys.path.insert(0, str(Path(__file__).resolve().parent))
import native_fixture as native

ROOT = native.ROOT
FIXTURE = native.BASE/'fixture-cff53592f5ca43a1a0cc65398957140f/fixture.json'
DATABASE = 'kdg_schema_659350f762c8494c9241b7b1c8ea9566'
FOUNDATION = '0001_kdg_foundation'
STORAGE = '0002_kdg_capture_storage'


def retained():
    value, original = native.load(FIXTURE)
    if value['database'] != DATABASE or value['run_id'] != native.RUN:
        raise ValueError('capture_commit_target_invalid')
    # Validates the known run's custody without preparing or changing resources.
    admin = native.administrator().set(database=DATABASE)
    return value, original, admin


def engine(url):
    return create_engine(make_url(url).set(drivername='postgresql+psycopg'),
        poolclass=pool.NullPool, hide_parameters=True,
        connect_args=dict(connect_timeout=5, hostaddr='127.0.0.1', sslmode='disable',
                          gssencmode='disable', passfile='/dev/null',
                          options='-c search_path=pg_catalog -c statement_timeout=10000 -c lock_timeout=2000'))


def revision(value):
    with native.connect(make_url(value['urls']['migrator']), readonly=True) as connection:
        return connection.execute('SELECT version_num FROM kdg_capture.alembic_version').fetchone()[0]


def configuration():
    """Only this test Config discovers the inert candidate; active ini is untouched."""
    config = Config(str(ROOT/'apps/kdg-capture/alembic.ini'))
    config.set_main_option('version_locations', os.pathsep.join(str(ROOT/p) for p in (
        'apps/kdg-capture/migrations/versions', 'apps/kdg-capture/migrations/candidates')))
    return config


@contextmanager
def migration_environment(value):
    url = make_url(value['urls']['migrator']).set(drivername='postgresql+psycopg')
    with patch.dict(os.environ, dict(KDG_MIGRATION_TARGET_ID='kdg-local',
        KDG_MIGRATION_ENVIRONMENT_KIND='local_disposable',
        KDG_MIGRATION_DATABASE_URL=url.render_as_string(hide_password=False))):
        yield


def receipt(phase, result):
    destination = FIXTURE.parent/('capture-commit-' + phase + '-' + uuid4().hex + '.json')
    native.write_private(destination, dict(result, phase=phase, run_id=native.RUN,
        database=DATABASE, fixture_sha256=sha256(FIXTURE.read_bytes()).hexdigest()))
    return destination


CANDIDATE = 'apps/kdg-capture/migrations/candidates/0002_capture_storage.py'


def migration_provenance(*, latest=False):
    """Known applied source, bound to original custody; revision alone is insufficient."""
    receipts = sorted(FIXTURE.parent.glob('capture-commit-migrate-*.json'),
                      key=lambda path: path.stat().st_mtime_ns)
    if not receipts:
        raise ValueError('capture_commit_migration_receipt_required')
    fixture_hash = sha256(FIXTURE.read_bytes()).hexdigest()
    candidate_hash = sha256((ROOT/CANDIDATE).read_bytes()).hexdigest()
    def matches(result):
        return (result.get('succeeded') is True and result.get('head') == STORAGE
            and result.get('database') == DATABASE and result.get('run_id') == native.RUN
            and result.get('fixture_sha256') == fixture_hash
            and result.get('sources', {}).get(CANDIDATE) == candidate_hash)
    records = [(path, native.private_json(path)) for path in receipts]
    applied = next(((path, result) for path, result in reversed(records)
                    if matches(result) and result.get('action') == 'upgrade'), None)
    if applied is None or (latest and not matches(records[-1][1])):
        raise ValueError('capture_commit_migration_reconciliation_required')
    return str(applied[0])


def migration_qualified(value):
    if revision(value) != STORAGE:
        raise ValueError('capture_commit_migration_required')
    return migration_provenance(latest=True)


def identities(value):
    result = {}
    for kind, role in zip(('migrator','runtime','operator'), native.ROLES):
        with native.connect(make_url(value['urls'][kind]), readonly=True) as connection:
            identity = connection.execute('SELECT current_user,session_user').fetchone()
            assert identity == (role, role), 'restricted_identity_required'
            assert connection.execute("SELECT rolsuper OR rolbypassrls OR rolcreaterole OR rolcreatedb FROM pg_roles WHERE rolname=current_user").fetchone() == (False,)
            assert connection.execute("SELECT pg_has_role(current_user,'supabase_admin','MEMBER')").fetchone() == (False,)
            if kind != 'migrator':
                assert connection.execute("SELECT pg_has_role(current_user,'kdg_capture_migrator','MEMBER')").fetchone() == (False,)
            result[kind] = dict(current_user=identity[0], session_user=identity[1])
    return result


def sentinel(admin):
    with native.connect(admin, readonly=True) as connection:
        assert connection.execute('SELECT value FROM fixture_foreign.sentinel').fetchall() == [(1,)]
