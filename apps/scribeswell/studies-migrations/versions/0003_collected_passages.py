"""Add independently revised, owner-scoped collected passage lists and receipts."""
from alembic import op
revision='scribeswell_studies_0003'
down_revision='scribeswell_studies_0002'
branch_labels=None
depends_on=None

def upgrade():
    op.execute('''
ALTER TABLE scribeswell_studies.receipts DROP CONSTRAINT receipts_command_check;
ALTER TABLE scribeswell_studies.receipts DROP CONSTRAINT receipts_check;
ALTER TABLE scribeswell_studies.receipts ADD CONSTRAINT receipts_command_check CHECK(command IN('study.create','study.rename','study.passages.replace','note.create','note.replace'));
ALTER TABLE scribeswell_studies.receipts ADD CONSTRAINT receipts_check CHECK((command IN('study.create','study.rename','study.passages.replace'))=(note_id IS NULL));
CREATE TABLE scribeswell_studies.passage_lists (
 account_id uuid NOT NULL, study_id uuid NOT NULL,
 revision bigint NOT NULL CHECK(revision>=2),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 created_by uuid NOT NULL CHECK(created_by<>'00000000-0000-0000-0000-000000000000'),
 updated_by uuid NOT NULL CHECK(updated_by<>'00000000-0000-0000-0000-000000000000'),
 PRIMARY KEY(account_id,study_id),FOREIGN KEY(account_id,study_id) REFERENCES scribeswell_studies.studies(account_id,id),CHECK(updated_at>=created_at));
CREATE TABLE scribeswell_studies.passage_entries (
 account_id uuid NOT NULL,study_id uuid NOT NULL,
 id uuid NOT NULL CHECK(id<>'00000000-0000-0000-0000-000000000000'),
 position integer NOT NULL CHECK(position BETWEEN 1 AND 200),
 catalogue_id text NOT NULL CHECK(catalogue_id='scribeswell.references.v1'),
 catalogue_version text NOT NULL CHECK(catalogue_version ~ '^[0-9a-f]{64}$'),
 versification_id text NOT NULL CHECK(length(versification_id) BETWEEN 1 AND 80),
 book_id text NOT NULL CHECK(length(book_id) BETWEEN 1 AND 8),
 kind text NOT NULL CHECK(kind IN('chapter','verse_range')),
 start_chapter integer NOT NULL CHECK(start_chapter BETWEEN 1 AND 150),
 start_verse integer,end_chapter integer,end_verse integer,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),created_by uuid NOT NULL CHECK(created_by<>'00000000-0000-0000-0000-000000000000'),
 PRIMARY KEY(account_id,study_id,id),UNIQUE(account_id,study_id,position),
 FOREIGN KEY(account_id,study_id) REFERENCES scribeswell_studies.passage_lists(account_id,study_id),
 CHECK((kind='chapter' AND start_verse IS NULL AND end_chapter IS NULL AND end_verse IS NULL) OR
 (kind='verse_range' AND start_verse IS NOT NULL AND end_chapter IS NOT NULL AND end_verse IS NOT NULL AND start_verse BETWEEN 1 AND 176 AND end_chapter BETWEEN 1 AND 150 AND end_verse BETWEEN 1 AND 176 AND (start_chapter,start_verse)<=(end_chapter,end_verse))),
 UNIQUE NULLS NOT DISTINCT(account_id,study_id,catalogue_id,catalogue_version,versification_id,book_id,kind,start_chapter,start_verse,end_chapter,end_verse));
CREATE FUNCTION scribeswell_studies.passage_list_attribution() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF (NEW.account_id,NEW.study_id,NEW.created_at,NEW.created_by) IS DISTINCT FROM (OLD.account_id,OLD.study_id,OLD.created_at,OLD.created_by) THEN RAISE EXCEPTION 'immutable attribution' USING ERRCODE='23514';END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION scribeswell_studies.passage_list_attribution() FROM PUBLIC;
CREATE TRIGGER passage_list_attribution BEFORE UPDATE ON scribeswell_studies.passage_lists FOR EACH ROW EXECUTE FUNCTION scribeswell_studies.passage_list_attribution();
''')
    for table in ('passage_lists','passage_entries'):
        op.execute(f'''ALTER TABLE scribeswell_studies.{table} ENABLE ROW LEVEL SECURITY;
ALTER TABLE scribeswell_studies.{table} FORCE ROW LEVEL SECURITY;
CREATE POLICY owner_scope ON scribeswell_studies.{table} USING(account_id=nullif(current_setting('app.account_id',true),'')::uuid) WITH CHECK(account_id=nullif(current_setting('app.account_id',true),'')::uuid);
REVOKE ALL ON scribeswell_studies.{table} FROM PUBLIC,scribeswell_studies_runtime,scribeswell_studies_operator;
GRANT SELECT,INSERT ON scribeswell_studies.{table} TO scribeswell_studies_runtime;''')
    op.execute('''GRANT UPDATE(revision,updated_by,updated_at) ON scribeswell_studies.passage_lists TO scribeswell_studies_runtime;
GRANT DELETE ON scribeswell_studies.passage_entries TO scribeswell_studies_runtime;''')

def downgrade():
    raise RuntimeError('Forward recovery only; preserve acknowledged collections and receipts')
