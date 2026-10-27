"""Database-free acceptance of retained administrator list qualification."""
import copy
import io
import json
from contextlib import ExitStack, redirect_stdout
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations/tests'))
import qualify_admin_history as q

class NativeAdminHistory(unittest.TestCase):
    def test_independent_oracle_orders_ties_across_owners_and_inclusive_dates(self):
        rows=[dict(capture_id='2',created_at='2026-10-27T10:00:00Z',observation_date='2026-10-24',owner_account_id='b'),
              dict(capture_id='1',created_at='2026-10-27T10:00:00Z',observation_date='2026-10-23',owner_account_id='a'),
              dict(capture_id='3',created_at='2026-10-27T09:00:00Z',observation_date='2026-10-25',owner_account_id='a')]
        self.assertEqual([r['capture_id'] for r in q.eligible(rows,'2026-10-23','2026-10-24')],['2','1'])
        self.assertEqual([r['capture_id'] for r in q.eligible(rows,'2026-10-23','2026-10-25','a')],['1','3'])

    def test_plan_journals_all_seed_ids_and_inputs(self):
        owners,admin,plan=q.new_plan()
        self.assertEqual(owners[0].org,owners[1].org)
        self.assertNotEqual(owners[0].org,owners[2].org)
        ids=[]
        for owner,group in zip(owners,plan):
            self.assertEqual(group['owner'],vars(owner))
            self.assertEqual(len(group['entries']),5)
            for entry in group['entries']:
                ids.extend([entry['outcome_id'],entry['command']['operation_id'],entry['command']['capture_id']])
        self.assertEqual(len(ids),len(set(ids)))
        self.assertNotIn(admin['account'],[o.account for o in owners])

    def test_multirow_statement_uses_candidate_columns_without_timestamp_override(self):
        _,_,plan=q.new_plan();sql=q.multirow_insert(plan[0]['entries'])
        self.assertEqual(sql.count('INSERT INTO'),1)
        self.assertEqual(sql.count('CAST(:capture_'),5)
        self.assertNotIn('created_at',sql)
        self.assertNotIn('updated_at',sql)
        for index in range(5):self.assertIn(':actor_'+str(index),sql)

    def test_closed_source_closure_binds_self_and_actual_history_handlers(self):
        self.assertIsNone(q.BOOTSTRAP_ERROR)
        paths=q.source_paths()
        self.assertEqual(len(paths),len(set(paths)))
        self.assertFalse(any('schema_fixture' in p for p in paths))
        for name in ('admin_http','admin_read','capture_history','history_http'):
            self.assertIn('apps/kdg-capture/write-candidate/'+name+'.py',paths)
        self.assertIn('apps/kdg-capture/migrations/tests/qualify_admin_history.py',paths)

    def oracle_fixture(self):
        owners,admin,plan=q.new_plan();observed=[]
        for owner,group in zip(owners,plan):
            rows={t:[] for t in ('capture','capture_revision','operation_outcome','child','questionnaire_version')}
            rows['child']=[dict(id=owner.child,display_name='Synthetic durable qualification child')]
            rows['questionnaire_version']=[dict(id=owner.version,questionnaire_id=owner.questionnaire,display_version=1,definition=q.commit.initial_definition(owner.questions).model_dump(mode='json'))]
            for entry in group['entries']:
                c=entry['command'];common=dict(org_id=owner.org,owner_account_id=owner.account,owner_actor_id=owner.actor,
                    child_id=owner.child,questionnaire_id=owner.questionnaire,questionnaire_version_id=owner.version,
                    answers=c['answers'],observation_date=c['observation_date'],captured_at=c['captured_at'],revision=1)
                rows['capture'].append(dict(common,id=c['capture_id'],created_by=owner.actor,updated_by=owner.actor,
                    created_at='2026-10-27T10:00:00+00:00',updated_at='2026-10-27T10:00:00+00:00',creator_membership_id=1,child_eligibility_ref=owner.ref))
                attribution=dict(executor_account_id=owner.account,executor_actor_id=owner.actor,initiator_actor_id=owner.actor,
                    operation_id=c['operation_id'],command_type='capture.create')
                rows['capture_revision'].append(dict(common,**attribution,capture_id=c['capture_id'],outcome_id=entry['outcome_id']))
                rows['operation_outcome'].append(dict(attribution,id=entry['outcome_id'],capture_id=c['capture_id'],command_version=1,result_version=1,
                    result_revision=1,result=dict(capture_id=c['capture_id'],revision='1')))
            observed.append(rows)
        # Both owners' all-read sessions expose both owners, private outcomes stay separate.
        for table in ('capture','capture_revision','child','questionnaire_version'):
            combined=observed[0][table]+observed[1][table]
            observed[0][table]=copy.deepcopy(combined);observed[1][table]=copy.deepcopy(combined)
        return owners,admin,plan,observed

    def test_seed_oracle_rejects_wrong_owner_tie_links_actor_and_answers(self):
        owners,admin,plan,rows=self.oracle_fixture()
        oracle=q.verify_seed(owners,plan,rows)
        self.assertEqual(len(oracle[owners[0].org]),10)
        for table,key,value in [('capture','owner_actor_id','wrong'),('capture','created_at','2026-10-27T11:00:00+00:00'),
            ('capture','answers',{}),('capture_revision','outcome_id','wrong'),('capture_revision','executor_actor_id','wrong'),
            ('operation_outcome','result_revision',9)]:
            damaged=copy.deepcopy(rows);damaged[0][table][0][key]=value
            with self.subTest(table=table,key=key),self.assertRaises(AssertionError):q.verify_seed(owners,plan,damaged)

    def test_same_org_sessions_must_independently_include_both_owners(self):
        owners,admin,plan,rows=self.oracle_fixture()
        reordered=copy.deepcopy(rows)
        reordered[1]['capture'].reverse()
        q.verify_seed(owners,plan,reordered)
        for index in (0,1):
            damaged=copy.deepcopy(rows)
            other=owners[1-index].account
            damaged[index]['capture']=[r for r in damaged[index]['capture'] if r['owner_account_id']!=other]
            with self.subTest(session=index),self.assertRaisesRegex(AssertionError,'same_org_observations_disagree'):
                q.verify_seed(owners,plan,damaged)

    def test_original_version_and_definition_must_match_journaled_inputs(self):
        owners,admin,plan,rows=self.oracle_fixture()
        for field,value in [('id','wrong'),('questionnaire_id','wrong'),('display_version',2),('definition',{})]:
            damaged=copy.deepcopy(rows)
            damaged[0]['questionnaire_version'][0][field]=value
            with self.subTest(field=field),self.assertRaisesRegex(AssertionError,'seed_original_definition_disagrees'):
                q.verify_seed(owners,plan,damaged)

    def test_page_oracle_rejects_reordering_extra_keys_and_attribution_corruption(self):
        rows=[dict(capture_id='2',owner_actor_id='a'),dict(capture_id='1',owner_actor_id='b')]
        body=dict(org_id='org',account_id='account',from_date='2026-10-23',to_date='2026-10-25',limit=2,items=rows,next_cursor=None)
        q.verify_page(body,rows,'org','account','2026-10-23','2026-10-25',2)
        for alteration in ('order','actor','extra','header'):
            damaged=copy.deepcopy(body)
            if alteration=='order':damaged['items'].reverse()
            if alteration=='actor':damaged['items'][0]['owner_actor_id']='wrong'
            if alteration=='extra':damaged['private']='canary'
            if alteration=='header':damaged['limit']=True
            with self.subTest(alteration=alteration),self.assertRaises(AssertionError):
                q.verify_page(damaged,rows,'org','account','2026-10-23','2026-10-25',2)

    def test_actual_matrix_retains_first_response_before_dto_lease_and_authority_rejection(self):
        import asyncio
        from contextlib import asynccontextmanager
        from types import SimpleNamespace
        import httpx
        owners,admin,plan,rows=self.oracle_fixture();oracle=q.verify_seed(owners,plan,rows)
        for failure in ('dto','lease','authority','header','status','preservation','dto_and_preservation'):
            callbacks={};apps=[];attempt=dict(execution_results={},cases=[])
            @asynccontextmanager
            async def lifespan(app):yield
            def create_candidate(**kwargs):
                engine=MagicMock();engine.pool.checkedout.return_value=0
                app=SimpleNamespace(state=SimpleNamespace(recovery_engine=engine),router=SimpleNamespace(lifespan_context=lifespan),transport=kwargs['transport'])
                apps.append(app);return app
            def listen(engine,name,callback):callbacks[(id(engine),name)]=callback
            class Client:
                def __init__(self,**kwargs):self.app=kwargs['transport'].app
                async def __aenter__(self):return self
                async def __aexit__(self,*args):pass
                async def get(self,*args,**kwargs):
                    if failure!='authority':
                        await self.app.transport.handle_async_request(httpx.Request('POST','https://access.invalid',json={'permission':q.base.READ}))
                    engine=self.app.state.recovery_engine;dbapi=MagicMock()
                    dbapi.info.backend_pid=1
                    dbapi.cursor.return_value.__enter__.return_value.fetchone.return_value=('kdg_capture_runtime','kdg_capture_runtime','on','','','','')
                    callbacks[(id(engine),'checkout')](dbapi,None,None)
                    if failure=='lease':engine.pool.checkedout.return_value=1
                    part=q.eligible(oracle[owners[0].org],'2026-10-23','2026-10-25')[:1]
                    body=dict(org_id=owners[0].org,account_id=admin['account'],from_date='2026-10-23',to_date='2026-10-25',limit=1,items=part,next_cursor='continuation')
                    return httpx.Response(201 if failure=='status' else 200,json={'wrong':'DTO'} if failure in ('dto','dto_and_preservation') else body,headers={'cache-control':'public' if failure=='header' else 'private, no-store'})
            inspections=[]
            def inspect():
                inspections.append(True)
                if failure in ('preservation','dto_and_preservation'):raise OSError('private-inspection-canary')
            with patch.object(q.base.admin_http,'create_candidate',side_effect=create_candidate),patch.object(q.history_http,'create_candidate',side_effect=create_candidate),patch.object(q.event,'listen',side_effect=listen),patch.object(q.httpx,'AsyncClient',Client):
                identifier={'dto':'closed_page_disagrees','lease':'response_before_lease_release','authority':'authority_sequence_disagrees','header':'private_no_store_required','status':'response_status_disagrees','dto_and_preservation':'closed_page_disagrees'}
                if failure=='preservation':
                    with self.assertRaises(OSError):asyncio.run(q.exercise({'urls':{'runtime':'synthetic'}},owners,admin,oracle,attempt,inspect))
                else:
                    with self.subTest(failure=failure),self.assertRaisesRegex(AssertionError,'^'+identifier[failure]+'$'):
                        asyncio.run(q.exercise({'urls':{'runtime':'synthetic'}},owners,admin,oracle,attempt,inspect))
            self.assertEqual(inspections,[True])
            self.assertEqual(attempt['execution_results']['ties_0']['preservation']['passed'],failure not in ('preservation','dto_and_preservation'))
            self.assertNotIn('canary',str(attempt))
            self.assertIn('ties_0',attempt['execution_results'])
            self.assertEqual(attempt['execution_results']['ties_0']['status'],201 if failure=='status' else 200)

    def harness(self):
        stack=ExitStack();self.addCleanup(stack.close)
        for name,value in [('retained',({'urls':{'runtime':'synthetic'}},{},object())),
            ('migration_qualified','applied'),('identities',{}),('sentinel',None),('revision',q.fixture.STORAGE)]:
            stack.enter_context(patch.object(q.fixture,name,return_value=value))
        stack.enter_context(patch.object(q,'snapshot',return_value={}))
        tables=q.preserved.DELTAS
        counts={t:15 if t in ('capture','capture_revision','operation_outcome') else 3 for t in tables}
        stack.enter_context(patch.object(q.preserved,'table_counts',side_effect=[{t:0 for t in tables},counts,counts]))
        stack.enter_context(patch.object(q.commit,'seed'))
        stack.enter_context(patch.object(q,'seed_captures'))
        stack.enter_context(patch.object(q,'independent_rows',return_value={}))
        stack.enter_context(patch.object(q,'verify_seed',return_value={}))
        async def exercise(*args):return {'leases_released':True}
        stack.enter_context(patch.object(q,'exercise',side_effect=exercise))
        return stack.enter_context(patch.object(q.fixture,'receipt',return_value=Path('/tmp/synthetic-receipt.json')))

    def test_full_journal_precedes_any_parent_or_capture_seed(self):
        receipt=self.harness()
        def seed(*args,**kwargs):
            journal=receipt.call_args.args[1]
            self.assertIsNone(journal['succeeded']);self.assertFalse(journal['qualified'])
            self.assertEqual(len(journal['plan']),3)
            self.assertIn('prior_rows',journal);self.assertIn('counts_before',journal)
        with patch.object(q.commit,'seed',side_effect=seed):result=q.qualify({})
        self.assertTrue(result['qualified'])
        self.assertEqual([c.args[0] for c in receipt.call_args_list],['admin-history-start','admin-history'])

    def test_source_drift_blocks_writes_and_success(self):
        receipt=self.harness()
        for hashes in ([{}],[q.INITIAL_SOURCES,{}],[q.INITIAL_SOURCES,q.INITIAL_SOURCES,{}]):
            with patch.object(q,'source_hashes',side_effect=hashes),patch.object(q.commit,'seed') as seed:
                with self.assertRaises(AssertionError):q.qualify({})
                if len(hashes)<3:seed.assert_not_called()
        self.assertFalse(any(c.args[1].get('qualified') for c in receipt.call_args_list))

    def test_later_seed_session_failure_retains_completed_observation(self):
        self.harness();attempt={};first={'capture':[{'id':'first-session'}]}
        with patch.object(q,'independent_rows',side_effect=[first,OSError('private-oracle-canary')]):
            with self.assertRaises(OSError):q.qualify(attempt)
        self.assertEqual(attempt['seed_observations'],[first])

    def test_source_bootstrap_failure_never_imports_repository_fallback_or_writes(self):
        import builtins
        import runpy
        original_read=Path.read_bytes;original_import=builtins.__import__;imports=[]
        def read(path):
            if path==q.ROOT/'platform/deployment/dev.py':raise OSError('private-source-canary')
            return original_read(path)
        def importing(name,*args,**kwargs):
            if name in q.HELPER_SOURCES or name in q.CANDIDATE_SOURCES:imports.append(name)
            return original_import(name,*args,**kwargs)
        with patch.object(Path,'read_bytes',read),patch.object(builtins,'__import__',importing),patch.object(q.fixture,'receipt') as receipt,patch.object(sys,'argv',[q.__file__,'--qualify-retained']),redirect_stdout(io.StringIO()) as out:
            with self.assertRaises(SystemExit) as stopped:runpy.run_path(q.__file__,run_name='__main__')
        self.assertEqual(stopped.exception.code,1)
        self.assertEqual(imports,[]);receipt.assert_not_called()
        result=json.loads(out.getvalue())
        self.assertEqual(result['failed_stage'],'source_bootstrap')
        self.assertFalse(result['qualified']);self.assertIsNone(result['report'])
        self.assertNotIn('canary',out.getvalue())

    def test_execution_and_oracle_failure_keep_progress_safe(self):
        self.harness()
        def failed(attempt):
            attempt['execution_results']={'first_page':{'status':200}}
            q.STAGE='oracle';raise ValueError('credential-canary')
        with patch.object(q,'qualify',side_effect=failed),patch.object(q.fixture,'receipt',return_value=Path('/tmp/failure')) as receipt,redirect_stdout(io.StringIO()) as out:
            self.assertEqual(q.main(['--qualify-retained']),1)
        failure=receipt.call_args.args[1]
        self.assertEqual(failure['execution_results']['first_page']['status'],200)
        self.assertFalse(failure['qualified']);self.assertEqual(failure['failed_stage'],'oracle')
        self.assertNotIn('canary',str(failure)+out.getvalue())

    def test_report_failure_cannot_report_qualified_success(self):
        self.harness()
        with patch.object(q.fixture,'receipt',side_effect=[Path('/tmp/start'),OSError('private-canary'),Path('/tmp/failure')]) as receipt,redirect_stdout(io.StringIO()) as out:
            self.assertEqual(q.main(['--qualify-retained']),1)
        self.assertFalse(receipt.call_args.args[1]['qualified'])
        self.assertEqual(receipt.call_args.args[1]['failed_stage'],'success_receipt')
        self.assertNotIn('canary',out.getvalue())

    def test_cli_requires_explicit_retained_action(self):
        with patch.object(q,'qualify') as run,self.assertRaises(SystemExit):q.main([])
        run.assert_not_called()

    def test_seed_driver_failure_disposes_physical_engine(self):
        owners,_,plan=q.new_plan();engine=MagicMock()
        engine.connect.side_effect=RuntimeError('private-canary')
        with patch.object(q.fixture,'engine',return_value=engine),self.assertRaises(RuntimeError):
            q.seed_captures({'urls':{'runtime':'synthetic'}},owners[0],plan[0]['entries'])
        engine.dispose.assert_called_once()

if __name__=='__main__':unittest.main()
