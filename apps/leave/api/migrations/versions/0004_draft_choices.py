"""Published draft catalogue and restricted Leave-owned configuration commands."""
from alembic import op
revision='0004_draft_choices'
down_revision='0003_draft_context'
branch_labels=None
depends_on=None

def upgrade():
    op.execute(r'''
    CREATE TABLE leave.leave_type (
      id uuid PRIMARY KEY CHECK(id<>'00000000-0000-0000-0000-000000000000'),
      org_id uuid NOT NULL CHECK(org_id<>'00000000-0000-0000-0000-000000000000'),
      code text NOT NULL CHECK(code COLLATE "C" ~ '^[a-z][a-z0-9_]{0,63}$'),
      archived_at timestamptz,choice_version_id uuid,
      revision bigint NOT NULL CHECK(revision>0),
      created_by uuid NOT NULL,created_at timestamptz NOT NULL,
      updated_by uuid NOT NULL,updated_at timestamptz NOT NULL,
      UNIQUE(org_id,id),UNIQUE(org_id,code)
    );
    CREATE TABLE leave.leave_type_version (
      id uuid PRIMARY KEY CHECK(id<>'00000000-0000-0000-0000-000000000000'),
      org_id uuid NOT NULL,leave_type_id uuid NOT NULL,
      version_number bigint NOT NULL CHECK(version_number>0),
      name text NOT NULL CHECK(length(name) BETWEEN 1 AND 120 AND name=btrim(name,U&'\0009\000A\000B\000C\000D\001C\001D\001E\001F\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000') AND name !~ '[[:cntrl:]]'),
      permitted_modes text[] NOT NULL CHECK(cardinality(permitted_modes) BETWEEN 1 AND 3 AND array_ndims(permitted_modes)=1 AND array_lower(permitted_modes,1)=1 AND permitted_modes<@ARRAY['full_days','half_day','hours']::text[] AND array_position(permitted_modes,NULL) IS NULL),
      effective_from date NOT NULL CHECK(isfinite(effective_from)),effective_to date CHECK(isfinite(effective_to) AND effective_to>=effective_from),
      published_at timestamptz,
      created_by uuid NOT NULL,created_at timestamptz NOT NULL,
      FOREIGN KEY(org_id,leave_type_id) REFERENCES leave.leave_type(org_id,id) ON DELETE RESTRICT,
      UNIQUE(org_id,leave_type_id,id),UNIQUE(org_id,leave_type_id,version_number)
    );
    ALTER TABLE leave.leave_type ADD CONSTRAINT choice_version_scope FOREIGN KEY(org_id,id,choice_version_id) REFERENCES leave.leave_type_version(org_id,leave_type_id,id) ON DELETE RESTRICT;
    CREATE FUNCTION leave.stamp_choice_type() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,leave AS $$
    DECLARE actor uuid:=leave.context_scope('app.actor_id');
    BEGIN
      IF TG_OP='DELETE' THEN RAISE EXCEPTION 'choice_immutable'; END IF;
      IF actor IS NULL OR actor='00000000-0000-0000-0000-000000000000' THEN RAISE EXCEPTION 'configuration_actor_required'; END IF;
      IF TG_OP='INSERT' THEN
        NEW.created_by:=actor;NEW.created_at:=statement_timestamp();NEW.revision:=1;
      ELSE
        IF (NEW.id,NEW.org_id,NEW.code,NEW.created_by,NEW.created_at) IS DISTINCT FROM (OLD.id,OLD.org_id,OLD.code,OLD.created_by,OLD.created_at) OR OLD.archived_at IS NOT NULL THEN RAISE EXCEPTION 'choice_immutable'; END IF;
        IF OLD.choice_version_id IS NULL AND NEW.choice_version_id IS NOT NULL AND OLD.created_at=statement_timestamp() AND OLD.revision=1 THEN NEW.revision:=1; ELSE NEW.revision:=OLD.revision+1; END IF;
      END IF;
      NEW.updated_by:=actor;NEW.updated_at:=statement_timestamp();RETURN NEW;
    END $$;
    CREATE FUNCTION leave.stamp_choice_version() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,leave AS $$
    DECLARE actor uuid:=leave.context_scope('app.actor_id');
    BEGIN
      IF TG_OP='DELETE' OR TG_OP='UPDATE' AND OLD.published_at IS NOT NULL THEN RAISE EXCEPTION 'published_choice_immutable'; END IF;
      IF actor IS NULL OR actor='00000000-0000-0000-0000-000000000000' THEN RAISE EXCEPTION 'configuration_actor_required'; END IF;
      IF cardinality(NEW.permitted_modes)<>(SELECT count(DISTINCT x) FROM unnest(NEW.permitted_modes) x) THEN RAISE EXCEPTION 'choice_modes_invalid' USING ERRCODE='23514'; END IF;
      IF TG_OP='INSERT' THEN NEW.created_by:=actor;NEW.created_at:=statement_timestamp();
      ELSIF (NEW.id,NEW.org_id,NEW.leave_type_id,NEW.version_number,NEW.created_by,NEW.created_at) IS DISTINCT FROM (OLD.id,OLD.org_id,OLD.leave_type_id,OLD.version_number,OLD.created_by,OLD.created_at) THEN RAISE EXCEPTION 'choice_immutable'; END IF;
      IF NEW.published_at IS NOT NULL THEN NEW.published_at:=statement_timestamp(); END IF;
      RETURN NEW;
    END $$;
    CREATE FUNCTION leave.check_choice_pointer() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,leave AS $$
    BEGIN
      IF NEW.choice_version_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM leave.leave_type_version WHERE org_id=NEW.org_id AND leave_type_id=NEW.id AND id=NEW.choice_version_id AND published_at IS NOT NULL) THEN RAISE EXCEPTION 'choice_not_published' USING ERRCODE='23514'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER stamp_choice_type BEFORE INSERT OR UPDATE OR DELETE ON leave.leave_type FOR EACH ROW EXECUTE FUNCTION leave.stamp_choice_type();
    CREATE TRIGGER stamp_choice_version BEFORE INSERT OR UPDATE OR DELETE ON leave.leave_type_version FOR EACH ROW EXECUTE FUNCTION leave.stamp_choice_version();
    CREATE TRIGGER check_choice_pointer BEFORE INSERT OR UPDATE ON leave.leave_type FOR EACH ROW EXECUTE FUNCTION leave.check_choice_pointer();
    CREATE TABLE leave.operator_principal (
      login_name text PRIMARY KEY,executor_actor_id uuid NOT NULL CHECK(executor_actor_id<>'00000000-0000-0000-0000-000000000000'),
      enabled boolean NOT NULL DEFAULT true
    );
    CREATE TABLE leave.operator_authority (
      login_name text NOT NULL REFERENCES leave.operator_principal(login_name),
      command text NOT NULL CHECK(command IN ('leave_type.create','leave_type.archive')),
      org_id uuid NOT NULL CHECK(org_id<>'00000000-0000-0000-0000-000000000000'),
      type_id uuid CHECK(type_id<>'00000000-0000-0000-0000-000000000000'),
      UNIQUE NULLS NOT DISTINCT(login_name,command,org_id,type_id)
    );
    CREATE TABLE leave.configuration_change (
      event_id uuid PRIMARY KEY,event_type text NOT NULL CHECK(event_type IN ('leave_type.created','leave_type.archived')),event_version integer NOT NULL CHECK(event_version=1),
      org_id uuid NOT NULL,type_id uuid NOT NULL,version_id uuid,revision bigint NOT NULL CHECK(revision>0),
      executor_actor_id uuid NOT NULL,operation_id uuid NOT NULL,reason_code text NOT NULL,evidence_ref text,
      created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
      FOREIGN KEY(org_id,type_id) REFERENCES leave.leave_type(org_id,id),
      UNIQUE(executor_actor_id,operation_id)
    );
    CREATE TABLE leave.operation_outcome (
      executor_actor_id uuid NOT NULL,operation_id uuid NOT NULL,command text NOT NULL CHECK(command IN ('leave_type.create','leave_type.archive')),
      command_version integer NOT NULL CHECK(command_version=1),org_id uuid NOT NULL,type_id uuid NOT NULL,
      fingerprint_version text NOT NULL CHECK(fingerprint_version='sha256-jcs-v1'),fingerprint bytea NOT NULL CHECK(octet_length(fingerprint)=32),
      result_version integer NOT NULL CHECK(result_version=1),result jsonb NOT NULL CHECK(jsonb_typeof(result)='object'),
      created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
      PRIMARY KEY(executor_actor_id,operation_id),FOREIGN KEY(org_id,type_id) REFERENCES leave.leave_type(org_id,id)
    );
    CREATE FUNCTION leave.immutable_configuration_evidence() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$ BEGIN RAISE EXCEPTION 'configuration_evidence_immutable'; END $$;
    CREATE TRIGGER immutable_configuration_change BEFORE UPDATE OR DELETE ON leave.configuration_change FOR EACH ROW EXECUTE FUNCTION leave.immutable_configuration_evidence();
    CREATE TRIGGER immutable_configuration_outcome BEFORE UPDATE OR DELETE ON leave.operation_outcome FOR EACH ROW EXECUTE FUNCTION leave.immutable_configuration_evidence();
    ''')
    for table in ('leave_type','leave_type_version','configuration_change','operation_outcome','operator_principal','operator_authority'):
        op.execute(f'''ALTER TABLE leave.{table} ENABLE ROW LEVEL SECURITY;
        ALTER TABLE leave.{table} FORCE ROW LEVEL SECURITY;
        CREATE POLICY command_owner ON leave.{table} TO leave_command_owner USING(true) WITH CHECK(true);''')
    for table in ('leave_type','leave_type_version'):
        op.execute(f'''CREATE POLICY choice_read ON leave.{table} FOR SELECT TO leave_runtime USING(org_id=leave.context_scope('app.org_id') AND current_setting('app.mode',true)='own_read');
        GRANT SELECT ON leave.{table} TO leave_runtime;''')
    op.execute(r'''
    GRANT USAGE ON SCHEMA leave TO leave_command_owner,leave_operator;
    GRANT EXECUTE ON FUNCTION leave.context_scope(text) TO leave_command_owner;
    GRANT SELECT ON leave.operator_principal,leave.operator_authority TO leave_command_owner;
    GRANT SELECT,INSERT,UPDATE ON leave.leave_type,leave.leave_type_version TO leave_command_owner;
    GRANT SELECT,INSERT ON leave.configuration_change,leave.operation_outcome TO leave_command_owner;
    CREATE FUNCTION leave.command_executor(cmd text,organization uuid,target uuid) RETURNS uuid LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,leave AS $$
    DECLARE actor uuid;
    BEGIN
      SELECT p.executor_actor_id INTO actor FROM leave.operator_principal p WHERE p.login_name=session_user AND p.enabled AND EXISTS(SELECT 1 FROM leave.operator_authority a WHERE a.login_name=p.login_name AND a.command=cmd AND a.org_id=organization AND (a.type_id IS NULL OR a.type_id=target));
      IF actor IS NULL THEN RAISE EXCEPTION 'access_denied' USING ERRCODE='42501'; END IF;
      RETURN actor;
    END $$;
    -- Exact JCS subset for this closed schema: ASCII property names, integer 1,
    -- booleans/null, Unicode scalar strings and arrays. No floating-point input.
    CREATE FUNCTION leave.canonical_configuration(value jsonb) RETURNS text LANGUAGE plpgsql IMMUTABLE SET search_path=pg_catalog,leave AS $$
    DECLARE result text;
    BEGIN
      IF jsonb_typeof(value)='object' THEN SELECT '{'||coalesce(string_agg(to_jsonb(key)::text||':'||leave.canonical_configuration(val),',' ORDER BY key COLLATE "C"),'')||'}' INTO result FROM jsonb_each(value) AS item(key,val);
      ELSIF jsonb_typeof(value)='array' THEN SELECT '['||coalesce(string_agg(leave.canonical_configuration(val),',' ORDER BY ord),'')||']' INTO result FROM jsonb_array_elements(value) WITH ORDINALITY AS item(val,ord);
      ELSE result:=value::text; END IF;
      RETURN result;
    END $$;
    CREATE FUNCTION leave.command_outcome(cmd text,organization uuid,target uuid,operation uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,leave AS $$
    DECLARE actor uuid;saved leave.operation_outcome;
    BEGIN
      IF current_setting('transaction_isolation') IS DISTINCT FROM 'read committed' THEN RAISE EXCEPTION 'command_invalid' USING ERRCODE='22023'; END IF;
      actor:=leave.command_executor(cmd,organization,target);
      SELECT * INTO saved FROM leave.operation_outcome WHERE executor_actor_id=actor AND operation_id=operation;
      IF NOT FOUND THEN RETURN jsonb_build_object('operation_id',operation,'status','unresolved'); END IF;
      IF saved.command<>cmd OR saved.org_id<>organization OR saved.type_id<>target OR saved.command_version<>1 OR saved.result_version<>1 OR saved.fingerprint_version<>'sha256-jcs-v1' THEN RAISE EXCEPTION 'operation_payload_mismatch' USING ERRCODE='P0003'; END IF;
      RETURN saved.result;
    END $$;
    CREATE FUNCTION leave.execute_command(document jsonb,canonical_bytes bytea) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,leave AS $$
    DECLARE cmd text;organization uuid;target uuid;version uuid;operation uuid;actor uuid;stamp timestamptz:=statement_timestamp();event uuid:=gen_random_uuid();fingerprint bytea;previous leave.operation_outcome;current_type leave.leave_type;p jsonb;keys text[];mode_values text[];result jsonb;rev bigint;reason text;evidence text;
    BEGIN
      IF current_setting('transaction_isolation') IS DISTINCT FROM 'read committed' THEN RAISE EXCEPTION 'command_invalid' USING ERRCODE='22023'; END IF;
      IF jsonb_typeof(document)<>'object' OR (SELECT array_agg(key ORDER BY key) FROM jsonb_object_keys(document) key)<>ARRAY['command','evidence_ref','operation_id','payload','reason_code','schema_version','scope'] OR (document->'schema_version')::text IS DISTINCT FROM '1' OR jsonb_typeof(document->'operation_id')<>'string' OR jsonb_typeof(document->'command')<>'string' OR jsonb_typeof(document->'reason_code')<>'string' THEN RAISE EXCEPTION 'command_invalid' USING ERRCODE='22023'; END IF;
      cmd:=document->>'command';operation:=(document->>'operation_id')::uuid;reason:=document->>'reason_code';evidence:=document->>'evidence_ref';
      IF cmd NOT IN ('leave_type.create','leave_type.archive') OR operation='00000000-0000-0000-0000-000000000000' OR operation::text<>document->>'operation_id' OR reason NOT IN ('initial_setup','synthetic_fixture','identity_adoption','access_change','setup_correction') OR NOT(document->'evidence_ref'='null'::jsonb OR jsonb_typeof(document->'evidence_ref')='string' AND length(evidence)<=256 AND evidence COLLATE "C" ~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]*$' AND position('://' IN evidence)=0) THEN RAISE EXCEPTION 'command_invalid' USING ERRCODE='22023'; END IF;
      IF jsonb_typeof(document->'scope')<>'object' OR (SELECT array_agg(key ORDER BY key) FROM jsonb_object_keys(document->'scope') key)<>ARRAY['kind','org_id'] OR document->'scope'->'kind' IS DISTINCT FROM '"organization"'::jsonb OR jsonb_typeof(document->'scope'->'org_id')<>'string' THEN RAISE EXCEPTION 'command_invalid' USING ERRCODE='22023'; END IF;
      organization:=(document->'scope'->>'org_id')::uuid;p:=document->'payload';
      IF organization='00000000-0000-0000-0000-000000000000' OR organization::text<>document->'scope'->>'org_id' OR jsonb_typeof(p)<>'object' THEN RAISE EXCEPTION 'command_invalid' USING ERRCODE='22023'; END IF;
      SELECT array_agg(key ORDER BY key) INTO keys FROM jsonb_object_keys(p) key;
      IF jsonb_typeof(p->'type_id')<>'string' THEN RAISE EXCEPTION 'command_invalid' USING ERRCODE='22023'; END IF;
      target:=(p->>'type_id')::uuid;
      IF target='00000000-0000-0000-0000-000000000000' OR target::text<>p->>'type_id' THEN RAISE EXCEPTION 'command_invalid' USING ERRCODE='22023'; END IF;
      IF cmd='leave_type.create' THEN
        IF keys IS DISTINCT FROM ARRAY['code','effective_from','effective_to','expected_absent','name','permitted_modes','type_id','version_id'] OR p->'expected_absent'<>'true'::jsonb OR jsonb_typeof(p->'code')<>'string' OR jsonb_typeof(p->'name')<>'string' OR jsonb_typeof(p->'permitted_modes')<>'array' OR jsonb_typeof(p->'version_id')<>'string' OR jsonb_typeof(p->'effective_from')<>'string' OR NOT(p->'effective_to'='null'::jsonb OR jsonb_typeof(p->'effective_to')='string') THEN RAISE EXCEPTION 'command_invalid' USING ERRCODE='22023'; END IF;
        version:=(p->>'version_id')::uuid;
        IF version='00000000-0000-0000-0000-000000000000' OR version::text<>p->>'version_id' OR p->>'code' COLLATE "C" !~ '^[a-z][a-z0-9_]{0,63}$' OR length(p->>'name') NOT BETWEEN 1 AND 120 OR p->>'name'<>btrim(p->>'name',U&'\0009\000A\000B\000C\000D\001C\001D\001E\001F\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000') OR p->>'name' ~ '[[:cntrl:]]' OR p->>'effective_from'!~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' OR (p->>'effective_to' IS NOT NULL AND p->>'effective_to'!~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$') THEN RAISE EXCEPTION 'command_invalid' USING ERRCODE='22023'; END IF;
        IF EXISTS(SELECT 1 FROM jsonb_array_elements(p->'permitted_modes') x WHERE jsonb_typeof(x)<>'string') THEN RAISE EXCEPTION 'command_invalid' USING ERRCODE='22023'; END IF;
        SELECT array_agg(x) INTO mode_values FROM jsonb_array_elements_text(p->'permitted_modes') x;
        IF cardinality(mode_values) NOT BETWEEN 1 AND 3 OR mode_values IS NULL OR NOT(mode_values<@ARRAY['full_days','half_day','hours']::text[]) OR cardinality(mode_values)<>(SELECT count(DISTINCT x) FROM unnest(mode_values) x) THEN RAISE EXCEPTION 'command_invalid' USING ERRCODE='22023'; END IF;
      ELSE
        IF keys IS DISTINCT FROM ARRAY['expected_revision','type_id'] OR jsonb_typeof(p->'expected_revision')<>'string' OR p->>'expected_revision'!~ '^[1-9][0-9]{0,18}$' THEN RAISE EXCEPTION 'command_invalid' USING ERRCODE='22023'; END IF;
      END IF;
      IF canonical_bytes IS DISTINCT FROM convert_to(leave.canonical_configuration(document),'UTF8') THEN RAISE EXCEPTION 'command_invalid' USING ERRCODE='22023'; END IF;
      actor:=leave.command_executor(cmd,organization,target);
      PERFORM pg_advisory_xact_lock(hashtextextended(actor::text||':'||operation::text,0));
      -- Recheck authority after waiting before exposing a replay or changing state.
      IF leave.command_executor(cmd,organization,target) IS DISTINCT FROM actor THEN RAISE EXCEPTION 'access_denied' USING ERRCODE='42501'; END IF;
      fingerprint:=sha256(canonical_bytes);
      SELECT * INTO previous FROM leave.operation_outcome WHERE executor_actor_id=actor AND operation_id=operation;
      IF FOUND THEN
        IF previous.fingerprint<>fingerprint OR previous.command<>cmd OR previous.org_id<>organization OR previous.type_id<>target OR previous.command_version<>1 OR previous.result_version<>1 OR previous.fingerprint_version<>'sha256-jcs-v1' THEN RAISE EXCEPTION 'operation_payload_mismatch' USING ERRCODE='P0003'; END IF;
        RETURN previous.result;
      END IF;
      PERFORM set_config('app.actor_id',actor::text,true);
      IF cmd='leave_type.create' THEN
        INSERT INTO leave.leave_type(id,org_id,code,revision,created_by,created_at,updated_by,updated_at) VALUES(target,organization,p->>'code',1,actor,stamp,actor,stamp);
        INSERT INTO leave.leave_type_version(id,org_id,leave_type_id,version_number,name,permitted_modes,effective_from,effective_to,published_at,created_by,created_at) VALUES(version,organization,target,1,p->>'name',mode_values,(p->>'effective_from')::date,(p->>'effective_to')::date,stamp,actor,stamp);
        UPDATE leave.leave_type SET choice_version_id=version WHERE org_id=organization AND id=target RETURNING revision INTO rev;
      ELSE
        SELECT * INTO current_type FROM leave.leave_type WHERE org_id=organization AND id=target FOR UPDATE;
        IF leave.command_executor(cmd,organization,target) IS DISTINCT FROM actor THEN RAISE EXCEPTION 'access_denied' USING ERRCODE='42501'; END IF;
        IF NOT FOUND OR current_type.revision<>(p->>'expected_revision')::bigint OR current_type.archived_at IS NOT NULL THEN RAISE EXCEPTION 'operation_conflict' USING ERRCODE='P0002'; END IF;
        version:=current_type.choice_version_id;
        UPDATE leave.leave_type SET archived_at=stamp WHERE org_id=organization AND id=target RETURNING revision INTO rev;
      END IF;
      INSERT INTO leave.configuration_change(event_id,event_type,event_version,org_id,type_id,version_id,revision,executor_actor_id,operation_id,reason_code,evidence_ref) VALUES(event,CASE WHEN cmd='leave_type.create' THEN 'leave_type.created' ELSE 'leave_type.archived' END,1,organization,target,version,rev,actor,operation,reason,evidence);
      result:=jsonb_build_object('operation_id',operation,'status','committed','command_version',1,'result_version',1,'committed_at',stamp,'result',jsonb_build_object('command',cmd,'target',CASE WHEN cmd='leave_type.create' THEN jsonb_build_object('org_id',organization,'type_id',target,'version_id',version) ELSE jsonb_build_object('org_id',organization,'type_id',target) END,'disposition',CASE WHEN cmd='leave_type.create' THEN 'created' ELSE 'changed' END,'revision',rev::text,'event_id',event));
      INSERT INTO leave.operation_outcome(executor_actor_id,operation_id,command,command_version,org_id,type_id,fingerprint_version,fingerprint,result_version,result) VALUES(actor,operation,cmd,1,organization,target,'sha256-jcs-v1',fingerprint,1,result);
      RETURN result;
    END $$;
    REVOKE ALL ON FUNCTION leave.stamp_choice_type(),leave.stamp_choice_version(),leave.check_choice_pointer(),leave.immutable_configuration_evidence(),leave.canonical_configuration(jsonb),leave.command_executor(text,uuid,uuid),leave.command_outcome(text,uuid,uuid,uuid),leave.execute_command(jsonb,bytea) FROM PUBLIC;
    GRANT EXECUTE ON FUNCTION leave.canonical_configuration(jsonb) TO leave_command_owner;
    GRANT EXECUTE ON FUNCTION leave.command_outcome(text,uuid,uuid,uuid),leave.execute_command(jsonb,bytea) TO leave_operator;
    ALTER FUNCTION leave.command_executor(text,uuid,uuid) OWNER TO leave_command_owner;
    ALTER FUNCTION leave.command_outcome(text,uuid,uuid,uuid) OWNER TO leave_command_owner;
    ALTER FUNCTION leave.execute_command(jsonb,bytea) OWNER TO leave_command_owner;
    ''')

def downgrade():raise RuntimeError('forward_recovery_required')
