"""Independently rehearsed person-link catalog; missing evidence fails closed."""
from hashlib import sha256
import json
from pathlib import Path
from identity_studies_catalog import snapshot
HERE=Path(__file__).parent
REFERENCE_SHA256='440d93b513ee0f19a6311cd628e2e67b0f72b28a36c836dcbbfbbadf8a5eb989'

def reference_document(connection):
    """Root-only rehearsal recorder input; never approves a target at runtime."""
    from identity_baseline import catalog_fingerprints
    return dict(migration_sha256=sha256((HERE/'versions/0022_person_links.py').read_bytes()).hexdigest(),
        predecessor_reference_sha256=sha256((HERE/'studies-setup-reference.json').read_bytes()).hexdigest(),
        catalog=catalog_fingerprints(snapshot(connection)))

def verify_person_catalog(connection):
    from studies_migration_support import verify_roles
    verify_roles(connection,'identity')
    from identity_baseline import BaselineError,trusted_check_reader_bridge_reference,compare_catalog
    from identity_studies_catalog import REFERENCE_SHA256 as previous
    trusted_check_reader_bridge_reference()
    if sha256((HERE/'studies-setup-reference.json').read_bytes()).hexdigest()!=previous:
        raise BaselineError('identity_person_reference_unavailable')
    studies_reference=json.loads((HERE/'studies-setup-reference.json').read_bytes())
    if studies_reference.get('migration_sha256')!=sha256((HERE/'versions/0021_studies_account_setup.py').read_bytes()).hexdigest():
        raise BaselineError('identity_person_reference_unavailable')
    path=HERE/'person-links-reference.json'
    if REFERENCE_SHA256 is None or not path.is_file() or sha256(path.read_bytes()).hexdigest()!=REFERENCE_SHA256:
        raise BaselineError('identity_person_reference_unavailable')
    reference=json.loads(path.read_bytes())
    actual=reference_document(connection)
    if reference.get('migration_sha256')!=actual['migration_sha256'] or reference.get('predecessor_reference_sha256')!=actual['predecessor_reference_sha256']:
        raise BaselineError('identity_person_reference_unavailable')
    compare_catalog(actual['catalog'],reference['catalog'])
