"""Synthetic loopback administrator/own conditional writes; never native SQL evidence."""
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
spec=importlib.util.spec_from_file_location('kdg_admin_edit_base_fixture',HERE.with_name('admin-read-http-fixture.py'))
inherited=importlib.util.module_from_spec(spec);spec.loader.exec_module(inherited)
base=inherited.base
import admin_edit
import admin_edit_http

CAPTURES=inherited.CAPTURES
FOREIGN_OPERATION='77777777-dddd-4ddd-8ddd-777777777777'
def json_equal(left,right):
    return json.dumps(left,sort_keys=True,separators=(',',':'))==json.dumps(right,sort_keys=True,separators=(',',':'))
class Connection(inherited.Connection):
    def execute(self,statement,p):
        sql=str(statement)
        if 'kdg_capture.' in sql and self.store.mode=='fail_sql':raise base.SQLAlchemyError('synthetic-private-sql')
        if sql==admin_edit.TARGET:
            value=self.captures.get(p['capture'])
            if self.store.mode=='target_sql_error':raise base.SQLAlchemyError('synthetic-private-target')
            if self.store.mode=='target_unavailable' or not value or value['org']!=p['org']:return base.Rows()
            return base.Rows(dict(id=p['capture'],org_id=value['org'],owner_account_id=value['account']))
        if sql==admin_edit.CAPTURE:
            value=self.captures.get(p['capture'])
            if not value or value['org']!=p['org']:return base.Rows()
            return base.Rows(dict(questionnaire_version_id=value['version'],revision=value['revision'],unchanged=value['date']==p['date'].isoformat() and json_equal(value['answers'],json.loads(p['answers']))))
        if sql==admin_edit.UPDATE:
            value=self.captures.get(p['capture']);result=base.Rows();result.rowcount=0
            if value and value['org']==p['org'] and value['revision']==p['previous']:
                value.update(date=p['date'].isoformat(),answers=json.loads(p['answers']),revision=p['revision'],updated_by=p['actor'],updated_at=datetime.now(timezone.utc).isoformat());result.rowcount=1
            return result
        if sql in (admin_edit.HISTORY_INSERT,base.edit.HISTORY_INSERT):
            if self.store.mode=='fail_history':raise base.SQLAlchemyError('synthetic-private-history')
            value=self.captures[p['capture']]
            self.history.append(dict(capture_id=p['capture'],revision=value['revision'],owner_account_id=value['account'],owner_actor_id=value['owner_actor'],created_by=value['created_by'],executor_account_id=p['account'],executor_actor_id=p['actor'],initiator_actor_id=p['actor'],operation_id=p['operation'],outcome_id=p['outcome'],answers=copy.deepcopy(value['answers'])))
            return base.Rows()
        if sql==base.outcomes.INSERT and self.store.mode=='fail_outcome':raise base.SQLAlchemyError('synthetic-private-outcome')
        return super().execute(statement,p)
base.Connection=Connection

async def serve(directory):
    directory=Path(directory);store=base.Store();store.contexts=[];store.admin_queries=0
    definition=base.initial_definition([base.QUESTION,base.ACTOR,base.CHILD,base.VERSION]).model_dump()
    definition['questions'][0]['label']='Original retained question'
    for index,key in enumerate(CAPTURES[:4]):
        store.captures[key]=dict(org=inherited.FOREIGN_ORG if index==2 else base.ORG,
            account=inherited.OTHER_ACCOUNT,owner_actor=inherited.OTHER_ACTOR,
            child=base.CHILD,version=base.VERSION,questionnaire=base.QUESTIONNAIRE,
            display_version=1,definition=copy.deepcopy(definition),revision=1,date='2026-10-25',
            answers={base.QUESTION:{'value':1},**{q:{'value':False} for q in (base.ACTOR,base.CHILD,base.VERSION)}},
            captured_at='2026-10-25T10:00:00Z',created_by=inherited.OTHER_ACTOR,
            created_at='2026-10-26T00:00:00Z',updated_by=inherited.OTHER_ACTOR,updated_at='2026-10-26T00:00:00Z')
    original=copy.deepcopy(store.captures)
    store.outcomes[(inherited.FOREIGN_ORG,base.ACCOUNT,'capture.edit',FOREIGN_OPERATION)]=dict(
        id=base.CHILD,org_id=inherited.FOREIGN_ORG,executor_account_id=base.ACCOUNT,
        executor_actor_id=base.ACTOR,command_type='capture.edit',operation_id=FOREIGN_OPERATION,
        command_version=1,result_version=1,result=dict(capture_id=CAPTURES[2],revision='1'),
        initiator_actor_id=base.ACTOR,committed_at=datetime.now(timezone.utc))
    async def access(request):
        permission=json.loads(request.content)['permission'];token=request.headers['authorization'].split(' ',1)[1]
        store.checks.append(dict(permission=permission,principal=token))
        if store.mode=='outage':return base.httpx.Response(503,json={'detail':{'code':'unavailable'}})
        if store.mode=='expired':return base.httpx.Response(401,json={'detail':{'code':'authentication_required'}})
        if store.mode=='actor_setup':return base.httpx.Response(409,json={'detail':{'code':'identity.actor_setup_required'}})
        if store.mode=='deny_read' and permission=='kdg_capture.capture.read.all' or store.mode=='deny_edit' and permission=='kdg_capture.capture.edit.all':return base.httpx.Response(403,json={'detail':{'code':'access_denied'}})
        facilitator=token=='facilitator';outsider=token=='other-admin'
        account=inherited.OTHER_ACCOUNT if facilitator else inherited.FOREIGN_ORG if outsider else base.ACCOUNT
        actor=inherited.OTHER_ACTOR if facilitator else base.CHILD if outsider else base.ACTOR
        is_all=permission.endswith('.all')
        evidence=dict(account_id=account,actor_id=actor,membership_id='7',authorization_scope=dict(kind='organization',org_id=base.ORG),resource_scope=dict(kind='organization',org_id=base.ORG) if is_all else dict(kind='own_account',account_id=account),permission=permission,decision_id=base.UNKNOWN,checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
        if store.mode=='mismatch_actor' and permission.endswith('edit.all'):evidence['actor_id']=base.CHILD
        if store.mode=='wrong_org':evidence['resource_scope']=dict(kind='organization',org_id=inherited.FOREIGN_ORG)
        return base.httpx.Response(200,json=evidence)
    args=dict(org_id=base.ORG,access_url='https://access.invalid',service_key='synthetic',transport=base.httpx.MockTransport(access))
    apps=[admin_edit_http._create_app(admin_edit.authority.AdminEditContextHandler(**args),store,store,base.ORG),base.edit_http._create_app(base.edit_handler.EditHandler(**args),store,base.ORG),inherited.admin_http._create_app(inherited.admin_read.AdminReadHandler(**args),store,base.ORG),base.recovery_http._create_app(base.recovery.RecoveryHandler(**args),store,base.ORG)]
    def state():return dict(json_equality_type_distinct=not json_equal({'value':True},{'value':1}) and not json_equal({'value':False},{'value':0}) and json_equal({'a':1,'b':False},{'b':False,'a':1}),captures=store.captures,events=store.history,outcomes=len(store.outcomes),acquired=store.acquired,released=store.released,disposed=store.disposed,commits=store.commits,checks=store.checks,contexts=store.contexts,foreign_unchanged=store.captures[CAPTURES[2]]==original[CAPTURES[2]])
    @asynccontextmanager
    async def lifespan(app):
        async with AsyncExitStack() as stack:
            for child in apps:await stack.enter_async_context(child.router.lifespan_context(child))
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
                raw=bytearray()
                async for chunk in Request(scope,receive).stream():
                    raw.extend(chunk)
                    if len(raw)>1024:return await base.JSONResponse({},status_code=422)(scope,receive,send)
                mode=json.loads(raw).get('mode')
                if mode not in ('all','inactive_removed','deny_read','deny_edit','outage','expired','actor_setup','mismatch_actor','wrong_org','fail_acquire','fail_sql','fail_commit','fail_release','fail_history','fail_outcome','target_unavailable','target_sql_error','drop_response'):return await base.JSONResponse({},status_code=422)(scope,receive,send)
                store.mode=mode
            return await base.JSONResponse(state())(scope,receive,send)
        child=apps[0] if path.startswith('/api/v1/admin/operations/') or path.startswith('/api/v1/admin/captures/') and scope['method']!='GET' else apps[2] if path.startswith('/api/v1/admin/') else apps[3] if path.startswith('/api/v1/operations/') else apps[1]
        async def deliver(message):
            if store.mode=='drop_response' and scope['method']=='PUT' and message['type']=='http.response.body':
                raise ConnectionResetError('synthetic_post_commit_response_interruption')
            await send(message)
        await child(scope,receive,deliver)
    sock=socket.socket();sock.bind(('127.0.0.1',0));sock.listen(128)
    server=base.uvicorn.Server(base.uvicorn.Config(dispatch,log_level='warning',lifespan='on',timeout_graceful_shutdown=5))
    async def bounded():await asyncio.sleep(45);server.should_exit=True
    timer=asyncio.create_task(bounded());task=asyncio.create_task(server.serve(sockets=[sock]))
    try:
        while not server.started:
            if task.done():await task
            await asyncio.sleep(.01)
        print(json.dumps(dict(origin='http://127.0.0.1:'+str(sock.getsockname()[1]),ids=dict(org=base.ORG,account=base.ACCOUNT,actor=base.ACTOR,owner=inherited.OTHER_ACCOUNT,owner_actor=inherited.OTHER_ACTOR,captures=CAPTURES[:4],question=base.QUESTION,foreign_operation=FOREIGN_OPERATION,boolean_questions=[base.ACTOR,base.CHILD,base.VERSION]))),flush=True)
        await task
    finally:timer.cancel();sock.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--proof-directory',required=True)
    asyncio.run(serve(parser.parse_args().proof_directory))
