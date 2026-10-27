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
