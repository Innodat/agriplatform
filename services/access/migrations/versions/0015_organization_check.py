"""Current exact membership-bound organization authorization reader."""
from alembic import op
revision = 'access_0015'
down_revision = 'access_0014'
branch_labels = None
depends_on = None

BODY = r'''
 SELECT i.account_id,i.org_id,i.membership_id,i.actor_id
 FROM identity.current_account_organization() i
 JOIN access.grants g ON g.org_id=i.org_id AND g.user_id=i.account_id
   AND g.membership_id=i.membership_id AND g.permission=p_permission
   AND g.scope_kind='organization' AND g.revoked_at IS NULL
 JOIN access.permissions p ON p.permission=g.permission AND p.scope_kind='organization' AND p.app_id='kdg_capture'
 JOIN access.applications a ON a.app_id=p.app_id AND a.enabled
 JOIN access.organization_applications oa ON oa.org_id=i.org_id AND oa.app_id=a.app_id AND oa.enabled
 WHERE current_setting('app.context_kind',true)='user'
   AND i.account_id::text=current_setting('app.account_id',true)
   AND i.org_id::text=current_setting('app.org_id',true)
'''
COLUMNS = {
    'applications': ('app_id','enabled'),
    'permissions': ('permission','app_id','scope_kind'),
    'organization_applications': ('org_id','app_id','enabled'),
    'grants': ('org_id','user_id','membership_id','permission','scope_kind','revoked_at'),
}
SQL = '\nREVOKE SELECT ON access.grants FROM access_runtime;\nGRANT USAGE ON SCHEMA access TO access_check_reader;\n'
for table, columns in COLUMNS.items():
    SQL += 'GRANT SELECT ('+','.join(columns)+') ON access.'+table+' TO access_check_reader;\n'
SQL += r'''
CREATE POLICY check_reader_org_scope ON access.organization_applications FOR SELECT TO access_check_reader
 USING (org_id::text=current_setting('app.org_id',true));
CREATE POLICY check_reader_account_scope ON access.grants AS RESTRICTIVE FOR SELECT TO access_check_reader
 USING (org_id::text=current_setting('app.org_id',true) AND user_id::text=current_setting('app.account_id',true));
-- Create as the private reader so SQL validation uses its existing Identity rights.
GRANT CREATE ON SCHEMA access TO access_check_reader;
SET LOCAL ROLE access_check_reader;
CREATE FUNCTION access.check_organization_permission(p_permission text)
 RETURNS TABLE(account_id uuid,org_id uuid,membership_id bigint,actor_id uuid)
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$'''+BODY+r'''$f$;
REVOKE ALL ON FUNCTION access.check_organization_permission(text) FROM PUBLIC,anon,authenticated,service_role;
GRANT EXECUTE ON FUNCTION access.check_organization_permission(text) TO access_runtime;
RESET ROLE;
REVOKE CREATE ON SCHEMA access FROM access_check_reader;
'''


def upgrade():
    connection = op.get_bind()
    # The fixed coordinated bridge verifier checks staged flags/edge/foreign ACLs.
    from access_organization_check_catalog import verify_reader_role
    verify_reader_role(connection, installed=False)
    connection.exec_driver_sql(SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
