"""Owner schema for candidate setup; offline export does not install a route."""
from copy import deepcopy
from fastapi.openapi.utils import get_openapi
from read_openapi import schema_for as detail_schema
from context import positive_bigint_pattern
from own_observation_openapi import UTC_Z_PATTERN

def schema_for(app,error_pairs):
    from read_http import _create_app
    detail=detail_schema(_create_app(None,None,None),error_pairs)
    schema=get_openapi(title=app.title,version=app.version,routes=app.routes)
    models=schema['components']['schemas']
    reference=detail['components']['schemas']
    for name in ('RatingQuestion','BooleanQuestion','TextQuestion','QuestionnaireDefinition'):
        models[name]=deepcopy(reference[name])
    uuid=deepcopy(reference['CaptureDetail']['properties']['org_id']);uuid.pop('title',None)
    for name,model in models.items():
        for field,prop in model.get('properties',{}).items():
            if field.endswith('_id') and field not in ('membership_id','error_id'):prop.update(deepcopy(uuid))
            if field in ('membership_id','child_revision','assignment_revision','questionnaire_version'):
                prop.update(pattern=positive_bigint_pattern().removesuffix('$')+r'(?![\s\S])')
            if field in ('checked_at','expires_at'):prop.update(format='date-time',pattern=UTC_Z_PATTERN)
    models['Child']['properties']['child_label']['pattern']=reference['CaptureDetail']['properties']['child_label']['pattern']
    models['Child']['properties']['child_eligibility_ref']['pattern']=r'^[A-Za-z0-9_-]{43}(?![\s\S])'
    operation=schema['paths']['/api/v1/provision']['get']
    operation.update(operationId='provision_setup',security=[{'HTTPBearer':[]}],description='Selector-free current setup. Four independent current Access checks precede checkout. Positive slots retain exact decisions and seven-day observations; no grant is inferred from another. One original ten-second budget includes checkout, worker drain, commit, release and final serialization. Complete response <=1MiB and <=1000 children, no truncation. Opaque newly committed eligibility references grant no authority. State precedence: not_permitted, no_published_questionnaire, no_eligible_children, ready. No capture/history, local persistence or activation.')
    schema['components']['securitySchemes']={'HTTPBearer':{'type':'http','scheme':'bearer'}}
    models.pop('HTTPValidationError',None);models.pop('ValidationError',None)
    for status in sorted({status for status,_ in error_pairs}):
        name='ProvisionError'+str(status)
        model=deepcopy(models['ErrorEnvelope']);model.update(title=name,additionalProperties=False)
        model['properties']['error_id']['enum']=sorted(code for candidate,code in error_pairs if candidate==status)
        models[name]=model
        operation['responses'][str(status)]={'description':'Safe failure','content':{'application/json':{'schema':{'$ref':'#/components/schemas/'+name}}}}
    del models['ErrorEnvelope']
    for response in operation['responses'].values():
        response.setdefault('headers',{})['Cache-Control']={'schema':{'type':'string','const':'private, no-store'}}
    operation['responses']['401']['headers']['WWW-Authenticate']={'schema':{'type':'string','const':'Bearer'}}
    return schema
