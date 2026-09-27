"""Install only registered frontend dependencies using owner-selected npm mode."""
import subprocess
from release import ROOT,load_manifests
for app in load_manifests():
 frontend=app.get('frontend')
 if not frontend:continue
 mode=frontend['install']
 args=['npm','ci','--prefix',frontend['path']] if mode=='prefix' else ['npm','ci','--workspace='+frontend['path'],'--include-workspace-root']
 subprocess.run(args,cwd=ROOT,check=True)
