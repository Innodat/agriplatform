"""Upload declared local documents through content HTTP; attach only finalized identities."""
import argparse
import hashlib
import json
import mimetypes
import os
from pathlib import Path
from uuid import UUID
import httpx
from sqlalchemy import text
from apps.pts.backend.db import engine,scoped


def upload(document,root,client):
    base=root.resolve();path=(base/document['local_path']).resolve()
    if not path.is_relative_to((base/'sources').resolve()):raise ValueError('unsafe source path')
    with path.open('rb') as source:
        sha=hashlib.file_digest(source,'sha256').hexdigest()
    if document.get('sha256') and sha!=document['sha256']:raise ValueError('source checksum mismatch')
    media=mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    r=client.post('/v1/objects',json={'sha256':sha,'size':path.stat().st_size,'media_type':media});r.raise_for_status();session=r.json()
    if session['state']!='ready':
        with path.open('rb') as data:
            # Separate client: never send internal service credentials to storage.
            try:
                r=httpx.put(session['url'],content=data,headers={'Content-Type':media},timeout=300);r.raise_for_status()
            except httpx.HTTPError:
                raise RuntimeError('Source transfer failed; retry the upload without logging signed credentials') from None
        r=client.post('/v1/objects/'+session['content_id']+'/finalize');r.raise_for_status()
    return session['content_id']


def require_canonical(conn, document):
    stored=conn.execute(text('SELECT payload FROM pts.source_documents WHERE id=:id'),{'id':document['id']}).scalar_one_or_none()
    if stored != document:
        raise ValueError('document differs from retained catalogue; resolve import conflict before uploading')


def attach_document(db, org, document, root, client):
    # Verify before external I/O, then recheck with association. No external wait under locks.
    with scoped(db,org,'service:pts-import') as conn:
        require_canonical(conn,document)
    content_id=upload(document,root,client)
    with scoped(db,org,'service:pts-import') as conn:
        require_canonical(conn,document)
        conn.execute(text("INSERT INTO pts.attachments(org_id,id,document_id,content_id) VALUES(:org,:id,:id,:content) ON CONFLICT DO NOTHING"),{'org':org,'id':document['id'],'content':UUID(content_id)})
        existing=conn.execute(text('SELECT content_id FROM pts.attachments WHERE document_id=:id'),{'id':document['id']}).scalar_one()
        if str(existing)!=content_id:
            raise ValueError('attachment conflict; deliberate review required')
    return content_id


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--library',type=Path,required=True);parser.add_argument('--org',type=UUID,required=True);args=parser.parse_args()
    library=json.loads(args.library.read_text());db=engine(os.environ['PTS_IMPORT_DATABASE_URL'])
    with httpx.Client(base_url=os.environ['CONTENT_URL'],headers={'X-Service-Key':os.environ['PTS_IMPORT_SERVICE_KEY'],'X-Org-ID':str(args.org)},timeout=300) as client:
        for doc in library['source_documents']:
            if not doc.get('local_path'):continue
            attach_document(db,args.org,doc,args.library.parent,client)
            print(json.dumps({'document_id':doc['id'],'status':'attached'}))

if __name__=='__main__':main()
