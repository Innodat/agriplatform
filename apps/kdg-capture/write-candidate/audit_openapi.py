"""Owner schema for the inert, closed audit metadata route."""
from copy import deepcopy
from fastapi.openapi.utils import get_openapi
from pydantic import TypeAdapter
from context import Identifier, positive_bigint_pattern


def schema_for(app,error_pairs):
    schema=get_openapi(title=app.title,version=app.version,routes=app.routes)
    models=schema['components']['schemas']
    uuid=TypeAdapter(Identifier).json_schema()
    uuid.update(pattern='^'+uuid['pattern'].removesuffix('$')+r'(?![\s\S])',minLength=36,maxLength=36)
    instant=dict(type='string',format='date-time',pattern=r'^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:[Zz]|\+00:00)(?![\s\S])')
    for model in models.values():
        for field,prop in model.get('properties',{}).items():
            if field!='error_id' and (field.endswith('_id') or field in ('created_by','updated_by')):
                branches=prop.get('anyOf',[prop])
                for branch in branches:
                    if branch.get('type')!='null':branch.update(deepcopy(uuid))
            if field in ('revision','current_revision'):prop['pattern']=positive_bigint_pattern().removesuffix('$')+r'(?![\s\S])'
            if field in ('created_at','updated_at','recorded_at'):prop.update(instant)
    cursor=dict(type='string',minLength=1,maxLength=2048,pattern=r'^[A-Za-z0-9_-]+(?![\s\S])')
    for branch in models['AuditPage']['properties']['next_cursor']['anyOf']:
        if branch.get('type')=='string':branch.update(cursor)
    operation=schema['paths']['/api/v1/admin/captures/{capture_id}/events']['get']
    operation.update(operationId='audit_events',security=[{'HTTPBearer':[]}],description='Current exact configured-organization read.all, verified account/durable actor/membership and exact organization resource scope before checkout; rechecked every page. Compact immutable create/changed-edit revision metadata only, without answers, definitions, receipts, outcome IDs or offline observation. Durable actor IDs are attribution rather than names or authority. Capture and revision stamps are independent statement times, not exact commit instants. One scoped SELECT with lateral limit+1, numeric revision DESC keyset, default30/max100, actual UTF8 <=64KiB. Closed canonical cursor binds account/org/capture/read.all/limit/last revision; navigation confers no authority. Refresh sees newer events; no cross-request snapshot promise. Empty continuation valid; first page without revision evidence unavailable. Unknown/duplicate query or nonempty body refused. All responses private/no-store; no activation or UI.')
    operation['parameters']=[dict(name='capture_id',**{'in':'path'},required=True,schema=deepcopy(uuid)),dict(name='limit',**{'in':'query'},required=False,schema=dict(type='integer',minimum=1,maximum=100,default=30)),dict(name='cursor',**{'in':'query'},required=False,schema=cursor)]
    schema['components']['securitySchemes']={'HTTPBearer':{'type':'http','scheme':'bearer'}}
    for status in sorted({status for status,_ in error_pairs}):
        name='AuditError'+str(status);model=deepcopy(models['ErrorEnvelope'])
        model.update(title=name,additionalProperties=False)
        model['properties']['error_id']['enum']=sorted(identifier for candidate,identifier in error_pairs if candidate==status)
        models[name]=model
        operation['responses'][str(status)]['content']['application/json']['schema']={'$ref':'#/components/schemas/'+name}
    del models['ErrorEnvelope']
    for response in operation['responses'].values():response.setdefault('headers',{})['Cache-Control']={'schema':{'type':'string','const':'private, no-store'}}
    operation['responses']['401']['headers']['WWW-Authenticate']={'schema':{'type':'string','const':'Bearer'}}
    return schema
