-- Explicit administrator preparation only. Refuse existing roles; no credentials or seeds.
BEGIN;
CREATE ROLE scribeswell_studies_migrator LOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE scribeswell_studies_runtime LOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE scribeswell_studies_operator NOLOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOREPLICATION;
-- Cluster owner must remove inherited database DDL authority before preparation.
-- Refuse instead of altering permissions belonging to other database consumers.
DO $$ BEGIN
 IF has_database_privilege('scribeswell_studies_runtime',current_database(),'CREATE') OR has_database_privilege('scribeswell_studies_runtime',current_database(),'TEMP') THEN
  RAISE EXCEPTION 'Restricted database privilege preparation required';
 END IF;
END $$;
CREATE SCHEMA scribeswell_studies AUTHORIZATION scribeswell_studies_migrator;
REVOKE ALL ON SCHEMA scribeswell_studies FROM PUBLIC;
GRANT USAGE ON SCHEMA scribeswell_studies TO scribeswell_studies_runtime;
COMMIT;
