"""Public evidence adapter. Caller must hold Database.reader_snapshot throughout."""
from highlight_evidence import observe_verse
from passage_references import make_reference

UNAVAILABLE={'version':1,'status':'unavailable'}
UNSET=object()

def observed(db,book,chapter,verse,words,publication=UNSET):
    if publication is UNSET:publication=db.reader_publication(book,chapter,verse)
    if not publication:return dict(UNAVAILABLE)
    try:
        reference=make_reference(book,{'kind':'verse_range','start':{'chapter':chapter,'verse':verse},'end':{'chapter':chapter,'verse':verse}})
        if publication['catalogue_version']!=reference['catalogue_version'] or publication['versification_id']!=reference['versification_id']:return dict(UNAVAILABLE)
        result=observe_verse(publication,[{'id':str(word['id']),'position':word['position'],'surface_he':word['surface_he']} for word in words])
        if result['status']=='ready':result['reference']=reference
        return result
    except (KeyError,ValueError,TypeError):return dict(UNAVAILABLE)
