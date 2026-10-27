"""Native target and semantic assertion guards; mocks do not qualify PostgreSQL."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import identity_native_guard as guard
import qualify_person_links as q

@pytest.mark.parametrize('defect',[None,'stopped','binding','network','count','target','port','marker'])
def test_actual_leave_guard_checks_marker_container_network_and_loopback(monkeypatch,defect):
    environment=dict(target_id='leave-local',ports=dict(database=55582),workspace_root=str(guard.ROOT))
    row=dict(State=dict(Running=True),NetworkSettings=dict(Ports={'5432/tcp':[dict(HostIp='127.0.0.1',HostPort='55582')]},Networks={'project-network':dict(NetworkID='verified-network')}))
    rows=[row]
    if defect=='stopped':row['State']['Running']=False
    elif defect=='binding':row['NetworkSettings']['Ports']['5432/tcp'][0]['HostIp']='0.0.0.0'
    elif defect=='network':row['NetworkSettings']['Networks']['project-network']['NetworkID']='foreign-network'
    elif defect=='count':rows.append(row)
    elif defect=='target':environment['target_id']='kdg-local'
    elif defect=='port':environment['ports']['database']=55482
    monkeypatch.setattr(guard.dev,'read',lambda _:json.dumps(environment).encode())
    monkeypatch.setattr(guard.dev,'project_identity',lambda *args:'project')
    monkeypatch.setattr(guard.native_cli,'validate_target',lambda _:None)
    monkeypatch.setattr(guard.native_cli,'run_path',lambda *args:Path('/explicit/run'))
    def marker(*args):
        if defect=='marker':raise ValueError('native_marker_changed')
    monkeypatch.setattr(guard.native_cli,'check_run',marker)
    monkeypatch.setattr(guard.native_cli,'network',lambda *args:'verified-network')
    monkeypatch.setattr(guard.native_cli,'docker',lambda *args:json.dumps(rows).encode())
    if defect:
        with pytest.raises(ValueError):guard.guard()
    else:assert guard.guard()==(environment,Path('/explicit/run'))

def test_qualifier_refuses_connection_before_native_target_verification(monkeypatch):
    def refused():raise ValueError('native_target_invalid')
    monkeypatch.setattr(q,'guard',refused)
    monkeypatch.setattr(q,'create_engine',lambda *args,**kwargs:pytest.fail('connection before native guard'))
    with pytest.raises(ValueError,match='native_target_invalid'):q.Qualification(dict(database='idb_88a737ddad7b_test',runtime_url='postgresql://access_runtime:synthetic@127.0.0.1:55582/idb_88a737ddad7b_test')).engine('runtime_url')

@pytest.mark.parametrize('defect',[None,'account','actor','person','revision','revision_bool','missing'])
def test_projection_assertion_requires_exact_person_and_revision(defect):
    row=['account','actor','person',1]
    if defect in ('account','actor','person'):row[{'account':0,'actor':1,'person':2}[defect]]='foreign'
    elif defect=='revision':row[3]=2
    elif defect=='revision_bool':row[3]=True
    rows=[] if defect=='missing' else [row]
    if defect:
        with pytest.raises(AssertionError):q.assert_projection(rows,'account','actor','person',1)
    else:q.assert_projection(rows,'account','actor','person',1)

@pytest.mark.parametrize('defect',[None,'duplicate','event','outcome','target','result','type'])
def test_race_evidence_requires_one_exact_linked_event(defect):
    result=SimpleNamespace(target=SimpleNamespace())
    # Use the actual typed receipt's compact representation.
    from test_person_links import OP,PERSON,document
    from identity_operator import PersonResult,PersonTarget,Receipt
    from datetime import datetime,timezone
    receipt=Receipt(OP,PersonResult('person.create',PersonTarget(PERSON),'created','1',OP),1,1,datetime.now(timezone.utc))
    compact=dict(target=dict(person_id=PERSON),disposition='created',revision='1',event_id=OP)
    row=['outcome','person.create',OP,compact,OP,'outcome',dict(person_id=PERSON),'identity.person_created']
    if defect=='event':row[4]='foreign'
    elif defect=='outcome':row[5]='foreign'
    elif defect=='target':row[6]=dict(person_id='foreign')
    elif defect=='result':row[3]={**compact,'revision':'2'}
    elif defect=='type':row[7]='identity.account_person_linked'
    rows=[row,row] if defect=='duplicate' else [row]
    if defect:
        with pytest.raises(AssertionError):q.assert_event_evidence(rows,document(),receipt)
    else:q.assert_event_evidence(rows,document(),receipt)


def test_direct_engine_construction_rejects_foreign_database_before_guard(monkeypatch):
    monkeypatch.setattr(q,'guard',lambda:pytest.fail('foreign target reached native guard'))
    monkeypatch.setattr(q,'create_engine',lambda *args,**kwargs:pytest.fail('foreign database connected'))
    with pytest.raises(ValueError,match='qualification_target_invalid'):
        q.Qualification(dict(database='foreign',runtime_url='postgresql://access_runtime:synthetic@127.0.0.1:55582/foreign')).engine('runtime_url')
