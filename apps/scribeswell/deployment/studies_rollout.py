"""App-only bounded rollout preparation. No prepare operation contacts a target.

Execution subcommands are for a separately approved maintenance window. They never
activate containers or reverse a migration. Secrets and raw child output stay private.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit
from uuid import UUID, uuid4

APP=Path(__file__).resolve().parents[1]
ROOT=APP.parents[1]
OWNER=Path('/tmp/studies-current-deb424b')
QUALIFICATION=Path('/tmp/studies-current-native-20261027-review/current/qualification.json')
# Final reviewed API_IMAGE_INTEGRATION_EVIDENCE / 56ec83ff qualified owner image.
# A later registry manifest must resolve to these exact frozen installed bytes.
FROZEN_ACCESS_IMAGE_ID='sha256:792933a8b3678b78657588e230e4f14dbbfe0e44909e616b56e1f9cf25448eba'
sys.path.insert(0,str(APP/'deployment'))
from studies_release_contract import valid_result
sys.path.insert(0,str(APP/'migrations'))
import release_profile
sys.path.insert(0,str(ROOT/'platform/deployment'))
from target_contract import database_url

MAX_DOCUMENT=2*1024*1024
API_PRIVATE={'SCRIBESWELL_STUDIES_DATABASE_URL','SCRIBESWELL_STUDIES_ACCESS_URL','SCRIBESWELL_STUDIES_SERVICE_KEY'}
ACCESS_PRIVATE={'SCRIBESWELL_SERVICE_KEY','STUDIES_ACCESS_DATABASE_URL','STUDIES_IDENTITY_DATABASE_URL','STUDIES_IDENTITY_SETUP_DATABASE_URL'}
INPUT_FIELDS={'schema_version','release_id','source_revision','account_id','observed_at','site_origin','api_origin',
 'retained_compose','retained_gateway','retained_api_env','retained_access_env','retained_frontend_env',
 'private_env','api_image','migration_image','access_image','image_proof','migration_network','migration_profile'}

class Refused(ValueError):
    def __init__(self,code='studies_rollout_input_invalid'):super().__init__(code)

def digest(path):return sha256(Path(path).read_bytes()).hexdigest()

def strict(raw,limit=MAX_DOCUMENT):
    def pairs(items):
        value={}
        for key,item in items:
            if key in value:raise Refused()
            value[key]=item
        return value
    try:
        if len(raw.encode('utf8') if isinstance(raw,str) else raw)>limit:raise Refused()
        return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Refused()))
    except (ValueError,TypeError,UnicodeError):raise Refused() from None

def external(value):
    if not isinstance(value,str):raise Refused()
    path=Path(value)
    if not path.is_absolute() or path.resolve().is_relative_to(ROOT.resolve()) or path!=path.resolve():raise Refused()
    return path

def read(path,limit=MAX_DOCUMENT):
    path=external(str(path))
    if not path.is_file() or path.stat().st_size>limit:raise Refused()
    return path.read_text(encoding='utf8')

def document(path):return strict(read(path))

def save(path,value):
    raw=value if isinstance(value,str) else json.dumps(value,sort_keys=True,indent=2)+'\n'
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w',encoding='utf8') as file:
        file.write(raw);file.flush();os.fsync(file.fileno())

def environment(raw):
    if len(raw.encode('utf8'))>65536:raise Refused()
    value={}
    for line in raw.splitlines():
        if not line or line.startswith('#'):continue
        key,sep,item=line.partition('=')
        if not sep or not re.fullmatch('[A-Z][A-Z0-9_]{0,127}',key) or key in value or len(item)>16384 or any(ord(c)<32 for c in item):raise Refused()
        value[key]=item
    return value

def env_text(value):return ''.join(key+'='+item+'\n' for key,item in value.items())

def canonical(value):
    try:
        parsed=UUID(value)
        if str(parsed)!=value or not parsed.int:raise ValueError
        return value
    except (ValueError,TypeError,AttributeError):raise Refused() from None

def image(value):
    if not isinstance(value,str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9./:_-]*@sha256:[a-f0-9]{64}',value):raise Refused()
    return value

def origin(value):
    parsed=urlsplit(value)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:raise Refused()
    return parsed

def instant(value):
    try:
        parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
        if parsed.tzinfo is None or parsed.utcoffset().total_seconds()!=0:raise ValueError
        return parsed
    except (ValueError,TypeError,AttributeError):raise Refused() from None

def fresh(value,seconds,now=None):
    age=((now or datetime.now(timezone.utc))-instant(value)).total_seconds()
    if not 0<=age<=seconds:raise Refused('studies_rollout_evidence_stale')

def retained_path(value):
    """A target-host path is inspected lexically; it need not exist locally."""
    if (not isinstance(value,str) or not value.startswith('/') or str(Path(value))!=value
            or '..' in Path(value).parts or '$' in value or ':' in value
            or any(ord(character)<32 for character in value)):raise Refused('studies_rollout_compose_topology_unsupported')
    return value

def bind_mount(value):
    if isinstance(value,str):
        parts=value.split(':')
        if len(parts) not in (2,3) or (len(parts)==3 and parts[2] not in ('ro','rw')):raise Refused('studies_rollout_compose_topology_unsupported')
        source,target=parts[:2]
        readonly=len(parts)==3 and parts[2]=='ro'
    elif type(value) is dict and value.get('type')=='bind':
        source,target=value.get('source'),value.get('target')
        readonly=value.get('read_only',False)
        if type(readonly) is not bool:raise Refused('studies_rollout_compose_topology_unsupported')
    else:raise Refused('studies_rollout_compose_topology_unsupported')
    return retained_path(source),retained_path(target),readonly

def retained_topology(compose,migration_network):
    """Refuse relocation-sensitive Compose features; never merge/normalize them."""
    name=compose.get('name')
    if not isinstance(name,str) or not re.fullmatch('[a-z0-9][a-z0-9_-]*',name):raise Refused('studies_rollout_compose_project_required')
    if 'include' in compose:raise Refused('studies_rollout_compose_topology_unsupported')
    networks=compose.get('networks',{})
    if type(networks) is not dict:raise Refused('studies_rollout_compose_topology_unsupported')
    default=networks.get('default') or {}
    if type(default) is not dict or type(default.get('external',False)) is not bool:raise Refused('studies_rollout_compose_topology_unsupported')
    if default.get('external') and not default.get('name'):raise Refused('studies_rollout_compose_topology_unsupported')
    network_name=default.get('name',name+'_default')
    if migration_network!=network_name:raise Refused('studies_rollout_compose_network_mismatch')
    for service_name,service in compose['services'].items():
        if type(service) is not dict:raise Refused('studies_rollout_compose_topology_unsupported')
        if any(key in service for key in ('extends','build','label_file','develop')):raise Refused('studies_rollout_compose_topology_unsupported')
        if service_name in ('scribeswell','access') and 'environment' in service:raise Refused('studies_rollout_compose_environment_override')
        if service_name in ('scribeswell','access','gateway'):
            attached=service.get('networks',['default'])
            if 'network_mode' in service or not isinstance(attached,(list,dict)) or set(attached)!={'default'}:raise Refused('studies_rollout_compose_topology_unsupported')
        files=service.get('env_file',[])
        if isinstance(files,str):files=[files]
        if not isinstance(files,list):raise Refused('studies_rollout_compose_topology_unsupported')
        for file in files:retained_path(file.get('path') if type(file) is dict else file)
        volumes=service.get('volumes',[])
        if not isinstance(volumes,list):raise Refused('studies_rollout_compose_topology_unsupported')
        for volume in volumes:bind_mount(volume)
    for kind in ('configs','secrets'):
        definitions=compose.get(kind,{})
        if type(definitions) is not dict:raise Refused('studies_rollout_compose_topology_unsupported')
        for definition in definitions.values():
            if type(definition) is not dict or set(definition)-{'file','name'}:raise Refused('studies_rollout_compose_topology_unsupported')
            retained_path(definition.get('file'))
    mounts=compose['services']['gateway'].get('volumes',[])
    matches=[index for index,item in enumerate(mounts) if bind_mount(item)[1]=='/usr/local/apisix/conf/apisix.yaml']
    if len(matches)!=1 or not bind_mount(mounts[matches[0]])[2]:raise Refused('studies_rollout_gateway_mount_required')
    return matches[0]

def owner_module():
    # Fixed immutable qualification archive, never the mixed live owner tree.
    spec=importlib.util.spec_from_file_location('bounded_frozen_owner_readiness',OWNER/'services/access/studies_readiness.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def package_paths(name):
    # Match the selected image's Docker COPY inputs, not the mixed repository.
    paths={};workdir=Path('/')
    dockerfile=APP/'deployment'/('Dockerfile' if name=='api' else 'Migrations.Dockerfile')
    for line in dockerfile.read_text().splitlines():
        if line.startswith('WORKDIR '):workdir=workdir/line.split()[1]
        if not line.startswith('COPY '):continue
        parts=line.split()
        if len(parts)!=3:raise Refused()
        source=ROOT/parts[1]
        if source.is_symlink():raise Refused()
        for path in source.rglob('*') if source.is_dir() else (source,):
            relative=path.relative_to(ROOT)
            if any(part.startswith('.env') or part in ('__pycache__','.pytest_cache','tests','.local') for part in relative.parts) or path.suffix=='.pyc':continue
            if path.is_symlink():raise Refused()
            if path.is_file():
                destination=workdir/parts[2]
                if source.is_dir():destination/=path.relative_to(source)
                elif parts[2].endswith('/'):destination/=source.name
                paths.setdefault(str(relative),[]).append(str(destination))
    return paths

def package_sources(name):
    return {path:digest(ROOT/path) for path in sorted(package_paths(name))}

def sources():
    return package_sources('api')|package_sources('migration')|{str(APP.relative_to(ROOT)/'deployment'/name):digest(APP/'deployment'/name) for name in ('Dockerfile','Dockerfile.dockerignore','Migrations.Dockerfile','Migrations.Dockerfile.dockerignore')}

def validate_image_proof(record,inputs,current):
    # A retained exact image inspection/proof reference, never an operator boolean.
    if type(record) is not dict or set(record)!={'schema_version','source_revision','images','sources','proofs','inspections'} or type(record['schema_version']) is not int or record['schema_version']!=1:raise Refused()
    if record['source_revision']!=inputs['source_revision'] or record['images']!={name:inputs[name+'_image'] for name in ('api','migration','access')} or record['sources']!=current:raise Refused('studies_rollout_image_source_mismatch')
    if not isinstance(record['proofs'],dict) or not record['proofs']:raise Refused()
    for path,expected in record['proofs'].items():
        if not re.fullmatch('[a-f0-9]{64}',expected) or digest(external(path))!=expected:raise Refused('studies_rollout_proof_changed')
    if type(record['inspections']) is not dict or set(record['inspections'])!={'api','migration','access'}:raise Refused()
    owner=owner_module()
    for name,path in record['inspections'].items():
        if path not in record['proofs']:raise Refused()
        observed=document(path)
        if set(observed)!={'reference','image_id','repo_digests','packaged_sources'} or observed['reference']!=inputs[name+'_image'] or inputs[name+'_image'] not in observed['repo_digests'] or not re.fullmatch('sha256:[a-f0-9]{64}',observed['image_id']):raise Refused('studies_rollout_image_source_mismatch')
        if name=='access' and observed['image_id']!=FROZEN_ACCESS_IMAGE_ID:raise Refused('studies_rollout_frozen_access_required')
        expected=owner.runtime_hashes() if name=='access' else package_sources(name)
        if observed['packaged_sources']!=expected:raise Refused('studies_rollout_image_source_mismatch')

def inspect_images(inputs,output,*,run=subprocess.run):
    """Read local immutable images using no network/credentials or target access.

    A registry digest must already exist locally. This does not pull or publish.
    Actual startup/authorization/native proof files remain separately reviewable.
    """
    output=external(str(output));output.mkdir(mode=0o700)
    images={name:image(inputs[name+'_image']) for name in ('api','migration','access')}
    proof={'schema_version':1,'source_revision':inputs['source_revision'],'images':images,
        'sources':sources(),'proofs':{},'inspections':{}}
    for name,reference in images.items():
        result=run(['docker','image','inspect',reference],capture_output=True,text=True,timeout=10,check=True)
        inspected=strict(result.stdout)[0]
        if reference not in (inspected.get('RepoDigests') or []):raise Refused('studies_rollout_immutable_image_missing')
        if name=='access' and inspected.get('Id')!=FROZEN_ACCESS_IMAGE_ID:raise Refused('studies_rollout_frozen_access_required')
        expected=owner_module().runtime_hashes() if name=='access' else package_sources(name)
        paths={key:['/srv/'+key] for key in expected} if name=='access' else package_paths(name)
        code='import hashlib,json;from pathlib import Path;actual={key:[hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in paths] for key,paths in '+repr(paths)+'.items()};assert all(len(set(values))==1 for values in actual.values());print(json.dumps({key:values[0] for key,values in actual.items()}))'
        python='/opt/python/bin/python3.15' if name=='access' else 'python'
        result=run(['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges',
            '--entrypoint',python,reference,'-B','-c',code],capture_output=True,text=True,timeout=30,check=True)
        observed=strict(result.stdout)
        if observed!=expected:raise Refused('studies_rollout_image_source_mismatch')
        path=output/(name+'-inspection.json')
        save(path,{'reference':reference,'image_id':inspected['Id'],'repo_digests':inspected['RepoDigests'],'packaged_sources':observed})
        proof['proofs'][str(path)]=digest(path);proof['inspections'][name]=str(path)
    save(output/'image-proof.json',proof)
    return {'status':'local-image-bytes-inspected'}

def prepare(inputs,output,*,now=None):
    if type(inputs) is not dict or set(inputs)!=INPUT_FIELDS or type(inputs['schema_version']) is not int or inputs['schema_version']!=1:raise Refused()
    if not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.-]{0,63}',inputs['release_id']) or not re.fullmatch('[a-f0-9]{40}',inputs['source_revision']):raise Refused()
    canonical(inputs['account_id']);fresh(inputs['observed_at'],86400,now)
    for name in ('api','migration','access'):image(inputs[name+'_image'])
    origin(inputs['site_origin']);api=origin(inputs['api_origin'])
    release_profile.selection(inputs['migration_profile'])
    if not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.-]{0,127}',inputs['migration_network']):raise Refused()
    retained={key:external(inputs[key]) for key in ('retained_compose','retained_gateway','retained_api_env','retained_access_env','retained_frontend_env','private_env','image_proof')}
    # Read every retained input before creating output. No remote access occurs.
    raw={key:read(path) for key,path in retained.items()}
    current=sources();validate_image_proof(strict(raw['image_proof']),inputs,current)
    owner=owner_module();owner.validate_qualification(document(QUALIFICATION),QUALIFICATION.parent)
    compose=strict(raw['retained_compose'])
    gateway=strict(raw['retained_gateway'].removesuffix('#END\n').removesuffix('#END'))
    if type(compose) is not dict or type(compose.get('services')) is not dict or not {'scribeswell','access','gateway'}<=set(compose['services']):raise Refused()
    gateway_mount=retained_topology(compose,inputs['migration_network'])
    if not isinstance(gateway.get('routes'),list) or not isinstance(gateway.get('ssls'),list) or not gateway['ssls']:raise Refused()
    public=[r for r in gateway['routes'] if r.get('id')=='scribeswell']
    if len(public)!=1 or public[0].get('host')!=api.hostname or public[0].get('uris')!=['/scribeswell/api/bible/*'] or public[0].get('methods')!=['GET','OPTIONS']:raise Refused()
    if public[0].get('vars')!=[['scheme','==','https']] or public[0].get('plugins',{}).get('cors',{}).get('allow_origins')!=inputs['site_origin']:raise Refused()
    if any(r.get('id')=='scribeswell-studies' for r in gateway['routes']):raise Refused()
    secrets=environment(raw['private_env'])
    if set(secrets)!=API_PRIVATE|ACCESS_PRIVATE or not all(secrets.values()) or secrets['SCRIBESWELL_SERVICE_KEY']!=secrets['SCRIBESWELL_STUDIES_SERVICE_KEY']:raise Refused()
    sys.path.insert(0,str(APP/'backend'))
    from database import validate_url
    project=environment(raw['retained_api_env']).get('SUPABASE_URL')
    for key,role in {'SCRIBESWELL_STUDIES_DATABASE_URL':'scribeswell_studies_runtime',**owner.DATABASE_ROLES}.items():database_url(secrets[key],project,role)
    access_url=urlsplit(secrets['SCRIBESWELL_STUDIES_ACCESS_URL'])
    if secrets['SCRIBESWELL_STUDIES_ACCESS_URL']!='http://access:8000':raise Refused()
    runtime=environment(raw['retained_api_env']);access=environment(raw['retained_access_env']);frontend=environment(raw['retained_frontend_env'])
    if any('MIGRATION' in key for values in (runtime,access) for key in values):raise Refused('studies_rollout_runtime_migration_authority')
    if runtime.get('APP_ENV')!='production' or any(runtime.get(k) for k in ('SUPABASE_SECRET_KEY','SUPABASE_SERVICE_ROLE_KEY')):raise Refused()
    if inputs['site_origin'] not in strict(runtime.get('CORS_ORIGINS','[]'),4096):raise Refused()
    database_url(runtime.get('SCRIBESWELL_DATABASE_URL'),project,'scribeswell_runtime')
    if access.get('SUPABASE_URL')!=project or frontend.get('VITE_SUPABASE_URL')!=project:raise Refused('studies_rollout_project_mismatch')
    if runtime.get('SCRIBESWELL_STUDIES_ENABLED','false')!='false' or any(k in runtime for k in API_PRIVATE|{'SCRIBESWELL_STUDIES_ACCOUNT_ID'}):raise Refused()
    if any(k in access for k in ACCESS_PRIVATE|{'STUDIES_READINESS_JSON'}):raise Refused()
    if frontend.get('VITE_APP_BASE')!='/scribeswell/' or frontend.get('VITE_STUDIES_ENABLED','false')!='false' or not frontend.get('VITE_BIBLE_API_URL'):raise Refused()
    output=external(str(output));output.mkdir(mode=0o700) # create-only, never overwrite old evidence
    output.chmod(0o700)
    runtime.update({k:secrets[k] for k in API_PRIVATE});runtime.update(SCRIBESWELL_STUDIES_ENABLED='true',SCRIBESWELL_STUDIES_ACCOUNT_ID=inputs['account_id'])
    access.update({k:secrets[k] for k in ACCESS_PRIVATE})
    frontend.update(VITE_STUDIES_ENABLED='true',VITE_STUDIES_PREGRANTED='true',VITE_STUDIES_API_URL=inputs['api_origin']+'/scribeswell')
    save(output/'scribeswell.env',env_text(runtime));save(output/'access-pending.env',env_text(access));save(output/'frontend.env',env_text(frontend))
    save(output/'public-scribeswell.env',raw['retained_api_env']);save(output/'public-frontend.env',raw['retained_frontend_env'])
    candidate=deepcopy(compose)
    for service,file,reference in (('scribeswell','scribeswell.env',inputs['api_image']),('access','access.env',inputs['access_image'])):
        candidate['services'][service]['image']=reference
        candidate['services'][service]['env_file']=[{'path':str(output/file),'format':'raw'}]
    volumes=candidate['services']['gateway'].get('volumes',[])
    if isinstance(volumes[gateway_mount],str):volumes[gateway_mount]=str(output/'apisix.yaml')+':/usr/local/apisix/conf/apisix.yaml:ro'
    else:volumes[gateway_mount]['source']=str(output/'apisix.yaml')
    route=deepcopy(public[0]);route.update(id='scribeswell-studies',uris=['/scribeswell/api/studies','/scribeswell/api/studies/*','/scribeswell/api/operations/*'],methods=['GET','POST','PUT','DELETE','OPTIONS'])
    route['plugins']['cors']['allow_methods']='GET,POST,PUT,DELETE,OPTIONS'
    gateway['routes'].append(route)
    save(output/'compose.json',candidate);save(output/'apisix.yaml',json.dumps(gateway,indent=2)+'\n#END\n')
    save(output/'inputs.json',inputs)
    files={str(p):digest(p) for p in output.iterdir() if p.is_file()}
    plan={'schema_version':1,'release_id':inputs['release_id'],'source_revision':inputs['source_revision'],
        'activation_authorized':False,'status':'prepared-awaiting-approved-execution','sources':current,
        'retained':{str(path):digest(path) for path in retained.values()},'files':files,
        'owner_readiness_source':str(OWNER/'services/access/studies_readiness.py'),
        'owner_readiness_sha256':digest(OWNER/'services/access/studies_readiness.py'),
        'qualification_sha256':digest(QUALIFICATION),'images':{k:inputs[k+'_image'] for k in ('api','migration','access')}}
    plan['tool_sha256']=digest(Path(__file__))
    save(output/'candidate.json',plan)
    return plan

def checked_candidate(directory):
    directory=external(str(directory));plan=document(directory/'candidate.json')
    inputs=document(directory/'inputs.json')
    if plan['activation_authorized'] is not False or plan['tool_sha256']!=digest(Path(__file__)) or plan['sources']!=sources() or plan['images']!={k:inputs[k+'_image'] for k in ('api','migration','access')}:raise Refused('studies_rollout_candidate_changed')
    fresh(inputs['observed_at'],86400)
    for mapping in ('retained','files'):
        for path,expected in plan[mapping].items():
            if digest(external(path))!=expected:raise Refused('studies_rollout_candidate_changed')
    if plan['owner_readiness_sha256']!=digest(OWNER/'services/access/studies_readiness.py') or plan['qualification_sha256']!=digest(QUALIFICATION):raise Refused()
    validate_image_proof(document(inputs['image_proof']),inputs,plan['sources'])
    return directory,plan,inputs

def migrate(directory,migration_env,*,run=subprocess.run):
    directory,plan,inputs=checked_candidate(directory)
    values=environment(read(migration_env,65536))
    if set(values)-({'SUPABASE_URL','SCRIBESWELL_MIGRATION_DATABASE_URL','SCRIBESWELL_STUDIES_MIGRATION_ENABLED','SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL'}|release_profile.OPTION_KEYS):raise Refused('studies_rollout_foreign_migration_authority')
    if values.get('SCRIBESWELL_STUDIES_MIGRATION_ENABLED')!='true':raise Refused()
    sys.path.insert(0,str(APP/'backend'))
    from database import validate_url
    project=environment(read(inputs['retained_api_env']))['SUPABASE_URL']
    if values.get('SUPABASE_URL')!=project or release_profile.from_environ(values)!=inputs['migration_profile']:raise Refused('studies_rollout_project_mismatch')
    database_url(values.get('SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL'),project,'scribeswell_studies_migrator')
    database_url(values.get('SCRIBESWELL_MIGRATION_DATABASE_URL'),project,'scribeswell_migrator')
    frozen_env=directory/'migration-input.env';save(frozen_env,env_text(values))
    evidence=directory/'migration';evidence.mkdir(mode=0o700)
    os.chown(evidence,10001,10001)
    name='scribeswell-bounded-'+uuid4().hex
    command=['docker','run','--name',name,'--user','10001:10001','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges',
        '--pids-limit','64','--memory','256m','--cpus','1','--tmpfs','/tmp:rw,noexec,nosuid,size=16m',
        '--network',inputs['migration_network'],'--env-file',str(frozen_env),
        '--mount','type=bind,src='+str(evidence)+',dst=/evidence',plan['images']['migration']]
    started=datetime.now(timezone.utc).isoformat()
    # Always retain failed/unknown status; no activation on timeout or bad report.
    receipt={'release_id':plan['release_id'],'candidate_sha256':digest(directory/'candidate.json'),'image':plan['images']['migration'],
        'started_at':started,'status':'unknown','container_name':name,'migration_env_sha256':digest(frozen_env)}
    try:
        child=run(command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=190,check=False)
        if child.returncode!=0:raise Refused('studies_rollout_migration_failed')
        public=document(evidence/'migrations.json');private=document(evidence/'studies-migrations.json')
        if not release_profile.successful_report(public,inputs['migration_profile']) or not valid_result(private):raise Refused('studies_rollout_migration_failed')
        receipt.update(status='succeeded',report_sha256=digest(evidence/'migrations.json'),private_sha256=digest(evidence/'studies-migrations.json'))
    except subprocess.TimeoutExpired:
        try:run(['docker','stop','--time','10',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=20,check=False)
        except Exception:receipt['stop_outcome']='unknown'
        raise Refused('studies_rollout_migration_unknown') from None
    except Refused:
        receipt['status']='failed'
        raise
    finally:
        # Host wrapper runs with the same local administrator authority as the
        # existing release adapter; retain evidence and restore host custody.
        os.chown(evidence,os.getuid(),os.getgid())
        receipt['finished_at']=datetime.now(timezone.utc).isoformat()
        save(evidence/'execution.json',receipt)
    return receipt

def gate(directory,*,environ=None,prepare_owner=None):
    directory,plan,inputs=checked_candidate(directory)
    receipt=document(directory/'migration/execution.json')
    if receipt.get('status')!='succeeded' or receipt.get('release_id')!=plan['release_id'] or receipt.get('candidate_sha256')!=digest(directory/'candidate.json') or receipt.get('image')!=plan['images']['migration']:raise Refused('studies_rollout_migration_unproven')
    if receipt.get('migration_env_sha256')!=digest(directory/'migration-input.env'):raise Refused('studies_rollout_migration_unproven')
    fresh(receipt['finished_at'],900)
    for file,key in (('migrations.json','report_sha256'),('studies-migrations.json','private_sha256')):
        if receipt.get(key)!=digest(directory/'migration'/file):raise Refused('studies_rollout_migration_unproven')
    if not valid_result(document(directory/'migration/studies-migrations.json')):raise Refused('studies_rollout_migration_unproven')
    if not release_profile.successful_report(document(directory/'migration/migrations.json'),inputs['migration_profile']):raise Refused('studies_rollout_migration_unproven')
    owner=owner_module();owner.validate_qualification(document(QUALIFICATION),QUALIFICATION.parent)
    env=os.environ if environ is None else environ
    project=environment(read(inputs['retained_api_env']))['SUPABASE_URL']
    for owner_name in ('identity','access'):
        database_url(env[owner_name.upper()+'_MIGRATION_DATABASE_URL'],project,owner_name+'_migrator')
    # Run owner preparation NOW; no supplied readiness JSON/boolean is trusted.
    artifact=(prepare_owner or owner.prepare)(env['IDENTITY_MIGRATION_DATABASE_URL'],env['ACCESS_MIGRATION_DATABASE_URL'],QUALIFICATION,plan['release_id'])
    owner.validate_artifact(json.dumps(artifact))
    if artifact['release_id']!=plan['release_id'] or artifact['qualification_sha256']!=plan['qualification_sha256']:raise Refused('studies_rollout_readiness_unproven')
    access=environment(read(directory/'access-pending.env'))
    access['STUDIES_READINESS_JSON']=json.dumps(artifact,separators=(',',':'))
    save(directory/'studies-readiness.json',artifact);save(directory/'access.env',env_text(access))
    result={'status':'eligible-for-separate-production-approval','activation_authorized':False,
        'release_id':plan['release_id'],'checked_at':datetime.now(timezone.utc).isoformat(),
        'candidate_sha256':digest(directory/'candidate.json'),'readiness_sha256':digest(directory/'studies-readiness.json'),
        'access_env_sha256':digest(directory/'access.env'),'migration_execution_sha256':digest(directory/'migration/execution.json')}
    save(directory/'gate.json',result)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('prepare');p.add_argument('--inputs',type=Path);p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('migrate');p.add_argument('--candidate',type=Path,required=True);p.add_argument('--migration-env',type=Path,required=True)
    p=sub.add_parser('gate');p.add_argument('--candidate',type=Path,required=True)
    p=sub.add_parser('inspect-images');p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        if args.action=='prepare':
            if args.inputs is None:
                print(json.dumps({'status':'blocked','activation_authorized':False,'missing':['fresh retained target inventory','canonical existing account UUID','restricted secret configuration','exact candidate image/source/proof references']}));return 2
            result=prepare(document(args.inputs),args.output)
        elif args.action=='inspect-images':result=inspect_images(document(args.inputs),args.output)
        elif args.action=='migrate':result=migrate(args.candidate,args.migration_env)
        else:result=gate(args.candidate)
        print(json.dumps({'status':result['status'],'activation_authorized':False}))
        return 0
    except Exception:
        print('studies_rollout_refused',file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
