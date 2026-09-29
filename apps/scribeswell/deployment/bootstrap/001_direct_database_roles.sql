-- Operator-applied expansion before activation, never API startup.
-- No passwords here: provision role credentials through the approved secret channel.
-- Preserves existing anon/authenticated/service_role grants and stored views/data.
BEGIN;
SET LOCAL lock_timeout = '3s';
SET LOCAL statement_timeout = '30s';
SELECT pg_advisory_xact_lock(hashtext('scribeswell-direct-database-bootstrap'));
DO $$
DECLARE role_name text; role_oid oid;
BEGIN
  FOREACH role_name IN ARRAY ARRAY['scribeswell_runtime', 'scribeswell_import'] LOOP
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = role_name) THEN
      EXECUTE format('CREATE ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS', role_name);
    END IF;
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = role_name AND
      (rolsuper OR rolcreatedb OR rolcreaterole OR rolinherit OR rolbypassrls OR rolreplication OR NOT rolcanlogin)) OR
      EXISTS (SELECT FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.member WHERE r.rolname=role_name) THEN
      RAISE EXCEPTION 'Unsafe existing Scribeswell role configuration';
    END IF;
    SELECT oid INTO role_oid FROM pg_roles WHERE rolname=role_name;
    -- Existing names must not silently retain owner or cross-owner authority.
    IF EXISTS (SELECT FROM pg_class c JOIN pg_roles r ON r.oid=c.relowner WHERE r.rolname=role_name)
      OR EXISTS (SELECT FROM pg_namespace n JOIN pg_roles r ON r.oid=n.nspowner WHERE r.rolname=role_name)
      OR EXISTS (
        SELECT FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
          AND n.nspname NOT LIKE 'pg_toast%' AND n.nspname NOT LIKE 'pg_temp%'
          AND c.relkind IN ('r','p','v','m','f')
          AND (
            (n.nspname <> 'scribeswell' AND (
              (has_schema_privilege(role_name,n.oid,'USAGE') AND has_table_privilege(role_name,c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER'))
              OR EXISTS (SELECT FROM aclexplode(c.relacl) a WHERE a.grantee=role_oid)
            ))
            OR (n.nspname = 'scribeswell' AND has_table_privilege(role_name,c.oid,
              CASE WHEN role_name='scribeswell_runtime' THEN 'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER'
                   ELSE 'DELETE,TRUNCATE,REFERENCES,TRIGGER' END))
          )
      )
      OR EXISTS (SELECT FROM pg_proc WHERE proowner=role_oid)
      OR EXISTS (
        SELECT FROM pg_namespace n, LATERAL aclexplode(n.nspacl) a
        WHERE a.grantee=role_oid AND (a.privilege_type='CREATE' OR a.is_grantable)
      )
      OR EXISTS (
        SELECT FROM pg_attribute col JOIN pg_class c ON c.oid=col.attrelid
          JOIN pg_namespace n ON n.oid=c.relnamespace,
          LATERAL aclexplode(col.attacl) a
        WHERE a.grantee=role_oid AND (a.is_grantable OR NOT (
          n.nspname='scribeswell' AND (
            (role_name='scribeswell_runtime' AND c.relname IN ('book','chapter','verse','word','morpheme','book_read','chapter_read','verse_read','word_read','morpheme_read') AND a.privilege_type='SELECT')
            OR (role_name='scribeswell_import' AND c.relname IN ('book','chapter','verse','word','morpheme') AND a.privilege_type IN ('SELECT','INSERT','UPDATE'))
          )
        ))
      )
      OR EXISTS (
        SELECT FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace,
          LATERAL aclexplode(c.relacl) a
        WHERE c.relkind='S' AND a.grantee=role_oid AND (a.is_grantable OR NOT (
          role_name='scribeswell_import' AND n.nspname='scribeswell'
          AND c.relname IN ('chapter_id_seq','verse_id_seq','word_id_seq','morpheme_id_seq')
          AND a.privilege_type='USAGE'
        ))
      )
      OR EXISTS (
        SELECT FROM pg_proc p, LATERAL aclexplode(p.proacl) a
        WHERE p.prosecdef AND a.grantee=role_oid AND a.privilege_type='EXECUTE'
      ) THEN
      RAISE EXCEPTION 'Unexpected existing Scribeswell authority';
    END IF;
    EXECUTE format('ALTER ROLE %I SET statement_timeout = %L', role_name, '15s');
    EXECUTE format('ALTER ROLE %I SET lock_timeout = %L', role_name, '3s');
    EXECUTE format('ALTER ROLE %I SET idle_in_transaction_session_timeout = %L', role_name, '15s');
  END LOOP;
END $$;
GRANT USAGE ON SCHEMA scribeswell TO scribeswell_runtime, scribeswell_import;
GRANT SELECT ON scribeswell.book, scribeswell.chapter, scribeswell.verse,
  scribeswell.word, scribeswell.morpheme, scribeswell.book_read,
  scribeswell.chapter_read, scribeswell.verse_read, scribeswell.word_read,
  scribeswell.morpheme_read TO scribeswell_runtime;
GRANT SELECT, INSERT, UPDATE ON scribeswell.book, scribeswell.chapter,
  scribeswell.verse, scribeswell.word, scribeswell.morpheme TO scribeswell_import;
GRANT USAGE ON SEQUENCE scribeswell.chapter_id_seq, scribeswell.verse_id_seq,
  scribeswell.word_id_seq, scribeswell.morpheme_id_seq TO scribeswell_import;
DO $$
DECLARE table_name text;
BEGIN
  FOREACH table_name IN ARRAY ARRAY['book', 'chapter', 'verse', 'word', 'morpheme'] LOOP
    EXECUTE format('DROP POLICY IF EXISTS direct_read ON scribeswell.%I', table_name);
    EXECUTE format('CREATE POLICY direct_read ON scribeswell.%I FOR SELECT TO scribeswell_runtime, scribeswell_import USING (true)', table_name);
    EXECUTE format('DROP POLICY IF EXISTS direct_insert ON scribeswell.%I', table_name);
    EXECUTE format('CREATE POLICY direct_insert ON scribeswell.%I FOR INSERT TO scribeswell_import WITH CHECK (true)', table_name);
    EXECUTE format('DROP POLICY IF EXISTS direct_update ON scribeswell.%I', table_name);
    EXECUTE format('CREATE POLICY direct_update ON scribeswell.%I FOR UPDATE TO scribeswell_import USING (true) WITH CHECK (true)', table_name);
  END LOOP;
END $$;
COMMIT;
