"""Synthetic organization-read acceptance; no native database or real authority."""
from contextlib import contextmanager
import copy
from uuid import UUID
import unittest
from unittest.mock import patch
import httpx
import test_capture_read as support
import test_history_http as history_support
import admin_http as boundary

PERMISSION='kdg_capture.capture.read.all'
FOREIGN=support.IDS[0]
DETAIL='/api/v1/admin/captures/'+support.CAPTURE
HISTORY='/api/v1/admin/captures?from_date=2026-10-01&to_date=2026-10-26&limit=2'

def evidence():
    return {**support.support.evidence(PERMISSION),'resource_scope':dict(kind='organization',org_id=support.ORG)}

class Connection(history_support.Connection):
    def __init__(self):
        super().__init__()
        self.detail['owner_account_id']=UUID(FOREIGN)
        for row in self.rows:row['owner_account_id']=UUID(FOREIGN)
    def execute(self,sql,parameters):
        sql=str(sql)
        if 'FROM kdg_capture.capture c' in sql and 'c.owner_account_id=CAST(:account AS uuid)' not in sql:
            self.calls.append((sql,parameters))
            if self.fail_execute:
                from sqlalchemy.exc import OperationalError
                raise OperationalError('private-sql',{},Exception('private-driver'))
            if 'ORDER BY' not in sql:return support.support.support.Rows(copy.deepcopy(self.detail))
            self.selected.append(parameters)
            rows=[r for r in self.rows if str(r['org_id'])==parameters['org'] and parameters['from_date']<=r['observation_date']<=parameters['to_date']]
            rows.sort(key=lambda r:(r['created_at'],str(r['capture_id'])),reverse=True)
            if parameters.get('last_id'):rows=[r for r in rows if (r['created_at'],str(r['capture_id']))<(parameters['last_created_at'],parameters['last_id'])]
            return history_support.Rows(copy.deepcopy(rows[:parameters['row_limit']]))
        return super().execute(sql,parameters)

class Pool(history_support.Pool):
    def __init__(self):
        super().__init__();self.connection=Connection();self.borrow=lambda:None;self.release=lambda:None
    @contextmanager
    def connect(self):
        self.borrow();self.borrows+=1
        try:yield self.connection
        finally:self.release();self.releases+=1

class AdminAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pool=Pool();self.checks=[]
        self.upstream=lambda:httpx.Response(200,json=evidence())
        async def access(request):
            self.assertFalse(self.pool.connection.in_transaction());self.checks.append(request);return self.upstream()
        with patch('sqlalchemy.create_engine',return_value=self.pool):
            if hasattr(boundary,'create_engine'):
                with patch.object(boundary,'create_engine',return_value=self.pool):self.app=self.make_app(access)
            else:self.app=self.make_app(access)
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='https://kdg.invalid')
    def make_app(self,access):
        return boundary.create_candidate(org_id=support.ORG,access_url='https://access.invalid',service_key='synthetic',database_url=history_support.DB_URL,transport=httpx.MockTransport(access))
    async def asyncTearDown(self):await self.client.aclose()
    async def get(self,url=DETAIL,**kwargs):
        kwargs.setdefault('headers',{'Authorization':'Bearer synthetic'})
        result=await self.client.request('GET',url,**kwargs)
        self.assertEqual(result.headers['cache-control'],'private, no-store')
        return result
    async def test_authorized_foreign_owner_detail_is_original_and_private(self):
        result=await self.get()
        self.assertEqual(result.status_code,200)
        self.assertEqual(result.json()['owner_account_id'],FOREIGN)
        self.assertEqual(result.json()['owner_actor_id'],support.ACTOR)
        self.assertEqual(result.json()['definition'],support.DEFINITION)
        self.assertEqual((len(self.checks),self.pool.borrows,self.pool.releases),(1,1,1))
    async def test_tied_pages_include_foreign_owners_and_recheck_every_page(self):
        import json
        seen=[];url=HISTORY
        self.pool.connection.rows[0]['owner_account_id']=UUID(support.ACCOUNT)
        self.pool.connection.rows.append({**copy.deepcopy(self.pool.connection.rows[0]),'org_id':UUID(FOREIGN)})
        for count in (2,2,1):
            result=await self.get(url);self.assertEqual(result.status_code,200)
            body=result.json();self.assertEqual(len(body['items']),count)
            self.assertEqual(set(body),{'org_id','account_id','from_date','to_date','limit','items','next_cursor'})
            seen.extend(item['capture_id'] for item in body['items'])
            self.assertTrue(all(item['definition']==support.DEFINITION for item in body['items']))
            cursor=body['next_cursor'];url=HISTORY+'&cursor='+cursor if cursor else HISTORY
        self.assertIsNone(cursor);self.assertEqual(len(set(seen)),5)
        self.assertEqual((len(self.checks),self.pool.borrows,self.pool.releases),(3,3,3))
        self.assertTrue(all(json.loads(check.content)['permission']==PERMISSION for check in self.checks))
        self.assertTrue(all(parameters['row_limit']==3 for parameters in self.pool.connection.selected))
    async def test_date_bounds_default_limit_and_empty_verified_envelope(self):
        from datetime import date
        self.pool.connection.rows[0]['observation_date']=date(2026,10,1)
        self.pool.connection.rows[1]['observation_date']=date(2026,9,30)
        result=await self.get(HISTORY.replace('&limit=2',''));self.assertEqual(result.status_code,200)
        self.assertEqual((len(result.json()['items']),result.json()['limit']),(4,30))
        result=await self.get(HISTORY.replace('2026-10-01','2020-01-01').replace('2026-10-26','2020-01-01'))
        self.assertEqual(result.json()['items'],[]);self.assertIsNone(result.json()['next_cursor'])
        self.assertEqual((result.json()['org_id'],result.json()['account_id']),(support.ORG,support.ACCOUNT))
    async def test_closed_query_ids_body_and_bearer_before_checkout(self):
        for url in (HISTORY+'&x=1',HISTORY+'&limit=2',HISTORY+'&cursor=bad',DETAIL+'?all_read=true',DETAIL.replace(support.CAPTURE,'bad'),'/api/v1/admin/captures',HISTORY.replace('2026-10-01','2026-10-27')):
            result=await self.get(url);self.assertEqual(result.status_code,422)
        for limit in ('0','101','01','-1','1.0','true','9999'):
            result=await self.get(HISTORY.replace('limit=2','limit='+limit));self.assertEqual(result.status_code,422)
        for url in (DETAIL,HISTORY):
            result=await self.get(url,content=b'private');self.assertEqual(result.status_code,422)
            for headers in ({},{'Authorization':'Basic synthetic'},[('authorization','Bearer a'),('Authorization','Bearer b')],{'Authorization':'Bearer a,b'},{'Authorization':'Bearer a!b'}):
                result=await self.get(url,headers=headers);self.assertEqual(result.status_code,401)
                self.assertEqual(result.headers['www-authenticate'],'Bearer')
        self.assertEqual((len(self.checks),self.pool.borrows),(0,0))
    async def test_denied_revoked_second_page_and_wrong_resource_never_checkout(self):
        first=await self.get(HISTORY);self.assertEqual(first.status_code,200)
        self.upstream=lambda:httpx.Response(403,json={'detail':{'code':'access_denied'}})
        result=await self.get(HISTORY+'&cursor='+first.json()['next_cursor'])
        self.assertEqual((result.status_code,result.json()['error_id']),(403,'access_denied'))
        self.assertEqual((len(self.checks),self.pool.borrows),(2,1))
        self.upstream=lambda:httpx.Response(200,json={**evidence(),'resource_scope':dict(kind='organization',org_id=FOREIGN)})
        result=await self.get();self.assertEqual(result.json()['error_id'],'authorization_unavailable');self.assertEqual(self.pool.borrows,1)
    async def test_cursor_bound_to_verified_account_org_dates_limit_and_mode(self):
        import admin_read as admin
        import capture_history as own
        first=await self.get(HISTORY);value=admin.decode_cursor(first.json()['next_cursor']).model_dump()
        for change in ({'account_id':FOREIGN},{'org_id':FOREIGN},{'permission':own.PERMISSION},{'from_date':'2026-09-01'},{'limit':3}):
            result=await self.get(HISTORY+'&cursor='+own._encode({**value,**change}));self.assertEqual(result.status_code,422)
        self.assertEqual(self.pool.borrows,1)
    async def test_missing_foreign_detail_and_corrupt_required_storage_are_safe(self):
        original=copy.deepcopy(self.pool.connection.detail)
        for value,status in ((None,404),({**original,'org_id':UUID(FOREIGN)},404),({**original,'capture_id':UUID(FOREIGN)},404),({**original,'definition':{}},503),({**original,'answers':{}},503)):
            self.pool.connection.detail=value
            result=await self.get();self.assertEqual(result.status_code,status)
        self.pool.connection.rows[-1]['answers']={}
        result=await self.get(HISTORY);self.assertEqual(result.status_code,503)
    async def test_checkout_freshness_and_release_fences_have_no_late_success(self):
        from types import SimpleNamespace
        import admin_read as admin
        for phase,expected in (('borrow','authorization_observation_expired'),('release','execution_timeout')):
            for url in (DETAIL,HISTORY):
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
        for url in (DETAIL,HISTORY):
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
        import admin_read as admin
        original_budget=admin.write.Budget
        def short():
            budget=original_budget();budget.deadline=budget.started_at+.06;return budget
        for url in (DETAIL,HISTORY):
            for cancel in (True,False):
                for phase in ('borrow','sql','release'):
                    self.pool=Pool();self.app.state.recovery_engine=self.pool
                    started,release=threading.Event(),threading.Event()
                    def pending():started.set();release.wait(2)
                    if phase=='sql':
                        original=self.pool.connection.execute
                        def execute(sql,params):
                            if 'FROM kdg_capture.capture c' in str(sql):pending()
                            return original(sql,params)
                        self.pool.connection.execute=execute
                    else:setattr(self.pool,phase,pending)
                    with patch.object(admin.write,'Budget',side_effect=short if not cancel else original_budget):
                        task=asyncio.create_task(self.get(url))
                        try:
                            for _ in range(200):
                                if started.is_set():break
                                await asyncio.sleep(.001)
                            self.assertTrue(started.is_set(),phase)
                            if cancel:task.cancel();await asyncio.sleep(.01);task.cancel()
                            await asyncio.sleep(.08);self.assertFalse(task.done(),phase)
                        finally:
                            release.set()
                            if cancel:
                                with self.assertRaises(asyncio.CancelledError):await task
                            else:
                                result=await task;self.assertEqual(result.json()['error_id'],'execution_timeout')
                        self.assertEqual(self.pool.releases,1)
    async def test_final_serialization_expiry_blocks_detail_and_history(self):
        from types import SimpleNamespace
        import admin_read as admin
        for url,model in ((DETAIL,admin.CaptureDetail),(HISTORY,admin.AdminHistoryPage)):
            now=100.0;calls=0;original=model.model_dump_json
            def serialize(value,*args,**kwargs):
                nonlocal now,calls
                result=original(value,*args,**kwargs);calls+=1
                if (model is admin.CaptureDetail and calls==2) or (model is admin.AdminHistoryPage and calls==3):now=111.0
                return result
            with patch.object(admin.write,'time',SimpleNamespace(monotonic=lambda:now)),patch.object(model,'model_dump_json',serialize):result=await self.get(url)
            self.assertEqual(result.json()['error_id'],'execution_timeout')
    async def test_private_routing_lazy_pool_policy_lifespan_and_no_activation(self):
        import importlib.util
        for method,url,status in (('POST',DETAIL,405),('GET','/missing',404),('GET',DETAIL+'/',404),('GET','/api/v1/captures',404)):
            result=await self.client.request(method,url);self.assertEqual(result.status_code,status)
            self.assertEqual(result.headers['cache-control'],'private, no-store')
        self.assertFalse(hasattr(boundary,'app'));self.assertEqual(self.pool.borrows,0)
        for exceptional in (True,False):
            before=self.pool.disposed
            try:
                async with self.app.router.lifespan_context(self.app):
                    if exceptional:raise RuntimeError('synthetic')
            except RuntimeError:pass
            self.assertEqual(self.pool.disposed,before+1)
        with patch.object(boundary,'create_engine',return_value=self.pool) as factory:boundary._engine(history_support.DB_URL)
        options=factory.call_args.kwargs
        self.assertEqual((options['pool_timeout'],options['max_overflow'],options['pool_pre_ping']),(.25,0,False))
        self.assertEqual(options['connect_args']['connect_timeout'],3)
        self.assertIn('default_transaction_read_only=on',options['connect_args']['options'])
        path=support.support.ROOT/'apps/kdg-capture/api/main.py'
        spec=importlib.util.spec_from_file_location('admin_activation_check',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.assertTrue(all('/admin/captures' not in path for path in module.app.openapi()['paths']))
    async def test_actual_utf8_detail_limit_and_page_truncation_without_skip(self):
        import admin_read as admin
        ids=[f'{n:08x}-bbbb-4bbb-8bbb-{n:012x}' for n in range(1,31)]
        stored=copy.deepcopy(self.pool.connection.detail)
        stored.update(definition=dict(schema_version=1,questions=[dict(id=i,type='text',label='漢',required=True) for i in ids]),answers={i:{'value':'x'} for i in ids})
        context=admin.write.VerifiedContext(support.ORG,support.ACCOUNT,support.ACTOR,'all_read',100)
        base=len(admin._snapshot(stored,context,admin.Lookup(capture_id=support.CAPTURE)).model_dump_json().encode('utf-8'))
        remaining=512*1024-base
        for key in ids:
            added=min(remaining,19996);emoji,ascii_bytes=divmod(added,4)
            stored['answers'][key]['value']='x'+'😀'*emoji+'a'*ascii_bytes;remaining-=added
        self.assertEqual(remaining,0);self.pool.connection.detail=stored
        result=await self.get();self.assertEqual(result.status_code,200);self.assertEqual(len(result.content),512*1024)
        self.pool.connection.rows=[{**copy.deepcopy(stored),'capture_id':r['capture_id']} for r in self.pool.connection.rows]
        result=await self.get(HISTORY.replace('limit=2','limit=5'));self.assertEqual(result.status_code,200)
        self.assertEqual(len(result.json()['items']),3);self.assertLessEqual(len(result.content),2*1024*1024)
        seen=[item['capture_id'] for item in result.json()['items']]
        next_page=await self.get(HISTORY.replace('limit=2','limit=5')+'&cursor='+result.json()['next_cursor'])
        self.assertEqual(next_page.status_code,200);seen.extend(item['capture_id'] for item in next_page.json()['items'])
        self.assertEqual(len(set(seen)),5);self.assertIsNone(next_page.json()['next_cursor'])
        stored['answers'][ids[-1]]['value']+='a'
        result=await self.get();self.assertEqual(result.json()['error_id'],'capture_read_unavailable')
    async def test_actual_page_exact_two_mib_and_one_byte_over_resumes_last_included(self):
        import admin_read as admin
        ids=[f'{n:08x}-bbbb-4bbb-8bbb-{n:012x}' for n in range(1,27)]
        for row in self.pool.connection.rows:
            row.update(definition=dict(schema_version=1,questions=[dict(id=i,type='text',label='T',required=True) for i in ids]),answers={i:{'value':'😀'*5000 if i!=ids[-1] else 'x'} for i in ids})
        context=admin.write.VerifiedContext(support.ORG,support.ACCOUNT,support.ACTOR,'all_read',100)
        query=admin.Query(from_date='2026-10-01',to_date='2026-10-26',limit=100)
        def intended():
            details=[admin._snapshot(row,context,admin.Lookup(capture_id=str(row['capture_id']))) for row in reversed(self.pool.connection.rows)]
            return admin.AdminHistoryPage(org_id=support.ORG,account_id=support.ACCOUNT,from_date=query.from_date,to_date=query.to_date,limit=100,items=details[:4],next_cursor=admin.continuation(query,context,details[3]))
        remaining=2*1024*1024-len(intended().model_dump_json().encode('utf-8'))
        self.assertGreater(remaining,0)
        for row in list(reversed(self.pool.connection.rows))[:4]:
            size=len(admin._snapshot(row,context,admin.Lookup(capture_id=str(row['capture_id']))).model_dump_json().encode('utf-8'))
            added=min(remaining,512*1024-size,19996);emoji,ascii_bytes=divmod(added,4)
            row['answers'][ids[-1]]['value']='x'+'😀'*emoji+'a'*ascii_bytes;remaining-=added
        self.assertEqual(remaining,0)
        url=HISTORY.replace('limit=2','limit=100')
        exact=await self.get(url);self.assertEqual(exact.status_code,200)
        self.assertEqual(len(exact.content),2*1024*1024);self.assertEqual(len(exact.json()['items']),4)
        list(reversed(self.pool.connection.rows))[3]['child_label']+='a'
        overflow=await self.get(url);self.assertEqual(overflow.status_code,200);self.assertEqual(len(overflow.json()['items']),3)
        resumed=await self.get(url+'&cursor='+overflow.json()['next_cursor']);self.assertEqual(resumed.status_code,200)
        self.assertEqual([item['capture_id'] for item in overflow.json()['items']+resumed.json()['items']],sorted([str(row['capture_id']) for row in self.pool.connection.rows],reverse=True))
    async def test_access_and_stream_timeouts_before_checkout(self):
        import asyncio
        import admin_read as admin
        original=admin.write.Budget
        def short():
            budget=original();budget.deadline=budget.started_at+.02;return budget
        async def body():await asyncio.sleep(.06);yield b''
        for url in (DETAIL,HISTORY):
            with patch.object(admin.write,'Budget',side_effect=short):result=await self.get(url,content=body())
            self.assertEqual(result.json()['error_id'],'execution_timeout')
        self.assertEqual((len(self.checks),self.pool.borrows),(0,0))
        async def delayed(request):await asyncio.sleep(.06);return httpx.Response(200,json=evidence())
        with patch.object(admin.protected,'ACCESS_SECONDS',.02):
            with patch.object(boundary,'create_engine',return_value=self.pool):self.app=self.make_app(delayed)
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='https://kdg.invalid') as client:
                for url in (DETAIL,HISTORY):
                    result=await client.get(url,headers={'Authorization':'Bearer synthetic'})
                    self.assertEqual(result.json()['error_id'],'authorization_unavailable')
                    self.assertEqual(result.headers['cache-control'],'private, no-store')
        self.assertEqual(self.pool.borrows,0)
    async def test_inactive_child_and_removed_assignments_preserve_historical_reads(self):
        connection=self.pool.connection
        connection.child=dict(active=False)
        connection.eligibility=None
        connection.assignment=None
        connection.replay_assignment=None
        detail=await self.get()
        page=await self.get(HISTORY)
        self.assertEqual((detail.status_code,page.status_code),(200,200))
        self.assertEqual(detail.json()['owner_account_id'],FOREIGN)
        self.assertEqual(detail.json()['definition'],support.DEFINITION)
        self.assertEqual(len(page.json()['items']),2)
        self.assertTrue(all(item['owner_account_id']==FOREIGN and item['definition']==support.DEFINITION for item in page.json()['items']))
        self.assertEqual((len(self.checks),self.pool.borrows,self.pool.releases),(2,2,2))
    async def test_pending_body_and_access_cancellation_is_prompt_without_checkout(self):
        import asyncio
        for url in (DETAIL,HISTORY):
            for phase in ('body','access'):
                started,release,unwound=asyncio.Event(),asyncio.Event(),asyncio.Event()
                async def gated_body():
                    try:
                        started.set();await release.wait();yield b''
                    finally:unwound.set()
                async def gated_access(request):
                    try:
                        started.set();await release.wait()
                        return httpx.Response(200,json=evidence())
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
