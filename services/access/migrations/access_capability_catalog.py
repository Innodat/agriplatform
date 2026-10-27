"""Current capability reader's fixed receiving authority and source-bound catalog."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from sqlalchemy import text
from access_baseline import BaselineError,require_equal,rows,acl
from access_account_grant_catalog import snapshot,fingerprints,verify_runtime_role
HERE=Path(__file__).parent
REFERENCE_SHA256='b6ee32aeb585f9ac5c0ad19ca278644a207a56692a9c3847e465f98252faac40'
READER='access_capability_reader'
_spec=importlib.util.spec_from_file_location('_capability_ddl',HERE/'versions/0018_current_capabilities.py')
_ddl=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_ddl)


def verify_reader_role(connection,installed,stage='bridged'):
    require_equal(rows(connection,"SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit FROM pg_roles WHERE rolname='access_capability_reader'"),[(READER,False,False,False,False,False,False,False)],'capability_reader_role_unsafe')
    require_equal(rows(connection,"SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,inherit_option,set_option FROM pg_auth_members WHERE roleid='access_capability_reader'::regrole OR member='access_capability_reader'::regrole"),[(READER,'access_migrator',False,False,True)],'capability_reader_role_unsafe')
    if connection.execute(text("SELECT has_database_privilege('access_capability_reader',current_database(),'CREATE')")).scalar_one():raise BaselineError('capability_reader_privileges_unsafe')
    if stage=='empty':
        require_equal(rows(connection,"SELECT s.classid::regclass::text,s.deptype,pg_describe_object(s.classid,s.objid,s.objsubid) FROM pg_shdepend s WHERE s.refclassid='pg_authid'::regclass AND s.refobjid='access_capability_reader'::regrole AND s.deptype IN ('a','o','r') AND s.dbid IN (0,(SELECT oid FROM pg_database WHERE datname=current_database()))"),[],'capability_reader_dependencies_unsafe')
        return
    dependencies={('pg_namespace','a','schema identity'),('pg_proc','a','function identity.capability_account_context()'),('pg_proc','a','function identity.capability_organization_context()')}
    if installed:
        dependencies.add(('pg_namespace','a','schema access'))
        dependencies|={('pg_proc','o','function access.'+signature) for signature in ('check_account_capability(text)','check_organization_capability(text)','current_organization_context()')}
        dependencies|={('pg_class','a','column '+column+' of table access.'+table) for table,columns in _ddl.COLUMNS.items() for column in columns}
        dependencies|={('pg_policy','r','policy '+policy+' on table access.'+table) for table,policy in (('organization_applications','capability_org_read'),('organization_applications','capability_org_bound'),('grants','capability_grant_read'),('grants','capability_grant_bound'),('account_grants','capability_account_read'),('account_grants','capability_account_bound'))}
    require_equal(rows(connection,"SELECT s.classid::regclass::text,s.deptype,pg_describe_object(s.classid,s.objid,s.objsubid) FROM pg_shdepend s WHERE s.refclassid='pg_authid'::regclass AND s.refobjid='access_capability_reader'::regrole AND s.deptype IN ('a','o','r') AND s.dbid IN (0,(SELECT oid FROM pg_database WHERE datname=current_database()))"),list(dependencies),'capability_reader_dependencies_unsafe')
    require_equal(rows(connection,"SELECT nspname,p FROM pg_namespace CROSS JOIN unnest(ARRAY['USAGE','CREATE','USAGE WITH GRANT OPTION','CREATE WITH GRANT OPTION']) p WHERE nspname !~ '^pg_' AND nspname<>'information_schema' AND has_schema_privilege('access_capability_reader',oid,p)"),[('public','USAGE'),('identity','USAGE')]+([('access','USAGE')] if installed else []),'capability_reader_privileges_unsafe')
    permitted_views=set()
    privileges=['SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER']
    if connection.dialect.server_version_info >= (17,):privileges.append('MAINTAIN')
    array=','.join("'"+p+"'" for p in privileges)
    for schema,name,kind,owner,grants,extension,column_acl in rows(connection,f"""SELECT n.nspname,c.relname,c.relkind,pg_get_userbyid(c.relowner),
      ARRAY(SELECT p FROM unnest(ARRAY[{array}]) p WHERE has_table_privilege('access_capability_reader',c.oid,p)),
      e.extname,EXISTS(SELECT 1 FROM pg_attribute a WHERE a.attrelid=c.oid AND a.attacl IS NOT NULL)
      FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
      LEFT JOIN pg_depend d ON d.classid='pg_class'::regclass AND d.objid=c.oid AND d.deptype='e'
      LEFT JOIN pg_extension e ON e.oid=d.refobjid
      WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND c.relkind IN ('r','p','v','m','f')
      AND has_table_privilege('access_capability_reader',c.oid,'{','.join(privileges)}')"""):
        if not (schema=='extensions' and name in ('pg_stat_statements','pg_stat_statements_info')
          and kind=='v' and owner=='supabase_admin' and grants==['SELECT'] and extension=='pg_stat_statements' and not column_acl):
            raise BaselineError('capability_reader_privileges_unsafe')
        permitted_views.add((schema,name))
    columns=rows(connection,"SELECT n.nspname,c.relname,a.attname,p FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace CROSS JOIN unnest(ARRAY['SELECT','INSERT','UPDATE','REFERENCES']) p WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND c.relkind IN ('r','p','v','m','f') AND a.attnum>0 AND NOT a.attisdropped AND has_column_privilege('access_capability_reader',c.oid,a.attnum,p)")
    require_equal([row for row in columns if tuple(row[:2]) not in permitted_views],[('access',table,column,'SELECT') for table,cols in _ddl.COLUMNS.items() for column in cols] if installed else [],'capability_reader_privileges_unsafe')
    require_equal(rows(connection,"SELECT n.nspname,c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND c.relkind='S' AND CASE WHEN c.relkind='S' THEN has_sequence_privilege('access_capability_reader',c.oid,'USAGE,SELECT,UPDATE') ELSE false END"),[],'capability_reader_privileges_unsafe')
    expected=[('identity','capability_account_context',''),('identity','capability_organization_context','')]
    if installed:expected += [('access','check_account_capability','p_permission text'),('access','check_organization_capability','p_permission text'),('access','current_organization_context','')]
    require_equal(rows(connection,"SELECT n.nspname,p.proname,pg_get_function_identity_arguments(p.oid) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND (n.nspname='identity' OR p.prosecdef) AND has_function_privilege('access_capability_reader',p.oid,'EXECUTE') AND NOT (n.nspname='identity' AND p.pronargs=0 AND p.prokind='f' AND NOT p.proretset AND ((NOT p.prosecdef AND ((p.proname='current_org_id' AND p.prorettype='pg_catalog.uuid'::regtype) OR (p.proname='current_member_id' AND p.prorettype='pg_catalog.int8'::regtype))) OR (p.proname IN ('handle_new_user','log_audit','set_audit_fields') AND p.prorettype='pg_catalog.trigger'::regtype)))"),expected,'capability_reader_privileges_unsafe')
    for name in ('capability_account_context','capability_organization_context'):
        oid="(SELECT p.oid FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity' AND p.proname='"+name+"')"
        require_equal(acl(connection,oid,'f'),[('identity_account_projection_owner',role,'EXECUTE',False) for role in ('identity_account_projection_owner',READER)],'capability_projection_acl_unsafe')


def reference_document(connection):
    return dict(migration_sha256=sha256((HERE/'versions/0018_current_capabilities.py').read_bytes()).hexdigest(),predecessor_reference_sha256=sha256((HERE/'account-grants-reference.json').read_bytes()).hexdigest(),catalog=fingerprints(snapshot(connection)))


def verify_predecessor_sources(document):
    sources=document.get('predecessor_sources')
    if not isinstance(sources,dict) or not sources:raise BaselineError('capability_predecessor_unavailable')
    for name,digest in sources.items():
        path=HERE/'versions'/name
        if Path(name).name!=name or not path.is_file() or sha256(path.read_bytes()).hexdigest()!=digest:
            raise BaselineError('capability_predecessor_unavailable')


def verify_capability_catalog(connection):
    from access_account_grant_catalog import REFERENCE_SHA256 as previous
    from access_organization_check_catalog import verify_reader_role as old_reader
    from access_baseline import verify_operator_roles
    from studies_migration_support import verify_roles
    verify_roles(connection,'access');verify_runtime_role(connection);verify_operator_roles(connection)
    old_reader(connection,installed=True);verify_reader_role(connection,installed=True)
    predecessor=HERE/'account-grants-reference.json'
    if sha256(predecessor.read_bytes()).hexdigest()!=previous or json.loads(predecessor.read_bytes()).get('migration_sha256')!=sha256((HERE/'versions/0017_account_grants.py').read_bytes()).hexdigest():raise BaselineError('capability_predecessor_unavailable')
    verify_predecessor_sources(json.loads(predecessor.read_bytes()))
    path=HERE/'current-capabilities-reference.json'
    if REFERENCE_SHA256 is None or not path.is_file() or sha256(path.read_bytes()).hexdigest()!=REFERENCE_SHA256:raise BaselineError('capability_reference_unavailable')
    if json.loads(path.read_bytes())!=reference_document(connection):raise BaselineError('access_catalog_mismatch')
