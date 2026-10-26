"""Offline generated-schema and actual own-read wire agreement."""
from copy import deepcopy
import json
import subprocess
import sys
from pathlib import Path
import unittest
import read_http
import capture_read
import test_capture_read as support
import test_create_contract as contract_support

class ReadContract(unittest.TestCase):
    valid=contract_support.CreateContract.valid
    def setUp(self):
        self.doc=read_http._create_app(None,None,None).openapi()
        self.op=self.doc['paths']['/api/v1/captures/{capture_id}']['get']
        context=capture_read.write.VerifiedContext(support.ORG,support.ACCOUNT,support.ACTOR,'own_read',100)
        self.value=capture_read._snapshot(support.row(),context,capture_read.Lookup(capture_id=support.CAPTURE)).model_dump(mode='json')
        self.shape=self.op['responses']['200']['content']['application/json']['schema']
    def test_detail_closed_ids_revisions_original_definition_and_private_metadata(self):
        self.assertTrue(self.valid(self.doc,self.shape,self.value))
        self.assertEqual(self.op['operationId'],'read_capture')
        self.assertEqual(self.op['security'],[{'HTTPBearer':[]}])
        self.assertNotIn('requestBody',self.op)
        for change in ({'revision':'1\n'},{'questionnaire_version':'9223372036854775808'},{'owner_actor_id':'bad'},{'child_label':' '},{'child_label':'\ud800'},{'private':'canary'}):
            self.assertFalse(self.valid(self.doc,self.shape,{**self.value,**change}))
        for response in self.op['responses'].values():self.assertEqual(response['headers']['Cache-Control']['schema']['const'],'private, no-store')
    def test_calendar_utc_answer_keys_and_hidden_details(self):
        for field,value in [('observation_date','2026-02-30'),('created_at','2026-10-26T25:00:00Z'),('captured_at','2026-10-26T10:00:00+02:00')]:
            self.assertFalse(self.valid(self.doc,self.shape,{**self.value,field:value}))
        for answer in ({'bad':{'value':1}},{support.IDS[0]:{'value':False,'details':'hidden'}},{support.IDS[0]:{'value':True,'details':None}},{support.IDS[0]:{'value':'\ud800'}}):
            self.assertFalse(self.valid(self.doc,self.shape,{**self.value,'answers':answer}))
        for definition in [dict(schema_version=1,questions=[dict(id=support.IDS[0],type='boolean',label='Label',required=True,default=False,details_enabled=True)]),dict(schema_version=1,questions=[dict(id=support.IDS[0],type='text',label='\x00',required=True)])]:
            self.assertFalse(self.valid(self.doc,self.shape,{**self.value,'definition':definition}))
    def test_python_nonblank_semantics_match_schema_for_labels_and_text_answers(self):
        from capture_commands import EditCommand, validate_answers, CommandError
        from questionnaire import parse_definition, DefinitionError
        for value,expected in [('',False),(' ',False),('\ufeff',True),('\x85',False),('\x1c',False),('\x85\x1c ',False),('\ufeff\x85',True)]:
            with self.subTest(value=ascii(value)):
                body=deepcopy(self.value)
                qid=support.IDS[0]
                body.update(child_label=value,definition=dict(schema_version=1,questions=[dict(id=qid,type='text',label=value,required=True)]),answers={qid:{'value':value}})
                self.assertEqual(self.valid(self.doc,self.shape,body),expected)
                context=capture_read.write.VerifiedContext(support.ORG,support.ACCOUNT,support.ACTOR,'own_read',100)
                stored={**support.row(),'child_label':value,'definition':body['definition'],'answers':body['answers']}
                try:capture_read._snapshot(stored,context,capture_read.Lookup(capture_id=support.CAPTURE));valid=True
                except capture_read.write.WriteError:valid=False
                self.assertEqual(valid,expected)
                # Isolate TextAnswer's nonblank constraint from the label constraints.
                body['child_label']='Child';body['definition']['questions'][0]['label']='Question'
                self.assertEqual(self.valid(self.doc,self.shape,body),expected)

    def test_status_error_families_are_closed(self):
        for status,code in read_http.PAIRS:
            shape=self.op['responses'][str(status)]['content']['application/json']['schema']
            self.assertTrue(self.valid(self.doc,shape,dict(error='Safe',error_id=code)))
            self.assertFalse(self.valid(self.doc,shape,dict(error='Safe',error_id=code,private='canary')))
    def test_export_is_current_and_does_not_construct_live_collaborators(self):
        from unittest.mock import patch
        import export_read_openapi
        with patch.object(read_http,'_engine',side_effect=AssertionError('engine forbidden')),patch.object(capture_read.ReadHandler,'__init__',side_effect=AssertionError('authority forbidden')):
            self.assertEqual(export_read_openapi.render(),export_read_openapi.DESTINATION.read_text())

class ReadWireContract(unittest.IsolatedAsyncioTestCase):
    valid=contract_support.CreateContract.valid
    def setUp(self):
        from test_read_http import HTTPAcceptance
        HTTPAcceptance.setUp(self)
    async def asyncTearDown(self):await self.client.aclose()
    async def test_actual_success_missing_and_denial_validate(self):
        import httpx
        from test_read_http import HTTPAcceptance
        results=[await HTTPAcceptance.get(self)]
        self.pool.borrows=0;self.pool.connection.detail=None
        results.append(await HTTPAcceptance.get(self));self.pool.borrows=0
        self.upstream=lambda:httpx.Response(403,json={'detail':{'code':'access_denied'}})
        results.append(await HTTPAcceptance.get(self))
        self.assertEqual([r.status_code for r in results],[200,404,403])
        doc=self.app.openapi();op=doc['paths']['/api/v1/captures/{capture_id}']['get']
        for result in results:self.assertTrue(self.valid(doc,op['responses'][str(result.status_code)]['content']['application/json']['schema'],result.json()))
