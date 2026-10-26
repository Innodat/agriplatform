"""Closed, private read search. SQL filters saved owner data before keyset limiting."""
import base64
import hashlib
import json
import re
import unicodedata
from pydantic import TypeAdapter
from personal_notes_contract import Identifier,UtcTimestamp,_unique_object
from personal_notes_access import NotesError
from passage_references import ALIASES,BOOKS,CATALOGUE_ID,CATALOGUE_VERSION,normalize,parse_reference,ReferenceError


def canonical_query(text):
    text=unicodedata.normalize('NFC',text.strip())
    reference=None
    if text:
        try:reference=parse_reference(text)
        except ReferenceError:
            ids=ALIASES.get(normalize(text).replace('.',''),set())
            if len(ids)==1:
                book=BOOKS[next(iter(ids))]
                reference={'catalogue_id':CATALOGUE_ID,'catalogue_version':CATALOGUE_VERSION,
                           'versification_id':book['versification_id'],'book_id':book['book_id'],'target':None}
    return {'matching_version':1,'text':text,'reference':reference}


def digest(query):
    return hashlib.sha256(json.dumps(query,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def encode_cursor(account,query,created_at,identifier):
    value=['scribeswell.search.v1','studies',account,digest(query),created_at,identifier]
    return base64.urlsafe_b64encode(json.dumps(value,separators=(',',':')).encode()).decode().rstrip('=')


def decode_cursor(cursor,account,query):
    try:
        if type(cursor) is not str or not 1<=len(cursor)<=512 or not re.fullmatch('[A-Za-z0-9_-]+',cursor):raise ValueError
        value=json.loads(base64.b64decode(cursor+'='*((-len(cursor))%4),altchars=b'-_',validate=True).decode('utf8'),object_pairs_hook=_unique_object)
        if type(value) is not list or len(value)!=6 or value[:4]!=['scribeswell.search.v1','studies',account,digest(query)]:raise ValueError
        TypeAdapter(UtcTimestamp).validate_python(value[4]);TypeAdapter(Identifier).validate_python(value[5])
        if encode_cursor(account,query,*value[4:])!=cursor:raise ValueError
        return value[4:]
    except Exception:raise NotesError('scribeswell_personal_notes_input_invalid') from None


def array(expression):
    return f"CASE WHEN jsonb_typeof({expression})='array' THEN {expression} ELSE '[]'::jsonb END"


def keys(expression,names):
    # Equality to a rebuilt object guards extra as well as missing keys without unsafe object functions.
    return f"({expression} = jsonb_build_object("+','.join(f"'{name}',{expression}->'{name}'" for name in names)+'))'


def integer(expression):
    # CASE encloses the cast: the planner cannot evaluate a cast on unknown stored shapes.
    return f"(CASE WHEN jsonb_typeof({expression})='number' AND ({expression} #>> '{{}}') ~ '^[1-9][0-9]{{0,2}}$' THEN ({expression} #>> '{{}}')::integer END)"


def reference_match(expression):
    t=f"({expression}->'target')";sc=integer(f"{t}->'chapter'")
    ac=integer(f"{t}->'start'->'chapter'");av=integer(f"{t}->'start'->'verse'")
    bc=integer(f"{t}->'end'->'chapter'");bv=integer(f"{t}->'end'->'verse'")
    chapter=f"({t}->>'kind'='chapter' AND {keys(t,['kind','chapter'])} AND {sc} BETWEEN 1 AND jsonb_array_length(q.counts) AND ({sc},1)<=(q.ec,q.ev) AND (q.sc,q.sv)<=({sc},(q.counts->>({sc}-1))::integer))"
    bounds=f"{ac} BETWEEN 1 AND jsonb_array_length(q.counts) AND {bc} BETWEEN 1 AND jsonb_array_length(q.counts) AND {av} BETWEEN 1 AND (q.counts->>({ac}-1))::integer AND {bv} BETWEEN 1 AND (q.counts->>({bc}-1))::integer"
    start_keys=keys(f"{t}->'start'",['chapter','verse'])
    end_keys=keys(f"{t}->'end'",['chapter','verse'])
    ranges=f"({t}->>'kind'='verse_range' AND {keys(t,['kind','start','end'])} AND {start_keys} AND {end_keys} AND {bounds} AND ({ac},{av})<=({bc},{bv}) AND ({ac},{av})<=(q.ec,q.ev) AND (q.sc,q.sv)<=({bc},{bv}))"
    # Whole-book still validates stored target against this book's inventory.
    return f"({keys(expression,['catalogue_id','catalogue_version','versification_id','book_id','target'])} AND {expression}->>'catalogue_id'=q.ref->>'catalogue_id' AND {expression}->>'catalogue_version'=q.ref->>'catalogue_version' AND {expression}->>'versification_id'=q.ref->>'versification_id' AND {expression}->>'book_id'=q.ref->>'book_id' AND ({chapter} OR {ranges}))"


# Paragraph/list traversal is nonrecursive and every array expansion is type guarded.
PARAGRAPHS=f"""
 SELECT b.block AS p,b.bi,0::bigint AS ii,0::bigint AS pi
 FROM jsonb_array_elements({array("n.value->'document'->'blocks'")}) WITH ORDINALITY b(block,bi)
 WHERE b.block->>'type'='paragraph'
 UNION ALL
 SELECT p.p,b.bi,i.ii,p.pi
 FROM jsonb_array_elements({array("n.value->'document'->'blocks'")}) WITH ORDINALITY b(block,bi)
 CROSS JOIN LATERAL jsonb_array_elements({array("b.block->'items'")}) WITH ORDINALITY i(item,ii)
 CROSS JOIN LATERAL jsonb_array_elements({array('i.item')}) WITH ORDINALITY p(p,pi)
 WHERE b.block->>'type'='list' AND b.block->>'style' IN ('bullet','ordered') AND {keys('b.block',['type','style','items'])}
"""
TEXT_NODE=f"i.node->>'type'='text' AND {keys('i.node',['type','text','marks'])} AND jsonb_typeof(i.node->'text')='string' AND char_length(i.node->>'text') BETWEEN 1 AND 4096 AND i.node->'marks' IN ('[]'::jsonb,'[\"bold\"]'::jsonb,'[\"italic\"]'::jsonb,'[\"bold\",\"italic\"]'::jsonb)"
EXTERNAL_TEXT=f"""(SELECT string_agg(c.node->>'text','' ORDER BY c.ci)
 FROM jsonb_array_elements({array("i.node->'content'")}) WITH ORDINALITY c(node,ci)
 WHERE c.node->>'type'='text' AND {keys('c.node',['type','text','marks'])}
 AND jsonb_typeof(c.node->'text')='string' AND char_length(c.node->>'text') BETWEEN 1 AND 4096 AND c.node->'marks' IN ('[]'::jsonb,'["bold"]'::jsonb,'["italic"]'::jsonb,'["bold","italic"]'::jsonb))"""


def search_sql(account,query,position,limit):
    ref=query['reference'];book=BOOKS[ref['book_id']] if ref else None
    counts=book['chapter_verse_counts'] if book else []
    target=ref['target'] if ref else None
    if not target:sc,sv,ec,ev=1,1,len(counts),counts[-1] if counts else 1
    elif target['kind']=='chapter':sc,sv,ec,ev=target['chapter'],1,target['chapter'],counts[target['chapter']-1]
    else:sc,sv,ec,ev=target['start']['chapter'],target['start']['verse'],target['end']['chapter'],target['end']['verse']
    passage=reference_match("(i.node->'reference')")
    visible=f"""SELECT COALESCE(string_agg(paragraph.text,E'\\n' ORDER BY paragraph.bi,paragraph.ii,paragraph.pi),'') AS text,
 bool_or(paragraph.reference_match) AS reference_match FROM (
 SELECT p.bi,p.ii,p.pi,COALESCE(string_agg(CASE
 WHEN {TEXT_NODE} THEN i.node->>'text'
 WHEN i.node->>'type'='external_link' AND {keys('i.node',['type','url','content'])} AND jsonb_typeof(i.node->'url')='string' THEN {EXTERNAL_TEXT}
 WHEN n.value->'document'->'version'='2'::jsonb AND i.node->>'type'='passage_link' AND {keys('i.node',['type','reference','label'])} AND jsonb_typeof(i.node->'label')='string' AND char_length(i.node->>'label') BETWEEN 1 AND 200 THEN i.node->>'label'
 ELSE '' END,'' ORDER BY i.ni),'') AS text,
 bool_or(n.value->'document'->'version'='2'::jsonb AND i.node->>'type'='passage_link' AND {keys('i.node',['type','reference','label'])} AND jsonb_typeof(i.node->'label')='string' AND char_length(i.node->>'label') BETWEEN 1 AND 200 AND {passage}) AS reference_match
 FROM ({PARAGRAPHS}) p
 LEFT JOIN LATERAL jsonb_array_elements({array("p.p->'content'")}) WITH ORDINALITY i(node,ni) ON true
 WHERE p.p->>'type'='paragraph' AND {keys('p.p',['type','direction','content'])} AND p.p->>'direction' IN ('auto','ltr','rtl')
 GROUP BY p.bi,p.ii,p.pi) paragraph"""
    aggregate_reference=reference_match('r.reference')
    aggregate_refs=f"""SELECT c.node->'reference' AS reference FROM jsonb_array_elements({array("n.value->'connections'")}) c(node)
 UNION ALL SELECT segment.node->'reference' FROM jsonb_array_elements({array("n.value->'highlights'")}) h(node)
 CROSS JOIN LATERAL jsonb_array_elements({array("h.node->'anchor'->'segments'")}) segment(node)"""
    boundary=' AND (s.created_at,s.id)<(%s::timestamptz,%s::uuid)' if position else ''
    sql=f"""WITH q AS (SELECT %s::uuid AS account,%s::text AS text,%s::jsonb AS ref,%s::jsonb AS counts,%s::int AS sc,%s::int AS sv,%s::int AS ec,%s::int AS ev)
 SELECT s.* FROM scribeswell_studies.studies s CROSS JOIN q
 WHERE s.account_id=q.account AND s.active AND (q.text=''
 OR POSITION(lower(q.text) IN lower(normalize(s.title,NFC)))>0
 OR EXISTS (SELECT 1 FROM scribeswell_studies.notes n CROSS JOIN LATERAL ({visible}) v
 WHERE n.account_id=q.account AND n.study_id=s.id AND n.active
 AND n.value->'document'->'version' IN ('1'::jsonb,'2'::jsonb)
 AND {keys("n.value->'document'",['version','blocks'])}
 AND (POSITION(lower(q.text) IN lower(normalize(v.text,NFC)))>0 OR v.reference_match))
 OR EXISTS (SELECT 1 FROM scribeswell_studies.notes n CROSS JOIN LATERAL ({aggregate_refs}) r
 WHERE n.account_id=q.account AND n.study_id=s.id AND n.active AND n.value->'format_version'='3'::jsonb AND {aggregate_reference})
 OR EXISTS (SELECT 1 FROM scribeswell_studies.passage_entries e
 WHERE e.account_id=q.account AND e.study_id=s.id AND s.active
 AND e.catalogue_id=q.ref->>'catalogue_id' AND e.catalogue_version=q.ref->>'catalogue_version'
 AND e.versification_id=q.ref->>'versification_id' AND e.book_id=q.ref->>'book_id'
 AND e.start_chapter BETWEEN 1 AND jsonb_array_length(q.counts)
 AND ((e.kind='chapter' AND (e.start_chapter,1)<=(q.ec,q.ev) AND (q.sc,q.sv)<=(e.start_chapter,(q.counts->>(e.start_chapter-1))::integer))
 OR (e.kind='verse_range' AND e.end_chapter BETWEEN 1 AND jsonb_array_length(q.counts)
 AND e.start_verse BETWEEN 1 AND (q.counts->>(e.start_chapter-1))::integer
 AND e.end_verse BETWEEN 1 AND (q.counts->>(e.end_chapter-1))::integer
 AND (e.start_chapter,e.start_verse)<=(q.ec,q.ev) AND (q.sc,q.sv)<=(e.end_chapter,e.end_verse)))))
 {boundary} ORDER BY s.created_at DESC,s.id DESC LIMIT %s"""
    values=[account,query['text'],json.dumps(ref),json.dumps(counts),sc,sv,ec,ev]
    if position:values.extend(position)
    values.append(limit+1)
    return sql,values
