"""Controlled optional private history; caller owns process deadline and activation."""
import json
import os
from pathlib import Path
import sys
APP=Path(__file__).resolve().parents[1]

def selected(environ):
    enabled=environ.get('SCRIBESWELL_STUDIES_MIGRATION_ENABLED','false')
    supplied='SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL' in environ
    if enabled not in ('true','false') or (enabled=='true')!=supplied:raise ValueError('studies_migration_configuration_invalid')
    return enabled=='true'

def upgrade(environ):
    from sqlalchemy.engine import make_url
    from alembic import command
    from alembic.config import Config
    raw=environ['SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL']
    url=make_url(raw)
    if url.username!='scribeswell_studies_migrator':raise ValueError('studies_migration_authority_invalid')
    os.environ['SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL']=raw
    command.upgrade(Config(str(APP/'studies-alembic.ini')),'head')
    return {'complete':True,'owner':'scribeswell_studies','after':'scribeswell_studies_0001','recovery':'forward-only'}

if __name__=='__main__':
    try:
        payload=json.loads(sys.stdin.read(16385))
        if not isinstance(payload,dict) or set(payload)!={'url'}:raise ValueError
        sys.stdout.write(json.dumps(upgrade({'SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL':payload['url']})))
    except BaseException:
        sys.stdout.write('{"complete":false,"code":"scribeswell_studies_migration_failed"}')
        raise SystemExit(1) from None
