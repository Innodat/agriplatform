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
  self.assertEqual(groups[0],{'id':'scribeswell-owned','dockerfile':'apps/scribeswell/deployment/Migrations.Dockerfile','env_file':'scribeswell-migrations.env','owners':['scribeswell'],'compatibility_inputs':['apps/scribeswell/deployment/migrate.py','apps/scribeswell/deployment/migration-requirements.txt','apps/scribeswell/backend/database.py','platform/deployment/host-release.py','platform/deployment/target_contract.py','apps/scribeswell/deployment/studies_migrate.py','apps/scribeswell/deployment/studies_release_contract.py','apps/scribeswell/studies-alembic.ini','apps/scribeswell/studies-migrations/env.py','apps/scribeswell/studies-migrations/versions/0001_personal_notes.py','apps/scribeswell/studies-migrations/versions/0002_study_rename.py','apps/scribeswell/studies-migrations/versions/0003_collected_passages.py','apps/scribeswell/studies-migrations/versions/0004_note_deletion.py','apps/scribeswell/studies-migrations/versions/0005_study_deletion.py','apps/scribeswell/studies-migrations/versions/0006_own_highlights.py','apps/scribeswell/studies-migrations/versions/0007_own_copies.py','apps/scribeswell/studies-migrations/versions/0008_study_details.py','apps/scribeswell/studies-migrations/versions/0009_note_metadata_predicates.py','apps/scribeswell/studies-database-tools/owned_migration.py','apps/scribeswell/tools/sql/prepare_personal_notes_roles.sql']})
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

class StudiesReadiness(unittest.TestCase):
 def manifest(self):
  return next(m for m in release.load_manifests(ROOT) if m['id']=='access')
 def artifact(self):
  path=ROOT/'services/access/studies_readiness.py'
  spec=importlib.util.spec_from_file_location('studies_readiness_test',path)
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  return {'schema_version':1,'release_id':'synthetic-release','identity_revision':'identity_0021','access_revision':'access_0016','service_actor_id':'11111111-1111-4111-8111-111111111111','runtime_sources':module.runtime_hashes(),'qualification_sha256':'a'*64,'profile_hook_qualified':True,'live_provider_qualified':True}
 def test_previous_consumers_need_no_studies_inputs(self):
  manifest=self.manifest();required,roles=release.runtime_contract(manifest,manifest['smoke_env'],ROOT)
  self.assertEqual(required,set(manifest['required_env']));self.assertEqual(roles,manifest['database_roles'])
 def test_opt_in_requires_closed_current_owner_readiness(self):
  manifest=self.manifest();values=dict(manifest['smoke_env'])
  values['SCRIBESWELL_SERVICE_KEY']='synthetic-studies'
  with self.assertRaises(ValueError):release.runtime_contract(manifest,values,ROOT)
  for field,role in manifest['studies_enrollment']['database_roles'].items():values[field]='postgresql://'+role+'@localhost/synthetic'
  values['STUDIES_READINESS_JSON']=json.dumps(self.artifact())
  required,roles=release.runtime_contract(manifest,values,ROOT)
  self.assertTrue(set(manifest['studies_enrollment']['required_env'])<=required)
  self.assertEqual(roles['STUDIES_IDENTITY_SETUP_DATABASE_URL'],'identity_studies_setup_runtime')
  for field,bad in [('identity_revision','identity_0020'),('access_revision','access_0015'),('profile_hook_qualified',False),('live_provider_qualified',False),('runtime_sources',{})]:
   artifact=self.artifact();artifact[field]=bad;values['STUDIES_READINESS_JSON']=json.dumps(artifact)
   with self.subTest(field=field),self.assertRaises(ValueError):release.runtime_contract(manifest,values,ROOT)
 def test_partial_studies_inputs_without_caller_key_fail(self):
  manifest=self.manifest();values=dict(manifest['smoke_env'],STUDIES_ACCESS_DATABASE_URL='postgresql://access_studies_runtime@localhost/synthetic')
  with self.assertRaises(ValueError):release.runtime_contract(manifest,values,ROOT)
