"""Synthetic actual-route acceptance; never native database qualification."""
import copy
from datetime import date, datetime, timedelta, timezone
from contextlib import contextmanager
import unittest
from unittest.mock import patch
from uuid import UUID
import httpx
import test_capture_read as support
import history_http as boundary

URL='/api/v1/captures?from_date=2026-10-01&to_date=2026-10-26&limit=2'
DB_URL='postgresql+psycopg://synthetic:synthetic@127.0.0.1:55482/synthetic'

class Rows:
    def __init__(self,rows):self.rows=rows
    def mappings(self):return self
    def all(self):return self.rows

class Connection(support.Connection):
    def __init__(self):
        super().__init__()
        self.rows=[]
        for n in range(5):
            row=support.row();row['capture_id']=UUID(f'{n+1:08x}-aaaa-4aaa-8aaa-{n+1:012x}')
            row['created_at']=datetime(2026,10,26,tzinfo=timezone.utc)
            self.rows.append(row)
        self.selected=[]
    def execute(self,sql,parameters):
        if 'ORDER BY c.created_at DESC,c.id DESC' in str(sql):
            self.calls.append((str(sql),parameters));self.selected.append(parameters)
            rows=[r for r in self.rows if str(r['org_id'])==parameters['org'] and str(r['owner_account_id'])==parameters['account'] and parameters['from_date']<=r['observation_date']<=parameters['to_date']]
            rows.sort(key=lambda r:(r['created_at'],str(r['capture_id'])),reverse=True)
            if parameters.get('last_id'):
                rows=[r for r in rows if (r['created_at'],str(r['capture_id']))<(parameters['last_created_at'],parameters['last_id'])]
            return Rows(copy.deepcopy(rows[:parameters['row_limit']]))
        return super().execute(sql,parameters)

class Pool:
    def __init__(self):self.connection=Connection();self.borrows=0;self.releases=0;self.disposed=0
    @contextmanager
    def connect(self):
        self.borrows+=1
        try:yield self.connection
        finally:self.releases+=1
    def dispose(self):self.disposed+=1

class HistoryAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pool=Pool();self.checks=[]
        self.upstream=lambda:httpx.Response(200,json=support.support.evidence(support.read.recovery.PERMISSION))
        async def access(request):self.checks.append(request);return self.upstream()
        # Stub ignores collaborators, so RED remains a behavioral HTTP assertion.
        with patch('sqlalchemy.create_engine',return_value=self.pool):
            if hasattr(boundary,'create_engine'):
                with patch.object(boundary,'create_engine',return_value=self.pool):self.app=self.make_app(access)
            else:self.app=self.make_app(access)
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='https://kdg.invalid')
    def make_app(self,access):
        return boundary.create_candidate(org_id=support.ORG,access_url='https://access.invalid',service_key='synthetic-key',database_url=DB_URL,transport=httpx.MockTransport(access))
    async def asyncTearDown(self):await self.client.aclose()
    async def get(self,url=URL,**kwargs):
        kwargs.setdefault('headers',{'Authorization':'Bearer synthetic'})
        result=await self.client.request('GET',url,**kwargs)
        self.assertEqual(result.headers['cache-control'],'private, no-store')
        return result
    async def test_traverse_tied_original_history_without_loss(self):
        seen=[];url=URL
        for count in (2,2,1):
            result=await self.get(url)
            self.assertEqual(result.status_code,200)
            body=result.json();self.assertEqual(len(body['items']),count)
            self.assertEqual((body['from_date'],body['to_date'],body['limit']),('2026-10-01','2026-10-26',2))
            seen.extend(item['capture_id'] for item in body['items'])
            self.assertTrue(all(item['definition']==support.DEFINITION for item in body['items']))
            cursor=body['next_cursor'];url=URL+'&cursor='+cursor if cursor else URL
        self.assertIsNone(cursor)
        self.assertEqual(seen,sorted([str(r['capture_id']) for r in self.pool.connection.rows],reverse=True))
        self.assertEqual((len(self.checks),self.pool.borrows,self.pool.releases),(3,3,3))
    async def test_closed_query_is_refused_before_authority(self):
        for suffix in ('&x=1','&limit=2','&cursor=bad'):
            result=await self.get(URL+suffix)
            self.assertEqual((result.status_code,result.json()['error_id']),(422,'validation_failed'))
        self.assertEqual((len(self.checks),self.pool.borrows),(0,0))

    async def test_explicit_inclusive_dates_default_limit_and_empty_scope(self):
        self.pool.connection.rows[0]['observation_date']=date(2026,10,1)
        self.pool.connection.rows[1]['observation_date']=date(2026,9,30)
        response=await self.get(URL.replace('&limit=2',''))
        self.assertEqual(response.status_code,200)
        body=response.json();self.assertEqual(body['limit'],30);self.assertEqual(len(body['items']),4)
        self.assertEqual((body['org_id'],body['account_id']),(support.ORG,support.ACCOUNT))
        response=await self.get('/api/v1/captures?from_date=2020-01-01&to_date=2020-01-01')
        self.assertEqual(response.json()['items'],[]);self.assertIsNone(response.json()['next_cursor'])
        self.assertEqual(response.json()['account_id'],support.ACCOUNT)
    async def test_invalid_query_dates_limits_and_size_before_authority(self):
        for query in ('','from_date=2026-10-01','from_date=2026-10-27&to_date=2026-10-26',
          'from_date=2026-02-30&to_date=2026-10-26','from_date=0000-01-01&to_date=2026-10-26'):
            result=await self.get('/api/v1/captures?'+query);self.assertEqual(result.status_code,422)
        for limit in ('0','101','01','-1','1.0','true','999999'):
            self.assertEqual((await self.get(URL.replace('limit=2','limit='+limit))).status_code,422)
        self.assertEqual((await self.get(URL+'&x='+'a'*8192)).status_code,422)
        self.assertEqual((self.pool.borrows,len(self.checks)),(0,0))
    async def test_exact_bearer_and_nonempty_body_before_authority(self):
        for headers in ({},{'Authorization':'Basic private'},[('authorization','Bearer a'),('Authorization','Bearer b')],{'Authorization':'Bearer a,b'},{'Authorization':'Bearer a!b'}):
            r=await self.get(headers=headers);self.assertEqual(r.status_code,401);self.assertEqual(r.headers['www-authenticate'],'Bearer')
        self.assertEqual((await self.get(content=b'private')).status_code,422)
        self.assertEqual((self.pool.borrows,len(self.checks)),(0,0))
    async def test_cursor_binding_is_checked_after_current_authority_before_checkout(self):
        import capture_history as history
        first=(await self.get()).json()['next_cursor'];value=history.decode_cursor(first).model_dump()
        for change in ({'org_id':support.IDS[0]},{'account_id':support.IDS[0]},{'from_date':'2026-09-01'},{'to_date':'2026-10-25'},{'limit':3}):
            cursor=history._encode({**value,**change});self.pool.borrows=0
            result=await self.get(URL+'&cursor='+cursor);self.assertEqual(result.status_code,422);self.assertEqual(self.pool.borrows,0)
    async def test_changed_position_only_navigates_current_authorized_query(self):
        import capture_history as history
        self.pool.connection.rows[0]['owner_account_id']=UUID(support.IDS[0])
        self.pool.connection.rows[1]['org_id']=UUID(support.IDS[0])
        self.pool.connection.rows[2]['observation_date']=date(2025,1,1)
        first=(await self.get()).json();cursor=history.continuation(history.Query(from_date='2026-10-01',to_date='2026-10-26',limit=2),
            history.write.VerifiedContext(support.ORG,support.ACCOUNT,support.ACTOR,'own_read',100),history.read._snapshot(support.row(),
            history.write.VerifiedContext(support.ORG,support.ACCOUNT,support.ACTOR,'own_read',100),history.read.Lookup(capture_id=support.CAPTURE)))
        value=history.decode_cursor(cursor).model_dump();value.update(last_created_at='9999-12-31T23:59:59Z',last_id=support.IDS[0])
        result=await self.get(URL+'&cursor='+history._encode(value));self.assertEqual(result.status_code,200)
        self.assertEqual([i['capture_id'] for i in result.json()['items']],[i['capture_id'] for i in first['items']])
        sql=history.HISTORY
        for predicate in ('c.org_id=CAST(:org AS uuid)','c.owner_account_id=CAST(:account AS uuid)','c.observation_date>=CAST(:from_date AS date)','c.observation_date<=CAST(:to_date AS date)','CAST(:last_id AS uuid) IS NULL'):
            self.assertIn(predicate,sql)
        self.assertEqual(self.pool.connection.selected[-1]['row_limit'],3)
    async def test_every_page_rechecks_denial_actor_setup_and_outage(self):
        cursor=(await self.get()).json()['next_cursor'];self.pool.borrows=0
        for status,code,expected in ((403,'access_denied','access_denied'),(401,'authentication_required','authentication_required'),(409,'identity.actor_setup_required','identity.actor_setup_required'),(503,'private','authorization_unavailable')):
            self.upstream=lambda:httpx.Response(status,json={'detail':{'code':code}})
            result=await self.get(URL+'&cursor='+cursor);self.assertEqual(result.json()['error_id'],expected)
        self.upstream=lambda:httpx.Response(200,json={**support.support.evidence(support.read.recovery.PERMISSION),'actor_id':None})
        self.assertNotEqual((await self.get(URL+'&cursor='+cursor)).status_code,200)
        self.assertEqual(self.pool.borrows,0)
    async def test_current_revision_original_definition_after_edit_and_unassignment(self):
        cursor=(await self.get()).json()['next_cursor']
        self.pool.connection.rows[0]['revision']=2;self.pool.connection.replay_assignment=None
        result=await self.get(URL+'&cursor='+cursor)
        self.assertEqual(result.status_code,200)
        # Refresh sees the updated current revision; original definition remains unchanged.
        result=await self.get(URL.replace('limit=2','limit=100'))
        self.assertEqual(result.json()['items'][-1]['revision'],'2')
        self.assertTrue(all(i['definition']==support.DEFINITION for i in result.json()['items']))
        self.assertFalse(any('FOR UPDATE' in sql or sql.startswith(('UPDATE','INSERT','DELETE')) for sql,_ in self.pool.connection.calls))
    async def test_bad_storage_never_publishes_partial_page(self):
        for change in ({'revision':0},{'answers':{}},{'created_by':UUID(support.IDS[0])},{'created_at':datetime(2026,10,26)},{'definition':{}}):
            self.pool.connection.rows[-1]={**support.row(),'capture_id':self.pool.connection.rows[-1]['capture_id'],**change}
            result=await self.get();self.assertEqual(result.status_code,503);self.assertNotIn('items',result.json())
    async def test_byte_limited_pages_resume_without_skipping(self):
        ids=[f'{n:08x}-bbbb-4bbb-8bbb-{n:012x}' for n in range(1,26)]
        for row in self.pool.connection.rows:
            row.update(definition=dict(schema_version=1,questions=[dict(id=i,type='text',label='Text',required=True) for i in ids]),answers={i:{'value':'😀'*5000} for i in ids})
        url=URL.replace('limit=2','limit=100');result=await self.get(url)
        self.assertEqual(result.status_code,200);self.assertLessEqual(len(result.content),2*1024*1024)
        body=result.json();self.assertEqual(len(body['items']),4);self.assertIsNotNone(body['next_cursor'])
        next_page=await self.get(url+'&cursor='+body['next_cursor']);self.assertEqual(next_page.status_code,200)
        self.assertEqual(len(next_page.json()['items']),1);self.assertIsNone(next_page.json()['next_cursor'])
        self.assertEqual(len({i['capture_id'] for i in body['items']+next_page.json()['items']}),5)
    async def test_microseconds_precede_inverse_uuid_order(self):
        self.pool.connection.rows=self.pool.connection.rows[:2]
        self.pool.connection.rows[0]['created_at']=datetime(2026,10,26,0,0,0,2,tzinfo=timezone.utc)
        self.pool.connection.rows[1]['created_at']=datetime(2026,10,26,0,0,0,1,tzinfo=timezone.utc)
        url=URL.replace('limit=2','limit=1');a=await self.get(url);self.assertEqual(a.status_code,200)
        b=await self.get(url+'&cursor='+a.json()['next_cursor']);self.assertEqual(b.status_code,200)
        self.assertEqual([a.json()['items'][0]['capture_id'],b.json()['items'][0]['capture_id']],[str(r['capture_id']) for r in self.pool.connection.rows])
    async def test_failure_in_checkout_sql_commit_or_release_is_safe(self):
        from sqlalchemy.exc import OperationalError
        for phase in ('borrow','sql','commit','release'):
            pool=Pool()
            def fail():raise OperationalError('private-history',{},Exception('private-driver'))
            if phase=='commit':pool.connection.fail_commit=True
            elif phase=='sql':
                original=pool.connection.execute
                def execute(sql,p):
                    if (phase=='sql' and str(sql)==boundary.recovery.HISTORY) or (phase=='commit' and str(sql)=='COMMIT'):fail()
                    return original(sql,p)
                pool.connection.execute=execute
            else:
                @contextmanager
                def connect():
                    if phase=='borrow':fail()
                    try:yield pool.connection
                    finally:
                        if phase=='release':fail()
                pool.connect=connect
            self.app.state.recovery_engine=pool
            result=await self.get();self.assertEqual(result.status_code,503);self.assertNotIn('private-',result.text)
    async def test_release_and_final_serialization_share_original_deadline(self):
        from types import SimpleNamespace
        history=boundary.recovery;original=history.HistoryPage.model_dump_json
        now=100.0;calls=0
        def dump(page,*a,**k):
            nonlocal now,calls
            result=original(page,*a,**k);calls+=1
            if calls==3:now=111.0
            return result
        with patch.object(history.write,'time',SimpleNamespace(monotonic=lambda:now)),patch.object(history.HistoryPage,'model_dump_json',dump):
            result=await self.get()
        self.assertEqual(result.json()['error_id'],'execution_timeout');self.assertEqual(calls,3)
    async def test_expiry_and_cancellation_retain_worker_ownership(self):
        import asyncio,threading
        history=boundary.recovery;original_budget=history.write.Budget
        for cancel in (False,True):
            for phase in ('borrow','sql','release'):
                pool=Pool();started=threading.Event();release=threading.Event();budgets=[]
                def pending():started.set();release.wait(5)
                if phase=='sql':
                    original=pool.connection.execute
                    def execute(sql,p):
                        if str(sql)==history.HISTORY:pending()
                        return original(sql,p)
                    pool.connection.execute=execute
                else:
                    @contextmanager
                    def connect():
                        if phase=='borrow':pending()
                        pool.borrows+=1
                        try:yield pool.connection
                        finally:
                            if phase=='release':pending()
                            pool.releases+=1
                    pool.connect=connect
                def controlled():
                    budget=original_budget();budgets.append(budget);return budget
                self.app.state.recovery_engine=pool
                with patch.object(history.write,'Budget',side_effect=controlled):
                    task=asyncio.create_task(self.get())
                    try:
                        self.assertTrue(await asyncio.to_thread(started.wait,2),phase)
                        # Expire only after the intended worker phase is reached;
                        # authorization/scheduling time cannot choose another phase.
                        self.assertEqual(len(budgets),1)
                        budgets[0].deadline=budgets[0].started_at-1
                        with self.assertRaisesRegex(history.write.WriteError,'execution_timeout'):
                            budgets[0].remaining()
                        if cancel:task.cancel();await asyncio.sleep(.01);task.cancel()
                        await asyncio.sleep(.01);self.assertFalse(task.done(),phase)
                    finally:
                        release.set()
                        if cancel:
                            with self.assertRaises(asyncio.CancelledError):await task
                        else:self.assertEqual((await task).json()['error_id'],'execution_timeout')
                self.assertEqual(pool.releases,1)

    async def test_actual_page_exact_utf8_2mib_then_one_byte_changes_continuation(self):
        import capture_history as history
        ids=[f'{n:08x}-bbbb-4bbb-8bbb-{n:012x}' for n in range(1,27)]
        for row in self.pool.connection.rows:
            row.update(definition=dict(schema_version=1,questions=[dict(id=i,type='text',label='T',required=True) for i in ids]),answers={i:{'value':'😀'*5000 if i!=ids[-1] else 'x'} for i in ids})
        context=history.write.VerifiedContext(support.ORG,support.ACCOUNT,support.ACTOR,'own_read',100)
        query=history.Query(from_date='2026-10-01',to_date='2026-10-26',limit=100)
        def intended():
            details=[history.read._snapshot(row,context,history.read.Lookup(capture_id=str(row['capture_id']))) for row in reversed(self.pool.connection.rows)]
            evidence=history.Context.model_validate(support.support.evidence(history.PERMISSION))
            observation=history.OwnReadObservation.model_validate({**evidence.model_dump(mode='json'),'expires_at':evidence.checked_at+timedelta(days=7)})
            return history.HistoryPage(observation=observation,org_id=support.ORG,account_id=support.ACCOUNT,from_date=query.from_date,to_date=query.to_date,limit=100,items=details[:4],next_cursor=history.continuation(query,context,details[3]))
        remaining=2*1024*1024-len(intended().model_dump_json().encode('utf-8'))
        self.assertGreater(remaining,0)
        for row in list(reversed(self.pool.connection.rows))[:4]:
            current=len(history.read._snapshot(row,context,history.read.Lookup(capture_id=str(row['capture_id']))).model_dump_json().encode('utf-8'))
            add=min(remaining,512*1024-current,19996)
            emoji,ascii_bytes=divmod(add,4);row['answers'][ids[-1]]['value']='x'+'😀'*emoji+'a'*ascii_bytes;remaining-=add
        self.assertEqual(remaining,0)
        self.assertEqual(len(intended().model_dump_json().encode('utf-8')),2*1024*1024)
        url=URL.replace('limit=2','limit=100')
        exact=await self.get(url);self.assertEqual(exact.status_code,200);self.assertEqual(len(exact.content),2*1024*1024);self.assertEqual(len(exact.json()['items']),4)
        # The fourth detail still fits512KiB; the envelope now forces an earlier continuation.
        fourth=list(reversed(self.pool.connection.rows))[3];fourth['child_label']+='a'
        overflow=await self.get(url);self.assertEqual(overflow.status_code,200);self.assertEqual(len(overflow.json()['items']),3)
        resumed=await self.get(url+'&cursor='+overflow.json()['next_cursor']);self.assertEqual(resumed.status_code,200)
        self.assertEqual([i['capture_id'] for i in overflow.json()['items']+resumed.json()['items']],sorted([str(r['capture_id']) for r in self.pool.connection.rows],reverse=True))

    async def test_cancelled_worker_failure_never_enters_loop_diagnostics(self):
        import asyncio,threading
        from sqlalchemy.exc import OperationalError
        history=boundary.recovery;started=threading.Event();release=threading.Event();contexts=[]
        original=self.pool.connection.execute
        def execute(sql,p):
            if str(sql)==history.HISTORY:
                started.set();release.wait(2)
                raise OperationalError('SELECT synthetic_private_sql',{'private':'synthetic_history_cancel_canary'},Exception('synthetic_private_driver'))
            return original(sql,p)
        self.pool.connection.execute=execute
        loop=asyncio.get_running_loop();previous=loop.get_exception_handler()
        loop.set_exception_handler(lambda owner,context:contexts.append(context))
        try:
            task=asyncio.create_task(self.get())
            try:
                for _ in range(200):
                    if started.is_set():break
                    await asyncio.sleep(.001)
                self.assertTrue(started.is_set());task.cancel();await asyncio.sleep(.01);task.cancel();await asyncio.sleep(.01)
                self.assertFalse(task.done());self.assertEqual(self.pool.releases,0)
            finally:
                release.set()
                with self.assertRaises(asyncio.CancelledError):await task
            await asyncio.sleep(0)
            self.assertEqual(self.pool.releases,1)
            self.assertEqual(contexts,[],str([str(item.get('exception')) for item in contexts]))
        finally:loop.set_exception_handler(previous)

    async def test_cancelled_release_failure_never_logs_raw_sql_canary(self):
        import asyncio,threading,logging
        from sqlalchemy.exc import OperationalError
        started=threading.Event();release=threading.Event();contexts=[];records=[];pool=self.pool
        @contextmanager
        def connect():
            pool.borrows+=1
            try:yield pool.connection
            finally:
                started.set();release.wait(2);pool.releases+=1
                raise OperationalError('SELECT synthetic_private_sql',{'private':'synthetic_history_cancel_canary'},Exception('synthetic_private_driver'))
        pool.connect=connect
        loop=asyncio.get_running_loop();previous=loop.get_exception_handler()
        loop.set_exception_handler(lambda owner,context:contexts.append(context))
        class Capture(logging.Handler):
            def emit(self,record):records.append(self.format(record))
        logger=logging.getLogger('asyncio');capture=Capture();logger.addHandler(capture)
        try:
            task=asyncio.create_task(self.get())
            try:
                for _ in range(200):
                    if started.is_set():break
                    await asyncio.sleep(.001)
                self.assertTrue(started.is_set());task.cancel();await asyncio.sleep(.01);task.cancel();await asyncio.sleep(.01)
                self.assertFalse(task.done());self.assertEqual(pool.releases,0)
            finally:
                release.set()
                with self.assertRaises(asyncio.CancelledError):await task
            await asyncio.sleep(0)
            self.assertEqual(pool.releases,1)
            diagnostic=str([str(item.get('exception')) for item in contexts])+str(records)
            self.assertNotIn('synthetic_history_cancel_canary',diagnostic)
            self.assertEqual(contexts,[]);self.assertEqual(records,[])
        finally:loop.set_exception_handler(previous);logger.removeHandler(capture)

    async def test_checkout_cannot_renew_observation_and_release_remains_in_budget(self):
        from types import SimpleNamespace
        now=100.0;pool=self.pool
        @contextmanager
        def connect():
            nonlocal now
            pool.borrows+=1;now=102.0
            try:yield pool.connection
            finally:pool.releases+=1
        pool.connect=connect
        with patch.object(boundary.write,'time',SimpleNamespace(monotonic=lambda:now)):
            result=await self.get()
        self.assertEqual(result.json()['error_id'],'authorization_observation_expired');self.assertEqual(pool.connection.calls,[]);self.assertEqual(pool.releases,1)
        pool=Pool();self.app.state.recovery_engine=pool;now=100.0
        @contextmanager
        def late_release():
            nonlocal now
            pool.borrows+=1
            try:yield pool.connection
            finally:now=111.0;pool.releases+=1
        pool.connect=late_release
        with patch.object(boundary.write,'time',SimpleNamespace(monotonic=lambda:now)):
            result=await self.get()
        self.assertEqual(result.json()['error_id'],'execution_timeout');self.assertNotIn('items',result.json());self.assertEqual(pool.releases,1)
    async def test_candidate_remains_unmounted_private_and_disposes_owned_pool(self):
        import importlib.util
        for method,url,status in (('POST','/api/v1/captures',405),('GET','/api/v1/captures/',404),('GET','/missing',404)):
            result=await self.client.request(method,url);self.assertEqual(result.status_code,status);self.assertEqual(result.headers['cache-control'],'private, no-store')
        spec=importlib.util.spec_from_file_location('history_active_route_check',support.support.ROOT/'apps/kdg-capture/api/main.py')
        active=importlib.util.module_from_spec(spec);spec.loader.exec_module(active)
        self.assertNotIn('/api/v1/captures',active.app.openapi()['paths']);self.assertFalse(hasattr(boundary,'app'))
        async with self.app.router.lifespan_context(self.app):self.assertEqual(self.pool.disposed,0)
        self.assertEqual(self.pool.disposed,1)

    async def test_page_construction_runs_after_read_transaction_closes(self):
        history=boundary.recovery;original=history._page;observed=[]
        def page(rows,budget,context,query,evidence):
            observed.append(self.pool.connection.in_transaction())
            self.assertEqual(self.pool.connection.calls[-1][0],'COMMIT')
            return original(rows,budget,context,query,evidence)
        with patch.object(history,'_page',side_effect=page):result=await self.get()
        self.assertEqual(result.status_code,200);self.assertEqual(observed,[False])
    async def test_continuation_rechecks_current_dates_and_refresh_finds_newer_insertion(self):
        first=await self.get();self.assertEqual(first.status_code,200)
        first_page=first.json();self.assertEqual(len(first_page['items']),2)
        changed=self.pool.connection.rows[2]
        changed['observation_date']=date(2026,9,30)
        inserted={**support.row(),'capture_id':UUID('99999999-aaaa-4aaa-8aaa-999999999999'),
            'created_at':datetime(2026,10,27,tzinfo=timezone.utc)}
        self.pool.connection.rows.append(inserted)
        continued=await self.get(URL+'&cursor='+first_page['next_cursor']);self.assertEqual(continued.status_code,200)
        current=continued.json();continued_ids=[i['capture_id'] for i in current['items']]
        self.assertEqual(continued_ids,[str(self.pool.connection.rows[1]['capture_id']),str(self.pool.connection.rows[0]['capture_id'])])
        self.assertIsNone(current['next_cursor'])
        self.assertNotIn(str(changed['capture_id']),continued_ids);self.assertNotIn(str(inserted['capture_id']),continued_ids)
        self.assertTrue(any(r['capture_id']==changed['capture_id'] for r in self.pool.connection.rows))
        refreshed=await self.get(URL.replace('limit=2','limit=100'));self.assertEqual(refreshed.status_code,200)
        refresh_ids=[i['capture_id'] for i in refreshed.json()['items']]
        self.assertEqual(refresh_ids[0],str(inserted['capture_id']));self.assertNotIn(str(changed['capture_id']),refresh_ids)
        self.assertFalse(any('operation_outcome' in sql or sql.startswith(('INSERT','UPDATE','DELETE')) for sql,_ in self.pool.connection.calls))
        self.assertTrue(all('status' not in item and 'operation_id' not in item for item in refreshed.json()['items']))
