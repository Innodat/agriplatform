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
from personal_notes_contract import MAX_REVISION,StudyView,NoteView,OperationAck,PassageList
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
        if outcome['command']=='study.delete':
            await cursor.execute(f'SELECT id FROM {SCHEMA}.studies WHERE account_id=%s AND id=%s AND NOT active',(account,outcome['study_id']))
            if await cursor.fetchone() is None: raise NotesError('resource_unavailable')
            return
        if outcome['command']=='note.delete':
            await cursor.execute(f'SELECT id FROM {SCHEMA}.notes WHERE account_id=%s AND study_id=%s AND id=%s AND NOT active',(account,outcome['study_id'],outcome['note_id']))
            if await cursor.fetchone() is None: raise NotesError('resource_unavailable')
            return
        await self._parent(cursor,account,outcome['study_id'])
        if outcome['note_id'] is not None: await self._note(cursor,account,outcome['study_id'],outcome['note_id'])

    async def execute(self,identity,command,payload,study_id,note_id,deadline):
        account,actor=identity['account_id'],identity['actor_id']
        body=payload.model_dump(mode='json')
        fingerprint=hashlib.sha256(json.dumps({'command':command,'version':1,'study_id':study_id,'note_id':note_id,'payload':body},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        from own_copies import COMMANDS,execute_copy
        if command in COMMANDS:return await execute_copy(self,identity,command,payload,study_id,note_id,deadline,fingerprint)
        observations={}
        if command in ('note.create','note.replace') and body['value'].get('highlights'):
            # Reconcile before source waits. This read takes no business write lock;
            # the later transaction rechecks current lifecycle/revision atomically.
            async with self.transaction(identity,deadline) as read_cursor:
                await read_cursor.execute(f'SELECT fingerprint,outcome FROM {SCHEMA}.receipts WHERE account_id=%s AND command=%s AND command_version=1 AND operation_id=%s',(account,command,payload.operation_id))
                previous=await read_cursor.fetchone()
                if previous:
                    if previous['fingerprint']!=fingerprint:raise NotesError('operation_payload_mismatch')
                    await self._live_outcome(read_cursor,account,previous['outcome'])
                    return OperationAck.model_validate(previous['outcome']).model_dump(mode='json')
                prior=(await self._note(read_cursor,account,study_id,note_id))['value'] if command=='note.replace' else {}
            trusted={h['id']:h['anchor'] for h in prior.get('highlights',[])}
            changed=[h for h in body['value']['highlights'] if trusted.get(h['id'])!=h['anchor']]
            if changed:
                from own_highlights import observe
                observations=await asyncio.to_thread(observe,{'highlights':changed},deadline)
        async with self.transaction(identity,deadline,write=True) as cursor:
            # An operation lock resolves duplicate requests before taking resource locks.
            await cursor.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",('operation:'+account+':'+command+':'+payload.operation_id,))
            await cursor.execute(f'SELECT fingerprint,outcome FROM {SCHEMA}.receipts WHERE account_id=%s AND command=%s AND command_version=1 AND operation_id=%s',(account,command,payload.operation_id))
            receipt=await cursor.fetchone()
            if receipt:
                if receipt['fingerprint']!=fingerprint: raise NotesError('operation_payload_mismatch')
                if command in ('study.rename','study.passages.replace'): await self._parent(cursor,account,receipt['outcome']['study_id'],lock=True)
                else: await self._live_outcome(cursor,account,receipt['outcome'])
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
            elif command=='study.rename':
                row=await self._parent(cursor,account,study_id,lock=True)
                revision=str(row['revision'])
                if revision!=payload.expected_revision: raise NotesError('study_revision_conflict',{'expected_revision':payload.expected_revision,'current_revision':revision})
                if row['title']!=payload.title:
                    if row['revision']>=int(MAX_REVISION): raise NotesError('resource_unavailable')
                    revision=str(row['revision']+1)
                    await cursor.execute(f'UPDATE {SCHEMA}.studies SET title=%s, revision=revision+1, updated_by=%s, updated_at=clock_timestamp() WHERE account_id=%s AND id=%s',(payload.title,actor,account,study_id))
            elif command=='study.delete':
                row=await self._parent(cursor,account,study_id,lock=True)
                revision=str(row['revision'])
                if revision!=payload.expected_revision: raise NotesError('study_revision_conflict',{'expected_revision':payload.expected_revision,'current_revision':revision})
                if row['revision']>=int(MAX_REVISION): raise NotesError('resource_unavailable')
                # Every API child writer locks this parent first. Preflight all
                # active notes before erasing anything; inactive receipts stay intact.
                await cursor.execute(f'SELECT id FROM {SCHEMA}.notes WHERE account_id=%s AND study_id=%s AND active AND revision>=%s LIMIT 1',(account,study_id,int(MAX_REVISION)))
                if await cursor.fetchone() is not None: raise NotesError('resource_unavailable')
                empty={'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}
                await cursor.execute(f'UPDATE {SCHEMA}.notes SET value=%s, active=false, revision=revision+1, updated_by=%s, updated_at=clock_timestamp() WHERE account_id=%s AND study_id=%s AND active',(Jsonb(empty),actor,account,study_id))
                await cursor.execute(f'DELETE FROM {SCHEMA}.passage_entries WHERE account_id=%s AND study_id=%s',(account,study_id))
                await cursor.execute(f'DELETE FROM {SCHEMA}.passage_lists WHERE account_id=%s AND study_id=%s',(account,study_id))
                await cursor.execute(f"UPDATE {SCHEMA}.studies SET title='Deleted study', active=false, revision=revision+1, updated_by=%s, updated_at=clock_timestamp() WHERE account_id=%s AND id=%s",(actor,account,study_id))
                revision=str(row['revision']+1)
            elif command=='study.passages.replace':
                await self._parent(cursor,account,study_id,lock=True)
                revision=await self._replace_passages(cursor,account,actor,study_id,payload)
            else:
                await self._parent(cursor,account,study_id,lock=True)
                value={'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]} if command=='note.delete' else payload.value.model_dump(mode='json')
                if command=='note.create':
                    from own_highlights import validate
                    validate(value,{},observations)
                    note_id=str(uuid4());revision='1'
                    await cursor.execute(f'INSERT INTO {SCHEMA}.notes(id,account_id,study_id,value,created_by,updated_by) VALUES(%s,%s,%s,%s,%s,%s)',(note_id,account,study_id,Jsonb(value),actor,actor))
                else:
                    row=await self._note(cursor,account,study_id,note_id,lock=True)
                    # Refuse richer saved aggregates before a restricted writer can erase them.
                    view(row,True)
                    revision=str(row['revision'])
                    if revision!=payload.expected_revision: raise NotesError('note_revision_conflict',{'expected_revision':payload.expected_revision,'current_revision':revision})
                    if command!='note.delete':
                        from own_highlights import validate
                        validate(value,row['value'],observations)
                        if row['value'].get('format_version')==3 and value.get('format_version')!=3:raise NotesError('note_format_unsupported')
                    if command!='note.delete' and row['value']['document']['version']==2 and value['document']['version']==1:
                        raise NotesError('note_format_unsupported')
                    if command=='note.delete' or row['value']!=value:
                        if row['revision']>=int(MAX_REVISION): raise NotesError('resource_unavailable')
                        revision=str(row['revision']+1)
                        await cursor.execute(f'UPDATE {SCHEMA}.notes SET value=%s, active=%s, revision=revision+1, updated_by=%s, updated_at=clock_timestamp() WHERE account_id=%s AND study_id=%s AND id=%s',(Jsonb(value),command!='note.delete',actor,account,study_id,note_id))
            if command in ('note.create','note.replace'):
                from own_highlights import metadata
                await cursor.execute(f'INSERT INTO {SCHEMA}.note_revision_metadata(account_id,study_id,note_id,revision,metadata,created_by) VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING',(account,study_id,note_id,int(revision),Jsonb(metadata(value)),actor))
            outcome={'operation_id':payload.operation_id,'command':command,'study_id':study_id,'note_id':note_id,'revision':revision}
            await cursor.execute(f'INSERT INTO {SCHEMA}.receipts(account_id,command,command_version,operation_id,fingerprint,outcome,study_id,note_id,created_by) VALUES(%s,%s,1,%s,%s,%s,%s,%s,%s)',(account,command,payload.operation_id,fingerprint,Jsonb(outcome),study_id,note_id,actor))
            return OperationAck.model_validate(outcome).model_dump(mode='json')

    async def _passages(self,cursor,account,study_id):
        await cursor.execute(f'SELECT revision FROM {SCHEMA}.passage_lists WHERE account_id=%s AND study_id=%s',(account,study_id))
        header=await cursor.fetchone()
        await cursor.execute(f'SELECT * FROM {SCHEMA}.passage_entries WHERE account_id=%s AND study_id=%s ORDER BY position',(account,study_id))
        rows=await cursor.fetchall()
        items=[]
        for row in rows:
            reference={key:row[key] for key in ('catalogue_id','catalogue_version','versification_id','book_id')}
            reference['target']={'kind':'chapter','chapter':row['start_chapter']} if row['kind']=='chapter' else {'kind':'verse_range','start':{'chapter':row['start_chapter'],'verse':row['start_verse']},'end':{'chapter':row['end_chapter'],'verse':row['end_verse']}}
            items.append({'id':str(row['id']),'reference':reference})
        return PassageList.model_validate_json(json.dumps({'study_id':study_id,'revision':str(header['revision']) if header else '1','items':items})).model_dump(mode='json'),rows

    async def passages(self,identity,study_id,deadline):
        async with self.transaction(identity,deadline) as cursor:
            # The same parent lock gives a coherent header/ordered-entry snapshot.
            await self._parent(cursor,identity['account_id'],study_id,lock=True)
            result,_=await self._passages(cursor,identity['account_id'],study_id)
            return result

    async def _replace_passages(self,cursor,account,actor,study_id,payload):
        current,rows=await self._passages(cursor,account,study_id)
        revision=current['revision']
        if revision!=payload.expected_revision:raise NotesError('passage_revision_conflict',{'expected_revision':payload.expected_revision,'current_revision':revision})
        items=[item.model_dump(mode='json') for item in payload.items]
        if items==current['items']:return revision
        if int(revision)>=int(MAX_REVISION):raise NotesError('resource_unavailable')
        retained={item['id']:item['reference'] for item in current['items']}
        if any(item['id'] in retained and retained[item['id']]!=item['reference'] for item in items):raise NotesError('scribeswell_personal_notes_input_invalid')
        retained_references={json.dumps(item['reference'],sort_keys=True):item['id'] for item in current['items']}
        if any(retained_references.get(json.dumps(item['reference'],sort_keys=True),item['id'])!=item['id'] for item in items):raise NotesError('scribeswell_personal_notes_input_invalid')
        revision=str(int(revision)+1)
        if current['revision']=='1':
            await cursor.execute(f'INSERT INTO {SCHEMA}.passage_lists(account_id,study_id,revision,created_by,updated_by) VALUES(%s,%s,%s,%s,%s)',(account,study_id,int(revision),actor,actor))
        else:
            await cursor.execute(f'UPDATE {SCHEMA}.passage_lists SET revision=%s,updated_by=%s,updated_at=clock_timestamp() WHERE account_id=%s AND study_id=%s',(int(revision),actor,account,study_id))
        # Replace order atomically; preserve original creation attribution of retained IDs.
        originals={str(row['id']):row for row in rows}
        await cursor.execute(f'DELETE FROM {SCHEMA}.passage_entries WHERE account_id=%s AND study_id=%s',(account,study_id))
        for position,item in enumerate(items,1):
            reference=item['reference'];target=reference['target'];old=originals.get(item['id'])
            start=target['start'] if target['kind']=='verse_range' else {'chapter':target['chapter'],'verse':None}
            end=target.get('end',{'chapter':None,'verse':None})
            await cursor.execute(f'INSERT INTO {SCHEMA}.passage_entries(account_id,study_id,id,position,catalogue_id,catalogue_version,versification_id,book_id,kind,start_chapter,start_verse,end_chapter,end_verse,created_at,created_by) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,COALESCE(%s,clock_timestamp()),%s)',(account,study_id,item['id'],position,reference['catalogue_id'],reference['catalogue_version'],reference['versification_id'],reference['book_id'],target['kind'],start['chapter'],start['verse'],end['chapter'],end['verse'],old['created_at'] if old else None,old['created_by'] if old else actor))
        return revision

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
            from own_copies import credit
            result=view(await self._note(cursor,identity['account_id'],study_id,note_id),True) if note_id else view(parent)
            source_credit=await credit(cursor,identity['account_id'],study_id,note_id)
            if source_credit is not None:result['copy_credit']=source_credit
            return result

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

    async def search(self,identity,payload,deadline):
        from personal_notes_search import canonical_query,decode_cursor,encode_cursor,search_sql
        account=identity['account_id'];query=canonical_query(payload.query)
        position=decode_cursor(payload.cursor,account,query) if payload.cursor else None
        sql,values=search_sql(account,query,position,payload.limit)
        async with self.transaction(identity,deadline) as cursor:
            await cursor.execute(sql,values)
            rows=await cursor.fetchall();more=len(rows)>payload.limit;rows=rows[:payload.limit]
            return {'items':[view(row) for row in rows], 'next_cursor':encode_cursor(account,query,stamp(rows[-1]['created_at']),str(rows[-1]['id'])) if more else None}
