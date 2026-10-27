"""Explicit offline Access production packaging from this owner's frozen lock."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_runtime import INPUTS,SOURCES,digest,inventory,verify

def package(root,python,uv,cache,output):
    root=root.resolve();output=output.absolute()
    if output.exists() or output.is_symlink():raise ValueError('access_package_output_exists')
    if not all(p.is_absolute() and p.exists() for p in (python,uv,cache)) or output.parent.is_symlink():raise ValueError('access_package_inputs_invalid')
    if not python.is_file() or not uv.is_file() or not cache.is_dir():raise ValueError('access_package_inputs_invalid')
    before={name:digest(root/name) for name in INPUTS}
    clean={'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8','UV_CACHE_DIR':str(cache),'UV_PYTHON_DOWNLOADS':'never','UV_OFFLINE':'1','PYTHONDONTWRITEBYTECODE':'1'}
    def run(argv,environment=clean):
        result=subprocess.run([str(x) for x in argv],cwd=root,env=environment,capture_output=True,text=True,timeout=180)
        if result.returncode:raise ValueError('access_package_tool_failed')
        return result.stdout.strip()
    selected=json.loads(run([python,'-I','-B','-c','import json,sys,platform;print(json.dumps({"version":platform.python_version(),"prefix":sys.base_prefix}))']))
    if selected['version']!='3.15.0' or run([uv,'--version']).split()[:2]!=['uv','0.13.1']:raise ValueError('access_package_tool_version_invalid')
    output.parent.mkdir(parents=True,exist_ok=True)
    # Failed work is retained; output is published only after complete verification.
    work=Path(tempfile.mkdtemp(prefix='.production-access-',dir=output.parent))
    environment=work/'environment';candidate=work/'runtime-bundle';candidate.mkdir()
    env={**clean,'UV_PROJECT_ENVIRONMENT':str(environment)}
    run([uv,'sync','--frozen','--no-dev','--offline','--python',python,'--project',root],env)
    site=environment/'lib/python3.15/site-packages'
    if not site.is_dir():raise ValueError('access_package_environment_invalid')
    shutil.copytree(Path(selected['prefix']),candidate/'python',symlinks=True,ignore=shutil.ignore_patterns('site-packages','dist-packages','__pycache__','*.pyc'))
    shutil.copytree(site,candidate/'site-packages',symlinks=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    code=candidate/'owner-code';code.mkdir()
    for name in SOURCES:shutil.copy2(root/name,code/name)
    if before!={name:digest(root/name) for name in INPUTS}:raise ValueError('access_package_source_changed')
    manifest={'schema_version':1,'python_version':'3.15.0','uv_version':'0.13.1','inputs':before,'files':inventory(candidate)}
    (candidate/'provenance.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    verify(root,candidate)
    os.rename(candidate,output)
    return manifest

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--python',type=Path,required=True);parser.add_argument('--uv',type=Path,required=True);parser.add_argument('--cache',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    try:package(Path(__file__).resolve().parents[1],args.python,args.uv,args.cache,args.output)
    except Exception:raise SystemExit('access_runtime_packaging_failed') from None
    print('access_runtime_packaged')

if __name__=='__main__':main()
