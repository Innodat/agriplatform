"""Protected current own detail; no engine, active route or startup effects."""
from datetime import date, datetime, timezone
import json
import re
from typing import Annotated
from uuid import UUID

from pydantic import Field, BeforeValidator
from sqlalchemy.exc import SQLAlchemyError
from capture_commands import Closed, Identifier, Revision, ObservationDate, DeviceTime, AnswerMap, EditCommand, validate_answers
from questionnaire import QuestionnaireDefinition, Label, parse_definition
import operation_recovery as recovery

write = recovery.write
protected = recovery.protected
MAX_RESPONSE_BYTES = 512 * 1024
STATUS={**protected.WRITE_STATUS,'capture_unavailable':404,'capture_read_unavailable':503}

class Lookup(Closed):
    capture_id: Identifier

class CaptureDetail(Closed):
    capture_id: Identifier
    org_id: Identifier
    owner_account_id: Identifier
    owner_actor_id: Identifier
    child_id: Identifier
    child_label: Annotated[Label, Field(max_length=200)]
    questionnaire_id: Identifier
    questionnaire_version_id: Identifier
    questionnaire_version: Revision
    definition: QuestionnaireDefinition
    revision: Revision
    observation_date: ObservationDate
    answers: AnswerMap
    captured_at: DeviceTime
    created_by: Identifier
    created_at: DeviceTime
    updated_by: Identifier
    updated_at: DeviceTime

PROJECTION='''SELECT c.id AS capture_id,c.org_id,c.owner_account_id,c.owner_actor_id,
c.child_id,ch.display_name AS child_label,c.questionnaire_id,c.questionnaire_version_id,
v.display_version AS questionnaire_version,v.definition,c.revision,c.observation_date,
c.answers,c.captured_at,c.created_by,c.created_at,c.updated_by,c.updated_at
FROM kdg_capture.capture c
JOIN kdg_capture.child ch ON ch.org_id=c.org_id AND ch.id=c.child_id
JOIN kdg_capture.questionnaire_version v ON v.org_id=c.org_id
AND v.questionnaire_id=c.questionnaire_id AND v.id=c.questionnaire_version_id'''

DETAIL=PROJECTION+'''
WHERE c.org_id=CAST(:org AS uuid) AND c.owner_account_id=CAST(:account AS uuid)
AND c.id=CAST(:capture AS uuid)'''


def _snapshot(row,context,lookup):
    if row is None:
        raise write.WriteError('capture_unavailable')
    try:
        value=dict(row)
        for key,item in value.items():
            if isinstance(item,UUID):value[key]=str(item)
        if (value['capture_id'],value['org_id'],value['owner_account_id'])!=(lookup.capture_id,context.org_id,context.account_id):
            raise write.WriteError('capture_unavailable')
        for key in ('revision','questionnaire_version'):
            if type(value[key]) is not int:raise ValueError('invalid_revision')
            value[key]=str(value[key])
        if type(value['observation_date']) is not date:raise ValueError('invalid_date')
        value['observation_date']=value['observation_date'].isoformat()
        for key in ('created_at','updated_at'):
            instant=value[key]
            if not isinstance(instant,datetime) or instant.utcoffset() is None:
                raise ValueError('invalid_timestamp')
            value[key]=instant.astimezone(timezone.utc).isoformat().replace('+00:00','Z')
        value['definition']=parse_definition(json.dumps(value['definition'],allow_nan=False,ensure_ascii=False,separators=(',',':')))
        detail=CaptureDetail.model_validate(value)
        if detail.created_by!=detail.owner_actor_id:raise ValueError('invalid_creation_provenance')
        # Consume the established answer validator with a local structural command;
        # no operation lookup or command is executed and no write authority is inferred.
        command=EditCommand(operation_id=detail.capture_id,command_version=1,
            expected_revision=detail.revision,observation_date=detail.observation_date,
            answers=detail.answers)
        validate_answers(command,detail.definition)
        if len(detail.model_dump_json().encode('utf-8'))>MAX_RESPONSE_BYTES:
            raise ValueError('response_too_large')
        return detail
    except write.WriteError:raise
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError):
        raise write.WriteError('capture_read_unavailable') from None


def _transaction(conn,budget,context,lookup,evidence):
    with write.transaction(conn,budget,context):
        row=write.execute(conn,budget,DETAIL,dict(org=context.org_id,account=context.account_id,
            capture=lookup.capture_id)).mappings().one_or_none()
        budget.remaining()
        result=_snapshot(row,context,lookup)
        budget.remaining()
    budget.remaining()
    return result

class ReadHandler(recovery.RecoveryHandler):
    async def execute(self,conn,capture_id,authorization):
        budget=write.Budget()
        try:
            if conn.in_transaction() or conn.connection.driver_connection.autocommit:
                raise write.WriteError('invalid_write_context')
            try:lookup=Lookup(capture_id=capture_id)
            except ValueError:raise protected.HandlerError(422,'validation_failed') from None
            if type(authorization) is not str or not re.fullmatch(r'Bearer [A-Za-z0-9\-._~+/]+=*',authorization,flags=re.IGNORECASE):
                raise protected.HandlerError(401,'authentication_required')
            evidence,observed_at=await self._authorize('Bearer '+authorization.split(' ',1)[1],budget)
            context=write.VerifiedContext(self.org_id,evidence.account_id,evidence.actor_id,'own_read',observed_at)
            return await protected._complete_worker(conn,budget,context,lookup,evidence,_transaction)
        except write.WriteError as error:
            code=str(error)
            if code in ('internal_error','operation_verification_unavailable'):code='capture_read_unavailable'
            raise protected.HandlerError(STATUS.get(code,500),code if code in STATUS else 'internal_error') from None
        except SQLAlchemyError:
            raise protected.HandlerError(503,'capture_read_unavailable') from None
