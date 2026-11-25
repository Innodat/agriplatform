"""Leave-owned bounded People HTTP adapter; no shared server imports."""
import asyncio,re
from datetime import date,datetime,timezone
import httpx

# Trust configuration is captured at process start; requests/credentials remain fresh.
_VERIFIED_TLS_CONTEXT = httpx.create_ssl_context(verify=True, trust_env=False)
from contracts import identifier,json_object
from access_client import Failure
from outbound_http import OwnerDependency

def utc(value):
    if type(value) is not str:raise ValueError()
    stamp=datetime.fromisoformat(value.replace('Z','+00:00'))
    if stamp.tzinfo is None or stamp.utcoffset()!=timezone.utc.utcoffset(stamp):raise ValueError()
    return stamp
def day(value):
    if type(value) is not str or re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}',value) is None:raise ValueError()
    return date.fromisoformat(value)
def validate(value,org,person,employment=None,as_of=None):
    status=value.get('status');common={'status','org_id','person_id','observed_at'}
    if status=='not_found':keys=common
    elif status=='found' and as_of is None:keys=common|{'employment_id','revision','has_periods'}
    elif status=='effective' and as_of is not None:keys=common|{'employment_id','revision','as_of_date','employment_state','period'}
    else:raise ValueError()
    if set(value)!=keys or value['org_id']!=org or value['person_id']!=person:raise ValueError()
    identifier(value['org_id']);identifier(value['person_id']);utc(value['observed_at'])
    if status=='not_found':
        if employment is not None:raise ValueError()
        return value
    identifier(value['employment_id']);revision=value['revision']
    if type(revision) is not str or re.fullmatch(r'[1-9][0-9]{0,18}',revision) is None or int(revision)>9223372036854775807:raise ValueError()
    if employment is not None and value['employment_id']!=employment:raise ValueError()
    if status=='found':
        if type(value['has_periods']) is not bool:raise ValueError()
    else:
        if value['as_of_date']!=as_of:raise ValueError()
        actual=day(value['as_of_date']);state=value['employment_state'];period=value['period']
        if state=='setup_required':
            if period is not None:raise ValueError()
        else:
            if state not in ('current','future','ended') or type(period) is not dict or set(period)!={'period_id','start_date','end_date'}:raise ValueError()
            identifier(period['period_id']);start=day(period['start_date']);end=day(period['end_date']) if period['end_date'] is not None else None
            if end is not None and end<start:raise ValueError()
            if state=='current' and not(start<=actual and (end is None or actual<=end)):raise ValueError()
            if state=='future' and not actual<start:raise ValueError()
            if state=='ended' and not(end is not None and end<actual):raise ValueError()
    return value

class PeopleClient:
    def __init__(self,origin,key,*,transport=None):self.config=OwnerDependency(origin,key,3);self.transport=transport
    async def read(self,authorization,org,person,budget,employment=None,as_of=None):
        timeout=min(3,budget.remaining())
        try:
            async with asyncio.timeout(timeout):
                async with httpx.AsyncClient(base_url=self.config.origin,timeout=timeout,trust_env=False,follow_redirects=False,transport=self.transport,verify=_VERIFIED_TLS_CONTEXT) as client:
                    async with client.stream('GET',f'/v1/organizations/{org}/employment/me',params={'as_of_date':as_of} if as_of else None,headers={'Authorization':authorization,'X-Service-Key':self.config.credential,'Accept-Encoding':'identity'}) as response:
                        if response.headers.get('content-encoding','identity').lower()!='identity':raise ValueError()
                        raw=bytearray()
                        async for chunk in response.aiter_bytes(chunk_size=65536):
                            raw.extend(chunk)
                            if len(raw)>65536:raise ValueError()
                        value=json_object(raw)
                        if response.status_code!=200:
                            name=value.get('error_id');allowed={401:{'authentication_required'},403:{'access_denied','identity.verification_required'},409:{'identity.actor_setup_required','identity.person_link_required'},503:{'authorization_unavailable','dependency_unavailable'}}
                            if set(value)!={'error_id','error','details'} or type(value['error']) is not str or value['details']!={} or name not in allowed.get(response.status_code,set()):raise ValueError()
                            raise Failure(response.status_code,name)
                        return validate(value,org,person,employment,as_of)
        except Failure:raise
        except Exception:raise Failure(503,'dependency_unavailable') from None
