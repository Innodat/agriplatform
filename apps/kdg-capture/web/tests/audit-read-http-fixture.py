"""Explicit loopback audit host; Access/storage are synthetic, never native SQL proof."""
import argparse
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
import copy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import socket
from starlette.requests import Request

HERE=Path(__file__).resolve()
spec=importlib.util.spec_from_file_location('kdg_audit_base_fixture',HERE.with_name('persistence-http-fixture.py'))
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
import audit_read
import audit_http

READER,READER_ACTOR,FOREIGN_ORG,FOREIGN_CAPTURE=[f'{n:08x}-bbbb-4bbb-8bbb-{n:012x}' for n in range(31,35)]
OriginalConnection=base.Connection

def metadata(capture_id,capture):
    return dict(capture_id=capture_id,org_id=capture['org'],owner_account_id=capture['account'],
        owner_actor_id=capture['owner_actor'],created_by=capture['created_by'],
        created_at=datetime.fromisoformat(capture['created_at']),updated_by=capture['updated_by'],
        updated_at=datetime.fromisoformat(capture['updated_at']),current_revision=capture['revision'])

class Connection(OriginalConnection):
    def execute(self,statement,p):
        sql=str(statement)
        if "set_config('app.mode'" in sql:self.store.contexts.append({k:p[k] for k in ('org','account','actor','mode')})
        if sql in (base.create.HISTORY_INSERT,base.edit.HISTORY_INSERT):
            capture=self.captures[p['capture']]
            # This fixture records the actual handler-selected revision/attribution.
            # Distinct timestamps deliberately do not model exact commit instants.
            self.history.append(dict(org_id=p['org'],capture_id=p['capture'],event_revision=capture['revision'],
                command_type='capture.create' if sql==base.create.HISTORY_INSERT else 'capture.edit',
                executor_actor_id=p['actor'],initiator_actor_id=p['actor'],
                recorded_at='2026-10-26T00:00:00Z'))
            return base.Rows()
        if sql==audit_read.EVENTS:
            self.store.audit_queries+=1
            if self.store.mode=='fail_sql':raise base.SQLAlchemyError('synthetic-private-query')
            capture=self.captures.get(p['capture'])
            if not capture or capture['org']!=p['org']:return base.Rows([])
            header=metadata(p['capture'],capture)
            rows=[event for event in self.history if event['org_id']==p['org'] and event['capture_id']==p['capture'] and (p['last_revision'] is None or event['event_revision']<p['last_revision'])]
            rows.sort(key=lambda event:event['event_revision'],reverse=True)
            if self.store.mode=='empty_evidence':rows=[]
            result=[]
            for event in rows[:p['row_limit']]:
                row={**header,**{k:datetime.fromisoformat(v) if k=='recorded_at' else v for k,v in event.items() if k not in ('org_id','capture_id')}}
                if self.store.mode=='invalid_event':row['executor_actor_id']=None
                result.append(row)
            if not result:result=[{**header,**dict.fromkeys(('event_revision','command_type','executor_actor_id','initiator_actor_id','recorded_at'))}]
            return base.Rows(copy.deepcopy(result))
        return super().execute(statement,p)
base.Connection=Connection

async def serve(directory):
    directory=Path(directory);store=base.Store();store.mode='writer';store.contexts=[];store.audit_queries=0
    async def access(request):
        permission=json.loads(request.content)['permission'];store.checks.append(permission);mode=store.mode
        if mode=='outage':return base.httpx.Response(503,json={'detail':{'code':'unavailable'}})
        if mode=='expired':return base.httpx.Response(401,json={'detail':{'code':'authentication_required'}})
        if mode=='deny':return base.httpx.Response(403,json={'detail':{'code':'access_denied'}})
        writer=mode=='writer';account=base.ACCOUNT if writer or mode=='other_account' else READER
        actor=base.ACTOR if writer or mode=='other_account' else READER_ACTOR
        scope=dict(kind='organization',org_id=base.ORG) if permission==audit_read.PERMISSION else dict(kind='own_account',account_id=account)
        evidence=dict(account_id=account,actor_id=actor,membership_id='7',authorization_scope=dict(kind='organization',org_id=base.ORG),resource_scope=scope,permission=permission,decision_id=base.UNKNOWN,checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
        if mode=='actor_missing':evidence.pop('actor_id')
        if mode=='wrong_scope':evidence['resource_scope']=dict(kind='own_account',account_id=account)
        if mode=='wrong_org':evidence['resource_scope']=dict(kind='organization',org_id=FOREIGN_ORG)
        if mode=='wrong_permission':evidence['permission']='kdg_capture.capture.read.own'
        return base.httpx.Response(200,json=evidence)
    args=dict(org_id=base.ORG,access_url='https://access.invalid',service_key='synthetic',transport=base.httpx.MockTransport(access))
    audit=audit_http._create_app(audit_read.AuditReadHandler(**args),store,base.ORG)
    create=base.create_http._create_app(base.handler.CreateHandler(**args),store,base.ORG)
    edit=base.edit_http._create_app(base.edit_handler.EditHandler(**args),store,base.ORG)
    own=base.read_http._create_app(base.read.ReadHandler(**args),store,base.ORG)
    def state():
        return dict(acquired=store.acquired,released=store.released,disposed=store.disposed,checks=store.checks,
            contexts=store.contexts,audit_queries=store.audit_queries,outcomes=len(store.outcomes),events=len(store.history),
            capture_revisions={k:v['revision'] for k,v in store.captures.items()},
            stored_evidence=copy.deepcopy(store.history))
    @asynccontextmanager
    async def lifespan(app):
        async with AsyncExitStack() as stack:
            for child in (audit,create,edit,own):await stack.enter_async_context(child.router.lifespan_context(child))
            yield
        (directory/'storage-final.json').write_text(json.dumps(state(),sort_keys=True,indent=2)+'\n')
    from starlette.applications import Starlette
    host=Starlette(lifespan=lifespan)
    async def dispatch(scope,receive,send):
        if scope['type']!='http':return await host(scope,receive,send)
        path=scope['path']
        if path=='/__fixture/stop':
            server.should_exit=True;return await base.JSONResponse({'stopping':True})(scope,receive,send)
        if path=='/__fixture':
            if scope['method']=='POST':
                chunks=[]
                async for chunk in Request(scope,receive).stream():
                    chunks.append(chunk)
                    if sum(map(len,chunks))>1024:return await base.JSONResponse({},status_code=422)(scope,receive,send)
                mode=json.loads(b''.join(chunks) or b'{}').get('mode')
                if mode not in ('writer','reader','deny','outage','expired','actor_missing','wrong_scope','wrong_org','wrong_permission','other_account','inactive_removed','fail_acquire','fail_sql','fail_commit','fail_release','invalid_event','empty_evidence','seed_foreign'):
                    return await base.JSONResponse({},status_code=422)(scope,receive,send)
                store.mode=mode
                if mode=='seed_foreign':
                    with store.lock:
                        record=copy.deepcopy(store.captures[base.CAPTURE]);record['org']=FOREIGN_ORG;store.captures[FOREIGN_CAPTURE]=record
            return await base.JSONResponse(state())(scope,receive,send)
        child=audit if path.startswith('/api/v1/admin/') else create if path=='/api/v1/captures' else edit if scope['method']=='PUT' else own
        await child(scope,receive,send)
    sock=socket.socket();sock.bind(('127.0.0.1',0));sock.listen(128)
    server=base.uvicorn.Server(base.uvicorn.Config(dispatch,log_level='warning',lifespan='on',timeout_graceful_shutdown=5))
    async def bounded():await asyncio.sleep(45);server.should_exit=True
    timer=asyncio.create_task(bounded());task=asyncio.create_task(server.serve(sockets=[sock]))
    try:
        while not server.started:
            if task.done():await task
            await asyncio.sleep(.01)
        print(json.dumps(dict(origin='http://127.0.0.1:'+str(sock.getsockname()[1]),ids=dict(org=base.ORG,account=base.ACCOUNT,actor=base.ACTOR,reader=READER,reader_actor=READER_ACTOR,child=base.CHILD,version=base.VERSION,capture=base.CAPTURE,create=base.CREATE_OP,edit=base.EDIT_OP,noop=base.NOOP_OP,question=base.QUESTION,unknown=base.UNKNOWN,foreign_capture=FOREIGN_CAPTURE))),flush=True)
        await task
    finally:timer.cancel();sock.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--proof-directory',required=True)
    asyncio.run(serve(parser.parse_args().proof_directory))
