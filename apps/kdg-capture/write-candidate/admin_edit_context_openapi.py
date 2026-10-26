"""Owner schema for the closed current administrator edit-context read."""
from copy import deepcopy
from fastapi.openapi.utils import get_openapi
from read_openapi import schema_for as detail_schema
from read_http import _create_app as detail_app


def schema_for(app,error_pairs):
    detail=detail_schema(detail_app(None,None,None),error_pairs)
    schema=get_openapi(title=app.title,version=app.version,routes=app.routes)
    context=deepcopy(schema['components']['schemas']['AdminEditContext'])
    schema['components']=deepcopy(detail['components'])
    schema['components']['schemas']['AdminEditContext']=context
    operation=schema['paths']['/api/v1/admin/captures/{capture_id}/edit-context']['get']
    original=detail['paths']['/api/v1/captures/{capture_id}']['get']
    operation.update(operationId='admin_edit_context',parameters=deepcopy(original['parameters']),security=[{'HTTPBearer':[]}],description='Current fixed-organization read.all AND edit.all checked independently before checkout, with matching verified account, durable actor and membership. Original complete capture, revision, definition and immutable provenance; only observation_date and answers declared editable. Historical reads require no active child or assignment. No query or nonempty body, offline observations, expiry, write authority, commands or outcomes. One ten-second execution budget and one outer three-second Access pair deadline; first observation retains one-second SQL-entry freshness. Maximum actual UTF8 detail512KiB and whole context544KiB.')
    for status,value in original['responses'].items():
        if status!='200':operation['responses'][status]=deepcopy(value)
    operation['responses']['200'].setdefault('headers',{})['Cache-Control']={'schema':{'type':'string','const':'private, no-store'}}
    return schema
