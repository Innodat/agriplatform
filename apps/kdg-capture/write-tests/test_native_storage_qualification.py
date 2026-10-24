"""Offline refusal/error-oracle tests; these cannot establish native SQL acceptance."""
import contextlib
from io import StringIO
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
import subprocess
import sys
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('kdg_storage_qualification_oracle', ROOT / 'apps/kdg-capture/migrations/tests/qualify_capture_storage.py')
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)


def failure(code):
    error = SQLAlchemyError('PRIVATE_SYNTHETIC_CREDENTIAL_OR_INPUT')
    error.orig = SimpleNamespace(sqlstate=code)
    return error


class Savepoint:
    def __init__(self): self.rolled_back = False
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def rollback(self): self.rolled_back = True


class Connection:
    def __init__(self, deferred_error=None):
        self.savepoint = Savepoint()
        self.deferred_error = deferred_error
        self.forced = False
    def begin_nested(self): return self.savepoint
    def execute(self, statement, parameters=None):
        if str(statement) == 'SET CONSTRAINTS ALL IMMEDIATE':
            self.forced = True
            if self.deferred_error: raise self.deferred_error


class QualificationOracle(unittest.TestCase):
    def test_expected_immediate_refusal_rolls_back_case(self):
        db = Connection()
        def refuse(): raise failure('23514')
        self.assertEqual(q.expect_error(db, refuse, ('23514',)), '23514')
        self.assertTrue(db.savepoint.rolled_back)

    def test_mapped_safe_sql_failure_retains_expected_native_state(self):
        db = Connection()
        def refuse():
            try: raise failure('42501')
            except SQLAlchemyError: raise q.write.WriteError('internal_error') from None
        self.assertEqual(q.expect_error(db, refuse, ('42501',)), '42501')
        self.assertTrue(db.savepoint.rolled_back)

    def test_unexpected_sqlstate_is_not_accepted(self):
        db = Connection()
        def refuse(): raise failure('42501')
        with self.assertRaisesRegex(AssertionError, 'unexpected_sqlstate'):
            q.expect_error(db, refuse, ('23514',))
        self.assertTrue(db.savepoint.rolled_back)

    def test_unexpected_success_is_not_accepted(self):
        db = Connection()
        with self.assertRaisesRegex(AssertionError, 'expected_database_refusal_missing'):
            q.expect_error(db, lambda: None, ('23514',))
        self.assertTrue(db.forced)
        self.assertTrue(db.savepoint.rolled_back)

    def test_deferred_constraints_must_actually_fire(self):
        db = Connection(failure('23503'))
        self.assertEqual(q.expect_error(db, lambda: None, ('23503',)), '23503')
        self.assertTrue(db.forced)
        self.assertTrue(db.savepoint.rolled_back)

    def test_native_negative_fixture_can_install_missing_mode(self):
        q.set_context(Connection(), mode='')

    def test_deferred_refusal_cannot_satisfy_immediate_guard_case(self):
        db = Connection(failure('23514'))
        with self.assertRaisesRegex(AssertionError, 'expected_immediate_refusal_missing'):
            q.expect_error(db, lambda: None, ('23514',), immediate=True)
        self.assertTrue(db.savepoint.rolled_back)

    def test_failed_body_still_gets_independent_rollback_inspection(self):
        import inspect_native
        from sqlalchemy.engine import make_url
        original = failure('23514')
        engine = SimpleNamespace(connect=lambda: (_ for _ in ()).throw(original), dispose=lambda: None)
        with patch.object(q.fixture, 'load', return_value=({'database':'synthetic'}, {'before':'baseline'})), \
             patch.object(q.fixture, 'administrator', return_value=make_url('postgresql://synthetic@127.0.0.1/synthetic')), \
             patch.object(q, 'inspect_current', side_effect=['baseline','baseline']) as inspect, \
             patch.object(inspect_native, 'inspect', return_value={}), \
             patch.object(q, 'create_engine', return_value=engine):
            with self.assertRaises(SQLAlchemyError) as failed:
                q.qualify()
        self.assertIs(failed.exception, original)
        self.assertEqual(inspect.call_count, 2)
        self.assertTrue(failed.exception.rollback_verified)

    def test_failed_preservation_check_does_not_replace_original_body_failure(self):
        import inspect_native
        from sqlalchemy.engine import make_url
        original = failure('23514')
        engine = SimpleNamespace(connect=lambda: (_ for _ in ()).throw(original), dispose=lambda: None)
        with patch.object(q.fixture, 'load', return_value=({'database':'synthetic'}, {'before':'baseline'})), \
             patch.object(q.fixture, 'administrator', return_value=make_url('postgresql://synthetic@127.0.0.1/synthetic')), \
             patch.object(q, 'inspect_current', side_effect=['baseline', ValueError('inspection failed')]) as inspect, \
             patch.object(inspect_native, 'inspect', return_value={}), \
             patch.object(q, 'create_engine', return_value=engine):
            with self.assertRaises(SQLAlchemyError) as failed:
                q.qualify()
        self.assertIs(failed.exception, original)
        self.assertEqual(inspect.call_count, 2)
        self.assertFalse(failed.exception.rollback_verified)

    def test_no_explicit_run_never_connects(self):
        with patch.object(q, 'qualify', side_effect=AssertionError('must not connect')) as run:
            with contextlib.redirect_stderr(StringIO()) as output:
                self.assertEqual(q.main([]), 1)
        run.assert_not_called()
        self.assertNotIn('PRIVATE', output.getvalue())

    def test_optimized_python_cannot_run_assertion_based_native_checks(self):
        result = subprocess.run([sys.executable, '-I', '-B', '-O', str(Path(q.__file__)), '--run'],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertIn('kdg_native_storage_failed', result.stderr)

    def test_cli_failures_do_not_dump_exception_input(self):
        with patch.object(q, 'qualify', side_effect=failure('23514')):
            with contextlib.redirect_stderr(StringIO()) as output:
                self.assertEqual(q.main(['--run']), 1)
        self.assertNotIn('PRIVATE', output.getvalue())
        self.assertIn('23514', output.getvalue())


if __name__ == '__main__': unittest.main()
