import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
spec=importlib.util.spec_from_file_location('host',Path(__file__).parents[1]/'host-release.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
class Host(unittest.TestCase):
 def setup_target(self,root):
  env=root/'env';env.mkdir();manifests=host.load_manifests();project='https://stage.supabase.co';site='https://stage.test'
  for m in manifests:
   values=m['smoke_env'].copy()
   for field,role in m.get('database_roles',{}).items():values[field]=f'postgresql+psycopg://{role}:literal$dollar@db.stage.supabase.co/postgres?sslmode=require'
   if 'SUPABASE_URL' in values:values['SUPABASE_URL']=project
   if 'CONTENT_S3_ENDPOINT' in values:values['CONTENT_S3_ENDPOINT']=project+'/storage/v1/s3'
   if 'CORS_ORIGINS' in values:values['CORS_ORIGINS']=json.dumps([site])
   if 'PTS_CORS_ORIGINS' in values:values['PTS_CORS_ORIGINS']=site
   path=env/m['env_file'];path.write_text(''.join(k+'='+v+'\n' for k,v in values.items()));path.chmod(0o600)
  registry=json.loads((host.ROOT/'platform/deployment/registry.json').read_text())
  migrations={m['migration']['owner']:m['migration'] for m in manifests if 'migration' in m}
  for group in registry['migration_groups']:
   values={'SUPABASE_URL':project}
   for owner in group['owners']:
    migration=migrations[owner];values[migration['url_env']]=f"postgresql+psycopg://{migration['role']}:fixture@db.stage.supabase.co/postgres?sslmode=require"
   path=env/group['env_file'];path.write_text(''.join(k+'='+v+'\n' for k,v in values.items()));path.chmod(0o600)
  bootstrap={'environment':'staging','supabase_url':project,'schema_fingerprint':host.fingerprint(),'migration_compatibility_fingerprint':host.migration_fingerprint(),**{key:True for key in ['initial_schema_verified','previous_version_compatible','recovery_verified','auth_storage_verified']},'approval_reference':'approved test evidence'}
  (root/'bootstrap.json').write_text(json.dumps(bootstrap));config={'environment':'staging','state_dir':str(root/'state'),'env_dir':str(env),'site':site,'api':'https://api.stage.test','supabase_url':project,'bootstrap_evidence':str(root/'bootstrap.json'),'cert':'fixture','key':'fixture'}
  (root/'config.json').write_text(json.dumps(config));public={key:config[key] for key in ['environment','site','api','supabase_url']};(root/'public.json').write_text(json.dumps(public))
  (root/'images.json').write_text(json.dumps({'sha':'a'*40,'images':{id:'fixture@sha256:'+'0'*64 for id in [m['id'] for m in manifests]+[g['id'] for g in registry['migration_groups']]}}))
  return config,public,manifests
 def studies_target(self,root):
  config,public,manifests=self.setup_target(root)
  access=next(m for m in manifests if m['id']=='access')
  path=host.ROOT/'services/access/studies_readiness.py'
  spec=importlib.util.spec_from_file_location('host_studies_readiness_test',path)
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  artifact={'schema_version':1,'release_id':'synthetic-host-release','identity_revision':'identity_0021','access_revision':'access_0016','service_actor_id':'11111111-1111-4111-8111-111111111111','runtime_sources':module.runtime_hashes(),'qualification_sha256':'a'*64,'profile_hook_qualified':True,'live_provider_qualified':True}
  values=host.env_values(root/'env/access.env')
  values.update(SCRIBESWELL_SERVICE_KEY='synthetic-studies',STUDIES_READINESS_JSON=json.dumps(artifact))
  for field,role in access['studies_enrollment']['database_roles'].items():values[field]=f'postgresql+psycopg://{role}:fixture@db.stage.supabase.co/postgres?sslmode=require'
  return config,public,manifests,values
 def test_studies_enabled_actual_preflight_accepts_prepared_inputs(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);config,public,manifests,values=self.studies_target(root)
   (root/'env/access.env').write_text(''.join(k+'='+v+'\n' for k,v in values.items()))
   host.preflight(config,'staging',manifests,public)
 def test_studies_preflight_refuses_before_release_effects(self):
  fields=('STUDIES_ACCESS_DATABASE_URL','STUDIES_IDENTITY_DATABASE_URL','STUDIES_IDENTITY_SETUP_DATABASE_URL')
  changes=[('missing',name) for name in (*fields,'SCRIBESWELL_SERVICE_KEY','STUDIES_READINESS_JSON')]+[('role',name) for name in fields]+[('project',name) for name in fields]+[('stale','STUDIES_READINESS_JSON')]
  for change,name in changes:
   with self.subTest(change=change,name=name),tempfile.TemporaryDirectory() as d:
    root=Path(d);config,public,manifests,values=self.studies_target(root)
    if change=='missing':values.pop(name)
    elif change=='role':values[name]=values[name].replace(values[name].split('//')[1].split(':')[0],'wrong_runtime')
    elif change=='project':values[name]=values[name].replace('db.stage.supabase.co','db.other.supabase.co')
    else:
     artifact=json.loads(values[name]);artifact['runtime_sources']={};values[name]=json.dumps(artifact)
    (root/'env/access.env').write_text(''.join(k+'='+v+'\n' for k,v in values.items()))
    with patch.object(host,'execute') as execute,patch.object(host,'render') as render,patch.object(host,'require_compose') as compose:
     with self.assertRaises(ValueError):self.deploy(root)
     execute.assert_not_called();render.assert_not_called();compose.assert_not_called()
 def migration_report(self,command,report):
  evidence=Path(command[command.index('-v')+1].removesuffix(':/evidence'))
  (evidence/'migrations.json').write_text(report if isinstance(report,str) else json.dumps(report))
 def deploy(self,root):return host.deploy('staging','a'*40,root/'images.json',root/'config.json',root/'attempt',root/'public.json')
 def success_report(self,command):
  if Path(command[command.index('--env-file')+1]).name!='scribeswell-migrations.env':return {'complete':True,'owners':{}}
  contract=host.scribeswell_contract();expected=contract.from_environ(host.env_values(Path(command[command.index('--env-file')+1])))
  proof=contract.evidence(expected)
  return {'complete':True,'owners':{'scribeswell':{'status':'succeeded','before':'scribeswell_0003','after':'scribeswell_0003','requested_validation':proof,'validation':proof}}}
 def test_scribeswell_revision_only_success_blocks_activation(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.setup_target(root);calls=[]
   def execute(command,**kwargs):
    calls.append(command)
    if command[:2]==['docker','run']:
     self.migration_report(command,{'complete':True,'owners':{'scribeswell':{'status':'succeeded','before':'scribeswell_0003','after':'scribeswell_0003'}}})
   def render(output,*args):output.mkdir();(output/'apisix.yaml').write_text('fake');return {}
   with patch.object(host,'require_compose'),patch.object(host,'render',side_effect=render),patch.object(host.os,'chown'),patch.object(host,'execute',side_effect=execute),patch.object(host.subprocess,'check_output',return_value=''),patch.object(host,'supervisor_events',return_value={}):
    with self.assertRaisesRegex(ValueError,'migration failed'):self.deploy(root)
   report=json.loads((root/'attempt/evidence.json').read_text())
   self.assertFalse(report['activated'])
   self.assertEqual(report['migrations']['pts-owned']['status'],'succeeded')
   self.assertEqual(report['migrations']['scribeswell-owned']['status'],'failed')
   self.assertFalse(any(c[:2]==['docker','compose'] for c in calls))
 def test_catalogue_reference_enters_migration_compatibility_fingerprint(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);app=root/'app';app.mkdir();(app/'alembic.ini').write_text('[alembic]')
   migrations=app/'migrations';migrations.mkdir();(migrations/'env.py').write_text('guard = True')
   reference=migrations/'reference.json';reference.write_text('{"schema":"original"}')
   registry=root/'platform/deployment/registry.json';registry.parent.mkdir(parents=True);registry.write_text('{"migration_groups":[]}')
   with patch.object(host,'ROOT',root),patch.object(host,'load_manifests',return_value=[{'migration':{'config':'app/alembic.ini'}}]):
    before=host.migration_fingerprint();reference.write_text('{"schema":"changed"}')
    self.assertNotEqual(before,host.migration_fingerprint())
 def test_migration_image_inputs_enter_compatibility_fingerprint(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);deployment=root/'platform/deployment';deployment.mkdir(parents=True)
   paths=['app/Migrations.Dockerfile','app/migrate.py','app/database.py','app/requirements.txt','platform/deployment/target_contract.py']
   for name in paths:
    source=root/name;source.parent.mkdir(parents=True,exist_ok=True);source.write_text('original')
   (deployment/'registry.json').write_text(json.dumps({'migration_groups':[{'dockerfile':paths[0],'compatibility_inputs':paths[1:]}]}))
   with patch.object(host,'ROOT',root),patch.object(host,'load_manifests',return_value=[]):
    before=host.migration_fingerprint()
    for name in paths:
     with self.subTest(source=name):
      source=root/name;source.write_text('changed')
      self.assertNotEqual(before,host.migration_fingerprint());source.write_text('original')
    (root/paths[-1]).unlink()
    with self.assertRaises(FileNotFoundError):host.migration_fingerprint()
 def test_real_preflight_accepts_direct_and_ref_qualified_pooler(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);config,public,manifests=self.setup_target(root);host.preflight(config,'staging',manifests,public)
   file=root/'env/pts.env';file.write_text(file.read_text().replace('pts_runtime:','pts_runtime.stage:').replace('db.stage.supabase.co','aws-1-eu-west-1.pooler.supabase.com'));host.preflight(config,'staging',manifests,public)
 def test_preflight_accepts_absent_legacy_jwt_without_dropping_other_inputs(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);config,public,manifests=self.setup_target(root)
   for name in ('directory.env','scribeswell.env'):
    file=root/'env'/name
    file.write_text(''.join(line+'\n' for line in file.read_text().splitlines() if not line.startswith('SUPABASE_JWT_SECRET=')))
   host.preflight(config,'staging',manifests,public)
   file=root/'env/directory.env'
   file.write_text(''.join(line+'\n' for line in file.read_text().splitlines() if not line.startswith('SUPABASE_ANON_KEY=')))
   with self.assertRaisesRegex(ValueError,'missing runtime inputs'):
    host.preflight(config,'staging',manifests,public)
 def test_mixed_projects_roles_missing_migration_and_flags_stop_before_effects(self):
  changes=[('pts.env','db.stage.supabase.co','db.production.supabase.co'),('pts.env','pts_runtime:','postgres:'),('pts.env','db.stage.supabase.co','aws-1-eu-west-1.pooler.supabase.com'),('content.env','https://stage.supabase.co/storage','https://production.supabase.co/storage'),('pts-migrations.env','content_migrator:','postgres:'),('pts-migrations.env','PTS_MIGRATION_DATABASE_URL=','WRONG_KEY='),('scribeswell-migrations.env','scribeswell_migrator:','postgres:'),('scribeswell-migrations.env','db.stage.supabase.co','db.production.supabase.co'),('scribeswell-migrations.env','SCRIBESWELL_MIGRATION_DATABASE_URL=','WRONG_KEY=')]
  for filename,old,new in changes:
   with self.subTest(filename=filename,change=new),tempfile.TemporaryDirectory() as d:
    root=Path(d);self.setup_target(root);file=root/'env'/filename;file.write_text(file.read_text().replace(old,new))
    with patch.object(host,'execute') as docker,patch.object(host,'require_compose') as compose:
     with self.assertRaises(ValueError):self.deploy(root)
     docker.assert_not_called();compose.assert_not_called();self.assertFalse((root/'state').exists())
  for key,value in [('previous_version_compatible','true'),('approval_reference',' ')]:
   with tempfile.TemporaryDirectory() as d:
    root=Path(d);self.setup_target(root);p=root/'bootstrap.json';data=json.loads(p.read_text());data[key]=value;p.write_text(json.dumps(data))
    with self.assertRaises(ValueError):self.deploy(root)
    self.assertFalse((root/'state').exists())
 def test_scribeswell_wrong_role_and_obsolete_service_key_block_activation(self):
  for value in ['SUPABASE_SECRET_KEY=old-secret\n','SUPABASE_SERVICE_ROLE_KEY=old-secret\n']:
   with tempfile.TemporaryDirectory() as d:
    root=Path(d);self.setup_target(root);file=root/'env/scribeswell.env';file.write_text(file.read_text()+value)
    with patch.object(host,'execute') as execute:
     with self.assertRaisesRegex(ValueError,'obsolete runtime authority'):self.deploy(root)
     execute.assert_not_called()
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.setup_target(root);file=root/'env/scribeswell.env';file.write_text(file.read_text().replace('scribeswell_runtime:', 'scribeswell_import:'))
   with patch.object(host,'execute') as execute:
    with self.assertRaisesRegex(ValueError,'database project/role mismatch'):self.deploy(root)
    execute.assert_not_called()
 def test_ci_public_configuration_mismatch_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.setup_target(root);p=root/'public.json';data=json.loads(p.read_text());data['site']='https://wrong.test';p.write_text(json.dumps(data))
   with self.assertRaises(ValueError):self.deploy(root)
   self.assertFalse((root/'state').exists())
 def test_real_coordinator_migration_failure_preserves_report_and_blocks_compose(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.setup_target(root);calls=[]
   def execute(command,**kwargs):
    calls.append(command)
    if command[:2]==['docker','run']:
     (root/'attempt/pts-owned/migrations.json').write_text(json.dumps({'complete':False,'owners':{'access':{'status':'succeeded','before':[],'after':['0001']},'content':{'status':'failed'},'pts':{'status':'not_attempted'}}}));raise RuntimeError('secret-db-password')
   def render(output,*args):output.mkdir();(output/'apisix.yaml').write_text('fake');return {}
   with patch.object(host,'require_compose'),patch.object(host,'render',side_effect=render),patch.object(host.os,'chown'),patch.object(host,'execute',side_effect=execute):
    with self.assertRaises(RuntimeError):self.deploy(root)
   report=json.loads((root/'attempt/evidence.json').read_text());self.assertFalse(report['activated']);self.assertEqual(report['migrations']['pts-owned']['status'],'failed');self.assertEqual(calls[0],['docker','pull',host.APISIX]);self.assertFalse(any(cmd[:2]==['docker','compose'] for cmd in calls));self.assertNotIn('secret-db-password',json.dumps(report))
 def test_supervisor_keeps_forced_termination_warning(self):
  events=json.dumps({'Action':'kill','Actor':{'ID':'old','Attributes':{'signal':'9'}}})+'\n'+json.dumps({'Action':'die','Actor':{'ID':'old','Attributes':{'exitCode':'137'}}})
  with patch.object(host.subprocess,'check_output',side_effect=[events,'new\n']):result=host.supervisor_events('staging',1,['old'])
  self.assertTrue(any(x['code']=='forced_termination' for x in result['warnings']));self.assertEqual(result['events'][1]['exit_code'],'137')
 def test_scribeswell_failure_retains_prior_group_success_and_blocks_activation(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.setup_target(root);calls=[]
   prior={'complete':True,'owners':{owner:{'status':'succeeded','before':[],'after':['0001']} for owner in ('access','content','pts')}}
   failed={'complete':False,'code':'scribeswell_migration_failed','owners':{'scribeswell':{'status':'failed','before':None,'outcome_requires_reconciliation':True}}}
   def execute(command,**kwargs):
    calls.append(command)
    if command[:2]==['docker','run']:
     new_group=Path(command[command.index('--env-file')+1]).name=='scribeswell-migrations.env'
     self.migration_report(command,failed if new_group else prior)
     if new_group:raise RuntimeError('secret-db-password')
   def render(output,*args):output.mkdir();(output/'apisix.yaml').write_text('fake');return {}
   with patch.object(host,'require_compose'),patch.object(host,'render',side_effect=render),patch.object(host.os,'chown'),patch.object(host,'execute',side_effect=execute):
    with self.assertRaises(RuntimeError):self.deploy(root)
   report=json.loads((root/'attempt/evidence.json').read_text())
   self.assertFalse(report['activated'])
   self.assertEqual(report['migrations']['pts-owned']['status'],'succeeded')
   self.assertEqual(report['migrations']['pts-owned']['detail'],prior)
   self.assertEqual(report['migrations']['scribeswell-owned']['status'],'failed')
   self.assertEqual(report['migrations']['scribeswell-owned']['detail'],failed)
   self.assertFalse(any(cmd[:2]==['docker','compose'] for cmd in calls))
   self.assertNotIn('secret-db-password',json.dumps(report))
 def test_activation_failure_preserves_supervisor_forced_stop_evidence(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.setup_target(root)
   def execute(command,**kwargs):
    if command[:2]==['docker','run']:self.migration_report(command,self.success_report(command))
    if command[:2]==['docker','compose']:raise RuntimeError('health failure')
   def render(output,*args):output.mkdir();(output/'apisix.yaml').write_text('fake');return {}
   observed={'events':[{'container_id':'old','action':'kill','signal':'9'}],'warnings':[{'code':'forced_termination','container_id':'old'}]}
   with patch.object(host,'require_compose'),patch.object(host,'render',side_effect=render),patch.object(host.os,'chown'),patch.object(host,'execute',side_effect=execute),patch.object(host.subprocess,'check_output',return_value='old\n'),patch.object(host,'supervisor_events',return_value=observed):
    with self.assertRaises(RuntimeError):self.deploy(root)
   report=json.loads((root/'attempt/evidence.json').read_text());self.assertFalse(report['activated']);self.assertEqual(report['supervisor'],observed)
   pending=json.loads((root/'state/release-pending.json').read_text());self.assertEqual(pending['candidate']['sha'],'a'*40)
 def test_pending_tls_recovery_blocks_all_release_effects(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.setup_target(root);state=root/'state';state.mkdir();(state/'tls-pending.json').write_text('{}')
   with patch.object(host,'require_compose'),patch.object(host,'execute') as execute,patch.object(host,'render') as render:
    with self.assertRaisesRegex(ValueError,'TLS recovery pending'):self.deploy(root)
   execute.assert_not_called();render.assert_not_called();self.assertFalse((root/'attempt').exists())

 def test_success_durably_records_current_then_clears_activation_intent(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.setup_target(root)
   def execute(command,**kwargs):
    if command[:2]==['docker','run']:self.migration_report(command,self.success_report(command))
    if command[:2]==['docker','compose']:self.assertTrue((root/'state/release-pending.json').exists())
   def render(output,*args):output.mkdir();(output/'apisix.yaml').write_text('fake');return {}
   with patch.object(host,'require_compose'),patch.object(host,'render',side_effect=render),patch.object(host.os,'chown'),patch.object(host,'execute',side_effect=execute),patch.object(host.subprocess,'check_output',return_value='old\n'),patch.object(host,'supervisor_events',return_value={}):
    self.deploy(root)
   self.assertFalse((root/'state/release-pending.json').exists());self.assertEqual(json.loads((root/'state/current.json').read_text())['sha'],'a'*40)

 def test_migration_network_lifecycle_and_failure_gates(self):
  for failure in (None,'create','create_timeout','run','timeout','stop','cleanup','cleanup_timeout','absent','detail'):
   with self.subTest(failure=failure),tempfile.TemporaryDirectory() as d:
    root=Path(d);self.setup_target(root);calls=[]
    def execute(command,**kwargs):
     calls.append(command)
     if command[:3]==['docker','network','create']:
      self.assertIn('--ipv6',command);self.assertLessEqual(kwargs['timeout'],30)
      if failure=='create':raise RuntimeError('secret-db-password')
      if failure=='create_timeout':raise host.subprocess.TimeoutExpired(command,30)
     if command[:2]==['docker','run']:
      self.assertTrue(any(c[:3]==['docker','network','create'] for c in calls))
      self.assertEqual(command[command.index('--network')+1],next(c[-1] for c in reversed(calls) if c[:3]==['docker','network','create']))
      if failure!='absent':self.migration_report(command,'invalid' if failure=='detail' else self.success_report(command))
      if failure=='run':raise RuntimeError('secret-db-password')
      if failure in ('timeout','stop'):raise host.subprocess.TimeoutExpired(command,1500)
     if command[:2]==['docker','stop']:
      self.assertLessEqual(kwargs['timeout'],30)
      if failure=='stop':raise RuntimeError('secret-db-password')
     if command[:3]==['docker','network','rm']:
      self.assertLessEqual(kwargs['timeout'],30)
      if failure=='cleanup':raise RuntimeError('secret-db-password')
      if failure=='cleanup_timeout':raise host.subprocess.TimeoutExpired(command,30)
    def render(output,*args):output.mkdir();(output/'apisix.yaml').write_text('fake');return {}
    with patch.object(host,'require_compose'),patch.object(host,'render',side_effect=render),patch.object(host.os,'chown'),patch.object(host,'execute',side_effect=execute),patch.object(host.subprocess,'check_output',return_value=''),patch.object(host,'supervisor_events',return_value={}):
     if failure:
      with self.assertRaises(Exception):self.deploy(root)
     else:self.deploy(root)
    report=json.loads((root/'attempt/evidence.json').read_text());entry=report['migrations']['pts-owned']
    creates=[c for c in calls if c[:3]==['docker','network','create']];removes=[c for c in calls if c[:3]==['docker','network','rm']]
    self.assertEqual(len(creates),len(json.loads((host.ROOT/'platform/deployment/registry.json').read_text())['migration_groups']) if failure is None else 1)
    self.assertNotEqual(creates[0][-1],'bridge')
    self.assertEqual(len(removes),0 if failure in ('create','create_timeout') else len(creates))
    if removes:self.assertEqual([c[-1] for c in removes],[c[-1] for c in creates])
    self.assertEqual(report['activated'],failure is None)
    self.assertEqual(entry['status'],'succeeded' if failure is None else 'failed')
    self.assertEqual(entry['network']['cleanup'],'not_owned' if failure in ('create','create_timeout') else 'failed_or_uncertain' if failure in ('cleanup','cleanup_timeout') else 'removed')
    if failure:self.assertFalse(any(c[:2]==['docker','compose'] for c in calls))
    self.assertNotIn('secret-db-password',json.dumps(report))
    if failure=='absent':self.assertIsNone(entry['detail'])
    if failure in ('timeout','stop'):
     self.assertEqual(entry['supervisor_warning'],'migration_timeout_outcome_requires_reconciliation')
     self.assertEqual(entry['stop_command'],'failed_or_uncertain' if failure=='stop' else 'succeeded')
     self.assertLess(next(i for i,c in enumerate(calls) if c[:2]==['docker','stop']),next(i for i,c in enumerate(calls) if c[:3]==['docker','network','rm']))

    if failure=='create_timeout':
     self.assertEqual(entry['supervisor_warning'],'network_creation_timeout_requires_reconciliation')
     self.assertFalse(any(c[:2] in (['docker','run'],['docker','stop']) for c in calls))

 def test_cleanup_removes_owned_network_when_evidence_save_fails(self):
  for stage in ('cleanup','timeout'):
   with self.subTest(stage=stage),tempfile.TemporaryDirectory() as d:
    root=Path(d);self.setup_target(root);calls=[];failed=[]
    write_text=Path.write_text
    def save_failure(path,text,*args,**kwargs):
     if path==root/'attempt/evidence.tmp' and not failed:
      entry=json.loads(text).get('migrations',{}).get('pts-owned',{})
      if (stage=='cleanup' and entry.get('network',{}).get('cleanup')=='failed_or_uncertain') or (stage=='timeout' and entry.get('supervisor_warning')):
       failed.append(True);raise OSError('evidence persistence failed')
     return write_text(path,text,*args,**kwargs)
    def execute(command,**kwargs):
     calls.append(command)
     if command[:2]==['docker','run']:
      self.migration_report(command,{'complete':True})
      if stage=='timeout':raise host.subprocess.TimeoutExpired(command,1500)
     if command[:2]==['docker','stop']:self.assertLessEqual(kwargs['timeout'],30)
    def render(output,*args):output.mkdir();(output/'apisix.yaml').write_text('fake');return {}
    with patch.object(host,'require_compose'),patch.object(host,'render',side_effect=render),patch.object(host.os,'chown'),patch.object(host,'execute',side_effect=execute),patch.object(Path,'write_text',save_failure):
     with self.assertRaisesRegex(OSError,'evidence persistence failed'):self.deploy(root)
    self.assertEqual(failed,[True])
    created=next(c[-1] for c in reversed(calls) if c[:3]==['docker','network','create'])
    self.assertIn(['docker','network','rm',created],calls)
    self.assertFalse(any(c[:2]==['docker','compose'] for c in calls))
    report=json.loads((root/'attempt/evidence.json').read_text())
    self.assertFalse(report['activated']);self.assertEqual(report['code'],'release_failed_reconcile_before_retry')
    if stage=='timeout':
     self.assertLess(next(i for i,c in enumerate(calls) if c[:2]==['docker','stop']),next(i for i,c in enumerate(calls) if c[:3]==['docker','network','rm']))
