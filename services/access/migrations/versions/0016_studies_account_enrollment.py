"""Retained account Studies grants and caller/account/version-scoped receipts."""
from alembic import op
revision='access_0016'
down_revision='access_0015'
branch_labels=None
depends_on=None

TABLES=('studies_runtime_principal','studies_account_grant','studies_enrollment_outcome','studies_assignment_event')
FUNCTIONS=('studies_registration_ready','studies_executor','studies_evidence_immutable','guard_studies_principal','guard_studies_grant','enroll_studies_account','check_studies_permission')
SQL=r'''
GRANT USAGE ON SCHEMA access TO access_studies_owner,access_studies_runtime;
CREATE TABLE access.studies_runtime_principal(
 database_login name PRIMARY KEY CHECK(database_login='access_studies_runtime'),
 executor_actor_id uuid NOT NULL CHECK(executor_actor_id<>'00000000-0000-0000-0000-000000000000'),
 enabled boolean NOT NULL DEFAULT false,created_by uuid NOT NULL,
 created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 updated_by uuid NOT NULL,updated_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 revision bigint NOT NULL DEFAULT 1 CHECK(revision>0),operation_id uuid NOT NULL);
CREATE TABLE access.studies_account_grant(
 account_id uuid PRIMARY KEY CHECK(account_id<>'00000000-0000-0000-0000-000000000000'),
 actor_id uuid NOT NULL CHECK(actor_id<>'00000000-0000-0000-0000-000000000000'),
 permission text NOT NULL DEFAULT 'scribeswell.studies.use' CHECK(permission='scribeswell.studies.use'),
 authorization_scope text NOT NULL DEFAULT 'account' CHECK(authorization_scope='account'),
 executor_actor_id uuid NOT NULL CHECK(executor_actor_id<>'00000000-0000-0000-0000-000000000000'),
 initiator_actor_id uuid NOT NULL CHECK(initiator_actor_id=actor_id),
 created_at timestamptz NOT NULL DEFAULT statement_timestamp(),revoked_at timestamptz,
 revoked_by uuid,revocation_operation_id uuid,
 CHECK((revoked_at IS NULL AND revoked_by IS NULL AND revocation_operation_id IS NULL) OR
 (revoked_at IS NOT NULL AND revoked_by IS NOT NULL AND revoked_by<>'00000000-0000-0000-0000-000000000000'
 AND revocation_operation_id IS NOT NULL AND revocation_operation_id<>'00000000-0000-0000-0000-000000000000')));
CREATE TABLE access.studies_enrollment_outcome(
 database_login name NOT NULL CHECK(database_login='access_studies_runtime'),
 account_id uuid NOT NULL REFERENCES access.studies_account_grant(account_id),
 command_version integer NOT NULL DEFAULT 1 CHECK(command_version=1),
 operation_id uuid NOT NULL CHECK(operation_id<>'00000000-0000-0000-0000-000000000000'),
 actor_id uuid NOT NULL CHECK(actor_id<>'00000000-0000-0000-0000-000000000000'),
 disposition text NOT NULL CHECK(disposition IN ('created','unchanged')),
 executor_actor_id uuid NOT NULL CHECK(executor_actor_id<>'00000000-0000-0000-0000-000000000000'),
 initiator_actor_id uuid NOT NULL CHECK(initiator_actor_id=actor_id),
 committed_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 PRIMARY KEY(database_login,account_id,command_version,operation_id));
CREATE TABLE access.studies_assignment_event(
 event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 event_type text NOT NULL DEFAULT 'access.studies_account_enrolled' CHECK(event_type='access.studies_account_enrolled'),
 event_version integer NOT NULL DEFAULT 1 CHECK(event_version=1),
 account_id uuid NOT NULL UNIQUE REFERENCES access.studies_account_grant(account_id),
 actor_id uuid NOT NULL CHECK(actor_id<>'00000000-0000-0000-0000-000000000000'),
 executor_actor_id uuid NOT NULL CHECK(executor_actor_id<>'00000000-0000-0000-0000-000000000000'),
 initiator_actor_id uuid NOT NULL CHECK(initiator_actor_id=actor_id),
 database_login name NOT NULL,command_version integer NOT NULL DEFAULT 1 CHECK(command_version=1),operation_id uuid NOT NULL,
 created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 FOREIGN KEY(database_login,account_id,command_version,operation_id)
 REFERENCES access.studies_enrollment_outcome(database_login,account_id,command_version,operation_id));
CREATE FUNCTION access.studies_registration_ready() RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
 SELECT EXISTS(SELECT 1 FROM access.applications a JOIN access.permissions p ON p.app_id=a.app_id
 WHERE a.app_id='scribeswell' AND a.enabled AND p.permission='scribeswell.studies.use' AND p.scope_kind='account')
$f$;
CREATE FUNCTION access.studies_executor() RETURNS uuid LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
 SELECT executor_actor_id FROM access.studies_runtime_principal WHERE database_login=session_user AND enabled
$f$;
CREATE FUNCTION access.studies_evidence_immutable() RETURNS trigger LANGUAGE plpgsql
 SET search_path=pg_catalog,pg_temp AS $f$
BEGIN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_studies_evidence_immutable';END $f$;
CREATE FUNCTION access.guard_studies_grant() RETURNS trigger LANGUAGE plpgsql
 SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF TG_OP='INSERT' THEN
  IF current_user<>'access_studies_owner' OR access.studies_executor() IS DISTINCT FROM NEW.executor_actor_id
  OR NEW.account_id::text IS DISTINCT FROM current_setting('app.account_id',true) OR NEW.revoked_at IS NOT NULL THEN
   RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_studies_owner_required'; END IF;
  NEW.created_at:=statement_timestamp();RETURN NEW;
 END IF;
 IF TG_OP='UPDATE' AND current_user='access_migrator' AND OLD.revoked_at IS NULL AND NEW.revoked_at IS NOT NULL
 AND (to_jsonb(NEW)-ARRAY['revoked_at','revoked_by','revocation_operation_id'])=(to_jsonb(OLD)-ARRAY['revoked_at','revoked_by','revocation_operation_id']) THEN
  NEW.revoked_at:=statement_timestamp();RETURN NEW;END IF;
 RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_studies_grant_retained';
END $f$;
CREATE TRIGGER studies_grant_guard BEFORE INSERT OR UPDATE OR DELETE ON access.studies_account_grant
 FOR EACH ROW EXECUTE FUNCTION access.guard_studies_grant();
CREATE TRIGGER studies_grant_retention BEFORE TRUNCATE ON access.studies_account_grant
 FOR EACH STATEMENT EXECUTE FUNCTION access.studies_evidence_immutable();
CREATE FUNCTION access.enroll_studies_account(p_operation uuid,p_actor uuid)
 RETURNS TABLE(disposition text,account_id uuid,actor_id uuid)
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE account uuid;executor uuid; existing access.studies_account_grant;
 saved access.studies_enrollment_outcome; result text;
BEGIN
 IF session_user<>'access_studies_runtime' OR current_setting('app.context_kind',true) IS DISTINCT FROM 'user'
 OR current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_actor IS NULL
 OR p_operation='00000000-0000-0000-0000-000000000000' OR p_actor='00000000-0000-0000-0000-000000000000' THEN RETURN;END IF;
 account:=nullif(current_setting('app.account_id',true),'')::uuid;executor:=access.studies_executor();
 IF account IS NULL OR executor IS NULL THEN RETURN;END IF;
 -- One fixed-capability lock serializes enrollment, receipts and controlled revoke.
 PERFORM pg_advisory_xact_lock(hashtextextended('access:studies-account:v1:'||account::text,0));
 IF executor IS DISTINCT FROM access.studies_executor() OR NOT access.studies_registration_ready() THEN RETURN;END IF;
 SELECT * INTO existing FROM access.studies_account_grant g WHERE g.account_id=account FOR UPDATE;
 IF FOUND THEN
  IF existing.revoked_at IS NOT NULL OR existing.actor_id<>p_actor THEN RETURN;END IF;
  result:='unchanged';
 ELSE result:='created';END IF;
 SELECT * INTO saved FROM access.studies_enrollment_outcome o WHERE o.database_login=session_user
 AND o.account_id=account AND o.command_version=1 AND o.operation_id=p_operation;
 IF FOUND THEN
  IF existing.account_id IS NULL OR saved.actor_id<>p_actor THEN RETURN; END IF;
  RETURN QUERY SELECT saved.disposition,account,p_actor;RETURN;
 END IF;
 IF result='created' THEN
  INSERT INTO access.studies_account_grant(account_id,actor_id,executor_actor_id,initiator_actor_id)
  VALUES(account,p_actor,executor,p_actor);
 END IF;
 INSERT INTO access.studies_enrollment_outcome(database_login,account_id,operation_id,actor_id,disposition,executor_actor_id,initiator_actor_id)
 VALUES(session_user,account,p_operation,p_actor,result,executor,p_actor);
 IF result='created' THEN
  INSERT INTO access.studies_assignment_event(account_id,actor_id,executor_actor_id,initiator_actor_id,database_login,operation_id)
  VALUES(account,p_actor,executor,p_actor,session_user,p_operation);
 END IF;
 RETURN QUERY SELECT result,account,p_actor;
END $f$;
CREATE FUNCTION access.check_studies_permission(p_actor uuid) RETURNS TABLE(account_id uuid,actor_id uuid)
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT g.account_id,g.actor_id FROM access.studies_account_grant g
 WHERE session_user='access_studies_runtime' AND current_setting('app.context_kind',true)='user'
 AND g.account_id::text=current_setting('app.account_id',true) AND g.actor_id=p_actor AND g.revoked_at IS NULL
 AND access.studies_executor() IS NOT NULL AND access.studies_registration_ready()
$f$;
'''

SQL+=r'''
CREATE FUNCTION access.guard_studies_principal() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF current_user<>'access_migrator' OR TG_OP IN ('DELETE','TRUNCATE') THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='studies_principal_owner_required'; END IF;
 IF NEW.operation_id IS NULL OR NEW.operation_id='00000000-0000-0000-0000-000000000000' THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='studies_principal_operation_required'; END IF;
 IF TG_OP='INSERT' THEN
  NEW.updated_by:=NEW.created_by;NEW.created_at:=statement_timestamp();NEW.updated_at:=NEW.created_at;NEW.revision:=1;
 ELSE
  IF NEW.database_login<>OLD.database_login OR NEW.executor_actor_id<>OLD.executor_actor_id
  OR NEW.created_by<>OLD.created_by OR NEW.created_at<>OLD.created_at OR NEW.operation_id=OLD.operation_id THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='studies_principal_binding_immutable'; END IF;
  NEW.revision:=OLD.revision+1;NEW.updated_at:=statement_timestamp();
 END IF;RETURN NEW;
END $f$;
CREATE TRIGGER studies_principal_guard BEFORE INSERT OR UPDATE OR DELETE ON access.studies_runtime_principal
 FOR EACH ROW EXECUTE FUNCTION access.guard_studies_principal();
CREATE TRIGGER studies_principal_retention BEFORE TRUNCATE ON access.studies_runtime_principal
 FOR EACH STATEMENT EXECUTE FUNCTION access.guard_studies_principal();
'''

def upgrade():
    from access_baseline import verify_catalog
    from studies_migration_support import verify_roles,strip_acl,secure_tables,transfer_functions
    connection=op.get_bind();verify_catalog(connection,'access_0015');verify_roles(connection,'access')
    if not connection.exec_driver_sql("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity' AND p.proname='prepare_studies_account' AND pg_get_userbyid(p.proowner)='identity_studies_owner')").scalar_one():
        raise RuntimeError('studies_identity_migration_required')
    connection.exec_driver_sql(SQL,execution_options={'no_parameters':True})
    strip_acl(connection,'access',FUNCTIONS)
    secure_tables(connection,'access',TABLES,'access_studies_owner','studies_evidence_immutable')
    # The grant has its own controlled retained-state trigger rather than immutable update guard.
    connection.exec_driver_sql('DROP TRIGGER studies_immutable ON access.studies_account_grant')
    connection.exec_driver_sql('''GRANT SELECT ON access.studies_runtime_principal TO access_studies_owner;
GRANT SELECT,INSERT ON access.studies_account_grant,access.studies_enrollment_outcome,access.studies_assignment_event TO access_studies_owner;
GRANT UPDATE(account_id) ON access.studies_account_grant TO access_studies_owner;
GRANT EXECUTE ON FUNCTION access.studies_registration_ready() TO access_studies_owner;
CREATE POLICY studies_principal ON access.studies_runtime_principal FOR SELECT TO access_studies_owner USING(database_login=session_user);
GRANT EXECUTE ON FUNCTION access.enroll_studies_account(uuid,uuid),access.check_studies_permission(uuid) TO access_studies_runtime;''')
    for table in TABLES[1:]:
        connection.exec_driver_sql('CREATE POLICY studies_account_scope ON access.'+table+" TO access_studies_owner USING(account_id::text=current_setting('app.account_id',true)) WITH CHECK(account_id::text=current_setting('app.account_id',true))")
    transfer_functions(connection,'access','access_studies_owner',('studies_executor()','enroll_studies_account(uuid,uuid)','check_studies_permission(uuid)'))

def downgrade():raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
