"""Direct handler and shared-boundary regressions with synthetic collaborators."""
import copy
from datetime import timedelta
import json
import unittest
from unittest.mock import patch
from uuid import UUID
import httpx
import test_admin_http as wire
import admin_read as admin
import capture_read as own
import capture_history as history

class DirectAdminAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db=wire.Connection();self.checks=[]
        self.upstream=lambda:httpx.Response(200,json=wire.evidence())
        async def access(request):
            self.assertFalse(self.db.in_transaction());self.checks.append(request);return self.upstream()
        self.handler=admin.AdminReadHandler(org_id=wire.support.ORG,access_url='https://access.invalid',service_key='synthetic',transport=httpx.MockTransport(access))
        self.query=dict(from_date='2026-10-01',to_date='2026-10-26',limit=2)
    async def execute(self,lookup=None,token='Bearer synthetic'):
        return await self.handler.execute(self.db,self.query if lookup is None else lookup,token)
    async def test_direct_foreign_detail_and_page_original_ownership(self):
        detail=await self.execute(wire.support.CAPTURE)
        page=await self.execute()
        self.assertEqual(detail.owner_account_id,wire.FOREIGN)
        self.assertTrue(all(item.owner_account_id==wire.FOREIGN for item in page.items))
        self.assertEqual(set(page.model_dump()),{'account_id','org_id','from_date','to_date','limit','items','next_cursor'})
        self.assertTrue(all(json.loads(request.content)['permission']==admin.PERMISSION for request in self.checks))
        modes=[parameters['mode'] for sql,parameters in self.db.calls if "set_config('app.mode'" in sql]
        self.assertEqual(modes,['all_read','all_read'])
    async def test_admin_detail_validation_runs_after_select_transaction(self):
        original=admin._snapshot;phases=[]
        def snapshot(row,context,lookup):
            self.assertFalse(self.db.in_transaction())
            self.assertEqual(self.db.calls[-1][0],'COMMIT')
            phases.append('validate_original_detail')
            return original(row,context,lookup)
        with patch.object(admin,'_snapshot',side_effect=snapshot):
            detail=await self.execute(wire.support.CAPTURE)
        self.assertEqual(detail.owner_account_id,wire.FOREIGN)
        self.assertEqual(phases,['validate_original_detail'])
    async def test_own_wrapper_still_refuses_foreign_and_all_wrapper_keeps_original(self):
        context=admin.write.VerifiedContext(wire.support.ORG,wire.support.ACCOUNT,wire.support.ACTOR,'all_read',100)
        lookup=own.Lookup(capture_id=wire.support.CAPTURE)
        with self.assertRaisesRegex(admin.write.WriteError,'^capture_unavailable$'):own._snapshot(self.db.detail,context,lookup)
        self.assertEqual(admin._snapshot(self.db.detail,context,lookup).owner_account_id,wire.FOREIGN)
    async def test_missing_stored_owner_remains_invalid_storage_for_both_wrappers(self):
        context=admin.write.VerifiedContext(wire.support.ORG,wire.support.ACCOUNT,wire.support.ACTOR,'all_read',100)
        lookup=own.Lookup(capture_id=wire.support.CAPTURE)
        stored=copy.deepcopy(self.db.detail);del stored['owner_account_id']
        for snapshot in (own._snapshot,admin._snapshot):
            with self.assertRaisesRegex(admin.write.WriteError,'^capture_read_unavailable$'):snapshot(stored,context,lookup)
    async def test_wrong_or_missing_authority_fails_before_sql(self):
        original=wire.evidence()
        changes=[{'permission':history.PERMISSION},{'account_id':None},{'actor_id':None},{'membership_id':'0'},
          {'authorization_scope':dict(kind='organization',org_id=wire.FOREIGN)},
          {'resource_scope':dict(kind='organization',org_id=wire.FOREIGN)},
          {'resource_scope':dict(kind='own_account',account_id=wire.support.ACCOUNT)},
          {'checked_at':'2020-01-01T00:00:00Z'},{'decision_id':None},{'extra':'private'}]
        for field in original:changes.append({field:None})
        for change in changes:
            self.upstream=lambda:httpx.Response(200,json={**original,**change})
            with self.assertRaises(admin.protected.HandlerError) as failed:await self.execute()
            self.assertEqual((failed.exception.status,failed.exception.error_id),(503,'authorization_unavailable'),change)
            self.assertEqual(self.db.calls,[])
    async def test_denial_has_no_own_fallback_and_outage_is_distinct(self):
        for status,error,expected in ((403,'access_denied',403),(401,'authentication_required',401),(409,'identity.actor_setup_required',409),(503,'private',503)):
            self.upstream=lambda:httpx.Response(status,json={'detail':{'code':error}})
            before=len(self.checks)
            with self.assertRaises(admin.protected.HandlerError) as failed:await self.execute()
            self.assertEqual(failed.exception.status,expected)
            self.assertEqual(len(self.checks)-before,1);self.assertEqual(self.db.calls,[])
    async def test_invalid_input_and_bearer_refuse_before_authority(self):
        for lookup in ('bad',{},dict(self.query,limit=True),dict(self.query,owner_account_id=wire.FOREIGN),dict(self.query,cursor='bad')):
            with self.assertRaises(admin.protected.HandlerError) as failed:await self.execute(lookup)
            self.assertEqual(failed.exception.status,422)
        for token in (None,'Basic synthetic','Bearer a,b','Bearer a!b','Bearer a=b'):
            with self.assertRaises(admin.protected.HandlerError) as failed:await self.execute(token=token)
            self.assertEqual(failed.exception.status,401)
        self.assertEqual(self.checks,[]);self.assertEqual(self.db.calls,[])
    async def test_active_or_autocommit_refuses_before_authority(self):
        for active,autocommit in ((True,False),(False,True)):
            self.db.active=active;self.db.autocommit=autocommit
            with self.assertRaises(admin.protected.HandlerError) as failed:await self.execute()
            self.assertEqual(failed.exception.error_id,'invalid_write_context')
        self.assertEqual(self.checks,[])
    async def test_direct_closed_cursor_binding_before_transaction(self):
        page=await self.execute()
        value=admin.decode_cursor(page.next_cursor).model_dump()
        for change in ({'account_id':wire.FOREIGN},{'org_id':wire.FOREIGN},{'from_date':'2026-09-01'},{'limit':3},{'permission':history.PERMISSION}):
            self.db.calls=[]
            cursor=history._encode({**value,**change})
            with self.assertRaises(admin.protected.HandlerError) as failed:await self.execute(dict(self.query,cursor=cursor))
            self.assertEqual(failed.exception.status,422);self.assertEqual(self.db.calls,[])
    async def test_detail_missing_scope_mismatch_and_invalid_storage(self):
        original=copy.deepcopy(self.db.detail)
        for value,status in ((None,404),({**original,'org_id':UUID(wire.FOREIGN)},404),({**original,'capture_id':UUID(wire.FOREIGN)},404),({**original,'answers':{}},503),({**original,'created_by':UUID(wire.FOREIGN)},503)):
            self.db.detail=value
            with self.assertRaises(admin.protected.HandlerError) as failed:await self.execute(wire.support.CAPTURE)
            self.assertEqual(failed.exception.status,status)
    async def test_sql_and_commit_failures_disclose_no_detail(self):
        for phase in ('sql','commit'):
            self.db=wire.Connection()
            if phase=='sql':self.db.fail_execute=True
            else:self.db.fail_commit=True
            with self.assertRaises(admin.protected.HandlerError) as failed:await self.execute()
            self.assertEqual(failed.exception.error_id,'capture_read_unavailable')
            self.assertFalse(self.db.in_transaction())

class CursorAndPacking(unittest.TestCase):
    def setUp(self):
        self.context=admin.write.VerifiedContext(wire.support.ORG,wire.support.ACCOUNT,wire.support.ACTOR,'all_read',100)
        self.query=admin.Query(from_date='2026-10-01',to_date='2026-10-26',limit=2)
        self.detail=admin._snapshot(wire.Connection().detail,self.context,own.Lookup(capture_id=wire.support.CAPTURE))
        self.cursor=admin.continuation(self.query,self.context,self.detail)
    def test_closed_canonical_cursor_and_incompatible_own_mode(self):
        import base64
        self.assertEqual(admin.decode_cursor(self.cursor).permission,admin.PERMISSION)
        with self.assertRaises(admin.protected.HandlerError):history.decode_cursor(self.cursor)
        value=admin.decode_cursor(self.cursor).model_dump()
        bad=['bad','x'*2049,self.cursor+'=']
        for change in ({'v':True},{'v':2},{'extra':1},{'last_created_at':'2026-10-26T00:00:00+00:00'},{'permission':history.PERMISSION}):bad.append(history._encode({**value,**change}))
        duplicate=json.dumps(value)[:-1]+',"v":1}'
        bad.append(base64.urlsafe_b64encode(duplicate.encode()).decode().rstrip('='))
        for raw in bad:
            with self.subTest(raw=raw),self.assertRaises(admin.protected.HandlerError):admin.decode_cursor(raw)
    def test_independent_sql_scope_and_no_activity_prerequisite(self):
        for sql in (admin.DETAIL,admin.HISTORY):
            self.assertIn('c.org_id=CAST(:org AS uuid)',sql)
            self.assertNotIn('c.owner_account_id=CAST(:account AS uuid)',sql)
            self.assertFalse(any(word in sql for word in ('active','assignment','FOR UPDATE')))
        self.assertIn('c.id=CAST(:capture AS uuid)',admin.DETAIL)
        self.assertIn('LIMIT :row_limit',admin.HISTORY)
        self.assertIn('c.observation_date>=CAST(:from_date AS date)',admin.HISTORY)
        self.assertIn('c.observation_date<=CAST(:to_date AS date)',admin.HISTORY)
        self.assertIn('CAST(:last_id AS uuid) IS NULL OR (c.created_at,c.id)<(CAST(:last_created_at AS timestamptz),CAST(:last_id AS uuid))',admin.HISTORY)
        self.assertIn('ORDER BY c.created_at DESC,c.id DESC LIMIT :row_limit',admin.HISTORY)
    def test_invalid_omitted_row_refuses_whole_page_and_order(self):
        rows=wire.Connection().rows
        rows.sort(key=lambda r:str(r['capture_id']),reverse=True)
        for change in ('invalid','duplicate','date','foreign'):
            selected=copy.deepcopy(rows[:3])
            if change=='invalid':selected[2]['answers']={}
            elif change=='duplicate':selected[1]=copy.deepcopy(selected[0])
            elif change=='date':selected[2]['observation_date']=__import__('datetime').date(2026,9,1)
            else:selected[2]['org_id']=UUID(wire.FOREIGN)
            with self.assertRaises(admin.write.WriteError):admin._page(selected,admin.write.Budget(),self.context,self.query,None)
