"""Inert fresh-only own-edit body. No engine, route, HTTP or authority discovery.

Caller supplies current backend-verified admission/membership, durable actor and
corresponding own-read/own-edit authority before entering write.transaction with
this SAME context and original Budget. Permission/context shape checks grant no
rights. Let failures escape the transaction; acknowledge only after durable commit.
Existing outcomes stop here: later orchestration must authorize their stored target.
"""
from datetime import date
import json
from uuid import uuid4

import capture_create as create
from capture_commands import EditCommand, CommandError, validate_answers
from questionnaire import DefinitionError, parse_definition

outcomes=create.outcomes
write=outcomes.write
OWN='kdg_capture.capture.edit.own'
MAX_REVISION=9223372036854775807

CAPTURE='''SELECT questionnaire_version_id,revision,
(observation_date=CAST(:date AS date) AND answers=CAST(:answers AS jsonb)) AS unchanged
FROM kdg_capture.capture WHERE org_id=CAST(:org AS uuid) AND id=CAST(:capture AS uuid)
AND owner_account_id=CAST(:account AS uuid) FOR UPDATE'''
UPDATE='''UPDATE kdg_capture.capture
SET observation_date=CAST(:date AS date),answers=CAST(:answers AS jsonb),revision=:revision
WHERE org_id=CAST(:org AS uuid) AND id=CAST(:capture AS uuid)
AND owner_account_id=CAST(:account AS uuid) AND revision=:previous'''
HISTORY_INSERT='''INSERT INTO kdg_capture.capture_revision
(org_id,capture_id,revision,owner_account_id,owner_actor_id,child_id,questionnaire_id,questionnaire_version_id,
observation_date,answers,captured_at,executor_account_id,executor_actor_id,initiator_actor_id,outcome_id,command_type,operation_id)
SELECT c.org_id,c.id,c.revision,c.owner_account_id,c.owner_actor_id,c.child_id,c.questionnaire_id,c.questionnaire_version_id,
c.observation_date,c.answers,c.captured_at,CAST(:account AS uuid),CAST(:actor AS uuid),CAST(:actor AS uuid),
CAST(:outcome AS uuid),'capture.edit',CAST(:operation AS uuid)
FROM kdg_capture.capture c WHERE c.org_id=CAST(:org AS uuid) AND c.id=CAST(:capture AS uuid)
AND c.owner_account_id=CAST(:account AS uuid)'''


class RevisionConflict(write.WriteError):
    """Safe typed metadata for a future409 adapter; never a record snapshot."""
    def __init__(self,current_revision):
        self.current_revision=str(current_revision)
        super().__init__('kdg_capture.capture_revision_conflict')


def edit_in_transaction(conn,budget,context,capture_id,command,*,permission):
    """Fresh-only provisional write. Caller owns current authority and commit.

    Ordinary own edits require neither current create assignment/eligibility nor
    child-active state. Stored ownership and original questionnaire remain fixed.
    PostgreSQL computes JSONB/date equality; Python bool/int equality is unsuitable.
    """
    if (type(context) is not write.VerifiedContext or context.mode!='own_write'
        or permission!=OWN):
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
