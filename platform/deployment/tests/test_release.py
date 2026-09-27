import importlib.util
from pathlib import Path
import tempfile
import unittest
import json
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
 def test_health_failure_is_not_success(self):
  def fail():raise RuntimeError('health')
  self.assertFalse(release.coordinate([],lambda _:None,fail)['activated'])
 def test_unsafe_manifest_paths_and_cycles_rejected(self):
  for docs in [[{'id':'a','depends_on':['a'],'dockerfile':'apps/a/Dockerfile'}],[{'id':'a','depends_on':[],'dockerfile':'../Dockerfile'}]]:
   with self.assertRaises(ValueError):release.validate_manifests(docs,ROOT)
if __name__=='__main__':unittest.main()
