"""Pure publication-command qualification, without execution or authority."""
from dataclasses import FrozenInstanceError, fields, is_dataclass
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP / 'backend'))


def source_bytes():
    from corpus_source import BOOK_METADATA
    return json.dumps({m['name_en']: [[[['שָׁ/אָב', '1', 'HNcmsa']]]]
                       for m in BOOK_METADATA}, ensure_ascii=False).encode()


def command(variant='begin', source=None):
    source = source_bytes() if source is None else source
    payload = {'input': {'source_sha256': hashlib.sha256(source).hexdigest(),
                         'catalogue_version': 'catalogue-v1', 'versification_id': 'versification-v1',
                         'tokenization_version': 'tokens-v1'}}
    if variant == 'begin':
        payload['expected_absent'] = True
    else:
        payload.update(expected_generation='9223372036854775807',
                       expected_attempt_id='abcdefff-1234-1234-1234-123456789abc')
    return dict(schema_version=1, operation_id='12345678-1234-1234-1234-123456789abc',
                command='corpus.' + variant, scope=dict(kind='source', source_id='tanakh'),
                payload=payload, reason_code='source_' + ('import' if variant == 'begin' else
                            'recovery' if variant == 'recover' else 'seal'), evidence_ref='run:fixture/1')


def encode(value):
    return json.dumps(value).encode()


# Independent wire oracle: fixed catalogue order, literal source digest/labels and
# hand-assembled sorted-key compact candidate JSON. No production builder,
# serializer, source decoder or catalogue is used to construct these bytes.
SMALL_SOURCE_SHA256 = '34e30aeffcb295b3c480fa3ede23a6a694b5d7636dfd73edbee98acf2833b9e2'
SMALL_CANDIDATE_SHA256 = '1213c12da4283b80f6e2bc5cc89d4ca4dc44ed5b430b29b929d596618c8a9cb0'


def expected_small_candidate_bytes():
    books = ('Gen Exod Lev Num Deut Josh Judg 1Sam 2Sam 1Kgs 2Kgs Isa Jer Ezek '
             'Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal Ps Prov Job '
             'Song Ruth Lam Eccl Esth Dan Ezra Neh 1Chr 2Chr').split()
    verses = []
    for book in books:
        token_bytes = ('["scribeswell.verse_tokens.v1","tanakh","catalogue-v1",'
                       '"versification-v1","tokens-v1","' + book +
                       '",1,1,[[1,"שָׁ/אָב"]]]').encode('utf-8')
        digest = hashlib.sha256(token_bytes).hexdigest()
        verses.append('{"book":"' + book + '","chapter":1,"token_count":1,'
                      '"verse":1,"verse_token_digest":"' + digest + '"}')
    return ('{"catalogue_version":"catalogue-v1",'
            '"counts":{"books":39,"chapters":39,"tokens":39,"verses":39},'
            '"kind":"scribeswell.source_evidence_candidate","publication":false,'
            '"source_id":"tanakh","source_sha256":"' + SMALL_SOURCE_SHA256 + '",'
            '"tokenization_version":"tokens-v1","verses":[' + ','.join(verses) + '],'
            '"versification_id":"versification-v1","version":1}\n').encode('utf-8')


@pytest.mark.parametrize('variant', ['begin', 'recover', 'seal'])
def test_complete_source_qualifies_exact_immutable_command(variant):
    from corpus_publication_input import parse_command, prepare_command
    raw = source_bytes()
    body = command(variant, raw)
    parsed = parse_command(encode(body))
    prepared = prepare_command(encode(body), raw)
    assert hashlib.sha256(raw).hexdigest() == SMALL_SOURCE_SHA256
    for result in (parsed, prepared.command):
        assert result.schema_version == 1
        assert result.operation_id == '12345678-1234-1234-1234-123456789abc'
        assert result.command == 'corpus.' + variant
        assert result.reason_code == {'begin': 'source_import', 'recover': 'source_recovery',
                                      'seal': 'source_seal'}[variant]
        assert result.evidence_ref == 'run:fixture/1'
        assert result.scope.kind == 'source'
        assert result.scope.source_id == 'tanakh'
        assert result.payload.input.source_sha256 == SMALL_SOURCE_SHA256
        assert result.payload.input.catalogue_version == 'catalogue-v1'
        assert result.payload.input.versification_id == 'versification-v1'
        assert result.payload.input.tokenization_version == 'tokens-v1'
        if variant == 'begin':
            assert result.payload.expected_absent is True
            assert {f.name for f in fields(result.payload)} == {'input', 'expected_absent'}
        else:
            assert result.payload.expected_generation == '9223372036854775807'
            assert result.payload.expected_attempt_id == 'abcdefff-1234-1234-1234-123456789abc'
            assert result.payload.expected_attempt_id != result.operation_id
            assert {f.name for f in fields(result.payload)} == {
                'input', 'expected_generation', 'expected_attempt_id'}
    assert prepared.command == parsed
    assert {f.name for f in fields(prepared)} == {'command', 'counts', 'source_candidate_sha256'}
    assert [getattr(prepared.counts, key) for key in ('books', 'chapters', 'verses', 'tokens')] == [39]*4
    expected_bytes = expected_small_candidate_bytes()
    assert hashlib.sha256(expected_bytes).hexdigest() == SMALL_CANDIDATE_SHA256
    assert prepared.source_candidate_sha256 == SMALL_CANDIDATE_SHA256
    def check_frozen(value):
        assert is_dataclass(value)
        assert repr(value) == object.__repr__(value)
        for field in fields(value):
            original = getattr(value, field.name)
            with pytest.raises(FrozenInstanceError):
                setattr(value, field.name, None)
            if is_dataclass(original):
                check_frozen(original)
            else:
                assert isinstance(original, (str, int, bool))
                # Check each record's own values, including counts, labels, UUIDs
                # and digests, rather than only a top-level evidence marker.
                if isinstance(original, str):
                    assert original not in repr(value)
                else:
                    assert field.name + '=' not in repr(value)
    check_frozen(parsed)
    check_frozen(prepared)
    body['payload']['input']['catalogue_version'] = 'changed'
    assert parsed.payload.input.catalogue_version == 'catalogue-v1'


def assert_invalid(raw):
    from corpus_publication_input import CommandValidationError, parse_command
    with pytest.raises(CommandValidationError) as caught:
        parse_command(raw)
    exc = caught.value
    assert str(exc) == exc.code == 'corpus_publication.input_invalid'
    assert exc.__cause__ is None
    assert exc.__context__ is None
    assert 'private-marker' not in repr(exc)


@pytest.mark.parametrize('raw', [b'', b'{private-marker', b'\xffprivate-marker', b'\xef\xbb\xbf{}',
                                b'{}' + b' '*65535, b'['*2000 + b']'*2000, b'null', b'[]',
                                b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}',
                                b'{"x":1.1}', b'{"x":1e9}', b'{"x":' + b'9'*5000 + b'}',
                                {}, None, bytearray(b'{}')])
def test_bad_encoding_and_json_are_safe(raw):
    assert_invalid(raw)


@pytest.mark.parametrize('path', [(), ('scope',), ('payload',), ('payload', 'input')])
@pytest.mark.parametrize('override', ['actor_id', 'executor', 'created_at', 'ready', 'manifest', 'arbitrary'])
def test_override_rejected_at_every_boundary(path, override):
    body = command()
    target = body
    for key in path:
        target = target[key]
    target[override] = 'private-marker'
    assert_invalid(encode(body))


@pytest.mark.parametrize('path', [(), ('scope',), ('payload',), ('payload', 'input')])
def test_missing_and_duplicate_fields_at_every_boundary(path):
    body = command()
    target = body
    for key in path:
        target = target[key]
    key = next(iter(target))
    needle = json.dumps(key) + ': '
    raw = json.dumps(body)
    raw = raw.replace(needle, needle + json.dumps(target[key]) + ', ' + needle, 1)
    assert_invalid(raw.encode())
    for key in list(target):
        saved = target.pop(key)
        assert_invalid(encode(body))
        target[key] = saved


@pytest.mark.parametrize('variant', ['begin', 'recover', 'seal'])
def test_reason_pairing_and_synthetic(variant):
    from corpus_publication_input import parse_command
    body = command(variant)
    for reason in ('source_import', 'source_recovery', 'source_seal', 'synthetic_fixture', 'unknown', None):
        body['reason_code'] = reason
        if reason in (command(variant)['reason_code'], 'synthetic_fixture'):
            assert parse_command(encode(body)).reason_code == reason
        else:
            assert_invalid(encode(body))


@pytest.mark.parametrize('path,values', [
    (('schema_version',), [True, 1.0, '1', 0, 2, None]),
    (('operation_id',), ['', '00000000-0000-0000-0000-000000000000', 'ABCdefff-1234-1234-1234-123456789abc', 'x']),
    (('command',), ['begin', 'corpus.unknown', True, [], {}]),
    (('scope', 'kind'), ['platform', 'organization', None]),
    (('scope', 'source_id'), ['', 'a'*65, 'é', 'a/b', 'a\n', 'a\x00', '\ud800', True]),
    (('evidence_ref',), ['', 'a'*257, 'é', '/a', 'a\n', 'a\x00', '\ud800', True, None]),
    (('payload', 'expected_absent'), [False, 1, 'true', None]),
    (('payload', 'input', 'source_sha256'), ['a'*63, 'A'*64, 'g'*64, 1, None]),
    (('payload', 'input', 'catalogue_version'), ['', 'a'*65, 'é', 'a/b', True]),
    (('payload', 'input', 'versification_id'), ['', 'a'*65, 'é', 'a/b', True]),
    (('payload', 'input', 'tokenization_version'), ['', 'a'*65, 'é', 'a/b', True]),
])
def test_field_type_and_format_boundaries(path, values):
    for value in values:
        body = command()
        target = body
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        assert_invalid(encode(body))


@pytest.mark.parametrize('variant', ['recover', 'seal'])
def test_attempt_and_generation_boundaries(variant):
    from corpus_publication_input import parse_command
    body = command(variant)
    for value in ['1', '9223372036854775807']:
        body['payload']['expected_generation'] = value
        assert parse_command(encode(body)).payload.expected_generation == value
    for value in [True, 1, 1.0, '0', '-1', '+1', '01', '1.0', '9223372036854775808', '9'*100, '١']:
        body['payload']['expected_generation'] = value
        assert_invalid(encode(body))
    body = command(variant)
    for value in [None, True, '', '00000000-0000-0000-0000-000000000000',
                  'ABCdefff-1234-1234-1234-123456789abc']:
        body['payload']['expected_attempt_id'] = value
        assert_invalid(encode(body))
    body = command(variant)
    body['payload']['expected_absent'] = True
    assert_invalid(encode(body))


def test_exact_body_and_string_maxima():
    from corpus_publication_input import parse_command
    body = command()
    body['scope']['source_id'] = 'a'*64
    body['evidence_ref'] = 'a'*256
    for key in ('catalogue_version', 'versification_id', 'tokenization_version'):
        body['payload']['input'][key] = 'a'*64
    raw = encode(body)
    assert parse_command(raw + b' '*(65536-len(raw))).evidence_ref == 'a'*256
    assert_invalid(raw + b' '*(65537-len(raw)))


@pytest.mark.parametrize('variant', ['begin', 'recover', 'seal'])
@pytest.mark.parametrize('fault', ['changed', 'checksum', 'incomplete', 'candidate', 'audit'])
def test_source_requalification_for_every_variant(variant, fault):
    from corpus_publication_input import prepare_command
    from corpus_evidence import EvidenceError
    raw = source_bytes()
    body = command(variant, raw)
    code = 'checksum_mismatch'
    if fault == 'changed':
        raw += b' '
    elif fault == 'checksum':
        body['payload']['input']['source_sha256'] = '0'*64
    else:
        raw = encode({} if fault == 'incomplete' else
                     {'kind': 'scribeswell.' + ('source_evidence_candidate' if fault == 'candidate' else
                                               'database_audit_candidate'), 'publication': False})
        body['payload']['input']['source_sha256'] = hashlib.sha256(raw).hexdigest()
        code = 'source_inventory_invalid'
    with pytest.raises(EvidenceError, match='^source_evidence.' + code + '$'):
        prepare_command(encode(body), raw)


@pytest.mark.parametrize('invalid', ['malformed_json', 'invalid_field'])
def test_command_failure_precedes_source(monkeypatch, invalid):
    import corpus_publication_input as module
    def forbidden(*args, **kwargs):
        pytest.fail('source qualification reached before valid command')
    monkeypatch.setattr(module, 'build_source_candidate', forbidden)
    body = command()
    body['payload']['expected_absent'] = False
    raw = b'{private-marker' if invalid == 'malformed_json' else encode(body)
    with pytest.raises(module.CommandValidationError):
        module.prepare_command(raw, b'bad source')


def test_full_checked_in_source():
    from corpus_publication_input import prepare_command
    raw = (APP / 'scripts/hebrew.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == 'c2d8e9e565be4ee69f938b444e5e0dc37fdfd0d9ccb185d1a5f8d95fab91c498'
    result = prepare_command(encode(command('seal', raw)), raw)
    assert [getattr(result.counts, key) for key in ('books', 'chapters', 'verses', 'tokens')] == [39, 929, 23213, 306785]


def test_standard_library_only_and_no_io():
    # Fresh -S interpreter proves no installed dependency; preloaded stdlib avoids
    # mistaking Python's own module loading for module-triggered file I/O.
    script = r'''
import builtins, dataclasses, hashlib, json, re, sys, typing
sys.path.insert(0, sys.argv[1])
original = builtins.__import__
def guarded(name, *args, **kwargs):
    assert name.split('.')[0] not in {'os', 'socket', 'pathlib', 'psycopg', 'sqlalchemy',
                                     'requests', 'httpx', 'database', 'fastapi', 'dotenv'}
    assert not name.startswith(('services.access', 'services.identity'))
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
def forbidden(*args, **kwargs):
    raise AssertionError('forbidden I/O')
builtins.open = forbidden
def audit(event, args):
    if event.startswith(('socket.', 'subprocess.', 'os.getenv', 'os.putenv')):
        forbidden()
sys.addaudithook(audit)
import corpus_publication_input as module
body, source = json.loads(sys.stdin.buffer.read())
result = module.prepare_command(body.encode(), source.encode())
assert result.counts.books == 39
assert 'database' not in sys.modules
'''
    raw = source_bytes()
    result = subprocess.run([sys.executable, '-S', '-c', script, str(APP / 'backend')],
                            input=encode([encode(command(source=raw)).decode(), raw.decode()]),
                            capture_output=True, env={}, timeout=15)
    assert result.returncode == 0, result.stderr.decode()


@pytest.mark.parametrize('variant', ['begin', 'recover', 'seal'])
@pytest.mark.parametrize('path', [(), ('scope',), ('payload',), ('payload', 'input')])
@pytest.mark.parametrize('value', [None, True, [], 'private-marker', 1])
def test_every_object_boundary_requires_an_object(variant, path, value):
    body = command(variant)
    if not path:
        body = value
    else:
        target = body
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    assert_invalid(encode(body))


@pytest.mark.parametrize('variant', ['recover', 'seal'])
def test_recovery_and_seal_require_exact_payload(variant):
    body = command(variant)
    for key in list(body['payload']):
        saved = body['payload'].pop(key)
        assert_invalid(encode(body))
        body['payload'][key] = saved
    for key in ('expected_generation', 'expected_attempt_id'):
        text = json.dumps(body)
        needle = json.dumps(key) + ': '
        duplicate = text.replace(needle, needle + json.dumps(body['payload'][key]) + ', ' + needle)
        assert_invalid(duplicate.encode())


def test_begin_rejects_recovery_tuple():
    body = command()
    body['payload'].update(expected_generation='1', expected_attempt_id=body['operation_id'])
    assert_invalid(encode(body))


@pytest.mark.parametrize('key,escaped', [
    ('operation_id', r'operation\u005fid'),
    ('source_id', r'source\u005fid'),
    ('expected_absent', r'expected\u005fabsent'),
    ('source_sha256', r'source\u005fsha256'),
])
def test_escaped_equivalent_duplicate_names(key, escaped):
    body = command()
    values = {'operation_id': body['operation_id'], 'source_id': 'tanakh',
              'expected_absent': True, 'source_sha256': SMALL_SOURCE_SHA256}
    needle = json.dumps(key) + ': '
    text = json.dumps(body)
    duplicate = text.replace(needle, '"' + escaped + '": ' + json.dumps(values[key]) + ', ' + needle)
    assert_invalid(duplicate.encode())
