"""Private organization check-reader bridge; no effective Access reader activation."""
from alembic import op
from identity_baseline import verify_catalog, verify_check_reader_role

revision = 'identity_0020'
down_revision = 'identity_0019'
branch_labels = None
depends_on = None


SENSITIVE_EXECUTE_SQL = r"""
GRANT EXECUTE ON FUNCTION identity.authorize(identity.app_permission)
  TO authenticated, service_role, postgres,
     identity_account_projection_owner, identity_target_projection_owner,
     identity_account_verification_owner, identity_command_owner;

-- 2. Retain the existing explicit browser role lookup and Auth-hook caller.
GRANT EXECUTE ON FUNCTION public.get_user_roles() TO authenticated;
GRANT EXECUTE ON FUNCTION identity.custom_access_token_hook(jsonb) TO supabase_auth_admin;

-- 3. create_user(text) is an old test-only Auth writer with no supported runtime caller
-- in the repository. Keep owner-only; qualification uses explicit fixture provisioning.
-- Strip only these four exact routines; no schema-wide/default-privilege mutation.
DO $identity_sensitive_execute_proposal$
DECLARE routine record; granted record; recipient text;
BEGIN
  FOR routine IN
    SELECT p.oid, p.proowner, p.oid::regprocedure AS signature,
      CASE p.oid
        WHEN 'identity.authorize(identity.app_permission)'::regprocedure THEN
          ARRAY['authenticated','service_role','postgres',
                'identity_account_projection_owner','identity_target_projection_owner',
                'identity_account_verification_owner','identity_command_owner']::text[]
        WHEN 'public.get_user_roles()'::regprocedure THEN ARRAY['authenticated']::text[]
        WHEN 'identity.custom_access_token_hook(jsonb)'::regprocedure THEN ARRAY['supabase_auth_admin']::text[]
        ELSE ARRAY[]::text[]
      END AS callers
    FROM pg_proc p WHERE p.oid IN (
      'identity.authorize(identity.app_permission)'::regprocedure,
      'identity.create_user(text)'::regprocedure,
      'identity.custom_access_token_hook(jsonb)'::regprocedure,
      'public.get_user_roles()'::regprocedure)
  LOOP
    IF routine.proowner <> (SELECT oid FROM pg_roles WHERE rolname=current_user) THEN
      RAISE EXCEPTION USING MESSAGE='identity_sensitive_execute_owner_required';
    END IF;
    EXECUTE format('REVOKE EXECUTE ON FUNCTION %s FROM PUBLIC',routine.signature);
    FOR granted IN
      SELECT DISTINCT a.grantee FROM pg_proc p,
        LATERAL aclexplode(coalesce(p.proacl,acldefault('f',p.proowner))) a
      WHERE p.oid=routine.oid AND a.privilege_type='EXECUTE'
        AND a.grantee<>routine.proowner AND a.grantee<>0
    LOOP
      recipient := pg_get_userbyid(granted.grantee);
      IF NOT recipient=ANY(routine.callers) THEN
        EXECUTE format('REVOKE EXECUTE ON FUNCTION %s FROM %I',routine.signature,recipient);
      ELSE
        EXECUTE format('REVOKE GRANT OPTION FOR EXECUTE ON FUNCTION %s FROM %I',routine.signature,recipient);
      END IF;
    END LOOP;
  END LOOP;
END;
$identity_sensitive_execute_proposal$;

-- 4. These fixed RLS authority probes are owned by authority_owner after Identity17.
-- The migrator's existing SET-only edge is required; executing REVOKE as migrator
-- without SET ROLE silently lacks owner authority and can leave PUBLIC grants intact.
SET LOCAL ROLE identity_operator_authority_owner;
GRANT EXECUTE ON FUNCTION identity.membership_join_profile_allowed(uuid),
  identity.membership_join_org_allowed(uuid) TO identity_command_owner;
DO $identity_join_execute_proposal$
DECLARE routine record; granted record; recipient text;
BEGIN
  FOR routine IN
    SELECT p.oid,p.proowner,p.oid::regprocedure AS signature FROM pg_proc p
    WHERE p.oid IN ('identity.membership_join_profile_allowed(uuid)'::regprocedure,
                   'identity.membership_join_org_allowed(uuid)'::regprocedure)
  LOOP
    IF routine.proowner <> (SELECT oid FROM pg_roles WHERE rolname=current_user) THEN
      RAISE EXCEPTION USING MESSAGE='identity_sensitive_execute_owner_required';
    END IF;
    EXECUTE format('REVOKE EXECUTE ON FUNCTION %s FROM PUBLIC',routine.signature);
    FOR granted IN
      SELECT DISTINCT a.grantee FROM pg_proc p,
        LATERAL aclexplode(coalesce(p.proacl,acldefault('f',p.proowner))) a
      WHERE p.oid=routine.oid AND a.privilege_type='EXECUTE'
        AND a.grantee<>routine.proowner AND a.grantee<>0
    LOOP
      recipient := pg_get_userbyid(granted.grantee);
      IF recipient<>'identity_command_owner' THEN
        EXECUTE format('REVOKE EXECUTE ON FUNCTION %s FROM %I',routine.signature,recipient);
      ELSE
        EXECUTE format('REVOKE GRANT OPTION FOR EXECUTE ON FUNCTION %s FROM %I',routine.signature,recipient);
      END IF;
    END LOOP;
  END LOOP;
END;
$identity_join_execute_proposal$;
RESET ROLE;

"""

def upgrade():
    connection = op.get_bind()
    # Refuse unknown definitions, owners and ACLs before any ACL mutation.
    verify_catalog(connection, 'organization_target')
    verify_check_reader_role(connection, staged=True, legacy=True)
    connection.exec_driver_sql(SENSITIVE_EXECUTE_SQL, execution_options={'no_parameters': True})
    verify_check_reader_role(connection, staged=True)
    connection.exec_driver_sql('GRANT USAGE ON SCHEMA identity TO access_check_reader')
    # Existing SET-only migration edge: the schema owner cannot grant this function.
    connection.exec_driver_sql('SET LOCAL ROLE identity_account_projection_owner')
    connection.exec_driver_sql('GRANT EXECUTE ON FUNCTION identity.current_account_organization() TO access_check_reader')
    connection.exec_driver_sql('RESET ROLE')
    verify_check_reader_role(connection)


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
