"""Selected account organization read and compatible server-owned member revision."""
from alembic import op
from sqlalchemy import text
from identity_baseline import verify_projection_role

revision = 'identity_0004'
down_revision = 'identity_0003'
branch_labels = None
depends_on = None

ORGANIZATION_SCHEMA_SQL = r"""
ALTER TABLE identity.org_member ADD COLUMN revision bigint NOT NULL DEFAULT 1
    CONSTRAINT org_member_revision_positive CHECK (revision > 0);
CREATE FUNCTION identity.guard_org_member_revision()
RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp
AS $revision_guard$
BEGIN
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
CREATE TRIGGER org_member_revision_guard BEFORE INSERT OR UPDATE ON identity.org_member
FOR EACH ROW EXECUTE FUNCTION identity.guard_org_member_revision();
GRANT SELECT (id, deleted_at) ON identity.org TO identity_account_projection_owner;
GRANT SELECT (id, org_id, user_id, deleted_at, revision) ON identity.org_member TO identity_account_projection_owner;
CREATE POLICY account_organization_read ON identity.org FOR SELECT TO identity_account_projection_owner
USING (current_setting('app.context_kind', true) = 'user'
       AND id::text = lower(current_setting('app.org_id', true)) AND deleted_at IS NULL);
CREATE POLICY account_organization_bound ON identity.org AS RESTRICTIVE FOR SELECT TO identity_account_projection_owner
USING (current_setting('app.context_kind', true) = 'user'
       AND id::text = lower(current_setting('app.org_id', true)) AND deleted_at IS NULL);
CREATE POLICY account_membership_read ON identity.org_member FOR SELECT TO identity_account_projection_owner
USING (current_setting('app.context_kind', true) = 'user'
       AND org_id::text = lower(current_setting('app.org_id', true))
       AND user_id::text = lower(current_setting('app.account_id', true)) AND deleted_at IS NULL);
CREATE POLICY account_membership_bound ON identity.org_member AS RESTRICTIVE FOR SELECT TO identity_account_projection_owner
USING (current_setting('app.context_kind', true) = 'user'
       AND org_id::text = lower(current_setting('app.org_id', true))
       AND user_id::text = lower(current_setting('app.account_id', true)) AND deleted_at IS NULL);
CREATE FUNCTION identity.current_account_organization()
RETURNS TABLE (account_id uuid, org_id uuid, membership_id bigint, membership_revision bigint, actor_id uuid)
LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = pg_catalog, pg_temp
AS $organization_projection$
DECLARE verified_account uuid; verified_org uuid; asserted_account text; asserted_org text;
BEGIN
    IF current_setting('app.context_kind', true) IS DISTINCT FROM 'user' THEN RETURN; END IF;
    asserted_account := current_setting('app.account_id', true);
    asserted_org := current_setting('app.org_id', true);
    IF asserted_account IS NULL OR asserted_org IS NULL
       OR asserted_account !~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
       OR asserted_org !~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' THEN RETURN; END IF;
    verified_account := asserted_account::uuid; verified_org := asserted_org::uuid;
    IF verified_account = '00000000-0000-0000-0000-000000000000'::uuid
       OR verified_org = '00000000-0000-0000-0000-000000000000'::uuid THEN RETURN; END IF;
    RETURN QUERY
        SELECT profile.id, organization.id, member.id, member.revision, actor.id
        FROM identity.users AS profile
        JOIN identity.org_member AS member ON member.user_id = profile.id
        JOIN identity.org AS organization ON organization.id = member.org_id
        LEFT JOIN identity.account_actor AS mapping ON mapping.account_id = profile.id AND mapping.actor_kind = 'account'
        LEFT JOIN identity.actor AS actor ON actor.id = mapping.actor_id AND actor.kind = mapping.actor_kind
        WHERE profile.id = verified_account AND organization.id = verified_org
          AND profile.deleted_at IS NULL AND organization.deleted_at IS NULL AND member.deleted_at IS NULL;
END;
$organization_projection$;
-- New routines must not inherit legacy or unlisted default grants.
DO $organization_acl$
DECLARE routine record; granted_role record; grantee_name text;
BEGIN
    FOR routine IN SELECT p.oid, p.proowner, p.proacl, p.oid::regprocedure AS signature
      FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
      WHERE n.nspname='identity' AND p.proname IN ('guard_org_member_revision','current_account_organization')
    LOOP
        EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC', routine.signature);
        FOR granted_role IN SELECT DISTINCT a.grantee FROM aclexplode(routine.proacl) a WHERE a.grantee <> routine.proowner
        LOOP
            grantee_name := CASE WHEN granted_role.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(granted_role.grantee)) END;
            EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s', routine.signature, grantee_name);
        END LOOP;
    END LOOP;
END;
$organization_acl$;
GRANT EXECUTE ON FUNCTION identity.current_account_organization() TO access_runtime;
GRANT CREATE ON SCHEMA identity TO identity_account_projection_owner;
ALTER FUNCTION identity.current_account_organization() OWNER TO identity_account_projection_owner;
REVOKE CREATE ON SCHEMA identity FROM identity_account_projection_owner;
"""


def upgrade():
    connection = op.get_bind()
    verify_projection_role(connection)
    connection.execute(text(ORGANIZATION_SCHEMA_SQL))


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
