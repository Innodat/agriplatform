"""Dormant owner-private transactional corpus controller; no caller provisioning."""
revision = 'scribeswell_0003'
down_revision = 'scribeswell_0002'
branch_labels = None
depends_on = None

DDL = r"""
CREATE TABLE scribeswell.corpus_operator_principal (
 database_login name PRIMARY KEY CHECK (database_login='scribeswell_corpus_operator'),
 enabled boolean NOT NULL DEFAULT false,
 revision bigint NOT NULL CHECK (revision>0),
 executor_actor_id uuid NOT NULL CHECK (executor_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid),
 actor_kind text NOT NULL CHECK (actor_kind='service'),
 actor_key text NOT NULL CHECK (actor_key ~ '^[a-z][a-z0-9_.:-]{0,127}$'),
 preparation_evidence_ref text NOT NULL CHECK (preparation_evidence_ref ~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$'),
 created_by_actor_id uuid NOT NULL CHECK (created_by_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid),
 updated_by_actor_id uuid NOT NULL CHECK (updated_by_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid),
 created_at timestamptz NOT NULL DEFAULT transaction_timestamp() CHECK (isfinite(created_at)),
 updated_at timestamptz NOT NULL DEFAULT transaction_timestamp() CHECK (isfinite(updated_at))
);
CREATE TABLE scribeswell.corpus_operator_authority (
 database_login name NOT NULL REFERENCES scribeswell.corpus_operator_principal(database_login) ON DELETE RESTRICT,
 source_id text NOT NULL CHECK (source_id ~ '^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$'),
 command text NOT NULL CHECK (command IN ('corpus.begin','corpus.recover','corpus.seal')),
 enabled boolean NOT NULL DEFAULT false,
 revision bigint NOT NULL CHECK (revision>0),
 created_by_actor_id uuid NOT NULL CHECK (created_by_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid),
 updated_by_actor_id uuid NOT NULL CHECK (updated_by_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid),
 created_at timestamptz NOT NULL DEFAULT transaction_timestamp() CHECK (isfinite(created_at)),
 updated_at timestamptz NOT NULL DEFAULT transaction_timestamp() CHECK (isfinite(updated_at)),
 PRIMARY KEY (database_login,source_id,command)
);
CREATE TABLE scribeswell.corpus_attempt (
 attempt_id uuid PRIMARY KEY DEFAULT gen_random_uuid() CHECK (attempt_id<>'00000000-0000-0000-0000-000000000000'::uuid),
 source_id text NOT NULL CHECK (source_id ~ '^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$'),
 generation bigint NOT NULL CHECK (generation>0),
 input_sha256 text NOT NULL CHECK (input_sha256 ~ '^[0-9a-f]{64}$'),
 catalogue_version text NOT NULL CHECK (catalogue_version ~ '^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$'),
 versification_id text NOT NULL CHECK (versification_id ~ '^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$'),
 tokenization_version text NOT NULL CHECK (tokenization_version ~ '^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$'),
 state text NOT NULL CHECK (state IN ('updating','closed','retired')),
 created_by_actor_id uuid NOT NULL CHECK (created_by_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid),
 updated_by_actor_id uuid NOT NULL CHECK (updated_by_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid),
 created_at timestamptz NOT NULL DEFAULT transaction_timestamp() CHECK (isfinite(created_at)),
 updated_at timestamptz NOT NULL DEFAULT transaction_timestamp() CHECK (isfinite(updated_at)),
 UNIQUE (source_id,generation), UNIQUE (attempt_id,source_id,generation)
);
CREATE TABLE scribeswell.corpus_command_outcome (
 database_login name NOT NULL REFERENCES scribeswell.corpus_operator_principal(database_login) ON DELETE RESTRICT,
 operation_id uuid NOT NULL CHECK (operation_id<>'00000000-0000-0000-0000-000000000000'::uuid),
 semantic_command jsonb NOT NULL CHECK (jsonb_typeof(semantic_command)='object'),
 executor_actor_id uuid NOT NULL CHECK (executor_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid),
 principal_revision bigint NOT NULL CHECK (principal_revision>0),
 authority_revision bigint NOT NULL CHECK (authority_revision>0),
 result jsonb NOT NULL CHECK (jsonb_typeof(result)='object'),
 attempt_id uuid NOT NULL,
 source_id text NOT NULL,
 generation bigint NOT NULL CHECK (generation>0),
 created_by_actor_id uuid NOT NULL CHECK (created_by_actor_id=executor_actor_id),
 created_at timestamptz NOT NULL DEFAULT transaction_timestamp() CHECK (isfinite(created_at)),
 PRIMARY KEY (database_login,operation_id),
 FOREIGN KEY (attempt_id,source_id,generation) REFERENCES scribeswell.corpus_attempt(attempt_id,source_id,generation) ON DELETE RESTRICT
);
REVOKE ALL ON scribeswell.corpus_operator_principal, scribeswell.corpus_operator_authority,
 scribeswell.corpus_attempt, scribeswell.corpus_command_outcome
 FROM PUBLIC,anon,authenticated,service_role,scribeswell_runtime,scribeswell_import;

CREATE FUNCTION scribeswell.protect_corpus_controller_record() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $body$
BEGIN
 IF TG_OP='DELETE' OR (TG_TABLE_NAME='corpus_command_outcome' AND TG_OP='UPDATE') THEN
  RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publication.conflict';
 END IF;
 IF TG_OP='UPDATE' THEN
  IF NEW.created_by_actor_id<>OLD.created_by_actor_id OR NEW.created_at<>OLD.created_at THEN
   RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publication.conflict';
  END IF;
  IF TG_TABLE_NAME='corpus_operator_principal' THEN
   IF (NEW.database_login<>OLD.database_login OR NEW.actor_key<>OLD.actor_key OR NEW.actor_kind<>OLD.actor_kind
    OR NEW.preparation_evidence_ref<>OLD.preparation_evidence_ref OR NEW.revision<=OLD.revision) THEN
   RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publication.conflict';
   END IF;
  ELSIF TG_TABLE_NAME='corpus_operator_authority' THEN
   IF (NEW.database_login<>OLD.database_login OR NEW.source_id<>OLD.source_id OR NEW.command<>OLD.command OR NEW.revision<=OLD.revision) THEN
   RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publication.conflict';
   END IF;
  ELSIF TG_TABLE_NAME='corpus_attempt' THEN
   IF (NEW.attempt_id<>OLD.attempt_id OR NEW.source_id<>OLD.source_id OR NEW.generation<>OLD.generation
    OR NEW.input_sha256<>OLD.input_sha256 OR NEW.catalogue_version<>OLD.catalogue_version
    OR NEW.versification_id<>OLD.versification_id OR NEW.tokenization_version<>OLD.tokenization_version
    OR OLD.state='retired' OR (OLD.state='closed' AND NEW.state<>'retired')
    OR (OLD.state='updating' AND NEW.state NOT IN ('closed','retired'))) THEN
   RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publication.conflict';
  END IF;
   END IF;
 ELSE
  NEW.created_at=transaction_timestamp();
 END IF;
 IF TG_TABLE_NAME<>'corpus_command_outcome' THEN NEW.updated_at=transaction_timestamp(); END IF;
 RETURN NEW;
END
$body$;

CREATE FUNCTION scribeswell.validate_corpus_command(request jsonb) RETURNS void
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $body$
DECLARE scope jsonb; payload jsonb; identity jsonb; variant text; value text;
BEGIN
 IF request IS NULL OR jsonb_typeof(request)<>'object' OR octet_length(request::text)>65536 THEN
  RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publication.input_invalid';
 END IF;
 IF (SELECT array_agg(k ORDER BY k) FROM jsonb_object_keys(request) k) IS DISTINCT FROM
 ARRAY['command','evidence_ref','operation_id','payload','reason_code','schema_version','scope']
 OR request->>'schema_version'<>'1' OR jsonb_typeof(request->'schema_version')<>'number'
 OR jsonb_typeof(request->'command')<>'string' OR jsonb_typeof(request->'operation_id')<>'string'
 OR request->>'operation_id' !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
 OR request->>'operation_id'='00000000-0000-0000-0000-000000000000'
 OR jsonb_typeof(request->'evidence_ref')<>'string' OR request->>'evidence_ref' !~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$'
 THEN RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publication.input_invalid'; END IF;
 variant=request->>'command'; scope=request->'scope'; payload=request->'payload';
 IF variant NOT IN ('corpus.begin','corpus.recover','corpus.seal')
 OR jsonb_typeof(request->'reason_code')<>'string'
 OR request->>'reason_code' NOT IN ('synthetic_fixture',CASE variant WHEN 'corpus.begin' THEN 'source_import' WHEN 'corpus.recover' THEN 'source_recovery' ELSE 'source_seal' END)
 OR jsonb_typeof(scope)<>'object' OR jsonb_typeof(payload)<>'object' THEN
  RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publication.input_invalid'; END IF;
 IF (SELECT array_agg(k ORDER BY k) FROM jsonb_object_keys(scope) k) IS DISTINCT FROM ARRAY['kind','source_id']
 OR scope->'kind'<>'"source"'::jsonb OR jsonb_typeof(scope->'source_id')<>'string'
 OR scope->>'source_id' !~ '^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$' THEN
  RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publication.input_invalid'; END IF;
 IF variant='corpus.begin' THEN
  IF (SELECT array_agg(k ORDER BY k) FROM jsonb_object_keys(payload) k) IS DISTINCT FROM ARRAY['expected_absent','input'] OR payload->'expected_absent'<>'true'::jsonb THEN
   RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publication.input_invalid'; END IF;
 ELSE
  IF (SELECT array_agg(k ORDER BY k) FROM jsonb_object_keys(payload) k) IS DISTINCT FROM ARRAY['expected_attempt_id','expected_generation','input']
  OR jsonb_typeof(payload->'expected_generation')<>'string' OR payload->>'expected_generation' !~ '^[1-9][0-9]{0,18}$'
  OR jsonb_typeof(payload->'expected_attempt_id')<>'string' OR payload->>'expected_attempt_id' !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
  OR payload->>'expected_attempt_id'='00000000-0000-0000-0000-000000000000' THEN
   RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publication.input_invalid'; END IF;
  IF (payload->>'expected_generation')::numeric>9223372036854775807 THEN
   RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publication.input_invalid'; END IF;
 END IF;
 identity=payload->'input';
 IF jsonb_typeof(identity)<>'object' THEN RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publication.input_invalid'; END IF;
 IF (SELECT array_agg(k ORDER BY k) FROM jsonb_object_keys(identity) k) IS DISTINCT FROM ARRAY['catalogue_version','source_sha256','tokenization_version','versification_id']
 OR jsonb_typeof(identity->'source_sha256')<>'string' OR identity->>'source_sha256' !~ '^[0-9a-f]{64}$' THEN
  RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publication.input_invalid'; END IF;
 FOREACH value IN ARRAY ARRAY['catalogue_version','versification_id','tokenization_version'] LOOP
  IF jsonb_typeof(identity->value)<>'string' OR identity->>value !~ '^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$' THEN
   RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='corpus_publication.input_invalid'; END IF;
 END LOOP;
END
$body$;

CREATE FUNCTION scribeswell.corpus_command_internal(request jsonb, lookup_only boolean) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $body$
DECLARE principal record;
 authority record;
 previous record;
 epoch record;
 attempt record;
 source text; variant text; operation uuid; identity jsonb; enabled boolean;
 next_attempt uuid; next_generation bigint; next_state text; receipt jsonb;
BEGIN
 -- Adapter sets finite local waits; direct calls are bounded too, never disable a smaller bound.
 IF current_setting('lock_timeout')::interval=interval '0' OR current_setting('lock_timeout')::interval>interval '2 seconds' THEN
  PERFORM set_config('lock_timeout','2s',true); END IF;
 PERFORM scribeswell.validate_corpus_command(request);
 IF current_setting('transaction_isolation')<>'read committed' OR current_setting('transaction_read_only')<>'off' THEN
  RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='corpus_publication.unavailable'; END IF;
 IF session_user<>'scribeswell_corpus_operator' OR NOT EXISTS
  (SELECT FROM pg_roles r WHERE r.rolname=session_user AND r.rolcanlogin AND NOT r.rolinherit
   AND NOT r.rolsuper AND NOT r.rolbypassrls AND NOT r.rolcreatedb AND NOT r.rolcreaterole AND NOT r.rolreplication
   AND NOT EXISTS (SELECT FROM pg_auth_members m WHERE m.member=r.oid OR m.roleid=r.oid)) THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='corpus_publication.access_denied'; END IF;
 source=request#>>'{scope,source_id}'; variant=request->>'command'; operation=(request->>'operation_id')::uuid;
 identity=request#>'{payload,input}';
 SELECT * INTO principal FROM scribeswell.corpus_operator_principal WHERE database_login=session_user FOR SHARE;
 IF NOT FOUND OR NOT principal.enabled THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='corpus_publication.access_denied'; END IF;
 SELECT * INTO authority FROM scribeswell.corpus_operator_authority
 WHERE database_login=session_user AND source_id=source AND command=variant FOR SHARE;
 IF NOT FOUND OR NOT authority.enabled THEN RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='corpus_publication.access_denied'; END IF;
 PERFORM pg_advisory_xact_lock(hashtextextended(session_user::text||':'||operation::text, 31003));
 SELECT * INTO previous FROM scribeswell.corpus_command_outcome WHERE database_login=session_user AND operation_id=operation;
 IF FOUND THEN
  IF previous.semantic_command<>request OR previous.executor_actor_id<>principal.executor_actor_id THEN
   RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publication.conflict'; END IF;
  RETURN previous.result;
 END IF;
 IF lookup_only THEN RETURN NULL; END IF;
 SELECT enforcement INTO enabled FROM scribeswell.corpus_fence_control WHERE singleton FOR SHARE;
 IF NOT FOUND OR NOT enabled THEN RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='corpus_publication.unavailable'; END IF;
 PERFORM pg_advisory_xact_lock(31003,1);
 SELECT * INTO epoch FROM scribeswell.corpus_epoch WHERE singleton FOR UPDATE;
 IF variant='corpus.begin' THEN
  IF FOUND THEN RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publication.conflict'; END IF;
  next_generation=1;
 ELSE
  IF NOT FOUND OR epoch.source_id<>source OR epoch.generation<>(request#>>'{payload,expected_generation}')::bigint
   OR epoch.attempt_id<>(request#>>'{payload,expected_attempt_id}')::uuid THEN
   RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publication.conflict'; END IF;
  SELECT * INTO attempt FROM scribeswell.corpus_attempt WHERE attempt_id=epoch.attempt_id FOR UPDATE;
  IF NOT FOUND OR attempt.source_id<>epoch.source_id OR attempt.generation<>epoch.generation
   OR attempt.state<>epoch.state OR attempt.input_sha256<>epoch.input_sha256 THEN
   RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publication.conflict'; END IF;
  IF variant='corpus.seal' THEN
   IF epoch.state<>'updating' OR attempt.input_sha256<>identity->>'source_sha256'
    OR attempt.catalogue_version<>identity->>'catalogue_version' OR attempt.versification_id<>identity->>'versification_id'
    OR attempt.tokenization_version<>identity->>'tokenization_version' THEN
    RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publication.conflict'; END IF;
   next_attempt=epoch.attempt_id; next_generation=epoch.generation; next_state='closed';
   UPDATE scribeswell.corpus_attempt SET state='closed',updated_by_actor_id=principal.executor_actor_id WHERE attempt_id=next_attempt;
  ELSE
   IF epoch.generation=9223372036854775807 THEN RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='corpus_publication.conflict'; END IF;
   next_generation=epoch.generation+1;
   UPDATE scribeswell.corpus_attempt SET state='retired',updated_by_actor_id=principal.executor_actor_id WHERE attempt_id=epoch.attempt_id;
  END IF;
 END IF;
 IF variant<>'corpus.seal' THEN
  next_attempt=gen_random_uuid(); next_state='updating';
  INSERT INTO scribeswell.corpus_attempt(attempt_id,source_id,generation,input_sha256,catalogue_version,versification_id,tokenization_version,state,created_by_actor_id,updated_by_actor_id)
  VALUES(next_attempt,source,next_generation,identity->>'source_sha256',identity->>'catalogue_version',identity->>'versification_id',identity->>'tokenization_version',next_state,principal.executor_actor_id,principal.executor_actor_id);
 END IF;
 IF variant='corpus.begin' THEN
  INSERT INTO scribeswell.corpus_epoch(source_id,generation,attempt_id,input_sha256,state,created_by_actor_id,updated_by_actor_id)
  VALUES(source,next_generation,next_attempt,identity->>'source_sha256',next_state,principal.executor_actor_id,principal.executor_actor_id);
 ELSE
  UPDATE scribeswell.corpus_epoch SET generation=next_generation,attempt_id=next_attempt,input_sha256=identity->>'source_sha256',state=next_state,updated_by_actor_id=principal.executor_actor_id,updated_at=transaction_timestamp() WHERE singleton;
 END IF;
 receipt=jsonb_build_object('version',1,'operation_id',operation::text,'command',variant,'source_id',source,
 'executor_actor_id',principal.executor_actor_id::text,'attempt_id',next_attempt::text,'generation',next_generation::text,'state',next_state);
 INSERT INTO scribeswell.corpus_command_outcome(database_login,operation_id,semantic_command,executor_actor_id,principal_revision,authority_revision,result,attempt_id,source_id,generation,created_by_actor_id)
 VALUES(session_user,operation,request,principal.executor_actor_id,principal.revision,authority.revision,receipt,next_attempt,source,next_generation,principal.executor_actor_id);
 RETURN receipt;
END
$body$;
CREATE FUNCTION scribeswell.execute_corpus_command(request jsonb) RETURNS jsonb
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog AS $body$
 SELECT scribeswell.corpus_command_internal(request,false)
$body$;
CREATE FUNCTION scribeswell.lookup_corpus_command_outcome(request jsonb) RETURNS jsonb
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog AS $body$
 SELECT scribeswell.corpus_command_internal(request,true)
$body$;
REVOKE ALL ON FUNCTION scribeswell.protect_corpus_controller_record(),scribeswell.validate_corpus_command(jsonb),
 scribeswell.corpus_command_internal(jsonb,boolean),scribeswell.execute_corpus_command(jsonb),scribeswell.lookup_corpus_command_outcome(jsonb)
 FROM PUBLIC,anon,authenticated,service_role,scribeswell_runtime,scribeswell_import;
"""
for table in ('corpus_operator_principal','corpus_operator_authority','corpus_attempt','corpus_command_outcome'):
    DDL += f"""
CREATE TRIGGER corpus_record_protection BEFORE INSERT OR UPDATE OR DELETE ON scribeswell.{table}
 FOR EACH ROW EXECUTE FUNCTION scribeswell.protect_corpus_controller_record();
ALTER TABLE scribeswell.{table} ENABLE ALWAYS TRIGGER corpus_record_protection;
"""

def upgrade():
    from alembic import op
    op.get_bind().exec_driver_sql(DDL)

def downgrade():
    raise RuntimeError('scribeswell_downgrade_prohibited')
