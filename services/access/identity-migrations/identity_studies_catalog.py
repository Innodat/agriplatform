"""Source-bound Identity21 extension, retaining immutable historical references."""
import json
from hashlib import sha256
from pathlib import Path
from sqlalchemy import text
from studies_migration_support import verify_roles
HERE=Path(__file__).parent
REFERENCE_SHA256='87a95ea22f9d2314fc81eaf7ac9f9f1150b1ee169d83078900d37fb9235b2f6d'

def snapshot(connection):
    from identity_baseline import check_reader_bridge_catalog_snapshot
    result=check_reader_bridge_catalog_snapshot(connection)
    roles=('identity_studies_owner','identity_studies_reader_runtime','identity_studies_setup_runtime')
    for role in roles:
        result[role+'_role']=[list(row) for row in connection.execute(text('SELECT rolname,rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,rolreplication,rolbypassrls FROM pg_roles WHERE rolname=:role'),{'role':role})]
    return result

def verify_studies_catalog(connection):
    from identity_baseline import BaselineError,trusted_check_reader_bridge_reference,catalog_fingerprints,compare_catalog
    trusted_check_reader_bridge_reference()
    verify_roles(connection,'identity')
    path=HERE/'studies-setup-reference.json'
    if REFERENCE_SHA256 is None or not path.is_file() or sha256(path.read_bytes()).hexdigest()!=REFERENCE_SHA256:
        raise BaselineError('identity_studies_reference_unavailable')
    reference=json.loads(path.read_bytes())
    if reference['migration_sha256']!=sha256((HERE/'versions/0021_studies_account_setup.py').read_bytes()).hexdigest():
        raise BaselineError('identity_studies_reference_unavailable')
    compare_catalog(catalog_fingerprints(snapshot(connection)),reference['catalog'])
