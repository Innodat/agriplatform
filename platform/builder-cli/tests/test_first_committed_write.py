"""Actual restricted PostgreSQL proof; dependencies/fixture absence fails, never skips."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time
import traceback
from uuid import uuid4

import pytest
import rfc8785
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

BUILDER=Path(__file__).resolve().parents[1]
EXAMPLE=BUILDER/'examples/owned-service'
sys.path[:0]=[str(EXAMPLE),str(Path(__file__).resolve().parent)]
import first_committed_write as a
from first_committed_sample import document, run


ORG=str(uuid4()); ACCOUNT=str(uuid4()); ACTOR=str(uuid4())


def test_candidate_import():
    assert callable(a.outcome_lock_key)


@pytest.fixture(scope='session')
def databases():
    path=os.environ.get('ATOMIC_WRITE_FIXTURE')
    assert path and Path(path).is_file(), 'ATOMIC_WRITE_FIXTURE must name retained private fixture.json'
    prepared=json.loads((Path(path).parent/'prepared.json').read_text())
    assert prepared['sql_sha256']==hashlib.sha256(Path(__file__).with_name('first_committed_fixture.sql').read_bytes()).hexdigest(), 'atomic_fixture_sql_changed_requires_fresh_fixture'
    private=json.loads(Path(path).read_text())
    assert set(private)=={'migrator','runtime'}, 'atomic_fixture_invalid'
    engines={}
    try:
        for role in private:
            engines[role]=create_engine(private[role].replace('postgresql:','postgresql+psycopg:'),
                hide_parameters=True,pool_size=1,max_overflow=4,
                connect_args={'connect_timeout':3})
        with engines['migrator'].begin() as c:
            c.execute(text('INSERT INTO sample.actor(id) VALUES(CAST(:id AS uuid))'),{'id':ACTOR})
        with engines['runtime'].begin() as c:
            flags=c.execute(text('SELECT rolsuper,rolbypassrls,rolcreatedb,rolcreaterole FROM pg_roles WHERE rolname=current_user')).one()
            assert flags==(False,False,False,False)
            assert int(c.execute(text('SHOW server_version_num')).scalar_one())>=170000
            guards=c.execute(text("SELECT relrowsecurity,relforcerowsecurity,pg_get_userbyid(relowner)<>current_user FROM pg_class JOIN pg_namespace ON pg_namespace.oid=relnamespace WHERE nspname='sample' AND relname IN ('record','outcome','revision')")).all()
            assert guards==[(True,True,True)]*3
    except Exception:
        pytest.fail('atomic_fixture_connection_failed',pytrace=False)
    yield engines
    for engine in engines.values():engine.dispose()


@pytest.fixture
def record(databases):
    target=str(uuid4())
    b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',time.monotonic())
    with databases['runtime'].connect() as c:
        with a.transaction(c,b,ctx):
            a.execute(c,b,"""INSERT INTO sample.record(id,org_id,owner_account_id,value,revision,created_by,updated_by)
                VALUES(CAST(:id AS uuid),CAST(:org AS uuid),CAST(:account AS uuid),0,1,CAST(:actor AS uuid),CAST(:actor AS uuid))""",
                dict(id=target,org=ORG,account=ACCOUNT,actor=ACTOR))
    return target


def call(databases,doc,op,**kwargs):
    with databases['runtime'].connect() as c:
        return run(c,doc,op,actor=ACTOR,authorize=lambda target,command,t:True,**kwargs)


def state(databases,target):
    b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_read',time.monotonic())
    with databases['runtime'].connect() as c:
        with a.transaction(c,b,ctx):
            row=a.execute(c,b,'SELECT value,revision,created_by,updated_by,created_at,updated_at FROM sample.record WHERE id=CAST(:id AS uuid)',{'id':target}).one()
            counts=tuple(a.execute(c,b,f'SELECT count(*) FROM sample.{table} WHERE {column}=CAST(:id AS uuid)',{'id':target}).scalar_one()
                for table,column in [('outcome','target_id'),('revision','record_id')])
    return tuple(row),counts



def test_changed_valid_target_body_versions_and_later_lifecycle(databases,record):
    op=str(uuid4());doc=document(ORG,ACCOUNT,record,1,3)
    original=call(databases,doc,op)
    assert original==dict(command_type='record.edit',command_version=1,result_version=1,result=dict(record_id=record,revision='2'))
    call(databases,document(ORG,ACCOUNT,record,2,9),str(uuid4()))
    with databases['runtime'].connect() as c:
        b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',time.monotonic())
        with a.transaction(c,b,ctx):a.execute(c,b,'UPDATE sample.record SET closed=true WHERE id=CAST(:id AS uuid)',dict(id=record))
    before=state(databases,record);calls=[]
    changed=document(ORG,ACCOUNT,str(uuid4()),777,99,version=2)
    with databases['runtime'].connect() as c:
        def authority(target,command,timeout):
            assert not c.in_transaction() and timeout<=3
            calls.append(target);return target==record
        assert run(c,changed,op,actor=ACTOR,authorize=authority)==original
        assert run(c,changed,op,actor=ACTOR,authorize=authority,lookup=True)==original
    assert calls==[record,record] and state(databases,record)==before
    with pytest.raises(a.WriteError,match='^lifecycle_conflict$'):call(databases,doc,str(uuid4()))


@pytest.mark.parametrize('command',['record.create','record.edit'])
@pytest.mark.parametrize('failure',['evidence','outcome'])
def test_required_insert_failure_rolls_back_every_effect(databases,record,command,failure):
    target=str(uuid4()) if command=='record.create' else record
    before=state(databases,record)
    op=str(uuid4());doc=document(ORG,ACCOUNT,target,0 if command=='record.create' else 1,22)
    with pytest.raises(a.WriteError,match='^internal_error$') as error:
        call(databases,doc,op,command=command,fail=failure)
    assert target not in ''.join(traceback.format_exception(error.value))
    assert error.value.__suppress_context__ and state(databases,record)==before
    # Observe the attempted create identity immediately, with matching authorized RLS.
    if command=='record.create':
        assert target_counts(databases,target,op)==(0,0,0)
    with databases['runtime'].connect() as c:
        assert c.execute(text('SELECT count(*) FROM sample.record')).scalar_one()==0;c.rollback()
    # The original operation remains usable after a proven rollback.
    assert call(databases,doc,op,command=command)['result']['record_id']==target


def test_create_replay_noop_and_exact_command_scope(databases,record):
    target=str(uuid4());op=str(uuid4())
    created=call(databases,document(ORG,ACCOUNT,target,0,7),op,command='record.create')
    assert created['result']==dict(record_id=target,revision='1') and state(databases,target)[1]==(1,1)
    assert call(databases,document(ORG,ACCOUNT,str(uuid4()),34,88,2),op,command='record.create')==created
    noop=call(databases,document(ORG,ACCOUNT,target,1,7),op)
    assert noop['command_type']=='record.edit' and state(databases,target)[1]==(2,1)
    assert call(databases,document(ORG,ACCOUNT,record,1,999),op)==noop


def test_different_bodies_race_and_raced_target_recheck(databases,record):
    from threading import Barrier
    gate=Barrier(2);op=str(uuid4());other=str(uuid4());first_target=str(uuid4());targets=[]
    # Create race: target differs, so one contender must rollback/recheck authority.
    def attempt(target,value):
        count=[0]
        with databases['runtime'].connect() as c:
            def authorize(target,command,timeout):
                assert not c.in_transaction();count[0]+=1;targets.append(target)
                if count[0]==1:gate.wait(timeout=2)
                return True
            return run(c,document(ORG,ACCOUNT,target,0,value),op,actor=ACTOR,authorize=authorize,command='record.create')
    with ThreadPoolExecutor(max_workers=2) as pool:
        first=pool.submit(attempt,first_target,5)
        second=pool.submit(attempt,other,8)
        results=[first.result(timeout=7),second.result(timeout=7)]
    assert results[0]==results[1] and len(targets)==3
    winner=results[0]['result']['record_id'];row,counts=state(databases,winner)
    assert row[0]=={first_target:5,other:8}[winner] and counts==(1,1)
    loser=other if winner==first_target else first_target
    assert target_counts(databases,loser,op)==(0,0,0)
    with databases['runtime'].connect() as c:
        b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_read',time.monotonic())
        with a.transaction(c,b,ctx):
            evidence=a.execute(c,b,'SELECT value,revision FROM sample.revision WHERE record_id=CAST(:id AS uuid)',dict(id=winner)).one()
            assert tuple(evidence)==row[:2]


def test_denied_original_target_and_foreign_unknown(databases,record):
    op=str(uuid4());doc=document(ORG,ACCOUNT,record,1,4);call(databases,doc,op)
    with databases['runtime'].connect() as c:
        checked=[]
        def denied(target,command,timeout):checked.append(target);return False
        with pytest.raises(a.WriteError,match='^access_denied$'):
            run(c,document(ORG,ACCOUNT,str(uuid4()),1,3),op,actor=ACTOR,authorize=denied)
        assert checked==[record] and not c.in_transaction()
    for org,account in [(str(uuid4()),ACCOUNT),(ORG,str(uuid4()))]:
        assert call(databases,document(org,account,record,1,4),op,lookup=True) is None
    unknown=str(uuid4());assert call(databases,doc,unknown,lookup=True) is None
    assert call(databases,document(ORG,ACCOUNT,record,2,6),unknown)['result']['revision']=='3'


@pytest.mark.parametrize('change',[dict(command_version=3),dict(result_version=2),dict(result={'record_id':'bad','revision':'1'})])
def test_unsupported_stored_receipt_is_retained(databases,record,change):
    op=str(uuid4());args=dict(id=str(uuid4()),org=ORG,account=ACCOUNT,actor=ACTOR,op=op,target=record,
        command_version=1,result_version=1,result=dict(record_id=record,revision='1'))
    args.update(change)
    args['result']=json.dumps(args['result'])
    with databases['runtime'].connect() as c:
        b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',time.monotonic())
        with a.transaction(c,b,ctx):
            a.execute(c,b,"""INSERT INTO sample.outcome(id,org_id,executor_account_id,executor_actor_id,command_type,
             operation_id,command_version,result_version,result,target_id) VALUES(CAST(:id AS uuid),CAST(:org AS uuid),
             CAST(:account AS uuid),CAST(:actor AS uuid),'record.edit',CAST(:op AS uuid),:command_version,:result_version,
             CAST(:result AS jsonb),CAST(:target AS uuid))""",args)
    before=state(databases,record)
    with pytest.raises(a.WriteError,match='^operation_verification_unavailable$'):call(databases,document(ORG,ACCOUNT,record,1,5),op)
    assert state(databases,record)==before


@pytest.mark.parametrize('data',[b'{"a":1,"a":2}',b'{"a":NaN}',b'{"a":1e999}',b'{"a":"\\ud800"}',b'{"a":"\\u0000"}',b'[]'*5000])
def test_strict_wire_parser(data):
    with pytest.raises(a.WriteError,match='^invalid_command$'):a.parse_json(data)


def test_invalid_fresh_stale_and_structure_before_authority(databases,record):
    from copy import deepcopy
    base=document(ORG,ACCOUNT,record,1,2)
    for field,value in [('command_version',True),('command_version',3),('command_type','record.create')]:
        doc=deepcopy(base);doc[field]=value;called=[]
        with pytest.raises(a.WriteError,match='^invalid_command$'):
            run(None,doc,str(uuid4()),actor=ACTOR,authorize=lambda *args:called.append(True))
        assert not called
    for expected in ('2','0'):
        with pytest.raises(a.WriteError,match='^revision_conflict$'):call(databases,document(ORG,ACCOUNT,record,expected,2),str(uuid4()))
    assert state(databases,record)[1]==(0,0)


def test_no_fingerprint_fields_or_calls(databases,monkeypatch):
    import command_fingerprint
    import atomic_write
    def forbidden(*args,**kwargs):raise AssertionError('fingerprint invoked')
    monkeypatch.setattr(command_fingerprint,'create_fingerprint',forbidden)
    monkeypatch.setattr(command_fingerprint,'verify_fingerprint',forbidden)
    monkeypatch.setattr(atomic_write,'verify_fingerprint',forbidden)
    target=str(uuid4());op=str(uuid4());doc=document(ORG,ACCOUNT,target,0,4)
    original=call(databases,doc,op,command='record.create')
    assert call(databases,document(ORG,ACCOUNT,str(uuid4()),99,42,2),op,command='record.create')==original
    edit=call(databases,document(ORG,ACCOUNT,target,1,7),op)
    assert call(databases,document(ORG,ACCOUNT,str(uuid4()),99,42,2),op)==edit
    with databases['runtime'].connect() as c:
        columns=c.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema='sample' AND table_name='outcome'")).scalars().all();c.rollback()
    assert not any('fingerprint' in name for name in columns)


def test_pool_context_commit_rollback_and_foreign_isolation(databases,record):
    with databases['runtime'].connect() as c:
        backend=c.execute(text('SELECT pg_backend_pid()')).scalar_one();c.rollback()
        assert c.execute(text('SELECT count(*) FROM sample.record')).scalar_one()==0;c.rollback()
        for fail in [False,True]:
            b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_read',time.monotonic())
            try:
                with a.transaction(c,b,ctx):
                    assert a.execute(c,b,'SELECT count(*) FROM sample.record WHERE id=CAST(:id AS uuid)',{'id':record}).scalar_one()==1
                    if fail:raise ValueError('synthetic_rollback')
            except ValueError:pass
            assert c.execute(text('SELECT count(*) FROM sample.record')).scalar_one()==0
            assert all(not v for v in c.execute(text("SELECT current_setting('app.org_id',true),current_setting('app.account_id',true),current_setting('app.actor_id',true),current_setting('app.mode',true)")).one())
            c.rollback()
        for changes in [dict(org_id=str(uuid4())),dict(account_id=str(uuid4())),dict(mode='own_write')]:
            b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_read',time.monotonic());ctx=replace(ctx,**changes)
            with a.transaction(c,b,ctx):
                count=a.execute(c,b,'SELECT count(*) FROM sample.record WHERE id=CAST(:id AS uuid)',{'id':record}).scalar_one()
                assert count==(1 if changes.get('mode')=='own_write' else 0)
        assert c.execute(text('SELECT pg_backend_pid()')).scalar_one()==backend;c.rollback()
    with databases['runtime'].connect() as reused:
        assert reused.execute(text('SELECT pg_backend_pid()')).scalar_one()==backend
        assert reused.execute(text('SELECT count(*) FROM sample.record')).scalar_one()==0
        reused.rollback()


@pytest.mark.parametrize('isolation',['AUTOCOMMIT','REPEATABLE READ','SERIALIZABLE'])
def test_non_read_committed_or_autocommit_refuses(databases,isolation):
    with databases['runtime'].connect().execution_options(isolation_level=isolation) as c:
        b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_read',time.monotonic())
        with pytest.raises(a.WriteError,match='^invalid_write_context$'):
            with a.transaction(c,b,ctx):pytest.fail('must_not_enter')


def test_immutable_guards_runtime_ddl_and_exact_linkage(databases,record):
    doc=document(ORG,ACCOUNT,record,1,8);op=str(uuid4());call(databases,doc,op)
    for table in ('outcome','revision'):
        for action in ('UPDATE sample.'+table+' SET id=id','DELETE FROM sample.'+table,'TRUNCATE sample.'+table):
            # Migrator owner is also guarded despite owning schema/table and no runtime privileges.
            with databases['migrator'].connect() as c:
                with pytest.raises(SQLAlchemyError):
                    c.execute(text(action))
                c.rollback()
    with databases['runtime'].connect() as c:
        with pytest.raises(SQLAlchemyError):c.execute(text('CREATE TABLE sample.forbidden(id int)'))
        c.rollback()
    b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',time.monotonic())
    with databases['runtime'].connect() as c:
        with a.transaction(c,b,ctx):
            row=dict(a.execute(c,b,'SELECT * FROM sample.revision WHERE record_id=CAST(:id AS uuid)',{'id':record}).mappings().one())
    for field in ['org_id','executor_actor_id','executor_account_id','operation_id','outcome_id','owner_account_id']:
        values=dict(row);values['id']=uuid4();values['revision']=99;values[field]=uuid4()
        with databases['runtime'].connect() as c:
            b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',time.monotonic())
            with pytest.raises(a.WriteError,match='^internal_error$'):
                with a.transaction(c,b,ctx):
                    columns=','.join(values);params=','.join(':'+k for k in values)
                    a.execute(c,b,f'INSERT INTO sample.revision({columns}) VALUES({params})',values)
    assert state(databases,record)[1]==(1,1)


def test_outcome_lock_timeout_only_is_busy_and_budget_observation_bounds(databases,record,monkeypatch):
    op=str(uuid4());doc=document(ORG,ACCOUNT,record,1,1)
    key=a.OutcomeKey('sample',ORG,ACCOUNT,'record.edit',op)
    import first_committed_sample
    diagnostics={}
    original=first_committed_sample.outcome_lock
    def instrumented(conn,budget,key,context):
        configured,pid,server_start=a.execute(conn,budget,
            "SELECT current_setting('lock_timeout'),pg_backend_pid(),extract(epoch from clock_timestamp())").one()
        diagnostics.update(lock_timeout=configured,pid=pid,server_start=float(server_start))
        try:
            original(conn,budget,key,context)
        except a.WriteError as error:
            driver=getattr(error.__context__,'orig',None)
            diagnostics['sqlstate']=getattr(driver,'sqlstate',None)
            raise
    monkeypatch.setattr(first_committed_sample,'outcome_lock',instrumented)
    with databases['runtime'].connect() as holder:
        holder_pid=holder.execute(text('SELECT pg_backend_pid()')).scalar_one()
        holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':a.outcome_lock_key(key)})
        started=time.monotonic()
        def blocked_call():
            with pytest.raises(a.WriteError,match='^operation_busy$'):
                call(databases,doc,op)
            with databases['runtime'].connect() as observer:
                diagnostics['server_end']=float(observer.execute(text('SELECT extract(epoch from clock_timestamp())')).scalar_one())
                observer.rollback()
        with ThreadPoolExecutor(max_workers=1) as pool:
            pending=pool.submit(blocked_call)
            witnessed=False;deadline=time.monotonic()+1
            while time.monotonic()<deadline and not pending.done():
                if 'pid' in diagnostics:
                    with databases['runtime'].connect() as observer:
                        witnessed=observer.execute(text('SELECT :holder=ANY(pg_blocking_pids(:blocked))'),
                            dict(holder=holder_pid,blocked=diagnostics['pid'])).scalar_one()
                        observer.rollback()
                    if witnessed:break
                time.sleep(0.01)
            pending.result(timeout=4)
        diagnostics.update(monotonic_elapsed=time.monotonic()-started,blocker_witnessed=witnessed,
            server_elapsed=diagnostics['server_end']-diagnostics['server_start'])
        # Only typed timings/configuration/classification; no SQL, credentials or payload.
        output=Path(os.environ['ATOMIC_WRITE_FIXTURE']).parent/('busy-diagnostics-'+uuid4().hex+'.json')
        output.write_text(json.dumps(diagnostics))
        assert diagnostics['lock_timeout']=='2s' and diagnostics['sqlstate']=='55P03'
        assert witnessed
        assert 1.7<diagnostics['monotonic_elapsed']<3.5
        holder.rollback()
    assert state(databases,record)[1]==(0,0)
    with databases['runtime'].connect() as c:
        b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_read',b.started_at-2)
        with pytest.raises(a.WriteError,match='^authorization_observation_expired$'):
            with a.transaction(c,b,ctx):pass
        b=a.Budget();b.deadline=time.monotonic()-1
        with pytest.raises(a.WriteError,match='^execution_timeout$'):
            with a.transaction(c,b,replace(ctx,observed_at=time.monotonic())):pass
        b=a.Budget();ctx=replace(ctx,observed_at=time.monotonic())
        with pytest.raises(a.WriteError,match='^internal_error$'):
            with a.transaction(c,b,ctx):
                # Small remaining budget makes the actual statement timeout bounded.
                b.deadline=time.monotonic()+0.08
                a.execute(c,b,'SELECT pg_sleep(1)')
        assert not c.in_transaction()


def test_actual_domain_lock_timeout_is_not_operation_busy(databases,record):
    with databases['runtime'].connect() as holder:
        b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',time.monotonic())
        with a.transaction(holder,b,ctx):
            a.execute(holder,b,'SELECT id FROM sample.record WHERE id=CAST(:id AS uuid) FOR UPDATE',{'id':record})
            with pytest.raises(a.WriteError,match='^internal_error$'):
                call(databases,document(ORG,ACCOUNT,record,1,3),str(uuid4()))
    assert state(databases,record)[1]==(0,0)


def test_safe_sql_and_commit_errors_and_post_response_deadline(monkeypatch):
    canary='sensitive-sql-credential-canary'
    class Driver:autocommit=False
    class Connection:driver_connection=Driver()
    class Fake:
        connection=Connection()
        def in_transaction(self):return False
        def get_execution_options(self):return {}
        def get_isolation_level(self):return 'READ COMMITTED'
        def execute(self,*args):raise SQLAlchemyError(canary)
        def begin(self):return self
        def __enter__(self):return self
        def __exit__(self,*args):raise SQLAlchemyError(canary)
    for operation in [lambda:a.execute(Fake(),a.Budget(),'sensitive SQL'),
                      lambda:a.outcome_lock(Fake(),a.Budget(),a.OutcomeKey('sample',ORG,ACCOUNT,'record.edit',str(uuid4())),a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',time.monotonic()))]:
        with pytest.raises(a.WriteError) as error:operation()
        assert canary not in ''.join(traceback.format_exception(error.value))
        assert error.value.__suppress_context__
    class CommitFailure(Fake):
        def execute(self,*args):return None
    with pytest.raises(a.WriteError,match='^internal_error$') as error:
        with a.transaction(CommitFailure(),a.Budget(),a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',time.monotonic())):pass
    assert canary not in ''.join(traceback.format_exception(error.value))
    budget=a.Budget()
    class LateResponse(Fake):
        calls=0
        def execute(self,*args):
            self.calls+=1
            if self.calls==2:budget.deadline=time.monotonic()-1
    with pytest.raises(a.WriteError,match='^execution_timeout$'):a.execute(LateResponse(),budget,'SELECT 1')


def test_late_commit_acknowledgement_retains_uncertainty():
    budget=a.Budget();events=[]
    class Driver:autocommit=False
    class Connection:driver_connection=Driver()
    class LateCommit:
        connection=Connection()
        def in_transaction(self):return False
        def get_execution_options(self):return {}
        def get_isolation_level(self):return 'READ COMMITTED'
        def execute(self,*args):pass
        def begin(self):return self
        def __enter__(self):return self
        def __exit__(self,*args):
            events.append('durably_committed')
            budget.deadline=time.monotonic()-1
    with pytest.raises(a.WriteError,match='^execution_timeout$'):
        with a.transaction(LateCommit(),budget,a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',time.monotonic())):
            events.append('business_effects')
    assert events==['business_effects','durably_committed']


def test_actual_transaction_timeout_rolls_back_and_releases_lock_while_owner_idle(databases,record):
    from threading import Event
    idle=Event();resume=Event();owner_resumed=Event()
    key=a.OutcomeKey('sample',ORG,ACCOUNT,'record.edit',str(uuid4()))
    before=state(databases,record)
    def owner():
        try:
            with databases['runtime'].connect() as c:
                b=a.Budget();b.deadline=time.monotonic()+0.25
                ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',time.monotonic())
                with a.transaction(c,b,ctx):
                    a.outcome_lock(c,b,key,ctx)
                    pid=a.execute(c,b,'SELECT pg_backend_pid()').scalar_one()
                    a.execute(c,b,'UPDATE sample.record SET value=77 WHERE id=CAST(:id AS uuid)',{'id':record})
                    idle.pid=pid;idle.set()
                    assert resume.wait(timeout=2), 'atomic_idle_owner_resume_missing'
                    owner_resumed.set()
        except a.WriteError as error:
            return str(error)
    with ThreadPoolExecutor(max_workers=1) as pool:
        pending=pool.submit(owner)
        try:
            assert idle.wait(timeout=1), 'atomic_idle_owner_not_ready'
            deadline=time.monotonic()+1.1
            with databases['runtime'].connect() as observer:
                while True:
                    acquired=observer.execute(text('SELECT pg_try_advisory_xact_lock(:key)'),{'key':a.outcome_lock_key(key)}).scalar_one()
                    if acquired:
                        # Still-idle owner has not run another statement or exited.
                        assert not owner_resumed.is_set()
                        assert observer.execute(text('SELECT count(*) FROM pg_stat_activity WHERE pid=:pid'),{'pid':idle.pid}).scalar_one()==0
                        observer.rollback()
                        break
                    observer.rollback()
                    assert time.monotonic()<deadline, 'transaction_timeout_did_not_release_lock'
                    time.sleep(0.01)
            assert state(databases,record)==before
        finally:
            resume.set()
        assert pending.result(timeout=2) in ('internal_error','execution_timeout')
    with databases['runtime'].connect() as usable:
        assert usable.execute(text('SELECT 1')).scalar_one()==1
        usable.rollback()


def test_existing_installer_copied_candidate_executes_and_replay_preserves(databases,record,tmp_path,monkeypatch):
    import importlib.util
    from test_command_fingerprint import run_installer
    node=os.environ.get('FINGERPRINT_TEST_NODE')
    assert node and Path(node).is_file(), 'FINGERPRINT_TEST_NODE must name explicit prepared Node'
    source=tmp_path/'candidate';source.mkdir()
    names=['atomic_write.py','command_fingerprint.py','first_committed_write.py']
    initial={name:(EXAMPLE/name).read_bytes() for name in names}
    for name,data in initial.items():(source/name).write_bytes(data)
    output=tmp_path/'owner'
    script=tmp_path/'install.mjs'
    script.write_text('''let installer;
try { installer=await import(INSTALLER); }
catch { console.error('fingerprint_fixture_import:module_load_failed'); process.exit(1); }
const [repositoryRoot,output]=process.argv.slice(2);
try {
 installer.installScaffold(output,{'base.txt':{classification:'generated',content:'base'}},
 {generator:'builder-v1',template:'application-v1-candidate',recipe:'a'.repeat(64),source:'b'.repeat(64)},
 undefined,{repositoryRoot,declarations:[{source:'candidate',destination:'api/custom'}]});
 installer.checkScaffold(output);
} catch {console.error('fingerprint_fixture_scaffold:scaffold_failed');process.exit(1);}
'''.replace('INSTALLER',json.dumps((BUILDER/'src/scaffold-install.ts').as_uri())))
    def install():run_installer([node,str(script),str(tmp_path),str(output)])
    install();copied=output/'api/custom'
    manifest_path=output/'.generated-files.json';provenance=manifest_path.read_bytes()
    manifest=json.loads(provenance)
    for name,data in initial.items():
        assert (copied/name).read_bytes()==data
        assert manifest['extensions']['imports'][0]['files'][name]==hashlib.sha256(data).hexdigest()
    def load(path,name):
        spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules,name,module);spec.loader.exec_module(module);return module
    monkeypatch.syspath_prepend(str(copied));monkeypatch.delitem(sys.modules,'command_fingerprint')
    monkeypatch.delitem(sys.modules,'atomic_write')
    monkeypatch.delitem(sys.modules,'first_committed_write')
    installed=load(copied/'first_committed_write.py','first_committed_write')
    owner=load(Path(__file__).with_name('first_committed_sample.py'),'installed_sample_owner')
    with databases['runtime'].connect() as c:
        result=owner.run(c,document(ORG,ACCOUNT,record,1,5),str(uuid4()),actor=ACTOR,authorize=lambda target,command,t:True)
        assert result['result']=={'record_id':record,'revision':'2'}
    assert sys.modules['command_fingerprint'].__file__==str(copied/'command_fingerprint.py')
    edited=initial['first_committed_write.py']+b'\n# Owner extension\nOWNER_EXTENSION=True\n'
    (copied/'first_committed_write.py').write_bytes(edited);(copied/'owner.txt').write_text('preserved')
    shutil.rmtree(source);install()
    assert (copied/'first_committed_write.py').read_bytes()==edited
    assert (copied/'owner.txt').read_text()=='preserved'
    assert manifest_path.read_bytes()==provenance
    replay=load(copied/'first_committed_write.py','replay_candidate')
    assert replay.OWNER_EXTENSION
    with databases['runtime'].connect() as c:
        b=replay.Budget();ctx=replay.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_read',time.monotonic())
        with replay.transaction(c,b,ctx):
            assert replay.execute(c,b,'SELECT revision FROM sample.record WHERE id=CAST(:id AS uuid)',{'id':record}).scalar_one()==2


def test_raced_stored_target_denial_and_original_budget(databases,record):
    other=str(uuid4());op=str(uuid4());checks=[]
    with databases['runtime'].connect() as c:
        def authorize(target,command,timeout):
            assert not c.in_transaction();checks.append(target)
            if len(checks)==1:
                call(databases,document(ORG,ACCOUNT,other,0,6),op,command='record.create')
                return True
            return False
        with pytest.raises(a.WriteError,match='^access_denied$'):
            run(c,document(ORG,ACCOUNT,str(uuid4()),0,9),op,actor=ACTOR,authorize=authorize,command='record.create')
        assert checks[-1]==other and len(checks)==2 and not c.in_transaction()
    assert state(databases,other)[1]==(1,1)
    # A raced target cannot reset the original execution deadline.
    budget=a.Budget();checks=[];op=str(uuid4());other=str(uuid4())
    with databases['runtime'].connect() as c:
        def expires(target,command,timeout):
            assert not c.in_transaction();checks.append(target)
            if len(checks)==1:
                call(databases,document(ORG,ACCOUNT,other,0,6),op,command='record.create')
                return True
            budget.deadline=time.monotonic()-1
            return True
        with pytest.raises(a.WriteError,match='^execution_timeout$'):
            run(c,document(ORG,ACCOUNT,str(uuid4()),0,9),op,actor=ACTOR,authorize=expires,command='record.create',budget=budget)
        assert len(checks)==2 and not c.in_transaction()
    assert state(databases,other)[1]==(1,1)


def test_changed_edit_bodies_race_has_one_complete_winner(databases,record):
    from threading import Barrier
    gate=Barrier(2);op=str(uuid4())
    def attempt(value):
        with databases['runtime'].connect() as c:
            def authorize(target,command,timeout):
                assert not c.in_transaction();gate.wait(timeout=2);return True
            return run(c,document(ORG,ACCOUNT,record,1,value),op,actor=ACTOR,authorize=authorize)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first=pool.submit(attempt,11);second=pool.submit(attempt,12)
        receipts=[first.result(timeout=7),second.result(timeout=7)]
    assert receipts[0]==receipts[1] and receipts[0]['result']['revision']=='2'
    row,counts=state(databases,record)
    assert row[0] in (11,12) and counts==(1,1)
    with databases['runtime'].connect() as c:
        b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_read',time.monotonic())
        with a.transaction(c,b,ctx):
            evidence=a.execute(c,b,'SELECT value,revision FROM sample.revision WHERE record_id=CAST(:id AS uuid)',dict(id=record)).one()
            assert tuple(evidence)==row[:2]


def test_same_uuid_isolated_by_exact_org_account_command(databases):
    op=str(uuid4());results=[]
    for org,account in [(ORG,ACCOUNT),(str(uuid4()),ACCOUNT),(ORG,str(uuid4()))]:
        target=str(uuid4());doc=document(org,account,target,0,1)
        created=call(databases,doc,op,command='record.create')
        assert created['result']['record_id']==target
        # Same UUID is a distinct edit operation, producing its own no-op receipt.
        edited=call(databases,document(org,account,target,1,1),op)
        assert edited['command_type']=='record.edit'
        results.append(created)
    assert len({r['result']['record_id'] for r in results})==3


@pytest.mark.parametrize('field,value',[
    ('org_id',None),('org_id',[]),('org_id','00000000-0000-0000-0000-000000000000'),
    ('executor_account_id','bad'),('command_version',True),('command_version',3),
    ('payload',[]),('payload',None)])
def test_malformed_command_never_reaches_authority(field,value):
    doc=document(ORG,ACCOUNT,str(uuid4()),1,2);doc[field]=value;calls=[]
    with pytest.raises(a.WriteError,match='^invalid_command$'):
        run(None,doc,str(uuid4()),actor=ACTOR,authorize=lambda *args:calls.append(args))
    assert not calls


def test_authorization_transport_exception_is_safe_and_atomic(databases,record):
    canary='private-authority-token-and-response-canary'
    before=state(databases,record);op=str(uuid4())
    with databases['runtime'].connect() as c:
        def broken(*args):raise RuntimeError(canary)
        with pytest.raises(a.WriteError,match='^authorization_unavailable$') as error:
            run(c,document(ORG,ACCOUNT,record,1,7),op,actor=ACTOR,authorize=broken)
        assert error.value.__suppress_context__
        assert canary not in ''.join(traceback.format_exception(error.value))
        assert not c.in_transaction()
    assert state(databases,record)==before


def target_counts(databases,target,operation):
    """Read exact attempted target and operation under its real authorized context."""
    with databases['runtime'].connect() as c:
        b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_read',time.monotonic())
        with a.transaction(c,b,ctx):
            return tuple(a.execute(c,b,statement,dict(id=target,op=operation)).scalar_one() for statement in (
                'SELECT count(*) FROM sample.record WHERE id=CAST(:id AS uuid)',
                'SELECT count(*) FROM sample.revision WHERE record_id=CAST(:id AS uuid) AND operation_id=CAST(:op AS uuid)',
                'SELECT count(*) FROM sample.outcome WHERE target_id=CAST(:id AS uuid) AND operation_id=CAST(:op AS uuid)'))


@pytest.mark.parametrize('command',['record.create','record.edit'])
def test_v2_original_receipt_survives_v1_duplicate(databases,record,command):
    target=str(uuid4()) if command=='record.create' else record;op=str(uuid4())
    original=call(databases,document(ORG,ACCOUNT,target,0 if command=='record.create' else 1,7,2),op,command=command)
    assert original['command_version']==2
    assert call(databases,document(ORG,ACCOUNT,str(uuid4()),777,99,1),op,command=command)==original
    assert state(databases,target)[1]==(1,1)


def test_valid_json_decodes_and_executes_native_create_replay(databases):
    target=str(uuid4());op=str(uuid4());doc=document(ORG,ACCOUNT,target,0,7)
    wire=json.dumps(doc,separators=(',',':')).encode()
    parsed=a.parse_json(wire)
    assert parsed==doc
    original=call(databases,parsed,op,command='record.create')
    changed=a.parse_json(json.dumps(document(ORG,ACCOUNT,str(uuid4()),8,99,2)).encode())
    assert call(databases,changed,op,command='record.create')==original
    assert target_counts(databases,target,op)==(1,1,1)


def test_linkage_fk_rejects_unrelated_operation_and_existing_target(databases,record):
    # An unused no-op outcome avoids UNIQUE(outcome_id) masking either FK assertion.
    op=str(uuid4());call(databases,document(ORG,ACCOUNT,record,1,0),op)
    other=str(uuid4());call(databases,document(ORG,ACCOUNT,other,0,4),str(uuid4()),command='record.create')
    with databases['runtime'].connect() as c:
        b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_read',time.monotonic())
        with a.transaction(c,b,ctx):
            outcome=a.execute(c,b,'SELECT id FROM sample.outcome WHERE operation_id=CAST(:op AS uuid)',dict(op=op)).scalar_one()
    for target,operation in [(record,str(uuid4())),(other,op)]:
        args=dict(org=ORG,target=target,owner=ACCOUNT,actor=ACTOR,op=operation,outcome=outcome)
        with databases['runtime'].connect() as c:
            b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',time.monotonic())
            with pytest.raises(a.WriteError,match='^internal_error$') as error:
                with a.transaction(c,b,ctx):
                    a.execute(c,b,"""INSERT INTO sample.revision(org_id,record_id,owner_account_id,revision,value,
                      executor_account_id,executor_actor_id,command_type,operation_id,outcome_id)
                      VALUES(CAST(:org AS uuid),CAST(:target AS uuid),CAST(:owner AS uuid),99,4,
                      CAST(:owner AS uuid),CAST(:actor AS uuid),'record.edit',CAST(:op AS uuid),CAST(:outcome AS uuid))""",args)
            driver=error.value.__context__.orig
            assert driver.sqlstate=='23503'
            assert driver.diag.constraint_name=='revision_outcome_id_org_id_executor_account_id_executor_ac_fkey'
    assert target_counts(databases,record,op)==(1,0,1)


def test_preparer_stages_exact_original_sources_and_preserves_prior_stage(tmp_path):
    from prepare_first_committed_write import stage
    first=stage(tmp_path/'attempt');second=stage(tmp_path/'attempt')
    assert first!=second and first.is_dir() and second.is_dir()
    for staged in (first,second):
        assert (staged/'prepare_atomic_write.py').read_bytes()==Path(__file__).with_name('prepare_atomic_write.py').read_bytes()
        assert (staged/'atomic_write_fixture.sql').read_bytes()==Path(__file__).with_name('first_committed_fixture.sql').read_bytes()
        assert json.loads((staged/'staged.json').read_text())['retained'] is True


def test_preparer_failure_is_safe_and_retains_staged_input(tmp_path):
    import subprocess
    private=tmp_path/'private.json';canary='private-preparation-canary'
    private.write_text(json.dumps({'admin_url':canary}))
    proof=tmp_path/'attempt'
    result=subprocess.run([sys.executable,'-I','-B',str(Path(__file__).with_name('prepare_first_committed_write.py')),
        '--admin',str(private),'--proof',str(proof)],capture_output=True,text=True)
    assert result.returncode==1
    assert result.stderr=='first_committed_fixture_preparation_failed\n'
    assert canary not in result.stdout+result.stderr
    assert proof.is_dir()
    staged=list(tmp_path.glob('attempt-preparer-*'))
    assert len(staged)==1 and (staged[0]/'staged.json').is_file()
