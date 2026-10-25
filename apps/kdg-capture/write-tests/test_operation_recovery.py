"""Synthetic own-read recovery acceptance; no mounted route or real authority."""
import asyncio
import json
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from uuid import UUID

import httpx
import test_capture_create_handler as support
import operation_recovery as recovery

class Connection(support.Connection):
    def execute(self, sql, parameters):
        result = super().execute(sql, parameters)
        if str(sql) == recovery.TARGET: return support.support.Rows(self.target)
        return result

handler = support.handler
write = handler.write

class RecoveryAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db = Connection()
        self.db.outcome = support.stored()
        self.requests = []
        self.response = lambda: httpx.Response(200, json=support.evidence(recovery.PERMISSION))
        async def access(request):
            self.assertFalse(self.db.in_transaction())
            self.requests.append(request)
            return self.response()
        self.handler = recovery.RecoveryHandler(org_id=support.ORG,
            access_url='https://access.invalid', service_key='synthetic-key',
            transport=httpx.MockTransport(access))
    async def execute(self, operation_id=support.support.OPERATION, command_type='capture.create'):
        return await self.handler.execute(self.db, operation_id, command_type, 'Bearer synthetic-token')
    async def test_recovers_original_receipt_using_only_current_own_read(self):
        self.db.replay_assignment = None
        result = await self.execute()
        self.assertEqual(result.result.capture_id, support.STORED_CAPTURE)
        self.assertEqual(result.result.revision, '1')
        self.assertEqual([json.loads(r.content)['permission'] for r in self.requests], [recovery.PERMISSION])
        self.assertEqual(self.db.calls[-1][0], 'COMMIT')
        sqls = [sql for sql, _ in self.db.calls]
        self.assertFalse(any(sql.startswith(('INSERT','UPDATE','DELETE')) or 'pg_advisory' in sql for sql in sqls))
        self.assertFalse(any(sql in (handler.create.ASSIGNMENT, handler.create.CHILD, handler.create.VERSION, handler.create.ELIGIBILITY) for sql in sqls))
    async def test_edit_returns_recorded_revision_without_current_revision_substitution(self):
        self.db.outcome.update(command_type='capture.edit',result=dict(capture_id=support.STORED_CAPTURE,revision='3'))
        result = await self.execute(command_type='capture.edit')
        self.assertEqual((result.command_type,result.result.revision),('capture.edit','3'))
    async def test_successful_absence_only_returns_compact_unresolved(self):
        self.db.outcome = None
        result = await self.execute()
        self.assertEqual(result.model_dump(),dict(operation_id=support.support.OPERATION,command_type='capture.create',status='unresolved'))
        self.assertEqual(self.db.calls[-1][0], 'COMMIT')
    async def test_missing_or_foreign_actual_target_is_unavailable(self):
        target = self.db.target
        for value in (None,{**target,'id':UUID(support.DECISION)},
                      {**target,'org_id':UUID(support.DECISION)},
                      {**target,'owner_account_id':UUID(support.DECISION)}):
            self.db = Connection(); self.db.outcome = support.stored(); self.db.target=value
            with self.assertRaises(handler.HandlerError) as failed: await self.execute()
            self.assertEqual((failed.exception.status,failed.exception.error_id),(503,'operation_verification_unavailable'))
    async def test_unsupported_or_foreign_outcome_never_becomes_unresolved(self):
        for changes in ({'result_version':2},{'command_version':2},{'command_type':'capture.edit'},
                        {'org_id':UUID(support.DECISION)},{'executor_account_id':UUID(support.DECISION)}):
            self.db = Connection(); self.db.outcome={**support.stored(),**changes}
            with self.assertRaises(handler.HandlerError) as failed: await self.execute()
            self.assertEqual(failed.exception.error_id,'operation_verification_unavailable')
    async def test_exact_closed_lookup_input_rejected_before_access(self):
        for operation,command in ((None,'capture.create'),(support.support.OPERATION.upper(),'capture.create'),
                (support.support.OPERATION,'capture.delete'),(support.support.OPERATION,None),
                (support.support.OPERATION,['capture.create']),('00000000-0000-0000-0000-000000000000','capture.create')):
            with self.assertRaises(handler.HandlerError) as failed: await self.execute(operation,command)
            self.assertEqual((failed.exception.status,failed.exception.error_id),(422,'validation_failed'))
        self.assertEqual(self.requests,[])
    async def test_current_access_denial_never_falls_back_or_reads(self):
        self.response=lambda:httpx.Response(403,json={'detail':{'code':'access_denied'}})
        with self.assertRaises(handler.HandlerError) as failed: await self.execute()
        self.assertEqual((failed.exception.status,failed.exception.error_id),(403,'access_denied'))
        self.assertEqual(len(self.requests),1); self.assertEqual(self.db.calls,[])
    async def test_bad_current_actor_scope_or_observation_never_reads(self):
        for changes in ({'actor_id':None},{'permission':handler.create.ALL},
                {'membership_id':'0'},{'checked_at':'2000-01-01T00:00:00Z'},
                {'authorization_scope':dict(kind='organization',org_id=support.DECISION)},
                {'resource_scope':dict(kind='own_account',account_id=support.DECISION)}):
            self.response=lambda:httpx.Response(200,json={**support.evidence(recovery.PERMISSION),**changes})
            with self.assertRaises(handler.HandlerError) as failed: await self.execute()
            self.assertEqual(failed.exception.error_id,'authorization_unavailable')
            self.assertEqual(self.db.calls,[])
    async def test_database_failure_never_claims_absence_or_exposes_details(self):
        from sqlalchemy.exc import OperationalError
        with patch.object(recovery,'_transaction',side_effect=OperationalError('private SQL',{},Exception('secret'))):
            with self.assertRaises(handler.HandlerError) as failed: await self.execute()
        self.assertEqual((failed.exception.status,failed.exception.error_id),(503,'operation_verification_unavailable'))
        self.assertNotIn('secret',str(failed.exception))
    async def test_actual_statement_failure_is_verification_unavailable(self):
        from sqlalchemy.exc import OperationalError
        original=self.db.execute
        def fail(sql, parameters):
            if 'FROM kdg_capture.operation_outcome' in str(sql):
                raise OperationalError('private SQL', {}, Exception('secret'))
            return original(sql,parameters)
        self.db.execute=fail
        with self.assertRaises(handler.HandlerError) as failed: await self.execute()
        self.assertEqual((failed.exception.status,failed.exception.error_id),(503,'operation_verification_unavailable'))
    async def test_cancellation_retains_connection_until_reader_finishes(self):
        import threading
        started,release=threading.Event(),threading.Event()
        def pending(*args):
            self.db.active=True; started.set()
            try: release.wait(1)
            finally: self.db.active=False
        with patch.object(recovery,'_transaction',side_effect=pending):
            task=asyncio.create_task(self.execute())
            try:
                for _ in range(100):
                    if started.is_set(): break
                    await asyncio.sleep(.001)
                self.assertTrue(started.is_set())
                task.cancel(); await asyncio.sleep(.01)
                task.cancel(); await asyncio.sleep(.01)
                self.assertFalse(task.done())
            finally:
                release.set()
                with self.assertRaises(asyncio.CancelledError): await task
            self.assertFalse(self.db.active)
    async def test_admission_deadline_prevents_late_read(self):
        import anyio.to_thread
        limiter=anyio.to_thread.current_default_thread_limiter()
        previous=limiter.total_tokens; limiter.total_tokens=1
        original=write.Budget
        def short():
            result=original(); result.deadline=result.started_at+.02
            return result
        try:
            async with limiter:
                with patch.object(write,'Budget',side_effect=short):
                    task=asyncio.create_task(self.execute())
                    try:
                        await asyncio.sleep(.06)
                        self.assertTrue(task.done())
                    finally:
                        limiter.release()
                        try:
                            with self.assertRaises(handler.HandlerError) as failed: await task
                            self.assertEqual(failed.exception.error_id,'execution_timeout')
                        finally: await limiter.acquire()
            self.assertEqual(self.db.calls,[])
        finally: limiter.total_tokens=previous
    async def test_late_transaction_completion_never_returns_unresolved(self):
        now=100.0
        def late():
            nonlocal now
            now=111.0
        self.db.outcome=None; self.db.on_commit=late
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):
            with self.assertRaises(handler.HandlerError) as failed: await self.execute()
        self.assertEqual(failed.exception.error_id,'execution_timeout')
    async def test_late_committed_receipt_never_escapes(self):
        now=100.0
        def late():
            nonlocal now
            now=111.0
        self.db.on_commit=late
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):
            with self.assertRaises(handler.HandlerError) as failed: await self.execute()
        self.assertEqual(failed.exception.error_id,'execution_timeout')
    async def test_commit_failure_after_absence_never_returns_unresolved(self):
        self.db.outcome=None; self.db.fail_commit=True
        with self.assertRaises(handler.HandlerError) as failed: await self.execute()
        self.assertEqual((failed.exception.status,failed.exception.error_id),(503,'operation_verification_unavailable'))
        self.assertFalse(self.db.in_transaction())
    async def test_stale_after_transport_cleanup_cannot_enter_transaction(self):
        now=100.0
        async def cleanup():
            nonlocal now
            now+=2
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)),patch.object(self.handler._transport,'aclose',side_effect=cleanup):
            with self.assertRaises(handler.HandlerError) as failed: await self.execute()
        self.assertEqual(failed.exception.error_id,'authorization_observation_expired')
        self.assertEqual(self.db.calls,[])

if __name__=='__main__':unittest.main()
