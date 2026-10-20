"""Fail-closed head4 provenance and recorder regression guards; no DB operations."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qualify_identity_baseline as qualification
from test_projection_qualification import recorder_fixture, digest


def test_new_head_requires_organization_catalog(monkeypatch):
    baseline=qualification.baseline
    monkeypatch.setattr(baseline, 'verify_owned_history', lambda c: baseline.ORGANIZATION_REVISION)
    monkeypatch.setattr(baseline, 'verify_legacy_history', lambda c: None)
    kinds=[]
    monkeypatch.setattr(baseline, 'verify_catalog', lambda c,k: kinds.append(k))
    baseline.verify_owned_postcondition(object(), require_head=True)
    assert kinds==['organization']
    monkeypatch.setattr(baseline, 'verify_owned_history', lambda c: baseline.PROJECTION_REVISION)
    with pytest.raises(baseline.BaselineError, match='identity_unknown_history'):
        baseline.verify_owned_postcondition(object(), require_head=True)


@pytest.mark.parametrize('corruption', [None,'reference.json','actor-reference.json','projection-reference.json',
    'versions/0002_actor_registry.py','versions/0003_current_account_actor.py','versions/0004_current_account_organization.py'])
def test_new_reference_keeps_all_historical_evidence(tmp_path, monkeypatch, corruption):
    baseline=qualification.baseline
    for name in ['source-pins.json','reference.json','actor-reference.json','projection-reference.json',
        'versions/0002_actor_registry.py','versions/0003_current_account_actor.py','versions/0004_current_account_organization.py']:
        path=tmp_path/name;path.parent.mkdir(exist_ok=True)
        shutil.copyfile(qualification.OWNER/name,path)
    reference={'source_pins':json.loads((tmp_path/'source-pins.json').read_bytes()),
        'migration_sha256':digest((tmp_path/'versions/0004_current_account_organization.py').read_bytes()),'organization':{}}
    content=json.dumps(reference).encode();(tmp_path/'organization-reference.json').write_bytes(content)
    monkeypatch.setattr(baseline,'HERE',tmp_path)
    monkeypatch.setattr(baseline,'ORGANIZATION_REFERENCE_SHA256',digest(content))
    assert baseline.trusted_organization_reference()=={}
    if corruption:
        (tmp_path/corruption).write_bytes(b'corrupted historical evidence')
        with pytest.raises(baseline.BaselineError,match='identity_reference_unavailable'):
            baseline.trusted_organization_reference()


def organization_recorder(tmp_path,monkeypatch,mutation=None):
    runner,statements=recorder_fixture(tmp_path,monkeypatch,mutation)
    (tmp_path/'identity_baseline.py').write_text('ORGANIZATION_REFERENCE_SHA256 = None\n')
    (tmp_path/'versions/0004_current_account_organization.py').write_text('ORGANIZATION_SCHEMA_SQL = "captured organization"\n')
    for name in ['reference.json','actor-reference.json','projection-reference.json']:
        (tmp_path/name).write_text('{}')
    runner.private={'owner_urls':{'organization_reference':'synthetic'}}
    monkeypatch.setattr(qualification.baseline,'trusted_projection_reference',lambda: {})
    return runner,statements


@pytest.mark.parametrize('mutation',['identity_baseline.py','source-pins.json','reference.json','actor-reference.json',
    'projection-reference.json','versions/0001_baseline.py','versions/0002_actor_registry.py',
    'versions/0003_current_account_actor.py','versions/0004_current_account_organization.py'])
def test_organization_recorder_refuses_changed_captured_sources(tmp_path,monkeypatch,mutation):
    runner,statements=organization_recorder(tmp_path,monkeypatch,mutation)
    with pytest.raises(AssertionError,match='organization_reference_source_changed'):
        runner.record_organization_reference()
    assert statements==['captured baseline','captured actor','captured projection','captured organization']
    assert not (tmp_path/'organization-reference.json').exists()


def test_organization_recorder_exclusive_and_manual_pin(tmp_path,monkeypatch):
    runner,_=organization_recorder(tmp_path,monkeypatch)
    helper=(tmp_path/'identity_baseline.py').read_bytes()
    temporary=tmp_path/'.organization-reference-recording';temporary.write_bytes(b'foreign evidence')
    with pytest.raises(FileExistsError): runner.record_organization_reference()
    assert temporary.read_bytes()==b'foreign evidence'
    temporary.unlink()
    runner.record_organization_reference()
    assert (tmp_path/'identity_baseline.py').read_bytes()==helper
    assert runner.records[-1]['pin_update_required'] is True
    with pytest.raises(AssertionError,match='organization_reference_already_exists'):
        runner.record_organization_reference()


def test_supported_seed_org_member_keeps_conflict_target_and_unretire_payload():
    # Load only the actual function AST: importing seed.py would configure clients.
    import ast
    source=ast.parse((qualification.ROOT/'scripts/seed.py').read_text())
    function=next(node for node in source.body if isinstance(node,ast.FunctionDef) and node.name=='seed_org_member')
    calls=[]
    class Client:
        def schema(self,name):calls.append(('schema',name));return self
        def table(self,name):calls.append(('table',name));return self
        def upsert(self,payload,**kwargs):calls.append(('upsert',payload,kwargs));return self
        def execute(self):
            class Result:data=[{'id':42}]
            return Result()
    namespace={'supabase':Client()}
    exec(compile(ast.Module(body=[function],type_ignores=[]),'scripts/seed.py','exec'),namespace)
    assert namespace['seed_org_member']('org','account',True)==42
    assert calls==[('schema','identity'),('table','org_member'),('upsert',
        {'org_id':'org','user_id':'account','is_owner':True,'deleted_at':None},
        {'on_conflict':'org_id,user_id','returning':'representation'})]


@pytest.mark.parametrize('preexisting',[False,True])
@pytest.mark.parametrize('failure',[None,'CREATE','INSERT'])
def test_shared_row_fixtures_preserve_direct_acl_entries_and_order(tmp_path,preexisting,failure):
    # Model only exact ACL effects, including order of schema entries. A blanket
    # REVOKE/regrant would move postgres behind reader and fail the final equality.
    query=qualification.FIXTURE_REFERENCE_ACLS_SQL
    assert 'has_schema_privilege' not in query and 'has_column_privilege' not in query
    assert query.count("a.grantor=(SELECT oid FROM pg_roles WHERE rolname='identity_migrator')")==2
    assert query.count("a.grantee=(SELECT oid FROM pg_roles WHERE rolname='postgres')")==2
    initial={'schema':['owner','postgres','reader'] if preexisting else ['owner'],
             'users':['postgres'] if preexisting else [],'org':['postgres'] if preexisting else []}
    acls={key:list(value) for key,value in initial.items()}
    calls=[]
    runner=qualification.Qualification(tmp_path,{})
    def sql(case,statement,values=None,role='owner_urls'):
        calls.append(statement)
        if failure=='CREATE' and statement.startswith('CREATE SCHEMA finance'):raise RuntimeError('synthetic_fixture_failure')
        if failure=='INSERT' and statement.startswith('INSERT INTO finance'):raise RuntimeError('synthetic_fixture_failure')
        if statement==query:
            return [(name,','.join(acls[name]) or None,'postgres' in acls[name]) for name in sorted(acls)]
        if statement.startswith('GRANT USAGE ON SCHEMA identity TO postgres;'):
            for entries in acls.values():
                if 'postgres' not in entries:entries.append('postgres')
        if statement.startswith('REVOKE '):
            for command in statement.split(';'):
                names=['schema'] if 'SCHEMA' in command else [name for name in ['users','org'] if 'identity.'+name in command]
                for name in names:acls[name].remove('postgres')
        return []
    runner.sql=sql
    if failure:
        with pytest.raises(RuntimeError,match='synthetic_fixture_failure'):runner.row_fixtures('synthetic')
    else:runner.row_fixtures('synthetic')
    assert acls==initial
    if preexisting:assert not any(statement.startswith('REVOKE ') for statement in calls)


@pytest.mark.parametrize('problem',['missing','corrupt','wrong-pin'])
def test_organization_reference_own_file_and_fixed_digest(tmp_path,monkeypatch,problem):
    baseline=qualification.baseline
    monkeypatch.setattr(baseline,'trusted_projection_reference',lambda: {})
    monkeypatch.setattr(baseline,'HERE',tmp_path)
    content=b'{"organization":{}}'
    monkeypatch.setattr(baseline,'ORGANIZATION_REFERENCE_SHA256',digest(content))
    if problem!='missing':(tmp_path/'organization-reference.json').write_bytes(content if problem=='wrong-pin' else b'corrupt')
    if problem=='wrong-pin':monkeypatch.setattr(baseline,'ORGANIZATION_REFERENCE_SHA256','0'*64)
    with pytest.raises(baseline.BaselineError,match='identity_reference_unavailable'):
        baseline.trusted_organization_reference()


def test_data_state_normalizes_only_requested_membership_revision(tmp_path,monkeypatch):
    rows={'org_member':{'id':1,'revision':2,'user_id':'account'},'users':{'id':'account','revision':'must-stay'}}
    queries=[]
    class Result:
        def __init__(self,value):self.value=value
        def scalar_one(self):return self.value
        def scalars(self):return self
        def all(self):return self.value
        def __iter__(self):return iter(self.value)
    class Connection:
        class dialect:
            class identifier_preparer:
                @staticmethod
                def quote(name):return name
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def execute(self,statement,params=None):
            if 'information_schema.tables' in str(statement):return Result(['org_member','users'])
            return Result(None)
        def exec_driver_sql(self,statement):
            queries.append(statement)
            name='org_member' if 'identity.org_member' in statement else 'users'
            value=dict(rows[name])
            if "-'revision'" in statement:value.pop('revision')
            return Result([value])
    class Engine:
        def connect(self):return Connection()
        def dispose(self):pass
    monkeypatch.setattr(qualification,'engine',lambda url:Engine())
    runner=qualification.Qualification(tmp_path,{'owner_urls':{'synthetic':'unused'}})
    full=runner.data_state('synthetic')
    normalized=runner.data_state('synthetic',membership_without_revision=True)
    assert normalized['users']==full['users']
    assert normalized['org_member']!=full['org_member']
    assert queries.count("SELECT to_jsonb(t)-'revision' FROM identity.org_member t")==1
    rows['org_member']['revision']=999
    assert runner.data_state('synthetic',membership_without_revision=True)==normalized
    assert runner.data_state('synthetic')!=full
    rows['org_member']['user_id']='different-account'
    assert runner.data_state('synthetic',membership_without_revision=True)!=normalized
