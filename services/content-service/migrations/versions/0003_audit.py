"""Safe immutable operation evidence."""
from alembic import op
revision='content_0003'
down_revision='content_0002'
branch_labels=None
depends_on=None

def upgrade():
    op.execute('''CREATE TABLE content.events(
      org_id uuid NOT NULL, id uuid NOT NULL, content_id text NOT NULL, operation text NOT NULL,
      created_at timestamptz NOT NULL DEFAULT clock_timestamp(), created_by text NOT NULL DEFAULT current_setting('app.actor_id'),
      PRIMARY KEY(org_id,id), FOREIGN KEY(org_id,content_id) REFERENCES content.objects(org_id,id));
      ALTER TABLE content.events ENABLE ROW LEVEL SECURITY; ALTER TABLE content.events FORCE ROW LEVEL SECURITY;
      CREATE POLICY org_scope ON content.events USING(org_id::text=current_setting('app.org_id',true)) WITH CHECK(org_id::text=current_setting('app.org_id',true));
      GRANT INSERT ON content.events TO content_runtime;''')

def downgrade():raise RuntimeError('Use recovery runbook')
