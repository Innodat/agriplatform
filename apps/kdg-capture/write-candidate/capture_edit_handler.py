"""Inert current-own-edit orchestration; no startup, engine or network construction."""
import asyncio
import re
from uuid import UUID
from typing import Literal
from sqlalchemy.exc import SQLAlchemyError
from context import Context, PERMISSION, canonical_uuid
from capture_commands import CommandError, parse_edit
import capture_create_handler as protected
import capture_edit as edit
import operation_recovery as recovery

write=edit.write
HandlerError=protected.HandlerError
TARGET=recovery.TARGET
WRITE_STATUS=dict(protected.WRITE_STATUS,capture_unavailable=404)

class RevisionConflictError(HandlerError):
    def __init__(self,current_revision):
        super().__init__(409,'kdg_capture.capture_revision_conflict')
        self.current_revision=current_revision

class EditEvidence(Context):
    permission: Literal['kdg_capture.capture.edit.own']

class _EditAuthority(protected.CreateHandler):
    _permissions=(edit.OWN,)
    _evidence_type=EditEvidence

class EditProposal:
    def __init__(self,capture_id,command):
        self.capture_id,self.command=capture_id,command

def _transaction(conn,budget,context,proposal,evidence):
    with write.transaction(conn,budget,context):
        key=write.OutcomeKey('kdg_capture',context.org_id,context.account_id,
            'capture.edit',proposal.command.operation_id)
        write.outcome_lock(conn,budget,key,context)
        found=edit.outcomes.lookup_private(conn,budget,key,context)
        if found is None:
            result=edit.edit_in_transaction(conn,budget,context,proposal.capture_id,
                proposal.command,permission=evidence.permission)
        else:
            # No received capture, answers or revision selects/authorizes replay.
            row=edit.create._one(conn,budget,TARGET,dict(org=context.org_id,
                account=context.account_id,capture=found.result.capture_id))
            try:
                normalized={key:str(value) if isinstance(value,UUID) else value
                    for key,value in dict(row).items()}
                if (normalized['id'],normalized['org_id'],normalized['owner_account_id'])!=(
                    found.result.capture_id,context.org_id,context.account_id):
                    raise ValueError('foreign_target')
            except (ValueError,TypeError,KeyError):
                raise write.WriteError('operation_verification_unavailable') from None
            result=found.receipt()
    budget.remaining()
    return result

class EditHandler(protected.CreateHandler):
    _permissions=(PERMISSION,)
    _evidence_type=Context
    async def _authorize_pair(self,token,budget):
        try:
            async with asyncio.timeout(min(protected.ACCESS_SECONDS,budget.remaining())):
                read,observed=await super()._authorize(token,budget)
                checker=_EditAuthority(org_id=self.org_id,access_url=self.access_url,
                    service_key=self._service_key,transport=self._transport)
                evidence,_=await checker._authorize(token,budget)
                if (read.account_id,read.actor_id,read.membership_id)!=(evidence.account_id,evidence.actor_id,evidence.membership_id):
                    raise HandlerError(503,'authorization_unavailable')
                return read,evidence,observed
        except TimeoutError:
            raise HandlerError(503,'authorization_unavailable') from None

    async def _authorize(self,token,budget):
        _,evidence,observed=await self._authorize_pair(token,budget)
        return evidence,observed

    async def execute(self,conn,capture_id,raw,authorization):
        budget=write.Budget()
        try:
            try:canonical_uuid(capture_id)
            except (ValueError,TypeError):raise CommandError('validation_failed') from None
            command=parse_edit(raw)
            if type(authorization) is not str or not re.fullmatch(r'Bearer [A-Za-z0-9\-._~+/]+=*',authorization,flags=re.IGNORECASE):
                raise HandlerError(401,'authentication_required')
            if conn.in_transaction() or conn.connection.driver_connection.autocommit:
                raise write.WriteError('invalid_write_context')
            evidence,observed=await self._authorize('Bearer '+authorization.split(' ',1)[1],budget)
            context=write.VerifiedContext(self.org_id,evidence.account_id,evidence.actor_id,'own_write',observed)
            return await protected._complete_worker(conn,budget,context,EditProposal(capture_id,command),evidence,_transaction)
        except edit.RevisionConflict as error:
            raise RevisionConflictError(error.current_revision) from None
        except (write.WriteError,CommandError) as error:
            code=str(error)
            raise HandlerError(WRITE_STATUS.get(code,500),code if code in WRITE_STATUS else 'internal_error') from None
        except SQLAlchemyError:
            raise HandlerError(500,'internal_error') from None
