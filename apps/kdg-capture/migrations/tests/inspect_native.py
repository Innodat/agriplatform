"""Dedicated SELECT-only retained fixture inspection. No setup or mutation imports."""
if not __debug__:
    raise RuntimeError('kdg_native_inspection_optimized_python_prohibited')
from hashlib import sha256
from pathlib import Path
import json
import os
import re
import stat
import sys
import psycopg
from sqlalchemy.engine import make_url
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'platform/deployment/.local/kdg-native-focused-20261023'
RUN='99b7231c-0a5b-4bdb-98e8-3329564c526a'
ROLES=['kdg_capture_migrator','kdg_capture_runtime','kdg_capture_operator']


def read_private(path):
    info=path.stat()
    if path.resolve()!=path or not stat.S_ISREG(info.st_mode) or info.st_mode&0o077 or info.st_uid!=os.getuid() or info.st_nlink!=1:
        raise ValueError('inspection_custody_invalid')
    return json.loads(path.read_text())


def connect(url):
    return psycopg.connect(url.render_as_string(hide_password=False),connect_timeout=5,hostaddr='127.0.0.1',
        sslmode='disable',gssencmode='disable',passfile='/dev/null',
        options='-c default_transaction_read_only=on -c search_path=pg_catalog -c statement_timeout=10000')


def inspect(path):
    if path.name!='fixture.json' or path.parent.parent!=BASE:
        raise ValueError('inspection_fixture_invalid')
    fixture=read_private(path);prepared=read_private(path.with_name('prepared.json'))
    if fixture['run_id']!=RUN or prepared['fixture_sha256']!=sha256(path.read_bytes()).hexdigest() or not re.fullmatch('kdg_schema_[0-9a-f]{32}',fixture['database']):
        raise ValueError('inspection_fixture_invalid')
    for kind,role in zip(('migrator','runtime','operator'),ROLES):
        url=make_url(fixture['urls'][kind])
        if (url.drivername,url.host,url.port,url.username,url.database)!=('postgresql','127.0.0.1',55482,role,fixture['database']) or url.query or not url.password:
            raise ValueError('inspection_url_invalid')
        with connect(url) as c:
            assert c.execute('SHOW transaction_read_only').fetchone()==('on',)
            assert c.execute('SELECT current_user,session_user').fetchone()==(role,role)
    source=ROOT/'platform/deployment/.local/identity-baseline/organization-check-reviewed3-20261022'
    if read_private(source/'run.json')['run_id']!=RUN:raise ValueError('inspection_source_invalid')
    admin=make_url(read_private(source/'credentials.json')['databases']['bridge'])
    if (admin.drivername,admin.host,admin.port,admin.username)!=('postgresql','127.0.0.1',55482,'postgres') or admin.query or not admin.password:
        raise ValueError('inspection_admin_invalid')
    admin=admin.set(database='postgres',username='supabase_admin')
    with connect(admin) as c:
        assert c.execute('SHOW transaction_read_only').fetchone()==('on',)
        databases=c.execute('SELECT datname,pg_get_userbyid(datdba),datacl::text FROM pg_database WHERE datname<>%s ORDER BY datname',(fixture['database'],)).fetchall()
        roles=c.execute('SELECT rolname,rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,rolreplication,rolbypassrls,rolconnlimit,rolvaliduntil::text,rolconfig FROM pg_roles WHERE NOT(rolname=ANY(%s)) ORDER BY rolname',(ROLES,)).fetchall()
        memberships=c.execute('SELECT roleid,member,grantor,admin_option,inherit_option,set_option FROM pg_auth_members ORDER BY roleid,member').fetchall()
        metadata=sha256(json.dumps([databases,roles,memberships],default=str).encode()).hexdigest()
        assert metadata==prepared['before']
        actual=c.execute('SELECT rolname,rolsuper,rolcreaterole,rolcreatedb,rolbypassrls,rolreplication,rolcanlogin FROM pg_roles WHERE rolname=ANY(%s) ORDER BY rolname',(ROLES,)).fetchall()
        assert actual==[(role,False,False,False,False,False,True) for role in sorted(ROLES)]
    with connect(admin.set(database=fixture['database'])) as c:
        assert c.execute('SHOW transaction_read_only').fetchone()==('on',)
        assert c.execute('SELECT version_num FROM kdg_capture.alembic_version').fetchall()==[('0001_kdg_foundation',)]
        assert c.execute("SELECT tablename FROM pg_tables WHERE schemaname='kdg_capture' ORDER BY tablename").fetchall()==[('alembic_version',)]
        assert c.execute('SELECT value FROM fixture_foreign.sentinel').fetchall()==[(1,)]
        for role in ROLES[1:]:
            assert c.execute("SELECT has_schema_privilege(%s,'kdg_capture','CREATE'),has_table_privilege(%s,'kdg_capture.alembic_version','SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')",(role,role)).fetchone()==(False,False)
    return dict(inspected=True,read_only=True,head='0001_kdg_foundation',ledger_only=True,
        foreign_sentinel_unchanged=True,preexisting_role_database_metadata_unchanged=True,
        historical_rows_rehashed=False,business_table_rls=False,release_ready=False)


if __name__=='__main__':
    try:
        if len(sys.argv)!=2:raise ValueError('inspection_arguments_invalid')
        print(json.dumps(inspect(Path(sys.argv[1]).absolute())))
    except Exception:
        print('kdg_native_inspection_failed',file=sys.stderr)
        raise SystemExit(1) from None
