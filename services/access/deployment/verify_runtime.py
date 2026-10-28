"""Access build-only frozen runtime custody; no credentials or startup migrations."""
import argparse
import hashlib
import json
import os
import stat
from pathlib import Path

SOURCES=('main.py','organization_check.py','studies_access.py','studies_identity.py','studies_contract.py','studies_readiness.py','identity_preferences.py','caller_policy.py','capability_contract.py','capability_check.py','identity_context.py','discovery.py','discovery_contract.py','discovery_query.py','actor_display_runtime.py','actor_display_http.py','actor_display_contract.py','actor_display_native.py')
INPUTS=('pyproject.toml','uv.lock',*SOURCES,'deployment/verify_runtime.py','deployment/package_runtime.py','deployment/Dockerfile','deployment/Dockerfile.dockerignore')

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory(root):
    root=root.resolve();result={}
    for folder,dirs,files in os.walk(root,followlinks=False):
        for name in sorted(dirs+files):
            path=Path(folder)/name;relative=path.relative_to(root).as_posix()
            if relative=='provenance.json':continue
            if path.is_symlink():
                if not path.resolve(strict=True).is_relative_to(root):raise ValueError('access_bundle_link_invalid')
                result[relative]={'link':os.readlink(path)}
            elif path.is_file():result[relative]={'sha256':digest(path)}
            elif not path.is_dir():raise ValueError('access_bundle_file_invalid')
    return result

def verify(root,bundle):
    manifest=json.loads((bundle/'provenance.json').read_text())
    if set(manifest)!={'schema_version','python_version','uv_version','inputs','files'} or manifest['schema_version']!=1 or manifest['python_version']!='3.15.0' or manifest['uv_version']!='0.13.1':raise ValueError('access_bundle_invalid')
    if manifest['inputs']!={name:digest(root/name) for name in INPUTS} or manifest['files']!=inventory(bundle):raise ValueError('access_bundle_stale')
    interpreter=bundle/'python/bin/python3.15'
    required=('python/lib/python3.15/encodings/__init__.py','site-packages/fastapi/__init__.py','site-packages/uvicorn/__init__.py')
    if not interpreter.is_file() or not interpreter.stat().st_mode & stat.S_IXUSR or any(not (bundle/name).is_file() for name in required):raise ValueError('access_bundle_layout_invalid')
    for name in SOURCES:
        packaged=bundle/'owner-code'/name
        if not packaged.is_file() or digest(packaged)!=manifest['inputs'][name]:raise ValueError('access_bundle_owner_source_mismatch')
    return manifest

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--bundle',type=Path,required=True);args=parser.parse_args()
    try:verify(args.root,args.bundle)
    except Exception:raise SystemExit('access_runtime_verification_failed') from None
    print('access_runtime_verified')
