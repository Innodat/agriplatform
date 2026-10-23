"""Live-provider semantics and cancellation of the actual async owner work."""
import asyncio
import sys
import time
from pathlib import Path
from uuid import UUID
import httpx
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from studies_identity import StudiesFailure,live_account,transaction,bound_actor
from studies_contract import Operation,AccountCheck,decode
ACCOUNT=UUID('11111111-1111-4111-8111-111111111111')
ENV={'SUPABASE_URL':'https://synthetic.invalid','SUPABASE_ANON_KEY':'synthetic'}
GOOD={'id':str(ACCOUNT),'email':'reader@example.invalid','email_confirmed_at':'2026-01-01T00:00:00Z','is_anonymous':False}

def provider(monkeypatch,value,status=200,delay=False):
    original=httpx.AsyncClient
    async def respond(request):
        if delay:await asyncio.sleep(30)
        return httpx.Response(status,json=value)
    monkeypatch.setattr(httpx,'AsyncClient',lambda **options:original(transport=httpx.MockTransport(respond),**options))

def test_live_verified_primary_account_and_pending_change(monkeypatch):
    provider(monkeypatch,{**GOOD,'new_email':'pending@example.invalid'})
    assert asyncio.run(live_account('Bearer synthetic',time.monotonic()+3,ENV))==ACCOUNT

@pytest.mark.parametrize('patch,status,error',[
    ({'email_confirmed_at':None},403,'identity.verification_required'),
    ({'email':''},403,'identity.verification_required'),
    ({'is_anonymous':True},403,'access_denied'),
    ({'deleted_at':'2026-01-01T00:00:00Z'},403,'access_denied'),
    ({'banned_until':'9999-01-01T00:00:00Z'},403,'access_denied'),
    ({'email_confirmed_at':'not-a-date'},503,'authorization_unavailable'),
    ({'id':'00000000-0000-0000-0000-000000000000'},503,'authorization_unavailable'),
    ({'id':True},503,'authorization_unavailable'),
])
def test_safe_live_current_eligibility(monkeypatch,patch,status,error):
    provider(monkeypatch,{**GOOD,**patch})
    with pytest.raises(StudiesFailure) as failed:asyncio.run(live_account('Bearer synthetic',time.monotonic()+3,ENV))
    assert (failed.value.status,failed.value.error_id)==(status,error)

@pytest.mark.parametrize('status,error',[(401,'authentication_required'),(403,'authentication_required'),(500,'authorization_unavailable')])
def test_safe_provider_errors(monkeypatch,status,error):
    provider(monkeypatch,{'sensitive':'never surfaced'},status)
    with pytest.raises(StudiesFailure) as failed:asyncio.run(live_account('Bearer synthetic',time.monotonic()+3,ENV))
    assert failed.value.error_id==error

def test_provider_deadline_cancels_real_async_work(monkeypatch):
    provider(monkeypatch,GOOD,delay=True)
    started=time.monotonic()
    with pytest.raises(StudiesFailure):asyncio.run(live_account('Bearer synthetic',started+.02,ENV))
    assert time.monotonic()-started<1

@pytest.mark.parametrize('row',[None,{'account_id':str(ACCOUNT),'actor_id':False},{'account_id':str(ACCOUNT),'actor_id':'00000000-0000-0000-0000-000000000000'}])
def test_invalid_owner_evidence_fails_closed(row):
    with pytest.raises(StudiesFailure):bound_actor(row,ACCOUNT)

def test_absent_mapping_distinct_from_invalid_profile():
    assert bound_actor({'account_id':ACCOUNT,'actor_id':None},ACCOUNT,True) is None
    with pytest.raises(StudiesFailure):bound_actor(None,ACCOUNT,True)

def test_async_db_execution_cancellation_rolls_back_without_continuing():
    from contextlib import asynccontextmanager
    events=[]
    class DB:
        @asynccontextmanager
        async def begin(self):
            try:yield self
            finally:events.append('closed')
        async def execute(self,*args):
            try:await asyncio.sleep(30)
            finally:events.append('cancelled')
            events.append('unsafe_continuation')
    with pytest.raises(StudiesFailure):asyncio.run(transaction(DB(),ACCOUNT,time.monotonic()+.02,'SELECT 1'))
    assert events==['cancelled','closed']

@pytest.mark.parametrize('raw',[b'{}',b'{"operation_id":true}',b'{"operation_id":"00000000-0000-0000-0000-000000000000"}',b'{"operation_id":"a","operation_id":"b"}',b'\xef\xbb\xbf{}',b' '*4097,b'[]',b'NaN'])
def test_closed_enrollment_decoder(raw):
    with pytest.raises((ValueError,TypeError)):decode(raw,Operation)

@pytest.mark.parametrize('state,code',[('IS003','access_denied'),('IS006','identity.verification_required')])
def test_confirmed_identity_sql_outcomes_have_closed_denial_mapping(state,code):
    import psycopg
    from contextlib import asynccontextmanager
    class Refusal(psycopg.DatabaseError):sqlstate=state
    class DB:
        @asynccontextmanager
        async def begin(self):yield self
        async def execute(self,*args):raise Refusal('sensitive provider/profile message')
    with pytest.raises(StudiesFailure) as failed:asyncio.run(transaction(DB(),ACCOUNT,time.monotonic()+3,'SELECT 1'))
    assert (failed.value.status,failed.value.error_id)==(403,code)
