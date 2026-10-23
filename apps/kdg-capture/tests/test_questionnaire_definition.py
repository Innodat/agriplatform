"""Synthetic definition acceptance; no DB, operator command or editor UI."""
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api'))
from questionnaire import DefinitionError, parse_definition
IDS=[f'{n:08x}-1111-4111-8111-{n:012x}' for n in range(1,5)]
def boolean(qid=IDS[0]):
    return dict(id=qid,type='boolean',label='Synthetic label',required=True,default=False,
                details_enabled=True,details_label='Besonderhede')
def document(questions=None):
    return dict(schema_version=1,questions=questions if questions is not None else [boolean()])
def test_repeated_question_id_is_not_a_valid_published_definition():
    raw=json.dumps(document([boolean(),boolean()]))
    with pytest.raises(DefinitionError,match='^kdg_capture.invalid_questionnaire_definition$'):
        parse_definition(raw)

from copy import deepcopy
import traceback
from pydantic import ValidationError
from questionnaire import initial_definition, QuestionnaireDefinition, MAX_DEFINITION_BYTES

LABELS=['Hoe was haar algehele houding vandag?',
        'Het sy enige uitbarstings/gedragsprobleme gehad?',
        'Het sy sonder toestemming uit die klas geloop vandag?',
        'Het sy probeer huis toe hardloop?']

def test_initial_definition_matches_approved_content_without_allocating_ids():
    model=initial_definition(IDS)
    result=model.model_dump(mode='json',exclude_none=True)
    assert result['schema_version']==1
    assert [q['id'] for q in result['questions']]==IDS
    assert [q['label'] for q in result['questions']]==LABELS
    assert all(q['required'] is True for q in result['questions'])
    rating=result['questions'][0]
    assert (rating['minimum'],rating['maximum'],rating['minimum_label'],rating['maximum_label'])==(1,5,'Goed','Nie goed nie')
    assert 'default' not in rating and 'descriptions' not in rating
    assert all(q['default'] is False and q['details_enabled'] is True and q['details_label']=='Besonderhede' for q in result['questions'][1:])
    assert parse_definition(json.dumps(result)).model_dump(mode='json',exclude_none=True)==result
    with pytest.raises(ValidationError): model.questions[0].label='Changed'
    with pytest.raises(TypeError): model.questions[0]=model.questions[1]

@pytest.mark.parametrize('ids',[[],IDS[:3],IDS+[IDS[0]],[IDS[0]]*4,['ABCDEF01-aaaa-4aaa-8aaa-000000000001',*IDS[1:]],
                                [IDS[0].encode(),*IDS[1:]],['00000000-0000-0000-0000-000000000000',*IDS[1:]]])
def test_initial_definition_requires_four_distinct_canonical_string_ids(ids):
    with pytest.raises(DefinitionError,match='^kdg_capture.invalid_questionnaire_definition$'):
        initial_definition(ids)

@pytest.mark.parametrize('change',[
    lambda v:v.update(schema_version=True),lambda v:v.update(schema_version=1.0),lambda v:v.update(schema_version='1'),
    lambda v:v.update(schema_version=2),lambda v:v.update(unexpected='PRIVATE_LABEL'),lambda v:v.update(questions=[]),
    lambda v:v['questions'][0].update(type='expression'),lambda v:v['questions'][0].update(required='true'),
    lambda v:v['questions'][0].update(required=1),lambda v:v['questions'][0].update(default=0),
    lambda v:v['questions'][0].update(default=True),lambda v:v['questions'][0].update(details_enabled='true'),
    lambda v:v['questions'][0].update(details_label=None),lambda v:v['questions'][0].update(details_enabled=False),
    lambda v:v['questions'][0].update(label=' '),lambda v:v['questions'][0].update(label='\x00'),
    lambda v:v['questions'][0].update(label='\ud800'),lambda v:v['questions'][0].update(label='x'*501),
    lambda v:v['questions'][0].update(details_label='x'*501),lambda v:v['questions'][0].update(answer=True),
    lambda v:v['questions'][0].update(id='INVALID_PRIVATE_UUID'),lambda v:v['questions'][0].pop('id'),
])
def test_invalid_definitions_fail_without_echoing_input(change):
    value=document();change(value)
    with pytest.raises(DefinitionError,match='^kdg_capture.invalid_questionnaire_definition$') as failure:
        parse_definition(json.dumps(value))
    rendered=''.join(traceback.format_exception(failure.value))
    assert 'PRIVATE' not in rendered and 'ValidationError' not in rendered and 'During handling' not in rendered

@pytest.mark.parametrize('field,value',[('minimum',0),('minimum',True),('minimum',1.0),('minimum','1'),
                                       ('maximum',6),('maximum',4),('maximum',5.0),('maximum','5'),
                                       ('minimum_label','Bad'),('maximum_label','Good'),('default',1),
                                       ('descriptions',['invented'])])
def test_rating_configuration_does_not_coerce_or_expand_mvp_scale(field,value):
    doc=initial_definition(IDS).model_dump(mode='json',exclude_none=True)
    doc['questions'][0][field]=value
    with pytest.raises(DefinitionError): parse_definition(json.dumps(doc))

def test_question_count_boundary_and_all_supported_variants_preserve_order_and_text():
    questions=[dict(id=f'{i:08x}-aaaa-4aaa-8aaa-{i:012x}',type='text',label='  Preserved é\n'*10,required=False) for i in range(1,51)]
    model=parse_definition(json.dumps(document(questions)))
    assert [q.id for q in model.questions]==[q['id'] for q in questions]
    assert model.questions[0].label==questions[0]['label']
    assert len(model.questions)==50
    with pytest.raises(DefinitionError): parse_definition(json.dumps(document(questions+[boolean()])))
    plain=boolean();plain.update(details_enabled=False);plain.pop('details_label')
    assert parse_definition(json.dumps(document([plain]))).questions[0].details_label is None
    bounded=boolean();bounded.update(label='é'*500,details_label='x'*500)
    assert parse_definition(json.dumps(document([bounded]))).questions[0].label==bounded['label']

@pytest.mark.parametrize('raw',[b'\xff',b'{',b'[]',b'null',b'{"schema_version":1,"schema_version":1,"questions":[]}',
    b'{"schema_version":1,"questions":[{"id":"x","id":"x"}]}',
    b'{"schema_version":NaN,"questions":[]}',b'{"schema_version":Infinity,"questions":[]}',
    b' '* (MAX_DEFINITION_BYTES+1),{'schema_version':1},None])
def test_json_boundary_rejects_malformed_duplicate_nonfinite_oversized_or_nonwire_input(raw):
    with pytest.raises(DefinitionError,match='^kdg_capture.invalid_questionnaire_definition$'): parse_definition(raw)

def test_json_schema_declares_closed_question_union_and_bounds_without_altering_http_schema():
    schema=QuestionnaireDefinition.model_json_schema()
    assert schema['additionalProperties'] is False
    questions=schema['properties']['questions']
    assert (questions['minItems'],questions['maxItems'])==(1,50)
    assert questions['items']['discriminator']['propertyName']=='type'
    assert set(questions['items']['discriminator']['mapping'])=={'rating','boolean','text'}
    assert all(schema['$defs'][name]['additionalProperties'] is False for name in ('RatingQuestion','BooleanQuestion','TextQuestion'))
    assert schema['$defs']['BooleanQuestion']['properties']['default']['const'] is False
