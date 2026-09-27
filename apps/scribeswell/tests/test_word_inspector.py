"""Canonical decoding and read-time correction without mutating stored imports."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/py'))
from oshb_morph import parse_morph_code


def test_finite_verb_characterization():
    verb = parse_morph_code('HVqp3ms')[0]
    assert (verb.verb_stem, verb.verb_aspect, verb.person, verb.gender, verb.number, verb.state) == ('qal', 'perfect', 'third', 'masculine', 'singular', None)


def test_participle_and_infinitive_positions():
    prep, verb, suffix = parse_morph_code('HR/Vqrmpc/Sp3ms')
    assert (verb.verb_stem, verb.verb_aspect, verb.gender, verb.number, verb.state, verb.person) == ('qal', 'participle_active', 'masculine', 'plural', 'construct', None)
    assert (suffix.person, suffix.gender, suffix.number) == ('third', 'masculine', 'singular')
    passive = parse_morph_code('HVqsfs a'.replace(' ', ''))[0]
    assert (passive.gender, passive.number, passive.state, passive.person) == ('feminine', 'singular', 'absolute', None)
    for code in ['HVqa', 'HVqc']:
        inf = parse_morph_code(code)[0]
        assert inf.person is inf.gender is inf.number is inf.state is None


def test_existing_api_rows_derive_features_after_integrity_check(monkeypatch):
    from test_reader_integrity import database
    from services import bible_service
    import pytest
    from copy import deepcopy
    word = dict(id=99, verse_id=1, position=1, surface_he='בְּ/עֹשָׂ֑י/ו', display_he='בְּעֹשָׂ֑יו', lemma_strong='b/6213 a', morph_code='HR/Vqrmpc/Sp3ms')
    db = database([word])
    db.rows['morpheme_read'] = [dict(word_id=99, segment_index=i, language='hebrew', part_of_speech='verb', pos_code=code, gender=None, number=None) for i, code in enumerate(['R', 'Vqrmpc', 'Sp3ms'])]
    original = deepcopy(db.rows)
    monkeypatch.setattr(bible_service, '_get_client', lambda: db)
    result = bible_service.get_word_morphology(99)
    assert result.morphemes[1].number == 'plural'
    assert result.morphemes[1].state == 'construct'
    assert db.rows == original
    db.rows['morpheme_read'].pop()
    with pytest.raises(bible_service.DataIntegrityError):
        bible_service.get_word_morphology(99)


def test_psalm_149_2_real_source_is_preserved_and_readable():
    import json
    corpus = json.loads((Path(__file__).resolve().parents[1] / 'scripts/hebrew.json').read_text())
    surface, lemma, code = corpus['Psalms'][148][1][2]
    assert (surface, lemma, code) == ('בְּ/עֹשָׂ֑י/ו', 'b/6213 a', 'HR/Vqrmpc/Sp3ms')
    parts = parse_morph_code(code)
    assert len(surface.split('/')) == len(parts) == 3
    assert (parts[1].gender, parts[1].number, parts[1].state, parts[1].person) == ('masculine', 'plural', 'construct', None)


def test_real_aramaic_stems_and_api_presentation(monkeypatch):
    import json
    from test_reader_integrity import database
    from services import bible_service
    corpus = json.loads((Path(__file__).resolve().parents[1] / 'scripts/hebrew.json').read_text())
    words = [word for chapters in corpus.values() for verses in chapters for verse in verses for word in verse]
    for code, stem, aspect, person in [('AVarmsa', 'aphel', 'participle_active', None), ('AVai3mp', 'aphel', 'imperfect', 'third'), ('AVqp3ms', 'peal', 'perfect', 'third')]:
        surface, lemma, actual = next(word for word in words if word[2] == code)
        parsed = parse_morph_code(actual)[0]
        assert (parsed.language, parsed.verb_stem, parsed.verb_aspect, parsed.person) == ('aramaic', stem, aspect, person)
        if person is None:
            assert (parsed.gender, parsed.number, parsed.state) == ('masculine', 'singular', 'absolute')
        db = database([dict(id=99, verse_id=1, position=1, surface_he=surface, display_he=surface, lemma_strong=lemma, morph_code=actual)])
        db.rows['morpheme_read'] = [dict(word_id=99, segment_index=0, language='aramaic', part_of_speech='verb', pos_code=actual[1:])]
        monkeypatch.setattr(bible_service, '_get_client', lambda: db)
        result = bible_service.get_word_morphology(99).morphemes[0]
        assert (result.verb_stem, result.verb_aspect, result.person) == (stem, aspect, person)
    assert parse_morph_code('HVqp3ms')[0].verb_stem == 'qal'
    assert parse_morph_code('AVqrmsa')[0].verb_stem == 'peal'
