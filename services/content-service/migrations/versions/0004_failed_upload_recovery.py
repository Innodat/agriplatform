"""Retain failed finalizations while allowing a fresh identity for their expected bytes."""
from alembic import op
revision = 'content_0004'
down_revision = 'content_0003'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""ALTER TABLE content.objects DROP CONSTRAINT objects_state_check;
        ALTER TABLE content.objects ADD CONSTRAINT objects_state_check
          CHECK(state IN ('pending','finalizing','ready','failed'));
        ALTER TABLE content.objects DROP CONSTRAINT objects_org_id_sha256_key;
        CREATE UNIQUE INDEX objects_active_hash ON content.objects(org_id,sha256) WHERE state<>'failed';
        CREATE FUNCTION content.protect_failed() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
          IF OLD.state='failed' AND NEW.state<>'failed' THEN RAISE EXCEPTION 'failed_content_retained'; END IF;
          IF NEW.state='failed' AND current_user<>'content_migrator' THEN RAISE EXCEPTION 'recovery_authority_required'; END IF;
          RETURN NEW;
        END $$;
        CREATE TRIGGER protect_failed BEFORE UPDATE ON content.objects FOR EACH ROW EXECUTE FUNCTION content.protect_failed();""")


def downgrade():
    raise RuntimeError('Use the forward recovery runbook')
