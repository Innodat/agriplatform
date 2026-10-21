"""Protected first join/rejoin, retained history, and coordinated writer cutover."""
from alembic import op

revision = 'identity_0017'
down_revision = 'identity_0016'
branch_labels = None
depends_on = None

MEMBERSHIP_JOIN_COMMAND_SQL = r"""
CREATE FUNCTION identity.membership_join_executor(p_org uuid,p_account uuid,p_owner boolean DEFAULT false) RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT executor_actor_id FROM identity.current_operator_authority('membership.join','organization',p_org,p_account)
 WHERE NOT p_owner OR executor_actor_id=(SELECT executor_actor_id FROM identity.current_operator_authority('membership.join_owner','organization',p_org,p_account))
$f$;
ALTER TABLE identity.operation_outcome DROP CONSTRAINT operation_outcome_command_type_check;
ALTER TABLE identity.operation_outcome ADD CONSTRAINT operation_outcome_command_type_check CHECK(command_type IN ('actor.register_system','membership.retire','membership.join'));
ALTER TABLE identity.operation_outcome DROP CONSTRAINT operation_outcome_check1;
ALTER TABLE identity.operation_outcome ADD CONSTRAINT operation_outcome_check1 CHECK(initiator_actor_id IS NULL AND ((command_type='actor.register_system' AND scope_kind='platform') OR (command_type IN ('membership.retire','membership.join') AND scope_kind='organization')));
ALTER TABLE identity.business_event DROP CONSTRAINT business_event_event_type_check;
ALTER TABLE identity.business_event ADD CONSTRAINT business_event_event_type_check CHECK(event_type IN ('identity.actor_registered','identity.membership_retired','identity.membership_joined'));
ALTER TABLE identity.business_event DROP CONSTRAINT business_event_check1;
ALTER TABLE identity.business_event ADD CONSTRAINT business_event_check1 CHECK(initiator_actor_id IS NULL AND ((event_type='identity.actor_registered' AND scope_kind='platform') OR (event_type IN ('identity.membership_retired','identity.membership_joined') AND scope_kind='organization')));
CREATE POLICY membership_join_outcome ON identity.operation_outcome TO identity_command_owner
 USING(command_type='membership.join' AND scope_kind='organization' AND executor_actor_id=identity.membership_join_executor(scope_id,(result->'target'->>'account_id')::uuid))
 WITH CHECK(command_type='membership.join' AND scope_kind='organization' AND executor_actor_id=identity.membership_join_executor(scope_id,(result->'target'->>'account_id')::uuid));
CREATE POLICY membership_join_event ON identity.business_event TO identity_command_owner
 USING(event_type='identity.membership_joined' AND scope_kind='organization' AND executor_actor_id=identity.membership_join_executor(scope_id,(target->>'account_id')::uuid))
 WITH CHECK(event_type='identity.membership_joined' AND scope_kind='organization' AND executor_actor_id=identity.membership_join_executor(scope_id,(target->>'account_id')::uuid));
CREATE POLICY membership_join_command ON identity.org_member TO identity_command_owner
 USING(identity.membership_join_executor(org_id,user_id) IS NOT NULL)
 WITH CHECK(identity.membership_join_executor(org_id,user_id,is_owner) IS NOT NULL);
ALTER POLICY membership_retirement_bound ON identity.org_member
 USING(identity.membership_retirement_executor(org_id,user_id) IS NOT NULL OR identity.membership_join_executor(org_id,user_id) IS NOT NULL)
 WITH CHECK(identity.membership_retirement_executor(org_id,user_id) IS NOT NULL OR identity.membership_join_executor(org_id,user_id,is_owner) IS NOT NULL);
-- Local existence validation deliberately does not require membership or live Auth.
GRANT USAGE ON SCHEMA auth TO identity_command_owner;
GRANT SELECT(id,deleted_at),UPDATE(id) ON identity.users,identity.org TO identity_command_owner;

CREATE FUNCTION identity.membership_join_profile_allowed(p_account uuid) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT EXISTS(SELECT 1 FROM identity.operator_principals p JOIN identity.operator_authorities a USING(database_login)
 WHERE p.database_login=session_user AND p.enabled AND a.enabled AND a.command='membership.join' AND a.scope_kind='organization'
 AND a.application_id IS NULL AND (a.target_account_id IS NULL OR a.target_account_id=p_account))
$f$;
CREATE FUNCTION identity.membership_join_org_allowed(p_org uuid) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT EXISTS(SELECT 1 FROM identity.operator_principals p JOIN identity.operator_authorities a USING(database_login)
 WHERE p.database_login=session_user AND p.enabled AND a.enabled AND a.command='membership.join' AND a.scope_kind='organization'
 AND a.org_id=p_org AND a.application_id IS NULL)
$f$;
CREATE POLICY membership_join_profile ON identity.users FOR SELECT TO identity_command_owner USING(identity.membership_join_profile_allowed(id));
CREATE POLICY membership_join_org ON identity.org FOR SELECT TO identity_command_owner USING(identity.membership_join_org_allowed(id));
CREATE POLICY membership_join_profile_lock ON identity.users FOR UPDATE TO identity_command_owner USING(identity.membership_join_profile_allowed(id)) WITH CHECK(identity.membership_join_profile_allowed(id));
CREATE POLICY membership_join_org_lock ON identity.org FOR UPDATE TO identity_command_owner USING(identity.membership_join_org_allowed(id)) WITH CHECK(identity.membership_join_org_allowed(id));
CREATE POLICY membership_join_profile_bound ON identity.users AS RESTRICTIVE FOR SELECT TO identity_command_owner USING(identity.membership_join_profile_allowed(id));
CREATE POLICY membership_join_org_bound ON identity.org AS RESTRICTIVE FOR SELECT TO identity_command_owner USING(identity.membership_join_org_allowed(id));

GRANT EXECUTE ON FUNCTION identity.membership_join_profile_allowed(uuid),identity.membership_join_org_allowed(uuid) TO identity_command_owner;
GRANT CREATE ON SCHEMA identity TO identity_operator_authority_owner;
ALTER FUNCTION identity.membership_join_profile_allowed(uuid) OWNER TO identity_operator_authority_owner;
ALTER FUNCTION identity.membership_join_org_allowed(uuid) OWNER TO identity_operator_authority_owner;
REVOKE CREATE ON SCHEMA identity FROM identity_operator_authority_owner;
CREATE OR REPLACE FUNCTION identity.guard_org_member_retirement_owner() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF TG_OP='INSERT' THEN
  IF current_user NOT IN ('identity_migrator','identity_command_owner') THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_membership_join_owner_required'; END IF;
  IF current_user='identity_command_owner' THEN
   IF NEW.deleted_at IS NOT NULL OR NEW.created_actor_id IS DISTINCT FROM identity.membership_join_executor(NEW.org_id,NEW.user_id,NEW.is_owner)
    OR NEW.created_actor_id IS NULL OR NEW.updated_actor_id IS DISTINCT FROM NEW.created_actor_id
    OR NEW.created_by IS NOT NULL OR NEW.updated_by IS NOT NULL THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_membership_join_owner_required'; END IF;
   NEW.created_at:=statement_timestamp(); NEW.updated_at:=NEW.created_at;
  END IF;
  RETURN NEW;
 END IF;
 IF NEW.is_owner IS DISTINCT FROM OLD.is_owner AND current_user<>'identity_migrator' THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_membership_owner_change_prohibited'; END IF;
 IF ((TG_OP='INSERT' AND NEW.deleted_at IS NOT NULL) OR
     (TG_OP='UPDATE' AND NEW.deleted_at IS DISTINCT FROM OLD.deleted_at)) AND
     current_user NOT IN ('identity_migrator','identity_command_owner') THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_membership_retirement_owner_required'; END IF;
 IF current_user='identity_command_owner' THEN
  IF TG_OP<>'UPDATE' OR OLD.deleted_at IS NOT NULL OR NEW.deleted_at IS NULL
   OR NEW.updated_actor_id IS DISTINCT FROM identity.membership_retirement_executor(NEW.org_id,NEW.user_id)
   OR (to_jsonb(NEW)-ARRAY['deleted_at','updated_at','updated_actor_id','revision']) IS DISTINCT FROM
      (to_jsonb(OLD)-ARRAY['deleted_at','updated_at','updated_actor_id','revision']) THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_membership_retirement_owner_required'; END IF;
  NEW.deleted_at:=statement_timestamp(); NEW.updated_at:=NEW.deleted_at;
 END IF;
 RETURN NEW;
END $f$;
CREATE OR REPLACE FUNCTION identity.guard_org_member_actor_attribution()
RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF TG_OP='UPDATE' AND OLD.created_actor_id IS NOT NULL AND NEW.created_actor_id IS DISTINCT FROM OLD.created_actor_id THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_membership_creation_actor_immutable',CONSTRAINT='org_member_creation_actor_immutable'; END IF;
 IF current_user <> 'identity_migrator' AND
  ((TG_OP='INSERT' AND (NEW.created_actor_id IS NOT NULL OR NEW.updated_actor_id IS NOT NULL)) OR
   (TG_OP='UPDATE' AND (NEW.created_actor_id IS DISTINCT FROM OLD.created_actor_id OR NEW.updated_actor_id IS DISTINCT FROM OLD.updated_actor_id))) THEN
  IF NOT ((TG_OP='INSERT' AND current_user='identity_command_owner' AND NEW.created_actor_id=identity.membership_join_executor(NEW.org_id,NEW.user_id,NEW.is_owner) AND NEW.updated_actor_id=NEW.created_actor_id) OR (TG_OP='UPDATE' AND current_user='identity_command_owner' AND OLD.deleted_at IS NULL AND NEW.deleted_at IS NOT NULL
   AND NEW.created_actor_id IS NOT DISTINCT FROM OLD.created_actor_id
   AND NEW.updated_actor_id=identity.membership_retirement_executor(NEW.org_id,NEW.user_id))) THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_membership_actor_owner_required',CONSTRAINT='org_member_actor_owner_required'; END IF;
 END IF;
 RETURN NEW;
END $f$;
CREATE OR REPLACE FUNCTION identity.guard_command_evidence() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
DECLARE o identity.operation_outcome; actor_id uuid;
BEGIN
 IF TG_OP<>'INSERT' THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_command_evidence_immutable';
 END IF;

 IF coalesce(to_jsonb(NEW)->>'command_type','')='membership.join' OR coalesce(to_jsonb(NEW)->>'event_type','')='identity.membership_joined' THEN
  IF TG_TABLE_NAME='operation_outcome' THEN
   IF current_user<>'identity_command_owner' OR NEW.executor_actor_id IS DISTINCT FROM identity.membership_join_executor(NEW.scope_id,(NEW.result->'target'->>'account_id')::uuid) THEN
    RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_command_owner_required'; END IF;
   IF NEW.command_version<>1 OR NEW.result_version<>1 OR NEW.scope_kind<>'organization'
    OR NEW.result->>'disposition' IS DISTINCT FROM 'created' OR NEW.result->>'event_id' IS NULL
    OR (NEW.result->>'event_id')::uuid='00000000-0000-0000-0000-000000000000'::uuid
    OR NOT EXISTS(SELECT 1 FROM identity.org_member m WHERE m.id::text=NEW.result->'target'->>'membership_id'
     AND m.org_id=NEW.scope_id AND m.user_id=(NEW.result->'target'->>'account_id')::uuid AND m.deleted_at IS NULL AND m.revision=1
     AND m.created_actor_id=NEW.executor_actor_id AND m.updated_actor_id=NEW.executor_actor_id
     AND NEW.result=jsonb_build_object('target',jsonb_build_object('org_id',m.org_id,'account_id',m.user_id,'membership_id',m.id::text),
      'disposition','created','revision','1','event_id',(NEW.result->>'event_id')::uuid)) THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_command_result_invalid'; END IF;
   NEW.committed_at:=statement_timestamp();
  ELSE
   SELECT * INTO o FROM identity.operation_outcome WHERE id=NEW.outcome_id;
   IF current_user<>'identity_command_owner' OR NEW.executor_actor_id IS DISTINCT FROM identity.membership_join_executor(NEW.scope_id,(NEW.target->>'account_id')::uuid) THEN
    RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_command_owner_required'; END IF;
   IF o.id IS NULL OR o.command_type<>'membership.join' OR NEW.event_version<>1
    OR NEW.scope_kind IS DISTINCT FROM o.scope_kind OR NEW.scope_id IS DISTINCT FROM o.scope_id
    OR NEW.executor_actor_id IS DISTINCT FROM o.executor_actor_id OR NEW.initiator_actor_id IS DISTINCT FROM o.initiator_actor_id
    OR NEW.event_id IS DISTINCT FROM (o.result->>'event_id')::uuid OR NEW.target IS DISTINCT FROM o.result->'target'
    OR NEW.target_key IS DISTINCT FROM NEW.target->>'membership_id'
    OR NOT EXISTS(SELECT 1 FROM identity.org_member m WHERE m.id::text=NEW.target_key AND m.org_id=NEW.scope_id
     AND m.user_id=(NEW.target->>'account_id')::uuid AND m.deleted_at IS NULL AND m.revision=1
     AND NEW.transition=jsonb_build_object('before',jsonb_build_object('previous_membership_id',
       (SELECT max(h.id)::text FROM identity.org_member h WHERE h.org_id=m.org_id AND h.user_id=m.user_id AND h.id<m.id)),
       'after',jsonb_build_object('revision','1','retired',false,'is_owner',m.is_owner))) THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_command_event_invalid'; END IF;
   NEW.created_at:=o.committed_at;
  END IF;
  RETURN NEW;
 END IF;
 IF coalesce(to_jsonb(NEW)->>'command_type','')='membership.retire'
    OR coalesce(to_jsonb(NEW)->>'event_type','')='identity.membership_retired' THEN
  IF TG_TABLE_NAME='operation_outcome' THEN
   IF current_user<>'identity_command_owner' OR NEW.executor_actor_id IS DISTINCT FROM
      identity.membership_retirement_executor(NEW.scope_id,(NEW.result->'target'->>'account_id')::uuid) THEN
    RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_command_owner_required'; END IF;
   IF NEW.command_version<>1 OR NEW.result_version<>1 OR NEW.scope_kind<>'organization'
    OR NEW.result->>'disposition' IS DISTINCT FROM 'changed'
    OR NOT EXISTS(SELECT 1 FROM identity.org_member m WHERE m.id::text=NEW.result->'target'->>'membership_id'
      AND m.org_id=NEW.scope_id AND m.user_id=(NEW.result->'target'->>'account_id')::uuid
      AND m.deleted_at IS NOT NULL AND m.updated_actor_id=NEW.executor_actor_id
      AND NEW.result=jsonb_build_object('target',jsonb_build_object('org_id',m.org_id,'account_id',m.user_id,'membership_id',m.id::text),
       'disposition','changed','revision',m.revision::text,'event_id',(NEW.result->>'event_id')::uuid))
    OR NEW.result->>'event_id' IS NULL OR (NEW.result->>'event_id')::uuid='00000000-0000-0000-0000-000000000000'::uuid THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_command_result_invalid'; END IF;
   NEW.committed_at:=statement_timestamp();
  ELSE
   SELECT * INTO o FROM identity.operation_outcome WHERE id=NEW.outcome_id;
   IF current_user<>'identity_command_owner' OR NEW.executor_actor_id IS DISTINCT FROM
      identity.membership_retirement_executor(NEW.scope_id,(NEW.target->>'account_id')::uuid) THEN
    RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_command_owner_required'; END IF;
   IF o.id IS NULL OR o.command_type<>'membership.retire' OR NEW.event_version<>1
    OR NEW.scope_kind IS DISTINCT FROM o.scope_kind OR NEW.scope_id IS DISTINCT FROM o.scope_id
    OR NEW.executor_actor_id IS DISTINCT FROM o.executor_actor_id OR NEW.initiator_actor_id IS DISTINCT FROM o.initiator_actor_id
    OR NEW.event_id IS DISTINCT FROM (o.result->>'event_id')::uuid OR NEW.target IS DISTINCT FROM o.result->'target'
    OR NEW.target_key IS DISTINCT FROM NEW.target->>'membership_id'
    OR NOT EXISTS(SELECT 1 FROM identity.org_member m WHERE m.id::text=NEW.target_key
     AND m.org_id=NEW.scope_id AND m.user_id=(NEW.target->>'account_id')::uuid AND m.deleted_at IS NOT NULL
     AND NEW.transition=jsonb_build_object('before',jsonb_build_object('revision',(m.revision-1)::text,'retired',false),
         'after',jsonb_build_object('revision',m.revision::text,'retired',true))) THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_command_event_invalid'; END IF;
   NEW.created_at:=o.committed_at;
  END IF;
  RETURN NEW;
 END IF;
 IF current_user<>'identity_command_owner' OR NEW.executor_actor_id IS DISTINCT FROM identity.command_executor() THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_command_owner_required';
 END IF;
 IF TG_TABLE_NAME='operation_outcome' THEN
  IF NEW.result_version=1 THEN
   actor_id:=(NEW.result->'target'->>'actor_id')::uuid;
   IF actor_id IS NULL OR actor_id='00000000-0000-0000-0000-000000000000'::uuid
    OR NEW.result IS DISTINCT FROM jsonb_build_object('target',jsonb_build_object('actor_id',actor_id),
       'disposition',NEW.result->>'disposition','revision',NULL,'event_id',NEW.result->'event_id')
    OR NEW.result->>'disposition' IS NULL OR NEW.result->>'disposition' NOT IN ('created','unchanged')
    OR (NEW.result->>'disposition'='created' AND
      (NEW.result->>'event_id' IS NULL OR (NEW.result->>'event_id')::uuid='00000000-0000-0000-0000-000000000000'::uuid))
    OR (NEW.result->>'disposition'='unchanged' AND NEW.result->>'event_id' IS NOT NULL) THEN
     RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_command_result_invalid';
   END IF;
   PERFORM 1 FROM identity.actor WHERE id=actor_id;
   IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='23503',MESSAGE='identity_command_actor_missing'; END IF;
  END IF;
  NEW.committed_at:=statement_timestamp();
 ELSE
  SELECT * INTO o FROM identity.operation_outcome WHERE id=NEW.outcome_id;
  IF NOT FOUND OR NEW.event_version<>1 OR NEW.scope_kind IS DISTINCT FROM o.scope_kind
   OR NEW.scope_id IS DISTINCT FROM o.scope_id OR NEW.executor_actor_id IS DISTINCT FROM o.executor_actor_id
   OR NEW.initiator_actor_id IS DISTINCT FROM o.initiator_actor_id
   OR o.result->>'disposition'<>'created' OR NEW.event_id IS DISTINCT FROM (o.result->>'event_id')::uuid
   OR NEW.target IS DISTINCT FROM o.result->'target' OR NEW.target_key IS DISTINCT FROM NEW.target->>'actor_id'
   OR NOT EXISTS(SELECT 1 FROM identity.actor a WHERE a.id=(NEW.target->>'actor_id')::uuid
       AND NEW.transition=jsonb_build_object('kind',a.kind,'actor_key',a.actor_key)) THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_command_event_invalid';
  END IF;
  NEW.created_at:=o.committed_at;
 END IF;
 RETURN NEW;
END $f$;
CREATE FUNCTION identity.join_membership(p_operation uuid,p_org uuid,p_account uuid,p_previous bigint,p_owner boolean,
 p_reason text,p_evidence text,p_canonical bytea)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; canonical text; lock_document text; saved identity.operation_outcome;
 existing identity.org_member; previous_id bigint; allocated bigint; outcome_id uuid; event_id uuid; response jsonb;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR
 p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid OR
 p_org IS NULL OR p_org='00000000-0000-0000-0000-000000000000'::uuid OR
 p_account IS NULL OR p_account='00000000-0000-0000-0000-000000000000'::uuid OR
 (p_previous IS NOT NULL AND p_previous<=0) OR p_owner IS NULL OR
 p_reason IS NULL OR p_reason NOT IN ('initial_setup','synthetic_fixture','identity_adoption','access_change','setup_correction') OR
 (p_evidence IS NOT NULL AND (p_evidence COLLATE "C" !~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$' OR position('://' in p_evidence)>0)) THEN
  RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
 canonical:='{"command":"membership.join","evidence_ref":'||coalesce(to_json(p_evidence)::text,'null')||
 ',"operation_id":'||to_json(p_operation::text)::text||',"payload":{"account_id":'||to_json(p_account::text)::text||
 ',"expected_previous_membership_id":'||coalesce(to_json(p_previous::text)::text,'null')||',"is_owner":'||to_json(p_owner)::text||
 '},"reason_code":'||to_json(p_reason)::text||',"schema_version":1,"scope":{"kind":"organization","org_id":'||to_json(p_org::text)::text||'}}';
 IF p_canonical IS DISTINCT FROM convert_to(canonical,'UTF8') THEN
  RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
 executor:=identity.membership_join_executor(p_org,p_account,p_owner);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"membership.join","lock_version":1,"operation_id":'||
 to_json(p_operation::text)::text||',"owner_schema":"identity","scope_id":'||to_json(p_org::text)::text||',"scope_kind":"organization"}';
 BEGIN
  PERFORM pg_advisory_xact_lock(identity.command_lock(lock_document));
 EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='IC001',MESSAGE='identity_operation_busy'; END;
 -- Serialize shared history and the exact row before holding the authority lock.
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:membership:v1:'||p_org::text||':'||p_account::text));

 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM identity.membership_join_executor(p_org,p_account,p_owner) THEN
  RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 SELECT * INTO saved FROM identity.operation_outcome o WHERE o.scope_kind='organization' AND o.scope_id=p_org
  AND o.executor_actor_id=executor AND o.command_type='membership.join' AND o.operation_id=p_operation;
 IF FOUND THEN
  IF saved.command_version<>1 OR saved.fingerprint_version<>1 OR saved.fingerprint_algorithm<>'sha256'
   OR saved.fingerprint_key_id IS NOT NULL OR saved.result_version<>1 THEN
   RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
  IF saved.fingerprint<>sha256(p_canonical) THEN RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_operation_conflict'; END IF;
  RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at; RETURN;
 END IF;
 -- Validate local references after all serialization waits, lock against retirement/deletion.
 PERFORM 1 FROM identity.users WHERE id=p_account AND deleted_at IS NULL FOR SHARE;
 IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_membership_conflict'; END IF;
 PERFORM 1 FROM identity.org WHERE id=p_org AND deleted_at IS NULL FOR SHARE;
 IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_membership_conflict'; END IF;
 SELECT max(m.id) INTO previous_id FROM identity.org_member m WHERE m.org_id=p_org AND m.user_id=p_account;
 IF previous_id IS DISTINCT FROM p_previous OR EXISTS(SELECT 1 FROM identity.org_member m WHERE m.org_id=p_org AND m.user_id=p_account AND m.deleted_at IS NULL) THEN
  RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_membership_conflict'; END IF;
 allocated:=nextval('identity.org_member_id_seq'::regclass);
 -- Never silently repair an unsafe owner sequence or issue an ID below retained history.
 IF allocated<=0 OR EXISTS(SELECT 1 FROM identity.org_member m WHERE m.id>=allocated) THEN
  RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_membership_sequence_conflict'; END IF;
 INSERT INTO identity.org_member(id,org_id,user_id,is_owner,created_actor_id,updated_actor_id,created_by,updated_by)
 VALUES(allocated,p_org,p_account,p_owner,executor,executor,NULL,NULL) RETURNING * INTO existing;
 outcome_id:=gen_random_uuid(); event_id:=gen_random_uuid();
 response:=jsonb_build_object('target',jsonb_build_object('org_id',p_org,'account_id',p_account,'membership_id',existing.id::text),
  'disposition','created','revision',existing.revision::text,'event_id',event_id);
 INSERT INTO identity.operation_outcome(id,scope_kind,scope_id,executor_actor_id,command_type,operation_id,
 command_version,fingerprint_version,fingerprint_algorithm,fingerprint_key_id,fingerprint,result_version,result,initiator_actor_id)
 VALUES(outcome_id,'organization',p_org,executor,'membership.join',p_operation,1,1,'sha256',NULL,sha256(p_canonical),1,response,NULL) RETURNING * INTO saved;
 INSERT INTO identity.business_event(event_id,event_type,event_version,scope_kind,scope_id,executor_actor_id,
 initiator_actor_id,outcome_id,target_key,target,transition,reason_code,evidence_ref)
 VALUES(event_id,'identity.membership_joined',1,'organization',p_org,executor,NULL,outcome_id,existing.id::text,response->'target',
  jsonb_build_object('before',jsonb_build_object('previous_membership_id',p_previous::text),
   'after',jsonb_build_object('revision','1','retired',false,'is_owner',p_owner)),p_reason,p_evidence);
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
CREATE FUNCTION identity.membership_join_outcome(p_operation uuid,p_org uuid,p_account uuid)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; saved identity.operation_outcome; lock_document text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid
 OR p_org IS NULL OR p_org='00000000-0000-0000-0000-000000000000'::uuid OR p_account IS NULL OR p_account='00000000-0000-0000-0000-000000000000'::uuid THEN
  RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
 executor:=identity.membership_join_executor(p_org,p_account);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"membership.join","lock_version":1,"operation_id":'||
 to_json(p_operation::text)::text||',"owner_schema":"identity","scope_id":'||to_json(p_org::text)::text||',"scope_kind":"organization"}';
 BEGIN PERFORM pg_advisory_xact_lock(identity.command_lock(lock_document));
 EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='IC001',MESSAGE='identity_operation_busy'; END;
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM identity.membership_join_executor(p_org,p_account) THEN
  RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 SELECT * INTO saved FROM identity.operation_outcome o WHERE o.scope_kind='organization' AND o.scope_id=p_org
 AND o.executor_actor_id=executor AND o.command_type='membership.join' AND o.operation_id=p_operation
 AND o.result->'target'->>'account_id'=p_account::text;
 IF NOT FOUND THEN RETURN; END IF;
 IF saved.command_version<>1 OR saved.fingerprint_version<>1 OR saved.fingerprint_algorithm<>'sha256'
 OR saved.fingerprint_key_id IS NOT NULL OR saved.result_version<>1 THEN
  RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
 IF EXISTS(SELECT 1 FROM identity.business_event e WHERE e.outcome_id=saved.id AND e.transition->'after'->>'is_owner'='true')
 AND executor IS DISTINCT FROM identity.membership_join_executor(p_org,p_account,true) THEN
  RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;

GRANT INSERT ON identity.org_member TO identity_command_owner;
GRANT USAGE ON SEQUENCE identity.org_member_id_seq TO identity_command_owner;
ALTER TABLE identity.org_member DROP CONSTRAINT org_member_org_id_user_id_key;
DO $acl$
DECLARE r record; a record; grantee text;
BEGIN
 FOR r IN SELECT p.proowner owner,p.proacl acl,p.oid::regprocedure::text object FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
 WHERE n.nspname='identity' AND p.proname IN ('membership_join_executor','membership_join_profile_allowed','membership_join_org_allowed','join_membership','membership_join_outcome') LOOP
  EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.object);
  FOR a IN SELECT DISTINCT x.grantee FROM aclexplode(r.acl) x WHERE x.grantee<>r.owner LOOP
   grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
   EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s',r.object,grantee);
  END LOOP;
 END LOOP;
END $acl$;
GRANT EXECUTE ON FUNCTION identity.membership_join_executor(uuid,uuid,boolean),identity.membership_join_profile_allowed(uuid),identity.membership_join_org_allowed(uuid) TO identity_command_owner;
GRANT EXECUTE ON FUNCTION identity.join_membership(uuid,uuid,uuid,bigint,boolean,text,text,bytea),identity.membership_join_outcome(uuid,uuid,uuid) TO identity_operator;
GRANT CREATE ON SCHEMA identity TO identity_command_owner;
ALTER FUNCTION identity.membership_join_executor(uuid,uuid,boolean) OWNER TO identity_command_owner;
ALTER FUNCTION identity.join_membership(uuid,uuid,uuid,bigint,boolean,text,text,bytea) OWNER TO identity_command_owner;
ALTER FUNCTION identity.membership_join_outcome(uuid,uuid,uuid) OWNER TO identity_command_owner;
REVOKE CREATE ON SCHEMA identity FROM identity_command_owner;
"""


def upgrade():
    op.get_bind().exec_driver_sql(MEMBERSHIP_JOIN_COMMAND_SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
