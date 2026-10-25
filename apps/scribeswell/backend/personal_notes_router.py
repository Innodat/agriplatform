"""Private HTTP boundary: bounded decoding and safe errors on every path."""
import asyncio
import time
from fastapi import APIRouter,Request
from fastapi.responses import JSONResponse
from pydantic import TypeAdapter
from personal_notes_contract import Identifier,parse_command,ContractInputError,MAX_BODY_BYTES,MAX_PASSAGE_BODY_BYTES,MAX_SEARCH_BODY_BYTES
from personal_notes_access import NotesError,STATUSES

async def body(request,limit=MAX_BODY_BYTES):
    raw=bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw)>limit: raise NotesError('scribeswell_personal_notes_input_invalid')
    return bytes(raw)

def build_router(access,storage):
    router=APIRouter()
    async def handle(request,kind):
        deadline=time.monotonic()+5
        try:
            async with asyncio.timeout(5):
                study_id=request.path_params.get('study_id'); note_id=request.path_params.get('note_id')
                operation_id=request.path_params.get('operation_id')
                for identifier in (study_id,note_id,operation_id):
                    if identifier is not None: TypeAdapter(Identifier).validate_python(identifier)
                bearer=request.headers.get('authorization','')
                if not bearer.startswith('Bearer ') or not bearer[7:]: raise NotesError('authentication_required')
                if kind=='enroll':
                    payload=parse_command('studies.enroll',await body(request))
                    result=await access.enroll(bearer,payload.operation_id,deadline)
                else:
                    payload=parse_command(kind,await body(request,MAX_SEARCH_BODY_BYTES if kind=='studies.search' else MAX_PASSAGE_BODY_BYTES if kind=='study.passages.replace' else MAX_BODY_BYTES)) if kind in ('studies.search','study.create','study.rename','study.passages.replace','note.create','note.replace','note.delete') else None
                    allowed={'limit','cursor'} if kind=='list' else {'command'} if kind=='lookup' else set()
                    if set(request.query_params)-allowed or any(len(request.query_params.getlist(k))!=1 for k in request.query_params): raise ValueError
                    # Fresh remote authority, completed before the first local transaction.
                    identity=await access.check(bearer,deadline)
                    if kind=='studies.search': result=await storage.search(identity,payload,deadline)
                    elif payload is not None: result=await storage.execute(identity,kind,payload,study_id,note_id,deadline)
                    elif kind=='passages': result=await storage.passages(identity,study_id,deadline)
                    elif kind=='read': result=await storage.read(identity,study_id,note_id,deadline)
                    elif kind=='list':
                        raw_limit=request.query_params.get('limit','20')
                        if not raw_limit.isascii() or not raw_limit.isdigit() or not 1<=int(raw_limit)<=50: raise ValueError
                        result=await storage.list(identity,study_id,int(raw_limit),request.query_params.get('cursor'),deadline)
                    else:
                        command=request.query_params.get('command')
                        if command not in ('study.create','study.rename','study.passages.replace','note.create','note.replace','note.delete'): raise ValueError
                        result=await storage.lookup(identity,operation_id,command,deadline)
                return JSONResponse(result,headers={'Cache-Control':'private, no-store'})
        except NotesError as error:
            code,details=error.code,error.details
        except (ContractInputError,ValueError,TypeError): code,details='scribeswell_personal_notes_input_invalid',None
        except TimeoutError: code,details='request_deadline_exceeded',None
        except Exception: code,details='studies_storage_unavailable',None
        return JSONResponse({'error':'Request could not be completed','code':code,'details':details},status_code=STATUSES[code],headers={'Cache-Control':'private, no-store'})

    @router.post('/api/studies/search')
    async def search_studies(request:Request): return await handle(request,'studies.search')
    @router.post('/api/studies/enrollment')
    async def enrollment(request:Request): return await handle(request,'enroll')
    @router.post('/api/studies')
    async def create_study(request:Request): return await handle(request,'study.create')
    @router.get('/api/studies')
    async def list_studies(request:Request): return await handle(request,'list')
    @router.get('/api/studies/{study_id}')
    async def read_study(request:Request): return await handle(request,'read')
    @router.get('/api/studies/{study_id}/passages')
    async def passages(request:Request): return await handle(request,'passages')
    @router.put('/api/studies/{study_id}/passages')
    async def replace_passages(request:Request): return await handle(request,'study.passages.replace')
    @router.put('/api/studies/{study_id}/title')
    async def rename_study(request:Request): return await handle(request,'study.rename')
    @router.post('/api/studies/{study_id}/notes')
    async def create_note(request:Request): return await handle(request,'note.create')
    @router.get('/api/studies/{study_id}/notes')
    async def list_notes(request:Request): return await handle(request,'list')
    @router.get('/api/studies/{study_id}/notes/{note_id}')
    async def read_note(request:Request): return await handle(request,'read')
    @router.put('/api/studies/{study_id}/notes/{note_id}')
    async def replace_note(request:Request): return await handle(request,'note.replace')
    @router.delete('/api/studies/{study_id}/notes/{note_id}')
    async def delete_note(request:Request): return await handle(request,'note.delete')
    @router.get('/api/operations/{operation_id}')
    async def lookup(request:Request): return await handle(request,'lookup')
    return router
