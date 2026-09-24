import copy
import json
from pathlib import Path
import pytest
from apps.pts.backend.collection import validate, select, citation, filters

LIBRARY = Path(__file__).parents[1] / 'reference/poetry-library/library.json'

@pytest.fixture
def library():
    return json.loads(LIBRARY.read_text())

def test_baseline_and_integrity(library):
    assert validate(library) == dict(poems=312, texts=190, checked=33, witnesses=275, sources=19, rights=19)
    broken = copy.deepcopy(library)
    broken['poems'][0]['source_id'] = 'MISSING'
    with pytest.raises(ValueError): validate(broken)

def test_filtered_export_retains_alternate_witness_rights(library):
    result = select(library, search='Mwanadani wako mwandani', availability='all')
    assert result['poems']
    ids = {p['id'] for p in result['poems']}
    assert all(w['poem_id'] in ids for w in result['witnesses'])
    source_ids = {s['id'] for s in result['sources']}
    assert all(w['source_id'] in source_ids for w in result['witnesses'])
    rights_ids = {r['id'] for r in result['rights']}
    assert all(s['rights_id'] in rights_ids for s in result['sources'])
    assert len(result['poems']) < 312
    assert len(select(library, availability='checked')['poems']) == 33
    assert len(select(library, availability='text')['poems']) == 190
    assert len(select(library, availability='review')['poems']) == 157

def test_citation_preserves_text_and_rights(library):
    p = library['poems'][0]
    result = citation(p, library)
    assert p['text'] in result
    assert p['source']['citation'] in result
    assert 'independent human review' in result
    assert 'Licence / terms:' in result

def test_filters_match_original_semantics(library):
    assert 'Kimvita' in filters(library)['dialect']
    for name in ('origin', 'dialect', 'genre', 'source', 'status'):
        value = filters(library)[name][0]
        assert select(library, availability='all', **{name: value})['poems']
    assert select(library, search='DOES_NOT_EXIST')['poems'] == []


def test_collection_references_survive_filtered_exports(library):
    references=[d for d in library['source_documents'] if not d.get('source_id')]
    assert len(references)==13
    result=select(library,availability='checked')
    assert all(d in result['source_documents'] for d in references)
