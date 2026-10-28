"""Owner schema for the isolated audit display aggregate."""
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
    operation=schema['paths']['/api/v1/admin/captures/{capture_id}/audit-details']['get']
    operation.update(operationId='audit_details',security=[{'HTTPBearer':[]}],description='Current exact configured-organization read.all with verified account, durable actor, membership and matching organization resource scope before checkout. Returns the unchanged bounded audit page and a closed actor_display union. After the business transaction and connection are released, Identity receives only the sorted distinct owner, creator, modifier, included executor and non-null initiator IDs selected by that authorized page. Loaded labels preserve explicit per-ID unavailable results; invalid or unavailable Identity produces temporarily_unavailable for the entire label batch. A fresh final matching account/actor/membership/permission/organization-scope authorization is required before any aggregate publication, including label degradation. One original ten-second monotonic Budget covers input, read, lookup, final authority, owned unwind and serialization. Actual UTF8 limits: audit subtree64KiB, successful Identity input256KiB, error input1KiB and aggregate321KiB; no trimming, partial label batches or pagination changes. Numeric revision DESC keyset, default30/max100; closed canonical cursor binds account/org/capture/read.all/limit/last revision and supplies no authority. Current retained names are not event-time snapshots and grant no authority. No answers, definitions, receipts, account associations or offline observation. Unknown/duplicate query, nonempty body and browser service credentials refused. All responses private/no-store; no active mount or UI.')
    operation['parameters']=[dict(name='capture_id',**{'in':'path'},required=True,schema=deepcopy(uuid)),dict(name='limit',**{'in':'query'},required=False,schema=dict(type='integer',minimum=1,maximum=100,default=30)),dict(name='cursor',**{'in':'query'},required=False,schema=cursor)]
    schema['components']['securitySchemes']={'HTTPBearer':{'type':'http','scheme':'bearer'}}
    for status in sorted({status for status,_ in error_pairs}):
        name='AuditDisplayError'+str(status);model=deepcopy(models['ErrorEnvelope'])
        model.update(title=name,additionalProperties=False)
        model['properties']['error_id']['enum']=sorted(identifier for candidate,identifier in error_pairs if candidate==status)
        models[name]=model
        operation['responses'][str(status)]['content']['application/json']['schema']={'$ref':'#/components/schemas/'+name}
    del models['ErrorEnvelope']
    for response in operation['responses'].values():response.setdefault('headers',{})['Cache-Control']={'schema':{'type':'string','const':'private, no-store'}}
    operation['responses']['401']['headers']['WWW-Authenticate']={'schema':{'type':'string','const':'Bearer'}}
    return schema
