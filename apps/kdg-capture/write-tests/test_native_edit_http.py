"""Native PUT qualification guards; no database setup or native writes."""
import copy
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations/tests'))
import qualify_edit_http as q

class NativeEditHTTP(unittest.TestCase):
    def test_response_requires_released_lease_and_exact_private_wire_result(self):
        result=dict(status=200,body={'receipt':'original'},cache_control='private, no-store',leased=0)
        q.verify_observation(result,200,{'receipt':'original'})
        for field,value in [('status',500),('body',{}),('cache_control','public'),('leased',1)]:
            changed=dict(result,**{field:value})
            with self.subTest(field=field),self.assertRaises(AssertionError):
                q.verify_observation(changed,200,{'receipt':'original'})


    def test_plan_covers_replay_stale_invalid_scopes_denials_and_original_retry(self):
        data,plan=q.new_plan();matrix=q.cases(data,plan)
        self.assertEqual(len(matrix),19)
        replay=next(c for c in matrix if c['label']=='committed_replay')
        self.assertNotEqual(replay['path'],plan['create']['capture_id'])
        self.assertEqual(replay['command']['operation_id'],plan['answers']['operation_id'])
        self.assertEqual(replay['command']['expected_revision'],'1')
        self.assertIn(data.invalid_question,replay['command']['answers'])
        self.assertEqual([c['name'] for c in matrix[-3:]],['retry']*3)
        self.assertEqual(len([c for c in matrix if c.get('denied')]),4)

    def test_replay_and_noop_storage_oracle_rejects_hidden_mutations(self):
        from test_native_own_edit import NativeOwnEdit
        data,plan,rows=NativeOwnEdit().oracle_rows(('create','answers','date','noop'))
        q.verify_transition(rows,copy.deepcopy(rows),unchanged=True)
        for table in rows:
            damaged=copy.deepcopy(rows);damaged[table].append({'hidden':'write'})
            with self.assertRaises(AssertionError):q.verify_transition(rows,damaged,unchanged=True)
        damaged=copy.deepcopy(rows);damaged['capture'][0]['updated_at']='2026-10-25T11:00:00+00:00'
        with self.assertRaises(AssertionError):q.verify_transition(rows,damaged,noop=True)
        damaged=copy.deepcopy(rows);damaged['operation_outcome'][1]['result']['revision']='3'
        with self.assertRaises(AssertionError):q.own.verify_rows(data,plan,['create','answers','date','noop'],damaged)

    def harness(self):
        from contextlib import ExitStack
        stack=ExitStack();self.addCleanup(stack.close)
        for name,result in [('retained',({'urls':{'runtime':'synthetic'}},{},object())),
            ('migration_qualified','applied'),('identities',{}),('sentinel',None),('revision',q.fixture.STORAGE)]:
            stack.enter_context(patch.object(q.fixture,name,return_value=result))
        stack.enter_context(patch.object(q,'source_hashes',return_value=q.INITIAL_SOURCES))
        stack.enter_context(patch.object(q,'snapshot',return_value={}))
        stack.enter_context(patch.object(q,'table_counts',side_effect=[{t:0 for t in q.DELTAS},q.DELTAS]))
        stack.enter_context(patch.object(q.commit,'seed'))
        stack.enter_context(patch.object(q.fixture,'engine'))
        stack.enter_context(patch.object(q.commit,'execute',side_effect=lambda engine,data,raw:
            dict(operation_id=json.loads(raw)['operation_id'],command_type='capture.create',command_version=1,
                status='committed',result=dict(capture_id=json.loads(raw)['capture_id'],revision='1'))))
        stack.enter_context(patch.object(q,'read_storage',return_value=({},dict(verified=True))))
        async def exercise(value,data,plan,attempt,rows,names):
            attempt['cases'].extend(case['label'] for case in attempt['http_plan'])
            return dict(leases_released=True,physical_connections_disposed=True)
        stack.enter_context(patch.object(q,'exercise',side_effect=exercise))
        return stack.enter_context(patch.object(q.fixture,'receipt',return_value=Path('/tmp/attempt.json')))

    def test_journal_precedes_seed_and_retains_all_planned_inputs(self):
        receipt=self.harness()
        def seed(*args,**kwargs):
            self.assertEqual(receipt.call_args.args[0],'edit-http-start')
            journal=receipt.call_args.args[1]
            self.assertEqual(len(journal['http_plan']),19)
            self.assertIn('editor_actor_id',journal)
            self.assertIn('assignment_id',journal)
            self.assertNotIn('outcome_id',json.dumps(journal['plan']))
        with patch.object(q.commit,'seed',side_effect=seed):result=q.qualify({})
        self.assertTrue(result['qualified'])
        self.assertEqual([c.args[0] for c in receipt.call_args_list],['edit-http-start','edit-http'])

    def test_source_drift_before_import_execution_and_writes_is_bound(self):
        required={'platform/deployment/dev.py','platform/deployment/native_cli.py',
            'platform/deployment/environments/kdg-local.json',
            'apps/kdg-capture/migrations/tests/qualify_edit_http.py',
            'apps/kdg-capture/migrations/tests/qualify_own_edit.py',
            'apps/kdg-capture/write-candidate/edit_http.py'}
        self.assertTrue(required<=set(q.INITIAL_SOURCES))
        for sequence in ([{}],[q.INITIAL_SOURCES,{}],[q.INITIAL_SOURCES,q.INITIAL_SOURCES,{}]):
            with self.subTest(sequence=len(sequence)):
                receipt=self.harness()
                with patch.object(q,'source_hashes',side_effect=sequence),self.assertRaises(AssertionError):q.qualify({})
                self.assertLessEqual(receipt.call_count,1)

    def test_create_result_survives_independent_oracle_failure(self):
        receipt=self.harness()
        with patch.object(q,'read_storage',side_effect=ValueError('private-canary')),redirect_stdout(io.StringIO()) as output:
            self.assertEqual(q.main(['--qualify-retained']),1)
        record=receipt.call_args.args[1]
        self.assertFalse(record['qualified'])
        self.assertEqual(record['execution_results']['create']['receipt'],q.expected_receipt(record['plan'],'create'))
        self.assertNotIn('private-canary',str(record)+output.getvalue())

    def test_any_storage_or_http_failure_prevents_success(self):
        for target in ('exercise','verify_deltas','verify_preservation','read_storage'):
            with self.subTest(target=target):
                receipt=self.harness()
                with patch.object(q,target,side_effect=ValueError('private')),self.assertRaises(ValueError):q.qualify({})
                self.assertEqual(receipt.call_count,1)

    def test_journal_failure_cannot_seed(self):
        self.harness()
        with patch.object(q.fixture,'receipt',side_effect=OSError('private')),patch.object(q.commit,'seed') as seed,self.assertRaises(OSError):q.qualify({})
        seed.assert_not_called()

    def test_success_receipt_failure_is_safe_and_unqualified(self):
        self.harness()
        with patch.object(q.fixture,'receipt',side_effect=[Path('/tmp/start'),OSError('private'),Path('/tmp/failure')]) as receipt,redirect_stdout(io.StringIO()) as output:
            self.assertEqual(q.main(['--qualify-retained']),1)
        self.assertFalse(receipt.call_args.args[1]['qualified'])
        self.assertEqual(receipt.call_args.args[1]['failed_stage'],'success_receipt')
        self.assertNotIn('private',output.getvalue())

    def test_failure_record_retains_observed_execution_without_raw_exception(self):
        def fail(attempt):
            attempt.update(plan={'intended':'ids'},execution_results={'answers':{'status':200}},checks={})
            q.STAGE='answers_independent_storage';raise RuntimeError('credential-canary')
        with patch.object(q,'qualify',side_effect=fail),patch.object(q.fixture,'receipt',return_value=Path('/tmp/failure')) as receipt,redirect_stdout(io.StringIO()) as output:
            self.assertEqual(q.main(['--qualify-retained']),1)
        record=receipt.call_args.args[1]
        self.assertEqual(record['execution_results'],{'answers':{'status':200}})
        self.assertEqual(record['failed_stage'],'answers_independent_storage')
        self.assertNotIn('credential-canary',str(record)+output.getvalue())

    def test_retained_flag_is_mandatory(self):
        with patch.object(q,'qualify') as run,self.assertRaises(SystemExit),redirect_stdout(io.StringIO()):q.main([])
        run.assert_not_called()


    def test_source_read_failure_writes_safe_best_effort_attempt(self):
        import runpy
        original=Path.read_bytes
        def read(path):
            if path==q.ROOT/'platform/deployment/dev.py':raise OSError('source-secret-canary')
            return original(path)
        with patch.object(Path,'read_bytes',read),patch.object(q.fixture,'receipt',return_value=Path('/tmp/bootstrap')) as receipt,patch.object(sys,'argv',[q.__file__,'--qualify-retained']),redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as stopped:runpy.run_path(q.__file__,run_name='__main__')
        self.assertEqual(stopped.exception.code,1)
        self.assertEqual(receipt.call_args.args[1]['failed_stage'],'source_bootstrap')
        self.assertNotIn('source-secret-canary',str(receipt.call_args)+output.getvalue())

    def test_import_failure_writes_safe_best_effort_attempt(self):
        import builtins
        import runpy
        original=builtins.__import__
        def importing(name,*args,**kwargs):
            if name=='qualify_own_edit':raise ImportError('import-secret-canary')
            return original(name,*args,**kwargs)
        with patch.object(builtins,'__import__',importing),patch.object(q.fixture,'receipt',return_value=Path('/tmp/bootstrap')) as receipt,patch.object(sys,'argv',[q.__file__,'--qualify-retained']),redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as stopped:runpy.run_path(q.__file__,run_name='__main__')
        self.assertEqual(stopped.exception.code,1)
        self.assertEqual(receipt.call_args.args[1]['failed_stage'],'imports')
        self.assertNotIn('import-secret-canary',str(receipt.call_args)+output.getvalue())


    def test_response_effects_survive_json_decode_failure_without_private_content(self):
        from unittest.mock import Mock
        attempt=dict(execution_results={})
        response=Mock(status_code=500,headers={'cache-control':'private, no-store'})
        def decode():
            saved=attempt['execution_results']['native_fault']
            self.assertEqual(saved['status'],500)
            self.assertEqual(saved['leased'],0)
            self.assertEqual(saved['cache_control'],'private, no-store')
            self.assertEqual(saved['sql'],dict(capture_updates=1,history_inserts=0))
            self.assertTrue(saved['outcome_present_before_fault'])
            raise ValueError('raw-body-and-credential-canary')
        response.json.side_effect=decode
        with self.assertRaises(ValueError):q.retain_response(attempt,'native_fault',response,leased=0,
            sql=dict(capture_updates=1,history_inserts=0),permissions=['read','edit'],
            fault=dict(native_sqlstate='23514',outcome_present_before_fault=True))
        saved=attempt['execution_results']['native_fault']
        self.assertEqual(saved['body_decode_error_type'],'ValueError')
        self.assertNotIn('body',saved)
        self.assertNotIn('raw-body-and-credential-canary',json.dumps(attempt))
        response.json.return_value={'receipt':'original'};response.json.side_effect=None
        self.assertEqual(q.retain_response(attempt,'retry',response,leased=0,sql={},permissions=[])['body'],{'receipt':'original'})

    def test_json_decode_failure_reaches_safe_append_only_failure_record(self):
        from unittest.mock import Mock
        response=Mock(status_code=500,headers={'cache-control':'private, no-store'})
        response.json.side_effect=ValueError('private-body-canary')
        def fail(attempt):
            attempt['execution_results']={};q.STAGE='native_fault'
            q.retain_response(attempt,'native_fault',response,leased=0,
                sql=dict(capture_updates=1,history_inserts=0),permissions=[])
        with patch.object(q,'qualify',side_effect=fail),patch.object(q.fixture,'receipt',return_value=Path('/tmp/failure')) as receipt,redirect_stdout(io.StringIO()) as output:
            self.assertEqual(q.main(['--qualify-retained']),1)
        record=receipt.call_args.args[1]
        self.assertFalse(record['qualified'])
        self.assertEqual(record['execution_results']['native_fault']['body_decode_error_type'],'ValueError')
        self.assertEqual(record['execution_results']['native_fault']['sql']['capture_updates'],1)
        self.assertNotIn('private-body-canary',json.dumps(record)+output.getvalue())

    def test_scope_groups_follow_explicit_metadata_after_insertions_and_reordering(self):
        data,plan=q.new_plan();matrix=q.cases(data,plan)
        for sequence in (matrix,list(reversed(matrix)),matrix[:2]+[dict(matrix[0],foreign_org=True)]+matrix[2:]):
            flattened=[]
            for foreign,group in q.case_groups(sequence):
                group=list(group)
                self.assertTrue(all(bool(case.get('foreign_org',False))==foreign for case in group))
                flattened.extend(group)
            self.assertEqual(flattened,sequence)
        groups=[list(group) for foreign,group in q.case_groups(matrix)]
        account_group=next(group for group in groups if any(c['label']=='foreign_account' for c in group))
        labels=[c['label'] for c in account_group]
        self.assertEqual(labels[labels.index('foreign_account')+1],'scope_reuse')
        reused=next(c for c in account_group if c['label']=='scope_reuse')
        self.assertEqual(reused['receipt'],'answers')
        self.assertTrue(reused['unchanged'])
        self.assertFalse(reused.get('foreign_account',False))

    def test_refused_http_requires_exact_capability_sequence_and_zero_checkout(self):
        data,plan=q.new_plan()
        read='kdg_capture.capture.read.own';edit=q.edit.OWN
        for case in (c for c in q.cases(data,plan) if c.get('no_checkout')):
            expected=[read] if case.get('denied')==read else ([read,edit] if case.get('denied') else [])
            q.verify_admission(case,dict(permissions=expected),10,10)
            for wrong in ([],[read],[edit],[read,edit],[edit,read],[read,edit,edit]):
                if wrong==expected:continue
                with self.subTest(case=case['label'],wrong=wrong),self.assertRaises(AssertionError):
                    q.verify_admission(case,dict(permissions=wrong),10,10)
            with self.assertRaises(AssertionError):q.verify_admission(case,dict(permissions=expected),10,11)

    def test_each_capability_denies_fresh_and_committed_replay_without_writes(self):
        data,plan=q.new_plan();denied=[case for case in q.cases(data,plan) if case.get('denied')]
        for permission in ('kdg_capture.capture.read.own',q.edit.OWN):
            pair=[case for case in denied if case['denied']==permission]
            self.assertEqual({case['name'] for case in pair},{'retry','answers'})
            for case in pair:
                self.assertEqual(case['status'],403)
                self.assertEqual(case['error'],'access_denied')
                self.assertTrue(case['no_checkout'] and case['unchanged'])
            replay=next(case for case in pair if case['name']=='answers')
            self.assertEqual(plan[replay['name']]['operation_id'],plan['answers']['operation_id'])

if __name__=='__main__':unittest.main()
