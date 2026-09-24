"""Canonical data stays intact; these projections never rewrite source metadata."""
from datetime import datetime, timezone

KINDS = ('rights', 'sources', 'poems', 'witnesses', 'source_documents')


def validate(library):
    indexes = {}
    for kind in KINDS:
        rows = library[kind]
        indexes[kind] = {row['id']: row for row in rows}
        if len(indexes[kind]) != len(rows):
            raise ValueError(f'duplicate {kind} identity')
    for source in library['sources']:
        if source['rights_id'] not in indexes['rights']: raise ValueError('missing source rights')
    for poem in library['poems']:
        if poem['source_id'] not in indexes['sources']: raise ValueError('missing poem source')
    for witness in library['witnesses']:
        if witness['source_id'] not in indexes['sources'] or witness['poem_id'] not in indexes['poems']:
            raise ValueError('missing witness relationship')
    for document in library['source_documents']:
        if document.get('source_id') and document['source_id'] not in indexes['sources']:
            raise ValueError('missing document source')
    return dict(poems=len(library['poems']), texts=sum(bool(p.get('text')) for p in library['poems']),
                checked=sum(checked(p) for p in library['poems']), witnesses=len(library['witnesses']),
                sources=len(library['sources']), rights=len(library['rights']))


def checked(poem):
    return bool(poem.get('text')) and poem['quality'].get('text_status') == 'checked_transcription' and poem['quality'].get('complete_in_witness') is True


def attributes(poem):
    geo = poem.get('geography', {})
    origin = geo.get('origin_locality') or 'Not established'
    # Match the original UI's compact grouping; evidence retains the full qualifier.
    for place in ('Mombasa', 'Zanzibar', 'Lubumbashi', 'Siu', 'Pate'):
        if origin.startswith(place): origin = place; break
    dialect = geo.get('dialect') or 'Not established'
    for name in ('Kimvita', 'Kitumbatu', 'Lubumbashi Swahili'):
        if dialect.startswith(name): dialect = name; break
    return dict(origin=origin, dialect=dialect, source=poem['source_id'],
                genre=poem.get('classification', {}).get('genre') or 'Not established',
                status=poem['quality']['text_status'])


def filters(library):
    return {key: sorted({attributes(p)[key] for p in library['poems']})
            for key in ('origin', 'dialect', 'source', 'genre', 'status')}


def select(library, search='', availability='text', **criteria):
    def matches(p):
        a = attributes(p)
        words = [p['title'], p.get('creator', {}).get('name'), *p.get('geography', {}).values(),
                 p.get('classification', {}).get('genre'), p.get('classification', {}).get('formal_poetry_type')]
        if search.strip().casefold() not in ' '.join(str(w or '') for w in words).casefold(): return False
        if any(value and a[key] != value for key, value in criteria.items() if key in a): return False
        if availability == 'text' and not p.get('text'): return False
        if availability == 'checked' and not checked(p): return False
        if availability == 'review' and (not p.get('text') or checked(p)): return False
        return True
    poems = [p for p in library['poems'] if matches(p)]
    ids = {p['id'] for p in poems}
    witnesses = [w for w in library['witnesses'] if w['poem_id'] in ids]
    sids = {p['source_id'] for p in poems} | {w['source_id'] for w in witnesses}
    sources = [s for s in library['sources'] if s['id'] in sids]
    rids = {s['rights_id'] for s in sources}
    return dict(schema_version=library['schema_version'], exported_at=datetime.now(timezone.utc).isoformat(),
                note='Filtered collection. Source checks do not establish human verification, rights clearance or training readiness.',
                poems=poems, witnesses=witnesses, sources=sources,
                rights=[r for r in library['rights'] if r['id'] in rids],
                source_documents=[d for d in library['source_documents'] if not d.get('source_id') or d.get('source_id') in sids])


def citation(poem, library):
    source = next(s for s in library['sources'] if s['id'] == poem['source_id'])
    rights = next(r for r in library['rights'] if r['id'] == source['rights_id'])
    quality = poem['quality']
    lines = [poem['title'], 'Poet: ' + (poem.get('creator', {}).get('name') or 'Unattributed'),
             poem.get('text') or '[Text not collected]', 'Text status: ' + quality['text_status'].replace('_', ' '),
             'Review note: ' + (quality.get('reviewer_note') or 'No review recorded'),
             'Complete in cited witness: ' + ('yes' if quality.get('complete_in_witness') else 'not confirmed'),
             'Source: ' + poem['source']['citation'], poem['source'].get('locator'), poem['source'].get('url')]
    for label, key in [('Attribution', 'attribution'), ('Reuse assessment', 'assessment'), ('Licence / terms', 'licence'),
                       ('Research use', 'research_use'), ('Publication / reuse', 'publication_and_commercial_use')]:
        lines.append(label + ': ' + (rights.get(key) or 'See source rights'))
    lines.append('Record: ' + poem['id'])
    return '\n\n'.join(str(line) for line in lines if line)


def text_export(selection):
    parts = [citation(p, selection) for p in selection['poems']]
    for w in selection['witnesses']:
        s = next(s for s in selection['sources'] if s['id'] == w['source_id'])
        r = next(r for r in selection['rights'] if r['id'] == s['rights_id'])
        import json
        parts.append('Alternate witness (not concatenated with main text):\n' + json.dumps(w, ensure_ascii=False, indent=2)
                     + '\nSource and rights:\n' + json.dumps({'source': s, 'rights': r}, ensure_ascii=False, indent=2))
    return '\n\n====================\n\n'.join(parts)
