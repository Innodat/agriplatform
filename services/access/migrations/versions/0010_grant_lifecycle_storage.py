"""Stage organization grant lifecycle storage without backfill or activation."""
from alembic import op

revision = 'access_0010'
down_revision = 'access_0009'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""ALTER TABLE access.grants
      ADD COLUMN scope_kind text NOT NULL DEFAULT 'organization',
      ADD COLUMN revision bigint NOT NULL DEFAULT 1,
      ADD COLUMN revoked_at timestamptz,
      ADD COLUMN created_actor_id uuid,
      ADD COLUMN updated_actor_id uuid,
      ADD COLUMN updated_at timestamptz,
      ADD CONSTRAINT grants_scope_kind_organization CHECK (scope_kind = 'organization'),
      ADD CONSTRAINT grants_revision_positive CHECK (revision > 0),
      ADD CONSTRAINT grants_created_actor_id_non_nil CHECK (created_actor_id <> '00000000-0000-0000-0000-000000000000'::uuid),
      ADD CONSTRAINT grants_updated_actor_id_non_nil CHECK (updated_actor_id <> '00000000-0000-0000-0000-000000000000'::uuid),
      ADD CONSTRAINT grants_revoked_at_finite CHECK (isfinite(revoked_at)),
      ADD CONSTRAINT grants_updated_at_finite CHECK (isfinite(updated_at))""")


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
