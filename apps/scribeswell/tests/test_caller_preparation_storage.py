"""Local synthetic storage fixtures; no database or owner admission."""
from dataclasses import FrozenInstanceError
import errno
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from test_caller_preparation_evidence import TARGET, VALID, canonical, records, wire

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
RUN = json.loads(VALID)['run_id']


def storage():
    from apps.scribeswell.backend import caller_preparation_storage
    return caller_preparation_storage


def target():
    from apps.scribeswell.backend.caller_preparation_evidence import parse_target_descriptor
    return parse_target_descriptor(canonical(TARGET))


@pytest.fixture
def custody(tmp_path):
    root = tmp_path/'custody'
    root.mkdir(mode=0o700)
    fd = os.open(root, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        yield root, fd
    finally:
        os.close(fd)


def create(fd):
    return storage().create_fixture_attempt(fd, request_raw=VALID, target=target())


def load(fd):
    return storage().read_fixture_prefix(fd, request_raw=VALID, target=target())


def reject(call):
    with pytest.raises(storage().PreparationStorageError) as failure:
        call()
    error = failure.value
    assert str(error) == error.code == 'scribeswell_preparation_storage_invalid'
    assert error.__cause__ is None and error.__context__ is None


def test_create_append_reload_acceptance(custody):
    root, fd = custody
    raw = wire(records())
    writer = create(fd)
    for sequence, item in enumerate(raw, 1):
        ack = writer.append(item)
        assert ack.sequence == sequence
        import hashlib
        assert ack.record_sha256 == hashlib.sha256(item).hexdigest()
        with pytest.raises(FrozenInstanceError):
            ack.sequence = 5
    assert 'fixture' not in repr(writer) and not hasattr(writer, '__dict__')
    writer.close()
    assert load(fd) == raw
    assert os.fstat(fd).st_mode & 0o7777 == 0o700
    run = root/RUN
    assert run.stat().st_mode & 0o7777 == 0o700
    assert sorted(p.name for p in run.iterdir()) == [f'{i:06d}.json' for i in range(1,5)]
    for p, item in zip(sorted(run.iterdir()),raw):
        assert p.read_bytes() == item
        assert p.stat().st_mode & 0o7777 == 0o600 and p.stat().st_nlink == 1
    reject(lambda: create(fd))


@pytest.mark.parametrize('mode,count,outcome', [('create',1,None),('create',2,None),('create',3,None),
    ('reuse',4,None),('create',2,'rejected'),('create',3,'rolled_back'),('create',4,'unknown')])
def test_valid_partial_and_terminal_prefixes(custody,mode,count,outcome):
    _,fd=custody
    raw=wire(records(mode,outcome=outcome))[:count]
    with create(fd) as writer:
        for item in raw:
            writer.append(item)
    assert load(fd)==raw


def test_empty_reservation_and_closed_writer(custody):
    root,fd=custody
    writer=create(fd); writer.close(); writer.close()
    assert load(fd)==()
    reject(lambda: writer.append(wire(records())[0]))
    reject(lambda: create(fd))
    assert list((root/RUN).iterdir())==[]


def test_bad_input_poisoned_without_mutation(custody):
    root,fd=custody
    with create(fd) as writer:
        reject(lambda: writer.append(b'invalid private-marker'))
        reject(lambda: writer.append(wire(records())[0]))
    assert list((root/RUN).iterdir())==[]


def test_no_terminal_extension_or_rewrite(custody):
    root,fd=custody
    with create(fd) as writer:
        original=wire(records(count=2,outcome='unknown'))
        for raw in original:
            writer.append(raw)
        reject(lambda: writer.append(wire(records())[2]))
    assert load(fd)==original


@pytest.mark.parametrize('operation,after', [('open',False),('write',False),('write',True),('fsync',False),
    ('fsync',True),('link',False),('link',True),('unlink',False),('unlink',True)])
def test_append_failure_retains_residue_and_poison(custody,monkeypatch,operation,after):
    root,fd=custody; writer=create(fd)
    original=getattr(os,operation)
    called=[]
    def failure(*args,**kwargs):
        called.append(True)
        if after:
            original(*args,**kwargs)
        raise OSError(errno.ENOSPC,'private-marker')
    with monkeypatch.context() as patch:
        patch.setattr(os,operation,failure)
        reject(lambda: writer.append(wire(records())[0]))
    assert called
    reject(lambda: writer.append(wire(records())[0]))
    writer.close()
    names={p.name for p in (root/RUN).iterdir()}
    if operation=='open':
        assert names==set()
    else:
        assert names # preserve, never automatically clean uncertain writes
    if names=={'000001.json'}:
        # Valid retained bytes do not retrospectively acknowledge the failed call.
        assert load(fd)==wire(records())[:1]
    elif names:
        reject(lambda: load(fd))


def test_directory_sync_failure_after_publication_is_not_acknowledged(custody,monkeypatch):
    root,fd=custody; writer=create(fd); original=os.fsync; count=0
    def fail_directory(descriptor):
        nonlocal count
        count+=1
        original(descriptor)
        if count==2:
            raise OSError(errno.EIO,'private-marker')
    with monkeypatch.context() as patch:
        patch.setattr(os,'fsync',fail_directory)
        reject(lambda: writer.append(wire(records())[0]))
    assert count==2
    reject(lambda: writer.append(wire(records())[1]))
    writer.close()
    assert load(fd)==wire(records())[:1]
    assert (root/RUN/'000001.json').read_bytes()==wire(records())[0]


def test_positive_short_writes_and_zero_progress(custody,monkeypatch):
    root,fd=custody; writer=create(fd); original=os.write; calls=[]
    def short(descriptor,data):
        calls.append(len(data)); return original(descriptor,data[:17])
    with monkeypatch.context() as patch:
        patch.setattr(os,'write',short)
        writer.append(wire(records())[0])
    assert len(calls)>1
    with monkeypatch.context() as patch:
        patch.setattr(os,'write',lambda *args:0)
        reject(lambda: writer.append(wire(records())[1]))
    writer.close()
    assert (root/RUN/'000001.json').read_bytes()==wire(records())[0]
    assert (root/RUN/'.pending.json').read_bytes()==b''
    reject(lambda: load(fd))


@pytest.mark.parametrize('unsafe',['symlink','fifo','directory','hardlink','mode','oversize','corrupt','gap','unknown','pending'])
def test_reader_refuses_unsafe_entries_without_repair(custody,unsafe):
    root,fd=custody
    with create(fd) as writer:
        writer.append(wire(records())[0])
    run=root/RUN; file=run/'000001.json'
    if unsafe=='symlink':
        file.unlink(); file.symlink_to(root/'outside')
    elif unsafe=='fifo':
        file.unlink(); os.mkfifo(file,0o600)
    elif unsafe=='directory':
        file.unlink(); file.mkdir(mode=0o700)
    elif unsafe=='hardlink':
        os.link(file,root/'alias')
    elif unsafe=='mode':
        file.chmod(0o644)
    elif unsafe=='oversize':
        file.write_bytes(b'x'*32769)
    elif unsafe=='corrupt':
        file.write_bytes(b'private-marker')
    elif unsafe=='gap':
        file.rename(run/'000002.json')
    elif unsafe=='unknown':
        (run/'other').touch(mode=0o600)
    else:
        (run/'.pending.json').touch(mode=0o600)
    names=sorted(p.name for p in run.iterdir())
    reject(lambda: load(fd))
    assert sorted(p.name for p in run.iterdir())==names


@pytest.mark.parametrize('mode',[0o755,0o777,0o1700,0o750])
def test_root_and_run_exact_mode(custody,mode):
    root,fd=custody; root.chmod(mode)
    reject(lambda: create(fd)); assert not (root/RUN).exists()
    root.chmod(0o700)
    with create(fd):pass
    (root/RUN).chmod(mode)
    reject(lambda: load(fd))


def test_root_input_closed_and_never_environment_selected(custody):
    root,fd=custody
    for bad in (True,None,str(root),root,-1):
        reject(lambda: create(bad))
    file=root/'file'; file.touch(mode=0o600)
    other=os.open(file,os.O_RDONLY)
    try:
        reject(lambda: create(other))
    finally:
        os.close(other)
    from dataclasses import replace
    reject(lambda: storage().create_fixture_attempt(fd,request_raw=VALID,target=replace(target(),kind='supabase')))
    assert not (root/RUN).exists()


def test_live_admission_refused_before_file_mutation(custody):
    root,fd=custody; values=records(); values[0]['payload']['admission_class']='owner_verified'
    with create(fd) as writer:
        reject(lambda: writer.append(canonical(values[0])))
    assert list((root/RUN).iterdir())==[]


def test_writer_detects_changed_prefix_and_replaced_run(custody):
    root,fd=custody
    writer=create(fd); writer.append(wire(records())[0])
    (root/RUN/'000001.json').write_bytes(b'private-marker')
    reject(lambda: writer.append(wire(records())[1])); writer.close()
    # A separate request/run is not created to bypass the failed reservation.
    reject(lambda: create(fd))


def test_replaced_parent_entry_does_not_receive_writes(custody):
    root,fd=custody; writer=create(fd)
    (root/RUN).rename(root/'original')
    (root/RUN).mkdir(mode=0o700)
    reject(lambda: writer.append(wire(records())[0])); writer.close()
    assert list((root/'original').iterdir())==list((root/RUN).iterdir())==[]


def test_safe_error_during_active_caller_exception(custody):
    _,fd=custody
    try:
        raise RuntimeError('private-marker')
    except RuntimeError:
        reject(lambda: storage().read_fixture_prefix(fd,request_raw=b'bad private-marker',target=target()))


CHILD=r'''
import base64,json,os,sys,time
sys.path.insert(0,sys.argv[1])
from apps.scribeswell.backend import caller_preparation_storage as s
from apps.scribeswell.backend.caller_preparation_evidence import parse_target_descriptor
request,descriptor,raw=json.loads(sys.stdin.buffer.read())
request=base64.b64decode(request); raw=[base64.b64decode(item) for item in raw]
root=os.open(sys.argv[2],os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
mode=sys.argv[3]
try:
    if mode=='read':
        try:s.read_fixture_prefix(root,request_raw=request,target=parse_target_descriptor(json.dumps(descriptor).encode()))
        except s.PreparationStorageError:sys.exit(41)
        sys.exit(0)
    writer=s.create_fixture_attempt(root,request_raw=request,target=parse_target_descriptor(json.dumps(descriptor).encode()))
except s.PreparationStorageError:
    sys.exit(42)
if mode=='reserve':
    writer.close();sys.exit(0)
for earlier in raw[:-1]:
    writer.append(earlier)
    print('PRIOR_ACK',flush=True)
operation={'created':'open','written':'write','file_synced':'fsync','linked':'link','unlinked':'unlink','dir_synced':'fsync','stall':'fsync'}[mode]
original=getattr(os,operation); calls=0
def injected(*args,**kwargs):
    global calls
    result=original(*args,**kwargs)
    if mode=='created' and args[0]!='.pending.json':return result
    calls+=1
    if mode=='dir_synced' and calls==1:return result
    if mode=='stall':
        print('STALLED',flush=True)
        while True:time.sleep(1)
    os._exit(73)
setattr(os,operation,injected)
writer.append(raw[-1])
print('ACK',flush=True)
'''


def child_payload(count=1):
    import base64
    return canonical([base64.b64encode(VALID).decode(),TARGET,[base64.b64encode(raw).decode() for raw in wire(records())[:count]]])


def child_command(root,mode):
    return [sys.executable,'-I','-S','-c',CHILD,str(ROOT),str(root),mode]


def test_independent_process_lock_and_reservation(custody):
    root,fd=custody; writer=create(fd)
    for mode,code in [('read',41),('reserve',42)]:
        result=subprocess.run(child_command(root,mode),input=child_payload(),env={},capture_output=True,timeout=10)
        assert result.returncode==code,result.stderr.decode()
    writer.close()
    assert load(fd)==()


@pytest.mark.parametrize('stage',['created','written','file_synced','linked','unlinked','dir_synced'])
def test_process_death_retains_uncertain_records(custody,stage):
    root,fd=custody
    result=subprocess.run(child_command(root,stage),input=child_payload(),env={},capture_output=True,timeout=10)
    assert result.returncode==73,result.stderr.decode()
    assert b'ACK' not in result.stdout
    names={p.name for p in (root/RUN).iterdir()}
    if stage in ('unlinked','dir_synced'):
        assert names=={'000001.json'}
        assert load(fd)==wire(records())[:1] # structurally readable, not original acknowledgement
    else:
        assert '.pending.json' in names
        reject(lambda: load(fd))
    reject(lambda: create(fd))


def test_stalled_sync_killed_only_by_fixture_harness(custody):
    import select
    root,fd=custody
    with subprocess.Popen(child_command(root,'stall'),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={}) as process:
        try:
            process.stdin.write(child_payload())
            process.stdin.close()
            process.stdin=None
            ready,_,_=select.select([process.stdout],[],[],10)
            assert ready,'child failed to reach bounded readiness handshake'
            marker=os.read(process.stdout.fileno(),8)
            assert marker==b'STALLED\n'
            # Startup/imports are finished before this separate stall interval.
            with pytest.raises(subprocess.TimeoutExpired):
                process.communicate(timeout=0.2)
        finally:
            process.kill()
            stdout,stderr=process.communicate(timeout=5)
    assert process.returncode<0 and b'ACK' not in stdout,stderr.decode()
    reject(lambda: load(fd))
    assert (root/RUN/'.pending.json').is_file()


def test_reject_wrong_owner_and_symlink_run(custody,monkeypatch):
    root,fd=custody
    with monkeypatch.context() as patch:
        patch.setattr(os,'geteuid',lambda:root.stat().st_uid+1)
        reject(lambda:create(fd))
    outside=root/'outside'; outside.mkdir(mode=0o700)
    (root/RUN).symlink_to(outside,target_is_directory=True)
    reject(lambda:create(fd)); reject(lambda:load(fd))
    assert list(outside.iterdir())==[]


def test_reservation_sync_failure_retains_empty_run(custody,monkeypatch):
    root,fd=custody
    def fail(*args):raise OSError(errno.EIO,'private-marker')
    with monkeypatch.context() as patch:
        patch.setattr(os,'fsync',fail)
        reject(lambda:create(fd))
    assert (root/RUN).is_dir() and load(fd)==()
    reject(lambda:create(fd))


def test_acknowledgement_order_and_existing_record_immutability(custody,monkeypatch):
    root,fd=custody; writer=create(fd)
    events=[]
    originals={name:getattr(os,name) for name in ('write','fsync','link','unlink')}
    def wrapped(name):
        def call(*args,**kwargs):
            result=originals[name](*args,**kwargs)
            if name=='fsync':
                import stat
                events.append('directory_sync' if stat.S_ISDIR(os.fstat(args[0]).st_mode) else 'file_sync')
            else:events.append(name)
            return result
        return call
    with monkeypatch.context() as patch:
        for name in originals:patch.setattr(os,name,wrapped(name))
        writer.append(wire(records())[0]);events.append('ack')
    assert events==['write','file_sync','link','unlink','directory_sync','ack']
    first=(root/RUN/'000001.json').stat()
    writer.append(wire(records())[1]); writer.close()
    after=(root/RUN/'000001.json').stat()
    assert (first.st_ino,first.st_mtime_ns,first.st_ctime_ns)==(after.st_ino,after.st_mtime_ns,after.st_ctime_ns)


def test_link_collision_never_replaces_existing_final(custody,monkeypatch):
    root,fd=custody; writer=create(fd); original=os.link
    def collide(src,dst,*args,**kwargs):
        # Simulate another cooperative caller discovering a conflicting final at
        # publication, after initial scan. O_EXCL link must refuse replacement.
        (root/RUN/dst).write_bytes(b'original-conflict')
        return original(src,dst,*args,**kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(os,'link',collide)
        reject(lambda:writer.append(wire(records())[0]))
    writer.close()
    assert (root/RUN/'000001.json').read_bytes()==b'original-conflict'
    assert (root/RUN/'.pending.json').read_bytes()==wire(records())[0]
    reject(lambda:load(fd))


def test_restrictive_umask_does_not_modify_or_reuse_material(custody):
    root,fd=custody; previous=os.umask(0o777)
    try:reject(lambda:create(fd))
    finally:os.umask(previous)
    assert (root/RUN).stat().st_mode & 0o7777==0
    reject(lambda:create(fd))
    # Only test fixture teardown repairs access to its private failed directory.
    (root/RUN).chmod(0o700)


def test_reload_checks_independently_expected_request_and_target(custody):
    from dataclasses import replace
    root,fd=custody
    with create(fd) as writer:
        writer.append(wire(records())[0])
    original=(root/RUN/'000001.json').read_bytes()
    wrong=VALID.replace(b'fixture:target',b'fixture:other')
    for request in (wrong,VALID+b' '):
        reject(lambda:storage().read_fixture_prefix(fd,request_raw=request,target=target()))
    for descriptor in (replace(target(),port=5433),replace(target(),binding='other_db',database='other_db')):
        reject(lambda:storage().read_fixture_prefix(fd,request_raw=VALID,target=descriptor))
    assert (root/RUN/'000001.json').read_bytes()==original
    assert load(fd)==(original,)


def test_positive_short_reads_preserve_whole_prefix(custody,monkeypatch):
    root,fd=custody
    with create(fd) as writer:
        writer.append(wire(records())[0])
    original=os.read; calls=[]
    def short(descriptor,size):
        calls.append(size)
        return original(descriptor,min(size,11))
    with monkeypatch.context() as patch:
        patch.setattr(os,'read',short)
        assert load(fd)==wire(records())[:1]
    assert len(calls)>2


@pytest.mark.parametrize('during_append',[False,True])
@pytest.mark.parametrize('after_read',[False,True])
def test_read_failure_preserves_records_and_releases_descriptors(custody,monkeypatch,during_append,after_read):
    root,fd=custody; writer=create(fd); writer.append(wire(records())[0])
    if not during_append:writer.close()
    original=os.read
    def fail(descriptor,size):
        if after_read:original(descriptor,min(size,13))
        raise OSError(errno.EIO,'private-marker')
    count=len(os.listdir('/proc/self/fd'))
    with monkeypatch.context() as patch:
        patch.setattr(os,'read',fail)
        reject(lambda:writer.append(wire(records())[1]) if during_append else load(fd))
    assert len(os.listdir('/proc/self/fd'))==count
    if during_append:
        reject(lambda:writer.append(wire(records())[1]))
        writer.close()
    assert load(fd)==wire(records())[:1]
    assert (root/RUN/'000001.json').read_bytes()==wire(records())[0]
    assert not (root/RUN/'.pending.json').exists()


@pytest.mark.parametrize('stage',['created','written','file_synced','linked','unlinked','dir_synced'])
def test_later_append_process_death_preserves_acknowledged_prefix(custody,stage):
    root,fd=custody
    result=subprocess.run(child_command(root,stage),input=child_payload(count=3),env={},capture_output=True,timeout=10)
    assert result.returncode==73,result.stderr.decode()
    assert result.stdout==b'PRIOR_ACK\nPRIOR_ACK\n'
    for index,raw in enumerate(wire(records())[:2],1):
        assert (root/RUN/f'{index:06d}.json').read_bytes()==raw
    if stage in ('unlinked','dir_synced'):
        assert load(fd)==wire(records())[:3]
    else:
        reject(lambda:load(fd))
    reject(lambda:create(fd))


def test_same_process_reader_cannot_unlock_writer(custody):
    root,fd=custody; writer=create(fd)
    reject(lambda:load(fd))
    other=subprocess.run(child_command(root,'read'),input=child_payload(),env={},capture_output=True,timeout=10)
    assert other.returncode==41,other.stderr.decode()
    writer.append(wire(records())[0])
    writer.close()
    other=subprocess.run(child_command(root,'read'),input=child_payload(),env={},capture_output=True,timeout=10)
    assert other.returncode==0,other.stderr.decode()


def test_writer_pins_root_independently_of_caller_descriptor(custody):
    root,fd=custody
    caller=os.dup(fd)
    writer=create(caller)
    os.close(caller)
    writer.append(wire(records())[0]); writer.close()
    assert load(fd)==wire(records())[:1]


def test_failed_reads_and_duplicate_reservations_do_not_leak_descriptors(custody):
    root,fd=custody
    before=len(os.listdir('/proc/self/fd'))
    for _ in range(12):reject(lambda:load(fd))
    assert len(os.listdir('/proc/self/fd'))==before
    with create(fd):pass
    for _ in range(12):reject(lambda:create(fd))
    assert len(os.listdir('/proc/self/fd'))==before
    assert load(fd)==()


@pytest.mark.parametrize('changed',['root_mode','run_mode','owner'])
def test_custody_changes_before_append_preserve_ack_and_poison(custody,monkeypatch,changed):
    root,fd=custody; writer=create(fd); writer.append(wire(records())[0])
    if changed=='root_mode':root.chmod(0o750)
    elif changed=='run_mode':(root/RUN).chmod(0o750)
    with monkeypatch.context() as patch:
        if changed=='owner':patch.setattr(os,'geteuid',lambda:root.stat().st_uid+1)
        reject(lambda:writer.append(wire(records())[1]))
    root.chmod(0o700);(root/RUN).chmod(0o700)
    reject(lambda:writer.append(wire(records())[1]));writer.close()
    assert load(fd)==wire(records())[:1]
    assert not (root/RUN/'.pending.json').exists()
