"""Manifest validation and release coordination. No implicit remote operations."""
import argparse
import json
import os
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def safe_path(root,value):
 path=Path(value)
 if path.is_absolute() or '..' in path.parts or not (root/path).resolve().is_relative_to(root.resolve()):raise ValueError('unsafe manifest path')
 return root/path

def validate_manifests(docs,root):
 ids=[m['id'] for m in docs]
 if len(ids)!=len(set(ids)) or any(not re.fullmatch('[a-z][a-z0-9-]*',id) for id in ids):raise ValueError('invalid manifest id')
 by_id=dict(zip(ids,docs));result=[];visiting=set();seen=set()
 def visit(id):
  if id in visiting:raise ValueError('dependency cycle')
  if id in seen:return
  if id not in by_id:raise ValueError('unknown dependency')
  visiting.add(id);m=by_id[id]
  if not safe_path(root,m['dockerfile']).is_file():raise ValueError('missing Dockerfile')
  if m.get('env_file',id+'.env')!=id+'.env':raise ValueError('unsafe env file')
  if not re.fullmatch(r'/[a-zA-Z0-9/_-]+',m.get('health_path','')):raise ValueError('invalid health path')
  if any(not re.fullmatch('[A-Z][A-Z0-9_]*_DATABASE_URL',field) or not re.fullmatch('[a-z][a-z0-9_]*_runtime',role) for field,role in m.get('database_roles',{}).items()):raise ValueError('invalid runtime database authority')
  if 'migration' in m and not re.fullmatch('[a-z][a-z0-9_]*_migrator',m['migration'].get('role','')):raise ValueError('invalid migration database authority')
  private=m.get('personal_studies')
  if private is not None:
   if m['id']!='scribeswell' or private.get('production_enabled') is not False or private.get('enabled_env')!='SCRIBESWELL_STUDIES_ENABLED':raise ValueError('invalid personal Studies feature contract')
   if private.get('database_roles')!={'SCRIBESWELL_STUDIES_DATABASE_URL':'scribeswell_studies_runtime'}:raise ValueError('invalid personal Studies authority')
  feature=m.get('studies_enrollment')
  if feature is not None:
   if m['id']!='access' or feature.get('enabled_env')!='SCRIBESWELL_SERVICE_KEY' or set(feature)!= {'enabled_env','required_env','database_roles'}:raise ValueError('invalid Studies feature contract')
   expected={'STUDIES_ACCESS_DATABASE_URL':'access_studies_runtime','STUDIES_IDENTITY_DATABASE_URL':'identity_studies_reader_runtime','STUDIES_IDENTITY_SETUP_DATABASE_URL':'identity_studies_setup_runtime'}
   if feature['database_roles']!=expected or set(feature['required_env'])!= {*expected,'SCRIBESWELL_SERVICE_KEY','STUDIES_READINESS_JSON'}:raise ValueError('invalid Studies runtime authority')
  for feature_name,prefix in (('current_session','PTS'),('leave_current_session','LEAVE')):
   session=m.get(feature_name)
   if session is not None:
    expected={prefix+'_CURRENT_SESSION_SERVICE_KEY','IDENTITY_CURRENT_SESSION_DATABASE_URL','IDENTITY_CURRENT_SESSION_AUTH_URL','IDENTITY_CURRENT_SESSION_ISSUER','IDENTITY_CURRENT_SESSION_AUDIENCE','IDENTITY_CURRENT_SESSION_POLICY','SUPABASE_ANON_KEY'}
    if (m['id']!='access' or set(session)!={'enabled_env','required_env','optional_env','database_roles'}
        or session['enabled_env']!=prefix+'_CURRENT_SESSION_SERVICE_KEY' or set(session['required_env'])!=expected
        or session['optional_env']!=[prefix+'_CURRENT_SESSION_PREVIOUS_SERVICE_KEY']
        or session['database_roles']!={'IDENTITY_CURRENT_SESSION_DATABASE_URL':'identity_current_session_runtime'}):raise ValueError('invalid current-session runtime authority')
  preferences=m.get('preferences')
  if preferences is not None:
   if m['id']!='access' or preferences!={'required_env':['IDENTITY_PREFERENCES_DATABASE_URL','IDENTITY_PREFERENCES_SERVICE_KEY'],'database_roles':{'IDENTITY_PREFERENCES_DATABASE_URL':'identity_preferences_runtime'}}:raise ValueError('invalid preferences authority')
  front=m.get('frontend')
  if front:
   if front.get('publication','shared') not in ('shared','leave') or (front.get('publication')=='leave' and m['id']!='leave'):raise ValueError('invalid publication owner')
   if front.get('install') not in ['prefix','workspace']:raise ValueError('invalid frontend install mode')
   if not safe_path(root,front['path']).is_dir() or not re.fullmatch(r'/(?:[a-z0-9-]+/)*',front['base']):raise ValueError('invalid frontend')
  if front and any(not re.fullmatch(r'VITE_[A-Z0-9_]+',key) or not re.fullmatch(r'/[a-zA-Z0-9/_-]+',value) for key,value in front.get('api_variables',{}).items()):raise ValueError('invalid frontend API mapping')
  public=m.get('public')
  files=m.get('private_files')
  if files is not None:
   if set(files)!={'session_paths','read_paths'} or any(not isinstance(paths,list) or not paths or any(not isinstance(p,str) or not re.fullmatch(r'/api/[a-zA-Z0-9/_*-]+',p) or '..' in p or '**' in p for p in paths) for paths in files.values()):raise ValueError('invalid private file routes')
  if public:
   if 'native_mount' in public and (m['id']!='leave' or public['native_mount']!='/api' or public['prefix']!='/leave'):raise ValueError('invalid native API mount')
   if not public.get('methods') or len(set(public['methods']))!=len(public['methods']) or any(method not in ['GET','HEAD','POST','PUT','PATCH','DELETE','OPTIONS'] for method in public['methods']):raise ValueError('invalid public methods')
   if not re.fullmatch('/[a-z0-9-]+',public['prefix']):raise ValueError('invalid public prefix')
   if any(not re.fullmatch(r'/api/[a-zA-Z0-9/_*-]+',p) or '..' in p or '**' in p for p in public['paths']):raise ValueError('invalid public path')
  for dependency in m.get('depends_on',[]):visit(dependency)
  visiting.remove(id);seen.add(id);result.append(m)
 for id in ids:visit(id)
 bases=[(m['frontend'].get('publication','shared'),m['frontend']['base']) for m in docs if 'frontend' in m]
 prefixes=[m['public']['prefix'] for m in docs if 'public' in m]
 if len(set(bases))!=len(bases) or len(set(prefixes))!=len(prefixes):raise ValueError('duplicate public route')
 return result

def runtime_contract(manifest,values,root=ROOT):
 # First consuming opt-in owner contract. Ordinary services keep their current
 # required inputs; runtime credentials never imply migration authority.
 required=set(manifest.get('required_env',[]));roles=dict(manifest.get('database_roles',{}))
 preferences=manifest.get('preferences')
 if preferences and any(field in values for field in preferences['required_env']):
  if not all(isinstance(values.get(field),str) and values[field].strip() for field in preferences['required_env']):raise ValueError('partial preferences configuration')
  required.update(preferences['required_env']);roles.update(preferences['database_roles'])
 sessions=[manifest[name] for name in ('current_session','leave_current_session') if name in manifest]
 if sessions:
  fields=set().union(*(set(session['required_env'])|set(session['optional_env']) for session in sessions))-{'SUPABASE_ANON_KEY'}
  if any(field in values for field in fields):
   active=[session for session in sessions if values.get(session['enabled_env'])]
   if not active:raise ValueError('partial current-session configuration')
   for session in sessions:
    if any(field in values for field in session['optional_env']) and session not in active:raise ValueError('partial current-session configuration')
   for session in active:
    if not all(isinstance(values.get(field),str) and values[field].strip() for field in session['required_env']):raise ValueError('partial current-session configuration')
    required.update(session['required_env']);roles.update(session['database_roles'])
   if values['IDENTITY_CURRENT_SESSION_POLICY']!='supabase-auth-2.197.0-default':raise ValueError('unsupported current-session provider policy')
 private=manifest.get('personal_studies')
 if private is not None:
  enabled=values.get(private['enabled_env'],'false')
  if enabled not in ('true','false'):raise ValueError('invalid personal Studies opt-in')
  if enabled=='true':raise ValueError('personal Studies production activation awaits qualification')
  if any(field in values for field in private['required_env']):raise ValueError('partial personal Studies configuration')
 feature=manifest.get('studies_enrollment')
 if feature is None:return required,roles
 if manifest['id']!='access':raise ValueError('unsupported Studies owner')
 active=bool(values.get(feature['enabled_env']))
 if not active:
  if any(field in values for field in feature['required_env']):raise ValueError('partial Studies configuration')
  return required,roles
 required.update(feature['required_env'])
 if not required<=values.keys():raise ValueError('missing Studies runtime inputs')
 import importlib.util
 path=safe_path(root,'services/access/studies_readiness.py')
 spec=importlib.util.spec_from_file_location('access_studies_release_contract',path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 module.validate_artifact(values['STUDIES_READINESS_JSON'])
 roles.update(feature['database_roles'])
 return required,roles

def load_registry(root=ROOT):
 registry=json.loads((root/'platform/deployment/registry.json').read_text())
 profile=os.environ.get('RELEASE_PROFILE','default')
 if profile not in ('default','leave-pilot'):raise ValueError('invalid release profile')
 if profile=='leave-pilot':
  # Extend the complete maintained inventory; never replace the shared Compose set.
  registry['manifests'].append('apps/leave/deployment/manifest.json')
  group=json.loads((root/'apps/leave/deployment/migration-group.example.json').read_text())
  registry['migration_groups'].append(group)
 return registry

def load_manifests(root=ROOT):
 registry=load_registry(root)
 manifests=validate_manifests([json.loads(safe_path(root,path).read_text()) for path in registry['manifests']],root)
 owners=[m['migration']['owner'] for m in manifests if 'migration' in m]
 covered=[];groups=[]
 for group in registry.get('migration_groups',[]):
  if not re.fullmatch('[a-z][a-z0-9-]*',group['id']) or group['id'] in groups or group['id'] in [m['id'] for m in manifests]:raise ValueError('invalid migration group')
  if not safe_path(root,group['dockerfile']).is_file() or not re.fullmatch(r'[a-z0-9-]+\.env',group['env_file']):raise ValueError('invalid migration artifact')
  inputs=group.get('compatibility_inputs',[])
  if not isinstance(inputs,list) or any(not isinstance(path,str) or not safe_path(root,path).is_file() for path in inputs):raise ValueError('invalid migration compatibility input')
  if 'evidence_uid' in group and (group['id']!='leave-owned' or group['evidence_uid']!=65532):raise ValueError('invalid evidence owner')
  groups.append(group['id']);covered.extend(group['owners'])
 if sorted(owners)!=sorted(covered):raise ValueError('migration owners require exactly one group')
 for path in registry['bootstrap_paths']:
  if not safe_path(root,path).is_dir():raise ValueError('invalid bootstrap path')
 return manifests

def coordinate(owners,migrate,activate,record=lambda _:None):
 report={'owners':{owner:{'status':'not_attempted'} for owner in owners},'activated':False}
 record(report)
 for owner in owners:
  report['owners'][owner]['status']='running';record(report)
  try:
   detail=migrate(owner)
   report['owners'][owner].update(status='succeeded',detail=detail)
  except Exception:
   report['owners'][owner].update(status='failed',outcome_requires_reconciliation=True)
   report['code']='migration_failed';record(report);return report
  record(report)
 try:activate();report['activated']=True
 except Exception:report['code']='activation_failed'
 record(report);return report

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('command',choices=['check','list','registry']);args=parser.parse_args()
 manifests=load_manifests()
 print(json.dumps(load_registry()) if args.command=='registry' else json.dumps(manifests) if args.command=='list' else 'Manifest contracts valid')
