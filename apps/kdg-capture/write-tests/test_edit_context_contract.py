"""Owner schema/export agrees with actual candidate wire contexts and safe errors."""
import unittest
from unittest.mock import patch
import httpx
import test_edit_context_http as wire
import test_create_contract as contracts
import edit_context_http, edit_context, export_edit_context_openapi

class ContextContract(unittest.IsolatedAsyncioTestCase):
    setUp=wire.HTTPAcceptance.setUp
    asyncTearDown=wire.HTTPAcceptance.asyncTearDown
    get=wire.HTTPAcceptance.get
    async def test_actual_closed_success_and_errors_validate(self):
        valid=contracts.CreateContract.valid
        doc=self.app.openapi();op=doc['paths'][wire.URL.replace(wire.OPERATION,'{capture_id}')]['get']
        results=[await self.get(),await self.get(headers={}),await self.get(wire.URL+'?org_id=x')]
        self.upstream=lambda permission:httpx.Response(403,json={'detail':{'code':'access_denied'}})
        self.pool.borrows=0
        results.append(await self.get())
        self.assertEqual([r.status_code for r in results],[200,401,422,403])
        for result in results:
            self.assertTrue(valid(self,doc,op['responses'][str(result.status_code)]['content']['application/json']['schema'],result.json()),result.text)
        value=results[0].json();shape=op['responses']['200']['content']['application/json']['schema']
        for change in ({'extra':'private'},{'editable_fields':['answers']},{'capture':{}},{'edit_observation':value['read_observation']}):
            self.assertFalse(valid(self,doc,shape,{**value,**change}))
        self.assertEqual(op['operationId'],'read_edit_context');self.assertNotIn('requestBody',op)
    async def test_owner_export_without_live_collaborators(self):
        with patch.object(edit_context_http,'_engine',side_effect=AssertionError('no_engine')),patch.object(edit_context.EditContextHandler,'__init__',side_effect=AssertionError('no_authority')):
            self.assertEqual(export_edit_context_openapi.render(),export_edit_context_openapi.DESTINATION.read_text())

    async def test_observation_metadata_rejects_noncanonical_membership_and_timestamps(self):
        import json
        doc=json.loads(export_edit_context_openapi.render())
        model=doc['components']['schemas']['OwnEditObservation']
        valid=contracts.CreateContract.valid
        for field,value in [('membership_id','7\n'),('checked_at','2026-10-26T10:00:00+00:00'),('checked_at','2026-10-26T12:00:00+02:00'),('expires_at','2026-11-02T10:00:00+00:00'),('expires_at','2026-11-02T10:00:00Z\n')]:
            with self.subTest(field=field,value=value):
                self.assertFalse(valid(self,doc,model['properties'][field],value))
        for name in ('OwnReadObservation','OwnEditObservation'):
            if name not in doc['components']['schemas']:continue
            props=doc['components']['schemas'][name]['properties']
            for field,title in [('account_id','Account Id'),('actor_id','Actor Id'),('decision_id','Decision Id')]:
                self.assertEqual(props[field]['title'],title)
                for value in ['00000000-0000-0000-0000-000000000000','11111111-1111-4111-8111-111111111111\n']:
                    self.assertFalse(valid(self,doc,props[field],value))

    async def test_actual_remaining_safe_error_families_validate(self):
        from contextlib import nullcontext
        from types import SimpleNamespace
        from sqlalchemy.exc import OperationalError
        valid=contracts.CreateContract.valid
        doc=self.app.openapi();op=doc['paths'][wire.URL.replace(wire.OPERATION,'{capture_id}')]['get']
        cases=[('missing',404,'capture_unavailable'),('setup',409,'identity.actor_setup_required'),('context',500,'invalid_write_context'),('unexpected',500,'internal_error'),('dependency',503,'authorization_unavailable'),('storage',503,'capture_read_unavailable'),('observation',503,'authorization_observation_expired'),('deadline',503,'execution_timeout')]
        for phase,status,error_id in cases:
            with self.subTest(phase=phase):
                self.pool=wire.Pool();self.app.state.recovery_engine=self.pool
                self.upstream=lambda permission:httpx.Response(200,json=wire.support.support.evidence(permission))
                scope=nullcontext();now=100.0
                if phase=='missing':self.pool.connection.detail=None
                elif phase=='setup':self.upstream=lambda permission:httpx.Response(409,json={'detail':{'code':'identity.actor_setup_required'}})
                elif phase=='context':scope=patch.object(self.pool.connection,'in_transaction',return_value=True)
                elif phase=='unexpected':
                    def fail():raise RuntimeError('private-failure')
                    self.pool.borrow=fail
                elif phase=='dependency':self.upstream=lambda permission:httpx.Response(503,json={'detail':{'code':'private-dependency'}})
                elif phase=='storage':
                    def fail():raise OperationalError('private',{},Exception('private'))
                    self.pool.borrow=fail
                elif phase=='observation':
                    def stale():
                        nonlocal now
                        now+=2
                    self.pool.borrow=stale
                    scope=patch.object(wire.write,'time',SimpleNamespace(monotonic=lambda:now))
                elif phase=='deadline':
                    original=wire.write.Budget
                    def expired():
                        budget=original();budget.deadline=budget.started_at-1;return budget
                    scope=patch.object(wire.write,'Budget',side_effect=expired)
                with scope:
                    if phase=='unexpected':
                        with self.assertLogs('service.operations',level='ERROR'):result=await self.get()
                    else:result=await self.get()
                self.assertEqual((result.status_code,result.json()['error_id']),(status,error_id))
                self.assertEqual(result.headers['cache-control'],'private, no-store')
                self.assertTrue(valid(self,doc,op['responses'][str(status)]['content']['application/json']['schema'],result.json()))
                self.assertNotIn('private',result.text)
