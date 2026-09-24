import os
from alembic import context
from sqlalchemy import create_engine, pool
engine = create_engine(os.environ["CONTENT_MIGRATION_DATABASE_URL"], poolclass=pool.NullPool, hide_parameters=True)
with engine.connect() as connection:
    context.configure(connection=connection, version_table_schema="content", version_table="alembic_version", include_schemas=True, include_name=lambda name, type_, parents: type_ != "schema" or name == "content")
    with context.begin_transaction():
        context.run_migrations()
