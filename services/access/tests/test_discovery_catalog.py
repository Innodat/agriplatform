"""Discovery heads retain pre-existing inherited-role and source safety checks."""
from pathlib import Path
import sys
import pytest
OWNER=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(OWNER/'identity-migrations'))
sys.path.insert(0,str(OWNER/'migrations'))
import identity_discovery_catalog as identity
import access_discovery_catalog as access
import studies_migration_support as studies

# Exact function metadata from the Access19 DDL and its Identity26 dependency.
# Its ten-row digest matches the immutable Access discovery reference; Identity28
# deliberately removes only these three inherited trigger-attachment permissions.
DISCOVERY_FUNCTIONS=sorted([
    ['access','discover_applications',''],
    ['access','discover_organizations','p_app_id text, p_after_org_id uuid, p_page_size integer'],
    ['access','discovery_memberships',''],
    ['identity','current_account_memberships',''],
    ['identity','current_member_id',''],
    ['identity','current_org_id',''],
    ['identity','discovery_account_context',''],
])
LEGACY_HELPERS=[['identity',name,''] for name in ('handle_new_user','log_audit','set_audit_fields')]


@pytest.fixture
def discovery_verifier(monkeypatch):
    """Exercise actual head comparison with the other native-unchanged categories.

    The coordinated rollback-only diagnosis found ONLY discovery_functions changed.
    This double supplies those already qualified category digests, not SQL authority.
    """
    import copy,json
    from types import SimpleNamespace
    import access_baseline as baseline
    import access_capability_catalog as capability
    import access_account_grant_catalog as account
    import access_organization_check_catalog as organization
    monkeypatch.setattr(studies,'verify_roles',lambda *_:None)
    monkeypatch.setattr(baseline,'verify_operator_roles',lambda *_:None)
    monkeypatch.setattr(organization,'verify_reader_role',lambda *_,**__:None)
    monkeypatch.setattr(capability,'verify_reader_role',lambda *_,**__:None)
    monkeypatch.setattr(account,'verify_runtime_role',lambda *_:None)
    monkeypatch.setattr(access,'verify_role',lambda *_:None)
    expected=json.loads((access.HERE/'discovery-reference.json').read_bytes())
    original=access.reference_document

    def verify(functions,hardened,deny_identity_usage=False):
        snapshot={'discovery_functions':copy.deepcopy(functions)}
        untouched=copy.deepcopy(snapshot)
        monkeypatch.setattr(access,'snapshot',lambda _:snapshot)
        class MetadataConnection:
            def execute(self,sql):
                if deny_identity_usage and str(sql)=="SELECT to_regprocedure('identity.actor_displays(uuid[])') IS NOT NULL":
                    from sqlalchemy.exc import ProgrammingError
                    raise ProgrammingError(str(sql),{},Exception('synthetic_identity_schema_usage_denied'))
                assert str(sql)=="SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='identity' AND p.proname='actor_displays' AND p.prokind='f' AND p.pronargs=1 AND p.proargtypes[0]='pg_catalog.uuid[]'::regtype)"
                return SimpleNamespace(scalar_one=lambda:hardened)
        def reference(connection):
            observed=original(connection)
            observed['catalog']={**expected['catalog'],**observed['catalog']}
            return observed
        monkeypatch.setattr(access,'reference_document',reference)
        try:access.verify_discovery_catalog(MetadataConnection())
        finally:assert snapshot==untouched  # Raw observations remain truthful.
    return verify


def test_identity28_permission_reduction_matches_unchanged_access19_reference(discovery_verifier):
    discovery_verifier(DISCOVERY_FUNCTIONS,True)


def test_restricted_access_migrator_observes_marker_without_identity_schema_usage(discovery_verifier):
    discovery_verifier(DISCOVERY_FUNCTIONS,True,deny_identity_usage=True)


def test_previous_identity_variant_retains_exact_published_comparison(discovery_verifier):
    discovery_verifier(sorted(DISCOVERY_FUNCTIONS+LEGACY_HELPERS),False)


@pytest.mark.parametrize('helpers',[LEGACY_HELPERS[:1],LEGACY_HELPERS])
def test_identity28_rejects_one_or_all_restored_helper_permissions(discovery_verifier,helpers):
    import access_baseline as baseline
    with pytest.raises(baseline.BaselineError,match='^discovery_owner_privileges_unsafe$'):
        discovery_verifier(sorted(DISCOVERY_FUNCTIONS+helpers),True)


@pytest.mark.parametrize('hardened',[False,True])
@pytest.mark.parametrize('change',['missing_required','extra_routine','wrong_overload','foreign_actor_reader'])
def test_compatibility_keeps_unrelated_function_drift_rejected(discovery_verifier,hardened,change):
    import copy
    import access_baseline as baseline
    functions=copy.deepcopy(DISCOVERY_FUNCTIONS)
    if change=='missing_required':functions.remove(['identity','current_account_memberships',''])
    if change=='extra_routine':functions.append(['identity','unrelated_helper',''])
    if change=='wrong_overload':functions.append(['identity','log_audit','value text'])
    if change=='foreign_actor_reader':functions.append(['identity','actor_displays','selected uuid[]'])
    if not hardened:functions+=LEGACY_HELPERS
    with pytest.raises(baseline.BaselineError,match='^access_catalog_mismatch$'):
        discovery_verifier(sorted(functions),hardened)


def test_missing_legacy_permissions_without_exact_projection_remains_a_mismatch(discovery_verifier):
    import access_baseline as baseline
    with pytest.raises(baseline.BaselineError,match='^access_catalog_mismatch$'):
        discovery_verifier(DISCOVERY_FUNCTIONS,False)


def test_compatible_comparison_preserves_immutable_reference_and_migration(discovery_verifier):
    from hashlib import sha256
    import json
    paths=[access.HERE/'discovery-reference.json',access.HERE/'versions/0019_discovery.py']
    before={path:path.read_bytes() for path in paths}
    assert sha256(before[paths[0]]).hexdigest()==access.REFERENCE_SHA256
    from access_account_grant_catalog import fingerprints
    historical=fingerprints({'discovery_functions':sorted(DISCOVERY_FUNCTIONS+LEGACY_HELPERS)})
    assert historical['discovery_functions']==json.loads(before[paths[0]])['catalog']['discovery_functions']
    discovery_verifier(DISCOVERY_FUNCTIONS,True)
    assert before=={path:path.read_bytes() for path in paths}

@pytest.mark.parametrize('module,owner',[(identity,'identity'),(access,'access')])
def test_new_head_preserves_inherited_studies_role_guards(monkeypatch,module,owner):
    def unsafe(connection,selected):
        assert selected==owner
        raise RuntimeError('studies_role_membership_unsafe')
    monkeypatch.setattr(studies,'verify_roles',unsafe)
    with pytest.raises(RuntimeError,match='studies_role_membership_unsafe'):module.verify_discovery_catalog(object())

@pytest.mark.parametrize('installed,edge,accepted',[
    (False,None,True),
    (False,('access_discovery_owner','USAGE',False),False),
    (True,('access_discovery_owner','USAGE',False),True),
    (True,None,False),
    (True,('access_discovery_owner','CREATE',False),False),
    (True,('access_discovery_owner','USAGE',True),False),
    (True,('unrelated_reader','USAGE',False),False),
])
def test_prerequisite_schema_acl_allows_only_installed_discovery_usage(monkeypatch,installed,edge,accepted):
    from types import SimpleNamespace
    import access_baseline as baseline
    owner='access_migrator'
    def rows(connection,sql):
        if sql=='SELECT session_user,current_user':return [(owner,owner)]
        if sql.startswith('SELECT rolname,rolcanlogin') and "FROM pg_roles WHERE rolname IN ('access_migrator','access_runtime')" in sql:
            return [(role,True,False,False,False,False,False) for role in (owner,'access_runtime')]
        if 'SELECT pg_get_userbyid(nspowner)' in sql:return [(owner,)]
        if "p.proname='discover_applications'" in sql:return [(1,)] if installed else []
        return []
    monkeypatch.setattr(baseline,'rows',rows)
    monkeypatch.setattr(baseline,'operator_installed',lambda _:False)
    monkeypatch.setattr(baseline,'organization_check_installed',lambda _:False)
    acl=baseline.owner_acl(['USAGE','CREATE'])+[(owner,'access_runtime','USAGE',False)]
    if edge:acl.append((owner,*edge))
    monkeypatch.setattr(baseline,'acl',lambda *_:acl)
    connection=SimpleNamespace(execute=lambda _:SimpleNamespace(scalar_one=lambda:False))
    if accepted:baseline.verify_prerequisites(connection)
    else:
        with pytest.raises(baseline.BaselineError,match='access_catalog_mismatch'):baseline.verify_prerequisites(connection)

def test_cross_owner_metadata_verifier_does_not_read_configuration_rows(monkeypatch):
    import json
    import access_baseline as baseline
    import access_capability_catalog as capability
    import access_account_grant_catalog as account
    import access_organization_check_catalog as organization
    monkeypatch.setattr(studies,'verify_roles',lambda *_:None)
    monkeypatch.setattr(baseline,'verify_operator_roles',lambda *_:None)
    monkeypatch.setattr(organization,'verify_reader_role',lambda *_,**__:None)
    monkeypatch.setattr(capability,'verify_reader_role',lambda *_,**__:None)
    monkeypatch.setattr(account,'verify_runtime_role',lambda *_:None)
    monkeypatch.setattr(access,'verify_role',lambda *_:None)
    expected=json.loads((access.HERE/'discovery-reference.json').read_bytes())
    monkeypatch.setattr(access,'reference_document',lambda _:expected)
    class MetadataConnection:
        def execute(self,sql):pytest.fail('metadata verifier read protected configuration: '+str(sql))
    access.verify_discovery_catalog(MetadataConnection())

@pytest.mark.parametrize('phase',['preflight','verify_postcondition'])
@pytest.mark.parametrize('count',[128,129])
def test_access_owner_release_phases_enforce_catalogue_bound_after_prerequisites(monkeypatch,phase,count):
    from types import SimpleNamespace
    import access_baseline as baseline
    observed=[]
    monkeypatch.setattr(baseline,'verify_encoding',lambda _:None)
    monkeypatch.setattr(baseline,'verify_prerequisites',lambda _:observed.append('owner_verified'))
    monkeypatch.setattr(baseline,'verify_table',lambda *_:None)
    monkeypatch.setattr(baseline,'verify_catalog',lambda *_:observed.append('metadata_verified'))
    monkeypatch.setattr(baseline,'rows',lambda *_:[('access_0019',)])
    class OwnerConnection:
        def execute(self,sql):
            if str(sql)=='SELECT count(*) FROM access.applications':
                assert observed==['owner_verified','metadata_verified']
                observed.append('configuration_checked')
                return SimpleNamespace(scalar_one=lambda:count)
            return SimpleNamespace(scalar_one=lambda:True)
    verify=getattr(baseline,phase)
    if count<=128:verify(OwnerConnection())
    else:
        with pytest.raises(baseline.BaselineError,match='discovery_catalogue_oversized'):verify(OwnerConnection())
    assert observed==['owner_verified','metadata_verified','configuration_checked']
