"""Focused HTTP contracts; actual restricted SQL is exercised by the native qualifier."""
import sys
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import create_app


ACCOUNT=UUID('11111111-1111-4111-8111-111111111111')
ACTOR=UUID('22222222-2222-4222-8222-222222222222')
ORG=UUID('33333333-3333-4333-8333-333333333333')

class Database:
    def __init__(self):
        self.row={'account_id':ACCOUNT,'actor_id':ACTOR,'org_id':ORG,'membership_id':9007199254740993}
        self.calls=[]; self.fail=False
    @contextmanager
    def begin(self):
        self.calls.append('begin')
        if self.fail: raise SQLAlchemyError('sensitive database payload')
        yield self
    def execute(self, statement, parameters=None):
        self.calls.append((str(statement),parameters)); return self
    def mappings(self): return self
    def one_or_none(self): return self.row

@pytest.fixture
def fixture(monkeypatch):
    monkeypatch.setenv('KDG_SERVICE_KEY','synthetic-check-key')
    monkeypatch.setenv('KDG_ORG_ID',str(ORG))
    database=Database(); auth=[]
    def authenticate(token):
        auth.append((token,len(database.calls)))
        from fastapi import HTTPException
        if token!='Bearer fixture':raise HTTPException(401,{'code':'authentication_required'})
        return ACCOUNT
    client=TestClient(create_app(database,authenticate))
    return client,database,auth

def body(permission='kdg_capture.capture.read.own'):
    return {'permission':permission,'authorization_scope':{'kind':'organization','org_id':str(ORG)}}

def post(fixture,payload=None,**kwargs):
    return fixture[0].post('/v2/check',json=payload if payload is not None else body(),headers={'Authorization':'Bearer fixture','X-Service-Key':'synthetic-check-key'},**kwargs)

@pytest.mark.parametrize('permission,resource_kind',[
    ('kdg_capture.capture.create.assigned','own_account'),
    ('kdg_capture.capture.create.all','own_account'),
    ('kdg_capture.capture.read.own','own_account'),
    ('kdg_capture.capture.edit.own','own_account'),
    ('kdg_capture.capture.read.all','organization'),
    ('kdg_capture.capture.edit.all','organization'),
    ('kdg_capture.questionnaire.manage','organization'),
    ('kdg_capture.child.manage','organization'),
    ('kdg_capture.assignment.manage','organization'),
])
def test_exact_success_resource_binding_and_fresh_decision(fixture,permission,resource_kind):
    first=post(fixture,body(permission)); second=post(fixture,body(permission))
    assert first.status_code==200,first.text
    value=first.json()
    assert set(value)=={'account_id','actor_id','permission','authorization_scope','membership_id','resource_scope','checked_at','decision_id'}
    assert value['membership_id']=='9007199254740993'
    assert value['permission']==permission and value['account_id']==str(ACCOUNT) and value['actor_id']==str(ACTOR)
    assert value['resource_scope']==({'kind':'own_account','account_id':str(ACCOUNT)} if resource_kind=='own_account' else {'kind':'organization','org_id':str(ORG)})
    assert value['authorization_scope']==body()['authorization_scope']
    assert value['checked_at'].endswith('Z') and UUID(value['decision_id'])!=UUID(second.json()['decision_id'])
    assert first.headers['cache-control']=='no-store'
    assert fixture[2][0]==('Bearer fixture',0)
    assert fixture[1].calls[1][0]=='SET TRANSACTION READ ONLY'
    assert ':permission' in fixture[1].calls[3][0]

@pytest.mark.parametrize('row,status,code',[(None,403,'access_denied'),({'account_id':ACCOUNT,'org_id':ORG,'membership_id':1,'actor_id':None},409,'identity.actor_setup_required')])
def test_denial_and_actor_after_authority(fixture,row,status,code):
    fixture[1].row=row
    response=post(fixture)
    assert (response.status_code,response.json())==(status,{'detail':{'code':code}})
    assert response.headers['cache-control']=='no-store'

@pytest.mark.parametrize('payload',[{}, {'permission':True,'authorization_scope':{'kind':'organization','org_id':str(ORG)}}, {**body(),'account_id':str(ACCOUNT)}, {**body(),'authorization_scope':{**body()['authorization_scope'],'actor_id':str(ACTOR)}}, {**body(),'authorization_scope':{'kind':'account'}}, {**body(),'authorization_scope':{'kind':'organization','org_id':'00000000-0000-0000-0000-000000000000'}}])
def test_strict_body_refuses_before_auth_and_db(fixture,payload):
    response=post(fixture,payload)
    assert response.status_code==422 and response.json()=={'detail':{'code':'validation_failed'}}
    assert not fixture[1].calls and not fixture[2]

@pytest.mark.parametrize('raw',['{"permission":"a","permission":"b"}', '{"permission":"x","authorization_scope":{"kind":"organization","kind":"organization"}}', 'NaN','[','['*1500+'0'+']'*1500,' '*65537])
def test_duplicate_malformed_deep_large_json_safe(fixture,raw):
    response=fixture[0].post('/v2/check',content=raw,headers={'X-Service-Key':'synthetic-check-key','Authorization':'Bearer fixture'})
    assert response.status_code==422 and response.json()=={'detail':{'code':'validation_failed'}}
    assert not fixture[1].calls and not fixture[2]

@pytest.mark.parametrize('payload',[body('kdg_capture.capture.read'),body('pts.poetry.read'),{**body(),'authorization_scope':{'kind':'organization','org_id':str(ACCOUNT)}}])
def test_exact_caller_policy_denies_before_subject_auth(fixture,payload):
    response=post(fixture,payload)
    assert response.status_code==403 and response.json()=={'detail':{'code':'service_access_denied'}}
    assert not fixture[1].calls and not fixture[2]

def test_invalid_service_auth_unavailable_and_foreign_result(fixture):
    client,database,auth=fixture
    response=client.post('/v2/check',json=body(),headers={'X-Service-Key':'foreign-key'})
    assert response.status_code==403 and not auth
    response=client.post('/v2/check',json=body(),headers={'X-Service-Key':'synthetic-check-key','Authorization':'Bearer bad'})
    assert response.status_code==401 and not database.calls
    database.fail=True
    response=post(fixture)
    assert response.status_code==503 and response.json()=={'detail':{'code':'authorization_unavailable'}}
    database.fail=False; database.row['account_id']=ACTOR
    assert post(fixture).status_code==503

@pytest.mark.parametrize('environment',[{'KDG_SERVICE_KEY':'x'},{'KDG_ORG_ID':str(ORG)},{'KDG_SERVICE_KEY':'x','KDG_ORG_ID':'invalid'},{'KDG_SERVICE_KEY':'x','KDG_ORG_ID':str(ORG),'PTS_SERVICE_KEY':'x'}])
def test_partial_or_shared_configuration_refuses(monkeypatch,environment):
    for name in ('KDG_SERVICE_KEY','KDG_ORG_ID','PTS_SERVICE_KEY','CONTENT_SERVICE_KEY'):monkeypatch.delenv(name,raising=False)
    for name,value in environment.items():monkeypatch.setenv(name,value)
    with pytest.raises(RuntimeError,match='kdg_check_configuration_invalid'):create_app(Database(),lambda _:ACCOUNT)

def test_absent_config_disables_and_openapi_refs_resolve(monkeypatch):
    monkeypatch.delenv('KDG_SERVICE_KEY',raising=False);monkeypatch.delenv('KDG_ORG_ID',raising=False)
    app=create_app(Database(),lambda _:ACCOUNT);client=TestClient(app)
    assert client.post('/v2/check',json=body()).status_code==403
    schema=app.openapi()
    def visit(value):
        if isinstance(value,dict):
            if '$ref' in value:
                target=schema
                for part in value['$ref'].removeprefix('#/').split('/'):target=target[part]
            for item in value.values():visit(item)
        elif isinstance(value,list):
            for item in value:visit(item)
    visit(schema)
    request=schema['paths']['/v2/check']['post']['requestBody']['content']['application/json']['schema']['oneOf'][0]
    assert request['additionalProperties'] is False
    assert request['properties']['authorization_scope']['additionalProperties'] is False
    assert schema['paths']['/v2/check']['post']['security']==[{'KdgBearer':[],'KdgServiceKey':[]}]
    schemes=schema['components']['securitySchemes']
    assert schemes['KdgBearer']=={'type':'http','scheme':'bearer'}
    assert schemes['KdgServiceKey']=={'type':'apiKey','in':'header','name':'X-Service-Key'}

@pytest.mark.parametrize('membership',[True,1.5,0,-1,9223372036854775808,'1'])
def test_unsafe_internal_membership_never_becomes_authority(fixture,membership):
    fixture[1].row['membership_id']=membership
    response=post(fixture)
    assert response.status_code==503 and response.json()=={'detail':{'code':'authorization_unavailable'}}


def test_legacy_pts_route_stays_closed(fixture):
    response=fixture[0].post('/v1/check',json={'org_id':str(ORG),'permission':'pts.poetry.read'})
    assert response.status_code==503 and response.json()=={'detail':{'code':'authorization_unavailable'}}
    assert not fixture[1].calls and not fixture[2]


def test_non_ascii_service_key_safely_denied(fixture):
    response=fixture[0].post('/v2/check',json=body(),headers=[(b'x-service-key',b'\xc3\xa9')])
    assert response.status_code==403 and response.json()=={'detail':{'code':'service_access_denied'}}
    assert not fixture[1].calls


def test_controlled_migration_refuses_before_any_ddl(monkeypatch):
    import importlib.util
    directory=Path(__file__).resolve().parents[1]/'migrations'
    sys.path.insert(0,str(directory))
    import access_organization_check_catalog as catalog
    spec=importlib.util.spec_from_file_location('_organization_migration_test',directory/'versions/0015_organization_check.py')
    migration=importlib.util.module_from_spec(spec);spec.loader.exec_module(migration)
    calls=[]
    class Connection:
        def exec_driver_sql(self,*args,**kwargs):calls.append(args)
    connection=Connection()
    monkeypatch.setattr(migration.op,'get_bind',lambda:connection)
    def refuse(*args,**kwargs):raise catalog.BaselineError('unsafe_fixture')
    monkeypatch.setattr(catalog,'verify_reader_role',refuse)
    with pytest.raises(catalog.BaselineError,match='unsafe_fixture'):migration.upgrade()
    assert not calls
    monkeypatch.setattr(catalog,'verify_reader_role',lambda *_args,**_kwargs:None)
    migration.upgrade()
    sql=calls[0][0]
    sequence=[
        'GRANT CREATE ON SCHEMA access TO access_check_reader;',
        'SET LOCAL ROLE access_check_reader;',
        'CREATE FUNCTION access.check_organization_permission(p_permission text)',
        'REVOKE ALL ON FUNCTION access.check_organization_permission(text)',
        'GRANT EXECUTE ON FUNCTION access.check_organization_permission(text) TO access_runtime;',
        'RESET ROLE;',
        'REVOKE CREATE ON SCHEMA access FROM access_check_reader;']
    positions=[sql.index(statement) for statement in sequence]
    assert positions==sorted(positions)
    assert 'ALTER FUNCTION' not in sql and 'check_function_bodies' not in sql
    assert 'GRANT USAGE ON SCHEMA identity' not in sql
    assert (migration.revision,migration.down_revision)==('access_0015','access_0014')
    with pytest.raises(RuntimeError,match='Destructive rollback'):migration.downgrade()


def test_provider_unavailability_uses_canonical_safe_error(fixture,monkeypatch):
    import httpx
    import main
    monkeypatch.setenv('SUPABASE_URL','https://fixture.invalid')
    monkeypatch.setenv('SUPABASE_ANON_KEY','synthetic-provider-key')
    def unavailable(*args,**kwargs):raise httpx.HTTPError('sensitive-provider-response')
    monkeypatch.setattr(main.httpx,'get',unavailable)
    database=Database()
    client=TestClient(create_app(database))
    response=client.post('/v2/check',json=body(),headers={'X-Service-Key':'synthetic-check-key','Authorization':'Bearer fixture'})
    assert response.status_code==503 and response.json()=={'detail':{'code':'authorization_unavailable'}}
    assert not database.calls and response.headers['cache-control']=='no-store'


def test_default_runtime_engine_bounds_pool_and_connect_waits(fixture,monkeypatch):
    import main
    observed=[]
    database=Database()
    def engine(url,**options):
        observed.append(options)
        return database
    monkeypatch.setattr(main,'create_engine',engine)
    create_app(authenticate=lambda _:ACCOUNT)
    assert observed[0]['pool_timeout']==5
    assert observed[0]['connect_args']['connect_timeout']==5
    assert observed[0]['hide_parameters'] is True


@pytest.mark.parametrize('payload',[
    {'id':12}, {'id':{}}, {'id':[]}, {'id':None}, {'id':True},
    {'id':'malformed'}, {}, [], None,
])
def test_malformed_provider_success_is_safe_unavailable(fixture,monkeypatch,payload):
    import httpx
    import main
    monkeypatch.setenv('SUPABASE_URL','https://fixture.invalid')
    monkeypatch.setenv('SUPABASE_ANON_KEY','synthetic-provider-key')
    response=httpx.Response(200,json=payload,request=httpx.Request('GET','https://fixture.invalid'))
    monkeypatch.setattr(main.httpx,'get',lambda *_args,**_kwargs:response)
    database=Database()
    client=TestClient(create_app(database))
    result=client.post('/v2/check',json=body(),headers={'X-Service-Key':'synthetic-check-key','Authorization':'Bearer fixture'})
    assert result.status_code==503 and result.json()=={'detail':{'code':'authorization_unavailable'}}
    assert result.headers['cache-control']=='no-store' and not database.calls


@pytest.mark.parametrize('key',['é','key\x00','key\x1f','key\x7f','key\n','key word'])
def test_configured_service_key_must_be_printable_ascii(fixture,monkeypatch,key):
    if '\x00' in key:
        # Environment APIs themselves reject NUL; exercise the same startup policy.
        from organization_check import router
        with pytest.raises(RuntimeError,match='kdg_check_configuration_invalid'):
            router(Database(),lambda _:ACCOUNT,{'KDG_SERVICE_KEY':key,'KDG_ORG_ID':str(ORG)})
    else:
        monkeypatch.setenv('KDG_SERVICE_KEY',key)
        with pytest.raises(RuntimeError,match='kdg_check_configuration_invalid'):create_app(Database(),lambda _:ACCOUNT)


def test_stalled_authenticated_request_body_has_receive_deadline(fixture,monkeypatch):
    import asyncio
    import httpx
    import organization_check
    monkeypatch.setattr(organization_check,'BODY_RECEIVE_TIMEOUT',0.01)
    database=Database()
    auth=[]
    app=create_app(database,lambda token:auth.append(token) or ACCOUNT)
    async def scenario():
        async def stalled():
            yield b'{"permission":'
            await asyncio.Event().wait()
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://fixture') as client:
            async with asyncio.timeout(1):
                return await client.post('/v2/check',content=stalled(),headers={'X-Service-Key':'synthetic-check-key','Authorization':'Bearer fixture'})
    result=asyncio.run(scenario())
    assert result.status_code==422 and result.json()=={'detail':{'code':'validation_failed'}}
    assert result.headers['cache-control']=='no-store' and not database.calls and not auth


def test_reader_preparation_checks_receiving_authority_before_grant():
    sql=(Path(__file__).resolve().parents[1]/'tools/prepare_access_check_reader_execution.sql').read_text()
    grant=sql.index('GRANT access_check_reader TO access_migrator')
    assert sql.index("rolname='access_migrator' AND rolcanlogin")<grant
    assert sql.index("WHERE member='access_migrator'::regrole")<grant
    assert sql.index("WHERE roleid='access_migrator'::regrole")<grant
    assert "('postgres','supabase_admin',true,false,false),('postgres','postgres',false,false,true)" in sql
    assert "rolname='postgres' AND rolcanlogin AND NOT rolsuper" in sql
    assert "rolname='supabase_admin' AND rolcanlogin AND rolsuper" in sql
    assert "current_setting('server_version_num')::integer < 160000" in sql
    assert "WITH ADMIN FALSE, INHERIT FALSE, SET TRUE" in sql
