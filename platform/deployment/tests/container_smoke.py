"""Run prebuilt images without external networking, using fixture credentials only."""
import argparse
import json
import subprocess
import time
import uuid
import sys
sys.path.insert(0,str(__import__('pathlib').Path(__file__).parents[1]))
from release import load_manifests
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--images',type=Path);inputs=parser.parse_args()
images=json.loads(inputs.images.read_text())['images'] if inputs.images else {}
MANIFESTS=load_manifests()

for manifest in MANIFESTS:
 name=manifest['id']
 container='release-smoke-'+name+'-'+uuid.uuid4().hex[:8]
 args=['docker','run','-d','--name',container,'--network','none','--read-only','--tmpfs','/tmp','--cap-drop','ALL','--security-opt','no-new-privileges:true']
 # Fake inputs only; production uses owner-specific env files, never this union.
 for key,value in manifest['smoke_env'].items():args+=['-e',key+'='+value]
 args+=[images.get(name,'agriplatform-'+name+':release-check')]
 try:
  subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
  for _ in range(45):
   result=subprocess.run(['docker','exec',container,'python','-c',"import urllib.request; urllib.request.urlopen("+repr('http://127.0.0.1:8000'+manifest['health_path'])+",timeout=2)"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   if result.returncode==0:break
   time.sleep(1)
  assert result.returncode==0,name+' health failed'
  uid=subprocess.check_output(['docker','exec',container,'id','-u'],text=True).strip();assert uid!='0'
  subprocess.run(['docker','exec',container,'python','-c',"from pathlib import Path; assert not list(Path('/app').rglob('.env*')); assert not Path('/app/apps/pts/reference').exists()"],check=True)
  for artifact in manifest.get('smoke_artifacts',[]):subprocess.run(['docker','exec',container,'python','-c',"from pathlib import Path; assert Path("+repr(artifact)+").exists()"],check=True)
  print(name+': non-root healthy with no outbound network, required artifacts present, private env/archive absent')
 finally:subprocess.run(['docker','rm','-f',container],check=True,stdout=subprocess.DEVNULL)
