"""Edit export is reproducible and has no live collaborators."""
import io
import json
from contextlib import redirect_stdout,redirect_stderr
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'write-candidate'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api'))
import export_edit_openapi as export

class EditExport(unittest.TestCase):
    def test_export_and_stale_check_without_live_engine_or_network(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(export,'DESTINATION',Path(folder)/'edit.json'),\
            patch('sqlalchemy.create_engine',side_effect=AssertionError('no_engine')),\
            patch('httpx.AsyncClient',side_effect=AssertionError('no_network')),redirect_stdout(io.StringIO()):
            self.assertEqual(export.main([]),0)
            self.assertIn('/api/v1/captures/{capture_id}',json.loads(export.DESTINATION.read_text())['paths'])
            self.assertEqual(export.main(['--check']),0)
            export.DESTINATION.write_text('{}')
            with redirect_stderr(io.StringIO()) as output:self.assertEqual(export.main(['--check']),1)
            self.assertEqual(output.getvalue().strip(),'edit_openapi_stale')
    def test_export_failures_remain_safe(self):
        with patch.object(export,'render',side_effect=ValueError('credential-canary')),redirect_stderr(io.StringIO()) as output:
            self.assertEqual(export.main([]),1)
        self.assertEqual(output.getvalue().strip(),'edit_openapi_export_failed')
    def test_symlink_output_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'target';target.write_text('original')
            link=Path(folder)/'edit.json';link.symlink_to(target)
            with patch.object(export,'DESTINATION',link),redirect_stderr(io.StringIO()):
                self.assertEqual(export.main([]),1)
            self.assertEqual(target.read_text(),'original')

if __name__=='__main__':unittest.main()
