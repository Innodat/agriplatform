"""Owner schema for protected own-edit context, reusing original-detail metadata."""
from copy import deepcopy
from fastapi.openapi.utils import get_openapi
from read_openapi import schema_for as detail_schema
from own_observation_openapi import apply_observation_metadata


def schema_for(app,error_pairs):
    from read_http import _create_app
    detail=detail_schema(_create_app(None,None,None),error_pairs)
    schema=get_openapi(title=app.title,version=app.version,routes=app.routes)
    own=schema['components']['schemas']
    schema['components']=deepcopy(detail['components'])
    models=schema['components']['schemas']
    for name,value in own.items():
        if name not in models:models[name]=deepcopy(value)
    apply_observation_metadata(models)
    operation=schema['paths']['/api/v1/captures/{capture_id}/edit-context']['get']
    original=detail['paths']['/api/v1/captures/{capture_id}']['get']
    operation.update(operationId='read_edit_context',parameters=deepcopy(original['parameters']),security=[{'HTTPBearer':[]}],description='Current original-own CaptureDetail and exact independently verified own-read/own-edit observations; each expires checked_at plus seven days. Only observation_date and answers may be edited. Both current Access checks finish before checkout. No query/nonempty body, write acknowledgement, command or local-state effect. Maximum detail512KiB, complete UTF8 envelope544KiB; one ten-second execution budget.')
    for status,value in original['responses'].items():
        if status!='200':operation['responses'][status]=deepcopy(value)
    operation['responses']['200'].setdefault('headers',{})['Cache-Control']={'schema':{'type':'string','const':'private, no-store'}}
    return schema
