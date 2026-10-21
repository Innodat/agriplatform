"""Organization grant assignment is typed input, with execution still closed."""
from dataclasses import FrozenInstanceError, fields
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import access_operator_input as operator
import test_access_operator_input as shared

NAME = 'grant.assign'
ORG = 'B2345678-2345-2345-2345-23456789ABCD'
ACCOUNT = 'C3456789-3456-4345-8345-3456789ABCDE'
encode, reject = shared.encode, shared.reject


def document(variant='create'):
    value = shared.document()
    value.update(command=NAME, scope=dict(kind='organization', org_id=ORG))
    value['payload'] = dict(account_id=ACCOUNT, membership_id='1', permission='fixture.read:*')
    value['payload'].update({'expected_absent': True} if variant == 'create' else {'expected_revision': '1'})
    return value


@pytest.mark.parametrize('variant,revision', [('create', None), ('update', '1'), ('update', '9007199254740993'), ('update', '9223372036854775807')])
@pytest.mark.parametrize('membership', ['1', '9007199254740993', '9223372036854775807'])
@pytest.mark.parametrize('permission', ['a', 'a'*200, 'literal:*\t\n\x01\x7f', ' leading', 'trailing ', ' \t\n'])
def test_exact_frozen_redacted_variants(variant, revision, membership, permission):
    value = document(variant)
    value['payload'].update(membership_id=membership, permission=permission)
    if revision is not None:
        value['payload']['expected_revision'] = revision
    parsed = operator.parse_command(encode(value))
    assert type(parsed) is operator.AssignGrantCommand
    assert type(parsed.scope) is operator.OrganizationScope
    assert type(parsed.payload) is (operator.CreateGrantAssignmentPayload if variant == 'create' else operator.UpdateGrantAssignmentPayload)
    for record, wire in ((parsed.scope, value['scope']), (parsed.payload, value['payload'])):
        assert {f.name for f in fields(record)} == wire.keys()
        for key, expected in wire.items():
            assert getattr(record, key) == expected
            assert type(getattr(record, key)) is type(expected)
    for key in ('schema_version', 'operation_id', 'command', 'reason_code', 'evidence_ref'):
        assert getattr(parsed, key) == value[key]
    for record in (parsed, parsed.scope, parsed.payload):
        assert repr(record) == object.__repr__(record)
        for field in fields(record):
            with pytest.raises(FrozenInstanceError):
                setattr(record, field.name, None)


@pytest.mark.parametrize('variant', ['create', 'update'])
def test_expected_state_is_exclusive_by_presence(variant):
    for other in (None, False, True, '1'):
        value = document(variant)
        value['payload']['expected_revision' if variant == 'create' else 'expected_absent'] = other
        reject(encode(value))
    value = document(variant)
    del value['payload']['expected_absent' if variant == 'create' else 'expected_revision']
    reject(encode(value))


@pytest.mark.parametrize('variant', ['create', 'update'])
def test_invalid_values_and_scope_never_coerce(variant):
    invalid_uuid = [None, True, 1, [], {}, '', '00000000-0000-0000-0000-000000000000', ACCOUNT.replace('-', ''), '{'+ACCOUNT+'}', 'urn:uuid:'+ACCOUNT, ACCOUNT+'\n']
    invalid_decimal = [None, True, False, 1, 1.0, [], {}, '', '0', '00', '01', '+1', '-1', ' 1', '1 ', '1\n', '١', '１', '9223372036854775808', '9'*20, '9'*5000]
    invalids = dict(account_id=invalid_uuid, membership_id=invalid_decimal,
                    permission=[None, True, 1, [], {}, '', 'x'*201, 'é', '\u0080'])
    invalids.update(expected_absent=[None, False, 0, 1, 1.0, 'true', [], {}] if variant == 'create' else [])
    if variant == 'update':
        del invalids['expected_absent']
        invalids['expected_revision'] = invalid_decimal
    for key, values in invalids.items():
        for invalid in values:
            value = document(variant); value['payload'][key] = invalid
            reject(encode(value))
    for invalid in invalid_uuid:
        value = document(variant); value['scope']['org_id'] = invalid
        reject(encode(value))
    for invalid in (None, [], {}, 'organization', {'kind':'platform'}, {'kind':'account'}, {'kind':'organization'}, {'kind':'platform','org_id':ORG}, {'kind':True,'org_id':ORG}):
        value = document(variant); value['scope'] = invalid
        reject(encode(value))
    value = document(variant)
    value['payload']['account_id'] = ACCOUNT.lower(); value['scope']['org_id'] = ORG.lower()
    parsed = operator.parse_command(encode(value))
    assert parsed.payload.account_id == ACCOUNT.lower() and parsed.scope.org_id == ORG.lower()


@pytest.mark.parametrize('variant', ['create', 'update'])
@pytest.mark.parametrize('level', [None, 'scope', 'payload'])
def test_closed_fields_and_duplicate_aliases(variant, level):
    original = document(variant); target = original if level is None else original[level]
    for key in target:
        value = document(variant); del (value if level is None else value[level])[key]
        if key == 'evidence_ref':
            assert operator.parse_command(encode(value)).evidence_ref is None
        else:
            reject(encode(value))
        token = (json.dumps(key)+': ').encode(); encoded = encode(target)
        for alias in (json.dumps(key), '"'+key[:-1]+'\\u'+format(ord(key[-1]), '04x')+'"'):
            duplicate = (alias+': '+json.dumps(target[key])+', ').encode()
            reject(encode(original).replace(encoded, encoded.replace(token, duplicate+token, 1), 1))
    for key in ('app_id', 'org_id', 'grant_id', 'actor_id', 'executor_actor_id', 'authorized', shared.SENTINEL):
        if key in target:
            continue
        value = document(variant); (value if level is None else value[level])[key] = shared.SENTINEL
        reject(encode(value))


@pytest.mark.parametrize('variant', ['create', 'update'])
def test_shared_strict_decoder_envelope_and_provenance(variant, monkeypatch):
    original = document(variant)
    monkeypatch.setattr(shared, 'document', lambda command=None: json.loads(json.dumps(original)))
    for field, values in [('schema_version', [True, '1', 1.0, 0, 2, None]),
                          ('command', [None, True, 'grant.revoke', 'account_grant.assign']),
                          ('payload', [None, [], True]), ('reason_code', [None, '', 'unknown', 'é'])]:
        shared.test_envelope_rejections(field, values)
    shared.test_provenance_uses_identity_closed_semantics(NAME)
    for forbidden in ('\x00', '\ud800', '\udfff'):
        shared.test_forbidden_text_anywhere(forbidden)
        shared.test_reused_decoder_checks_nested_keys_lists_and_values(forbidden)
    for body in (b'\xff', b'\xef\xbb\xbf{}', b'[]', b'null', b'{', b'{} trailing', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e9999}', b'{"x":'+b'9'*5000+b'}', b'['*2000+b']'*2000, '{}', bytearray(b'{}'), memoryview(b'{}'), None, 1):
        shared.test_decoder_and_nonbytes_fail_safely(body)
    raw = encode(original)
    assert operator.parse_command(raw+b' '*(65536-len(raw))).command == NAME
    reject(raw+b' '*(65537-len(raw)))


@pytest.mark.parametrize('variant', ['create', 'update'])
def test_execution_and_lookup_refuse_before_all_effects(variant, tmp_path, monkeypatch, capsys):
    import access_operator as access
    import identity_operator as identity
    import operator_cli as cli
    original = document(variant); raw = encode(original)
    assert operator.parse_command(raw).command == NAME
    class Trap:
        def __getattr__(self, name):
            pytest.fail('unsupported assignment touched a connection')
    def trap(*args, **kwargs):
        pytest.fail('unsupported assignment touched target/connection/dispatch')
    monkeypatch.setattr(access, '_run', trap)
    monkeypatch.setattr(cli, 'load_target', trap)
    monkeypatch.setattr(cli, '_connection', trap)
    monkeypatch.setattr(cli, 'dispatch', trap)
    with pytest.raises(access.OperatorError) as caught:
        access.execute(Trap(), raw)
    shared.assert_safe_refusal(caught.value, 'command_unsupported')
    for adapter in (access, identity):
        outcome_kwargs = {'app_id':'fixture_app'} if adapter is access else {}
        with pytest.raises(adapter.OperatorError) as caught:
            adapter.outcome(Trap(), shared.UUID, command=NAME, **outcome_kwargs)
        shared.assert_safe_refusal(caught.value, 'command_invalid')
    monkeypatch.setattr(shared, 'document', lambda command=None: original.copy())
    shared.test_identity_parser_adapter_cli_refuse_before_effects(NAME, tmp_path, monkeypatch, capsys)
    with pytest.raises(cli.CommandValidationError) as caught:
        cli.worker(['execute', 'unused', raw.decode(), shared.UUID])
    shared.assert_safe_refusal(caught.value, 'identity_operator_input_invalid')
    with pytest.raises(ValueError) as caught:
        cli.worker(['outcome', 'unused', dict(command=NAME, org_id=ORG, account_id=ACCOUNT), shared.UUID])
    assert type(caught.value) is ValueError and caught.value.args == ()
    assert caught.value.__context__ is None and caught.value.__cause__ is None
    for worker in (cli.access_worker, cli.worker):
        with pytest.raises(ValueError) as caught:
            worker(['execute', 'unused', raw.decode(), shared.UUID, 'access'])
        assert type(caught.value) is ValueError and caught.value.args == ()
        assert caught.value.__context__ is None and caught.value.__cause__ is None
        with pytest.raises(ValueError) as caught:
            worker(['outcome', 'unused', dict(command=NAME, org_id=ORG, account_id=ACCOUNT, membership_id='1', permission='fixture.read:*'), shared.UUID, 'access'])
        assert caught.value.args == () and caught.value.__context__ is None
    for owner in ('access', 'identity'):
        assert cli.main(['outcome', '--owner', owner, '--target', 'unused', '--command', NAME, '--operation-id', shared.UUID,
                         *(['--app-id', 'fixture_app'] if owner == 'access' else [])]) == 2
        output = capsys.readouterr()
        assert json.loads(output.out) == dict(code='command_invalid') and output.err == ''
