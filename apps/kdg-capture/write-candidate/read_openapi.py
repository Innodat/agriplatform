"""Owner metadata for the explicit own-detail boundary; offline export only."""
from copy import deepcopy
from fastapi.openapi.utils import get_openapi
from pydantic import TypeAdapter
from context import Identifier, positive_bigint_pattern


def schema_for(app,error_pairs):
    schema=get_openapi(title=app.title,version=app.version,routes=app.routes)
    models=schema['components']['schemas']
    uuid=TypeAdapter(Identifier).json_schema()
    uuid.update(pattern='^'+uuid['pattern'].removesuffix('$')+r'(?![\s\S])',minLength=36,maxLength=36)
    operation=schema['paths']['/api/v1/captures/{capture_id}']['get']
    operation.update(operationId='read_capture',description='Current own capture and its original immutable questionnaire. No query items or nonempty body. This read never confirms an uncertain write or grants future write authority.')
    operation['parameters']=[dict(name='capture_id',**{'in':'path'},required=True,schema=deepcopy(uuid))]
    schema['components']['securitySchemes']={'HTTPBearer':{'type':'http','scheme':'bearer'}}
    operation['security']=[{'HTTPBearer':[]}]
    for name,model in models.items():
        for field,prop in model.get('properties',{}).items():
            if field!='error_id' and (field.endswith('_id') or field in ('created_by','updated_by','id')):
                prop.update(deepcopy(uuid))
            if field in ('revision','questionnaire_version'):
                prop['pattern']=positive_bigint_pattern().removesuffix('$')+r'(?![\s\S])'
    detail=models['CaptureDetail']['properties']
    detail['observation_date'].update(format='date',pattern=r'^[0-9]{4}-[0-9]{2}-[0-9]{2}(?![\s\S])')
    detail['answers']['propertyNames']=deepcopy(uuid)
    for field in ('captured_at','created_at','updated_at'):
        detail[field].update(format='date-time',pattern=r'^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:[Zz]|\+00:00)(?![\s\S])')
    text={'type':'string','maxLength':5000,'pattern':r'^[^\u0000\ud800-\udfff]*(?![\s\S])'}
    # Match Python str.strip exactly across JSON Schema and ECMAScript consumers.
    nonblank=r'[^\u0009-\u000d\u001c-\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]'
    label=r'^(?=[\s\S]*'+nonblank+r')[^\u0000\ud800-\udfff]*(?![\s\S])'
    models['TextAnswer']['properties']['value'].update({**text,'pattern':label})
    models['BooleanAnswer']={'title':'BooleanAnswer','oneOf':[
        {'type':'object','additionalProperties':False,'required':['value'],'properties':{'value':{'type':'boolean','const':False}}},
        {'type':'object','additionalProperties':False,'required':['value'],'properties':{'value':{'type':'boolean','const':True},'details':deepcopy(text)}},
    ]}
    detail['child_label']['pattern']=label
    for name in ('RatingQuestion','BooleanQuestion','TextQuestion'):
        models[name]['properties']['label']['pattern']=label
    # Boolean detail configuration mirrors the validated original definition.
    boolean=models['BooleanQuestion']
    boolean['allOf']=[{'if':{'properties':{'details_enabled':{'const':True}}},'then':{'required':['details_label'],'properties':{'details_label':{'type':'string','minLength':1,'maxLength':500,'pattern':label}}},'else':{'properties':{'details_label':{'type':'null'}}}}]
    # Required canonical output includes optional-in-definition fields serialized by Pydantic.
    codes={status:sorted(code for candidate,code in error_pairs if candidate==status) for status,_ in error_pairs}
    for status,identifiers in sorted(codes.items()):
        name='ReadError'+str(status);model=deepcopy(models['ErrorEnvelope'])
        model.update(title=name,additionalProperties=False);model['properties']['error_id']['enum']=identifiers
        models[name]=model
        operation['responses'][str(status)]['content']['application/json']['schema']={'$ref':'#/components/schemas/'+name}
    del models['ErrorEnvelope']
    for response in operation['responses'].values():
        response.setdefault('headers',{})['Cache-Control']={'schema':{'type':'string','const':'private, no-store'}}
    operation['responses']['401']['headers']['WWW-Authenticate']={'schema':{'type':'string','const':'Bearer'}}
    return schema
