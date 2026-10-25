"""Retained-only qualification of the actual inert own-edit transaction body."""
import argparse
import asyncio
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[4]
APP=ROOT/'apps/kdg-capture'
def source_paths():
    return tuple(sorted(str(path.relative_to(ROOT)) for path in (
    * (APP/'write-candidate').glob('*.py'), * (APP/'api').glob('*.py'),
    APP/'write-tools/transaction_context.py',
    *(APP/'migrations/tests'/name for name in ('qualify_own_edit.py','qualify_edit_recovery_http.py',
      'qualify_capture_commit.py','qualify_capture_storage.py','capture_commit_fixture.py',
      'native_fixture.py','qualify_recovery_http.py','qualify_operation_recovery.py')),
    APP/'migrations/candidates/0002_capture_storage.py',
    ROOT/'platform/deployment/dev.py', ROOT/'platform/deployment/native_cli.py')))

def source_hashes():
    return {path:sha256((ROOT/path).read_bytes()).hexdigest() for path in source_paths()}

INITIAL_SOURCES={}
BOOTSTRAP_ERROR=None
STAGE='source_bootstrap'
sys.path.insert(0,str(Path(__file__).resolve().parent))
try:
    INITIAL_SOURCES=source_hashes()
    STAGE='imports'
    import qualify_capture_commit as commit
    import qualify_recovery_http as prior
    import qualify_edit_recovery_http as preserved
    import capture_edit as edit
    from unittest.mock import patch
    from sqlalchemy.exc import DBAPIError
    import httpx
    from sqlalchemy import event, text
    fixture=commit.fixture
    write=commit.write
    outcomes=commit.create.outcomes
    boundary=prior.boundary
except Exception as error:
    BOOTSTRAP_ERROR=error
    # Receipt custody may remain available even if source reads or candidate imports
    # fail. Importing this adapter never prepares resources or opens connections.
    try:
        import capture_commit_fixture as fixture
    except Exception:
        fixture=None


def require(condition, identifier):
    if not condition:
        raise AssertionError(identifier)


DELTAS=dict(questionnaire=1,questionnaire_version=1,child=1,child_assignment=1,
    child_eligibility=1,capture=1,operation_outcome=5,capture_revision=4)
def snapshot(admin,excluded_org):
    return preserved.snapshot(admin,excluded_org)


def table_counts(admin):
    return preserved.table_counts(admin)


def verify_preservation(before,after):
    return preserved.verify_preservation(before,after)


def verify_deltas(before,after):
    require(set(before)==set(after)==set(DELTAS),'unexpected_count_tables')
    require(all(after[t]-before[t]==DELTAS[t] for t in DELTAS),'unexpected_dataset_delta')


def new_plan():
    data=commit.Dataset()
    data.assignment_id,data.editor,data.foreign_account,data.foreign_org,data.invalid_question=[str(uuid4()) for _ in range(5)]
    create=json.loads(data.raw())
    def command(previous,observation_date,answers):
        return dict(operation_id=str(uuid4()),command_version=1,expected_revision=str(previous),
            observation_date=observation_date,answers=json.loads(json.dumps(answers)))
    answers=json.loads(json.dumps(create['answers']))
    answers[data.questions[0]]={'value':2}
    answer_edit=command(1,create['observation_date'],answers)
    date_edit=command(2,'2026-10-25',answers)
    retry_answers=json.loads(json.dumps(answers));retry_answers[data.questions[0]]={'value':3}
    invalid=json.loads(json.dumps(answers));invalid[data.invalid_question]={'value':True}
    return data,dict(create=create,answers=answer_edit,date=date_edit,
        noop=command(3,date_edit['observation_date'],answers),
        stale=command(2,date_edit['observation_date'],answers),
        invalid=command(3,date_edit['observation_date'],invalid),
        foreign_account=command(3,date_edit['observation_date'],answers),
        foreign_org=command(3,date_edit['observation_date'],answers),
        retry=command(3,date_edit['observation_date'],retry_answers))


def expected_receipt(plan,name):
    revision=dict(create=1,answers=2,date=3,noop=3,retry=4)[name]
    return dict(operation_id=plan[name]['operation_id'],command_type='capture.create' if name=='create' else 'capture.edit',
        command_version=1,status='committed',result=dict(capture_id=plan['create']['capture_id'],revision=str(revision)))


def verify_rows(data,plan,names,rows):
    """Independent domain oracle; internal outcome identities are discovered, never supplied."""
    captures,history,receipts=[rows[t] for t in ('capture','capture_revision','operation_outcome')]
    changed=[n for n in names if n!='noop']
    require(len(captures)==1 and len(history)==len(changed) and len(receipts)==len(names),'dataset_row_counts_disagree')
    capture=captures[0]
    current=plan[changed[-1]]
    common=dict(org_id=data.org,owner_account_id=data.account,owner_actor_id=data.actor,
        child_id=data.child,questionnaire_id=data.questionnaire,questionnaire_version_id=data.version,
        captured_at=plan['create']['captured_at'])
    require(all(capture[k]==v for k,v in common.items()),'immutable_capture_disagrees')
    require(capture['id']==plan['create']['capture_id'] and capture['revision']==len(changed) and
        capture['answers']==current['answers'] and capture['observation_date']==current['observation_date'],
        'current_capture_disagrees')
    require(capture['created_by']==data.actor and capture['updated_by']==(data.actor if len(changed)==1 else data.editor)
        and capture['child_eligibility_ref']==data.ref and capture['creator_membership_id']==int(data.membership),
        'capture_provenance_disagrees')
    for field in ('created_at','updated_at'):
        require(datetime.fromisoformat(capture[field]).utcoffset() is not None,'capture_timestamp_not_aware')
    require(datetime.fromisoformat(capture['updated_at'])>=datetime.fromisoformat(capture['created_at']),
        'capture_timestamp_disagrees')
    discovered={}
    for name in names:
        command=plan[name];expected=expected_receipt(plan,name)
        matches=[o for o in receipts if o['operation_id']==command['operation_id']]
        require(len(matches)==1,'original_receipt_missing')
        outcome=matches[0];discovered[name]=outcome['id']
        actor=data.actor if name=='create' else data.editor
        require(outcome['result']==expected['result'] and outcome['capture_id']==capture['id'] and
            outcome['result_revision']==int(expected['result']['revision']) and outcome['command_version']==outcome['result_version']==1
            and outcome['command_type']==expected['command_type'],'stored_receipt_disagrees')
        require(outcome['org_id']==data.org and outcome['executor_account_id']==data.account and
            outcome['executor_actor_id']==outcome['initiator_actor_id']==actor,'outcome_attribution_disagrees')
        linked=[h for h in history if h['outcome_id']==outcome['id']]
        if name=='noop':
            require(not linked,'noop_inserted_history')
            continue
        require(len(linked)==1,'history_link_disagrees')
        row=linked[0]
        require(all(row[k]==v for k,v in common.items()),'immutable_history_disagrees')
        require(row['capture_id']==capture['id'] and row['revision']==int(expected['result']['revision']) and
            row['operation_id']==command['operation_id'] and row['command_type']==expected['command_type'] and
            row['answers']==command['answers'] and row['observation_date']==command['observation_date'],
            'history_snapshot_disagrees')
        require(row['executor_account_id']==data.account and row['executor_actor_id']==row['initiator_actor_id']==actor,
            'history_attribution_disagrees')
    require(len(set(discovered.values()))==len(names),'outcome_identity_reused')
    return dict(verified=True,current_revision=len(changed),discovered_outcomes=discovered)


def read_storage(value,data,plan,names):
    """A new physical restricted read-only session, opened only after writer disposal."""
    engine=fixture.engine(value['urls']['runtime']).execution_options(postgresql_readonly=True)
    try:
        with engine.connect() as conn:
            require(conn.execute(text("SELECT current_user,session_user,current_setting('transaction_read_only')")).one()==
                ('kdg_capture_runtime','kdg_capture_runtime','on'),'independent_runtime_read_required')
            conn.rollback()
            budget=write.Budget()
            context=write.VerifiedContext(data.org,data.account,data.editor,'own_read',time.monotonic())
            with write.transaction(conn,budget,context):
                rows={table:conn.execute(text('SELECT to_jsonb(t) FROM kdg_capture.'+table+
                    ' t ORDER BY to_jsonb(t)::text')).scalars().all() for table in ('capture','capture_revision','operation_outcome')}
            return rows,verify_rows(data,plan,names,rows)
    finally:
        engine.dispose()


def verify_transition(before,after,*,unchanged=False,noop=False):
    """Preserve complete earlier immutable records, and all capture bytes for refusals/no-op."""
    if unchanged:
        require(before==after,'refused_command_changed_storage')
        return
    for table in ('capture_revision','operation_outcome'):
        require(all(row in after[table] for row in before[table]),'original_evidence_changed')
    if noop:
        require(before['capture']==after['capture'] and before['capture_revision']==after['capture_revision'],
            'noop_changed_capture_or_history')
    else:
        old,new=before['capture'][0],after['capture'][0]
        mutable={'answers','observation_date','revision','updated_at','updated_by'}
        require({k:v for k,v in old.items() if k not in mutable}==
            {k:v for k,v in new.items() if k not in mutable},'original_capture_facts_changed')
        require(datetime.fromisoformat(new['updated_at'])>datetime.fromisoformat(old['updated_at']),
            'changed_edit_timestamp_not_observed')


def execute_edit(value,data,plan,name,*,fault=False):
    """No replay adapter: invoke actual fresh-only body in its original context/Budget."""
    engine=fixture.engine(value['urls']['runtime'])
    counts=dict(capture_updates=0,history_inserts=0)
    native_fault=False
    outcome_present_before_fault=False
    original=write.execute
    def execute(conn,budget,statement,parameters=None):
        nonlocal native_fault,outcome_present_before_fault
        if statement==edit.UPDATE:counts['capture_updates']+=1
        if statement==edit.HISTORY_INSERT:
            if fault:
                key=write.OutcomeKey('kdg_capture',context.org_id,context.account_id,
                    'capture.edit',plan[name]['operation_id'])
                found=outcomes.lookup_private(conn,budget,key,context)
                require(found is not None and found.receipt().model_dump()==expected_receipt(plan,name)
                    and found.executor_actor_id==found.initiator_actor_id==data.editor,
                    'uncommitted_outcome_required_before_fault')
                outcome_present_before_fault=True
                native_fault=True
                original(conn,budget,'UPDATE kdg_capture.capture SET observation_date=NULL WHERE id=CAST(:capture AS uuid)',
                    dict(capture=plan['create']['capture_id']))
                raise AssertionError('native_fault_unexpected_success')
            counts['history_inserts']+=1
        return original(conn,budget,statement,parameters)
    try:
        with engine.connect() as conn:
            require(conn.execute(text('SELECT current_user,session_user')).one()==
                ('kdg_capture_runtime','kdg_capture_runtime'),'restricted_runtime_required')
            conn.rollback()
            budget=write.Budget()
            context=write.VerifiedContext(data.foreign_org if name=='foreign_org' else data.org,
                data.foreign_account if name=='foreign_account' else data.account,data.editor,'own_write',time.monotonic())
            with patch.object(write,'execute',execute):
                with write.transaction(conn,budget,context):
                    receipt=edit.edit_in_transaction(conn,budget,context,plan['create']['capture_id'],
                        plan[name],permission=edit.OWN)
            return dict(receipt=receipt.model_dump(),sql=counts)
    except edit.RevisionConflict as error:
        return dict(error=str(error),current_revision=error.current_revision,sql=counts)
    except write.WriteError as error:
        if fault:
            state=commit.sqlstate(error)
            require(native_fault and str(error)=='internal_error' and state in ('23502','23514'),
                'native_constraint_failure_required')
            return dict(error='internal_error',native_sqlstate=state,sql=counts,
                outcome_present_before_fault=outcome_present_before_fault)
        return dict(error=str(error),sql=counts)
    except DBAPIError as error:
        require(fault and native_fault and commit.sqlstate(error) in ('23502','23514'),'unexpected_native_failure')
        return dict(error='internal_error',native_sqlstate=commit.sqlstate(error),sql=counts,
            outcome_present_before_fault=outcome_present_before_fault)
    finally:
        engine.dispose()


def qualify(attempt):
    global STAGE
    STAGE='source_preflight'
    require(source_hashes()==INITIAL_SOURCES,'source_changed_before_execution')
    require(__debug__,'optimized_python_prohibited')
    STAGE='fixture_preflight'
    value,original,admin=fixture.retained()
    applied=fixture.migration_qualified(value)
    identities=fixture.identities(value)
    fixture.sentinel(admin)
    data,plan=new_plan()
    attempt.update(attempt_id=str(uuid4()),org_id=data.org,account_id=data.account,actor_id=data.actor,
        editor_actor_id=data.editor,foreign_account_id=data.foreign_account,foreign_org_id=data.foreign_org,
        invalid_question_id=data.invalid_question,questionnaire_id=data.questionnaire,questionnaire_version_id=data.version,
        child_id=data.child,assignment_id=data.assignment_id,question_ids=data.questions,eligibility_ref=data.ref,
        plan=plan,cases=[],sources=INITIAL_SOURCES,applied_receipt=applied)
    before=table_counts(admin);original_rows=snapshot(admin,data.org)
    STAGE='intent_journal'
    attempt['start_receipt']=str(fixture.receipt('own-edit-start',dict(attempt,succeeded=None,counts_before=before)))
    STAGE='fresh_parent_seed'
    commit.seed(admin,data,assignment_id=data.assignment_id)
    STAGE='actual_create'
    engine=fixture.engine(value['urls']['runtime'])
    attempt['execution_results']={}
    try:
        receipt=commit.execute(engine,data,json.dumps(plan['create']))
        attempt['execution_results']['create']=dict(receipt=receipt)
    finally:engine.dispose()
    require(receipt==expected_receipt(plan,'create'),'create_receipt_disagrees')
    names=['create']
    rows,proof=read_storage(value,data,plan,names)
    attempt['cases'].append('actual_create_independent_restricted_read')
    attempt['checks']={'create':proof}
    for label,name,expected,fault in (
        ('answers','answers',None,False),('date','date',None,False),('noop','noop',None,False),
        ('stale','stale','kdg_capture.capture_revision_conflict',False),
        ('invalid','invalid','validation_failed',False),('foreign_account','foreign_account','capture_unavailable',False),
        ('foreign_org','foreign_org','capture_unavailable',False),('native_fault','retry','internal_error',True),
        ('retry','retry',None,False),('duplicate','retry','operation_verification_unavailable',False)):
        STAGE=label
        result=execute_edit(value,data,plan,name,fault=fault)
        attempt['execution_results'][label]=result
        if expected:
            require(result.get('error')==expected,'expected_safe_failure_missing')
            if label=='stale':require(result.get('current_revision')=='3','conflict_revision_disagrees')
            if label=='native_fault':
                require(result['sql']==dict(capture_updates=1,history_inserts=0),'fault_not_after_update')
                require(result.get('outcome_present_before_fault') is True,'fault_not_after_outcome')
        else:
            require(result.get('receipt')==expected_receipt(plan,name),'edit_receipt_disagrees')
            require(result['sql']==dict(capture_updates=0 if name=='noop' else 1,history_inserts=0 if name=='noop' else 1),
                'unexpected_native_write_statements')
            names.append(name)
        after,proof=read_storage(value,data,plan,names)
        verify_transition(rows,after,unchanged=expected is not None,noop=name=='noop')
        attempt['checks'][label]=dict(result=result,storage=proof)
        attempt['cases'].append(label)
        rows=after
    STAGE='preservation_checks'
    after=table_counts(admin)
    verify_deltas(before,after)
    verify_preservation(original_rows,snapshot(admin,data.org))
    fixture.sentinel(admin)
    require(fixture.revision(value)==fixture.STORAGE,'ordinary_revision_changed')
    STAGE='source_postflight'
    require(source_hashes()==INITIAL_SOURCES,'source_changed_during_execution')
    result=dict(attempt,succeeded=True,qualified=True,native_own_edit_body=True,edit_http_qualified=False,
        head=fixture.STORAGE,identities=identities,counts_before=before,counts_after=after,
        prior_rows=original_rows,prior_rows_unchanged=True,sentinel_unchanged=True,real_access=False,
        real_identity_binding=False,native_contention=False,native_cancellation=False)
    STAGE='success_receipt'
    destination=fixture.receipt('own-edit',result)
    return dict(result,report=str(destination))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qualify-retained',required=True,action='store_true')
    parser.parse_args(argv)
    attempt={}
    try:
        if BOOTSTRAP_ERROR is not None:
            raise BOOTSTRAP_ERROR
        result=qualify(attempt)
        print(json.dumps(dict(succeeded=True,qualified=True,report=result['report'],
            cases=result['cases']),sort_keys=True));return 0
    except Exception as error:
        result=dict(attempt,succeeded=False,qualified=False,error_type=type(error).__name__,
            failed_stage=STAGE,sources=INITIAL_SOURCES)
        try:
            report=str(fixture.receipt('own-edit',result))
        except Exception as receipt_error:
            report=None
            result['receipt_error_type']=type(receipt_error).__name__
        # Native exceptions and SQL parameters never enter diagnostic output.
        print(json.dumps(dict(succeeded=False,qualified=False,error_type=type(error).__name__,
            failed_stage=STAGE,report=report),sort_keys=True))
        return 1

if __name__=='__main__':raise SystemExit(main())
