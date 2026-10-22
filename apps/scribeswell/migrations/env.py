"""All mutation is inside the verified adoption transaction."""
import os
from alembic import context
from sqlalchemy import create_engine, pool
from baseline import BaselineError, preflight, ledger
config = context.config
if context.is_offline_mode():
    raise BaselineError('scribeswell_offline_prohibited')
engine = None
try:
    command = getattr(getattr(config, 'cmd_opts', None), 'cmd', None)
    if command and command[0].__name__ != 'upgrade':
        raise BaselineError('scribeswell_upgrade_only')
    # Runner supplies a validated, explicit URL; standalone entry is validated too.
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'backend'))
    from database import validate_url
    url = validate_url(os.environ['SCRIBESWELL_MIGRATION_DATABASE_URL'], 'scribeswell_migrator')
    from urllib.parse import urlsplit
    if urlsplit(url).hostname not in ('127.0.0.1','localhost','::1'):
        sys.path.insert(0,str(Path(__file__).resolve().parents[3] / 'platform/deployment'))
        from target_contract import database_url
        database_url(url,os.environ['SUPABASE_URL'],'scribeswell_migrator')
    for key in list(os.environ):
        if key.startswith('PG'):
            del os.environ[key]
    url = url.replace('postgresql://','postgresql+psycopg://',1)
    engine = create_engine(url,poolclass=pool.NullPool,hide_parameters=True,connect_args={'connect_timeout':5,'options':'-c search_path=pg_catalog -c statement_timeout=30000 -c lock_timeout=3000 -c idle_in_transaction_session_timeout=15000'})
    with engine.begin() as connection:
        context.configure(connection=connection,version_table_schema='scribeswell',version_table='alembic_version',transactional_ddl=True)
        migration_fn = context.get_context().opts.get('fn')
        if getattr(migration_fn,'__name__',None) != 'upgrade':
            raise BaselineError('scribeswell_upgrade_only')
        if context.get_context().opts.get('destination_rev') != 'head':
            raise BaselineError('scribeswell_upgrade_head_only')
        state = preflight(connection)
        config.attributes['scribeswell_before'] = state
        context.run_migrations()
        connection.exec_driver_sql('REVOKE ALL ON scribeswell.alembic_version FROM PUBLIC, anon, authenticated, service_role, scribeswell_runtime, scribeswell_import')
        preflight(connection)
        config.attributes['scribeswell_after'] = ledger(connection)
except BaselineError:
    raise
except Exception:
    raise BaselineError('scribeswell_migration_failed_requires_reconciliation') from None
finally:
    if engine is not None:
        engine.dispose()
