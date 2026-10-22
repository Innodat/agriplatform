"""Generate ONLY from pinned SQL in a newly created disposable local fixture.

Never accepts an existing database/schema as a reference source. Cluster roles must
be absent before any mutation. Also shared by guarded acceptance fixtures.
"""
import os
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import unquote,urlsplit
import psycopg
from psycopg import sql
from sqlalchemy import create_engine
sys.path.insert(0,str(Path(__file__).resolve().parent))
from baseline import APP,verify_pins
from catalogue import snapshot
ROLES = ['anon','authenticated','service_role','scribeswell_runtime','scribeswell_import','scribeswell_migrator']

@contextmanager
def prepared_fixture():
    verify_pins()
    url = os.environ.get('SCRIBESWELL_TEST_DATABASE_URL','')
    if urlsplit(url).hostname not in ('127.0.0.1','localhost'):
        raise RuntimeError('disposable_local_fixture_required')
    for key in list(os.environ):
        if key.startswith('PG'):
            del os.environ[key]
    name = 'scribeswell_migration_' + uuid.uuid4().hex
    created = []
    with psycopg.connect(url,autocommit=True) as control:
        identity=control.execute("SELECT current_user,session_user,current_setting('server_version_num')::int").fetchone()
        if identity[:2]!=('postgres','postgres') or not 170000<=identity[2]<180000:
            raise RuntimeError('fixture_postgres17_owner_required')
        if control.execute('SELECT rolname FROM pg_roles WHERE rolname=ANY(%s)',(ROLES,)).fetchall():
            raise RuntimeError('fixture_roles_must_be_absent')
        control.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(name)))
        try:
            fixture_url = urlsplit(url)._replace(path='/'+name).geturl()
            with psycopg.connect(fixture_url,autocommit=True) as admin:
                for role in ROLES[:3]:
                    admin.execute(sql.SQL('CREATE ROLE {}').format(sql.Identifier(role)))
                    created.append(role)
                admin.execute('ALTER ROLE service_role BYPASSRLS')
                admin.execute((APP / next(iter(__import__('baseline').PINS))).read_text())
                admin.execute((APP / 'deployment/bootstrap/001_direct_database_roles.sql').read_text())
                created.extend(ROLES[3:5])
                admin.execute('CREATE ROLE scribeswell_migrator LOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOREPLICATION')
                created.append('scribeswell_migrator')
                password = unquote(urlsplit(url).password or '')
                for role in ROLES[3:]:
                    admin.execute(sql.SQL('ALTER ROLE {} PASSWORD {}').format(sql.Identifier(role),sql.Literal(password)))
                admin.execute('ALTER SCHEMA scribeswell OWNER TO scribeswell_migrator')
                relations=admin.execute("SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='scribeswell' AND c.relkind IN ('r','v') ORDER BY c.relkind,c.relname").fetchall()
                for (relation,) in relations:
                    admin.execute(sql.SQL('ALTER TABLE scribeswell.{} OWNER TO scribeswell_migrator').format(sql.Identifier(relation)))
                yield admin,fixture_url
        finally:
            control.execute(sql.SQL('DROP DATABASE {} WITH (FORCE)').format(sql.Identifier(name)))
            for role in reversed(created):
                control.execute(sql.SQL('DROP ROLE {}').format(sql.Identifier(role)))

def generate(destination=None):
    import json
    with prepared_fixture() as (_,url):
        engine=create_engine(url.replace('postgresql://','postgresql+psycopg://',1))
        try:
            with engine.begin() as connection:
                connection.exec_driver_sql('SET LOCAL search_path=pg_catalog')
                reference=snapshot(connection)
        finally:
            engine.dispose()
    destination=Path(destination) if destination is not None else Path(__file__).with_name('reference.json')
    with destination.open('x') as out:
        json.dump(reference,out,indent=2,ensure_ascii=False)
        out.write('\n')

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    generate(parser.parse_args().output)
