"""Bridge registered organization grants while preserving three legacy PtS values."""
from alembic import op

revision = 'access_0011'
down_revision = 'access_0010'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""ALTER TABLE access.grants
      ADD COLUMN registry_permission text GENERATED ALWAYS AS (
        CASE WHEN permission = ANY (ARRAY['pts.poetry.read', 'pts.poetry.export', 'pts.poetry.documents'])
          THEN NULL::text ELSE permission END) STORED,
      DROP CONSTRAINT grants_permission_check,
      ADD CONSTRAINT grants_registry_permission_scope_fkey
        FOREIGN KEY (registry_permission, scope_kind)
        REFERENCES access.permissions(permission, scope_kind) ON DELETE RESTRICT,
      ADD CONSTRAINT grants_nonlegacy_active_fields CHECK (
        registry_permission IS NULL OR revoked_at IS NOT NULL OR (
          membership_id IS NOT NULL AND created_actor_id IS NOT NULL
          AND updated_actor_id IS NOT NULL AND updated_at IS NOT NULL))""")


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
