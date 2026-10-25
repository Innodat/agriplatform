"""Behavioral guards for the native own-edit qualification and its independent oracle."""
import copy
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations/tests'))
import qualify_own_edit as q

class NativeOwnEdit(unittest.TestCase):
    def test_native_plan_preserves_partial_inputs_and_failed_retry_identity(self):
        data,plan=q.new_plan()
        self.assertEqual(plan['answers']['observation_date'],plan['create']['observation_date'])
        self.assertEqual(plan['date']['answers'],plan['answers']['answers'])
        self.assertEqual(plan['noop']['answers'],plan['date']['answers'])
        self.assertEqual(plan['noop']['expected_revision'],'3')
        self.assertEqual(plan['stale']['expected_revision'],'2')
        self.assertEqual(plan['retry']['expected_revision'],'3')
        self.assertNotIn('outcome_id',plan['retry'])
        self.assertNotEqual(data.actor,data.editor)
        identities=[v['operation_id'] for k,v in plan.items()]
        self.assertEqual(len(identities),len(set(identities)))


    def oracle_rows(self,names=('create','answers','date','noop','retry')):
        data,plan=q.new_plan()
        common=dict(org_id=data.org,owner_account_id=data.account,owner_actor_id=data.actor,
            child_id=data.child,questionnaire_id=data.questionnaire,questionnaire_version_id=data.version,
            captured_at=plan['create']['captured_at'])
        history=[];outcomes=[]
        for name in names:
            command=plan[name];expected=q.expected_receipt(plan,name)
            actor=data.actor if name=='create' else data.editor
            evidence=dict(org_id=data.org,executor_account_id=data.account,executor_actor_id=actor,initiator_actor_id=actor,
                operation_id=command['operation_id'],command_type=expected['command_type'])
            outcome=dict(evidence,id='internal-'+name,capture_id=plan['create']['capture_id'],result=expected['result'],
                result_revision=int(expected['result']['revision']),command_version=1,result_version=1)
            outcomes.append(outcome)
            if name!='noop':
                history.append(dict(common,**{k:v for k,v in evidence.items() if k!='org_id'},
                    capture_id=plan['create']['capture_id'],revision=outcome['result_revision'],outcome_id=outcome['id'],
                    answers=command['answers'],observation_date=command['observation_date']))
        current=history[-1]
        capture=dict(common,id=plan['create']['capture_id'],revision=current['revision'],answers=current['answers'],
            observation_date=current['observation_date'],created_by=data.actor,
            updated_by=data.actor if len(history)==1 else data.editor,child_eligibility_ref=data.ref,
            creator_membership_id=int(data.membership),created_at='2026-10-25T10:00:00+00:00',updated_at='2026-10-25T10:00:01+00:00')
        return data,plan,dict(capture=[capture],capture_revision=history,operation_outcome=outcomes)

    def test_oracle_independently_discovers_five_outcomes_and_four_revisions(self):
        data,plan,rows=self.oracle_rows()
        proof=q.verify_rows(data,plan,['create','answers','date','noop','retry'],rows)
        self.assertEqual(proof['current_revision'],4)
        self.assertEqual(len(proof['discovered_outcomes']),5)

    def test_oracle_rejects_scope_attribution_history_and_receipt_corruption(self):
        data,plan,rows=self.oracle_rows()
        names=['create','answers','date','noop','retry']
        for table,index,key,value in (
            ('capture',0,'owner_actor_id','wrong'),('capture',0,'child_eligibility_ref','wrong'),
            ('capture',0,'creator_membership_id',2),('capture',0,'updated_by',data.actor),
            ('capture',0,'questionnaire_version_id','wrong'),('capture',0,'revision',3),
            ('capture_revision',1,'executor_actor_id',data.actor),('capture_revision',2,'operation_id','wrong'),
            ('capture_revision',3,'outcome_id','orphan'),('capture_revision',1,'observation_date','2020-01-01'),
            ('operation_outcome',2,'result_revision',2),('operation_outcome',3,'executor_account_id','wrong'),
            ('operation_outcome',0,'command_version',2),('operation_outcome',4,'result',{})):
            with self.subTest(table=table,key=key):
                corrupted=copy.deepcopy(rows);corrupted[table][index][key]=value
                with self.assertRaises(AssertionError):q.verify_rows(data,plan,names,corrupted)
        corrupted=copy.deepcopy(rows);corrupted['capture_revision'].append(dict(rows['capture_revision'][2],outcome_id='internal-noop'))
        with self.assertRaises(AssertionError):q.verify_rows(data,plan,names,corrupted)

    def test_noop_requires_exact_capture_timestamps_and_no_history(self):
        data,plan,rows=self.oracle_rows(('create','answers','date'))
        after=copy.deepcopy(rows);after['operation_outcome'].append({'id':'new-noop'})
        q.verify_transition(rows,after,noop=True)
        for key,value in [('updated_at','2026-10-25T10:00:02+00:00'),('updated_by','changed')]:
            damaged=copy.deepcopy(after);damaged['capture'][0][key]=value
            with self.assertRaises(AssertionError):q.verify_transition(rows,damaged,noop=True)
        damaged=copy.deepcopy(after);damaged['capture_revision'].append({'unexpected':'history'})
        with self.assertRaises(AssertionError):q.verify_transition(rows,damaged,noop=True)

    def test_failed_attempt_requires_complete_rollback(self):
        data,plan,rows=self.oracle_rows(('create','answers','date','noop'))
        q.verify_transition(rows,copy.deepcopy(rows),unchanged=True)
        for table in rows:
            damaged=copy.deepcopy(rows);damaged[table].append({'orphan':'row'})
            with self.assertRaises(AssertionError):q.verify_transition(rows,damaged,unchanged=True)

    def test_prior_evidence_and_original_capture_facts_are_preserved(self):
        data,plan,rows=self.oracle_rows(('create','answers','date'))
        after=copy.deepcopy(rows)
        after['capture'][0].update(revision=4,updated_at='2026-10-25T10:00:02+00:00')
        q.verify_transition(rows,after)
        for field in ('created_at','created_by','captured_at','child_id'):
            damaged=copy.deepcopy(after);damaged['capture'][0][field]='changed'
            with self.assertRaises(AssertionError):q.verify_transition(rows,damaged)
        for table in ('operation_outcome','capture_revision'):
            damaged=copy.deepcopy(after);damaged[table][0]['new']='changed'
            with self.assertRaises(AssertionError):q.verify_transition(rows,damaged)

    def test_exact_new_row_deltas_cover_all_eight_tables(self):
        before={table:10 for table in q.DELTAS}
        after={table:10+delta for table,delta in q.DELTAS.items()}
        q.verify_deltas(before,after)
        for table in q.DELTAS:
            damaged=dict(after);damaged[table]+=1
            with self.assertRaises(AssertionError):q.verify_deltas(before,damaged)

    def test_safe_cli_failure_retains_plan_and_never_exposes_exception_payload(self):
        def fail(attempt):
            attempt.update(plan={'original':'command'},cases=['created']);q.STAGE='native_fault'
            raise ValueError('credential-canary')
        with patch.object(q,'qualify',side_effect=fail),patch.object(q.fixture,'receipt',return_value=Path('/tmp/failed.json')) as receipt,redirect_stdout(io.StringIO()) as output:
            self.assertEqual(q.main(['--qualify-retained']),1)
        result=receipt.call_args.args[1]
        self.assertFalse(result['qualified']);self.assertEqual(result['failed_stage'],'native_fault')
        self.assertEqual(result['plan'],{'original':'command'})
        self.assertNotIn('credential-canary',str(result)+output.getvalue())

    def test_source_bindings_include_all_executed_qualifiers_and_custody(self):
        paths=set(q.source_paths())
        self.assertTrue({'platform/deployment/dev.py','platform/deployment/native_cli.py',
            'apps/kdg-capture/write-candidate/capture_edit.py',
            'apps/kdg-capture/migrations/tests/qualify_own_edit.py',
            'apps/kdg-capture/migrations/tests/qualify_edit_recovery_http.py'}<=paths)

    def test_explicit_retained_cli_required(self):
        with patch.object(q,'qualify') as run,self.assertRaises(SystemExit):q.main([])
        run.assert_not_called()


    def harness(self):
        from contextlib import ExitStack
        stack=ExitStack();self.addCleanup(stack.close)
        for name,result in [('retained',({'urls':{'runtime':'synthetic'}},{},object())),
            ('migration_qualified','applied'),('identities',{}),('sentinel',None),('revision',q.fixture.STORAGE)]:
            stack.enter_context(patch.object(q.fixture,name,return_value=result))
        stack.enter_context(patch.object(q,'snapshot',return_value={}))
        stack.enter_context(patch.object(q,'table_counts',side_effect=[{t:0 for t in q.DELTAS},q.DELTAS]))
        stack.enter_context(patch.object(q.commit,'seed'))
        stack.enter_context(patch.object(q.fixture,'engine'))
        stack.enter_context(patch.object(q.commit,'execute',side_effect=lambda engine,data,raw:
            dict(operation_id=json.loads(raw)['operation_id'],command_type='capture.create',command_version=1,
                status='committed',result=dict(capture_id=json.loads(raw)['capture_id'],revision='1'))))
        stack.enter_context(patch.object(q,'read_storage',return_value=({},dict(verified=True))))
        stack.enter_context(patch.object(q,'verify_transition'))
        def execute(value,data,plan,name,*,fault=False):
            error=dict(stale='kdg_capture.capture_revision_conflict',invalid='validation_failed',
                foreign_account='capture_unavailable',foreign_org='capture_unavailable').get(name)
            if fault:return dict(error='internal_error',sql=dict(capture_updates=1,history_inserts=0),outcome_present_before_fault=True)
            if name=='retry':
                execute.retries+=1
                if execute.retries>1:return dict(error='operation_verification_unavailable')
            if error:return dict(error=error,current_revision='3')
            return dict(receipt=q.expected_receipt(plan,name),sql=dict(capture_updates=int(name!='noop'),history_inserts=int(name!='noop')))
        execute.retries=0
        stack.enter_context(patch.object(q,'execute_edit',side_effect=execute))
        return stack.enter_context(patch.object(q.fixture,'receipt',return_value=Path('/tmp/attempt.json')))

    def test_journal_precedes_seed_and_every_write_has_independent_read(self):
        receipt=self.harness();order=[]
        def seed(*a,**k):
            self.assertEqual(receipt.call_args.args[0],'own-edit-start')
            plan=receipt.call_args.args[1]['plan']
            self.assertEqual(len(plan),9)
            order.append('seed')
        with patch.object(q.commit,'seed',side_effect=seed),patch.object(q,'read_storage',side_effect=lambda *a:
            (order.append('read') or {},dict(verified=True))):
            result=q.qualify({})
        self.assertTrue(result['qualified']);self.assertEqual(order,['seed']+['read']*11)
        self.assertEqual([c.args[0] for c in receipt.call_args_list],['own-edit-start','own-edit'])

    def test_any_write_or_oracle_failure_prevents_qualified_success(self):
        for target in ('execute_edit','read_storage','verify_transition','verify_deltas','verify_preservation'):
            with self.subTest(target=target):
                receipt=self.harness()
                with patch.object(q,target,side_effect=ValueError('private')),self.assertRaises(ValueError):q.qualify({})
                self.assertEqual(receipt.call_count,1)

    def test_source_drift_prevents_writes_or_success(self):
        receipt=self.harness()
        with patch.object(q,'source_hashes',return_value={}),patch.object(q.commit,'seed') as seed,self.assertRaises(AssertionError):q.qualify({})
        seed.assert_not_called();receipt.assert_not_called()
        with patch.object(q,'source_hashes',side_effect=[q.INITIAL_SOURCES,{}]),self.assertRaises(AssertionError):q.qualify({})
        self.assertEqual(receipt.call_count,1)

    def test_success_receipt_io_failure_returns_safe_failed_attempt(self):
        self.harness()
        with patch.object(q.fixture,'receipt',side_effect=[Path('/tmp/start.json'),OSError('private-io'),Path('/tmp/failure.json')]) as receipt,redirect_stdout(io.StringIO()) as output:
            self.assertEqual(q.main(['--qualify-retained']),1)
        failure=receipt.call_args.args[1]
        self.assertFalse(failure['qualified']);self.assertEqual(failure['failed_stage'],'success_receipt')
        self.assertEqual(len(failure['cases']),11)
        self.assertNotIn('private-io',str(failure)+output.getvalue())


    def test_safe_write_error_uses_actual_identifier_and_releases_engine(self):
        from unittest.mock import MagicMock
        from contextlib import nullcontext
        data,plan=q.new_plan();engine=MagicMock();conn=engine.connect.return_value.__enter__.return_value
        conn.execute.return_value.one.return_value=('kdg_capture_runtime','kdg_capture_runtime')
        with patch.object(q.fixture,'engine',return_value=engine),patch.object(q.write,'transaction',return_value=nullcontext()),patch.object(q.edit,'edit_in_transaction',side_effect=q.edit.RevisionConflict(3)):
            result=q.execute_edit({'urls':{'runtime':'synthetic'}},data,plan,'stale')
        self.assertEqual(result['error'],'kdg_capture.capture_revision_conflict');self.assertEqual(result['current_revision'],'3')
        engine.dispose.assert_called_once()

    def test_native_fault_cannot_pass_on_synthetic_internal_error(self):
        from unittest.mock import MagicMock
        from contextlib import nullcontext
        data,plan=q.new_plan();engine=MagicMock();conn=engine.connect.return_value.__enter__.return_value
        conn.execute.return_value.one.return_value=('kdg_capture_runtime','kdg_capture_runtime')
        with patch.object(q.fixture,'engine',return_value=engine),patch.object(q.write,'transaction',return_value=nullcontext()),patch.object(q.edit,'edit_in_transaction',side_effect=q.write.WriteError('internal_error')):
            with self.assertRaisesRegex(AssertionError,'native_constraint_failure_required'):
                q.execute_edit({'urls':{'runtime':'synthetic'}},data,plan,'retry',fault=True)
        engine.dispose.assert_called_once()


    def test_bootstrap_read_failure_returns_safe_best_effort_receipt(self):
        import runpy
        original=Path.read_bytes
        def read(path):
            if path==q.ROOT/'platform/deployment/dev.py':raise OSError('credential-canary')
            return original(path)
        with patch.object(Path,'read_bytes',read),patch.object(q.fixture,'receipt',return_value=Path('/tmp/bootstrap.json')) as receipt,patch.object(sys,'argv',[q.__file__,'--qualify-retained']),redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as stopped:runpy.run_path(q.__file__,run_name='__main__')
        self.assertEqual(stopped.exception.code,1)
        result=json.loads(output.getvalue());self.assertEqual(result['failed_stage'],'source_bootstrap')
        self.assertFalse(receipt.call_args.args[1]['qualified'])
        self.assertNotIn('credential-canary',str(receipt.call_args)+output.getvalue())

    def test_bootstrap_import_failure_returns_safe_best_effort_receipt(self):
        import builtins
        import runpy
        original=builtins.__import__
        def importing(name,*args,**kwargs):
            if name=='qualify_capture_commit':raise ImportError('import-canary')
            return original(name,*args,**kwargs)
        with patch.object(builtins,'__import__',importing),patch.object(q.fixture,'receipt',return_value=Path('/tmp/bootstrap.json')) as receipt,patch.object(sys,'argv',[q.__file__,'--qualify-retained']),redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as stopped:runpy.run_path(q.__file__,run_name='__main__')
        self.assertEqual(stopped.exception.code,1)
        self.assertEqual(json.loads(output.getvalue())['failed_stage'],'imports')
        self.assertNotIn('import-canary',str(receipt.call_args)+output.getvalue())


    def test_missing_uncommitted_outcome_refuses_before_native_fault(self):
        from unittest.mock import MagicMock
        from contextlib import nullcontext
        data,plan=q.new_plan();engine=MagicMock();conn=engine.connect.return_value.__enter__.return_value
        conn.execute.return_value.one.return_value=('kdg_capture_runtime','kdg_capture_runtime')
        def body(connection,budget,context,capture,command,*,permission):
            return q.write.execute(connection,budget,q.edit.HISTORY_INSERT,{})
        with patch.object(q.fixture,'engine',return_value=engine),patch.object(q.write,'transaction',return_value=nullcontext()),patch.object(q.edit,'edit_in_transaction',side_effect=body),patch.object(q.outcomes,'lookup_private',return_value=None) as lookup,patch.object(q.write,'execute') as native:
            with self.assertRaisesRegex(AssertionError,'uncommitted_outcome_required_before_fault'):
                q.execute_edit({'urls':{'runtime':'synthetic'}},data,plan,'retry',fault=True)
        native.assert_not_called()
        self.assertIs(lookup.call_args.args[0],conn)
        self.assertEqual(lookup.call_args.args[2].operation_id,plan['retry']['operation_id'])
        engine.dispose.assert_called_once()

    def test_successful_execution_retained_when_create_or_edit_read_fails(self):
        for fail_after in ('create','answers'):
            with self.subTest(fail_after=fail_after):
                receipt=self.harness()
                def read(value,data,plan,names):
                    if names[-1]==fail_after:raise ValueError('private-read-canary')
                    return {},dict(verified=True)
                with patch.object(q,'read_storage',side_effect=read),redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(q.main(['--qualify-retained']),1)
                failure=receipt.call_args.args[1]
                self.assertFalse(failure['qualified'])
                self.assertEqual(failure['execution_results']['create']['receipt'],q.expected_receipt(failure['plan'],'create'))
                if fail_after=='answers':
                    result=failure['execution_results']['answers']
                    self.assertEqual(result['receipt'],q.expected_receipt(failure['plan'],'answers'))
                    self.assertEqual(result['sql'],dict(capture_updates=1,history_inserts=1))
                    self.assertNotIn('answers',failure['checks'])
                self.assertNotIn('private-read-canary',str(failure)+output.getvalue())

if __name__=='__main__':unittest.main()
