"""Unmounted KDG create/retry orchestration; no engine, route or startup I/O.

The embedding owner supplies ONE exclusive already-open connection, acquired under
its bounded connection policy with no transaction. It must retain ownership until
execute() completes, including cancellation/worker unwind. Never share the connection
with another request. Header multiplicity/body streaming belong to the future HTTP
adapter. Tests inject MockTransport; this module never provisions authority or storage.
"""
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import re
from typing import Literal
from urllib.parse import urlsplit
from uuid import UUID

import anyio
import httpx
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool

from context import Context, canonical_uuid
from capture_commands import CommandError, parse_create
import capture_create as create

write = create.write
ACCESS_SECONDS = 3.0
MAX_RESPONSE_BYTES = 16384


class CreateEvidence(Context):
    permission: Literal['kdg_capture.capture.create.all', 'kdg_capture.capture.create.assigned']


class HandlerError(Exception):
    """Allowlisted safe HTTP adaptation data, no raw upstream/database exception."""
    def __init__(self, status, error_id):
        self.status, self.error_id = status, error_id
        super().__init__(error_id)


WRITE_STATUS = {
    'validation_failed': 422, 'unsupported_command_version': 422,
    'assignment_unavailable': 403, 'child_eligibility_unavailable': 409,
    'questionnaire_version_unavailable': 409, 'operation_busy': 409,
    'operation_verification_unavailable': 503, 'authorization_observation_expired': 503,
    'execution_timeout': 503, 'invalid_write_context': 500, 'internal_error': 500,
}


def _closed_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate_key')
        result[key] = value
    return result


STORED_CAPTURE = '''SELECT id,org_id,owner_account_id,child_id FROM kdg_capture.capture
WHERE org_id=CAST(:org AS uuid) AND owner_account_id=CAST(:account AS uuid)
AND id=CAST(:capture AS uuid)'''


def _transaction(conn, budget, context, command, evidence):
    with write.transaction(conn, budget, context):
        key = write.OutcomeKey('kdg_capture', context.org_id, context.account_id,
                               'capture.create', command.operation_id)
        write.outcome_lock(conn, budget, key, context)
        found = create.outcomes.lookup_private(conn, budget, key, context)
        if found is None:
            # Reentrant operation lock + repeated absence check are intentional:
            # preserve the existing independently protected fresh body unchanged.
            receipt = create.create_in_transaction(conn, budget, context, command,
                membership_id=evidence.membership_id, permission=evidence.permission)
        else:
            # This projection is private; no received target participates.
            target = create._one(conn, budget, STORED_CAPTURE, dict(
                org=context.org_id, account=context.account_id, capture=found.result.capture_id))
            try:
                normalized = {key: str(value) if isinstance(value, UUID) else value
                              for key, value in dict(target).items()}
                if (normalized['id'], normalized['org_id'], normalized['owner_account_id']) != (
                    found.result.capture_id, context.org_id, context.account_id):
                    raise ValueError('foreign_target')
                child_id = canonical_uuid(normalized['child_id'])
            except (ValueError, TypeError, KeyError):
                raise write.WriteError('operation_verification_unavailable') from None
            create.child_lock(conn, budget, context, child_id)
            if evidence.permission == create.ASSIGNED:
                assignment = create._one(conn, budget, create.ASSIGNMENT,
                    dict(org=context.org_id, account=context.account_id, child=child_id))
                if (assignment is None or assignment['active'] is not True
                    or assignment['membership_id'] != int(evidence.membership_id)):
                    raise write.WriteError('assignment_unavailable')
            receipt = found.receipt()
    # The managed helper checks after commit too. No provisional receipt crosses
    # this boundary on commit failure or a late acknowledgement.
    budget.remaining()
    return receipt


async def _worker(conn, budget, context, command, evidence, transaction=None):
    try:
        # AnyIO cancels limiter admission on expiry. Once started, its default
        # non-abandoning worker scope awaits completion; SQL has the same Budget.
        with anyio.fail_after(budget.remaining()):
            return await run_in_threadpool(transaction or _transaction, conn, budget, context, command, evidence)
    except TimeoutError:
        raise write.WriteError('execution_timeout') from None


@dataclass(frozen=True,repr=False)
class _WorkerOutcome:
    # A completed private task must never render a receipt, SQL or raw exception,
    # including asyncio debug/task diagnostics after outer cancellation.
    value: object = None
    error: Exception | None = None
    def __repr__(self):return '<_WorkerOutcome private>'


async def _worker_outcome(conn,budget,context,command,evidence,transaction=None):
    try:
        return _WorkerOutcome(value=await _worker(conn,budget,context,command,evidence,transaction))
    except Exception as error:
        return _WorkerOutcome(error=error)


async def _complete_worker(conn, budget, context, command, evidence, transaction=None):
    # Python3.15 shield logs the inner task's raw exception after cancellation,
    # even when an owner later retrieves it. Shield a non-raising private outcome;
    # only a current, uncancelled owner unwraps the result/error below.
    task = asyncio.create_task(_worker_outcome(conn, budget, context, command, evidence, transaction))
    try:
        outcome = await asyncio.shield(task)
    except asyncio.CancelledError:
        # Repeated cancellation cannot release the connection before unwind.
        while not task.done():
            try:
                await asyncio.shield(task)
            except asyncio.CancelledError:
                pass
        if not task.cancelled():
            task.result()  # Consume privately; never unwrap a cancelled attempt.
        raise
    if outcome.error is not None:
        raise outcome.error
    return outcome.value


class CreateHandler:
    _permissions = (create.ALL, create.ASSIGNED)
    _evidence_type = CreateEvidence

    def __init__(self, *, org_id, access_url, service_key, transport=None):
        try:
            canonical_uuid(org_id)
            url = urlsplit(access_url)
            if (url.scheme != 'https' or not url.hostname or url.username or url.password
                or url.query or url.fragment or url.path not in ('', '/')
                or url.netloc.endswith(':') or (url.port is not None and url.port == 0)
                or not isinstance(service_key, str) or not service_key
                or any(not 33 <= ord(c) <= 126 for c in service_key)):
                raise ValueError('invalid_configuration')
        except (ValueError, TypeError, AttributeError):
            raise RuntimeError('kdg_create_configuration_invalid') from None
        self.org_id, self.access_url = org_id, access_url.rstrip('/')
        self._service_key, self._transport = service_key, transport

    def _resource_matches(self, evidence):
        return evidence.resource_scope.account_id == evidence.account_id

    async def _authorize(self, token, budget):
        try:
            # One total window bounds both capability checks, transport AND body.
            async with asyncio.timeout(min(ACCESS_SECONDS, budget.remaining())):
                async with httpx.AsyncClient(transport=self._transport, timeout=ACCESS_SECONDS,
                    follow_redirects=False, trust_env=False) as client:
                    for permission in self._permissions:
                        observed_start = datetime.now(timezone.utc)
                        async with client.stream('POST', self.access_url + '/v2/check',
                            headers={'Authorization': token, 'X-Service-Key': self._service_key,
                                     'Accept-Encoding': 'identity'},
                            json={'permission': permission, 'authorization_scope': {
                                  'kind': 'organization', 'org_id': self.org_id}}) as upstream:
                            if upstream.headers.get('content-encoding', '').strip().lower() not in ('', 'identity'):
                                raise ValueError('unsupported_encoding')
                            raw = bytearray()
                            async for chunk in upstream.aiter_bytes():
                                if len(raw) + len(chunk) > MAX_RESPONSE_BYTES:
                                    raise ValueError('response_too_large')
                                raw.extend(chunk)
                            body = json.loads(raw.decode('utf-8'), object_pairs_hook=_closed_object,
                                parse_constant=lambda _: (_ for _ in ()).throw(ValueError('invalid_constant')))
                            if upstream.status_code != 200:
                                detail = body.get('detail') if isinstance(body, dict) else None
                                code = detail.get('code') if isinstance(detail, dict) else None
                                if upstream.status_code == 403 and code == 'access_denied':
                                    if permission == create.ALL:
                                        continue
                                    raise HandlerError(403, 'access_denied')
                                if (upstream.status_code, code) in (
                                    (401, 'authentication_required'), (409, 'identity.actor_setup_required')):
                                    raise HandlerError(upstream.status_code, code)
                                raise ValueError('unavailable_check')
                            evidence = self._evidence_type.model_validate(body)
                            now = datetime.now(timezone.utc)
                            if (evidence.permission != permission
                                or evidence.authorization_scope.org_id != self.org_id
                                or not self._resource_matches(evidence)
                                or not observed_start-timedelta(seconds=1) <= evidence.checked_at <= now+timedelta(seconds=1)):
                                raise ValueError('invalid_authority')
                            budget.remaining()
                            return evidence, write.time.monotonic()
        except (httpx.HTTPError, TimeoutError, ValueError, TypeError, RecursionError):
            raise HandlerError(503, 'authorization_unavailable') from None

    async def execute(self, conn, raw, authorization):
        """Protected POST semantics, not an HTTP route or outcome-GET handler.

        Current create authority remains necessary for replay. Under assigned
        authority recheck the STORED child's current same-membership assignment;
        recovery after losing create/assignment instead needs the own-read GET.
        No incoming child/version/answers/eligibility authorize stored receipt access.
        """
        budget = write.Budget()
        try:
            if conn.in_transaction() or conn.connection.driver_connection.autocommit:
                raise write.WriteError('invalid_write_context')
            command = parse_create(raw)
            if command.capture_id == command.operation_id:
                raise CommandError('validation_failed')
            if type(authorization) is not str or not re.fullmatch(r'Bearer [\x21-\x7e]+', authorization, flags=re.IGNORECASE):
                raise HandlerError(401, 'authentication_required')
            token = 'Bearer ' + authorization.split(' ', 1)[1]
            evidence, observed_at = await self._authorize(token, budget)
            context = write.VerifiedContext(self.org_id, evidence.account_id, evidence.actor_id,
                                             'own_write', observed_at)
            return await _complete_worker(conn, budget, context, command, evidence)
        except (write.WriteError, CommandError) as error:
            code = str(error)
            raise HandlerError(WRITE_STATUS.get(code, 500), code if code in WRITE_STATUS else 'internal_error') from None
        except SQLAlchemyError:
            raise HandlerError(500, 'internal_error') from None
