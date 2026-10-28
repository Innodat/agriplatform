"""Configured active administrator HTTP: synthetic owners/storage, no native claim."""
import asyncio
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
from unittest.mock import patch

import httpx
import pytest

APP = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(APP / 'api'), str(APP / 'write-candidate'), str(APP / 'write-tests')]
import test_audit_http as fixtures

ORG = fixtures.wire.support.ORG
KEY = 'synthetic-active-actor-display-key-0001'
CONFIG = {'KDG_ORG_ID': ORG, 'KDG_ACCESS_URL': 'https://access.invalid',
          'KDG_SERVICE_KEY': 'synthetic-access-key',
          'KDG_ADMIN_READ_DATABASE_URL': 'postgresql+psycopg://kdg_capture_runtime:synthetic@127.0.0.1:55482/synthetic',
          'KDG_IDENTITY_URL': 'https://identity.invalid', 'KDG_ACTOR_DISPLAY_SERVICE_KEY': KEY}
DETAIL = fixtures.wire.DETAIL
AUDIT = DETAIL + '/audit-details'
SETTINGS = ('KDG_ADMIN_READ_DATABASE_URL', 'KDG_IDENTITY_URL', 'KDG_ACTOR_DISPLAY_SERVICE_KEY')


def runtime():
    owner_spec = importlib.util.spec_from_file_location('kdg_admin_context_owner', APP / 'api/main.py')
    owner = importlib.util.module_from_spec(owner_spec)
    owner_spec.loader.exec_module(owner)
    spec = importlib.util.spec_from_file_location('kdg_configured_admin', APP / 'api/runtime.py')
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {'main': owner}):
        spec.loader.exec_module(module)
    return module


def test_active_factory_composes_current_admin_detail_and_history():
    pool, calls = fixtures.Pool(), []
    def access(request):
        calls.append(request)
        return httpx.Response(200, json=fixtures.wire.evidence())
    with patch('sqlalchemy.create_engine', return_value=pool), patch.object(fixtures.wire.boundary, 'create_engine', return_value=pool):
        app = runtime().create_app(CONFIG, transport=httpx.MockTransport(access))
    async def execute():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='https://kdg.invalid') as client:
            return [await client.get(path, headers={'Authorization': 'Bearer synthetic'})
                    for path in (DETAIL, fixtures.wire.HISTORY)]
    for reply in asyncio.run(execute()):
        assert reply.status_code == 200, reply.text
        assert reply.headers['cache-control'] == 'private, no-store'
    assert len(calls) == 2
    assert all(json.loads(call.content)['permission'] == 'kdg_capture.capture.read.all' for call in calls)


def active_app(pool, access, identity=None, configuration=None):
    with patch.object(fixtures.wire.boundary, 'create_engine', return_value=pool), \
         patch.object(fixtures.boundary, 'create_engine', return_value=pool):
        return runtime().create_app(configuration or CONFIG, transport=httpx.MockTransport(access),
            identity_transport=httpx.MockTransport(identity) if identity else None)


def request(app, path=AUDIT, **kwargs):
    async def execute():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='https://kdg.invalid') as client:
            return await client.get(path, **kwargs)
    kwargs.setdefault('headers', {'Authorization': 'Bearer synthetic'})
    return asyncio.run(execute())


def test_active_audit_details_uses_exact_authorized_selection_after_release_and_rechecks():
    pool, access_calls, identity_calls = fixtures.Pool(), [], []
    def access(incoming):
        assert not pool.connection.in_transaction()
        access_calls.append(incoming)
        return httpx.Response(200, json=fixtures.wire.evidence())
    def identity(incoming):
        assert (pool.borrows, pool.releases) == (1, 1)
        assert not pool.connection.in_transaction()
        identity_calls.append(incoming)
        assert incoming.headers['x-service-key'] == KEY
        assert 'authorization' not in incoming.headers
        assert str(incoming.url) == 'https://identity.invalid/v2/identity/actor-displays'
        body = json.loads(incoming.content)
        # Expected independently from the synthetic fixture's exact original actors.
        expected = sorted({fixtures.wire.support.ACTOR, fixtures.wire.FOREIGN})
        assert body == {'org_id': ORG, 'actor_ids': expected}
        return httpx.Response(200, json={'org_id': ORG, 'labels': [
            {'actor_id': value, 'status': 'resolved', 'display_name': 'Retained name'} for value in expected]},
            headers={'Cache-Control': 'private, no-store'})
    reply = request(active_app(pool, access, identity))
    assert reply.status_code == 200, reply.text
    assert reply.headers['cache-control'] == 'private, no-store'
    body = reply.json()
    assert body['audit']['owner_account_id'] == fixtures.wire.FOREIGN
    assert [event['revision'] for event in body['audit']['events']] == ['5', '4', '3', '2', '1']
    assert body['audit']['events'][-1]['initiator_actor_id'] is None
    assert body['actor_display']['status'] == 'loaded'
    assert (len(access_calls), len(identity_calls)) == (2, 1)
    assert all(json.loads(call.content)['permission'] == 'kdg_capture.capture.read.all' for call in access_calls)


@pytest.mark.parametrize('path', [DETAIL, fixtures.wire.HISTORY, AUDIT])
def test_denied_current_all_read_never_checks_out_or_falls_back(path):
    pool, calls = fixtures.Pool(), []
    def denied(incoming):
        calls.append(incoming)
        return httpx.Response(403, json={'detail': {'code': 'access_denied'}})
    app = active_app(pool, denied, lambda incoming: pytest.fail('Identity lookup'))
    reply = request(app, path)
    assert (reply.status_code, reply.json()['error_id']) == (403, 'access_denied')
    assert reply.headers['cache-control'] == 'private, no-store'
    assert pool.borrows == 0 and len(calls) == 1
    assert json.loads(calls[0].content)['permission'] == 'kdg_capture.capture.read.all'


@pytest.mark.parametrize('path', [DETAIL + '?org_id=' + ORG, AUDIT + '?actor_ids=x',
                                      AUDIT + '?limit=1&limit=2', AUDIT + '?cursor=bad'])
def test_malformed_selectors_never_call_authority_or_storage(path):
    pool = fixtures.Pool()
    app = active_app(pool, lambda incoming: pytest.fail('Access'), lambda incoming: pytest.fail('Identity'))
    reply = request(app, path)
    assert reply.status_code == 422 and pool.borrows == 0
    assert reply.headers['cache-control'] == 'private, no-store'


def test_changed_or_lost_final_authority_never_publishes_audit():
    for final in (httpx.Response(403, json={'detail': {'code': 'access_denied'}}),
                  httpx.Response(200, json={**fixtures.wire.evidence(), 'membership_id': '98'})):
        pool, calls = fixtures.Pool(), []
        def access(incoming):
            calls.append(incoming)
            return httpx.Response(200, json=fixtures.wire.evidence()) if len(calls) == 1 else final
        def identity(incoming):
            return httpx.Response(503, json={}, headers={'Cache-Control': 'private, no-store'})
        reply = request(active_app(pool, access, identity))
        assert reply.status_code in (403, 503)
        assert reply.json()['error_id'] in ('access_denied', 'authorization_observation_expired')
        assert 'audit' not in reply.json() and len(calls) == 2
        assert reply.headers['cache-control'] == 'private, no-store'


def test_active_aggregate_cancellation_keeps_transport_unwind_owned_and_private():
    async def execute():
        pool = fixtures.Pool()
        started, release, closed = asyncio.Event(), asyncio.Event(), asyncio.Event()
        async def identity(incoming):
            try:
                started.set()
                await asyncio.Event().wait()
            finally:
                await release.wait()
                closed.set()
                raise RuntimeError('private-active-display-cleanup')
        app = active_app(pool, lambda incoming: httpx.Response(200, json=fixtures.wire.evidence()), identity)
        loop = asyncio.get_running_loop()
        diagnostics, previous = [], loop.get_exception_handler()
        loop.set_exception_handler(lambda loop, context: diagnostics.append(context))
        try:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='https://kdg.invalid') as client:
                task = asyncio.create_task(client.get(AUDIT, headers={'Authorization': 'Bearer synthetic'}))
                await asyncio.wait_for(started.wait(), 2)
                task.cancel()
                await asyncio.sleep(.01)
                assert not task.done()
                release.set()
                with pytest.raises(asyncio.CancelledError):
                    await asyncio.wait_for(task, 1)
                await asyncio.sleep(0)
                assert closed.is_set() and not diagnostics
        finally:
            release.set()
            loop.set_exception_handler(previous)
    asyncio.run(execute())


@pytest.mark.parametrize('configuration', [
    {**CONFIG, key: ''} for key in SETTINGS
] + [{key: value for key, value in CONFIG.items() if key != missing} for missing in SETTINGS] + [
    {**CONFIG, 'KDG_ADMIN_READ_DATABASE_URL': CONFIG['KDG_ADMIN_READ_DATABASE_URL'].replace('kdg_capture_runtime:', 'postgres:')},
    {**CONFIG, 'KDG_ADMIN_READ_DATABASE_URL': 'private-dsn-canary'},
    {**CONFIG, 'KDG_IDENTITY_URL': 'http://identity.invalid'},
    {**CONFIG, 'KDG_IDENTITY_URL': 'https://private:user@identity.invalid'},
    {**CONFIG, 'KDG_ACTOR_DISPLAY_SERVICE_KEY': CONFIG['KDG_SERVICE_KEY']},
    {**CONFIG, 'OTHER_SERVICE_KEY': KEY},
])
def test_partial_unsafe_and_duplicate_policy_refuses_without_io(configuration, caplog):
    with patch.object(fixtures.wire.boundary, 'create_engine', side_effect=AssertionError('engine')) as admin_engine, \
         patch.object(fixtures.boundary, 'create_engine', side_effect=AssertionError('engine')) as audit_engine:
        with pytest.raises(RuntimeError) as caught:
            runtime().create_app(configuration)
    admin_engine.assert_not_called()
    audit_engine.assert_not_called()
    assert str(caught.value) == 'kdg_admin_configuration_invalid'
    assert 'private-dsn-canary' not in str(caught.value) + caplog.text


def test_composed_lifespan_keeps_context_client_and_disposes_both_candidate_engines():
    pool = fixtures.Pool()
    app = active_app(pool, lambda incoming: httpx.Response(403, json={'detail': {'code': 'access_denied'}}))
    assert (pool.borrows, pool.disposed) == (0, 0)
    async def execute():
        async with app.router.lifespan_context(app):
            assert not app.state.access_client.is_closed
            assert pool.disposed == 0
        assert app.state.access_client.is_closed
    asyncio.run(execute())
    assert pool.disposed == 2


def test_active_schema_composes_owner_models_security_errors_and_no_write_routes():
    pool = fixtures.Pool()
    app = active_app(pool, lambda incoming: pytest.fail('Access'))
    schema = app.openapi()
    assert set(schema['paths']) == {'/api/v1/context', '/api/v1/admin/captures',
        '/api/v1/admin/captures/{capture_id}', '/api/v1/admin/captures/{capture_id}/audit-details'}
    assert all(set(operation) == {'get'} for operation in schema['paths'].values())
    for path in schema['paths']:
        assert schema['paths'][path]['get']['security'] == [{'HTTPBearer': []}]
    operation = schema['paths']['/api/v1/admin/captures/{capture_id}/audit-details']['get']
    assert 'no active mount' not in operation['description']
    assert operation['responses']['403']['content']['application/json']['schema'] == {
        '$ref': '#/components/schemas/AuditDisplayError403'}
    assert schema['components']['schemas']['AuditDetails']['additionalProperties'] is False
    assert schema['components']['schemas']['CaptureDetail']['properties']['definition']['$ref'].endswith('/QuestionnaireDefinition')
    exporter_spec = importlib.util.spec_from_file_location('kdg_active_admin_export', APP / 'api/export_configured_admin_openapi.py')
    exporter = importlib.util.module_from_spec(exporter_spec)
    exporter_spec.loader.exec_module(exporter)
    # Export in its ordinary API-only import environment, independently of the
    # Access owner's generic main module if present in the shared test process.
    owner_spec = importlib.util.spec_from_file_location('kdg_export_context', APP / 'api/main.py')
    owner = importlib.util.module_from_spec(owner_spec)
    owner_spec.loader.exec_module(owner)
    with patch.dict(sys.modules, {'main': owner}):
        assert exporter.schema() == schema


def owner_schemas():
    import admin_runtime
    admin,audit=admin_runtime.handlers()
    return admin_runtime,[runtime().context_app().openapi(),
        admin._create_app(None,None,None).openapi(),
        audit._create_app(None,None,None,None).openapi()]


@pytest.mark.parametrize('category,definition',[
    ('schemas',{'type':'object','properties':{'value':{'type':'string'}}}),
    ('securitySchemes',{'type':'http','scheme':'bearer'}),
])
def test_schema_composition_accepts_identical_shared_definitions_without_mutation(category,definition):
    owner,schemas=owner_schemas()
    for schema in schemas:
        schema.setdefault('components',{}).setdefault(category,{})['SharedDefinition']=deepcopy(definition)
    before=deepcopy(schemas)
    combined=owner.compose_schema(*schemas)
    assert combined['components'][category]['SharedDefinition']==definition
    combined['components'][category]['SharedDefinition']['description']='combined only'
    assert schemas==before


@pytest.mark.parametrize('category,definition',[
    ('schemas',{'type':'string'}),
    ('securitySchemes',{'type':'http','scheme':'bearer'}),
])
def test_schema_composition_refuses_conflicting_shared_components(category,definition):
    owner,schemas=owner_schemas()
    schemas[0].setdefault('components',{}).setdefault(category,{})['SharedDefinition']=definition
    schemas[1].setdefault('components',{}).setdefault(category,{})['SharedDefinition']={**definition,'description':'conflict'}
    with pytest.raises(RuntimeError,match='^kdg_admin_schema_invalid$'):
        owner.compose_schema(*schemas)


@pytest.mark.parametrize('source,target',[(0,1),(1,2)])
def test_schema_composition_refuses_duplicate_owner_paths(source,target):
    owner,schemas=owner_schemas()
    path=next(iter(schemas[source]['paths']))
    schemas[target]['paths'][path]=deepcopy(schemas[source]['paths'][path])
    with pytest.raises(RuntimeError,match='^kdg_admin_schema_invalid$'):
        owner.compose_schema(*schemas)


def test_active_factory_refuses_conflicting_owner_schema():
    import admin_runtime
    admin,_=admin_runtime.handlers()
    original=admin._create_app
    def conflicting(*args,**kwargs):
        app=original(*args,**kwargs)
        schema=app.openapi()
        schema['components']['schemas']['Context']={'type':'string','description':'private-schema-canary'}
        app.openapi=lambda:schema
        return app
    pool=fixtures.Pool()
    with patch.object(admin,'_create_app',side_effect=conflicting):
        with pytest.raises(RuntimeError,match='^kdg_admin_configuration_invalid$') as error:
            active_app(pool,lambda incoming:pytest.fail('Access I/O'))
    assert pool.borrows==0
    assert 'private-schema-canary' not in str(error.value)


def test_context_only_compatibility_has_no_admin_engine_or_routes():
    configuration = {key: value for key, value in CONFIG.items() if key not in SETTINGS}
    with patch.object(fixtures.wire.boundary, 'create_engine', side_effect=AssertionError('engine')):
        app = runtime().create_app(configuration)
    assert set(app.openapi()['paths']) == {'/api/v1/context'}
    reply = request(app, DETAIL)
    assert reply.status_code == 404 and reply.headers['cache-control'] == 'private, no-store'


@pytest.mark.parametrize('enabled', [False, True])
def test_real_factory_import_from_api_only_path_has_no_database_io(enabled):
    selected = CONFIG if enabled else {key: value for key, value in CONFIG.items() if key not in SETTINGS}
    # New process has no test-only candidate paths or preloaded schema modules.
    # It exercises the real Uvicorn import layout without starting a socket.
    program = '''
import json,sys
from unittest.mock import patch
sys.path.insert(0,sys.argv[1])
from runtime import create_app
policy=json.loads(sys.argv[2])
enabled=json.loads(sys.argv[3])
if enabled:
    from sqlalchemy.engine import Engine
    with patch.object(Engine,'connect',side_effect=AssertionError('checkout')):
        app=create_app(policy)
else:
    app=create_app(policy)
    assert 'sqlalchemy' not in sys.modules and 'psycopg' not in sys.modules
assert len(app.openapi()['paths'])==(4 if enabled else 1)
print('factory_import_safe')
'''
    result = subprocess.run([sys.executable, '-I', '-B', '-c', program,
                             str(APP / 'api'), json.dumps(selected), json.dumps(enabled)],
                            env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'},
                            capture_output=True, text=True, timeout=8)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'factory_import_safe'
