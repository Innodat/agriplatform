"""Exact inert owner export and actual write/recovery response schemas."""
import json
import unittest
from unittest.mock import patch
import test_admin_edit_http as wire
import test_create_contract as contracts
import admin_edit as edit
import admin_edit_http as boundary
import export_admin_edit_openapi as owner

class AdminEditContract(unittest.IsolatedAsyncioTestCase):
    setUp=wire.HTTPAcceptance.setUp
    asyncTearDown=wire.HTTPAcceptance.asyncTearDown
    put=wire.HTTPAcceptance.put
    get=wire.HTTPAcceptance.get
    valid=contracts.CreateContract.valid
    async def test_success_conflict_and_recovery_closed_wire_shapes(self):
        doc=self.app.openapi();put=doc['paths']['/api/v1/admin/captures/{capture_id}']['put'];get=doc['paths']['/api/v1/admin/operations/{operation_id}']['get']
        for operation,request in ((put,self.put),(get,self.get)):
            result=await request();schema=operation['responses']['200']['content']['application/json']['schema']
            self.assertTrue(self.valid(doc,schema,result.json()))
            for extra in ('owner_account_id','answers','read_observation','edit_observation','actor_name','authority','expires_at'):
                self.assertFalse(self.valid(doc,schema,{**result.json(),extra:'private'}))
        result=await self.put(json=wire.own.body.command(expected_revision='3').model_dump())
        schema=put['responses']['409']['content']['application/json']['schema']
        self.assertTrue(self.valid(doc,schema,result.json()))
        self.assertFalse(self.valid(doc,schema,{**result.json(),'answers':{}}))
        self.assertFalse(self.valid(doc,schema,{**result.json(),'current_revision':'0'}))
        self.read_pool.connection.existing=wire.own.stored()
        result=await self.get();schema=get['responses']['200']['content']['application/json']['schema']
        self.assertTrue(self.valid(doc,schema,result.json()))
        self.assertFalse(self.valid(doc,schema,{**result.json(),'command_type':'capture.create'}))
    async def test_exact_routes_and_original_closed_command(self):
        doc=self.app.openapi();self.assertEqual(set(doc['paths']),{'/api/v1/admin/captures/{capture_id}','/api/v1/admin/operations/{operation_id}'})
        command=doc['components']['schemas']['EditCommand'];original=wire.own.body.command().model_dump()
        self.assertTrue(self.valid(doc,command,original))
        for key in ('owner_account_id','actor_id','org_id','child_id','questionnaire_version_id','force','read_observation'):
            self.assertFalse(self.valid(doc,command,{**original,key:'private'}),key)
        for path,methods in doc['paths'].items():
            for op in methods.values():
                self.assertEqual(op['security'],[{'HTTPBearer':[]}])
                for response in op['responses'].values():self.assertEqual(response['headers']['Cache-Control']['schema']['const'],'private, no-store')
        get=doc['paths']['/api/v1/admin/operations/{operation_id}']['get']
        self.assertNotIn('requestBody',get)
        self.assertEqual([(p['name'],p['in']) for p in get['parameters']],[('operation_id','path'),('command_type','query')])
        self.assertEqual(get['parameters'][1]['schema']['const'],'capture.edit')
    async def test_export_is_inert_and_exact(self):
        with patch.object(boundary,'_engine',side_effect=AssertionError('engine')),patch.object(edit.authority.AdminEditContextHandler,'__init__',side_effect=AssertionError('authority')):
            self.assertEqual(owner.render(),owner.DESTINATION.read_text())
        self.assertEqual(json.loads(owner.render()),self.app.openapi())
