"""Concrete malformed-owner, body-deadline and reviewed-inventory regressions."""
import asyncio
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import httpx
import pytest
from fastapi import HTTPException
from starlette.requests import Request

from apps.pts.backend.clients import AccessClient, CurrentSessionClient
from apps.pts.backend import file_auth
from apps.pts.tools import bind_corpus

ACCOUNT = str(uuid4())
SESSION = str(uuid4())


def account_evidence():
    return dict(account_id=ACCOUNT, actor_id=str(uuid4()), decision_id=str(uuid4()),
                permission='pts.poetry.read', authorization_scope={'kind': 'account'},
                checked_at=datetime.now(timezone.utc).isoformat())


@pytest.mark.parametrize('field,value', [('checked_at', None), ('account_id', 7), ('actor_id', 7), ('decision_id', 7)])
def test_malformed_access_evidence_is_typed_unavailable(monkeypatch, field, value):
    body = {**account_evidence(), field: value}
    monkeypatch.setattr(httpx, 'post', lambda url, **kwargs: httpx.Response(200, json=body, request=httpx.Request('POST', url)))
    with pytest.raises(HTTPException) as failure:
        AccessClient('https://access.test', 'restricted').verify('Bearer current', 'pts.poetry.read')
    assert failure.value.status_code == 503
    assert failure.value.detail == {'code': 'access_unavailable'}


@pytest.mark.parametrize('field,value', [('credential_expires_at', None), ('observed_at', None), ('account_id', 7), ('session_id', 7)])
def test_malformed_identity_evidence_is_typed_unavailable(field, value):
    now = datetime.now(timezone.utc)
    body = dict(account_id=ACCOUNT, session_id=SESSION, observed_at=now.isoformat(),
                credential_expires_at=(now + timedelta(minutes=5)).isoformat())
    body[field] = value
    client = CurrentSessionClient('https://identity.test', 'restricted', httpx.MockTransport(lambda request: httpx.Response(200, json=body)))
    with pytest.raises(HTTPException) as failure:
        asyncio.run(client.verify('Bearer current'))
    assert failure.value.status_code == 503
    assert failure.value.detail == {'code': 'identity.current_session_unavailable'}


@pytest.mark.parametrize('replacement', [dict(permission='pts.poetry.export'), dict(authorization_scope={'kind': 'organization', 'org_id': str(uuid4())})])
def test_complete_wrong_permission_or_foreign_scope_is_rejected(monkeypatch, replacement):
    body = {**account_evidence(), **replacement}
    monkeypatch.setattr(httpx, 'post', lambda url, **kwargs: httpx.Response(200, json=body, request=httpx.Request('POST', url)))
    with pytest.raises(HTTPException) as failure:
        AccessClient('https://access.test', 'restricted').verify('Bearer current', 'pts.poetry.read')
    assert failure.value.status_code == 503


def test_stalled_empty_body_has_typed_validation_deadline(monkeypatch):
    # Preserve the real cancellation mechanism while shortening this focused case.
    timeout = asyncio.timeout
    monkeypatch.setattr(file_auth.asyncio, 'timeout', lambda seconds: timeout(.01))
    async def run():
        async def receive():
            await asyncio.sleep(1)
            return {'type': 'http.request', 'body': b'', 'more_body': False}
        request = Request({'type': 'http', 'query_string': b''}, receive)
        with pytest.raises(HTTPException) as failure:
            await file_auth.empty(request)
        assert failure.value.status_code == 422
        assert failure.value.detail == {'code': 'validation_failed'}
    asyncio.run(run())


def test_repeated_reviewed_binding_still_reconciles_inventory(monkeypatch):
    partition = str(uuid4())
    document = dict(schema_version=1, executor_actor_id=str(uuid4()), legacy_partition_id=partition,
                    inventory_sha256='a' * 64, release_reference='reviewed-release',
                    counts={'poems': 1}, snapshot_sha256='b' * 64)
    class Result:
        def scalar_one(self): return 'pts_migrator'
        def mappings(self): return self
        def first(self): return {key: document[key] for key in ('legacy_partition_id', 'inventory_sha256', 'release_reference')}
    class Connection:
        def execute(self, *args): return Result()
    @contextmanager
    def scoped(*args, **kwargs): yield Connection()
    monkeypatch.setattr(bind_corpus, 'scoped', scoped)
    observed = []
    def inventory(connection):
        observed.append(True)
        return dict(counts={'poems': 2}, snapshot_sha256='c' * 64)
    monkeypatch.setattr(bind_corpus, 'inventory', inventory)
    with pytest.raises(ValueError, match='^corpus_inventory_changed$'):
        bind_corpus.bind(object(), document)
    assert observed == [True]
