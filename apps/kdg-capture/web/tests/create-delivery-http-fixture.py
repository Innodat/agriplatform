"""Selected synthetic delivery host. Reuses existing storage model, never native SQL."""
import argparse
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import socket

HERE=Path(__file__).resolve()
spec=importlib.util.spec_from_file_location('kdg_delivery_base_fixture',HERE.with_name('persistence-http-fixture.py'))
base=importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
REF='a'*43
OriginalConnection=base.Connection
class Connection(OriginalConnection):
    def execute(self,statement,parameters):
        if str(statement)==base.create.ELIGIBILITY and parameters.get('ref')==REF:
            parameters={**parameters,'ref':'synthetic'}
        return super().execute(statement,parameters)
# This replacement is confined to this isolated fixture process. Historical fixture
# source/commands remain unchanged; only this host accepts its explicit seeded ref.
base.Connection=Connection

async def serve(directory):
    directory=Path(directory)
    store=base.Store()
    async def access(request):
        permission=json.loads(request.content)['permission']
        store.checks.append(permission)
        mode=store.mode
        if mode=='outage':return base.httpx.Response(503,json={'detail':{'code':'unavailable'}})
        if mode=='expired':return base.httpx.Response(401,json={'detail':{'code':'authentication_required'}})
        if mode=='deny' or mode=='create_denied' and permission in (base.create.ALL,base.create.ASSIGNED) or mode=='assigned_removed' and permission==base.create.ALL:
            return base.httpx.Response(403,json={'detail':{'code':'access_denied'}})
        account=base.ACTOR if mode=='foreign_read' else base.ACCOUNT
        return base.httpx.Response(200,json=dict(account_id=account,actor_id=base.ACTOR,membership_id='7',authorization_scope=dict(kind='organization',org_id=base.ORG),resource_scope=dict(kind='own_account',account_id=account),permission=permission,decision_id=base.UNKNOWN,checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')))
    args=dict(org_id=base.ORG,access_url='https://access.invalid',service_key='synthetic',transport=base.httpx.MockTransport(access))
    create_app=base.create_http._create_app(base.handler.CreateHandler(**args),store,base.ORG)
    edit_app=base.edit_http._create_app(base.edit_handler.EditHandler(**args),store,base.ORG)
    recovery_app=base.recovery_http._create_app(base.recovery.RecoveryHandler(**args),store,base.ORG)
    read_app=base.read_http._create_app(base.read.ReadHandler(**args),store,base.ORG)
    context_app=base.context_http.create_app(**args)
    edit_context_app=base.edit_context_http._create_app(base.edit_context.EditContextHandler(**args),store,base.ORG)
    @asynccontextmanager
    async def lifespan(app):
        async with AsyncExitStack() as stack:
            for child in (create_app,edit_app,recovery_app,read_app,context_app,edit_context_app):
                await stack.enter_async_context(child.router.lifespan_context(child))
            yield
        (directory/'storage-final.json').write_text(json.dumps(store.snapshot(),sort_keys=True,indent=2)+'\n')
    from starlette.applications import Starlette
    host=Starlette(lifespan=lifespan)
    async def dispatch(scope,receive,send):
        if scope['type']!='http':return await host(scope,receive,send)
        path=scope['path']
        if path=='/__fixture/stop':
            server.should_exit=True
            return await base.JSONResponse({'stopping':True})(scope,receive,send)
        if path=='/__fixture':
            if scope['method']=='POST':
                raw=await receive()
                mode=json.loads(raw.get('body',b'{}')).get('mode')
                if mode not in ('all','create_denied','assigned_removed','inactive_removed','deny','expired','outage','fail_commit','fail_release','foreign_read','invalid_detail'):
                    return await base.JSONResponse({},status_code=422)(scope,receive,send)
                store.mode=mode
            return await base.JSONResponse(store.snapshot())(scope,receive,send)
        child=edit_context_app if path.endswith('/edit-context') else context_app if path=='/api/v1/context' else recovery_app if path.startswith('/api/v1/operations/') else create_app if path=='/api/v1/captures' else read_app if scope['method']=='GET' else edit_app
        await child(scope,receive,send)
    sock=socket.socket()
    sock.bind(('127.0.0.1',0))
    sock.listen(128)
    server=base.uvicorn.Server(base.uvicorn.Config(dispatch,log_level='warning',lifespan='on',timeout_graceful_shutdown=5))
    async def bounded():
        await asyncio.sleep(45)
        server.should_exit=True
    timer=asyncio.create_task(bounded())
    task=asyncio.create_task(server.serve(sockets=[sock]))
    try:
        while not server.started:
            if task.done():await task
            await asyncio.sleep(.01)
        print(json.dumps(dict(origin='http://127.0.0.1:'+str(sock.getsockname()[1]),ids=dict(org=base.ORG,account=base.ACCOUNT,actor=base.ACTOR,child=base.CHILD,version=base.VERSION,questionnaire=base.QUESTIONNAIRE,question=base.QUESTION,decision=base.UNKNOWN,eligibility_ref=REF,definition=base.initial_definition([base.QUESTION,base.ACTOR,base.CHILD,base.VERSION]).model_dump()))),flush=True)
        await task
    finally:
        timer.cancel()
        sock.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--proof-directory',required=True)
    asyncio.run(serve(parser.parse_args().proof_directory))
