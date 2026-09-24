"""Freeze verified byte identity and manage update attribution at the server."""
from alembic import op
revision='content_0002'
down_revision='content_0001'
branch_labels=None
depends_on=None

def upgrade():
    op.execute('''CREATE FUNCTION content.protect_identity() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
      IF NEW.org_id IS DISTINCT FROM OLD.org_id OR NEW.id IS DISTINCT FROM OLD.id OR NEW.sha256 IS DISTINCT FROM OLD.sha256 OR NEW.size IS DISTINCT FROM OLD.size OR NEW.media_type IS DISTINCT FROM OLD.media_type
      OR NEW.created_at IS DISTINCT FROM OLD.created_at OR NEW.created_by IS DISTINCT FROM OLD.created_by
      OR (OLD.state='ready' AND NEW.state<>'ready') THEN RAISE EXCEPTION 'immutable_content_identity'; END IF;
      NEW.updated_at=clock_timestamp(); NEW.updated_by=current_setting('app.actor_id'); RETURN NEW;
    END $$;
    CREATE TRIGGER immutable_identity BEFORE UPDATE ON content.objects FOR EACH ROW EXECUTE FUNCTION content.protect_identity();''')

def downgrade():raise RuntimeError('Use the recovery runbook; destructive rollback is unsupported')
