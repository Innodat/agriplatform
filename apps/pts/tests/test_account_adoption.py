"""Account admission and preservation characterization; no membership fixture."""
from datetime import datetime, timezone
from uuid import uuid4
import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from apps.pts.backend.clients import AccessClient
from apps.pts.backend.main import create_app
from apps.pts.tests.test_api import Repo

ACCOUNT='33333333-3333-4333-8333-333333333333'
ACTOR='44444444-4444-4444-8444-444444444444'

class AccountAccess:
    def __init__(self):self.allowed={'pts.poetry.read'};self.calls=[]
    def verify(self,token,permission):
        self.calls.append(permission)
        if not token:raise HTTPException(401,{'code':'authentication_required'})
        if permission not in self.allowed:raise HTTPException(403,{'code':'access_denied'})
        return dict(account_id=ACCOUNT,actor_id=ACTOR,permission=permission,authorization_scope={'kind':'account'})

class AccountRepo:
    def __init__(self):self.actors=[]
    def read(self,actor):self.actors.append(actor);return Repo().read(None,None)
    def sources(self,actor):return {k:self.read(actor)[k] for k in ('sources','rights','source_documents')}
    def attachment(self,actor,document):return None


def test_membership_free_entry_preserves_payload_order_citations_filters_and_exact_grants():
    access=AccountAccess();repo=AccountRepo();client=TestClient(create_app(access=access,repository=repo))
    headers={'Authorization':'Bearer current'}
    result=client.get('/api/poetry?availability=checked',headers=headers)
    assert result.status_code==200
    assert result.json()['total']==33
    assert repo.actors==[ACTOR]
    assert client.get('/api/poetry/SWA-001',headers=headers).json()['poem']==Repo().read(None,None)['poems'][0]
    assert client.get('/api/sources',headers=headers).json()['source_documents']==Repo().read(None,None)['source_documents']
    for path in ('/api/exports?format=json','/api/documents/DOC-VELTEN'):
        assert client.get(path,headers=headers).status_code==403
    access.allowed={'pts.poetry.export'}
    assert client.get('/api/poetry',headers=headers).status_code==403
    assert len(client.get('/api/exports?format=json&availability=checked',headers=headers).json()['poems'])==33


def test_stale_org_cannot_select_a_partition():
    client=TestClient(create_app(access=AccountAccess(),repository=AccountRepo()))
    headers={'Authorization':'Bearer current','X-Org-ID':str(uuid4())}
    assert client.get('/api/poetry?org='+str(uuid4()),headers=headers).status_code==200


def test_typed_account_http_contract_has_no_v1_or_scope_fallback(monkeypatch):
    calls=[]
    def post(url,**kwargs):
        calls.append((url,kwargs))
        return httpx.Response(200,json=dict(account_id=ACCOUNT,actor_id=ACTOR,permission='pts.poetry.read',authorization_scope={'kind':'account'},decision_id=str(uuid4()),checked_at=datetime.now(timezone.utc).isoformat()),request=httpx.Request('POST',url))
    monkeypatch.setattr(httpx,'post',post)
    decision=AccessClient('http://access.test','private').verify('Bearer current','pts.poetry.read')
    assert decision['actor_id']==ACTOR
    assert calls[0][0]=='http://access.test/v2/check'
    assert calls[0][1]['json']==dict(permission='pts.poetry.read',authorization_scope={'kind':'account'})
    def foreign(url,**kwargs):
        return httpx.Response(200,json=dict(account_id=ACCOUNT,actor_id=ACTOR,permission='pts.poetry.read',authorization_scope={'kind':'organization','org_id':str(uuid4())},decision_id=str(uuid4()),checked_at=datetime.now(timezone.utc).isoformat()),request=httpx.Request('POST',url))
    monkeypatch.setattr(httpx,'post',foreign)
    with pytest.raises(HTTPException) as failure:AccessClient('http://access.test','private').verify('Bearer current','pts.poetry.read')
    assert failure.value.status_code==503
