"""Prepared target boundaries; real database proof is root-owned."""
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))


def test_missing_target_is_safe_and_no_network():
    import identity_operator_target as target
    with pytest.raises(target.TargetError) as error:
        target.load_target('/tmp/secret-password-target')
    assert str(error.value)=='identity_operator_target_invalid'
    assert 'secret-password' not in repr(error.value)


@pytest.fixture
def prepared(tmp_path,monkeypatch):
    import json, shutil, uuid
    import identity_operator_target as t
    original=t.ROOT
    monkeypatch.setattr(t,'ROOT',tmp_path)
    monkeypatch.setattr(t.dev,'ROOT',tmp_path)
    env_path=tmp_path/t.ENV_REF
    env_path.parent.mkdir(parents=True)
    environment=json.loads((original/t.ENV_REF).read_bytes())
    environment['workspace_root']=str(tmp_path)
    env_path.write_text(json.dumps(environment))
    schema=tmp_path/t.dev.SCHEMA
    schema.parent.mkdir(parents=True)
    shutil.copyfile(original/t.dev.SCHEMA,schema)
    run_id=str(uuid.uuid4());run=tmp_path/t.RUN_REF/run_id
    t.native_cli.prepare(run,environment,env_path.read_bytes(),run_id)
    (run/'secrets').mkdir(mode=0o700)
    secret=run/'secrets/identity.env'
    secret.write_bytes(b'IDENTITY_OPERATOR_PASSWORD=private-value\n');secret.chmod(0o600)
    return t,env_path,run_id,run,secret


def test_prepare_load_exclusive_and_binding(prepared):
    t,env,run_id,run,secret=prepared
    descriptor=t.prepare_target(env,run_id)
    loaded=t.load_target(descriptor)
    assert loaded.database=='idop_'+run_id.replace('-','')
    assert loaded.port==55482 and loaded.password=='private-value'
    assert 'private-value' not in repr(loaded)
    with pytest.raises(t.TargetError):t.prepare_target(env,run_id)
    env.write_bytes(env.read_bytes()+b'\n')
    with pytest.raises(t.TargetError):t.load_target(descriptor)


@pytest.mark.parametrize('value',[b'IDENTITY_OPERATOR_PASSWORD=\n',b'IDENTITY_OPERATOR_PASSWORD=x\nOTHER=y',b'IDENTITY_OPERATOR_PASSWORD=${HOME}',b'IDENTITY_OPERATOR_PASSWORD=x\x00',b'IDENTITY_OPERATOR_PASSWORD='+b'x'*1024])
def test_invalid_secrets(prepared,value):
    t,env,run_id,run,secret=prepared
    secret.write_bytes(value)
    with pytest.raises(t.TargetError):t.prepare_target(env,run_id)
    assert not (run/'identity-operator.json').exists()


@pytest.mark.parametrize('mutation',['secret_mode','run_mode','secret_link','secret_symlink','descriptor_link','descriptor_mode','secrets_mode','descriptor_change','native_change'])
def test_unsafe_inputs(prepared,mutation):
    import os,json
    t,env,run_id,run,secret=prepared
    descriptor=t.prepare_target(env,run_id)
    if mutation=='secret_mode':secret.chmod(0o644)
    if mutation=='run_mode':run.chmod(0o755)
    if mutation=='secrets_mode':secret.parent.chmod(0o755)
    if mutation=='secret_link':os.link(secret,run/'copy')
    if mutation=='secret_symlink':
        secret.rename(run/'copy');secret.symlink_to(run/'copy')
    if mutation=='descriptor_link':os.link(descriptor,run/'copy')
    if mutation=='descriptor_mode':descriptor.chmod(0o644)
    if mutation=='descriptor_change':
        value=json.loads(descriptor.read_bytes());value['database_login']='postgres';descriptor.write_text(json.dumps(value))
    if mutation=='native_change':(run/'native.json').write_text('{}')
    with pytest.raises(t.TargetError):t.load_target(descriptor)


@pytest.mark.parametrize('field,value',[
    ('owner_id','access'),('environment_kind','production'),('run_id','11111111-1111-1111-1111-111111111111'),
    ('environment_target_ref','other.json'),('target_sha256','0'*64),('database','wrong'),
    ('database_login','postgres'),('secret_ref','other.env'),('schema_version',True),('extra','forbidden')])
def test_each_descriptor_binding_refuses(prepared,field,value):
    import json
    t,env,run_id,run,secret=prepared
    descriptor=t.prepare_target(env,run_id)
    document=json.loads(descriptor.read_bytes());document[field]=value
    descriptor.write_text(json.dumps(document))
    with pytest.raises(t.TargetError):t.load_target(descriptor)


@pytest.fixture
def prepared_leave(tmp_path,monkeypatch):
    import json,shutil
    import identity_operator_target as t
    original=t.ROOT
    monkeypatch.setattr(t,'ROOT',tmp_path);monkeypatch.setattr(t.dev,'ROOT',tmp_path)
    source=tmp_path/t.LEAVE_ENV_REF;source.parent.mkdir(parents=True)
    environment=json.loads((original/t.LEAVE_ENV_REF).read_bytes());environment['workspace_root']=str(tmp_path)
    source.write_text(json.dumps(environment))
    schema=tmp_path/'platform/deployment/schema/leave-development-target-v1.json';schema.parent.mkdir(parents=True);shutil.copyfile(original/'platform/deployment/schema/leave-development-target-v1.json',schema)
    run=tmp_path/t.LEAVE_RUN_REF/t.LEAVE_RUN
    t.native_cli.prepare(run,environment,source.read_bytes(),t.LEAVE_RUN)
    (run/'secrets').mkdir(mode=0o700);secret=run/'secrets/identity-operator.env'
    secret.write_bytes(b'IDENTITY_OPERATOR_PASSWORD=explicit-existing-password\n');secret.chmod(0o600)
    project=t.dev.project_identity(environment,t.LEAVE_RUN)
    row=dict(State=dict(Running=True),NetworkSettings=dict(Ports={'5432/tcp':[dict(HostIp='127.0.0.1',HostPort='55582')]},Networks={project+'-network':dict(NetworkID='verified-leave-network')}))
    monkeypatch.setattr(t.native_cli,'network',lambda *args:'verified-leave-network')
    monkeypatch.setattr(t.native_cli,'docker',lambda *args:json.dumps([row]).encode())
    return t,source,run,secret,row


def test_leave_descriptor_is_explicit_namespace_and_original_worker_binding(prepared_leave):
    t,source,run,secret,row=prepared_leave
    descriptor=t.prepare_target(source,t.LEAVE_RUN,namespace='1234abcd')
    target=t.load_target(descriptor)
    assert descriptor==run/'identity-operator-1234abcd.json'
    assert target.database=='idb_88a737ddad7b_1234abcd' and target.port==55582 and target.password=='explicit-existing-password'
    assert 'explicit-existing-password' not in repr(target)


@pytest.mark.parametrize('defect',['foreign_run','no_namespace','namespace','owner','secret_mode','secret_content','container','network','database'])
def test_leave_descriptor_rejects_foreign_binding_before_connections(prepared_leave,defect):
    import json
    t,source,run,secret,row=prepared_leave
    if defect=='foreign_run':
        with pytest.raises(t.TargetError):t.prepare_target(source,'11111111-1111-4111-8111-111111111111',namespace='1234abcd')
        return
    if defect in ('no_namespace','namespace','owner'):
        with pytest.raises(t.TargetError):t.prepare_target(source,t.LEAVE_RUN,namespace=None if defect=='no_namespace' else '1234abcG' if defect=='namespace' else '1234abcd',owner='access' if defect=='owner' else 'identity')
        return
    descriptor=t.prepare_target(source,t.LEAVE_RUN,namespace='1234abcd')
    if defect=='secret_mode':secret.chmod(0o644)
    elif defect=='secret_content':secret.write_bytes(b'IDENTITY_OPERATOR_PASSWORD=${HOME}\n')
    elif defect=='container':row['State']['Running']=False
    elif defect=='network':next(iter(row['NetworkSettings']['Networks'].values()))['NetworkID']='foreign'
    elif defect=='database':
        value=json.loads(descriptor.read_bytes());value['database']='idb_88a737ddad7b_foreign';descriptor.write_text(json.dumps(value))
    with pytest.raises(t.TargetError):t.load_target(descriptor)
