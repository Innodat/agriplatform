"""Initialize only the private KDG Alembic ledger in a separately prepared schema.

No domain objects, users, actors, grants, roles or databases are created here.
"""
revision='0001_kdg_foundation'
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    # Alembic creates/stamps its owner-local version table in the guarded transaction.
    pass

def downgrade():
    raise RuntimeError('kdg_migration_downgrade_prohibited')
