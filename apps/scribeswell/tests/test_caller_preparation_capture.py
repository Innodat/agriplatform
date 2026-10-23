"""End-to-end synthetic local capture; no preparation SQL or live owner work."""
import base64
from dataclasses import replace
import errno
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from test_caller_preparation_evidence import TARGET, VALID, canonical, records, relink, wire
from test_caller_preparation_fixture import FakeProcess, module, target, reject
from test_caller_preparation_storage import custody, RUN, load
from apps.scribeswell.backend.caller_preparation_storage import PreparationStorageError

ROOT=Path(__file__).resolve().parents[3]


def capture(fd,rows=None):
    return module().capture_fixture(fd,request_raw=VALID,target=target(),records=wire(rows or records()))


def test_integrated_capture_acceptance(custody):
    root,fd=custody
    result=capture(fd)
    assert result.status==result.code=='fixture_records_acknowledged'
    assert result.termination=='child_exited'
    assert load(fd)==wire(records())
    assert os.fstat(fd).st_mode & 0o7777==0o700
    assert result.reply.outcome=='committed' # supplied synthetic declaration, not SQL
    for path,raw in zip(sorted((root/RUN).iterdir()),wire(records())):
        assert path.read_bytes()==raw and path.stat().st_mode & 0o7777==0o600


@pytest.mark.parametrize('mode,outcome,count',[('reuse','reused',4),('create','rejected',2),
    ('create','unknown',2),('create','rolled_back',3),('create','unknown',4)])
def test_integrated_terminal_modes(custody,mode,outcome,count):
    root,fd=custody; rows=records(mode,outcome=outcome,count=count)
    result=capture(fd,rows)
    assert result.status=='fixture_records_acknowledged' and result.reply.outcome==outcome
    assert load(fd)==wire(rows)


def test_capture_reuses_supervisor_and_never_reads_storage_in_parent(custody,monkeypatch):
    import apps.scribeswell.backend.caller_preparation_storage as store
    root,fd=custody; m=module(); spawn=m.subprocess.Popen; seen=[]
    def forbidden(*args,**kwargs):pytest.fail('storage called in parent')
    def observe(*args,**kwargs):
        seen.append((args,kwargs))
        assert kwargs['pass_fds'] and len(kwargs['pass_fds'])==1
        assert kwargs['pass_fds'][0]!=fd and kwargs['pass_fds'][0]>=3
        assert not os.get_inheritable(fd)
        return spawn(*args,**kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(store,'create_fixture_attempt',forbidden)
        patch.setattr(store,'read_fixture_prefix',forbidden)
        patch.setattr(m.subprocess,'Popen',observe)
        assert capture(fd).status=='fixture_records_acknowledged'
    assert seen[0][1]['env']=={} and seen[0][1]['stderr']==subprocess.DEVNULL
    assert load(fd)==wire(records())


def test_duplicate_reservation_is_unknown_without_overwrite(custody):
    root,fd=custody
    assert capture(fd).status=='fixture_records_acknowledged'
    before={p.name:p.read_bytes() for p in (root/RUN).iterdir()}
    result=capture(fd)
    assert result.status=='unknown' and result.reply is None
    assert {p.name:p.read_bytes() for p in (root/RUN).iterdir()}==before


@pytest.mark.parametrize('bad',[None,True,-1,'/tmp'])
def test_bad_root_descriptor_safe(custody,bad):
    reject(lambda:capture(bad))
    assert list(custody[0].iterdir())==[]


def test_invalid_root_mode_and_non_directory_do_not_mutate(custody):
    root,fd=custody;root.chmod(0o755)
    assert capture(fd).status=='unknown' and not (root/RUN).exists()
    root.chmod(0o700)
    path=root/'ordinary';path.write_bytes(b'original')
    other=os.open(path,os.O_RDONLY)
    try:assert capture(other).status=='unknown'
    finally:os.close(other)
    assert path.read_bytes()==b'original'


def test_live_invalid_prefix_rejected_before_reservation(custody,monkeypatch):
    root,fd=custody; rows=records();rows[0]['payload']['admission_class']='owner_verified'
    reject(lambda:capture(fd,relink(rows)))
    reject(lambda:module().capture_fixture(fd,request_raw=VALID,target=replace(target(),port=5433),records=wire(records())))
    assert list(root.iterdir())==[]


# Test-only trusted bootstraps inject faults into the real fixed capture entrypoint.
# They are never public command/callback settings.
def fault_driver(monkeypatch,stage,action='exit',later=False):
    m=module()
    script=r'''
import os,sys,time,stat,fcntl
sys.path.insert(0,sys.argv[1])
from apps.scribeswell.backend import caller_preparation_fixture as f
from apps.scribeswell.backend import caller_preparation_storage as store
stage,action,later=sys.argv[3],sys.argv[4],sys.argv[5]=='yes'
append=store.FixtureAttemptWriter.append
count=0
armed=False

def append_wrapper(self,raw):
    global count,armed
    count+=1
    armed=count==(3 if later else 1)
    return append(self,raw)
store.FixtureAttemptWriter.append=append_wrapper
operation={'reserve_mkdir':'mkdir','reserve_open':'open','reserve_lock':'flock','reserve_sync':'fsync','create':'open','write':'write','file_sync':'fsync','link':'link','unlink':'unlink','dir_sync':'fsync','readback':'read_fixture_prefix','close':'close','lost_reply':'write_reply'}[stage]
if operation=='read_fixture_prefix':
    original=store.read_fixture_prefix
    def replacement(*args,**kwargs):
        if action=='stall':time.sleep(10)
        if action=='mismatch':return ()
        raise OSError('private-marker')
    store.read_fixture_prefix=replacement
elif operation=='write_reply':
    class Lost:
        def write(self,*args):raise OSError('private-marker')
        def flush(self):pass
    class Output:buffer=Lost()
    sys.stdout=Output()
else:
    owner=fcntl if operation=='flock' else os
    original=getattr(owner,operation)
    def replacement(*args,**kwargs):
        reservation=stage.startswith('reserve_') and count==0
        if not reservation and not armed and not (operation=='close' and count==4):return original(*args,**kwargs)
        if operation=='open':
            if stage=='reserve_open' and len(str(args[0]))!=36:return original(*args,**kwargs)
            if stage!='reserve_open' and args[0]!='.pending.json':return original(*args,**kwargs)
        if operation=='close':
            # Fail closing the writer's directory after the full final append.
            if count!=4 or not stat.S_ISDIR(os.fstat(args[0]).st_mode):return original(*args,**kwargs)
        if operation=='fsync':
            isdir=stat.S_ISDIR(os.fstat(args[0]).st_mode)
            if isdir!=(stage in ('dir_sync','reserve_sync')):return original(*args,**kwargs)
        if action=='before':raise OSError('private-marker')
        if action=='stall':time.sleep(10)
        if operation=='write' and action in ('exit','fail'):
            result=original(args[0],args[1][:17])
        else:
            result=original(*args,**kwargs)
        if action=='exit':os._exit(73)
        if action=='fail':raise OSError('private-marker')
        return result
    setattr(owner,operation,replacement)
raise SystemExit(f._capture_main(int(sys.argv[2])))
'''
    monkeypatch.setattr(m,'_capture_command',lambda fd:[sys.executable,'-I','-S','-c',script,str(ROOT),str(fd),stage,action,'yes' if later else 'no'])
    monkeypatch.setattr(m,'_WORK_SECONDS',0.7)
    monkeypatch.setattr(m,'_TOTAL_SECONDS',2.0)
    monkeypatch.setattr(m,'_CLEANUP_SECONDS',0.7)


@pytest.mark.parametrize('stage',['create','write','file_sync','link','unlink','dir_sync'])
@pytest.mark.parametrize('later',[False,True])
def test_interrupted_real_capture_retains_exact_earlier_prefix(custody,monkeypatch,stage,later):
    root,fd=custody;fault_driver(monkeypatch,stage,later=later)
    result=capture(fd)
    assert result.status=='unknown' and result.reply is None and result.termination=='child_exited'
    if later:
        for index,raw in enumerate(wire(records())[:2],1):
            assert (root/RUN/f'{index:06d}.json').read_bytes()==raw
    names={p.name for p in (root/RUN).iterdir()}
    if stage in ('unlink','dir_sync'):
        assert load(fd)==wire(records())[:3 if later else 1]
    else:
        assert '.pending.json' in names
        if stage=='write':assert (root/RUN/'.pending.json').stat().st_size==17
        with pytest.raises(PreparationStorageError):load(fd)
    # Never promote structurally readable files to this failed invocation's ack.
    assert result.status=='unknown'


@pytest.mark.parametrize('stage',['write','file_sync','readback'])
def test_stalled_real_storage_is_killed_by_delivered_supervisor(custody,monkeypatch,stage):
    root,fd=custody;fault_driver(monkeypatch,stage,action='stall')
    before=len(os.listdir('/proc/self/fd'));started=time.monotonic()
    result=capture(fd)
    assert time.monotonic()-started<5
    assert result.code=='fixture_deadline_exceeded' and result.termination=='forced_termination_reaped'
    assert result.reply is None and len(os.listdir('/proc/self/fd'))==before
    if stage=='readback':assert load(fd)==wire(records())
    else:assert (root/RUN/'.pending.json').exists()


@pytest.mark.parametrize('stage,action',[('readback','fail'),('readback','mismatch'),('close','fail'),('lost_reply','fail')])
def test_complete_looking_capture_without_ack_stays_unknown(custody,monkeypatch,stage,action):
    root,fd=custody;fault_driver(monkeypatch,stage,action=action)
    result=capture(fd)
    assert result.status=='unknown' and result.reply is None
    assert load(fd)==wire(records())


def test_capture_protocol_closed_and_bounded():
    m=module();raw=m._encode_capture(VALID,target(),wire(records()))
    body=json.loads(raw)
    assert body['schema_version']==2 and body['operation']=='fixture.capture'
    assert m._decode_capture(raw)[0]==VALID
    for changed in (body|dict(operation='other'),body|dict(schema_version=True),body|dict(extra=1)):
        reject(lambda:m._decode_capture(canonical(changed)))
    reject(lambda:m._decode_capture(raw+b' '*(65537-len(raw))))


def test_root_pin_survives_caller_close_and_fd_reuse(custody,monkeypatch):
    root,fd=custody;m=module();caller=os.dup(fd);spawn=m.subprocess.Popen;replacement=[]
    def close_caller(*args,**kwargs):
        os.close(caller)
        replacement.append(os.open(root/'other',os.O_CREAT|os.O_RDWR,0o600))
        assert replacement[0]==caller
        return spawn(*args,**kwargs)
    try:
        with monkeypatch.context() as patch:
            patch.setattr(m.subprocess,'Popen',close_caller)
            assert capture(caller).status=='fixture_records_acknowledged'
    finally:
        if replacement:os.close(replacement[0])
        else:os.close(caller)
    assert load(fd)==wire(records())
    assert (root/'other').read_bytes()==b''


def test_pin_and_spawn_failures_release_owned_descriptors(custody,monkeypatch):
    root,fd=custody;m=module();before=len(os.listdir('/proc/self/fd'))
    def fail(*args,**kwargs):raise OSError(errno.EIO,'private-marker')
    with monkeypatch.context() as patch:
        patch.setattr(m.fcntl,'fcntl',fail)
        reject(lambda:capture(fd))
    assert len(os.listdir('/proc/self/fd'))==before
    with monkeypatch.context() as patch:
        patch.setattr(m.subprocess,'Popen',fail)
        assert capture(fd).code=='fixture_spawn_failed'
    assert len(os.listdir('/proc/self/fd'))==before and list(root.iterdir())==[]


def test_root_duplication_time_uses_original_budget(custody,monkeypatch):
    root,fd=custody;m=module();clock=[0.0];original=m.fcntl.fcntl
    monkeypatch.setattr(m.time,'monotonic',lambda:clock[0])
    def late(*args):
        value=original(*args);clock[0]=58.0;return value
    monkeypatch.setattr(m.fcntl,'fcntl',late)
    monkeypatch.setattr(m.subprocess,'Popen',lambda *args,**kwargs:pytest.fail('fresh deadline started'))
    result=capture(fd)
    assert result.code=='fixture_deadline_exceeded' and result.termination=='not_started'
    assert list(root.iterdir())==[]


@pytest.mark.parametrize('failure',['late','error'])
def test_root_pin_close_is_charged_and_cannot_claim_ack(custody,monkeypatch,failure):
    root,fd=custody;m=module();clock=[0.0];dup=m.fcntl.fcntl;close=os.close;pins=[]
    monkeypatch.setattr(m.time,'monotonic',lambda:clock[0])
    def pin(*args):
        value=dup(*args);pins.append(value);return value
    def finish(descriptor):
        close(descriptor)
        if descriptor in pins:
            if failure=='late':clock[0]=61.0
            else:raise OSError('private-marker')
    with monkeypatch.context() as patch:
        patch.setattr(m.fcntl,'fcntl',pin);patch.setattr(os,'close',finish)
        result=capture(fd)
    assert result.status=='unknown' and result.reply is None and result.termination=='child_exited'
    assert result.code==('fixture_deadline_exceeded' if failure=='late' else 'fixture_cleanup_unverified')
    assert load(fd)==wire(records())


def test_capture_live_scope_restrictions_are_not_just_invalid_schema(custody):
    from test_caller_preparation_fixture import live_inputs
    _,fd=custody
    for admission in (True,False):
        _,descriptor,packed=live_inputs(admission)
        reject(lambda:module().capture_fixture(fd,request_raw=VALID,target=descriptor,records=packed))
    assert list(custody[0].iterdir())==[]


@pytest.mark.parametrize('stage',['write','file_sync','link','unlink','dir_sync'])
@pytest.mark.parametrize('later',[False,True])
def test_pre_effect_filesystem_errors_retain_original_records(custody,monkeypatch,stage,later):
    root,fd=custody;fault_driver(monkeypatch,stage,action='before',later=later)
    result=capture(fd)
    assert result.status=='unknown' and result.reply is None
    if later:
        for index,raw in enumerate(wire(records())[:2],1):
            assert (root/RUN/f'{index:06d}.json').read_bytes()==raw
    if stage=='dir_sync':assert load(fd)==wire(records())[:3 if later else 1]
    else:
        assert (root/RUN/'.pending.json').exists()
        with pytest.raises(PreparationStorageError):load(fd)
    if stage=='write':assert (root/RUN/'.pending.json').stat().st_size==0


@pytest.mark.parametrize('stage',['reserve_mkdir','reserve_open','reserve_lock','reserve_sync'])
@pytest.mark.parametrize('action',['before','exit'])
def test_reservation_error_and_interruption_preserve_without_replay(custody,monkeypatch,stage,action):
    root,fd=custody;fault_driver(monkeypatch,stage,action=action)
    result=capture(fd)
    assert result.status=='unknown' and result.reply is None
    if stage=='reserve_mkdir' and action=='before':assert list(root.iterdir())==[]
    else:
        assert (root/RUN).is_dir() and list((root/RUN).iterdir())==[]
        assert load(fd)==()
        # Existence, including an empty uncertain reservation, never authorizes replay.
        assert capture(fd).status=='unknown'


def test_capture_unverified_termination_releases_parent_pin_without_read_or_retry(custody,monkeypatch):
    import apps.scribeswell.backend.caller_preparation_storage as store
    root,fd=custody;(root/RUN).mkdir(mode=0o700)
    m=module();fake=FakeProcess(wait_error=True);original=m.fcntl.fcntl;pins=[];launches=[]
    def pin(*args):
        value=original(*args);pins.append(value);return value
    def spawn(*args,**kwargs):launches.append(True);return fake
    def fail(*args):raise OSError('private-marker')
    with monkeypatch.context() as patch:
        patch.setattr(m.time,'monotonic',lambda:0.0)
        patch.setattr(m.fcntl,'fcntl',pin);patch.setattr(m.subprocess,'Popen',spawn)
        patch.setattr(m,'_exchange',fail)
        patch.setattr(store,'read_fixture_prefix',lambda *a,**k:pytest.fail('read after unverified stop'))
        result=capture(fd)
    assert result.code=='fixture_cleanup_unverified' and result.termination=='termination_unverified'
    assert result.reply is None and len(launches)==1
    with pytest.raises(OSError):os.fstat(pins[0])
    assert os.fstat(fd).st_mode & 0o7777==0o700
    assert (root/RUN).is_dir() and list((root/RUN).iterdir())==[]


@pytest.mark.parametrize('mutation',['duplicate','bom','deep','base64','target_type','record_type','version1','missing','utf8'])
def test_real_capture_child_rejects_v2_before_reserving(custody,mutation):
    root,fd=custody;m=module();raw=m._encode_capture(VALID,target(),wire(records()));body=json.loads(raw)
    if mutation=='duplicate':raw=raw.replace(b'"schema_version":2',b'"schema_version":2,"schema_version":2')
    elif mutation=='bom':raw=b'\xef\xbb\xbf'+raw
    elif mutation=='deep':raw=b'['*1000+raw+b']'*1000
    elif mutation=='base64':body['records_b64'][0]+='=';raw=canonical(body)
    elif mutation=='target_type':body['target']=[];raw=canonical(body)
    elif mutation=='record_type':body['records_b64'][0]={};raw=canonical(body)
    elif mutation=='version1':raw=m._encode_envelope(VALID,target(),wire(records()))
    elif mutation=='missing':del body['request_b64'];raw=canonical(body)
    else:raw=b'\xff'+raw
    reject(lambda:m._decode_capture(raw))
    result=subprocess.run(m._capture_command(fd),input=raw,pass_fds=(fd,),env={},capture_output=True,timeout=10)
    assert result.returncode==2 and result.stdout==result.stderr==b''
    assert list(root.iterdir())==[]


def test_parent_never_opens_stats_or_reads_business_files(custody,monkeypatch):
    import builtins
    import stat
    root,fd=custody;m=module();original_open=os.open;original_read=os.read;original_stat=os.fstat
    def no_files(path,*args,**kwargs):
        if path=='/dev/null':return original_open(path,*args,**kwargs) # required child stderr sink
        pytest.fail('parent opened a filesystem resource')
    def no_metadata(*args,**kwargs):pytest.fail('parent inspected filesystem metadata')
    def pipe_read(descriptor,size):
        assert stat.S_ISFIFO(original_stat(descriptor).st_mode),'parent read a business file'
        return original_read(descriptor,size)
    def no_builtin(*args,**kwargs):pytest.fail('parent used path-based file I/O')
    with monkeypatch.context() as patch:
        patch.setattr(os,'open',no_files);patch.setattr(os,'stat',no_metadata);patch.setattr(os,'fstat',no_metadata)
        patch.setattr(os,'read',pipe_read);patch.setattr(builtins,'open',no_builtin)
        result=capture(fd)
    assert result.status=='fixture_records_acknowledged' and load(fd)==wire(records())
