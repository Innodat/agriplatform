"""Private history is opt-in and failures block activation; no live release occurs."""
import importlib.util
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'platform/deployment'))
sys.path.insert(0,str(ROOT/'apps/scribeswell/deployment'))
from studies_migrate import selected
from release import runtime_contract,load_manifests,coordinate

def test_disabled_production_contract_and_partial_authority_refusal():
    manifest=next(m for m in load_manifests(ROOT) if m['id']=='scribeswell')
    assert manifest['public']['paths']==['/api/bible/*']
    assert manifest['personal_studies']['production_enabled'] is False
    assert 'SCRIBESWELL_STUDIES_DATABASE_URL' not in runtime_contract(manifest,{})[1]
    for values in ({'SCRIBESWELL_STUDIES_ENABLED':'true'}, {'SCRIBESWELL_STUDIES_DATABASE_URL':'private'}, {'SCRIBESWELL_STUDIES_ENABLED':'garbage'}):
        with pytest.raises(ValueError):runtime_contract(manifest,values)

def test_optional_private_migration_selection_is_complete():
    assert selected({}) is False
    assert selected({'SCRIBESWELL_STUDIES_MIGRATION_ENABLED':'true','SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL':'private'}) is True
    for values in ({'SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL':'private'}, {'SCRIBESWELL_STUDIES_MIGRATION_ENABLED':'true'}):
        with pytest.raises(ValueError):selected(values)

def test_private_history_failure_blocks_activation_after_previous_owners():
    calls=[]
    def migration(owner):
        calls.append(owner)
        if owner=='scribeswell_studies':raise RuntimeError('private details')
    report=coordinate(['identity','access','scribeswell','scribeswell_studies'],migration,lambda:calls.append('activate'))
    assert calls==['identity','access','scribeswell','scribeswell_studies']
    assert report['activated'] is False
    assert report['owners']['scribeswell']['status']=='succeeded'
    assert report['owners']['scribeswell_studies']['status']=='failed'
    assert 'private details' not in str(report)

@pytest.mark.parametrize('private_succeeds',[False,True])
def test_actual_entry_orders_histories_and_private_failure_blocks_complete(tmp_path,monkeypatch,private_succeeds):
    import json
    path=ROOT/'apps/scribeswell/deployment/migrate.py'
    spec=importlib.util.spec_from_file_location('notes_migration_entry',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    monkeypatch.setattr(module,'validate_url',lambda env:'synthetic-corpus')
    calls=[]
    class Child:
        def __init__(self,command):self.command=command;self.returncode=0 if len(calls)==1 or private_succeeds else 1
        def communicate(self,payload=None,timeout=None):
            if len(calls)==1:return json.dumps({'before':'scribeswell_0003','after':'scribeswell_0003','validation':{'profile':'dormant','custody_sha256':None}}),''
            assert json.loads(payload)=={'url':'synthetic-private'}
            return json.dumps({'complete':True,'owner':'scribeswell_studies','before':'scribeswell_studies_0008','after':'scribeswell_studies_0009','recovery':'forward-only'} if private_succeeds else {'complete':False,'code':'scribeswell_studies_migration_failed'}),''
        def poll(self):return self.returncode
    def run(command,**kwargs):calls.append(command);assert 'synthetic-private' not in str(command);return Child(command)
    env={'SCRIBESWELL_STUDIES_MIGRATION_ENABLED':'true','SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL':'synthetic-private'}
    target=tmp_path/'migrations.json'
    if private_succeeds:module.main(target,environ=env,run=run)
    else:
        with pytest.raises(SystemExit):module.main(target,environ=env,run=run)
    report=json.loads(target.read_text())
    assert report['complete'] is private_succeeds
    assert len(calls)==2 and calls[0][-1]=='--worker' and calls[1][-1].endswith('studies_migrate.py')
    assert target.with_name('studies-migrations.json').exists() is private_succeeds
    assert 'synthetic-private' not in target.read_text()
    if private_succeeds:
        assert json.loads(target.with_name('studies-migrations.json').read_text())==private_report('scribeswell_studies_0008')


def private_report(before='scribeswell_studies_0008'):
    return {'complete':True,'owner':'scribeswell_studies','before':before,
            'after':'scribeswell_studies_0009','recovery':'forward-only'}


def test_private_contract_matches_actual_linear_history_and_package():
    import json
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    import studies_release_contract as contract
    history=ScriptDirectory.from_config(Config(str(ROOT/'apps/scribeswell/studies-alembic.ini')))
    assert history.get_heads()==[contract.TARGET]
    revisions=list(history.walk_revisions())
    assert [revision.revision for revision in revisions]==list(reversed(contract.REVISIONS))
    assert all(revision.down_revision==(revisions[index+1].revision if index+1<len(revisions) else None)
               for index,revision in enumerate(revisions))
    assert contract.valid_result(private_report(None))
    assert contract.valid_result(private_report(contract.TARGET))
    registry=json.loads((ROOT/'platform/deployment/registry.json').read_text())
    sources=next(group for group in registry['migration_groups'] if group['id']=='scribeswell-owned')['compatibility_inputs']
    assert 'apps/scribeswell/deployment/studies_release_contract.py' in sources
    assert all(str(Path(revision.path).relative_to(ROOT)) in sources for revision in revisions)
    docker=(ROOT/'apps/scribeswell/deployment/Migrations.Dockerfile').read_text()
    assert 'COPY apps/scribeswell/deployment/studies_release_contract.py apps/scribeswell/deployment/studies_release_contract.py' in docker


@pytest.mark.parametrize('changes',[
    {'complete':1},{'owner':'foreign'},{'before':[]},{'before':'unknown'},
    {'after':'scribeswell_studies_0001'},{'after':'foreign_0009'},
    {'recovery':'rollback'},{'extra':'private payload'},
])
def test_private_contract_refuses_unsafe_or_stale_success(changes):
    from studies_release_contract import valid_result
    assert not valid_result(private_report()|changes)


@pytest.mark.parametrize('output',[
    '{}','[]','not-json','x'*4097,
    '{"complete":true,"owner":"scribeswell_studies","after":"scribeswell_studies_0001","recovery":"forward-only"}',
    '{"complete":true,"owner":"scribeswell_studies","before":null,"after":"scribeswell_studies_0009","after":"scribeswell_studies_0009","recovery":"forward-only"}',
    '{"complete":true,"owner":"scribeswell_studies","before":null,"after":"scribeswell_studies_0009","recovery":"forward-only","unsafe":"private payload"}',
    '{"complete":false,"code":"scribeswell_studies_migration_failed"}',
])
def test_supervisor_refuses_private_output_without_success_artifact(tmp_path,monkeypatch,output):
    import json
    spec=importlib.util.spec_from_file_location('private_refusal_entry',ROOT/'apps/scribeswell/deployment/migrate.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    monkeypatch.setattr(module,'validate_url',lambda env:'synthetic-corpus')
    calls=[]
    class Child:
        returncode=0
        def communicate(self,*args,**kwargs):
            return (json.dumps({'before':None,'after':'scribeswell_0003','validation':{'profile':'dormant','custody_sha256':None}}) if len(calls)==1 else output),''
        def poll(self):return 0
    def run(*args,**kwargs):calls.append(args);return Child()
    target=tmp_path/'migrations.json'
    with pytest.raises(SystemExit):module.main(target,environ={'SCRIBESWELL_STUDIES_MIGRATION_ENABLED':'true','SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL':'synthetic-private'},run=run)
    report=json.loads(target.read_text())
    assert not report['complete'] and report['owners']['scribeswell']['outcome_requires_reconciliation']
    assert not target.with_name('studies-migrations.json').exists()
    assert 'private payload' not in target.read_text()


@pytest.mark.parametrize('observation',[None,{'scribeswell_studies_before':None,'scribeswell_studies_after':'scribeswell_studies_0001'},
    {'scribeswell_studies_before':None,'scribeswell_studies_after':'scribeswell_studies_0009'}])
def test_worker_requires_committed_observations(monkeypatch,observation):
    import studies_migrate
    from alembic import command
    def upgrade(config,target):
        assert target=='head'
        assert config.attributes['scribeswell_studies_expected_head']=='scribeswell_studies_0009'
        if observation:config.attributes.update(observation)
    monkeypatch.setattr(command,'upgrade',upgrade)
    monkeypatch.setattr(command,'current',lambda *a,**k:pytest.fail('must not query a second connection'))
    environment={'SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL':'postgresql://scribeswell_studies_migrator:synthetic@127.0.0.1/postgres'}
    # upgrade deliberately publishes its validated URL for Alembic. Own that
    # mutation so later no-migration-authority image oracles stay isolated.
    monkeypatch.setenv('SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL',environment['SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL'])
    if observation and observation['scribeswell_studies_after']=='scribeswell_studies_0009':
        assert studies_migrate.upgrade(environment)==private_report(None)
    else:
        with pytest.raises((KeyError,ValueError)):studies_migrate.upgrade(environment)


def test_worker_rejects_packaged_target_mismatch_before_migration(tmp_path,monkeypatch):
    import shutil
    import studies_migrate
    from alembic import command
    app=ROOT/'apps/scribeswell'
    shutil.copytree(app/'studies-migrations',tmp_path/'studies-migrations')
    shutil.copy2(app/'studies-alembic.ini',tmp_path/'studies-alembic.ini')
    (tmp_path/'studies-migrations/versions/0009_note_metadata_predicates.py').unlink()
    monkeypatch.setattr(studies_migrate,'APP',tmp_path)
    monkeypatch.setattr(command,'upgrade',lambda *a,**k:pytest.fail('history mismatch must precede DB work'))
    monkeypatch.setenv('SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL','postgresql://scribeswell_studies_migrator:synthetic@127.0.0.1/postgres')
    with pytest.raises(ValueError,match='history_invalid'):
        studies_migrate.upgrade({'SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL':'postgresql://scribeswell_studies_migrator:synthetic@127.0.0.1/postgres'})


def test_private_timeout_reaps_child_and_retains_unknown_without_success(tmp_path,monkeypatch):
    import json
    import subprocess
    spec=importlib.util.spec_from_file_location('private_timeout_entry',ROOT/'apps/scribeswell/deployment/migrate.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    monkeypatch.setattr(module,'validate_url',lambda env:'synthetic-corpus')
    children=[];events=[]
    class Child:
        def __init__(self,*args,**kwargs):
            self.private=bool(children);self.returncode=None if self.private else 0;children.append(self)
        def communicate(self,*args,**kwargs):
            if not self.private:return json.dumps({'before':None,'after':'scribeswell_0003','validation':{'profile':'dormant','custody_sha256':None}}),''
            events.append('communicate')
            if self.returncode is None:raise subprocess.TimeoutExpired('private-worker',.01)
            return '',None
        def kill(self):events.append('kill');self.returncode=-9
        def poll(self):return self.returncode
    target=tmp_path/'migrations.json'
    env={'SCRIBESWELL_STUDIES_MIGRATION_ENABLED':'true','SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL':'synthetic-private'}
    with pytest.raises(SystemExit):module.main(target,environ=env,run=Child,timeout=.01)
    report=json.loads(target.read_text())
    assert not report['complete'] and report['owners']['scribeswell']['status']=='unknown'
    assert report['owners']['scribeswell']['outcome_requires_reconciliation']
    assert not target.with_name('studies-migrations.json').exists()
    assert events==['communicate','kill','communicate']


def test_existing_private_evidence_refused_before_children_and_preserved(tmp_path,monkeypatch):
    spec=importlib.util.spec_from_file_location('private_existing_entry',ROOT/'apps/scribeswell/deployment/migrate.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    private=tmp_path/'studies-migrations.json';private.write_text('existing evidence')
    env={'SCRIBESWELL_STUDIES_MIGRATION_ENABLED':'true','SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL':'synthetic-private'}
    with pytest.raises(SystemExit):module.main(tmp_path/'migrations.json',environ=env,run=lambda *a,**k:pytest.fail('must not launch'))
    assert private.read_text()=='existing evidence'
