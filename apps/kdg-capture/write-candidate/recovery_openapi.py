"""Documentation metadata for the manually validated candidate recovery route.

Build from FastAPI/Pydantic output; retain runtime validation and its ordering.
TypeScript UUID/revision aliases remain strings, not runtime validation promises.
"""
from copy import deepcopy

from fastapi.openapi.utils import get_openapi
from pydantic import TypeAdapter
from context import Identifier, positive_bigint_pattern
from operation_outcomes import Command


def schema_for(app, error_pairs):
    schema=get_openapi(title=app.title,version=app.version,routes=app.routes)
    models=schema['components']['schemas']
    uuid=TypeAdapter(Identifier).json_schema()
    # JSON Schema patterns search; use an anchored, strict end assertion (also
    # portable to ECMAScript) rather than $'s before-final-newline position.
    uuid['pattern']='^'+uuid['pattern'].removesuffix('$')+r'(?![\s\S])'
    uuid.update(minLength=36,maxLength=36)
    operation=schema['paths']['/api/v1/operations/{operation_id}']['get']
    operation.update(operationId='recover_operation',
        description='Current own-read recovery. Exactly one command_type query item and one Bearer header; unknown or duplicate query items and nonempty bodies are refused. Unresolved is verified absence, not proof that an executing save cannot commit later.')
    operation['parameters']=[
        {'name':'operation_id','in':'path','required':True,'schema':deepcopy(uuid)},
        {'name':'command_type','in':'query','required':True,'schema':TypeAdapter(Command).json_schema(),
         'description':'Exactly one value; unknown and duplicate query items are rejected.'},
    ]
    schema['components']['securitySchemes']={'HTTPBearer':{'type':'http','scheme':'bearer'}}
    operation['security']=[{'HTTPBearer':[]}]
    for model,field in (('CaptureReceipt','operation_id'),('CaptureResult','capture_id'),('Unresolved','operation_id')):
        models[model]['properties'][field].update(deepcopy(uuid))
    version=models['CaptureReceipt']['properties']['command_version']
    if version.get('minimum')==version.get('maximum'):
        version['const']=version['minimum']
    models['CaptureResult']['properties']['revision']['pattern']=positive_bigint_pattern().removesuffix('$')+r'(?![\s\S])'
    # FastAPI serializes defaults on this output; internal defaulting stays intact.
    models['Unresolved']['required']=sorted(set(models['Unresolved']['required'])|{'status'})
    codes={status:sorted(code for candidate,code in error_pairs if candidate==status)
           for status,_ in error_pairs}
    for status,identifiers in sorted(codes.items()):
        name='RecoveryError'+str(status)
        model=deepcopy(models['ErrorEnvelope'])
        model.update(title=name,additionalProperties=False)
        model['properties']['error_id']['enum']=identifiers
        models[name]=model
        operation['responses'][str(status)]['content']['application/json']['schema']={'$ref':'#/components/schemas/'+name}
    del models['ErrorEnvelope']
    for response in operation['responses'].values():
        response.setdefault('headers',{})['Cache-Control']={'schema':{'type':'string','const':'private, no-store'}}
    operation['responses']['401']['headers']['WWW-Authenticate']={'schema':{'type':'string','const':'Bearer'}}
    return schema
