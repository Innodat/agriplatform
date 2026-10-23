"""Synthetic consumption only; entry read authority is never promoted to write authority."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[3]
tools=ROOT/'apps/kdg-capture/write-tools'
spec=importlib.util.spec_from_file_location('kdg_generated_context_tests',tools/'test_transaction_context.py')
support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
context=support.context

class OwnerConsumption(unittest.TestCase):
    def test_kdg_handler_operation_is_scoped_without_payload_fingerprints(self):
        # Future handlers supply command names and freshly qualified write authority.
        # This fixture neither consumes entry read authority nor creates a capture.
        operation='dddddddd-dddd-4ddd-8ddd-dddddddddddd'
        with patch.object(context.time,'monotonic',return_value=100):
            budget=context.Budget();verified=context.VerifiedContext(support.ORG,support.ACCOUNT,support.ACTOR,'own_write',100)
            key=context.OutcomeKey('kdg_capture',support.ORG,support.ACCOUNT,'capture.create',operation)
            db=support.Connection()
            with context.transaction(db,budget,verified):context.outcome_lock(db,budget,key,verified)
        bound=[args['key'] for sql,args in db.calls if 'pg_advisory_xact_lock' in sql]
        self.assertEqual(bound,[context.outcome_lock_key(key)])
        installed=next(args for sql,args in db.calls if "set_config('app.org_id'" in sql)
        self.assertEqual((key.org_id,key.account_id),(installed['org'],installed['account']))
        other=context.OutcomeKey('kdg_capture',support.ORG,support.ACCOUNT,'capture.edit',operation)
        self.assertNotEqual(context.outcome_lock_key(other),bound[0])
        self.assertEqual(db.calls[-1][0],'COMMIT')
    def test_owner_binds_fixed_scope_and_read_mode_on_managed_copy(self):
        # These are synthetic already-qualified backend assertions, never browser input.
        with patch.object(context.time,'monotonic',return_value=100):
            budget=context.Budget()
            verified=context.VerifiedContext(support.ORG,support.ACCOUNT,support.ACTOR,'own_read',100)
            db=support.Connection()
            with context.transaction(db,budget,verified):
                context.execute(db,budget,'SELECT :owner',{'owner':support.ACCOUNT})
        scope=next(args for sql,args in db.calls if "set_config('app.org_id'" in sql)
        self.assertEqual(scope['org'],support.ORG)
        self.assertEqual(scope['account'],support.ACCOUNT)
        self.assertEqual(scope['actor'],support.ACTOR)
        self.assertEqual(scope['mode'],'own_read')
        self.assertEqual(db.calls[-1][0],'COMMIT')
    def test_restarted_local_attempt_keeps_original_budget(self):
        now=[100.0]
        with patch.object(context.time,'monotonic',side_effect=lambda:now[0]):
            budget=context.Budget();old=context.VerifiedContext(support.ORG,support.ACCOUNT,support.ACTOR,'own_read',100)
            now[0]=102
            with self.assertRaisesRegex(context.WriteError,'authorization_observation_expired'):
                with context.transaction(support.Connection(),budget,old):self.fail('stale entry')
            # Owner would recheck HTTP authority outside locks, without resetting budget.
            now[0]=109.5;fresh=context.VerifiedContext(support.ORG,support.ACCOUNT,support.ACTOR,'own_read',now[0]);db=support.Connection()
            with context.transaction(db,budget,fresh):pass
            self.assertEqual(next(args['total'] for _,args in db.calls if 'total' in args),'500')
    def test_copy_has_no_fingerprint_or_shared_runtime_imports(self):
        import ast
        tree=ast.parse((tools/'transaction_context.py').read_text())
        imports=[node.module for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)]
        imports.extend(alias.name for node in ast.walk(tree) if isinstance(node,ast.Import) for alias in node.names)
        self.assertNotIn('atomic_write',imports)
        self.assertNotIn('command_fingerprint',imports)
        self.assertNotIn('rfc8785',imports)
        forbidden=('atomic_write','command_fingerprint','rfc8785','services','apps')
        self.assertFalse(any(name and any(name==prefix or name.startswith(prefix+'.') for prefix in forbidden) for name in imports))

if __name__=='__main__':unittest.main()
