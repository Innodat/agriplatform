"""Protected own-history pages. Cursors navigate; they never authorize a read."""
import base64
from datetime import date, datetime, timedelta, timezone
import json
import re
from typing import Annotated, Literal

from pydantic import Field, model_validator
import capture_read as read

write=read.write
protected=read.protected
STATUS=read.STATUS
MAX_RESPONSE_BYTES=2*1024*1024
MAX_CURSOR_BYTES=2048
PERMISSION='kdg_capture.capture.read.own'

class Query(read.Closed):
    from_date: read.ObservationDate
    to_date: read.ObservationDate
    limit: Annotated[int,Field(strict=True,ge=1,le=100)]=30
    cursor: Annotated[str,Field(strict=True,min_length=1,max_length=MAX_CURSOR_BYTES)]|None=None
    @model_validator(mode='after')
    def bounds(self):
        if self.from_date>self.to_date:raise ValueError('invalid_bounds')
        return self

class Continuation(read.Closed):
    v: Literal[1]
    org_id: read.Identifier
    account_id: read.Identifier
    permission: Literal['kdg_capture.capture.read.own']
    from_date: read.ObservationDate
    to_date: read.ObservationDate
    limit: Annotated[int,Field(strict=True,ge=1,le=100)]
    last_created_at: read.DeviceTime
    last_id: read.Identifier

from context import Context

class OwnReadObservation(Context):
    expires_at: datetime

class HistoryPage(read.Closed):
    observation: OwnReadObservation
    org_id: read.Identifier
    account_id: read.Identifier
    from_date: read.ObservationDate
    to_date: read.ObservationDate
    limit: Annotated[int,Field(strict=True,ge=1,le=100)]
    items: Annotated[list[read.CaptureDetail],Field(max_length=100)]
    next_cursor: Annotated[str,Field(strict=True,min_length=1,max_length=MAX_CURSOR_BYTES)]|None


def _canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')

def _encode(value):
    return base64.urlsafe_b64encode(_canonical(value)).decode('ascii').rstrip('=')

def _pairs(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate_key')
        result[key]=value
    return result

def _decode_cursor(raw,model):
    """Strict closed canonical syntax, before any authority call or checkout."""
    try:
        if type(raw) is not str or not 1<=len(raw)<=MAX_CURSOR_BYTES or not re.fullmatch(r'[A-Za-z0-9_-]+',raw):raise ValueError('cursor')
        encoded=base64.b64decode(raw+'='*((-len(raw))%4),altchars=b'-_',validate=True)
        value=json.loads(encoded.decode('ascii'),object_pairs_hook=_pairs)
        # Reject duplicate keys, alternate JSON spellings/padding and bool version.
        if _encode(value)!=raw or type(value.get('v')) is not int:raise ValueError('cursor')
        cursor=model.model_validate(value)
        instant=datetime.fromisoformat(cursor.last_created_at)
        if instant.astimezone(timezone.utc).isoformat().replace('+00:00','Z')!=cursor.last_created_at:raise ValueError('cursor')
        if cursor.from_date>cursor.to_date:raise ValueError('cursor')
        return cursor
    except (ValueError,TypeError,KeyError,AttributeError,UnicodeError,RecursionError,OverflowError):
        raise protected.HandlerError(422,'validation_failed') from None

def decode_cursor(raw):
    return _decode_cursor(raw,Continuation)


def _parse_query(items,decoder):
    values={}
    try:
        for key,value in items:
            if key not in ('from_date','to_date','limit','cursor') or key in values:raise ValueError('query')
            values[key]=value
        if 'limit' in values:
            if not re.fullmatch(r'[1-9][0-9]{0,2}',values['limit']):raise ValueError('limit')
            values['limit']=int(values['limit'])
        query=Query.model_validate(values)
        if query.cursor is not None:decoder(query.cursor)
        return query
    except (ValueError,TypeError,RecursionError):
        raise protected.HandlerError(422,'validation_failed') from None

def parse_query(items):
    return _parse_query(items,decode_cursor)


def _position(query,context,decoder,permission):
    if query.cursor is None:return None
    cursor=decoder(query.cursor)
    if (cursor.org_id,cursor.account_id,cursor.permission,cursor.from_date,cursor.to_date,cursor.limit)!=(context.org_id,context.account_id,permission,query.from_date,query.to_date,query.limit):
        raise protected.HandlerError(422,'validation_failed')
    return cursor

def position(query,context):
    return _position(query,context,decode_cursor,PERMISSION)


def _continuation(query,context,detail,permission):
    return _encode(dict(v=1,org_id=context.org_id,account_id=context.account_id,permission=permission,
        from_date=query.from_date,to_date=query.to_date,limit=query.limit,
        last_created_at=detail.created_at,last_id=detail.capture_id))

def continuation(query,context,detail):
    return _continuation(query,context,detail,PERMISSION)

# Independently enforce every scope/filter predicate: the position carries no authority.
HISTORY=read.PROJECTION+'''
WHERE c.org_id=CAST(:org AS uuid) AND c.owner_account_id=CAST(:account AS uuid)
AND c.observation_date>=CAST(:from_date AS date)
AND c.observation_date<=CAST(:to_date AS date)
AND (CAST(:last_id AS uuid) IS NULL OR (c.created_at,c.id)<(CAST(:last_created_at AS timestamptz),CAST(:last_id AS uuid)))
ORDER BY c.created_at DESC,c.id DESC LIMIT :row_limit'''

def _page_details(rows,budget,context,query,last,snapshot):
    if len(rows)>query.limit+1:raise write.WriteError('capture_read_unavailable')
    previous=(datetime.fromisoformat(last.last_created_at),last.last_id) if last else None
    details=[]
    for row in rows:
        budget.remaining()
        try:
            detail=snapshot(row,context,read.Lookup(capture_id=str(row['capture_id'])))
            current=(datetime.fromisoformat(detail.created_at),detail.capture_id)
            if not query.from_date<=detail.observation_date<=query.to_date or (previous is not None and current>=previous):raise ValueError('invalid_order')
            previous=current;details.append(detail)
        except (ValueError,TypeError,KeyError,write.WriteError):
            raise write.WriteError('capture_read_unavailable') from None
    return details


def _bounded_page(page,details,budget,context,query,make_cursor):
    included=[]
    # Serialize the empty envelope once. Item bytes and commas accumulate;
    # only the small nullable cursor overhead changes for each candidate.
    envelope_bytes=len(page.model_dump_json().encode('utf-8'))
    item_bytes=0;next_cursor=None
    for index,detail in enumerate(details[:query.limit]):
        candidate_cursor=make_cursor(query,context,detail) if index+1<len(details) else None
        candidate_items=item_bytes+len(detail.model_dump_json().encode('utf-8'))+(1 if included else 0)
        # Canonical continuation contains only ASCII base64url characters.
        cursor_bytes=len(candidate_cursor)+2 if candidate_cursor is not None else 4
        if envelope_bytes+candidate_items+cursor_bytes-4>MAX_RESPONSE_BYTES:
            if not included:raise write.WriteError('capture_read_unavailable')
            break
        item_bytes=candidate_items;next_cursor=candidate_cursor;included.append(detail)
        budget.remaining()
    page=page.model_copy(update=dict(items=included,next_cursor=next_cursor))
    # Retain a final actual UTF8 check, independent of incremental accounting.
    if len(page.model_dump_json().encode('utf-8'))>MAX_RESPONSE_BYTES:
        raise write.WriteError('capture_read_unavailable')
    budget.remaining()
    return page

def _page(rows,budget,context,query,evidence):
    details=_page_details(rows,budget,context,query,position(query,context),read._snapshot)
    observation=OwnReadObservation.model_validate({**evidence.model_dump(mode='json'),'expires_at':evidence.checked_at+timedelta(days=7)})
    page=HistoryPage(observation=observation,org_id=context.org_id,account_id=context.account_id,from_date=query.from_date,to_date=query.to_date,limit=query.limit,items=[],next_cursor=None)
    return _bounded_page(page,details,budget,context,query,continuation)

def _transaction(conn,budget,context,query,evidence):
    last=position(query,context)
    with write.transaction(conn,budget,context):
        rows=write.execute(conn,budget,HISTORY,dict(org=context.org_id,account=context.account_id,
            from_date=date.fromisoformat(query.from_date),to_date=date.fromisoformat(query.to_date),
            last_id=last.last_id if last else None,last_created_at=datetime.fromisoformat(last.last_created_at) if last else None,
            row_limit=query.limit+1)).mappings().all()
        budget.remaining()
    budget.remaining()
    # Database work is complete before CPU-only validation and serialization.
    page=_page(rows,budget,context,query,evidence)
    budget.remaining()
    return page

class HistoryHandler(read.ReadHandler):
    """Reuse verified current own-read Access contract; never create/edit authority."""
    async def execute(self,conn,query,authorization):
        from sqlalchemy.exc import SQLAlchemyError
        budget=write.Budget()
        try:
            if conn.in_transaction() or conn.connection.driver_connection.autocommit:raise write.WriteError('invalid_write_context')
            try:query=Query.model_validate(query)
            except ValueError:raise protected.HandlerError(422,'validation_failed') from None
            if query.cursor is not None:decode_cursor(query.cursor)
            if type(authorization) is not str or not re.fullmatch(r'Bearer [A-Za-z0-9\-._~+/]+=*',authorization,flags=re.IGNORECASE):raise protected.HandlerError(401,'authentication_required')
            evidence,observed_at=await self._authorize('Bearer '+authorization.split(' ',1)[1],budget)
            context=write.VerifiedContext(self.org_id,evidence.account_id,evidence.actor_id,'own_read',observed_at)
            position(query,context)
            return await protected._complete_worker(conn,budget,context,query,evidence,_transaction)
        except write.WriteError as error:
            code=str(error)
            if code in ('internal_error','operation_verification_unavailable'):code='capture_read_unavailable'
            raise protected.HandlerError(STATUS.get(code,500),code if code in STATUS else 'internal_error') from None
        except SQLAlchemyError:raise protected.HandlerError(503,'capture_read_unavailable') from None
