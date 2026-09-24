"""Initial owned schema. Bootstrap roles/schema separately; no legacy cutover."""
from alembic import op
revision = "content_0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE TABLE content.objects (\n org_id uuid NOT NULL, id text NOT NULL, sha256 text NOT NULL CHECK(sha256 ~ '^[a-f0-9]{64}$'), size bigint NOT NULL CHECK(size > 0 AND size <= 134217728), media_type text NOT NULL, state text NOT NULL DEFAULT 'pending' CHECK(state IN ('pending','finalizing','ready')), updated_at timestamptz NOT NULL DEFAULT clock_timestamp(), updated_by text NOT NULL DEFAULT current_setting('app.actor_id'), lease_until timestamptz, UNIQUE(org_id,sha256),\n created_at timestamptz NOT NULL DEFAULT clock_timestamp(),\n created_by text NOT NULL DEFAULT current_setting('app.actor_id'),\n PRIMARY KEY (org_id,id));\n ALTER TABLE content.objects ENABLE ROW LEVEL SECURITY;\n ALTER TABLE content.objects FORCE ROW LEVEL SECURITY;\n CREATE POLICY org_scope ON content.objects USING (org_id::text = current_setting('app.org_id',true)) WITH CHECK (org_id::text = current_setting('app.org_id',true));\nGRANT SELECT,INSERT,UPDATE ON content.objects TO content_runtime;")

def downgrade():
    raise RuntimeError("Destructive rollback is not supported; use the recovery runbook")
