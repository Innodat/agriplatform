"""Qualifier supervision only: real synthetic children, no Auth/DB/socket resources."""
import importlib.util
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import pytest

SOURCE=Path(__file__).with_name('qualify_story31_http.py')


def qualifier():
    spec=importlib.util.spec_from_file_location('story31_http_qualifier',SOURCE)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def _hold_probe(proof,repeat,interrupt_during_start=False):
    """Run the real hold/finally/main path with inert prepared HTTP observations."""
    module=qualifier()
    proof.mkdir()
    for marker in ('resource-ready.json','owners-prepared.json','auth-identity-ready.json',
                   'access-seed-ready.json','kdg-parents-ready.json'):
        (proof/marker).write_text('{}')
    values={'org_id':'synthetic-org','foreign_org_id':'foreign-org','auth_port':1234,
            'jwt_secret':'synthetic-private-jwt-secret'}
    accounts={name:{'id':name,'actor_id':name+'-actor','session':{'access_token':name}}
              for name in ('admin','capturer','other','member','platform','foreign','nomember')}
    data={'definition':{'original':True},'commands':{
        name:{'capture_id':name+'-capture'} for name in ('capturer','other')}}
    (proof/'accounts.json').write_text(json.dumps(accounts))
    (proof/'capture-inputs.json').write_text(json.dumps(data))
    children=[];real_popen=subprocess.Popen;second_sent=False
    worker="import signal,sys,time\nsignal.signal(signal.SIGTERM,lambda *_:sys.exit(0))\nprint('ready',flush=True)\nwhile True:time.sleep(5)"
    class Child:
        def __init__(self):
            self.process=real_popen([sys.executable,'-I','-B','-c',worker],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
            assert self.process.stdout.readline().strip()=='ready'
            self.process.stdout.close()
            self.pid=self.process.pid
            children.append(self.pid)
            (proof/'children.json').write_text(json.dumps(children))
            if interrupt_during_start and len(children)==1:
                # The OS child exists, but production Popen has not returned and
                # the supervisor has not registered its handle yet.
                os.kill(os.getpid(),interrupt_during_start)
        def poll(self):return self.process.poll()
        def send_signal(self,number):self.process.send_signal(number)
        def kill(self):self.process.kill()
        def wait(self,timeout):
            nonlocal second_sent
            if repeat and not second_sent:
                second_sent=True
                os.kill(os.getpid(),signal.SIGTERM)
            return self.process.wait(timeout=timeout)
    class Socket:
        def bind(self,*_):pass
        def listen(self,*_):pass
        def getsockname(self):return ('127.0.0.1',12345)
        def fileno(self):return 200
        def close(self):pass
    class Client:
        def __init__(self,**_):self.histories=0
        def __enter__(self):return self
        def __exit__(self,*_):pass
        def get(self,url):return httpx.Response(200 if url.endswith('/health') else 401)
        def request(self,method,url,headers,json):
            name=headers['Authorization'].removeprefix('Bearer ')
            status=200;body={}
            if method=='POST':pass
            elif url.endswith('/api/v1/context'):body={'account_id':accounts[name]['id']}
            elif name!='admin':status=403
            elif '?org_id=' in url:status=422
            elif '/audit-details' in url:
                body={'audit':{'owner_actor_id':'capturer-actor'},'actor_display':{'status':'loaded',
                      'labels':[{'actor_id':'capturer-actor','status':'resolved','display_name':'Synthetic Capturer'}]}}
            elif '?from_date=' in url:
                self.histories+=1
                body={'items':[],'next_cursor':None} if self.histories==1 else {
                    'items':[{'capture_id':'other-capture' if 'cursor=' in url else 'capturer-capture'}],
                    'next_cursor':None if 'cursor=' in url else 'next'}
            else:body={'definition':data['definition'],'owner_account_id':'capturer'}
            return httpx.Response(status,json=body,headers={'Cache-Control':'private, no-store'})
    def hold(_seconds):
        (proof/'holding.json').write_text('{}')
        os.kill(os.getpid(),signal.SIGTERM)
    old_term,old_int=signal.getsignal(signal.SIGTERM),signal.getsignal(signal.SIGINT)
    private_imports=[]
    # The pre-repair qualifier imported a private script. Keep the regression
    # self-contained, and require the completed run to leave this stub unused.
    private_stub=SimpleNamespace(token=lambda *_:private_imports.append(True) or 'synthetic-anon')
    with patch.object(module,'load',return_value=values),patch.object(module,'BASE',proof.parent), \
         patch.object(module,'source_binding',return_value={}), \
         patch.object(module.socket,'socket',Socket),patch.object(module.httpx,'Client',Client), \
         patch.object(module.ssl,'create_default_context',return_value=None), \
         patch.object(module.subprocess,'run',return_value=SimpleNamespace(returncode=0)), \
         patch.object(module.subprocess,'Popen',side_effect=lambda *_,**__:Child()), \
         patch.object(module.time,'sleep',side_effect=hold), \
         patch.dict(sys.modules,{'seed_authority':private_stub}), \
         patch.object(sys,'argv',[str(SOURCE),'--proof',str(proof),'--hold']):
        code=module.main()
    assert not private_imports
    assert signal.getsignal(signal.SIGTERM)==old_term and signal.getsignal(signal.SIGINT)==old_int
    return code


@pytest.mark.parametrize('repeat',[False,True])
def test_hold_sigterm_stops_all_owned_children_and_retains_interruption(tmp_path,repeat):
    proof=tmp_path/'fresh-probe'
    try:
        result=subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),
                               '--hold-probe',str(proof),str(int(repeat))],capture_output=True,text=True,timeout=15)
        assert result.returncode==128+signal.SIGTERM,result.stderr
        assert (proof/'holding.json').is_file()
        run=next(proof.glob('http-*'))
        evidence=json.loads((run/'result.json').read_text())
        assert evidence['passed'] is False
        assert evidence['interruption_signal']==signal.SIGTERM
        assert evidence['interruption_phase']=='hold'
        assert evidence['checks'][-1]=='read-retry-preserves-audit'
        assert sorted(evidence['normal_owned_server_stop'],key=lambda row:row['name'])==[
            {'name':name,'exit_code':0,'forced':False} for name in ('access','auth','kdg')]
        failure=json.loads((run/'failure.json').read_text())
        assert failure['type']=='QualificationInterrupted' and failure['signal']==signal.SIGTERM
        assert 'synthetic-private-jwt-secret' not in result.stdout+result.stderr
        for pid in json.loads((proof/'children.json').read_text()):
            assert not Path('/proc',str(pid)).exists()
    finally:
        # A failing pre-fix supervisor must not leave these test-owned workers.
        manifest=proof/'children.json'
        if manifest.is_file():
            for pid in json.loads(manifest.read_text()):
                try:os.kill(pid,signal.SIGTERM)
                except ProcessLookupError:pass


def test_synthetic_anon_key_preserves_prepared_gotrue_contract_without_private_import(monkeypatch):
    module=qualifier()
    monkeypatch.setattr(module.time,'time',lambda:1000)
    values={'auth_port':1234,'jwt_secret':'synthetic-private-jwt-secret'}
    encoded=module._anon_token(values)
    header,payload,signature=encoded.split('.')
    decode=lambda value:base64.urlsafe_b64decode(value+'='*((-len(value))%4))
    assert json.loads(decode(header))=={'alg':'HS256','typ':'JWT'}
    assert json.loads(decode(payload))=={'role':'anon','aud':'authenticated','iat':995,
        'exp':8200,'iss':'http://127.0.0.1:1234'}
    expected=hmac.new(values['jwt_secret'].encode(),(header+'.'+payload).encode(),hashlib.sha256).digest()
    assert hmac.compare_digest(decode(signature),expected)


@pytest.mark.parametrize('number',[signal.SIGTERM,signal.SIGINT])
def test_signal_after_child_creation_is_deferred_until_registration_and_reaped(tmp_path,number):
    proof=tmp_path/'fresh-start-probe'
    try:
        result=subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()),
                               '--hold-probe',str(proof),'0',str(int(number))],
                              capture_output=True,text=True,timeout=15)
        assert result.returncode==128+number,result.stderr
        children=json.loads((proof/'children.json').read_text())
        assert len(children)==1  # Pending termination prevents other launches.
        run=next(proof.glob('http-*'))
        evidence=json.loads((run/'result.json').read_text())
        assert evidence['passed'] is False
        assert evidence['interruption_signal']==number
        assert evidence['interruption_phase']=='starting'
        assert evidence['normal_owned_server_stop']==[{'name':'auth','exit_code':0,'forced':False}]
        assert evidence['checks']==[] and not (proof/'holding.json').exists()
        assert not (run/'access.log').exists() and not (run/'kdg.log').exists()
        assert not Path('/proc',str(children[0])).exists()
    finally:
        manifest=proof/'children.json'
        if manifest.is_file():
            for pid in json.loads(manifest.read_text()):
                try:os.kill(pid,signal.SIGTERM)
                except ProcessLookupError:pass


if __name__=='__main__':
    assert sys.argv[1]=='--hold-probe'
    raise SystemExit(_hold_probe(Path(sys.argv[2]),bool(int(sys.argv[3])),int(sys.argv[4]) if len(sys.argv)>4 else 0))
