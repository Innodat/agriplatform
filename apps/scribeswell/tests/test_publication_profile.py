"""Pure version selection and historical catalogue preservation."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'migrations'))
from release_profile import selection, valid_result, evidence


def test_publication_profile_selects_forward_revision_without_changing_old_profiles():
    expected = selection(dict(profile='publication-v1',custody=None))
    assert valid_result(dict(before='scribeswell_0003',after='scribeswell_0004',validation=evidence(expected)),expected)
    assert valid_result(dict(before='scribeswell_0004',after='scribeswell_0004',validation=evidence(expected)),expected)
    assert not valid_result(dict(before=None,after='scribeswell_0004',validation=evidence(expected)),expected)
    old = selection(dict(profile='dormant',custody=None))
    assert valid_result(dict(before=None,after='scribeswell_0003',validation=evidence(old)),old)
    assert not valid_result(dict(before='scribeswell_0003',after='scribeswell_0004',validation=evidence(old)),old)

import copy
import json
import pytest
import publication_profile as profile
from baseline import APP, PROFILES, SUPPORTED_REVISIONS


def test_new_revision_is_recognized_independently_of_historical_reference_snapshots():
    assert 'scribeswell_0004' in SUPPORTED_REVISIONS
    assert 'scribeswell_0004' not in PROFILES
    assert set(PROFILES)=={'scribeswell_0001','scribeswell_0002','scribeswell_0003'}


def test_pinned_controller_additions_are_allowed_but_previous_definitions_are_preserved(monkeypatch):
    pinned=json.loads((APP/'migrations/reference-controller.json').read_text())
    actual=copy.deepcopy(pinned)
    actual['functions'].append(['new_routine','', 'new definition','scribeswell_migrator',True,None,None,'v','u',False,False,'f','plpgsql'])
    actual['relations'].append(['new_table','r','p','scribeswell_migrator',False,False,None,None,'d',False,False])
    monkeypatch.setattr(profile,'acl',lambda db,value: [] if value is None else [value])
    profile.preserve_controller(None,actual,pinned,prepared=False)
    actual['functions'][0][2]='changed historical function definition'
    with pytest.raises(profile.BaselineError):profile.preserve_controller(None,actual,pinned,prepared=False)


@pytest.mark.parametrize('kind',['missing','acl','extra_overload','duplicate'])
def test_pinned_identity_and_normalized_acl_cannot_be_replaced(monkeypatch,kind):
    pinned=json.loads((APP/'migrations/reference-controller.json').read_text());actual=copy.deepcopy(pinned)
    monkeypatch.setattr(profile,'acl',lambda db,value: [] if value is None else [value])
    if kind=='missing':actual['functions'].pop()
    elif kind=='acl':actual['functions'][0][6]='{unsafe_grant}'
    elif kind=='duplicate':actual['functions'].append(copy.deepcopy(actual['functions'][0]))
    else:
        # A new overload may coexist, but may never stand in for a missing pinned signature.
        actual['functions'][0][1]='new_argument text'
    with pytest.raises(profile.BaselineError):profile.preserve_controller(None,actual,pinned,prepared=False)


def test_publication_profile_accepts_explicit_custody_and_environment():
    from release_profile import from_environ
    custody=dict(schema_version=1,source_id='tanakh',executor_actor_id='22222222-2222-4222-8222-222222222222',
                 actor_kind='service',actor_key='fixture.controller',preparation_evidence_ref='fixture:identity')
    assert from_environ({'SCRIBESWELL_MIGRATION_PROFILE':'publication-v1'})==dict(profile='publication-v1',custody=None)
    expected=selection(dict(profile='publication-v1',custody=custody))
    assert from_environ({'SCRIBESWELL_MIGRATION_PROFILE':'publication-v1','SCRIBESWELL_MIGRATION_CUSTODY_JSON':json.dumps(custody)})==expected
    assert valid_result(dict(before='scribeswell_0004',after='scribeswell_0004',validation=evidence(expected)),expected)


@pytest.mark.parametrize('selected,target,before,after',[
    ('dormant','scribeswell_0003',None,'scribeswell_0003'),
    ('publication-v1','head','scribeswell_0003','scribeswell_0004'),
    ('publication-v1','head','scribeswell_0004','scribeswell_0004')])
def test_worker_pins_historical_profiles_and_reports_new_profile(monkeypatch,capsys,selected,target,before,after):
    import io
    from alembic import command
    from test_owned_migrations import load_adapter
    request=dict(url='postgresql://scribeswell_migrator:fixture@127.0.0.1:1/postgres',
                 validation=dict(profile=selected,custody=None))
    def upgraded(config,revision):
        assert revision==target
        config.attributes.update(scribeswell_before=before,scribeswell_after=after,
                                 scribeswell_validated_profile=selected)
    monkeypatch.setattr(command,'upgrade',upgraded)
    monkeypatch.setattr(sys,'stdin',io.StringIO(json.dumps(request)))
    load_adapter().worker()
    assert json.loads(capsys.readouterr().out)==dict(before=before,after=after,validation=evidence(request['validation']))


def test_alembic_retains_previous_and_forward_paths_without_executing_sql():
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    script=ScriptDirectory.from_config(Config(str(APP/'alembic.ini')))
    assert script.get_current_head()=='scribeswell_0004'
    assert [step.revision.revision for step in script._upgrade_revs('scribeswell_0003','scribeswell_0002')]==['scribeswell_0003']
    assert [step.revision.revision for step in script._upgrade_revs('head','scribeswell_0003')]==['scribeswell_0004']
