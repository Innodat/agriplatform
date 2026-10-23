"""Short, bounded private transactions. Owner HTTP checks complete before entry."""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime,timezone
import hashlib
import json
import time
from uuid import uuid4
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from personal_notes_access import NotesError,remaining
from personal_notes_contract import MAX_REVISION,StudyView,NoteView,OperationAck
from personal_notes_cursor import encode,decode

SCHEMA='scribeswell_studies'

def stamp(value): return value.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

def view(row,note=False):
    result={key:str(row[key]) for key in ('id','revision')}
    result.update(owner_account_id=str(row['account_id']),created_at=stamp(row['created_at']),updated_at=stamp(row['updated_at']),
                  created_by_actor_id=str(row['created_by']),updated_by_actor_id=str(row['updated_by']))
    if note: result.update(study_id=str(row['study_id']),visibility=row['visibility'],value=row['value'])
    else: result['title']=row['title']
    return (NoteView if note else StudyView).model_validate_json(json.dumps(result,ensure_ascii=False)).model_dump(mode='json')

class PersonalNotesStorage:
    def __init__(self,url): self.url=url.replace('postgresql+psycopg://','postgresql://',1)

    @asynccontextmanager
    async def transaction(self,identity,deadline,*,write=False):
        connection=None
        committing=False
        timer=None
        try:
            async with asyncio.timeout(remaining(deadline)):
                connection=await psycopg.AsyncConnection.connect(self.url,autocommit=False,row_factory=dict_row,connect_timeout=1)
                timer=asyncio.get_running_loop().call_at(deadline,connection.pgconn.finish)
                async with connection.cursor() as cursor:
                    await cursor.execute("SELECT set_config('app.account_id',%s,true), set_config('lock_timeout',%s,true),set_config('statement_timeout',%s,true)",
                        (identity['account_id'],str(max(1,min(1000,int(remaining(deadline)*1000))))+'ms',str(max(1,min(2000,int(remaining(deadline)*1000))))+'ms'))
                    yield cursor
                    remaining(deadline)
                    committing=True
                    await connection.commit()
        except NotesError: raise
        except BaseException as exc:
            # No cancellation cleanup wait: close the dedicated libpq socket.
            code='operation_unresolved' if write and committing else 'request_deadline_exceeded' if time.monotonic()>=deadline else 'studies_storage_unavailable'
            if isinstance(exc,(KeyboardInterrupt,SystemExit)): raise
            raise NotesError(code) from None
        finally:
            if timer is not None:timer.cancel()
            if connection is not None: connection.pgconn.finish()

    async def _parent(self,cursor,account,study,*,lock=False):
        await cursor.execute(f'SELECT * FROM {SCHEMA}.studies WHERE account_id=%s AND id=%s AND active'+(' FOR UPDATE' if lock else ''),(account,study))
        row=await cursor.fetchone()
        if row is None: raise NotesError('resource_unavailable')
        return row

    async def _note(self,cursor,account,study,note,*,lock=False):
        await cursor.execute(f'SELECT * FROM {SCHEMA}.notes WHERE account_id=%s AND study_id=%s AND id=%s AND active'+(' FOR UPDATE' if lock else ''),(account,study,note))
        row=await cursor.fetchone()
        if row is None: raise NotesError('resource_unavailable')
        return row

    async def _live_outcome(self,cursor,account,outcome):
        await self._parent(cursor,account,outcome['study_id'])
        if outcome['note_id'] is not None: await self._note(cursor,account,outcome['study_id'],outcome['note_id'])

    async def execute(self,identity,command,payload,study_id,note_id,deadline):
        account,actor=identity['account_id'],identity['actor_id']
        body=payload.model_dump(mode='json')
        fingerprint=hashlib.sha256(json.dumps({'command':command,'version':1,'study_id':study_id,'note_id':note_id,'payload':body},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        async with self.transaction(identity,deadline,write=True) as cursor:
            # An operation lock resolves duplicate requests before taking resource locks.
            await cursor.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",('operation:'+account+':'+command+':'+payload.operation_id,))
            await cursor.execute(f'SELECT fingerprint,outcome FROM {SCHEMA}.receipts WHERE account_id=%s AND command=%s AND command_version=1 AND operation_id=%s',(account,command,payload.operation_id))
            receipt=await cursor.fetchone()
            if receipt:
                if receipt['fingerprint']!=fingerprint: raise NotesError('operation_payload_mismatch')
                await self._live_outcome(cursor,account,receipt['outcome'])
                return OperationAck.model_validate(receipt['outcome']).model_dump(mode='json')
            if command=='study.create':
                study_id=str(uuid4()); title=payload.title
                await cursor.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",('titles:'+account,))
                if title is None:
                    await cursor.execute(f'SELECT title FROM {SCHEMA}.studies WHERE account_id=%s AND active',(account,))
                    titles={row['title'] for row in await cursor.fetchall()}
                    title='Untitled study'; number=0
                    while title in titles:
                        remaining(deadline); number+=1; title=f'Untitled study {number}'
                await cursor.execute(f'INSERT INTO {SCHEMA}.studies(id,account_id,title,created_by,updated_by) VALUES(%s,%s,%s,%s,%s)',(study_id,account,title,actor,actor))
                revision='1'
            else:
                await self._parent(cursor,account,study_id,lock=True)
                value=payload.value.model_dump(mode='json')
                if command=='note.create':
                    note_id=str(uuid4());revision='1'
                    await cursor.execute(f'INSERT INTO {SCHEMA}.notes(id,account_id,study_id,value,created_by,updated_by) VALUES(%s,%s,%s,%s,%s,%s)',(note_id,account,study_id,Jsonb(value),actor,actor))
                else:
                    row=await self._note(cursor,account,study_id,note_id,lock=True)
                    # Refuse richer saved aggregates before a restricted writer can erase them.
                    view(row,True)
                    revision=str(row['revision'])
                    if revision!=payload.expected_revision: raise NotesError('note_revision_conflict',{'expected_revision':payload.expected_revision,'current_revision':revision})
                    if row['value']!=value:
                        if row['revision']>=int(MAX_REVISION): raise NotesError('resource_unavailable')
                        revision=str(row['revision']+1)
                        await cursor.execute(f'UPDATE {SCHEMA}.notes SET value=%s, revision=revision+1, updated_by=%s, updated_at=clock_timestamp() WHERE account_id=%s AND study_id=%s AND id=%s',(Jsonb(value),actor,account,study_id,note_id))
            outcome={'operation_id':payload.operation_id,'command':command,'study_id':study_id,'note_id':note_id,'revision':revision}
            await cursor.execute(f'INSERT INTO {SCHEMA}.receipts(account_id,command,command_version,operation_id,fingerprint,outcome,study_id,note_id,created_by) VALUES(%s,%s,1,%s,%s,%s,%s,%s,%s)',(account,command,payload.operation_id,fingerprint,Jsonb(outcome),study_id,note_id,actor))
            return OperationAck.model_validate(outcome).model_dump(mode='json')

    async def lookup(self,identity,operation_id,command,deadline):
        async with self.transaction(identity,deadline) as cursor:
            await cursor.execute(f'SELECT outcome FROM {SCHEMA}.receipts WHERE account_id=%s AND command=%s AND command_version=1 AND operation_id=%s',(identity['account_id'],command,operation_id))
            row=await cursor.fetchone()
            if row is None: return {'status':'unresolved'}
            await self._live_outcome(cursor,identity['account_id'],row['outcome'])
            return {'status':'committed','outcome':OperationAck.model_validate(row['outcome']).model_dump(mode='json')}

    async def read(self,identity,study_id,note_id,deadline):
        async with self.transaction(identity,deadline) as cursor:
            parent=await self._parent(cursor,identity['account_id'],study_id)
            return view(await self._note(cursor,identity['account_id'],study_id,note_id),True) if note_id else view(parent)

    async def list(self,identity,study_id,limit,cursor_value,deadline):
        resource='notes' if study_id else 'studies'; account=identity['account_id']
        position=decode(cursor_value,resource,account,study_id) if cursor_value else None
        async with self.transaction(identity,deadline) as cursor:
            if study_id: await self._parent(cursor,account,study_id)
            where='account_id=%s AND active'; values=[account]
            if study_id: where+=' AND study_id=%s';values.append(study_id)
            if position: where+=' AND (created_at,id)<(%s::timestamptz,%s::uuid)';values.extend(position)
            await cursor.execute(f'SELECT * FROM {SCHEMA}.{resource} WHERE {where} ORDER BY created_at DESC,id DESC LIMIT %s',(*values,limit+1))
            rows=await cursor.fetchall(); more=len(rows)>limit; rows=rows[:limit]
            return {'items':[view(row,bool(study_id)) for row in rows],'next_cursor':encode(resource,account,study_id,stamp(rows[-1]['created_at']),str(rows[-1]['id'])) if more else None}
