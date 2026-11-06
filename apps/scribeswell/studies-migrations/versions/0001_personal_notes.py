"""Additive personal Studies foundation. No cross-owner objects or identity seeds."""
from alembic import op
revision='scribeswell_studies_0001'
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    op.execute('''
CREATE TABLE scribeswell_studies.studies (
 id uuid PRIMARY KEY CHECK(id<>'00000000-0000-0000-0000-000000000000'),
 account_id uuid NOT NULL CHECK(account_id<>'00000000-0000-0000-0000-000000000000'),
 title text NOT NULL CHECK(char_length(title) BETWEEN 1 AND 200 AND title ~ '[^[:space:]]' AND title !~ '[[:cntrl:]]'),
 revision bigint NOT NULL DEFAULT 1 CHECK(revision>0), active boolean NOT NULL DEFAULT true,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(), updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 created_by uuid NOT NULL CHECK(created_by<>'00000000-0000-0000-0000-000000000000'),
 updated_by uuid NOT NULL CHECK(updated_by<>'00000000-0000-0000-0000-000000000000'),
 UNIQUE(account_id,id),CHECK(updated_at>=created_at));
CREATE TABLE scribeswell_studies.notes (
 id uuid PRIMARY KEY CHECK(id<>'00000000-0000-0000-0000-000000000000'),
 account_id uuid NOT NULL, study_id uuid NOT NULL,
 visibility text NOT NULL DEFAULT 'study' CHECK(visibility='study'),
 value jsonb NOT NULL CHECK(jsonb_typeof(value)='object' AND value ?& ARRAY['document','connections','highlights']),
 revision bigint NOT NULL DEFAULT 1 CHECK(revision>0),active boolean NOT NULL DEFAULT true,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 created_by uuid NOT NULL CHECK(created_by<>'00000000-0000-0000-0000-000000000000'),
 updated_by uuid NOT NULL CHECK(updated_by<>'00000000-0000-0000-0000-000000000000'),
 UNIQUE(account_id,study_id,id),FOREIGN KEY(account_id,study_id) REFERENCES scribeswell_studies.studies(account_id,id),CHECK(updated_at>=created_at));
CREATE TABLE scribeswell_studies.receipts (
 account_id uuid NOT NULL,command text NOT NULL CHECK(command IN('study.create','note.create','note.replace')),
 command_version integer NOT NULL CHECK(command_version=1),operation_id uuid NOT NULL CHECK(operation_id<>'00000000-0000-0000-0000-000000000000'),
 fingerprint text NOT NULL CHECK(fingerprint ~ '^[a-f0-9]{64}$'),outcome jsonb NOT NULL,
 study_id uuid NOT NULL,note_id uuid,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),created_by uuid NOT NULL CHECK(created_by<>'00000000-0000-0000-0000-000000000000'),
 PRIMARY KEY(account_id,command,command_version,operation_id),
 FOREIGN KEY(account_id,study_id) REFERENCES scribeswell_studies.studies(account_id,id),
 FOREIGN KEY(account_id,study_id,note_id) REFERENCES scribeswell_studies.notes(account_id,study_id,id),
 CHECK((command='study.create')=(note_id IS NULL)));
CREATE INDEX studies_owner_page ON scribeswell_studies.studies(account_id,created_at DESC,id DESC) WHERE active;
CREATE INDEX notes_owner_page ON scribeswell_studies.notes(account_id,study_id,created_at DESC,id DESC) WHERE active;
CREATE FUNCTION scribeswell_studies.immutable_attribution() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF NEW.id<>OLD.id OR NEW.account_id<>OLD.account_id OR NEW.created_at<>OLD.created_at OR NEW.created_by<>OLD.created_by THEN RAISE EXCEPTION 'immutable attribution' USING ERRCODE='23514'; END IF;
 IF TG_TABLE_NAME='notes' THEN
  IF NEW.study_id<>OLD.study_id OR NEW.visibility<>OLD.visibility THEN RAISE EXCEPTION 'immutable scope' USING ERRCODE='23514';END IF;
 END IF;
 IF NOT OLD.active AND NEW.active THEN RAISE EXCEPTION 'closed lifecycle' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION scribeswell_studies.immutable_attribution() FROM PUBLIC;
CREATE TRIGGER study_attribution BEFORE UPDATE ON scribeswell_studies.studies FOR EACH ROW EXECUTE FUNCTION scribeswell_studies.immutable_attribution();
CREATE TRIGGER note_attribution BEFORE UPDATE ON scribeswell_studies.notes FOR EACH ROW EXECUTE FUNCTION scribeswell_studies.immutable_attribution();
''')
    for table in ('studies','notes','receipts'):
        op.execute(f'''ALTER TABLE scribeswell_studies.{table} ENABLE ROW LEVEL SECURITY;
ALTER TABLE scribeswell_studies.{table} FORCE ROW LEVEL SECURITY;
CREATE POLICY owner_scope ON scribeswell_studies.{table} USING (account_id=nullif(current_setting('app.account_id',true),'')::uuid) WITH CHECK (account_id=nullif(current_setting('app.account_id',true),'')::uuid);
REVOKE ALL ON scribeswell_studies.{table} FROM PUBLIC,scribeswell_studies_runtime,scribeswell_studies_operator;
GRANT SELECT,INSERT ON scribeswell_studies.{table} TO scribeswell_studies_runtime;''')
    op.execute('''DO $$ DECLARE denied text; BEGIN
 FOR denied IN SELECT rolname FROM pg_roles WHERE rolname IN ('anon','authenticated','service_role','scribeswell_runtime','scribeswell_import') LOOP
  EXECUTE format('REVOKE ALL ON SCHEMA scribeswell_studies FROM %I',denied);
  EXECUTE format('REVOKE ALL ON ALL TABLES IN SCHEMA scribeswell_studies FROM %I',denied);
 END LOOP;
END $$;
GRANT UPDATE(title,revision,active,updated_at,updated_by) ON scribeswell_studies.studies TO scribeswell_studies_runtime;
GRANT UPDATE(value,revision,active,updated_at,updated_by) ON scribeswell_studies.notes TO scribeswell_studies_runtime;''')

def downgrade():
    raise RuntimeError('Forward recovery only; preserve acknowledged notes and receipts')
