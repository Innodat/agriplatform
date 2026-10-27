"""Private caller-scoped organization and entry-application discovery."""
import asyncio
import logging
import re
import time
from datetime import datetime,timezone
from uuid import uuid4
from fastapi import APIRouter,Request,Header,Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader,HTTPBearer
from caller_policy import CallerPolicy
from discovery_contract import (ApplicationsDiscovery,OrganizationsDiscovery,DiscoveryError,
    DiscoveryOrganization,DiscoveryApplication,CATALOGUE_LIMIT,APP_PATTERN,query,cursor_encode)
from discovery_query import read
from studies_identity import StudiesFailure,account_uuid,live_account

LOGGER=logging.getLogger('access.discovery')
EXECUTION_SECONDS=3.0
PROVIDER_SECONDS=2.0

def organizations(rows,after,size):
    if len(rows)>size+1:raise ValueError('rows')
    result=[];previous=after.int if after else 0
    for row in rows:
        if set(row)!={'org_id','org_name','membership_id'}:raise ValueError('row')
        org=account_uuid(row['org_id']);member=row['membership_id'];name=row['org_name']
        if org.int<=previous or type(member) is not int or not 0<member<=9223372036854775807 or not isinstance(name,str):raise ValueError('row')
        previous=org.int
        result.append(DiscoveryOrganization(org_id=org,name=name,membership_id=str(member)))
    return OrganizationsDiscovery(organizations=result[:size],next_cursor=cursor_encode(result[size-1].org_id) if len(result)>size else None)

def applications(rows):
    if len(rows)>CATALOGUE_LIMIT:raise ValueError('catalogue')
    result=[];previous=''
    for row in rows:
        if set(row)!={'app_id','eligible_scope_kinds'}:raise ValueError('row')
        app=row['app_id'];scopes=row['eligible_scope_kinds']
        if not isinstance(app,str) or not re.fullmatch(APP_PATTERN,app) or app<=previous or type(scopes) is not list:raise ValueError('row')
        result.append(DiscoveryApplication(app_id=app,eligible_scope_kinds=scopes));previous=app
    return ApplicationsDiscovery(applications=result,checked_at=datetime.now(timezone.utc))

class Discovery:
    def __init__(self,db,environment,provider=None):
        self.db=db;self.environment=dict(environment);self.provider=provider;self.policy=CallerPolicy(environment)
    async def handle(self,request,authorization,key,apps=False):
        trace=str(uuid4())
        try:
            caller=self.policy.caller(key)
            if caller is None or (apps and caller.name!='directory') or (not apps and caller.name not in ('leave','reference')):raise StudiesFailure(403,'service_access_denied')
            if len(request.headers.getlist('x-service-key'))!=1 or len(request.headers.getlist('authorization'))>1:raise StudiesFailure(403,'service_access_denied')
            try:app,after,size=query(request,apps)
            except (ValueError,TypeError,UnicodeError):raise StudiesFailure(422,'validation_failed') from None
            if not apps and app!=caller.name:raise StudiesFailure(403,'service_access_denied')
            deadline=time.monotonic()+EXECUTION_SECONDS
            async with asyncio.timeout(EXECUTION_SECONDS):
                if not authorization.startswith('Bearer ') or not authorization[7:].strip():raise StudiesFailure(401,'authentication_required')
                async with asyncio.timeout(min(PROVIDER_SECONDS,EXECUTION_SECONDS)):
                    try:account=await live_account(authorization,deadline,self.environment) if self.provider is None else account_uuid(await self.provider(authorization,deadline))
                    except StudiesFailure as error:
                        if error.error_id=='identity.verification_required':raise StudiesFailure(403,'access_denied') from None
                        raise
                    except (ValueError,TypeError,KeyError):raise StudiesFailure(503,'authorization_unavailable') from None
                rows=await read(self.db,account,deadline,app,after,size)
                try:return applications(rows) if apps else organizations(rows,after,size)
                except (ValueError,TypeError,KeyError):raise StudiesFailure(503,'authorization_unavailable') from None
        except StudiesFailure as error:return self.error(error.status,error.error_id,trace)
        except (TimeoutError,OSError):return self.error(503,'authorization_unavailable',trace)
        except Exception:return self.error(500,'internal_error',trace)
    def error(self,status,error_id,trace):
        if status>=500:LOGGER.warning('discovery_failed',extra={'trace_id':trace,'error_id':error_id})
        return JSONResponse(DiscoveryError(error_id=error_id).model_dump(),status_code=status,headers={'Cache-Control':'private, no-store'})
    def router(self):
        router=APIRouter()
        options=dict(dependencies=[Security(HTTPBearer(scheme_name='KdgBearer',auto_error=False)),Security(APIKeyHeader(name='X-Service-Key',scheme_name='KdgServiceKey',auto_error=False))],responses={s:{'model':DiscoveryError} for s in (401,403,422,500,503)})
        @router.get('/v2/organizations',response_model=OrganizationsDiscovery,openapi_extra={'parameters':[
            {'name':'application','in':'query','required':True,'schema':{'type':'string','enum':['leave','reference']}},
            {'name':'cursor','in':'query','required':False,'schema':{'type':'string','pattern':'^[A-Za-z0-9_-]{48}$','maxLength':48}},
            {'name':'page_size','in':'query','required':False,'schema':{'type':'integer','minimum':1,'maximum':100,'default':100}},
        ]},**options)
        async def discover_organizations(request:Request,authorization:str=Header(default=''),x_service_key:str=Header(default='')):
            return await self.handle(request,authorization,x_service_key)
        @router.get('/v2/applications',response_model=ApplicationsDiscovery,**options)
        async def discover_applications(request:Request,authorization:str=Header(default=''),x_service_key:str=Header(default='')):
            return await self.handle(request,authorization,x_service_key,True)
        return router
