"""Protected mutable application receipts and dispatch."""
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_application_enable_input import document
from test_application_register import OP

def test_enablement_dispatch_and_lookup(monkeypatch):
    import access_operator as a
    seen=[]
    monkeypatch.setattr(a,'_run',lambda *args:seen.append(args))
    a.execute(object(),json.dumps(document()).encode())
    assert 'access.set_application_enabled' in seen[-1][2]
    assert seen[-1][3]['enabled'] is True and seen[-1][3]['revision']=='1'
    assert seen[-1][-1]=='application.set_enabled'
    a.outcome(object(),OP,command='application.set_enabled',app_id='fixture_app')
    assert 'access.application_enablement_outcome' in seen[-1][2]
    for kwargs in ({'permission':'p'},{'app_id':None}):
        with pytest.raises(a.OperatorError):a.outcome(object(),OP,command='application.set_enabled',**({'app_id':'fixture_app'}|kwargs))

def test_enablement_receipt_closed_mutable_contract():
    import access_operator as a
    base={'target':{'app_id':'fixture_app'},'disposition':'changed','revision':'2','event_id':OP}
    tail=(1,1,datetime.now(timezone.utc))
    result=a._receipt((base,*tail),OP,'application.set_enabled').result
    assert type(result) is a.SetApplicationEnabledResult and result.revision=='2'
    assert a._receipt(({**base,'disposition':'unchanged','revision':'9223372036854775807','event_id':None},*tail),OP,'application.set_enabled')
    for changes in ({'disposition':'created'},{'event_id':None},{'revision':2},{'revision':'1'},{'revision':'9223372036854775808'},{'target':{'app_id':'fixture_app','enabled':True}}):
        with pytest.raises(a.OperatorError):a._receipt(({**base,**changes},*tail),OP,'application.set_enabled')

def test_exact_history_and_catalog_seven():
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations'))
    import access_baseline as b
    from access_registration_catalog import enablement_catalog,entry_catalog
    assert b.HEAD=='access_0007'
    for i in range(1,8):assert b.validate_revision([f'access_000{i}'])==f'access_000{i}'
    assert 'application.set_enabled' not in repr(entry_catalog())
    assert 'application.set_enabled' in repr(enablement_catalog())


def test_enablement_source_pin_refuses_drift_before_import(monkeypatch):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations'))
    import access_registration_baseline as b
    original=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:original(path)+b'\n# drift\n' if path.name=='0007_application_set_enabled.py' else original(path))
    with pytest.raises(b.BaselineError,match='access_original_source_mismatch'):b._sql('access_0007')
    assert 'register_entry_permission' in b._sql('access_0006')



def test_identity_metadata_dependency_exclusion_is_exact():
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'identity-migrations/identity_baseline.py'
    spec=importlib.util.spec_from_file_location('_enablement_identity_catalog',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    def row(description):return ['db','pg_class','a',description]
    allowed=row('column enabled of table access.applications')
    unexpected=[row('column revision of table access.applications'),row('column enabled of table other.applications'),row('column enabled of table access.other')]
    assert module._identity_target_dependencies([allowed,*unexpected])==unexpected
