"""Closed person commands, canonical identity and compact recovery contracts."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
from copy import deepcopy
from datetime import datetime,timezone
import pytest
import identity_operator_input as inputs
import identity_operator as operator

PERSON='b232820e-f9e0-4f63-a218-9215d4d09b43'
ACCOUNT='091580ed-ed07-4403-aec3-dcbe619acc63'
ACTOR='440ae776-06d3-4fbb-99cc-1dc1b64a4810'
OP='1c2aef61-94d6-4718-bd8b-570033b2ce8c'
def document(link=False):
    return dict(schema_version=1,operation_id=OP,command='account.link_person' if link else 'person.create',scope=dict(kind='platform'),payload=dict(person_id=PERSON,**(dict(account_id=ACCOUNT,actor_id=ACTOR) if link else {}),expected_absent=True),reason_code='synthetic_fixture',evidence_ref='fixture:verified')

@pytest.mark.parametrize('link',[False,True])
def test_person_commands_have_closed_typed_canonical_models(link):
    value=document(link)
    command=inputs.parse_command(json.dumps(value).encode())
    assert command.command==value['command']
    alias=deepcopy(value);alias['payload']['person_id']=PERSON.upper()
    assert operator.canonical_command(inputs.parse_command(json.dumps(alias).encode()))==operator.canonical_command(command)

@pytest.mark.parametrize('defect',['extra','zero','org','evidence','expected','both'])
def test_invalid_person_links_are_refused(defect):
    value=document(True)
    if defect=='extra':value['payload']['email']='private@example.invalid'
    elif defect=='zero':value['payload']['person_id']='00000000-0000-0000-0000-000000000000'
    elif defect=='org':value['scope']=dict(kind='organization',org_id=PERSON)
    elif defect=='evidence':value.pop('evidence_ref')
    elif defect=='expected':value['payload'].pop('expected_absent')
    elif defect=='both':value['payload']['expected_revision']='1'
    with pytest.raises(inputs.CommandValidationError):inputs.parse_command(json.dumps(value).encode())

def test_link_explicit_revision_is_decimal_string():
    value=document(True);value['payload'].pop('expected_absent');value['payload']['expected_revision']='1'
    assert inputs.parse_command(json.dumps(value).encode()).payload.expected_revision=='1'
    value['payload']['expected_revision']=1
    with pytest.raises(inputs.CommandValidationError):inputs.parse_command(json.dumps(value).encode())

@pytest.mark.parametrize('link',[False,True])
def test_person_receipts_are_typed_and_fail_closed(link):
    target=dict(person_id=PERSON,**(dict(account_id=ACCOUNT,actor_id=ACTOR) if link else {}))
    result=dict(target=target,disposition='created',revision='1',event_id=OP)
    receipt=operator._receipt((result,1,1,datetime.now(timezone.utc)),OP,'account.link_person' if link else 'person.create')
    assert receipt.result.target.person_id==PERSON
    result['target']['email']='private@example.invalid'
    with pytest.raises(operator.OperatorError):operator._receipt((result,1,1,datetime.now(timezone.utc)),OP,'account.link_person' if link else 'person.create')

@pytest.mark.parametrize('link',[False,True])
def test_execute_and_lookup_keep_exact_person_target(link):
    from test_identity_operator import Connection
    value=document(link)
    target=dict(person_id=PERSON,**(dict(account_id=ACCOUNT,actor_id=ACTOR) if link else {}))
    class PersonConnection(Connection):
        def one_or_none(self):
            return dict(target=target,disposition='created',revision='1',event_id=OP),1,1,datetime.now(timezone.utc)
    connection=PersonConnection()
    receipt=operator.execute(connection,json.dumps(value).encode())
    assert connection.committed and receipt.result.command==value['command']
    assert ('identity.link_person' if link else 'identity.create_person') in connection.calls[-1][0]
    lookup=PersonConnection()
    assert operator.outcome(lookup,OP,command=value['command'],person_id=PERSON,**(dict(account_id=ACCOUNT) if link else {})).result==receipt.result
    assert lookup.calls[-1][1]['person']==PERSON
    with pytest.raises(operator.OperatorError):operator.outcome(PersonConnection(),OP,command=value['command'],person_id=None)

@pytest.mark.parametrize('link',[False,True])
def test_cli_execute_and_scoped_outcome_transport(link,tmp_path,monkeypatch,capsys):
    import operator_cli as cli
    from types import SimpleNamespace
    value=document(link);path=tmp_path/'command.json';path.write_text(json.dumps(value))
    monkeypatch.setattr(cli,'load_target',lambda _:SimpleNamespace(path=tmp_path/'target.json'))
    sent=[]
    monkeypatch.setattr(cli,'dispatch',lambda request:sent.append(request) or json.dumps(dict(operation_id=OP,status='unresolved')).encode())
    assert cli.main(['execute','--owner','identity','--target','prepared','--command-file',str(path)])==2
    assert sent[-1][2]==json.dumps(value)
    assert json.loads(capsys.readouterr().out)['status']=='unresolved'
    args=['outcome','--owner','identity','--target','prepared','--command',value['command'],'--operation-id',OP,'--person-id',PERSON]
    if link:args+=['--account-id',ACCOUNT]
    assert cli.main(args)==2
    assert sent[-1][2]==dict(command=value['command'],person_id=PERSON,**(dict(account_id=ACCOUNT) if link else {}))
    assert json.loads(capsys.readouterr().out)['status']=='unresolved'

@pytest.mark.parametrize('defect',[None,'extra','login','port','database','cohort','run'])
def test_native_qualifier_requires_explicit_bound_private_fixture(tmp_path,defect):
    import qualify_person_links as qualifier
    run='88a737dd-ad7b-429a-a83c-5d103716d659'
    value=dict(run_id=run,port=55582,database='idb_88a737ddad7b_1234abcd',
        owner_url='postgresql://identity_migrator:synthetic@127.0.0.1:55582/idb_88a737ddad7b_1234abcd',
        operator_url='postgresql://identity_operator:synthetic@127.0.0.1:55582/idb_88a737ddad7b_1234abcd',
        runtime_url='postgresql://access_runtime:synthetic@127.0.0.1:55582/idb_88a737ddad7b_1234abcd',
        cohorts={name:dict(account_id=str(__import__('uuid').uuid4()),actor_id=str(__import__('uuid').uuid4())) for name in ('retained','second','recreated','inactive','unlinked','missing_actor','foreign_target')},cli_target=str(Path(__file__).resolve().parents[3]/'platform/deployment/.local/leave'/run/'identity-operator-1234abcd.json'))
    value['cohorts']['missing_actor']['actor_id']=None
    if defect=='extra':value['discover']=True
    elif defect=='login':value['owner_url']=value['owner_url'].replace('identity_migrator','postgres')
    elif defect=='port':value['operator_url']=value['operator_url'].replace('55582','55583')
    elif defect=='database':value['runtime_url']=value['runtime_url'].replace('/idb_88a737ddad7b_1234abcd','/foreign')
    elif defect=='cohort':value['cohorts']['second']=value['cohorts']['retained']
    elif defect=='run':value['run_id']=PERSON
    path=tmp_path/'private.json';path.write_text(json.dumps(value));path.chmod(0o600)
    if defect:
        with pytest.raises(ValueError):qualifier.load_fixture(path,run,55582)
    else:assert qualifier.load_fixture(path,run,55582)==value

@pytest.mark.parametrize('run,port',[(PERSON,55582),('88a737dd-ad7b-429a-a83c-5d103716d659',55482)])
def test_native_qualifier_refuses_caller_selected_foreign_target(tmp_path,run,port):
    import qualify_person_links as qualifier
    value=dict(run_id=run,port=port,database='idb_88a737ddad7b_1234abcd',
        owner_url=f'postgresql://identity_migrator:synthetic@127.0.0.1:{port}/idb_88a737ddad7b_1234abcd',
        operator_url=f'postgresql://identity_operator:synthetic@127.0.0.1:{port}/idb_88a737ddad7b_1234abcd',
        runtime_url=f'postgresql://access_runtime:synthetic@127.0.0.1:{port}/idb_88a737ddad7b_1234abcd',
        cohorts={name:dict(account_id=str(__import__('uuid').uuid4()),actor_id=str(__import__('uuid').uuid4())) for name in ('retained','second','recreated','inactive','unlinked','missing_actor','foreign_target')},cli_target=str(Path(__file__).resolve().parents[3]/'platform/deployment/.local/leave'/run/'identity-operator-1234abcd.json'))
    value['cohorts']['missing_actor']['actor_id']=None
    path=tmp_path/'private.json';path.write_text(json.dumps(value));path.chmod(0o600)
    with pytest.raises(ValueError):qualifier.load_fixture(path,run,port)

@pytest.mark.parametrize('state',['42501','42601','23503',None])
def test_native_permission_oracle_requires_insufficient_privilege(state):
    import qualify_person_links as qualifier
    from types import SimpleNamespace
    failure=RuntimeError('synthetic database error');failure.orig=SimpleNamespace(sqlstate=state)
    class Connection:
        rolled=False
        def execute(self,*args):raise failure
        def rollback(self):self.rolled=True
    connection=Connection()
    if state=='42501':
        qualifier.require_permission_denial(connection,'SELECT * FROM identity.person')
        assert connection.rolled
    else:
        with pytest.raises(RuntimeError) as error:qualifier.require_permission_denial(connection,'SELECT * FROM identity.person')
        assert error.value is failure and connection.rolled

def test_native_permission_oracle_refuses_unexpected_success():
    import qualify_person_links as qualifier
    class Connection:
        def execute(self,*args):return self
    with pytest.raises(AssertionError,match='qualification_runtime_boundary_failed'):
        qualifier.require_permission_denial(Connection(),'SELECT * FROM identity.person')


def test_native_diagnostics_do_not_expose_exception_text_or_parameters():
    import qualify_person_links as qualifier
    failure=operator.OperatorError('operation_unavailable',OP)
    try:raise failure
    except operator.OperatorError as error:diagnostic=qualifier.safe_diagnostic(error)
    assert diagnostic['code']=='operation_unavailable'
    assert all(set(location)=={'file','line'} for location in diagnostic['locations'])
    try:raise RuntimeError('PRIVATE SQL VALUES postgresql://secret@host/database')
    except RuntimeError as error:diagnostic=qualifier.safe_diagnostic(error)
    assert 'PRIVATE' not in json.dumps(diagnostic) and 'secret' not in json.dumps(diagnostic)


def test_native_journal_is_private_durable_and_never_overwrites(tmp_path):
    import qualify_person_links as qualifier
    path=tmp_path/'attempts.jsonl';journal=qualifier.Journal(path)
    reference=dict(stage='execute',command='person.create',operation_id=OP,target=dict(person_id=PERSON),status='attempting')
    journal(reference)
    assert json.loads(path.read_text())==reference and path.stat().st_mode & 0o777==0o600
    journal.close()
    with pytest.raises(FileExistsError):qualifier.Journal(path)


def test_native_operation_reference_is_recorded_before_connection_failure(monkeypatch):
    import qualify_person_links as qualifier
    records=[];runner=qualifier.Qualification({},records.append)
    def unavailable(key):raise RuntimeError('PRIVATE connection material')
    monkeypatch.setattr(runner,'engine',unavailable)
    with pytest.raises(RuntimeError):runner.invoke(document(True))
    assert records==[dict(stage='execute',command='account.link_person',operation_id=OP,
        target=dict(account_id=ACCOUNT,person_id=PERSON,actor_id=ACTOR),credential_kind='operator_url',status='attempting')]
    assert 'PRIVATE' not in json.dumps(records)

@pytest.mark.parametrize('event',['',False,0,[],{}])
@pytest.mark.parametrize('command',['person.create','account.link_person'])
def test_created_receipt_rejects_every_non_null_malformed_event(event,command):
    target=dict(person_id=PERSON,**(dict(account_id=ACCOUNT,actor_id=ACTOR) if command=='account.link_person' else {}))
    with pytest.raises(operator.OperatorError):
        operator._receipt((dict(target=target,disposition='created',revision='1',event_id=event),1,1,datetime.now(timezone.utc)),OP,command)


def test_native_person_qualifier_documented_isolated_entrypoint_loads():
    import subprocess
    result=subprocess.run([sys.executable,'-I','-B',str(Path(__file__).with_name('qualify_person_links.py')),'--help'],capture_output=True,timeout=10)
    assert result.returncode==0 and b'--fixture' in result.stdout and not result.stderr
