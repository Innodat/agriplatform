import os
from alembic import context
from sqlalchemy import create_engine, pool, text
engine = create_engine(os.environ["PTS_MIGRATION_DATABASE_URL"], poolclass=pool.NullPool, hide_parameters=True)
with engine.begin() as connection:
    if connection.execute(text('SELECT current_user')).scalar_one()!='pts_migrator':raise RuntimeError('pts_migration_authority_invalid')
    for setting in ("SET LOCAL lock_timeout='5s'","SET LOCAL statement_timeout='60s'","SET LOCAL idle_in_transaction_session_timeout='10s'"):
        connection.execute(text(setting))
    connection.execute(text("SELECT pg_advisory_xact_lock(hashtextextended('pts:migrations',0))"))
    context.configure(connection=connection, version_table_schema="pts", version_table="alembic_version", include_schemas=True, include_name=lambda name, type_, parents: type_ != "schema" or name == "pts")
    with context.begin_transaction():
        context.run_migrations()
