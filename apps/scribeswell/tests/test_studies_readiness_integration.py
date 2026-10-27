"""App launch boundary and source-freeze oracles; native proof is separate."""
import json
from pathlib import Path
import sys
from hashlib import sha256
import subprocess
from importlib.machinery import PathFinder
import pytest

sys.path.insert(0,str(Path(__file__).parent))
import studies_owner_fixture as owner
import studies_readiness_integration_fixture as integration
from studies_signup_fixture import SignupQualification


def test_access_launch_uses_default_module_without_injected_dependencies(monkeypatch):
    run=object.__new__(integration.ReadinessIntegrationQualification)
    run.environment={};run.service_key='synthetic-key'
    run.status={'api_url':'http://localhost:55491','anon_key':'synthetic-public'}
    class URL:
        def render_as_string(self,**kwargs):return 'synthetic-private-url'
    run.urls=dict.fromkeys(('access_studies_runtime','identity_studies_reader_runtime',
        'identity_studies_setup_runtime','scribeswell_runtime','scribeswell_studies_runtime'),URL())
    run.owner_access=Path('/explicit/qualified/services/access')
    run.runtime_environment={'STUDIES_READINESS_JSON':'verbatim private artifact'}
    stages=[]
    run.prepare_readiness=lambda:stages.append('prepare')
    run.startup_refusals=lambda:stages.append('refusals')
    launches=[]
    run.spawn=lambda label,args,env,cwd:launches.append((label,args,env,cwd))
    monkeypatch.setattr(owner,'wait_http',lambda *args:None)
    run.start_apps()
    label,args,env,cwd=launches[0]
    assert args[1:4]==['-m','uvicorn','main:app']
    assert not any(key.startswith('FIXTURE_') for key in env)
    assert env==run.runtime_environment and cwd==run.owner_access
    assert stages==['prepare','refusals']
    assert [call[0] for call in launches]==['access-http','scribeswell-http','vite']


def test_original_signup_browser_sql_and_privacy_oracles_are_inherited():
    cls=integration.ReadinessIntegrationQualification
    for method in ('browser','observe','snapshot','signup_observe','auth_account','record_auth','execute'):
        assert getattr(cls,method) is getattr(SignupQualification,method)


def test_selected_owner_is_restored_even_after_failed_preparation(tmp_path):
    previous=owner.ACCESS
    with pytest.raises(RuntimeError):
        with integration.selected_owner(tmp_path):
            assert owner.ACCESS==tmp_path/'services/access'
            raise RuntimeError('synthetic')
    assert owner.ACCESS==previous


def test_driver_and_test_are_in_independent_app_freeze():
    paths=integration.app_sources()
    for name in ('tests/studies_readiness_integration_fixture.py','tests/test_studies_readiness_integration.py',
        'tools/py/qualify_studies_readiness_integration.py','tests/studies_signup_fixture.py',
        'web/tests/studies-signup.integration.cjs','web/tests/studies-owner.integration.cjs'):
        assert owner.APP/name in paths
    assert not any(path.is_relative_to(owner.ROOT/'services/access') for path in paths)


@pytest.mark.parametrize('changed',['app','owner','qualification','cli'])
def test_freeze_refuses_independent_source_or_proof_drift(tmp_path,monkeypatch,changed):
    run=object.__new__(integration.ReadinessIntegrationQualification)
    paths={name:tmp_path/name for name in ('app','owner','qualification','cli')}
    for path in paths.values():path.write_text('original')
    digest=sha256(b'original').hexdigest()
    run.app_sources={paths['app']:digest};run.owner_sources={paths['owner']:digest}
    run.owner_access=tmp_path/'selected-owner';run.owner_access.mkdir()
    run.owner_module_sources=integration.owner_module_sources(run.owner_access)
    run.proof_sources={paths['qualification']:digest};run.cli=paths['cli'];run.cli_sha256=digest
    monkeypatch.setattr(integration,'app_sources',lambda:{paths['app']:sha256(paths['app'].read_bytes()).hexdigest()})
    run.verify_sources();paths[changed].write_text('changed')
    with pytest.raises(RuntimeError,match='^qualification_.*changed$'):run.verify_sources()


def test_cli_requires_explicit_owner_source_and_qualification_without_defaults():
    result=subprocess.run([sys.executable,str(owner.APP/'tools/py/qualify_studies_readiness_integration.py'),
        '--run-id','11111111-1111-4111-8111-111111111111','--supabase','/explicit/supabase','--proof','/tmp/unused'],
        capture_output=True,text=True,timeout=10)
    assert result.returncode==2
    assert '--source-root' in result.stderr and '--qualification' in result.stderr


@pytest.mark.parametrize('late_path',['httpx.py','httpx/__init__.py','existing/late.py'])
def test_owner_freeze_refuses_late_importable_module_or_package(tmp_path,monkeypatch,late_path):
    run=object.__new__(integration.ReadinessIntegrationQualification)
    run.owner_access=tmp_path/'selected-owner';run.owner_access.mkdir()
    (run.owner_access/'main.py').write_text('baseline = True\n')
    package=run.owner_access/'existing';package.mkdir()
    (package/'__init__.py').write_text('baseline = True\n')
    run.app_sources={};monkeypatch.setattr(integration,'app_sources',lambda:{})
    run.owner_module_sources={path:sha256(path.read_bytes()).hexdigest()
        for path in run.owner_access.rglob('*.py')}
    run.owner_sources=dict(run.owner_module_sources);run.proof_sources={}
    run.cli=tmp_path/'cli';run.cli.write_text('unchanged')
    run.cli_sha256=sha256(run.cli.read_bytes()).hexdigest()
    run.verify_sources()
    added=run.owner_access/late_path;added.parent.mkdir(exist_ok=True)
    added.write_text('late = True\n')
    search=package if late_path.startswith('existing/') else run.owner_access
    name='late' if late_path.startswith('existing/') else 'httpx'
    assert PathFinder.find_spec(name,[str(search)]).origin==str(added)
    with pytest.raises(RuntimeError,match='^qualification_owner_sources_changed$'):
        run.verify_sources()
