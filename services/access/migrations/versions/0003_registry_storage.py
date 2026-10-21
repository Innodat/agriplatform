"""Private empty global registry storage; protected commands remain gated."""
from alembic import op

revision = 'access_0003'
down_revision = 'access_0002'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE TABLE access.applications (
 app_id text PRIMARY KEY,
 enabled boolean NOT NULL DEFAULT false,
 revision bigint NOT NULL DEFAULT 1,
 created_by uuid NOT NULL,
 updated_by uuid NOT NULL,
 created_at timestamptz NOT NULL,
 updated_at timestamptz NOT NULL,
 CONSTRAINT applications_app_id_valid CHECK (app_id COLLATE "C" ~ '^[a-z][a-z0-9_]{1,63}$'),
 CONSTRAINT applications_revision_positive CHECK (revision > 0),
 CONSTRAINT applications_created_by_non_nil CHECK (created_by <> '00000000-0000-0000-0000-000000000000'::uuid),
 CONSTRAINT applications_updated_by_non_nil CHECK (updated_by <> '00000000-0000-0000-0000-000000000000'::uuid),
 CONSTRAINT applications_created_at_finite CHECK (isfinite(created_at)),
 CONSTRAINT applications_updated_at_finite CHECK (isfinite(updated_at))
);
CREATE TABLE access.permissions (
 permission text PRIMARY KEY,
 app_id text NOT NULL,
 scope_kind text NOT NULL,
 created_by uuid NOT NULL,
 created_at timestamptz NOT NULL,
 CONSTRAINT permissions_permission_valid CHECK (octet_length(convert_to(permission, 'UTF8')) BETWEEN 1 AND 200 AND length(permission) = octet_length(convert_to(permission, 'UTF8'))),
 CONSTRAINT permissions_scope_kind_valid CHECK (scope_kind IN ('account', 'organization')),
 CONSTRAINT permissions_created_by_non_nil CHECK (created_by <> '00000000-0000-0000-0000-000000000000'::uuid),
 CONSTRAINT permissions_created_at_finite CHECK (isfinite(created_at)),
 CONSTRAINT permissions_app_id_fkey FOREIGN KEY (app_id) REFERENCES access.applications(app_id) ON DELETE RESTRICT,
 CONSTRAINT permissions_permission_scope_kind_key UNIQUE (permission, scope_kind),
 CONSTRAINT permissions_app_id_permission_key UNIQUE (app_id, permission)
);
CREATE TABLE access.entry_permissions (
 app_id text NOT NULL,
 permission text NOT NULL,
 created_by uuid NOT NULL,
 created_at timestamptz NOT NULL,
 CONSTRAINT entry_permissions_pkey PRIMARY KEY (app_id, permission),
 CONSTRAINT entry_permissions_created_by_non_nil CHECK (created_by <> '00000000-0000-0000-0000-000000000000'::uuid),
 CONSTRAINT entry_permissions_created_at_finite CHECK (isfinite(created_at)),
 CONSTRAINT entry_permissions_app_id_permission_fkey FOREIGN KEY (app_id, permission) REFERENCES access.permissions(app_id, permission) ON DELETE RESTRICT
);
CREATE FUNCTION access.registry_storage_immutable() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path = pg_catalog, pg_temp AS $guard$
BEGIN
 RAISE EXCEPTION USING ERRCODE = '55000', MESSAGE = 'access_registry_storage_immutable';
END
$guard$;
REVOKE ALL ON FUNCTION access.registry_storage_immutable() FROM PUBLIC;
CREATE TRIGGER registry_storage_immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON access.applications FOR EACH STATEMENT EXECUTE FUNCTION access.registry_storage_immutable();
CREATE TRIGGER registry_storage_immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON access.permissions FOR EACH STATEMENT EXECUTE FUNCTION access.registry_storage_immutable();
CREATE TRIGGER registry_storage_immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON access.entry_permissions FOR EACH STATEMENT EXECUTE FUNCTION access.registry_storage_immutable();
REVOKE ALL ON access.applications, access.permissions, access.entry_permissions FROM PUBLIC;
""")


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
