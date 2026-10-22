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
import atomic_write as a
from atomic_write_sample import document, run
from command_fingerprint import create_fingerprint

ORG=str(uuid4()); ACCOUNT=str(uuid4()); ACTOR=str(uuid4())
KEYS={'old':bytes(range(32)), 'new':bytes(range(32,64))}


def test_candidate_import():
    assert callable(a.outcome_lock_key)


@pytest.fixture(scope='session')
def databases():
    path=os.environ.get('ATOMIC_WRITE_FIXTURE')
    assert path and Path(path).is_file(), 'ATOMIC_WRITE_FIXTURE must name retained private fixture.json'
    prepared=json.loads((Path(path).parent/'prepared.json').read_text())
    assert prepared['sql_sha256']==hashlib.sha256(Path(__file__).with_name('atomic_write_fixture.sql').read_bytes()).hexdigest(), 'atomic_fixture_sql_changed_requires_fresh_fixture'
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
        return run(c,doc,op,actor=ACTOR,authorize=lambda d,t:True,keys=KEYS,**kwargs)


def state(databases,target):
    b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_read',time.monotonic())
    with databases['runtime'].connect() as c:
        with a.transaction(c,b,ctx):
            row=a.execute(c,b,'SELECT value,revision,created_by,updated_by,created_at,updated_at FROM sample.record WHERE id=CAST(:id AS uuid)',{'id':target}).one()
            counts=tuple(a.execute(c,b,f'SELECT count(*) FROM sample.{table} WHERE {column}=CAST(:id AS uuid)',{'id':target}).scalar_one()
                for table,column in [('outcome','target_id'),('revision','record_id')])
    return tuple(row),counts


def test_atomic_commit_lost_response_later_change_and_denied_recovery(databases,record):
    doc=document(ORG,ACCOUNT,record,1,3);op=str(uuid4())
    receipt=call(databases,doc,op)
    assert receipt=={'record_id':record,'revision':'2'}
    row,counts=state(databases,record)
    assert row[:4]==(3,2, __import__('uuid').UUID(ACTOR),__import__('uuid').UUID(ACTOR)) and counts==(1,1)
    assert row[5]>=row[4]
    call(databases,document(ORG,ACCOUNT,record,2,9),str(uuid4()))
    before=state(databases,record)
    assert call(databases,doc,op)==receipt
    assert call(databases,doc,op,lookup=True)==receipt
    assert state(databases,record)==before
    with databases['runtime'].connect() as c:
        for lookup in (False,True):
            with pytest.raises(a.WriteError,match='^access_denied$'):
                run(c,doc,op,actor=ACTOR,authorize=lambda d,t:False,keys=KEYS,lookup=lookup)
            assert not c.in_transaction()
    assert state(databases,record)==before


def test_changed_payload_missing_original_key_noop_and_unknown_result(databases,record):
    doc=document(ORG,ACCOUNT,record,1,0);op=str(uuid4())
    assert call(databases,doc,op)['revision']=='1'
    assert state(databases,record)[1]==(1,0)
    with pytest.raises(a.WriteError,match='^operation_payload_mismatch$'):
        call(databases,document(ORG,ACCOUNT,record,1,8),op)
    with databases['runtime'].connect() as c:
        with pytest.raises(a.WriteError,match='^operation_verification_unavailable$'):
            run(c,doc,op,actor=ACTOR,authorize=lambda d,t:True,keys={'new':KEYS['new']},active='new')
    assert state(databases,record)[1]==(1,0)
    fp=create_fingerprint(doc,key_id='old',key=KEYS['old'])
    for changes in [dict(command_version=2,result_version=1),dict(command_version=1,result_version=2)]:
        with pytest.raises(a.WriteError,match='^operation_verification_unavailable$'):
            a.verify_existing(doc,fp,keys=KEYS,**changes)


@pytest.mark.parametrize('failure',['evidence','outcome'])
def test_required_insert_failure_rolls_back_every_local_effect(databases,record,failure):
    before=state(databases,record)
    with pytest.raises(a.WriteError,match='^internal_error$') as error:
        call(databases,document(ORG,ACCOUNT,record,1,2),str(uuid4()),fail=failure)
    rendered=''.join(traceback.format_exception(error.value))
    # Static call-site source is expected in a Python traceback; dynamic bound
    # values and the underlying driver exception must remain suppressed.
    assert record not in rendered and ACTOR not in rendered and 'IntegrityError' not in rendered
    assert error.value.__suppress_context__
    assert state(databases,record)==before


def test_concurrent_same_key_and_different_key_revision_race(databases,record):
    def overlap(attempts):
        # Hold the actual domain row and witness both callers blocked concurrently.
        with ThreadPoolExecutor(max_workers=2) as pool:
            with databases['runtime'].connect() as holder:
                b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',time.monotonic())
                with a.transaction(holder,b,ctx):
                    a.execute(holder,b,'SELECT id FROM sample.record WHERE id=CAST(:id AS uuid) FOR UPDATE',{'id':record})
                    futures=[pool.submit(attempt) for attempt in attempts]
                    deadline=time.monotonic()+1.3
                    while True:
                        with databases['runtime'].connect() as observer:
                            blocked=observer.execute(text("SELECT count(*) FROM pg_stat_activity WHERE usename=current_user AND wait_event_type='Lock' AND pid<>pg_backend_pid()")).scalar_one()
                            observer.rollback()
                        if blocked>=2:break
                        assert time.monotonic()<deadline, 'atomic_concurrent_wait_not_witnessed'
                        time.sleep(0.01)
                return [future.result(timeout=6) for future in futures]
    doc=document(ORG,ACCOUNT,record,1,2);op=str(uuid4())
    results=overlap([lambda:call(databases,doc,op)]*2)
    assert results[0]==results[1]
    assert state(databases,record)[1]==(1,1)
    def attempt(value):
        try:return call(databases,document(ORG,ACCOUNT,record,2,value),str(uuid4()))
        except a.WriteError as error:return str(error)
    results=overlap([lambda:attempt(3),lambda:attempt(4)])
    assert sum(type(result) is dict for result in results)==1
    assert 'revision_conflict' in results
    assert state(databases,record)[1]==(2,2)


def test_exact_lock_vector_and_all_key_dimensions():
    key=a.OutcomeKey('sample',ORG,ACCOUNT,'record.edit',str(uuid4()))
    # Independent explicit canonical vector, not helper-produced serialization.
    canonical=('{'+'"caller_id":"'+ACCOUNT+'","caller_kind":"account","command_type":"record.edit",'
        '"lock_version":1,"operation_id":"'+key.operation_id+'","owner_schema":"sample",'
        '"scope_id":"'+ORG+'","scope_kind":"organization"}').encode()
    assert a.outcome_lock_key(key)==int.from_bytes(hashlib.sha256(canonical).digest()[:8],'big',signed=True)
    for changes in [dict(owner_schema='another'),dict(org_id=str(uuid4())),dict(account_id=str(uuid4())),
                    dict(command_type='record.adjust'),dict(operation_id=str(uuid4()))]:
        assert a.outcome_lock_key(replace(key,**changes))!=a.outcome_lock_key(key)


def test_reused_uuid_isolated_across_actual_org_account_command(databases,record):
    op=str(uuid4())
    call(databases,document(ORG,ACCOUNT,record,1,0),op)
    call(databases,document(ORG,ACCOUNT,record,1,0,'record.adjust'),op)
    for org,account in [(str(uuid4()),ACCOUNT),(ORG,str(uuid4()))]:
        target=str(uuid4());b=a.Budget();ctx=a.VerifiedContext(org,account,ACTOR,'own_write',time.monotonic())
        with databases['runtime'].connect() as c:
            with a.transaction(c,b,ctx):
                a.execute(c,b,"""INSERT INTO sample.record(id,org_id,owner_account_id,value,revision,created_by,updated_by)
                VALUES(CAST(:id AS uuid),CAST(:org AS uuid),CAST(:account AS uuid),0,1,CAST(:actor AS uuid),CAST(:actor AS uuid))""",dict(id=target,org=org,account=account,actor=ACTOR))
        assert call(databases,document(org,account,target,1,0),op)=={'record_id':target,'revision':'1'}
    assert state(databases,record)[1]==(2,0)


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


def test_outcome_lock_timeout_only_is_busy_and_budget_observation_bounds(databases,record):
    op=str(uuid4());doc=document(ORG,ACCOUNT,record,1,1)
    key=a.OutcomeKey('sample',ORG,ACCOUNT,'record.edit',op)
    with databases['runtime'].connect() as holder:
        holder.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':a.outcome_lock_key(key)})
        started=time.monotonic()
        with pytest.raises(a.WriteError,match='^operation_busy$'):
            call(databases,doc,op)
        assert 1.7<time.monotonic()-started<3.5
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


@pytest.mark.parametrize('field,value',[
    ('org_id',''),('account_id','00000000-0000-0000-0000-000000000000'),
    ('actor_id','unverified'),('mode','request_admin'),('observed_at',float('nan'))])
def test_unverified_context_refuses(field,value):
    args=dict(org_id=ORG,account_id=ACCOUNT,actor_id=ACTOR,mode='own_write',observed_at=time.monotonic());args[field]=value
    with pytest.raises(a.WriteError,match='^invalid_write_context$'):a.VerifiedContext(**args)


def test_wrong_mode_write_missing_actor_and_no_network_under_lock(databases,record):
    with databases['runtime'].connect() as c:
        for context in [a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_read',time.monotonic()),
                        a.VerifiedContext(ORG,ACCOUNT,str(uuid4()),'own_write',time.monotonic())]:
            with pytest.raises(a.WriteError,match='^internal_error$'):
                b=a.Budget()
                with a.transaction(c,b,replace(context,observed_at=time.monotonic())):
                    a.execute(c,a.Budget(),"""INSERT INTO sample.record(id,org_id,owner_account_id,value,revision,created_by,updated_by)
                        VALUES(CAST(:id AS uuid),CAST(:org AS uuid),CAST(:account AS uuid),0,1,CAST(:actor AS uuid),CAST(:actor AS uuid))""",
                        dict(id=str(uuid4()),org=ORG,account=ACCOUNT,actor=context.actor_id))
        events=[]
        def authorize(doc,timeout):
            assert not c.in_transaction() and 0<timeout<=3
            events.append('authorized')
            return True
        doc=document(ORG,ACCOUNT,record,1,2);op=str(uuid4())
        run(c,doc,op,actor=ACTOR,authorize=authorize,keys=KEYS)
        run(c,doc,op,actor=ACTOR,authorize=authorize,keys=KEYS,lookup=True)
        assert events==['authorized','authorized']


def test_stored_unsupported_metadata_and_structural_hmac_key_refuse(databases,record):
    # The migrator has INSERT, but FORCE RLS applies even to this table owner.
    doc=document(ORG,ACCOUNT,record,1,0);op=str(uuid4())
    b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',time.monotonic())
    args=dict(id=str(uuid4()),org=ORG,account=ACCOUNT,actor=ACTOR,op=op,target=record,
              digest=bytes(32),result=json.dumps({'record_id':record,'revision':'1'}))
    insert="""INSERT INTO sample.outcome(id,org_id,executor_account_id,executor_actor_id,
    command_type,operation_id,command_version,fingerprint_version,fingerprint_algorithm,fingerprint_key_id,
    fingerprint,result_version,result,target_id) VALUES(CAST(:id AS uuid),CAST(:org AS uuid),CAST(:account AS uuid),
    CAST(:actor AS uuid),'record.edit',CAST(:op AS uuid),1,2,'hmac-sha256',:key,:digest,1,CAST(:result AS jsonb),CAST(:target AS uuid))"""
    with databases['migrator'].connect() as c:
        with pytest.raises(a.WriteError,match='^internal_error$'):
            with a.transaction(c,b,ctx):a.execute(c,b,insert,dict(args,key=None))
    with databases['runtime'].connect() as c:
        b=a.Budget();ctx=replace(ctx,observed_at=time.monotonic())
        with a.transaction(c,b,ctx):a.execute(c,b,insert,dict(args,key='old'))
    before=state(databases,record)
    with pytest.raises(a.WriteError,match='^operation_verification_unavailable$'):call(databases,doc,op)
    assert state(databases,record)==before


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


def test_existing_installer_copied_candidate_executes_and_replay_preserves(databases,record,tmp_path,monkeypatch):
    import importlib.util
    from test_command_fingerprint import run_installer
    node=os.environ.get('FINGERPRINT_TEST_NODE')
    assert node and Path(node).is_file(), 'FINGERPRINT_TEST_NODE must name explicit prepared Node'
    source=tmp_path/'candidate';source.mkdir()
    names=['atomic_write.py','command_fingerprint.py']
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
    installed=load(copied/'atomic_write.py','atomic_write')
    owner=load(Path(__file__).with_name('atomic_write_sample.py'),'installed_sample_owner')
    with databases['runtime'].connect() as c:
        result=owner.run(c,document(ORG,ACCOUNT,record,1,5),str(uuid4()),actor=ACTOR,authorize=lambda d,t:True,keys=KEYS)
        assert result=={'record_id':record,'revision':'2'}
    assert sys.modules['command_fingerprint'].__file__==str(copied/'command_fingerprint.py')
    edited=initial['atomic_write.py']+b'\n# Owner extension\nOWNER_EXTENSION=True\n'
    (copied/'atomic_write.py').write_bytes(edited);(copied/'owner.txt').write_text('preserved')
    shutil.rmtree(source);install()
    assert (copied/'atomic_write.py').read_bytes()==edited
    assert (copied/'owner.txt').read_text()=='preserved'
    assert manifest_path.read_bytes()==provenance
    replay=load(copied/'atomic_write.py','replay_candidate')
    assert replay.OWNER_EXTENSION
    with databases['runtime'].connect() as c:
        b=replay.Budget();ctx=replay.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_read',time.monotonic())
        with replay.transaction(c,b,ctx):
            assert replay.execute(c,b,'SELECT revision FROM sample.record WHERE id=CAST(:id AS uuid)',{'id':record}).scalar_one()==2


def test_owner_rejects_invalid_normalized_command_before_authority():
    from copy import deepcopy
    base=document(ORG,ACCOUNT,str(uuid4()),1,2)
    cases=[]
    for field,value in [('command_version',True),('command_version',2),('command_type','unknown')]:
        changed=deepcopy(base);changed[field]=value;cases.append(changed)
    for field,value in [('expected_revision','01'),('expected_revision','0'),('expected_revision','9'*20),
                        ('value',True),('value',2**31)]:
        changed=deepcopy(base);changed['payload'][field]=value;cases.append(changed)
    for changed in cases:
        called=[]
        with pytest.raises(a.WriteError):
            run(None,changed,str(uuid4()),actor=ACTOR,authorize=lambda d,t:called.append(True),keys=KEYS)
        assert called==[]


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


def test_in_budget_observation_expiry_and_fresh_acceptance(monkeypatch):
    now=[100.0]
    monkeypatch.setattr(a.time,'monotonic',lambda:now[0])
    budget=a.Budget()
    old=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',100.1)
    now[0]=101.2
    with pytest.raises(a.WriteError,match='^authorization_observation_expired$'):
        budget.local_start(old)
    budget.local_start(replace(old,observed_at=101.1))


def test_fixed_historical_lock_v1_literal():
    key=a.OutcomeKey('sample','11111111-1111-4111-8111-111111111111',
                     '22222222-2222-4222-8222-222222222222','record.edit',
                     '33333333-3333-4333-8333-333333333333')
    assert a.outcome_lock_key(key)==-5169148205731144946


@pytest.mark.parametrize('keys,active', [({},'old'),({'old':b'short'},'old'),
    ({'old':bytearray(32)},'old'),(None,'old'),(KEYS,[])])
def test_missing_bad_active_key_rolls_back_tentative_mutation(databases,record,keys,active):
    before=state(databases,record)
    with databases['runtime'].connect() as c:
        with pytest.raises(a.WriteError,match='^operation_verification_unavailable$') as error:
            run(c,document(ORG,ACCOUNT,record,1,22),str(uuid4()),actor=ACTOR,
                authorize=lambda d,t:True,keys=keys,active=active)
    assert error.value.__suppress_context__ or keys is None
    assert state(databases,record)==before


def test_malformed_shapes_ids_never_invoke_authority():
    from copy import deepcopy
    base=document(ORG,ACCOUNT,str(uuid4()),1,2)
    cases=[(None,str(uuid4())),([],str(uuid4())),('private',str(uuid4()))]
    for payload in (None,[],['record_id'],3):
        doc=deepcopy(base);doc['payload']=payload;cases.append((doc,str(uuid4())))
    for name in ('org_id','executor_account_id'):
        for value in (None,[],1,'malformed','00000000-0000-0000-0000-000000000000'):
            doc=deepcopy(base);doc[name]=value;cases.append((doc,str(uuid4())))
    for operation in (None,[],1,'malformed','00000000-0000-0000-0000-000000000000'):
        cases.append((base,operation))
    for doc,operation in cases:
        called=[]
        with pytest.raises(a.WriteError):
            run(None,doc,operation,actor=ACTOR,authorize=lambda d,t:called.append(True),keys=KEYS)
        assert called==[]


def test_two_existing_records_and_foreign_owner_cannot_reuse_outcome(databases,record):
    # A no-op outcome has no revision, so UNIQUE(outcome_id) cannot mask either
    # the target FK or the independent original-owner INSERT policy under test.
    call(databases,document(ORG,ACCOUNT,record,1,0),str(uuid4()))
    b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_read',time.monotonic())
    with databases['runtime'].connect() as c:
        with a.transaction(c,b,ctx):
            outcome=dict(a.execute(c,b,'SELECT * FROM sample.outcome WHERE target_id=CAST(:id AS uuid)',{'id':record}).mappings().one())
    for owner in (ACCOUNT,str(uuid4())):
        other=str(uuid4());b=a.Budget();ctx=a.VerifiedContext(ORG,owner,ACTOR,'own_write',time.monotonic())
        with databases['runtime'].connect() as c:
            with a.transaction(c,b,ctx):
                a.execute(c,b,"""INSERT INTO sample.record(id,org_id,owner_account_id,value,revision,created_by,updated_by)
                  VALUES(CAST(:id AS uuid),CAST(:org AS uuid),CAST(:owner AS uuid),0,1,CAST(:actor AS uuid),CAST(:actor AS uuid))""",
                  dict(id=other,org=ORG,owner=owner,actor=ACTOR))
            values=dict(id=uuid4(),org_id=ORG,record_id=other,owner_account_id=owner,
                revision=2,value=4,executor_account_id=ACCOUNT,executor_actor_id=ACTOR,
                command_type=outcome['command_type'],operation_id=outcome['operation_id'],outcome_id=outcome['id'])
            b=a.Budget();ctx=a.VerifiedContext(ORG,ACCOUNT,ACTOR,'own_write',time.monotonic())
            with pytest.raises(a.WriteError,match='^internal_error$') as error:
                with a.transaction(c,b,ctx):
                    columns=','.join(values);params=','.join(':'+key for key in values)
                    a.execute(c,b,f'INSERT INTO sample.revision({columns}) VALUES({params})',values)
            # Inspect driver classification privately; never print driver details.
            driver=error.value.__context__.orig
            assert driver.sqlstate==('23503' if owner==ACCOUNT else '42501')
            if owner==ACCOUNT:
                assert driver.diag.table_name=='revision'
                assert 'outcome' in driver.diag.constraint_name
    assert state(databases,record)[1]==(1,0)


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


def test_unresolved_and_foreign_lookup_do_not_prevent_later_commit(databases,record):
    doc=document(ORG,ACCOUNT,record,1,6);op=str(uuid4())
    before=state(databases,record)
    assert call(databases,doc,op,lookup=True) is None
    for org,account in [(str(uuid4()),ACCOUNT),(ORG,str(uuid4()))]:
        foreign=document(org,account,record,1,6)
        assert call(databases,foreign,op,lookup=True) is None
    assert state(databases,record)==before
    result=call(databases,doc,op)
    assert result=={'record_id':record,'revision':'2'}
    assert call(databases,doc,op,lookup=True)==result
    assert state(databases,record)[1]==(1,1)
