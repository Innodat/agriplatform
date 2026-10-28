"""KDG-owned migration policy; no database access on import."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'database-tools'))
from owned_migration import MigrationPolicy,MigrationError

POLICY=MigrationPolicy('kdg_capture','kdg_capture_migrator','kdg_capture_runtime','kdg_capture_operator')

def connection_url(environment):
    """Candidate is restricted to explicit known synthetic target; no target discovery."""
    from sqlalchemy.engine import make_url
    try:
        if environment.get('KDG_MIGRATION_ENVIRONMENT_KIND') not in ('local_disposable','ci_disposable'):
            raise ValueError()
        target=environment.get('KDG_MIGRATION_TARGET_ID')
        if target=='kdg-local':
            port=55482
        elif target=='kdg-story31-synthetic':
            selected=environment.get('KDG_MIGRATION_SYNTHETIC_PORT')
            if (type(selected) is not str or not selected.isascii() or not selected.isdigit()
                or not 1<=int(selected)<=65535 or selected!=str(int(selected)) or int(selected)==55482):
                raise ValueError()
            port=int(selected)
        else:
            raise ValueError()
        raw=environment.get('KDG_MIGRATION_DATABASE_URL')
        if type(raw) is not str or not raw or any(ord(c)<33 or ord(c)>126 for c in raw):raise ValueError()
        url=make_url(raw)
        if (url.drivername!='postgresql+psycopg' or url.host!='127.0.0.1' or url.port!=port
            or url.username!=POLICY.migrator or not url.password or url.query
            or not url.database or __import__('re').fullmatch(r'kdg_schema_[0-9a-f]{32}',url.database) is None):raise ValueError()
        return url
    except Exception:
        raise MigrationError('kdg_migration_configuration_invalid') from None

def guard_command(command, destination, *, offline=False):
    if offline or command!='upgrade' or destination!='head':
        raise MigrationError('kdg_migration_upgrade_head_only')
