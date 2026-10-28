"""Actual synthetic HTTP composition; injected authority/storage, no native claim."""
import asyncio
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from uuid import UUID
import httpx
import test_audit_http as base
import audit_display_http as boundary
import audit_display as aggregate
import identity_actor_display as consumer

PATH=base.PATH.replace('/events','/audit-details')
KEY='synthetic-display-service-key-0001'
ORG=base.wire.support.ORG

class CompositionAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.pool=base.Pool();self.access_calls=[];self.identity_calls=[]
        self.authority_response=lambda:httpx.Response(200,json=base.wire.evidence())
        self.identity_response=None
        async def access(request):
            self.assertFalse(self.pool.connection.in_transaction());self.access_calls.append(request)
            return self.authority_response()
        async def identity(request):
            self.assertEqual((self.pool.borrows,self.pool.releases),(1,1))
            self.assertFalse(self.pool.connection.in_transaction());self.identity_calls.append(request)
            self.assertEqual(str(request.url),'https://identity.invalid/v2/identity/actor-displays')
            self.assertEqual(request.headers['x-service-key'],KEY)
            self.assertNotIn('authorization',request.headers)
            data=json.loads(request.content)
            self.assertEqual(data['org_id'],ORG)
            return self.identity_response(data) if self.identity_response else httpx.Response(200,json={'org_id':ORG,'labels':[{'actor_id':actor,'status':'resolved','display_name':'Retained <name>'} for actor in data['actor_ids']]},headers={'Cache-Control':'private, no-store'})
        self.access=access;self.identity=identity
        self.app=self.make_app()
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='https://kdg.invalid')
    def make_app(self,identity=None):
        with patch.object(base.boundary,'create_engine',return_value=self.pool):
            return boundary.create_candidate(org_id=ORG,access_url='https://access.invalid',service_key='synthetic',database_url=base.wire.history_support.DB_URL,identity_url='https://identity.invalid',identity_service_key=KEY,transport=httpx.MockTransport(self.access),identity_transport=httpx.MockTransport(identity or self.identity))
    async def asyncTearDown(self):await self.client.aclose()
    async def get(self,url=PATH,**kwargs):
        kwargs.setdefault('headers',{'Authorization':'Bearer synthetic'})
        reply=await self.client.request('GET',url,**kwargs)
        self.assertEqual(reply.headers['cache-control'],'private, no-store')
        return reply
    async def test_authorized_audit_details(self):
        reply=await self.get();self.assertEqual(reply.status_code,200)
        data=reply.json();self.assertEqual(set(data),{'audit','actor_display'})
        self.assertEqual(data['actor_display']['status'],'loaded')
        page=base.audit.AuditPage.model_validate(data['audit'])
        expected=aggregate.selected_actor_ids(page)
        self.assertEqual(tuple(label['actor_id'] for label in data['actor_display']['labels']),expected)
        self.assertEqual(json.loads(self.identity_calls[0].content)['actor_ids'],list(expected))
        self.assertEqual((len(self.access_calls),self.pool.borrows,self.pool.releases),(2,1,1))
        self.assertEqual([e['revision'] for e in data['audit']['events']],['5','4','3','2','1'])
    async def test_fresh_access_decision_id_is_not_authority_identity(self):
        self.authority_response=lambda:httpx.Response(200,json={**base.wire.evidence(),'decision_id':base.wire.FOREIGN if len(self.access_calls)>1 else base.wire.support.ORG})
        self.assertEqual((await self.get()).status_code,200)
    async def test_only_selected_page_ids_not_reader_lookahead_or_account(self):
        reader='99999999-9999-4999-8999-999999999999'
        lookahead='88888888-8888-4888-8888-888888888888'
        self.authority_response=lambda:httpx.Response(200,json={**base.wire.evidence(),'actor_id':reader})
        self.pool.connection.events[-2]['executor_actor_id']=UUID(lookahead)
        reply=await self.get(PATH+'?limit=1');self.assertEqual(reply.status_code,200)
        data=reply.json();ids=json.loads(self.identity_calls[0].content)['actor_ids']
        self.assertNotIn(reader,ids);self.assertNotIn(lookahead,ids)
        self.assertEqual(len(data['audit']['events']),1);self.assertIsNotNone(data['audit']['next_cursor'])
    async def test_header_only_actors_and_empty_continuation_select_exact_ids(self):
        owner='11111111-1111-4111-8111-111111111111'
        modifier='22222222-2222-4222-8222-222222222222'
        executor='33333333-3333-4333-8333-333333333333'
        initiator='44444444-4444-4444-8444-444444444444'
        reader='55555555-5555-4555-8555-555555555555'
        owner_account='66666666-6666-4666-8666-666666666666'
        other_page='77777777-7777-4777-8777-777777777777'
        self.authority_response=lambda:httpx.Response(200,json={**base.wire.evidence(),'actor_id':reader})
        self.pool.connection.header.update(owner_account_id=UUID(owner_account),owner_actor_id=UUID(owner),created_by=UUID(owner),updated_by=UUID(modifier))
        for event in self.pool.connection.events:
            revision=event['event_revision']
            event['executor_actor_id']=UUID(owner if revision==1 else modifier if revision==5 else executor if revision==3 else other_page)
            event['initiator_actor_id']=UUID(initiator) if revision==3 else None
        # This independent navigation fixture requests an older page, so neither
        # header actor appears in its included event. Never derive expected IDs
        # with the production selection helper or from the returned audit page.
        for last_revision,expected_revisions,expected_ids in (
            ('4',['3'],[owner,modifier,executor,initiator]),
            ('1',[],[owner,modifier]),
        ):
            with self.subTest(last_revision=last_revision):
                self.pool.borrows=self.pool.releases=0
                cursor=base.audit.admin.history._encode(dict(v=1,org_id=ORG,account_id=base.wire.support.ACCOUNT,capture_id=base.wire.support.CAPTURE,permission='kdg_capture.capture.read.all',limit=1,last_revision=last_revision))
                reply=await self.get(PATH+'?limit=1&cursor='+cursor)
                self.assertEqual(reply.status_code,200)
                data=reply.json()
                self.assertEqual([event['revision'] for event in data['audit']['events']],expected_revisions)
                self.assertEqual((data['audit']['owner_actor_id'],data['audit']['created_by'],data['audit']['updated_by']),(owner,owner,modifier))
                self.assertEqual(json.loads(self.identity_calls[-1].content),{'org_id':ORG,'actor_ids':expected_ids})
                self.assertEqual(data['actor_display'],{'status':'loaded','labels':[{'actor_id':actor,'status':'resolved','display_name':'Retained <name>'} for actor in expected_ids]})
                self.assertEqual((self.pool.borrows,self.pool.releases),(1,1))
                if not expected_revisions:self.assertIsNone(data['audit']['next_cursor'])
        self.assertEqual((len(self.identity_calls),len(self.access_calls)),(2,4))
    async def test_invalid_request_no_identity_or_checkout(self):
        for suffix in ('?actor_ids=x','?org_id='+ORG,'?limit=1&limit=2','?cursor=bad','?limit=101','?limit=01','?'+('x'*8193)):
            self.assertEqual((await self.get(PATH+suffix)).status_code,422)
        self.assertEqual((await self.get(content=b'private')).status_code,422)
        self.assertEqual((await self.get(headers={'Authorization':'Bearer synthetic','X-Service-Key':KEY})).status_code,422)
        for headers in ({},[('Authorization','Bearer a'),('Authorization','Bearer b')]):self.assertEqual((await self.get(headers=headers)).status_code,401)
        self.assertEqual((len(self.access_calls),len(self.identity_calls),self.pool.borrows),(0,0,0))
    async def test_denial_and_bad_audit_no_identity(self):
        self.authority_response=lambda:httpx.Response(403,json={'detail':{'code':'access_denied'}})
        self.assertEqual((await self.get()).status_code,403)
        self.assertEqual(self.pool.borrows,0)
        self.authority_response=lambda:httpx.Response(200,json=base.wire.evidence())
        self.pool.connection.missing=True
        self.assertEqual((await self.get()).status_code,404)
        self.pool.connection.missing=False
        self.pool.connection.transform=lambda rows:[rows[0],rows[0]]
        self.assertEqual((await self.get()).status_code,503)
        self.assertEqual(len(self.identity_calls),0)
    async def test_unmapped_is_loaded_and_outage_is_batch_unavailable(self):
        self.identity_response=lambda data:httpx.Response(200,json={'org_id':ORG,'labels':[{'actor_id':a,'status':'unavailable'} for a in data['actor_ids']]},headers={'Cache-Control':'private, no-store'})
        reply=await self.get();self.assertEqual(reply.json()['actor_display']['status'],'loaded')
        self.assertTrue(all(set(label)=={'actor_id','status'} for label in reply.json()['actor_display']['labels']))
        self.pool.borrows=self.pool.releases=0
        self.identity_response=lambda data:httpx.Response(503,content=b'private-upstream',headers={'Content-Type':'application/json','Cache-Control':'private, no-store'})
        reply=await self.get();self.assertEqual(reply.status_code,200)
        self.assertEqual(reply.json()['actor_display'],{'status':'temporarily_unavailable'})
        self.assertNotIn('private-upstream',reply.text)
    async def test_final_authority_loss_or_changed_binding_prevents_publication(self):
        for code,error in ((403,'access_denied'),(401,'authentication_required'),(409,'identity.actor_setup_required'),(503,'authorization_unavailable')):
            self.pool.borrows=self.pool.releases=0;self.access_calls.clear()
            self.authority_response=lambda:httpx.Response(200,json=base.wire.evidence()) if len(self.access_calls)==1 else httpx.Response(code,json={'detail':{'code':error}})
            reply=await self.get();self.assertEqual((reply.status_code,reply.json()['error_id']),(code,error))
            self.assertNotIn('audit',reply.json())
        self.pool.borrows=self.pool.releases=0;self.access_calls.clear()
        self.identity_response=lambda data:httpx.Response(503,json={'private':'not exposed'},headers={'Cache-Control':'private, no-store'})
        self.authority_response=lambda:httpx.Response(200,json=base.wire.evidence()) if len(self.access_calls)==1 else httpx.Response(403,json={'detail':{'code':'access_denied'}})
        reply=await self.get();self.assertEqual(reply.status_code,403);self.assertNotIn('audit',reply.json())
        self.identity_response=None
        for field,value in (('account_id',base.wire.FOREIGN),('actor_id',base.wire.FOREIGN),('membership_id','987')):
            self.pool.borrows=self.pool.releases=0;self.access_calls.clear()
            self.authority_response=lambda:httpx.Response(200,json=base.wire.evidence() if len(self.access_calls)==1 else {**base.wire.evidence(),field:value})
            reply=await self.get();self.assertEqual(reply.json()['error_id'],'authorization_observation_expired',field)
    async def test_invalid_identity_whole_batch_degrades_after_final_authority(self):
        def original(data):return {'org_id':ORG,'labels':[{'actor_id':a,'status':'resolved','display_name':'Valid'} for a in data['actor_ids']]}
        def bad_label(data,change):
            value=original(data);value['labels'][0].update(change);return value
        variants=[lambda d:{**original(d),'org_id':base.wire.FOREIGN},lambda d:{**original(d),'extra':1},lambda d:{**original(d),'labels':[]},lambda d:{**original(d),'labels':list(reversed(original(d)['labels']))},lambda d:{**original(d),'labels':[original(d)['labels'][0]]*len(d['actor_ids'])}]
        variants.extend(lambda d,c=c:bad_label(d,c) for c in ({'extra':1},{'display_name':' '},{'display_name':'a\n'},{'display_name':'x'*257},{'actor_id':ORG.upper()},{'actor_id':'00000000-0000-0000-0000-000000000000'},{'status':'unavailable'}))
        for variant in variants:
            self.pool.borrows=self.pool.releases=0
            self.identity_response=lambda data:httpx.Response(200,json=variant(data),headers={'Cache-Control':'private, no-store'})
            reply=await self.get();self.assertEqual(reply.json()['actor_display'],{'status':'temporarily_unavailable'})
        for body,headers,status in ((b'{"org_id":1,"org_id":2}',{},200),(b'\xff',{},200),(b' '* (consumer.RESPONSE_BYTES+1),{},200),(b'private',{'Cache-Control':'public, private, no-store'},200),(b'private',{'Content-Encoding':'gzip'},200),(b'private',{'Content-Type':'text/plain'},200),(b'private',{'Cache-Control':'no-store'},200),(b'x'*1025,{},403),(b'private',{},302)):
            self.pool.borrows=self.pool.releases=0
            self.identity_response=lambda data:httpx.Response(status,content=body,headers={'Content-Type':'application/json','Cache-Control':'private, no-store',**headers})
            reply=await self.get();self.assertEqual(reply.json()['actor_display'],{'status':'temporarily_unavailable'})
        self.assertEqual(len(self.access_calls),2*len(self.identity_calls))
    async def test_one_budget_and_skip_labels_preserves_final_check(self):
        original=base.audit.write.Budget;budgets=[]
        def budget():
            result=original();budgets.append(result);return result
        original_auth=base.audit.AuditReadHandler._authorize
        seen=[]
        async def authorize(owner,token,passed):
            seen.append(passed)
            result=await original_auth(owner,token,passed)
            if len(seen)==1:passed.deadline=passed.time_now()+3 if hasattr(passed,'time_now') else base.audit.write.time.monotonic()+3
            return result
        with patch.object(base.audit.write,'Budget',side_effect=budget),patch.object(base.audit.AuditReadHandler,'_authorize',authorize):reply=await self.get()
        self.assertEqual(reply.status_code,200);self.assertEqual(reply.json()['actor_display']['status'],'temporarily_unavailable')
        self.assertEqual(len(budgets),1);self.assertEqual(seen,[budgets[0],budgets[0]]);self.assertFalse(self.identity_calls)
    async def test_lookup_cancellation_awaits_close_and_suppresses_cleanup_diagnostics(self):
        for fail in (False,True):
            self.pool.borrows=self.pool.releases=0
            started,release,unwound=asyncio.Event(),asyncio.Event(),asyncio.Event()
            async def pending(request):
                try:started.set();await asyncio.Event().wait()
                finally:
                    await release.wait();unwound.set()
                    if fail:raise RuntimeError('private-cleanup-canary')
            app=self.make_app(pending)
            diagnostics=[];loop=asyncio.get_running_loop();old=loop.get_exception_handler();loop.set_exception_handler(lambda loop,context:diagnostics.append(context))
            try:
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='https://kdg.invalid') as client:
                    task=asyncio.create_task(client.get(PATH,headers={'Authorization':'Bearer synthetic'}))
                    await asyncio.wait_for(started.wait(),1);task.cancel();await asyncio.sleep(.01);task.cancel();await asyncio.sleep(.01)
                    self.assertFalse(task.done());release.set()
                    with self.assertRaises(asyncio.CancelledError):await task
                    await asyncio.sleep(0);self.assertTrue(unwound.is_set());self.assertFalse(diagnostics)
            finally:release.set();loop.set_exception_handler(old)
    async def test_lookup_timeout_owns_cleanup_and_final_authority(self):
        closed=asyncio.Event()
        async def pending(request):
            try:await asyncio.Event().wait()
            finally:closed.set();raise RuntimeError('private-timeout-canary')
        self.app=self.make_app(pending)
        diagnostics=[];loop=asyncio.get_running_loop();old=loop.get_exception_handler();loop.set_exception_handler(lambda loop,context:diagnostics.append(context))
        try:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='https://kdg.invalid') as client:
                with patch.object(consumer,'LOOKUP_SECONDS',.08),patch.object(consumer,'UNWIND_RESERVE',.02):
                    reply=await client.get(PATH,headers={'Authorization':'Bearer synthetic'})
            await asyncio.sleep(0);self.assertFalse(diagnostics)
        finally:loop.set_exception_handler(old)
        self.assertTrue(closed.is_set());self.assertEqual(reply.json()['actor_display']['status'],'temporarily_unavailable');self.assertEqual(len(self.access_calls),2)
    async def test_maximum_page_and_scalar_names_are_not_trimmed(self):
        from datetime import timedelta
        current=100
        self.pool.connection.header['current_revision']=current
        actors=[str(UUID(int=1000+i)) for i in range(200)]
        self.pool.connection.header['updated_by']=UUID(actors[-2])
        now=self.pool.connection.header['created_at']
        self.pool.connection.events=[dict(event_revision=n,command_type='capture.create' if n==1 else 'capture.edit',executor_actor_id=UUID(base.wire.support.ACTOR if n==1 else actors[(n-1)*2]),initiator_actor_id=UUID(actors[(n-1)*2+1]),recorded_at=now+timedelta(seconds=n)) for n in range(1,101)]
        def response(data):
            value={'org_id':ORG,'labels':[{'actor_id':actor,'status':'resolved','display_name':'😀'*256} for actor in data['actor_ids']]}
            return httpx.Response(200,content=json.dumps(value,ensure_ascii=False).encode(),headers={'Content-Type':'application/json','Cache-Control':'private, no-store'})
        self.identity_response=response
        reply=await self.get(PATH+'?limit=100');self.assertEqual(reply.status_code,200)
        data=reply.json();self.assertEqual(len(data['audit']['events']),100)
        self.assertIsNone(data['audit']['next_cursor']);self.assertEqual(data['actor_display']['status'],'loaded')
        self.assertEqual(len(data['actor_display']['labels']),200)
        self.assertTrue(all(label['display_name']=='😀'*256 for label in data['actor_display']['labels']))
        self.assertLessEqual(len(reply.content),aggregate.MAX_RESPONSE_BYTES)
        # JSON escaping counts toward the upstream byte ceiling, even for valid names.
        self.pool.borrows=self.pool.releases=0
        self.identity_response=lambda data:httpx.Response(200,content=json.dumps({'org_id':ORG,'labels':[{'actor_id':actor,'status':'resolved','display_name':'😀'*256} for actor in data['actor_ids']]}).encode(),headers={'Content-Type':'application/json','Cache-Control':'private, no-store'})
        reply=await self.get(PATH+'?limit=100');self.assertEqual(reply.status_code,200)
        self.assertEqual(reply.json()['actor_display'],{'status':'temporarily_unavailable'})
        self.assertEqual(len(reply.json()['audit']['events']),100)
    async def test_stream_bounds_and_uncooperative_first_abort_are_owned(self):
        class Stream(httpx.AsyncByteStream):
            def __init__(self):self.closed=False
            async def __aiter__(self):
                yield b'x'*(consumer.RESPONSE_BYTES+1)
            async def aclose(self):self.closed=True
        stream=Stream()
        self.identity_response=lambda data:httpx.Response(200,stream=stream,headers={'Content-Type':'application/json','Cache-Control':'private, no-store','Content-Length':'1'})
        reply=await self.get();self.assertTrue(stream.closed)
        self.assertEqual(reply.json()['actor_display']['status'],'temporarily_unavailable')
        started,closed=asyncio.Event(),asyncio.Event()
        async def ignores_first_abort(request):
            try:
                started.set()
                try:await asyncio.Event().wait()
                except asyncio.CancelledError:await asyncio.Event().wait()
            finally:closed.set()
        self.pool.borrows=self.pool.releases=0
        app=self.make_app(ignores_first_abort)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='https://kdg.invalid') as client:
            with patch.object(consumer,'LOOKUP_SECONDS',.1),patch.object(consumer,'UNWIND_RESERVE',.03):
                reply=await asyncio.wait_for(client.get(PATH,headers={'Authorization':'Bearer synthetic'}),1)
        self.assertTrue(closed.is_set());self.assertEqual(reply.json()['actor_display']['status'],'temporarily_unavailable')
    async def test_serialization_expiry_never_publishes_aggregate(self):
        original=aggregate.AuditDetails.model_dump_json
        budget_type=base.audit.write.Budget;budgets=[]
        def make_budget():
            value=budget_type();budgets.append(value);return value
        def serialize(value,*args,**kwargs):
            body=original(value,*args,**kwargs);budgets[0].deadline=budgets[0].started_at-1;return body
        with patch.object(base.audit.write,'Budget',side_effect=make_budget),patch.object(aggregate.AuditDetails,'model_dump_json',serialize):reply=await self.get()
        self.assertEqual(reply.json()['error_id'],'execution_timeout');self.assertNotIn('audit',reply.json())
    async def test_only_new_route_and_closed_aggregate(self):
        for path in (base.PATH,PATH+'/',PATH.replace(base.wire.support.CAPTURE,'bad')):
            self.assertIn((await self.get(path)).status_code,(404,422))
        self.assertFalse(hasattr(boundary,'app'))
        for value in ({'status':'temporarily_unavailable','labels':[]},{'status':'loaded','labels':[]}):
            with self.assertRaises(ValueError):aggregate.AuditDetails(audit={},actor_display=value)

class Configuration(unittest.TestCase):
    def test_explicit_redacted_policy(self):
        for url in ('http://identity.invalid','https://u:p@identity.invalid','https://identity.invalid/path','https://identity.invalid?x','https://identity.invalid#x','https://identity.invalid:0','https://identity.invalid:'):
            with self.assertRaisesRegex(RuntimeError,'^kdg_actor_display_configuration_invalid$'):consumer.IdentityDisplays(base_url=url,service_key=KEY,access_service_key='synthetic')
        for key in ('',KEY+' ', 'x'*257,'secret'):
            with self.assertRaisesRegex(RuntimeError,'^kdg_actor_display_configuration_invalid$'):consumer.IdentityDisplays(base_url='https://identity.invalid',service_key=key,access_service_key='synthetic')
        with self.assertRaises(RuntimeError):consumer.IdentityDisplays(base_url='https://identity.invalid',service_key=KEY,access_service_key=KEY)
        self.assertNotIn(KEY,repr(consumer.IdentityDisplays(base_url='https://identity.invalid',service_key=KEY,access_service_key='synthetic')))

class SyntheticIdentityHTTP(unittest.IsolatedAsyncioTestCase):
    # Real in-process HTTP owner, synthetic narrow projection; no server imports in runtime.
    def setUp(self):
        CompositionAcceptance.setUp(self)
        sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'services/access'))
        from actor_display_http import create_app
        self.projected=[]
        async def read(selected,deadline):
            self.assertEqual((self.pool.borrows,self.pool.releases),(1,1))
            self.assertFalse(self.pool.connection.in_transaction())
            self.projected.append(selected)
            return [{'actor_id':actor,'display_name':'Retained name'} for actor in reversed(selected)]
        owner=create_app({'KDG_ACTOR_DISPLAY_SERVICE_KEY':KEY,'KDG_ACTOR_DISPLAY_ORG_ID':ORG},read)
        with patch.object(base.boundary,'create_engine',return_value=self.pool):
            self.owner_app=boundary.create_candidate(org_id=ORG,access_url='https://access.invalid',service_key='synthetic',database_url=base.wire.history_support.DB_URL,identity_url='https://identity.invalid',identity_service_key=KEY,transport=httpx.MockTransport(self.access),identity_transport=httpx.ASGITransport(app=owner))
    make_app=CompositionAcceptance.make_app
    asyncTearDown=CompositionAcceptance.asyncTearDown
    async def test_real_owner_http_matches_exact_selected_labels(self):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self.owner_app),base_url='https://kdg.invalid') as client:
            reply=await client.get(PATH+'?limit=2',headers={'Authorization':'Bearer synthetic'})
        self.assertEqual(reply.status_code,200)
        data=reply.json();self.assertEqual(data['actor_display']['status'],'loaded')
        selected=aggregate.selected_actor_ids(base.audit.AuditPage.model_validate(data['audit']))
        self.assertEqual(self.projected,[tuple(UUID(actor) for actor in selected)])
        self.assertEqual([label['actor_id'] for label in data['actor_display']['labels']],list(selected))
