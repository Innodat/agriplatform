"""Frozen-runtime acceptance boundaries; actual Docker/provider proof is separate."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0,str(Path(__file__).parent))
import studies_frozen_runtime_fixture as frozen
from studies_readiness_integration_fixture import ReadinessIntegrationQualification


def test_original_consumer_oracles_are_inherited():
    for name in ('browser','observe','snapshot','signup_observe','auth_account','record_auth','execute'):
        assert getattr(frozen.FrozenRuntimeQualification,name) is getattr(ReadinessIntegrationQualification,name)


def test_runtime_is_hardened_and_uses_unchanged_image_command(tmp_path):
    args=frozen.container_arguments('owned','sha256:synthetic','fixture-network',tmp_path/'private.env',8193)
    assert args[-1]=='sha256:synthetic'
    for value in ('--read-only','--cap-drop','ALL','--security-opt','no-new-privileges',
                  '--pids-limit','64','--memory','256m','--cpus','1','--user','65532:65532'):
        assert value in args
    assert args[args.index('--publish')+1]=='127.0.0.1:8193:8000'
    assert '--rm' not in args


def test_credentials_are_only_in_exclusive_private_env_file(tmp_path):
    path=tmp_path/'private.env';env={'PRIVATE_SENTINEL':'credential:with=separator'}
    frozen.write_environment(path,env)
    assert path.stat().st_mode&0o777==0o600
    assert path.read_text()=='PRIVATE_SENTINEL=credential:with=separator\n'
    assert env['PRIVATE_SENTINEL'] not in ' '.join(frozen.container_arguments('owned','image','network',path))
    with pytest.raises(FileExistsError):frozen.write_environment(path,env)
    for bad in ('line\nbreak','line\rbreak','nul\0byte'):
        with pytest.raises(ValueError):frozen.write_environment(tmp_path/'bad.env',{'KEY':bad})
        assert not (tmp_path/'bad.env').exists()


def test_genuine_artifact_is_inherited_verbatim_without_value_in_argv(tmp_path):
    raw='{"genuine":"artifact"}\n'
    path=tmp_path/'private.env'
    inherited=frozen.write_runtime_environment(path,{'STUDIES_READINESS_JSON':raw,'SERVICE_KEY':'private'})
    assert inherited=={'STUDIES_READINESS_JSON':raw}
    assert path.read_text()=='SERVICE_KEY=private\n'
    assert 'STUDIES_READINESS_JSON' not in path.read_text()


def test_container_launch_passes_only_artifact_name_to_docker(tmp_path,monkeypatch):
    run=object.__new__(frozen.FrozenRuntimeQualification)
    run.proof=tmp_path;run.run=tmp_path;run.run_id='synthetic';run.image_id='image';run.containers={}
    run.container_environment=lambda values:values
    monkeypatch.setattr(frozen.owner.native_cli,'network',lambda *args:'owned-network')
    calls=[]
    def docker(label,args,**kwargs):
        calls.append((args,kwargs));return 'a'*64+'\n'
    run.docker=docker
    raw='{"genuine":"artifact"}\n'
    run.launch_container('access',{'STUDIES_READINESS_JSON':raw,'SECRET_KEY':'private'})
    args,kwargs=calls[0]
    assert args[args.index('--env')+1]=='STUDIES_READINESS_JSON'
    assert raw not in args and 'private' not in args
    assert kwargs['environment']=={'STUDIES_READINESS_JSON':raw}
    assert args[-1]=='image'


@pytest.mark.parametrize('name',['extra.py','foreign/__init__.py','module.pyc','native.so'])
def test_exact_runtime_membership_refuses_extra_importable_sources(tmp_path,name):
    for module in frozen.RUNTIME_MODULES:(tmp_path/module).write_text('original')
    expected=frozen.runtime_inventory(tmp_path)
    frozen.require_runtime_sources(tmp_path,expected)
    extra=tmp_path/name;extra.parent.mkdir(exist_ok=True);extra.write_text('unexpected')
    with pytest.raises(RuntimeError,match='qualification_runtime_membership_invalid'):
        frozen.require_runtime_sources(tmp_path,expected)


def test_runtime_membership_refuses_changed_expected_source(tmp_path):
    for module in frozen.RUNTIME_MODULES:(tmp_path/module).write_text('original')
    expected=frozen.runtime_inventory(tmp_path)
    (tmp_path/'main.py').write_text('changed')
    with pytest.raises(RuntimeError,match='qualification_runtime_membership_invalid'):
        frozen.require_runtime_sources(tmp_path,expected)


def test_container_cleanup_observes_exact_id_and_preserves_forced_outcome(tmp_path):
    run=object.__new__(frozen.FrozenRuntimeQualification)
    run.proof=tmp_path;run.containers={'name':'a'*64};run.container_stops=[]
    calls=[]
    def docker(label,args,**kwargs):
        calls.append(args)
        if args[0]=='inspect':return json.dumps({'Id':'a'*64,'State':{'Running':False,'ExitCode':137,'OOMKilled':False}})
        return ''
    run.docker=docker
    run.stop_containers()
    assert all(args[-1]=='a'*64 for args in calls)
    assert run.container_stops[0]['forced'] is True
    assert run.container_stops[0]['termination_confirmed'] is True


@pytest.mark.parametrize('unrelated_failure_at',[None,0,1,2])
def test_packaging_refusals_require_actual_verifier_marker(tmp_path,monkeypatch,unrelated_failure_at):
    run=object.__new__(frozen.FrozenRuntimeQualification)
    run.context=tmp_path/'context';run.packaged_owner=run.context/'services/access'
    run.packaged_owner.mkdir(parents=True)
    run.proof=tmp_path/'proof';run.proof.mkdir();run.docker_sequence=0;run.events=[]
    run.owner_access=tmp_path/'archive'
    for name in frozen.INPUTS:
        path=run.packaged_owner/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('synthetic')
    bundle=run.packaged_owner/'runtime-bundle';(bundle/'owner-code').mkdir(parents=True)
    (bundle/'owner-code/main.py').write_text('original')
    (bundle/'provenance.json').write_text('{"files":{}}')
    monkeypatch.setattr(frozen.runpy,'run_path',lambda path:{'inventory':lambda root:{}})
    calls=[]
    def execute(args,**kwargs):
        index=len(calls);calls.append(args)
        stderr=b'Cannot connect to the Docker daemon' if index==unrelated_failure_at else b'access_runtime_verification_failed'
        return subprocess.CompletedProcess(args,1,stdout=b'',stderr=stderr)
    monkeypatch.setattr(frozen.subprocess,'run',execute)
    if unrelated_failure_at is None:
        run.packaging_refusals()
        assert len(calls)==3 and (run.proof/'packaging-refusals.json').exists()
    else:
        with pytest.raises(RuntimeError,match='qualification_docker_refusal_reason_invalid'):
            run.packaging_refusals()
        assert len(calls)==unrelated_failure_at+1
        assert not (run.proof/'packaging-refusals.json').exists()


def test_forced_termination_truth_survives_final_log_failure(tmp_path):
    run=object.__new__(frozen.FrozenRuntimeQualification)
    run.proof=tmp_path;run.containers={'owned':'a'*64};run.container_stops=[]
    def docker(label,args,**kwargs):
        assert args[-1]=='a'*64
        if args[0]=='inspect':return json.dumps({'Id':'a'*64,'State':{'Running':False,'ExitCode':137,'OOMKilled':True}})
        if args[0]=='logs':raise RuntimeError('qualification_docker_failed:logs')
        return ''
    run.docker=docker
    run.stop_containers()
    shutdown=json.loads((tmp_path/'container-shutdown.json').read_text())
    assert shutdown['forced'] is True and shutdown['all_termination_confirmed'] is True
    assert shutdown['containers']==[{'container_id':'a'*64,'termination_confirmed':True,
        'exit_code':137,'oom_killed':True,'forced':True,'stop_command_failed':False,'log_retrieval_failed':True}]
    assert run.containers=={}


@pytest.mark.parametrize('running_after_kill',[False,True])
def test_running_after_stop_is_killed_and_actual_outcome_retained(tmp_path,running_after_kill):
    run=object.__new__(frozen.FrozenRuntimeQualification)
    run.proof=tmp_path;run.containers={'owned':'a'*64};run.container_stops=[]
    calls=[];states=iter([True,running_after_kill])
    def docker(label,args,**kwargs):
        calls.append(args)
        assert args[-1]=='a'*64
        if args[0]=='inspect':
            running=next(states)
            return json.dumps({'Id':'a'*64,'State':{'Running':running,'ExitCode':0 if running else 137,'OOMKilled':False}})
        return ''
    run.docker=docker
    if running_after_kill:
        with pytest.raises(OSError,match='qualification_container_stop_unconfirmed'):run.stop_containers()
        assert run.containers=={'owned':'a'*64}
        shutdown=json.loads((tmp_path/'container-shutdown.json').read_text())
        assert shutdown['all_termination_confirmed'] is False
        assert shutdown['containers']==[{'name':'owned','termination_confirmed':False}]
    else:
        run.stop_containers()
        assert run.containers=={}
        shutdown=json.loads((tmp_path/'container-shutdown.json').read_text())
        assert shutdown['all_termination_confirmed'] is True and shutdown['forced'] is True
        assert shutdown['containers'][0]['exit_code']==137
    assert [args[0] for args in calls][:4]==['stop','inspect','kill','inspect']


def test_container_cleanup_failure_does_not_skip_other_containers(tmp_path):
    run=object.__new__(frozen.FrozenRuntimeQualification)
    run.proof=tmp_path;run.containers={'first':'a'*64,'second':'b'*64};run.container_stops=[]
    calls=[]
    def docker(label,args,**kwargs):
        calls.append(args)
        if args[-1]=='a'*64:raise RuntimeError('qualification_docker_failed')
        if args[0]=='inspect':return json.dumps({'Id':'b'*64,'State':{'Running':False,'ExitCode':0,'OOMKilled':False}})
        return ''
    run.docker=docker
    with pytest.raises(OSError,match='qualification_container_stop_unconfirmed'):run.stop_containers()
    assert any(args[-1]=='b'*64 and args[0]=='inspect' for args in calls)
    assert len(run.container_stops)==2


def test_fixture_stop_attempted_when_container_cleanup_fails(monkeypatch):
    run=object.__new__(frozen.FrozenRuntimeQualification)
    def failed():raise OSError('qualification_container_stop_unconfirmed')
    run.stop_containers=failed
    calls=[]
    monkeypatch.setattr(ReadinessIntegrationQualification,'wrapper',lambda self,action:calls.append(action))
    with pytest.raises(OSError):run.wrapper('stop')
    assert calls==['stop']


def test_qualification_driver_and_checks_are_frozen():
    paths=frozen.app_sources()
    for name in ('tests/studies_frozen_runtime_fixture.py','tests/test_studies_frozen_runtime.py',
                 'tools/py/qualify_studies_frozen_runtime.py'):
        assert frozen.owner.APP/name in paths
