"""Source-bound Identity27 reference observation; historical heads remain intact."""
from hashlib import sha256
from pathlib import Path
import json
from sqlalchemy import text
HERE=Path(__file__).parent
REFERENCE_SHA256='09e5c4f8895ae7ba33a3a7863e9c7bc31e747d10cc54301f1f9c53d1dbbabbbe'

def reference_document(connection):
    from identity_baseline import catalog_fingerprints,QUERIES
    from identity_discovery_catalog import snapshot
    actual=snapshot(connection)
    actual['people_setup_role']=[list(row) for row in connection.execute(text("SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit FROM pg_roles WHERE rolname='identity_people_setup_runtime'"))]
    actual['people_setup_memberships']=[list(row) for row in connection.execute(text("SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,inherit_option,set_option FROM pg_auth_members WHERE roleid=to_regrole('identity_people_setup_runtime') OR member=to_regrole('identity_people_setup_runtime')"))]
    for category in ('effective_tables','effective_columns','effective_functions','effective_schemas','effective_sequences'):
        query=QUERIES[category].replace("'identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin'","'identity_people_setup_runtime'")
        actual['people_setup_'+category]=sorted([list(row) for row in connection.execute(text(query))],key=lambda r:json.dumps(r,sort_keys=True))
    return dict(migration_sha256=sha256((HERE/'versions/0027_people_setup_references.py').read_bytes()).hexdigest(),predecessor_reference_sha256=sha256((HERE/'discovery-reference.json').read_bytes()).hexdigest(),catalog=catalog_fingerprints(actual))

def verify_people_setup_catalog(connection):
    from identity_baseline import BaselineError,compare_catalog
    from identity_discovery_catalog import REFERENCE_SHA256 as previous,verify_role
    from identity_account_grant_catalog import trusted_predecessors
    from studies_migration_support import verify_roles
    trusted_predecessors();verify_roles(connection,'identity');verify_role(connection)
    verify_role(connection,'access_discovery_owner','access_migrator')
    before=HERE/'discovery-reference.json';path=HERE/'people-setup-reference.json'
    if sha256(before.read_bytes()).hexdigest()!=previous or json.loads(before.read_bytes())['migration_sha256']!=sha256((HERE/'versions/0026_discovery.py').read_bytes()).hexdigest():raise BaselineError('people_setup_predecessor_unavailable')
    if REFERENCE_SHA256 is None or not path.is_file() or sha256(path.read_bytes()).hexdigest()!=REFERENCE_SHA256:raise BaselineError('people_setup_reference_unavailable')
    expected=json.loads(path.read_bytes());actual=reference_document(connection)
    if any(expected.get(k)!=actual[k] for k in ('migration_sha256','predecessor_reference_sha256')):raise BaselineError('people_setup_reference_unavailable')
    compare_catalog(actual['catalog'],expected['catalog'])
