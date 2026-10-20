"""Additive active membership uniqueness and trusted reference custody."""
import importlib.util
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_identity_baseline as qualification


def test_active_index_is_exact_additive_migration():
    path=qualification.OWNER/'versions/0014_active_membership_index.py'
    spec=importlib.util.spec_from_file_location('active_membership_revision',path)
    revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
    assert revision.revision=='identity_0014' and revision.down_revision=='identity_0013'
    assert revision.ACTIVE_MEMBERSHIP_INDEX_SQL.strip()=='CREATE UNIQUE INDEX org_member_active_org_user_uidx ON identity.org_member USING btree (org_id, user_id) WHERE deleted_at IS NULL;'
    with pytest.raises(RuntimeError,match='Destructive'):revision.downgrade()


def test_active_index_required_head_preserves_historical13(monkeypatch):
    b=qualification.baseline
    assert b.ACTIVE_MEMBERSHIP_INDEX_REVISION=='identity_0014'
    monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.ACTIVE_MEMBERSHIP_INDEX_REVISION)
    seen=[];monkeypatch.setattr(b,'verify_catalog',lambda c,k:seen.append(k))
    b.verify_owned_postcondition(object(),require_head=True)
    assert seen==['active_membership_index']
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.MEMBERSHIP_RETIREMENT_REVISION)
    b.verify_owned_postcondition(object())
    assert seen[-1]=='membership_retirement'
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):b.verify_owned_postcondition(object(),require_head=True)


@pytest.mark.parametrize('mutation',[None,'identity_baseline.py','source-pins.json','reference.json','actor-reference.json',
    'projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json',
    'target-reference.json','profile-reference.json','legacy-role-reference.json','token-hook-reference.json','membership-binding-reference.json',
    'membership-retention-reference.json','membership-retirement-reference.json',
    'versions/0001_baseline.py','versions/0002_actor_registry.py','versions/0003_current_account_actor.py',
    'versions/0004_current_account_organization.py','versions/0005_operator_authority.py','versions/0006_actor_command.py',
    'versions/0007_organization_targets.py','versions/0008_profile_fields.py','versions/0009_legacy_roles.py',
    'versions/0010_token_hook.py','versions/0011_membership_binding.py','versions/0012_membership_retention.py',
    'versions/0013_membership_retirement.py','versions/0014_active_membership_index.py'])
def test_recorder_captures_every_source_and_checks_every_prior_catalog(tmp_path,monkeypatch,mutation):
    from test_actor_command_qualification import recorder
    from test_projection_qualification import digest
    import stat
    runner,statements=recorder(tmp_path,monkeypatch,mutation)
    (tmp_path/'identity_baseline.py').write_text('ACTIVE_MEMBERSHIP_INDEX_REFERENCE_SHA256 = None\n')
    for name in ['command-reference.json','target-reference.json','profile-reference.json','legacy-role-reference.json','token-hook-reference.json','membership-binding-reference.json','membership-retention-reference.json','membership-retirement-reference.json']:(tmp_path/name).write_text('{}')
    for number,name,symbol in [(7,'organization_targets','TARGET_SCHEMA_SQL'),(8,'profile_fields','PROFILE_FIELDS_SQL'),(9,'legacy_roles','LEGACY_ROLES_SQL'),(10,'token_hook','TOKEN_HOOK_SQL'),(11,'membership_binding','MEMBERSHIP_BINDING_SQL'),(12,'membership_retention','MEMBERSHIP_RETENTION_SQL'),(13,'membership_retirement','MEMBERSHIP_RETIREMENT_SQL'),(14,'active_membership_index','ACTIVE_MEMBERSHIP_INDEX_SQL')]:
        (tmp_path/f'versions/{number:04d}_{name}.py').write_text(f'{symbol} = "captured {name}"\n')
    runner.private={'owner_urls':{'active_membership_index_reference':'synthetic'}}
    b=qualification.baseline
    monkeypatch.setattr(b,'trusted_membership_retirement_reference',lambda:{})
    monkeypatch.setattr(b,'verify_target_roles',lambda *a,**k:None)
    monkeypatch.setattr(b,'verify_profile_privileges',lambda *a,**k:None)
    monkeypatch.setattr(b,'target_catalog_snapshot',lambda *a:{})
    monkeypatch.setattr(b,'IMPORTED_SOURCE_SHA256',digest((tmp_path/'identity_baseline.py').read_bytes()))
    helper=(tmp_path/'identity_baseline.py').read_bytes();catalogs=[]
    monkeypatch.setattr(b,'verify_catalog',lambda c,kind:catalogs.append(kind))
    deadline="SET LOCAL statement_timeout='60s'; SET LOCAL lock_timeout='5s'"
    preflights=[]
    def preflight(*args):
        assert statements[-1]==deadline
        preflights.append(len(statements));return 'clean'
    monkeypatch.setattr(b,'preflight',preflight)
    if mutation:
        with pytest.raises(AssertionError,match='active_membership_index_reference_source_changed'):runner.record_active_membership_index_reference()
        assert not (tmp_path/'active-membership-index-reference.json').exists()
    else:
        runner.record_active_membership_index_reference()
        assert (tmp_path/'identity_baseline.py').read_bytes()==helper
        assert runner.records[-1]['pin_update_required'] is True
        assert stat.S_IMODE((tmp_path/'active-membership-index-reference.json').stat().st_mode)==0o600
        with pytest.raises(AssertionError,match='already_exists'):runner.record_active_membership_index_reference()
    assert len(preflights)==2
    assert catalogs==['owned','actor','projection','organization','authority','command','target','profile','legacy_roles','token_hook','membership_binding','membership_retention','membership_retirement']
    assert statements==[deadline,'captured baseline','captured actor','captured projection','captured organization','captured authority','captured command',
        'captured organization_targets','captured profile_fields','captured legacy_roles','captured token_hook','captured membership_binding','captured membership_retention','captured membership_retirement','captured active_membership_index',deadline]


@pytest.mark.parametrize('defect',[None,'migration','missing_reference','modified_reference','source_pins'])
def test_trusted_reference_keeps_historical_chain_and_refuses_drift(tmp_path,monkeypatch,defect):
    import json
    from test_projection_qualification import digest
    b=qualification.baseline;calls=[]
    monkeypatch.setattr(b,'trusted_membership_retirement_reference',lambda:calls.append('retirement'))
    monkeypatch.setattr(b,'HERE',tmp_path)
    (tmp_path/'versions').mkdir();migration=tmp_path/'versions/0014_active_membership_index.py';migration.write_bytes(b'source')
    (tmp_path/'source-pins.json').write_text('{}')
    content=json.dumps({'source_pins':{},'migration_sha256':digest(b'source'),'active_membership_index':{}}).encode()
    path=tmp_path/'active-membership-index-reference.json';path.write_bytes(content)
    monkeypatch.setattr(b,'ACTIVE_MEMBERSHIP_INDEX_REFERENCE_SHA256',digest(content))
    if defect=='migration':migration.write_bytes(b'drift')
    elif defect=='missing_reference':path.unlink()
    elif defect=='modified_reference':path.write_bytes(content+b' ')
    elif defect=='source_pins':(tmp_path/'source-pins.json').write_text('{"changed":"pin"}')
    if defect:
        with pytest.raises(b.BaselineError,match='identity_reference_unavailable'):b.trusted_active_membership_index_reference()
    else:assert b.trusted_active_membership_index_reference()=={}
    assert calls==['retirement']


def test_prior_manifest_exact29_and_unchanged_retirement_writes():
    import qualify_active_membership_index as active
    import qualify_membership_retirement as retirement
    assert len(active.PREVIOUS_FILES)==29
    assert active.PREVIOUS_COMMIT=='0e460f65afd8e92c32b974412d0ea648f915eced'
    assert 'versions/0014_active_membership_index.py' not in active.PREVIOUS_FILES
    assert active.ActiveMembershipIndexQualification.writes is retirement.MembershipRetirementQualification.writes
    assert len(active.REQUIRED_CASES)==9 and 'active_membership_index_reference' in active.REQUIRED_CASES


@pytest.mark.parametrize('module,args',[('qualify_identity_baseline',['--record-active-membership-index-reference']),('qualify_active_membership_index',[])])
def test_optimized_execution_refused_before_fixture(module,args):
    import subprocess
    source="""import importlib,sys
sys.path.insert(0,sys.argv[1])
module=importlib.import_module(sys.argv[2])
module.fixture=lambda: (_ for _ in ()).throw(RuntimeError('fixture_reached'))
sys.argv=[module.__file__]+sys.argv[3:]
try:module.main()
except RuntimeError as error:
    if str(error) not in {'active_membership_index_reference_optimized_python_prohibited','active_membership_index_qualification_optimized_python_prohibited'}:raise RuntimeError('wrong_guard')
else:raise RuntimeError('missing_guard')
"""
    result=subprocess.run([sys.executable,'-I','-B','-O','-c',source,str(Path(__file__).resolve().parent),module,*args],capture_output=True,text=True,timeout=10)
    assert result.returncode==0 and result.stdout==result.stderr==''


def failure_fixture_mock(tmp_path,*,create_failure=False,cleanup_fails=False,initially_called=False):
    import qualify_active_membership_index as retirement
    import json
    runner=retirement.ActiveMembershipIndexQualification(tmp_path,{})
    state={'created':False,'called':initially_called};commands=[]
    def sql(case,statement,values=None):
        commands.append(statement)
        if statement.startswith('SELECT last_value,is_called'):
            assert state['created']
            return [(1,state['called'])]
        if statement.startswith('SELECT '):
            return [('event_trigger','synthetic_active_membership_index_failure'),
                ('function','synthetic_active_membership_index_failure'),
                ('sequence','synthetic_active_membership_index_failure_marker')] if state['created'] else []
        if statement.startswith('CREATE SEQUENCE'):
            paths=list(tmp_path.glob('active-membership-index-event-restoration-required-*.json'))
            assert len(paths)==1 and json.loads(paths[0].read_text())['before']==[]
            assert "WHEN TAG IN ('CREATE INDEX')" in statement
            assert statement.index("to_regclass('identity.org_member_active_org_user_uidx')")<statement.index('pg_catalog.nextval(')<statement.index("RAISE EXCEPTION USING ERRCODE='P0001'")
            assert 'GRANT USAGE ON SEQUENCE public.synthetic_active_membership_index_failure_marker TO identity_migrator;' in statement
            assert statement.count('GRANT ')==1
            state['created']=True
            if create_failure:raise RuntimeError('synthetic_create_after_commit')
        if statement.startswith('DROP EVENT TRIGGER'):
            assert 'DROP FUNCTION IF EXISTS public.synthetic_active_membership_index_failure()' in statement
            assert 'DROP SEQUENCE IF EXISTS public.synthetic_active_membership_index_failure_marker' in statement
            if cleanup_fails:raise RuntimeError('synthetic_cleanup_failed')
            state['created']=False
        return []
    runner.admin_sql=sql
    return runner,state,commands


@pytest.mark.parametrize('failure',['create_after_commit','body'])
def test_after_create_index_failure_fixture_restores_exact_objects(tmp_path,failure):
    import stat
    runner,state,commands=failure_fixture_mock(tmp_path,create_failure=failure=='create_after_commit')
    with pytest.raises(RuntimeError,match='synthetic_'):
        with runner.failure_fixture('failure'):raise RuntimeError('synthetic_body')
    assert state['created'] is False
    paths=list(tmp_path.glob('active-membership-index-event-restored-*.json'))
    assert len(paths)==1 and stat.S_IMODE(paths[0].stat().st_mode)==0o600


@pytest.mark.parametrize('signame',['SIGINT','SIGTERM'])
@pytest.mark.parametrize('cleanup_fails',[False,True])
def test_failure_fixture_signal_and_failed_cleanup_keep_witness(tmp_path,monkeypatch,signame,cleanup_fails):
    import qualify_active_membership_index as retirement
    signal=retirement.signal
    originals={signal.SIGINT:object(),signal.SIGTERM:object()};handlers=dict(originals)
    monkeypatch.setattr(signal,'getsignal',lambda sig:handlers[sig])
    monkeypatch.setattr(signal,'signal',lambda sig,handler:handlers.__setitem__(sig,handler))
    runner,state,commands=failure_fixture_mock(tmp_path,cleanup_fails=cleanup_fails)
    expected='synthetic_cleanup_failed' if cleanup_fails else 'profile_fixture_interrupted'
    with pytest.raises(RuntimeError,match=expected):
        with runner.failure_fixture('failure'):handlers[getattr(signal,signame)](getattr(signal,signame),None)
    assert handlers==originals
    assert len(list(tmp_path.glob('active-membership-index-event-restoration-required-*.json')))==1
    assert len(list(tmp_path.glob('active-membership-index-event-restored-*.json')))==(0 if cleanup_fails else 1)
    assert state['created'] is cleanup_fails


@pytest.mark.parametrize('kind',['event_trigger','function','sequence'])
def test_failure_fixture_refuses_preexisting_object_without_mutation(tmp_path,kind):
    import qualify_active_membership_index as retirement
    runner=retirement.ActiveMembershipIndexQualification(tmp_path,{})
    commands=[]
    def sql(case,statement,values=None):commands.append(statement);return [(kind,'synthetic_active_membership_index_failure')]
    runner.admin_sql=sql
    with pytest.raises(AssertionError,match='already_exists'):
        with runner.failure_fixture('failure'):raise AssertionError('body_reached')
    assert len(commands)==1 and commands[0].startswith('SELECT ')
    assert not list(tmp_path.glob('active-membership-index-event-*.json'))


@pytest.mark.parametrize('fired',[False,True])
def test_failure_marker_proves_injected_event_before_rollback_claim_and_restores(tmp_path,fired):
    import json
    runner,state,commands=failure_fixture_mock(tmp_path)
    def execute():
        with runner.failure_fixture('failure') as verify_fired:
            assert state['called'] is False
            state['called']=fired
            verify_fired()
    if fired:
        execute()
        witnesses=list(tmp_path.glob('active-membership-index-event-fired-*.json'))
        assert len(witnesses)==1
        assert json.loads(witnesses[0].read_text())=={'case':'failure','marker_before':[1,False],'marker_after':[1,True],'new_index_observed':True}
    else:
        with pytest.raises(AssertionError,match='failure_fixture_not_fired'):execute()
        assert not list(tmp_path.glob('active-membership-index-event-fired-*.json'))
    assert state['created'] is False
    assert len(list(tmp_path.glob('active-membership-index-event-restored-*.json')))==1


def test_failure_marker_cannot_start_called(tmp_path):
    runner,state,commands=failure_fixture_mock(tmp_path,initially_called=True)
    with pytest.raises(AssertionError,match='failure_marker_initially_called'):
        with runner.failure_fixture('failure'):raise AssertionError('body_reached')
    assert state['created'] is False
    assert len(list(tmp_path.glob('active-membership-index-event-restored-*.json')))==1




@pytest.mark.parametrize('defect',[None,'extra_index','missing_full','function_change','stale_binding','missing_relation','extra_relation','relation_name','relation_kind','relation_owner','relation_rls','relation_force_rls','relation_acl','relation_options'])
def test_compatibility_requires_exact_single_index_delta(tmp_path,monkeypatch,defect):
    import json
    import qualify_active_membership_index as active
    runner=active.ActiveMembershipIndexQualification(tmp_path,{})
    old={'indexes':[['org_member','full unique index',True,True]],'functions':[['same']],'relations':[['org_member','r','identity_migrator',False,False,'','']]}
    relation=['org_member_active_org_user_uidx','i','identity_migrator',False,False,'','']
    current=dict(old,indexes=old['indexes']+[active.INDEX_ROW],relations=old['relations']+[relation])
    witness={'binding':{'synthetic':'binding'},'head':'identity_0013','unchanged_data':True,
        'catalog':old,'full_unique':[[active.FULL_NAME,'UNIQUE (org_id, user_id)','full index',[]]],
        'retired_duplicates_refused':True,'active_seed_preserved':True}
    if defect=='extra_index':current['indexes']=current['indexes']+[['org_member','unapproved index',True,True]]
    elif defect=='missing_full':current['indexes']=[active.INDEX_ROW]
    elif defect=='function_change':current['functions']=[['changed']]
    elif defect=='stale_binding':witness['binding']={}
    elif defect=='missing_relation':current['relations']=old['relations']
    elif defect=='extra_relation':current['relations']=current['relations']+[['extra','i','identity_migrator',False,False,'','']]
    elif defect and defect.startswith('relation_'):
        field,value={'relation_name':(0,'wrong'),'relation_kind':(1,'r'),'relation_owner':(2,'postgres'),
            'relation_rls':(3,True),'relation_force_rls':(4,True),'relation_acl':(5,'unexpected grant'),
            'relation_options':(6,'unexpected option')}[defect]
        relation[field]=value
    (tmp_path/'active-membership-index-head13-characterization-synthetic.json').write_text(json.dumps(witness))
    runner.snapshot=lambda case:current
    runner.characterization_binding=lambda:{'synthetic':'binding'}
    runner.sql=lambda case,sql:[tuple(row) for row in witness['full_unique']]
    monkeypatch.setattr(active.baseline,'trusted_active_membership_index_reference',lambda:active.baseline.catalog_fingerprints(current))
    monkeypatch.setattr(active.baseline,'trusted_membership_retirement_reference',lambda:active.baseline.catalog_fingerprints(old))
    if defect:
        with pytest.raises(AssertionError):runner.compatibility()
    else:
        runner.compatibility()
        assert runner.records[-1]['full_unique_definition_dependencies_preserved'] is True


@pytest.mark.parametrize('administrator',[False,True])
def test_full_unique_witness_serializes_actual_sqlalchemy_rows(tmp_path,administrator):
    import json
    from sqlalchemy import create_engine,text
    import qualify_active_membership_index as active
    db=create_engine('sqlite://')
    try:
        with db.connect() as connection:
            rows=connection.execute(text("SELECT 'org_member_org_id_user_id_key', 'UNIQUE (org_id, user_id)', 'full index', NULL")).all()
        runner=active.ActiveMembershipIndexQualification(tmp_path,{})
        calls=[]
        def read(case,statement):
            calls.append((case,statement));return rows
        runner.admin_sql=read if administrator else lambda *a:pytest.fail('wrong administrator path')
        runner.sql=read if not administrator else lambda *a:pytest.fail('wrong owner path')
        normalized=runner.full_unique('characterization',administrator=administrator)
        path=runner.witness('full-unique-serialization',{'full_unique':normalized})
        assert json.loads(path.read_text())=={'full_unique':[[active.FULL_NAME,'UNIQUE (org_id, user_id)','full index',None]]}
        assert calls==[('characterization',active.FULL_SQL)]
    finally:db.dispose()


@pytest.mark.parametrize('refusal',[None,'verify_projection_role','verify_authority_roles','verify_command_role','verify_target_roles','verify_profile_privileges'])
def test_active_catalog_runs_each_guard_before_catalog_comparison(monkeypatch,refusal):
    b=qualification.baseline;calls=[]
    guards=['verify_projection_role','verify_authority_roles','verify_command_role','verify_target_roles','verify_profile_privileges']
    for name in guards:
        def guard(connection,name=name):
            calls.append(name)
            if name==refusal:raise b.BaselineError('synthetic_guard_refusal')
        monkeypatch.setattr(b,name,guard)
    monkeypatch.setattr(b,'target_catalog_snapshot',lambda c:calls.append('snapshot') or {'synthetic':[]})
    monkeypatch.setattr(b,'trusted_active_membership_index_reference',lambda:calls.append('trusted') or {})
    monkeypatch.setattr(b,'compare_catalog',lambda *a:calls.append('compare'))
    if refusal:
        with pytest.raises(b.BaselineError,match='synthetic_guard_refusal'):b.verify_catalog(object(),'active_membership_index')
        assert calls==guards[:guards.index(refusal)+1]
    else:
        b.verify_catalog(object(),'active_membership_index')
        assert calls==guards+['snapshot','trusted','compare']


@pytest.mark.parametrize('failure',['loser_startup','no_block','commit'])
def test_concurrency_failure_rolls_back_joins_worker_and_cleans_fixture(tmp_path,monkeypatch,failure):
    from contextlib import contextmanager
    from threading import Event,current_thread,main_thread
    import qualify_active_membership_index as active
    runner=active.ActiveMembershipIndexQualification(tmp_path,{'runtime_urls':{'clean':'synthetic'}})
    runner.inputs={'clean':{'spare_org':'synthetic-org','spare':'synthetic-account'}}
    runner.data_state=lambda case:{};runner.snapshot=lambda case:{}
    runner.sql=lambda case,statement,values=None:[(0,)] if 'count(*)' in statement else []
    released=Event();events=[];polls=[];sleeps=[]
    class Result:
        def __init__(self,value):self.value=value
        def scalar_one(self):return self.value
        def one(self):return self.value
    class Transaction:
        def __init__(self,lane):self.lane=lane;self.is_active=True
        def rollback(self):
            assert self.is_active
            self.is_active=False;events.append(self.lane+' rollback')
            if self.lane=='winner':released.set()
        def commit(self):
            events.append('commit attempted')
            raise RuntimeError('synthetic_commit_failure')
    class Connection:
        def __init__(self,lane):self.lane=lane
        def __enter__(self):return self
        def __exit__(self,*args):events.append(self.lane+' closed')
        def begin(self):return Transaction(self.lane)
        def execute(self,statement,values=None):
            sql=str(statement)
            if 'SET LOCAL' in sql and self.lane=='loser' and failure=='loser_startup':raise RuntimeError('synthetic_loser_startup')
            if 'session_user' in sql:return Result(('access_runtime','service_role'))
            if 'pg_backend_pid' in sql:return Result(10 if self.lane=='winner' else 11)
            if 'pg_blocking_pids' in sql:
                assert values=={'winner':10,'loser':11};polls.append(sql)
                return Result(failure=='commit')
            if sql.startswith(active.INSERT):
                if self.lane=='loser':
                    assert released.wait(2),'winner_not_released'
                    events.append('worker insert finished')
                return Result(99)
            return Result(None)
    class Database:
        def __init__(self,observer=False):self.observer=observer
        def connect(self):return Connection('observer' if self.observer else ('winner' if current_thread() is main_thread() else 'loser'))
        def dispose(self):events.append('admin disposed' if self.observer else 'runtime disposed')
    monkeypatch.setattr(active,'engine',lambda url:Database())
    runner.admin=lambda case:Database(observer=True)
    @contextmanager
    def execution(case):
        events.append('fixture entered')
        try:yield
        finally:
            assert 'loser rollback' in events and 'loser closed' in events
            assert 'runtime disposed' in events and 'admin disposed' in events
            events.append('fixture cleaned')
    runner.fixture_execution=execution
    # Advance only this module's observer clock; real worker synchronization stays Event-based.
    clock=iter(range(20))
    monkeypatch.setattr(active.time,'monotonic',lambda:next(clock))
    monkeypatch.setattr(active.time,'sleep',lambda duration:sleeps.append(duration))
    expected={'loser_startup':'synthetic_loser_startup','no_block':'block_not_observed','commit':'synthetic_commit_failure'}[failure]
    with pytest.raises((RuntimeError,AssertionError),match=expected):runner.concurrency()
    assert events.count('winner rollback')==events.count('loser rollback')==1
    assert events[-1]=='fixture cleaned'
    assert events.index('loser closed')<events.index('fixture cleaned')
    if failure!='loser_startup':assert events.index('winner rollback')<events.index('worker insert finished')<events.index('fixture cleaned')
    if failure=='no_block':
        assert polls and sleeps and all(0<=duration<=.02 for duration in sleeps)
        assert 'commit attempted' not in events
    if failure=='commit':assert polls and 'commit attempted' in events
    assert not list(tmp_path.glob('active-membership-index-concurrent-result-*.json'))


@pytest.mark.parametrize('command_failure',[False,True])
def test_blocked_ddl_holds_owner_lock_and_releases_on_refusal_or_error(tmp_path,monkeypatch,command_failure):
    import qualify_active_membership_index as active
    runner=active.ActiveMembershipIndexQualification(tmp_path,{'owner_urls':{'failure':'owner'}})
    runner.data_state=lambda case:{'rows':'unchanged'};runner.snapshot=lambda case:{'catalog':'unchanged'}
    runner.sql=lambda *args:[('identity_0013',)]
    events=[];locked=False
    class Transaction:
        def rollback(self):
            nonlocal locked
            locked=False;events.append('rollback')
    class Connection:
        def __enter__(self):return self
        def __exit__(self,*args):events.append('closed')
        def begin(self):return Transaction()
        def execute(self,statement):
            nonlocal locked
            if str(statement).startswith('LOCK TABLE'):
                assert str(statement)=='LOCK TABLE identity.org_member IN ROW EXCLUSIVE MODE'
                locked=True
    class Database:
        def connect(self):return Connection()
        def dispose(self):events.append('disposed')
    monkeypatch.setattr(active,'engine',lambda url:Database())
    clock=iter([0,5.2]);monkeypatch.setattr(active.time,'monotonic',lambda:next(clock))
    def command(label,case,expected):
        assert locked and case=='failure' and expected=='identity_migration_failed_requires_reconciliation'
        events.append('migration called')
        if command_failure:raise RuntimeError('synthetic_command_error')
    runner.command=command
    if command_failure:
        with pytest.raises(RuntimeError,match='synthetic_command_error'):runner.blocked_index_ddl()
    else:
        runner.blocked_index_ddl()
        assert list(tmp_path.glob('active-membership-index-blocked-ddl-restored-*.json'))
    assert events==['migration called','rollback','closed','disposed'] and not locked


def test_index_drift_uses_direct_preflight_and_restores_each_transaction(tmp_path,monkeypatch):
    import qualify_active_membership_index as active
    runner=active.ActiveMembershipIndexQualification(tmp_path,{'owner_urls':{'unsafe':'owner'}})
    catalog={'indexes':['exact'],'relations':['exact']};events=[];form=None
    runner.data_state=lambda case:{'rows':'unchanged'};runner.snapshot=lambda case:catalog
    runner.state=lambda c:{'rows':'unchanged'}
    runner.command=lambda *a,**k:pytest.fail('subprocess_migration_not_allowed')
    class Result:
        def scalar_one(self):return 'identity_0014'
    class Transaction:
        def rollback(self):
            nonlocal form
            events.append('rollback '+str(form));form=None
    class Connection:
        def __enter__(self):return self
        def __exit__(self,*args):events.append('closed')
        def begin(self):return Transaction()
        def rollback(self):events.append('read rollback')
        def execute(self,statement):
            nonlocal form
            sql=str(statement)
            if sql.startswith('DROP INDEX'):
                assert sql=='DROP INDEX identity.'+active.INDEX_NAME
                form='missing'
            if sql.startswith('CREATE UNIQUE INDEX'):
                assert 'WHERE deleted_at IS NOT NULL' in sql
                form='wrong_predicate'
            return Result()
    class Database:
        def connect(self):return Connection()
        def dispose(self):events.append('disposed')
    monkeypatch.setattr(active,'engine',lambda url:Database())
    def snapshot(connection):
        if form=='missing':return {'indexes':[],'relations':[]}
        if form=='wrong_predicate':return dict(catalog,indexes=['wrong predicate'])
        return catalog
    monkeypatch.setattr(active.baseline,'target_catalog_snapshot',snapshot)
    def preflight(connection,mode):
        assert mode=='clean' and form in {'missing','wrong_predicate'}
        events.append('preflight '+form)
        raise active.baseline.BaselineError('identity_catalog_mismatch:'+('indexes,relations' if form=='missing' else 'indexes'))
    monkeypatch.setattr(active.baseline,'preflight',preflight)
    runner.index_drift_refusal()
    assert events==['preflight missing','rollback missing','read rollback','preflight wrong_predicate','rollback wrong_predicate','read rollback','closed','disposed']
    assert form is None
