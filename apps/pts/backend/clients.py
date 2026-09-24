import httpx
from fastapi import HTTPException

class AccessClient:
    def __init__(self, base_url, service_key):
        self.base_url=base_url.rstrip('/')
        self.key=service_key

    def verify(self, token, org, permission):
        if not token: raise HTTPException(401, {'code':'authentication_required'})
        try:
            response=httpx.post(self.base_url+'/v1/check',headers={'Authorization': token,'X-Service-Key':self.key},
                                json={'org_id':str(org),'permission':permission}, timeout=5)
            if response.status_code in (401,403):
                raise HTTPException(response.status_code, {'code':'authentication_required' if response.status_code==401 else 'access_denied'})
            response.raise_for_status()
            data=response.json()
            if data.get('org_id') != str(org) or not data.get('actor_id'): raise ValueError('invalid access response')
            return data
        except (httpx.HTTPError,ValueError,KeyError):
            raise HTTPException(503, {'code':'access_unavailable'}) from None

class ContentClient:
    def __init__(self, base_url, service_key):
        self.base_url=base_url.rstrip('/')
        self.key=service_key
    def read(self, content_id, org, token):
        try:
            response=httpx.post(self.base_url+f'/v1/objects/{content_id}/read',headers={'Authorization':token,'X-Service-Key':self.key,'X-Org-ID':str(org)},timeout=10)
            if response.status_code in (401,403,404): raise HTTPException(response.status_code, {'code':{401:'authentication_required',403:'document_denied',404:'document_missing'}[response.status_code]})
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError,ValueError): raise HTTPException(503, {'code':'document_unavailable'}) from None
