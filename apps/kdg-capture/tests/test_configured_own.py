"""Configured own routes reuse existing owners; synthetic I/O, never native proof."""
import asyncio
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
from unittest.mock import patch

import httpx
import pytest

APP=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(APP/'api'),str(APP/'write-candidate'),str(APP/'write-tests')]
import test_provision_http as provision_fixture
import test_configured_admin as existing

CONFIG={**{key:value for key,value in existing.CONFIG.items() if key not in existing.SETTINGS},
 'KDG_OWN_DATABASE_URL':existing.CONFIG['KDG_ADMIN_READ_DATABASE_URL'],
 'KDG_QUESTIONNAIRE_ID':provision_fixture.support.QUESTIONNAIRE}
CAPTURE='/api/v1/captures/'+provision_fixture.support.CHILD
OWN_PATHS={'/api/v1/context','/api/v1/provision','/api/v1/captures',
 '/api/v1/captures/{capture_id}','/api/v1/captures/{capture_id}/edit-context',
 '/api/v1/operations/{operation_id}'}

def app_with(pool,access,configuration=None):
 # Each existing candidate has its own engine factory; ordinary SQLAlchemy remains
 # the sole engine constructor, patched before the configured factory is invoked.
 modules=['provision_http','create_http','edit_http','edit_context_http','recovery_http','read_http','history_http']
 from contextlib import ExitStack
 with ExitStack() as stack:
  for name in modules:
   module=__import__(name);stack.enter_context(patch.object(module,'create_engine',return_value=pool))
  return existing.runtime().create_app(configuration or CONFIG,transport=httpx.MockTransport(access))

def request(app,method,path,**kwargs):
 async def execute():
  async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='https://kdg.invalid') as client:
   return await client.request(method,path,**kwargs)
 kwargs.setdefault('headers',{'Authorization':'Bearer synthetic'})
 return asyncio.run(execute())

def test_configured_own_provision_uses_server_questionnaire_and_current_four_checks():
 pool=provision_fixture.Pool();calls=[]
 def access(incoming):
  import json
  assert not pool.connection.in_transaction() and pool.borrows==0
  permission=json.loads(incoming.content)['permission'];calls.append(permission)
  return httpx.Response(200,json=provision_fixture.support.support.support.evidence(permission))
 reply=request(app_with(pool,access),'GET','/api/v1/provision')
 assert reply.status_code==200,reply.text
 assert reply.json()['questionnaire']['questionnaire_id']==CONFIG['KDG_QUESTIONNAIRE_ID']
 assert reply.json()['children'][0]['child_id']==provision_fixture.support.CHILD
 assert calls==provision_fixture.support.PERMISSIONS
 assert (pool.borrows,pool.releases)==(1,1)
 assert reply.headers['cache-control']=='private, no-store'

@pytest.mark.parametrize('method,path',[
 ('GET','/api/v1/provision'),('POST','/api/v1/captures'),
 ('PUT',CAPTURE),('GET',CAPTURE+'/edit-context'),('GET',CAPTURE),
 ('GET','/api/v1/captures?from_date=2026-10-01&to_date=2026-10-28'),
 ('GET','/api/v1/operations/'+provision_fixture.support.ASSIGNMENT+'?command_type=capture.create')])
def test_every_configured_own_route_reaches_existing_bearer_boundary_before_io(method,path):
 pool=provision_fixture.Pool();app=app_with(pool,lambda incoming:pytest.fail('Access'))
 reply=request(app,method,path,headers={})
 assert reply.status_code==401,reply.text
 assert reply.headers['cache-control']=='private, no-store'
 assert pool.borrows==0

def test_schema_keeps_legitimate_methods_and_every_owner_component_reference():
 import own_runtime
 app=app_with(provision_fixture.Pool(),lambda incoming:pytest.fail('Access'))
 schema=app.openapi()
 assert set(schema['paths'])==OWN_PATHS
 assert set(schema['paths']['/api/v1/captures'])=={'get','post'}
 assert set(schema['paths']['/api/v1/captures/{capture_id}'])=={'get','put'}
 operations=[operation for path in schema['paths'].values() for operation in path.values()]
 assert len({operation['operationId'] for operation in operations})==8
 assert all(operation['security']==[{'HTTPBearer':[]}] for operation in operations)
 def references(value):
  if isinstance(value,dict):
   for child in value.values():yield from references(child)
  elif isinstance(value,list):
   for child in value:yield from references(child)
  elif isinstance(value,str) and value.startswith('#/components/'):
   _,_,category,name=value.split('/');assert name in schema['components'][category]
 list(references(schema))
 for prefix in ['OwnProvision','OwnCreate','OwnEdit','OwnEditContext','OwnRecovery','OwnRead','OwnHistory']:
  assert any(name.startswith(prefix) for name in schema['components']['schemas'])
 assert schema['paths']['/api/v1/captures']['post']['responses']['200']['content']['application/json']['schema']=={'$ref':'#/components/schemas/OwnCreateCaptureReceipt'}


def test_method_merge_refuses_duplicate_method_or_conflicting_path_metadata_without_mutation():
 from admin_runtime import compose_schema
 first={'info':{'title':'first'},'paths':{'/api/v1/items':{'get':{'operationId':'get_items'}}}}
 second={'info':{'title':'second'},'paths':{'/api/v1/items':{'post':{'operationId':'create_item'}}}}
 before=deepcopy([first,second]);merged=compose_schema(first,second)
 assert set(merged['paths']['/api/v1/items'])=={'get','post'}
 assert [first,second]==before
 with pytest.raises(RuntimeError,match='^kdg_admin_schema_invalid$'):compose_schema(first,first)
 first['paths']['/api/v1/items']['summary']='first'
 second['paths']['/api/v1/items']['summary']='second'
 with pytest.raises(RuntimeError,match='^kdg_admin_schema_invalid$'):compose_schema(first,second)


@pytest.mark.parametrize('configuration',[
 {key:value for key,value in CONFIG.items() if key!=missing}
 for missing in ('KDG_OWN_DATABASE_URL','KDG_QUESTIONNAIRE_ID')
]+[{**CONFIG,key:bad} for key,bad in [
 ('KDG_OWN_DATABASE_URL',''),('KDG_OWN_DATABASE_URL','private-own-dsn-canary'),
 ('KDG_OWN_DATABASE_URL',CONFIG['KDG_OWN_DATABASE_URL'].replace('kdg_capture_runtime:','postgres:')),
 ('KDG_OWN_DATABASE_URL',CONFIG['KDG_OWN_DATABASE_URL'].replace('127.0.0.1','remote.invalid')),
 ('KDG_QUESTIONNAIRE_ID',''),('KDG_QUESTIONNAIRE_ID','00000000-0000-0000-0000-000000000000'),
 ('KDG_QUESTIONNAIRE_ID','private-questionnaire-canary')]])
def test_partial_or_invalid_own_settings_refuse_safely_before_engine_construction(configuration,caplog):
 with patch('sqlalchemy.create_engine',side_effect=AssertionError('engine')) as factory:
  with pytest.raises(RuntimeError,match='^kdg_own_configuration_invalid$') as error:
   existing.runtime().create_app(configuration)
 assert factory.call_count==0
 assert 'canary' not in str(error.value)+caplog.text


def test_own_lifespans_keep_context_client_and_dispose_each_closure_engine_once():
 import own_runtime
 from contextlib import ExitStack
 pools=[provision_fixture.Pool() for _ in own_runtime.MODULES]
 with ExitStack() as stack:
  for module,pool in zip(own_runtime.handlers(),pools,strict=True):
   stack.enter_context(patch.object(module,'create_engine',return_value=pool))
  app=existing.runtime().create_app(CONFIG)
 assert all((pool.borrows,pool.disposed)==(0,0) for pool in pools)
 async def execute():
  async with app.router.lifespan_context(app):
   assert not app.state.access_client.is_closed
   assert all(pool.disposed==0 for pool in pools)
  assert app.state.access_client.is_closed
 asyncio.run(execute())
 assert all((pool.borrows,pool.disposed)==(0,1) for pool in pools)


def test_combined_own_and_admin_routes_keep_all_read_and_own_permission_boundaries():
 from contextlib import ExitStack
 import own_runtime,admin_runtime
 pool=provision_fixture.Pool();calls=[]
 def access(incoming):
  import json
  calls.append(json.loads(incoming.content)['permission'])
  return httpx.Response(403,json={'detail':{'code':'access_denied'}})
 with ExitStack() as stack:
  for module in (*own_runtime.handlers(),*admin_runtime.handlers()):
   stack.enter_context(patch.object(module if hasattr(module,'create_engine') else module.source,'create_engine',return_value=pool))
  app=existing.runtime().create_app({**existing.CONFIG,**CONFIG},transport=httpx.MockTransport(access))
 assert set(app.openapi()['paths'])==OWN_PATHS|{'/api/v1/admin/captures','/api/v1/admin/captures/{capture_id}','/api/v1/admin/captures/{capture_id}/audit-details'}
 for path in ['/api/v1/provision','/api/v1/admin/captures?from_date=2026-10-01&to_date=2026-10-28']:
  reply=request(app,'GET',path);assert reply.status_code==403
 assert calls==['kdg_capture.capture.read.own','kdg_capture.capture.read.all']
 assert pool.borrows==0


def test_configured_get_and_post_collection_keep_distinct_existing_engine_closures():
 import own_runtime,json
 import test_create_http as create_fixture
 import test_history_http as history_fixture
 from contextlib import ExitStack
 pools={name:provision_fixture.Pool() for name in own_runtime.MODULES}
 pools['create']=create_fixture.Pool();pools['history']=history_fixture.Pool()
 def access(incoming):
  permission=json.loads(incoming.content)['permission']
  return httpx.Response(200,json=create_fixture.support.evidence(permission))
 with ExitStack() as stack:
  for name,module in zip(own_runtime.MODULES,own_runtime.handlers(),strict=True):
   stack.enter_context(patch.object(module,'create_engine',return_value=pools[name]))
  app=existing.runtime().create_app(CONFIG,transport=httpx.MockTransport(access))
 created=request(app,'POST','/api/v1/captures',json=create_fixture.support.support.command().model_dump())
 assert created.status_code==200,created.text
 page=request(app,'GET',history_fixture.URL)
 assert page.status_code==200,page.text
 assert page.json()['items'] and page.json()['observation']['permission']=='kdg_capture.capture.read.own'
 assert pools['create'].borrows==pools['history'].borrows==1
 assert all(pool.borrows==0 for name,pool in pools.items() if name not in ('create','history'))


@pytest.mark.parametrize('method,path,kwargs',[
 ('GET','/api/v1/provision?org_id=private',{}),
 ('GET',CAPTURE+'?account_id=private',{}),
 ('GET',CAPTURE+'/edit-context?x=1',{}),
 ('GET','/api/v1/captures?from_date=invalid&to_date=2026-10-28',{}),
 ('POST','/api/v1/captures',{'content':b'{}'}),
 ('PUT',CAPTURE,{'content':b'{}'}),
 ('GET','/api/v1/operations/'+provision_fixture.support.ASSIGNMENT+'?command_type=capture.create&org_id=x',{})])
def test_malformed_own_requests_stay_in_existing_closed_boundaries(method,path,kwargs):
 pool=provision_fixture.Pool();app=app_with(pool,lambda incoming:pytest.fail('Access'))
 reply=request(app,method,path,**kwargs)
 assert reply.status_code==422 and pool.borrows==0
 assert reply.headers['cache-control']=='private, no-store'


def test_own_route_slashes_and_admin_writes_are_not_exposed():
 pool=provision_fixture.Pool();app=app_with(pool,lambda incoming:pytest.fail('Access'))
 for method,path,status in [('GET','/api/v1/provision/',404),('DELETE',CAPTURE,405),
 ('PUT','/api/v1/admin/captures/'+provision_fixture.support.CHILD,404)]:
  reply=request(app,method,path);assert reply.status_code==status
  assert reply.headers['cache-control']=='private, no-store'
 assert pool.borrows==0

def test_offline_exports_match_explicit_own_and_combined_runtime_without_engine_io():
 import export_configured_own_openapi as exporter
 from contextlib import ExitStack
 import own_runtime,admin_runtime
 pool=provision_fixture.Pool()
 own=app_with(pool,lambda incoming:pytest.fail('Access'))
 assert own.openapi()==exporter.schema()
 with ExitStack() as stack:
  for module in (*own_runtime.handlers(),*admin_runtime.handlers()):
   stack.enter_context(patch.object(module if hasattr(module,'create_engine') else module.source,'create_engine',return_value=pool))
  combined=existing.runtime().create_app({**existing.CONFIG,**CONFIG})
 assert combined.openapi()==exporter.schema(include_administrator=True)
 assert pool.borrows==0


def test_owner_component_qualification_preserves_each_isolated_schema_and_discriminator():
 import own_runtime
 owners=own_runtime.applications([None]*7,[None]*7,None,None)
 originals=[owner.openapi() for owner in owners];before=deepcopy(originals)
 qualified=own_runtime.schemas(owners)
 assert [owner.openapi() for owner in owners]==before
 for name,original,converted in zip(own_runtime.MODULES,originals,qualified,strict=True):
  prefix='Own'+''.join(part.title() for part in name.split('_'))
  expected={key:prefix+key for key in original['components']['schemas']}
  assert set(converted['components']['schemas'])==set(expected.values())
  # Restore refs and component names to prove definitions and operations were not
  # silently normalized when owners use the same name for different declarations.
  raw=__import__('json').dumps(converted)
  for key,value in expected.items():raw=raw.replace('#/components/schemas/'+value+'"','#/components/schemas/'+key+'"')
  restored=__import__('json').loads(raw)
  restored['components']['schemas']={key:restored['components']['schemas'][value] for key,value in expected.items()}
  assert restored==original


def test_real_api_only_import_composes_without_connecting_or_startup_migrations():
 import subprocess,json
 program='''
import json,sys,asyncio
from unittest.mock import patch
sys.path.insert(0,sys.argv[1])
from sqlalchemy.engine import Engine
from runtime import create_app
with patch.object(Engine,'connect',side_effect=AssertionError('checkout')):
    app=create_app(json.loads(sys.argv[2]))
    assert set(app.openapi()['paths'])==set(json.loads(sys.argv[3]))
    assert 'alembic' not in sys.modules
    async def lifecycle():
        async with app.router.lifespan_context(app):
            assert not app.state.access_client.is_closed
        assert app.state.access_client.is_closed
    asyncio.run(lifecycle())
print('own_factory_no_io')
'''
 result=subprocess.run([sys.executable,'-I','-B','-c',program,str(APP/'api'),json.dumps(CONFIG),json.dumps(sorted(OWN_PATHS))],
  env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},capture_output=True,text=True,timeout=10)
 assert result.returncode==0,result.stderr
 assert result.stdout.strip()=='own_factory_no_io'


def test_absent_own_settings_keep_explicit_context_configuration_despite_ambient_values():
 import os
 selected={key:value for key,value in CONFIG.items() if key not in ('KDG_OWN_DATABASE_URL','KDG_QUESTIONNAIRE_ID')}
 with patch.dict(os.environ,{'KDG_OWN_DATABASE_URL':'private-ambient','KDG_QUESTIONNAIRE_ID':'private-ambient'}):
  app=existing.runtime().create_app(selected)
 assert set(app.openapi()['paths'])=={'/api/v1/context'}
