"""Bounded production admission; HTTP doubles never establish owner readiness."""
import asyncio
from datetime import datetime, timezone
import sys
import time
from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from config import Settings
from personal_notes_access import StudiesAccess, NotesError
from personal_notes_router import build_router

A='10000000-0000-4000-8000-000000000001'
B='10000000-0000-4000-8000-000000000002'

def configuration(**changes):
    return Settings(_env_file=None,app_env='production',
        scribeswell_database_url='postgresql://scribeswell_runtime:fixture@localhost/postgres?sslmode=require',
        **({'scribeswell_studies_enabled':True,
        'scribeswell_studies_account_id':A,
        'scribeswell_studies_database_url':'postgresql://scribeswell_studies_runtime:fixture@localhost/postgres?sslmode=require',
        'scribeswell_studies_access_url':'https://access.example',
        'scribeswell_studies_service_key':'server-only'}|changes))

def test_bounded_production_requires_canonical_account_tls_and_complete_opt_in():
    assert configuration().scribeswell_studies_account_id==A
    assert configuration(scribeswell_studies_access_url='http://access:8000').scribeswell_studies_enabled
    for changes in ({'scribeswell_studies_account_id':''},{'scribeswell_studies_account_id':'AAAAAAAA-0000-4000-8000-000000000001'},
        {'scribeswell_studies_account_id':A+','+B},{'scribeswell_studies_account_id':'00000000-0000-0000-0000-000000000000'},
        {'scribeswell_studies_database_url':'postgresql://scribeswell_studies_runtime:fixture@localhost/postgres'},
        {'scribeswell_studies_access_url':'http://access.example'},{'scribeswell_studies_enabled':False}):
        with pytest.raises(ValueError):configuration(**changes)

def test_only_freshly_verified_matching_account_may_reach_storage_and_enrollment_never_calls_owner():
    calls=[]
    account=A
    status=200
    def upstream(request):
        calls.append(request.url.path)
        return httpx.Response(status,json={'account_id':account,'actor_id':A,
            'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'},
            'decision_id':B,'checked_at':datetime.now(timezone.utc).isoformat()})
    access=StudiesAccess('https://access.example','server-only',httpx.MockTransport(upstream),allowed_account_id=A)
    class Storage:
        async def list(self,identity,*args):
            assert identity['account_id']==A
            return {'items':[],'next_cursor':None}
    app=FastAPI();app.include_router(build_router(access,Storage()))
    client=TestClient(app);headers={'Authorization':'Bearer current'}
    assert client.get('/api/studies',headers=headers).status_code==200
    assert client.get('/api/studies',headers=headers).status_code==200
    assert calls==['/v2/check','/v2/check']
    account=B
    assert client.get('/api/studies',headers=headers).status_code==403
    account=A;status=403
    assert client.get('/api/studies',headers=headers).status_code==403
    status=503
    assert client.get('/api/studies',headers=headers).status_code==503
    before=list(calls)
    assert client.post('/api/studies/enrollment',headers=headers,json={'operation_id':B}).status_code==403
    assert calls==before

def test_default_keeps_private_routes_absent_and_public_options_independent():
    from main import app
    client=TestClient(app)
    assert client.get('/api/studies').status_code==404
    assert client.get('/health').status_code==200
    result=client.options('/api/bible/books',headers={'Origin':'http://localhost:5174','Access-Control-Request-Method':'GET'})
    assert result.status_code==200
