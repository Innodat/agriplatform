"""Composed opening acceptance: complete response with one current preparation."""
import asyncio,copy,sys
from pathlib import Path
from uuid import uuid4
import httpx,pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import create_app
from test_draft_context import Access,People,Config,ORG,NOW
from drafts import Active,Discarded,DraftFailure,empty_input
from access_client import Failure
DRAFT=str(uuid4());TYPE=str(uuid4());VERSION=str(uuid4())
class Store:
    def __init__(self):self.calls=[];self.closed=False;self.error=None
    async def editor(self,prepared,budget,draft):
        self.calls.append((prepared,draft))
        if self.error:raise self.error
        p=prepared.public
        base=dict(org_id=p.org_id,draft_id=draft,revision='7')
        value=Discarded(**base,state='discarded',discarded_at=NOW.isoformat()) if self.closed else Active(**base,state='active',input={**empty_input(),'leave_type_id':TYPE,'note':' exact 😀 e\u0301 \n'},editability=p.editability,setup_notices=p.setup_notices,updated_at=NOW.isoformat())
        return value,dict(scope_generation='3',active_draft=None if self.closed else dict(draft_id=draft,revision='7'))
class Choices:
    def __init__(self):self.calls=[];self.error=None;self.obsolete=False
    async def choices(self,context,org,selected,after,budget):
        self.calls.append((context,org,selected,after))
        if self.error:raise self.error
        return dict(choices=[],next_cursor=None,selected=dict(status='obsolete') if self.obsolete else dict(status='available',choice=dict(type_id=selected,version_id=VERSION,name='Selected outside first page',revision='2',permitted_modes=['full_days','hours'])))
def request(store=None,choices=None,access=None,people=None,config=None,suffix='',headers=None):
    async def run():
        app=create_app(repository=object(),access=access or Access(),environment={},people=people or People(),configuration=config or Config(),clock=lambda:NOW,drafts=store or Store(),choices=choices or Choices())
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://leave') as c:return await c.get(f'/v1/organizations/{ORG}/drafts/{DRAFT}/editor'+suffix,headers=headers if headers is not None else {'Authorization':'Bearer synthetic'})
    return asyncio.run(run())
def test_open_composes_one_preparation_and_selected_resolution_without_mutation():
    store,choices,access,people,config=Store(),Choices(),Access(),People(),Config();r=request(store,choices,access,people,config)
    assert r.status_code==200,r.text
    v=r.json();assert set(v)=={'context','draft','choices'}
    assert v['context']['active_draft']=={'draft_id':DRAFT,'revision':'7'} and v['draft']['input']['note']==' exact 😀 e\u0301 \n'
    assert v['choices']['selected']['choice']['type_id']==TYPE and not v['choices']['choices']
    assert access.calls==[ORG] and people.calls==[None,'2026-11-08'] and len(config.calls)==1 and len(store.calls)==1
    assert choices.calls==[(store.calls[0][0].authority,ORG,TYPE,None)]
    assert r.headers['cache-control']=='private, no-store'
@pytest.mark.parametrize('suffix',['?x=1','?selected_type_id='+TYPE,'?x=1&x=1'])
def test_open_rejects_all_queries_before_preparation(suffix):
    access=Access();assert request(access=access,suffix=suffix).status_code==422 and not access.calls
@pytest.mark.parametrize('closed',[False,True])
def test_discarded_has_context_and_no_choices_and_readonly_preserves_input(closed):
    s,c,a=Store(),Choices(),Access();s.closed=closed;a.manage=False;r=request(s,c,a);assert r.status_code==200
    if closed:assert set(r.json())=={'context','draft'} and not c.calls
    else:assert r.json()['draft']['editability']=={'status':'read_only','reason':'permission_missing'} and len(c.calls)==1
@pytest.mark.parametrize('reason',['work_timezone_missing','work_timezone_invalid'])
def test_open_missing_timezone_retains_input_and_choices(reason):
    config=Config();config.zone=None;config.notice=reason;people=People();r=request(config=config,people=people)
    assert r.status_code==200 and r.json()['draft']['setup_notices']==[{'code':reason}] and people.calls==[None]
def test_open_initial_failure_has_no_partial_editor_retry_same_read_target():
    s,c=Store(),Choices();c.error=Failure(503,'dependency_unavailable');r=request(s,c);assert r.status_code==503 and set(r.json())=={'error','error_id','details'}
    c.error=None;assert request(s,c).status_code==200 and [v[1] for v in s.calls]==[DRAFT,DRAFT]
def test_open_refuses_setup_denial_and_missing_ownership_without_choices():
    for mode in ['setup','denial','ownership']:
        a,p,s,c=Access(),People(),Store(),Choices()
        if mode=='setup':p.missing=True
        elif mode=='denial':a.error=(403,'access_denied')
        else:s.error=DraftFailure(404,'resource_not_found')
        r=request(s,c,a,p);assert r.status_code=={'setup':409,'denial':403,'ownership':404}[mode] and not c.calls
        assert 'input' not in r.text and 'employment_id' not in r.text
@pytest.mark.parametrize('kind',['cross_org','summary','editability','selected','extra','closed_choices','obsolete_offered'])
def test_schema_rejects_impossible_bindings(kind):
    from pydantic import TypeAdapter
    from drafts import EditorRead
    value=request().json()
    if kind=='cross_org':value['draft']['org_id']=str(uuid4())
    elif kind=='summary':value['context']['active_draft']['revision']='8'
    elif kind=='editability':value['draft']['editability']={'status':'read_only','reason':'permission_missing'}
    elif kind=='selected':value['choices']['selected']['choice']['type_id']=str(uuid4())
    elif kind=='extra':value['extra']=True
    elif kind=='obsolete_offered':value['choices']['choices']=[value['choices']['selected']['choice']];value['choices']['selected']={'status':'obsolete'}
    else:value['draft']={k:v for k,v in value['draft'].items() if k in ('org_id','draft_id','revision')};value['draft'].update(state='discarded',discarded_at=NOW.isoformat())
    with pytest.raises(ValueError):TypeAdapter(EditorRead).validate_python(value)
def test_previous_read_context_and_choices_routes_remain_in_schema():
    paths=create_app(environment={}).openapi()['paths']
    for path in ['/v1/organizations/{org_id}/drafts/{draft_id}','/v1/organizations/{org_id}/draft-choices','/v1/organizations/{org_id}/me/draft-context','/v1/organizations/{org_id}/drafts/{draft_id}/editor']:assert path in paths

def test_open_malformed_selected_snapshot_is_dependency_failure_without_input():
    class Contradictory(Choices):
        async def choices(self,*args):
            value=await super().choices(*args);value['choices']=[value['selected']['choice']];value['selected']={'status':'obsolete'};return value
    response=request(choices=Contradictory());assert response.status_code==503 and response.json()['error_id']=='dependency_unavailable' and set(response.json())=={'error_id','error','details'}
