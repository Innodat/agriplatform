"""Add durable attribution structure; no account adoption or authority is activated."""
from alembic import op
from sqlalchemy import text

revision = 'identity_0002'
down_revision = 'identity_0001'
branch_labels = None
depends_on = None

# Also executed independently, rollback-only, by the synthetic reference recorder.
# No business seeds, external identities or caller-selectable runtime actor context.
ACTOR_SCHEMA_SQL = r"""
CREATE TABLE identity.actor (
    id uuid PRIMARY KEY CHECK (id <> '00000000-0000-0000-0000-000000000000'::uuid),
    kind text NOT NULL CHECK (kind IN ('account', 'system', 'service')),
    display_name text NOT NULL CHECK (
        char_length(display_name) BETWEEN 1 AND 200
        AND char_length(btrim(display_name, U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000')) > 0),
    actor_key text UNIQUE CHECK (
        actor_key COLLATE "C" ~ '^[a-z][a-z0-9_.:-]{0,127}$'),
    created_by uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
    updated_by uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
    created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (id, kind)
);
CREATE TABLE identity.account_actor (
    account_id uuid PRIMARY KEY CHECK (account_id <> '00000000-0000-0000-0000-000000000000'::uuid),
    actor_id uuid NOT NULL UNIQUE,
    actor_kind text NOT NULL CHECK (actor_kind = 'account'),
    created_by uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
    created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    FOREIGN KEY (actor_id, actor_kind) REFERENCES identity.actor(id, kind) ON DELETE RESTRICT
);

CREATE FUNCTION identity.guard_actor() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp AS $actor_guard$
BEGIN
    -- No application command exists yet. Attribution below is explicit deployment
    -- fixture input from the actual owner, never a browser payload or actor GUC.
    IF current_user <> 'identity_migrator' THEN
        RAISE EXCEPTION USING ERRCODE = '42501', MESSAGE = 'identity_actor_owner_required';
    END IF;
    IF TG_OP IN ('DELETE', 'TRUNCATE') THEN
        RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'identity_actor_history_retained';
    END IF;
    IF TG_OP = 'INSERT' THEN
        NEW.created_at := statement_timestamp();
        NEW.updated_at := NEW.created_at;
        NEW.updated_by := NEW.created_by;
        RETURN NEW;
    END IF;
    IF NEW.id IS DISTINCT FROM OLD.id
       OR NEW.kind IS DISTINCT FROM OLD.kind
       OR NEW.created_by IS DISTINCT FROM OLD.created_by
       OR NEW.created_at IS DISTINCT FROM OLD.created_at
       OR (OLD.actor_key IS NOT NULL AND NEW.actor_key IS DISTINCT FROM OLD.actor_key) THEN
        RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'identity_actor_identity_immutable';
    END IF;
    IF NEW.display_name IS DISTINCT FROM OLD.display_name OR NEW.actor_key IS DISTINCT FROM OLD.actor_key THEN
        -- NEW.updated_by must identify an existing actor, supplied explicitly by
        -- the deployment owner. Controlled execution derivation is a later gate.
        NEW.updated_at := statement_timestamp();
    ELSE
        NEW.updated_by := OLD.updated_by;
        NEW.updated_at := OLD.updated_at;
    END IF;
    RETURN NEW;
END;
$actor_guard$;
CREATE TRIGGER actor_guard BEFORE INSERT OR UPDATE OR DELETE ON identity.actor
FOR EACH ROW EXECUTE FUNCTION identity.guard_actor();
CREATE TRIGGER actor_retention BEFORE TRUNCATE ON identity.actor
FOR EACH STATEMENT EXECUTE FUNCTION identity.guard_actor();

CREATE FUNCTION identity.guard_account_actor() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp AS $mapping_guard$
BEGIN
    IF current_user <> 'identity_migrator' THEN
        RAISE EXCEPTION USING ERRCODE = '42501', MESSAGE = 'identity_actor_owner_required';
    END IF;
    IF TG_OP <> 'INSERT' THEN
        RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'identity_account_actor_immutable';
    END IF;
    NEW.created_at := statement_timestamp();
    RETURN NEW;
END;
$mapping_guard$;
CREATE TRIGGER account_actor_guard BEFORE INSERT OR UPDATE OR DELETE ON identity.account_actor
FOR EACH ROW EXECUTE FUNCTION identity.guard_account_actor();
CREATE TRIGGER account_actor_retention BEFORE TRUNCATE ON identity.account_actor
FOR EACH STATEMENT EXECUTE FUNCTION identity.guard_account_actor();

-- Legacy default privileges remain untouched for old consumers, but are stripped
-- from every new object for ALL grantees, not merely known browser role names.
DO $restricted_actor_objects$
DECLARE object_name text; grantee_name text; granted_role record;
BEGIN
    FOREACH object_name IN ARRAY ARRAY['actor', 'account_actor'] LOOP
        FOR granted_role IN
            SELECT DISTINCT a.grantee FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            CROSS JOIN LATERAL aclexplode(c.relacl) a
            WHERE n.nspname = 'identity' AND c.relname = object_name AND a.grantee <> c.relowner
        LOOP
            grantee_name := CASE WHEN granted_role.grantee = 0 THEN 'PUBLIC'
                ELSE quote_ident(pg_get_userbyid(granted_role.grantee)) END;
            EXECUTE format('REVOKE ALL ON TABLE identity.%I FROM %s', object_name, grantee_name);
        END LOOP;
    END LOOP;
    FOREACH object_name IN ARRAY ARRAY['guard_actor', 'guard_account_actor'] LOOP
        -- NULL proacl means PUBLIC EXECUTE; explicitly remove it as well.
        EXECUTE format('REVOKE ALL ON FUNCTION identity.%I() FROM PUBLIC', object_name);
        FOR granted_role IN
            SELECT DISTINCT a.grantee FROM pg_proc p
            JOIN pg_namespace n ON n.oid = p.pronamespace
            CROSS JOIN LATERAL aclexplode(p.proacl) a
            WHERE n.nspname = 'identity' AND p.proname = object_name AND a.grantee <> p.proowner
        LOOP
            grantee_name := CASE WHEN granted_role.grantee = 0 THEN 'PUBLIC'
                ELSE quote_ident(pg_get_userbyid(granted_role.grantee)) END;
            EXECUTE format('REVOKE ALL ON FUNCTION identity.%I() FROM %s', object_name, grantee_name);
        END LOOP;
    END LOOP;
END;
$restricted_actor_objects$;
"""


def upgrade():
    op.get_bind().execute(text(ACTOR_SCHEMA_SQL))


def downgrade():
    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
