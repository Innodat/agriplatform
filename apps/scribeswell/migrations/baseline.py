"""Adoption only: inspect pinned supported catalogue before any ledger DDL."""
import hashlib
import json
from pathlib import Path
from catalogue import snapshot
APP = Path(__file__).resolve().parents[1]
LEGACY_REVISION = 'scribeswell_0001'
REVISION = 'scribeswell_0002'
SUPPORTED_REVISIONS = (LEGACY_REVISION, REVISION)
PINS = {
 'supabase/migrations/20260614000000_scribeswell_create_schema.sql': 'b5140822e9655b933a98f17df8b7a7cb8424246991e168238ba736a319b511f0',
 'deployment/bootstrap/001_direct_database_roles.sql': 'd03e8e34227fe73d0572d74e9c799a76982ed6ec83a774fec86e2c757d54c66d',
}
class BaselineError(RuntimeError):
    pass

def verify_pins():
    for relative, digest in PINS.items():
        if hashlib.sha256((APP / relative).read_bytes()).hexdigest() != digest:
            raise BaselineError('scribeswell_reference_pin_mismatch')

def ledger(connection):
    if not connection.exec_driver_sql("SELECT to_regclass('scribeswell.alembic_version')").scalar():
        return None
    relation = connection.exec_driver_sql("""SELECT c.relkind,pg_get_userbyid(c.relowner),c.relrowsecurity,c.relforcerowsecurity,c.reloptions,c.relpersistence,c.relispartition,c.reltablespace FROM pg_class c WHERE c.oid='scribeswell.alembic_version'::regclass""").one()
    columns = connection.exec_driver_sql("""SELECT attname,format_type(atttypid,atttypmod),attnotnull,attidentity,attgenerated,attacl FROM pg_attribute WHERE attrelid='scribeswell.alembic_version'::regclass AND attnum>0 ORDER BY attnum""").fetchall()
    constraints = connection.exec_driver_sql("SELECT conname,pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='scribeswell.alembic_version'::regclass").fetchall()
    acl = connection.exec_driver_sql("""SELECT 1 FROM pg_class c,LATERAL aclexplode(COALESCE(c.relacl,acldefault('r',c.relowner))) a WHERE c.oid='scribeswell.alembic_version'::regclass AND (a.grantee<>c.relowner OR a.grantor<>c.relowner)""").fetchall()
    if tuple(relation) != ('r','scribeswell_migrator',False,False,None,'p',False,0) or [tuple(x) for x in columns] != [('version_num','character varying(32)',True,'','',None)] or [tuple(x) for x in constraints] != [('alembic_version_pkc','PRIMARY KEY (version_num)')] or acl:
        raise BaselineError('scribeswell_ledger_invalid')
    rows = connection.exec_driver_sql('SELECT version_num FROM scribeswell.alembic_version').fetchall()
    if len(rows) != 1 or rows[0][0] not in SUPPORTED_REVISIONS:
        raise BaselineError('scribeswell_ledger_invalid')
    extras = connection.exec_driver_sql("""SELECT 1 FROM pg_attrdef WHERE adrelid='scribeswell.alembic_version'::regclass
 UNION ALL SELECT 1 FROM pg_trigger WHERE tgrelid='scribeswell.alembic_version'::regclass
 UNION ALL SELECT 1 FROM pg_rewrite WHERE ev_class='scribeswell.alembic_version'::regclass
 UNION ALL SELECT 1 FROM pg_index WHERE indrelid='scribeswell.alembic_version'::regclass AND (NOT indisvalid OR NOT indisready OR NOT indislive OR NOT indisprimary)
 UNION ALL SELECT 1 WHERE (SELECT count(*) FROM pg_index WHERE indrelid='scribeswell.alembic_version'::regclass)<>1
 UNION ALL SELECT 1 WHERE NOT has_table_privilege(current_user,'scribeswell.alembic_version','SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')""").first()
    owner_acl = connection.exec_driver_sql("""SELECT a.privilege_type,a.is_grantable FROM pg_class c,LATERAL aclexplode(COALESCE(c.relacl,acldefault('r',c.relowner))) a WHERE c.oid='scribeswell.alembic_version'::regclass ORDER BY 1""").fetchall()
    expected_acl = [(privilege,False) for privilege in ['DELETE','INSERT','MAINTAIN','REFERENCES','SELECT','TRIGGER','TRUNCATE','UPDATE']]
    if [tuple(row) for row in owner_acl] != expected_acl:
        raise BaselineError('scribeswell_ledger_invalid')
    if extras:
        raise BaselineError('scribeswell_ledger_invalid')
    return rows[0][0]

def preflight(connection):
    verify_pins()
    version = int(connection.exec_driver_sql('SHOW server_version_num').scalar())
    if not 170000 <= version < 180000:
        raise BaselineError('scribeswell_unsupported_postgres_profile')
    for name in ('scribeswell_runtime','scribeswell_import'):
        role = connection.exec_driver_sql("SELECT rolcanlogin,rolsuper,rolbypassrls,rolcreatedb,rolcreaterole,rolreplication,rolinherit FROM pg_roles WHERE rolname=%s",(name,)).first()
        if role is None or tuple(role)!=(True,False,False,False,False,False,False):
            raise BaselineError('scribeswell_unsafe_direct_roles')
        if connection.exec_driver_sql("SELECT 1 FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.member WHERE r.rolname=%s",(name,)).first():
            raise BaselineError('scribeswell_unsafe_direct_memberships')
    authority = connection.exec_driver_sql("""SELECT session_user,current_user,rolcanlogin,rolsuper,rolbypassrls,rolcreatedb,rolcreaterole,rolreplication,rolinherit FROM pg_roles WHERE rolname=current_user""").one()
    if tuple(authority) != ('scribeswell_migrator','scribeswell_migrator',True,False,False,False,False,False,False):
        raise BaselineError('scribeswell_unsafe_authority')
    if connection.exec_driver_sql("""SELECT 1 FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.member OR r.oid=m.roleid WHERE r.rolname='scribeswell_migrator'""").first():
        raise BaselineError('scribeswell_unsafe_membership')
    if connection.exec_driver_sql("""SELECT 1 FROM pg_db_role_setting s JOIN pg_roles r ON r.oid=s.setrole WHERE r.rolname='scribeswell_migrator' AND EXISTS (SELECT FROM unnest(s.setconfig) x WHERE split_part(x,'=',1) NOT IN ('statement_timeout','lock_timeout','idle_in_transaction_session_timeout'))""").first():
        raise BaselineError('scribeswell_unsafe_role_settings')
    # Ownership and explicit authority outside this silo are unsupported. PUBLIC
    # system/catalogue read access is not an app-specific privilege.
    if connection.exec_driver_sql("""WITH actor AS (SELECT oid FROM pg_roles WHERE rolname='scribeswell_migrator')
 SELECT 1 FROM pg_namespace n,actor WHERE n.nspname<>'scribeswell' AND n.nspowner=actor.oid
 UNION ALL SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace,actor WHERE n.nspname NOT IN ('scribeswell','pg_catalog','information_schema') AND left(n.nspname,8)<>'pg_toast' AND left(n.nspname,7)<>'pg_temp' AND c.relowner=actor.oid
 UNION ALL SELECT 1 FROM pg_namespace n WHERE n.nspname NOT IN ('scribeswell','pg_catalog','information_schema') AND left(n.nspname,3)<>'pg_' AND has_schema_privilege(current_user,n.oid,'CREATE')
 UNION ALL SELECT 1 FROM pg_database d,actor WHERE d.datdba=actor.oid
 UNION ALL SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname NOT IN ('scribeswell','pg_catalog','information_schema') AND left(n.nspname,3)<>'pg_' AND c.relkind IN ('r','p','v','m','f','S') AND has_schema_privilege(current_user,n.oid,'USAGE') AND CASE WHEN c.relkind='S' THEN has_sequence_privilege(current_user,c.oid,'USAGE,SELECT,UPDATE') ELSE has_table_privilege(current_user,c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') END
 UNION ALL SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname NOT IN ('scribeswell','pg_catalog','information_schema') AND left(n.nspname,3)<>'pg_' AND c.relkind IN ('r','p','v','m','f') AND has_schema_privilege(current_user,n.oid,'USAGE') AND has_any_column_privilege(current_user,c.oid,'SELECT,INSERT,UPDATE,REFERENCES')
 UNION ALL SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname NOT IN ('scribeswell','pg_catalog','information_schema') AND left(n.nspname,3)<>'pg_' AND p.prosecdef AND has_schema_privilege(current_user,n.oid,'USAGE') AND has_function_privilege(current_user,p.oid,'EXECUTE')
 UNION ALL SELECT 1 FROM pg_database d WHERE has_database_privilege(current_user,d.oid,'CREATE')
 UNION ALL SELECT 1 FROM pg_default_acl d,LATERAL aclexplode(d.defaclacl) a,actor WHERE d.defaclrole<>actor.oid AND a.grantee=actor.oid
 UNION ALL SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace,actor WHERE p.proowner=actor.oid AND n.nspname<>'scribeswell'
 UNION ALL SELECT 1 FROM pg_namespace n,LATERAL aclexplode(n.nspacl) a,actor WHERE n.nspname<>'scribeswell' AND a.grantee=actor.oid
 UNION ALL SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace,LATERAL aclexplode(c.relacl) a,actor WHERE n.nspname<>'scribeswell' AND a.grantee=actor.oid
 UNION ALL SELECT 1 FROM pg_attribute col JOIN pg_class c ON c.oid=col.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace,LATERAL aclexplode(col.attacl) a,actor WHERE n.nspname<>'scribeswell' AND a.grantee=actor.oid
 UNION ALL SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace,LATERAL aclexplode(p.proacl) a,actor WHERE a.grantee=actor.oid AND n.nspname<>'scribeswell'
 UNION ALL SELECT 1 FROM pg_default_acl d,actor WHERE d.defaclnamespace=0 AND d.defaclrole=actor.oid
 UNION ALL SELECT 1 FROM pg_database d,LATERAL aclexplode(d.datacl) a,actor WHERE a.grantee=actor.oid AND a.privilege_type='CREATE'
 """).first():
        raise BaselineError('scribeswell_cross_owner_authority')
    connection.exec_driver_sql("SELECT pg_advisory_xact_lock(hashtext('scribeswell-owned-migrations'))")
    state = ledger(connection)
    head = state == REVISION
    expected = json.loads((APP / ('migrations/reference-head.json' if head else 'migrations/reference.json')).read_text())
    if snapshot(connection, head=head) != expected:
        raise BaselineError('scribeswell_catalogue_mismatch')
    if head:
        if connection.exec_driver_sql('SELECT singleton,enforcement FROM scribeswell.corpus_fence_control').fetchall() != [(True,False)]:
            raise BaselineError('scribeswell_dormant_fence_required')
        if connection.exec_driver_sql('SELECT 1 FROM scribeswell.corpus_epoch UNION ALL SELECT 1 FROM scribeswell.corpus_write_binding').first():
            raise BaselineError('scribeswell_dormant_fence_required')
    return state
