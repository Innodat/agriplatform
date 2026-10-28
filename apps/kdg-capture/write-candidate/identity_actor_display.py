"""KDG's isolated HTTP consumer of Identity's closed display projection.

No Identity implementation imports, cache, ambient clients or credential discovery.
The injected transport must cooperate with cancellation and release owned resources.
"""
import asyncio
from dataclasses import dataclass
import hmac
import json
import time
import unicodedata
from typing import Annotated, Literal
from urllib.parse import urlsplit
from uuid import UUID

import httpx
from pydantic import AfterValidator, Field
import audit_read as audit

MAX_ACTORS=203
REQUEST_BYTES=16*1024
RESPONSE_BYTES=256*1024
ERROR_BYTES=1024
LOOKUP_SECONDS=3.0
FINAL_SECONDS=3.0
FINAL_RESERVE=0.25
UNWIND_RESERVE=0.1


def _name(value):
    if not value.strip() or any(unicodedata.category(c) in ('Cc','Cs') for c in value) or len(value.encode('utf-8'))>1024:
        raise ValueError('display_name')
    return value

Name=Annotated[str,Field(strict=True,min_length=1,max_length=256),AfterValidator(_name)]

class ResolvedLabel(audit.read.Closed):
    actor_id: audit.read.Identifier
    status: Literal['resolved']
    display_name: Name

class UnavailableLabel(audit.read.Closed):
    actor_id: audit.read.Identifier
    status: Literal['unavailable']

Label=Annotated[ResolvedLabel|UnavailableLabel,Field(discriminator='status')]

class DisplayBatch(audit.read.Closed):
    org_id: audit.read.Identifier
    labels: Annotated[list[Label],Field(min_length=1,max_length=MAX_ACTORS)]


def _pairs(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate')
        result[key]=value
    return result


def _constant(_):raise ValueError('constant')


@dataclass(frozen=True,repr=False)
class _Outcome:
    value: object=None
    error: Exception|None=None
    def __repr__(self):return '<_Outcome private>'


async def _outcome(operation):
    try:return _Outcome(value=await operation())
    except Exception as error:return _Outcome(error=error)


async def _owned(operation,deadline):
    """Never shield a raising task (including Python3.15 diagnostic callbacks)."""
    task=asyncio.create_task(_outcome(operation))
    try:
        result=await asyncio.shield(task)
    except asyncio.CancelledError:
        task.cancel()
        # A second abort interrupts cooperative cleanup at the absolute deadline.
        loop=asyncio.get_running_loop()
        abort=loop.call_later(max(0,deadline-time.monotonic()),task.cancel)
        try:
            while not task.done():
                try:await asyncio.shield(task)
                except asyncio.CancelledError:
                    if time.monotonic()>=deadline:task.cancel()
            if not task.cancelled():task.result()
        finally:abort.cancel()
        raise
    if result.error is not None:raise result.error from None
    return result.value


class IdentityDisplays:
    __slots__=('url','_key','_transport')
    def __repr__(self):return '<IdentityDisplays redacted>'
    def __init__(self,*,base_url,service_key,access_service_key,transport=None):
        try:
            if type(base_url) is not str or any(c.isspace() for c in base_url) or '?' in base_url or '#' in base_url:raise ValueError()
            parsed=urlsplit(base_url)
            if (parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password
                or parsed.query or parsed.fragment or parsed.path not in ('','/')
                or parsed.netloc.endswith(':') or parsed.port==0
                or type(service_key) is not str or not 32<=len(service_key)<=256
                or any(not 33<=ord(c)<=126 for c in service_key)
                or not isinstance(access_service_key,str)
                or hmac.compare_digest(service_key.encode('ascii'),access_service_key.encode('utf-8'))):
                raise ValueError()
        except Exception:raise RuntimeError('kdg_actor_display_configuration_invalid') from None
        self.url=base_url.rstrip('/')+'/v2/identity/actor-displays'
        self._key=service_key
        self._transport=transport

    async def lookup(self,org_id,actor_ids,budget):
        # The original Budget owns all phases. Reserving final authority is mandatory.
        remaining=budget.remaining()
        if remaining<=FINAL_SECONDS+FINAL_RESERVE:return None
        deadline=min(time.monotonic()+LOOKUP_SECONDS,budget.deadline-FINAL_SECONDS-FINAL_RESERVE)
        async def operation():
            request=json.dumps({'org_id':org_id,'actor_ids':list(actor_ids)},ensure_ascii=False,separators=(',',':')).encode('utf-8')
            if not 1<=len(actor_ids)<=MAX_ACTORS or list(actor_ids)!=sorted(set(actor_ids)) or len(request)>REQUEST_BYTES:raise ValueError('selection')
            async with httpx.AsyncClient(transport=self._transport,timeout=LOOKUP_SECONDS,follow_redirects=False,trust_env=False) as client:
                async with client.stream('POST',self.url,headers={'X-Service-Key':self._key,'Accept':'application/json','Accept-Encoding':'identity','Content-Type':'application/json'},content=request) as reply:
                    if (reply.headers.get('content-type','').split(';',1)[0].strip().lower()!='application/json'
                        or reply.headers.get('content-encoding','').strip().lower() not in ('','identity')):raise ValueError('headers')
                    cache=[part.strip().lower() for value in reply.headers.get_list('cache-control') for part in value.split(',')]
                    if 'private' not in cache or 'no-store' not in cache or any(part.split('=',1)[0] in ('public','s-maxage','max-age') for part in cache):raise ValueError('cache')
                    maximum=RESPONSE_BYTES if reply.status_code==200 else ERROR_BYTES
                    raw=bytearray()
                    async for chunk in reply.aiter_bytes():
                        if time.monotonic()>=deadline or len(raw)+len(chunk)>maximum:raise ValueError('body')
                        raw.extend(chunk)
                    if reply.status_code!=200:raise ValueError('upstream')
                    value=json.loads(raw.decode('utf-8'),object_pairs_hook=_pairs,parse_constant=_constant)
                    batch=DisplayBatch.model_validate(value)
                    if batch.org_id!=org_id or tuple(label.actor_id for label in batch.labels)!=tuple(actor_ids):raise ValueError('binding')
                    if time.monotonic()>=deadline:raise TimeoutError()
                    return batch.labels
        try:
            async with asyncio.timeout_at(deadline):
                async with asyncio.timeout_at(deadline-UNWIND_RESERVE):
                    result=await _owned(operation,deadline)
            budget.remaining()
            return result
        except Exception:
            # No exception text, upstream body, partial labels or service status escape.
            return None
