"""Direct read-only context and independent authority-pair characterization."""
import json
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID
import httpx
import test_capture_read as support
import edit_context as context

READ='kdg_capture.capture.read.own'
EDIT='kdg_capture.capture.edit.own'
class ContextAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db=support.Connection();self.checks=[]
        self.upstream=lambda permission:httpx.Response(200,json=support.support.evidence(permission))
        async def access(request):
            self.assertEqual(self.db.calls,[])
            permission=json.loads(request.content)['permission'];self.checks.append(permission)
            return self.upstream(permission)
        self.handler=context.EditContextHandler(org_id=support.ORG,access_url='https://access.invalid',service_key='synthetic',transport=httpx.MockTransport(access))
    async def execute(self):return await self.handler.execute(self.db,support.CAPTURE,'Bearer synthetic')
    async def test_read_only_complete_original_owner_context_without_assignment(self):
        self.db.replay_assignment=None
        result=await self.execute()
        self.assertEqual(result.capture.capture_id,support.CAPTURE)
        self.assertEqual(result.capture.definition.model_dump(mode='json'),support.DEFINITION)
        self.assertEqual(result.editable_fields,('observation_date','answers'))
        self.assertEqual(self.checks,[READ,EDIT])
        self.assertFalse(any(s.startswith(('INSERT','UPDATE','DELETE')) or 'FOR UPDATE' in s for s,_ in self.db.calls))
    async def test_each_actual_decision_and_verification_time_retained(self):
        values={READ:support.support.evidence(READ),EDIT:support.support.evidence(EDIT)}
        values[EDIT]['decision_id']=support.IDS[0]
        instant=datetime.now(timezone.utc)-timedelta(milliseconds=200)
        values[READ]['checked_at']=instant.isoformat().replace('+00:00','Z')
        values[EDIT]['checked_at']=(instant+timedelta(milliseconds=100)).isoformat().replace('+00:00','Z')
        self.upstream=lambda permission:httpx.Response(200,json=values[permission])
        result=await self.execute()
        for permission,observation in [(READ,result.read_observation),(EDIT,result.edit_observation)]:
            self.assertEqual(observation.decision_id,values[permission]['decision_id'])
            self.assertEqual(observation.checked_at,datetime.fromisoformat(values[permission]['checked_at']))
            self.assertEqual(observation.expires_at-observation.checked_at,timedelta(days=7))
    async def test_pair_identity_scope_mismatch_never_enters_transaction(self):
        for change in [{'account_id':support.IDS[0]},{'actor_id':support.IDS[0]},{'membership_id':'8'},{'authorization_scope':{'kind':'organization','org_id':support.IDS[0]}},{'resource_scope':{'kind':'own_account','account_id':support.IDS[0]}},{'permission':READ},{'private':'secret'}]:
            self.upstream=lambda permission:httpx.Response(200,json={**support.support.evidence(permission),**(change if permission==EDIT else {})})
            with self.assertRaises(context.protected.HandlerError) as failed:await self.execute()
            self.assertEqual(failed.exception.error_id,'authorization_unavailable');self.assertEqual(self.db.calls,[])
    async def test_first_observation_is_not_renewed_by_second_check(self):
        now=100.0
        def upstream(permission):
            nonlocal now
            if permission==EDIT:now+=1.1
            return httpx.Response(200,json=support.support.evidence(permission))
        self.upstream=upstream
        with patch.object(context.write,'time',SimpleNamespace(monotonic=lambda:now)):
            with self.assertRaises(context.protected.HandlerError) as failed:await self.execute()
        self.assertEqual(failed.exception.error_id,'authorization_observation_expired')
        self.assertFalse(any('kdg_capture.' in sql for sql,_ in self.db.calls))
    async def test_current_actor_must_agree_with_capture_original_owner(self):
        self.db.detail['owner_actor_id']=UUID(support.IDS[0]);self.db.detail['created_by']=UUID(support.IDS[0])
        with self.assertRaises(context.protected.HandlerError) as failed:await self.execute()
        self.assertEqual(failed.exception.error_id,'capture_read_unavailable')
