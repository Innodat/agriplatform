"""CLI strict input and untrusted response boundaries."""
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))


def test_invalid_arguments_safe(capsys):
    import operator_cli
    assert operator_cli.main(['execute','--owner','password-value'])==2
    assert capsys.readouterr().out=='{"code":"command_invalid"}\n'


@pytest.mark.parametrize('argv',[[],['outcome','--owner','access'],['execute','--actor','PRIVATE'],['outcome','--owner','identity','--target','PRIVATE','--command','actor.register_system','--operation-id','bad']])
def test_malformed_no_dispatch(argv,monkeypatch,capsys):
    import operator_cli as c
    monkeypatch.setattr(c,'dispatch',lambda _:pytest.fail('dispatched invalid input'))
    assert c.main(argv)==2
    output=capsys.readouterr()
    assert 'PRIVATE' not in output.out+output.err
    assert not output.err


def test_response_closed_and_receipt_versions():
    import operator_cli as c
    import json
    op='a1234567-1234-1234-1234-123456789abc'
    good=dict(operation_id=op,status='committed',command_version=1,result_version=1,
        committed_at='2026-10-20T00:00:00+00:00',result=dict(command='actor.register_system',
        target={'actor_id':op},disposition='unchanged',revision=None,event_id=None))
    assert c.validate_response(json.dumps(good).encode(),op)==good
    for bad in [{**good,'extra':'PRIVATE'},{**good,'command_version':True},{**good,'committed_at':'PRIVATE'},
                {'operation_id':op,'code':'PRIVATE'},{'operation_id':op,'status':'unresolved','extra':1}]:
        with pytest.raises(Exception):c.validate_response(json.dumps(bad).encode(),op)


@pytest.mark.parametrize('script,timeout,limit',[('import time;time.sleep(10)',0.12,8192),('print("x"*9000)',2,8192)])
def test_real_process_bounds(script,timeout,limit):
    import operator_cli as c
    import time
    started=time.monotonic()
    with pytest.raises(c.dev.Refusal):
        c.images.bounded_command([sys.executable,'-I','-B','-c',script],c.ROOT,{},timeout,limit)
    assert time.monotonic()-started<3


def test_fixed_worker_minimal_environment(monkeypatch):
    import operator_cli as c
    monkeypatch.setenv('PGPASSWORD','PRIVATE')
    def bounded(command,cwd,env,timeout,limit,**kwargs):
        assert command==[sys.executable,'-I','-B',str(Path(c.__file__).resolve()),'_worker']
        assert env=={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'}
        assert timeout==12 and limit==8192
        assert b'PRIVATE' not in kwargs['input_data']
        return b'{}'
    monkeypatch.setattr(c.images,'bounded_command',bounded)
    assert c.dispatch(['outcome','/some/descriptor',None,'a1234567-1234-1234-1234-123456789abc'])==b'{}'


@pytest.mark.parametrize('index',range(11))
def test_session_identity_and_restricted_flags(index):
    import operator_cli as c
    from types import SimpleNamespace
    expected=['identity_operator','identity_operator','idop_test',True,False,False,False,False,False,False,False]
    class Connection:
        rolled=False
        def execute(self,*args):return self
        def one(self):return expected
        def rollback(self):self.rolled=True
    connection=Connection();target=SimpleNamespace(database='idop_test')
    c.verify_session(connection,target)
    assert connection.rolled
    connection.rolled=False
    expected[index]=not expected[index] if type(expected[index]) is bool else 'wrong'
    with pytest.raises(c.adapter.OperatorError) as failure:c.verify_session(connection,target)
    assert failure.value.code=='access_denied' and not connection.rolled


@pytest.mark.parametrize('raw',[b'PRIVATE',b'{}',b'{"status":"committed"}',b'{"code":"PRIVATE"}'])
def test_corrupt_worker_output_keeps_id(tmp_path,monkeypatch,capsys,raw):
    import operator_cli as c
    import json
    from types import SimpleNamespace
    from test_identity_operator import document
    value=document();path=tmp_path/'command.json';path.write_text(json.dumps(value))
    monkeypatch.setattr(c,'load_target',lambda _:SimpleNamespace(path=tmp_path/'identity-operator.json'))
    monkeypatch.setattr(c,'dispatch',lambda _:raw)
    assert c.main(['execute','--owner','identity','--target','unused','--command-file',str(path)])==2
    assert json.loads(capsys.readouterr().out)==dict(code='operation_unavailable',operation_id=value['operation_id'].lower())


@pytest.mark.parametrize('signum',['SIGINT','SIGTERM'])
def test_real_dispatch_interrupt_cleanup(tmp_path,signum):
    import operator_cli as c
    import subprocess,time,signal,json,os
    # Replace only the worker command in a separate parent; exercise dispatch's
    # installed signal handlers and the existing real process-group cleanup.
    pidfile=tmp_path/'worker.pid';ready=tmp_path/'ready'
    script='''import sys,signal,os,json
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import operator_cli as c
original=c.images.bounded_command
def child(command,cwd,env,timeout,limit,**kwargs):
    source="import os,time;from pathlib import Path;Path("+repr(sys.argv[2])+").write_text(str(os.getpid()));time.sleep(30)"
    Path(sys.argv[3]).write_text('ready')
    return original([sys.executable,'-I','-B','-c',source],cwd,env,timeout,limit)
c.images.bounded_command=child
try:c.dispatch(['outcome','unused',None,'a1234567-1234-1234-1234-123456789abc'])
except c.WorkerInterrupted:print('cleaned')
'''
    parent=subprocess.Popen([sys.executable,'-I','-B','-c',script,str(Path(c.__file__).parent),str(pidfile),str(ready)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    started=time.monotonic()
    try:
        while not pidfile.exists() and time.monotonic()-started<4:time.sleep(.01)
        assert pidfile.exists()
        parent.send_signal(getattr(signal,signum))
        stdout,stderr=parent.communicate(timeout=3)
        assert parent.returncode==0 and stdout.strip()==b'cleaned' and not stderr
        with pytest.raises(ProcessLookupError):os.kill(int(pidfile.read_text()),0)
    finally:
        if parent.poll() is None:parent.kill();parent.wait()


def test_connection_arguments_disable_discovery_without_empty_service(monkeypatch):
    import operator_cli as c
    import sqlalchemy
    from sqlalchemy.pool import NullPool
    from types import SimpleNamespace
    captured={}
    def create_engine(url,**kwargs):
        captured.update(url=url,**kwargs)
        return 'engine'
    monkeypatch.setattr(sqlalchemy,'create_engine',create_engine)
    target=SimpleNamespace(password='private-value',port=55482,database='idop_test')
    assert c._connection(target)=='engine'
    url=captured['url']
    assert (url.drivername,url.host,url.port,url.database,url.username,url.password)==('postgresql+psycopg','127.0.0.1',55482,'idop_test','identity_operator','private-value')
    assert captured['poolclass'] is NullPool
    assert captured['isolation_level']=='READ COMMITTED' and captured['hide_parameters'] is True
    assert captured['connect_args']==dict(connect_timeout=3,sslmode='disable',gssencmode='disable',passfile='/dev/null',application_name='identity_operator',options='-c statement_timeout=5000 -c lock_timeout=2000')


@pytest.mark.parametrize('action',['execute','outcome'])
def test_worker_unsafe_session_denies_before_adapter(action,monkeypatch):
    import operator_cli as c
    from types import SimpleNamespace
    from test_identity_operator import document
    import json
    value=document();operation_id=value['operation_id'].lower()
    class Connection:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def execute(self,*args):return self
        def one(self):return ('identity_operator','identity_operator','idop_test',True,True,False,False,False,False,False,False)
        def rollback(self):pytest.fail('unsafe verification cannot roll back to dispatch')
    class Engine:
        disposed=False
        def connect(self):return Connection()
        def dispose(self):self.disposed=True
    engine=Engine()
    monkeypatch.setattr(c,'load_target',lambda _:SimpleNamespace(database='idop_test'))
    monkeypatch.setattr(c,'_connection',lambda _:engine)
    monkeypatch.setattr(c.adapter,'execute',lambda *args:pytest.fail('unsafe execute dispatched'))
    monkeypatch.setattr(c.adapter,'outcome',lambda *args:pytest.fail('unsafe outcome dispatched'))
    with pytest.raises(c.adapter.OperatorError) as failure:
        c.worker([action,'target',json.dumps(value) if action=='execute' else None,operation_id])
    assert failure.value.code=='access_denied' and engine.disposed


@pytest.mark.parametrize('kind', ['account_actor.ensure'])
def test_prepared_retry_inputs_do_not_activate_cli_or_worker(kind, tmp_path, monkeypatch, capsys):
    import operator_cli as c
    import json
    from test_identity_operator_input import document, encode
    value = document(kind)
    path = tmp_path / 'command.json'
    path.write_bytes(encode(value))
    monkeypatch.setattr(c, 'load_target', lambda _: pytest.fail('unsupported target loaded'))
    monkeypatch.setattr(c, 'dispatch', lambda _: pytest.fail('unsupported worker dispatched'))
    monkeypatch.setattr(c, '_connection', lambda _: pytest.fail('unsupported connection opened'))
    assert c.main(['execute', '--owner', 'identity', '--target', 'unused',
                   '--command-file', str(path)]) == 2
    assert json.loads(capsys.readouterr().out)['code'] == 'command_unsupported'
    # The internal transport rejects unsupported variants as malformed requests.
    with pytest.raises(ValueError):
        c.worker(['execute', 'unused', encode(value).decode(), value['operation_id'].lower()])
