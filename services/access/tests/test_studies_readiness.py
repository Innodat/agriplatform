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
