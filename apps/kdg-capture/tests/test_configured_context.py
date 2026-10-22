"""Behavioral acceptance of explicit KDG startup policy; synthetic HTTP only."""
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

API = Path(__file__).resolve().parents[1] / 'api'
sys.path.insert(0, str(API))
ACCOUNT = '11111111-1111-4111-8111-111111111111'
ACTOR = '22222222-2222-4222-8222-222222222222'
ORG = '33333333-3333-4333-8333-333333333333'
POLICY = {'KDG_ORG_ID': ORG, 'KDG_ACCESS_URL': 'https://access.synthetic',
          'KDG_SERVICE_KEY': 'synthetic-config-key'}


def factory(environment, transport):
    path = API / 'runtime.py'
    spec = importlib.util.spec_from_file_location('kdg_configured_runtime', path)
    module = importlib.util.module_from_spec(spec)
    # Each owner normally runs in its own process; isolate sibling main imports
    # when this test shares a pytest process with Access's main module.
    owner_spec = importlib.util.spec_from_file_location('kdg_startup_main', API / 'main.py')
    owner = importlib.util.module_from_spec(owner_spec)
    owner_spec.loader.exec_module(owner)
    from unittest.mock import patch
    with patch.dict(sys.modules, {'main': owner}):
        spec.loader.exec_module(module)
    return module.create_app(environment, transport=transport)


def test_configured_entry_calls_current_exact_access():
    calls = []
    def current(request):
        calls.append(request)
        return httpx.Response(200, json={
            'account_id': ACCOUNT, 'actor_id': ACTOR, 'membership_id': '9007199254740993',
            'permission': 'kdg_capture.capture.read.own',
            'authorization_scope': {'kind': 'organization', 'org_id': ORG},
            'resource_scope': {'kind': 'own_account', 'account_id': ACCOUNT},
            'decision_id': '44444444-4444-4444-8444-444444444444',
            'checked_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')})
    with TestClient(factory(POLICY, httpx.MockTransport(current))) as client:
        response = client.get('/api/v1/context', headers={'Authorization': 'Bearer synthetic-caller'})
    assert response.status_code == 200, response.text
    assert response.json()['account_id'] == ACCOUNT
    assert response.headers['cache-control'] == 'private, no-store'
    assert len(calls) == 1
    assert calls[0].url == 'https://access.synthetic/v2/check'
    assert calls[0].headers['x-service-key'] == POLICY['KDG_SERVICE_KEY']
    assert json.loads(calls[0].content)['authorization_scope']['org_id'] == ORG


@pytest.mark.parametrize('missing', list(POLICY))
def test_missing_policy_refuses_at_startup(missing):
    policy = {key: value for key, value in POLICY.items() if key != missing}
    with pytest.raises(RuntimeError, match='^kdg_context_configuration_invalid$'):
        factory(policy, httpx.MockTransport(lambda request: pytest.fail('network')))


def test_empty_explicit_policy_does_not_inherit_ambient(monkeypatch):
    for key, value in POLICY.items():
        monkeypatch.setenv(key, value)
    with pytest.raises(RuntimeError, match='^kdg_context_configuration_invalid$'):
        factory({}, httpx.MockTransport(lambda request: pytest.fail('network')))


@pytest.mark.parametrize('key,value', [('KDG_SERVICE_KEY','sensitive-config-canary\n'),
                                      ('KDG_ORG_ID','sensitive-config-canary'),
                                      ('KDG_ACCESS_URL','https://user:sensitive-config-canary@access.synthetic')])
def test_invalid_policy_has_fixed_safe_failure(key, value, caplog):
    with pytest.raises(RuntimeError) as error:
        factory({**POLICY, key: value}, httpx.MockTransport(lambda request: pytest.fail('network')))
    assert str(error.value) == 'kdg_context_configuration_invalid'
    assert 'sensitive-config-canary' not in caplog.text + repr(error.value)


def test_default_environment_is_read_once_at_construction(monkeypatch):
    calls = []
    for key,value in POLICY.items():
        monkeypatch.setenv(key,value)
    def denied(request):
        calls.append(request)
        return httpx.Response(403,json={'detail':{'code':'access_denied'}})
    app = factory(None,httpx.MockTransport(denied))
    monkeypatch.setenv('KDG_ORG_ID',ACTOR)
    monkeypatch.setenv('KDG_SERVICE_KEY','synthetic-later-key')
    with TestClient(app) as client:
        response = client.get('/api/v1/context',headers={'Authorization':'Bearer synthetic-caller'})
    assert response.status_code == 403
    assert calls[0].headers['x-service-key'] == POLICY['KDG_SERVICE_KEY']
    assert json.loads(calls[0].content)['authorization_scope']['org_id'] == ORG
