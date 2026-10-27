"""Later heads retain inherited role membership and historical source guards."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'identity-migrations'))
import identity_baseline as baseline
import identity_person_catalog as person
import identity_preferences_catalog as preferences
import identity_studies_catalog as studies
import studies_migration_support as support

@pytest.mark.parametrize('module,verify',[(person,person.verify_person_catalog),(preferences,preferences.verify_preferences_catalog)])
def test_later_head_refuses_unsafe_inherited_studies_membership(monkeypatch,module,verify):
    def unsafe(connection,owner):
        assert owner=='identity'
        raise RuntimeError('studies_role_membership_unsafe')
    monkeypatch.setattr(support,'verify_roles',unsafe)
    monkeypatch.setattr(baseline,'trusted_check_reader_bridge_reference',lambda:None)
    with pytest.raises(RuntimeError,match='studies_role_membership_unsafe'):verify(object())

def test_person_head_refuses_changed_revision21_source(tmp_path,monkeypatch):
    (tmp_path/'versions').mkdir();(tmp_path/'versions/0021_studies_account_setup.py').write_bytes(b'changed historical source')
    previous=json.dumps(dict(migration_sha256=sha256(b'approved historical source').hexdigest())).encode()
    (tmp_path/'studies-setup-reference.json').write_bytes(previous)
    reference=dict(migration_sha256='approved22',predecessor_reference_sha256=sha256(previous).hexdigest(),catalog={})
    raw=json.dumps(reference).encode();(tmp_path/'person-links-reference.json').write_bytes(raw)
    monkeypatch.setattr(person,'HERE',tmp_path);monkeypatch.setattr(person,'REFERENCE_SHA256',sha256(raw).hexdigest())
    monkeypatch.setattr(studies,'REFERENCE_SHA256',sha256(previous).hexdigest())
    monkeypatch.setattr(person,'reference_document',lambda _:reference)
    monkeypatch.setattr(baseline,'trusted_check_reader_bridge_reference',lambda:None)
    monkeypatch.setattr(baseline,'compare_catalog',lambda *args:None)
    monkeypatch.setattr(support,'verify_roles',lambda *args:None)
    with pytest.raises(baseline.BaselineError,match='identity_person_reference_unavailable'):person.verify_person_catalog(object())
