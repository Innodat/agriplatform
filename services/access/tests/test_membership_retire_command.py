"""Typed membership retirement transport acceptance."""
import json
from datetime import datetime, timezone
import pytest
from test_identity_operator import Connection
from test_identity_operator_input import document, encode
import identity_operator as operator


def membership_row():
    value = document('membership.retire')
    return ({'target':{'org_id':value['scope']['org_id'].lower(),
        'account_id':value['payload']['account_id'].lower(),
        'membership_id':value['payload']['membership_id']},
        'disposition':'changed','revision':'2',
        'event_id':'c1234567-1234-1234-1234-123456789abc'},1,1,datetime.now(timezone.utc))


class MembershipConnection(Connection):
    def one_or_none(self):
        return None if self.missing else membership_row()


def test_retirement_uses_fixed_sql_and_returns_typed_receipt_only_after_commit():
    connection=MembershipConnection()
    receipt=operator.execute(connection,encode(document('membership.retire')))
    assert connection.committed
    assert receipt.result.command=='membership.retire'
    assert receipt.result.revision=='2'
    assert 'identity.retire_membership' in connection.calls[-1][0]
    assert receipt.result.target.membership_id==document('membership.retire')['payload']['membership_id']


def test_scoped_lookup_requires_and_binds_context_before_sql():
    c=MembershipConnection()
    value=document('membership.retire')
    receipt=operator.outcome(c,value['operation_id'],command='membership.retire',
        org_id=value['scope']['org_id'],account_id=value['payload']['account_id'])
    assert receipt.result.command=='membership.retire'
    assert 'identity.membership_retirement_outcome' in c.calls[-1][0]
    for context in ({'command':'membership.retire'}, {'org_id':value['scope']['org_id']},
                    {'command':'unknown'}, {'command':'actor.register_system','account_id':value['payload']['account_id']}):
        c=MembershipConnection()
        with pytest.raises(operator.OperatorError) as error:
            operator.outcome(c,value['operation_id'],**context)
        assert error.value.code=='command_invalid' and not c.calls


@pytest.mark.parametrize('mutate',[lambda r:r[0].update(revision='01'),lambda r:r[0].update(revision=2),
    lambda r:r[0].update(disposition='unchanged'),lambda r:r[0].update(event_id=None),
    lambda r:r[0]['target'].update(membership_id='9223372036854775808'),lambda r:r.__setitem__(2,2)])
def test_membership_receipt_rejects_malformed_or_unknown_versions(mutate):
    row=list(membership_row());mutate(row)
    with pytest.raises(operator.OperatorError) as error:
        operator._receipt(row,document('membership.retire')['operation_id'],'membership.retire')
    assert error.value.code=='operation_verification_unavailable'


def test_head16_retains_exact_historical_head15_verification(monkeypatch):
    import qualify_identity_baseline as q
    b=q.baseline
    monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
    seen=[];monkeypatch.setattr(b,'verify_catalog',lambda c,k:seen.append(k))
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.MEMBERSHIP_RETIRE_COMMAND_REVISION)
    b.verify_owned_postcondition(object())
    assert seen==['membership_retire_command']
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.MEMBERSHIP_ACTOR_ATTRIBUTION_REVISION)
    b.verify_owned_postcondition(object())
    assert seen[-1]=='membership_actor_attribution'
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):
        b.verify_owned_postcondition(object(),require_head=True)


@pytest.mark.parametrize('args',[
    ['--command','membership.retire'],
    ['--command','membership.retire','--org-id','a1234567-1234-1234-1234-123456789abc'],
    ['--command','actor.register_system','--account-id','a1234567-1234-1234-1234-123456789abc']])
def test_cli_rejects_missing_or_extraneous_scope_before_loading_target(args,monkeypatch,capsys):
    import operator_cli as cli
    monkeypatch.setattr(cli,'load_target',lambda _:pytest.fail('target loaded'))
    assert cli.main(['outcome','--owner','identity','--target','unused','--operation-id',
        'a1234567-1234-1234-1234-123456789abc',*args])==2
    assert json.loads(capsys.readouterr().out)['code']=='command_invalid'


def test_worker_response_requires_expected_retirement_variant():
    from dataclasses import asdict
    import operator_cli as cli
    operation=document('membership.retire')['operation_id'].lower()
    receipt=operator._receipt(membership_row(),operation,'membership.retire')
    response=asdict(receipt);response['committed_at']=receipt.committed_at.isoformat()
    assert cli.validate_response(json.dumps(response).encode(),operation,'membership.retire')==response
    with pytest.raises(ValueError):cli.validate_response(json.dumps(response).encode(),operation)


@pytest.mark.parametrize('defect',[None,'migration','missing_reference','modified_reference','source_pins'])
def test_retirement_reference_preserves_head15_chain_and_rejects_drift(tmp_path,monkeypatch,defect):
    from hashlib import sha256
    import qualify_identity_baseline as q
    b=q.baseline;calls=[]
    monkeypatch.setattr(b,'trusted_membership_actor_attribution_reference',lambda:calls.append('head15'))
    monkeypatch.setattr(b,'HERE',tmp_path)
    (tmp_path/'versions').mkdir()
    migration=tmp_path/'versions/0016_membership_retire_command.py';migration.write_bytes(b'source')
    (tmp_path/'source-pins.json').write_text('{}')
    content=json.dumps({'source_pins':{},'migration_sha256':sha256(b'source').hexdigest(),'membership_retire_command':{}}).encode()
    path=tmp_path/'membership-retire-command-reference.json';path.write_bytes(content)
    monkeypatch.setattr(b,'MEMBERSHIP_RETIRE_COMMAND_REFERENCE_SHA256',sha256(content).hexdigest())
    if defect=='migration':migration.write_bytes(b'drift')
    elif defect=='missing_reference':path.unlink()
    elif defect=='modified_reference':path.write_bytes(content+b' ')
    elif defect=='source_pins':(tmp_path/'source-pins.json').write_text('{"changed":"pin"}')
    if defect:
        with pytest.raises(b.BaselineError,match='identity_reference_unavailable'):
            b.trusted_membership_retire_command_reference()
    else:assert b.trusted_membership_retire_command_reference()=={}
    assert calls==['head15']


@pytest.mark.parametrize('field,replacement',[
    ('org_id','d1234567-1234-1234-1234-123456789abc'),
    ('account_id','d1234567-1234-1234-1234-123456789abc'),('membership_id','987654')])
def test_public_cli_rejects_well_formed_wrong_worker_target(field,replacement,tmp_path,monkeypatch,capsys):
    from dataclasses import asdict
    from types import SimpleNamespace
    import operator_cli as cli
    value=document('membership.retire');operation=value['operation_id'].lower()
    path=tmp_path/'command.json';path.write_bytes(encode(value))
    receipt=operator._receipt(membership_row(),operation,'membership.retire')
    response=asdict(receipt);response['committed_at']=receipt.committed_at.isoformat()
    response['result']['target'][field]=replacement
    monkeypatch.setattr(cli,'load_target',lambda _:SimpleNamespace(path=tmp_path/'target'))
    monkeypatch.setattr(cli,'dispatch',lambda _:json.dumps(response).encode())
    assert cli.main(['execute','--owner','identity','--target','unused','--command-file',str(path)])==2
    assert json.loads(capsys.readouterr().out)=={'code':'operation_unavailable','operation_id':operation}


@pytest.mark.parametrize('defect',['transition','event_id','executor','time','event_count',None])
def test_retained_consistency_checks_transition_identity_executor_and_time(defect,tmp_path):
    from copy import deepcopy
    from qualify_membership_retire_command import RetirementQualification
    result,cv,rv,instant=membership_row();target=result['target']
    executor='e1234567-1234-1234-1234-123456789abc'
    row=[document('membership.retire')['operation_id'].lower(),result,cv,rv,instant,
         executor,target['org_id'],result['event_id'],'identity.membership_retired',1,instant,
         executor,target['org_id'],deepcopy(target),target['membership_id'],
         {'before':{'revision':'1','retired':False},'after':{'revision':'2','retired':True}},
         target['membership_id'],target['org_id'],target['account_id'],2,instant,instant,executor,1]
    if defect=='transition':row[15]['before']['revision']='2'
    elif defect=='event_id':row[7]='d1234567-1234-1234-1234-123456789abc'
    elif defect=='executor':row[11]='d1234567-1234-1234-1234-123456789abc'
    elif defect=='time':row[10]=instant.replace(year=instant.year-1)
    elif defect=='event_count':row[23]=2
    q=RetirementQualification(tmp_path,{})
    q.sql=lambda *a,**k:[row]
    if defect:
        with pytest.raises(AssertionError):q.verify_all_retirements('clean')
    else:assert q.verify_all_retirements('clean')[0]['result']['target']==target
