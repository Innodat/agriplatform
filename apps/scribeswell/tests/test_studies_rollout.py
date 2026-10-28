"""Offline candidate boundaries and fail-closed execution evidence; no target access."""
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'deployment'))
import studies_rollout as rollout

A='10000000-0000-4000-8000-000000000001'

def put(path,value):
    path=Path(path)
    path.write_text(value if isinstance(value,str) else json.dumps(value))
    return str(path)

@pytest.fixture
def target(tmp_path,monkeypatch):
    gateway=tmp_path/'retained-apisix.yaml'
    route={'id':'scribeswell','host':'api.example.invalid','uris':['/scribeswell/api/bible/*'],'methods':['GET','OPTIONS'],
        'vars':[['scheme','==','https']],'plugins':{'proxy-rewrite':{'regex_uri':['^/scribeswell/(.*)','/$1']},'cors':{'allow_origins':'https://example.invalid','allow_methods':'GET,OPTIONS'}},
        'upstream':{'nodes':{'scribeswell:8000':1}}}
    put(gateway,{'routes':[route,{'id':'unrelated','host':'unrelated.invalid'}],'ssls':[{'id':'retained','cert':'synthetic certificate','key':'synthetic private key'}]})
    compose={'name':'retained-production','services':{
        'scribeswell':{'image':'old-api','env_file':['/private/deployed/scribeswell.env'],'read_only':True},
        'access':{'image':'old-access','env_file':['/private/deployed/access.env'],'read_only':True},
        'gateway':{'image':'existing-gateway','volumes':[str(gateway)+':/usr/local/apisix/conf/apisix.yaml:ro'],'ports':['443:9443']},
        'leave':{'image':'retain-leave','environment':{'UNCHANGED':'true'}}},'networks':{'default':{'enable_ipv6':True}}}
    env={'SCRIBESWELL_STUDIES_DATABASE_URL':'postgresql://scribeswell_studies_runtime:synthetic@db.fixture.supabase.co/postgres?sslmode=require',
        'SCRIBESWELL_STUDIES_ACCESS_URL':'http://access:8000','SCRIBESWELL_STUDIES_SERVICE_KEY':'synthetic-private-key',
        'SCRIBESWELL_SERVICE_KEY':'synthetic-private-key',
        'STUDIES_ACCESS_DATABASE_URL':'postgresql://access_studies_runtime:synthetic@db.fixture.supabase.co/postgres?sslmode=require',
        'STUDIES_IDENTITY_DATABASE_URL':'postgresql://identity_studies_reader_runtime:synthetic@db.fixture.supabase.co/postgres?sslmode=require',
        'STUDIES_IDENTITY_SETUP_DATABASE_URL':'postgresql://identity_studies_setup_runtime:synthetic@db.fixture.supabase.co/postgres?sslmode=require'}
    values={'schema_version':1,'release_id':'bounded-fixture','source_revision':'a'*40,'account_id':A,
        'observed_at':datetime.now(timezone.utc).isoformat(),'site_origin':'https://example.invalid','api_origin':'https://api.example.invalid',
        'retained_compose':put(tmp_path/'retained-compose.json',compose),'retained_gateway':str(gateway),
        'retained_api_env':put(tmp_path/'retained-api.env','APP_ENV=production\nSUPABASE_URL=https://fixture.supabase.co\nCORS_ORIGINS=["https://example.invalid"]\nSCRIBESWELL_DATABASE_URL=postgresql://scribeswell_runtime:synthetic@db.fixture.supabase.co/postgres?sslmode=require\nRETAINED=value\n'),
        'retained_access_env':put(tmp_path/'retained-access.env','SUPABASE_URL=https://fixture.supabase.co\nOTHER_CONSUMER=retained\n'),
        'retained_frontend_env':put(tmp_path/'retained-frontend.env','VITE_APP_BASE=/scribeswell/\nVITE_BIBLE_API_URL=https://api.example.invalid/scribeswell/api/bible\nVITE_API_BASE_URL=http://dev-only.invalid\nVITE_SUPABASE_URL=https://fixture.supabase.co\n'),
        'private_env':put(tmp_path/'private.env',rollout.env_text(env)),
        'api_image':'api.example/image@sha256:'+'b'*64,'migration_image':'migration.example/image@sha256:'+'c'*64,
        'access_image':'access.example/image@sha256:'+'d'*64,'migration_network':'retained-production_default','migration_profile':{'profile':'dormant','custody':None}}
    current={'synthetic-api-source':'e'*64}
    proof={'schema_version':1,'source_revision':values['source_revision'],'images':{key:values[key+'_image'] for key in ('api','migration','access')},
        'sources':current,'proofs':{put(tmp_path/'actual-image-inspection.json',{'image_id':'synthetic-local-image'}):None}}
    proof['proofs']={path:rollout.digest(path) for path in proof['proofs']}
    proof['inspections']={}
    frozen=rollout.owner_module()
    for name in ('api','migration','access'):
        path=put(tmp_path/(name+'-inspection.json'),{'reference':values[name+'_image'],'image_id':rollout.FROZEN_ACCESS_IMAGE_ID if name=='access' else 'sha256:'+'f'*64,
            'repo_digests':[values[name+'_image']],'packaged_sources':frozen.runtime_hashes() if name=='access' else current})
        proof['inspections'][name]=path;proof['proofs'][path]=rollout.digest(path)
    values['image_proof']=put(tmp_path/'image-proof.json',proof)
    monkeypatch.setattr(rollout,'sources',lambda:current)
    monkeypatch.setattr(rollout,'package_sources',lambda name:current)
    # Real archived validator remains used in gate; unit fixture isolates target I/O.
    module=rollout.owner_module()
    monkeypatch.setattr(module,'validate_qualification',lambda *args:None)
    monkeypatch.setattr(rollout,'owner_module',lambda:module)
    return values,tmp_path/'candidate',compose,route,module

def test_candidate_preserves_unselected_services_public_tls_and_frontend_base(target):
    inputs,out,previous,route,_=target
    retained={key:Path(value).read_bytes() for key,value in inputs.items() if key.startswith('retained_')}
    plan=rollout.prepare(inputs,out)
    candidate=rollout.document(out/'compose.json')
    assert candidate['services']['leave']==previous['services']['leave']
    assert candidate['networks']==previous['networks'] and candidate['name']==previous['name']
    assert candidate['services']['gateway']['image']=='existing-gateway'
    gateway=rollout.strict((out/'apisix.yaml').read_text().removesuffix('#END\n'))
    assert gateway['routes'][0]==route and gateway['ssls']==rollout.document(inputs['retained_gateway'])['ssls']
    assert gateway['routes'][-1]['methods']==['GET','POST','PUT','DELETE','OPTIONS']
    assert gateway['routes'][-1]['vars']==[['scheme','==','https']]
    assert gateway['routes'][-1]['uris']==['/scribeswell/api/studies','/scribeswell/api/studies/*','/scribeswell/api/operations/*']
    assert gateway['routes'][-1]['upstream']==route['upstream']
    assert gateway['routes'][-1]['plugins']['proxy-rewrite']==route['plugins']['proxy-rewrite']
    env=rollout.environment((out/'frontend.env').read_text())
    assert env['VITE_API_BASE_URL']=='http://dev-only.invalid'
    assert env['VITE_BIBLE_API_URL']=='https://api.example.invalid/scribeswell/api/bible'
    assert env['VITE_APP_BASE']=='/scribeswell/' and env['VITE_STUDIES_PREGRANTED']=='true'
    assert env['VITE_STUDIES_API_URL']=='https://api.example.invalid/scribeswell'
    assert not (out/'access.env').exists() and plan['activation_authorized'] is False
    assert all(Path(inputs[key]).read_bytes()==raw for key,raw in retained.items())
    assert all(path.stat().st_mode&0o777==0o600 for path in out.iterdir())
    with pytest.raises(FileExistsError):rollout.prepare(inputs,out)

@pytest.mark.parametrize('change',[
    {'unexpected':True},{'schema_version':True},{'account_id':A+','+A},{'account_id':'00000000-0000-0000-0000-000000000000'},
    {'api_image':'mutable:latest'},{'migration_network':'network;touch unsafe'},
    {'api_origin':'http://api.invalid'},{'site_origin':'https://example.invalid/path'},
    {'observed_at':'2020-01-01T00:00:00Z'}, {'source_revision':'branch-name'},
])
def test_unsafe_or_stale_inputs_refuse_without_candidate(target,change):
    inputs,out,*_=target
    with pytest.raises((ValueError,TypeError)):rollout.prepare(inputs|change,out)
    assert not out.exists()

def test_duplicate_json_oversize_and_secret_error_are_bounded(tmp_path,capsys,monkeypatch):
    for raw in ('{"a":1,"a":2}','NaN','[NaN]', 'x'*(rollout.MAX_DOCUMENT+1)):
        with pytest.raises(rollout.Refused):rollout.strict(raw)
    secret=tmp_path/'secret-input.json';secret.write_text('{"secret":"private-marker"}')
    monkeypatch.setattr(sys,'argv',['rollout','prepare','--inputs',str(secret),'--output',str(tmp_path/'candidate')])
    assert rollout.main()==1
    captured=capsys.readouterr()
    assert captured.err=='studies_rollout_refused\n' and 'private-marker' not in captured.out+captured.err


def test_absent_inventory_explicitly_blocks_without_files(tmp_path,monkeypatch,capsys):
    out=tmp_path/'candidate'
    monkeypatch.setattr(sys,'argv',['rollout','prepare','--output',str(out)])
    assert rollout.main()==2
    assert json.loads(capsys.readouterr().out)['status']=='blocked' and not out.exists()

@pytest.mark.parametrize('tamper',['source','image-proof','retained','candidate'])
def test_candidate_source_image_and_retained_input_changes_block_execution(target,tamper,monkeypatch):
    inputs,out,*_=target;rollout.prepare(inputs,out)
    if tamper=='source':monkeypatch.setattr(rollout,'sources',lambda:{'changed':'f'*64})
    elif tamper=='image-proof':Path(inputs['image_proof']).write_text('{}')
    elif tamper=='retained':Path(inputs['retained_api_env']).write_text('changed')
    else:(out/'scribeswell.env').write_text('changed')
    with pytest.raises(ValueError):rollout.checked_candidate(out)


def bound_migration(out,plan,*,status='succeeded',private=None):
    folder=out/'migration';folder.mkdir()
    put(out/'migration-input.env','synthetic-private-migration-input')
    public={'complete':True,'owners':{'scribeswell':{'status':'succeeded','before':None,'after':'scribeswell_0003','requested_validation':{'profile':'dormant','custody_sha256':None},'validation':{'profile':'dormant','custody_sha256':None}}}}
    private=private or {'complete':True,'owner':'scribeswell_studies','before':None,'after':'scribeswell_studies_0009','recovery':'forward-only'}
    put(folder/'migrations.json',public);put(folder/'studies-migrations.json',private)
    receipt={'status':status,'release_id':plan['release_id'],'candidate_sha256':rollout.digest(out/'candidate.json'),'image':plan['images']['migration'],
        'migration_env_sha256':rollout.digest(out/'migration-input.env'),'finished_at':datetime.now(timezone.utc).isoformat(),'report_sha256':rollout.digest(folder/'migrations.json'),'private_sha256':rollout.digest(folder/'studies-migrations.json')}
    put(folder/'execution.json',receipt)
    return receipt


def test_gate_calls_actual_owner_preparation_with_current_release_and_never_activates(target):
    inputs,out,_,_,owner=target
    plan=rollout.prepare(inputs,out);bound_migration(out,plan)
    calls=[]
    def preparation(identity,access,qualification,release):
        calls.append((identity,access,qualification,release))
        return {'schema_version':2,'release_id':release,'identity_revision':'identity_0026','access_revision':'access_0019',
            'service_actor_id':A,'runtime_sources':owner.runtime_hashes(),'qualification_sha256':rollout.digest(rollout.QUALIFICATION),
            'profile_hook_qualified':True,'live_provider_qualified':True}
    result=rollout.gate(out,environ={'IDENTITY_MIGRATION_DATABASE_URL':'postgresql://identity_migrator:synthetic@db.fixture.supabase.co/postgres?sslmode=require','ACCESS_MIGRATION_DATABASE_URL':'postgresql://access_migrator:synthetic@db.fixture.supabase.co/postgres?sslmode=require'},prepare_owner=preparation)
    assert calls==[('postgresql://identity_migrator:synthetic@db.fixture.supabase.co/postgres?sslmode=require','postgresql://access_migrator:synthetic@db.fixture.supabase.co/postgres?sslmode=require',rollout.QUALIFICATION,inputs['release_id'])]
    assert result['activation_authorized'] is False and (out/'access.env').exists()
    artifact=rollout.document(out/'studies-readiness.json')
    assert json.loads(rollout.environment((out/'access.env').read_text())['STUDIES_READINESS_JSON'])==artifact

@pytest.mark.parametrize('failure',['missing','failed','unknown','wrong-head','old','wrong-image','wrong-release','changed-report'])
def test_bad_migration_blocks_before_owner_preparation(target,failure):
    inputs,out,*_=target;plan=rollout.prepare(inputs,out)
    if failure!='missing':
        receipt=bound_migration(out,plan,status=failure if failure in ('failed','unknown') else 'succeeded',
            private={'complete':True,'owner':'scribeswell_studies','before':None,'after':'scribeswell_studies_0001','recovery':'forward-only'} if failure=='wrong-head' else None)
        if failure=='old':receipt['finished_at']='2020-01-01T00:00:00Z'
        if failure=='wrong-image':receipt['image']='other-image'
        if failure=='wrong-release':receipt['release_id']='other-release'
        if failure=='changed-report':(out/'migration/studies-migrations.json').write_text('{}')
        if failure in ('old','wrong-image','wrong-release'):put(out/'migration/execution.json',receipt)
    with pytest.raises((ValueError,FileNotFoundError)):rollout.gate(out,prepare_owner=lambda *args:pytest.fail('must not call owner'))
    assert not (out/'access.env').exists() and not (out/'gate.json').exists()


def test_missing_or_stale_live_readiness_never_creates_activation_env(target):
    inputs,out,*_=target;plan=rollout.prepare(inputs,out);bound_migration(out,plan)
    def stale(*args):raise ValueError('owner refuses current actual database')
    with pytest.raises(ValueError):rollout.gate(out,environ={'IDENTITY_MIGRATION_DATABASE_URL':'synthetic','ACCESS_MIGRATION_DATABASE_URL':'synthetic'},prepare_owner=stale)
    assert not (out/'access.env').exists()

@pytest.mark.parametrize('kind',['private-project','owner-project','frontend-project','public-profile','image-inspection'])
def test_selected_target_project_profile_and_exact_image_bytes_are_required(target,kind):
    inputs,out,*_=target
    if kind=='private-project':
        path=Path(inputs['private_env']);path.write_text(path.read_text().replace('db.fixture.supabase.co','db.other.supabase.co',1))
    elif kind=='owner-project':
        path=Path(inputs['retained_access_env']);path.write_text(path.read_text().replace('fixture.supabase.co','other.supabase.co'))
    elif kind=='frontend-project':
        path=Path(inputs['retained_frontend_env']);path.write_text(path.read_text().replace('fixture.supabase.co','other.supabase.co'))
    elif kind=='public-profile':inputs['migration_profile']={'profile':'invented','custody':None}
    else:
        proof=rollout.document(inputs['image_proof']);path=Path(proof['inspections']['api']);row=rollout.document(path)
        row['packaged_sources']={'changed':'f'*64};put(path,row);proof['proofs'][str(path)]=rollout.digest(path);put(inputs['image_proof'],proof)
    with pytest.raises(ValueError):rollout.prepare(inputs,out)
    assert not out.exists()


def test_gate_rejects_live_preparation_against_another_project_before_owner_calls(target):
    inputs,out,*_=target;plan=rollout.prepare(inputs,out);bound_migration(out,plan)
    with pytest.raises(ValueError):rollout.gate(out,environ={
        'IDENTITY_MIGRATION_DATABASE_URL':'postgresql://identity_migrator:synthetic@db.other.supabase.co/postgres?sslmode=require',
        'ACCESS_MIGRATION_DATABASE_URL':'postgresql://access_migrator:synthetic@db.fixture.supabase.co/postgres?sslmode=require'},
        prepare_owner=lambda *args:pytest.fail('wrong project must not call owner'))

@pytest.mark.parametrize('outcome',['succeeded','failed','unknown','wrong-head'])
def test_app_only_migration_supervision_binds_result_and_retains_failure(target,monkeypatch,outcome):
    inputs,out,*_=target;plan=rollout.prepare(inputs,out)
    env=put(out.parent/'migration.env','SUPABASE_URL=https://fixture.supabase.co\nSCRIBESWELL_MIGRATION_DATABASE_URL=postgresql://scribeswell_migrator:synthetic@db.fixture.supabase.co/postgres?sslmode=require\nSCRIBESWELL_STUDIES_MIGRATION_ENABLED=true\nSCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL=postgresql://scribeswell_studies_migrator:synthetic@db.fixture.supabase.co/postgres?sslmode=require\n')
    monkeypatch.setattr(rollout.os,'chown',lambda *args:None)
    calls=[]
    def execute(command,**kwargs):
        calls.append(command)
        assert 'synthetic' not in str(command)
        if command[1]=='stop':return SimpleNamespace(returncode=0)
        assert command[command.index('--user')+1]=='10001:10001' and command[-1]==inputs['migration_image']
        assert '--read-only' in command and '--cap-drop' in command and command[command.index('--network')+1]==inputs['migration_network']
        if outcome=='unknown':raise subprocess.TimeoutExpired('synthetic migration',190)
        if outcome=='failed':return SimpleNamespace(returncode=1)
        folder=out/'migration'
        put(folder/'migrations.json',{'complete':True,'owners':{'scribeswell':{'status':'succeeded','before':None,'after':'scribeswell_0003','requested_validation':{'profile':'dormant','custody_sha256':None},'validation':{'profile':'dormant','custody_sha256':None}}}})
        put(folder/'studies-migrations.json',{'complete':True,'owner':'scribeswell_studies','before':None,'after':'scribeswell_studies_0001' if outcome=='wrong-head' else 'scribeswell_studies_0009','recovery':'forward-only'})
        return SimpleNamespace(returncode=0)
    if outcome=='succeeded':assert rollout.migrate(out,env,run=execute)['status']=='succeeded'
    else:
        with pytest.raises(ValueError):rollout.migrate(out,env,run=execute)
    receipt=rollout.document(out/'migration/execution.json')
    assert receipt['status']==('succeeded' if outcome=='succeeded' else 'unknown' if outcome=='unknown' else 'failed')
    assert receipt['candidate_sha256']==rollout.digest(out/'candidate.json')
    assert receipt['migration_env_sha256']==rollout.digest(out/'migration-input.env')
    assert not (out/'access.env').exists()
    if outcome=='unknown':assert calls[-1][1]=='stop'


def test_image_copy_paths_follow_actual_docker_destinations():
    paths=rollout.package_paths('migration')
    assert paths['apps/scribeswell/deployment/migration-requirements.txt']==['/tmp/migration-requirements.txt']
    assert paths['apps/scribeswell/backend/database.py']==['/workspace/apps/scribeswell/backend/database.py']
    assert rollout.package_paths('api')['apps/scribeswell/backend/requirements.txt']==['/tmp/requirements.txt','/app/apps/scribeswell/backend/requirements.txt']


def test_local_image_inspection_binds_digest_and_actual_packaged_bytes(target,monkeypatch):
    inputs,out,_,_,owner=target
    monkeypatch.setattr(rollout,'package_paths',lambda name:{'synthetic-api-source':['/tmp/copied-input']})
    calls=[]
    def execute(command,**kwargs):
        calls.append(command)
        if command[1:3]==['image','inspect']:
            return SimpleNamespace(stdout=json.dumps([{'Id':rollout.FROZEN_ACCESS_IMAGE_ID if command[-1]==inputs['access_image'] else 'sha256:'+'f'*64,'RepoDigests':[command[-1]]}]))
        assert command[1]=='run' and command[command.index('--network')+1]=='none'
        assert '--read-only' in command and '--rm' in command
        sources=owner.runtime_hashes() if command[command.index('--entrypoint')+1].endswith('python3.15') else {'synthetic-api-source':'e'*64}
        return SimpleNamespace(stdout=json.dumps(sources))
    output=out.parent/'inspections'
    assert rollout.inspect_images(inputs,output,run=execute)['status']=='local-image-bytes-inspected'
    proof=rollout.document(output/'image-proof.json')
    assert len(calls)==6 and set(proof['inspections'])=={'api','migration','access'}
    rollout.validate_image_proof(proof,inputs,{'synthetic-api-source':'e'*64})


def test_local_image_without_published_digest_refuses_probe(target):
    inputs,out,*_=target
    def execute(*args,**kwargs):return SimpleNamespace(stdout=json.dumps([{'Id':'sha256:'+'f'*64,'RepoDigests':[]}]))
    with pytest.raises(ValueError,match='immutable_image_missing'):rollout.inspect_images(inputs,out.parent/'inspections',run=execute)


def test_migration_probe_includes_generated_helper_and_manifest_with_restricted_default_user():
    inputs=rollout.package_paths('migration')
    assert inputs['apps/scribeswell/studies-database-tools/owned_migration.py']==['/workspace/apps/scribeswell/studies-database-tools/owned_migration.py']
    assert inputs['apps/scribeswell/studies-database-tools/.generated-files.json']==['/workspace/apps/scribeswell/studies-database-tools/.generated-files.json']


def test_runtime_configuration_cannot_retain_migration_authority(target):
    inputs,out,*_=target
    path=Path(inputs['retained_api_env']);path.write_text(path.read_text()+'SCRIBESWELL_MIGRATION_DATABASE_URL=synthetic-private-migrator\n')
    with pytest.raises(ValueError,match='runtime_migration_authority'):rollout.prepare(inputs,out)
    assert not out.exists()


@pytest.mark.parametrize('service',['scribeswell','access'])
@pytest.mark.parametrize('inline',[
    {'SCRIBESWELL_STUDIES_ACCOUNT_ID':'10000000-0000-4000-8000-000000000002'},
    ['STUDIES_READINESS_JSON=forged','SCRIBESWELL_DATABASE_URL=unrestricted'],
])
def test_compose_inline_selected_environment_refuses_before_output(target,service,inline):
    inputs,out,compose,*_=target
    compose['services'][service]['environment']=inline
    put(inputs['retained_compose'],compose)
    with pytest.raises(ValueError):rollout.prepare(inputs,out)
    assert not out.exists()


@pytest.mark.parametrize('kind',[
    'relative-env','relative-long-env','relative-bind','relative-long-bind',
    'relative-config','relative-secret','indirect-config','indirect-secret',
    'include','extends','interpolated-path',
])
def test_compose_relocation_unsafe_topology_refuses_before_output(target,kind):
    inputs,out,compose,*_=target
    service=compose['services']['leave']
    if kind=='relative-env':service['env_file']=['./leave.env']
    elif kind=='relative-long-env':service['env_file']=[{'path':'../secrets/leave.env','format':'raw'}]
    elif kind=='relative-bind':service['volumes']=['./saved:/data:ro']
    elif kind=='relative-long-bind':service['volumes']=[{'type':'bind','source':'../saved','target':'/data','read_only':True}]
    elif kind=='relative-config':compose['configs']={'settings':{'file':'./settings.json'}};service['configs']=['settings']
    elif kind=='relative-secret':compose['secrets']={'password':{'file':'../password'}};service['secrets']=['password']
    elif kind=='indirect-config':compose['configs']={'settings':{'environment':'SETTINGS_JSON'}};service['configs']=['settings']
    elif kind=='indirect-secret':compose['secrets']={'password':{'environment':'SECRET_PASSWORD'}};service['secrets']=['password']
    elif kind=='include':compose['include']=['/private/deployed/other-compose.json']
    elif kind=='extends':service['extends']={'file':'/private/deployed/other-compose.json','service':'leave'}
    else:service['env_file']=['${PRIVATE_DIR}/leave.env']
    put(inputs['retained_compose'],compose)
    with pytest.raises(ValueError):rollout.prepare(inputs,out)
    assert not out.exists()


@pytest.mark.parametrize('kind',['missing-name','invalid-name','wrong-network','missing-external-name','selected-other-network'])
def test_compose_explicit_project_and_matching_network_are_required(target,kind):
    inputs,out,compose,*_=target
    if kind=='missing-name':compose.pop('name')
    elif kind=='invalid-name':compose['name']='${OTHER_PROJECT}'
    elif kind=='wrong-network':inputs['migration_network']='another-project_default'
    elif kind=='missing-external-name':compose['networks']['default']['external']=True
    else:compose['services']['access']['networks']=['other']
    put(inputs['retained_compose'],compose)
    with pytest.raises(ValueError):rollout.prepare(inputs,out)
    assert not out.exists()


@pytest.mark.parametrize('long_mount',[False,True])
def test_compose_absolute_topology_and_original_gateway_mount_are_preserved(target,long_mount):
    inputs,out,compose,*_=target
    original='/private/deployed/gateway/apisix.yaml'
    assert original!=inputs['retained_gateway']
    mount={'type':'bind','source':original,'target':'/usr/local/apisix/conf/apisix.yaml','read_only':True} if long_mount else original+':/usr/local/apisix/conf/apisix.yaml:ro'
    compose['services']['gateway']['volumes']=[
        '/private/deployed/gateway/config.yaml:/usr/local/apisix/conf/config.yaml:ro',mount]
    compose['services']['leave'].update(env_file=[{'path':'/private/deployed/leave.env','format':'raw'}],
        volumes=[{'type':'bind','source':'/private/deployed/data','target':'/data','read_only':True}],
        configs=['settings'],secrets=['password'])
    compose['configs']={'settings':{'file':'/private/deployed/settings.json'}}
    compose['secrets']={'password':{'file':'/private/deployed/password'}}
    compose['networks']['default']['name']='retained-explicit-network'
    inputs['migration_network']='retained-explicit-network'
    put(inputs['retained_compose'],compose)
    original_bytes=Path(inputs['retained_compose']).read_bytes()
    rollout.prepare(inputs,out)
    candidate=rollout.document(out/'compose.json')
    assert candidate['name']==compose['name'] and candidate['networks']==compose['networks']
    for field in ('configs','secrets'):assert candidate[field]==compose[field]
    assert candidate['services']['leave']==compose['services']['leave']
    assert candidate['services']['gateway']['volumes'][0]==compose['services']['gateway']['volumes'][0]
    expected=dict(mount,source=str(out/'apisix.yaml')) if long_mount else str(out/'apisix.yaml')+':/usr/local/apisix/conf/apisix.yaml:ro'
    assert candidate['services']['gateway']['volumes'][1]==expected
    assert Path(inputs['retained_compose']).read_bytes()==original_bytes
