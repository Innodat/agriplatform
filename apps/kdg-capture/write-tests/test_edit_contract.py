"""Candidate edit schema follows validated runtime wire shapes."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'write-candidate'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api'))
from fastapi import FastAPI
from safe_errors import ErrorEnvelope
from operation_outcomes import CaptureReceipt
from capture_commands import Revision, parse_edit, CommandError
import edit_openapi

PAIRS={(401,'authentication_required'),(403,'access_denied'),(404,'capture_unavailable'),
    (409,'kdg_capture.capture_revision_conflict'),(409,'identity.actor_setup_required'),
    (422,'validation_failed'),(422,'unsupported_command_version'),(500,'internal_error'),
    (503,'authorization_unavailable')}
class EditConflict(ErrorEnvelope):
    current_revision:Revision

def schema():
    app=FastAPI()
    @app.put('/api/v1/captures/{capture_id}',response_model=CaptureReceipt,
        responses={status:{'model':ErrorEnvelope} for status,_ in PAIRS})
    def edit_capture(capture_id:str):pass
    return edit_openapi.schema_for(app,PAIRS)

class EditContract(unittest.TestCase):
    def valid(self,doc,shape,value):
        tool=Path(__file__).resolve().parents[1]/'tests/validate_recovery_schema.py'
        result=subprocess.run(['/usr/bin/python3','-I','-B',str(tool)],input=json.dumps(dict(
            document=doc,schema=shape,value=value)),text=True,capture_output=True,timeout=5)
        self.assertEqual(result.returncode,0,'qualified schema validator must run')
        return json.loads(result.stdout)['valid']
    def test_closed_request_path_bearer_and_private_response_metadata(self):
        doc=schema();op=doc['paths']['/api/v1/captures/{capture_id}']['put']
        self.assertEqual(op['operationId'],'edit_capture')
        self.assertEqual(op['security'],[{'HTTPBearer':[]}])
        path=op['parameters'][0]
        self.assertEqual((path['name'],path['in'],path['required']),('capture_id','path',True))
        self.assertTrue(op['requestBody']['required'])
        shape=op['requestBody']['content']['application/json']['schema']
        body=dict(operation_id='11111111-1111-4111-8111-111111111111',command_version=1,
            expected_revision='1',observation_date='2026-10-25',answers={})
        self.assertTrue(self.valid(doc,shape,body))
        for change in ({'capture_id':body['operation_id']},{'command_version':2},{'expected_revision':1}):
            self.assertFalse(self.valid(doc,shape,dict(body,**change)))
        for response in op['responses'].values():
            self.assertEqual(response['headers']['Cache-Control']['schema']['const'],'private, no-store')
    def test_populated_answer_schema_agrees_with_runtime_structural_parser(self):
        from uuid import UUID
        doc=schema();shape=doc['paths']['/api/v1/captures/{capture_id}']['put']['requestBody']['content']['application/json']['schema']
        ids=[str(UUID(int=i+1)) for i in range(51)]
        body=dict(operation_id=ids[0],command_version=1,expected_revision='1',
            observation_date='2026-10-25',answers={})
        cases=[(True,{ids[0]:{'value':3}}),(True,{ids[0]:{'value':False}}),
            (True,{ids[0]:{'value':True}}),(True,{ids[0]:{'value':True,'details':'méér'}}),
            (True,{ids[0]:{'value':'text'}}),(True,{ids[0]:{'value':''}}),
            (True,{ids[0]:{'value':3},ids[1]:{'value':False},ids[2]:{'value':'text'}}),
            (False,{ids[0]:{'value':False,'details':'hidden'}}),
            (False,{ids[0]:{'value':False,'details':None}}),
            (False,{ids[0]:{'value':True,'details':None}}),
            (False,{ids[0]:{'value':'nul\x00text'}}),
            (False,{ids[0]:{'value':True,'details':'nul\x00text'}}),
            (False,{'invalid-key':{'value':3}}),
            (False,{'00000000-0000-0000-0000-000000000000':{'value':3}}),
            (False,{key:{'value':'text'} for key in ids}),
            (False,{ids[0]:{'value':True,'unknown':'content'}})]
        for expected,answers in cases:
            with self.subTest(answers=answers):
                value=dict(body,answers=answers)
                try:parse_edit(json.dumps(value));runtime=True
                except CommandError:runtime=False
                self.assertEqual(runtime,expected)
                self.assertEqual(self.valid(doc,shape,value),runtime)
    def test_conflict_requires_only_typed_metadata_and_code_specific_errors(self):
        doc=schema();op=doc['paths']['/api/v1/captures/{capture_id}']['put']
        shape=op['responses']['409']['content']['application/json']['schema']
        conflict=dict(error='Safe message',error_id='kdg_capture.capture_revision_conflict',current_revision='4')
        self.assertTrue(self.valid(doc,shape,conflict))
        for bad in ({k:v for k,v in conflict.items() if k!='current_revision'},
            dict(conflict,current_revision=4),dict(conflict,current_revision='9223372036854775808'),
            dict(conflict,answers={}),dict(conflict,error_id='identity.actor_setup_required')):
            self.assertFalse(self.valid(doc,shape,bad))
        self.assertTrue(self.valid(doc,shape,dict(error='Safe message',error_id='identity.actor_setup_required')))
        self.assertFalse(self.valid(doc,op['responses']['403']['content']['application/json']['schema'],
            dict(error='Safe message',error_id='authorization_unavailable')))
    def test_success_is_edit_only_and_revision_remains_bounded_string(self):
        doc=schema();op=doc['paths']['/api/v1/captures/{capture_id}']['put']
        shape=op['responses']['200']['content']['application/json']['schema']
        receipt=dict(operation_id='11111111-1111-4111-8111-111111111111',command_type='capture.edit',
            command_version=1,status='committed',result=dict(capture_id='22222222-2222-4222-8222-222222222222',revision='4'))
        self.assertTrue(self.valid(doc,shape,receipt))
        for bad in (dict(receipt,command_type='capture.create'),dict(receipt,command_version=2),
            dict(receipt,result=dict(receipt['result'],revision='9223372036854775808'))):
            self.assertFalse(self.valid(doc,shape,bad))


class EditWireContract(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        import test_edit_http as support
        support.HTTPAcceptance.setUp(self)
    async def asyncTearDown(self):await self.client.aclose()
    async def put(self,**kwargs):
        import test_edit_http as support
        return await support.HTTPAcceptance.put(self,**kwargs)
    valid=EditContract.valid
    async def test_actual_success_conflict_and_denial_match_schema(self):
        import httpx
        import test_edit_http as support
        doc=self.app.openapi();op=doc['paths']['/api/v1/captures/{capture_id}']['put']
        success=await self.put()
        self.pool.borrows=0
        conflict=await self.put(json=support.support.body.command(expected_revision='3').model_dump())
        self.pool.borrows=0
        self.upstream=lambda permission:httpx.Response(403,json={'detail':{'code':'access_denied'}})
        denied=await self.put()
        self.assertEqual([r.status_code for r in (success,conflict,denied)],[200,409,403])
        for result in (success,conflict,denied):
            self.assertTrue(self.valid(doc,op['responses'][str(result.status_code)]['content']['application/json']['schema'],result.json()))

if __name__=='__main__':unittest.main()
