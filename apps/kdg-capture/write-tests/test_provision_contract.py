"""Export and real candidate wire agree; strict schema rejects unsafe spellings."""
import json
import unittest
from unittest.mock import patch
import test_provision_http as wire
import test_create_contract as contract
import export_provision_openapi as export
import provision_http
import provision
class ProvisionContract(unittest.IsolatedAsyncioTestCase):
    setUp=wire.HTTPAcceptance.setUp
    asyncTearDown=wire.HTTPAcceptance.asyncTearDown
    get=wire.HTTPAcceptance.get
    async def test_actual_closed_wire_and_status_schema(self):
        doc=self.app.openapi();op=doc['paths'][wire.URL]['get'];valid=contract.CreateContract.valid
        response=await self.get();value=response.json();shape=op['responses']['200']['content']['application/json']['schema']
        self.assertTrue(valid(self,doc,shape,value))
        for change in ({'extra':1},{'schema_version':2},{'actor_id':'invalid'}):self.assertFalse(valid(self,doc,shape,{**value,**change}))
        for model,field,invalid in [('Child','child_id',wire.support.CHILD+'\n'),('Child','child_label',' \t\n'),('Child','child_label','x\x00'),('Child','child_eligibility_ref','x'*43+'\n'),('Child','checked_at','2026-10-26T00:00:00Z\n'),('Provision','membership_id','7\n'),('OwnReadObservation','expires_at','2026-11-02T00:00:00+00:00')]:
            self.assertFalse(valid(self,doc,doc['components']['schemas'][model]['properties'][field],invalid),(model,field))
        for status,identifier in provision_http.PAIRS:
            self.assertTrue(valid(self,doc,op['responses'][str(status)]['content']['application/json']['schema'],{'error':'Safe','error_id':identifier}))
        self.assertEqual(op['operationId'],'provision_setup');self.assertNotIn('requestBody',op)
    async def test_owner_export_is_inert_and_current(self):
        with patch.object(provision_http,'_engine',side_effect=AssertionError('no_engine')),patch.object(provision.ProvisionHandler,'__init__',side_effect=AssertionError('no_authority')):
            self.assertEqual(export.render(),export.DESTINATION.read_text())
