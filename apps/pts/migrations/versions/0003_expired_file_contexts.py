"""Bounded owner reclamation of expired contexts from departed sessions."""
from alembic import op

revision='pts_0003'
down_revision='pts_0002'
branch_labels=None
depends_on=None


def upgrade():
    # The definer is the existing restricted schema owner. FORCE RLS still
    # applies: it can see/delete only expired rows through this new policy.
    # Runtime keeps its exact-session direct policies and no broader table grant.
    op.execute('''CREATE INDEX file_context_expiry ON pts.file_contexts(expires_at,id);
        CREATE POLICY owner_expired_context ON pts.file_contexts TO pts_migrator
        USING(expires_at<=clock_timestamp()) WITH CHECK(false);
        CREATE FUNCTION pts.reclaim_expired_file_contexts() RETURNS void
        LANGUAGE sql SECURITY DEFINER
        SET search_path=pg_catalog,pg_temp SET lock_timeout='100ms'
        AS $reclaim$
          WITH expired AS (
            SELECT id FROM pts.file_contexts WHERE expires_at<=clock_timestamp()
            ORDER BY expires_at,id LIMIT 128 FOR UPDATE SKIP LOCKED
          )
          DELETE FROM pts.file_contexts WHERE id IN (SELECT id FROM expired)
        $reclaim$;
        REVOKE ALL ON FUNCTION pts.reclaim_expired_file_contexts() FROM PUBLIC;
        GRANT EXECUTE ON FUNCTION pts.reclaim_expired_file_contexts() TO pts_account_runtime;''')


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
