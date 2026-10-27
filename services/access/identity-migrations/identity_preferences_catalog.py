"""Source-bound preference extension of the existing Identity owner evidence."""
from hashlib import sha256
import json
from pathlib import Path
from sqlalchemy import text
HERE=Path(__file__).parent
REFERENCE_SHA256='93b3f573e4df2c92d6c936674e552bdadd8d6b2f68e22a3134c7ceaf9400683f'

def snapshot(connection):
    from identity_studies_catalog import snapshot as previous
    from identity_baseline import QUERIES
    result=previous(connection)
    result['preferences_role']=[list(row) for row in connection.execute(text("SELECT rolname,rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,rolreplication,rolbypassrls FROM pg_roles WHERE rolname='identity_preferences_runtime'"))]
    result['preferences_memberships']=[list(row) for row in connection.execute(text("SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option FROM pg_auth_members WHERE roleid='identity_preferences_runtime'::regrole OR member='identity_preferences_runtime'::regrole"))]
    for category in ('effective_tables','effective_columns','effective_functions','effective_schemas','effective_sequences'):
        query=QUERIES[category].replace("'identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin'","'identity_preferences_runtime'")
        query=query.replace(" AND c.relname<>'alembic_version'",'')
        result['preferences_'+category]=sorted([list(row) for row in connection.execute(text(query))],key=lambda row:json.dumps(row,sort_keys=True))
    return result

def reference_document(connection):
    from identity_baseline import catalog_fingerprints
    return dict(migration_sha256=sha256((HERE/'versions/0023_language_preferences.py').read_bytes()).hexdigest(),
                predecessor_reference_sha256=sha256((HERE/'person-links-reference.json').read_bytes()).hexdigest(),
                catalog=catalog_fingerprints(snapshot(connection)))

def verify_preferences_catalog(connection):
    from studies_migration_support import verify_roles
    verify_roles(connection,'identity')
    from identity_baseline import BaselineError,compare_catalog,trusted_check_reader_bridge_reference
    import identity_studies_catalog as studies
    import identity_person_catalog as person
    trusted_check_reader_bridge_reference()
    for filename,expected,migration in [('studies-setup-reference.json',studies.REFERENCE_SHA256,'0021_studies_account_setup.py'),('person-links-reference.json',person.REFERENCE_SHA256,'0022_person_links.py')]:
        path=HERE/filename
        if not path.is_file() or sha256(path.read_bytes()).hexdigest()!=expected:raise BaselineError('identity_preferences_reference_unavailable')
        if json.loads(path.read_bytes()).get('migration_sha256')!=sha256((HERE/'versions'/migration).read_bytes()).hexdigest():raise BaselineError('identity_preferences_reference_unavailable')
    path=HERE/'language-preferences-reference.json'
    if REFERENCE_SHA256 is None or not path.is_file() or sha256(path.read_bytes()).hexdigest()!=REFERENCE_SHA256:raise BaselineError('identity_preferences_reference_unavailable')
    expected=json.loads(path.read_bytes());actual=reference_document(connection)
    if expected.get('migration_sha256')!=actual['migration_sha256'] or expected.get('predecessor_reference_sha256')!=actual['predecessor_reference_sha256']:raise BaselineError('identity_preferences_reference_unavailable')
    compare_catalog(actual['catalog'],expected['catalog'])
