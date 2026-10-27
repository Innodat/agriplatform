"""Explicit retained-only native administrator Save/read/recovery qualification.

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
HELPER_SOURCES='''qualify_admin_api qualify_capture_commit qualify_capture_storage
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
    import qualify_capture_commit as commit
    import qualify_own_edit as own
    import qualify_edit_recovery_http as preserved
    import admin_http
    import admin_edit_context_http
    import audit_http
    import admin_edit_http
    import edit_http
    import admin_edit
    import capture_edit
    import httpx
    from sqlalchemy import event, text
    from unittest.mock import patch
    fixture=commit.fixture
    write=commit.write
    outcomes=commit.create.outcomes
except Exception as error:
    BOOTSTRAP_ERROR=error
    try:
        import capture_commit_fixture as fixture
    except Exception:
        fixture=None


def require(condition,identifier):
    if not condition:raise AssertionError(identifier)


def clone(value):return json.loads(json.dumps(value))


def new_plan():
    data=commit.Dataset()
    data.assignment_id,data.admin_account,data.admin_actor,data.foreign_account,data.foreign_actor,data.foreign_org=[str(uuid4()) for _ in range(6)]
    plan={}
    for target in ('a','b'):
        command=json.loads(data.raw())
        plan['create_'+target]=dict(command=command,capture_id=command['capture_id'],executor='owner',revision=1,changed=True)
    def edit(name,target,executor,previous,value,changed=True):
        create=plan['create_'+target]
        answers=clone(create['command']['answers']);answers[data.questions[0]]={'value':value}
        plan[name]=dict(command=dict(operation_id=str(uuid4()),command_version=1,expected_revision=str(previous),
            observation_date='2026-10-24',answers=answers),capture_id=create['capture_id'],executor=executor,
            revision=previous+int(changed),changed=changed)
    edit('admin_a','a','admin',1,2)
    edit('owner_a_stale','a','owner',1,3)
    edit('owner_a','a','owner',2,3)
    edit('admin_a_stale','a','admin',2,4)
    edit('admin_a2','a','admin',3,4)
    edit('noop','a','admin',4,4,False)
    edit('owner_b','b','owner',1,2)
    edit('admin_b_stale','b','admin',1,3)
    edit('admin_b','b','admin',2,3)
    edit('owner_b_stale','b','owner',2,4)
    edit('owner_b2','b','owner',3,4)
    edit('retry','a','admin',4,5)
    edit('denied','a','admin',5,5)
    repeated=clone(plan['admin_a2']['command']);repeated['operation_id']=plan['denied']['command']['operation_id']
    replay=clone(plan['admin_a']['command']);replay.update(expected_revision='1',answers={})
    data.request_inputs=dict(repeated_review=dict(body=repeated,capture_id=plan['denied']['capture_id']),
        changed_path_body_replay=dict(body=replay,capture_id=plan['create_b']['capture_id']),
        malformed_body=dict(body={'operation_id':plan['denied']['command']['operation_id']},capture_id=plan['denied']['capture_id']),
        foreign_target=dict(body=plan['denied']['command'],capture_id=data.foreign_account))
    return data,plan


def executor(data,entry):
    return (data.account,data.actor) if entry['executor']=='owner' else (data.admin_account,data.admin_actor)


def expected_receipt(plan,name):
    entry=plan[name]
    return dict(operation_id=entry['command']['operation_id'],command_type='capture.create' if name.startswith('create_') else 'capture.edit',
        command_version=1,status='committed',result=dict(capture_id=entry['capture_id'],revision=str(entry['revision'])))


def verify_rows(data,plan,names,rows):
    """Cross-account oracle: discover outcome IDs, independently link both targets.

    Capture/history are all-read; each outcome list is acquired in its executor's
    separate physical session. A foreign executor's visible row is a failure.
    """
    require(set(rows)=={'capture','capture_revision','operation_outcome'},'oracle_tables_disagree')
    captures,history,receipts=[rows[t] for t in ('capture','capture_revision','operation_outcome')]
    changed=[name for name in names if plan[name]['changed']]
    targets={plan[name]['capture_id'] for name in names}
    require(len(captures)==len(targets) and len(history)==len(changed) and len(receipts)==len(names),'dataset_row_counts_disagree')
    common=dict(org_id=data.org,owner_account_id=data.account,owner_actor_id=data.actor,
        child_id=data.child,questionnaire_id=data.questionnaire,questionnaire_version_id=data.version)
    discovered={}
    revisions={}
    for capture in captures:
        selected=[name for name in changed if plan[name]['capture_id']==capture['id']]
        require(bool(selected),'unexpected_capture')
        first,last=plan[selected[0]],plan[selected[-1]]
        require(all(capture[key]==value for key,value in common.items()),'immutable_capture_disagrees')
        require(capture['captured_at']==first['command']['captured_at'] and
            capture['created_by']==data.actor and capture['updated_by']==executor(data,last)[1] and
            capture['child_eligibility_ref']==data.ref and capture['creator_membership_id']==int(data.membership),
            'capture_provenance_disagrees')
        require(capture['revision']==len(selected)==last['revision'] and
            capture['answers']==last['command']['answers'] and capture['observation_date']==last['command']['observation_date'],
            'current_capture_disagrees')
        created,updated=[datetime.fromisoformat(capture[field]) for field in ('created_at','updated_at')]
        require(created.utcoffset() is not None and updated.utcoffset() is not None and updated>=created,'capture_timestamp_disagrees')
        revisions[capture['id']]=capture['revision']
    for name in names:
        entry=plan[name];command=entry['command'];expected=expected_receipt(plan,name)
        account,actor=executor(data,entry)
        found=[row for row in receipts if row['operation_id']==command['operation_id']]
        require(len(found)==1,'original_receipt_missing')
        outcome=found[0];discovered[name]=outcome['id']
        require(outcome['org_id']==data.org and outcome['executor_account_id']==account and
            outcome['executor_actor_id']==outcome['initiator_actor_id']==actor,'outcome_attribution_disagrees')
        require(outcome['result']==expected['result'] and outcome['capture_id']==entry['capture_id'] and
            outcome['result_revision']==entry['revision'] and outcome['command_version']==outcome['result_version']==1 and
            outcome['command_type']==expected['command_type'],'stored_receipt_disagrees')
        linked=[row for row in history if row['outcome_id']==outcome['id']]
        if not entry['changed']:
            require(not linked,'noop_inserted_history');continue
        require(len(linked)==1,'history_link_disagrees')
        row=linked[0]
        require(all(row[key]==value for key,value in common.items()),'immutable_history_disagrees')
        initial=next(plan[item] for item in names if plan[item]['capture_id']==entry['capture_id'])
        require(row['captured_at']==initial['command']['captured_at'] and row['capture_id']==entry['capture_id'] and
            row['revision']==entry['revision'] and row['operation_id']==command['operation_id'] and
            row['command_type']==expected['command_type'] and row['answers']==command['answers'] and
            row['observation_date']==command['observation_date'],'history_snapshot_disagrees')
        require(row['executor_account_id']==account and row['executor_actor_id']==row['initiator_actor_id']==actor,
            'history_attribution_disagrees')
    require(len(set(discovered.values()))==len(names),'outcome_identity_reused')
    return dict(verified=True,current_revisions=revisions,discovered_outcomes=discovered)


def read_storage(value,data,plan,names):
    """New NullPool physical read-only session for all-read and each executor."""
    rows={table:[] for table in ('capture','capture_revision','operation_outcome')}
    for account,actor,tables in (
        (data.admin_account,data.admin_actor,('capture','capture_revision')),
        (data.account,data.actor,('operation_outcome',)),
        (data.admin_account,data.admin_actor,('operation_outcome',))):
        engine=fixture.engine(value['urls']['runtime']).execution_options(postgresql_readonly=True)
        try:
            with engine.connect() as conn:
                require(tuple(conn.execute(text("SELECT current_user,session_user,current_setting('transaction_read_only')")).one())==
                    ('kdg_capture_runtime','kdg_capture_runtime','on'),'independent_runtime_read_required')
                conn.rollback()
                budget=write.Budget()
                context=write.VerifiedContext(data.org,account,actor,'all_read',time.monotonic())
                with write.transaction(conn,budget,context):
                    for table in tables:
                        found=conn.execute(text('SELECT to_jsonb(t) FROM kdg_capture.'+table+' t ORDER BY to_jsonb(t)::text')).scalars().all()
                        if table=='operation_outcome':
                            require(all(row['executor_account_id']==account for row in found),'private_outcome_visibility_failed')
                        rows[table].extend(found)
        finally:engine.dispose()
    return rows,verify_rows(data,plan,names,rows)


def verify_transition(before,after,*,unchanged=False,noop=False):
    if unchanged:
        require(before==after,'refused_command_changed_storage');return
    for table in ('capture_revision','operation_outcome'):
        require(all(row in after[table] for row in before[table]),'original_evidence_changed')
    old={row['id']:row for row in before['capture']};new={row['id']:row for row in after['capture']}
    require(set(old)<=set(new),'original_capture_removed')
    for identifier,row in old.items():
        # Reuse the existing full-row transition guard, one target at a time.
        def target_rows(source,capture):
            return dict(capture=[capture],**{table:[item for item in source[table] if item['capture_id']==identifier]
                for table in ('capture_revision','operation_outcome')})
        own.verify_transition(target_rows(before,row),target_rows(after,new[identifier]),
            unchanged=False,noop=noop or row==new[identifier])


DELTAS=dict(questionnaire=1,questionnaire_version=1,child=1,child_assignment=1,
    child_eligibility=1,capture=2,operation_outcome=10,capture_revision=9)

def verify_deltas(before,after):
    require(set(before)==set(after)==set(DELTAS),'unexpected_count_tables')
    require(all(after[table]-before[table]==delta for table,delta in DELTAS.items()),'unexpected_dataset_delta')


READ='kdg_capture.capture.read.all'
EDIT='kdg_capture.capture.edit.all'
HEADERS={'Authorization':'Bearer synthetic-account'}


def envelope(identifier,**details):
    return dict(error='The request could not be completed.',error_id=identifier,**details)


def observe_response(response,engines):
    """Selected diagnostic fields only; never retain response payload dumps."""
    from uuid import UUID
    result=dict(status=response.status_code,cache_control=response.headers.get('cache-control'),
        leases_released=all(engine.pool.checkedout()==0 for engine in engines))
    try:value=response.json()
    except (ValueError,UnicodeError):return result
    if not isinstance(value,dict):return result
    selected={}
    for key in ('operation_id','capture_id','owner_account_id','owner_actor_id','created_by','updated_by'):
        try:
            raw=value[key]
            if type(raw) is str and str(UUID(raw))==raw:selected[key]=raw
        except (KeyError,ValueError,TypeError,AttributeError):pass
    for key in ('revision','current_revision'):
        raw=value.get(key)
        if type(raw) is str and raw.isascii() and raw.isdigit() and 1<=len(raw)<=19:selected[key]=raw
    if value.get('command_type') in ('capture.create','capture.edit'):selected['command_type']=value['command_type']
    if value.get('status') in ('committed','unresolved'):selected['status']=value['status']
    known={code for _,code in admin_edit_http.PAIRS}|{'capture_read_unavailable'}
    if type(value.get('error_id')) is str and value['error_id'] in known:selected['error_id']=value['error_id']
    stored=value.get('result')
    if isinstance(stored,dict):
        try:
            capture,revision=stored['capture_id'],stored['revision']
            if str(UUID(capture))==capture and type(revision) is str and revision.isascii() and revision.isdigit() and 1<=len(revision)<=19:
                selected['result']=dict(capture_id=capture,revision=revision)
        except (KeyError,ValueError,TypeError,AttributeError):pass
    result['observed']=selected
    return result


def verify_response(response,status,expected,engines):
    require(all(engine.pool.checkedout()==0 for engine in engines),'response_before_lease_release')
    require(response.headers.get('cache-control')=='private, no-store','private_no_store_required')
    require(response.status_code==status and response.json()==expected,'response_contract_disagrees')


async def recover_edit_loss(request,inspect,plan):
    for name,label in (('admin_a','edit_loss_recovery'),('noop','edit_loss_noop_recovery')):
        url='/api/v1/admin/operations/'+plan[name]['command']['operation_id']+'?command_type=capture.edit'
        await request(label,'admin','GET',url,expected_receipt(plan,name),permissions=[READ])
        inspect(label,unchanged=True)


async def read_response(client,url,label,attempt,engines,checks,checkouts):
    """Record the direct GET before checking current authority and released lease."""
    global STAGE
    STAGE=label
    start,before=len(checks),len(checkouts)
    response=await client.get(url,headers=HEADERS)
    observed=observe_response(response,engines)
    observed.update(access_permissions=checks[start:],checkouts=len(checkouts)-before)
    attempt['execution_results'][label]=observed
    require(observed['access_permissions']==[READ],'authority_sequence_disagrees')
    require(observed['checkouts']==1,'read_checkout_count_disagrees')
    require(observed['leases_released'],'response_before_lease_release')
    require(response.headers.get('cache-control')=='private, no-store','private_no_store_required')
    require(response.status_code==200,'current_read_failed')
    return response


def verify_read_shape(value,kind):
    """Literal closed wire contracts, independent of candidate DTO implementation."""
    detail_keys=set(('capture_id org_id owner_account_id owner_actor_id child_id child_label '
        'questionnaire_id questionnaire_version_id questionnaire_version definition revision '
        'observation_date answers captured_at created_by created_at updated_by updated_at').split())
    audit_keys=set(('org_id account_id capture_id owner_account_id owner_actor_id created_by '
        'created_at updated_by updated_at current_revision limit events next_cursor').split())
    event_keys={'revision','command_type','executor_actor_id','initiator_actor_id','recorded_at'}
    require(type(value) is dict and set(value)==(detail_keys if kind=='detail' else audit_keys),
        'closed_read_contract_disagrees')
    if kind=='audit':
        require(type(value['limit']) is int and value['limit']==30,'audit_limit_disagrees')
        require(type(value['events']) is list and all(type(item) is dict and set(item)==event_keys for item in value['events']),
            'closed_audit_event_contract_disagrees')


@contextmanager
def native_fault(data,plan):
    """Inject only actual invalid SQL after provisional private outcome, before history."""
    state=dict(capture_updates=0,history_inserts=0,outcome_present_before_fault=False,native_sqlstate=None)
    original=write.execute
    def execute(conn,budget,statement,parameters=None):
        if statement==admin_edit.UPDATE:state['capture_updates']+=1
        if statement==admin_edit.HISTORY_INSERT:
            require(state['capture_updates']==1,'fault_before_update')
            context=write.VerifiedContext(data.org,data.admin_account,data.admin_actor,'all_write',time.monotonic())
            key=write.OutcomeKey('kdg_capture',data.org,data.admin_account,'capture.edit',plan['retry']['command']['operation_id'])
            found=outcomes.lookup_private(conn,budget,key,context)
            require(found is not None and found.receipt().model_dump()==expected_receipt(plan,'retry') and
                found.executor_actor_id==found.initiator_actor_id==data.admin_actor,'uncommitted_outcome_required_before_fault')
            state['outcome_present_before_fault']=True
            try:
                original(conn,budget,'UPDATE kdg_capture.capture SET observation_date=NULL WHERE id=CAST(:capture AS uuid)',
                    dict(capture=plan['retry']['capture_id']))
            except Exception as error:
                state['native_sqlstate']=commit.sqlstate(error)
                raise
            raise AssertionError('native_fault_unexpected_success')
        return original(conn,budget,statement,parameters)
    with patch.object(write,'execute',execute):yield state


async def create_observation(value,data,entry,attempt,name):
    """Keep the synchronous helper's event loop and connection in one worker."""
    def run():
        engine=fixture.engine(value['urls']['runtime'])
        try:
            receipt=commit.execute(engine,data,json.dumps(entry['command']))
            # Preserve a committed result even if disposal subsequently fails.
            attempt['execution_results'][name]=dict(receipt=receipt)
            return receipt
        finally:engine.dispose()
    return await asyncio.to_thread(run)


async def exercise(value,data,plan,attempt):
    """Actual inert apps, pools and worker orchestration; only Access uses a mock."""
    global STAGE
    state=dict(account=data.admin_account,actor=data.admin_actor,denied=None,malformed=None,org=data.org)
    checks=[];engines=[];physical=set();closed=set();checkouts=[]
    async def access(request):
        raw=json.loads(request.content);permission=raw['permission'];checks.append(permission)
        require(raw['authorization_scope']==dict(kind='organization',org_id=state['org']),'unexpected_access_scope')
        # All database workers must be quiescent while checking current authority.
        require(all(engine.pool.checkedout()==0 for engine in engines),'access_under_database_lease')
        if permission==state['denied']:return httpx.Response(403,json=dict(detail=dict(code='access_denied')))
        evidence=dict(account_id=state['account'],actor_id=state['actor'],membership_id='1',decision_id=str(uuid4()),
            permission=permission,authorization_scope=dict(kind='organization',org_id=state['org']),
            resource_scope=dict(kind='organization',org_id=state['org']) if permission in (READ,EDIT) else
                dict(kind='own_account',account_id=state['account']),
            checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
        if state['malformed']==permission:evidence['resource_scope']=dict(kind='own_account',account_id=state['account'])
        return httpx.Response(200,json=evidence)
    def monitor(engine,readonly):
        engines.append(engine)
        def checkout(dbapi,record,proxy):
            with dbapi.cursor() as cursor:
                cursor.execute("SELECT current_user,session_user,current_setting('transaction_read_only'),current_setting('app.org_id',true),current_setting('app.account_id',true),current_setting('app.actor_id',true),current_setting('app.mode',true)")
                row=cursor.fetchone()
            dbapi.rollback()
            require(row[:3]==('kdg_capture_runtime','kdg_capture_runtime','on' if readonly else 'off'),'candidate_runtime_identity_disagrees')
            require(all(value in (None,'') for value in row[3:]),'pooled_context_not_cleared')
            physical.add(dbapi.info.backend_pid);checkouts.append(dbapi.info.backend_pid)
        event.listen(engine,'checkout',checkout)
        event.listen(engine,'close',lambda dbapi,record:closed.add(dbapi.info.backend_pid))
    names=[];rows={table:[] for table in ('capture','capture_revision','operation_outcome')}
    def inspect(label,*,unchanged=False,noop=False):
        nonlocal rows
        after,proof=read_storage(value,data,plan,names)
        verify_transition(rows,after,unchanged=unchanged,noop=noop)
        rows=after;attempt.setdefault('checks',{})[label]=proof;attempt['cases'].append(label)
    async with AsyncExitStack() as stack:
        clients={}
        for name,module in [('admin',admin_edit_http),('owner',edit_http),('detail',admin_http),
                            ('context',admin_edit_context_http),('audit',audit_http)]:
            app=module.create_candidate(org_id=data.org,access_url='https://access.invalid',service_key='synthetic-only',
                database_url=value['urls']['runtime'],transport=httpx.MockTransport(access))
            if name in ('admin','owner'):monitor(app.state.edit_engine,False)
            if name!='owner':monitor(app.state.recovery_engine,True)
            await stack.enter_async_context(app.router.lifespan_context(app))
            clients[name]=await stack.enter_async_context(httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='https://kdg.invalid'))
        async def request(label,client,method,url,expected,status=200,*,body=None,no_checkout=False,permissions=None):
            global STAGE
            STAGE=label
            before=len(checkouts);start=len(checks)
            response=await clients[client].request(method,url,headers=HEADERS,**({'json':body} if body is not None else {}))
            # Preserve actual execution before response or independent oracle assertions.
            attempt['execution_results'][label]=observe_response(response,engines)
            attempt['execution_results'][label].update(access_permissions=checks[start:],checkouts=len(checkouts)-before)
            verify_response(response,status,expected,engines)
            if no_checkout:require(len(checkouts)==before,'denial_checked_out_connection')
            if permissions is not None:require(checks[start:]==permissions,'authority_sequence_disagrees')
            return response.json()
        async def put(name,*,label=None,error=None,status=200,replay=False,path=None,body=None,fault=False):
            entry=plan[name];label=label or name
            state['account'],state['actor']=executor(data,entry)
            client=entry['executor'];route='/api/v1/'+('admin/' if client=='admin' else '')+'captures/'+(path or entry['capture_id'])
            await request(label,client,'PUT',route,error or expected_receipt(plan,name),status,
                body=body or entry['command'],permissions=[READ,EDIT] if client=='admin' else ['kdg_capture.capture.read.own',capture_edit.OWN])
            if not error and not replay:names.append(name)
            inspect(label,unchanged=bool(error) or replay,noop=not entry['changed'])
        # Actual create helper retains current owner permissions and original evidence.
        for name in ('create_a','create_b'):
            STAGE=name
            receipt=await create_observation(value,data,plan[name],attempt,name)
            require(receipt==expected_receipt(plan,name),'create_receipt_disagrees')
            names.append(name);inspect(name)
        conflict=lambda revision:envelope('kdg_capture.capture_revision_conflict',current_revision=str(revision))
        for name in ('admin_a','owner_a_stale','owner_a','admin_a_stale','admin_a2','noop',
                     'owner_b','admin_b_stale','admin_b','owner_b_stale','owner_b2'):
            stale=name.endswith('_stale')
            current={'owner_a_stale':2,'admin_a_stale':3,'admin_b_stale':2,'owner_b_stale':3}.get(name)
            await put(name,error=conflict(current) if stale else None,status=409 if stale else 200)
        # New operation cannot reuse a reviewed stale revision, even with unchanged values.
        repeated=data.request_inputs['repeated_review']['body']
        await put('denied',label='repeated_review',body=repeated,error=conflict(4),status=409)
        with native_fault(data,plan) as observed:
            attempt['native_fault_observation']=observed
            await put('retry',label='native_fault',error=envelope('internal_error'),status=500)
        attempt['execution_results']['native_fault']['fault']=dict(observed)
        require(observed['native_sqlstate'] in ('23502','23514') and observed['outcome_present_before_fault'] and
            observed['capture_updates']==1 and observed['history_inserts']==0,'native_constraint_failure_required')
        await put('retry')
        await put('retry',label='original_retry_replay',replay=True)
        changed=data.request_inputs['changed_path_body_replay']['body']
        await put('admin_a',label='changed_path_body_replay',path=plan['create_b']['capture_id'],body=changed,replay=True)
        state['account'],state['actor']=data.admin_account,data.admin_actor
        operation=plan['admin_a']['command']['operation_id']
        recovery='/api/v1/admin/operations/'+operation+'?command_type=capture.edit'
        state['denied']=EDIT
        await recover_edit_loss(request,inspect,plan)
        await request('edit_loss_put','admin','PUT','/api/v1/admin/captures/'+plan['denied']['capture_id'],
            envelope('access_denied'),403,body=plan['denied']['command'],no_checkout=True,permissions=[READ,EDIT])
        inspect('edit_loss_put',unchanged=True)
        state['denied']=READ
        await request('read_loss_recovery','admin','GET',recovery,envelope('access_denied'),403,no_checkout=True,permissions=[READ])
        inspect('read_loss_recovery',unchanged=True)
        state['denied']=None
        for account,actor,label in ((data.account,data.actor,'owner_private_absence'),
            (data.foreign_account,data.foreign_actor,'another_executor_absence')):
            state['account'],state['actor']=account,actor
            await request(label,'admin','GET',recovery,dict(operation_id=operation,command_type='capture.edit',status='unresolved'),permissions=[READ])
            inspect(label,unchanged=True)
        state['account'],state['actor']=data.admin_account,data.admin_actor
        for permission in (READ,EDIT):
            state['denied']=permission
            await request('denied_'+permission,'admin','PUT','/api/v1/admin/captures/'+plan['denied']['capture_id'],
                envelope('access_denied'),403,body=plan['denied']['command'],no_checkout=True,
                permissions=[READ] if permission==READ else [READ,EDIT])
            inspect('denied_'+permission,unchanged=True)
            state['denied']=None;state['malformed']=permission
            await request('malformed_'+permission,'admin','PUT','/api/v1/admin/captures/'+plan['denied']['capture_id'],
                envelope('authorization_unavailable'),503,body=plan['denied']['command'],no_checkout=True,
                permissions=[READ] if permission==READ else [READ,EDIT])
            inspect('malformed_'+permission,unchanged=True);state['malformed']=None
        await request('malformed_body','admin','PUT','/api/v1/admin/captures/'+plan['denied']['capture_id'],
            envelope('validation_failed'),422,body=data.request_inputs['malformed_body']['body'],no_checkout=True,permissions=[])
        inspect('malformed_body',unchanged=True)
        # Foreign target is a fresh journaled UUID, never an existing external org.
        await put('denied',label='foreign_target',path=data.foreign_account,error=envelope('capture_unavailable'),status=404)
        # Each current detail, original context and audit must agree with independent rows.
        for capture in rows['capture']:
            target=capture['id'];prefix='/api/v1/admin/captures/'+target
            STAGE='read_current_'+target
            response=await read_response(clients['detail'],prefix,'detail_'+target,attempt,engines,checks,checkouts)
            detail=response.json();verify_read_shape(detail,'detail')
            require(detail['capture_id']==target and all(detail[key]==capture[key] for key in
                ('org_id','owner_account_id','owner_actor_id','child_id','questionnaire_id','questionnaire_version_id',
                'answers','observation_date','captured_at','created_by','updated_by')) and detail['revision']==str(capture['revision']),
                'detail_storage_disagrees')
            require(detail['child_label']=='Synthetic durable qualification child' and
                all(datetime.fromisoformat(detail[key])==datetime.fromisoformat(capture[key]) for key in ('created_at','updated_at')),
                'detail_creation_update_disagrees')
            # Independent definition must remain the original published version.
            require(detail['definition']==commit.initial_definition(data.questions).model_dump(mode='json') and
                detail['questionnaire_version']=='1','original_definition_disagrees')
            inspect('detail_'+target,unchanged=True)
            await request('context_'+target,'context','GET',prefix+'/edit-context',
                dict(capture=detail,editable_fields=['observation_date','answers']),permissions=[READ,EDIT])
            inspect('context_'+target,unchanged=True)
            response=await read_response(clients['audit'],prefix+'/events','audit_'+target,attempt,engines,checks,checkouts)
            page=response.json();verify_read_shape(page,'audit')
            require(page['org_id']==data.org and page['account_id']==data.admin_account and page['capture_id']==target and
                all(datetime.fromisoformat(page[key])==datetime.fromisoformat(capture[key]) for key in ('created_at','updated_at')) and
                page['owner_account_id']==data.account and page['owner_actor_id']==data.actor and
                page['created_by']==data.actor and page['updated_by']==capture['updated_by'] and
                page['current_revision']==str(capture['revision']) and page['next_cursor'] is None,'audit_header_disagrees')
            expected=sorted([row for row in rows['capture_revision'] if row['capture_id']==target],key=lambda row:row['revision'],reverse=True)
            require(len(page['events'])==len(expected) and all(event['revision']==str(row['revision']) and
                all(event[key]==row[key] for key in ('command_type','executor_actor_id','initiator_actor_id')) and
                datetime.fromisoformat(event['recorded_at'])==datetime.fromisoformat(row['created_at'])
                for event,row in zip(page['events'],expected)),'audit_attribution_disagrees')
            inspect('audit_'+target,unchanged=True)
        # Another organization with legitimate all-read sees neither the receipt nor target.
        state['org']=data.foreign_org
        app=admin_edit_http.create_candidate(org_id=data.foreign_org,access_url='https://access.invalid',service_key='synthetic-only',
            database_url=value['urls']['runtime'],transport=httpx.MockTransport(access))
        monitor(app.state.edit_engine,False);monitor(app.state.recovery_engine,True)
        await stack.enter_async_context(app.router.lifespan_context(app))
        clients['foreign']=await stack.enter_async_context(httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='https://kdg.invalid'))
        await request('foreign_org_receipt','foreign','GET',recovery,dict(operation_id=operation,command_type='capture.edit',status='unresolved'),permissions=[READ])
        inspect('foreign_org_receipt',unchanged=True)
        await request('foreign_org_target','foreign','PUT','/api/v1/admin/captures/'+plan['denied']['capture_id'],
            envelope('capture_unavailable'),404,body=plan['denied']['command'],permissions=[READ,EDIT])
        inspect('foreign_org_target',unchanged=True)
    require(physical==closed and all(engine.pool.checkedout()==0 for engine in engines),'lifespan_connections_not_closed')
    return dict(leases_released=True,physical_connections_closed=True,committed_names=names)


def qualify(attempt):
    global STAGE
    STAGE='source_preflight'
    require(source_hashes()==INITIAL_SOURCES,'source_changed_before_execution')
    require(__debug__,'optimized_python_prohibited')
    STAGE='fixture_preflight'
    value,original,admin=fixture.retained()
    applied=fixture.migration_qualified(value);identities=fixture.identities(value);fixture.sentinel(admin)
    data,plan=new_plan()
    attempt.update(attempt_id=str(uuid4()),org_id=data.org,account_id=data.account,actor_id=data.actor,
        admin_account_id=data.admin_account,admin_actor_id=data.admin_actor,foreign_account_id=data.foreign_account,
        foreign_actor_id=data.foreign_actor,foreign_org_id=data.foreign_org,questionnaire_id=data.questionnaire,
        questionnaire_version_id=data.version,child_id=data.child,assignment_id=data.assignment_id,
        question_ids=data.questions,eligibility_ref=data.ref,plan=plan,request_inputs=data.request_inputs,cases=[],execution_results={},sources=INITIAL_SOURCES,
        applied_receipt=applied)
    before=preserved.table_counts(admin);original_rows=preserved.snapshot(admin,data.org)
    attempt.update(counts_before=before,prior_rows=original_rows)
    STAGE='intent_journal'
    attempt['start_receipt']=str(fixture.receipt('admin-api-start',dict(attempt,succeeded=None,qualified=False)))
    STAGE='source_before_writes'
    require(source_hashes()==INITIAL_SOURCES,'source_changed_before_writes')
    STAGE='fresh_parent_seed'
    commit.seed(admin,data,assignment_id=data.assignment_id)
    attempt['http']=asyncio.run(exercise(value,data,plan,attempt))
    STAGE='preservation_checks'
    after=preserved.table_counts(admin);verify_deltas(before,after)
    preserved.verify_preservation(original_rows,preserved.snapshot(admin,data.org))
    fixture.sentinel(admin);require(fixture.revision(value)==fixture.STORAGE,'ordinary_revision_changed')
    STAGE='source_postflight'
    require(source_hashes()==INITIAL_SOURCES,'source_changed_during_execution')
    result=dict(attempt,succeeded=True,qualified=True,native_admin_api=True,head=fixture.STORAGE,identities=identities,
        counts_after=after,prior_rows_unchanged=True,sentinel_unchanged=True,asgi_transport=True,
        real_access=False,real_identity_binding=False,real_http_listener=False,native_contention=False,native_cancellation=False)
    STAGE='success_receipt'
    destination=fixture.receipt('admin-api',result)
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
        try:report=str(fixture.receipt('admin-api',result))
        except Exception as receipt_error:
            report=None;result['receipt_error_type']=type(receipt_error).__name__
        output=dict(succeeded=False,qualified=False,error_type=type(error).__name__,failed_stage=STAGE,report=report)
        if 'receipt_error_type' in result:output['receipt_error_type']=result['receipt_error_type']
        print(json.dumps(output,sort_keys=True));return 1

if __name__=='__main__':raise SystemExit(main())
