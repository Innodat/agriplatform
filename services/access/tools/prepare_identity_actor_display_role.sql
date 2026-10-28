-- Explicit controlled prerequisite before Identity28. Existing names fail closed.
-- Supply a synthetic or authorized runtime password separately, never in this file.
CREATE ROLE identity_actor_display_runtime LOGIN NOINHERIT NOSUPERUSER NOCREATEDB
 NOCREATEROLE NOREPLICATION NOBYPASSRLS;
-- CONNECT is normally inherited from PUBLIC; the deployment administrator grants
-- CONNECT on the selected database separately if its default policy revokes it.
