-- Explicit true-administrator preparation on an authorized target; no default password.
-- Existing names refuse. No grants, memberships, mappings, users or app authority.
BEGIN;
DO $preferences_admin$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=current_user AND rolsuper) THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_preferences_preparation_admin_required';END IF;
END $preferences_admin$;
CREATE ROLE identity_preferences_runtime LOGIN NOINHERIT NOSUPERUSER NOCREATEDB
 NOCREATEROLE NOREPLICATION NOBYPASSRLS;
COMMIT;
