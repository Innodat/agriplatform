"""Coordinate owned migrations. Completion is never deployment authorization."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[2]
OWNERS = [('access', 'services/access'), ('content', 'services/content-service'), ('pts', 'apps/pts')]


def now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def deployment_lock():
    db = create_engine(os.environ['ACCESS_MIGRATION_DATABASE_URL'], hide_parameters=True,
                       connect_args={'connect_timeout': 5})
    try:
        with db.connect() as connection:
            locked = connection.execute(text("SELECT pg_try_advisory_lock(hashtextextended('pts-coordinated-release',0))")).scalar_one()
            if not locked:
                raise RuntimeError('Another PtS deployment is running')
            try:
                yield
            finally:
                connection.execute(text("SELECT pg_advisory_unlock(hashtextextended('pts-coordinated-release',0))"))
    finally:
        db.dispose()


def revisions(owner):
    db = create_engine(os.environ[owner.upper()+'_MIGRATION_DATABASE_URL'], hide_parameters=True,
                       connect_args={'connect_timeout': 5})
    try:
        with db.connect() as connection:
            if not connection.execute(text('SELECT to_regclass(:name)'), {'name': owner+'.alembic_version'}).scalar():
                return []
            return list(connection.execute(text(f'SELECT version_num FROM {owner}.alembic_version ORDER BY version_num')).scalars())
    finally:
        db.dispose()


def migrate(run=subprocess.run, acquire_lock=deployment_lock, progress=None, inspect=revisions):
    for owner, _ in OWNERS:
        if not os.environ.get(owner.upper()+'_MIGRATION_DATABASE_URL'):
            raise RuntimeError(f'Missing {owner} migration configuration')
    with acquire_lock():
        for owner, folder in OWNERS:
            entry = progress[owner] if progress is not None else None
            try:
                if entry is not None:
                    entry.update(status='running', started_at=now(), before=inspect(owner))
                run([sys.executable, '-m', 'alembic', '-c', str(ROOT/folder/'alembic.ini'), 'upgrade', 'head'], check=True)
                if entry is not None:
                    entry.update(status='succeeded', after=inspect(owner), finished_at=now())
            except Exception:
                if entry is not None:
                    entry.update(status='failed', finished_at=now())
                    try:
                        entry['after'] = inspect(owner)
                    except Exception:
                        entry['after'] = None
                        entry['outcome_requires_reconciliation'] = True
                raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--release-id', required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    # Reserve before doing work; never overwrite another attempt's evidence.
    try:
        evidence = args.evidence.open('x')
    except FileExistsError:
        raise SystemExit('Use a fresh evidence path for every release attempt') from None
    revision = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    dirty = bool(subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT, capture_output=True, text=True, check=True).stdout)
    report = {'release_id': args.release_id, 'code_revision': revision, 'working_tree_dirty': dirty,
              'started_at': now(), 'migrations_complete': False, 'activation_allowed': False,
              'owners': {owner: {'status': 'not_attempted'} for owner, _ in OWNERS}}
    try:
        migrate(progress=report['owners'])
        report['migrations_complete'] = True
        report['next_step'] = 'Verify configured auth/storage, compatibility and obtain deployment authorization.'
    except Exception:
        report['code'] = 'migration_failed'
        raise
    finally:
        report['finished_at'] = now()
        json.dump(report, evidence, indent=2)
        evidence.write('\n')
        evidence.close()


if __name__ == '__main__':
    main()
