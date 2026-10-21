"""Private account-free selected organization verification for staged Access setup."""
from alembic import op

revision = 'identity_0019'
down_revision = 'identity_0018'
branch_labels = None
depends_on = None

ORGANIZATION_TARGET_SQL = r"""
CREATE FUNCTION identity.organization_target(p_org uuid)
RETURNS TABLE (org_id uuid)
LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = pg_catalog, pg_temp
AS $organization_target$
DECLARE selected_org text := current_setting('app.org_id', true);
BEGIN
    -- Trusted backend assertions; Access must check current exact authority first.
    IF current_setting('app.context_kind', true) IS DISTINCT FROM 'setup'
       OR nullif(current_setting('app.account_id', true), '') IS NOT NULL
       OR (current_setting('app.actor_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
           AND current_setting('app.actor_id', true) <> '00000000-0000-0000-0000-000000000000') IS NOT TRUE
       OR (selected_org ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
           AND selected_org <> '00000000-0000-0000-0000-000000000000') IS NOT TRUE
       OR p_org IS NULL OR p_org = '00000000-0000-0000-0000-000000000000'::uuid THEN
        RETURN;
    END IF;
    IF p_org <> selected_org::uuid THEN RETURN; END IF;
    RETURN QUERY SELECT organization.id FROM identity.org AS organization
        WHERE organization.id = p_org AND organization.deleted_at IS NULL;
END;
$organization_target$;
-- Strip inherited/default routine grants atomically; do not change default ACLs.
DO $organization_target_acl$
DECLARE routine record; granted_role record; grantee_name text;
BEGIN
    SELECT p.oid, p.proowner, p.proacl, p.oid::regprocedure AS signature INTO STRICT routine
      FROM pg_proc p WHERE p.oid='identity.organization_target(uuid)'::regprocedure;
    EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC', routine.signature);
    FOR granted_role IN SELECT DISTINCT a.grantee FROM aclexplode(routine.proacl) a WHERE a.grantee <> routine.proowner
    LOOP
        grantee_name := CASE WHEN granted_role.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(granted_role.grantee)) END;
        EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s', routine.signature, grantee_name);
    END LOOP;
END;
$organization_target_acl$;
GRANT EXECUTE ON FUNCTION identity.organization_target(uuid) TO access_command_owner;
GRANT CREATE ON SCHEMA identity TO identity_target_projection_owner;
ALTER FUNCTION identity.organization_target(uuid) OWNER TO identity_target_projection_owner;
REVOKE CREATE ON SCHEMA identity FROM identity_target_projection_owner;
"""


def upgrade():
    op.get_bind().exec_driver_sql(ORGANIZATION_TARGET_SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
