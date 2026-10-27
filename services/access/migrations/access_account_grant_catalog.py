"""Source-bound Access17 catalog; reference is independently published by root."""
from hashlib import sha256
import json
from pathlib import Path
from sqlalchemy import text
HERE=Path(__file__).parent
REFERENCE_SHA256='7bfa0b7d8057b9004fd6ffa97478b2101427caa3985e4b0c9ad5c2934058c7c3'

def snapshot(connection):
    # Reuse existing selected catalog queries, restricted to this owner. This is
    # evidence for this migration, not a generic runtime authorization framework.
    queries={
        'schema': "SELECT nspname,pg_get_userbyid(nspowner),coalesce(nspacl::text,'') FROM pg_namespace WHERE nspname='access'",
        'indexes': "SELECT c.relname,pg_get_indexdef(i.indexrelid),i.indisvalid,i.indisready,i.indislive FROM pg_index i JOIN pg_class c ON c.oid=i.indrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' AND c.relname<>'alembic_version'",
        'relations': "SELECT c.relname,c.relkind,pg_get_userbyid(c.relowner),c.relrowsecurity,c.relforcerowsecurity,coalesce(c.relacl::text,'') FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' AND c.relname NOT LIKE 'alembic_version%'",
        'columns': "SELECT c.relname,a.attname,a.attnum,format_type(a.atttypid,a.atttypmod),a.attnotnull,coalesce(pg_get_expr(d.adbin,d.adrelid),''),coalesce(a.attacl::text,'') FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_attrdef d ON d.adrelid=c.oid AND d.adnum=a.attnum WHERE n.nspname='access' AND c.relkind='r' AND c.relname<>'alembic_version' AND a.attnum>0 AND NOT a.attisdropped",
        'constraints': "SELECT c.relname,k.conname,pg_get_constraintdef(k.oid,true),k.convalidated,k.condeferrable,k.condeferred FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' AND c.relname<>'alembic_version'",
        'functions': "SELECT p.proname,pg_get_function_identity_arguments(p.oid),pg_get_userbyid(p.proowner),pg_get_functiondef(p.oid),coalesce(p.proacl::text,'') FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access'",
        'policies': "SELECT tablename,policyname,permissive,roles::text,cmd,qual,with_check FROM pg_policies WHERE schemaname='access'",
        'triggers': "SELECT c.relname,t.tgname,pg_get_triggerdef(t.oid,true),t.tgenabled FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' AND NOT t.tgisinternal",
        'effective_tables': "SELECT r.rolname,c.relname,p,has_table_privilege(r.oid,c.oid,p) FROM pg_roles r CROSS JOIN pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace CROSS JOIN unnest(ARRAY['SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER']) p WHERE n.nspname='access' AND c.relkind='r' AND c.relname<>'alembic_version' AND r.rolname IN ('access_runtime','access_operator','access_command_owner','access_operator_authority_owner','access_check_reader','access_studies_owner','access_studies_runtime')",
    }
    return {category: sorted([list(row) for row in connection.execute(text(query))],key=lambda row:json.dumps(row,sort_keys=True)) for category,query in queries.items()}

def fingerprints(value):
    return {category:dict(sha256=sha256(json.dumps(rows,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest(),rows=len(rows)) for category,rows in value.items()}

def reference_document(connection):
    return dict(migration_sha256=sha256((HERE/'versions/0017_account_grants.py').read_bytes()).hexdigest(),
        predecessor_sources={path.name:sha256(path.read_bytes()).hexdigest() for path in sorted((HERE/'versions').glob('*.py')) if path.name<'0017'},
        catalog=fingerprints(snapshot(connection)))

def verify_account_grant_catalog(connection):
    from studies_migration_support import verify_roles
    verify_roles(connection,'access')
    verify_runtime_role(connection)
    from access_organization_check_catalog import verify_reader_role
    verify_reader_role(connection,installed=True)
    from access_baseline import BaselineError,verify_operator_roles
    verify_operator_roles(connection)
    path=HERE/'account-grants-reference.json'
    if REFERENCE_SHA256 is None or not path.is_file() or sha256(path.read_bytes()).hexdigest()!=REFERENCE_SHA256:raise BaselineError('access_account_grant_reference_unavailable')
    expected=json.loads(path.read_bytes());actual=reference_document(connection)
    if any(expected.get(k)!=actual[k] for k in ('migration_sha256','predecessor_sources')):raise BaselineError('access_account_grant_reference_unavailable')
    if actual['catalog']!=expected.get('catalog'):raise BaselineError('access_catalog_mismatch')


def verify_runtime_role(connection):
    """A standalone cross-owner catalog check must also reject SET-only edges."""
    from access_baseline import BaselineError
    row=connection.execute(text("SELECT rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls FROM pg_roles WHERE rolname='access_runtime'")).one_or_none()
    if row is None or tuple(row)!=(True,False,False,False,False,False):raise BaselineError('access_runtime_role_unsafe')
    edges=[tuple(edge) for edge in connection.execute(text("SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),pg_get_userbyid(grantor),admin_option,coalesce((to_jsonb(m)->>'inherit_option')::boolean,(SELECT rolinherit FROM pg_roles WHERE oid=m.member)),coalesce((to_jsonb(m)->>'set_option')::boolean,true) FROM pg_auth_members m WHERE member=(SELECT oid FROM pg_roles WHERE rolname='access_runtime') OR roleid=(SELECT oid FROM pg_roles WHERE rolname='access_runtime')")).all()]
    # Preserve the independently observed native ADMIN-only bootstrap. It grants
    # no SET/INHERIT path to runtime; every outgoing or additional edge is denied.
    if edges not in ([],[('access_runtime','postgres','supabase_admin',True,False,False)]):raise BaselineError('access_runtime_role_unsafe')
    if edges:
        bootstrap=[tuple(role) for role in connection.execute(text("SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit FROM pg_roles WHERE rolname IN ('postgres','supabase_admin') ORDER BY rolname")).all()]
        if bootstrap!=[('postgres',True,False,True,True,True,True,True),('supabase_admin',True,True,True,True,True,True,True)]:raise BaselineError('access_runtime_role_unsafe')
    if connection.execute(text("SELECT has_database_privilege('access_runtime',current_database(),'CREATE')")).scalar_one():raise BaselineError('access_runtime_role_unsafe')
