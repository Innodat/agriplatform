"""Explicit synthetic KDG fixture preparation; never runs on import. Retain resources."""
from hashlib import sha256
from pathlib import Path
from uuid import uuid4
import json
import os
import re
import secrets
import stat
import sys
import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[4]
RUN = '99b7231c-0a5b-4bdb-98e8-3329564c526a'
SOURCE = ROOT/'platform/deployment/.local/identity-baseline/organization-check-reviewed3-20261022'
BASE = ROOT/'platform/deployment/.local/kdg-native-focused-20261023'
ROLES = ('kdg_capture_migrator', 'kdg_capture_runtime', 'kdg_capture_operator')


def private_json(path):
    path = Path(path)
    info = path.stat()
    if (not path.is_absolute() or path.resolve() != path or not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid() or info.st_mode & 0o077 or info.st_nlink != 1):
        raise ValueError('fixture_custody_invalid')
    return json.loads(path.read_text())


def write_private(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as output:
        json.dump(value, output, sort_keys=True, indent=2)


def administrator():
    sys.path.insert(0, str(ROOT/'platform/deployment'))
    import dev, native_cli
    target_path = ROOT/'platform/deployment/environments/kdg-local.json'
    raw = dev.read(target_path)
    native_cli.check_run(ROOT/'platform/deployment/.local/kdg'/RUN, dev.decode(raw), raw, RUN)
    if private_json(SOURCE/'run.json')['run_id'] != RUN:
        raise ValueError('fixture_source_invalid')
    url = make_url(private_json(SOURCE/'credentials.json')['databases']['bridge'])
    if ((url.drivername, url.host, url.port, url.username) != ('postgresql', '127.0.0.1', 55482, 'postgres')
            or not url.password or url.query):
        raise ValueError('fixture_source_invalid')
    return url.set(database='postgres', username='supabase_admin')


def connect(url, readonly=False):
    return psycopg.connect(url.render_as_string(hide_password=False), connect_timeout=5,
        hostaddr='127.0.0.1', sslmode='disable', gssencmode='disable', passfile='/dev/null',
        options='-c search_path=pg_catalog -c statement_timeout=10000 -c lock_timeout=2000'
                + (' -c default_transaction_read_only=on' if readonly else ''))


def retained_cluster_state(admin, new_database):
    """SELECT-only metadata snapshot, excluding only this fixture's new objects.

    This checks preexisting role/database definitions, not every historical data row.
    No historical qualification script is imported or executed.
    """
    with connect(admin, readonly=True) as c:
        if c.execute('SHOW transaction_read_only').fetchone()[0] != 'on':
            raise ValueError('fixture_readonly_required')
        databases = c.execute('SELECT datname,pg_get_userbyid(datdba),datacl::text FROM pg_database WHERE datname<>%s ORDER BY datname', (new_database,)).fetchall()
        roles = c.execute('SELECT rolname,rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,rolreplication,rolbypassrls,rolconnlimit,rolvaliduntil::text,rolconfig FROM pg_roles WHERE NOT(rolname=ANY(%s)) ORDER BY rolname', (list(ROLES),)).fetchall()
        memberships = c.execute('SELECT roleid,member,grantor,admin_option,inherit_option,set_option FROM pg_auth_members ORDER BY roleid,member').fetchall()
    return sha256(json.dumps([databases, roles, memberships], default=str).encode()).hexdigest()


def prepare():
    admin = administrator()
    database = 'kdg_schema_' + uuid4().hex
    with connect(admin, readonly=True) as c:
        if c.execute('SELECT current_user,session_user,rolsuper FROM pg_roles WHERE rolname=current_user').fetchone() != ('supabase_admin','supabase_admin',True):
            raise ValueError('fixture_admin_invalid')
        if c.execute('SELECT 1 FROM pg_roles WHERE rolname=ANY(%s)', (list(ROLES),)).fetchone():
            raise ValueError('fixture_existing_roles_refused')
    before = retained_cluster_state(admin, database)
    BASE.mkdir(mode=0o700, parents=True, exist_ok=True)
    directory = BASE/('fixture-' + uuid4().hex)
    directory.mkdir(mode=0o700)
    passwords = {role: secrets.token_urlsafe(32) for role in ROLES}
    fixture = dict(run_id=RUN, database=database, target_id='kdg-local', environment_kind='local_disposable',
        urls={kind: admin.set(database=database, username=role, password=passwords[role]).render_as_string(hide_password=False)
              for kind,role in zip(('migrator','runtime','operator'), ROLES)})
    write_private(directory/'fixture.json', fixture)
    write_private(directory/'planned.json', dict(database=database, roles=ROLES, retained=True, before=before))
    with connect(admin) as c:
        for role in ROLES:
            c.execute(sql.SQL('CREATE ROLE {} LOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD {}').format(sql.Identifier(role), sql.Literal(passwords[role])))
    with connect(admin) as c:
        c.autocommit = True
        c.execute(sql.SQL('CREATE DATABASE {} OWNER supabase_admin TEMPLATE template0').format(sql.Identifier(database)))
    with connect(admin.set(database=database)) as c:
        c.execute(sql.SQL('REVOKE ALL ON DATABASE {} FROM PUBLIC').format(sql.Identifier(database)))
        c.execute(sql.SQL('GRANT CONNECT ON DATABASE {} TO {}').format(sql.Identifier(database), sql.SQL(',').join(map(sql.Identifier, ROLES))))
        c.execute('CREATE SCHEMA kdg_capture AUTHORIZATION kdg_capture_migrator')
        c.execute('REVOKE ALL ON SCHEMA kdg_capture FROM PUBLIC')
        c.execute('GRANT USAGE ON SCHEMA kdg_capture TO kdg_capture_runtime,kdg_capture_operator')
        c.execute('CREATE SCHEMA fixture_foreign AUTHORIZATION supabase_admin')
        c.execute('REVOKE ALL ON SCHEMA fixture_foreign FROM PUBLIC')
        c.execute('GRANT USAGE ON SCHEMA fixture_foreign TO kdg_capture_migrator,kdg_capture_runtime,kdg_capture_operator')
        c.execute('CREATE TABLE fixture_foreign.sentinel(value integer PRIMARY KEY)')
        c.execute('INSERT INTO fixture_foreign.sentinel VALUES(1)')
    if retained_cluster_state(admin, database) != before:
        raise ValueError('fixture_retained_metadata_changed')
    write_private(directory/'prepared.json', dict(retained=True, before=before,
        fixture_sha256=sha256((directory/'fixture.json').read_bytes()).hexdigest()))
    return directory/'fixture.json'


def load(path):
    path = Path(path).absolute()
    if path.name != 'fixture.json' or path.parent.parent != BASE or not path.parent.name.startswith('fixture-'):
        raise ValueError('fixture_path_invalid')
    fixture = private_json(path)
    receipt = private_json(path.with_name('prepared.json'))
    if receipt['fixture_sha256'] != sha256(path.read_bytes()).hexdigest() or fixture['run_id'] != RUN:
        raise ValueError('fixture_changed')
    if not re.fullmatch('kdg_schema_[0-9a-f]{32}', fixture['database']):
        raise ValueError('fixture_database_invalid')
    for kind,role in zip(('migrator','runtime','operator'), ROLES):
        url = make_url(fixture['urls'][kind])
        if ((url.drivername,url.host,url.port,url.database,url.username) != ('postgresql','127.0.0.1',55482,fixture['database'],role)
                or not url.password or url.query):
            raise ValueError('fixture_url_invalid')
    return fixture, receipt


if __name__ == '__main__':
    try:
        if sys.argv[1:] != ['--prepare']:
            raise ValueError('fixture_action_invalid')
        print(json.dumps({'prepared':True, 'fixture':str(prepare())}))
    except Exception:
        print('kdg_native_fixture_preparation_failed', file=sys.stderr)
        raise SystemExit(1) from None
