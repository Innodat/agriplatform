"""Real-owner acceptance extension for a NEW guarded integration fixture only.

Cross-owner imports below are migration/test adapters; applications use HTTP only.
No retained data or hosted provider is a writable input to this driver.
"""
import base64
import hashlib
import json
import os
import subprocess
from pathlib import Path
import sys
import time
from uuid import uuid4
import httpx
import psycopg
from sqlalchemy import create_engine,text
from apps.pts.backend.db import engine,scoped,corpus
from apps.pts.tools.import_library import import_library
from apps.pts.tools.bind_corpus import inventory,bind
from apps.pts.tests.integration_fixture import ROOT,private,raw,module


def synthetic_pdf():
    # A real, minimal PDF exercises the browser's native viewer without a JS viewer.
    objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    stream=b'BT /F1 16 Tf 30 100 Td (Synthetic PtS source) Tj ET'
    objects.append(b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'\nendstream')
    data=b'%PDF-1.4\n';offsets=[0]
    for index,value in enumerate(objects,1):offsets.append(len(data));data+=str(index).encode()+b' 0 obj\n'+value+b'\nendobj\n'
    xref=len(data);data+=b'xref\n0 6\n0000000000 65535 f \n'+b''.join(f'{offset:010d} 00000 n \n'.encode() for offset in offsets[1:])+b'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n'+str(xref).encode()+b'\n%%EOF\n'
    return data


def adopt(f):
    f.guard();f.partition=str(uuid4());f.content_id=str(uuid4())
    library=json.loads((ROOT/'apps/pts/reference/poetry-library/library.json').read_text())
    f.library=library;f.document=next(d for d in library['source_documents'] if d['id']=='DOC-VELTEN')
    data=synthetic_pdf()
    f.pdf=data;digest=hashlib.sha256(data).hexdigest()
    legacy=engine(f.pts_urls['pts_import']);owner=engine(f.pts_urls['pts_migrator'])
    try:
        with scoped(legacy,f.partition,'legacy:fixture') as connection:
            import_library(connection,library)
            connection.execute(text('INSERT INTO pts.attachments(org_id,id,document_id,content_id) VALUES(:org,:document,:document,:content)'),{'org':f.partition,'document':f.document['id'],'content':f.content_id})
        with scoped(owner,f.partition,f.subjects[0]['actor_id']) as connection:before=inventory(connection)
        binding={'schema_version':1,'executor_actor_id':f.subjects[0]['actor_id'],'legacy_partition_id':f.partition,'inventory_sha256':hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),'release_reference':'fixture:'+f.nonce,**before}
        assert bind(owner,binding)=={'status':'bound'} and bind(owner,binding)=={'status':'unchanged'}
        with scoped(owner,f.partition,f.subjects[0]['actor_id']) as connection:assert inventory(connection)==before
    finally:legacy.dispose();owner.dispose()
    export={'version':1,'sources':[{'source_org_id':f.partition,'source_content_id':f.content_id,'owner':{'application_id':'pts','kind':'application'},'associations':['source_document:'+f.document['id']]}]}
    private(f.out/'independent-application-export.json',export);private(f.out/'reviewed-corpus-binding.json',binding)
    with psycopg.connect(raw(f.content_urls['content_migrator'])) as connection:
        connection.execute("SELECT set_config('app.org_id',%s,true),set_config('app.actor_id','legacy:fixture',true)",(f.partition,))
        connection.execute("INSERT INTO content.objects(org_id,id,sha256,size,media_type,state) VALUES(%s,%s,%s,%s,'application/pdf','ready')",(f.partition,f.content_id,digest,len(data)))
        connection.execute("INSERT INTO content.events(org_id,id,content_id,operation) VALUES(%s,%s,%s,'fixture-original')",(f.partition,uuid4(),f.content_id))
    # Content imports have unqualified owner-local dependencies. Keep them isolated
    # from PtS modules and restore environment after configuring the provider adapter.
    sys.path.insert(0,str(ROOT/'services/content-service'))
    from adoption import AdoptionManifest,AdoptionInventory,adopt as content_adopt
    from provider import Storage
    settings={'CONTENT_BUCKET':'pts-adoption-private','CONTENT_S3_ENDPOINT':f.storage_frame['origin']+'/s3','CONTENT_S3_REGION':'local','CONTENT_S3_ACCESS_KEY':f.storage_frame['env']['S3_PROTOCOL_ACCESS_KEY_ID'],'CONTENT_S3_SECRET_KEY':f.storage_frame['env']['S3_PROTOCOL_ACCESS_KEY_SECRET']}
    previous={name:os.environ.get(name) for name in settings};os.environ.update(settings)
    try:storage=Storage()
    finally:
        for name,value in previous.items():
            if value is None:os.environ.pop(name,None)
            else:os.environ[name]=value
    storage.client.put_object(Bucket=storage.bucket,Key=f.partition+'/sealed/'+f.content_id,Body=data,ContentType='application/pdf')
    manifest={'version':1,'objects':[{**export['sources'][0],'sha256':digest,'size':len(data),'media_type':'application/pdf'}]}
    private(f.out/'content-manifest.json',manifest)
    db=create_engine(f.content_urls['content_migrator'],hide_parameters=True)
    try:
        adopted=content_adopt(db,storage,AdoptionManifest.model_validate(manifest),f.content_executor,AdoptionInventory.model_validate(export))
        assert content_adopt(db,storage,AdoptionManifest.model_validate(manifest),f.content_executor,AdoptionInventory.model_validate(export))==adopted
        with psycopg.connect(raw(f.content_urls['content_migrator'])) as connection:
            assert connection.execute('SELECT created_by,operation FROM content.events WHERE content_id=%s',(f.content_id,)).fetchall()==[('legacy:fixture','fixture-original')]
    finally:db.dispose()
    private(f.out/'adoption-proof.json',{'content_id':f.content_id,'sha256':digest,'size':len(data),'manifest_sha256':adopted,'corpus_preserved':True,'repeat_unchanged':True,'legacy_event_preserved':True})
    f.checks.append('real-Storage-byte-adoption-independent-association-export-and-singleton-corpus-binding')


def owner_paths(f):
    f.refresh_subject_credentials('owner-paths')
    origin=f.services['pts']['origin'];subject=f.subjects[0];auth={'Authorization':'Bearer '+subject['access_token']}
    file_host=httpx.URL(f.file_origin).netloc.decode()
    file_headers={**auth,'Host':file_host,'Origin':f.frontend_origin}
    observations=[]
    with httpx.Client(timeout=30,trust_env=False) as client:
        response=client.get(origin+'/api/poetry',headers=auth);assert response.status_code==200
        body=response.json();assert body['collection_total']==len(f.library['poems']) and body['citations']
        for path in ('/api/sources','/api/poetry/'+f.library['poems'][0]['id'],'/api/exports?format=json','/api/exports?format=text','/api/documents/'+f.document['id']):
            response=client.get(origin+path,headers=auth);assert response.status_code==200,path
            observations.append({'path':path,'status':response.status_code})
        response=client.get(origin+'/api/poetry?org_id='+str(uuid4()),headers={**auth,'X-Org-ID':str(uuid4())})
        alternate=response.json();changed=[key for key in set(body)|set(alternate) if body.get(key)!=alternate.get(key)]
        private(f.out/'obsolete-selector-comparison.json',{'status':response.status_code,'changed_fields':changed,'volatile_field_source':'apps/pts/backend/collection.py:select generates exported_at for each request'})
        assert response.status_code==200 and set(changed)<= {'exported_at'}
        response=client.post(origin+'/api/file-session',headers=file_headers);assert response.status_code==200
        cookie=response.headers['set-cookie'].split(';',1)[0];native={'Host':file_host,'Cookie':cookie}
        response=client.post(origin+'/api/file-contexts/'+f.document['id'],headers=file_headers);assert response.status_code==200
        path=httpx.URL(response.json()['url']).path;f.native_path=path;f.native_cookie=cookie
        response=client.get(origin+path,headers=native);assert response.status_code==200 and response.content==f.pdf
        etag=response.headers['etag'];assert 'inline;' in response.headers['content-disposition'] and response.headers['cache-control']=='private, no-store'
        response=client.head(origin+path,headers=native);assert response.status_code==200 and response.content==b'' and int(response.headers['content-length'])==len(f.pdf)
        for value,start,end in [('bytes=2-8',2,8),('bytes=5-',5,len(f.pdf)-1),('bytes=-7',len(f.pdf)-7,len(f.pdf)-1)]:
            response=client.get(origin+path,headers={**native,'Range':value});assert response.status_code==206 and response.content==f.pdf[start:end+1]
        response=client.get(origin+path,headers={**native,'Range':'bytes=0-7','If-Range':etag});assert response.status_code==206 and response.content==f.pdf[:8]
        response=client.get(origin+path,headers={**native,'Range':'bytes=0-7','If-Range':'"different"'})
        claims=json.loads(base64.urlsafe_b64decode(subject['access_token'].split('.')[1]+'='*(-len(subject['access_token'].split('.')[1])%4)))
        private(f.out/'if-range-mismatch-observation.json',{'status':response.status_code,'received_bytes':len(response.content),'expected_bytes':len(f.pdf),'byte_identity_matches':hashlib.sha256(response.content).digest()==hashlib.sha256(f.pdf).digest(),'credential_expired':claims['exp']<=time.time()})
        assert response.status_code==200 and response.content==f.pdf
        response=client.get(origin+path,headers={**native,'Range':'bytes=999999-'});assert response.status_code==416 and response.headers['content-range']=='bytes */'+str(len(f.pdf))
        response=client.get(origin+path,headers={**native,'Range':'bytes=0-1,3-4'});assert response.status_code==400
        assert client.head(origin+path,headers={'Host':file_host}).status_code==401
        for permission,denied,allowed in [('pts.poetry.read','/api/poetry','/api/exports?format=json'),('pts.poetry.export','/api/exports?format=json','/api/poetry'),('pts.poetry.documents',path,'/api/poetry')]:
            f.grant(subject['account'],permission,False)
            assert client.get(origin+denied,headers=native if denied==path else auth).status_code==403
            assert client.get(origin+allowed,headers=auth).status_code==200
            if denied==path:assert client.head(origin+path,headers={**native,'Range':'bytes=0-7'}).status_code==403
            f.grant(subject['account'],permission,True)
        f.app_enabled(False);assert client.get(origin+'/api/poetry',headers=auth).status_code==403;f.app_enabled(True)
    private(f.out/'owner-path-proof.json',{'operations':observations,'ranges':6,'independent_capabilities':3,'disabled_application_denied':True,'unauthenticated_HEAD_denied':True,'bytes_sha256':hashlib.sha256(f.pdf).hexdigest()})
    f.checks.append('real-zero-membership-reader-export-source-citation-document-and-exact-capability-revocation')
    f.checks.append('real-Content-full-HEAD-single-ranges-If-Range-416-multirange-and-private-headers')


def qualify(f):
    adopt(f);successor_upload(f);owner_paths(f);owner_denials(f)


def successor_upload(f):
    """Actual operator command, pending PUT/finalize, ready replay and association.

    No upload mock or legacy Content adoption supplies this new object's identity.
    """
    f.guard()
    root=f.out/'successor-upload';(root/'sources').mkdir(parents=True)
    payload=synthetic_pdf()+b'\n% successor uploader '+f.nonce.encode()+b'\n'
    (root/'sources/successor.pdf').write_bytes(payload)
    document={**f.document,'id':'DOC-SUCCESSOR-UPLOAD','title':'Synthetic successor uploader document','local_path':'sources/successor.pdf','sha256':hashlib.sha256(payload).hexdigest()}
    library={**f.library,'source_documents':[*f.library['source_documents'],document]}
    importer=engine(f.pts_urls['pts_corpus_import'])
    try:
        with corpus(importer,f.subjects[0]['actor_id']) as conn:import_library(conn,library)
    finally:importer.dispose()
    path=root/'library.json';private(path,{'source_documents':[document]})
    command=[sys.executable,'-B','-m','apps.pts.tools.upload_sources','--library',str(path)]
    environment={**os.environ,'PTS_IMPORT_DATABASE_URL':f.pts_urls['pts_corpus_import'],'PTS_IMPORT_ACTOR_ID':f.subjects[0]['actor_id'],
        'CONTENT_URL':f.services['content']['origin'],'PTS_IMPORT_SERVICE_KEY':f.content_key}
    observed=[]
    for phase in ('pending-finalization','ready-replay'):
        result=subprocess.run(command,cwd=ROOT,env=environment,capture_output=True,timeout=60)
        (root/(phase+'.stdout')).write_bytes(result.stdout);(root/(phase+'.stderr')).write_bytes(result.stderr)
        assert result.returncode==0,'actual_successor_uploader_command_failed_'+phase
        assert json.loads(result.stdout)=={'document_id':document['id'],'status':'attached'}
        from apps.pts.backend.main import Repository
        reader=engine(f.pts_urls['pts_account_runtime'])
        try:
            identity=str(Repository(reader).attachment(f.subjects[0]['actor_id'],document['id']))
            with corpus(reader,f.subjects[0]['actor_id']) as conn:
                assert conn.execute(text('SELECT count(*) FROM pts.attachments WHERE document_id=:document'),{'document':document['id']}).scalar_one()==1
        finally:reader.dispose()
        with httpx.Client(timeout=15,trust_env=False,headers={'X-Service-Key':f.content_key}) as client:
            metadata=client.get(f.services['content']['origin']+'/v2/objects/'+identity,params={'application_id':'pts','kind':'application'})
            assert metadata.status_code==200
            value=metadata.json();assert value['id']==identity and value['state']=='ready' and value['sha256']==document['sha256'] and value['size']==len(payload)
            response=client.get(f.services['content']['origin']+'/v2/objects/'+identity+'/bytes',params={'application_id':'pts','kind':'application'})
            assert response.status_code==200 and response.content==payload
        observed.append({'phase':phase,'content_id':identity,'sha256':value['sha256'],'size':value['size'],'state':value['state'],'association_count':1})
    assert observed[0]['content_id']==observed[1]['content_id'],'ready_replay_changed_content_identity'
    f.library=library
    private(root/'successor-upload-proof.json',{'argv':command,'observations':observed,'actual_pending_PUT_and_finalization':True,'actual_ready_replay':True})
    f.checks.append('actual-successor-upload-command-pending-PUT-finalization-ready-replay-byte-identity-and-persisted-association')


def owner_denials(f):
    """Real owner/service and current-session failures before private metadata."""
    f.guard();origin=f.services['pts']['origin'];content=f.services['content']['origin']
    subject=f.subjects[0];auth={'Authorization':'Bearer '+subject['access_token']}
    native={'Host':httpx.URL(f.file_origin).netloc.decode(),'Cookie':f.native_cookie}
    setup={**auth,'Host':native['Host'],'Origin':f.frontend_origin}
    headers={'X-Service-Key':f.content_key,'X-Initiator-Account-Id':subject['account'],
        'X-Initiator-Actor-Id':subject['actor_id'],'X-Operation-Id':str(uuid4())}
    owner={'application_id':'pts','kind':'application'};observations=[]
    with httpx.Client(timeout=10,trust_env=False) as client:
        # This account/actor has never had any PtS grant, and has no membership.
        absent=next(item for item in f.subjects if item['absent_grants'])
        for path in ('/api/poetry','/api/exports?format=json','/api/documents/'+f.document['id']):
            response=client.get(origin+path,headers={'Authorization':'Bearer '+absent['access_token']})
            assert response.status_code==403
        response=client.post(origin+'/api/file-session',headers={**setup,'Authorization':'Bearer '+absent['access_token']})
        assert response.status_code==403 and 'set-cookie' not in response.headers
        observations.append({'case':'never-granted-account','operations':4,'status':403})
        for method in ('GET','HEAD'):
            for selected,params in (({**headers,'X-Service-Key':'unregistered-fixture-service'},owner),
                                    (headers,{'application_id':'leave','kind':'application'})):
                response=client.request(method,content+'/v2/objects/'+f.content_id+'/bytes',headers=selected,params=params)
                assert response.status_code==403 and response.headers['x-content-error-id']=='content.denied'
                assert 'content-range' not in response.headers and 'content-disposition' not in response.headers
        observations.append({'case':'wrong-service-and-application','operations':4,'status':403})
        # A new finalized object exists in Content but has no PtS source association.
        data=f.pdf+b'\n% unrelated fixture '+uuid4().hex.encode()
        created=client.post(content+'/v2/objects',headers=headers,json={'owner':owner,'sha256':hashlib.sha256(data).hexdigest(),'size':len(data),'media_type':'application/pdf'})
        assert created.status_code==200;unrelated=created.json()
        target=httpx.URL(unrelated['url']);assert target.scheme=='http' and target.netloc==httpx.URL(f.storage_frame['origin']).netloc
        assert client.put(unrelated['url'],content=data,headers={'Content-Type':'application/pdf'}).status_code==200
        assert client.post(content+'/v2/objects/'+unrelated['id']+'/finalize',headers=headers,json={'owner':owner}).status_code==200
        assert client.head(content+'/v2/objects/'+unrelated['id']+'/bytes',headers=headers,params=owner).status_code==200
        replay=client.post(content+'/v2/objects',headers=headers,json={'owner':owner,'sha256':hashlib.sha256(data).hexdigest(),'size':len(data),'media_type':'application/pdf'})
        assert replay.status_code==200 and replay.json()['id']==unrelated['id'] and replay.json()['state']=='ready'
        assert client.post(content+'/v2/objects/'+unrelated['id']+'/finalize',headers=headers,json={'owner':owner}).status_code==200
        reread=client.get(content+'/v2/objects/'+unrelated['id']+'/bytes',headers=headers,params=owner)
        assert reread.status_code==200 and reread.content==data
        for path in ('/api/documents/'+unrelated['id'],'/api/files/'+unrelated['id']):
            assert client.get(origin+path,headers={**native,**auth}).status_code==404
        response=client.post(origin+'/api/file-contexts/'+unrelated['id'],headers=setup)
        assert response.status_code==404
        observations.append({'case':'finalized-unassociated-content-cannot-select-PtS-resource','operations':3,'status':404})
        pending_data=uuid4().bytes
        response=client.post(content+'/v2/objects',headers=headers,json={'owner':owner,'sha256':hashlib.sha256(pending_data).hexdigest(),'size':len(pending_data),'media_type':'application/pdf'})
        assert response.status_code==200;pending=response.json();assert pending['state']=='pending'
        db=engine(f.pts_urls['pts_corpus_import'])
        try:
            with corpus(db,subject['actor_id']) as connection:
                connection.execute(text('INSERT INTO pts.attachments(org_id,id,document_id,content_id) VALUES(:partition,:document,:document,:content)'),
                    {'partition':f.partition,'document':'DOC-SHUWARI','content':pending['id']})
        finally:db.dispose()
        response=client.post(origin+'/api/file-contexts/DOC-SHUWARI',headers=setup)
        assert response.status_code==200;pending_path=httpx.URL(response.json()['url']).path
        for method in ('GET','HEAD'):
            direct=client.request(method,content+'/v2/objects/'+pending['id']+'/bytes',headers=headers,params=owner)
            assert direct.status_code==409 and direct.headers['x-content-error-id']=='content.not_ready'
            response=client.request(method,origin+pending_path,headers=native)
            assert response.status_code==409 and response.headers['x-pts-error-code']=='content.not_ready'
            assert 'content-range' not in response.headers and 'content-disposition' not in response.headers
            if method=='GET':assert response.json()=={'detail':{'code':'content.not_ready'}}
        observations.append({'case':'associated-not-ready-content','operations':4,'status':409})
        external=next(item for item in f.library['source_documents'] if not item.get('local_path') and str(item.get('url','')).startswith(('https://','http://')))
        response=client.get(origin+'/api/documents/'+external['id'],headers=auth)
        assert response.status_code==200 and response.json()['status']=='link_only' and response.json()['url']==external['url']
        assert client.post(origin+'/api/file-contexts/'+external['id'],headers=setup).status_code==404
        observations.append({'case':'external-reference-remains-explicit-link','status':200})
    private(f.out/'owner-denial-proof.json',{'observations':observations,'private_metadata_escaped':False})
    f.checks.append('real-absent-grants-wrong-service-unrelated-and-not-ready-owner-denials')


def provider_outage(f):
    """Pause the fresh genuine provider through the actual generated TLS route."""
    from apps.pts.tests.resource_acceptance import request,metadata
    f.guard();f.refresh_subject_credentials('tls-provider-outage')
    target=metadata(f,0,f.document['id']);url=target['url'];native=target['headers']
    f.native_path=httpx.URL(url).path;f.native_cookie=native['Cookie']
    claims=json.loads(base64.urlsafe_b64decode(f.subjects[0]['access_token'].split('.')[1]+'='*(-len(f.subjects[0]['access_token'].split('.')[1])%4)))
    def observe(phase,response):
        private(f.out/('provider-outage-'+phase+'-observation.json'),{'status':response.status,'error_id':response.getheader('X-PtS-Error-Code'),'credential_expired':claims['exp']<=time.time(),'body_length_header_matches':response.getheader('Content-Length')==str(len(f.pdf))})
    with request(f,'HEAD',url,native) as response:
        observe('before',response)
        assert response.status==200 and int(response.getheader('Content-Length'))==len(f.pdf)
        assert response.read()==b''
    f.docker('pause',f.frame['container']);started=time.monotonic()
    try:
        with request(f,'HEAD',url,native) as response:
            observe('paused',response)
            elapsed=time.monotonic()-started
            assert response.status==503 and response.getheader('X-PtS-Error-Code')=='identity.current_session_unavailable'
            assert response.read()==b'' and elapsed<3
            assert response.getheader('Content-Range') is None and response.getheader('Content-Disposition') is None
            assert response.getheader('Cache-Control')=='private, no-store'
    finally:f.docker('unpause',f.frame['container'])
    f.wait(f.frame['origin'])
    with request(f,'HEAD',url,native) as response:
        observe('recovery',response)
        assert response.status==200 and int(response.getheader('Content-Length'))==len(f.pdf)
        assert response.read()==b''
    private(f.out/'provider-outage-proof.json',{'genuine_provider_paused':True,'native_TLS_HEAD_status':503,
        'code':'identity.current_session_unavailable','seconds':round(elapsed,3),'recovery_HEAD_status':200,
        'private_metadata_escaped':False})
    f.checks.append('real-TLS-current-session-provider-pause-native-HEAD-typed-deadline-and-recovery')
