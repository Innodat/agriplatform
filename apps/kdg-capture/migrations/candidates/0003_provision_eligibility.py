"""Controlled candidate: least-privilege own provisioning eligibility issuance.

Linked to the storage candidate; never discovered by active versions or API startup.
Existing server DEFAULT owns issued_at; runtime cannot INSERT that column. Existing
immutable triggers, SELECT policies and previous capture consumers remain unchanged.
"""
from alembic import op

revision = '0003_kdg_provision_eligibility'
down_revision = '0002_kdg_capture_storage'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''GRANT INSERT (org_id,ref,account_id,membership_id,child_id,child_revision,
observed_active,create_permission,assignment_id,assignment_revision,issued_by)
ON kdg_capture.child_eligibility TO kdg_capture_runtime''')
    op.execute('''CREATE POLICY runtime_issue ON kdg_capture.child_eligibility
FOR INSERT TO kdg_capture_runtime WITH CHECK (
 current_setting('app.mode', true) = 'own_write'
 AND org_id = current_setting('app.org_id', true)::uuid
 AND account_id = current_setting('app.account_id', true)::uuid
 AND issued_by = current_setting('app.actor_id', true)::uuid
 AND membership_id = nullif(current_setting('app.provision_membership_id', true), '')::bigint
 AND create_permission = current_setting('app.provision_create_permission', true)
)''')


def downgrade():
    raise RuntimeError('kdg_migration_downgrade_prohibited')
