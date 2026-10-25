"""Qualification control-flow acceptance; doubles never establish owner readiness."""
from pathlib import Path
import sys
import uuid
import pytest

HERE=Path(__file__).parent
sys.path.insert(0,str(HERE))

def fixture_module():
    import studies_owner_fixture
    return studies_owner_fixture

@pytest.fixture(autouse=True)
def free_ports(monkeypatch,tmp_path):
    module=fixture_module()
    detector=module.check_ports
    monkeypatch.setattr(module,"check_ports",lambda:None)
    monkeypatch.setattr(module,"RESERVATIONS",tmp_path/'reservations')
    return detector

def test_missing_capability_has_explicit_one_run_entry():
    module=fixture_module()
    assert callable(module.qualify)
    assert (HERE.parent/'tools/py/qualify_studies_owner_integration.py').is_file()
    assert (HERE.parent/'web/tests/studies-owner.integration.cjs').is_file()

def test_failed_preparation_never_starts_apps_and_stops_only_owned_run(tmp_path):
    module=fixture_module(); events=[]
    class Failed(module.Qualification):
        def wrapper(self,action):events.append(action)
        def capture_status(self):events.append('status')
        def prepare_owners(self):raise RuntimeError('synthetic_preparation_failure')
        def start_apps(self):events.append('apps')
    run=Failed(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof')
    with pytest.raises(RuntimeError,match='synthetic_preparation_failure'):run.execute()
    assert events==['prepare','up','verify','status','stop']
    assert run.events[-1]['stage']=='failed'
    assert (run.proof/'result.json').stat().st_mode&0o777==0o600

def test_existing_proof_and_noncanonical_run_refuse(tmp_path):
    module=fixture_module()
    with pytest.raises(ValueError):module.Qualification('not-a-uuid',Path('/explicit/supabase'),tmp_path/'proof')
    proof=tmp_path/'existing';proof.mkdir()
    with pytest.raises(FileExistsError):module.Qualification(str(uuid.uuid4()),Path('/explicit/supabase'),proof)

def test_collision_refuses_before_wrapper_or_adoption(tmp_path,monkeypatch,free_ports):
    import socket
    module=fixture_module();run=module.Qualification(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof')
    with socket.socket() as listener:
        listener.bind(('127.0.0.1',0));listener.listen()
        monkeypatch.setattr(module,'PORTS',(listener.getsockname()[1],))
        monkeypatch.setattr(module,'check_ports',free_ports)
        called=[];monkeypatch.setattr(run,'wrapper',lambda action:called.append(action))
        with pytest.raises(RuntimeError,match='qualification_port_occupied'):run.execute()
    assert not called

def test_interrupt_stops_owned_processes_and_exact_run(tmp_path):
    module=fixture_module();events=[]
    class Interrupted(module.Qualification):
        def wrapper(self,action):events.append(action)
        def capture_status(self):pass
        def prepare_owners(self):raise KeyboardInterrupt()
    with pytest.raises(KeyboardInterrupt):Interrupted(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof').execute()
    assert events==['prepare','up','verify','stop']

def test_exact_run_stop_failure_is_a_failure(tmp_path):
    module=fixture_module()
    class StopFailed(module.Qualification):
        def wrapper(self,action):
            if action=='stop':raise RuntimeError('synthetic_stop_failure')
        def capture_status(self):pass
        def prepare_owners(self):raise RuntimeError('synthetic_preparation_failure')
    run=StopFailed(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof')
    with pytest.raises(RuntimeError,match='qualification_exact_run_stop_failed'):run.execute()
    assert run.events[-1]['stage']=='stop-failed'

def test_exited_launcher_still_terminates_its_owned_group(tmp_path,monkeypatch):
    module=fixture_module();signals=[]
    class Process:
        pid=100000
        def poll(self):return 0
        def wait(self,timeout):return 0
    class Failed(module.Qualification):
        def wrapper(self,action):pass
        def capture_status(self):pass
        def prepare_owners(self):raise RuntimeError('synthetic_failure')
    def killpg(pid,signum):
        signals.append((pid,signum))
        if signum==0:raise ProcessLookupError()
    monkeypatch.setattr(module.os,'killpg',killpg)
    run=Failed(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof');run.processes.append(Process())
    with pytest.raises(RuntimeError,match='synthetic_failure'):run.execute()
    assert signals[0]==(100000,module.signal.SIGTERM)

def test_process_cleanup_error_still_stops_exact_native_run(tmp_path):
    module=fixture_module();actions=[]
    class Process:pid=100000
    class Failed(module.Qualification):
        def wrapper(self,action):actions.append(action)
        def capture_status(self):pass
        def prepare_owners(self):raise RuntimeError('synthetic_failure')
        def stop_process(self,process):raise OSError('synthetic_cleanup_failure')
    run=Failed(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof');run.processes.append(Process())
    with pytest.raises(RuntimeError,match='qualification_exact_run_stop_failed'):run.execute()
    assert actions[-1]=='stop'
    assert any(e['stage']=='process-stop-failed' for e in run.events)

def test_callback_failure_never_writes_signed_url_diagnostics(tmp_path):
    """Execute a throwing callback scenario through real Playwright failure output."""
    import json
    import subprocess
    module=fixture_module();reporter=module.APP/'web/tests/studies-owner-reporter.cjs'
    # A harness fault, not an Auth response/session/private HTTP substitute.
    sentinel='http://provider.invalid/verify?token=private-synthetic-token'
    test_file=module.APP/'web/tests'/('owner-safety-'+uuid.uuid4().hex+'.cjs')
    config=tmp_path/'playwright.config.cjs'
    config.write_text('module.exports='+json.dumps({'testDir':str(test_file.parent),'testMatch':test_file.name,'reporter':[[str(reporter)]],'outputDir':str(tmp_path/'results')})+';')
    test_file.write_text("const {test}=require('@playwright/test');const {safeCall}=require('./studies-owner-reporter.cjs');test('callback failure',async()=>safeCall(async()=>{throw new Error("+json.dumps(sentinel)+");}));")
    try:
        result=subprocess.run(['node',str(module.ROOT/'node_modules/@playwright/test/cli.js'),'test','--config',str(config)],capture_output=True,text=True,timeout=30,env={**module.os.environ,'PLAYWRIGHT_NO_COPY_PROMPT':'1'})
        assert result.returncode==1
        diagnostics=result.stdout+result.stderr+'\n'.join(p.read_text(errors='replace') for p in (tmp_path/'results').rglob('*') if p.is_file())
        assert sentinel not in diagnostics
        assert 'private-synthetic-token' not in diagnostics
        assert 'browser-case' in result.stdout
    finally:test_file.unlink(missing_ok=True)

@pytest.mark.parametrize('interrupt',[False,True])
def test_timed_out_or_interrupted_command_stops_real_descendant_before_return(tmp_path,interrupt):
    import os
    import signal
    import subprocess
    import time
    module=fixture_module();run=module.Qualification(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof')
    pidfile=tmp_path/'descendant.pid'
    child_code='import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(60)'
    launcher='import subprocess,sys,time;from pathlib import Path;p=subprocess.Popen([sys.executable,"-c",'+repr(child_code)+']);Path('+repr(str(pidfile))+').write_text(str(p.pid));time.sleep(60)'
    thread=None
    if interrupt:
        import threading
        def interrupt_when_started():
            limit=time.monotonic()+3
            while not pidfile.exists() and time.monotonic()<limit:time.sleep(.01)
            if pidfile.exists():os.kill(os.getpid(),signal.SIGINT)
        thread=threading.Thread(target=interrupt_when_started,daemon=True);thread.start()
    try:
        with pytest.raises(KeyboardInterrupt if interrupt else subprocess.TimeoutExpired):
            run.command('synthetic-child-boundary',[sys.executable,'-c',launcher],timeout=5 if interrupt else .5)
        if thread:thread.join(timeout=3)
        pid=int(pidfile.read_text())
        state=Path('/proc')/str(pid)/'stat'
        assert not state.exists() or state.read_text().split()[2]=='Z','Owned command descendant still executes after timeout'
        assert any(e.get('stage')=='process-stopped' and e.get('forced') and e.get('termination_confirmed') for e in run.events)
    finally:
        if pidfile.exists():
            try:os.kill(int(pidfile.read_text()),signal.SIGKILL)
            except ProcessLookupError:pass

def test_concurrent_same_uuid_cannot_adopt_or_clean_reserved_run(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    module=fixture_module();run_id=str(uuid.uuid4())
    def reserve(index):
        try:return module.Qualification(run_id,Path('/explicit/supabase'),tmp_path/('proof-'+str(index)))
        except FileExistsError:return None
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(reserve,range(2)))
    owners=[item for item in results if item is not None]
    assert len(owners)==1
    reservation=owners[0].reservation;before=reservation.read_bytes()
    assert reservation.stat().st_mode&0o777==0o600
    with pytest.raises(FileExistsError):module.Qualification(run_id,Path('/explicit/supabase'),tmp_path/'third-proof')
    assert reservation.read_bytes()==before and not owners[0].run.exists()
    assert not owners[0].owned and not owners[0].events

def test_sources_cover_executed_inputs_and_new_consumed_file(tmp_path,monkeypatch):
    module=fixture_module();inventory=module.source_inventory()
    for path in (module.APP/'tools/sql/prepare_personal_notes_roles.sql',module.APP/'supabase/migrations/20260614000000_scribeswell_create_schema.sql',module.APP/'studies-alembic.ini',module.ACCESS/'identity-alembic.ini',module.ACCESS/'alembic.ini'):
        assert path in inventory
    app=tmp_path/'app';(app/'backend').mkdir(parents=True)
    monkeypatch.setattr(module,'APP',app)
    run=object.__new__(module.Qualification);run.sources=module.source_inventory()
    consumed=app/'backend/new_consumed.py';consumed.write_text('new_input=True\n')
    assert consumed in module.source_inventory()
    with pytest.raises(RuntimeError,match='qualification_sources_changed'):run.verify_sources()

def test_fixture_sql_connections_bound_statements_and_locks(tmp_path,monkeypatch):
    import psycopg
    from sqlalchemy.engine import make_url
    module=fixture_module();run=module.Qualification(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof')
    run.admin=make_url('postgresql://synthetic:synthetic@127.0.0.1/postgres');calls=[]
    monkeypatch.setattr(psycopg,'connect',lambda *args,**kwargs:calls.append(kwargs))
    run.connect()
    assert calls[0]['connect_timeout']==3
    assert 'statement_timeout=20000' in calls[0]['options'] and 'lock_timeout=3000' in calls[0]['options']

@pytest.mark.parametrize('table',['identity.studies_setup_outcome','identity.studies_setup_event','access.studies_enrollment_outcome','access.studies_assignment_event','scribeswell_studies.receipts'])
def test_initial_zero_effect_oracle_refuses_any_retained_outcome_or_event(table):
    module=fixture_module();state={name:[] for name in module.PROTECTED_TABLES};state[table]=[{'operation_id':'unexpected'}]
    with pytest.raises(AssertionError,match='Protected effects'):module.empty_protected_state(state)

@pytest.mark.parametrize('table,field',[('scribeswell_studies.studies','revision'),('scribeswell_studies.notes','updated_at'),('scribeswell_studies.receipts','outcome'),('identity.studies_setup_outcome','actor_id'),('access.studies_enrollment_outcome','disposition')])
def test_denial_oracle_compares_complete_rows(table,field):
    import copy
    module=fixture_module();before={name:[] for name in module.PROTECTED_TABLES};before[table]=[{field:'before'}]
    after=copy.deepcopy(before);after[table][0][field]='after'
    with pytest.raises(AssertionError,match='Denied operation changed'):module.unchanged_state(before,after)

def test_cleanup_fails_when_actual_descendant_stop_cannot_be_confirmed(tmp_path,monkeypatch):
    module=fixture_module();run=module.Qualification(str(uuid.uuid4()),Path('/explicit/supabase'),tmp_path/'proof');clock=iter(range(0,100,2))
    class Process:
        pid=100000
        def poll(self):return 0
        def wait(self,timeout):return 0
    monkeypatch.setattr(module,'executing_group_members',lambda group:[123])
    monkeypatch.setattr(module.os,'killpg',lambda *args:None)
    monkeypatch.setattr(module.time,'monotonic',lambda:next(clock))
    monkeypatch.setattr(module.time,'sleep',lambda duration:None)
    with pytest.raises(OSError,match='termination_unconfirmed'):run.stop_process(Process())
    assert not any(e['stage']=='process-stopped' for e in run.events)

@pytest.mark.parametrize('channel',['request-url','request-body','response-header','other-response-body','websocket'])
def test_service_sentinels_cover_browser_channels_without_payload_logs(tmp_path,channel):
    import json,subprocess
    module=fixture_module();helper=module.APP/'web/tests/studies-owner-privacy.cjs'
    code="""const {EventEmitter}=require('events');const {credentialInspection}=require(process.argv[1]);
const context=new EventEmitter();context.pages=()=>[];const inspection=credentialInspection(['private-test-key']);inspection.inspect(context);
const channel=process.argv[2];
if(channel.startsWith('request'))context.emit('request',{url:()=>channel==='request-url'?'http://x/?key=private-test-key':'http://x/',headers:()=>({}),postData:()=>channel==='request-body'?'private-test-key':null});
else if(channel==='websocket'){const page=new EventEmitter();context.emit('page',page);const socket=new EventEmitter();socket.url=()=> 'ws://x/';page.emit('websocket',socket);socket.emit('framereceived',{payload:'private-test-key'});}
else context.emit('response',{url:()=> 'http://other-origin/',headers:()=>channel==='response-header'?{'x-key':'private-test-key'}:{'content-type':'application/octet-stream'},status:()=>200,body:async()=>Buffer.from(channel==='other-response-body'?'private-test-key':'safe')});
inspection.settle().then(()=>process.exit(1),()=>console.log('sentinel-rejected'));
"""
    result=subprocess.run(['node','-e',code,str(helper),channel],capture_output=True,text=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='sentinel-rejected'
    assert 'private-test-key' not in result.stdout+result.stderr

@pytest.mark.parametrize('study_closed',[False,True])
@pytest.mark.parametrize('change',[None,'missing-other-binding','wrong-other-binding','study-creation-actor','study-update-actor','note-actor','receipt-actor','deleted-value','deleted-active','retained-active','retained-creation-actor','retained-update-actor'])
def test_final_oracle_checks_both_durable_bindings_and_all_record_actors(tmp_path,change,study_closed):
    import copy
    module=fixture_module();state={name:[] for name in module.PROTECTED_TABLES}
    expected={'study':'ui-study','retry_study':'retry-study','note':'note','retained_note':'retained-note','note_delete_operation':'delete-op','operation':'retry-op','ui_operation':'ui-op','enrollment':'retry-enroll','ui_enrollment':'ui-enroll','other_enrollment':'other-enroll','account_actors':{'owner':'actor-a','other':'actor-b'},'value':{'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}}
    state['identity.users']=[{'id':'owner'},{'id':'other'}]
    state['identity.actor']=[{'id':'service','kind':'service'},{'id':'actor-a','kind':'account'},{'id':'actor-b','kind':'account'}]
    state['identity.account_actor']=[{'account_id':a,'actor_id':b} for a,b in expected['account_actors'].items()]
    attribution={'account_id':'owner','created_by':'actor-a','updated_by':'actor-a','created_at':'2026-01-01','updated_at':'2026-01-01','revision':1}
    state['scribeswell_studies.studies']=[dict(attribution,id=id) for id in ('ui-study','retry-study')]
    state['scribeswell_studies.notes']=[dict(attribution,id='note',study_id='ui-study',value=copy.deepcopy(expected['value']),active=False),dict(attribution,id='retained-note',study_id='ui-study',value={'document':'retained-oracle-value'},active=True)]
    state['scribeswell_studies.notes'][0]['revision']=2
    state['scribeswell_studies.receipts']=[{'command':command,'operation_id':operation,'account_id':'owner','created_by':'actor-a','created_at':'2026-01-01'} for command,operation in [('study.create','ui-op'),('study.create','retry-op'),('note.create','note-op'),('note.replace','replace-op'),('note.create','retained-note-op'),('note.delete','delete-op')]]
    if study_closed:
        expected['study_delete_operation']='study-delete-op'
        state['scribeswell_studies.studies'][0].update(active=False,title='Deleted study',revision=3)
        state['scribeswell_studies.studies'][1]['active']=True
        state['scribeswell_studies.notes'][1].update(active=False,value=copy.deepcopy(expected['value']))
        state['scribeswell_studies.receipts'].append({'command':'study.delete','operation_id':'study-delete-op','account_id':'owner','created_by':'actor-a','created_at':'2026-01-01'})
    for table in ('access.studies_account_grant','access.studies_assignment_event','identity.studies_setup_event'):
        state[table]=copy.deepcopy(state['identity.account_actor'])
    for table in ('access.studies_enrollment_outcome','identity.studies_setup_outcome'):
        state[table]=[{'account_id':'owner','actor_id':'actor-a','operation_id':'ui-enroll'},{'account_id':'other','actor_id':'actor-b','operation_id':'other-enroll'}]
    state['access.studies_enrollment_outcome'].append({'account_id':'owner','actor_id':'actor-a','operation_id':'retry-enroll'})
    if change=='missing-other-binding':state['identity.account_actor'].pop()
    if change=='wrong-other-binding':state['identity.account_actor'][1]['actor_id']='actor-a'
    for label,table,field in [('study-creation-actor','scribeswell_studies.studies','created_by'),('study-update-actor','scribeswell_studies.studies','updated_by'),('note-actor','scribeswell_studies.notes','created_by'),('receipt-actor','scribeswell_studies.receipts','created_by')]:
        if change==label:state[table][0][field]='actor-b'
    if change=='deleted-value':state['scribeswell_studies.notes'][0]['value']={'document':'deleted-content-refilled'}
    if change=='deleted-active':state['scribeswell_studies.notes'][0]['active']=True
    if change=='retained-active':state['scribeswell_studies.notes'][1]['active']=study_closed
    if change=='retained-creation-actor':state['scribeswell_studies.notes'][1]['created_by']='actor-b'
    if change=='retained-update-actor':state['scribeswell_studies.notes'][1]['updated_by']='actor-b'
    run=object.__new__(module.Qualification);run.proof=tmp_path;run.actor='service';run.accounts=[{'account_id':'owner'},{'account_id':'other'}];run.snapshot=lambda label:state
    module.private(tmp_path/'browser-result.json',expected)
    if change:
        with pytest.raises(AssertionError):run.observe('synthetic-oracle')
    else:run.observe('synthetic-oracle')

@pytest.mark.parametrize('change',[None,'value','revision','delete','extra'])
def test_note_link_checkpoint_refuses_changes_to_every_non_target_note(change):
    import copy
    module=fixture_module()
    before=[{'id':'target','study_id':'study-a','revision':1,'value':'original'},
            {'id':'other','study_id':'study-b','revision':7,'value':'unrelated'}]
    after=copy.deepcopy(before);after[0].update(revision=2,value='rich target')
    if change=='value':after[1]['value']='unexpected'
    elif change=='revision':after[1]['revision']=8
    elif change=='delete':after.pop()
    elif change=='extra':after.append({'id':'new-other','revision':1,'value':'unexpected'})
    if change:
        with pytest.raises(AssertionError,match='another note'):
            module.assert_non_target_notes_unchanged(before,after,'target')
    else:module.assert_non_target_notes_unchanged(before,after,'target')

@pytest.mark.parametrize('tamper',[None,'title','active','note-value','note-revision','inactive-note','passage','receipt','unrelated'])
def test_whole_study_erasure_independent_oracle_retains_other_scope_and_old_tombstones(tamper):
    import copy
    module=fixture_module();before={name:[] for name in module.PROTECTED_TABLES}
    attribution=dict(account_id='owner',created_by='actor',updated_by='actor',created_at='2026-01-01',updated_at='2026-01-01',revision=1,active=True)
    empty={'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}
    before['scribeswell_studies.studies']=[dict(attribution,id='study',title='Private title'),dict(attribution,id='other',title='Other title')]
    before['scribeswell_studies.notes']=[dict(attribution,id='note',study_id='study',value={'private':'body'}),dict(attribution,id='old',study_id='study',active=False,value=copy.deepcopy(empty)),dict(attribution,id='copy',study_id='other',value={'private':'independent'})]
    before['scribeswell_studies.passage_lists']=[dict(study_id='study')];before['scribeswell_studies.passage_entries']=[dict(study_id='study')]
    before['scribeswell_studies.receipts']=[dict(command='note.delete',operation_id='old-op')]
    after=copy.deepcopy(before);after['scribeswell_studies.studies'][0].update(active=False,title='Deleted study',revision=2,updated_at='2026-01-02')
    after['scribeswell_studies.notes'][0].update(active=False,value=copy.deepcopy(empty),revision=2,updated_at='2026-01-02')
    after['scribeswell_studies.passage_lists']=[];after['scribeswell_studies.passage_entries']=[]
    expected=dict(study='study',operation='delete-op',revision='2')
    after['scribeswell_studies.receipts'].append(dict(command='study.delete',operation_id='delete-op',outcome=dict(operation_id='delete-op',command='study.delete',study_id='study',note_id=None,revision='2')))
    if tamper=='title':after['scribeswell_studies.studies'][0]['title']='Private title'
    if tamper=='active':after['scribeswell_studies.studies'][0]['active']=True
    if tamper=='note-value':after['scribeswell_studies.notes'][0]['value']={'private':'body'}
    if tamper=='note-revision':after['scribeswell_studies.notes'][0]['revision']=1
    if tamper=='inactive-note':after['scribeswell_studies.notes'][1]['revision']=2
    if tamper=='passage':after['scribeswell_studies.passage_entries']=before['scribeswell_studies.passage_entries']
    if tamper=='receipt':after['scribeswell_studies.receipts'].pop(0)
    if tamper=='unrelated':after['scribeswell_studies.notes'][2]['active']=False
    if tamper:
        with pytest.raises(AssertionError):module.assert_study_erasure(before,after,expected)
    else:module.assert_study_erasure(before,after,expected)
