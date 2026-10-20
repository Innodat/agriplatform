"""Restricted selected-organization targets; Access owns caller authorization."""
from alembic import op
from identity_baseline import verify_target_roles, verify_projection_prerequisites

revision = 'identity_0007'
down_revision = 'identity_0006'
branch_labels = None
depends_on = None

TARGET_SCHEMA_SQL = r"""
GRANT USAGE ON SCHEMA identity TO identity_target_projection_owner, access_target_reader, access_setup_target_reader, access_command_owner;
GRANT USAGE ON SCHEMA auth TO identity_target_projection_owner;
GRANT SELECT (id, deleted_at) ON identity.users TO identity_target_projection_owner;
GRANT SELECT (id, deleted_at) ON identity.org TO identity_target_projection_owner;
GRANT SELECT (id, org_id, user_id, deleted_at, revision) ON identity.org_member TO identity_target_projection_owner;
GRANT SELECT (account_id, actor_id, actor_kind) ON identity.account_actor TO identity_target_projection_owner;
GRANT SELECT (id, kind, display_name) ON identity.actor TO identity_target_projection_owner;
CREATE POLICY target_organization_read ON identity.org
FOR SELECT TO identity_target_projection_owner USING ((current_setting('app.actor_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.actor_id', true) <> '00000000-0000-0000-0000-000000000000' AND current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.org_id', true) <> '00000000-0000-0000-0000-000000000000'
        AND ((current_setting('app.context_kind', true) = 'user' AND current_setting('app.account_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.account_id', true) <> '00000000-0000-0000-0000-000000000000')
          OR (current_setting('app.context_kind', true) = 'setup'
              AND nullif(current_setting('app.account_id', true), '') IS NULL))) AND id = (CASE WHEN current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' THEN current_setting('app.org_id', true)::uuid ELSE NULL::uuid END) AND deleted_at IS NULL);
CREATE POLICY target_organization_bound ON identity.org AS RESTRICTIVE
FOR SELECT TO identity_target_projection_owner USING ((current_setting('app.actor_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.actor_id', true) <> '00000000-0000-0000-0000-000000000000' AND current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.org_id', true) <> '00000000-0000-0000-0000-000000000000'
        AND ((current_setting('app.context_kind', true) = 'user' AND current_setting('app.account_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.account_id', true) <> '00000000-0000-0000-0000-000000000000')
          OR (current_setting('app.context_kind', true) = 'setup'
              AND nullif(current_setting('app.account_id', true), '') IS NULL))) AND id = (CASE WHEN current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' THEN current_setting('app.org_id', true)::uuid ELSE NULL::uuid END) AND deleted_at IS NULL);
CREATE POLICY target_membership_read ON identity.org_member
FOR SELECT TO identity_target_projection_owner USING ((current_setting('app.actor_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.actor_id', true) <> '00000000-0000-0000-0000-000000000000' AND current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.org_id', true) <> '00000000-0000-0000-0000-000000000000'
        AND ((current_setting('app.context_kind', true) = 'user' AND current_setting('app.account_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.account_id', true) <> '00000000-0000-0000-0000-000000000000')
          OR (current_setting('app.context_kind', true) = 'setup'
              AND nullif(current_setting('app.account_id', true), '') IS NULL))) AND org_id = (CASE WHEN current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' THEN current_setting('app.org_id', true)::uuid ELSE NULL::uuid END) AND deleted_at IS NULL);
CREATE POLICY target_membership_bound ON identity.org_member AS RESTRICTIVE
FOR SELECT TO identity_target_projection_owner USING ((current_setting('app.actor_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.actor_id', true) <> '00000000-0000-0000-0000-000000000000' AND current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.org_id', true) <> '00000000-0000-0000-0000-000000000000'
        AND ((current_setting('app.context_kind', true) = 'user' AND current_setting('app.account_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.account_id', true) <> '00000000-0000-0000-0000-000000000000')
          OR (current_setting('app.context_kind', true) = 'setup'
              AND nullif(current_setting('app.account_id', true), '') IS NULL))) AND org_id = (CASE WHEN current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' THEN current_setting('app.org_id', true)::uuid ELSE NULL::uuid END) AND deleted_at IS NULL);
CREATE POLICY target_profile_read ON identity.users
FOR SELECT TO identity_target_projection_owner USING ((current_setting('app.actor_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.actor_id', true) <> '00000000-0000-0000-0000-000000000000' AND current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.org_id', true) <> '00000000-0000-0000-0000-000000000000'
        AND ((current_setting('app.context_kind', true) = 'user' AND current_setting('app.account_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.account_id', true) <> '00000000-0000-0000-0000-000000000000')
          OR (current_setting('app.context_kind', true) = 'setup'
              AND nullif(current_setting('app.account_id', true), '') IS NULL))) AND deleted_at IS NULL AND EXISTS (SELECT 1 FROM identity.org_member AS scoped_member WHERE scoped_member.user_id = users.id AND scoped_member.org_id = (CASE WHEN current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' THEN current_setting('app.org_id', true)::uuid ELSE NULL::uuid END) AND scoped_member.deleted_at IS NULL));
CREATE POLICY target_profile_bound ON identity.users AS RESTRICTIVE
FOR SELECT TO identity_target_projection_owner USING ((current_setting('app.actor_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.actor_id', true) <> '00000000-0000-0000-0000-000000000000' AND current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.org_id', true) <> '00000000-0000-0000-0000-000000000000'
        AND ((current_setting('app.context_kind', true) = 'user' AND current_setting('app.account_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.account_id', true) <> '00000000-0000-0000-0000-000000000000')
          OR (current_setting('app.context_kind', true) = 'setup'
              AND nullif(current_setting('app.account_id', true), '') IS NULL))) AND deleted_at IS NULL AND EXISTS (SELECT 1 FROM identity.org_member AS scoped_member WHERE scoped_member.user_id = users.id AND scoped_member.org_id = (CASE WHEN current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' THEN current_setting('app.org_id', true)::uuid ELSE NULL::uuid END) AND scoped_member.deleted_at IS NULL));
CREATE FUNCTION identity.organization_account_candidates(after_account_id uuid)
RETURNS TABLE (account_id uuid, membership_id bigint, membership_revision bigint, actor_id uuid, display_name text)
LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = pg_catalog, pg_temp
AS $target_projection$
BEGIN
    -- Assertions are trusted Access backend context, not authorization decisions.
    IF ((current_setting('app.actor_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.actor_id', true) <> '00000000-0000-0000-0000-000000000000' AND current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.org_id', true) <> '00000000-0000-0000-0000-000000000000'
        AND ((current_setting('app.context_kind', true) = 'user' AND current_setting('app.account_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.account_id', true) <> '00000000-0000-0000-0000-000000000000')
          OR (current_setting('app.context_kind', true) = 'setup'
              AND nullif(current_setting('app.account_id', true), '') IS NULL)))) IS NOT TRUE THEN RETURN; END IF;
    IF current_setting('app.context_kind', true) IS DISTINCT FROM 'user' THEN RETURN; END IF;
    IF after_account_id = '00000000-0000-0000-0000-000000000000'::uuid THEN RETURN; END IF;
    RETURN QUERY
        SELECT profile.id, member.id, member.revision, actor.id, actor.display_name
        FROM identity.users AS profile
        JOIN identity.org_member AS member ON member.user_id = profile.id
        JOIN identity.org AS organization ON organization.id = member.org_id
        JOIN identity.account_actor AS mapping ON mapping.account_id = profile.id AND mapping.actor_kind = 'account'
        JOIN identity.actor AS actor ON actor.id = mapping.actor_id AND actor.kind = mapping.actor_kind
        WHERE organization.id = (CASE WHEN current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' THEN current_setting('app.org_id', true)::uuid ELSE NULL::uuid END)
          AND profile.deleted_at IS NULL AND organization.deleted_at IS NULL AND member.deleted_at IS NULL
          AND (after_account_id IS NULL OR profile.id > after_account_id)
        ORDER BY profile.id;
END;
$target_projection$;
CREATE FUNCTION identity.organization_account_target(target_account_id uuid, expected_membership_id bigint)
RETURNS TABLE (account_id uuid, membership_id bigint, membership_revision bigint, actor_id uuid, display_name text)
LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = pg_catalog, pg_temp
AS $target_projection$
BEGIN
    -- Assertions are trusted Access backend context, not authorization decisions.
    IF ((current_setting('app.actor_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.actor_id', true) <> '00000000-0000-0000-0000-000000000000' AND current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.org_id', true) <> '00000000-0000-0000-0000-000000000000'
        AND ((current_setting('app.context_kind', true) = 'user' AND current_setting('app.account_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        AND current_setting('app.account_id', true) <> '00000000-0000-0000-0000-000000000000')
          OR (current_setting('app.context_kind', true) = 'setup'
              AND nullif(current_setting('app.account_id', true), '') IS NULL)))) IS NOT TRUE THEN RETURN; END IF;
    IF target_account_id IS NULL OR target_account_id = '00000000-0000-0000-0000-000000000000'::uuid
       OR expected_membership_id IS NULL OR expected_membership_id <= 0 THEN RETURN; END IF;
    RETURN QUERY
        SELECT profile.id, member.id, member.revision, actor.id, actor.display_name
        FROM identity.users AS profile
        JOIN identity.org_member AS member ON member.user_id = profile.id
        JOIN identity.org AS organization ON organization.id = member.org_id
        JOIN identity.account_actor AS mapping ON mapping.account_id = profile.id AND mapping.actor_kind = 'account'
        JOIN identity.actor AS actor ON actor.id = mapping.actor_id AND actor.kind = mapping.actor_kind
        WHERE organization.id = (CASE WHEN current_setting('app.org_id', true) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' THEN current_setting('app.org_id', true)::uuid ELSE NULL::uuid END)
          AND profile.deleted_at IS NULL AND organization.deleted_at IS NULL AND member.deleted_at IS NULL
          AND profile.id = target_account_id AND member.id = expected_membership_id
        ORDER BY profile.id;
END;
$target_projection$;
-- Strip all named default grants and PUBLIC atomically before exact caller grants.
DO $target_acl$
DECLARE routine record; granted_role record; grantee_name text;
BEGIN
    FOR routine IN SELECT p.oid, p.proowner, p.proacl, p.oid::regprocedure AS signature
      FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
      WHERE n.nspname='identity' AND p.proname IN ('organization_account_candidates','organization_account_target')
    LOOP
        EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC', routine.signature);
        FOR granted_role IN SELECT DISTINCT a.grantee FROM aclexplode(routine.proacl) a WHERE a.grantee <> routine.proowner
        LOOP
            grantee_name := CASE WHEN granted_role.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(granted_role.grantee)) END;
            EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s', routine.signature, grantee_name);
        END LOOP;
    END LOOP;
END;
$target_acl$;
GRANT EXECUTE ON FUNCTION identity.organization_account_candidates(uuid) TO access_target_reader;
GRANT EXECUTE ON FUNCTION identity.organization_account_target(uuid,bigint) TO access_target_reader, access_setup_target_reader, access_command_owner;
GRANT CREATE ON SCHEMA identity TO identity_target_projection_owner;
ALTER FUNCTION identity.organization_account_candidates(uuid) OWNER TO identity_target_projection_owner;
ALTER FUNCTION identity.organization_account_target(uuid,bigint) OWNER TO identity_target_projection_owner;
REVOKE CREATE ON SCHEMA identity FROM identity_target_projection_owner;
"""


def upgrade():
    connection = op.get_bind()
    verify_projection_prerequisites(connection)
    verify_target_roles(connection, staged=True)
    connection.exec_driver_sql(TARGET_SCHEMA_SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
