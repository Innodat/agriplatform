"""SELECT-only candidate qualification on the exact retained runtime database.

Access and ASGI requests are synthetic. No listener, migration, seed, DML,
provisioning, active API configuration or cleanup. Prior source receipts stay intact.
"""
import argparse
import asyncio
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
import threading
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[4]
SOURCES=(
    'apps/kdg-capture/write-candidate/operation_recovery.py',
    'apps/kdg-capture/write-candidate/capture_create_handler.py',
    'apps/kdg-capture/write-candidate/operation_outcomes.py',
    'apps/kdg-capture/write-tools/transaction_context.py',
    'apps/kdg-capture/api/context.py',
    'apps/kdg-capture/migrations/tests/qualify_operation_recovery.py',
    'apps/kdg-capture/migrations/tests/capture_commit_fixture.py',
    'apps/kdg-capture/migrations/tests/native_fixture.py',
    'apps/kdg-capture/write-candidate/recovery_http.py',
    'apps/kdg-capture/api/safe_errors.py',
    'apps/kdg-capture/migrations/tests/qualify_recovery_http.py',
)


def source_hashes():
    return {p:sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}


# Native CLI starts fresh: capture before importing the candidate or custody code.
INITIAL_SOURCES=source_hashes()
STAGE='imports'
import httpx
from sqlalchemy import event
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_operation_recovery as prior
fixture=prior.fixture
import recovery_http as boundary

require=prior.require


def verify_response(response,status,body):
    require(response.status_code==status,'unexpected_http_status')
    require(response.headers.get('cache-control')=='private, no-store','private_response_required')
    require(response.json()==body,'unexpected_http_body')


def envelope(identifier):
    return dict(error='The request could not be completed.',error_id=identifier)


async def exercise(value,data):
    state=dict(account=data['account_id'],denied=False,mode='normal',checks=0,checkouts=0)
    physical=set();closed=set();overlap_pids=set();lock=threading.Lock()
    cases=[]
    command=data['commands']['fresh']
    path='/api/v1/operations/'+command['operation_id']
    expected=dict(operation_id=command['operation_id'],command_type='capture.create',
        command_version=1,status='committed',result=dict(capture_id=command['capture_id'],revision='1'))
    async def access(request):
        require(json.loads(request.content)==dict(permission=boundary.recovery.PERMISSION,
            authorization_scope=dict(kind='organization',org_id=data['org_id'])), 'own_read_check_required')
        state['checks']+=1
        if state['denied']:
            return httpx.Response(403,json=dict(detail=dict(code='access_denied')))
        return httpx.Response(200,json=dict(account_id=state['account'],actor_id=data['actor_id'],
            membership_id='1',decision_id=str(uuid4()),permission=boundary.recovery.PERMISSION,
            authorization_scope=dict(kind='organization',org_id=data['org_id']),
            resource_scope=dict(kind='own_account',account_id=state['account']),
            checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')))
    app=boundary.create_candidate(org_id=data['org_id'],access_url='https://access.invalid',
        service_key='synthetic-service-key',database_url=value['urls']['runtime'],
        transport=httpx.MockTransport(access))
    engine=app.state.recovery_engine
    def checkout(dbapi,record,proxy):
        with dbapi.cursor() as cursor:
            cursor.execute("SELECT current_user,session_user,current_setting('transaction_read_only'),current_setting('app.org_id',true),current_setting('app.account_id',true),current_setting('app.actor_id',true),current_setting('app.mode',true),pg_backend_pid()")
            row=cursor.fetchone()
        dbapi.rollback()
        require(row[:3]==('kdg_capture_runtime','kdg_capture_runtime','on'),'runtime_read_only_required')
        require(all(item in (None,'') for item in row[3:7]),'pooled_context_not_cleared')
        with lock:
            physical.add(row[7]);state['checkouts']+=1
    def close(dbapi,record):
        closed.add(dbapi.info.backend_pid)
    barrier=threading.Barrier(2)
    def before_cursor(conn,cursor,statement,parameters,context,many):
        if 'FROM kdg_capture.operation_outcome' in statement and state['mode']=='overlap':
            with lock:overlap_pids.add(conn.connection.driver_connection.info.backend_pid)
            barrier.wait(2)
        if 'FROM kdg_capture.operation_outcome' in statement and state['mode']=='sql_failure':
            return 'SELECT 1/0', {}
        return statement,parameters
    event.listen(engine,'checkout',checkout)
    event.listen(engine,'close',close)
    event.listen(engine,'before_cursor_execute',before_cursor,retval=True)
    pool=engine.pool
    async with app.router.lifespan_context(app):
        # Real driver warm-up is explicit and read-only. Route freshness is unchanged.
        with engine.connect():pass
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='https://kdg.invalid') as client:
            async def get(url=path+'?command_type=capture.create'):
                return await client.get(url,headers={'Authorization':'Bearer synthetic-account'})
            checkout_before=state['checkouts']
            verify_response(await get(),200,expected)
            require(state['checkouts']==checkout_before+1,'one_request_lease_required')
            require(pool.checkedout()==0,'receipt_returned_before_release')
            cases.append('original_receipt_and_release')
            for name,url,account in (
                ('unknown_operation','/api/v1/operations/'+str(uuid4())+'?command_type=capture.create',data['account_id']),
                ('command_discriminator',path+'?command_type=capture.edit',data['account_id']),
                ('foreign_account',path+'?command_type=capture.create',str(uuid4()))):
                state['account']=account
                operation=url.split('/')[-1].split('?')[0]
                kind=url.split('command_type=')[1]
                verify_response(await get(url),200,dict(operation_id=operation,command_type=kind,status='unresolved'))
                require(pool.checkedout()==0,'scoped_read_lease_retained')
                cases.append(name)
            state['account']=data['account_id']
            verify_response(await get(),200,expected)
            cases.append('scope_cleared_on_reused_connection')
            before=(state['checks'],state['checkouts'])
            verify_response(await get(path+'?command_type=capture.create&command_type=capture.edit'),422,envelope('validation_failed'))
            verify_response(await get(path+'?command_type=capture.create&org_id=foreign'),422,envelope('validation_failed'))
            require(before==(state['checks'],state['checkouts']),'invalid_query_entered_dependencies')
            cases.append('closed_http_selectors')
            state['denied']=True;before=state['checkouts']
            verify_response(await get(),403,envelope('access_denied'))
            require(state['checkouts']==before,'denial_checked_out_connection')
            state['denied']=False
            cases.append('current_access_denial_before_checkout')
            held=[]
            try:
                for _ in range(5):held.append(engine.connect())
                started=time.monotonic()
                verify_response(await get(),503,envelope('operation_verification_unavailable'))
                require(.15<=time.monotonic()-started<3,'pool_timeout_not_bounded')
                require(pool.checkedout()==5,'saturation_changed_held_leases')
            finally:
                for conn in held:conn.close()
            require(pool.checkedout()==0,'held_lease_not_released')
            verify_response(await get(),200,expected)
            cases.append('actual_pool_saturation_failure_and_reuse')
            state['mode']='sql_failure'
            try:
                verify_response(await get(),503,envelope('operation_verification_unavailable'))
            finally:
                state['mode']='normal'
            require(pool.checkedout()==0,'failed_sql_lease_retained')
            verify_response(await get(),200,expected)
            cases.append('native_select_error_rollback_and_reuse')
            state['mode']='overlap'
            try:
                for result in await asyncio.gather(get(),get()):verify_response(result,200,expected)
            finally:
                state['mode']='normal'
            require(len(overlap_pids)==2 and pool.checkedout()==0,'overlapping_leases_not_exclusive')
            cases.append('overlapping_runtime_connections')
        require(pool.checkedout()==0,'lifespan_started_with_active_lease')
    require(physical<=closed,'lifespan_did_not_close_physical_connections')
    require(pool.checkedout()==0,'disposed_pool_still_borrowed')
    cases.append('actual_lifespan_disposal')
    # A separately configured organization, never a request-selected override.
    foreign=str(uuid4())
    async def foreign_access(request):
        require(json.loads(request.content)==dict(permission=boundary.recovery.PERMISSION,
            authorization_scope=dict(kind='organization',org_id=foreign)), 'foreign_org_check_required')
        return httpx.Response(200,json=dict(account_id=data['account_id'],actor_id=data['actor_id'],
            membership_id='1',decision_id=str(uuid4()),permission=boundary.recovery.PERMISSION,
            authorization_scope=dict(kind='organization',org_id=foreign),
            resource_scope=dict(kind='own_account',account_id=data['account_id']),
            checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')))
    other=boundary.create_candidate(org_id=foreign,access_url='https://access.invalid',
        service_key='synthetic-service-key',database_url=value['urls']['runtime'],
        transport=httpx.MockTransport(foreign_access))
    event.listen(other.state.recovery_engine,'checkout',checkout)
    event.listen(other.state.recovery_engine,'close',close)
    async with other.router.lifespan_context(other):
        with other.state.recovery_engine.connect():pass
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=other),base_url='https://kdg.invalid') as client:
            verify_response(await client.get(path+'?command_type=capture.create',headers={'Authorization':'Bearer synthetic-account'}),200,
                dict(operation_id=command['operation_id'],command_type='capture.create',status='unresolved'))
            require(other.state.recovery_engine.pool.checkedout()==0,'foreign_org_lease_retained')
    require(physical<=closed,'foreign_lifespan_did_not_close_connections')
    cases.append('foreign_organization')
    return dict(cases=cases,read_only=True,physical_connections=len(physical),
        physical_connections_closed=len(closed),overlap_connections=len(overlap_pids),native_edit_receipt=False,
        asgi_transport=True,real_http_listener=False,real_access=False)


def qualify():
    global STAGE
    STAGE='source_preflight'
    require(source_hashes()==INITIAL_SOURCES,'source_changed_before_execution')
    STAGE='fixture_preflight'
    require(__debug__,'optimized_python_prohibited')
    value,original,admin=fixture.retained()
    applied=fixture.migration_qualified(value)
    identities=fixture.identities(value)
    data=prior.retained_proof()
    before=prior.counts(admin)
    fixture.sentinel(admin)
    STAGE='native_exercise'
    result=asyncio.run(exercise(value,data))
    STAGE='preservation_checks'
    after=prior.counts(admin)
    require(before==after,'retained_rows_changed')
    fixture.sentinel(admin)
    require(fixture.revision(value)==fixture.STORAGE,'retained_revision_changed')
    result.update(succeeded=True,qualified=True,head=fixture.STORAGE,identities=identities,
        counts_before=before,counts_after=after,sentinel_unchanged=True,
        applied_receipt=applied,identifier_receipt=str(prior.PROOF),
        sources=INITIAL_SOURCES)
    STAGE='source_postflight'
    require(source_hashes()==INITIAL_SOURCES,'source_changed_during_execution')
    STAGE='success_receipt'
    destination=fixture.receipt('recovery-http',result)
    return dict(result,report=str(destination))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qualify-retained',required=True,action='store_true')
    parser.parse_args(argv)
    try:
        print(json.dumps(qualify(),sort_keys=True))
        return 0
    except Exception as error:
        result=dict(succeeded=False,error_type=type(error).__name__,failed_stage=STAGE,
            sources=INITIAL_SOURCES)
        report=fixture.receipt('recovery-http',result)
        print(json.dumps(dict(result,report=str(report))))
        return 1


if __name__=='__main__':
    raise SystemExit(main())
