-- Controlled true-superuser preparation; existing names refuse without repair.
BEGIN;
DO $admin$
BEGIN
 IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user) THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_account_verification_preparation_admin_required'; END IF;
END $admin$;
CREATE ROLE identity_account_verification_owner NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB
 NOCREATEROLE NOREPLICATION NOBYPASSRLS;
GRANT identity_account_verification_owner TO identity_migrator WITH ADMIN FALSE, INHERIT FALSE, SET TRUE;
COMMIT;
