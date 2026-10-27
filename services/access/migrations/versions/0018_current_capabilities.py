"""Exact current registered account/organization capability readers."""
from alembic import op
revision='access_0018'
down_revision='access_0017'
branch_labels=None
depends_on=None
COLUMNS={
 'applications':('app_id','enabled'),
 'permissions':('permission','app_id','scope_kind'),
 'organization_applications':('org_id','app_id','enabled'),
 'grants':('org_id','user_id','membership_id','permission','scope_kind','revoked_at'),
 'account_grants':('account_id','permission','scope_kind','revoked_at'),
}
SQL='GRANT USAGE ON SCHEMA access TO access_capability_reader;\n'
for table,columns in COLUMNS.items():
    SQL+='GRANT SELECT('+','.join(columns)+') ON access.'+table+' TO access_capability_reader;\n'
SQL+=r'''
CREATE POLICY capability_org_read ON access.organization_applications FOR SELECT TO access_capability_reader
 USING(current_setting('app.context_kind',true)='user' AND org_id::text=current_setting('app.org_id',true));
CREATE POLICY capability_org_bound ON access.organization_applications AS RESTRICTIVE FOR SELECT TO access_capability_reader
 USING(current_setting('app.context_kind',true)='user' AND org_id::text=current_setting('app.org_id',true));
CREATE POLICY capability_grant_read ON access.grants FOR SELECT TO access_capability_reader
 USING(current_setting('app.context_kind',true)='user' AND org_id::text=current_setting('app.org_id',true) AND user_id::text=current_setting('app.account_id',true));
CREATE POLICY capability_grant_bound ON access.grants AS RESTRICTIVE FOR SELECT TO access_capability_reader
 USING(current_setting('app.context_kind',true)='user' AND org_id::text=current_setting('app.org_id',true) AND user_id::text=current_setting('app.account_id',true));
CREATE POLICY capability_account_read ON access.account_grants FOR SELECT TO access_capability_reader
 USING(current_setting('app.context_kind',true)='user' AND account_id::text=current_setting('app.account_id',true) AND nullif(current_setting('app.org_id',true),'') IS NULL);
CREATE POLICY capability_account_bound ON access.account_grants AS RESTRICTIVE FOR SELECT TO access_capability_reader
 USING(current_setting('app.context_kind',true)='user' AND account_id::text=current_setting('app.account_id',true) AND nullif(current_setting('app.org_id',true),'') IS NULL);
GRANT CREATE ON SCHEMA access TO access_capability_reader;
SET LOCAL ROLE access_capability_reader;
CREATE FUNCTION access.check_account_capability(p_permission text)
RETURNS TABLE(account_id uuid,actor_id uuid)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT i.account_id,i.actor_id FROM identity.capability_account_context() i
 JOIN access.account_grants g ON g.account_id=i.account_id AND g.permission=p_permission AND g.scope_kind='account' AND g.revoked_at IS NULL
 JOIN access.permissions p ON p.permission=g.permission AND p.scope_kind='account'
 JOIN access.applications a ON a.app_id=p.app_id AND a.enabled
 WHERE current_setting('app.context_kind',true)='user' AND i.account_id::text=current_setting('app.account_id',true)
 AND nullif(current_setting('app.org_id',true),'') IS NULL
$f$;
CREATE FUNCTION access.check_organization_capability(p_permission text)
RETURNS TABLE(account_id uuid,org_id uuid,membership_id bigint,actor_id uuid,person_id uuid)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT i.account_id,i.org_id,i.membership_id,i.actor_id,i.person_id FROM identity.capability_organization_context() i
 JOIN access.grants g ON g.user_id=i.account_id AND g.org_id=i.org_id AND g.membership_id=i.membership_id
 AND g.permission=p_permission AND g.scope_kind='organization' AND g.revoked_at IS NULL
 JOIN access.permissions p ON p.permission=g.permission AND p.scope_kind='organization'
 JOIN access.applications a ON a.app_id=p.app_id AND a.enabled
 JOIN access.organization_applications oa ON oa.org_id=i.org_id AND oa.app_id=a.app_id AND oa.enabled
 WHERE current_setting('app.context_kind',true)='user' AND i.account_id::text=current_setting('app.account_id',true)
 AND i.org_id::text=current_setting('app.org_id',true)
$f$;
CREATE FUNCTION access.current_organization_context()
RETURNS TABLE(account_id uuid,org_id uuid,membership_id bigint,actor_id uuid,person_id uuid)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT * FROM identity.capability_organization_context()
$f$;
DO $acl$
DECLARE r record;a record;grantee text;
BEGIN FOR r IN SELECT p.proowner owner,p.proacl acl,p.oid::regprocedure::text object
 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access'
 AND p.proname IN ('check_account_capability','check_organization_capability','current_organization_context') LOOP
 EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.object);
 FOR a IN SELECT DISTINCT x.grantee FROM aclexplode(r.acl) x WHERE x.grantee<>r.owner LOOP
 grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
 EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s',r.object,grantee);END LOOP;
 EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO access_runtime',r.object);
 END LOOP;
END $acl$;
RESET ROLE;
REVOKE CREATE ON SCHEMA access FROM access_capability_reader;
'''

def upgrade():
    from access_baseline import verify_catalog
    from access_capability_catalog import verify_reader_role
    connection=op.get_bind()
    verify_catalog(connection,'access_0017')
    verify_reader_role(connection,installed=False)
    connection.exec_driver_sql(SQL,execution_options={'no_parameters':True})

def downgrade():raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
