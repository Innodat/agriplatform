"""Explicit durable qualification; retained writes only on the approved synthetic target.

Migration and qualification are separate commands. No provisioning, cleanup, API
mounting, real Access or automatic reversal. Failures retain data and safe receipts.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextvars import ContextVar
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
import threading
import time
from unittest.mock import patch
from uuid import uuid4

from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import text
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import capture_commit_fixture as fixture
import qualify_capture_storage as storage
sys.path.insert(0, str(fixture.ROOT/'apps/kdg-capture/write-candidate'))
import capture_create_handler as handler
from questionnaire import initial_definition

create, write = handler.create, handler.write
WRITER = ContextVar("kdg_qualification_writer", default=None)


def require(condition, identifier):
    if not condition:
        raise AssertionError(identifier)


def sqlstate(error):
    return storage.sqlstate(error)


def migrate_retained():
    require(__debug__, 'optimized_python_prohibited')
    config = fixture.configuration()
    graph = ScriptDirectory.from_config(config)
    require(graph.get_heads() == [fixture.STORAGE]
            and graph.get_revision(fixture.STORAGE).down_revision == fixture.FOUNDATION,
            'unexpected_candidate_graph')
    sources = source_hashes()
    value, original, admin = fixture.retained()
    before = fixture.native.retained_cluster_state(admin.set(database='postgres'), fixture.DATABASE)
    fixture.identities(value)
    fixture.sentinel(admin)
    head = fixture.revision(value)
    require(head in (fixture.FOUNDATION, fixture.STORAGE), 'unexpected_revision_requires_reconciliation')
    # On an explicit retry, reconcile a completed/uncertain prior migration by
    # observing its actual revision, rather than stamping or reapplying candidate DDL.
    action = 'upgrade' if head == fixture.FOUNDATION else 'reconciled_existing_head'
    provenance = None
    try:
        if head == fixture.STORAGE:
            provenance = fixture.migration_provenance()
        if head == fixture.FOUNDATION:
            missing_storage(value)
            with fixture.migration_environment(value):
                command.upgrade(config, 'head')
        require(fixture.revision(value) == fixture.STORAGE, 'migration_head_missing')
        fixture.sentinel(admin)
        after = fixture.native.retained_cluster_state(admin.set(database='postgres'), fixture.DATABASE)
        require(before == after, 'migration_metadata_changed')
    except Exception as error:
        try:
            observed = fixture.revision(value)
        except Exception:
            observed = 'unavailable'
        record_failure('migrate', error, dict(head=observed, before_head=head,
            action=action, applied_receipt=provenance, sources=sources))
        raise
    result = dict(succeeded=True, head=fixture.STORAGE, action=action,
        before_head=head, applied_receipt=provenance, current_metadata_sha256=after,
        historical_global_hash_matches=before == original['before'],
        missing_storage_observed=head == fixture.FOUNDATION,
        sources=sources)
    destination = fixture.receipt('migrate', result)
    return dict(result, report=str(destination))


def missing_storage(value):
    """Before migration acceptance: actual handler fails at absent outcome storage.

    Access is MockTransport; native restricted SQL is read-only until its first
    missing-table SELECT. Transaction exits roll back, and ledger remains0001.
    """
    data = Dataset()
    engine = fixture.engine(value['urls']['runtime'])
    try:
        with engine.connect() as connection:
            try:
                asyncio.run(make_handler(data, connection).execute(connection, data.raw(), 'Bearer synthetic'))
            except handler.HandlerError as error:
                require(error.error_id == 'internal_error' and sqlstate(error) == '42P01',
                        'missing_table_failure_required')
            else:
                raise AssertionError('missing_storage_unexpected_success')
        require(fixture.revision(value) == fixture.FOUNDATION, 'preflight_changed_revision')
    finally:
        engine.dispose()


class Dataset:
    def __init__(self):
        self.org, self.account, self.actor, self.questionnaire, self.version, self.child = [str(uuid4()) for _ in range(6)]
        self.questions = [str(uuid4()) for _ in range(4)]
        self.ref = str(uuid4())
        self.membership = '1'
        self.assigned = False
    def raw(self, **changes):
        return json.dumps(dict(dict(operation_id=str(uuid4()), command_version=1,
            capture_id=str(uuid4()), child_id=self.child, questionnaire_version_id=self.version,
            observation_date='2026-10-24', answers={self.questions[0]:{'value':1},
                **{key:{'value':False} for key in self.questions[1:]}},
            captured_at='2026-10-24T10:11:12.123456789Z', child_eligibility_ref=self.ref), **changes))


def changed(raw, **values):
    return json.dumps(dict(json.loads(raw), **values))


def seed(admin, data, *, assignment_id=None):
    """Only synthetic KDG parents. No capture/outcome/history or identity writes."""
    engine = fixture.engine(admin)
    try:
        with engine.begin() as connection:
            params = dict(org=data.org, actor=data.actor, account=data.account,
                questionnaire=data.questionnaire, version=data.version, child=data.child, ref=data.ref)
            definition = json.dumps(initial_definition(data.questions).model_dump())
            connection.execute(text('INSERT INTO kdg_capture.questionnaire(id,org_id,created_by) VALUES(:questionnaire,:org,:actor)'), params)
            connection.execute(text('INSERT INTO kdg_capture.questionnaire_version(id,org_id,questionnaire_id,display_version,definition,definition_hash,published_by) VALUES(:version,:org,:questionnaire,1,CAST(:definition AS jsonb),:hash,:actor)'), dict(params,definition=definition,hash=sha256(definition.encode()).hexdigest()))
            connection.execute(text("INSERT INTO kdg_capture.child(id,org_id,display_name,active,revision,created_by,updated_by) VALUES(:child,:org,'Synthetic durable qualification child',true,1,:actor,:actor)"),params)
            connection.execute(text("INSERT INTO kdg_capture.child_assignment(id,org_id,child_id,account_id,membership_id,active,revision,created_by,updated_by) VALUES(:id,:org,:child,:account,1,true,1,:actor,:actor)"),dict(params,id=assignment_id or str(uuid4())))
            connection.execute(text("INSERT INTO kdg_capture.child_eligibility(org_id,ref,account_id,membership_id,child_id,child_revision,observed_active,create_permission,issued_by) VALUES(:org,:ref,:account,1,:child,1,true,:permission,:actor)"),dict(params,permission=create.ALL))
    finally:
        engine.dispose()


def make_handler(data, connection):
    async def access(request):
        require(not connection.in_transaction(), 'network_under_transaction')
        permission = json.loads(request.content)['permission']
        if data.assigned and permission == create.ALL:
            return httpx.Response(403,json={'detail':{'code':'access_denied'}})
        return httpx.Response(200,json=dict(account_id=data.account,actor_id=data.actor,
            membership_id=data.membership, authorization_scope=dict(kind='organization',org_id=data.org),
            resource_scope=dict(kind='own_account',account_id=data.account),permission=permission,
            decision_id=str(uuid4()),checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')))
    return handler.CreateHandler(org_id=data.org,access_url='https://access.invalid',
        service_key='synthetic-only',transport=httpx.MockTransport(access))


def execute(engine, data, raw, writer=None):
    WRITER.set(writer)
    with engine.connect() as connection:
        return asyncio.run(make_handler(data,connection).execute(connection,raw,'Bearer synthetic')).model_dump()


def read_triplet(engine, data, raw, expected=1):
    """Fresh restricted connection after writer closed; exact linked immutable evidence."""
    command = json.loads(raw)
    with engine.connect() as connection:
        budget = write.Budget()
        context = write.VerifiedContext(data.org,data.account,data.actor,'own_read',time.monotonic())
        with write.transaction(connection,budget,context):
            for table, predicate, parameters in (
                ('capture','id=CAST(:id AS uuid)',dict(id=command['capture_id'])),
                ('capture_revision','capture_id=CAST(:id AS uuid)',dict(id=command['capture_id'])),
                ('operation_outcome','operation_id=CAST(:id AS uuid)',dict(id=command['operation_id']))):
                count = connection.execute(text('SELECT count(*) FROM kdg_capture.'+table+' WHERE '+predicate),parameters).scalar_one()
                require(count == expected, 'triplet_count_disagreement:'+table)
            if not expected:
                return
            row = connection.execute(text('''SELECT c.owner_account_id::text,c.owner_actor_id::text,
c.questionnaire_version_id::text,c.revision,c.answers,c.captured_at,c.created_by::text,c.updated_by::text,
h.executor_account_id::text,h.executor_actor_id::text,h.initiator_actor_id::text,
h.questionnaire_version_id::text,h.answers,h.captured_at,o.operation_id::text,o.result,
c.child_id::text,c.questionnaire_id::text,c.observation_date,c.child_eligibility_ref,c.creator_membership_id,
h.child_id::text,h.questionnaire_id::text,h.observation_date,h.revision,h.command_type,h.operation_id::text,
o.command_type,o.command_version
FROM kdg_capture.capture c JOIN kdg_capture.capture_revision h ON h.org_id=c.org_id AND h.capture_id=c.id
JOIN kdg_capture.operation_outcome o ON o.org_id=h.org_id AND o.id=h.outcome_id
WHERE c.id=CAST(:id AS uuid)'''),dict(id=command['capture_id'])).one()
            require(tuple(row[:4]) == (data.account,data.actor,data.version,1), 'owner_version_revision_disagreement')
            require(tuple(row[4:8]) == (command['answers'],command['captured_at'],data.actor,data.actor), 'capture_attribution_input_disagreement')
            require(tuple(row[8:15]) == (data.account,data.actor,data.actor,data.version,command['answers'],command['captured_at'],command['operation_id']), 'history_outcome_disagreement')
            require(row[15] == dict(capture_id=command['capture_id'],revision='1'), 'outcome_result_disagreement')
            require(tuple(row[16:21]) == (data.child,data.questionnaire,
                date.fromisoformat(command['observation_date']),command['child_eligibility_ref'],int(data.membership)),
                'capture_domain_facts_disagreement')
            require(tuple(row[21:]) == (data.child,data.questionnaire,
                date.fromisoformat(command['observation_date']),1,'capture.create',command['operation_id'],
                'capture.create',command['command_version']), 'history_command_identity_disagreement')


def read_counts(engine, data, checks):
    """Fresh owner-scoped reads for absence and complete per-dataset totals."""
    observed = {}
    with engine.connect() as connection:
        budget = write.Budget()
        context = write.VerifiedContext(data.org,data.account,data.actor,'own_read',time.monotonic())
        with write.transaction(connection,budget,context):
            for label,table,predicate,parameters,expected in checks:
                count = connection.execute(text('SELECT count(*) FROM kdg_capture.'+table+' WHERE '+predicate),parameters).scalar_one()
                require(count == expected,label)
                observed[table] = count
    return observed


def read_absent_targets(engine,data,raw):
    capture = json.loads(raw)['capture_id']
    read_counts(engine,data,[(label,table,column+'=CAST(:id AS uuid)',dict(id=capture),0)
        for label,table,column in (('unexpected_capture_survived','capture','id'),
                                  ('unexpected_history_survived','capture_revision','capture_id'))])


def read_absent_operation(engine,data,raw):
    operation = json.loads(raw)['operation_id']
    read_counts(engine,data,[(label,table,'operation_id=CAST(:id AS uuid)',dict(id=operation),0)
        for label,table in (('loser_orphan_outcome','operation_outcome'),
                            ('loser_orphan_history','capture_revision'))])


def read_dataset_counts(engine,data):
    return read_counts(engine,data,[("dataset_count_disagreement:"+table,table,
        'org_id=CAST(:org AS uuid) AND '+owner+'=CAST(:account AS uuid)',
        dict(org=data.org,account=data.account),5)
        for table,owner in (('capture','owner_account_id'),('operation_outcome','executor_account_id'),
                            ('capture_revision','owner_account_id'))])



def race(engine, data, first, second, *, fail_first=False, same_operation=True, force_busy=False):
    """Hold writer after its INSERTs; observe second entering competing native lock.

    Events are bounded. The holder waits until the other session reaches the exact
    contended SQL, then the main thread independently sees pg_stat_activity Lock.
    No Access callback or network wait occurs within either transaction.
    """
    inserted, competing, release = threading.Event(), threading.Event(), threading.Event()
    pids, failures = {}, []
    original = write.execute
    original_lock = write.outcome_lock
    def intercept(connection,budget,statement,parameters=None):
        name = WRITER.get()
        if name == 'first' and statement == create.HISTORY_INSERT:
            result = original(connection,budget,statement,parameters)
            pids['first'] = connection.connection.driver_connection.info.backend_pid
            inserted.set()
            require(release.wait(4), 'holder_barrier_timeout')
            if fail_first:
                # Real native NOT NULL/check failure after all three INSERTs.
                original(connection,budget,'UPDATE kdg_capture.capture SET observation_date=NULL WHERE id=CAST(:id AS uuid)',dict(id=json.loads(first)['capture_id']))
            return result
        if not same_operation and name == 'second' and statement == create.CHILD_LOCK:
            pids['second'] = connection.connection.driver_connection.info.backend_pid
            competing.set()
        return original(connection,budget,statement,parameters)
    def lock(connection,budget,key,context):
        if same_operation and WRITER.get() == 'second':
            pids['second'] = connection.connection.driver_connection.info.backend_pid
            competing.set()
        return original_lock(connection,budget,key,context)
    with patch.object(write,'execute',intercept), patch.object(write,'outcome_lock',lock):
        with ThreadPoolExecutor(max_workers=2,thread_name_prefix='kdg_race') as workers:
            a = workers.submit(execute,engine,data,first,'first')
            try:
                require(inserted.wait(4), 'first_writer_not_inserted')
                b = workers.submit(execute,engine,data,second,'second')
                require(competing.wait(4), 'second_writer_not_competing')
                # SELECT on pg_stat_activity is available to the restricted login for
                # its own sessions. This proves actual blocking rather than timing.
                deadline = time.monotonic()+1.5
                overlap = False
                while time.monotonic() < deadline:
                    with engine.connect() as observer:
                        overlap = observer.execute(text("SELECT wait_event_type='Lock' FROM pg_stat_activity WHERE pid=:pid"),dict(pid=pids['second'])).scalar_one_or_none() is True
                    if overlap:
                        break
                    time.sleep(.01)
                require(overlap, 'native_lock_overlap_not_observed')
                if force_busy:
                    # Deliberately cross only the second request's 2s lock cap.
                    # Its budget remains bounded and the later retry reauthorizes.
                    time.sleep(2.15)
            finally:
                release.set()
            results=[]
            for future in (a,b):
                try:
                    results.append(future.result(timeout=12))
                except handler.HandlerError as error:
                    if fail_first and future is a:
                        require(sqlstate(error) in ('23502','23514'), 'native_post_insert_constraint_failure_required')
                    failures.append(error.error_id)
                    results.append(None)
    if fail_first:
        require(results[0] is None and failures == ['internal_error'], 'failed_first_writer_not_refused')
        require(results[1] is not None, 'waiting_valid_writer_failed')
    elif same_operation:
        require(results[0] is not None, 'first_writer_failed')
        if force_busy:
            require(results[1] is None and failures == ['operation_busy'], 'bounded_busy_not_observed')
        if results[1] is None:
            require(failures == ['operation_busy'], 'unexpected_duplicate_failure')
            results[1] = execute(engine,data,second)
        require(results[0] == results[1], 'duplicate_receipt_disagreement')
    else:
        require(results[0] is not None and results[1] is None and failures == ['internal_error'], 'shared_capture_safe_loser_missing')
    return results


def source_hashes():
    paths = [Path(__file__),Path(fixture.__file__),Path(fixture.native.__file__),
        Path(storage.__file__),Path(handler.__file__),Path(create.__file__),
        Path(create.outcomes.__file__),Path(write.__file__)]
    paths += [fixture.ROOT/path for path in (
        'apps/kdg-capture/api/context.py',
        'apps/kdg-capture/api/capture_commands.py',
        'apps/kdg-capture/api/questionnaire.py',
        'apps/kdg-capture/migrations/candidates/0002_capture_storage.py',
        'apps/kdg-capture/migrations/versions/0001_foundation.py',
        'apps/kdg-capture/migrations/env.py',
        'apps/kdg-capture/migrations/policy.py',
        'apps/kdg-capture/database-tools/owned_migration.py',
        'apps/kdg-capture/alembic.ini',
        'platform/deployment/dev.py',
        'platform/deployment/native_cli.py',
        'platform/deployment/environments/kdg-local.json')]
    return {str(path.relative_to(fixture.ROOT)):sha256(path.read_bytes()).hexdigest() for path in paths}


def record_failure(phase, error, details):
    """Preserve the originating error and one informative append-only receipt."""
    try:
        destination = fixture.receipt(phase, dict(details, succeeded=False,
            error='phase_failed_retained_requires_reconciliation',
            failure_type=type(error).__name__, sqlstate=sqlstate(error)))
        error.capture_commit_failure_receipt = str(destination)
    except Exception:
        pass


def command_plan(data):
    fresh = data.raw()
    identical = data.raw()
    different = data.raw()
    failed = data.raw()
    shared = data.raw()
    return dict(fresh=fresh,
        retry=changed(fresh,capture_id=str(uuid4()),child_id=str(uuid4()),
            questionnaire_version_id=str(uuid4()),answers={},child_eligibility_ref='obsolete'),
        identical_first=identical,identical_second=identical,
        different_first=different,different_second=changed(different,capture_id=str(uuid4()),answers={}),
        failure_first=failed,failure_second=changed(failed,capture_id=str(uuid4())),
        shared_first=shared,shared_second=changed(shared,operation_id=str(uuid4())))


def qualify_retained():
    attempt = dict(attempt_id=str(uuid4()),start_receipt=None,cases=[],commands={})
    try:
        return _qualify_retained(attempt)
    except Exception as error:
        record_failure('qualify',error,attempt)
        raise


def _qualify_retained(attempt):
    require(__debug__, 'optimized_python_prohibited')
    value, original, admin = fixture.retained()
    fixture.migration_qualified(value)
    before = fixture.native.retained_cluster_state(admin.set(database='postgres'),fixture.DATABASE)
    identities = fixture.identities(value)
    fixture.sentinel(admin)
    data = Dataset()
    # Append intent before the first persistent seed write. A partial seed or
    # failed qualification remains attributable without rewriting prior receipts.
    plan = command_plan(data)
    attempt.update(head=fixture.STORAGE,org_id=data.org,account_id=data.account,
        actor_id=data.actor,questionnaire_id=data.questionnaire,
        questionnaire_version_id=data.version,child_id=data.child,
        question_ids=data.questions,eligibility_ref=data.ref,sources=source_hashes())
    attempt['commands'] = {name: {key: json.loads(raw)[key] for key in ('operation_id','capture_id')}
                           for name, raw in plan.items()}
    attempt['start_receipt'] = str(fixture.receipt('qualification-start',dict(attempt,
        succeeded=None,current_metadata_sha256=before)))
    seed(admin,data)
    engine = fixture.engine(value['urls']['runtime'])
    cases=attempt['cases']
    try:
        raw = plan['fresh']
        receipt = execute(engine,data,raw)
        read_triplet(engine,data,raw)
        cases.append('fresh_commit_independent_restricted_triplet')
        # Deliberately discard delivery; retry uses unusable fresh semantics.
        retry = plan['retry']
        require(execute(engine,data,retry)==receipt,'changed_body_replay_not_original')
        read_triplet(engine,data,raw)
        read_absent_targets(engine,data,retry)
        cases.append('discarded_delivery_changed_body_original_receipt')
        for label,different in (('identical',False),('different',True)):
            first=plan[label+'_first']
            second=plan[label+'_second']
            race(engine,data,first,second,force_busy=not different)
            read_triplet(engine,data,first)
            if different:
                read_absent_targets(engine,data,second)
            cases.append('overlapping_duplicate_'+label+'_body')
        first=plan['failure_first']
        second=plan['failure_second']
        race(engine,data,first,second,fail_first=True)
        read_triplet(engine,data,second)
        read_absent_targets(engine,data,first)
        cases.append('native_failure_after_inserts_waiter_commits')
        first=plan['shared_first']
        second=plan['shared_second']
        race(engine,data,first,second,same_operation=False)
        read_triplet(engine,data,first)
        read_absent_operation(engine,data,second)
        cases.append('different_operations_shared_capture_safe_loser')
        authority_cases(engine,data,raw,receipt,admin)
        cases.append('assigned_replay_current_stored_child_membership')
        restrictions(engine,data,raw)
        cases.append('foreign_scope_ddl_ledger_role_switch_denied')
        counts = read_dataset_counts(engine,data)
    finally:
        engine.dispose()
    fixture.sentinel(admin)
    after=fixture.native.retained_cluster_state(admin.set(database='postgres'),fixture.DATABASE)
    require(before==after,'retained_metadata_changed')
    result=dict(attempt,succeeded=True,qualified=True,head=fixture.STORAGE,retained_triplets=counts,
        identities=identities,retained=True,org_id=data.org,account_id=data.account,
        current_metadata_sha256=after,historical_global_hash_matches=before==original['before'],sources=source_hashes())
    destination=fixture.receipt('qualify',result)
    return dict(result,report=str(destination))


def authority_cases(engine,data,raw,receipt,admin):
    data.assigned=True
    changed_body=changed(raw,child_id=str(uuid4()),answers={},child_eligibility_ref='obsolete')
    require(execute(engine,data,changed_body)==receipt,'assigned_stored_child_replay_failed')
    data.membership='2'
    try:
        execute(engine,data,changed_body)
    except handler.HandlerError as error:
        require(error.error_id=='assignment_unavailable','membership_denial_wrong_error')
    else:
        raise AssertionError('old_membership_assignment_accepted')
    data.membership='1'
    parent_engine=fixture.engine(admin)
    try:
        with parent_engine.begin() as connection:
            connection.execute(text(create.CHILD_LOCK),dict(org=data.org,child=data.child))
            connection.execute(text('UPDATE kdg_capture.child_assignment SET active=false,revision=revision+1 WHERE org_id=CAST(:org AS uuid) AND child_id=CAST(:child AS uuid)'),dict(org=data.org,child=data.child))
    finally:
        parent_engine.dispose()
    try:
        execute(engine,data,changed_body)
    except handler.HandlerError as error:
        require(error.error_id=='assignment_unavailable','inactive_assignment_denial_wrong_error')
    else:
        raise AssertionError('inactive_stored_child_assignment_accepted')
    data.assigned=False


def restrictions(engine,data,raw):
    with engine.connect() as connection:
        with write.transaction(connection,write.Budget(),write.VerifiedContext(data.org,str(uuid4()),str(uuid4()),'own_read',time.monotonic())):
            for table in ('capture','capture_revision','operation_outcome'):
                require(connection.execute(text('SELECT count(*) FROM kdg_capture.'+table)).scalar_one()==0,'foreign_account_visible')
    with engine.connect() as connection:
        with write.transaction(connection,write.Budget(),write.VerifiedContext(str(uuid4()),data.account,data.actor,'all_read',time.monotonic())):
            for table in ('capture','capture_revision','operation_outcome','child','child_assignment','child_eligibility','questionnaire','questionnaire_version'):
                require(connection.execute(text('SELECT count(*) FROM kdg_capture.'+table)).scalar_one()==0,'foreign_org_visible')
    for statement in ('CREATE TABLE kdg_capture.forbidden_commit_probe(value int)',
                      'SELECT * FROM kdg_capture.alembic_version',
                      'SET ROLE kdg_capture_migrator','SET ROLE supabase_admin'):
        with engine.connect() as connection:
            try:
                connection.execute(text(statement))
            except Exception as error:
                require(sqlstate(error)=='42501','unexpected_restriction_sqlstate')
                connection.rollback()
            else:
                connection.rollback()
                raise AssertionError('runtime_restriction_missing')


def main(argv=None):
    phase='not_attempted'
    try:
        require(__debug__,'optimized_python_prohibited')
        args=sys.argv[1:] if argv is None else argv
        if args == ['--migrate-retained']:
            phase='migrate'
            result=migrate_retained()
        elif args == ['--qualify-retained']:
            phase='qualify'
            result=qualify_retained()
        else:
            raise ValueError('explicit_phase_required')
        print(json.dumps(dict(succeeded=True,phase=phase,head=result['head'],
            cases=len(result.get('cases',[])),report=result['report'])))
        return 0
    except Exception as error:
        if phase in ('migrate','qualify') and not getattr(error,'capture_commit_failure_receipt',None):
            # This receipt is best effort; never replace the original safe failure.
            try:
                record_failure(phase,error,dict(head='unavailable'))
            except Exception:
                pass
        print(json.dumps(dict(succeeded=False,phase=phase,error='capture_commit_failed_requires_reconciliation',sqlstate=sqlstate(error),
            report=getattr(error,'capture_commit_failure_receipt',None))),file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
