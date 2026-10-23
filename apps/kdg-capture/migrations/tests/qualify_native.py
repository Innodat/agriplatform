"""Explicit owner adapter for the approved retained synthetic migration qualification."""
from pathlib import Path
from uuid import uuid4
import json
import os
import subprocess
import sys
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import make_url
sys.path.insert(0,str(Path(__file__).resolve().parent))
import native_fixture as fixture
sys.path.insert(0,str(fixture.ROOT/'apps/kdg-capture/migrations'))
from policy import POLICY


def upgrade(path):
    value,_ = fixture.load(path)
    url = make_url(value['urls']['migrator']).set(drivername='postgresql+psycopg')
    result = subprocess.run([sys.executable,'-I','-B','-m','alembic','-c',str(fixture.ROOT/'apps/kdg-capture/alembic.ini'),'upgrade','head'],
        cwd=fixture.ROOT,env={'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8',
        'KDG_MIGRATION_TARGET_ID':'kdg-local','KDG_MIGRATION_ENVIRONMENT_KIND':'local_disposable',
        'KDG_MIGRATION_DATABASE_URL':url.render_as_string(hide_password=False)},capture_output=True,timeout=45)
    log = Path(path).parent/('upgrade-'+uuid4().hex+'.log')
    fd=os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as output:output.write(result.stdout+result.stderr)
    return dict(ok=result.returncode==0,exit_code=result.returncode,log=str(log),
                safe_failure=b'owned_migration_failed_requires_reconciliation' in result.stderr)


def qualify(path):
    sys.path.insert(0,str(fixture.ROOT/'apps/kdg-capture/native-database-tools'))
    from native_migration_checks import check_native_migrations
    value,receipt=fixture.load(path)
    engines={kind:create_engine(make_url(raw).set(drivername='postgresql+psycopg'),poolclass=pool.NullPool,hide_parameters=True,
        connect_args={'connect_timeout':5,'hostaddr':'127.0.0.1','sslmode':'disable','gssencmode':'disable','passfile':'/dev/null'})
        for kind,raw in value['urls'].items()}
    try:
        report=check_native_migrations(engines,POLICY,lambda:upgrade(path),'fixture_foreign','0001_kdg_foundation')
        with fixture.connect(fixture.administrator().set(database=value['database']),readonly=True) as c:
            if c.execute('SELECT value FROM fixture_foreign.sentinel').fetchall()!=[(1,)]:
                raise ValueError('foreign_sentinel_changed')
        if fixture.retained_cluster_state(fixture.administrator(),value['database'])!=receipt['before']:
            raise ValueError('retained_metadata_changed')
        report.update(database=value['database'],retained_metadata_unchanged=True,foreign_sentinel_unchanged=True)
        destination=Path(path).parent/('qualification-'+uuid4().hex+'.json')
        fixture.write_private(destination,report)
        return dict(qualified=True,report=str(destination),stages=report['stages'])
    finally:
        for engine in engines.values():engine.dispose()


if __name__=='__main__':
    try:
        if len(sys.argv)!=3 or sys.argv[1] not in ('--upgrade','--qualify'):
            raise ValueError('native_action_invalid')
        result=upgrade(sys.argv[2]) if sys.argv[1]=='--upgrade' else qualify(sys.argv[2])
        print(json.dumps(result))
        if result.get('ok') is False:raise SystemExit(1)
    except Exception:
        print('kdg_native_qualification_failed',file=sys.stderr)
        raise SystemExit(1) from None
