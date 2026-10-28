"""Own lock/source binding, isolated image inputs and fail-closed packaging."""
from pathlib import Path
import importlib.util
import json
import os
import pytest
OWNER=Path(__file__).resolve().parents[1]

def module():
    path=OWNER/'deployment/package_runtime.py'
    spec=importlib.util.spec_from_file_location('access_package',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def binding(tmp_path,*,layout=True):
    m=module();root=tmp_path/'binding';root.mkdir();bundle=root/'runtime-bundle';bundle.mkdir()
    for name in m.INPUTS:
        target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('source:'+name)
    if layout:
        for name in ('python/bin/python3.15','python/lib/python3.15/encodings/__init__.py','site-packages/fastapi/__init__.py','site-packages/uvicorn/__init__.py'):
            p=bundle/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('synthetic layout fixture')
        (bundle/'python/bin/python3.15').chmod(0o755)
        code=bundle/'owner-code';code.mkdir()
        for name in m.SOURCES:(code/name).write_bytes((root/name).read_bytes())
    else:(bundle/'payload.txt').write_text('synthetic payload')
    manifest={'schema_version':1,'python_version':'3.15.0','uv_version':'0.13.1','inputs':{name:m.digest(root/name) for name in m.INPUTS},'files':m.inventory(bundle)}
    (bundle/'provenance.json').write_text(json.dumps(manifest));return m,root,bundle,manifest

def test_access_image_uses_owner_frozen_bundle_and_explicit_python15():
    source=(OWNER/'deployment/Dockerfile').read_text()
    assert 'apps/pts/requirements.txt' not in source
    assert 'runtime-bundle' in source and '/opt/python/bin/python3.15' in source
    assert 'verify_runtime.py' in source

def test_occupied_output_refuses_before_tool_execution(tmp_path):
    m=module();out=tmp_path/'occupied';out.mkdir();(out/'retained').write_text('evidence')
    with pytest.raises(ValueError):m.package(OWNER,Path('/unselected/python'),Path('/unselected/uv'),Path('/unselected/cache'),out)
    assert (out/'retained').read_text()=='evidence'

def test_bundle_verifier_rejects_stale_owner_input_and_extra_payload(tmp_path):
    m,root,bundle,manifest=binding(tmp_path)
    assert m.verify(root,bundle)==manifest
    (root/'uv.lock').write_text('stale lock')
    with pytest.raises(ValueError):m.verify(root,bundle)
    (root/'uv.lock').write_text('source:uv.lock')
    (bundle/'unexpected.txt').write_text('foreign payload')
    with pytest.raises(ValueError):m.verify(root,bundle)

def test_reinventoried_packaged_source_must_match_authoritative_input(tmp_path):
    m,root,bundle,manifest=binding(tmp_path)
    (bundle/'owner-code/main.py').write_text('different source')
    manifest['files']=m.inventory(bundle);(bundle/'provenance.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError):m.verify(root,bundle)

def test_self_consistent_incomplete_payload_is_not_a_runtime(tmp_path):
    m,root,bundle,_=binding(tmp_path,layout=False)
    with pytest.raises(ValueError):m.verify(root,bundle)

def test_selected_interpreter_requires_owner_execute_permission(tmp_path):
    m,root,bundle,_=binding(tmp_path)
    (bundle/'python/bin/python3.15').chmod(0o644)
    with pytest.raises(ValueError):m.verify(root,bundle)

def test_bundle_preserves_existing_studies_readiness_runtime_input(tmp_path):
    m=module()
    assert 'studies_readiness.py' in m.SOURCES
    assert '!services/access/studies_readiness.py' in (OWNER/'deployment/Dockerfile.dockerignore').read_text()

def test_bundle_includes_current_capability_runtime_modules():
    m=module()
    expected={'caller_policy.py','capability_contract.py','capability_check.py','identity_context.py'}
    assert expected <= set(m.SOURCES)
    context=(OWNER/'deployment/Dockerfile.dockerignore').read_text()
    for name in expected:assert '!services/access/'+name in context

def test_existing_pts_deployment_declares_canonical_runtime_dependency():
    manifest=json.loads((OWNER/'deployment/manifest.json').read_text())
    assert 'CAPABILITY_ACCESS_DATABASE_URL' in manifest['required_env']
    assert manifest['database_roles']['CAPABILITY_ACCESS_DATABASE_URL']=='access_runtime'
    from urllib.parse import urlsplit
    assert urlsplit(manifest['smoke_env']['CAPABILITY_ACCESS_DATABASE_URL']).username=='access_runtime'

def test_bundle_includes_discovery_runtime_modules():
    m=module()
    expected={'discovery.py','discovery_contract.py','discovery_query.py'}
    assert expected <= set(m.SOURCES)
    context=(OWNER/'deployment/Dockerfile.dockerignore').read_text()
    for name in expected:assert '!services/access/'+name in context

def test_bundle_includes_native_actor_display_and_refuses_missing_or_stale_payload(tmp_path):
    m,root,bundle,manifest=binding(tmp_path)
    expected={'actor_display_runtime.py','actor_display_http.py','actor_display_contract.py','actor_display_native.py'}
    assert expected <= set(m.SOURCES)
    context=(OWNER/'deployment/Dockerfile.dockerignore').read_text()
    for name in expected:assert '!services/access/'+name in context
    target=bundle/'owner-code/actor_display_native.py'
    target.unlink()
    manifest['files']=m.inventory(bundle);(bundle/'provenance.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='access_bundle_owner_source_mismatch'):m.verify(root,bundle)
    target.write_text('stale-native-reader')
    manifest['files']=m.inventory(bundle);(bundle/'provenance.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='access_bundle_owner_source_mismatch'):m.verify(root,bundle)
