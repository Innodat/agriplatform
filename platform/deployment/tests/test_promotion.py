"""Exercise the production verifier without GitHub network access."""
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch
class Promotion(unittest.TestCase):
 def verify(self,sha,runs,artifact=True):
  script=Path(__file__).parents[1]/'verify-promotion.py'
  def response(request):
   if '/artifacts' in request.full_url:return io.StringIO(json.dumps({'artifacts':[{'name':'staged-'+sha,'expired':False}] if artifact else []}))
   return io.StringIO(json.dumps({'workflow_runs':runs}))
  with tempfile.TemporaryDirectory() as d:
   def download(args,**kwargs):
    Path(d,'staged.json').write_text(json.dumps({'sha':sha,'environment':'staging','complete':True}));Path(d,'images.json').write_text(json.dumps({'sha':sha}))
   with patch.object(sys,'argv',[str(script),'--sha',sha,'--repository','innodat/agriplatform','--output',d]),patch.dict('os.environ',{'GH_TOKEN':'fixture'}),patch('urllib.request.urlopen',side_effect=response),patch('subprocess.run',side_effect=download):
    with self.assertRaises(SystemExit) as outcome:runpy.run_path(str(script),run_name='__main__')
    return outcome.exception.code
 def test_unstaged_and_nonexact_refs_rejected(self):
  self.assertNotEqual(self.verify('main',[]),0)
  self.assertNotEqual(self.verify('a'*40,[]),0)
 def test_successful_main_sha_requires_artifact(self):
  sha='a'*40;run={'id':42,'head_sha':sha,'head_branch':'main','conclusion':'success'}
  self.assertNotEqual(self.verify(sha,[run],False),0)
  self.assertEqual(self.verify(sha,[run]),0)
 def test_other_branch_and_different_sha_rejected(self):
  sha='a'*40
  for run in [{'id':42,'head_sha':sha,'head_branch':'other','conclusion':'success'},{'id':42,'head_sha':'b'*40,'head_branch':'main','conclusion':'success'}]:self.assertNotEqual(self.verify(sha,[run]),0)
