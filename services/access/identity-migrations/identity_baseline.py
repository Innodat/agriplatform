"""Pinned ID-A sources and fail-closed, read-only adoption verification.

The reference is repository evidence produced from a separate clean source rehearsal.
There is deliberately no target approval/export CLI or reference-path environment option.
"""
from hashlib import sha256
import json
from pathlib import Path
import re
from sqlalchemy import text

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REVISION = 'identity_0001'
SOURCE_NAMES = (
    '20250815110000_platform_create_identity_schema.sql',
    '20250815150000_platform_auth-hook.sql',
    '20250815160000_platform_create_audit_log_tbl.sql',
    '20250815170000_platform_create_audit_triggers.sql',
    '20250815180000_platform_add_get_user_roles_function.sql',
    '20250815210000_platform_multitenancy_orgs.sql',
)
SOURCES = tuple('platform/supabase/migrations/' + name for name in SOURCE_NAMES) + (
    'services/access/tools/identity_bridge.sql',)
# Filled from the independently executed clean synthetic reference before adoption is supported.
REFERENCE_SHA256 = 'ae183b435b2659efbe1a9f2ffdf3eaf1b8d64b2f9256ea72927b6f78453beb00'

class BaselineError(RuntimeError):
    """Safe machine-readable failure; never expose SQL, URLs or payloads."""

def source_sql():
    pins = json.loads((HERE/'source-pins.json').read_text())
    result = []
    for path in SOURCES:
        content = (ROOT/path).read_bytes()
        if sha256(content).hexdigest() != pins.get(path):
            raise BaselineError('identity_source_pin_mismatch')
        sql = content.decode()
        if path == SOURCES[0]:
            # Provisioned separately by the restricted deployment administrator.
            # PostgreSQL checks database CREATE even when IF NOT EXISTS is a no-op.
            schema_bootstrap = 'CREATE SCHEMA IF NOT EXISTS identity;'
            if sql.count(schema_bootstrap) != 1:
                raise BaselineError('identity_source_bootstrap_mismatch')
            sql = sql.replace(schema_bootstrap, '', 1)
        # Historical outer BEGIN/COMMIT must not escape Alembic's transaction.
        sql = re.sub(r'(?im)^\s*(begin|commit);\s*$', '', sql)
        result.append(sql)
    return result

def compare_catalog(actual, expected):
    if actual != expected:
        # Category identifiers are safe; catalog values may include business-sensitive defaults.
        changed = sorted(k for k in actual.keys() | expected.keys() if actual.get(k) != expected.get(k))
        raise BaselineError('identity_catalog_mismatch:' + ','.join(changed))

def trusted_reference(kind):
    path = HERE/'reference.json'
    if REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    data = path.read_bytes()
    if sha256(data).hexdigest() != REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference = json.loads(data)
    if reference['source_pins'] != json.loads((HERE/'source-pins.json').read_text()):
        raise BaselineError('identity_reference_unavailable')
    return reference[kind]

# Object OIDs/physical storage IDs and sequence last values are volatile. Definitions,
# owners, grants and all semantic seed tuples are retained. No target rows are exported.
QUERIES = {
'schema': "SELECT n.nspname, pg_get_userbyid(n.nspowner), coalesce(n.nspacl::text,'') FROM pg_namespace n WHERE n.nspname='identity'",
'relations': """SELECT c.relname,c.relkind,pg_get_userbyid(c.relowner),c.relrowsecurity,c.relforcerowsecurity,coalesce(c.relacl::text,''),coalesce(c.reloptions::text,'') FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='identity' AND c.relname<>'alembic_version' AND c.relname NOT LIKE 'alembic_version_%'""",
'columns': """SELECT c.relname,a.attname,a.attnum,format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity,a.attgenerated,coalesce(pg_get_expr(d.adbin,d.adrelid),''),coalesce(a.attacl::text,''),coalesce(coll.collname,'') FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_attrdef d ON d.adrelid=c.oid AND d.adnum=a.attnum LEFT JOIN pg_collation coll ON coll.oid=a.attcollation WHERE n.nspname='identity' AND c.relkind IN ('r','p','v','m','f') AND c.relname<>'alembic_version' AND a.attnum>0 AND NOT a.attisdropped""",
'constraints': """SELECT c.relname,k.conname,pg_get_constraintdef(k.oid,true),k.convalidated,k.condeferrable,k.condeferred FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='identity' AND c.relname<>'alembic_version'""",
'indexes': """SELECT c.relname,pg_get_indexdef(i.indexrelid),i.indisvalid,i.indisready FROM pg_index i JOIN pg_class c ON c.oid=i.indrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='identity' AND c.relname<>'alembic_version'""",
'sequences': """SELECT c.relname,format_type(s.seqtypid,NULL),s.seqstart,s.seqincrement,s.seqmax,s.seqmin,s.seqcache,s.seqcycle FROM pg_sequence s JOIN pg_class c ON c.oid=s.seqrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='identity'""",
'enums': """SELECT t.typname,pg_get_userbyid(t.typowner),e.enumlabel,e.enumsortorder FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace JOIN pg_enum e ON e.enumtypid=t.oid WHERE n.nspname='identity'""",
'functions': """SELECT n.nspname,p.proname,pg_get_function_identity_arguments(p.oid),pg_get_userbyid(p.proowner),pg_get_functiondef(p.oid),coalesce(p.proacl::text,'') FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity' OR (n.nspname='public' AND p.proname='get_user_roles')""",
'policies': """SELECT schemaname,tablename,policyname,permissive,roles::text,cmd,qual,with_check FROM pg_policies WHERE schemaname='identity'""",
# Include every trigger on auth.users invoking Identity (and the expected name even
# if an attacker points it elsewhere), plus all triggers on Identity relations.
 'triggers': """SELECT n.nspname,c.relname,t.tgname,pg_get_triggerdef(t.oid,true),t.tgenabled FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_proc p ON p.oid=t.tgfoid JOIN pg_namespace pn ON pn.oid=p.pronamespace WHERE NOT t.tgisinternal AND (n.nspname='identity' OR (n.nspname='auth' AND c.relname='users' AND (pn.nspname='identity' OR t.tgname='on_auth_user_created')))""",
'default_privileges': """SELECT pg_get_userbyid(d.defaclrole),coalesce(n.nspname,''),d.defaclobjtype,d.defaclacl::text FROM pg_default_acl d LEFT JOIN pg_namespace n ON n.oid=d.defaclnamespace WHERE n.nspname='identity' OR (d.defaclnamespace=0 AND pg_get_userbyid(d.defaclrole)='identity_migrator')""",
'roles': """SELECT rolname,rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,rolreplication,rolbypassrls FROM pg_roles WHERE rolname IN ('identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin')""",
'role_memberships': """SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,to_jsonb(pg_auth_members)->>'inherit_option',to_jsonb(pg_auth_members)->>'set_option' FROM pg_auth_members WHERE pg_get_userbyid(member) IN ('identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin') OR pg_get_userbyid(roleid)='identity_migrator'""",
'permission_seeds': """SELECT role::text,permission::text,deleted_at IS NULL FROM identity.role_permissions""",
# Effective privileges include inherited authority and PUBLIC defaults, not only ACL text.
'effective_tables': """SELECT r.rolname,c.relname,p,has_table_privilege(r.oid,c.oid,p) FROM pg_roles r CROSS JOIN pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace CROSS JOIN unnest(ARRAY['SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER']) p WHERE n.nspname='identity' AND c.relkind IN ('r','p') AND c.relname<>'alembic_version' AND r.rolname IN ('identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin')""",
'effective_columns': """SELECT r.rolname,c.relname,a.attname,p,has_column_privilege(r.oid,c.oid,a.attnum,p) FROM pg_roles r CROSS JOIN pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_attribute a ON a.attrelid=c.oid CROSS JOIN unnest(ARRAY['SELECT','INSERT','UPDATE','REFERENCES']) p WHERE n.nspname='identity' AND c.relkind IN ('r','p') AND c.relname<>'alembic_version' AND a.attnum>0 AND NOT a.attisdropped AND r.rolname IN ('identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin')""",
'effective_functions': """SELECT r.rolname,n.nspname,p.proname,pg_get_function_identity_arguments(p.oid),has_function_privilege(r.oid,p.oid,'EXECUTE') FROM pg_roles r CROSS JOIN pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE (n.nspname='identity' OR (n.nspname='public' AND p.proname='get_user_roles')) AND r.rolname IN ('identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin')""",
}

QUERIES.update({
    'types': """SELECT t.typname,t.typtype,pg_get_userbyid(t.typowner),t.typnotnull,coalesce(t.typdefault,''),coalesce(t.typacl::text,''),format_type(t.typbasetype,t.typtypmod) FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace WHERE n.nspname='identity' AND t.typname NOT IN ('alembic_version','_alembic_version')""",
    'effective_schemas': """SELECT r.rolname,p,has_schema_privilege(r.oid,n.oid,p) FROM pg_roles r CROSS JOIN pg_namespace n CROSS JOIN unnest(ARRAY['USAGE','CREATE']) p WHERE n.nspname='identity' AND r.rolname IN ('identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin')""",
    'effective_sequences': """SELECT r.rolname,c.relname,p,has_sequence_privilege(r.oid,c.oid,p) FROM pg_roles r CROSS JOIN pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace CROSS JOIN unnest(ARRAY['USAGE','SELECT','UPDATE']) p WHERE n.nspname='identity' AND c.relkind='S' AND r.rolname IN ('identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin')""",
})

def catalog_snapshot(connection):
    result = {}
    for key, sql in QUERIES.items():
        rows = [list(row) for row in connection.execute(text(sql))]
        # Stable serialization also normalizes float/numeric representations.
        result[key] = sorted(json.loads(json.dumps(rows, default=str)), key=lambda row: json.dumps(row, sort_keys=True))
    return result

def catalog_fingerprints(snapshot):
    """Exact normalized category identity without persisting catalog definitions."""
    return {
        category: {'sha256': sha256(json.dumps(rows, sort_keys=True, separators=(',', ':'),
                                              ensure_ascii=True).encode('utf-8')).hexdigest(),
                   'rows': len(rows)}
        for category, rows in snapshot.items()
    }


def verify_catalog(connection, kind):
    compare_catalog(catalog_fingerprints(catalog_snapshot(connection)), trusted_reference(kind))

def preflight(connection, mode):
    source_sql()  # verify immutable source pins even on no-op/adoption
    if mode not in ('clean','adopt'):
        raise BaselineError('identity_invalid_migration_mode')
    if connection.execute(text('SELECT session_user, current_user')).one() != ('identity_migrator','identity_migrator'):
        raise BaselineError('identity_migration_login_required')
    if connection.execute(text("SELECT rolsuper OR rolcreatedb OR rolcreaterole OR rolbypassrls FROM pg_roles WHERE rolname=current_user")).scalar_one():
        raise BaselineError('identity_migration_role_excess_authority')
    if not connection.execute(text("SELECT pg_try_advisory_xact_lock(hashtextextended('identity-owned-migrations',0))")).scalar_one():
        raise BaselineError('identity_migration_busy')
    exists = connection.execute(text("SELECT to_regclass('identity.alembic_version')")).scalar_one()
    revisions = list(connection.execute(text('SELECT version_num FROM identity.alembic_version')).scalars()) if exists else []
    if exists and not revisions:
        raise BaselineError('identity_unknown_history')
    if revisions:
        verify_owned_postcondition(connection)
        return 'owned'
    objects = connection.execute(text("SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='identity' AND c.relname<>'alembic_version'")).scalar_one()
    routines = connection.execute(text("SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity' OR (n.nspname='public' AND p.proname='get_user_roles')")).scalar_one()
    types = connection.execute(text("SELECT count(*) FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace WHERE n.nspname='identity'")).scalar_one()
    hooks = connection.execute(text("SELECT count(*) FROM pg_trigger WHERE tgname='on_auth_user_created' AND tgrelid='auth.users'::regclass")).scalar_one()
    if mode == 'adopt':
        verify_catalog(connection, 'legacy')
        verify_legacy_history(connection)
        return 'adopt'
    if objects or routines or types or hooks:
        raise BaselineError('identity_existing_schema_requires_verified_adoption')
    schema = connection.execute(text("SELECT pg_get_userbyid(nspowner),nspacl::text FROM pg_namespace WHERE nspname='identity'")).one_or_none()
    if schema is None or schema[0] != 'identity_migrator':
        raise BaselineError('identity_empty_schema_owner_mismatch')
    extras = connection.execute(text("SELECT count(*) FROM pg_namespace n, LATERAL aclexplode(n.nspacl) a WHERE n.nspname='identity' AND (a.grantee<>(SELECT oid FROM pg_roles WHERE rolname='identity_migrator') OR a.grantor<>(SELECT oid FROM pg_roles WHERE rolname='identity_migrator'))")).scalar_one()
    defaults = connection.execute(text("SELECT count(*) FROM pg_default_acl d LEFT JOIN pg_namespace n ON n.oid=d.defaclnamespace WHERE n.nspname='identity' OR pg_get_userbyid(d.defaclrole)='identity_migrator'")).scalar_one()
    if extras or defaults:
        raise BaselineError('identity_empty_schema_privileges_mismatch')
    verify_legacy_history(connection, clean=True)
    return 'clean'

def verify_legacy_history(connection, clean=False):
    if not connection.execute(text("SELECT to_regclass('supabase_migrations.schema_migrations')")).scalar_one():
        return
    versions = [name[:14] for name in SOURCE_NAMES]
    # Preserve original ledger; only inspect it. A partial/misnamed source set is unexplained.
    rows = connection.execute(text('SELECT version,name FROM supabase_migrations.schema_migrations')).all()
    known = {version: name[15:-4] for version,name in zip(versions,SOURCE_NAMES)}
    found = {version: name for version,name in rows if version in known}
    for version, name in rows:
        if version not in known and re.search(r'identity|auth.?hook|audit.?triggers|multitenancy_orgs|get_user_roles', name or '', re.I):
            # Other owners have similarly named audit/multitenancy files: only the
            # platform namespace or Identity literal denotes this owner's history.
            if 'identity' in (name or '').lower() or (name or '').startswith('platform_'):
                raise BaselineError('identity_unknown_legacy_history')
    if clean and found:
        raise BaselineError('identity_conflicting_legacy_history')
    if not clean and found and found != known:
        raise BaselineError('identity_unknown_legacy_history')


def verify_owned_postcondition(connection):
    verify_owned_history(connection)
    verify_legacy_history(connection)
    verify_catalog(connection, 'owned')


def verify_owned_history(connection):
    revisions = list(connection.execute(text('SELECT version_num FROM identity.alembic_version')).scalars())
    if revisions != [REVISION]:
        raise BaselineError('identity_unknown_history')
    columns = connection.execute(text("SELECT column_name,data_type,character_maximum_length,is_nullable,column_default FROM information_schema.columns WHERE table_schema='identity' AND table_name='alembic_version' ORDER BY ordinal_position")).all()
    if [tuple(row) for row in columns] != [('version_num','character varying',32,'NO',None)]:
        raise BaselineError('identity_unknown_history')
    owner = connection.execute(text("SELECT pg_get_userbyid(relowner) FROM pg_class WHERE oid='identity.alembic_version'::regclass")).scalar_one()
    extras = connection.execute(text("SELECT count(*) FROM pg_class c,LATERAL aclexplode(c.relacl) a WHERE c.oid='identity.alembic_version'::regclass AND (a.grantee<>c.relowner OR a.grantor<>c.relowner)")).scalar_one()
    column_extras = connection.execute(text("SELECT count(*) FROM pg_attribute att JOIN pg_class c ON c.oid=att.attrelid,LATERAL aclexplode(att.attacl) a WHERE c.oid='identity.alembic_version'::regclass AND (a.grantee<>c.relowner OR a.grantor<>c.relowner)")).scalar_one()
    triggers = connection.execute(text("SELECT count(*) FROM pg_trigger WHERE tgrelid='identity.alembic_version'::regclass AND NOT tgisinternal")).scalar_one()
    constraints = connection.execute(text("SELECT contype,pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='identity.alembic_version'::regclass")).all()
    if owner != 'identity_migrator' or extras or column_extras or triggers or [tuple(row) for row in constraints] != [('p','PRIMARY KEY (version_num)')]:
        raise BaselineError('identity_unknown_history')
