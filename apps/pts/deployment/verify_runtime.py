"""PtS build-only frozen runtime custody; no credentials or startup migrations."""
import argparse
import hashlib
import json
import os
import stat
from pathlib import Path

SOURCES=('backend/acquisition.py', 'backend/acquisition_catalogue.json', 'backend/clients.py', 'backend/collection.py', 'backend/contracts.py', 'backend/db.py', 'backend/file_auth.py', 'backend/main.py', 'backend/private_stream.py', 'backend/reader_cache.py', 'backend/research_use.py')
INPUTS=('pyproject.toml','uv.lock',*SOURCES,'deployment/verify_runtime.py','deployment/package_runtime.py','deployment/Dockerfile','deployment/Dockerfile.dockerignore')

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory(root):
    root=root.resolve();result={}
    for folder,dirs,files in os.walk(root,followlinks=False):
        for name in sorted(dirs+files):
            path=Path(folder)/name;relative=path.relative_to(root).as_posix()
            if relative=='provenance.json':continue
            if path.is_symlink():
                if not path.resolve(strict=True).is_relative_to(root):raise ValueError('pts_bundle_link_invalid')
                result[relative]={'link':os.readlink(path)}
            elif path.is_file():result[relative]={'sha256':digest(path)}
            elif not path.is_dir():raise ValueError('pts_bundle_file_invalid')
    return result

def verify(root,bundle):
    manifest=json.loads((bundle/'provenance.json').read_text())
    if set(manifest)!={'schema_version','python_version','uv_version','inputs','files'} or manifest['schema_version']!=1 or manifest['python_version']!='3.15.0' or manifest['uv_version']!='0.13.1':raise ValueError('pts_bundle_invalid')
    if manifest['inputs']!={name:digest(root/name) for name in INPUTS} or manifest['files']!=inventory(bundle):raise ValueError('pts_bundle_stale')
    interpreter=bundle/'python/bin/python3.15'
    required=('python/lib/python3.15/encodings/__init__.py','site-packages/fastapi/__init__.py','site-packages/uvicorn/__init__.py')
    if not interpreter.is_file() or not interpreter.stat().st_mode & stat.S_IXUSR or any(not (bundle/name).is_file() for name in required):raise ValueError('pts_bundle_layout_invalid')
    for name in SOURCES:
        packaged=bundle/'owner-code'/name
        if not packaged.is_file() or digest(packaged)!=manifest['inputs'][name]:raise ValueError('pts_bundle_owner_source_mismatch')
    return manifest

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--bundle',type=Path,required=True);args=parser.parse_args()
    try:verify(args.root,args.bundle)
    except Exception:raise SystemExit('pts_runtime_verification_failed') from None
    print('pts_runtime_verified')
