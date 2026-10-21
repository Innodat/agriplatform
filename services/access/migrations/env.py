"""Controlled Access owner route; no stamp, downgrade, adoption or startup runner."""
import os
from alembic import context
from sqlalchemy import create_engine, pool
from access_baseline import BaselineError, preflight, verify_postcondition

config = context.config
if context.is_offline_mode():
    raise BaselineError('access_offline_migrations_prohibited')
command = getattr(getattr(config, 'cmd_opts', None), 'cmd', None)
if command and command[0].__name__ != 'upgrade':
    raise BaselineError('access_use_verified_upgrade_route')
url = os.environ.get('ACCESS_MIGRATION_DATABASE_URL')
if not url:
    raise BaselineError('access_missing_migration_configuration')
engine = None
try:
    engine = create_engine(url, poolclass=pool.NullPool, hide_parameters=True,
                           connect_args={'connect_timeout': 5})
    with engine.begin() as connection:
        connection.exec_driver_sql('SET LOCAL search_path=pg_catalog,pg_temp')
        connection.exec_driver_sql("SET LOCAL lock_timeout='3s'")
        connection.exec_driver_sql("SET LOCAL statement_timeout='30s'")
        connection.exec_driver_sql("SET LOCAL idle_in_transaction_session_timeout='10s'")
        if connection.dialect.server_version_info >= (17,):
            connection.exec_driver_sql("SET LOCAL transaction_timeout='60s'")
        context.configure(connection=connection, version_table_schema='access',
                          version_table='alembic_version', transactional_ddl=True)
        if getattr(context.get_context().opts.get('fn'), '__name__', None) != 'upgrade':
            raise BaselineError('access_use_verified_upgrade_route')
        preflight(connection)
        context.run_migrations()
        verify_postcondition(connection)
except BaselineError:
    raise
except Exception:
    # Never render DBAPI/Alembic payload, URL, SQL or business-value strings.
    raise BaselineError('access_migration_failed_requires_reconciliation') from None
finally:
    if engine is not None:
        engine.dispose()
