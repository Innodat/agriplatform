"""Limit ordinary authenticated profile writes to existing supported inputs."""
from alembic import op
from identity_baseline import verify_profile_privileges

revision = 'identity_0008'
down_revision = 'identity_0007'
branch_labels = None
depends_on = None

PROFILE_FIELDS_SQL = r"""
REVOKE INSERT, UPDATE ON identity.users FROM authenticated;
-- Explicitly clear per-column grants before exact supported inputs.
DO $profile_columns$
DECLARE columns text;
BEGIN
    SELECT string_agg(quote_ident(attname), ', ' ORDER BY attnum) INTO columns
      FROM pg_attribute
      WHERE attrelid = 'identity.users'::regclass AND attnum > 0 AND NOT attisdropped;
    EXECUTE format('REVOKE INSERT (%s), UPDATE (%s) ON identity.users FROM authenticated', columns, columns);
END;
$profile_columns$;
GRANT INSERT (id, username) ON identity.users TO authenticated;
GRANT UPDATE (username, deleted_at) ON identity.users TO authenticated;
"""


def upgrade():
    connection = op.get_bind()
    connection.exec_driver_sql(PROFILE_FIELDS_SQL, execution_options={'no_parameters': True})
    # PUBLIC/inherited privileges survive direct REVOKE. Refuse rather than
    # changing an unlisted principal or activating an ineffective restriction.
    verify_profile_privileges(connection)


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
