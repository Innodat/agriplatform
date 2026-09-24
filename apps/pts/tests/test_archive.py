import json
from pathlib import Path
from apps.pts.tools.verify_archive import verify

def test_archived_bytes_and_frontend_public_boundary():
    root=Path(__file__).parents[1]
    report=verify(root/'reference/poetry-library',json.loads((root/'reference/copy-manifest.json').read_text()))
    assert report['files']==264
    assert report['bytes']==222505940
    assert not (root/'web/public').exists()
    for path in (root/'web/dist').rglob('*'):
        if path.is_file():assert b'SWA-001' not in path.read_bytes()


def test_source_transfer_errors_never_expose_signed_urls(tmp_path,monkeypatch):
    import httpx,pytest,traceback
    from apps.pts.tools.upload_sources import upload
    (tmp_path/'sources').mkdir();(tmp_path/'sources/test.pdf').write_bytes(b'fixture')
    signed='https://storage.invalid/object?signature=private-test-secret'
    class Client:
        def post(self,*args,**kwargs):
            return httpx.Response(200,json={'state':'pending','content_id':'fixture','url':signed},request=httpx.Request('POST','https://content.invalid/v1/objects'))
    monkeypatch.setattr(httpx,'put',lambda *args,**kwargs:httpx.Response(403,request=httpx.Request('PUT',signed)))
    with pytest.raises(RuntimeError) as error:upload({'local_path':'sources/test.pdf'},tmp_path,Client())
    assert 'private-test-secret' not in ''.join(traceback.format_exception(error.value))
