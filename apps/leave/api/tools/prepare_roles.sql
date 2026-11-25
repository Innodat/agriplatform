-- Owner seed. Protected setup only; never run during API startup.
-- Supply LOGIN passwords separately using protected operator custody.
CREATE ROLE leave_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
CREATE ROLE leave_migrator LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
CREATE ROLE leave_runtime LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
CREATE SCHEMA leave AUTHORIZATION leave_owner;
GRANT USAGE,CREATE ON SCHEMA leave TO leave_migrator;
GRANT USAGE ON SCHEMA leave TO leave_runtime;
-- Migrator objects become owned by the nonlogin owner through controlled setup
-- after upgrade; grant that membership only to the migrator, never runtime.
GRANT leave_owner TO leave_migrator;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- Choices protected setup; never grant owner membership to the operator.
CREATE ROLE leave_command_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
CREATE ROLE leave_operator LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
GRANT leave_command_owner TO leave_owner;
GRANT USAGE,CREATE ON SCHEMA leave TO leave_command_owner;
GRANT USAGE ON SCHEMA leave TO leave_operator;
-- Revoke command_owner schema CREATE after controlled migration. Bootstrap principal
-- and exact authorities through protected owner custody using an existing actor.
