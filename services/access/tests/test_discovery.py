"""Discovery transport acceptance; native qualification supplies actual eligibility proof."""
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
import sys
from uuid import UUID
import pytest
import psycopg
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import create_app
ACCOUNT=UUID('11111111-1111-4111-8111-111111111111')
ORG=UUID('33333333-3333-4333-8333-333333333333')

class Database:
    def __init__(self):self.calls=[];self.rows=[];self.active=True
    @asynccontextmanager
    async def begin(self):yield self
    async def execute(self,sql,parameters=None):
        self.calls.append((str(sql),parameters))
        if 'access.discover_' in str(sql) and not self.active:
            class AccountDenied(psycopg.Error):sqlstate='ID003'
            raise AccountDenied('discovery_account_denied')
        return self
    def mappings(self):return self
    def all(self):return self.rows
    def one_or_none(self):return {'account_id':ACCOUNT} if self.active else None

@pytest.fixture
def fixture(monkeypatch):
    for name in ('LEAVE','REFERENCE','DIRECTORY','PTS','PEOPLE'):monkeypatch.setenv(name+'_SERVICE_KEY','synthetic-'+name.lower())
    db=Database();provider=[]
    async def verify(token,deadline):provider.append(token);return ACCOUNT
    return TestClient(create_app(Database(),capability_db=db,capability_provider=verify)),db,provider

def get(fixture,path='/v2/organizations?application=leave',caller='leave',**kwargs):
    return fixture[0].get(path,headers={'Authorization':'Bearer synthetic','X-Service-Key':'synthetic-'+caller},**kwargs)

def test_organizations_do_not_require_actor_person_or_employment(fixture):
    fixture[1].rows=[dict(org_id=ORG,org_name='For Profit Limited',membership_id=9223372036854775807)]
    response=get(fixture)
    assert response.status_code==200,response.text
    assert response.json()=={'organizations':[{'org_id':str(ORG),'name':'For Profit Limited','membership_id':'9223372036854775807'}],'next_cursor':None}
    assert response.headers['cache-control']=='private, no-store'

def test_reference_organizations_are_current_and_app_specific(fixture):
    reference_org=UUID('55555555-5555-4555-8555-555555555555')
    fixture[1].rows=[dict(org_id=reference_org,org_name='Reference Publishing Limited',membership_id=29)]
    response=get(fixture,'/v2/organizations?application=reference','reference')
    assert response.status_code==200,response.text
    assert response.json()=={'organizations':[{'org_id':str(reference_org),'name':'Reference Publishing Limited','membership_id':'29'}],'next_cursor':None}
    assert response.headers['cache-control']=='private, no-store'
    fixture[1].rows=[]
    current=get(fixture,'/v2/organizations?application=reference','reference')
    assert current.status_code==200,current.text
    assert current.json()=={'organizations':[],'next_cursor':None}
    queries=[parameters for sql,parameters in fixture[1].calls if 'access.discover_organizations' in sql]
    assert queries==[{'application':'reference','after':None,'page_size':100}]*2
    assert len(fixture[2])==2

def test_page_fetches_extra_eligible_row_and_cursor_is_position_only(fixture):
    fixture[1].rows=[dict(org_id=UUID(int=n),org_name='Organization',membership_id=n) for n in (1,2)]
    response=get(fixture,'/v2/organizations?application=leave&page_size=1')
    assert response.status_code==200,response.text
    body=response.json();assert len(body['organizations'])==1 and body['next_cursor']
    fixture[1].rows=[]
    assert get(fixture,'/v2/organizations?application=leave&page_size=1&cursor='+body['next_cursor']).json()=={'organizations':[],'next_cursor':None}
    assert len(fixture[2])==2
    assert any('discover_organizations' in sql and params['page_size']==1 for sql,params in fixture[1].calls)

def test_empty_and_disabled_account_are_distinct(fixture):
    assert get(fixture).json()=={'organizations':[],'next_cursor':None}
    fixture[1].active=False
    response=get(fixture)
    assert response.status_code==403 and response.json()['error_id']=='access_denied'

def test_apps_are_unique_canonical_scope_aggregate_without_organization_details(fixture):
    fixture[1].rows=[dict(app_id='pts',eligible_scope_kinds=['account']),dict(app_id='reference',eligible_scope_kinds=['account','organization'])]
    response=get(fixture,'/v2/applications','directory')
    assert response.status_code==200,response.text
    assert response.json()['applications']==fixture[1].rows
    assert response.json()['checked_at'].endswith('Z')
    assert response.headers['cache-control']=='private, no-store'

@pytest.mark.parametrize('path,caller',[
 ('/v2/organizations?application=reference','leave'),('/v2/organizations?application=leave','reference'),
 ('/v2/organizations?application=leave','directory'),('/v2/applications','leave'),('/v2/applications','pts'),('/v2/applications','people')])
def test_closed_service_route_policy_precedes_provider(fixture,path,caller):
    response=get(fixture,path,caller)
    assert response.status_code==403 and response.json()['error_id']=='service_access_denied'
    assert not fixture[2] and not fixture[1].calls

@pytest.mark.parametrize('query',['','application=leave&account_id='+str(ACCOUNT),'application=leave&application=leave','application=leave&page_size=0','application=leave&page_size=101','application=leave&page_size=01','application=leave&cursor=garbage','application=unknown','application=leave&cursor='+('a'*100)])
def test_unknown_duplicate_spoofed_and_invalid_query_fields(fixture,query):
    response=get(fixture,'/v2/organizations?'+query)
    assert response.status_code==422 and response.json()['error_id']=='validation_failed'
    assert not fixture[2] and not fixture[1].calls

@pytest.mark.parametrize('rows',[
 [{'org_id':ORG,'org_name':'name','membership_id':'1'}],
 [{'org_id':ORG,'org_name':'name','membership_id':True}],
 [{'org_id':ORG,'org_name':None,'membership_id':1}],
 [{'org_id':ORG,'org_name':'name','membership_id':1}]*2])
def test_malformed_membership_dependency_is_unavailable(fixture,rows):
    fixture[1].rows=rows
    response=get(fixture)
    assert response.status_code==503 and response.json()['error_id']=='authorization_unavailable'

@pytest.mark.parametrize('rows',[
 [{'app_id':'pts','eligible_scope_kinds':[]}],
 [{'app_id':'pts','eligible_scope_kinds':['organization','account']}],
 [{'app_id':'pts','eligible_scope_kinds':['account','account']}],
 [{'app_id':'pts','eligible_scope_kinds':['account']}]*2])
def test_malformed_application_dependency_is_unavailable(fixture,rows):
    fixture[1].rows=rows
    response=get(fixture,'/v2/applications','directory')
    assert response.status_code==503 and response.json()['error_id']=='authorization_unavailable'

def test_directory_cannot_check_capabilities(fixture):
    response=fixture[0].post('/v2/check',json={'permission':'pts.poetry.read','authorization_scope':{'kind':'account'}},headers={'X-Service-Key':'synthetic-directory','Authorization':'Bearer synthetic'})
    assert response.status_code==403 and response.json()['error_id']=='service_access_denied'
    assert not fixture[2] and not fixture[1].calls

def test_unknown_application_fields_and_duplicate_credentials_rejected(fixture):
    response=get(fixture,'/v2/applications?account_id='+str(ACCOUNT),'directory')
    assert response.status_code==422
    response=fixture[0].get('/v2/applications',headers=[('Authorization','Bearer synthetic'),('X-Service-Key','synthetic-directory'),('X-Service-Key','synthetic-directory')])
    assert response.status_code==403
    assert not fixture[2] and not fixture[1].calls

def test_unexpected_failure_is_internal_error(fixture,monkeypatch):
    async def broken(*args):raise RuntimeError('sensitive value must never escape')
    monkeypatch.setattr('discovery.read',broken)
    response=get(fixture)
    assert response.status_code==500 and response.json()=={'error_id':'internal_error','error':'Request could not be completed','details':{}}

def request():
    from starlette.requests import Request
    return Request({'type':'http','method':'GET','path':'/v2/organizations','query_string':b'application=leave','headers':[(b'x-service-key',b'synthetic-leave'),(b'authorization',b'Bearer synthetic')]})

def test_provider_timeout_cancels_before_sql(monkeypatch):
    import discovery
    monkeypatch.setattr(discovery,'PROVIDER_SECONDS',0.01)
    cancelled=[];db=Database()
    async def stalled(*args):
        try:await asyncio.Event().wait()
        finally:cancelled.append(True)
    async def run():return await discovery.Discovery(db,{'LEAVE_SERVICE_KEY':'synthetic-leave'},stalled).handle(request(),'Bearer synthetic','synthetic-leave')
    response=asyncio.run(run())
    assert response.status_code==503 and cancelled==[True] and not db.calls

def test_total_budget_encloses_provider_and_sql_and_releases_context(monkeypatch):
    import discovery,discovery_query
    monkeypatch.setattr(discovery,'EXECUTION_SECONDS',0.04)
    monkeypatch.setattr(discovery,'PROVIDER_SECONDS',0.2)
    monkeypatch.setattr(discovery_query,'SQL_SECONDS',0.2)
    observed=[]
    class SlowDatabase(Database):
        @asynccontextmanager
        async def begin(self):
            try:yield self
            finally:observed.append('transaction_closed')
        async def execute(self,sql,parameters=None):
            if 'discover_organizations' in str(sql):
                try:await asyncio.Event().wait()
                finally:observed.append('sql_cancelled')
            return await super().execute(sql,parameters)
    async def provider(*args):await asyncio.sleep(0.02);return ACCOUNT
    async def run():return await discovery.Discovery(SlowDatabase(),{'LEAVE_SERVICE_KEY':'synthetic-leave'},provider).handle(request(),'Bearer synthetic','synthetic-leave')
    response=asyncio.run(run())
    assert response.status_code==503 and observed==['sql_cancelled','transaction_closed']

def test_untrusted_provider_identity_is_unavailable_before_sql():
    import discovery
    db=Database()
    async def provider(*args):return 'malformed'
    async def run():return await discovery.Discovery(db,{'LEAVE_SERVICE_KEY':'synthetic-leave'},provider).handle(request(),'Bearer synthetic','synthetic-leave')
    assert asyncio.run(run()).status_code==503 and not db.calls

def test_catalogue_overflow_is_not_silent_truncation(fixture):
    fixture[1].rows=[dict(app_id='app'+str(n).zfill(3),eligible_scope_kinds=['account']) for n in range(129)]
    response=get(fixture,'/v2/applications','directory')
    assert response.status_code==503 and response.json()['error_id']=='authorization_unavailable'

def test_documented_query_schema_matches_manual_closed_validation(fixture):
    operation=fixture[0].app.openapi()['paths']['/v2/organizations']['get']
    parameters={item['name']:item for item in operation['parameters'] if item['in']=='query'}
    assert parameters['application']['required'] is True
    assert parameters['page_size']['schema']=={'type':'integer','minimum':1,'maximum':100,'default':100}
    assert operation['security']==[{'KdgBearer':[],'KdgServiceKey':[]}]

def test_runtime_reads_only_one_access_routine_and_no_identity_projection(fixture):
    assert get(fixture).status_code==200
    statements=[sql for sql,_ in fixture[1].calls if not sql.startswith('SET ') and 'set_config' not in sql]
    assert len(statements)==1 and 'access.discover_organizations' in statements[0]
