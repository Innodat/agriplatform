"""Offline candidate create schema and actual wire agreement; no native storage."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'write-candidate'),str(Path(__file__).resolve().parents[1]/'api')]
import create_http
import test_capture_create_handler as support

class CreateContract(unittest.TestCase):
    def valid(self,doc,shape,value):
        tool=Path(__file__).resolve().parents[1]/'tests/validate_recovery_schema.py'
        result=subprocess.run(['/usr/bin/python3','-I','-B',str(tool)],input=json.dumps(dict(document=doc,schema=shape,value=value)),text=True,capture_output=True,timeout=5)
        self.assertEqual(result.returncode,0,'qualified schema validator must run')
        return json.loads(result.stdout)['valid']
    def test_closed_create_request_and_private_response_metadata(self):
        doc=create_http._create_app(None,None,None).openapi();op=doc['paths']['/api/v1/captures']['post'];shape=op['requestBody']['content']['application/json']['schema']
        value=support.support.command().model_dump()
        self.assertTrue(self.valid(doc,shape,value));self.assertEqual(op['operationId'],'create_capture')
        self.assertEqual(op['security'],[{'HTTPBearer':[]}]);self.assertEqual(op['parameters'],[])
        for change in ({'expected_revision':'1'},{'command_version':2},{'capture_id':'invalid'},{'child_id':support.ORG+'\n'},{'operation_id':support.ORG.upper()}):
            self.assertFalse(self.valid(doc,shape,dict(value,**change)))
        for response in op['responses'].values():self.assertEqual(response['headers']['Cache-Control']['schema']['const'],'private, no-store')
    def test_device_time_reference_and_unicode_agree_with_runtime(self):
        from capture_commands import parse_create, CommandError
        doc=create_http._create_app(None,None,None).openapi()
        shape=doc['paths']['/api/v1/captures']['post']['requestBody']['content']['application/json']['schema']
        cases=[('captured_at',value,expected) for value,expected in [
            ('2026-10-26T10:00:00Z',True),('2026-10-26t10:00:00z',True),
            ('2026-10-26t10:00:00.123456789z',True),('2026-10-26T10:00:00.1+00:00',True),
            ('2026-02-30T10:00:00Z',False),('2026-10-26T10:00:00+02:00',False),
            ('2026-10-26T25:00:00Z',False),('not-a-time',False)]]
        cases += [('child_eligibility_ref',value,expected) for value,expected in [('',False),(' \t\n',False),('x\x00',False),('\ud800',False),(' x ',True),('😀',True)]]
        for field,value,expected in cases:
            with self.subTest(field=field,value=ascii(value)):
                body=dict(support.support.command().model_dump(),**{field:value})
                try:parse_create(json.dumps(body));runtime=True
                except CommandError:runtime=False
                self.assertEqual(runtime,expected);self.assertEqual(self.valid(doc,shape,body),runtime)
        for value,expected in [('\ud800',False),('\udfff',False),('😀',True),('𐀀',True)]:
            for answer in ({'value':value},{'value':True,'details':value}):
                body=dict(support.support.command().model_dump(),answers={support.support.QUESTION:answer})
                try:parse_create(json.dumps(body));runtime=True
                except CommandError:runtime=False
                self.assertEqual(runtime,expected);self.assertEqual(self.valid(doc,shape,body),runtime)
    def test_receipt_create_only_and_closed_error_status_families(self):
        doc=create_http._create_app(None,None,None).openapi();op=doc['paths']['/api/v1/captures']['post'];shape=op['responses']['200']['content']['application/json']['schema']
        value=dict(operation_id=support.support.OPERATION,command_type='capture.create',command_version=1,status='committed',result=dict(capture_id=support.support.CAPTURE,revision='1'))
        self.assertTrue(self.valid(doc,shape,value))
        for change in ({'command_type':'capture.edit'},{'command_version':2},{'result':dict(capture_id=support.support.CAPTURE,revision=1)},{'result':dict(capture_id=support.support.CAPTURE,revision='9223372036854775808')}):self.assertFalse(self.valid(doc,shape,dict(value,**change)))
        for status,code in create_http.PAIRS:
            shape=op['responses'][str(status)]['content']['application/json']['schema'];body=dict(error='Safe',error_id=code)
            self.assertTrue(self.valid(doc,shape,body));self.assertFalse(self.valid(doc,shape,dict(body,current_revision='2')))

class CreateWireContract(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        import test_create_http
        test_create_http.HTTPAcceptance.setUp(self)
    async def asyncTearDown(self):await self.client.aclose()
    valid=CreateContract.valid
    async def test_actual_create_denial_and_domain_error_match_schema(self):
        import httpx
        import test_create_http
        post=lambda **kwargs:test_create_http.HTTPAcceptance.post(self,**kwargs)
        doc=self.app.openapi();op=doc['paths']['/api/v1/captures']['post']
        success=await post();self.pool.borrows=0
        invalid=await post(json=support.support.command(answers={}).model_dump());self.pool.borrows=0
        self.upstream=lambda permission:httpx.Response(403,json={'detail':{'code':'access_denied'}})
        denied=await post();self.assertEqual([r.status_code for r in (success,invalid,denied)],[200,422,403])
        for result in (success,invalid,denied):self.assertTrue(self.valid(doc,op['responses'][str(result.status_code)]['content']['application/json']['schema'],result.json()))

if __name__=='__main__':unittest.main()
