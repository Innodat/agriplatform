"""Parser-only acceptance: no database, credentials or operator execution."""
from dataclasses import FrozenInstanceError, fields
import importlib.util
import json
from pathlib import Path
import sys

import pytest

MODULE = Path(__file__).resolve().parents[1] / 'identity_operator_input.py'
spec = importlib.util.spec_from_file_location('identity_operator_input', MODULE)
operator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = operator
spec.loader.exec_module(operator)

UUID = 'A1234567-1234-1234-1234-123456789ABC'
OTHER = 'b2345678-1234-1234-1234-123456789abc'
MAX = '9223372036854775807'
SENTINEL = 'PRIVATE_SUBMITTED_SENTINEL'
WHITE_SPACE = '\t\n\v\f\r \x85\xa0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000'


def document(command='actor.register_system'):
    payloads = {
        'actor.register_system': dict(actor_id=UUID, kind='system', actor_key='system:migrate', display_name='System', expected_absent=True),
        'account_actor.ensure': dict(account_id=UUID, actor_id=OTHER, display_name='Account', expected_absent=True),
        'membership.join': dict(account_id=UUID, expected_previous_membership_id=None),
        'membership.retire': dict(account_id=UUID, membership_id='1', expected_revision='1'),
    }
    return dict(schema_version=1, operation_id=UUID, command=command,
                scope={'kind': 'organization', 'org_id': OTHER} if command.startswith('membership.') else {'kind': 'platform'},
                payload=payloads[command], reason_code='synthetic_fixture', evidence_ref='setup:fixture/1')


def encode(value):
    return json.dumps(value, ensure_ascii=True).encode()


def reject(body):
    with pytest.raises(operator.CommandValidationError) as caught:
        operator.parse_command(body if isinstance(body, bytes) else encode(body))
    assert str(caught.value) == 'identity_operator_input_invalid'
    assert SENTINEL not in repr(caught.value)
    assert SENTINEL not in str(caught.value)
    assert caught.value.code == 'identity_operator_input_invalid'


@pytest.mark.parametrize('command,payload_type,scope_type', [
    ('actor.register_system', 'RegisterSystemPayload', 'PlatformScope'),
    ('account_actor.ensure', 'EnsureAccountActorPayload', 'PlatformScope'),
    ('membership.join', 'JoinMembershipPayload', 'OrganizationScope'),
    ('membership.retire', 'RetireMembershipPayload', 'OrganizationScope'),
])
def test_selected_commands_are_typed_frozen_and_redacted(command, payload_type, scope_type):
    value = document(command)
    variant = ['actor.register_system', 'account_actor.ensure', 'membership.join', 'membership.retire'].index(command)
    value['operation_id'] = f'{variant+1:08X}-ABCD-1234-ABCD-123456789ABC'
    value['evidence_ref'] = 'private:evidence/'+command.replace('.', '/')
    if command.startswith('membership.'):
        value['scope']['org_id'] = f'{variant+12:08X}-ABCD-1234-ABCD-123456789ABC'
    for name in ('account_id', 'actor_id'):
        if name in value['payload']:
            value['payload'][name] = f'{variant+(8 if name == "actor_id" else 4):08x}-abcd-1234-abcd-123456789abc'
    if 'display_name' in value['payload']:
        value['payload']['display_name'] = SENTINEL+'_'+command
    if 'actor_key' in value['payload']:
        value['payload']['actor_key'] = 'private:actor.registration'
    parsed = operator.parse_command(encode(value))
    assert parsed.command == command and parsed.operation_id == value['operation_id']
    assert parsed.schema_version == 1 and parsed.reason_code == 'synthetic_fixture'
    assert parsed.evidence_ref == value['evidence_ref']
    assert type(parsed.payload).__name__ == payload_type
    assert type(parsed.scope).__name__ == scope_type
    assert parsed.scope.kind == value['scope']['kind']
    if command.startswith('membership.'):
        assert parsed.scope.org_id == value['scope']['org_id']
    else:
        assert not hasattr(parsed.scope, 'org_id')
    submitted = [value['operation_id'], value['evidence_ref']]
    submitted += [item for key, item in value['payload'].items()
                  if key in ('account_id', 'actor_id', 'actor_key', 'display_name')]
    if 'org_id' in value['scope']:
        submitted.append(value['scope']['org_id'])
    assert len(submitted) == len(set(submitted))
    for part in [parsed, parsed.payload, parsed.scope]:
        for sensitive in submitted:
            assert sensitive not in repr(part)
        with pytest.raises(FrozenInstanceError):
            setattr(part, fields(part)[0].name, None)
    for name, expected in value['payload'].items():
        assert getattr(parsed.payload, name) == expected


@pytest.mark.parametrize('owner', [None, False, True])
def test_owner_is_only_typed_requested_input(owner):
    value = document('membership.join')
    if owner is not None: value['payload']['is_owner'] = owner
    parsed = operator.parse_command(encode(value))
    assert parsed.payload.is_owner is (owner is True)
    assert not hasattr(parsed, 'authorized')


@pytest.mark.parametrize('command', ['actor.register_system', 'account_actor.ensure', 'membership.join', 'membership.retire'])
def test_closed_fields_and_required_fields_at_every_level(command):
    original = document(command)
    for location in [None, 'scope', 'payload']:
        original_part = original if location is None else original[location]
        for key in original_part:
            if key == 'evidence_ref' or (location == 'payload' and key == 'is_owner'): continue
            value = document(command)
            del (value if location is None else value[location])[key]
            reject(value)
        for key in [SENTINEL, 'executor_actor_id', 'authorized', 'owner']:
            value = document(command)
            (value if location is None else value[location])[key] = SENTINEL
            reject(value)


@pytest.mark.parametrize('field,values', [
    ('schema_version', [True, False, 1.0, '1', 0, 2, None]),
    ('operation_id', [None, 1, True, '00000000-0000-0000-0000-000000000000', UUID.replace('-', ''), '{'+UUID+'}', 'urn:uuid:'+UUID]),
    ('command', [None, [], 'membership.join_owner', SENTINEL]),
    ('scope', [None, [], {'kind': 'platform', 'org_id': UUID}, {'kind': 'organization'}, {'kind': SENTINEL}]),
    ('payload', [None, [], SENTINEL]),
    ('reason_code', [None, True, SENTINEL, 'a'*129, 'é']),
])
def test_envelope_scalar_and_scope_rejection(field, values):
    for item in values:
        value = document(); value[field] = item; reject(value)


@pytest.mark.parametrize('reason', ['initial_setup', 'synthetic_fixture', 'identity_adoption', 'access_change', 'setup_correction'])
def test_closed_reasons(reason):
    value = document(); value['reason_code'] = reason
    assert operator.parse_command(encode(value)).reason_code == reason


@pytest.mark.parametrize('command', ['actor.register_system', 'account_actor.ensure', 'membership.join', 'membership.retire'])
def test_payload_types_uuid_and_exact_scope(command):
    value = document(command)
    value['scope'] = {'kind': 'platform'} if command.startswith('membership.') else {'kind': 'organization', 'org_id': UUID}
    reject(value)
    original = document(command)
    for key in original['payload']:
        invalid = [None, [], 1, False] if key.endswith('_id') else [None, [], 1]
        if key == 'expected_previous_membership_id': invalid.remove(None)
        if key == 'expected_absent': invalid += [False, 'true']
        if key == 'kind': invalid += ['account', 'SYSTEM']
        for item in invalid:
            value = document(command); value['payload'][key] = item; reject(value)
    if command.startswith('membership.'):
        value = document(command); value['scope']['org_id'] = '00000000-0000-0000-0000-000000000000'; reject(value)


@pytest.mark.parametrize('command,key', [('membership.join', 'expected_previous_membership_id'), ('membership.retire', 'membership_id'), ('membership.retire', 'expected_revision')])
def test_bigint_decimal_boundaries(command, key):
    for accepted in ['1', MAX]:
        value = document(command); value['payload'][key] = accepted
        assert getattr(operator.parse_command(encode(value)).payload, key) == accepted
    for invalid in ['0', '01', '-1', '+1', '1.0', ' 1', '1 ', '١', str(int(MAX)+1), '1'*20, 1, True]:
        value = document(command); value['payload'][key] = invalid; reject(value)


@pytest.mark.parametrize('command,key,accepted,rejected', [
    ('actor.register_system', 'actor_key', ['a', 'a'+'0_.:-'*25+'zz', 'a'*128], ['', 'A', 'a'*129, 'a/b', 'é', 'a\n']),
    ('actor.register_system', 'display_name', ['a', 'é'*200, 'e\u0301 🙂', '\x1ca', '\x1c', '\u200b'], ['', 'a'*201, WHITE_SPACE]),
    ('account_actor.ensure', 'display_name', ['a', 'é'*200, 'e\u0301 🙂', '\x1ca', '\x1c', '\u200b'], ['', 'a'*201, WHITE_SPACE]),
])
def test_actor_text_boundaries_and_unicode_preservation(command, key, accepted, rejected):
    for item in accepted:
        value = document(command); value['payload'][key] = item
        assert getattr(operator.parse_command(encode(value)).payload, key) == item
    for item in rejected:
        value = document(command); value['payload'][key] = item; reject(value)
    value = document(); value['payload']['kind'] = 'service'
    assert operator.parse_command(encode(value)).payload.kind == 'service'


@pytest.mark.parametrize('item', [None, '', 'https://private', 'id?token=private', 'a'*257, '/a', 'é', 'a b'])
def test_evidence_lexical_rejection(item):
    value = document(); value['evidence_ref'] = item; reject(value)


def test_evidence_required_only_for_ensure_and_max_identifier():
    for command in ['actor.register_system', 'membership.join', 'membership.retire']:
        value = document(command); del value['evidence_ref']
        assert operator.parse_command(encode(value)).evidence_ref is None
    value = document('account_actor.ensure'); del value['evidence_ref']; reject(value)
    value = document(); value['evidence_ref'] = 'A'+'_.:/-'*51
    assert len(operator.parse_command(encode(value)).evidence_ref) == 256


@pytest.mark.parametrize('invalid', [0, 1, 'true', None, []])
def test_owner_requires_boolean(invalid):
    value = document('membership.join'); value['payload']['is_owner'] = invalid; reject(value)


@pytest.mark.parametrize('body', [b'\xff', b'\xef\xbb\xbf{}', b'[]', b'null', b'{', b'{} trailing', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}', b'{"x":1e9999}', b'{"x":'+b'9'*5000+b'}', b'['*2000+b']'*2000])
def test_decoder_failures_are_safe(body):
    reject(body)


def test_forbidden_codepoints_anywhere():
    for forbidden in ['\x00', '\ud800', '\udfff']:
        for key in ['display_name', 'actor_key']:
            value = document(); value['payload'][key] = SENTINEL+forbidden; reject(value)
        value = document(); value[SENTINEL+forbidden] = 'value'; reject(value)


def test_exact_utf8_body_byte_boundary():
    value = document(); value['payload']['display_name'] = '🙂'
    raw = json.dumps(value, ensure_ascii=False).encode('utf-8')
    assert operator.parse_command(raw+b' '*(65536-len(raw))).payload.display_name == '🙂'
    reject(raw+b' '*(65537-len(raw)))


def test_error_repr_and_command_repr_do_not_expose_submitted_values():
    value = document(); value['payload']['display_name'] = SENTINEL
    parsed = operator.parse_command(encode(value))
    assert SENTINEL not in repr(parsed) and SENTINEL not in repr(parsed.payload)
    reject(encode(value)+SENTINEL.encode())


@pytest.mark.parametrize('command,key', [('actor.register_system', 'actor_id'), ('account_actor.ensure', 'account_id'), ('account_actor.ensure', 'actor_id'), ('membership.join', 'account_id'), ('membership.retire', 'account_id')])
def test_all_payload_uuids_reject_aliases_and_nil(command, key):
    for invalid in ['00000000-0000-0000-0000-000000000000', UUID.replace('-', ''), '{'+UUID+'}', 'urn:uuid:'+UUID, 'g'+UUID[1:], UUID+'\\n']:
        value = document(command); value['payload'][key] = invalid; reject(value)


def test_invalid_decoding_does_not_chain_unsafe_decoder_exception():
    for body in [b'{"'+SENTINEL.encode()+b'":', SENTINEL.encode()+b'\xff']:
        with pytest.raises(operator.CommandValidationError) as caught:
            operator.parse_command(body)
        assert caught.value.__context__ is None
        assert caught.value.__cause__ is None


@pytest.mark.parametrize('command', ['actor.register_system', 'account_actor.ensure', 'membership.join', 'membership.retire'])
@pytest.mark.parametrize('level,key', [(None, 'operation_id'), ('scope', 'kind'), ('payload', 'account_id')])
@pytest.mark.parametrize('escaped', [False, True])
def test_duplicate_fields_rejected_in_otherwise_complete_commands(command, level, key, escaped):
    value = document(command)
    if level == 'payload' and command == 'actor.register_system':
        key = 'actor_id'
    target = value if level is None else value[level]
    raw = encode(value)
    assert operator.parse_command(raw).command == command
    alias = '"'+key[:-1]+'\\u'+format(ord(key[-1]), '04x')+'"' if escaped else json.dumps(key)
    token = (json.dumps(key)+': ').encode()
    duplicate = (alias+': '+json.dumps(target[key])+', ').encode()
    encoded_target = encode(target)
    assert encoded_target.count(token) == 1
    assert raw.count(encoded_target) == 1
    reject(raw.replace(encoded_target, encoded_target.replace(token, duplicate+token, 1), 1))


@pytest.mark.parametrize('number', [b'NaN', b'Infinity', b'-Infinity', b'1e9999', b'9'*20, b'9'*5000])
def test_decoder_itself_rejects_nonfinite_and_oversized_integers(number):
    # Directly observe decoding, independently of the closed envelope validator.
    assert operator._decode(b'{"number":1}') == {'number': 1}
    with pytest.raises(operator.CommandValidationError) as caught:
        operator._decode(b'{"number":'+number+b'}')
    assert str(caught.value) == 'identity_operator_input_invalid'
    assert caught.value.__context__ is None


@pytest.mark.parametrize('body', ['{}', bytearray(b'{}'), memoryview(b'{}'), None])
def test_public_boundary_rejects_nonbytes_without_encoding(body):
    with pytest.raises(operator.CommandValidationError) as caught:
        operator.parse_command(body)
    assert str(caught.value) == 'identity_operator_input_invalid'
    assert caught.value.code == 'identity_operator_input_invalid'
    assert repr(body) not in repr(caught.value)


@pytest.mark.parametrize('command', ['membership.join', 'membership.retire'])
@pytest.mark.parametrize('invalid', [None, True, 1, [], {}, '', '00000000-0000-0000-0000-000000000000', UUID.replace('-', ''), '{'+UUID+'}', 'urn:uuid:'+UUID, 'g'+UUID[1:], UUID+' ', UUID+'\n'])
def test_organization_scope_rejects_uuid_aliases_malformed_and_nonstring(command, invalid):
    value = document(command); value['scope']['org_id'] = invalid; reject(value)
