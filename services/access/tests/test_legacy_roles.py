"""Legacy RPC identity-binding and independent source custody regression tests."""
from pathlib import Path
import importlib.util
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_identity_baseline as qualification


def revision_module():
    path=qualification.OWNER/'versions/0009_legacy_roles.py'
    spec=importlib.util.spec_from_file_location('legacy_role_revision',path)
    revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
    return revision


def test_legacy_roles_binds_exact_active_token_identity_without_new_acl():
    revision=revision_module()
    assert revision.revision=='identity_0009' and revision.down_revision=='identity_0008'
    sql=revision.LEGACY_ROLES_SQL
    for binding in ['auth.uid()',"auth.jwt() ->> 'org_id'","auth.jwt() ->> 'member_id'",
                    'm.id = token_member_id','m.user_id = token_account_id','m.org_id = token_org_id',
                    'u.deleted_at IS NULL','o.deleted_at IS NULL','m.deleted_at IS NULL','mr.deleted_at IS NULL',
                    'token_member_id <= 0','SET search_path = pg_catalog, pg_temp']:
        assert binding in sql
    assert 'RETURNS TABLE (role text)' in sql
    assert not any(word in sql for word in ['GRANT ','REVOKE ','ALTER FUNCTION','app.',"->> 'user_roles'",'actor','INSERT ','UPDATE ','DELETE '])
    with pytest.raises(RuntimeError,match='Destructive'):revision.downgrade()


def test_blank_or_missing_jwt_sub_is_gated_before_native_uuid_conversion():
    sql=revision_module().LEGACY_ROLES_SQL
    declaration=sql.split('token_account_id uuid :=',1)[1].split(';',1)[0].strip()
    assert declaration=="CASE WHEN nullif(auth.jwt() ->> 'sub', '') IS NULL THEN NULL ELSE auth.uid() END"
    # Nonempty malformed inputs still reach the native typed helper; do not swallow
    # its 22P02 (or the existing organization/member conversion errors).
    assert 'EXCEPTION' not in sql and 'WHEN OTHERS' not in sql


def test_legacy_roles_is_head_and_profile_remains_supported(monkeypatch):
    b=qualification.baseline
    assert b.LEGACY_ROLES_REVISION=='identity_0009'
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.LEGACY_ROLES_REVISION)
    monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
    seen=[];monkeypatch.setattr(b,'verify_catalog',lambda c,k:seen.append(k))
    b.verify_owned_postcondition(object())
    assert seen==['legacy_roles']
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.PROFILE_REVISION)
    b.verify_owned_postcondition(object())
    assert seen==['legacy_roles','profile']
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):b.verify_owned_postcondition(object(),require_head=True)


@pytest.mark.parametrize('mutation',[None,'identity_baseline.py','source-pins.json','reference.json','actor-reference.json',
    'projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json',
    'target-reference.json','profile-reference.json','versions/0001_baseline.py','versions/0002_actor_registry.py',
    'versions/0003_current_account_actor.py','versions/0004_current_account_organization.py','versions/0005_operator_authority.py',
    'versions/0006_actor_command.py','versions/0007_organization_targets.py','versions/0008_profile_fields.py','versions/0009_legacy_roles.py'])
def test_recorder_full_source_custody_and_exclusive_publication(tmp_path,monkeypatch,mutation):
    from test_actor_command_qualification import recorder
    from test_projection_qualification import digest
    import stat
    runner,statements=recorder(tmp_path,monkeypatch,mutation)
    (tmp_path/'identity_baseline.py').write_text('LEGACY_ROLES_REFERENCE_SHA256 = None\n')
    for name in ['command-reference.json','target-reference.json','profile-reference.json']:(tmp_path/name).write_text('{}')
    for number,name,symbol in [(7,'organization_targets','TARGET_SCHEMA_SQL'),(8,'profile_fields','PROFILE_FIELDS_SQL'),(9,'legacy_roles','LEGACY_ROLES_SQL')]:
        (tmp_path/f'versions/{number:04d}_{name}.py').write_text(f'{symbol} = "captured {name}"\n')
    runner.private={'owner_urls':{'legacy_roles_reference':'synthetic'}}
    b=qualification.baseline
    monkeypatch.setattr(b,'trusted_profile_reference',lambda:{})
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
        with pytest.raises(AssertionError,match='legacy_roles_reference_source_changed'):runner.record_legacy_roles_reference()
        assert not (tmp_path/'legacy-role-reference.json').exists()
    else:
        runner.record_legacy_roles_reference()
        assert (tmp_path/'identity_baseline.py').read_bytes()==helper
        assert runner.records[-1]['pin_update_required'] is True
        assert stat.S_IMODE((tmp_path/'legacy-role-reference.json').stat().st_mode)==0o600
        with pytest.raises(AssertionError,match='legacy_roles_reference_already_exists'):runner.record_legacy_roles_reference()
    assert len(preflight_calls)==2
    assert statements==[deadline,'captured baseline','captured actor','captured projection','captured organization','captured authority','captured command',
                       'captured organization_targets','captured profile_fields','captured legacy_roles',deadline]


def test_legacy_role_reference_binds_prior_trust_and_own_source(tmp_path,monkeypatch):
    import json
    from test_projection_qualification import digest
    b=qualification.baseline;calls=[]
    monkeypatch.setattr(b,'trusted_profile_reference',lambda:calls.append('profile'))
    monkeypatch.setattr(b,'HERE',tmp_path)
    (tmp_path/'versions').mkdir();(tmp_path/'versions/0009_legacy_roles.py').write_bytes(b'source')
    (tmp_path/'source-pins.json').write_text('{}')
    reference={'source_pins':{},'migration_sha256':digest(b'source'),'legacy_roles':{}}
    content=json.dumps(reference).encode();(tmp_path/'legacy-role-reference.json').write_bytes(content)
    monkeypatch.setattr(b,'LEGACY_ROLES_REFERENCE_SHA256',digest(content))
    assert b.trusted_legacy_roles_reference()=={} and calls==['profile']
    (tmp_path/'versions/0009_legacy_roles.py').write_bytes(b'drift')
    with pytest.raises(b.BaselineError,match='identity_reference_unavailable'):b.trusted_legacy_roles_reference()


def test_independent_reference_preserves_all_catalog_categories_except_function_definition():
    b=qualification.baseline
    prior=b.trusted_profile_reference();current=b.trusted_legacy_roles_reference()
    assert prior.keys()==current.keys()
    assert {category for category in prior if prior[category]!=current[category]}=={'functions'}


@pytest.mark.parametrize('module,args',[('qualify_identity_baseline',['--record-legacy-role-reference']),('qualify_legacy_roles',[])])
def test_optimized_execution_refused_before_fixture(module,args):
    import subprocess
    source="""import importlib,sys
sys.path.insert(0,sys.argv[1])
module=importlib.import_module(sys.argv[2])
module.fixture=lambda: (_ for _ in ()).throw(RuntimeError('fixture_reached'))
sys.argv=[module.__file__]+sys.argv[3:]
try:module.main()
except RuntimeError as error:
    if str(error) not in {'legacy_roles_reference_optimized_python_prohibited','legacy_roles_qualification_optimized_python_prohibited'}:raise RuntimeError('wrong_guard')
else:raise RuntimeError('missing_guard')
"""
    result=subprocess.run([sys.executable,'-I','-B','-O','-c',source,str(Path(__file__).resolve().parent),module,*args],capture_output=True,text=True,timeout=10)
    assert result.returncode==0 and result.stdout==result.stderr==''


@pytest.mark.parametrize('failure',['create_after_commit','snapshot'])
def test_legacy_failure_fixture_restores_after_mutation_or_body_failure(tmp_path,failure):
    import qualify_legacy_roles as legacy
    import json,stat
    runner=legacy.LegacyRolesQualification(tmp_path,{})
    state={'created':False};commands=[]
    def sql(case,statement,values=None):
        commands.append(statement)
        if statement.startswith('SELECT '):return [('event_trigger','synthetic_legacy_roles_failure')] if state['created'] else []
        if statement.startswith('CREATE FUNCTION'):
            witnesses=list(tmp_path.glob('legacy-roles-event-restoration-required-*.json'))
            assert len(witnesses)==1 and json.loads(witnesses[0].read_text())['before']==[]
            state['created']=True
            if failure=='create_after_commit':raise RuntimeError('synthetic_create_after_commit')
        if statement.startswith('DROP EVENT TRIGGER'):state['created']=False
        return []
    runner.admin_sql=sql
    with pytest.raises(RuntimeError,match='synthetic_'):
        with runner.failure_fixture('failure'):raise RuntimeError('synthetic_snapshot')
    assert state['created'] is False
    paths=list(tmp_path.glob('legacy-roles-event-restored-*.json'))
    assert len(paths)==1 and stat.S_IMODE(paths[0].stat().st_mode)==0o600


def test_legacy_failure_fixture_refuses_existing_objects(tmp_path):
    import qualify_legacy_roles as legacy
    runner=legacy.LegacyRolesQualification(tmp_path,{})
    commands=[]
    def sql(case,statement,values=None):commands.append(statement);return [('event_trigger','synthetic_legacy_roles_failure')]
    runner.admin_sql=sql
    with pytest.raises(AssertionError,match='already_exists'):
        with runner.failure_fixture('failure'):raise RuntimeError('body_reached')
    assert len(commands)==1 and commands[0].startswith('SELECT ')
    assert not list(tmp_path.glob('legacy-roles-event-*.json'))


@pytest.mark.parametrize('signame',['SIGINT','SIGTERM'])
@pytest.mark.parametrize('cleanup_fails',[False,True])
def test_installed_signal_unwinds_and_cleanup_failure_retains_required_witness(tmp_path,monkeypatch,signame,cleanup_fails):
    import qualify_legacy_roles as legacy
    signal=legacy.signal
    originals={signal.SIGINT:object(),signal.SIGTERM:object()};handlers=dict(originals)
    monkeypatch.setattr(signal,'getsignal',lambda sig:handlers[sig])
    monkeypatch.setattr(signal,'signal',lambda sig,handler:handlers.__setitem__(sig,handler))
    runner=legacy.LegacyRolesQualification(tmp_path,{})
    state={'created':False};commands=[]
    def sql(case,statement,values=None):
        commands.append(statement)
        if statement.startswith('SELECT '):return [('event_trigger','synthetic_legacy_roles_failure')] if state['created'] else []
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
    assert len(list(tmp_path.glob('legacy-roles-event-restoration-required-*.json')))==1
    assert len(list(tmp_path.glob('legacy-roles-event-restored-*.json')))==(0 if cleanup_fails else 1)
    assert state['created'] is cleanup_fails


@pytest.mark.parametrize('corruption',['other_body','helper_acl','helper_owner','helper_signature','helper_language','removed'])
def test_per_function_comparison_refuses_unrelated_or_declaration_changes(corruption):
    import qualify_legacy_roles as legacy
    import copy
    old=[['public','get_user_roles','','identity_migrator',
          "CREATE OR REPLACE FUNCTION public.get_user_roles()\n RETURNS TABLE(role text)\n LANGUAGE plpgsql\n SECURITY DEFINER\n SET search_path TO 'public', 'identity'\nAS $function$old body$function$\n",'acl'],
         ['identity','auth_hook','event jsonb','identity_migrator','hook definition','hook acl']]
    new=copy.deepcopy(old)
    new[0][4]=new[0][4].replace("'public', 'identity'","'pg_catalog', 'pg_temp'").replace('old body','new body')
    legacy.LegacyRolesQualification.verify_function_delta(old,new)
    if corruption=='other_body':new[1][4]='changed hook'
    elif corruption=='helper_acl':new[0][5]='changed acl'
    elif corruption=='helper_owner':new[0][3]='changed owner'
    elif corruption=='helper_signature':new[0][4]=new[0][4].replace('TABLE(role text)','TABLE(role bigint)')
    elif corruption=='helper_language':new[0][4]=new[0][4].replace('LANGUAGE plpgsql','LANGUAGE sql')
    elif corruption=='removed':new.pop()
    with pytest.raises(AssertionError,match='legacy_roles_'):legacy.LegacyRolesQualification.verify_function_delta(old,new)


def test_native_helper_parity_refuses_stub_definitions(tmp_path):
    import qualify_legacy_roles as legacy
    import json
    (tmp_path/'auth-helper-definitions.json').write_text(json.dumps({'native':['native uid','native jwt']}))
    runner=legacy.LegacyRolesQualification(tmp_path,{})
    runner.sql=lambda *args:[('native uid','native jwt')]
    runner.auth_helper_parity('clean')
    runner.sql=lambda *args:[('scratch uid','scratch jwt')]
    with pytest.raises(AssertionError,match='auth_helper_parity_mismatch'):runner.auth_helper_parity('clean')


@pytest.mark.parametrize('state',['42702','42501','42883'])
def test_characterization_retains_raw_witness_then_refuses_unknown_errors(tmp_path,monkeypatch,state):
    import qualify_legacy_roles as legacy
    import json
    from contextlib import nullcontext
    runner=legacy.LegacyRolesQualification(tmp_path,{ 'runtime_urls':{'characterization':'synthetic'}})
    runner.inputs={'characterization':{'account':'account','org':'org','member':'1','other_member':'2','other_org':'other'}}
    runner.auth_helper_parity=lambda case:None
    runner.sql=lambda *args:[('identity_0008',)]
    runner.data_state=lambda *args:{}
    runner.snapshot=lambda *args:{'functions':[['retained actual function row']]}
    runner.fixture_execution=lambda case:nullcontext()
    passed=[];runner.passed=lambda *a,**k:passed.append(a)
    class Error(Exception):
        class orig:sqlstate=state
    class Transaction:
        def rollback(self):pass
    class Connection:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def begin(self):return Transaction()
        def execute(self,statement,values=None):
            if str(statement)==legacy.RPC:raise Error()
            return []
    class Engine:
        def connect(self):return Connection()
        def dispose(self):pass
    monkeypatch.setattr(legacy,'engine',lambda *args:Engine())
    if state=='42702':runner.characterize()
    else:
        with pytest.raises(AssertionError,match='unexpected_head8_observations'):runner.characterize()
    paths=list(tmp_path.glob('legacy-roles-head8-characterization-*.json'))
    assert len(paths)==1
    observed=json.loads(paths[0].read_text())
    assert observed['observed']==[{'case':kind,'sqlstate':state} for kind in ['own','foreign_member','foreign_org']]
    assert observed['functions']==[['retained actual function row']]
    assert bool(passed)==(state=='42702')


def test_invoke_sets_all_native_claim_forms_locally_and_refuses_spoof_sentinel(tmp_path):
    import qualify_legacy_roles as legacy
    import json
    runner=legacy.LegacyRolesQualification(tmp_path,{})
    runner.inputs={'clean':{'account':'account','org':'org'}}
    events=[];settings={}
    class Transaction:
        def rollback(self):events.append('rollback')
    class Result:
        def one(self):return ('access_runtime','authenticated')
        def __iter__(self):return iter([(legacy.SPOOF_ROLE,)])
    class Connection:
        def begin(self):return Transaction()
        def execute(self,statement,values=None):
            events.append(str(statement))
            if values and 'key' in values:settings[values['key']]=values['value']
            return Result()
    with pytest.raises(AssertionError,match='search_path_spoof_leaked'):
        runner.invoke(Connection(),{'sub':'plural'},spoof=True,
            claim_settings={'request.jwt.claim.sub':'legacy','request.jwt.claim':json.dumps({'sub':'legacy'})})
    assert settings=={'request.jwt.claim.sub':'legacy','request.jwt.claim':json.dumps({'sub':'legacy'}),'request.jwt.claims':json.dumps({'sub':'plural'})}
    assert events[-1]=='rollback'


@pytest.mark.parametrize('signame',['SIGINT','SIGTERM'])
@pytest.mark.parametrize('cleanup_fails',[False,True])
def test_role_edge_signal_unwind_and_failed_cleanup_keep_recovery_evidence(tmp_path,monkeypatch,signame,cleanup_fails):
    import qualify_legacy_roles as legacy
    from contextlib import contextmanager
    signal=legacy.signal
    originals={signal.SIGINT:object(),signal.SIGTERM:object()};handlers=dict(originals)
    monkeypatch.setattr(signal,'getsignal',lambda sig:handlers[sig])
    monkeypatch.setattr(signal,'signal',lambda sig,handler:handlers.__setitem__(sig,handler))
    state={'granted':False};commands=[]
    class Result:
        def __iter__(self):return iter([(role,'access_runtime','supabase_admin',False,'false','true') for role in ['authenticated','service_role']] if state['granted'] else [])
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
    runner=legacy.LegacyRolesQualification(tmp_path,{})
    runner.admin=lambda case:Admin();runner.passed=lambda *a,**k:None
    expected='synthetic_cleanup_failed' if cleanup_fails else 'profile_fixture_interrupted'
    with pytest.raises(RuntimeError,match=expected):
        with runner.fixture_execution('clean'):
            handlers[getattr(signal,signame)](getattr(signal,signame),None)
    assert any(command.startswith('REVOKE ') for command in commands)
    assert handlers==originals and commands[-1]=='dispose'
    assert len(list(tmp_path.glob('profile-role-restoration-required-*.json')))==1
    assert len(list(tmp_path.glob('profile-role-restored-*.json')))==(0 if cleanup_fails else 1)
    assert state['granted'] is cleanup_fails
