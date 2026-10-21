"""Organization configuration inputs convey no authority or execution support."""
from dataclasses import FrozenInstanceError, fields
import json
from pathlib import Path
import sys
import traceback

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import access_operator_input as operator
import test_access_operator_input as registration
import test_application_enable_input as enablement

UUID = registration.UUID
ORG_UUID = 'B2345678-2345-2345-2345-23456789ABCD'
SENTINEL = registration.SENTINEL
encode = registration.encode
NAME = 'organization_application.configure'
_registration_document = registration.document


def reject(body):
    with pytest.raises(operator.CommandValidationError) as caught:
        operator.parse_command(body)
    registration.assert_safe_refusal(caught.value, 'access_operator_input_invalid')
    assert ORG_UUID not in ''.join(traceback.format_exception(caught.value))


def document(variant='create'):
    value = _registration_document()
    value['command'] = NAME
    value['scope'] = dict(kind='organization', org_id=ORG_UUID)
    value['payload'] = dict(app_id='fixture_app', enabled=True)
    if variant == 'create':
        value['payload']['expected_absent'] = True
    else:
        value['payload']['expected_revision'] = '1'
    return value


@pytest.mark.parametrize('variant,revision', [
    ('create', None), ('update', '1'), ('update', '9007199254740993'),
    ('update', '9223372036854775807'),
])
@pytest.mark.parametrize('enabled', [True, False])
@pytest.mark.parametrize('app', ['ab', 'a'*64, 'a0_b'])
def test_typed_frozen_redacted_exact_variant(variant, enabled, app, revision):
    value = document(variant)
    value['payload'].update(app_id=app, enabled=enabled)
    if variant == 'update':
        value['payload']['expected_revision'] = revision
    parsed = operator.parse_command(encode(value))
    assert type(parsed) is operator.ConfigureOrganizationApplicationCommand
    # Compare the parser's imported class: Identity characterization reloads its module.
    assert type(parsed.scope) is operator.OrganizationScope
    expected_type = (operator.CreateOrganizationApplicationPayload if variant == 'create'
                     else operator.UpdateOrganizationApplicationPayload)
    assert type(parsed.payload) is expected_type
    assert {field.name for field in fields(parsed.payload)} == value['payload'].keys()
    for key, expected in value.items():
        if key not in ('scope', 'payload'):
            assert getattr(parsed, key) == expected
    for record, expected_values in ((parsed.scope, value['scope']), (parsed.payload, value['payload'])):
        for key, expected in expected_values.items():
            assert getattr(record, key) == expected
            assert type(getattr(record, key)) is type(expected)
    for record in (parsed, parsed.scope, parsed.payload):
        assert repr(record) == object.__repr__(record)
        for field in fields(record):
            with pytest.raises(FrozenInstanceError):
                setattr(record, field.name, None)


@pytest.mark.parametrize('variant', ['create', 'update'])
def test_variant_keys_are_exclusive_by_presence(variant):
    for other in (None, False, True, '1'):
        value = document(variant)
        value['payload']['expected_revision' if variant == 'create' else 'expected_absent'] = other
        reject(encode(value))
    value = document(variant)
    del value['payload']['expected_absent' if variant == 'create' else 'expected_revision']
    reject(encode(value))


@pytest.mark.parametrize('variant', ['create', 'update'])
def test_payload_values_without_coercion(variant):
    invalids = {
        'app_id': ['a', 'a'*65, 'Ab', 'éa', 'a١', 'ab\n', '0a', 'a-b', None, True, 1, [], {}],
        'enabled': [None, 0, 1, 1.0, 'true', 'false', [], {}],
    }
    if variant == 'create':
        invalids['expected_absent'] = [False, None, 1, 0, 1.0, 'true', [], {}]
    else:
        invalids['expected_revision'] = [None, True, False, 1, 1.0, [], {}, '', '0', '00', '01', '+1', '-1', ' 1', '1 ', '1\n', '١', '１', '9223372036854775808', '9'*20, '9'*5000]
    for field, items in invalids.items():
        for item in items:
            value = document(variant)
            value['payload'][field] = item
            reject(encode(value))


@pytest.mark.parametrize('variant', ['create', 'update'])
def test_scope_has_no_fallback_or_inference(variant):
    for invalid in (None, [], 'organization', {}, {'kind':'organization'}, {'kind':'platform'},
                    {'kind':'account'}, {'kind':'platform','org_id':UUID}, {'kind':'account','org_id':UUID},
                    {'kind':True,'org_id':UUID}, {'kind':'organization','org_id':UUID,'extra':SENTINEL}):
        value = document(variant); value['scope'] = invalid
        reject(encode(value))
    for invalid in (None, True, 1, [], {}, '', '00000000-0000-0000-0000-000000000000',
                    UUID.replace('-', ''), '{'+UUID+'}', 'urn:uuid:'+UUID, 'g'+UUID[1:], UUID+'\n'):
        value = document(variant); value['scope']['org_id'] = invalid
        reject(encode(value))
    value = document(variant); value['payload']['org_id'] = UUID
    reject(encode(value))
    for spelling in (ORG_UUID, ORG_UUID.lower()):
        value = document(variant); value['scope']['org_id'] = spelling
        assert operator.parse_command(encode(value)).scope.org_id == spelling


@pytest.mark.parametrize('command', [*registration.COMMANDS, 'application.set_enabled'])
def test_existing_commands_remain_platform_only(command):
    value = enablement.document() if command == 'application.set_enabled' else registration.document(command)
    assert operator.parse_command(encode(value)).scope.kind == 'platform'
    for scope in ({'kind':'organization','org_id':UUID}, {'kind':'organization'}, {'kind':'platform','org_id':UUID}):
        value['scope'] = scope
        reject(encode(value))


@pytest.mark.parametrize('variant', ['create', 'update'])
@pytest.mark.parametrize('level', [None, 'scope', 'payload'])
def test_closed_fields_and_plain_or_escaped_duplicates(variant, level):
    original = document(variant)
    target = original if level is None else original[level]
    for key in target:
        value = document(variant)
        del (value if level is None else value[level])[key]
        if key == 'evidence_ref':
            assert operator.parse_command(encode(value)).evidence_ref is None
        else:
            reject(encode(value))
        token = (json.dumps(key)+': ').encode()
        encoded_target = encode(target)
        for alias in (json.dumps(key), '"'+key[:-1]+'\\u'+format(ord(key[-1]), '04x')+'"'):
            duplicate = (alias+': '+json.dumps(target[key])+', ').encode()
            reject(encode(original).replace(encoded_target, encoded_target.replace(token, duplicate+token, 1), 1))
    for key in ('owner', 'actor_id', 'executor_actor_id', 'permission', 'authorized', SENTINEL):
        value = document(variant); (value if level is None else value[level])[key] = SENTINEL
        reject(encode(value))


@pytest.mark.parametrize('variant', ['create', 'update'])
def test_shared_strict_envelope_provenance_decoder_and_byte_limit(variant, monkeypatch):
    monkeypatch.setattr(registration, 'document', lambda command=None: document(variant))
    for field, invalid in [
        ('schema_version', [True, False, '1', 1.0, 0, 2, None, [], {}]),
        ('operation_id', [None, True, 1, [], {}, '', '00000000-0000-0000-0000-000000000000', UUID.replace('-', ''), '{'+UUID+'}', 'urn:uuid:'+UUID, 'g'+UUID[1:], UUID+'\n']),
        ('command', [None, True, 1, [], {}, 'actor.register_system', 'organization_application.enable', SENTINEL]),
        ('payload', [None, True, [], SENTINEL]),
        ('reason_code', [None, True, 1, [], {}, '', SENTINEL, 'a'*129, 'é']),
    ]:
        registration.test_envelope_rejections(field, invalid)
    registration.test_provenance_uses_identity_closed_semantics(NAME)
    for forbidden in ('\x00', '\ud800', '\udfff'):
        registration.test_forbidden_text_anywhere(forbidden)
        registration.test_reused_decoder_checks_nested_keys_lists_and_values(forbidden)
    for body in (b'\xff', b'\xef\xbb\xbf{}', b'[]', b'null', b'{', b'{} trailing', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}', b'{"x":1e9999}', b'{"x":'+b'9'*5000+b'}', b'['*2000+b']'*2000, b'{"PRIVATE_SUBMITTED_SENTINEL":', b'PRIVATE_SUBMITTED_SENTINEL\xff', '{}', bytearray(b'{}'), memoryview(b'{}'), None, 1):
        registration.test_decoder_and_nonbytes_fail_safely(body)
    enablement.test_reused_decoder_rejects_excessive_nesting_safely()
    raw = encode(document(variant))
    assert operator.parse_command(raw+b' '*(65536-len(raw))).command == NAME
    reject(raw+b' '*(65537-len(raw)))


@pytest.mark.parametrize('variant', ['create', 'update'])
def test_identity_consumers_refuse_before_effects(variant, tmp_path, monkeypatch, capsys):
    import identity_operator as adapter
    import operator_cli as cli
    monkeypatch.setattr(registration, 'document', lambda command=None: document(variant))
    registration.test_identity_parser_adapter_cli_refuse_before_effects(NAME, tmp_path, monkeypatch, capsys)
    # Lookup remains closed as well; the shared execute helper already traps the
    # CLI target, connection and dispatcher for the remainder of this test.
    class Trap:
        def __getattr__(self, name):
            pytest.fail('Identity outcome touched connection')
    with pytest.raises(adapter.OperatorError) as caught:
        adapter.outcome(Trap(), UUID, command=NAME)
    registration.assert_safe_refusal(caught.value, 'command_invalid')
    assert cli.main(['outcome', '--owner', 'identity', '--target', 'unused', '--command', NAME, '--operation-id', UUID]) == 2
    output = capsys.readouterr()
    assert json.loads(output.out) == dict(code='command_invalid')
    assert output.err == ''
    lookup = dict(command=NAME, app_id=document(variant)['payload']['app_id'])
    with pytest.raises(ValueError) as caught:
        cli.worker(['outcome', 'unused', lookup, UUID])
    assert type(caught.value) is ValueError and caught.value.args == ()
    assert caught.value.__context__ is None and caught.value.__cause__ is None


@pytest.mark.parametrize('variant', ['create', 'update'])
@pytest.mark.parametrize('enabled', [True, False])
def test_access_consumers_refuse_before_effects(variant, enabled, tmp_path, monkeypatch, capsys):
    import access_operator as adapter
    import operator_cli as cli
    value = document(variant); value['payload']['enabled'] = enabled
    raw = encode(value)
    def trap(*args, **kwargs):
        pytest.fail('unsupported command touched target, connection, dispatch or SQL')
    class Trap:
        def __getattr__(self, name):
            trap()
    for name in ('load_target', '_connection', 'dispatch'):
        monkeypatch.setattr(cli, name, trap)
    monkeypatch.setattr(adapter, '_run', trap)
    with pytest.raises(adapter.OperatorError) as caught:
        adapter.execute(Trap(), raw)
    registration.assert_safe_refusal(caught.value, 'command_unsupported')
    assert caught.value.operation_id == UUID.lower()
    with pytest.raises(adapter.OperatorError) as caught:
        adapter.outcome(Trap(), UUID, command=NAME, app_id=value['payload']['app_id'])
    registration.assert_safe_refusal(caught.value, 'command_invalid')
    path = tmp_path/'command.json'; path.write_bytes(raw)
    assert cli.main(['execute', '--owner', 'access', '--target', 'unused', '--command-file', str(path)]) == 2
    output = capsys.readouterr()
    assert json.loads(output.out) == dict(code='command_unsupported', operation_id=UUID.lower())
    assert output.err == ''
    assert cli.main(['outcome', '--owner', 'access', '--target', 'unused', '--command', NAME, '--operation-id', UUID, '--app-id', value['payload']['app_id']]) == 2
    output = capsys.readouterr()
    assert json.loads(output.out) == dict(code='command_invalid')
    assert output.err == ''
    lookup = dict(command=NAME, app_id=value['payload']['app_id'])
    for request in (['execute', 'unused', raw.decode(), UUID, 'access'], ['outcome', 'unused', lookup, UUID, 'access']):
        for worker in (cli.access_worker, cli.worker):
            with pytest.raises(ValueError) as caught:
                worker(request)
            error = caught.value
            assert type(error) is ValueError and error.args == ()
            assert error.__context__ is None and error.__cause__ is None
            rendered = str(error)+repr(error)+''.join(traceback.format_exception(error))
            for submitted in (SENTINEL, UUID, ORG_UUID, value['payload']['app_id'], value['evidence_ref'], raw.decode()):
                assert submitted not in rendered
