"""Direct authorization, metadata validation and canonical cursor regressions."""
from pathlib import Path
import sys

sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'write-candidate'),str(Path(__file__).resolve().parents[1]/'api')]

import base64
import copy
from datetime import datetime, timedelta, timezone
import json
import unittest
from unittest.mock import patch
import httpx
import audit_read as audit
import capture_read as own
import test_audit_http as wire

class AuditDirect(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db=wire.Connection();self.checks=[]
        self.upstream=lambda:httpx.Response(200,json=wire.wire.evidence())
        async def access(request):self.checks.append(request);return self.upstream()
        self.handler=audit.AuditReadHandler(org_id=wire.wire.support.ORG,access_url='https://access.invalid',service_key='synthetic',transport=httpx.MockTransport(access))
        self.query=dict(capture_id=wire.wire.support.CAPTURE,limit=2)
    async def execute(self,query=None,token='Bearer synthetic'):
        return await self.handler.execute(self.db,self.query if query is None else query,token)
    async def test_cross_owner_metadata_and_validation_after_transaction(self):
        original=audit._page
        def page(*args):
            self.assertFalse(self.db.in_transaction());self.assertEqual(self.db.calls[-1][0],'COMMIT')
            return original(*args)
        with patch.object(audit,'_page',side_effect=page):result=await self.execute()
        self.assertEqual(result.owner_account_id,wire.wire.FOREIGN)
        self.assertEqual([e.revision for e in result.events],['5','4'])
        self.assertEqual(sum('FROM kdg_capture.capture c' in sql for sql,_ in self.db.calls),1)
        self.assertEqual([p['mode'] for sql,p in self.db.calls if "set_config('app.mode'" in sql],['all_read'])
        context=audit.write.VerifiedContext(wire.wire.support.ORG,wire.wire.support.ACCOUNT,wire.wire.support.ACTOR,'all_read',100)
        with self.assertRaisesRegex(audit.write.WriteError,'capture_unavailable'):own._snapshot(self.db.detail,context,own.Lookup(capture_id=self.query['capture_id']))
    async def test_repeated_reads_preserve_identical_metadata(self):
        first=await self.execute();second=await self.execute()
        self.assertEqual(first,second);self.assertEqual(len(self.db.events),5)
    async def test_invalid_query_bearer_transaction_and_autocommit(self):
        for query in ({},dict(self.query,limit=True),dict(self.query,answers={}),dict(self.query,cursor='bad')):
            with self.assertRaises(audit.protected.HandlerError) as raised:await self.execute(query)
            self.assertEqual(raised.exception.status,422)
        for token in (None,'Basic a','Bearer a,b','Bearer a!'):
            with self.assertRaises(audit.protected.HandlerError) as raised:await self.execute(token=token)
            self.assertEqual(raised.exception.status,401)
        for active,auto in ((True,False),(False,True)):
            self.db.active=active;self.db.autocommit=auto
            with self.assertRaises(audit.protected.HandlerError) as raised:await self.execute()
            self.assertEqual(raised.exception.error_id,'invalid_write_context')
        self.assertEqual((self.checks,self.db.calls),([],[]))
    async def test_denial_and_authority_setup_and_outage_without_own_fallback(self):
        for status,error in ((401,'authentication_required'),(403,'access_denied'),(409,'identity.actor_setup_required'),(503,'private')):
            self.upstream=lambda:httpx.Response(status,json={'detail':{'code':error}})
            with self.assertRaises(audit.protected.HandlerError) as raised:await self.execute()
            self.assertEqual(raised.exception.status,status)
        self.assertEqual(self.db.calls,[]);self.assertEqual(len(self.checks),4)
    async def test_direct_sql_and_commit_failure(self):
        for phase in ('fail_execute','fail_commit'):
            self.db=wire.Connection();setattr(self.db,phase,True)
            with self.assertRaises(audit.protected.HandlerError) as raised:await self.execute()
            self.assertEqual(raised.exception.error_id,'capture_read_unavailable')
            self.assertFalse(self.db.in_transaction())

class CursorAndRows(unittest.TestCase):
    def setUp(self):
        self.db=wire.Connection()
        self.context=audit.write.VerifiedContext(wire.wire.support.ORG,wire.wire.support.ACCOUNT,wire.wire.support.ACTOR,'all_read',100)
        self.query=audit.Query(capture_id=wire.wire.support.CAPTURE,limit=2)
        self.rows=[{**self.db.header,**event} for event in reversed(self.db.events)]
        self.page=self.page_for(self.rows[:3]);self.cursor=self.page.next_cursor
    def page_for(self,rows,query=None):return audit._page(rows,audit.write.Budget(),self.context,query or self.query,None)
    def test_closed_canonical_cursor_rejects_alternate_and_duplicate_syntax(self):
        value=audit.decode_cursor(self.cursor).model_dump()
        bad=['bad','x'*2049,self.cursor+'=']
        for change in ({'v':True},{'v':2},{'extra':1},{'last_revision':0},{'last_revision':'01'},{'last_revision':True},{'permission':'kdg_capture.capture.read.own'}):bad.append(audit.admin.history._encode({**value,**change}))
        for text in (json.dumps(value),json.dumps(value)[:-1]+',"v":1}'):
            bad.append(base64.urlsafe_b64encode(text.encode()).decode().rstrip('='))
        for raw in bad:
            with self.subTest(raw=raw),self.assertRaises(audit.protected.HandlerError):audit.decode_cursor(raw)
        for change in ({'org_id':wire.wire.FOREIGN},{'account_id':wire.wire.FOREIGN},{'capture_id':wire.wire.FOREIGN},{'limit':3}):
            query=self.query.model_copy(update={'cursor':audit.admin.history._encode({**value,**change})})
            with self.assertRaises(audit.protected.HandlerError):audit.position(query,self.context)
    def test_independently_scoped_single_metadata_sql(self):
        sql=audit.EVENTS
        for token in ('LEFT JOIN LATERAL','c.org_id=CAST(:org AS uuid)','c.id=CAST(:capture AS uuid)','org_id=CAST(:org AS uuid) AND capture_id=CAST(:capture AS uuid)','revision<CAST(:last_revision AS bigint)','ORDER BY revision DESC LIMIT :row_limit'):
            self.assertIn(token,sql)
        for token in ('answers','definition','operation_outcome','outcome_id','operation_id','active','assignment','FOR UPDATE'):
            self.assertNotIn(token,sql)
    def test_lookahead_row_and_all_header_and_event_fields_validated(self):
        corruptions=[('event_revision',True),('event_revision',2**63),('event_revision',5),('command_type','capture.create'),('executor_actor_id',None),('initiator_actor_id','bad'),('recorded_at',None)]
        corruptions.extend((key,None) for key in audit.HEADER)
        for key,value in corruptions:
            rows=copy.deepcopy(self.rows[:3]);rows[2][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(audit.write.WriteError):self.page_for(rows)
        for key in audit.HEADER:
            rows=copy.deepcopy(self.rows[:3])
            for row in rows:row.pop(key)
            with self.subTest(missing=key),self.assertRaises(audit.write.WriteError):self.page_for(rows)
    def test_canonical_unequal_actor_provenance_is_rejected(self):
        query=self.query.model_copy(update={'limit':5})
        for predicate in ('creation_header','creation_event','latest_event'):
            rows=copy.deepcopy(self.rows)
            if predicate=='creation_header':
                for row in rows:row['created_by']=wire.wire.FOREIGN
                self.assertNotEqual(str(rows[0]['created_by']),str(rows[0]['owner_actor_id']))
            elif predicate=='creation_event':
                rows[-1]['executor_actor_id']=wire.wire.FOREIGN
                self.assertNotEqual(str(rows[-1]['executor_actor_id']),str(rows[-1]['owner_actor_id']))
            else:
                rows[0]['executor_actor_id']=wire.wire.support.ACTOR
                self.assertNotEqual(str(rows[0]['executor_actor_id']),str(rows[0]['updated_by']))
            with self.subTest(predicate=predicate),self.assertRaisesRegex(audit.write.WriteError,'^capture_read_unavailable$'):
                self.page_for(rows,query)
    def test_aware_offset_timestamps_normalize_to_utc_without_changing_instant(self):
        rows=copy.deepcopy(self.rows[:3]);offset=timezone(timedelta(hours=2))
        for row in rows:
            for key in ('created_at','updated_at','recorded_at'):row[key]=row[key].astimezone(offset)
        page=self.page_for(rows)
        for field in ('created_at','updated_at'):
            actual=getattr(page,field)
            self.assertTrue(actual.endswith('Z'))
            self.assertEqual(datetime.fromisoformat(actual),rows[0][field])
        self.assertTrue(page.events[0].recorded_at.endswith('Z'))
        self.assertEqual(datetime.fromisoformat(page.events[0].recorded_at),rows[0]['recorded_at'])
    def test_numeric_order_not_timestamp_and_first_page_current_evidence_required(self):
        self.assertGreater(self.rows[-1]['recorded_at'],self.rows[0]['recorded_at'])
        self.assertEqual([e.revision for e in self.page.events],['5','4'])
        for rows in (self.rows[1:3],self.rows[:4],[self.rows[0],self.rows[0]]):
            with self.assertRaises(audit.write.WriteError):self.page_for(rows)
        empty=[{**self.db.header,**dict.fromkeys(audit.EVENT_FIELDS)}]
        with self.assertRaises(audit.write.WriteError):self.page_for(empty)
        self.assertEqual(self.page_for(empty,self.query.model_copy(update={'cursor':self.cursor})).events,[])
    def test_largest_numeric_revision_page_and_actual_serialized_bound(self):
        current=2**63-1
        header={**self.db.header,'current_revision':current}
        rows=[{**header,**self.db.events[-1],'event_revision':current-i} for i in range(101)]
        query=self.query.model_copy(update={'limit':100})
        page=self.page_for(rows,query)
        self.assertEqual(len(page.events),100);self.assertLessEqual(len(page.model_dump_json().encode('utf-8')),65536)
        self.assertEqual(audit.decode_cursor(page.next_cursor).last_revision,str(current-99))
        with patch.object(audit.AuditPage,'model_dump_json',return_value='😀'*16385):
            with self.assertRaisesRegex(audit.write.WriteError,'capture_read_unavailable'):self.page_for(rows,query)
