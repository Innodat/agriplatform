"""D1 acceptance: versioned discovery, explicit start and current reads."""
import asyncio,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx,pytest
from test_draft_context import Access,People,Config,ORG,NOW
from main import create_app

class Store:
    def __init__(self):self.calls=[]
    async def snapshot(self,prepared,budget):
        self.calls.append('snapshot');return {'scope_generation':'0','active_draft':None}

def call(path,store=None,**kwargs):
    async def run():
        app=create_app(repository=object(),access=Access(),environment={},people=People(),configuration=Config(),clock=lambda:NOW,drafts=store or Store())
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://leave') as client:return await client.request(kwargs.pop('method','GET'),path,headers={'Authorization':'Bearer synthetic'},**kwargs)
    return asyncio.run(run())

def test_extended_context_is_explicit_and_read_never_starts():
    store=Store();r=call(f'/v1/organizations/{ORG}/me/draft-context?draft_context_version=1',store)
    assert r.status_code==200 and r.json()['scope_generation']=='0' and r.json()['active_draft'] is None
    assert store.calls==['snapshot']

@pytest.mark.parametrize('query',['draft_context_version=2','draft_context_version=1&draft_context_version=1','x=1'])
def test_context_rejects_unknown_repeated_version(query):assert call(f'/v1/organizations/{ORG}/me/draft-context?{query}').status_code==422

def test_start_requires_closed_canonical_counter_and_v4_operation():
    from uuid import uuid4
    for body in ({'operation_id':str(uuid4()),'expected_scope_generation':'00'},{'operation_id':str(uuid4()),'expected_scope_generation':'0','input':{}},{'operation_id':str(uuid4()),'expected_scope_generation':'9223372036854775808'}):
        assert call(f'/v1/organizations/{ORG}/me/draft/start',method='POST',json=body).status_code==422

def test_empty_shape_and_fingerprint_are_stable_and_sensitive_to_raw_text():
    from drafts import empty_input,command_fingerprint
    from uuid import uuid4
    actor,employment,operation=[str(uuid4()) for _ in range(3)]
    args=(ORG,actor,employment,operation,'0')
    assert empty_input()['duration_mode'] is None and empty_input()['leave_type_id'] is None
    first=command_fingerprint(*args)
    assert len(first)==32 and first==command_fingerprint(*args)
    assert first!=command_fingerprint(ORG,actor,employment,operation,'1')


def test_draft_input_preserves_partial_raw_text_and_rejects_structural_loss():
    from drafts import Input,empty_input
    import copy
    original=empty_input();original['full_days']['start']['text']='24/09/';original['hours']['duration']['text']='1.';original['note']='😀'*4000
    assert Input.model_validate(original).model_dump()==original
    for path,value in [('note','😀'*4001),('input_version',2),('leave_type_id','00000000-0000-0000-0000-000000000000')]:
        broken=copy.deepcopy(original);broken[path]=value
        with pytest.raises(ValueError):Input.model_validate(broken)
    for broken in ({k:v for k,v in original.items() if k!='hours'},{**original,'extra':1},{**original,'note':'a\0b'}):
        with pytest.raises(ValueError):Input.model_validate(broken)

def test_preparation_retains_actual_tagged_evidence_without_public_authority_token():
    from draft_context import prepare
    from drafts import evidence
    from transaction_context import Budget
    async def run():
        config=Config();config.zone=None;config.notice='work_timezone_missing'
        prepared=await prepare(Access(),People(),config,'Bearer synthetic',ORG,Budget(),lambda:NOW,retain=True)
        observed=evidence(prepared)
        assert observed['kind']=='discovery' and observed['has_periods'] is True
        assert 'as_of_date' not in observed and 'timezone' not in observed and 'observation' not in prepared.public.model_dump()
        config=Config();prepared=await prepare(Access(),People(),config,'Bearer synthetic',ORG,Budget(),lambda:NOW,retain=True)
        observed=evidence(prepared);assert observed['kind']=='effective' and observed['as_of_date']=='2026-11-08' and observed['decision_id']==prepared.authority.decision.decision_id
    asyncio.run(run())

def test_start_save_discard_and_outcome_routes_do_not_add_submission():
    paths=create_app(environment={}).openapi()['paths']
    assert '/v1/organizations/{org_id}/me/draft/start' in paths
    assert '/v1/organizations/{org_id}/operations/{operation_id}' in paths
    assert '/v1/organizations/{org_id}/drafts/{draft_id}/input' in paths
    assert '/v1/organizations/{org_id}/drafts/{draft_id}/discard' in paths
    assert not any('/submit' in p for p in paths)
    query=paths['/v1/organizations/{org_id}/me/draft-context']['get']['parameters']
    assert any(p['name']=='draft_context_version' for p in query)
