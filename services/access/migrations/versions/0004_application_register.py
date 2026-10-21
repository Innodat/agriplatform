"""Protected disabled application registration and immutable compact recovery."""
from alembic import op
revision = 'access_0004'
down_revision = 'access_0003'
branch_labels = None
depends_on = None

SQL = r'''
CREATE TABLE access.operator_principals (
 database_login name PRIMARY KEY CHECK(database_login::text<>''),
 executor_actor_id uuid NOT NULL CHECK(executor_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid),
 enabled boolean NOT NULL DEFAULT false,
 revision bigint NOT NULL DEFAULT 1 CHECK(revision>0),
 created_by uuid NOT NULL CHECK(created_by<>'00000000-0000-0000-0000-000000000000'::uuid),
 updated_by uuid NOT NULL CHECK(updated_by<>'00000000-0000-0000-0000-000000000000'::uuid),
 created_at timestamptz NOT NULL DEFAULT statement_timestamp() CHECK(isfinite(created_at)),
 updated_at timestamptz NOT NULL DEFAULT statement_timestamp() CHECK(isfinite(updated_at))
);
CREATE TABLE access.operator_authorities (
 id uuid PRIMARY KEY CHECK(id<>'00000000-0000-0000-0000-000000000000'::uuid),
 database_login name NOT NULL REFERENCES access.operator_principals(database_login) ON DELETE RESTRICT,
 command text NOT NULL CHECK(command='application.register'),
 scope_kind text NOT NULL CHECK(scope_kind='platform'),
 org_id uuid CHECK(org_id IS NULL),
 application_id text CHECK(application_id IS NULL OR application_id COLLATE "C" ~ '^[a-z][a-z0-9_]{1,63}$'),
 target_account_id uuid CHECK(target_account_id IS NULL),
 enabled boolean NOT NULL DEFAULT false,
 revision bigint NOT NULL DEFAULT 1 CHECK(revision>0),
 created_by uuid NOT NULL CHECK(created_by<>'00000000-0000-0000-0000-000000000000'::uuid),
 updated_by uuid NOT NULL CHECK(updated_by<>'00000000-0000-0000-0000-000000000000'::uuid),
 created_at timestamptz NOT NULL DEFAULT statement_timestamp() CHECK(isfinite(created_at)),
 updated_at timestamptz NOT NULL DEFAULT statement_timestamp() CHECK(isfinite(updated_at)),
 UNIQUE NULLS NOT DISTINCT(database_login,command,scope_kind,org_id,application_id,target_account_id)
);
CREATE TABLE access.operation_outcome (
 id uuid PRIMARY KEY CHECK(id<>'00000000-0000-0000-0000-000000000000'::uuid),
 executor_actor_id uuid NOT NULL CHECK(executor_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid),
 operation_id uuid NOT NULL CHECK(operation_id<>'00000000-0000-0000-0000-000000000000'::uuid),
 command_type text NOT NULL CHECK(command_type='application.register'),
 scope_kind text NOT NULL CHECK(scope_kind='platform'),
 scope_id uuid CHECK(scope_id IS NULL),
 initiator_actor_id uuid CHECK(initiator_actor_id IS NULL),
 command_version integer NOT NULL CHECK(command_version=1),
 fingerprint_version integer NOT NULL CHECK(fingerprint_version=1),
 fingerprint_algorithm text NOT NULL CHECK(fingerprint_algorithm='sha256'),
 fingerprint_key_id text CHECK(fingerprint_key_id IS NULL),
 fingerprint bytea NOT NULL CHECK(octet_length(fingerprint)=32),
 result_version integer NOT NULL CHECK(result_version=1),
 result jsonb NOT NULL CHECK(jsonb_typeof(result)='object' AND octet_length(result::text)<=8192),
 committed_at timestamptz NOT NULL DEFAULT statement_timestamp() CHECK(isfinite(committed_at)),
 UNIQUE(executor_actor_id,operation_id)
);
CREATE TABLE access.business_event (
 event_id uuid PRIMARY KEY CHECK(event_id<>'00000000-0000-0000-0000-000000000000'::uuid),
 event_type text NOT NULL CHECK(event_type='access.application_registered'),
 event_version integer NOT NULL CHECK(event_version=1),
 scope_kind text NOT NULL DEFAULT 'platform' CHECK(scope_kind='platform'),
 scope_id uuid CHECK(scope_id IS NULL),
 initiator_actor_id uuid CHECK(initiator_actor_id IS NULL),
 executor_actor_id uuid NOT NULL CHECK(executor_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid),
 operation_id uuid NOT NULL,
 outcome_id uuid NOT NULL UNIQUE REFERENCES access.operation_outcome(id) ON DELETE RESTRICT,
 target jsonb NOT NULL,
 transition jsonb NOT NULL,
 reason_code text NOT NULL CHECK(reason_code IN ('initial_setup','synthetic_fixture','identity_adoption','access_change','setup_correction')),
 evidence_ref text CHECK(evidence_ref COLLATE "C" ~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$' AND position('://' in evidence_ref)=0),
 created_at timestamptz NOT NULL DEFAULT statement_timestamp() CHECK(isfinite(created_at))
);
CREATE FUNCTION access.command_lock(value text) RETURNS bigint
LANGUAGE sql IMMUTABLE SET search_path=pg_catalog,pg_temp AS $f$
 SELECT ('x'||encode(substring(sha256(convert_to(value,'UTF8')) FROM 1 FOR 8),'hex'))::bit(64)::bigint
$f$;
CREATE FUNCTION access.current_operator_authority(p_app text) RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT p.executor_actor_id FROM access.operator_principals p
 JOIN access.operator_authorities a ON a.database_login=p.database_login
 WHERE p.database_login=session_user AND p.enabled AND a.enabled
 AND a.command='application.register' AND a.scope_kind='platform' AND a.org_id IS NULL AND a.target_account_id IS NULL
 AND (a.application_id IS NULL OR a.application_id=p_app)
 ORDER BY a.id LIMIT 1
$f$;
CREATE FUNCTION access.guard_operator_authority() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF current_user<>'access_migrator' OR TG_OP IN ('DELETE','TRUNCATE') THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_authority_retained'; END IF;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:'||NEW.database_login::text));
 IF TG_OP='INSERT' THEN
  NEW.revision:=1; NEW.created_at:=statement_timestamp(); NEW.updated_at:=NEW.created_at; NEW.updated_by:=NEW.created_by;
 ELSE
  IF (to_jsonb(NEW)-ARRAY['enabled','revision','updated_by','updated_at']) IS DISTINCT FROM
     (to_jsonb(OLD)-ARRAY['enabled','revision','updated_by','updated_at']) THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_authority_identity_immutable'; END IF;
  IF NEW.enabled IS DISTINCT FROM OLD.enabled THEN
   NEW.revision:=OLD.revision+1; NEW.updated_at:=statement_timestamp();
  ELSE NEW.revision:=OLD.revision; NEW.updated_at:=OLD.updated_at; NEW.updated_by:=OLD.updated_by; END IF;
 END IF;
 RETURN NEW;
END $f$;
CREATE TRIGGER operator_principals_guard BEFORE INSERT OR UPDATE OR DELETE ON access.operator_principals FOR EACH ROW EXECUTE FUNCTION access.guard_operator_authority();
CREATE TRIGGER operator_principals_retention BEFORE TRUNCATE ON access.operator_principals FOR EACH STATEMENT EXECUTE FUNCTION access.guard_operator_authority();
CREATE TRIGGER operator_authorities_guard BEFORE INSERT OR UPDATE OR DELETE ON access.operator_authorities FOR EACH ROW EXECUTE FUNCTION access.guard_operator_authority();
CREATE TRIGGER operator_authorities_retention BEFORE TRUNCATE ON access.operator_authorities FOR EACH STATEMENT EXECUTE FUNCTION access.guard_operator_authority();
CREATE FUNCTION access.guard_command_evidence() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
DECLARE saved access.operation_outcome; app access.applications; executor uuid; event uuid;
BEGIN
 IF TG_OP<>'INSERT' THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_evidence_immutable'; END IF;
 IF current_user<>'access_command_owner' THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_command_owner_required'; END IF;
 IF TG_TABLE_NAME='operation_outcome' THEN
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
  NEW.committed_at:=statement_timestamp();
 ELSE
  SELECT * INTO saved FROM access.operation_outcome o WHERE o.id=NEW.outcome_id;
  IF saved.id IS NULL OR NEW.event_id IS DISTINCT FROM (saved.result->>'event_id')::uuid
   OR NEW.executor_actor_id<>saved.executor_actor_id OR NEW.operation_id<>saved.operation_id
   OR NEW.target IS DISTINCT FROM saved.result->'target' OR saved.result->>'disposition'<>'created'
   OR NEW.transition IS DISTINCT FROM jsonb_build_object('enabled',false,'revision','1') THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_event_invalid'; END IF;
  NEW.created_at:=saved.committed_at;
 END IF;
 RETURN NEW;
END $f$;
CREATE TRIGGER operation_outcome_guard BEFORE INSERT OR UPDATE OR DELETE ON access.operation_outcome FOR EACH ROW EXECUTE FUNCTION access.guard_command_evidence();
CREATE TRIGGER operation_outcome_retention BEFORE TRUNCATE ON access.operation_outcome FOR EACH STATEMENT EXECUTE FUNCTION access.guard_command_evidence();
CREATE TRIGGER business_event_guard BEFORE INSERT OR UPDATE OR DELETE ON access.business_event FOR EACH ROW EXECUTE FUNCTION access.guard_command_evidence();
CREATE TRIGGER business_event_retention BEFORE TRUNCATE ON access.business_event FOR EACH STATEMENT EXECUTE FUNCTION access.guard_command_evidence();
CREATE FUNCTION access.require_command_event() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF NEW.result->>'disposition'='created' AND NOT EXISTS(SELECT 1 FROM access.business_event e WHERE e.outcome_id=NEW.id AND e.event_id=(NEW.result->>'event_id')::uuid) THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_required_event_missing'; END IF;
 RETURN NULL;
END $f$;
CREATE CONSTRAINT TRIGGER operation_outcome_required_event AFTER INSERT ON access.operation_outcome DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION access.require_command_event();
CREATE FUNCTION access.require_application_registration() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM access.operation_outcome o JOIN access.business_event e ON e.outcome_id=o.id
  WHERE o.result->'target'=jsonb_build_object('app_id',NEW.app_id) AND o.result->>'disposition'='created'
  AND o.executor_actor_id=NEW.created_by AND o.committed_at=NEW.created_at
  AND e.event_id=(o.result->>'event_id')::uuid) THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='access_required_registration_missing'; END IF;
 RETURN NULL;
END $f$;
CREATE CONSTRAINT TRIGGER application_required_registration AFTER INSERT ON access.applications DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION access.require_application_registration();
CREATE FUNCTION access.register_application(p_operation uuid,p_app text,p_reason text,p_evidence text,p_canonical bytea)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; saved access.operation_outcome; app access.applications; expected jsonb; doc jsonb; lock_document text; event uuid; outcome_id uuid; disposition text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid
 OR p_app IS NULL OR p_app COLLATE "C" !~ '^[a-z][a-z0-9_]{1,63}$' OR p_reason IS NULL OR p_reason NOT IN ('initial_setup','synthetic_fixture','identity_adoption','access_change','setup_correction')
 OR (p_evidence IS NOT NULL AND (p_evidence COLLATE "C" !~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$' OR position('://' in p_evidence)>0))
 OR p_canonical IS NULL OR octet_length(p_canonical)>65536 THEN
  RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 expected:=jsonb_build_object('schema_version',1,'command','application.register','operation_id',p_operation::text,'scope',jsonb_build_object('kind','platform'),
 'payload',jsonb_build_object('app_id',p_app,'expected_absent',true),'reason_code',p_reason,'evidence_ref',p_evidence);
 BEGIN doc:=convert_from(p_canonical,'UTF8')::jsonb; EXCEPTION WHEN OTHERS THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END;
 -- This fixed ASCII envelope has no numbers except 1 and no unbounded JSON values.
 IF doc IS DISTINCT FROM expected OR convert_from(p_canonical,'UTF8') IS DISTINCT FROM
  '{"command":"application.register","evidence_ref":'||coalesce(to_json(p_evidence)::text,'null')||',"operation_id":'||to_json(p_operation::text)::text||',"payload":{"app_id":'||to_json(p_app)::text||',"expected_absent":true},"reason_code":'||to_json(p_reason)::text||',"schema_version":1,"scope":{"kind":"platform"}}' THEN
  RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 executor:=access.current_operator_authority(p_app);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"application.register","lock_version":1,"operation_id":'||to_json(p_operation::text)::text||',"owner_schema":"access","scope_id":null,"scope_kind":"platform"}';
 BEGIN PERFORM pg_advisory_xact_lock(access.command_lock(lock_document)); EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='AC001',MESSAGE='access_operation_busy'; END;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM access.current_operator_authority(p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 SELECT * INTO saved FROM access.operation_outcome o WHERE o.executor_actor_id=executor AND o.operation_id=p_operation;
 IF FOUND THEN
  IF saved.fingerprint<>sha256(p_canonical) THEN RAISE EXCEPTION USING ERRCODE='AC003',MESSAGE='access_operation_conflict'; END IF;
  RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at; RETURN;
 END IF;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:application:v1:'||p_app));
 IF executor IS DISTINCT FROM access.current_operator_authority(p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 SELECT * INTO app FROM access.applications a WHERE a.app_id=p_app;
 IF FOUND THEN disposition:='unchanged'; event:=NULL;
 ELSE
  INSERT INTO access.applications(app_id,created_by,updated_by,created_at,updated_at)
   VALUES(p_app,executor,executor,statement_timestamp(),statement_timestamp()) RETURNING * INTO app;
  disposition:='created'; event:=gen_random_uuid();
 END IF;
 outcome_id:=gen_random_uuid();
 INSERT INTO access.operation_outcome(id,executor_actor_id,operation_id,command_type,scope_kind,command_version,fingerprint_version,fingerprint_algorithm,fingerprint,result_version,result)
 VALUES(outcome_id,executor,p_operation,'application.register','platform',1,1,'sha256',sha256(p_canonical),1,
 jsonb_build_object('target',jsonb_build_object('app_id',p_app),'disposition',disposition,'revision',app.revision::text,'event_id',event)) RETURNING * INTO saved;
 IF event IS NOT NULL THEN
  INSERT INTO access.business_event(event_id,event_type,event_version,executor_actor_id,operation_id,outcome_id,target,transition,reason_code,evidence_ref)
  VALUES(event,'access.application_registered',1,executor,p_operation,outcome_id,jsonb_build_object('app_id',p_app),jsonb_build_object('enabled',false,'revision','1'),p_reason,p_evidence);
 END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
CREATE FUNCTION access.application_registration_outcome(p_operation uuid,p_app text)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid; saved access.operation_outcome; lock_document text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000'::uuid
 OR p_app IS NULL OR p_app COLLATE "C" !~ '^[a-z][a-z0-9_]{1,63}$' THEN RAISE EXCEPTION USING ERRCODE='AC005',MESSAGE='access_command_invalid'; END IF;
 executor:=access.current_operator_authority(p_app);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"application.register","lock_version":1,"operation_id":'||to_json(p_operation::text)::text||',"owner_schema":"access","scope_id":null,"scope_kind":"platform"}';
 BEGIN PERFORM pg_advisory_xact_lock(access.command_lock(lock_document)); EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='AC001',MESSAGE='access_operation_busy'; END;
 PERFORM pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM access.current_operator_authority(p_app) THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 SELECT * INTO saved FROM access.operation_outcome o WHERE o.executor_actor_id=executor AND o.operation_id=p_operation;
 IF NOT FOUND THEN RETURN; END IF;
 IF saved.result->'target'->>'app_id' IS DISTINCT FROM p_app THEN RAISE EXCEPTION USING ERRCODE='AC002',MESSAGE='access_denied'; END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
DO $acl$
DECLARE r record; a record; grantee text;
BEGIN
 FOR r IN SELECT c.relowner owner,c.relacl acl,c.oid::regclass::text object FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
 WHERE n.nspname='access' AND c.relname IN ('operator_principals','operator_authorities','operation_outcome','business_event') LOOP
  EXECUTE format('REVOKE ALL ON TABLE %s FROM PUBLIC',r.object);
  FOR a IN SELECT DISTINCT x.grantee FROM aclexplode(r.acl) x WHERE x.grantee<>r.owner LOOP
   grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
   EXECUTE format('REVOKE ALL ON TABLE %s FROM %s',r.object,grantee);
  END LOOP;
 END LOOP;
 FOR r IN SELECT p.proowner owner,p.proacl acl,p.oid::regprocedure::text object FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
 WHERE n.nspname='access' AND p.proname IN ('command_lock','current_operator_authority','guard_operator_authority','guard_command_evidence','require_command_event','require_application_registration','register_application','application_registration_outcome') LOOP
  EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',r.object);
  FOR a IN SELECT DISTINCT x.grantee FROM aclexplode(r.acl) x WHERE x.grantee<>r.owner LOOP
   grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
   EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s',r.object,grantee);
  END LOOP;
 END LOOP;
END $acl$;
GRANT USAGE ON SCHEMA access TO access_operator,access_operator_authority_owner,access_command_owner;
GRANT SELECT(database_login,executor_actor_id,enabled) ON access.operator_principals TO access_operator_authority_owner;
GRANT SELECT(id,database_login,command,scope_kind,org_id,application_id,target_account_id,enabled) ON access.operator_authorities TO access_operator_authority_owner;
GRANT SELECT,INSERT ON access.applications,access.operation_outcome,access.business_event TO access_command_owner;
REVOKE ALL ON access.operator_principals,access.operator_authorities,access.operation_outcome,access.business_event FROM PUBLIC;
REVOKE ALL ON FUNCTION access.command_lock(text),access.current_operator_authority(text),access.guard_operator_authority(),access.guard_command_evidence(),access.require_command_event(),access.require_application_registration(),access.register_application(uuid,text,text,text,bytea),access.application_registration_outcome(uuid,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION access.command_lock(text),access.current_operator_authority(text) TO access_command_owner;
GRANT EXECUTE ON FUNCTION access.register_application(uuid,text,text,text,bytea),access.application_registration_outcome(uuid,text) TO access_operator;
GRANT CREATE ON SCHEMA access TO access_operator_authority_owner,access_command_owner;
ALTER FUNCTION access.current_operator_authority(text) OWNER TO access_operator_authority_owner;
ALTER FUNCTION access.require_command_event() OWNER TO access_command_owner;
ALTER FUNCTION access.require_application_registration() OWNER TO access_command_owner;
ALTER FUNCTION access.register_application(uuid,text,text,text,bytea) OWNER TO access_command_owner;
ALTER FUNCTION access.application_registration_outcome(uuid,text) OWNER TO access_command_owner;
REVOKE CREATE ON SCHEMA access FROM access_operator_authority_owner,access_command_owner;
'''

def upgrade():
    from access_baseline import verify_operator_roles
    verify_operator_roles(op.get_bind())
    op.get_bind().exec_driver_sql(SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
