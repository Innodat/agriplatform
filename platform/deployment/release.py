"""Manifest validation and release coordination. No implicit remote operations."""
import argparse
import json
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
  front=m.get('frontend')
  if front:
   if front.get('install') not in ['prefix','workspace']:raise ValueError('invalid frontend install mode')
   if not safe_path(root,front['path']).is_dir() or not re.fullmatch(r'/(?:[a-z0-9-]+/)*',front['base']):raise ValueError('invalid frontend')
  if front and any(not re.fullmatch(r'VITE_[A-Z0-9_]+',key) or not re.fullmatch(r'/[a-zA-Z0-9/_-]+',value) for key,value in front.get('api_variables',{}).items()):raise ValueError('invalid frontend API mapping')
  public=m.get('public')
  if public:
   if not public.get('methods') or len(set(public['methods']))!=len(public['methods']) or any(method not in ['GET','HEAD','POST','PUT','PATCH','DELETE','OPTIONS'] for method in public['methods']):raise ValueError('invalid public methods')
   if not re.fullmatch('/[a-z0-9-]+',public['prefix']):raise ValueError('invalid public prefix')
   if any(not re.fullmatch(r'/api/[a-zA-Z0-9/_*-]+',p) or '..' in p or '**' in p for p in public['paths']):raise ValueError('invalid public path')
  for dependency in m.get('depends_on',[]):visit(dependency)
  visiting.remove(id);seen.add(id);result.append(m)
 for id in ids:visit(id)
 bases=[m['frontend']['base'] for m in docs if 'frontend' in m]
 prefixes=[m['public']['prefix'] for m in docs if 'public' in m]
 if len(set(bases))!=len(bases) or len(set(prefixes))!=len(prefixes):raise ValueError('duplicate public route')
 return result

def load_manifests(root=ROOT):
 registry=json.loads((root/'platform/deployment/registry.json').read_text())
 manifests=validate_manifests([json.loads(safe_path(root,path).read_text()) for path in registry['manifests']],root)
 owners=[m['migration']['owner'] for m in manifests if 'migration' in m]
 covered=[];groups=[]
 for group in registry.get('migration_groups',[]):
  if not re.fullmatch('[a-z][a-z0-9-]*',group['id']) or group['id'] in groups or group['id'] in [m['id'] for m in manifests]:raise ValueError('invalid migration group')
  if not safe_path(root,group['dockerfile']).is_file() or not re.fullmatch(r'[a-z0-9-]+\.env',group['env_file']):raise ValueError('invalid migration artifact')
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
 parser=argparse.ArgumentParser();parser.add_argument('command',choices=['check','list']);args=parser.parse_args()
 manifests=load_manifests()
 print(json.dumps(manifests) if args.command=='list' else 'Manifest contracts valid')
