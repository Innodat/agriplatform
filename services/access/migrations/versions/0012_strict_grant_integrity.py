"""Require registered organization permissions and complete active grant provenance."""
from alembic import op

revision = 'access_0012'
down_revision = 'access_0011'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""ALTER TABLE access.grants
      DROP CONSTRAINT grants_registry_permission_scope_fkey,
      DROP CONSTRAINT grants_nonlegacy_active_fields,
      DROP COLUMN registry_permission,
      ADD CONSTRAINT grants_permission_scope_fkey
        FOREIGN KEY (permission, scope_kind)
        REFERENCES access.permissions(permission, scope_kind) ON DELETE RESTRICT,
      ADD CONSTRAINT grants_active_fields CHECK (
        revoked_at IS NOT NULL OR (
          membership_id IS NOT NULL AND created_actor_id IS NOT NULL
          AND updated_actor_id IS NOT NULL AND updated_at IS NOT NULL))""")


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
