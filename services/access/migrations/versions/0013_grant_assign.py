"""Protected exact-member organization capability grant assignment."""
from alembic import op
revision = 'access_0013'
down_revision = 'access_0012'
branch_labels = None
depends_on = None
SQL = r'''
ALTER TABLE access.operator_authorities DROP CONSTRAINT operator_authorities_command_check;
ALTER TABLE access.operator_authorities ADD CONSTRAINT operator_authorities_command_check CHECK(command IN ('application.register','permission.register','entry_permission.register','application.set_enabled','organization_application.configure','grant.assign'));
ALTER TABLE access.operator_authorities DROP CONSTRAINT operator_authorities_scope_kind_check;
ALTER TABLE access.operator_authorities ADD CONSTRAINT operator_authorities_scope_kind_check CHECK ((command IN ('organization_application.configure','grant.assign') AND scope_kind='organization' AND org_id IS NOT NULL AND org_id<>'00000000-0000-0000-0000-000000000000'::uuid) OR (command NOT IN ('organization_application.configure','grant.assign') AND scope_kind='platform' AND org_id IS NULL));
ALTER TABLE access.operator_authorities DROP CONSTRAINT operator_authorities_target_account_id_check;
ALTER TABLE access.operator_authorities ADD CONSTRAINT operator_authorities_target_account_id_check CHECK(target_account_id IS NULL OR (command='grant.assign' AND target_account_id<>'00000000-0000-0000-0000-000000000000'::uuid));
ALTER TABLE access.operation_outcome DROP CONSTRAINT operation_outcome_command_type_check;
ALTER TABLE access.operation_outcome ADD CONSTRAINT operation_outcome_command_type_check CHECK(command_type IN ('application.register','permission.register','entry_permission.register','application.set_enabled','organization_application.configure','grant.assign'));
ALTER TABLE access.operation_outcome DROP CONSTRAINT operation_outcome_scope_kind_check;
ALTER TABLE access.operation_outcome ADD CONSTRAINT operation_outcome_scope_kind_check CHECK ((command_type IN ('organization_application.configure','grant.assign') AND scope_kind='organization' AND scope_id IS NOT NULL AND scope_id<>'00000000-0000-0000-0000-000000000000'::uuid) OR (command_type NOT IN ('organization_application.configure','grant.assign') AND scope_kind='platform' AND scope_id IS NULL));
ALTER TABLE access.operation_outcome ADD COLUMN verified_membership_revision bigint, ADD COLUMN verified_account_actor_id uuid, ADD COLUMN target_observed_at timestamptz;
ALTER TABLE access.business_event DROP CONSTRAINT business_event_event_type_check;
ALTER TABLE access.business_event ADD CONSTRAINT business_event_event_type_check CHECK(event_type IN ('access.application_registered','access.permission_registered','access.entry_permission_registered','access.application_availability_changed','access.organization_application_changed','access.organization_grant_assigned'));
ALTER TABLE access.business_event DROP CONSTRAINT business_event_scope_kind_check;
ALTER TABLE access.business_event ADD CONSTRAINT business_event_scope_kind_check CHECK ((event_type IN ('access.organization_application_changed','access.organization_grant_assigned') AND scope_kind='organization' AND scope_id IS NOT NULL AND scope_id<>'00000000-0000-0000-0000-000000000000'::uuid) OR (event_type NOT IN ('access.organization_application_changed','access.organization_grant_assigned') AND scope_kind='platform' AND scope_id IS NULL));
CREATE FUNCTION access.grant_assignment_authority(p_org uuid,p_app text,p_account uuid) RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT p.executor_actor_id FROM access.operator_principals p JOIN access.operator_authorities a ON a.database_login=p.database_login
 WHERE p.database_login=session_user AND p.enabled AND a.enabled AND a.command='grant.assign'
 AND a.scope_kind='organization' AND a.org_id=p_org
 AND (a.target_account_id IS NULL OR a.target_account_id=p_account)
 AND (a.application_id IS NULL OR a.application_id=p_app) ORDER BY a.id LIMIT 1
$f$;
CREATE OR REPLACE FUNCTION access.guard_command_evidence() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
DECLARE saved access.operation_outcome; app access.applications; executor uuid; event uuid; perm access.permissions; entry access.entry_permissions; orgapp access.organization_applications; bound_grant access.grants; grant_app text;
BEGIN
 IF TG_OP<>'INSERT' THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_evidence_immutable'; END IF;
 IF current_user<>'access_command_owner' THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_command_owner_required'; END IF;
 IF TG_TABLE_NAME='operation_outcome' THEN
  IF NEW.command_type<>'grant.assign' AND (NEW.verified_membership_revision IS NOT NULL OR NEW.verified_account_actor_id IS NOT NULL OR NEW.target_observed_at IS NOT NULL) THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_observation_invalid'; END IF;
  IF NEW.command_type='grant.assign' THEN
   SELECT * INTO bound_grant FROM access.grants g WHERE g.org_id=NEW.scope_id AND g.id=NEW.result->'target'->>'grant_id';
   SELECT p.app_id INTO grant_app FROM access.permissions p WHERE p.permission=bound_grant.permission AND p.scope_kind='organization';
   executor:=access.grant_assignment_authority(NEW.scope_id,grant_app,bound_grant.user_id);
   IF executor IS NULL OR executor IS DISTINCT FROM NEW.executor_actor_id OR bound_grant.id IS NULL
    OR NEW.scope_kind<>'organization' OR NEW.scope_id IS NULL
    OR NEW.result IS DISTINCT FROM jsonb_build_object('target',jsonb_build_object('org_id',bound_grant.org_id,'grant_id',bound_grant.id,'account_id',bound_grant.user_id,'membership_id',bound_grant.membership_id::text,'permission',bound_grant.permission),'disposition',NEW.result->>'disposition','revision',bound_grant.revision::text,'event_id',NEW.result->'event_id')
    OR NEW.result->>'disposition' IS NULL OR NEW.result->>'disposition' NOT IN ('created','changed','unchanged')
    OR bound_grant.revoked_at IS NOT NULL OR bound_grant.created_actor_id IS NULL
    OR NEW.verified_membership_revision IS NULL OR NEW.verified_membership_revision<=0
    OR NEW.verified_account_actor_id IS NULL OR NEW.verified_account_actor_id='00000000-0000-0000-0000-000000000000'::uuid
    OR NEW.target_observed_at IS NULL OR NOT isfinite(NEW.target_observed_at)
    OR NEW.target_observed_at>clock_timestamp() OR clock_timestamp()-NEW.target_observed_at>=interval '5 seconds' THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_grant_result_invalid'; END IF;
   IF NEW.result->>'disposition' IN ('created','changed') THEN
    event:=(NEW.result->>'event_id')::uuid;
    IF event IS NULL OR event='00000000-0000-0000-0000-000000000000'::uuid
     OR bound_grant.updated_actor_id<>executor OR bound_grant.updated_at<>statement_timestamp()
     OR (NEW.result->>'disposition'='created' AND (bound_grant.revision<>1 OR bound_grant.created_actor_id<>executor OR bound_grant.created_at<>statement_timestamp() OR bound_grant.created_by<>executor::text))
     OR (NEW.result->>'disposition'='changed' AND bound_grant.revision<2) THEN
     RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_grant_changed_result_invalid'; END IF;
   ELSIF NEW.result->>'event_id' IS NOT NULL THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_unchanged_event_invalid'; END IF;
  ELSIF NEW.command_type='organization_application.configure' THEN
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
  IF saved.command_type='grant.assign' THEN
   SELECT * INTO bound_grant FROM access.grants g WHERE g.org_id=saved.scope_id AND g.id=saved.result->'target'->>'grant_id';
   IF saved.id IS NULL OR NEW.event_id IS DISTINCT FROM (saved.result->>'event_id')::uuid
    OR NEW.executor_actor_id<>saved.executor_actor_id OR NEW.operation_id<>saved.operation_id
    OR NEW.target IS DISTINCT FROM saved.result->'target' OR saved.result->>'disposition' NOT IN ('created','changed')
    OR NEW.scope_kind IS DISTINCT FROM saved.scope_kind OR NEW.scope_id IS DISTINCT FROM saved.scope_id
    OR NEW.event_type<>'access.organization_grant_assigned'
    OR NEW.transition IS DISTINCT FROM jsonb_build_object('before',NEW.transition->'before','after',jsonb_build_object('membership_id',bound_grant.membership_id::text,'revoked_at',bound_grant.revoked_at,'revision',bound_grant.revision::text))
    OR (saved.result->>'disposition'='created' AND NEW.transition->'before' IS DISTINCT FROM 'null'::jsonb)
    OR (saved.result->>'disposition'='changed' AND (jsonb_typeof(NEW.transition->'before') IS DISTINCT FROM 'object' OR NEW.transition->'before' IS DISTINCT FROM jsonb_build_object('membership_id',NEW.transition->'before'->'membership_id','revoked_at',NEW.transition->'before'->'revoked_at','revision',(bound_grant.revision-1)::text)))
    OR bound_grant.updated_actor_id IS DISTINCT FROM saved.executor_actor_id OR bound_grant.updated_at IS DISTINCT FROM saved.committed_at THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_event_invalid'; END IF;
  ELSE
  IF saved.id IS NULL OR NEW.event_id IS DISTINCT FROM (saved.result->>'event_id')::uuid
   OR NEW.executor_actor_id<>saved.executor_actor_id OR NEW.operation_id<>saved.operation_id
   OR NEW.target IS DISTINCT FROM saved.result->'target' OR saved.result->>'disposition' IS DISTINCT FROM (CASE WHEN saved.command_type='organization_application.configure' THEN saved.result->>'disposition' ELSE CASE WHEN saved.command_type='application.set_enabled' THEN 'changed' ELSE 'created' END END)
   OR (saved.command_type='organization_application.configure' AND saved.result->>'disposition' NOT IN ('created','changed'))
   OR NEW.scope_kind IS DISTINCT FROM saved.scope_kind OR NEW.scope_id IS DISTINCT FROM saved.scope_id
   OR NEW.event_type IS DISTINCT FROM (CASE saved.command_type WHEN 'organization_application.configure' THEN 'access.organization_application_changed' WHEN 'application.set_enabled' THEN 'access.application_availability_changed' WHEN 'application.register' THEN 'access.application_registered' WHEN 'permission.register' THEN 'access.permission_registered' WHEN 'entry_permission.register' THEN 'access.entry_permission_registered' END)
   OR NEW.transition IS DISTINCT FROM (CASE saved.command_type WHEN 'organization_application.configure' THEN (SELECT jsonb_build_object('before',CASE WHEN saved.result->>'disposition'='created' THEN NULL ELSE jsonb_build_object('enabled',NOT a.enabled,'revision',(a.revision-1)::text) END,'after',jsonb_build_object('enabled',a.enabled,'revision',a.revision::text)) FROM access.organization_applications a WHERE a.org_id=saved.scope_id AND a.app_id=saved.result->'target'->>'app_id' AND a.revision::text=saved.result->>'revision' AND a.updated_by=saved.executor_actor_id AND a.updated_at=saved.committed_at) WHEN 'application.set_enabled' THEN (SELECT jsonb_build_object('before',jsonb_build_object('enabled',NOT a.enabled,'revision',(a.revision-1)::text),'after',jsonb_build_object('enabled',a.enabled,'revision',a.revision::text)) FROM access.applications a WHERE a.app_id=saved.result->'target'->>'app_id' AND a.revision::text=saved.result->>'revision' AND a.updated_by=saved.executor_actor_id AND a.updated_at=saved.committed_at) WHEN 'application.register' THEN jsonb_build_object('enabled',false,'revision','1') WHEN 'entry_permission.register' THEN '{}'::jsonb ELSE (SELECT jsonb_build_object('scope_kind',p.scope_kind) FROM access.permissions p WHERE p.permission=saved.result->'target'->>'permission' AND p.app_id=saved.result->'target'->>'app_id') END) THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_event_invalid'; END IF;
  END IF;
  NEW.created_at:=saved.committed_at;
 END IF;
 RETURN NEW;
END $f$;
-- Access12 grants_active_fields and direct registered-scope FK remain unchanged.
CREATE POLICY command_org_scope ON access.grants TO access_command_owner
 USING (org_id::text=current_setting('app.org_id',true)) WITH CHECK (org_id::text=current_setting('app.org_id',true));
CREATE FUNCTION access.guard_grant_write() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; app text;
BEGIN
 IF current_user<>'access_command_owner' THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_command_owner_required'; END IF;
 IF TG_LEVEL='STATEMENT' THEN RETURN NULL; END IF;
 SELECT p.app_id INTO app FROM access.permissions p WHERE p.permission=NEW.permission AND p.scope_kind='organization';
 executor:=access.grant_assignment_authority(NEW.org_id,app,NEW.user_id);
 IF executor IS NULL OR app IS NULL OR current_setting('app.context_kind',true) IS DISTINCT FROM 'setup'
 OR nullif(current_setting('app.account_id',true),'') IS NOT NULL
 OR current_setting('app.actor_id',true) IS DISTINCT FROM executor::text THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_command_owner_required'; END IF;
 IF TG_OP='INSERT' THEN
  IF NEW.id IS NULL OR NEW.id !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' OR NEW.id::uuid='00000000-0000-0000-0000-000000000000'::uuid
   OR NEW.revision<>1 OR NEW.revoked_at IS NOT NULL OR NEW.membership_id IS NULL
   OR NEW.created_by<>executor::text OR NEW.created_actor_id IS DISTINCT FROM executor OR NEW.updated_actor_id IS DISTINCT FROM executor
   OR NEW.created_at<>statement_timestamp() OR NEW.updated_at IS DISTINCT FROM NEW.created_at THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_grant_insert_invalid'; END IF;
 ELSE
  IF (to_jsonb(NEW)-'membership_id'-'revoked_at') IS DISTINCT FROM (to_jsonb(OLD)-'membership_id'-'revoked_at')
   OR (NEW.membership_id IS NOT DISTINCT FROM OLD.membership_id AND NEW.revoked_at IS NOT DISTINCT FROM OLD.revoked_at)
   OR NEW.revoked_at IS NOT NULL OR NEW.membership_id IS NULL OR OLD.created_actor_id IS NULL OR OLD.revision=9223372036854775807 THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_grant_update_invalid'; END IF;
  NEW.revision:=OLD.revision+1; NEW.updated_actor_id:=executor; NEW.updated_at:=statement_timestamp();
 END IF;
 RETURN NEW;
END $f$;
CREATE FUNCTION access.guard_grant_statement() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF (SELECT count(*) FROM written_rows)<>1 THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_grant_statement_invalid'; END IF;
 RETURN NULL;
END $f$;
CREATE TRIGGER grant_write_statement BEFORE INSERT OR UPDATE ON access.grants FOR EACH STATEMENT EXECUTE FUNCTION access.guard_grant_write();
CREATE TRIGGER grant_write_guard BEFORE INSERT OR UPDATE ON access.grants FOR EACH ROW EXECUTE FUNCTION access.guard_grant_write();
CREATE TRIGGER grant_insert_statement AFTER INSERT ON access.grants REFERENCING NEW TABLE AS written_rows FOR EACH STATEMENT EXECUTE FUNCTION access.guard_grant_statement();
CREATE TRIGGER grant_update_statement AFTER UPDATE ON access.grants REFERENCING NEW TABLE AS written_rows FOR EACH STATEMENT EXECUTE FUNCTION access.guard_grant_statement();
CREATE TRIGGER grant_retention BEFORE DELETE OR TRUNCATE ON access.grants FOR EACH STATEMENT EXECUTE FUNCTION access.registry_storage_immutable();
GRANT SELECT,INSERT ON access.grants TO access_command_owner;
GRANT UPDATE(membership_id,revoked_at) ON access.grants TO access_command_owner;
GRANT CREATE ON SCHEMA access TO access_command_owner,access_operator_authority_owner;
SET LOCAL ROLE access_command_owner;
CREATE OR REPLACE FUNCTION access.require_command_event() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF NEW.command_type='grant.assign' AND (
  NEW.target_observed_at IS NULL OR NOT isfinite(NEW.target_observed_at)
  OR NEW.target_observed_at>clock_timestamp()
  OR clock_timestamp()-NEW.target_observed_at>=interval '5 seconds') THEN
  RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END IF;
 IF NEW.result->>'disposition' IN ('created','changed') AND NOT EXISTS(SELECT 1 FROM access.business_event e WHERE e.outcome_id=NEW.id AND e.event_id=(NEW.result->>'event_id')::uuid) THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_required_event_missing'; END IF;
 RETURN NULL;
END $f$;
CREATE FUNCTION access.require_grant_change() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE previous jsonb;
BEGIN
 IF TG_OP='INSERT' THEN previous:=NULL;
 ELSE previous:=jsonb_build_object('membership_id',OLD.membership_id::text,'revoked_at',OLD.revoked_at,'revision',OLD.revision::text); END IF;
 IF NOT EXISTS(SELECT 1 FROM access.operation_outcome o JOIN access.business_event e ON e.outcome_id=o.id
  WHERE o.command_type='grant.assign' AND o.scope_kind='organization' AND o.scope_id=NEW.org_id
  AND o.result=jsonb_build_object('target',jsonb_build_object('org_id',NEW.org_id,'grant_id',NEW.id,'account_id',NEW.user_id,'membership_id',NEW.membership_id::text,'permission',NEW.permission),'disposition',CASE WHEN TG_OP='INSERT' THEN 'created' ELSE 'changed' END,'revision',NEW.revision::text,'event_id',e.event_id)
  AND o.executor_actor_id=NEW.updated_actor_id AND o.committed_at=NEW.updated_at
  AND e.transition=jsonb_build_object('before',previous,'after',jsonb_build_object('membership_id',NEW.membership_id::text,'revoked_at',NEW.revoked_at,'revision',NEW.revision::text))
  AND e.event_type='access.organization_grant_assigned' AND e.created_at=NEW.updated_at) THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_required_grant_change_missing'; END IF;
 RETURN NULL;
END $f$;
CREATE FUNCTION access.assign_organization_grant(p_operation uuid,p_org uuid,p_account uuid,p_member bigint,p_permission text,p_absent boolean,p_revision text,p_reason text,p_evidence text,p_canonical bytea)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; saved access.operation_outcome; bound_grant access.grants; p_app text; expected jsonb; payload jsonb; doc jsonb; canonical text; lock_document text; event uuid; outcome_id uuid; disposition text; previous jsonb; observed_at timestamptz; verified_member_revision bigint; verified_actor uuid;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid
 OR p_org IS NULL OR p_org='00000000-0000-0000-0000-000000000000'::uuid
 OR p_account IS NULL OR p_account='00000000-0000-0000-0000-000000000000'::uuid
 OR p_member IS NULL OR p_member<=0 OR p_permission IS NULL OR octet_length(p_permission) NOT BETWEEN 1 AND 200 OR octet_length(p_permission)<>length(p_permission)
 OR p_reason IS NULL OR p_reason NOT IN ('initial_setup','synthetic_fixture','identity_adoption','access_change','setup_correction')
 OR (p_evidence IS NOT NULL AND (p_evidence COLLATE "C" !~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$' OR position('://' in p_evidence)>0))
 OR p_absent IS NULL OR (p_absent AND p_revision IS NOT NULL)
 OR (NOT p_absent AND (p_revision IS NULL OR p_revision COLLATE "C" !~ '^[1-9][0-9]{0,18}$' OR (length(p_revision)=19 AND p_revision COLLATE "C">'9223372036854775807')))
 OR p_canonical IS NULL OR octet_length(p_canonical)>65536 THEN
  RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 payload:=jsonb_build_object('account_id',p_account,'membership_id',p_member::text,'permission',p_permission)||CASE WHEN p_absent THEN jsonb_build_object('expected_absent',true) ELSE jsonb_build_object('expected_revision',p_revision) END;
 expected:=jsonb_build_object('schema_version',1,'command','grant.assign','operation_id',p_operation::text,'scope',jsonb_build_object('kind','organization','org_id',p_org),'payload',payload,'reason_code',p_reason,'evidence_ref',p_evidence);
 BEGIN doc:=convert_from(p_canonical,'UTF8')::jsonb; EXCEPTION WHEN OTHERS THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END;
 canonical:='{"command":"grant.assign","evidence_ref":'||coalesce(to_json(p_evidence)::text,'null')||',"operation_id":'||to_json(p_operation::text)::text||',"payload":{"account_id":'||to_json(p_account::text)::text||','||CASE WHEN p_absent THEN '"expected_absent":true' ELSE '"expected_revision":'||to_json(p_revision)::text END||',"membership_id":'||to_json(p_member::text)::text||',"permission":'||to_json(p_permission)::text||'},"reason_code":'||to_json(p_reason)::text||',"schema_version":1,"scope":{"kind":"organization","org_id":'||to_json(p_org::text)::text||'}}';
 IF doc IS DISTINCT FROM expected OR convert_from(p_canonical,'UTF8') IS DISTINCT FROM canonical THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 -- Registration is immutable. Resolve only the organization capability's application.
 SELECT p.app_id INTO p_app FROM access.permissions p WHERE p.permission=p_permission AND p.scope_kind='organization';
 IF p_app IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
 executor:=access.grant_assignment_authority(p_org,p_app,p_account);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 PERFORM set_config('app.context_kind','setup',true),set_config('app.org_id',p_org::text,true),set_config('app.actor_id',executor::text,true),set_config('app.account_id','',true);
 observed_at:=clock_timestamp();
 BEGIN SELECT t.membership_revision,t.actor_id INTO verified_member_revision,verified_actor
  FROM identity.organization_account_target(p_account,p_member) t WHERE t.account_id=p_account AND t.membership_id=p_member;
 EXCEPTION WHEN OTHERS THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END;
 IF clock_timestamp()-observed_at>=interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END IF;
 IF verified_member_revision IS NULL OR verified_member_revision<=0 OR verified_actor IS NULL OR verified_actor='00000000-0000-0000-0000-000000000000'::uuid THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"grant.assign","lock_version":1,"operation_id":'||to_json(p_operation::text)::text||',"owner_schema":"access","scope_id":'||to_json(p_org::text)::text||',"scope_kind":"organization"}';
 BEGIN PERFORM pg_advisory_xact_lock(access.command_lock(lock_document)); EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='AC001',MESSAGE='access_operation_busy'; END;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM access.grant_assignment_authority(p_org,p_app,p_account) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 IF clock_timestamp()-observed_at>=interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END IF;
 SELECT * INTO saved FROM access.operation_outcome o WHERE o.scope_kind='organization' AND o.scope_id=p_org AND o.command_type='grant.assign' AND o.executor_actor_id=executor AND o.operation_id=p_operation;
 IF executor IS DISTINCT FROM access.grant_assignment_authority(p_org,p_app,p_account) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 IF clock_timestamp()-observed_at>=interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END IF;
 IF saved.id IS NOT NULL THEN
  IF saved.fingerprint<>sha256(p_canonical) THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
  RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at; RETURN;
 END IF;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:organization-grant:v1:'||p_org::text||':'||p_account::text||':'||p_permission));
 IF executor IS DISTINCT FROM access.grant_assignment_authority(p_org,p_app,p_account) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 IF clock_timestamp()-observed_at>=interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END IF;
 SELECT * INTO bound_grant FROM access.grants g WHERE g.org_id=p_org AND g.user_id=p_account AND g.permission=p_permission FOR UPDATE;
 IF executor IS DISTINCT FROM access.grant_assignment_authority(p_org,p_app,p_account) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 IF clock_timestamp()-observed_at>=interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END IF;
 IF (p_absent AND bound_grant.id IS NOT NULL) OR (NOT p_absent AND (bound_grant.id IS NULL OR bound_grant.revision::text<>p_revision)) THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
 IF bound_grant.id IS NOT NULL AND bound_grant.created_actor_id IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
 IF p_absent THEN
  INSERT INTO access.grants(org_id,id,user_id,permission,created_at,created_by,membership_id,scope_kind,revision,revoked_at,created_actor_id,updated_actor_id,updated_at)
  VALUES(p_org,gen_random_uuid()::text,p_account,p_permission,statement_timestamp(),executor::text,p_member,'organization',1,NULL,executor,executor,statement_timestamp()) RETURNING * INTO bound_grant;
  disposition:='created'; previous:=NULL; event:=gen_random_uuid();
 ELSIF bound_grant.membership_id=p_member AND bound_grant.revoked_at IS NULL THEN disposition:='unchanged'; event:=NULL;
 ELSE
  IF bound_grant.revision=9223372036854775807 THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
  previous:=jsonb_build_object('membership_id',bound_grant.membership_id::text,'revoked_at',bound_grant.revoked_at,'revision',bound_grant.revision::text);
  UPDATE access.grants g SET membership_id=p_member,revoked_at=NULL WHERE g.org_id=p_org AND g.id=bound_grant.id RETURNING g.* INTO bound_grant;
  disposition:='changed'; event:=gen_random_uuid();
 END IF;
 outcome_id:=gen_random_uuid();
 INSERT INTO access.operation_outcome(id,executor_actor_id,operation_id,command_type,scope_kind,scope_id,command_version,fingerprint_version,fingerprint_algorithm,fingerprint,result_version,result,verified_membership_revision,verified_account_actor_id,target_observed_at)
 VALUES(outcome_id,executor,p_operation,'grant.assign','organization',p_org,1,1,'sha256',sha256(p_canonical),1,
 jsonb_build_object('target',jsonb_build_object('org_id',p_org,'grant_id',bound_grant.id,'account_id',p_account,'membership_id',p_member::text,'permission',p_permission),'disposition',disposition,'revision',bound_grant.revision::text,'event_id',event),verified_member_revision,verified_actor,observed_at) RETURNING * INTO saved;
 IF event IS NOT NULL THEN
  INSERT INTO access.business_event(event_id,event_type,event_version,scope_kind,scope_id,executor_actor_id,operation_id,outcome_id,target,transition,reason_code,evidence_ref)
  VALUES(event,'access.organization_grant_assigned',1,'organization',p_org,executor,p_operation,outcome_id,saved.result->'target',jsonb_build_object('before',previous,'after',jsonb_build_object('membership_id',bound_grant.membership_id::text,'revoked_at',bound_grant.revoked_at,'revision',bound_grant.revision::text)),p_reason,p_evidence);
 END IF;
 IF executor IS DISTINCT FROM access.grant_assignment_authority(p_org,p_app,p_account) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 IF clock_timestamp()-observed_at>=interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable'; END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
CREATE FUNCTION access.organization_grant_assignment_outcome(p_operation uuid,p_org uuid,p_account uuid,p_member bigint,p_permission text)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; saved access.operation_outcome; lock_document text; app text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid
 OR p_org IS NULL OR p_org='00000000-0000-0000-0000-000000000000'::uuid
 OR p_account IS NULL OR p_account='00000000-0000-0000-0000-000000000000'::uuid OR p_member IS NULL OR p_member<=0
 OR p_permission IS NULL OR octet_length(p_permission) NOT BETWEEN 1 AND 200 OR octet_length(p_permission)<>length(p_permission) THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 SELECT p.app_id INTO app FROM access.permissions p WHERE p.permission=p_permission AND p.scope_kind='organization';
 IF app IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
 executor:=access.grant_assignment_authority(p_org,app,p_account);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 PERFORM set_config('app.context_kind','setup',true),set_config('app.org_id',p_org::text,true),set_config('app.actor_id',executor::text,true),set_config('app.account_id','',true);
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"grant.assign","lock_version":1,"operation_id":'||to_json(p_operation::text)::text||',"owner_schema":"access","scope_id":'||to_json(p_org::text)::text||',"scope_kind":"organization"}';
 BEGIN PERFORM pg_advisory_xact_lock(access.command_lock(lock_document)); EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='AC001',MESSAGE='access_operation_busy'; END;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM access.grant_assignment_authority(p_org,app,p_account) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 SELECT * INTO saved FROM access.operation_outcome o WHERE o.scope_kind='organization' AND o.scope_id=p_org AND o.command_type='grant.assign' AND o.executor_actor_id=executor AND o.operation_id=p_operation;
 IF NOT FOUND THEN RETURN; END IF;
 IF saved.result->'target'->>'org_id' IS DISTINCT FROM p_org::text OR saved.result->'target'->>'account_id' IS DISTINCT FROM p_account::text
 OR saved.result->'target'->>'membership_id' IS DISTINCT FROM p_member::text OR saved.result->'target'->>'permission' IS DISTINCT FROM p_permission THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
REVOKE ALL ON FUNCTION access.assign_organization_grant(uuid,uuid,uuid,bigint,text,boolean,text,text,text,bytea),access.organization_grant_assignment_outcome(uuid,uuid,uuid,bigint,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION access.assign_organization_grant(uuid,uuid,uuid,bigint,text,boolean,text,text,text,bytea),access.organization_grant_assignment_outcome(uuid,uuid,uuid,bigint,text) TO access_operator;
RESET ROLE;
CREATE CONSTRAINT TRIGGER grant_required_change AFTER INSERT OR UPDATE ON access.grants DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION access.require_grant_change();
SET LOCAL ROLE access_command_owner;
DO $acl$
DECLARE r record; a record; grantee text;
BEGIN
 FOR r IN SELECT p.proowner owner,p.proacl acl,p.oid::regprocedure::text object FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
 WHERE n.nspname='access' AND p.proname IN ('require_grant_change','assign_organization_grant','organization_grant_assignment_outcome') LOOP
  EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.object);
  FOR a IN SELECT DISTINCT x.grantee FROM aclexplode(r.acl) x WHERE x.grantee<>r.owner LOOP
   grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
   EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s',r.object,grantee);
  END LOOP;
 END LOOP;
END $acl$;
GRANT EXECUTE ON FUNCTION access.assign_organization_grant(uuid,uuid,uuid,bigint,text,boolean,text,text,text,bytea),access.organization_grant_assignment_outcome(uuid,uuid,uuid,bigint,text) TO access_operator;
RESET ROLE;
DO $acl$
DECLARE r record; a record; grantee text;
BEGIN
 FOR r IN SELECT p.proowner owner,p.proacl acl,p.oid::regprocedure::text object FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
 WHERE n.nspname='access' AND p.proname IN ('guard_grant_write','guard_grant_statement','grant_assignment_authority') LOOP
  EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.object);
  FOR a IN SELECT DISTINCT x.grantee FROM aclexplode(r.acl) x WHERE x.grantee<>r.owner LOOP
   grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
   EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s',r.object,grantee);
  END LOOP;
 END LOOP;
END $acl$;

GRANT EXECUTE ON FUNCTION access.grant_assignment_authority(uuid,text,uuid) TO access_command_owner;
ALTER FUNCTION access.grant_assignment_authority(uuid,text,uuid) OWNER TO access_operator_authority_owner;
REVOKE CREATE ON SCHEMA access FROM access_command_owner,access_operator_authority_owner;
'''


def upgrade():
    from access_baseline import verify_operator_roles
    verify_operator_roles(op.get_bind())
    op.get_bind().exec_driver_sql(SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
