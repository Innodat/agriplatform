import httpx
from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException

class AccessClient:
    def __init__(self, base_url, service_key):
        self.base_url=base_url.rstrip('/')
        self.key=service_key

    def verify(self, token, permission):
        if not token: raise HTTPException(401, {'code':'authentication_required'})
        try:
            response=httpx.post(self.base_url+'/v2/check',headers={'Authorization': token,'X-Service-Key':self.key},
                                json={'authorization_scope':{'kind':'account'},'permission':permission}, timeout=5)
            if response.status_code in (401,403):
                raise HTTPException(response.status_code, {'code':'authentication_required' if response.status_code==401 else 'access_denied'})
            response.raise_for_status()
            data=response.json()
            if set(data)!={'account_id','actor_id','permission','authorization_scope','decision_id','checked_at'}:raise ValueError()
            for field in ('account_id','actor_id','decision_id'):
                if not isinstance(data[field],str) or str(UUID(data[field]))!=data[field] or not UUID(data[field]).int:raise ValueError()
            if data['permission']!=permission or data['authorization_scope']!={'kind':'account'}:raise ValueError()
            if not isinstance(data['checked_at'],str) or datetime.fromisoformat(data['checked_at'].replace('Z','+00:00')).tzinfo is None:raise ValueError()
            return data
        except (httpx.HTTPError,ValueError,KeyError,TypeError):
            raise HTTPException(503, {'code':'access_unavailable'}) from None

class CurrentSessionClient:
    """Identity is the only provider-session owner; no positive result is cached."""
    def __init__(self,base_url,service_key,transport=None):
        self.base_url=base_url.rstrip('/');self.key=service_key;self.transport=transport

    async def _post(self,authorization,path):
        import asyncio
        if not isinstance(authorization,str) or not authorization.startswith('Bearer '):raise HTTPException(401,{'code':'authentication_required'})
        try:
            async with asyncio.timeout(2):
                async with httpx.AsyncClient(transport=self.transport,trust_env=False,timeout=2,follow_redirects=False) as client:
                    response=await client.post(self.base_url+path,headers={'Authorization':authorization,'X-Service-Key':self.key})
                    if response.status_code in (401,403):raise HTTPException(response.status_code,{'code':'authentication_required' if response.status_code==401 else 'access_denied'})
                    response.raise_for_status();return response.json()
        except (httpx.HTTPError,ValueError,TypeError,TimeoutError):raise HTTPException(503,{'code':'identity.current_session_unavailable'}) from None

    async def _session(self,authorization,path):
        try:
            data=await self._post(authorization,path)
            if set(data)!={'account_id','session_id','credential_expires_at','observed_at'}:raise ValueError()
            for field in ('account_id','session_id'):
                if not isinstance(data[field],str) or str(UUID(data[field]))!=data[field] or not UUID(data[field]).int:raise ValueError()
            if any(not isinstance(data[field],str) for field in ('credential_expires_at','observed_at')):raise ValueError()
            expires=datetime.fromisoformat(data['credential_expires_at'].replace('Z','+00:00'))
            observed=datetime.fromisoformat(data['observed_at'].replace('Z','+00:00'))
            if expires.tzinfo is None or observed.tzinfo is None or expires<=datetime.now(timezone.utc):raise ValueError()
            return {**data,'expires_at':expires}
        except (httpx.HTTPError,ValueError,KeyError,TypeError,TimeoutError):raise HTTPException(503,{'code':'identity.current_session_unavailable'}) from None

    async def verify(self,authorization):return await self._session(authorization,'/v2/identity/current-session')
    async def prepare_cleanup(self,authorization):return await self._session(authorization,'/v2/identity/file-cleanup/prepare')

    async def cleanup(self,authorization):
        try:
            data=await self._post(authorization,'/v2/identity/file-cleanup/check')
            if set(data)!={'account_id','session_id','provider_session','observed_at'}:raise ValueError()
            for field in ('account_id','session_id'):
                if not isinstance(data[field],str) or str(UUID(data[field]))!=data[field] or not UUID(data[field]).int:raise ValueError()
            if data['provider_session'] not in ('present','absent') or not isinstance(data['observed_at'],str):raise ValueError()
            if datetime.fromisoformat(data['observed_at'].replace('Z','+00:00')).tzinfo is None:raise ValueError()
            return data
        except (httpx.HTTPError,ValueError,KeyError,TypeError,TimeoutError):raise HTTPException(503,{'code':'identity.current_session_unavailable'}) from None

# The HTTP adapter is application-owned; it never imports Content's server modules.
from .private_stream import ContentClient
