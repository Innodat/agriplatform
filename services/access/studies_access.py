"""Explicit account enrollment and canonical checks through bounded async owners."""
import asyncio
import logging
import secrets
import time
from datetime import datetime,timezone
from uuid import uuid4
from fastapi import APIRouter,Header,Request,Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader,HTTPBearer
from studies_contract import (AccountCheck,AccountDecision,AccountScope,EnrollmentAck,
    EnrollmentResult,Operation,StudiesError,decode,inline_schema)
from studies_identity import (StudiesFailure,account_uuid,bound_actor,evidence,live_account,
    prepare,remaining,transaction)

LOGGER=logging.getLogger('access.studies')
TOTAL_SECONDS=3.0

def error_response(status,error_id):
    return JSONResponse(StudiesError(error_id=error_id).model_dump(),status_code=status,
        headers={'Cache-Control':'private, no-store'})

class StudiesAccess:
    def __init__(self,db,identity_db,setup_db,environment,provider=None):
        self.db=db;self.identity_db=identity_db;self.setup_db=setup_db;self.environment=dict(environment)
        self.provider=provider;self.key=environment.get('SCRIBESWELL_SERVICE_KEY','')
        if self.key and (any(not 33<=ord(c)<=126 for c in self.key) or self.key in (
            environment.get('KDG_SERVICE_KEY'),environment.get('PTS_SERVICE_KEY'),environment.get('CONTENT_SERVICE_KEY'))):
            raise RuntimeError('studies_configuration_invalid')
    def matches(self,key):
        return bool(self.key and key and secrets.compare_digest(self.key.encode(),key.encode('utf-8')))
    async def handle(self,request,authorization,key,enroll=False):
        deadline=time.monotonic()+TOTAL_SECONDS
        trace_id=str(uuid4());operation_id=None
        def failed(status,error_id):
            if status==503:
                LOGGER.warning('studies_dependency_failed',extra={'trace_id':trace_id,
                    'operation_id':operation_id,'error_id':error_id})
            return error_response(status,error_id)
        try:
            if not self.matches(key):raise StudiesFailure(403,'service_access_denied')
            async with asyncio.timeout(remaining(deadline)):
                raw=bytearray()
                try:
                    async for chunk in request.stream():
                        raw.extend(chunk)
                        if len(raw)>4096:raise ValueError('body')
                    body=decode(raw,Operation if enroll else AccountCheck)
                except (ValueError,TypeError,RecursionError):raise StudiesFailure(422,'validation_failed') from None
                if enroll:operation_id=str(body.operation_id)
                if self.provider is None:account=await live_account(authorization,deadline,self.environment)
                else:account=account_uuid(await self.provider(authorization,deadline))
                actor=await evidence(self.identity_db,account,deadline)
                if actor is None:
                    if not enroll:raise StudiesFailure(503,'identity.setup_unavailable')
                    actor=await prepare(self.setup_db,account,body.operation_id,deadline)
                if enroll:
                    row=await transaction(self.db,account,deadline,
                        'SELECT disposition,account_id,actor_id FROM access.enroll_studies_account(:operation,:actor)',
                        {'operation':body.operation_id,'actor':actor},error_id='dependency_unavailable')
                else:
                    row=await transaction(self.db,account,deadline,
                        'SELECT account_id,actor_id FROM access.check_studies_permission(:actor)',
                        {'actor':actor},readonly=True)
                if row is None:raise StudiesFailure(403,'access_denied')
                if bound_actor(row,account)!=actor:raise StudiesFailure(503,'authorization_unavailable')
                if enroll:
                    try:result=EnrollmentResult(disposition=row['disposition'],account_id=account,actor_id=actor)
                    except (ValueError,KeyError,TypeError):raise StudiesFailure(503,'dependency_unavailable') from None
                    return EnrollmentAck(operation_id=body.operation_id,result=result)
                return AccountDecision(account_id=account,actor_id=actor,authorization_scope=AccountScope(kind='account'),decision_id=uuid4(),checked_at=datetime.now(timezone.utc))
        except StudiesFailure as failure:return failed(failure.status,failure.error_id)
        except TimeoutError:return failed(503,'authorization_unavailable')
        except Exception:
            # Private owner adapters never serialize dependency exceptions or request values.
            return failed(503,'dependency_unavailable')
    def router(self):
        routes=APIRouter()
        @routes.post('/v2/enrollments/scribeswell-studies',response_model=EnrollmentAck,
            dependencies=[Security(HTTPBearer(scheme_name='KdgBearer',auto_error=False)),
                Security(APIKeyHeader(name='X-Service-Key',scheme_name='KdgServiceKey',auto_error=False))],
            responses={status:{'model':StudiesError} for status in (401,403,422,503)})
        async def enroll(request:Request,authorization:str=Header(default=''),x_service_key:str=Header(default='')):
            return await self.handle(request,authorization,x_service_key,True)
        routes.routes[0].openapi_extra={'requestBody':{'required':True,'content':{'application/json':{'schema':inline_schema(Operation)}}}}
        return routes
