-- Explicit administrator preparation, never API startup or a runtime command.
-- No passwords, service actors, principal mappings, accounts or grants are seeded.
BEGIN;
DO $studies_roles$
DECLARE name text; owner_name text;
BEGIN
 IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=current_user AND rolsuper) THEN
  RAISE EXCEPTION 'studies_role_administrator_required';END IF;
 IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname IN ('identity_studies_owner','identity_studies_reader_runtime',
 'identity_studies_setup_runtime','access_studies_owner','access_studies_runtime')) THEN
  RAISE EXCEPTION 'studies_roles_already_present_requires_owner_verification';END IF;
 FOR owner_name IN SELECT unnest(ARRAY['identity_migrator','access_migrator']) LOOP
  IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=owner_name AND rolcanlogin
   AND NOT (rolsuper OR rolinherit OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls)) THEN
   RAISE EXCEPTION 'studies_migrator_role_unsafe';END IF;
 END LOOP;
 FOREACH name IN ARRAY ARRAY['identity_studies_owner','access_studies_owner'] LOOP
  EXECUTE format('CREATE ROLE %I NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS',name);
  owner_name:=split_part(name,'_',1)||'_migrator';
  EXECUTE format('GRANT %I TO %I WITH ADMIN FALSE, INHERIT FALSE, SET TRUE',name,owner_name);
 END LOOP;
 FOREACH name IN ARRAY ARRAY['identity_studies_reader_runtime','identity_studies_setup_runtime','access_studies_runtime'] LOOP
  EXECUTE format('CREATE ROLE %I LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS',name);
 END LOOP;
END $studies_roles$;
COMMIT;
