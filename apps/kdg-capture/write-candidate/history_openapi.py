"""History owner schema built on existing original-detail schema owner."""
from copy import deepcopy
from fastapi.openapi.utils import get_openapi
from read_openapi import schema_for as detail_schema
from own_observation_openapi import apply_observation_metadata


def schema_for(app,error_pairs):
    from read_http import _create_app
    # Offline construction does not create engines or authority collaborators.
    detail=detail_schema(_create_app(None,None,None),error_pairs)
    schema=get_openapi(title=app.title,version=app.version,routes=app.routes)
    schema['components']=deepcopy(detail['components'])
    own=get_openapi(title=app.title,version=app.version,routes=app.routes)['components']['schemas']
    for name,value in own.items():
        if name not in schema['components']['schemas']:schema['components']['schemas'][name]=deepcopy(value)
    history=own['HistoryPage']
    uuid=apply_observation_metadata(schema['components']['schemas'])
    for key in ('org_id','account_id'):history['properties'][key].update(uuid)
    for key in ('from_date','to_date'):history['properties'][key].update(format='date',pattern=r'^[0-9]{4}-[0-9]{2}-[0-9]{2}(?![\s\S])')
    cursor_schema=dict(type='string',minLength=1,maxLength=2048,pattern=r'^[A-Za-z0-9_-]+(?![\s\S])')
    for branch in history['properties']['next_cursor']['anyOf']:
        if branch.get('type')=='string':branch.update(deepcopy(cursor_schema))
    schema['components']['schemas']['HistoryPage']=history
    operation=schema['paths']['/api/v1/captures']['get']
    operation.update(operationId='history_captures',security=[{'HTTPBearer':[]}],description='Current original-owner history with inclusive explicit observation dates, descending immutable (created_at,id) keyset position. Bounded canonical base64url JSON cursor binds current org/account/own-read/date/limit; untrusted navigation, neither signature nor authority. Every query independently constrains scope and dates. Includes the exact verified own-read observation, expiring seven days after its checked_at. No snapshot, deletion evidence or write acknowledgement; no create/edit authority. Unknown/duplicate query and nonempty body refused. Maximum UTF8 page 2MiB; each original-definition detail 512KiB. Caller pins dates across pages.')
    operation['parameters']=[
        dict(name=key,**{'in':'query'},required=True,schema=deepcopy(history['properties'][key])) for key in ('from_date','to_date')]+[
        dict(name='limit',**{'in':'query'},required=False,schema=dict(type='integer',minimum=1,maximum=100,default=30)),
        dict(name='cursor',**{'in':'query'},required=False,schema=deepcopy(cursor_schema))]
    detail_op=detail['paths']['/api/v1/captures/{capture_id}']['get']
    for status,value in detail_op['responses'].items():
        if status!='200':operation['responses'][status]=deepcopy(value)
    operation['responses']['200'].setdefault('headers',{})['Cache-Control']={'schema':{'type':'string','const':'private, no-store'}}
    return schema
