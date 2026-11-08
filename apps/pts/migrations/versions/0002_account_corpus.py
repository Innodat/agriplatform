"""Server-owned corpus selection; additive successor roles preserve old consumers."""
from alembic import op
revision='pts_0002'
down_revision='pts_0001'
branch_labels=None
depends_on=None
TABLES=('rights','sources','poems','witnesses','source_documents','metadata','imports','conflicts','attachments')

def upgrade():
    op.execute('''CREATE TABLE pts.corpus_binding (
        singleton boolean PRIMARY KEY DEFAULT true CHECK(singleton), legacy_partition_id uuid NOT NULL,
        inventory_sha256 text NOT NULL CHECK(inventory_sha256 ~ '^[a-f0-9]{64}$'),
        release_reference text NOT NULL CHECK(length(release_reference) BETWEEN 1 AND 200),
        verified_at timestamptz NOT NULL, created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
        created_by uuid NOT NULL DEFAULT current_setting('app.actor_id')::uuid);
        REVOKE ALL ON pts.corpus_binding FROM PUBLIC;
        GRANT SELECT ON pts.corpus_binding TO pts_account_runtime,pts_corpus_import;
        ALTER TABLE pts.corpus_binding ENABLE ROW LEVEL SECURITY;
        ALTER TABLE pts.corpus_binding FORCE ROW LEVEL SECURITY;
        CREATE POLICY owner_binding ON pts.corpus_binding TO pts_migrator USING(true) WITH CHECK(true);
        CREATE POLICY read_binding ON pts.corpus_binding FOR SELECT TO pts_account_runtime,pts_corpus_import USING(true);''')
    for table in TABLES:
        op.execute(f'''ALTER POLICY org_scope ON pts.{table} TO pts_runtime,pts_import,pts_migrator;
            CREATE POLICY corpus_scope ON pts.{table} TO pts_account_runtime,pts_corpus_import
            USING(org_id=(SELECT legacy_partition_id FROM pts.corpus_binding WHERE singleton AND verified_at IS NOT NULL))
            WITH CHECK(org_id=(SELECT legacy_partition_id FROM pts.corpus_binding WHERE singleton AND verified_at IS NOT NULL));
            GRANT SELECT ON pts.{table} TO pts_corpus_import;''')
        if table not in ('imports','conflicts'):op.execute(f'GRANT SELECT ON pts.{table} TO pts_account_runtime')
        op.execute(f'GRANT INSERT ON pts.{table} TO pts_corpus_import')
    op.execute('''CREATE TABLE pts.file_contexts (
        id uuid PRIMARY KEY, account_id uuid NOT NULL, session_id uuid NOT NULL,
        application_id text NOT NULL DEFAULT 'pts' CHECK(application_id='pts'),
        document_id text NOT NULL, presentation text NOT NULL CHECK(presentation IN ('open','download')),
        expires_at timestamptz NOT NULL, created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
        created_by uuid NOT NULL DEFAULT current_setting('app.actor_id')::uuid);
        CREATE INDEX file_context_session ON pts.file_contexts(account_id,session_id);
        ALTER TABLE pts.file_contexts ENABLE ROW LEVEL SECURITY;
        ALTER TABLE pts.file_contexts FORCE ROW LEVEL SECURITY;
        CREATE POLICY file_session ON pts.file_contexts TO pts_account_runtime
        USING(account_id::text=current_setting('app.account_id',true) AND session_id::text=current_setting('app.session_id',true))
        WITH CHECK(account_id::text=current_setting('app.account_id',true) AND session_id::text=current_setting('app.session_id',true));
        GRANT SELECT,INSERT,DELETE ON pts.file_contexts TO pts_account_runtime;
        REVOKE ALL ON pts.file_contexts FROM PUBLIC;''')

def downgrade():raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
