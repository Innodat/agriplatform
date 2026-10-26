"""Inert original administrator edit context; no observations or write effects."""
import asyncio
import re
from typing import Literal
from sqlalchemy.exc import SQLAlchemyError
from context import Context, OrganizationScope
import admin_read as admin

read=admin.read
write=admin.write
protected=admin.protected
STATUS=admin.STATUS
Lookup=admin.Lookup
DETAIL=admin.DETAIL
MAX_RESPONSE_BYTES=544*1024
EDIT_PERMISSION='kdg_capture.capture.edit.all'

class AllEditEvidence(Context):
    permission: Literal['kdg_capture.capture.edit.all']
    resource_scope: OrganizationScope

class AdminEditContext(read.Closed):
    capture: read.CaptureDetail
    editable_fields: tuple[Literal['observation_date'],Literal['answers']]

class _EditAuthority(admin.AdminReadHandler):
    _permissions=(EDIT_PERMISSION,)
    _evidence_type=AllEditEvidence

class AdminEditContextHandler(admin.AdminReadHandler):
    async def _authorize_pair(self,token,budget):
        try:
            async with asyncio.timeout(min(protected.ACCESS_SECONDS,budget.remaining())):
                first,observed=await super()._authorize(token,budget)
                checker=_EditAuthority(org_id=self.org_id,access_url=self.access_url,
                    service_key=self._service_key,transport=self._transport)
                second,_=await checker._authorize(token,budget)
                if (first.account_id,first.actor_id,first.membership_id)!=(second.account_id,second.actor_id,second.membership_id):
                    raise protected.HandlerError(503,'authorization_unavailable')
                return first,second,observed
        except TimeoutError:
            raise protected.HandlerError(503,'authorization_unavailable') from None

    async def execute(self,conn,capture_id,authorization):
        budget=write.Budget()
        try:
            try:lookup=Lookup(capture_id=capture_id)
            except ValueError:raise protected.HandlerError(422,'validation_failed') from None
            if type(authorization) is not str or not re.fullmatch(r'Bearer [A-Za-z0-9\-._~+/]+=*',authorization,flags=re.IGNORECASE):
                raise protected.HandlerError(401,'authentication_required')
            if conn.in_transaction() or conn.connection.driver_connection.autocommit:
                raise write.WriteError('invalid_write_context')
            first,second,observed=await self._authorize_pair('Bearer '+authorization.split(' ',1)[1],budget)
            context=write.VerifiedContext(self.org_id,first.account_id,first.actor_id,'all_read',observed)
            return await protected._complete_worker(conn,budget,context,lookup,(first,second),_transaction)
        except write.WriteError as error:
            code=str(error)
            if code in ('internal_error','operation_verification_unavailable'):code='capture_read_unavailable'
            raise protected.HandlerError(STATUS.get(code,500),code if code in STATUS else 'internal_error') from None
        except SQLAlchemyError:raise protected.HandlerError(503,'capture_read_unavailable') from None

def _transaction(conn,budget,context,lookup,evidence):
    capture=admin._transaction(conn,budget,context,lookup,evidence[0])
    result=AdminEditContext(capture=capture,editable_fields=('observation_date','answers'))
    if len(result.model_dump_json().encode('utf-8'))>MAX_RESPONSE_BYTES:
        raise write.WriteError('capture_read_unavailable')
    budget.remaining()
    return result
