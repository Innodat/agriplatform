"""Build silo images, recording registry digests for exact promotion. CI only."""
import argparse
import json
from pathlib import Path
import re
import subprocess
from release import ROOT,load_manifests
p=argparse.ArgumentParser();p.add_argument('--sha',required=True);p.add_argument('--repository',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--push',action='store_true');a=p.parse_args()
if not re.fullmatch('[0-9a-f]{40}',a.sha) or not re.fullmatch('[a-z0-9-]+/[a-z0-9_.-]+',a.repository):raise SystemExit('Invalid immutable build identity')
registry=json.loads((ROOT/'platform/deployment/registry.json').read_text());images={}
for m in [*load_manifests(),*registry.get('migration_groups',[])]:
 tag=f"ghcr.io/{a.repository}/{m['id']}:{a.sha}"
 subprocess.run(['docker','build','--pull','-f',m['dockerfile'],'-t',tag,'.'],cwd=ROOT,check=True)
 if a.push:
  subprocess.run(['docker','push',tag],check=True)
  digests=json.loads(subprocess.check_output(['docker','image','inspect',tag,'--format','{{json .RepoDigests}}'],text=True))
  images[m['id']]=next(d for d in digests if d.startswith(tag.rsplit(':',1)[0]+'@sha256:'))
 else:images[m['id']]=tag
 a.output.write_text(json.dumps({'sha':a.sha,'images':images},indent=2)+'\n')
