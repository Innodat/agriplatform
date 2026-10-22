"""Revocation input preserves an exact historical binding without enabling writes."""
from dataclasses import FrozenInstanceError, fields
import json
from pathlib import Path
import sys
import traceback

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import access_operator_input as operator
import test_access_operator_input as shared

NAME = 'grant.revoke'
ORG = 'B2345678-2345-2345-2345-23456789ABCD'
ACCOUNT = 'C3456789-3456-4345-8345-3456789ABCDE'
encode, reject = shared.encode, shared.reject


def document():
    value = shared.document()
    value.update(command=NAME, scope=dict(kind='organization', org_id=ORG))
    value['payload'] = dict(grant_id='opaque:legacy grant', account_id=ACCOUNT,
                            membership_id='1', permission='fixture.read:*', expected_revision='1')
    return value


@pytest.mark.parametrize('grant_id', ['', 'opaque:legacy grant', ' retained é🙂\t\n ', '00000000-0000-0000-0000-000000000000', 'x'*10000])
@pytest.mark.parametrize('membership', ['1', '9007199254740993', '9223372036854775807'])
@pytest.mark.parametrize('revision', ['1', '9223372036854775807'])
@pytest.mark.parametrize('permission', ['a', 'a'*200, 'literal:"\\\t\n\x01\x7f', ' \t\n'])
def test_exact_binding_is_preserved_frozen_and_redacted(grant_id, membership, revision, permission):
    value = document()
    value['payload'].update(grant_id=grant_id, membership_id=membership,
                            expected_revision=revision, permission=permission)
    parsed = operator.parse_command(encode(value))
    assert type(parsed) is operator.RevokeGrantCommand
    assert type(parsed.payload) is operator.GrantRevocationPayload
    assert type(parsed.scope) is operator.OrganizationScope
    for record, wire in ((parsed.scope, value['scope']), (parsed.payload, value['payload'])):
        assert {f.name for f in fields(record)} == wire.keys()
        for key, expected in wire.items():
            assert getattr(record, key) == expected and type(getattr(record, key)) is type(expected)
    for key in ('schema_version', 'operation_id', 'command', 'reason_code', 'evidence_ref'):
        assert getattr(parsed, key) == value[key]
    for record in (parsed, parsed.scope, parsed.payload):
        assert repr(record) == object.__repr__(record)
        for field in fields(record):
            with pytest.raises(FrozenInstanceError):
                setattr(record, field.name, None)


def test_typed_identifiers_and_expected_revision_never_coerce():
    invalid_uuid = [None, True, 1, [], {}, '', '00000000-0000-0000-0000-000000000000', ACCOUNT.replace('-', ''), '{'+ACCOUNT+'}', 'urn:uuid:'+ACCOUNT, ACCOUNT+'\n']
    invalid_decimal = [None, True, False, 1, 1.0, [], {}, '', '0', '00', '01', '+1', '-1', ' 1', '1 ', '1\n', '١', '１', '9223372036854775808', '9'*5000]
    for key, invalids in dict(grant_id=[None, True, 1, 1.0, [], {}], account_id=invalid_uuid,
            membership_id=invalid_decimal, expected_revision=invalid_decimal,
            permission=[None, True, 1, [], {}, '', 'x'*201, 'é', '\u0080']).items():
        for invalid in invalids:
            value = document(); value['payload'][key] = invalid
            reject(encode(value))
    for invalid in invalid_uuid:
        value = document(); value['scope']['org_id'] = invalid
        reject(encode(value))
    for invalid in (None, [], {}, 'organization', {'kind':'platform'}, {'kind':'account'}, {'kind':'organization'}, {'kind':'platform','org_id':ORG}, {'kind':True,'org_id':ORG}):
        value = document(); value['scope'] = invalid
        reject(encode(value))
    value = document(); value['payload']['account_id'] = ACCOUNT.lower(); value['scope']['org_id'] = ORG.lower()
    parsed = operator.parse_command(encode(value))
    assert parsed.payload.account_id == ACCOUNT.lower() and parsed.scope.org_id == ORG.lower()


@pytest.mark.parametrize('level', [None, 'scope', 'payload'])
def test_closed_fields_missing_duplicate_and_escaped_aliases(level):
    original = document(); target = original if level is None else original[level]
    for key in target:
        value = document(); del (value if level is None else value[level])[key]
        if key == 'evidence_ref':
            assert operator.parse_command(encode(value)).evidence_ref is None
        else:
            reject(encode(value))
        token = (json.dumps(key)+': ').encode(); encoded = encode(target)
        for alias in (json.dumps(key), '"'+key[:-1]+'\\u'+format(ord(key[-1]), '04x')+'"'):
            duplicate = (alias+': '+json.dumps(target[key])+', ').encode()
            reject(encode(original).replace(encoded, encoded.replace(token, duplicate+token, 1), 1))
    for key in ('expected_absent', 'app_id', 'org_id', 'grant_id', 'actor_id', 'executor_actor_id', 'authorized', shared.SENTINEL):
        if key in target:
            continue
        for extra in (None, False, True, shared.SENTINEL):
            value = document(); (value if level is None else value[level])[key] = extra
            reject(encode(value))


def test_decoder_envelope_provenance_and_forbidden_grant_text(monkeypatch):
    original = document()
    monkeypatch.setattr(shared, 'document', lambda command=None: json.loads(json.dumps(original)))
    for field, values in [('schema_version', [True, '1', 1.0, 0, 2, None]),
            ('operation_id', [None, True, '', '00000000-0000-0000-0000-000000000000']),
            ('command', [None, True, 'account_grant.revoke', 'grant.assign']),
            ('payload', [None, [], True]), ('reason_code', [None, '', 'unknown', 'é'])]:
        shared.test_envelope_rejections(field, values)
    shared.test_provenance_uses_identity_closed_semantics(NAME)
    for forbidden in ('\x00', '\ud800', '\udfff'):
        value = document(); value['payload']['grant_id'] = shared.SENTINEL+forbidden
        reject(encode(value))
        shared.test_forbidden_text_anywhere(forbidden)
        shared.test_reused_decoder_checks_nested_keys_lists_and_values(forbidden)
    for body in (b'\xff', b'\xef\xbb\xbf{}', b'[]', b'null', b'{', b'{} trailing', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e9999}', b'{"x":'+b'9'*5000+b'}', b'['*2000+b']'*2000, '{}', bytearray(b'{}'), memoryview(b'{}'), None, 1):
        shared.test_decoder_and_nonbytes_fail_safely(body)
    raw = encode(original)
    assert operator.parse_command(raw+b' '*(65536-len(raw))).command == NAME
    reject(raw+b' '*(65537-len(raw)))


def test_raw_utf8_opaque_id_exact_body_byte_boundary():
    value = document(); value['payload']['grant_id'] = ' retained é🙂\t '
    raw = json.dumps(value, ensure_ascii=False).encode('utf-8')
    assert operator.parse_command(raw).payload.grant_id == value['payload']['grant_id']
    value['payload']['grant_id'] = ''
    overhead = len(json.dumps(value, ensure_ascii=False).encode('utf-8'))
    available = 65536-overhead
    grant_id = 'é'*(available//2)+'x'*(available%2)
    value['payload']['grant_id'] = grant_id
    raw = json.dumps(value, ensure_ascii=False).encode('utf-8')
    assert len(raw) == 65536 and len(raw.decode('utf-8')) < 65536
    assert operator.parse_command(raw).payload.grant_id == grant_id
    value['payload']['grant_id'] += 'x'
    oversized = json.dumps(value, ensure_ascii=False).encode('utf-8')
    assert len(oversized) == 65537
    reject(oversized)


@pytest.mark.parametrize('grant_id', ['', ' retained é🙂\t ', 'x'*10000, 'PRIVATE_REVOKE_GRANT_SENTINEL'])
def test_identity_remains_closed_and_malformed_access_lookup_refuses_before_io(grant_id, tmp_path, monkeypatch, capsys):
    import access_operator as access
    import identity_operator as identity
    import operator_cli as cli
    original = document(); original['payload']['grant_id'] = grant_id; raw = encode(original)
    assert operator.parse_command(raw).command == NAME
    class Trap:
        def __getattr__(self, name):
            pytest.fail('unsupported revocation touched a connection')
    def trap(*args, **kwargs):
        pytest.fail('unsupported revocation touched target/connection/dispatch')
    def safe(error, code):
        shared.assert_safe_refusal(error, code)
        rendered = str(error)+repr(error)+''.join(traceback.format_exception(error))
        assert 'PRIVATE_REVOKE_GRANT_SENTINEL' not in rendered
        if grant_id:
            assert grant_id not in rendered
    monkeypatch.setattr(access, '_run', trap)
    monkeypatch.setattr(cli, 'load_target', trap)
    monkeypatch.setattr(cli, '_connection', trap)
    monkeypatch.setattr(cli, 'dispatch', trap)
    with pytest.raises(cli.CommandValidationError) as caught:
        identity.execute(Trap(), raw)
    safe(caught.value, 'identity_operator_input_invalid')
    for adapter in (access, identity):
        kwargs = dict(app_id='fixture_app', permission='fixture.read:*', org_id=ORG) if adapter is access else {}
        with pytest.raises(adapter.OperatorError) as caught:
            adapter.outcome(Trap(), shared.UUID, command=NAME, **kwargs)
        safe(caught.value, 'command_invalid')
    for worker in (cli.access_worker, cli.worker):
        for action, value in [('outcome', dict(command=NAME, org_id=ORG, account_id=ACCOUNT, membership_id='1', permission='fixture.read:*'))]:
            with pytest.raises(ValueError) as caught:
                worker([action, 'unused', value, shared.UUID, 'access'])
            assert type(caught.value) is ValueError and caught.value.args == ()
            assert caught.value.__context__ is None and caught.value.__cause__ is None
            assert 'PRIVATE_REVOKE_GRANT_SENTINEL' not in ''.join(traceback.format_exception(caught.value))
    monkeypatch.setattr(shared, 'document', lambda command=None: json.loads(json.dumps(original)))
    path = tmp_path/'revoke-sensitive.json'; path.write_bytes(raw)
    for owner in ('identity',):
        assert cli.main(['execute','--owner',owner,'--target','unused','--command-file',str(path)]) == 2
        output = capsys.readouterr()
        expected = (dict(code='command_unsupported',operation_id=shared.UUID.lower()) if owner == 'access' else dict(code='identity_operator_input_invalid'))
        assert json.loads(output.out) == expected and output.err == ''
        assert 'PRIVATE_REVOKE_GRANT_SENTINEL' not in output.out
        if grant_id:
            assert grant_id not in output.out
        flags = ['--app-id','fixture_app','--permission','fixture.read:*','--org-id',ORG] if owner == 'access' else []
        assert cli.main(['outcome','--owner',owner,'--target','unused','--command',NAME,'--operation-id',shared.UUID,*flags]) == 2
        output = capsys.readouterr()
        assert json.loads(output.out) == dict(code='command_invalid') and output.err == ''
