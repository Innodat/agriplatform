"""Reject numerically equal noninteger input versions on alternate write paths.

0005 JSONB equality admits 1.0; the supported API writes exact integer1.
This additive check preserves the previous running D1 reader/writer contract.
"""
from alembic import op
revision='0006_draft_input_version'
down_revision='0005_drafts'
branch_labels=None
depends_on=None

def upgrade():
    op.execute("""ALTER TABLE leave.draft ADD CONSTRAINT draft_input_version_exact
      CHECK(state<>'active' OR (jsonb_typeof(input->'input_version')='number'
        AND input->>'input_version'='1'))""")

def downgrade():raise RuntimeError('forward_recovery_required')
