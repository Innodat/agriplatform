-- Run only against an explicitly chosen new/disposable database using bootstrap authority.
-- Does not touch legacy application objects, passwords, grants or production memberships.
CREATE ROLE pts_migrator NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE pts_runtime NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE pts_import NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE access_migrator NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE access_runtime NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE content_migrator NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE content_runtime NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE SCHEMA pts AUTHORIZATION pts_migrator;
CREATE SCHEMA access AUTHORIZATION access_migrator;
CREATE SCHEMA content AUTHORIZATION content_migrator;
REVOKE ALL ON SCHEMA pts,access,content FROM PUBLIC;
GRANT USAGE ON SCHEMA pts TO pts_runtime,pts_import;
GRANT USAGE ON SCHEMA access TO access_runtime;
GRANT USAGE ON SCHEMA content TO content_runtime;
-- Access owns the compatibility bridge to current legacy identity membership.
-- Apply access/tools/identity_bridge.sql through the identity owner's deployment.
