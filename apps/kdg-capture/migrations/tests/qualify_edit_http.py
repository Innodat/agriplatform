"""Retained-only qualification of the actual candidate PUT orchestration."""
import argparse
import asyncio
from datetime import datetime, timezone
from hashlib import sha256
from itertools import groupby
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
    *(APP/'migrations/tests'/name for name in ('qualify_edit_http.py','qualify_own_edit.py','qualify_edit_recovery_http.py',
      'qualify_capture_commit.py','qualify_capture_storage.py','capture_commit_fixture.py',
      'native_fixture.py','qualify_recovery_http.py','qualify_operation_recovery.py')),
    APP/'migrations/candidates/0002_capture_storage.py',
    ROOT/'platform/deployment/dev.py', ROOT/'platform/deployment/native_cli.py',
    ROOT/'platform/deployment/environments/kdg-local.json')))

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
    import qualify_own_edit as own
    import edit_http as boundary
    import threading
    import capture_edit as edit
    from unittest.mock import patch
    from sqlalchemy.exc import DBAPIError
    import httpx
    from sqlalchemy import event, text
    fixture=commit.fixture
    write=commit.write
    outcomes=commit.create.outcomes

except Exception as error:
    BOOTSTRAP_ERROR=error
    # Receipt custody may remain available even if source reads or candidate imports
    # fail. Importing this adapter never prepares resources or opens connections.
    try:
        import capture_commit_fixture as fixture
    except Exception:
        fixture=None

if BOOTSTRAP_ERROR is None:
    require=commit.require
    new_plan=own.new_plan
    expected_receipt=own.expected_receipt
    read_storage=own.read_storage
    verify_transition=own.verify_transition
    verify_deltas=own.verify_deltas
    verify_preservation=own.verify_preservation
    table_counts=own.table_counts
    snapshot=own.snapshot
    DELTAS=own.DELTAS


def verify_observation(result,status,body):
    require(result['leased']==0,'response_before_lease_release')
    require(result['status']==status,'unexpected_http_status')
    require(result['cache_control']=='private, no-store','private_response_required')
    require(result['body']==body,'unexpected_http_body')


def retain_response(attempt,label,response,*,leased,sql,permissions,fault=None):
    """Save effects before decoding; malformed bytes/exception messages stay private."""
    observed=dict(status=response.status_code,cache_control=response.headers.get('cache-control'),
        leased=leased,sql=dict(sql),permissions=list(permissions))
    if fault is not None:observed.update(fault)
    attempt['execution_results'][label]=observed
    try:
        observed['body']=response.json()
    except Exception as error:
        observed['body_decode_error_type']=type(error).__name__
        raise
    return observed


def case_groups(sequence):
    """A candidate owns one fixed organization for each contiguous scope group."""
    return groupby(sequence,key=lambda case:bool(case.get('foreign_org',False)))


def verify_admission(case,observed,before_checkout,after_checkout):
    read='kdg_capture.capture.read.own'
    expected=[read] if case.get('denied')==read else (
        [read,edit.OWN] if case.get('denied') or not case.get('no_checkout') else [])
    require(observed['permissions']==expected,'expected_current_authority_sequence_required')
    if case.get('no_checkout'):
        require(after_checkout==before_checkout,'refusal_checked_out_connection')


def cases(data,plan):
    """Every supplied path and operation is journaled before seeding."""
    target=plan['create']['capture_id']
    replay=dict(plan['answers'],expected_revision='1',answers=plan['invalid']['answers'])
    result=[dict(label=name,name=name,path=target,status=200,receipt=name)
        for name in ('answers','date','noop')]
    result.extend([
        dict(label='committed_replay',name='answers',path=data.invalid_question,command=replay,status=200,receipt='answers',unchanged=True),
        dict(label='stale',name='stale',path=target,status=409,error='kdg_capture.capture_revision_conflict',unchanged=True),
        dict(label='invalid',name='invalid',path=target,status=422,error='validation_failed',unchanged=True),
        dict(label='foreign_account',name='foreign_account',path=target,status=404,error='capture_unavailable',foreign_account=True,unchanged=True),
        dict(label='scope_reuse',name='answers',path=target,status=200,receipt='answers',unchanged=True),
        dict(label='foreign_org',name='foreign_org',path=target,status=404,error='capture_unavailable',foreign_org=True,unchanged=True),
    ])
    for permission in ('kdg_capture.capture.read.own','kdg_capture.capture.edit.own'):
        for name,suffix in (('retry',''),('answers','_replay')):
            result.append(dict(label='denied_'+permission.split('.')[-2]+suffix,name=name,path=target,status=403,
                error='access_denied',denied=permission,no_checkout=True,unchanged=True))
    for label,change,status,error in (
        ('malformed_json',dict(raw='{'),422,'validation_failed'),
        ('missing_bearer',dict(authorization=None),401,'authentication_required'),
        ('closed_query',dict(query='?org_id=foreign'),422,'validation_failed')):
        result.append(dict(label=label,name='retry',path=target,status=status,error=error,no_checkout=True,unchanged=True,**change))
    result.extend([
        dict(label='native_fault',name='retry',path=target,status=500,error='internal_error',fault=True,unchanged=True),
        dict(label='retry',name='retry',path=target,status=200,receipt='retry'),
        dict(label='duplicate',name='retry',path=target,status=200,receipt='retry',unchanged=True),
    ])
    return result


async def exercise(value,data,plan,attempt,rows,names):
    """Only Access is mocked; ordinary candidate engine/pool/worker/body execute."""
    global STAGE
    state=dict(account=data.account,denied=None,checkouts=0,permissions=[],fault=False)
    physical=set();closed=set()
    async def run(org,selected):
        nonlocal rows
        async def access(request):
            request_body=json.loads(request.content)
            permission=request_body['permission']
            require(request_body==dict(permission=permission,authorization_scope=dict(kind='organization',org_id=org))
                and permission in ('kdg_capture.capture.read.own',edit.OWN),'exact_capability_scope_required')
            state['permissions'].append(permission)
            if permission==state['denied']:
                return httpx.Response(403,json=dict(detail=dict(code='access_denied')))
            return httpx.Response(200,json=dict(account_id=state['account'],actor_id=data.editor,
                membership_id=data.membership,decision_id=str(uuid4()),permission=permission,
                authorization_scope=dict(kind='organization',org_id=org),
                resource_scope=dict(kind='own_account',account_id=state['account']),
                checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')))
        app=boundary.create_candidate(org_id=org,access_url='https://access.invalid',
            service_key='synthetic-service-key',database_url=value['urls']['runtime'],transport=httpx.MockTransport(access))
        engine=app.state.edit_engine
        def checkout(dbapi,record,proxy):
            with dbapi.cursor() as cursor:
                cursor.execute("SELECT current_user,session_user,current_setting('transaction_read_only'),current_setting('app.org_id',true),current_setting('app.account_id',true),current_setting('app.actor_id',true),current_setting('app.mode',true),pg_backend_pid()")
                row=cursor.fetchone()
            dbapi.rollback()
            require(row[:3]==('kdg_capture_runtime','kdg_capture_runtime','off'),'restricted_ordinary_writer_required')
            require(all(item in (None,'') for item in row[3:7]),'pooled_context_not_cleared')
            physical.add(row[7]);state['checkouts']+=1
        event.listen(engine,'checkout',checkout)
        event.listen(engine,'close',lambda dbapi,record:closed.add(dbapi.info.backend_pid))
        original=write.execute
        sql=dict(capture_updates=0,history_inserts=0)
        def execute(conn,budget,statement,parameters=None):
            if statement==edit.UPDATE:sql['capture_updates']+=1
            if statement==edit.HISTORY_INSERT:
                if state['fault']:
                    context=write.VerifiedContext(org,data.account,data.editor,'own_write',time.monotonic())
                    key=write.OutcomeKey('kdg_capture',org,data.account,'capture.edit',plan['retry']['operation_id'])
                    found=outcomes.lookup_private(conn,budget,key,context)
                    require(found is not None and found.receipt().model_dump()==expected_receipt(plan,'retry')
                        and found.executor_actor_id==found.initiator_actor_id==data.editor,'uncommitted_outcome_required_before_fault')
                    state['outcome_present_before_fault']=True
                    try:
                        original(conn,budget,'UPDATE kdg_capture.capture SET observation_date=NULL WHERE id=CAST(:capture AS uuid)',dict(capture=plan['create']['capture_id']))
                    except Exception as error:
                        state['native_sqlstate']=commit.sqlstate(error)
                        raise
                    raise AssertionError('native_fault_unexpected_success')
                sql['history_inserts']+=1
            return original(conn,budget,statement,parameters)
        async with app.router.lifespan_context(app):
            # Explicit warm-up precedes requests and never changes an observation.
            with engine.connect():pass
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='https://kdg.invalid') as client:
                for case in selected:
                    STAGE=case['label'];state.update(account=data.foreign_account if case.get('foreign_account') else data.account,
                        denied=case.get('denied'),fault=case.get('fault',False))
                    state['permissions']=[];sql.update(capture_updates=0,history_inserts=0)
                    before_checkout=state['checkouts']
                    headers={'Content-Type':'application/json'}
                    if case.get('authorization','Bearer synthetic-account') is not None:
                        headers['Authorization']=case.get('authorization','Bearer synthetic-account')
                    with patch.object(write,'execute',execute):
                        response=await client.put('/api/v1/captures/'+case['path']+case.get('query',''),headers=headers,
                            content=case.get('raw',json.dumps(case.get('command',plan[case['name']]))))
                    observed=retain_response(attempt,case['label'],response,leased=engine.pool.checkedout(),
                        sql=sql,permissions=state['permissions'],fault=(dict(native_sqlstate=state.get('native_sqlstate'),
                        outcome_present_before_fault=state.get('outcome_present_before_fault',False)) if case.get('fault') else None))
                    expected=expected_receipt(plan,case['receipt']) if 'receipt' in case else prior.envelope(case['error'])
                    if case['label']=='stale':expected['current_revision']='3'
                    verify_observation(observed,case['status'],expected)
                    verify_admission(case,observed,before_checkout,state['checkouts'])
                    if case.get('fault'):
                        require(observed.get('native_sqlstate') in ('23502','23514') and observed.get('outcome_present_before_fault') is True
                            and sql==dict(capture_updates=1,history_inserts=0),'actual_native_fault_after_outcome_required')
                    elif case.get('unchanged') or case['name']=='noop':
                        require(sql==dict(capture_updates=0,history_inserts=0),'unexpected_update_or_history')
                    else:require(sql==dict(capture_updates=1,history_inserts=1),'changed_edit_not_executed')
                    if 'receipt' in case and not case.get('unchanged'):names.append(case['name'])
                    STAGE=case['label']+'_independent_storage'
                    after,proof=read_storage(value,data,plan,names)
                    verify_transition(rows,after,unchanged=case.get('unchanged',False),noop=case['name']=='noop')
                    attempt['checks'][case['label']]=proof;attempt['cases'].append(case['label']);rows=after
        require(engine.pool.checkedout()==0 and physical<=closed,'lifespan_connections_not_disposed')
    sequence=attempt['http_plan']
    # Preserve the matrix sequence while constructing a distinct fixed-org candidate.
    for foreign_org,group in case_groups(sequence):
        await run(data.foreign_org if foreign_org else data.org,group)
    return dict(leases_released=True,physical_connections=len(physical),physical_connections_closed=len(closed),
        physical_connections_disposed=physical<=closed)


def qualify(attempt):
    global STAGE
    STAGE='source_preflight'
    require(source_hashes()==INITIAL_SOURCES,'source_changed_before_execution')
    require(__debug__,'optimized_python_prohibited')
    STAGE='fixture_preflight'
    value,original,admin=fixture.retained();applied=fixture.migration_qualified(value)
    identities=fixture.identities(value);fixture.sentinel(admin)
    data,plan=new_plan()
    attempt.update(attempt_id=str(uuid4()),org_id=data.org,account_id=data.account,actor_id=data.actor,editor_actor_id=data.editor,
        foreign_account_id=data.foreign_account,foreign_org_id=data.foreign_org,invalid_question_id=data.invalid_question,
        questionnaire_id=data.questionnaire,questionnaire_version_id=data.version,child_id=data.child,assignment_id=data.assignment_id,
        question_ids=data.questions,eligibility_ref=data.ref,plan=plan,http_plan=cases(data,plan),cases=[],checks={},
        execution_results={},sources=INITIAL_SOURCES,applied_receipt=applied)
    before=table_counts(admin);original_rows=snapshot(admin,data.org)
    attempt['counts_before']=before
    STAGE='intent_journal'
    attempt['start_receipt']=str(fixture.receipt('edit-http-start',dict(attempt,succeeded=None)))
    STAGE='source_before_writes'
    require(source_hashes()==INITIAL_SOURCES,'source_changed_before_writes')
    STAGE='fresh_parent_seed'
    commit.seed(admin,data,assignment_id=data.assignment_id)
    STAGE='actual_create'
    engine=fixture.engine(value['urls']['runtime'])
    try:
        receipt=commit.execute(engine,data,json.dumps(plan['create']))
        attempt['execution_results']['create']=dict(receipt=receipt)
    finally:engine.dispose()
    require(receipt==expected_receipt(plan,'create'),'create_receipt_disagrees')
    STAGE='create_independent_storage'
    names=['create'];rows,proof=read_storage(value,data,plan,names)
    attempt['checks']['create']=proof;attempt['cases'].append('actual_create_independent_restricted_read')
    attempt['http']=asyncio.run(exercise(value,data,plan,attempt,rows,names))
    STAGE='preservation_checks'
    after=table_counts(admin);attempt['counts_after']=after
    verify_deltas(before,after);verify_preservation(original_rows,snapshot(admin,data.org));fixture.sentinel(admin)
    require(fixture.revision(value)==fixture.STORAGE,'ordinary_revision_changed')
    STAGE='source_postflight'
    require(source_hashes()==INITIAL_SOURCES,'source_changed_during_execution')
    result=dict(attempt,succeeded=True,qualified=True,native_edit_http=True,head=fixture.STORAGE,identities=identities,
        prior_rows=original_rows,prior_rows_unchanged=True,sentinel_unchanged=True,asgi_transport=True,
        real_access=False,real_identity_binding=False,real_http_listener=False,native_contention=False,native_cancellation=False)
    STAGE='success_receipt'
    destination=fixture.receipt('edit-http',result)
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
            report=str(fixture.receipt('edit-http',result))
        except Exception as receipt_error:
            report=None
            result['receipt_error_type']=type(receipt_error).__name__
        # Native exceptions and SQL parameters never enter diagnostic output.
        print(json.dumps(dict(succeeded=False,qualified=False,error_type=type(error).__name__,
            failed_stage=STAGE,report=report),sort_keys=True))
        return 1

if __name__=='__main__':raise SystemExit(main())
