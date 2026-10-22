"""Explicit synthetic-only fixture preparation. Retains database/roles/private input.

No source credentials or connection exceptions are printed. Run with prepared Python.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import secrets
import sys
from uuid import uuid4

import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url


def prepare(admin_path, proof):
    proof.mkdir(mode=0o700, parents=True, exist_ok=False)
    admin_url = json.loads(admin_path.read_text())['admin_url']
    url = make_url(admin_url)
    assert (url.host,url.port,url.database)==('127.0.0.1',55482,'postgres'), 'fixture_local_target_required'
    assert not url.query, 'fixture_url_options_prohibited'
    suffix = uuid4().hex[:16]
    database, migrator, runtime = ['atomic_' + suffix + '_' + part for part in ('db','m','r')]
    passwords = [secrets.token_urlsafe(32), secrets.token_urlsafe(32)]
    # Credential URL is held privately; psycopg accepts only the postgres scheme.
    def dsn(u):
        return u.set(drivername='postgresql').render_as_string(hide_password=False)
    with psycopg.connect(dsn(url), user='supabase_admin', autocommit=True, connect_timeout=3, options='-c statement_timeout=5000 -c lock_timeout=2000') as conn:
        assert conn.execute("SELECT rolsuper FROM pg_roles WHERE rolname=current_user").fetchone()[0], 'fixture_superuser_required'
        for role, password in zip((migrator,runtime), passwords):
            conn.execute(sql.SQL('CREATE ROLE {} LOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE PASSWORD {}').format(sql.Identifier(role),sql.Literal(password)))
        conn.execute(sql.SQL('CREATE DATABASE {} OWNER {}').format(sql.Identifier(database),sql.Identifier(migrator)))
    urls = {label: dsn(url.set(database=database, username=role,password=password))
            for label,role,password in zip(('migrator','runtime'),(migrator,runtime),passwords)}
    with psycopg.connect(urls['migrator'], autocommit=True, connect_timeout=3, options='-c statement_timeout=5000 -c lock_timeout=2000') as conn:
        conn.execute(Path(__file__).with_name('atomic_write_fixture.sql').read_text())
        conn.execute(sql.SQL('GRANT USAGE ON SCHEMA sample TO {}').format(sql.Identifier(runtime)))
        conn.execute(sql.SQL('GRANT SELECT,INSERT,UPDATE ON sample.record TO {}').format(sql.Identifier(runtime)))
        conn.execute(sql.SQL('GRANT SELECT,INSERT ON sample.outcome,sample.revision TO {}').format(sql.Identifier(runtime)))
        conn.execute(sql.SQL('GRANT SELECT ON sample.actor TO {}').format(sql.Identifier(runtime)))
    private = proof/'fixture.json'
    with private.open('x') as handle:
        os.chmod(private,0o600)
        json.dump(urls,handle)
    with (proof/'prepared.json').open('x') as handle:
        json.dump({'synthetic':True,'retained':True,'database':database,'roles':[migrator,runtime],'sql_sha256':sha256(Path(__file__).with_name('atomic_write_fixture.sql').read_bytes()).hexdigest()},handle)
    print('atomic_fixture_prepared')


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--admin',type=Path,required=True)
    parser.add_argument('--proof',type=Path,required=True)
    args=parser.parse_args()
    try:
        prepare(args.admin,args.proof)
    except Exception:
        print('atomic_fixture_preparation_failed',file=sys.stderr)
        raise SystemExit(1) from None
