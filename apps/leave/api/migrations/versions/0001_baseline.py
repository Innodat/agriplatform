"""Owner empty baseline: Alembic ledger only, no domain objects."""
revision = '0001_baseline'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    raise RuntimeError('automatic_downgrade_unsupported')
