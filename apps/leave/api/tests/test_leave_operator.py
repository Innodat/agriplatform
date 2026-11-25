"""Closed configuration validation and exact bounded JCS subset vectors."""
import json,pytest
from leave_operator import parse_command,canonical_command,OperationError
ORG='11111111-1111-4111-8111-111111111111'
TYPE='22222222-2222-4222-8222-222222222222'
VERSION='33333333-3333-4333-8333-333333333333'
def command():return {'schema_version':1,'operation_id':'44444444-4444-4444-8444-444444444444','command':'leave_type.create','scope':{'kind':'organization','org_id':ORG},'payload':{'type_id':TYPE,'version_id':VERSION,'code':' ANNUAL ','name':' Annual 😀 ','permitted_modes':['hours','full_days'],'effective_from':'2040-01-01','effective_to':None,'expected_absent':True},'reason_code':'synthetic_fixture'}
def test_normalized_configuration_arrays_and_unicode_preserved():
 c=parse_command(json.dumps(command()).encode());assert c.payload.code=='annual';assert c.payload.name=='Annual 😀';assert c.payload.permitted_modes==['full_days','hours']
 raw=canonical_command(c);assert b'"permitted_modes":["full_days","hours"]' in raw;assert '😀'.encode() in raw
 assert raw==canonical_command(parse_command(json.dumps(command(),ensure_ascii=False,sort_keys=True).encode()))
@pytest.mark.parametrize('field,value',[('name','bad\nname'),('name','\ud800'),('code','1bad'),('permitted_modes',[]),('permitted_modes',['hours','hours']),('permitted_modes',['unknown']),('effective_to','2030-01-01'),('expected_absent',1),('actor_id',ORG)])
def test_invalid_closed_input(field,value):
 c=command();c['payload'][field]=value
 with pytest.raises(OperationError,match='command_invalid'):parse_command(json.dumps(c).encode())
def test_unknown_schema_spoofed_actor_duplicate_and_invalid_unicode():
 for raw in [b'{"schema_version":1,"schema_version":1}',json.dumps({**command(),'actor_id':ORG}).encode(),json.dumps({**command(),'schema_version':True}).encode(),json.dumps({**command(),'schema_version':1.0}).encode()]:
  with pytest.raises(OperationError):parse_command(raw)
def test_array_subset_order_and_raw_text_changes_bind_canonical_bytes():
 c=command();base=canonical_command(parse_command(json.dumps(c).encode()))
 c['payload']['permitted_modes']=['hours'];assert canonical_command(parse_command(json.dumps(c).encode()))!=base
 c=command();c['payload']['name']='Annual e\u0301';a=canonical_command(parse_command(json.dumps(c).encode()));c['payload']['name']='Annual é';assert canonical_command(parse_command(json.dumps(c).encode()))!=a

def test_configuration_strips_python_boundary_whitespace_and_preserves_feff():
 c=command();c['payload']['name']='\u00a0Annual\u00a0';assert parse_command(json.dumps(c).encode()).payload.name=='Annual'
 c['payload']['name']='\ufeffAnnual\ufeff';assert parse_command(json.dumps(c).encode()).payload.name=='\ufeffAnnual\ufeff'
