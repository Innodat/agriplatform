-- Controlled true-superuser preparation only; refuse existing names atomically.
BEGIN;
DO $admin$
BEGIN
 IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user) THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_command_preparation_admin_required';
 END IF;
END $admin$;
CREATE ROLE identity_command_owner NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB
 NOCREATEROLE NOREPLICATION NOBYPASSRLS;
DO $membership$
BEGIN
 IF current_setting('server_version_num')::integer>=160000 THEN
  EXECUTE 'GRANT identity_command_owner TO identity_migrator WITH ADMIN FALSE, INHERIT FALSE, SET TRUE';
 ELSE
  IF (SELECT rolinherit FROM pg_roles WHERE rolname='identity_migrator') THEN
   RAISE EXCEPTION 'identity_command_role_unsafe';
  END IF;
  GRANT identity_command_owner TO identity_migrator;
 END IF;
END $membership$;
COMMIT;
