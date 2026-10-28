"""Owner aggregate schema/runtime agreement, inert export, existing export unchanged."""
from pathlib import Path
import sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'write-candidate'),str(Path(__file__).resolve().parents[1]/'api')]
import copy
import json
import unittest
from unittest.mock import patch
import audit_display_http
import audit_display
import export_audit_display_openapi as export
import test_audit_display_http as wire
import test_create_contract as contracts

class AggregateContract(unittest.IsolatedAsyncioTestCase):
    setUp=wire.CompositionAcceptance.setUp
    make_app=wire.CompositionAcceptance.make_app
    get=wire.CompositionAcceptance.get
    asyncTearDown=wire.CompositionAcceptance.asyncTearDown
    valid=contracts.CreateContract.valid
    async def test_actual_response_and_all_safe_errors_match_owner_schema(self):
        doc=self.app.openapi();op=doc['paths'][wire.PATH.replace(wire.base.wire.support.CAPTURE,'{capture_id}')]['get']
        response=await self.get();self.assertEqual(response.status_code,200)
        shape=op['responses']['200']['content']['application/json']['schema'];value=response.json()
        self.assertTrue(self.valid(doc,shape,value))
        for field,change in (('extra',True),('actor_display',{'status':'temporarily_unavailable','labels':[]}),('actor_display',{'status':'loaded','labels':[]}),('actor_display',{'status':'loaded','labels':[{'actor_id':wire.ORG,'status':'unavailable','display_name':'forbidden'}]})):
            self.assertFalse(self.valid(doc,shape,{**value,field:change}))
        for status,error in wire.base.boundary.PAIRS:
            response=wire.base.boundary.failure(status,error)
            schema=op['responses'][str(status)]['content']['application/json']['schema']
            self.assertTrue(self.valid(doc,schema,json.loads(response.body)))
    async def test_export_current_closed_inert(self):
        with patch.object(wire.base.boundary,'_engine',side_effect=AssertionError('no_engine')):
            self.assertEqual(export.render(),export.DESTINATION.read_text())
        self.assertEqual(export.main(['--check']),0)
        doc=self.app.openapi();self.assertEqual(list(doc['paths']),['/api/v1/admin/captures/{capture_id}/audit-details'])
        models=doc['components']['schemas']
        for name in ('AuditDetails','AuditPage','AuditEvent','LoadedDisplays','UnavailableDisplays','ResolvedLabel','UnavailableLabel'):
            self.assertFalse(models[name]['additionalProperties'])
        op=next(iter(doc['paths'].values()))['get']
        self.assertEqual(op['operationId'],'audit_details');self.assertEqual(op['security'],[{'HTTPBearer':[]}])
        self.assertEqual([p['name'] for p in op['parameters']],['capture_id','limit','cursor'])
        self.assertNotIn('requestBody',op)
        for response in op['responses'].values():self.assertEqual(response['headers']['Cache-Control']['schema']['const'],'private, no-store')
