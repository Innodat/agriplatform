"""Discovery native proof refuses incomplete or unsafe fixture/result oracles."""
import json
from pathlib import Path
import sys
import pytest
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_discovery as proof

ORG='33333333-3333-4333-8333-333333333333'

def case(apps=False):
    return {'request':{'path':'/v2/applications' if apps else '/v2/organizations','caller':'directory' if apps else 'leave','token':'user','query':'' if apps else 'application=leave'},'expected':{'status':200,'fields':{'applications':[{'app_id':'pts','eligible_scope_kinds':['account']}]} if apps else {'organizations':[{'org_id':ORG,'name':'For Profit Limited','membership_id':'9223372036854775807'}],'next_cursor':None}}}

def fixture():return {'service_keys':{'directory':'synthetic-directory','leave':'synthetic-leave'},'tokens':{'user':'synthetic-token'}}

@pytest.mark.parametrize('apps',[True,False])
def test_success_requires_complete_independent_oracle(apps):
    item=case(apps);proof.validate_http_case(item,fixture())
    for key in list(item['expected']['fields']):
        altered=json.loads(json.dumps(item));del altered['expected']['fields'][key]
        with pytest.raises(ValueError,match='fixture_binding_oracle_required'):proof.validate_http_case(altered,fixture())

@pytest.mark.parametrize('alteration',['name','member','extra','order','scope','time','details'])
def test_response_rejects_foreign_or_malformed_results(alteration):
    apps=alteration in ('scope','time','details');item=case(apps);actual=json.loads(json.dumps(item['expected']['fields']))
    if apps:actual['checked_at']='2026-10-27T12:00:00Z'
    if alteration=='name':actual['organizations'][0]['name']='another organization'
    elif alteration=='member':actual['organizations'][0]['membership_id']=1
    elif alteration=='extra':actual['organizations'][0]['account_id']=ORG
    elif alteration=='order':actual['organizations']*=2
    elif alteration=='scope':actual['applications'][0]['eligible_scope_kinds']=['organization','account']
    elif alteration=='time':actual['checked_at']='2026-02-30T12:00:00Z'
    else:actual['applications'][0]['org_id']=ORG
    with pytest.raises(ValueError):proof.validate_response(httpx.Response(200,json=actual,headers={'cache-control':'private, no-store'}),item)

def test_error_requires_explicit_identifier_and_closed_safe_envelope():
    item=case();item['expected']={'status':403}
    with pytest.raises(ValueError,match='fixture_error_oracle_required'):proof.validate_http_case(item,fixture())
    item['expected']['error_id']='access_denied'
    for value in ({'error_id':'service_access_denied','error':'safe','details':{}},{'error_id':'access_denied','error':'safe','details':{'account_id':ORG}}):
        with pytest.raises(ValueError):proof.validate_response(httpx.Response(403,json=value,headers={'cache-control':'private, no-store'}),item)

@pytest.mark.parametrize('path',['http://foreign.invalid','//foreign.invalid','/v2/check','/v2/organizations?application=leave'])
def test_only_closed_owner_paths_can_receive_credentials(path):
    item=case();item['request']['path']=path
    with pytest.raises(ValueError,match='fixture_http_invalid'):proof.validate_http_case(item,fixture())

def test_reserves_evidence_and_journal_before_native_guard(tmp_path,monkeypatch):
    source=tmp_path/'fixture.json';source.write_text('{}');source.chmod(0o600)
    output=tmp_path/'proof.json';calls=[]
    def refuse():
        calls.append(True)
        assert json.loads(output.read_text())=={'status':'incomplete'}
        assert output.with_suffix('.journal.jsonl').exists()
        raise ValueError('guard_refused')
    monkeypatch.setattr(proof,'guard',refuse)
    monkeypatch.setattr(sys,'argv',['qualify','--fixture',str(source),'--output',str(output)])
    with pytest.raises(ValueError,match='guard_refused'):proof.main()
    with pytest.raises(FileExistsError):proof.main()
    assert calls==[True]

def test_complete_source_custody_includes_discovery_runtime_and_histories():
    manifest=proof.source_manifest()
    for name in ('discovery.py','discovery_query.py','discovery_contract.py','migrations/versions/0019_discovery.py','identity-migrations/versions/0026_discovery.py'):
        assert 'services/access/'+name in manifest

def test_empty_token_omits_authorization_and_validates_actual_api_401(monkeypatch):
    from fastapi.testclient import TestClient
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    from main import create_app
    monkeypatch.setenv('DIRECTORY_SERVICE_KEY','synthetic-directory')
    provider=[];seen=[];responses=[]
    async def verify(*args):provider.append(True);raise AssertionError('missing_bearer_reached_provider')
    app=create_app(capability_db=object(),capability_provider=verify)
    @app.middleware('http')
    async def capture(request,call_next):
        seen.append(dict(request.headers));response=await call_next(request)
        responses.append(response.status_code);return response
    client=TestClient(app)
    monkeypatch.setattr(proof.httpx,'Client',lambda **_:client)
    item={'name':'missing-bearer','request':{'caller':'directory','token':'missing','path':'/v2/applications'},
        'expected':{'status':401,'error_id':'authentication_required'}}
    proof.Qualification({'api_url':'http://testserver','service_keys':{'directory':'synthetic-directory'},'tokens':{'missing':''}},None).request(item)
    assert len(seen)==1 and 'authorization' not in seen[0]
    assert responses==[401] and not provider
