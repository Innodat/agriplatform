"""Actual own-edit orchestration with synthetic Access and recorded connections."""
import asyncio
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID

import httpx
import test_capture_edit as body
import test_capture_create_handler as access
import capture_edit_handler as handler

write=body.write
ORG,ACCOUNT,ACTOR,CAPTURE,OPERATION=body.ORG,body.ACCOUNT,body.ACTOR,body.CAPTURE,body.OPERATION
READ='kdg_capture.capture.read.own'
EDIT='kdg_capture.capture.edit.own'

class Connection(body.Connection):
    def __init__(self):
        super().__init__();self.target=dict(id=UUID(access.STORED_CAPTURE),org_id=UUID(ORG),owner_account_id=UUID(ACCOUNT))
    def execute(self,sql,parameters):
        result=super().execute(sql,parameters)
        if str(sql)==handler.TARGET:return body.Rows(self.target)
        return result

def stored():
    row=access.stored();row['command_type']='capture.edit';row['result']['revision']='2'
    return row

class HandlerAcceptance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db=Connection();self.requests=[]
        self.upstream=lambda permission:httpx.Response(200,json=access.evidence(permission))
        async def check(request):
            self.assertEqual(self.db.calls,[])
            permission=json.loads(request.content)['permission'];self.requests.append(permission)
            result=self.upstream(permission)
            return await result if hasattr(result,'__await__') else result
        self.handler=handler.EditHandler(org_id=ORG,access_url='https://access.invalid',service_key='synthetic',transport=httpx.MockTransport(check))
    async def execute(self,command=None,capture=CAPTURE,authorization='Bearer synthetic'):
        return await self.handler.execute(self.db,capture,json.dumps((command or body.command()).model_dump()),authorization)
    def mutations(self):return [(sql,args) for sql,args in self.db.calls if sql.startswith(('INSERT','UPDATE','DELETE'))]
    async def test_fresh_requires_both_current_capabilities_and_actual_body(self):
        receipt=await self.execute()
        self.assertEqual(self.requests,[READ,EDIT]);self.assertEqual(receipt.result.revision,'5')
        self.assertEqual(len(self.mutations()),3);self.assertEqual(self.db.calls[-1][0],'COMMIT')
    async def test_noop_uses_actual_body_without_assignment_or_child(self):
        self.db.unchanged=True;self.db.assignment=None;self.db.child=None
        receipt=await self.execute()
        self.assertEqual(receipt.result.revision,'4');self.assertEqual(len(self.mutations()),1)
    async def test_duplicate_authorizes_stored_target_and_ignores_proposal_semantics(self):
        self.db.existing=stored()
        receipt=await self.execute(body.command(answers={},expected_revision='1'),capture=ACTOR)
        self.assertEqual((receipt.result.capture_id,receipt.result.revision),(access.STORED_CAPTURE,'2'))
        targets=[args for sql,args in self.db.calls if sql==handler.TARGET]
        self.assertEqual(targets[0]['capture'],access.STORED_CAPTURE)
        self.assertFalse(any('FOR UPDATE' in sql for sql,_ in self.db.calls));self.assertEqual(self.mutations(),[])
    async def test_missing_foreign_or_malformed_stored_target_is_private(self):
        for target in (None,{},
            dict(id=UUID(CAPTURE),org_id=UUID(ORG),owner_account_id=UUID(ACCOUNT)),
            dict(id=UUID(access.STORED_CAPTURE),org_id=UUID(ACTOR),owner_account_id=UUID(ACCOUNT)),
            dict(id=UUID(access.STORED_CAPTURE),org_id=UUID(ORG),owner_account_id=UUID(ACTOR))):
            self.db=Connection();self.db.existing=stored();self.db.target=target
            with self.assertRaises(handler.HandlerError) as failed:await self.execute()
            self.assertEqual((failed.exception.status,failed.exception.error_id),(503,'operation_verification_unavailable'))
            self.assertEqual(self.mutations(),[])
    async def test_malformed_outcome_is_private(self):
        self.db.existing=stored();self.db.existing['result']['revision']='0'
        with self.assertRaises(handler.HandlerError) as failed:await self.execute()
        self.assertEqual(failed.exception.error_id,'operation_verification_unavailable')
    async def test_stale_unchanged_conflict_has_only_current_revision(self):
        self.db.unchanged=True
        with self.assertRaises(handler.RevisionConflictError) as failed:await self.execute(body.command(expected_revision='3'))
        self.assertEqual((failed.exception.status,failed.exception.error_id,failed.exception.current_revision),(409,'kdg_capture.capture_revision_conflict','4'))
        self.assertEqual(self.mutations(),[])
    async def test_missing_fresh_capture_is_safe_404(self):
        self.db.capture=None
        with self.assertRaises(handler.HandlerError) as failed:await self.execute()
        self.assertEqual((failed.exception.status,failed.exception.error_id),(404,'capture_unavailable'))
    async def test_denial_of_either_never_falls_back_or_enters_sql(self):
        for denied in (READ,EDIT):
            self.requests=[]
            self.upstream=lambda permission:httpx.Response(403,json={'detail':{'code':'access_denied'}}) if permission==denied else httpx.Response(200,json=access.evidence(permission))
            with self.assertRaises(handler.HandlerError) as failed:await self.execute()
            self.assertEqual((failed.exception.status,failed.exception.error_id),(403,'access_denied'))
            self.assertEqual(self.requests,[READ] if denied==READ else [READ,EDIT]);self.assertEqual(self.db.calls,[])
    async def test_pair_must_match_account_actor_membership_scope(self):
        changes=[{'account_id':ACTOR},{'actor_id':CAPTURE},{'membership_id':'8'},
            {'authorization_scope':{'kind':'organization','org_id':ACTOR}},
            {'resource_scope':{'kind':'own_account','account_id':ACTOR}}]
        for change in changes:
            self.upstream=lambda permission:httpx.Response(200,json=dict(access.evidence(permission),**(change if permission==EDIT else {})))
            with self.assertRaises(handler.HandlerError) as failed:await self.execute()
            self.assertEqual((failed.exception.status,failed.exception.error_id),(503,'authorization_unavailable'))
            self.assertEqual(self.db.calls,[])
    async def test_older_observation_is_not_renewed_by_second_check(self):
        now=100.0
        def check(permission):
            nonlocal now
            if permission==EDIT:now+=1.1
            return httpx.Response(200,json=access.evidence(permission))
        self.upstream=check
        with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):
            with self.assertRaises(handler.HandlerError) as failed:await self.execute()
        self.assertEqual(failed.exception.error_id,'authorization_observation_expired')
        self.assertFalse(any('kdg_capture.' in sql for sql,_ in self.db.calls))
    async def test_access_closed_decoding_rejects_untrusted_evidence_before_sql(self):
        malformed=[dict(access.evidence(EDIT),unexpected='private'),
            dict(access.evidence(EDIT),checked_at='2020-01-01T00:00:00Z'),
            dict(access.evidence(EDIT),actor_id='00000000-0000-0000-0000-000000000000'),
            dict(access.evidence(EDIT),membership_id='0'),
            dict(access.evidence(EDIT),permission='kdg_capture.capture.edit.all')]
        responses=[httpx.Response(200,json=value) for value in malformed]+[
            httpx.Response(200,content=b'{"account_id":"private","account_id":"duplicate"}'),
            httpx.Response(200,content=b'x'*16385),httpx.Response(200,content=b'not JSON'),
            httpx.Response(500,json={'detail':{'code':'private-upstream'}})]
        for response in responses:
            self.upstream=lambda permission:response if permission==EDIT else httpx.Response(200,json=access.evidence(permission))
            with self.assertRaises(handler.HandlerError) as failed:await self.execute()
            self.assertEqual((failed.exception.status,failed.exception.error_id),(503,'authorization_unavailable'))
            self.assertEqual(self.db.calls,[])
    async def test_both_checks_receive_same_scoped_bearer_and_service_boundary(self):
        captured=[]
        async def upstream(request):
            captured.append(request)
            return httpx.Response(200,json=access.evidence(json.loads(request.content)['permission']))
        self.handler._transport=httpx.MockTransport(upstream)
        await self.execute()
        self.assertEqual(len(captured),2)
        for request in captured:
            self.assertEqual(request.headers['authorization'],'Bearer synthetic')
            self.assertEqual(request.headers['x-service-key'],'synthetic')
            self.assertEqual(json.loads(request.content)['authorization_scope'],dict(kind='organization',org_id=ORG))
    async def test_original_budget_context_and_actual_body_identity_are_preserved(self):
        original=handler._transaction;seen=[]
        def transaction(conn,budget,context,proposal,evidence):
            seen.append((budget,context))
            with patch.object(handler.edit,'edit_in_transaction',wraps=handler.edit.edit_in_transaction) as actual:
                result=original(conn,budget,context,proposal,evidence)
                self.assertIs(actual.call_args.args[1],budget)
                self.assertIs(actual.call_args.args[2],context)
            return result
        with patch.object(handler,'_transaction',side_effect=transaction):await self.execute()
        self.assertEqual(len(seen),1)
        self.assertEqual(seen[0][1].mode,'own_write')
    async def test_operation_contention_has_safe_busy_result_without_business_write(self):
        from sqlalchemy.exc import OperationalError
        class Busy(Exception):sqlstate='55P03'
        original=self.db.execute
        def execute(sql,args):
            if 'pg_advisory_xact_lock' in str(sql):raise OperationalError('private',{},Busy('private'))
            return original(sql,args)
        self.db.execute=execute
        with self.assertRaises(handler.HandlerError) as failed:await self.execute()
        self.assertEqual((failed.exception.status,failed.exception.error_id),(409,'operation_busy'))
        self.assertEqual(self.mutations(),[])
    async def test_parse_precedes_access_even_for_duplicate(self):
        for raw,path in ((b'{}',CAPTURE),(json.dumps(body.command().model_dump()),'invalid'),
            (b'{"command_version":2}',CAPTURE),(b'{"command_version":1,"command_version":1}',CAPTURE)):
            with self.assertRaises(handler.HandlerError):await self.handler.execute(self.db,path,raw,'Bearer synthetic')
        self.assertEqual(self.requests,[]);self.assertEqual(self.db.calls,[])
    async def test_sql_commit_failure_and_late_commit_never_acknowledge(self):
        for phase in ('sql','commit','late'):
            self.db=Connection();now=100.0
            if phase=='sql':self.db.failure='UPDATE kdg_capture.capture'
            if phase=='commit':self.db.fail_commit=True
            if phase=='late':
                def late():
                    nonlocal now
                    now=111.0
                self.db.on_commit=late
            with patch.object(write,'time',SimpleNamespace(monotonic=lambda:now)):
                with self.assertRaises(handler.HandlerError) as failed:await self.execute()
            self.assertEqual(failed.exception.error_id,'execution_timeout' if phase=='late' else 'internal_error')

if __name__=='__main__':unittest.main()
