"""Owned loopback-only administrator-read host; storage/Access are synthetic.

No SQL is executed and no native privileges, driver rollback or live account authority
is established. Existing fixture source stays unchanged.
"""
import argparse
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
import copy
from datetime import date, datetime, timezone
import importlib.util
import json
from pathlib import Path
import socket

HERE=Path(__file__).resolve()
spec=importlib.util.spec_from_file_location('kdg_admin_base_fixture',HERE.with_name('persistence-http-fixture.py'))
base=importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
import admin_read
import admin_http

OTHER_ACCOUNT,OTHER_ACTOR,FOREIGN_ORG=[f'{n:08x}-bbbb-4bbb-8bbb-{n:012x}' for n in range(31,34)]
CAPTURES=[f'{n:08x}-cccc-4ccc-8ccc-{n:012x}' for n in range(101,106)]
OriginalConnection=base.Connection

def snapshot(key,capture):
    return dict(capture_id=key,org_id=capture['org'],owner_account_id=capture['account'],
        owner_actor_id=capture['owner_actor'],child_id=capture['child'],child_label='Synthetic child',
        questionnaire_id=capture['questionnaire'],questionnaire_version_id=capture['version'],
        questionnaire_version=capture['display_version'],definition=copy.deepcopy(capture['definition']),
        revision=capture['revision'],observation_date=date.fromisoformat(capture['date']),
        answers=copy.deepcopy(capture['answers']),captured_at=capture['captured_at'],
        created_by=capture['created_by'],created_at=datetime.fromisoformat(capture['created_at']),
        updated_by=capture['updated_by'],updated_at=datetime.fromisoformat(capture['updated_at']))

class Connection(OriginalConnection):
    def execute(self,statement,parameters):
        sql=str(statement)
        if "set_config('app.mode'" in sql:
            self.store.contexts.append({key:parameters[key] for key in ('org','account','actor','mode')})
        if sql==admin_read.DETAIL:
            self.store.admin_queries+=1
            if self.store.mode=='fail_sql':raise base.SQLAlchemyError('synthetic-private-sql')
            value=self.captures.get(parameters['capture'])
            row=snapshot(parameters['capture'],value) if value and value['org']==parameters['org'] else None
            if row and self.store.mode=='invalid_detail':row['answers']={}
            return base.Rows(row)
        if sql==admin_read.HISTORY:
            self.store.admin_queries+=1
            if self.store.mode=='fail_sql':raise base.SQLAlchemyError('synthetic-private-sql')
            rows=[]
            for key,value in self.captures.items():
                position=(datetime.fromisoformat(value['created_at']),key)
                if value['org']!=parameters['org'] or not parameters['from_date']<=date.fromisoformat(value['date'])<=parameters['to_date']:continue
                if parameters['last_id'] is not None and position>=(parameters['last_created_at'],parameters['last_id']):continue
                row=snapshot(key,value)
                if self.store.mode=='invalid_detail':row['answers']={}
                rows.append((position,row))
            rows.sort(key=lambda item:item[0],reverse=True)
            return base.Rows([row for _,row in rows[:parameters['row_limit']]])
        return super().execute(statement,parameters)
base.Connection=Connection

async def serve(directory):
    directory=Path(directory)
    store=base.Store();store.contexts=[];store.admin_queries=0
    definition=base.initial_definition([base.QUESTION,base.ACTOR,base.CHILD,base.VERSION]).model_dump()
    definition['questions'][0]['label']='Original retained question'
    for index,key in enumerate(CAPTURES):
        other=index in (1,2)
        actor=OTHER_ACTOR if other else base.ACTOR
        store.captures[key]=dict(org=FOREIGN_ORG if index==3 else base.ORG,
            account=OTHER_ACCOUNT if other else base.ACCOUNT,owner_actor=actor,
            child=base.CHILD,version=base.VERSION,questionnaire=base.QUESTIONNAIRE,
            display_version=1,definition=copy.deepcopy(definition),revision=index+1,
            date='2026-09-30' if index==4 else '2026-10-25',
            answers={base.QUESTION:{'value':index+1},**{q:{'value':False} for q in (base.ACTOR,base.CHILD,base.VERSION)}},
            captured_at='2026-10-25T10:00:00Z',created_by=actor,
            created_at='2026-10-26T00:00:00Z',updated_by=base.ACTOR,
            updated_at='2026-10-26T01:00:00Z')
    original=copy.deepcopy(store.captures)
    async def access(request):
        body=json.loads(request.content);permission=body['permission'];store.checks.append(permission)
        mode=store.mode
        if mode=='outage':return base.httpx.Response(503,json={'detail':{'code':'unavailable'}})
        if mode=='expired':return base.httpx.Response(401,json={'detail':{'code':'authentication_required'}})
        if mode=='deny' and permission==admin_read.PERMISSION:return base.httpx.Response(403,json={'detail':{'code':'access_denied'}})
        account=OTHER_ACCOUNT if mode=='other_account' else base.ACCOUNT
        scope=dict(kind='organization',org_id=base.ORG) if permission==admin_read.PERMISSION else dict(kind='own_account',account_id=account)
        evidence=dict(account_id=account,actor_id=OTHER_ACTOR if mode=='other_account' else base.ACTOR,membership_id='7',
            authorization_scope=dict(kind='organization',org_id=base.ORG),resource_scope=scope,
            permission=permission,decision_id=base.UNKNOWN,checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
        if mode=='actor_missing':evidence.pop('actor_id')
        if mode=='wrong_scope':evidence['resource_scope']=dict(kind='own_account',account_id=account)
        if mode=='wrong_permission':evidence['permission']='kdg_capture.capture.read.own'
        if mode=='wrong_org':evidence['resource_scope']=dict(kind='organization',org_id=FOREIGN_ORG)
        return base.httpx.Response(200,json=evidence)
    args=dict(org_id=base.ORG,access_url='https://access.invalid',service_key='synthetic',transport=base.httpx.MockTransport(access))
    # Construct only inert candidate collaborators inside this explicitly invoked host.
    admin=admin_http._create_app(admin_read.AdminReadHandler(**args),store,base.ORG)
    own=base.read_http._create_app(base.read.ReadHandler(**args),store,base.ORG)
    own_history=base.history_http._create_app(base.history_read.HistoryHandler(**args),store,base.ORG)
    def state():
        return dict(acquired=store.acquired,released=store.released,disposed=store.disposed,
            commits=store.commits,checks=store.checks,contexts=store.contexts,admin_queries=store.admin_queries,
            source_records_unchanged=store.captures==original,outcomes=len(store.outcomes),history=len(store.history))
    @asynccontextmanager
    async def lifespan(app):
        async with AsyncExitStack() as stack:
            for child in (admin,own,own_history):await stack.enter_async_context(child.router.lifespan_context(child))
            yield
        (directory/'storage-final.json').write_text(json.dumps(state(),sort_keys=True,indent=2)+'\n')
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
                message=await receive();mode=json.loads(message.get('body',b'{}')).get('mode')
                if mode not in ('all','deny','outage','expired','actor_missing','wrong_scope','wrong_permission','wrong_org','other_account','fail_sql','fail_release','invalid_detail'):
                    return await base.JSONResponse({},status_code=422)(scope,receive,send)
                store.mode=mode
            return await base.JSONResponse(state())(scope,receive,send)
        child=admin if path.startswith('/api/v1/admin/') else own_history if path=='/api/v1/captures' else own
        await child(scope,receive,send)
    sock=socket.socket();sock.bind(('127.0.0.1',0));sock.listen(128)
    server=base.uvicorn.Server(base.uvicorn.Config(dispatch,log_level='warning',lifespan='on',timeout_graceful_shutdown=5))
    async def bounded():
        await asyncio.sleep(45);server.should_exit=True
    timer=asyncio.create_task(bounded());task=asyncio.create_task(server.serve(sockets=[sock]))
    try:
        while not server.started:
            if task.done():await task
            await asyncio.sleep(.01)
        print(json.dumps(dict(origin='http://127.0.0.1:'+str(sock.getsockname()[1]),ids=dict(org=base.ORG,account=base.ACCOUNT,actor=base.ACTOR,other_account=OTHER_ACCOUNT,other_actor=OTHER_ACTOR,foreign_org=FOREIGN_ORG,captures=CAPTURES,question=base.QUESTION))),flush=True)
        await task
    finally:timer.cancel();sock.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--proof-directory',required=True)
    asyncio.run(serve(parser.parse_args().proof_directory))
