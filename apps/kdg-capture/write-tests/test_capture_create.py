"""Behavioral fresh-create acceptance; fake connection is not native proof."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'apps/kdg-capture/api'))
sys.path.insert(0, str(ROOT / 'apps/kdg-capture/write-candidate'))
import capture_create as create
from capture_commands import parse_create
from questionnaire import initial_definition

spec = importlib.util.spec_from_file_location('create_connection_support', ROOT / 'apps/kdg-capture/write-tools/test_transaction_context.py')
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)
write = create.write
ORG, ACCOUNT, ACTOR, CHILD, VERSION, CAPTURE, OPERATION, QUESTIONNAIRE, QUESTION = [
    f'{n:08x}-aaaa-4aaa-8aaa-{n:012x}' for n in range(1, 10)]


def command(**changes):
    value = dict(operation_id=OPERATION, command_version=1, capture_id=CAPTURE,
        child_id=CHILD, questionnaire_version_id=VERSION, observation_date='2026-10-24',
        captured_at='2026-10-24t10:11:12.123456789z', child_eligibility_ref='opaque-ref',
        answers={QUESTION: {'value': 1}, **{key: {'value': False} for key in (ACTOR, CHILD, VERSION)}})
    value.update(changes)
    return parse_create(json.dumps(value))


class Rows:
    rowcount = 1
    def __init__(self, value): self.value = value
    def mappings(self): return self
    def one_or_none(self): return self.value


class Connection(support.Connection):
    def __init__(self):
        super().__init__()
        self.child = dict(active=True)
        self.eligibility = dict(membership_id=7, observed_active=True)
        self.assignment = dict(membership_id=7, active=True)
        self.version = dict(questionnaire_id=QUESTIONNAIRE,
            definition=initial_definition([QUESTION, ACTOR, CHILD, VERSION]).model_dump())
        self.fail_history = False
    def execute(self, sql, parameters):
        result = super().execute(sql, parameters)
        sql = str(sql)
        for fragment, value in (
            ('FROM kdg_capture.operation_outcome', None),
            ('FROM kdg_capture.child WHERE', self.child),
            ('FROM kdg_capture.child_eligibility', self.eligibility),
            ('FROM kdg_capture.child_assignment', self.assignment),
            ('FROM kdg_capture.questionnaire_version', self.version),
        ):
            if fragment in sql: return Rows(value)
        if sql.startswith('INSERT INTO kdg_capture.capture_revision'):
            if self.fail_history:
                from sqlalchemy.exc import SQLAlchemyError
                raise SQLAlchemyError('sensitive payload canary')
            return Rows(None)
        return result


class FreshCreateAcceptance(unittest.TestCase):
    def setUp(self):
        self.now = 100.0
        clock = patch.object(write.time, 'monotonic', side_effect=lambda: self.now)
        clock.start(); self.addCleanup(clock.stop)
        self.budget = write.Budget()
        self.context = write.VerifiedContext(ORG, ACCOUNT, ACTOR, 'own_write', self.now)
        self.db = Connection()
    def execute(self, permission='kdg_capture.capture.create.assigned', membership='7', cmd=None):
        with write.transaction(self.db, self.budget, self.context):
            return create.create_in_transaction(self.db, self.budget, self.context,
                cmd or command(), membership_id=membership, permission=permission)
    def inserts(self): return [(sql, args) for sql, args in self.db.calls if sql.startswith('INSERT')]
    def test_current_assigned_create_writes_one_linked_capture_outcome_history(self):
        receipt = self.execute()
        inserts = self.inserts()
        self.assertEqual(len(inserts), 3)
        self.assertTrue(inserts[0][0].startswith('INSERT INTO kdg_capture.capture\n'))
        self.assertTrue(inserts[1][0].startswith('INSERT INTO kdg_capture.operation_outcome'))
        self.assertTrue(inserts[2][0].startswith('INSERT INTO kdg_capture.capture_revision'))
        capture = inserts[0][1]
        self.assertEqual((capture['member'], capture['account'], capture['actor']), (7, ACCOUNT, ACTOR))
        self.assertEqual(capture['device'], command().captured_at)
        self.assertEqual(json.loads(capture['answers'])[ACTOR], {'value': False})
        self.assertEqual(receipt.result.capture_id, CAPTURE)
        self.assertEqual(receipt.result.revision, '1')
        self.assertEqual(inserts[2][1]['outcome'], inserts[1][1]['id'])
    def test_removed_assignment_or_rejoined_membership_cannot_save(self):
        for assignment in (None, dict(active=False, membership_id=7), dict(active=True, membership_id=8)):
            self.db = Connection(); self.db.assignment = assignment
            with self.subTest(assignment=assignment), self.assertRaisesRegex(write.WriteError, '^assignment_unavailable$'):
                self.execute()
            self.assertEqual(self.inserts(), [])
    def test_foreign_missing_or_old_membership_eligibility_cannot_save(self):
        for eligibility in (None, dict(membership_id=8, observed_active=True), dict(membership_id=7, observed_active=False)):
            self.db = Connection(); self.db.eligibility = eligibility
            with self.subTest(eligibility=eligibility), self.assertRaisesRegex(write.WriteError, '^child_eligibility_unavailable$'):
                self.execute()
            self.assertEqual(self.inserts(), [])
    def test_prior_active_observation_allows_ordinary_inactive_child(self):
        self.db.child = dict(active=False)
        self.assertEqual(self.execute().result.revision, '1')
    def test_current_create_all_needs_no_assignment_and_stays_own_author(self):
        self.db.assignment = None
        self.execute(permission='kdg_capture.capture.create.all')
        self.assertFalse(any('FROM kdg_capture.child_assignment' in sql for sql, _ in self.db.calls))
        self.assertEqual(self.inserts()[0][1]['account'], ACCOUNT)
    def test_existing_outcome_stops_before_incoming_domain_validation_or_disclosure(self):
        with patch.object(create.outcomes, 'lookup_private', return_value=object()):
            with self.assertRaisesRegex(write.WriteError, '^operation_verification_unavailable$'):
                self.execute(cmd=command(answers={}))
        self.assertFalse(any('FROM kdg_capture.child' in sql for sql, _ in self.db.calls))
        self.assertEqual(self.inserts(), [])
    def test_capture_identity_is_distinct_from_operation_identity(self):
        with self.assertRaisesRegex(write.WriteError, '^validation_failed$'):
            self.execute(cmd=command(capture_id=OPERATION))
        self.assertEqual(self.inserts(), [])
        self.assertFalse(any('pg_advisory_xact_lock' in sql for sql, _ in self.db.calls))
    def test_missing_child_or_original_version_and_invalid_answers_do_not_write(self):
        for attribute, value, error in (('child', None, 'child_eligibility_unavailable'),
                ('version', None, 'questionnaire_version_unavailable'),
                ('version', dict(questionnaire_id=QUESTIONNAIRE, definition={}), 'questionnaire_version_unavailable')):
            self.db = Connection(); setattr(self.db, attribute, value)
            with self.subTest(attribute=attribute), self.assertRaisesRegex(write.WriteError, '^' + error + '$'):
                self.execute()
            self.assertEqual(self.inserts(), [])
        self.db = Connection()
        with self.assertRaisesRegex(write.WriteError, '^validation_failed$'): self.execute(cmd=command(answers={}))
        self.assertEqual(self.inserts(), [])
    def test_invalid_authority_shape_refuses_without_owner_sql(self):
        for membership, permission in (('0', 'kdg_capture.capture.create.all'), ('01', 'kdg_capture.capture.create.all'),
            ('9223372036854775808', 'kdg_capture.capture.create.all'), (7, 'kdg_capture.capture.create.all'),
            ('7', 'kdg_capture.capture.edit.own')):
            self.db = Connection()
            with self.subTest(membership=membership, permission=permission), self.assertRaisesRegex(write.WriteError, '^invalid_write_context$'):
                self.execute(permission, membership)
            self.assertFalse(any('kdg_capture.' in sql for sql, _ in self.db.calls))
        self.context = write.VerifiedContext(ORG, ACCOUNT, ACTOR, 'all_write', self.now)
        with self.assertRaisesRegex(write.WriteError, '^invalid_write_context$'): self.execute()
    def test_lock_and_lookup_order_and_explicit_parent_scope(self):
        self.execute()
        statements = [sql for sql, _ in self.db.calls]
        operation_lock = next(i for i, sql in enumerate(statements) if 'pg_advisory_xact_lock' in sql)
        lookup = next(i for i, sql in enumerate(statements) if 'FROM kdg_capture.operation_outcome' in sql)
        child_lock = next(i for i, sql in enumerate(statements) if 'hashtextextended' in sql)
        child_read = next(i for i, sql in enumerate(statements) if 'FROM kdg_capture.child WHERE' in sql)
        self.assertLess(operation_lock, lookup); self.assertLess(lookup, child_lock); self.assertLess(child_lock, child_read)
        for sql, args in self.db.calls:
            if sql in (create.ELIGIBILITY, create.ASSIGNMENT):
                self.assertEqual((args['org'], args['account'], args['child']), (ORG, ACCOUNT, CHILD))
    def test_history_failure_rolls_back_without_ack_or_sensitive_error(self):
        self.db.fail_history = True
        with self.assertRaisesRegex(write.WriteError, '^internal_error$') as failed: self.execute()
        self.assertNotIn('canary', str(failed.exception))
        self.assertIn(('EXIT_WITH_ERROR', {}), self.db.calls)
        self.assertNotIn(('COMMIT', {}), self.db.calls)
    def test_late_parent_fetch_stops_before_writes(self):
        original = Rows.one_or_none
        def late(row):
            if row.value is self.db.version: self.now = 111
            return original(row)
        with patch.object(Rows, 'one_or_none', late), self.assertRaisesRegex(write.WriteError, '^execution_timeout$'): self.execute()
        self.assertEqual(self.inserts(), [])


if __name__ == '__main__': unittest.main()
