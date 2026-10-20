"""Pinned ID-A sources and fail-closed, read-only adoption verification.

The reference is repository evidence produced from a separate clean source rehearsal.
There is deliberately no target approval/export CLI or reference-path environment option.
"""
from hashlib import sha256
import json
from pathlib import Path
import re
from sqlalchemy import text

IMPORTED_SOURCE_SHA256 = sha256(Path(__file__).read_bytes()).hexdigest()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REVISION = 'identity_0001'
ACTOR_REVISION = 'identity_0002'
PROJECTION_REVISION = 'identity_0003'
ORGANIZATION_REVISION = 'identity_0004'
AUTHORITY_REVISION = 'identity_0005'
COMMAND_REVISION = 'identity_0006'
COMMAND_REFERENCE_SHA256 = 'ebe11f9cd4dbed35496488e6eb21b5c6af4c3c8f767447fd1e1ad7fb2c2c1188'
COMMAND_OWNER = 'identity_command_owner'
AUTHORITY_REFERENCE_SHA256 = '2f378cf2e9641bf60a84be4efda88c395a951c1032499d68c13fee878c13a81e'
AUTHORITY_OWNER = 'identity_operator_authority_owner'
OPERATOR = 'identity_operator'
ORGANIZATION_REFERENCE_SHA256 = '5eeed70cf624fc548e9fcbbe13f0adfb83d7e00081def9e71b69e644afd2e6ae'
PROJECTION_REFERENCE_SHA256 = '6cc6467bef0ba9c744cb53f9c2bb8542412a660c1a161f2be76fd3fa1d0a85a9'
PROJECTION_OWNER = 'identity_account_projection_owner'
ACTOR_REFERENCE_SHA256 = 'c83985f3761cbac85666118fdbbd140d324a424a031baea69b6f174d4585cd1a'
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
    if kind == 'command':
        return trusted_command_reference()
    if kind == 'authority':
        return trusted_authority_reference()
    if kind == 'organization':
        return trusted_organization_reference()
    if kind == 'projection':
        return trusted_projection_reference()
    if kind == 'actor':
        return trusted_actor_reference()
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

def trusted_actor_reference():
    """Additional fixed fixture; original ID-A evidence is never rewritten."""
    path = HERE/'actor-reference.json'
    if ACTOR_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    data = path.read_bytes()
    if sha256(data).hexdigest() != ACTOR_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference = json.loads(data)
    if (reference['source_pins'] != json.loads((HERE/'source-pins.json').read_text())
            or reference['migration_sha256'] != sha256((HERE/'versions/0002_actor_registry.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['actor']

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
    if kind == 'command':
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        compare_catalog(catalog_fingerprints(command_catalog_snapshot(connection)), trusted_reference(kind))
        return
    if kind == 'authority':
        verify_projection_role(connection)
        verify_authority_roles(connection)
        snapshot = authority_catalog_snapshot(connection)
        normalize_staged_command(connection, snapshot)
        compare_catalog(catalog_fingerprints(snapshot), trusted_reference(kind))
        return
    if kind in ('projection', 'organization'):
        verify_projection_role(connection)
        snapshot = projection_catalog_snapshot(connection)
    else:
        snapshot = catalog_snapshot(connection)
        # Only a separately validated, still empty staged owner may differ from
        # old immutable references. No arbitrary membership/ACL is normalized.
        present = connection.execute(text("SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname=:role)"), {'role': PROJECTION_OWNER}).scalar_one()
        if present:
            verify_projection_role(connection, staged=True)
            snapshot['role_memberships'] = [row for row in snapshot['role_memberships']
                if row not in ([PROJECTION_OWNER, 'identity_migrator', False, 'false', 'true'],
                               [PROJECTION_OWNER, 'identity_migrator', False, None, None])]
    normalize_staged_authority(connection, snapshot)
    normalize_staged_command(connection, snapshot)
    compare_catalog(catalog_fingerprints(snapshot), trusted_reference(kind))

def preflight(connection, mode):
    source_sql()  # verify immutable source pins even on no-op/adoption
    if connection.execute(text("SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname IN ('identity_operator','identity_operator_authority_owner'))")).scalar_one():
        verify_authority_roles(connection)
    if mode not in ('clean','adopt'):
        raise BaselineError('identity_invalid_migration_mode')
    if connection.execute(text('SELECT session_user, current_user')).one() != ('identity_migrator','identity_migrator'):
        raise BaselineError('identity_migration_login_required')
    if connection.execute(text("SELECT rolsuper OR rolcreatedb OR rolcreaterole OR rolbypassrls FROM pg_roles WHERE rolname=current_user")).scalar_one():
        raise BaselineError('identity_migration_role_excess_authority')
    verify_projection_prerequisites(connection)
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


def verify_owned_postcondition(connection, require_head=False):
    revision = verify_owned_history(connection)
    if require_head and revision != COMMAND_REVISION:
        raise BaselineError('identity_unknown_history')
    verify_legacy_history(connection)
    verify_catalog(connection, {REVISION: 'owned', ACTOR_REVISION: 'actor', PROJECTION_REVISION: 'projection', ORGANIZATION_REVISION: 'organization', AUTHORITY_REVISION: 'authority', COMMAND_REVISION: 'command'}[revision])


def verify_owned_history(connection):
    revisions = list(connection.execute(text('SELECT version_num FROM identity.alembic_version')).scalars())
    if revisions not in ([REVISION], [ACTOR_REVISION], [PROJECTION_REVISION], [ORGANIZATION_REVISION], [AUTHORITY_REVISION], [COMMAND_REVISION]):
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

    return revisions[0]


def trusted_projection_reference():
    # A later head must not stop protecting earlier immutable source evidence.
    trusted_reference('owned')
    trusted_actor_reference()
    path = HERE/'projection-reference.json'
    if PROJECTION_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    data = path.read_bytes()
    if sha256(data).hexdigest() != PROJECTION_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference = json.loads(data)
    if (reference['source_pins'] != json.loads((HERE/'source-pins.json').read_text())
            or reference['migration_sha256'] != sha256((HERE/'versions/0003_current_account_actor.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['projection']


def verify_projection_prerequisites(connection):
    # Existing Auth schema USAGE is insufficient to pass it to the NOLOGIN reader.
    # Only the actual schema owner can prepare this controlled bootstrap grant.
    if not connection.execute(text("SELECT has_schema_privilege(current_user, 'auth', 'USAGE WITH GRANT OPTION')")).scalar_one():
        raise BaselineError('identity_projection_auth_grant_required')


PROJECTION_ROLE_QUERIES = {
    'projection_role': "SELECT rolname,rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,rolreplication,rolbypassrls FROM pg_roles WHERE rolname='identity_account_projection_owner'",
    'projection_memberships': "SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,coalesce(to_jsonb(pg_auth_members)->>'inherit_option',(SELECT rolinherit::text FROM pg_roles WHERE oid=member)),coalesce(to_jsonb(pg_auth_members)->>'set_option','true') FROM pg_auth_members WHERE roleid=(SELECT oid FROM pg_roles WHERE rolname='identity_account_projection_owner') OR member=(SELECT oid FROM pg_roles WHERE rolname='identity_account_projection_owner')",
    # Current-database and shared ACL/ownership dependencies catch unlisted grants
    # even outside Identity. Other databases have independent owner histories.
    # OIDs are deliberately replaced by stable names.
    'projection_dependencies': "SELECT coalesce(d.datname,''),s.classid::regclass::text,s.deptype,CASE WHEN s.dbid IN (0,(SELECT oid FROM pg_database WHERE datname=current_database())) THEN pg_describe_object(s.classid,s.objid,s.objsubid) ELSE 'other_database' END FROM pg_shdepend s LEFT JOIN pg_database d ON d.oid=s.dbid WHERE s.refclassid='pg_authid'::regclass AND s.refobjid=(SELECT oid FROM pg_roles WHERE rolname='identity_account_projection_owner') AND s.deptype IN ('a','o') AND s.dbid IN (0,(SELECT oid FROM pg_database WHERE datname=current_database()))",
}


def verify_projection_role(connection, staged=False):
    rows = connection.execute(text(PROJECTION_ROLE_QUERIES['projection_role'])).all()
    if not rows:
        raise BaselineError('identity_projection_role_missing')
    if [tuple(row) for row in rows] != [(PROJECTION_OWNER, False, False, False, False, False, False, False)]:
        raise BaselineError('identity_projection_role_unsafe')
    members = connection.execute(text(PROJECTION_ROLE_QUERIES['projection_memberships'])).all()
    if [tuple(row) for row in members] != [(PROJECTION_OWNER, 'identity_migrator', False, 'false', 'true')]:
        raise BaselineError('identity_projection_role_unsafe')
    if staged and connection.execute(text(PROJECTION_ROLE_QUERIES['projection_dependencies'])).all():
        raise BaselineError('identity_projection_role_not_empty')


def projection_catalog_snapshot(connection):
    result = catalog_snapshot(connection)
    for key, sql in PROJECTION_ROLE_QUERIES.items():
        rows = [list(row) for row in connection.execute(text(sql))]
        # DB names are per-rehearsal identities, not privilege semantics.
        if key == 'projection_dependencies':
            for row in rows:
                if row[0] == connection.execute(text('SELECT current_database()')).scalar_one():
                    row[0] = 'current_database'
        result[key] = sorted(json.loads(json.dumps(rows, default=str)), key=lambda row: json.dumps(row, sort_keys=True))
    auth_sql = "SELECT r.rolname,p,has_schema_privilege(r.oid,n.oid,p) FROM pg_roles r CROSS JOIN pg_namespace n CROSS JOIN unnest(ARRAY['USAGE','CREATE','USAGE WITH GRANT OPTION','CREATE WITH GRANT OPTION']) p WHERE n.nspname='auth' AND r.rolname='identity_account_projection_owner'"
    result['projection_auth_schema_privileges'] = sorted([list(row) for row in connection.execute(text(auth_sql))], key=lambda row: json.dumps(row, sort_keys=True))
    for category in ('effective_tables', 'effective_columns', 'effective_functions', 'effective_schemas', 'effective_sequences'):
        sql = QUERIES[category].replace("'identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin'", "'identity_account_projection_owner'")
        result['projection_' + category] = sorted([list(row) for row in connection.execute(text(sql))], key=lambda row: json.dumps(row, sort_keys=True))
        if category in ('effective_tables', 'effective_columns'):
            auth_sql = sql.replace("n.nspname='identity'", "n.nspname='auth'")
            # Denied vendor tables/columns are not Identity contract shape. Keep
            # only effective grants, including authority inherited through PUBLIC.
            result['projection_auth_' + category] = sorted([list(row) for row in connection.execute(text(auth_sql)) if row[-1]], key=lambda row: json.dumps(row, sort_keys=True))
    return result


def projection_catalog_fingerprints(snapshot):
    return catalog_fingerprints(snapshot)


def trusted_organization_reference():
    """Head4 retains all previous immutable references and source identities."""
    trusted_projection_reference()
    path = HERE/'organization-reference.json'
    if ORGANIZATION_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    data = path.read_bytes()
    if sha256(data).hexdigest() != ORGANIZATION_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference = json.loads(data)
    if (reference['source_pins'] != json.loads((HERE/'source-pins.json').read_text())
            or reference['migration_sha256'] != sha256((HERE/'versions/0004_current_account_organization.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['organization']


# Separately prepared roles are never silently repaired by migration.
AUTHORITY_ROLE_QUERIES = {
    key.replace('projection','authority'): sql.replace(PROJECTION_OWNER, AUTHORITY_OWNER)
    for key, sql in PROJECTION_ROLE_QUERIES.items()
}
AUTHORITY_ROLE_QUERIES.update({
    'operator_role': PROJECTION_ROLE_QUERIES['projection_role'].replace(PROJECTION_OWNER, OPERATOR),
    'operator_memberships': PROJECTION_ROLE_QUERIES['projection_memberships'].replace(PROJECTION_OWNER, OPERATOR),
    'operator_dependencies': PROJECTION_ROLE_QUERIES['projection_dependencies'].replace(PROJECTION_OWNER, OPERATOR),
})


def verify_authority_roles(connection, staged=False):
    for role, prefix, login in [(AUTHORITY_OWNER,'authority',False),(OPERATOR,'operator',True)]:
        rows=connection.execute(text(AUTHORITY_ROLE_QUERIES[prefix+'_role'])).all()
        if not rows:
            raise BaselineError('identity_authority_role_missing')
        if [tuple(row) for row in rows] != [(role,False,False,False,False,login,False,False)]:
            raise BaselineError('identity_authority_role_unsafe')
        members=connection.execute(text(AUTHORITY_ROLE_QUERIES[prefix+'_memberships'])).all()
        expected=[(AUTHORITY_OWNER,'identity_migrator',False,'false','true')] if role==AUTHORITY_OWNER else []
        if [tuple(row) for row in members] != expected:
            raise BaselineError('identity_authority_role_unsafe')
        if staged and connection.execute(text(AUTHORITY_ROLE_QUERIES[prefix+'_dependencies'])).all():
            raise BaselineError('identity_authority_role_not_empty')
        # External SECURITY DEFINER execution can confer privileges independently
        # of direct ACLs. Only the fixed retained legacy read is allowed; its
        # definition/ACL remains protected by every historical canonical catalog.
        if connection.execute(text("""SELECT EXISTS (SELECT 1 FROM pg_proc p
            JOIN pg_namespace n ON n.oid=p.pronamespace
            WHERE n.nspname NOT IN ('pg_catalog','information_schema','identity')
              AND p.prosecdef AND has_function_privilege(:role,p.oid,'EXECUTE')
              AND p.oid <> coalesce(to_regprocedure('public.get_user_roles()')::oid,0))"""),{'role':role}).scalar_one():
            raise BaselineError('identity_authority_role_unsafe')
        if connection.execute(text("""SELECT EXISTS (SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND c.relkind='S'
              AND CASE WHEN c.relkind='S' THEN has_sequence_privilege(:role,c.oid,'USAGE,UPDATE') ELSE false END)"""),{'role':role}).scalar_one():
            raise BaselineError('identity_authority_role_unsafe')
        # Effective PUBLIC/inherited privileges need checking even for empty roles.
        if connection.execute(text("""SELECT EXISTS (
            SELECT 1 FROM pg_namespace n WHERE n.nspname !~ '^pg_' AND n.nspname <> 'information_schema'
              AND has_schema_privilege(:role,n.oid,'CREATE')
            UNION ALL SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
              WHERE n.nspname !~ '^pg_' AND n.nspname <> 'information_schema' AND c.relkind IN ('r','p','v','m','f')
              AND (has_table_privilege(:role,c.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
                   OR has_any_column_privilege(:role,c.oid,'INSERT,UPDATE,REFERENCES'))
        )"""),{'role':role}).scalar_one():
            raise BaselineError('identity_authority_role_unsafe')
        if connection.execute(text("""SELECT EXISTS (SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE n.nspname !~ '^pg_' AND n.nspname <> 'information_schema'
              AND (:staged OR n.nspname <> 'identity') AND c.relkind IN ('r','p','v','m','f')
              AND has_any_column_privilege(:role,c.oid,'SELECT'))"""),{'role':role,'staged':staged}).scalar_one():
            raise BaselineError('identity_authority_role_unsafe')


def normalize_staged_authority(connection,snapshot):
    present=connection.execute(text("SELECT count(*) FROM pg_roles WHERE rolname IN ('identity_operator','identity_operator_authority_owner')")).scalar_one()
    if not present:return
    verify_authority_roles(connection,staged=True)
    snapshot['role_memberships']=[row for row in snapshot['role_memberships'] if row not in (
        [AUTHORITY_OWNER,'identity_migrator',False,'false','true'],
        [AUTHORITY_OWNER,'identity_migrator',False,None,None])]


def authority_catalog_snapshot(connection):
    result=projection_catalog_snapshot(connection)
    for key,sql in AUTHORITY_ROLE_QUERIES.items():
        rows=[list(row) for row in connection.execute(text(sql))]
        if key.endswith('_dependencies'):
            current=connection.execute(text('SELECT current_database()')).scalar_one()
            for row in rows:
                if row[0]==current:row[0]='current_database'
        result[key]=sorted(json.loads(json.dumps(rows,default=str)),key=lambda row:json.dumps(row,sort_keys=True))
    for category in ('effective_tables','effective_columns','effective_functions','effective_schemas','effective_sequences'):
        sql=QUERIES[category].replace("'identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin'", "'identity_operator','identity_operator_authority_owner'")
        result['authority_'+category]=sorted([list(row) for row in connection.execute(text(sql))],key=lambda row:json.dumps(row,sort_keys=True))
    return result


def trusted_authority_reference():
    """Head5 supplements, and never replaces, the four historical reference chains."""
    trusted_organization_reference()
    path=HERE/'authority-reference.json'
    if AUTHORITY_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    data=path.read_bytes()
    if sha256(data).hexdigest()!=AUTHORITY_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference=json.loads(data)
    if (reference['source_pins']!=json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256']!=sha256((HERE/'versions/0005_operator_authority.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['authority']


COMMAND_ROLE_QUERIES = {key.replace('projection','command'): value.replace(PROJECTION_OWNER,COMMAND_OWNER)
                        for key,value in PROJECTION_ROLE_QUERIES.items()}


def verify_command_role(connection, staged=False):
    rows=connection.execute(text(COMMAND_ROLE_QUERIES['command_role'])).all()
    if not rows:
        raise BaselineError('identity_command_role_missing')
    if [tuple(row) for row in rows] != [(COMMAND_OWNER,False,False,False,False,False,False,False)]:
        raise BaselineError('identity_command_role_unsafe')
    rows=connection.execute(text(COMMAND_ROLE_QUERIES['command_memberships'])).all()
    if [tuple(row) for row in rows] != [(COMMAND_OWNER,'identity_migrator',False,'false','true')]:
        raise BaselineError('identity_command_role_unsafe')
    if staged and connection.execute(text(COMMAND_ROLE_QUERIES['command_dependencies'])).all():
        raise BaselineError('identity_command_role_not_empty')
    # Reject PUBLIC/inherited authority outside the fixed local owner boundary.
    if connection.execute(text("""SELECT EXISTS (
      SELECT 1 WHERE has_database_privilege(:role,current_database(),'CREATE')
      UNION ALL SELECT 1 FROM pg_namespace n WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema'
       AND has_schema_privilege(:role,n.oid,'CREATE')
      UNION ALL SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
       WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND c.relkind IN ('r','p','v','m','f')
       AND (:staged OR n.nspname<>'identity')
       AND (has_table_privilege(:role,c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
            OR has_any_column_privilege(:role,c.oid,'SELECT,INSERT,UPDATE,REFERENCES'))
      UNION ALL SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
       WHERE n.nspname !~ '^pg_' AND c.relkind='S' AND CASE WHEN c.relkind='S' THEN has_sequence_privilege(:role,c.oid,'USAGE,SELECT,UPDATE') ELSE false END
      UNION ALL SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
       WHERE n.nspname NOT IN ('pg_catalog','information_schema','identity') AND p.prosecdef
       AND has_function_privilege(:role,p.oid,'EXECUTE')
       AND p.oid<>coalesce(to_regprocedure('public.get_user_roles()')::oid,0)
    )"""),{'role':COMMAND_OWNER,'staged':staged}).scalar_one():
        raise BaselineError('identity_command_role_unsafe')


def normalize_staged_command(connection,snapshot):
    if not connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='identity_command_owner')")).scalar_one():
        return
    verify_command_role(connection,staged=True)
    snapshot['role_memberships']=[row for row in snapshot['role_memberships'] if row not in (
        [COMMAND_OWNER,'identity_migrator',False,'false','true'],
        [COMMAND_OWNER,'identity_migrator',False,None,None])]


def command_catalog_snapshot(connection):
    result=authority_catalog_snapshot(connection)
    for key,sql in COMMAND_ROLE_QUERIES.items():
        rows=[list(row) for row in connection.execute(text(sql))]
        if key.endswith('_dependencies'):
            current=connection.execute(text('SELECT current_database()')).scalar_one()
            for row in rows:
                if row[0]==current:row[0]='current_database'
        result[key]=sorted(json.loads(json.dumps(rows,default=str)),key=lambda row:json.dumps(row,sort_keys=True))
    for category in ('effective_tables','effective_columns','effective_functions','effective_schemas','effective_sequences'):
        sql=QUERIES[category].replace("'identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin'", "'identity_command_owner'")
        result['command_'+category]=sorted([list(row) for row in connection.execute(text(sql))],key=lambda row:json.dumps(row,sort_keys=True))
    return result


def trusted_command_reference():
    trusted_authority_reference()
    path=HERE/'command-reference.json'
    if COMMAND_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    content=path.read_bytes()
    if sha256(content).hexdigest()!=COMMAND_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference=json.loads(content)
    if (reference['source_pins']!=json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256']!=sha256((HERE/'versions/0006_actor_command.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['command']
