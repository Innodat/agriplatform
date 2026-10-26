"""Bounded online immutable audit metadata; navigation never supplies authority."""
import base64
from datetime import datetime, timezone
import json
import re
from typing import Annotated, Literal
from uuid import UUID
from pydantic import Field
from sqlalchemy.exc import SQLAlchemyError
import admin_read as admin

read=admin.read
write=admin.write
protected=admin.protected
STATUS=admin.STATUS
PERMISSION=admin.PERMISSION
MAX_CURSOR_BYTES=2048
MAX_RESPONSE_BYTES=64*1024

class Query(read.Closed):
    capture_id: read.Identifier
    limit: Annotated[int,Field(strict=True,ge=1,le=100)]=30
    cursor: Annotated[str,Field(strict=True,min_length=1,max_length=MAX_CURSOR_BYTES)]|None=None

class Continuation(read.Closed):
    v: Literal[1]
    org_id: read.Identifier
    account_id: read.Identifier
    capture_id: read.Identifier
    permission: Literal['kdg_capture.capture.read.all']
    limit: Annotated[int,Field(strict=True,ge=1,le=100)]
    last_revision: read.Revision

class AuditEvent(read.Closed):
    revision: read.Revision
    command_type: Literal['capture.create','capture.edit']
    executor_actor_id: read.Identifier
    initiator_actor_id: read.Identifier|None
    recorded_at: read.DeviceTime

class AuditPage(read.Closed):
    org_id: read.Identifier
    account_id: read.Identifier
    capture_id: read.Identifier
    owner_account_id: read.Identifier
    owner_actor_id: read.Identifier
    created_by: read.Identifier
    created_at: read.DeviceTime
    updated_by: read.Identifier
    updated_at: read.DeviceTime
    current_revision: read.Revision
    limit: Annotated[int,Field(strict=True,ge=1,le=100)]
    events: Annotated[list[AuditEvent],Field(max_length=100)]
    next_cursor: Annotated[str,Field(strict=True,min_length=1,max_length=MAX_CURSOR_BYTES)]|None


def decode_cursor(raw):
    try:
        if type(raw) is not str or not 1<=len(raw)<=MAX_CURSOR_BYTES or not re.fullmatch(r'[A-Za-z0-9_-]+',raw):raise ValueError('cursor')
        value=json.loads(base64.b64decode(raw+'='*((-len(raw))%4),altchars=b'-_',validate=True).decode('ascii'),object_pairs_hook=admin.history._pairs)
        if admin.history._encode(value)!=raw or type(value.get('v')) is not int:raise ValueError('cursor')
        return Continuation.model_validate(value)
    except (ValueError,TypeError,KeyError,AttributeError,UnicodeError,RecursionError,OverflowError):
        raise protected.HandlerError(422,'validation_failed') from None


def parse_query(capture_id,items):
    try:
        values={'capture_id':capture_id}
        for key,value in items:
            if key not in ('limit','cursor') or key in values:raise ValueError('query')
            values[key]=value
        if 'limit' in values:
            if not re.fullmatch(r'[1-9][0-9]{0,2}',values['limit']):raise ValueError('limit')
            values['limit']=int(values['limit'])
        query=Query.model_validate(values)
        if query.cursor is not None:decode_cursor(query.cursor)
        return query
    except (ValueError,TypeError,RecursionError):raise protected.HandlerError(422,'validation_failed') from None


def position(query,context):
    if query.cursor is None:return None
    cursor=decode_cursor(query.cursor)
    if (cursor.org_id,cursor.account_id,cursor.capture_id,cursor.permission,cursor.limit)!=(context.org_id,context.account_id,query.capture_id,PERMISSION,query.limit):
        raise protected.HandlerError(422,'validation_failed')
    return cursor


def continuation(query,context,event):
    return admin.history._encode(dict(v=1,org_id=context.org_id,account_id=context.account_id,
        capture_id=query.capture_id,permission=PERMISSION,limit=query.limit,last_revision=event.revision))

EVENTS='''SELECT c.id AS capture_id,c.org_id,c.owner_account_id,c.owner_actor_id,
c.created_by,c.created_at,c.updated_by,c.updated_at,c.revision AS current_revision,
r.revision AS event_revision,r.command_type,r.executor_actor_id,r.initiator_actor_id,
r.created_at AS recorded_at
FROM kdg_capture.capture c
LEFT JOIN LATERAL (
 SELECT revision,command_type,executor_actor_id,initiator_actor_id,created_at
 FROM kdg_capture.capture_revision
 WHERE org_id=CAST(:org AS uuid) AND capture_id=CAST(:capture AS uuid)
 AND (CAST(:last_revision AS bigint) IS NULL OR revision<CAST(:last_revision AS bigint))
 ORDER BY revision DESC LIMIT :row_limit
) r ON TRUE
WHERE c.org_id=CAST(:org AS uuid) AND c.id=CAST(:capture AS uuid)
ORDER BY r.revision DESC'''

HEADER=('capture_id','org_id','owner_account_id','owner_actor_id','created_by','created_at','updated_by','updated_at','current_revision')
EVENT_FIELDS=('event_revision','command_type','executor_actor_id','initiator_actor_id','recorded_at')

def _revision(value):
    if type(value) is not int:raise ValueError('revision')
    return str(value)


def _instant(value):
    if not isinstance(value,datetime) or value.utcoffset() is None:raise ValueError('timestamp')
    return value.astimezone(timezone.utc).isoformat().replace('+00:00','Z')


def _page(rows,budget,context,query,evidence):
    if not rows:raise write.WriteError('capture_unavailable')
    try:
        if len(rows)>query.limit+1:raise ValueError('row_limit')
        rows=[{key:str(value) if isinstance(value,UUID) else value for key,value in dict(row).items()} for row in rows]
        header={key:rows[0][key] for key in HEADER}
        if (header['org_id'],header['capture_id'])!=(context.org_id,query.capture_id):raise write.WriteError('capture_unavailable')
        if header['created_by']!=header['owner_actor_id']:raise ValueError('creation_actor')
        current=header['current_revision'];header['current_revision']=_revision(current)
        for key in ('created_at','updated_at'):header[key]=_instant(header[key])
        page=AuditPage(**header,account_id=context.account_id,limit=query.limit,events=[],next_cursor=None)
        last=position(query,context);previous=int(last.last_revision) if last else current+1
        events=[]
        for row in rows:
            budget.remaining()
            if any(row[key]!=rows[0][key] for key in HEADER):raise ValueError('incoherent_header')
            revision=row['event_revision']
            if revision is None:
                if len(rows)!=1 or any(row[key] is not None for key in EVENT_FIELDS) or last is None:raise ValueError('missing_evidence')
                continue
            revision_string=_revision(revision)
            if not 0<revision<=current or revision>=previous:raise ValueError('event_order')
            event=AuditEvent(revision=revision_string,command_type=row['command_type'],executor_actor_id=row['executor_actor_id'],initiator_actor_id=row['initiator_actor_id'],recorded_at=_instant(row['recorded_at']))
            if event.command_type!=('capture.create' if revision==1 else 'capture.edit'):raise ValueError('command_revision')
            if revision==1 and event.executor_actor_id!=page.owner_actor_id:raise ValueError('creation_actor')
            if revision==current and event.executor_actor_id!=page.updated_by:raise ValueError('latest_actor')
            previous=revision;events.append(event)
        if last is None and (not events or int(events[0].revision)!=current):raise ValueError('missing_current_evidence')
        included=events[:query.limit]
        cursor=continuation(query,context,included[-1]) if len(events)>query.limit else None
        page=page.model_copy(update=dict(events=included,next_cursor=cursor))
        if len(page.model_dump_json().encode('utf-8'))>MAX_RESPONSE_BYTES:raise ValueError('page_size')
        budget.remaining()
        return page
    except write.WriteError:raise
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError):raise write.WriteError('capture_read_unavailable') from None


def _transaction(conn,budget,context,query,evidence):
    last=position(query,context)
    with write.transaction(conn,budget,context):
        rows=write.execute(conn,budget,EVENTS,dict(org=context.org_id,capture=query.capture_id,
            last_revision=int(last.last_revision) if last else None,row_limit=query.limit+1)).mappings().all()
        budget.remaining()
    budget.remaining()
    return _page(rows,budget,context,query,evidence)

class AuditReadHandler(admin.AdminReadHandler):
    async def execute(self,conn,query,authorization):
        budget=write.Budget()
        try:
            if conn.in_transaction() or conn.connection.driver_connection.autocommit:raise write.WriteError('invalid_write_context')
            try:query=Query.model_validate(query)
            except ValueError:raise protected.HandlerError(422,'validation_failed') from None
            if query.cursor is not None:decode_cursor(query.cursor)
            if type(authorization) is not str or not re.fullmatch(r'Bearer [A-Za-z0-9\-._~+/]+=*',authorization,flags=re.IGNORECASE):raise protected.HandlerError(401,'authentication_required')
            evidence,observed_at=await self._authorize('Bearer '+authorization.split(' ',1)[1],budget)
            context=write.VerifiedContext(self.org_id,evidence.account_id,evidence.actor_id,'all_read',observed_at)
            position(query,context)
            return await protected._complete_worker(conn,budget,context,query,evidence,_transaction)
        except write.WriteError as error:
            code=str(error)
            if code in ('internal_error','operation_verification_unavailable'):code='capture_read_unavailable'
            raise protected.HandlerError(STATUS.get(code,500),code if code in STATUS else 'internal_error') from None
        except SQLAlchemyError:raise protected.HandlerError(503,'capture_read_unavailable') from None
