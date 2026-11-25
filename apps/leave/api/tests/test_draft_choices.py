"""E1-AC03/04/05/07/13/15/16/17: offered metadata never authorizes a write."""
import asyncio,sys
from pathlib import Path
import pytest,httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import create_app
from draft_choices import decode_cursor,encode_cursor,resolve_rows
ORG='11111111-1111-4111-8111-111111111111'
TYPE='22222222-2222-4222-8222-222222222222'
VERSION='33333333-3333-4333-8333-333333333333'
def row():return dict(id=TYPE,org_id=ORG,archived_at=None,choice_version_id=VERSION,revision=1,version_id=VERSION,published_at='2020-01-01',name='Annual',permitted_modes=['full_days','half_day','hours'])
def test_scoped_cursor_closed_and_canonical():
 c=encode_cursor(ORG,TYPE);assert decode_cursor(c,ORG)==TYPE
 for value,org in [(c,'44444444-4444-4444-8444-444444444444'),(c+'=',ORG),('x',ORG)]:
  with pytest.raises(ValueError):decode_cursor(value,org)
def test_selected_outside_page_and_safe_obsolete():
 result=resolve_rows([],row(),ORG,TYPE);assert result.selected.status=='available';assert result.choices==[]
 assert resolve_rows([],None,ORG,TYPE).selected.status=='obsolete'
 assert resolve_rows([],None,ORG,None).selected.status=='not_requested'
def test_broken_published_metadata_is_unavailable():
 for changes in [{'published_at':None},{'permitted_modes':[]},{'permitted_modes':['full_days','full_days']},{'name':'bad\nname'},{'version_id':None}]:
  value=row();value.update(changes)
  with pytest.raises(ValueError):resolve_rows([value],value,ORG,TYPE)
class Access:
 def __init__(self):self.calls=[]
 async def own_read(self,authorization,org,budget):self.calls.append(org);return object()
class Catalogue:
 async def choices(self,context,org,selected,after,budget):return resolve_rows([],None,org,selected)
def test_http_current_own_read_no_manage_people_private_and_closed_query():
 async def run():
  access=Access();app=create_app(access=access,choices=Catalogue(),environment={})
  async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://leave') as client:
   path='/v1/organizations/'+ORG+'/draft-choices'
   response=await client.get(path+'?selected_type_id='+TYPE,headers={'Authorization':'Bearer private'})
   assert response.status_code==200;assert response.json()=={'choices':[],'next_cursor':None,'selected':{'status':'obsolete'}}
   assert response.headers['cache-control']=='private, no-store';assert access.calls==[ORG]
   for query in ['?unknown=x','?cursor=x','?selected_type_id=x','?selected_type_id='+TYPE+'&selected_type_id='+TYPE]:assert (await client.get(path+query,headers={'Authorization':'Bearer private'})).status_code==422
   assert (await client.get(path)).status_code==401
 asyncio.run(run())
def test_selected_discriminator_tags_are_required_in_openapi():
 schema=create_app(environment={}).openapi()['components']['schemas']
 for model in ('NotRequested','Obsolete','Available'):assert 'status' in schema[model].get('required',[])

def test_archived_and_unconfigured_selection_are_definitively_obsolete():
 for changes in ({'archived_at':'2026-11-08T00:00:00Z'},{'choice_version_id':None}):
  value=row();value.update(changes);assert resolve_rows([],value,ORG,TYPE).selected.status=='obsolete'
def test_actual_page_size_and_next_position_are_explicit():
 rows=[]
 for number in range(1,102):
  value=row();value['id']=f'00000000-0000-4000-8000-{number:012x}';rows.append(value)
 result=resolve_rows(rows,None,ORG,None);assert len(result.choices)==100;assert decode_cursor(result.next_cursor,ORG)==rows[99]['id']
 result=resolve_rows(rows[:100],None,ORG,None);assert result.next_cursor is None
@pytest.mark.parametrize('modes',[['full_days'],['half_day'],['hours'],['full_days','half_day'],['full_days','hours'],['half_day','hours'],['full_days','half_day','hours']])
def test_all_mode_subsets_are_offered_without_policy_date_selection(modes):
 value=row();value['permitted_modes']=modes
 assert resolve_rows([value],value,ORG,TYPE).selected.choice.permitted_modes==modes

def test_unicode_boundary_whitespace_follows_python_without_rejecting_format_characters():
 from draft_choices import name,configuration_name
 for value in ('\ufeffAnnual\ufeff','Annual\u200b'):
  assert name(value)==value;assert configuration_name(value)==value
 for whitespace in ('\u00a0','\u2003','\u0085'):
  assert configuration_name(whitespace+'Annual'+whitespace)=='Annual'
  with pytest.raises(ValueError):name(whitespace+'Annual')
