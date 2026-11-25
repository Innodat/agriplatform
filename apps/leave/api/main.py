"""Leave entry only: current session and authority on each protected request."""
import asyncio,os,re
from typing import Literal
from fastapi import FastAPI,Request,Security
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel,ValidationError
from contracts import Selection,Receipt,Unresolved,Language,SetLanguage,identifier,json_object
from leave_entry import Organizations,discover,cursor
from access_client import AccessClient,Failure
from repository import Repository
from transaction_context import Budget,WriteError
from safe_errors import install_safe_errors,ErrorEnvelope

class HealthResponse(BaseModel):
    status: Literal["ok"]
class Private:
    def __init__(self,app):self.app=app
    async def __call__(self,scope,receive,send):
        async def private_send(message):
            if message['type']=='http.response.start' and scope.get('path','').startswith('/v1/'):
                message={**message,'headers':[(k,v) for k,v in message.get('headers',[]) if k.lower()!=b'cache-control']+[(b'cache-control',b'private, no-store')]}
            await send(message)
        await self.app(scope,receive,private_send)

def create_app(repository=None,access=None,environment=None,*,people=None,configuration=None,clock=None,choices=None,drafts=None):
    env=dict(os.environ if environment is None else environment)
    app=FastAPI(title='Leave authorized entry',version='1.0.0',docs_url=None,redoc_url=None,openapi_url=None,servers=[{'url':'/api'}])
    app.add_middleware(Private);install_safe_errors(app)
    from datetime import datetime,timezone
    from draft_choices import Choices,ChoicesRepository,decode_cursor
    from draft_context import Context,prepare
    from drafts import DraftRepository,DraftReady,ExtendedContext,Start,Save,Discard,Outcome,StartOutcome,SaveOutcome,DiscardOutcome,validation_details,DraftRead,DraftFailure,DraftErrorEnvelope,require_ready,v4,EditorRead,EditorActive,EditorClosed
    from people_client import PeopleClient
    from work_timezone import ConfigurationRepository
    clock=clock or (lambda:datetime.now(timezone.utc))
    try:
        if access is None and any(env.get(k) for k in ('LEAVE_ACCESS_ORIGIN','LEAVE_SERVICE_KEY','LEAVE_CURRENT_SESSION_SERVICE_KEY','LEAVE_PREFERENCES_SERVICE_KEY')):
            access=AccessClient(*(env[k] for k in ('LEAVE_ACCESS_ORIGIN','LEAVE_SERVICE_KEY','LEAVE_CURRENT_SESSION_SERVICE_KEY','LEAVE_PREFERENCES_SERVICE_KEY')))
        if repository is None and env.get('LEAVE_DATABASE_URL'):repository=Repository(env['LEAVE_DATABASE_URL'])
        if drafts is None and env.get('LEAVE_DATABASE_URL'):drafts=DraftRepository(env['LEAVE_DATABASE_URL'])
        if choices is None and env.get('LEAVE_DATABASE_URL'):choices=ChoicesRepository(env['LEAVE_DATABASE_URL'])
        if configuration is None and env.get('LEAVE_DATABASE_URL'):configuration=ConfigurationRepository(env['LEAVE_DATABASE_URL'])
        if people is None and any(env.get(k) for k in ('LEAVE_PEOPLE_ORIGIN','LEAVE_PEOPLE_SERVICE_KEY')):people=PeopleClient(env['LEAVE_PEOPLE_ORIGIN'],env['LEAVE_PEOPLE_SERVICE_KEY'])
    except Exception:raise RuntimeError('leave_configuration_invalid') from None
    def error(status,name):return JSONResponse({'error_id':name,'error':'Request could not be completed','details':{}},status_code=status)
    async def perform(request,kind,org_id=None,operation_id=None):
        budget=Budget()
        try:
            authorization=request.headers.get('authorization','')
            if len(request.headers.getlist('authorization'))!=1 or not re.fullmatch(r'Bearer [^\s\x00-\x1f\x7f]+',authorization):raise Failure(401,'authentication_required')
            if access is None:raise Failure(503,'authorization_unavailable')
            org=identifier(org_id) if org_id else None
            operation=identifier(operation_id) if operation_id else None
            if kind=='organizations':
                fields={}
                for key,value in request.query_params.multi_items():
                    if key!='cursor' or key in fields:raise ValueError()
                    fields[key]=cursor(value)
                await access.session(authorization,budget)
                return await discover(access,authorization,fields.get('cursor'))
            if request.query_params:raise ValueError()
            command=None
            if kind in ('select','language-write'):
                raw=bytearray()
                async with asyncio.timeout(min(3,budget.remaining())):
                    async for chunk in request.stream():
                        raw.extend(chunk)
                        if len(raw)>4096:raise ValueError()
                command=(Selection if kind=='select' else SetLanguage).model_validate(json_object(raw))
            if kind.startswith('language'):return await access.language(authorization,budget,command.model_dump() if command else None)
            context=await access.authorize(authorization,org,budget)
            if repository is None:raise WriteError('operation_verification_unavailable')
            result=await repository.run(kind,context,budget,operation or command.operation_id)
            if result is None:return JSONResponse(Unresolved(operation_id=operation).model_dump(),status_code=202)
            return Receipt.model_validate(result)
        except Failure as failure:return error(failure.status,failure.error_id)
        except (ValueError,TypeError,UnicodeError,RecursionError):return error(422,'validation_failed')
        except (WriteError,TimeoutError):return error(503,'outcome_unresolved' if kind=='select' else 'operation_verification_unavailable')
        except Exception:return error(503,'authorization_unavailable')
    errors={s:{'model':ErrorEnvelope} for s in (401,403,409,422,503)}
    bearer=[Security(HTTPBearer(scheme_name='LeaveBearer',auto_error=False))]
    @app.get('/v1/organizations/{org_id}/draft-choices',response_model=Choices,dependencies=bearer,responses=errors)
    async def draft_choices(org_id:str,request:Request):
        budget=Budget()
        try:
            async with asyncio.timeout_at(budget.deadline):
                authorization=request.headers.get('authorization','')
                if len(request.headers.getlist('authorization'))!=1 or not re.fullmatch(r'Bearer [^\s\x00-\x1f\x7f]+',authorization):raise Failure(401,'authentication_required')
                org=identifier(org_id);fields={}
                for key,value in request.query_params.multi_items():
                    if key not in ('cursor','selected_type_id') or key in fields:raise ValueError()
                    fields[key]=decode_cursor(value,org) if key=='cursor' else identifier(value)
                if access is None:raise Failure(503,'authorization_unavailable')
                context=await access.own_read(authorization,org,budget)
                if choices is None:raise Failure(503,'dependency_unavailable')
                result=await choices.choices(context,org,fields.get('selected_type_id'),fields.get('cursor'),budget)
                try:response=JSONResponse(Choices.model_validate(result).model_dump(mode='json'))
                except Exception:raise Failure(503,'dependency_unavailable') from None
                budget.remaining();return response
        except Failure as failure:return error(503 if failure.error_id=='service_access_denied' else failure.status,'dependency_unavailable' if failure.error_id=='service_access_denied' else failure.error_id)
        except (ValueError,TypeError,UnicodeError,RecursionError):return error(422,'validation_failed')
        except Exception:return error(503,'dependency_unavailable')
    @app.get('/v1/organizations/{org_id}/me/draft-context',response_model=Context|ExtendedContext,dependencies=bearer,responses=errors,openapi_extra={'parameters':[{'name':'draft_context_version','in':'query','required':False,'schema':{'type':'string','enum':['1']},'description':'Omit for the legacy strict preparation response; version1 adds the current draft summary.'}]})
    async def draft_context(org_id:str,request:Request):
        budget=Budget()
        try:
            async with asyncio.timeout_at(budget.deadline):
                authorization=request.headers.get('authorization','')
                if len(request.headers.getlist('authorization'))!=1 or not re.fullmatch(r'Bearer [^\s\x00-\x1f\x7f]+',authorization):raise Failure(401,'authentication_required')
                org=identifier(org_id)
                extended=bool(request.query_params)
                if extended and list(request.query_params.multi_items())!=[('draft_context_version','1')]:raise ValueError()
                if access is None:raise Failure(503,'authorization_unavailable')
                prepared=await prepare(access,people,configuration,authorization,org,budget,clock,retain=True)
                result=prepared.public
                if extended and result.status=='ready':
                    if drafts is None:raise Failure(503,'dependency_unavailable')
                    result=DraftReady(**result.model_dump(),**await drafts.snapshot(prepared,budget))
                response=JSONResponse(result.model_dump(mode='json'));budget.remaining()
                return response
        except Failure as failure:return error(503 if failure.error_id=='service_access_denied' else failure.status,'dependency_unavailable' if failure.error_id=='service_access_denied' else failure.error_id)
        except (ValueError,TypeError,UnicodeError,RecursionError):return error(422,'validation_failed')
        except Exception:return error(503,'dependency_unavailable')
    async def draft_action(request,org_id,kind,target=None):
        budget=Budget()
        try:
            async with asyncio.timeout_at(budget.deadline):
                authorization=request.headers.get('authorization','')
                if len(request.headers.getlist('authorization'))!=1 or not re.fullmatch(r'Bearer [^\s\x00-\x1f\x7f]+',authorization):raise Failure(401,'authentication_required')
                org=identifier(org_id)
                if request.query_params:raise ValueError()
                if target is not None:target=v4(target)
                command=None
                models={'start':Start,'save':Save,'discard':Discard}
                if kind in models:
                    raw=bytearray()
                    async for chunk in request.stream():
                        if len(raw)+len(chunk)>32768:raise DraftFailure(413,'request_too_large',{'max_bytes':32768})
                        raw.extend(chunk)
                    try:decoded=json_object(raw)
                    except (ValueError,TypeError,UnicodeError,RecursionError):raise DraftFailure(422,'validation_failed',{'fields':[{'path':'$','rule':'invalid_json'}]}) from None
                    try:command=models[kind].model_validate(decoded)
                    except ValidationError as failure:raise DraftFailure(422,'validation_failed',validation_details(failure)) from None
                if access is None:raise Failure(503,'authorization_unavailable')
                if drafts is None:raise Failure(503,'dependency_unavailable')
                while True:
                    prepared=await prepare(access,people,configuration,authorization,org,budget,clock,retain=True)
                    require_ready(prepared)
                    try:
                        if kind=='start':result=await drafts.start(prepared,budget,command,configuration,clock)
                        elif kind=='save':result=await drafts.save(prepared,budget,target,command,configuration,clock)
                        elif kind=='discard':result=await drafts.discard(prepared,budget,target,command,configuration,clock)
                        elif kind=='read':result=await drafts.read(prepared,budget,target)
                        else:result=await drafts.lookup(prepared,budget,target)
                        break
                    except DraftFailure as failure:
                        if failure.error_id!='leave.draft_preparation_changed':raise
                        budget.remaining()
                response=JSONResponse(result.model_dump(mode='json'));budget.remaining();return response
        except DraftFailure as failure:return JSONResponse({'error_id':failure.error_id,'error':'Request could not be completed','details':failure.details},status_code=failure.status)
        except Failure as failure:return error(503 if failure.error_id=='service_access_denied' else failure.status,'dependency_unavailable' if failure.error_id=='service_access_denied' else failure.error_id)
        except (ValueError,TypeError,UnicodeError,RecursionError):return error(422,'validation_failed')
        except Exception:return error(503,'outcome_unresolved' if kind in ('start','save','discard') else 'operation_verification_unavailable')
    draft_errors={s:{'model':DraftErrorEnvelope} for s in (401,403,404,409,413,422,503)}
    @app.get('/v1/organizations/{org_id}/drafts/{draft_id}/editor',response_model=EditorRead,dependencies=bearer,responses=draft_errors)
    async def open_editor(org_id:str,draft_id:str,request:Request):
        budget=Budget()
        try:
            async with asyncio.timeout_at(budget.deadline):
                authorization=request.headers.get('authorization','')
                if len(request.headers.getlist('authorization'))!=1 or not re.fullmatch(r'Bearer [^\s\x00-\x1f\x7f]+',authorization):raise Failure(401,'authentication_required')
                org=identifier(org_id);target=v4(draft_id)
                if request.query_params:raise ValueError()
                if access is None:raise Failure(503,'authorization_unavailable')
                if drafts is None:raise Failure(503,'dependency_unavailable')
                prepared=await prepare(access,people,configuration,authorization,org,budget,clock,retain=True)
                public=require_ready(prepared)
                draft,summary=await drafts.editor(prepared,budget,target)
                context=DraftReady(**public.model_dump(),**summary)
                if draft.state=='discarded':result=EditorClosed(context=context,draft=draft)
                else:
                    if choices is None:raise Failure(503,'dependency_unavailable')
                    # This owner-local snapshot completes before the next query begins;
                    # no cross-owner/cross-transaction atomicity is claimed.
                    catalogue=await choices.choices(prepared.authority,org,draft.input.leave_type_id,None,budget)
                    result=EditorActive(context=context,draft=draft,choices=catalogue)
                response=JSONResponse(result.model_dump(mode='json'));budget.remaining();return response
        except DraftFailure as failure:return JSONResponse({'error_id':failure.error_id,'error':'Request could not be completed','details':failure.details},status_code=failure.status)
        except Failure as failure:return error(503 if failure.error_id=='service_access_denied' else failure.status,'dependency_unavailable' if failure.error_id=='service_access_denied' else failure.error_id)
        except ValidationError:return error(503,'dependency_unavailable')
        except (ValueError,TypeError,UnicodeError,RecursionError):return error(422,'validation_failed')
        except Exception:return error(503,'operation_verification_unavailable')
    @app.post('/v1/organizations/{org_id}/me/draft/start',response_model=StartOutcome,dependencies=bearer,responses=draft_errors,openapi_extra={'requestBody':{'required':True,'content':{'application/json':{'schema':Start.model_json_schema()}}}})
    async def start_draft(org_id:str,request:Request):return await draft_action(request,org_id,'start')
    @app.put('/v1/organizations/{org_id}/drafts/{draft_id}/input',response_model=SaveOutcome,dependencies=bearer,responses=draft_errors,openapi_extra={'requestBody':{'required':True,'content':{'application/json':{'schema':Save.model_json_schema(ref_template='#/components/schemas/{model}')}}}})
    async def save_draft(org_id:str,draft_id:str,request:Request):return await draft_action(request,org_id,'save',draft_id)
    @app.post('/v1/organizations/{org_id}/drafts/{draft_id}/discard',response_model=DiscardOutcome,dependencies=bearer,responses=draft_errors,openapi_extra={'requestBody':{'required':True,'content':{'application/json':{'schema':Discard.model_json_schema()}}}})
    async def discard_draft(org_id:str,draft_id:str,request:Request):return await draft_action(request,org_id,'discard',draft_id)
    @app.get('/v1/organizations/{org_id}/drafts/{draft_id}',response_model=DraftRead,dependencies=bearer,responses=draft_errors)
    async def read_draft(org_id:str,draft_id:str,request:Request):return await draft_action(request,org_id,'read',draft_id)
    @app.get('/v1/organizations/{org_id}/operations/{operation_id}',response_model=Outcome,dependencies=bearer,responses=draft_errors)
    async def draft_outcome(org_id:str,operation_id:str,request:Request):return await draft_action(request,org_id,'lookup',operation_id)
    @app.get('/health',operation_id='health',response_model=HealthResponse,responses={s:{'model':ErrorEnvelope} for s in (422,500,503)})
    async def health():return HealthResponse(status='ok')
    @app.get('/v1/me/organizations',response_model=Organizations,dependencies=bearer,responses=errors)
    async def organizations(request:Request):return await perform(request,'organizations')
    @app.post('/v1/organizations/{org_id}/context/selection',response_model=Receipt,dependencies=bearer,responses=errors,openapi_extra={'requestBody':{'required':True,'content':{'application/json':{'schema':Selection.model_json_schema()}}}})
    async def select(org_id:str,request:Request):return await perform(request,'select',org_id)
    @app.get('/v1/organizations/{org_id}/context/operations/{operation_id}',response_model=Receipt,dependencies=bearer,responses={202:{'model':Unresolved},**errors})
    async def lookup(org_id:str,operation_id:str,request:Request):return await perform(request,'lookup',org_id,operation_id)
    @app.get('/v1/me/preferences/language',response_model=Language,dependencies=bearer,responses=errors)
    async def language(request:Request):return await perform(request,'language-read')
    @app.put('/v1/me/preferences/language',response_model=Language,dependencies=bearer,responses=errors,openapi_extra={'requestBody':{'required':True,'content':{'application/json':{'schema':SetLanguage.model_json_schema()}}}})
    async def set_language(request:Request):return await perform(request,'language-write')
    return app
app=create_app()
