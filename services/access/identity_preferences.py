"""Restricted own-account language preferences; authentication precedes all locks."""
import asyncio
import hmac
import inspect
import json
import re
import time
from uuid import UUID
from typing import Literal
import psycopg
from fastapi import APIRouter,HTTPException,Request,Security
from fastapi.security import HTTPBearer,APIKeyHeader
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from studies_identity import AsyncDatabase

LIMIT=2048
REVISION=re.compile(r'0|[1-9][0-9]{0,18}')
HEADERS={'Cache-Control':'private, no-store','Vary':'Authorization, X-Service-Key'}
BEARER=HTTPBearer(auto_error=False,scheme_name='IdentityPreferenceBearer')
SERVICE=APIKeyHeader(name='X-Service-Key',auto_error=False,scheme_name='IdentityPreferenceServiceKey')
SECURITY=[{'IdentityPreferenceBearer':[],'IdentityPreferenceServiceKey':[]}]

class LanguagePreference(BaseModel):
    preferred_locale:Literal['en','pt']
    revision:str=Field(pattern=r'^(0|[1-9][0-9]{0,18})$')

class PreferenceErrorDetails(BaseModel):
    code:Literal['authentication_required','access_denied','identity.actor_setup_required',
        'identity.preference_revision_conflict','identity.preference_operation_conflict',
        'identity.preference_invalid','identity.preference_unavailable']

class PreferenceErrorResponse(BaseModel):
    detail:PreferenceErrorDetails

ERROR_RESPONSES={status:{'model':PreferenceErrorResponse} for status in (401,403,409,422,503)}

class PreferenceError(Exception):
    def __init__(self,status,code):self.status,self.code=status,code

def remaining(deadline):
    value=deadline-time.monotonic()
    if value<=0:raise PreferenceError(503,'identity.preference_unavailable')
    return value

def response(row):
    if (not isinstance(row,dict) or set(row)!={'preferred_locale','revision'}
            or row['preferred_locale'] not in ('en','pt')
            or type(row['revision']) is not int or not 0<=row['revision']<=9223372036854775807):
        raise PreferenceError(503,'identity.preference_unavailable')
    return {'preferred_locale':row['preferred_locale'],'revision':str(row['revision'])}

def parse(raw):
    def pairs(values):
        result={}
        for key,value in values:
            if key in result:raise ValueError()
            result[key]=value
        return result
    try:
        body=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs)
        if type(body) is not dict or set(body)!={'operation_id','expected_revision','preferred_locale'}:raise ValueError()
        if type(body['preferred_locale']) is not str or body['preferred_locale'] not in ('en','pt'):raise ValueError()
        revision=body['expected_revision']
        if type(revision) is not str or REVISION.fullmatch(revision) is None or int(revision)>9223372036854775807:raise ValueError()
        operation=body['operation_id']
        if type(operation) is not str or not UUID(operation).int or str(UUID(operation))!=operation.lower():raise ValueError()
        return {'operation':str(UUID(operation)),'expected':int(revision),'locale':body['preferred_locale']}
    except (ValueError,TypeError,KeyError,UnicodeError,RecursionError):
        raise PreferenceError(422,'identity.preference_invalid') from None

class PreferenceStore:
    def __init__(self,db):self.db=db
    async def execute(self,account,deadline,command=None):
        if self.db is None:raise PreferenceError(503,'identity.preference_unavailable')
        try:
            async with asyncio.timeout(remaining(deadline)):
                async with self.db.begin(deadline) as connection:
                    if command is None:await connection.execute(text('SET TRANSACTION READ ONLY'))
                    milliseconds=max(1,int(remaining(deadline)*1000))
                    await connection.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true),set_config('app.org_id','',true),set_config('app.actor_id','',true),set_config('statement_timeout',:statement,true),set_config('lock_timeout',:lock,true),set_config('idle_in_transaction_session_timeout',:idle,true)"),
                        {'account':str(account),'statement':str(min(2000,milliseconds)),'lock':str(min(1000,milliseconds)),'idle':str(milliseconds)})
                    statement='SELECT preferred_locale,revision FROM identity.read_account_language()' if command is None else 'SELECT preferred_locale,revision FROM identity.set_account_language(CAST(:operation AS uuid),CAST(:expected AS bigint),:locale)'
                    row=(await connection.execute(text(statement),command)).mappings().one_or_none()
                    value=response(row)
                    remaining(deadline)
                remaining(deadline)
                return value
        except PreferenceError:raise
        except (SQLAlchemyError,psycopg.Error,OSError,TimeoutError,ValueError,TypeError):
            # SQLSTATE only: never stringify driver errors containing SQL/parameters.
            import sys
            error=sys.exception();state=getattr(getattr(error,'orig',error),'sqlstate',None)
            states={'IP001':(409,'identity.preference_revision_conflict'),
                    'IP002':(409,'identity.preference_operation_conflict'),
                    'IP003':(409,'identity.actor_setup_required'),
                    'IP004':(422,'identity.preference_invalid'),
                    '42501':(403,'access_denied')}
            raise PreferenceError(*states.get(state,(503,'identity.preference_unavailable'))) from None

def configured_database(environment):
    url=environment.get('IDENTITY_PREFERENCES_DATABASE_URL')
    if not url:return None
    from sqlalchemy.engine import make_url
    try:
        parsed=make_url(url)
        if parsed.username!='identity_preferences_runtime' or parsed.drivername not in ('postgresql','postgresql+psycopg') or parsed.query:raise ValueError()
    except (SQLAlchemyError,TypeError,ValueError):
        raise RuntimeError('identity_preferences_configuration_invalid') from None
    return AsyncDatabase(url)

def router(db,authenticate,environment):
    routes=APIRouter();store=PreferenceStore(db)
    async def handle(request,write=False):
        deadline=time.monotonic()+3
        try:
            async with asyncio.timeout(remaining(deadline)):
                key=environment.get('IDENTITY_PREFERENCES_SERVICE_KEY','')
                supplied=request.headers.get('x-service-key','')
                if not key:raise PreferenceError(503,'identity.preference_unavailable')
                if not supplied or not hmac.compare_digest(key.encode(),supplied.encode()):raise PreferenceError(403,'access_denied')
                authorization=request.headers.get('authorization','')
                if not authorization.startswith('Bearer ') or not authorization[7:].strip():raise PreferenceError(401,'authentication_required')
                account=await authenticate(authorization) if inspect.iscoroutinefunction(authenticate) else await asyncio.to_thread(authenticate,authorization)
                if not isinstance(account,(UUID,str)) or not UUID(str(account)).int:raise PreferenceError(503,'identity.preference_unavailable')
                account=UUID(str(account))
                if request.query_params:raise PreferenceError(422,'identity.preference_invalid')
                command=None
                if write:
                    raw=bytearray()
                    async for chunk in request.stream():
                        if len(raw)+len(chunk)>LIMIT:raise PreferenceError(422,'identity.preference_invalid')
                        raw.extend(chunk)
                    command=parse(bytes(raw))
                value=await store.execute(account,deadline,command)
                return JSONResponse(value,headers=HEADERS)
        except PreferenceError as error:
            return JSONResponse({'detail':{'code':error.code}},status_code=error.status,headers=HEADERS)
        except HTTPException as error:
            status=error.status_code if error.status_code in (401,403) else 503
            code={401:'authentication_required',403:'access_denied'}.get(status,'identity.preference_unavailable')
            return JSONResponse({'detail':{'code':code}},status_code=status,headers=HEADERS)
        except (TimeoutError,ValueError,TypeError,OSError):
            return JSONResponse({'detail':{'code':'identity.preference_unavailable'}},status_code=503,headers=HEADERS)

    schema={'type':'object','additionalProperties':False,'required':['operation_id','expected_revision','preferred_locale'],'properties':{
        'operation_id':{'type':'string','format':'uuid'},'expected_revision':{'type':'string','pattern':'^(0|[1-9][0-9]{0,18})$'},'preferred_locale':{'type':'string','enum':['en','pt']}}}
    @routes.get('/v2/me/preferences/language',response_model=LanguagePreference,responses=ERROR_RESPONSES,openapi_extra={'security':SECURITY})
    async def read(request:Request,bearer=Security(BEARER),service=Security(SERVICE)):return await handle(request)
    @routes.put('/v2/me/preferences/language',response_model=LanguagePreference,responses=ERROR_RESPONSES,openapi_extra={'security':SECURITY,'requestBody':{'required':True,'content':{'application/json':{'schema':schema}}}})
    async def write(request:Request,bearer=Security(BEARER),service=Security(SERVICE)):return await handle(request,True)
    return routes
