"""Protected exact-member retirement with atomic immutable outcome/evidence."""
from alembic import op

revision = 'identity_0016'
down_revision = 'identity_0015'
branch_labels = None
depends_on = None

MEMBERSHIP_RETIRE_COMMAND_SQL = r"""
CREATE FUNCTION identity.membership_retirement_executor(p_org uuid,p_account uuid) RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT executor_actor_id FROM identity.current_operator_authority('membership.retire','organization',p_org,p_account)
$f$;

ALTER TABLE identity.operation_outcome DROP CONSTRAINT operation_outcome_command_type_check;
ALTER TABLE identity.operation_outcome ADD CONSTRAINT operation_outcome_command_type_check
 CHECK(command_type IN ('actor.register_system','membership.retire'));
ALTER TABLE identity.operation_outcome DROP CONSTRAINT operation_outcome_check1;
ALTER TABLE identity.operation_outcome ADD CONSTRAINT operation_outcome_check1
 CHECK(initiator_actor_id IS NULL AND ((command_type='actor.register_system' AND scope_kind='platform') OR
 (command_type='membership.retire' AND scope_kind='organization')));
ALTER TABLE identity.business_event DROP CONSTRAINT business_event_event_type_check;
ALTER TABLE identity.business_event ADD CONSTRAINT business_event_event_type_check
 CHECK(event_type IN ('identity.actor_registered','identity.membership_retired'));
ALTER TABLE identity.business_event DROP CONSTRAINT business_event_check1;
ALTER TABLE identity.business_event ADD CONSTRAINT business_event_check1
 CHECK(initiator_actor_id IS NULL AND ((event_type='identity.actor_registered' AND scope_kind='platform') OR
 (event_type='identity.membership_retired' AND scope_kind='organization')));

CREATE POLICY membership_retirement_outcome ON identity.operation_outcome TO identity_command_owner
 USING(command_type='membership.retire' AND scope_kind='organization' AND
 executor_actor_id=identity.membership_retirement_executor(scope_id,(result->'target'->>'account_id')::uuid))
 WITH CHECK(command_type='membership.retire' AND scope_kind='organization' AND
 executor_actor_id=identity.membership_retirement_executor(scope_id,(result->'target'->>'account_id')::uuid));
CREATE POLICY membership_retirement_event ON identity.business_event TO identity_command_owner
 USING(event_type='identity.membership_retired' AND scope_kind='organization' AND
 executor_actor_id=identity.membership_retirement_executor(scope_id,(target->>'account_id')::uuid))
 WITH CHECK(event_type='identity.membership_retired' AND scope_kind='organization' AND
 executor_actor_id=identity.membership_retirement_executor(scope_id,(target->>'account_id')::uuid));
CREATE POLICY membership_retirement_command ON identity.org_member TO identity_command_owner
 USING(identity.membership_retirement_executor(org_id,user_id) IS NOT NULL)
 WITH CHECK(identity.membership_retirement_executor(org_id,user_id) IS NOT NULL);
CREATE POLICY membership_retirement_bound ON identity.org_member AS RESTRICTIVE TO identity_command_owner
 USING(identity.membership_retirement_executor(org_id,user_id) IS NOT NULL)
 WITH CHECK(identity.membership_retirement_executor(org_id,user_id) IS NOT NULL);

CREATE FUNCTION identity.guard_org_member_retirement_owner() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
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
CREATE TRIGGER org_member_command_retirement_guard BEFORE INSERT OR UPDATE ON identity.org_member
 FOR EACH ROW EXECUTE FUNCTION identity.guard_org_member_retirement_owner();

CREATE OR REPLACE FUNCTION identity.guard_org_member_actor_attribution()
RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF TG_OP='UPDATE' AND OLD.created_actor_id IS NOT NULL AND NEW.created_actor_id IS DISTINCT FROM OLD.created_actor_id THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_membership_creation_actor_immutable',CONSTRAINT='org_member_creation_actor_immutable'; END IF;
 IF current_user <> 'identity_migrator' AND
  ((TG_OP='INSERT' AND (NEW.created_actor_id IS NOT NULL OR NEW.updated_actor_id IS NOT NULL)) OR
   (TG_OP='UPDATE' AND (NEW.created_actor_id IS DISTINCT FROM OLD.created_actor_id OR NEW.updated_actor_id IS DISTINCT FROM OLD.updated_actor_id))) THEN
  IF NOT (TG_OP='UPDATE' AND current_user='identity_command_owner' AND OLD.deleted_at IS NULL AND NEW.deleted_at IS NOT NULL
   AND NEW.created_actor_id IS NOT DISTINCT FROM OLD.created_actor_id
   AND NEW.updated_actor_id=identity.membership_retirement_executor(NEW.org_id,NEW.user_id)) THEN
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
CREATE OR REPLACE FUNCTION identity.require_command_event() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF NEW.result_version=1 AND NEW.result->>'disposition' IN ('created','changed') AND NOT EXISTS
 (SELECT 1 FROM identity.business_event e WHERE e.outcome_id=NEW.id AND e.event_id=(NEW.result->>'event_id')::uuid) THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_command_event_missing';
 END IF; RETURN NULL;
END $f$;

CREATE FUNCTION identity.retire_membership(p_operation uuid,p_org uuid,p_account uuid,p_member bigint,p_revision bigint,
 p_reason text,p_evidence text,p_canonical bytea)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; canonical text; lock_document text; saved identity.operation_outcome;
 existing identity.org_member; outcome_id uuid; event_id uuid; response jsonb;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR
 p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid OR
 p_org IS NULL OR p_org='00000000-0000-0000-0000-000000000000'::uuid OR
 p_account IS NULL OR p_account='00000000-0000-0000-0000-000000000000'::uuid OR
 p_member IS NULL OR p_member<=0 OR p_revision IS NULL OR p_revision<=0 OR
 p_reason IS NULL OR p_reason NOT IN ('initial_setup','synthetic_fixture','identity_adoption','access_change','setup_correction') OR
 (p_evidence IS NOT NULL AND (p_evidence COLLATE "C" !~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$' OR position('://' in p_evidence)>0)) THEN
  RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
 canonical:='{"command":"membership.retire","evidence_ref":'||coalesce(to_json(p_evidence)::text,'null')||
 ',"operation_id":'||to_json(p_operation::text)::text||',"payload":{"account_id":'||to_json(p_account::text)::text||
 ',"expected_revision":'||to_json(p_revision::text)::text||',"membership_id":'||to_json(p_member::text)::text||
 '},"reason_code":'||to_json(p_reason)::text||',"schema_version":1,"scope":{"kind":"organization","org_id":'||to_json(p_org::text)::text||'}}';
 IF p_canonical IS DISTINCT FROM convert_to(canonical,'UTF8') THEN
  RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
 executor:=identity.membership_retirement_executor(p_org,p_account);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"membership.retire","lock_version":1,"operation_id":'||
 to_json(p_operation::text)::text||',"owner_schema":"identity","scope_id":'||to_json(p_org::text)::text||',"scope_kind":"organization"}';
 BEGIN
  PERFORM pg_advisory_xact_lock(identity.command_lock(lock_document));
 EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='IC001',MESSAGE='identity_operation_busy'; END;
 -- Serialize shared history and the exact row before holding the authority lock.
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:membership:v1:'||p_org::text||':'||p_account::text));
 SELECT * INTO existing FROM identity.org_member m WHERE m.id=p_member AND m.org_id=p_org AND m.user_id=p_account FOR UPDATE;
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM identity.membership_retirement_executor(p_org,p_account) THEN
  RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 SELECT * INTO saved FROM identity.operation_outcome o WHERE o.scope_kind='organization' AND o.scope_id=p_org
  AND o.executor_actor_id=executor AND o.command_type='membership.retire' AND o.operation_id=p_operation;
 IF FOUND THEN
  IF saved.command_version<>1 OR saved.fingerprint_version<>1 OR saved.fingerprint_algorithm<>'sha256'
   OR saved.fingerprint_key_id IS NOT NULL OR saved.result_version<>1 THEN
   RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
  IF saved.fingerprint<>sha256(p_canonical) THEN RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_operation_conflict'; END IF;
  RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at; RETURN;
 END IF;
 IF existing.id IS NULL OR existing.deleted_at IS NOT NULL OR existing.revision<>p_revision OR existing.revision=9223372036854775807 THEN
  RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_membership_conflict'; END IF;
 UPDATE identity.org_member m SET deleted_at=statement_timestamp(),updated_at=statement_timestamp(),updated_actor_id=executor
  WHERE m.id=p_member AND m.org_id=p_org AND m.user_id=p_account AND m.revision=p_revision AND m.deleted_at IS NULL
  RETURNING * INTO existing;
 IF NOT FOUND THEN RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_membership_conflict'; END IF;
 outcome_id:=gen_random_uuid(); event_id:=gen_random_uuid();
 response:=jsonb_build_object('target',jsonb_build_object('org_id',p_org,'account_id',p_account,'membership_id',p_member::text),
  'disposition','changed','revision',existing.revision::text,'event_id',event_id);
 INSERT INTO identity.operation_outcome(id,scope_kind,scope_id,executor_actor_id,command_type,operation_id,
 command_version,fingerprint_version,fingerprint_algorithm,fingerprint_key_id,fingerprint,result_version,result,initiator_actor_id)
 VALUES(outcome_id,'organization',p_org,executor,'membership.retire',p_operation,1,1,'sha256',NULL,sha256(p_canonical),1,response,NULL) RETURNING * INTO saved;
 INSERT INTO identity.business_event(event_id,event_type,event_version,scope_kind,scope_id,executor_actor_id,
 initiator_actor_id,outcome_id,target_key,target,transition,reason_code,evidence_ref)
 VALUES(event_id,'identity.membership_retired',1,'organization',p_org,executor,NULL,outcome_id,p_member::text,response->'target',
  jsonb_build_object('before',jsonb_build_object('revision',p_revision::text,'retired',false),
   'after',jsonb_build_object('revision',existing.revision::text,'retired',true)),p_reason,p_evidence);
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;

CREATE FUNCTION identity.membership_retirement_outcome(p_operation uuid,p_org uuid,p_account uuid)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; saved identity.operation_outcome; lock_document text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid
 OR p_org IS NULL OR p_org='00000000-0000-0000-0000-000000000000'::uuid OR p_account IS NULL OR p_account='00000000-0000-0000-0000-000000000000'::uuid THEN
  RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
 executor:=identity.membership_retirement_executor(p_org,p_account);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"membership.retire","lock_version":1,"operation_id":'||
 to_json(p_operation::text)::text||',"owner_schema":"identity","scope_id":'||to_json(p_org::text)::text||',"scope_kind":"organization"}';
 BEGIN PERFORM pg_advisory_xact_lock(identity.command_lock(lock_document));
 EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='IC001',MESSAGE='identity_operation_busy'; END;
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM identity.membership_retirement_executor(p_org,p_account) THEN
  RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 SELECT * INTO saved FROM identity.operation_outcome o WHERE o.scope_kind='organization' AND o.scope_id=p_org
 AND o.executor_actor_id=executor AND o.command_type='membership.retire' AND o.operation_id=p_operation
 AND o.result->'target'->>'account_id'=p_account::text;
 IF NOT FOUND THEN RETURN; END IF;
 IF saved.command_version<>1 OR saved.fingerprint_version<>1 OR saved.fingerprint_algorithm<>'sha256'
 OR saved.fingerprint_key_id IS NOT NULL OR saved.result_version<>1 THEN
  RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;

GRANT SELECT ON identity.org_member TO identity_command_owner;
GRANT UPDATE(deleted_at,updated_at,updated_actor_id) ON identity.org_member TO identity_command_owner;
-- Strip inherited EXECUTE on every new routine before exact grants.
DO $acl$
DECLARE r record; a record; grantee text;
BEGIN
 FOR r IN SELECT p.proowner owner,p.proacl acl,p.oid::regprocedure::text object FROM pg_proc p
 JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity' AND p.proname IN
 ('membership_retirement_executor','guard_org_member_retirement_owner','retire_membership','membership_retirement_outcome') LOOP
  EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.object);
  FOR a IN SELECT DISTINCT x.grantee FROM aclexplode(r.acl) x WHERE x.grantee<>r.owner LOOP
   grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
   EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s',r.object,grantee);
  END LOOP;
 END LOOP;
END $acl$;
GRANT EXECUTE ON FUNCTION identity.membership_retirement_executor(uuid,uuid) TO identity_command_owner;
GRANT EXECUTE ON FUNCTION identity.retire_membership(uuid,uuid,uuid,bigint,bigint,text,text,bytea),
 identity.membership_retirement_outcome(uuid,uuid,uuid) TO identity_operator;
GRANT CREATE ON SCHEMA identity TO identity_command_owner;
ALTER FUNCTION identity.membership_retirement_executor(uuid,uuid) OWNER TO identity_command_owner;
ALTER FUNCTION identity.retire_membership(uuid,uuid,uuid,bigint,bigint,text,text,bytea) OWNER TO identity_command_owner;
ALTER FUNCTION identity.membership_retirement_outcome(uuid,uuid,uuid) OWNER TO identity_command_owner;
REVOKE CREATE ON SCHEMA identity FROM identity_command_owner;
"""


def upgrade():
    op.get_bind().exec_driver_sql(MEMBERSHIP_RETIRE_COMMAND_SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
