"""Packaging and safety boundaries for the real default API image qualifier."""
import json
from pathlib import Path
import subprocess
import sys

APP=Path(__file__).resolve().parents[1]


def test_shipped_copy_includes_import_time_reference_catalogue(tmp_path):
    """Replay shipped COPY inputs and really import the offline parser."""
    import shutil
    for line in (APP/'deployment/Dockerfile').read_text().splitlines():
        if not line.startswith('COPY '):continue
        _,source,destination=line.split()
        source=APP.parents[1]/source
        target=tmp_path/destination.lstrip('/')
        target.parent.mkdir(parents=True,exist_ok=True)
        if source.is_dir():shutil.copytree(source,target,dirs_exist_ok=True)
        else:shutil.copy2(source,target)
    result=subprocess.run([sys.executable,'-B','-c',
        "import sys;sys.path.insert(0,sys.argv[1]);import passage_references;assert passage_references.BOOKS",
        str(tmp_path/'apps/scribeswell/backend')],capture_output=True,text=True)
    assert result.returncode==0,result.stderr


def test_generic_smoke_requires_catalogue_and_context_allows_it():
    manifest=json.loads((APP/'deployment/manifest.json').read_text())
    assert '/app/apps/scribeswell/data/reference-catalogue/catalogue.json' in manifest['smoke_artifacts']
    assert '!apps/scribeswell/data/reference-catalogue/**' in (APP/'deployment/Dockerfile.dockerignore').read_text()


import studies_api_image_fixture as api
import studies_frozen_runtime_fixture as frozen
import studies_owner_fixture as owner
import pytest


def test_inherits_complete_consumer_and_frozen_owner_oracles():
    for method in ('browser','observe','snapshot','create_accounts','prepare_readiness',
                   'startup_refusals','operator','stop_one','stop_containers','wrapper'):
        assert getattr(api.ApiImageQualification,method) is getattr(frozen.FrozenRuntimeQualification,method)
    assert api.ApiImageQualification.__mro__[1] is frozen.FrozenRuntimeQualification


def test_api_container_preserves_default_command_uid_and_hardening(tmp_path):
    args=api.app_container_arguments('new-owned','sha256:synthetic','new-network',tmp_path/'private.env',8192)
    assert args[-1]=='sha256:synthetic'
    assert args[args.index('--user')+1]=='10001:10001'
    assert args[args.index('--publish')+1]=='127.0.0.1:8192:8000'
    assert all(value in args for value in ('--read-only','--cap-drop','ALL','no-new-privileges','--pids-limit','64','--memory','256m','--cpus','1'))
    assert '--entrypoint' not in args and '--rm' not in args


def test_packaging_inventory_detects_changed_new_and_removed_inputs(tmp_path,monkeypatch):
    app=tmp_path/'apps/scribeswell';(app/'backend').mkdir(parents=True);(app/'deployment').mkdir()
    (app/'deployment/Dockerfile').write_text('COPY apps/scribeswell/backend/ apps/scribeswell/backend/\n')
    source=app/'backend/module.py';source.write_text('original')
    monkeypatch.setattr(owner,'ROOT',tmp_path);monkeypatch.setattr(owner,'APP',app)
    before=api.packaged_sources();assert set(before)=={source}
    source.write_text('changed');assert api.packaged_sources()!=before
    source.write_text('original');late=app/'backend/late.bin';late.write_bytes(b'late');assert api.packaged_sources()!=before
    late.unlink();assert api.packaged_sources()==before
    source.unlink();assert api.packaged_sources()!=before


def test_packaging_inventory_refuses_symlink(tmp_path,monkeypatch):
    app=tmp_path/'apps/scribeswell';(app/'backend').mkdir(parents=True);(app/'deployment').mkdir()
    (app/'deployment/Dockerfile').write_text('COPY apps/scribeswell/backend/ apps/scribeswell/backend/\n')
    (app/'backend/foreign.py').symlink_to('/etc/hosts')
    monkeypatch.setattr(owner,'ROOT',tmp_path);monkeypatch.setattr(owner,'APP',app)
    with pytest.raises(RuntimeError,match='qualification_packaging_symlink_refused'):api.packaged_sources()



def test_packaging_inventory_refuses_top_level_directory_symlink(tmp_path,monkeypatch):
    repository=tmp_path/'repository';app=repository/'apps/scribeswell'
    (app/'deployment').mkdir(parents=True)
    (app/'deployment/Dockerfile').write_text('COPY apps/scribeswell/backend/ apps/scribeswell/backend/\n')
    external=tmp_path/'external';external.mkdir();(external/'foreign.py').write_text('external = True')
    (app/'backend').symlink_to(external,target_is_directory=True)
    monkeypatch.setattr(owner,'ROOT',repository);monkeypatch.setattr(owner,'APP',app)
    with pytest.raises(RuntimeError,match='qualification_packaging_symlink_refused'):api.packaged_sources()


def test_runtime_environment_uses_only_restricted_app_urls_and_no_inherited_authority():
    from sqlalchemy.engine import make_url
    run=object.__new__(api.ApiImageQualification);run.run_id='f4071678-722d-42bc-b5c8-aa4aec2d6b66'
    run.access_container='owned-access';run.containers={'owned-access':'a'*64}
    environment={'PATH':'sentinel','HOME':'sentinel','IDENTITY_MIGRATION_DATABASE_URL':'credential-sentinel',
        'SUPABASE_SERVICE_ROLE_KEY':'','SCRIBESWELL_DATABASE_URL':'postgresql://scribeswell_runtime:private@localhost:55492/postgres',
        'SCRIBESWELL_STUDIES_DATABASE_URL':'postgresql://scribeswell_studies_runtime:private@localhost:55492/postgres',
        'SCRIBESWELL_STUDIES_ENABLED':'true','SCRIBESWELL_STUDIES_SERVICE_KEY':'private-service'}
    result=run.api_environment(environment)
    assert 'PATH' not in result and 'HOME' not in result and 'IDENTITY_MIGRATION_DATABASE_URL' not in result
    assert result['SCRIBESWELL_STUDIES_ACCESS_URL']=='http://owned-access:8000'
    for name,role in api.APP_ROLE_KEYS.items():
        url=make_url(result[name]);assert url.username==role and url.query['sslmode']=='require'
        assert url.host.startswith('supabase_db_') and url.port==5432


def test_api_driver_packaging_and_all_corpus_inputs_are_frozen():
    inputs=api.packaged_sources()
    for name in ('backend/main.py','backend/requirements.txt','data/reference-catalogue/catalogue.json',
                 'scripts/hebrew.json','scripts/seed.py','tools/py/import_bible.py','tools/py/oshb_morph.py'):
        assert APP/name in inputs
    assert any(p.is_relative_to(APP/'data/hebrew-lexicon') for p in inputs)
    assert all((APP/name).is_file() for name in (*api.PACKAGING,*api.DRIVERS))


def test_unknown_image_file_refuses_before_success_claim(tmp_path):
    run=object.__new__(api.ApiImageQualification)
    run.containers={'api':'a'*64};run.api_container='api';run.api_inputs={APP/'backend/requirements.txt':'expected'}
    run.docker=lambda *args,**kwargs:json.dumps({'files':{'/app/unexpected.py':{'sha256':'unexpected'}},'requirements_sha256':'expected'})
    with pytest.raises(RuntimeError,match='qualification_api_image_files_invalid'):run.probe_api()
    assert not (tmp_path/'api-runtime-probe.json').exists()


def test_packaging_context_membership_drift_refuses(tmp_path,monkeypatch):
    run=object.__new__(api.ApiImageQualification)
    run.api_inputs={};run.api_driver_inputs={};run.api_context=tmp_path
    monkeypatch.setattr(frozen.FrozenRuntimeQualification,'verify_sources',lambda self:None)
    monkeypatch.setattr(api,'packaged_sources',lambda:{})
    run.verify_sources()
    (tmp_path/'unlisted').write_bytes(b'unexpected')
    with pytest.raises(RuntimeError,match='qualification_api_context_changed'):run.verify_sources()


def test_dependency_drift_after_signup_refuses(tmp_path):
    run=object.__new__(api.ApiImageQualification)
    run.proof=tmp_path;run.containers={'api':'a'*64};run.api_container='api'
    initial={'files':{},'requirements_sha256':'same','dependencies':{'installed':'1'},'dependency_files':{'file':{'sha256':'original'}}}
    (tmp_path/'api-runtime-probe.json').write_text(json.dumps(initial))
    run.docker=lambda *args,**kwargs:json.dumps(initial|{'dependency_files':{'file':{'sha256':'changed'}}})
    with pytest.raises(RuntimeError,match='qualification_api_runtime_drift'):run.probe_api_final()
    assert not (tmp_path/'api-final-inspection.json').exists()


@pytest.mark.parametrize('tls_enabled',[True,False])
def test_runtime_probe_reads_requirements_inside_app_and_requires_real_role_tls(monkeypatch,capsys,tls_enabled):
    import errno
    import hashlib
    import importlib.metadata
    import importlib.util
    import os
    requirement=Path('/app/apps/scribeswell/backend/requirements.txt')
    def contents(path):
        if path!=requirement:raise FileNotFoundError('staged /tmp artifact is hidden by runtime tmpfs')
        return b'shipped requirements'
    def readonly(*args,**kwargs):raise OSError(errno.EROFS,'read-only')
    monkeypatch.setattr(Path,'rglob',lambda path,pattern:iter([requirement]) if path==Path('/app') else iter([]))
    monkeypatch.setattr(Path,'read_bytes',contents)
    monkeypatch.setattr(Path,'write_text',readonly)
    monkeypatch.setattr(Path,'is_symlink',lambda self:False)
    monkeypatch.setattr(Path,'is_file',lambda self:True)
    monkeypatch.setattr(os,'getuid',lambda:10001)
    monkeypatch.setattr(importlib.util,'find_spec',lambda module:None)
    monkeypatch.setattr(importlib.metadata,'distributions',lambda:[])
    import psycopg
    class Connection:
        def __init__(self,role):self.role=role
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def execute(self,*args):return self
        def fetchone(self):return (self.role,tls_enabled,'TLSv1.3','synthetic-cipher')
    monkeypatch.setattr(psycopg,'connect',lambda role,**kwargs:Connection(role))
    for key,role in api.APP_ROLE_KEYS.items():monkeypatch.setenv(key,role)
    if not tls_enabled:
        with pytest.raises(AssertionError):exec(api.PROBE,{})
        assert capsys.readouterr().out==''
        return
    exec(api.PROBE,{})
    value=json.loads(capsys.readouterr().out)
    assert set(value['sql_tls'])==set(api.APP_ROLE_KEYS.values())
    assert all(row['ssl'] for row in value['sql_tls'].values())
    assert value['requirements_sha256']==hashlib.sha256(b'shipped requirements').hexdigest()


@pytest.mark.parametrize('marker_present',[False,True])
def test_app_refusals_require_configuration_reason_and_preserve_all_cases(tmp_path,marker_present):
    from sqlalchemy.engine import make_url
    run=object.__new__(api.ApiImageQualification)
    run.proof=tmp_path;run.containers={}
    run.urls={'identity_migrator':make_url('postgresql://identity_migrator:private@localhost/db')}
    seen=[]
    def launch(label,environment):
        seen.append((label,environment));run.containers[label]='a'*64;return label
    run.launch_api=launch
    run.container_state=lambda name:{'State':{'Running':False,'ExitCode':1,'OOMKilled':False}}
    run.docker=lambda *args:'Invalid database configuration Remove obsolete runtime service-key authority Studies production activation awaits migration and integration qualification' if marker_present else 'unrelated failure'
    run.stop_one=lambda name:run.containers.pop(name)
    if marker_present:
        run.api_refusals({'SCRIBESWELL_STUDIES_ENABLED':'true'})
        assert len(seen)==5
        assert json.loads((tmp_path/'api-startup-refusals.json').read_text())['all_refused'] is True
    else:
        with pytest.raises(RuntimeError,match='qualification_api_refusal_reason_invalid'):run.api_refusals({})
        assert len(seen)==1 and not (tmp_path/'api-startup-refusals.json').exists()


@pytest.mark.parametrize('both_runtime_roles_observed',[True,False])
def test_closed_private_transactions_need_no_resident_pool_but_runtime_tls_is_required(tmp_path,monkeypatch,both_runtime_roles_observed):
    from contextlib import contextmanager
    run=object.__new__(api.ApiImageQualification)
    run.proof=tmp_path;run.containers={'api':'a'*64};run.api_container='api'
    run.api_image='image';run.api_image_metadata={'Cmd':['default'],'User':'10001:10001'}
    run.api_inputs={APP/'backend/requirements.txt':'expected'}
    run.run_id='synthetic';run.run=tmp_path
    files={'/app/apps':{'directory':True},'/app/apps/scribeswell':{'directory':True},
        '/app/apps/scribeswell/backend':{'directory':True},'/app/apps/scribeswell/backend/requirements.txt':{'sha256':'expected'}}
    value={'files':files,'requirements_sha256':'expected','sql_tls':{role:{'ssl':True} for role in api.APP_ROLE_KEYS.values()}}
    if not both_runtime_roles_observed:value['sql_tls'].pop('scribeswell_studies_runtime')
    restrictions={'Image':'image','Cmd':['default'],'User':'10001:10001','ReadonlyRootfs':True,
        'CapDrop':['ALL'],'SecurityOpt':['no-new-privileges'],'PidsLimit':64,'Memory':256*1024*1024,
        'NanoCpus':1000000000,'NetworkMode':'fixture','PortBindings':{'8000/tcp':[{'HostIp':'127.0.0.1','HostPort':str(owner.TARGET_CONFIG['ports']['api'])}]},
        'Tmpfs':{'/tmp':'rw,noexec,nosuid,size=16m'},'Mounts':[],'Privileged':False}
    monkeypatch.setattr(owner.native_cli,'network',lambda *args:'fixture')
    run.docker=lambda label,args:json.dumps(value if args[0]=='exec' else restrictions)
    class Connection:
        def execute(self,*args):return self
        def fetchall(self):return [('scribeswell_runtime',True,'TLSv1.3','synthetic-cipher')]
    @contextmanager
    def connect():yield Connection()
    run.connect=connect
    if both_runtime_roles_observed:
        run.probe_api()
        recorded=json.loads((tmp_path/'api-runtime-probe.json').read_text())
        assert recorded['resident_sessions_tls']['scribeswell_studies_runtime']==[]
        assert recorded['sql_tls']['scribeswell_studies_runtime']['ssl'] is True
    else:
        with pytest.raises(RuntimeError,match='qualification_api_runtime_tls_unproven'):run.probe_api()
        assert not (tmp_path/'api-runtime-probe.json').exists()
