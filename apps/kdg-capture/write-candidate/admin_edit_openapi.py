"""OpenAPI metadata for the explicitly constructed candidate own-edit route.

Runtime keeps strict streaming/parsing order; schema describes validated JSON values.
Duplicate keys, UTF-8 byte limits and single headers remain boundary requirements.
"""
from copy import deepcopy

from fastapi.openapi.utils import get_openapi
from pydantic import TypeAdapter
from context import Identifier, positive_bigint_pattern
from capture_commands import EditCommand

CONFLICT='kdg_capture.capture_revision_conflict'


def schema_for(app,error_pairs):
    schema=get_openapi(title=app.title,version=app.version,routes=app.routes)
    models=schema.setdefault('components',{}).setdefault('schemas',{})
    uuid=TypeAdapter(Identifier).json_schema()
    uuid.update(pattern='^'+uuid['pattern'].removesuffix('$')+r'(?![\s\S])',minLength=36,maxLength=36)
    revision={'type':'string','pattern':positive_bigint_pattern().removesuffix('$')+r'(?![\s\S])'}
    command=EditCommand.model_json_schema(ref_template='#/components/schemas/{model}')
    models.update(command.pop('$defs',{}))
    command['properties']['operation_id'].update(deepcopy(uuid))
    command['properties']['command_version']['const']=1
    command['properties']['expected_revision'].update(revision)
    command['properties']['observation_date'].update(format='date',pattern=r'^[0-9]{4}-[0-9]{2}-[0-9]{2}(?![\s\S])')
    command['properties']['answers']['propertyNames']=deepcopy(uuid)
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
    models['EditCommand']=command
    operation=schema['paths']['/api/v1/admin/captures/{capture_id}']['put']
    operation.update(operationId='admin_edit_capture',description=(
        'Candidate administrator edit. Requires current organization read.all then edit.all capability. '
        'Exactly one Bearer header and one application/json Content-Type (parameters allowed), no query items and a bounded JSON body (131072 UTF-8 bytes); '
        'duplicate JSON keys are rejected. Current stored-target authority precedes replay. '
        'The original committed receipt may identify a different target than the incoming path.'))
    operation['parameters']=[{'name':'capture_id','in':'path','required':True,'schema':deepcopy(uuid)}]
    operation['requestBody']={'required':True,'content':{'application/json':{'schema':{'$ref':'#/components/schemas/EditCommand'}}}}
    schema['components']['securitySchemes']={'HTTPBearer':{'type':'http','scheme':'bearer'}}
    operation['security']=[{'HTTPBearer':[]}]
    for model,field in (('CaptureReceipt','operation_id'),('CaptureResult','capture_id')):
        models[model]['properties'][field].update(deepcopy(uuid))
    models['CaptureReceipt']['properties']['command_version']['const']=1
    models['CaptureReceipt']['properties']['command_type']={'type':'string','const':'capture.edit'}
    models['CaptureResult']['properties']['revision'].update(revision)
    base=deepcopy(models['ErrorEnvelope']);base['additionalProperties']=False
    for status in sorted({status for status,_ in error_pairs}):
        variants=[];mapping={}
        for index,code in enumerate(sorted(code for s,code in error_pairs if s==status)):
            name='EditError'+str(status)+'Variant'+str(index)
            error=deepcopy(base);error['title']=name
            error['properties']['error_id']={'type':'string','const':code}
            if code==CONFLICT:
                error['properties']['current_revision']=deepcopy(revision)
                error['required']=sorted(set(error['required'])|{'current_revision'})
            models[name]=error
            ref='#/components/schemas/'+name
            variants.append({'$ref':ref});mapping[code]=ref
        name='EditError'+str(status)
        models[name]={'oneOf':variants,'discriminator':{'propertyName':'error_id','mapping':mapping}}
        operation['responses'][str(status)]['content']['application/json']['schema']={'$ref':'#/components/schemas/'+name}
    for response in operation['responses'].values():
        response.setdefault('headers',{})['Cache-Control']={'schema':{'type':'string','const':'private, no-store'}}
    operation['responses']['401']['headers']['WWW-Authenticate']={'schema':{'type':'string','const':'Bearer'}}
    recovery=schema['paths']['/api/v1/admin/operations/{operation_id}']['get']
    recovery.update(operationId='admin_recover_edit',description=(
        'Current organization read.all only; never executes an edit. Exactly one capture.edit command_type query item, '
        'one Bearer header and an empty body. Executor-private original receipt; unresolved is verified absence, '
        'not proof that in-flight work cannot later commit. Stored-target authority precedes disclosure.'))
    recovery['parameters']=[
        {'name':'operation_id','in':'path','required':True,'schema':deepcopy(uuid)},
        {'name':'command_type','in':'query','required':True,'schema':{'type':'string','const':'capture.edit'}},
    ]
    recovery['security']=[{'HTTPBearer':[]}]
    models['Unresolved']['properties']['operation_id'].update(deepcopy(uuid))
    models['Unresolved']['properties']['command_type']={'type':'string','const':'capture.edit'}
    models['Unresolved']['required']=sorted(set(models['Unresolved']['required'])|{'status'})
    recovery_pairs={pair for pair in error_pairs if pair[0] not in (404,) and pair[1] not in (
        'questionnaire_version_unavailable',CONFLICT,'operation_busy','unsupported_command_version')}
    for status in sorted({status for status,_ in recovery_pairs}):
        name='AdminRecoveryError'+str(status)
        error=deepcopy(base);error.update(title=name,additionalProperties=False)
        error['properties']['error_id']={'type':'string','enum':sorted(code for s,code in recovery_pairs if s==status)}
        models[name]=error
        recovery['responses'][str(status)]['content']['application/json']['schema']={'$ref':'#/components/schemas/'+name}
    for response in recovery['responses'].values():
        response.setdefault('headers',{})['Cache-Control']={'schema':{'type':'string','const':'private, no-store'}}
    recovery['responses']['401']['headers']['WWW-Authenticate']={'schema':{'type':'string','const':'Bearer'}}
    return schema
