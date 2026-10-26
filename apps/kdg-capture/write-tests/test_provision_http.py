"""Actual candidate ASGI boundary with recorded exclusive connection ownership."""
import asyncio
from contextlib import contextmanager
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import httpx
import test_provision as support
import test_edit_context_http as existing
import provision_http as boundary

recovery=boundary.recovery
write=recovery.write
URL='/api/v1/provision'
class Pool(existing.Pool):
    def __init__(self):super().__init__();self.connection=support.Connection()
    @contextmanager
    def connect(self):
        self.borrow();self.borrows+=1
        try:yield self.connection
        finally:self.releases+=1;self.release()
class HTTPAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pool=Pool();self.checks=[]
        self.upstream=lambda permission:httpx.Response(200,json=support.support.support.evidence(permission))
        async def access(request):
            self.assertEqual(self.pool.borrows,0)
            self.checks.append(request);return self.upstream(__import__('json').loads(request.content)['permission'])
        with patch.object(boundary,'create_engine',return_value=self.pool) as factory:
            self.app=boundary.create_candidate(org_id=support.ORG,questionnaire_id=support.QUESTIONNAIRE,access_url='https://access.invalid',service_key='synthetic',database_url=existing.DB_URL,transport=httpx.MockTransport(access))
            self.engine_options=factory.call_args.kwargs
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='https://kdg.invalid')
    async def asyncTearDown(self):await self.client.aclose()
    async def get(self,url=URL,**kwargs):
        kwargs.setdefault('headers',{'Authorization':'Bearer synthetic'})
        result=await self.client.request('GET',url,**kwargs)
        self.assertEqual(result.headers['cache-control'],'private, no-store');return result
    async def test_exact_current_setup_after_commit_and_release(self):
        result=await self.get();self.assertEqual(result.status_code,200)
        self.assertEqual(result.json()['children'][0]['child_id'],support.CHILD)
        self.assertEqual(result.json()['questionnaire']['definition'],support.support.DEFINITION)
        self.assertEqual((len(self.checks),self.pool.borrows,self.pool.releases),(4,1,1))
        self.assertEqual(self.pool.connection.calls[-1][0],'COMMIT')
    async def test_selector_body_and_duplicate_auth_refused_before_access(self):
        for url,kwargs,status in ((URL+'?org_id=x',{},422),(URL+'?x=1&x=2',{},422),(URL,{'content':b'x'},422),(URL,{'headers':[('Authorization','Bearer a'),('Authorization','Bearer b')]},401),(URL,{'headers':{}},401),(URL,{'headers':{'Authorization':'Bearer a!b'}},401)):
            response=await self.get(url,**kwargs);self.assertEqual(response.status_code,status)
        self.assertEqual((self.checks,self.pool.borrows),([],0))
    async def test_edit_denial_is_honest_success_and_entry_denial_blocks_checkout(self):
        self.upstream=lambda p:httpx.Response(403,json={'detail':{'code':'access_denied'}}) if p==recovery.EDIT else httpx.Response(200,json=support.support.support.evidence(p))
        result=await self.get();self.assertEqual(result.status_code,200);self.assertIsNone(result.json()['edit_observation'])
        self.pool.borrows=0
        self.upstream=lambda p:httpx.Response(403,json={'detail':{'code':'access_denied'}})
        result=await self.get();self.assertEqual(result.status_code,403);self.assertEqual(self.pool.borrows,0)
    async def test_commit_and_release_failure_cannot_publish_success(self):
        from sqlalchemy.exc import SQLAlchemyError
        for phase in ('commit','release'):
            self.pool=Pool();self.app.state.recovery_engine=self.pool
            if phase=='commit':self.pool.connection.fail_commit=True
            else:
                def fail():raise SQLAlchemyError('private-canary')
                self.pool.release=fail
            result=await self.get()
            self.assertEqual((result.status_code,result.json()['error_id']),(503,'provision_unavailable'))
            self.assertEqual(self.pool.releases,1);self.assertNotIn('canary',result.text)
    async def test_release_expiry_and_serialization_expiry_in_original_budget(self):
        for phase in ('release','serialize'):
            self.pool=Pool();self.app.state.recovery_engine=self.pool;now=100.;count=0
            def expire():
                nonlocal now
                now=111.
            original=recovery.Provision.model_dump_json
            def serialize(value,*args,**kwargs):
                nonlocal count
                count+=1;body=original(value,*args,**kwargs)
                if count==2:expire()
                return body
            if phase=='release':self.pool.release=expire
            scope=patch.object(recovery.Provision,'model_dump_json',serialize) if phase=='serialize' else __import__('contextlib').nullcontext()
            with scope,patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):result=await self.get()
            self.assertEqual((result.status_code,result.json()['error_id']),(503,'execution_timeout'))
            self.assertEqual(self.pool.releases,1)
    async def test_checkout_staleness_does_not_renew_any_observation(self):
        now=100.
        def stale():
            nonlocal now
            now+=2
        self.pool.borrow=stale
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):result=await self.get()
        self.assertEqual(result.json()['error_id'],'authorization_observation_expired');self.assertEqual(self.pool.connection.calls,[])
    async def test_engine_is_lazy_write_capable_bounded_and_candidate_unmounted(self):
        self.assertEqual(self.pool.borrows,0)
        self.assertEqual((self.engine_options['pool_timeout'],self.engine_options['max_overflow']),(.25,0))
        self.assertNotIn('default_transaction_read_only=on',self.engine_options['connect_args']['options'])
        self.assertFalse(hasattr(boundary,'app'))
        import main
        self.assertNotIn(URL,main.app.openapi()['paths'])
    async def test_routing_errors_private(self):
        for method,url,status in (('POST',URL,405),('GET',URL+'/',404),('GET','/missing',404)):
            result=await self.client.request(method,url)
            self.assertEqual(result.status_code,status);self.assertEqual(result.headers['cache-control'],'private, no-store')
    async def test_cancellation_keeps_checkout_sql_and_release_owned_until_worker_drains(self):
        import threading
        for phase in ('borrow','sql','release'):
            self.pool=Pool();self.app.state.recovery_engine=self.pool
            started,release=threading.Event(),threading.Event()
            def pending():started.set();release.wait(2)
            if phase=='sql':
                original=self.pool.connection.execute
                def execute(sql,p):
                    if str(sql)==recovery.VERSION:pending()
                    return original(sql,p)
                self.pool.connection.execute=execute
            else:setattr(self.pool,phase,pending)
            task=asyncio.create_task(self.get())
            try:
                for _ in range(200):
                    if started.is_set():break
                    await asyncio.sleep(.001)
                self.assertTrue(started.is_set(),phase)
                task.cancel();await asyncio.sleep(.01);task.cancel();await asyncio.sleep(.01)
                self.assertFalse(task.done(),phase)
            finally:
                release.set()
                with self.assertRaises(asyncio.CancelledError):await task
            self.assertEqual(self.pool.releases,1,phase)
    async def test_expiry_keeps_worker_owned_until_each_phase_drains(self):
        import threading
        for phase in ('borrow','sql','release'):
            self.pool=Pool();self.app.state.recovery_engine=self.pool;now=100.
            started,release=threading.Event(),threading.Event()
            def pending():started.set();release.wait(2)
            if phase=='sql':
                original=self.pool.connection.execute
                def execute(sql,p):
                    if str(sql)==recovery.VERSION:pending()
                    return original(sql,p)
                self.pool.connection.execute=execute
            else:setattr(self.pool,phase,pending)
            with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):
                task=asyncio.create_task(self.get())
                try:
                    for _ in range(200):
                        if started.is_set():break
                        await asyncio.sleep(.001)
                    self.assertTrue(started.is_set(),phase)
                    now=111.;await asyncio.sleep(.02);self.assertFalse(task.done(),phase)
                finally:
                    release.set();result=await task
                self.assertEqual((result.status_code,result.json()['error_id']),(503,'execution_timeout'))
                self.assertEqual(self.pool.releases,1,phase)
    async def test_stream_body_deadline_precedes_authorization_and_checkout(self):
        original=write.Budget
        def short():
            budget=original();budget.deadline=budget.started_at+.01;return budget
        async def slow():
            await asyncio.sleep(.03);yield b''
        with patch.object(write,'Budget',side_effect=short):result=await self.get(content=slow())
        self.assertEqual((result.status_code,result.json()['error_id']),(503,'execution_timeout'))
        self.assertEqual((self.checks,self.pool.borrows),([],0))
    async def test_immediate_empty_asgi_messages_check_original_budget_without_timer_yield(self):
        now=100.;received=0;sent=[]
        async def receive():
            nonlocal now,received
            received+=1
            now=100.+received*6
            return {'type':'http.request','body':b'','more_body':received<4}
        async def send(message):sent.append(message)
        scope={'type':'http','asgi':{'version':'3.0'},'http_version':'1.1','method':'GET','scheme':'https','path':URL,'raw_path':URL.encode(),'query_string':b'','headers':[(b'authorization',b'Bearer synthetic')],'server':('kdg.invalid',443),'client':('127.0.0.1',1234),'root_path':''}
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):
            await self.app(scope,receive,send)
        start=next(message for message in sent if message['type']=='http.response.start')
        self.assertEqual(start['status'],503)
        self.assertEqual(received,2)
        self.assertEqual((self.checks,self.pool.borrows),([],0))
