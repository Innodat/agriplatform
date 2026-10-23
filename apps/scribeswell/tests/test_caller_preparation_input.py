"""Preparation declarations are parsed, never admitted or executed."""
from dataclasses import FrozenInstanceError, asdict, fields
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
# Explicit trusted namespace root, independent of other tests' migration paths.
sys.path.insert(0, str(ROOT))

# Literal wire oracle: not constructed by the production parser or serializer.
VALID = b'''{"schema_version":1,"command":"caller.prepare_initial",
"run_id":"11111111-1111-4111-8111-111111111111",
"custody":{"schema_version":1,"source_id":"tanakh",
"executor_actor_id":"22222222-2222-4222-8222-222222222222",
"actor_kind":"service","actor_key":"fixture.controller",
"preparation_evidence_ref":"fixture:preparation"},
"preparer_actor_id":"33333333-3333-4333-8333-333333333333",
"target_plan_ref":"fixture:target","identity_observation_ref":"fixture:identity",
"session_authorization_ref":"fixture:session","release_binding_ref":"fixture:release"}'''


def test_closed_request_returns_exact_immutable_declaration():
    from apps.scribeswell.backend.caller_preparation_input import parse_preparation_request
    result = parse_preparation_request(VALID)
    assert asdict(result) == json.loads(VALID)
    assert result.command == 'caller.prepare_initial'
    assert result.custody.actor_kind == 'service'
    with pytest.raises(FrozenInstanceError):
        result.run_id = 'changed'
    with pytest.raises(FrozenInstanceError):
        result.custody.actor_key = 'changed'
    for value in (result, result.custody):
        assert not hasattr(value, '__dict__')
        assert all(not isinstance(getattr(value, field.name), (dict, list)) for field in fields(value))
        assert 'fixture:' not in repr(value) and '22222222' not in repr(value)


def encode(body):
    return json.dumps(body, ensure_ascii=False, separators=(',', ':')).encode()


def reject(raw):
    from apps.scribeswell.backend.caller_preparation_input import PreparationRequestError, parse_preparation_request
    with pytest.raises(PreparationRequestError) as failure:
        parse_preparation_request(raw)
    error = failure.value
    assert error.code == str(error) == 'scribeswell_preparation_request_invalid'
    assert error.args == (error.code,)
    assert error.__cause__ is None and error.__context__ is None
    assert 'private-marker' not in repr(error)


@pytest.mark.parametrize('raw', [None, '', VALID.decode(), bytearray(VALID), memoryview(VALID), {}, [], True, 1])
def test_bytes_only(raw):
    reject(raw)


def test_bytes_subclass_not_accepted():
    class OtherBytes(bytes):
        pass
    reject(OtherBytes(VALID))


@pytest.mark.parametrize('raw', [b'', b' \r\n\t', b'\xef\xbb\xbf'+VALID, b'\xff', b'\xc0\xaf',
    b'\xed\xa0\x80', b'{"private-marker":', b'null', b'[]', b'true', b'1',
    b'"private-marker"', VALID+b'{}', VALID+b' private-marker', VALID[:-1],
    VALID.replace(b'"source_id":"tanakh"', b'"source_id":"private-marker\x00"')])
def test_encoding_framing_and_root_object(raw):
    reject(raw)


def test_exact_byte_budget_and_allowed_json_whitespace():
    from apps.scribeswell.backend.caller_preparation_input import parse_preparation_request
    at_limit = VALID + b' '*(8192-len(VALID))
    assert parse_preparation_request(at_limit) == parse_preparation_request(VALID)
    assert parse_preparation_request(b'\r\n\t '+VALID+b'\r\n') == parse_preparation_request(VALID)
    reject(at_limit+b' ')
    reject(b' '*8193)


@pytest.mark.parametrize('key', list(json.loads(VALID)))
def test_every_root_field_required(key):
    value = json.loads(VALID)
    del value[key]
    reject(encode(value))


@pytest.mark.parametrize('key', ['enabled','timeout','verified','database_url','organization','sql','private-marker'])
def test_extra_fields_do_not_expand_request(key):
    reject(encode(json.loads(VALID) | {key: 'private-marker'}))


@pytest.mark.parametrize('key', ['schema_version','command','run_id','preparer_actor_id',
    'target_plan_ref','identity_observation_ref','session_authorization_ref','release_binding_ref'])
@pytest.mark.parametrize('bad', [None, True, 1.0, [], {}])
def test_root_scalar_types_are_exact(key, bad):
    reject(encode(json.loads(VALID) | {key: bad}))


@pytest.mark.parametrize('bad', [None, True, 1, [], 'private-marker'])
def test_custody_requires_object(bad):
    reject(encode(json.loads(VALID) | {'custody': bad}))


@pytest.mark.parametrize('key', ['run_id','preparer_actor_id'])
@pytest.mark.parametrize('bad', ['', '00000000-0000-0000-0000-000000000000',
    'ABCDEFAB-1234-1234-1234-123456789ABC', '11111111111141118111111111111111',
    '{11111111-1111-4111-8111-111111111111}', 'urn:uuid:11111111-1111-4111-8111-111111111111',
    '11111111-1111-4111-8111-111111111111\n', 4, False])
def test_uuid_spelling_and_identity(key, bad):
    reject(encode(json.loads(VALID) | {key: bad}))


@pytest.mark.parametrize('key', ['target_plan_ref','identity_observation_ref','session_authorization_ref','release_binding_ref'])
@pytest.mark.parametrize('bad', ['', 'a'*257, '/relative', 'private-marker secret', 'a\n', 'a?token=x', 'a#fragment', 'é', '\ud800'])
def test_reference_boundaries(key, bad):
    # ensure_ascii preserves escaped lone surrogates as JSON wire input.
    reject(json.dumps(json.loads(VALID) | {key: bad}).encode())


@pytest.mark.parametrize('key', ['target_plan_ref','identity_observation_ref','session_authorization_ref','release_binding_ref'])
@pytest.mark.parametrize('good', ['a', 'A'*256, 'file:/private-marker/a_b.c-d:7'])
def test_reference_syntax_does_not_authenticate_or_open_it(key, good):
    from apps.scribeswell.backend.caller_preparation_input import parse_preparation_request
    result = parse_preparation_request(encode(json.loads(VALID) | {key: good}))
    assert getattr(result, key) == good


@pytest.mark.parametrize('raw', [
    VALID.replace(b'"schema_version":1',b'"schema_version":1,"schema_version":1',1),
    VALID.replace(b'"schema_version":1',b'"schema_version":1,"\\u0073chema_version":1',1),
    VALID.replace(b'"source_id":"tanakh"',b'"source_id":"tanakh","source_id":"tanakh"'),
    VALID.replace(b'"source_id":"tanakh"',b'"source_id":"tanakh","\\u0073ource_id":"tanakh"'),
])
def test_duplicate_keys_even_equal_or_escaped(raw):
    reject(raw)


@pytest.mark.parametrize('number', [b'NaN', b'Infinity', b'-Infinity', b'1e999', b'-1e999', b'1.0', b'1e0', b'0', b'-1', b'2', b'9'*5000])
def test_numeric_values_are_not_coerced(number):
    reject(VALID.replace(b'"schema_version":1', b'"schema_version":'+number, 1))


@pytest.mark.parametrize('depth', [4,5,100,1000])
def test_nested_noncontract_objects_safely_reject(depth):
    # Unknown nested members remain invalid even within the generic depth ceiling.
    raw = b'{"private-marker":'+b'['*depth+b'1'+b']'*depth+b'}'
    reject(raw)


@pytest.mark.parametrize('change', [{'schema_version':True},{'schema_version':1.0},{'schema_version':2},
    {'source_id':''},{'source_id':'a'*65},{'actor_kind':'person'},{'actor_key':'Bad'},
    {'actor_key':'a'*129},{'executor_actor_id':'00000000-0000-0000-0000-000000000000'},
    {'executor_actor_id':'ABCDEFAB-1234-1234-1234-123456789ABC'},
    {'preparation_evidence_ref':'a'*257},{'preparation_evidence_ref':'a?secret=private-marker'},
    {'extra':'private-marker'}])
def test_custody_keeps_existing_semantics(change):
    value = json.loads(VALID)
    value['custody'].update(change)
    reject(encode(value))


@pytest.mark.parametrize('missing', list(json.loads(VALID)['custody']))
def test_each_custody_field_required(missing):
    value = json.loads(VALID)
    del value['custody'][missing]
    reject(encode(value))


def test_same_actor_is_two_declarations_not_authority():
    from apps.scribeswell.backend.caller_preparation_input import parse_preparation_request
    value = json.loads(VALID)
    value['preparer_actor_id'] = value['custody']['executor_actor_id']
    result = parse_preparation_request(encode(value))
    assert result.preparer_actor_id == result.custody.executor_actor_id
    assert not hasattr(result, 'verified') and not hasattr(result, 'authorized')


def test_custody_result_agrees_with_unchanged_validator_and_digest():
    from apps.scribeswell.backend.caller_preparation_input import parse_preparation_request
    from apps.scribeswell.migrations.release_profile import validate_custody, evidence
    value = json.loads(VALID)
    value['custody'].update(source_id='s'*64, actor_key='a'*128, preparation_evidence_ref='r'*256)
    result = parse_preparation_request(encode(value))
    assert asdict(result.custody) == validate_custody(value['custody'])
    selection = {'profile':'prepared-controller-v1', 'custody':asdict(result.custody)}
    assert evidence(selection) == evidence(selection | {'custody':value['custody']})


def test_fresh_standard_library_interpreter_has_no_runtime_side_effects(tmp_path):
    import subprocess
    script = r'''
import builtins, dataclasses, hashlib, json, math, re, sys, typing, uuid, os
raw = sys.stdin.buffer.read()
sys.path.insert(0, sys.argv[1])
paths = list(sys.path)
original = builtins.__import__
def guarded(name, *args, **kwargs):
    app_modules = {'apps', 'apps.scribeswell', 'apps.scribeswell.backend',
        'apps.scribeswell.backend.caller_preparation_input', 'apps.scribeswell.migrations',
        'apps.scribeswell.migrations.release_profile'}
    assert name.split('.')[0] in sys.stdlib_module_names or name in app_modules
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
def forbidden(*args, **kwargs):
    raise AssertionError('unexpected side effect')
os.getenv = forbidden
class ForbiddenEnvironment:
    __getitem__ = __iter__ = __contains__ = __len__ = get = items = keys = values = copy = forbidden
os.environ = ForbiddenEnvironment()
import apps.scribeswell.backend.caller_preparation_input as module
assert sys.path == paths
# Normal Python module loading is allowed; parsing may not perform explicit I/O.
builtins.open = forbidden
def audit(event, args):
    if event == 'open' or event.startswith(('socket.','subprocess.','os.putenv','os.listdir','os.scandir')):
        forbidden()
sys.addaudithook(audit)
result = module.parse_preparation_request(raw)
assert result.target_plan_ref == 'fixture:target'
for bad in (b'{"private-marker":', b'\xff'):
    try:
        module.parse_preparation_request(bad)
    except module.PreparationRequestError as error:
        assert error.__context__ is None and error.__cause__ is None
    else:
        raise AssertionError('invalid accepted')
assert sys.path == paths
'''
    result = subprocess.run([sys.executable,'-I','-S','-c',script,str(ROOT)], input=VALID,
                            cwd=tmp_path, env={}, capture_output=True, timeout=15)
    assert result.returncode == 0, result.stderr.decode()


@pytest.mark.parametrize('outer', ['decoder', 'ordinary'])
def test_rejection_does_not_retain_callers_active_exception(outer):
    from apps.scribeswell.backend.caller_preparation_input import parse_preparation_request, PreparationRequestError
    try:
        if outer == 'decoder':
            json.loads('private-marker submitted decoder text')
        else:
            raise RuntimeError('private-marker credentials')
    except (ValueError, RuntimeError):
        with pytest.raises(PreparationRequestError) as failure:
            parse_preparation_request(b'{')
        assert failure.value.__context__ is None
        assert failure.value.__cause__ is None


def test_generic_decoded_depth_guard_boundary_independently_of_closed_shape():
    from apps.scribeswell.backend.caller_preparation_input import _depth
    # Fixed independently counted container nesting: root is depth 1.
    _depth({'a': {'b': {'c': {}}}})
    with pytest.raises(ValueError):
        _depth({'a': {'b': {'c': {'d': {}}}}})


@pytest.mark.parametrize('command', ['', 'caller.prepare', 'caller.prepare_initial ',
    'Caller.prepare_initial', 'corpus.begin', 'caller.prepare_initial\n'])
def test_command_literal_is_closed(command):
    reject(encode(json.loads(VALID) | {'command':command}))


@pytest.mark.parametrize('key', ['run_id','preparer_actor_id'])
def test_canonical_uuid_case_for_same_hex_identity(key):
    from apps.scribeswell.backend.caller_preparation_input import parse_preparation_request
    canonical = 'abcdefab-abcd-4abc-8abc-abcdefabcdef'
    assert getattr(parse_preparation_request(encode(json.loads(VALID) | {key:canonical})), key) == canonical
    reject(encode(json.loads(VALID) | {key:canonical.upper()}))
