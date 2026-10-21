"""Private organization admission storage; no verification or execution authority."""
from alembic import op

revision = 'access_0008'
down_revision = 'access_0007'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE TABLE access.organization_applications (
 org_id uuid NOT NULL,
 app_id text NOT NULL,
 enabled boolean NOT NULL DEFAULT false,
 revision bigint NOT NULL DEFAULT 1,
 created_by uuid NOT NULL,
 updated_by uuid NOT NULL,
 created_at timestamptz NOT NULL,
 updated_at timestamptz NOT NULL,
 CONSTRAINT organization_applications_pkey PRIMARY KEY (org_id, app_id),
 CONSTRAINT organization_applications_app_id_fkey FOREIGN KEY (app_id) REFERENCES access.applications(app_id) ON DELETE RESTRICT,
 CONSTRAINT organization_applications_org_id_non_nil CHECK (org_id <> '00000000-0000-0000-0000-000000000000'::uuid),
 CONSTRAINT organization_applications_revision_positive CHECK (revision > 0),
 CONSTRAINT organization_applications_created_by_non_nil CHECK (created_by <> '00000000-0000-0000-0000-000000000000'::uuid),
 CONSTRAINT organization_applications_updated_by_non_nil CHECK (updated_by <> '00000000-0000-0000-0000-000000000000'::uuid),
 CONSTRAINT organization_applications_created_at_finite CHECK (isfinite(created_at)),
 CONSTRAINT organization_applications_updated_at_finite CHECK (isfinite(updated_at))
);
ALTER TABLE access.organization_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE access.organization_applications FORCE ROW LEVEL SECURITY;
CREATE POLICY org_scope ON access.organization_applications TO access_migrator
 USING (org_id::text = current_setting('app.org_id', true))
 WITH CHECK (org_id::text = current_setting('app.org_id', true));
CREATE TRIGGER registry_storage_immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON access.organization_applications FOR EACH STATEMENT EXECUTE FUNCTION access.registry_storage_immutable();
REVOKE ALL ON access.organization_applications FROM PUBLIC;
""")


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
