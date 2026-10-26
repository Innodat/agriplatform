"""Explicit loopback synthetic setup host; no native storage or live authority."""
import argparse
import asyncio
import copy
from contextlib import asynccontextmanager,contextmanager
from datetime import datetime,timezone
import json
from pathlib import Path
import socket
import sys
import threading
from types import SimpleNamespace

APP=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(APP/'write-candidate'),str(APP/'api')]
import httpx
import uvicorn
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import JSONResponse
import provision
import provision_http
from questionnaire import initial_definition

ORG,ACCOUNT,ACTOR,CHILD,VERSION,QUESTIONNAIRE,QUESTION,ASSIGNMENT,DECISION=[f'{n:08x}-aaaa-4aaa-8aaa-{n:012x}' for n in range(1,10)]
class Rows:
    def __init__(self,value=None):self.value=value
    def mappings(self):return self
    def one_or_none(self):return self.value
    def all(self):return self.value
class Store:
    def __init__(self):
        self.mode='all';self.acquired=0;self.released=0;self.commits=0;self.disposed=0
        self.checks=[];self.refs={};self.lock=threading.Lock()
    def snapshot(self):return dict(mode=self.mode,acquired=self.acquired,released=self.released,commits=self.commits,disposed=self.disposed,checks=self.checks,eligibility=copy.deepcopy(self.refs),captures=0,outcomes=0,history=0)
    def dispose(self):self.disposed+=1
    @contextmanager
    def connect(self):
        if self.mode=='fail_acquire':raise SQLAlchemyError('synthetic failure')
        self.acquired+=1
        try:yield Connection(self)
        finally:
            self.released+=1
            if self.mode=='fail_release':raise SQLAlchemyError('synthetic failure')
class Connection:
    def __init__(self,store):
        self.store=store;self.active=False;self.autocommit=False
        self.connection=SimpleNamespace(driver_connection=self)
    def in_transaction(self):return self.active
    def get_execution_options(self):return {}
    def get_isolation_level(self):return 'READ COMMITTED'
    @contextmanager
    def begin(self):
        with self.store.lock:
            self.active=True;self.refs=copy.deepcopy(self.store.refs)
            try:
                yield self
                if self.store.mode=='fail_commit':raise SQLAlchemyError('synthetic failure')
                self.store.refs=self.refs;self.store.commits+=1
            finally:self.active=False
    def execute(self,statement,p):
        sql=str(statement);mode=self.store.mode
        if 'kdg_capture.' in sql and mode=='fail_sql':raise SQLAlchemyError('synthetic failure')
        child=dict(id=CHILD,org_id=ORG,display_name='Synthetic child',active=mode!='inactive',revision=3)
        if sql==provision.VERSION:
            return Rows(None if mode=='no_published' else dict(id=VERSION,org_id=ORG,questionnaire_id=QUESTIONNAIRE,display_version=2,definition=initial_definition([QUESTION,ACTOR,CHILD,VERSION]).model_dump()))
        if sql in (provision.CHILDREN,provision.ASSIGNED_CHILDREN):return Rows([] if mode in ('empty','inactive') else [child])
        if sql==provision.CHILD:return Rows(child)
        if sql==provision.ASSIGNMENT:return Rows(dict(id=ASSIGNMENT,org_id=ORG,child_id=CHILD,account_id=ACCOUNT,membership_id=7,active=mode!='assignment_changed',revision=4))
        if sql==provision.ISSUE:
            now=datetime.now(timezone.utc);self.refs[p['ref']]={**p,'issued_at':now.isoformat().replace('+00:00','Z')}
            return Rows(dict(issued_at=now))
        if sql in (
            "SELECT set_config('statement_timeout', :statement, true), set_config('lock_timeout', :lock, true)",
            "SELECT set_config('transaction_timeout', :total, true), set_config('app.org_id', :org, true), set_config('app.account_id', :account, true), set_config('app.actor_id', :actor, true), set_config('app.mode', :mode, true)",
            provision.create.CHILD_LOCK):return Rows()
        raise AssertionError('unmodeled_synthetic_sql')

async def serve(directory):
    directory=Path(directory);store=Store()
    async def access(request):
        permission=json.loads(request.content)['permission'];store.checks.append(permission);mode=store.mode
        if mode=='outage':return httpx.Response(503,json={'detail':{'code':'unavailable'}})
        if mode=='expired':return httpx.Response(401,json={'detail':{'code':'authentication_required'}})
        denied=mode=='deny' or mode=='edit_denied' and permission==provision.EDIT or mode=='not_permitted' and permission in (provision.create.ALL,provision.create.ASSIGNED) or mode in ('assigned','assignment_changed') and permission==provision.create.ALL
        if denied:return httpx.Response(403,json={'detail':{'code':'access_denied'}})
        return httpx.Response(200,json=dict(account_id=ACCOUNT,actor_id=CHILD if mode=='identity_mismatch' and permission==provision.EDIT else ACTOR,membership_id='7',authorization_scope=dict(kind='organization',org_id=ORG),resource_scope=dict(kind='own_account',account_id=ACCOUNT),permission=permission,decision_id=DECISION,checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')))
    authority=provision.ProvisionHandler(org_id=ORG,questionnaire_id=QUESTIONNAIRE,access_url='https://access.invalid',service_key='synthetic',transport=httpx.MockTransport(access))
    app=provision_http._create_app(authority,store,ORG,QUESTIONNAIRE)
    @asynccontextmanager
    async def lifespan(host):
        async with app.router.lifespan_context(app):yield
        (directory/'provision-final.json').write_text(json.dumps(store.snapshot(),sort_keys=True,indent=2)+'\n')
    from starlette.applications import Starlette
    host=Starlette(lifespan=lifespan)
    async def dispatch(scope,receive,send):
        if scope['type']!='http':return await host(scope,receive,send)
        if scope['path']=='/__fixture/stop':
            server.should_exit=True
            return await JSONResponse({'stopping':True})(scope,receive,send)
        if scope['path']=='/__fixture':
            if scope['method']=='POST':
                raw=bytearray()
                while True:
                    message=await receive();raw.extend(message.get('body',b''))
                    if len(raw)>1024:return await JSONResponse({},status_code=422)(scope,receive,send)
                    if not message.get('more_body'):break
                mode=json.loads(raw).get('mode')
                if mode not in ('all','assigned','assignment_changed','empty','inactive','no_published','not_permitted','deny','expired','edit_denied','identity_mismatch','outage','fail_acquire','fail_sql','fail_commit','fail_release'):return await JSONResponse({},status_code=422)(scope,receive,send)
                store.mode=mode
            return await JSONResponse(store.snapshot())(scope,receive,send)
        await app(scope,receive,send)
    sock=socket.socket();sock.bind(('127.0.0.1',0));sock.listen(128)
    server=uvicorn.Server(uvicorn.Config(dispatch,log_level='warning',lifespan='on',timeout_graceful_shutdown=5))
    async def bounded():
        await asyncio.sleep(45);server.should_exit=True
    timer=asyncio.create_task(bounded());task=asyncio.create_task(server.serve(sockets=[sock]))
    try:
        while not server.started:
            if task.done():await task
            await asyncio.sleep(.01)
        print(json.dumps(dict(origin='http://127.0.0.1:'+str(sock.getsockname()[1]),ids=dict(org=ORG,account=ACCOUNT,actor=ACTOR,child=CHILD,version=VERSION,questionnaire=QUESTIONNAIRE,question=QUESTION,assignment=ASSIGNMENT,decision=DECISION))),flush=True)
        await task
    finally:timer.cancel();sock.close()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--proof-directory',required=True)
    args=parser.parse_args();asyncio.run(serve(args.proof_directory))
