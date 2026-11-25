"""Entry owner behavior; native authorization/persistence are separate required evidence."""
import asyncio,sys,time
from pathlib import Path
from uuid import uuid4
from datetime import datetime,timezone,timedelta
import httpx,pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import create_app
from access_client import AccessClient,Decision,EntryContext,Failure
from contracts import Receipt,SelectionResult
from transaction_context import VerifiedContext,WriteError
ORG=str(uuid4());ACCOUNT=str(uuid4());ACTOR=str(uuid4());EVENT=str(uuid4());OP=str(uuid4())
class Access:
    def __init__(self):self.calls=[];self.denied=False
    async def session(self,authorization,budget):
        self.calls.append('session')
        if self.denied:raise Failure(401,'authentication_required')
        return ACCOUNT
    async def authorize(self,authorization,org,budget):
        await self.session(authorization,budget);self.calls.append('entry')
        return EntryContext(Decision(account_id=ACCOUNT,actor_id=ACTOR,permission='leave.request.own.read',authorization_scope={'kind':'organization','org_id':org},resource_scope={'kind':'organization','org_id':org},membership_id='19',decision_id=str(uuid4()),checked_at=datetime.now(timezone.utc).isoformat()),VerifiedContext(org,ACCOUNT,ACTOR,'all_write',time.monotonic()))
class Repo:
    def __init__(self):self.events={};self.fail=False;self.calls=[]
    async def run(self,kind,context,budget,operation):
        self.calls.append(context)
        if self.fail:raise WriteError('outcome_unresolved')
        if kind=='select':self.events.setdefault(operation,Receipt(operation_id=operation,result=SelectionResult(org_id=context.local.org_id,event_id=EVENT)).model_dump())
        return self.events.get(operation)
def run(kind='select',access=None,repo=None,body=None):
    async def execute():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=create_app(repo or Repo(),access or Access(),{})),base_url='http://leave') as client:
            headers={'Authorization':'Bearer synthetic'}
            return await (client.post(f'/v1/organizations/{ORG}/context/selection',headers=headers,content=body or '{"operation_id":"'+OP+'"}') if kind=='select' else client.get(f'/v1/organizations/{ORG}/context/operations/{OP}',headers=headers))
    return asyncio.run(execute())
def test_selection_original_receipt_fresh_authority_and_unresolved():
    access,repo=Access(),Repo()
    missing=run('lookup',access,repo);assert missing.status_code==202 and missing.json()['status']=='unresolved'
    first=run(access=access,repo=repo);second=run(access=access,repo=repo)
    assert first.status_code==second.status_code==200 and first.json()==second.json() and len(repo.events)==1
    assert run('lookup',access,repo).json()==first.json()
    assert len(access.calls)==8
    access.denied=True
    before=len(repo.calls);r=run('lookup',access,repo)
    assert r.status_code==401 and len(repo.calls)==before and 'event_id' not in r.text
    assert r.headers['cache-control']=='private, no-store'
def test_audit_failure_never_acknowledges():
    repo=Repo();repo.fail=True;r=run(repo=repo)
    assert r.status_code==503 and r.json()['error_id']=='outcome_unresolved' and not repo.events
@pytest.mark.parametrize('body',['{}','{"operation_id":"'+OP+'","actor_id":"'+ACTOR+'"}','{"operation_id":"'+OP+'","operation_id":"'+OP+'"}'])
def test_invalid_input_has_no_authorization_or_write(body):
    access,repo=Access(),Repo();assert run(access=access,repo=repo,body=body).status_code==422
    assert not access.calls and not repo.calls

def test_real_http_adapter_binds_session_and_full_entry_decision_without_people():
    requests=[]
    async def handler(request):
        requests.append(request)
        if request.url.path.endswith('current-session'):return httpx.Response(200,json={'account_id':ACCOUNT,'session_id':str(uuid4()),'credential_expires_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),'observed_at':datetime.now(timezone.utc).isoformat()})
        context=await Access().authorize('Bearer synthetic',ORG,type('Budget',(),{})())
        return httpx.Response(200,json=context.decision.model_dump())
    from transaction_context import Budget
    async def execute():
        client=AccessClient('http://localhost:8191','s'*40,'c'*40,'p'*40,transport=httpx.MockTransport(handler))
        return await client.authorize('Bearer synthetic',ORG,Budget())
    result=asyncio.run(execute())
    assert result.decision.membership_id=='19' and result.decision.decision_id
    assert [r.url.path for r in requests]==['/v2/identity/current-session','/v2/organizations/entry']
    assert requests[0].headers['x-service-key']=='c'*40 and requests[1].headers['x-service-key']=='s'*40

@pytest.mark.parametrize('kind',['select','lookup'])
@pytest.mark.parametrize('foreign_field',['account_id','authorization_scope','resource_scope'])
def test_real_http_foreign_decision_binding_fails_before_repository(kind,foreign_field):
    requests=[]
    async def handler(request):
        requests.append(request.url.path)
        if request.url.path.endswith('current-session'):
            return httpx.Response(200,json={'account_id':ACCOUNT,'session_id':str(uuid4()),'credential_expires_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),'observed_at':datetime.now(timezone.utc).isoformat()})
        context=await Access().authorize('Bearer synthetic',ORG,type('Budget',(),{})())
        decision=context.decision.model_dump()
        decision[foreign_field]=str(uuid4()) if foreign_field=='account_id' else {'kind':'organization','org_id':str(uuid4())}
        # Still a well-formed decision: only the requested account/scope binding differs.
        Decision.model_validate(decision)
        return httpx.Response(200,json=decision)
    access=AccessClient('http://localhost:8191','s'*40,'c'*40,'p'*40,transport=httpx.MockTransport(handler))
    repo=Repo();response=run(kind,access,repo)
    assert response.status_code==503 and response.json()['error_id']=='authorization_unavailable'
    assert requests==['/v2/identity/current-session','/v2/organizations/entry']
    assert not repo.calls and not repo.events and 'event_id' not in response.text

@pytest.mark.parametrize('query',['?sslmode=require','?sslmode=verify-full&connect_timeout=5',''])
def test_hosted_database_tls_is_bounded(query):
    from repository import Repository
    from runtime_database import validated_url
    value='postgresql+psycopg://leave_runtime:private@db.fixture.supabase.co/postgres'+query
    assert validated_url(value).username=='leave_runtime'
    assert 'sslmode' in Repository(value).url or not query

@pytest.mark.parametrize('query',['?sslmode=disable','?sslmode=prefer','?options=-c%20role%3Dleave_owner','?sslmode=require&connect_timeout=11','?sslmode=require&sslmode=disable','?connect_timeout=5'])
def test_hosted_database_tls_refuses_unqualified_options(query):
    from repository import Repository
    with pytest.raises(ValueError):Repository('postgresql+psycopg://leave_runtime:private@db.fixture.supabase.co/postgres'+query)

def test_hosted_access_origin_is_fixed_private_compose_owner():
    assert AccessClient('http://access:8000','admission','session','preference').config.origin=='http://access:8000'
    for origin in ['http://foreign:8000','http://access:8001','http://access:8000/path','http://access:8000@foreign']:
        with pytest.raises(Exception):AccessClient(origin,'admission','session','preference')

def test_hosted_migration_report_preflight_refuses_before_database(tmp_path,monkeypatch):
    import migrate
    monkeypatch.setenv('MIGRATION_EVIDENCE_DIR',str(tmp_path/'missing'))
    calls=[]
    monkeypatch.setattr(migrate,'create_engine',lambda *args,**kwargs:calls.append(args))
    with pytest.raises(ValueError):migrate.upgrade()
    assert calls==[]

def test_hosted_migration_failure_report_is_restricted_and_requires_reconciliation(tmp_path,monkeypatch):
    import migrate,json,stat
    monkeypatch.setenv('MIGRATION_EVIDENCE_DIR',str(tmp_path))
    monkeypatch.delenv('LEAVE_MIGRATION_DATABASE_URL',raising=False)
    with pytest.raises(RuntimeError):migrate.upgrade()
    target=tmp_path/'migrations.json';report=json.loads(target.read_text())
    assert report=={'complete':False,'owners':{'leave':{'status':'failed','before':None,'revision':None}},'outcome_requires_reconciliation':True}
    assert stat.S_IMODE(target.stat().st_mode)==0o600
