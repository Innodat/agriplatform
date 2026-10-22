"""Grant assignment transport stays closed and binds the exact selected target."""
from datetime import datetime,timezone
from dataclasses import asdict
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import access_operator as a
import operator_cli as cli
from access_operator_input import parse_command
from test_grant_assign_input import document,ORG,ACCOUNT
from test_application_register import OP


def result():
    return dict(target=dict(grant_id='opaque:existing grant',org_id=ORG.lower(),account_id=ACCOUNT.lower(),membership_id='9007199254740993',permission='literal:*\n'),disposition='changed',revision='2',event_id=OP)


def test_assignment_execute_and_outcome_bind_exact_target(monkeypatch):
    seen=[];monkeypatch.setattr(a,'_run',lambda *args:seen.append(args))
    value=document();value['payload']['membership_id']='9007199254740993'
    a.execute(object(),json.dumps(value).encode())
    call=seen.pop();assert 'access.assign_organization_grant(' in call[2]
    assert call[3]['account']==ACCOUNT.lower() and call[3]['org']==ORG.lower()
    assert call[3]['member']=='9007199254740993' and call[3]['absent'] is True and call[3]['revision'] is None
    assert call[-1]=='grant.assign'
    canonical=json.loads(a.canonical_command(parse_command(json.dumps(value).encode())))
    assert canonical['payload']['account_id']==ACCOUNT.lower() and canonical['scope']['org_id']==ORG.lower()
    a.outcome(object(),OP,command='grant.assign',org_id=ORG,account_id=ACCOUNT,membership_id='9007199254740993',permission=value['payload']['permission'])
    call=seen.pop();assert 'access.organization_grant_assignment_outcome(' in call[2]
    assert call[3]['account']==ACCOUNT.lower() and call[3]['member']=='9007199254740993'


def test_assignment_receipt_preserves_opaque_identifier_and_exact_decimal():
    receipt=a._receipt((result(),1,1,datetime.now(timezone.utc)),OP,'grant.assign')
    assert receipt.result.target.grant_id=='opaque:existing grant'
    assert receipt.result.target.membership_id=='9007199254740993'
    wire=asdict(receipt);wire['committed_at']=receipt.committed_at.isoformat()
    assert cli.validate_response(json.dumps(wire).encode(),OP,'grant.assign',result()['target'])==wire
    for field,changed in [('org_id',OP),('account_id',OP),('membership_id','9007199254740992'),('permission','other')]:
        with pytest.raises(ValueError):cli.validate_response(json.dumps(wire).encode(),OP,'grant.assign',result()['target']|{field:changed})


@pytest.mark.parametrize('field,bad',[('membership_id',True),('membership_id',1),('membership_id','01'),('membership_id','9223372036854775808'),('account_id','00000000-0000-0000-0000-000000000000'),('org_id',ORG),('grant_id',None),('permission','é')])
def test_assignment_receipt_refuses_malformed_target(field,bad):
    value=result();value['target'][field]=bad
    with pytest.raises(a.OperatorError) as caught:a._receipt((value,1,1,datetime.now(timezone.utc)),OP,'grant.assign')
    assert caught.value.code=='operation_verification_unavailable'


@pytest.mark.parametrize('changes',[dict(disposition='created',revision='2'),dict(disposition='changed',revision='1'),dict(event_id=None),dict(disposition='unchanged'),dict(revision='01'),dict(revision=True)])
def test_assignment_receipt_refuses_bad_transition(changes):
    with pytest.raises(a.OperatorError):a._receipt((result()|changes,1,1,datetime.now(timezone.utc)),OP,'grant.assign')


def test_assignment_outcome_rejects_irrelevant_or_missing_selectors_before_sql(monkeypatch):
    monkeypatch.setattr(a,'_run',lambda *args:pytest.fail('invalid lookup touched SQL'))
    good=dict(command='grant.assign',org_id=ORG,account_id=ACCOUNT,membership_id='1',permission='p')
    for changed in (dict(app_id='fixture_app'),dict(account_id=None),dict(membership_id=1),dict(membership_id='01'),dict(org_id=None),dict(permission='')):
        with pytest.raises(a.OperatorError):a.outcome(object(),OP,**(good|changed))


def test_retained_opaque_ids_need_no_uuid_or_nonempty_normalization():
    for grant_id in ('', 'retained é : identifier', 'x'*10000):
        value=result();value['target']['grant_id']=grant_id
        assert a._receipt((value,1,1,datetime.now(timezone.utc)),OP,'grant.assign').result.target.grant_id==grant_id


def test_cli_assignment_execute_outcome_and_mismatched_response(tmp_path,monkeypatch,capsys):
    from types import SimpleNamespace
    value=document();value['operation_id']=OP
    path=tmp_path/'command.json';path.write_text(json.dumps(value))
    seen=[];target=SimpleNamespace(path=tmp_path/'trusted-target')
    monkeypatch.setattr(cli,'load_target',lambda *args,**kwargs:target)
    target_result=result();target_result['target'].update(membership_id='1',permission=value['payload']['permission'])
    receipt=a._receipt((target_result,1,1,datetime.now(timezone.utc)),OP,'grant.assign')
    wire=asdict(receipt);wire['committed_at']=receipt.committed_at.isoformat()
    def dispatch(request):seen.append(request);return json.dumps(wire).encode()
    monkeypatch.setattr(cli,'dispatch',dispatch)
    execute=['execute','--owner','access','--target','unused','--command-file',str(path)]
    assert cli.main(execute)==0
    assert json.loads(capsys.readouterr().out)==wire
    assert seen[-1][0]=='execute' and seen[-1][4]=='access' and json.loads(seen[-1][2])==value
    lookup=['outcome','--owner','access','--target','unused','--command','grant.assign','--operation-id',OP,
        '--org-id',ORG,'--account-id',ACCOUNT,'--membership-id','1','--permission',value['payload']['permission']]
    assert cli.main(lookup)==0
    assert json.loads(capsys.readouterr().out)==wire
    assert seen[-1][2]==dict(command='grant.assign',org_id=ORG.lower(),account_id=ACCOUNT.lower(),membership_id='1',permission=value['payload']['permission'])
    wire['result']['target']['account_id']=OP
    for argv in (execute,lookup):
        assert cli.main(argv)==2
        output=capsys.readouterr();assert json.loads(output.out)==dict(code='operation_unavailable',operation_id=OP) and output.err==''


@pytest.mark.parametrize('extra',[['--app-id','fixture_app'],['--membership-id','2'],['--account-id',OP]])
def test_cli_assignment_refuses_irrelevant_duplicate_flags_before_target(extra,monkeypatch,capsys):
    monkeypatch.setattr(cli,'load_target',lambda *args,**kwargs:pytest.fail('invalid lookup opened target'))
    argv=['outcome','--owner','access','--target','unused','--command','grant.assign','--operation-id',OP,
        '--org-id',ORG,'--account-id',ACCOUNT,'--membership-id','1','--permission','p']
    assert cli.main(argv+extra)==2
    output=capsys.readouterr();assert json.loads(output.out)==dict(code='command_invalid') and output.err==''


def test_created_and_unchanged_receipts_obey_event_revision_contract():
    value=result();value['target']['grant_id']=OP
    for changes in (dict(disposition='created',revision='1'),dict(disposition='unchanged',revision='9223372036854775807',event_id=None)):
        assert a._receipt((value|changes,1,1,datetime.now(timezone.utc)),OP,'grant.assign')
    value['target']['grant_id']='opaque existing'
    with pytest.raises(a.OperatorError):a._receipt((value|dict(disposition='created',revision='1'),1,1,datetime.now(timezone.utc)),OP,'grant.assign')
