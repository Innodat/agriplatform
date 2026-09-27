from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
class Install(unittest.TestCase):
 def test_registered_frontend_paths_and_install_modes_drive_commands(self):
  manifests=[{'frontend':{'path':'apps/new-one/web','install':'prefix'}},{'frontend':{'path':'apps/new-two/web','install':'workspace'}},{'id':'private-service'}]
  with patch('release.load_manifests',return_value=manifests),patch('subprocess.run') as run:runpy.run_path(str(Path(__file__).parents[1]/'install-frontends.py'),run_name='__main__')
  self.assertEqual([call.args[0] for call in run.call_args_list],[['npm','ci','--prefix','apps/new-one/web'],['npm','ci','--workspace=apps/new-two/web','--include-workspace-root']])
