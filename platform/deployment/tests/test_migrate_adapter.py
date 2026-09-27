import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from contextlib import nullcontext
from unittest.mock import patch
class Adapter(unittest.TestCase):
 def load(self):
  owner=types.ModuleType('deploy_pts');owner.OWNERS=[('access','services/access'),('content','services/content-service'),('pts','apps/pts')];owner.deployment_lock=nullcontext;owner.revisions=lambda _:[]
  with patch.dict(sys.modules,{'deploy_pts':owner}):
   spec=importlib.util.spec_from_file_location('adapter',Path(__file__).resolve().parents[3]/'apps/pts/deployment/migrate.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
 def values(self):return {'SUPABASE_URL':'https://stage.supabase.co',**{owner.upper()+'_MIGRATION_DATABASE_URL':f'postgresql+psycopg://{owner}_migrator:fixture@db.stage.supabase.co:5432/postgres?sslmode=require' for owner in ['access','content','pts']}}
 def test_actual_adapter_records_partial_outcomes_with_bounds(self):
  module=self.load();calls=[];states={'access':['old'],'content':['old'],'pts':['old']}
  with tempfile.TemporaryDirectory() as d:
   evidence=Path(d)/'migrations.json'
   def run(cmd,**kwargs):
    owner='access' if 'access' in cmd[4] else 'content';calls.append(owner)
    self.assertEqual(kwargs['timeout'],180);self.assertIn('statement_timeout',kwargs['env']['ACCESS_MIGRATION_DATABASE_URL'])
    self.assertEqual(json.loads(evidence.read_text())['owners'][owner]['before'],['old'])
    states[owner]=['new']
    if owner=='content':raise TimeoutError('secret')
   with self.assertRaises(SystemExit):module.main(evidence,run,nullcontext,lambda owner:states[owner],self.values())
   report=json.loads(evidence.read_text());self.assertEqual(calls,['access','content']);self.assertEqual(report['owners']['access']['after'],['new']);self.assertEqual(report['owners']['content']['after'],['new']);self.assertEqual(report['owners']['pts']['status'],'not_attempted');self.assertNotIn('secret',json.dumps(report))
 def test_missing_later_url_stops_before_first_owner_and_lock(self):
  module=self.load();values=self.values();del values['PTS_MIGRATION_DATABASE_URL']
  with tempfile.TemporaryDirectory() as d,patch.object(module,'database_url',wraps=module.database_url):
   with self.assertRaises(SystemExit):module.main(Path(d)/'evidence.json',lambda *a,**k:self.fail('owner ran'),lambda:self.fail('lock acquired'),lambda _:[],values)
