"""Controlled Identity-only route; guarded before Alembic can create/stamp history."""
import os
from alembic import context
from sqlalchemy import create_engine, pool
from identity_baseline import BaselineError, preflight, verify_owned_postcondition

config = context.config
if context.is_offline_mode():
    raise BaselineError('identity_offline_migrations_prohibited')
command = getattr(getattr(config, 'cmd_opts', None), 'cmd', None)
if command and command[0].__name__ != 'upgrade':
    raise BaselineError('identity_use_verified_upgrade_route')
url = os.environ.get('IDENTITY_MIGRATION_DATABASE_URL')
if not url:
    raise BaselineError('identity_missing_migration_configuration')
engine = create_engine(url, poolclass=pool.NullPool, hide_parameters=True,
                       connect_args={'connect_timeout': 5})
try:
    with engine.begin() as connection:
        connection.exec_driver_sql("SET LOCAL lock_timeout='5s'")
        connection.exec_driver_sql("SET LOCAL statement_timeout='60s'")
        context.configure(connection=connection, version_table_schema='identity',
                          version_table='alembic_version', transactional_ddl=True)
        # Also guard Python Alembic command.stamp/ensure_version paths, where
        # config.cmd_opts is absent. Configuration itself performs no DDL.
        migration_fn = context.get_context().opts.get('fn')
        if getattr(migration_fn, '__name__', None) != 'upgrade':
            raise BaselineError('identity_use_verified_upgrade_route')
        state = preflight(connection, os.environ.get('IDENTITY_MIGRATION_MODE', 'clean'))
        config.attributes['identity_state'] = state
        context.run_migrations()
        # Legacy broad table defaults apply on adoption; the owner ledger must
        # never inherit business-role write privileges.
        connection.exec_driver_sql("REVOKE ALL ON identity.alembic_version FROM PUBLIC, anon, authenticated, service_role, supabase_auth_admin, access_runtime")
        verify_owned_postcondition(connection)
except BaselineError:
    raise
except Exception:
    # DBAPI/Alembic exception strings can contain SQL, credentials or business values.
    raise BaselineError('identity_migration_failed_requires_reconciliation') from None
finally:
    engine.dispose()
