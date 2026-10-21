"""Permission execution closure and command-isolated recovery."""
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_application_register import document, OP

def test_permission_receipt_closed_literal_target():
    import access_operator as a
    target={'app_id':'synthetic_app','permission':' \t\x01\x7f'}
    row=({'target':target,'disposition':'created','revision':None,'event_id':OP},1,1,datetime.now(timezone.utc))
    receipt=a._receipt(row,OP,'permission.register')
    assert receipt.result.target.permission==target['permission'] and receipt.result.revision is None
    for changed in ({'revision':'1'},{'event_id':None},{'target':{**target,'permission':'\x00'}},{'target':{**target,'scope_kind':'account'}}):
        with pytest.raises(a.OperatorError):a._receipt(({**row[0],**changed},*row[1:]),OP,'permission.register')

def test_permission_lock_uses_actual_command():
    import access_operator as a
    actor='b1234567-1234-1234-1234-123456789abc'
    app=a.parse_command(json.dumps(document()).encode())
    permission=a.parse_command(json.dumps(document('permission.register')).encode())
    assert a.command_outcome_lock_key(actor,app)!=a.command_outcome_lock_key(actor,permission)

def test_permission_dispatch_and_lookup(monkeypatch):
    import access_operator as a
    seen=[]
    monkeypatch.setattr(a,'_run',lambda *args:seen.append(args))
    a.execute(object(),json.dumps(document('permission.register')).encode())
    assert 'access.register_permission' in seen[-1][2]
    assert seen[-1][3]['permission']=='synthetic.read' and seen[-1][-1]=='permission.register'
    a.outcome(object(),OP,command='permission.register',app_id='synthetic_app',permission='synthetic.read')
    assert 'access.permission_registration_outcome' in seen[-1][2]
    for value in (None,'','\x00','é','a'*201):
        with pytest.raises(a.OperatorError) as failure:a.outcome(object(),OP,command='permission.register',app_id='synthetic_app',permission=value)
        assert failure.value.code=='command_invalid'

def test_history_retains_four_and_adds_five():
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations'))
    import access_baseline as b
    assert b.HEAD=='access_0007'
    assert b.validate_revision(['access_0004'])=='access_0004'
    assert b.validate_revision(['access_0005'])=='access_0005'

@pytest.mark.parametrize('literal',('a','a'*200,' \t\b\f\n\r\x01\x1f\x7f\\"/'))
def test_permission_canonical_preserves_literal_scope_and_expected(literal):
    import access_operator as a
    value=document('permission.register');value['payload']['permission']=literal
    encoded=a.canonical_command(a.parse_command(json.dumps(value).encode()))
    assert json.loads(encoded)==value
    assert encoded==__import__('rfc8785').dumps(value)


@pytest.mark.parametrize('literal',('synthetic.read','--owner','--permission=x'))
def test_permission_cli_execute_lookup_and_target_validation(tmp_path,monkeypatch,capsys,literal):
    import operator_cli as cli
    from types import SimpleNamespace
    value=document('permission.register');value['payload']['permission']=literal;path=tmp_path/'permission.json';path.write_text(json.dumps(value))
    seen=[]
    monkeypatch.setattr(cli,'load_target',lambda *args,**kwargs:SimpleNamespace(path=Path('/synthetic/access-target.json')))
    row=dict(operation_id=OP,status='committed',command_version=1,result_version=1,committed_at=datetime.now(timezone.utc).isoformat(),result=dict(command='permission.register',target={'app_id':'synthetic_app','permission':literal},disposition='created',revision=None,event_id=OP))
    monkeypatch.setattr(cli,'dispatch',lambda request:seen.append(request) or json.dumps(row).encode())
    assert cli.main(['execute','--owner','access','--target','synthetic','--command-file',str(path)])==0
    assert json.loads(capsys.readouterr().out)==row
    assert cli.main(['outcome','--owner','access','--target','synthetic','--command','permission.register','--operation-id',OP,'--app-id','synthetic_app','--permission='+literal])==0
    assert seen[-1][2]==dict(command='permission.register',app_id='synthetic_app',permission=literal)
    capsys.readouterr()
    before=len(seen)
    assert cli.main(['outcome','--owner','access','--target','synthetic','--command','permission.register','--operation-id',OP,'--app-id','synthetic_app'])==2
    assert json.loads(capsys.readouterr().out)['code']=='command_invalid' and len(seen)==before
    with pytest.raises(ValueError):cli.validate_response(json.dumps(row).encode(),OP,'permission.register',{'permission':'foreign'})


def test_catalog_keeps_command_specific_four_and_five_expectations():
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations'))
    import access_registration_baseline as b
    from access_registration_catalog import TABLE_CATALOG,permission_catalog
    assert 'register_permission' not in b.FUNCTIONS and 'register_permission' in b.PERMISSION_FUNCTIONS
    assert 'permission.register' not in repr(TABLE_CATALOG)
    tables,functions=permission_catalog()
    assert 'permission.register' in repr(tables)
    assert 'register_permission' in functions
    assert 'operation_outcome_executor_actor_id_operation_id_key' in b.INDEXES
    assert 'operation_outcome_executor_actor_id_operation_id_key' not in b.PERMISSION_INDEXES


def test_permission_source_pin_refuses_drift_before_import(monkeypatch):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations'))
    import access_registration_baseline as b
    original=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:original(path)+b'\n# drift\n' if path.name=='0005_permission_register.py' else original(path))
    with pytest.raises(b.BaselineError,match='access_original_source_mismatch'):b._sql('access_0005')
    # The historical4 branch remains independent of new source drift.
    assert 'CREATE TABLE access.operator_principals' in b._sql('access_0004')


def test_permission_lookup_nul_safe_refusal_before_sql():
    import access_operator as a
    class Connection:
        def in_transaction(self):pytest.fail('NUL lookup reached connection')
    with pytest.raises(a.OperatorError) as failure:
        a.outcome(Connection(),OP,command='permission.register',app_id='synthetic_app',permission='before\x00after')
    assert failure.value.code=='command_invalid'


def test_native_escaped_nul_case_is_json_escape():
    import qualify_permission_register as q
    import access_operator as a
    value=q.document('malformed.sql')
    parameters={'canonical':a.canonical_command(a.parse_command(json.dumps(value).encode()))}
    change=dict(q.malformed_permission_sql_cases())['escaped_nul'](parameters)
    assert b'\\u0000' in change['canonical'] and b'\x00' not in change['canonical']
    assert json.loads(change['canonical'])['payload']['permission']=='\x00'


def test_previous_application_fixture_refuses_drift_before_import(tmp_path):
    import qualify_permission_register as q
    path=tmp_path/q.PREVIOUS_APPLICATION_ADAPTER_FILE
    path.write_text("raise RuntimeError('unapproved source executed')")
    with pytest.raises(AssertionError,match='previous_application_adapter_source_mismatch'):
        q.load_previous_application_adapter(tmp_path)
