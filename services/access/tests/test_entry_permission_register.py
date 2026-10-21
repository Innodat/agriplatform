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
    receipt=a._receipt(row,OP,'entry_permission.register')
    assert receipt.result.target.permission==target['permission'] and receipt.result.revision is None
    for changed in ({'revision':'1'},{'event_id':None},{'target':{**target,'permission':'\x00'}},{'target':{**target,'scope_kind':'account'}}):
        with pytest.raises(a.OperatorError):a._receipt(({**row[0],**changed},*row[1:]),OP,'entry_permission.register')

def test_permission_lock_uses_actual_command():
    import access_operator as a
    actor='b1234567-1234-1234-1234-123456789abc'
    app=a.parse_command(json.dumps(document()).encode())
    permission=a.parse_command(json.dumps(document('entry_permission.register')).encode())
    assert a.command_outcome_lock_key(actor,app)!=a.command_outcome_lock_key(actor,permission)

def test_permission_dispatch_and_lookup(monkeypatch):
    import access_operator as a
    seen=[]
    monkeypatch.setattr(a,'_run',lambda *args:seen.append(args))
    a.execute(object(),json.dumps(document('entry_permission.register')).encode())
    assert 'access.register_entry_permission' in seen[-1][2]
    assert seen[-1][3]['permission']=='synthetic.read' and seen[-1][-1]=='entry_permission.register'
    a.outcome(object(),OP,command='entry_permission.register',app_id='synthetic_app',permission='synthetic.read')
    assert 'access.entry_permission_registration_outcome' in seen[-1][2]
    for value in (None,'','\x00','é','a'*201):
        with pytest.raises(a.OperatorError) as failure:a.outcome(object(),OP,command='entry_permission.register',app_id='synthetic_app',permission=value)
        assert failure.value.code=='command_invalid'

def test_history_retains_five_and_adds_six():
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations'))
    import access_baseline as b
    assert b.validate_revision(['access_0007'])=='access_0007'
    assert b.validate_revision(['access_0006'])=='access_0006'
    assert b.validate_revision(['access_0005'])=='access_0005'
    from access_registration_catalog import entry_catalog,permission_catalog
    assert 'entry_permission.register' not in repr(permission_catalog())
    assert 'entry_permission.register' in repr(entry_catalog())

@pytest.mark.parametrize('literal',('synthetic.read','--owner','--permission=x'))
def test_permission_cli_execute_lookup_and_target_validation(tmp_path,monkeypatch,capsys,literal):
    import operator_cli as cli
    from types import SimpleNamespace
    value=document('entry_permission.register');value['payload']['permission']=literal;path=tmp_path/'permission.json';path.write_text(json.dumps(value))
    seen=[]
    monkeypatch.setattr(cli,'load_target',lambda *args,**kwargs:SimpleNamespace(path=Path('/synthetic/access-target.json')))
    row=dict(operation_id=OP,status='committed',command_version=1,result_version=1,committed_at=datetime.now(timezone.utc).isoformat(),result=dict(command='entry_permission.register',target={'app_id':'synthetic_app','permission':literal},disposition='created',revision=None,event_id=OP))
    monkeypatch.setattr(cli,'dispatch',lambda request:seen.append(request) or json.dumps(row).encode())
    assert cli.main(['execute','--owner','access','--target','synthetic','--command-file',str(path)])==0
    assert json.loads(capsys.readouterr().out)==row
    assert cli.main(['outcome','--owner','access','--target','synthetic','--command','entry_permission.register','--operation-id',OP,'--app-id','synthetic_app','--permission='+literal])==0
    assert seen[-1][2]==dict(command='entry_permission.register',app_id='synthetic_app',permission=literal)
    capsys.readouterr()
    before=len(seen)
    assert cli.main(['outcome','--owner','access','--target','synthetic','--command','entry_permission.register','--operation-id',OP,'--app-id','synthetic_app'])==2
    assert json.loads(capsys.readouterr().out)['code']=='command_invalid' and len(seen)==before
    with pytest.raises(ValueError):cli.validate_response(json.dumps(row).encode(),OP,'entry_permission.register',{'permission':'foreign'})



def test_entry_source_pin_refuses_drift_before_import(monkeypatch):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations'))
    import access_registration_baseline as b
    original=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:original(path)+b'\n# drift\n' if path.name=='0006_entry_permission_register.py' else original(path))
    with pytest.raises(b.BaselineError,match='access_original_source_mismatch'):b._sql('access_0006')
    assert 'register_permission' in b._sql('access_0005')


def test_entry_lookup_nul_refuses_before_connection():
    import access_operator as a
    with pytest.raises(a.OperatorError) as failure:
        a.outcome(object(),OP,command='entry_permission.register',app_id='synthetic_app',permission='a\x00b')
    assert failure.value.code=='command_invalid'


def test_retained_rejects_aggregate_source_mismatch_before_state_or_writes(tmp_path,monkeypatch):
    import qualify_entry_permission_register as q
    captured={'qualifier.py':'current'}
    witness={'status':'passed','before':captured,'after':captured,'logs':{}}
    (tmp_path/'bootstrap-source-custody.json').write_text(json.dumps(witness))
    (tmp_path/'results.json').write_text(json.dumps({'status':'passed','source':{'qualifier.py':'other'}}))
    original={p.name:p.read_bytes() for p in tmp_path.iterdir()}
    monkeypatch.setenv('ACCESS_QUALIFICATION_DIR',str(tmp_path))
    monkeypatch.setattr(sys,'argv',['qualify_entry_permission_register.py','--verify-retained'])
    monkeypatch.setattr(q.prior,'load_fixture',lambda _:({'databases':{}},{}))
    monkeypatch.setattr(q,'source_snapshot',lambda _:captured)
    class Qualification:
        def __init__(self,*args):pass
        def snapshot(self,*args):pytest.fail('mismatched aggregate reached retained data')
        def retained(self):pytest.fail('mismatched aggregate reached retained verification')
    monkeypatch.setattr(q,'Qualification',Qualification)
    with pytest.raises(AssertionError,match='aggregate_source_mismatch'):q.main()
    assert {p.name:p.read_bytes() for p in tmp_path.iterdir()}==original
    q.require_aggregate_source({'status':'passed','source':captured},captured)


def test_native_lookup_matrix_covers_shape_bounds():
    import qualify_entry_permission_register as q
    cases=dict(q.malformed_lookup_cases())
    assert {'null_operation','nil_operation','null_app','invalid_app','null_permission','empty_permission','nonascii_permission','long_permission'}<=cases.keys()
    assert cases['long_permission']['permission']=='a'*201
