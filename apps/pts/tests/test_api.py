from fastapi.testclient import TestClient
from apps.pts.backend.main import create_app

class Access:
    status = 200
    def verify(self, token, org, permission):
        from fastapi import HTTPException
        if not token: raise HTTPException(401, {'code':'authentication_required'})
        if self.status != 200: raise HTTPException(self.status, {'code':'access_denied' if self.status==403 else 'access_unavailable'})
        return {'actor_id':'00000000-0000-0000-0000-000000000001', 'org_id':str(org)}

class Repo:
    def read(self, org, actor):
        import json
        from pathlib import Path
        return json.loads((Path(__file__).parents[1]/'reference/poetry-library/library.json').read_text())
    def attachment(self, org, actor, document): return None


def test_all_protected_routes_check_current_authority():
    access = Access()
    client = TestClient(create_app(access=access, repository=Repo()))
    routes=['/api/poetry','/api/poetry/SWA-001','/api/exports?format=json','/api/documents/DOC-VELTEN']
    for route in routes:
        assert client.get(route,headers={'X-Org-ID':'00000000-0000-0000-0000-000000000002'}).status_code == 401
        for denied in (403,503):
            access.status=denied
            assert client.get(route,headers={'Authorization':'Bearer old-admin-token','X-Org-ID':'00000000-0000-0000-0000-000000000002'}).status_code == denied
    access.status=200
    headers={'Authorization':'Bearer authorized','X-Org-ID':'00000000-0000-0000-0000-000000000002'}
    assert client.get('/api/poetry?availability=checked',headers=headers).json()['total']==33
    assert client.get('/api/poetry/SWA-001',headers=headers).json()['poem']['text']
    assert client.get('/api/poetry/missing',headers=headers).status_code==404
    assert client.get('/api/documents/DOC-VELTEN',headers=headers).status_code==404
    assert client.get('/api/documents/DOC-MANTIS',headers=headers).status_code in (200,404)


def test_exports_and_link_only_document_contracts():
    import json
    access=Access();client=TestClient(create_app(access=access,repository=Repo()))
    headers={'Authorization':'Bearer authorized','X-Org-ID':'00000000-0000-0000-0000-000000000002'}
    library=Repo().read(None,None)
    doc=next(d for d in library['source_documents'] if not d.get('local_path') and d.get('url'))
    response=client.get('/api/documents/'+doc['id'],headers=headers)
    assert response.status_code==200
    assert response.json()['status']=='link_only' and response.json()['document']==doc
    result=client.get('/api/exports?format=json&availability=checked',headers=headers)
    assert len(result.json()['poems'])==33
    assert result.headers['cache-control']=='no-store'
    text_result=client.get('/api/exports?format=text&availability=all&search=Mwanadani',headers=headers)
    assert text_result.status_code==200
    assert 'Alternate witness' in text_result.text
    assert 'Licence / terms' in text_result.text


def test_http_access_outage_fails_closed(monkeypatch):
    import httpx
    from apps.pts.backend.clients import AccessClient
    def unavailable(*args,**kwargs):raise httpx.ConnectError('test outage')
    monkeypatch.setattr(httpx,'post',unavailable)
    client=TestClient(create_app(access=AccessClient('http://access.invalid','test'),repository=Repo()))
    result=client.get('/api/poetry',headers={'Authorization':'Bearer admin','X-Org-ID':'00000000-0000-0000-0000-000000000002'})
    assert result.status_code==503
    assert result.json()['detail']['code']=='access_unavailable'
