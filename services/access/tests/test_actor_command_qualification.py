"""Head6 custody and fail-closed preparation; actual effects require live qualifier."""
import json
from pathlib import Path
import shutil
import stat
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_identity_baseline as qualification
import qualify_actor_command as command
from test_operator_authority_qualification import authority_recorder
from test_projection_qualification import digest


def recorder(tmp_path,monkeypatch,mutation=None):
    runner,statements,_=authority_recorder(tmp_path,monkeypatch,mutation)
    (tmp_path/'identity_baseline.py').write_text('COMMAND_REFERENCE_SHA256 = None\n')
    (tmp_path/'authority-reference.json').write_text('{}')
    (tmp_path/'versions/0006_actor_command.py').write_text('COMMAND_SCHEMA_SQL = "captured command"\n')
    runner.private={'owner_urls':{'command_reference':'synthetic'}}
    monkeypatch.setattr(qualification.baseline,'trusted_authority_reference',lambda:{})
    monkeypatch.setattr(qualification.baseline,'verify_command_role',lambda *a,**k:None)
    monkeypatch.setattr(qualification.baseline,'command_catalog_snapshot',lambda *a:{})
    monkeypatch.setattr(qualification.baseline,'IMPORTED_SOURCE_SHA256',digest((tmp_path/'identity_baseline.py').read_bytes()))
    cls=type(qualification.engine('synthetic').connect())
    original=cls.exec_driver_sql
    def raw(self,sql,**options):
        if str(sql)=='captured command':assert options=={'execution_options':{'no_parameters':True}}
        return original(self,sql)
    monkeypatch.setattr(cls,'exec_driver_sql',raw)
    return runner,statements


@pytest.mark.parametrize('mutation',[None,'identity_baseline.py','source-pins.json','reference.json',
 'actor-reference.json','projection-reference.json','organization-reference.json','authority-reference.json',
 'versions/0001_baseline.py','versions/0002_actor_registry.py','versions/0003_current_account_actor.py',
 'versions/0004_current_account_organization.py','versions/0005_operator_authority.py','versions/0006_actor_command.py'])
def test_command_reference_captures_full_chain_and_never_pins(tmp_path,monkeypatch,mutation):
    runner,statements=recorder(tmp_path,monkeypatch,mutation)
    helper=(tmp_path/'identity_baseline.py').read_bytes()
    if mutation:
        with pytest.raises(AssertionError,match='command_reference_source_changed'):runner.record_command_reference()
        assert not (tmp_path/'command-reference.json').exists()
    else:
        runner.record_command_reference()
        assert (tmp_path/'identity_baseline.py').read_bytes()==helper
        assert runner.records[-1]['pin_update_required'] is True
        assert stat.S_IMODE((tmp_path/'command-reference.json').stat().st_mode)==0o600
        with pytest.raises(AssertionError,match='command_reference_already_exists'):runner.record_command_reference()
    assert statements==['captured baseline','captured actor','captured projection','captured organization','captured authority','captured command']


def test_only_command_is_current_head_and_authority_stays_supported(monkeypatch):
    b=qualification.baseline
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.COMMAND_REVISION)
    monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
    kinds=[];monkeypatch.setattr(b,'verify_catalog',lambda c,k:kinds.append(k))
    b.verify_owned_postcondition(object(),require_head=True)
    assert kinds==['command']
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.AUTHORITY_REVISION)
    b.verify_owned_postcondition(object())
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):b.verify_owned_postcondition(object(),require_head=True)


@pytest.mark.parametrize('defect',['missing','unsafe','membership','dependencies','effective'])
def test_command_role_refuses_unsafe_preparation(defect):
    b=qualification.baseline
    class Result:
        def __init__(self,rows=(),scalar=False):self.rows=rows;self.scalar=scalar
        def all(self):return self.rows
        def scalar_one(self):return self.scalar
    class Connection:
        def execute(self,sql,params=None):
            sql=str(sql)
            if sql==b.COMMAND_ROLE_QUERIES['command_role']:
                return Result([] if defect=='missing' else [(b.COMMAND_OWNER,False,False,False,False,defect=='unsafe',False,False)])
            if sql==b.COMMAND_ROLE_QUERIES['command_memberships']:
                return Result([(b.COMMAND_OWNER,'identity_migrator',defect=='membership','false','true')])
            if sql==b.COMMAND_ROLE_QUERIES['command_dependencies']:
                return Result([('unexpected',)] if defect=='dependencies' else [])
            assert 'has_database_privilege' in sql and 'CASE WHEN' in sql
            return Result(scalar=defect=='effective')
    with pytest.raises(b.BaselineError,match='identity_command_role_'):b.verify_command_role(Connection(),staged=True)


def test_qualified_target_groups_are_exact_before_writes(tmp_path):
    private={group:{case:'postgresql://'+login+':synthetic@127.0.0.1:1234/'+case for case in command.REQUIRED_CASES}
      for group,login in [('operator_urls','identity_operator'),('owner_urls','identity_migrator'),('databases','postgres'),('runtime_urls','access_runtime')]}
    runner=command.CommandQualification(tmp_path,private);runner.validate_operator_urls()
    private['operator_urls']['clean']=private['operator_urls']['clean'].replace('identity_operator','wrong')
    with pytest.raises(AssertionError,match='command_login_invalid'):runner.validate_operator_urls()
