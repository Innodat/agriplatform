"""Synthetic current-detail acceptance. No native/storage qualification."""
from datetime import date, datetime, timezone
from uuid import UUID
import unittest
import httpx
import test_capture_create_handler as support
import capture_read as read
from questionnaire import initial_definition

ORG=support.ORG
CAPTURE=support.STORED_CAPTURE
ACCOUNT=support.ACCOUNT
ACTOR=support.ACTOR
IDS=['11111111-1111-4111-8111-11111111111'+str(i) for i in range(1,5)]
DEFINITION=initial_definition(IDS).model_dump(mode='json')
def row():
    now=datetime(2026,10,26,tzinfo=timezone.utc)
    return dict(capture_id=UUID(CAPTURE),org_id=UUID(ORG),owner_account_id=UUID(ACCOUNT),
        owner_actor_id=UUID(ACTOR),child_id=UUID(IDS[0]),child_label='Original child',
        questionnaire_id=UUID(IDS[1]),questionnaire_version_id=UUID(IDS[2]),questionnaire_version=1,
        revision=1,observation_date=date(2026,10,26),answers={IDS[0]:{'value':3},**{i:{'value':False} for i in IDS[1:]}},
        captured_at='2026-10-26t10:00:00z',created_by=UUID(ACTOR),created_at=now,updated_by=UUID(ACTOR),updated_at=now,definition=DEFINITION)

class Connection(support.Connection):
    def __init__(self):super().__init__();self.detail=row()
    def execute(self,sql,parameters):
        if str(sql)==getattr(read,'DETAIL',None):
            self.calls.append((str(sql),parameters));return support.support.Rows(self.detail)
        return super().execute(sql,parameters)

class ReadAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db=Connection();self.checks=[]
        self.upstream=lambda:httpx.Response(200,json=support.evidence(read.recovery.PERMISSION))
        async def access(request):
            self.assertFalse(self.db.in_transaction());self.checks.append(request);return self.upstream()
        self.handler=read.ReadHandler(org_id=ORG,access_url='https://access.invalid',service_key='synthetic',transport=httpx.MockTransport(access))
    async def execute(self,capture=CAPTURE):return await self.handler.execute(self.db,capture,'Bearer synthetic')
    async def test_current_own_detail_contains_original_definition_and_provenance(self):
        result=await self.execute()
        self.assertEqual(result.capture_id,CAPTURE)
        self.assertEqual(result.revision,'1')
        self.assertEqual(result.definition.model_dump(mode='json'),DEFINITION)
        self.assertEqual(result.child_label,'Original child')
        self.assertEqual(result.owner_actor_id,ACTOR)
        self.assertEqual(self.db.calls[-1][0],'COMMIT')
    async def test_after_edit_current_revision_is_independent_of_receipts(self):
        self.db.detail['revision']=2
        self.assertEqual((await self.execute()).revision,'2')
    async def test_missing_and_foreign_have_same_safe_404(self):
        for value in (None,{**row(),'owner_account_id':UUID(IDS[0])},{**row(),'org_id':UUID(IDS[0])},{**row(),'capture_id':UUID(IDS[0])}):
            self.db.detail=value
            with self.assertRaises(read.protected.HandlerError) as failed:await self.execute()
            self.assertEqual((failed.exception.status,failed.exception.error_id),(404,'capture_unavailable'))
    async def test_read_ignores_assignment_active_and_create_eligibility(self):
        self.db.replay_assignment=None
        await self.execute()
        sql=[s for s,_ in self.db.calls]
        self.assertEqual(sum(s==read.DETAIL for s in sql),1)
        self.assertFalse(any('FOR UPDATE' in s or 'pg_advisory' in s or s.startswith(('UPDATE','INSERT','DELETE')) for s in sql))
        self.assertIn('c.owner_account_id=CAST(:account AS uuid)',read.DETAIL)
        self.assertIn('c.org_id=CAST(:org AS uuid)',read.DETAIL)
    async def test_bad_storage_never_publishes_partial_snapshot(self):
        for change in ({'revision':0},{'revision':True},{'questionnaire_version':0},{'owner_actor_id':None},
                {'created_by':UUID(IDS[0])},{'captured_at':None},{'created_at':datetime(2026,10,26)},{'definition':{}},{'answers':{}},
                {'child_label':'x'*201},{'answers':{IDS[0]:{'value':True}}}):
            self.db.detail={**row(),**change}
            with self.assertRaises(read.protected.HandlerError) as failed:await self.execute()
            self.assertEqual((failed.exception.status,failed.exception.error_id),(503,'capture_read_unavailable'))
    async def test_denial_and_bad_actor_never_select(self):
        for response in (httpx.Response(403,json={'detail':{'code':'access_denied'}}),httpx.Response(200,json={**support.evidence(read.recovery.PERMISSION),'actor_id':None})):
            self.upstream=lambda:response
            with self.assertRaises(read.protected.HandlerError):await self.execute()
            self.assertEqual(self.db.calls,[])
    async def test_invalid_id_never_checks_authority(self):
        with self.assertRaises(read.protected.HandlerError) as failed:await self.execute('bad')
        self.assertEqual(failed.exception.status,422);self.assertFalse(self.checks)

    async def test_oversized_valid_storage_is_safe_unavailable(self):
        ids=[f'{n:08x}-bbbb-4bbb-8bbb-{n:012x}' for n in range(1,51)]
        self.db.detail.update(definition=dict(schema_version=1,questions=[dict(id=i,type='text',label='Text',required=True) for i in ids]),answers={i:{'value':'😀'*5000} for i in ids})
        with self.assertRaises(read.protected.HandlerError) as failed:await self.execute()
        self.assertEqual((failed.exception.status,failed.exception.error_id),(503,'capture_read_unavailable'))

    async def test_near_limit_compact_multilingual_original_definition_round_trips(self):
        import json
        from questionnaire import parse_definition, MAX_DEFINITION_BYTES
        ids=[f'{n:08x}-bbbb-4bbb-8bbb-{n:012x}' for n in range(1,51)]
        definition=dict(schema_version=1,questions=[dict(id=i,type='boolean',label='漢'*500,required=True,default=False,details_enabled=True,details_label='漢'*320) for i in ids])
        raw=json.dumps(definition,ensure_ascii=False,separators=(',',':')).encode('utf-8')
        self.assertGreater(len(raw),MAX_DEFINITION_BYTES-4096)
        self.assertLessEqual(len(raw),MAX_DEFINITION_BYTES)
        expected=parse_definition(raw)
        self.db.detail.update(definition=definition,answers={i:{'value':False} for i in ids})
        result=await self.execute()
        self.assertEqual(result.definition,expected)
    async def test_aware_session_offset_timestamps_normalize_to_the_same_utc_instant(self):
        from datetime import timedelta
        original=row();self.db.detail.update(created_at=original['created_at'].astimezone(timezone(timedelta(hours=2))),updated_at=original['updated_at'].astimezone(timezone(timedelta(hours=-5))))
        result=await self.execute()
        self.assertEqual(result.created_at,'2026-10-26T00:00:00Z')
        self.assertEqual(result.updated_at,result.created_at)
