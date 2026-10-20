"""Fixed protected actor registration and immutable committed recovery."""
from alembic import op
from sqlalchemy import text
from identity_baseline import verify_command_role

revision = 'identity_0006'
down_revision = 'identity_0005'
branch_labels = None
depends_on = None

COMMAND_SCHEMA_SQL = r'''
CREATE TABLE identity.operation_outcome (
 id uuid PRIMARY KEY CHECK(id <> '00000000-0000-0000-0000-000000000000'::uuid),
 scope_kind text NOT NULL CHECK(scope_kind IN ('platform','organization')),
 scope_id uuid CHECK(scope_id <> '00000000-0000-0000-0000-000000000000'::uuid),
 executor_actor_id uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
 command_type text NOT NULL CHECK(command_type='actor.register_system'),
 operation_id uuid NOT NULL CHECK(operation_id <> '00000000-0000-0000-0000-000000000000'::uuid),
 command_version integer NOT NULL CHECK(command_version>0),
 fingerprint_version integer NOT NULL CHECK(fingerprint_version>0),
 fingerprint_algorithm text NOT NULL CHECK(fingerprint_algorithm IN ('sha256','hmac-sha256')),
 fingerprint_key_id text,
 fingerprint bytea NOT NULL CHECK(octet_length(fingerprint)=32),
 result_version integer NOT NULL CHECK(result_version>0),
 result jsonb NOT NULL CHECK(jsonb_typeof(result)='object' AND octet_length(result::text)<=8192),
 committed_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 initiator_actor_id uuid REFERENCES identity.actor(id) ON DELETE RESTRICT,
 CHECK((scope_kind='platform' AND scope_id IS NULL) OR (scope_kind='organization' AND scope_id IS NOT NULL)),
 CHECK(scope_kind='platform' AND initiator_actor_id IS NULL),
 CHECK((fingerprint_algorithm='sha256' AND fingerprint_key_id IS NULL) OR
       (fingerprint_algorithm='hmac-sha256' AND fingerprint_key_id IS NOT NULL AND fingerprint_key_id COLLATE "C" ~ '^[A-Za-z0-9_.:-]{1,128}$')),
 UNIQUE NULLS NOT DISTINCT(scope_kind,scope_id,executor_actor_id,command_type,operation_id)
);
CREATE TABLE identity.business_event (
 event_id uuid PRIMARY KEY CHECK(event_id <> '00000000-0000-0000-0000-000000000000'::uuid),
 event_type text NOT NULL CHECK(event_type='identity.actor_registered'),
 event_version integer NOT NULL CHECK(event_version>0),
 created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 scope_kind text NOT NULL CHECK(scope_kind IN ('platform','organization')),
 scope_id uuid CHECK(scope_id <> '00000000-0000-0000-0000-000000000000'::uuid),
 executor_actor_id uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
 initiator_actor_id uuid REFERENCES identity.actor(id) ON DELETE RESTRICT,
 outcome_id uuid NOT NULL REFERENCES identity.operation_outcome(id) ON DELETE RESTRICT,
 target_key text NOT NULL CHECK(octet_length(target_key)<=512 AND target_key COLLATE "C" ~ '^[ -~]+$'),
 target jsonb NOT NULL CHECK(jsonb_typeof(target)='object'),
 transition jsonb NOT NULL CHECK(jsonb_typeof(transition)='object'),
 reason_code text NOT NULL CHECK(reason_code IN ('initial_setup','synthetic_fixture','identity_adoption','access_change','setup_correction')),
 evidence_ref text CHECK(evidence_ref COLLATE "C" ~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$' AND position('://' in evidence_ref)=0),
 CHECK((scope_kind='platform' AND scope_id IS NULL) OR (scope_kind='organization' AND scope_id IS NOT NULL)),
 CHECK(scope_kind='platform' AND initiator_actor_id IS NULL),
 CHECK(octet_length(target::text)+octet_length(transition::text)<=8192),
 UNIQUE(outcome_id,event_type,target_key)
);

-- The original login, never a caller-provided setting or assumed role, is authority.
CREATE FUNCTION identity.command_executor() RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT executor_actor_id FROM identity.current_operator_authority('actor.register_system','platform',NULL,NULL)
$f$;

CREATE FUNCTION identity.command_lock(value text) RETURNS bigint
LANGUAGE sql IMMUTABLE SET search_path=pg_catalog,pg_temp AS $f$
 SELECT ('x'||encode(substring(sha256(convert_to(value,'UTF8')) FROM 1 FOR 8),'hex'))::bit(64)::bigint
$f$;

CREATE OR REPLACE FUNCTION identity.guard_operator_authority() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF current_user <> 'identity_migrator' THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_operator_owner_required';
 END IF;
 IF TG_OP IN ('DELETE','TRUNCATE') THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_operator_history_retained';
 END IF;
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:operator-authority:v1:'||NEW.database_login::text));
 IF TG_OP='INSERT' THEN
  NEW.revision:=1; NEW.created_at:=statement_timestamp(); NEW.updated_at:=NEW.created_at;
  NEW.updated_by:=NEW.created_by; RETURN NEW;
 END IF;
 IF NEW.database_login IS DISTINCT FROM OLD.database_login
 OR NEW.created_by IS DISTINCT FROM OLD.created_by OR NEW.created_at IS DISTINCT FROM OLD.created_at
 OR (TG_TABLE_NAME='operator_principals' AND to_jsonb(NEW)->'executor_actor_id' IS DISTINCT FROM to_jsonb(OLD)->'executor_actor_id')
 OR (TG_TABLE_NAME='operator_authorities' AND
 (to_jsonb(NEW)-ARRAY['enabled','revision','updated_by','updated_at']) IS DISTINCT FROM
 (to_jsonb(OLD)-ARRAY['enabled','revision','updated_by','updated_at'])) THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_operator_identity_immutable';
 END IF;
 IF NEW.enabled IS DISTINCT FROM OLD.enabled THEN
  IF OLD.revision=9223372036854775807 THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_operator_revision_exhausted';
  END IF;
  NEW.revision:=OLD.revision+1; NEW.updated_at:=statement_timestamp();
 ELSE
  NEW.revision:=OLD.revision; NEW.updated_at:=OLD.updated_at; NEW.updated_by:=OLD.updated_by;
 END IF;
 RETURN NEW;
END $f$;

CREATE OR REPLACE FUNCTION identity.guard_actor() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid;
BEGIN
 IF current_user='identity_command_owner' THEN
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

CREATE FUNCTION identity.guard_command_evidence() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
DECLARE o identity.operation_outcome; actor_id uuid;
BEGIN
 IF TG_OP<>'INSERT' THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_command_evidence_immutable';
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
CREATE TRIGGER operation_outcome_guard BEFORE INSERT OR UPDATE OR DELETE ON identity.operation_outcome
 FOR EACH ROW EXECUTE FUNCTION identity.guard_command_evidence();
CREATE TRIGGER operation_outcome_retention BEFORE TRUNCATE ON identity.operation_outcome
 FOR EACH STATEMENT EXECUTE FUNCTION identity.guard_command_evidence();
CREATE TRIGGER business_event_guard BEFORE INSERT OR UPDATE OR DELETE ON identity.business_event
 FOR EACH ROW EXECUTE FUNCTION identity.guard_command_evidence();
CREATE TRIGGER business_event_retention BEFORE TRUNCATE ON identity.business_event
 FOR EACH STATEMENT EXECUTE FUNCTION identity.guard_command_evidence();
CREATE FUNCTION identity.require_command_event() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF NEW.result_version=1 AND NEW.result->>'disposition'='created' AND NOT EXISTS
 (SELECT 1 FROM identity.business_event e WHERE e.outcome_id=NEW.id AND e.event_id=(NEW.result->>'event_id')::uuid) THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_command_event_missing';
 END IF; RETURN NULL;
END $f$;
CREATE CONSTRAINT TRIGGER operation_outcome_event AFTER INSERT ON identity.operation_outcome
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION identity.require_command_event();

CREATE FUNCTION identity.register_system(p_operation uuid,p_actor uuid,p_kind text,p_key text,
 p_display text,p_reason text,p_evidence text,p_canonical bytea)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; canonical text; lock_document text; saved identity.operation_outcome;
 existing identity.actor; outcome_id uuid; event_id uuid; response jsonb; disposition text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' THEN
  RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
 IF p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid
 OR p_actor IS NULL OR p_actor='00000000-0000-0000-0000-000000000000'::uuid
 OR p_kind IS NULL OR p_kind NOT IN ('system','service') OR p_key IS NULL
 OR p_key COLLATE "C" !~ '^[a-z][a-z0-9_.:-]{0,127}$'
 OR p_display IS NULL OR char_length(p_display) NOT BETWEEN 1 AND 200
 OR length(btrim(p_display,U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000'))=0
 OR p_reason IS NULL OR p_reason NOT IN ('initial_setup','synthetic_fixture','identity_adoption','access_change','setup_correction')
 OR (p_evidence IS NOT NULL AND (p_evidence COLLATE "C" !~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$' OR position('://' in p_evidence)>0)) THEN
  RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
 canonical:='{"command":"actor.register_system","evidence_ref":'||coalesce(to_json(p_evidence)::text,'null')||
 ',"operation_id":'||to_json(p_operation::text)::text||',"payload":{"actor_id":'||to_json(p_actor::text)::text||
 ',"actor_key":'||to_json(p_key)::text||',"display_name":'||to_json(p_display)::text||
 ',"expected_absent":true,"kind":'||to_json(p_kind)::text||'},"reason_code":'||to_json(p_reason)::text||
 ',"schema_version":1,"scope":{"kind":"platform"}}';
 IF p_canonical IS DISTINCT FROM convert_to(canonical,'UTF8') THEN
  RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
 executor:=identity.command_executor();
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"actor.register_system","lock_version":1,"operation_id":'||
 to_json(p_operation::text)::text||',"owner_schema":"identity","scope_id":null,"scope_kind":"platform"}';
 BEGIN
  PERFORM pg_advisory_xact_lock(identity.command_lock(lock_document));
 EXCEPTION WHEN lock_not_available THEN
  RAISE EXCEPTION USING ERRCODE='IC001',MESSAGE='identity_operation_busy';
 END;
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM identity.command_executor() THEN
  RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 SELECT * INTO saved FROM identity.operation_outcome o WHERE o.scope_kind='platform' AND o.scope_id IS NULL
 AND o.executor_actor_id=executor AND o.command_type='actor.register_system' AND o.operation_id=p_operation;
 IF FOUND THEN
  IF saved.command_version<>1 OR saved.fingerprint_version<>1 OR saved.fingerprint_algorithm<>'sha256'
   OR saved.fingerprint_key_id IS NOT NULL OR saved.result_version<>1 THEN
   RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
  IF saved.fingerprint<>sha256(p_canonical) THEN
   RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_operation_conflict'; END IF;
  RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at; RETURN;
 END IF;
 -- Fixed order across every registration, including distinct operation IDs.
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:actor-id:v1:'||p_actor::text));
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:actor-key:v1:'||p_key));
 SELECT a.id,a.kind,a.actor_key,a.display_name INTO existing.id,existing.kind,existing.actor_key,existing.display_name FROM identity.actor a WHERE a.id=p_actor;
 IF FOUND THEN
  IF existing.kind<>p_kind OR existing.actor_key IS DISTINCT FROM p_key OR existing.display_name<>p_display THEN
   RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_registration_conflict'; END IF;
  disposition:='unchanged'; event_id:=NULL;
 ELSE
  IF EXISTS(SELECT 1 FROM identity.actor a WHERE a.actor_key=p_key) THEN
   RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_registration_conflict'; END IF;
  INSERT INTO identity.actor(id,kind,actor_key,display_name,created_by,updated_by)
   VALUES(p_actor,p_kind,p_key,p_display,executor,executor);
  disposition:='created'; event_id:=gen_random_uuid();
 END IF;
 outcome_id:=gen_random_uuid();
 response:=jsonb_build_object('target',jsonb_build_object('actor_id',p_actor),'disposition',disposition,'revision',NULL,'event_id',event_id);
 INSERT INTO identity.operation_outcome(id,scope_kind,scope_id,executor_actor_id,command_type,operation_id,
 command_version,fingerprint_version,fingerprint_algorithm,fingerprint_key_id,fingerprint,result_version,result,initiator_actor_id)
 VALUES(outcome_id,'platform',NULL,executor,'actor.register_system',p_operation,1,1,'sha256',NULL,sha256(p_canonical),1,response,NULL)
 RETURNING * INTO saved;
 IF event_id IS NOT NULL THEN
  INSERT INTO identity.business_event(event_id,event_type,event_version,scope_kind,scope_id,executor_actor_id,
   initiator_actor_id,outcome_id,target_key,target,transition,reason_code,evidence_ref)
  VALUES(event_id,'identity.actor_registered',1,'platform',NULL,executor,NULL,outcome_id,p_actor::text,
   jsonb_build_object('actor_id',p_actor),jsonb_build_object('kind',p_kind,'actor_key',p_key),p_reason,p_evidence);
 END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;

CREATE FUNCTION identity.system_actor_outcome(p_operation uuid)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; saved identity.operation_outcome; lock_document text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL
 OR p_operation='00000000-0000-0000-0000-000000000000'::uuid THEN
  RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
 executor:=identity.command_executor();
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"actor.register_system","lock_version":1,"operation_id":'||
 to_json(p_operation::text)::text||',"owner_schema":"identity","scope_id":null,"scope_kind":"platform"}';
 BEGIN PERFORM pg_advisory_xact_lock(identity.command_lock(lock_document));
 EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='IC001',MESSAGE='identity_operation_busy'; END;
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM identity.command_executor() THEN
  RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
 SELECT * INTO saved FROM identity.operation_outcome o WHERE o.scope_kind='platform' AND o.scope_id IS NULL
 AND o.executor_actor_id=executor AND o.command_type='actor.register_system' AND o.operation_id=p_operation;
 IF NOT FOUND THEN RETURN; END IF;
 IF saved.command_version<>1 OR saved.fingerprint_version<>1 OR saved.fingerprint_algorithm<>'sha256'
 OR saved.fingerprint_key_id IS NOT NULL OR saved.result_version<>1 THEN
  RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;

ALTER TABLE identity.operation_outcome ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.operation_outcome FORCE ROW LEVEL SECURITY;
ALTER TABLE identity.business_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.business_event FORCE ROW LEVEL SECURITY;
CREATE POLICY operation_outcome_command ON identity.operation_outcome TO identity_command_owner
 USING(scope_kind='platform' AND scope_id IS NULL AND executor_actor_id=identity.command_executor())
 WITH CHECK(scope_kind='platform' AND scope_id IS NULL AND executor_actor_id=identity.command_executor());
CREATE POLICY business_event_command ON identity.business_event TO identity_command_owner
 USING(scope_kind='platform' AND scope_id IS NULL AND executor_actor_id=identity.command_executor())
 WITH CHECK(scope_kind='platform' AND scope_id IS NULL AND executor_actor_id=identity.command_executor());
CREATE POLICY operation_outcome_inspection ON identity.operation_outcome FOR SELECT TO identity_migrator USING(true);
CREATE POLICY business_event_inspection ON identity.business_event FOR SELECT TO identity_migrator USING(true);

-- Remove unexpected inherited defaults for every new table and function.
DO $acl$
DECLARE r record; a record; grantee text;
BEGIN
 FOR r IN SELECT c.relowner owner,c.relacl acl,c.oid::regclass::text object FROM pg_class c
 JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='identity'
 AND c.relname IN ('operation_outcome','business_event') LOOP
  EXECUTE format('REVOKE ALL ON TABLE %s FROM PUBLIC',r.object);
  FOR a IN SELECT DISTINCT x.grantee FROM aclexplode(r.acl) x WHERE x.grantee<>r.owner LOOP
   grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
   EXECUTE format('REVOKE ALL ON TABLE %s FROM %s',r.object,grantee);
  END LOOP;
 END LOOP;
 FOR r IN SELECT p.proowner owner,p.proacl acl,p.oid::regprocedure::text object FROM pg_proc p
 JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity'
 AND p.proname IN ('command_executor','command_lock','guard_command_evidence','require_command_event','register_system','system_actor_outcome') LOOP
  EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.object);
  FOR a IN SELECT DISTINCT x.grantee FROM aclexplode(r.acl) x WHERE x.grantee<>r.owner LOOP
   grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
   EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s',r.object,grantee);
  END LOOP;
 END LOOP;
END $acl$;
GRANT USAGE ON SCHEMA identity TO identity_command_owner;
GRANT SELECT(id,kind,actor_key,display_name) ON identity.actor TO identity_command_owner;
GRANT INSERT(id,kind,actor_key,display_name,created_by,updated_by) ON identity.actor TO identity_command_owner;
GRANT SELECT,INSERT ON identity.operation_outcome,identity.business_event TO identity_command_owner;
SET LOCAL ROLE identity_operator_authority_owner;
GRANT EXECUTE ON FUNCTION identity.current_operator_authority(text,text,uuid,uuid) TO identity_command_owner;
RESET ROLE;
GRANT EXECUTE ON FUNCTION identity.command_lock(text),identity.command_executor() TO identity_command_owner;
GRANT EXECUTE ON FUNCTION identity.register_system(uuid,uuid,text,text,text,text,text,bytea),identity.system_actor_outcome(uuid) TO identity_operator;
GRANT CREATE ON SCHEMA identity TO identity_command_owner;
ALTER FUNCTION identity.command_executor() OWNER TO identity_command_owner;
ALTER FUNCTION identity.register_system(uuid,uuid,text,text,text,text,text,bytea) OWNER TO identity_command_owner;
ALTER FUNCTION identity.system_actor_outcome(uuid) OWNER TO identity_command_owner;
REVOKE CREATE ON SCHEMA identity FROM identity_command_owner;
'''


def upgrade():
    connection = op.get_bind()
    verify_command_role(connection, staged=True)
    connection.exec_driver_sql(COMMAND_SCHEMA_SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
