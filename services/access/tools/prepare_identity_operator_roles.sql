-- Controlled deployment administrator, separate from migrations. New roles only;
-- existing names fail atomically rather than being repaired or granted authority.
BEGIN;
DO $prepare_administrator$
BEGIN
    IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user) THEN
        RAISE EXCEPTION USING ERRCODE='42501', MESSAGE='identity_authority_preparation_admin_required';
    END IF;
END;
$prepare_administrator$;
CREATE ROLE identity_operator LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE
    NOREPLICATION NOBYPASSRLS;
CREATE ROLE identity_operator_authority_owner NOLOGIN NOINHERIT NOSUPERUSER
    NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
DO $prepare_membership$
BEGIN
    IF current_setting('server_version_num')::integer >= 160000 THEN
        EXECUTE 'GRANT identity_operator_authority_owner TO identity_migrator WITH ADMIN FALSE, INHERIT FALSE, SET TRUE';
    ELSE
        IF (SELECT rolinherit FROM pg_roles WHERE rolname='identity_migrator') THEN
            RAISE EXCEPTION 'identity_authority_role_unsafe';
        END IF;
        GRANT identity_operator_authority_owner TO identity_migrator;
    END IF;
END;
$prepare_membership$;
COMMIT;
