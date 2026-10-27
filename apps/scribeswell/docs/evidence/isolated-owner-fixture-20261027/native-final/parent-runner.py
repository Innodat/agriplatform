from pathlib import Path
import json,subprocess,socket,time,ipaddress,os
base=Path(__file__).resolve().parent
plan=json.loads((base/'plan.json').read_text())
for port in [5192,8192,8193,55490,55491,55492,55493,15494,8447]:
 with socket.socket() as sock:sock.bind(('127.0.0.1',port))
ids=subprocess.check_output(['docker','network','ls','--quiet'],text=True).split()
if ids:
 for network in json.loads(subprocess.check_output(['docker','network','inspect',*ids],text=True)):
  for c in network.get('IPAM',{}).get('Config',[]) or []:
   subnet=c.get('Subnet')
   if subnet and ipaddress.ip_network(subnet).version==4 and ipaddress.ip_network('10.254.27.0/24').overlaps(ipaddress.ip_network(subnet)):raise RuntimeError('isolated_subnet_occupied')
cmd=[plan['python'],'apps/scribeswell/tools/py/qualify_studies_owner_integration.py','--run-id',plan['run_id'],'--supabase',plan['supabase'],'--proof',plan['proof']]
started=time.monotonic();r=subprocess.run(cmd,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
result={'command':cmd,'exit_code':r.returncode,'elapsed_seconds':round(time.monotonic()-started,2),'proof':plan['proof'],'run_id':plan['run_id']}
(base/('result-'+plan['run_id']+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));raise SystemExit(r.returncode)
