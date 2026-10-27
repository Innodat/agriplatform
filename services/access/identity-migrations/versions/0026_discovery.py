"""Narrow current-account discovery facts, independent of actor/person setup."""
from alembic import op
revision='identity_0026'
down_revision='identity_0025'
branch_labels=None
depends_on=None

SQL=r'''
GRANT USAGE ON SCHEMA identity,auth TO identity_discovery_owner;
-- Existing PUBLIC profile policies invoke this legacy helper even for private
-- projection owners. Match Identity20's exact private-owner treatment; discovery's
-- restrictive account policy remains binding regardless of JWT-derived helper output.
GRANT EXECUTE ON FUNCTION identity.authorize(identity.app_permission) TO identity_discovery_owner;
GRANT SELECT(id,deleted_at,is_system,actor_key) ON identity.users TO identity_discovery_owner;
GRANT SELECT(id,name,deleted_at) ON identity.org TO identity_discovery_owner;
GRANT SELECT(id,org_id,user_id,deleted_at) ON identity.org_member TO identity_discovery_owner;
CREATE POLICY discovery_account_read ON identity.users FOR SELECT TO identity_discovery_owner
 USING(current_setting('app.context_kind',true)='user' AND id::text=current_setting('app.account_id',true) AND deleted_at IS NULL AND is_system IS NOT TRUE AND actor_key IS NULL);
CREATE POLICY discovery_account_bound ON identity.users AS RESTRICTIVE FOR SELECT TO identity_discovery_owner
 USING(current_setting('app.context_kind',true)='user' AND id::text=current_setting('app.account_id',true) AND deleted_at IS NULL AND is_system IS NOT TRUE AND actor_key IS NULL);
CREATE POLICY discovery_membership_read ON identity.org_member FOR SELECT TO identity_discovery_owner
 USING(current_setting('app.context_kind',true)='user' AND user_id::text=current_setting('app.account_id',true) AND deleted_at IS NULL);
CREATE POLICY discovery_membership_bound ON identity.org_member AS RESTRICTIVE FOR SELECT TO identity_discovery_owner
 USING(current_setting('app.context_kind',true)='user' AND user_id::text=current_setting('app.account_id',true) AND deleted_at IS NULL);
CREATE POLICY discovery_organization_read ON identity.org FOR SELECT TO identity_discovery_owner
 USING(deleted_at IS NULL AND EXISTS(SELECT 1 FROM identity.org_member m WHERE m.org_id=org.id AND m.user_id::text=current_setting('app.account_id',true) AND m.deleted_at IS NULL));
CREATE POLICY discovery_organization_bound ON identity.org AS RESTRICTIVE FOR SELECT TO identity_discovery_owner
 USING(deleted_at IS NULL AND EXISTS(SELECT 1 FROM identity.org_member m WHERE m.org_id=org.id AND m.user_id::text=current_setting('app.account_id',true) AND m.deleted_at IS NULL));
GRANT CREATE ON SCHEMA identity TO identity_discovery_owner;
SET LOCAL ROLE identity_discovery_owner;
CREATE FUNCTION identity.discovery_account_context()
RETURNS TABLE(account_id uuid)
LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE asserted text;
BEGIN
 asserted:=current_setting('app.account_id',true);
 IF current_setting('app.context_kind',true) IS DISTINCT FROM 'user'
 OR nullif(current_setting('app.org_id',true),'') IS NOT NULL
 OR asserted IS NULL OR asserted !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
 OR asserted='00000000-0000-0000-0000-000000000000'
 OR nullif(current_setting('app.discovery_transaction',true),'') IS NULL
 OR current_setting('app.discovery_transaction',true) IS DISTINCT FROM pg_current_xact_id_if_assigned()::text
 THEN RAISE EXCEPTION USING ERRCODE='ID001',MESSAGE='discovery_context_invalid'; END IF;
 RETURN QUERY SELECT u.id FROM identity.users u WHERE u.id=asserted::uuid
 AND u.deleted_at IS NULL AND u.is_system IS NOT TRUE AND u.actor_key IS NULL;
END $f$;
CREATE FUNCTION identity.current_account_memberships()
RETURNS TABLE(org_id uuid,org_name text,membership_id bigint)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT o.id,o.name,m.id FROM identity.discovery_account_context() a
 JOIN identity.org_member m ON m.user_id=a.account_id AND m.deleted_at IS NULL
 JOIN identity.org o ON o.id=m.org_id AND o.deleted_at IS NULL
 ORDER BY o.id
$f$;
DO $acl$
DECLARE r record;a record;grantee text;
BEGIN FOR r IN SELECT p.proowner owner,p.proacl acl,p.oid::regprocedure::text object
 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity'
 AND p.proname IN ('discovery_account_context','current_account_memberships') LOOP
 EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.object);
 FOR a IN SELECT DISTINCT x.grantee FROM aclexplode(r.acl) x WHERE x.grantee<>r.owner LOOP
 grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
 EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s',r.object,grantee);END LOOP;
 EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO access_discovery_owner',r.object);
 END LOOP;
END $acl$;
RESET ROLE;
REVOKE CREATE ON SCHEMA identity FROM identity_discovery_owner;
GRANT USAGE ON SCHEMA identity TO access_discovery_owner;
'''

def upgrade():
    from identity_baseline import verify_catalog
    from identity_discovery_catalog import verify_role
    connection=op.get_bind()
    verify_catalog(connection,'capability_reader')
    verify_role(connection,'identity_discovery_owner','identity_migrator',empty=True)
    verify_role(connection,'access_discovery_owner','access_migrator',empty=True)
    connection.exec_driver_sql(SQL,execution_options={'no_parameters':True})

def downgrade():raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
