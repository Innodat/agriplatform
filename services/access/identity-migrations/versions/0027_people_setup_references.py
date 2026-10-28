"""Narrow organization/person existence for accountless People setup; no writes."""
from alembic import op
revision='identity_0027'
down_revision='identity_0026'
branch_labels=None
depends_on=None
SQL=r'''
GRANT USAGE ON SCHEMA identity TO identity_people_setup_runtime;
GRANT SELECT(id) ON identity.person TO identity_account_verification_owner;
CREATE POLICY people_setup_person ON identity.person FOR SELECT TO identity_account_verification_owner
 USING(id::text=current_setting('app.people_setup_person_id',true));
CREATE POLICY people_setup_org ON identity.org FOR SELECT TO identity_account_verification_owner
 USING(id::text=current_setting('app.people_setup_org_id',true) AND deleted_at IS NULL);
GRANT SELECT(id,deleted_at) ON identity.org TO identity_account_verification_owner;
GRANT CREATE ON SCHEMA identity TO identity_account_verification_owner;
SET LOCAL ROLE identity_account_verification_owner;
CREATE FUNCTION identity.people_setup_references() RETURNS TABLE(org_id uuid,person_id uuid)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT o.id,p.id FROM identity.org o CROSS JOIN identity.person p
 WHERE o.id::text=current_setting('app.people_setup_org_id',true) AND o.deleted_at IS NULL
 AND p.id::text=current_setting('app.people_setup_person_id',true)
 AND session_user='identity_people_setup_runtime'
$f$;
DO $acl$
DECLARE item record;grantee text;
BEGIN
 REVOKE ALL ON FUNCTION identity.people_setup_references() FROM PUBLIC;
 FOR item IN SELECT DISTINCT x.grantee FROM pg_proc p,LATERAL aclexplode(p.proacl) x
 WHERE p.oid='identity.people_setup_references()'::regprocedure AND x.grantee<>p.proowner LOOP
 grantee:=CASE WHEN item.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(item.grantee)) END;
 EXECUTE format('REVOKE ALL ON FUNCTION identity.people_setup_references() FROM %s',grantee);
 END LOOP;
END $acl$;
GRANT EXECUTE ON FUNCTION identity.people_setup_references() TO identity_people_setup_runtime;
RESET ROLE;
REVOKE CREATE ON SCHEMA identity FROM identity_account_verification_owner;
'''
def upgrade():
    from identity_baseline import verify_catalog
    from sqlalchemy import text
    c=op.get_bind();verify_catalog(c,'discovery')
    flags=c.execute(text("SELECT rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit FROM pg_roles WHERE rolname='identity_people_setup_runtime'")).one()
    if tuple(flags)!=(True,False,False,False,False,False,False):raise RuntimeError('people_setup_role_unsafe')
    if c.execute(text("SELECT EXISTS(SELECT 1 FROM pg_auth_members WHERE member=to_regrole('identity_people_setup_runtime') OR roleid=to_regrole('identity_people_setup_runtime')) OR has_database_privilege('identity_people_setup_runtime',current_database(),'CREATE')")).scalar_one():raise RuntimeError('people_setup_role_unsafe')
    c.exec_driver_sql(SQL,execution_options={'no_parameters':True})
def downgrade():raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
