"""Explicit retained-only native administrator history qualification.

Only Access is mocked. This module never starts the retained stack, prepares a
fixture, runs migrations, or changes privileges. Failures retain their observations.
"""
import argparse
import asyncio
from contextlib import AsyncExitStack, contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[4]
APP=ROOT/'apps/kdg-capture'
# Explicit sources, including the helpers' own import-time source bindings. No
# migration discovery and, in particular, no schema_fixture.py access.
CANDIDATE_SOURCES='''own_observation_openapi edit_context_openapi provision_openapi
admin_edit_http create_openapi audit_read operation_recovery audit_openapi
operation_outcomes recovery_http audit_http recovery_openapi edit_http capture_create
history_openapi provision_http admin_edit admin_read admin_edit_context edit_context_http
capture_edit capture_read read_http edit_openapi history_http admin_edit_context_http
provision create_http admin_edit_context_openapi admin_edit_openapi admin_openapi
capture_create_handler read_openapi capture_history edit_context capture_edit_handler admin_http
export_admin_edit_context_openapi export_provision_openapi export_edit_openapi
export_read_openapi export_recovery_openapi export_admin_openapi export_edit_context_openapi
export_audit_openapi export_history_openapi export_admin_edit_openapi export_create_openapi'''.split()
API_SOURCES='context capture_commands questionnaire safe_errors main runtime export_openapi'.split()
HELPER_SOURCES='''qualify_admin_history qualify_admin_api qualify_capture_commit qualify_capture_storage
capture_commit_fixture native_fixture qualify_own_edit qualify_edit_recovery_http
qualify_recovery_http qualify_operation_recovery'''.split()

def source_paths():
    return tuple(sorted(
        ['apps/kdg-capture/write-candidate/'+name+'.py' for name in CANDIDATE_SOURCES]+
        ['apps/kdg-capture/api/'+name+'.py' for name in API_SOURCES]+
        ['apps/kdg-capture/migrations/tests/'+name+'.py' for name in HELPER_SOURCES]+[
        'apps/kdg-capture/write-tools/transaction_context.py',
        'apps/kdg-capture/migrations/candidates/0002_capture_storage.py',
        'platform/deployment/dev.py','platform/deployment/native_cli.py',
        'platform/deployment/environments/kdg-local.json']))

def source_hashes():
    return {path:sha256((ROOT/path).read_bytes()).hexdigest() for path in source_paths()}

INITIAL_SOURCES={}
BOOTSTRAP_ERROR=None
STAGE='source_bootstrap'
fixture=None
sys.path.insert(0,str(Path(__file__).resolve().parent))
try:
    INITIAL_SOURCES=source_hashes()
    STAGE='imports'
    import qualify_admin_api as base
    import history_http
    import httpx
    from sqlalchemy import event, text
    commit,fixture,write,preserved=base.commit,base.fixture,base.write,base.preserved
    outcomes=commit.create.outcomes
except Exception as error:
    BOOTSTRAP_ERROR=error
    if INITIAL_SOURCES and set(INITIAL_SOURCES)==set(source_paths()):
        try:import capture_commit_fixture as fixture
        except Exception:fixture=None


def require(condition,identifier):
    if not condition:raise AssertionError(identifier)


def eligible(rows,start,end,account=None):
    """Independent complete-row oracle; never use candidate projection or cursor."""
    return sorted([row for row in rows if start<=row['observation_date']<=end and
        (account is None or row['owner_account_id']==account)],
        key=lambda row:(datetime.fromisoformat(row['created_at']),row['capture_id']),reverse=True)


def new_plan():
    owners=[commit.Dataset() for _ in range(3)]
    owners[1].org=owners[0].org
    for owner in owners:owner.assignment_id=str(uuid4())
    admin=dict(account=str(uuid4()),actor=str(uuid4()))
    plan=[]
    for index,owner in enumerate(owners):
        entries=[]
        for day in ('2026-10-22','2026-10-23','2026-10-24','2026-10-25','2026-10-26'):
            command=json.loads(owner.raw(observation_date=day))
            entries.append(dict(command=command,outcome_id=str(uuid4())))
        plan.append(dict(owner=vars(owner).copy(),entries=entries))
    return owners,admin,plan


def multirow_insert(entries):
    statement=commit.create.CAPTURE_INSERT
    head,values=statement.split('VALUES',1)
    import re
    return head+'VALUES'+','.join(re.sub(r':([a-z_]+)',lambda match:':'+match[1]+'_'+str(i),values)
        for i in range(len(entries)))


def seed_captures(value,owner,entries):
    """One restricted multi-row statement creates a genuine timestamp tie."""
    from datetime import date
    engine=fixture.engine(value['urls']['runtime'])
    try:
        with engine.connect() as conn:
            require(tuple(conn.execute(text("SELECT current_user,session_user,current_setting('transaction_read_only')")).one())==
                ('kdg_capture_runtime','kdg_capture_runtime','off'),'seed_runtime_identity_disagrees')
            conn.rollback()
            budget=write.Budget()
            context=write.VerifiedContext(owner.org,owner.account,owner.actor,'own_write',time.monotonic())
            with write.transaction(conn,budget,context):
                parameters={}
                for i,entry in enumerate(entries):
                    command=entry['command']
                    p=dict(capture=command['capture_id'],org=owner.org,child=owner.child,
                        questionnaire=owner.questionnaire,version=owner.version,account=owner.account,actor=owner.actor,
                        ref=owner.ref,member=int(owner.membership),date=date.fromisoformat(command['observation_date']),
                        answers=json.dumps(command['answers']),device=command['captured_at'])
                    parameters.update({key+'_'+str(i):v for key,v in p.items()})
                require(write.execute(conn,budget,multirow_insert(entries),parameters).rowcount==len(entries),'multirow_seed_count_disagrees')
                for entry in entries:
                    command=entry['command'];capture=command['capture_id'];operation=command['operation_id']
                    receipt=outcomes.CaptureReceipt(operation_id=operation,command_type='capture.create',command_version=1,
                        status='committed',result=dict(capture_id=capture,revision='1'))
                    key=write.OutcomeKey('kdg_capture',owner.org,owner.account,'capture.create',operation)
                    outcomes.append(conn,budget,key,context,outcome_id=entry['outcome_id'],receipt=receipt)
                    require(write.execute(conn,budget,commit.create.HISTORY_INSERT,dict(org=owner.org,account=owner.account,
                        actor=owner.actor,capture=capture,operation=operation,outcome=entry['outcome_id'])).rowcount==1,'history_seed_count_disagrees')
    finally:engine.dispose()


def snapshot(admin,excluded=()):
    """Complete business rows, known tables only; explicit new organizations only."""
    with fixture.native.connect(admin,readonly=True) as conn:
        return {table:conn.execute('SELECT to_jsonb(t) FROM kdg_capture.'+table+
            ' t WHERE NOT (org_id=ANY(%s::uuid[])) ORDER BY to_jsonb(t)::text',(list(excluded),)).fetchall()
            for table in preserved.DELTAS}


def independent_rows(value,owner,admin):
    """New physical restricted read-only sessions for DTOs and private seed links."""
    engine=fixture.engine(value['urls']['runtime']).execution_options(postgresql_readonly=True)
    try:
        with engine.connect() as conn:
            require(tuple(conn.execute(text("SELECT current_user,session_user,current_setting('transaction_read_only')")).one())==
                ('kdg_capture_runtime','kdg_capture_runtime','on'),'independent_runtime_read_required')
            conn.rollback();budget=write.Budget()
            context=write.VerifiedContext(owner.org,owner.account,owner.actor,'all_read',time.monotonic())
            with write.transaction(conn,budget,context):
                rows={table:conn.execute(text('SELECT to_jsonb(t) FROM kdg_capture.'+table+' t')).scalars().all()
                    for table in ('capture','capture_revision','operation_outcome','child','questionnaire_version')}
    finally:engine.dispose()
    return rows


def verify_seed(owners,plan,observed):
    result={}
    for owner,group,rows in zip(owners,plan,observed):
        versions=[r for r in rows['questionnaire_version'] if r['id']==owner.version]
        require(len(versions)==1 and versions[0]['questionnaire_id']==owner.questionnaire and
            versions[0]['display_version']==1 and versions[0]['definition']==
            commit.initial_definition(owner.questions).model_dump(mode='json'),'seed_original_definition_disagrees')
        captures=[r for r in rows['capture'] if r['owner_account_id']==owner.account]
        require({r['id'] for r in captures}=={e['command']['capture_id'] for e in group['entries']},'seed_capture_identity_disagrees')
        require(len({r['created_at'] for r in captures})==1,'genuine_creation_tie_missing')
        for entry in group['entries']:
            command=entry['command'];capture=next(r for r in captures if r['id']==command['capture_id'])
            common=dict(org_id=owner.org,owner_account_id=owner.account,owner_actor_id=owner.actor,
                child_id=owner.child,questionnaire_id=owner.questionnaire,questionnaire_version_id=owner.version,
                answers=command['answers'],observation_date=command['observation_date'],captured_at=command['captured_at'],revision=1)
            require(all(capture[k]==v for k,v in common.items()) and capture['created_by']==capture['updated_by']==owner.actor and
                capture['creator_membership_id']==1 and capture['child_eligibility_ref']==owner.ref,'seed_capture_facts_disagree')
            histories=[r for r in rows['capture_revision'] if r['capture_id']==capture['id']]
            receipts=[r for r in rows['operation_outcome'] if r['id']==entry['outcome_id']]
            require(len(histories)==len(receipts)==1,'seed_link_missing')
            h,o=histories[0],receipts[0]
            require(all(h[k]==v for k,v in common.items()) and h['outcome_id']==o['id'] and
                h['operation_id']==o['operation_id']==command['operation_id'] and
                h['executor_account_id']==o['executor_account_id']==owner.account and
                h['executor_actor_id']==h['initiator_actor_id']==o['executor_actor_id']==o['initiator_actor_id']==owner.actor and
                h['command_type']==o['command_type']=='capture.create' and o['command_version']==o['result_version']==1 and
                o['capture_id']==capture['id'] and o['result_revision']==1 and
                o['result']==dict(capture_id=capture['id'],revision='1'),'seed_history_receipt_disagrees')
        # DTO projection from complete SQL rows, independent of candidate helpers.
        details=[]
        for c in rows['capture']:
            child=next(r for r in rows['child'] if r['id']==c['child_id'])
            version=next(r for r in rows['questionnaire_version'] if r['id']==c['questionnaire_version_id'])
            dto={k:c[k] for k in ('org_id owner_account_id owner_actor_id child_id questionnaire_id questionnaire_version_id observation_date answers captured_at created_by updated_by').split()}
            dto.update(capture_id=c['id'],child_label=child['display_name'],questionnaire_version=str(version['display_version']),
                definition=version['definition'],revision=str(c['revision']))
            for key in ('created_at','updated_at'):dto[key]=datetime.fromisoformat(c[key]).astimezone(timezone.utc).isoformat().replace('+00:00','Z')
            details.append(dto)
        details=sorted(details,key=lambda row:row['capture_id'])
        if owner.org in result:
            require(result[owner.org]==details,'same_org_observations_disagree')
        else:result[owner.org]=details
    return result


def verify_page(body,expected,org,account,start,end,limit,own=False):
    keys=set('org_id account_id from_date to_date limit items next_cursor'.split())
    if own:keys.add('observation')
    require(type(body) is dict and set(body)==keys,'closed_page_disagrees')
    require(type(body['limit']) is int and all(body[k]==v for k,v in dict(org_id=org,account_id=account,
        from_date=start,to_date=end,limit=limit).items()),'page_header_disagrees')
    require(body['items']==expected,'independent_dto_page_disagrees')

async def exercise(value,owners,admin,oracle,attempt,inspect):
    from urllib.parse import urlencode
    state=dict(org=owners[0].org,account=admin['account'],actor=admin['actor'],denied=False,malformed=False)
    engines=[];checks=[];checkouts=[];physical=set();closed=set()
    async def access(request):
        permission=json.loads(request.content)['permission'];checks.append(permission)
        require(all(e.pool.checkedout()==0 for e in engines),'access_under_database_lease')
        if state['denied']:return httpx.Response(403,json=dict(detail=dict(code='access_denied')))
        evidence=dict(account_id=state['account'],actor_id=state['actor'],membership_id='1',decision_id=str(uuid4()),
            permission=permission,authorization_scope=dict(kind='organization',org_id=state['org']),
            resource_scope=dict(kind='organization',org_id=state['org']) if permission==base.READ else dict(kind='own_account',account_id=state['account']),
            checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
        if state['malformed']:evidence['resource_scope']=dict(kind='own_account',account_id=state['account'])
        return httpx.Response(200,json=evidence)
    def monitor(engine):
        engines.append(engine)
        def checkout(dbapi,record,proxy):
            with dbapi.cursor() as cursor:
                cursor.execute("SELECT current_user,session_user,current_setting('transaction_read_only'),current_setting('app.org_id',true),current_setting('app.account_id',true),current_setting('app.actor_id',true),current_setting('app.mode',true)")
                row=cursor.fetchone()
            dbapi.rollback()
            require(row[:3]==('kdg_capture_runtime','kdg_capture_runtime','on'),'candidate_runtime_identity_disagrees')
            require(all(v in (None,'') for v in row[3:]),'pooled_context_not_cleared')
            physical.add(dbapi.info.backend_pid);checkouts.append(dbapi.info.backend_pid)
        event.listen(engine,'checkout',checkout)
        event.listen(engine,'close',lambda dbapi,record:closed.add(dbapi.info.backend_pid))
    async with AsyncExitStack() as stack:
        clients={}
        for name,module,org in [('all',base.admin_http,owners[0].org),('own',history_http,owners[0].org),('foreign',base.admin_http,owners[2].org)]:
            app=module.create_candidate(org_id=org,access_url='https://access.invalid',service_key='synthetic-only',
                database_url=value['urls']['runtime'],transport=httpx.MockTransport(access))
            monitor(app.state.recovery_engine)
            await stack.enter_async_context(app.router.lifespan_context(app))
            clients[name]=await stack.enter_async_context(httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='https://kdg.invalid'))
        async def request(label,query,expected=None,status=200,client='all',permissions=None,checkout_count=1,validate=None):
            global STAGE
            STAGE=label;before=len(checkouts);start=len(checks)
            route='/api/v1/'+('admin/' if client!='own' else '')+'captures?'
            try:
                response=await clients[client].get(route+(query if isinstance(query,str) else urlencode(query)),headers=base.HEADERS)
                observed=base.observe_response(response,engines)
                observed.update(access_permissions=checks[start:],checkouts=len(checkouts)-before)
                attempt['execution_results'][label]=observed
                require(observed['access_permissions']==(permissions if permissions is not None else [base.READ]),'authority_sequence_disagrees')
                require(observed['checkouts']==checkout_count,'checkout_count_disagrees')
                require(observed['leases_released'],'response_before_lease_release')
                require(response.headers.get('cache-control')=='private, no-store','private_no_store_required')
                require(response.status_code==status,'response_status_disagrees')
                body=response.json()
                if expected is not None:require(body==expected,'response_contract_disagrees')
                if validate is not None:validate(body)
                attempt['cases'].append(label)
                return body
            finally:
                original_error=sys.exception()
                preservation=attempt['execution_results'].setdefault(label,{})
                try:inspect()
                except Exception as error:
                    preservation['preservation']=dict(passed=False,error_type=type(error).__name__)
                    if original_error is None:raise
                else:preservation['preservation']=dict(passed=True)
        async def pages(label,start,end,limit,client='all',account=None,omit_limit=False):
            expected=eligible(oracle[state['org']],start,end,account);seen=[];cursor=None;first=None
            for index in range(len(expected)+1):
                query=dict(from_date=start,to_date=end)
                if not omit_limit:query['limit']=limit
                if cursor:query['cursor']=cursor
                part=expected[len(seen):len(seen)+limit]
                body=await request(label+'_'+str(index),query,client=client,
                    permissions=[base.READ if client!='own' else 'kdg_capture.capture.read.own'],
                    validate=lambda body:verify_page(body,part,state['org'],state['account'],start,end,limit,client=='own'))
                seen.extend(body['items']);cursor=body['next_cursor']
                if len(seen)<len(expected):require(type(cursor) is str and bool(cursor),'continuation_missing')
                else:require(cursor is None,'final_cursor_not_null')
                if first is None:first=cursor
                if cursor is None:break
            require(seen==expected and len({r['capture_id'] for r in seen})==len(seen),'pagination_omission_or_duplicate')
            return first
        cursor=await pages('ties','2026-10-23','2026-10-25',1)
        for label,start,end,limit in [('full','2026-10-23','2026-10-25',100),('default','2026-10-23','2026-10-25',30),
            ('empty','2026-10-01','2026-10-02',30),('single_date','2026-10-24','2026-10-24',1)]:
            await pages(label,start,end,limit,omit_limit=label=='default')
        query=dict(from_date='2026-10-23',to_date='2026-10-25',limit=1,cursor=cursor)
        error=base.envelope('validation_failed')
        state['account'],state['actor']=owners[0].account,owners[0].actor
        await request('another_account_cursor',query,error,422,checkout_count=0)
        state['account'],state['actor']=admin['account'],admin['actor']
        state['org']=owners[2].org
        await request('another_org_cursor',query,error,422,client='foreign',checkout_count=0)
        await pages('foreign_own_org','2026-10-23','2026-10-25',1,client='foreign')
        state['org']=owners[0].org
        for key,v in [('from_date','2026-10-24'),('to_date','2026-10-26'),('limit',2)]:
            await request('changed_'+key,dict(query,**{key:v}),error,422,checkout_count=0)
        await request('all_cursor_in_own',query,error,422,client='own',permissions=[],checkout_count=0)
        state['account'],state['actor']=owners[0].account,owners[0].actor
        own_cursor=await pages('own_ties','2026-10-23','2026-10-25',1,client='own',account=owners[0].account)
        await request('own_cursor_in_all',dict(query,cursor=own_cursor),error,422,permissions=[],checkout_count=0)
        state['account'],state['actor']=admin['account'],admin['actor']
        state['denied']=True
        await request('role_lost_between_pages',query,base.envelope('access_denied'),403,checkout_count=0)
        state['denied']=False;state['malformed']=True
        await request('malformed_scope',query,base.envelope('authorization_unavailable'),503,checkout_count=0)
        state['malformed']=False
        for label,raw in [('malformed_cursor',dict(query,cursor='!')),('invalid_limit',dict(query,limit=101)),
            ('reversed_dates',dict(query,from_date='2026-10-26')),('unknown_query','from_date=2026-10-23&to_date=2026-10-25&secret=1'),
            ('duplicate_query','from_date=2026-10-23&from_date=2026-10-23&to_date=2026-10-25')]:
            await request(label,raw,error,422,permissions=[],checkout_count=0)
    require(physical==closed and all(e.pool.checkedout()==0 for e in engines),'physical_connections_not_closed')
    return dict(leases_released=True,physical_connections_closed=True,physical_connections=len(physical))


def qualify(attempt):
    global STAGE
    STAGE='source_preflight';require(source_hashes()==INITIAL_SOURCES,'source_changed_before_execution')
    require(__debug__,'optimized_python_prohibited')
    STAGE='fixture_preflight'
    value,original,admin=fixture.retained()
    applied=fixture.migration_qualified(value);identities=fixture.identities(value);fixture.sentinel(admin)
    owners,administrator,plan=new_plan();orgs=sorted({o.org for o in owners})
    attempt.update(attempt_id=str(uuid4()),plan=plan,administrator=administrator,org_ids=orgs,
        cases=[],execution_results={},sources=INITIAL_SOURCES,applied_receipt=applied)
    prior=snapshot(admin,orgs);before=preserved.table_counts(admin)
    attempt.update(prior_rows=prior,counts_before=before)
    STAGE='intent_journal'
    attempt['start_receipt']=str(fixture.receipt('admin-history-start',dict(attempt,succeeded=None,qualified=False)))
    STAGE='source_before_writes';require(source_hashes()==INITIAL_SOURCES,'source_changed_before_writes')
    for index,(owner,group) in enumerate(zip(owners,plan)):
        STAGE='parent_seed_'+str(index);commit.seed(admin,owner,assignment_id=owner.assignment_id)
        STAGE='capture_seed_'+str(index);seed_captures(value,owner,group['entries'])
        attempt.setdefault('seed_completed',[]).append(index)
    STAGE='independent_seed_oracle'
    observed=attempt['seed_observations']=[]
    for owner in owners:observed.append(independent_rows(value,owner,administrator))
    oracle=verify_seed(owners,plan,observed)
    complete=snapshot(admin);counts=preserved.table_counts(admin)
    expected={t:before[t]+(15 if t in ('capture','capture_revision','operation_outcome') else 3) for t in before}
    require(counts==expected,'seed_count_deltas_disagree')
    require(snapshot(admin,orgs)==prior,'prior_business_rows_changed')
    attempt.update(seeded_rows=complete,counts_after_seed=counts)
    def inspect():
        require(snapshot(admin)==complete and preserved.table_counts(admin)==counts,'read_changed_business_rows')
    attempt['http']=asyncio.run(exercise(value,owners,administrator,oracle,attempt,inspect))
    STAGE='preservation_checks';inspect()
    require(snapshot(admin,orgs)==prior,'prior_business_rows_changed')
    fixture.sentinel(admin);require(fixture.revision(value)==fixture.STORAGE,'ordinary_revision_changed')
    STAGE='source_postflight';require(source_hashes()==INITIAL_SOURCES,'source_changed_during_execution')
    result=dict(attempt,succeeded=True,qualified=True,native_admin_history=True,head=fixture.STORAGE,identities=identities,
        prior_rows_unchanged=True,reads_unchanged=True,sentinel_unchanged=True,asgi_transport=True,
        real_access=False,real_identity_binding=False,real_http_listener=False,native_contention=False,native_cancellation=False)
    STAGE='success_receipt';destination=fixture.receipt('admin-history',result)
    return dict(result,report=str(destination))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qualify-retained',required=True,action='store_true');parser.parse_args(argv)
    attempt={}
    try:
        if BOOTSTRAP_ERROR is not None:raise BOOTSTRAP_ERROR
        result=qualify(attempt)
        print(json.dumps(dict(succeeded=True,qualified=True,report=result['report'],cases=result['cases']),sort_keys=True));return 0
    except Exception as error:
        result=dict(attempt,succeeded=False,qualified=False,error_type=type(error).__name__,failed_stage=STAGE,sources=INITIAL_SOURCES)
        try:report=str(fixture.receipt('admin-history',result)) if fixture is not None else None
        except Exception as receipt_error:
            report=None;result['receipt_error_type']=type(receipt_error).__name__
        output=dict(succeeded=False,qualified=False,error_type=type(error).__name__,failed_stage=STAGE,report=report)
        if 'receipt_error_type' in result:output['receipt_error_type']=result['receipt_error_type']
        print(json.dumps(output,sort_keys=True));return 1

if __name__=='__main__':raise SystemExit(main())
