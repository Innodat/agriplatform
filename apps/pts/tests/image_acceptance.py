"""Package and exercise a fresh PtS runtime image with isolated owner services."""
import hashlib
import json
from pathlib import Path
import socket
import sys
from apps.pts.tests.integration_fixture import ROOT,private


def runtime_image_mode(phase,binding):
    if binding:
        if phase not in ('cleanup','image-resources','image-session-races'):raise ValueError('runtime_image_reuse_requires_qualified_phase')
        return 'reuse'
    return 'prepare' if phase in ('image-browser','image-resources','image-session-races') else None


def bundle_for_binding(receipt):
    name=receipt.get('bundle_path','apps/pts/runtime-bundle')
    assert isinstance(name,str) and not Path(name).is_absolute() and '..' not in Path(name).parts,'runtime_bundle_custody_invalid'
    candidate=ROOT/name;bundle=candidate.resolve(strict=True)
    assert candidate==bundle and (bundle==ROOT/'apps/pts/runtime-bundle' or bundle.is_relative_to(ROOT/'platform/deployment/.local/e1-pts-adoption')),'runtime_bundle_custody_invalid'
    assert bundle.is_dir(),'runtime_bundle_custody_invalid'
    return bundle


def reuse(f,binding):
    """Use an immutable qualified image; never restart a retained container."""
    from apps.pts.deployment.verify_runtime import verify
    f.guard();path=Path(binding).resolve()
    assert path.is_relative_to(ROOT/'platform/deployment/.local/e1-pts-adoption') and not path.is_relative_to(f.out)
    receipt=json.loads(path.read_text());bundle=bundle_for_binding(receipt)
    verify(ROOT/'apps/pts',bundle)
    assert hashlib.sha256((bundle/'provenance.json').read_bytes()).hexdigest()==receipt['bundle_provenance_sha256']
    selected=json.loads(f.docker('image','inspect',receipt['image_id']))[0]
    assert selected['Id']==receipt['image_id'] and selected['Config']['User']=='65532:65532'
    f.runtime_image=selected['Id']
    private(f.out/'runtime-image-binding.json',{**receipt,'reused_binding':str(path.relative_to(ROOT)),
        'reused_binding_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'retained_container_restarted':False})
    f.checks.append('same-frozen-PtS-image-and-verified-current-bundle-reused-in-new-fixture')


def prepare(f):
    f.guard();owner=ROOT/'apps/pts';bundle=owner/'runtime-bundle'
    if bundle.exists():
        preserved=owner/('runtime-bundle.pre-e1-'+f.nonce)
        assert not preserved.exists();bundle.rename(preserved)
        private(f.out/'preserved-bundle.json',{'path':str(preserved.relative_to(ROOT)),'provenance_sha256':hashlib.sha256((preserved/'provenance.json').read_bytes()).hexdigest()})
    python=Path(sys.base_prefix)/'bin/python3.15'
    uv=ROOT/'platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/uv/uv'
    f.command([sys.executable,'-B',owner/'deployment/package_runtime.py','--python',python,'--uv',uv,'--cache',Path.home()/'.cache/uv','--output',bundle],'frozen-runtime-package',timeout=300)
    f.command([bundle/'python/bin/python3.15','-B','-c','import importlib.util; p='+repr(str(bundle/'owner-code/backend/acquisition.py'))+'; s=importlib.util.spec_from_file_location("packaged_acquisition",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); result=m.acquisition_catalogue([]); assert len(result["acquisition_leads"])==13; print("packaged-source-catalogue-green")'],'packaged-catalogue-GREEN')
    tag='pts-e1-native:'+f.nonce
    f.command(['docker','build','--network=none','--file','apps/pts/deployment/Dockerfile','--tag',tag,'.'],'frozen-runtime-image-build',timeout=300)
    selected=json.loads(f.docker('image','inspect',tag))[0];assert selected['Config']['User']=='65532:65532'
    f.runtime_image=selected['Id']
    private(f.out/'runtime-image-binding.json',{'image_id':selected['Id'],'user':selected['Config']['User'],'bundle_provenance_sha256':hashlib.sha256((bundle/'provenance.json').read_bytes()).hexdigest(),'boundary':'Actual PtS runtime image; Access/Identity '+('frozen packaged image' if getattr(f,'access_image',None) else 'source process')+'; Content and Directory actual source-process owners.'})
    f.checks.append('fresh-offline-frozen-PtS-image-with-preserved-old-bundle-and-packaged-catalogue-GREEN')


def start_pts(f,environment,port=None,generation='initial'):
    if port is None:
        with socket.socket() as selected:selected.bind(('127.0.0.1',0));port=selected.getsockname()[1]
    path=f.out/('pts-image-'+generation+'.env');path.write_text(''.join(name+'='+value+'\n' for name,value in environment.items()));path.chmod(0o600)
    container='pts-adopt-runtime-'+f.nonce[:16]+'-'+generation
    identity=f.docker('create','--name',container,'--label','agriplatform.pts-adoption='+f.nonce,'--network','host','--read-only','--tmpfs','/tmp','--cap-drop','ALL','--security-opt','no-new-privileges:true','--restart','no','--log-driver','none','--env-file',path,f.runtime_image,'/opt/python/bin/python3.15','-B','-m','uvicorn','backend.main:app','--host','127.0.0.1','--port',port,'--no-access-log','--log-level','critical','--timeout-graceful-shutdown','20')
    f.containers.append(container);f.docker('start',container);f.wait('http://127.0.0.1:'+str(port))
    state=json.loads(f.docker('inspect',container))[0]
    private(f.out/('runtime-container-'+generation+'-binding.json'),{'container_id':identity,'image_id':state['Image'],'pid':state['State']['Pid'],'read_only':state['HostConfig']['ReadonlyRootfs'],'user':state['Config']['User']})
    return {'origin':'http://127.0.0.1:'+str(port),'port':port,'pid':state['State']['Pid'],'container_id':identity,'container_name':container,'runtime_image':state['Image']}


def start_access(f,environment):
    """NEW immutable Access instance using only its declared runtime credentials."""
    import re
    assert re.fullmatch('sha256:[a-f0-9]{64}',f.access_image),'immutable_access_image_required'
    image=json.loads(f.docker('image','inspect',f.access_image))[0]
    assert image['Id']==f.access_image and image['Config']['User']=='65532:65532'
    # Confirm every packaged owner-code byte against current source, independently
    # of a tag or the old Identity29 image's historical receipts.
    from services.access.deployment.verify_runtime import SOURCES
    program='import hashlib,json;from pathlib import Path;names='+repr(SOURCES)+';print(json.dumps({name:hashlib.sha256((Path("/srv")/name).read_bytes()).hexdigest() for name in names},sort_keys=True))'
    selected=json.loads(f.docker('run','--rm','--network','none','--read-only','--entrypoint','/opt/python/bin/python3.15',f.access_image,'-I','-B','-c',program))
    assert selected=={name:hashlib.sha256((ROOT/'services/access'/name).read_bytes()).hexdigest() for name in SOURCES},'access_image_source_changed'
    with socket.socket() as selected_port:selected_port.bind(('127.0.0.1',0));port=selected_port.getsockname()[1]
    path=f.out/'access-image.env';path.write_text(''.join(name+'='+value+'\n' for name,value in environment.items()));path.chmod(0o600)
    container='pts-adopt-access-'+f.nonce[:16]
    identity=f.docker('create','--name',container,'--label','agriplatform.pts-adoption='+f.nonce,'--network','host','--read-only','--tmpfs','/tmp','--cap-drop','ALL','--security-opt','no-new-privileges:true','--restart','no','--log-driver','none','--env-file',path,f.access_image,'/opt/python/bin/python3.15','-B','-m','uvicorn','main:app','--host','127.0.0.1','--port',port,'--no-access-log','--log-level','critical','--timeout-graceful-shutdown','20')
    f.containers.append(container);f.docker('start',container);f.wait('http://127.0.0.1:'+str(port))
    state=json.loads(f.docker('inspect',container))[0]
    private(f.out/'access-runtime-image-binding.json',{'container_id':identity,'image_id':state['Image'],'pid':state['State']['Pid'],'read_only':state['HostConfig']['ReadonlyRootfs'],'user':state['Config']['User'],'owner_code_sha256':selected})
    f.checks.append('actual-frozen-Access-image-matching-all-current-owner-code')
    return {'origin':'http://127.0.0.1:'+str(port),'port':port,'pid':state['State']['Pid'],'container_id':identity,'container_name':container,'runtime_image':state['Image']}
