"""Add nullable study details; controlled migration before activation, authored only."""
from alembic import op
revision='scribeswell_studies_0008'
down_revision='scribeswell_studies_0007'
branch_labels=None
depends_on=None

def upgrade():
 op.execute('''
ALTER TABLE scribeswell_studies.studies ADD COLUMN introduction text;
ALTER TABLE scribeswell_studies.studies ADD COLUMN source_url text;
ALTER TABLE scribeswell_studies.studies ADD CONSTRAINT study_introduction_length CHECK(introduction IS NULL OR char_length(introduction)<=10000);
ALTER TABLE scribeswell_studies.studies ADD CONSTRAINT study_source_url_length CHECK(source_url IS NULL OR octet_length(source_url)<=2048);
CREATE FUNCTION scribeswell_studies.erase_closed_study_details() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF NOT NEW.active THEN NEW.introduction=NULL; NEW.source_url=NULL; END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION scribeswell_studies.erase_closed_study_details() FROM PUBLIC;
CREATE TRIGGER study_details_lifecycle BEFORE UPDATE ON scribeswell_studies.studies FOR EACH ROW EXECUTE FUNCTION scribeswell_studies.erase_closed_study_details();
ALTER TABLE scribeswell_studies.studies ADD CONSTRAINT closed_study_details_empty CHECK(active OR (introduction IS NULL AND source_url IS NULL));
GRANT UPDATE(introduction,source_url) ON scribeswell_studies.studies TO scribeswell_studies_runtime;
ALTER TABLE scribeswell_studies.receipts DROP CONSTRAINT receipts_command_check;
ALTER TABLE scribeswell_studies.receipts DROP CONSTRAINT receipts_check;
ALTER TABLE scribeswell_studies.receipts ADD CONSTRAINT receipts_command_check CHECK(command IN('study.details.replace','study.create','study.rename','study.passages.replace','study.delete','study.copy','note.create','note.replace','note.delete','note.duplicate','note.conflict_copy'));
ALTER TABLE scribeswell_studies.receipts ADD CONSTRAINT receipts_check CHECK((command IN('study.details.replace','study.create','study.rename','study.passages.replace','study.delete','study.copy'))=(note_id IS NULL));
''')

def downgrade():
 raise RuntimeError('Forward recovery only; preserve study details and receipts')
