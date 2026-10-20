"""Identity legacy-equivalent baseline and existing Access read bridge.

Never transfers Identity ownership into Access's migration history.
"""
from alembic import context, op
from identity_baseline import source_sql
revision = 'identity_0001'
down_revision = None
branch_labels = None
depends_on = None

# Fixed owner integration for retained CS/Expense FKs and synthetic composer seeds.
# No Identity owner role, DELETE, Auth INSERT or application-runtime authority.
LEGACY_INTEGRATION_SQL = """
GRANT USAGE ON SCHEMA identity TO postgres;
GRANT REFERENCES (id) ON identity.users, identity.org TO postgres;
GRANT SELECT (id) ON identity.users TO postgres;
GRANT UPDATE (actor_key, is_system, username, is_platform_admin, updated_at)
  ON identity.users TO postgres;
GRANT SELECT (id, slug) ON identity.org TO postgres;
GRANT INSERT (name, slug, created_by, updated_by) ON identity.org TO postgres;
GRANT SELECT (id, org_id, user_id) ON identity.org_member TO postgres;
GRANT INSERT (org_id, user_id, is_owner, created_by, updated_by)
  ON identity.org_member TO postgres;
GRANT INSERT (member_id, role, created_by, updated_by) ON identity.member_role TO postgres;
"""

def upgrade():
    state = context.config.attributes['identity_state']
    scripts = source_sql()
    if state == 'clean':
        for sql in scripts[:-1]:
            op.get_bind().exec_driver_sql(sql)
    elif state != 'adopt':
        raise RuntimeError('identity_baseline_state_invalid')
    op.get_bind().exec_driver_sql(scripts[-1])
    op.get_bind().exec_driver_sql(LEGACY_INTEGRATION_SQL)

def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
