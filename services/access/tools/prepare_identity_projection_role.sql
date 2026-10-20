-- Controlled deployment administrator only. This delivery executes it solely on
-- its isolated synthetic target. Existing/unsafe roles are never silently repaired.
BEGIN;
CREATE ROLE identity_account_projection_owner NOLOGIN NOINHERIT NOSUPERUSER
    NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
-- PostgreSQL 15 has role-level inheritance and implicit SET ROLE membership.
-- Later versions provide explicit per-membership options. Never weaken the
-- migration login's existing role flags to accommodate preparation.
DO $prepare_membership$
BEGIN
    IF current_setting('server_version_num')::integer >= 160000 THEN
        EXECUTE 'GRANT identity_account_projection_owner TO identity_migrator WITH ADMIN FALSE, INHERIT FALSE, SET TRUE';
    ELSE
        IF (SELECT rolinherit FROM pg_roles WHERE rolname = 'identity_migrator') THEN
            RAISE EXCEPTION 'identity_projection_role_unsafe';
        END IF;
        GRANT identity_account_projection_owner TO identity_migrator;
    END IF;
END;
$prepare_membership$;
COMMIT;
