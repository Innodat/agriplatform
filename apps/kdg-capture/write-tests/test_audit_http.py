"""Synthetic audit acceptance and failure fences; no native database or authority."""
from pathlib import Path
import sys

sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'write-candidate'),str(Path(__file__).resolve().parents[1]/'api')]

from contextlib import contextmanager
import copy
from datetime import datetime, timezone, timedelta
from uuid import UUID
import unittest
from unittest.mock import patch
import httpx
import test_admin_http as wire
import audit_read as audit
import audit_http as boundary

PATH='/api/v1/admin/captures/'+wire.support.CAPTURE+'/events'

class Rows:
    def __init__(self,rows):self.rows=rows
    def mappings(self):return self
    def all(self):return self.rows

class Connection(wire.Connection):
    def __init__(self):
        super().__init__()
        self.header={key:copy.deepcopy(self.detail[key]) for key in audit.HEADER if key!='current_revision'}
        self.header['current_revision']=5
        self.header['updated_by']=UUID(wire.FOREIGN)
        now=self.header['created_at']
        self.events=[dict(event_revision=n,command_type='capture.create' if n==1 else 'capture.edit',executor_actor_id=UUID(wire.support.ACTOR if n==1 else wire.FOREIGN),initiator_actor_id=None if n==1 else UUID(wire.support.ACTOR),recorded_at=now+timedelta(seconds=10-n)) for n in range(1,6)]
        self.missing=False;self.transform=lambda rows:rows
    def execute(self,sql,parameters):
        if str(sql)==audit.EVENTS:
            self.calls.append((str(sql),parameters));self.selected.append(parameters)
            if self.fail_execute:
                from sqlalchemy.exc import OperationalError
                raise OperationalError('private-sql',{},Exception('private-driver'))
            events=sorted([e for e in self.events if parameters['last_revision'] is None or e['event_revision']<parameters['last_revision']],key=lambda e:e['event_revision'],reverse=True)[:parameters['row_limit']]
            if self.missing:rows=[]
            else:rows=[{**self.header,**e} for e in events] or [{**self.header,**dict.fromkeys(audit.EVENT_FIELDS)}]
            return Rows(self.transform(copy.deepcopy(rows)))
        return super().execute(sql,parameters)

class Pool(wire.Pool):
    def __init__(self):super().__init__();self.connection=Connection()

class AuditAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pool=Pool();self.checks=[];self.upstream=lambda:httpx.Response(200,json=wire.evidence())
        async def access(request):
            self.assertFalse(self.pool.connection.in_transaction());self.checks.append(request);return self.upstream()
        self.access=access
        with patch.object(boundary,'create_engine',return_value=self.pool):self.app=self.make_app(access)
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='https://kdg.invalid')
    def make_app(self,access):
        return boundary.create_candidate(org_id=wire.support.ORG,access_url='https://access.invalid',service_key='synthetic',database_url=wire.history_support.DB_URL,transport=httpx.MockTransport(access))
    async def asyncTearDown(self):await self.client.aclose()
    async def get(self,url=PATH,**kwargs):
        # Reuse existing generic failure-fence tests with their URLs mapped to
        # this single metadata route; their collaboration controls are unchanged.
        if url in (wire.DETAIL,wire.HISTORY):url=PATH
        kwargs.setdefault('headers',{'Authorization':'Bearer synthetic'})
        result=await self.client.request('GET',url,**kwargs)
        self.assertEqual(result.headers['cache-control'],'private, no-store')
        return result
    async def test_cross_owner_metadata_route(self):
        response=await self.get();self.assertEqual(response.status_code,200)
        page=response.json()
        self.assertEqual(page['owner_account_id'],wire.FOREIGN)
        self.assertEqual(page['account_id'],wire.support.ACCOUNT)
        self.assertEqual(set(page),set(audit.AuditPage.model_fields))
        self.assertEqual([e['revision'] for e in page['events']],['5','4','3','2','1'])
        self.assertEqual(set(page['events'][0]),set(audit.AuditEvent.model_fields))
        self.assertNotEqual(page['updated_at'],page['events'][0]['recorded_at'])
        self.assertEqual(page['events'][0]['executor_actor_id'],wire.FOREIGN)
        self.assertEqual(page['events'][0]['initiator_actor_id'],wire.support.ACTOR)
        self.assertEqual(page['events'][-1]['executor_actor_id'],wire.support.ACTOR)
        self.assertIsNone(page['events'][-1]['initiator_actor_id'])
        self.assertEqual((self.pool.borrows,self.pool.releases,len(self.checks)),(1,1,1))
    async def test_numeric_tied_nonmonotonic_pages_refresh_and_empty_continuation(self):
        seen=[];url=PATH+'?limit=2'
        for count in (2,2,1):
            response=await self.get(url);self.assertEqual(response.status_code,200)
            page=response.json();self.assertEqual(len(page['events']),count)
            seen.extend(e['revision'] for e in page['events'])
            url=PATH+'?limit=2&cursor='+page['next_cursor'] if page['next_cursor'] else PATH
        self.assertEqual(seen,['5','4','3','2','1']);self.assertEqual(len(self.checks),3)
        first=(await self.get(PATH+'?limit=2')).json();cursor=first['next_cursor']
        self.pool.connection.header['current_revision']=6
        self.pool.connection.events.append({**self.pool.connection.events[-1],'event_revision':6})
        refreshed=(await self.get()).json();self.assertEqual(refreshed['events'][0]['revision'],'6')
        continued=(await self.get(PATH+'?limit=2&cursor='+cursor)).json()
        self.assertEqual(continued['current_revision'],'6');self.assertEqual(continued['events'][0]['revision'],'3')
        query=audit.Query(capture_id=wire.support.CAPTURE,limit=2)
        context=audit.write.VerifiedContext(wire.support.ORG,wire.support.ACCOUNT,wire.support.ACTOR,'all_read',100)
        cursor=audit.continuation(query,context,audit.AuditEvent(revision='1',command_type='capture.create',executor_actor_id=wire.support.ACTOR,initiator_actor_id=None,recorded_at='2026-10-26T00:00:00Z'))
        response=await self.get(PATH+'?limit=2&cursor='+cursor)
        self.assertEqual(response.status_code,200);self.assertEqual(response.json()['events'],[])
    async def test_invalid_query_path_body_auth_before_authority(self):
        for suffix in ('?owner_account_id='+wire.FOREIGN,'?from_date=2026-10-01','?limit=2&limit=2','?cursor=bad','?limit=0','?limit=101','?limit=01','?limit=true','?limit=1.0','?selector=all','?'+('x'*8193)):
            self.assertEqual((await self.get(PATH+suffix)).status_code,422)
        self.assertEqual((await self.get(PATH.replace(wire.support.CAPTURE,'bad'))).status_code,422)
        self.assertEqual((await self.get(content=b'private')).status_code,422)
        for headers in ({},{'Authorization':'Basic a'},[('Authorization','Bearer a'),('Authorization','Bearer b')],{'Authorization':'Bearer a,b'}):
            response=await self.get(headers=headers);self.assertEqual(response.status_code,401)
        self.assertEqual((len(self.checks),self.pool.borrows),(0,0))
    async def test_authority_scope_required_and_continuation_revocation(self):
        first=(await self.get(PATH+'?limit=2')).json()
        self.upstream=lambda:httpx.Response(403,json={'detail':{'code':'access_denied'}})
        response=await self.get(PATH+'?limit=2&cursor='+first['next_cursor']);self.assertEqual(response.status_code,403)
        self.assertEqual(self.pool.borrows,1)
        original=wire.evidence()
        changes=[{field:None} for field in original]+[{'resource_scope':dict(kind='organization',org_id=wire.FOREIGN)},{'permission':'kdg_capture.capture.read.own'},{'authorization_scope':dict(kind='organization',org_id=wire.FOREIGN)}]
        for change in changes:
            self.upstream=lambda:httpx.Response(200,json={**original,**change})
            response=await self.get();self.assertEqual(response.status_code,503,change)
        self.assertEqual(self.pool.borrows,1)
    async def test_cursor_binding_current_caller_capture_org_limit_and_mode(self):
        first=(await self.get(PATH+'?limit=2')).json();value=audit.decode_cursor(first['next_cursor']).model_dump()
        for change in ({'account_id':wire.FOREIGN},{'org_id':wire.FOREIGN},{'capture_id':wire.FOREIGN},{'limit':3},{'permission':'kdg_capture.capture.read.own'}):
            cursor=audit.admin.history._encode({**value,**change})
            self.assertEqual((await self.get(PATH+'?limit=2&cursor='+cursor)).status_code,422)
        self.assertEqual(self.pool.borrows,1)
    async def test_missing_foreign_and_malformed_metadata_fail_privately(self):
        original=copy.deepcopy(self.pool.connection.header)
        self.pool.connection.missing=True;self.assertEqual((await self.get()).status_code,404);self.pool.connection.missing=False
        for key in ('org_id','capture_id'):
            self.pool.connection.header={**original,key:UUID(wire.FOREIGN)}
            self.assertEqual((await self.get()).status_code,404)
        self.pool.connection.header=original
        for key,value in (('event_revision',True),('command_type','capture.delete'),('executor_actor_id',None),('initiator_actor_id','bad'),('recorded_at',datetime.now()),('event_revision',0)):
            def corrupt(rows):rows[-1][key]=value;return rows
            self.pool.connection.transform=corrupt
            self.assertEqual((await self.get()).status_code,503,(key,value))
        self.pool.connection.transform=lambda rows:[rows[0],rows[0]]
        self.assertEqual((await self.get()).status_code,503)
        self.pool.connection.transform=lambda rows:rows;self.pool.connection.events=[]
        self.assertEqual((await self.get()).status_code,503)
    async def test_historical_read_without_eligibility(self):
        self.pool.connection.child={'active':False};self.pool.connection.assignment=None;self.pool.connection.eligibility=None
        self.assertEqual((await self.get()).status_code,200)
    async def test_inert_private_routing_and_readonly_engine(self):
        for method,path,status in (('POST',PATH,405),('GET',PATH+'/',404),('GET','/api/v1/captures',404),('GET',wire.DETAIL,404)):
            response=await self.client.request(method,path);self.assertEqual(response.status_code,status)
            self.assertEqual(response.headers['cache-control'],'private, no-store')
        self.assertFalse(hasattr(boundary,'app'));self.assertEqual(self.pool.borrows,0)
        with patch.object(boundary,'create_engine',return_value=self.pool) as factory:boundary._engine(wire.history_support.DB_URL)
        options=factory.call_args.kwargs
        self.assertIn('default_transaction_read_only=on',options['connect_args']['options'])
        async with self.app.router.lifespan_context(self.app):pass
        self.assertEqual(self.pool.disposed,1)
    async def test_checkout_freshness_and_release_fences_have_no_late_success(self):
        from types import SimpleNamespace
        import audit_read as admin
        for phase,expected in (('borrow','authorization_observation_expired'),('release','execution_timeout')):
            for url in (PATH,):
                self.pool=Pool();self.app.state.recovery_engine=self.pool;now=100.0
                def delayed():
                    nonlocal now
                    now+=2 if phase=='borrow' else 11
                setattr(self.pool,phase,delayed)
                with patch.object(admin.write,'time',SimpleNamespace(monotonic=lambda:now)):
                    result=await self.get(url)
                self.assertEqual(result.json()['error_id'],expected)
                self.assertEqual(self.pool.releases,1)
                if phase=='borrow':self.assertEqual(self.pool.connection.calls,[])
    async def test_pool_sql_commit_release_failure_and_unexpected_error_are_private(self):
        from sqlalchemy.exc import OperationalError,TimeoutError
        for url in (PATH,):
            for phase in ('borrow','sql','commit','release'):
                self.pool=Pool();self.app.state.recovery_engine=self.pool
                def failed():raise OperationalError('private-sql',{},Exception('private-driver'))
                if phase=='sql':self.pool.connection.fail_execute=True
                elif phase=='commit':self.pool.connection.fail_commit=True
                else:setattr(self.pool,phase,failed)
                result=await self.get(url)
                self.assertEqual((result.status_code,result.json()['error_id']),(503,'capture_read_unavailable'))
                self.assertNotIn('private-',result.text)
        self.pool=Pool();self.app.state.recovery_engine=self.pool
        def unexpected():raise RuntimeError('private-canary')
        self.pool.borrow=unexpected
        with self.assertLogs('service.operations',level='ERROR') as logs:result=await self.get()
        self.assertEqual(result.status_code,500);self.assertNotIn('private-canary',str(logs.output)+result.text)
    async def test_cancel_and_deadline_keep_worker_owned_through_unwind(self):
        import asyncio
        import threading
        original_budget=audit.write.Budget
        original_authorize=audit.AuditReadHandler._authorize
        async def delayed_authorize(owner,*args,**kwargs):
            # Authorization can legitimately outlast the former 60ms test budget.
            await asyncio.sleep(.08)
            return await original_authorize(owner,*args,**kwargs)
        for cancel in (False,True):
            for phase in ('borrow','sql','release'):
                self.pool=Pool();self.app.state.recovery_engine=self.pool
                started,release=threading.Event(),threading.Event();budgets=[]
                def pending():started.set();release.wait(5)
                if phase=='sql':
                    original=self.pool.connection.execute
                    def execute(sql,params):
                        if str(sql)==audit.EVENTS:pending()
                        return original(sql,params)
                    self.pool.connection.execute=execute
                else:setattr(self.pool,phase,pending)
                def controlled():
                    budget=original_budget();budgets.append(budget);return budget
                with patch.object(audit.write,'Budget',side_effect=controlled),patch.object(audit.AuditReadHandler,'_authorize',delayed_authorize):
                    task=asyncio.create_task(self.get())
                    try:
                        self.assertTrue(await asyncio.to_thread(started.wait,2),phase)
                        # Expire the original request budget only once this worker
                        # phase is reached, independently of Access/scheduling time.
                        self.assertEqual(len(budgets),1)
                        budgets[0].deadline=budgets[0].started_at-1
                        with self.assertRaisesRegex(audit.write.WriteError,'execution_timeout'):
                            budgets[0].remaining()
                        if cancel:task.cancel();await asyncio.sleep(.01);task.cancel()
                        await asyncio.sleep(.01);self.assertFalse(task.done(),phase)
                        self.assertEqual(self.pool.releases,0)
                    finally:
                        release.set()
                        if cancel:
                            with self.assertRaises(asyncio.CancelledError):await task
                        else:
                            result=await task
                            self.assertEqual(result.json()['error_id'],'execution_timeout')
                            self.assertNotIn('events',result.json())
                    self.assertEqual(self.pool.releases,1)
    async def test_access_and_stream_timeouts_before_checkout(self):
        import asyncio
        import audit_read as admin
        original=admin.write.Budget
        def short():
            budget=original();budget.deadline=budget.started_at+.02;return budget
        async def body():await asyncio.sleep(.06);yield b''
        for url in (PATH,):
            with patch.object(admin.write,'Budget',side_effect=short):result=await self.get(url,content=body())
            self.assertEqual(result.json()['error_id'],'execution_timeout')
        self.assertEqual((len(self.checks),self.pool.borrows),(0,0))
        async def delayed(request):await asyncio.sleep(.06);return httpx.Response(200,json=wire.evidence())
        with patch.object(admin.protected,'ACCESS_SECONDS',.02):
            with patch.object(boundary,'create_engine',return_value=self.pool):self.app=self.make_app(delayed)
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='https://kdg.invalid') as client:
                for url in (PATH,):
                    result=await client.get(url,headers={'Authorization':'Bearer synthetic'})
                    self.assertEqual(result.json()['error_id'],'authorization_unavailable')
                    self.assertEqual(result.headers['cache-control'],'private, no-store')
        self.assertEqual(self.pool.borrows,0)
    async def test_pending_body_and_access_cancellation_is_prompt_without_checkout(self):
        import asyncio
        for url in (PATH,):
            for phase in ('body','access'):
                started,release,unwound=asyncio.Event(),asyncio.Event(),asyncio.Event()
                async def gated_body():
                    try:
                        started.set();await release.wait();yield b''
                    finally:unwound.set()
                async def gated_access(request):
                    try:
                        started.set();await release.wait()
                        return httpx.Response(200,json=wire.evidence())
                    finally:unwound.set()
                if phase=='access':
                    with patch.object(boundary,'create_engine',return_value=self.pool):app=self.make_app(gated_access)
                else:app=self.app
                checks_before=len(self.checks)
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='https://kdg.invalid') as client:
                    options={'content':gated_body()} if phase=='body' else {}
                    task=asyncio.create_task(client.request('GET',url,headers={'Authorization':'Bearer synthetic'},**options))
                    try:
                        await asyncio.wait_for(started.wait(),.5)
                        self.assertFalse(task.done())
                        task.cancel()
                        with self.assertRaises(asyncio.CancelledError):await asyncio.wait_for(task,.5)
                        await asyncio.wait_for(unwound.wait(),.5)
                        self.assertEqual((self.pool.borrows,self.pool.releases),(0,0))
                        self.assertEqual(len(self.checks),checks_before)
                        release.set();await asyncio.sleep(0)
                        self.assertTrue(task.cancelled())
                        self.assertEqual((self.pool.borrows,self.pool.releases),(0,0))
                    finally:
                        release.set()
                        if not task.done():
                            task.cancel()
                            try:await asyncio.wait_for(task,.5)
                            except asyncio.CancelledError:pass
    async def test_final_serialization_deadline_and_failure(self):
        from types import SimpleNamespace
        original=audit.AuditPage.model_dump_json;now=100.;calls=0
        def serialized(page,*args,**kwargs):
            nonlocal now,calls
            result=original(page,*args,**kwargs);calls+=1
            if calls==2:now=111.
            return result
        with patch.object(audit.write,'time',SimpleNamespace(monotonic=lambda:now)),patch.object(audit.AuditPage,'model_dump_json',serialized):
            response=await self.get()
        self.assertEqual(response.json()['error_id'],'execution_timeout')
        with patch.object(audit.AuditPage,'model_dump_json',side_effect=ValueError('private')):response=await self.get()
        self.assertEqual(response.json()['error_id'],'capture_read_unavailable');self.assertNotIn('private',response.text)
    async def test_final_http_serialization_failure_is_private_after_connection_release(self):
        original=audit.AuditPage.model_dump_json;calls=0
        def serialized(page,*args,**kwargs):
            nonlocal calls
            calls+=1
            if calls==2:
                self.assertEqual((self.pool.borrows,self.pool.releases),(1,1))
                self.assertFalse(self.pool.connection.in_transaction())
                raise ValueError('private-final-serialization-canary')
            return original(page,*args,**kwargs)
        with patch.object(audit.AuditPage,'model_dump_json',serialized):response=await self.get()
        self.assertEqual(calls,2)
        self.assertEqual((response.status_code,response.json()['error_id']),(503,'capture_read_unavailable'))
        self.assertNotIn('private-final-serialization-canary',response.text)
        self.assertNotIn('events',response.json())
        self.assertEqual((self.pool.borrows,self.pool.releases),(1,1))
