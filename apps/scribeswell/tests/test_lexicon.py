import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from services.lexicon_service import lexical_id, match_metadata, get_entry


def test_content_identity_preserves_augmented_homonyms():
    assert lexical_id('c/l/1254 a') == '1254 a'
    assert lexical_id('c/l') is None
    assert lexical_id('1254 a/1254 b') is None
    assert match_metadata('c/1254 a', 'HC/Vqp3ms')['lexical_id'] == '1254 a'
    assert match_metadata('1254 a', 'HVqp3ms')['match_key'] != match_metadata('1254 b', 'HVqp3ms')['match_key']


def test_missing_entry_falls_back_without_invented_root():
    assert get_entry('99999')['status'] == 'missing'
    assert match_metadata('99999', 'HNcmsa')['match_key'] == 'lemma:99999'


def test_recorded_root_uses_identity_and_not_spelling():
    king = get_entry('4428')
    kingdom = get_entry('4467')
    counsel = get_entry('4427 b')
    assert king['root']['id'] == kingdom['root']['id'] == 'haj'
    assert counsel['root']['id'] == 'hah'
    assert counsel['root']['text'] == king['root']['text']
    assert match_metadata('c/l/4467', 'HC/R/Ncfsa')['match_key'] == 'root:haj'
    assert match_metadata('4428', 'HTd')['match_key'] == 'lemma:4428'
    assert get_entry('1254 a')['lexical_id'] == '1254 a'


def test_unsafe_xml_and_safe_structured_senses():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/py'))
    from build_lexicon import parse, blocks
    import pytest
    with pytest.raises(ValueError):
        parse(b'<!DOCTYPE entry [<!ENTITY bad "secret">]><entry>&bad;</entry>')
    with pytest.raises(ValueError):
        parse(b' ' * 12_000_001)
    nodes = blocks(parse(b'<entry>One <sense n="1">sense <ref r="Gen.1.1">Gn 1:1</ref><script>alert(1)</script></sense> tail</entry>'))
    assert nodes[1]['kind'] == 'sense'
    assert nodes[1]['children'][1]['book'] == 'Gen'
    assert 'alert' not in str(nodes)


def test_missing_artifact_is_nonfatal(monkeypatch):
    from services import lexicon_service
    lexicon_service.artifact.cache_clear()
    monkeypatch.setattr(lexicon_service, 'ARTIFACT', Path('/nonexistent-lexicon'))
    assert get_entry('1')['status'] == 'unavailable'
    assert match_metadata('1', 'HNcmsa')['match_key'] == 'lemma:1'
    lexicon_service.artifact.cache_clear()


def test_occurrences_count_words_and_verses_filter_and_page(monkeypatch):
    from test_reader_integrity import Database
    from services import bible_service, lexicon_service
    db = Database(cap=2)
    db.rows['book_read'] = [{'id': i, 'osis_id': osis, 'name_en': osis, 'name_he': 'א', 'testament': 'old', 'division': 'torah', 'book_order': i} for i, osis in [(1, 'Gen'), (2, 'Exod')]]
    db.rows['verse_read'] = [{'id': i, 'book_id': 1 if i < 3 else 2, 'chapter_num': 1, 'verse_num': i} for i in range(1, 4)]
    db.rows['word_read'] = [{'id': i, 'verse_id': verse, 'position': i, 'surface_he': 'אב', 'display_he': 'אב', 'lemma_strong': lemma} for i, verse, lemma in [(1, 1, '1'), (2, 1, 'c/1'), (3, 2, '1'), (4, 3, '1'), (5, 3, '1 a')]]
    monkeypatch.setattr(bible_service, '_get_client', lambda: db)
    monkeypatch.setattr(lexicon_service, 'lemma_variants', lambda: {'1': ['1', 'c/1']})
    result = bible_service.get_occurrences('1', offset=1, limit=2)
    assert result['total'] == 4 and result['verse_total'] == 3
    assert [w['id'] for w in result['data']] == [2, 3]
    filtered = bible_service.get_occurrences('1', book='Exod')
    assert filtered['total'] == 1 and filtered['data'][0]['id'] == 4
    assert bible_service.get_occurrences('1', book='Unknown')['total'] == 0
    assert bible_service.get_occurrences('1', offset=99)['data'] == []


def test_public_lexicon_and_bounded_occurrences_contract(monkeypatch):
    from test_reader_integrity import app, TestClient
    from services import bible_service
    monkeypatch.setattr(bible_service, 'get_occurrences', lambda *args: {'data': [], 'total': 0, 'verse_total': 0, 'offset': 0, 'limit': 25})
    with TestClient(app) as client:
        entry = client.get('/api/bible/lexicon/4427%20b')
        assert entry.status_code == 200 and entry.json()['root']['id'] == 'hah'
        assert client.get('/api/bible/occurrences/1').status_code == 200
        assert client.get('/api/bible/occurrences/1?limit=101').status_code == 422
        assert client.get('/api/bible/occurrences/1?offset=-1').status_code == 422
        assert client.get('/api/bible/lexicon/c%2Fl').status_code == 404


def test_mixed_content_separators_language_and_full_rebuild():
    import json
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/py'))
    import build_lexicon as builder
    def flatten(nodes):
        return ''.join(flatten(n['children']) if 'children' in n else n['text'] for n in nodes)
    mixed = '<entry><w>אב</w> <foreign xml:lang="ara">أب</foreign> <ref r="Gen.1.1">Gn 1:1</ref> <ref r="Gen.1.2">Gn 1:2</ref></entry>'
    nodes = builder.blocks(builder.parse(mixed.encode()))
    assert flatten(nodes) == 'אב أب Gn 1:1 Gn 1:2'
    assert nodes[0]['language'] == 'he' and nodes[0]['direction'] == 'rtl'
    assert nodes[2]['language'] == 'ar' and nodes[2]['direction'] == 'rtl'
    assert builder.blocks(builder.parse(b'<entry><w>word</w></entry>'), 'arc')[0]['language'] == 'arc'
    snapshot = (builder.DIRECTORY / 'lexicon.json').read_bytes()
    builder.build()
    assert (builder.DIRECTORY / 'lexicon.json').read_bytes() == snapshot
    entries = json.loads(snapshot)['entries']
    assert '13:17' in flatten(entries['3247']['bdb'])
    def walk(nodes):
        for node in nodes:
            yield node
            yield from walk(node.get('children', []))
    refs = [n for n in walk(entries['3247']['bdb']) if n['kind'] == 'reference']
    assert not any(n['book'] == 'Ezra' and n['chapter'] == 13 for n in refs)
    assert any(n['kind'] == 'language' for n in walk(entries['1']['bdb']))
    assert all(builder.valid_reference(n['book'], n['chapter'], n['verse']) for entry in entries.values() for n in walk(entry['bdb']) if n['kind'] == 'reference')
    source = next(e for e in builder.parse((builder.DIRECTORY / 'BrownDriverBriggs.xml').read_bytes()).iter('entry') if e.get('id') == 'a.ab.ab')
    for child in list(source):
        if child.tag == 'status':
            source.remove(child)
    assert ' '.join(flatten(entries['3']['bdb']).split()) == ' '.join(''.join(source.itertext()).split())


def test_http_chapter_enriches_roots_homonyms_and_prefix_only(monkeypatch):
    from test_reader_integrity import app, TestClient, database
    from services import bible_service
    lemmas = ['4428', 'c/4467', '4427 b', 'c/l']
    db = database([{'id': i, 'verse_id': 1, 'position': i, 'surface_he': 'אב', 'display_he': 'אב', 'lemma_strong': lemma, 'morph_code': 'HNcmsa'} for i, lemma in enumerate(lemmas, 1)])
    monkeypatch.setattr(bible_service, '_get_client', lambda: db)
    with TestClient(app) as client:
        response = client.get('/api/bible/books/Ps/chapters/23/verses')
    assert response.status_code == 200
    words = response.json()['data'][0]['words']
    assert [w['match_key'] for w in words] == ['root:haj', 'root:haj', 'root:hah', None]
    assert [w['lexical_id'] for w in words] == ['4428', '4467', '4427 b', None]


def test_real_variants_and_canonical_order_independent_of_ids(monkeypatch):
    from test_reader_integrity import Database
    from services import bible_service, lexicon_service
    variants = lexicon_service.lemma_variants()
    assert 'c/1254 a' in variants['1254 a']
    db = Database(cap=2)
    db.rows['book_read'] = [{'id': i, 'osis_id': osis, 'name_en': osis, 'name_he': 'א', 'testament': 'old', 'division': 'torah', 'book_order': order} for i, osis, order in [(9, 'Gen', 1), (2, 'Exod', 2)]]
    db.rows['verse_read'] = [{'id': i, 'book_id': i, 'chapter_num': 1, 'verse_num': 1} for i in [9, 2]]
    db.rows['word_read'] = [{'id': i, 'verse_id': book, 'position': i, 'surface_he': 'ברא', 'display_he': 'ברא', 'lemma_strong': lemma} for i, book, lemma in [(1, 2, '1254 a'), (2, 9, 'c/1254 a'), (3, 9, '1254 b')]]
    monkeypatch.setattr(bible_service, '_get_client', lambda: db)
    result = bible_service.get_occurrences('1254 a')
    assert result['total'] == 2
    assert [w['id'] for w in result['data']] == [2, 1]
