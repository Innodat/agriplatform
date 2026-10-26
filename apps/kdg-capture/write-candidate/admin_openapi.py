"""Owner schema for inert online organization reads; detail retains its owner DTO."""
from copy import deepcopy
from fastapi.openapi.utils import get_openapi
from read_openapi import schema_for as detail_schema
from read_http import _create_app as detail_app


def schema_for(app,error_pairs):
    detail=detail_schema(detail_app(None,None,None),error_pairs)
    schema=get_openapi(title=app.title,version=app.version,routes=app.routes)
    own=schema['components']['schemas']
    schema['components']=deepcopy(detail['components'])
    models=schema['components']['schemas']
    models['AdminHistoryPage']=deepcopy(own['AdminHistoryPage'])
    page=models['AdminHistoryPage']['properties']
    uuid=deepcopy(models['CaptureDetail']['properties']['org_id'])
    for field in ('org_id','account_id'):
        title=page[field].get('title');page[field].update(uuid);page[field]['title']=title
    for field in ('from_date','to_date'):
        page[field].update(format='date',pattern=r'^[0-9]{4}-[0-9]{2}-[0-9]{2}(?![\s\S])')
    cursor=dict(type='string',minLength=1,maxLength=2048,pattern=r'^[A-Za-z0-9_-]+(?![\s\S])')
    for branch in page['next_cursor']['anyOf']:
        if branch.get('type')=='string':branch.update(deepcopy(cursor))
    original=detail['paths']['/api/v1/captures/{capture_id}']['get']
    for path,operation_id in (('/api/v1/admin/captures','admin_history'),('/api/v1/admin/captures/{capture_id}','admin_detail')):
        operation=schema['paths'][path]['get']
        operation.update(operationId=operation_id,security=[{'HTTPBearer':[]}])
        for status,value in original['responses'].items():
            if status!='200':operation['responses'][status]=deepcopy(value)
        operation['responses']['200'].setdefault('headers',{})['Cache-Control']={'schema':{'type':'string','const':'private, no-store'}}
    operation=schema['paths']['/api/v1/admin/captures/{capture_id}']['get']
    operation['parameters']=deepcopy(original['parameters'])
    operation['description']='Current exact configured-organization read.all with verified account, durable actor, membership and organization resource scope before checkout. Preserves original owner, definition and provenance; no active-child or assignment requirement. No query selectors or nonempty body, offline observation, write acknowledgement or all-edit authority. Maximum actual UTF8 detail 512KiB.'
    operation=schema['paths']['/api/v1/admin/captures']['get']
    operation['parameters']=[dict(name=key,**{'in':'query'},required=True,schema=deepcopy(page[key])) for key in ('from_date','to_date')]+[
        dict(name='limit',**{'in':'query'},required=False,schema=dict(type='integer',minimum=1,maximum=100,default=30)),
        dict(name='cursor',**{'in':'query'},required=False,schema=deepcopy(cursor))]
    operation['description']='Online current organization history under exact read.all; rechecked every page. Inclusive explicit observation dates; default30/max100. Descending immutable (created_at,id) keyset; limit+1 rows, actual UTF8 page at most 2MiB and details at most512KiB. Closed canonical base64url JSON cursor binds verified account/org/read.all/dates/limit; untrusted navigation, no HMAC or authority. Own cursors incompatible; SQL independently enforces organization and dates. Byte-limited pages continue after last included row. No cross-page snapshot, deletion inference, offline observation, expiry, lease or edit authority. Unknown/duplicate query and nonempty body refused; all responses private/no-store.'
    return schema
