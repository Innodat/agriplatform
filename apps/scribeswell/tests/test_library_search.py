"""Component proof; native matching qualification is deliberately separate."""
import asyncio
from contextlib import asynccontextmanager
import json
from pathlib import Path
import sys
import time
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from personal_notes_contract import parse_command,ContractInputError
from personal_notes_search import canonical_query,encode_cursor,decode_cursor,search_sql
from personal_notes_storage import PersonalNotesStorage
from personal_notes_access import NotesError

A='10000000-0000-4000-8000-000000000001'
ID='30000000-0000-4000-8000-000000000001'
STAMP='2026-10-25T10:00:00.000000Z'

def test_beyond_first_unfiltered_page_is_filtered_inside_database_before_limit():
    sql,values=search_sql(A,canonical_query('saved writing'),None,20)
    assert 'EXISTS' in sql and 'notes' in sql and 'passage_entries' in sql
    assert sql.index('POSITION(')<sql.index('ORDER BY s.created_at DESC,s.id DESC LIMIT')
    assert values[-1]==21
    assert 'ILIKE' not in sql and '::text' not in sql.split('POSITION(')[1].split('>0')[0]

def test_strict_search_body():
    body=parse_command('studies.search',b'{"query":"  cafe\\u0301  "}')
    assert body.query=='  cafe\u0301  ' and body.limit==20 and body.cursor is None
    for raw in (b'{}',b'{"query":"x","query":"y"}',b'{"query":"x","limit":true}',b'{"query":"x","limit":1.0}',b'{"query":"x","operation_id":"x"}',b'{"query":"\\u0000"}',b'{"query":"\\ud800"}',json.dumps({'query':'x'*201}).encode(),b' '*4097):
        with pytest.raises(ContractInputError):parse_command('studies.search',raw)

def test_nfc_literal_query_and_closed_reference_interpretation():
    assert canonical_query('  cafe\u0301  ')['text']=='café'
    for text in ('100% _ \\ "','שָׁלוֹם','Gen 999','Gen 1:3-2'):
        assert canonical_query(text)['reference'] is None
    for text in ('Genesis 1:31–2:2','בראשית א:לא–ב:ב','Matthew'):
        assert canonical_query(text)['reference']['book_id'] in ('Gen','Matt')
    assert canonical_query('Matthew')['reference']['target'] is None

def test_cursor_binds_full_query_account_and_closed_canonical_encoding():
    query=canonical_query('Genesis 1');cursor=encode_cursor(A,query,STAMP,ID)
    assert len(cursor)<=512 and decode_cursor(cursor,A,query)==[STAMP,ID]
    for account,q,value in ((ID,query,cursor),(A,canonical_query('Genesis 2'),cursor),(A,query,cursor+'='),(A,query,'garbage')):
        with pytest.raises(NotesError):decode_cursor(value,account,q)

def test_search_http_is_read_only_and_rejects_private_query_urls():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from personal_notes_router import build_router
    calls=[]
    class Access:
        async def check(self,bearer,deadline):calls.append('check');return {'account_id':A}
    class Storage:
        async def search(self,identity,payload,deadline):
            calls.append(('search',identity,payload.query,payload.limit,payload.cursor));return {'items':[],'next_cursor':None}
    app=FastAPI();app.include_router(build_router(Access(),Storage()));client=TestClient(app)
    result=client.post('/api/studies/search',headers={'Authorization':'Bearer current'},json={'query':'saved writing'})
    assert result.status_code==200 and result.json()=={'items':[],'next_cursor':None}
    assert result.headers['cache-control']=='private, no-store'
    assert calls[0]=='check' and calls[1][0]=='search'
    for raw in ('{"query":"x","limit":true}','{"query":"x","query":"y"}','{"query":"\\u0000"}'):
        calls.clear();bad=client.post('/api/studies/search',headers={'Authorization':'Bearer current'},content=raw)
        assert bad.status_code==400 and calls==[] and bad.json()['details'] is None
    calls.clear();bad=client.post('/api/studies/search?query=private',headers={'Authorization':'Bearer current'},json={'query':''})
    assert bad.status_code==400 and calls==[]

@pytest.mark.parametrize('query',['','  ','100%_\\','Gen 1','Genesis 1:31–2:3','בראשית א:לא–ב:ב','Matthew','invalid reference 999'])
def test_search_storage_method_uses_one_filtered_read_and_no_write(query):
    statements=[]
    class Cursor:
        async def execute(self,sql,values):statements.append((sql,values))
        async def fetchall(self):return []
    class Storage(PersonalNotesStorage):
        @asynccontextmanager
        async def transaction(self,identity,deadline,*,write=False):
            assert write is False;yield Cursor()
    body=parse_command('studies.search',json.dumps({'query':query}).encode())
    result=asyncio.run(Storage('unused').search({'account_id':A},body,time.monotonic()+5))
    assert result=={'items':[],'next_cursor':None} and len(statements)==1
    sql,values=statements[0]
    assert values[1]==canonical_query(query)['text'] and values[-1]==21
    assert all(term not in sql for term in ('INSERT INTO','UPDATE ','DELETE FROM','receipts','FOR UPDATE'))

@pytest.mark.parametrize('raw',[
    b'{"query":null}',b'{"query":7}',b'{"query":"x","limit":0}',b'{"query":"x","limit":51}',
    b'{"query":"x","limit":"20"}',b'{"query":"x","cursor":""}',b'{"query":"x","cursor":false}',
    b'{"query":"x","cursor":"="}',b'\xef\xbb\xbf{"query":"x"}',b'{"query":"x"} {}',
    b'{"query":"\xff"}',b'{"query":"x","extra":NaN}',b'{"query":"x","extra":'+b'['*17+b'0'+b']'*17+b'}',
])
def test_search_strict_invalid_transport_matrix(raw):
    with pytest.raises(ContractInputError):parse_command('studies.search',raw)


def test_search_cursor_refuses_list_version_extra_fields_and_query_plaintext():
    import base64
    from personal_notes_cursor import encode
    query=canonical_query('private saved writing')
    cursor=encode_cursor(A,query,STAMP,ID)
    decoded=base64.urlsafe_b64decode(cursor+'='*((-len(cursor))%4))
    assert b'private saved writing' not in decoded
    with pytest.raises(NotesError):decode_cursor(encode('studies',A,None,STAMP,ID),A,query)
    fields=json.loads(decoded);fields.append('extra')
    bad=base64.urlsafe_b64encode(json.dumps(fields,separators=(',',':')).encode()).decode().rstrip('=')
    with pytest.raises(NotesError):decode_cursor(bad,A,query)


def test_search_query_schema_agrees_on_nul_blank_and_scalar_unicode():
    from jsonschema import validate,ValidationError
    from personal_notes_contract import openapi_contract
    schema=openapi_contract()['components']['schemas']['SearchStudies']['properties']['query']
    with pytest.raises(ValidationError):validate('\x00',schema)
    with pytest.raises(ContractInputError):parse_command('studies.search',b'{"query":"\\u0000"}')
    for query in ('','שלום','😀','cafe\u0301'):
        validate(query,schema)
        assert parse_command('studies.search',json.dumps({'query':query}).encode()).query==query
    assert 'scalar' in schema['description']
