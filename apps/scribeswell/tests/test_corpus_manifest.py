"""Complete manifest candidate acceptance, without SQL/publication authority."""
from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from corpus_source import BOOK_METADATA
from corpus_manifest import build_manifest_candidate, ManifestError


LABELS = dict(source_id='fixture', catalogue_version='fixture-v1',
              versification_id='fixture-v1', tokenization_version='fixture-v1')
ATTEMPT = '10000000-0000-4000-8000-000000000001'
REVISION = '20000000-0000-4000-8000-000000000001'
ACTOR = '30000000-0000-4000-8000-000000000001'


def inputs():
    raw = json.dumps({book['name_en']: [[[['אָב', '1', 'HNcmsa']]]]
                      for book in BOOK_METADATA}, ensure_ascii=False).encode()
    observed = {(book['osis_id'], 1, 1): [str(n)]
                for n, book in enumerate(BOOK_METADATA, 101)}
    return dict(raw=raw, expected_source_sha256=hashlib.sha256(raw).hexdigest(),
                **LABELS, source_revision=REVISION, executor_actor_id=ACTOR,
                attempt_id=ATTEMPT, generation=1, expected_attempt_id=ATTEMPT,
                expected_generation=1, observed=observed)


def test_complete_inventory_is_frozen_and_explicitly_not_published():
    kwargs = inputs()
    manifest = build_manifest_candidate(**kwargs)
    assert manifest.publication is False
    assert manifest.attempt_id == ATTEMPT and manifest.generation == 1
    assert manifest.source_revision == REVISION and manifest.executor_actor_id == ACTOR
    assert len(manifest.verses) == 39
    assert tuple(verse.book for verse in manifest.verses) == tuple(book['osis_id'] for book in BOOK_METADATA)
    assert manifest.verses[0].observed_word_ids == ('101',)
    kwargs['observed'][('Gen', 1, 1)][0] = '999'
    assert manifest.verses[0].observed_word_ids == ('101',)
    with pytest.raises(FrozenInstanceError):
        manifest.generation = 2
    with pytest.raises(FrozenInstanceError):
        manifest.verses[0].verse_token_digest = 'bad'


@pytest.mark.parametrize('change', ['missing', 'extra', 'duplicate', 'wrong_count', 'bool_id',
                                  'noncanonical_id', 'large_id', 'stale_attempt', 'stale_generation',
                                  'bool_generation', 'revision', 'actor', 'checksum'])
def test_invalid_or_wrong_binding_cannot_assemble(change):
    kwargs = inputs()
    if change == 'missing': del kwargs['observed'][('Gen', 1, 1)]
    elif change == 'extra': kwargs['observed'][('Gen', 1, 2)] = ['999']
    elif change == 'duplicate': kwargs['observed'][('Exod', 1, 1)] = ['101']
    elif change == 'wrong_count': kwargs['observed'][('Gen', 1, 1)] = ['101', '999']
    elif change == 'bool_id': kwargs['observed'][('Gen', 1, 1)] = [True]
    elif change == 'noncanonical_id': kwargs['observed'][('Gen', 1, 1)] = ['01']
    elif change == 'large_id': kwargs['observed'][('Gen', 1, 1)] = [str(2 ** 63)]
    elif change == 'stale_attempt': kwargs['expected_attempt_id'] = REVISION
    elif change == 'stale_generation': kwargs['expected_generation'] = 2
    elif change == 'bool_generation': kwargs['generation'] = True
    elif change == 'revision': kwargs['source_revision'] = 'bad'
    elif change == 'actor': kwargs['executor_actor_id'] = 'bad'
    else: kwargs['expected_source_sha256'] = '0' * 64
    with pytest.raises(ManifestError, match='corpus_manifest.invalid'):
        build_manifest_candidate(**kwargs)


def test_boolean_coordinate_alias_cannot_replace_canonical_integer_coordinate():
    kwargs = inputs()
    ids = kwargs['observed'].pop(('Gen', 1, 1))
    kwargs['observed'][('Gen', True, True)] = ids
    with pytest.raises(ManifestError):
        build_manifest_candidate(**kwargs)


def test_direct_model_construction_does_not_retain_mutable_inventories():
    from dataclasses import replace
    manifest = build_manifest_candidate(**inputs())
    ids = ['101']
    verse = replace(manifest.verses[0], observed_word_ids=ids)
    verses = [verse]
    copied = replace(manifest, verses=verses)
    ids[0] = '999'
    verses.clear()
    assert copied.verses[0].observed_word_ids == ('101',)


def test_multichapter_multiverse_mapping_order_and_exact_source_binding():
    from corpus_evidence import build_source_candidate
    kwargs = inputs()
    source = json.loads(kwargs['raw'])
    source['Genesis'] = [[[['אָב', '1', 'HNcmsa'], ['בֵּן', '1', 'HNcmsa']],
                          [['אֵם', '1', 'HNcmsa']]], [[['בַּת', '1', 'HNcmsa']]]]
    kwargs['raw'] = json.dumps(source, ensure_ascii=False).encode()
    kwargs['expected_source_sha256'] = hashlib.sha256(kwargs['raw']).hexdigest()
    kwargs['observed'][('Gen', 1, 1)] = ['999', '501']
    kwargs['observed'][('Gen', 1, 2)] = ['502']
    kwargs['observed'][('Gen', 2, 1)] = ['503']
    manifest = build_manifest_candidate(**kwargs)
    qualified = build_source_candidate(kwargs['raw'], kwargs['expected_source_sha256'], **LABELS)
    assert all(getattr(manifest, key) == value for key, value in LABELS.items())
    assert manifest.source_sha256 == qualified['source_sha256']
    assert [(v.book, v.chapter, v.verse, v.verse_token_digest) for v in manifest.verses] == [
        (v['book'], v['chapter'], v['verse'], v['verse_token_digest']) for v in qualified['verses']]
    assert [(v.book, v.chapter, v.verse, v.observed_word_ids) for v in manifest.verses[:3]] == [
        ('Gen', 1, 1, ('999', '501')), ('Gen', 1, 2, ('502',)), ('Gen', 2, 1, ('503',))]
    source['Genesis'][0][0][0][0] = 'אחר'
    kwargs['raw'] = json.dumps(source, ensure_ascii=False).encode()
    kwargs['expected_source_sha256'] = hashlib.sha256(kwargs['raw']).hexdigest()
    changed = build_manifest_candidate(**kwargs)
    assert changed.verses[0].verse_token_digest != manifest.verses[0].verse_token_digest
    assert changed.verses[1:] == manifest.verses[1:]
    assert changed.verses[0].observed_word_ids == manifest.verses[0].observed_word_ids
    kwargs['observed'][('Gen', 2, 2)] = kwargs['observed'].pop(('Gen', 2, 1))
    with pytest.raises(ManifestError):
        build_manifest_candidate(**kwargs)
