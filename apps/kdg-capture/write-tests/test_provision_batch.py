"""Protect provision semantics before removing native N+1 roundtrips.

Recorded connections establish control flow only. Coordinator owns actual restricted
1000-child success, PostgreSQL locks, timeout and rollback qualification.
"""
from types import SimpleNamespace
from unittest.mock import patch
import unittest
import test_provision as support

provision=support.provision

class ProvisionBatchAcceptance(unittest.IsolatedAsyncioTestCase):
 setUp=support.ProvisionAcceptance.setUp
 execute=support.ProvisionAcceptance.execute
 denied=support.ProvisionAcceptance.denied
 install_children=support.ProvisionAcceptance.install_children

 async def test_post_lock_current_revisions_and_labels_are_used_for_each_selected_child(self):
  rows,assignments=self.install_children(3);self.denied(provision.create.ALL)
  def changed():
   rows[1].update(revision=99,display_name='Current child')
   assignments[rows[1]['id']]['revision']=101
  self.db.on_lock=changed
  result=await self.execute()
  self.assertEqual([child.child_id for child in result.children],[row['id'] for row in rows])
  self.assertEqual((result.children[1].child_revision,result.children[1].child_label,result.children[1].assignment.assignment_revision),('99','Current child','101'))
  self.assertEqual(len({child.child_eligibility_ref for child in result.children}),3)
  for child,issued in zip(result.children,self.db.issued,strict=True):
   self.assertEqual((issued['child'],issued['revision'],issued['ref'],issued['actor'],issued['member'],issued['permission']),
    (child.child_id,int(child.child_revision),child.child_eligibility_ref,support.ACTOR,7,provision.create.ASSIGNED))
  self.assertEqual(self.db.calls[-1][0],'COMMIT')

 async def test_later_invalid_recheck_withholds_complete_setup_and_commit(self):
  rows,assignments=self.install_children(3);self.denied(provision.create.ALL)
  self.db.on_lock=lambda:assignments[rows[-1]['id']].update(membership_id=8)
  with self.assertRaises(provision.protected.HandlerError) as error:await self.execute()
  self.assertEqual(error.exception.error_id,'provision_unavailable')
  self.assertNotIn('COMMIT',[sql for sql,args in self.db.calls])
  self.assertEqual(self.db.calls[-1][0],'EXIT_WITH_ERROR')

 async def test_thousand_children_use_bounded_sql_roundtrips_without_relaxing_semantics(self):
  # A count oracle, not a latency or native-permission claim. Existing deadline
  # tests and coordinator native acceptance keep the production ten-second budget.
  with patch.object(provision.write,'time',SimpleNamespace(monotonic=lambda:100.)):
   self.install_children(1000);self.denied(provision.create.ALL)
   result=await self.execute()
  self.assertEqual(len(result.children),1000)
  self.assertEqual(len(self.db.issued),1000)
  self.assertLessEqual(len(self.db.calls),20)

 async def test_unordered_batch_returning_is_correlated_by_reference_not_position(self):
  rows,_=self.install_children(3)
  self.db.return_issuance=lambda issued:list(reversed(issued))
  result=await self.execute()
  self.assertEqual([child.child_id for child in result.children],[row['id'] for row in rows])
  self.assertEqual([child.child_eligibility_ref for child in result.children],[row['ref'] for row in self.db.issued])

 async def test_missing_duplicate_unknown_or_cross_child_batch_result_rolls_back(self):
  for change in ('missing','duplicate','unknown','cross_child','invalid_time'):
   with self.subTest(change=change):
    self.setUp();rows,_=self.install_children(3)
    def alter(issued):
     if change=='missing':return issued[:-1]
     if change=='duplicate':return [issued[0],issued[0],issued[2]]
     if change=='unknown':issued[0]['ref']='x'*43
     if change=='cross_child':issued[0]['child_id']=rows[1]['id']
     if change=='invalid_time':issued[0]['issued_at']='invalid'
     return issued
    self.db.return_issuance=alter
    with self.assertRaises(provision.protected.HandlerError) as error:await self.execute()
    self.assertEqual(error.exception.error_id,'provision_unavailable')
    self.assertNotIn('COMMIT',[sql for sql,args in self.db.calls])
    self.assertEqual(self.db.calls[-1][0],'EXIT_WITH_ERROR')

 async def test_incomplete_or_unordered_lock_result_prevents_reread_and_issuance(self):
  for change in ('missing','duplicate','reverse'):
   self.setUp();self.install_children(3);original=self.db.execute
   def execute(sql,args):
    value=original(sql,args)
    if str(sql)==provision.LOCK_CHILDREN:
     if change=='missing':return support.Rows(value.value[:-1])
     if change=='duplicate':return support.Rows([value.value[0]]*3)
     return support.Rows(list(reversed(value.value)))
    return value
   self.db.execute=execute
   with self.assertRaises(provision.protected.HandlerError):await self.execute()
   self.assertEqual(self.db.issued,[])
   self.assertFalse(any(sql in (provision.CHILDREN_AFTER_LOCK,provision.ASSIGNED_AFTER_LOCK) for sql,args in self.db.calls))

 def test_lock_expression_uses_exact_shared_namespace_after_uuid_sort(self):
  # PostgreSQL17 SELECT List guarantees output-expression evaluation after sort
  # when the expression is not a DISTINCT/GROUP/ORDER key; this is not ORDER BY2.
  sql=provision.LOCK_CHILDREN
  self.assertIn("'kdg_capture:child:v1:' || :org || ':' || child_id::text,0)",sql)
  self.assertTrue(sql.endswith('ORDER BY child_id'))
  self.assertNotIn('DISTINCT',sql);self.assertNotIn('GROUP BY',sql);self.assertNotIn('LIMIT',sql)
