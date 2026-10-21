"""Protected live-account verification and permanent attribution mapping."""
from alembic import op
from identity_baseline import verify_account_verification_role

revision = 'identity_0018'
down_revision = 'identity_0017'
branch_labels = None
depends_on = None

ACCOUNT_ACTOR_ENSURE_SQL = r"""
CREATE FUNCTION identity.account_actor_executor(p_account uuid) RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT executor_actor_id FROM identity.current_operator_authority('account_actor.ensure','platform',NULL,p_account)
$f$;
CREATE FUNCTION identity.account_actor_creation_executor() RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT p.executor_actor_id FROM identity.operator_principals p JOIN identity.operator_authorities a USING(database_login)
 WHERE p.database_login=session_user AND p.enabled AND a.enabled AND a.command='account_actor.ensure'
 AND a.scope_kind='platform' AND a.application_id IS NULL ORDER BY a.id LIMIT 1
$f$;
CREATE FUNCTION identity.account_actor_uuid_available(p_account uuid,p_actor uuid) RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF identity.account_actor_executor(p_account) IS NULL THEN
  RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 IF (SELECT count(*) FROM pg_auth_members WHERE roleid=(SELECT oid FROM pg_roles WHERE rolname=current_user)
  OR member=(SELECT oid FROM pg_roles WHERE rolname=current_user))<>1
 OR NOT EXISTS(SELECT 1 FROM pg_auth_members m WHERE m.roleid=(SELECT oid FROM pg_roles WHERE rolname=current_user)
  AND m.member=(SELECT oid FROM pg_roles WHERE rolname='identity_migrator') AND NOT m.admin_option
  AND coalesce(to_jsonb(m)->>'inherit_option','false')='false'
  AND coalesce(to_jsonb(m)->>'set_option','true')='true') THEN
  RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
 -- Every retained profile references Auth; include deleted Auth IDs in collision checks.
 RETURN p_actor=p_account OR NOT EXISTS(SELECT 1 FROM auth.users a WHERE a.id=p_actor);
END $f$;
CREATE FUNCTION identity.account_actor_profile(p_account uuid) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT EXISTS(SELECT 1 FROM identity.users u WHERE u.id=p_account AND u.deleted_at IS NULL
 AND u.is_system IS NOT TRUE AND u.actor_key IS NULL AND identity.account_actor_executor(p_account) IS NOT NULL)
$f$;
CREATE FUNCTION identity.verify_account_actor_account(p_account uuid) RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF identity.account_actor_executor(p_account) IS NULL THEN
  RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 IF (SELECT count(*) FROM pg_auth_members WHERE roleid=(SELECT oid FROM pg_roles WHERE rolname=current_user)
  OR member=(SELECT oid FROM pg_roles WHERE rolname=current_user))<>1
 OR NOT EXISTS(SELECT 1 FROM pg_auth_members m WHERE m.roleid=(SELECT oid FROM pg_roles WHERE rolname=current_user)
  AND m.member=(SELECT oid FROM pg_roles WHERE rolname='identity_migrator') AND NOT m.admin_option
  AND coalesce(to_jsonb(m)->>'inherit_option','false')='false'
  AND coalesce(to_jsonb(m)->>'set_option','true')='true') THEN
  RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
 IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=current_user AND NOT rolsuper AND NOT rolinherit
  AND NOT rolcreaterole AND NOT rolcreatedb AND NOT rolcanlogin AND NOT rolreplication AND NOT rolbypassrls)
 OR has_table_privilege(current_user,'auth.users','SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
 OR EXISTS(SELECT 1 FROM pg_attribute WHERE attrelid='auth.users'::regclass AND attnum>0 AND NOT attisdropped
  AND ((attname IN ('id','deleted_at') AND NOT has_column_privilege(current_user,attrelid,attnum,'SELECT'))
   OR (attname NOT IN ('id','deleted_at') AND has_column_privilege(current_user,attrelid,attnum,'SELECT'))
   OR has_column_privilege(current_user,attrelid,attnum,'INSERT,UPDATE,REFERENCES')))
 OR (SELECT count(*) FROM pg_policies WHERE schemaname='auth' AND tablename='users'
  AND roles::text[] && ARRAY['public','identity_account_verification_owner'])<>1
 OR NOT EXISTS(SELECT 1 FROM pg_class WHERE oid='auth.users'::regclass AND relrowsecurity)
 OR NOT EXISTS(SELECT 1 FROM pg_policies WHERE schemaname='auth' AND tablename='users'
  AND policyname='identity_account_actor_verification' AND roles::text='{identity_account_verification_owner}'
  AND cmd='SELECT' AND permissive='PERMISSIVE' AND qual='true' AND with_check IS NULL) THEN
  RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
 RETURN EXISTS(SELECT 1 FROM auth.users a WHERE a.id=p_account AND a.deleted_at IS NULL)
 AND identity.account_actor_profile(p_account);
END $f$;
GRANT USAGE ON SCHEMA identity TO identity_account_verification_owner;
GRANT SELECT(id,deleted_at,is_system,actor_key) ON identity.users TO identity_account_verification_owner;
CREATE POLICY account_actor_verification_profile ON identity.users FOR SELECT TO identity_account_verification_owner
 USING(identity.account_actor_executor(id) IS NOT NULL);
SET LOCAL ROLE identity_operator_authority_owner;
GRANT EXECUTE ON FUNCTION identity.current_operator_authority(text,text,uuid,uuid) TO identity_account_verification_owner;
RESET ROLE;
GRANT EXECUTE ON FUNCTION identity.account_actor_executor(uuid) TO identity_account_verification_owner,identity_command_owner;
GRANT EXECUTE ON FUNCTION identity.account_actor_creation_executor(),identity.account_actor_uuid_available(uuid,uuid),identity.account_actor_profile(uuid),identity.verify_account_actor_account(uuid) TO identity_command_owner;


ALTER TABLE identity.operation_outcome DROP CONSTRAINT operation_outcome_command_type_check;
ALTER TABLE identity.operation_outcome ADD CONSTRAINT operation_outcome_command_type_check CHECK(command_type IN ('actor.register_system','account_actor.ensure','membership.retire','membership.join'));
ALTER TABLE identity.operation_outcome DROP CONSTRAINT operation_outcome_check1;
ALTER TABLE identity.operation_outcome ADD CONSTRAINT operation_outcome_check1 CHECK(initiator_actor_id IS NULL AND ((command_type IN ('actor.register_system','account_actor.ensure') AND scope_kind='platform') OR (command_type IN ('membership.retire','membership.join') AND scope_kind='organization')));
ALTER TABLE identity.business_event DROP CONSTRAINT business_event_event_type_check;
ALTER TABLE identity.business_event ADD CONSTRAINT business_event_event_type_check CHECK(event_type IN ('identity.actor_registered','identity.account_actor_ensured','identity.membership_retired','identity.membership_joined'));
ALTER TABLE identity.business_event DROP CONSTRAINT business_event_check1;
ALTER TABLE identity.business_event ADD CONSTRAINT business_event_check1 CHECK(initiator_actor_id IS NULL AND ((event_type IN ('identity.actor_registered','identity.account_actor_ensured') AND scope_kind='platform') OR (event_type IN ('identity.membership_retired','identity.membership_joined') AND scope_kind='organization')));
CREATE POLICY account_actor_ensure_outcome ON identity.operation_outcome TO identity_command_owner
 USING(command_type='account_actor.ensure' AND scope_kind='platform' AND executor_actor_id=identity.account_actor_executor((result->'target'->>'account_id')::uuid))
 WITH CHECK(command_type='account_actor.ensure' AND scope_kind='platform' AND executor_actor_id=identity.account_actor_executor((result->'target'->>'account_id')::uuid));
CREATE POLICY account_actor_ensure_event ON identity.business_event TO identity_command_owner
 USING(event_type='identity.account_actor_ensured' AND scope_kind='platform' AND executor_actor_id=identity.account_actor_executor((target->>'account_id')::uuid))
 WITH CHECK(event_type='identity.account_actor_ensured' AND scope_kind='platform' AND executor_actor_id=identity.account_actor_executor((target->>'account_id')::uuid));
GRANT SELECT(account_id,actor_id,actor_kind,created_by,created_at) ON identity.account_actor TO identity_command_owner;
GRANT INSERT ON identity.account_actor TO identity_command_owner;
CREATE OR REPLACE FUNCTION identity.guard_account_actor() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF TG_OP<>'INSERT' THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_account_actor_immutable'; END IF;
 IF current_user='identity_command_owner' THEN
  IF identity.account_actor_executor(NEW.account_id) IS NULL OR NOT identity.account_actor_profile(NEW.account_id) THEN
   RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_actor_owner_required'; END IF;
  NEW.created_by:=identity.account_actor_executor(NEW.account_id);
 ELSIF current_user<>'identity_migrator' THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_actor_owner_required'; END IF;
 NEW.created_at:=statement_timestamp(); RETURN NEW;
END $f$;
CREATE OR REPLACE FUNCTION identity.guard_actor() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid;
BEGIN
 IF current_user='identity_command_owner' THEN
  IF NEW.kind='account' THEN
   executor:=identity.account_actor_creation_executor();
   IF TG_OP<>'INSERT' OR executor IS NULL OR NEW.actor_key IS NOT NULL THEN
    RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_actor_owner_required'; END IF;
   NEW.created_by:=executor; NEW.updated_by:=executor;
   NEW.created_at:=statement_timestamp(); NEW.updated_at:=NEW.created_at; RETURN NEW;
  END IF;
  executor:=identity.command_executor();
  IF TG_OP<>'INSERT' OR executor IS NULL OR NEW.kind NOT IN ('system','service') OR NEW.actor_key IS NULL THEN
   RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_actor_owner_required';
  END IF;
  NEW.created_by:=executor; NEW.updated_by:=executor;
  NEW.created_at:=statement_timestamp(); NEW.updated_at:=NEW.created_at; RETURN NEW;
 END IF;
 IF current_user<>'identity_migrator' THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_actor_owner_required';
 END IF;
 IF TG_OP IN ('DELETE','TRUNCATE') THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_actor_history_retained';
 END IF;
 IF TG_OP='INSERT' THEN
  NEW.created_at:=statement_timestamp(); NEW.updated_at:=NEW.created_at; NEW.updated_by:=NEW.created_by; RETURN NEW;
 END IF;
 IF NEW.id IS DISTINCT FROM OLD.id OR NEW.kind IS DISTINCT FROM OLD.kind
 OR NEW.created_by IS DISTINCT FROM OLD.created_by OR NEW.created_at IS DISTINCT FROM OLD.created_at
 OR (OLD.actor_key IS NOT NULL AND NEW.actor_key IS DISTINCT FROM OLD.actor_key) THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_actor_identity_immutable';
 END IF;
 IF NEW.display_name IS DISTINCT FROM OLD.display_name OR NEW.actor_key IS DISTINCT FROM OLD.actor_key THEN
  NEW.updated_at:=statement_timestamp();
 ELSE NEW.updated_by:=OLD.updated_by; NEW.updated_at:=OLD.updated_at;
 END IF; RETURN NEW;
END $f$;

CREATE OR REPLACE FUNCTION identity.guard_command_evidence() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
DECLARE o identity.operation_outcome; actor_id uuid;
BEGIN
 IF TG_OP<>'INSERT' THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_command_evidence_immutable';
 END IF;

 IF coalesce(to_jsonb(NEW)->>'command_type','')='account_actor.ensure' OR coalesce(to_jsonb(NEW)->>'event_type','')='identity.account_actor_ensured' THEN
  IF TG_TABLE_NAME='operation_outcome' THEN
   IF current_user<>'identity_command_owner' OR NEW.executor_actor_id IS DISTINCT FROM identity.account_actor_executor((NEW.result->'target'->>'account_id')::uuid) THEN
    RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_command_owner_required'; END IF;
   IF NEW.command_version<>1 OR NEW.result_version<>1 OR NEW.scope_kind<>'platform' OR NEW.scope_id IS NOT NULL
    OR NEW.result->>'disposition' IS NULL OR NEW.result->>'disposition' NOT IN ('created','unchanged')
    OR (NEW.result->>'disposition'='created') IS DISTINCT FROM (NEW.result->>'event_id' IS NOT NULL)
    OR (NEW.result->>'event_id')::uuid='00000000-0000-0000-0000-000000000000'::uuid
    OR NOT EXISTS(SELECT 1 FROM identity.account_actor m JOIN identity.actor a ON a.id=m.actor_id
      WHERE m.account_id=(NEW.result->'target'->>'account_id')::uuid AND m.actor_id=(NEW.result->'target'->>'actor_id')::uuid
      AND a.kind='account' AND a.actor_key IS NULL
      AND NEW.result=jsonb_build_object('target',jsonb_build_object('account_id',m.account_id,'actor_id',m.actor_id),
       'disposition',NEW.result->>'disposition','revision',NULL,'event_id',(NEW.result->>'event_id')::uuid)) THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_command_result_invalid'; END IF;
   NEW.committed_at:=statement_timestamp();
  ELSE
   SELECT * INTO o FROM identity.operation_outcome WHERE id=NEW.outcome_id;
   IF current_user<>'identity_command_owner' OR NEW.executor_actor_id IS DISTINCT FROM identity.account_actor_executor((NEW.target->>'account_id')::uuid) THEN
    RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_command_owner_required'; END IF;
   IF o.id IS NULL OR o.command_type<>'account_actor.ensure' OR NEW.event_version<>1 OR o.result->>'disposition'<>'created'
    OR NEW.scope_kind IS DISTINCT FROM o.scope_kind OR NEW.scope_id IS DISTINCT FROM o.scope_id
    OR NEW.executor_actor_id IS DISTINCT FROM o.executor_actor_id OR NEW.initiator_actor_id IS DISTINCT FROM o.initiator_actor_id
    OR NEW.event_id IS DISTINCT FROM (o.result->>'event_id')::uuid OR NEW.target IS DISTINCT FROM o.result->'target'
    OR NEW.target_key IS DISTINCT FROM NEW.target->>'account_id'
    OR NEW.evidence_ref IS NULL OR NEW.transition IS DISTINCT FROM jsonb_build_object('kind','account') THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_command_event_invalid'; END IF;
   NEW.created_at:=o.committed_at;
  END IF;
  RETURN NEW;
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

CREATE FUNCTION identity.ensure_account_actor(p_operation uuid,p_account uuid,p_actor uuid,p_display text,
 p_reason text,p_evidence text,p_canonical bytea)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; canonical text; lock_document text; saved identity.operation_outcome;
 existing identity.actor; mapping identity.account_actor; outcome_id uuid; event_id uuid; response jsonb; disposition text;
 verified_at timestamptz; uuid_available boolean;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR
 p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid OR
 p_account IS NULL OR p_account='00000000-0000-0000-0000-000000000000'::uuid OR
 p_actor IS NULL OR p_actor='00000000-0000-0000-0000-000000000000'::uuid OR
 p_display IS NULL OR char_length(p_display) NOT BETWEEN 1 AND 200 OR
 length(btrim(p_display,U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000'))=0 OR
 p_reason IS NULL OR p_reason NOT IN ('initial_setup','synthetic_fixture','identity_adoption','access_change','setup_correction') OR
 p_evidence IS NULL OR p_evidence COLLATE "C" !~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$' OR position('://' in p_evidence)>0 THEN
  RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
 canonical:='{"command":"account_actor.ensure","evidence_ref":'||to_json(p_evidence)::text||
 ',"operation_id":'||to_json(p_operation::text)::text||',"payload":{"account_id":'||to_json(p_account::text)::text||
 ',"actor_id":'||to_json(p_actor::text)::text||',"display_name":'||to_json(p_display)::text||
 ',"expected_absent":true},"reason_code":'||to_json(p_reason)::text||',"schema_version":1,"scope":{"kind":"platform"}}';
 IF p_canonical IS DISTINCT FROM convert_to(canonical,'UTF8') THEN
  RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
 executor:=identity.account_actor_executor(p_account);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 -- The bounded observation includes both reads and occurs before coordination locks.
 verified_at:=clock_timestamp();
 IF NOT identity.verify_account_actor_account(p_account) THEN
  RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_account_ineligible'; END IF;
 uuid_available:=identity.account_actor_uuid_available(p_account,p_actor);
 IF clock_timestamp()-verified_at>interval '5 seconds' THEN
  RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"account_actor.ensure","lock_version":1,"operation_id":'||
 to_json(p_operation::text)::text||',"owner_schema":"identity","scope_id":null,"scope_kind":"platform"}';
 BEGIN PERFORM pg_advisory_xact_lock(identity.command_lock(lock_document));
 EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='IC001',MESSAGE='identity_operation_busy'; END;
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM identity.account_actor_executor(p_account) THEN
  RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 SELECT * INTO saved FROM identity.operation_outcome o WHERE o.scope_kind='platform' AND o.scope_id IS NULL
 AND o.executor_actor_id=executor AND o.command_type='account_actor.ensure' AND o.operation_id=p_operation;
 IF FOUND THEN
  IF saved.command_version<>1 OR saved.fingerprint_version<>1 OR saved.fingerprint_algorithm<>'sha256'
   OR saved.fingerprint_key_id IS NOT NULL OR saved.result_version<>1 THEN
   RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
  IF saved.fingerprint<>sha256(p_canonical) THEN RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_operation_conflict'; END IF;
  IF clock_timestamp()-verified_at>interval '5 seconds' THEN
   RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
  IF NOT identity.account_actor_profile(p_account) THEN
   RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_account_ineligible'; END IF;
  RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at; RETURN;
 END IF;
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:account-actor:v1:'||p_account::text));
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:actor-id:v1:'||p_actor::text));
 IF clock_timestamp()-verified_at>interval '5 seconds' THEN
  RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
 IF NOT identity.account_actor_profile(p_account) THEN RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_account_ineligible'; END IF;
 SELECT * INTO mapping FROM identity.account_actor m WHERE m.account_id=p_account;
 SELECT a.id,a.kind,a.actor_key,a.display_name INTO existing.id,existing.kind,existing.actor_key,existing.display_name FROM identity.actor a WHERE a.id=p_actor;
 IF mapping.account_id IS NOT NULL THEN
  IF mapping.actor_id<>p_actor OR existing.kind IS DISTINCT FROM 'account' OR existing.actor_key IS NOT NULL OR existing.display_name IS DISTINCT FROM p_display THEN
   RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_mapping_conflict'; END IF;
  disposition:='unchanged';
 ELSE
  IF EXISTS(SELECT 1 FROM identity.account_actor m WHERE m.actor_id=p_actor)
   OR (p_actor<>p_account AND (existing.id IS NOT NULL OR EXISTS(SELECT 1 FROM identity.actor a WHERE a.id=p_account)
    OR NOT uuid_available))
   OR (existing.id IS NOT NULL AND (existing.kind<>'account' OR existing.actor_key IS NOT NULL OR existing.display_name<>p_display)) THEN
   RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_mapping_conflict'; END IF;
  IF existing.id IS NULL THEN
   INSERT INTO identity.actor(id,kind,display_name,created_by,updated_by) VALUES(p_actor,'account',p_display,executor,executor);
  END IF;
  INSERT INTO identity.account_actor(account_id,actor_id,actor_kind,created_by) VALUES(p_account,p_actor,'account',executor);
  disposition:='created'; event_id:=gen_random_uuid();
 END IF;
 outcome_id:=gen_random_uuid();
 response:=jsonb_build_object('target',jsonb_build_object('account_id',p_account,'actor_id',p_actor),'disposition',disposition,'revision',NULL,'event_id',event_id);
 INSERT INTO identity.operation_outcome(id,scope_kind,scope_id,executor_actor_id,command_type,operation_id,command_version,
 fingerprint_version,fingerprint_algorithm,fingerprint_key_id,fingerprint,result_version,result,initiator_actor_id)
 VALUES(outcome_id,'platform',NULL,executor,'account_actor.ensure',p_operation,1,1,'sha256',NULL,sha256(p_canonical),1,response,NULL) RETURNING * INTO saved;
 IF event_id IS NOT NULL THEN
  INSERT INTO identity.business_event(event_id,event_type,event_version,scope_kind,scope_id,executor_actor_id,initiator_actor_id,
  outcome_id,target_key,target,transition,reason_code,evidence_ref)
  VALUES(event_id,'identity.account_actor_ensured',1,'platform',NULL,executor,NULL,outcome_id,p_account::text,
   jsonb_build_object('account_id',p_account,'actor_id',p_actor),jsonb_build_object('kind','account'),p_reason,p_evidence);
 END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
CREATE FUNCTION identity.account_actor_outcome(p_operation uuid,p_account uuid)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; saved identity.operation_outcome; lock_document text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_account IS NULL
 OR p_operation='00000000-0000-0000-0000-000000000000'::uuid OR p_account='00000000-0000-0000-0000-000000000000'::uuid THEN
  RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
 executor:=identity.account_actor_executor(p_account);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"account_actor.ensure","lock_version":1,"operation_id":'||
 to_json(p_operation::text)::text||',"owner_schema":"identity","scope_id":null,"scope_kind":"platform"}';
 BEGIN PERFORM pg_advisory_xact_lock(identity.command_lock(lock_document));
 EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='IC001',MESSAGE='identity_operation_busy'; END;
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM identity.account_actor_executor(p_account) THEN
  RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 SELECT * INTO saved FROM identity.operation_outcome o WHERE o.scope_kind='platform' AND o.scope_id IS NULL
 AND o.executor_actor_id=executor AND o.command_type='account_actor.ensure' AND o.operation_id=p_operation
 AND o.result->'target'->>'account_id'=p_account::text;
 IF NOT FOUND THEN RETURN; END IF;
 IF saved.command_version<>1 OR saved.fingerprint_version<>1 OR saved.fingerprint_algorithm<>'sha256'
 OR saved.fingerprint_key_id IS NOT NULL OR saved.result_version<>1 THEN
  RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
DO $acl$
DECLARE r record; a record; grantee text;
BEGIN
 FOR r IN SELECT p.proowner owner,p.proacl acl,p.oid::regprocedure::text object FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
 WHERE n.nspname='identity' AND p.proname IN ('account_actor_creation_executor','account_actor_uuid_available','account_actor_executor','account_actor_profile','verify_account_actor_account','ensure_account_actor','account_actor_outcome') LOOP
  EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.object);
  FOR a IN SELECT DISTINCT x.grantee FROM aclexplode(r.acl) x WHERE x.grantee<>r.owner LOOP
   grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
   EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s',r.object,grantee);
  END LOOP;
 END LOOP;
END $acl$;
GRANT EXECUTE ON FUNCTION identity.account_actor_executor(uuid) TO identity_account_verification_owner,identity_command_owner;
GRANT EXECUTE ON FUNCTION identity.account_actor_creation_executor(),identity.account_actor_uuid_available(uuid,uuid),identity.account_actor_profile(uuid),identity.verify_account_actor_account(uuid) TO identity_command_owner;
GRANT EXECUTE ON FUNCTION identity.ensure_account_actor(uuid,uuid,uuid,text,text,text,bytea),identity.account_actor_outcome(uuid,uuid) TO identity_operator;
GRANT CREATE ON SCHEMA identity TO identity_operator_authority_owner;
ALTER FUNCTION identity.account_actor_creation_executor() OWNER TO identity_operator_authority_owner;
REVOKE CREATE ON SCHEMA identity FROM identity_operator_authority_owner;
GRANT CREATE ON SCHEMA identity TO identity_account_verification_owner,identity_command_owner;
ALTER FUNCTION identity.account_actor_executor(uuid) OWNER TO identity_command_owner;
ALTER FUNCTION identity.account_actor_uuid_available(uuid,uuid) OWNER TO identity_account_verification_owner;
ALTER FUNCTION identity.account_actor_profile(uuid) OWNER TO identity_account_verification_owner;
ALTER FUNCTION identity.verify_account_actor_account(uuid) OWNER TO identity_account_verification_owner;
REVOKE CREATE ON SCHEMA identity FROM identity_account_verification_owner,identity_command_owner;
GRANT CREATE ON SCHEMA identity TO identity_command_owner;
ALTER FUNCTION identity.ensure_account_actor(uuid,uuid,uuid,text,text,text,bytea) OWNER TO identity_command_owner;
ALTER FUNCTION identity.account_actor_outcome(uuid,uuid) OWNER TO identity_command_owner;
REVOKE CREATE ON SCHEMA identity FROM identity_command_owner;
"""


def upgrade():
    connection = op.get_bind()
    verify_account_verification_role(connection, staged=True)
    connection.exec_driver_sql(ACCOUNT_ACTOR_ENSURE_SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
