"""Independent root-rehearsed selected-account projection catalog."""
from hashlib import sha256
import json
from pathlib import Path
from identity_preferences_catalog import snapshot
HERE=Path(__file__).parent
REFERENCE_SHA256='ec933c81061a5d4de659feac5961436a93a13650b6d22da727406e59ec3d6825'

def reference_document(connection):
    from identity_baseline import catalog_fingerprints
    return dict(migration_sha256=sha256((HERE/'versions/0024_account_grant_target.py').read_bytes()).hexdigest(),
        predecessor_reference_sha256=sha256((HERE/'language-preferences-reference.json').read_bytes()).hexdigest(),
        catalog=catalog_fingerprints(snapshot(connection)))

def verify_account_grant_catalog(connection):
    from studies_migration_support import verify_roles
    verify_roles(connection,'identity')
    from identity_baseline import BaselineError,compare_catalog
    trusted_predecessors()
    path=HERE/'account-grant-target-reference.json'
    if REFERENCE_SHA256 is None or not path.is_file() or sha256(path.read_bytes()).hexdigest()!=REFERENCE_SHA256:raise BaselineError('identity_account_grant_reference_unavailable')
    expected=json.loads(path.read_bytes());actual=reference_document(connection)
    if any(expected.get(k)!=actual[k] for k in ('migration_sha256','predecessor_reference_sha256')):raise BaselineError('identity_account_grant_reference_unavailable')
    compare_catalog(actual['catalog'],expected['catalog'])


def trusted_predecessors():
    from identity_baseline import BaselineError,trusted_check_reader_bridge_reference
    from identity_preferences_catalog import REFERENCE_SHA256 as previous
    trusted_check_reader_bridge_reference()
    if sha256((HERE/'language-preferences-reference.json').read_bytes()).hexdigest()!=previous:raise BaselineError('identity_account_grant_reference_unavailable')
    import identity_studies_catalog as studies
    import identity_person_catalog as person
    import identity_preferences_catalog as preferences
    for filename,expected,migration in (
        ('studies-setup-reference.json',studies.REFERENCE_SHA256,'0021_studies_account_setup.py'),
        ('person-links-reference.json',person.REFERENCE_SHA256,'0022_person_links.py'),
        ('language-preferences-reference.json',preferences.REFERENCE_SHA256,'0023_language_preferences.py')):
        path=HERE/filename
        if expected is None or not path.is_file() or sha256(path.read_bytes()).hexdigest()!=expected:raise BaselineError('identity_account_grant_reference_unavailable')
        reference=json.loads(path.read_bytes())
        if reference.get('migration_sha256')!=sha256((HERE/'versions'/migration).read_bytes()).hexdigest():raise BaselineError('identity_account_grant_reference_unavailable')
