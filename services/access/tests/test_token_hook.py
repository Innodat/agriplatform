"""Token hook membership retirement and source custody regressions."""
from pathlib import Path
import importlib.util
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_identity_baseline as qualification


def revision_module():
    path=qualification.OWNER/'versions/0010_token_hook.py'
    spec=importlib.util.spec_from_file_location('token_hook_revision',path)
    revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
    return revision


def test_token_hook_filters_three_membership_paths_preserving_selection_contract():
    revision=revision_module();sql=revision.TOKEN_HOOK_SQL
    assert revision.revision=='identity_0010' and revision.down_revision=='identity_0009'
    assert sql.count('join identity.org o on o.id = om.org_id')==3
    assert sql.count('and o.deleted_at IS NULL')==4
    assert "(event->'user_metadata'->>'current_org_id')::uuid" in sql
    assert 'order by om.is_owner desc, om.created_at asc' in sql
    assert 'SET search_path = pg_catalog, pg_temp' in sql
    assert not any(word in sql for word in ['GRANT ','REVOKE ','ALTER FUNCTION','identity.users','INSERT ','UPDATE ','DELETE ','EXCEPTION'])
    for key in ['org_id','org_slug','member_id','user_roles','role_ids','org_ids','is_org_owner']:
        assert "'{"+key+"}'" in sql
    with pytest.raises(RuntimeError,match='Destructive'):revision.downgrade()


def test_token_hook_head_and_historical_head(monkeypatch):
    b=qualification.baseline
    assert b.TOKEN_HOOK_REVISION=='identity_0010'
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.TOKEN_HOOK_REVISION)
    monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
    seen=[];monkeypatch.setattr(b,'verify_catalog',lambda c,k:seen.append(k))
    b.verify_owned_postcondition(object())
    assert seen==['token_hook']
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):b.verify_owned_postcondition(object(),require_head=True)
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.LEGACY_ROLES_REVISION)
    b.verify_owned_postcondition(object())
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):b.verify_owned_postcondition(object(),require_head=True)


@pytest.mark.parametrize('mutation',[None,'identity_baseline.py','source-pins.json','reference.json','actor-reference.json',
    'projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json',
    'target-reference.json','profile-reference.json','legacy-role-reference.json','versions/0001_baseline.py','versions/0002_actor_registry.py',
    'versions/0003_current_account_actor.py','versions/0004_current_account_organization.py','versions/0005_operator_authority.py',
    'versions/0006_actor_command.py','versions/0007_organization_targets.py','versions/0008_profile_fields.py','versions/0009_legacy_roles.py','versions/0010_token_hook.py'])
def test_recorder_full_source_custody_and_exclusive_publication(tmp_path,monkeypatch,mutation):
    from test_actor_command_qualification import recorder
    from test_projection_qualification import digest
    import stat
    runner,statements=recorder(tmp_path,monkeypatch,mutation)
    (tmp_path/'identity_baseline.py').write_text('TOKEN_HOOK_REFERENCE_SHA256 = None\n')
    for name in ['command-reference.json','target-reference.json','profile-reference.json','legacy-role-reference.json']:(tmp_path/name).write_text('{}')
    for number,name,symbol in [(7,'organization_targets','TARGET_SCHEMA_SQL'),(8,'profile_fields','PROFILE_FIELDS_SQL'),(9,'legacy_roles','LEGACY_ROLES_SQL'),(10,'token_hook','TOKEN_HOOK_SQL')]:
        (tmp_path/f'versions/{number:04d}_{name}.py').write_text(f'{symbol} = "captured {name}"\n')
    runner.private={'owner_urls':{'token_hook_reference':'synthetic'}}
    b=qualification.baseline
    monkeypatch.setattr(b,'trusted_legacy_roles_reference',lambda:{})
    monkeypatch.setattr(b,'verify_target_roles',lambda *a,**k:None)
    monkeypatch.setattr(b,'verify_profile_privileges',lambda *a,**k:None)
    monkeypatch.setattr(b,'target_catalog_snapshot',lambda *a:{})
    monkeypatch.setattr(b,'IMPORTED_SOURCE_SHA256',digest((tmp_path/'identity_baseline.py').read_bytes()))
    helper=(tmp_path/'identity_baseline.py').read_bytes()
    deadline="SET LOCAL statement_timeout='60s'; SET LOCAL lock_timeout='5s'"
    preflight_calls=[]
    def preflight(*args):
        assert statements[-1]==deadline
        preflight_calls.append(len(statements))
        return 'clean'
    monkeypatch.setattr(b,'preflight',preflight)
    if mutation:
        with pytest.raises(AssertionError,match='token_hook_reference_source_changed'):runner.record_token_hook_reference()
        assert not (tmp_path/'token-hook-reference.json').exists()
    else:
        runner.record_token_hook_reference()
        assert (tmp_path/'identity_baseline.py').read_bytes()==helper
        assert runner.records[-1]['pin_update_required'] is True
        assert stat.S_IMODE((tmp_path/'token-hook-reference.json').stat().st_mode)==0o600
        with pytest.raises(AssertionError,match='token_hook_reference_already_exists'):runner.record_token_hook_reference()
    assert len(preflight_calls)==2
    assert statements==[deadline,'captured baseline','captured actor','captured projection','captured organization','captured authority','captured command',
                       'captured organization_targets','captured profile_fields','captured legacy_roles','captured token_hook',deadline]


def test_token_hook_reference_binds_prior_trust_and_own_source(tmp_path,monkeypatch):
    import json
    from test_projection_qualification import digest
    b=qualification.baseline;calls=[]
    monkeypatch.setattr(b,'trusted_legacy_roles_reference',lambda:calls.append('profile'))
    monkeypatch.setattr(b,'HERE',tmp_path)
    (tmp_path/'versions').mkdir();(tmp_path/'versions/0010_token_hook.py').write_bytes(b'source')
    (tmp_path/'source-pins.json').write_text('{}')
    reference={'source_pins':{},'migration_sha256':digest(b'source'),'token_hook':{}}
    content=json.dumps(reference).encode();(tmp_path/'token-hook-reference.json').write_bytes(content)
    monkeypatch.setattr(b,'TOKEN_HOOK_REFERENCE_SHA256',digest(content))
    assert b.trusted_token_hook_reference()=={} and calls==['profile']
    (tmp_path/'versions/0010_token_hook.py').write_bytes(b'drift')
    with pytest.raises(b.BaselineError,match='identity_reference_unavailable'):b.trusted_token_hook_reference()



@pytest.mark.parametrize('module,args',[('qualify_identity_baseline',['--record-token-hook-reference']),('qualify_token_hook',[])])
def test_optimized_execution_refused_before_fixture(module,args):
    import subprocess
    source="""import importlib,sys
sys.path.insert(0,sys.argv[1])
module=importlib.import_module(sys.argv[2])
module.fixture=lambda: (_ for _ in ()).throw(RuntimeError('fixture_reached'))
sys.argv=[module.__file__]+sys.argv[3:]
try:module.main()
except RuntimeError as error:
    if str(error) not in {'token_hook_reference_optimized_python_prohibited','token_hook_qualification_optimized_python_prohibited'}:raise RuntimeError('wrong_guard')
else:raise RuntimeError('missing_guard')
"""
    result=subprocess.run([sys.executable,'-I','-B','-O','-c',source,str(Path(__file__).resolve().parent),module,*args],capture_output=True,text=True,timeout=10)
    assert result.returncode==0 and result.stdout==result.stderr==''


@pytest.mark.parametrize('failure',['create_after_commit','snapshot'])
def test_legacy_failure_fixture_restores_after_mutation_or_body_failure(tmp_path,failure):
    import qualify_token_hook as legacy
    import json,stat
    runner=legacy.TokenHookQualification(tmp_path,{})
    state={'created':False};commands=[]
    def sql(case,statement,values=None):
        commands.append(statement)
        if statement.startswith('SELECT '):return [('event_trigger','synthetic_token_hook_failure')] if state['created'] else []
        if statement.startswith('CREATE FUNCTION'):
            witnesses=list(tmp_path.glob('token-hook-event-restoration-required-*.json'))
            assert len(witnesses)==1 and json.loads(witnesses[0].read_text())['before']==[]
            state['created']=True
            if failure=='create_after_commit':raise RuntimeError('synthetic_create_after_commit')
        if statement.startswith('DROP EVENT TRIGGER'):state['created']=False
        return []
    runner.admin_sql=sql
    with pytest.raises(RuntimeError,match='synthetic_'):
        with runner.failure_fixture('failure'):raise RuntimeError('synthetic_snapshot')
    assert state['created'] is False
    paths=list(tmp_path.glob('token-hook-event-restored-*.json'))
    assert len(paths)==1 and stat.S_IMODE(paths[0].stat().st_mode)==0o600


def test_legacy_failure_fixture_refuses_existing_objects(tmp_path):
    import qualify_token_hook as legacy
    runner=legacy.TokenHookQualification(tmp_path,{})
    commands=[]
    def sql(case,statement,values=None):commands.append(statement);return [('event_trigger','synthetic_token_hook_failure')]
    runner.admin_sql=sql
    with pytest.raises(AssertionError,match='already_exists'):
        with runner.failure_fixture('failure'):raise RuntimeError('body_reached')
    assert len(commands)==1 and commands[0].startswith('SELECT ')
    assert not list(tmp_path.glob('token-hook-event-*.json'))


@pytest.mark.parametrize('signame',['SIGINT','SIGTERM'])
@pytest.mark.parametrize('cleanup_fails',[False,True])
def test_installed_signal_unwinds_and_cleanup_failure_retains_required_witness(tmp_path,monkeypatch,signame,cleanup_fails):
    import qualify_token_hook as legacy
    signal=legacy.signal
    originals={signal.SIGINT:object(),signal.SIGTERM:object()};handlers=dict(originals)
    monkeypatch.setattr(signal,'getsignal',lambda sig:handlers[sig])
    monkeypatch.setattr(signal,'signal',lambda sig,handler:handlers.__setitem__(sig,handler))
    runner=legacy.TokenHookQualification(tmp_path,{})
    state={'created':False};commands=[]
    def sql(case,statement,values=None):
        commands.append(statement)
        if statement.startswith('SELECT '):return [('event_trigger','synthetic_token_hook_failure')] if state['created'] else []
        if statement.startswith('CREATE FUNCTION'):state['created']=True
        if statement.startswith('DROP EVENT TRIGGER'):
            if cleanup_fails:raise RuntimeError('synthetic_cleanup_failed')
            state['created']=False
        return []
    runner.admin_sql=sql
    expected='synthetic_cleanup_failed' if cleanup_fails else 'profile_fixture_interrupted'
    with pytest.raises(RuntimeError,match=expected):
        with runner.failure_fixture('failure'):
            handler=handlers[getattr(signal,signame)]
            assert callable(handler)
            handler(getattr(signal,signame),None)
    assert any(statement.startswith('DROP EVENT TRIGGER') for statement in commands)
    assert handlers==originals
    assert len(list(tmp_path.glob('token-hook-event-restoration-required-*.json')))==1
    assert len(list(tmp_path.glob('token-hook-event-restored-*.json')))==(0 if cleanup_fails else 1)
    assert state['created'] is cleanup_fails



@pytest.mark.parametrize('corruption',['other_body','helper_acl','helper_owner','helper_signature','helper_language','removed'])
def test_per_function_comparison_refuses_unrelated_or_declaration_changes(corruption):
    import qualify_token_hook as legacy
    import copy
    old=[['identity','custom_access_token_hook','event jsonb','identity_migrator',
          "CREATE OR REPLACE FUNCTION identity.custom_access_token_hook(event jsonb)\n RETURNS TABLE(role text)\n LANGUAGE plpgsql\n SECURITY DEFINER\n SET search_path TO 'public', 'identity'\nAS $function$old body$function$\n",'acl'],
         ['identity','auth_hook','event jsonb','identity_migrator','hook definition','hook acl']]
    new=copy.deepcopy(old)
    new[0][4]=new[0][4].replace("'public', 'identity'","'pg_catalog', 'pg_temp'").replace('old body','new body')
    legacy.TokenHookQualification.verify_function_delta(old,new)
    if corruption=='other_body':new[1][4]='changed hook'
    elif corruption=='helper_acl':new[0][5]='changed acl'
    elif corruption=='helper_owner':new[0][3]='changed owner'
    elif corruption=='helper_signature':new[0][4]=new[0][4].replace('TABLE(role text)','TABLE(role bigint)')
    elif corruption=='helper_language':new[0][4]=new[0][4].replace('LANGUAGE plpgsql','LANGUAGE sql')
    elif corruption=='removed':new.pop()
    with pytest.raises(AssertionError,match='token_hook_'):legacy.TokenHookQualification.verify_function_delta(old,new)



@pytest.mark.parametrize('signame',['SIGINT','SIGTERM'])
@pytest.mark.parametrize('cleanup_fails',[False,True])
def test_role_edge_signal_unwind_and_failed_cleanup_keep_recovery_evidence(tmp_path,monkeypatch,signame,cleanup_fails):
    import qualify_token_hook as legacy
    from contextlib import contextmanager
    signal=legacy.signal
    originals={signal.SIGINT:object(),signal.SIGTERM:object()};handlers=dict(originals)
    monkeypatch.setattr(signal,'getsignal',lambda sig:handlers[sig])
    monkeypatch.setattr(signal,'signal',lambda sig,handler:handlers.__setitem__(sig,handler))
    state={'granted':False};commands=[]
    class Result:
        def __iter__(self):return iter([(role,'access_runtime','supabase_admin',False,'false','true') for role in ['supabase_auth_admin','service_role']] if state['granted'] else [])
    class Admin:
        @contextmanager
        def begin(self):yield self
        def execute(self,statement):
            statement=str(statement);commands.append(statement)
            if statement.startswith('GRANT '):state['granted']=True
            if statement.startswith('REVOKE '):
                if cleanup_fails:raise RuntimeError('synthetic_cleanup_failed')
                state['granted']=False
            return Result()
        def dispose(self):commands.append('dispose')
    runner=legacy.TokenHookQualification(tmp_path,{})
    runner.admin=lambda case:Admin();runner.passed=lambda *a,**k:None
    expected='synthetic_cleanup_failed' if cleanup_fails else 'token_hook_fixture_interrupted'
    with pytest.raises(RuntimeError,match=expected):
        with runner.fixture_execution('clean'):
            handlers[getattr(signal,signame)](getattr(signal,signame),None)
    assert any(command.startswith('REVOKE ') for command in commands)
    assert handlers==originals and commands[-1]=='dispose'
    assert len(list(tmp_path.glob('token-hook-role-restoration-required-*.json')))==1
    assert len(list(tmp_path.glob('token-hook-role-restored-*.json')))==(0 if cleanup_fails else 1)
    assert state['granted'] is cleanup_fails


@pytest.mark.parametrize('grant_failure',['before_mutation','after_commit'])
@pytest.mark.parametrize('cleanup_fails',[False,True])
def test_role_edge_grant_failure_restores_exact_state_and_handlers(tmp_path,monkeypatch,grant_failure,cleanup_fails):
    import qualify_token_hook as hook
    from contextlib import contextmanager
    import json
    signal=hook.signal
    originals={signal.SIGINT:object(),signal.SIGTERM:object()};handlers=dict(originals)
    monkeypatch.setattr(signal,'getsignal',lambda sig:handlers[sig])
    monkeypatch.setattr(signal,'signal',lambda sig,handler:handlers.__setitem__(sig,handler))
    state={'granted':False};commands=[]
    class Result:
        def __iter__(self):
            return iter([(role,'access_runtime','supabase_admin',False,'false','true')
                for role in ['supabase_auth_admin','service_role']] if state['granted'] else [])
    class Admin:
        @contextmanager
        def begin(self):
            yield self
            if commands[-1].startswith('GRANT ') and grant_failure=='after_commit':
                raise RuntimeError('synthetic_grant_after_commit')
        def execute(self,statement):
            statement=str(statement);commands.append(statement)
            if statement.startswith('GRANT '):
                assert len(list(tmp_path.glob('token-hook-role-restoration-required-*.json')))==1
                if grant_failure=='before_mutation':raise RuntimeError('synthetic_grant_before_mutation')
                state['granted']=True
            if statement.startswith('REVOKE '):
                if cleanup_fails:raise RuntimeError('synthetic_cleanup_failed')
                state['granted']=False
            return Result()
        def dispose(self):commands.append('dispose')
    runner=hook.TokenHookQualification(tmp_path,{})
    runner.admin=lambda case:Admin();runner.passed=lambda *a,**k:None
    expected='synthetic_cleanup_failed' if cleanup_fails else 'synthetic_grant_'
    with pytest.raises(RuntimeError,match=expected):
        with runner.fixture_execution('clean'):raise AssertionError('body_reached')
    assert any(command.startswith('REVOKE ') for command in commands)
    assert handlers==originals and commands[-1]=='dispose'
    required=list(tmp_path.glob('token-hook-role-restoration-required-*.json'))
    restored=list(tmp_path.glob('token-hook-role-restored-*.json'))
    assert len(required)==1 and json.loads(required[0].read_text())['before']==[]
    assert len(restored)==(0 if cleanup_fails else 1)
    if restored:
        receipt=json.loads(restored[0].read_text())
        assert receipt['before']==receipt['after']==[] and receipt['exact_edges'] is True
    assert state['granted'] is (cleanup_fails and grant_failure=='after_commit')


@pytest.mark.parametrize('missing',['malformed','00000000-0000-0000-0000-000000000000','duplicate','valid'])
def test_missing_fixture_uuid_is_canonical_nonnil_and_distinct(tmp_path,missing):
    import qualify_token_hook as hook
    import json,uuid
    row={key:str(uuid.uuid4()) for key in ['account','other','missing','org','other_org']}
    row.update({key:str(number) for number,key in enumerate(['member','other_member','other_org_member','role','deleted_role'],1)})
    if missing=='duplicate':row['missing']=row['account']
    elif missing!='valid':row['missing']=missing
    (tmp_path/'token-hook-fixtures.json').write_text(json.dumps({'characterization':row,'clean':row}))
    runner=hook.TokenHookQualification(tmp_path,{group:{case:'' for case in hook.REQUIRED_CASES}
        for group in ['owner_urls','runtime_urls','databases']})
    if missing=='valid':runner.validate_targets()
    else:
        with pytest.raises((AssertionError,ValueError)):runner.validate_targets()


@pytest.mark.parametrize('with_claims',[False,True])
def test_invoke_accepts_absent_claims_and_preserves_supplied_unrelated_claims(tmp_path,with_claims):
    import qualify_token_hook as hook
    event={'user_id':'synthetic','unrelated_event':['preserved']}
    if with_claims:event['claims']={'custom':{'preserved':True}}
    generated={'org_id':None,'org_slug':None,'member_id':None,'user_roles':[],
        'role_ids':[],'org_ids':[],'is_org_owner':False}
    claims={**event.get('claims',{}),**generated};rolled_back=[]
    class Transaction:
        def rollback(self):rolled_back.append(True)
    class Result:
        def one(self):return ('access_runtime','supabase_auth_admin')
        def scalar_one(self):return {**event,'claims':claims}
    class Connection:
        def begin(self):return Transaction()
        def execute(self,*args,**kwargs):return Result()
    runner=hook.TokenHookQualification(tmp_path,{})
    assert runner.invoke(Connection(),event)==claims
    assert rolled_back==[True]
