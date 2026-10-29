"""Offline candidate DDL/binding checks; coordinator owns actual restricted SQL proof."""
from io import StringIO
import importlib.util
from pathlib import Path
import unittest
from alembic.migration import MigrationContext
from alembic.operations import Operations
import test_provision as support

SOURCE=Path(__file__).resolve().parents[1]/'migrations/candidates/0003_provision_eligibility.py'
spec=importlib.util.spec_from_file_location('kdg_provision_eligibility_candidate',SOURCE)
candidate=importlib.util.module_from_spec(spec);spec.loader.exec_module(candidate)

def render():
 output=StringIO()
 context=MigrationContext.configure(dialect_name='postgresql',opts={'as_sql':True,'output_buffer':output})
 with Operations.context(context):candidate.upgrade()
 return output.getvalue()

class ProvisionPrivilegeCandidate(unittest.TestCase):
 def test_linked_upgrade_is_column_scoped_and_keeps_server_default_time(self):
  self.assertEqual(candidate.down_revision,'0002_kdg_capture_storage')
  sql=render();grant=next(part for part in sql.split(';') if 'GRANT INSERT' in part)
  self.assertIn('INSERT (org_id,ref,account_id,membership_id,child_id,child_revision,',grant)
  self.assertNotIn('issued_at',grant)
  self.assertIn('ON kdg_capture.child_eligibility TO kdg_capture_runtime',grant)
  for forbidden in ['GRANT UPDATE','GRANT DELETE','CREATE FUNCTION','CREATE ROLE','CREATE TABLE','ALTER DEFAULT','DISABLE ROW','DROP ',' TO PUBLIC']:
   self.assertNotIn(forbidden,sql)
  with self.assertRaisesRegex(RuntimeError,'^kdg_migration_downgrade_prohibited$'):candidate.downgrade()
 def test_issuance_policy_requires_exact_own_write_evidence_and_scope(self):
  sql=render()
  for expected in ["current_setting('app.mode', true) = 'own_write'",'FOR INSERT TO kdg_capture_runtime',
   "org_id = current_setting('app.org_id', true)::uuid", "account_id = current_setting('app.account_id', true)::uuid",
   "issued_by = current_setting('app.actor_id', true)::uuid", "membership_id = nullif(current_setting('app.provision_membership_id', true), '')::bigint",
   "create_permission = current_setting('app.provision_create_permission', true)"]:
   self.assertIn(expected,sql)
  self.assertNotIn('all_write',sql);self.assertNotIn('all_read',sql)

class ProvisionEvidenceBinding(unittest.IsolatedAsyncioTestCase):
 setUp=support.ProvisionAcceptance.setUp
 execute=support.ProvisionAcceptance.execute
 denied=support.ProvisionAcceptance.denied
 async def test_owner_local_binding_uses_verified_membership_and_selected_permission_before_issuance(self):
  self.denied(support.provision.create.ALL)
  await self.execute()
  calls=self.db.calls
  index=next(i for i,(sql,args) in enumerate(calls) if sql==support.provision.BIND_ISSUANCE)
  self.assertEqual(calls[index][1],{'member':'7','permission':support.provision.create.ASSIGNED})
  issue=next(i for i,(sql,args) in enumerate(calls) if sql==support.provision.ISSUE_BATCH)
  self.assertLess(index,issue);self.assertEqual(calls[-1][0],'COMMIT')
 async def test_no_creation_authority_never_binds_issuance(self):
  self.denied(support.provision.create.ALL,support.provision.create.ASSIGNED)
  await self.execute()
  self.assertFalse(any(sql==support.provision.BIND_ISSUANCE for sql,args in self.db.calls))
