"""One-way membership retirement structural and qualification contract."""
from pathlib import Path
import importlib.util
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_identity_baseline as qualification


def revision_module():
    path=qualification.OWNER/'versions/0013_membership_retirement.py'
    spec=importlib.util.spec_from_file_location('membership_retirement_revision',path)
    revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
    return revision


def test_retirement_migration_is_exact_function_only_extension():
    revision=revision_module();sql=revision.MEMBERSHIP_RETIREMENT_SQL
    assert revision.revision=='identity_0013' and revision.down_revision=='identity_0012'
    prior=(qualification.OWNER/'versions/0012_membership_retention.py').read_text()
    prior='CREATE OR REPLACE FUNCTION'+prior.split('CREATE OR REPLACE FUNCTION',1)[1].split('$revision_guard$;',1)[0]+'$revision_guard$;'
    insertion="""    IF TG_OP = 'UPDATE' AND OLD.deleted_at IS NOT NULL
        AND NEW.deleted_at IS DISTINCT FROM OLD.deleted_at THEN
        RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'identity_membership_retirement_immutable',
            CONSTRAINT = 'org_member_retirement_immutable';
    END IF;
"""
    assert sql.strip()==prior.replace("    IF TG_OP = 'INSERT' THEN",insertion+"    IF TG_OP = 'INSERT' THEN").strip()
    assert not any(word in sql for word in ['ALTER TABLE','CREATE TRIGGER','DROP TRIGGER','GRANT ','REVOKE ','SECURITY DEFINER'])
    with pytest.raises(RuntimeError,match='Destructive'):revision.downgrade()


def test_retirement_is_required_head_and_retention_stays_historical(monkeypatch):
    b=qualification.baseline
    assert b.MEMBERSHIP_RETIREMENT_REVISION=='identity_0013'
    monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.MEMBERSHIP_RETIREMENT_REVISION)
    seen=[];monkeypatch.setattr(b,'verify_catalog',lambda c,k:seen.append(k))
    b.verify_owned_postcondition(object(),require_head=True)
    assert seen==['membership_retirement']
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.MEMBERSHIP_RETENTION_REVISION)
    b.verify_owned_postcondition(object())
    assert seen[-1]=='membership_retention'
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):b.verify_owned_postcondition(object(),require_head=True)


@pytest.mark.parametrize('mutation',[None,'identity_baseline.py','source-pins.json','reference.json','actor-reference.json',
    'projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json',
    'target-reference.json','profile-reference.json','legacy-role-reference.json','token-hook-reference.json','membership-binding-reference.json',
    'versions/0001_baseline.py','versions/0002_actor_registry.py','versions/0003_current_account_actor.py',
    'versions/0004_current_account_organization.py','versions/0005_operator_authority.py','versions/0006_actor_command.py',
    'versions/0007_organization_targets.py','versions/0008_profile_fields.py','versions/0009_legacy_roles.py',
    'versions/0010_token_hook.py','versions/0011_membership_binding.py','versions/0012_membership_retention.py','membership-retention-reference.json','versions/0013_membership_retirement.py'])
def test_retention_recorder_custody_publication_and_every_prior_catalog(tmp_path,monkeypatch,mutation):
    from test_actor_command_qualification import recorder
    from test_projection_qualification import digest
    import stat
    runner,statements=recorder(tmp_path,monkeypatch,mutation)
    (tmp_path/'identity_baseline.py').write_text('MEMBERSHIP_RETIREMENT_REFERENCE_SHA256 = None\n')
    for name in ['command-reference.json','target-reference.json','profile-reference.json','legacy-role-reference.json','token-hook-reference.json','membership-binding-reference.json','membership-retention-reference.json']:(tmp_path/name).write_text('{}')
    for number,name,symbol in [(7,'organization_targets','TARGET_SCHEMA_SQL'),(8,'profile_fields','PROFILE_FIELDS_SQL'),(9,'legacy_roles','LEGACY_ROLES_SQL'),(10,'token_hook','TOKEN_HOOK_SQL'),(11,'membership_binding','MEMBERSHIP_BINDING_SQL'),(12,'membership_retention','MEMBERSHIP_RETENTION_SQL'),(13,'membership_retirement','MEMBERSHIP_RETIREMENT_SQL')]:
        (tmp_path/f'versions/{number:04d}_{name}.py').write_text(f'{symbol} = "captured {name}"\n')
    runner.private={'owner_urls':{'membership_retirement_reference':'synthetic'}}
    b=qualification.baseline
    monkeypatch.setattr(b,'trusted_membership_retention_reference',lambda:{})
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
        with pytest.raises(AssertionError,match='membership_retirement_reference_source_changed'):runner.record_membership_retirement_reference()
        assert not (tmp_path/'membership-retirement-reference.json').exists()
    else:
        runner.record_membership_retirement_reference()
        assert (tmp_path/'identity_baseline.py').read_bytes()==helper
        assert runner.records[-1]['pin_update_required'] is True
        assert stat.S_IMODE((tmp_path/'membership-retirement-reference.json').stat().st_mode)==0o600
        with pytest.raises(AssertionError,match='already_exists'):runner.record_membership_retirement_reference()
    assert len(preflights)==2
    assert catalogs==['owned','actor','projection','organization','authority','command','target','profile','legacy_roles','token_hook','membership_binding','membership_retention']
    assert statements==[deadline,'captured baseline','captured actor','captured projection','captured organization','captured authority','captured command',
        'captured organization_targets','captured profile_fields','captured legacy_roles','captured token_hook','captured membership_binding','captured membership_retention','captured membership_retirement',deadline]


def test_reference_retains_prior_trust_and_own_source(tmp_path,monkeypatch):
    import json
    from test_projection_qualification import digest
    b=qualification.baseline;calls=[]
    monkeypatch.setattr(b,'trusted_membership_retention_reference',lambda:calls.append('retention'))
    monkeypatch.setattr(b,'HERE',tmp_path)
    (tmp_path/'versions').mkdir();(tmp_path/'versions/0013_membership_retirement.py').write_bytes(b'source')
    (tmp_path/'source-pins.json').write_text('{}')
    content=json.dumps({'source_pins':{},'migration_sha256':digest(b'source'),'membership_retirement':{}}).encode()
    (tmp_path/'membership-retirement-reference.json').write_bytes(content)
    monkeypatch.setattr(b,'MEMBERSHIP_RETIREMENT_REFERENCE_SHA256',digest(content))
    assert b.trusted_membership_retirement_reference()=={} and calls==['retention']
    (tmp_path/'versions/0013_membership_retirement.py').write_bytes(b'drift')
    with pytest.raises(b.BaselineError,match='identity_reference_unavailable'):b.trusted_membership_retirement_reference()


@pytest.mark.parametrize('module,args',[('qualify_identity_baseline',['--record-membership-retirement-reference']),('qualify_membership_retirement',[])])
def test_optimized_execution_refused_before_fixture(module,args):
    import subprocess
    source="""import importlib,sys
sys.path.insert(0,sys.argv[1])
module=importlib.import_module(sys.argv[2])
module.fixture=lambda: (_ for _ in ()).throw(RuntimeError('fixture_reached'))
sys.argv=[module.__file__]+sys.argv[3:]
try:module.main()
except RuntimeError as error:
    if str(error) not in {'membership_retirement_reference_optimized_python_prohibited','membership_retirement_qualification_optimized_python_prohibited'}:raise RuntimeError('wrong_guard')
else:raise RuntimeError('missing_guard')
"""
    result=subprocess.run([sys.executable,'-I','-B','-O','-c',source,str(Path(__file__).resolve().parent),module,*args],capture_output=True,text=True,timeout=10)
    assert result.returncode==0 and result.stdout==result.stderr==''




def test_prior_execution_manifest_is_exact27_baseline12_files():
    import qualify_membership_retirement as retirement
    assert len(retirement.PREVIOUS_FILES)==27
    assert {'versions/0012_membership_retention.py','membership-retention-reference.json'}<=retirement.PREVIOUS_FILES
    assert 'versions/0013_membership_retirement.py' not in retirement.PREVIOUS_FILES
    assert retirement.PREVIOUS_COMMIT=='c70a5d02096c3c22d582d3bd277134962bd02e51'


def failure_fixture_mock(tmp_path,*,create_failure=False,cleanup_fails=False,initially_called=False):
    import qualify_membership_retirement as retirement
    import json
    runner=retirement.MembershipRetirementQualification(tmp_path,{})
    state={'created':False,'called':initially_called};commands=[]
    def sql(case,statement,values=None):
        commands.append(statement)
        if statement.startswith('SELECT last_value,is_called'):
            assert state['created']
            return [(1,state['called'])]
        if statement.startswith('SELECT '):
            return [('event_trigger','synthetic_membership_retirement_failure'),
                ('function','synthetic_membership_retirement_failure'),
                ('sequence','synthetic_membership_retirement_failure_marker')] if state['created'] else []
        if statement.startswith('CREATE SEQUENCE'):
            paths=list(tmp_path.glob('membership-retirement-event-restoration-required-*.json'))
            assert len(paths)==1 and json.loads(paths[0].read_text())['before']==[]
            assert "WHEN TAG IN ('CREATE FUNCTION')" in statement
            assert statement.index('identity_membership_retirement_immutable')<statement.index('pg_catalog.nextval(')<statement.index("RAISE EXCEPTION USING ERRCODE='P0001'")
            assert 'GRANT USAGE ON SEQUENCE public.synthetic_membership_retirement_failure_marker TO identity_migrator;' in statement
            assert statement.count('GRANT ')==1
            state['created']=True
            if create_failure:raise RuntimeError('synthetic_create_after_commit')
        if statement.startswith('DROP EVENT TRIGGER'):
            assert 'DROP FUNCTION IF EXISTS public.synthetic_membership_retirement_failure()' in statement
            assert 'DROP SEQUENCE IF EXISTS public.synthetic_membership_retirement_failure_marker' in statement
            if cleanup_fails:raise RuntimeError('synthetic_cleanup_failed')
            state['created']=False
        return []
    runner.admin_sql=sql
    return runner,state,commands


@pytest.mark.parametrize('failure',['create_after_commit','body'])
def test_after_create_function_failure_fixture_restores_exact_objects(tmp_path,failure):
    import stat
    runner,state,commands=failure_fixture_mock(tmp_path,create_failure=failure=='create_after_commit')
    with pytest.raises(RuntimeError,match='synthetic_'):
        with runner.failure_fixture('failure'):raise RuntimeError('synthetic_body')
    assert state['created'] is False
    paths=list(tmp_path.glob('membership-retirement-event-restored-*.json'))
    assert len(paths)==1 and stat.S_IMODE(paths[0].stat().st_mode)==0o600


@pytest.mark.parametrize('signame',['SIGINT','SIGTERM'])
@pytest.mark.parametrize('cleanup_fails',[False,True])
def test_failure_fixture_signal_and_failed_cleanup_keep_witness(tmp_path,monkeypatch,signame,cleanup_fails):
    import qualify_membership_retirement as retirement
    signal=retirement.signal
    originals={signal.SIGINT:object(),signal.SIGTERM:object()};handlers=dict(originals)
    monkeypatch.setattr(signal,'getsignal',lambda sig:handlers[sig])
    monkeypatch.setattr(signal,'signal',lambda sig,handler:handlers.__setitem__(sig,handler))
    runner,state,commands=failure_fixture_mock(tmp_path,cleanup_fails=cleanup_fails)
    expected='synthetic_cleanup_failed' if cleanup_fails else 'profile_fixture_interrupted'
    with pytest.raises(RuntimeError,match=expected):
        with runner.failure_fixture('failure'):handlers[getattr(signal,signame)](getattr(signal,signame),None)
    assert handlers==originals
    assert len(list(tmp_path.glob('membership-retirement-event-restoration-required-*.json')))==1
    assert len(list(tmp_path.glob('membership-retirement-event-restored-*.json')))==(0 if cleanup_fails else 1)
    assert state['created'] is cleanup_fails


@pytest.mark.parametrize('kind',['event_trigger','function','sequence'])
def test_failure_fixture_refuses_preexisting_object_without_mutation(tmp_path,kind):
    import qualify_membership_retirement as retirement
    runner=retirement.MembershipRetirementQualification(tmp_path,{})
    commands=[]
    def sql(case,statement,values=None):commands.append(statement);return [(kind,'synthetic_membership_retirement_failure')]
    runner.admin_sql=sql
    with pytest.raises(AssertionError,match='already_exists'):
        with runner.failure_fixture('failure'):raise AssertionError('body_reached')
    assert len(commands)==1 and commands[0].startswith('SELECT ')
    assert not list(tmp_path.glob('membership-retirement-event-*.json'))


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
        witnesses=list(tmp_path.glob('membership-retirement-event-fired-*.json'))
        assert len(witnesses)==1
        assert json.loads(witnesses[0].read_text())=={'case':'failure','marker_before':[1,False],'marker_after':[1,True],'new_guard_observed':True}
    else:
        with pytest.raises(AssertionError,match='failure_fixture_not_fired'):execute()
        assert not list(tmp_path.glob('membership-retirement-event-fired-*.json'))
    assert state['created'] is False
    assert len(list(tmp_path.glob('membership-retirement-event-restored-*.json')))==1


def test_failure_marker_cannot_start_called(tmp_path):
    runner,state,commands=failure_fixture_mock(tmp_path,initially_called=True)
    with pytest.raises(AssertionError,match='failure_marker_initially_called'):
        with runner.failure_fixture('failure'):raise AssertionError('body_reached')
    assert state['created'] is False
    assert len(list(tmp_path.glob('membership-retirement-event-restored-*.json')))==1


@pytest.mark.parametrize('defect',['missing_reference','modified_reference','source_pins'])
def test_trusted_retirement_reference_refuses_untrusted_input(tmp_path,monkeypatch,defect):
    import json
    from test_projection_qualification import digest
    b=qualification.baseline;calls=[]
    monkeypatch.setattr(b,'trusted_membership_retention_reference',lambda:calls.append('retention'))
    monkeypatch.setattr(b,'HERE',tmp_path)
    (tmp_path/'versions').mkdir();(tmp_path/'versions/0013_membership_retirement.py').write_bytes(b'source')
    (tmp_path/'source-pins.json').write_text('{}')
    content=json.dumps({'source_pins':{},'migration_sha256':digest(b'source'),'membership_retirement':{}}).encode()
    path=tmp_path/'membership-retirement-reference.json';path.write_bytes(content)
    monkeypatch.setattr(b,'MEMBERSHIP_RETIREMENT_REFERENCE_SHA256',digest(content))
    if defect=='missing_reference':path.unlink()
    elif defect=='modified_reference':path.write_bytes(content+b' ')
    else:(tmp_path/'source-pins.json').write_text('{"changed":"pin"}')
    with pytest.raises(b.BaselineError,match='identity_reference_unavailable'):b.trusted_membership_retirement_reference()
    assert calls==['retention']


@pytest.mark.parametrize('is_owner',[False,True])
def test_actual_seed_function_matches_qualified_membership_upsert(is_owner):
    import ast
    from types import SimpleNamespace
    import qualify_membership_retirement as retirement
    path=qualification.OWNER.parents[2]/'scripts/seed.py'
    tree=ast.parse(path.read_text(),filename=str(path))
    functions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='seed_org_member']
    assert len(functions)==1
    calls=[]
    class Client:
        def schema(self,name):calls.append(('schema',name));return self
        def table(self,name):calls.append(('table',name));return self
        def upsert(self,payload,**options):calls.append(('upsert',payload,options));return self
        def execute(self):calls.append(('execute',));return SimpleNamespace(data=[{'id':'123'}])
    namespace={'supabase':Client()}
    # Compile only the selected function; seed module credentials and setup never execute.
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(path),'exec'),namespace)
    result=namespace['seed_org_member']('org-fixture','account-fixture',is_owner)
    assert result==123 and type(result) is int
    assert calls==[('schema','identity'),('table','org_member'),
        ('upsert',{'org_id':'org-fixture','user_id':'account-fixture','is_owner':is_owner,'deleted_at':None},
            {'on_conflict':'org_id,user_id','returning':'representation'}),('execute',)]
    if is_owner:
        schema,table=calls[0][1],calls[1][1];payload,options=calls[2][1:]
        values={'org_id':'CAST(:org AS uuid)','user_id':'CAST(:account AS uuid)','is_owner':'true','deleted_at':'NULL'}
        columns=','.join(payload)
        assert retirement.MembershipRetirementQualification.seed_statement()==(
            'INSERT INTO '+schema+'.'+table+'('+columns+') VALUES('+','.join(values[key] for key in payload)+') ON CONFLICT('
            +options['on_conflict']+') DO UPDATE SET is_owner=excluded.is_owner,deleted_at=excluded.deleted_at')
