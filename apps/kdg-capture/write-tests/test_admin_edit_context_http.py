"""Synthetic current admin edit-context HTTP acceptance with exclusive read leases."""
import asyncio
import copy
import json
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import httpx
import test_admin_http as support
import test_admin_edit_context as direct
import admin_edit_context_http as boundary

recovery=boundary.recovery
write=recovery.write
URL='/api/v1/admin/captures/'+support.support.CAPTURE+'/edit-context'
DB_URL=support.history_support.DB_URL

class HTTPAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pool=support.Pool();self.checks=[]
        self.upstream=lambda permission:httpx.Response(200,json=direct.evidence(permission))
        async def access(request):
            self.assertEqual(self.pool.borrows,0)
            self.checks.append(json.loads(request.content)['permission'])
            return self.upstream(self.checks[-1])
        with patch.object(boundary,'create_engine',return_value=self.pool) as factory:
            self.app=boundary.create_candidate(org_id=support.support.ORG,access_url='https://access.invalid',service_key='synthetic',database_url=DB_URL,transport=httpx.MockTransport(access))
            self.engine_options=factory.call_args.kwargs
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='https://kdg.invalid')
    async def asyncTearDown(self):await self.client.aclose()
    async def get(self,url=URL,**kwargs):
        kwargs.setdefault('headers',{'Authorization':'Bearer synthetic'})
        result=await self.client.request('GET',url,**kwargs)
        self.assertEqual(result.headers['cache-control'],'private, no-store')
        return result
    async def test_foreign_original_context_private_closed_and_released(self):
        self.pool.connection.replay_assignment=None
        result=await self.get();self.assertEqual(result.status_code,200)
        body=result.json();self.assertEqual(set(body),{'capture','editable_fields'})
        self.assertEqual(body['editable_fields'],['observation_date','answers'])
        self.assertEqual(body['capture']['owner_account_id'],support.FOREIGN)
        self.assertEqual(body['capture']['revision'],'1')
        self.assertEqual(body['capture']['definition'],support.support.DEFINITION)
        self.assertEqual((self.checks,self.pool.borrows,self.pool.releases),([direct.READ,direct.EDIT],1,1))
        self.assertFalse(self.pool.connection.in_transaction())
    async def test_input_refused_before_authority_or_checkout(self):
        for url in (URL+'?org_id=x',URL+'?x=1&x=2',URL.replace(support.support.CAPTURE,'bad')):
            result=await self.get(url);self.assertEqual((result.status_code,result.json()['error_id']),(422,'validation_failed'))
        result=await self.get(content=b'private-body');self.assertEqual(result.status_code,422)
        for headers in ({},{'Authorization':'Basic private'},[('authorization','Bearer a'),('Authorization','Bearer b')],{'Authorization':'Bearer a,b'},{'Authorization':'Bearer a:b'},{'Authorization':'Bearer a=b'},{'Authorization':'Bearer a!b'}):
            result=await self.get(headers=headers)
            self.assertEqual((result.status_code,result.json()['error_id']),(401,'authentication_required'))
            self.assertEqual(result.headers['www-authenticate'],'Bearer')
        self.assertEqual((self.checks,self.pool.borrows),([],0))
    async def test_both_decision_failure_families_never_checkout(self):
        for selected in (direct.READ,direct.EDIT):
            for status,error,expected in ((401,'authentication_required','authentication_required'),(403,'access_denied','access_denied'),(409,'identity.actor_setup_required','identity.actor_setup_required'),(503,'private','authorization_unavailable')):
                self.upstream=lambda permission:httpx.Response(status,json={'detail':{'code':error}}) if permission==selected else httpx.Response(200,json=direct.evidence(permission))
                before=len(self.checks)
                result=await self.get();self.assertEqual((result.status_code,result.json()['error_id']),(status,expected))
                self.assertEqual(len(self.checks)-before,1 if selected==direct.READ else 2)
                self.assertEqual(self.pool.borrows,0)
    async def test_pair_deadline_is_outer_not_renewed(self):
        phases=[];first_release=asyncio.Event();second_entered=asyncio.Event()
        async def access(request):
            permission=json.loads(request.content)['permission']
            if permission==direct.READ:
                phases.append('first_entered')
                await first_release.wait()
                phases.append('first_completed')
                return httpx.Response(200,json=direct.evidence(permission))
            phases.append('second_entered');second_entered.set()
            try:await asyncio.sleep(.15)
            except asyncio.CancelledError:
                phases.append('second_cancelled');raise
            phases.append('second_completed')
            return httpx.Response(200,json=direct.evidence(permission))
        self.app=boundary._create_app(recovery.AdminEditContextHandler(org_id=support.support.ORG,access_url='https://access.invalid',service_key='synthetic',transport=httpx.MockTransport(access)),self.pool,support.support.ORG)
        await self.client.aclose();self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='https://kdg.invalid')
        with patch.object(recovery.protected,'ACCESS_SECONDS',.2):
            task=asyncio.create_task(self.get())
            release_timer=asyncio.get_running_loop().call_later(.12,first_release.set)
            try:
                await asyncio.wait_for(second_entered.wait(),.18)
                self.assertEqual(phases,['first_entered','first_completed','second_entered'])
                self.assertFalse(task.done())
                result=await task
            finally:
                release_timer.cancel();first_release.set()
                if not task.done():
                    task.cancel()
                    with self.assertRaises(asyncio.CancelledError):await task
        self.assertEqual((result.status_code,result.json()['error_id']),(503,'authorization_unavailable'))
        self.assertEqual(phases,['first_entered','first_completed','second_entered','second_cancelled'])
        self.assertEqual((self.pool.borrows,self.pool.releases),(0,0))
    async def test_cancellation_during_either_access_check_stops_pair_before_checkout(self):
        for selected in (direct.READ,direct.EDIT):
            entered=asyncio.Event();gate=asyncio.Event();phases=[]
            async def access(request):
                permission=json.loads(request.content)['permission'];phases.append((permission,'entered'))
                if permission==selected:
                    entered.set()
                    try:await gate.wait()
                    except asyncio.CancelledError:
                        phases.append((permission,'cancelled'));raise
                phases.append((permission,'completed'))
                return httpx.Response(200,json=direct.evidence(permission))
            self.app=boundary._create_app(recovery.AdminEditContextHandler(org_id=support.support.ORG,access_url='https://access.invalid',service_key='synthetic',transport=httpx.MockTransport(access)),self.pool,support.support.ORG)
            await self.client.aclose();self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='https://kdg.invalid')
            task=asyncio.create_task(self.get())
            try:
                await asyncio.wait_for(entered.wait(),1)
                task.cancel()
                with self.assertRaises(asyncio.CancelledError):await task
            finally:
                gate.set()
                if not task.done():
                    task.cancel()
                    with self.assertRaises(asyncio.CancelledError):await task
            await asyncio.sleep(0)
            expected=[] if selected==direct.READ else [(direct.READ,'entered'),(direct.READ,'completed')]
            self.assertEqual(phases,expected+[(selected,'entered'),(selected,'cancelled')])
            self.assertEqual((self.pool.borrows,self.pool.releases,self.pool.connection.calls),(0,0,[]))
    async def test_stream_total_deadline_before_authority(self):
        async def slow():
            await asyncio.sleep(.05);yield b''
        original=write.Budget
        def short():
            budget=original();budget.deadline=budget.started_at+.02;return budget
        with patch.object(write,'Budget',side_effect=short):result=await self.get(content=slow())
        self.assertEqual((result.status_code,result.json()['error_id']),(503,'execution_timeout'))
        self.assertEqual((self.checks,self.pool.borrows),([],0))
    async def test_checkout_freshness_and_release_deadline(self):
        now=100.0
        def stale():
            nonlocal now
            now+=1.1
        self.pool.borrow=stale
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):result=await self.get()
        self.assertEqual(result.json()['error_id'],'authorization_observation_expired')
        self.assertEqual((self.pool.connection.calls,self.pool.releases),([],1))
        self.pool.borrow=lambda:None;self.pool.borrows=0;now=100.0
        def expired():
            nonlocal now
            now=111.0
        self.pool.release=expired
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):result=await self.get()
        self.assertEqual(result.json()['error_id'],'execution_timeout')
    async def test_missing_foreign_invalid_and_driver_release_failures(self):
        from sqlalchemy.exc import OperationalError
        for phase in ('missing','foreign','invalid','driver','commit','release','serialization'):
            self.pool=support.Pool();self.app.state.recovery_engine=self.pool
            if phase=='missing':self.pool.connection.detail=None
            elif phase=='foreign':
                from uuid import UUID
                self.pool.connection.detail['org_id']=UUID(support.FOREIGN)
            elif phase=='invalid':self.pool.connection.detail['answers']={}
            elif phase=='driver':self.pool.connection.fail_execute=True
            elif phase=='commit':self.pool.connection.fail_commit=True
            elif phase=='release':
                def fail():raise OperationalError('private-release',{},Exception('private'))
                self.pool.release=fail
            self.pool.borrows=0
            if phase=='serialization':
                with patch.object(recovery.AdminEditContext,'model_dump_json',side_effect=ValueError('private')):result=await self.get()
            else:result=await self.get()
            self.assertEqual((result.status_code,result.json()['error_id']), (404,'capture_unavailable') if phase in ('missing','foreign') else (503,'capture_read_unavailable'),phase)
            self.assertNotIn('private',result.text);self.assertEqual(self.pool.releases,0 if phase=='release' else 1,phase)
    async def test_final_http_serialization_failure_after_worker_release_is_safe(self):
        original=recovery.AdminEditContext.model_dump_json;phases=[]
        def fail_final(value,*args,**kwargs):
            if self.pool.releases:
                self.assertEqual((self.pool.borrows,self.pool.releases),(1,1))
                self.assertFalse(self.pool.connection.in_transaction())
                phases.append('http_after_release')
                raise ValueError('private-final-serialization')
            phases.append('worker_before_release')
            return original(value,*args,**kwargs)
        with patch.object(recovery.AdminEditContext,'model_dump_json',fail_final):result=await self.get()
        self.assertEqual(phases,['worker_before_release','http_after_release'])
        self.assertEqual((result.status_code,result.json()['error_id']),(503,'capture_read_unavailable'))
        self.assertNotIn('private',result.text);self.assertNotIn('capture',result.json())
        self.assertEqual((self.pool.borrows,self.pool.releases),(1,1))
    async def test_context_validation_and_serialization_finish_inside_original_budget(self):
        now=100.0;original=recovery.AdminEditContext.model_dump_json
        def slow(value,*args,**kwargs):
            nonlocal now
            result=original(value,*args,**kwargs)
            if self.pool.releases:now=111.0
            return result
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)),patch.object(recovery.AdminEditContext,'model_dump_json',slow):result=await self.get()
        self.assertEqual((result.status_code,result.json()['error_id']),(503,'execution_timeout'))
        self.assertEqual(self.pool.releases,1)
    async def test_actual_envelope_544kib_inclusive_and_one_byte_over_after_release(self):
        original=recovery.AdminEditContext.model_dump_json
        for size,status in ((544*1024,200),(544*1024+1,503)):
            self.pool.borrows=0;self.pool.releases=0
            def padded(value,*args,**kwargs):
                body=original(value,*args,**kwargs)
                if self.pool.releases:return body+' '*(size-len(body.encode('utf-8')))
                return body
            with patch.object(recovery.AdminEditContext,'model_dump_json',padded):result=await self.get()
            self.assertEqual(result.status_code,status)
            self.assertEqual(self.pool.releases,1)
            if status==200:self.assertEqual(len(result.content),size)
            else:self.assertEqual(result.json()['error_id'],'capture_read_unavailable')
    async def test_actual_detail_512kib_inclusive_and_one_byte_over(self):
        ids=[f'{n:08x}-bbbb-4bbb-8bbb-{n:012x}' for n in range(1,31)]
        stored=copy.deepcopy(self.pool.connection.detail)
        stored.update(definition=dict(schema_version=1,questions=[dict(id=i,type='text',label='漢',required=True) for i in ids]),answers={i:{'value':'x'} for i in ids})
        ctx=write.VerifiedContext(support.support.ORG,support.support.ACCOUNT,support.support.ACTOR,'all_read',100)
        lookup=recovery.Lookup(capture_id=support.support.CAPTURE)
        remaining=512*1024-len(recovery.admin._snapshot(copy.deepcopy(stored),ctx,lookup).model_dump_json().encode())
        for i in ids:
            added=min(remaining,19996);emoji,ascii_bytes=divmod(added,4)
            stored['answers'][i]['value']='x'+'😀'*emoji+'a'*ascii_bytes;remaining-=added
        self.assertEqual(remaining,0);self.pool.connection.detail=stored
        result=await self.get();self.assertEqual(result.status_code,200)
        self.assertEqual(len(json.dumps(result.json()['capture'],ensure_ascii=False,separators=(',',':')).encode()),512*1024)
        stored['answers'][ids[-1]]['value']+='a';self.pool.borrows=0
        result=await self.get();self.assertEqual((result.status_code,result.json()['error_id']),(503,'capture_read_unavailable'))
    async def test_expiry_and_cancellation_retain_worker_through_unwind(self):
        for cancelled in (False,True):
            for phase in ('borrow','sql','release'):
                self.pool=support.Pool();self.app.state.recovery_engine=self.pool
                now=100.0;started,release=threading.Event(),threading.Event()
                def pending():started.set();release.wait(2)
                if phase=='sql':
                    original=self.pool.connection.execute
                    def execute(sql,params):
                        if str(sql)==recovery.DETAIL:pending()
                        return original(sql,params)
                    self.pool.connection.execute=execute
                else:setattr(self.pool,phase,pending)
                with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):
                    task=asyncio.create_task(self.get())
                    try:
                        for _ in range(200):
                            if started.is_set():break
                            await asyncio.sleep(.001)
                        self.assertTrue(started.is_set(),(cancelled,phase))
                        if cancelled:task.cancel()
                        else:now=111.0
                        await asyncio.sleep(.06);self.assertFalse(task.done(),(cancelled,phase))
                    finally:
                        release.set()
                        if cancelled:
                            with self.assertRaises(asyncio.CancelledError):await task
                        else:
                            result=await task;self.assertEqual(result.json()['error_id'],'execution_timeout')
                    self.assertEqual(self.pool.releases,1)
    async def test_lazy_readonly_engine_routing_and_lifespan(self):
        self.assertEqual(self.pool.borrows,0)
        self.assertEqual(self.engine_options['pool_timeout'],.25)
        self.assertEqual(self.engine_options['max_overflow'],0)
        self.assertIn('default_transaction_read_only=on',self.engine_options['connect_args']['options'])
        self.assertFalse(self.engine_options['pool_pre_ping'])
        for method,url,status in (('POST',URL,405),('GET',URL+'/',404),('GET','/missing',404)):
            result=await self.client.request(method,url);self.assertEqual(result.status_code,status)
            self.assertEqual(result.headers['cache-control'],'private, no-store')
        async with self.app.router.lifespan_context(self.app):pass
        self.assertEqual(self.pool.disposed,1)
        self.assertFalse(hasattr(boundary,'app'))

if __name__=='__main__':unittest.main()
