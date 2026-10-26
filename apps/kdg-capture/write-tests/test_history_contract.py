"""Owner-generated page contract and live synthetic ASGI wire agreement."""
import unittest
from unittest.mock import patch
import test_capture_read as support
import test_create_contract as contracts
import test_history_http as wire
import history_http, capture_history, export_history_openapi

class HistoryContract(unittest.IsolatedAsyncioTestCase):
    valid=contracts.CreateContract.valid
    def setUp(self):wire.HistoryAcceptance.setUp(self)
    make_app=wire.HistoryAcceptance.make_app
    async def asyncTearDown(self):await self.client.aclose()
    async def test_actual_page_empty_denial_and_validation_contracts(self):
        import httpx
        first=await wire.HistoryAcceptance.get(self)
        self.pool.connection.rows=[]
        empty=await wire.HistoryAcceptance.get(self)
        invalid=await wire.HistoryAcceptance.get(self,wire.URL+'&limit=3')
        self.upstream=lambda:httpx.Response(403,json={'detail':{'code':'access_denied'}})
        denied=await wire.HistoryAcceptance.get(self)
        doc=self.app.openapi();op=doc['paths']['/api/v1/captures']['get']
        for result in (first,empty,invalid,denied):
            shape=op['responses'][str(result.status_code)]['content']['application/json']['schema']
            self.assertTrue(self.valid(doc,shape,result.json()),result.text)
        self.assertEqual(op['operationId'],'history_captures');self.assertEqual(op['security'],[{'HTTPBearer':[]}])
        self.assertNotIn('requestBody',op)
        self.assertEqual([p['name'] for p in op['parameters']],['from_date','to_date','limit','cursor'])
        shape=op['responses']['200']['content']['application/json']['schema']
        for change in ({'limit':101},{'org_id':'bad'},{'from_date':'2026-02-30'},{'private':'canary'},{'items':[{'capture_id':support.CAPTURE}]}):
            self.assertFalse(self.valid(doc,shape,{**first.json(),**change}))
        for response in op['responses'].values():self.assertEqual(response['headers']['Cache-Control']['schema']['const'],'private, no-store')
    async def test_export_current_without_live_collaborators(self):
        with patch.object(history_http,'_engine',side_effect=AssertionError('no_engine')),patch.object(capture_history.HistoryHandler,'__init__',side_effect=AssertionError('no_authority')):
            self.assertEqual(export_history_openapi.render(),export_history_openapi.DESTINATION.read_text())
    async def test_actual_auth_setup_outage_read_failure_and_timeout_validate(self):
        import httpx
        doc=self.app.openapi();op=doc['paths']['/api/v1/captures']['get']
        results=[await wire.HistoryAcceptance.get(self,headers={})]
        for status,code in ((409,'identity.actor_setup_required'),(503,'private_upstream_canary')):
            self.upstream=lambda:httpx.Response(status,json={'detail':{'code':code}})
            results.append(await wire.HistoryAcceptance.get(self))
        self.upstream=lambda:httpx.Response(200,json=support.support.evidence(capture_history.PERMISSION))
        self.pool.connection.rows[-1]['answers']={}
        results.append(await wire.HistoryAcceptance.get(self))
        self.pool.connection.rows=[]
        original=capture_history.write.Budget
        def expired():
            budget=original();budget.deadline=budget.started_at-1;return budget
        with patch.object(capture_history.write,'Budget',side_effect=expired):
            results.append(await wire.HistoryAcceptance.get(self))
        self.assertEqual([(r.status_code,r.json()['error_id']) for r in results],[(401,'authentication_required'),(409,'identity.actor_setup_required'),(503,'authorization_unavailable'),(503,'capture_read_unavailable'),(503,'execution_timeout')])
        for result in results:
            shape=op['responses'][str(result.status_code)]['content']['application/json']['schema']
            self.assertTrue(self.valid(doc,shape,result.json()),result.text)
            self.assertEqual(result.headers['cache-control'],'private, no-store')
    async def test_response_cursor_matches_query_base64url_metadata(self):
        first=await wire.HistoryAcceptance.get(self)
        self.assertEqual(first.status_code,200)
        import json
        doc=json.loads(export_history_openapi.DESTINATION.read_text());op=doc['paths']['/api/v1/captures']['get']
        query=next(p['schema'] for p in op['parameters'] if p['name']=='cursor')
        response=next(branch for branch in doc['components']['schemas']['HistoryPage']['properties']['next_cursor']['anyOf'] if branch['type']=='string')
        for field in ('type','minLength','maxLength','pattern'):self.assertEqual(query[field],response[field])
        shape=op['responses']['200']['content']['application/json']['schema']
        for cursor in ('','bad+cursor','bad/cursor','bad=cursor','bad cursor','bad\n','x'*2049):
            self.assertFalse(self.valid(doc,shape,{**first.json(),'next_cursor':cursor}))
        self.assertTrue(self.valid(doc,shape,{**first.json(),'next_cursor':None}))
