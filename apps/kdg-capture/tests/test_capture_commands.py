"""Synthetic capture input acceptance; no HTTP, account, database or browser I/O."""
import json
from pathlib import Path
import sys
import traceback

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'api'))
from capture_commands import CommandError, parse_create, parse_edit, validate_answers
from questionnaire import initial_definition, parse_definition

IDS = [f'{n:08x}-aaaa-4aaa-8aaa-{n:012x}' for n in range(1, 10)]
QUESTION_IDS = IDS[:4]


def create(**changes):
    value = dict(
        operation_id=IDS[4], command_version=1, capture_id=IDS[5], child_id=IDS[6],
        questionnaire_version_id=IDS[7], observation_date='2026-10-23',
        captured_at='2026-10-23T10:11:12Z', child_eligibility_ref='synthetic opaque ref',
        answers={QUESTION_IDS[0]: {'value': 1}, **{
            key: {'value': False} for key in QUESTION_IDS[1:]
        }},
    )
    value.update(changes)
    return value


def test_incomplete_initial_observation_is_not_valid_for_fresh_persistence():
    command = parse_create(json.dumps(create(answers={})))
    with pytest.raises(CommandError, match='^validation_failed$'):
        validate_answers(command, initial_definition(QUESTION_IDS))


def test_initial_rating_one_and_required_false_are_valid_without_transformation():
    value = create()
    command = parse_create(json.dumps(value))
    validate_answers(command, initial_definition(QUESTION_IDS))


@pytest.mark.parametrize('changes', [
    {'owner_account_id': IDS[8]}, {'command_version': True},
    {'capture_id': IDS[5].upper()}, {'observation_date': '2026-02-30'},
    {'answers': {QUESTION_IDS[0]: {'value': 1.0}}},
    {'answers': {QUESTION_IDS[1]: {'value': False, 'details': 'private hidden text'}}},
])
def test_structurally_invalid_commands_never_reach_outcome_discovery(changes):
    with pytest.raises(CommandError, match='^validation_failed$'):
        parse_create(json.dumps(create(**changes)))


def test_duplicate_json_field_is_not_silently_overwritten():
    raw = json.dumps(create()).replace('"command_version": 1', '"command_version": 2, "command_version": 1')
    with pytest.raises(CommandError, match='^validation_failed$'):
        parse_create(raw)


def edit(**changes):
    value = {key: item for key, item in create().items() if key in (
        'operation_id', 'command_version', 'observation_date', 'answers'
    )}
    value['expected_revision'] = '9223372036854775807'
    value.update(changes)
    return value


def definition(question):
    return parse_definition(json.dumps(dict(schema_version=1, questions=[question])))


def question(kind, **changes):
    value = dict(id=QUESTION_IDS[0], type=kind, label='Synthetic label', required=True)
    if kind == 'rating':
        value.update(minimum=1, maximum=5, minimum_label='Goed', maximum_label='Nie goed nie')
    elif kind == 'boolean':
        value.update(default=False, details_enabled=True, details_label='Besonderhede')
    value.update(changes)
    return value


def test_default_dump_does_not_invent_hidden_false_details():
    value = create()
    command = parse_create(json.dumps(value))
    assert command.model_dump() == value


@pytest.mark.parametrize('value', [0, 6, -1, 1.0, 2.5, '1', None, [], {}])
def test_rating_like_invalid_scalars_fail_structure_or_pinned_type(value):
    raw = json.dumps(create(answers={QUESTION_IDS[0]: {'value': value}}))
    with pytest.raises(CommandError, match='^validation_failed$'):
        command = parse_create(raw)
        validate_answers(command, definition(question('rating')))


@pytest.mark.parametrize('value', [0, 1, 'false', None, [], {}])
def test_boolean_never_coerces_other_values(value):
    with pytest.raises(CommandError, match='^validation_failed$'):
        command = parse_create(json.dumps(create(answers={QUESTION_IDS[0]: {'value': value}})))
        validate_answers(command, definition(question('boolean')))


@pytest.mark.parametrize('details', ['', 'private hidden text', None])
def test_false_details_must_be_absent_even_when_empty(details):
    with pytest.raises(CommandError, match='^validation_failed$'):
        parse_create(json.dumps(create(answers={QUESTION_IDS[0]: {'value': False, 'details': details}})))


def test_true_details_require_definition_enablement_and_preserve_exact_input():
    text = '  synthetic e\u0301\nline two  '
    value = create(answers={QUESTION_IDS[0]: {'value': True, 'details': text}})
    command = parse_create(json.dumps(value))
    validate_answers(command, definition(question('boolean')))
    assert command.answers[QUESTION_IDS[0]].details == text
    disabled = definition(question('boolean', details_enabled=False, details_label=None))
    with pytest.raises(CommandError, match='^validation_failed$'):
        validate_answers(command, disabled)
    without_details = parse_create(json.dumps(create(answers={QUESTION_IDS[0]: {'value': True}})))
    validate_answers(without_details, disabled)


@pytest.mark.parametrize('required', [True, False])
@pytest.mark.parametrize('text', ['', ' \t\n'])
def test_blank_text_is_never_a_completed_answer(required, text):
    command = parse_create(json.dumps(create(answers={QUESTION_IDS[0]: {'value': text}})))
    with pytest.raises(CommandError, match='^validation_failed$'):
        validate_answers(command, definition(question('text', required=required)))


def test_text_preserves_unicode_whitespace_and_optional_omission():
    text = '  e\u0301\nplain <text>  '
    value = create(answers={QUESTION_IDS[0]: {'value': text}})
    command = parse_create(json.dumps(value, ensure_ascii=False))
    validate_answers(command, definition(question('text')))
    assert command.model_dump() == value
    omitted = parse_create(json.dumps(create(answers={})))
    validate_answers(omitted, definition(question('text', required=False)))


def test_explicit_old_definition_is_used_without_latest_version_substitution():
    old = definition(question('text'))
    newer = definition(question('rating'))
    command = parse_create(json.dumps(create(answers={QUESTION_IDS[0]: {'value': 'original text'}})))
    validate_answers(command, old)
    with pytest.raises(CommandError, match='^validation_failed$'):
        validate_answers(command, newer)
    validate_answers(command, old)


def test_missing_or_foreign_questions_are_fresh_semantics_not_lookup_preconditions():
    for answers in ({}, {IDS[8]: {'value': True}}):
        command = parse_create(json.dumps(create(answers=answers)))
        with pytest.raises(CommandError, match='^validation_failed$'):
            validate_answers(command, initial_definition(QUESTION_IDS))


@pytest.mark.parametrize('field', ['operation_id', 'capture_id', 'child_id', 'questionnaire_version_id'])
@pytest.mark.parametrize('bad', ['00000000-0000-0000-0000-000000000000', IDS[5].upper(), 'not-an-id', 1])
def test_identifiers_are_canonical_nonzero_strings(field, bad):
    with pytest.raises(CommandError, match='^validation_failed$'):
        parse_create(json.dumps(create(**{field: bad})))


@pytest.mark.parametrize('revision', [0, 1, True, '0', '-1', '01', '1.0', '9223372036854775808', '1\n'])
def test_edit_revision_is_a_positive_signed64_decimal_string(revision):
    with pytest.raises(CommandError, match='^validation_failed$'):
        parse_edit(json.dumps(edit(expected_revision=revision)))


def test_edit_fields_are_exact_and_initial_revision_one_is_valid():
    value = edit(expected_revision='1')
    command = parse_edit(json.dumps(value))
    validate_answers(command, initial_definition(QUESTION_IDS))
    assert command.model_dump() == value
    for field, item in [('capture_id', IDS[5]), ('child_id', IDS[6]), ('questionnaire_version_id', IDS[7]), ('captured_at', '2026-10-23T00:00:00Z')]:
        with pytest.raises(CommandError, match='^validation_failed$'):
            parse_edit(json.dumps(edit(**{field:item})))


@pytest.mark.parametrize('field', ['org_id', 'actor_id', 'owner_account_id', 'created_by', 'created_at', 'command_type', 'expected_revision'])
def test_create_does_not_accept_server_authority_or_edit_fields(field):
    with pytest.raises(CommandError, match='^validation_failed$'):
        parse_create(json.dumps(create(**{field:IDS[8]})))


@pytest.mark.parametrize('bad', ['2026-2-01', '2026-02-29', '0000-01-01', '2026-01-01T00:00:00Z', 20261023])
def test_observation_date_is_an_explicit_calendar_date(bad):
    with pytest.raises(CommandError, match='^validation_failed$'):
        parse_create(json.dumps(create(observation_date=bad)))


@pytest.mark.parametrize('bad', ['2026-10-23T00:00:00', '2026-10-23T00:00:00+02:00',
                                  '2026-02-30T00:00:00Z', '2026-10-23T25:00:00Z',
                                  '2026-10-23T00:00Z', 123])
def test_device_time_must_be_valid_rfc3339_utc(bad):
    with pytest.raises(CommandError, match='^validation_failed$'):
        parse_create(json.dumps(create(captured_at=bad)))


@pytest.mark.parametrize('stamp', ['2024-02-29T00:00:00Z', '2026-10-23T12:34:56.123456789+00:00', '2026-10-23t12:34:56z'])
def test_valid_utc_device_time_is_preserved_as_untrusted_input(stamp):
    value = create(captured_at=stamp, observation_date='2024-02-29')
    assert parse_create(json.dumps(value)).captured_at == stamp


@pytest.mark.parametrize('version', [True, 1.0, '1', 0, -1, None])
def test_malformed_versions_fail_validation(version):
    with pytest.raises(CommandError, match='^validation_failed$'):
        parse_create(json.dumps(create(command_version=version)))


@pytest.mark.parametrize('parse, value', [(parse_create, create()), (parse_edit, edit())])
def test_unsupported_positive_integer_version_has_stable_error(parse, value):
    value['command_version'] = 2
    with pytest.raises(CommandError, match='^unsupported_command_version$'):
        parse(json.dumps(value))


@pytest.mark.parametrize('text', ['bad\x00text', 'bad\ud800text', 'bad\udffftext'])
def test_persisted_strings_reject_nul_and_invalid_unicode(text):
    for value in (create(child_eligibility_ref=text), create(answers={QUESTION_IDS[0]: {'value': text}})):
        with pytest.raises(CommandError, match='^validation_failed$'):
            parse_create(json.dumps(value))


@pytest.mark.parametrize('field', ['value', 'details'])
def test_answer_text_bounds_count_unicode_codepoints(field):
    for size in (5000, 5001):
        answer = {'value': '\U0001f338' * size} if field == 'value' else {'value': True, 'details': '\U0001f338' * size}
        raw = json.dumps(create(answers={QUESTION_IDS[0]:answer}), ensure_ascii=False)
        if size == 5001:
            with pytest.raises(CommandError, match='^validation_failed$'):
                parse_create(raw)
        else:
            command = parse_create(raw)
            validate_answers(command, definition(question('text' if field == 'value' else 'boolean')))


def test_total_envelope_byte_limit_includes_utf8_and_whitespace():
    from capture_commands import MAX_COMMAND_BYTES
    raw = json.dumps(create(child_eligibility_ref='opaque \U0001f338'), ensure_ascii=False).encode()
    exact = raw + b' ' * (MAX_COMMAND_BYTES - len(raw))
    parse_create(exact)
    with pytest.raises(CommandError, match='^validation_failed$'):
        parse_create(exact + b' ')
    # Character count is below the byte ceiling while UTF-8 byte count exceeds it.
    large = json.dumps(create(child_eligibility_ref='\U0001f338' * 40000), ensure_ascii=False)
    assert len(large) < MAX_COMMAND_BYTES < len(large.encode())
    with pytest.raises(CommandError, match='^validation_failed$'):
        parse_create(large)


def test_answer_count_and_key_safety():
    answers = {f'{n:08x}-aaaa-4aaa-8aaa-{n:012x}': {'value': False} for n in range(1, 51)}
    parse_create(json.dumps(create(answers=answers)))
    answers[IDS[8].replace('00000009', '000000ff')] = {'value': False}
    with pytest.raises(CommandError, match='^validation_failed$'):
        parse_create(json.dumps(create(answers=answers)))
    for key in ('not-an-id', IDS[0].upper(), 'bad\x00key'):
        with pytest.raises(CommandError, match='^validation_failed$'):
            parse_create(json.dumps(create(answers={key:{'value':False}})))


@pytest.mark.parametrize('raw', [b'\xff', '[]', 'null', '{}', '{', '{"command_version":NaN}', '{"command_version":Infinity}', '{"command_version":1e999}', '['*2000 + ']'*2000])
def test_malformed_json_fails_safely(raw):
    with pytest.raises(CommandError, match='^validation_failed$'):
        parse_create(raw)


def test_nested_duplicate_keys_are_rejected():
    raw = json.dumps(create()).replace('"value": false', '"value": true, "value": false', 1)
    with pytest.raises(CommandError, match='^validation_failed$'):
        parse_create(raw)


def test_safe_errors_and_model_diagnostics_omit_private_input():
    canary = 'PRIVATE_SYNTHETIC_NOTES_DO_NOT_DISCLOSE'
    command = parse_create(json.dumps(create(answers={QUESTION_IDS[0]: {'value':canary}})))
    assert canary not in repr(command)
    assert canary not in str(command.answers[QUESTION_IDS[0]])
    with pytest.raises(CommandError) as failed:
        validate_answers(command, initial_definition(QUESTION_IDS))
    rendered = ''.join(traceback.format_exception(failed.value))
    assert canary not in rendered
    assert failed.value.__suppress_context__
    with pytest.raises(CommandError) as failed:
        parse_create(json.dumps(create(owner_account_id=canary)))
    assert canary not in ''.join(traceback.format_exception(failed.value))


@pytest.mark.parametrize('kind', ['rating', 'boolean', 'text'])
@pytest.mark.parametrize('required', [True, False])
def test_completeness_is_explicit_for_each_question_type(kind, required):
    command = parse_create(json.dumps(create(answers={})))
    pinned = definition(question(kind, required=required))
    if required:
        with pytest.raises(CommandError, match='^validation_failed$'):
            validate_answers(command, pinned)
    else:
        validate_answers(command, pinned)


def test_supplied_null_true_details_is_rejected():
    with pytest.raises(CommandError, match='^validation_failed$'):
        parse_create(json.dumps(create(answers={QUESTION_IDS[0]: {'value': True, 'details': None}})))


@pytest.mark.parametrize('details', ['', ' \t\n'])
def test_true_blank_details_are_valid_optional_content_and_preserved(details):
    value = create(answers={QUESTION_IDS[0]: {'value': True, 'details': details}})
    command = parse_create(json.dumps(value))
    validate_answers(command, definition(question('boolean')))
    assert command.model_dump() == value


def test_revalidation_refuses_constructed_invalid_nested_answers():
    from capture_commands import RatingAnswer
    command = parse_create(json.dumps(create()))
    command.answers[QUESTION_IDS[0]] = RatingAnswer.model_construct(value=6)
    with pytest.raises(CommandError, match='^validation_failed$'):
        validate_answers(command, initial_definition(QUESTION_IDS))


def test_revalidation_refuses_mutated_definition_configuration():
    pinned = definition(question('boolean'))
    object.__setattr__(pinned.questions[0], 'details_enabled', False)
    command = parse_create(json.dumps(create(answers={QUESTION_IDS[0]: {'value': False}})))
    with pytest.raises(CommandError, match='^validation_failed$'):
        validate_answers(command, pinned)


def test_revalidation_refuses_foreign_question_added_after_parse():
    from capture_commands import BooleanAnswer
    command = parse_create(json.dumps(create()))
    command.answers[IDS[8]] = BooleanAnswer(value=False)
    with pytest.raises(CommandError, match='^validation_failed$'):
        validate_answers(command, initial_definition(QUESTION_IDS))


@pytest.mark.parametrize('raw', [
    '{"command_version":2,"unknown":"bad\\u0000text"}',
    '{"command_version":2,"unknown":"bad\\ud800text"}',
    '{"command_version":2,"bad\\udfffkey":true}',
    '{"command_version":2,"unknown":{"nested":[1e999]}}',
])
def test_whole_envelope_checks_unknown_values_and_object_keys(raw):
    with pytest.raises(CommandError, match='^validation_failed$') as failed:
        parse_create(raw)
    assert failed.value.__suppress_context__


@pytest.mark.parametrize('answer', [
    {'value': 'PRIVATE_SYNTHETIC_NOTES_DO_NOT_DISCLOSE' * 200},
    {'value': False, 'details': 'PRIVATE_SYNTHETIC_NOTES_DO_NOT_DISCLOSE'},
    {'value': 'PRIVATE_SYNTHETIC_NOTES_DO_NOT_DISCLOSE\ud800'},
])
def test_parser_tracebacks_do_not_reveal_invalid_private_answers(answer):
    with pytest.raises(CommandError) as failed:
        parse_create(json.dumps(create(answers={QUESTION_IDS[0]: answer})))
    assert str(failed.value) == 'validation_failed'
    assert failed.value.__suppress_context__
    assert 'PRIVATE_SYNTHETIC_NOTES_DO_NOT_DISCLOSE' not in ''.join(traceback.format_exception(failed.value))
