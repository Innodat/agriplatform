"""Whole-note admission against fresh public observations and trusted saved metadata."""
from personal_notes_access import NotesError,remaining
from highlight_evidence import segment_status,IDENTITY

def metadata(value):
    references=[c['reference'] for c in value.get('connections',[])]
    references.extend(s['reference'] for h in value.get('highlights',[]) for s in h['anchor']['segments'])
    for block in value.get('document',{}).get('blocks',[]):
        for paragraph in [block] if block.get('type')=='paragraph' else [p for item in block.get('items',[]) for p in item]:
            references.extend(i['reference'] for i in paragraph.get('content',[]) if i.get('type')=='passage_link')
    import json
    references=list({json.dumps(r,sort_keys=True):r for r in references}.values())
    return {'connections':value.get('connections',[]),'highlights':[{'id':h['id'],'anchor':h['anchor']} for h in value.get('highlights',[])],'references':references}

def segment_input(anchor,segment):
    point=segment['reference']['target']['start']
    return {**{key:anchor[key] for key in (*IDENTITY,'source_revision')},'book':segment['reference']['book_id'],**point,
            **{key:segment[key] for key in ('start_position','end_position','observed_word_ids','verse_token_digest')}}

def validate(value,prior,observations):
    trusted={h['id']:h['anchor'] for h in prior.get('highlights',[])}
    for highlight in value.get('highlights',[]):
        anchor=highlight['anchor']
        if trusted.get(highlight['id'])==anchor:continue
        for index,segment in enumerate(anchor['segments']):
            ref=segment['reference'];point=ref['target']['start'];key=(ref['book_id'],point['chapter'],point['verse'])
            evidence=observations.get(key,{'status':'unavailable'})
            if evidence.get('status')!='ready':raise NotesError('highlight_proof_unavailable')
            current=segment_input(anchor,segment)
            if segment_status(current,evidence)!='valid' or anchor['source_revision']!=evidence['source_revision'] or segment['observed_word_ids']!=evidence['observed_word_ids'][segment['start_position']-1:segment['end_position']]:raise NotesError('highlight_proof_invalid')
            if index<len(anchor['segments'])-1 and segment['end_position']!=evidence['token_count']:raise NotesError('highlight_proof_invalid')

def observe(value,deadline):
    """Fresh actual source reads only; called before any private transaction locks."""
    from database import get_database
    from reader_evidence import observed
    result={}
    try:
        db=get_database()
        groups={}
        for highlight in value.get('highlights',[]):
            for segment in highlight['anchor']['segments']:
                ref=segment['reference'];point=ref['target']['start']
                groups.setdefault((ref['book_id'],point['chapter']),set()).add(point['verse'])
        with db.reader_snapshot():
            books={}
            for (book_id,chapter),numbers in groups.items():
                remaining(deadline)
                if book_id not in books:books[book_id]=db.one('book',columns='id',filters={'osis_id':book_id},order=())
                book=books[book_id]
                verses=db.read('verse',columns='id,verse_num',filters={'book_id':book['id'],'chapter_num':chapter},in_filters={'verse_num':sorted(numbers)},order=('verse_num',)) if book else []
                words=db.read('word',columns='id,verse_id,position,surface_he',in_filters={'verse_id':[v['id'] for v in verses]},order=('verse_id','position')) if verses else []
                grouped={v['id']:[] for v in verses}
                for word in words:
                    if word['verse_id'] in grouped:grouped[word['verse_id']].append(word)
                publications=db.reader_publications(book_id,chapter,sorted(numbers))
                for verse in verses:
                    result[(book_id,chapter,verse['verse_num'])]=observed(db,book_id,chapter,verse['verse_num'],grouped[verse['id']],publications.get(verse['verse_num']))
            remaining(deadline)
    except Exception:
        # Missing public proof never blocks exact saved-anchor preservation/replay.
        return {}
    return result
