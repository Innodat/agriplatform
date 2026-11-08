"""Authenticated conditional corpus reads; synthetic corpus never needs private files."""
from copy import deepcopy
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from apps.pts.backend.main import create_app

class Access:
    status=200
    account='reader-a'
    calls=0
    def verify(self,token,permission):
        self.calls+=1
        if self.status!=200:raise HTTPException(self.status,{'code':'access_denied'})
        return {'actor_id':'actor','account_id':self.account}

class Repo:
    library={'schema_version':'1.2','poems':[{'id':'p','title':'Poem','text':'Verse','source_id':'s','quality':{'text_status':'checked_transcription','complete_in_witness':True},'source':{'citation':'Source'}}], 'sources':[{'id':'s','title':'Source','rights_id':'r'}], 'rights':[{'id':'r','licence':'CC BY 4.0','assessment':'Original terms'}], 'witnesses':[], 'source_documents':[]}
    def __init__(self):self.library=deepcopy(self.library)
    def read(self,actor):return self.library
    def sources(self,actor):return {k:self.library[k] for k in ('sources','rights','source_documents')}

@pytest.fixture
def boundary():
    access=Access();repo=Repo()
    return TestClient(create_app(access=access,repository=repo)),access,repo

@pytest.mark.parametrize('path',['/api/poetry?lean=true','/api/poetry/p','/api/sources'])
def test_unchanged_corpus_reuses_body_only_after_current_authorization(boundary,path):
    client,access,repo=boundary
    first=client.get(path);tag=first.headers.get('etag')
    assert tag and tag.startswith('W/"')
    assert first.headers['cache-control']=='no-store'
    second=client.get(path,headers={'If-None-Match':tag})
    assert second.status_code==304 and second.content==b''
    assert second.headers['etag']==tag
    assert client.get(path,headers={'If-None-Match':'"unrelated", '+tag[2:]}).status_code==304
    assert access.calls==3
    for status in (401,403,503):
        access.status=status
        assert client.get(path,headers={'If-None-Match':tag}).status_code==status
    access.status=200;access.account='reader-b'
    assert client.get(path,headers={'If-None-Match':tag}).status_code==200

@pytest.mark.parametrize('kind,key,value',[('poems','text','Changed verse'),('rights','assessment','Rights held'),('sources','title','Corrected source')])
def test_changed_evidence_invalidates_collection_and_detail(boundary,kind,key,value):
    client,access,repo=boundary
    tags={p:client.get(p).headers.get('etag') for p in ('/api/poetry?lean=true','/api/poetry/p')}
    repo.library[kind][0][key]=value
    for path,tag in tags.items():
        result=client.get(path,headers={'If-None-Match':tag or ''})
        assert result.status_code==200 and result.headers.get('etag')!=tag


def test_lean_is_additive_scoped_and_cors_allows_validator(boundary):
    client,_,_=boundary
    full=client.get('/api/poetry');lean=client.get('/api/poetry?lean=true')
    assert full.json()['citations']['p']
    assert lean.json()['citations']=={}
    assert lean.headers.get('etag')!=full.headers.get('etag')
    assert client.get('/api/poetry?search=absent',headers={'If-None-Match':full.headers.get('etag','')}).status_code==200
    preflight=client.options('/api/poetry',headers={'Origin':'http://localhost:5179','Access-Control-Request-Method':'GET','Access-Control-Request-Headers':'authorization,if-none-match'})
    assert preflight.status_code==200
    assert 'etag' in client.get('/api/poetry',headers={'Origin':'http://localhost:5179'}).headers['access-control-expose-headers'].lower()
    assert 'etag' not in client.get('/api/exports?format=json').headers


def test_schema_and_projection_versions_invalidate_validators(boundary,monkeypatch):
    from apps.pts.backend import reader_cache
    client,_,repo=boundary
    path='/api/poetry?lean=true';tag=client.get(path).headers['etag']
    repo.library['schema_version']='1.3'
    second=client.get(path,headers={'If-None-Match':tag})
    assert second.status_code==200 and second.headers['etag']!=tag
    monkeypatch.setattr(reader_cache,'REPRESENTATION_VERSION','pts-reader-next')
    third=client.get(path,headers={'If-None-Match':second.headers['etag']})
    assert third.status_code==200 and third.headers['etag']!=second.headers['etag']
