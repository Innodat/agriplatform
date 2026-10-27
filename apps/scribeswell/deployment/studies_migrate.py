"""Controlled optional private history; caller owns process deadline and activation."""
import json
import os
from pathlib import Path
import sys
APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP/'deployment'))
from studies_release_contract import TARGET, REVISIONS, valid_result

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
    from alembic.script import ScriptDirectory
    config=Config(str(APP/'studies-alembic.ini'))
    history=ScriptDirectory.from_config(config)
    if history.get_heads()!=[TARGET] or set(revision.revision for revision in history.walk_revisions())!=set(REVISIONS):
        raise ValueError('studies_migration_history_invalid')
    config.attributes['scribeswell_studies_expected_head']=TARGET
    command.upgrade(config,'head')
    result={'complete':True,'owner':'scribeswell_studies',
            'before':config.attributes['scribeswell_studies_before'],
            'after':config.attributes['scribeswell_studies_after'],'recovery':'forward-only'}
    if not valid_result(result):raise ValueError('studies_migration_report_invalid')
    return result

if __name__=='__main__':
    try:
        payload=json.loads(sys.stdin.read(16385))
        if not isinstance(payload,dict) or set(payload)!={'url'}:raise ValueError
        sys.stdout.write(json.dumps(upgrade({'SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL':payload['url']})))
    except BaseException:
        sys.stdout.write('{"complete":false,"code":"scribeswell_studies_migration_failed"}')
        raise SystemExit(1) from None
