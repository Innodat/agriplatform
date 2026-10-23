"""KDG schema-version1 definition candidate. No persistence, setup or API I/O."""
import json
from typing import Annotated, Literal
from pydantic import AfterValidator, BeforeValidator, BaseModel, ConfigDict, Field, StrictBool, StrictInt, field_validator, model_validator
from context import Identifier, canonical_uuid

MAX_DEFINITION_BYTES = 128 * 1024
ERROR_ID = 'kdg_capture.invalid_questionnaire_definition'


def _label(value):
    if not value.strip() or '\x00' in value:
        raise ValueError('invalid_label')
    try:
        value.encode('utf-8')
    except UnicodeEncodeError:
        raise ValueError('invalid_label') from None
    return value


Label = Annotated[str, Field(strict=True, min_length=1, max_length=500), AfterValidator(_label)]
QuestionId = Annotated[Identifier, BeforeValidator(canonical_uuid)]


class DefinitionModel(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, hide_input_in_errors=True,
                              revalidate_instances='always')


class Question(DefinitionModel):
    id: QuestionId
    label: Label
    required: StrictBool


class RatingQuestion(Question):
    type: Literal['rating']
    minimum: Annotated[StrictInt, Field(ge=1, le=1)]
    maximum: Annotated[StrictInt, Field(ge=5, le=5)]
    minimum_label: Literal['Goed']
    maximum_label: Literal['Nie goed nie']


class BooleanQuestion(Question):
    type: Literal['boolean']
    default: Literal[False]
    details_enabled: StrictBool
    details_label: Label | None = None

    @field_validator('default', mode='before')
    @classmethod
    def strict_default(cls, value):
        if type(value) is not bool:
            raise ValueError('invalid_boolean_default')
        return value

    @model_validator(mode='after')
    def detail_configuration(self):
        if self.details_enabled != (self.details_label is not None):
            raise ValueError('invalid_details_configuration')
        return self


class TextQuestion(Question):
    type: Literal['text']


QuestionDefinition = Annotated[RatingQuestion | BooleanQuestion | TextQuestion, Field(discriminator='type')]


class QuestionnaireDefinition(DefinitionModel):
    schema_version: Annotated[StrictInt, Field(ge=1, le=1)]
    questions: Annotated[tuple[QuestionDefinition, ...], Field(min_length=1, max_length=50)]

    @model_validator(mode='after')
    def distinct_question_ids(self):
        if len({question.id for question in self.questions}) != len(self.questions):
            raise ValueError('duplicate_question_id')
        return self


class DefinitionError(ValueError):
    """Safe public domain failure. Raw Pydantic/JSON diagnostics stay internal."""


def _closed_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate_key')
        result[key] = value
    return result


def parse_definition(raw: str | bytes) -> QuestionnaireDefinition:
    """Validate bounded UTF-8 JSON without echoing input or exception context."""
    try:
        if type(raw) not in (str, bytes):
            raise ValueError('invalid_input')
        data = raw.encode('utf-8') if type(raw) is str else raw
        if len(data) > MAX_DEFINITION_BYTES:
            raise ValueError('input_too_large')
        value = json.loads(data.decode('utf-8'), object_pairs_hook=_closed_object,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError('invalid_constant')))
        return QuestionnaireDefinition.model_validate(value)
    except (ValueError, TypeError, RecursionError):
        raise DefinitionError(ERROR_ID) from None


def initial_definition(question_ids) -> QuestionnaireDefinition:
    """Build inert initial content using four explicit IDs; never allocate or persist."""
    try:
        if type(question_ids) not in (list, tuple) or len(question_ids) != 4:
            raise ValueError('four_ids_required')
        labels = ('Hoe was haar algehele houding vandag?',
                  'Het sy enige uitbarstings/gedragsprobleme gehad?',
                  'Het sy sonder toestemming uit die klas geloop vandag?',
                  'Het sy probeer huis toe hardloop?')
        questions = [dict(id=question_ids[0], type='rating', label=labels[0], required=True,
                          minimum=1, maximum=5, minimum_label='Goed', maximum_label='Nie goed nie')]
        questions.extend(dict(id=qid, type='boolean', label=label, required=True, default=False,
                              details_enabled=True, details_label='Besonderhede')
                         for qid, label in zip(question_ids[1:], labels[1:]))
        return QuestionnaireDefinition(schema_version=1, questions=tuple(questions))
    except (ValueError, TypeError):
        raise DefinitionError(ERROR_ID) from None
