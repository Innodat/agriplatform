"""Membership instance binding and historical source custody regressions."""
from pathlib import Path
import importlib.util
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_identity_baseline as qualification


def revision_module():
    path=qualification.OWNER/'versions/0011_membership_binding.py'
    spec=importlib.util.spec_from_file_location('membership_binding_revision',path)
    revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
    return revision


def test_membership_binding_guard_and_revision_contract():
    revision=revision_module();sql=revision.MEMBERSHIP_BINDING_SQL
    assert revision.revision=='identity_0011' and revision.down_revision=='identity_0010'
    for field in ['id','org_id','user_id']:
        assert f'NEW.{field} IS DISTINCT FROM OLD.{field}' in sql
    assert sql.index('identity_membership_binding_immutable') < sql.index("IF TG_OP = 'INSERT'")
    assert "ERRCODE = '23514'" in sql and "CONSTRAINT = 'org_member_binding_immutable'" in sql
    assert 'CREATE OR REPLACE FUNCTION identity.guard_org_member_revision()' in sql
    assert 'RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp' in sql
    assert "NEW.revision := 1" in sql and 'NEW.revision := OLD.revision + 1' in sql
    assert 'NEW.revision := OLD.revision' in sql and '9223372036854775807' in sql
    assert not any(word in sql for word in ['GRANT ','REVOKE ','ALTER ','CREATE TRIGGER','SECURITY DEFINER','INSERT INTO','UPDATE identity.','DELETE ','LOCK '])
    with pytest.raises(RuntimeError,match='Destructive'):revision.downgrade()


def test_membership_binding_head_and_historical_head(monkeypatch):
    b=qualification.baseline
    assert b.MEMBERSHIP_BINDING_REVISION=='identity_0011'
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.MEMBERSHIP_BINDING_REVISION)
    monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
    seen=[];monkeypatch.setattr(b,'verify_catalog',lambda c,k:seen.append(k))
    b.verify_owned_postcondition(object())
    assert seen==['membership_binding']
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.TOKEN_HOOK_REVISION)
    b.verify_owned_postcondition(object())
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):b.verify_owned_postcondition(object(),require_head=True)


@pytest.mark.parametrize('mutation',[None,'identity_baseline.py','source-pins.json','reference.json','actor-reference.json',
    'projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json',
    'target-reference.json','profile-reference.json','legacy-role-reference.json','token-hook-reference.json','versions/0001_baseline.py','versions/0002_actor_registry.py',
    'versions/0003_current_account_actor.py','versions/0004_current_account_organization.py','versions/0005_operator_authority.py',
    'versions/0006_actor_command.py','versions/0007_organization_targets.py','versions/0008_profile_fields.py','versions/0009_legacy_roles.py','versions/0010_token_hook.py','versions/0011_membership_binding.py'])
def test_recorder_full_source_custody_and_exclusive_publication(tmp_path,monkeypatch,mutation):
    from test_actor_command_qualification import recorder
    from test_projection_qualification import digest
    import stat
    runner,statements=recorder(tmp_path,monkeypatch,mutation)
    (tmp_path/'identity_baseline.py').write_text('MEMBERSHIP_BINDING_REFERENCE_SHA256 = None\n')
    for name in ['command-reference.json','target-reference.json','profile-reference.json','legacy-role-reference.json','token-hook-reference.json']:(tmp_path/name).write_text('{}')
    for number,name,symbol in [(7,'organization_targets','TARGET_SCHEMA_SQL'),(8,'profile_fields','PROFILE_FIELDS_SQL'),(9,'legacy_roles','LEGACY_ROLES_SQL'),(10,'token_hook','TOKEN_HOOK_SQL'),(11,'membership_binding','MEMBERSHIP_BINDING_SQL')]:
        (tmp_path/f'versions/{number:04d}_{name}.py').write_text(f'{symbol} = "captured {name}"\n')
    runner.private={'owner_urls':{'membership_binding_reference':'synthetic'}}
    b=qualification.baseline
    monkeypatch.setattr(b,'trusted_token_hook_reference',lambda:{})
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
        with pytest.raises(AssertionError,match='membership_binding_reference_source_changed'):runner.record_membership_binding_reference()
        assert not (tmp_path/'membership-binding-reference.json').exists()
    else:
        runner.record_membership_binding_reference()
        assert (tmp_path/'identity_baseline.py').read_bytes()==helper
        assert runner.records[-1]['pin_update_required'] is True
        assert stat.S_IMODE((tmp_path/'membership-binding-reference.json').stat().st_mode)==0o600
        with pytest.raises(AssertionError,match='membership_binding_reference_already_exists'):runner.record_membership_binding_reference()
    assert len(preflight_calls)==2
    assert statements==[deadline,'captured baseline','captured actor','captured projection','captured organization','captured authority','captured command',
                       'captured organization_targets','captured profile_fields','captured legacy_roles','captured token_hook','captured membership_binding',deadline]


def test_membership_binding_reference_binds_prior_trust_and_own_source(tmp_path,monkeypatch):
    import json
    from test_projection_qualification import digest
    b=qualification.baseline;calls=[]
    monkeypatch.setattr(b,'trusted_token_hook_reference',lambda:calls.append('token_hook'))
    monkeypatch.setattr(b,'HERE',tmp_path)
    (tmp_path/'versions').mkdir();(tmp_path/'versions/0011_membership_binding.py').write_bytes(b'source')
    (tmp_path/'source-pins.json').write_text('{}')
    reference={'source_pins':{},'migration_sha256':digest(b'source'),'membership_binding':{}}
    content=json.dumps(reference).encode();(tmp_path/'membership-binding-reference.json').write_bytes(content)
    monkeypatch.setattr(b,'MEMBERSHIP_BINDING_REFERENCE_SHA256',digest(content))
    assert b.trusted_membership_binding_reference()=={} and calls==['token_hook']
    (tmp_path/'versions/0011_membership_binding.py').write_bytes(b'drift')
    with pytest.raises(b.BaselineError,match='identity_reference_unavailable'):b.trusted_membership_binding_reference()



@pytest.mark.parametrize('module,args',[('qualify_identity_baseline',['--record-membership-binding-reference']),('qualify_membership_binding',[])])
def test_optimized_execution_refused_before_fixture(module,args):
    import subprocess
    source="""import importlib,sys
sys.path.insert(0,sys.argv[1])
module=importlib.import_module(sys.argv[2])
module.fixture=lambda: (_ for _ in ()).throw(RuntimeError('fixture_reached'))
sys.argv=[module.__file__]+sys.argv[3:]
try:module.main()
except RuntimeError as error:
    if str(error) not in {'membership_binding_reference_optimized_python_prohibited','membership_binding_qualification_optimized_python_prohibited'}:raise RuntimeError('wrong_guard')
else:raise RuntimeError('missing_guard')
"""
    result=subprocess.run([sys.executable,'-I','-B','-O','-c',source,str(Path(__file__).resolve().parent),module,*args],capture_output=True,text=True,timeout=10)
    assert result.returncode==0 and result.stdout==result.stderr==''


@pytest.mark.parametrize('failure',['create_after_commit','snapshot'])
def test_legacy_failure_fixture_restores_after_mutation_or_body_failure(tmp_path,failure):
    import qualify_membership_binding as legacy
    import json,stat
    runner=legacy.MembershipBindingQualification(tmp_path,{})
    state={'created':False};commands=[]
    def sql(case,statement,values=None):
        commands.append(statement)
        if statement.startswith('SELECT '):return [('event_trigger','synthetic_membership_binding_failure')] if state['created'] else []
        if statement.startswith('CREATE FUNCTION'):
            witnesses=list(tmp_path.glob('membership-binding-event-restoration-required-*.json'))
            assert len(witnesses)==1 and json.loads(witnesses[0].read_text())['before']==[]
            state['created']=True
            if failure=='create_after_commit':raise RuntimeError('synthetic_create_after_commit')
        if statement.startswith('DROP EVENT TRIGGER'):state['created']=False
        return []
    runner.admin_sql=sql
    with pytest.raises(RuntimeError,match='synthetic_'):
        with runner.failure_fixture('failure'):raise RuntimeError('synthetic_snapshot')
    assert state['created'] is False
    paths=list(tmp_path.glob('membership-binding-event-restored-*.json'))
    assert len(paths)==1 and stat.S_IMODE(paths[0].stat().st_mode)==0o600


def test_legacy_failure_fixture_refuses_existing_objects(tmp_path):
    import qualify_membership_binding as legacy
    runner=legacy.MembershipBindingQualification(tmp_path,{})
    commands=[]
    def sql(case,statement,values=None):commands.append(statement);return [('event_trigger','synthetic_membership_binding_failure')]
    runner.admin_sql=sql
    with pytest.raises(AssertionError,match='already_exists'):
        with runner.failure_fixture('failure'):raise RuntimeError('body_reached')
    assert len(commands)==1 and commands[0].startswith('SELECT ')
    assert not list(tmp_path.glob('membership-binding-event-*.json'))


@pytest.mark.parametrize('signame',['SIGINT','SIGTERM'])
@pytest.mark.parametrize('cleanup_fails',[False,True])
def test_installed_signal_unwinds_and_cleanup_failure_retains_required_witness(tmp_path,monkeypatch,signame,cleanup_fails):
    import qualify_membership_binding as legacy
    signal=legacy.signal
    originals={signal.SIGINT:object(),signal.SIGTERM:object()};handlers=dict(originals)
    monkeypatch.setattr(signal,'getsignal',lambda sig:handlers[sig])
    monkeypatch.setattr(signal,'signal',lambda sig,handler:handlers.__setitem__(sig,handler))
    runner=legacy.MembershipBindingQualification(tmp_path,{})
    state={'created':False};commands=[]
    def sql(case,statement,values=None):
        commands.append(statement)
        if statement.startswith('SELECT '):return [('event_trigger','synthetic_membership_binding_failure')] if state['created'] else []
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
    assert len(list(tmp_path.glob('membership-binding-event-restoration-required-*.json')))==1
    assert len(list(tmp_path.glob('membership-binding-event-restored-*.json')))==(0 if cleanup_fails else 1)
    assert state['created'] is cleanup_fails



@pytest.mark.parametrize('corruption',['other_body','helper_acl','helper_owner','helper_signature','helper_language','helper_search_path','removed'])
def test_per_function_comparison_refuses_unrelated_or_declaration_changes(corruption):
    import qualify_membership_binding as legacy
    import copy
    old=[['identity','guard_org_member_revision','','identity_migrator',
          "CREATE OR REPLACE FUNCTION identity.guard_org_member_revision()\n RETURNS TABLE(role text)\n LANGUAGE plpgsql\n SECURITY DEFINER\n SET search_path TO 'public', 'identity'\nAS $function$old body$function$\n",'acl'],
         ['identity','auth_hook','event jsonb','identity_migrator','hook definition','hook acl']]
    new=copy.deepcopy(old)
    new[0][4]=new[0][4].replace('old body','new body')
    legacy.MembershipBindingQualification.verify_function_delta(old,new)
    if corruption=='other_body':new[1][4]='changed hook'
    elif corruption=='helper_acl':new[0][5]='changed acl'
    elif corruption=='helper_owner':new[0][3]='changed owner'
    elif corruption=='helper_signature':new[0][4]=new[0][4].replace('TABLE(role text)','TABLE(role bigint)')
    elif corruption=='helper_language':new[0][4]=new[0][4].replace('LANGUAGE plpgsql','LANGUAGE sql')
    elif corruption=='helper_search_path':new[0][4]=new[0][4].replace("'public', 'identity'","'pg_catalog', 'pg_temp'")
    elif corruption=='removed':new.pop()
    with pytest.raises(AssertionError,match='membership_binding_'):legacy.MembershipBindingQualification.verify_function_delta(old,new)



@pytest.mark.parametrize('signame',['SIGINT','SIGTERM'])
@pytest.mark.parametrize('cleanup_fails',[False,True])
def test_role_edge_signal_unwind_and_failed_cleanup_keep_recovery_evidence(tmp_path,monkeypatch,signame,cleanup_fails):
    import qualify_membership_binding as legacy
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
    runner=legacy.MembershipBindingQualification(tmp_path,{})
    runner.admin=lambda case:Admin();runner.passed=lambda *a,**k:None
    expected='synthetic_cleanup_failed' if cleanup_fails else 'membership_binding_fixture_interrupted'
    with pytest.raises(RuntimeError,match=expected):
        with runner.fixture_execution('clean'):
            handlers[getattr(signal,signame)](getattr(signal,signame),None)
    assert any(command.startswith('REVOKE ') for command in commands)
    assert handlers==originals and commands[-1]=='dispose'
    assert len(list(tmp_path.glob('membership-binding-role-restoration-required-*.json')))==1
    assert len(list(tmp_path.glob('membership-binding-role-restored-*.json')))==(0 if cleanup_fails else 1)
    assert state['granted'] is cleanup_fails


@pytest.mark.parametrize('grant_failure',['before_mutation','after_commit'])
@pytest.mark.parametrize('cleanup_fails',[False,True])
def test_role_edge_grant_failure_restores_exact_state_and_handlers(tmp_path,monkeypatch,grant_failure,cleanup_fails):
    import qualify_membership_binding as hook
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
                for role in ['authenticated','service_role']] if state['granted'] else [])
    class Admin:
        @contextmanager
        def begin(self):
            yield self
            if commands[-1].startswith('GRANT ') and grant_failure=='after_commit':
                raise RuntimeError('synthetic_grant_after_commit')
        def execute(self,statement):
            statement=str(statement);commands.append(statement)
            if statement.startswith('GRANT '):
                assert len(list(tmp_path.glob('membership-binding-role-restoration-required-*.json')))==1
                if grant_failure=='before_mutation':raise RuntimeError('synthetic_grant_before_mutation')
                state['granted']=True
            if statement.startswith('REVOKE '):
                if cleanup_fails:raise RuntimeError('synthetic_cleanup_failed')
                state['granted']=False
            return Result()
        def dispose(self):commands.append('dispose')
    runner=hook.MembershipBindingQualification(tmp_path,{})
    runner.admin=lambda case:Admin();runner.passed=lambda *a,**k:None
    expected='synthetic_cleanup_failed' if cleanup_fails else 'synthetic_grant_'
    with pytest.raises(RuntimeError,match=expected):
        with runner.fixture_execution('clean'):raise AssertionError('body_reached')
    assert any(command.startswith('REVOKE ') for command in commands)
    assert handlers==originals and commands[-1]=='dispose'
    required=list(tmp_path.glob('membership-binding-role-restoration-required-*.json'))
    restored=list(tmp_path.glob('membership-binding-role-restored-*.json'))
    assert len(required)==1 and json.loads(required[0].read_text())['before']==[]
    assert len(restored)==(0 if cleanup_fails else 1)
    if restored:
        receipt=json.loads(restored[0].read_text())
        assert receipt['before']==receipt['after']==[] and receipt['exact_edges'] is True
    assert state['granted'] is (cleanup_fails and grant_failure=='after_commit')


@pytest.mark.parametrize('missing',['malformed','00000000-0000-0000-0000-000000000000','duplicate','valid'])
def test_spare_fixture_uuid_is_canonical_nonnil_and_distinct(tmp_path,missing):
    import qualify_membership_binding as hook
    import json,uuid
    row={key:str(uuid.uuid4()) for key in ['account','other','spare','org','other_org','spare_org']}
    row.update({key:str(number) for number,key in enumerate(['member','other_member','other_org_member','role','deleted_role'],1)})
    if missing=='duplicate':row['spare']=row['account']
    elif missing!='valid':row['spare']=missing
    (tmp_path/'member-binding-fixtures.json').write_text(json.dumps({'characterization':row,'clean':row}))
    runner=hook.MembershipBindingQualification(tmp_path,{group:{case:'' for case in hook.REQUIRED_CASES}
        for group in ['owner_urls','runtime_urls','databases']})
    if missing=='valid':runner.validate_targets()
    else:
        with pytest.raises((AssertionError,ValueError)):runner.validate_targets()



def binding_fixture(tmp_path):
    import qualify_membership_binding as binding
    import json,uuid
    row={key:str(uuid.uuid4()) for key in ['account','other','spare','org','other_org','spare_org']}
    row.update({key:str(number) for number,key in enumerate(['member','other_member','other_org_member','role','deleted_role'],1)})
    (tmp_path/'member-binding-fixtures.json').write_text(json.dumps({'characterization':row,'clean':row}))
    (tmp_path/'run.json').write_text(json.dumps({'run_id':str(uuid.uuid4())}))
    runner=binding.MembershipBindingQualification(tmp_path,{group:{case:'' for case in binding.REQUIRED_CASES}
        for group in ['owner_urls','runtime_urls','databases']})
    runner.validate_targets()
    return runner,row


@pytest.mark.parametrize('defect',['duplicate','numeric_duplicate','missing','malformed','headroom'])
def test_fixture_member_preconditions_refuse_before_database(tmp_path,defect):
    import json
    runner,row=binding_fixture(tmp_path)
    if defect=='duplicate':row['other_member']=row['member']
    elif defect=='numeric_duplicate':row['other_member']='0'+row['member']
    elif defect=='missing':row.pop('other_member')
    elif defect=='malformed':row['member']='not-an-id'
    else:row['member']=str(9223372036854775807-999999)
    (tmp_path/'member-binding-fixtures.json').write_text(json.dumps({'characterization':row,'clean':row}))
    runner.sql=lambda *a: (_ for _ in ()).throw(RuntimeError('database_reached'))
    with pytest.raises(AssertionError):runner.validate_targets()


@pytest.mark.parametrize('defect',['missing','wrong_account','wrong_org','collision','valid'])
def test_fixture_actual_rows_precheck_is_bounded_and_exact(tmp_path,defect):
    runner,v=binding_fixture(tmp_path)
    rows=[(v['member'],v['account'],v['org']),(v['other_member'],v['other'],v['org']),
          (v['other_org_member'],v['account'],v['other_org'])]
    if defect=='missing':rows.pop()
    elif defect=='wrong_account':rows[1]=(v['other_member'],v['account'],v['org'])
    elif defect=='wrong_org':rows[2]=(v['other_org_member'],v['account'],v['org'])
    elif defect=='collision':rows.append((str(int(v['member'])+1000000),v['spare'],v['spare_org']))
    calls=[]
    def sql(case,statement,values):
        calls.append((case,statement,values))
        assert 'WHERE id IN (' in statement and 'CAST(:member AS bigint)+1000000' in statement
        assert values==v
        return rows
    runner.sql=sql
    if defect=='valid':runner.fixture_rows('clean')
    else:
        with pytest.raises(AssertionError,match='fixture_rows_mismatch_or_id_collision'):runner.fixture_rows('clean')
    assert len(calls)==1


@pytest.mark.parametrize('defect',['proof','run_id','fixture_sha256','field_duplicate','transition','original','valid'])
def test_characterization_requires_current_fixture_and_three_exact_transitions(tmp_path,defect):
    runner,v=binding_fixture(tmp_path)
    before={'id':int(v['member']),'org_id':v['org'],'user_id':v['account'],'revision':7,'is_owner':True}
    replacements={'id':int(v['member'])+1000000,'org_id':v['spare_org'],'user_id':v['spare']}
    observed=[{'field':field,'before':dict(before),'after':dict(before,**{field:value,'revision':8}),
               'dependent_roles_removed_rollback_only':field=='id'} for field,value in replacements.items()]
    witness={'binding':runner.characterization_binding(),'head':'identity_0010','unchanged_data':True,'observed':observed}
    if defect in ['proof','run_id','fixture_sha256']:witness['binding'][defect]='stale'
    elif defect=='field_duplicate':observed[2]=observed[1]
    elif defect=='transition':observed[0]['after']['is_owner']=False
    elif defect=='original':observed[0]['before']['org_id']=v['other_org']
    if defect=='valid':runner.verify_characterization(witness)
    else:
        with pytest.raises(AssertionError,match='membership_binding_characterization_'):runner.verify_characterization(witness)
