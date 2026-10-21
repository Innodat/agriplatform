"""Protected revision-safe organization application configuration."""
from alembic import op
revision = 'access_0009'
down_revision = 'access_0008'
branch_labels = None
depends_on = None
SQL = r'''
ALTER TABLE access.operator_authorities DROP CONSTRAINT operator_authorities_command_check;
ALTER TABLE access.operator_authorities ADD CONSTRAINT operator_authorities_command_check CHECK(command IN ('application.register','permission.register','entry_permission.register','application.set_enabled','organization_application.configure'));
ALTER TABLE access.operator_authorities DROP CONSTRAINT operator_authorities_scope_kind_check;
ALTER TABLE access.operator_authorities DROP CONSTRAINT operator_authorities_org_id_check;
ALTER TABLE access.operator_authorities ADD CONSTRAINT operator_authorities_scope_kind_check CHECK ((command='organization_application.configure' AND scope_kind='organization' AND org_id IS NOT NULL AND org_id<>'00000000-0000-0000-0000-000000000000'::uuid) OR (command<>'organization_application.configure' AND scope_kind='platform' AND org_id IS NULL));
ALTER TABLE access.operation_outcome DROP CONSTRAINT operation_outcome_command_type_check;
ALTER TABLE access.operation_outcome ADD CONSTRAINT operation_outcome_command_type_check CHECK(command_type IN ('application.register','permission.register','entry_permission.register','application.set_enabled','organization_application.configure'));
ALTER TABLE access.operation_outcome DROP CONSTRAINT operation_outcome_scope_kind_check;
ALTER TABLE access.operation_outcome DROP CONSTRAINT operation_outcome_scope_id_check;
ALTER TABLE access.operation_outcome ADD CONSTRAINT operation_outcome_scope_kind_check CHECK ((command_type='organization_application.configure' AND scope_kind='organization' AND scope_id IS NOT NULL AND scope_id<>'00000000-0000-0000-0000-000000000000'::uuid) OR (command_type<>'organization_application.configure' AND scope_kind='platform' AND scope_id IS NULL));
ALTER TABLE access.business_event DROP CONSTRAINT business_event_event_type_check;
ALTER TABLE access.business_event ADD CONSTRAINT business_event_event_type_check CHECK(event_type IN ('access.application_registered','access.permission_registered','access.entry_permission_registered','access.application_availability_changed','access.organization_application_changed'));
ALTER TABLE access.business_event DROP CONSTRAINT business_event_scope_kind_check;
ALTER TABLE access.business_event DROP CONSTRAINT business_event_scope_id_check;
ALTER TABLE access.business_event ADD CONSTRAINT business_event_scope_kind_check CHECK ((event_type='access.organization_application_changed' AND scope_kind='organization' AND scope_id IS NOT NULL AND scope_id<>'00000000-0000-0000-0000-000000000000'::uuid) OR (event_type<>'access.organization_application_changed' AND scope_kind='platform' AND scope_id IS NULL));
CREATE FUNCTION access.organization_application_authority(p_org uuid,p_app text) RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT p.executor_actor_id FROM access.operator_principals p JOIN access.operator_authorities a ON a.database_login=p.database_login
 WHERE p.database_login=session_user AND p.enabled AND a.enabled AND a.command='organization_application.configure'
 AND a.scope_kind='organization' AND a.org_id=p_org AND a.target_account_id IS NULL
 AND (a.application_id IS NULL OR a.application_id=p_app) ORDER BY a.id LIMIT 1
$f$;
CREATE OR REPLACE FUNCTION access.guard_command_evidence() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
DECLARE saved access.operation_outcome; app access.applications; executor uuid; event uuid; perm access.permissions; entry access.entry_permissions; orgapp access.organization_applications;
BEGIN
 IF TG_OP<>'INSERT' THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_evidence_immutable'; END IF;
 IF current_user<>'access_command_owner' THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_command_owner_required'; END IF;
 IF TG_TABLE_NAME='operation_outcome' THEN
  IF NEW.command_type='organization_application.configure' THEN
   executor:=access.organization_application_authority(NEW.scope_id,NEW.result->'target'->>'app_id');
   SELECT * INTO orgapp FROM access.organization_applications a WHERE a.org_id=NEW.scope_id AND a.app_id=NEW.result->'target'->>'app_id';
   IF executor IS NULL OR executor IS DISTINCT FROM NEW.executor_actor_id OR orgapp.app_id IS NULL
    OR NEW.scope_kind<>'organization' OR NEW.scope_id IS NULL
    OR NEW.result IS DISTINCT FROM jsonb_build_object('target',jsonb_build_object('org_id',orgapp.org_id,'app_id',orgapp.app_id),'disposition',NEW.result->>'disposition','revision',orgapp.revision::text,'event_id',NEW.result->'event_id')
    OR NEW.result->>'disposition' IS NULL OR NEW.result->>'disposition' NOT IN ('created','changed','unchanged') THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_configuration_result_invalid'; END IF;
   IF NEW.result->>'disposition' IN ('created','changed') THEN
    event:=(NEW.result->>'event_id')::uuid;
    IF event IS NULL OR event='00000000-0000-0000-0000-000000000000'::uuid
     OR orgapp.updated_by<>executor OR orgapp.updated_at<>statement_timestamp()
     OR (NEW.result->>'disposition'='created' AND (orgapp.revision<>1 OR orgapp.created_by<>executor OR orgapp.created_at<>statement_timestamp()))
     OR (NEW.result->>'disposition'='changed' AND orgapp.revision<2) THEN
     RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_configuration_changed_result_invalid'; END IF;
   ELSIF NEW.result->>'event_id' IS NOT NULL THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_unchanged_event_invalid'; END IF;
  ELSIF NEW.command_type='application.set_enabled' THEN
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
   OR NEW.target IS DISTINCT FROM saved.result->'target' OR saved.result->>'disposition' IS DISTINCT FROM (CASE WHEN saved.command_type='organization_application.configure' THEN saved.result->>'disposition' ELSE CASE WHEN saved.command_type='application.set_enabled' THEN 'changed' ELSE 'created' END END)
   OR (saved.command_type='organization_application.configure' AND saved.result->>'disposition' NOT IN ('created','changed'))
   OR NEW.scope_kind IS DISTINCT FROM saved.scope_kind OR NEW.scope_id IS DISTINCT FROM saved.scope_id
   OR NEW.event_type IS DISTINCT FROM (CASE saved.command_type WHEN 'organization_application.configure' THEN 'access.organization_application_changed' WHEN 'application.set_enabled' THEN 'access.application_availability_changed' WHEN 'application.register' THEN 'access.application_registered' WHEN 'permission.register' THEN 'access.permission_registered' WHEN 'entry_permission.register' THEN 'access.entry_permission_registered' END)
   OR NEW.transition IS DISTINCT FROM (CASE saved.command_type WHEN 'organization_application.configure' THEN (SELECT jsonb_build_object('before',CASE WHEN saved.result->>'disposition'='created' THEN NULL ELSE jsonb_build_object('enabled',NOT a.enabled,'revision',(a.revision-1)::text) END,'after',jsonb_build_object('enabled',a.enabled,'revision',a.revision::text)) FROM access.organization_applications a WHERE a.org_id=saved.scope_id AND a.app_id=saved.result->'target'->>'app_id' AND a.revision::text=saved.result->>'revision' AND a.updated_by=saved.executor_actor_id AND a.updated_at=saved.committed_at) WHEN 'application.set_enabled' THEN (SELECT jsonb_build_object('before',jsonb_build_object('enabled',NOT a.enabled,'revision',(a.revision-1)::text),'after',jsonb_build_object('enabled',a.enabled,'revision',a.revision::text)) FROM access.applications a WHERE a.app_id=saved.result->'target'->>'app_id' AND a.revision::text=saved.result->>'revision' AND a.updated_by=saved.executor_actor_id AND a.updated_at=saved.committed_at) WHEN 'application.register' THEN jsonb_build_object('enabled',false,'revision','1') WHEN 'entry_permission.register' THEN '{}'::jsonb ELSE (SELECT jsonb_build_object('scope_kind',p.scope_kind) FROM access.permissions p WHERE p.permission=saved.result->'target'->>'permission' AND p.app_id=saved.result->'target'->>'app_id') END) THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_event_invalid'; END IF;
  NEW.created_at:=saved.committed_at;
 END IF;
 RETURN NEW;
END $f$;
DROP TRIGGER registry_storage_immutable ON access.organization_applications;
CREATE TRIGGER registry_storage_immutable BEFORE DELETE OR TRUNCATE ON access.organization_applications FOR EACH STATEMENT EXECUTE FUNCTION access.registry_storage_immutable();
CREATE POLICY command_org_scope ON access.organization_applications TO access_command_owner
 USING (org_id::text=current_setting('app.org_id',true)) WITH CHECK (org_id::text=current_setting('app.org_id',true));
CREATE FUNCTION access.guard_organization_application_write() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid;
BEGIN
 IF current_user<>'access_command_owner' THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_command_owner_required'; END IF;
 IF TG_LEVEL='STATEMENT' THEN RETURN NULL; END IF;
 executor:=access.organization_application_authority(NEW.org_id,NEW.app_id);
 IF executor IS NULL OR current_setting('app.context_kind',true) IS DISTINCT FROM 'setup'
 OR nullif(current_setting('app.account_id',true),'') IS NOT NULL
 OR current_setting('app.actor_id',true) IS DISTINCT FROM executor::text THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_command_owner_required'; END IF;
 IF TG_OP='INSERT' THEN
  IF NEW.revision<>1 OR NEW.created_by<>executor OR NEW.updated_by<>executor OR NEW.created_at<>statement_timestamp() OR NEW.updated_at<>NEW.created_at THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_configuration_insert_invalid'; END IF;
 ELSE
  IF (to_jsonb(NEW)-'enabled') IS DISTINCT FROM (to_jsonb(OLD)-'enabled') OR NEW.enabled IS NOT DISTINCT FROM OLD.enabled OR OLD.revision=9223372036854775807 THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_configuration_update_invalid'; END IF;
  NEW.revision:=OLD.revision+1; NEW.updated_by:=executor; NEW.updated_at:=statement_timestamp();
 END IF;
 RETURN NEW;
END $f$;
CREATE FUNCTION access.guard_organization_application_statement() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF (SELECT count(*) FROM written_rows)<>1 THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_configuration_statement_invalid'; END IF;
 RETURN NULL;
END $f$;
CREATE TRIGGER organization_application_write_statement BEFORE INSERT OR UPDATE ON access.organization_applications FOR EACH STATEMENT EXECUTE FUNCTION access.guard_organization_application_write();
CREATE TRIGGER organization_application_write_guard BEFORE INSERT OR UPDATE ON access.organization_applications FOR EACH ROW EXECUTE FUNCTION access.guard_organization_application_write();
CREATE TRIGGER organization_application_insert_statement AFTER INSERT ON access.organization_applications REFERENCING NEW TABLE AS written_rows FOR EACH STATEMENT EXECUTE FUNCTION access.guard_organization_application_statement();
CREATE TRIGGER organization_application_update_statement AFTER UPDATE ON access.organization_applications REFERENCING NEW TABLE AS written_rows FOR EACH STATEMENT EXECUTE FUNCTION access.guard_organization_application_statement();
GRANT SELECT,INSERT ON access.organization_applications TO access_command_owner;
GRANT UPDATE(enabled) ON access.organization_applications TO access_command_owner;
GRANT CREATE ON SCHEMA access TO access_command_owner,access_operator_authority_owner;
SET LOCAL ROLE access_command_owner;
CREATE FUNCTION access.require_organization_application_change() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE previous jsonb;
BEGIN
 IF TG_OP='INSERT' THEN previous:=NULL;
 ELSE previous:=jsonb_build_object('enabled',OLD.enabled,'revision',OLD.revision::text); END IF;
 IF NOT EXISTS(SELECT 1 FROM access.operation_outcome o JOIN access.business_event e ON e.outcome_id=o.id
  WHERE o.command_type='organization_application.configure' AND o.scope_kind='organization' AND o.scope_id=NEW.org_id
  AND o.result=jsonb_build_object('target',jsonb_build_object('org_id',NEW.org_id,'app_id',NEW.app_id),'disposition',CASE WHEN TG_OP='INSERT' THEN 'created' ELSE 'changed' END,'revision',NEW.revision::text,'event_id',e.event_id)
  AND o.executor_actor_id=NEW.updated_by AND o.committed_at=NEW.updated_at
  AND e.transition=jsonb_build_object('before',previous,'after',jsonb_build_object('enabled',NEW.enabled,'revision',NEW.revision::text))
  AND e.event_type='access.organization_application_changed' AND e.created_at=NEW.updated_at) THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_required_configuration_change_missing'; END IF;
 RETURN NULL;
END $f$;
CREATE FUNCTION access.configure_organization_application(p_operation uuid,p_org uuid,p_app text,p_enabled boolean,p_absent boolean,p_revision text,p_reason text,p_evidence text,p_canonical bytea)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; saved access.operation_outcome; app access.organization_applications; expected jsonb; payload jsonb; doc jsonb; canonical text; lock_document text; event uuid; outcome_id uuid; disposition text; previous jsonb; observed_at timestamptz; eligible boolean;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid
 OR p_org IS NULL OR p_org='00000000-0000-0000-0000-000000000000'::uuid
 OR p_app IS NULL OR p_app COLLATE "C" !~ '^[a-z][a-z0-9_]{1,63}$' OR p_reason IS NULL OR p_reason NOT IN ('initial_setup','synthetic_fixture','identity_adoption','access_change','setup_correction')
 OR (p_evidence IS NOT NULL AND (p_evidence COLLATE "C" !~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$' OR position('://' in p_evidence)>0))
 OR p_enabled IS NULL OR p_absent IS NULL
 OR (p_absent AND p_revision IS NOT NULL)
 OR (NOT p_absent AND (p_revision IS NULL OR p_revision COLLATE "C" !~ '^[1-9][0-9]{0,18}$' OR (length(p_revision)=19 AND p_revision COLLATE "C">'9223372036854775807')))
 OR p_canonical IS NULL OR octet_length(p_canonical)>65536 THEN
  RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 payload:=jsonb_build_object('app_id',p_app,'enabled',p_enabled)||CASE WHEN p_absent THEN jsonb_build_object('expected_absent',true) ELSE jsonb_build_object('expected_revision',p_revision) END;
 expected:=jsonb_build_object('schema_version',1,'command','organization_application.configure','operation_id',p_operation::text,'scope',jsonb_build_object('kind','organization','org_id',p_org),'payload',payload,'reason_code',p_reason,'evidence_ref',p_evidence);
 BEGIN doc:=convert_from(p_canonical,'UTF8')::jsonb; EXCEPTION WHEN OTHERS THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END;
 canonical:='{"command":"organization_application.configure","evidence_ref":'||coalesce(to_json(p_evidence)::text,'null')||',"operation_id":'||to_json(p_operation::text)::text||',"payload":{"app_id":'||to_json(p_app)::text||',"enabled":'||to_json(p_enabled)::text||','||CASE WHEN p_absent THEN '"expected_absent":true' ELSE '"expected_revision":'||to_json(p_revision)::text END||'},"reason_code":'||to_json(p_reason)::text||',"schema_version":1,"scope":{"kind":"organization","org_id":'||to_json(p_org::text)::text||'}}';
 IF doc IS DISTINCT FROM expected OR convert_from(p_canonical,'UTF8') IS DISTINCT FROM canonical THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 executor:=access.organization_application_authority(p_org,p_app);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 PERFORM set_config('app.context_kind','setup',true),set_config('app.org_id',p_org::text,true),set_config('app.actor_id',executor::text,true),set_config('app.account_id','',true);
 -- Start before the cross-owner call; its waits consume the same bounded observation.
 observed_at:=clock_timestamp();
 BEGIN SELECT EXISTS(SELECT 1 FROM identity.organization_target(p_org) t WHERE t.org_id=p_org) INTO eligible;
 EXCEPTION WHEN OTHERS THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END;
 IF clock_timestamp()-observed_at>=interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END IF;
 IF NOT eligible THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"organization_application.configure","lock_version":1,"operation_id":'||to_json(p_operation::text)::text||',"owner_schema":"access","scope_id":'||to_json(p_org::text)::text||',"scope_kind":"organization"}';
 BEGIN PERFORM pg_advisory_xact_lock(access.command_lock(lock_document)); EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='AC001',MESSAGE='access_operation_busy'; END;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM access.organization_application_authority(p_org,p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 IF clock_timestamp()-observed_at>=interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END IF;
 SELECT * INTO saved FROM access.operation_outcome o WHERE o.scope_kind='organization' AND o.scope_id=p_org AND o.command_type='organization_application.configure' AND o.executor_actor_id=executor AND o.operation_id=p_operation;
 IF executor IS DISTINCT FROM access.organization_application_authority(p_org,p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 IF clock_timestamp()-observed_at>=interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END IF;
 IF saved.id IS NOT NULL THEN
  IF saved.fingerprint<>sha256(p_canonical) THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
  RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at; RETURN;
 END IF;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:organization-application:v1:'||p_org::text||':'||p_app));
 IF executor IS DISTINCT FROM access.organization_application_authority(p_org,p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 IF clock_timestamp()-observed_at>=interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END IF;
 PERFORM 1 FROM access.applications a WHERE a.app_id=p_app;
 IF executor IS DISTINCT FROM access.organization_application_authority(p_org,p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 IF clock_timestamp()-observed_at>=interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END IF;
 IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
 SELECT * INTO app FROM access.organization_applications a WHERE a.org_id=p_org AND a.app_id=p_app FOR UPDATE;
 IF executor IS DISTINCT FROM access.organization_application_authority(p_org,p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 IF clock_timestamp()-observed_at>=interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END IF;
 IF (p_absent AND app.app_id IS NOT NULL) OR (NOT p_absent AND (app.app_id IS NULL OR app.revision::text<>p_revision)) THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
 IF clock_timestamp()-observed_at>=interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END IF;
 IF p_absent THEN
  INSERT INTO access.organization_applications(org_id,app_id,enabled,revision,created_by,updated_by,created_at,updated_at)
  VALUES(p_org,p_app,p_enabled,1,executor,executor,statement_timestamp(),statement_timestamp()) RETURNING * INTO app;
  disposition:='created'; previous:=NULL; event:=gen_random_uuid();
 ELSIF app.enabled=p_enabled THEN disposition:='unchanged'; event:=NULL;
 ELSE
  IF app.revision=9223372036854775807 THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
  previous:=jsonb_build_object('enabled',app.enabled,'revision',app.revision::text);
  UPDATE access.organization_applications a SET enabled=p_enabled WHERE a.org_id=p_org AND a.app_id=p_app RETURNING a.* INTO app;
  disposition:='changed'; event:=gen_random_uuid();
 END IF;
 outcome_id:=gen_random_uuid();
 INSERT INTO access.operation_outcome(id,executor_actor_id,operation_id,command_type,scope_kind,scope_id,command_version,fingerprint_version,fingerprint_algorithm,fingerprint,result_version,result)
 VALUES(outcome_id,executor,p_operation,'organization_application.configure','organization',p_org,1,1,'sha256',sha256(p_canonical),1,
 jsonb_build_object('target',jsonb_build_object('org_id',p_org,'app_id',p_app),'disposition',disposition,'revision',app.revision::text,'event_id',event)) RETURNING * INTO saved;
 IF event IS NOT NULL THEN
  INSERT INTO access.business_event(event_id,event_type,event_version,scope_kind,scope_id,executor_actor_id,operation_id,outcome_id,target,transition,reason_code,evidence_ref)
  VALUES(event,'access.organization_application_changed',1,'organization',p_org,executor,p_operation,outcome_id,jsonb_build_object('org_id',p_org,'app_id',p_app),jsonb_build_object('before',previous,'after',jsonb_build_object('enabled',app.enabled,'revision',app.revision::text)),p_reason,p_evidence);
 END IF;
 IF executor IS DISTINCT FROM access.organization_application_authority(p_org,p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 IF clock_timestamp()-observed_at>=interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
CREATE FUNCTION access.organization_application_configuration_outcome(p_operation uuid,p_org uuid,p_app text)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; saved access.operation_outcome; lock_document text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid
 OR p_org IS NULL OR p_org='00000000-0000-0000-0000-000000000000'::uuid
 OR p_app IS NULL OR p_app COLLATE "C" !~ '^[a-z][a-z0-9_]{1,63}$' THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 executor:=access.organization_application_authority(p_org,p_app);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 PERFORM set_config('app.context_kind','setup',true),set_config('app.org_id',p_org::text,true),set_config('app.actor_id',executor::text,true),set_config('app.account_id','',true);
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"organization_application.configure","lock_version":1,"operation_id":'||to_json(p_operation::text)::text||',"owner_schema":"access","scope_id":'||to_json(p_org::text)::text||',"scope_kind":"organization"}';
 BEGIN PERFORM pg_advisory_xact_lock(access.command_lock(lock_document)); EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='AC001',MESSAGE='access_operation_busy'; END;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM access.organization_application_authority(p_org,p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 SELECT * INTO saved FROM access.operation_outcome o WHERE o.scope_kind='organization' AND o.scope_id=p_org AND o.command_type='organization_application.configure' AND o.executor_actor_id=executor AND o.operation_id=p_operation;
 IF NOT FOUND THEN RETURN; END IF;
 IF saved.result->'target'->>'org_id' IS DISTINCT FROM p_org::text OR saved.result->'target'->>'app_id' IS DISTINCT FROM p_app THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
REVOKE ALL ON FUNCTION access.configure_organization_application(uuid,uuid,text,boolean,boolean,text,text,text,bytea),access.organization_application_configuration_outcome(uuid,uuid,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION access.configure_organization_application(uuid,uuid,text,boolean,boolean,text,text,text,bytea),access.organization_application_configuration_outcome(uuid,uuid,text) TO access_operator;
RESET ROLE;
CREATE CONSTRAINT TRIGGER organization_application_required_change AFTER INSERT OR UPDATE ON access.organization_applications DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION access.require_organization_application_change();
SET LOCAL ROLE access_command_owner;
REVOKE ALL ON FUNCTION access.require_organization_application_change() FROM PUBLIC;
RESET ROLE;
REVOKE ALL ON FUNCTION access.guard_organization_application_write(),access.guard_organization_application_statement(),access.organization_application_authority(uuid,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION access.organization_application_authority(uuid,text) TO access_command_owner;
ALTER FUNCTION access.organization_application_authority(uuid,text) OWNER TO access_operator_authority_owner;
REVOKE CREATE ON SCHEMA access FROM access_command_owner,access_operator_authority_owner;
'''

def upgrade():
    from access_baseline import verify_operator_roles
    verify_operator_roles(op.get_bind())
    op.get_bind().exec_driver_sql(SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
