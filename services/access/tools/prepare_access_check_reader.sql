-- Controlled true-administrator preparation only. Existing names refuse without repair.
BEGIN;
DO $check_reader_preparation_admin$
BEGIN
    IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user) THEN
        RAISE EXCEPTION USING ERRCODE='42501', MESSAGE='access_check_reader_preparation_admin_required';
    END IF;
END;
$check_reader_preparation_admin$;
CREATE ROLE access_check_reader NOLOGIN NOINHERIT NOSUPERUSER
    NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
COMMIT;
