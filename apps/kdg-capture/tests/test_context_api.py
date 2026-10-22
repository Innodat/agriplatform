"""Synthetic HTTP acceptance for KDG's current-context consumer."""
import importlib.util
import sys
from pathlib import Path
from datetime import datetime, timezone

import httpx
import pytest
from fastapi.testclient import TestClient

API = Path(__file__).resolve().parents[1] / 'api'
sys.path.insert(0, str(API))
spec = importlib.util.spec_from_file_location('kdg_context_main', API / 'main.py')
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

ACCOUNT = '11111111-1111-4111-8111-111111111111'
ACTOR = '22222222-2222-4222-8222-222222222222'
ORG = '33333333-3333-4333-8333-333333333333'
DECISION = '44444444-4444-4444-8444-444444444444'
PERMISSION = 'kdg_capture.capture.read.own'
HEADERS = {'Authorization': 'Bearer synthetic-user'}


def decision():
    return dict(account_id=ACCOUNT, actor_id=ACTOR, membership_id='9007199254740993',
                authorization_scope={'kind': 'organization', 'org_id': ORG},
                resource_scope={'kind': 'own_account', 'account_id': ACCOUNT},
                permission=PERMISSION, decision_id=DECISION,
                checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))


@pytest.fixture
def boundary():
    calls = []
    state = {'status': 200, 'body': decision()}

    def respond(request):
        calls.append(request)
        if 'exception' in state:
            raise state['exception']
        return httpx.Response(state['status'], json=state['body'])

    app = main.create_app(org_id=ORG, access_url='https://access.synthetic',
                          service_key='synthetic-service-key', transport=httpx.MockTransport(respond))
    with TestClient(app) as client:
        yield client, state, calls


def test_authorized_context_is_current_and_exact(boundary):
    client, state, calls = boundary
    first = client.get('/api/v1/context', headers=HEADERS)
    assert first.status_code == 200, first.text
    assert first.json() == state['body']
    assert first.headers['cache-control'] == 'private, no-store'
    assert len(calls) == 1
    assert calls[0].url == 'https://access.synthetic/v2/check'
    assert calls[0].headers['authorization'] == HEADERS['Authorization']
    assert calls[0].headers['x-service-key'] == 'synthetic-service-key'
    import json
    assert json.loads(calls[0].content) == {
        'permission': PERMISSION, 'authorization_scope': {'kind': 'organization', 'org_id': ORG}}
    state.update(status=403, body={'detail': {'code': 'access_denied'}})
    denied = client.get('/api/v1/context', headers=HEADERS)
    assert denied.status_code == 403 and denied.json()['error_id'] == 'access_denied'
    assert len(calls) == 2  # A prior success does not cache authority.


@pytest.mark.parametrize('headers', [{}, {'Authorization': 'Basic synthetic'}, {'Authorization': 'Bearer '},
                                      {'Authorization': 'Bearer a b'}])
def test_missing_or_malformed_bearer_never_calls_access(boundary, headers):
    client, _, calls = boundary
    response = client.get('/api/v1/context', headers=headers)
    assert response.status_code == 401
    assert response.json()['error_id'] == 'authentication_required'
    assert response.headers['cache-control'] == 'private, no-store'
    assert not calls


@pytest.mark.parametrize('url,body', [('/api/v1/context?org_id='+ACCOUNT, b''),
                                     ('/api/v1/context?account_id='+ACCOUNT, b''),
                                     ('/api/v1/context?unknown=', b''),
                                     ('/api/v1/context', b'{}')])
def test_selector_free_route_refuses_before_access(boundary, url, body):
    client, _, calls = boundary
    response = client.request('GET', url, content=body, headers=HEADERS)
    assert response.status_code == 422 and response.json()['error_id'] == 'validation_failed'
    assert not calls


@pytest.mark.parametrize('status,code,expected,identifier', [
    (401, 'authentication_required', 401, 'authentication_required'),
    (403, 'access_denied', 403, 'access_denied'),
    (403, 'service_access_denied', 503, 'authorization_unavailable'),
    (409, 'identity.actor_setup_required', 409, 'identity.actor_setup_required'),
    (503, 'authorization_unavailable', 503, 'authorization_unavailable'),
    (500, 'sensitive-internal-canary', 503, 'authorization_unavailable'),
    (302, 'access_denied', 503, 'authorization_unavailable'),
])
def test_error_adaptation_is_closed_and_safe(boundary, status, code, expected, identifier, caplog):
    client, state, _ = boundary
    state.update(status=status, body={'detail': {'code': code, 'payload': 'sensitive-internal-canary'}})
    response = client.get('/api/v1/context', headers=HEADERS)
    assert (response.status_code, response.json()['error_id']) == (expected, identifier)
    assert response.headers['cache-control'] == 'private, no-store'
    assert 'sensitive-internal-canary' not in response.text + caplog.text
    assert 'synthetic-user' not in response.text + caplog.text
    assert 'synthetic-service-key' not in response.text + caplog.text


@pytest.mark.parametrize('field,value', [
    ('account_id', '00000000-0000-0000-0000-000000000000'),
    ('actor_id', ACCOUNT.upper().replace('11111111', 'AAAAAAAA')),
    ('actor_id', '00000000-0000-0000-0000-000000000000'),
    ('actor_id', None), ('decision_id', 'not-a-uuid'),
    ('permission', 'kdg_capture.capture.read.all'),
    ('membership_id', 1), ('membership_id', '0'), ('membership_id', '01'),
    ('membership_id', '9223372036854775808'), ('membership_id', '1\n'),
    ('authorization_scope', {'kind': 'organization', 'org_id': ACCOUNT}),
    ('resource_scope', {'kind': 'own_account', 'account_id': ACTOR}),
    ('resource_scope', {'kind': 'organization', 'org_id': ORG}),
    ('checked_at', '2026-01-01T00:00:00Z'), ('checked_at', '2099-01-01T00:00:00Z'),
    ('checked_at', '2026-10-22T12:00:00'), ('unexpected', 'sensitive-internal-canary'),
])
def test_malformed_or_mismatched_authority_fails_closed(boundary, field, value):
    client, state, _ = boundary
    state['body'][field] = value
    response = client.get('/api/v1/context', headers=HEADERS)
    assert response.status_code == 503 and response.json()['error_id'] == 'authorization_unavailable'
    assert 'sensitive-internal-canary' not in response.text


def test_transport_failure_is_safe(boundary, caplog):
    client, state, _ = boundary
    state['exception'] = httpx.ReadTimeout('sensitive-internal-canary')
    response = client.get('/api/v1/context', headers=HEADERS)
    assert response.status_code == 503 and response.json()['error_id'] == 'authorization_unavailable'
    assert 'sensitive-internal-canary' not in response.text + caplog.text


def test_unconfigured_app_refuses_without_network():
    with TestClient(main.create_app()) as client:
        response = client.get('/api/v1/context', headers=HEADERS)
    assert response.status_code == 503 and response.json()['error_id'] == 'authorization_unavailable'


def test_nullable_scope_metadata_and_transport_body_are_rejected(boundary):
    client, state, _ = boundary
    state['body']['authorization_scope']['extra'] = True
    response = client.get('/api/v1/context', headers=HEADERS)
    assert response.status_code == 503


@pytest.mark.parametrize('change', [
    {'org_id': '00000000-0000-0000-0000-000000000000'},
    {'access_url': 'https://user:password@access.synthetic'},
    {'access_url': 'https://access.synthetic?secret=value'},
    {'access_url': 'http://access.synthetic'},
    {'service_key': ''}, {'service_key': 'key\n'}, {'org_id': None},
])
def test_invalid_configuration_is_safe(change):
    config = dict(org_id=ORG, access_url='https://access.synthetic', service_key='synthetic-service-key')
    config.update(change)
    with pytest.raises(RuntimeError, match='^kdg_context_configuration_invalid$'):
        main.create_app(**config)


def test_slow_access_has_one_bounded_total_wait(monkeypatch):
    import asyncio
    import time
    monkeypatch.setattr(main, 'ACCESS_SECONDS', 0.03)

    async def slow(request):
        await asyncio.sleep(1)
        return httpx.Response(200, json=decision())

    app = main.create_app(org_id=ORG, access_url='https://access.synthetic',
                          service_key='synthetic-service-key', transport=httpx.MockTransport(slow))
    with TestClient(app) as client:
        start = time.monotonic()
        response = client.get('/api/v1/context', headers=HEADERS)
        elapsed = time.monotonic() - start
    assert response.status_code == 503 and response.json()['error_id'] == 'authorization_unavailable'
    assert 0.02 <= elapsed < 0.5


def test_context_identifiers_publish_uuid_schema():
    schema = main.create_app().openapi()
    definitions = schema['components']['schemas']
    assert definitions['Context']['properties']['account_id']['format'] == 'uuid'
    assert definitions['OrganizationScope']['properties']['org_id']['format'] == 'uuid'


@pytest.mark.parametrize('raw', [b'{"account_id":"a","account_id":"b"}', b'NaN',
                                  b'null', b'[]', b'\xff', b'[' * 1500, b' ' * 16385])
def test_invalid_upstream_wire_never_becomes_authority(raw):
    app = main.create_app(org_id=ORG, access_url='https://access.synthetic',
                          service_key='synthetic-service-key',
                          transport=httpx.MockTransport(lambda request: httpx.Response(200, content=raw)))
    with TestClient(app) as client:
        response = client.get('/api/v1/context', headers=HEADERS)
    assert response.status_code == 503
    assert response.json()['error_id'] == 'authorization_unavailable'


def test_duplicate_authorization_header_is_not_forwarded(boundary):
    client, _, calls = boundary
    response = client.get('/api/v1/context', headers=[('Authorization', 'Bearer first'),
                                                    ('Authorization', 'Bearer second')])
    assert response.status_code == 401 and not calls


def test_unexpected_failure_is_safe_and_documented(boundary, caplog):
    client, state, _ = boundary
    state['exception'] = RuntimeError('sensitive-internal-canary')
    response = client.get('/api/v1/context', headers=HEADERS)
    assert response.status_code == 500
    assert response.json()['error_id'] == 'internal_error'
    assert response.headers['cache-control'] == 'private, no-store'
    assert 'sensitive-internal-canary' not in response.text + caplog.text
    assert '500' in main.create_app().openapi()['paths']['/api/v1/context']['get']['responses']


@pytest.mark.parametrize('scheme', ['bearer', 'BEARER'])
def test_bearer_scheme_is_case_insensitive_and_normalized(boundary, scheme):
    client, _, calls = boundary
    response = client.get('/api/v1/context', headers={'Authorization': scheme+' synthetic-user'})
    assert response.status_code == 200
    assert calls[0].headers['authorization'] == 'Bearer synthetic-user'


@pytest.mark.parametrize('origin', ['https://access.synthetic:notaport', 'https://access.synthetic:99999',
                                    'https://access.synthetic:'])
def test_invalid_origin_ports_refuse_at_construction(origin):
    with pytest.raises(RuntimeError, match='^kdg_context_configuration_invalid$'):
        main.create_app(org_id=ORG, access_url=origin, service_key='synthetic-service-key')


def test_encoded_access_response_refuses_before_reading_bytes():
    read = []
    class Encoded(httpx.AsyncByteStream):
        async def __aiter__(self):
            read.append(True)
            yield b'not-even-valid-gzip'
    app = main.create_app(org_id=ORG, access_url='https://access.synthetic',
                          service_key='synthetic-service-key', transport=httpx.MockTransport(
                              lambda request: httpx.Response(200, headers={'Content-Encoding': 'gzip'}, stream=Encoded())))
    with TestClient(app) as client:
        response = client.get('/api/v1/context', headers=HEADERS)
    assert response.status_code == 503
    assert not read


@pytest.mark.parametrize('formatted', ['%Y%m%dT%H%M%SZ', '%Y-%m-%dT%HZ'])
def test_non_rfc3339_current_timestamp_is_not_authority(boundary, formatted):
    client, state, _ = boundary
    # Minute/hour boundaries keep this near current even in implementations truncating.
    fixed = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed
    from unittest.mock import patch
    state['body']['checked_at'] = fixed.strftime(formatted)
    with patch.object(main, 'datetime', Clock):
        response = client.get('/api/v1/context', headers=HEADERS)
    assert response.status_code == 503


def test_schema_publishes_nonnil_and_bigint_constraints():
    import re
    schema = main.create_app().openapi()['components']['schemas']['Context']['properties']
    assert schema['account_id']['not'] == {'const': '00000000-0000-0000-0000-000000000000'}
    member = schema['membership_id']['pattern']
    for value in ('1', '9007199254740993', '9223372036854775807'):
        assert re.fullmatch(member, value)
    for value in ('0', '01', '9223372036854775808', '9999999999999999999'):
        assert not re.fullmatch(member, value)


def test_stalled_request_body_is_bounded_before_access(monkeypatch):
    import asyncio
    import time
    calls = []
    monkeypatch.setattr(main, 'REQUEST_SECONDS', 0.03)
    app = main.create_app(org_id=ORG, access_url='https://access.synthetic', service_key='synthetic-service-key',
                          transport=httpx.MockTransport(lambda request: calls.append(request)))
    async def body():
        await asyncio.sleep(1)
        yield b'{}'
    async def run():
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='https://kdg.synthetic') as client:
                started = time.monotonic()
                response = await client.request('GET', '/api/v1/context', headers=HEADERS, content=body())
                return response, time.monotonic()-started
    response, elapsed = asyncio.run(run())
    assert response.status_code == 503 and 0.02 <= elapsed < 0.5
    assert not calls


def test_streamed_body_uses_same_access_deadline_and_closes(monkeypatch):
    import asyncio
    import time
    closed = []
    monkeypatch.setattr(main, 'ACCESS_SECONDS', 0.03)
    class SlowBody(httpx.AsyncByteStream):
        async def __aiter__(self):
            for _ in range(20):
                await asyncio.sleep(0.01)
                yield b' '
        async def aclose(self):
            closed.append(True)
    app = main.create_app(org_id=ORG, access_url='https://access.synthetic', service_key='synthetic-service-key',
                          transport=httpx.MockTransport(lambda request: httpx.Response(200, stream=SlowBody())))
    with TestClient(app) as client:
        started = time.monotonic()
        response = client.get('/api/v1/context', headers=HEADERS)
        elapsed = time.monotonic()-started
    assert response.status_code == 503 and 0.02 <= elapsed < 0.5
    assert closed


@pytest.mark.parametrize('offset,status', [(-1,200), (-1.000001,503), (1,200), (1.000001,503)])
def test_freshness_tolerance_boundaries(boundary, monkeypatch, offset, status):
    from datetime import timedelta
    client, state, _ = boundary
    fixed = datetime.now(timezone.utc)
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed
    monkeypatch.setattr(main, 'datetime', Clock)
    state['body']['checked_at'] = (fixed+timedelta(seconds=offset)).isoformat().replace('+00:00','Z')
    assert client.get('/api/v1/context', headers=HEADERS).status_code == status
