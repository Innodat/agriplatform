"""Admit compact delete receipts and prohibit payloads in closed notes."""
from alembic import op
revision='scribeswell_studies_0004'
down_revision='scribeswell_studies_0003'
branch_labels=None
depends_on=None

def upgrade():
    op.execute('''
ALTER TABLE scribeswell_studies.receipts DROP CONSTRAINT receipts_command_check;
ALTER TABLE scribeswell_studies.receipts DROP CONSTRAINT receipts_check;
ALTER TABLE scribeswell_studies.receipts ADD CONSTRAINT receipts_command_check CHECK(command IN('study.create','study.rename','study.passages.replace','note.create','note.replace','note.delete'));
ALTER TABLE scribeswell_studies.receipts ADD CONSTRAINT receipts_check CHECK((command IN('study.create','study.rename','study.passages.replace'))=(note_id IS NULL));
ALTER TABLE scribeswell_studies.notes ADD CONSTRAINT notes_closed_value_empty CHECK(active OR value='{"document":{"version":1,"blocks":[]},"connections":[],"highlights":[]}'::jsonb);
''')

def downgrade():
    raise RuntimeError('Forward recovery only; preserve deletion tombstones and receipts')
