"""Controlled opt-in candidate only; never imported by API or registered for release."""
import os
from alembic import context
from sqlalchemy import create_engine,pool,text
from policy import POLICY,MigrationError,connection_url,guard_command
from owned_migration import migration_transaction
config=context.config
engine=None
try:
    if context.is_offline_mode():guard_command(None,None,offline=True)
    command=getattr(getattr(config,'cmd_opts',None),'cmd',None)
    if command and getattr(command[0],'__name__',None)!='upgrade':guard_command(None,None)
    url=connection_url(os.environ)
    engine=create_engine(url,poolclass=pool.NullPool,hide_parameters=True,
        connect_args={'connect_timeout':5,'hostaddr':'127.0.0.1','sslmode':'disable','gssencmode':'disable','passfile':'/dev/null','options':'-c search_path=pg_catalog -c statement_timeout=30000 -c lock_timeout=3000 -c idle_in_transaction_session_timeout=10000'})
    with migration_transaction(engine,POLICY) as connection:
        context.configure(connection=connection,version_table_schema=POLICY.schema,
            version_table='alembic_version',transactional_ddl=True,
            include_schemas=True,include_name=lambda name,kind,parent:kind!='schema' or name==POLICY.schema)
        options=context.get_context().opts
        guard_command(getattr(options.get('fn'),'__name__',None),options.get('destination_rev'))
        context.run_migrations()
        connection.execute(text('REVOKE ALL ON kdg_capture.alembic_version FROM PUBLIC,kdg_capture_runtime,kdg_capture_operator'))
except MigrationError:raise
except Exception:
    raise MigrationError('kdg_migration_failed_requires_reconciliation') from None
finally:
    if engine is not None:
        try:engine.dispose()
        except Exception:raise MigrationError('kdg_migration_disposal_failed_requires_reconciliation') from None
