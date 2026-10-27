"""Identity26 source-bound discovery catalogue; historical references stay immutable."""
from hashlib import sha256
import json
from pathlib import Path
from sqlalchemy import text
HERE=Path(__file__).parent
REFERENCE_SHA256='3878dbe7761b1067f01491171336d96d86dd21e2aede985ec107b50bdedcb475'  # Independently republished after private-owner RLS compatibility repair.

def verify_role(connection,role='identity_discovery_owner',migrator='identity_migrator',empty=False):
    from identity_baseline import BaselineError
    flags=connection.execute(text('SELECT rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit FROM pg_roles WHERE rolname=:role'),{'role':role}).one_or_none()
    edges=[tuple(row) for row in connection.execute(text('SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,inherit_option,set_option FROM pg_auth_members WHERE roleid=to_regrole(:role) OR member=to_regrole(:role)'),{'role':role})]
    if flags is None or tuple(flags)!=(False,)*7 or edges!=[(role,migrator,False,False,True)]:raise BaselineError('discovery_owner_role_unsafe')
    if connection.execute(text("SELECT has_database_privilege(:role,current_database(),'CREATE')"),{'role':role}).scalar_one():raise BaselineError('discovery_owner_role_unsafe')
    if empty and connection.execute(text("SELECT count(*) FROM pg_shdepend WHERE refclassid='pg_authid'::regclass AND refobjid=to_regrole(:role) AND deptype IN ('a','o','r') AND dbid IN (0,(SELECT oid FROM pg_database WHERE datname=current_database()))"),{'role':role}).scalar_one():raise BaselineError('discovery_owner_not_empty')

def snapshot(connection):
    from identity_preferences_catalog import snapshot as previous
    from identity_baseline import QUERIES
    result=previous(connection)
    for category in ('effective_tables','effective_columns','effective_functions','effective_schemas','effective_sequences'):
        query=QUERIES[category].replace("'identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin'","'identity_discovery_owner','access_discovery_owner'")
        result['discovery_'+category]=sorted([list(row) for row in connection.execute(text(query))],key=lambda row:json.dumps(row,sort_keys=True))
    return result

def reference_document(connection):
    from identity_baseline import catalog_fingerprints
    return dict(migration_sha256=sha256((HERE/'versions/0026_discovery.py').read_bytes()).hexdigest(),predecessor_reference_sha256=sha256((HERE/'capability-reader-reference.json').read_bytes()).hexdigest(),catalog=catalog_fingerprints(snapshot(connection)))

def verify_discovery_catalog(connection):
    from identity_baseline import BaselineError,compare_catalog
    from identity_capability_catalog import REFERENCE_SHA256 as previous
    from identity_account_grant_catalog import trusted_predecessors,REFERENCE_SHA256 as account_reference
    from studies_migration_support import verify_roles
    verify_roles(connection,'identity');trusted_predecessors()
    account_path=HERE/'account-grant-target-reference.json'
    if sha256(account_path.read_bytes()).hexdigest()!=account_reference or json.loads(account_path.read_bytes()).get('migration_sha256')!=sha256((HERE/'versions/0024_account_grant_target.py').read_bytes()).hexdigest():raise BaselineError('identity_discovery_predecessor_unavailable')
    verify_role(connection)
    verify_role(connection,'access_discovery_owner','access_migrator')
    predecessor=HERE/'capability-reader-reference.json'
    if sha256(predecessor.read_bytes()).hexdigest()!=previous or json.loads(predecessor.read_bytes()).get('migration_sha256')!=sha256((HERE/'versions/0025_capability_reader.py').read_bytes()).hexdigest():raise BaselineError('identity_discovery_predecessor_unavailable')
    path=HERE/'discovery-reference.json'
    if REFERENCE_SHA256 is None or not path.is_file() or sha256(path.read_bytes()).hexdigest()!=REFERENCE_SHA256:raise BaselineError('identity_discovery_reference_unavailable')
    expected=json.loads(path.read_bytes());actual=reference_document(connection)
    if any(expected.get(key)!=actual[key] for key in ('migration_sha256','predecessor_reference_sha256')):raise BaselineError('identity_discovery_reference_unavailable')
    compare_catalog(actual['catalog'],expected['catalog'])
