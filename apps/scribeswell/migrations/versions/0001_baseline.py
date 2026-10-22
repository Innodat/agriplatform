"""Verified adoption; no corpus DDL or DML."""
revision = 'scribeswell_0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    raise RuntimeError('scribeswell_downgrade_prohibited')
