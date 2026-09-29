"""Bounded, recoverable certificate adoption under the release coordinator's lock."""
import argparse
import fcntl
import hashlib
import http.client
import json
import os
from pathlib import Path
import signal
import shutil
import socket
import ssl
import subprocess
import tempfile
import time
from urllib.parse import urlsplit

PRIMARY_SECONDS = 180
RECOVERY_SECONDS = 120


class Failure(Exception):
    """Only locally selected stable identifiers cross the diagnostic boundary."""
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class Control:
    def __init__(self):
        self.interrupted = False

    def stop(self, signum, frame):
        # Drain the bounded current command. The next checkpoint enters recovery.
        self.interrupted = True


class Budget:
    def __init__(self, control=None, seconds=PRIMARY_SECONDS, recovery=False):
        self.control = control or Control()
        self.until = time.monotonic() + seconds
        self.recovery = recovery

    def check(self):
        if self.control.interrupted and not self.recovery:
            raise Failure('interrupted')
        if time.monotonic() >= self.until:
            raise Failure('operation_timeout')

    def timeout(self, maximum):
        self.check()
        return min(maximum, max(0.001, self.until - time.monotonic()))


def run(args, budget, code, maximum=10, **kwargs):
    try:
        result = subprocess.run(args, check=True, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL,
                                timeout=budget.timeout(maximum), **kwargs).stdout
    except Failure:
        raise
    except subprocess.TimeoutExpired:
        raise Failure('command_timeout') from None
    except Exception:
        raise Failure(code) from None
    budget.check()
    return result


def leaf_fingerprint(cert, budget=None):
    # OpenSSL reads the first leaf, even when its DER encoding has no Base64 padding.
    return hashlib.sha256(run(['openssl', 'x509', '-in', str(cert), '-outform', 'DER'],
                              budget or Budget(), 'certificate_parse')).hexdigest()


def validate(cert, key, host, budget=None):
    budget = budget or Budget()
    run(['openssl', 'x509', '-in', str(cert), '-noout', '-checkend', '86400'],
        budget, 'certificate_expiry')
    # x509 -checkhost prints a mismatch but exits zero on some OpenSSL releases.
    # Explicit leaf trust isolates hostname validation from the chain check below.
    run(['openssl', 'verify', '-trusted', str(cert), '-partial_chain',
         '-no-CAfile', '-no-CApath', '-no-CAstore', '-verify_hostname', host, str(cert)],
        budget, 'certificate_hostname')
    certkey = run(['openssl', 'x509', '-in', str(cert), '-pubkey', '-noout'],
                  budget, 'certificate_parse')
    privatekey = run(['openssl', 'pkey', '-in', str(key), '-passin', 'pass:', '-pubout'],
                     budget, 'private_key_parse')
    if certkey != privatekey:
        raise Failure('certificate_key_mismatch')
    run(['openssl', 'verify', '-purpose', 'sslserver', '-verify_hostname', host,
         '-untrusted', str(cert), str(cert)], budget, 'certificate_trust')
    return leaf_fingerprint(cert, budget)


def atomic(path, content, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            os.fchmod(stream.fileno(), mode)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(directory_fd)
        finally: os.close(directory_fd)
    finally:
        if os.path.exists(name): os.unlink(name)


def save(path, document):
    atomic(path, (json.dumps(document, indent=2)+'\n').encode())



def diagnostic(path, report):
    try: save(path, report)
    except Exception: report['diagnostic_write_failed'] = True


def safe_code(error):
    return error.code if isinstance(error, Failure) else 'tls_operation_failed'


def durable_unlink(path):
    path.unlink()
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)


def discard_backup(state, pending):
    backup = Path(pending['backup'])
    if backup.parent == state and backup.name.startswith('tls-backup-'):
        try: shutil.rmtree(backup)
        except OSError: pass  # Completed transaction; retain leftovers for operator cleanup.


def prune_evidence(state):
    # Bound routine polling records only. Failures, recoveries and referenced
    # evidence remain available for explicit operational retention review.
    protected = set()
    def references(value):
        if isinstance(value, str): protected.add(value)
        elif isinstance(value, dict):
            for item in value.values(): references(item)
        elif isinstance(value, list):
            for item in value: references(item)
    try:
        for name in ('current.json', 'tls-pending.json', 'release-pending.json'):
            path = state/name
            if path.exists(): references(json.loads(path.read_text()))
        routine = []
        for path in state.glob('tls-[0-9]*.json'):
            document = json.loads(path.read_text())
            if (document.get('outcome') in ('already_active', 'pending_gateway_activation')
                    and not any(key in document for key in ('recovery', 'prior_recovery'))
                    and str(path) not in protected):
                routine.append(path)
        for path in sorted(routine, key=lambda item: item.stat().st_mtime_ns)[:-96]:
            path.unlink()
    except Exception: pass  # Retention failures must never interfere with recovery.


def protect_gateway(directory):
    directory.chmod(0o750)
    os.chown(directory, -1, 636)
    (directory/'apisix.yaml').chmod(0o640)
    os.chown(directory/'apisix.yaml', -1, 636)


def activate(compose, budget):
    run(['docker', 'compose', '-f', str(compose), 'up', '-d', '--no-deps',
         '--force-recreate', '--pull', 'never', 'gateway'],
        budget, 'gateway_activation', maximum=60)


def verify_served(api, fingerprint, budget=None):
    budget = budget or Budget()
    target = urlsplit(api)
    port = target.port or 443
    context = ssl.create_default_context()
    try:
        with socket.create_connection(('127.0.0.1', port), timeout=budget.timeout(5)) as tcp:
            with context.wrap_socket(tcp, server_hostname=target.hostname) as tls:
                if hashlib.sha256(tls.getpeercert(binary_form=True)).hexdigest() != fingerprint:
                    raise Failure('served_fingerprint')
                tls.settimeout(budget.timeout(5))
                tls.sendall(('GET /directory/api/apps HTTP/1.1\r\nHost: '+target.netloc+
                             '\r\nConnection: close\r\n\r\n').encode('ascii'))
                response = http.client.HTTPResponse(tls)
                response.begin()
                if not 200 <= response.status < 300:
                    raise Failure('api_route_health')
    except Failure:
        raise
    except ssl.SSLError:
        raise Failure('served_trust') from None
    except Exception:
        raise Failure('served_connection') from None
    budget.check()


def verify_retry(api, fingerprint, budget):
    for attempt in range(3):
        try:
            verify_served(api, fingerprint, budget)
            return
        except Failure:
            budget.check()
            if attempt == 2: raise
            time.sleep(min(1, budget.timeout(1)))


def restore_pending(config, pending, budget, attempt_uncertain=False):
    """Also used after process loss/reboot; intent survives until recovery completes."""
    state = Path(config['state_dir'])
    if pending.get('docker_state_uncertain') and not attempt_uncertain:
        raise Failure('docker_state_uncertain')
    previous = pending['previous']
    if previous is not None:
        activate(Path(previous['compose']), budget)
        verify_retry(config['api'], pending['previous_fingerprint'], budget)
    for field in ('cert', 'key'):
        destination = Path(config[field])
        backup = Path(pending['backup'])/field
        if field in pending['existed']:
            atomic(destination, backup.read_bytes())
        elif destination.exists():
            destination.unlink()
        budget.check()
    if previous is not None:
        save(state/'current.json', previous)
    if pending.get('docker_state_uncertain'):
        raise Failure('docker_state_uncertain')
    durable_unlink(state/'tls-pending.json')
    discard_backup(state, pending)


def install_pair(config, cert, key, budget):
    for field, source in (('cert', cert), ('key', key)):
        budget.check()
        atomic(Path(config[field]), source.read_bytes())
        budget.check()


def prepare_gateway(current, cert, key, state):
    previous = Path(current['compose'])
    old = json.loads((previous.parent/'apisix.yaml').read_text().removesuffix('\n#END\n'))
    if len(old['ssls']) != 1:
        raise Failure('unsupported_tls_configuration')
    material = {'cert': cert.read_text(), 'key': key.read_text()}
    if all(old['ssls'][0][field] == value for field, value in material.items()):
        return None
    directory = Path(tempfile.mkdtemp(prefix='tls-gateway-', dir=state))
    old['ssls'][0].update(material)
    atomic(directory/'apisix.yaml', (json.dumps(old, indent=2)+'\n#END\n').encode())
    atomic(directory/'config.yaml', (previous.parent/'config.yaml').read_bytes(), 0o644)
    compose = json.loads(previous.read_text())
    volumes = compose['services']['gateway']['volumes']
    for name in ('config.yaml', 'apisix.yaml'):
        oldmount = str(previous.parent/name)+':/usr/local/apisix/conf/'+name+':ro'
        if oldmount not in volumes:
            raise Failure('unsupported_gateway_mount')
        volumes[volumes.index(oldmount)] = str(directory/name)+':/usr/local/apisix/conf/'+name+':ro'
    save(directory/'compose.json', compose)
    protect_gateway(directory)
    return directory/'compose.json'


def install(config, cert, key, control=None):
    control = control or Control()
    budget = Budget(control)
    state = Path(config['state_dir'])
    state.mkdir(parents=True, exist_ok=True, mode=0o750)
    evidence = state/('tls-'+str(time.time_ns())+'.json')
    report = {'operation': 'tls_adoption', 'started_at': int(time.time()),
              'outcome': 'failed', 'phase': 'lock'}
    pending_path = state/'tls-pending.json'
    diagnostic(evidence, report)
    try:
        with (state/'release.lock').open('a') as lock:
            try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError: raise Failure('release_busy') from None
            if (state/'release-pending.json').exists():
                raise Failure('release_activation_pending')
            target = urlsplit(config['api'])
            if (config['environment'] not in ('production', 'staging') or target.scheme != 'https'
                    or not target.hostname or target.username or target.password
                    or target.path or target.query or target.fragment):
                raise Failure('invalid_target')
            if pending_path.exists():
                report['phase'] = 'interrupted_operation_recovery'
                diagnostic(evidence, report)
                try:
                    restore_pending(config, json.loads(pending_path.read_text()),
                                    Budget(control, RECOVERY_SECONDS, recovery=True))
                    report['prior_recovery'] = 'verified'
                except Exception as error:
                    report['prior_recovery_code'] = safe_code(error)
                    report['prior_recovery'] = 'failed'
                    raise Failure('prior_recovery_failed') from None
                # Bound a reboot reconciliation to recovery only; next timer adopts.
                report['outcome'] = 'recovered_retry_required'
                return report
            report['phase'] = 'validation'
            with tempfile.TemporaryDirectory(prefix='tls-candidate-', dir=state) as temp:
                snapshot = Path(temp)
                atomic(snapshot/'fullchain.pem', cert.read_bytes())
                atomic(snapshot/'privkey.pem', key.read_bytes())
                cert, key = snapshot/'fullchain.pem', snapshot/'privkey.pem'
                fingerprint = validate(cert, key, target.hostname, budget)
                report['fingerprint'] = fingerprint
                current_path = state/'current.json'
                current = json.loads(current_path.read_text()) if current_path.exists() else None
                candidate = prepare_gateway(current, cert, key, state) if current else None
                previous_fingerprint = None
                if current:
                    old = json.loads((Path(current['compose']).parent/'apisix.yaml').read_text().removesuffix('\n#END\n'))
                    atomic(snapshot/'previous.pem', old['ssls'][0]['cert'].encode())
                    previous_fingerprint = leaf_fingerprint(snapshot/'previous.pem', budget)
                    if candidate is None:
                        verify_retry(config['api'], fingerprint, budget)
                if candidate is None and all(Path(config[field]).exists() and
                        Path(config[field]).read_bytes() == source.read_bytes()
                        for field, source in (('cert', cert), ('key', key))):
                    report['outcome'] = 'already_active' if current else 'pending_gateway_activation'
                    return report
                backup = Path(tempfile.mkdtemp(prefix='tls-backup-', dir=state))
                existed = []
                for field in ('cert', 'key'):
                    source = Path(config[field])
                    if source.exists():
                        atomic(backup/field, source.read_bytes())
                        existed.append(field)
                pending = {'previous': current, 'previous_fingerprint': previous_fingerprint,
                           'backup': str(backup), 'existed': existed,
                           'candidate_compose': str(candidate) if candidate else None,
                           'evidence': str(evidence)}
                report['phase'] = 'installation'
                report['previous_compose'] = current['compose'] if current else None
                report['candidate_compose'] = pending['candidate_compose']
                diagnostic(evidence, report)
                save(pending_path, pending)  # fsync intent before any gateway/copy mutation
                try:
                    budget.check()
                    if candidate:
                        report['phase'] = 'gateway_activation'; diagnostic(evidence, report)
                        activate(candidate, budget)
                        budget.check()
                        report['phase'] = 'gateway_verification'; diagnostic(evidence, report)
                        verify_retry(config['api'], fingerprint, budget)
                    install_pair(config, cert, key, budget)
                    if candidate:
                        save(current_path, {**current, 'compose': str(candidate), 'tls_evidence': str(evidence)})
                    budget.check()
                    report['outcome'] = ('activated' if candidate else
                                         'already_active' if current else 'pending_gateway_activation')
                    diagnostic(evidence, report)
                    durable_unlink(pending_path)
                    discard_backup(state, pending)
                except BaseException as original_error:
                    if safe_code(original_error) == 'command_timeout':
                        pending['docker_state_uncertain'] = True
                        report['docker_state_uncertain'] = True
                        try: save(pending_path, pending)
                        except Exception: report['intent_write_failed'] = True
                    report['recovery'] = 'failed'; diagnostic(evidence, report)
                    try:
                        restore_pending(config, pending, Budget(control, RECOVERY_SECONDS, recovery=True), attempt_uncertain=True)
                        report['recovery'] = 'verified'
                    except Exception as error:
                        report['recovery_code'] = safe_code(error)
                        if safe_code(error) == 'command_timeout':
                            pending['docker_state_uncertain'] = True
                            report['docker_state_uncertain'] = True
                            try: save(pending_path, pending)
                            except Exception: report['intent_write_failed'] = True
                    raise
    except Failure as failure:
        report['code'] = failure.code
        report['outcome'] = 'failed'
        raise
    except Exception:
        report['code'] = 'tls_operation_failed'
        report['outcome'] = 'failed'
        raise Failure('tls_operation_failed') from None
    finally:
        report['interrupted'] = control.interrupted
        report['finished_at'] = int(time.time())
        diagnostic(evidence, report)
        prune_evidence(state)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--lineage', required=True, type=Path)
    args = parser.parse_args()
    control = Control()
    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, control.stop)
    try:
        report = install(json.loads(args.config.read_text()), args.lineage/'fullchain.pem',
                         args.lineage/'privkey.pem', control)
        print(json.dumps({'operation': 'tls_adoption', 'outcome': report['outcome']}))
        if report['outcome'] == 'recovered_retry_required' or report.get('diagnostic_write_failed'): return 1
    except Exception:
        print('TLS adoption failed; inspect protected tls evidence; timer will retry', file=__import__('sys').stderr)
        return 1
    return 0


if __name__ == '__main__': raise SystemExit(main())
