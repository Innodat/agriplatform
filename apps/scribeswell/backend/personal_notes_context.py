"""Bounded own-note context discovery; reuse canonical search overlap and traversal."""
import json
from pydantic import TypeAdapter
from personal_notes_contract import NoteValue, ContextNote
from personal_notes_search import BOOKS, PARAGRAPHS, array, keys, reference_match


def context_query(reference):
    return {'matching_version':1,'resource':'context-notes','reference':reference}


def context_sql(account,reference,position,limit):
    counts=BOOKS[reference['book_id']]['chapter_verse_counts'];target=reference['target']
    if target['kind']=='chapter':sc,sv,ec,ev=target['chapter'],1,target['chapter'],counts[target['chapter']-1]
    else:sc,sv,ec,ev=target['start']['chapter'],target['start']['verse'],target['end']['chapter'],target['end']['verse']
    refs=f"""SELECT c.node->'reference' AS reference
 FROM jsonb_array_elements({array("n.value->'connections'")}) c(node)
 WHERE n.value->'format_version'='3'::jsonb AND {keys('c.node',['id','reference'])}
 UNION ALL SELECT segment.node->'reference'
 FROM jsonb_array_elements({array("n.value->'highlights'")}) h(node)
 CROSS JOIN LATERAL jsonb_array_elements({array("h.node->'anchor'->'segments'")}) segment(node)
 WHERE n.value->'format_version'='3'::jsonb
 UNION ALL SELECT i.node->'reference' FROM ({PARAGRAPHS}) p
 CROSS JOIN LATERAL jsonb_array_elements({array("p.p->'content'")}) i(node)
 WHERE n.value->'document'->'version'='2'::jsonb
 AND {keys('p.p',['type','direction','content'])} AND p.p->>'direction' IN ('auto','ltr','rtl')
 AND i.node->>'type'='passage_link' AND {keys('i.node',['type','reference','label'])}
 AND jsonb_typeof(i.node->'label')='string' AND char_length(i.node->>'label') BETWEEN 1 AND 200"""
    boundary=' AND (n.created_at,n.id)<(%s::timestamptz,%s::uuid)' if position else ''
    sql=f"""WITH q AS (SELECT %s::uuid AS account,%s::jsonb AS ref,%s::jsonb AS counts,%s::int AS sc,%s::int AS sv,%s::int AS ec,%s::int AS ev)
 SELECT n.*,s.title AS study_title FROM scribeswell_studies.notes n
 JOIN scribeswell_studies.studies s ON s.account_id=n.account_id AND s.id=n.study_id
 CROSS JOIN q WHERE n.account_id=q.account AND s.account_id=q.account
 AND n.active AND s.active AND n.visibility='study'
 AND n.value->'document'->'version' IN ('1'::jsonb,'2'::jsonb)
 AND (n.value->'format_version'='3'::jsonb OR (NOT (n.value ? 'format_version') AND n.value->'connections'='[]'::jsonb AND n.value->'highlights'='[]'::jsonb))
 AND {keys("n.value->'document'",['version','blocks'])}
 AND EXISTS(SELECT 1 FROM ({refs}) r WHERE {reference_match('r.reference')})
 {boundary} ORDER BY n.created_at DESC,n.id DESC LIMIT %s"""
    values=[account,json.dumps(reference),json.dumps(counts),sc,sv,ec,ev]
    if position:values.extend(position)
    return sql,[*values,limit+1]


def context_item(row):
    value=TypeAdapter(NoteValue).validate_json(json.dumps(row['value'])).model_dump(mode='json')
    refs=[c['reference'] for c in value['connections']]
    refs.extend(s['reference'] for h in value['highlights'] for s in h['anchor']['segments'])
    text=[]
    for block in value['document']['blocks']:
        for paragraph in [block] if block['type']=='paragraph' else [p for item in block['items'] for p in item]:
            line=[]
            for inline in paragraph['content']:
                if inline['type']=='passage_link':refs.append(inline['reference']);line.append(inline['label'])
                elif inline['type']=='text':line.append(inline['text'])
                else:line.append(''.join(t['text'] for t in inline['content']))
            text.append(''.join(line))
    unique=list({json.dumps(ref,sort_keys=True):ref for ref in refs}.values())[:256]
    return ContextNote.model_validate_json(json.dumps({'study_id':str(row['study_id']),'study_title':row['study_title'],
        'owner_account_id':str(row['account_id']),'note_id':str(row['id']),'revision':str(row['revision']),
        'preview':' '.join(text)[:120],'references':unique})).model_dump(mode='json')
