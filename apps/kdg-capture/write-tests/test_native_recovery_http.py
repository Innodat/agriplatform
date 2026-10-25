"""Qualification evidence must reject unsafe or incomplete success claims."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch,AsyncMock
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations/tests'))
import qualify_recovery_http as q

class QualificationEvidence(unittest.TestCase):
    def test_matching_response_requires_private_header_and_exact_body(self):
        for status,body,headers in ((503,{'status':'unresolved'},{'Cache-Control':'private, no-store'}),
            (200,{'status':'unresolved'},{}),(200,{'status':'committed'},{'Cache-Control':'private, no-store'}),
            (200,{'status':'unresolved','private':'canary'},{'Cache-Control':'private, no-store'})):
            with self.assertRaises(AssertionError):
                q.verify_response(httpx.Response(status,json=body,headers=headers),200,{'status':'unresolved'})
        q.verify_response(httpx.Response(200,json={'status':'unresolved'},headers={'Cache-Control':'private, no-store'}),200,{'status':'unresolved'})
    def run_qualification(self,*,after=None,sentinel_error=False,exercise_error=False):
        self.stack=__import__('contextlib').ExitStack();self.addCleanup(self.stack.close)
        counts={'capture':10,'operation_outcome':10,'capture_revision':10}
        for name,result in (('retained',({}, {}, object())),('migration_qualified','historical-applied-proof'),('identities',{})):
            self.stack.enter_context(patch.object(q.fixture,name,return_value=result))
        self.stack.enter_context(patch.object(q.prior,'retained_proof',return_value={}))
        self.stack.enter_context(patch.object(q.prior,'counts',side_effect=[counts,after or counts]))
        self.stack.enter_context(patch.object(q.fixture,'sentinel',side_effect=[None,ValueError('drift')] if sentinel_error else None))
        self.stack.enter_context(patch.object(q.fixture,'revision',return_value=q.fixture.STORAGE))
        self.stack.enter_context(patch.object(q,'exercise',new=AsyncMock(side_effect=RuntimeError('private-native') if exercise_error else None,return_value={'cases':['native'],'read_only':True})))
        receipt=self.stack.enter_context(patch.object(q.fixture,'receipt',return_value=Path('/tmp/synthetic-native-proof.json')))
        return receipt
    def test_no_success_receipt_after_count_drift(self):
        receipt=self.run_qualification(after={'capture':11})
        with self.assertRaises(AssertionError):q.qualify()
        receipt.assert_not_called()
    def test_no_success_receipt_after_sentinel_drift(self):
        receipt=self.run_qualification(sentinel_error=True)
        with self.assertRaises(ValueError):q.qualify()
        receipt.assert_not_called()
    def test_no_success_receipt_after_native_failure(self):
        receipt=self.run_qualification(exercise_error=True)
        with self.assertRaisesRegex(RuntimeError,'^private-native$'):q.qualify()
        receipt.assert_not_called()
    def test_no_success_receipt_if_source_changes_during_execution(self):
        receipt=self.run_qualification()
        with patch.object(q,'source_hashes',side_effect=[q.INITIAL_SOURCES,{}]):
            with self.assertRaisesRegex(AssertionError,'source_changed_during_execution'):q.qualify()
        receipt.assert_not_called()
    def test_cli_failure_receipt_has_initial_sources_and_safe_stage(self):
        import io
        from contextlib import redirect_stdout
        with patch.object(q,'qualify',side_effect=ValueError('private-credential-canary')),patch.object(q.fixture,'receipt',return_value=Path('/tmp/failure.json')) as receipt,redirect_stdout(io.StringIO()) as output:
            self.assertEqual(q.main(['--qualify-retained']),1)
        result=receipt.call_args.args[1]
        self.assertEqual(result['sources'],q.INITIAL_SOURCES)
        self.assertEqual(result['failed_stage'],q.STAGE)
        self.assertNotIn('private-credential-canary',output.getvalue()+str(result))
        self.assertFalse(result['succeeded'])
    def test_qualified_only_after_final_verification(self):
        receipt=self.run_qualification()
        result=q.qualify()
        self.assertTrue(result['qualified']);self.assertTrue(result['succeeded'])
        receipt.assert_called_once()

if __name__=='__main__':unittest.main()
