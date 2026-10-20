"""Retain membership instances and their dependent legacy evidence."""
from alembic import op

revision = 'identity_0012'
down_revision = 'identity_0011'
branch_labels = None
depends_on = None

MEMBERSHIP_RETENTION_SQL = r"""
ALTER TABLE identity.org_member DROP CONSTRAINT org_member_org_id_fkey;
ALTER TABLE identity.org_member ADD CONSTRAINT org_member_org_id_fkey
    FOREIGN KEY (org_id) REFERENCES identity.org(id) ON DELETE RESTRICT;
ALTER TABLE identity.org_member DROP CONSTRAINT org_member_user_id_fkey;
ALTER TABLE identity.org_member ADD CONSTRAINT org_member_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES identity.users(id) ON DELETE RESTRICT;
ALTER TABLE identity.member_role DROP CONSTRAINT member_role_member_id_fkey;
ALTER TABLE identity.member_role ADD CONSTRAINT member_role_member_id_fkey
    FOREIGN KEY (member_id) REFERENCES identity.org_member(id) ON DELETE RESTRICT;
CREATE OR REPLACE FUNCTION identity.guard_org_member_revision()
RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp
AS $revision_guard$
BEGIN
    IF TG_OP IN ('DELETE', 'TRUNCATE') THEN
        RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'identity_membership_history_retained',
            CONSTRAINT = 'org_member_history_retained';
    END IF;
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
DROP TRIGGER org_member_revision_guard ON identity.org_member;
CREATE TRIGGER org_member_revision_guard BEFORE INSERT OR UPDATE OR DELETE ON identity.org_member
FOR EACH ROW EXECUTE FUNCTION identity.guard_org_member_revision();
CREATE TRIGGER org_member_history_truncate_guard BEFORE TRUNCATE ON identity.org_member
FOR EACH STATEMENT EXECUTE FUNCTION identity.guard_org_member_revision();
"""


def upgrade():
    # CREATE OR REPLACE preserves the existing function identity, owner and ACL.
    op.get_bind().exec_driver_sql(MEMBERSHIP_RETENTION_SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
