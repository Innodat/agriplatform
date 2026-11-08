-- Controlled owner/bootstrap prerequisite, never API/worker startup.
-- Provision unique environment credentials separately; retain predecessor roles.
CREATE ROLE pts_account_runtime NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE pts_corpus_import NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
GRANT USAGE ON SCHEMA pts TO pts_account_runtime,pts_corpus_import;
