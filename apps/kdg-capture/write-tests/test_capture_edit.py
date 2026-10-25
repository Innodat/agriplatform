"""Own-edit behavioral acceptance. Connection doubles do not prove native SQL/RLS."""
from datetime import date
import json
import unittest
from unittest.mock import patch

import test_capture_create as support
import capture_edit as edit
from capture_commands import parse_edit
write=edit.write
ORG,ACCOUNT,ACTOR,CHILD,VERSION,CAPTURE,OPERATION,QUESTIONNAIRE,QUESTION=(
    support.ORG,support.ACCOUNT,support.ACTOR,support.CHILD,support.VERSION,
    support.CAPTURE,support.OPERATION,support.QUESTIONNAIRE,support.QUESTION)
MAX=9223372036854775807


def command(**changes):
    value=dict(operation_id=OPERATION,command_version=1,expected_revision='4',
        observation_date='2026-10-25',answers={QUESTION:{'value':2},
        **{key:{'value':False} for key in (ACTOR,CHILD,VERSION)}})
    value.update(changes)
    return parse_edit(json.dumps(value))


class Rows(support.Rows):
    def __init__(self,value,rowcount=1):
        super().__init__(value);self.rowcount=rowcount


class Connection(support.Connection):
    def __init__(self):
        super().__init__()
        self.capture=dict(id=CAPTURE,org_id=ORG,owner_account_id=ACCOUNT,
            questionnaire_id=QUESTIONNAIRE,questionnaire_version_id=VERSION,revision=4)
        self.existing=None;self.unchanged=False;self.update_count=1;self.failure=None;self.history_count=1;self.after_execute=lambda sql:None
    def execute(self,sql,parameters):
        result=super().execute(sql,parameters);sql=str(sql)
        self.after_execute(sql)
        if self.failure and self.failure in sql:
            from sqlalchemy.exc import SQLAlchemyError
            raise SQLAlchemyError('SENSITIVE SQL values')
        if 'FROM kdg_capture.operation_outcome' in sql:return Rows(self.existing)
        if 'FROM kdg_capture.capture WHERE' in sql:
            return Rows(None if self.capture is None else dict(self.capture,unchanged=self.unchanged))
        if sql.startswith('UPDATE kdg_capture.capture'):return Rows(None,self.update_count)
        if sql.startswith('INSERT INTO kdg_capture.capture_revision'):return Rows(None,self.history_count)
        return result


class OwnEditAcceptance(unittest.TestCase):
    def setUp(self):
        self.now=100.0
        clock=patch.object(write.time,'monotonic',side_effect=lambda:self.now)
        clock.start();self.addCleanup(clock.stop)
        self.context=write.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',self.now)
        self.budget=write.Budget();self.db=Connection()
    def execute(self,cmd=None,permission='kdg_capture.capture.edit.own',capture=CAPTURE):
        with write.transaction(self.db,self.budget,self.context):
            return edit.edit_in_transaction(self.db,self.budget,self.context,capture,
                cmd if cmd is not None else command(),permission=permission)
    def mutations(self):return [(sql,args) for sql,args in self.db.calls if sql.startswith(('INSERT','UPDATE','DELETE'))]
    def test_current_own_edit_writes_conditional_capture_and_linked_receipt_history(self):
        receipt=self.execute();writes=self.mutations()
        self.assertEqual(len(writes),3)
        self.assertTrue(writes[0][0].startswith('UPDATE kdg_capture.capture'))
        self.assertEqual((writes[0][1]['previous'],writes[0][1]['revision']),(4,5))
        self.assertIn('revision=:previous',writes[0][0])
        self.assertEqual((writes[0][1]['org'],writes[0][1]['account'],writes[0][1]['capture']),(ORG,ACCOUNT,CAPTURE))
        self.assertEqual(writes[0][1]['date'],date(2026,10,25))
        self.assertEqual(json.loads(writes[0][1]['answers'])[ACTOR],{'value':False})
        self.assertTrue(writes[1][0].startswith('INSERT INTO kdg_capture.operation_outcome'))
        self.assertTrue(writes[2][0].startswith('INSERT INTO kdg_capture.capture_revision'))
        self.assertIn("'capture.edit'",writes[2][0]);self.assertEqual(writes[2][1]['outcome'],writes[1][1]['id'])
        self.assertEqual((writes[2][1]['actor'],writes[2][1]['account']),(ACTOR,ACCOUNT))
        self.assertEqual(receipt.model_dump(),dict(operation_id=OPERATION,command_type='capture.edit',command_version=1,status='committed',result=dict(capture_id=CAPTURE,revision='5')))
        self.assertEqual(self.db.calls[-1][0],'COMMIT')
    def test_history_snapshot_preserves_stored_facts_and_current_executor(self):
        self.execute()
        sql,args=next((sql,args) for sql,args in self.mutations() if sql.startswith('INSERT INTO kdg_capture.capture_revision'))
        columns=[v.strip() for v in sql.split('(',1)[1].split(')',1)[0].split(',')]
        values=[v.strip() for v in sql.split('SELECT ',1)[1].split('FROM ',1)[0].split(',')]
        projection=dict(zip(columns,values,strict=True))
        for field in ('org_id','owner_account_id','owner_actor_id','child_id','questionnaire_id','questionnaire_version_id','observation_date','answers','captured_at','revision'):
            self.assertEqual(projection[field],'c.'+field)
        self.assertEqual(projection['capture_id'],'c.id')
        self.assertEqual(projection['executor_account_id'],'CAST(:account AS uuid)')
        for field in ('executor_actor_id','initiator_actor_id'):
            self.assertEqual(projection[field],'CAST(:actor AS uuid)')
        self.assertEqual((args['account'],args['actor']),(ACCOUNT,ACTOR))
    def test_date_only_and_answers_only_proposals_bind_both_change_dimensions(self):
        proposals=[command(observation_date='2026-10-26'),command(answers={QUESTION:{'value':3},**{key:{'value':False} for key in (ACTOR,CHILD,VERSION)}})]
        for proposal in proposals:
            self.db=Connection();self.db.unchanged=False
            with self.subTest(date=proposal.observation_date):
                self.assertEqual(self.execute(proposal).result.revision,'5')
                sql,parameters=next((sql,args) for sql,args in self.db.calls if 'FROM kdg_capture.capture WHERE' in sql)
                # Protect the delegated PostgreSQL conjunction: OR would drop either partial edit.
                self.assertIn('(observation_date=CAST(:date AS date) AND answers=CAST(:answers AS jsonb)) AS unchanged',sql)
                update=self.mutations()[0][1]
                self.assertEqual(update['date'],date.fromisoformat(proposal.observation_date))
                self.assertEqual(json.loads(update['answers']),{key:value.model_dump() for key,value in proposal.answers.items()})
    def test_authorized_noop_appends_only_receipt_without_capture_update_or_history(self):
        self.db.unchanged=True;receipt=self.execute();writes=self.mutations()
        self.assertEqual(receipt.result.revision,'4');self.assertEqual(len(writes),1)
        self.assertTrue(writes[0][0].startswith('INSERT INTO kdg_capture.operation_outcome'))
        self.assertEqual(json.loads(writes[0][1]['result']),dict(capture_id=CAPTURE,revision='4'))
    def test_stale_revision_conflicts_even_when_values_are_unchanged(self):
        self.db.unchanged=True
        with self.assertRaises(edit.RevisionConflict) as failed:self.execute(command(expected_revision='3'))
        self.assertEqual(str(failed.exception),'kdg_capture.capture_revision_conflict')
        self.assertEqual(failed.exception.current_revision,'4');self.assertEqual(self.mutations(),[])
        self.assertNotIn('answers',str(failed.exception))
    def test_historical_edit_ignores_current_assignment_child_active_and_create_eligibility(self):
        self.db.child=None;self.db.assignment=None;self.db.eligibility=None
        self.assertEqual(self.execute().result.revision,'5')
        self.assertFalse(any('FROM kdg_capture.child' in sql for sql,_ in self.db.calls))
    def test_original_version_is_used_for_validation(self):
        self.execute()
        version=[args for sql,args in self.db.calls if 'FROM kdg_capture.questionnaire_version' in sql]
        self.assertEqual(len(version),1);self.assertEqual(version[0]['version'],VERSION)
        self.assertFalse(any('ORDER BY' in sql for sql,_ in self.db.calls))
    def test_invalid_original_answers_and_missing_or_malformed_version_never_write(self):
        with self.assertRaisesRegex(write.WriteError,'^validation_failed$'):self.execute(command(answers={}))
        self.assertEqual(self.mutations(),[])
        for version in (None,dict(questionnaire_id=QUESTIONNAIRE,definition={})):
            self.db=Connection();self.db.version=version
            with self.subTest(version=version),self.assertRaisesRegex(write.WriteError,'^questionnaire_version_unavailable$'):self.execute()
            self.assertEqual(self.mutations(),[])
    def test_noop_still_requires_original_answer_validation(self):
        self.db.unchanged=True
        with self.assertRaisesRegex(write.WriteError,'^validation_failed$'):self.execute(command(answers={}))
        self.assertEqual(self.mutations(),[])
    def test_existing_operation_stops_privately_before_received_target_or_semantics(self):
        with patch.object(edit.outcomes,'lookup_private',return_value=object()):
            with self.assertRaisesRegex(write.WriteError,'^operation_verification_unavailable$'):self.execute(command(answers={}))
        self.assertFalse(any('FROM kdg_capture.capture WHERE' in sql for sql,_ in self.db.calls));self.assertEqual(self.mutations(),[])
    def test_missing_or_foreign_target_uses_same_safe_failure(self):
        self.db.capture=None
        with self.assertRaisesRegex(write.WriteError,'^capture_unavailable$'):self.execute()
        self.assertEqual(self.mutations(),[])
        reads=[sql for sql,_ in self.db.calls if 'FROM kdg_capture.capture WHERE' in sql]
        self.assertEqual(len(reads),1)
        self.assertIn('org_id=CAST(:org AS uuid)',reads[0]);self.assertIn('owner_account_id=CAST(:account AS uuid)',reads[0])
    def test_wrong_scope_permission_or_input_stops_before_business_sql(self):
        for permission in ('kdg_capture.capture.edit.all','kdg_capture.capture.create.all','kdg_capture.capture.read.own'):
            self.db=Connection()
            with self.subTest(permission=permission),self.assertRaisesRegex(write.WriteError,'^invalid_write_context$'):self.execute(permission=permission)
            self.assertFalse(any('kdg_capture.' in sql for sql,_ in self.db.calls))
        self.db=Connection();self.context=write.VerifiedContext(ORG,ACCOUNT,ACTOR,'all_write',self.now)
        with self.assertRaisesRegex(write.WriteError,'^invalid_write_context$'):self.execute()
        self.assertEqual(self.mutations(),[])
    def test_invalid_ids_and_structural_input_never_lock_or_lookup(self):
        for capture,cmd in [(CAPTURE.upper(),command()),('00000000-0000-0000-0000-000000000000',command()),(CAPTURE,{'operation_id':OPERATION})]:
            self.db=Connection()
            with self.subTest(capture=capture),self.assertRaisesRegex(write.WriteError,'^validation_failed$'):self.execute(cmd,capture=capture)
            self.assertFalse(any('pg_advisory_xact_lock' in sql for sql,_ in self.db.calls));self.assertEqual(self.mutations(),[])
    def test_operation_lookup_precedes_locked_capture_read(self):
        with patch.object(edit.outcomes,'lookup_private',wraps=edit.outcomes.lookup_private) as lookup_call,patch.object(write,'outcome_lock',wraps=write.outcome_lock) as lock_call:
            self.execute()
        key=lookup_call.call_args.args[2]
        self.assertEqual((key.owner_schema,key.org_id,key.account_id,key.command_type,key.operation_id),('kdg_capture',ORG,ACCOUNT,'capture.edit',OPERATION))
        self.assertIs(lock_call.call_args.args[2],key)
        self.assertIs(lookup_call.call_args.args[1],self.budget);self.assertIs(lookup_call.call_args.args[3],self.context)
        sql=[s for s,_ in self.db.calls]
        lock=next(i for i,s in enumerate(sql) if 'pg_advisory_xact_lock' in s)
        lookup=next(i for i,s in enumerate(sql) if 'FROM kdg_capture.operation_outcome' in s)
        capture=next(i for i,s in enumerate(sql) if 'FROM kdg_capture.capture WHERE' in s)
        self.assertLess(lock,lookup);self.assertLess(lookup,capture);self.assertIn('FOR UPDATE',sql[capture])
        self.assertIn('answers=CAST(:answers AS jsonb)',sql[capture]);self.assertIn('observation_date=CAST(:date AS date)',sql[capture])
    def test_conditional_update_miss_does_not_append_receipt(self):
        self.db.update_count=0
        with self.assertRaisesRegex(write.WriteError,'^internal_error$'):self.execute()
        self.assertEqual(len(self.mutations()),1);self.assertNotIn('COMMIT',[sql for sql,_ in self.db.calls])
    def test_sql_failure_at_each_phase_exits_without_ack_or_sensitive_error(self):
        for phase in ('FROM kdg_capture.capture WHERE','FROM kdg_capture.questionnaire_version','UPDATE kdg_capture.capture','INSERT INTO kdg_capture.operation_outcome','INSERT INTO kdg_capture.capture_revision'):
            self.db=Connection();self.db.failure=phase
            with self.subTest(phase=phase),self.assertRaisesRegex(write.WriteError,'^internal_error$') as failed:self.execute()
            self.assertNotIn('SENSITIVE',str(failed.exception));self.assertNotIn('COMMIT',[sql for sql,_ in self.db.calls])
            self.assertIn(('EXIT_WITH_ERROR',{}),self.db.calls)
    def test_deadline_during_original_definition_lookup_prevents_mutation(self):
        original=Rows.one_or_none
        def late(row):
            if row.value is self.db.version:self.now=111
            return original(row)
        with patch.object(support.Rows,'one_or_none',late),self.assertRaisesRegex(write.WriteError,'^execution_timeout$'):self.execute()
        self.assertEqual(self.mutations(),[])
    def test_bigint_max_noop_is_valid_but_changed_overflow_fails_safely(self):
        self.db.capture['revision']=MAX;self.db.unchanged=True
        self.assertEqual(self.execute(command(expected_revision=str(MAX))).result.revision,str(MAX))
        self.db=Connection();self.db.capture['revision']=MAX
        with self.assertRaisesRegex(write.WriteError,'^internal_error$'):self.execute(command(expected_revision=str(MAX)))
        self.assertEqual(self.mutations(),[])
    def test_history_insert_must_materialize_exactly_one_snapshot(self):
        self.db.history_count=0
        with self.assertRaisesRegex(write.WriteError,'^internal_error$'):self.execute()
        self.assertNotIn('COMMIT',[sql for sql,_ in self.db.calls])
    def test_deadline_after_each_mutation_does_not_acknowledge_or_commit(self):
        for phase in ('UPDATE kdg_capture.capture','INSERT INTO kdg_capture.operation_outcome','INSERT INTO kdg_capture.capture_revision'):
            self.now=100;self.budget=write.Budget();self.db=Connection()
            def late(sql):
                if sql.startswith(phase):self.now=111
            self.db.after_execute=late
            with self.subTest(phase=phase),self.assertRaisesRegex(write.WriteError,'^execution_timeout$'):self.execute()
            self.assertNotIn('COMMIT',[sql for sql,_ in self.db.calls])
    def test_late_commit_ack_remains_uncertain_not_a_rollback_claim(self):
        self.db.on_commit=lambda:setattr(self,'now',111)
        with self.assertRaisesRegex(write.WriteError,'^execution_timeout$'):self.execute()
        self.assertIn(('COMMIT',{}),self.db.calls)
    def test_caller_input_mutation_after_revalidation_cannot_change_the_proposal(self):
        original=command()
        def mutate(sql):
            if 'FROM kdg_capture.capture WHERE' in sql:original.answers[QUESTION]=support.command().answers[QUESTION]
        self.db.after_execute=mutate
        self.execute(original)
        self.assertEqual(json.loads(self.mutations()[0][1]['answers'])[QUESTION],{'value':2})
    def test_failed_durable_commit_cannot_acknowledge_provisional_receipt(self):
        self.db.fail_commit=True
        with self.assertRaisesRegex(write.WriteError,'^internal_error$'):self.execute()
        self.assertNotIn('COMMIT',[sql for sql,_ in self.db.calls])

if __name__=='__main__':unittest.main()
