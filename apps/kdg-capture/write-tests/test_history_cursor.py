"""Closed canonical untrusted navigation, with no signing authority."""
import base64,json,unittest
import test_capture_read as support
import capture_history as history

class CursorContract(unittest.TestCase):
    def setUp(self):
        self.context=history.write.VerifiedContext(support.ORG,support.ACCOUNT,support.ACTOR,'own_read',100)
        self.query=history.Query(from_date='2026-10-01',to_date='2026-10-26')
        detail=history.read._snapshot(support.row(),self.context,history.read.Lookup(capture_id=support.CAPTURE))
        self.raw=history.continuation(self.query,self.context,detail);self.value=history.decode_cursor(self.raw).model_dump()
    def test_roundtrip_and_closed_binding(self):
        self.assertEqual(history.decode_cursor(self.raw).last_id,support.CAPTURE)
        self.assertEqual(history.position(self.query,self.context),None)
        self.assertEqual(history.position(history.Query(**{**self.query.model_dump(),'cursor':self.raw}),self.context).account_id,support.ACCOUNT)
    def test_noncanonical_malformed_duplicate_or_wrong_shapes(self):
        b64=lambda v:base64.urlsafe_b64encode(v).decode().rstrip('=')
        for raw in ('','x','x'*2049,self.raw+'=',b64(json.dumps(self.value).encode()),b64(b'{"v":1,"v":1}'),b64(history._canonical(self.value).replace(b'"v":1',b'"v":1.0')),history._encode([]),
          *[history._encode({**self.value,**change}) for change in ({'from_date':'2026-10-27','to_date':'2026-10-26'},{'last_id':'00000000-0000-0000-0000-000000000000'},{'account_id':'00000000-0000-0000-0000-000000000000'},{'org_id':'00000000-0000-0000-0000-000000000000'},{'v':True},{'v':2},{'permission':'other'},{'last_id':'bad'},{'last_created_at':'2026-10-26T00:00:00.000000Z'},{'last_created_at':'2026-10-26T00:00:00+02:00'},{'private':'canary'},{'limit':True},{'from_date':'2026-02-30'})]):
            with self.subTest(raw=raw[:20]),self.assertRaises(history.protected.HandlerError) as failed:history.decode_cursor(raw)
            self.assertEqual((failed.exception.status,failed.exception.error_id),(422,'validation_failed'))
    def test_server_defense_rejects_out_of_order_foreign_or_out_of_filter_rows(self):
        for rows in ([support.row(),support.row()],[{**support.row(),'org_id':support.IDS[0]}],[{**support.row(),'observation_date':__import__('datetime').date(2025,1,1)}]):
            with self.assertRaises(history.write.WriteError):history._page(rows,history.write.Budget(),self.context,self.query)
    def test_private_worker_outcome_repr_never_renders_values_or_errors(self):
        error=ValueError('synthetic_history_cancel_canary')
        for outcome in (history.protected._WorkerOutcome(value={'private':'synthetic_history_cancel_canary'}),history.protected._WorkerOutcome(error=error)):
            self.assertEqual(repr(outcome),'<_WorkerOutcome private>');self.assertNotIn('canary',str(outcome))
    def test_page_size_accounting_does_not_reserialize_included_prefixes(self):
        from unittest.mock import patch
        from uuid import UUID
        rows=[{**support.row(),'capture_id':UUID(f'{n:08x}-aaaa-4aaa-8aaa-{n:012x}')} for n in range(30,0,-1)]
        original=history.HistoryPage.model_dump_json;lengths=[]
        def dump(page,*a,**k):
            lengths.append(len(page.items));return original(page,*a,**k)
        with patch.object(history.HistoryPage,'model_dump_json',dump):
            page=history._page(rows,history.write.Budget(),self.context,self.query)
        self.assertEqual(len(page.items),30)
        self.assertEqual(lengths,[0,30])
