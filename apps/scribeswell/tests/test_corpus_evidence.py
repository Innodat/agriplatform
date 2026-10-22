"""Source-artifact qualification; no database/publication qualification."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

APP = Path(__file__).resolve().parents[1]
CLI = APP / 'tools/py/build_source_evidence.py'
sys.path.insert(0, str(APP / 'backend'))
sys.path.insert(0, str(APP / 'tools/py'))
LABELS = dict(source_id='fixture-source', catalogue_version='fixture-catalogue-v1',
              versification_id='fixture-versification', tokenization_version='fixture-tokenization-v1')


def invoke(source, output, checksum=None):
    args = [sys.executable, '-S', str(CLI), '--source', str(source), '--output', str(output),
            '--expected-source-sha256', checksum or hashlib.sha256(source.read_bytes()).hexdigest()]
    for key, value in LABELS.items():
        args += ['--' + key.replace('_', '-'), value]
    return subprocess.run(args, capture_output=True, text=True, env={})


def test_cli_rejects_incomplete_source_without_writing(tmp_path):
    source, output = tmp_path / 'source', tmp_path / 'candidate'
    source.write_text('{}')
    result = invoke(source, output)
    assert result.returncode != 0
    assert result.stderr.strip() == 'source_evidence.source_inventory_invalid'
    assert not output.exists()


def test_canonical_vectors():
    from corpus_evidence import encode_verse_tokens, verse_token_digest
    fixture = json.loads((APP / 'tests/fixtures/verse-token-digests-v1.json').read_text())
    for vector in fixture['vectors']:
        payload = json.loads(vector['canonical_payload_utf8'])
        args = (*payload[1:8], payload[8])
        assert encode_verse_tokens(*args) == vector['canonical_payload_utf8'].encode('utf-8')
        assert verse_token_digest(*args) == vector['sha256']


@pytest.mark.parametrize('tokens', [[], [[True, 'א']], [[2, 'א']], [[1, 'א'], [1, 'ב']],
                                  [[1, 'א'], [3, 'ב']], [[1, '']], [[1, '\ud800']],
                                  [[1, 'א' * 1025]]])
def test_invalid_tokens(tokens):
    from corpus_evidence import encode_verse_tokens, EvidenceError
    with pytest.raises(EvidenceError):
        encode_verse_tokens(*LABELS.values(), 'Gen', 1, 1, tokens)


def small_source():
    from corpus_source import BOOK_METADATA
    return {meta['name_en']: [[[['שָׁ/אָב', '1', 'HNcmsa']]]] for meta in reversed(BOOK_METADATA)}


def write_source(tmp_path, data):
    path = tmp_path / 'input.json'
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    return path


def test_source_order_counts_and_no_scripture_bodies(tmp_path):
    from corpus_source import BOOK_METADATA
    source = write_source(tmp_path, small_source())
    first, second = tmp_path / 'one', tmp_path / 'two'
    before = source.read_bytes()
    assert invoke(source, first).returncode == 0
    assert invoke(source, second).returncode == 0
    assert first.read_bytes() == second.read_bytes()
    assert source.read_bytes() == before
    data = json.loads(first.read_bytes())
    assert data['kind'] == 'scribeswell.source_evidence_candidate'
    assert data['publication'] is False
    assert data['counts'] == dict(books=39, chapters=39, verses=39, tokens=39)
    assert [v['book'] for v in data['verses']] == [m['osis_id'] for m in BOOK_METADATA]
    assert all(set(v) == {'book', 'chapter', 'verse', 'token_count', 'verse_token_digest'}
               for v in data['verses'])
    assert 'אָב' not in first.read_text()
    assert first.read_bytes().endswith(b'\n')


@pytest.mark.parametrize('change', ['missing_book', 'extra_book', 'empty_book', 'empty_chapter',
                                    'empty_verse', 'bad_word', 'bad_morph', 'surrogate',
                                    'chapters_limit', 'verses_limit', 'tokens_limit'])
def test_malformed_source_never_writes(tmp_path, change):
    data = small_source()
    if change == 'missing_book':
        data.pop('Genesis')
    elif change == 'extra_book':
        data['Unknown'] = data['Genesis']
    elif change == 'empty_book':
        data['Genesis'] = []
    elif change == 'empty_chapter':
        data['Genesis'] = [[]]
    elif change == 'empty_verse':
        data['Genesis'] = [[[]]]
    elif change == 'bad_word':
        data['Genesis'] = [[[['1', '2', 'HNcmsa']]]]
    elif change == 'bad_morph':
        data['Genesis'][0][0][0][2] = 'HZ'
    elif change == 'surrogate':
        data['Genesis'][0][0][0][1] = '\ud800'
    elif change == 'chapters_limit':
        data['Genesis'] *= 151
    elif change == 'verses_limit':
        data['Genesis'][0] *= 177
    elif change == 'tokens_limit':
        data['Genesis'][0][0] *= 513
    source = tmp_path / 'input'
    source.write_text(json.dumps(data), encoding='utf-8')
    output = tmp_path / 'output'
    result = invoke(source, output)
    assert result.returncode == 1
    assert result.stderr.startswith('source_evidence.')
    assert 'Traceback' not in result.stderr
    assert not output.exists()


@pytest.mark.parametrize('raw,code', [(b'{"Genesis":[],"Genesis":[]}', 'duplicate_json_key'),
                                     (b'\xff', 'json_invalid'), (b'{', 'json_invalid'),
                                     (b'{"x":NaN}', 'json_invalid')])
def test_invalid_json(tmp_path, raw, code):
    source, output = tmp_path / 'source', tmp_path / 'output'
    source.write_bytes(raw)
    result = invoke(source, output)
    assert result.stderr.strip() == 'source_evidence.' + code
    assert not output.exists()


def test_checksum_and_size_limits(tmp_path):
    source = write_source(tmp_path, small_source())
    output = tmp_path / 'output'
    assert invoke(source, output, '0' * 64).stderr.strip() == 'source_evidence.checksum_mismatch'
    assert invoke(source, output, 'A' * 64).stderr.strip() == 'source_evidence.checksum_invalid'
    from corpus_evidence import MAX_SOURCE_BYTES
    with source.open('wb') as stream:
        stream.truncate(MAX_SOURCE_BYTES + 1)
    assert invoke(source, output).stderr.strip() == 'source_evidence.source_too_large'
    assert not output.exists()


@pytest.mark.parametrize('value', ['', 'a' * 65, 'å', 'a/b', 'a\n', True])
def test_metadata_validation(value):
    from corpus_evidence import encode_verse_tokens, EvidenceError
    labels = dict(LABELS, source_id=value)
    with pytest.raises(EvidenceError, match='identity_invalid'):
        encode_verse_tokens(**labels, book='Gen', chapter=1, verse=1, tokens=[[1, 'א']])


@pytest.mark.parametrize('chapter,verse', [(True, 1), (0, 1), (151, 1), (1, False), (1, 177), (1.0, 1)])
def test_invalid_coordinates(chapter, verse):
    from corpus_evidence import encode_verse_tokens, EvidenceError
    with pytest.raises(EvidenceError):
        encode_verse_tokens(**LABELS, book='Gen', chapter=chapter, verse=verse, tokens=[[1, 'א']])


def test_digest_binds_every_identity_and_order():
    from corpus_evidence import verse_token_digest
    args = [*LABELS.values(), 'Gen', 1, 1, [[1, 'א'], [2, 'ב']]]
    base = verse_token_digest(*args)
    for index in range(7):
        changed = args.copy()
        changed[index] = changed[index] + ('x' if index < 5 else 1)
        assert verse_token_digest(*changed) != base
    args[-1] = [[1, 'ב'], [2, 'א']]
    assert verse_token_digest(*args) != base


def test_output_exists_symlink_and_write_failure(tmp_path):
    source = write_source(tmp_path, small_source())
    output = tmp_path / 'output'
    output.write_bytes(b'keep')
    assert invoke(source, output).stderr.strip() == 'source_evidence.output_exists'
    assert output.read_bytes() == b'keep'
    link = tmp_path / 'link'
    link.symlink_to(output)
    assert invoke(source, link).stderr.strip() == 'source_evidence.output_exists'
    assert output.read_bytes() == b'keep'
    assert invoke(source, tmp_path / 'missing' / 'output').stderr.strip() == 'source_evidence.output_write_failed'
    assert not list(tmp_path.glob('.source-evidence-*'))


def test_atomic_write_failure_removes_only_owned_temp(tmp_path, monkeypatch):
    from build_source_evidence import atomic_create
    from corpus_evidence import EvidenceError
    import os
    foreign = tmp_path / '.source-evidence-foreign'
    foreign.write_bytes(b'keep')
    def fail(*args):
        raise OSError('sensitive error')
    monkeypatch.setattr(os, 'fsync', fail)
    with pytest.raises(EvidenceError, match='output_write_failed'):
        atomic_create(tmp_path / 'output', b'candidate')
    assert list(tmp_path.iterdir()) == [foreign]


def test_destination_created_during_publish_is_preserved(tmp_path, monkeypatch):
    from build_source_evidence import atomic_create
    from corpus_evidence import EvidenceError
    import os
    output = tmp_path / 'output'
    original_link = os.link
    def racing_link(temporary, destination):
        output.write_bytes(b'other writer')
        original_link(temporary, destination)
    monkeypatch.setattr(os, 'link', racing_link)
    with pytest.raises(EvidenceError, match='output_exists'):
        atomic_create(output, b'candidate')
    assert output.read_bytes() == b'other writer'
    assert list(tmp_path.iterdir()) == [output]


def test_full_checked_in_source_is_reproducible(tmp_path):
    source = APP / 'scripts/hebrew.json'
    approved = 'c2d8e9e565be4ee69f938b444e5e0dc37fdfd0d9ccb185d1a5f8d95fab91c498'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == approved
    first, second = tmp_path / 'full-one', tmp_path / 'full-two'
    assert invoke(source, first, approved).returncode == 0
    assert invoke(source, second, approved).returncode == 0
    assert first.read_bytes() == second.read_bytes()
    assert json.loads(first.read_bytes())['counts'] == dict(books=39, chapters=929, verses=23213, tokens=306785)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == approved


def test_safe_argument_and_source_read_errors(tmp_path):
    result = subprocess.run([sys.executable, '-S', str(CLI), '--unknown', 'private-marker'],
                            capture_output=True, text=True, env={})
    assert result.returncode == 2
    assert result.stderr.strip() == 'source_evidence.arguments_invalid'
    result = invoke(tmp_path / 'missing', tmp_path / 'output', '0' * 64)
    assert result.returncode == 1
    assert result.stderr.strip() == 'source_evidence.source_read_failed'
    assert not (tmp_path / 'output').exists()


@pytest.mark.parametrize('field,value', [(1, '1' * 2049), (2, 'HC/' + 'C/' * 1023 + 'C')],
                         ids=['oversized-strong', 'oversized-morphology'])
def test_source_fields_are_bounded_before_decode(monkeypatch, field, value):
    import corpus_evidence
    source = small_source()
    source['Genesis'][0][0][0][field] = value
    raw = json.dumps(source, ensure_ascii=False).encode('utf-8')
    def unexpected_decode(*args):
        pytest.fail('oversized source field reached decoder')
    monkeypatch.setattr(corpus_evidence, 'decode_word', unexpected_decode)
    with pytest.raises(corpus_evidence.EvidenceError, match='surface_too_large'):
        corpus_evidence.build_source_candidate(raw, hashlib.sha256(raw).hexdigest(), **LABELS)


def test_cleanup_failure_reports_safe_error_after_complete_destination(tmp_path, monkeypatch, capsys):
    import build_source_evidence as cli
    from corpus_evidence import build_source_candidate, serialize_candidate
    source = write_source(tmp_path, small_source())
    output = tmp_path / 'output'
    unrelated = tmp_path / '.source-evidence-foreign'
    unrelated.write_bytes(b'keep')
    raw = source.read_bytes()
    checksum = hashlib.sha256(raw).hexdigest()
    expected = serialize_candidate(build_source_candidate(raw, checksum, **LABELS))
    args = [str(CLI), '--source', str(source), '--output', str(output),
            '--expected-source-sha256', checksum]
    for key, value in LABELS.items():
        args += ['--' + key.replace('_', '-'), value]
    monkeypatch.setattr(sys, 'argv', args)
    attempted = []
    def fail_unlink(path, *args, **kwargs):
        attempted.append(path)
        raise OSError('sensitive unlink failure')
    monkeypatch.setattr(Path, 'unlink', fail_unlink)
    assert cli.main() == 1
    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == 'source_evidence.output_cleanup_failed\n'
    assert output.read_bytes() == expected
    assert json.loads(output.read_bytes())['counts']['verses'] == 39
    assert unrelated.read_bytes() == b'keep'
    assert len(attempted) == 1
    assert attempted[0].name.startswith('.source-evidence-')
    assert attempted[0] != unrelated
    assert attempted[0].read_bytes() == expected


def test_cli_pins_exact_multiword_verse_digests(tmp_path):
    source = small_source()
    source['Genesis'] = [[
        [['שָׁ/אָב', '1', 'HNcmsa'], ['2', 'בֵּן', 'HNcmsa']],
        [['אֵם/בַּת', '3', 'HNcmsa'], ['וְ/אָב', '4', 'HC/Ncmsa']],
    ]]
    source_path = write_source(tmp_path, source)
    output = tmp_path / 'candidate'
    assert invoke(source_path, output).returncode == 0
    verses = json.loads(output.read_bytes())['verses']
    # Independent fixed hashes of the positional JSON for LABELS and Gen 1:1/1:2.
    expected = [
        ('Gen', 1, 1, 2, 'c93ea368c25d980dfe9bec1af90d1697e15c3230b4bd3676d2b7b3ed2722e748'),
        ('Gen', 1, 2, 2, '6a652c6c00f187b702c250f8e9321a89a97b20634bf74ea547c7f35d4b0c2589'),
    ]
    assert [(v['book'], v['chapter'], v['verse'], v['token_count'], v['verse_token_digest'])
            for v in verses[:2]] == expected
    # Slash-stripped display_he bytes have different independently pinned hashes.
    assert verses[0]['verse_token_digest'] != 'b0f510c1288c4af5d9c8130d7f243ef9c9d037672d7b62e475903b2535d124ce'
    assert verses[1]['verse_token_digest'] != '508e5b33a32416244dfb1a5ff015a93860996b0bde874af90f32dd28c89051e7'
