"""Current canonical capability checks and People-only identity observations."""
import asyncio
import logging
import time
from datetime import datetime,timezone
from uuid import uuid4
from fastapi import APIRouter,Request,Header,Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader,HTTPBearer
from capability_contract import (CapabilityCheck,ContextInput,CapabilityAccountDecision,OwnDecision,
    CapabilityOrganizationDecision,OrganizationContext,CapabilityError,decode)
from caller_policy import CallerPolicy
from identity_context import current,bind
from studies_identity import StudiesFailure,account_uuid,live_account
from studies_contract import inline_schema
LOGGER=logging.getLogger('access.capabilities')
PROVIDER_SECONDS=2.0
EXECUTION_SECONDS=5.0

class CapabilityAccess:
    def __init__(self,db,environment,provider=None):
        self.db=db;self.environment=dict(environment);self.provider=provider;self.policy=CallerPolicy(environment)
    def matches(self,key):return self.policy.caller(key) is not None
    async def handle(self,request,authorization,key,context=False):
        trace=str(uuid4())
        try:
            caller=self.policy.caller(key)
            if caller is None or (context and caller.name!='people') or (not context and caller.name in ('people','directory')):
                raise StudiesFailure(403,'service_access_denied')
            if len(request.headers.getlist('x-service-key'))!=1 or len(request.headers.getlist('authorization'))>1:
                raise StudiesFailure(403,'service_access_denied')
            try:body=await decode(request,ContextInput if context else CapabilityCheck)
            except (ValueError,TypeError,UnicodeError,RecursionError,TimeoutError):raise StudiesFailure(422,'validation_failed') from None
            if not context:
                scope=self.policy.scope(caller,body.permission)
                if scope is None:raise StudiesFailure(403,'service_access_denied')
                if scope!=body.authorization_scope.kind:raise StudiesFailure(422,'validation_failed')
            deadline=time.monotonic()+EXECUTION_SECONDS
            async with asyncio.timeout(EXECUTION_SECONDS):
                if not authorization.startswith('Bearer ') or not authorization[7:].strip():
                    raise StudiesFailure(401,'authentication_required')
                # Provider wait is separately bounded and precedes all SQL transactions.
                async with asyncio.timeout(PROVIDER_SECONDS):
                    account=await live_account(authorization,deadline,self.environment) if self.provider is None else account_uuid(await self.provider(authorization,deadline))
                org=body.org_id if context else getattr(body.authorization_scope,'org_id',None)
                function='access.current_organization_context' if context else 'access.check_organization_capability' if org else 'access.check_account_capability'
                row=await current(self.db,account,org,deadline,function,None if context else body.permission)
                actor,member,person=bind(row,account,org)
                if actor is None:raise StudiesFailure(409,'identity.actor_setup_required')
                common=dict(account_id=account,actor_id=actor,checked_at=datetime.now(timezone.utc))
                if context:return OrganizationContext(**common,org_id=org,membership_id=member,person_id=person,observation_id=uuid4())
                common.update(permission=body.permission,authorization_scope=body.authorization_scope,decision_id=uuid4())
                if not org:return CapabilityAccountDecision(**common)
                if caller.name=='leave':
                    if person is None:raise StudiesFailure(409,'identity.person_link_required')
                    return OwnDecision(**common,membership_id=member,person_id=person,resource_scope={'kind':'own','person_id':person})
                return CapabilityOrganizationDecision(**common,membership_id=member,resource_scope=body.authorization_scope)
        except StudiesFailure as failure:return self.error(failure.status,failure.error_id,trace)
        except Exception:return self.error(503,'authorization_unavailable',trace)
    def error(self,status,error_id,trace):
        if status==503:LOGGER.warning('capability_dependency_failed',extra={'trace_id':trace,'error_id':error_id})
        return JSONResponse(CapabilityError(error_id=error_id).model_dump(),status_code=status,headers={'Cache-Control':'private, no-store'})
    def router(self):
        routes=APIRouter()
        @routes.post('/v2/identity/organization-context',response_model=OrganizationContext,
            dependencies=[Security(HTTPBearer(scheme_name='KdgBearer',auto_error=False)),Security(APIKeyHeader(name='X-Service-Key',scheme_name='KdgServiceKey',auto_error=False))],
            responses={status:{'model':CapabilityError} for status in (401,403,409,422,503)})
        async def context(request:Request,authorization:str=Header(default=''),x_service_key:str=Header(default='')):
            return await self.handle(request,authorization,x_service_key,True)
        routes.routes[0].openapi_extra={'requestBody':{'required':True,'content':{'application/json':{'schema':inline_schema(ContextInput)}}}}
        return routes
