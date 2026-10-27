"""Independent retained account capability grants; controlled setup only."""
from alembic import op
revision='access_0017'
down_revision='access_0016'
branch_labels=None
depends_on=None
SQL=r'''
ALTER TABLE access.operator_authorities DROP CONSTRAINT operator_authorities_command_check;
ALTER TABLE access.operator_authorities ADD CONSTRAINT operator_authorities_command_check CHECK(command IN ('application.register','permission.register','entry_permission.register','application.set_enabled','organization_application.configure','grant.assign','grant.revoke','account_grant.assign','account_grant.revoke'));
ALTER TABLE access.operator_authorities DROP CONSTRAINT operator_authorities_target_account_id_check;
ALTER TABLE access.operator_authorities ADD CONSTRAINT operator_authorities_target_account_id_check CHECK(target_account_id IS NULL OR (command IN ('grant.assign','grant.revoke','account_grant.assign','account_grant.revoke') AND target_account_id<>'00000000-0000-0000-0000-000000000000'::uuid));
ALTER TABLE access.operation_outcome DROP CONSTRAINT operation_outcome_command_type_check;
ALTER TABLE access.operation_outcome ADD CONSTRAINT operation_outcome_command_type_check CHECK(command_type IN ('application.register','permission.register','entry_permission.register','application.set_enabled','organization_application.configure','grant.assign','grant.revoke','account_grant.assign','account_grant.revoke'));
ALTER TABLE access.business_event DROP CONSTRAINT business_event_event_type_check;
ALTER TABLE access.business_event ADD CONSTRAINT business_event_event_type_check CHECK(event_type IN ('access.application_registered','access.permission_registered','access.entry_permission_registered','access.application_availability_changed','access.organization_application_changed','access.organization_grant_assigned','access.organization_grant_revoked','access.account_grant_assigned','access.account_grant_revoked'));
CREATE TABLE access.account_grants(
 id uuid PRIMARY KEY CHECK(id<>'00000000-0000-0000-0000-000000000000'),
 account_id uuid NOT NULL CHECK(account_id<>'00000000-0000-0000-0000-000000000000'),
 permission text NOT NULL,scope_kind text NOT NULL DEFAULT 'account' CHECK(scope_kind='account'),
 revision bigint NOT NULL DEFAULT 1 CHECK(revision>0),revoked_at timestamptz CHECK(revoked_at IS NULL OR isfinite(revoked_at)),
 created_by uuid NOT NULL CHECK(created_by<>'00000000-0000-0000-0000-000000000000'),
 updated_by uuid NOT NULL CHECK(updated_by<>'00000000-0000-0000-0000-000000000000'),
 created_at timestamptz NOT NULL DEFAULT statement_timestamp() CHECK(isfinite(created_at)),updated_at timestamptz NOT NULL DEFAULT statement_timestamp() CHECK(isfinite(updated_at)),
 UNIQUE(account_id,permission),FOREIGN KEY(permission,scope_kind) REFERENCES access.permissions(permission,scope_kind));
ALTER TABLE access.account_grants ENABLE ROW LEVEL SECURITY;
ALTER TABLE access.account_grants FORCE ROW LEVEL SECURITY;
DO $table_acl$
DECLARE a record;grantee text;
BEGIN
 FOR a IN SELECT DISTINCT x.grantee FROM pg_class c,LATERAL aclexplode(c.relacl) x
 WHERE c.oid='access.account_grants'::regclass AND x.grantee<>c.relowner LOOP
 grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
 EXECUTE format('REVOKE ALL ON access.account_grants FROM %s',grantee);
 END LOOP;
END $table_acl$;
REVOKE ALL ON access.account_grants FROM PUBLIC;
GRANT SELECT,INSERT,UPDATE ON access.account_grants TO access_command_owner;
GRANT SELECT ON access.account_grants TO access_runtime;
CREATE POLICY account_grant_runtime_read ON access.account_grants FOR SELECT TO access_runtime
 USING(current_setting('app.context_kind',true)='user' AND account_id::text=current_setting('app.account_id',true));
CREATE POLICY account_grant_inspection ON access.account_grants FOR SELECT TO access_migrator USING(true);
CREATE POLICY account_grant_command ON access.account_grants TO access_command_owner
 USING(current_setting('app.context_kind',true)='setup' AND account_id::text=current_setting('app.target_account_id',true)
 AND nullif(current_setting('app.account_id',true),'') IS NULL AND nullif(current_setting('app.org_id',true),'') IS NULL)
 WITH CHECK(current_setting('app.context_kind',true)='setup' AND account_id::text=current_setting('app.target_account_id',true)
 AND nullif(current_setting('app.account_id',true),'') IS NULL AND nullif(current_setting('app.org_id',true),'') IS NULL);
CREATE FUNCTION access.account_grant_authority(p_command text,p_app text,p_account uuid) RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT p.executor_actor_id FROM access.operator_principals p JOIN access.operator_authorities a USING(database_login)
 WHERE p.database_login=session_user AND p.enabled AND a.enabled AND a.command=p_command
 AND p_command IN ('account_grant.assign','account_grant.revoke') AND a.scope_kind='platform' AND a.org_id IS NULL
 AND (a.application_id IS NULL OR a.application_id=p_app) AND (a.target_account_id IS NULL OR a.target_account_id=p_account)
 ORDER BY a.id LIMIT 1
$f$;
CREATE FUNCTION access.guard_account_grant() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; app text;
BEGIN
 IF current_user<>'access_command_owner' OR TG_OP NOT IN ('INSERT','UPDATE') THEN
 RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_command_owner_required'; END IF;
 SELECT p.app_id INTO app FROM access.permissions p WHERE p.permission=NEW.permission AND p.scope_kind='account';
 executor:=access.account_grant_authority(CASE WHEN NEW.revoked_at IS NULL THEN 'account_grant.assign' ELSE 'account_grant.revoke' END,app,NEW.account_id);
 IF executor IS NULL OR app IS NULL OR current_setting('app.actor_id',true) IS DISTINCT FROM executor::text
 OR current_setting('app.context_kind',true) IS DISTINCT FROM 'setup'
 OR nullif(current_setting('app.account_id',true),'') IS NOT NULL OR nullif(current_setting('app.org_id',true),'') IS NOT NULL
 OR current_setting('app.target_account_id',true) IS DISTINCT FROM NEW.account_id::text THEN
 RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_command_owner_required'; END IF;
 IF TG_OP='INSERT' THEN
 IF NEW.revision<>1 OR NEW.revoked_at IS NOT NULL THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_account_grant_invalid'; END IF;
 NEW.created_by:=executor;NEW.updated_by:=executor;NEW.created_at:=statement_timestamp();NEW.updated_at:=NEW.created_at;
 ELSE
 IF (to_jsonb(NEW)-'revoked_at') IS DISTINCT FROM (to_jsonb(OLD)-'revoked_at')
 OR NEW.revoked_at IS NOT DISTINCT FROM OLD.revoked_at OR OLD.revision=9223372036854775807
 OR (NEW.revoked_at IS NOT NULL AND OLD.revoked_at IS NOT NULL) THEN
 RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_account_grant_invalid'; END IF;
 NEW.revision:=OLD.revision+1;NEW.updated_by:=executor;NEW.updated_at:=statement_timestamp();
 IF NEW.revoked_at IS NOT NULL THEN NEW.revoked_at:=NEW.updated_at; END IF;
 END IF;RETURN NEW;
END $f$;
CREATE TRIGGER account_grant_guard BEFORE INSERT OR UPDATE OR DELETE ON access.account_grants FOR EACH ROW EXECUTE FUNCTION access.guard_account_grant();
CREATE TRIGGER account_grant_retention BEFORE TRUNCATE ON access.account_grants FOR EACH STATEMENT EXECUTE FUNCTION access.guard_account_grant();
GRANT CREATE ON SCHEMA access TO access_command_owner,access_operator_authority_owner;
REVOKE ALL ON FUNCTION access.account_grant_authority(text,text,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION access.account_grant_authority(text,text,uuid) TO access_command_owner;
ALTER FUNCTION access.account_grant_authority(text,text,uuid) OWNER TO access_operator_authority_owner;
SET LOCAL ROLE access_command_owner;
CREATE FUNCTION access.require_account_grant_change() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE previous jsonb;
BEGIN
 previous:=CASE WHEN TG_OP='INSERT' THEN NULL ELSE jsonb_build_object('revoked_at',OLD.revoked_at,'revision',OLD.revision::text) END;
 IF NOT EXISTS(SELECT 1 FROM access.operation_outcome o JOIN access.business_event e ON e.outcome_id=o.id
 WHERE o.command_type=CASE WHEN NEW.revoked_at IS NULL THEN 'account_grant.assign' ELSE 'account_grant.revoke' END
 AND o.scope_kind='platform' AND o.scope_id IS NULL AND o.executor_actor_id=NEW.updated_by AND o.committed_at=NEW.updated_at
 AND o.result=jsonb_build_object('target',jsonb_build_object('grant_id',NEW.id,'account_id',NEW.account_id,'permission',NEW.permission),
 'disposition',CASE WHEN TG_OP='INSERT' THEN 'created' ELSE 'changed' END,'revision',NEW.revision::text,'event_id',e.event_id)
 AND e.event_type=CASE WHEN NEW.revoked_at IS NULL THEN 'access.account_grant_assigned' ELSE 'access.account_grant_revoked' END
 AND e.transition=jsonb_build_object('before',previous,'after',jsonb_build_object('revoked_at',NEW.revoked_at,'revision',NEW.revision::text))) THEN
 RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_required_account_grant_change_missing'; END IF;RETURN NULL;
END $f$;
CREATE FUNCTION access.change_account_grant(p_operation uuid,p_command text,p_account uuid,p_permission text,p_grant uuid,p_absent boolean,p_revision text,p_reason text,p_evidence text,p_canonical bytea)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid;app text;saved access.operation_outcome;bound access.account_grants;observed_actor uuid;observed timestamptz;
 payload jsonb;expected jsonb;doc jsonb;canonical text;lock_document text;disposition text;event uuid;previous jsonb;violated text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'
 OR p_command IS NULL OR p_command NOT IN ('account_grant.assign','account_grant.revoke')
 OR p_account IS NULL OR p_account='00000000-0000-0000-0000-000000000000'
 OR p_permission IS NULL OR octet_length(p_permission) NOT BETWEEN 1 AND 200 OR octet_length(p_permission)<>length(p_permission)
 OR p_absent IS NULL OR (p_absent AND (p_command<>'account_grant.assign' OR p_grant IS NOT NULL OR p_revision IS NOT NULL))
 OR (NOT p_absent AND (p_grant IS NULL OR p_grant='00000000-0000-0000-0000-000000000000' OR p_revision IS NULL
 OR p_revision COLLATE "C" !~ '^[1-9][0-9]{0,18}$' OR (length(p_revision)=19 AND p_revision COLLATE "C">'9223372036854775807')))
 OR p_reason IS NULL OR p_reason NOT IN ('initial_setup','synthetic_fixture','identity_adoption','access_change','setup_correction')
 OR (p_evidence IS NOT NULL AND (p_evidence COLLATE "C" !~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$' OR position('://' in p_evidence)>0))
 OR p_canonical IS NULL OR octet_length(p_canonical)>65536 THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 payload:=jsonb_build_object('account_id',p_account,'permission',p_permission)||CASE WHEN p_absent THEN jsonb_build_object('expected_absent',true) ELSE jsonb_build_object('grant_id',p_grant,'expected_revision',p_revision) END;
 expected:=jsonb_build_object('command',p_command,'evidence_ref',p_evidence,'operation_id',p_operation,'payload',payload,'reason_code',p_reason,'schema_version',1,'scope',jsonb_build_object('kind','platform'));
 BEGIN doc:=convert_from(p_canonical,'UTF8')::jsonb;EXCEPTION WHEN OTHERS THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid';END;
 canonical:='{"command":'||to_json(p_command)::text||',"evidence_ref":'||coalesce(to_json(p_evidence)::text,'null')||',"operation_id":'||to_json(p_operation::text)::text||',"payload":{"account_id":'||to_json(p_account::text)::text||','||CASE WHEN p_absent THEN '"expected_absent":true,' ELSE '"expected_revision":'||to_json(p_revision)::text||',"grant_id":'||to_json(p_grant::text)::text||',' END||'"permission":'||to_json(p_permission)::text||'},"reason_code":'||to_json(p_reason)::text||',"schema_version":1,"scope":{"kind":"platform"}}';
 IF doc IS DISTINCT FROM expected OR convert_from(p_canonical,'UTF8') IS DISTINCT FROM canonical THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid';END IF;
 SELECT p.app_id INTO app FROM access.permissions p WHERE p.permission=p_permission AND p.scope_kind='account';
 executor:=access.account_grant_authority(p_command,app,p_account);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied';END IF;
 IF app IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict';END IF;
 PERFORM set_config('app.context_kind','setup',true),set_config('app.account_id','',true),set_config('app.org_id','',true),set_config('app.actor_id',executor::text,true),set_config('app.target_account_id',p_account::text,true);
 -- A committed exact retry is recovery, not a fresh eligibility observation.
 SELECT * INTO saved FROM access.operation_outcome o WHERE o.executor_actor_id=executor AND o.operation_id=p_operation;
 IF saved.id IS NOT NULL THEN
 IF saved.command_type IS DISTINCT FROM p_command OR saved.scope_kind IS DISTINCT FROM 'platform' OR saved.scope_id IS NOT NULL OR saved.fingerprint<>sha256(p_canonical) THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict';END IF;
 IF executor IS DISTINCT FROM access.account_grant_authority(p_command,app,p_account) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied';END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;RETURN;END IF;
 -- Observe the protected Identity projection before any local coordination/write locks.
 IF p_command='account_grant.assign' THEN
 observed:=clock_timestamp(); SELECT t.actor_id INTO observed_actor FROM identity.account_grant_target(p_account) t WHERE t.account_id=p_account;
 IF observed_actor IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable';END IF;END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":'||to_json(p_command)::text||',"lock_version":1,"operation_id":'||to_json(p_operation::text)::text||',"owner_schema":"access","scope_id":null,"scope_kind":"platform"}';
 BEGIN PERFORM pg_advisory_xact_lock(access.command_lock(lock_document));EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='AC001',MESSAGE='access_operation_busy';END;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM access.account_grant_authority(p_command,app,p_account) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied';END IF;
 SELECT * INTO saved FROM access.operation_outcome o WHERE o.executor_actor_id=executor AND o.operation_id=p_operation;
 IF saved.id IS NOT NULL THEN
 IF saved.command_type IS DISTINCT FROM p_command OR saved.scope_kind IS DISTINCT FROM 'platform' OR saved.scope_id IS NOT NULL OR saved.fingerprint<>sha256(p_canonical) THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict';END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;RETURN;END IF;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:account-grant:v1:'||p_account::text||':'||p_permission));
 IF executor IS DISTINCT FROM access.account_grant_authority(p_command,app,p_account) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied';END IF;
 IF p_command='account_grant.assign' AND clock_timestamp()-observed>=interval '5 seconds' THEN RAISE EXCEPTION USING ERRCODE='AC004',MESSAGE='access_verification_unavailable';END IF;
 SELECT * INTO bound FROM access.account_grants g WHERE g.account_id=p_account AND g.permission=p_permission FOR UPDATE;
 IF (p_absent AND bound.id IS NOT NULL) OR (NOT p_absent AND (bound.id IS NULL OR bound.id IS DISTINCT FROM p_grant OR bound.revision::text IS DISTINCT FROM p_revision)) THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict';END IF;
 previous:=CASE WHEN bound.id IS NULL THEN NULL ELSE jsonb_build_object('revoked_at',bound.revoked_at,'revision',bound.revision::text) END;
 IF bound.id IS NULL THEN
 INSERT INTO access.account_grants(id,account_id,permission,created_by,updated_by) VALUES(gen_random_uuid(),p_account,p_permission,executor,executor) RETURNING * INTO bound;disposition:='created';
 ELSIF (p_command='account_grant.assign' AND bound.revoked_at IS NULL) OR (p_command='account_grant.revoke' AND bound.revoked_at IS NOT NULL) THEN disposition:='unchanged';
 ELSE
 IF bound.revision=9223372036854775807 THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict';END IF;
 UPDATE access.account_grants g SET revoked_at=CASE WHEN p_command='account_grant.assign' THEN NULL ELSE statement_timestamp() END WHERE g.id=bound.id RETURNING * INTO bound;disposition:='changed';END IF;
 event:=CASE WHEN disposition='unchanged' THEN NULL ELSE gen_random_uuid() END;
 BEGIN
 INSERT INTO access.operation_outcome(id,executor_actor_id,operation_id,command_type,scope_kind,scope_id,command_version,fingerprint_version,fingerprint_algorithm,fingerprint,result_version,result,verified_account_actor_id,target_observed_at)
 VALUES(gen_random_uuid(),executor,p_operation,p_command,'platform',NULL,1,1,'sha256',sha256(p_canonical),1,jsonb_build_object('target',jsonb_build_object('grant_id',bound.id,'account_id',p_account,'permission',p_permission),'disposition',disposition,'revision',bound.revision::text,'event_id',event),observed_actor,observed) RETURNING * INTO saved;
 EXCEPTION WHEN unique_violation THEN
 GET STACKED DIAGNOSTICS violated=CONSTRAINT_NAME;
 IF violated='operation_outcome_executor_actor_id_operation_id_key' THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict';END IF;
 RAISE;
 END;
 IF event IS NOT NULL THEN
 INSERT INTO access.business_event(event_id,event_type,event_version,scope_kind,scope_id,executor_actor_id,operation_id,outcome_id,target,transition,reason_code,evidence_ref)
 VALUES(event,CASE WHEN p_command='account_grant.assign' THEN 'access.account_grant_assigned' ELSE 'access.account_grant_revoked' END,1,'platform',NULL,executor,p_operation,saved.id,saved.result->'target',jsonb_build_object('before',previous,'after',jsonb_build_object('revoked_at',bound.revoked_at,'revision',bound.revision::text)),p_reason,p_evidence);END IF;
 IF executor IS DISTINCT FROM access.account_grant_authority(p_command,app,p_account) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied';END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
CREATE FUNCTION access.account_grant_outcome(p_operation uuid,p_command text,p_account uuid,p_permission text,p_grant uuid)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid;app text;saved access.operation_outcome;lock_document text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'
 OR p_account IS NULL OR p_account='00000000-0000-0000-0000-000000000000' OR p_command IS NULL OR p_command NOT IN ('account_grant.assign','account_grant.revoke')
 OR p_permission IS NULL OR octet_length(p_permission) NOT BETWEEN 1 AND 200 OR octet_length(p_permission)<>length(p_permission)
 OR (p_command='account_grant.assign' AND p_grant IS NOT NULL) OR (p_command='account_grant.revoke' AND (p_grant IS NULL OR p_grant='00000000-0000-0000-0000-000000000000')) THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid';END IF;
 SELECT p.app_id INTO app FROM access.permissions p WHERE p.permission=p_permission AND p.scope_kind='account';
 executor:=access.account_grant_authority(p_command,app,p_account);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied';END IF;
 PERFORM set_config('app.context_kind','setup',true),set_config('app.account_id','',true),set_config('app.org_id','',true),set_config('app.actor_id',executor::text,true),set_config('app.target_account_id',p_account::text,true);
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":'||to_json(p_command)::text||',"lock_version":1,"operation_id":'||to_json(p_operation::text)::text||',"owner_schema":"access","scope_id":null,"scope_kind":"platform"}';
 BEGIN PERFORM pg_advisory_xact_lock(access.command_lock(lock_document));EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='AC001',MESSAGE='access_operation_busy';END;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM access.account_grant_authority(p_command,app,p_account) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied';END IF;
 SELECT * INTO saved FROM access.operation_outcome o WHERE o.scope_kind='platform' AND o.scope_id IS NULL AND o.command_type=p_command AND o.executor_actor_id=executor AND o.operation_id=p_operation;
 IF saved.id IS NULL THEN RETURN;END IF;
 IF saved.result->'target'->>'account_id' IS DISTINCT FROM p_account::text OR saved.result->'target'->>'permission' IS DISTINCT FROM p_permission
 OR (p_command='account_grant.revoke' AND saved.result->'target'->>'grant_id' IS DISTINCT FROM p_grant::text) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied';END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
REVOKE ALL ON FUNCTION access.change_account_grant(uuid,text,uuid,text,uuid,boolean,text,text,text,bytea),access.account_grant_outcome(uuid,text,uuid,text,uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION access.change_account_grant(uuid,text,uuid,text,uuid,boolean,text,text,text,bytea),access.account_grant_outcome(uuid,text,uuid,text,uuid) TO access_operator;
RESET ROLE;
CREATE CONSTRAINT TRIGGER account_grant_required_change AFTER INSERT OR UPDATE ON access.account_grants DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION access.require_account_grant_change();
REVOKE CREATE ON SCHEMA access FROM access_command_owner,access_operator_authority_owner;
'''

# Extend the delivered trigger body with an early account branch. Historical branches
# remain byte-for-byte intact, so existing organization command semantics stay owned.
EVIDENCE_BRANCH=r'''
 IF TG_OP='INSERT' THEN
  IF TG_TABLE_NAME='operation_outcome' THEN
   account_command:=NEW.command_type IN ('account_grant.assign','account_grant.revoke');
  ELSIF TG_TABLE_NAME='business_event' THEN
   account_command:=NEW.event_type IN ('access.account_grant_assigned','access.account_grant_revoked');
  END IF;
 END IF;
 IF account_command THEN
  IF current_user<>'access_command_owner' THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_command_owner_required';END IF;
  IF TG_TABLE_NAME='operation_outcome' THEN
   SELECT * INTO account_bound FROM access.account_grants g WHERE g.id=(NEW.result->'target'->>'grant_id')::uuid;
   SELECT p.app_id INTO account_app FROM access.permissions p WHERE p.permission=account_bound.permission AND p.scope_kind='account';
   account_executor:=access.account_grant_authority(NEW.command_type,account_app,account_bound.account_id);
   IF account_executor IS NULL OR account_executor IS DISTINCT FROM NEW.executor_actor_id OR account_bound.id IS NULL
   OR NEW.scope_kind<>'platform' OR NEW.scope_id IS NOT NULL
   OR NEW.result IS DISTINCT FROM jsonb_build_object('target',jsonb_build_object('grant_id',account_bound.id,'account_id',account_bound.account_id,'permission',account_bound.permission),'disposition',NEW.result->>'disposition','revision',account_bound.revision::text,'event_id',NEW.result->'event_id')
   OR NEW.result->>'disposition' IS NULL OR NEW.result->>'disposition' NOT IN ('created','changed','unchanged')
   OR (NEW.command_type='account_grant.revoke' AND (NEW.result->>'disposition'='created' OR account_bound.revoked_at IS NULL OR NEW.verified_account_actor_id IS NOT NULL OR NEW.target_observed_at IS NOT NULL))
   OR (NEW.command_type='account_grant.assign' AND (account_bound.revoked_at IS NOT NULL OR NEW.verified_account_actor_id IS NULL OR NEW.verified_account_actor_id='00000000-0000-0000-0000-000000000000'
   OR NEW.target_observed_at IS NULL OR NOT isfinite(NEW.target_observed_at) OR NEW.target_observed_at>clock_timestamp() OR clock_timestamp()-NEW.target_observed_at>=interval '5 seconds'))
   OR NEW.verified_membership_revision IS NOT NULL THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_account_result_invalid';END IF;
   IF NEW.result->>'disposition' IN ('created','changed') THEN
    IF (NEW.result->>'event_id')::uuid IS NULL OR (NEW.result->>'event_id')::uuid='00000000-0000-0000-0000-000000000000'
    OR account_bound.updated_by IS DISTINCT FROM account_executor OR account_bound.updated_at IS DISTINCT FROM statement_timestamp()
    OR (NEW.result->>'disposition'='created' AND (account_bound.revision<>1 OR account_bound.created_by IS DISTINCT FROM account_executor OR account_bound.created_at IS DISTINCT FROM statement_timestamp()))
    OR (NEW.result->>'disposition'='changed' AND account_bound.revision<2) THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_account_result_invalid';END IF;
   ELSIF NEW.result->>'event_id' IS NOT NULL THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_unchanged_event_invalid';END IF;
   NEW.committed_at:=statement_timestamp();
  ELSE
   SELECT * INTO account_saved FROM access.operation_outcome o WHERE o.id=NEW.outcome_id;
   SELECT * INTO account_bound FROM access.account_grants g WHERE g.id=(account_saved.result->'target'->>'grant_id')::uuid;
   IF account_saved.id IS NULL OR account_saved.command_type NOT IN ('account_grant.assign','account_grant.revoke')
   OR NEW.event_id IS DISTINCT FROM (account_saved.result->>'event_id')::uuid OR NEW.executor_actor_id IS DISTINCT FROM account_saved.executor_actor_id
   OR NEW.operation_id IS DISTINCT FROM account_saved.operation_id OR NEW.target IS DISTINCT FROM account_saved.result->'target'
   OR NEW.scope_kind<>'platform' OR NEW.scope_id IS NOT NULL OR account_saved.result->>'disposition' NOT IN ('created','changed')
   OR NEW.event_type IS DISTINCT FROM (CASE WHEN account_saved.command_type='account_grant.assign' THEN 'access.account_grant_assigned' ELSE 'access.account_grant_revoked' END)
   OR NEW.transition IS DISTINCT FROM jsonb_build_object('before',NEW.transition->'before','after',jsonb_build_object('revoked_at',account_bound.revoked_at,'revision',account_bound.revision::text))
   OR (account_saved.result->>'disposition'='created' AND NEW.transition->'before' IS DISTINCT FROM 'null'::jsonb)
   OR (account_saved.result->>'disposition'='changed' AND (NEW.transition->'before' IS DISTINCT FROM jsonb_build_object('revoked_at',NEW.transition->'before'->'revoked_at','revision',(account_bound.revision-1)::text)))
   OR account_bound.updated_by IS DISTINCT FROM account_saved.executor_actor_id OR account_bound.updated_at IS DISTINCT FROM account_saved.committed_at THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_account_event_invalid';END IF;
   NEW.created_at:=account_saved.committed_at;
  END IF;RETURN NEW;
 END IF;
'''

def upgrade():
    connection=op.get_bind()
    from access_baseline import verify_catalog,verify_operator_roles
    verify_operator_roles(connection)
    verify_catalog(connection,'access_0016')
    connection.exec_driver_sql(SQL,execution_options={'no_parameters':True})
    definition=connection.exec_driver_sql("SELECT pg_get_functiondef('access.guard_command_evidence()'::regprocedure)").scalar_one()
    definition=definition.replace('BEGIN\n','DECLARE account_bound access.account_grants;account_saved access.operation_outcome;account_app text;account_executor uuid;account_command boolean:=false;\nBEGIN\n'+EVIDENCE_BRANCH,1)
    # Existing function already has a DECLARE block; append declarations to it.
    definition=definition.replace('DECLARE account_bound','account_bound')
    connection.exec_driver_sql(definition,execution_options={'no_parameters':True})
    definition=connection.exec_driver_sql("SELECT pg_get_functiondef('access.require_command_event()'::regprocedure)").scalar_one()
    definition=definition.replace("NEW.command_type='grant.assign'","NEW.command_type IN ('grant.assign','account_grant.assign')")
    connection.exec_driver_sql('GRANT CREATE ON SCHEMA access TO access_command_owner; SET LOCAL ROLE access_command_owner')
    connection.exec_driver_sql(definition,execution_options={'no_parameters':True})
    connection.exec_driver_sql('RESET ROLE; REVOKE CREATE ON SCHEMA access FROM access_command_owner')
    # Clear any inherited/default grants on the new routines, then restore only
    # the required callable boundaries. Never change owner-wide default ACLs.
    connection.exec_driver_sql(r'''DO $acl$
DECLARE r record;a record;grantee text;
BEGIN FOR r IN SELECT p.proowner owner,p.proacl acl,p.oid::regprocedure::text object FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
 WHERE n.nspname='access' AND p.proname IN ('account_grant_authority','guard_account_grant','require_account_grant_change','change_account_grant','account_grant_outcome') LOOP
 EXECUTE format('SET LOCAL ROLE %I',pg_get_userbyid(r.owner));
 EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.object);
 FOR a IN SELECT DISTINCT x.grantee FROM aclexplode(r.acl) x WHERE x.grantee<>r.owner LOOP
 grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
 EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s',r.object,grantee);END LOOP;RESET ROLE;END LOOP;END $acl$;
SET LOCAL ROLE access_operator_authority_owner;
GRANT EXECUTE ON FUNCTION access.account_grant_authority(text,text,uuid) TO access_command_owner;
RESET ROLE;
SET LOCAL ROLE access_command_owner;
GRANT EXECUTE ON FUNCTION access.change_account_grant(uuid,text,uuid,text,uuid,boolean,text,text,text,bytea),access.account_grant_outcome(uuid,text,uuid,text,uuid) TO access_operator;
RESET ROLE;
''',execution_options={'no_parameters':True})

def downgrade():raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
