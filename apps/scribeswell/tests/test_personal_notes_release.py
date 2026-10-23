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
            return json.dumps({'complete':True,'owner':'scribeswell_studies','after':'scribeswell_studies_0001','recovery':'forward-only'} if private_succeeds else {'complete':False,'code':'scribeswell_studies_migration_failed'}),''
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
