"""Independent copy provenance and receipts; no source FK or source content cache."""
from alembic import op
revision='scribeswell_studies_0007'
down_revision='scribeswell_studies_0006'
branch_labels=None
depends_on=None

def upgrade():
 op.execute('''
ALTER TABLE scribeswell_studies.receipts DROP CONSTRAINT receipts_command_check;
ALTER TABLE scribeswell_studies.receipts DROP CONSTRAINT receipts_check;
ALTER TABLE scribeswell_studies.receipts ADD CONSTRAINT receipts_command_check CHECK(command IN('study.create','study.rename','study.passages.replace','study.delete','study.copy','note.create','note.replace','note.delete','note.duplicate','note.conflict_copy'));
ALTER TABLE scribeswell_studies.receipts ADD CONSTRAINT receipts_check CHECK((command IN('study.create','study.rename','study.passages.replace','study.delete','study.copy'))=(note_id IS NULL));
CREATE TABLE scribeswell_studies.study_copy_provenance(
 account_id uuid NOT NULL,study_id uuid NOT NULL,
 source_account_id uuid NOT NULL CHECK(source_account_id<>'00000000-0000-0000-0000-000000000000'),
 source_study_id uuid NOT NULL CHECK(source_study_id<>'00000000-0000-0000-0000-000000000000'),
 origin_account_id uuid NOT NULL CHECK(origin_account_id<>'00000000-0000-0000-0000-000000000000'),
 origin_study_id uuid NOT NULL CHECK(origin_study_id<>'00000000-0000-0000-0000-000000000000'),
 relation text NOT NULL CHECK(relation='study.copy'),
 created_by uuid NOT NULL CHECK(created_by<>'00000000-0000-0000-0000-000000000000'),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 CHECK(source_account_id=account_id AND origin_account_id=account_id),
 PRIMARY KEY(account_id,study_id),
 FOREIGN KEY(account_id,study_id) REFERENCES scribeswell_studies.studies(account_id,id)
);
CREATE TABLE scribeswell_studies.note_copy_provenance(
 account_id uuid NOT NULL,study_id uuid NOT NULL,note_id uuid NOT NULL,
 source_account_id uuid NOT NULL CHECK(source_account_id<>'00000000-0000-0000-0000-000000000000'),
 source_study_id uuid NOT NULL CHECK(source_study_id<>'00000000-0000-0000-0000-000000000000'),
 source_note_id uuid NOT NULL CHECK(source_note_id<>'00000000-0000-0000-0000-000000000000'),
 origin_account_id uuid NOT NULL CHECK(origin_account_id<>'00000000-0000-0000-0000-000000000000'),
 origin_study_id uuid NOT NULL CHECK(origin_study_id<>'00000000-0000-0000-0000-000000000000'),
 origin_note_id uuid NOT NULL CHECK(origin_note_id<>'00000000-0000-0000-0000-000000000000'),
 relation text NOT NULL CHECK(relation IN('study.copy','note.duplicate','note.conflict_copy')),
 created_by uuid NOT NULL CHECK(created_by<>'00000000-0000-0000-0000-000000000000'),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 CHECK(source_account_id=account_id AND origin_account_id=account_id),
 PRIMARY KEY(account_id,study_id,note_id),
 FOREIGN KEY(account_id,study_id,note_id) REFERENCES scribeswell_studies.notes(account_id,study_id,id)
);
''')
 for table in ('study_copy_provenance','note_copy_provenance'):
  op.execute(f'''
ALTER TABLE scribeswell_studies.{table} ENABLE ROW LEVEL SECURITY;
ALTER TABLE scribeswell_studies.{table} FORCE ROW LEVEL SECURITY;
CREATE POLICY owner_scope ON scribeswell_studies.{table} USING(account_id=nullif(current_setting('app.account_id',true),'')::uuid) WITH CHECK(account_id=nullif(current_setting('app.account_id',true),'')::uuid);
REVOKE ALL ON scribeswell_studies.{table} FROM PUBLIC,scribeswell_studies_runtime,scribeswell_studies_operator;
GRANT SELECT,INSERT ON scribeswell_studies.{table} TO scribeswell_studies_runtime;
CREATE TRIGGER immutable_copy_provenance BEFORE UPDATE OR DELETE OR TRUNCATE ON scribeswell_studies.{table} FOR EACH STATEMENT EXECUTE FUNCTION scribeswell_studies.immutable_note_metadata();
CREATE TRIGGER active_study_insert BEFORE INSERT ON scribeswell_studies.{table} FOR EACH ROW EXECUTE FUNCTION scribeswell_studies.require_active_parent();
''')

def downgrade():
 raise RuntimeError('Forward recovery only; preserve independent copies and receipts')
