"""Qualifier safety checks do not substitute for native behavioral evidence."""
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_capabilities as qualification

@pytest.mark.parametrize('url',[
 'postgresql://postgres@127.0.0.1:55582/acb_88a737ddad7b_12345678',
 'postgresql://access_runtime@127.0.0.1:55482/acb_88a737ddad7b_12345678',
 'postgresql://access_runtime@127.0.0.1:55582/postgres',
 'postgresql://access_runtime@localhost:55582/acb_88a737ddad7b_12345678',
 'postgresql://access_runtime@127.0.0.1:55582/acb_88a737ddad7b_12345678?options=-csearch_path%3Dpublic',
])
def test_database_target_and_restricted_role_fail_closed(url):
    with pytest.raises(ValueError,match='fixture_database_binding_invalid'):
        qualification.database_url(url,'acb_88a737ddad7b_12345678')


def test_fixture_requires_private_regular_file_and_closed_json(tmp_path):
    path=tmp_path/'fixture.json';path.write_text('{}');path.chmod(0o644)
    with pytest.raises(ValueError,match='fixture_private_file_required'):qualification.private_json(path)
    path.chmod(0o600);path.write_text('{"schema_version":1,"schema_version":1}')
    with pytest.raises(ValueError,match='fixture_duplicate_key'):qualification.private_json(path)
    link=tmp_path/'symlink.json';link.symlink_to(path)
    with pytest.raises(ValueError,match='fixture_private_file_required'):qualification.private_json(link)

@pytest.mark.parametrize('url',[
 'https://127.0.0.1:55581','http://example.org:55581','http://127.0.0.1:55481',
 'http://user:password@127.0.0.1:55581','http://127.0.0.1:55581/private',
 'http://127.0.0.1:55581?credentials=secret',
])
def test_provider_binding_cannot_reach_other_targets(url):
    with pytest.raises(ValueError,match='fixture_http_binding_invalid'):qualification.loopback_url(url,55581)


def test_output_and_journal_are_reserved_before_guard(tmp_path,monkeypatch):
    output=tmp_path/'proof.json';observed=[]
    fixture=tmp_path/'fixture.json';fixture.write_text('{}');fixture.chmod(0o600)
    def refuse():
        observed.append(True)
        assert output.read_text()=='{"status":"incomplete"}\n'
        assert output.with_suffix('.journal.jsonl').read_text()=='{"state":"reserved"}\n'
        raise ValueError('native_target_invalid')
    monkeypatch.setattr(qualification,'guard',refuse)
    monkeypatch.setattr(sys,'argv',['qualify_capabilities','--fixture',str(fixture),'--output',str(output)])
    with pytest.raises(ValueError,match='native_target_invalid'):qualification.main()
    assert observed and output.stat().st_mode & 0o777==0o600
    with pytest.raises(FileExistsError):qualification.main()
    assert len(observed)==1


def test_existing_journal_refuses_before_guard(tmp_path,monkeypatch):
    output=tmp_path/'proof.json';output.with_suffix('.journal.jsonl').write_text('retained')
    def unexpected():raise AssertionError('guard_must_not_run')
    monkeypatch.setattr(qualification,'guard',unexpected)
    monkeypatch.setattr(sys,'argv',['qualify_capabilities','--fixture','unused','--output',str(output)])
    with pytest.raises(FileExistsError):qualification.main()
    assert output.with_suffix('.journal.jsonl').read_text()=='retained'

ACCOUNT='11111111-1111-4111-8111-111111111111'
ACTOR='22222222-2222-4222-8222-222222222222'
ORG='33333333-3333-4333-8333-333333333333'
PERSON='44444444-4444-4444-8444-444444444444'
URL='postgresql://access_runtime@127.0.0.1:55582/acb_88a737ddad7b_12345678'


def http_case(kind='account'):
    request={'caller':'pts','token':'user','path':'/v2/check','body':{'permission':'pts.poetry.read','authorization_scope':{'kind':'account'}}}
    fields={'account_id':ACCOUNT,'actor_id':ACTOR,'permission':'pts.poetry.read','authorization_scope':{'kind':'account'}}
    if kind in ('own','organization'):
        request.update(caller='leave' if kind=='own' else 'reference')
        request['body']={'permission':'leave.request.own.read' if kind=='own' else 'reference.record.read','authorization_scope':{'kind':'organization','org_id':ORG}}
        fields.update(permission=request['body']['permission'],authorization_scope=request['body']['authorization_scope'],membership_id='19',resource_scope={'kind':'own','person_id':PERSON} if kind=='own' else {'kind':'organization','org_id':ORG})
        if kind=='own':fields['person_id']=PERSON
    if kind=='context':
        request={'caller':'people','token':'user','path':'/v2/identity/organization-context','body':{'org_id':ORG}}
        fields={'account_id':ACCOUNT,'actor_id':ACTOR,'org_id':ORG,'membership_id':'19','person_id':None}
    return {'request':request,'expected':{'status':200,'fields':fields}}


def success(case):
    return {**case['expected']['fields'],'checked_at':'2026-10-27T12:00:00Z',('observation_id' if case['request']['path'].endswith('organization-context') else 'decision_id'):ACTOR}


def response(value,status=200):
    import httpx
    return httpx.Response(status,json=value,headers={'cache-control':'private, no-store'})


def test_complete_response_oracles_accept_all_variants():
    for kind in ('account','own','organization','context'):
        case=http_case(kind)
        qualification.validate_http_case(case,{'tokens':{'user':'synthetic'},'service_keys':{case['request']['caller']:'synthetic'}})
        qualification.validate_response(response(success(case)),case)

@pytest.mark.parametrize('kind',['account','own','organization','context'])
def test_success_requires_all_independent_expected_binding_fields(kind):
    case=http_case(kind)
    fixture={'tokens':{'user':'synthetic'},'service_keys':{case['request']['caller']:'synthetic'}}
    for key in list(case['expected']['fields']):
        altered=json.loads(json.dumps(case));del altered['expected']['fields'][key]
        with pytest.raises(ValueError,match='fixture_binding_oracle_required'):qualification.validate_http_case(altered,fixture)

@pytest.mark.parametrize('field,value',[
 ('account_id',ACTOR),('actor_id',ACCOUNT),('membership_id','20'),('person_id',ACTOR),
 ('resource_scope',{'kind':'own','person_id':ACTOR}),
 ('checked_at','2026-10-27T12:00:00+02:00'),('checked_at','2026-02-30T12:00:00Z'),
 ('membership_id','9223372036854775808'),('membership_id',19),('actor_id','invalid'),('extra',True),
])
def test_org_response_rejects_malformed_foreign_or_wrong_expected_values(field,value):
    case=http_case('own');actual=success(case);actual[field]=value
    with pytest.raises(ValueError):qualification.validate_response(response(actual),case)

@pytest.mark.parametrize('field,value',[('account_id',ACTOR),('actor_id',ACCOUNT),('org_id',ACTOR),('person_id',PERSON),('membership_id','20')])
def test_people_response_rejects_independently_wrong_context(field,value):
    case=http_case('context');actual=success(case);actual[field]=value
    with pytest.raises(ValueError):qualification.validate_response(response(actual),case)


def test_non_success_requires_explicit_error_id_and_exact_error_shape():
    case=http_case();case['expected']={'status':403}
    fixture={'tokens':{'user':'synthetic'},'service_keys':{'pts':'synthetic'}}
    with pytest.raises(ValueError,match='fixture_error_oracle_required'):qualification.validate_http_case(case,fixture)
    case['expected']['error_id']='access_denied'
    for invalid in ({'error_id':'authorization_unavailable','error':'safe','details':{}},{'error_id':'access_denied','error':'safe','details':{'person_id':PERSON}},{'error_id':'access_denied'}):
        with pytest.raises(ValueError,match='http_error_mismatch'):qualification.validate_response(response(invalid,403),case)
    case['expected']={'status':403,'error_id':'service_access_denied','error_envelope':'legacy'}
    qualification.validate_response(response({'detail':{'code':'service_access_denied'}},403),case)


def process_fixture(tmp_path):
    fixture={'api_process_id':1234,'api_url':'http://127.0.0.1:55589','provider_url':'http://127.0.0.1:55581','runtime_database_url':URL,'service_keys':{'pts':'synthetic-pts'}}
    process=tmp_path/'1234';process.mkdir();(process/'fd').mkdir();(process/'net').mkdir()
    (process/'cwd').symlink_to(qualification.OWNER,target_is_directory=True)
    (process/'cmdline').write_bytes(b'\0'.join(value.encode() for value in ['/synthetic/python','-B','-m','uvicorn','main:app','--host','127.0.0.1','--port','55589'])+b'\0')
    environment={'CAPABILITY_ACCESS_DATABASE_URL':URL,'SUPABASE_URL':fixture['provider_url'],'PTS_SERVICE_KEY':'synthetic-pts'}
    (process/'environ').write_bytes(b'\0'.join((key+'='+value).encode() for key,value in environment.items())+b'\0')
    (process/'stat').write_text('1234 (python) '+' '.join(['S']+['0']*18+['123456'])+'\n')
    (process/'fd/9').symlink_to('socket:[98765]')
    (process/'net/tcp').write_text('header\n0: 0100007F:D925 00000000:0000 0A 0:0 0:0 0 0 0 98765\n')
    return fixture,process


def test_process_requires_actual_owner_provider_database_credentials_and_socket(tmp_path):
    fixture,process=process_fixture(tmp_path)
    qualification.process_binding(fixture,tmp_path)
    assert int('D925',16)==55589

@pytest.mark.parametrize('change',['cwd','command','database','provider','keys','socket','pid'])
def test_process_binding_rejects_unrelated_api_without_disclosing_env(tmp_path,change):
    fixture,process=process_fixture(tmp_path)
    if change=='cwd':(process/'cwd').unlink();(process/'cwd').symlink_to(tmp_path,target_is_directory=True)
    elif change=='command':(process/'cmdline').write_bytes(b'python\0-c\0secret=payload\0')
    elif change=='socket':(process/'fd/9').unlink();(process/'fd/9').symlink_to('socket:[12345]')
    elif change=='pid':fixture['api_process_id']=True
    else:
        raw=(process/'environ').read_bytes()
        replacements={'database':(b'acb_88a737ddad7b_12345678',b'postgres'),'provider':(b'55581',b'55481'),'keys':(b'synthetic-pts',b'secret-other-key')}
        old,new=replacements[change];(process/'environ').write_bytes(raw.replace(old,new))
    with pytest.raises(ValueError) as error:qualification.process_binding(fixture,tmp_path)
    assert 'secret' not in str(error.value)


def test_manifest_captures_all_packaged_runtime_sources():
    manifest=qualification.source_manifest()
    required=('studies_identity.py','studies_contract.py','studies_access.py','studies_readiness.py','identity_preferences.py')
    assert all('services/access/'+name in manifest for name in required)

@pytest.mark.parametrize('changed',['fixture','sources'])
def test_fixture_and_runtime_changes_leave_incomplete_reserved_evidence(tmp_path,monkeypatch,changed):
    path=tmp_path/'fixture.json';path.write_text('{ "private": true }\n');path.chmod(0o600)
    output=tmp_path/'proof.json'
    monkeypatch.setattr(qualification,'guard',lambda:({},tmp_path))
    monkeypatch.setattr(qualification,'load',lambda document,*_:document)
    calls=[]
    def manifest():calls.append(True);return {'runtime.py':'before' if len(calls)==1 or changed=='fixture' else 'after'}
    monkeypatch.setattr(qualification,'source_manifest',manifest)
    class Proof:
        def __init__(self,*args):pass
        def run(self):
            assert calls==[True]
            if changed=='fixture':path.write_text('{}')
            return []
    monkeypatch.setattr(qualification,'Qualification',Proof)
    monkeypatch.setattr(sys,'argv',['qualify','--fixture',str(path),'--output',str(output)])
    with pytest.raises(ValueError,match='fixture_changed' if changed=='fixture' else 'runtime_source_changed'):qualification.main()
    assert json.loads(output.read_bytes())=={'status':'incomplete'}


def test_snapshot_hashes_the_same_secure_bytes_it_parses(tmp_path,monkeypatch):
    raw=b'{ "private": true }\n';fixture=tmp_path/'fixture.json';fixture.write_bytes(raw);fixture.chmod(0o600)
    output=tmp_path/'proof.json'
    monkeypatch.setattr(qualification,'guard',lambda:({},tmp_path))
    monkeypatch.setattr(qualification,'load',lambda document,*_:document)
    monkeypatch.setattr(qualification,'source_manifest',lambda:{'runtime.py':'stable'})
    monkeypatch.setattr(qualification,'process_binding',lambda *_:None)
    class Proof:
        def __init__(self,document,*args):assert document=={'private':True}
        def run(self):return ['explicit-oracle']
    monkeypatch.setattr(qualification,'Qualification',Proof)
    monkeypatch.setattr(sys,'argv',['qualify','--fixture',str(fixture),'--output',str(output)])
    qualification.main()
    assert json.loads(output.read_bytes())['fixture_sha256']==qualification.sha256(raw).hexdigest()


def test_concurrent_sql_and_http_launch_together_after_nested_journal(tmp_path,monkeypatch):
    import io,threading
    http=http_case();sql={'sql':{'database_url':URL,'statement':'SELECT 1','expected_rows':[[1]]}}
    fixture={'database':'acb_88a737ddad7b_12345678','runtime_database_url':URL,'steps':[{'name':'ordered','coverage':[],'concurrent':[http,sql]}]}
    journal_path=tmp_path/'journal';journal=journal_path.open('w+')
    proof=qualification.Qualification(fixture,journal);arrived=threading.Barrier(2);seen=[]
    def worker(kind):
        text=journal_path.read_text()
        assert '"case": 0' in text and '"case": 1' in text
        arrived.wait(timeout=2);seen.append(kind)
    def sql_case(case):
        if case.get('statement')=='SELECT current_user,current_database()':return
        worker('sql')
    monkeypatch.setattr(proof,'sql',sql_case);monkeypatch.setattr(proof,'request',lambda _:worker('http'))
    try:assert proof.run()==['ordered']
    finally:journal.close()
    assert sorted(seen)==['http','sql']

@pytest.mark.parametrize('invalid',['url','oracle'])
def test_nested_concurrent_sql_is_validated_before_any_execution(invalid):
    sql={'database_url':URL,'statement':'SELECT 1','expected_rows':[[1]]}
    if invalid=='url':sql['database_url']='postgresql://postgres@127.0.0.1:55582/postgres'
    else:del sql['expected_rows']
    fixture={'database':'acb_88a737ddad7b_12345678','tokens':{'user':'synthetic'},'service_keys':{'pts':'synthetic'}}
    with pytest.raises(ValueError):qualification.validate_case({'concurrent':[http_case(),{'sql':sql}]},fixture)
