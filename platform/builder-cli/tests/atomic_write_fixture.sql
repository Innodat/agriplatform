-- Synthetic test-only schema; applied once to an exclusive fresh database.
CREATE SCHEMA sample;
REVOKE ALL ON SCHEMA sample FROM PUBLIC;
CREATE TABLE sample.actor(id uuid PRIMARY KEY CHECK(id <> '00000000-0000-0000-0000-000000000000'));
CREATE TABLE sample.record(
 id uuid PRIMARY KEY CHECK(id <> '00000000-0000-0000-0000-000000000000'),
 org_id uuid NOT NULL CHECK(org_id <> '00000000-0000-0000-0000-000000000000'),
 owner_account_id uuid NOT NULL CHECK(owner_account_id <> '00000000-0000-0000-0000-000000000000'),
 value integer NOT NULL, revision bigint NOT NULL CHECK(revision>0),
 created_by uuid NOT NULL REFERENCES sample.actor(id), updated_by uuid NOT NULL REFERENCES sample.actor(id),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(), updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 UNIQUE(org_id,id,owner_account_id));
CREATE TABLE sample.outcome(
 id uuid PRIMARY KEY CHECK(id <> '00000000-0000-0000-0000-000000000000'), org_id uuid NOT NULL,
 executor_account_id uuid NOT NULL CHECK(executor_account_id <> '00000000-0000-0000-0000-000000000000'),
 executor_actor_id uuid NOT NULL REFERENCES sample.actor(id),
 command_type text NOT NULL CHECK(command_type IN ('record.edit','record.adjust')),
 operation_id uuid NOT NULL CHECK(operation_id <> '00000000-0000-0000-0000-000000000000'),
 command_version integer NOT NULL CHECK(command_version>0),
 fingerprint_version integer NOT NULL CHECK(fingerprint_version>0),
 fingerprint_algorithm text NOT NULL CHECK(fingerprint_algorithm IN ('sha256','hmac-sha256')),
 fingerprint_key_id text,
 fingerprint bytea NOT NULL CHECK(octet_length(fingerprint)=32),
 result_version integer NOT NULL CHECK(result_version>0), result jsonb NOT NULL CHECK(jsonb_typeof(result)='object' AND octet_length(result::text)<=8192),
 target_id uuid NOT NULL, committed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 CHECK((fingerprint_algorithm='hmac-sha256' AND fingerprint_key_id IS NOT NULL AND fingerprint_key_id ~ '^[A-Za-z0-9_-]{1,64}$') OR (fingerprint_algorithm='sha256' AND fingerprint_key_id IS NULL)),
 UNIQUE(org_id,executor_account_id,command_type,operation_id),
 UNIQUE(id,org_id,executor_account_id,executor_actor_id,command_type,operation_id,target_id),
 FOREIGN KEY(org_id,target_id,executor_account_id) REFERENCES sample.record(org_id,id,owner_account_id));
CREATE TABLE sample.revision(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), org_id uuid NOT NULL, record_id uuid NOT NULL,
 owner_account_id uuid NOT NULL, revision bigint NOT NULL CHECK(revision>0), value integer NOT NULL,
 executor_account_id uuid NOT NULL, executor_actor_id uuid NOT NULL REFERENCES sample.actor(id),
 command_type text NOT NULL, operation_id uuid NOT NULL, outcome_id uuid NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 UNIQUE(org_id,record_id,revision), UNIQUE(outcome_id),
 FOREIGN KEY(org_id,record_id,owner_account_id) REFERENCES sample.record(org_id,id,owner_account_id),
 FOREIGN KEY(outcome_id,org_id,executor_account_id,executor_actor_id,command_type,operation_id,record_id)
 REFERENCES sample.outcome(id,org_id,executor_account_id,executor_actor_id,command_type,operation_id,target_id));
CREATE FUNCTION sample.immutable() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION USING ERRCODE='55000', MESSAGE='immutable_record'; END $$;
CREATE TRIGGER immutable_outcome BEFORE UPDATE OR DELETE OR TRUNCATE ON sample.outcome FOR EACH STATEMENT EXECUTE FUNCTION sample.immutable();
CREATE TRIGGER immutable_revision BEFORE UPDATE OR DELETE OR TRUNCATE ON sample.revision FOR EACH STATEMENT EXECUTE FUNCTION sample.immutable();
CREATE FUNCTION sample.fixed_owner() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF (NEW.org_id,NEW.owner_account_id,NEW.id,NEW.created_by,NEW.created_at) IS DISTINCT FROM (OLD.org_id,OLD.owner_account_id,OLD.id,OLD.created_by,OLD.created_at)
 THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='immutable_record_owner'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER fixed_owner BEFORE UPDATE ON sample.record FOR EACH ROW EXECUTE FUNCTION sample.fixed_owner();
ALTER TABLE sample.record ENABLE ROW LEVEL SECURITY; ALTER TABLE sample.record FORCE ROW LEVEL SECURITY;
ALTER TABLE sample.outcome ENABLE ROW LEVEL SECURITY; ALTER TABLE sample.outcome FORCE ROW LEVEL SECURITY;
ALTER TABLE sample.revision ENABLE ROW LEVEL SECURITY; ALTER TABLE sample.revision FORCE ROW LEVEL SECURITY;
CREATE POLICY record_read ON sample.record FOR SELECT USING (
 org_id::text=current_setting('app.org_id',true) AND
 (current_setting('app.mode',true) IN ('all_read','all_write') OR
 (current_setting('app.mode',true) IN ('own_read','own_write') AND owner_account_id::text=current_setting('app.account_id',true))));
CREATE POLICY record_insert ON sample.record FOR INSERT WITH CHECK (
 org_id::text=current_setting('app.org_id',true) AND owner_account_id::text=current_setting('app.account_id',true)
 AND current_setting('app.mode',true)='own_write' AND created_by::text=current_setting('app.actor_id',true) AND updated_by=created_by);
CREATE POLICY record_update ON sample.record FOR UPDATE USING (
 org_id::text=current_setting('app.org_id',true) AND owner_account_id::text=current_setting('app.account_id',true) AND current_setting('app.mode',true)='own_write')
 WITH CHECK(updated_by::text=current_setting('app.actor_id',true));
CREATE POLICY outcome_read ON sample.outcome FOR SELECT USING (
 org_id::text=current_setting('app.org_id',true) AND executor_account_id::text=current_setting('app.account_id',true)
 AND current_setting('app.mode',true) IN ('own_read','own_write'));
CREATE POLICY outcome_insert ON sample.outcome FOR INSERT WITH CHECK (
 org_id::text=current_setting('app.org_id',true) AND executor_account_id::text=current_setting('app.account_id',true)
 AND executor_actor_id::text=current_setting('app.actor_id',true) AND current_setting('app.mode',true)='own_write');
CREATE POLICY revision_read ON sample.revision FOR SELECT USING (
 org_id::text=current_setting('app.org_id',true) AND owner_account_id::text=current_setting('app.account_id',true)
 AND current_setting('app.mode',true) IN ('own_read','own_write'));
CREATE POLICY revision_insert ON sample.revision FOR INSERT WITH CHECK (
 org_id::text=current_setting('app.org_id',true) AND owner_account_id::text=current_setting('app.account_id',true)
 AND executor_account_id::text=current_setting('app.account_id',true)
 AND executor_actor_id::text=current_setting('app.actor_id',true) AND current_setting('app.mode',true)='own_write');
REVOKE ALL ON ALL TABLES IN SCHEMA sample FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA sample FROM PUBLIC;
