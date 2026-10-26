"""Direct original-admin context and independently verified all-capability pair."""
import copy
from datetime import date, datetime, timezone
import json
from types import SimpleNamespace
from unittest.mock import patch
import unittest
from uuid import UUID
import httpx
import test_admin_http as support
import admin_edit_context as context

READ='kdg_capture.capture.read.all'
EDIT='kdg_capture.capture.edit.all'
def evidence(permission):return {**support.evidence(),'permission':permission}

class ContextAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db=support.Connection();self.checks=[]
        self.upstream=lambda permission:httpx.Response(200,json=evidence(permission))
        async def access(request):
            self.assertEqual(self.db.calls,[])
            permission=json.loads(request.content)['permission'];self.checks.append(permission)
            return self.upstream(permission)
        self.handler=context.AdminEditContextHandler(org_id=support.support.ORG,access_url='https://access.invalid',service_key='synthetic',transport=httpx.MockTransport(access))
    async def execute(self,capture_id=support.support.CAPTURE,authorization='Bearer synthetic'):
        return await self.handler.execute(self.db,capture_id,authorization)
    async def test_foreign_original_context_is_closed_and_readonly(self):
        self.db.replay_assignment=None
        question='99999999-9999-4999-8999-999999999999'
        self.db.detail.update(owner_actor_id=UUID(support.FOREIGN),created_by=UUID(support.FOREIGN),
            revision=7,questionnaire_version=4,observation_date=date(2026,10,25),
            updated_at=datetime(2026,10,26,12,30,tzinfo=timezone.utc),
            definition={'schema_version':1,'questions':[{'id':question,'type':'text','label':'Original question','required':True}]},
            answers={question:{'value':'Original answer'}})
        result=await self.execute()
        self.assertEqual(set(result.model_dump()),{'capture','editable_fields'})
        # Specify every original wire field independently of the DTO/normalizer.
        self.assertEqual(result.capture.model_dump(mode='json'),{
            'capture_id':support.support.CAPTURE,'org_id':support.support.ORG,
            'owner_account_id':support.FOREIGN,'owner_actor_id':support.FOREIGN,
            'child_id':'11111111-1111-4111-8111-111111111111','child_label':'Original child',
            'questionnaire_id':'11111111-1111-4111-8111-111111111112',
            'questionnaire_version_id':'11111111-1111-4111-8111-111111111113',
            'questionnaire_version':'4','revision':'7','observation_date':'2026-10-25',
            'definition':{'schema_version':1,'questions':[{'id':'99999999-9999-4999-8999-999999999999','type':'text','label':'Original question','required':True}]},
            'answers':{'99999999-9999-4999-8999-999999999999':{'value':'Original answer'}},
            'captured_at':'2026-10-26t10:00:00z','created_by':support.FOREIGN,
            'created_at':'2026-10-26T00:00:00Z','updated_by':support.support.ACTOR,
            'updated_at':'2026-10-26T12:30:00Z'})
        self.assertEqual(result.editable_fields,('observation_date','answers'))
        self.assertEqual(self.checks,[READ,EDIT])
        modes=[p['mode'] for sql,p in self.db.calls if "set_config('app.mode'" in sql]
        self.assertEqual(modes,['all_read'])
        self.assertFalse(any(sql.startswith(('INSERT','UPDATE','DELETE')) or 'FOR UPDATE' in sql for sql,_ in self.db.calls))
    async def test_each_check_rejects_bad_decisions_without_sql(self):
        changes=[{'account_id':support.FOREIGN},{'actor_id':support.FOREIGN},{'membership_id':'8'},
            {'authorization_scope':{'kind':'organization','org_id':support.FOREIGN}},
            {'resource_scope':{'kind':'organization','org_id':support.FOREIGN}},
            {'resource_scope':{'kind':'own_account','account_id':support.support.ACCOUNT}},
            {'checked_at':'2020-01-01T00:00:00Z'},{'permission':'kdg_capture.capture.edit.own'},{'private':'secret'}]
        for selected in (READ,EDIT):
            for change in changes:
                self.upstream=lambda permission:httpx.Response(200,json={**evidence(permission),**(change if permission==selected else {})})
                with self.assertRaises(context.protected.HandlerError) as failed:await self.execute()
                self.assertEqual(failed.exception.error_id,'authorization_unavailable',change)
                self.assertEqual(self.db.calls,[])
        for selected in (READ,EDIT):
            for field in evidence(selected):
                self.upstream=lambda permission:httpx.Response(200,json={**evidence(permission),**({field:None} if permission==selected else {})})
                with self.assertRaises(context.protected.HandlerError):await self.execute()
                self.assertEqual(self.db.calls,[])
    async def test_first_observation_not_renewed_by_second_check(self):
        now=100.0
        def upstream(permission):
            nonlocal now
            if permission==EDIT:now+=1.1
            return httpx.Response(200,json=evidence(permission))
        self.upstream=upstream
        with patch.object(context.write,'time',SimpleNamespace(monotonic=lambda:now)):
            with self.assertRaises(context.protected.HandlerError) as failed:await self.execute()
        self.assertEqual(failed.exception.error_id,'authorization_observation_expired')
        self.assertFalse(any('kdg_capture.' in sql for sql,_ in self.db.calls))
    async def test_validation_after_committed_read(self):
        original=context.admin._snapshot
        def validate(*args):
            self.assertFalse(self.db.in_transaction());self.assertEqual(self.db.calls[-1][0],'COMMIT')
            return original(*args)
        with patch.object(context.admin,'_snapshot',side_effect=validate):await self.execute()
    async def test_missing_foreign_and_invalid_storage(self):
        original=copy.deepcopy(self.db.detail)
        for value,status in ((None,404),({**original,'org_id':UUID(support.FOREIGN)},404),({**original,'capture_id':UUID(support.FOREIGN)},404),({**original,'answers':{}},503),({**original,'created_by':UUID(support.FOREIGN)},503)):
            self.db.detail=value;self.db.calls=[]
            with self.assertRaises(context.protected.HandlerError) as failed:await self.execute()
            self.assertEqual(failed.exception.status,status)
    async def test_invalid_input_authentication_and_connection_context(self):
        for capture_id in ('bad',None):
            with self.assertRaises(context.protected.HandlerError) as failed:await self.execute(capture_id)
            self.assertEqual(failed.exception.status,422)
        for token in (None,'Basic private','Bearer a,b','Bearer a=b'):
            with self.assertRaises(context.protected.HandlerError) as failed:await self.execute(authorization=token)
            self.assertEqual(failed.exception.status,401)
        for active,autocommit in ((True,False),(False,True)):
            self.db.active=active;self.db.autocommit=autocommit
            with self.assertRaises(context.protected.HandlerError) as failed:await self.execute()
            self.assertEqual(failed.exception.error_id,'invalid_write_context')
        self.assertEqual((self.checks,self.db.calls),([],[]))
