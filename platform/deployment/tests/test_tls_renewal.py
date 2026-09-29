import fcntl
import hashlib
import http.server
import importlib.util
import json
import os
from pathlib import Path
import signal
import ssl
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch

PATH=Path(__file__).resolve().parents[1]/'tls/renew.py'
spec=importlib.util.spec_from_file_location('renewal',PATH)
renewal=importlib.util.module_from_spec(spec);spec.loader.exec_module(renewal)

class AdoptionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name);self.state=self.root/'state';self.state.mkdir()
  self.cert=self.root/'cert';self.cert.write_text('new cert');self.key=self.root/'key';self.key.write_text('new key')
  self.config={'environment':'production','api':'https://api.example.test','state_dir':str(self.state),'cert':str(self.root/'installed/cert'),'key':str(self.root/'installed/key')}
  for name in ['validate','leaf_fingerprint','protect_gateway','verify_retry','activate']:
   mocked=patch.object(renewal,name,return_value='fingerprint');setattr(self,name,mocked.start());self.addCleanup(mocked.stop)
 def active(self,certificate='old cert'):
  old=self.root/'old';old.mkdir();(old/'config.yaml').write_text('{}')
  (old/'apisix.yaml').write_text(json.dumps({'routes':[{'id':'preserve'}],'ssls':[{'id':'api','cert':certificate,'key':'old key'}]})+'\n#END\n')
  compose={'name':'agriplatform-production','services':{'api':{'image':'unchanged'},'gateway':{'image':'same','volumes':[str(old/'config.yaml')+':/usr/local/apisix/conf/config.yaml:ro',str(old/'apisix.yaml')+':/usr/local/apisix/conf/apisix.yaml:ro']}}}
  (old/'compose.json').write_text(json.dumps(compose))
  current={'sha':'a'*40,'images':{'api':'digest'},'compose':str(old/'compose.json'),'evidence':'prior'}
  (self.state/'current.json').write_text(json.dumps(current));return current,compose
 def evidence(self):return json.loads(sorted(self.state.glob('tls-[0-9]*.json'))[-1].read_text())
 def test_pre_activation_only_installs_verified_copies(self):
  self.assertEqual(renewal.install(self.config,self.cert,self.key)['outcome'],'pending_gateway_activation')
  self.activate.assert_not_called();self.assertEqual(Path(self.config['key']).read_text(),'new key')
 def test_active_preserves_services_routes_and_release_identity(self):
  old,compose=self.active();renewal.install(self.config,self.cert,self.key)
  current=json.loads((self.state/'current.json').read_text());new=json.loads(Path(current['compose']).read_text())
  self.assertEqual(current['sha'],old['sha']);self.assertEqual(current['images'],old['images']);self.assertEqual(new['services']['api'],compose['services']['api'])
  doc=json.loads((Path(current['compose']).parent/'apisix.yaml').read_text().removesuffix('\n#END\n'))
  self.assertEqual(doc['routes'],[{'id':'preserve'}]);self.verify_retry.assert_called_once()
 def test_same_leaf_changed_chain_still_activates(self):
  self.active();renewal.install(self.config,self.cert,self.key)
  self.activate.assert_called_once() # mocked old/new leaf identity is deliberately equal
 def test_failure_restores_exact_prior_gateway_and_pointer(self):
  old,_=self.active();self.verify_retry.side_effect=[renewal.Failure('served_mismatch'),None]
  with self.assertRaises(renewal.Failure):renewal.install(self.config,self.cert,self.key)
  self.assertEqual(json.loads((self.state/'current.json').read_text()),old)
  self.assertEqual(self.activate.call_args_list[-1].args[0],Path(old['compose']))
  self.assertEqual(self.evidence()['recovery'],'verified');self.assertEqual(self.evidence()['code'],'served_mismatch')
 def test_second_installed_copy_failure_restores_previous_pair(self):
  for field in ['cert','key']:
   path=Path(self.config[field]);path.parent.mkdir(exist_ok=True);path.write_text('previous '+field)
  original=renewal.atomic
  def fail_second(path,content,*args,**kwargs):
   if path==Path(self.config['key']) and content==b'new key':raise OSError('sensitive external diagnostic')
   return original(path,content,*args,**kwargs)
  with patch.object(renewal,'atomic',side_effect=fail_second):
   with self.assertRaises(renewal.Failure):renewal.install(self.config,self.cert,self.key)
  for field in ['cert','key']:self.assertEqual(Path(self.config[field]).read_text(),'previous '+field)
  self.assertNotIn('sensitive',json.dumps(self.evidence()))
  self.assertFalse((self.state/'tls-pending.json').exists())
 def test_interruption_after_gateway_mutation_recovers_and_has_prior_intent(self):
  old,_=self.active();control=renewal.Control()
  def activation(path,budget):
   self.assertTrue((self.state/'tls-pending.json').exists())
   if path!=Path(old['compose']):os.kill(os.getpid(),signal.SIGTERM)
  self.activate.side_effect=activation
  previous_handler=signal.signal(signal.SIGTERM,control.stop)
  try:
   with self.assertRaises(renewal.Failure):renewal.install(self.config,self.cert,self.key,control)
  finally:signal.signal(signal.SIGTERM,previous_handler)
  self.assertEqual(self.activate.call_args_list[-1].args[0],Path(old['compose']))
  self.assertEqual(json.loads((self.state/'current.json').read_text()),old)
  self.assertTrue(self.evidence()['interrupted']);self.assertEqual(self.evidence()['recovery'],'verified')
 def test_failed_recovery_is_reconciled_before_retrying_adoption(self):
  old,_=self.active();self.verify_retry.side_effect=[renewal.Failure('api_route_health'),renewal.Failure('served_connection')]
  with self.assertRaises(renewal.Failure):renewal.install(self.config,self.cert,self.key)
  self.assertTrue((self.state/'tls-pending.json').exists());self.assertEqual(self.evidence()['recovery'],'failed')
  self.verify_retry.side_effect=None;self.validate.reset_mock()
  report=renewal.install(self.config,self.cert,self.key)
  self.assertEqual(report['outcome'],'recovered_retry_required');self.validate.assert_not_called()
  self.assertEqual(self.activate.call_args_list[-1].args[0],Path(old['compose']))
  self.assertFalse((self.state/'tls-pending.json').exists())
  self.assertEqual(renewal.install(self.config,self.cert,self.key)['outcome'],'activated')
 def test_busy_lock_does_not_replace_copies(self):
  with (self.state/'release.lock').open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   with self.assertRaises(renewal.Failure):renewal.install(self.config,self.cert,self.key)
  self.validate.assert_not_called();self.assertEqual(self.evidence()['code'],'release_busy')
 def test_invalid_certificate_does_not_replace_copies(self):
  self.validate.side_effect=renewal.Failure('certificate_trust')
  with self.assertRaises(renewal.Failure):renewal.install(self.config,self.cert,self.key)
  self.assertFalse(Path(self.config['key']).exists());self.assertEqual(self.evidence()['code'],'certificate_trust')

class ProductionVerificationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  from tls_fixture import certificates
  cls.temp=tempfile.TemporaryDirectory();cls.root=Path(cls.temp.name)
  cls.ca,cls.key,cls.leaf,cls.chain,cls.short=certificates(cls.root)
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_unpadded_leaf_fingerprint_excludes_remaining_chain(self):
  leaf=ssl.PEM_cert_to_DER_cert(self.leaf.read_text())
  self.assertEqual(len(leaf)%3,0)
  self.assertEqual(renewal.leaf_fingerprint(self.chain),hashlib.sha256(leaf).hexdigest())
 def test_real_validation_has_safe_error_categories(self):
  with patch.dict(os.environ,{'SSL_CERT_FILE':str(self.ca)}):
   self.assertEqual(renewal.validate(self.chain,self.key,'api.example.test'),renewal.leaf_fingerprint(self.leaf))
   for args,code in [((self.chain,self.key,'wrong.test'),'certificate_hostname'),((self.chain,self.root/'ca.key','api.example.test'),'certificate_key_mismatch'),((self.short,self.key,'api.example.test'),'certificate_expiry')]:
    with self.assertRaises(renewal.Failure) as raised:renewal.validate(*args)
    self.assertEqual(raised.exception.code,code)
  with patch.dict(os.environ,{'SSL_CERT_FILE':'/nonexistent-test-ca'}):
   with self.assertRaises(renewal.Failure) as raised:renewal.validate(self.chain,self.key,'api.example.test')
   self.assertEqual(raised.exception.code,'certificate_trust')
 def test_production_verifier_accepts_real_tls_and_rejects_mismatch_bad_route_and_untrusted(self):
  received=[];status=[200]
  class Handler(http.server.BaseHTTPRequestHandler):
   def do_GET(self):
    received.append(self.path);self.send_response(status[0]);self.end_headers()
   def log_message(self,*args):pass
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
  context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(self.chain,self.key)
  server.socket=context.wrap_socket(server.socket,server_side=True)
  thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   api='https://api.example.test:'+str(server.server_port);fingerprint=renewal.leaf_fingerprint(self.chain)
   with patch.dict(os.environ,{'SSL_CERT_FILE':str(self.ca)}):
    renewal.verify_served(api,fingerprint)
    self.assertEqual(received,['/directory/api/apps'])
    with self.assertRaises(renewal.Failure) as raised:renewal.verify_served(api,'0'*64)
    self.assertEqual(raised.exception.code,'served_fingerprint')
    status[0]=503
    with self.assertRaises(renewal.Failure) as raised:renewal.verify_served(api,fingerprint)
    self.assertEqual(raised.exception.code,'api_route_health')
   with patch.dict(os.environ,{'SSL_CERT_FILE':'/nonexistent-test-ca'}):
    with self.assertRaises(renewal.Failure) as raised:renewal.verify_served(api,fingerprint)
    self.assertEqual(raised.exception.code,'served_trust')
  finally:
   server.shutdown();server.server_close();thread.join(timeout=2)

class ReviewRegressions(unittest.TestCase):
 setUp=AdoptionTests.setUp
 active=AdoptionTests.active
 evidence=AdoptionTests.evidence
 def test_diagnostic_write_failure_never_skips_recovery(self):
  old,_=self.active();real_save=renewal.save
  self.verify_retry.side_effect=[renewal.Failure('api_route_health'),None]
  def failing_diagnostic(path,document):
   if document.get('recovery')=='failed':raise OSError('private disk detail')
   return real_save(path,document)
  with patch.object(renewal,'save',side_effect=failing_diagnostic):
   with self.assertRaises(renewal.Failure) as error:renewal.install(self.config,self.cert,self.key)
  self.assertEqual(error.exception.code,'api_route_health')
  self.assertEqual(self.activate.call_args_list[-1].args[0],Path(old['compose']))
  self.assertFalse((self.state/'tls-pending.json').exists())
 def test_unchanged_pre_activation_and_active_create_no_backups(self):
  renewal.install(self.config,self.cert,self.key)
  self.assertEqual(list(self.state.glob('tls-backup-*')),[])
  with patch.object(renewal,'install_pair') as pair:
   renewal.install(self.config,self.cert,self.key);pair.assert_not_called()
  self.active();renewal.install(self.config,self.cert,self.key)
  self.assertEqual(list(self.state.glob('tls-backup-*')),[])
  self.activate.reset_mock()
  with patch.object(renewal,'install_pair') as pair:
   renewal.install(self.config,self.cert,self.key);pair.assert_not_called()
  self.activate.assert_not_called()
 def test_failed_recovery_preserves_safe_error_codes(self):
  self.active();self.verify_retry.side_effect=[renewal.Failure('api_route_health'),renewal.Failure('served_trust')]
  with self.assertRaises(renewal.Failure):renewal.install(self.config,self.cert,self.key)
  self.assertEqual(self.evidence()['code'],'api_route_health');self.assertEqual(self.evidence()['recovery_code'],'served_trust')
  self.verify_retry.side_effect=renewal.Failure('served_fingerprint')
  with self.assertRaises(renewal.Failure):renewal.install(self.config,self.cert,self.key)
  self.assertEqual(self.evidence()['prior_recovery_code'],'served_fingerprint')
 def test_uncertain_release_blocks_tls_before_effects(self):
  (self.state/'release-pending.json').write_text('{}')
  with self.assertRaises(renewal.Failure) as error:renewal.install(self.config,self.cert,self.key)
  self.assertEqual(error.exception.code,'release_activation_pending');self.validate.assert_not_called();self.activate.assert_not_called()
 def test_routine_evidence_is_bounded_but_recovery_references_survive(self):
  protected=self.state/'tls-1.json';protected.write_text(json.dumps({'outcome':'already_active'}))
  (self.state/'current.json').write_text(json.dumps({'tls_evidence':str(protected)}))
  failed=self.state/'tls-2.json';failed.write_text(json.dumps({'outcome':'failed','recovery':'failed'}))
  for number in range(3,110):(self.state/f'tls-{number}.json').write_text(json.dumps({'outcome':'already_active'}))
  renewal.prune_evidence(self.state)
  self.assertTrue(protected.exists());self.assertTrue(failed.exists());self.assertLessEqual(len(list(self.state.glob('tls-*.json'))),98)

 def test_docker_timeout_retains_intent_even_after_recovery_probe_succeeds(self):
  self.active();self.activate.side_effect=[renewal.Failure('command_timeout'),None]
  with self.assertRaises(renewal.Failure):renewal.install(self.config,self.cert,self.key)
  self.assertTrue(json.loads((self.state/'tls-pending.json').read_text())['docker_state_uncertain'])
  self.assertEqual(self.evidence()['code'],'command_timeout');self.assertEqual(self.evidence()['recovery_code'],'docker_state_uncertain')
