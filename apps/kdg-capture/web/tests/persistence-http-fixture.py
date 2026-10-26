"""Explicit loopback-only synthetic host. No database, credentials or active app wiring.

Storage models transaction effects for HTTP integration only; it establishes no native
permissions, SQL execution, driver cancellation or rollback properties.
"""
import argparse
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager, contextmanager
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import socket
import sys
import threading
from types import SimpleNamespace
from uuid import UUID

HERE=Path(__file__).resolve()
APP=HERE.parents[2]
sys.path[:0]=[str(APP/'write-candidate'),str(APP/'api')]
import httpx
import uvicorn
from starlette.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import create_http
import edit_http
import recovery_http
import main as context_http
import capture_create as create
import capture_edit as edit
import capture_create_handler as handler
import capture_edit_handler as edit_handler
import operation_recovery as recovery
import operation_outcomes as outcomes
from questionnaire import initial_definition

ORG,ACCOUNT,ACTOR,CHILD,VERSION,CAPTURE,CREATE_OP,QUESTIONNAIRE,QUESTION,EDIT_OP,NOOP_OP,UNKNOWN=[f'{n:08x}-aaaa-4aaa-8aaa-{n:012x}' for n in range(1,13)]

class Rows:
    rowcount=1
    def __init__(self,value=None):self.value=value
    def mappings(self):return self
    def one_or_none(self):return self.value

class Store:
    def __init__(self):
        self.captures={};self.outcomes={};self.history=[];self.mode='all'
        self.acquired=0;self.released=0;self.disposed=0;self.commits=0;self.checks=[]
        self.lock=threading.Lock()
    def snapshot(self):return dict(captures=copy.deepcopy(self.captures),outcomes=len(self.outcomes),history=len(self.history),acquired=self.acquired,released=self.released,disposed=self.disposed,commits=self.commits,checks=self.checks,mode=self.mode)
    @asynccontextmanager
    async def unused(self):yield
    def dispose(self):self.disposed+=1
    @contextmanager
    def connect(self):
        if self.mode=='fail_acquire':raise SQLAlchemyError('synthetic acquisition failure')
        self.acquired+=1
        try:yield Connection(self)
        finally:
            self.released+=1
            if self.mode=='fail_release':raise SQLAlchemyError('synthetic release failure')

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
            self.active=True
            self.captures=copy.deepcopy(self.store.captures);self.outcomes=copy.deepcopy(self.store.outcomes);self.history=copy.deepcopy(self.store.history)
            try:
                yield self
                if self.store.mode=='fail_commit':raise SQLAlchemyError('synthetic commit failure')
                self.store.captures=self.captures;self.store.outcomes=self.outcomes;self.store.history=self.history;self.store.commits+=1
            finally:self.active=False
    def execute(self,statement,p):
        sql=str(statement)
        if 'kdg_capture.' in sql and self.store.mode=='fail_sql':raise SQLAlchemyError('synthetic SQL failure')
        if sql==outcomes.SELECT:return Rows(self.outcomes.get((p['org'],p['account'],p['command'],p['operation'])))
        if sql==create.CHILD:return Rows(dict(active=True) if p['org']==ORG and p['child']==CHILD else None)
        if sql==create.ELIGIBILITY:return Rows(dict(membership_id=7,observed_active=True) if p['org']==ORG and p['account']==ACCOUNT and p['child']==CHILD and p['ref']=='synthetic' else None)
        if sql==create.ASSIGNMENT:return Rows(dict(membership_id=7,active=True) if p['org']==ORG and p['account']==ACCOUNT and p['child']==CHILD and self.store.mode!='assigned_removed' else None)
        if sql==create.VERSION:return Rows(dict(questionnaire_id=QUESTIONNAIRE,definition=initial_definition([QUESTION,ACTOR,CHILD,VERSION]).model_dump()) if p['org']==ORG and p['version']==VERSION else None)
        if sql in (handler.STORED_CAPTURE,edit_handler.TARGET,recovery.TARGET):
            capture=self.captures.get(p['capture'])
            if not capture or capture['org']!=p['org'] or capture['account']!=p['account']:return Rows()
            result=dict(id=p['capture'],org_id=p['org'],owner_account_id=p['account'])
            if sql==handler.STORED_CAPTURE:result['child_id']=capture['child']
            return Rows(result)
        if sql==edit.CAPTURE:
            capture=self.captures.get(p['capture'])
            if not capture or capture['org']!=p['org'] or capture['account']!=p['account']:return Rows()
            return Rows(dict(questionnaire_version_id=capture['version'],revision=capture['revision'],unchanged=capture['date']==p['date'].isoformat() and capture['answers']==json.loads(p['answers'])))
        if sql==create.CAPTURE_INSERT:
            if p['capture'] in self.captures:raise SQLAlchemyError('synthetic duplicate capture')
            self.captures[p['capture']]=dict(org=p['org'],account=p['account'],child=p['child'],version=p['version'],revision=1,date=p['date'].isoformat(),answers=json.loads(p['answers']))
            return Rows()
        if sql==edit.UPDATE:
            capture=self.captures[p['capture']];capture.update(date=p['date'].isoformat(),answers=json.loads(p['answers']),revision=p['revision'])
            return Rows()
        if sql==outcomes.INSERT:
            key=(p['org'],p['account'],p['command'],p['operation'])
            if key in self.outcomes:raise SQLAlchemyError('synthetic duplicate outcome')
            self.outcomes[key]=dict(id=p['id'],org_id=p['org'],executor_account_id=p['account'],executor_actor_id=p['actor'],command_type=p['command'],operation_id=p['operation'],command_version=1,result_version=1,result=json.loads(p['result']),initiator_actor_id=p['actor'],committed_at=datetime.now(timezone.utc))
            return Rows()
        if sql in (create.HISTORY_INSERT,edit.HISTORY_INSERT):
            self.history.append((p['capture'],p.get('revision',1)))
            return Rows()
        # Only the actual bounded helper/context and lock statements are modeled.
        if sql in (
            "SELECT set_config('statement_timeout', :statement, true), set_config('lock_timeout', :lock, true)",
            "SELECT set_config('transaction_timeout', :total, true), set_config('app.org_id', :org, true), set_config('app.account_id', :account, true), set_config('app.actor_id', :actor, true), set_config('app.mode', :mode, true)",
            'SELECT pg_advisory_xact_lock(:key)', create.CHILD_LOCK,
        ):return Rows()
        raise AssertionError('unmodeled_synthetic_sql')

async def serve(directory):
    directory=Path(directory);store=Store()
    async def access(request):
        permission=json.loads(request.content)['permission'];store.checks.append(permission)
        mode=store.mode
        if mode=='outage':return httpx.Response(503,json={'detail':{'code':'unavailable'}})
        if mode in ('deny','expired'):return httpx.Response(403 if mode=='deny' else 401,json={'detail':{'code':'access_denied' if mode=='deny' else 'authentication_required'}})
        if mode.startswith('assigned') and permission==create.ALL:return httpx.Response(403,json={'detail':{'code':'access_denied'}})
        return httpx.Response(200,json=dict(account_id=ACCOUNT,actor_id=ACTOR,membership_id='7',authorization_scope=dict(kind='organization',org_id=ORG),resource_scope=dict(kind='own_account',account_id=ACTOR if mode=='mismatch' else ACCOUNT),permission=permission,decision_id=UNKNOWN,checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')))
    transport=httpx.MockTransport(access)
    args=dict(org_id=ORG,access_url='https://access.invalid',service_key='synthetic',transport=transport)
    create_app=create_http._create_app(handler.CreateHandler(**args),store,ORG)
    edit_app=edit_http._create_app(edit_handler.EditHandler(**args),store,ORG)
    recovery_app=recovery_http._create_app(recovery.RecoveryHandler(**args),store,ORG)
    context_app=context_http.create_app(**args)
    @asynccontextmanager
    async def lifespan(app):
        async with AsyncExitStack() as stack:
            for child in (create_app,edit_app,recovery_app,context_app):await stack.enter_async_context(child.router.lifespan_context(child))
            yield
        (directory/'storage-final.json').write_text(json.dumps(store.snapshot(),sort_keys=True,indent=2)+'\n')
    from starlette.applications import Starlette
    host=Starlette(lifespan=lifespan)
    async def dispatch(scope,receive,send):
        if scope['type']!='http':return await host(scope,receive,send)
        path=scope['path']
        if path=='/__fixture/stop':
            server.should_exit=True
            return await JSONResponse({'stopping':True})(scope,receive,send)
        if path=='/__fixture':
            if scope['method']=='POST':
                raw=await receive();mode=json.loads(raw.get('body',b'{}')).get('mode')
                if mode not in ('all','assigned','assigned_removed','deny','expired','mismatch','outage','fail_acquire','fail_sql','fail_commit','fail_release'):return await JSONResponse({},status_code=422)(scope,receive,send)
                store.mode=mode
            return await JSONResponse(store.snapshot())(scope,receive,send)
        child=context_app if path=='/api/v1/context' else recovery_app if path.startswith('/api/v1/operations/') else create_app if path=='/api/v1/captures' else edit_app
        await child(scope,receive,send)
    sock=socket.socket();sock.bind(('127.0.0.1',0));sock.listen(128)
    server=uvicorn.Server(uvicorn.Config(dispatch,log_level='warning',lifespan='on',timeout_graceful_shutdown=5))
    async def bounded():
        await asyncio.sleep(45);server.should_exit=True
    timer=asyncio.create_task(bounded())
    task=asyncio.create_task(server.serve(sockets=[sock]))
    try:
        while not server.started:
            if task.done():await task
            await asyncio.sleep(.01)
        print(json.dumps(dict(origin='http://127.0.0.1:'+str(sock.getsockname()[1]),ids=dict(org=ORG,account=ACCOUNT,actor=ACTOR,child=CHILD,version=VERSION,capture=CAPTURE,create=CREATE_OP,edit=EDIT_OP,noop=NOOP_OP,question=QUESTION,unknown=UNKNOWN))),flush=True)
        await task
    finally:timer.cancel();sock.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--proof-directory',required=True)
    args=parser.parse_args();asyncio.run(serve(args.proof_directory))
