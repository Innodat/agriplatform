"""Account-owned desired language, revision and original write outcomes."""
from alembic import op
revision='identity_0023'
down_revision='identity_0022'
branch_labels=None
depends_on=None

SQL=r'''
CREATE TABLE identity.account_language_preference(
 account_id uuid PRIMARY KEY CHECK(account_id<>'00000000-0000-0000-0000-000000000000'),
 preferred_locale text NOT NULL CHECK(preferred_locale IN ('en','pt')),
 revision bigint NOT NULL CHECK(revision>0),
 created_by uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
 created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 updated_by uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
 updated_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 FOREIGN KEY(account_id,created_by) REFERENCES identity.account_actor(account_id,actor_id) ON DELETE RESTRICT,
 FOREIGN KEY(account_id,updated_by) REFERENCES identity.account_actor(account_id,actor_id) ON DELETE RESTRICT);
CREATE TABLE identity.language_preference_outcome(
 account_id uuid NOT NULL CHECK(account_id<>'00000000-0000-0000-0000-000000000000'),
 operation_id uuid NOT NULL CHECK(operation_id<>'00000000-0000-0000-0000-000000000000'),
 fingerprint bytea NOT NULL CHECK(octet_length(fingerprint)=32),
 preferred_locale text NOT NULL CHECK(preferred_locale IN ('en','pt')),
 revision bigint NOT NULL CHECK(revision>0),
 actor_id uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
 created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 PRIMARY KEY(account_id,operation_id),
 FOREIGN KEY(account_id,actor_id) REFERENCES identity.account_actor(account_id,actor_id) ON DELETE RESTRICT);
CREATE FUNCTION identity.language_outcome_immutable() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
BEGIN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_preference_outcome_immutable';END $f$;
CREATE TRIGGER language_outcome_retention BEFORE UPDATE OR DELETE OR TRUNCATE
 ON identity.language_preference_outcome FOR EACH STATEMENT EXECUTE FUNCTION identity.language_outcome_immutable();
ALTER TABLE identity.account_language_preference ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.account_language_preference FORCE ROW LEVEL SECURITY;
ALTER TABLE identity.language_preference_outcome ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.language_preference_outcome FORCE ROW LEVEL SECURITY;
CREATE POLICY migration_inspection ON identity.account_language_preference FOR SELECT TO identity_migrator USING(true);
CREATE POLICY migration_inspection ON identity.language_preference_outcome FOR SELECT TO identity_migrator USING(true);
CREATE POLICY own_language ON identity.account_language_preference TO identity_command_owner
 USING(session_user='identity_preferences_runtime' AND current_setting('app.context_kind',true)='user' AND account_id::text=current_setting('app.account_id',true))
 WITH CHECK(session_user='identity_preferences_runtime' AND current_setting('app.context_kind',true)='user' AND account_id::text=current_setting('app.account_id',true));
CREATE POLICY own_language_outcomes ON identity.language_preference_outcome TO identity_command_owner
 USING(session_user='identity_preferences_runtime' AND current_setting('app.context_kind',true)='user' AND account_id::text=current_setting('app.account_id',true))
 WITH CHECK(session_user='identity_preferences_runtime' AND current_setting('app.context_kind',true)='user' AND account_id::text=current_setting('app.account_id',true));
CREATE FUNCTION identity.read_account_language() RETURNS TABLE(preferred_locale text,revision bigint)
 LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE observed record;
BEGIN
 IF session_user<>'identity_preferences_runtime' THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_preference_context_required';END IF;
 SELECT * INTO observed FROM identity.current_account_actor();
 IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_preference_context_required';END IF;
 RETURN QUERY SELECT p.preferred_locale,p.revision FROM identity.account_language_preference p WHERE p.account_id=observed.account_id;
 IF NOT FOUND THEN RETURN QUERY SELECT 'en'::text,0::bigint;END IF;
END $f$;
CREATE FUNCTION identity.set_account_language(p_operation uuid,p_expected bigint,p_locale text)
 RETURNS TABLE(preferred_locale text,revision bigint)
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE observed record;saved identity.language_preference_outcome;fingerprint bytea;current_revision bigint;next_revision bigint;
BEGIN
 IF session_user<>'identity_preferences_runtime' THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_preference_context_required';END IF;
 IF p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000' OR p_expected IS NULL OR p_expected<0
 OR p_locale IS NULL OR p_locale NOT IN ('en','pt') THEN RAISE EXCEPTION USING ERRCODE='IP004',MESSAGE='identity_preference_invalid';END IF;
 SELECT * INTO observed FROM identity.current_account_actor();
 IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_preference_context_required';END IF;
 IF observed.actor_id IS NULL THEN RAISE EXCEPTION USING ERRCODE='IP003',MESSAGE='identity_actor_setup_required';END IF;
 fingerprint:=sha256(convert_to('account-language-v1:'||p_expected::text||':'||p_locale,'UTF8'));
 PERFORM pg_advisory_xact_lock(hashtextextended('account-language-operation:'||observed.account_id::text||':'||p_operation::text,0));
 SELECT o.* INTO saved FROM identity.language_preference_outcome o WHERE o.account_id=observed.account_id AND o.operation_id=p_operation;
 IF FOUND THEN
  IF saved.fingerprint IS DISTINCT FROM fingerprint THEN RAISE EXCEPTION USING ERRCODE='IP002',MESSAGE='identity_preference_operation_conflict';END IF;
  RETURN QUERY SELECT saved.preferred_locale,saved.revision;RETURN;
 END IF;
 PERFORM pg_advisory_xact_lock(hashtextextended('account-language-account:'||observed.account_id::text,0));
 SELECT p.revision INTO current_revision FROM identity.account_language_preference p WHERE p.account_id=observed.account_id FOR UPDATE;
 current_revision:=coalesce(current_revision,0);
 IF current_revision<>p_expected THEN RAISE EXCEPTION USING ERRCODE='IP001',MESSAGE='identity_preference_revision_conflict';END IF;
 IF current_revision=9223372036854775807 THEN RAISE EXCEPTION USING ERRCODE='IP004',MESSAGE='identity_preference_revision_exhausted';END IF;
 next_revision:=current_revision+1;
 INSERT INTO identity.account_language_preference(account_id,preferred_locale,revision,created_by,updated_by)
 VALUES(observed.account_id,p_locale,next_revision,observed.actor_id,observed.actor_id)
 ON CONFLICT(account_id) DO UPDATE SET preferred_locale=excluded.preferred_locale,revision=excluded.revision,
 updated_by=excluded.updated_by,updated_at=statement_timestamp();
 INSERT INTO identity.language_preference_outcome(account_id,operation_id,fingerprint,preferred_locale,revision,actor_id)
 VALUES(observed.account_id,p_operation,fingerprint,p_locale,next_revision,observed.actor_id);
 RETURN QUERY SELECT p_locale,next_revision;
END $f$;
'''

def upgrade():
    from identity_baseline import verify_catalog
    from studies_migration_support import strip_acl,transfer_functions
    connection=op.get_bind()
    verify_catalog(connection,'person_links')
    row=connection.exec_driver_sql("SELECT rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,rolreplication,rolbypassrls FROM pg_roles WHERE rolname='identity_preferences_runtime'").one_or_none()
    if row is None or tuple(row)!=(False,False,False,False,True,False,False):raise RuntimeError('identity_preferences_role_missing_or_unsafe')
    if connection.exec_driver_sql("SELECT count(*) FROM pg_auth_members WHERE roleid='identity_preferences_runtime'::regrole OR member='identity_preferences_runtime'::regrole").scalar_one()!=0:raise RuntimeError('identity_preferences_role_membership_unsafe')
    connection.exec_driver_sql(SQL,execution_options={'no_parameters':True})
    strip_acl(connection,'identity',('language_outcome_immutable','read_account_language','set_account_language'))
    for table in ('account_language_preference','language_preference_outcome'):
        rows=connection.exec_driver_sql("SELECT DISTINCT CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END FROM pg_class c CROSS JOIN LATERAL aclexplode(c.relacl) a WHERE c.oid='identity."+table+"'::regclass AND a.grantee<>c.relowner").scalars().all()
        for role in rows:connection.exec_driver_sql('REVOKE ALL ON identity.'+table+' FROM '+role)
    connection.exec_driver_sql('''GRANT SELECT,INSERT,UPDATE ON identity.account_language_preference TO identity_command_owner;
GRANT SELECT,INSERT ON identity.language_preference_outcome TO identity_command_owner;
GRANT USAGE ON SCHEMA identity TO identity_preferences_runtime;
SET LOCAL ROLE identity_account_projection_owner;
GRANT EXECUTE ON FUNCTION identity.current_account_actor() TO identity_command_owner;
RESET ROLE;
GRANT EXECUTE ON FUNCTION identity.read_account_language(),identity.set_account_language(uuid,bigint,text) TO identity_preferences_runtime;
''')
    transfer_functions(connection,'identity','identity_command_owner',('read_account_language()','set_account_language(uuid,bigint,text)'))

def downgrade():raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
