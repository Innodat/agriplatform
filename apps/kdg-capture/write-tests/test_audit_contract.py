"""Owner export, closed wire metadata and generated contract qualification."""
from pathlib import Path
import sys

sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'write-candidate'),str(Path(__file__).resolve().parents[1]/'api')]

import copy
import json
import unittest
from unittest.mock import patch
import httpx
import audit_http
import audit_read
import export_audit_openapi
import test_audit_http as wire
import test_create_contract as contracts

class AuditContract(unittest.IsolatedAsyncioTestCase):
    valid=contracts.CreateContract.valid
    setUp=wire.AuditAcceptance.setUp
    make_app=wire.AuditAcceptance.make_app
    get=wire.AuditAcceptance.get
    asyncTearDown=wire.AuditAcceptance.asyncTearDown
    async def test_actual_page_and_safe_error_families_match_owner_schema(self):
        doc=self.app.openapi();op=doc['paths']['/api/v1/admin/captures/{capture_id}/events']['get']
        samples=[await self.get(),await self.get(headers={}),await self.get(content=b'private')]
        self.pool.connection.missing=True;samples.append(await self.get());self.pool.connection.missing=False
        for status,error in ((403,'access_denied'),(409,'identity.actor_setup_required'),(503,'private-upstream')):
            self.upstream=lambda:httpx.Response(status,json={'detail':{'code':error}})
            samples.append(await self.get())
        for response in samples:
            shape=op['responses'][str(response.status_code)]['content']['application/json']['schema']
            self.assertTrue(self.valid(doc,shape,response.json()),response.text)
        for status,error in audit_http.PAIRS:
            response=audit_http.failure(status,error)
            shape=op['responses'][str(status)]['content']['application/json']['schema']
            self.assertTrue(self.valid(doc,shape,json.loads(response.body)),(status,error))
        shape=op['responses']['200']['content']['application/json']['schema'];page=samples[0].json()
        for change in ({'answers':{}},{'observation':{}},{'definition':{}},{'operation_id':wire.wire.FOREIGN},{'current_revision':'0'},{'limit':101},{'account_id':'bad'},{'next_cursor':'bad='}):
            self.assertFalse(self.valid(doc,shape,{**page,**change}),change)
        for change in ({'revision':True},{'revision':'9223372036854775808'},{'executor_actor_id':None},{'initiator_actor_id':'bad'},{'recorded_at':'2026-02-30T00:00:00Z'},{'answers':{}},{'command_type':'capture.delete'}):
            candidate=copy.deepcopy(page);candidate['events'][0].update(change)
            self.assertFalse(self.valid(doc,shape,candidate),change)
    async def test_export_is_current_inert_and_closed(self):
        with patch.object(audit_http,'_engine',side_effect=AssertionError('no_engine')),patch.object(audit_read.AuditReadHandler,'__init__',side_effect=AssertionError('no_access')):
            self.assertEqual(export_audit_openapi.render(),export_audit_openapi.DESTINATION.read_text())
        self.assertEqual(export_audit_openapi.main(['--check']),0)
        doc=self.app.openapi();self.assertEqual(set(doc['paths']),{'/api/v1/admin/captures/{capture_id}/events'})
        op=next(iter(doc['paths'].values()))['get']
        self.assertEqual(op['security'],[{'HTTPBearer':[]}]);self.assertNotIn('requestBody',op)
        self.assertEqual([p['name'] for p in op['parameters']],['capture_id','limit','cursor'])
        for response in op['responses'].values():self.assertEqual(response['headers']['Cache-Control']['schema']['const'],'private, no-store')
        models=doc['components']['schemas']
        self.assertFalse(models['AuditPage']['additionalProperties']);self.assertFalse(models['AuditEvent']['additionalProperties'])
        self.assertEqual(set(models['AuditPage']['properties']),set(audit_read.AuditPage.model_fields))
        self.assertEqual(set(models['AuditEvent']['properties']),set(audit_read.AuditEvent.model_fields))
        for forbidden in ('CaptureDetail','OwnReadObservation','QuestionnaireDefinition','TextAnswer'):self.assertNotIn(forbidden,models)
