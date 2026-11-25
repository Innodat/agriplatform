"""Current-session, fixed organization entry, discovery and Identity preferences over HTTP."""
import asyncio,re,time
from dataclasses import dataclass
from datetime import datetime,timezone
from typing import Literal
import httpx

# Trust configuration is captured at process start; requests/credentials remain fresh.
_VERIFIED_TLS_CONTEXT = httpx.create_ssl_context(verify=True, trust_env=False)
from pydantic import field_validator
from contracts import Closed,identifier,json_object,Language
from outbound_http import OwnerDependency
from transaction_context import VerifiedContext

class Failure(Exception):
    def __init__(self,status,error_id):self.status=status;self.error_id=error_id

class Scope(Closed):
    kind:Literal['organization']
    org_id:str
    @field_validator('org_id')
    @classmethod
    def id(cls,value):return identifier(value)
class Decision(Closed):
    account_id:str
    actor_id:str
    permission:Literal['leave.request.own.read']
    authorization_scope:Scope
    resource_scope:Scope
    membership_id:str
    decision_id:str
    checked_at:str
    @field_validator('account_id','actor_id','decision_id')
    @classmethod
    def ids(cls,value):return identifier(value)
    @field_validator('membership_id')
    @classmethod
    def member(cls,value):
        if not value.isascii() or not value.isdigit() or value.startswith('0') or not 0<int(value)<=9223372036854775807:raise ValueError('membership')
        return value
    @field_validator('checked_at')
    @classmethod
    def utc(cls,value):
        stamp=datetime.fromisoformat(value.replace('Z','+00:00'))
        if stamp.tzinfo is None or stamp.utcoffset()!=timezone.utc.utcoffset(stamp):raise ValueError('timestamp')
        return value
@dataclass(frozen=True,repr=False)
class EntryContext:
    decision:Decision
    local:VerifiedContext

class AccessClient:
    def __init__(self,origin,key,session_key,preference_key,*,transport=None):
        self.config=OwnerDependency(origin,key,3);self.transport=transport
        self.session_key=OwnerDependency(origin,session_key,3).credential
        self.preference_key=OwnerDependency(origin,preference_key,3).credential
    async def request(self,method,path,authorization,budget,*,key=None,body=None,params=None):
        timeout=min(3,budget.remaining())
        try:
            async with asyncio.timeout(timeout):
                async with httpx.AsyncClient(base_url=self.config.origin,timeout=timeout,trust_env=False,follow_redirects=False,transport=self.transport,verify=_VERIFIED_TLS_CONTEXT) as client:
                    async with client.stream(method,path,json=body if body is not None else None,params=params,headers={'Authorization':authorization,'X-Service-Key':key or self.config.credential,'Accept-Encoding':'identity'}) as response:
                        if response.headers.get('content-encoding','identity').lower()!='identity':raise ValueError()
                        raw=bytearray()
                        async for chunk in response.aiter_bytes(chunk_size=65536):
                            raw.extend(chunk)
                            if len(raw)>65536:raise ValueError()
                        value=json_object(raw)
                        if response.status_code!=200:
                            name=value.get('error_id') if set(value)=={'error_id','error','details'} and type(value['error']) is str and value['details']=={} else value.get('detail',{}).get('code') if set(value)=={'detail'} and type(value['detail']) is dict and set(value['detail'])=={'code'} else None
                            allowed={401:{'authentication_required'},403:{'access_denied','service_access_denied','identity.verification_required'},409:{'identity.actor_setup_required','identity.person_link_required','identity.preference_revision_conflict','identity.preference_operation_conflict'},422:{'validation_failed','identity.preference_invalid'},503:{'authorization_unavailable','identity.current_session_unavailable','identity.preference_unavailable'}}
                            if name not in allowed.get(response.status_code,set()):raise ValueError()
                            raise Failure(response.status_code,name)
                        return value
        except Failure:raise
        except Exception:raise Failure(503,'authorization_unavailable') from None
    async def session(self,authorization,budget):
        value=await self.request('POST','/v2/identity/current-session',authorization,budget,key=self.session_key)
        try:
            if set(value)!={'account_id','session_id','credential_expires_at','observed_at'}:raise ValueError()
            account=identifier(value['account_id']);identifier(value['session_id'])
            expiry=datetime.fromisoformat(value['credential_expires_at'].replace('Z','+00:00'));observed=datetime.fromisoformat(value['observed_at'].replace('Z','+00:00'))
            if any(stamp.tzinfo is None or stamp.utcoffset()!=timezone.utc.utcoffset(stamp) for stamp in (expiry,observed)) or expiry<=datetime.now(timezone.utc):raise ValueError()
            return account
        except Exception:raise Failure(503,'authorization_unavailable') from None
    async def authorize(self,authorization,org,budget):
        account=await self.session(authorization,budget)
        try:
            decision=Decision.model_validate(await self.request('POST','/v2/organizations/entry',authorization,budget,body={'org_id':org}))
            if decision.account_id!=account or decision.authorization_scope.org_id!=org or decision.resource_scope.org_id!=org:raise ValueError()
            return EntryContext(decision,VerifiedContext(org,account,decision.actor_id,'all_write',time.monotonic()))
        except Failure:raise
        except Exception:raise Failure(503,'authorization_unavailable') from None
    async def own_check(self,authorization,org,budget,account,permission):
        try:
            d=OwnDecision.model_validate(await self.request('POST','/v2/check',authorization,budget,body={'permission':permission,'authorization_scope':{'kind':'organization','org_id':org}}))
            d.require_scope(account, org, permission)
            return d
        except Failure:raise
        except Exception:raise Failure(503,'authorization_unavailable') from None
    async def own_read(self,authorization,org,budget):
        account=await self.session(authorization,budget)
        return OwnContext(await self.own_check(authorization,org,budget,account,'leave.request.own.read'),False)
    async def own(self,authorization,org,budget):
        account = await self.session(authorization, budget)
        try:
            decisions = OwnDecisions.model_validate(await self.request(
                'POST', '/v2/organizations/leave-own-context', authorization, budget, body={'org_id': org},
            ))
            read, manage = decisions.read, decisions.manage
            read.require_scope(account, org, 'leave.request.own.read')
            if manage is not None:
                manage.require_scope(account, org, 'leave.request.own.manage')
                if manage.decision_id == read.decision_id:
                    raise ValueError('decision_id')
                if (manage.actor_id, manage.person_id, manage.membership_id) != (
                    read.actor_id, read.person_id, read.membership_id
                ):
                    raise ValueError('decision_binding')
            return OwnContext(read, manage is not None, manage)
        except Failure:
            raise
        except Exception:
            raise Failure(503, 'authorization_unavailable') from None
    async def language(self,authorization,budget,command=None):
        await self.session(authorization,budget)
        try:return Language.model_validate(await self.request('PUT' if command else 'GET','/v2/me/preferences/language',authorization,budget,key=self.preference_key,body=command))
        except Failure:raise
        except Exception:raise Failure(503,'identity.preference_unavailable') from None


class OwnScope(Closed):
    kind:Literal['own']
    person_id:str
    @field_validator('person_id')
    @classmethod
    def id(cls,value):return identifier(value)
class OwnDecision(Decision):
    permission:Literal['leave.request.own.read','leave.request.own.manage']
    person_id:str
    resource_scope:OwnScope
    @field_validator('person_id')
    @classmethod
    def person(cls,value):return identifier(value)

    def require_scope(self, account, org, permission):
        if (self.account_id != account or self.authorization_scope.org_id != org
            or self.permission != permission or self.resource_scope.person_id != self.person_id):
            raise ValueError('decision_scope')


class OwnDecisions(Closed):
    read: OwnDecision
    manage: OwnDecision | None

    @field_validator('read', 'manage')
    @classmethod
    def require_wire_timestamp(cls, decision: OwnDecision | None) -> OwnDecision | None:
        if decision is not None and not re.fullmatch(
            r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|\+00:00)',
            decision.checked_at,
        ):
            raise ValueError('timestamp')
        return decision


@dataclass(frozen=True,repr=False)
class OwnContext:
    decision:OwnDecision
    manage:bool
    manage_decision:OwnDecision|None=None

