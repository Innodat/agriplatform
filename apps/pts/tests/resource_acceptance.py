"""Real private TLS stream/resource acceptance in a NEW guarded fixture only.

No full-file buffers, response doubles, process-global DNS changes or retained fixture
mutation. TLS connects to loopback while verifying the generated hostname/certificate.
"""
from contextlib import contextmanager
import hashlib
import http.client
import json
from pathlib import Path
import socket
import signal
import ssl
import threading
import time
from urllib.parse import urlsplit
from uuid import uuid4

import httpx
import psycopg
from sqlalchemy import text
from apps.pts.backend.db import engine,corpus
from apps.pts.tests.integration_fixture import private,raw

MIB=1024*1024
SIZE=128*MIB


def event(f,**values):
    # Only this NEW attempt owns the append-only journal. Values are selected
    # statuses/counts, never credentials, request payloads or provider locators.
    path=f.out/'resource-events.jsonl'
    with path.open('a') as output:output.write(json.dumps({'at':time.monotonic(),**values})+'\n')


class FixtureTLS(http.client.HTTPSConnection):
    def connect(self):
        sock=socket.create_connection(('127.0.0.1',self.port),self.timeout)
        self.sock=self._context.wrap_socket(sock,server_hostname=self.host)


@contextmanager
def request(f,method,url,headers=None):
    parsed=urlsplit(url)
    assert parsed.scheme=='https' and parsed.netloc==urlsplit(f.file_origin).netloc
    context=ssl.create_default_context(cafile=str(f.out/'gateway/cert.pem'))
    connection=FixtureTLS(parsed.hostname,parsed.port,context=context,timeout=40)
    try:
        connection.request(method,parsed.path+('?' + parsed.query if parsed.query else ''),headers=headers or {})
        response=connection.getresponse()
        try:yield response
        finally:response.close()
    finally:connection.close()


def metadata(f,index,document):
    subject=f.subjects[index]
    headers={'Authorization':'Bearer '+subject['access_token'],'Origin':f.frontend_origin}
    with request(f,'POST',f.file_origin+'/api/file-session',headers) as response:
        assert response.status==200
        cookie=response.getheader('Set-Cookie').split(';',1)[0];response.read()
    with request(f,'POST',f.file_origin+'/api/file-contexts/'+document+'?presentation=download',headers) as response:
        assert response.status==200
        url=json.loads(response.read())['url']
    return {'url':url,'headers':{'Cookie':cookie},'account':subject['account']}


def rss(pid):
    for line in Path('/proc/'+str(pid)+'/status').read_text().splitlines():
        if line.startswith('VmRSS:'):return int(line.split()[1])*1024
    raise AssertionError('process_RSS_unavailable')


def descendants(pid):
    result={pid};pending=[pid]
    while pending:
        parent=pending.pop()
        for path in Path('/proc').glob('[0-9]*/stat'):
            try:
                # comm may contain spaces, so split after its final parenthesis.
                parent_id=int(path.read_text().rsplit(')',1)[1].split()[1])
                if parent_id==parent and int(path.parent.name) not in result:
                    child=int(path.parent.name);result.add(child);pending.append(child)
            except (OSError,ValueError):pass
    return sorted(result)


def process_role(pid):
    # Classify only known process titles; never retain arbitrary command lines.
    try:title=Path('/proc/'+str(pid)+'/cmdline').read_bytes()
    except OSError:return 'unavailable'
    for needle,role in ((b'cache loader','cache_loader'),(b'cache manager','cache_manager'),
        (b'worker process','worker'),(b'master process','master'),(b'privileged agent','privileged_agent')):
        if needle in title:return role
    return 'other'


class Monitor:
    def __init__(self,f):
        self.f=f
        gateway=json.loads(f.docker('inspect',f.gateway_container))[0]
        storage=json.loads(f.docker('inspect',f.storage_frame['container']))[0]
        self.principals={'pts':f.services['pts']['pid'],'content':f.services['content']['pid'],
            'gateway':gateway['State']['Pid'],'storage':storage['State']['Pid']}
        self.processes={name:descendants(pid) for name,pid in self.principals.items()}
        self.roles={pid:process_role(pid) for pids in self.processes.values() for pid in pids}
        self.previous={name:set(pids) for name,pids in self.processes.items()};self.lifecycle=[]
        self.ports={name:service['port'] for name,service in f.services.items() if name in ('pts','content','access')}
        self.ports['gateway']=urlsplit(f.file_origin).port
        self.samples=[];self.stopped=threading.Event();self.lock=threading.Lock();self.failure=None

    def sample(self):
        memory={};observed={}
        for name,principal in self.principals.items():
            # A daemon's short-lived cache loader can retire normally while the
            # principal and workers keep streaming. Sample its CURRENT owned tree
            # instead of treating a stale helper PID as the whole API instance.
            rss(principal) # principal loss is always a failed observation
            selected=set(descendants(principal));observed[name]=sorted(selected)
            for pid in selected:
                if pid not in self.roles:self.roles[pid]=process_role(pid)
            for pid in self.previous[name]-selected:
                self.lifecycle.append({'service':name,'pid':pid,'role':self.roles[pid],'event':'retired','seconds':round(time.monotonic()-self.started,3)})
            total=0
            for pid in selected:
                try:total+=rss(pid)
                except (FileNotFoundError,ProcessLookupError):
                    if pid==principal:raise
                    self.lifecycle.append({'service':name,'pid':pid,'role':self.roles[pid],'event':'retired_during_sample','seconds':round(time.monotonic()-self.started,3)})
            self.previous[name]=selected;memory[name]=total
        connections={name:0 for name in self.ports}
        for path in ('/proc/net/tcp','/proc/net/tcp6'):
            for line in Path(path).read_text().splitlines()[1:]:
                fields=line.split()
                if fields[3]!='01':continue
                port=int(fields[1].rsplit(':',1)[1],16)
                for name,value in self.ports.items():
                    if value==port:connections[name]+=1
        observation={'seconds':round(time.monotonic()-self.started,3),'rss':memory,'observed_processes':observed,'established_server_connections':connections}
        with self.lock:self.samples.append(observation)
        return observation

    def _run(self):
        try:
            while not self.stopped.wait(.5):self.sample()
        except BaseException as error:
            self.failure={'type':type(error).__name__,'errno':getattr(error,'errno',None),
                'category':str(error) if isinstance(error,AssertionError) else 'proc_observation_failed'}

    def __enter__(self):
        self.started=time.monotonic();self.before=self.sample();self.thread=threading.Thread(target=self._run,daemon=True);self.thread.start();return self

    def __exit__(self,*args):
        self.stopped.set();self.thread.join(5)
        # Persist partial measurements and the original operation outcome even
        # when the measurement worker fails. Never mask the first acceptance
        # failure with a teardown assertion.
        private(self.f.out/'resource-samples.json',{'processes':self.processes,'principals':self.principals,'roles':self.roles,'lifecycle':self.lifecycle,'samples':self.samples,
            'monitor_failure':self.failure,'monitor_thread_alive':self.thread.is_alive(),
            'operation_exception':args[0].__name__ if args and args[0] else None})
        if not args or args[0] is None:
            assert not self.thread.is_alive() and self.failure is None,'resource_monitor_failed'

    def summary(self):
        with self.lock:samples=list(self.samples)
        return {name:{'baseline':self.before['rss'][name],'peak':max(v['rss'][name] for v in samples),
            'growth':max(v['rss'][name] for v in samples)-self.before['rss'][name]} for name in self.processes}


def large_source(f):
    """Use actual Content control-plane/finalization and a new actual PtS association."""
    chunk=('%PDF-1.7\n'+uuid4().hex+'\n').encode();chunk+=b'x'*(MIB-len(chunk))
    digest=hashlib.sha256()
    for _ in range(128):digest.update(chunk)
    expected=digest.hexdigest();origin=f.services['content']['origin']
    subject=f.subjects[0]
    headers={'X-Service-Key':f.content_key,'X-Initiator-Account-Id':subject['account'],
        'X-Initiator-Actor-Id':subject['actor_id'],'X-Operation-Id':str(uuid4())}
    owner={'application_id':'pts','kind':'application'}
    with httpx.Client(timeout=120,trust_env=False) as client:
        created=client.post(origin+'/v2/objects',headers=headers,json={'owner':owner,'sha256':expected,'size':SIZE,'media_type':'application/pdf'})
        assert created.status_code==200
        item=created.json();target=urlsplit(item['url']);storage=urlsplit(f.storage_frame['origin'])
        assert target.scheme==storage.scheme and target.netloc==storage.netloc and not target.username and not target.fragment,'upload_target_not_fresh_storage'
        uploaded=client.put(item['url'],content=(chunk for _ in range(128)),headers={'Content-Type':'application/pdf','Content-Length':str(SIZE)})
        assert uploaded.status_code==200
        finalized=client.post(origin+'/v2/objects/'+item['id']+'/finalize',headers=headers,json={'owner':owner})
        assert finalized.status_code==200
    db=engine(f.pts_urls['pts_corpus_import'])
    try:
        with corpus(db,subject['actor_id']) as connection:
            connection.execute(text('INSERT INTO pts.attachments(org_id,id,document_id,content_id) VALUES(:partition,:document,:document,:content)'),
                {'partition':f.partition,'document':'DOC-MURITHI','content':item['id']})
    finally:db.dispose()
    private(f.out/'large-object-proof.json',{'content_id':item['id'],'size':SIZE,'sha256':expected,'document':'DOC-MURITHI','streamed_create_upload_finalize':True})
    return expected


def read_small(f,item,method='HEAD',extra=None):
    with request(f,method,item['url'],{**item['headers'],**(extra or {})}) as response:
        return response.status,{name.lower():value for name,value in response.getheaders()},response.read()


def prove_capacity(f,items):
    results=[]
    def batch(indices,label):
        deadline=time.monotonic()+60
        while True:
            held=[];admitted=True
            try:
                for index in indices:
                    item=items[index];context=request(f,'GET',item['url'],item['headers']);response=context.__enter__();held.append(context)
                    event(f,phase=label,admitted_index=len(held),subject_index=index,status=response.status)
                    if response.status!=200:
                        assert response.status==429,'unexpected_stream_admission_failure'
                        admitted=False;break
                if admitted:
                    # This same-account probe runs while 14 global slots remain
                    # in the pair case; the ninth account isolates the global limit.
                    status,headers,body=read_small(f,items[indices[0]],'GET')
                    assert status==429 and headers.get('retry-after')=='1'
                    assert json.loads(body)['detail']['code']=='file_capacity_exceeded'
                    if len(indices)==16:
                        status,headers,body=read_small(f,items[8],'GET')
                        assert status==429 and headers.get('retry-after')=='1'
                    time.sleep(1)
                    transaction=no_open_business_transaction(f,label)
                    results.append({'phase':label,'held':len(held),'account_limit_denied':True,'global_limit_denied':len(indices)==16,**transaction})
                    event(f,phase=label,held=len(held),denials_verified=True)
                    return
            finally:
                for context in reversed(held):context.__exit__(None,None,None)
            assert time.monotonic()<deadline,'full_capacity_did_not_recover_after_disconnect'
            time.sleep(.1)
    batch([0,0],'account_initial');batch([0,0],'account_reacquired')
    indices=[index for index in range(8) for _ in range(2)]
    batch(indices,'global_initial');batch(indices,'same_accounts_full_global_reacquired')
    return results


def probe(f):
    """Cheap native admission/measurement diagnosis, excluding timed transfer proof."""
    f.guard();expected=large_source(f);items=[metadata(f,index,'DOC-MURITHI') for index in range(9)]
    with Monitor(f) as monitor:
        capacity=prove_capacity(f,items)
        for name in ('pts','content','gateway'):
            assert max(sample['established_server_connections'][name] for sample in monitor.samples)>=16,'sixteen_held_connections_not_observed'
        cleanup=no_open_business_transaction(f,'after_probe_final_disconnect',settle_cleanup=True)
    graceful=graceful_recovery(f,items[0],expected)
    private(f.out/'resource-probe-proof.json',{'capacity':capacity,'RSS':monitor.summary(),'final_disconnect_cleanup':cleanup,
        'graceful_shutdown':graceful,'timed_transfer_claim':False})
    f.checks.append('native-resource-admission-measurement-and-graceful-recovery-probe-only')


def no_open_business_transaction(f,phase,settle_cleanup=False):
    from psycopg.rows import dict_row
    statement="""SELECT pid,usename,state,
        extract(epoch FROM clock_timestamp()-xact_start)*1000 AS transaction_age_ms,
        extract(epoch FROM clock_timestamp()-state_change)*1000 AS state_age_ms,
        wait_event_type,wait_event,
        CASE WHEN query ILIKE 'INSERT INTO content.owned_events%' THEN 'content_read_audit_insert'
             WHEN query ILIKE '%set_config%' THEN 'owner_scope_setup'
             WHEN query ILIKE 'COMMIT%' THEN 'transaction_commit'
             WHEN query ILIKE 'ROLLBACK%' THEN 'transaction_rollback'
             WHEN query ILIKE 'SELECT%' THEN 'owner_select' ELSE 'owner_statement' END AS operation_category
        FROM pg_stat_activity WHERE datname=current_database()
        AND usename IN ('pts_account_runtime','content_runtime') AND state LIKE 'idle in transaction%'"""
    with psycopg.connect(raw(f.frame['urls']['admin']),autocommit=True,row_factory=dict_row) as connection:
        rows=connection.execute(statement).fetchall()
        if rows or settle_cleanup:
            # Keep in-flight checks immediate. Only final disconnect allows the
            # existing bounded cleanup audit to finish; retain the whole interval
            # and require zero at its deadline rather than claiming zero throughout.
            started=time.monotonic();samples=[{'seconds':0,'rows':rows}]
            for _ in range(20):
                time.sleep(.1)
                samples.append({'seconds':round(time.monotonic()-started,3),'rows':connection.execute(statement).fetchall()})
            private(f.out/('transaction-observation-'+phase+'.json'),{'phase':phase,'initial_idle':bool(rows),
                'final_disconnect_cleanup':settle_cleanup,'samples':samples})
        if settle_cleanup:
            assert samples[-1]['rows']==[],'stream_left_business_transaction_open_after_cleanup_deadline'
            return {'phase':phase,'idle_business_transactions_at_deadline':0,'initial_idle_transactions':len(rows),
                'observed_idle_samples':sum(bool(sample['rows']) for sample in samples),'cleanup_deadline_seconds':samples[-1]['seconds']}
        assert rows==[],'stream_left_business_transaction_open'
    return {'phase':phase,'idle_business_transactions':0}


def graceful_exit(code,*,container=False,oom=False):
    # Qualified Uvicorn0.54 restores and replays TERM after graceful shutdown.
    # Popen reports -signal; Docker reports128+signal. Never accept KILL/OOM or
    # an unrelated nonzero exit merely because some bytes reached the client.
    return not oom and code in (0,128+signal.SIGTERM if container else -signal.SIGTERM)


def graceful_recovery(f,item,expected):
    """Drain an active byte response across SIGTERM, then start a NEW instance.

    Original process/container and its status remain in attempt custody. No prior
    attempt or stopped container is restarted. The supervisor owns the outcome.
    """
    old=f.services['pts'];total=0;digest=hashlib.sha256()
    with request(f,'GET',item['url'],item['headers']) as response:
        assert response.status==200
        block=response.read(MIB);total+=len(block);digest.update(block)
        assert len(block)==MIB
        etag=response.getheader('ETag');prefix=block[:32]
        started=time.monotonic()
        if old.get('container_id'):
            container=old['container_name']
            # Docker stop sends TERM and records any escalation. It waits while
            # the client drains, so invoke it concurrently with byte consumption.
            stopped=[]
            thread=threading.Thread(target=lambda:stopped.append(f.docker('stop','--time','25',container)))
            thread.start()
        else:
            process=next(process for process,_ in f.processes if process.pid==old['pid'])
            process.terminate()
        while block:=response.read(MIB):total+=len(block);digest.update(block)
    private(f.out/'graceful-transfer-observation.json',{'SIGTERM_after_bytes_started':True,'drained_bytes':total,
        'sha256':digest.hexdigest(),'expected_sha256':expected,'seconds':round(time.monotonic()-started,3)})
    assert total==SIZE and digest.hexdigest()==expected,'graceful_drain_corrupted_bytes'
    if old.get('container_id'):
        thread.join(30);assert not thread.is_alive() and len(stopped)==1,'bounded_image_shutdown_failed'
        state=json.loads(f.docker('inspect',container))[0]['State'];code=state['ExitCode']
        oom=state['OOMKilled'];unforced=graceful_exit(code,container=True,oom=oom)
        private(f.out/'graceful-shutdown-observation.json',{'exit_code':code,'OOMKilled':oom,'unforced_TERM_or_zero':unforced,
            'runtime_mode':'frozen_image','seconds':round(time.monotonic()-started,3)})
        assert unforced,'bounded_image_shutdown_failed'
        from apps.pts.tests.image_acceptance import start_pts
        replacement=start_pts(f,f.pts_environment,port=old['port'],generation='recovery')
    else:
        code=process.wait(timeout=25);unforced=graceful_exit(code)
        private(f.out/'graceful-shutdown-observation.json',{'exit_code':code,'unforced_TERM_or_zero':unforced,
            'runtime_mode':'source_process','seconds':round(time.monotonic()-started,3)})
        assert unforced,'bounded_source_shutdown_failed'
        replacement=f.start_owner('.',f.pts_environment,'pts-recovery','apps.pts.backend.main:app',port=old['port'])
    elapsed=time.monotonic()-started;assert elapsed<30
    f.services['pts']=replacement
    private(f.out/'recovery-service-binding-private.json',{'previous':old,'new_instance':replacement})
    status,headers,body=read_small(f,item,'GET',{'Range':'bytes=0-31'})
    assert status==206 and body==prefix and headers.get('etag')==etag
    return {'SIGTERM_after_bytes_started':True,'drained_bytes':total,'sha256':expected,'exit_code':code,'seconds':round(elapsed,3),
        'forced':False,'new_instance_same_context_authorized_range':True,'retained_process_or_container_restarted':False}


def qualify(f):
    f.guard();expected=large_source(f)
    items=[metadata(f,index,'DOC-MURITHI') for index in range(9)]
    transfer={};capacity=[];failure={}
    with Monitor(f) as monitor:
        started=time.monotonic();total=0;digest=hashlib.sha256()
        with request(f,'GET',items[0]['url'],items[0]['headers']) as response:
            assert response.status==200 and response.getheader('Content-Length')==str(SIZE)
            assert response.getheader('Cache-Control')=='private, no-store'
            etag=response.getheader('ETag')
            while block:=response.read(MIB):
                total+=len(block);digest.update(block)
                if total==MIB:in_flight=no_open_business_transaction(f,'during_throttled_transfer')
                target=started+total/MIB
                if target>time.monotonic():time.sleep(target-time.monotonic())
        seconds=time.monotonic()-started
        assert total==SIZE and digest.hexdigest()==expected and seconds>=120
        single=monitor.summary()
        assert all(values['growth']<64*MIB for values in single.values()),'single_stream_RSS_growth_exceeded_64MiB'
        transfer={**in_flight,'bytes':total,'sha256':expected,'seconds':round(seconds,3),'throttle_bytes_per_second':MIB,'RSS':single}
        # Reads hold actual large-body responses until downstream disconnect.
        capacity=prove_capacity(f,items)
        for name in ('pts','content','gateway'):
            assert max(sample['established_server_connections'][name] for sample in monitor.samples)>=16,'sixteen_held_connections_not_observed'
        concurrent=monitor.summary()
        assert all(values['growth']<192*MIB for values in concurrent.values()),'concurrent_stream_RSS_growth_exceeded_192MiB'
        # Pause only this new fixture's own Storage while a genuine transfer is
        # in flight. Content's 30s upstream-idle bound must terminate partial bytes.
        deadline=time.monotonic()+30
        while True:
            context=request(f,'GET',items[0]['url'],items[0]['headers']);response=context.__enter__()
            if response.status==200:break
            context.__exit__(None,None,None)
            assert response.status==429 and time.monotonic()<deadline
            time.sleep(.1)
        received=0;interrupted=False;paused=False;failure_started=time.monotonic();termination='EOF'
        try:
            assert response.getheader('Content-Length')==str(SIZE)
            first=response.read(MIB);received+=len(first);assert len(first)==MIB
            f.docker('pause',f.storage_frame['container']);paused=True
            try:
                while block:=response.read(MIB):
                    received+=len(block)
                    assert block==first[:len(block)],'binary_stream_contains_foreign_or_error_bytes'
            except (http.client.IncompleteRead,ConnectionError,TimeoutError,ssl.SSLError) as error:
                interrupted=True;termination=type(error).__name__
        finally:
            if paused:f.docker('unpause',f.storage_frame['container'])
            context.__exit__(None,None,None)
        observation={'interrupted_exception':interrupted,'received_bytes':received,'declared_bytes':SIZE,
            'remaining_declared_bytes':response.length,'seconds':round(time.monotonic()-failure_started,3),'termination':termination}
        private(f.out/'upstream-failure-observation.json',observation)
        event(f,phase='upstream_failure_observed',**observation)
        # Bounded HTTPResponse.read(amount) can return EOF without raising; its
        # remaining declared length still exposes a detectably incomplete body.
        premature_eof=termination=='EOF' and response.length==SIZE-received and response.length>0
        assert (interrupted or premature_eof) and 0<received<SIZE and time.monotonic()-failure_started<40,'upstream_failure_was_not_bounded_incomplete'
        # A resumed range is a fresh authorized request against the same ETag.
        deadline=time.monotonic()+30
        while True:
            status,headers,body=read_small(f,items[0],'GET',{'Range':'bytes=0-31','If-Range':etag})
            if status==206:break
            assert status in (429,503) and time.monotonic()<deadline
            time.sleep(.1)
        assert headers.get('etag')==etag and len(body)==32
        failure={'bounded_upstream_idle_failure':True,'partial_bytes':received,'seconds':round(time.monotonic()-failure_started,3),'no_error_bytes_appended':True,'fresh_same_ETag_range_recovered':True}
        # All 16 slots must be available again, including the interrupted account.
        capacity.extend(prove_capacity(f,items))
        cleanup=no_open_business_transaction(f,'after_final_disconnect',settle_cleanup=True)
    graceful=graceful_recovery(f,items[0],expected)
    private(f.out/'resource-proof.json',{'graceful_shutdown':graceful,'transfer':transfer,'capacity':capacity,'failure':failure,'RSS_all_phases':monitor.summary(),
        'no_idle_business_transaction_during_held_stream_observations':True,'final_disconnect_cleanup':cleanup,
        'pts_runtime_mode':'frozen_image' if hasattr(f,'runtime_image') else 'source_process',
        'boundary':'Actual verified generated TLS/APISIX, PtS, Content and Storage. PtS '+('frozen packaged image' if hasattr(f,'runtime_image') else 'source process')+'; Access/Identity '+('frozen packaged image' if getattr(f,'access_image',None) else 'source process')+'; Content and Directory source processes. No hosted/human-device or production-capacity claim.'})
    f.checks.extend(['actual-TLS-128MiB-at-1MiBps-byte-identity-and-process-RSS-connection-occupancy',
        'actual-two-per-account-sixteen-global-seventeenth-denial-disconnect-full-reacquisition',
        'actual-upstream-idle-incomplete-transfer-and-authorized-same-representation-range-recovery',
        'actual-bounded-graceful-SIGTERM-drain-and-new-instance-authorized-range-recovery'])
