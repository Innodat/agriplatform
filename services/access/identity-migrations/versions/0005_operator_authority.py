"""Protected operator mapping and fixed authorization read; no command effects."""
from alembic import op
from sqlalchemy import text
from identity_baseline import verify_authority_roles
revision = 'identity_0005'
down_revision = 'identity_0004'
branch_labels = None
depends_on = None

AUTHORITY_SCHEMA_SQL = r"""
CREATE TABLE identity.operator_principals (
    database_login name PRIMARY KEY CHECK (database_login::text <> ''),
    executor_actor_id uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
    enabled boolean NOT NULL DEFAULT false,
    revision bigint NOT NULL DEFAULT 1 CHECK (revision > 0),
    created_by uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
    updated_by uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
    created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT statement_timestamp()
);
CREATE TABLE identity.operator_authorities (
    id uuid PRIMARY KEY CHECK (id <> '00000000-0000-0000-0000-000000000000'::uuid),
    database_login name NOT NULL REFERENCES identity.operator_principals(database_login) ON DELETE RESTRICT,
    command text NOT NULL,
    scope_kind text NOT NULL CHECK (scope_kind IN ('platform','organization')),
    org_id uuid CHECK (org_id <> '00000000-0000-0000-0000-000000000000'::uuid),
    application_id text CHECK (application_id IS NULL),
    target_account_id uuid CHECK (target_account_id <> '00000000-0000-0000-0000-000000000000'::uuid),
    enabled boolean NOT NULL DEFAULT false,
    revision bigint NOT NULL DEFAULT 1 CHECK (revision > 0),
    created_by uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
    updated_by uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
    created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    CHECK ((scope_kind = 'platform' AND org_id IS NULL
            AND command IN ('actor.register_system','account_actor.ensure'))
        OR (scope_kind = 'organization' AND org_id IS NOT NULL
            AND command IN ('membership.join','membership.retire','membership.join_owner'))),
    CHECK (command <> 'actor.register_system' OR target_account_id IS NULL),
    UNIQUE NULLS NOT DISTINCT (database_login,command,scope_kind,org_id,application_id,target_account_id)
);
CREATE FUNCTION identity.guard_operator_authority() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp AS $authority_guard$
BEGIN
    IF current_user <> 'identity_migrator' THEN
        RAISE EXCEPTION USING ERRCODE='42501', MESSAGE='identity_operator_owner_required';
    END IF;
    IF TG_OP IN ('DELETE','TRUNCATE') THEN
        RAISE EXCEPTION USING ERRCODE='23514', MESSAGE='identity_operator_history_retained';
    END IF;
    IF TG_OP = 'INSERT' THEN
        NEW.revision := 1;
        NEW.created_at := statement_timestamp(); NEW.updated_at := NEW.created_at;
        NEW.updated_by := NEW.created_by;
        RETURN NEW;
    END IF;
    IF NEW.database_login IS DISTINCT FROM OLD.database_login
       OR NEW.created_by IS DISTINCT FROM OLD.created_by OR NEW.created_at IS DISTINCT FROM OLD.created_at
       OR (TG_TABLE_NAME = 'operator_principals' AND
           to_jsonb(NEW)->'executor_actor_id' IS DISTINCT FROM to_jsonb(OLD)->'executor_actor_id')
       OR (TG_TABLE_NAME = 'operator_authorities' AND
           (to_jsonb(NEW) - ARRAY['enabled','revision','updated_by','updated_at']) IS DISTINCT FROM
           (to_jsonb(OLD) - ARRAY['enabled','revision','updated_by','updated_at'])) THEN
        RAISE EXCEPTION USING ERRCODE='23514', MESSAGE='identity_operator_identity_immutable';
    END IF;
    IF NEW.enabled IS DISTINCT FROM OLD.enabled THEN
        IF OLD.revision = 9223372036854775807 THEN
            RAISE EXCEPTION USING ERRCODE='23514', MESSAGE='identity_operator_revision_exhausted';
        END IF;
        NEW.revision := OLD.revision + 1; NEW.updated_at := statement_timestamp();
    ELSE
        NEW.revision := OLD.revision; NEW.updated_at := OLD.updated_at; NEW.updated_by := OLD.updated_by;
    END IF;
    RETURN NEW;
END;
$authority_guard$;
CREATE TRIGGER operator_principals_guard BEFORE INSERT OR UPDATE OR DELETE ON identity.operator_principals
FOR EACH ROW EXECUTE FUNCTION identity.guard_operator_authority();
CREATE TRIGGER operator_principals_retention BEFORE TRUNCATE ON identity.operator_principals
FOR EACH STATEMENT EXECUTE FUNCTION identity.guard_operator_authority();
CREATE TRIGGER operator_authorities_guard BEFORE INSERT OR UPDATE OR DELETE ON identity.operator_authorities
FOR EACH ROW EXECUTE FUNCTION identity.guard_operator_authority();
CREATE TRIGGER operator_authorities_retention BEFORE TRUNCATE ON identity.operator_authorities
FOR EACH STATEMENT EXECUTE FUNCTION identity.guard_operator_authority();
CREATE FUNCTION identity.current_operator_authority(command_type text, scope_kind text, org_id uuid, target_account_id uuid)
RETURNS TABLE (executor_actor_id uuid, principal_revision bigint, authority_id uuid, authority_revision bigint)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pg_catalog, pg_temp
AS $authority_read$
    SELECT principal.executor_actor_id, principal.revision, authority.id, authority.revision
    FROM identity.operator_principals AS principal
    JOIN identity.operator_authorities AS authority ON authority.database_login = principal.database_login
    WHERE principal.database_login = session_user AND principal.enabled AND authority.enabled
      AND authority.command = $1 AND authority.scope_kind = $2 AND authority.org_id IS NOT DISTINCT FROM $3
      AND authority.application_id IS NULL
      AND ($4 IS NULL OR $4 <> '00000000-0000-0000-0000-000000000000'::uuid)
      AND (authority.target_account_id IS NULL OR authority.target_account_id = $4)
      AND (($1 = 'actor.register_system' AND $2 = 'platform' AND $3 IS NULL AND $4 IS NULL)
        OR ($1 = 'account_actor.ensure' AND $2 = 'platform' AND $3 IS NULL AND $4 IS NOT NULL)
        OR ($1 IN ('membership.join','membership.retire','membership.join_owner') AND $2 = 'organization'
            AND $3 IS NOT NULL AND $3 <> '00000000-0000-0000-0000-000000000000'::uuid AND $4 IS NOT NULL))
    ORDER BY authority.id LIMIT 1;
$authority_read$;
-- Strip every inherited default ACL, including unexpected named grantees, before exact grants.
DO $authority_acl$
DECLARE relation record; routine record; granted record; grantee_name text;
BEGIN
    FOR relation IN SELECT c.oid,c.relowner,c.relacl,c.oid::regclass AS name
        FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname='identity' AND c.relname IN ('operator_principals','operator_authorities')
    LOOP
        EXECUTE format('REVOKE ALL ON TABLE %s FROM PUBLIC',relation.name);
        FOR granted IN SELECT DISTINCT a.grantee FROM aclexplode(relation.relacl) a WHERE a.grantee<>relation.relowner LOOP
            grantee_name := CASE WHEN granted.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(granted.grantee)) END;
            EXECUTE format('REVOKE ALL ON TABLE %s FROM %s',relation.name,grantee_name);
        END LOOP;
    END LOOP;
    FOR routine IN SELECT p.proowner,p.proacl,p.oid::regprocedure AS signature
        FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
        WHERE n.nspname='identity' AND p.proname IN ('guard_operator_authority','current_operator_authority')
    LOOP
        EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',routine.signature);
        FOR granted IN SELECT DISTINCT a.grantee FROM aclexplode(routine.proacl) a WHERE a.grantee<>routine.proowner LOOP
            grantee_name := CASE WHEN granted.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(granted.grantee)) END;
            EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %s',routine.signature,grantee_name);
        END LOOP;
    END LOOP;
END;
$authority_acl$;
GRANT USAGE ON SCHEMA identity TO identity_operator, identity_operator_authority_owner;
GRANT SELECT (database_login,executor_actor_id,enabled,revision) ON identity.operator_principals TO identity_operator_authority_owner;
GRANT SELECT (id,database_login,command,scope_kind,org_id,application_id,target_account_id,enabled,revision) ON identity.operator_authorities TO identity_operator_authority_owner;
GRANT EXECUTE ON FUNCTION identity.current_operator_authority(text,text,uuid,uuid) TO identity_operator;
GRANT CREATE ON SCHEMA identity TO identity_operator_authority_owner;
ALTER FUNCTION identity.current_operator_authority(text,text,uuid,uuid) OWNER TO identity_operator_authority_owner;
REVOKE CREATE ON SCHEMA identity FROM identity_operator_authority_owner;
"""


def upgrade():
    connection=op.get_bind()
    verify_authority_roles(connection,staged=True)
    connection.execute(text(AUTHORITY_SCHEMA_SQL))


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
