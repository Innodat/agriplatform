"""Synthetic storage adapter acceptance; not PostgreSQL/RLS/commit qualification."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from datetime import datetime,timezone
from uuid import UUID

ROOT=Path(__file__).resolve().parents[3]
source=ROOT/'apps/kdg-capture/write-candidate/operation_outcomes.py'
spec=importlib.util.spec_from_file_location('kdg_outcome_candidate',source)
candidate=importlib.util.module_from_spec(spec);spec.loader.exec_module(candidate)
write=candidate.write
support_spec=importlib.util.spec_from_file_location('kdg_outcome_connection_support',ROOT/'apps/kdg-capture/write-tools/test_transaction_context.py')
support=importlib.util.module_from_spec(support_spec);support_spec.loader.exec_module(support)
ORG='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
ACCOUNT='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'
ACTOR='cccccccc-cccc-4ccc-8ccc-cccccccccccc'
OPERATION='dddddddd-dddd-4ddd-8ddd-dddddddddddd'
CAPTURE='eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee'
INTERNAL='ffffffff-ffff-4fff-8fff-ffffffffffff'

def receipt():return dict(operation_id=OPERATION,command_type='capture.create',command_version=1,status='committed',result=dict(capture_id=CAPTURE,revision='8'))
def row():return dict(id=UUID(INTERNAL),org_id=UUID(ORG),executor_account_id=UUID(ACCOUNT),executor_actor_id=UUID(ACTOR),command_type='capture.create',operation_id=UUID(OPERATION),command_version=1,result_version=1,result=dict(capture_id=CAPTURE,revision='8'),initiator_actor_id=UUID(ACTOR),committed_at=datetime(2026,10,23,tzinfo=timezone.utc))

class Rows:
    def __init__(self,value):self.value=value
    def mappings(self):return self
    def one_or_none(self):return self.value

class Connection(support.Connection):
    def __init__(self):super().__init__();self.row=row();self.fail_read=False;self.fail_insert=False
    def execute(self,sql,parameters):
        from sqlalchemy.exc import SQLAlchemyError
        result=super().execute(sql,parameters);sql=str(sql)
        if 'FROM kdg_capture.operation_outcome' in sql:
            if self.fail_read:raise SQLAlchemyError('private read SQL and payload')
            return Rows(self.row)
        if sql.startswith('INSERT INTO kdg_capture.operation_outcome'):
            if self.fail_insert:raise SQLAlchemyError('private insert SQL and payload')
            return Rows(None)
        return result

class StorageAcceptance(unittest.TestCase):
    def setUp(self):
        self.now=100.0;clock=patch.object(write.time,'monotonic',side_effect=lambda:self.now);clock.start();self.addCleanup(clock.stop)
    def key(self,**changes):
        values=dict(owner_schema='kdg_capture',org_id=ORG,account_id=ACCOUNT,command_type='capture.create',operation_id=OPERATION);values.update(changes)
        return write.OutcomeKey(**values)
    def budget(self):
        if not hasattr(self, '_budget'):self._budget = write.Budget()
        return self._budget
    def context(self,mode='own_read'):return write.VerifiedContext(ORG,ACCOUNT,ACTOR,mode,self.now)
    def test_existing_scoped_outcome_recovers_original_compact_receipt(self):
        db=Connection();budget=self.budget()
        with write.transaction(db,budget,self.context()):found=candidate.lookup_private(db,budget,self.key(),self.context())
        self.assertIsNotNone(found,'existing scoped outcome must not become unresolved')
        self.assertEqual(found.receipt().model_dump(),receipt())
    def test_append_records_exact_caller_operation_without_commit(self):
        db=Connection();budget=self.budget();context=self.context('own_write')
        with write.transaction(db,budget,context):
            write.outcome_lock(db,budget,self.key(),context)
            result=candidate.append(db,budget,self.key(),context,outcome_id=INTERNAL,receipt=receipt())
            inserts=[(sql,args) for sql,args in db.calls if sql.startswith('INSERT INTO kdg_capture.operation_outcome')]
            self.assertEqual(len(inserts),1,'one explicit outcome append is required')
            self.assertNotIn('COMMIT',[sql for sql,_ in db.calls])
            self.assertIsNone(result,'append cannot acknowledge a durable commit')

    def test_late_fetch_cannot_report_absence_or_receipt(self):
        owner = self
        class LateRows(Rows):
            def one_or_none(self):
                owner.now = 111
                return super().one_or_none()
        for value in (None, row()):
            self.now = 100
            db = Connection()
            with self.subTest(value=value is None), self.assertRaisesRegex(write.WriteError, '^execution_timeout$'):
                with write.transaction(db, self.budget(), self.context()):
                    with patch.object(candidate.write, 'execute', return_value=LateRows(value)):
                        candidate.lookup_private(db, self.budget(), self.key(), self.context())
                    self.fail('late discovery returned')


    def test_absence_is_distinct_from_failed_or_duplicate_read(self):
        from sqlalchemy.exc import MultipleResultsFound
        db = Connection(); db.row = None
        with write.transaction(db, self.budget(), self.context()):
            self.assertIsNone(candidate.lookup_private(db, self.budget(), self.key(), self.context()))
        for failure in ('sql', 'duplicate'):
            db = Connection(); db.fail_read = failure == 'sql'
            with self.subTest(failure=failure), self.assertRaisesRegex(write.WriteError, '^internal_error$') as failed:
                with write.transaction(db, self.budget(), self.context()):
                    if failure == 'duplicate':
                        with patch.object(Rows, 'one_or_none', side_effect=MultipleResultsFound('sensitive canary')):
                            candidate.lookup_private(db, self.budget(), self.key(), self.context())
                    else:
                        candidate.lookup_private(db, self.budget(), self.key(), self.context())
            self.assertTrue(failed.exception.__suppress_context__)
            self.assertNotIn('COMMIT', [sql for sql, _ in db.calls])

    def test_read_binds_every_scope_component(self):
        db = Connection()
        with write.transaction(db, self.budget(), self.context()):
            found = candidate.lookup_private(db, self.budget(), self.key(), self.context())
        sql, args = next((sql, args) for sql, args in db.calls if 'FROM kdg_capture.operation_outcome' in sql)
        self.assertEqual(args, dict(org=ORG, account=ACCOUNT, command='capture.create', operation=OPERATION))
        for predicate in ('org_id=CAST(:org AS uuid)', 'executor_account_id=CAST(:account AS uuid)', 'command_type=:command', 'operation_id=CAST(:operation AS uuid)'):
            self.assertIn(predicate, sql)
        self.assertEqual(found.receipt().result.revision, '8')
        self.assertNotIn('target_id', sql)

    def test_foreign_or_unsupported_stored_rows_never_become_absence(self):
        cases = [(field, INTERNAL) for field in ('org_id', 'executor_account_id', 'operation_id')]
        cases += [('command_type', 'capture.edit'), ('command_version', 2), ('command_version', True),
                  ('result_version', 1.0), ('result_version', 2), ('id', None), ('id', OPERATION),
                  ('executor_actor_id', '00000000-0000-0000-0000-000000000000'),
                  ('committed_at', datetime(2026,10,23)), ('unknown', 'sensitive canary'),
                  ('result', dict(capture_id=CAPTURE, revision='8', payload='sensitive canary')),
                  ('result', dict(capture_id=CAPTURE, revision='9223372036854775808'))]
        for field, value in cases:
            db = Connection(); db.row = {**row(), field: value}
            with self.subTest(field=field, value=value), self.assertRaisesRegex(write.WriteError, '^operation_verification_unavailable$'):
                with write.transaction(db, self.budget(), self.context()):
                    candidate.lookup_private(db, self.budget(), self.key(), self.context())
            self.assertNotIn('COMMIT', [sql for sql, _ in db.calls])

    def test_append_receipt_is_closed_strict_and_key_matched(self):
        cases = [('operation_id', INTERNAL), ('command_type', 'capture.edit'), ('command_version', True),
                 ('command_version', '1'), ('command_version', 2), ('status', 'pending'),
                 ('unknown', 'sensitive canary')]
        for field, value in cases:
            db = Connection(); context = self.context('own_write')
            with self.subTest(field=field), self.assertRaisesRegex(write.WriteError, '^invalid_command$'):
                with write.transaction(db, self.budget(), context):
                    candidate.append(db, self.budget(), self.key(), context, outcome_id=INTERNAL, receipt={**receipt(), field:value})
            self.assertFalse(any(sql.startswith('INSERT') for sql, _ in db.calls))

    def test_result_revision_and_uuid_bounds(self):
        for revision in ('0', '-1', '01', '1.0', 1, True, '9223372036854775808', '1'*100, '1\n'):
            with self.subTest(revision=revision), self.assertRaises(ValueError):
                candidate.CaptureResult(capture_id=CAPTURE, revision=revision)
        for identifier in (CAPTURE.upper(), UUID(CAPTURE), None, '00000000-0000-0000-0000-000000000000'):
            with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                candidate.CaptureResult(capture_id=identifier, revision='1')
        for revision in ('1', '9223372036854775807'):
            self.assertEqual(candidate.CaptureResult(capture_id=CAPTURE, revision=revision).revision, revision)

    def test_invalid_contexts_refuse_before_owner_sql(self):
        for key in (self.key(owner_schema='another'), self.key(org_id=INTERNAL), self.key(account_id=INTERNAL), self.key(command_type='other.command')):
            db = Connection()
            with write.transaction(db, self.budget(), self.context()):
                before = len(db.calls)
                with self.assertRaisesRegex(write.WriteError, '^invalid_write_context$'):
                    candidate.lookup_private(db, self.budget(), key, self.context())
                self.assertEqual(len(db.calls), before)
        db = Connection()
        with self.assertRaisesRegex(write.WriteError, '^invalid_write_context$'):
            candidate.lookup_private(db, self.budget(), self.key(), self.context())
        for mode in ('own_read', 'all_read'):
            db = Connection(); context = self.context(mode)
            with write.transaction(db, self.budget(), context):
                with self.assertRaisesRegex(write.WriteError, '^invalid_write_context$'):
                    candidate.append(db, self.budget(), self.key(), context, outcome_id=INTERNAL, receipt=receipt())

    def test_insert_is_plain_server_attributed_and_both_commands_supported(self):
        import json
        for command in ('capture.create', 'capture.edit'):
            db = Connection(); context = self.context('all_write'); key = self.key(command_type=command)
            value = {**receipt(), 'command_type':command}
            with write.transaction(db, self.budget(), context):
                self.assertIsNone(candidate.append(db, self.budget(), key, context, outcome_id=INTERNAL, receipt=value))
            sql, args = next((sql, args) for sql, args in db.calls if sql.startswith('INSERT'))
            self.assertIn('statement_timestamp()', sql)
            self.assertNotIn('ON CONFLICT', sql); self.assertNotIn('RETURNING', sql)
            self.assertEqual(args, dict(org=ORG, account=ACCOUNT, command=command, operation=OPERATION,
                                      id=INTERNAL, actor=ACTOR, version=1, result=json.dumps(value['result'], separators=(',', ':'))))
            db.row['command_type'] = command
            with write.transaction(db, self.budget(), self.context()):
                self.assertEqual(candidate.lookup_private(db, self.budget(), key, self.context()).receipt().model_dump(), value)

    def test_insert_sql_failure_has_no_acknowledgement_or_following_work(self):
        db = Connection(); db.fail_insert = True; context = self.context('own_write')
        with self.assertRaisesRegex(write.WriteError, '^internal_error$') as failed:
            with write.transaction(db, self.budget(), context):
                candidate.append(db, self.budget(), self.key(), context, outcome_id=INTERNAL, receipt=receipt())
                self.fail('following owner work ran')
        self.assertTrue(failed.exception.__suppress_context__)
        self.assertNotIn('COMMIT', [sql for sql, _ in db.calls])

    def test_invalid_internal_id_and_autocommit_cannot_insert(self):
        for invalid in (None, UUID(INTERNAL), INTERNAL.upper(), OPERATION):
            db = Connection(); context = self.context('own_write')
            with write.transaction(db, self.budget(), context):
                with self.assertRaisesRegex(write.WriteError, '^invalid_command$'):
                    candidate.append(db, self.budget(), self.key(), context, outcome_id=invalid, receipt=receipt())
            self.assertFalse(any(sql.startswith('INSERT') for sql, _ in db.calls))
        db = Connection(); db.active = True; db.autocommit = True
        with self.assertRaisesRegex(write.WriteError, '^invalid_write_context$'):
            candidate.lookup_private(db, self.budget(), self.key(), self.context())
        self.assertEqual(db.calls, [])

    def test_diagnostics_redact_models_and_invalid_inputs(self):
        from pydantic import ValidationError
        model = candidate.StoredOutcome.model_validate({**row(), **{key:str(value) for key, value in row().items() if isinstance(value, UUID)}})
        self.assertEqual(repr(model), '<StoredOutcome redacted>')
        self.assertNotIn(CAPTURE, str(model.receipt()))
        with self.assertRaises(ValidationError) as failed:
            candidate.CaptureResult(capture_id='sensitive canary', revision='1')
        self.assertNotIn('sensitive canary', str(failed.exception))

    def test_original_budget_bounds_lookup_after_elapsed_owner_work(self):
        db = Connection(); budget = self.budget(); context = self.context()
        with self.assertRaisesRegex(write.WriteError, '^execution_timeout$'), write.transaction(db, budget, context):
            self.now = 109.5
            candidate.lookup_private(db, budget, self.key(), context)
            sql_index = next(i for i, (sql, _) in enumerate(db.calls) if 'FROM kdg_capture.operation_outcome' in sql)
            self.assertEqual(db.calls[sql_index - 1][1], dict(statement='500', lock='500'))
            self.now = 110
            candidate.lookup_private(db, budget, self.key(), context)
        self.assertNotIn('COMMIT', [sql for sql, _ in db.calls])

    def test_duplicate_insert_aborts_without_following_work(self):
        from sqlalchemy.exc import IntegrityError
        class Duplicate(Connection):
            def execute(self, sql, parameters):
                if str(sql).startswith('INSERT INTO kdg_capture.operation_outcome'):
                    raise IntegrityError('sensitive SQL', parameters, Exception('unique violation'))
                return super().execute(sql, parameters)
        db = Duplicate(); budget = self.budget(); context = self.context('own_write')
        with self.assertRaisesRegex(write.WriteError, '^internal_error$'):
            with write.transaction(db, budget, context):
                candidate.append(db, budget, self.key(), context, outcome_id=INTERNAL, receipt=receipt())
                self.fail('duplicate allowed following owner work')
        self.assertNotIn('COMMIT', [sql for sql, _ in db.calls])
        self.assertIn('EXIT_WITH_ERROR', [sql for sql, _ in db.calls])

    def test_supported_owner_import_reuses_one_helper_identity(self):
        spec = importlib.util.spec_from_file_location('second_owner_storage_import', source)
        other = importlib.util.module_from_spec(spec); spec.loader.exec_module(other)
        self.assertIs(other.write, candidate.write)
        self.assertIs(other.write.VerifiedContext, candidate.write.VerifiedContext)
        self.assertIs(other.write.OutcomeKey, candidate.write.OutcomeKey)
        db = Connection(); budget = self.budget(); context = self.context()
        with other.write.transaction(db, budget, context):
            self.assertIsNotNone(other.lookup_private(db, budget, self.key(), context))

if __name__=='__main__':unittest.main()
