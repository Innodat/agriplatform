"""Staged membership actor reference custody and release checks."""
import importlib.util
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_identity_baseline as qualification


def test_new_head_preserves_previous_index_catalog(monkeypatch):
    b=qualification.baseline
    assert b.MEMBERSHIP_ACTOR_ATTRIBUTION_REVISION=='identity_0015'
    monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.MEMBERSHIP_ACTOR_ATTRIBUTION_REVISION)
    seen=[];monkeypatch.setattr(b,'verify_catalog',lambda c,k:seen.append(k))
    b.verify_owned_postcondition(object(),require_head=True)
    assert seen==['membership_actor_attribution']
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.ACTIVE_MEMBERSHIP_INDEX_REVISION)
    b.verify_owned_postcondition(object())
    assert seen[-1]=='active_membership_index'
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):b.verify_owned_postcondition(object(),require_head=True)


@pytest.mark.parametrize('mutation',[None,'identity_baseline.py','source-pins.json','reference.json','actor-reference.json',
    'projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json',
    'target-reference.json','profile-reference.json','legacy-role-reference.json','token-hook-reference.json','membership-binding-reference.json',
    'membership-retention-reference.json','membership-retirement-reference.json','active-membership-index-reference.json',
    'versions/0001_baseline.py','versions/0002_actor_registry.py','versions/0003_current_account_actor.py',
    'versions/0004_current_account_organization.py','versions/0005_operator_authority.py','versions/0006_actor_command.py',
    'versions/0007_organization_targets.py','versions/0008_profile_fields.py','versions/0009_legacy_roles.py',
    'versions/0010_token_hook.py','versions/0011_membership_binding.py','versions/0012_membership_retention.py',
    'versions/0013_membership_retirement.py','versions/0014_active_membership_index.py','versions/0015_membership_actor_attribution.py'])
def test_recorder_captures_every_source_and_checks_every_prior_catalog(tmp_path,monkeypatch,mutation):
    from test_actor_command_qualification import recorder
    from test_projection_qualification import digest
    import stat
    runner,statements=recorder(tmp_path,monkeypatch,mutation)
    (tmp_path/'identity_baseline.py').write_text('MEMBERSHIP_ACTOR_ATTRIBUTION_REFERENCE_SHA256 = None\n')
    for name in ['command-reference.json','target-reference.json','profile-reference.json','legacy-role-reference.json','token-hook-reference.json','membership-binding-reference.json','membership-retention-reference.json','membership-retirement-reference.json','active-membership-index-reference.json']:(tmp_path/name).write_text('{}')
    for number,name,symbol in [(7,'organization_targets','TARGET_SCHEMA_SQL'),(8,'profile_fields','PROFILE_FIELDS_SQL'),(9,'legacy_roles','LEGACY_ROLES_SQL'),(10,'token_hook','TOKEN_HOOK_SQL'),(11,'membership_binding','MEMBERSHIP_BINDING_SQL'),(12,'membership_retention','MEMBERSHIP_RETENTION_SQL'),(13,'membership_retirement','MEMBERSHIP_RETIREMENT_SQL'),(14,'active_membership_index','ACTIVE_MEMBERSHIP_INDEX_SQL'),(15,'membership_actor_attribution','MEMBERSHIP_ACTOR_ATTRIBUTION_SQL')]:
        (tmp_path/f'versions/{number:04d}_{name}.py').write_text(f'{symbol} = "captured {name}"\n')
    runner.private={'owner_urls':{'membership_actor_attribution_reference':'synthetic'}}
    b=qualification.baseline
    monkeypatch.setattr(b,'trusted_active_membership_index_reference',lambda:{})
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
        with pytest.raises(AssertionError,match='membership_actor_attribution_reference_source_changed'):runner.record_membership_actor_attribution_reference()
        assert not (tmp_path/'membership-actor-attribution-reference.json').exists()
    else:
        runner.record_membership_actor_attribution_reference()
        assert (tmp_path/'identity_baseline.py').read_bytes()==helper
        assert runner.records[-1]['pin_update_required'] is True
        assert stat.S_IMODE((tmp_path/'membership-actor-attribution-reference.json').stat().st_mode)==0o600
        with pytest.raises(AssertionError,match='already_exists'):runner.record_membership_actor_attribution_reference()
    assert len(preflights)==2
    assert catalogs==['owned','actor','projection','organization','authority','command','target','profile','legacy_roles','token_hook','membership_binding','membership_retention','membership_retirement','active_membership_index']
    assert statements==[deadline,'captured baseline','captured actor','captured projection','captured organization','captured authority','captured command',
        'captured organization_targets','captured profile_fields','captured legacy_roles','captured token_hook','captured membership_binding','captured membership_retention','captured membership_retirement','captured active_membership_index','captured membership_actor_attribution',deadline]


@pytest.mark.parametrize('defect',[None,'migration','missing_reference','modified_reference','source_pins'])
def test_trusted_reference_keeps_historical_chain_and_refuses_drift(tmp_path,monkeypatch,defect):
    import json
    from test_projection_qualification import digest
    b=qualification.baseline;calls=[]
    monkeypatch.setattr(b,'trusted_active_membership_index_reference',lambda:calls.append('index'))
    monkeypatch.setattr(b,'HERE',tmp_path)
    (tmp_path/'versions').mkdir();migration=tmp_path/'versions/0015_membership_actor_attribution.py';migration.write_bytes(b'source')
    (tmp_path/'source-pins.json').write_text('{}')
    content=json.dumps({'source_pins':{},'migration_sha256':digest(b'source'),'membership_actor_attribution':{}}).encode()
    path=tmp_path/'membership-actor-attribution-reference.json';path.write_bytes(content)
    monkeypatch.setattr(b,'MEMBERSHIP_ACTOR_ATTRIBUTION_REFERENCE_SHA256',digest(content))
    if defect=='migration':migration.write_bytes(b'drift')
    elif defect=='missing_reference':path.unlink()
    elif defect=='modified_reference':path.write_bytes(content+b' ')
    elif defect=='source_pins':(tmp_path/'source-pins.json').write_text('{"changed":"pin"}')
    if defect:
        with pytest.raises(b.BaselineError,match='identity_reference_unavailable'):b.trusted_membership_actor_attribution_reference()
    else:assert b.trusted_membership_actor_attribution_reference()=={}
    assert calls==['index']


@pytest.mark.parametrize('module,args',[('qualify_identity_baseline',['--record-membership-actor-attribution-reference']),('qualify_membership_actor_attribution',[])])
def test_optimized_execution_refused_before_fixture(module,args):
    import subprocess
    source="""import importlib,sys
sys.path.insert(0,sys.argv[1])
module=importlib.import_module(sys.argv[2])
module.fixture=lambda: (_ for _ in ()).throw(RuntimeError('fixture_reached'))
sys.argv=[module.__file__]+sys.argv[3:]
try:module.main()
except RuntimeError as error:
    if str(error) not in {'membership_actor_attribution_reference_optimized_python_prohibited','membership_actor_attribution_qualification_optimized_python_prohibited'}:raise RuntimeError('wrong_guard')
else:raise RuntimeError('missing_guard')
"""
    result=subprocess.run([sys.executable,'-I','-B','-O','-c',source,str(Path(__file__).resolve().parent),module,*args],capture_output=True,text=True,timeout=10)
    assert result.returncode==0 and result.stdout==result.stderr==''


def failure_fixture_mock(tmp_path,*,create_failure=False,cleanup_fails=False,initially_called=False):
    import qualify_membership_actor_attribution as retirement
    import json
    runner=retirement.MembershipActorAttributionQualification(tmp_path,{})
    state={'created':False,'called':initially_called};commands=[]
    def sql(case,statement,values=None):
        commands.append(statement)
        if statement.startswith('SELECT last_value,is_called'):
            assert state['created']
            return [(1,state['called'])]
        if statement.startswith('SELECT '):
            return [('event_trigger','synthetic_membership_actor_attribution_failure'),
                ('function','synthetic_membership_actor_attribution_failure'),
                ('sequence','synthetic_membership_actor_attribution_failure_marker')] if state['created'] else []
        if statement.startswith('CREATE SEQUENCE'):
            paths=list(tmp_path.glob('membership-actor-attribution-event-restoration-required-*.json'))
            assert len(paths)==1 and json.loads(paths[0].read_text())['before']==[]
            assert "WHEN TAG IN ('CREATE TRIGGER')" in statement
            assert statement.index("to_regprocedure('identity.guard_org_member_actor_attribution()')")<statement.index('pg_catalog.nextval(')<statement.index("RAISE EXCEPTION USING ERRCODE='P0001'")
            assert 'GRANT USAGE ON SEQUENCE public.synthetic_membership_actor_attribution_failure_marker TO identity_migrator;' in statement
            assert statement.count('GRANT ')==1
            state['created']=True
            if create_failure:raise RuntimeError('synthetic_create_after_commit')
        if statement.startswith('DROP EVENT TRIGGER'):
            assert 'DROP FUNCTION IF EXISTS public.synthetic_membership_actor_attribution_failure()' in statement
            assert 'DROP SEQUENCE IF EXISTS public.synthetic_membership_actor_attribution_failure_marker' in statement
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
    paths=list(tmp_path.glob('membership-actor-attribution-event-restored-*.json'))
    assert len(paths)==1 and stat.S_IMODE(paths[0].stat().st_mode)==0o600


@pytest.mark.parametrize('signame',['SIGINT','SIGTERM'])
@pytest.mark.parametrize('cleanup_fails',[False,True])
def test_failure_fixture_signal_and_failed_cleanup_keep_witness(tmp_path,monkeypatch,signame,cleanup_fails):
    import qualify_membership_actor_attribution as retirement
    signal=retirement.signal
    originals={signal.SIGINT:object(),signal.SIGTERM:object()};handlers=dict(originals)
    monkeypatch.setattr(signal,'getsignal',lambda sig:handlers[sig])
    monkeypatch.setattr(signal,'signal',lambda sig,handler:handlers.__setitem__(sig,handler))
    runner,state,commands=failure_fixture_mock(tmp_path,cleanup_fails=cleanup_fails)
    expected='synthetic_cleanup_failed' if cleanup_fails else 'profile_fixture_interrupted'
    with pytest.raises(RuntimeError,match=expected):
        with runner.failure_fixture('failure'):handlers[getattr(signal,signame)](getattr(signal,signame),None)
    assert handlers==originals
    assert len(list(tmp_path.glob('membership-actor-attribution-event-restoration-required-*.json')))==1
    assert len(list(tmp_path.glob('membership-actor-attribution-event-restored-*.json')))==(0 if cleanup_fails else 1)
    assert state['created'] is cleanup_fails


@pytest.mark.parametrize('kind',['event_trigger','function','sequence'])
def test_failure_fixture_refuses_preexisting_object_without_mutation(tmp_path,kind):
    import qualify_membership_actor_attribution as retirement
    runner=retirement.MembershipActorAttributionQualification(tmp_path,{})
    commands=[]
    def sql(case,statement,values=None):commands.append(statement);return [(kind,'synthetic_membership_actor_attribution_failure')]
    runner.admin_sql=sql
    with pytest.raises(AssertionError,match='already_exists'):
        with runner.failure_fixture('failure'):raise AssertionError('body_reached')
    assert len(commands)==1 and commands[0].startswith('SELECT ')
    assert not list(tmp_path.glob('membership-actor-attribution-event-*.json'))


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
        witnesses=list(tmp_path.glob('membership-actor-attribution-event-fired-*.json'))
        assert len(witnesses)==1
        assert json.loads(witnesses[0].read_text())=={'case':'failure','marker_before':[1,False],'marker_after':[1,True],'new_guard_observed':True}
    else:
        with pytest.raises(AssertionError,match='failure_fixture_not_fired'):execute()
        assert not list(tmp_path.glob('membership-actor-attribution-event-fired-*.json'))
    assert state['created'] is False
    assert len(list(tmp_path.glob('membership-actor-attribution-event-restored-*.json')))==1


def test_failure_marker_cannot_start_called(tmp_path):
    runner,state,commands=failure_fixture_mock(tmp_path,initially_called=True)
    with pytest.raises(AssertionError,match='failure_marker_initially_called'):
        with runner.failure_fixture('failure'):raise AssertionError('body_reached')
    assert state['created'] is False
    assert len(list(tmp_path.glob('membership-actor-attribution-event-restored-*.json')))==1






def catalogue_fixture():
    from copy import deepcopy
    fields=('created_actor_id','updated_actor_id')
    old={'columns':[], 'constraints':[], 'functions':[], 'triggers':[], 'indexes':['unchanged']}
    prefixes=('', 'authority_', 'command_', 'projection_', 'target_')
    for prefix in prefixes:
        old[prefix+'effective_tables']=[['identity_migrator','org_member','SELECT',True],
                                      ['restricted','org_member','SELECT',False]]
        old[prefix+'effective_columns']=[['restricted','org_member','id','SELECT',False]]
        old[prefix+'effective_functions']=[['identity_migrator','identity','prior','',True],
                                         ['restricted','identity','prior','',False]]
    current=deepcopy(old)
    current['columns']=[['org_member',name,11+i,'uuid',False,'','','','',''] for i,name in enumerate(fields)]
    current['constraints']=[['org_member','org_member_'+prefix+'_actor_fk',
        'FOREIGN KEY ('+prefix+'_actor_id) REFERENCES identity.actor(id) ON DELETE RESTRICT',True,False,False]
        for prefix in ('created','updated')]
    current['functions']=[['identity','guard_org_member_actor_attribution','','identity_migrator',
                          'fixture definition','{identity_migrator=X/identity_migrator}']]
    current['triggers']=[['identity','org_member','org_member_actor_attribution_guard',
        'CREATE TRIGGER org_member_actor_attribution_guard BEFORE INSERT OR UPDATE ON identity.org_member FOR EACH ROW EXECUTE FUNCTION identity.guard_org_member_actor_attribution()','O']]
    for prefix in prefixes:
        current[prefix+'effective_columns'] += [[role,'org_member',field,'SELECT',allowed]
            for role,allowed in [('identity_migrator',True),('restricted',False)] for field in fields]
        current[prefix+'effective_functions'] += [[role,'identity','guard_org_member_actor_attribution','',allowed]
            for role,allowed in [('identity_migrator',True),('restricted',False)]]
    return old,current


@pytest.mark.parametrize('defect', [None, 'missing_false_column', 'extra_column_grant',
    'new_function_public', 'old_privilege_change', 'unrelated_category_change',
    'column_type','column_default','fk_target','trigger_scope','trigger_disabled',
    'function_body','function_owner','function_acl'])
def test_catalog_delta_accounts_for_exact_effective_observations(monkeypatch,defect):
    from hashlib import sha256
    import qualify_membership_actor_attribution as q
    old,current=catalogue_fixture()
    monkeypatch.setattr(q,'GUARD_FUNCTION_SHA256',sha256(b'fixture definition').hexdigest(),raising=False)
    if defect=='missing_false_column':current['effective_columns'].pop()
    if defect=='extra_column_grant':current['effective_columns'][-1][-1]=True
    if defect=='new_function_public':current['effective_functions'][-1][-1]=True
    if defect=='old_privilege_change':current['effective_columns'][0][-1]=True
    if defect=='unrelated_category_change':current['indexes'].append('unexpected')
    if defect=='column_type':current['columns'][0][3]='text'
    if defect=='column_default':current['columns'][0][7]="gen_random_uuid()"
    if defect=='fk_target':current['constraints'][0][2]=current['constraints'][0][2].replace('identity.actor','identity.users')
    if defect=='trigger_scope':current['triggers'][0][3]=current['triggers'][0][3].replace('INSERT OR UPDATE','INSERT')
    if defect=='trigger_disabled':current['triggers'][0][4]='D'
    if defect=='function_body':current['functions'][0][4]='changed definition'
    if defect=='function_owner':current['functions'][0][3]='postgres'
    if defect=='function_acl':current['functions'][0][5]='{=X/identity_migrator}'
    if defect:
        with pytest.raises(AssertionError):q.MembershipActorAttributionQualification.verify_catalog_delta(old,current)
    else:q.MembershipActorAttributionQualification.verify_catalog_delta(old,current)


@pytest.mark.parametrize('failure',['driver','assertion',None])
def test_entrypoint_never_prints_driver_sql_or_diagnostics(monkeypatch,capsys,failure):
    import qualify_membership_actor_attribution as q
    from sqlalchemy.exc import IntegrityError
    def main():
        if failure=='driver':raise IntegrityError('PRIVATE SQL',{'secret':'PRIVATE VALUE'},RuntimeError('PRIVATE DIAGNOSTIC'))
        if failure=='assertion':raise AssertionError('PRIVATE ASSERTION')
    monkeypatch.setattr(q,'main',main)
    assert q.entrypoint()==(1 if failure else 0)
    output=capsys.readouterr()
    assert output.out==''
    assert output.err==('membership_actor_attribution_qualification_failed\n' if failure else '')


@pytest.mark.parametrize('actual_constraint',['org_member_created_actor_fk','unrelated_fk'])
def test_fk_metadata_checked_without_matching_english_message(monkeypatch,actual_constraint):
    from types import SimpleNamespace
    from qualify_membership_binding import MembershipBindingQualification as Q
    monkeypatch.setattr(Q,'state',lambda _: {'unchanged':True})
    class Failure(RuntimeError):
        orig=SimpleNamespace(sqlstate='23503',diag=SimpleNamespace(constraint_name=actual_constraint))
    class Connection:
        rolled_back=False
        def begin_nested(self):return self
        def rollback(self):self.rolled_back=True
        def execute(self,*args):raise Failure()
    connection=Connection()
    if actual_constraint=='unrelated_fk':
        with pytest.raises(AssertionError):Q.reject(connection,'unused',{},'23503',None,'org_member_created_actor_fk')
    else:Q.reject(connection,'unused',{},'23503',None,'org_member_created_actor_fk')
    assert connection.rolled_back


def test_unknown_history_bounds_precede_ledger_mutation(monkeypatch,tmp_path):
    import qualify_membership_actor_attribution as q
    calls=[]
    class Connection:
        rolled=False
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def begin(self):return self
        def rollback(self):self.rolled=True
        def execute(self,statement,*args):calls.append(str(statement))
    class Engine:
        disposed=False
        def connect(self):return c
        def dispose(self):self.disposed=True
    c=Connection();db=Engine()
    monkeypatch.setattr(q,'engine',lambda _:db)
    runner=q.MembershipActorAttributionQualification(tmp_path,{'owner_urls':{'unknown':'synthetic'}})
    runner.data_state=lambda _: {'unchanged':True}
    runner.snapshot=lambda _: {'unchanged':True}
    runner.passed=lambda *a,**k:None
    def refuse(connection,mode):
        assert len(calls)==2
        raise q.baseline.BaselineError('identity_unknown_history')
    monkeypatch.setattr(q.baseline,'preflight',refuse)
    runner.unknown_history_refusal()
    assert calls[0]=="SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"
    assert calls[1]=="UPDATE identity.alembic_version SET version_num='identity_unknown'"
    assert c.rolled and db.disposed


def test_actual_script_entrypoint_sanitizes_unexpected_driver_exception(monkeypatch,capsys):
    import runpy
    import qualify_membership_actor_attribution as q
    import qualify_identity_baseline as baseline
    from sqlalchemy.exc import IntegrityError
    def failure():
        raise IntegrityError('PRIVATE SQL',{'secret':'PRIVATE VALUE'},RuntimeError('PRIVATE DIAGNOSTIC'))
    monkeypatch.setattr(baseline,'fixture',failure)
    with pytest.raises(SystemExit) as caught:
        runpy.run_path(q.__file__,run_name='__main__')
    assert caught.value.code==1
    output=capsys.readouterr()
    assert output.out=='' and output.err=='membership_actor_attribution_qualification_failed\n'
