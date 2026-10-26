"""Independent own-copy transactions; every write uses the owner's parent lane."""
import asyncio
import copy
import json
from uuid import uuid4
from psycopg.types.json import Jsonb
from personal_notes_access import NotesError
from personal_notes_contract import OperationAck, ReplacePassages, NoteValue
from pydantic import TypeAdapter,ValidationError
from own_highlights import metadata, validate

SCHEMA='scribeswell_studies'
COMMANDS=('note.duplicate','note.conflict_copy','study.copy')

def independent_value(value):
    result=copy.deepcopy(value)
    for key in ('connections','highlights'):
        for item in result.get(key,[]):item['id']=str(uuid4())
    # Refuse unknown source aggregates instead of narrowing their content.
    try:return TypeAdapter(NoteValue).validate_json(json.dumps(result)).model_dump(mode='json')
    except (ValidationError,ValueError,TypeError):raise NotesError('note_format_unsupported') from None

def check_bounds(title,notes,passages):
    aggregate={'title':title,'notes':[{'visibility':n['visibility'],'value':n['value']} for n in notes],
               'passages':[p['reference'] for p in passages]}
    if len(notes)>128 or len(passages)>200 or len(json.dumps(aggregate,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())>2097152:
        raise NotesError('copy_limit_exceeded')

def legacy_without_anchors(value):return not value.get('highlights')

async def base_metadata(storage,cursor,account,study,note,payload):
    await storage._parent(cursor,account,study)
    await storage._note(cursor,account,study,note)
    await cursor.execute(f'SELECT metadata FROM {SCHEMA}.note_revision_metadata WHERE account_id=%s AND study_id=%s AND note_id=%s AND revision=%s',
                         (account,study,note,int(payload.base_revision)))
    row=await cursor.fetchone()
    if row:return row['metadata']
    if not legacy_without_anchors(payload.value.model_dump(mode='json')):raise NotesError('note_base_unavailable')
    return {}

async def provenance(cursor,account,destination_study,destination_note,source_study,source_note,relation,actor):
    table='note_copy_provenance' if destination_note else 'study_copy_provenance'
    predicate=' AND note_id=%s' if source_note else ''
    await cursor.execute(f'SELECT * FROM {SCHEMA}.{table} WHERE account_id=%s AND study_id=%s'+predicate,
                         (account,source_study,source_note) if source_note else (account,source_study))
    original=await cursor.fetchone()
    origin_account=str(original['origin_account_id']) if original else account
    origin_study=str(original['origin_study_id']) if original else source_study
    columns='account_id,study_id,source_account_id,source_study_id,origin_account_id,origin_study_id,relation,created_by'
    values=[account,destination_study,account,source_study,origin_account,origin_study,relation,actor]
    if destination_note:
        columns+=',note_id,source_note_id,origin_note_id'
        values.extend([destination_note,source_note,str(original['origin_note_id']) if original else source_note])
    await cursor.execute(f'INSERT INTO {SCHEMA}.{table}({columns}) VALUES('+','.join(['%s']*len(values))+')',tuple(values))

async def insert_note(cursor,account,actor,study,value,visibility):
    if visibility!='study':raise NotesError('note_format_unsupported')
    identifier=str(uuid4());value=independent_value(value)
    await cursor.execute(f'INSERT INTO {SCHEMA}.notes(id,account_id,study_id,visibility,value,created_by,updated_by) VALUES(%s,%s,%s,%s,%s,%s,%s)',
                         (identifier,account,study,visibility,Jsonb(value),actor,actor))
    await cursor.execute(f'INSERT INTO {SCHEMA}.note_revision_metadata(account_id,study_id,note_id,revision,metadata,created_by) VALUES(%s,%s,%s,1,%s,%s)',
                         (account,study,identifier,Jsonb(metadata(value)),actor))
    return identifier

async def execute_copy(storage,identity,command,payload,study,note,deadline,fingerprint):
    account,actor=identity['account_id'],identity['actor_id'];observations={};base={}
    # All copies reconcile before touching the source. Unknown outcomes reuse the
    # exact operation and fingerprint; deleted sources are irrelevant to replay.
    async with storage.transaction(identity,deadline) as cursor:
        await cursor.execute(f'SELECT fingerprint,outcome FROM {SCHEMA}.receipts WHERE account_id=%s AND command=%s AND command_version=1 AND operation_id=%s',(account,command,payload.operation_id))
        previous=await cursor.fetchone()
        if previous:
            if previous['fingerprint']!=fingerprint:raise NotesError('operation_payload_mismatch')
            await storage._live_outcome(cursor,account,previous['outcome'])
            return OperationAck.model_validate(previous['outcome']).model_dump(mode='json')
        if command=='note.conflict_copy':base=await base_metadata(storage,cursor,account,study,note,payload)
    if command=='note.conflict_copy':
        value=payload.value.model_dump(mode='json');trusted={h['id']:h['anchor'] for h in base.get('highlights',[])}
        changed=[h for h in value.get('highlights',[]) if trusted.get(h['id'])!=h['anchor']]
        if changed:
            from own_highlights import observe
            observations=await asyncio.to_thread(observe,{'highlights':changed},deadline)
        validate(value,base,observations)
    async with storage.transaction(identity,deadline,write=True) as cursor:
        await cursor.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',('operation:'+account+':'+command+':'+payload.operation_id,))
        await cursor.execute(f'SELECT fingerprint,outcome FROM {SCHEMA}.receipts WHERE account_id=%s AND command=%s AND command_version=1 AND operation_id=%s',(account,command,payload.operation_id))
        previous=await cursor.fetchone()
        if previous:
            if previous['fingerprint']!=fingerprint:raise NotesError('operation_payload_mismatch')
            await storage._live_outcome(cursor,account,previous['outcome'])
            return OperationAck.model_validate(previous['outcome']).model_dump(mode='json')
        # There is one existing parent; the new destination is allocated after
        # validation, so no opposing parent lock order is possible.
        parent=await storage._parent(cursor,account,study,lock=True)
        destination=study;destination_note=None
        if command=='study.copy':
            revision=str(parent['revision'])
            if revision!=payload.expected_revision:raise NotesError('study_revision_conflict',{'expected_revision':payload.expected_revision,'current_revision':revision})
            # Never page through the outline API and mistake its first page for all.
            await cursor.execute(f'SELECT * FROM {SCHEMA}.notes WHERE account_id=%s AND study_id=%s AND active ORDER BY id LIMIT 129',(account,study))
            notes=await cursor.fetchall()
            passages,_=await storage._passages(cursor,account,study)
            check_bounds(parent['title'],notes,passages['items'])
            if any(row['visibility']!='study' for row in notes):raise NotesError('note_format_unsupported')
            # Validate all aggregates before allocating destination identities.
            for row in notes:
                try:TypeAdapter(NoteValue).validate_json(json.dumps(row['value']))
                except (ValidationError,ValueError,TypeError):raise NotesError('note_format_unsupported') from None
            destination=str(uuid4())
            await cursor.execute(f'INSERT INTO {SCHEMA}.studies(id,account_id,title,created_by,updated_by) VALUES(%s,%s,%s,%s,%s)',(destination,account,parent['title'],actor,actor))
            await provenance(cursor,account,destination,None,study,None,command,actor)
            for row in notes:
                copied=await insert_note(cursor,account,actor,destination,row['value'],row['visibility'])
                await provenance(cursor,account,destination,copied,study,str(row['id']),command,actor)
            if passages['items']:
                replacement=ReplacePassages.model_validate_json(json.dumps({'operation_id':payload.operation_id,'expected_revision':'1','items':[{'id':str(uuid4()),'reference':p['reference']} for p in passages['items']]}))
                await storage._replace_passages(cursor,account,actor,destination,replacement)
        else:
            source=await storage._note(cursor,account,study,note,lock=True)
            if source['visibility']!='study':raise NotesError('note_format_unsupported')
            if command=='note.duplicate':
                revision=str(source['revision'])
                if revision!=payload.expected_revision:raise NotesError('note_revision_conflict',{'expected_revision':payload.expected_revision,'current_revision':revision})
                value=source['value']
            else:
                # Immutable base metadata is rechecked with the active source under
                # parent/note locks, never substituted with the latest revision.
                base=await base_metadata(storage,cursor,account,study,note,payload)
                value=payload.value.model_dump(mode='json');validate(value,base,observations)
                if int(payload.base_revision)>source['revision']:raise NotesError('note_base_unavailable')
            destination_note=await insert_note(cursor,account,actor,destination,value,source['visibility'])
            await provenance(cursor,account,destination,destination_note,study,note,command,actor)
        outcome={'operation_id':payload.operation_id,'command':command,'study_id':destination,'note_id':destination_note,'revision':'1'}
        await cursor.execute(f'INSERT INTO {SCHEMA}.receipts(account_id,command,command_version,operation_id,fingerprint,outcome,study_id,note_id,created_by) VALUES(%s,%s,1,%s,%s,%s,%s,%s,%s)',(account,command,payload.operation_id,fingerprint,Jsonb(outcome),destination,destination_note,actor))
        return OperationAck.model_validate(outcome).model_dump(mode='json')


async def credit(cursor,account,study,note=None):
    table='note_copy_provenance' if note else 'study_copy_provenance'
    await cursor.execute(f'SELECT * FROM {SCHEMA}.{table} WHERE account_id=%s AND study_id=%s'+(' AND note_id=%s' if note else ''),(account,study,note) if note else (account,study))
    row=await cursor.fetchone()
    if not row:return None
    # Resolve original credit only with current source account ownership, parent
    # lifecycle and (where present) note lifecycle. Never cache source labels.
    origin_note=str(row['origin_note_id']) if note else None
    origin_study=str(row['origin_study_id']);origin_account=str(row['origin_account_id'])
    label='Original unavailable'
    if origin_account==account:
        sql=f'SELECT title FROM {SCHEMA}.studies WHERE account_id=%s AND id=%s AND active'
        args=[account,origin_study]
        if origin_note:
            sql+=f' AND EXISTS(SELECT 1 FROM {SCHEMA}.notes WHERE account_id=%s AND study_id=%s AND id=%s AND active AND visibility=\'study\')'
            args.extend([account,origin_study,origin_note])
        await cursor.execute(sql,tuple(args));source=await cursor.fetchone()
        if source:label=source['title']
    return {'relation':row['relation'],'source_account_id':str(row['source_account_id']),'source_study_id':str(row['source_study_id']),
            'source_note_id':str(row['source_note_id']) if note else None,'origin_account_id':origin_account,'origin_study_id':origin_study,
            'origin_note_id':origin_note,'created_at':row['created_at'].astimezone(__import__('datetime').timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'created_by_actor_id':str(row['created_by']),'label':label}
