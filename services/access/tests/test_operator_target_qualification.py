"""Qualification guards must survive optimized Python; no live DB access here."""
from pathlib import Path
import json
import subprocess
import sys


def test_optimized_python_invalid_private_fixture_refuses_before_network(tmp_path):
    tmp_path.chmod(0o700)
    fixture=tmp_path/'fixture.json'
    fixture.write_text(json.dumps({'owner_url':'private-do-not-echo'}));fixture.chmod(0o600)
    tests=Path(__file__).resolve().parent
    script='''import sys
from types import SimpleNamespace
sys.path.insert(0,sys.argv[1])
import qualify_operator_target as q
q.load_target=lambda _:SimpleNamespace(run_id='run',database='db',port=55482)
def no_network(*args,**kwargs):raise BaseException('network-dispatched')
q.create_engine=no_network
try:q.qualify('unused',sys.argv[2])
except RuntimeError as error:
    if str(error)!='qualification_fixture_invalid':raise
    print('closed')
else:raise BaseException('unsafe acceptance')
'''
    result=subprocess.run([sys.executable,'-I','-B','-O','-c',script,str(tests),str(fixture)],capture_output=True,timeout=4)
    assert result.returncode==0 and result.stdout==b'closed\n' and not result.stderr


def test_exact_effect_rejects_unrelated_mutation_and_wrong_links():
    import copy
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    import qualify_operator_target as q
    import pytest
    executor='executor';actor_id='actor';operation='operation';event_id='event';outcome_id='outcome'
    value={'operation_id':operation,'command':'actor.register_system','reason_code':'synthetic_fixture',
        'payload':{'actor_id':actor_id,'kind':'service','actor_key':'synthetic:key','display_name':'Synthetic'}}
    result={'target':{'actor_id':actor_id},'disposition':'created','revision':None,'event_id':event_id,'command':value['command']}
    receipt={'result':result,'command_version':1,'result_version':1}
    before={'actor':[{'id':executor,'display_name':'Original'}],'operation_outcome':[],
        'business_event':[],'operator_principals':[{'database_login':'identity_operator','executor_actor_id':executor}],'other':[{'id':'original'}]}
    after=copy.deepcopy(before)
    after['actor'].append({'id':actor_id,'kind':'service','actor_key':'synthetic:key','display_name':'Synthetic','created_by':executor,'updated_by':executor})
    common={'scope_kind':'platform','scope_id':None,'initiator_actor_id':None,'executor_actor_id':executor}
    after['operation_outcome'].append({**common,'id':outcome_id,'operation_id':operation,'command_type':value['command'],'command_version':1,'result_version':1,'result':{k:v for k,v in result.items() if k!='command'}})
    after['business_event'].append({**common,'event_id':event_id,'outcome_id':outcome_id,'event_type':'identity.actor_registered','event_version':1,'target_key':actor_id,'target':{'actor_id':actor_id},'transition':{'kind':'service','actor_key':'synthetic:key'},'reason_code':'synthetic_fixture','evidence_ref':None})
    q.verify_effect(before,after,value,receipt)
    for table,index,field,bad in [('actor',0,'display_name','Changed'),('other',0,'id','changed'),('business_event',0,'outcome_id','wrong'),('operation_outcome',0,'operation_id','wrong')]:
        changed=copy.deepcopy(after);changed[table][index][field]=bad
        with pytest.raises(RuntimeError):q.verify_effect(before,changed,value,receipt)
