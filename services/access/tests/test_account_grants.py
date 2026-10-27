"""Closed general account provisioning contracts, independent from organization grants."""
import json
import sys
from pathlib import Path
from uuid import uuid4
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from access_operator_input import parse_command,CommandValidationError
from access_operator import canonical_command

def document(command='account_grant.assign',**payload):
    return dict(schema_version=1,operation_id=str(uuid4()),command=command,scope={'kind':'platform'},reason_code='synthetic_fixture',payload=dict(account_id=str(uuid4()),permission='pts.use',**payload))

def test_planned_account_assignment_is_typed():
    doc=document(expected_absent=True)
    command=parse_command(json.dumps(doc).encode())
    assert command.command=='account_grant.assign'
    assert json.loads(canonical_command(command))['payload']==doc['payload']

def test_planned_account_update_and_revocation_require_exact_uuid_grant():
    for name in ('account_grant.assign','account_grant.revoke'):
        doc=document(name,grant_id=str(uuid4()),expected_revision='2')
        assert parse_command(json.dumps(doc).encode()).payload.grant_id==doc['payload']['grant_id']
        upper=str(uuid4()).upper();doc['payload']['grant_id']=upper
        assert json.loads(canonical_command(parse_command(json.dumps(doc).encode())))['payload']['grant_id']==upper.lower()
        for invalid in ('legacy-composite',None):
            doc['payload']['grant_id']=invalid
            with pytest.raises(CommandValidationError):parse_command(json.dumps(doc).encode())

@pytest.mark.parametrize('extra',[{'actor_id':str(uuid4())},{'org_id':str(uuid4())},{'membership_id':'1'},{'grant_id':str(uuid4())},{'expected_revision':'0'}])
def test_create_closed_payload(extra):
    doc=document(expected_absent=True);doc['payload'].update(extra)
    with pytest.raises(CommandValidationError):parse_command(json.dumps(doc).encode())

def test_typed_account_receipt_is_closed_and_revision_checked():
    from datetime import datetime,timezone
    from access_operator import _receipt
    from identity_operator import OperatorError
    target=dict(grant_id=str(uuid4()),account_id=str(uuid4()),permission='pts.use')
    result=dict(target=target,disposition='created',revision='1',event_id=str(uuid4()))
    instant=datetime.now(timezone.utc)
    assert _receipt((result,1,1,instant),str(uuid4()),'account_grant.assign').result.target.account_id==target['account_id']
    for broken in (dict(result,revision='2'),dict(result,event_id=None),dict(result,target=dict(target,org_id=str(uuid4())))):
        with pytest.raises(OperatorError):_receipt((broken,1,1,instant),str(uuid4()),'account_grant.assign')
    assert _receipt((dict(result,disposition='unchanged',event_id=None),1,1,instant),str(uuid4()),'account_grant.revoke').result.event_id is None

def test_outcome_rejects_organization_or_membership_selectors_before_io():
    from access_operator import outcome
    from identity_operator import OperatorError
    for extra in (dict(org_id=str(uuid4())),dict(membership_id='1'),dict(app_id='pts'),dict(grant_id=str(uuid4()))):
        with pytest.raises(OperatorError):outcome(None,str(uuid4()),command='account_grant.assign',account_id=str(uuid4()),permission='pts.use',**extra)

def test_cli_account_context_is_closed():
    from operator_cli import _account_grant_outcome_context
    value=dict(command='account_grant.revoke',account_id=str(uuid4()),permission='pts.use',grant_id=str(uuid4()))
    assert _account_grant_outcome_context(value)==value
    for extra in (dict(org_id=str(uuid4())),dict(actor_id=str(uuid4())),dict(membership_id='1')):
        with pytest.raises(ValueError):_account_grant_outcome_context(value|extra)

def test_assignment_observation_precedes_local_locks_and_revoke_is_independent():
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'migrations/versions/0017_account_grants.py'
    spec=importlib.util.spec_from_file_location('_account_grants_migration',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    sql=module.SQL
    command=sql[sql.index('CREATE FUNCTION access.change_account_grant('):]
    assert command.index('account_grant_authority(p_command,app,p_account)')<command.index('identity.account_grant_target(p_account)')<command.index('pg_advisory_xact_lock')
    assert 'IF p_command=\'account_grant.assign\' THEN' in command
    assert 'FOREIGN KEY(permission,scope_kind) REFERENCES access.permissions(permission,scope_kind)' in sql
    assert 'UNIQUE(account_id,permission)' in sql
    assert 'access_required_account_grant_change_missing' in sql
    assert 'studies_account_grant' not in sql
    assert 'FROM identity.org_member' not in sql

def test_new_identity_head_rechecks_studies_role_and_full_predecessor_sources(monkeypatch):
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'identity-migrations/identity_account_grant_catalog.py'
    sys.path.insert(0,str(path.parent))
    spec=importlib.util.spec_from_file_location('_account_identity_catalog',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    import studies_migration_support as support
    def reject(*args):raise RuntimeError('inherited_role_edge')
    monkeypatch.setattr(support,'verify_roles',reject)
    with pytest.raises(RuntimeError,match='inherited_role_edge'):module.verify_account_grant_catalog(None)
    source=path.read_text()
    for name in ('0021_studies_account_setup.py','0022_person_links.py','0023_language_preferences.py'):
        assert name in source

def test_new_access_head_rechecks_inherited_studies_roles(monkeypatch):
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'migrations/access_account_grant_catalog.py'
    sys.path.insert(0,str(path.parent))
    spec=importlib.util.spec_from_file_location('_account_access_catalog',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    import studies_migration_support as support
    def reject(*args):raise RuntimeError('inherited_role_edge')
    monkeypatch.setattr(support,'verify_roles',reject)
    with pytest.raises(RuntimeError,match='inherited_role_edge'):module.verify_account_grant_catalog(None)

def test_runtime_account_storage_has_explicit_scoped_read_policy():
    source=(Path(__file__).resolve().parents[1]/'migrations/versions/0017_account_grants.py').read_text()
    assert 'GRANT SELECT ON access.account_grants TO access_runtime' in source
    assert 'CREATE POLICY account_grant_runtime_read' in source

def test_qualifier_reserves_output_before_guard(monkeypatch,tmp_path):
    import qualify_account_grants as q
    output=tmp_path/'evidence.json';output.write_text('prior evidence')
    monkeypatch.setattr(sys,'argv',['qualifier','--fixture',str(tmp_path/'missing'),'--output',str(output)])
    monkeypatch.setattr(q,'guard',lambda:pytest.fail('guard called before output reservation'))
    with pytest.raises(FileExistsError):q.main()
    assert output.read_text()=='prior evidence'

def test_identity24_refuses_changed_immutable_preference_source(tmp_path,monkeypatch):
    import identity_account_grant_catalog as catalog
    import identity_baseline
    import shutil
    original=catalog.HERE
    (tmp_path/'versions').mkdir()
    for name in ('studies-setup-reference.json','person-links-reference.json','language-preferences-reference.json'):
        shutil.copyfile(original/name,tmp_path/name)
    for name in ('0021_studies_account_setup.py','0022_person_links.py','0023_language_preferences.py'):
        shutil.copyfile(original/'versions'/name,tmp_path/'versions'/name)
    monkeypatch.setattr(catalog,'HERE',tmp_path)
    monkeypatch.setattr(identity_baseline,'trusted_check_reader_bridge_reference',lambda:None)
    catalog.trusted_predecessors()
    path=tmp_path/'versions/0023_language_preferences.py';path.write_bytes(path.read_bytes()+b'\n# unexpected historical mutation\n')
    with pytest.raises(identity_baseline.BaselineError,match='identity_account_grant_reference_unavailable'):catalog.trusted_predecessors()

def test_identity_new_access_detection_uses_permission_independent_metadata():
    source=(Path(__file__).resolve().parents[1]/'identity-migrations/identity_baseline.py').read_text()
    assert "to_regprocedure('access.change_account_grant" not in source
    assert "n.nspname='access' AND p.proname='change_account_grant'" in source

def test_staged_identity24_foreign_projection_is_exactly_pinned():
    import access_baseline as baseline
    key=('identity','account_grant_target','p_account uuid')
    assert baseline._FOREIGN_FUNCTIONS.get(key)==('identity_account_verification_owner',frozenset({'64cdb1e12e6f68238e5351358d899066d4495d0b987abfcdf940ef6ea9fa0d3b'}),'{identity_account_verification_owner=X/identity_account_verification_owner,access_command_owner=X/identity_account_verification_owner}')

def test_shared_evidence_guard_branches_before_record_specific_fields():
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'migrations/versions/0017_account_grants.py'
    spec=importlib.util.spec_from_file_location('_account_trigger_shape',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    branch=module.EVIDENCE_BRANCH
    assert "IF TG_TABLE_NAME='operation_outcome' THEN" in branch
    assert "ELSIF TG_TABLE_NAME='business_event' THEN" in branch
    assert "IF account_command THEN" in branch
    assert "TG_TABLE_NAME='operation_outcome' AND NEW.command_type" not in branch

def test_standalone_access17_rejects_runtime_set_only_role_edge():
    import access_account_grant_catalog as catalog
    class Result:
        def __init__(self,value):self.value=value
        def one_or_none(self):return self.value
        def scalar_one(self):return self.value
        def all(self):return self.value
    class Connection:
        def execute(self,statement,parameters=None):
            sql=str(statement)
            if 'pg_auth_members' in sql:return Result([(1,)])
            if 'has_database_privilege' in sql:return Result(False)
            return Result((True,False,False,False,False,False))
    import access_baseline
    with pytest.raises(access_baseline.BaselineError,match='access_runtime_role_unsafe'):catalog.verify_runtime_role(Connection())

def test_cross_command_operation_reuse_is_an_exact_ledger_conflict():
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'migrations/versions/0017_account_grants.py'
    spec=importlib.util.spec_from_file_location('_account_operation_collision',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    command=module.SQL.split('CREATE FUNCTION access.change_account_grant(',1)[1].split('CREATE FUNCTION access.account_grant_outcome(',1)[0]
    selection=command.split('SELECT * INTO saved FROM access.operation_outcome',1)[1].split(';',1)[0]
    assert 'o.command_type=p_command' not in selection
    assert 'saved.command_type IS DISTINCT FROM p_command' in command
    assert 'operation_outcome_executor_actor_id_operation_id_key' in command
    assert 'GET STACKED DIAGNOSTICS' in command

def test_runtime_guard_preserves_exact_native_admin_only_bootstrap():
    import access_account_grant_catalog as catalog
    class Result:
        def __init__(self,value):self.value=value
        def one_or_none(self):return self.value
        def scalar_one(self):return self.value
        def all(self):return self.value
    class Connection:
        def execute(self,statement,parameters=None):
            sql=str(statement)
            if 'pg_auth_members' in sql:return Result([('access_runtime','postgres','supabase_admin',True,False,False)])
            if 'has_database_privilege' in sql:return Result(False)
            if "'postgres','supabase_admin'" in sql:return Result([('postgres',True,False,True,True,True,True,True),('supabase_admin',True,True,True,True,True,True,True)])
            return Result((True,False,False,False,False,False))
    catalog.verify_runtime_role(Connection())

def test_catalog_covers_schema_authority_and_native_index_state():
    import access_account_grant_catalog as catalog
    queries=[]
    class Rows:
        def __iter__(self):return iter(())
    class Connection:
        def execute(self,statement):queries.append(str(statement));return Rows()
    catalog.snapshot(Connection())
    assert any('nspowner' in q and 'nspacl' in q for q in queries)
    assert any(all(part in q for part in ('pg_get_indexdef','indisvalid','indisready','indislive')) for q in queries)

def test_committed_assignment_recovery_precedes_fresh_observation():
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'migrations/versions/0017_account_grants.py'
    spec=importlib.util.spec_from_file_location('_account_recovery_order',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    command=module.SQL.split('CREATE FUNCTION access.change_account_grant(',1)[1].split('CREATE FUNCTION access.account_grant_outcome(',1)[0]
    assert command.index('SELECT * INTO saved FROM access.operation_outcome')<command.index('identity.account_grant_target(p_account)')<command.index('pg_advisory_xact_lock')

@pytest.mark.parametrize('symlink',[False,True])
def test_qualifier_reserves_command_before_guard(tmp_path,monkeypatch,symlink):
    import qualify_account_grants as q
    output=tmp_path/'result.json';command=output.with_suffix('.command.json');target=tmp_path/'retained';target.write_text('retained')
    if symlink:command.symlink_to(target)
    else:command.write_text('occupied')
    monkeypatch.setattr(sys,'argv',['qualifier','--fixture',str(tmp_path/'missing'),'--output',str(output)])
    monkeypatch.setattr(q,'guard',lambda:pytest.fail('guard called before command reservation'))
    with pytest.raises(FileExistsError):q.main()
    assert target.read_text()=='retained'

@pytest.mark.parametrize('defect',[None,'missing_outcome','refused_outcome','missing_event','wrong_target','wrong_outcome'])
def test_qualifier_exact_outcome_and_event_sets(defect):
    from qualify_account_grants import Proof
    from copy import deepcopy
    operation,refused,oid,event,grant,account,executor=[str(uuid4()) for _ in range(7)]
    result=dict(target=dict(grant_id=grant,account_id=account,permission='pts.use'),disposition='created',revision='1',event_id=event)
    proof=Proof.__new__(Proof);proof.f=dict(executor_actor_id=executor);proof.operation_ids=[operation,refused];proof.refused={refused};proof.committed={operation:dict(command='account_grant.assign',result=result)}
    rows=[(oid,operation,'account_grant.assign',deepcopy(result),executor,'platform',None)]
    events=[(event,operation,oid,'access.account_grant_assigned',deepcopy(result['target']),executor,'platform',None,1)]
    if defect=='missing_outcome':rows=[]
    if defect=='refused_outcome':rows.append((str(uuid4()),refused,'account_grant.assign',result,executor,'platform',None))
    if defect=='missing_event':events=[]
    if defect=='wrong_target':events[0][4]['account_id']=str(uuid4())
    if defect=='wrong_outcome':events[0]=(event,operation,str(uuid4()),*events[0][3:])
    proof.owner=lambda query,parameters:events if 'FROM access.business_event' in query else rows
    if defect is None:proof.verify_cardinality()
    else:
        with pytest.raises(AssertionError):proof.verify_cardinality()

def test_qualifier_writes_all_bytes_before_fsync(monkeypatch):
    import qualify_account_grants as q
    received=bytearray();synced=[]
    def short_write(fd,value):
        chunk=bytes(value[:2]);received.extend(chunk);return len(chunk)
    monkeypatch.setattr(q.os,'write',short_write)
    monkeypatch.setattr(q.os,'fsync',lambda fd:synced.append(bytes(received)))
    q.write_all(42,b'complete command')
    assert bytes(received)==b'complete command' and synced==[b'complete command']
