"""Close and erase owned studies; guard alternate restricted inserts/closure."""
from alembic import op
revision='scribeswell_studies_0005'
down_revision='scribeswell_studies_0004'
branch_labels=None
depends_on=None


def upgrade():
    # The NOBYPASSRLS table owner has no account setting. Transactional DDL
    # locks keep the temporary owner-only validation visibility from committing.
    for table in ('studies','notes','passage_lists','passage_entries'):
        op.execute(f'ALTER TABLE scribeswell_studies.{table} NO FORCE ROW LEVEL SECURITY')
    op.execute('''
DO $$ BEGIN
 IF EXISTS(SELECT 1 FROM scribeswell_studies.studies s WHERE NOT s.active AND
   (EXISTS(SELECT 1 FROM scribeswell_studies.notes n WHERE n.account_id=s.account_id AND n.study_id=s.id AND n.active)
    OR EXISTS(SELECT 1 FROM scribeswell_studies.passage_lists p WHERE p.account_id=s.account_id AND p.study_id=s.id)
    OR EXISTS(SELECT 1 FROM scribeswell_studies.passage_entries p WHERE p.account_id=s.account_id AND p.study_id=s.id))) THEN
  RAISE EXCEPTION 'closed study integrity violation' USING ERRCODE='23514';
 END IF;
END $$;
ALTER TABLE scribeswell_studies.receipts DROP CONSTRAINT receipts_command_check;
ALTER TABLE scribeswell_studies.receipts DROP CONSTRAINT receipts_check;
ALTER TABLE scribeswell_studies.receipts ADD CONSTRAINT receipts_command_check CHECK(command IN('study.create','study.rename','study.passages.replace','study.delete','note.create','note.replace','note.delete'));
ALTER TABLE scribeswell_studies.receipts ADD CONSTRAINT receipts_check CHECK((command IN('study.create','study.rename','study.passages.replace','study.delete'))=(note_id IS NULL));
ALTER TABLE scribeswell_studies.studies ADD CONSTRAINT studies_closed_title_empty CHECK(active OR title='Deleted study');
GRANT DELETE ON scribeswell_studies.passage_lists TO scribeswell_studies_runtime;
CREATE FUNCTION scribeswell_studies.require_active_parent() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 PERFORM id FROM scribeswell_studies.studies WHERE account_id=NEW.account_id AND id=NEW.study_id AND active FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'study unavailable' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION scribeswell_studies.require_active_parent() FROM PUBLIC;
CREATE FUNCTION scribeswell_studies.require_empty_closed_study() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF NOT NEW.active AND
  (EXISTS(SELECT 1 FROM scribeswell_studies.notes WHERE account_id=NEW.account_id AND study_id=NEW.id AND active)
   OR EXISTS(SELECT 1 FROM scribeswell_studies.passage_lists WHERE account_id=NEW.account_id AND study_id=NEW.id)
   OR EXISTS(SELECT 1 FROM scribeswell_studies.passage_entries WHERE account_id=NEW.account_id AND study_id=NEW.id)) THEN
  RAISE EXCEPTION 'closed study integrity violation' USING ERRCODE='23514';
 END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION scribeswell_studies.require_empty_closed_study() FROM PUBLIC;
CREATE TRIGGER studies_closed_children BEFORE UPDATE ON scribeswell_studies.studies FOR EACH ROW EXECUTE FUNCTION scribeswell_studies.require_empty_closed_study();
''')
    for table in ('notes','passage_lists','passage_entries'):
        op.execute(f'CREATE TRIGGER active_study_insert BEFORE INSERT ON scribeswell_studies.{table} FOR EACH ROW EXECUTE FUNCTION scribeswell_studies.require_active_parent()')
    for table in ('studies','notes','passage_lists','passage_entries'):
        op.execute(f'ALTER TABLE scribeswell_studies.{table} FORCE ROW LEVEL SECURITY')


def downgrade():
    raise RuntimeError('Forward recovery only; preserve study tombstones and receipts')
