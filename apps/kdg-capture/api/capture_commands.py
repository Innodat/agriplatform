"""KDG capture inputs; no routes, authorization, outcome orchestration or storage.

Parse structure before outcome lookup. Validate against the explicitly supplied pinned
published definition only for a fresh action after confirmed outcome absence. Replays
must use the stored receipt/resource and current authority, not incoming answer semantics.

Pydantic freezes field assignment, not the answers dictionary. Keep parsed input private
and call validate_answers immediately before consuming a fresh write; it revalidates
nested instances. These DTOs are not an immutable queued-command envelope.
"""
from datetime import date, datetime, timezone
import json
import math
import re
from typing import Annotated

from pydantic import (
    BaseModel, BeforeValidator, ConfigDict, Field, StrictBool, StrictInt,
    model_validator,
)

from context import canonical_uuid, positive_bigint_pattern
from questionnaire import (
    BooleanQuestion, QuestionnaireDefinition, RatingQuestion, TextQuestion,
)

MAX_COMMAND_BYTES = 131072


class CommandError(ValueError):
    """Safe identifier only; never expose validation dictionaries or exception locals."""


def _text(value):
    if type(value) is not str or '\x00' in value:
        raise ValueError('invalid_text')
    value.encode('utf-8')
    return value


def _nonblank(value):
    value = _text(value)
    if not value.strip():
        raise ValueError('empty_reference')
    return value


def _date(value):
    if type(value) is not str or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):
        raise ValueError('invalid_date')
    date.fromisoformat(value)
    return value


def _device_time(value):
    if type(value) is not str or not re.fullmatch(
        r'[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}:[0-9]{2}'
        r'(?:\.[0-9]+)?(?:[Zz]|\+00:00)', value,
    ):
        raise ValueError('invalid_device_time')
    parsed = datetime.fromisoformat(value.upper())
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError('invalid_device_time')
    return value


Identifier = Annotated[str, Field(strict=True), BeforeValidator(canonical_uuid)]
AnswerText = Annotated[str, Field(strict=True, max_length=5000), BeforeValidator(_text)]
Revision = Annotated[str, Field(strict=True, pattern=positive_bigint_pattern())]
ObservationDate = Annotated[str, BeforeValidator(_date)]
DeviceTime = Annotated[str, BeforeValidator(_device_time)]
OpaqueReference = Annotated[str, BeforeValidator(_nonblank)]


class Closed(BaseModel):
    model_config = ConfigDict(
        extra='forbid', strict=True, frozen=True, hide_input_in_errors=True,
        revalidate_instances='always',
    )

    def __repr__(self):
        return '<' + type(self).__name__ + ' redacted>'

    def __str__(self):
        return self.__repr__()


class RatingAnswer(Closed):
    value: Annotated[StrictInt, Field(ge=1, le=5)]


class BooleanAnswer(Closed):
    value: StrictBool
    details: AnswerText | None = Field(default=None, exclude_if=lambda value: value is None)

    @model_validator(mode='after')
    def active_details(self):
        if 'details' in self.model_fields_set and (not self.value or self.details is None):
            raise ValueError('hidden_or_null_details')
        return self


class TextAnswer(Closed):
    value: AnswerText


Answer = RatingAnswer | BooleanAnswer | TextAnswer
AnswerMap = Annotated[dict[Identifier, Answer], Field(max_length=50)]


class CaptureInput(Closed):
    operation_id: Identifier
    command_version: Annotated[StrictInt, Field(ge=1, le=1)]
    observation_date: ObservationDate
    answers: AnswerMap


class CreateCommand(CaptureInput):
    capture_id: Identifier
    child_id: Identifier
    questionnaire_version_id: Identifier
    captured_at: DeviceTime
    child_eligibility_ref: OpaqueReference


class EditCommand(CaptureInput):
    expected_revision: Revision


def _closed_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate_key')
        result[key] = value
    return result


def _check_values(value):
    # Includes JSON object keys and unknown fields, not just eventual model values.
    if isinstance(value, str):
        _text(value)
    elif isinstance(value, dict):
        for key, item in value.items():
            _text(key)
            _check_values(item)
    elif isinstance(value, list):
        for item in value:
            _check_values(item)
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError('nonfinite_number')


def _invalid_constant(_):
    raise ValueError('invalid_constant')


def _parse(raw, model):
    try:
        if type(raw) not in (str, bytes):
            raise ValueError('invalid_input')
        data = raw.encode('utf-8') if type(raw) is str else raw
        if len(data) > MAX_COMMAND_BYTES:
            raise ValueError('input_too_large')
        value = json.loads(
            data.decode('utf-8'), object_pairs_hook=_closed_object,
            parse_constant=_invalid_constant,
        )
        _check_values(value)
        if isinstance(value, dict):
            version = value.get('command_version')
            if type(version) is int and version > 0 and version != 1:
                raise CommandError('unsupported_command_version') from None
        return model.model_validate(value)
    except CommandError:
        raise
    except (ValueError, TypeError, RecursionError):
        raise CommandError('validation_failed') from None


def parse_create(raw: str | bytes) -> CreateCommand:
    """Strict bounded structure only; eligibility reference conveys no authority."""
    return _parse(raw, CreateCommand)


def parse_edit(raw: str | bytes) -> EditCommand:
    """Strict bounded structure; capture identity belongs to the future route path."""
    return _parse(raw, EditCommand)


def validate_answers(command: CreateCommand | EditCommand, definition: QuestionnaireDefinition) -> None:
    """Check a fresh action against its explicit original definition, without mutation.

    No latest-version discovery, published-state proof, authorization or persistence.
    Caller must bind definition to the referenced create version or stored edit version.
    """
    try:
        if type(command) not in (CreateCommand, EditCommand):
            raise ValueError('invalid_command')
        command = type(command).model_validate(command)
        if type(definition) is not QuestionnaireDefinition:
            raise ValueError('invalid_definition')
        definition = QuestionnaireDefinition.model_validate(definition)
        questions = {question.id: question for question in definition.questions}
        if command.answers.keys() - questions.keys():
            raise ValueError('foreign_question')
        for question in definition.questions:
            answer = command.answers.get(question.id)
            if answer is None:
                if question.required:
                    raise ValueError('required_answer')
                continue
            if isinstance(question, RatingQuestion):
                if type(answer) is not RatingAnswer:
                    raise ValueError('wrong_answer_type')
            elif isinstance(question, BooleanQuestion):
                if type(answer) is not BooleanAnswer:
                    raise ValueError('wrong_answer_type')
                if not question.details_enabled and 'details' in answer.model_fields_set:
                    raise ValueError('disabled_details')
            elif isinstance(question, TextQuestion):
                if type(answer) is not TextAnswer or not answer.value.strip():
                    raise ValueError('empty_or_wrong_text')
    except (ValueError, TypeError, RecursionError):
        raise CommandError('validation_failed') from None
