"""Immutable, scoped Leave selection evidence; no active organization preference."""
from alembic import op
revision='0002_selection'
down_revision='0001_baseline'
branch_labels=None
depends_on=None

def upgrade():
    op.execute('''
    CREATE TABLE leave.organization_selection (
      event_id uuid PRIMARY KEY CHECK(event_id <> '00000000-0000-0000-0000-000000000000'),
      event_type text NOT NULL DEFAULT 'leave.organization_context_selected' CHECK(event_type='leave.organization_context_selected'),
      event_version integer NOT NULL DEFAULT 1 CHECK(event_version=1),
      org_id uuid NOT NULL CHECK(org_id <> '00000000-0000-0000-0000-000000000000'),
      account_id uuid NOT NULL CHECK(account_id <> '00000000-0000-0000-0000-000000000000'),
      actor_id uuid NOT NULL CHECK(actor_id <> '00000000-0000-0000-0000-000000000000'),
      membership_id bigint NOT NULL CHECK(membership_id>0),
      operation_id uuid NOT NULL CHECK(operation_id <> '00000000-0000-0000-0000-000000000000'),
      decision_id uuid NOT NULL CHECK(decision_id <> '00000000-0000-0000-0000-000000000000'),
      checked_at timestamptz NOT NULL,
      created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
      UNIQUE(org_id,actor_id,operation_id)
    );
    CREATE FUNCTION leave.stamp_selection() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      NEW.org_id := nullif(current_setting('app.org_id',true),'')::uuid;
      NEW.account_id := nullif(current_setting('app.account_id',true),'')::uuid;
      NEW.actor_id := nullif(current_setting('app.actor_id',true),'')::uuid;
      NEW.created_at := statement_timestamp();
      RETURN NEW;
    END $$;
    REVOKE ALL ON FUNCTION leave.stamp_selection() FROM PUBLIC;
    CREATE TRIGGER stamp_selection BEFORE INSERT ON leave.organization_selection FOR EACH ROW EXECUTE FUNCTION leave.stamp_selection();
    ALTER TABLE leave.organization_selection ENABLE ROW LEVEL SECURITY;
    ALTER TABLE leave.organization_selection FORCE ROW LEVEL SECURITY;
    CREATE POLICY selection_read ON leave.organization_selection FOR SELECT TO leave_runtime USING(
      org_id=nullif(current_setting('app.org_id',true),'')::uuid AND
      account_id=nullif(current_setting('app.account_id',true),'')::uuid AND
      actor_id=nullif(current_setting('app.actor_id',true),'')::uuid AND current_setting('app.mode',true)='all_write');
    CREATE POLICY selection_insert ON leave.organization_selection FOR INSERT TO leave_runtime WITH CHECK(
      org_id=nullif(current_setting('app.org_id',true),'')::uuid AND
      account_id=nullif(current_setting('app.account_id',true),'')::uuid AND
      actor_id=nullif(current_setting('app.actor_id',true),'')::uuid AND current_setting('app.mode',true)='all_write');
    GRANT SELECT,INSERT ON leave.organization_selection TO leave_runtime;
    ''')

def downgrade():raise RuntimeError('forward_recovery_required')
