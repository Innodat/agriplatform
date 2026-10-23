"""Run the real host coordinator with synthetic immutable-image execution."""
import copy
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
import pytest
import test_host as fixture

host=fixture.host
CUSTODY=dict(schema_version=1,source_id='tanakh',executor_actor_id='22222222-2222-4222-8222-222222222222',
             actor_kind='service',actor_key='fixture.controller',preparation_evidence_ref='fixture:identity')


def select(root,profile):
    path=root/'env/scribeswell-migrations.env'
    path.write_text(path.read_text()+'SCRIBESWELL_MIGRATION_PROFILE='+profile+'\n'+
                    ('' if profile=='dormant' else 'SCRIBESWELL_MIGRATION_CUSTODY_JSON='+json.dumps(CUSTODY)+'\n'))


@pytest.mark.parametrize('profile',['dormant','prepared-controller-v1','controller-history-v1'])
@pytest.mark.parametrize('fault',[None,'missing','mismatch','digest','unrequested','unknown','incomplete','boolean','revision','extra','malformed','invalid_utf8'])
def test_host_matches_profile_evidence_before_activation(tmp_path,profile,fault):
    harness=fixture.Host();harness.setup_target(tmp_path);select(tmp_path,profile);calls=[]
    def execute(command,**kwargs):
        calls.append(command)
        if command[:2]!=['docker','run']:return
        report=harness.success_report(command)
        if Path(command[command.index('--env-file')+1]).name=='scribeswell-migrations.env':
            if fault=='invalid_utf8':
                evidence=Path(command[command.index('-v')+1].removesuffix(':/evidence'))/'migrations.json'
                evidence.write_bytes(b'\xffsensitive-db-password');return
            report=copy.deepcopy(report);entry=report['owners']['scribeswell']
            if fault=='missing':entry.pop('validation')
            if fault=='mismatch':entry['validation']['profile']='unknown'
            if fault=='digest':entry['validation']['custody_sha256']='0'*64
            if fault=='unrequested':entry.pop('requested_validation')
            if fault=='unknown':entry.update(status='unknown',outcome_requires_reconciliation=True)
            if fault=='incomplete':report['complete']=False
            if fault=='boolean':report['complete']=1
            if fault=='revision':entry['after']='scribeswell_0002'
            if fault=='extra':entry['secret']='sensitive-db-password'
            if fault=='malformed':report='sensitive-db-password'
        harness.migration_report(command,report)
    def render(output,*args):output.mkdir();(output/'apisix.yaml').write_text('fake');return {}
    with patch.object(host,'require_compose'),patch.object(host,'render',side_effect=render),patch.object(host.os,'chown'),patch.object(host,'execute',side_effect=execute),patch.object(host.subprocess,'check_output',return_value=''),patch.object(host,'supervisor_events',return_value={}):
        if fault:
            with pytest.raises(ValueError):harness.deploy(tmp_path)
        else:harness.deploy(tmp_path)
    report=json.loads((tmp_path/'attempt/evidence.json').read_text())
    assert report['activated'] is (fault is None)
    assert report['migrations']['pts-owned']['status']=='succeeded'
    assert report['migrations']['scribeswell-owned']['network']['cleanup']=='removed'
    assert type(report['migrations']['scribeswell-owned']['detail']) is dict
    assert any(c[:2]==['docker','compose'] for c in calls) is (fault is None)
    assert 'sensitive-db-password' not in json.dumps(report)
    assert not list((tmp_path/'state').glob('migration-inputs-*'))


@pytest.mark.parametrize('line',[
    'SCRIBESWELL_MIGRATION_PROFILE=unknown',
    'SCRIBESWELL_MIGRATION_PROFILE=controller-history-v1',
    'SCRIBESWELL_MIGRATION_CUSTODY_JSON={}',
    'SCRIBESWELL_MIGRATION_PROFIL=dormant',
    'SCRIBESWELL_MIGRATION_PROFILE=dormant\nSCRIBESWELL_MIGRATION_PROFILE=dormant',
])
def test_bad_profile_configuration_stops_host_before_effects(tmp_path,line):
    harness=fixture.Host();harness.setup_target(tmp_path)
    path=tmp_path/'env/scribeswell-migrations.env';path.write_text(path.read_text()+line+'\n')
    with patch.object(host,'execute') as execute,patch.object(host,'render') as render:
        with pytest.raises(ValueError):harness.deploy(tmp_path)
    execute.assert_not_called();render.assert_not_called()
    assert not (tmp_path/'state').exists()


def test_validated_migration_inputs_are_frozen_before_first_effect(tmp_path):
    harness=fixture.Host();harness.setup_target(tmp_path);changed=[];used=[]
    source=tmp_path/'env/scribeswell-migrations.env'
    def execute(command,**kwargs):
        if command[:2]==['docker','pull'] and not changed:
            changed.append(True);select(tmp_path,'controller-history-v1')
        if command[:2]==['docker','run']:
            path=Path(command[command.index('--env-file')+1]);used.append(path)
            assert path.parent!=source.parent and path.stat().st_mode & 0o777 == 0o600
            harness.migration_report(command,harness.success_report(command))
    def render(output,*args):output.mkdir();(output/'apisix.yaml').write_text('fake');return {}
    with patch.object(host,'require_compose'),patch.object(host,'render',side_effect=render),patch.object(host.os,'chown'),patch.object(host,'execute',side_effect=execute),patch.object(host.subprocess,'check_output',return_value=''),patch.object(host,'supervisor_events',return_value={}):harness.deploy(tmp_path)
    report=json.loads((tmp_path/'attempt/evidence.json').read_text())
    assert report['activated'] is True and changed and len(used)==2
    assert report['migrations']['scribeswell-owned']['detail']['owners']['scribeswell']['validation']=={'profile':'dormant','custody_sha256':None}
    assert 'postgresql' not in json.dumps(report) and 'literal$dollar' not in json.dumps(report)
    assert not list((tmp_path/'state').glob('migration-inputs-*'))


def test_scribeswell_options_do_not_broaden_other_migration_groups(tmp_path):
    harness=fixture.Host();config,public,manifests=harness.setup_target(tmp_path)
    path=tmp_path/'env/pts-migrations.env'
    path.write_text(path.read_text()+'SCRIBESWELL_MIGRATION_PROFILE=dormant\n')
    with pytest.raises(ValueError,match='migration authority mismatch'):
        host.preflight(config,'staging',manifests,public)


def test_contract_is_host_stdlib_only_and_in_image_and_fingerprint(tmp_path):
    source=host.ROOT/'apps/scribeswell/migrations/release_profile.py'
    probe="import runpy,sys; m=runpy.run_path(sys.argv[1]); assert m['from_environ']({})=={'profile':'dormant','custody':None}; assert 'sqlalchemy' not in sys.modules and 'alembic' not in sys.modules"
    subprocess.run([sys.executable,'-I','-S','-c',probe,str(source)],check=True,capture_output=True,text=True,timeout=5)
    dockerfile=(host.ROOT/'apps/scribeswell/deployment/Migrations.Dockerfile').read_text()
    assert 'COPY apps/scribeswell/migrations apps/scribeswell/migrations' in dockerfile
    app=tmp_path/'app';(app/'migrations').mkdir(parents=True)
    (app/'alembic.ini').write_text('[alembic]')
    contract=app/'migrations/release_profile.py';contract.write_text(source.read_text())
    registry=tmp_path/'platform/deployment/registry.json';registry.parent.mkdir(parents=True)
    registry.write_text('{"migration_groups":[]}')
    with patch.object(host,'ROOT',tmp_path),patch.object(host,'load_manifests',return_value=[{'migration':{'config':'app/alembic.ini'}}]):
        before=host.migration_fingerprint();contract.write_text(contract.read_text()+'\n# changed\n')
        assert before!=host.migration_fingerprint()
