"""Explicit loopback context host. Access and storage are synthetic; no native SQL proof."""
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
spec=importlib.util.spec_from_file_location('kdg_admin_context_base_fixture',HERE.with_name('admin-read-http-fixture.py'))
inherited=importlib.util.module_from_spec(spec);spec.loader.exec_module(inherited)
base=inherited.base
import admin_edit_context as context
import admin_edit_context_http as boundary

async def serve(directory):
    directory=Path(directory);store=base.Store();store.contexts=[];store.admin_queries=0
    definition=base.initial_definition([base.QUESTION,base.ACTOR,base.CHILD,base.VERSION]).model_dump()
    definition['questions'][0]['label']='Original retained question'
    for index,key in enumerate(inherited.CAPTURES[:4]):
        other=index in (1,2);actor=inherited.OTHER_ACTOR if other else base.ACTOR
        store.captures[key]=dict(org=inherited.FOREIGN_ORG if index==3 else base.ORG,
            account=inherited.OTHER_ACCOUNT if other else base.ACCOUNT,owner_actor=actor,
            child=base.CHILD,version=base.VERSION,questionnaire=base.QUESTIONNAIRE,
            display_version=1,definition=copy.deepcopy(definition),revision=index+1,date='2026-10-25',
            answers={base.QUESTION:{'value':index+1},**{q:{'value':False} for q in (base.ACTOR,base.CHILD,base.VERSION)}},
            captured_at='2026-10-25T10:00:00Z',created_by=actor,created_at='2026-10-26T00:00:00Z',
            updated_by=base.ACTOR,updated_at='2026-10-26T01:00:00Z')
    original=copy.deepcopy(store.captures)
    async def access(request):
        assert store.acquired==store.released,'authority_must_precede_checkout'
        permission=json.loads(request.content)['permission'];store.checks.append(permission);mode=store.mode
        read_all=permission=='kdg_capture.capture.read.all';edit_all=permission=='kdg_capture.capture.edit.all'
        if (mode=='deny_read' and read_all) or (mode=='deny_edit' and edit_all):return base.httpx.Response(403,json={'detail':{'code':'access_denied'}})
        if mode=='outage_read' and read_all or mode=='outage_edit' and edit_all:return base.httpx.Response(503,json={'detail':{'code':'unavailable'}})
        if mode=='expired':return base.httpx.Response(401,json={'detail':{'code':'authentication_required'}})
        if mode=='actor_setup' and edit_all:return base.httpx.Response(409,json={'detail':{'code':'identity.actor_setup_required'}})
        evidence=dict(account_id=base.ACCOUNT,actor_id=base.ACTOR,membership_id='7',
            authorization_scope=dict(kind='organization',org_id=base.ORG),
            resource_scope=dict(kind='organization',org_id=base.ORG) if read_all or edit_all else dict(kind='own_account',account_id=base.ACCOUNT),
            permission=permission,decision_id=base.UNKNOWN,checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
        if edit_all:
            if mode=='mismatch_account':evidence['account_id']=inherited.OTHER_ACCOUNT
            if mode=='mismatch_actor':evidence['actor_id']=inherited.OTHER_ACTOR
            if mode=='mismatch_membership':evidence['membership_id']='8'
            if mode=='wrong_auth_org':evidence['authorization_scope']=dict(kind='organization',org_id=inherited.FOREIGN_ORG)
            if mode=='wrong_resource_org':evidence['resource_scope']=dict(kind='organization',org_id=inherited.FOREIGN_ORG)
            if mode=='wrong_resource_kind':evidence['resource_scope']=dict(kind='own_account',account_id=base.ACCOUNT)
            if mode=='wrong_permission':evidence['permission']='kdg_capture.capture.edit.own'
            if mode=='missing_actor':evidence.pop('actor_id')
        return base.httpx.Response(200,json=evidence)
    args=dict(org_id=base.ORG,access_url='https://access.invalid',service_key='synthetic',transport=base.httpx.MockTransport(access))
    admin=boundary._create_app(context.AdminEditContextHandler(**args),store,base.ORG)
    read=inherited.admin_http._create_app(inherited.admin_read.AdminReadHandler(**args),store,base.ORG)
    own=base.edit_context_http._create_app(base.edit_context.EditContextHandler(**args),store,base.ORG)
    def state():return dict(acquired=store.acquired,released=store.released,disposed=store.disposed,checks=store.checks,contexts=store.contexts,queries=store.admin_queries,records_unchanged=store.captures==original,outcomes=len(store.outcomes),events=len(store.history))
    @asynccontextmanager
    async def lifespan(app):
        async with AsyncExitStack() as stack:
            for child in (admin,read,own):await stack.enter_async_context(child.router.lifespan_context(child))
            yield
        (directory/'storage-final.json').write_text(json.dumps(state(),sort_keys=True,indent=2)+'\n')
    from starlette.applications import Starlette
    host=Starlette(lifespan=lifespan)
    async def dispatch(scope,receive,send):
        if scope['type']!='http':return await host(scope,receive,send)
        path=scope['path']
        if path=='/__fixture/stop':server.should_exit=True;return await base.JSONResponse({'stopping':True})(scope,receive,send)
        if path=='/__fixture':
            if scope['method']=='POST':
                chunks=[];size=0
                async for chunk in Request(scope,receive).stream():
                    size+=len(chunk)
                    if size>1024:return await base.JSONResponse({},status_code=422)(scope,receive,send)
                    chunks.append(chunk)
                mode=json.loads(b''.join(chunks) or b'{}').get('mode')
                if mode not in ('all','deny_read','deny_edit','outage_read','outage_edit','expired','actor_setup','mismatch_account','mismatch_actor','mismatch_membership','wrong_auth_org','wrong_resource_org','wrong_resource_kind','wrong_permission','missing_actor','fail_acquire','fail_sql','fail_commit','fail_release','invalid_detail','inactive_removed'):
                    return await base.JSONResponse({},status_code=422)(scope,receive,send)
                store.mode=mode
            return await base.JSONResponse(state())(scope,receive,send)
        child=admin if path.startswith('/api/v1/admin/') and path.endswith('/edit-context') else read if path.startswith('/api/v1/admin/') else own
        await child(scope,receive,send)
    sock=socket.socket();sock.bind(('127.0.0.1',0));sock.listen(128)
    server=base.uvicorn.Server(base.uvicorn.Config(dispatch,log_level='warning',lifespan='on',timeout_graceful_shutdown=5))
    async def bounded():await asyncio.sleep(45);server.should_exit=True
    timer=asyncio.create_task(bounded());task=asyncio.create_task(server.serve(sockets=[sock]))
    try:
        while not server.started:
            if task.done():await task
            await asyncio.sleep(.01)
        print(json.dumps(dict(origin='http://127.0.0.1:'+str(sock.getsockname()[1]),ids=dict(org=base.ORG,account=base.ACCOUNT,actor=base.ACTOR,other_account=inherited.OTHER_ACCOUNT,other_actor=inherited.OTHER_ACTOR,captures=inherited.CAPTURES))),flush=True)
        await task
    finally:timer.cancel();sock.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--proof-directory',required=True)
    asyncio.run(serve(parser.parse_args().proof_directory))
