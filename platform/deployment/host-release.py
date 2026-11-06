"""Host-side, serialized release. Invoke only with approved external target configuration."""
import argparse
import fcntl
import hashlib
import hmac
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import uuid
from release import ROOT, load_registry, load_manifests, safe_path, runtime_contract
from render_gateway import APISIX, render, origin, require_compose,file_configuration
from target_contract import database_url
from content_policy import validate_policy as validate_content_policy
from tls.renew import save as save_state, durable_unlink

def scribeswell_contract():
 # App-owned pure build-time contract, not an imported runtime/server capability.
 path=ROOT/'apps/scribeswell/migrations/release_profile.py'
 spec=importlib.util.spec_from_file_location('scribeswell_release_profile',path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module

def scribeswell_studies_contract():
 # The release image and host SHA bind this app-owned private target together.
 path=ROOT/'apps/scribeswell/deployment/studies_release_contract.py'
 spec=importlib.util.spec_from_file_location('scribeswell_studies_release_contract',path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module

def execute(args,**kwargs):
 # Suppress third-party exception/stdout content: credentials may be in database errors.
 kwargs.setdefault('stdout',subprocess.DEVNULL)
 return subprocess.run(args,check=True,stderr=subprocess.DEVNULL,**kwargs)

def fingerprint():
 registry=load_registry(ROOT);digest=hashlib.sha256()
 for item in registry['bootstrap_paths']:
  path=safe_path(ROOT,item)
  if not path.is_dir():raise ValueError('missing bootstrap source')
  for source in sorted(path.rglob('*.sql')):digest.update(str(source.relative_to(ROOT)).encode());digest.update(source.read_bytes())
 return digest.hexdigest()

def migration_fingerprint():
 digest=hashlib.sha256()
 for manifest in load_manifests():
  if 'migration' not in manifest:continue
  config=safe_path(ROOT,manifest['migration']['config'])
  sources=[config,*sorted(path for path in (config.parent/'migrations').rglob('*') if path.is_file() and path.suffix in ('.py','.json'))]
  for source in sources:digest.update(str(source.relative_to(ROOT)).encode());digest.update(source.read_bytes())
 registry=load_registry(ROOT)
 for group in registry.get('migration_groups',[]):
  for item in [group['dockerfile'],*group.get('compatibility_inputs',[])]:
   source=safe_path(ROOT,item)
   digest.update(str(source.relative_to(ROOT)).encode());digest.update(source.read_bytes())
 return digest.hexdigest()

def env_values(path):
 if path.stat().st_mode & 0o077:raise ValueError('runtime env must be private mode 0600')
 data={}
 for line in path.read_text().splitlines():
  if not line or line.startswith('#'):continue
  key,separator,value=line.partition('=')
  if not separator or key in data or not value or 'REQUIRED' in value or 'STAGING_' in value or '\x00' in value:raise ValueError('incomplete environment')
  data[key]=value
 return data

def preflight(config,environment,manifests,public_config,*,migration_inputs=None):
 # Build-time declarations describe the actual consumer implementation. Runtime
 # configuration cannot authorize a mixed release with the legacy signed reader.
 if any(item['id']=='content' for item in manifests):
  for item in manifests:
   if item['id']=='pts' and item.get('content_read_contract')!='owned-private-stream-v2':
    raise ValueError('content_consumer_contract_incompatible')
 expected_public={"environment":environment,"site":config["site"],"api":config["api"],"supabase_url":config["supabase_url"],"pts_file_origin":config.get("file_origins",{}).get("pts",{}).get("origin")}
 if os.environ.get('RELEASE_PROFILE','default')=='leave-pilot':
  if config.get('release_profile')!='leave-pilot' or config.get('leave_site')!='https://leave.machon.io':raise ValueError('leave_target_not_bound')
  expected_public.update(release_profile='leave-pilot',leave_site=config['leave_site'])
 if public_config!=expected_public:raise ValueError('CI public configuration differs from host')
 if config.get('release_profile','default')!=os.environ.get('RELEASE_PROFILE','default'):raise ValueError('release_profile_mismatch')
 if config['environment']!=environment:raise ValueError('environment mismatch')
 site=config['site'];api=config['api'];origin(site);origin(api)
 files=file_configuration(origin(api).hostname,site,manifests,config.get('file_origins',{}))
 if {m['id'] for m in manifests if 'private_files' in m}!=set(files):raise ValueError('missing private file origin')
 secrets=Path(config['env_dir'])
 if not secrets.is_absolute():raise ValueError('absolute external env_dir required')
 project=config['supabase_url'];origin(project)
 if environment=='staging' and project.rstrip('/')=='https://gjbsnxmbhxsvcblzgfts.supabase.co':raise ValueError('production staging database rejected')
 runtime_inputs={}
 for m in manifests:
  values=env_values(secrets/m['env_file'])
  runtime_inputs[m['id']]=values
  required,runtime_roles=runtime_contract(m,values,ROOT)
  if not required<=values.keys():raise ValueError('missing runtime inputs')
  if m['id']=='content':validate_content_policy(secrets,values)
  if any(field in values for field in m.get('forbidden_env',[])):raise ValueError('obsolete runtime authority')
  if any('MIGRATION' in key or 'IMPORT' in key for key in values):raise ValueError('privileged runtime inputs')
  for field,role in runtime_roles.items():database_url(values[field],project,role)
  if any(key.endswith('_DATABASE_URL') and key not in runtime_roles for key in values):raise ValueError('undeclared database authority')
  if 'CONTENT_S3_ENDPOINT' in values and values['CONTENT_S3_ENDPOINT']!=project+'/storage/v1/s3':raise ValueError('Storage project mismatch')
  if 'SUPABASE_URL' in values and values['SUPABASE_URL']!=project:raise ValueError('runtime project mismatch')
  if 'CORS_ORIGINS' in values and json.loads(values['CORS_ORIGINS'])!=([site,'https://leave.machon.io'] if m['id']=='directory' and any(item['id']=='leave' for item in manifests) else [site]):raise ValueError('CORS mismatch')
  if 'PTS_CORS_ORIGINS' in values and values['PTS_CORS_ORIGINS']!=site:raise ValueError('CORS mismatch')
  if m['id'] in files:
   selected=files[m['id']]
   if values.get('PTS_FILE_ORIGIN')!=selected['origin'] or values.get('PTS_FILE_FRONTEND_ORIGIN')!=selected['frontend_origin']:raise ValueError('private file origin mismatch')
 if 'pts' in files:
  pts=runtime_inputs['pts'];identity=runtime_inputs.get('access',{})
  if not identity.get('PTS_CURRENT_SESSION_SERVICE_KEY') or not hmac.compare_digest(pts.get('PTS_CURRENT_SESSION_SERVICE_KEY',''),identity['PTS_CURRENT_SESSION_SERVICE_KEY']):raise ValueError('private file current-session configuration mismatch')
 if 'directory' in runtime_inputs:
  access_inputs=runtime_inputs.get('access',{})
  directory_key=runtime_inputs['directory'].get('DIRECTORY_SERVICE_KEY','')
  access_key=access_inputs.get('DIRECTORY_SERVICE_KEY','')
  if (not directory_key or not access_key
      or any(not 33<=ord(char)<=126 for char in directory_key+access_key)
      or not hmac.compare_digest(directory_key,access_key)
      or any(hmac.compare_digest(directory_key.encode(),value.encode())
             for field,value in access_inputs.items()
             if field.endswith('_SERVICE_KEY') and field!='DIRECTORY_SERVICE_KEY')):
   raise ValueError('directory_discovery_configuration_invalid')
 if 'leave' in runtime_inputs:
  directory=runtime_inputs.get('directory',{})
  publication=directory.get('APP_PUBLISH_LEAVE','false')
  if publication not in ('true','false') or (publication=='true' and directory.get('APP_URL_LEAVE')!='https://leave.machon.io'):raise ValueError('leave_directory_publication_invalid')
  leave=runtime_inputs['leave'];access=runtime_inputs.get('access',{})
  if leave.get('LEAVE_ACCESS_ORIGIN')!='http://access:8000':raise ValueError('leave_access_origin_invalid')
  pairs={'LEAVE_SERVICE_KEY':'LEAVE_SERVICE_KEY','LEAVE_CURRENT_SESSION_SERVICE_KEY':'LEAVE_CURRENT_SESSION_SERVICE_KEY','LEAVE_PREFERENCES_SERVICE_KEY':'IDENTITY_PREFERENCES_SERVICE_KEY'}
  selected=[]
  for field,paired in pairs.items():
   key=leave.get(field,'')
   if (not key or (field=='LEAVE_CURRENT_SESSION_SERVICE_KEY' and not 32<=len(key)<=256) or any(not 33<=ord(char)<=126 for char in key) or not access.get(paired) or not hmac.compare_digest(key,access[paired])
       or any(hmac.compare_digest(key,value) for name,value in access.items() if name.endswith('_SERVICE_KEY') and name!=paired)):
    raise ValueError('leave_service_pair_invalid')
   selected.append(key)
  if len(set(selected))!=3:raise ValueError('leave_service_pair_invalid')
 registry=load_registry(ROOT)
 owner_map={m['migration']['owner']:m['migration'] for m in manifests if 'migration' in m}
 for group in registry.get('migration_groups',[]):
  values=env_values(secrets/group['env_file'])
  if values.get('SUPABASE_URL')!=project:raise ValueError('migration project mismatch')
  expected={owner_map[owner]['url_env']:owner_map[owner]['role'] for owner in group['owners']}
  options={'PTS_CORPUS_ADOPTION_INPUT_JSON'} if group['id']=='pts-owned' else set()
  if group['id']=='scribeswell-owned':
   contract=scribeswell_contract();contract.from_environ(values);options=contract.OPTION_KEYS|{'SCRIBESWELL_STUDIES_MIGRATION_ENABLED','SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL'}
   private_enabled=values.get('SCRIBESWELL_STUDIES_MIGRATION_ENABLED','false')
   if private_enabled not in ('true','false') or (private_enabled=='true')!=('SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL' in values):raise ValueError('partial private migration configuration')
   if private_enabled=='true':database_url(values['SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL'],project,'scribeswell_studies_migrator')
  if not {*expected,'SUPABASE_URL'}<=set(values) or set(values)-{*expected,'SUPABASE_URL'}-options:raise ValueError('migration authority mismatch')
  for field,role in expected.items():database_url(values[field],project,role)
  if migration_inputs is not None:migration_inputs[group['id']]=dict(values)
 bootstrap=json.loads(Path(config['bootstrap_evidence']).read_text())
 if os.environ.get('RELEASE_PROFILE','default')=='leave-pilot':
  adoption=bootstrap.get('leave_adoption',{})
  if (adoption.get('identity_revision')!='identity_0030' or adoption.get('access_revision')!='access_0019' or adoption.get('mode')!='already-compatible'
      or not all(isinstance(adoption.get(field),str) and adoption[field].strip() for field in ('catalog_observation','recovery_reference','pilot_bindings_reference'))):raise ValueError('leave_prerequisites_unqualified')
 if bootstrap.get('environment')!=environment or bootstrap.get('supabase_url')!=project or bootstrap.get('schema_fingerprint')!=fingerprint() or bootstrap.get('migration_compatibility_fingerprint')!=migration_fingerprint() or not all(bootstrap.get(key) is True for key in ['initial_schema_verified','previous_version_compatible','recovery_verified','auth_storage_verified']) or not isinstance(bootstrap.get('approval_reference'),str) or not bootstrap['approval_reference'].strip():raise ValueError('bootstrap/compatibility evidence missing or stale')
 return secrets

def supervisor_events(environment,since,previous_ids):
 result={'events':[],'warnings':[]}
 try:
  raw=subprocess.check_output(['docker','events','--since',str(since),'--until',str(int(time.time())+1),'--filter','type=container','--filter','label=com.docker.compose.project=agriplatform-'+environment,'--format','{{json .}}'],text=True,stderr=subprocess.DEVNULL,timeout=10)
  for line in raw.splitlines():
   event=json.loads(line);action=event.get('Action',event.get('status'));attrs=event.get('Actor',{}).get('Attributes',{})
   if action not in ['stop','kill','die','oom']:continue
   item={'container_id':event.get('id',event.get('Actor',{}).get('ID')),'action':action,'time':event.get('time'),'exit_code':attrs.get('exitCode'),'signal':attrs.get('signal')}
   result['events'].append(item)
   if action=='oom' or str(item['signal']) in ['9','SIGKILL'] or str(item['exit_code'])=='137':result['warnings'].append({'code':'forced_termination','container_id':item['container_id']})
  current=subprocess.check_output(['docker','ps','-q','--no-trunc','--filter','label=com.docker.compose.project=agriplatform-'+environment],text=True,stderr=subprocess.DEVNULL,timeout=10).split()
  observed={item['container_id'] for item in result['events'] if item['action']=='die'}
  for previous in previous_ids:
   if previous not in current and previous not in observed:result['warnings'].append({'code':'shutdown_outcome_unobserved','container_id':previous})
 except Exception:result['warnings'].append({'code':'supervisor_observation_failed'})
 return result

def deploy(environment,sha,images_path,config_path,release_dir,public_config_path):
 if not re.fullmatch('[0-9a-f]{40}',sha):raise ValueError('exact commit SHA required')
 config=json.loads(config_path.read_text())
 # Hosted owners have independent ancestry and an active retained Studies
 # deployment. Ordinary registry groups/rendering are not a qualified invocation.
 # Prepare retained Leave-only artifacts; production execution is separately gated.
 if config.get('owner_profile') is not None:raise ValueError('hosted_leave_prepared_invocation_required')
 manifests=load_manifests();migration_inputs={}
 secrets=preflight(config,environment,manifests,json.loads(public_config_path.read_text()),migration_inputs=migration_inputs)
 images=json.loads(images_path.read_text());registry=load_registry(ROOT)
 if images.get('sha')!=sha:raise ValueError('image commit mismatch')
 if set(images['images'])!={m['id'] for m in manifests}|{g['id'] for g in registry.get('migration_groups',[])}:raise ValueError('image inventory mismatch')
 require_compose()
 # Lock covers migrations AND activation; CI also serializes the environment.
 state=Path(config['state_dir']);state.mkdir(parents=True,exist_ok=True,mode=0o750)
 with (state/'release.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if (state/'tls-pending.json').exists():raise ValueError('TLS recovery pending; reconcile before release')
  if (state/'release-pending.json').exists():raise ValueError('Application activation pending; reconcile before release')
  previous=json.loads((state/'current.json').read_text()) if (state/'current.json').exists() else None
  if previous and 'leave' in previous.get('images',{}) and not any(m['id']=='leave' for m in manifests):raise ValueError('existing Leave requires complete pilot inventory')
  release_dir.mkdir(parents=True,exist_ok=False,mode=0o750)
  report={'sha':sha,'environment':environment,'images':images['images'],'started_at':int(time.time()),'activated':False,'migrations':{},'previous':json.loads((state/'current.json').read_text()) if (state/'current.json').exists() else None}
  def save():
   tmp=release_dir/'evidence.tmp';tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(release_dir/'evidence.json')
  save()
  inputs_temp=None
  try:
   # Freeze the exact validated migration inputs, including credentials, privately.
   # Docker and evidence comparison consume the same attempt-specific selection.
   inputs_temp=tempfile.TemporaryDirectory(prefix='migration-inputs-',dir=state)
   input_dir=Path(inputs_temp.name)
   for group in registry.get('migration_groups',[]):
    fd=os.open(input_dir/group['env_file'],os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as stream:
     stream.write(''.join(key+'='+value+'\n' for key,value in migration_inputs[group['id']].items()))
     stream.flush();os.fsync(stream.fileno())
   for group in registry.get('migration_groups',[]):
    report['migrations'][group['id']]={'status':'not_attempted'}
   # Validate and pull ALL images before any database changes.
   for group in registry.get('migration_groups',[]):env_values(input_dir/group['env_file'])
   for image in [APISIX,*images['images'].values()]:
    if not re.fullmatch(r'[a-zA-Z0-9./:_-]+@sha256:[0-9a-f]{64}',image):raise ValueError('immutable images required')
    execute(['docker','pull',image],timeout=300)
   if any('private_files' in item for item in manifests):
    # Identity remains separately migrated. Probe its additive0030 cleanup
    # prerequisite with only the existing restricted runtime credential before
    # any app migration or activation; never place Identity migration keys here.
    report['identity_file_cleanup']={'required_contract':'exact-credential-receipts-v1','required_migration':'identity_0030','status':'checking'};save()
    identity_inputs=env_values(secrets/'access.env')
    identity_env=input_dir/'identity-cleanup.env'
    fd=os.open(identity_env,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as stream:stream.write('IDENTITY_CURRENT_SESSION_DATABASE_URL='+identity_inputs['IDENTITY_CURRENT_SESSION_DATABASE_URL']+'\n')
    execute(['docker','run','--rm','--network','host','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges:true','--env-file',str(identity_env),images['images']['access'],'/opt/python/bin/python3.15','-B','/srv/file_cleanup_preflight.py'],timeout=10)
    report['identity_file_cleanup']['status']='verified';save()
   generated=release_dir/'gateway'
   render(generated,secrets,images['images'],config['site'],config['api'],Path(config['cert']),Path(config['key']),environment,file_origins=config.get('file_origins'))
   # Official gateway runs uid/gid 636; config contains TLS key, readable by gateway group only.
   os.chown(generated,-1,636);os.chown(generated/'apisix.yaml',-1,636)
   for group in registry.get('migration_groups',[]):
    group_id=group['id'];entry=report['migrations'][group_id];entry['status']='running';save()
    migration_env=input_dir/group['env_file'];migration_values=migration_inputs[group_id]
    expected_validation=scribeswell_contract().from_environ(migration_values) if group_id=='scribeswell-owned' else None
    evidence=release_dir/group_id;evidence.mkdir(mode=0o700);os.chown(evidence,group.get('evidence_uid',10001),group.get('evidence_uid',10001))
    migration_name='migration-'+group_id+'-'+uuid.uuid4().hex
    network_name=migration_name+'-network';network_created=False;job_succeeded=False
    entry['network']={'name':network_name,'creation':'pending','cleanup':'not_owned'};save()
    try:
     # Docker rejects an existing name. Only a confirmed creation grants cleanup ownership.
     entry['network']['creation']='failed_or_uncertain';save()
     execute(['docker','network','create','--driver','bridge','--ipv6','--label','agriplatform.migration='+migration_name,network_name],timeout=30)
     network_created=True;entry['network']['creation']='created';entry['network']['cleanup']='pending';save()
     entry['command']=['docker','run','--rm','--name',migration_name,'--network',network_name,'--env-file',str(migration_env),'-v',str(evidence)+':/evidence',images['images'][group_id]];save()
     execute(entry['command'],timeout=1500)
     job_succeeded=True
    except subprocess.TimeoutExpired:
     entry['supervisor_warning']='migration_timeout_outcome_requires_reconciliation' if network_created else 'network_creation_timeout_requires_reconciliation'
     try:save()
     finally:
      if network_created:
       try:execute(['docker','stop','--time','20',migration_name],timeout=30);entry['stop_command']='succeeded'
       except Exception:entry['stop_command']='failed_or_uncertain'
     save();raise
    finally:
     entry['status']='failed'
     try:
      if network_created:
       entry['network']['cleanup']='failed_or_uncertain'
       try:save()
       finally:
        execute(['docker','network','rm',network_name],timeout=30)
        entry['network']['cleanup']='removed'
     finally:
      # Cleanup must run even when the migration evidence is absent or malformed.
      try:
       evidence_file=evidence/'migrations.json'
       if group_id=='scribeswell-owned':
        contract=scribeswell_contract()
        detail=None
        if evidence_file.exists():
         with evidence_file.open() as stream:
          try:detail=contract.strict_json(stream.read(4097),4096)
          except ValueError:pass
        qualified=contract.successful_report(detail,expected_validation)
        if migration_values.get('SCRIBESWELL_STUDIES_MIGRATION_ENABLED')=='true':
         private_file=evidence/'studies-migrations.json'
         private_detail=None
         if private_file.exists():
          with private_file.open() as stream:
           try:private_detail=contract.strict_json(stream.read(4097),4096)
           except ValueError:pass
         private_qualified=scribeswell_studies_contract().valid_result(private_detail)
         # Retain only validated private observations, never raw child diagnostics.
         entry['private_detail']=private_detail if private_qualified else None
         qualified=qualified and private_qualified
        entry['detail']=detail if qualified else contract.safe_failure(detail,expected_validation)
       else:
        entry['detail']=json.loads(evidence_file.read_text()) if evidence_file.exists() else None
        qualified=bool(entry['detail'] and entry['detail'].get('complete'))
        if group_id=='leave-owned':
         detail=entry['detail'];owner=detail.get('owners',{}).get('leave',{}) if isinstance(detail,dict) else {}
         qualified=(isinstance(detail,dict) and set(detail)=={'complete','owners','outcome_requires_reconciliation'} and detail['complete'] is True and detail['outcome_requires_reconciliation'] is False
                    and set(detail['owners'])=={'leave'} and set(owner)=={'status','before','revision'} and owner['status']=='succeeded' and owner['revision']=='0002_selection' and owner['before'] in ([],['0001_baseline'],['0002_selection']))
       if job_succeeded and entry['network']['cleanup']=='removed' and qualified:entry['status']='succeeded'
      finally:save()
    if entry['status']!='succeeded':raise ValueError('migration failed')
   inputs_temp.cleanup();inputs_temp=None
   command=['docker','compose','-f',str(generated/'compose.json')]
   previous_ids=subprocess.check_output(['docker','ps','-q','--no-trunc','--filter','label=com.docker.compose.project=agriplatform-'+environment],text=True,stderr=subprocess.DEVNULL,timeout=10).split()
   candidate={'sha':sha,'images':images['images'],'compose':str(generated/'compose.json'),'evidence':str(release_dir/'evidence.json')}
   save_state(state/'release-pending.json',{'candidate':candidate,'previous':report['previous'],'environment':environment})
   activation_started=int(time.time());report['supervisor']={'status':'observing','previous_container_ids':previous_ids};save()
   try:execute([*command,'up','-d','--wait','--wait-timeout','120','--remove-orphans'],timeout=240)
   finally:report['supervisor']=supervisor_events(environment,activation_started,previous_ids);save()
   # Gateway has no health endpoint: verify a real public route through TLS and CORS.
   probe=execute(['curl','--fail','--silent','--show-error','--retry','10','--retry-all-errors','--retry-delay','2','--connect-timeout','5','--max-time','45','--resolve',origin(config['api']).hostname+':443:127.0.0.1',config['api']+'/directory/api/v2/me/apps'],timeout=600,stdout=subprocess.PIPE)
   try:
    if json.loads(probe.stdout)!={'apps':[],'protected_access_status':'sign_in_required'}:raise ValueError()
   except (ValueError,TypeError):raise ValueError('directory_probe_invalid') from None
   report['activated']=True;report['finished_at']=int(time.time());save()
   save_state(state/'current.json',candidate)
   durable_unlink(state/'release-pending.json')
  except Exception:
   report['code']='release_failed_reconcile_before_retry';report['finished_at']=int(time.time());save();raise
  finally:
   if inputs_temp is not None:inputs_temp.cleanup()

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--profile',choices=['default','leave-pilot'],default=os.environ.get('RELEASE_PROFILE','default'));p.add_argument('--public-config',type=Path);p.add_argument('--fingerprint',action='store_true');p.add_argument('--environment',choices=['staging','production']);p.add_argument('--sha');p.add_argument('--images',type=Path);p.add_argument('--config',type=Path);p.add_argument('--release-dir',type=Path);a=p.parse_args()
 os.environ['RELEASE_PROFILE']=a.profile
 if a.fingerprint:print(json.dumps({'schema_fingerprint':fingerprint(),'migration_compatibility_fingerprint':migration_fingerprint()},indent=2))
 else:
  try:deploy(a.environment,a.sha,a.images,a.config,a.release_dir,a.public_config)
  except Exception:raise SystemExit('Release blocked or failed; inspect safe release evidence and reconcile before retry') from None
