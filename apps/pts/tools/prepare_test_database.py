"""Bootstrap only a fresh local disposable PtS verification database.

Never use this fixture against Supabase or an existing application database.
"""
import os
from pathlib import Path
import sys
import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parents[3]


def main():
    url = os.environ['PTS_TEST_DATABASE_URL'].replace('postgresql+psycopg:', 'postgresql:')
    info = psycopg.conninfo.conninfo_to_dict(url)
    if info.get('host') not in {'127.0.0.1', 'localhost'} or info.get('port') != '55439':
        raise SystemExit('Fixture requires a fresh disposable database on localhost:55439')
    with psycopg.connect(url) as connection:
        if connection.execute("SELECT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname IN ('pts','identity','access','content'))").fetchone()[0]:
            raise SystemExit('Fixture refuses an already initialized database')
        connection.execute((ROOT/'apps/pts/tools/bootstrap_roles.sql').read_text())
        for role in ['pts_migrator','pts_runtime','pts_import','access_migrator','access_runtime','content_migrator','content_runtime']:
            connection.execute(sql.SQL('ALTER ROLE {} LOGIN PASSWORD {}').format(sql.Identifier(role), sql.Literal(info['password'])))
        connection.execute('''CREATE SCHEMA identity;
            CREATE TABLE identity.org(id uuid PRIMARY KEY, deleted_at timestamptz);
            CREATE TABLE identity.org_member(org_id uuid REFERENCES identity.org(id), user_id uuid,
                deleted_at timestamptz, PRIMARY KEY(org_id,user_id));
            ALTER TABLE identity.org ENABLE ROW LEVEL SECURITY;
            ALTER TABLE identity.org_member ENABLE ROW LEVEL SECURITY;''')
        connection.execute((ROOT/'services/access/tools/identity_bridge.sql').read_text())
    from tools.py.deploy_pts import migrate
    for owner in ('access','content','pts'):
        os.environ[owner.upper()+'_MIGRATION_DATABASE_URL'] = os.environ['PTS_TEST_DATABASE_URL'].replace('postgres:', owner+'_migrator:')
    migrate()
    print('Disposable fixture initialized; identity tables are minimal contract fixtures, not a Supabase migration.')


if __name__ == '__main__':
    main()
