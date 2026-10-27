"""ACCESS-B current typed decisions, disclosure ordering and caller isolation."""
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from uuid import UUID
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import create_app
ACCOUNT=UUID('11111111-1111-4111-8111-111111111111')
ACTOR=UUID('22222222-2222-4222-8222-222222222222')
ORG=UUID('33333333-3333-4333-8333-333333333333')
PERSON=UUID('44444444-4444-4444-8444-444444444444')
class Database:
    def __init__(self):
        self.calls=[];self.row=dict(account_id=ACCOUNT,actor_id=ACTOR,org_id=ORG,membership_id=19,person_id=PERSON)
    @asynccontextmanager
    async def begin(self):yield self
    async def execute(self,statement,parameters=None):self.calls.append((str(statement),parameters));return self
    def mappings(self):return self
    def one_or_none(self):return self.row
@pytest.fixture
def fixture(monkeypatch):
    for name in ('LEAVE','PTS','REFERENCE','PEOPLE'):monkeypatch.setenv(name+'_SERVICE_KEY','synthetic-'+name.lower())
    db=Database();calls=[]
    async def provider(token,deadline):calls.append(token);return ACCOUNT
    return TestClient(create_app(Database(),capability_db=db,capability_provider=provider)),db,calls

def post(fixture,permission='pts.poetry.read',scope=None,key='pts',path='/v2/check',body=None):
    return fixture[0].post(path,json=body or dict(permission=permission,authorization_scope=scope or {'kind':'account'}),headers={'Authorization':'Bearer synthetic','X-Service-Key':'synthetic-'+key})

def test_account_decision_without_membership_or_person(fixture):
    fixture[1].row=dict(account_id=ACCOUNT,actor_id=ACTOR)
    response=post(fixture)
    assert response.status_code==200,response.text
    assert set(response.json())=={'account_id','actor_id','permission','authorization_scope','decision_id','checked_at'}
    assert response.json()['authorization_scope']=={'kind':'account'}
    assert response.headers['cache-control']=='private, no-store'

@pytest.mark.parametrize('permission',['leave.request.own.read','leave.request.own.manage'])
def test_leave_exact_own_person_resource(fixture,permission):
    response=post(fixture,permission,{'kind':'organization','org_id':str(ORG)},'leave')
    assert response.status_code==200,response.text
    assert response.json()['person_id']==str(PERSON)
    assert response.json()['membership_id']=='19'
    assert response.json()['resource_scope']=={'kind':'own','person_id':str(PERSON)}
    assert any('SET TRANSACTION READ ONLY' in sql for sql,_ in fixture[1].calls)
    assert any('check_organization_capability' in sql for sql,_ in fixture[1].calls)

def test_reference_org_needs_no_person(fixture):
    fixture[1].row['person_id']=None
    response=post(fixture,'reference.record.read',{'kind':'organization','org_id':str(ORG)},'reference')
    assert response.status_code==200,response.text
    assert 'person_id' not in response.json()
    assert response.json()['resource_scope']=={'kind':'organization','org_id':str(ORG)}

def test_people_context_is_nullable_observation_not_app_decision(fixture):
    fixture[1].row['person_id']=None
    response=post(fixture,key='people',path='/v2/identity/organization-context',body={'org_id':str(ORG)})
    assert response.status_code==200,response.text
    assert response.json()['person_id'] is None and response.json()['org_id']==str(ORG)
    assert 'observation_id' in response.json() and 'decision_id' not in response.json()
    assert 'permission' not in response.json()

@pytest.mark.parametrize('caller,permission,scope,path,body',[
 ('leave','pts.poetry.read',None,'/v2/check',None),
 ('pts','leave.request.own.read',None,'/v2/check',None),
 ('reference','leave.request.own.read',None,'/v2/check',None),
 ('people','pts.poetry.read',None,'/v2/check',None),
 ('leave','',None,'/v2/identity/organization-context',{'org_id':str(ORG)}),
])
def test_service_policy_precedes_provider_and_sql(fixture,caller,permission,scope,path,body):
    response=post(fixture,permission,scope,caller,path,body)
    assert response.status_code==403 and response.json()['error_id']=='service_access_denied'
    assert not fixture[1].calls and not fixture[2]

@pytest.mark.parametrize('body',[
 {'permission':'pts.poetry.read','authorization_scope':{'kind':'account'},'account_id':str(ACCOUNT)},
 {'permission':'pts.poetry.read','authorization_scope':{'kind':'account','org_id':str(ORG)}},
 {'permission':'pts.poetry.read','authorization_scope':{'kind':'organization','org_id':str(ORG)}},
 {'permission':'pts.poetry.read','authorization_scope':{'kind':'organization','org_id':str(UUID(int=0))}},
 {'permission':'pts.poetry.read','authorization_scope':{'kind':'own','person_id':str(PERSON)}},
])
def test_bad_or_incompatible_scope_fails_without_fallback(fixture,body):
    response=post(fixture,body=body)
    assert response.status_code==422 and response.json()['error_id']=='validation_failed'
    assert not fixture[1].calls and not fixture[2]

@pytest.mark.parametrize('raw',[
 '{"permission":"pts.poetry.read","permission":"pts.poetry.read","authorization_scope":{"kind":"account"}}',
 '{"permission":"pts.poetry.read","authorization_scope":{"kind":"account","kind":"account"}}',
 'NaN','[',' '*65537,'['*1500+'0'+']'*1500,
])
def test_closed_json_decoder(fixture,raw):
    response=fixture[0].post('/v2/check',content=raw,headers={'Authorization':'Bearer synthetic','X-Service-Key':'synthetic-pts'})
    assert response.status_code==422 and response.json()['error_id']=='validation_failed'
    assert not fixture[1].calls and not fixture[2]

def test_authority_absence_precedes_setup_disclosure(fixture):
    fixture[1].row=None
    assert post(fixture).json()['error_id']=='access_denied'
    fixture[1].row=dict(account_id=ACCOUNT,actor_id=None)
    response=post(fixture)
    assert response.status_code==409 and response.json()['error_id']=='identity.actor_setup_required'
    fixture[1].row=dict(account_id=ACCOUNT,actor_id=ACTOR,org_id=ORG,membership_id=19,person_id=None)
    response=post(fixture,'leave.request.own.read',{'kind':'organization','org_id':str(ORG)},'leave')
    assert response.status_code==409 and response.json()['error_id']=='identity.person_link_required'

@pytest.mark.parametrize('column,value',[
 ('account_id',ACTOR),('actor_id',UUID(int=0)),('org_id',ACTOR),
 ('membership_id',True),('membership_id',0),('membership_id','19'),('membership_id',9223372036854775808),('person_id',UUID(int=0)),
])
def test_malformed_foreign_owner_row_never_authorizes(fixture,column,value):
    fixture[1].row[column]=value
    response=post(fixture,'leave.request.own.read',{'kind':'organization','org_id':str(ORG)},'leave')
    assert response.status_code==503 and response.json()['error_id']=='authorization_unavailable'


def test_repeated_requests_recheck_current_authority(fixture):
    assert post(fixture).status_code==200
    fixture[1].row=None
    assert post(fixture).status_code==403
    assert len(fixture[2])==2
    assert sum('check_account_capability' in sql for sql,_ in fixture[1].calls)==2

@pytest.mark.parametrize('field',['account_id','actor_id','person_id','permission','kind'])
def test_people_rejects_any_selector_except_org(fixture,field):
    response=post(fixture,key='people',path='/v2/identity/organization-context',body={'org_id':str(ORG),field:str(ACCOUNT)})
    assert response.status_code==422 and not fixture[2]


def test_duplicate_service_or_bearer_headers_deny_before_provider(fixture):
    for field in ('X-Service-Key','Authorization'):
        headers=[('X-Service-Key','synthetic-pts'),('Authorization','Bearer synthetic'),(field,'synthetic-pts' if field=='X-Service-Key' else 'Bearer synthetic')]
        response=fixture[0].post('/v2/check',json={'permission':'pts.poetry.read','authorization_scope':{'kind':'account'}},headers=headers)
        assert response.status_code==403 and not fixture[2]


def test_provider_failure_and_sql_exception_are_safe(monkeypatch,fixture,caplog):
    async def provider(token,deadline):raise RuntimeError('sensitive-provider-payload')
    client=TestClient(create_app(Database(),capability_db=Database(),capability_provider=provider))
    with caplog.at_level('WARNING',logger='access.capabilities'):
        response=client.post('/v2/check',json={'permission':'pts.poetry.read','authorization_scope':{'kind':'account'}},headers={'X-Service-Key':'synthetic-pts','Authorization':'Bearer sensitive'})
    assert response.status_code==503 and 'sensitive' not in response.text
    for record in caplog.records:
        assert record.exc_info is None and 'sensitive' not in repr(record.__dict__)

@pytest.mark.parametrize('other',['LEAVE_SERVICE_KEY','PTS_SERVICE_KEY','REFERENCE_SERVICE_KEY','KDG_SERVICE_KEY','SCRIBESWELL_SERVICE_KEY','CONTENT_SERVICE_KEY','DIRECTORY_SERVICE_KEY'])
def test_duplicate_credentials_fail_closed(monkeypatch,other):
    from caller_policy import CallerPolicy
    with pytest.raises(RuntimeError):CallerPolicy({'PEOPLE_SERVICE_KEY':'duplicate',other:'duplicate'})


def test_service_policy_uses_no_prefix_matches(fixture):
    response=post(fixture,'pts.poetry.read.extra')
    assert response.status_code==403 and not fixture[2]


def test_provider_precedes_read_only_transaction(fixture,monkeypatch):
    order=[]
    class Ordered(Database):
        @asynccontextmanager
        async def begin(self):order.append('transaction');yield self
    async def provider(token,deadline):order.append('provider');return ACCOUNT
    client=TestClient(create_app(Database(),capability_db=Ordered(),capability_provider=provider))
    response=client.post('/v2/check',json={'permission':'pts.poetry.read','authorization_scope':{'kind':'account'}},headers={'X-Service-Key':'synthetic-pts','Authorization':'Bearer synthetic'})
    assert response.status_code==200 and order==['provider','transaction']


def test_unknown_caller_preserves_legacy_envelope_with_canonical_enabled(fixture):
    response=post(fixture,key='foreign')
    assert response.status_code==403 and response.json()=={'detail':{'code':'service_access_denied'}}
    assert not fixture[1].calls and not fixture[2]


def test_live_provider_rejects_invalid_session_without_sql(fixture,monkeypatch):
    import httpx
    monkeypatch.setenv('SUPABASE_URL','http://provider.invalid')
    monkeypatch.setenv('SUPABASE_ANON_KEY','synthetic')
    async def request(*args,**kwargs):return httpx.Response(401,request=httpx.Request('GET','http://provider.invalid'))
    monkeypatch.setattr(httpx.AsyncClient,'get',request)
    db=Database()
    client=TestClient(create_app(Database(),capability_db=db))
    response=client.post('/v2/check',json={'permission':'pts.poetry.read','authorization_scope':{'kind':'account'}},headers={'X-Service-Key':'synthetic-pts','Authorization':'Bearer invalid'})
    assert response.status_code==401 and response.json()['error_id']=='authentication_required' and not db.calls


def test_sql_failure_is_unavailable_never_denied(fixture):
    class Broken(Database):
        async def execute(self,*args,**kwargs):raise RuntimeError('sensitive-sql-detail')
    async def provider(token,deadline):return ACCOUNT
    client=TestClient(create_app(Database(),capability_db=Broken(),capability_provider=provider))
    response=client.post('/v2/check',json={'permission':'pts.poetry.read','authorization_scope':{'kind':'account'}},headers={'X-Service-Key':'synthetic-pts','Authorization':'Bearer synthetic'})
    assert response.status_code==503 and response.json()['error_id']=='authorization_unavailable'
    assert 'sensitive' not in response.text


def test_concurrent_account_and_org_never_share_context(fixture):
    import asyncio,httpx
    from sqlalchemy import text
    scopes=[]
    class Connection(Database):
        async def execute(self,statement,parameters=None):
            await asyncio.sleep(0)
            if 'set_config' in str(statement):
                self.scope=parameters.copy();scopes.append(self.scope)
            if 'check_' in str(statement):
                assert self.scope['account']==str(ACCOUNT)
            return self
    class ConcurrentDatabase:
        @asynccontextmanager
        async def begin(self):yield Connection()
    async def provider(token,deadline):await asyncio.sleep(0);return ACCOUNT
    app=create_app(Database(),capability_db=ConcurrentDatabase(),capability_provider=provider)
    async def scenario():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://fixture') as client:
            return await asyncio.gather(*[client.post('/v2/check',json={'permission':permission,'authorization_scope':scope},headers={'X-Service-Key':key,'Authorization':'Bearer synthetic'}) for permission,scope,key in [('pts.poetry.read',{'kind':'account'},'synthetic-pts'),('leave.request.own.read',{'kind':'organization','org_id':str(ORG)},'synthetic-leave')]])
    assert [r.status_code for r in asyncio.run(scenario())]==[200,200]
    assert sorted(s['org'] for s in scopes)==['',str(ORG)]

@pytest.mark.parametrize('authorization',[None,'','Basic invalid','Bearer '])
def test_missing_or_malformed_bearer_is_authentication_error(fixture,authorization):
    headers={'X-Service-Key':'synthetic-pts'}
    if authorization is not None:headers['Authorization']=authorization
    response=fixture[0].post('/v2/check',json={'permission':'pts.poetry.read','authorization_scope':{'kind':'account'}},headers=headers)
    assert response.status_code==401 and response.json()['error_id']=='authentication_required'
    assert not fixture[1].calls and not fixture[2]


def test_environment_example_configures_canonical_pts_startup(monkeypatch):
    source=Path(__file__).resolve().parents[1]/'deployment/runtime.env.example'
    example=dict(line.split('=',1) for line in source.read_text().splitlines() if line and not line.startswith('#'))
    assert 'CAPABILITY_ACCESS_DATABASE_URL' in example
    for name in ('LEAVE_SERVICE_KEY','REFERENCE_SERVICE_KEY','PEOPLE_SERVICE_KEY','KDG_SERVICE_KEY','KDG_ORG_ID','SCRIBESWELL_SERVICE_KEY'):
        monkeypatch.delenv(name,raising=False)
    for name,value in example.items():
        if name.endswith('DATABASE_URL'):value='postgresql+psycopg://access_runtime@localhost/synthetic'
        elif name.endswith('SERVICE_KEY'):value='synthetic-'+name.lower()
        monkeypatch.setenv(name,value)
    client=TestClient(create_app(Database()))
    assert client.get('/health').json()=={'status':'running'}
    assert '/v2/identity/organization-context' in client.app.openapi()['paths']


def test_async_body_reception_timeout_cancels_stream_before_provider(fixture,monkeypatch):
    import asyncio,json
    from starlette.requests import Request
    import capability_contract
    from capability_check import CapabilityAccess
    monkeypatch.setattr(capability_contract,'BODY_RECEIVE_SECONDS',0.01)
    cancelled=[];provider=[];db=Database()
    async def receive():
        try:await asyncio.Event().wait()
        finally:cancelled.append(True)
    async def verify(*args):provider.append(True);return ACCOUNT
    scope={'type':'http','method':'POST','path':'/v2/check','headers':[(b'x-service-key',b'synthetic-pts'),(b'authorization',b'Bearer synthetic')]}
    async def run():
        return await CapabilityAccess(db,{'PTS_SERVICE_KEY':'synthetic-pts'},verify).handle(Request(scope,receive),'Bearer synthetic','synthetic-pts')
    response=asyncio.run(run())
    assert response.status_code==422 and json.loads(response.body)['error_id']=='validation_failed'
    assert cancelled==[True] and not provider and not db.calls


def timeout_request():
    import json
    from starlette.requests import Request
    raw=json.dumps({'permission':'pts.poetry.read','authorization_scope':{'kind':'account'}}).encode()
    async def receive():return {'type':'http.request','body':raw,'more_body':False}
    return Request({'type':'http','method':'POST','path':'/v2/check','headers':[(b'x-service-key',b'synthetic-pts'),(b'authorization',b'Bearer synthetic')]},receive)


def test_async_provider_timeout_cancels_before_connect(monkeypatch):
    import asyncio,json
    import capability_check
    monkeypatch.setattr(capability_check,'PROVIDER_SECONDS',0.01)
    cancelled=[];db=Database()
    async def stalled(*args):
        try:await asyncio.Event().wait()
        finally:cancelled.append(True)
    async def run():return await capability_check.CapabilityAccess(db,{'PTS_SERVICE_KEY':'synthetic-pts'},stalled).handle(timeout_request(),'Bearer synthetic','synthetic-pts')
    response=asyncio.run(run())
    assert response.status_code==503 and json.loads(response.body)['error_id']=='authorization_unavailable'
    assert cancelled==[True] and not db.calls


def test_async_connect_timeout_cancels_without_transaction(monkeypatch):
    import asyncio,json,psycopg
    import identity_context
    from capability_check import CapabilityAccess
    from studies_identity import AsyncDatabase
    monkeypatch.setattr(identity_context,'SQL_SECONDS',0.01)
    cancelled=[]
    async def connect(*args,**kwargs):
        try:await asyncio.Event().wait()
        finally:cancelled.append(True)
    monkeypatch.setattr(psycopg.AsyncConnection,'connect',connect)
    async def provider(*args):return ACCOUNT
    async def run():return await CapabilityAccess(AsyncDatabase('postgresql://access_runtime@localhost/synthetic'),{'PTS_SERVICE_KEY':'synthetic-pts'},provider).handle(timeout_request(),'Bearer synthetic','synthetic-pts')
    response=asyncio.run(run())
    assert response.status_code==503 and json.loads(response.body)['error_id']=='authorization_unavailable'
    assert cancelled==[True]


def test_async_sql_timeout_cancels_and_closes_connection_context(monkeypatch):
    import asyncio,json,psycopg
    import identity_context
    from capability_check import CapabilityAccess
    from studies_identity import AsyncDatabase
    monkeypatch.setattr(identity_context,'SQL_SECONDS',0.02)
    observed=[];context={}
    class Socket:
        def finish(self):observed.append('socket_closed')
    class Cursor:
        description=None
    class Connection:
        pgconn=Socket()
        @asynccontextmanager
        async def transaction(self):
            observed.append('transaction_entered')
            try:yield
            finally:context.clear();observed.append('transaction_exited')
        async def execute(self,sql,parameters=None):
            if 'set_config' in sql:context.update(parameters)
            if 'check_account_capability' in sql:
                try:await asyncio.Event().wait()
                finally:observed.append('sql_cancelled')
            return Cursor()
        async def close(self):observed.append('connection_closed')
    async def connect(*args,**kwargs):return Connection()
    monkeypatch.setattr(psycopg.AsyncConnection,'connect',connect)
    async def provider(*args):return ACCOUNT
    async def run():return await CapabilityAccess(AsyncDatabase('postgresql://access_runtime@localhost/synthetic'),{'PTS_SERVICE_KEY':'synthetic-pts'},provider).handle(timeout_request(),'Bearer synthetic','synthetic-pts')
    response=asyncio.run(run())
    assert response.status_code==503 and json.loads(response.body)['error_id']=='authorization_unavailable'
    assert observed[0]=='transaction_entered'
    assert 'sql_cancelled' in observed and 'transaction_exited' in observed and observed[-1]=='connection_closed'
    assert not context
