"""Initial owned schema. Bootstrap roles/schema separately; no legacy cutover."""
from alembic import op
revision = "access_0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE TABLE access.grants (\n org_id uuid NOT NULL, id text NOT NULL, user_id uuid NOT NULL, permission text NOT NULL CHECK(permission IN ('pts.poetry.read','pts.poetry.export','pts.poetry.documents')), UNIQUE(org_id,user_id,permission),\n created_at timestamptz NOT NULL DEFAULT clock_timestamp(),\n created_by text NOT NULL DEFAULT current_setting('app.actor_id'),\n PRIMARY KEY (org_id,id));\n ALTER TABLE access.grants ENABLE ROW LEVEL SECURITY;\n ALTER TABLE access.grants FORCE ROW LEVEL SECURITY;\n CREATE POLICY org_scope ON access.grants USING (org_id::text = current_setting('app.org_id',true)) WITH CHECK (org_id::text = current_setting('app.org_id',true));\nGRANT SELECT ON access.grants TO access_runtime;")

def downgrade():
    raise RuntimeError("Destructive rollback is not supported; use the recovery runbook")
