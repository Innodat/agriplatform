import json
import importlib.util
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).parents[1]))
spec=importlib.util.spec_from_file_location('gateway',Path(__file__).parents[1]/'render_gateway.py')
gateway=importlib.util.module_from_spec(spec);spec.loader.exec_module(gateway)
class Routing(unittest.TestCase):
 def test_routes_are_host_and_tls_scoped(self):
  routes=gateway.routes()
  self.assertEqual(len(routes),3)
  for route in routes:
   self.assertEqual(route['host'],'api.scribeswell.com')
   self.assertIn(['scheme','==','https'],route['vars'])
   self.assertEqual(route['methods'],['GET','OPTIONS'])
   self.assertEqual(route['plugins']['cors']['allow_origins'],'https://scribeswell.com')
  self.assertEqual(next(r for r in routes if r['id']=='directory')['uris'],['/directory/api/apps','/directory/api/me/apps','/directory/api/me/context'])
if __name__=='__main__':unittest.main()

class ComposeContract(unittest.TestCase):
 def test_compose_raw_environment_version_gate(self):
  from unittest.mock import patch
  with patch.object(gateway.subprocess,'check_output',return_value='2.29.9'):
   with self.assertRaises(ValueError):gateway.require_compose()
  with patch.object(gateway.subprocess,'check_output',return_value='v2.30.0'):self.assertEqual(gateway.require_compose(),'2.30.0')
 def test_methods_follow_manifest_and_healthcheck_uses_declared_path(self):
  manifests=gateway.load_manifests();m=next(x for x in manifests if 'public' in x);m['public']['methods']=['POST','OPTIONS']
  route=gateway.routes(manifests=[m])[0];self.assertEqual(route['methods'],['POST','OPTIONS']);self.assertEqual(route['plugins']['cors']['allow_methods'],'POST,OPTIONS')
 def test_rendered_services_have_declared_health_and_raw_env_files(self):
  import tempfile
  from unittest.mock import patch
  manifests=gateway.load_manifests();manifests[0]['health_path']='/custom-health'
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);env=root/'env';env.mkdir();cert=root/'cert';cert.write_text('fixture');key=root/'key';key.write_text('fixture')
   for m in manifests:(env/m['env_file']).write_text('PASSWORD=literal$dollar${VALUE}$$\n')
   with patch.object(gateway,'load_manifests',return_value=manifests),patch.object(gateway.subprocess,'run') as run,patch.object(gateway.subprocess,'check_output',return_value=b'publickey') as capture:
    services=gateway.render(root/'out',env,{m['id']:'fixture@sha256:'+'0'*64 for m in manifests},'https://stage.test','https://api.stage.test',cert,key,'staging')
   self.assertEqual(len(run.call_args_list)+len(capture.call_args_list),4)
   for call in [*run.call_args_list,*capture.call_args_list]:self.assertEqual(call.kwargs['timeout'],10)
   self.assertIn('/custom-health',services[manifests[0]['id']]['healthcheck']['test'][-1]);self.assertEqual(services[manifests[0]['id']]['env_file'][0]['format'],'raw')

   compose=json.loads((root/'out/compose.json').read_text())
   self.assertEqual(compose['networks'],{'default':{'enable_ipv6':True}})
   self.assertEqual({name for name,service in services.items() if service.get('ports')},{'gateway'})
   self.assertFalse(any(service.get('network_mode') for service in services.values()))
