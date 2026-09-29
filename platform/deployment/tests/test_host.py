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
  path=env/'pts-migrations.env';path.write_text('SUPABASE_URL='+project+'\n'+''.join(f'{owner.upper()}_MIGRATION_DATABASE_URL=postgresql+psycopg://{owner}_migrator:fixture@db.stage.supabase.co/postgres?sslmode=require\n' for owner in ['access','content','pts']));path.chmod(0o600)
  bootstrap={'environment':'staging','supabase_url':project,'schema_fingerprint':host.fingerprint(),'migration_compatibility_fingerprint':host.migration_fingerprint(),**{key:True for key in ['initial_schema_verified','previous_version_compatible','recovery_verified','auth_storage_verified']},'approval_reference':'approved test evidence'}
  (root/'bootstrap.json').write_text(json.dumps(bootstrap));config={'environment':'staging','state_dir':str(root/'state'),'env_dir':str(env),'site':site,'api':'https://api.stage.test','supabase_url':project,'bootstrap_evidence':str(root/'bootstrap.json'),'cert':'fixture','key':'fixture'}
  (root/'config.json').write_text(json.dumps(config));public={key:config[key] for key in ['environment','site','api','supabase_url']};(root/'public.json').write_text(json.dumps(public))
  (root/'images.json').write_text(json.dumps({'sha':'a'*40,'images':{id:'fixture@sha256:'+'0'*64 for id in ['pts','access','content','directory','scribeswell','pts-owned']}}))
  return config,public,manifests
 def deploy(self,root):return host.deploy('staging','a'*40,root/'images.json',root/'config.json',root/'attempt',root/'public.json')
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
  changes=[('pts.env','db.stage.supabase.co','db.production.supabase.co'),('pts.env','pts_runtime:','postgres:'),('pts.env','db.stage.supabase.co','aws-1-eu-west-1.pooler.supabase.com'),('content.env','https://stage.supabase.co/storage','https://production.supabase.co/storage'),('pts-migrations.env','content_migrator:','postgres:'),('pts-migrations.env','PTS_MIGRATION_DATABASE_URL=','WRONG_KEY=')]
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
 def test_activation_failure_preserves_supervisor_forced_stop_evidence(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.setup_target(root)
   def execute(command,**kwargs):
    if command[:2]==['docker','run']:(root/'attempt/pts-owned/migrations.json').write_text(json.dumps({'complete':True,'owners':{}}))
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
    if command[:2]==['docker','run']:(root/'attempt/pts-owned/migrations.json').write_text(json.dumps({'complete':True,'owners':{}}))
    if command[:2]==['docker','compose']:self.assertTrue((root/'state/release-pending.json').exists())
   def render(output,*args):output.mkdir();(output/'apisix.yaml').write_text('fake');return {}
   with patch.object(host,'require_compose'),patch.object(host,'render',side_effect=render),patch.object(host.os,'chown'),patch.object(host,'execute',side_effect=execute),patch.object(host.subprocess,'check_output',return_value='old\n'),patch.object(host,'supervisor_events',return_value={}):
    self.deploy(root)
   self.assertFalse((root/'state/release-pending.json').exists());self.assertEqual(json.loads((root/'state/current.json').read_text())['sha'],'a'*40)
