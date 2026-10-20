"""Stage active membership uniqueness while preserving legacy full uniqueness."""
from alembic import op

revision = 'identity_0014'
down_revision = 'identity_0013'
branch_labels = None
depends_on = None

ACTIVE_MEMBERSHIP_INDEX_SQL = r"""
CREATE UNIQUE INDEX org_member_active_org_user_uidx ON identity.org_member USING btree (org_id, user_id) WHERE deleted_at IS NULL;
"""


def upgrade():
    op.get_bind().exec_driver_sql(ACTIVE_MEMBERSHIP_INDEX_SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
