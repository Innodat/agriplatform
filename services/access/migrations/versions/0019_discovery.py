"""Entry-only current discovery using restricted owner columns and account RLS."""
from alembic import op
revision='access_0019'
down_revision='access_0018'
branch_labels=None
depends_on=None
COLUMNS={
 'applications':('app_id','enabled'),
 'permissions':('permission','app_id','scope_kind'),
 'entry_permissions':('app_id','permission'),
 'organization_applications':('org_id','app_id','enabled'),
 'grants':('org_id','user_id','membership_id','permission','scope_kind','revoked_at'),
 'account_grants':('account_id','permission','scope_kind','revoked_at'),
}
SQL='GRANT USAGE ON SCHEMA access TO access_discovery_owner;\n'
for table,columns in COLUMNS.items():SQL+='GRANT SELECT('+','.join(columns)+') ON access.'+table+' TO access_discovery_owner;\n'
SQL+=r'''
-- Policy expressions are installed by the table-owning migrator, which has no
-- Identity schema authority. Bind them to this private Access-owned projection;
-- only its definer resolves/calls the Identity interface.
GRANT CREATE ON SCHEMA access TO access_discovery_owner;
SET LOCAL ROLE access_discovery_owner;
CREATE FUNCTION access.discovery_memberships()
RETURNS TABLE(org_id uuid,org_name text,membership_id bigint)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT m.org_id,m.org_name,m.membership_id FROM identity.current_account_memberships() m
$f$;
REVOKE ALL ON FUNCTION access.discovery_memberships() FROM PUBLIC;
RESET ROLE;
CREATE POLICY discovery_org_read ON access.organization_applications FOR SELECT TO access_discovery_owner
 USING(EXISTS(SELECT 1 FROM access.discovery_memberships() m WHERE m.org_id=organization_applications.org_id));
CREATE POLICY discovery_org_bound ON access.organization_applications AS RESTRICTIVE FOR SELECT TO access_discovery_owner
 USING(EXISTS(SELECT 1 FROM access.discovery_memberships() m WHERE m.org_id=organization_applications.org_id));
CREATE POLICY discovery_grant_read ON access.grants FOR SELECT TO access_discovery_owner
 USING(user_id::text=current_setting('app.account_id',true) AND revoked_at IS NULL AND EXISTS(SELECT 1 FROM access.discovery_memberships() m WHERE m.org_id=grants.org_id AND m.membership_id=grants.membership_id));
CREATE POLICY discovery_grant_bound ON access.grants AS RESTRICTIVE FOR SELECT TO access_discovery_owner
 USING(user_id::text=current_setting('app.account_id',true) AND revoked_at IS NULL AND EXISTS(SELECT 1 FROM access.discovery_memberships() m WHERE m.org_id=grants.org_id AND m.membership_id=grants.membership_id));
CREATE POLICY discovery_account_read ON access.account_grants FOR SELECT TO access_discovery_owner
 USING(current_setting('app.context_kind',true)='user' AND account_id::text=current_setting('app.account_id',true) AND revoked_at IS NULL AND nullif(current_setting('app.org_id',true),'') IS NULL);
CREATE POLICY discovery_account_bound ON access.account_grants AS RESTRICTIVE FOR SELECT TO access_discovery_owner
 USING(current_setting('app.context_kind',true)='user' AND account_id::text=current_setting('app.account_id',true) AND revoked_at IS NULL AND nullif(current_setting('app.org_id',true),'') IS NULL);
SET LOCAL ROLE access_discovery_owner;
CREATE FUNCTION access.discover_organizations(p_app_id text,p_after_org_id uuid,p_page_size integer)
RETURNS TABLE(org_id uuid,org_name text,membership_id bigint)
LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 PERFORM account_id FROM identity.discovery_account_context();
 IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='ID003',MESSAGE='discovery_account_denied'; END IF;
 IF (SELECT count(*) FROM access.applications)>128 THEN RAISE EXCEPTION USING ERRCODE='DC001',MESSAGE='discovery_catalogue_oversized'; END IF;
 IF p_app_id IS NULL OR p_app_id !~ '^[a-z][a-z0-9_]{1,63}$'
 OR NOT EXISTS(SELECT 1 FROM access.applications a WHERE a.app_id=p_app_id)
 OR p_page_size IS NULL OR p_page_size<1 OR p_page_size>100
 OR p_after_org_id='00000000-0000-0000-0000-000000000000'::uuid
 THEN RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='discovery_input_invalid'; END IF;
 RETURN QUERY SELECT m.org_id,m.org_name,m.membership_id
 FROM identity.current_account_memberships() m
 JOIN access.organization_applications oa ON oa.org_id=m.org_id AND oa.app_id=p_app_id AND oa.enabled
 JOIN access.applications a ON a.app_id=oa.app_id AND a.enabled
 WHERE (p_after_org_id IS NULL OR m.org_id>p_after_org_id)
 AND EXISTS(SELECT 1 FROM access.grants g
 JOIN access.permissions p ON p.permission=g.permission AND p.scope_kind='organization' AND p.app_id=a.app_id
 JOIN access.entry_permissions e ON e.app_id=p.app_id AND e.permission=p.permission
 WHERE g.org_id=m.org_id AND g.membership_id=m.membership_id
 AND g.user_id::text=current_setting('app.account_id',true) AND g.scope_kind='organization' AND g.revoked_at IS NULL)
 ORDER BY m.org_id LIMIT p_page_size+1;
END $f$;
CREATE FUNCTION access.discover_applications()
RETURNS TABLE(app_id text,eligible_scope_kinds text[])
LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 PERFORM account_id FROM identity.discovery_account_context();
 IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='ID003',MESSAGE='discovery_account_denied'; END IF;
 IF (SELECT count(*) FROM access.applications)>128 THEN RAISE EXCEPTION USING ERRCODE='DC001',MESSAGE='discovery_catalogue_oversized'; END IF;
 RETURN QUERY WITH eligible AS (
 SELECT a.app_id,'account'::text scope_kind FROM access.applications a
 JOIN access.permissions p ON p.app_id=a.app_id AND p.scope_kind='account'
 JOIN access.entry_permissions e ON e.app_id=p.app_id AND e.permission=p.permission
 JOIN access.account_grants g ON g.permission=p.permission AND g.scope_kind='account' AND g.revoked_at IS NULL
 JOIN identity.discovery_account_context() i ON i.account_id=g.account_id
 WHERE a.enabled
 UNION
 SELECT a.app_id,'organization'::text scope_kind FROM access.applications a
 JOIN access.permissions p ON p.app_id=a.app_id AND p.scope_kind='organization'
 JOIN access.entry_permissions e ON e.app_id=p.app_id AND e.permission=p.permission
 JOIN access.grants g ON g.permission=p.permission AND g.scope_kind='organization' AND g.revoked_at IS NULL
 JOIN identity.current_account_memberships() m ON m.org_id=g.org_id AND m.membership_id=g.membership_id
 JOIN access.organization_applications oa ON oa.app_id=a.app_id AND oa.org_id=m.org_id AND oa.enabled
 WHERE a.enabled AND g.user_id::text=current_setting('app.account_id',true)
 ) SELECT eligible.app_id,array_agg(eligible.scope_kind ORDER BY eligible.scope_kind COLLATE "C")
 FROM eligible GROUP BY eligible.app_id ORDER BY eligible.app_id COLLATE "C";
END $f$;
DO $acl$
DECLARE r record;a record;grantee text;
BEGIN FOR r IN SELECT p.proname name,p.proowner owner,p.proacl acl,p.oid::regprocedure::text object
 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access'
 AND p.proname IN ('discovery_memberships','discover_organizations','discover_applications') LOOP
 EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.object);
 FOR a IN SELECT DISTINCT x.grantee FROM aclexplode(r.acl) x WHERE x.grantee<>r.owner LOOP
 grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
 EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s',r.object,grantee);END LOOP;
 IF r.name<>'discovery_memberships' THEN
 EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO access_runtime',r.object);
 END IF;
 END LOOP;
END $acl$;
RESET ROLE;
REVOKE CREATE ON SCHEMA access FROM access_discovery_owner;
'''

def upgrade():
    from access_baseline import verify_catalog
    from access_discovery_catalog import verify_role
    from sqlalchemy import text
    connection=op.get_bind()
    verify_catalog(connection,'access_0018')
    verify_role(connection)
    if not connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity' AND p.proname='current_account_memberships')")).scalar_one():raise RuntimeError('identity_discovery_prerequisite_missing')
    connection.exec_driver_sql(SQL,execution_options={'no_parameters':True})

def downgrade():raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
