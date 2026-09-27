"""Immutable lexical reference data; no source markup reaches the browser as HTML."""
from functools import lru_cache
import json
from pathlib import Path
import re

ARTIFACT = Path(__file__).resolve().parents[2] / 'data/hebrew-lexicon/lexicon.json'


def lexical_id(raw: str | None) -> str | None:
    parts = [part.strip().removeprefix('H') for part in (raw or '').split('/')]
    identities = [part for part in parts if re.fullmatch(r'[1-9][0-9]*(?:\s+[a-z])?', part)]
    return identities[0] if len(identities) == 1 else None


@lru_cache(maxsize=1)
def artifact():
    return json.loads(ARTIFACT.read_text())


def get_entry(identity: str):
    try:
        entry = artifact()['entries'].get(identity)
    except (OSError, ValueError, KeyError):
        return {'status': 'unavailable', 'lexical_id': identity}
    return {'status': 'available', **entry} if entry else {'status': 'missing', 'lexical_id': identity}


def match_metadata(raw: str | None, morphology: str | None):
    identity = lexical_id(raw)
    if not identity:
        return {'lexical_id': None, 'match_key': None}
    entry = get_entry(identity)
    # Only noun/verb relationships expand to recorded roots; other words use lemma.
    content = [p for p in (morphology or '').removeprefix('H').removeprefix('A').split('/') if p.startswith(('N', 'V'))]
    root = entry.get('root') if content else None
    return {'lexical_id': identity, 'match_key': f"root:{root['id']}" if root else f'lemma:{identity}'}


@lru_cache(maxsize=1)
def lemma_variants():
    """Raw import spellings for exact lexical matching, without editing the source."""
    source = Path(__file__).resolve().parents[2] / 'scripts/hebrew.json'
    result = {}
    for chapters in json.loads(source.read_text()).values():
        for verses in chapters:
            for words in verses:
                for fields in words:
                    # The canonical export stores lemma before surface.
                    for raw in fields[:2]:
                        identity = lexical_id(raw)
                        if identity:
                            result.setdefault(identity, set()).add(raw)
    return {key: sorted(value) for key, value in result.items()}
