"""Studies owner acceptance: no organization prerequisite or implicit setup on checks."""
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import create_app

ACCOUNT=UUID('11111111-1111-4111-8111-111111111111')
ACTOR=UUID('22222222-2222-4222-8222-222222222222')
OP='33333333-3333-4333-8333-333333333333'
class Database:
    def __init__(self):self.calls=[];self.row={'account_id':ACCOUNT,'actor_id':ACTOR,'disposition':'created'}
    @asynccontextmanager
    async def begin(self):yield self
    async def execute(self,statement,parameters=None):self.calls.append((str(statement),parameters));return self
    def mappings(self):return self
    def one_or_none(self):return self.row

@pytest.fixture
def fixture(monkeypatch):
    monkeypatch.setenv('SCRIBESWELL_SERVICE_KEY','synthetic-studies-key')
    db=Database(); identity=Database()
    async def verify(token,deadline):return ACCOUNT
    app=create_app(db,studies_provider=verify,studies_identity_db=identity,studies_setup_db=identity,studies_db=db)
    return TestClient(app),db,identity

def post(fixture,path='/v2/enrollments/scribeswell-studies',body=None,key='synthetic-studies-key'):
    return fixture[0].post(path,json=body or {'operation_id':OP},headers={'Authorization':'Bearer synthetic','X-Service-Key':key})

def test_enroll_then_check_without_memberships(fixture):
    response=post(fixture)
    assert response.status_code==200,response.text
    assert response.json()=={'operation_id':OP,'status':'committed','result':{'disposition':'created','account_id':str(ACCOUNT),'actor_id':str(ACTOR),'permission':'scribeswell.studies.use'}}
    assert response.headers['cache-control']=='private, no-store'
    fixture[1].row.pop('disposition')
    response=post(fixture,'/v2/check',{'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
    assert response.status_code==200,response.text
    assert set(response.json())=={'account_id','actor_id','permission','authorization_scope','decision_id','checked_at'}
    assert response.headers['cache-control']=='private, no-store'
    assert not any('prepare_studies' in sql for sql,_ in fixture[2].calls)

@pytest.mark.parametrize('field',['account_id','actor_id','email','org_id','permission'])
def test_target_selectors_fail_before_identity(fixture,field):
    response=post(fixture,body={'operation_id':OP,field:str(ACCOUNT)})
    assert response.status_code==422 and not fixture[2].calls
    assert response.json()['error_id']=='validation_failed'

def test_wrong_caller_and_duplicate_keys(fixture):
    assert post(fixture,key='other').status_code==403
    response=fixture[0].post('/v2/enrollments/scribeswell-studies',content='{"operation_id":"'+OP+'","operation_id":"'+OP+'"}',headers={'X-Service-Key':'synthetic-studies-key'})
    assert response.status_code==422 and not fixture[2].calls

def test_denial_does_not_create_or_replay(fixture):
    fixture[1].row=None
    response=post(fixture)
    assert response.status_code==403 and response.json()['error_id']=='access_denied'

@pytest.mark.parametrize('scope',[{'kind':'organization','org_id':str(ACCOUNT)}, {'kind':'own_account','account_id':str(ACCOUNT)}, {'kind':'account','org_id':str(ACCOUNT)}])
def test_account_scope_never_falls_back(fixture,scope):
    response=post(fixture,'/v2/check',{'permission':'scribeswell.studies.use','authorization_scope':scope})
    assert response.status_code==422 and not fixture[2].calls

def test_actor_only_completion_resumes_with_same_actor(fixture):
    fixture[2].row={'account_id':ACCOUNT,'actor_id':None}
    setup=Database() # independent restricted setup connection
    async def verify(token,deadline):return ACCOUNT
    client=TestClient(create_app(Database(),studies_provider=verify,studies_identity_db=fixture[2],studies_setup_db=setup,studies_db=fixture[1]))
    response=client.post('/v2/enrollments/scribeswell-studies',json={'operation_id':OP},headers={'X-Service-Key':'synthetic-studies-key'})
    assert response.status_code==200 and response.json()['result']['actor_id']==str(ACTOR)
    assert sum('prepare_studies_account' in sql for sql,_ in setup.calls)==1

def test_check_does_not_set_up_actor(fixture):
    fixture[2].row={'account_id':ACCOUNT,'actor_id':None}
    response=post(fixture,'/v2/check',{'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}})
    assert response.status_code==503 and response.json()['error_id']=='identity.setup_unavailable'
    assert not fixture[1].calls

def test_same_operation_uses_retained_disposition_and_rechecks(fixture):
    assert post(fixture).json()['result']['disposition']=='created'
    assert post(fixture).json()['result']['disposition']=='created'
    fixture[1].row=None
    assert post(fixture).status_code==403
    assert sum('studies_account_evidence()' in sql for sql,_ in fixture[2].calls)==3

@pytest.mark.parametrize('other',['KDG_SERVICE_KEY','PTS_SERVICE_KEY','CONTENT_SERVICE_KEY'])
def test_shared_service_credential_configuration_refused(monkeypatch,other):
    monkeypatch.setenv('SCRIBESWELL_SERVICE_KEY','synthetic-shared')
    monkeypatch.setenv(other,'synthetic-shared')
    with pytest.raises(RuntimeError,match='studies_configuration_invalid'):create_app(Database())

@pytest.mark.parametrize('value',['not-a-database-url','postgresql://wrong_runtime@localhost/synthetic'])
def test_runtime_database_configuration_refuses_safe_before_activation(monkeypatch,value):
    monkeypatch.setenv('STUDIES_ACCESS_DATABASE_URL',value)
    with pytest.raises(RuntimeError,match='studies_configuration_invalid'):create_app(Database())

def test_opt_in_without_all_dedicated_owner_connections_refuses(monkeypatch):
    monkeypatch.setenv('SCRIBESWELL_SERVICE_KEY','synthetic-studies-key')
    for name in ('STUDIES_ACCESS_DATABASE_URL','STUDIES_IDENTITY_DATABASE_URL','STUDIES_IDENTITY_SETUP_DATABASE_URL'):monkeypatch.delenv(name,raising=False)
    with pytest.raises(RuntimeError,match='studies_configuration_invalid'):create_app(Database())

@pytest.mark.parametrize('name,value',[
 ('STUDIES_ACCESS_DATABASE_URL','postgresql://access_studies_runtime@localhost/synthetic'),
 ('STUDIES_IDENTITY_DATABASE_URL','postgresql://identity_studies_reader_runtime@localhost/synthetic'),
 ('STUDIES_IDENTITY_SETUP_DATABASE_URL','postgresql://identity_studies_setup_runtime@localhost/synthetic'),
 ('STUDIES_READINESS_JSON','{}'),('SCRIBESWELL_SERVICE_KEY','')])
def test_keyless_partial_runtime_configuration_refuses(monkeypatch,name,value):
    monkeypatch.delenv('SCRIBESWELL_SERVICE_KEY',raising=False)
    monkeypatch.setenv(name,value)
    with pytest.raises(RuntimeError,match='^studies_configuration_invalid$'):create_app(Database())

def test_dependency_failure_emits_only_safe_structured_correlation(fixture,caplog):
    class Broken(Database):
        async def execute(self,*args,**kwargs):raise RuntimeError('secret-password Bearer synthetic private-account')
    async def provider(token,deadline):return ACCOUNT
    client=TestClient(create_app(Database(),studies_provider=provider,studies_identity_db=Database(),studies_setup_db=Database(),studies_db=Broken()))
    with caplog.at_level('WARNING',logger='access.studies'):
        response=client.post('/v2/enrollments/scribeswell-studies',json={'operation_id':OP},headers={'X-Service-Key':'synthetic-studies-key','Authorization':'Bearer synthetic','X-Trace-Id':'untrusted-secret'})
    assert response.status_code==503
    records=[r for r in caplog.records if r.name=='access.studies']
    assert len(records)==1
    record=records[0]
    assert record.error_id=='dependency_unavailable' and record.operation_id==OP
    assert str(UUID(record.trace_id))==record.trace_id
    assert record.getMessage()=='studies_dependency_failed'
    assert record.exc_info is None
    rendered=repr(record.__dict__)
    for secret in ('secret-password','Bearer synthetic','private-account','untrusted-secret',str(ACCOUNT),str(ACTOR)):
        assert secret not in rendered
