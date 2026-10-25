"""Candidate PUT acceptance: actual authorization, transaction body and replay."""
import asyncio
from contextlib import contextmanager
import json
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import httpx
import test_capture_edit_handler as support
import edit_http as boundary

write=support.write
URL='/api/v1/captures/'+support.CAPTURE
DB_URL='postgresql+psycopg://synthetic:synthetic@127.0.0.1:55482/synthetic'

class Pool:
    def __init__(self):
        self.connection=support.Connection();self.borrows=0;self.releases=0;self.disposed=0
        self.borrow=lambda:None;self.release=lambda:None
    @contextmanager
    def connect(self):
        self.borrow();self.borrows+=1
        try:yield self.connection
        finally:self.release();self.releases+=1
    def dispose(self):self.disposed+=1

class HTTPAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pool=Pool();self.checks=[]
        self.upstream=lambda permission:httpx.Response(200,json=support.access.evidence(permission))
        async def access(request):
            self.assertEqual(self.pool.borrows,0)
            permission=json.loads(request.content)['permission'];self.checks.append(permission)
            response=self.upstream(permission)
            return await response if hasattr(response,'__await__') else response
        with patch.object(boundary,'create_engine',return_value=self.pool) as factory:
            self.app=boundary.create_candidate(org_id=support.ORG,access_url='https://access.invalid',service_key='synthetic',database_url=DB_URL,transport=httpx.MockTransport(access))
            self.engine_options=factory.call_args.kwargs
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='https://kdg.invalid')
    async def asyncTearDown(self):await self.client.aclose()
    async def put(self,url=URL,**kwargs):
        kwargs.setdefault('headers',{'Authorization':'Bearer synthetic','Content-Type':'application/json'})
        if not any(key in kwargs for key in ('content','json')):kwargs['json']=support.body.command().model_dump()
        response=await self.client.put(url,**kwargs)
        self.assertEqual(response.headers['cache-control'],'private, no-store')
        return response
    async def test_actual_fresh_committed_and_noop_receipts(self):
        for noop,revision in ((False,'5'),(True,'4')):
            self.pool.connection=support.Connection();self.pool.connection.unchanged=noop;self.pool.borrows=0
            result=await self.put()
            self.assertEqual((result.status_code,result.json()['result']['revision']),(200,revision))
            self.assertEqual(self.checks[-2:],[support.READ,support.EDIT])
            self.assertEqual(self.pool.connection.calls[-1][0],'COMMIT')
        self.assertEqual(self.pool.releases,2)
    async def test_duplicate_different_valid_target_and_invalid_domain_returns_original(self):
        self.pool.connection.existing=support.stored()
        result=await self.put('/api/v1/captures/'+support.ACTOR,json=support.body.command(answers={},expected_revision='1').model_dump())
        self.assertEqual((result.status_code,result.json()['result']),(200,dict(capture_id=support.access.STORED_CAPTURE,revision='2')))
        self.assertFalse(any(sql.startswith(('INSERT','UPDATE')) for sql,_ in self.pool.connection.calls))
    async def test_conflict_wire_is_safe_typed_metadata(self):
        result=await self.put(json=support.body.command(expected_revision='3').model_dump())
        self.assertEqual(result.status_code,409)
        self.assertEqual(result.json(),dict(error='The request could not be completed.',error_id='kdg_capture.capture_revision_conflict',current_revision='4'))
    async def test_path_body_version_bounds_and_duplicates_precede_access(self):
        invalid=[(URL,b'{}'),('/api/v1/captures/invalid',b'{}'),
            (URL,b'{"command_version":1,"command_version":1}'),(URL,b'{"command_version":2}'),
            (URL,b'x'*131073),(URL,b'\xff')]
        for url,raw in invalid:
            result=await self.put(url,content=raw)
            self.assertEqual(result.status_code,422)
        self.assertEqual((self.checks,self.pool.borrows),([],0))
    async def test_query_and_bearer_ambiguity_never_checks_out(self):
        for url,headers in ((URL+'?x=1',{'Authorization':'Bearer synthetic'}),
            (URL,{}),(URL,[('Authorization','Bearer a'),('authorization','Bearer b')]),
            (URL,{'Authorization':'Bearer a,b'}),(URL,{'Authorization':'Basic secret'})):
            result=await self.put(url,headers=headers)
            self.assertEqual(result.status_code,422 if '?' in url else 401)
            if result.status_code==401:self.assertEqual(result.headers['www-authenticate'],'Bearer')
        self.assertEqual((self.checks,self.pool.borrows),([],0))
    async def test_json_media_type_is_required_single_and_allows_parameters(self):
        for media in ([],['text/plain'],['application/json','application/json'],
            ['application/json','text/plain'],['application/json, text/plain']):
            headers=[('Authorization','Bearer synthetic')]+[('Content-Type',value) for value in media]
            result=await self.put(headers=headers,content=json.dumps(support.body.command().model_dump()))
            self.assertEqual((result.status_code,result.json()['error_id']),(422,'validation_failed'))
        self.assertEqual((self.checks,self.pool.borrows),([],0))
        result=await self.put(headers={'Authorization':'Bearer synthetic',
            'Content-Type':'Application/JSON; charset=utf-8'},content=json.dumps(support.body.command().model_dump()))
        self.assertEqual(result.status_code,200)
    async def test_cumulative_chunked_utf8_byte_ceiling_allows_exact_limit_only(self):
        from uuid import UUID
        self.pool.connection.existing=support.stored()
        command=support.body.command().model_dump()
        command['answers']={str(UUID(int=i+1)):{'value':'é'*1250} for i in range(50)}
        raw=json.dumps(command,ensure_ascii=False,separators=(',',':')).encode('utf-8')
        padding=131072-len(raw)
        self.assertGreater(padding,0)
        last=next(reversed(command['answers']))
        command['answers'][last]['value']+='a'*padding
        self.assertLessEqual(len(command['answers'][last]['value']),5000)
        raw=json.dumps(command,ensure_ascii=False,separators=(',',':')).encode('utf-8')
        self.assertEqual(len(raw),131072)
        async def chunks(value):
            for offset in range(0,len(value),1023):yield value[offset:offset+1023]
        result=await self.put(content=chunks(raw))
        self.assertEqual((result.status_code,result.json()['result']['revision']),(200,'2'))
        self.checks=[];self.pool.borrows=0
        result=await self.put(content=chunks(raw+b' '))
        self.assertEqual((result.status_code,result.json()['error_id']),(422,'validation_failed'))
        self.assertEqual((self.checks,self.pool.borrows),([],0))
    async def test_denial_setup_outage_and_bad_scope_prevent_acquisition(self):
        cases=[(403,{'detail':{'code':'access_denied'}},403,'access_denied'),
            (409,{'detail':{'code':'identity.actor_setup_required'}},409,'identity.actor_setup_required'),
            (500,{'private':'secret'},503,'authorization_unavailable'),
            (200,dict(support.access.evidence(support.EDIT),membership_id='8'),503,'authorization_unavailable')]
        for status,data,expected,code in cases:
            self.upstream=lambda permission:httpx.Response(status,json=data) if permission==support.EDIT else httpx.Response(200,json=support.access.evidence(permission))
            result=await self.put()
            self.assertEqual((result.status_code,result.json()['error_id']),(expected,code))
            self.assertEqual(self.pool.borrows,0)
    async def test_missing_target_and_failed_replay_never_disclose_receipt(self):
        self.pool.connection.capture=None
        result=await self.put();self.assertEqual((result.status_code,result.json()['error_id']),(404,'capture_unavailable'))
        self.pool.borrows=0;self.pool.connection.existing=support.stored();self.pool.connection.target=None
        result=await self.put();self.assertEqual((result.status_code,result.json()['error_id']),(503,'operation_verification_unavailable'))
    async def test_write_engine_is_lazy_bounded_and_not_readonly(self):
        self.assertEqual(self.pool.borrows,0)
        self.assertEqual(self.engine_options['pool_timeout'],.25)
        self.assertEqual(self.engine_options['max_overflow'],0)
        self.assertEqual(self.engine_options['connect_args']['connect_timeout'],3)
        self.assertNotIn('default_transaction_read_only=on',self.engine_options['connect_args']['options'])
        self.assertFalse(self.engine_options['pool_pre_ping'])
        for url in (DB_URL.replace('127.0.0.1','localhost'),DB_URL+'?options=unsafe',DB_URL.replace('postgresql+psycopg','sqlite')):
            with self.assertRaisesRegex(RuntimeError,'kdg_edit_database_configuration_invalid'):boundary._engine(url)
    async def test_slow_acquisition_does_not_refresh_evidence(self):
        now=100.0
        def slow():
            nonlocal now
            now+=2
        self.pool.borrow=slow
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):result=await self.put()
        self.assertEqual(result.json()['error_id'],'authorization_observation_expired')
        self.assertEqual(self.pool.connection.calls,[]);self.assertEqual(self.pool.releases,1)
    async def test_sql_commit_release_and_acquisition_errors_do_not_ack(self):
        from sqlalchemy.exc import OperationalError,TimeoutError
        for phase in ('sql','commit','release','borrow'):
            self.pool.connection=support.Connection();self.pool.borrows=0;self.pool.release=lambda:None;self.pool.borrow=lambda:None
            def fail():raise OperationalError('PRIVATE',{},Exception('PRIVATE'))
            if phase=='sql':self.pool.connection.failure='UPDATE kdg_capture.capture'
            if phase=='commit':self.pool.connection.fail_commit=True
            if phase=='release':self.pool.release=fail
            if phase=='borrow':self.pool.borrow=lambda:(_ for _ in ()).throw(TimeoutError('PRIVATE'))
            result=await self.put()
            self.assertEqual((result.status_code,result.json()['error_id']),(500,'internal_error'))
            self.assertNotIn('PRIVATE',result.text)
    async def test_body_stream_deadline_and_continuous_empty_chunks(self):
        original=write.Budget
        def short():
            budget=original();budget.deadline=budget.started_at+.02;return budget
        async def slow():
            await asyncio.sleep(.05);yield b''
        with patch.object(write,'Budget',side_effect=short):result=await self.put(content=slow())
        self.assertEqual((result.status_code,result.json()['error_id']),(503,'execution_timeout'))
        self.assertEqual((self.checks,self.pool.borrows),([],0))
        now=100.0
        async def empties():
            nonlocal now
            for _ in range(12):now+=1;yield b''
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):result=await self.put(content=empties())
        self.assertEqual(result.json()['error_id'],'execution_timeout');self.assertEqual(self.pool.borrows,0)
    async def test_total_access_window_bounds_both_checks(self):
        async def slow(permission):
            await asyncio.sleep(.04)
            return httpx.Response(200,json=support.access.evidence(permission))
        self.upstream=slow
        with patch.object(support.handler.protected,'ACCESS_SECONDS',.06):result=await self.put()
        self.assertEqual(result.json()['error_id'],'authorization_unavailable');self.assertEqual(self.pool.borrows,0)
    async def test_direct_repeated_cancellation_holds_lease_until_worker_unwind(self):
        for phase in ('borrow','sql','commit','release'):
            self.pool=Pool();self.app.state.edit_engine=self.pool
            entered,finish=threading.Event(),threading.Event()
            def pending():entered.set();finish.wait(2)
            if phase=='sql':
                execute=self.pool.connection.execute
                def blocked(sql,args):
                    if str(sql).startswith('UPDATE kdg_capture.capture'):pending()
                    return execute(sql,args)
                self.pool.connection.execute=blocked
            elif phase=='commit':self.pool.connection.on_commit=pending
            else:setattr(self.pool,phase,pending)
            task=asyncio.create_task(self.put())
            try:
                for _ in range(200):
                    if entered.is_set():break
                    await asyncio.sleep(.001)
                self.assertTrue(entered.is_set(),phase)
                task.cancel();await asyncio.sleep(.01);task.cancel();await asyncio.sleep(.01)
                self.assertFalse(task.done(),phase)
                if phase!='release':self.assertEqual(self.pool.releases,0)
            finally:
                finish.set()
                with self.assertRaises(asyncio.CancelledError):await task
            self.assertEqual(self.pool.releases,1)
    async def test_expiry_and_release_completion_remain_in_original_budget(self):
        now=100.0
        def late():
            nonlocal now
            now=111.0
        self.pool.release=late
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):result=await self.put()
        self.assertEqual(result.json()['error_id'],'execution_timeout')
    async def test_expired_workers_hold_exclusive_lease_until_unwind(self):
        original_budget=write.Budget
        def short():
            budget=original_budget();budget.deadline=budget.started_at+.04;return budget
        for phase in ('borrow','sql','release'):
            self.pool=Pool();self.app.state.edit_engine=self.pool
            entered,finish=threading.Event(),threading.Event()
            def pending():entered.set();finish.wait(2)
            if phase=='sql':
                execute=self.pool.connection.execute
                def blocked(sql,args):
                    if str(sql).startswith('UPDATE kdg_capture.capture'):pending()
                    return execute(sql,args)
                self.pool.connection.execute=blocked
            else:setattr(self.pool,phase,pending)
            with patch.object(write,'Budget',side_effect=short):
                task=asyncio.create_task(self.put())
                try:
                    for _ in range(200):
                        if entered.is_set():break
                        await asyncio.sleep(.001)
                    self.assertTrue(entered.is_set(),phase)
                    await asyncio.sleep(.06)
                    self.assertFalse(task.done(),phase)
                finally:
                    finish.set();result=await task
                self.assertEqual((result.status_code,result.json()['error_id']),(503,'execution_timeout'))
                self.assertEqual(self.pool.releases,1)
    async def test_access_cancellation_never_acquires_connection(self):
        entered=asyncio.Event()
        async def wait(permission):
            entered.set();await asyncio.Event().wait()
        self.upstream=wait
        task=asyncio.create_task(self.put())
        await entered.wait();task.cancel()
        with self.assertRaises(asyncio.CancelledError):await task
        self.assertEqual(self.pool.borrows,0)
    async def test_busy_lock_wire_mapping(self):
        from sqlalchemy.exc import OperationalError
        class Busy(Exception):sqlstate='55P03'
        original=self.pool.connection.execute
        def execute(sql,args):
            if 'pg_advisory_xact_lock' in str(sql):raise OperationalError('private',{},Busy('private'))
            return original(sql,args)
        self.pool.connection.execute=execute
        result=await self.put()
        self.assertEqual((result.status_code,result.json()['error_id']),(409,'operation_busy'))
    async def test_overlapping_successful_writes_use_separate_exclusive_connections(self):
        from sqlalchemy.pool import QueuePool
        overlap=threading.Barrier(2);lock=threading.Lock();held=set();seen=set()
        class Driver(support.Connection):
            def rollback(self):pass
            def close(self):pass
            def execute(self,sql,args):
                if str(sql).startswith('UPDATE kdg_capture.capture'):overlap.wait(1)
                return super().execute(sql,args)
        pool=QueuePool(Driver,pool_size=2,max_overflow=0,timeout=.1)
        testcase=self
        class Lease:
            @contextmanager
            def connect(self):
                proxy=pool.connect();connection=proxy.driver_connection
                with lock:
                    testcase.assertNotIn(id(connection),held)
                    held.add(id(connection));seen.add(id(connection))
                try:yield connection
                finally:
                    with lock:held.remove(id(connection))
                    proxy.close()
        self.app.state.edit_engine=Lease()
        try:
            # Distinct operations isolate connection ownership from duplicate
            # serialization, which remains a native qualification gate.
            second=support.body.command(operation_id=support.ACTOR).model_dump()
            results=await asyncio.gather(self.put(),self.put(json=second))
            self.assertEqual([r.status_code for r in results],[200,200])
            self.assertEqual(len(seen),2);self.assertEqual(held,set());self.assertEqual(pool.checkedout(),0)
        finally:pool.dispose()
    async def test_unexpected_failure_and_routing_failures_are_private_and_safe(self):
        def fail():raise RuntimeError('PRIVATE-canary')
        self.pool.borrow=fail
        with self.assertLogs('service.operations',level='ERROR') as logs:result=await self.put()
        self.assertEqual((result.status_code,result.json()['error_id']),(500,'internal_error'))
        self.assertNotIn('PRIVATE',result.text+str(logs.output))
        result=await self.put('/missing')
        self.assertEqual((result.status_code,result.json()['error_id']),(404,'resource_not_found'))
    async def test_lifespan_disposes_owned_engine_without_checkout(self):
        async with self.app.router.lifespan_context(self.app):pass
        self.assertEqual((self.pool.disposed,self.pool.borrows),(1,0))

if __name__=='__main__':unittest.main()
