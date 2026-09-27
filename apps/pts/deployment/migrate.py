"""Scoped, bounded adapter: access -> content -> PtS only; no activation."""
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'tools/py'))
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'platform/deployment'))
from target_contract import database_url
from deploy_pts import OWNERS, deployment_lock, revisions

def main(target=Path('/evidence/migrations.json'),run=subprocess.run,acquire_lock=deployment_lock,inspect=revisions,environ=None):
 environ=os.environ if environ is None else environ
 report={'owners':{owner:{'status':'not_attempted'} for owner,_ in OWNERS},'complete':False}
 def save():
  temporary=target.with_suffix('.tmp');temporary.write_text(json.dumps(report,indent=2)+'\n');temporary.replace(target)
 save()
 try:
  # Validate every authority before locking or running the first owner.
  project=environ['SUPABASE_URL']
  for owner,_ in OWNERS:database_url(environ[owner.upper()+'_MIGRATION_DATABASE_URL'],project,owner+'_migrator')
  for owner,_ in OWNERS:
   field=owner.upper()+'_MIGRATION_DATABASE_URL';url=urlsplit(environ[field]);query=dict(parse_qsl(url.query));query.update(connect_timeout='5',options='-c lock_timeout=10000 -c statement_timeout=120000')
   environ[field]=urlunsplit(url._replace(query=urlencode(query)))
  with acquire_lock():
   for owner,folder in OWNERS:
    entry=report['owners'][owner];entry['status']='running';save()
    try:
     entry['before']=inspect(owner);save()
     run([sys.executable,'-m','alembic','-c',folder+'/alembic.ini','upgrade','head'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=180,env=dict(environ))
     entry.update(status='succeeded',after=inspect(owner));save()
    except Exception:
     entry.update(status='failed',outcome_requires_reconciliation=True)
     try:entry['after']=inspect(owner)
     except Exception:entry['after']=None
     save();raise
  report['complete']=True;save()
 except Exception:
  report['code']='migration_failed';save();raise SystemExit(1) from None
if __name__=='__main__':main()
