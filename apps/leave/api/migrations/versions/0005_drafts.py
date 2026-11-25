"""D1 application-owned drafts and retained compact command evidence."""
from alembic import op
revision='0005_drafts'
down_revision='0004_draft_choices'
branch_labels=None
depends_on=None

def upgrade():
    op.execute('''
    CREATE FUNCTION leave.draft_input_valid(v jsonb) RETURNS boolean LANGUAGE plpgsql IMMUTABLE AS $$
    DECLARE entry jsonb; path text[];
    BEGIN
      IF v IS NULL OR jsonb_typeof(v) IS DISTINCT FROM 'object' OR (SELECT array_agg(k ORDER BY k) FROM jsonb_object_keys(v) k) IS DISTINCT FROM ARRAY['duration_mode','full_days','half_day','hours','input_version','leave_type_id','note'] THEN RETURN false; END IF;
      IF v->'input_version' IS DISTINCT FROM '1'::jsonb OR NOT(v->'duration_mode'='null'::jsonb OR v->>'duration_mode' IN ('full_days','half_day','hours')) THEN RETURN false; END IF;
      IF NOT(v->'leave_type_id'='null'::jsonb OR (jsonb_typeof(v->'leave_type_id')='string' AND v->>'leave_type_id' ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' AND v->>'leave_type_id'<>'00000000-0000-0000-0000-000000000000')) THEN RETURN false; END IF;
      IF jsonb_typeof(v->'note') IS DISTINCT FROM 'string' OR length(v->>'note')>4000 THEN RETURN false; END IF;
      IF jsonb_typeof(v->'full_days') IS DISTINCT FROM 'object' OR (SELECT array_agg(k ORDER BY k) FROM jsonb_object_keys(v->'full_days') k) IS DISTINCT FROM ARRAY['end','start'] OR jsonb_typeof(v->'half_day') IS DISTINCT FROM 'object' OR (SELECT array_agg(k) FROM jsonb_object_keys(v->'half_day') k) IS DISTINCT FROM ARRAY['date'] OR jsonb_typeof(v->'hours') IS DISTINCT FROM 'object' OR (SELECT array_agg(k ORDER BY k) FROM jsonb_object_keys(v->'hours') k) IS DISTINCT FROM ARRAY['date','duration'] THEN RETURN false; END IF;
      FOREACH path SLICE 1 IN ARRAY ARRAY[['full_days','start'],['full_days','end'],['half_day','date'],['hours','date'],['hours','duration']] LOOP
        entry:=v#>path;
        IF jsonb_typeof(entry) IS DISTINCT FROM 'object' OR (SELECT array_agg(k ORDER BY k) FROM jsonb_object_keys(entry) k) IS DISTINCT FROM ARRAY['format','text'] OR jsonb_typeof(entry->'text') IS DISTINCT FROM 'string' OR length(entry->>'text')>(CASE WHEN path[2]='duration' THEN 32 ELSE 64 END) OR entry->>'format' IS DISTINCT FROM (CASE WHEN path[2]='duration' THEN 'decimal_hours_dot_v1' ELSE 'dmy_numeric_v1' END) THEN RETURN false; END IF;
      END LOOP;
      RETURN true;
    EXCEPTION WHEN OTHERS THEN RETURN false; END $$;
    CREATE FUNCTION leave.draft_receipt_result_valid(v jsonb,kind text,target uuid,rev bigint) RETURNS boolean LANGUAGE plpgsql IMMUTABLE AS $$
    BEGIN
      RETURN (jsonb_typeof(v)='object' AND (SELECT array_agg(k ORDER BY k) FROM jsonb_object_keys(v) k)=ARRAY['command','disposition','draft_id','revision','scope_generation'] AND v->>'command'=kind AND v->>'draft_id'=target::text AND jsonb_typeof(v->'revision')='string' AND v->>'revision'=rev::text AND jsonb_typeof(v->'scope_generation')='string' AND v->>'scope_generation' ~ '^(0|[1-9][0-9]{0,18})$' AND (v->>'scope_generation')::bigint>=0 AND ((kind='start' AND v->>'disposition' IN ('created','resumed')) OR (kind='save' AND v->>'disposition'='saved') OR (kind='discard' AND v->>'disposition'='discarded'))) IS TRUE;
    EXCEPTION WHEN OTHERS THEN RETURN false; END $$;
    CREATE FUNCTION leave.draft_observation_valid(v jsonb,org uuid,employment uuid) RETURNS boolean LANGUAGE plpgsql IMMUTABLE AS $$
    DECLARE kind text:=v->>'kind';keys text[];name text;
    BEGIN
      IF jsonb_typeof(v) IS DISTINCT FROM 'object' OR kind IS NULL OR kind NOT IN ('discovery','effective') THEN RETURN false; END IF;
      keys:=ARRAY['account_id','checked_at','decision_id','employment_id','kind','membership_id','observed_at','org_id','person_id','revision'];
      keys:=keys||(CASE WHEN kind='discovery' THEN ARRAY['has_periods'] ELSE ARRAY['as_of_date','employment_state','period','timezone'] END);
      IF (SELECT array_agg(k ORDER BY k) FROM jsonb_object_keys(v) k) IS DISTINCT FROM (SELECT array_agg(k ORDER BY k) FROM unnest(keys) k) THEN RETURN false; END IF;
      IF v->>'org_id' IS DISTINCT FROM org::text OR v->>'employment_id' IS DISTINCT FROM employment::text THEN RETURN false; END IF;
      FOREACH name IN ARRAY ARRAY['account_id','decision_id','person_id'] LOOP
        IF jsonb_typeof(v->name) IS DISTINCT FROM 'string' OR (v->>name)::uuid='00000000-0000-0000-0000-000000000000' THEN RETURN false; END IF;
      END LOOP;
      FOREACH name IN ARRAY ARRAY['revision','membership_id'] LOOP
        IF jsonb_typeof(v->name) IS DISTINCT FROM 'string' OR NOT(v->>name ~ '^[1-9][0-9]{0,18}$') OR (v->>name)::bigint<1 THEN RETURN false; END IF;
      END LOOP;
      FOREACH name IN ARRAY ARRAY['observed_at','checked_at'] LOOP
        IF jsonb_typeof(v->name) IS DISTINCT FROM 'string' OR NOT isfinite((v->>name)::timestamptz) THEN RETURN false; END IF;
      END LOOP;
      IF kind='discovery' THEN RETURN jsonb_typeof(v->'has_periods')='boolean'; END IF;
      RETURN (jsonb_typeof(v->'as_of_date')='string' AND v->>'as_of_date' ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' AND isfinite((v->>'as_of_date')::date) AND v->>'employment_state' IN ('current','future','ended','setup_required') AND jsonb_typeof(v->'timezone')='object' AND (jsonb_typeof(v->'period')='object' OR (v->>'employment_state'='setup_required' AND v->'period'='null'::jsonb))) IS TRUE;
    EXCEPTION WHEN OTHERS THEN RETURN false; END $$;
    CREATE TABLE leave.draft_scope(
      org_id uuid NOT NULL CHECK(org_id<>'00000000-0000-0000-0000-000000000000'),
      employment_id uuid NOT NULL CHECK(employment_id<>'00000000-0000-0000-0000-000000000000'),
      generation bigint NOT NULL CHECK(generation>=0),
      created_by uuid NOT NULL,created_at timestamptz NOT NULL,
      updated_by uuid NOT NULL,updated_at timestamptz NOT NULL,
      PRIMARY KEY(org_id,employment_id));
    CREATE TABLE leave.draft(
      id uuid PRIMARY KEY CHECK(id<>'00000000-0000-0000-0000-000000000000'),
      org_id uuid NOT NULL,employment_id uuid NOT NULL,
      revision bigint NOT NULL CHECK(revision>0),state text NOT NULL CHECK(state IN ('active','discarded')),
      input jsonb,created_by uuid NOT NULL,created_at timestamptz NOT NULL,
      updated_by uuid NOT NULL,updated_at timestamptz NOT NULL,discarded_by uuid,discarded_at timestamptz,
      FOREIGN KEY(org_id,employment_id) REFERENCES leave.draft_scope ON DELETE RESTRICT,
      UNIQUE(org_id,employment_id,id),
      CONSTRAINT draft_payload_state CHECK((state='active' AND input IS NOT NULL AND leave.draft_input_valid(input) IS TRUE AND discarded_by IS NULL AND discarded_at IS NULL) OR (state='discarded' AND input IS NULL AND discarded_by IS NOT NULL AND discarded_at IS NOT NULL)));
    CREATE UNIQUE INDEX draft_one_active ON leave.draft(org_id,employment_id) WHERE state='active';
    CREATE TABLE leave.operation_receipt(
      org_id uuid NOT NULL,actor_id uuid NOT NULL,operation_id uuid NOT NULL,
      employment_id uuid NOT NULL,draft_id uuid NOT NULL,
      command text NOT NULL CHECK(command IN ('start','save','discard')),
      command_version integer NOT NULL CHECK(command_version>0),
      fingerprint_algorithm text NOT NULL,fingerprint_version integer NOT NULL CHECK(fingerprint_version>0),
      fingerprint bytea NOT NULL CHECK(octet_length(fingerprint)=32),
      committed_revision bigint NOT NULL CHECK(committed_revision>0),result jsonb NOT NULL CONSTRAINT operation_receipt_result_shape CHECK(leave.draft_receipt_result_valid(result,command,draft_id,committed_revision) IS TRUE),
      observation jsonb NOT NULL CONSTRAINT operation_receipt_observation_shape CHECK(leave.draft_observation_valid(observation,org_id,employment_id) IS TRUE),
      created_by uuid NOT NULL,created_at timestamptz NOT NULL,
      PRIMARY KEY(org_id,actor_id,operation_id),
      FOREIGN KEY(org_id,employment_id,draft_id) REFERENCES leave.draft(org_id,employment_id,id) ON DELETE RESTRICT);
    CREATE FUNCTION leave.stamp_draft() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE actor uuid:=leave.context_scope('app.actor_id');
    BEGIN
      IF actor IS NULL OR actor='00000000-0000-0000-0000-000000000000' THEN RAISE EXCEPTION 'draft_actor_required'; END IF;
      IF TG_OP='DELETE' THEN RAISE EXCEPTION 'draft_evidence_retained'; END IF;
      IF TG_OP='INSERT' THEN
        IF TG_TABLE_NAME='draft_scope' THEN IF NEW.generation<>0 THEN RAISE EXCEPTION 'scope_initial_generation'; END IF; END IF;
        IF TG_TABLE_NAME='draft' THEN IF NEW.revision<>1 OR NEW.state<>'active' THEN RAISE EXCEPTION 'draft_initial_state'; END IF; END IF;
        NEW.created_by:=actor;NEW.created_at:=statement_timestamp();
      ELSE
        IF NEW.org_id<>OLD.org_id OR NEW.employment_id<>OLD.employment_id OR NEW.created_by<>OLD.created_by OR NEW.created_at<>OLD.created_at THEN RAISE EXCEPTION 'draft_immutable'; END IF;
        IF TG_TABLE_NAME='operation_receipt' THEN RAISE EXCEPTION 'receipt_immutable'; END IF;
        IF TG_TABLE_NAME='draft' THEN
          IF NEW.id<>OLD.id OR OLD.state<>'active' OR NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'draft_lifecycle_revision'; END IF;
          IF NEW.state='discarded' THEN NEW.discarded_by:=actor;NEW.discarded_at:=statement_timestamp(); END IF;
        ELSIF NEW.generation<>OLD.generation+1 THEN RAISE EXCEPTION 'scope_generation'; END IF;
      END IF;
      IF TG_TABLE_NAME='operation_receipt' THEN
        IF NEW.actor_id<>actor THEN RAISE EXCEPTION 'receipt_actor'; END IF;
      ELSE NEW.updated_by:=actor;NEW.updated_at:=statement_timestamp(); END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER stamp_scope BEFORE INSERT OR UPDATE OR DELETE ON leave.draft_scope FOR EACH ROW EXECUTE FUNCTION leave.stamp_draft();
    CREATE TRIGGER stamp_draft BEFORE INSERT OR UPDATE OR DELETE ON leave.draft FOR EACH ROW EXECUTE FUNCTION leave.stamp_draft();
    CREATE TRIGGER stamp_receipt BEFORE INSERT OR UPDATE OR DELETE ON leave.operation_receipt FOR EACH ROW EXECUTE FUNCTION leave.stamp_draft();
    -- A config writer obtains the configuration guard before touching rows. Dated
    -- D1 writes hold the shared guard and compare their source/date until commit.
    CREATE FUNCTION leave.guard_timezone_configuration() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      PERFORM pg_advisory_xact_lock(hashtextextended('leave.timezone.configuration',0));RETURN NULL;
    END $$;
    REVOKE ALL ON FUNCTION leave.draft_input_valid(jsonb),leave.draft_receipt_result_valid(jsonb,text,uuid,bigint),leave.draft_observation_valid(jsonb,uuid,uuid),leave.stamp_draft(),leave.guard_timezone_configuration() FROM PUBLIC;
    GRANT EXECUTE ON FUNCTION leave.draft_input_valid(jsonb),leave.draft_receipt_result_valid(jsonb,text,uuid,bigint),leave.draft_observation_valid(jsonb,uuid,uuid) TO leave_runtime;
    ''')
    for table in ('work_profile','organization_settings','work_profile_version','employment_settings'):
        op.execute(f'CREATE TRIGGER guard_draft_timezone BEFORE INSERT OR UPDATE OR DELETE ON leave.{table} FOR EACH STATEMENT EXECUTE FUNCTION leave.guard_timezone_configuration()')
        employment=" AND employment_id=leave.context_scope('app.employment_id')" if table=='employment_settings' else ''
        # The protected D1 transaction uses own_write. Its source guard needs
        # the same bounded reads as preparation; no configuration writes/grants.
        op.execute(f"""CREATE POLICY draft_timezone_read ON leave.{table} FOR SELECT TO leave_runtime USING(
          org_id=leave.context_scope('app.org_id') AND current_setting('app.mode',true)='own_write'{employment});""")
    for table in ('draft_scope','draft','operation_receipt'):
        read_scope="actor_id=leave.context_scope('app.actor_id')" if table=='operation_receipt' else "employment_id=leave.context_scope('app.employment_id')"
        op.execute(f'''ALTER TABLE leave.{table} ENABLE ROW LEVEL SECURITY;ALTER TABLE leave.{table} FORCE ROW LEVEL SECURITY;
          CREATE POLICY draft_read ON leave.{table} FOR SELECT TO leave_runtime USING(org_id=leave.context_scope('app.org_id') AND {read_scope} AND current_setting('app.mode',true) IN ('own_read','own_write'));
          CREATE POLICY draft_insert ON leave.{table} FOR INSERT TO leave_runtime WITH CHECK(org_id=leave.context_scope('app.org_id') AND employment_id=leave.context_scope('app.employment_id') AND current_setting('app.mode',true)='own_write');
          GRANT SELECT,INSERT ON leave.{table} TO leave_runtime;''')
        if table!='operation_receipt':
            op.execute(f'''CREATE POLICY draft_update ON leave.{table} FOR UPDATE TO leave_runtime USING(org_id=leave.context_scope('app.org_id') AND employment_id=leave.context_scope('app.employment_id') AND current_setting('app.mode',true)='own_write') WITH CHECK(org_id=leave.context_scope('app.org_id') AND employment_id=leave.context_scope('app.employment_id') AND current_setting('app.mode',true)='own_write');GRANT UPDATE ON leave.{table} TO leave_runtime;''')

def downgrade():raise RuntimeError('forward_recovery_required')
