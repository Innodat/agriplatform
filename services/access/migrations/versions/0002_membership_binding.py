"""Stage an exact external membership identifier; no backfill or activation."""
from alembic import op

revision = 'access_0002'
down_revision = 'access_0001'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE access.grants ADD COLUMN membership_id bigint, ADD CONSTRAINT grants_membership_id_positive CHECK (membership_id > 0)')


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
