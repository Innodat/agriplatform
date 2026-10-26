"""OpenAPI metadata for the explicitly constructed candidate create route.

Runtime keeps strict streaming/parsing order; schema describes validated JSON values.
Duplicate keys, UTF-8 byte limits and single headers remain boundary requirements.
"""
from copy import deepcopy

from fastapi.openapi.utils import get_openapi
from pydantic import TypeAdapter
from context import Identifier, positive_bigint_pattern
from capture_commands import CreateCommand


def schema_for(app,error_pairs):
    schema=get_openapi(title=app.title,version=app.version,routes=app.routes)
    models=schema.setdefault('components',{}).setdefault('schemas',{})
    uuid=TypeAdapter(Identifier).json_schema()
    uuid.update(pattern='^'+uuid['pattern'].removesuffix('$')+r'(?![\s\S])',minLength=36,maxLength=36)
    revision={'type':'string','pattern':positive_bigint_pattern().removesuffix('$')+r'(?![\s\S])'}
    command=CreateCommand.model_json_schema(ref_template='#/components/schemas/{model}')
    models.update(command.pop('$defs',{}))
    command['properties']['operation_id'].update(deepcopy(uuid))
    command['properties']['command_version']['const']=1
    for field in ('capture_id','child_id','questionnaire_version_id'):
        command['properties'][field].update(deepcopy(uuid))
    command['properties']['observation_date'].update(format='date',pattern=r'^[0-9]{4}-[0-9]{2}-[0-9]{2}(?![\s\S])')
    command['properties']['answers']['propertyNames']=deepcopy(uuid)
    command['properties']['captured_at'].update(format='date-time',pattern=r'^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:[Zz]|\+00:00)(?![\s\S])')
    command['properties']['child_eligibility_ref'].update(minLength=1,pattern=r'^(?=[\s\S]*\S)[^\u0000\ud800-\udfff]*(?![\s\S])')
    # Explicit Boolean branches retain the runtime details rule in generated
    # TypeScript as well as JSON Schema (if/then is not a type-level constraint).
    text={'type':'string','maxLength':5000,'pattern':r'^[^\u0000\ud800-\udfff]*(?![\s\S])'}
    models['TextAnswer']['properties']['value'].update(deepcopy(text))
    models['BooleanAnswer']={'title':'BooleanAnswer','oneOf':[
        {'type':'object','additionalProperties':False,'required':['value'],
         'properties':{'value':{'type':'boolean','const':False}}},
        {'type':'object','additionalProperties':False,'required':['value'],
         'properties':{'value':{'type':'boolean','const':True},'details':deepcopy(text)}},
    ]}
    models['CreateCommand']=command
    operation=schema['paths']['/api/v1/captures']['post']
    operation.update(operationId='create_capture',description=(
        'Candidate create. Requires current create-all or assigned capability. '
        'Exactly one Bearer header and application/json Content-Type, no query items; '
        'strict JSON body bounded to 131072 UTF-8 bytes. Stored target authorizes replay.'))
    operation['parameters']=[]
    operation['requestBody']={'required':True,'content':{'application/json':{'schema':{'$ref':'#/components/schemas/CreateCommand'}}}}
    schema['components']['securitySchemes']={'HTTPBearer':{'type':'http','scheme':'bearer'}}
    operation['security']=[{'HTTPBearer':[]}]
    for model,field in (('CaptureReceipt','operation_id'),('CaptureResult','capture_id')):
        models[model]['properties'][field].update(deepcopy(uuid))
    models['CaptureReceipt']['properties']['command_version']['const']=1
    models['CaptureReceipt']['properties']['command_type']={'type':'string','const':'capture.create'}
    models['CaptureResult']['properties']['revision'].update(revision)
    base=deepcopy(models['ErrorEnvelope']);base['additionalProperties']=False
    for status in sorted({status for status,_ in error_pairs}):
        variants=[];mapping={}
        for index,code in enumerate(sorted(code for s,code in error_pairs if s==status)):
            name='CreateError'+str(status)+'Variant'+str(index)
            error=deepcopy(base);error['title']=name
            error['properties']['error_id']={'type':'string','const':code}
            models[name]=error
            ref='#/components/schemas/'+name
            variants.append({'$ref':ref});mapping[code]=ref
        name='CreateError'+str(status)
        models[name]={'oneOf':variants,'discriminator':{'propertyName':'error_id','mapping':mapping}}
        operation['responses'][str(status)]['content']['application/json']['schema']={'$ref':'#/components/schemas/'+name}
    for response in operation['responses'].values():
        response.setdefault('headers',{})['Cache-Control']={'schema':{'type':'string','const':'private, no-store'}}
    operation['responses']['401']['headers']['WWW-Authenticate']={'schema':{'type':'string','const':'Bearer'}}
    return schema
