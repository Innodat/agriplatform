"""Explicit retained-only stored-edit fixture qualification, never an edit API.

Creates one fresh synthetic capture with the actual create handler. Only its two
fixture edits use direct restricted-runtime SQL. No migration/preparer/cleanup.
"""
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
    *(APP/'migrations/tests'/name for name in ('qualify_edit_recovery_http.py',
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
    child_eligibility=1,capture=1,operation_outcome=3,capture_revision=3)


def new_plan():
    data=commit.Dataset()
    data.assignment_id=str(uuid4())
    create=json.loads(data.raw())
    plan=dict(create=create)
    for revision in (2,3):
        answers=dict(create['answers'])
        answers[data.questions[0]]=dict(value=revision)
        plan['edit'+str(revision)]=dict(operation_id=str(uuid4()),outcome_id=str(uuid4()),
            capture_id=create['capture_id'],revision=revision,
            observation_date='2026-10-'+str(23+revision),answers=answers)
    return data,plan


def snapshot(admin,excluded_org):
    """Known business tables only; never inspect schema/cluster/ledger inventory.

    Hash complete original row values privately, so equal counts cannot hide edits.
    """
    with fixture.native.connect(admin,readonly=True) as conn:
        result={}
        for table in DELTAS:
            rows=conn.execute('SELECT to_jsonb(t)::text FROM kdg_capture.'+table+
                ' t WHERE org_id<>%s::uuid ORDER BY to_jsonb(t)::text',(excluded_org,)).fetchall()
            result[table]=dict(count=len(rows),sha256=sha256(json.dumps(rows).encode()).hexdigest())
        return result


def table_counts(admin):
    with fixture.native.connect(admin,readonly=True) as conn:
        return {table:conn.execute('SELECT count(*) FROM kdg_capture.'+table).fetchone()[0] for table in DELTAS}


def verify_preservation(before,after):
    require(before==after,'prior_business_rows_changed')


def verify_deltas(before,after):
    require(set(before)==set(after)==set(DELTAS),'unexpected_count_tables')
    require(all(after[t]-before[t]==DELTAS[t] for t in DELTAS),'unexpected_dataset_delta')


def fixture_edit(engine,data,plan,edit):
    """TEST ONLY. Fixed fresh target, bounded transaction, no domain-authority claim."""
    require(edit is plan['edit2'] or edit is plan['edit3'],'unplanned_fixture_edit')
    require(edit['capture_id']==plan['create']['capture_id'],'fixture_target_changed')
    with engine.connect() as conn:
        require(conn.execute(text('SELECT current_user,session_user')).one()==
            ('kdg_capture_runtime','kdg_capture_runtime'),'restricted_runtime_required')
        conn.rollback()
        budget=write.Budget()
        context=write.VerifiedContext(data.org,data.account,data.actor,'own_write',time.monotonic())
        key=write.OutcomeKey('kdg_capture',data.org,data.account,'capture.edit',edit['operation_id'])
        with write.transaction(conn,budget,context):
            write.outcome_lock(conn,budget,key,context)
            params=dict(org=data.org,account=data.account,actor=data.actor,capture=edit['capture_id'],
                revision=edit['revision'],previous=edit['revision']-1,date=edit['observation_date'],
                answers=json.dumps(edit['answers']),operation=edit['operation_id'],outcome=edit['outcome_id'])
            result=write.execute(conn,budget,'''UPDATE kdg_capture.capture
SET observation_date=CAST(:date AS date),answers=CAST(:answers AS jsonb),revision=:revision
WHERE org_id=CAST(:org AS uuid) AND id=CAST(:capture AS uuid)
AND owner_account_id=CAST(:account AS uuid) AND revision=:previous''',params)
            require(result.rowcount==1,'fixture_revision_update_failed')
            receipt=outcomes.CaptureReceipt(operation_id=edit['operation_id'],command_type='capture.edit',
                command_version=1,status='committed',result=dict(capture_id=edit['capture_id'],revision=str(edit['revision'])))
            outcomes.append(conn,budget,key,context,outcome_id=edit['outcome_id'],receipt=receipt)
            sql=commit.create.HISTORY_INSERT.replace("'capture.create'","'capture.edit'")
            require(write.execute(conn,budget,sql,params).rowcount==1,'fixture_history_missing')


def write_dataset(value,data,plan,attempt):
    global STAGE
    engine=fixture.engine(value['urls']['runtime'])
    try:
        STAGE='runtime_create'
        receipt=commit.execute(engine,data,json.dumps(plan['create']))
        require(receipt==expected_receipt(plan,'create'),'create_receipt_disagreement')
        commit.read_triplet(engine,data,json.dumps(plan['create']))
        attempt['cases'].append('actual_create_commit_independent_triplet')

    finally:
        engine.dispose()


def expected_receipt(plan,name):
    command=plan[name]
    return dict(operation_id=command['operation_id'],command_type='capture.create' if name=='create' else 'capture.edit',
        command_version=1,status='committed',result=dict(capture_id=command['capture_id'],revision=str(command.get('revision',1))))


def read_storage(value,data,plan,revision):
    """New physical restricted read-only connection after writer disposal."""
    engine=fixture.engine(value['urls']['runtime']).execution_options(postgresql_readonly=True)
    try:
        with engine.connect() as conn:
            require(conn.execute(text('SELECT current_user,session_user,current_setting(\'transaction_read_only\')')).one()==
                ('kdg_capture_runtime','kdg_capture_runtime','on'),'independent_runtime_read_required')
            conn.rollback()
            budget=write.Budget()
            context=write.VerifiedContext(data.org,data.account,data.actor,'own_read',time.monotonic())
            with write.transaction(conn,budget,context):
                capture=conn.execute(text('SELECT to_jsonb(c) FROM kdg_capture.capture c')).scalar_one()
                history=conn.execute(text('SELECT to_jsonb(h) FROM kdg_capture.capture_revision h ORDER BY revision')).scalars().all()
                receipts=conn.execute(text('SELECT to_jsonb(o) FROM kdg_capture.operation_outcome o')).scalars().all()
                require(len(history)==revision and len(receipts)==revision,'linked_row_counts_disagree')
                require(capture['id']==plan['create']['capture_id'] and capture['revision']==revision,'current_capture_disagrees')
                common=dict(org_id=data.org,owner_account_id=data.account,owner_actor_id=data.actor,
                    child_id=data.child,questionnaire_id=data.questionnaire,questionnaire_version_id=data.version,
                    captured_at=plan['create']['captured_at'])
                require(all(capture[k]==v for k,v in common.items()),'immutable_capture_disagrees')
                require(capture['created_by']==capture['updated_by']==data.actor,'capture_actor_disagrees')
                require(capture['child_eligibility_ref']==plan['create']['child_eligibility_ref'] and
                    capture['creator_membership_id']==int(data.membership),'capture_eligibility_disagrees')
                created=datetime.fromisoformat(capture['created_at'])
                updated=datetime.fromisoformat(capture['updated_at'])
                require(created.utcoffset() is not None and updated.utcoffset() is not None and
                    updated>=created,'capture_timestamp_disagrees')
                for number,row in enumerate(history,1):
                    name='create' if number==1 else 'edit'+str(number)
                    command=plan[name];expected=expected_receipt(plan,name)
                    found=[o for o in receipts if o['operation_id']==command['operation_id']]
                    require(len(found)==1,'original_outcome_missing')
                    outcome=found[0]
                    if number>1:
                        require(row['outcome_id']==command['outcome_id'] and outcome['id']==command['outcome_id'],
                            'planned_outcome_id_disagrees')
                    require(all(row[k]==v for k,v in common.items()),'history_immutable_facts_disagree')
                    require(row['capture_id']==capture['id'] and row['revision']==number and
                        row['answers']==command['answers'] and row['observation_date']==command['observation_date'],
                        'history_snapshot_disagrees')
                    require(row['outcome_id']==outcome['id'] and row['operation_id']==command['operation_id'] and
                        row['command_type']==expected['command_type'],'history_operation_disagrees')
                    require(outcome['result']==expected['result'] and outcome['capture_id']==capture['id'] and
                        outcome['result_revision']==number and outcome['command_type']==expected['command_type'] and
                        outcome['command_version']==outcome['result_version']==1,'stored_receipt_disagrees')
                    require(all(record['executor_account_id']==data.account and record['executor_actor_id']==data.actor and
                        record['initiator_actor_id']==data.actor and record['org_id']==data.org for record in (row,outcome)),
                        'evidence_attribution_disagrees')
                current=plan['create' if revision==1 else 'edit'+str(revision)]
                require(capture['answers']==current['answers'] and capture['observation_date']==current['observation_date'],
                    'current_snapshot_disagrees')
                return dict(verified=True,current_revision=revision,original_edit=expected_receipt(plan,'edit2') if revision>1 else None,
                    history_sha256=sha256(json.dumps(history,sort_keys=True).encode()).hexdigest(),
                    immutable_revisions={str(row['revision']):sha256(json.dumps(row,sort_keys=True).encode()).hexdigest() for row in history},
                    immutable_outcomes={row['operation_id']:sha256(json.dumps(row,sort_keys=True).encode()).hexdigest() for row in receipts},
                    capture_created_at=capture['created_at'],capture_created_by=capture['created_by'],
                    capture_updated_at=capture['updated_at'])
    finally:
        engine.dispose()


def verify_original_evidence(before,after):
    for field in ('immutable_revisions','immutable_outcomes'):
        require(all(after[field].get(key)==value for key,value in before[field].items()),
            'original_evidence_changed_after_edit')
    require(before['capture_created_at']==after['capture_created_at'] and
        before['capture_created_by']==after['capture_created_by'],'capture_creation_changed')
    require(datetime.fromisoformat(after['capture_updated_at'])>datetime.fromisoformat(before['capture_updated_at']),
        'capture_update_time_not_advanced')


async def exercise(value,data,plan,revision):
    state=dict(account=data.account,denied=False,checkouts=0)
    cases=[]
    foreign=str(uuid4())
    async def run(org,*,foreign_org=False):
        async def access(request):
            require(json.loads(request.content)==dict(permission=boundary.recovery.PERMISSION,
                authorization_scope=dict(kind='organization',org_id=org)),'own_read_required')
            if state['denied']:return httpx.Response(403,json=dict(detail=dict(code='access_denied')))
            return httpx.Response(200,json=dict(account_id=state['account'],actor_id=data.actor,membership_id='1',
                decision_id=str(uuid4()),permission=boundary.recovery.PERMISSION,
                authorization_scope=dict(kind='organization',org_id=org),
                resource_scope=dict(kind='own_account',account_id=state['account']),
                checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')))
        app=boundary.create_candidate(org_id=org,access_url='https://access.invalid',service_key='synthetic-only',
            database_url=value['urls']['runtime'],transport=httpx.MockTransport(access))
        engine=app.state.recovery_engine
        physical=set();closed=set()
        def checkout(dbapi,record,proxy):
            with dbapi.cursor() as cursor:
                cursor.execute("SELECT current_user,session_user,current_setting('transaction_read_only'),current_setting('app.org_id',true),current_setting('app.account_id',true),current_setting('app.actor_id',true),current_setting('app.mode',true)")
                row=cursor.fetchone()
            dbapi.rollback()
            require(row[:3]==('kdg_capture_runtime','kdg_capture_runtime','on'),'runtime_read_only_required')
            require(all(v in (None,'') for v in row[3:]),'pooled_context_not_cleared')
            physical.add(dbapi.info.backend_pid);state['checkouts']+=1
        event.listen(engine,'checkout',checkout)
        event.listen(engine,'close',lambda dbapi,record:closed.add(dbapi.info.backend_pid))
        async with app.router.lifespan_context(app):
            with engine.connect():pass
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='https://kdg.invalid') as client:
                async def get(name='edit2',kind='capture.edit',status=200,expected=None):
                    operation=plan[name]['operation_id']
                    response=await client.get('/api/v1/operations/'+operation+'?command_type='+kind,
                        headers={'Authorization':'Bearer synthetic-account'})
                    prior.verify_response(response,status,expected or expected_receipt(plan,name))
                    require(engine.pool.checkedout()==0,'response_before_lease_release')
                unresolved=dict(operation_id=plan['edit2']['operation_id'],command_type='capture.edit',status='unresolved')
                if foreign_org:
                    await get(expected=unresolved);cases.append('foreign_organization_unresolved')
                else:
                    await get();cases.append('original_edit_receipt_and_release')
                    if revision==3:
                        await get('edit3');cases.append('latest_edit3_receipt_and_release')
                    await get('create','capture.create');cases.append('original_create_still_revision1')
                    await get(kind='capture.create',expected=dict(unresolved,command_type='capture.create'))
                    cases.append('wrong_discriminator_unresolved')
                    state['account']=foreign
                    await get(expected=unresolved);cases.append('foreign_account_unresolved')
                    state['account']=data.account
                    await get();cases.append('pooled_scope_cleared')
                    state['denied']=True;before=state['checkouts']
                    await get(status=403,expected=prior.envelope('access_denied'))
                    require(state['checkouts']==before,'denial_checked_out_connection')
                    state['denied']=False;cases.append('current_denial_before_checkout')
        require(physical==closed and engine.pool.checkedout()==0,'lifespan_connections_not_closed')
    await run(data.org)
    await run(foreign,foreign_org=True)
    return dict(cases=cases,leases_released=True,physical_connections_closed=True)


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
        questionnaire_id=data.questionnaire,questionnaire_version_id=data.version,child_id=data.child,
        assignment_id=data.assignment_id,question_ids=data.questions,eligibility_ref=data.ref,plan=plan,
        cases=[],sources=INITIAL_SOURCES,applied_receipt=applied)
    before=table_counts(admin)
    original_rows=snapshot(admin,data.org)
    STAGE='intent_journal'
    attempt['start_receipt']=str(fixture.receipt('edit-recovery-start',dict(attempt,succeeded=None,counts_before=before)))
    STAGE='fresh_parent_seed'
    commit.seed(admin,data,assignment_id=data.assignment_id)
    write_dataset(value,data,plan,attempt)
    STAGE='independent_revision1'
    attempt['revision1_storage']=read_storage(value,data,plan,1)
    STAGE='fixture_edit2'
    engine=fixture.engine(value['urls']['runtime'])
    try:fixture_edit(engine,data,plan,plan['edit2'])
    finally:engine.dispose()
    STAGE='independent_revision2'
    attempt['revision2_storage']=read_storage(value,data,plan,2)
    verify_original_evidence(attempt['revision1_storage'],attempt['revision2_storage'])
    attempt['revision2_http']=asyncio.run(exercise(value,data,plan,2))
    attempt['cases'].append('revision2_independent_storage_and_http')
    STAGE='fixture_edit3'
    engine=fixture.engine(value['urls']['runtime'])
    try:fixture_edit(engine,data,plan,plan['edit3'])
    finally:engine.dispose()
    STAGE='independent_revision3'
    attempt['revision3_storage']=read_storage(value,data,plan,3)
    verify_original_evidence(attempt['revision2_storage'],attempt['revision3_storage'])
    attempt['revision3_http']=asyncio.run(exercise(value,data,plan,3))
    attempt['cases'].append('original_edit_stable_after_revision3')
    STAGE='preservation_checks'
    after=table_counts(admin)
    verify_deltas(before,after)
    verify_preservation(original_rows,snapshot(admin,data.org))
    fixture.sentinel(admin)
    require(fixture.revision(value)==fixture.STORAGE,'ordinary_revision_changed')
    STAGE='source_postflight'
    require(source_hashes()==INITIAL_SOURCES,'source_changed_during_execution')
    result=dict(attempt,succeeded=True,qualified=True,native_edit_receipt=True,edit_api_qualified=False,
        head=fixture.STORAGE,identities=identities,counts_before=before,counts_after=after,
        prior_rows=original_rows,prior_rows_unchanged=True,sentinel_unchanged=True,
        asgi_transport=True,real_access=False,real_http_listener=False)
    STAGE='success_receipt'
    destination=fixture.receipt('edit-recovery-http',result)
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
            report=str(fixture.receipt('edit-recovery-http',result))
        except Exception as receipt_error:
            report=None
            result['receipt_error_type']=type(receipt_error).__name__
        # Native exceptions and SQL parameters never enter diagnostic output.
        print(json.dumps(dict(succeeded=False,qualified=False,error_type=type(error).__name__,
            failed_stage=STAGE,report=report),sort_keys=True))
        return 1

if __name__=='__main__':raise SystemExit(main())
