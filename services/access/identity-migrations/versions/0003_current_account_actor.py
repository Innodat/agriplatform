"""Restricted current verified account projection; no provisioning or admission."""
from alembic import op
from sqlalchemy import text
from identity_baseline import verify_projection_role, verify_projection_prerequisites

revision = 'identity_0003'
down_revision = 'identity_0002'
branch_labels = None
depends_on = None

PROJECTION_SCHEMA_SQL = r"""
GRANT USAGE ON SCHEMA identity TO identity_account_projection_owner;
-- Legacy PUBLIC profile policy invokes auth.role(); schema usage permits that
-- fixed helper without granting any Auth table or schema-creation authority.
GRANT USAGE ON SCHEMA auth TO identity_account_projection_owner;
GRANT SELECT (id, deleted_at) ON identity.users TO identity_account_projection_owner;
GRANT SELECT (account_id, actor_id, actor_kind) ON identity.account_actor TO identity_account_projection_owner;
GRANT SELECT (id, kind, display_name) ON identity.actor TO identity_account_projection_owner;
CREATE POLICY account_projection_read ON identity.users
FOR SELECT TO identity_account_projection_owner
USING (current_setting('app.context_kind', true) = 'user'
       AND id::text = lower(current_setting('app.account_id', true))
       AND deleted_at IS NULL);
-- Restrictive policy keeps legacy PUBLIC policies from broadening this reader.
CREATE POLICY account_projection_bound ON identity.users AS RESTRICTIVE
FOR SELECT TO identity_account_projection_owner
USING (current_setting('app.context_kind', true) = 'user'
       AND id::text = lower(current_setting('app.account_id', true))
       AND deleted_at IS NULL);
CREATE FUNCTION identity.current_account_actor()
RETURNS TABLE (account_id uuid, actor_id uuid, display_name text)
LANGUAGE plpgsql STABLE SECURITY DEFINER
SET search_path = pg_catalog, pg_temp
AS $account_projection$
DECLARE verified_account uuid; asserted_account text;
BEGIN
    IF current_setting('app.context_kind', true) IS DISTINCT FROM 'user' THEN
        RETURN;
    END IF;
    asserted_account := current_setting('app.account_id', true);
    IF asserted_account IS NULL OR asserted_account !~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' THEN
        RETURN;
    END IF;
    verified_account := asserted_account::uuid;
    IF verified_account = '00000000-0000-0000-0000-000000000000'::uuid THEN
        RETURN;
    END IF;
    RETURN QUERY
        SELECT profile.id, actor.id, actor.display_name
        FROM identity.users AS profile
        LEFT JOIN identity.account_actor AS mapping
          ON mapping.account_id = profile.id AND mapping.actor_kind = 'account'
        LEFT JOIN identity.actor AS actor
          ON actor.id = mapping.actor_id AND actor.kind = mapping.actor_kind
        WHERE profile.id = verified_account AND profile.deleted_at IS NULL;
END;
$account_projection$;
-- Remove every inherited default ACL, including unknown grantees.
DO $projection_acl$
DECLARE granted_role record; grantee_name text;
BEGIN
    REVOKE ALL ON FUNCTION identity.current_account_actor() FROM PUBLIC;
    FOR granted_role IN
        SELECT DISTINCT a.grantee FROM pg_proc p
        JOIN pg_namespace n ON n.oid = p.pronamespace
        CROSS JOIN LATERAL aclexplode(p.proacl) a
        WHERE n.nspname = 'identity' AND p.proname = 'current_account_actor'
          AND a.grantee <> p.proowner
    LOOP
        grantee_name := CASE WHEN granted_role.grantee = 0 THEN 'PUBLIC'
            ELSE quote_ident(pg_get_userbyid(granted_role.grantee)) END;
        EXECUTE format('REVOKE ALL ON FUNCTION identity.current_account_actor() FROM %s', grantee_name);
    END LOOP;
END;
$projection_acl$;
-- Grant while the migrator still owns the routine; SET-only membership does
-- not let it grant privileges after ownership transfer. The ACL survives transfer.
GRANT EXECUTE ON FUNCTION identity.current_account_actor() TO access_runtime;
-- Ownership transfer needs CREATE only inside this controlled transaction.
GRANT CREATE ON SCHEMA identity TO identity_account_projection_owner;
ALTER FUNCTION identity.current_account_actor() OWNER TO identity_account_projection_owner;
REVOKE CREATE ON SCHEMA identity FROM identity_account_projection_owner;
"""


def upgrade():
    connection = op.get_bind()
    verify_projection_prerequisites(connection)
    verify_projection_role(connection, staged=True)
    connection.execute(text(PROJECTION_SCHEMA_SQL))


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
