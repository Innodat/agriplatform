"""Executable app-owned wire acceptance; no API/database/Access substitute."""
import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from apps.scribeswell.backend import personal_notes_contract as contract

OP = '11111111-1111-4111-8111-111111111111'
STUDY = '22222222-2222-4222-8222-222222222222'
NOTE = '33333333-3333-4333-8333-333333333333'
VALUE = {'document': {'version': 1, 'blocks': [
    {'type': 'paragraph', 'direction': 'rtl', 'content': [
        {'type': 'text', 'text': 'שָׁלוֹם private', 'marks': ['bold', 'italic']},
        {'type': 'external_link', 'url': 'https://example.org/שלום', 'content': [
            {'type': 'text', 'text': 'source', 'marks': []}]}]}]},
    'connections': [], 'highlights': []}


def command(name, payload):
    return contract.parse_command(name, json.dumps(payload, ensure_ascii=False).encode())


def replacement():
    return {'operation_id': OP, 'expected_revision': '1', 'value': copy.deepcopy(VALUE)}


def test_create_save_reopen_wire_acceptance():
    created = command('study.create', {'operation_id': OP, 'title': None})
    first = command('note.create', {'operation_id': OP, 'value': VALUE})
    saved = command('note.replace', replacement())
    assert created.title is None
    assert first.value == saved.value
    wire = {'id': NOTE, 'study_id': STUDY, 'owner_account_id': OP,
            'visibility': 'study', 'revision': '2', 'value': VALUE,
            'created_at': '2026-10-23T10:00:00.000000Z',
            'updated_at': '2026-10-23T10:00:01.000000Z',
            'created_by_actor_id': OP, 'updated_by_actor_id': OP}
    reopened = contract.NoteView.model_validate_json(json.dumps(wire))
    assert reopened.model_dump(mode='json') == wire
    assert saved.expected_revision == '1'
    assert 'private' not in repr(saved)


@pytest.mark.parametrize('revision', [0, 1, True, 1.0, '0', '01', '-1', '9223372036854775808'])
def test_revisions_are_positive_bigint_strings(revision):
    payload = replacement()
    payload['expected_revision'] = revision
    with pytest.raises(contract.ContractInputError, match='scribeswell_personal_notes_input_invalid'):
        command('note.replace', payload)


@pytest.mark.parametrize('raw', [b'{', b'\xff', b'\xef\xbb\xbf{}', b'[]', b'{"x":NaN}',
    b'{"operation_id":"x","operation_id":"y"}',
    b'{"nested":{"x":1,"x":2}}', b'{"secret":"\\ud800"}',
    b'{"x":1e999}', b'{"x":1.0}', b'{} trailing', b'[' * 20 + b']' * 20,
    b' ' * 65537])
def test_bad_framing_is_safe(raw):
    with pytest.raises(contract.ContractInputError) as caught:
        contract.parse_command('note.replace', raw)
    assert str(caught.value) == 'scribeswell_personal_notes_input_invalid'
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None


@pytest.mark.parametrize('mutate', [
    lambda p: p.update(owner_account_id=OP),
    lambda p: p.update(operation_id='00000000-0000-0000-0000-000000000000'),
    lambda p: p.update(operation_id=OP.upper().replace('11111111', 'AAAAAAAA', 1)),
    lambda p: p['value'].pop('highlights'),
    lambda p: p['value'].update(connections=[{}]),
    lambda p: p['value'].update(highlights=[{}]),
    lambda p: p['value']['document'].update(version=True),
    lambda p: p['value']['document'].update(version=1.0),
    lambda p: p['value']['document']['blocks'][0]['content'][0].update(marks=['italic', 'bold']),
    lambda p: p['value']['document']['blocks'][0]['content'][0].update(marks=['bold', 'bold']),
    lambda p: p['value']['document']['blocks'][0]['content'][0].update(text='\udfff'),
    lambda p: p['value']['document']['blocks'][0]['content'][0].update(html='<img>'),
    lambda p: p['value']['document']['blocks'][0]['content'][0].update(type='passage_link'),
])
def test_closed_aggregate_rejects_unsupported_or_forged_fields(mutate):
    payload = replacement()
    mutate(payload)
    with pytest.raises(contract.ContractInputError):
        contract.parse_command('note.replace', json.dumps(payload).encode())


@pytest.mark.parametrize('url', ['javascript:alert(1)', '/relative', 'https://u:p@example.org',
    'https://example.org\\evil', 'https://example.org/%xx', 'https://example.org:99999',
    'https://example.org/has space', 'https://example.org/\nsecret', 'https://',
    'https://example.org/%0a', 'https://example.org/%5c'])
def test_unsafe_external_links_are_rejected(url):
    payload = replacement()
    payload['value']['document']['blocks'][0]['content'][1]['url'] = url
    with pytest.raises(contract.ContractInputError):
        command('note.replace', payload)


@pytest.mark.parametrize('title', ['', '  ', 'line\nbreak', 'x' * 201, 1])
def test_supplied_titles_are_validated(title):
    with pytest.raises(contract.ContractInputError):
        command('study.create', {'operation_id': OP, 'title': title})


def test_list_and_empty_note_are_accepted_without_coercion():
    value = copy.deepcopy(VALUE)
    value['document']['blocks'] = [{'type': 'list', 'style': 'ordered', 'items': [
        [{'type': 'paragraph', 'direction': 'auto', 'content': []}]]}]
    assert command('note.create', {'operation_id': OP, 'value': value}).value.document.blocks
    value['document']['blocks'] = []
    assert command('note.create', {'operation_id': OP, 'value': value}).value.document.blocks == ()


def test_outcome_shapes_are_closed_and_resource_correlated():
    valid = {'status': 'committed', 'outcome': {'operation_id': OP,
        'command': 'note.replace', 'study_id': STUDY, 'note_id': NOTE, 'revision': '2'}}
    assert contract.OUTCOME_ADAPTER.validate_json(json.dumps(valid)).status == 'committed'
    valid['outcome']['note_id'] = None
    with pytest.raises(ValueError):
        contract.OUTCOME_ADAPTER.validate_json(json.dumps(valid))
    with pytest.raises(ValueError):
        contract.OUTCOME_ADAPTER.validate_json('{"status":"unresolved","body":"secret"}')


def test_exact_field_limits():
    payload = replacement()
    text = payload['value']['document']['blocks'][0]['content'][0]
    text['text'] = 'א' * 4096
    command('note.replace', payload)
    text['text'] += 'א'
    with pytest.raises(contract.ContractInputError):
        command('note.replace', payload)
    assert command('study.create', {'operation_id': OP, 'title': 'x' * 200}).title == 'x' * 200


def test_generation_is_reproducible_and_explicitly_opt_in():
    schema = contract.openapi_contract()
    assert schema['x-runtime-status'] == 'opt-in-development-production-disabled'
    assert schema['paths']['/api/studies/{study_id}/notes/{note_id}']['put']['requestBody']
    assert 'owner_account_id' not in schema['components']['schemas']['CreateStudy']['properties']
    app = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, str(app / 'tools/py/export_personal_notes_contract.py'), '--check'],
                            capture_output=True, timeout=10)
    assert result.returncode == 0, result.stderr.decode()
    assert json.loads((app / 'contracts/personal-notes-v1.openapi.json').read_text()) == schema
    assert 'personal_notes_contract' not in (app / 'backend/main.py').read_text()


def test_body_size_boundary_and_bigint_maximum():
    raw = json.dumps({'operation_id': OP, 'title': 'valid'}).encode()
    contract.parse_command('study.create', raw + b' ' * (65536 - len(raw)))
    with pytest.raises(contract.ContractInputError):
        contract.parse_command('study.create', raw + b' ' * (65537 - len(raw)))
    payload = replacement()
    payload['expected_revision'] = '9223372036854775807'
    assert command('note.replace', payload).expected_revision == '9223372036854775807'


def test_total_text_budget_boundary():
    payload = replacement()
    paragraph = {'type': 'paragraph', 'direction': 'auto', 'content': [
        {'type': 'text', 'text': 'x' * 4000, 'marks': []} for _ in range(12)] + [
        {'type': 'text', 'text': 'x' * 2000, 'marks': []}]}
    payload['value']['document']['blocks'] = [paragraph]
    command('note.replace', payload)
    paragraph['content'][-1]['text'] += 'x'
    with pytest.raises(contract.ContractInputError):
        command('note.replace', payload)


@pytest.mark.parametrize('raw', [None, 'text', bytearray(b'{}')])
def test_transport_is_bytes_only(raw):
    with pytest.raises(contract.ContractInputError):
        contract.parse_command('study.create', raw)


def test_unknown_command_is_safe():
    with pytest.raises(contract.ContractInputError):
        contract.parse_command('study.delete', b'{}')


@pytest.mark.parametrize('timestamp', ['2026-02-30T10:00:00.000000Z',
    '2026-10-23T10:00:00Z', '2026-10-23T10:00:00.000000+00:00',
    '0000-01-01T10:00:00.000000Z'])
def test_invalid_attribution_timestamps_rejected(timestamp):
    wire = {'id': STUDY, 'owner_account_id': OP, 'title': 'one', 'revision': '1',
        'created_at': timestamp, 'updated_at': timestamp,
        'created_by_actor_id': OP, 'updated_by_actor_id': OP}
    with pytest.raises(ValueError):
        contract.StudyView.model_validate_json(json.dumps(wire))


def test_storage_failure_has_its_own_safe_code():
    problem = {'error': 'Request could not be completed', 'code': 'studies_storage_unavailable', 'details': None}
    assert contract.Problem.model_validate_json(json.dumps(problem)).code == 'studies_storage_unavailable'


def test_all_generated_local_references_resolve():
    schema = contract.openapi_contract()
    pending = [schema]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            if '$ref' in item:
                prefix = '#/components/schemas/'
                assert item['$ref'].startswith(prefix)
                assert item['$ref'][len(prefix):] in schema['components']['schemas']
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)


@pytest.mark.parametrize(('kind', 'limit'), [('blocks', 256), ('inlines', 256), ('items', 128), ('paragraphs', 16), ('link', 64)])
def test_collection_limits(kind, limit):
    empty = {'type': 'paragraph', 'direction': 'auto', 'content': []}
    text = {'type': 'text', 'text': 'x', 'marks': []}
    def value(size):
        block = copy.deepcopy(empty)
        if kind == 'blocks':
            blocks = [block] * size
        elif kind == 'inlines':
            block['content'] = [text] * size
            blocks = [block]
        elif kind == 'link':
            block['content'] = [{'type': 'external_link', 'url': 'https://example.org', 'content': [text] * size}]
            blocks = [block]
        else:
            block = {'type': 'list', 'style': 'bullet', 'items': [[empty]] * size if kind == 'items' else [[empty] * size]}
            blocks = [block]
        return {'document': {'version': 1, 'blocks': blocks}, 'connections': [], 'highlights': []}
    contract.NoteValue.model_validate_json(json.dumps(value(limit)))
    with pytest.raises(ValueError):
        contract.NoteValue.model_validate_json(json.dumps(value(limit + 1)))


def test_url_byte_limit_counts_unicode_bytes():
    prefix = 'https://example.org/'
    url = prefix + 'א' * ((2048 - len(prefix.encode())) // 2)
    assert len(url.encode()) == 2048
    payload = replacement()
    link = payload['value']['document']['blocks'][0]['content'][1]
    link['url'] = url
    command('note.replace', payload)
    link['url'] += 'x'
    with pytest.raises(contract.ContractInputError):
        command('note.replace', payload)


def test_document_node_budget_is_independent_of_transport_budget():
    block = {'type': 'paragraph', 'direction': 'auto', 'content': [
        {'type': 'text', 'text': 'x', 'marks': []} for _ in range(255)]}
    value = {'document': {'version': 1, 'blocks': [block] * 7}, 'connections': [], 'highlights': []}
    # Validate the response DTO directly: transport limit is independently tighter here.
    contract.NoteValue.model_validate_json(json.dumps(value))
    value['document']['blocks'].append(block)
    with pytest.raises(ValueError):
        contract.NoteValue.model_validate_json(json.dumps(value))


@pytest.mark.parametrize('value', ['a\u0080b', 'a\u009fb'])
def test_unicode_controls_in_title_and_url(value):
    with pytest.raises(contract.ContractInputError):
        command('study.create', {'operation_id': OP, 'title': value})
    payload = replacement()
    payload['value']['document']['blocks'][0]['content'][1]['url'] = 'https://example.org/' + value
    with pytest.raises(contract.ContractInputError):
        command('note.replace', payload)


@pytest.mark.parametrize('url', ['https://999.999.999.999', 'https://[fe80::1%25eth0]/',
    'https://127.1', 'https://0x7f000001'])
def test_browser_incompatible_or_noncanonical_ip_hosts_rejected(url):
    payload = replacement()
    payload['value']['document']['blocks'][0]['content'][1]['url'] = url
    with pytest.raises(contract.ContractInputError):
        command('note.replace', payload)


def schema_validates(name, payload):
    from jsonschema import Draft202012Validator
    document = contract.openapi_contract()
    document['$ref'] = '#/components/schemas/' + name
    return Draft202012Validator(document).is_valid(payload)


@pytest.mark.parametrize(('revision', 'valid'), [('1', True), ('9223372036854775807', True),
    ('9223372036854775808', False), ('9999999999999999999', False), ('0', False), ('01', False)])
def test_revision_schema_dto_parity(revision, valid):
    payload = replacement()
    payload['expected_revision'] = revision
    assert schema_validates('ReplaceNote', payload) is valid
    if valid:
        command('note.replace', payload)
    else:
        with pytest.raises(contract.ContractInputError):
            command('note.replace', payload)


@pytest.mark.parametrize(('marks', 'valid'), [([], True), (['bold'], True), (['italic'], True),
    (['bold', 'italic'], True), (['bold', 'bold'], False), (['italic', 'bold'], False)])
def test_marks_schema_dto_parity(marks, valid):
    assert schema_validates('TextInline', {'type': 'text', 'text': 'x', 'marks': marks}) is valid


@pytest.mark.parametrize(('title', 'valid'), [('valid', True), ('א', True), ('', False),
    ('   ', False), ('a\u0080b', False), ('line\nbreak', False), ('trailing\n', False)])
def test_title_schema_dto_parity(title, valid):
    assert schema_validates('CreateStudy', {'operation_id': OP, 'title': title}) is valid


@pytest.mark.parametrize(('url', 'valid'), [('https://example.org/שלום', True),
    ('HTTP://example.org', True), ('/relative', False), ('https://u:p@example.org', False),
    ('https://example.org/a\u0080b', False), ('https://example.org/\n', False)])
def test_url_representable_schema_rules(url, valid):
    assert schema_validates('ExternalLink', {'type': 'external_link', 'url': url,
        'content': [{'type': 'text', 'text': 'source', 'marks': []}]}) is valid


def test_nil_uuid_is_invalid_in_schema():
    assert not schema_validates('CreateStudy', {'operation_id': '00000000-0000-0000-0000-000000000000', 'title': None})


@pytest.mark.parametrize(('name', 'note_id', 'valid'), [('study.create', None, True),
    ('study.create', NOTE, False), ('note.create', NOTE, True), ('note.create', None, False),
    ('note.replace', NOTE, True), ('note.replace', None, False)])
def test_ack_command_resource_schema_dto_parity(name, note_id, valid):
    payload = {'operation_id': OP, 'command': name, 'study_id': STUDY, 'note_id': note_id, 'revision': '1'}
    assert schema_validates('OperationAck', payload) is valid
    if valid:
        assert contract.OperationAck.model_validate_json(json.dumps(payload)).command == name
    else:
        with pytest.raises(ValueError):
            contract.OperationAck.model_validate_json(json.dumps(payload))


def test_error_schema_status_mapping():
    from jsonschema import Draft202012Validator
    document = contract.openapi_contract()
    responses = document['paths']['/api/studies/{study_id}/notes/{note_id}']['put']['responses']
    authentication = {'error': 'Request could not be completed', 'code': 'authentication_required', 'details': None}
    conflict = {'error': 'Request could not be completed', 'code': 'note_revision_conflict',
                'details': {'expected_revision': '1', 'current_revision': '2'}}
    for status, good, bad in [('401', authentication, conflict), ('409', conflict, authentication)]:
        schema = {**document, **responses[status]['content']['application/json']['schema']}
        validator = Draft202012Validator(schema)
        assert validator.is_valid(good)
        assert not validator.is_valid(bad)


def test_depth_and_value_budgets_are_exercised_before_dto_validation(monkeypatch):
    calls = []
    class Spy:
        @staticmethod
        def model_validate_json(raw):
            calls.append(True)
            return object()
    monkeypatch.setitem(contract.COMMAND_MODELS, 'study.create', Spy)
    tree = {'x': None}
    for _ in range(14):
        tree = {'x': tree}
    command('study.create', tree)  # deepest scalar exactly 16
    assert len(calls) == 1
    with pytest.raises(contract.ContractInputError):
        command('study.create', {'x': tree})
    assert len(calls) == 1
    command('study.create', {'values': [0] * 8190})  # root + list + values = 8192
    assert len(calls) == 2
    with pytest.raises(contract.ContractInputError):
        command('study.create', {'values': [0] * 8191})
    assert len(calls) == 2


def test_duplicate_valid_command_keys_cannot_be_masked_by_shape_errors():
    raw = ('{"operation_id":"' + OP + '","title":"one","title":"two"}').encode()
    with pytest.raises(contract.ContractInputError):
        contract.parse_command('study.create', raw)


def test_pages_revision_details_and_attribution_round_trip():
    study = {'id': STUDY, 'owner_account_id': OP, 'title': 'one', 'revision': '1',
             'created_at': '2026-10-23T10:00:00.000000Z', 'updated_at': '2026-10-23T10:00:00.000000Z',
             'created_by_actor_id': OP, 'updated_by_actor_id': OP}
    note = {**study, 'id': NOTE, 'study_id': STUDY, 'visibility': 'study', 'value': VALUE}
    note.pop('title')
    for model, item in [(contract.StudyPage, study), (contract.NotePage, note)]:
        for cursor in (None, 'A' * 512):
            payload = {'items': [item] * 50, 'next_cursor': cursor}
            assert model.model_validate_json(json.dumps(payload)).model_dump(mode='json') == payload
        for payload in ({'items': []}, {'items': [item] * 51, 'next_cursor': None},
                        {'items': [], 'next_cursor': 'A' * 513}, {'items': [], 'next_cursor': '+invalid'}):
            with pytest.raises(ValueError):
                model.model_validate_json(json.dumps(payload))
    study['updated_at'] = '2026-10-23T09:59:59.999999Z'
    with pytest.raises(ValueError):
        contract.StudyView.model_validate_json(json.dumps(study))
    payload = {'error': 'Request could not be completed', 'code': 'note_revision_conflict',
               'details': {'expected_revision': '1', 'current_revision': '2'}}
    assert contract.RevisionProblem.model_validate_json(json.dumps(payload)).model_dump(mode='json') == payload
    payload['details']['body'] = 'private'
    with pytest.raises(ValueError):
        contract.RevisionProblem.model_validate_json(json.dumps(payload))


def test_schema_anchored_scalars_reject_terminal_newlines():
    assert not schema_validates('CreateStudy', {'operation_id': OP + '\n', 'title': None})
    payload = replacement()
    payload['expected_revision'] += '\n'
    assert not schema_validates('ReplaceNote', payload)
    assert not schema_validates('StudyPage', {'items': [], 'next_cursor': 'abc\n'})


def test_all_generated_components_are_valid_json_schema():
    from jsonschema import Draft202012Validator
    for schema in contract.openapi_contract()['components']['schemas'].values():
        Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize('url', ['https://127.0.0.1/', 'https://[::1]/', 'https://example.org:443/a',
    'https://שלום.example/דרך', 'HTTP://EXAMPLE.ORG'])
def test_safe_host_variants_are_preserved(url):
    payload = replacement()
    payload['value']['document']['blocks'][0]['content'][1]['url'] = url
    assert command('note.replace', payload).value.document.blocks[0].content[1].url == url
