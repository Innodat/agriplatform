"""Stage protected durable membership actor references; no inferred adoption."""
from alembic import op

revision = 'identity_0015'
down_revision = 'identity_0014'
branch_labels = None
depends_on = None

MEMBERSHIP_ACTOR_ATTRIBUTION_SQL = r"""
ALTER TABLE identity.org_member
 ADD COLUMN created_actor_id uuid CONSTRAINT org_member_created_actor_fk REFERENCES identity.actor(id) ON DELETE RESTRICT,
 ADD COLUMN updated_actor_id uuid CONSTRAINT org_member_updated_actor_fk REFERENCES identity.actor(id) ON DELETE RESTRICT;

CREATE FUNCTION identity.guard_org_member_actor_attribution()
RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp
AS $actor_guard$
BEGIN
 IF TG_OP='UPDATE' AND OLD.created_actor_id IS NOT NULL
    AND NEW.created_actor_id IS DISTINCT FROM OLD.created_actor_id THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_membership_creation_actor_immutable',
    CONSTRAINT='org_member_creation_actor_immutable';
 END IF;
 IF current_user <> 'identity_migrator' AND
   ((TG_OP='INSERT' AND (NEW.created_actor_id IS NOT NULL OR NEW.updated_actor_id IS NOT NULL))
    OR (TG_OP='UPDATE' AND (NEW.created_actor_id IS DISTINCT FROM OLD.created_actor_id
                          OR NEW.updated_actor_id IS DISTINCT FROM OLD.updated_actor_id))) THEN
  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_membership_actor_owner_required',
    CONSTRAINT='org_member_actor_owner_required';
 END IF;
 RETURN NEW;
END;
$actor_guard$;
CREATE TRIGGER org_member_actor_attribution_guard BEFORE INSERT OR UPDATE ON identity.org_member
 FOR EACH ROW EXECUTE FUNCTION identity.guard_org_member_actor_attribution();

-- Strip any inherited function grants, including unlisted default grantees.
DO $acl$
DECLARE a record; grantee text;
BEGIN
 REVOKE ALL ON FUNCTION identity.guard_org_member_actor_attribution() FROM PUBLIC;
 FOR a IN SELECT DISTINCT x.grantee FROM pg_proc p,
  LATERAL aclexplode(p.proacl) x
  WHERE p.oid='identity.guard_org_member_actor_attribution()'::regprocedure AND x.grantee<>p.proowner LOOP
  grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
  EXECUTE format('REVOKE ALL ON FUNCTION identity.guard_org_member_actor_attribution() FROM %s',grantee);
 END LOOP;
END;
$acl$;
"""


def upgrade():
    op.get_bind().exec_driver_sql(MEMBERSHIP_ACTOR_ATTRIBUTION_SQL, execution_options={'no_parameters': True})


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
