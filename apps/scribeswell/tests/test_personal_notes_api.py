"""Private route acceptance. HTTP doubles prove adaptation, not owner SQL authority."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from fastapi import FastAPI
from fastapi.testclient import TestClient
from personal_notes_router import build_router

ACCOUNT='10000000-0000-4000-8000-000000000001'
ACTOR='20000000-0000-4000-8000-000000000001'
OP='30000000-0000-4000-8000-000000000001'

class Access:
    async def check(self, bearer, deadline):
        assert bearer == 'Bearer current'
        return {'account_id': ACCOUNT, 'actor_id': ACTOR}

class Storage:
    async def execute(self, identity, command, payload, study_id, note_id, deadline):
        assert identity['account_id']==ACCOUNT
        return {'operation_id':payload.operation_id,'command':command,'study_id':OP,'note_id':None,'revision':'1'}

def client():
    app=FastAPI()
    app.include_router(build_router(Access(), Storage()))
    return TestClient(app)

def test_explicit_create_current_authority_safe_error_and_no_store():
    c=client()
    result=c.post('/api/studies',headers={'Authorization':'Bearer current'},json={'operation_id':OP,'title':None})
    assert result.status_code==200
    assert result.json()['revision']=='1'
    assert result.headers['cache-control']=='private, no-store'
    invalid=c.post('/api/studies',headers={'Authorization':'Bearer current'},json={'secret':'private note'})
    assert invalid.status_code==400
    assert 'private note' not in invalid.text
    assert invalid.headers['cache-control']=='private, no-store'

def test_authentication_denial_happens_before_storage_and_input_is_never_echoed():
    from personal_notes_access import NotesError
    class Denied:
        async def check(self,*args):raise NotesError('studies_access_denied')
    class Never:
        async def list(self,*args):raise AssertionError('Storage must not execute')
    app=FastAPI();app.include_router(build_router(Denied(),Never()));c=TestClient(app)
    denied=c.get('/api/studies',headers={'Authorization':'Bearer current'})
    assert denied.status_code==403 and denied.json()['code']=='studies_access_denied'
    assert denied.headers['cache-control']=='private, no-store'
    assert c.get('/api/studies').status_code==401
    for raw in (b'{"title":"sensitive","title":null}',b'{"operation_id":"'+OP.encode()+b'","title":"'+b'x'*65536+b'"}'):
        invalid=c.post('/api/studies',headers={'Authorization':'Bearer current'},content=raw)
        assert invalid.status_code==400 and 'sensitive' not in invalid.text

def test_access_exact_binding_and_safe_errors():
    import asyncio,time,httpx
    from personal_notes_access import StudiesAccess,NotesError
    base={'account_id':ACCOUNT,'actor_id':ACTOR,'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'},'decision_id':OP,'checked_at':'2026-10-23T10:00:00Z'}
    async def check(response):
        def transport(req):
            assert req.headers['x-service-key']=='server-only'
            assert req.headers['authorization']=='Bearer current'
            return response
        return await StudiesAccess('https://access.invalid','server-only',httpx.MockTransport(transport)).check('Bearer current',time.monotonic()+5)
    assert asyncio.run(check(httpx.Response(200,json=base)))['account_id']==ACCOUNT
    import pytest
    for invalid in ({**base,'organization_id':ACCOUNT},{**base,'authorization_scope':{'kind':'organization'}},{**base,'actor_id':'invalid'}):
        with pytest.raises(NotesError,match='studies_access_unavailable'):asyncio.run(check(httpx.Response(200,json=invalid)))
    for status,code in ((401,'authentication_required'),(403,'studies_access_denied'),(503,'studies_access_unavailable')):
        with pytest.raises(NotesError,match=code):asyncio.run(check(httpx.Response(status,json={'secret':'never copied'})))

def test_enrollment_rejects_unbound_owner_acknowledgements():
    import httpx
    from personal_notes_access import StudiesAccess
    base={'operation_id':OP,'status':'committed','result':{'disposition':'created','account_id':ACCOUNT,'actor_id':ACTOR,'permission':'scribeswell.studies.use'}}
    invalid=[{**base,'operation_id':ACCOUNT},{**base,'status':'unresolved'}]
    invalid.extend({**base,'result':{**base['result'],field:value}} for field,value in (
        ('permission','another.permission'),('account_id','invalid'),('actor_id','invalid')))
    for acknowledgement in invalid:
        access=StudiesAccess('https://access.invalid','server-only',httpx.MockTransport(lambda request:httpx.Response(200,json=acknowledgement)))
        app=FastAPI();app.include_router(build_router(access,Storage()))
        response=TestClient(app).post('/api/studies/enrollment',headers={'Authorization':'Bearer current'},json={'operation_id':OP})
        assert response.status_code==503
        assert response.json()=={'error':'Request could not be completed','code':'studies_access_unavailable','details':None}
        assert response.headers['cache-control']=='private, no-store'


def test_enabled_main_contains_framework_validation_and_unexpected_private_errors(monkeypatch):
    import importlib.util
    from pydantic import SecretStr
    import config
    monkeypatch.setattr(config.settings,'scribeswell_studies_enabled',True)
    monkeypatch.setattr(config.settings,'scribeswell_studies_access_url','https://access.invalid')
    monkeypatch.setattr(config.settings,'scribeswell_studies_service_key',SecretStr('server-only'))
    monkeypatch.setattr(config.settings,'scribeswell_studies_database_url',SecretStr('postgresql://scribeswell_studies_runtime:fixture@127.0.0.1:1/postgres'))
    spec=importlib.util.spec_from_file_location('notes_review_enabled_main',Path(__file__).resolve().parents[1]/'backend/main.py')
    mounted=importlib.util.module_from_spec(spec);spec.loader.exec_module(mounted)
    @mounted.app.get('/api/studies/_review/typed')
    async def typed(count:int):return {'count':count}
    @mounted.app.get('/api/studies/_review/unexpected')
    async def unexpected():raise RuntimeError('private raw exception')
    @mounted.app.get('/review-public-unexpected')
    async def public_unexpected():raise RuntimeError('public raw exception')
    c=TestClient(mounted.app,raise_server_exceptions=False)
    assert c.post('/api/studies/enrollment',json={'operation_id':OP}).status_code==401
    for response,status,code in (
        (c.get('/api/studies/_review/missing'),404,'resource_unavailable'),
        (c.delete('/api/studies'),404,'resource_unavailable'),
        (c.get('/api/studies/_review/typed?count=private-input'),400,'scribeswell_personal_notes_input_invalid'),
        (c.get('/api/studies/_review/unexpected'),503,'studies_storage_unavailable'),
        (c.post('/api/studies',headers={'Authorization':'Bearer current'},json={'title':'private input'}),400,'scribeswell_personal_notes_input_invalid'),
    ):
        assert response.status_code==status
        assert response.json()=={'error':'Request could not be completed','code':code,'details':None}
        assert response.headers['cache-control']=='private, no-store'
        assert 'private-input' not in response.text and 'raw exception' not in response.text
    public=c.get('/review-public-unexpected')
    assert public.status_code==500 and public.json()=={'error':'Internal server error'}
    assert 'cache-control' not in public.headers
