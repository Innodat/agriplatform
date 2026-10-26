"""Exact-token comparison acceptance; fixtures confer no publication authority."""
from copy import deepcopy
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from corpus_evidence import verse_token_digest
from highlight_evidence import observe_verse, segment_status, HighlightEvidenceError


LABELS = dict(source_id='fixture', catalogue_version='fixture-v1',
              versification_id='fixture-v1', tokenization_version='fixture-v1')
REVISION = '10000000-0000-4000-8000-000000000001'


def fixture():
    words = [dict(position=1, id='101', surface_he='אָב'),
             dict(position=2, id='102', surface_he='בֵּן')]
    digest = verse_token_digest(**LABELS, book='Gen', chapter=1, verse=1,
                                tokens=[[w['position'], w['surface_he']] for w in words])
    publication = dict(version=1, status='ready', **LABELS, source_revision=REVISION,
                       book='Gen', chapter=1, verse=1, verse_token_digest=digest,
                       observed_word_ids=['101', '102'])
    segment = dict(**LABELS, source_revision=REVISION, book='Gen', chapter=1, verse=1,
                   verse_token_digest=digest, start_position=1, end_position=2,
                   observed_word_ids=['101', '102'])
    return publication, words, segment


def test_exact_match_is_valid_without_mutating_inputs():
    publication, words, segment = fixture()
    original = deepcopy((publication, words, segment))
    proof = observe_verse(publication, words)
    assert proof['status'] == 'ready'
    assert segment_status(segment, proof) == 'valid'
    assert (publication, words, segment) == original


def test_reused_ids_with_changed_surface_never_produce_ready_evidence():
    publication, words, segment = fixture()
    words[0]['surface_he'] = 'אחר'
    proof = observe_verse(publication, words)
    assert proof == {'version': 1, 'status': 'unavailable'}
    assert segment_status(segment, proof) == 'unavailable'


def test_new_current_publication_with_changed_text_needs_review():
    publication, words, segment = fixture()
    words[0]['surface_he'] = 'אחר'
    publication['verse_token_digest'] = verse_token_digest(
        **LABELS, book='Gen', chapter=1, verse=1,
        tokens=[[w['position'], w['surface_he']] for w in words])
    assert segment_status(segment, observe_verse(publication, words)) == 'needs_review'


def test_identical_tokens_with_new_ids_and_revision_remain_valid():
    publication, words, segment = fixture()
    publication['source_revision'] = '20000000-0000-4000-8000-000000000001'
    for n, word in enumerate(words, 201):
        word['id'] = str(n)
    publication['observed_word_ids'] = ['201', '202']
    assert segment_status(segment, observe_verse(publication, words)) == 'valid'


@pytest.mark.parametrize('change', ['missing', 'reordered', 'duplicate_id', 'bool_position',
                                  'bad_id', 'oversize_id', 'wrong_ids', 'bad_revision', 'updating'])
def test_inconsistent_observation_is_unavailable(change):
    publication, words, _ = fixture()
    if change == 'missing': words.pop()
    elif change == 'reordered': words.reverse()
    elif change == 'duplicate_id': words[1]['id'] = words[0]['id']
    elif change == 'bool_position': words[0]['position'] = True
    elif change == 'bad_id': words[0]['id'] = '01'
    elif change == 'oversize_id': words[0]['id'] = str(2 ** 63)
    elif change == 'wrong_ids': publication['observed_word_ids'] = ['301', '302']
    elif change == 'bad_revision': publication['source_revision'] = 'bad'
    else: publication['status'] = 'updating'
    assert observe_verse(publication, words) == {'version': 1, 'status': 'unavailable'}


@pytest.mark.parametrize('field,value', [('source_id', 'other'), ('catalogue_version', 'other'),
                                       ('versification_id', 'other'), ('tokenization_version', 'other'),
                                       ('book', 'Exod'), ('chapter', 2), ('verse', 2)])
def test_incompatible_identity_needs_review(field, value):
    publication, words, segment = fixture()
    segment[field] = value
    assert segment_status(segment, observe_verse(publication, words)) == 'needs_review'


@pytest.mark.parametrize('field,value', [('start_position', 0), ('end_position', True),
                                       ('end_position', 1), ('observed_word_ids', ['101']),
                                       ('source_revision', 'bad'), ('verse_token_digest', 'bad')])
def test_malformed_saved_segment_is_rejected(field, value):
    publication, words, segment = fixture()
    if field == 'end_position' and value == 1:
        segment['start_position'] = 2
    segment[field] = value
    with pytest.raises(HighlightEvidenceError, match='highlight_evidence.segment_invalid'):
        segment_status(segment, observe_verse(publication, words))


@pytest.mark.parametrize('change', ['version', 'count', 'duplicate', 'identity', 'digest', 'revision'])
def test_malformed_current_evidence_is_unavailable(change):
    publication, words, segment = fixture()
    evidence = observe_verse(publication, words)
    if change == 'version': evidence['version'] = True
    elif change == 'count': evidence['token_count'] = True
    elif change == 'duplicate': evidence['observed_word_ids'] = ['101', '101']
    elif change == 'identity': evidence['source_id'] = []
    elif change == 'digest': evidence['verse_token_digest'] = 'invalid'
    else: evidence['source_revision'] = 'invalid'
    assert segment_status(segment, evidence) == 'unavailable'


@pytest.mark.parametrize('start,end,ids,status', [(1, 1, ['101'], 'valid'),
                                                (2, 2, ['102'], 'valid'),
                                                (2, 3, ['102', '103'], 'needs_review')])
def test_inclusive_subrange_and_missing_position(start, end, ids, status):
    publication, words, segment = fixture()
    segment.update(start_position=start, end_position=end, observed_word_ids=ids)
    assert segment_status(segment, observe_verse(publication, words)) == status


@pytest.mark.parametrize('surface', ['אָ֑ב', 'אָב\u200b', '\ud800', 'א' * 1025])
def test_exact_surface_changes_and_invalid_surfaces_are_unavailable(surface):
    publication, words, _ = fixture()
    words[0]['surface_he'] = surface
    assert observe_verse(publication, words) == {'version': 1, 'status': 'unavailable'}


def test_canonically_equivalent_unicode_sequences_are_not_normalized():
    publication, words, _ = fixture()
    import unicodedata
    first, second = 'א\u05b8\u05b7', 'א\u05b7\u05b8'
    assert first != second and unicodedata.normalize('NFD', first) == unicodedata.normalize('NFD', second)
    words[0]['surface_he'] = first
    publication['verse_token_digest'] = verse_token_digest(
        **LABELS, book='Gen', chapter=1, verse=1,
        tokens=[[w['position'], w['surface_he']] for w in words])
    assert observe_verse(publication, words)['status'] == 'ready'
    words[0]['surface_he'] = second
    assert observe_verse(publication, words)['status'] == 'unavailable'


def test_ready_output_has_only_evidence_and_independent_ids():
    publication, words, _ = fixture()
    publication['unexpected_secret'] = 'must not escape'
    result = observe_verse(publication, words)
    assert set(result) == {'version', 'status', *LABELS, 'book', 'chapter', 'verse',
                           'source_revision', 'verse_token_digest', 'observed_word_ids', 'token_count'}
    assert result['observed_word_ids'] == ['101', '102']
    result['observed_word_ids'][0] = '999'
    assert publication['observed_word_ids'] == ['101', '102']
    assert words[0]['id'] == '101'
