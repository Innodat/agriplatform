"""Current-account Studies attribution setup, separate from operator authority."""
from alembic import op
revision='identity_0021'
down_revision='identity_0020'
branch_labels=None
depends_on=None

SQL=r'''
GRANT USAGE ON SCHEMA identity,auth TO identity_studies_owner;
GRANT USAGE ON SCHEMA identity TO identity_studies_reader_runtime,identity_studies_setup_runtime;
GRANT SELECT(id,username,deleted_at,is_system,actor_key) ON identity.users TO identity_studies_owner;
GRANT SELECT ON identity.actor,identity.account_actor TO identity_studies_owner;
GRANT INSERT ON identity.actor,identity.account_actor TO identity_studies_owner;
GRANT EXECUTE ON FUNCTION identity.authorize(identity.app_permission) TO identity_studies_owner;
CREATE POLICY studies_profile ON identity.users FOR SELECT TO identity_studies_owner
 USING(current_setting('app.context_kind',true)='user' AND id::text=current_setting('app.account_id',true));
CREATE POLICY studies_profile_bound ON identity.users AS RESTRICTIVE FOR SELECT TO identity_studies_owner
 USING(current_setting('app.context_kind',true)='user' AND id::text=current_setting('app.account_id',true));
CREATE TABLE identity.studies_runtime_principal(
 database_login name PRIMARY KEY CHECK(database_login='identity_studies_setup_runtime'),
 executor_actor_id uuid NOT NULL REFERENCES identity.actor(id),enabled boolean NOT NULL DEFAULT false,
 created_by uuid NOT NULL REFERENCES identity.actor(id),created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 updated_by uuid NOT NULL REFERENCES identity.actor(id),updated_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 revision bigint NOT NULL DEFAULT 1 CHECK(revision>0),operation_id uuid NOT NULL);
CREATE TABLE identity.studies_setup_outcome(
 database_login name NOT NULL CHECK(database_login='identity_studies_setup_runtime'),
 account_id uuid NOT NULL CHECK(account_id<>'00000000-0000-0000-0000-000000000000'),
 operation_id uuid NOT NULL CHECK(operation_id<>'00000000-0000-0000-0000-000000000000'),
 command_version integer NOT NULL DEFAULT 1 CHECK(command_version=1),
 actor_id uuid NOT NULL REFERENCES identity.actor(id),
 disposition text NOT NULL CHECK(disposition IN ('created','unchanged')),
 executor_actor_id uuid NOT NULL REFERENCES identity.actor(id),
 initiator_actor_id uuid NOT NULL REFERENCES identity.actor(id),
 committed_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 PRIMARY KEY(database_login,account_id,operation_id),CHECK(initiator_actor_id=actor_id));
CREATE TABLE identity.studies_setup_event(
 event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),event_type text NOT NULL DEFAULT 'identity.studies_account_prepared'
 CHECK(event_type='identity.studies_account_prepared'),event_version integer NOT NULL DEFAULT 1 CHECK(event_version=1),
 account_id uuid PRIMARY KEY_EXAMPLE,
 actor_id uuid NOT NULL REFERENCES identity.actor(id),executor_actor_id uuid NOT NULL REFERENCES identity.actor(id),
 initiator_actor_id uuid NOT NULL REFERENCES identity.actor(id),
 operation_id uuid NOT NULL,database_login name NOT NULL,
 created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 UNIQUE(account_id),CHECK(initiator_actor_id=actor_id),
 FOREIGN KEY(database_login,account_id,operation_id) REFERENCES identity.studies_setup_outcome(database_login,account_id,operation_id));
CREATE FUNCTION identity.studies_executor() RETURNS uuid LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
 SELECT p.executor_actor_id FROM identity.studies_runtime_principal p JOIN identity.actor a ON a.id=p.executor_actor_id
 WHERE p.database_login=session_user AND p.enabled AND a.kind='service' AND a.actor_key IS NOT NULL
$f$;
CREATE FUNCTION identity.studies_account_evidence() RETURNS TABLE(account_id uuid,actor_id uuid)
 LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE account uuid; mapped uuid; auth_state record;
BEGIN
 IF session_user NOT IN ('identity_studies_reader_runtime','identity_studies_setup_runtime')
 OR current_setting('app.context_kind',true) IS DISTINCT FROM 'user' THEN RETURN; END IF;
 account:=nullif(current_setting('app.account_id',true),'')::uuid;
 SELECT a.deleted_at,a.email_confirmed_at,a.banned_until,a.is_anonymous INTO auth_state FROM auth.users a WHERE a.id=account;
 IF NOT FOUND OR auth_state.deleted_at IS NOT NULL OR auth_state.is_anonymous IS TRUE
 OR coalesce(auth_state.banned_until,'-infinity')>clock_timestamp() THEN
  RAISE EXCEPTION USING ERRCODE='IS003',MESSAGE='identity_studies_account_ineligible'; END IF;
 IF auth_state.email_confirmed_at IS NULL THEN
  RAISE EXCEPTION USING ERRCODE='IS006',MESSAGE='identity_studies_verification_required'; END IF;
 IF account IS NULL OR NOT EXISTS(SELECT 1 FROM identity.users u WHERE u.id=account AND u.deleted_at IS NULL
 AND u.is_system IS NOT TRUE AND u.actor_key IS NULL) THEN RETURN; END IF;
 SELECT m.actor_id INTO mapped FROM identity.account_actor m JOIN identity.actor a ON a.id=m.actor_id
 WHERE m.account_id=account AND m.actor_kind='account' AND a.kind='account' AND a.actor_key IS NULL;
 IF mapped IS NULL AND (EXISTS(SELECT 1 FROM identity.account_actor m WHERE m.account_id=account)
 OR EXISTS(SELECT 1 FROM identity.actor a WHERE a.id=account)) THEN RETURN; END IF;
 RETURN QUERY SELECT account,mapped;
END $f$;
CREATE FUNCTION identity.prepare_studies_account(p_operation uuid) RETURNS TABLE(account_id uuid,actor_id uuid)
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE account uuid; actor uuid; executor uuid; observed timestamptz; label text;
 saved identity.studies_setup_outcome; disposition text; auth_state record;
BEGIN
 IF session_user<>'identity_studies_setup_runtime' OR current_setting('app.context_kind',true) IS DISTINCT FROM 'user'
 OR current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL
 OR p_operation='00000000-0000-0000-0000-000000000000' THEN RETURN; END IF;
 account:=nullif(current_setting('app.account_id',true),'')::uuid;executor:=identity.studies_executor();
 IF account IS NULL OR executor IS NULL THEN RETURN; END IF;
 observed:=clock_timestamp();
 SELECT a.deleted_at,a.email_confirmed_at,a.banned_until,a.is_anonymous INTO auth_state FROM auth.users a WHERE a.id=account;
 IF NOT FOUND OR auth_state.deleted_at IS NOT NULL OR auth_state.is_anonymous IS TRUE
 OR coalesce(auth_state.banned_until,'-infinity')>clock_timestamp() THEN
  RAISE EXCEPTION USING ERRCODE='IS003',MESSAGE='identity_studies_account_ineligible'; END IF;
 IF auth_state.email_confirmed_at IS NULL THEN
  RAISE EXCEPTION USING ERRCODE='IS006',MESSAGE='identity_studies_verification_required'; END IF;
 -- Coordinate with the delivered operator path, not a second actor lock namespace.
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:account-actor:v1:'||account::text));
 -- READ COMMITTED: refresh Auth after a concurrent lock holder can commit.
 SELECT a.deleted_at,a.email_confirmed_at,a.banned_until,a.is_anonymous INTO auth_state FROM auth.users a WHERE a.id=account;
 IF NOT FOUND OR auth_state.deleted_at IS NOT NULL OR auth_state.is_anonymous IS TRUE
 OR coalesce(auth_state.banned_until,'-infinity')>clock_timestamp() THEN
  RAISE EXCEPTION USING ERRCODE='IS003',MESSAGE='identity_studies_account_ineligible'; END IF;
 IF auth_state.email_confirmed_at IS NULL THEN
  RAISE EXCEPTION USING ERRCODE='IS006',MESSAGE='identity_studies_verification_required'; END IF;
 SELECT u.username INTO label FROM identity.users u WHERE u.id=account AND u.deleted_at IS NULL
 AND u.is_system IS NOT TRUE AND u.actor_key IS NULL;
 IF NOT FOUND OR executor IS DISTINCT FROM identity.studies_executor()
 OR clock_timestamp()-observed>interval '5 seconds' THEN RETURN; END IF;
 SELECT m.actor_id INTO actor FROM identity.account_actor m JOIN identity.actor a ON a.id=m.actor_id
 WHERE m.account_id=account AND m.actor_kind='account' AND a.kind='account' AND a.actor_key IS NULL;
 IF actor IS NULL THEN
  IF EXISTS(SELECT 1 FROM identity.account_actor m WHERE m.account_id=account) THEN RETURN; END IF;
  actor:=account;
  IF label IS NULL OR length(btrim(label))=0 THEN label:='Account '||account::text; END IF;
  PERFORM pg_advisory_xact_lock(identity.command_lock('identity:actor-id:v1:'||actor::text));
 SELECT a.deleted_at,a.email_confirmed_at,a.banned_until,a.is_anonymous INTO auth_state FROM auth.users a WHERE a.id=account;
 IF NOT FOUND OR auth_state.deleted_at IS NOT NULL OR auth_state.is_anonymous IS TRUE
 OR coalesce(auth_state.banned_until,'-infinity')>clock_timestamp() THEN
  RAISE EXCEPTION USING ERRCODE='IS003',MESSAGE='identity_studies_account_ineligible'; END IF;
 IF auth_state.email_confirmed_at IS NULL THEN
  RAISE EXCEPTION USING ERRCODE='IS006',MESSAGE='identity_studies_verification_required'; END IF;
  IF clock_timestamp()-observed>interval '5 seconds' OR NOT EXISTS(SELECT 1 FROM identity.users u WHERE u.id=account AND u.deleted_at IS NULL AND u.is_system IS NOT TRUE AND u.actor_key IS NULL) THEN RETURN; END IF;
  IF EXISTS(SELECT 1 FROM identity.actor a WHERE a.id=actor)
   OR EXISTS(SELECT 1 FROM identity.account_actor m WHERE m.actor_id=actor)
   OR label IS NULL OR length(btrim(label))=0 OR char_length(label)>200 THEN RETURN; END IF;
  INSERT INTO identity.actor(id,kind,display_name,created_by,updated_by) VALUES(actor,'account',label,executor,executor);
  INSERT INTO identity.account_actor(account_id,actor_id,actor_kind,created_by) VALUES(account,actor,'account',executor);
  disposition:='created';
 ELSE disposition:='unchanged'; END IF;
 IF clock_timestamp()-observed>interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='57014',MESSAGE='identity_setup_expired'; END IF;
 SELECT * INTO saved FROM identity.studies_setup_outcome o WHERE o.database_login=session_user
 AND o.account_id=account AND o.operation_id=p_operation;
 IF FOUND THEN
  IF saved.actor_id<>actor THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_setup_binding_conflict'; END IF;
 ELSE
  INSERT INTO identity.studies_setup_outcome(database_login,account_id,operation_id,actor_id,disposition,executor_actor_id,initiator_actor_id)
   VALUES(session_user,account,p_operation,actor,disposition,executor,actor);
  IF disposition='created' THEN
   INSERT INTO identity.studies_setup_event(account_id,actor_id,executor_actor_id,initiator_actor_id,operation_id,database_login)
   VALUES(account,actor,executor,actor,p_operation,session_user);
  END IF;
 END IF;
 RETURN QUERY SELECT account,actor;
END $f$;
CREATE FUNCTION identity.studies_evidence_immutable() RETURNS trigger LANGUAGE plpgsql
 SET search_path=pg_catalog,pg_temp AS $f$
BEGIN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_studies_evidence_immutable'; END $f$;
'''.replace('account_id uuid PRIMARY KEY_EXAMPLE','account_id uuid NOT NULL')


SQL+=r'''
CREATE FUNCTION identity.guard_studies_principal() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF current_user<>'identity_migrator' OR TG_OP IN ('DELETE','TRUNCATE') THEN
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
CREATE TRIGGER studies_principal_guard BEFORE INSERT OR UPDATE OR DELETE ON identity.studies_runtime_principal
 FOR EACH ROW EXECUTE FUNCTION identity.guard_studies_principal();
CREATE TRIGGER studies_principal_retention BEFORE TRUNCATE ON identity.studies_runtime_principal
 FOR EACH STATEMENT EXECUTE FUNCTION identity.guard_studies_principal();
'''

def upgrade():
    from identity_baseline import verify_catalog
    from studies_migration_support import verify_roles,strip_acl,secure_tables,transfer_functions
    connection=op.get_bind()
    verify_catalog(connection,'check_reader_bridge')
    verify_roles(connection,'identity')
    connection.exec_driver_sql(SQL,execution_options={'no_parameters':True})
    # The preceding verified old head pins these exact trigger bodies. Only add a
    # separately authenticated runtime owner branch; operator behavior is retained.
    for routine in ('guard_actor','guard_account_actor'):
        definition=connection.exec_driver_sql("SELECT pg_get_functiondef('identity."+routine+"()'::regprocedure)").scalar_one()
        branch="""
 IF current_user='identity_studies_owner' THEN
  IF TG_OP<>'INSERT' OR identity.studies_executor() IS NULL THEN
   RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_studies_owner_required'; END IF;
 """
        if routine=='guard_actor':
            branch+="""IF NEW.kind<>'account' OR NEW.actor_key IS NOT NULL OR NEW.id::text IS DISTINCT FROM current_setting('app.account_id',true) THEN
 RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_studies_binding_invalid'; END IF;
 NEW.created_by:=identity.studies_executor(); NEW.updated_by:=NEW.created_by;
 NEW.created_at:=statement_timestamp();NEW.updated_at:=NEW.created_at;RETURN NEW;
 END IF;
"""
        else:
            branch+="""IF NEW.account_id::text IS DISTINCT FROM current_setting('app.account_id',true) OR NEW.actor_id<>NEW.account_id THEN
 RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_studies_binding_invalid'; END IF;
 NEW.created_by:=identity.studies_executor();NEW.created_at:=statement_timestamp();RETURN NEW;
 END IF;
"""
        definition=definition.replace('BEGIN\n','BEGIN\n'+branch,1)
        connection.exec_driver_sql(definition,execution_options={'no_parameters':True})
    strip_acl(connection,'identity',('studies_executor','studies_account_evidence','prepare_studies_account','studies_evidence_immutable','guard_studies_principal'))
    secure_tables(connection,'identity',('studies_runtime_principal','studies_setup_outcome','studies_setup_event'),'identity_studies_owner','studies_evidence_immutable')
    connection.exec_driver_sql('''GRANT SELECT ON identity.studies_runtime_principal TO identity_studies_owner;
GRANT SELECT,INSERT ON identity.studies_setup_outcome,identity.studies_setup_event TO identity_studies_owner;
CREATE POLICY studies_principal_read ON identity.studies_runtime_principal FOR SELECT TO identity_studies_owner USING(database_login=session_user);
CREATE POLICY studies_outcome_scope ON identity.studies_setup_outcome TO identity_studies_owner USING(account_id::text=current_setting('app.account_id',true) AND database_login=session_user) WITH CHECK(account_id::text=current_setting('app.account_id',true) AND database_login=session_user);
CREATE POLICY studies_event_scope ON identity.studies_setup_event TO identity_studies_owner USING(account_id::text=current_setting('app.account_id',true) AND database_login=session_user) WITH CHECK(account_id::text=current_setting('app.account_id',true) AND database_login=session_user);
GRANT EXECUTE ON FUNCTION identity.studies_account_evidence() TO identity_studies_reader_runtime;
GRANT EXECUTE ON FUNCTION identity.prepare_studies_account(uuid) TO identity_studies_setup_runtime;
''')
    connection.exec_driver_sql('GRANT EXECUTE ON FUNCTION identity.command_lock(text) TO identity_studies_owner')
    transfer_functions(connection,'identity','identity_studies_owner',('studies_executor()','studies_account_evidence()','prepare_studies_account(uuid)'))

def downgrade():raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
