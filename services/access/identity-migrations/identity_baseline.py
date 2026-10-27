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
TARGET_REVISION = 'identity_0007'
PROFILE_REVISION = 'identity_0008'
LEGACY_ROLES_REVISION = 'identity_0009'
TOKEN_HOOK_REVISION = 'identity_0010'
MEMBERSHIP_ACTOR_ATTRIBUTION_REVISION = 'identity_0015'
ORGANIZATION_TARGET_REVISION = 'identity_0019'
CHECK_READER_BRIDGE_REVISION = 'identity_0020'
STUDIES_SETUP_REVISION = 'identity_0021'
PERSON_LINKS_REVISION = 'identity_0022'
PREFERENCES_REVISION = 'identity_0023'
ACCOUNT_GRANT_TARGET_REVISION = 'identity_0024'
CAPABILITY_REVISION = 'identity_0025'
DISCOVERY_REVISION = 'identity_0026'
CHECK_READER_BRIDGE_REFERENCE_SHA256 = '154c165f0f5635d42f2ecca1a0b75033be0aa7ef344353042cbcfc3ed72770a7'
CHECK_READER = 'access_check_reader'
ORGANIZATION_TARGET_REFERENCE_SHA256 = 'ac95baf560fd71eef4fa4867e45cc79fb22072c16ebb1dce80185bf524730235'
ACCOUNT_ACTOR_ENSURE_REVISION = 'identity_0018'
ACCOUNT_ACTOR_ENSURE_REFERENCE_SHA256 = '9502c7183ed38c6f81a3de6f578e04e6feb81059c56fdbbc44045b6f6054eb50'
ACCOUNT_VERIFICATION_OWNER = 'identity_account_verification_owner'
MEMBERSHIP_JOIN_COMMAND_REVISION = 'identity_0017'
MEMBERSHIP_JOIN_COMMAND_REFERENCE_SHA256 = '8e6a0b7f61535e0c541b7e80836e1431331ddb37a5ad57432a800b02e4ebd5df'
MEMBERSHIP_RETIRE_COMMAND_REVISION = 'identity_0016'
MEMBERSHIP_RETIRE_COMMAND_REFERENCE_SHA256 = '71bd766de85d53269c7f972851442eacdfea45f4d785589d42abb3d2a38ec488'
MEMBERSHIP_ACTOR_ATTRIBUTION_REFERENCE_SHA256 = '2204a3ca4323bf9693aacc5f4202d2aab1516ac395e71516df2d8f702298a715'
ACTIVE_MEMBERSHIP_INDEX_REVISION = 'identity_0014'
ACTIVE_MEMBERSHIP_INDEX_REFERENCE_SHA256 = 'b710b943ecb95e4b7cbce9eb77debad8f1ad181c40a2532ff87cd85be317033b'
MEMBERSHIP_RETIREMENT_REVISION = 'identity_0013'
MEMBERSHIP_RETIREMENT_REFERENCE_SHA256 = '63543e9abe478ddc277cb00f8f241b181dd3e88c8eb29be827fc17835c3cfab0'
MEMBERSHIP_RETENTION_REVISION = 'identity_0012'
MEMBERSHIP_RETENTION_REFERENCE_SHA256 = '6476b2210402434fd4fa732a7ab882dc8ca02cdbc694c94955647f43d696cf81'
MEMBERSHIP_BINDING_REVISION = 'identity_0011'
MEMBERSHIP_BINDING_REFERENCE_SHA256 = '43bf6d868efb7234ebd8199d884f7cafcca018a2fd274df6329187381a6827f3'
TOKEN_HOOK_REFERENCE_SHA256 = 'f227a7839ba8e04fe1626254e91678c73cf3fc2aa5e38fdb0a5b1ec6a3633263'
LEGACY_ROLES_REFERENCE_SHA256 = '983d00ac73bfc9d86188ce166cece3c246926f169b9993af0141a527d8bbd0aa'
PROFILE_REFERENCE_SHA256 = '05ccb6afc5c546d18ea16747a59d4e63c6f8576718d885b43ecc03e676779868'
TARGET_REFERENCE_SHA256 = '7e7dea28f7d1659b8793b7286de4dbddd7a22b81947db5644595f37e2f1299ae'
TARGET_OWNER = 'identity_target_projection_owner'
TARGET_ROLES = (TARGET_OWNER, 'access_target_reader', 'access_setup_target_reader', 'access_command_owner')
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
    if kind == 'check_reader_bridge':
        return trusted_check_reader_bridge_reference()
    if kind == 'organization_target':
        return trusted_organization_target_reference()
    if kind == 'account_actor_ensure':
        return trusted_account_actor_ensure_reference()
    if kind == 'membership_join_command':
        return trusted_membership_join_command_reference()
    if kind == 'membership_retire_command':
        return trusted_membership_retire_command_reference()
    if kind == 'membership_actor_attribution':
        return trusted_membership_actor_attribution_reference()
    if kind == 'active_membership_index':
        return trusted_active_membership_index_reference()
    if kind == 'membership_retirement':
        return trusted_membership_retirement_reference()
    if kind == 'membership_retention':
        return trusted_membership_retention_reference()
    if kind == 'membership_binding':
        return trusted_membership_binding_reference()
    if kind == 'token_hook':
        return trusted_token_hook_reference()
    if kind == 'legacy_roles':
        return trusted_legacy_roles_reference()
    if kind == 'profile':
        return trusted_profile_reference()
    if kind == 'target':
        return trusted_target_reference()
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
    if connection.execute(text("SELECT to_regrole('identity_discovery_owner') IS NOT NULL")).scalar_one():
        from identity_discovery_catalog import verify_role
        verify_role(connection)
        result['role_memberships']=[row for row in result['role_memberships'] if row!=['identity_discovery_owner','identity_migrator',False,'false','true']]
    # A verified, still staged Studies SET-only edge is not an old owner change.
    if connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='identity_studies_owner')")).scalar_one() and not connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity' AND p.proname='prepare_studies_account')")).scalar_one():
        from studies_migration_support import verify_roles
        verify_roles(connection,'identity')
        result['role_memberships']=[row for row in result['role_memberships'] if row!=['identity_studies_owner','identity_migrator',False,'false','true']]
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
    if kind == 'discovery':
        from identity_discovery_catalog import verify_discovery_catalog
        verify_discovery_catalog(connection)
        return
    if kind == 'capability_reader':
        from identity_capability_catalog import verify_capability_catalog
        verify_capability_catalog(connection)
        return
    if kind == 'account_grant_target':
        from identity_account_grant_catalog import verify_account_grant_catalog
        verify_account_grant_catalog(connection)
        return
    if kind == 'language_preferences':
        from identity_preferences_catalog import verify_preferences_catalog
        verify_preferences_catalog(connection)
        return
    if kind == 'person_links':
        from identity_person_catalog import verify_person_catalog
        verify_person_catalog(connection)
        return
    if kind == 'studies_setup':
        from identity_studies_catalog import verify_studies_catalog
        verify_studies_catalog(connection)
        return
    if kind == 'check_reader_bridge':
        verify_account_verification_role(connection)
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        verify_target_roles(connection)
        verify_profile_privileges(connection)
        verify_check_reader_role(connection)
        compare_catalog(catalog_fingerprints(check_reader_bridge_catalog_snapshot(connection)), trusted_check_reader_bridge_reference())
        return
    if kind == 'organization_target':
        verify_account_verification_role(connection)
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        verify_target_roles(connection)
        verify_profile_privileges(connection)
        compare_catalog(catalog_fingerprints(account_actor_catalog_snapshot(connection)), trusted_organization_target_reference())
        return
    if kind == 'account_actor_ensure':
        verify_account_verification_role(connection)
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        verify_target_roles(connection)
        verify_profile_privileges(connection)
        compare_catalog(catalog_fingerprints(account_actor_catalog_snapshot(connection)), trusted_account_actor_ensure_reference())
        return
    if kind == 'membership_join_command':
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        verify_target_roles(connection)
        verify_profile_privileges(connection)
        compare_catalog(historical_catalog_fingerprints(connection, target_catalog_snapshot(connection)), trusted_membership_join_command_reference())
        return
    if kind == 'membership_retire_command':
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        verify_target_roles(connection)
        verify_profile_privileges(connection)
        compare_catalog(historical_catalog_fingerprints(connection, target_catalog_snapshot(connection)), trusted_membership_retire_command_reference())
        return
    if kind == 'membership_actor_attribution':
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        verify_target_roles(connection)
        verify_profile_privileges(connection)
        compare_catalog(historical_catalog_fingerprints(connection, target_catalog_snapshot(connection)), trusted_membership_actor_attribution_reference())
        return
    if kind == 'active_membership_index':
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        verify_target_roles(connection)
        verify_profile_privileges(connection)
        compare_catalog(historical_catalog_fingerprints(connection, target_catalog_snapshot(connection)), trusted_active_membership_index_reference())
        return
    if kind == 'membership_retirement':
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        verify_target_roles(connection)
        verify_profile_privileges(connection)
        compare_catalog(historical_catalog_fingerprints(connection, target_catalog_snapshot(connection)), trusted_membership_retirement_reference())
        return
    if kind == 'membership_retention':
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        verify_target_roles(connection)
        verify_profile_privileges(connection)
        compare_catalog(historical_catalog_fingerprints(connection, target_catalog_snapshot(connection)), trusted_membership_retention_reference())
        return
    if kind == 'membership_binding':
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        verify_target_roles(connection)
        verify_profile_privileges(connection)
        compare_catalog(historical_catalog_fingerprints(connection, target_catalog_snapshot(connection)), trusted_membership_binding_reference())
        return
    if kind == 'token_hook':
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        verify_target_roles(connection)
        verify_profile_privileges(connection)
        compare_catalog(historical_catalog_fingerprints(connection, target_catalog_snapshot(connection)), trusted_token_hook_reference())
        return
    if kind == 'legacy_roles':
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        verify_target_roles(connection)
        verify_profile_privileges(connection)
        compare_catalog(historical_catalog_fingerprints(connection, target_catalog_snapshot(connection)), trusted_legacy_roles_reference())
        return
    if kind == 'profile':
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        verify_target_roles(connection)
        verify_profile_privileges(connection)
        compare_catalog(historical_catalog_fingerprints(connection, target_catalog_snapshot(connection)), trusted_profile_reference())
        return
    if kind == 'target':
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        verify_target_roles(connection)
        compare_catalog(historical_catalog_fingerprints(connection, target_catalog_snapshot(connection)), trusted_target_reference())
        return
    if kind == 'command':
        verify_projection_role(connection)
        verify_authority_roles(connection)
        verify_command_role(connection)
        snapshot = command_catalog_snapshot(connection)
        normalize_staged_target(connection, snapshot)
        compare_catalog(historical_catalog_fingerprints(connection, snapshot), trusted_reference(kind))
        return
    if kind == 'authority':
        verify_projection_role(connection)
        verify_authority_roles(connection)
        snapshot = authority_catalog_snapshot(connection)
        normalize_staged_command(connection, snapshot)
        normalize_staged_target(connection, snapshot)
        compare_catalog(historical_catalog_fingerprints(connection, snapshot), trusted_reference(kind))
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
    normalize_staged_target(connection, snapshot)
    compare_catalog(historical_catalog_fingerprints(connection, snapshot), trusted_reference(kind))

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
    if connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='identity_account_verification_owner')")).scalar_one():
        deployed = connection.execute(text("SELECT to_regprocedure('identity.ensure_account_actor(uuid,uuid,uuid,text,text,text,bytea)') IS NOT NULL")).scalar_one()
        verify_account_verification_role(connection, staged=not deployed)
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
    if require_head and revision != DISCOVERY_REVISION:
        raise BaselineError('identity_unknown_history')
    verify_legacy_history(connection)
    verify_catalog(connection, {REVISION: 'owned', ACTOR_REVISION: 'actor', PROJECTION_REVISION: 'projection', ORGANIZATION_REVISION: 'organization', AUTHORITY_REVISION: 'authority', COMMAND_REVISION: 'command', TARGET_REVISION: 'target', PROFILE_REVISION: 'profile', LEGACY_ROLES_REVISION: 'legacy_roles', TOKEN_HOOK_REVISION: 'token_hook', MEMBERSHIP_BINDING_REVISION: 'membership_binding', MEMBERSHIP_RETENTION_REVISION: 'membership_retention', MEMBERSHIP_RETIREMENT_REVISION: 'membership_retirement', ACTIVE_MEMBERSHIP_INDEX_REVISION: 'active_membership_index', MEMBERSHIP_ACTOR_ATTRIBUTION_REVISION: 'membership_actor_attribution', MEMBERSHIP_RETIRE_COMMAND_REVISION: 'membership_retire_command', MEMBERSHIP_JOIN_COMMAND_REVISION: 'membership_join_command', ACCOUNT_ACTOR_ENSURE_REVISION: 'account_actor_ensure', ORGANIZATION_TARGET_REVISION: 'organization_target', CHECK_READER_BRIDGE_REVISION: 'check_reader_bridge', STUDIES_SETUP_REVISION:'studies_setup', PERSON_LINKS_REVISION:'person_links', PREFERENCES_REVISION:'language_preferences', ACCOUNT_GRANT_TARGET_REVISION:'account_grant_target', CAPABILITY_REVISION:'capability_reader', DISCOVERY_REVISION:'discovery'}[revision])


def verify_owned_history(connection):
    revisions = list(connection.execute(text('SELECT version_num FROM identity.alembic_version')).scalars())
    if revisions not in ([REVISION], [ACTOR_REVISION], [PROJECTION_REVISION], [ORGANIZATION_REVISION], [AUTHORITY_REVISION], [COMMAND_REVISION], [TARGET_REVISION], [PROFILE_REVISION], [LEGACY_ROLES_REVISION], [TOKEN_HOOK_REVISION], [MEMBERSHIP_BINDING_REVISION], [MEMBERSHIP_RETENTION_REVISION], [MEMBERSHIP_RETIREMENT_REVISION], [ACTIVE_MEMBERSHIP_INDEX_REVISION], [MEMBERSHIP_ACTOR_ATTRIBUTION_REVISION], [MEMBERSHIP_RETIRE_COMMAND_REVISION], [MEMBERSHIP_JOIN_COMMAND_REVISION], [ACCOUNT_ACTOR_ENSURE_REVISION], [ORGANIZATION_TARGET_REVISION], [CHECK_READER_BRIDGE_REVISION], [STUDIES_SETUP_REVISION], [PERSON_LINKS_REVISION], [PREFERENCES_REVISION], [ACCOUNT_GRANT_TARGET_REVISION], [CAPABILITY_REVISION], [DISCOVERY_REVISION]):
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
       WHERE n.nspname !~ '^pg_' AND c.relkind='S'
       AND (:staged OR n.nspname<>'identity' OR c.relname<>'org_member_id_seq' OR has_sequence_privilege(:role,c.oid,'SELECT,UPDATE')) AND CASE WHEN c.relkind='S' THEN has_sequence_privilege(:role,c.oid,'USAGE,SELECT,UPDATE') ELSE false END
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


TARGET_ROLE_QUERIES = {
    role: {key.replace('projection', 'target'): sql.replace(PROJECTION_OWNER, role)
           for key, sql in PROJECTION_ROLE_QUERIES.items()}
    for role in TARGET_ROLES
}


def verified_access_command_extension(connection):
    """Recognize only the explicitly prepared Access0004/5/6/7/8/9/10/11/12 recipient bundle.

    Metadata validation grants Identity no Access reads or role assumption. Existing
    immutable Identity references continue describing Identity's own privileges.
    """
    members=connection.execute(text(TARGET_ROLE_QUERIES['access_command_owner']['target_memberships'])).all()
    if not members:
        return False,False
    if [tuple(row) for row in members] != [('access_command_owner','access_migrator',False,'false','true')]:
        raise BaselineError('identity_target_role_unsafe')
    # Import only the colocated fixed catalog verifier; no Access business data.
    import importlib.util
    import sys
    directory=HERE.parent/'migrations'
    previous=list(sys.path)
    try:
        sys.path.insert(0,str(directory))
        import access_baseline as access_catalog
        access_catalog.verify_operator_roles(connection)
        installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='register_application')")).scalar_one())
        if installed:
            permission_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='register_permission')")).scalar_one())
            entry_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='register_entry_permission')")).scalar_one())
            enablement_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='set_application_enabled')")).scalar_one())
            storage_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' AND c.relname='organization_applications')")).scalar_one())
            configure_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='configure_organization_application')")).scalar_one())
            grant_storage_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_attribute a WHERE a.attrelid=(SELECT c.oid FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' AND c.relname='grants') AND a.attname='revision' AND a.attnum>0 AND NOT a.attisdropped)")).scalar_one())
            grant_bridge_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_attribute a WHERE a.attrelid=(SELECT c.oid FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' AND c.relname='grants') AND a.attname='registry_permission' AND a.attgenerated='s' AND a.attnum>0 AND NOT a.attisdropped)")).scalar_one())
            grant_strict_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_class p ON p.oid=k.confrelid JOIN pg_namespace pn ON pn.oid=p.relnamespace WHERE n.nspname='access' AND c.relname='grants' AND pn.nspname='access' AND p.relname='permissions' AND k.contype='f' AND k.conname='grants_permission_scope_fkey')")).scalar_one())
            grant_assign_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='assign_organization_grant')")).scalar_one())
            grant_revoke_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='revoke_organization_grant')")).scalar_one())
            reader_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='check_organization_permission')")).scalar_one())
            studies_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='enroll_studies_account')")).scalar_one())
            account_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='change_account_grant')")).scalar_one())
            capability_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='check_account_capability')")).scalar_one())
            discovery_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='discover_applications')")).scalar_one())
            access_catalog.verify_catalog(connection,'access_0019' if discovery_installed else 'access_0018' if capability_installed else 'access_0017' if account_installed else 'access_0016' if studies_installed else 'access_0015' if reader_installed else 'access_0014' if grant_revoke_installed else 'access_0013' if grant_assign_installed else 'access_0012' if grant_strict_installed else 'access_0011' if grant_bridge_installed else 'access_0010' if grant_storage_installed else 'access_0009' if configure_installed else 'access_0008' if storage_installed else 'access_0007' if enablement_installed else 'access_0006' if entry_installed else 'access_0005' if permission_installed else 'access_0004')
            access_catalog.require_equal(access_catalog.rows(connection,"SELECT pg_get_userbyid(nspowner) FROM pg_namespace WHERE nspname='access'"),[('access_migrator',)])
            access_catalog.require_equal(access_catalog.acl(connection,"(SELECT oid FROM pg_namespace WHERE nspname='access')",'n'),
                access_catalog.owner_acl(['USAGE','CREATE'])+ [('access_migrator',r,'USAGE',False) for r in ('access_runtime','access_operator','access_operator_authority_owner','access_command_owner')]+([('access_migrator','access_check_reader','USAGE',False)] if reader_installed else [])+([('access_migrator',r,'USAGE',False) for r in ('access_studies_owner','access_studies_runtime')] if studies_installed else [])+([('access_migrator','access_capability_reader','USAGE',False)] if capability_installed else [])+([('access_migrator','access_discovery_owner','USAGE',False)] if discovery_installed else []))
        return True,installed
    except access_catalog.BaselineError:
        raise BaselineError('identity_target_role_unsafe') from None
    finally:
        sys.path[:]=previous


def _identity_target_dependencies(rows):
    # Called only after the complete installed Access catalog/ACL was verified.
    # Access7's exact column UPDATE adds this one pg_shdepend description.
    return [row for row in rows if str(row[3]) not in ('schema access','column enabled of table access.applications','column enabled of table access.organization_applications','column membership_id of table access.grants','column revoked_at of table access.grants') and not str(row[3]).startswith(('table access.','function access.'))]


def verify_target_roles(connection, staged=False):
    """Validate separately staged roles; never repair or normalize arbitrary rights."""
    access_edge,access_catalog = verified_access_command_extension(connection)
    for role, queries in TARGET_ROLE_QUERIES.items():
        rows=connection.execute(text(queries['target_role'])).all()
        if not rows:
            raise BaselineError('identity_target_role_missing')
        if [tuple(row) for row in rows] != [(role,False,False,False,False,False,False,False)]:
            raise BaselineError('identity_target_role_unsafe')
        members=connection.execute(text(queries['target_memberships'])).all()
        expected=([(TARGET_OWNER,'identity_migrator',False,'false','true')] if role==TARGET_OWNER else [('access_command_owner','access_migrator',False,'false','true')] if role=='access_command_owner' and access_edge else [])
        if [tuple(row) for row in members] != expected:
            raise BaselineError('identity_target_role_unsafe')
        if staged and (_identity_target_dependencies(connection.execute(text(queries['target_dependencies'])).all()) if role=='access_command_owner' and access_catalog else connection.execute(text(queries['target_dependencies'])).all()):
            raise BaselineError('identity_target_role_not_empty')
        if connection.execute(text("""SELECT EXISTS (
          SELECT 1 WHERE has_database_privilege(:role,current_database(),'CREATE')
          UNION ALL SELECT 1 FROM pg_namespace n WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema'
           AND has_schema_privilege(:role,n.oid,'CREATE')
          UNION ALL SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
           WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND NOT (:access_catalog AND :role='access_command_owner' AND n.nspname='access') AND c.relkind IN ('r','p','v','m','f')
           AND (has_table_privilege(:role,c.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
                OR has_any_column_privilege(:role,c.oid,'INSERT,UPDATE,REFERENCES')
                OR ((:staged OR :role <> 'identity_target_projection_owner' OR n.nspname<>'identity')
                    AND has_any_column_privilege(:role,c.oid,'SELECT')))
          UNION ALL SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
           WHERE n.nspname !~ '^pg_' AND c.relkind='S'
           AND CASE WHEN c.relkind='S' THEN has_sequence_privilege(:role,c.oid,'USAGE,SELECT,UPDATE') ELSE false END
          UNION ALL SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
           WHERE n.nspname NOT IN ('pg_catalog','information_schema','identity') AND NOT (:access_catalog AND :role='access_command_owner' AND n.nspname='access') AND p.prosecdef
           AND has_function_privilege(:role,p.oid,'EXECUTE')
           AND p.oid<>coalesce(to_regprocedure('public.get_user_roles()')::oid,0)
        )"""),{'role':role,'staged':staged,'access_catalog':access_catalog}).scalar_one():
            raise BaselineError('identity_target_role_unsafe')


def normalize_staged_target(connection, snapshot):
    present=connection.execute(text("SELECT count(*) FROM pg_roles WHERE rolname IN ('identity_target_projection_owner','access_target_reader','access_setup_target_reader','access_command_owner')")).scalar_one()
    if not present:return
    verify_target_roles(connection,staged=True)
    snapshot['role_memberships']=[row for row in snapshot['role_memberships'] if row not in (
        [TARGET_OWNER,'identity_migrator',False,'false','true'],
        [TARGET_OWNER,'identity_migrator',False,None,None])]


def target_catalog_snapshot(connection):
    result=command_catalog_snapshot(connection)
    for role, queries in TARGET_ROLE_QUERIES.items():
        for key, sql in queries.items():
            rows=[list(row) for row in connection.execute(text(sql))]
            if key.endswith('_dependencies'):
                current=connection.execute(text('SELECT current_database()')).scalar_one()
                for row in rows:
                    if row[0]==current:row[0]='current_database'
            result[role+'_'+key]=sorted(json.loads(json.dumps(rows,default=str)),key=lambda row:json.dumps(row,sort_keys=True))
    selected=','.join("'"+role+"'" for role in TARGET_ROLES)
    for category in ('effective_tables','effective_columns','effective_functions','effective_schemas','effective_sequences'):
        sql=QUERIES[category].replace("'identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin'",selected)
        result['target_'+category]=sorted([list(row) for row in connection.execute(text(sql))],key=lambda row:json.dumps(row,sort_keys=True))
    access_edge,access_catalog=verified_access_command_extension(connection)
    if access_edge:
        result['access_command_owner_target_memberships']=[]
    if access_catalog:
        result['access_command_owner_target_dependencies']=_identity_target_dependencies(result['access_command_owner_target_dependencies'])
    return result


def trusted_target_reference():
    """Head7 retains the complete six-head immutable evidence/source chain."""
    trusted_command_reference()
    path=HERE/'target-reference.json'
    if TARGET_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    content=path.read_bytes()
    if sha256(content).hexdigest()!=TARGET_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference=json.loads(content)
    if (reference['source_pins']!=json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256']!=sha256((HERE/'versions/0007_organization_targets.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['target']


def verify_profile_privileges(connection):
    """Exact effective write columns, including PUBLIC and inherited grants."""
    if connection.execute(text("SELECT has_table_privilege('authenticated', 'identity.users', 'INSERT,UPDATE')")).scalar_one():
        raise BaselineError('identity_profile_column_privileges_mismatch')
    rows = connection.execute(text("""SELECT a.attname, p,
        has_column_privilege('authenticated', a.attrelid, a.attnum, p)
        FROM pg_attribute a CROSS JOIN unnest(ARRAY['INSERT','UPDATE']) p
        WHERE a.attrelid='identity.users'::regclass AND a.attnum>0 AND NOT a.attisdropped""")).all()
    allowed = {'INSERT': {'id', 'username'}, 'UPDATE': {'username', 'deleted_at'}}
    if (not rows or any(bool(granted) != (column in allowed[permission]) for column,permission,granted in rows)
            or {(column,permission) for column,permission,granted in rows if granted}
               != {(column,permission) for permission,columns in allowed.items() for column in columns}):
        raise BaselineError('identity_profile_column_privileges_mismatch')


def trusted_profile_reference():
    """Head8 extends, and independently rechecks, all seven historical heads."""
    trusted_target_reference()
    path=HERE/'profile-reference.json'
    if PROFILE_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    content=path.read_bytes()
    if sha256(content).hexdigest()!=PROFILE_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference=json.loads(content)
    if (reference['source_pins']!=json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256']!=sha256((HERE/'versions/0008_profile_fields.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['profile']


def trusted_legacy_roles_reference():
    """Independent helper-only fixture, retaining the full historical trust chain."""
    trusted_profile_reference()
    path=HERE/'legacy-role-reference.json'
    if LEGACY_ROLES_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    content=path.read_bytes()
    if sha256(content).hexdigest()!=LEGACY_ROLES_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference=json.loads(content)
    if (reference['source_pins']!=json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256']!=sha256((HERE/'versions/0009_legacy_roles.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['legacy_roles']


def trusted_token_hook_reference():
    """Independent helper-only fixture, retaining the full historical trust chain."""
    trusted_legacy_roles_reference()
    path=HERE/'token-hook-reference.json'
    if TOKEN_HOOK_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    content=path.read_bytes()
    if sha256(content).hexdigest()!=TOKEN_HOOK_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference=json.loads(content)
    if (reference['source_pins']!=json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256']!=sha256((HERE/'versions/0010_token_hook.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['token_hook']


def trusted_membership_binding_reference():
    """Independent helper-only fixture, retaining the full historical trust chain."""
    trusted_token_hook_reference()
    path=HERE/'membership-binding-reference.json'
    if MEMBERSHIP_BINDING_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    content=path.read_bytes()
    if sha256(content).hexdigest()!=MEMBERSHIP_BINDING_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference=json.loads(content)
    if (reference['source_pins']!=json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256']!=sha256((HERE/'versions/0011_membership_binding.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['membership_binding']


def trusted_membership_retention_reference():
    """Independent helper-only fixture, retaining the full historical trust chain."""
    trusted_membership_binding_reference()
    path=HERE/'membership-retention-reference.json'
    if MEMBERSHIP_RETENTION_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    content=path.read_bytes()
    if sha256(content).hexdigest()!=MEMBERSHIP_RETENTION_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference=json.loads(content)
    if (reference['source_pins']!=json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256']!=sha256((HERE/'versions/0012_membership_retention.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['membership_retention']


def trusted_membership_retirement_reference():
    """Independent helper-only fixture, retaining the full historical trust chain."""
    trusted_membership_retention_reference()
    path=HERE/'membership-retirement-reference.json'
    if MEMBERSHIP_RETIREMENT_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    content=path.read_bytes()
    if sha256(content).hexdigest()!=MEMBERSHIP_RETIREMENT_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference=json.loads(content)
    if (reference['source_pins']!=json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256']!=sha256((HERE/'versions/0013_membership_retirement.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['membership_retirement']


def trusted_active_membership_index_reference():
    """Independent helper-only fixture, retaining the full historical trust chain."""
    trusted_membership_retirement_reference()
    path=HERE/'active-membership-index-reference.json'
    if ACTIVE_MEMBERSHIP_INDEX_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    content=path.read_bytes()
    if sha256(content).hexdigest()!=ACTIVE_MEMBERSHIP_INDEX_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference=json.loads(content)
    if (reference['source_pins']!=json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256']!=sha256((HERE/'versions/0014_active_membership_index.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['active_membership_index']


def trusted_membership_actor_attribution_reference():
    """Independent helper-only fixture, retaining the full historical trust chain."""
    trusted_active_membership_index_reference()
    path=HERE/'membership-actor-attribution-reference.json'
    if MEMBERSHIP_ACTOR_ATTRIBUTION_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    content=path.read_bytes()
    if sha256(content).hexdigest()!=MEMBERSHIP_ACTOR_ATTRIBUTION_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference=json.loads(content)
    if (reference['source_pins']!=json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256']!=sha256((HERE/'versions/0015_membership_actor_attribution.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['membership_actor_attribution']


def trusted_membership_retire_command_reference():
    """Independent helper-only fixture, retaining the full historical trust chain."""
    trusted_membership_actor_attribution_reference()
    path=HERE/'membership-retire-command-reference.json'
    if MEMBERSHIP_RETIRE_COMMAND_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    content=path.read_bytes()
    if sha256(content).hexdigest()!=MEMBERSHIP_RETIRE_COMMAND_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference=json.loads(content)
    if (reference['source_pins']!=json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256']!=sha256((HERE/'versions/0016_membership_retire_command.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['membership_retire_command']


def trusted_membership_join_command_reference():
    """Independent helper-only fixture, retaining the full historical trust chain."""
    trusted_membership_retire_command_reference()
    path=HERE/'membership-join-command-reference.json'
    if MEMBERSHIP_JOIN_COMMAND_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    content=path.read_bytes()
    if sha256(content).hexdigest()!=MEMBERSHIP_JOIN_COMMAND_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference=json.loads(content)
    if (reference['source_pins']!=json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256']!=sha256((HERE/'versions/0017_membership_join_command.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['membership_join_command']


ACCOUNT_VERIFICATION_ROLE_QUERIES = {
    key.replace('projection','account_verification'): sql.replace(PROJECTION_OWNER, ACCOUNT_VERIFICATION_OWNER)
    for key, sql in PROJECTION_ROLE_QUERIES.items()
}


def verify_account_verification_role(connection, staged=False):
    role = ACCOUNT_VERIFICATION_OWNER
    queries = ACCOUNT_VERIFICATION_ROLE_QUERIES
    if [tuple(r) for r in connection.execute(text(queries['account_verification_role']))] != [(role,False,False,False,False,False,False,False)]:
        raise BaselineError('identity_account_verification_role_unsafe')
    if [tuple(r) for r in connection.execute(text(queries['account_verification_memberships']))] != [(role,'identity_migrator',False,'false','true')]:
        raise BaselineError('identity_account_verification_role_unsafe')
    if not connection.execute(text("SELECT relrowsecurity FROM pg_class WHERE oid='auth.users'::regclass")).scalar_one():
        raise BaselineError('identity_account_verification_auth_rls_required')
    schemas = connection.execute(text("SELECT nspname,p FROM pg_namespace CROSS JOIN unnest(ARRAY['USAGE','CREATE','USAGE WITH GRANT OPTION','CREATE WITH GRANT OPTION']) p WHERE nspname !~ '^pg_' AND nspname<>'information_schema' AND has_schema_privilege(:role,oid,p)"), {'role':role}).all()
    expected = {('auth','USAGE'),('public','USAGE')} | (set() if staged else {('identity','USAGE')})
    if set(map(tuple,schemas)) != expected or connection.execute(text("SELECT has_database_privilege(:role,current_database(),'CREATE')"),{'role':role}).scalar_one():
        raise BaselineError('identity_account_verification_privileges_unsafe')
    columns = connection.execute(text("""SELECT n.nspname,c.relname,a.attname,p FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_attribute a ON a.attrelid=c.oid CROSS JOIN unnest(ARRAY['SELECT','INSERT','UPDATE','REFERENCES']) p
     WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND c.relkind IN ('r','p','v','m','f') AND a.attnum>0 AND NOT a.attisdropped
     AND (:staged OR n.nspname<>'identity') AND has_column_privilege(:role,c.oid,a.attnum,p)"""),{'role':role,'staged':staged}).all()
    if set(map(tuple,columns)) != {('auth','users','id','SELECT'),('auth','users','deleted_at','SELECT')}:
        raise BaselineError('identity_account_verification_privileges_unsafe')
    if connection.execute(text("""SELECT EXISTS(SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
     WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND
     ((c.relkind IN ('r','p','v','m','f') AND (:staged OR n.nspname<>'identity') AND has_table_privilege(:role,c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER'))
     OR (c.relkind='S' AND CASE WHEN c.relkind='S' THEN has_sequence_privilege(:role,c.oid,'USAGE,SELECT,UPDATE') ELSE false END)))"""),{'role':role,'staged':staged}).scalar_one():
        raise BaselineError('identity_account_verification_privileges_unsafe')
    policy = connection.execute(text("SELECT policyname,permissive,roles::text,cmd,qual,with_check FROM pg_policies WHERE schemaname='auth' AND tablename='users' AND roles::text[] && ARRAY[:role,'public']"),{'role':role}).all()
    if list(map(tuple,policy)) != [('identity_account_actor_verification','PERMISSIVE','{identity_account_verification_owner}','SELECT','true',None)]:
        raise BaselineError('identity_account_verification_policy_unsafe')
    if staged:
        dependencies = connection.execute(text(queries['account_verification_dependencies'])).all()
        descriptions = {r[3] for r in dependencies}
        if descriptions != {'schema auth','column id of table auth.users','column deleted_at of table auth.users'} or any(r[2]!='a' for r in dependencies):
            raise BaselineError('identity_account_verification_role_not_staged')


def historical_catalog_fingerprints(connection, snapshot):
    # Validate the exact separately staged Auth preparation even on early returns.
    present = connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='identity_account_verification_owner')")).scalar_one()
    if present:
        verify_account_verification_role(connection, staged=True)
        snapshot['role_memberships'] = [row for row in snapshot['role_memberships']
            if row != [ACCOUNT_VERIFICATION_OWNER,'identity_migrator',False,'false','true']]
    return catalog_fingerprints(snapshot)


def account_actor_catalog_snapshot(connection):
    result = target_catalog_snapshot(connection)
    for key, sql in ACCOUNT_VERIFICATION_ROLE_QUERIES.items():
        rows = [list(r) for r in connection.execute(text(sql))]
        if key.endswith('_dependencies'):
            current = connection.execute(text('SELECT current_database()')).scalar_one()
            for row in rows:
                if row[0] == current: row[0] = 'current_database'
        result[key] = sorted(rows,key=lambda row:json.dumps(row,sort_keys=True))
    for category in ('effective_tables','effective_columns','effective_functions','effective_schemas','effective_sequences'):
        sql = QUERIES[category].replace("'identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin'", "'identity_account_verification_owner'")
        result['account_verification_'+category] = sorted([list(r) for r in connection.execute(text(sql))],key=lambda row:json.dumps(row,sort_keys=True))
    return result


def trusted_account_actor_ensure_reference():
    trusted_membership_join_command_reference()
    path = HERE/'account-actor-ensure-reference.json'
    if ACCOUNT_ACTOR_ENSURE_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    content = path.read_bytes()
    if sha256(content).hexdigest() != ACCOUNT_ACTOR_ENSURE_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference = json.loads(content)
    if (reference['source_pins'] != json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256'] != sha256((HERE/'versions/0018_account_actor_ensure.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['account_actor_ensure']


def trusted_organization_target_reference():
    trusted_account_actor_ensure_reference()
    path = HERE/'organization-target-reference.json'
    if ORGANIZATION_TARGET_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    content = path.read_bytes()
    if sha256(content).hexdigest() != ORGANIZATION_TARGET_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference = json.loads(content)
    if (reference['source_pins'] != json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256'] != sha256((HERE/'versions/0019_organization_target.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['organization_target']


CHECK_READER_ROLE_QUERIES = {
    key.replace('projection', 'check_reader'): sql.replace(PROJECTION_OWNER, CHECK_READER)
    for key, sql in PROJECTION_ROLE_QUERIES.items()
}
# Policy-role dependencies are authority-bearing even without an ACL grant.
# Keep historical projection queries/reference semantics byte-for-byte unchanged.
CHECK_READER_ROLE_QUERIES['check_reader_dependencies'] = CHECK_READER_ROLE_QUERIES['check_reader_dependencies'].replace(
    "s.deptype IN ('a','o')", "s.deptype IN ('a','o','r')")


def verified_access_reader_extension(connection):
    """Acyclic, metadata-only recognition of exactly staged/installed Access15."""
    members=connection.execute(text(CHECK_READER_ROLE_QUERIES['check_reader_memberships'])).all()
    if not members:
        return None
    import sys
    directory=HERE.parent/'migrations'
    previous=list(sys.path)
    try:
        sys.path.insert(0,str(directory))
        import access_baseline as access_catalog
        from access_organization_check_catalog import verify_reader_role
        installed=access_catalog.organization_check_installed(connection)
        verify_reader_role(connection,installed)
        # Staged reader has precisely its Identity20 bridge rights plus this edge.
        # Installed state must validate every Access object/ACL, not just a routine.
        if installed:
            studies=connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='enroll_studies_account')")).scalar_one()
            account_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='change_account_grant')")).scalar_one())
            capability_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='check_account_capability')")).scalar_one())
            discovery_installed=bool(connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='discover_applications')")).scalar_one())
            access_catalog.verify_catalog(connection,'access_0019' if discovery_installed else 'access_0018' if capability_installed else 'access_0017' if account_installed else 'access_0016' if studies else 'access_0015')
        return installed
    except access_catalog.BaselineError:
        raise BaselineError('identity_check_reader_extension_unsafe') from None
    finally:
        sys.path[:]=previous


def verify_check_reader_role(connection, staged=False, legacy=False):
    """Refuse unknown effective authority, including PUBLIC and incoming SET edges."""
    role = CHECK_READER
    flags = [tuple(r) for r in connection.execute(text(CHECK_READER_ROLE_QUERIES['check_reader_role']))]
    if not flags:
        raise BaselineError('identity_check_reader_role_missing')
    if flags != [(role, False, False, False, False, False, False, False)]:
        raise BaselineError('identity_check_reader_role_unsafe')
    if staged:
        # Membership is cluster-global, while the bridge dependencies are per DB.
        # A separately prepared Access database may already retain this one edge.
        # Continue every empty-catalog/effective-right check below before grants.
        members = [tuple(row) for row in connection.execute(text(CHECK_READER_ROLE_QUERIES['check_reader_memberships'])).all()]
        if members not in ([], [(CHECK_READER, 'access_migrator', False, 'false', 'true')]):
            raise BaselineError('identity_check_reader_role_unsafe')
    else:
        extension = verified_access_reader_extension(connection)
        if extension is not None:
            return
        if connection.execute(text(CHECK_READER_ROLE_QUERIES['check_reader_memberships'])).all():
            raise BaselineError('identity_check_reader_role_unsafe')
    dependencies = connection.execute(text(CHECK_READER_ROLE_QUERIES['check_reader_dependencies'])).all()
    expected = set() if staged else {('pg_namespace', 'a', 'schema identity'),
        ('pg_proc', 'a', 'function identity.current_account_organization()')}
    if {(r[1], r[2], r[3]) for r in dependencies} != expected or len(dependencies) != len(expected):
        raise BaselineError('identity_check_reader_role_not_empty' if staged else 'identity_check_reader_dependencies_unsafe')
    schemas = connection.execute(text("""SELECT nspname,p FROM pg_namespace
      CROSS JOIN unnest(ARRAY['USAGE','CREATE','USAGE WITH GRANT OPTION','CREATE WITH GRANT OPTION']) p
      WHERE nspname !~ '^pg_' AND nspname<>'information_schema'
      AND has_schema_privilege(:role,oid,p)"""), {'role': role}).all()
    allowed_schemas = {('public','USAGE')} | (set() if staged else {('identity','USAGE')})
    if set(map(tuple, schemas)) != allowed_schemas or connection.execute(text("SELECT has_database_privilege(:role,current_database(),'CREATE')"), {'role': role}).scalar_one():
        raise BaselineError('identity_check_reader_privileges_unsafe')
    if connection.execute(text("""SELECT EXISTS (
      SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
      WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND
       ((c.relkind IN ('r','p','v','m','f') AND
         (has_table_privilege(:role,c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
          OR has_any_column_privilege(:role,c.oid,'SELECT,INSERT,UPDATE,REFERENCES')
          OR CASE WHEN current_setting('server_version_num')::integer>=170000
            THEN has_table_privilege(:role,c.oid,'MAINTAIN') ELSE false END))
        OR (c.relkind='S' AND CASE WHEN c.relkind='S' THEN has_sequence_privilege(:role,c.oid,'USAGE,SELECT,UPDATE') ELSE false END))
      UNION ALL
      SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
      WHERE n.nspname NOT IN ('pg_catalog','information_schema')
        AND (n.nspname='identity' OR p.prosecdef)
        AND has_function_privilege(:role,p.oid,'EXECUTE')
        -- Exact definitions/owners/ACLs are source-checked by the surrounding
        -- catalog verifier. Trigger-only functions cannot be called as SQL data
        -- routines; these two invokers only read the caller's own JWT context.
        AND p.oid NOT IN ('identity.current_org_id()'::regprocedure,
          'identity.current_member_id()'::regprocedure,
          'identity.handle_new_user()'::regprocedure,
          'identity.log_audit()'::regprocedure,'identity.set_audit_fields()'::regprocedure)
        AND (NOT :legacy OR p.oid NOT IN (
          'identity.authorize(identity.app_permission)'::regprocedure,
          'identity.create_user(text)'::regprocedure,
          'identity.custom_access_token_hook(jsonb)'::regprocedure,
          'public.get_user_roles()'::regprocedure,
          'identity.membership_join_profile_allowed(uuid)'::regprocedure,
          'identity.membership_join_org_allowed(uuid)'::regprocedure))
        AND (:staged OR p.oid<>to_regprocedure('identity.current_account_organization()')::oid
             OR has_function_privilege(:role,p.oid,'EXECUTE WITH GRANT OPTION'))
    )"""), {'role': role, 'staged': staged, 'legacy': legacy}).scalar_one():
        raise BaselineError('identity_check_reader_privileges_unsafe')
    if not staged and not connection.execute(text("SELECT has_function_privilege(:role,'identity.current_account_organization()','EXECUTE')"), {'role': role}).scalar_one():
        raise BaselineError('identity_check_reader_privileges_unsafe')


def check_reader_bridge_catalog_snapshot(connection):
    extension = verified_access_reader_extension(connection)
    result = account_actor_catalog_snapshot(connection)
    current = connection.execute(text('SELECT current_database()')).scalar_one()
    for key, sql in CHECK_READER_ROLE_QUERIES.items():
        rows = [list(r) for r in connection.execute(text(sql))]
        if extension is not None and key.endswith('_memberships'):
            rows = []
        if extension is not None and key.endswith('_dependencies'):
            rows = [row for row in rows if row[3] in ('schema identity','function identity.current_account_organization()')]
        if key.endswith('_dependencies'):
            for row in rows:
                if row[0] == current: row[0] = 'current_database'
        result[key] = sorted(rows, key=lambda row: json.dumps(row, sort_keys=True))
    for category in ('effective_tables','effective_columns','effective_functions','effective_schemas','effective_sequences'):
        # Unlike historical snapshots, include the private history ledger explicitly.
        sql = QUERIES[category].replace("'identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin'", "'access_check_reader'")
        sql = sql.replace(" AND c.relname<>'alembic_version'", '')
        result['check_reader_'+category] = sorted([list(r) for r in connection.execute(text(sql))], key=lambda row: json.dumps(row, sort_keys=True))
    # Exact staged SET-only edge for the next owner is independently verified.
    if connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='identity_studies_owner')")).scalar_one() and not connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity' AND p.proname='prepare_studies_account')")).scalar_one():
        from studies_migration_support import verify_roles
        verify_roles(connection,'identity')
        result['role_memberships']=[row for row in result['role_memberships'] if row!=['identity_studies_owner','identity_migrator',False,'false','true']]
    return result


def trusted_check_reader_bridge_reference():
    trusted_organization_target_reference()
    path = HERE/'check-reader-bridge-reference.json'
    if CHECK_READER_BRIDGE_REFERENCE_SHA256 is None or not path.exists():
        raise BaselineError('identity_reference_unavailable')
    content = path.read_bytes()
    if sha256(content).hexdigest() != CHECK_READER_BRIDGE_REFERENCE_SHA256:
        raise BaselineError('identity_reference_unavailable')
    reference = json.loads(content)
    if (reference['source_pins'] != json.loads((HERE/'source-pins.json').read_text())
        or reference['migration_sha256'] != sha256((HERE/'versions/0020_check_reader_bridge.py').read_bytes()).hexdigest()):
        raise BaselineError('identity_reference_unavailable')
    return reference['check_reader_bridge']
