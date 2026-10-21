-- Explicit true-superuser preparation; names must be absent. No authority seeds.
BEGIN;
DO $admin$
BEGIN
 IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user) THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_preparation_admin_required';
 END IF;
END $admin$;
CREATE ROLE access_operator LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE access_operator_authority_owner NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
DO $command_owner$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='access_command_owner') THEN
  CREATE ROLE access_command_owner NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
 ELSIF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='access_command_owner' AND NOT rolcanlogin AND NOT rolinherit AND NOT rolsuper AND NOT rolcreatedb AND NOT rolcreaterole AND NOT rolreplication AND NOT rolbypassrls)
 OR EXISTS(SELECT 1 FROM pg_auth_members WHERE member='access_command_owner'::regrole OR roleid='access_command_owner'::regrole) THEN
  RAISE EXCEPTION 'access_preexisting_command_owner_unsafe';
 END IF;
END $command_owner$;
DO $edges$
BEGIN
 IF current_setting('server_version_num')::integer >= 160000 THEN
  EXECUTE 'GRANT access_operator_authority_owner,access_command_owner TO access_migrator WITH ADMIN FALSE, INHERIT FALSE, SET TRUE';
 ELSE
  IF (SELECT rolinherit FROM pg_roles WHERE rolname='access_migrator') THEN
   RAISE EXCEPTION 'access_preparation_unsafe_migrator';
  END IF;
  GRANT access_operator_authority_owner,access_command_owner TO access_migrator;
 END IF;
END $edges$;
COMMIT;
