"""Join writer/seed cutover unit acceptance; actual sessions live in qualifier."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'services/access'))


def test_demo_seed_refuses_before_import_or_client_side_effects():
    result=subprocess.run([sys.executable,'-I','-B',str(ROOT/'scripts/seed.py')],capture_output=True,text=True)
    assert result.returncode != 0
    assert 'identity_legacy_demo_seed_retired' in result.stderr
    assert 'ModuleNotFoundError' not in result.stderr


def test_owned_seed_composition_requires_no_seeds_and_empty_generated_output(tmp_path):
    path=ROOT/'tools/py/run_compose_supabase.py'
    spec=importlib.util.spec_from_file_location('join_composer',path);m=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=m;spec.loader.exec_module(m)
    stale=tmp_path/'seeds';stale.mkdir()
    with pytest.raises(SystemExit):m.validate_identity_seeds('owned',False,stale)
    m.validate_identity_seeds('owned',True,stale)
    source=stale/'old.sql';source.write_text('retained fixture')
    with pytest.raises(SystemExit):m.validate_identity_seeds('owned',True,stale)
    assert source.read_text()=='retained fixture'
    m.validate_identity_seeds('legacy',False,stale)


def test_historical_heads18_17_16_preserve_catalog_dispatch(monkeypatch):
    import qualify_identity_baseline as q
    b=q.baseline
    monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
    seen=[];monkeypatch.setattr(b,'verify_catalog',lambda c,k:seen.append(k))
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.MEMBERSHIP_JOIN_COMMAND_REVISION)
    b.verify_owned_postcondition(object())
    assert seen==['membership_join_command']
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):
        b.verify_owned_postcondition(object(),require_head=True)
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.ACCOUNT_ACTOR_ENSURE_REVISION)
    b.verify_owned_postcondition(object())
    assert seen[-1]=='account_actor_ensure'
    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.MEMBERSHIP_RETIRE_COMMAND_REVISION)
    b.verify_owned_postcondition(object())
    assert seen[-1]=='membership_retire_command'
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):
        b.verify_owned_postcondition(object(),require_head=True)


@pytest.mark.parametrize('defect',[None,'migration','missing_reference','modified_reference','source_pins'])
def test_join_reference_retains_historical_chain_and_refuses_drift(tmp_path,monkeypatch,defect):
    import json
    from hashlib import sha256
    import qualify_identity_baseline as q
    b=q.baseline;calls=[]
    monkeypatch.setattr(b,'trusted_membership_retire_command_reference',lambda:calls.append('head16'))
    monkeypatch.setattr(b,'HERE',tmp_path)
    (tmp_path/'versions').mkdir()
    migration=tmp_path/'versions/0017_membership_join_command.py';migration.write_bytes(b'source')
    (tmp_path/'source-pins.json').write_text('{}')
    content=json.dumps({'source_pins':{},'migration_sha256':sha256(b'source').hexdigest(),'membership_join_command':{}}).encode()
    path=tmp_path/'membership-join-command-reference.json';path.write_bytes(content)
    monkeypatch.setattr(b,'MEMBERSHIP_JOIN_COMMAND_REFERENCE_SHA256',sha256(content).hexdigest())
    if defect=='migration':migration.write_bytes(b'drift')
    elif defect=='missing_reference':path.unlink()
    elif defect=='modified_reference':path.write_bytes(content+b' ')
    elif defect=='source_pins':(tmp_path/'source-pins.json').write_text('{"changed":"pin"}')
    if defect:
        with pytest.raises(b.BaselineError,match='identity_reference_unavailable'):b.trusted_membership_join_command_reference()
    else:assert b.trusted_membership_join_command_reference()=={}
    assert calls==['head16']


@pytest.mark.parametrize('revision,disposition',[('2','created'),('1','changed'),('01','created')])
def test_join_created_result_rejects_other_lifecycles(revision,disposition):
    from datetime import datetime,timezone
    import identity_operator as o
    result={'target':{'org_id':'c1234567-1234-1234-1234-123456789abc','account_id':'b1234567-1234-1234-1234-123456789abc','membership_id':'91'},
            'disposition':disposition,'revision':revision,'event_id':'d1234567-1234-1234-1234-123456789abc'}
    with pytest.raises(o.OperatorError,match='operation_verification_unavailable'):
        o._receipt((result,1,1,datetime.now(timezone.utc)),'a1234567-1234-1234-1234-123456789abc','membership.join')


def test_qualification_entrypoint_hides_unexpected_database_diagnostics(monkeypatch,capsys):
    import qualify_membership_join_command as q
    def fail():raise RuntimeError('PRIVATE SQL credentials and diagnostic values')
    monkeypatch.setattr(q,'main',fail)
    assert q.entrypoint()==1
    result=capsys.readouterr()
    assert result.out=='' and result.err=='membership_join_qualification_failed\n'


def join_cli_response():
    from datetime import datetime,timezone
    from dataclasses import asdict
    from test_identity_operator_input import document
    import identity_operator as o
    value=document('membership.join');operation=value['operation_id'].lower()
    result={'target':{'org_id':value['scope']['org_id'].lower(),
        'account_id':value['payload']['account_id'].lower(),'membership_id':'91'},
        'disposition':'created','revision':'1','event_id':'d1234567-1234-1234-1234-123456789abc'}
    receipt=o._receipt((result,1,1,datetime.now(timezone.utc)),operation,'membership.join')
    response=asdict(receipt);response['committed_at']=receipt.committed_at.isoformat()
    return value,response


@pytest.mark.parametrize('defect', ['org','account','command','revision','member_zero','member_overflow'])
def test_public_join_cli_refuses_adversarial_worker_receipt(defect,tmp_path,monkeypatch,capsys):
    import json
    from types import SimpleNamespace
    from test_identity_operator_input import encode
    import operator_cli as cli
    value,response=join_cli_response();operation=response['operation_id']
    path=tmp_path/'join.json';path.write_bytes(encode(value))
    result=response['result']
    if defect in ('org','account'):result['target'][defect+'_id']='e1234567-1234-1234-1234-123456789abc'
    elif defect=='command':result['command']='membership.retire'
    elif defect=='revision':result['revision']='2'
    else:result['target']['membership_id']='0' if defect=='member_zero' else '9223372036854775808'
    monkeypatch.setattr(cli,'load_target',lambda _:SimpleNamespace(path=tmp_path/'target'))
    monkeypatch.setattr(cli,'dispatch',lambda _:json.dumps(response).encode())
    assert cli.main(['execute','--owner','identity','--target','unused','--command-file',str(path)])==2
    output=json.loads(capsys.readouterr().out)
    assert output=={'code':'operation_unavailable','operation_id':operation}


@pytest.mark.parametrize('status',['unresolved','access_denied','operation_unavailable'])
def test_public_join_lookup_preserves_operation_and_safe_result(status,tmp_path,monkeypatch,capsys):
    import json
    from types import SimpleNamespace
    import operator_cli as cli
    value,response=join_cli_response();operation=response['operation_id'];seen=[]
    expected={'operation_id':operation,**({'status':'unresolved'} if status=='unresolved' else {'code':status})}
    monkeypatch.setattr(cli,'load_target',lambda _:SimpleNamespace(path=tmp_path/'target'))
    def dispatch(request):seen.append(request);return json.dumps(expected).encode()
    monkeypatch.setattr(cli,'dispatch',dispatch)
    assert cli.main(['outcome','--owner','identity','--target','unused','--command','membership.join',
        '--operation-id',operation,'--org-id',value['scope']['org_id'],'--account-id',value['payload']['account_id']])==2
    assert json.loads(capsys.readouterr().out)==expected
    assert seen==[['outcome',str(tmp_path/'target'),{'command':'membership.join',
        'org_id':value['scope']['org_id'].lower(),'account_id':value['payload']['account_id'].lower()},operation]]
