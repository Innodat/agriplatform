"""Bind the compatibility RPC to the token's exact currently active membership."""
from alembic import op

revision = 'identity_0009'
down_revision = 'identity_0008'
branch_labels = None
depends_on = None

LEGACY_ROLES_SQL = r"""
CREATE OR REPLACE FUNCTION public.get_user_roles()
RETURNS TABLE (role text)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, pg_temp
AS $legacy_roles$
DECLARE
  token_account_id uuid := CASE WHEN nullif(auth.jwt() ->> 'sub', '') IS NULL THEN NULL ELSE auth.uid() END;
  token_org_id uuid := nullif(auth.jwt() ->> 'org_id', '')::uuid;
  token_member_id bigint := nullif(auth.jwt() ->> 'member_id', '')::bigint;
BEGIN
  IF token_account_id IS NULL OR token_account_id = '00000000-0000-0000-0000-000000000000'::uuid
     OR token_org_id IS NULL OR token_org_id = '00000000-0000-0000-0000-000000000000'::uuid
     OR token_member_id IS NULL OR token_member_id <= 0 THEN
    RETURN;
  END IF;
  RETURN QUERY
  SELECT mr.role::text
  FROM identity.member_role AS mr
  JOIN identity.org_member AS m ON m.id = mr.member_id
  JOIN identity.users AS u ON u.id = m.user_id
  JOIN identity.org AS o ON o.id = m.org_id
  WHERE m.id = token_member_id
    AND m.user_id = token_account_id
    AND m.org_id = token_org_id
    AND u.deleted_at IS NULL
    AND o.deleted_at IS NULL
    AND m.deleted_at IS NULL
    AND mr.deleted_at IS NULL;
END;
$legacy_roles$;
"""


def upgrade():
    # CREATE OR REPLACE preserves the existing owner, ACL and function identity.
    op.get_bind().exec_driver_sql(LEGACY_ROLES_SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
