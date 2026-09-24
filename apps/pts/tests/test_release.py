import subprocess
from contextlib import nullcontext
import pytest
from tools.py.deploy_pts import migrate

def test_failure_stops_later_histories_without_reverse(monkeypatch):
    for name in ('ACCESS','CONTENT','PTS'): monkeypatch.setenv(name+'_MIGRATION_DATABASE_URL','configured')
    calls=[]
    def run(command,check):
        calls.append(command)
        if len(calls)==2: raise subprocess.CalledProcessError(1,command)
    with pytest.raises(subprocess.CalledProcessError): migrate(run,acquire_lock=nullcontext)
    assert len(calls)==2
    assert all(c[-2:]==['upgrade','head'] for c in calls)


def test_cli_evidence_never_authorizes_activation_and_preserves_existing(tmp_path,monkeypatch):
    import json,sys
    from tools.py import deploy_pts
    evidence=tmp_path/'release.json'
    monkeypatch.setattr(sys,'argv',['deploy_pts','--release-id','test-release','--evidence',str(evidence)])
    monkeypatch.setattr(deploy_pts,'migrate',lambda **kwargs: None)
    deploy_pts.main()
    report=json.loads(evidence.read_text())
    assert report['migrations_complete'] is True
    assert report['activation_allowed'] is False
    assert report['code_revision']
    with pytest.raises(SystemExit):deploy_pts.main()
    evidence.unlink()
    def fail(**kwargs):raise RuntimeError('deliberate test failure')
    monkeypatch.setattr(deploy_pts,'migrate',fail)
    with pytest.raises(RuntimeError):deploy_pts.main()
    report=json.loads(evidence.read_text())
    assert report['activation_allowed'] is False
    assert report['migrations_complete'] is False
    assert report['code']=='migration_failed'


def test_owner_evidence_identifies_partial_failure(monkeypatch):
    from tools.py.deploy_pts import OWNERS
    for name in ('ACCESS','CONTENT','PTS'):monkeypatch.setenv(name+'_MIGRATION_DATABASE_URL','configured')
    progress={name:{'status':'not_attempted'} for name,_ in OWNERS}
    def run(command,check):
        if 'content-service' in ' '.join(command):raise subprocess.CalledProcessError(1,command)
    with pytest.raises(subprocess.CalledProcessError):
        migrate(run,acquire_lock=nullcontext,progress=progress,inspect=lambda owner:[owner+'_test'])
    assert progress['access']['status']=='succeeded'
    assert progress['content']['status']=='failed'
    assert progress['pts']['status']=='not_attempted'
    assert progress['content']['before']==progress['content']['after']==['content_test']
