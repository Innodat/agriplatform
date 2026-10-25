"""Bounded server-only Access adapter; never trusts browser account or JWT claims."""
import asyncio
import time
from datetime import datetime, timedelta
import httpx
from pydantic import TypeAdapter
from personal_notes_contract import Identifier, UtcTimestamp

class NotesError(Exception):
    def __init__(self, code, details=None):
        self.code, self.details = code, details
        super().__init__(code)

STATUSES = {'scribeswell_personal_notes_input_invalid':400,'authentication_required':401,
    'studies_access_denied':403,'resource_unavailable':404,'note_revision_conflict':409,'study_revision_conflict':409,'passage_revision_conflict':409,
    'operation_payload_mismatch':409,'operation_unresolved':409,'studies_access_unavailable':503,
    'studies_storage_unavailable':503,'request_deadline_exceeded':503}

def remaining(deadline):
    seconds=deadline-time.monotonic()
    if seconds <= 0: raise NotesError('request_deadline_exceeded')
    return seconds

class StudiesAccess:
    def __init__(self, url, service_key, transport=None):
        self.url=url.rstrip('/'); self.key=service_key; self.transport=transport

    async def _request(self, path, bearer, payload, deadline):
        if not bearer or not bearer.startswith('Bearer ') or len(bearer)>8192:
            raise NotesError('authentication_required')
        try:
            async with asyncio.timeout(min(3,remaining(deadline))):
                async with httpx.AsyncClient(transport=self.transport,timeout=min(3,remaining(deadline)),follow_redirects=False) as client:
                    async with client.stream('POST',self.url+path,headers={'Authorization':bearer,'X-Service-Key':self.key},json=payload) as response:
                        parts=bytearray()
                        async for chunk in response.aiter_bytes():
                            parts.extend(chunk)
                            if len(parts)>8192: raise ValueError
                        if response.status_code!=200:
                            code='authentication_required' if response.status_code==401 else 'studies_access_denied' if response.status_code==403 else 'studies_access_unavailable'
                            raise NotesError(code)
                        import json
                        from personal_notes_contract import _unique_object
                        result=json.loads(parts,object_pairs_hook=_unique_object)
                        if type(result) is not dict: raise ValueError
                        return result
        except NotesError: raise
        except (Exception, asyncio.CancelledError):
            raise NotesError('request_deadline_exceeded' if time.monotonic()>=deadline else 'studies_access_unavailable') from None

    async def check(self,bearer,deadline):
        result=await self._request('/v2/check',bearer,{'permission':'scribeswell.studies.use','authorization_scope':{'kind':'account'}},deadline)
        try:
            if set(result)!={'account_id','actor_id','permission','authorization_scope','decision_id','checked_at'}: raise ValueError
            for field in ('account_id','actor_id','decision_id'): TypeAdapter(Identifier).validate_python(result[field])
            checked = TypeAdapter(datetime).validate_python(result['checked_at'])
            if checked.tzinfo is None or checked.utcoffset()!=timedelta(0): raise ValueError
            if result['permission']!='scribeswell.studies.use' or result['authorization_scope']!={'kind':'account'}: raise ValueError
        except Exception: raise NotesError('studies_access_unavailable') from None
        return result

    async def enroll(self,bearer,operation_id,deadline):
        result=await self._request('/v2/enrollments/scribeswell-studies',bearer,{'operation_id':operation_id},deadline)
        try:
            if set(result)!={'operation_id','status','result'} or result['operation_id']!=operation_id or result['status']!='committed': raise ValueError
            value=result['result']
            if set(value)!={'disposition','account_id','actor_id','permission'} or value['disposition'] not in ('created','unchanged') or value['permission']!='scribeswell.studies.use': raise ValueError
            for field in ('account_id','actor_id'): TypeAdapter(Identifier).validate_python(value[field])
        except Exception: raise NotesError('studies_access_unavailable') from None
        return result
