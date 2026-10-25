"""Candidate schema must describe the existing protected wire behavior."""
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch
import httpx
import test_recovery_http as support
import export_recovery_openapi as export

class ContractAcceptance(unittest.IsolatedAsyncioTestCase):
    setUp=support.HTTPAcceptance.setUp
    asyncTearDown=support.HTTPAcceptance.asyncTearDown
    get=support.HTTPAcceptance.get
    def schema_valid(self,schema,value):
        tool=Path(__file__).resolve().parents[1]/'tests/validate_recovery_schema.py'
        result=subprocess.run(['/usr/bin/python3','-I','-B',str(tool)],input=json.dumps(dict(
            document=self.app.openapi(),schema=schema,value=value)),text=True,capture_output=True,timeout=5)
        self.assertEqual(result.returncode,0,'qualified schema validator must execute successfully')
        return json.loads(result.stdout)['valid']
    def validate_wire(self,result):
        op=self.operation();response=op['responses'][str(result.status_code)]
        self.assertTrue(self.schema_valid(response['content']['application/json']['schema'],result.json()))
        for header,definition in response['headers'].items():
            self.assertIn(header,result.headers)
            self.assertTrue(self.schema_valid(definition['schema'],result.headers[header]))
    def operation(self):return self.app.openapi()['paths']['/api/v1/operations/{operation_id}']['get']
    def test_required_closed_query_path_and_bearer_are_described(self):
        op=self.operation();self.assertEqual(op['operationId'],'recover_operation')
        query=next(p for p in op['parameters'] if p['in']=='query')
        self.assertEqual((query['name'],query['required'],query['schema']['enum']),('command_type',True,['capture.create','capture.edit']))
        path=next(p for p in op['parameters'] if p['in']=='path')
        self.assertEqual(path['schema']['format'],'uuid')
        self.assertIn('not',path['schema']);self.assertEqual(op['security'],[{'HTTPBearer':[]}])
        self.assertNotIn('requestBody',op)
    def test_success_discriminator_and_revision_match_serialized_contract(self):
        schemas=self.app.openapi()['components']['schemas']
        self.assertIn('status',schemas['Unresolved']['required'])
        self.assertFalse(schemas['CaptureReceipt']['additionalProperties'])
        self.assertEqual(schemas['CaptureReceipt']['properties']['command_version']['const'],1)
        import re
        pattern=schemas['CaptureResult']['properties']['revision']['pattern']
        self.assertTrue(re.fullmatch(pattern,'9223372036854775807'))
        self.assertFalse(re.fullmatch(pattern,'9223372036854775808'))
    async def test_error_schemas_match_actual_safe_wire(self):
        self.upstream=lambda:httpx.Response(403,json={'detail':{'code':'access_denied'}})
        result=await self.get()
        schema=self.app.openapi();ref=self.operation()['responses']['403']['content']['application/json']['schema']['$ref'].split('/')[-1]
        error=schema['components']['schemas'][ref]
        self.assertEqual(error['properties']['error_id']['enum'],['access_denied'])
        self.assertFalse(error['additionalProperties'])
        self.assertEqual(result.json()['error_id'],'access_denied')
        self.assertTrue(set(result.json())<=set(error['properties']))
    def test_export_is_deterministic_and_never_connects_or_sends(self):
        with patch.object(support.boundary,'_engine',side_effect=AssertionError('engine_constructor_must_not_run')),patch.object(httpx.AsyncClient,'send',side_effect=AssertionError('no_network')):
            first=export.render();second=export.render()
        self.assertEqual(first,second)
        self.assertEqual(json.loads(first),self.app.openapi())
        self.assertEqual(set(json.loads(first)['paths']),{'/api/v1/operations/{operation_id}'})
        self.assertNotIn('synthetic-key',first)
    async def test_actual_create_edit_and_unresolved_match_exported_schemas(self):
        for command in ('capture.create','capture.edit'):
            self.pool=support.Pool();self.app.state.recovery_engine=self.pool
            self.pool.connection.outcome.update(command_type=command,result=dict(
                capture_id=support.support.support.STORED_CAPTURE,revision='9223372036854775807'))
            result=await self.get(support.URL.replace('capture.create',command))
            self.assertEqual(result.status_code,200);self.validate_wire(result)
        self.pool=support.Pool();self.app.state.recovery_engine=self.pool
        self.pool.connection.outcome=None
        result=await self.get();self.assertEqual(result.status_code,200);self.validate_wire(result)
    async def test_all_declared_error_pairs_match_actual_wire_and_headers(self):
        boundary=support.boundary
        for status,identifier in sorted(boundary.PAIRS):
            with self.subTest(status=status,identifier=identifier),patch.object(boundary.recovery.RecoveryHandler,'_authorize',side_effect=boundary.protected.HandlerError(status,identifier)):
                result=await self.get()
                self.assertEqual(result.status_code,status);self.validate_wire(result)
    def test_schema_rejects_noncanonical_ids_and_trailing_revision_characters(self):
        schema=next(p['schema'] for p in self.operation()['parameters'] if p['in']=='path')
        identifier='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
        self.assertTrue(self.schema_valid(schema,identifier))
        for value in ('x'+identifier,identifier+'x',identifier.upper(),identifier+'\n','00000000-0000-0000-0000-000000000000'):
            self.assertFalse(self.schema_valid(schema,value),repr(value))
        revision=self.app.openapi()['components']['schemas']['CaptureResult']['properties']['revision']
        for value in ('1\n','1x','01','0','9223372036854775808'):
            self.assertFalse(self.schema_valid(revision,value),repr(value))
    def test_fresh_import_export_has_no_engine_network_or_socket_io(self):
        candidate=Path(export.__file__).resolve().parent
        code="""import sys,json,runpy,socket,httpx,sqlalchemy
from unittest.mock import patch
sys.path.insert(0,sys.argv[1])
with patch.object(sqlalchemy,'create_engine',side_effect=AssertionError('engine_io')),patch.object(httpx.AsyncClient,'__init__',side_effect=AssertionError('async_http_client')),patch.object(httpx.Client,'__init__',side_effect=AssertionError('http_client')),patch.object(socket.socket,'connect',side_effect=AssertionError('socket_io')):
    module=runpy.run_path(sys.argv[1]+'/export_recovery_openapi.py')
    result=module['render']()
    assert '/api/v1/operations/{operation_id}' in json.loads(result)['paths']
print('fresh_export_no_io')
"""
        result=subprocess.run([sys.executable,'-I','-B','-c',code,str(candidate)],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),'fresh_export_no_io')
    def test_committed_artifact_is_current(self):
        self.assertEqual(export.main(['--check']),0)
    def test_export_check_detects_missing_or_stale_output_without_overwriting(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'candidate.json'
            with patch.object(export,'DESTINATION',path):
                self.assertEqual(export.main(['--check']),1)
                self.assertFalse(path.exists())
                self.assertEqual(export.main([]),0)
                self.assertEqual(export.main(['--check']),0)
                path.write_text('stale')
                self.assertEqual(export.main(['--check']),1)
                self.assertEqual(path.read_text(),'stale')

if __name__=='__main__':unittest.main()
