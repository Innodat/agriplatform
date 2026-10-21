"""Fixed Access-local assertions for known empty and revision1/2/3 catalogs.

Unknown state is preserved for explicit disposition. This module never repairs ACLs,
normalizes history, adopts tables or inspects Identity business data.
"""
from hashlib import sha256
from pathlib import Path
from sqlalchemy import text

OWNER = 'access_migrator'
HEAD = 'access_0006'
LOCK_SQL = "SELECT pg_try_advisory_xact_lock(hashtextextended('access-owned-migrations',0))"


class BaselineError(RuntimeError):
    pass


def rows(connection, sql):
    return [tuple(row) for row in connection.execute(text(sql)).all()]


def require_equal(actual, expected, code='access_catalog_mismatch'):
    if sorted(actual, key=repr) != sorted(expected, key=repr):
        raise BaselineError(code)


def validate_revision(revisions):
    if revisions not in (['access_0001'], ['access_0002'], ['access_0003'], ['access_0004'], ['access_0005'], [HEAD]):
        raise BaselineError('access_unknown_history')
    return revisions[0]


def acl(connection, oid_sql, kind, column=False):
    if kind == 'f':
        return rows(connection, f"SELECT pg_get_userbyid(a.grantor),CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END,a.privilege_type,a.is_grantable FROM pg_proc o,LATERAL aclexplode(coalesce(o.proacl,acldefault('f',o.proowner))) a WHERE o.oid={oid_sql}")
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
    if rows(connection, "SELECT 1 FROM pg_auth_members WHERE member IN (SELECT oid FROM pg_roles WHERE rolname IN ('access_migrator','access_runtime')) AND roleid NOT IN (SELECT oid FROM pg_roles WHERE rolname IN ('access_operator_authority_owner','access_command_owner'))"):
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
                  owner_acl(['USAGE','CREATE']) + [(OWNER,'access_runtime','USAGE',False)] + ([(OWNER,r,'USAGE',False) for r in ('access_operator','access_operator_authority_owner','access_command_owner')] if operator_installed(connection) else []))
    if rows(connection, "SELECT 1 FROM pg_default_acl d LEFT JOIN pg_namespace n ON n.oid=d.defaclnamespace WHERE n.nspname='access' OR d.defaclrole=(SELECT oid FROM pg_roles WHERE rolname='access_migrator')"):
        raise BaselineError('access_default_privileges_mismatch')
    if rows(connection, "SELECT 1 FROM pg_namespace WHERE nspname='identity' AND has_schema_privilege(current_user,oid,'CREATE')"):
        raise BaselineError('access_migration_role_excess_authority')
    if rows(connection, "SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='identity' AND c.relkind IN ('r','p','v','m','S') AND (pg_get_userbyid(c.relowner)='access_migrator' OR has_table_privilege(current_user,c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') OR has_any_column_privilege(current_user,c.oid,'SELECT,INSERT,UPDATE,REFERENCES'))"):
        raise BaselineError('access_migration_role_excess_authority')


def verify_table(connection, name, revision):
    ledger = name == 'alembic_version'
    oid = f"(SELECT c.oid FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' AND c.relname='{name}')"
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
    if not ledger and revision in ('access_0002', 'access_0003', 'access_0004', 'access_0005', HEAD):
        expected += [('membership_id','bigint',False,'','',None,'-')]
    if columns != expected:
        raise BaselineError(code)
    constraints = [('alembic_version_pkc','p','PRIMARY KEY (version_num)',True,False,False)] if ledger else [
        ('grants_pkey','p','PRIMARY KEY (org_id, id)',True,False,False),
        ('grants_org_id_user_id_permission_key','u','UNIQUE (org_id, user_id, permission)',True,False,False),
        ('grants_permission_check','c',"CHECK ((permission = ANY (ARRAY['pts.poetry.read'::text, 'pts.poetry.export'::text, 'pts.poetry.documents'::text])))",True,False,False)]
    if not ledger and revision in ('access_0002', 'access_0003', 'access_0004', 'access_0005', HEAD):
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
    if revision in ('access_0003', 'access_0004', 'access_0005', HEAD):
        names += [*REGISTRY_TABLES, *[index for indexes in REGISTRY_INDEXES.values() for index,columns in indexes]]
    types = [] if revision is None else ['grants','_grants','alembic_version','_alembic_version']
    if revision in ('access_0003', 'access_0004', 'access_0005', HEAD):
        types += [t for name in REGISTRY_TABLES for t in (name,'_'+name)]
    if revision in ('access_0004', 'access_0005', HEAD):
        from access_registration_baseline import TABLES, INDEXES, FUNCTIONS
        if revision in ('access_0005',HEAD):
            from access_registration_baseline import PERMISSION_INDEXES as INDEXES, PERMISSION_FUNCTIONS as FUNCTIONS
        if revision == HEAD:
            from access_registration_baseline import ENTRY_FUNCTIONS as FUNCTIONS
        names += list(TABLES) + list(INDEXES)
    require_equal(rows(connection, "SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access'"), [(n,) for n in names])
    expected_functions = ['registry_storage_immutable'] if revision in ('access_0003','access_0004','access_0005',HEAD) else []
    if revision in ('access_0004', 'access_0005', HEAD):
        expected_functions += list(FUNCTIONS)
        types += [t for name in TABLES for t in (name,'_'+name)]
    require_equal(rows(connection, "SELECT p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access'"), [(n,) for n in expected_functions])
    require_equal(rows(connection, "SELECT t.typname FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace WHERE n.nspname='access'"), [(n,) for n in types])
    if revision is not None:
        verify_table(connection, 'alembic_version', revision)
        verify_table(connection, 'grants', revision)
    if revision in ('access_0003', 'access_0004', 'access_0005', HEAD):
        for name in REGISTRY_TABLES:verify_registry(connection,name,revision)
        verify_registry_guard(connection)
    if revision in ('access_0004', 'access_0005', HEAD):
        from access_registration_baseline import verify_registration
        verify_registration(connection,revision)


def verify_encoding(connection):
    require_equal(rows(connection, "SHOW server_encoding"), [('UTF8',)], 'access_utf8_encoding_required')


def preflight(connection):
    verify_encoding(connection)
    if sha256((Path(__file__).parent/'versions/0001_initial.py').read_bytes()).hexdigest() != '438611104dcb30e8e04d729c0047003487f93e889fa66093aca14a77612e409b':
        raise BaselineError('access_original_source_mismatch')
    if sha256((Path(__file__).parent/'versions/0002_membership_binding.py').read_bytes()).hexdigest() != '781e6e0c80700ab35b2f819891288fedde5137175547eb045651d8ef6c9d222d':
        raise BaselineError('access_original_source_mismatch')
    if sha256((Path(__file__).parent/'versions/0003_registry_storage.py').read_bytes()).hexdigest() != '889eec9bf64fd92f121987916441f56185aa613b069030869a74a1fde3cd1ae2':
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
    verify_encoding(connection)
    verify_prerequisites(connection)
    revision = validate_revision([row[0] for row in rows(connection, 'SELECT version_num FROM access.alembic_version')])
    verify_catalog(connection, revision)


REGISTRY_TABLES = ('applications', 'permissions', 'entry_permissions')
REGISTRY_INDEXES = {
    'applications': [('applications_pkey','app_id')],
    'permissions': [('permissions_pkey','permission'),('permissions_permission_scope_kind_key','permission, scope_kind'),('permissions_app_id_permission_key','app_id, permission')],
    'entry_permissions': [('entry_permissions_pkey','app_id, permission')],
}
REGISTRY_GUARD_BODY = "\nBEGIN\n RAISE EXCEPTION USING ERRCODE = '55000', MESSAGE = 'access_registry_storage_immutable';\nEND\n"


def verify_registry(connection, name, revision=None):
    oid = f"(SELECT c.oid FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' AND c.relname='{name}')"
    require_equal(rows(connection, f"SELECT pg_get_userbyid(relowner),relkind,relrowsecurity,relforcerowsecurity,reloptions,relispartition,relreplident,relpersistence FROM pg_class WHERE oid={oid}"),
                  [(OWNER,'r',False,False,None,False,'d','p')])
    require_equal(rows(connection,f"SELECT 1 FROM pg_inherits WHERE inhrelid={oid} OR inhparent={oid}"),[])
    fields = {
        'applications':[('app_id','text',None),('enabled','boolean','false'),('revision','bigint','1'),('created_by','uuid',None),('updated_by','uuid',None),('created_at','timestamp with time zone',None),('updated_at','timestamp with time zone',None)],
        'permissions':[('permission','text',None),('app_id','text',None),('scope_kind','text',None),('created_by','uuid',None),('created_at','timestamp with time zone',None)],
        'entry_permissions':[('app_id','text',None),('permission','text',None),('created_by','uuid',None),('created_at','timestamp with time zone',None)],
    }[name]
    require_equal(rows(connection,f"SELECT attnum,attname,format_type(atttypid,atttypmod),attnotnull,attidentity,attgenerated,pg_get_expr(d.adbin,d.adrelid),attcollation::regcollation::text FROM pg_attribute a LEFT JOIN pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum WHERE a.attrelid={oid} AND a.attnum>0 AND NOT a.attisdropped"),
                  [(i,col,kind,True,'','',default,'"default"' if kind=='text' else '-') for i,(col,kind,default) in enumerate(fields,1)])
    constraints = {
        'applications':[
            ('applications_pkey','p','PRIMARY KEY (app_id)'),
            ('applications_app_id_valid','c','CHECK (((app_id COLLATE "C") ~ \'^[a-z][a-z0-9_]{1,63}$\'::text))'),
            ('applications_revision_positive','c','CHECK ((revision > 0))'),
        ],
        'permissions':[
            ('permissions_pkey','p','PRIMARY KEY (permission)'),
            ('permissions_permission_valid','c',"CHECK ((((octet_length(convert_to(permission, 'UTF8'::name)) >= 1) AND (octet_length(convert_to(permission, 'UTF8'::name)) <= 200)) AND (length(permission) = octet_length(convert_to(permission, 'UTF8'::name)))))"),
            ('permissions_scope_kind_valid','c',"CHECK ((scope_kind = ANY (ARRAY['account'::text, 'organization'::text])))"),
            ('permissions_app_id_fkey','f','FOREIGN KEY (app_id) REFERENCES access.applications(app_id) ON DELETE RESTRICT'),
            ('permissions_permission_scope_kind_key','u','UNIQUE (permission, scope_kind)'),
            ('permissions_app_id_permission_key','u','UNIQUE (app_id, permission)'),
        ],
        'entry_permissions':[
            ('entry_permissions_pkey','p','PRIMARY KEY (app_id, permission)'),
            ('entry_permissions_app_id_permission_fkey','f','FOREIGN KEY (app_id, permission) REFERENCES access.permissions(app_id, permission) ON DELETE RESTRICT'),
        ],
    }[name]
    for col in ('created_by','updated_by') if name=='applications' else ('created_by',):
        constraints.append((name+'_'+col+'_non_nil','c',f"CHECK (({col} <> '00000000-0000-0000-0000-000000000000'::uuid))"))
    for col in ('created_at','updated_at') if name=='applications' else ('created_at',):
        constraints.append((name+'_'+col+'_finite','c',f'CHECK (isfinite({col}))'))
    require_equal(rows(connection,f"SELECT conname,contype,pg_get_constraintdef(oid),convalidated,condeferrable,condeferred FROM pg_constraint WHERE conrelid={oid}"),
                  [(n,t,d,True,False,False) for n,t,d in constraints]+([('application_required_registration','t','TRIGGER DEFERRABLE INITIALLY DEFERRED',True,True,True)] if name=='applications' and operator_installed(connection) else [('permission_required_registration','t','TRIGGER DEFERRABLE INITIALLY DEFERRED',True,True,True)] if name=='permissions' and revision in ('access_0005',HEAD) else [('entry_permission_required_registration','t','TRIGGER DEFERRABLE INITIALLY DEFERRED',True,True,True)] if name=='entry_permissions' and revision==HEAD else []))
    require_equal(rows(connection,f"SELECT pg_get_indexdef(indexrelid),indisvalid,indisready,indislive FROM pg_index WHERE indrelid={oid}"),
                  [(f'CREATE UNIQUE INDEX {index} ON access.{name} USING btree ({columns})',True,True,True) for index,columns in REGISTRY_INDEXES[name]])
    privileges=['SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER']
    if connection.dialect.server_version_info >= (17,):privileges.append('MAINTAIN')
    require_equal(acl(connection,oid,'r'),owner_acl(privileges)+([(OWNER,'access_command_owner',p,False) for p in ('SELECT','INSERT')] if (name=='applications' and operator_installed(connection)) or (name=='permissions' and revision in ('access_0005',HEAD)) or (name=='entry_permissions' and revision==HEAD) else []))
    require_equal(acl(connection,oid,'r',column=True),[])
    for query in (f'SELECT 1 FROM pg_policy WHERE polrelid={oid}',f'SELECT 1 FROM pg_rewrite WHERE ev_class={oid}',f'SELECT 1 FROM pg_attribute WHERE attrelid={oid} AND attisdropped'):
        require_equal(rows(connection,query),[])
    # FK constraints can remain validated even when their internal triggers are disabled.
    foreign_triggers = {
        'applications': ['permissions_app_id_fkey'] * 2,
        'permissions': ['permissions_app_id_fkey'] * 2 + ['entry_permissions_app_id_permission_fkey'] * 2,
        'entry_permissions': ['entry_permissions_app_id_permission_fkey'] * 2,
    }[name]
    require_equal(rows(connection,f"SELECT k.conname,t.tgenabled FROM pg_trigger t LEFT JOIN pg_constraint k ON k.oid=t.tgconstraint WHERE t.tgrelid={oid} AND t.tgisinternal"),
                  [(constraint,'O') for constraint in foreign_triggers])
    require_equal(rows(connection,f"SELECT tgname,tgenabled,pg_get_triggerdef(oid) FROM pg_trigger WHERE tgrelid={oid} AND NOT tgisinternal"),
                  [('registry_storage_immutable','O',f'CREATE TRIGGER registry_storage_immutable BEFORE DELETE OR UPDATE OR TRUNCATE ON access.{name} FOR EACH STATEMENT EXECUTE FUNCTION access.registry_storage_immutable()')]+([('application_required_registration','O','CREATE CONSTRAINT TRIGGER application_required_registration AFTER INSERT ON access.applications DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION access.require_application_registration()')] if name=='applications' and operator_installed(connection) else [('permission_required_registration','O','CREATE CONSTRAINT TRIGGER permission_required_registration AFTER INSERT ON access.permissions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION access.require_permission_registration()')] if name=='permissions' and revision in ('access_0005',HEAD) else [('entry_permission_required_registration','O','CREATE CONSTRAINT TRIGGER entry_permission_required_registration AFTER INSERT ON access.entry_permissions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION access.require_entry_permission_registration()')] if name=='entry_permissions' and revision==HEAD else []))


def verify_registry_guard(connection):
    oid="(SELECT p.oid FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='registry_storage_immutable')"
    require_equal(rows(connection,f"SELECT pg_get_userbyid(proowner),l.lanname,prokind,prosecdef,proleakproof,proisstrict,provolatile,proparallel,proretset,prorettype::regtype::text,pronargs,proargtypes::text,proallargtypes,proargmodes,proargnames,pronargdefaults,proconfig,prosrc,probin,procost,prorows,prosupport::text FROM pg_proc p JOIN pg_language l ON l.oid=p.prolang WHERE p.oid={oid}"),
                  [(OWNER,'plpgsql','f',False,False,False,'v','u',False,'trigger',0,'',None,None,None,0,['search_path=pg_catalog, pg_temp'],REGISTRY_GUARD_BODY,None,100.0,0.0,'-')])
    require_equal(acl(connection,oid,'f'),owner_acl(['EXECUTE']))


def operator_installed(connection):
    return bool(rows(connection,"SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='register_application'"))


def verify_operator_roles(connection):
    roles=('access_operator','access_operator_authority_owner','access_command_owner')
    require_equal(rows(connection,"SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit FROM pg_roles WHERE rolname IN ('access_operator','access_operator_authority_owner','access_command_owner')"),
        [(r,r=='access_operator',False,False,False,False,False,False) for r in roles], 'access_operator_roles_invalid')
    require_equal(rows(connection,"SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,coalesce((to_jsonb(m)->>'inherit_option')::boolean,(SELECT rolinherit FROM pg_roles WHERE oid=m.member)),coalesce((to_jsonb(m)->>'set_option')::boolean,true) FROM pg_auth_members m WHERE roleid IN (SELECT oid FROM pg_roles WHERE rolname IN ('access_operator','access_operator_authority_owner','access_command_owner')) OR member IN (SELECT oid FROM pg_roles WHERE rolname IN ('access_operator','access_operator_authority_owner','access_command_owner'))"),
        [(r,OWNER,False,False,True) for r in roles if r!='access_operator'], 'access_operator_roles_invalid')
    for role in roles:
        if connection.execute(text("SELECT has_database_privilege(:role,current_database(),'CREATE')"),{'role':role}).scalar_one():
            raise BaselineError('access_operator_roles_invalid')
        verify_operator_foreign_privileges(connection,role)


# Existing Identity/bootstrap routines remain separately owned. Only these exact
# definitions/ACLs may confer foreign definer execution on a restricted Access role.
_FOREIGN_FUNCTIONS = {
 ('public','get_user_roles',''):('identity_migrator',frozenset((
  '70f79a2d8e0ea471156bc48db7adec34cbd5e490cfee72253bf691aaf3e62ef9',
  '92a975a5f5370f2e573597a99704cabea68500c1e2f040dddff390ddd01e3421')),
  '{=X/identity_migrator,identity_migrator=X/identity_migrator,authenticated=X/identity_migrator}'),
 ('identity','authorize','requested_permission identity.app_permission'):('identity_migrator',frozenset(('1f579c398a8830fb55129be4e874d44b5c8b518747ede491e94a0e2b7463fdd0',)),None),
 ('identity','create_user','email text'):('identity_migrator',frozenset(('dbcb47172a78d9c9ba72f16d820e701dcd6c083b7db3375f38d1b840be99c193',)),None),
 ('identity','custom_access_token_hook','event jsonb'):('identity_migrator',frozenset(('0a49cb14def79173fc3575c9739103c6e993d8edcc70ca7e39d68dba7d8ea387',)),
  '{=X/identity_migrator,identity_migrator=X/identity_migrator,supabase_auth_admin=X/identity_migrator}'),
 ('identity','handle_new_user',''):('identity_migrator',frozenset(('359c7e66dcfc2a9b6532e455771876d80dad1a49e06a120e2cfc1fee72ea8588',)),None),
 ('identity','log_audit',''):('identity_migrator',frozenset(('f9497c24903b4fdb86189fc2cf182bcee2e01d572c5a0ec5882fb15a9be040d8',)),None),
 ('identity','set_audit_fields',''):('identity_migrator',frozenset(('d8b726dbeed3ed8453a05fbbdf19f8f13f1944a37aac1fbeaa0da2953d819652',)),None),
 ('identity','membership_join_org_allowed','p_org uuid'):('identity_operator_authority_owner',frozenset(('2343a1cf4da02c2b0267c8ff1533a88a7006577279333c8567aa89d2fffc54c0',)),
  '{=X/identity_operator_authority_owner,identity_operator_authority_owner=X/identity_operator_authority_owner,identity_command_owner=X/identity_operator_authority_owner}'),
 ('identity','membership_join_profile_allowed','p_account uuid'):('identity_operator_authority_owner',frozenset(('7ddbfedaeefd6cee5cf4f5e48bcb32aacf8d01592c3d84709dbb50a619b47208',)),
  '{=X/identity_operator_authority_owner,identity_operator_authority_owner=X/identity_operator_authority_owner,identity_command_owner=X/identity_operator_authority_owner}'),
 ('identity','organization_account_target','target_account_id uuid, expected_membership_id bigint'):('identity_target_projection_owner',frozenset(('baf9708e8bf61ff99a74b6dbfa5aa00d84a76705bb375f6e634c17e67be16f40',)),
  '{identity_target_projection_owner=X/identity_target_projection_owner,access_target_reader=X/identity_target_projection_owner,access_setup_target_reader=X/identity_target_projection_owner,access_command_owner=X/identity_target_projection_owner}'),
}


def verify_operator_foreign_privileges(connection, role):
    """Reject effective foreign authority; preserve only the exact prior bootstrap.

    Catalog inspection needs no foreign business-table reads or new grants. PUBLIC
    grants count as effective privileges, including inaccessible-schema table ACLs.
    """
    permitted_identity=False
    for schema,name,arguments,owner,definition,grants in rows(connection,f"""
        SELECT n.nspname,p.proname,pg_get_function_identity_arguments(p.oid),pg_get_userbyid(p.proowner),
          encode(sha256(convert_to(pg_get_functiondef(p.oid),'UTF8')),'hex'),p.proacl::text
        FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
        WHERE n.nspname NOT IN ('pg_catalog','information_schema','access')
          AND (p.prosecdef OR pg_get_userbyid(p.proowner)='{role}')
          AND has_schema_privilege('{role}',n.oid,'USAGE')
          AND has_function_privilege('{role}',p.oid,'EXECUTE')"""):
        expected=_FOREIGN_FUNCTIONS.get((schema,name,arguments))
        if (expected is None or (schema=='identity' and role!='access_command_owner')
            or owner!=expected[0] or definition not in expected[1] or grants!=expected[2]):
            raise BaselineError('access_operator_roles_invalid')
        if schema=='identity' and name=='organization_account_target':permitted_identity=True
    for schema,usage,create in rows(connection,f"""
        SELECT nspname,has_schema_privilege('{role}',oid,'USAGE'),has_schema_privilege('{role}',oid,'CREATE')
        FROM pg_namespace WHERE nspname !~ '^pg_' AND nspname NOT IN ('information_schema','access')"""):
        if create or (usage and schema!='public' and not (schema=='identity' and permitted_identity)):
            raise BaselineError('access_operator_roles_invalid')
    table_privileges='SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER'
    if connection.dialect.server_version_info>=(17,):table_privileges+=',MAINTAIN'
    privilege_array=','.join("'"+p+"'" for p in table_privileges.split(','))
    for schema,name,kind,owner,privileges,extension,column_acl in rows(connection,f"""
        SELECT n.nspname,c.relname,c.relkind,pg_get_userbyid(c.relowner),
          ARRAY(SELECT p FROM unnest(ARRAY[{privilege_array}]) p WHERE has_table_privilege('{role}',c.oid,p)),
          e.extname,EXISTS(SELECT 1 FROM pg_attribute a WHERE a.attrelid=c.oid AND a.attacl IS NOT NULL)
        FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        LEFT JOIN pg_depend d ON d.classid='pg_class'::regclass AND d.objid=c.oid AND d.deptype='e'
        LEFT JOIN pg_extension e ON e.oid=d.refobjid
        WHERE n.nspname !~ '^pg_' AND n.nspname NOT IN ('information_schema','access') AND c.relkind IN ('r','p','v','m','f')
          AND (has_table_privilege('{role}',c.oid,'{table_privileges}')
            OR has_any_column_privilege('{role}',c.oid,'SELECT,INSERT,UPDATE,REFERENCES') OR pg_get_userbyid(c.relowner)='{role}')"""):
        # Native Supabase's two PUBLIC SELECT-only extension diagnostic views.
        if not (schema=='extensions' and name in ('pg_stat_statements','pg_stat_statements_info')
            and kind=='v' and owner=='supabase_admin' and privileges==['SELECT']
            and extension=='pg_stat_statements' and not column_acl):
            raise BaselineError('access_operator_roles_invalid')
    if rows(connection,f"""SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname !~ '^pg_' AND n.nspname NOT IN ('information_schema','access') AND c.relkind='S'
          AND (has_sequence_privilege('{role}',c.oid,'USAGE,SELECT,UPDATE') OR pg_get_userbyid(c.relowner)='{role}')"""):
        raise BaselineError('access_operator_roles_invalid')
