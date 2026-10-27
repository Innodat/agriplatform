"""Private selected-account observation for controlled Access configuration."""
from alembic import op
revision='identity_0024'
down_revision='identity_0023'
branch_labels=None
depends_on=None
SQL=r'''
GRANT SELECT(account_id,actor_id,actor_kind) ON identity.account_actor TO identity_account_verification_owner;
GRANT SELECT(id,kind,actor_key) ON identity.actor TO identity_account_verification_owner;
CREATE POLICY account_grant_target_profile ON identity.users FOR SELECT TO identity_account_verification_owner
 USING(current_setting('app.context_kind',true)='setup'
 AND nullif(current_setting('app.account_id',true),'') IS NULL
 AND nullif(current_setting('app.org_id',true),'') IS NULL
 AND id::text=current_setting('app.target_account_id',true));
CREATE FUNCTION identity.account_grant_target(p_account uuid)
RETURNS TABLE(account_id uuid,actor_id uuid)
LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF current_setting('app.context_kind',true) IS DISTINCT FROM 'setup'
 OR nullif(current_setting('app.account_id',true),'') IS NOT NULL
 OR nullif(current_setting('app.org_id',true),'') IS NOT NULL
 OR current_setting('app.target_account_id',true) IS DISTINCT FROM p_account::text
 OR p_account IS NULL OR p_account='00000000-0000-0000-0000-000000000000'
 OR (current_setting('app.actor_id',true) ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
 AND current_setting('app.actor_id',true)<>'00000000-0000-0000-0000-000000000000') IS NOT TRUE THEN RETURN; END IF;
 RETURN QUERY SELECT u.id,m.actor_id FROM identity.users u
 JOIN auth.users a ON a.id=u.id AND a.deleted_at IS NULL
 JOIN identity.account_actor m ON m.account_id=u.id AND m.actor_kind='account'
 JOIN identity.actor actor ON actor.id=m.actor_id AND actor.kind='account' AND actor.actor_key IS NULL
 WHERE u.id=p_account AND u.deleted_at IS NULL AND u.is_system IS NOT TRUE AND u.actor_key IS NULL;
END $f$;
DO $acl$
DECLARE r record;a record;grantee text;
BEGIN
 SELECT p.proowner owner,p.proacl acl,p.oid::regprocedure::text object INTO r FROM pg_proc p
 WHERE p.oid='identity.account_grant_target(uuid)'::regprocedure;
 EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.object);
 FOR a IN SELECT DISTINCT x.grantee FROM aclexplode(r.acl) x WHERE x.grantee<>r.owner LOOP
 grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
 EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s',r.object,grantee); END LOOP;
END $acl$;
GRANT EXECUTE ON FUNCTION identity.account_grant_target(uuid) TO access_command_owner;
GRANT CREATE ON SCHEMA identity TO identity_account_verification_owner;
ALTER FUNCTION identity.account_grant_target(uuid) OWNER TO identity_account_verification_owner;
REVOKE CREATE ON SCHEMA identity FROM identity_account_verification_owner;
'''
def upgrade():
    from identity_baseline import verify_catalog
    verify_catalog(op.get_bind(),'language_preferences')
    op.get_bind().exec_driver_sql(SQL,execution_options={'no_parameters':True})
def downgrade():raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
