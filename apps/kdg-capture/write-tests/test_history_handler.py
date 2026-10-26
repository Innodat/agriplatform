"""Direct protected history handler, using existing synthetic authority/storage."""
import unittest
import httpx
import test_capture_read as support
import test_history_http as wire
import capture_history as history

class HistoryHandlerAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db=wire.Connection();self.checks=[]
        self.upstream=lambda:httpx.Response(200,json=support.support.evidence(history.PERMISSION))
        async def access(request):
            self.assertFalse(self.db.in_transaction());self.checks.append(request);return self.upstream()
        self.handler=history.HistoryHandler(org_id=support.ORG,access_url='https://access.invalid',service_key='synthetic',transport=httpx.MockTransport(access))
        self.query=dict(from_date='2026-10-01',to_date='2026-10-26',limit=2)
    async def execute(self,query=None,authorization='Bearer synthetic'):
        return await self.handler.execute(self.db,self.query if query is None else query,authorization)
    async def test_valid_direct_pages_use_current_owner_and_original_definition(self):
        first=await self.execute();self.assertEqual(len(first.items),2);self.assertIsNotNone(first.next_cursor)
        second=await self.execute({**self.query,'cursor':first.next_cursor})
        self.assertEqual(len(second.items),2);self.assertNotEqual(first.items[0].capture_id,second.items[0].capture_id)
        self.assertEqual(first.items[0].definition.model_dump(mode='json'),support.DEFINITION)
        self.assertEqual((first.org_id,first.account_id),(support.ORG,support.ACCOUNT))
        self.assertEqual(len(self.checks),2);self.assertFalse(self.db.in_transaction())
    async def test_exact_access_observation_is_seven_days_without_another_check(self):
        from datetime import timedelta
        evidence=support.support.evidence(history.PERMISSION)
        self.upstream=lambda:httpx.Response(200,json=evidence)
        page=await self.execute()
        observed=page.observation.model_dump(mode='json')
        for key,value in evidence.items():self.assertEqual(observed[key],value)
        self.assertEqual(page.observation.expires_at-page.observation.checked_at,timedelta(days=7))
        self.assertEqual(len(self.checks),1)
    async def test_invalid_query_and_bearer_never_check_authority_or_select(self):
        for query in ({},{**self.query,'limit':None},{**self.query,'from_date':'2026-10-27'},{**self.query,'cursor':'bad'},{**self.query,'private':'canary'}):
            with self.assertRaises(history.protected.HandlerError) as failed:await self.execute(query)
            self.assertEqual((failed.exception.status,failed.exception.error_id),(422,'validation_failed'))
        for authorization in (None,'Basic synthetic','Bearer a,b','Bearer a!b','Bearer a=b'):
            with self.assertRaises(history.protected.HandlerError) as failed:await self.execute(authorization=authorization)
            self.assertEqual((failed.exception.status,failed.exception.error_id),(401,'authentication_required'))
        self.assertEqual(self.checks,[]);self.assertEqual(self.db.calls,[])
    async def test_current_denial_and_bad_actor_precede_select(self):
        cases=[(httpx.Response(403,json={'detail':{'code':'access_denied'}}),(403,'access_denied')),
            (httpx.Response(409,json={'detail':{'code':'identity.actor_setup_required'}}),(409,'identity.actor_setup_required')),
            (httpx.Response(200,json={**support.support.evidence(history.PERMISSION),'actor_id':None}),(503,'authorization_unavailable'))]
        for response,expected in cases:
            self.upstream=lambda:response
            with self.assertRaises(history.protected.HandlerError) as failed:await self.execute()
            self.assertEqual((failed.exception.status,failed.exception.error_id),expected)
            self.assertEqual(self.db.calls,[])
    async def test_active_transaction_or_autocommit_context_never_checks_authority(self):
        for active,autocommit in ((True,False),(False,True)):
            self.db.active=active;self.db.autocommit=autocommit
            with self.assertRaises(history.protected.HandlerError) as failed:await self.execute()
            self.assertEqual((failed.exception.status,failed.exception.error_id),(500,'invalid_write_context'))
        self.assertEqual(self.checks,[]);self.assertEqual(self.db.calls,[])
    async def test_storage_sql_and_commit_failures_remain_safe(self):
        for phase in ('storage','sql','commit'):
            self.db=wire.Connection()
            if phase=='storage':self.db.rows[-1]['answers']={}
            elif phase=='sql':self.db.fail_execute=True
            else:self.db.fail_commit=True
            with self.assertRaises(history.protected.HandlerError) as failed:await self.execute()
            self.assertEqual((failed.exception.status,failed.exception.error_id),(503,'capture_read_unavailable'))
            self.assertNotIn('secret',str(failed.exception));self.assertFalse(self.db.in_transaction())
