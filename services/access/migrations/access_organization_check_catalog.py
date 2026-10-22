"""Exact Access15 reader metadata. No Identity imports, writes or business reads."""
import importlib.util
from pathlib import Path
from sqlalchemy import text
from access_baseline import BaselineError, require_equal, rows, acl

_spec = importlib.util.spec_from_file_location('_organization_check_ddl', Path(__file__).parent/'versions/0015_organization_check.py')
_ddl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ddl)
COLUMNS = _ddl.COLUMNS
READER = 'access_check_reader'
EDGE = (READER, 'access_migrator', False, False, True)


def reader_edges(connection):
    return rows(connection,"""SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,
      coalesce((to_jsonb(m)->>'inherit_option')::boolean,(SELECT rolinherit FROM pg_roles WHERE oid=m.member)),
      coalesce((to_jsonb(m)->>'set_option')::boolean,true)
      FROM pg_auth_members m WHERE roleid=(SELECT oid FROM pg_roles WHERE rolname='access_check_reader')
        OR member=(SELECT oid FROM pg_roles WHERE rolname='access_check_reader')""")


def verify_reader_function(connection):
    oid="(SELECT p.oid FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='check_organization_permission')"
    require_equal(rows(connection,f"""SELECT pg_get_userbyid(proowner),l.lanname,prokind,prosecdef,proleakproof,proisstrict,
      provolatile,proparallel,proretset,pg_get_function_identity_arguments(p.oid),pg_get_function_result(p.oid),
      pronargdefaults,proconfig,prosrc,probin,procost,prorows,prosupport::text,
      proallargtypes,proargmodes,proargnames
      FROM pg_proc p JOIN pg_language l ON l.oid=p.prolang WHERE p.oid={oid}"""),
      [(READER,'sql','f',True,False,False,'s','u',True,'p_permission text',
        'TABLE(account_id uuid, org_id uuid, membership_id bigint, actor_id uuid)',0,
        ['search_path=pg_catalog, pg_temp'],_ddl.BODY,None,100.0,1000.0,'-',
        [25,2950,2950,20,2950],['i','t','t','t','t'],['p_permission','account_id','org_id','membership_id','actor_id'])])
    require_equal(acl(connection,oid,'f'),[(READER,READER,'EXECUTE',False),(READER,'access_runtime','EXECUTE',False)])


def expected_dependencies(installed):
    result = {('pg_namespace','a','schema identity'), ('pg_proc','a','function identity.current_account_organization()')}
    if installed:
        result |= {('pg_namespace','a','schema access'),('pg_proc','o','function access.check_organization_permission(text)')}
        result |= {('pg_class','a','column '+column+' of table access.'+table) for table, columns in COLUMNS.items() for column in columns}
        result |= {('pg_policy','r','policy '+policy+' on table access.'+table) for table, policy in (
            ('grants','check_reader_account_scope'),('organization_applications','check_reader_org_scope'))}
    return result


def verify_reader_role(connection, installed):
    require_equal(rows(connection,"SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit FROM pg_roles WHERE rolname='access_check_reader'"),
        [(READER,False,False,False,False,False,False,False)], 'access_check_reader_role_unsafe')
    require_equal(reader_edges(connection),[EDGE], 'access_check_reader_role_unsafe')
    dependencies=rows(connection,"""SELECT s.classid::regclass::text,s.deptype,
      pg_describe_object(s.classid,s.objid,s.objsubid)
      FROM pg_shdepend s WHERE s.refclassid='pg_authid'::regclass
      AND s.refobjid=(SELECT oid FROM pg_roles WHERE rolname='access_check_reader')
      AND s.deptype IN ('a','o','r') AND s.dbid IN (0,(SELECT oid FROM pg_database WHERE datname=current_database()))""")
    require_equal(dependencies,list(expected_dependencies(installed)), 'access_check_reader_dependencies_unsafe')
    require_equal(rows(connection,"""SELECT nspname,p FROM pg_namespace
      CROSS JOIN unnest(ARRAY['USAGE','CREATE','USAGE WITH GRANT OPTION','CREATE WITH GRANT OPTION']) p
      WHERE nspname !~ '^pg_' AND nspname<>'information_schema' AND has_schema_privilege('access_check_reader',oid,p)"""),
      [('public','USAGE'),('identity','USAGE')]+([('access','USAGE')] if installed else []),'access_check_reader_privileges_unsafe')
    if connection.execute(text("SELECT has_database_privilege('access_check_reader',current_database(),'CREATE')")).scalar_one():
        raise BaselineError('access_check_reader_privileges_unsafe')
    # Pin the only foreign projection this reader may call. Identity owns its RLS
    # and complete catalog; fixed metadata recognition remains acyclic here.
    projection="(SELECT p.oid FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity' AND p.proname='current_account_organization')"
    require_equal(rows(connection,f"""SELECT pg_get_userbyid(proowner),prosecdef,provolatile,proconfig,
      pg_get_function_identity_arguments(p.oid),pg_get_function_result(p.oid),
      encode(sha256(convert_to(prosrc,'UTF8')),'hex') FROM pg_proc p WHERE p.oid={projection}"""),
      [('identity_account_projection_owner',True,'s',['search_path=pg_catalog, pg_temp'],'',
        'TABLE(account_id uuid, org_id uuid, membership_id bigint, membership_revision bigint, actor_id uuid)',
        '445df234cf37f0908802feda4df79f9440e7709b4f88e44ccfccf664e2ea704e')], 'access_check_reader_projection_unsafe')
    require_equal(acl(connection,projection,'f'),
      [('identity_account_projection_owner',role,'EXECUTE',False) for role in ('identity_account_projection_owner','access_runtime',READER)],
      'access_check_reader_projection_unsafe')
    # No effective table-level privileges, sequence rights or unlisted column reads.
    table_privileges = ['SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER']
    if connection.dialect.server_version_info >= (17,):
        table_privileges.append('MAINTAIN')
    privilege_array = ','.join("'"+privilege+"'" for privilege in table_privileges)
    require_equal(rows(connection,f"""SELECT n.nspname,c.relname,p FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
      CROSS JOIN unnest(ARRAY[{privilege_array}]) p
      WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND c.relkind IN ('r','p','v','m','f')
      AND has_table_privilege('access_check_reader',c.oid,p)"""),[], 'access_check_reader_privileges_unsafe')
    require_equal(rows(connection,"""SELECT n.nspname,c.relname,a.attname,p FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid
      JOIN pg_namespace n ON n.oid=c.relnamespace CROSS JOIN unnest(ARRAY['SELECT','INSERT','UPDATE','REFERENCES']) p
      WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND c.relkind IN ('r','p','v','m','f')
      AND a.attnum>0 AND NOT a.attisdropped AND has_column_privilege('access_check_reader',c.oid,a.attnum,p)"""),
      [('access',table,col,'SELECT') for table,columns in COLUMNS.items() for col in columns] if installed else [],'access_check_reader_privileges_unsafe')
    require_equal(rows(connection,"""SELECT n.nspname,c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
      WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND c.relkind='S'
      AND CASE WHEN c.relkind='S' THEN has_sequence_privilege('access_check_reader',c.oid,'USAGE,SELECT,UPDATE') ELSE false END"""),[],'access_check_reader_privileges_unsafe')
    # Catalog classification avoids Identity regprocedure resolution: the Access
    # migrator deliberately has no Identity schema USAGE. Only the known pure
    # context invokers and SQL-uncallable trigger routines are excluded.
    require_equal(rows(connection,"""SELECT n.nspname,p.proname,pg_get_function_identity_arguments(p.oid)
      FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
      WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND (n.nspname='identity' OR p.prosecdef)
      AND has_function_privilege('access_check_reader',p.oid,'EXECUTE')
      AND NOT (n.nspname='identity' AND p.pronargs=0 AND p.prokind='f' AND NOT p.proretset AND (
        (NOT p.prosecdef AND ((p.proname='current_org_id' AND p.prorettype='pg_catalog.uuid'::regtype)
          OR (p.proname='current_member_id' AND p.prorettype='pg_catalog.int8'::regtype)))
        OR (p.proname IN ('handle_new_user','log_audit','set_audit_fields')
          AND p.prorettype='pg_catalog.trigger'::regtype)))"""),
      [('identity','current_account_organization','')]+([('access','check_organization_permission','p_permission text')] if installed else []),'access_check_reader_privileges_unsafe')
    if installed: verify_reader_function(connection)
