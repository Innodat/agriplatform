"""Find a completed staging run for an exact SHA; download its immutable image evidence."""
import argparse
import json
import os
from pathlib import Path
import re
import urllib.request
import zipfile
import io
p=argparse.ArgumentParser();p.add_argument('--sha',required=True);p.add_argument('--repository',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if not re.fullmatch('[0-9a-f]{40}',a.sha):raise SystemExit('Promotion requires a full commit SHA')
base='https://api.github.com/repos/'+a.repository
# Requests follow signed GitHub artifact redirects without forwarding credentials to storage hosts.
def request(path):
 req=urllib.request.Request(base+path,headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
 return json.load(urllib.request.urlopen(req))
runs=request('/actions/workflows/staging.yml/runs?event=push&status=success&head_sha='+a.sha)['workflow_runs']
for run in runs:
 if run['head_sha']!=a.sha or run['head_branch']!='main' or run['conclusion']!='success':continue
 for artifact in request('/actions/runs/'+str(run['id'])+'/artifacts')['artifacts']:
  if artifact['name']=='staged-'+a.sha and not artifact['expired']:
   # gh delegates authenticated archive download; never put token in command arguments.
   import subprocess
   a.output.mkdir(parents=True,exist_ok=True)
   subprocess.run(['gh','run','download',str(run['id']),'--repo',a.repository,'--name',artifact['name'],'--dir',str(a.output)],check=True)
   evidence=json.loads((a.output/'staged.json').read_text());images=json.loads((a.output/'images.json').read_text())
   if evidence.get('sha')!=a.sha or evidence.get('environment')!='staging' or not evidence.get('complete') or images.get('sha')!=a.sha:raise SystemExit('Invalid staging evidence')
   print('Verified successful staging run '+str(run['id']));raise SystemExit(0)
raise SystemExit('No successful, unexpired staging evidence for this exact SHA')
