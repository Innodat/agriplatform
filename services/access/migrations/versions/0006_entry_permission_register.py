"""Protected immutable entry-permission registration; no access grant."""
from alembic import op
revision = 'access_0006'
down_revision = 'access_0005'
branch_labels = None
depends_on = None
SQL = r'''
ALTER TABLE access.operator_authorities DROP CONSTRAINT operator_authorities_command_check;
ALTER TABLE access.operator_authorities ADD CONSTRAINT operator_authorities_command_check CHECK(command IN ('application.register','permission.register','entry_permission.register'));
ALTER TABLE access.operation_outcome DROP CONSTRAINT operation_outcome_command_type_check;
ALTER TABLE access.operation_outcome ADD CONSTRAINT operation_outcome_command_type_check CHECK(command_type IN ('application.register','permission.register','entry_permission.register'));
ALTER TABLE access.business_event DROP CONSTRAINT business_event_event_type_check;
ALTER TABLE access.business_event ADD CONSTRAINT business_event_event_type_check CHECK(event_type IN ('access.application_registered','access.permission_registered','access.entry_permission_registered'));
CREATE OR REPLACE FUNCTION access.entry_permission_operator_authority(p_app text) RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT p.executor_actor_id FROM access.operator_principals p
 JOIN access.operator_authorities a ON a.database_login=p.database_login
 WHERE p.database_login=session_user AND p.enabled AND a.enabled
 AND a.command='entry_permission.register' AND a.scope_kind='platform' AND a.org_id IS NULL AND a.target_account_id IS NULL
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
  IF NEW.command_type='entry_permission.register' THEN
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
   OR NEW.target IS DISTINCT FROM saved.result->'target' OR saved.result->>'disposition'<>'created'
   OR NEW.scope_kind IS DISTINCT FROM saved.scope_kind OR NEW.scope_id IS DISTINCT FROM saved.scope_id
   OR NEW.event_type IS DISTINCT FROM (CASE saved.command_type WHEN 'application.register' THEN 'access.application_registered' WHEN 'permission.register' THEN 'access.permission_registered' WHEN 'entry_permission.register' THEN 'access.entry_permission_registered' END)
   OR NEW.transition IS DISTINCT FROM (CASE saved.command_type WHEN 'application.register' THEN jsonb_build_object('enabled',false,'revision','1') WHEN 'entry_permission.register' THEN '{}'::jsonb ELSE (SELECT jsonb_build_object('scope_kind',p.scope_kind) FROM access.permissions p WHERE p.permission=saved.result->'target'->>'permission' AND p.app_id=saved.result->'target'->>'app_id') END) THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_event_invalid'; END IF;
  NEW.created_at:=saved.committed_at;
 END IF;
 RETURN NEW;
END $f$;
GRANT CREATE ON SCHEMA access TO access_command_owner,access_operator_authority_owner;
SET LOCAL ROLE access_command_owner;
CREATE OR REPLACE FUNCTION access.require_entry_permission_registration() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM access.operation_outcome o JOIN access.business_event e ON e.outcome_id=o.id
  WHERE o.command_type='entry_permission.register' AND o.result->'target'=jsonb_build_object('app_id',NEW.app_id,'permission',NEW.permission) AND o.result->>'disposition'='created'
  AND o.executor_actor_id=NEW.created_by AND o.committed_at=NEW.created_at
  AND e.event_id=(o.result->>'event_id')::uuid) THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_required_registration_missing'; END IF;
 RETURN NULL;
END $f$;
CREATE OR REPLACE FUNCTION access.register_entry_permission(p_operation uuid,p_app text,p_permission text,p_reason text,p_evidence text,p_canonical bytea)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; saved access.operation_outcome; app access.applications; perm access.permissions; expected jsonb; doc jsonb; lock_document text; event uuid; outcome_id uuid; disposition text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid
 OR p_app IS NULL OR p_app COLLATE "C" !~ '^[a-z][a-z0-9_]{1,63}$' OR p_reason IS NULL OR p_reason NOT IN ('initial_setup','synthetic_fixture','identity_adoption','access_change','setup_correction')
 OR (p_evidence IS NOT NULL AND (p_evidence COLLATE "C" !~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$' OR position('://' in p_evidence)>0))
 OR p_permission IS NULL OR octet_length(p_permission) NOT BETWEEN 1 AND 200 OR octet_length(p_permission)<>length(p_permission)
 OR p_canonical IS NULL OR octet_length(p_canonical)>65536 THEN
  RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 expected:=jsonb_build_object('schema_version',1,'command','entry_permission.register','operation_id',p_operation::text,'scope',jsonb_build_object('kind','platform'),
 'payload',jsonb_build_object('app_id',p_app,'permission',p_permission,'expected_absent',true),'reason_code',p_reason,'evidence_ref',p_evidence);
 BEGIN doc:=convert_from(p_canonical,'UTF8')::jsonb; EXCEPTION WHEN OTHERS THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END;
 -- This fixed ASCII envelope has no numbers except 1 and no unbounded JSON values.
 IF doc IS DISTINCT FROM expected OR convert_from(p_canonical,'UTF8') IS DISTINCT FROM
  '{"command":"entry_permission.register","evidence_ref":'||coalesce(to_json(p_evidence)::text,'null')||',"operation_id":'||to_json(p_operation::text)::text||',"payload":{"app_id":'||to_json(p_app)::text||',"expected_absent":true,"permission":'||to_json(p_permission)::text||'},"reason_code":'||to_json(p_reason)::text||',"schema_version":1,"scope":{"kind":"platform"}}' THEN
  RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 executor:=access.entry_permission_operator_authority(p_app);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"entry_permission.register","lock_version":1,"operation_id":'||to_json(p_operation::text)::text||',"owner_schema":"access","scope_id":null,"scope_kind":"platform"}';
 BEGIN PERFORM pg_advisory_xact_lock(access.command_lock(lock_document)); EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='AC001',MESSAGE='access_operation_busy'; END;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM access.entry_permission_operator_authority(p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 SELECT * INTO saved FROM access.operation_outcome o WHERE o.scope_kind='platform' AND o.scope_id IS NULL AND o.command_type='entry_permission.register' AND o.executor_actor_id=executor AND o.operation_id=p_operation;
 IF FOUND THEN
  IF saved.fingerprint<>sha256(p_canonical) THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
  RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at; RETURN;
 END IF;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:entry-permission:v1:'||jsonb_build_array(p_app,p_permission)::text));
 IF executor IS DISTINCT FROM access.entry_permission_operator_authority(p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 SELECT * INTO app FROM access.applications a WHERE a.app_id=p_app;
 IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
 SELECT * INTO perm FROM access.permissions p WHERE p.permission=p_permission AND p.app_id=p_app;
 IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
 IF EXISTS(SELECT 1 FROM access.entry_permissions e WHERE e.app_id=p_app AND e.permission=p_permission) THEN
  disposition:='unchanged'; event:=NULL;
 ELSE
  INSERT INTO access.entry_permissions(app_id,permission,created_by,created_at)
   VALUES(p_app,p_permission,executor,statement_timestamp());
  disposition:='created'; event:=gen_random_uuid();
 END IF;
 outcome_id:=gen_random_uuid();
 INSERT INTO access.operation_outcome(id,executor_actor_id,operation_id,command_type,scope_kind,command_version,fingerprint_version,fingerprint_algorithm,fingerprint,result_version,result)
 VALUES(outcome_id,executor,p_operation,'entry_permission.register','platform',1,1,'sha256',sha256(p_canonical),1,
 jsonb_build_object('target',jsonb_build_object('app_id',p_app,'permission',p_permission),'disposition',disposition,'revision',NULL,'event_id',event)) RETURNING * INTO saved;
 IF event IS NOT NULL THEN
  INSERT INTO access.business_event(event_id,event_type,event_version,executor_actor_id,operation_id,outcome_id,target,transition,reason_code,evidence_ref)
  VALUES(event,'access.entry_permission_registered',1,executor,p_operation,outcome_id,jsonb_build_object('app_id',p_app,'permission',p_permission),'{}'::jsonb,p_reason,p_evidence);
 END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
CREATE OR REPLACE FUNCTION access.entry_permission_registration_outcome(p_operation uuid,p_app text,p_permission text)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; saved access.operation_outcome; lock_document text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid
 OR p_permission IS NULL OR octet_length(p_permission) NOT BETWEEN 1 AND 200 OR octet_length(p_permission)<>length(p_permission)
 OR p_app IS NULL OR p_app COLLATE "C" !~ '^[a-z][a-z0-9_]{1,63}$' THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 executor:=access.entry_permission_operator_authority(p_app);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"entry_permission.register","lock_version":1,"operation_id":'||to_json(p_operation::text)::text||',"owner_schema":"access","scope_id":null,"scope_kind":"platform"}';
 BEGIN PERFORM pg_advisory_xact_lock(access.command_lock(lock_document)); EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='AC001',MESSAGE='access_operation_busy'; END;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM access.entry_permission_operator_authority(p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 SELECT * INTO saved FROM access.operation_outcome o WHERE o.scope_kind='platform' AND o.scope_id IS NULL AND o.command_type='entry_permission.register' AND o.executor_actor_id=executor AND o.operation_id=p_operation;
 IF NOT FOUND THEN RETURN; END IF;
 IF saved.result->'target' IS DISTINCT FROM jsonb_build_object('app_id',p_app,'permission',p_permission) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;

RESET ROLE;
CREATE CONSTRAINT TRIGGER entry_permission_required_registration AFTER INSERT ON access.entry_permissions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION access.require_entry_permission_registration();
GRANT SELECT,INSERT ON access.entry_permissions TO access_command_owner;
REVOKE ALL ON FUNCTION access.entry_permission_operator_authority(text) FROM PUBLIC;
SET LOCAL ROLE access_command_owner;
REVOKE ALL ON FUNCTION access.require_entry_permission_registration(),access.register_entry_permission(uuid,text,text,text,text,bytea),access.entry_permission_registration_outcome(uuid,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION access.register_entry_permission(uuid,text,text,text,text,bytea),access.entry_permission_registration_outcome(uuid,text,text) TO access_operator;
RESET ROLE;
GRANT EXECUTE ON FUNCTION access.entry_permission_operator_authority(text) TO access_command_owner;
ALTER FUNCTION access.entry_permission_operator_authority(text) OWNER TO access_operator_authority_owner;
REVOKE CREATE ON SCHEMA access FROM access_command_owner,access_operator_authority_owner;
'''

def upgrade():
    from access_baseline import verify_operator_roles
    verify_operator_roles(op.get_bind())
    op.get_bind().exec_driver_sql(SQL, execution_options={'no_parameters': True})

def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
