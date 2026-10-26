"""Owner export and actual synthetic responses agree; no live schema collaborators."""
import json
import unittest
from unittest.mock import patch
import httpx
import test_admin_http as wire
import test_create_contract as contracts
import admin_http, admin_read, export_admin_openapi

class AdminContract(unittest.IsolatedAsyncioTestCase):
    valid=contracts.CreateContract.valid
    setUp=wire.AdminAcceptance.setUp
    make_app=wire.AdminAcceptance.make_app
    get=wire.AdminAcceptance.get
    asyncTearDown=wire.AdminAcceptance.asyncTearDown
    async def test_actual_detail_history_and_safe_failures_validate(self):
        doc=self.app.openapi()
        detail=await self.get();page=await self.get(wire.HISTORY)
        self.pool.connection.rows=[]
        empty=await self.get(wire.HISTORY)
        samples=[(wire.DETAIL,detail),(wire.HISTORY,page),(wire.HISTORY,empty)]
        for path in (wire.DETAIL,wire.HISTORY):
            samples.append((path,await self.get(path,headers={})))
            samples.append((path,await self.get(path,content=b'private')))
            for status,error in ((403,'access_denied'),(409,'identity.actor_setup_required'),(503,'private-upstream')):
                self.upstream=lambda:httpx.Response(status,json={'detail':{'code':error}})
                samples.append((path,await self.get(path)))
            self.upstream=lambda:httpx.Response(200,json=wire.evidence())
        for url,result in samples:
            path='/api/v1/admin/captures' if '?' in url else '/api/v1/admin/captures/{capture_id}'
            op=doc['paths'][path]['get']
            shape=op['responses'][str(result.status_code)]['content']['application/json']['schema']
            self.assertTrue(self.valid(doc,shape,result.json()),result.text)
        self.assertEqual(set(doc['paths']),{'/api/v1/admin/captures','/api/v1/admin/captures/{capture_id}'})
        for path,entry in doc['paths'].items():
            op=entry['get'];self.assertEqual(op['security'],[{'HTTPBearer':[]}]);self.assertNotIn('requestBody',op)
            for result in op['responses'].values():self.assertEqual(result['headers']['Cache-Control']['schema']['const'],'private, no-store')
        self.assertNotIn('OwnReadObservation',doc['components']['schemas'])
        props=doc['components']['schemas']['AdminHistoryPage']['properties']
        self.assertEqual(set(props),{'org_id','account_id','from_date','to_date','limit','items','next_cursor'})
        shape=doc['paths']['/api/v1/admin/captures']['get']['responses']['200']['content']['application/json']['schema']
        for change in ({'observation':{}},{'expires_at':'2026-11-02T00:00:00Z'},{'limit':101},{'account_id':'bad'},{'from_date':'2026-02-30'},{'next_cursor':'x='},{'items':[{}]}):
            self.assertFalse(self.valid(doc,shape,{**page.json(),**change}))
    async def test_export_fresh_and_no_engine_or_access_constructor(self):
        with patch.object(admin_http,'_engine',side_effect=AssertionError('no_engine')),patch.object(admin_read.AdminReadHandler,'__init__',side_effect=AssertionError('no_authority')):
            self.assertEqual(export_admin_openapi.render(),export_admin_openapi.DESTINATION.read_text())
        self.assertEqual(export_admin_openapi.main(['--check']),0)
    async def test_detail_schema_matches_original_owner_metadata_and_cursor_closed(self):
        import export_read_openapi
        doc=json.loads(export_admin_openapi.render());own=json.loads(export_read_openapi.render())
        for name in ('CaptureDetail','QuestionnaireDefinition','TextAnswer','BooleanAnswer','RatingAnswer'):
            self.assertEqual(doc['components']['schemas'][name],own['components']['schemas'][name])
        page=doc['components']['schemas']['AdminHistoryPage']
        self.assertFalse(page['additionalProperties'])
        op=doc['paths']['/api/v1/admin/captures']['get']
        self.assertEqual([item['name'] for item in op['parameters']],['from_date','to_date','limit','cursor'])
        query=op['parameters'][-1]['schema']
        response=next(branch for branch in page['properties']['next_cursor']['anyOf'] if branch['type']=='string')
        for field in ('type','minLength','maxLength','pattern'):self.assertEqual(query[field],response[field])
    async def test_actual_missing_internal_expired_and_timeout_errors_validate(self):
        from types import SimpleNamespace
        doc=self.app.openapi();samples=[]
        stored=self.pool.connection.detail
        self.pool.connection.detail=None
        missing=await self.get()
        self.assertEqual((missing.status_code,missing.json()['error_id']),(404,'capture_unavailable'))
        samples.append((wire.DETAIL,missing))
        self.pool.connection.detail=stored
        for path in (wire.DETAIL,wire.HISTORY):
            def unexpected():raise RuntimeError('private_contract_canary')
            with patch.object(self.pool,'borrow',side_effect=unexpected),self.assertLogs('service.operations',level='ERROR') as logs:
                internal=await self.get(path)
            self.assertEqual((internal.status_code,internal.json()['error_id']),(500,'internal_error'))
            self.assertNotIn('private_contract_canary',str(logs.output)+internal.text)
            samples.append((path,internal))
            now=100.0
            def slow_checkout():
                nonlocal now
                now+=2
            with patch.object(admin_read.write,'time',SimpleNamespace(monotonic=lambda:now)),patch.object(self.pool,'borrow',side_effect=slow_checkout):
                expired=await self.get(path)
            self.assertEqual((expired.status_code,expired.json()['error_id']),(503,'authorization_observation_expired'))
            samples.append((path,expired))
            original=admin_read.write.Budget
            def expired_budget():
                budget=original();budget.deadline=budget.started_at-1;return budget
            with patch.object(admin_read.write,'Budget',side_effect=expired_budget):timeout=await self.get(path)
            self.assertEqual((timeout.status_code,timeout.json()['error_id']),(503,'execution_timeout'))
            samples.append((path,timeout))
        for url,result in samples:
            path='/api/v1/admin/captures' if '?' in url else '/api/v1/admin/captures/{capture_id}'
            shape=doc['paths'][path]['get']['responses'][str(result.status_code)]['content']['application/json']['schema']
            self.assertTrue(self.valid(doc,shape,result.json()),result.text)
            self.assertEqual(result.headers['cache-control'],'private, no-store')
