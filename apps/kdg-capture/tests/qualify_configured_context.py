"""Explicit synthetic loopback KDG→TLS Access→retained PostgreSQL acceptance.

Run with the approved Access Python environment. Never installs or changes data.
"""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import signal
import socket
import ssl
import stat
import subprocess
import sys
import time
from uuid import uuid4

import httpx

ROOT = Path(__file__).resolve().parents[3]
API = ROOT / 'apps/kdg-capture/api'
OUTPUT_ROOT = ROOT / 'platform/deployment/.local/kdg-configured-context-20261022'
FIXTURE = ROOT / 'platform/deployment/.local/identity-baseline/organization-check-reviewed3-20261022'
RETAINED_SHA = '2c341e184cc151eaa017a9c46e96028959165c867e02eed5528cfb43f1f2f48b'
SAFE_ENV = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C.UTF-8'}


class QualificationFailure(RuntimeError):
    pass


class QualificationInterrupted(RuntimeError):
    def __init__(self, number):
        self.number = number
        super().__init__('supervisor_termination')


def require(condition, identifier):
    if not condition:
        raise QualificationFailure(identifier)


def failure_id(error):
    # Only our fixed identifiers are eligible; never serialize arbitrary messages.
    return str(error) if isinstance(error, (QualificationFailure, QualificationInterrupted)) else type(error).__name__


def runtime_provenance():
    interpreter = Path(sys.executable).resolve()
    return {'executable':sys.executable,'resolved_executable':str(interpreter),
            'executable_sha256':hashlib.sha256(interpreter.read_bytes()).hexdigest(),
            'python':sys.version,'openssl':ssl.OPENSSL_VERSION,
            'packages':{name:importlib.metadata.version(name) for name in
                ('fastapi','pydantic','httpx','uvicorn','sqlalchemy','psycopg','starlette','anyio')},
            'locks':{str(path):hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in
                (Path('services/access/uv.lock'),Path('apps/kdg-capture/api/uv.lock'))}}


def private_json(path):
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and not path.is_symlink()
            and info.st_uid == os.getuid() and not info.st_mode & 0o077, 'private_input_invalid')
    return json.loads(path.read_text())


def checked_process(command, proof, label, environment=None):
    with (proof/(label+'.log')).open('xb') as output:
        result = subprocess.run(command, cwd=ROOT, env=environment or SAFE_ENV,
                                stdout=output, stderr=subprocess.STDOUT, timeout=40)
    require(result.returncode == 0, label+'_failed')


def listener():
    channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    channel.bind(('127.0.0.1', 0))
    channel.listen(128)
    return channel


def launch(command, channel, proof, label, environment):
    output = (proof/(label+'.log')).open('xb')
    try:
        process = subprocess.Popen(command+[str(channel.fileno())], cwd=ROOT,
            env=environment, pass_fds=(channel.fileno(),), stdout=output, stderr=subprocess.STDOUT)
    finally:
        output.close()
        channel.close()
    return process


def stop(process, proof, label):
    if process.poll() is None:
        process.send_signal(signal.SIGTERM)
    try:
        code = process.wait(timeout=12)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3)
        (proof/(label+'-forced.json')).write_text(json.dumps({'forced_termination': True}))
        raise RuntimeError(label+'_forced_termination') from None
    require(code == 0, label+'_exit_failed')


def wait_http(process, address, *, verify=True):
    deadline = time.monotonic()+15
    with httpx.Client(verify=verify, trust_env=False, timeout=0.3) as client:
        while time.monotonic() < deadline:
            require(process.poll() is None, 'test_server_exited')
            try:
                result = client.get(address)
                if result.status_code in (200,401):
                    return result
            except httpx.HTTPError:
                pass
            time.sleep(0.05)
    raise RuntimeError('test_server_start_timeout')


def serve_kdg(proof, fd):
    # Explicit test-only CA transport; production factory retains normal TLS verification.
    values = private_json(proof/'access-ready.json')
    policy = {'KDG_ORG_ID': values['org_id'], 'KDG_SERVICE_KEY':values['service_key'],
              'KDG_ACCESS_URL':os.environ['KDG_ACCESS_URL']}
    os.environ.update(policy)
    sys.path.insert(0,str(API))
    from runtime import create_app
    import uvicorn
    transport = httpx.AsyncHTTPTransport(verify=ssl.create_default_context(cafile=proof/'tls-cert.pem'), trust_env=False)
    app = create_app(transport=transport)
    channel = socket.socket(fileno=fd)
    require(channel.family == socket.AF_INET and channel.getsockname()[0] == '127.0.0.1', 'socket_invalid')
    server = uvicorn.Server(uvicorn.Config(app, access_log=False, log_level='warning'))
    signal.signal(signal.SIGTERM, lambda signum, frame: None)
    server.run(sockets=[channel])
    require(server.started, 'kdg_server_did_not_start')


def run(*, interrupt_probe=False):
    require(__debug__, 'optimized_python_prohibited')
    require(OUTPUT_ROOT.is_dir() and not OUTPUT_ROOT.is_symlink(), 'output_root_invalid')
    proof = OUTPUT_ROOT / ('native-'+uuid4().hex)
    proof.mkdir(mode=0o700)
    os.umask(0o077)
    paths = [API/'runtime.py',API/'main.py',API/'context.py',API/'safe_errors.py',Path(__file__).resolve(),
             ROOT/'services/access/tests/serve_kdg_context_fixture.py',
             ROOT/'services/access/main.py',ROOT/'services/access/organization_check.py']
    source_hashes = {}
    for path in paths:
        data = path.read_bytes()
        name = str(path.relative_to(ROOT))
        source_hashes[name] = hashlib.sha256(data).hexdigest()
        copy = proof/'executed-sources'/name
        copy.parent.mkdir(parents=True,exist_ok=True)
        copy.write_bytes(data)
    observer = [sys.executable,'-I','-B',str(ROOT/'services/access/tests/qualify_organization_check.py'),'--verify-retained']
    observer_env = SAFE_ENV | {'IDENTITY_QUALIFICATION_DIR':str(FIXTURE)}
    provenance = runtime_provenance()
    processes, results = [], []
    success, values, permission_reads = False, None, None
    stage, failure, failed_stage, interrupted = 'created', None, None, None
    retained_after = {'status':'not_attempted'}
    tokens = tuple('synthetic-'+kind for kind in ('positive','denied','unmapped','unknown'))
    previous_handlers = {}
    def request_termination(number, frame):
        nonlocal interrupted
        if interrupted is None:
            interrupted = number
            raise QualificationInterrupted(number)
    for number in (signal.SIGTERM,signal.SIGINT):
        previous_handlers[number] = signal.signal(number,request_termination)
    try:
        stage='retained_before'
        checked_process(observer,proof,'retained-before',observer_env)
        receipt = FIXTURE/'organization-check-retained.json'
        require(hashlib.sha256(receipt.read_bytes()).hexdigest()==RETAINED_SHA, 'retained_receipt_changed')
        stage='tls_fixture'
        checked_process(['/usr/bin/openssl','req','-x509','-newkey','rsa:2048','-nodes',
            '-keyout',str(proof/'tls-key.pem'),'-out',str(proof/'tls-cert.pem'),'-days','1',
            '-subj','/CN=localhost','-addext','subjectAltName=IP:127.0.0.1,DNS:localhost'],proof,'tls-fixture')
        stage='access_start'
        access_socket = listener()
        access_url = 'https://127.0.0.1:'+str(access_socket.getsockname()[1])
        access = launch([sys.executable,'-I','-B',str(ROOT/'services/access/tests/serve_kdg_context_fixture.py'),str(proof)],
                        access_socket,proof,'access-server',SAFE_ENV)
        processes.append(('access',access))
        ca = ssl.create_default_context(cafile=proof/'tls-cert.pem')
        wait_http(access,access_url+'/health',verify=ca)
        values = private_json(proof/'access-ready.json')
        stage='kdg_start'
        kdg_socket = listener()
        address = 'http://127.0.0.1:'+str(kdg_socket.getsockname()[1])+'/api/v1/context'
        kdg = launch([sys.executable,'-I','-B',str(Path(__file__).resolve()),'--serve-kdg',str(proof)],
                     kdg_socket,proof,'kdg-server',SAFE_ENV | {'KDG_ACCESS_URL':access_url})
        processes.append(('kdg',kdg))
        wait_http(kdg,address)
        if interrupt_probe:
            stage='supervisor_interruption_probe'
            os.kill(os.getpid(),signal.SIGTERM)
        stage='consuming_http'
        with httpx.Client(timeout=12, trust_env=False) as client:
            def request(kind, expected, identifier=None, query=''):
                result = client.get(address+query,headers={'Authorization':'Bearer synthetic-'+kind})
                require(all(secret not in result.text for secret in (values['service_key'],)+tokens),'response_credential_leak')
                require(result.status_code == expected, kind+'_status_mismatch')
                require(result.headers.get('cache-control') == 'private, no-store',kind+'_cache_mismatch')
                body = result.json()
                if identifier:
                    require(body.get('error_id') == identifier,kind+'_error_mismatch')
                else:
                    require(body.get('account_id')==values['positive'] and body.get('actor_id')==values['actor_id']
                        and body.get('membership_id')==values['membership_id']
                        and body.get('permission')=='kdg_capture.capture.read.own'
                        and body.get('authorization_scope')=={'kind':'organization','org_id':values['org_id']}
                        and body.get('resource_scope')=={'kind':'own_account','account_id':values['positive']},'context_binding_mismatch')
                results.append({'case':kind+query.split('=')[0],'status':result.status_code,'error_id':identifier})
                return body
            first = request('positive',200)
            second = request('positive',200)
            require(first['decision_id']!=second['decision_id'],'decision_was_reused')
            request('denied',403,'access_denied')
            request('unmapped',409,'identity.actor_setup_required')
            request('unknown',401,'authentication_required')
            request('positive',422,'validation_failed','?org_id='+values['org_id'])
            stage='access_stop'
            stop(access,proof,'access')
            stage='owner_unavailable'
            started=time.monotonic()
            request('positive',503,'authorization_unavailable')
            require(time.monotonic()-started < 4,'unavailable_deadline_exceeded')
        permission_reads = private_json(proof/'access-summary.json')['permission_reads']
        require(permission_reads==4,'actual_sql_read_count_mismatch')
        stage='kdg_stop'
        stop(kdg,proof,'kdg')
        # Exercise the advertised unmodified ASGI entry point through Uvicorn's CLI.
        # A single unauthenticated401 checks factory loading without private TLS trust.
        stage='factory_entrypoint'
        cli_socket = listener()
        cli_address='http://127.0.0.1:'+str(cli_socket.getsockname()[1])+'/api/v1/context'
        cli_env=SAFE_ENV | {'KDG_ORG_ID':values['org_id'],'KDG_ACCESS_URL':access_url,'KDG_SERVICE_KEY':values['service_key']}
        cli=launch([sys.executable,'-I','-B','-m','uvicorn','--app-dir',str(API),'runtime:create_app',
                    '--factory','--limit-max-requests','1','--timeout-graceful-shutdown','3',
                    '--no-access-log','--log-level','warning','--fd'],cli_socket,proof,'entrypoint-server',cli_env)
        processes.append(('entrypoint',cli))
        smoke=wait_http(cli,cli_address)
        require(smoke.status_code==401 and smoke.headers.get('cache-control')=='private, no-store'
                and smoke.json().get('error_id')=='authentication_required','entrypoint_smoke_failed')
        require(cli.wait(timeout=10)==0,'entrypoint_exit_failed')
        results.append({'case':'uvicorn_factory_entrypoint','status':401,'error_id':'authentication_required'})
        stage='source_custody'
        require(all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in source_hashes.items()), 'executed_source_changed')
        success=True
    except Exception as error:
        failure, failed_stage = failure_id(error), stage
        raise
    finally:
        teardown=[]
        for label,process in reversed(processes):
            try:
                if process.poll() is None:
                    stop(process,proof,label)
                require(process.returncode==0,label+'_exit_failed')
                teardown.append({'server':label,'exit_code':process.returncode})
            except Exception as error:
                teardown.append({'server':label,'failure':failure_id(error),'exit_code':process.returncode})
                success=False
                if failure is None:
                    failure, failed_stage=failure_id(error),'teardown_'+label
        # Always attempt the independent after-inspection, including interruption or
        # failed assertions/forced teardown. Its failure cannot erase earlier evidence.
        try:
            checked_process(observer,proof,'retained-after',observer_env)
            retained_after={'status':'passed'}
        except Exception as error:
            retained_after={'status':'failed','identifier':failure_id(error)}
            success=False
            if failure is None:
                failure, failed_stage='retained_after_failed','retained_after'
        if values is not None:
            try:
                for label in ('access-server','kdg-server','entrypoint-server'):
                    path=proof/(label+'.log')
                    if path.exists():
                        text=path.read_text()
                        require(all(secret not in text for secret in (values['service_key'],)+tokens),'server_log_credential_leak')
            except Exception as error:
                success=False
                if failure is None:
                    failure, failed_stage=failure_id(error),'log_confidentiality'
        evidence={'schema_version':1,'passed':success,'cases':results,'teardown':teardown,
            'failure_identifier':failure,'failure_stage':failed_stage,'interruption_signal':interrupted,
            'expected_interruption_probe':interrupt_probe,'retained_after':retained_after,
            'permission_reads':permission_reads,'runtime':provenance,
            'retained_receipt_sha256':RETAINED_SHA,'sources':source_hashes,
            'access_shutdown_warning': 'timeout graceful shutdown exceeded' in (proof/'access-server.log').read_text() if (proof/'access-server.log').exists() else None,
            'logs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in proof.glob('*.log')},
            'limitations':['synthetic bearer verification','no real provider/browser/device qualification','static retained grants; no lifecycle mutations'],
            'proof':str(proof.relative_to(ROOT))}
        (proof/'result.json').write_text(json.dumps(evidence,sort_keys=True,indent=2)+'\n')
        for number,previous in previous_handlers.items():
            signal.signal(number,previous)
        print(json.dumps({'passed':success,'proof':str(proof.relative_to(ROOT))}),flush=True)
    require(success,'qualification_failed')


if __name__=='__main__':
    try:
        if sys.argv[1:] == ['--run']:
            run()
        elif sys.argv[1:] == ['--interrupt-probe']:
            run(interrupt_probe=True)
        elif len(sys.argv)==4 and sys.argv[1]=='--serve-kdg':
            serve_kdg(Path(sys.argv[2]),int(sys.argv[3]))
        else:
            raise RuntimeError('arguments_invalid')
    except Exception as error:
        print('kdg_context_qualification_failed:'+failure_id(error),file=sys.stderr)
        raise SystemExit(128+error.number if isinstance(error,QualificationInterrupted) else 1) from None
