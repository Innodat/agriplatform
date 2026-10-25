"""Synthetic ASGI + exclusive recorded-connection recovery acceptance."""
import asyncio
from contextlib import contextmanager
import json
import threading
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import httpx
import test_operation_recovery as support
import recovery_http as boundary

recovery = support.recovery
handler = support.handler
write = support.write
OPERATION = support.support.support.OPERATION
URL = '/api/v1/operations/' + OPERATION + '?command_type=capture.create'
DB_URL = 'postgresql+psycopg://synthetic:synthetic@127.0.0.1:55482/synthetic'

class Pool:
    def __init__(self):
        self.connection=support.Connection(); self.connection.outcome=support.support.stored()
        self.disposed=0;self.borrows=0;self.releases=0;self.borrow=lambda:None;self.release=lambda:None
    def dispose(self):self.disposed+=1
    @contextmanager
    def connect(self):
        self.borrow();self.borrows+=1
        try:yield self.connection
        finally:self.release();self.releases+=1

class HTTPAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pool=Pool();self.checks=[]
        self.upstream=lambda:httpx.Response(200,json=support.support.evidence(recovery.PERMISSION))
        async def access(request):
            self.assertEqual(self.pool.borrows,0)
            self.checks.append(request)
            return self.upstream()
        with patch.object(boundary,'create_engine',return_value=self.pool) as factory:
            self.app=boundary.create_candidate(org_id=support.support.ORG,
                access_url='https://access.invalid',service_key='synthetic-key',
                database_url=DB_URL,transport=httpx.MockTransport(access))
            self.engine_options=factory.call_args.kwargs
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='https://kdg.invalid')
    async def asyncTearDown(self):await self.client.aclose()
    async def get(self,url=URL,**kwargs):
        kwargs.setdefault('headers',{'Authorization':'Bearer synthetic'})
        result=await self.client.request('GET',url,**kwargs)
        self.assertEqual(result.headers['cache-control'],'private, no-store')
        return result
    async def test_http_committed_receipt_and_exclusive_release(self):
        result=await self.get()
        self.assertEqual(result.status_code,200)
        self.assertEqual(result.json(),dict(operation_id=OPERATION,command_type='capture.create',command_version=1,status='committed',result=dict(capture_id=support.support.STORED_CAPTURE,revision='1')))
        self.assertEqual((len(self.checks),self.pool.borrows,self.pool.releases),(1,1,1))
        self.assertFalse(self.pool.connection.in_transaction())
    async def test_http_verified_absence(self):
        self.pool.connection.outcome=None
        result=await self.get()
        self.assertEqual(result.json(),dict(operation_id=OPERATION,command_type='capture.create',status='unresolved'))
    async def test_closed_single_valued_query_and_identifier(self):
        for url in (URL+'&command_type=capture.edit',URL+'&account_id=x',URL+'&org_id=x',
                    URL.replace('?command_type=capture.create',''),URL.replace('capture.create','capture.delete'),
                    URL.replace(OPERATION,'invalid'),URL+'&%63ommand_type=capture.create'):
            result=await self.get(url)
            self.assertEqual((result.status_code,result.json()['error_id']),(422,'validation_failed'))
        self.assertEqual((len(self.checks),self.pool.borrows),(0,0))
    async def test_exact_bearer_header_and_challenge(self):
        for headers in ({},{'Authorization':'Basic private'},[('authorization','Bearer a'),('Authorization','Bearer b')],{'Authorization':'Bearer a, Bearer b'},{'Authorization':'Bearer a,b'}, {'Authorization':'Bearer a:b'}, {'Authorization':'Bearer a=b'}, {'Authorization':'Bearer a!b'}):
            result=await self.get(headers=headers)
            self.assertEqual((result.status_code,result.json()['error_id']),(401,'authentication_required'))
            self.assertEqual(result.headers['www-authenticate'],'Bearer')
        self.assertEqual((len(self.checks),self.pool.borrows),(0,0))
    async def test_nonempty_body_refused_before_authorization(self):
        result=await self.get(content=b'private-body')
        self.assertEqual((result.status_code,result.json()['error_id']),(422,'validation_failed'))
        self.assertFalse(self.checks)
    async def test_current_denial_prevents_pool_checkout(self):
        self.upstream=lambda:httpx.Response(403,json={'detail':{'code':'access_denied'}})
        result=await self.get()
        self.assertEqual((result.status_code,result.json()['error_id']),(403,'access_denied'))
        self.assertEqual(self.pool.borrows,0)
    async def test_ordinary_engine_policy_is_lazy_and_bounded(self):
        self.assertEqual(self.pool.borrows,0)
        self.assertEqual(self.engine_options['pool_timeout'],.25)
        self.assertEqual(self.engine_options['max_overflow'],0)
        self.assertEqual(self.engine_options['connect_args']['connect_timeout'],3)
        self.assertIn('default_transaction_read_only=on',self.engine_options['connect_args']['options'])
        self.assertFalse(self.engine_options['pool_pre_ping'])
    async def test_pool_or_driver_failure_is_safe_unavailable(self):
        from sqlalchemy.exc import TimeoutError,OperationalError
        for error in (TimeoutError('private-pool'),OperationalError('private-sql',{},Exception('private-driver'))):
            def fail():raise error
            self.pool.borrow=fail
            result=await self.get()
            self.assertEqual((result.status_code,result.json()['error_id']),(503,'operation_verification_unavailable'))
            self.assertNotIn('private-',result.text)
    async def test_checkout_expiry_does_not_refresh_authority(self):
        now=100.0
        def checkout():
            nonlocal now
            now+=2
        self.pool.borrow=checkout
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):
            result=await self.get()
        self.assertEqual(result.json()['error_id'],'authorization_observation_expired')
        self.assertEqual(self.pool.releases,1)
        self.assertEqual(self.pool.connection.calls,[])
    async def test_release_completion_is_in_original_budget(self):
        now=100.0
        def release():
            nonlocal now
            now=111.0
        self.pool.release=release
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):
            result=await self.get()
        self.assertEqual(result.json()['error_id'],'execution_timeout')
    async def test_release_failure_never_discloses_provisional_receipt(self):
        from sqlalchemy.exc import OperationalError
        def release():raise OperationalError('private-release',{},Exception('private'))
        self.pool.release=release
        result=await self.get()
        self.assertEqual((result.status_code,result.json()['error_id']),(503,'operation_verification_unavailable'))
    async def test_unexpected_error_is_safe_and_not_cached(self):
        def fail():raise RuntimeError('private-unexpected-canary')
        self.pool.borrow=fail
        with self.assertLogs('service.operations',level='ERROR') as logs:
            result=await self.get()
        self.assertEqual((result.status_code,result.json()['error_id']),(500,'internal_error'))
        self.assertNotIn('private-',result.text+str(logs.output))
    async def test_explicit_default_port_overrides_ambient_pgport(self):
        import os
        with patch.dict(os.environ,{'PGPORT':'9999'}),patch.object(boundary,'create_engine',return_value=self.pool) as factory:
            boundary._engine(DB_URL.replace(':55482',''))
        self.assertEqual(factory.call_args.kwargs['connect_args']['port'],5432)
        self.assertEqual(self.engine_options['connect_args']['port'],55482)
    async def test_overlapping_successful_checkouts_are_exclusive_until_release(self):
        from sqlalchemy.pool import QueuePool
        overlap=threading.Barrier(2);lock=threading.Lock();held=set();seen=set()
        class Driver(support.Connection):
            def __init__(self):
                super().__init__();self.outcome=support.support.stored()
            def rollback(self):pass
            def close(self):pass
            def execute(self,sql,parameters):
                if 'FROM kdg_capture.operation_outcome' in str(sql):overlap.wait(1)
                return super().execute(sql,parameters)
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
        self.app.state.recovery_engine=Lease()
        try:
            results=await asyncio.gather(self.get(),self.get())
            self.assertTrue(all(result.status_code==200 for result in results))
            self.assertEqual(len(seen),2);self.assertEqual(held,set())
            self.assertEqual(pool.checkedout(),0)
        finally:pool.dispose()
    async def test_expired_worker_retains_ownership_until_each_phase_unwinds(self):
        original_budget=write.Budget
        def short():
            budget=original_budget();budget.deadline=budget.started_at+.06
            return budget
        for phase in ('borrow','sql','release'):
            self.pool=Pool();started,release=threading.Event(),threading.Event()
            def pending():started.set();release.wait(1)
            if phase=='sql':
                original=self.pool.connection.execute
                def execute(sql,parameters):
                    if 'FROM kdg_capture.operation_outcome' in str(sql):pending()
                    return original(sql,parameters)
                self.pool.connection.execute=execute
            else:setattr(self.pool,phase,pending)
            with patch.object(boundary,'_pool_for',return_value=self.pool),patch.object(write,'Budget',side_effect=short):
                task=asyncio.create_task(self.get())
                try:
                    for _ in range(100):
                        if started.is_set():break
                        await asyncio.sleep(.001)
                    self.assertTrue(started.is_set(),phase)
                    await asyncio.sleep(.08)
                    self.assertFalse(task.done(),phase)
                finally:
                    release.set()
                    result=await task
                self.assertEqual((result.status_code,result.json()['error_id']),(503,'execution_timeout'))
                self.assertEqual(self.pool.releases,1)
    async def test_owned_pool_disposed_on_normal_and_exceptional_lifespan_exit(self):
        for exceptional in (False,True):
            self.pool.disposed=0
            try:
                async with self.app.router.lifespan_context(self.app):
                    self.assertEqual(self.pool.disposed,0)
                    if exceptional:raise RuntimeError('synthetic-lifespan-exit')
            except RuntimeError:
                if not exceptional:raise
            self.assertEqual(self.pool.disposed,1)
            self.assertEqual(self.pool.borrows,0)
    async def test_edit_receipt_adapts_without_revision_replacement(self):
        self.pool.connection.outcome.update(command_type='capture.edit',result=dict(capture_id=support.support.STORED_CAPTURE,revision='3'))
        result=await self.get(URL.replace('capture.create','capture.edit'))
        self.assertEqual((result.status_code,result.json()['command_type'],result.json()['result']['revision']),(200,'capture.edit','3'))
    async def test_stream_receipt_has_total_deadline_before_access(self):
        async def slow():
            await asyncio.sleep(.05)
            yield b''
        original=write.Budget
        def short():
            budget=original(); budget.deadline=budget.started_at+.02
            return budget
        with patch.object(write,'Budget',side_effect=short):
            result=await self.get(content=slow())
        self.assertEqual((result.status_code,result.json()['error_id']),(503,'execution_timeout'))
        self.assertEqual((len(self.checks),self.pool.borrows),(0,0))
    async def test_database_policy_rejects_dns_failover_and_ambient_parameters(self):
        for url in ('sqlite://','postgresql://user:secret@localhost/db',
            'postgresql://user:secret@127.0.0.1,127.0.0.2/db', DB_URL+'?connect_timeout=999',
            'postgresql://user@127.0.0.1/db','not a url'):
            with self.assertRaisesRegex(RuntimeError,'^kdg_recovery_database_configuration_invalid$'):
                boundary._engine(url)
    async def test_routing_errors_private_and_candidate_not_activated(self):
        for method,url,status in (('POST',URL,405),('GET','/missing',404),('GET',URL.replace('?','/?'),404)):
            result=await self.client.request(method,url)
            self.assertEqual(result.status_code,status)
            self.assertEqual(result.headers['cache-control'],'private, no-store')
        import importlib.util
        path=support.support.ROOT/'apps/kdg-capture/api/main.py'
        spec=importlib.util.spec_from_file_location('kdg_active_http_check',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.assertNotIn('/api/v1/operations/{operation_id}',module.app.openapi()['paths'])
        self.assertFalse(hasattr(boundary,'app'))
    async def test_unknown_handler_error_pair_is_not_disclosed(self):
        with patch.object(recovery.RecoveryHandler,'_authorize',side_effect=handler.HandlerError(418,'private-canary')):
            result=await self.get()
        self.assertEqual((result.status_code,result.json()['error_id']),(500,'internal_error'))
        self.assertNotIn('private-canary',result.text)
    async def test_upstream_setup_and_authentication_errors_are_safe(self):
        for status,identifier in ((401,'authentication_required'),(409,'identity.actor_setup_required'),(503,'secret-canary')):
            self.upstream=lambda:httpx.Response(status,json={'detail':{'code':identifier}})
            result=await self.get()
            expected='authorization_unavailable' if status==503 else identifier
            self.assertEqual(result.json()['error_id'],expected)
        self.assertEqual(self.pool.borrows,0)
    async def test_real_queue_pool_exhaustion_is_bounded_and_unavailable(self):
        from sqlalchemy.pool import QueuePool
        class Driver:
            def rollback(self):pass
            def close(self):pass
        pool=QueuePool(lambda:Driver(),pool_size=1,max_overflow=0,timeout=.02)
        held=pool.connect()
        self.app.state.recovery_engine=pool
        try:
            result=await self.get()
            self.assertEqual((result.status_code,result.json()['error_id']),(503,'operation_verification_unavailable'))
        finally:
            held.close();pool.dispose()
    async def test_cancellation_keeps_checkout_sql_and_release_owned(self):
        for phase in ('borrow','sql','release'):
            self.pool=Pool()
            started,release=threading.Event(),threading.Event()
            def pending():started.set();release.wait(1)
            if phase=='sql':
                original=self.pool.connection.execute
                def execute(sql,params):
                    if 'FROM kdg_capture.operation_outcome' in str(sql):pending()
                    return original(sql,params)
                self.pool.connection.execute=execute
            else:setattr(self.pool,phase,pending)
            with patch.object(boundary,'_pool_for',return_value=self.pool):
                task=asyncio.create_task(self.get())
                try:
                    for _ in range(100):
                        if started.is_set():break
                        await asyncio.sleep(.001)
                    self.assertTrue(started.is_set(),phase)
                    task.cancel();await asyncio.sleep(.01);task.cancel();await asyncio.sleep(.01)
                    self.assertFalse(task.done(),phase)
                finally:
                    release.set()
                    with self.assertRaises(asyncio.CancelledError):await task
                self.assertEqual(self.pool.releases,1,phase)

if __name__=='__main__':unittest.main()
