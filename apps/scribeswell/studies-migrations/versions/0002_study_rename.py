"""Admit metadata rename receipts without altering prior commands or data."""
from alembic import op
revision='scribeswell_studies_0002'
down_revision='scribeswell_studies_0001'
branch_labels=None
depends_on=None

def upgrade():
    op.execute("""
ALTER TABLE scribeswell_studies.receipts DROP CONSTRAINT receipts_command_check;
ALTER TABLE scribeswell_studies.receipts DROP CONSTRAINT receipts_check;
ALTER TABLE scribeswell_studies.receipts ADD CONSTRAINT receipts_command_check CHECK(command IN('study.create','study.rename','note.create','note.replace'));
ALTER TABLE scribeswell_studies.receipts ADD CONSTRAINT receipts_check CHECK((command IN('study.create','study.rename'))=(note_id IS NULL));
""")

def downgrade():
    raise RuntimeError('Forward recovery only; preserve acknowledged metadata and receipts')
