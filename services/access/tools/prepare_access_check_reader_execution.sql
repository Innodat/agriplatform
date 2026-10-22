-- Controlled true-administrator preparation of only the exact reader SET edge.
BEGIN;
DO $reader_execution$
BEGIN
 IF NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user) THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='access_check_reader_preparation_admin_required';
 END IF;
 -- Validate the receiving login and every assumption path before adding authority.
 IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='access_migrator' AND rolcanlogin
     AND NOT rolsuper AND NOT rolcreatedb AND NOT rolcreaterole AND NOT rolreplication AND NOT rolbypassrls)
 OR has_database_privilege('access_migrator',current_database(),'CREATE')
 OR (current_setting('server_version_num')::integer < 160000
     AND (SELECT rolinherit FROM pg_roles WHERE rolname='access_migrator')) THEN
  RAISE EXCEPTION 'access_check_reader_migrator_unsafe';
 END IF;
 -- The only outgoing memberships are the existing two noninherited SET-only owners.
 IF (SELECT count(*) FROM pg_auth_members WHERE member='access_migrator'::regrole)<>2
 OR (SELECT count(DISTINCT roleid) FROM pg_auth_members WHERE member='access_migrator'::regrole)<>2
 OR EXISTS(SELECT 1 FROM pg_auth_members m WHERE member='access_migrator'::regrole AND
     (pg_get_userbyid(roleid) NOT IN ('access_operator_authority_owner','access_command_owner')
      OR admin_option
      OR coalesce((to_jsonb(m)->>'inherit_option')::boolean,(SELECT rolinherit FROM pg_roles WHERE oid=m.member))
      OR NOT coalesce((to_jsonb(m)->>'set_option')::boolean,true))) THEN
  RAISE EXCEPTION 'access_check_reader_migrator_unsafe';
 END IF;
 -- Non-native targets have no incoming edges. Native Supabase retains exactly its
 -- independently verified ADMIN-only and SET-only postgres edges and role profiles.
 IF EXISTS(SELECT 1 FROM pg_auth_members WHERE roleid='access_migrator'::regrole) THEN
  IF (SELECT count(*) FROM pg_auth_members WHERE roleid='access_migrator'::regrole)<>2
  OR EXISTS(SELECT 1 FROM pg_auth_members m WHERE roleid='access_migrator'::regrole
      AND (pg_get_userbyid(member),pg_get_userbyid(grantor),admin_option,
        coalesce((to_jsonb(m)->>'inherit_option')::boolean,(SELECT rolinherit FROM pg_roles WHERE oid=m.member)),
        coalesce((to_jsonb(m)->>'set_option')::boolean,true)) NOT IN (
          ('postgres','supabase_admin',true,false,false),('postgres','postgres',false,false,true)))
  OR NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='postgres' AND rolcanlogin AND NOT rolsuper
      AND rolcreatedb AND rolcreaterole AND rolreplication AND rolbypassrls AND rolinherit)
  OR NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='supabase_admin' AND rolcanlogin AND rolsuper
      AND rolcreatedb AND rolcreaterole AND rolreplication AND rolbypassrls AND rolinherit) THEN
   RAISE EXCEPTION 'access_check_reader_migrator_unsafe';
  END IF;
 END IF;
 -- Preserve Access's existing refusal of foreign Identity write/read/definer rights.
 IF EXISTS(SELECT 1 FROM pg_namespace WHERE nspname='identity' AND has_schema_privilege('access_migrator',oid,'CREATE'))
 OR EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
     WHERE n.nspname='identity' AND p.prosecdef AND has_schema_privilege('access_migrator',n.oid,'USAGE')
       AND has_function_privilege('access_migrator',p.oid,'EXECUTE'))
 OR EXISTS(SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
     WHERE n.nspname='identity' AND c.relkind IN ('r','p','v','m','S')
       AND (pg_get_userbyid(c.relowner)='access_migrator'
         OR has_table_privilege('access_migrator',c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
         OR has_any_column_privilege('access_migrator',c.oid,'SELECT,INSERT,UPDATE,REFERENCES'))) THEN
  RAISE EXCEPTION 'access_check_reader_migrator_unsafe';
 END IF;
 IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='access_check_reader' AND NOT rolcanlogin AND NOT rolinherit AND NOT rolsuper AND NOT rolcreatedb AND NOT rolcreaterole AND NOT rolreplication AND NOT rolbypassrls)
 OR EXISTS(SELECT 1 FROM pg_auth_members WHERE roleid='access_check_reader'::regrole OR member='access_check_reader'::regrole) THEN
  RAISE EXCEPTION 'access_check_reader_preparation_unsafe';
 END IF;
 -- Before changing the role graph, require precisely the retained Identity20 bridge.
 IF (SELECT count(*) FROM pg_shdepend s WHERE s.refclassid='pg_authid'::regclass
     AND s.refobjid='access_check_reader'::regrole AND s.deptype IN ('a','o','r')
     AND s.dbid IN (0,(SELECT oid FROM pg_database WHERE datname=current_database())))<>2
 OR EXISTS(SELECT 1 FROM pg_shdepend s WHERE s.refclassid='pg_authid'::regclass
     AND s.refobjid='access_check_reader'::regrole AND s.deptype IN ('a','o','r')
     AND s.dbid IN (0,(SELECT oid FROM pg_database WHERE datname=current_database()))
     AND NOT ((s.classid='pg_namespace'::regclass AND s.deptype='a' AND pg_describe_object(s.classid,s.objid,s.objsubid)='schema identity')
       OR (s.classid='pg_proc'::regclass AND s.deptype='a' AND pg_describe_object(s.classid,s.objid,s.objsubid)='function identity.current_account_organization()')))
 OR EXISTS(SELECT 1 FROM pg_namespace n CROSS JOIN unnest(ARRAY['USAGE','CREATE','USAGE WITH GRANT OPTION','CREATE WITH GRANT OPTION']) p
     WHERE nspname !~ '^pg_' AND nspname<>'information_schema' AND has_schema_privilege('access_check_reader',n.oid,p)
     AND NOT (nspname IN ('public','identity') AND p='USAGE'))
 OR has_database_privilege('access_check_reader',current_database(),'CREATE')
 OR EXISTS(SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
     WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND
       ((c.relkind IN ('r','p','v','m','f') AND (has_table_privilege('access_check_reader',c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
          OR has_any_column_privilege('access_check_reader',c.oid,'SELECT,INSERT,UPDATE,REFERENCES')
          OR CASE WHEN current_setting('server_version_num')::integer >= 170000
            THEN has_table_privilege('access_check_reader',c.oid,'MAINTAIN') ELSE false END))
        OR (c.relkind='S' AND CASE WHEN c.relkind='S' THEN has_sequence_privilege('access_check_reader',c.oid,'USAGE,SELECT,UPDATE') ELSE false END)))
 OR EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
     WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND (n.nspname='identity' OR p.prosecdef)
       AND has_function_privilege('access_check_reader',p.oid,'EXECUTE')
       AND p.oid NOT IN ('identity.current_org_id()'::regprocedure,'identity.current_member_id()'::regprocedure,
         'identity.handle_new_user()'::regprocedure,'identity.log_audit()'::regprocedure,'identity.set_audit_fields()'::regprocedure)
       AND (p.oid<>to_regprocedure('identity.current_account_organization()')::oid
         OR has_function_privilege('access_check_reader',p.oid,'EXECUTE WITH GRANT OPTION')))
 OR NOT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
     WHERE n.nspname='identity' AND p.proname='current_account_organization'
       AND pg_get_userbyid(p.proowner)='identity_account_projection_owner' AND p.prosecdef AND p.provolatile='s'
       AND p.proconfig=ARRAY['search_path=pg_catalog, pg_temp'] AND p.pronargs=0
       AND encode(sha256(convert_to(p.prosrc,'UTF8')),'hex')='445df234cf37f0908802feda4df79f9440e7709b4f88e44ccfccf664e2ea704e'
       AND has_function_privilege('access_check_reader',p.oid,'EXECUTE')) THEN
  RAISE EXCEPTION 'access_check_reader_preparation_unsafe';
 END IF;
 IF current_setting('server_version_num')::integer >= 160000 THEN
  EXECUTE 'GRANT access_check_reader TO access_migrator WITH ADMIN FALSE, INHERIT FALSE, SET TRUE';
 ELSE
  IF (SELECT rolinherit FROM pg_roles WHERE rolname='access_migrator') THEN
   RAISE EXCEPTION 'access_check_reader_preparation_unsafe';
  END IF;
  GRANT access_check_reader TO access_migrator;
 END IF;
END $reader_execution$;
COMMIT;
