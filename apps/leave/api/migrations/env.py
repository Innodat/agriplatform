"""Owner Alembic seed: controlled connection required, no independent URL loading."""
from alembic import context
connection = context.config.attributes.get('connection')
if connection is None:
    raise RuntimeError('controlled_migration_connection_required')
context.configure(connection=connection, version_table_schema='leave', transactional_ddl=True)
with context.begin_transaction():
    context.run_migrations()
