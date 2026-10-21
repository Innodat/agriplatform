"""Enablement input is typed data; every execution boundary remains closed."""
from dataclasses import FrozenInstanceError, fields
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import access_operator_input as operator
import test_access_operator_input as registration

UUID = registration.UUID
SENTINEL = registration.SENTINEL
encode = registration.encode
reject = registration.reject
_registration_document = registration.document


def document():
    value = _registration_document()
    value['command'] = 'application.set_enabled'
    value['payload'] = dict(app_id='fixture_app', enabled=True, expected_revision='1')
    return value


@pytest.mark.parametrize('enabled', [True, False])
@pytest.mark.parametrize('revision', ['1', '9223372036854775807'])
@pytest.mark.parametrize('app', ['ab', 'a'*64, 'a0_b'])
def test_enablement_is_typed_frozen_redacted_and_preserved(enabled, revision, app):
    value = document()
    value['payload'].update(enabled=enabled, expected_revision=revision, app_id=app)
    parsed = operator.parse_command(encode(value))
    assert type(parsed) is operator.SetApplicationEnabledCommand
    assert type(parsed.payload) is operator.SetApplicationEnabledPayload
    assert isinstance(parsed.scope, operator.PlatformScope)
    assert parsed.scope.kind == 'platform'
    for key, expected in value.items():
        if key not in ('scope', 'payload'):
            assert getattr(parsed, key) == expected
    for key, expected in value['payload'].items():
        assert getattr(parsed.payload, key) == expected
        assert type(getattr(parsed.payload, key)) is type(expected)
    for record in (parsed, parsed.payload, parsed.scope):
        for field in fields(record):
            with pytest.raises(FrozenInstanceError):
                setattr(record, field.name, None)
        assert repr(record) == object.__repr__(record)


@pytest.mark.parametrize('field,invalid', [
    ('enabled', [None, 0, 1, 1.0, 'true', 'false', [], {}]),
    ('expected_revision', [None, True, False, 1, 1.0, [], {}, '', '0', '00', '01', '+1', '-1', ' 1', '1 ', '1\n', '١', '１', '9223372036854775808', '9'*20, '9'*5000]),
    ('app_id', ['a', 'a'*65, 'Ab', 'éa', 'a١', 'ab\n', '0a', 'a-b', None, True, 1, [], {}]),
])
def test_payload_rejects_without_coercion(field, invalid):
    for item in invalid:
        value = document(); value['payload'][field] = item
        reject(encode(value))


@pytest.mark.parametrize('level', [None, 'scope', 'payload'])
def test_closed_fields_and_plain_or_escaped_duplicates(level):
    original = document()
    target = original if level is None else original[level]
    for key in target:
        value = document()
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
    for key in ('expected_absent', 'owner', 'actor_id', 'executor_actor_id', 'permission', 'authorized', SENTINEL):
        value = document(); (value if level is None else value[level])[key] = SENTINEL
        reject(encode(value))


# Apply the existing envelope, provenance and decoder characterization to the
# new command, without changing the separate registration absence assertions.
def test_shared_strict_envelope_provenance_and_decoder(monkeypatch):
    monkeypatch.setattr(registration, 'document', lambda command=None: document())
    for field, invalid in [
        ('schema_version', [True, False, '1', 1.0, 0, 2, None, [], {}]),
        ('operation_id', [None, True, 1, [], {}, '', '00000000-0000-0000-0000-000000000000', UUID.replace('-', ''), '{'+UUID+'}', 'urn:uuid:'+UUID, 'g'+UUID[1:], UUID+'\n']),
        ('command', [None, True, 1, [], {}, 'actor.register_system', 'application.enable', SENTINEL]),
        ('scope', [None, [], 'platform', {'kind':'organization', 'org_id':UUID}, {'kind':'platform', 'org_id':UUID}, {'kind':True}]),
        ('payload', [None, True, [], SENTINEL]),
        ('reason_code', [None, True, 1, [], {}, '', SENTINEL, 'a'*129, 'é']),
    ]:
        registration.test_envelope_rejections(field, invalid)
    registration.test_provenance_uses_identity_closed_semantics('application.set_enabled')
    for forbidden in ('\x00', '\ud800', '\udfff'):
        registration.test_forbidden_text_anywhere(forbidden)
        registration.test_reused_decoder_checks_nested_keys_lists_and_values(forbidden)
    for body in (b'\xff', b'\xef\xbb\xbf{}', b'[]', b'null', b'{', b'{} trailing', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}', b'{"x":1e9999}', b'{"x":'+b'9'*5000+b'}', b'['*2000+b']'*2000, b'{"PRIVATE_SUBMITTED_SENTINEL":', b'PRIVATE_SUBMITTED_SENTINEL\xff', '{}', bytearray(b'{}'), memoryview(b'{}'), None, 1):
        registration.test_decoder_and_nonbytes_fail_safely(body)
    raw = encode(document())
    assert operator.parse_command(raw+b' '*(65536-len(raw))).command == 'application.set_enabled'
    reject(raw+b' '*(65537-len(raw)))


def test_reused_decoder_rejects_excessive_nesting_safely():
    control = {'outer': [{'nested': ['safe', {'value': 'safe'}]}]}
    assert operator._decode(encode(control)) == control
    raw = b'['*2000+encode(SENTINEL)+b']'*2000
    with pytest.raises(operator._IdentityValidationError) as caught:
        operator._decode(raw)
    registration.assert_safe_refusal(caught.value, 'identity_operator_input_invalid')


def test_identity_consumers_refuse_before_effects(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(registration, 'document', lambda command=None: document())
    registration.test_identity_parser_adapter_cli_refuse_before_effects('application.set_enabled', tmp_path, monkeypatch, capsys)


@pytest.mark.parametrize('enabled', [True, False])
def test_access_consumers_refuse_before_effects(enabled, tmp_path, monkeypatch, capsys):
    import access_operator as adapter
    import operator_cli as cli
    value = document()
    value['payload']['enabled'] = enabled
    raw = encode(value)
    class Trap:
        def __getattr__(self, name):
            pytest.fail('Access touched connection before refusing enablement')
    def trap(*args, **kwargs):
        pytest.fail('Access touched target, connection or dispatch before refusing enablement')
    monkeypatch.setattr(adapter, '_run', trap)
    monkeypatch.setattr(cli, 'load_target', trap)
    monkeypatch.setattr(cli, '_connection', trap)
    monkeypatch.setattr(cli, 'dispatch', trap)
    with pytest.raises(adapter.OperatorError) as caught:
        adapter.execute(Trap(), raw)
    registration.assert_safe_refusal(caught.value, 'command_unsupported')
    app_id = document()['payload']['app_id']
    with pytest.raises(adapter.OperatorError) as caught:
        adapter.outcome(Trap(), UUID, command='application.set_enabled', app_id=app_id)
    registration.assert_safe_refusal(caught.value, 'command_invalid')
    path = tmp_path/'command.json'; path.write_bytes(raw)
    assert cli.main(['execute', '--owner', 'access', '--target', 'unused', '--command-file', str(path)]) == 2
    assert json.loads(capsys.readouterr().out) == dict(code='command_unsupported', operation_id=UUID.lower())
    assert cli.main(['outcome', '--owner', 'access', '--target', 'unused', '--command', 'application.set_enabled', '--operation-id', UUID, '--app-id', 'fixture_app']) == 2
    assert json.loads(capsys.readouterr().out) == dict(code='command_invalid')
    for action, value in [('execute', raw.decode()), ('outcome', dict(command='application.set_enabled', app_id='fixture_app'))]:
        with pytest.raises(ValueError) as caught:
            cli.access_worker([action, 'unused', value, UUID, 'access'])
        assert type(caught.value) is ValueError
        assert caught.value.args == ()
        assert caught.value.__context__ is None and caught.value.__cause__ is None
