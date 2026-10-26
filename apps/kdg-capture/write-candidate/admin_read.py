"""Current organization reads only; no offline observation or all-edit authority."""
from datetime import date, datetime
import re
from typing import Annotated, Literal
from pydantic import Field
from sqlalchemy.exc import SQLAlchemyError
from context import Context, OrganizationScope
import capture_read as read
import capture_history as history

write=read.write
protected=read.protected
STATUS=read.STATUS
PERMISSION='kdg_capture.capture.read.all'
MAX_RESPONSE_BYTES=history.MAX_RESPONSE_BYTES
Query=history.Query
Lookup=read.Lookup
CaptureDetail=read.CaptureDetail

class AllReadEvidence(Context):
    permission: Literal['kdg_capture.capture.read.all']
    resource_scope: OrganizationScope

class Continuation(history.Continuation):
    permission: Literal['kdg_capture.capture.read.all']

class AdminHistoryPage(read.Closed):
    org_id: read.Identifier
    account_id: read.Identifier
    from_date: read.ObservationDate
    to_date: read.ObservationDate
    limit: Annotated[int,Field(strict=True,ge=1,le=100)]
    items: Annotated[list[CaptureDetail],Field(max_length=100)]
    next_cursor: Annotated[str,Field(strict=True,min_length=1,max_length=history.MAX_CURSOR_BYTES)]|None


def decode_cursor(raw):return history._decode_cursor(raw,Continuation)
def parse_query(items):return history._parse_query(items,decode_cursor)
def position(query,context):return history._position(query,context,decode_cursor,PERMISSION)
def continuation(query,context,detail):return history._continuation(query,context,detail,PERMISSION)
def _snapshot(row,context,lookup):return read._validated_record(read._bound_record(row,context,lookup))

DETAIL=read.PROJECTION+'''
WHERE c.org_id=CAST(:org AS uuid) AND c.id=CAST(:capture AS uuid)'''
HISTORY=read.PROJECTION+'''
WHERE c.org_id=CAST(:org AS uuid)
AND c.observation_date>=CAST(:from_date AS date)
AND c.observation_date<=CAST(:to_date AS date)
AND (CAST(:last_id AS uuid) IS NULL OR (c.created_at,c.id)<(CAST(:last_created_at AS timestamptz),CAST(:last_id AS uuid)))
ORDER BY c.created_at DESC,c.id DESC LIMIT :row_limit'''


def _page(rows,budget,context,query,evidence):
    details=history._page_details(rows,budget,context,query,position(query,context),_snapshot)
    page=AdminHistoryPage(org_id=context.org_id,account_id=context.account_id,from_date=query.from_date,to_date=query.to_date,limit=query.limit,items=[],next_cursor=None)
    return history._bounded_page(page,details,budget,context,query,continuation)


def _transaction(conn,budget,context,lookup,evidence):
    if isinstance(lookup,Lookup):
        with write.transaction(conn,budget,context):
            row=write.execute(conn,budget,DETAIL,dict(org=context.org_id,capture=lookup.capture_id)).mappings().one_or_none()
            budget.remaining()
        budget.remaining()
        result=_snapshot(row,context,lookup)
        budget.remaining()
    else:
        last=position(lookup,context)
        with write.transaction(conn,budget,context):
            rows=write.execute(conn,budget,HISTORY,dict(org=context.org_id,
                from_date=date.fromisoformat(lookup.from_date),to_date=date.fromisoformat(lookup.to_date),
                last_id=last.last_id if last else None,last_created_at=datetime.fromisoformat(last.last_created_at) if last else None,
                row_limit=lookup.limit+1)).mappings().all()
            budget.remaining()
        budget.remaining()
        result=_page(rows,budget,context,lookup,evidence)
    budget.remaining()
    return result


class AdminReadHandler(read.ReadHandler):
    _permissions=(PERMISSION,)
    _evidence_type=AllReadEvidence

    def _resource_matches(self,evidence):
        return evidence.resource_scope.org_id==self.org_id

    async def execute(self,conn,lookup,authorization):
        """A capture ID reads detail; a closed query reads one current page."""
        budget=write.Budget()
        try:
            if conn.in_transaction() or conn.connection.driver_connection.autocommit:raise write.WriteError('invalid_write_context')
            try:
                lookup=Lookup(capture_id=lookup) if isinstance(lookup,str) else Query.model_validate(lookup)
                if isinstance(lookup,Query) and lookup.cursor is not None:decode_cursor(lookup.cursor)
            except ValueError:raise protected.HandlerError(422,'validation_failed') from None
            if type(authorization) is not str or not re.fullmatch(r'Bearer [A-Za-z0-9\-._~+/]+=*',authorization,flags=re.IGNORECASE):raise protected.HandlerError(401,'authentication_required')
            evidence,observed_at=await self._authorize('Bearer '+authorization.split(' ',1)[1],budget)
            context=write.VerifiedContext(self.org_id,evidence.account_id,evidence.actor_id,'all_read',observed_at)
            if isinstance(lookup,Query):position(lookup,context)
            return await protected._complete_worker(conn,budget,context,lookup,evidence,_transaction)
        except write.WriteError as error:
            code=str(error)
            if code in ('internal_error','operation_verification_unavailable'):code='capture_read_unavailable'
            raise protected.HandlerError(STATUS.get(code,500),code if code in STATUS else 'internal_error') from None
        except SQLAlchemyError:raise protected.HandlerError(503,'capture_read_unavailable') from None
