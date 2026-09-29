import importlib.util
import json
import subprocess
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

PATH=Path(__file__).resolve().parents[1]/'publish-frontend.py'
spec=importlib.util.spec_from_file_location('publish_frontend',PATH)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class FrontendPublication(unittest.TestCase):
 def test_assembled_artifact_is_published_outside_workspace(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);artifact=root/'platform/deployment/public-release';artifact.mkdir(parents=True)
   (root/'package.json').write_text('{"workspaces":["apps/*/web"]}')
   (root/'netlify.toml').write_text('[build]\npublish="platform/deployment/public-release"\n')
   for name in ('release-identity.json','index.html','_redirects'):(artifact/name).write_text(name)
   (artifact/'scribeswell').mkdir();(artifact/'scribeswell/index.html').write_text('reader')
   def run(command,work,output):
    work=Path(work);self.assertNotEqual(work,root);self.assertNotIn(root,work.parents)
    self.assertFalse((work/'package.json').exists())
    self.assertEqual((work/'netlify.toml').read_bytes(),(root/'netlify.toml').read_bytes())
    copied=work/'platform/deployment/public-release'
    self.assertEqual((copied/'scribeswell/index.html').read_text(),'reader')
    self.assertEqual((copied/'_redirects').read_bytes(),(artifact/'_redirects').read_bytes())
    self.assertIn('--prod',command);self.assertIn('--no-build',command)
    output.write(b'{"deploy_id":"fixture"}')
   with patch.object(module,'run_publisher',side_effect=run):module.publish(root)
   self.assertEqual(json.loads((root/'netlify-deploy.json').read_text())['deploy_id'],'fixture')
 def test_missing_identity_prevents_publication(self):
  with tempfile.TemporaryDirectory() as directory,patch.object(module,'run_publisher') as run:
   with self.assertRaises(ValueError):module.publish(Path(directory))
   run.assert_not_called()
 def test_ci_uses_isolated_publisher_after_backend_activation(self):
  workflow=(PATH.parents[2]/'.github/workflows/production.yml').read_text()
  self.assertIn('python3 platform/deployment/publish-frontend.py',workflow)
  self.assertLess(workflow.index('ci-deploy.sh'),workflow.index('publish-frontend.py'))

 def test_timeout_kills_group_and_drains_before_cleanup(self):
  from unittest.mock import Mock
  child=Mock(pid=123,wait=Mock(side_effect=[subprocess.TimeoutExpired('npx',1),0]))
  with patch.object(module.subprocess,'Popen',return_value=child) as spawn,patch.object(module.os,'killpg') as kill:
   with self.assertRaises(subprocess.TimeoutExpired):module.run_publisher(['npx'],Path('/tmp'),None,1)
   self.assertTrue(spawn.call_args.kwargs['start_new_session'])
   kill.assert_called_once_with(123,module.signal.SIGKILL)
   self.assertEqual(child.wait.call_count,2)
 def test_failure_preserves_existing_evidence_and_cleans_directory(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);artifact=root/'platform/deployment/public-release';artifact.mkdir(parents=True)
   (artifact/'release-identity.json').write_text('{}');(root/'netlify.toml').write_text('')
   original=root/'netlify-deploy.json';original.write_text('original evidence')
   with patch.object(module,'run_publisher') as run:
    with self.assertRaises(FileExistsError):module.publish(root)
    run.assert_not_called()
   self.assertEqual(original.read_text(),'original evidence')
   workspaces=[]
   def failure(command,work,output):
    workspaces.append(work);raise subprocess.CalledProcessError(1,command)
   with patch.object(module,'run_publisher',side_effect=failure):
    with self.assertRaises(subprocess.CalledProcessError):module.publish(root,'netlify-retry.json')
   self.assertFalse(workspaces[0].exists());self.assertEqual(original.read_text(),'original evidence')
