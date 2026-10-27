"""Source and required-case evidence is checked before owner preparation."""
import copy
import json
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import studies_readiness as readiness

def test_all_authoritative_sources_are_validated(monkeypatch,tmp_path):
    sources=readiness.source_hashes()
    assert 'platform/deployment/tests/test_host.py' in sources
    for name in ('services/access/migrations/access_baseline.py','services/access/studies_identity.py','platform/deployment/host-release.py'):
        stale=dict(sources);stale[name]='0'*64
        with pytest.raises(ValueError,match='studies_qualification_missing_or_stale'):readiness.validate_sources(stale)
    for name in ('../outside','/tmp/outside','services/access/../../outside'):
        with pytest.raises(ValueError,match='studies_qualification_missing_or_stale'):readiness.validate_sources({name:'0'*64})
    with pytest.raises(ValueError):readiness.validate_sources({})

def stage_proofs():
    sources={'synthetic':'test-only'}
    proofs={name:{**{field:True for field in fields},'executed_sources':sources} for name,fields in readiness.STAGE_FIELDS.items()}
    proofs['current-first-use-race.json']['initial_statuses']=[200]*4
    proofs['boundaries.json'].update(actual_sql_timeout_seconds=.1,restricted_role_denials=[[role,action] for role in readiness.DATABASE_ROLES.values() for action in ('SELECT','SELECT','SELECT','SET','SET')])
    proofs['current-denials.json']['write_lock_timeout_seconds']=.2
    proofs['confirmed-http-denials.json']['results']=[{'status':403,'error_id':error,'path':path} for error in ('identity.verification_required','access_denied') for path in ('/v2/check','/v2/enrollments/scribeswell-studies')]
    proofs['current-cli-proof.json'].update(activation_executed=False,results=[{'stage':stage,'exit_code':code} for stage,code in [('cli-access-before-identity',1),('cli-identity-failure',1),('cli-identity-upgrade',0),('cli-identity-repeat',0),('cli-access-failure',1),('cli-access-upgrade',0),('cli-access-repeat',0)]])
    proofs['current-clean-upgrade-proof.json']['ordered_owner_results']=[{'owner':'identity','exit_code':0},{'owner':'access','exit_code':0}]
    return proofs,sources

def test_required_native_fields_and_execution_sources_are_not_inferred():
    proofs,sources=stage_proofs()
    assert readiness.validate_stage_proofs(proofs,sources)['current_auth_after_lock'] is True
    for name,fields in readiness.STAGE_FIELDS.items():
        for field in fields:
            missing=copy.deepcopy(proofs);missing[name].pop(field)
            with pytest.raises(ValueError):readiness.validate_stage_proofs(missing,sources)
        stale=copy.deepcopy(proofs);stale[name]['executed_sources']={}
        with pytest.raises(ValueError):readiness.validate_stage_proofs(stale,sources)
    missing=copy.deepcopy(proofs);missing.pop('boundaries.json')
    with pytest.raises(ValueError):readiness.validate_stage_proofs(missing,sources)
    for name,field,value in [('current-first-use-race.json','initial_statuses',[200,503,200,200]),('boundaries.json','restricted_role_denials',[]),('confirmed-http-denials.json','results',[]),('current-cli-proof.json','results',[]),('current-clean-upgrade-proof.json','ordered_owner_results',[])]:
        missing=copy.deepcopy(proofs);missing[name][field]=value
        with pytest.raises(ValueError):readiness.validate_stage_proofs(missing,sources)


def current_artifact():
    return {'schema_version':2,'release_id':'synthetic-current-owners',
        'identity_revision':'identity_0026','access_revision':'access_0019',
        'service_actor_id':'11111111-1111-4111-8111-111111111111',
        'runtime_sources':readiness.runtime_hashes(),'qualification_sha256':'a'*64,
        'profile_hook_qualified':True,'live_provider_qualified':True}


def test_current_exact_owner_pair_is_the_closed_artifact_contract():
    artifact=current_artifact()
    assert readiness.validate_artifact(json.dumps(artifact))==artifact
    for patch in ({'schema_version':1},{'identity_revision':'identity_0021','access_revision':'access_0016'},
            {'identity_revision':'identity_0025','access_revision':'access_0018'},
            {'identity_revision':'identity_0027'},{'access_revision':'access_0020'},
            {'runtime_sources':{}},{'qualification_sha256':'not-a-hash'},
            {'profile_hook_qualified':False},{'live_provider_qualified':False},
            {'service_actor_id':'00000000-0000-0000-0000-000000000000'}):
        with pytest.raises(ValueError,match='studies_readiness_missing_or_stale'):
            readiness.validate_artifact(json.dumps(artifact|patch))


def test_artifact_refuses_malformed_partial_duplicate_and_extra_fields():
    artifact=current_artifact()
    samples=['not-json','[]','null',json.dumps(artifact|{'unexpected':True}),
        json.dumps(artifact)[:-1]+',"schema_version":2}']
    samples.extend(json.dumps({key:value for key,value in artifact.items() if key!=field}) for field in artifact)
    for raw in samples:
        with pytest.raises(ValueError,match='studies_readiness_missing_or_stale'):
            readiness.validate_artifact(raw)


def test_current_transitive_owner_and_qualification_sources_are_bound():
    sources=readiness.source_hashes()
    for name in ('services/access/identity-migrations/versions/0026_discovery.py',
            'services/access/identity-migrations/discovery-reference.json',
            'services/access/migrations/versions/0019_discovery.py',
            'services/access/migrations/discovery-reference.json',
            'services/access/identity-migrations/source-pins.json',
            'services/access/tests/qualify_studies_current.py',
            'apps/scribeswell/tests/studies_owner_fixture.py'):
        assert name in sources
        stale=dict(sources);stale[name]='0'*64
        with pytest.raises(ValueError,match='studies_qualification_missing_or_stale'):readiness.validate_sources(stale)
    for name in ('discovery.py','capability_check.py','identity_preferences.py'):
        assert name in readiness.runtime_hashes()


def test_qualification_refuses_old_pair_changed_stage_and_runtime(monkeypatch,tmp_path):
    from hashlib import sha256
    proofs,sources=stage_proofs()
    monkeypatch.setattr(readiness,'source_hashes',lambda:sources)
    monkeypatch.setattr(readiness,'validate_sources',lambda recorded:None if recorded==sources else (_ for _ in ()).throw(ValueError('stale')))
    record={'schema_version':2,'identity_revision':'identity_0026','access_revision':'access_0019',
        'sources':sources,'runtime_sources':readiness.runtime_hashes(),
        'cases':readiness.validate_stage_proofs(proofs,sources),'proof_sha256':{}}
    for name,value in proofs.items():
        raw=json.dumps(value).encode();(tmp_path/name).write_bytes(raw)
        record['proof_sha256'][name]=sha256(raw).hexdigest()
    readiness.validate_qualification(record,tmp_path)
    for change in ({'schema_version':1},{'identity_revision':'identity_0025'},
            {'access_revision':'access_0018'},{'runtime_sources':{}},{'proof_sha256':{}},{'cases':{}}):
        with pytest.raises(ValueError):readiness.validate_qualification(record|change,tmp_path)
    name=next(iter(proofs));(tmp_path/name).write_text('{}')
    with pytest.raises(ValueError,match='studies_qualification_proof_changed'):readiness.validate_qualification(record,tmp_path)
