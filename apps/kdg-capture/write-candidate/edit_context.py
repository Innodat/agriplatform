"""Closed protected original-own-edit context; no write or local state effects."""
from datetime import timedelta
from typing import Literal
import re
from sqlalchemy.exc import SQLAlchemyError
import capture_read as read
from capture_history import OwnReadObservation
from capture_edit_handler import EditHandler, EditEvidence

write=read.write
protected=read.protected
Lookup=read.Lookup
DETAIL=read.DETAIL
STATUS=read.STATUS
# A512KiB detail plus two bounded Access observations and fixed envelope overhead.
MAX_RESPONSE_BYTES=544*1024

class OwnEditObservation(EditEvidence):
    expires_at: read.datetime

class EditContext(read.Closed):
    capture: read.CaptureDetail
    editable_fields: tuple[Literal['observation_date'],Literal['answers']]
    read_observation: OwnReadObservation
    edit_observation: OwnEditObservation

class EditContextHandler(EditHandler):
    async def execute(self,conn,capture_id,authorization):
        budget=write.Budget()
        try:
            try:lookup=Lookup(capture_id=capture_id)
            except ValueError:raise protected.HandlerError(422,'validation_failed') from None
            if type(authorization) is not str or not re.fullmatch(r'Bearer [A-Za-z0-9\-._~+/]+=*',authorization,flags=re.IGNORECASE):
                raise protected.HandlerError(401,'authentication_required')
            if conn.in_transaction() or conn.connection.driver_connection.autocommit:
                raise write.WriteError('invalid_write_context')
            read_evidence,edit_evidence,observed_at=await self._authorize_pair('Bearer '+authorization.split(' ',1)[1],budget)
            context=write.VerifiedContext(self.org_id,read_evidence.account_id,read_evidence.actor_id,'own_read',observed_at)
            return await protected._complete_worker(conn,budget,context,lookup,(read_evidence,edit_evidence),_transaction)
        except write.WriteError as error:
            code=str(error)
            if code in ('internal_error','operation_verification_unavailable'):code='capture_read_unavailable'
            raise protected.HandlerError(STATUS.get(code,500),code if code in STATUS else 'internal_error') from None
        except SQLAlchemyError:raise protected.HandlerError(503,'capture_read_unavailable') from None

def _transaction(conn,budget,context,lookup,evidence):
    read_evidence,edit_evidence=evidence
    capture=read._transaction(conn,budget,context,lookup,read_evidence)
    # The durable actor is part of original ownership, not a received selector.
    if capture.owner_actor_id!=read_evidence.actor_id:
        raise write.WriteError('capture_read_unavailable')
    result=EditContext(capture=capture,editable_fields=('observation_date','answers'),
        read_observation=OwnReadObservation.model_validate({**read_evidence.model_dump(mode='json'),'expires_at':read_evidence.checked_at+timedelta(days=7)}),
        edit_observation=OwnEditObservation.model_validate({**edit_evidence.model_dump(mode='json'),'expires_at':edit_evidence.checked_at+timedelta(days=7)}))
    if len(result.model_dump_json().encode('utf-8'))>MAX_RESPONSE_BYTES:
        raise write.WriteError('capture_read_unavailable')
    budget.remaining()
    return result
