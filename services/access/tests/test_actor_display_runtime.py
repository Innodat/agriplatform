"""Active owner acceptance; synthetic native acquisition, no database authority claim."""
import asyncio
import importlib.util
from pathlib import Path
import sys
from uuid import UUID

import httpx
import pytest
from fastapi import FastAPI

OWNER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OWNER))
from actor_display_http import ACTIVE, PREVIOUS, ORG as ORG_SETTING
import actor_display_native as native
import actor_display_runtime as runtime

ORG = '33333333-3333-4333-8333-333333333333'
ACTOR = '44444444-4444-4444-8444-444444444444'
KEY = 'synthetic-actor-display-runtime-key-0001'
DATABASE = 'IDENTITY_ACTOR_DISPLAY_DATABASE_URL'
CONFIG = {ACTIVE: KEY, ORG_SETTING: ORG,
          DATABASE: 'host=127.0.0.1 port=5432 dbname=synthetic user=identity_actor_display_runtime password=private-synthetic'}
PATH = '/v2/identity/actor-displays'


def owner_module():
    spec = importlib.util.spec_from_file_location('actor_display_active_owner', OWNER / 'main.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def post(app, *, body=None, headers=None):
    async def execute():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='https://owner.synthetic') as client:
            return await client.post(PATH, json=body or {'org_id': ORG, 'actor_ids': [ACTOR]},
                                     headers=headers if headers is not None else {'X-Service-Key': KEY})
    return asyncio.run(execute())


def test_active_owner_mounts_reviewed_native_reader_without_construction_io(monkeypatch):
    configured, reads = [], []
    def connection(value):
        configured.append(value)
        return object()
    def reader(acquire):
        async def read(selected, deadline):
            reads.append((selected, deadline))
            return [{'actor_id': UUID(ACTOR), 'display_name': 'Retained actor'}]
        return read
    for key, value in CONFIG.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(native, 'PrivateConnection', connection)
    monkeypatch.setattr(native, 'NativeActorDisplayReader', reader)
    app = owner_module().create_app(db=object())
    assert not reads
    reply = post(app)
    assert reply.status_code == 200, reply.text
    assert reply.headers['cache-control'] == 'private, no-store'
    assert reply.json() == {'org_id': ORG, 'labels': [
        {'actor_id': ACTOR, 'status': 'resolved', 'display_name': 'Retained actor'}]}
    assert configured and all(value == CONFIG[DATABASE] for value in configured)
    assert reads[0][0] == (UUID(ACTOR),)


def configured_app(configuration):
    app = FastAPI()
    app.include_router(runtime.create_router(configuration))
    return app


def test_disabled_policy_is_private_closed_and_has_no_native_construction(monkeypatch):
    monkeypatch.setattr(native, 'PrivateConnection', lambda value: pytest.fail('native construction'))
    for headers in ({}, {'X-Service-Key': KEY}, {'Authorization': 'Bearer browser'}):
        reply = post(configured_app({}), headers=headers)
        assert reply.status_code == 403
        assert reply.json() == {'error_id': 'service_access_denied',
                                'error': 'Request could not be completed', 'details': {}}
        assert reply.headers['cache-control'] == 'private, no-store'


@pytest.mark.parametrize('configuration', [
    {ACTIVE: KEY}, {ORG_SETTING: ORG}, {DATABASE: CONFIG[DATABASE]}, {PREVIOUS: KEY},
    {key: value for key, value in CONFIG.items() if key != DATABASE},
    {**CONFIG, ACTIVE: ''}, {**CONFIG, ORG_SETTING: 'private-canary'},
    {**CONFIG, DATABASE: ''}, {**CONFIG, DATABASE: 'private-canary'},
    {**CONFIG, DATABASE: CONFIG[DATABASE].replace('identity_actor_display_runtime', 'postgres')},
    {**CONFIG, DATABASE: CONFIG[DATABASE].replace('host=127.0.0.1 ', '')},
    {**CONFIG, DATABASE: CONFIG[DATABASE].replace(' password=private-synthetic', '')},
    {**CONFIG, PREVIOUS: KEY}, {**CONFIG, 'KDG_SERVICE_KEY': KEY},
    {**CONFIG, PREVIOUS: 'synthetic-previous-display-key-0001',
     'OTHER_SERVICE_KEY': 'synthetic-previous-display-key-0001'},
])
def test_partial_invalid_privileged_and_duplicate_configuration_refuses_safely(configuration, caplog):
    with pytest.raises(RuntimeError) as caught:
        configured_app(configuration)
    assert str(caught.value) == 'actor_display_configuration_invalid'
    assert 'private-canary' not in caplog.text + repr(caught.value)
    assert 'private-synthetic' not in caplog.text + repr(caught.value)


def test_enabled_previous_rotation_and_denials_reuse_reviewed_owner(monkeypatch):
    reads = []
    def reader(acquire):
        async def read(selected, deadline):
            reads.append(selected)
            return [{'actor_id': UUID(ACTOR), 'display_name': 'Retained actor'}]
        return read
    monkeypatch.setattr(native, 'NativeActorDisplayReader', reader)
    previous = 'synthetic-previous-display-key-0001'
    app = configured_app({**CONFIG, PREVIOUS: previous})
    for key in (KEY, previous):
        assert post(app, headers={'X-Service-Key': key}).status_code == 200
    reads.clear()
    for headers in ({}, {'Authorization': 'Bearer browser'}, {'X-Service-Key': 'wrong'},
                    [('X-Service-Key', KEY), ('X-Service-Key', KEY)],
                    {'X-Service-Key': KEY, 'Authorization': ''}):
        reply = post(app, headers=headers)
        assert reply.status_code == 403
        assert reply.headers['cache-control'] == 'private, no-store'
    assert post(app, body={'org_id': ACTOR, 'actor_ids': [ACTOR]}).status_code == 403
    assert post(app, body={'org_id': ORG, 'actor_ids': [ACTOR], 'extra': True}).status_code == 422
    assert not reads
    # Ending the overlap removes previous-key authority without altering the route.
    assert post(configured_app(CONFIG), headers={'X-Service-Key': previous}).status_code == 403


def test_native_failure_stays_closed_and_private(monkeypatch, caplog):
    def reader(acquire):
        async def read(selected, deadline):
            raise RuntimeError('private-driver-canary')
        return read
    monkeypatch.setattr(native, 'NativeActorDisplayReader', reader)
    reply = post(configured_app(CONFIG))
    assert reply.status_code == 503
    assert reply.json() == {'error_id': 'identity.actor_display_unavailable',
                            'error': 'Request could not be completed', 'details': {}}
    assert reply.headers['cache-control'] == 'private, no-store'
    assert 'private-driver-canary' not in reply.text + caplog.text


def test_active_owner_cancellation_keeps_reader_cleanup_owned_and_private(monkeypatch):
    async def execute():
        started, release, closed = asyncio.Event(), asyncio.Event(), asyncio.Event()
        def reader(acquire):
            async def read(selected, deadline):
                try:
                    started.set()
                    await asyncio.Event().wait()
                finally:
                    await release.wait()
                    closed.set()
                    raise RuntimeError('private-active-reader-cleanup')
            return read
        monkeypatch.setattr(native, 'NativeActorDisplayReader', reader)
        app = owner_module().create_app(db=object(), actor_display_configuration=CONFIG)
        loop = asyncio.get_running_loop()
        diagnostics, previous = [], loop.get_exception_handler()
        loop.set_exception_handler(lambda loop, context: diagnostics.append(context))
        try:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='https://owner.synthetic') as client:
                task = asyncio.create_task(client.post(PATH, json={'org_id': ORG, 'actor_ids': [ACTOR]}, headers={'X-Service-Key': KEY}))
                await asyncio.wait_for(started.wait(), 1)
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


def test_explicit_disabled_policy_does_not_merge_ambient_configuration(monkeypatch):
    for key, value in CONFIG.items():
        monkeypatch.setenv(key, value)
    app = owner_module().create_app(db=object(), actor_display_configuration={})
    assert post(app).status_code == 403


@pytest.mark.parametrize('reuse_previous',[False,True])
@pytest.mark.parametrize('override_supplied_host_key',[False,True])
def test_explicit_display_policy_rejects_actual_host_credential_reuse(monkeypatch,reuse_previous,override_supplied_host_key):
    owner=owner_module()
    monkeypatch.setenv('KDG_SERVICE_KEY',KEY)
    monkeypatch.setenv('KDG_ORG_ID',ORG)
    # The current host route actually accepts this ambient service key, even if
    # the explicit display mapping supplies a different key under the same name.
    host=owner.create_app(db=object(),actor_display_configuration={})
    async def host_check():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=host),base_url='https://owner.synthetic') as client:
            return await client.post('/v2/check',headers={'X-Service-Key':KEY},json={})
    assert asyncio.run(host_check()).status_code==422  # Past service-key admission.
    configuration={**CONFIG}
    if reuse_previous:
        configuration.update({ACTIVE:'synthetic-distinct-active-display-key-0001',PREVIOUS:KEY})
    if override_supplied_host_key:
        configuration['KDG_SERVICE_KEY']='synthetic-explicit-key-that-host-does-not-use'
    with pytest.raises(RuntimeError,match='^actor_display_configuration_invalid$'):
        owner.create_app(db=object(),actor_display_configuration=configuration)


@pytest.mark.parametrize('enabled',[False,True])
def test_explicit_display_policy_ignores_ambient_display_settings(monkeypatch,enabled):
    owner=owner_module()
    for name in (*CONFIG,PREVIOUS):
        monkeypatch.setenv(name,'invalid-ambient-display-value')
    monkeypatch.setenv('KDG_SERVICE_KEY','synthetic-distinct-actual-host-service-key')
    monkeypatch.setenv('KDG_ORG_ID',ORG)
    def reader(acquire):
        async def read(selected,deadline):
            return [{'actor_id':UUID(ACTOR),'display_name':'Retained actor'}]
        return read
    monkeypatch.setattr(native,'NativeActorDisplayReader',reader)
    app=owner.create_app(db=object(),actor_display_configuration=CONFIG if enabled else {})
    assert post(app).status_code==(200 if enabled else 403)


def test_active_owner_schema_contains_same_display_contract_and_preserves_baseline_routes(monkeypatch):
    for key in CONFIG:
        monkeypatch.delenv(key, raising=False)
    schema = owner_module().create_app(db=object()).openapi()
    from actor_display_http import create_app
    async def no_read(selected, deadline):
        pytest.fail('schema read')
    isolated = create_app({}, no_read).openapi()
    assert schema['paths'][PATH] == isolated['paths'][PATH]
    for name, model in isolated['components']['schemas'].items():
        assert schema['components']['schemas'][name] == model
    for path in ('/health','/v1/check','/v2/check','/v2/organizations','/v2/applications'):
        assert path in schema['paths']
