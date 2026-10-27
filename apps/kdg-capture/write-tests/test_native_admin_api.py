"""Database-free acceptance of native admin qualification and cross-account oracle."""
import copy
import io
import json
from contextlib import redirect_stdout, ExitStack
from pathlib import Path
import sys
import unittest
from unittest.mock import patch, MagicMock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations/tests'))
import qualify_admin_api as q

COMMITTED=['create_a','create_b','admin_a','owner_a','admin_a2','noop','owner_b','admin_b','owner_b2','retry']

class NativeAdminAPI(unittest.TestCase):
    def oracle_rows(self,names=None):
        names=names or COMMITTED
        data,plan=q.new_plan();history=[];outcomes=[];captures={}
        for name in names:
            entry=plan[name];command=entry['command'];account,actor=q.executor(data,entry)
            common=dict(org_id=data.org,owner_account_id=data.account,owner_actor_id=data.actor,
                child_id=data.child,questionnaire_id=data.questionnaire,questionnaire_version_id=data.version,
                captured_at=plan['create_a' if entry['capture_id']==plan['create_a']['capture_id'] else 'create_b']['command']['captured_at'])
            evidence=dict(org_id=data.org,executor_account_id=account,executor_actor_id=actor,initiator_actor_id=actor,
                operation_id=command['operation_id'],command_type=q.expected_receipt(plan,name)['command_type'])
            outcome=dict(evidence,id='internal-'+name,capture_id=entry['capture_id'],result=q.expected_receipt(plan,name)['result'],
                result_revision=entry['revision'],command_version=1,result_version=1)
            outcomes.append(outcome)
            if entry['changed']:
                history.append(dict(common,**{key:value for key,value in evidence.items() if key!='org_id'},
                    capture_id=entry['capture_id'],revision=entry['revision'],outcome_id=outcome['id'],
                    answers=command['answers'],observation_date=command['observation_date']))
                captures[entry['capture_id']]=dict(common,id=entry['capture_id'],revision=entry['revision'],answers=command['answers'],
                    observation_date=command['observation_date'],created_by=data.actor,updated_by=actor,
                    child_eligibility_ref=data.ref,creator_membership_id=int(data.membership),
                    created_at='2026-10-25T10:00:00+00:00',updated_at='2026-10-25T10:00:0'+str(entry['revision'])+'+00:00')
        return data,plan,dict(capture=list(captures.values()),capture_revision=history,operation_outcome=outcomes)

    def test_foreign_owner_admin_outcomes_are_valid_and_executor_private(self):
        data,plan,rows=self.oracle_rows()
        proof=q.verify_rows(data,plan,COMMITTED,rows)
        self.assertTrue(proof['verified']);self.assertEqual(sorted(proof['current_revisions'].values()),[4,5])
        self.assertEqual(len(proof['discovered_outcomes']),10)
        self.assertNotEqual(data.account,data.admin_account);self.assertNotEqual(data.actor,data.admin_actor)

    def test_oracle_rejects_owner_admin_confusion_or_linkage_corruption(self):
        data,plan,rows=self.oracle_rows()
        for table,index,key,value in (
            ('capture',0,'owner_account_id',data.admin_account),('capture',0,'created_by',data.admin_actor),
            ('capture',0,'updated_by',data.actor),('capture',0,'child_eligibility_ref','wrong'),
            ('capture',0,'creator_membership_id',2),('capture',0,'questionnaire_version_id','wrong'),
            ('capture_revision',2,'executor_account_id',data.account),('capture_revision',2,'executor_actor_id',data.actor),
            ('capture_revision',2,'owner_actor_id',data.admin_actor),('capture_revision',2,'outcome_id','orphan'),
            ('operation_outcome',2,'executor_account_id',data.account),('operation_outcome',2,'initiator_actor_id',data.actor),
            ('operation_outcome',2,'result_revision',1),('operation_outcome',2,'capture_id',plan['create_b']['capture_id']),
            ('operation_outcome',2,'command_version',2),('operation_outcome',2,'result',{})):
            with self.subTest(table=table,key=key):
                damaged=copy.deepcopy(rows);damaged[table][index][key]=value
                with self.assertRaises(AssertionError):q.verify_rows(data,plan,COMMITTED,damaged)
        damaged=copy.deepcopy(rows);damaged['capture_revision'].append(dict(rows['capture_revision'][2],outcome_id='internal-noop'))
        with self.assertRaises(AssertionError):q.verify_rows(data,plan,COMMITTED,damaged)

    def test_noop_keeps_both_complete_captures_and_all_history(self):
        _,_,before=self.oracle_rows(COMMITTED[:5]);after=copy.deepcopy(before)
        after['operation_outcome'].append(dict(after['operation_outcome'][-1],id='noop'))
        q.verify_transition(before,after,noop=True)
        for table in ('capture','capture_revision'):
            damaged=copy.deepcopy(after);damaged[table][0]['updated_at']='changed'
            with self.assertRaises(AssertionError):q.verify_transition(before,damaged,noop=True)

    def test_two_target_transition_keeps_unedited_target_and_old_evidence(self):
        _,_,before=self.oracle_rows(['create_a','create_b'])
        after=copy.deepcopy(before);first=after['capture'][0]
        first.update(revision=2,updated_at='2026-10-25T10:00:02+00:00',updated_by='admin')
        after['capture_revision'].append(dict(after['capture_revision'][0],revision=2))
        q.verify_transition(before,after)
        after['capture'][1]['created_by']='changed'
        with self.assertRaises(AssertionError):q.verify_transition(before,after)

    def test_refusal_requires_exact_rollback_of_all_tables(self):
        _,_,rows=self.oracle_rows()
        q.verify_transition(rows,copy.deepcopy(rows),unchanged=True)
        for table in rows:
            damaged=copy.deepcopy(rows);damaged[table].append({'orphan':'row'})
            with self.assertRaises(AssertionError):q.verify_transition(rows,damaged,unchanged=True)

    def test_plan_has_two_orderings_and_journaled_retry_without_outcome_ids(self):
        data,plan=q.new_plan()
        self.assertEqual(plan['admin_a']['command']['expected_revision'],'1')
        self.assertEqual(plan['owner_b']['command']['expected_revision'],'1')
        self.assertEqual(plan['owner_a']['command']['expected_revision'],'2')
        self.assertEqual(plan['admin_b']['command']['expected_revision'],'2')
        self.assertEqual(plan['noop']['revision'],4);self.assertFalse(plan['noop']['changed'])
        self.assertEqual(plan['retry']['revision'],5)
        operations=[entry['command']['operation_id'] for entry in plan.values()]
        self.assertEqual(len(operations),len(set(operations)))
        self.assertTrue(all('outcome_id' not in entry['command'] for entry in plan.values()))

    def test_receipts_preserve_original_target_and_revision(self):
        data,plan=q.new_plan()
        receipt=q.expected_receipt(plan,'admin_a')
        self.assertEqual(receipt['result'],dict(capture_id=plan['create_a']['capture_id'],revision='2'))
        self.assertNotEqual(receipt['result']['capture_id'],plan['create_b']['capture_id'])

    def test_responses_require_released_leases_exact_body_status_and_private_cache(self):
        import httpx
        engine=MagicMock();engine.pool.checkedout.return_value=0
        response=httpx.Response(200,json={'receipt':'ok'},headers={'cache-control':'private, no-store'})
        q.verify_response(response,200,{'receipt':'ok'},[engine])
        for status,body,cache,leases in ((201,{'receipt':'ok'},'private, no-store',0),
            (200,{'receipt':'wrong'},'private, no-store',0),(200,{'receipt':'ok'},'public',0),
            (200,{'receipt':'ok'},'private, no-store',1)):
            engine.pool.checkedout.return_value=leases
            with self.assertRaises(AssertionError):q.verify_response(httpx.Response(status,json=body,headers={'cache-control':cache}),200,{'receipt':'ok'},[engine])

    def test_observations_retain_safe_receipt_fields_without_payload_diagnostics(self):
        import httpx
        _,plan=q.new_plan();body=q.expected_receipt(plan,'admin_a')
        body['private']='credential-canary'
        body['answers']={'private':'payload-canary'}
        result=q.observe_response(httpx.Response(200,json=body),[])
        self.assertEqual(result['observed']['result'],body['result'])
        self.assertNotIn('canary',str(result))
        invalid=q.observe_response(httpx.Response(500,text='credential-canary'),[])
        self.assertEqual(invalid['status'],500);self.assertNotIn('canary',str(invalid))

    def storage_harness(self,foreign=False):
        from contextlib import contextmanager
        data,plan,rows=self.oracle_rows();engines=[];contexts=[]
        owner=[row for row in rows['operation_outcome'] if row['executor_account_id']==data.account]
        admin=[row for row in rows['operation_outcome'] if row['executor_account_id']==data.admin_account]
        groups=[{'capture':rows['capture'],'capture_revision':rows['capture_revision']},
            {'operation_outcome':owner+admin if foreign else owner},{'operation_outcome':admin}]
        for group in groups:
            engine=MagicMock();engine.execution_options.return_value=engine
            conn=engine.connect.return_value.__enter__.return_value
            def execute(statement,group=group):
                result=MagicMock();sql=str(statement)
                result.one.return_value=('kdg_capture_runtime','kdg_capture_runtime','on')
                result.scalars.return_value.all.return_value=next((values for table,values in group.items() if 'kdg_capture.'+table+' ' in sql),[])
                return result
            conn.execute.side_effect=execute;engines.append(engine)
        @contextmanager
        def transaction(conn,budget,context):
            self.assertGreaterEqual(context.observed_at,budget.started_at)
            contexts.append(context);yield
        return data,plan,rows,engines,contexts,transaction

    def test_independent_read_sessions_separate_all_read_and_both_private_executors(self):
        data,plan,rows,engines,contexts,transaction=self.storage_harness()
        with patch.object(q.fixture,'engine',side_effect=engines),patch.object(q.write,'transaction',side_effect=transaction):
            found,proof=q.read_storage({'urls':{'runtime':'synthetic'}},data,plan,COMMITTED)
        for table in rows:self.assertCountEqual(found[table],rows[table])
        self.assertTrue(proof['verified'])
        self.assertEqual([context.account_id for context in contexts],[data.admin_account,data.account,data.admin_account])
        self.assertTrue(all(context.mode=='all_read' for context in contexts))
        for engine in engines:
            engine.dispose.assert_called_once();engine.execution_options.assert_called_once_with(postgresql_readonly=True)

    def test_all_read_cannot_make_foreign_executor_outcomes_visible(self):
        data,plan,rows,engines,contexts,transaction=self.storage_harness(foreign=True)
        with patch.object(q.fixture,'engine',side_effect=engines),patch.object(q.write,'transaction',side_effect=transaction):
            with self.assertRaisesRegex(AssertionError,'private_outcome_visibility_failed'):
                q.read_storage({'urls':{'runtime':'synthetic'}},data,plan,COMMITTED)
        engines[0].dispose.assert_called_once();engines[1].dispose.assert_called_once()

    def test_expected_complete_count_deltas(self):
        before={table:10 for table in q.DELTAS};after={table:10+delta for table,delta in q.DELTAS.items()}
        q.verify_deltas(before,after)
        for table in q.DELTAS:
            damaged=dict(after);damaged[table]+=1
            with self.assertRaises(AssertionError):q.verify_deltas(before,damaged)

    def test_sources_explicitly_bind_candidates_helpers_and_exclude_prohibited_fixture(self):
        paths=q.source_paths()
        self.assertEqual(len(paths),len(set(paths)))
        self.assertFalse(any('schema_fixture' in path for path in paths))
        for name in ('admin_http','admin_edit_context_http','audit_http','admin_edit_http','edit_http'):
            self.assertIn('apps/kdg-capture/write-candidate/'+name+'.py',paths)
        self.assertIn('apps/kdg-capture/migrations/tests/qualify_admin_api.py',paths)
        self.assertEqual(q.BOOTSTRAP_ERROR,None)

    def harness(self):
        stack=ExitStack();self.addCleanup(stack.close)
        for name,result in [('retained',({'urls':{'runtime':'synthetic'}},{},object())),
            ('migration_qualified','applied'),('identities',{}),('sentinel',None),('revision',q.fixture.STORAGE)]:
            stack.enter_context(patch.object(q.fixture,name,return_value=result))
        stack.enter_context(patch.object(q.preserved,'snapshot',return_value={}))
        stack.enter_context(patch.object(q.preserved,'table_counts',side_effect=[{table:0 for table in q.DELTAS},q.DELTAS]))
        stack.enter_context(patch.object(q.commit,'seed'))
        async def exercise(value,data,plan,attempt):
            attempt['execution_results']['admin_a']=dict(status=200,body=q.expected_receipt(plan,'admin_a'))
            attempt['cases'].append('admin_a');return dict(leases_released=True)
        stack.enter_context(patch.object(q,'exercise',side_effect=exercise))
        return stack.enter_context(patch.object(q.fixture,'receipt',return_value=Path('/tmp/admin-evidence.json')))

    def test_full_intent_and_original_snapshot_journaled_before_seed(self):
        receipt=self.harness();order=[]
        def seed(*args,**kwargs):
            result=receipt.call_args.args[1]
            self.assertEqual(receipt.call_args.args[0],'admin-api-start')
            self.assertIsNone(result['succeeded']);self.assertFalse(result['qualified'])
            self.assertEqual(set(result['plan']),set(q.new_plan()[1]))
            self.assertIn('prior_rows',result);self.assertIn('counts_before',result)
            self.assertNotEqual(result['account_id'],result['admin_account_id'])
            order.append('seed')
        with patch.object(q.commit,'seed',side_effect=seed):result=q.qualify({})
        self.assertTrue(result['qualified']);self.assertEqual(order,['seed'])
        self.assertEqual([call.args[0] for call in receipt.call_args_list],['admin-api-start','admin-api'])

    def test_source_drift_fails_before_seed_and_after_execution_before_success(self):
        receipt=self.harness()
        with patch.object(q,'source_hashes',return_value={}),patch.object(q.commit,'seed') as seed,self.assertRaises(AssertionError):q.qualify({})
        seed.assert_not_called();receipt.assert_not_called()
        with patch.object(q,'source_hashes',side_effect=[q.INITIAL_SOURCES,{}]),patch.object(q.commit,'seed') as seed,self.assertRaises(AssertionError):q.qualify({})
        seed.assert_not_called();self.assertEqual(receipt.call_count,1)
        self.harness()
        with patch.object(q,'source_hashes',side_effect=[q.INITIAL_SOURCES,q.INITIAL_SOURCES,{}]),self.assertRaises(AssertionError):q.qualify({})
        self.assertEqual(receipt.call_count,1)

    def test_read_or_oracle_failure_retains_observed_execution_without_success(self):
        receipt=self.harness()
        async def fail(value,data,plan,attempt):
            attempt['execution_results']['admin_a']=dict(status=200,body=q.expected_receipt(plan,'admin_a'))
            q.STAGE='independent_read';raise ValueError('credential-canary')
        with patch.object(q,'exercise',side_effect=fail),redirect_stdout(io.StringIO()) as output:
            self.assertEqual(q.main(['--qualify-retained']),1)
        failure=receipt.call_args.args[1]
        self.assertFalse(failure['qualified']);self.assertEqual(failure['failed_stage'],'independent_read')
        self.assertEqual(failure['execution_results']['admin_a']['status'],200)
        self.assertNotIn('credential-canary',str(failure)+output.getvalue())

    def test_failed_success_report_records_unqualified_failure(self):
        self.harness()
        with patch.object(q.fixture,'receipt',side_effect=[Path('/tmp/start.json'),OSError('credential-canary'),Path('/tmp/failure.json')]) as receipt,redirect_stdout(io.StringIO()) as output:
            self.assertEqual(q.main(['--qualify-retained']),1)
        failure=receipt.call_args.args[1]
        self.assertFalse(failure['qualified']);self.assertEqual(failure['failed_stage'],'success_receipt')
        self.assertIn('admin_a',failure['execution_results'])
        self.assertNotIn('credential-canary',str(failure)+output.getvalue())

    def test_bootstrap_read_or_import_failure_has_safe_unqualified_evidence(self):
        import builtins
        import runpy
        original_read=Path.read_bytes;original_import=builtins.__import__
        def read(path):
            if path==q.ROOT/'platform/deployment/dev.py':raise OSError('credential-canary')
            return original_read(path)
        def importing(name,*args,**kwargs):
            if name=='qualify_capture_commit':raise ImportError('credential-canary')
            return original_import(name,*args,**kwargs)
        for stage,scope in [('source_bootstrap',patch.object(Path,'read_bytes',read)),
            ('imports',patch.object(builtins,'__import__',importing))]:
            with scope,patch.object(q.fixture,'receipt',return_value=Path('/tmp/failure.json')) as receipt,patch.object(sys,'argv',[q.__file__,'--qualify-retained']),redirect_stdout(io.StringIO()) as output:
                with self.assertRaises(SystemExit) as stopped:runpy.run_path(q.__file__,run_name='__main__')
            self.assertEqual(stopped.exception.code,1)
            self.assertFalse(receipt.call_args.args[1]['qualified'])
            self.assertEqual(json.loads(output.getvalue())['failed_stage'],stage)
            self.assertNotIn('credential-canary',str(receipt.call_args)+output.getvalue())

    def test_repeated_review_journals_current_answers_with_stale_revision_and_fresh_operation(self):
        data,plan=q.new_plan();command=data.request_inputs['repeated_review']['body']
        current=plan['admin_a2']
        self.assertEqual(command['answers'],current['command']['answers'])
        self.assertEqual(command['observation_date'],current['command']['observation_date'])
        self.assertLess(int(command['expected_revision']),current['revision'])
        self.assertEqual(data.request_inputs['repeated_review']['capture_id'],current['capture_id'])
        self.assertNotIn(command['operation_id'],[plan[name]['command']['operation_id'] for name in COMMITTED])

    def test_edit_loss_recovers_changed_and_noop_receipts_using_read_only_checks(self):
        import asyncio
        data,plan=q.new_plan();observed=[]
        async def request(label,client,method,url,expected,**kwargs):
            observed.append(('request',label))
            name='noop' if label=='edit_loss_noop_recovery' else 'admin_a'
            self.assertEqual((client,method),('admin','GET'))
            self.assertEqual(url,'/api/v1/admin/operations/'+plan[name]['command']['operation_id']+'?command_type=capture.edit')
            self.assertEqual(expected,q.expected_receipt(plan,name))
            self.assertEqual(kwargs,dict(permissions=[q.READ]))
        def inspect(label,**kwargs):
            observed.append(('inspect',label));self.assertEqual(kwargs,dict(unchanged=True))
        asyncio.run(q.recover_edit_loss(request,inspect,plan))
        self.assertEqual(observed,[('request','edit_loss_recovery'),('inspect','edit_loss_recovery'),
            ('request','edit_loss_noop_recovery'),('inspect','edit_loss_noop_recovery')])

    def test_direct_get_records_authority_and_checkout_before_assertions(self):
        import asyncio
        import httpx
        from types import SimpleNamespace
        engine=MagicMock();engine.pool.checkedout.return_value=0
        for permissions,count,passing in (([q.READ],1,True),([q.READ,q.EDIT],1,False),([],1,False),([q.READ],0,False),([q.READ],2,False)):
            checks=[];checkouts=[];attempt={'execution_results':{}}
            async def get(url,**kwargs):
                checks.extend(permissions);checkouts.extend([object() for _ in range(count)])
                return httpx.Response(200,json={},headers={'cache-control':'private, no-store'})
            client=SimpleNamespace(get=get)
            async def run():return await q.read_response(client,'/capture','detail',attempt,[engine],checks,checkouts)
            if passing:asyncio.run(run())
            else:
                with self.assertRaises(AssertionError):asyncio.run(run())
            observed=attempt['execution_results']['detail']
            self.assertEqual(observed['access_permissions'],permissions)
            self.assertEqual(observed['checkouts'],count);self.assertEqual(observed['status'],200)

    def test_closed_detail_audit_and_event_contracts_reject_added_private_keys(self):
        detail={key:None for key in q.admin_http.recovery.CaptureDetail.model_fields}
        event={key:None for key in q.audit_http.recovery.AuditEvent.model_fields}
        audit={key:None for key in q.audit_http.recovery.AuditPage.model_fields}
        audit.update(limit=30,events=[event])
        q.verify_read_shape(detail,'detail');q.verify_read_shape(audit,'audit')
        for kind,body in (('detail',detail),('audit',audit)):
            damaged=copy.deepcopy(body);damaged['private']='credential-canary'
            with self.assertRaisesRegex(AssertionError,'closed_read_contract_disagrees'):q.verify_read_shape(damaged,kind)
        damaged=copy.deepcopy(audit);damaged['events'][0]['private']='credential-canary'
        with self.assertRaisesRegex(AssertionError,'closed_audit_event_contract_disagrees'):q.verify_read_shape(damaged,'audit')
        for limit in (29,31,True,'30'):
            damaged=copy.deepcopy(audit);damaged['limit']=limit
            with self.assertRaisesRegex(AssertionError,'audit_limit_disagrees'):q.verify_read_shape(damaged,'audit')

    def test_failure_receipt_io_type_is_retained_in_safe_fallback_stdout(self):
        with patch.object(q,'qualify',side_effect=ValueError('execution-canary')),patch.object(q.fixture,'receipt',side_effect=OSError('credential-canary')),redirect_stdout(io.StringIO()) as output:
            self.assertEqual(q.main(['--qualify-retained']),1)
        result=json.loads(output.getvalue())
        self.assertEqual(result['receipt_error_type'],'OSError');self.assertEqual(result['error_type'],'ValueError')
        self.assertIsNone(result['report']);self.assertFalse(result['qualified'])
        self.assertNotIn('canary',output.getvalue())

    def test_actual_sync_create_helper_runs_inside_active_loop_and_retains_receipt_before_disposal_failure(self):
        import asyncio
        import threading
        from types import SimpleNamespace
        caller=threading.get_ident()
        for disposal_failure in (False,True):
            data,plan=q.new_plan();attempt={'execution_results':{}};threads=[]
            receipt=q.expected_receipt(plan,'create_a');engine=MagicMock()
            engine.connect.return_value.__enter__.side_effect=lambda:(threads.append(threading.get_ident()) or MagicMock())
            engine.dispose.side_effect=RuntimeError('private-disposal-canary') if disposal_failure else None
            async def execute(conn,raw,token):
                threads.append(threading.get_ident())
                self.assertIsNotNone(asyncio.get_running_loop())
                return SimpleNamespace(model_dump=lambda:receipt)
            def make_handler(data,conn):return SimpleNamespace(execute=execute)
            async def run():
                # This enclosing loop reproduces exercise()'s native call site.
                self.assertEqual(threading.get_ident(),caller)
                return await q.create_observation({'urls':{'runtime':'synthetic'}},data,plan['create_a'],attempt,'create_a')
            with patch.object(q.fixture,'engine',return_value=engine),patch.object(q.commit,'make_handler',side_effect=make_handler):
                if disposal_failure:
                    with self.assertRaisesRegex(RuntimeError,'private-disposal-canary'):asyncio.run(run())
                else:self.assertEqual(asyncio.run(run()),receipt)
            self.assertEqual(attempt['execution_results']['create_a'],dict(receipt=receipt))
            self.assertTrue(threads);self.assertTrue(all(thread!=caller for thread in threads))
            engine.dispose.assert_called_once()

    def test_cli_requires_explicit_retained_action(self):
        with patch.object(q,'qualify') as run,redirect_stdout(io.StringIO()),self.assertRaises(SystemExit):q.main([])
        run.assert_not_called()

    def test_fault_requires_actual_update_and_private_provisional_outcome(self):
        data,plan=q.new_plan();conn=object();budget=object()
        with patch.object(q.write,'execute') as native,patch.object(q.outcomes,'lookup_private',return_value=None),q.native_fault(data,plan) as observed:
            q.write.execute(conn,budget,q.admin_edit.UPDATE,{})
            with self.assertRaisesRegex(AssertionError,'uncommitted_outcome_required_before_fault'):
                q.write.execute(conn,budget,q.admin_edit.HISTORY_INSERT,{})
        self.assertEqual(observed['capture_updates'],1);self.assertIsNone(observed['native_sqlstate'])
        self.assertEqual(native.call_count,1)

    def test_fault_captures_real_driver_sqlstate_and_rethrows(self):
        data,plan=q.new_plan();found=MagicMock()
        found.receipt.return_value.model_dump.return_value=q.expected_receipt(plan,'retry')
        found.executor_actor_id=found.initiator_actor_id=data.admin_actor
        class NativeError(Exception):sqlstate='23502'
        def execute(conn,budget,statement,parameters=None):
            if 'observation_date=NULL' in statement:raise NativeError('private-driver-message')
        with patch.object(q.write,'execute',side_effect=execute),patch.object(q.outcomes,'lookup_private',return_value=found),q.native_fault(data,plan) as observed:
            q.write.execute(None,None,q.admin_edit.UPDATE)
            with self.assertRaises(NativeError):q.write.execute(None,None,q.admin_edit.HISTORY_INSERT)
        self.assertEqual(observed['native_sqlstate'],'23502');self.assertTrue(observed['outcome_present_before_fault'])
        self.assertNotIn('private-driver-message',str(observed))

if __name__=='__main__':unittest.main()
