"""Synthetic protected setup acceptance; no database privilege qualification."""
import asyncio
import json
from itertools import product
import unittest
from datetime import datetime,timedelta,timezone
from types import SimpleNamespace
from unittest.mock import patch
import httpx
import test_capture_read as support
import provision

ORG,ACCOUNT,ACTOR=support.ORG,support.ACCOUNT,support.ACTOR
CHILD,QUESTIONNAIRE,VERSION,ASSIGNMENT=support.IDS
PERMISSIONS=[provision.READ,provision.EDIT,provision.create.ALL,provision.create.ASSIGNED]
class Rows:
    rowcount=1
    def __init__(self,value):self.value=value
    def mappings(self):return self
    def one_or_none(self):return self.value
    def all(self):return self.value
class Connection(support.support.support.Connection):
    def __init__(self):
        super().__init__()
        self.child=dict(id=CHILD,org_id=ORG,display_name='Synthetic child',active=True,revision=3)
        self.children=[self.child.copy()]
        self.assignment=dict(id=ASSIGNMENT,org_id=ORG,child_id=CHILD,account_id=ACCOUNT,membership_id=7,active=True,revision=4)
        self.version=dict(id=VERSION,org_id=ORG,questionnaire_id=QUESTIONNAIRE,display_version=2,definition=support.DEFINITION)
        self.issued=[];self.on_lock=lambda:None;self.locked=[]
        self.current_children={CHILD:self.child};self.current_assignments={CHILD:self.assignment}
        self.return_issuance=lambda rows:rows
    def execute(self,sql,p):
        result=super().execute(sql,p);sql=str(sql)
        if sql==provision.VERSION:return Rows(self.version)
        if sql in (provision.CHILDREN,provision.ASSIGNED_CHILDREN):return Rows(self.children)
        if sql==provision.LOCK_CHILDREN:
            self.locked.extend(p['children']);self.on_lock()
            return Rows([{'child_id':child} for child in p['children']])
        if sql in (provision.CHILDREN_AFTER_LOCK,provision.ASSIGNED_AFTER_LOCK):
            rows=[]
            for child in p['children']:
                if child not in self.current_children:continue
                row=self.current_children[child].copy()
                if sql==provision.ASSIGNED_AFTER_LOCK:
                    item=self.current_assignments.get(child) or {}
                    row.update({'assignment_'+key:item.get(key) for key in ('id','org_id','child_id','account_id','membership_id','active','revision')})
                rows.append(row)
            return Rows(rows)
        if sql==provision.ISSUE_BATCH:
            rows=[];issued_at=datetime.now(timezone.utc)
            for item in json.loads(p['issues']):
                self.issued.append({**p,**item});rows.append(dict(ref=item['ref'],child_id=item['child'],issued_at=issued_at))
            return Rows(self.return_issuance(rows))
        return result

class ProvisionAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db=Connection();self.checks=[]
        self.upstream=lambda permission:httpx.Response(200,json=support.support.evidence(permission))
        async def access(request):
            self.assertEqual(self.db.calls,[])
            body=json.loads(request.content);self.assertEqual(body['authorization_scope'],{'kind':'organization','org_id':ORG})
            self.checks.append(body['permission']);return self.upstream(body['permission'])
        self.handler=provision.ProvisionHandler(org_id=ORG,questionnaire_id=QUESTIONNAIRE,access_url='https://access.invalid',service_key='synthetic',transport=httpx.MockTransport(access))
    async def execute(self):return await self.handler.execute(self.db,'Bearer synthetic')
    def denied(self,*permissions):
        self.upstream=lambda permission:httpx.Response(403,json={'detail':{'code':'access_denied'}}) if permission in permissions else httpx.Response(200,json=support.support.evidence(permission))
    async def test_all_four_checks_are_independent_and_exact(self):
        result=await self.execute()
        self.assertEqual(self.checks,PERMISSIONS)
        self.assertEqual(result.create_state,'ready');self.assertEqual(result.schema_version,1)
        self.assertEqual(result.questionnaire.definition.model_dump(mode='json'),support.DEFINITION)
        self.assertEqual(result.questionnaire.questionnaire_version,'2')
        self.assertIsNone(result.children[0].assignment)
        self.assertFalse(any(sql==provision.ASSIGNED_AFTER_LOCK for sql,_ in self.db.calls))
        self.assertEqual(self.db.calls[-1][0],'COMMIT')
        self.assertEqual((result.org_id,result.account_id,result.actor_id,result.membership_id),(ORG,ACCOUNT,ACTOR,'7'))
        for observation in (result.read_observation,result.edit_observation,result.create_all_observation,result.create_assigned_observation):self.assertEqual(observation.expires_at-observation.checked_at,timedelta(days=7))
        child=result.children[0]
        self.assertEqual(datetime.fromisoformat(child.expires_at)-datetime.fromisoformat(child.checked_at),timedelta(days=7))
        self.assertEqual((child.child_revision,child.create_permission),('3',provision.create.ALL))
        self.assertEqual((self.db.issued[0]['actor'],self.db.issued[0]['member'],self.db.issued[0]['account']),(ACTOR,7,ACCOUNT))
    async def test_optional_checks_overlap_after_mandatory_read_before_any_sql(self):
        # Real yielding transport gates qualify overlap without a wall-clock race.
        arrived=set();release=asyncio.Event();read_done=False;active=0
        async def access(request):
            nonlocal read_done,active
            permission=json.loads(request.content)['permission']
            self.assertEqual(self.db.calls,[])
            if permission==provision.READ:
                self.assertFalse(arrived);read_done=True
            else:
                self.assertTrue(read_done);arrived.add(permission);active+=1
                try:await release.wait()
                finally:active-=1
            return httpx.Response(200,json=support.support.evidence(permission))
        self.handler._transport=httpx.MockTransport(access)
        task=asyncio.create_task(self.execute())
        try:
            for _ in range(100):
                if len(arrived)==3:break
                await asyncio.sleep(.001)
            self.assertEqual(arrived,set(PERMISSIONS[1:]),'optional capability checks remained sequential')
            self.assertEqual(active,3);self.assertEqual(self.db.calls,[])
        finally:
            release.set()
            await task
        self.assertEqual(self.db.calls[-1][0],'COMMIT')

    async def test_concurrent_roundtrips_keep_oldest_read_fresh_without_resetting_it(self):
        # Each yielded roundtrip costs .4s in the existing monotonic DB guard.
        # Serial optional calls age READ by1.2s; one concurrent round ages it by.4s.
        now=100.
        async def access(request):
            nonlocal now
            started=now;await asyncio.sleep(0);now=started+.4
            return httpx.Response(200,json=support.support.evidence(json.loads(request.content)['permission']))
        self.handler._transport=httpx.MockTransport(access)
        with patch.object(provision.write,'time',SimpleNamespace(monotonic=lambda:now)):
            result=await self.execute()
        self.assertEqual(result.create_state,'ready');self.assertAlmostEqual(now,100.8)
        self.assertEqual(self.db.calls[-1][0],'COMMIT')

    async def test_reordered_optional_completion_keeps_slots_and_oldest_observation(self):
        finished=[]
        async def authorize(checker,token,budget):
            permission=checker._permissions[0]
            if permission!=provision.READ:
                for _ in range({provision.EDIT:3,provision.create.ALL:2,provision.create.ASSIGNED:1}[permission]):await asyncio.sleep(0)
            finished.append(permission)
            return checker._evidence_type.model_validate(support.support.evidence(permission)),100.+len(finished)*.1
        with patch.object(provision._Checker,'_authorize',authorize):
            evidence,observed=await self.handler.authorize('Bearer synthetic',provision.write.Budget())
        self.assertEqual(finished,[provision.READ,provision.create.ASSIGNED,provision.create.ALL,provision.EDIT])
        self.assertEqual([item.permission for item in evidence],PERMISSIONS)
        self.assertEqual(observed,100.1);self.assertEqual(self.db.calls,[])

    async def test_optional_denial_matrix_preserves_each_grant_without_inference(self):
        for allowed in product((False,True),repeat=3):
            with self.subTest(allowed=allowed):
                self.setUp();self.denied(*(permission for permission,granted in zip(PERMISSIONS[1:],allowed,strict=True) if not granted))
                result=await self.execute()
                self.assertEqual(self.checks,PERMISSIONS)
                self.assertEqual(tuple(item is not None for item in (result.edit_observation,result.create_all_observation,result.create_assigned_observation)),allowed)
                self.assertEqual(result.create_state,'ready' if any(allowed[1:]) else 'not_permitted')
                if any(allowed[1:]):self.assertEqual(result.children[0].create_permission,provision.create.ALL if allowed[1] else provision.create.ASSIGNED)
                else:self.assertEqual(self.db.issued,[])

    async def test_optional_non_denial_errors_never_become_absent_grants(self):
        for permission in PERMISSIONS[1:]:
            for status,code in ((401,'authentication_required'),(409,'identity.actor_setup_required'),(503,'authorization_unavailable'),(403,'unknown')):
                with self.subTest(permission=permission,status=status):
                    self.setUp()
                    self.upstream=lambda current:httpx.Response(status,json={'detail':{'code':code}}) if current==permission else httpx.Response(200,json=support.support.evidence(current))
                    with self.assertRaises(provision.protected.HandlerError) as error:await self.execute()
                    self.assertEqual((error.exception.status,error.exception.error_id),(status,code) if status in (401,409) else (503,'authorization_unavailable'))
                    self.assertEqual(self.db.calls,[])

    async def test_parent_cancellation_drains_all_optional_checks_without_sql(self):
        arrived=set();closed=set();release=asyncio.Event()
        async def access(request):
            permission=json.loads(request.content)['permission']
            if permission!=provision.READ:
                arrived.add(permission)
                try:await release.wait()
                finally:closed.add(permission)
            return httpx.Response(200,json=support.support.evidence(permission))
        self.handler._transport=httpx.MockTransport(access)
        task=asyncio.create_task(self.execute())
        try:
            for _ in range(100):
                if len(arrived)==3:break
                await asyncio.sleep(.001)
            self.assertEqual(arrived,set(PERMISSIONS[1:]))
        finally:
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):await task
        self.assertEqual(closed,set(PERMISSIONS[1:]));self.assertEqual(self.db.calls,[])

    async def test_optional_failure_cancels_and_drains_siblings_before_return(self):
        arrived=set();closed=set();release=asyncio.Event()
        async def access(request):
            permission=json.loads(request.content)['permission']
            if permission!=provision.READ:
                arrived.add(permission)
                try:
                    if len(arrived)==3:release.set()
                    await release.wait()
                    if permission==provision.EDIT:return httpx.Response(503,json={'detail':{'code':'unavailable'}})
                    await asyncio.Event().wait()
                finally:closed.add(permission)
            return httpx.Response(200,json=support.support.evidence(permission))
        self.handler._transport=httpx.MockTransport(access)
        with self.assertRaises(provision.protected.HandlerError) as error:
            async with asyncio.timeout(.5):await self.execute()
        self.assertEqual((error.exception.status,error.exception.error_id),(503,'authorization_unavailable'))
        self.assertEqual(closed,set(PERMISSIONS[1:]));self.assertEqual(self.db.calls,[])

    async def test_repeated_cancellation_keeps_optional_cleanup_owned_until_drained(self):
        arrived=set();draining=set();closed=set();release=asyncio.Event()
        async def access(request):
            permission=json.loads(request.content)['permission']
            if permission!=provision.READ:
                arrived.add(permission)
                try:await asyncio.Event().wait()
                finally:
                    draining.add(permission);await release.wait();closed.add(permission)
            return httpx.Response(200,json=support.support.evidence(permission))
        self.handler._transport=httpx.MockTransport(access);task=asyncio.create_task(self.execute())
        try:
            for _ in range(100):
                if len(arrived)==3:break
                await asyncio.sleep(.001)
            self.assertEqual(arrived,set(PERMISSIONS[1:]))
            task.cancel()
            for _ in range(100):
                if len(draining)==3:break
                await asyncio.sleep(.001)
            self.assertEqual(draining,arrived);task.cancel();await asyncio.sleep(0)
            self.assertFalse(task.done());self.assertEqual(self.db.calls,[])
        finally:
            release.set()
            if not task.cancelling():task.cancel()
            with self.assertRaises(asyncio.CancelledError):await task
        self.assertEqual(closed,arrived);self.assertEqual(self.db.calls,[])

    async def test_cancellation_closes_each_borrowed_transport_response_before_return(self):
        # Match the configured fixture's ownership contract: client close is a no-op
        # on its borrowed transport; streamed responses remain client-owned.
        arrived=set();closed=set();client_closes=[];release=asyncio.Event()
        class Stream(httpx.AsyncByteStream):
            def __init__(self,permission):self.permission=permission
            async def __aiter__(self):
                arrived.add(self.permission);await release.wait()
                yield json.dumps(support.support.evidence(self.permission)).encode()
            async def aclose(self):closed.add(self.permission)
        class BorrowedTransport(httpx.AsyncBaseTransport):
            async def handle_async_request(self,request):
                permission=json.loads(request.content)['permission']
                if permission==provision.READ:return httpx.Response(200,json=support.support.evidence(permission))
                return httpx.Response(200,stream=Stream(permission))
            async def aclose(self):client_closes.append(True)
        self.handler._transport=BorrowedTransport();task=asyncio.create_task(self.execute())
        try:
            for _ in range(100):
                if len(arrived)==3:break
                await asyncio.sleep(.001)
            self.assertEqual(arrived,set(PERMISSIONS[1:]))
        finally:
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):await task
        self.assertEqual(closed,arrived);self.assertEqual(len(client_closes),4);self.assertEqual(self.db.calls,[])

    async def test_shared_access_deadline_includes_read_and_drains_optional_work(self):
        arrived=set();closed=set()
        async def access(request):
            permission=json.loads(request.content)['permission']
            if permission==provision.READ:await asyncio.sleep(.02)
            else:
                arrived.add(permission)
                try:await asyncio.sleep(.02)
                finally:closed.add(permission)
            return httpx.Response(200,json=support.support.evidence(permission))
        self.handler._transport=httpx.MockTransport(access)
        self.assertEqual(provision.protected.ACCESS_SECONDS,3.)
        with patch.object(provision.protected,'ACCESS_SECONDS',.03):
            with self.assertRaises(provision.protected.HandlerError) as error:await self.execute()
        self.assertEqual((error.exception.status,error.exception.error_id),(503,'authorization_unavailable'))
        self.assertEqual(arrived,set(PERMISSIONS[1:]));self.assertEqual(closed,arrived);self.assertEqual(self.db.calls,[])

    async def test_assigned_scope_current_membership_and_revision(self):
        self.denied(provision.create.ALL,provision.EDIT)
        result=await self.execute()
        self.assertIsNone(result.edit_observation);self.assertIsNone(result.create_all_observation)
        self.assertEqual(result.children[0].assignment.model_dump(),{'assignment_id':ASSIGNMENT,'assignment_revision':'4'})
        self.assertEqual(self.db.issued[0]['assignment'],ASSIGNMENT)
        sql=[sql for sql,_ in self.db.calls]
        self.assertLess(sql.index(provision.LOCK_CHILDREN),sql.index(provision.ASSIGNED_AFTER_LOCK))
        self.assertLess(sql.index(provision.ASSIGNED_AFTER_LOCK),sql.index(provision.ISSUE_BATCH))
    async def test_states_have_explicit_precedence_and_no_inferred_authority(self):
        self.denied(provision.create.ALL,provision.create.ASSIGNED)
        self.db.version=None
        result=await self.execute();self.assertEqual(result.create_state,'not_permitted');self.assertEqual(result.children,[])
        self.assertEqual(self.db.issued,[])
        self.setUp();self.db.version=None;result=await self.execute();self.assertEqual(result.create_state,'no_published_questionnaire')
        self.setUp();self.db.children=[];result=await self.execute();self.assertEqual(result.create_state,'no_eligible_children')
        self.assertIsNotNone(result.questionnaire)
    async def test_entry_denial_blocks_all_setup(self):
        self.denied(provision.READ)
        with self.assertRaises(provision.protected.HandlerError) as failed:await self.execute()
        self.assertEqual(failed.exception.error_id,'access_denied');self.assertEqual(self.checks,[provision.READ]);self.assertEqual(self.db.calls,[])
    async def test_malformed_foreign_unavailable_or_stale_check_never_issues(self):
        for change in ({'account_id':CHILD},{'actor_id':CHILD},{'membership_id':'8'},{'permission':provision.READ},{'private':'secret'}, {'checked_at':'2000-01-01T00:00:00Z'}):
            self.setUp()
            self.upstream=lambda permission:httpx.Response(200,json={**support.support.evidence(permission),**(change if permission==provision.create.ASSIGNED else {})})
            with self.assertRaises(provision.protected.HandlerError) as failed:await self.execute()
            self.assertEqual(failed.exception.error_id,'authorization_unavailable');self.assertEqual(self.db.calls,[])
        self.setUp();self.upstream=lambda p:httpx.Response(503,json={'detail':{'code':'private'}})
        with self.assertRaises(provision.protected.HandlerError) as failed:await self.execute()
        self.assertEqual(failed.exception.error_id,'authorization_unavailable');self.assertEqual(self.db.issued,[])
    async def test_checked_child_and_assignment_changes_stop_entire_issuance(self):
        for target,change in (('child',{'active':False}),('child',{'org_id':CHILD}),('child',{'revision':True}),('assignment',{'membership_id':8}),('assignment',{'active':False}),('assignment',{'account_id':CHILD})):
            self.setUp();self.denied(provision.create.ALL)
            self.db.on_lock=lambda:getattr(self.db,target).update(change)
            with self.assertRaises(provision.protected.HandlerError) as failed:await self.execute()
            self.assertEqual(failed.exception.error_id,'provision_unavailable');self.assertEqual(self.db.issued,[])
            self.assertNotIn('COMMIT',[sql for sql,_ in self.db.calls])
    async def test_duplicate_foreign_oversized_or_invalid_rows_are_not_truncated(self):
        for children in ([{**self.db.child,'org_id':CHILD}],[self.db.child]*2,[self.db.child]*1001):
            self.setUp();self.db.children=children
            with self.assertRaises(provision.protected.HandlerError):await self.execute()
            self.assertEqual(self.db.issued,[])
        self.setUp();self.db.version['definition']={}
        with self.assertRaises(provision.protected.HandlerError):await self.execute()
        self.assertEqual(self.db.issued,[])
    async def test_repeat_only_issues_unique_refs_without_capture_history_or_outcome(self):
        first=await self.execute();self.db.calls=[];second=await self.execute()
        self.assertNotEqual(first.children[0].child_eligibility_ref,second.children[0].child_eligibility_ref)
        mutations=[sql for sql,_ in self.db.calls if sql.startswith(('INSERT','UPDATE','DELETE'))]
        self.assertEqual(mutations,[provision.ISSUE_BATCH])
    async def test_commit_failure_and_expired_first_check_never_return_setup(self):
        self.db.fail_commit=True
        with self.assertRaises(provision.protected.HandlerError) as failed:await self.execute()
        self.assertEqual(failed.exception.error_id,'provision_unavailable')
        self.setUp();now=100.
        original=self.upstream
        def upstream(permission):
            nonlocal now
            if permission==provision.create.ASSIGNED:now+=1.1
            return original(permission)
        self.upstream=upstream
        with patch.object(provision.write,'time',SimpleNamespace(monotonic=lambda:now)):
            with self.assertRaises(provision.protected.HandlerError) as failed:await self.execute()
        self.assertEqual(failed.exception.error_id,'authorization_observation_expired');self.assertEqual(self.db.calls,[])
    async def test_closed_model_and_bounds(self):
        result=await self.execute()
        with self.assertRaises(ValueError):provision.Provision.model_validate({**result.model_dump(mode='json'),'private':'secret'})
        self.assertEqual(provision.MAX_CHILDREN,1000);self.assertEqual(provision.MAX_RESPONSE_BYTES,1024*1024)
    async def test_new_issuer_reference_runtime_matches_closed_schema(self):
        import provision_http
        import test_create_contract
        result=await self.execute();value=result.children[0].model_dump(mode='json')
        doc=provision_http._create_app(None,None,None,None).openapi()
        shape=doc['components']['schemas']['Child']['properties']['child_eligibility_ref']
        for ref,expected in [('x'*43,True),('x',False),('x'*42+'!',False),('x'*43+'\n',False)]:
            with self.subTest(ref=ref):
                try:provision.Child.model_validate({**value,'child_eligibility_ref':ref});runtime=True
                except ValueError:runtime=False
                self.assertEqual(runtime,expected)
                self.assertEqual(test_create_contract.CreateContract.valid(self,doc,shape,ref),expected)
    def install_children(self,count,label='Child'):
        rows=[dict(id=f'{n:08x}-bbbb-4bbb-8bbb-{n:012x}',org_id=ORG,display_name=label,active=True,revision=n+2) for n in range(1,count+1)]
        children={row['id']:row for row in rows}
        assignments={row['id']:dict(id=f'{n:08x}-cccc-4ccc-8ccc-{n:012x}',org_id=ORG,child_id=row['id'],account_id=ACCOUNT,membership_id=7,active=True,revision=n+4) for n,row in enumerate(rows,1)}
        self.db.children=rows;self.db.current_children=children;self.db.current_assignments=assignments
        return rows,assignments
    async def test_multiple_children_have_sorted_locks_and_independent_committed_bindings(self):
        rows,assignments=self.install_children(3);self.denied(provision.create.ALL)
        result=await self.execute()
        self.assertEqual(self.db.locked,[row['id'] for row in rows])
        lock_positions=[n for n,(sql,_) in enumerate(self.db.calls) if sql==provision.LOCK_CHILDREN]
        first_read=next(n for n,(sql,_) in enumerate(self.db.calls) if sql==provision.ASSIGNED_AFTER_LOCK)
        self.assertLess(max(lock_positions),first_read)
        self.assertEqual(len({child.child_eligibility_ref for child in result.children}),3)
        for child,row,stored in zip(result.children,rows,self.db.issued,strict=True):
            assignment=assignments[row['id']]
            self.assertEqual((child.child_id,child.child_revision,child.assignment.assignment_id,child.assignment.assignment_revision),(row['id'],str(row['revision']),assignment['id'],str(assignment['revision'])))
            self.assertEqual((stored['child'],stored['revision'],stored['ref'],stored['assignment'],stored['assignment_revision']),(child.child_id,row['revision'],child.child_eligibility_ref,assignment['id'],assignment['revision']))
            self.assertEqual((stored['org'],stored['account'],stored['actor'],stored['member'],stored['permission']),(ORG,ACCOUNT,ACTOR,7,provision.create.ASSIGNED))
        self.assertEqual(self.db.calls[-1][0],'COMMIT')
    async def test_incomplete_batch_rechecks_or_issuance_have_no_successful_commit(self):
        for phase in ('child','assignment','issuance'):
            self.setUp();self.install_children(2);self.denied(provision.create.ALL)
            original=self.db.execute
            def execute(sql,p):
                result=original(sql,p)
                if str(sql)==provision.ASSIGNED_AFTER_LOCK:
                    if phase=='child':return Rows(result.value[:1])
                    if phase=='assignment':result.value[1]['assignment_membership_id']=8
                if str(sql)==provision.ISSUE_BATCH and phase=='issuance':return Rows(result.value[:1])
                return result
            self.db.execute=execute
            with self.assertRaises(provision.protected.HandlerError) as failed:await self.execute()
            self.assertEqual((failed.exception.status,failed.exception.error_id),(503,'provision_unavailable'))
            # Complete rechecks now precede the single INSERT. Only an issuance
            # result mismatch has provisional rows; final rollback remains required.
            self.assertEqual(len(self.db.issued),2 if phase=='issuance' else 0)
            self.assertFalse(self.db.in_transaction());self.assertNotIn('COMMIT',[sql for sql,_ in self.db.calls])
            self.assertEqual(self.db.calls[-1][0],'EXIT_WITH_ERROR')
    async def test_distinct_thousand_row_bound_accepts_complete_result_and_rejects_overflow(self):
        # Isolate structural/result-size guards from synthetic fake-DB CPU under
        # shared host load. Actual deadline/worker tests use their own clocks;
        # this double establishes no native1000-row latency qualification.
        with patch.object(provision.write,'time',SimpleNamespace(monotonic=lambda:100.)):
            await self._distinct_thousand_row_bound()
    async def _distinct_thousand_row_bound(self):
        rows,_=self.install_children(1000)
        result=await self.execute()
        self.assertEqual(len(result.children),1000)
        self.assertEqual([child.child_id for child in result.children],[row['id'] for row in rows])
        self.assertEqual(len(self.db.issued),1000)
        self.assertLessEqual(len(result.model_dump_json().encode('utf-8')),provision.MAX_RESPONSE_BYTES)
        self.setUp();self.install_children(1001)
        with self.assertRaises(provision.protected.HandlerError) as failed:await self.execute()
        self.assertEqual(failed.exception.error_id,'provision_unavailable')
        self.assertEqual(self.db.issued,[]);self.assertNotIn('COMMIT',[sql for sql,_ in self.db.calls])
    async def test_legal_unicode_response_bytes_over_limit_reject_before_commit(self):
        # Qualify actual UTF-8 size accounting, independently of fake-DB runtime.
        # Production10-second deadlines and separate timing tests are unchanged.
        with patch.object(provision.write,'time',SimpleNamespace(monotonic=lambda:100.)):
            await self._legal_unicode_response_bytes_over_limit()
    async def _legal_unicode_response_bytes_over_limit(self):
        self.install_children(1000,label='😀'*200)
        # Preserve the real serializer, recording actual UTF-8 bytes immediately
        # before the production byte guard; legal labels remain200 codepoints.
        original=provision.Provision.model_dump_json;observed=[]
        def serialize(value,*args,**kwargs):
            body=original(value,*args,**kwargs);observed.append((len(body),len(body.encode('utf-8'))));return body
        with patch.object(provision.Provision,'model_dump_json',serialize):
            with self.assertRaises(provision.protected.HandlerError) as failed:await self.execute()
        self.assertEqual(failed.exception.error_id,'provision_unavailable')
        self.assertLess(observed[0][0],provision.MAX_RESPONSE_BYTES)
        self.assertGreater(observed[0][1],provision.MAX_RESPONSE_BYTES)
        self.assertEqual(len(self.db.issued),1000) # Double records provisional INSERT calls only.
        self.assertNotIn('COMMIT',[sql for sql,_ in self.db.calls]);self.assertFalse(self.db.in_transaction())
