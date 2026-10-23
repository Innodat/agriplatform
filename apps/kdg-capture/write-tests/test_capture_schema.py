"""Offline Alembic smoke checks only; not PostgreSQL enforcement qualification."""
from io import StringIO
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'apps/kdg-capture/migrations/candidates/0002_capture_storage.py'
spec = importlib.util.spec_from_file_location('kdg_linked_storage_candidate', SOURCE)
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)


def render():
    output = StringIO()
    context = MigrationContext.configure(
        dialect_name='postgresql', opts={'as_sql': True, 'output_buffer': output},
    )
    with Operations.context(context):
        candidate.upgrade()
    return output.getvalue()


class OfflineStorageAcceptance(unittest.TestCase):
    def test_linked_capture_history_and_outcome_ddl_is_rendered_without_connection(self):
        with patch('sqlalchemy.create_engine', side_effect=AssertionError('connection forbidden')):
            sql = render()
        for table in ('capture', 'capture_revision', 'operation_outcome'):
            self.assertIn('CREATE TABLE kdg_capture.' + table + ' (', sql)

    def test_active_alembic_head_is_unchanged(self):
        scripts = ScriptDirectory.from_config(Config(str(ROOT / 'apps/kdg-capture/alembic.ini')))
        self.assertEqual(scripts.get_heads(), ['0001_kdg_foundation'])
        self.assertNotIn(candidate.revision, [item.revision for item in scripts.walk_revisions()])

    def test_snapshot_completeness_guard_is_deferred_to_transaction_end(self):
        sql = render()
        self.assertIn('CREATE CONSTRAINT TRIGGER capture_snapshot_present', sql)
        self.assertIn('DEFERRABLE INITIALLY DEFERRED FOR EACH ROW', sql)

    def test_composite_links_and_current_revision_fk_are_rendered(self):
        sql = render()
        self.assertIn('FOREIGN KEY(org_id, questionnaire_id, questionnaire_version_id)', sql)
        self.assertIn('FOREIGN KEY(org_id, outcome_id, executor_account_id, executor_actor_id, command_type, operation_id, capture_id, revision)', sql)
        self.assertIn('fk_capture_current_revision', sql)
        self.assertIn('DEFERRABLE INITIALLY DEFERRED', sql)

    def test_outcome_relational_values_are_derived_without_changing_adapter_columns(self):
        sql = render()
        self.assertIn("GENERATED ALWAYS AS ((result->>'capture_id')::uuid) STORED", sql)
        self.assertIn("GENERATED ALWAYS AS ((result->>'revision')::bigint) STORED", sql)
        self.assertIn('UNIQUE (org_id, executor_account_id, command_type, operation_id)', sql)
        self.assertNotIn('fingerprint', sql.lower())

    def test_candidate_does_not_create_resources_seed_data_or_delete_rows(self):
        sql = render().upper()
        for forbidden in ('CREATE ROLE', 'CREATE SCHEMA', 'CREATE DATABASE', 'INSERT INTO',
                          'DELETE FROM', 'DROP TABLE', 'TRUNCATE ', 'SECURITY DEFINER'):
            self.assertNotIn(forbidden, sql)
        with self.assertRaisesRegex(RuntimeError, '^kdg_migration_downgrade_prohibited$'):
            candidate.downgrade()

    def test_rls_and_grants_keep_outcomes_caller_scoped_and_parent_writes_ungranted(self):
        sql = render()
        self.assertIn('ALTER TABLE kdg_capture.capture FORCE ROW LEVEL SECURITY', sql)
        self.assertIn('ALTER TABLE kdg_capture.operation_outcome FORCE ROW LEVEL SECURITY', sql)
        policy = next(part for part in sql.split(';') if 'CREATE POLICY runtime_read ON kdg_capture.operation_outcome' in part)
        self.assertIn("executor_account_id = current_setting('app.account_id', true)::uuid", policy)
        self.assertNotRegex(policy, r'\bOR\b')
        self.assertNotIn('GRANT INSERT ON kdg_capture.child', sql)
        self.assertNotIn('GRANT DELETE', sql)
        self.assertNotIn(' TO PUBLIC', sql)

    def test_rendering_is_deterministic_and_leaves_active_history_unchanged(self):
        self.assertEqual(render(), render())
        self.assertEqual(candidate.down_revision, '0001_kdg_foundation')
        self.test_active_alembic_head_is_unchanged()

    def test_reported_outcome_revision_has_deferred_history_reference(self):
        sql = render()
        self.assertIn('fk_outcome_reported_revision', sql)
        self.assertIn('FOREIGN KEY(org_id, capture_id, result_revision)', sql)

    def test_own_write_outcome_requires_visible_owned_target(self):
        sql = render()
        policy = next(part for part in sql.split(';') if 'CREATE POLICY runtime_append ON kdg_capture.operation_outcome' in part)
        self.assertIn('EXISTS (SELECT 1 FROM kdg_capture.capture c', policy)
        self.assertIn('c.id = operation_outcome.capture_id', policy)
        self.assertIn('c.owner_account_id', policy)

    def test_history_side_checks_real_snapshot_and_null_safe_initiator(self):
        sql = render()
        self.assertIn('history_snapshot_invalid', sql)
        self.assertIn('o.initiator_actor_id IS NOT DISTINCT FROM NEW.initiator_actor_id', sql)
        self.assertIn('ROW(c.revision,c.observation_date,c.answers,c.captured_at,c.updated_by)', sql)
        self.assertIn('ROW(NEW.revision,NEW.observation_date,NEW.answers,NEW.captured_at,NEW.executor_actor_id)', sql)
        self.assertIn('ROW(r.revision,r.observation_date,r.answers,r.captured_at,r.executor_actor_id)', sql)
        self.assertIn('ROW(NEW.revision,NEW.observation_date,NEW.answers,NEW.captured_at,NEW.updated_by)', sql)

    def test_alternate_writer_clock_and_blank_constraints_match_input_contract(self):
        sql = render()
        self.assertIn('([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]', sql)
        self.assertIn('chr(9)', sql)
        self.assertIn('chr(12288)', sql)

    def test_blankness_characters_match_python_input_validation(self):
        self.assertEqual(set(candidate.WHITESPACE), {value for value in range(0x110000) if chr(value).isspace()})


if __name__ == '__main__':
    unittest.main()
