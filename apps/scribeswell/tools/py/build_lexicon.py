"""Build the pinned HebrewLexicon snapshot into safe deterministic reference JSON."""
import argparse
import ast
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

DIRECTORY = Path(__file__).resolve().parents[2] / 'data/hebrew-lexicon'
NS = '{http://openscriptures.github.com/morphhb/namespace}'


def parse(data):
    if len(data) > 12_000_000 or re.search(br'<!\s*(?:DOCTYPE|ENTITY)', data, re.I):
        raise ValueError('Unsafe or oversized XML')
    root = ET.fromstring(data)
    for node in root.iter():
        node.tag = node.tag.removeprefix(NS)
    return root


def text(node):
    return ' '.join(''.join(node.itertext()).split()) if node is not None else ''


@lru_cache(maxsize=1)
def corpus_bounds():
    """Reuse importer book metadata and canonical collection chapter/verse bounds."""
    importer = ast.parse((Path(__file__).parent / 'import_bible.py').read_text())
    metadata = next(ast.literal_eval(node.value) for node in importer.body
                    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
                    and node.target.id == 'BOOK_METADATA')
    corpus = json.loads((DIRECTORY.parents[1] / 'scripts/hebrew.json').read_text())
    return {book['osis_id']: [len(chapter) for chapter in corpus[book['name_en']]]
            for book in metadata if book['name_en'] in corpus}


def valid_reference(book, chapter, verse):
    chapters = corpus_bounds().get(book, [])
    return 1 <= chapter <= len(chapters) and 1 <= verse <= chapters[chapter - 1]


def blocks(node, inherited_language="heb", resolver=lambda value: None):
    """Preserve mixed-content separators and safe language/direction boundaries."""
    result = []
    if node.text:
        result.append({'kind': 'text', 'text': re.sub(r'\s+', ' ', node.text)})
    for child in node:
        if child.tag == 'sense':
            result.append({'kind': 'sense', 'text': child.get('n', ''), 'children': blocks(child, inherited_language, resolver)})
        elif child.tag == 'ref' and re.fullmatch(r'[1-3]?[A-Za-z]+\.[1-9][0-9]*\.[1-9][0-9]*', child.get('r', '')):
            book, chapter, verse = child.get('r').split('.')
            if valid_reference(book, int(chapter), int(verse)):
                result.append({'kind': 'reference', 'text': text(child), 'book': book, 'chapter': int(chapter), 'verse': int(verse)})
            else:
                result.extend(blocks(child, inherited_language, resolver))
        elif child.tag in ('w', 'foreign'):
            language = child.get('{http://www.w3.org/XML/1998/namespace}lang', inherited_language if child.tag == 'w' else 'und')
            language = {'heb': 'he', 'ara': 'ar', 'lat': 'la'}.get(language, language)
            if not re.fullmatch(r'[a-z]{2,3}(?:-[A-Za-z0-9]+)*', language):
                language = 'und'
            target = resolver(child.get('src', '')) if child.tag == 'w' else None
            result.append({'kind': 'dictionary_reference' if target else 'language',
                           'text': text(child) if target else '', 'language': language,
                           'direction': 'rtl' if language in ('he', 'ar', 'arc', 'syr') else 'auto',
                           **({'lexical_id': target} if target else {}),
                           'children': blocks(child, language, resolver)})
        elif child.tag not in ('status', 'page', 'script', 'style'):
            result.extend(blocks(child, inherited_language, resolver))
        if child.tail:
            result.append({'kind': 'text', 'text': re.sub(r'\s+', ' ', child.tail)})
    return result


def build():
    manifest = json.loads((DIRECTORY / 'manifest.json').read_text())
    trees = {}
    for name in ('AugIndex.xml', 'LexicalIndex.xml', 'HebrewStrong.xml', 'BrownDriverBriggs.xml'):
        data = (DIRECTORY / name).read_bytes()
        # Manifest structure is verified by the acquisition command and independently below.
        expected = manifest['files'][name]['sha256']
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f'Checksum mismatch: {name}')
        trees[name] = parse(data)
    lexical = {e.get('id'): e for e in trees['LexicalIndex.xml'].iter('entry')}
    strong = {e.get('id'): e for e in trees['HebrewStrong.xml'].iter('entry')}
    bdb = {e.get('id'): e for e in trees['BrownDriverBriggs.xml'].iter('entry')}
    bdb_languages = {entry.get('id'): part.get('{http://www.w3.org/XML/1998/namespace}lang', 'heb')
                     for part in trees['BrownDriverBriggs.xml'].iter('part') for entry in part.iter('entry')}
    # Only explicit references with exactly one available augmented identity
    # become links. In particular H1254 must never choose between its homonyms.
    mappings = [(re.sub(r'(?<=\d)([a-z])$', r' \1', m.get('aug')), text(m))
                for m in trees['AugIndex.xml'].iter('w') if text(m) in lexical]
    targets = {}
    for identity, key in mappings:
        xref = lexical[key].find('xref')
        refs = [key, 'H' + identity.split()[0]]
        if xref is not None and xref.get('bdb'):
            refs.append(xref.get('bdb'))
        for ref in refs:
            targets.setdefault(ref, set()).add(identity)
    def resolve(ref):
        candidates = targets.get(ref, set())
        return next(iter(candidates)) if len(candidates) == 1 else None

    def root_for(key, seen=None):
        seen = set() if seen is None else seen
        if key in seen or key not in lexical:
            return None
        seen.add(key)
        etym = lexical[key].find('etym')
        if etym is None:
            return None
        if etym.get('root'):
            return {'id': key, 'text': etym.get('root'), 'lexical_id': resolve(key)}
        target = text(etym)
        return root_for(target, seen) if etym.get('type') == 'sub' and target in lexical else None
    entries = {}
    for mapping in trees['AugIndex.xml'].iter('w'):
        identity, key = re.sub(r'(?<=\d)([a-z])$', r' \1', mapping.get('aug')), text(mapping)
        entry = lexical.get(key)
        if entry is None:
            continue
        word, xref = entry.find('w'), entry.find('xref')
        detail = strong.get('H' + identity.split()[0])
        sw = detail.find('w') if detail is not None else None
        outline = bdb.get(xref.get('bdb')) if xref is not None else None
        entries[identity] = {'lexical_id': identity, 'entry_id': key, 'lemma': text(word), 'transliteration': word.get('xlit', '') if word is not None else '', 'definition': text(entry.find('def')), 'root': root_for(key), 'pronunciation': sw.get('pron', '') if sw is not None else '', 'strong_definition': text(detail.find('meaning')) if detail is not None else '', 'strong_usage': text(detail.find('usage')) if detail is not None else '', 'strong_source': text(detail.find('source')) if detail is not None else '', 'bdb': blocks(outline, bdb_languages.get(outline.get('id'), 'heb'), resolve) if outline is not None else [], 'bdb_status': text(outline.find('status')) if outline is not None else 'missing'}
        for field, tag in [('strong_definition_nodes', 'meaning'), ('strong_usage_nodes', 'usage'), ('strong_source_nodes', 'source')]:
            source = detail.find(tag) if detail is not None else None
            entries[identity][field] = blocks(source, resolver=resolve) if source is not None else []
    result = {'entries': entries, 'coverage': {'entries': len(entries), 'recorded_roots': sum(bool(e['root']) for e in entries.values())}}
    (DIRECTORY / 'lexicon.json').write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n')
    print(result['coverage'])

def acquire():
    """Reacquire only manifest-pinned HTTPS files, verifying bytes before replacement."""
    from urllib.request import urlopen
    manifest = json.loads((DIRECTORY / 'manifest.json').read_text())
    prefix = f"https://raw.githubusercontent.com/openscriptures/HebrewLexicon/{manifest['revision']}/"
    for name, record in manifest['files'].items():
        if '/' in name or not record['url'].startswith(prefix):
            raise ValueError('Unexpected source path')
        with urlopen(record['url'], timeout=30) as response:
            data = response.read(12_000_001)
        if len(data) != record['bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
            raise ValueError(f'Checksum mismatch: {name}')
        (DIRECTORY / name).write_bytes(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acquire', action='store_true', help='Download the exact manifest-pinned source files before building')
    if parser.parse_args().acquire:
        acquire()
    build()
