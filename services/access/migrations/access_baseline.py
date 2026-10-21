"""Fixed Access-local assertions for the empty, original and staged single table.

Unknown state is preserved for explicit disposition. This module never repairs ACLs,
normalizes history, adopts tables or inspects Identity business data.
"""
from hashlib import sha256
from pathlib import Path
from sqlalchemy import text

OWNER = 'access_migrator'
HEAD = 'access_0002'
LOCK_SQL = "SELECT pg_try_advisory_xact_lock(hashtextextended('access-owned-migrations',0))"


class BaselineError(RuntimeError):
    pass


def rows(connection, sql):
    return [tuple(row) for row in connection.execute(text(sql)).all()]


def require_equal(actual, expected, code='access_catalog_mismatch'):
    if sorted(actual, key=repr) != sorted(expected, key=repr):
        raise BaselineError(code)


def validate_revision(revisions):
    if revisions not in (['access_0001'], [HEAD]):
        raise BaselineError('access_unknown_history')
    return revisions[0]


def acl(connection, oid_sql, kind, column=False):
    if column:
        return rows(connection, f"SELECT attname,pg_get_userbyid(a.grantor),CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END,a.privilege_type,a.is_grantable FROM pg_attribute att,LATERAL aclexplode(att.attacl) a WHERE att.attrelid={oid_sql}")
    table, field, owner = ('pg_namespace','nspacl','nspowner') if kind == 'n' else ('pg_class','relacl','relowner')
    return rows(connection, f"SELECT pg_get_userbyid(a.grantor),CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END,a.privilege_type,a.is_grantable FROM {table} o,LATERAL aclexplode(coalesce(o.{field},acldefault('{kind}',o.{owner}))) a WHERE o.oid={oid_sql}")


def owner_acl(privileges):
    return [(OWNER, OWNER, p, False) for p in privileges]


def verify_prerequisites(connection):
    if rows(connection, 'SELECT session_user,current_user') != [(OWNER, OWNER)]:
        raise BaselineError('access_migration_login_required')
    if rows(connection, "SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls FROM pg_roles WHERE rolname IN ('access_migrator','access_runtime') ORDER BY rolname") != [(role,True,False,False,False,False,False) for role in ('access_migrator','access_runtime')]:
        raise BaselineError('access_migration_role_excess_authority')
    if connection.execute(text("SELECT has_database_privilege(current_user,current_database(),'CREATE')")).scalar_one():
        raise BaselineError('access_migration_role_excess_authority')
    # No owner assumption, inherited writer or runtime owner path is permitted.
    if rows(connection, "SELECT 1 FROM pg_auth_members WHERE member IN (SELECT oid FROM pg_roles WHERE rolname IN ('access_migrator','access_runtime'))"):
        raise BaselineError('access_migration_role_excess_authority')
    # Preserve the exact existing native Supabase bootstrap, including the separate
    # ADMIN-only edge and SET-only edge. Names alone never establish authority.
    incoming = rows(connection, "SELECT pg_get_userbyid(member),pg_get_userbyid(grantor),admin_option,coalesce((to_jsonb(m)->>'inherit_option')::boolean,(SELECT rolinherit FROM pg_roles WHERE oid=m.member)),coalesce((to_jsonb(m)->>'set_option')::boolean,true) FROM pg_auth_members m WHERE roleid=(SELECT oid FROM pg_roles WHERE rolname='access_migrator')")
    if incoming:
        require_equal(incoming, [('postgres','supabase_admin',True,False,False),
                                 ('postgres','postgres',False,False,True)],
                      'access_migration_role_excess_authority')
        require_equal(rows(connection, "SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit FROM pg_roles WHERE rolname IN ('postgres','supabase_admin')"),
                      [('postgres',True,False,True,True,True,True,True),
                       ('supabase_admin',True,True,True,True,True,True,True)],
                      'access_migration_role_excess_authority')
    if rows(connection, "SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity' AND has_schema_privilege(current_user,n.oid,'USAGE') AND p.prosecdef AND has_function_privilege(current_user,p.oid,'EXECUTE')"):
        raise BaselineError('access_migration_role_excess_authority')
    if rows(connection, "SELECT pg_get_userbyid(nspowner) FROM pg_namespace WHERE nspname='access'") != [(OWNER,)]:
        raise BaselineError('access_schema_owner_mismatch')
    require_equal(acl(connection, "'access'::regnamespace", 'n'),
                  owner_acl(['USAGE','CREATE']) + [(OWNER,'access_runtime','USAGE',False)])
    if rows(connection, "SELECT 1 FROM pg_default_acl d LEFT JOIN pg_namespace n ON n.oid=d.defaclnamespace WHERE n.nspname='access' OR d.defaclrole=(SELECT oid FROM pg_roles WHERE rolname='access_migrator')"):
        raise BaselineError('access_default_privileges_mismatch')
    if rows(connection, "SELECT 1 FROM pg_namespace WHERE nspname='identity' AND has_schema_privilege(current_user,oid,'CREATE')"):
        raise BaselineError('access_migration_role_excess_authority')
    if rows(connection, "SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='identity' AND c.relkind IN ('r','p','v','m','S') AND (pg_get_userbyid(c.relowner)='access_migrator' OR has_table_privilege(current_user,c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') OR has_any_column_privilege(current_user,c.oid,'SELECT,INSERT,UPDATE,REFERENCES'))"):
        raise BaselineError('access_migration_role_excess_authority')


def verify_table(connection, name, revision):
    ledger = name == 'alembic_version'
    oid = f"'access.{name}'::regclass"
    code = 'access_unknown_history' if ledger else 'access_catalog_mismatch'
    require_equal(rows(connection, f"SELECT pg_get_userbyid(relowner),relkind,relrowsecurity,relforcerowsecurity,reloptions,relispartition,relreplident,relpersistence FROM pg_class WHERE oid={oid}"),
                  [(OWNER,'r',not ledger,not ledger,None,False,'d','p')], code)
    require_equal(rows(connection, f"SELECT 1 FROM pg_inherits WHERE inhrelid={oid} OR inhparent={oid}"), [], code)
    columns = rows(connection, f"SELECT attname,format_type(atttypid,atttypmod),attnotnull,attidentity,attgenerated,pg_get_expr(d.adbin,d.adrelid),attcollation::regcollation::text FROM pg_attribute a LEFT JOIN pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum WHERE a.attrelid={oid} AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum")
    expected = [('version_num','character varying(32)',True,'','',None,'"default"')] if ledger else [
        ('org_id','uuid',True,'','',None,'-'),('id','text',True,'','',None,'"default"'),
        ('user_id','uuid',True,'','',None,'-'),('permission','text',True,'','',None,'"default"'),
        ('created_at','timestamp with time zone',True,'','','clock_timestamp()','-'),
        ('created_by','text',True,'','',"current_setting('app.actor_id'::text)",'"default"')]
    if not ledger and revision == HEAD:
        expected += [('membership_id','bigint',False,'','',None,'-')]
    if columns != expected:
        raise BaselineError(code)
    constraints = [('alembic_version_pkc','p','PRIMARY KEY (version_num)',True,False,False)] if ledger else [
        ('grants_pkey','p','PRIMARY KEY (org_id, id)',True,False,False),
        ('grants_org_id_user_id_permission_key','u','UNIQUE (org_id, user_id, permission)',True,False,False),
        ('grants_permission_check','c',"CHECK ((permission = ANY (ARRAY['pts.poetry.read'::text, 'pts.poetry.export'::text, 'pts.poetry.documents'::text])))",True,False,False)]
    if not ledger and revision == HEAD:
        constraints += [('grants_membership_id_positive','c','CHECK ((membership_id > 0))',True,False,False)]
    require_equal(rows(connection, f"SELECT conname,contype,pg_get_constraintdef(oid),convalidated,condeferrable,condeferred FROM pg_constraint WHERE conrelid={oid}"), constraints, code)
    indexes = ['CREATE UNIQUE INDEX alembic_version_pkc ON access.alembic_version USING btree (version_num)'] if ledger else [
        'CREATE UNIQUE INDEX grants_pkey ON access.grants USING btree (org_id, id)',
        'CREATE UNIQUE INDEX grants_org_id_user_id_permission_key ON access.grants USING btree (org_id, user_id, permission)']
    require_equal(rows(connection, f"SELECT pg_get_indexdef(indexrelid),indisvalid,indisready,indislive FROM pg_index WHERE indrelid={oid}"), [(i,True,True,True) for i in indexes], code)
    policies = [] if ledger else [('org_scope','*',True,'{0}',"((org_id)::text = current_setting('app.org_id'::text, true))","((org_id)::text = current_setting('app.org_id'::text, true))")]
    require_equal(rows(connection, f"SELECT polname,polcmd,polpermissive,polroles::text,pg_get_expr(polqual,polrelid),pg_get_expr(polwithcheck,polrelid) FROM pg_policy WHERE polrelid={oid}"), policies, code)
    privileges = ['SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER','MAINTAIN']
    # MAINTAIN is a PostgreSQL17 table privilege; older supported servers omit it.
    if connection.dialect.server_version_info < (17,): privileges.remove('MAINTAIN')
    expected_acl = owner_acl(privileges)
    if not ledger: expected_acl += [(OWNER,'access_runtime','SELECT',False)]
    require_equal(acl(connection, oid, 'r'), expected_acl, code)
    require_equal(acl(connection, oid, 'r', column=True), [], code)
    for query in (f"SELECT 1 FROM pg_trigger WHERE tgrelid={oid} AND NOT tgisinternal",
                  f"SELECT 1 FROM pg_rewrite WHERE ev_class={oid}",
                  f"SELECT 1 FROM pg_attribute WHERE attrelid={oid} AND attisdropped"):
        require_equal(rows(connection, query), [], code)


def verify_catalog(connection, revision):
    names = [] if revision is None else ['grants','grants_pkey','grants_org_id_user_id_permission_key','alembic_version','alembic_version_pkc']
    require_equal(rows(connection, "SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access'"), [(n,) for n in names])
    require_equal(rows(connection, "SELECT p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access'"), [])
    types = [] if revision is None else ['grants','_grants','alembic_version','_alembic_version']
    require_equal(rows(connection, "SELECT t.typname FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace WHERE n.nspname='access'"), [(n,) for n in types])
    if revision is not None:
        verify_table(connection, 'alembic_version', revision)
        verify_table(connection, 'grants', revision)


def preflight(connection):
    if sha256((Path(__file__).parent/'versions/0001_initial.py').read_bytes()).hexdigest() != '438611104dcb30e8e04d729c0047003487f93e889fa66093aca14a77612e409b':
        raise BaselineError('access_original_source_mismatch')
    verify_prerequisites(connection)
    if not connection.execute(text(LOCK_SQL)).scalar_one():
        raise BaselineError('access_migration_busy')
    exists = connection.execute(text("SELECT to_regclass('access.alembic_version')")).scalar_one()
    revision = None
    if exists:
        # Validate shape before querying caller-controlled history content.
        verify_table(connection, 'alembic_version', None)
        revision = validate_revision([row[0] for row in rows(connection, 'SELECT version_num FROM access.alembic_version')])
    verify_catalog(connection, revision)
    return revision


def verify_postcondition(connection):
    verify_prerequisites(connection)
    revision = validate_revision([row[0] for row in rows(connection, 'SELECT version_num FROM access.alembic_version')])
    verify_catalog(connection, revision)
