"""Pure registry inputs and refusal at the existing Identity owner boundary."""
from dataclasses import FrozenInstanceError, fields
import json
from pathlib import Path
import sys
import traceback

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import access_operator_input as operator
import identity_operator_input as identity

UUID = 'A1234567-1234-1234-1234-123456789ABC'
SENTINEL = 'PRIVATE_SUBMITTED_SENTINEL'
COMMANDS = ('application.register', 'permission.register', 'entry_permission.register')


def document(command='application.register'):
    payload = dict(app_id='fixture_app', expected_absent=True)
    if command != 'application.register':
        payload['permission'] = 'fixture.read:*'
    if command == 'permission.register':
        payload['scope_kind'] = 'account'
    return dict(schema_version=1, operation_id=UUID, command=command,
                scope={'kind': 'platform'}, payload=payload,
                reason_code='synthetic_fixture', evidence_ref='setup:fixture/1')


def encode(value):
    return json.dumps(value, ensure_ascii=True).encode()


def reject(body):
    with pytest.raises(operator.CommandValidationError) as caught:
        operator.parse_command(body)
    error = caught.value
    assert error.code == str(error) == 'access_operator_input_invalid'
    assert error.__context__ is None and error.__cause__ is None
    assert SENTINEL not in repr(error)
    assert SENTINEL not in ''.join(traceback.format_exception(error))


def assert_safe_refusal(error, code):
    assert error.code == str(error) == code
    assert error.args == (code,)
    assert error.__context__ is None and error.__cause__ is None
    rendered = str(error) + repr(error) + ''.join(traceback.format_exception(error))
    for submitted in (SENTINEL, 'setup:'+SENTINEL, UUID, 'fixture_app', 'fixture.read:*'):
        assert submitted not in rendered


@pytest.mark.parametrize('command,payload_type,command_type', [
    ('application.register', 'RegisterApplicationPayload', 'RegisterApplicationCommand'),
    ('permission.register', 'RegisterPermissionPayload', 'RegisterPermissionCommand'),
    ('entry_permission.register', 'RegisterEntryPermissionPayload', 'RegisterEntryPermissionCommand'),
])
def test_registration_is_typed_frozen_preserved_and_redacted(command, payload_type, command_type):
    value = document(command)
    parsed = operator.parse_command(encode(value))
    assert type(parsed).__name__ == command_type
    assert type(parsed.payload).__name__ == payload_type
    assert isinstance(parsed.scope, identity.PlatformScope)
    for key, expected in value.items():
        if key not in ('scope', 'payload'):
            assert getattr(parsed, key) == expected
    for key, expected in value['payload'].items():
        assert getattr(parsed.payload, key) == expected
    for record in (parsed, parsed.payload, parsed.scope):
        for field in fields(record):
            with pytest.raises(FrozenInstanceError):
                setattr(record, field.name, None)
        assert UUID not in repr(record) and 'fixture_app' not in repr(record)
        assert 'fixture.read' not in repr(record) and 'setup:fixture' not in repr(record)


@pytest.mark.parametrize('command', COMMANDS)
@pytest.mark.parametrize('level', [None, 'scope', 'payload'])
def test_missing_extra_and_duplicate_fields(command, level):
    original = document(command)
    target = original if level is None else original[level]
    for key in target:
        value = document(command)
        del (value if level is None else value[level])[key]
        if key == 'evidence_ref':
            assert operator.parse_command(encode(value)).evidence_ref is None
        else:
            reject(encode(value))
        raw = encode(original)
        token = (json.dumps(key) + ': ').encode()
        for alias in (json.dumps(key), '"'+key[:-1]+'\\u'+format(ord(key[-1]), '04x')+'"'):
            encoded_target = encode(target)
            duplicate = (alias+': '+json.dumps(target[key])+', ').encode()
            reject(raw.replace(encoded_target, encoded_target.replace(token, duplicate+token, 1), 1))
    for key in (SENTINEL, 'owner', 'executor_actor_id', 'authorized'):
        value = document(command)
        (value if level is None else value[level])[key] = SENTINEL
        reject(encode(value))


@pytest.mark.parametrize('field,invalid', [
    ('schema_version', [True, False, '1', 1.0, 0, 2, None, [], {}]),
    ('operation_id', [None, True, 1, [], {}, '', '00000000-0000-0000-0000-000000000000', UUID.replace('-', ''), '{'+UUID+'}', 'urn:uuid:'+UUID, 'g'+UUID[1:], UUID+'\n']),
    ('command', [None, True, 1, [], {}, 'actor.register_system', 'application.set_enabled', SENTINEL]),
    ('scope', [None, [], 'platform', {'kind': 'organization', 'org_id': UUID}, {'kind': 'platform', 'org_id': UUID}, {'kind': True}]),
    ('payload', [None, True, [], SENTINEL]),
    ('reason_code', [None, True, 1, [], {}, '', SENTINEL, 'a'*129, 'é']),
])
def test_envelope_rejections(field, invalid):
    for item in invalid:
        value = document(); value[field] = item
        reject(encode(value))


@pytest.mark.parametrize('command', COMMANDS)
@pytest.mark.parametrize('invalid', [False, 1, 0, None, 'true', [], {}])
def test_expected_absence_is_exact_true(command, invalid):
    value = document(command); value['payload']['expected_absent'] = invalid
    reject(encode(value))


@pytest.mark.parametrize('command', COMMANDS)
def test_app_id_ascii_grammar(command):
    for item in ('ab', 'a'*64, 'a0_b'):
        value = document(command); value['payload']['app_id'] = item
        assert operator.parse_command(encode(value)).payload.app_id == item
    for item in ('a', 'a'*65, 'Ab', 'éa', 'ab\n', '0a', 'a-b', None, True, 1, [], {}):
        value = document(command); value['payload']['app_id'] = item
        reject(encode(value))


@pytest.mark.parametrize('command', COMMANDS[1:])
def test_permission_literal_ascii_boundaries(command):
    for item in ('x', 'x'*200, ''.join(chr(point) for point in range(0x01, 0x80))):
        value = document(command); value['payload']['permission'] = item
        assert operator.parse_command(encode(value)).payload.permission.encode('ascii') == item.encode('ascii')
    for item in ('', 'x'*201, 'é', 'x\x00', None, True, 1, [], {}):
        value = document(command); value['payload']['permission'] = item
        reject(encode(value))


def test_permission_scope_is_closed_without_inferred_association():
    for scope in ('account', 'organization'):
        value = document('permission.register'); value['payload']['scope_kind'] = scope
        value['payload']['permission'] = 'unrelated.literal:*'
        assert operator.parse_command(encode(value)).payload.scope_kind == scope
    for scope in ('platform', 'ACCOUNT', None, True, 1, [], {}):
        value = document('permission.register'); value['payload']['scope_kind'] = scope
        reject(encode(value))


@pytest.mark.parametrize('command', COMMANDS)
def test_provenance_uses_identity_closed_semantics(command):
    for reason in ('initial_setup', 'synthetic_fixture', 'identity_adoption', 'access_change', 'setup_correction'):
        value = document(command); value['reason_code'] = reason
        assert operator.parse_command(encode(value)).reason_code == reason
    value = document(command); del value['evidence_ref']
    assert operator.parse_command(encode(value)).evidence_ref is None
    value['evidence_ref'] = 'A'+'_.:/-'*51
    assert operator.parse_command(encode(value)).evidence_ref == value['evidence_ref']
    for item in (None, '', 'https://private', 'a?token=private', 'a'*257, '/a', 'é', 'a b', True, 1, [], {}):
        value['evidence_ref'] = item
        reject(encode(value))


@pytest.mark.parametrize('body', [b'\xff', b'\xef\xbb\xbf{}', b'[]', b'null', b'{', b'{} trailing',
    b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}', b'{"x":1e9999}',
    b'{"x":'+b'9'*5000+b'}', b'['*2000+b']'*2000,
    b'{"PRIVATE_SUBMITTED_SENTINEL":', b'PRIVATE_SUBMITTED_SENTINEL\xff',
    '{}', bytearray(b'{}'), memoryview(b'{}'), None, 1])
def test_decoder_and_nonbytes_fail_safely(body):
    reject(body)


@pytest.mark.parametrize('forbidden', ['\x00', '\ud800', '\udfff'])
def test_forbidden_text_anywhere(forbidden):
    for level in (None, 'scope', 'payload'):
        value = document('permission.register')
        target = value if level is None else value[level]
        target[SENTINEL+forbidden] = [SENTINEL+forbidden]
        reject(encode(value))
    value = document('permission.register'); value['payload']['permission'] = SENTINEL+forbidden
    reject(encode(value))


@pytest.mark.parametrize('forbidden', ['\x00', '\ud800', '\udfff'])
def test_reused_decoder_checks_nested_keys_lists_and_values(forbidden):
    # Exercise the exact decoder imported by Access, without closed-field or ASCII
    # payload validation masking a missing recursive decoder check.
    def nested(text):
        return (
            {'outer': [{'nested': {text: 'safe'}}]},
            {'outer': [{'nested': ['safe', [text]]}]},
            {'outer': [{'nested': {'safe': text}}]},
        )
    for positive in nested('safe\t\x7fé🙂'):
        assert operator._decode(encode(positive)) == positive
    for invalid in nested(SENTINEL+forbidden):
        raw = encode(invalid)
        assert json.loads(raw) == invalid  # Ordinary JSON decoding accepts it.
        with pytest.raises(operator._IdentityValidationError) as caught:
            operator._decode(raw)
        assert_safe_refusal(caught.value, 'identity_operator_input_invalid')


def test_exact_body_byte_boundary():
    raw = encode(document())
    assert operator.parse_command(raw+b' '*(65536-len(raw))).command == 'application.register'
    reject(raw+b' '*(65537-len(raw)))


@pytest.mark.parametrize('command', COMMANDS)
def test_identity_parser_adapter_cli_refuse_before_effects(command, tmp_path, monkeypatch, capsys):
    import identity_operator as adapter
    import operator_cli as cli
    value = document(command)
    value['evidence_ref'] = 'setup:'+SENTINEL
    raw = encode(value)
    assert operator.parse_command(raw).evidence_ref == value['evidence_ref']
    with pytest.raises(identity.CommandValidationError) as caught:
        identity.parse_command(raw)
    assert_safe_refusal(caught.value, 'identity_operator_input_invalid')
    class Trap:
        def __getattr__(self, name):
            pytest.fail('Identity touched connection before refusing registry command')
    # The Identity parser's characterization suite deliberately reloads its module;
    # use each consumer's actual imported error class when suites run together.
    with pytest.raises(adapter.CommandValidationError) as caught:
        adapter.execute(Trap(), raw)
    assert_safe_refusal(caught.value, 'identity_operator_input_invalid')
    def trap(*args, **kwargs):
        pytest.fail('Identity CLI touched target, connection or dispatch')
    monkeypatch.setattr(cli, 'load_target', trap)
    monkeypatch.setattr(cli, '_connection', trap)
    monkeypatch.setattr(cli, 'dispatch', trap)
    path = tmp_path/'command.json'; path.write_bytes(raw)
    for owner in ('identity', 'access'):
        assert cli.main(['execute', '--owner', owner, '--target', 'unused', '--command-file', str(path)]) == 2
        output = capsys.readouterr()
        expected = 'identity_operator_input_invalid' if owner == 'identity' else 'command_invalid'
        assert json.loads(output.out) == {'code': expected}
        for submitted in (SENTINEL, value['evidence_ref'], UUID, 'fixture_app', 'fixture.read:*'):
            assert submitted not in output.out + output.err
        assert not output.err
    with pytest.raises(cli.CommandValidationError) as caught:
        cli.worker(['execute', 'unused', raw.decode(), UUID])
    assert_safe_refusal(caught.value, 'identity_operator_input_invalid')
