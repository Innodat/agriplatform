"""Owner export and actual closed online admin context wire agreement."""
import unittest
from unittest.mock import patch
import httpx
import test_admin_edit_context_http as wire
import test_create_contract as contracts
import admin_edit_context_http as boundary
import admin_edit_context as context
import export_admin_edit_context_openapi as owner

class ContextContract(unittest.IsolatedAsyncioTestCase):
    setUp=wire.HTTPAcceptance.setUp
    asyncTearDown=wire.HTTPAcceptance.asyncTearDown
    get=wire.HTTPAcceptance.get
    valid=contracts.CreateContract.valid
    async def test_actual_success_and_all_safe_error_families_match_owner_schema(self):
        from contextlib import nullcontext
        from types import SimpleNamespace
        from sqlalchemy.exc import OperationalError
        doc=self.app.openapi();op=doc['paths']['/api/v1/admin/captures/{capture_id}/edit-context']['get']
        result=await self.get();self.assertEqual(result.status_code,200)
        shape=op['responses']['200']['content']['application/json']['schema']
        self.assertTrue(self.valid(doc,shape,result.json()))
        original=result.json()
        for change in ({'read_observation':{}},{'edit_observation':{}},{'expires_at':'2026-11-02T00:00:00Z'},{'actor_name':'private'},{'operation_id':wire.support.FOREIGN},{'editable_fields':['answers']},{'editable_fields':['answers','observation_date']},{'editable_fields':['observation_date','answers','child_id']},{'capture':{}}):
            self.assertFalse(self.valid(doc,shape,{**original,**change}),change)
        for phase,status,error in (('authentication',401,'authentication_required'),('denial',403,'access_denied'),('missing',404,'capture_unavailable'),('setup',409,'identity.actor_setup_required'),('validation',422,'validation_failed'),('context',500,'invalid_write_context'),('unexpected',500,'internal_error'),('dependency',503,'authorization_unavailable'),('storage',503,'capture_read_unavailable'),('observation',503,'authorization_observation_expired'),('deadline',503,'execution_timeout')):
            self.pool=wire.support.Pool();self.app.state.recovery_engine=self.pool
            self.upstream=lambda permission:httpx.Response(200,json=wire.direct.evidence(permission))
            scope=nullcontext();kwargs={};url=wire.URL;now=100.0
            if phase=='authentication':kwargs={'headers':{}}
            elif phase=='denial':self.upstream=lambda permission:httpx.Response(403,json={'detail':{'code':'access_denied'}})
            elif phase=='missing':self.pool.connection.detail=None
            elif phase=='setup':self.upstream=lambda permission:httpx.Response(409,json={'detail':{'code':'identity.actor_setup_required'}})
            elif phase=='validation':url+='?org_id=x'
            elif phase=='context':self.pool.connection.active=True
            elif phase=='unexpected':
                def fail():raise RuntimeError('private')
                self.pool.borrow=fail
            elif phase=='dependency':self.upstream=lambda permission:httpx.Response(503,json={'detail':{'code':'private'}})
            elif phase=='storage':
                def fail():raise OperationalError('private',{},Exception('private'))
                self.pool.borrow=fail
            elif phase=='observation':
                def stale():
                    nonlocal now
                    now+=2
                self.pool.borrow=stale;scope=patch.object(wire.write,'time',SimpleNamespace(monotonic=lambda:now))
            elif phase=='deadline':
                original_budget=wire.write.Budget
                def expired():
                    value=original_budget();value.deadline=value.started_at-1;return value
                scope=patch.object(wire.write,'Budget',side_effect=expired)
            with scope:
                if phase=='unexpected':
                    with self.assertLogs('service.operations',level='ERROR') as logs:result=await self.get(url,**kwargs)
                    self.assertNotIn('private',str(logs.output))
                else:result=await self.get(url,**kwargs)
            self.assertEqual((result.status_code,result.json()['error_id']),(status,error),phase)
            self.assertTrue(self.valid(doc,op['responses'][str(status)]['content']['application/json']['schema'],result.json()))
            self.assertNotIn('private',result.text)
    async def test_export_inert_and_single_exact_route(self):
        with patch.object(boundary,'_engine',side_effect=AssertionError('engine')),patch.object(context.AdminEditContextHandler,'__init__',side_effect=AssertionError('authority')):
            self.assertEqual(owner.render(),owner.DESTINATION.read_text())
        doc=self.app.openapi();self.assertEqual(set(doc['paths']),{'/api/v1/admin/captures/{capture_id}/edit-context'})
        op=next(iter(doc['paths'].values()))['get']
        self.assertEqual(op['operationId'],'admin_edit_context');self.assertEqual(op['security'],[{'HTTPBearer':[]}])
        self.assertNotIn('requestBody',op)
        self.assertEqual([(p['name'],p['in']) for p in op['parameters']],[('capture_id','path')])
        for value in op['responses'].values():self.assertEqual(value['headers']['Cache-Control']['schema']['const'],'private, no-store')
        models=doc['components']['schemas']
        self.assertFalse(any('Observation' in name or 'Receipt' in name or 'Command' in name for name in models))
