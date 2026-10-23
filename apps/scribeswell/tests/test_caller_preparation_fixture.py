"""Communication declarations only: no database, storage or live admission."""
from dataclasses import FrozenInstanceError, replace
import base64
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from test_caller_preparation_evidence import TARGET, VALID, canonical, records, relink, wire

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))


def module():
    from apps.scribeswell.backend import caller_preparation_fixture
    return caller_preparation_fixture


def target():
    from apps.scribeswell.backend.caller_preparation_evidence import parse_target_descriptor
    return parse_target_descriptor(canonical(TARGET))


def run(rows=None):
    return module().supervise_fixture(request_raw=VALID,target=target(),records=wire(rows or records()))


def reject(call):
    m=module()
    with pytest.raises(m.PreparationFixtureError) as failure:call()
    error=failure.value
    assert str(error)==error.code=='scribeswell_preparation_fixture_invalid'
    assert error.__context__ is None and error.__cause__ is None


def test_isolated_worker_acceptance():
    result=run()
    assert result.status==result.code=='fixture_reply_validated'
    assert result.termination=='child_exited'
    assert result.reply.outcome=='committed' # synthetic declaration, no DB outcome
    with pytest.raises(FrozenInstanceError):result.status='unknown'
    assert 'fixture:' not in repr(result) and not hasattr(result,'__dict__')


def envelope(rows=None):
    return dict(schema_version=1,request_b64=base64.b64encode(VALID).decode(),target=dict(TARGET),
                records_b64=[base64.b64encode(raw).decode() for raw in wire(rows or records())])


def test_fixed_launch_has_no_private_arguments_or_ambient_environment(monkeypatch):
    m=module(); original=m.subprocess.Popen; observed=[]
    def capture(*args,**kwargs):
        observed.append((args,kwargs))
        return original(*args,**kwargs)
    monkeypatch.setattr(m.subprocess,'Popen',capture)
    monkeypatch.setenv('PGPASSWORD','private-marker')
    assert run().status=='fixture_reply_validated'
    args,kwargs=observed[0]
    assert '-I' in args[0] and '-S' in args[0]
    assert all('fixture:' not in part and 'private-marker' not in part for part in args[0])
    assert kwargs['env']=={} and kwargs['stderr']==subprocess.DEVNULL and kwargs['close_fds']
    assert kwargs['bufsize']==0 and kwargs['cwd']==str(ROOT)


@pytest.mark.parametrize('mode,outcome,count',[('reuse','reused',4),('create','unknown',2),('create','rejected',2),
    ('create','rolled_back',3),('create','unknown',4)])
def test_other_terminal_fixture_replies(mode,outcome,count):
    result=run(records(mode,outcome=outcome,count=count))
    assert result.status=='fixture_reply_validated' and result.reply.outcome==outcome


@pytest.mark.parametrize('invalid',['request','target','admission','nonterminal','list','bytes','binding'])
def test_invalid_or_live_inputs_never_spawn(monkeypatch,invalid):
    m=module(); rows=records(); raw=VALID; descriptor=target(); packed=wire(rows)
    if invalid=='request':raw=b'bad private-marker'
    elif invalid=='target':descriptor=replace(descriptor,kind='supabase')
    elif invalid=='admission':rows[0]['payload']['admission_class']='owner_verified';packed=wire(relink(rows))
    elif invalid=='nonterminal':packed=packed[:3]
    elif invalid=='list':packed=list(packed)
    elif invalid=='bytes':packed=(bytearray(packed[0]),)+packed[1:]
    else:descriptor=replace(descriptor,port=5433)
    def forbidden(*args,**kwargs):pytest.fail('invalid input launched worker')
    monkeypatch.setattr(m.subprocess,'Popen',forbidden)
    reject(lambda:m.supervise_fixture(request_raw=raw,target=descriptor,records=packed))


@pytest.mark.parametrize('mutation',['bom','utf8','duplicate','extra','missing','float','trailing','b64','count','live','deep'])
def test_child_protocol_closed_and_safe(mutation):
    m=module(); body=envelope(); raw=canonical(body)
    if mutation=='bom':raw=b'\xef\xbb\xbf'+raw
    elif mutation=='utf8':raw=b'\xff'+raw
    elif mutation=='duplicate':raw=raw.replace(b'"schema_version":1',b'"schema_version":1,"schema_version":1')
    elif mutation=='extra':body['extra']=1;raw=canonical(body)
    elif mutation=='missing':del body['target'];raw=canonical(body)
    elif mutation=='float':raw=raw.replace(b'"schema_version":1',b'"schema_version":1.0')
    elif mutation=='trailing':raw+=b'{}'
    elif mutation=='b64':body['request_b64']+='=';raw=canonical(body)
    elif mutation=='count':body['records_b64']*=2;raw=canonical(body)
    elif mutation=='live':body['target']['kind']='supabase';raw=canonical(body)
    else:raw=b'['*1000+raw+b']'*1000
    reject(lambda:m._decode_envelope(raw))


def test_child_protocol_transport_boundary_and_stream_cap():
    m=module(); raw=canonical(envelope())
    padded=raw+b' '*(65536-len(raw))
    assert m._decode_envelope(padded)[0]==VALID
    reject(lambda:m._decode_envelope(padded+b' '))
    class Limited(io.BytesIO):
        def read(self,size=-1):
            assert 0<size<=65537
            return super().read(min(size,113))
    assert m._read_request(Limited(padded))==padded
    reject(lambda:m._read_request(Limited(padded+b' ')))


def test_parent_transport_limit_before_launch(monkeypatch):
    m=module(); payload=m._encode_envelope(VALID,target(),wire(records()))
    monkeypatch.setattr(m,'_MAX_REQUEST',len(payload)-1)
    monkeypatch.setattr(m.subprocess,'Popen',lambda *args,**kwargs:pytest.fail('oversize launched'))
    reject(lambda:run())


def driver(monkeypatch,body):
    m=module()
    script='import os,sys,time\n'+body
    monkeypatch.setattr(m,'_worker_command',lambda:[sys.executable,'-I','-S','-c',script])
    monkeypatch.setattr(m,'_WORK_SECONDS',0.5)
    monkeypatch.setattr(m,'_TOTAL_SECONDS',2.0)
    monkeypatch.setattr(m,'_CLEANUP_SECONDS',0.5)


@pytest.mark.parametrize('body,code',[
    ("sys.stdin.buffer.read();sys.stdout.buffer.write(b'x'*4097);sys.stdout.flush()",'fixture_transport_invalid'),
    ("sys.stdin.buffer.read();sys.stdout.buffer.write(b'invalid private-marker')",'fixture_reply_invalid'),
    ("sys.stdin.buffer.read();sys.exit(7)",'fixture_child_failed'),
    ("time.sleep(10)",'fixture_deadline_exceeded'),
    ("sys.stdin.buffer.read();sys.stdout.close();time.sleep(10)",'fixture_deadline_exceeded'),
    ("sys.stdin.buffer.read();os.write(2,b'private-marker'*1000000);time.sleep(10)",'fixture_deadline_exceeded'),
])
def test_real_worker_failures_are_safe_and_bounded(monkeypatch,body,code):
    driver(monkeypatch,body)
    started=time.monotonic()
    result=run()
    assert time.monotonic()-started<5.0 # distinguish bounded cleanup from ten-second child sleep
    assert result.status=='unknown' and result.code==code and result.reply is None
    assert result.termination in ('child_exited','forced_termination_reaped')
    assert 'private-marker' not in repr(result)


def test_valid_reply_with_nonzero_exit_is_not_accepted(monkeypatch):
    from test_caller_preparation_evidence import reply
    raw=canonical(reply(records()))
    driver(monkeypatch,'sys.stdin.buffer.read();os.write(1,'+repr(raw)+');sys.exit(9)')
    result=run()
    assert result.status=='unknown' and result.code=='fixture_child_failed'


def test_valid_reply_without_eof_stays_unknown(monkeypatch):
    from test_caller_preparation_evidence import reply
    raw=canonical(reply(records()))
    driver(monkeypatch,'sys.stdin.buffer.read();os.write(1,'+repr(raw)+');time.sleep(10)')
    assert run().code=='fixture_deadline_exceeded'


def test_safe_error_has_no_active_caller_context(monkeypatch):
    try:raise RuntimeError('private-marker')
    except RuntimeError:
        reject(lambda:module().supervise_fixture(request_raw=b'bad',target=target(),records=wire(records())))


@pytest.mark.parametrize('elapsed',[58.0,59.5,61.0])
def test_validation_time_is_charged_before_spawn(monkeypatch,elapsed):
    m=module(); clock=[0.0]; original=m._encode_envelope
    monkeypatch.setattr(m.time,'monotonic',lambda:clock[0])
    def slow(*args):
        payload=original(*args);clock[0]=elapsed;return payload
    monkeypatch.setattr(m,'_encode_envelope',slow)
    monkeypatch.setattr(m.subprocess,'Popen',lambda *args,**kwargs:pytest.fail('expired work spawned'))
    result=run()
    assert result.status=='unknown' and result.code=='fixture_deadline_exceeded'
    assert result.termination=='not_started'


class FakeProcess:
    def __init__(self,wait_error=False,kill_error=False,close_error=False):
        self.stdin,self.stdout=io.BytesIO(),io.BytesIO()
        self.returncode=None
        self.killed=False
        self.waits=[]
        self.wait_error,self.kill_error=wait_error,kill_error
        if close_error:
            class BadClose(io.BytesIO):
                def close(self):
                    super().close();raise OSError('private-marker')
            self.stdin=BadClose()
    def poll(self):return self.returncode
    def kill(self):
        if self.kill_error:raise PermissionError('private-marker')
        self.killed=True
    def wait(self,timeout):
        self.waits.append(timeout)
        if self.wait_error:raise subprocess.TimeoutExpired('private-marker',timeout)
        self.returncode=-9 if self.killed else 0
        return self.returncode


@pytest.mark.parametrize('elapsed,expected_wait,termination',[(58.0,2.0,'forced_termination_reaped'),
    (59.5,0.5,'forced_termination_reaped'),(60.0,None,'termination_unverified'),(61.0,None,'termination_unverified')])
def test_spawn_overrun_uses_only_remaining_cleanup_budget(monkeypatch,elapsed,expected_wait,termination):
    m=module(); clock=[0.0]; fake=FakeProcess()
    monkeypatch.setattr(m.time,'monotonic',lambda:clock[0])
    def spawn(*args,**kwargs):clock[0]=elapsed;return fake
    monkeypatch.setattr(m.subprocess,'Popen',spawn)
    result=run()
    assert result.status=='unknown' and result.termination==termination and fake.killed
    assert fake.waits==([] if expected_wait is None else [expected_wait])
    assert fake.stdin.closed and fake.stdout.closed


def test_cleanup_never_takes_fresh_two_seconds_after_spent_total(monkeypatch):
    m=module(); clock=[0.0]; fake=FakeProcess()
    monkeypatch.setattr(m.time,'monotonic',lambda:clock[0])
    monkeypatch.setattr(m.subprocess,'Popen',lambda *args,**kwargs:fake)
    def fail(*args):clock[0]=59.9999;raise OSError('private-marker')
    monkeypatch.setattr(m,'_exchange',fail)
    result=run()
    assert result.termination=='forced_termination_reaped'
    assert len(fake.waits)==1 and 0<fake.waits[0]<0.001


@pytest.mark.parametrize('wait_error,kill_error,close_error',[(True,False,False),(True,True,False),(False,True,False),(False,False,True)])
def test_cleanup_failures_retain_truthful_termination(monkeypatch,wait_error,kill_error,close_error):
    m=module(); fake=FakeProcess(wait_error,kill_error,close_error)
    monkeypatch.setattr(m.time,'monotonic',lambda:0.0)
    monkeypatch.setattr(m.subprocess,'Popen',lambda *args,**kwargs:fake)
    def fail(*args):raise OSError('private-marker')
    monkeypatch.setattr(m,'_exchange',fail)
    result=run()
    assert result.status=='unknown' and result.reply is None
    if wait_error:assert result.termination=='termination_unverified'
    elif kill_error:assert result.termination=='child_exited'
    else:assert result.termination=='forced_termination_reaped'
    assert result.code==('fixture_cleanup_unverified' if wait_error or close_error else 'fixture_transport_invalid')
    assert fake.stdin.closed and fake.stdout.closed


def test_spawn_failure_safe_no_process(monkeypatch):
    m=module()
    def fail(*args,**kwargs):raise OSError('private-marker')
    monkeypatch.setattr(m.subprocess,'Popen',fail)
    result=run()
    assert result.code=='fixture_spawn_failed' and result.termination=='not_started' and result.reply is None


def test_parent_validation_is_charged_to_original_work_deadline(monkeypatch):
    m=module(); clock=[0.0]; original=m.parse_worker_result
    monkeypatch.setattr(m.time,'monotonic',lambda:clock[0])
    def slow(*args,**kwargs):
        result=original(*args,**kwargs);clock[0]=58.0;return result
    monkeypatch.setattr(m,'parse_worker_result',slow)
    result=run()
    assert result.code=='fixture_deadline_exceeded' and result.reply is None
    assert result.termination=='child_exited'


@pytest.mark.parametrize('field', ['run_id','request_sha256','target_sha256','record_sequence','record_sha256','outcome','code','schema_version'])
def test_parent_refuses_each_forged_reply_field(monkeypatch,field):
    from test_caller_preparation_evidence import reply
    body=reply(records())
    body[field]=3 if field in ('record_sequence','schema_version') else 'invalid'
    driver(monkeypatch,'sys.stdin.buffer.read();os.write(1,'+repr(canonical(body))+')')
    result=run()
    assert result.status=='unknown' and result.code=='fixture_reply_invalid'


def test_response_at_limit_and_one_byte_over(monkeypatch):
    from test_caller_preparation_evidence import reply
    raw=canonical(reply(records())); at_limit=raw+b' '*(4096-len(raw))
    driver(monkeypatch,'sys.stdin.buffer.read();os.write(1,'+repr(at_limit)+')')
    assert run().status=='fixture_reply_validated'
    driver(monkeypatch,'sys.stdin.buffer.read();os.write(1,'+repr(at_limit+b' ')+')')
    assert run().code=='fixture_transport_invalid'


@pytest.mark.parametrize('operation', ['read','write'])
def test_transient_pipe_backpressure_and_short_operations(monkeypatch,operation):
    m=module(); original=getattr(os,operation); calls=[]; selected=[]
    spawn=m.subprocess.Popen
    def capture(*args,**kwargs):
        process=spawn(*args,**kwargs)
        selected.append((process.stdout if operation=='read' else process.stdin).fileno())
        return process
    def limited(fd,value):
        if fd not in selected:return original(fd,value)
        calls.append(True)
        if len(calls)==1:raise BlockingIOError()
        if operation=='read':return original(fd,min(value,19))
        return original(fd,value[:23])
    with monkeypatch.context() as patch:
        patch.setattr(m.subprocess,'Popen',capture)
        patch.setattr(os,operation,limited)
        assert run().status=='fixture_reply_validated'
    assert len(calls)>2


def test_zero_progress_write_is_refused_and_child_reaped(monkeypatch):
    m=module(); original=os.write
    with monkeypatch.context() as patch:
        patch.setattr(os,'write',lambda *args:0)
        result=run()
    assert result.code=='fixture_transport_invalid' and result.termination=='forced_termination_reaped'


def test_no_descriptor_growth_across_repeated_runtime_failures(monkeypatch):
    driver(monkeypatch,"sys.stdin.buffer.read();os.write(1,b'invalid private-marker')")
    before=len(os.listdir('/proc/self/fd'))
    for _ in range(5):assert run().status=='unknown'
    assert len(os.listdir('/proc/self/fd'))==before


def test_total_deadline_overrun_during_cleanup_never_reports_validated(monkeypatch):
    m=module(); clock=[0.0]; original=m._finish
    monkeypatch.setattr(m.time,'monotonic',lambda:clock[0])
    def late(*args):
        result=original(*args);clock[0]=61.0;return result
    monkeypatch.setattr(m,'_finish',late)
    result=run()
    assert result.status=='unknown' and result.code=='fixture_deadline_exceeded'
    assert result.reply is None and result.termination=='child_exited'


def test_natural_exit_during_kill_race_is_not_forced_termination(monkeypatch):
    m=module(); fake=FakeProcess()
    def exited(timeout):
        fake.waits.append(timeout)
        fake.returncode=0
        return 0
    fake.wait=exited
    monkeypatch.setattr(m.time,'monotonic',lambda:0.0)
    monkeypatch.setattr(m.subprocess,'Popen',lambda *args,**kwargs:fake)
    def fail(*args):raise OSError('private-marker')
    monkeypatch.setattr(m,'_exchange',fail)
    result=run()
    assert result.termination=='child_exited' and result.status=='unknown'


@pytest.mark.parametrize('field,value',[('run_id','44444444-4444-4444-8444-444444444444'),
    ('request_sha256','a'*64),('target_sha256','b'*64),('record_sequence',3),('record_sha256','c'*64),('outcome','reused')])
def test_parent_rejects_well_formed_alternate_bindings(monkeypatch,field,value):
    from test_caller_preparation_evidence import reply
    from apps.scribeswell.backend.caller_preparation_evidence import WorkerResult, encode_worker_result
    body=reply(records());body[field]=value
    if field=='outcome':body['code']='preparation_reused'
    raw=encode_worker_result(WorkerResult(**body)) # shape valid; only parent binding can reject
    driver(monkeypatch,'sys.stdin.buffer.read();os.write(1,'+repr(raw)+')')
    result=run()
    assert result.code=='fixture_reply_invalid' and result.reply is None


def live_inputs(admission=False):
    from test_caller_preparation_evidence import digest
    from apps.scribeswell.backend.caller_preparation_evidence import parse_target_descriptor, parse_attempt
    rows=records()
    descriptor=TARGET.copy()
    if admission:
        rows[0]['payload']['admission_class']='owner_verified'
    else:
        descriptor=dict(kind='supabase',binding='https://a.supabase.co',host='db.a.supabase.co',
                        port=5432,database='postgres',login='scribeswell_migrator')
        rows[0]['payload']['target']=descriptor
        rows[1]['payload']['session']['database']='postgres'
        for row in rows:row['target_sha256']=digest(descriptor)
    packed=wire(relink(rows)); typed=parse_target_descriptor(canonical(descriptor))
    assert len(parse_attempt(packed,request_raw=VALID,target=typed))==4 # valid declarations, fixture-forbidden
    body=dict(schema_version=1,request_b64=base64.b64encode(VALID).decode(),target=descriptor,
              records_b64=[base64.b64encode(raw).decode() for raw in packed])
    return body,typed,packed


@pytest.mark.parametrize('admission',[False,True])
def test_parent_refuses_schema_valid_live_scope_before_spawn(monkeypatch,admission):
    body,descriptor,packed=live_inputs(admission)
    m=module()
    monkeypatch.setattr(m.subprocess,'Popen',lambda *args,**kwargs:pytest.fail('live scope launched'))
    reject(lambda:m.supervise_fixture(request_raw=VALID,target=descriptor,records=packed))


@pytest.mark.parametrize('case',['invalid','bom','duplicate','oversize','float','extra','live_target','live_admission'])
def test_real_isolated_child_refuses_bad_transport_without_diagnostics(case,tmp_path):
    body=envelope();raw=canonical(body)
    if case=='invalid':raw=b'private-marker'
    elif case=='bom':raw=b'\xef\xbb\xbf'+raw
    elif case=='duplicate':raw=raw.replace(b'"schema_version":1',b'"schema_version":1,"schema_version":1')
    elif case=='oversize':raw+=b' '*(65537-len(raw))
    elif case=='float':raw=raw.replace(b'"schema_version":1',b'"schema_version":1.0')
    elif case=='extra':body['private-marker']=True;raw=canonical(body)
    else:body,_,_=live_inputs(admission=case=='live_admission');raw=canonical(body)
    result=subprocess.run(module()._worker_command(),input=raw,cwd=tmp_path,env={},capture_output=True,timeout=10)
    assert result.returncode==2
    assert result.stdout==result.stderr==b''


def test_repeated_forced_cleanup_reaps_children_without_descriptor_growth(monkeypatch):
    driver(monkeypatch,'sys.stdin.buffer.read();time.sleep(10)')
    m=module(); original=m.subprocess.Popen; children=[]
    def capture(*args,**kwargs):
        child=original(*args,**kwargs);children.append(child);return child
    monkeypatch.setattr(m.subprocess,'Popen',capture)
    count=len(os.listdir('/proc/self/fd')); started=time.monotonic()
    for _ in range(3):
        result=run()
        assert result.code=='fixture_deadline_exceeded' and result.termination=='forced_termination_reaped'
    assert time.monotonic()-started<5.0
    assert len(os.listdir('/proc/self/fd'))==count
    for child in children:
        assert child.returncode==-9
        with pytest.raises(ChildProcessError):os.waitpid(child.pid,os.WNOHANG)


def test_zero_exit_empty_reply_is_invalid_not_child_failure(monkeypatch):
    driver(monkeypatch,'sys.stdin.buffer.read()')
    result=run()
    assert result.code=='fixture_reply_invalid' and result.termination=='child_exited'
    assert result.status=='unknown' and result.reply is None
