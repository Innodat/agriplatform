"""Synthetic protected HTTP + recorded SQL; no native commit or real authority."""
import asyncio
import threading
import anyio.to_thread
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from uuid import UUID
from types import SimpleNamespace

import httpx

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'apps/kdg-capture/api'))
sys.path.insert(0, str(ROOT / 'apps/kdg-capture/write-candidate'))
import capture_create_handler as handler
import test_capture_create as support
from test_operation_outcomes import Rows as OutcomeRows

create = handler.create
write = create.write
ORG, ACCOUNT, ACTOR = support.ORG, support.ACCOUNT, support.ACTOR
STORED_CAPTURE = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
STORED_CHILD = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'
DECISION = 'cccccccc-cccc-4ccc-8ccc-cccccccccccc'
INTERNAL = 'dddddddd-dddd-4ddd-8ddd-dddddddddddd'


def evidence(permission=create.ALL):
    return dict(account_id=ACCOUNT, actor_id=ACTOR, membership_id='7',
        authorization_scope=dict(kind='organization', org_id=ORG),
        resource_scope=dict(kind='own_account', account_id=ACCOUNT), permission=permission,
        decision_id=DECISION, checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))


def stored():
    return dict(id=UUID(INTERNAL), org_id=UUID(ORG), executor_account_id=UUID(ACCOUNT),
        executor_actor_id=UUID(ACTOR), command_type='capture.create', operation_id=UUID(support.OPERATION),
        command_version=1, result_version=1, result=dict(capture_id=STORED_CAPTURE, revision='1'),
        initiator_actor_id=UUID(ACTOR), committed_at=datetime.now(timezone.utc))


class Connection(support.Connection):
    def __init__(self):
        super().__init__(); self.outcome=None
        self.target=dict(id=UUID(STORED_CAPTURE), org_id=UUID(ORG), owner_account_id=UUID(ACCOUNT), child_id=UUID(STORED_CHILD))
        self.replay_assignment=dict(membership_id=7, active=True)
    def execute(self, sql, parameters):
        result = super().execute(sql, parameters)
        if 'FROM kdg_capture.operation_outcome' in str(sql): return OutcomeRows(self.outcome)
        if str(sql) == handler.STORED_CAPTURE: return support.Rows(self.target)
        if str(sql) == create.ASSIGNMENT and parameters['child'] == STORED_CHILD:
            return support.Rows(self.replay_assignment)
        return result


class ProtectedCreateAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db=Connection(); self.requests=[]; self.response=lambda permission: httpx.Response(200,json=evidence(permission))
        self.fresh=[]
        async def upstream(request):
            self.assertFalse(self.db.in_transaction(), 'Access must run before locks/transaction')
            self.requests.append(request)
            result=self.response(json.loads(request.content)['permission'])
            return await result if hasattr(result,'__await__') else result
        self.handler=handler.CreateHandler(org_id=ORG,access_url='https://access.invalid',service_key='synthetic-service-key',transport=httpx.MockTransport(upstream))
    def raw(self,**changes): return json.dumps(support.command(**changes).model_dump())
    async def execute(self,**changes): return await self.handler.execute(self.db,self.raw(**changes),'Bearer synthetic-account-token')
    def permissions(self): return [json.loads(request.content)['permission'] for request in self.requests]
    def assert_no_business_sql(self): self.assertFalse(any('kdg_capture.' in sql for sql,_ in self.db.calls))
    async def test_combined_capability_checks_share_one_deadline(self):
        async def delayed(permission):
            await asyncio.sleep(.025)
            return httpx.Response(403,json={'detail':{'code':'access_denied'}}) if permission==create.ALL else httpx.Response(200,json=evidence(permission))
        self.response=delayed
        with patch.object(handler,'ACCESS_SECONDS',.04),self.assertRaises(handler.HandlerError) as failed:
            await self.execute()
        self.assertEqual(failed.exception.error_id,'authorization_unavailable')
        self.assertEqual(self.permissions(),[create.ALL,create.ASSIGNED]);self.assert_no_business_sql()
    async def test_lost_acknowledgement_retry_recovers_without_second_inserts(self):
        now=100.0
        def committed_but_late():
            nonlocal now
            self.db.outcome={**stored(),'result':dict(capture_id=support.CAPTURE,revision='1')}
            self.db.target=dict(id=UUID(support.CAPTURE),org_id=UUID(ORG),owner_account_id=UUID(ACCOUNT),child_id=UUID(support.CHILD))
            now=111.0
        self.db.on_commit=committed_but_late
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):
            with self.assertRaises(handler.HandlerError) as failed:await self.execute()
            self.assertEqual(failed.exception.error_id,'execution_timeout')
            before=sum(sql.startswith('INSERT') for sql,_ in self.db.calls)
            self.assertEqual(before,3)
            self.db.on_commit=lambda:None
            receipt=await self.execute(capture_id=STORED_CAPTURE,answers={},child_eligibility_ref='obsolete')
            self.assertEqual(receipt.result.capture_id,support.CAPTURE)
            self.assertEqual(receipt.operation_id,support.OPERATION)
            self.assertEqual(sum(sql.startswith('INSERT') for sql,_ in self.db.calls),before)
    async def test_distinct_wire_id_requirement_applies_before_existing_lookup(self):
        self.db.outcome=stored()
        with self.assertRaises(handler.HandlerError) as failed:await self.execute(capture_id=support.OPERATION)
        self.assertEqual(failed.exception.error_id,'validation_failed')
        self.assertEqual(self.requests,[]);self.assert_no_business_sql()
    def test_configuration_is_explicit_and_safe(self):
        for changes in ({'org_id':None},{'access_url':'http://access.invalid'},
            {'access_url':'https://user:secret@access.invalid'}, {'access_url':'https://access.invalid?secret'},
            {'access_url':'https://access.invalid/path'}, {'access_url':'https://access.invalid:0'},
            {'service_key':'secret\nkey'},{'service_key':''}):
            policy=dict(org_id=ORG,access_url='https://access.invalid',service_key='synthetic-service-key')
            policy.update(changes)
            with self.subTest(changes=changes),self.assertRaisesRegex(RuntimeError,'^kdg_create_configuration_invalid$'):
                handler.CreateHandler(**policy)
        self.assertEqual(self.requests,[])
    async def test_cancellation_waits_for_worker_before_connection_release(self):
        started,release=threading.Event(),threading.Event()
        def pending_worker(*args):
            self.db.active=True;started.set()
            try:release.wait(1)
            finally:self.db.active=False
        with patch.object(handler,'_transaction',side_effect=pending_worker):
            task=asyncio.create_task(self.execute())
            try:
                for _ in range(100):
                    if started.is_set():break
                    await asyncio.sleep(.001)
                self.assertTrue(started.is_set())
                task.cancel();await asyncio.sleep(.01)
                task.cancel();await asyncio.sleep(.01)
                self.assertFalse(task.done(),'caller cancellation escaped while worker owned connection')
            finally:
                release.set()
                with self.assertRaises(asyncio.CancelledError):await task
                for _ in range(100):
                    if not self.db.active:break
                    await asyncio.sleep(.001)
                self.assertFalse(self.db.active)
    async def test_worker_admission_expires_without_late_sql(self):
        limiter=anyio.to_thread.current_default_thread_limiter()
        previous=limiter.total_tokens;limiter.total_tokens=1
        original_budget=write.Budget
        def short_budget():
            budget=original_budget();budget.deadline=budget.started_at+.02
            return budget
        try:
            async with limiter:
                with patch.object(write,'Budget',side_effect=short_budget):
                    task=asyncio.create_task(self.execute())
                    try:
                        await asyncio.sleep(.06)
                        self.assertTrue(task.done(),'worker admission retained connection beyond total budget')
                    finally:
                        # On the old implementation, release the limiter before cleanup.
                        limiter.release()
                        try:
                            with self.assertRaises(handler.HandlerError) as failed:await task
                            self.assertEqual(failed.exception.error_id,'execution_timeout')
                        finally:
                            await limiter.acquire()
            self.assert_no_business_sql()
        finally:limiter.total_tokens=previous
    async def test_current_create_all_returns_only_after_commit(self):
        receipt=await self.execute()
        self.assertEqual(receipt.result.capture_id,support.CAPTURE)
        self.assertEqual(self.db.calls[-1][0],'COMMIT')
        self.assertEqual(self.permissions(),[create.ALL])
        req=self.requests[0]
        self.assertEqual(str(req.url),'https://access.invalid/v2/check')
        self.assertEqual(req.headers['X-Service-Key'],'synthetic-service-key')
        self.assertEqual(req.headers['Authorization'],'Bearer synthetic-account-token')
        self.assertEqual(json.loads(req.content)['authorization_scope'],dict(kind='organization',org_id=ORG))
    async def test_confirmed_all_denial_selects_current_assigned(self):
        self.response=lambda permission: httpx.Response(403,json={'detail':{'code':'access_denied'}}) if permission==create.ALL else httpx.Response(200,json=evidence(permission))
        await self.execute()
        self.assertEqual(self.permissions(),[create.ALL,create.ASSIGNED])
    async def test_committed_retry_uses_original_target_not_changed_incoming_semantics(self):
        self.db.outcome=stored()
        receipt=await self.execute(answers={},child_eligibility_ref='no-longer-valid')
        self.assertEqual(receipt.result.capture_id,STORED_CAPTURE)
        self.assertEqual(receipt.result.revision,'1')
        self.assertFalse(any(sql.startswith('INSERT') for sql,_ in self.db.calls))
        self.assertFalse(any(sql in (create.ELIGIBILITY,create.VERSION,create.CHILD) for sql,_ in self.db.calls))
        _,args=next((sql,args) for sql,args in self.db.calls if sql==handler.STORED_CAPTURE)
        self.assertEqual((args['capture'],args['account'],args['org']),(STORED_CAPTURE,ACCOUNT,ORG))
    async def test_assigned_retry_checks_stored_child_current_membership(self):
        self.db.outcome=stored()
        self.response=lambda permission: httpx.Response(403,json={'detail':{'code':'access_denied'}}) if permission==create.ALL else httpx.Response(200,json=evidence(permission))
        self.db.replay_assignment=None
        with self.assertRaises(handler.HandlerError) as failed: await self.execute(answers={})
        self.assertEqual((failed.exception.status,failed.exception.error_id),(403,'assignment_unavailable'))
        _,args=next((sql,args) for sql,args in self.db.calls if sql==create.ASSIGNMENT)
        self.assertEqual(args['child'],STORED_CHILD)
        self.assertNotIn(('COMMIT',{}),self.db.calls)
    async def test_replay_assignment_active_and_membership_are_current(self):
        self.response=lambda permission: httpx.Response(403,json={'detail':{'code':'access_denied'}}) if permission==create.ALL else httpx.Response(200,json=evidence(permission))
        for assignment in (dict(membership_id=8,active=True),dict(membership_id=7,active=False),dict(membership_id=7,active=True)):
            self.db=Connection(); self.db.outcome=stored(); self.db.replay_assignment=assignment
            if assignment['membership_id']==7 and assignment['active']:
                self.assertEqual((await self.execute(answers={})).result.capture_id,STORED_CAPTURE)
            else:
                with self.assertRaises(handler.HandlerError) as failed: await self.execute(answers={})
                self.assertEqual(failed.exception.error_id,'assignment_unavailable')
    async def test_missing_or_foreign_stored_target_never_discloses_receipt(self):
        for target in (None,{**self.db.target,'owner_account_id':UUID(DECISION)},
                       {**self.db.target,'id':UUID(DECISION)},{**self.db.target,'org_id':UUID(DECISION)}):
            self.db=Connection(); self.db.outcome=stored(); self.db.target=target
            with self.subTest(target=target),self.assertRaises(handler.HandlerError) as failed: await self.execute()
            self.assertEqual(failed.exception.error_id,'operation_verification_unavailable')
            self.assertNotIn(('COMMIT',{}),self.db.calls)
    async def test_unknown_stored_outcome_version_is_unavailable(self):
        self.db.outcome={**stored(),'result_version':2}
        with self.assertRaises(handler.HandlerError) as failed: await self.execute()
        self.assertEqual(failed.exception.error_id,'operation_verification_unavailable')
        self.assertFalse(any(sql==handler.STORED_CAPTURE for sql,_ in self.db.calls))
    async def test_fresh_validation_failure_cannot_commit(self):
        with self.assertRaises(handler.HandlerError) as failed: await self.execute(answers={})
        self.assertEqual((failed.exception.status,failed.exception.error_id),(422,'validation_failed'))
        self.assertNotIn(('COMMIT',{}),self.db.calls)
    async def test_commit_failure_never_returns_provisional_receipt(self):
        self.db.fail_commit=True
        with self.assertRaises(handler.HandlerError) as failed: await self.execute()
        self.assertEqual(failed.exception.error_id,'internal_error')
        self.assertNotIn('secret',str(failed.exception))
    async def test_deadline_after_commit_remains_uncertain_failure(self):
        now=100.0
        def clock():return now
        def late():
            nonlocal now
            now=111
        self.db.on_commit=late
        with patch.object(write,'time',SimpleNamespace(monotonic=clock)),self.assertRaises(handler.HandlerError) as failed:
            await self.execute()
        self.assertEqual(failed.exception.error_id,'execution_timeout')
        self.assertIn(('COMMIT',{}),self.db.calls)
    async def test_authority_scope_permission_actor_and_freshness_are_closed(self):
        cases=[{'actor_id':None},{'membership_id':'0'},{'membership_id':'9223372036854775808'},
            {'permission':create.ASSIGNED},{'authorization_scope':{'kind':'organization','org_id':DECISION}},
            {'resource_scope':{'kind':'own_account','account_id':DECISION}},
            {'resource_scope':{'kind':'organization','org_id':ORG}},
            {'checked_at':'2000-01-01T00:00:00Z'},{'checked_at':'2999-01-01T00:00:00Z'},
            {'decision_id':None},{'extra':'sensitive-canary'}]
        for changes in cases:
            self.db=Connection();self.requests=[]
            self.response=lambda permission: httpx.Response(200,json={**evidence(permission),**changes})
            with self.subTest(changes=changes),self.assertRaises(handler.HandlerError) as failed: await self.execute()
            self.assertEqual(failed.exception.error_id,'authorization_unavailable')
            self.assertEqual(self.permissions(),[create.ALL]); self.assert_no_business_sql()
    async def test_only_confirmed_access_denied_allows_fallback(self):
        for status,body,expected in ((503,{'detail':{'code':'access_denied'}},'authorization_unavailable'),
            (403,{'detail':{'code':'service_access_denied'}},'authorization_unavailable'),
            (401,{'detail':{'code':'authentication_required'}},'authentication_required'),
            (409,{'detail':{'code':'identity.actor_setup_required'}},'identity.actor_setup_required'),
            (302,{'detail':{'code':'access_denied'}},'authorization_unavailable')):
            self.requests=[];self.response=lambda permission:httpx.Response(status,json=body,headers={'location':'https://other.invalid'})
            with self.subTest(status=status),self.assertRaises(handler.HandlerError) as failed:await self.execute()
            self.assertEqual(failed.exception.error_id,expected);self.assertEqual(self.permissions(),[create.ALL]);self.assert_no_business_sql()
    async def test_both_capability_denials_are_access_denied(self):
        self.response=lambda permission:httpx.Response(403,json={'detail':{'code':'access_denied'}})
        with self.assertRaises(handler.HandlerError) as failed:await self.execute()
        self.assertEqual((failed.exception.status,failed.exception.error_id),(403,'access_denied'))
        self.assertEqual(self.permissions(),[create.ALL,create.ASSIGNED]);self.assert_no_business_sql()
    async def test_transport_error_body_bounds_duplicates_encoding_fail_closed(self):
        async def transport_failure():raise httpx.ConnectError('sensitive-token-connection-canary')
        for result in (httpx.Response(200,content=b'{"account_id":"x","account_id":"y"}'),
            httpx.Response(200,content=b'x'*16385),httpx.Response(200,content=b'{bad'),
            httpx.Response(200,content=b'',headers={'content-encoding':'gzip'}),transport_failure):
            self.requests=[]
            self.response=lambda permission:result() if callable(result) else result
            with self.subTest(result=type(result).__name__),self.assertRaises(handler.HandlerError) as failed:await self.execute()
            self.assertEqual(failed.exception.error_id,'authorization_unavailable')
            self.assertNotIn('canary',str(failed.exception));self.assertEqual(self.permissions(),[create.ALL]);self.assert_no_business_sql()
    async def test_cleanup_delay_cannot_refresh_authority_observation(self):
        now=100.0
        async def close_transport():
            nonlocal now
            now+=2
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)), \
             patch.object(self.handler._transport,'aclose',side_effect=close_transport), \
             self.assertRaises(handler.HandlerError) as failed:
            await self.execute()
        self.assertEqual(failed.exception.error_id,'authorization_observation_expired')
        self.assert_no_business_sql()
    async def test_total_access_deadline_bounds_slow_body(self):
        class Slow(httpx.AsyncByteStream):
            async def __aiter__(self):
                await asyncio.sleep(.05)
                yield b'{}'
        self.response=lambda permission:httpx.Response(200,stream=Slow())
        with patch.object(handler,'ACCESS_SECONDS',.01),self.assertRaises(handler.HandlerError) as failed:await self.execute()
        self.assertEqual(failed.exception.error_id,'authorization_unavailable');self.assert_no_business_sql()
    async def test_active_transaction_and_invalid_input_refuse_before_http(self):
        self.db.active=True
        with self.assertRaises(handler.HandlerError) as failed:await self.execute()
        self.assertEqual(failed.exception.error_id,'invalid_write_context');self.assertEqual(self.requests,[])
        self.db.active=False;self.db.autocommit=True
        with self.assertRaises(handler.HandlerError) as failed:await self.execute()
        self.assertEqual(failed.exception.error_id,'invalid_write_context');self.assertEqual(self.requests,[])
        self.db.autocommit=False
        for raw,token,expected in (('{bad','Bearer token','validation_failed'),(self.raw(),'bad token','authentication_required'),
            (self.raw(capture_id=support.OPERATION),'Bearer token','validation_failed')):
            with self.subTest(expected=expected),self.assertRaises(handler.HandlerError) as failed:
                await self.handler.execute(self.db,raw,token)
            self.assertEqual(failed.exception.error_id,expected);self.assertEqual(self.requests,[])


if __name__=='__main__':unittest.main()
