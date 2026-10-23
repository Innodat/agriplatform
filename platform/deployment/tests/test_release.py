import importlib.util
from pathlib import Path
import tempfile
import unittest
import json
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('release',ROOT/'platform/deployment/release.py')
release=importlib.util.module_from_spec(spec);spec.loader.exec_module(release)
class Release(unittest.TestCase):
 def test_registry(self):
  manifests=release.load_manifests(ROOT)
  self.assertEqual({m['id'] for m in manifests},{'pts','scribeswell','access','content','directory'})
  self.assertLess([m['id'] for m in manifests].index('access'),[m['id'] for m in manifests].index('pts'))
 def test_failure_blocks_activation_and_preserves_partial_outcomes(self):
  calls=[]
  def run(step):
   calls.append(step)
   if step=='content':raise RuntimeError('sensitive upstream text')
  report=release.coordinate(['access','content','pts'],run,lambda:calls.append('activate'))
  self.assertEqual(calls,['access','content'])
  self.assertEqual(report['owners']['access']['status'],'succeeded')
  self.assertEqual(report['owners']['content']['status'],'failed')
  self.assertEqual(report['owners']['pts']['status'],'not_attempted')
  self.assertFalse(report['activated'])
  self.assertNotIn('sensitive',json.dumps(report))
 def test_scribeswell_has_one_separate_owned_migration_group(self):
  manifests=release.load_manifests(ROOT)
  registry=json.loads((ROOT/'platform/deployment/registry.json').read_text())
  groups=[g for g in registry['migration_groups'] if 'scribeswell' in g['owners']]
  self.assertEqual(len(groups),1)
  self.assertEqual(groups[0],{'id':'scribeswell-owned','dockerfile':'apps/scribeswell/deployment/Migrations.Dockerfile','env_file':'scribeswell-migrations.env','owners':['scribeswell'],'compatibility_inputs':['apps/scribeswell/deployment/migrate.py','apps/scribeswell/deployment/migration-requirements.txt','apps/scribeswell/backend/database.py','platform/deployment/host-release.py','platform/deployment/target_contract.py']})
  app=next(m for m in manifests if m['id']=='scribeswell')
  self.assertEqual(app['migration'],{'owner':'scribeswell','config':'apps/scribeswell/alembic.ini','url_env':'SCRIBESWELL_MIGRATION_DATABASE_URL','role':'scribeswell_migrator'})
 def test_health_failure_is_not_success(self):
  def fail():raise RuntimeError('health')
  self.assertFalse(release.coordinate([],lambda _:None,fail)['activated'])
 def test_migration_compatibility_inputs_require_owned_existing_files(self):
  for inputs in ('app/validator.py',[None],['../outside.py'],['/outside.py'],['missing.py'],['app']):
   with self.subTest(inputs=inputs),tempfile.TemporaryDirectory() as d:
    root=Path(d);deployment=root/'platform/deployment';deployment.mkdir(parents=True)
    app=root/'app';app.mkdir();(app/'Dockerfile').write_text('FROM fixture')
    (deployment/'registry.json').write_text(json.dumps({'manifests':[],'migration_groups':[{'id':'app-owned','dockerfile':'app/Dockerfile','env_file':'app-migrations.env','owners':['app'],'compatibility_inputs':inputs}],'bootstrap_paths':[]}))
    with patch.object(release,'validate_manifests',return_value=[{'id':'app','migration':{'owner':'app'}}]):
     with self.assertRaises(ValueError):release.load_manifests(root)
 def test_unsafe_manifest_paths_and_cycles_rejected(self):
  for docs in [[{'id':'a','depends_on':['a'],'dockerfile':'apps/a/Dockerfile'}],[{'id':'a','depends_on':[],'dockerfile':'../Dockerfile'}]]:
   with self.assertRaises(ValueError):release.validate_manifests(docs,ROOT)
if __name__=='__main__':unittest.main()
