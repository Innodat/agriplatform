"""Access19 source-bound discovery catalogue and bounded registered app set."""
from hashlib import sha256
import json
from pathlib import Path
from sqlalchemy import text
HERE=Path(__file__).parent
REFERENCE_SHA256='7f75626830545a173cd3417a8080f2a201bf373cd1fc4d55575402682df28bf4'  # Published independently from the guarded clean rehearsal.

def verify_role(connection):
    from access_baseline import BaselineError
    role='access_discovery_owner'
    flags=connection.execute(text("SELECT rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit FROM pg_roles WHERE rolname='access_discovery_owner'")).one_or_none()
    edges=[tuple(row) for row in connection.execute(text("SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,inherit_option,set_option FROM pg_auth_members WHERE roleid=to_regrole('access_discovery_owner') OR member=to_regrole('access_discovery_owner')"))]
    if flags is None or tuple(flags)!=(False,)*7 or edges!=[(role,'access_migrator',False,False,True)]:raise BaselineError('discovery_owner_role_unsafe')
    if connection.execute(text("SELECT has_database_privilege('access_discovery_owner',current_database(),'CREATE')")).scalar_one():raise BaselineError('discovery_owner_role_unsafe')

def snapshot(connection):
    from access_account_grant_catalog import snapshot as previous
    result=previous(connection)
    result['discovery_columns']=[list(row) for row in connection.execute(text("SELECT n.nspname,c.relname,a.attname,p FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace CROSS JOIN unnest(ARRAY['SELECT','INSERT','UPDATE','REFERENCES']) p WHERE n.nspname IN ('access','identity') AND c.relkind IN ('r','p') AND a.attnum>0 AND NOT a.attisdropped AND has_column_privilege('access_discovery_owner',c.oid,a.attnum,p) ORDER BY 1,2,3,4"))]
    result['discovery_functions']=[list(row) for row in connection.execute(text("SELECT n.nspname,p.proname,pg_get_function_identity_arguments(p.oid) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname IN ('access','identity') AND has_function_privilege('access_discovery_owner',p.oid,'EXECUTE') ORDER BY 1,2,3"))]
    return result

def reference_document(connection):
    from access_account_grant_catalog import fingerprints
    return dict(migration_sha256=sha256((HERE/'versions/0019_discovery.py').read_bytes()).hexdigest(),predecessor_reference_sha256=sha256((HERE/'current-capabilities-reference.json').read_bytes()).hexdigest(),catalog=fingerprints(snapshot(connection)))

def verify_configuration(connection):
    """Access-owner release check; cross-owner catalogue inspection reads no rows."""
    from access_baseline import BaselineError
    if connection.execute(text('SELECT count(*) FROM access.applications')).scalar_one()>128:raise BaselineError('discovery_catalogue_oversized')

def verify_discovery_catalog(connection):
    from access_baseline import BaselineError,verify_operator_roles
    from access_capability_catalog import REFERENCE_SHA256 as previous,verify_reader_role,verify_predecessor_sources
    from access_account_grant_catalog import verify_runtime_role,REFERENCE_SHA256 as account_reference
    from access_organization_check_catalog import verify_reader_role as old_reader
    from studies_migration_support import verify_roles
    verify_roles(connection,'access');verify_operator_roles(connection);old_reader(connection,installed=True)
    account_path=HERE/'account-grants-reference.json'
    if sha256(account_path.read_bytes()).hexdigest()!=account_reference or json.loads(account_path.read_bytes()).get('migration_sha256')!=sha256((HERE/'versions/0017_account_grants.py').read_bytes()).hexdigest():raise BaselineError('discovery_predecessor_unavailable')
    verify_predecessor_sources(json.loads(account_path.read_bytes()))
    verify_role(connection);verify_runtime_role(connection);verify_reader_role(connection,installed=True)
    predecessor=HERE/'current-capabilities-reference.json'
    if sha256(predecessor.read_bytes()).hexdigest()!=previous or json.loads(predecessor.read_bytes()).get('migration_sha256')!=sha256((HERE/'versions/0018_current_capabilities.py').read_bytes()).hexdigest():raise BaselineError('discovery_predecessor_unavailable')
    path=HERE/'discovery-reference.json'
    if REFERENCE_SHA256 is None or not path.is_file() or sha256(path.read_bytes()).hexdigest()!=REFERENCE_SHA256:raise BaselineError('discovery_reference_unavailable')
    if json.loads(path.read_bytes())!=reference_document(connection):raise BaselineError('access_catalog_mismatch')
