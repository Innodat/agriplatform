"""Private current capability/context projections, without provisioning authority."""
from alembic import op
revision='identity_0025'
down_revision='identity_0024'
branch_labels=None
depends_on=None
SQL=r'''
CREATE FUNCTION identity.capability_account_context()
RETURNS TABLE(account_id uuid,actor_id uuid)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT a.account_id,a.actor_id FROM identity.current_account_actor() a
 JOIN identity.users u ON u.id=a.account_id
 WHERE u.deleted_at IS NULL AND u.is_system IS NOT TRUE AND u.actor_key IS NULL
$f$;
CREATE FUNCTION identity.capability_organization_context()
RETURNS TABLE(account_id uuid,org_id uuid,membership_id bigint,actor_id uuid,person_id uuid)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT i.account_id,i.org_id,i.membership_id,i.actor_id,p.person_id
 FROM identity.current_account_organization() i
 JOIN identity.users u ON u.id=i.account_id
 LEFT JOIN identity.account_person p ON p.account_id=i.account_id AND p.actor_id=i.actor_id
 WHERE u.deleted_at IS NULL AND u.is_system IS NOT TRUE AND u.actor_key IS NULL
$f$;
-- RLS remains enforced by the existing narrow projection owner.
GRANT SELECT(is_system,actor_key) ON identity.users TO identity_account_projection_owner;
DO $acl$
DECLARE r record;a record;grantee text;
BEGIN
 FOR r IN SELECT p.proowner owner,p.proacl acl,p.oid::regprocedure::text object
 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
 WHERE n.nspname='identity' AND p.proname IN ('capability_account_context','capability_organization_context') LOOP
 EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.object);
 FOR a IN SELECT DISTINCT x.grantee FROM aclexplode(r.acl) x WHERE x.grantee<>r.owner LOOP
 grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
 EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s',r.object,grantee); END LOOP;
 END LOOP;
END $acl$;
GRANT USAGE ON SCHEMA identity TO access_capability_reader;
GRANT EXECUTE ON FUNCTION identity.capability_account_context(),identity.capability_organization_context() TO access_capability_reader;
GRANT CREATE ON SCHEMA identity TO identity_account_projection_owner;
ALTER FUNCTION identity.capability_account_context() OWNER TO identity_account_projection_owner;
ALTER FUNCTION identity.capability_organization_context() OWNER TO identity_account_projection_owner;
REVOKE CREATE ON SCHEMA identity FROM identity_account_projection_owner;
'''

def upgrade():
    from identity_baseline import verify_catalog,BaselineError
    from sqlalchemy import text
    connection=op.get_bind()
    verify_catalog(connection,'account_grant_target')
    row=connection.execute(text("SELECT rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit FROM pg_roles WHERE rolname='access_capability_reader'")).one_or_none()
    if row is None or tuple(row)!=(False,False,False,False,False,False,False):raise BaselineError('capability_reader_role_unsafe')
    edges=[tuple(row) for row in connection.execute(text("SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,inherit_option,set_option FROM pg_auth_members WHERE roleid='access_capability_reader'::regrole OR member='access_capability_reader'::regrole"))]
    if edges!=[('access_capability_reader','access_migrator',False,False,True)]:raise BaselineError('capability_reader_role_unsafe')
    dependencies=connection.execute(text("SELECT count(*) FROM pg_shdepend WHERE refclassid='pg_authid'::regclass AND refobjid='access_capability_reader'::regrole AND deptype IN ('a','o','r') AND dbid IN (0,(SELECT oid FROM pg_database WHERE datname=current_database()))")).scalar_one()
    if dependencies:raise BaselineError('capability_reader_not_empty')
    connection.exec_driver_sql(SQL,execution_options={'no_parameters':True})

def downgrade():raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
