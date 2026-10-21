"""Protected application availability changes and exact mutation evidence."""
from alembic import op
revision = 'access_0007'
down_revision = 'access_0006'
branch_labels = None
depends_on = None
SQL = r'''
ALTER TABLE access.operator_authorities DROP CONSTRAINT operator_authorities_command_check;
ALTER TABLE access.operator_authorities ADD CONSTRAINT operator_authorities_command_check CHECK(command IN ('application.register','permission.register','entry_permission.register','application.set_enabled'));
ALTER TABLE access.operation_outcome DROP CONSTRAINT operation_outcome_command_type_check;
ALTER TABLE access.operation_outcome ADD CONSTRAINT operation_outcome_command_type_check CHECK(command_type IN ('application.register','permission.register','entry_permission.register','application.set_enabled'));
ALTER TABLE access.business_event DROP CONSTRAINT business_event_event_type_check;
ALTER TABLE access.business_event ADD CONSTRAINT business_event_event_type_check CHECK(event_type IN ('access.application_registered','access.permission_registered','access.entry_permission_registered','access.application_availability_changed'));
DROP TRIGGER registry_storage_immutable ON access.applications;
CREATE TRIGGER registry_storage_immutable BEFORE DELETE OR TRUNCATE ON access.applications FOR EACH STATEMENT EXECUTE FUNCTION access.registry_storage_immutable();
CREATE OR REPLACE FUNCTION access.application_enablement_authority(p_app text) RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT p.executor_actor_id FROM access.operator_principals p
 JOIN access.operator_authorities a ON a.database_login=p.database_login
 WHERE p.database_login=session_user AND p.enabled AND a.enabled
 AND a.command='application.set_enabled' AND a.scope_kind='platform' AND a.org_id IS NULL AND a.target_account_id IS NULL
 AND (a.application_id IS NULL OR a.application_id=p_app)
 ORDER BY a.id LIMIT 1
$f$;
CREATE OR REPLACE FUNCTION access.guard_command_evidence() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
DECLARE saved access.operation_outcome; app access.applications; executor uuid; event uuid; perm access.permissions; entry access.entry_permissions;
BEGIN
 IF TG_OP<>'INSERT' THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_evidence_immutable'; END IF;
 IF current_user<>'access_command_owner' THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_command_owner_required'; END IF;
 IF TG_TABLE_NAME='operation_outcome' THEN
  IF NEW.command_type='application.set_enabled' THEN
   executor:=access.application_enablement_authority(NEW.result->'target'->>'app_id');
   SELECT * INTO app FROM access.applications a WHERE a.app_id=NEW.result->'target'->>'app_id';
   IF executor IS NULL OR executor IS DISTINCT FROM NEW.executor_actor_id OR app.app_id IS NULL
    OR NEW.result IS DISTINCT FROM jsonb_build_object('target',jsonb_build_object('app_id',app.app_id),'disposition',NEW.result->>'disposition','revision',app.revision::text,'event_id',NEW.result->'event_id')
    OR NEW.result->>'disposition' IS NULL OR NEW.result->>'disposition' NOT IN ('changed','unchanged') THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_enablement_result_invalid'; END IF;
   IF NEW.result->>'disposition'='changed' THEN
    event:=(NEW.result->>'event_id')::uuid;
    IF event IS NULL OR event='00000000-0000-0000-0000-000000000000'::uuid OR app.revision<2
     OR app.updated_by<>executor OR app.updated_at<>statement_timestamp() THEN
     RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_changed_result_invalid'; END IF;
   ELSIF NEW.result->>'event_id' IS NOT NULL THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_unchanged_event_invalid'; END IF;
  ELSIF NEW.command_type='entry_permission.register' THEN
   executor:=access.entry_permission_operator_authority(NEW.result->'target'->>'app_id');
   SELECT * INTO entry FROM access.entry_permissions e WHERE e.app_id=NEW.result->'target'->>'app_id' AND e.permission=NEW.result->'target'->>'permission';
   IF executor IS NULL OR executor IS DISTINCT FROM NEW.executor_actor_id OR entry.app_id IS NULL
    OR NEW.result IS DISTINCT FROM jsonb_build_object('target',jsonb_build_object('app_id',entry.app_id,'permission',entry.permission),'disposition',NEW.result->>'disposition','revision',NULL,'event_id',NEW.result->'event_id')
    OR NEW.result->>'disposition' IS NULL OR NEW.result->>'disposition' NOT IN ('created','unchanged') THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_entry_result_invalid'; END IF;
   IF NEW.result->>'disposition'='created' THEN
    event:=(NEW.result->>'event_id')::uuid;
    IF event IS NULL OR event='00000000-0000-0000-0000-000000000000'::uuid OR entry.created_by<>executor OR entry.created_at<>statement_timestamp() THEN
     RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_entry_created_result_invalid'; END IF;
   ELSIF NEW.result->>'event_id' IS NOT NULL THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_unchanged_event_invalid'; END IF;
  ELSIF NEW.command_type='permission.register' THEN
   executor:=access.permission_operator_authority(NEW.result->'target'->>'app_id');
   SELECT * INTO perm FROM access.permissions p WHERE p.permission=NEW.result->'target'->>'permission';
   IF executor IS NULL OR executor IS DISTINCT FROM NEW.executor_actor_id OR perm.permission IS NULL
    OR NEW.result IS DISTINCT FROM jsonb_build_object('target',jsonb_build_object('app_id',perm.app_id,'permission',perm.permission),'disposition',NEW.result->>'disposition','revision',NULL,'event_id',NEW.result->'event_id')
    OR NEW.result->>'disposition' IS NULL OR NEW.result->>'disposition' NOT IN ('created','unchanged') THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_permission_result_invalid'; END IF;
   IF NEW.result->>'disposition'='created' THEN
    event:=(NEW.result->>'event_id')::uuid;
    IF event IS NULL OR event='00000000-0000-0000-0000-000000000000'::uuid OR perm.created_by<>executor OR perm.created_at<>statement_timestamp() THEN
     RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_permission_created_result_invalid'; END IF;
   ELSIF NEW.result->>'event_id' IS NOT NULL THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_unchanged_event_invalid'; END IF;
  ELSE
  executor:=access.current_operator_authority(NEW.result->'target'->>'app_id');
  SELECT * INTO app FROM access.applications a WHERE a.app_id=NEW.result->'target'->>'app_id';
  IF executor IS NULL OR executor IS DISTINCT FROM NEW.executor_actor_id OR app.app_id IS NULL
   OR NEW.result IS DISTINCT FROM jsonb_build_object('target',jsonb_build_object('app_id',app.app_id),'disposition',NEW.result->>'disposition','revision',app.revision::text,'event_id',NEW.result->'event_id')
   OR NEW.result->>'disposition' IS NULL OR NEW.result->>'disposition' NOT IN ('created','unchanged') THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_result_invalid'; END IF;
  IF NEW.result->>'disposition'='created' THEN
   event:=(NEW.result->>'event_id')::uuid;
   IF event IS NULL OR event='00000000-0000-0000-0000-000000000000'::uuid OR app.enabled OR app.revision<>1
    OR app.created_by<>executor OR app.updated_by<>executor OR app.created_at<>statement_timestamp() OR app.updated_at<>app.created_at THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_created_result_invalid'; END IF;
  ELSIF NEW.result->>'event_id' IS NOT NULL THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_unchanged_event_invalid';
  END IF;
  END IF;
  NEW.committed_at:=statement_timestamp();
 ELSE
  SELECT * INTO saved FROM access.operation_outcome o WHERE o.id=NEW.outcome_id;
  IF saved.id IS NULL OR NEW.event_id IS DISTINCT FROM (saved.result->>'event_id')::uuid
   OR NEW.executor_actor_id<>saved.executor_actor_id OR NEW.operation_id<>saved.operation_id
   OR NEW.target IS DISTINCT FROM saved.result->'target' OR saved.result->>'disposition' IS DISTINCT FROM (CASE WHEN saved.command_type='application.set_enabled' THEN 'changed' ELSE 'created' END)
   OR NEW.scope_kind IS DISTINCT FROM saved.scope_kind OR NEW.scope_id IS DISTINCT FROM saved.scope_id
   OR NEW.event_type IS DISTINCT FROM (CASE saved.command_type WHEN 'application.set_enabled' THEN 'access.application_availability_changed' WHEN 'application.register' THEN 'access.application_registered' WHEN 'permission.register' THEN 'access.permission_registered' WHEN 'entry_permission.register' THEN 'access.entry_permission_registered' END)
   OR NEW.transition IS DISTINCT FROM (CASE saved.command_type WHEN 'application.set_enabled' THEN (SELECT jsonb_build_object('before',jsonb_build_object('enabled',NOT a.enabled,'revision',(a.revision-1)::text),'after',jsonb_build_object('enabled',a.enabled,'revision',a.revision::text)) FROM access.applications a WHERE a.app_id=saved.result->'target'->>'app_id' AND a.revision::text=saved.result->>'revision' AND a.updated_by=saved.executor_actor_id AND a.updated_at=saved.committed_at) WHEN 'application.register' THEN jsonb_build_object('enabled',false,'revision','1') WHEN 'entry_permission.register' THEN '{}'::jsonb ELSE (SELECT jsonb_build_object('scope_kind',p.scope_kind) FROM access.permissions p WHERE p.permission=saved.result->'target'->>'permission' AND p.app_id=saved.result->'target'->>'app_id') END) THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_event_invalid'; END IF;
  NEW.created_at:=saved.committed_at;
 END IF;
 RETURN NEW;
END $f$;
CREATE OR REPLACE FUNCTION access.guard_application_update() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid;
BEGIN
 IF current_user<>'access_command_owner' THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_command_owner_required'; END IF;
 IF TG_LEVEL='STATEMENT' THEN RETURN NULL; END IF;
 executor:=access.application_enablement_authority(OLD.app_id);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_command_owner_required'; END IF;
 IF (to_jsonb(NEW)-'enabled') IS DISTINCT FROM (to_jsonb(OLD)-'enabled') OR NEW.enabled IS NOT DISTINCT FROM OLD.enabled OR OLD.revision=9223372036854775807 THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_application_update_invalid'; END IF;
 NEW.revision:=OLD.revision+1; NEW.updated_by:=executor; NEW.updated_at:=statement_timestamp();
 RETURN NEW;
END $f$;
CREATE TRIGGER application_update_statement BEFORE UPDATE ON access.applications FOR EACH STATEMENT EXECUTE FUNCTION access.guard_application_update();
CREATE TRIGGER application_update_guard BEFORE UPDATE ON access.applications FOR EACH ROW EXECUTE FUNCTION access.guard_application_update();

GRANT CREATE ON SCHEMA access TO access_command_owner,access_operator_authority_owner;
SET LOCAL ROLE access_command_owner;
CREATE OR REPLACE FUNCTION access.require_command_event() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF NEW.result->>'disposition' IN ('created','changed') AND NOT EXISTS(SELECT 1 FROM access.business_event e WHERE e.outcome_id=NEW.id AND e.event_id=(NEW.result->>'event_id')::uuid) THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_required_event_missing'; END IF;
 RETURN NULL;
END $f$;
CREATE OR REPLACE FUNCTION access.require_application_change() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM access.operation_outcome o JOIN access.business_event e ON e.outcome_id=o.id
  WHERE o.command_type='application.set_enabled' AND o.scope_kind='platform' AND o.scope_id IS NULL
  AND o.result=jsonb_build_object('target',jsonb_build_object('app_id',NEW.app_id),'disposition','changed','revision',NEW.revision::text,'event_id',e.event_id)
  AND o.executor_actor_id=NEW.updated_by AND o.committed_at=NEW.updated_at
  AND e.transition=jsonb_build_object('before',jsonb_build_object('enabled',OLD.enabled,'revision',OLD.revision::text),'after',jsonb_build_object('enabled',NEW.enabled,'revision',NEW.revision::text))
  AND e.event_type='access.application_availability_changed' AND e.created_at=NEW.updated_at) THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_required_change_missing'; END IF;
 RETURN NULL;
END $f$;
CREATE OR REPLACE FUNCTION access.set_application_enabled(p_operation uuid,p_app text,p_enabled boolean,p_revision text,p_reason text,p_evidence text,p_canonical bytea)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; saved access.operation_outcome; app access.applications; expected jsonb; doc jsonb; lock_document text; event uuid; outcome_id uuid; disposition text; previous access.applications;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid
 OR p_app IS NULL OR p_app COLLATE "C" !~ '^[a-z][a-z0-9_]{1,63}$' OR p_reason IS NULL OR p_reason NOT IN ('initial_setup','synthetic_fixture','identity_adoption','access_change','setup_correction')
 OR (p_evidence IS NOT NULL AND (p_evidence COLLATE "C" !~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$' OR position('://' in p_evidence)>0))
 OR p_enabled IS NULL OR p_revision IS NULL OR p_revision COLLATE "C" !~ '^[1-9][0-9]{0,18}$'
 OR (length(p_revision)=19 AND p_revision COLLATE "C">'9223372036854775807')
 OR p_canonical IS NULL OR octet_length(p_canonical)>65536 THEN
  RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 expected:=jsonb_build_object('schema_version',1,'command','application.set_enabled','operation_id',p_operation::text,'scope',jsonb_build_object('kind','platform'),
 'payload',jsonb_build_object('app_id',p_app,'enabled',p_enabled,'expected_revision',p_revision),'reason_code',p_reason,'evidence_ref',p_evidence);
 BEGIN doc:=convert_from(p_canonical,'UTF8')::jsonb; EXCEPTION WHEN OTHERS THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END;
 -- This fixed ASCII envelope has no numbers except 1 and no unbounded JSON values.
 IF doc IS DISTINCT FROM expected OR convert_from(p_canonical,'UTF8') IS DISTINCT FROM
  '{"command":"application.set_enabled","evidence_ref":'||coalesce(to_json(p_evidence)::text,'null')||',"operation_id":'||to_json(p_operation::text)::text||',"payload":{"app_id":'||to_json(p_app)::text||',"enabled":'||to_json(p_enabled)::text||',"expected_revision":'||to_json(p_revision)::text||'},"reason_code":'||to_json(p_reason)::text||',"schema_version":1,"scope":{"kind":"platform"}}' THEN
  RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 executor:=access.application_enablement_authority(p_app);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"application.set_enabled","lock_version":1,"operation_id":'||to_json(p_operation::text)::text||',"owner_schema":"access","scope_id":null,"scope_kind":"platform"}';
 BEGIN PERFORM pg_advisory_xact_lock(access.command_lock(lock_document)); EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='AC001',MESSAGE='access_operation_busy'; END;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM access.application_enablement_authority(p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 SELECT * INTO saved FROM access.operation_outcome o WHERE o.scope_kind='platform' AND o.scope_id IS NULL AND o.command_type='application.set_enabled' AND o.executor_actor_id=executor AND o.operation_id=p_operation;
 IF FOUND THEN
  IF saved.fingerprint<>sha256(p_canonical) THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
  RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at; RETURN;
 END IF;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:application:v1:'||p_app));
 IF executor IS DISTINCT FROM access.application_enablement_authority(p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 SELECT * INTO app FROM access.applications a WHERE a.app_id=p_app FOR UPDATE;
 IF NOT FOUND OR app.revision::text<>p_revision THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
 previous:=app;
 IF app.enabled=p_enabled THEN disposition:='unchanged'; event:=NULL;
 ELSE
  IF app.revision=9223372036854775807 THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
  UPDATE access.applications a SET enabled=p_enabled WHERE a.app_id=p_app RETURNING a.* INTO app;
  disposition:='changed'; event:=gen_random_uuid();
 END IF;
 outcome_id:=gen_random_uuid();
 INSERT INTO access.operation_outcome(id,executor_actor_id,operation_id,command_type,scope_kind,command_version,fingerprint_version,fingerprint_algorithm,fingerprint,result_version,result)
 VALUES(outcome_id,executor,p_operation,'application.set_enabled','platform',1,1,'sha256',sha256(p_canonical),1,
 jsonb_build_object('target',jsonb_build_object('app_id',p_app),'disposition',disposition,'revision',app.revision::text,'event_id',event)) RETURNING * INTO saved;
 IF event IS NOT NULL THEN
  INSERT INTO access.business_event(event_id,event_type,event_version,executor_actor_id,operation_id,outcome_id,target,transition,reason_code,evidence_ref)
  VALUES(event,'access.application_availability_changed',1,executor,p_operation,outcome_id,jsonb_build_object('app_id',p_app),jsonb_build_object('before',jsonb_build_object('enabled',previous.enabled,'revision',previous.revision::text),'after',jsonb_build_object('enabled',app.enabled,'revision',app.revision::text)),p_reason,p_evidence);
 END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
CREATE OR REPLACE FUNCTION access.application_enablement_outcome(p_operation uuid,p_app text)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; saved access.operation_outcome; lock_document text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid
 OR p_app IS NULL OR p_app COLLATE "C" !~ '^[a-z][a-z0-9_]{1,63}$' THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 executor:=access.application_enablement_authority(p_app);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"application.set_enabled","lock_version":1,"operation_id":'||to_json(p_operation::text)::text||',"owner_schema":"access","scope_id":null,"scope_kind":"platform"}';
 BEGIN PERFORM pg_advisory_xact_lock(access.command_lock(lock_document)); EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='AC001',MESSAGE='access_operation_busy'; END;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM access.application_enablement_authority(p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 SELECT * INTO saved FROM access.operation_outcome o WHERE o.scope_kind='platform' AND o.scope_id IS NULL AND o.command_type='application.set_enabled' AND o.executor_actor_id=executor AND o.operation_id=p_operation;
 IF NOT FOUND THEN RETURN; END IF;
 IF saved.result->'target'->>'app_id' IS DISTINCT FROM p_app THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
REVOKE ALL ON FUNCTION access.set_application_enabled(uuid,text,boolean,text,text,text,bytea),access.application_enablement_outcome(uuid,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION access.set_application_enabled(uuid,text,boolean,text,text,text,bytea),access.application_enablement_outcome(uuid,text) TO access_operator;
RESET ROLE;
CREATE CONSTRAINT TRIGGER application_required_change AFTER UPDATE ON access.applications DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION access.require_application_change();
SET LOCAL ROLE access_command_owner;
REVOKE ALL ON FUNCTION access.require_application_change() FROM PUBLIC;
RESET ROLE;
GRANT UPDATE(enabled) ON access.applications TO access_command_owner;
REVOKE ALL ON FUNCTION access.guard_application_update(),access.application_enablement_authority(text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION access.application_enablement_authority(text) TO access_command_owner;
ALTER FUNCTION access.application_enablement_authority(text) OWNER TO access_operator_authority_owner;
REVOKE CREATE ON SCHEMA access FROM access_command_owner,access_operator_authority_owner;
'''

def upgrade():
    from access_baseline import verify_operator_roles
    verify_operator_roles(op.get_bind())
    op.get_bind().exec_driver_sql(SQL, execution_options={'no_parameters': True})

def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
