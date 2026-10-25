"""Stored-edit qualification cannot certify partial or drifting evidence."""
from contextlib import ExitStack, redirect_stdout, nullcontext
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations/tests'))
import qualify_edit_recovery_http as q

class NativeEditEvidence(unittest.TestCase):
    def test_plan_has_fresh_distinct_journaled_identities(self):
        data, plan = q.new_plan()
        ids = [data.org,data.account,data.actor,data.questionnaire,data.version,data.child,data.assignment_id,data.ref,*data.questions]
        ids += [plan['create']['operation_id'],plan['create']['capture_id'],plan['edit2']['operation_id'],plan['edit3']['operation_id'],plan['edit2']['outcome_id'],plan['edit3']['outcome_id']]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(plan['edit2']['revision'],2)
        self.assertEqual(plan['edit3']['revision'],3)
        self.assertEqual(plan['edit2']['capture_id'],plan['create']['capture_id'])
    def test_preservation_rejects_any_prior_row_change(self):
        before={'capture':{'count':10,'sha256':'original'}}
        with self.assertRaises(AssertionError):q.verify_preservation(before,{'capture':{'count':10,'sha256':'changed'}})
    def test_delta_checks_all_parent_and_business_tables(self):
        before={table:0 for table in q.DELTAS}
        q.verify_deltas(before,q.DELTAS)
        for table in q.DELTAS:
            with self.subTest(table=table),self.assertRaises(AssertionError):
                q.verify_deltas(before,dict(q.DELTAS,**{table:q.DELTAS[table]+1}))
    def test_later_edit_preserves_exact_original_evidence(self):
        before=dict(immutable_revisions={'1':'one','2':'two'},immutable_outcomes={'operation':'stored'},capture_created_at='2026-10-25T10:00:00+00:00',capture_created_by='actor',capture_updated_at='2026-10-25T10:00:00+00:00')
        after=dict(before,immutable_revisions={'1':'one','2':'two','3':'three'},capture_updated_at='2026-10-25T10:00:01+00:00')
        q.verify_original_evidence(before,after)
        for field,value in [('immutable_revisions',{'1':'one','2':'changed'}),('immutable_outcomes',{}),('capture_created_at','changed'),('capture_created_by','other'),('capture_updated_at',before['capture_updated_at'])]:
            with self.subTest(field=field),self.assertRaises(AssertionError):q.verify_original_evidence(before,dict(after,**{field:value}))
    def test_fixture_edits_reject_unplanned_or_foreign_targets_before_checkout(self):
        data,plan=q.new_plan()
        with patch.object(q.fixture,'engine') as engine:
            for edit in (dict(plan['edit2']),dict(plan['edit2'],capture_id='foreign')):
                with self.assertRaises(AssertionError):q.fixture_edit(engine,data,plan,edit)
            plan['edit2']['capture_id']='foreign'
            with self.assertRaisesRegex(AssertionError,'^fixture_target_changed$'):
                q.fixture_edit(engine,data,plan,plan['edit2'])
            engine.connect.assert_not_called()
    def test_bootstrap_source_read_failure_is_safe_and_receipted(self):
        import runpy
        original=Path.read_bytes
        def read(path):
            if path==q.ROOT/'platform/deployment/dev.py':raise OSError('credential-canary')
            return original(path)
        with patch.object(Path,'read_bytes',read),patch.object(q.fixture,'receipt',return_value=Path('/tmp/bootstrap.json')) as receipt,patch.object(sys,'argv',[q.__file__,'--qualify-retained']),redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as stopped:runpy.run_path(q.__file__,run_name='__main__')
        self.assertEqual(stopped.exception.code,1)
        body=json.loads(output.getvalue())
        self.assertEqual((body['failed_stage'],body['error_type']),('source_bootstrap','OSError'))
        self.assertNotIn('credential-canary',output.getvalue()+str(receipt.call_args))
        self.assertFalse(receipt.call_args.args[1]['qualified'])
    def test_bootstrap_import_failure_is_safe_and_receipted(self):
        import builtins
        import runpy
        original=builtins.__import__
        def importing(name,*args,**kwargs):
            if name=='qualify_capture_commit':raise ImportError('import-credential-canary')
            return original(name,*args,**kwargs)
        with patch.object(builtins,'__import__',importing),patch.object(q.fixture,'receipt',return_value=Path('/tmp/bootstrap.json')) as receipt,patch.object(sys,'argv',[q.__file__,'--qualify-retained']),redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as stopped:runpy.run_path(q.__file__,run_name='__main__')
        self.assertEqual(stopped.exception.code,1)
        body=json.loads(output.getvalue())
        self.assertEqual((body['failed_stage'],body['error_type']),('imports','ImportError'))
        self.assertNotIn('import-credential-canary',output.getvalue()+str(receipt.call_args))
    def test_source_binding_includes_executed_custody_dependencies(self):
        self.assertTrue({'platform/deployment/dev.py','platform/deployment/native_cli.py'}<=set(q.source_paths()))
    def oracle_rows(self):
        data,plan=q.new_plan();common=dict(org_id=data.org,owner_account_id=data.account,owner_actor_id=data.actor,
            child_id=data.child,questionnaire_id=data.questionnaire,questionnaire_version_id=data.version,captured_at=plan['create']['captured_at'])
        capture=dict(common,id=plan['create']['capture_id'],revision=2,created_by=data.actor,updated_by=data.actor,
            child_eligibility_ref=data.ref,creator_membership_id=int(data.membership),
            created_at='2026-10-25T10:00:00+00:00',updated_at='2026-10-25T10:00:01+00:00',
            answers=plan['edit2']['answers'],observation_date=plan['edit2']['observation_date'])
        history=[];outcomes=[]
        for n,name in enumerate(('create','edit2'),1):
            command=plan[name];outcome_id=command.get('outcome_id','internal-create-id')
            evidence=dict(org_id=data.org,executor_account_id=data.account,executor_actor_id=data.actor,initiator_actor_id=data.actor,
                operation_id=command['operation_id'],command_type=q.expected_receipt(plan,name)['command_type'])
            history.append(dict(common,**{k:v for k,v in evidence.items() if k!='org_id'},capture_id=capture['id'],revision=n,
                outcome_id=outcome_id,answers=command['answers'],observation_date=command['observation_date']))
            outcomes.append(dict(evidence,id=outcome_id,capture_id=capture['id'],result_revision=n,
                result=q.expected_receipt(plan,name)['result'],command_version=1,result_version=1))
        return data,plan,capture,history,outcomes
    def read_rows(self,data,plan,capture,history,outcomes):
        connection=MagicMock()
        identity=MagicMock();identity.one.return_value=('kdg_capture_runtime','kdg_capture_runtime','on')
        c=MagicMock();c.scalar_one.return_value=capture
        h=MagicMock();h.scalars.return_value.all.return_value=history
        o=MagicMock();o.scalars.return_value.all.return_value=outcomes
        connection.execute.side_effect=[identity,c,h,o]
        engine=MagicMock();engine.execution_options.return_value=engine
        engine.connect.return_value.__enter__.return_value=connection
        with patch.object(q.fixture,'engine',return_value=engine),patch.object(q.write,'transaction',return_value=nullcontext()):
            return q.read_storage({'urls':{'runtime':'synthetic'}},data,plan,2)
    def test_controlled_rows_exercise_independent_oracle(self):
        import copy
        data,plan,capture,history,outcomes=self.oracle_rows()
        self.assertTrue(self.read_rows(data,plan,capture,history,outcomes)['verified'])
        mutations=[('capture','child_eligibility_ref','wrong'),('capture','creator_membership_id',2),
            ('capture','owner_actor_id','wrong'),('capture','revision',3),('capture','created_by','wrong'),
            ('capture','updated_by','wrong'),('capture','updated_at','2026-10-25T09:00:00+00:00'),
            ('history','questionnaire_version_id','wrong'),('history','revision',3),('history','executor_actor_id','wrong'),
            ('history','outcome_id','wrong'),('outcome','id','wrong'),('outcome','result_revision',3),
            ('outcome','executor_account_id','wrong')]
        for target,key,value in mutations:
            with self.subTest(target=target,key=key):
                c,h,o=copy.deepcopy((capture,history,outcomes))
                row=c if target=='capture' else h[1] if target=='history' else o[1]
                row[key]=value
                with self.assertRaises(AssertionError):self.read_rows(data,plan,c,h,o)
        # A mutually linked but unjournaled outcome must also fail.
        h,o=copy.deepcopy((history,outcomes));h[1]['outcome_id']=o[1]['id']='other-linked-id'
        with self.assertRaisesRegex(AssertionError,'planned_outcome_id_disagrees'):
            self.read_rows(data,plan,capture,h,o)
    def test_http_recovers_edit3_only_after_its_commit_checkpoint(self):
        import asyncio
        data,plan=q.new_plan()
        for revision in (2,3):
            with self.subTest(revision=revision):
                expected=[q.expected_receipt(plan,'edit2')]
                if revision==3:expected.append(q.expected_receipt(plan,'edit3'))
                unresolved=dict(operation_id=plan['edit2']['operation_id'],command_type='capture.edit',status='unresolved')
                expected += [q.expected_receipt(plan,'create'),dict(unresolved,command_type='capture.create'),
                    unresolved,q.expected_receipt(plan,'edit2'),q.prior.envelope('access_denied'),unresolved]
                replies=[q.httpx.Response(403 if body==q.prior.envelope('access_denied') else 200,json=body,
                    headers={'Cache-Control':'private, no-store'}) for body in expected]
                app=MagicMock();app.state.recovery_engine.pool.checkedout.return_value=0
                client=MagicMock();client.get=AsyncMock(side_effect=replies)
                owner=MagicMock();owner.__aenter__.return_value=client
                with patch.object(q.boundary,'create_candidate',return_value=app),patch.object(q.event,'listen'),patch.object(q.httpx,'AsyncClient',return_value=owner):
                    result=asyncio.run(q.exercise({'urls':{'runtime':'synthetic'}},data,plan,revision))
                edit3_calls=[call for call in client.get.call_args_list if plan['edit3']['operation_id'] in call.args[0]]
                self.assertEqual(len(edit3_calls),int(revision==3))
                self.assertEqual('latest_edit3_receipt_and_release' in result['cases'],revision==3)
    def harness(self,fail=None):
        stack=ExitStack();self.addCleanup(stack.close)
        for name,result in [('retained',({'urls':{'runtime':'synthetic'}}, {}, object())),('migration_qualified','applied'),('identities',{}),('sentinel',None),('revision',q.fixture.STORAGE)]:
            stack.enter_context(patch.object(q.fixture,name,return_value=result))
        stack.enter_context(patch.object(q,'snapshot',return_value={}))
        stack.enter_context(patch.object(q,'table_counts',side_effect=[{t:0 for t in q.DELTAS},q.DELTAS]))
        stack.enter_context(patch.object(q.commit,'seed'))
        stack.enter_context(patch.object(q.fixture,'engine'))
        stack.enter_context(patch.object(q,'fixture_edit'))
        stack.enter_context(patch.object(q,'write_dataset',side_effect=RuntimeError('secret-canary') if fail=='write' else None))
        stack.enter_context(patch.object(q,'read_storage',side_effect=[dict(verified=True,immutable_revisions={},immutable_outcomes={},capture_created_at='2026-10-25T10:00:00+00:00',capture_created_by='actor',capture_updated_at=f'2026-10-25T10:00:0{n}+00:00') for n in range(3)]))
        stack.enter_context(patch.object(q,'exercise',new=AsyncMock(return_value={'cases':['native']})))
        return stack.enter_context(patch.object(q.fixture,'receipt',return_value=Path('/tmp/attempt.json')))
    def test_journal_precedes_seed(self):
        receipt=self.harness()
        with patch.object(q.commit,'seed',side_effect=lambda *a,**k:self.assertEqual(receipt.call_args.args[0],'edit-recovery-start')):
            q.qualify({})
        self.assertEqual([c.args[0] for c in receipt.call_args_list],['edit-recovery-start','edit-recovery-http'])
    def test_revision1_baseline_precedes_both_edits(self):
        self.harness();observed=[]
        def read(value,data,plan,revision):
            observed.append(('read',revision))
            return dict(immutable_revisions={},immutable_outcomes={},capture_created_at='2026-10-25T10:00:00+00:00',
                capture_created_by=data.actor,capture_updated_at=f'2026-10-25T10:00:0{revision}+00:00')
        with patch.object(q,'read_storage',side_effect=read),patch.object(q,'fixture_edit',side_effect=lambda engine,data,plan,edit:observed.append(('edit',edit['revision']))):
            q.qualify({})
        self.assertEqual(observed,[('read',1),('edit',2),('read',2),('edit',3),('read',3)])
    def test_write_failure_has_no_success_receipt(self):
        receipt=self.harness('write');attempt={}
        with self.assertRaises(RuntimeError):q.qualify(attempt)
        self.assertIn('plan',attempt);self.assertIn('start_receipt',attempt)
        self.assertEqual(receipt.call_count,1)
    def test_source_drift_has_no_success_receipt(self):
        receipt=self.harness()
        with patch.object(q,'source_hashes',side_effect=[q.INITIAL_SOURCES,{}]),self.assertRaises(AssertionError):q.qualify({})
        self.assertEqual(receipt.call_count,1)
    def test_read_or_preservation_failure_has_no_success_receipt(self):
        for name in ('read_storage','verify_preservation','verify_deltas'):
            with self.subTest(name=name):
                receipt=self.harness()
                with patch.object(q,name,side_effect=ValueError('private')),self.assertRaises(ValueError):q.qualify({})
                self.assertEqual(receipt.call_count,1)
    def test_cli_failure_retains_intent_and_safe_stage(self):
        def fail(attempt):
            attempt.update(plan={'operation_id':'intended'},cases=['completed']);q.STAGE='fixture_edit2'
            raise ValueError('private-credential-canary')
        with patch.object(q,'qualify',side_effect=fail),patch.object(q.fixture,'receipt',return_value=Path('/tmp/failure.json')) as receipt,redirect_stdout(io.StringIO()) as output:
            self.assertEqual(q.main(['--qualify-retained']),1)
        result=receipt.call_args.args[1]
        self.assertFalse(result['succeeded']);self.assertFalse(result['qualified'])
        self.assertEqual(result['plan'],{'operation_id':'intended'})
        self.assertEqual(result['cases'],['completed'])
        self.assertEqual(result['failed_stage'],'fixture_edit2')
        self.assertNotIn('private-credential-canary',output.getvalue()+str(result))
    def test_receipt_io_failure_never_prints_exception_payload(self):
        with patch.object(q,'qualify',side_effect=ValueError('private-native')),patch.object(q.fixture,'receipt',side_effect=OSError('credential-canary')),redirect_stdout(io.StringIO()) as output:
            self.assertEqual(q.main(['--qualify-retained']),1)
        self.assertNotIn('credential-canary',output.getvalue())
        self.assertFalse(json.loads(output.getvalue())['qualified'])
    def test_explicit_cli_required(self):
        with patch.object(q,'qualify') as run,self.assertRaises(SystemExit):q.main([])
        run.assert_not_called()

if __name__=='__main__':unittest.main()
