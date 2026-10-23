"""Operational profile propagation; custody here is synthetic fixture evidence."""
import hashlib
import io
import json
import subprocess
import sys
import time
import pytest
from test_owned_migrations import load_adapter, migration_url, VALID_ENV
from test_corpus_publication import controller_database, enabled
from test_prepared_controller_profile import staged, CUSTODY
from test_controller_history_profile import chain, state

PROFILE_ENV = 'SCRIBESWELL_MIGRATION_PROFILE'
CUSTODY_ENV = 'SCRIBESWELL_MIGRATION_CUSTODY_JSON'


def environment(profile):
    return {PROFILE_ENV: profile, CUSTODY_ENV: json.dumps(CUSTODY)}


def proof(profile,custody=CUSTODY):
    digest = hashlib.sha256(json.dumps(custody,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'profile':profile,'custody_sha256':digest}


@pytest.mark.parametrize('profile',['prepared-controller-v1','controller-history-v1'])
def test_real_supervised_replay_carries_selected_profile(staged,tmp_path,monkeypatch,profile):
    admin,url=staged
    if profile=='controller-history-v1':chain(staged)
    before=state(admin,url)
    adapter=load_adapter()
    monkeypatch.setattr(adapter,'validate_url',lambda env:migration_url(url))
    result=adapter.main(tmp_path/'evidence.json',environ=environment(profile))
    assert result['complete'] is True
    entry=result['owners']['scribeswell']
    assert entry['validation']==entry['requested_validation']==proof(profile)
    assert entry['before']==entry['after']=='scribeswell_0003'
    assert state(admin,url)==before
    raw=(tmp_path/'evidence.json').read_text()
    assert CUSTODY['executor_actor_id'] not in raw and 'postgresql' not in raw


@pytest.mark.parametrize('extra',[
    {PROFILE_ENV:'unknown'}, {PROFILE_ENV:''}, {CUSTODY_ENV:json.dumps(CUSTODY)},
    {PROFILE_ENV:'prepared-controller-v1'},
    environment('dormant'), environment('controller-history-v1')|{CUSTODY_ENV:'[]'},
    environment('controller-history-v1')|{CUSTODY_ENV:'{"schema_version":1,"schema_version":1}'},
    environment('controller-history-v1')|{CUSTODY_ENV:' '*4097},
    environment('controller-history-v1')|{CUSTODY_ENV:json.dumps(CUSTODY|{'extra':True})},
    environment('controller-history-v1')|{CUSTODY_ENV:json.dumps(CUSTODY|{'schema_version':True})},
    {'SCRIBESWELL_MIGRATION_PROFIL':'dormant'},
    environment('controller-history-v1')|{CUSTODY_ENV:json.dumps(CUSTODY,indent=2)},
    environment('controller-history-v1')|{CUSTODY_ENV:json.dumps(CUSTODY)+'\r'},
])
def test_invalid_selection_never_starts_worker(tmp_path,extra):
    target=tmp_path/'evidence.json'
    with pytest.raises(SystemExit):
        load_adapter().main(target,environ=VALID_ENV|extra,run=lambda *a,**k:pytest.fail('worker launched'))
    report=json.loads(target.read_text())
    assert report['complete'] is False
    assert 'outcome_requires_reconciliation' not in report['owners']['scribeswell'] or report['owners']['scribeswell']['outcome_requires_reconciliation'] is False


def test_revision_only_worker_success_is_rejected(tmp_path):
    class Process:
        returncode=0
        def __init__(self,*a,**kw):pass
        def communicate(self,*a,**kw):return '{"before":"scribeswell_0003","after":"scribeswell_0003"}',None
        def poll(self):return 0
    with pytest.raises(SystemExit):
        load_adapter().main(tmp_path/'evidence.json',environ=VALID_ENV,run=Process)
    entry=json.loads((tmp_path/'evidence.json').read_text())['owners']['scribeswell']
    assert entry['status']=='failed' and entry['outcome_requires_reconciliation'] is True
    assert 'validation' not in entry


def test_final_evidence_write_failure_removes_success_marker(tmp_path,monkeypatch):
    adapter=load_adapter();calls=[];original=adapter.os.fsync
    def fsync(fd):
        calls.append(1)
        if len(calls)==3:raise OSError('sensitive final write failure')
        original(fd)
    monkeypatch.setattr(adapter.os,'fsync',fsync)
    class Process:
        returncode=0
        def __init__(self,*a,**kw):pass
        def communicate(self,*a,**kw):return json.dumps({'before':'scribeswell_0003','after':'scribeswell_0003','validation':proof('controller-history-v1')}),None
        def poll(self):return 0
    target=tmp_path/'failed.json'
    with pytest.raises(SystemExit):adapter.main(target,environ=VALID_ENV|environment('controller-history-v1'),run=Process)
    report=json.loads(target.read_text());entry=report['owners']['scribeswell']
    assert len(calls)==4 and report['complete'] is False and entry['status']=='failed'
    assert 'validation' not in entry and 'after' not in entry
    assert entry['outcome_requires_reconciliation'] is True
    assert 'sensitive' not in target.read_text()


def test_bad_url_preserves_valid_requested_selection(tmp_path):
    target=tmp_path/'failed.json'
    with pytest.raises(SystemExit):
        load_adapter().main(target,environ={'SUPABASE_URL':'https://demo.supabase.co','SCRIBESWELL_MIGRATION_DATABASE_URL':'sensitive'}|environment('controller-history-v1'),run=lambda *a,**k:pytest.fail('worker started'))
    entry=json.loads(target.read_text())['owners']['scribeswell']
    assert entry['requested_validation']==proof('controller-history-v1')
    assert entry['outcome_requires_reconciliation'] is False
    assert 'sensitive' not in target.read_text()


@pytest.mark.parametrize('raw',['1e999','-1e999','{"extra":1e999}','NaN','Infinity'])
def test_strict_decoder_rejects_nonfinite_numbers(raw):
    from release_profile import strict_json
    with pytest.raises(ValueError,match='^scribeswell_release_profile_invalid$'):strict_json(raw,4096)


@pytest.mark.parametrize('change',[
    {'validation':{'profile':'dormant','custody_sha256':None}},
    {'validation':{'profile':'controller-history-v1','custody_sha256':'0'*64}},
    {'validation':proof('controller-history-v1')|{'extra':'sensitive'}},
    {'before':None}, {'after':'scribeswell_0002'}, {'extra':'sensitive'},
])
def test_parent_rejects_mismatched_worker_evidence(tmp_path,change):
    class Process:
        returncode=0
        def __init__(self,*a,**kw):
            assert PROFILE_ENV not in kw['env'] and CUSTODY_ENV not in kw['env']
        def communicate(self,request,**kw):
            parsed=json.loads(request)
            assert parsed['validation']=={'profile':'controller-history-v1','custody':CUSTODY}
            return json.dumps({'before':'scribeswell_0003','after':'scribeswell_0003','validation':proof('controller-history-v1')}|change),None
        def poll(self):return 0
    target=tmp_path/'evidence.json'
    with pytest.raises(SystemExit):load_adapter().main(target,environ=VALID_ENV|environment('controller-history-v1'),run=Process)
    entry=json.loads(target.read_text())['owners']['scribeswell']
    assert entry['status']=='failed' and entry['outcome_requires_reconciliation']
    assert 'validation' not in entry and 'sensitive' not in target.read_text()


@pytest.mark.parametrize('marker',[None,'dormant','controller-history-v1'])
def test_worker_requires_native_postcommit_marker(monkeypatch,capsys,marker):
    from alembic import command
    def upgrade(config,revision):
        assert config.attributes['scribeswell_validation_profile']=='prepared-controller-v1'
        assert config.attributes['scribeswell_prepared_actor']==CUSTODY
        config.attributes.update(scribeswell_before='scribeswell_0003',scribeswell_after='scribeswell_0003')
        if marker is not None:config.attributes['scribeswell_validated_profile']=marker
    monkeypatch.setattr(command,'upgrade',upgrade)
    request={'url':'postgresql://scribeswell_migrator:fixture@127.0.0.1:1/postgres','validation':{'profile':'prepared-controller-v1','custody':CUSTODY}}
    monkeypatch.setattr(sys,'stdin',io.StringIO(json.dumps(request)))
    with pytest.raises(SystemExit):load_adapter().worker()
    assert json.loads(capsys.readouterr().out)=={'code':'scribeswell_migration_failed','before':'scribeswell_0003'}


@pytest.mark.parametrize('raw',[
    '{}','[]','{"url":"sensitive"}',
    '{"url":"sensitive","validation":null}',
    '{"url":"a","url":"sensitive","validation":null}',
    ' '*16385,
])
def test_worker_rejects_bad_ipc_before_alembic(monkeypatch,capsys,raw):
    from alembic import command
    monkeypatch.setattr(command,'upgrade',lambda *a:pytest.fail('database work'))
    monkeypatch.setattr(sys,'stdin',io.StringIO(raw))
    with pytest.raises(SystemExit):load_adapter().worker()
    assert json.loads(capsys.readouterr().out)=={'code':'scribeswell_migration_failed'}


def test_history_supervisor_timeout_and_explicit_reconciliation(staged,tmp_path,monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    import signal
    import psycopg
    admin,url=staged;chain(staged);before=state(admin,url)
    adapter=load_adapter();monkeypatch.setattr(adapter,'validate_url',lambda env:migration_url(url))
    target=tmp_path/'timeout.json'
    children=[]
    def launch(*args,**kwargs):
        child=subprocess.Popen(*args,**kwargs);children.append(child);return child
    with psycopg.connect(url,autocommit=True) as observer:
        with admin.transaction():
            admin.execute('SELECT pg_advisory_xact_lock(31003,1)')
            with ThreadPoolExecutor(max_workers=1) as executor:
                attempt=executor.submit(adapter.main,target,environ=environment('controller-history-v1'),timeout=2.5,run=launch)
                deadline=time.monotonic()+2
                waiting=[]
                while time.monotonic()<deadline:
                    waiting=observer.execute("SELECT pid FROM pg_stat_activity WHERE usename='scribeswell_migrator' AND datname=current_database() AND wait_event='advisory'").fetchall()
                    if waiting:break
                    time.sleep(.02)
                assert waiting,'actual worker must reach controller advisory lock'
                # Force the supervisor branch independently of native lock expiry.
                children[0].send_signal(signal.SIGSTOP)
                with pytest.raises(SystemExit):attempt.result(timeout=8)
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                remaining=observer.execute('SELECT pid FROM pg_stat_activity WHERE pid=ANY(%s)',([r[0] for r in waiting],)).fetchall()
                if not remaining:break
                time.sleep(.02)
            assert not remaining
    entry=json.loads(target.read_text())['owners']['scribeswell']
    assert entry['status']=='unknown' and entry['outcome_requires_reconciliation'] is True
    assert children[0].returncode == -signal.SIGKILL
    assert 'validation' not in entry and state(admin,url)==before
    result=adapter.main(tmp_path/'reconciled.json',environ=environment('controller-history-v1'))
    assert result['complete'] is True and state(admin,url)==before


@pytest.mark.parametrize('profile',[None,'prepared-controller-v1'])
def test_history_never_selects_profile_by_target_drift(staged,tmp_path,monkeypatch,profile):
    admin,url=staged;chain(staged);before=state(admin,url)
    adapter=load_adapter();monkeypatch.setattr(adapter,'validate_url',lambda env:migration_url(url))
    target=tmp_path/'denied.json'
    with pytest.raises(SystemExit):adapter.main(target,environ={} if profile is None else environment(profile))
    entry=json.loads(target.read_text())['owners']['scribeswell']
    assert entry['status']=='failed' and 'validation' not in entry
    assert state(admin,url)==before


def test_actual_commit_ack_loss_through_supervised_worker(staged,tmp_path,monkeypatch):
    from pathlib import Path
    from test_owned_migrations import APP
    admin,url=staged;chain(staged)
    admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
    before=state(admin,url)
    # Test-only child instrumentation: real DBAPI COMMIT, then injected lost reply.
    wrapper=tmp_path/'ack_loss.py'
    wrapper.write_text('''import runpy,sys
from pathlib import Path
app=Path(sys.argv[1])
sys.path.insert(0,str(app/'migrations'))
import baseline
from sqlalchemy.dialects.postgresql.psycopg import PGDialect_psycopg
original=PGDialect_psycopg.do_commit
checked=baseline.preflight_controller_history
calls=[]
def check(connection,actor):
    result=checked(connection,actor)
    calls.append(1)
    if len(calls)==2:
        connection.exec_driver_sql("UPDATE scribeswell.book SET name_en='committed before response loss' WHERE id=1")
    return result
def lost(self,connection):
    assert calls==[1,1]
    original(self,connection)
    raise RuntimeError('sensitive injected acknowledgement loss')
baseline.preflight_controller_history=check
PGDialect_psycopg.do_commit=lost
runpy.run_path(str(app/'deployment/migrate.py'))['worker']()
''')
    def launch(command,**kwargs):return subprocess.Popen([sys.executable,str(wrapper),str(APP)],**kwargs)
    adapter=load_adapter();monkeypatch.setattr(adapter,'validate_url',lambda env:migration_url(url))
    target=tmp_path/'unknown.json'
    with pytest.raises(SystemExit):adapter.main(target,environ=environment('controller-history-v1'),run=launch)
    entry=json.loads(target.read_text())['owners']['scribeswell']
    assert entry['status']=='failed' and entry['before']=='scribeswell_0003'
    assert entry['outcome_requires_reconciliation'] and 'validation' not in entry
    assert 'sensitive' not in target.read_text()
    assert admin.execute('SELECT name_en FROM scribeswell.book WHERE id=1').fetchone()==('committed before response loss',)
    after=state(admin,url)
    assert before[0]==after[0] and before[2]==after[2]
    assert adapter.main(tmp_path/'reconciled.json',environ=environment('controller-history-v1'))['complete'] is True
    assert state(admin,url)==after


@pytest.mark.parametrize('mode',['prepared','history','paused','rotated','denied'])
def test_real_host_coordinator_consumes_actual_supervised_replay(staged,tmp_path,monkeypatch,mode):
    from pathlib import Path
    from unittest.mock import patch
    from test_owned_migrations import APP
    from test_corpus_publication import operator, execute, body
    import importlib.util
    root=APP.parents[1]
    sys.path.insert(0,str(root/'platform/deployment/tests'))
    spec=importlib.util.spec_from_file_location('host_fixture_for_scribeswell',root/'platform/deployment/tests/test_host.py')
    fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
    host=fixture.host;harness=fixture.Host();harness.setup_target(tmp_path)
    profile='prepared-controller-v1' if mode=='prepared' else 'controller-history-v1'
    admin,url=staged;expected=dict(CUSTODY)
    if mode!='prepared':commands=chain(staged)
    if mode=='paused':
        admin.execute('UPDATE scribeswell.corpus_fence_control SET enforcement=false')
        admin.execute('UPDATE scribeswell.corpus_operator_principal SET enabled=false,revision=revision+1')
        admin.execute('UPDATE scribeswell.corpus_operator_authority SET enabled=false,revision=revision+1')
    if mode=='rotated':
        replacement='33333333-3333-4333-8333-333333333333'
        admin.execute('UPDATE scribeswell.corpus_operator_principal SET executor_actor_id=%s,revision=revision+1,updated_by_actor_id=%s',(replacement,replacement))
        expected['executor_actor_id']=replacement
        with operator(url) as connection:execute(connection,body('recover',commands[-1][1]))
    if mode=='denied':expected['actor_key']='fixture.wrong'
    path=tmp_path/'env/scribeswell-migrations.env'
    path.write_text(path.read_text()+PROFILE_ENV+'='+profile+'\n'+CUSTODY_ENV+'='+json.dumps(expected)+'\n')
    before=state(admin,url);calls=[]
    adapter=load_adapter();monkeypatch.setattr(adapter,'validate_url',lambda env:migration_url(url))
    def execute_host(command,**kwargs):
        calls.append(command)
        if command[:2]!=['docker','run']:return
        frozen=Path(command[command.index('--env-file')+1])
        if frozen.name=='scribeswell-migrations.env':
            evidence=Path(command[command.index('-v')+1].removesuffix(':/evidence'))/'migrations.json'
            try:adapter.main(evidence,environ=host.env_values(frozen))
            except SystemExit:raise subprocess.CalledProcessError(1,command) from None
        else:harness.migration_report(command,{'complete':True,'owners':{}})
    def render(output,*args):output.mkdir();(output/'apisix.yaml').write_text('fake');return {}
    with patch.object(host,'require_compose'),patch.object(host,'render',side_effect=render),patch.object(host.os,'chown'),patch.object(host,'execute',side_effect=execute_host),patch.object(host.subprocess,'check_output',return_value=''),patch.object(host,'supervisor_events',return_value={}):
        if mode=='denied':
            with pytest.raises(subprocess.CalledProcessError):harness.deploy(tmp_path)
        else:harness.deploy(tmp_path)
    report=json.loads((tmp_path/'attempt/evidence.json').read_text())
    assert report['activated'] is (mode!='denied')
    assert report['migrations']['pts-owned']['status']=='succeeded'
    entry=report['migrations']['scribeswell-owned']
    assert entry['network']['cleanup']=='removed'
    actual=entry['detail']['owners']['scribeswell']
    if mode=='denied':
        assert entry['status']==actual['status']=='failed'
        assert actual['outcome_requires_reconciliation'] is True and 'validation' not in actual
        assert 'postgresql' not in json.dumps(report) and 'fixture.wrong' not in json.dumps(report)
    else:assert actual['validation']==proof(profile,expected)
    assert state(admin,url)==before
    assert any(c[:2]==['docker','compose'] for c in calls) is (mode!='denied')
