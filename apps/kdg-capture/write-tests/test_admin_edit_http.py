"""Both inert administrator routes: actual pair, transactions and private replay."""
import asyncio
from contextlib import contextmanager
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from uuid import UUID
import httpx
import test_capture_edit_handler as own
import test_admin_edit_context as authority_support
import admin_edit as edit
import admin_edit_http as boundary

write=edit.write
READ='kdg_capture.capture.read.all'
EDIT='kdg_capture.capture.edit.all'
URL='/api/v1/admin/captures/'+own.CAPTURE
RECOVERY='/api/v1/admin/operations/'+own.OPERATION+'?command_type=capture.edit'
DB_URL='postgresql+psycopg://synthetic:synthetic@127.0.0.1:55482/synthetic'

class Connection(own.Connection):
    def __init__(self):
        super().__init__();self.capture['owner_account_id']=own.CAPTURE
    def execute(self,sql,parameters):
        result=super().execute(sql,parameters)
        if str(sql)==edit.TARGET:return own.body.Rows(self.target)
        return result

class Pool:
    def __init__(self):
        self.connection=Connection();self.borrows=0;self.releases=0;self.disposed=0
        self.borrow=lambda:None;self.release=lambda:None
    @contextmanager
    def connect(self):
        self.borrow();self.borrows+=1
        try:yield self.connection
        finally:self.release();self.releases+=1
    def dispose(self):self.disposed+=1

class HTTPAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pool=Pool();self.read_pool=Pool();self.checks=[]
        self.upstream=lambda permission:httpx.Response(200,json=authority_support.evidence(permission))
        async def access(request):
            permission=json.loads(request.content)['permission'];self.checks.append(permission)
            result=self.upstream(permission)
            return await result if hasattr(result,'__await__') else result
        self.authority=edit.authority.AdminEditContextHandler(org_id=own.ORG,access_url='https://access.invalid',service_key='synthetic',transport=httpx.MockTransport(access))
        self.app=boundary._create_app(self.authority,self.pool,self.read_pool,own.ORG)
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='https://kdg.invalid')
    async def asyncTearDown(self):await self.client.aclose()
    async def put(self,url=URL,**kwargs):
        kwargs.setdefault('headers',{'Authorization':'Bearer synthetic','Content-Type':'application/json'})
        if not any(key in kwargs for key in ('json','content')):kwargs['json']=own.body.command().model_dump()
        result=await self.client.put(url,**kwargs);self.assertEqual(result.headers['cache-control'],'private, no-store');return result
    async def get(self,url=RECOVERY,**kwargs):
        kwargs.setdefault('headers',{'Authorization':'Bearer synthetic'})
        result=await self.client.request('GET',url,**kwargs);self.assertEqual(result.headers['cache-control'],'private, no-store');return result
    async def test_foreign_owner_actual_executor_changed_and_noop(self):
        for noop,revision,count in ((False,'5',3),(True,'4',1)):
            self.pool.connection=Connection();self.pool.connection.unchanged=noop
            result=await self.put();self.assertEqual((result.status_code,result.json()['result']['revision']),(200,revision))
            self.assertEqual(self.checks[-2:],[READ,EDIT])
            mutations=[(s,p) for s,p in self.pool.connection.calls if s.startswith(('UPDATE','INSERT'))]
            self.assertEqual(len(mutations),count)
            for sql,args in mutations:
                self.assertEqual((args['account'],args['actor']),(own.ACCOUNT,own.ACTOR))
            self.assertEqual(self.pool.connection.calls[-1][0],'COMMIT')
    async def test_original_receipt_survives_changed_retry_path_body_and_later_revision(self):
        self.pool.connection.existing=own.stored();self.pool.connection.capture['revision']=19
        result=await self.put('/api/v1/admin/captures/'+own.ACTOR,json=own.body.command(answers={},expected_revision='1').model_dump())
        self.assertEqual((result.status_code,result.json()['result']),(200,dict(capture_id=own.access.STORED_CAPTURE,revision='2')))
        target=[p for s,p in self.pool.connection.calls if s==edit.TARGET]
        self.assertEqual(target,[dict(org=own.ORG,capture=own.access.STORED_CAPTURE)])
        self.assertFalse(any(s.startswith(('UPDATE','INSERT')) for s,_ in self.pool.connection.calls))
    async def test_recovery_read_only_after_edit_loss_and_verified_absence(self):
        self.upstream=lambda p:httpx.Response(403,json={'detail':{'code':'access_denied'}}) if p==EDIT else httpx.Response(200,json=authority_support.evidence(p))
        self.read_pool.connection.existing=own.stored()
        result=await self.get();self.assertEqual((result.status_code,result.json()['result']['revision']),(200,'2'))
        self.assertEqual(self.checks,[READ]);self.assertEqual(self.pool.borrows,0)
        self.assertFalse(any(s.startswith(('UPDATE','INSERT')) or 'FOR UPDATE' in s for s,_ in self.read_pool.connection.calls))
        self.read_pool.connection=Connection();result=await self.get()
        self.assertEqual(result.json(),dict(operation_id=own.OPERATION,command_type='capture.edit',status='unresolved'))
    async def test_stored_target_and_receipt_corruption_are_unavailable(self):
        for target in (None,{},dict(id=UUID(own.ACTOR),org_id=UUID(own.ORG)),dict(id=UUID(own.access.STORED_CAPTURE),org_id=UUID(own.ACTOR))):
            for method,pool in ((self.put,self.pool),(self.get,self.read_pool)):
                pool.connection=Connection();pool.connection.existing=own.stored();pool.connection.target=target
                result=await method();self.assertEqual((result.status_code,result.json()['error_id']),(503,'operation_verification_unavailable'))
        for method,pool in ((self.put,self.pool),(self.get,self.read_pool)):
            pool.connection=Connection();pool.connection.existing=own.stored();pool.connection.existing['result']['revision']='0'
            result=await method();self.assertEqual(result.json()['error_id'],'operation_verification_unavailable')
    async def test_denial_scope_mismatch_setup_and_outage_before_checkout(self):
        cases=[(403,{'detail':{'code':'access_denied'}},403),(409,{'detail':{'code':'identity.actor_setup_required'}},409),(500,{'private':'secret'},503)]
        changes=[{'account_id':own.ACTOR},{'actor_id':own.CAPTURE},{'membership_id':'8'}, {'authorization_scope':{'kind':'organization','org_id':own.ACTOR}},{'resource_scope':{'kind':'own_account','account_id':own.ACCOUNT}},{'unexpected':'private'}]
        for selected in (READ,EDIT):
            for status,value,expected in cases:
                self.upstream=lambda p:httpx.Response(status,json=value) if p==selected else httpx.Response(200,json=authority_support.evidence(p))
                result=await self.put();self.assertEqual(result.status_code,expected)
            for change in changes:
                self.upstream=lambda p:httpx.Response(200,json={**authority_support.evidence(p),**(change if p==selected else {})})
                result=await self.put();self.assertEqual(result.status_code,503)
        self.assertEqual((self.pool.borrows,self.read_pool.borrows),(0,0))
    async def test_conflict_and_invalid_original_answers_have_no_outcome(self):
        for noop in (False,True):
            self.pool.connection=Connection();self.pool.connection.unchanged=noop
            result=await self.put(json=own.body.command(expected_revision='3').model_dump())
            self.assertEqual(result.json(),dict(error='The request could not be completed.',error_id='kdg_capture.capture_revision_conflict',current_revision='4'))
        result=await self.put(json=own.body.command(answers={}).model_dump());self.assertEqual(result.status_code,422)
        self.assertFalse(any(s.startswith(('UPDATE','INSERT')) for s,_ in self.pool.connection.calls))
    async def test_strict_body_path_query_header_and_discriminator(self):
        for url,raw in ((URL,b'{}'),(URL,b'\xff'),(URL,b'x'*131073),(URL,b'{"command_version":1,"command_version":1}'),(URL+'?x=1',b'{}'),('/api/v1/admin/captures/bad',b'{}')):
            self.assertEqual((await self.put(url,content=raw)).status_code,422)
        for suffix in ('','?command_type=capture.create','?command_type=capture.edit&x=1','?command_type=capture.edit&command_type=capture.edit'):
            self.assertEqual((await self.get(RECOVERY.split('?')[0]+suffix)).status_code,422)
        self.assertEqual((await self.get(content=b'x')).status_code,422)
        for headers in ({},[('Authorization','Bearer a'),('Authorization','Bearer b')],{'Authorization':'Bearer a,b'}):
            self.assertEqual((await self.put(headers=headers)).status_code,401)
        self.assertEqual((self.checks,self.pool.borrows,self.read_pool.borrows),([],0,0))
    async def test_first_freshness_pair_deadline_checkout_and_release_budget(self):
        now=100.0
        def age(p):
            nonlocal now
            if p==EDIT:now+=1.1
            return httpx.Response(200,json=authority_support.evidence(p))
        self.upstream=age
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):result=await self.put()
        self.assertEqual(result.json()['error_id'],'authorization_observation_expired')
        self.assertFalse(any('kdg_capture.' in s for s,_ in self.pool.connection.calls))
        self.upstream=lambda p:httpx.Response(200,json=authority_support.evidence(p))
        now=100.
        def late():
            nonlocal now
            now=111.
        self.pool.release=late
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):result=await self.put()
        self.assertEqual(result.json()['error_id'],'execution_timeout')
    async def test_sql_commit_unknown_release_and_serialization_faults_are_safe(self):
        for phase in ('sql','commit','release','serialize'):
            self.pool.connection=Connection();self.pool.release=lambda:None
            if phase=='sql':self.pool.connection.failure='UPDATE kdg_capture.capture'
            if phase=='commit':self.pool.connection.fail_commit=True
            if phase=='release':self.pool.release=lambda:(_ for _ in ()).throw(RuntimeError('PRIVATE'))
            from contextlib import nullcontext
            scope=patch.object(edit.outcomes.CaptureReceipt,'model_dump_json',side_effect=RuntimeError('PRIVATE')) if phase=='serialize' else nullcontext()
            with scope:result=await self.put()
            self.assertEqual((result.status_code,result.json()['error_id']),(500,'internal_error'));self.assertNotIn('PRIVATE',result.text)
    async def test_lazy_distinct_write_read_engines_and_shutdown(self):
        with patch.object(boundary,'create_engine',side_effect=[self.pool,self.read_pool]) as factory:
            boundary.create_candidate(org_id=own.ORG,access_url='https://access.invalid',service_key='synthetic',database_url=DB_URL)
        options=[c.kwargs for c in factory.call_args_list]
        self.assertNotIn('default_transaction_read_only=on',options[0]['connect_args']['options'])
        self.assertIn('default_transaction_read_only=on',options[1]['connect_args']['options'])
        self.assertTrue(all(o['pool_timeout']==.25 and o['max_overflow']==0 for o in options))
        async with self.app.router.lifespan_context(self.app):pass
        self.assertEqual((self.pool.disposed,self.read_pool.disposed,self.pool.borrows,self.read_pool.borrows),(1,1,0,0))

    async def test_pair_total_deadline_cancels_second_after_first_completes(self):
        phases=[];first_release=asyncio.Event();second_entered=asyncio.Event()
        async def upstream(permission):
            if permission==READ:
                phases.append('first_entered');await first_release.wait();phases.append('first_completed')
                return httpx.Response(200,json=authority_support.evidence(permission))
            phases.append('second_entered');second_entered.set()
            try:await asyncio.sleep(.15)
            except asyncio.CancelledError:
                phases.append('second_cancelled');raise
            phases.append('second_completed')
            return httpx.Response(200,json=authority_support.evidence(permission))
        self.upstream=upstream
        with patch.object(edit.protected,'ACCESS_SECONDS',.2):
            task=asyncio.create_task(self.put());timer=asyncio.get_running_loop().call_later(.12,first_release.set)
            try:
                await asyncio.wait_for(second_entered.wait(),.18)
                self.assertEqual(phases,['first_entered','first_completed','second_entered']);self.assertFalse(task.done())
                result=await task
            finally:
                timer.cancel();first_release.set()
                if not task.done():
                    task.cancel()
                    with self.assertRaises(asyncio.CancelledError):await task
        self.assertEqual(result.json()['error_id'],'authorization_unavailable')
        self.assertEqual(phases,['first_entered','first_completed','second_entered','second_cancelled'])
        self.assertEqual((self.pool.borrows,self.read_pool.borrows),(0,0))
    async def test_both_routes_hold_lease_through_repeated_cancel_and_worker_unwind(self):
        import threading
        for request,pool in ((self.put,self.pool),(self.get,self.read_pool)):
            for phase in ('borrow','sql','commit','release'):
                pool.connection=Connection();pool.borrow=lambda:None;pool.release=lambda:None;pool.releases=0
                entered,finish=threading.Event(),threading.Event()
                def pending():entered.set();finish.wait(2)
                if phase=='sql':
                    execute=pool.connection.execute
                    def blocked(sql,args):
                        if 'FROM kdg_capture.operation_outcome' in str(sql):pending()
                        return execute(sql,args)
                    pool.connection.execute=blocked
                elif phase=='commit':pool.connection.on_commit=pending
                else:setattr(pool,phase,pending)
                task=asyncio.create_task(request())
                try:
                    for _ in range(250):
                        if entered.is_set():break
                        await asyncio.sleep(.001)
                    self.assertTrue(entered.is_set(),phase)
                    task.cancel();await asyncio.sleep(.01);task.cancel();await asyncio.sleep(.01)
                    self.assertFalse(task.done(),phase);self.assertEqual(pool.releases,0)
                finally:
                    finish.set()
                    with self.assertRaises(asyncio.CancelledError):await task
                self.assertEqual(pool.releases,1)
    async def test_both_routes_refuse_late_or_failed_final_serialization(self):
        now=100.
        for request,model in ((self.put,edit.outcomes.CaptureReceipt),(self.get,edit.Unresolved)):
            original=model.model_dump_json
            def late(value,*args,**kwargs):
                nonlocal now
                result=original(value,*args,**kwargs);now=111.;return result
            now=100.
            with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)),patch.object(model,'model_dump_json',late):
                result=await request()
            self.assertEqual(result.json()['error_id'],'execution_timeout')
            with patch.object(model,'model_dump_json',side_effect=RuntimeError('PRIVATE-serialization')):result=await request()
            self.assertGreaterEqual(result.status_code,500);self.assertNotIn('PRIVATE',result.text)
    async def test_recovery_empty_stream_is_bounded_without_access(self):
        now=100.
        async def empty_chunks():
            nonlocal now
            for _ in range(15):now+=1;yield b''
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):result=await self.get(content=empty_chunks())
        self.assertEqual(result.json()['error_id'],'execution_timeout');self.assertEqual(self.checks,[])
    async def test_direct_handlers_share_pair_and_read_only_recovery(self):
        writer=edit.AdminEditHandler(org_id=own.ORG,access_url='https://access.invalid',service_key='synthetic',transport=self.authority._transport)
        reader=edit.AdminRecoveryHandler(org_id=own.ORG,access_url='https://access.invalid',service_key='synthetic',transport=self.authority._transport)
        db=Connection()
        result=await writer.execute(db,own.CAPTURE,json.dumps(own.body.command().model_dump()),'Bearer synthetic')
        self.assertEqual(result.result.revision,'5');self.assertEqual(self.checks,[READ,EDIT])
        self.checks=[];db=Connection();db.existing=own.stored()
        result=await reader.execute(db,own.OPERATION,'capture.edit','Bearer synthetic')
        self.assertEqual(result.result.revision,'2');self.assertEqual(self.checks,[READ])
        with self.assertRaises(edit.RevisionConflictError):
            await writer.execute(Connection(),own.CAPTURE,json.dumps(own.body.command(expected_revision='3').model_dump()),'Bearer synthetic')

    async def test_stored_target_sql_failure_maps_to_verification_unavailable(self):
        from sqlalchemy.exc import SQLAlchemyError
        for request,pool in ((self.put,self.pool),(self.get,self.read_pool)):
            pool.connection=Connection();pool.connection.existing=own.stored()
            original=pool.connection.execute
            def failed_target(sql,args):
                if str(sql)==edit.TARGET:raise SQLAlchemyError('PRIVATE-target')
                return original(sql,args)
            pool.connection.execute=failed_target
            result=await request()
            self.assertEqual((result.status_code,result.json()['error_id']),(503,'operation_verification_unavailable'))
            self.assertNotIn('PRIVATE',result.text);self.assertNotIn('result',result.json())
    async def test_first_disposal_failure_still_attempts_distinct_recovery_pool(self):
        def fail():
            self.pool.disposed+=1
            raise RuntimeError('synthetic-dispose-failure')
        self.pool.dispose=fail
        with self.assertRaisesRegex(RuntimeError,'^synthetic-dispose-failure$'):
            async with self.app.router.lifespan_context(self.app):pass
        self.assertEqual((self.pool.disposed,self.read_pool.disposed),(1,1))
    async def test_recovery_sql_commit_release_faults_never_disclose_result(self):
        for phase in ('sql','commit','release'):
            self.read_pool.connection=Connection();self.read_pool.release=lambda:None
            if phase=='sql':self.read_pool.connection.failure='FROM kdg_capture.operation_outcome'
            if phase=='commit':self.read_pool.connection.fail_commit=True
            if phase=='release':
                def fail():raise RuntimeError('PRIVATE-release')
                self.read_pool.release=fail
            result=await self.get()
            self.assertEqual((result.status_code,result.json()['error_id']),(503,'operation_verification_unavailable'),phase)
            self.assertNotIn('PRIVATE',result.text);self.assertNotIn('result',result.json());self.assertNotIn('status',result.json())
    async def test_recovery_checkout_cannot_renew_read_observation(self):
        now=100.
        def delayed():
            nonlocal now
            now+=1.1
        self.read_pool.borrow=delayed
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):result=await self.get()
        self.assertEqual((result.status_code,result.json()['error_id']),(503,'authorization_observation_expired'))
        self.assertEqual((self.checks,self.read_pool.connection.calls,self.read_pool.releases),([READ],[],1))
    async def test_admin_put_stream_deadline_bounds_immediate_body_chunks(self):
        now=100.;consumed=0
        async def chunks():
            nonlocal now,consumed
            for _ in range(25):
                now+=1.;consumed+=1;yield b' '
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):result=await self.put(content=chunks())
        self.assertEqual((result.status_code,result.json()['error_id']),(503,'execution_timeout'))
        self.assertLessEqual(consumed,10)
        self.assertEqual((self.checks,self.pool.borrows,self.read_pool.borrows),([],0,0))
