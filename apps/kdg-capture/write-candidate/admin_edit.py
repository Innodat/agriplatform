"""Inert administrator edit and executor-private original-operation recovery."""
from uuid import UUID
from typing import Literal
import re
from sqlalchemy.exc import SQLAlchemyError
import admin_edit_context as authority
import capture_edit_handler as own_handler
import operation_recovery as recovery
from capture_commands import parse_edit
from context import canonical_uuid
from capture_edit import RevisionConflict

from datetime import date
import json
from uuid import uuid4

import capture_create as create
from capture_commands import EditCommand, CommandError, validate_answers
from questionnaire import DefinitionError, parse_definition

outcomes=create.outcomes
write=outcomes.write
ALL='kdg_capture.capture.edit.all'
MAX_REVISION=9223372036854775807

CAPTURE='''SELECT questionnaire_version_id,revision,
(observation_date=CAST(:date AS date) AND answers=CAST(:answers AS jsonb)) AS unchanged
FROM kdg_capture.capture WHERE org_id=CAST(:org AS uuid) AND id=CAST(:capture AS uuid)
FOR UPDATE'''
UPDATE='''UPDATE kdg_capture.capture
SET observation_date=CAST(:date AS date),answers=CAST(:answers AS jsonb),revision=:revision
WHERE org_id=CAST(:org AS uuid) AND id=CAST(:capture AS uuid) AND revision=:previous'''
HISTORY_INSERT='''INSERT INTO kdg_capture.capture_revision
(org_id,capture_id,revision,owner_account_id,owner_actor_id,child_id,questionnaire_id,questionnaire_version_id,
observation_date,answers,captured_at,executor_account_id,executor_actor_id,initiator_actor_id,outcome_id,command_type,operation_id)
SELECT c.org_id,c.id,c.revision,c.owner_account_id,c.owner_actor_id,c.child_id,c.questionnaire_id,c.questionnaire_version_id,
c.observation_date,c.answers,c.captured_at,CAST(:account AS uuid),CAST(:actor AS uuid),CAST(:actor AS uuid),
CAST(:outcome AS uuid),'capture.edit',CAST(:operation AS uuid)
FROM kdg_capture.capture c WHERE c.org_id=CAST(:org AS uuid) AND c.id=CAST(:capture AS uuid)'''


def edit_in_transaction(conn,budget,context,capture_id,command,*,permission):
    """Fresh-only provisional write. Caller owns current authority and commit.

    Administrator edits require neither current create assignment/eligibility nor
    child-active state. Stored ownership and original questionnaire remain fixed.
    PostgreSQL computes JSONB/date equality; Python bool/int equality is unsuitable.
    """
    if (type(context) is not write.VerifiedContext or context.mode!='all_write'
        or permission!=ALL):
        raise write.WriteError('invalid_write_context')
    try:
        capture_id=outcomes._identifier(capture_id)
        command=EditCommand.model_validate(command)
    except (ValueError,TypeError):
        raise write.WriteError('validation_failed') from None
    key=write.OutcomeKey('kdg_capture',context.org_id,context.account_id,'capture.edit',command.operation_id)
    outcomes._scope(conn,key,context,True)
    write.outcome_lock(conn,budget,key,context)
    if outcomes.lookup_private(conn,budget,key,context) is not None:
        raise write.WriteError('operation_verification_unavailable')
    parameters=dict(org=context.org_id,account=context.account_id,actor=context.actor_id,
        capture=capture_id,date=date.fromisoformat(command.observation_date),
        answers=json.dumps({key:value.model_dump() for key,value in command.answers.items()},
            separators=(',',':')))
    capture=create._one(conn,budget,CAPTURE,parameters)
    if capture is None:
        raise write.WriteError('capture_unavailable')
    previous=capture['revision']
    if previous!=int(command.expected_revision):
        raise RevisionConflict(previous)
    parameters['version']=str(capture['questionnaire_version_id'])
    version=create._one(conn,budget,create.VERSION,parameters)
    if version is None:
        raise write.WriteError('questionnaire_version_unavailable')
    try:
        definition=parse_definition(json.dumps(version['definition']))
    except (DefinitionError,ValueError,TypeError):
        raise write.WriteError('questionnaire_version_unavailable') from None
    try:
        validate_answers(command,definition)
    except CommandError:
        raise write.WriteError('validation_failed') from None
    changed=capture['unchanged'] is not True
    if changed and previous==MAX_REVISION:
        raise write.WriteError('internal_error')
    revision=previous+1 if changed else previous
    parameters.update(previous=previous,revision=revision)
    if changed and write.execute(conn,budget,UPDATE,parameters).rowcount!=1:
        raise write.WriteError('internal_error')
    receipt=outcomes.CaptureReceipt(operation_id=command.operation_id,command_type='capture.edit',
        command_version=1,status='committed',result=dict(capture_id=capture_id,revision=str(revision)))
    internal_id=str(uuid4())
    outcomes.append(conn,budget,key,context,outcome_id=internal_id,receipt=receipt)
    if changed:
        parameters.update(outcome=internal_id,operation=command.operation_id)
        if write.execute(conn,budget,HISTORY_INSERT,parameters).rowcount!=1:
            raise write.WriteError('internal_error')
    budget.remaining()
    return receipt


# A stored receipt selects its actual organization target. Ownership remains with
# the original observer, while receipt privacy remains with the current executor.
TARGET="""SELECT id,org_id FROM kdg_capture.capture
WHERE org_id=CAST(:org AS uuid) AND id=CAST(:capture AS uuid)"""

protected=authority.protected
EditProposal=own_handler.EditProposal
RevisionConflictError=own_handler.RevisionConflictError
WRITE_STATUS=own_handler.WRITE_STATUS

class Lookup(recovery.Lookup):
    command_type: Literal['capture.edit']

class Unresolved(Lookup):
    status: Literal['unresolved']='unresolved'

def _stored_target(conn,budget,context,found):
    try:
        row=create._one(conn,budget,TARGET,dict(org=context.org_id,capture=found.result.capture_id))
    except write.WriteError as error:
        if str(error)=='internal_error':
            raise write.WriteError('operation_verification_unavailable') from None
        raise
    try:
        normalized={key:str(value) if isinstance(value,UUID) else value for key,value in dict(row).items()}
        if (normalized['id'],normalized['org_id'])!=(found.result.capture_id,context.org_id):
            raise ValueError('foreign_target')
    except (ValueError,TypeError,KeyError):
        raise write.WriteError('operation_verification_unavailable') from None
    return found.receipt()

def _transaction(conn,budget,context,proposal,evidence):
    with write.transaction(conn,budget,context):
        key=write.OutcomeKey('kdg_capture',context.org_id,context.account_id,'capture.edit',proposal.command.operation_id)
        write.outcome_lock(conn,budget,key,context)
        found=outcomes.lookup_private(conn,budget,key,context)
        result=(_stored_target(conn,budget,context,found) if found is not None else
            edit_in_transaction(conn,budget,context,proposal.capture_id,proposal.command,permission=evidence.permission))
    budget.remaining()
    return result

def _recovery_transaction(conn,budget,context,lookup,evidence):
    with write.transaction(conn,budget,context):
        key=write.OutcomeKey('kdg_capture',context.org_id,context.account_id,'capture.edit',lookup.operation_id)
        found=outcomes.lookup_private(conn,budget,key,context)
        result=Unresolved(**lookup.model_dump()) if found is None else _stored_target(conn,budget,context,found)
    budget.remaining()
    return result

class AdminEditHandler(authority.AdminEditContextHandler):
    async def _authorize(self,token,budget):
        _,evidence,observed=await self._authorize_pair(token,budget)
        return evidence,observed

    # _authorize_pair is inherited from the original context owner; its super()
    # resolves the read.all check before the independent edit.all check.
    async def execute(self,conn,capture_id,raw,authorization):
        budget=write.Budget()
        try:
            try:canonical_uuid(capture_id)
            except (ValueError,TypeError):raise CommandError('validation_failed') from None
            command=parse_edit(raw)
            if type(authorization) is not str or not re.fullmatch(r'Bearer [A-Za-z0-9\-._~+/]+=*',authorization,flags=re.IGNORECASE):
                raise protected.HandlerError(401,'authentication_required')
            if conn.in_transaction() or conn.connection.driver_connection.autocommit:
                raise write.WriteError('invalid_write_context')
            evidence,observed=await self._authorize('Bearer '+authorization.split(' ',1)[1],budget)
            context=write.VerifiedContext(self.org_id,evidence.account_id,evidence.actor_id,'all_write',observed)
            return await protected._complete_worker(conn,budget,context,EditProposal(capture_id,command),evidence,_transaction)
        except RevisionConflict as error:raise RevisionConflictError(error.current_revision) from None
        except (write.WriteError,CommandError) as error:
            code=str(error)
            raise protected.HandlerError(WRITE_STATUS.get(code,500),code if code in WRITE_STATUS else 'internal_error') from None
        except SQLAlchemyError:raise protected.HandlerError(500,'internal_error') from None

class AdminRecoveryHandler(authority.admin.AdminReadHandler):
    async def execute(self,conn,operation_id,command_type,authorization):
        budget=write.Budget()
        try:
            try:lookup=Lookup(operation_id=operation_id,command_type=command_type)
            except ValueError:raise protected.HandlerError(422,'validation_failed') from None
            if type(authorization) is not str or not re.fullmatch(r'Bearer [A-Za-z0-9\-._~+/]+=*',authorization,flags=re.IGNORECASE):
                raise protected.HandlerError(401,'authentication_required')
            if conn.in_transaction() or conn.connection.driver_connection.autocommit:raise write.WriteError('invalid_write_context')
            evidence,observed=await self._authorize('Bearer '+authorization.split(' ',1)[1],budget)
            context=write.VerifiedContext(self.org_id,evidence.account_id,evidence.actor_id,'all_read',observed)
            return await protected._complete_worker(conn,budget,context,lookup,evidence,_recovery_transaction)
        except write.WriteError as error:
            code=str(error)
            if code=='internal_error':code='operation_verification_unavailable'
            raise protected.HandlerError(WRITE_STATUS.get(code,500),code if code in WRITE_STATUS else 'internal_error') from None
        except SQLAlchemyError:raise protected.HandlerError(503,'operation_verification_unavailable') from None
