"""Owner seed: current Leave entry discovery over private Access HTTP."""
import asyncio,base64,re
from typing import Annotated
from pydantic import Field,field_validator
import httpx
from fastapi import APIRouter,Request,Security
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from contracts import Closed,Identifier,identifier,json_object
from access_client import Failure
from safe_errors import ErrorEnvelope


def cursor(value):
    if type(value) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{48}',value):raise ValueError('cursor')
    decoded=base64.b64decode(value,altchars=b'-_',validate=True).decode('ascii')
    identifier(decoded)
    if base64.urlsafe_b64encode(decoded.encode()).decode().rstrip('=')!=value:raise ValueError('cursor')
    return value

class Organization(Closed):
    org_id:Identifier
    name:Annotated[str,Field(max_length=4096)]
    membership_id:Annotated[str,Field(pattern=r'^[1-9][0-9]{0,18}$')]
    @field_validator('org_id')
    @classmethod
    def uuid(cls,value):return identifier(value)
    @field_validator('membership_id')
    @classmethod
    def member(cls,value):
        if int(value)>9223372036854775807:raise ValueError('membership')
        return value

class Organizations(Closed):
    organizations:Annotated[list[Organization],Field(max_length=100)]
    next_cursor:str|None
    @field_validator('next_cursor')
    @classmethod
    def next(cls,value):return cursor(value) if value is not None else None

async def discover(access,authorization,after):
    if access is None:raise Failure(503,'authorization_unavailable')
    try:
        async with asyncio.timeout(3):
            async with httpx.AsyncClient(base_url=access.config.origin,timeout=3,trust_env=False,follow_redirects=False,transport=access.transport) as client:
                params={'application':'leave','page_size':'100'}
                if after is not None:params['cursor']=after
                async with client.stream('GET','/v2/organizations',params=params,headers={'Authorization':authorization,'X-Service-Key':access.config.credential,'Accept-Encoding':'identity'}) as response:
                    if response.headers.get('content-encoding','identity').lower()!='identity':raise ValueError('encoding')
                    raw=bytearray()
                    async for chunk in response.aiter_bytes(chunk_size=65536):
                        if len(raw)+len(chunk)>65536:raise ValueError('size')
                        raw.extend(chunk)
                    value=json_object(raw)
                    if response.status_code!=200:
                        allowed={(401,'authentication_required'),(403,'access_denied'),(403,'service_access_denied'),(409,'identity.person_link_required'),(409,'identity.actor_setup_required'),(403,'identity.verification_required'),(503,'authorization_unavailable')}
                        if response.status_code==403 and value=={'detail':{'code':'service_access_denied'}}:raise Failure(403,'service_access_denied')
                        if type(value) is not dict or set(value)!={'error_id','error','details'} or type(value['error']) is not str or value['details']!={} or (response.status_code,value['error_id']) not in allowed:raise ValueError('error')
                        raise Failure(response.status_code,value['error_id'])
                    result=Organizations.model_validate(value)
                    previous=base64.b64decode(after,altchars=b'-_').decode() if after else ''
                    for org in result.organizations:
                        if org.org_id<=previous:raise ValueError('order')
                        previous=org.org_id
                    if result.next_cursor is not None and (not result.organizations or result.next_cursor!=base64.urlsafe_b64encode(previous.encode()).decode().rstrip('=')):raise ValueError('continuation')
                    return result
    except Failure:raise
    except Exception:raise Failure(503,'authorization_unavailable') from None
