-- Controlled deployment administrator only, separately authorized target preparation.
-- Existing roles cause refusal; migration verifies their full flags, memberships,
-- effective privileges and dependencies. Never silently repair an existing role.
BEGIN;
DO $target_preparation_admin$
BEGIN
    IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user) THEN
        RAISE EXCEPTION USING ERRCODE='42501', MESSAGE='identity_target_preparation_admin_required';
    END IF;
END;
$target_preparation_admin$;
CREATE ROLE identity_target_projection_owner NOLOGIN NOINHERIT NOSUPERUSER
    NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE access_target_reader NOLOGIN NOINHERIT NOSUPERUSER
    NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE access_setup_target_reader NOLOGIN NOINHERIT NOSUPERUSER
    NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE access_command_owner NOLOGIN NOINHERIT NOSUPERUSER
    NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
-- Only the Identity definer is assumable by its migrator, SET-only, no ADMIN.
DO $prepare_target_membership$
BEGIN
    IF current_setting('server_version_num')::integer >= 160000 THEN
        EXECUTE 'GRANT identity_target_projection_owner TO identity_migrator WITH ADMIN FALSE, INHERIT FALSE, SET TRUE';
    ELSE
        IF (SELECT rolinherit FROM pg_roles WHERE rolname='identity_migrator') THEN
            RAISE EXCEPTION 'identity_target_role_unsafe';
        END IF;
        GRANT identity_target_projection_owner TO identity_migrator;
    END IF;
END;
$prepare_target_membership$;
COMMIT;
