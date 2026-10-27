"""Fixture boundaries and authority-restoration control flow, no native DB proof."""
from pathlib import Path
import sys
import json
from uuid import uuid4
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_identity_transition as q


def fixture():
    accounts=[dict(account_id=str(uuid4()),person_id=str(uuid4()),membership_id=str(i+1)) for i in range(3)]
    for account in accounts:account['actor_id']=account['account_id']
    value=dict(run_id=q.APPROVED_RUN,port=q.APPROVED_PORT,database='idb_88a737ddad7b_transition',org_ids=[str(uuid4()),str(uuid4())],retained_accounts=accounts,
        replacement=dict(account_id=str(uuid4()),actor_id=str(uuid4()),person_id=accounts[2]['person_id']),receipt_authority_id=str(uuid4()))
    for key,login in [('owner_url','identity_migrator'),('operator_url','identity_operator'),('runtime_url','access_runtime'),('legacy_probe_url','identity_legacy_probe_runtime')]:
        value[key]=f'postgresql://{login}:synthetic@127.0.0.1:55582/idb_88a737ddad7b_transition'
    return value


@pytest.mark.parametrize('defect',[None,'extra','actor','replacement','run','port','login','member','person'])
def test_transition_fixture_is_closed_and_fixed_to_approved_leave(tmp_path,defect):
    value=fixture();run=q.APPROVED_RUN;port=q.APPROVED_PORT
    if defect=='extra':value['discover']=True
    elif defect=='actor':value['retained_accounts'][0]['actor_id']=str(uuid4())
    elif defect=='replacement':value['replacement']['person_id']=str(uuid4())
    elif defect=='run':run=value['run_id']=str(uuid4())
    elif defect=='port':port=value['port']=55482
    elif defect=='login':value['legacy_probe_url']=value['legacy_probe_url'].replace('identity_legacy_probe_runtime','postgres')
    elif defect=='member':value['retained_accounts'][0]['membership_id']='01'
    elif defect=='person':value['retained_accounts'][1]['person_id']=value['retained_accounts'][0]['person_id']
    path=tmp_path/'private.json';path.write_text(json.dumps(value));path.chmod(0o600)
    if defect:
        with pytest.raises(ValueError):q.load_fixture(path,run,port)
    else:assert q.load_fixture(path,run,port)==value


def test_authority_restore_occurs_when_denial_assertion_fails(monkeypatch):
    value=fixture();runner=q.Transition(value);seen=[]
    account=value['retained_accounts'][0]['account_id'];link=runner.value(value['retained_accounts'][0]['person_id'],dict(account_id=account,actor_id=account))
    def sql(statement,params=None,key='owner_url'):
        seen.append(statement)
        if statement.startswith('SELECT'):return [('identity_operator','account.link_person','platform',None,account,True)]
    def denied(*args,**kwargs):raise AssertionError('synthetic unexpected lookup success')
    monkeypatch.setattr(runner,'state',lambda:{'same':1})
    monkeypatch.setattr(runner,'sql',sql);monkeypatch.setattr(runner,'denied',denied)
    with pytest.raises(AssertionError,match='unexpected lookup success'):runner.revoke_receipt(link)
    assert 'enabled=false' in seen[1] and 'enabled=true' in seen[2]
