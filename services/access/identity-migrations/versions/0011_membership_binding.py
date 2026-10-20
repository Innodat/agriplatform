"""Preserve the identity of existing membership instances."""
from alembic import op

revision = 'identity_0011'
down_revision = 'identity_0010'
branch_labels = None
depends_on = None

MEMBERSHIP_BINDING_SQL = r"""
CREATE OR REPLACE FUNCTION identity.guard_org_member_revision()
RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp
AS $revision_guard$
BEGIN
    IF TG_OP = 'UPDATE' AND (NEW.id IS DISTINCT FROM OLD.id
        OR NEW.org_id IS DISTINCT FROM OLD.org_id
        OR NEW.user_id IS DISTINCT FROM OLD.user_id) THEN
        RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'identity_membership_binding_immutable',
            CONSTRAINT = 'org_member_binding_immutable';
    END IF;
    IF TG_OP = 'INSERT' THEN
        NEW.revision := 1;
    ELSIF (to_jsonb(NEW) - 'revision') IS DISTINCT FROM (to_jsonb(OLD) - 'revision') THEN
        IF OLD.revision = 9223372036854775807 THEN
            RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'identity_membership_revision_exhausted',
                CONSTRAINT = 'org_member_revision_positive';
        END IF;
        NEW.revision := OLD.revision + 1;
    ELSE
        NEW.revision := OLD.revision;
    END IF;
    RETURN NEW;
END;
$revision_guard$;
"""


def upgrade():
    # CREATE OR REPLACE preserves the existing function identity, owner and ACL.
    op.get_bind().exec_driver_sql(MEMBERSHIP_BINDING_SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
