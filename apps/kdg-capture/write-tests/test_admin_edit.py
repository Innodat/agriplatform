"""All-edit contracts use real candidate SQL and recorded doubles, never native RLS."""
import unittest
from unittest.mock import patch
import test_capture_edit as own
import admin_edit as edit

class AdminEditAcceptance(own.OwnEditAcceptance):
    def setUp(self):
        super().setUp()
        self.context=edit.write.VerifiedContext(own.ORG,own.ACCOUNT,own.ACTOR,'all_write',self.now)
        self.db.capture['owner_account_id']=own.CHILD
    def execute(self,cmd=None,permission='kdg_capture.capture.edit.all',capture=own.CAPTURE):
        with edit.write.transaction(self.db,self.budget,self.context):
            return edit.edit_in_transaction(self.db,self.budget,self.context,capture,cmd if cmd is not None else own.command(),permission=permission)
    def test_missing_or_foreign_target_uses_same_safe_failure(self):
        self.db.capture=None
        with self.assertRaisesRegex(edit.write.WriteError,'^capture_unavailable$'):self.execute()
        sql=next(sql for sql,_ in self.db.calls if 'FROM kdg_capture.capture WHERE' in sql)
        self.assertNotIn('owner_account_id=',sql)
        self.assertIn('org_id=CAST(:org AS uuid)',sql)
    def test_wrong_scope_permission_or_input_stops_before_business_sql(self):
        for permission in ('kdg_capture.capture.edit.own','kdg_capture.capture.create.all','kdg_capture.capture.read.all'):
            self.db=own.Connection()
            with self.assertRaisesRegex(edit.write.WriteError,'^invalid_write_context$'):self.execute(permission=permission)
            self.assertFalse(any('kdg_capture.' in sql for sql,_ in self.db.calls))
        self.context=edit.write.VerifiedContext(own.ORG,own.ACCOUNT,own.ACTOR,'own_write',self.now)
        with self.assertRaisesRegex(edit.write.WriteError,'^invalid_write_context$'):self.execute()
    def test_organization_sql_never_impersonates_original_owner(self):
        self.execute()
        for sql in (edit.CAPTURE,edit.UPDATE,edit.HISTORY_INSERT):
            self.assertNotIn('owner_account_id=CAST(:account AS uuid)',sql)
            self.assertIn('org_id=CAST(:org AS uuid)',sql)
        self.assertEqual(self.db.capture['owner_account_id'],own.CHILD)
