"""Independent root-published Identity25 projection catalog and source provenance."""
from hashlib import sha256
import json
from pathlib import Path
from identity_preferences_catalog import snapshot
HERE=Path(__file__).parent
REFERENCE_SHA256='ddfefbeb1ea8fa5933a0bddbd4f1265bd38d1c0dd3b171453fb7512f9012ba24'

def reference_document(connection):
    from identity_baseline import catalog_fingerprints
    return dict(migration_sha256=sha256((HERE/'versions/0025_capability_reader.py').read_bytes()).hexdigest(),predecessor_reference_sha256=sha256((HERE/'account-grant-target-reference.json').read_bytes()).hexdigest(),catalog=catalog_fingerprints(snapshot(connection)))

def verify_capability_catalog(connection):
    from identity_baseline import BaselineError,compare_catalog
    from identity_account_grant_catalog import trusted_predecessors,REFERENCE_SHA256 as previous
    from studies_migration_support import verify_roles
    trusted_predecessors();verify_roles(connection,'identity')
    predecessor=HERE/'account-grant-target-reference.json'
    if sha256(predecessor.read_bytes()).hexdigest()!=previous or json.loads(predecessor.read_bytes()).get('migration_sha256')!=sha256((HERE/'versions/0024_account_grant_target.py').read_bytes()).hexdigest():raise BaselineError('identity_capability_predecessor_unavailable')
    path=HERE/'capability-reader-reference.json'
    if REFERENCE_SHA256 is None or not path.is_file() or sha256(path.read_bytes()).hexdigest()!=REFERENCE_SHA256:raise BaselineError('identity_capability_reference_unavailable')
    expected=json.loads(path.read_bytes());actual=reference_document(connection)
    if any(expected.get(key)!=actual[key] for key in ('migration_sha256','predecessor_reference_sha256')):raise BaselineError('identity_capability_reference_unavailable')
    compare_catalog(actual['catalog'],expected['catalog'])
