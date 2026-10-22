"""Revocation binds exact retained selectors through typed transport."""
from datetime import datetime,timezone
from dataclasses import asdict
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import access_operator as a
import operator_cli as cli
from test_grant_assign_adapter import result,ORG,ACCOUNT,OP
from test_grant_assign_input import document as assignment


def document(grant='opaque:existing grant'):
    value=assignment();value['command']='grant.revoke'
    value['payload'].pop('expected_absent');value['payload'].update(grant_id=grant,expected_revision='1')
    return value


def test_execute_and_lookup_exact_binding(monkeypatch):
    seen=[];monkeypatch.setattr(a,'_run',lambda *args:seen.append(args))
    value=document();a.execute(object(),json.dumps(value).encode());call=seen.pop()
    assert 'access.revoke_organization_grant(' in call[2]
    assert call[3]['account']==ACCOUNT.lower() and call[3]['grant']==value['payload']['grant_id']
    assert call[3]['revision']=='1' and 'absent' not in call[3] and call[-1]=='grant.revoke'
    assert json.loads(call[3]['canonical'])['payload']['account_id']==ACCOUNT.lower()
    a.outcome(object(),OP,command='grant.revoke',org_id=ORG,grant_id='',account_id=ACCOUNT,membership_id='1',permission='p')
    call=seen.pop();assert 'access.organization_grant_revocation_outcome(' in call[2] and call[3]['grant']==''


@pytest.mark.parametrize('changes',[dict(disposition='created',revision='1'),dict(disposition='changed',revision='1'),dict(event_id=None),dict(disposition='unchanged'),dict(revision='01'),dict(revision=True)])
def test_refuse_bad_transition(changes):
    with pytest.raises(a.OperatorError):a._receipt((result()|changes,1,1,datetime.now(timezone.utc)),OP,'grant.revoke')


@pytest.mark.parametrize('grant',['','-option=é','x'*10000])
def test_preserves_opaque_grant(grant):
    value=result();value['target']['grant_id']=grant
    receipt=a._receipt((value,1,1,datetime.now(timezone.utc)),OP,'grant.revoke')
    assert type(receipt.result) is a.RevokeGrantResult and receipt.result.target.grant_id==grant
    assert a._receipt((value|dict(disposition='unchanged',event_id=None),1,1,datetime.now(timezone.utc)),OP,'grant.revoke')


def test_invalid_lookup_never_touches_sql(monkeypatch):
    monkeypatch.setattr(a,'_run',lambda *args:pytest.fail('invalid lookup touched SQL'))
    good=dict(command='grant.revoke',org_id=ORG,grant_id='',account_id=ACCOUNT,membership_id='1',permission='p')
    for changes in (dict(grant_id=None),dict(grant_id='\x00'),dict(app_id='fixture_app'),dict(account_id=None),dict(membership_id=1),dict(org_id=None)):
        with pytest.raises(a.OperatorError):a.outcome(object(),OP,**(good|changes))


def test_cli_exact_target_and_literal_option(tmp_path,monkeypatch,capsys):
    from types import SimpleNamespace
    grant='-opaque=é';value=document(grant);value['operation_id']=OP
    path=tmp_path/'command.json';path.write_text(json.dumps(value))
    monkeypatch.setattr(cli,'load_target',lambda *args,**kwargs:SimpleNamespace(path=tmp_path/'trusted'))
    returned=result();returned['target'].update(grant_id=grant,membership_id='1',permission=value['payload']['permission'])
    receipt=a._receipt((returned,1,1,datetime.now(timezone.utc)),OP,'grant.revoke');wire=asdict(receipt);wire['committed_at']=receipt.committed_at.isoformat()
    seen=[];monkeypatch.setattr(cli,'dispatch',lambda request:seen.append(request) or json.dumps(wire).encode())
    execute=['execute','--owner','access','--target','unused','--command-file',str(path)]
    lookup=['outcome','--owner','access','--target','unused','--command','grant.revoke','--operation-id',OP,'--org-id',ORG,'--account-id',ACCOUNT,'--membership-id','1','--permission',value['payload']['permission'],'--grant-id='+grant]
    for args in (execute,lookup):
        assert cli.main(args)==0;assert json.loads(capsys.readouterr().out)==wire
    assert seen[-1][2]['grant_id']==grant and len(seen[-1][2])==6
    wire['result']['target']['grant_id']='replacement'
    assert cli.main(execute)==2 and json.loads(capsys.readouterr().out)['code']=='operation_unavailable'


def test_surrogate_selector_and_receipt_refuse_before_io(monkeypatch):
    monkeypatch.setattr(a,'_run',lambda *args:pytest.fail('invalid UTF8 touched SQL'))
    with pytest.raises(a.OperatorError):a.outcome(object(),OP,command='grant.revoke',org_id=ORG,grant_id='\ud800',account_id=ACCOUNT,membership_id='1',permission='p')
    with pytest.raises(ValueError):cli._grant_outcome_context(dict(command='grant.revoke',org_id=ORG,grant_id='\ud800',account_id=ACCOUNT,membership_id='1',permission='p'))
    value=result();value['target']['grant_id']='\ud800'
    with pytest.raises(a.OperatorError):a._receipt((value,1,1,datetime.now(timezone.utc)),OP,'grant.revoke')


def test_revoke_transport_budget_is_bounded_for_large_valid_receipts(monkeypatch):
    limits=[]
    monkeypatch.setattr(cli.images,'bounded_command',lambda *args,**kwargs:limits.append(args[4]) or b'{}')
    value=document('é'*10000)
    cli.dispatch(['execute','unused',json.dumps(value,ensure_ascii=False),OP,'access'])
    cli.dispatch(['outcome','unused',dict(command='grant.revoke'),OP,'access'])
    cli.dispatch(['outcome','unused',dict(command='grant.assign'),OP,'access'])
    assert limits==[4*65536,4*65536,8192]
    returned=result();returned['target']['grant_id']='é'*10000
    receipt=a._receipt((returned,1,1,datetime.now(timezone.utc)),OP,'grant.revoke');wire=asdict(receipt);wire['committed_at']=receipt.committed_at.isoformat()
    raw=json.dumps(wire).encode();assert len(raw)>8192
    assert cli.validate_response(raw,OP,'grant.revoke',returned['target'])==wire


@pytest.mark.parametrize('grant',['x'*65537,'é'*32769])
def test_oversized_recovery_selector_refuses_before_io(grant,monkeypatch,capsys):
    monkeypatch.setattr(a,'_run',lambda *args:pytest.fail('oversized selector touched SQL'))
    monkeypatch.setattr(cli,'load_target',lambda *args,**kwargs:pytest.fail('oversized selector opened target'))
    monkeypatch.setattr(cli,'dispatch',lambda *args:pytest.fail('oversized selector entered transport'))
    with pytest.raises(a.OperatorError) as caught:a.outcome(object(),OP,command='grant.revoke',org_id=ORG,grant_id=grant,account_id=ACCOUNT,membership_id='1',permission='p')
    assert caught.value.code=='command_invalid'
    context=dict(command='grant.revoke',org_id=ORG,grant_id=grant,account_id=ACCOUNT,membership_id='1',permission='p')
    with pytest.raises(ValueError):cli._grant_outcome_context(context)
    argv=['outcome','--owner','access','--target','unused','--command','grant.revoke','--operation-id',OP,'--org-id',ORG,'--account-id',ACCOUNT,'--membership-id','1','--permission','p','--grant-id='+grant]
    assert cli.main(argv)==2 and json.loads(capsys.readouterr().out)==dict(code='command_invalid')


@pytest.mark.parametrize('flags',[
    ['--grant-id','one','--grant-id','two'],
    ['--grant-id=one','--grant-id=two'],
    ['--grant-id','one','--grant-id=two'],
    ['--grant-id=one','--grant-id','two'],
])
def test_duplicate_grant_id_forms_refuse_before_dispatch(flags,monkeypatch,capsys):
    monkeypatch.setattr(cli,'load_target',lambda *args,**kwargs:pytest.fail('duplicate opened target'))
    monkeypatch.setattr(cli,'dispatch',lambda *args:pytest.fail('duplicate entered transport'))
    argv=['outcome','--owner','access','--target','unused','--command','grant.revoke','--operation-id',OP,'--org-id',ORG,'--account-id',ACCOUNT,'--membership-id','1','--permission','p']
    assert cli.main(argv+flags)==2
    assert json.loads(capsys.readouterr().out)==dict(code='command_invalid')


def test_recovery_selector_ceiling_preserves_utf8_opaque_and_legacy(monkeypatch):
    seen=[];monkeypatch.setattr(a,'_run',lambda *args:seen.append(args))
    for grant in ('','é'*32768,'x'*65536):
        a.outcome(object(),OP,command='grant.revoke',org_id=ORG,grant_id=grant,account_id=ACCOUNT,membership_id='1',permission='p')
        assert seen.pop()[3]['grant']==grant
    assert a.valid_opaque_grant('x'*65537)  # Historical receipt validation stays unchanged.
