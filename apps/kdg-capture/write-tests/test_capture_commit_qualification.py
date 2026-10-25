"""Offline phase/oracle acceptance; actual native cases run only by explicit CLI."""
import contextlib
from io import StringIO
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
import json
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock
from sqlalchemy.engine import make_url
from unittest.mock import patch
from alembic.script import ScriptDirectory
from alembic.config import Config
from sqlalchemy.exc import SQLAlchemyError

ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT/'apps/kdg-capture/migrations/tests/qualify_capture_commit.py'
spec = importlib.util.spec_from_file_location('kdg_commit_acceptance', PATH)
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)


def failure(code='23514'):
    error = SQLAlchemyError('PRIVATE_SYNTHETIC_CREDENTIAL')
    error.orig = SimpleNamespace(sqlstate=code)
    return error


class CaptureCommitAcceptance(unittest.TestCase):
    def test_exact_test_only_graph_preserves_active_discovery(self):
        active = ScriptDirectory.from_config(Config(str(ROOT/'apps/kdg-capture/alembic.ini')))
        self.assertEqual(active.get_current_head(), q.fixture.FOUNDATION)
        retained = ScriptDirectory.from_config(q.fixture.configuration())
        self.assertEqual(retained.get_current_head(), '0002_kdg_capture_storage')
        self.assertEqual(retained.get_revision(q.fixture.STORAGE).down_revision, q.fixture.FOUNDATION)

    def test_migration_graph_mismatch_refuses_before_target_or_upgrade(self):
        from unittest.mock import MagicMock
        for heads,parent in ((['unexpected'],q.fixture.FOUNDATION),
                             ([q.fixture.STORAGE],'unexpected_parent')):
            graph=MagicMock()
            graph.get_heads.return_value=heads
            graph.get_revision.return_value.down_revision=parent
            with patch.object(q.ScriptDirectory,'from_config',return_value=graph), \
                 patch.object(q.fixture,'retained') as retained, \
                 patch.object(q.command,'upgrade') as upgrade:
                with self.assertRaisesRegex(AssertionError,'unexpected_candidate_graph'):
                    q.migrate_retained()
                retained.assert_not_called()
                upgrade.assert_not_called()

    def test_no_explicit_or_combined_phase_never_connects(self):
        for args in ([],['--run'],['--migrate-retained','--qualify-retained']):
            with patch.object(q.fixture,'retained',side_effect=AssertionError('must not connect')) as connect:
                with contextlib.redirect_stderr(StringIO()):
                    self.assertEqual(q.main(args),1)
                connect.assert_not_called()

    def test_separate_explicit_phases(self):
        result = dict(head=q.fixture.STORAGE,report='/private/receipt')
        for flag,selected,other in (('--migrate-retained','migrate_retained','qualify_retained'),
                                    ('--qualify-retained','qualify_retained','migrate_retained')):
            with patch.object(q,selected,return_value=result) as action, patch.object(q,other) as forbidden:
                with contextlib.redirect_stdout(StringIO()):
                    self.assertEqual(q.main([flag]),0)
                action.assert_called_once_with()
                forbidden.assert_not_called()

    def test_migration_failure_reports_phase_and_never_qualifies(self):
        with patch.object(q,'migrate_retained',side_effect=failure('42501')), patch.object(q,'qualify_retained') as qualify, patch.object(q.fixture,'receipt'):
            with contextlib.redirect_stderr(StringIO()) as output:
                self.assertEqual(q.main(['--migrate-retained']),1)
            qualify.assert_not_called()
            self.assertIn('"phase": "migrate"',output.getvalue())
            self.assertIn('42501',output.getvalue())
            self.assertNotIn('PRIVATE',output.getvalue())

    def test_missing_migration_blocks_before_seed_or_runtime_engine(self):
        with patch.object(q.fixture,'retained',return_value=({},None,None)), \
             patch.object(q.fixture,'migration_qualified',side_effect=ValueError('migration_required')), \
             patch.object(q,'seed') as seed, patch.object(q.fixture,'engine') as engine, patch.object(q.fixture,'receipt'):
            with self.assertRaisesRegex(ValueError,'migration_required'):
                q.qualify_retained()
            seed.assert_not_called()
            engine.assert_not_called()

    def test_start_receipt_records_dataset_before_failed_seed(self):
        from sqlalchemy.engine import make_url
        recorded=[]
        def seed_failed(admin,data):
            self.assertEqual(len(recorded),1)
            self.assertEqual(recorded[0][0],'qualification-start')
            intent=recorded[0][1]
            for field,expected in (('org_id',data.org),('account_id',data.account),
                ('actor_id',data.actor),('questionnaire_version_id',data.version),('child_id',data.child)):
                self.assertEqual(intent[field],expected)
            self.assertTrue(intent['sources'])
            raise ValueError('seed_failed')
        with patch.object(q.fixture,'retained',return_value=({},None,make_url('postgresql://synthetic@localhost/synthetic'))), \
             patch.object(q.fixture,'migration_qualified'), \
             patch.object(q.fixture.native,'retained_cluster_state',return_value='before'), \
             patch.object(q.fixture,'identities'),patch.object(q.fixture,'sentinel'), \
             patch.object(q.fixture,'receipt',side_effect=lambda *args:recorded.append(args)), \
             patch.object(q,'seed',side_effect=seed_failed):
            with self.assertRaisesRegex(ValueError,'seed_failed'):
                q.qualify_retained()

    def test_missing_storage_oracle_demands_actual_missing_table(self):
        value={'urls':{'runtime':'synthetic'}}
        from unittest.mock import MagicMock
        engine=MagicMock()
        for code in ('42P01','42501',None):
            error= q.handler.HandlerError(500,'internal_error')
            error.__context__=failure(code)
            async def refuse(*args): raise error
            fake=SimpleNamespace(execute=refuse)
            with patch.object(q.fixture,'engine',return_value=engine), \
                 patch.object(q,'make_handler',return_value=fake), \
                 patch.object(q.fixture,'revision',return_value=q.fixture.FOUNDATION):
                if code=='42P01':
                    q.missing_storage(value)
                else:
                    with self.assertRaisesRegex(AssertionError,'missing_table_failure_required'):
                        q.missing_storage(value)

    def test_qualification_failure_safe_and_retained_receipt(self):
        with patch.object(q,'qualify_retained',side_effect=failure()),patch.object(q.fixture,'receipt') as receipt:
            with contextlib.redirect_stderr(StringIO()) as output:
                self.assertEqual(q.main(['--qualify-retained']),1)
            self.assertNotIn('PRIVATE',output.getvalue())
            self.assertIn('"phase": "qualify"',output.getvalue())
            self.assertFalse(receipt.call_args.args[1]['succeeded'])
            self.assertEqual(receipt.call_args.args[0],'qualify')

    def test_native_oracle_does_not_accept_expected_count_disagreement(self):
        from unittest.mock import MagicMock
        engine=MagicMock()
        engine.connect.return_value.__enter__.return_value.execute.return_value.scalar_one.return_value=0
        with patch.object(q.write,'transaction',return_value=contextlib.nullcontext()):
            with self.assertRaisesRegex(AssertionError,'triplet_count_disagreement:capture'):
                q.read_triplet(engine,q.Dataset(),q.Dataset().raw())

    def test_changed_body_keeps_operation_identity(self):
        data=q.Dataset()
        import json
        raw=data.raw()
        retry=q.changed(raw,answers={},child_id=str(q.uuid4()))
        self.assertEqual(json.loads(raw)['operation_id'],json.loads(retry)['operation_id'])
        self.assertNotEqual(json.loads(raw)['answers'],json.loads(retry)['answers'])

    def test_latest_failed_migration_receipt_blocks_even_if_head_present(self):
        from unittest.mock import MagicMock
        path=MagicMock()
        path.stat.return_value.st_mtime_ns=1
        with patch.object(q.fixture,'revision',return_value=q.fixture.STORAGE), \
             patch.object(q.fixture,'FIXTURE') as fixture_path, \
             patch.object(q.fixture.native,'private_json',return_value={'succeeded':False}):
            fixture_path.parent.glob.return_value=[path]
            fixture_path.read_bytes.return_value=b'fixture'
            with self.assertRaisesRegex(ValueError,'reconciliation_required'):
                q.fixture.migration_qualified({})


class ProvenanceAndFailureTests(unittest.TestCase):
    def provenance(self, directory, **changes):
        target=Path(directory)/'fixture.json'
        if not target.exists():
            q.fixture.native.write_private(target,{})
        result=dict(succeeded=True,head=q.fixture.STORAGE,database=q.fixture.DATABASE,
            run_id=q.fixture.native.RUN,fixture_sha256=q.sha256(target.read_bytes()).hexdigest(),
            action='upgrade',sources={q.fixture.CANDIDATE:q.sha256((q.fixture.ROOT/q.fixture.CANDIDATE).read_bytes()).hexdigest()})
        result.update(changes)
        q.fixture.native.write_private(Path(directory)/'capture-commit-migrate-proof.json',result)
        return target

    def test_provenance_rejects_changed_source_and_foreign_custody(self):
        for change in ({'sources':{}},{'sources':{q.fixture.CANDIDATE:'changed'}},
                       {'run_id':'foreign'},{'database':'foreign'},{'fixture_sha256':'changed'},
                       {'action':'reconciled_existing_head'}):
            with self.subTest(change=change),TemporaryDirectory() as directory:
                target=self.provenance(directory,**change)
                with patch.object(q.fixture,'FIXTURE',target),patch.object(q.fixture,'revision',return_value=q.fixture.STORAGE):
                    with self.assertRaisesRegex(ValueError,'reconciliation_required'):
                        q.fixture.migration_qualified({})
                    with self.assertRaisesRegex(ValueError,'reconciliation_required'):
                        q.fixture.migration_provenance()

    def test_known_upgrade_provenance_required_despite_reconciled_receipt(self):
        with TemporaryDirectory() as directory:
            target=self.provenance(directory)
            with patch.object(q.fixture,'FIXTURE',target),patch.object(q.fixture,'revision',return_value=q.fixture.STORAGE):
                proof=q.fixture.migration_qualified({})
                self.assertTrue(proof.endswith('capture-commit-migrate-proof.json'))
                failed=Path(directory)/'capture-commit-migrate-failed.json'
                q.fixture.native.write_private(failed,dict(succeeded=False,head=q.fixture.STORAGE))
                with self.assertRaisesRegex(ValueError,'reconciliation_required'):
                    q.fixture.migration_qualified({})
                # Explicit reconciliation may reuse known applied provenance.
                self.assertEqual(q.fixture.migration_provenance(),proof)

    def migration_patches(self, stack, revisions):
        stack.enter_context(patch.object(q.fixture,'retained',return_value=({},dict(before='metadata'),make_url('postgresql://fixture@localhost/synthetic'))))
        stack.enter_context(patch.object(q.fixture.native,'retained_cluster_state',return_value='metadata'))
        stack.enter_context(patch.object(q.fixture,'identities'))
        stack.enter_context(patch.object(q.fixture,'sentinel'))
        stack.enter_context(patch.object(q.fixture,'revision',side_effect=revisions))
        stack.enter_context(patch.object(q.fixture,'migration_environment',return_value=contextlib.nullcontext()))
        stack.enter_context(patch.object(q,'missing_storage'))
        return stack.enter_context(patch.object(q.fixture,'receipt',return_value=Path('/private/failure.json')))

    def test_actual_upgrade_failure_retains_observed_head_and_original_once(self):
        for observed in (q.fixture.FOUNDATION,q.fixture.STORAGE,ValueError('reconnect_failed')):
            original=failure('42501')
            with self.subTest(observed=observed),contextlib.ExitStack() as stack:
                receipt=self.migration_patches(stack,[q.fixture.FOUNDATION,observed])
                upgrade=stack.enter_context(patch.object(q.command,'upgrade',side_effect=original))
                with self.assertRaises(SQLAlchemyError) as caught:
                    q.migrate_retained()
                self.assertIs(caught.exception,original)
                upgrade.assert_called_once()
                self.assertEqual(receipt.call_count,1)
                recorded=receipt.call_args.args[1]
                self.assertEqual(recorded['head'],'unavailable' if isinstance(observed,Exception) else observed)
                self.assertEqual(recorded['before_head'],q.fixture.FOUNDATION)
                self.assertEqual(recorded['sqlstate'],'42501')
                self.assertEqual(recorded['failure_type'],'SQLAlchemyError')
                self.assertIn(q.fixture.CANDIDATE,recorded['sources'])
                self.assertEqual(original.capture_commit_failure_receipt,'/private/failure.json')
                with patch.object(q,'migrate_retained',side_effect=original),contextlib.redirect_stderr(StringIO()) as output:
                    self.assertEqual(q.main(['--migrate-retained']),1)
                self.assertIn('/private/failure.json',output.getvalue())
                self.assertEqual(receipt.call_count,1,'CLI must preserve detailed failure receipt')

    def test_existing_head_reconciliation_requires_applied_provenance_without_upgrade(self):
        for known in (False,True):
            with self.subTest(known=known),contextlib.ExitStack() as stack:
                receipt=self.migration_patches(stack,[q.fixture.STORAGE,q.fixture.STORAGE])
                provenance=stack.enter_context(patch.object(q.fixture,'migration_provenance',
                    side_effect=None if known else ValueError('provenance_missing'),return_value='/private/applied.json'))
                upgrade=stack.enter_context(patch.object(q.command,'upgrade'))
                if known:
                    result=q.migrate_retained()
                    self.assertEqual(result['action'],'reconciled_existing_head')
                    self.assertEqual(result['applied_receipt'],'/private/applied.json')
                else:
                    with self.assertRaisesRegex(ValueError,'provenance_missing'):
                        q.migrate_retained()
                    self.assertFalse(receipt.call_args.args[1]['succeeded'])
                upgrade.assert_not_called()
                provenance.assert_called_once_with()

    def test_source_inventory_contains_executing_models_custody_and_migration_inputs(self):
        sources=q.source_hashes()
        for name in ('migrations/tests/native_fixture.py','migrations/tests/qualify_capture_storage.py',
            'api/context.py','api/capture_commands.py','api/questionnaire.py',
            'database-tools/owned_migration.py','alembic.ini','migrations/versions/0001_foundation.py'):
            path='apps/kdg-capture/'+name
            self.assertEqual(sources[path],q.sha256((ROOT/path).read_bytes()).hexdigest())


class ConcreteReadOracleTests(unittest.TestCase):
    def setUp(self):
        self.data=q.Dataset()
        self.raw=self.data.raw()
        self.command=json.loads(self.raw)
        c,d=self.command,self.data
        self.row=[d.account,d.actor,d.version,1,c['answers'],c['captured_at'],d.actor,d.actor,
            d.account,d.actor,d.actor,d.version,c['answers'],c['captured_at'],c['operation_id'],
            dict(capture_id=c['capture_id'],revision='1'),d.child,d.questionnaire,
            q.date.fromisoformat(c['observation_date']),d.ref,1,d.child,d.questionnaire,
            q.date.fromisoformat(c['observation_date']),1,'capture.create',c['operation_id'],'capture.create',1]

    def engine(self,counts,row=None):
        engine=MagicMock()
        results=[]
        for count in counts:
            result=MagicMock()
            result.scalar_one.return_value=count
            results.append(result)
        if row is not None:
            result=MagicMock()
            result.one.return_value=row
            results.append(result)
        engine.connect.return_value.__enter__.return_value.execute.side_effect=results
        return engine

    def test_persisted_domain_and_operation_fields_cannot_disagree(self):
        with patch.object(q.write,'transaction',return_value=contextlib.nullcontext()):
            q.read_triplet(self.engine([1,1,1],self.row),self.data,self.raw)
            for index in range(16,29):
                row=self.row.copy()
                row[index]='wrong'
                with self.subTest(index=index),self.assertRaisesRegex(AssertionError,'disagreement'):
                    q.read_triplet(self.engine([1,1,1],row),self.data,self.raw)
            for index in (14,15):
                row=self.row.copy()
                row[index]='wrong-waiting-operation'
                with self.subTest(index=index),self.assertRaisesRegex(AssertionError,'disagreement'):
                    q.read_triplet(self.engine([1,1,1],row),self.data,self.raw)

    def test_failed_and_alternate_targets_require_capture_and_history_absence(self):
        with patch.object(q.write,'transaction',return_value=contextlib.nullcontext()):
            q.read_absent_targets(self.engine([0,0]),self.data,self.raw)
            for counts,error in (([1,0],'unexpected_capture_survived'),([0,1],'unexpected_history_survived')):
                with self.subTest(counts=counts),self.assertRaisesRegex(AssertionError,error):
                    q.read_absent_targets(self.engine(counts),self.data,self.raw)
            with self.assertRaisesRegex(AssertionError,'loser_orphan_history'):
                q.read_absent_operation(self.engine([0,1]),self.data,self.raw)

    def test_final_dataset_requires_five_of_each_scoped_record(self):
        with patch.object(q.write,'transaction',return_value=contextlib.nullcontext()):
            self.assertEqual(q.read_dataset_counts(self.engine([5,5,5]),self.data),
                dict(capture=5,operation_outcome=5,capture_revision=5))
            for index in range(3):
                counts=[5,5,5]
                counts[index]=6
                with self.subTest(index=index),self.assertRaisesRegex(AssertionError,'dataset_count_disagreement'):
                    q.read_dataset_counts(self.engine(counts),self.data)


class CorrelationTests(unittest.TestCase):
    def test_start_failure_and_success_share_command_journal_and_completed_cases(self):
        for fail in (False,True):
            records=[]
            executed=[]
            def record(phase,result):
                records.append((phase,dict(result)))
                return Path('/private/'+phase+'.json')
            def run(engine,data,raw,writer=None):
                start=records[0][1]
                self.assertTrue(start['attempt_id'])
                self.assertIn(dict(operation_id=json.loads(raw)['operation_id'],capture_id=json.loads(raw)['capture_id']),start['commands'].values())
                executed.append(raw)
                if fail and len(executed)==2:
                    raise ValueError('execution_failed')
                return {'original':'receipt'}
            with self.subTest(fail=fail),contextlib.ExitStack() as stack:
                stack.enter_context(patch.object(q.fixture,'retained',return_value=({'urls':{'runtime':'synthetic'}},{'before':'metadata'},make_url('postgresql://fixture@localhost/synthetic'))))
                for name in ('migration_qualified','identities','sentinel'):
                    stack.enter_context(patch.object(q.fixture,name))
                stack.enter_context(patch.object(q.fixture.native,'retained_cluster_state',return_value='metadata'))
                stack.enter_context(patch.object(q.fixture,'receipt',side_effect=record))
                stack.enter_context(patch.object(q.fixture,'engine',return_value=MagicMock()))
                stack.enter_context(patch.object(q,'seed'))
                stack.enter_context(patch.object(q,'execute',side_effect=run))
                checks={}
                for name in ('read_triplet','read_absent_targets','read_absent_operation','race','authority_cases','restrictions'):
                    checks[name]=stack.enter_context(patch.object(q,name))
                counts=stack.enter_context(patch.object(q,'read_dataset_counts',return_value=dict(capture=5,operation_outcome=5,capture_revision=5)))
                if fail:
                    with self.assertRaisesRegex(ValueError,'execution_failed'):
                        q.qualify_retained()
                else:
                    result=q.qualify_retained()
                    self.assertEqual(len(result['cases']),8)
                    counts.assert_called_once()
                    self.assertEqual(checks['read_absent_targets'].call_count,3)
                    checks['read_absent_operation'].assert_called_once()
                    waiting=records[0][1]['commands']['failure_second']
                    persisted=[json.loads(call.args[2]) for call in checks['read_triplet'].call_args_list]
                    self.assertTrue(any(item['capture_id']==waiting['capture_id'] and item['operation_id']==waiting['operation_id'] for item in persisted))
                self.assertEqual([phase for phase,_ in records],['qualification-start','qualify'])
                start,end=records[0][1],records[1][1]
                self.assertEqual(end['attempt_id'],start['attempt_id'])
                self.assertEqual(end['start_receipt'],'/private/qualification-start.json')
                self.assertEqual(end['commands'],start['commands'])
                self.assertEqual(len(end['commands']),10)
                self.assertFalse(any(key in str(end['commands']) for key in ('answers','captured_at')))
                self.assertEqual(end['succeeded'],not fail)
                if fail:
                    self.assertEqual(end['cases'],['fresh_commit_independent_restricted_triplet'])

if __name__ == '__main__': unittest.main()
