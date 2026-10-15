#!/usr/bin/env python3
"""Opt-in run-network proof using a private synthetic Unix daemon only.

No configurable endpoint, real Docker mutation, selected CLI execution or receipt
repair. Prepared sources must be current. This proves adapter checks, not isolation.
"""
from contextlib import contextmanager
import base64
import copy
import hashlib
import json
from pathlib import Path
import socketserver
import sys
import tempfile
import threading
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dev
import networks
import startup

CONTROLS = ['positive', 'existing', 'foreign', 'unsafe-options', 'ipv6', 'attached',
            'conflict', 'lost-response', 'replacement', 'old-daemon', 'malformed',
            'oversized', 'slow', 'daemon-error', 'missing-preparation']
EXPECTED = {'foreign': 'network_not_run_owned', 'unsafe-options': 'network_not_run_owned',
            'ipv6': 'network_not_run_owned', 'attached': 'network_not_run_owned',
            'lost-response': 'docker_response_invalid', 'replacement': 'network_replaced',
            'old-daemon': 'docker_28_required', 'malformed': 'docker_response_invalid',
            'oversized': 'docker_response_invalid', 'slow': 'docker_timeout',
            'daemon-error': 'network_inspection_failed', 'missing-preparation': 'prepared_run_required'}


API_PREFIX = '/v1.48/networks/'


def expected_request(target, run_id):
    """Independent contract oracle, deliberately separate from production choices."""
    token = base64.urlsafe_b64encode(uuid.UUID(run_id).bytes).decode().rstrip('=')
    project = target['project_id_prefix'] + '-' + token
    return {'Name': project + '-network', 'Driver': 'bridge', 'Scope': 'local',
            'EnableIPv4': True, 'EnableIPv6': False, 'Internal': False,
            'Attachable': False, 'Ingress': False, 'ConfigOnly': False,
            'Options': {'com.docker.network.bridge.host_binding_ipv4': '127.0.0.1'},
            'Labels': {'io.agriplatform.env.owner': 'platform/deployment',
                       'io.agriplatform.env.target': target['target_id'],
                       'io.agriplatform.env.run': run_id,
                       'io.agriplatform.env.project': project}}


class SyntheticDaemon:
    """Real Unix-socket HTTP boundary, strict event inventory and controlled state."""
    def __init__(self, target, run_id, control='positive'):
        self.target, self.run_id, self.control = target, run_id, control
        self.network_id = hashlib.sha256(run_id.encode()).hexdigest()
        self.name = expected_request(target, run_id)['Name']
        self.network = dict(expected_request(target, run_id), Id=self.network_id,
                            Containers={}, ConfigFrom={'Network': ''}, Created='2026-10-15T00:00:00Z', IPAM={'Driver': 'default'})
        self.present = control in ['existing', 'foreign', 'unsafe-options', 'ipv6', 'attached',
                                   'replacement', 'malformed', 'oversized', 'slow', 'daemon-error']
        self.events, self.errors, self.inspect_count = [], [], 0
        self.hook = None
        if control == 'foreign':
            self.network['Labels']['io.agriplatform.env.owner'] = 'foreign'
        elif control == 'unsafe-options':
            self.network['Options']['com.docker.network.bridge.host_binding_ipv4'] = '0.0.0.0'
        elif control == 'ipv6':
            self.network['EnableIPv6'] = True
        elif control == 'attached':
            self.network['Containers'] = {'foreign': {'Name': 'private-marker'}}

    def dispatch(self, method, path, body):
        self.events.append((method, path, body))
        if self.hook:
            self.hook(method, path)
        if method == 'GET' and path == '/version':
            return 200, {'Version': '27.9.9' if self.control == 'old-daemon' else '28.0.0', 'Os': 'linux'}
        if method == 'POST' and path == API_PREFIX + 'create':
            if body != expected_request(self.target, self.run_id) or self.present:
                self.errors.append('create_input_mismatch')
                return 500, {}
            self.present = True
            return (409 if self.control == 'conflict' else 201), {'Id': self.network_id, 'Warning': ''}
        if method == 'GET' and path in [API_PREFIX + self.name, API_PREFIX + self.network_id]:
            self.inspect_count += 1
            if self.control == 'daemon-error':
                return 500, {'message': 'sensitive-marker'}
            if not self.present:
                return 404, {'message': 'sensitive-marker'}
            result = copy.deepcopy(self.network)
            if self.control == 'replacement' and self.inspect_count > 1:
                result['Id'] = 'b' * 64
            return 200, result
        self.errors.append('unauthorized_operation')
        return 500, {}

    def validate_events(self):
        if self.errors or not self.events:
            networks.fail('synthetic_event_mismatch')
        allowed = {('GET', '/version'), ('GET', API_PREFIX + self.name),
                   ('GET', API_PREFIX + self.network_id), ('POST', API_PREFIX + 'create')}
        if any((method, path) not in allowed for method, path, _ in self.events):
            networks.fail('synthetic_event_mismatch')
        if any((body != expected_request(self.target, self.run_id) if method == 'POST' else body is not None)
               for method, _, body in self.events):
            networks.fail('synthetic_event_mismatch')
        version = ('GET', '/version')
        name = ('GET', API_PREFIX + self.name)
        network_id = ('GET', API_PREFIX + self.network_id)
        create = ('POST', API_PREFIX + 'create')
        success_sequences = {
            'positive': [version, name, create, network_id, network_id, name, network_id],
            'existing': [version, name, network_id, name, network_id],
            'conflict': [version, name, create, name, network_id, name, network_id],
        }
        if self.control in success_sequences:
            if [(method, path) for method, path, _ in self.events] != success_sequences[self.control]:
                networks.fail('synthetic_event_mismatch')
        posts = [(method, path, body) for method, path, body in self.events if method == 'POST']
        expected_posts = 1 if self.control in ['positive', 'conflict', 'lost-response'] else 0
        if len(posts) != expected_posts:
            networks.fail('synthetic_event_mismatch')
        if self.control == 'old-daemon' and len(self.events) != 1:
            networks.fail('synthetic_event_mismatch')

    @contextmanager
    def serve(self):
        daemon = self
        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                try:
                    self.request.settimeout(1)
                    data = b''
                    while b'\r\n\r\n' not in data:
                        chunk = self.request.recv(4096)
                        if not chunk or len(data) + len(chunk) > 16384:
                            return
                        data += chunk
                    header, body = data.split(b'\r\n\r\n', 1)
                    lines = header.split(b'\r\n')
                    method, path, protocol = lines[0].decode('ascii').split(' ')
                    fields = dict(line.lower().split(b':', 1) for line in lines[1:])
                    length = int(fields.get(b'content-length', b'0'))
                    if length > 16384:
                        return
                    while len(body) < length:
                        chunk = self.request.recv(4096)
                        if not chunk:
                            return
                        body += chunk
                    payload = dev.decode(body) if body else None
                    status, response = daemon.dispatch(method, path, payload)
                    if method == 'POST' and daemon.control == 'lost-response':
                        return
                    if '/networks/' in path:
                        if daemon.control == 'malformed':
                            self.request.sendall(b'not-http-sensitive-marker')
                            return
                        if daemon.control == 'oversized':
                            self.request.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 999999\r\n\r\n')
                            return
                        if daemon.control == 'slow':
                            daemon.stop.wait(networks.SECONDS + .2)
                            return
                    raw = json.dumps(response).encode()
                    wire = (f'HTTP/1.1 {status} Result\r\nContent-Length: {len(raw)}\r\n\r\n'.encode() + raw)
                    self.request.sendall(wire)
                except (OSError, ValueError, dev.Refusal):
                    # Keep uncontrolled response/request content out of diagnostics.
                    daemon.errors.append('synthetic_transport_error')
        with tempfile.TemporaryDirectory(prefix='env-net-socket-') as temporary:
            path = str(Path(temporary) / 'daemon.sock')
            self.stop = threading.Event()
            with socketserver.UnixStreamServer(path, Handler) as server:
                thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': .01}, daemon=True)
                thread.start()
                try:
                    yield path
                finally:
                    self.stop.set()
                    server.shutdown()
                    thread.join(timeout=1)


def qualify(args):
    networks.validate_run_id(args.run_id)
    path = Path(args.target).absolute()
    target = dev.decode(dev.read(path))
    daemon = SyntheticDaemon(target, args.run_id, args.control)
    with daemon.serve() as endpoint, tempfile.TemporaryDirectory(prefix='env-network-work-') as temporary:
        work = Path(temporary)
        startup.initialize_workdir(work, target, args.run_id)
        try:
            # Construct only. No subprocess or Docker CLI is invoked.
            argv, env = networks.invocation(path, args.run_id, '/synthetic/not-executed/supabase', work,
                                            _socket_path=endpoint)
        except dev.Refusal as error:
            if args.control in EXPECTED and EXPECTED[args.control] != error.code:
                networks.fail('synthetic_outcome_mismatch')
            if args.control == 'missing-preparation':
                if daemon.events:
                    networks.fail('synthetic_event_mismatch')
            else:
                daemon.validate_events()
            # The qualifier returns the same safe failure and nonzero status.
            raise
        if args.control not in ['positive', 'existing', 'conflict']:
            networks.fail('negative_control_failed')
        daemon.validate_events()
        if argv[-2:] != ['--network-id', daemon.network_id] or env['DOCKER_HOST'] != 'unix:///var/run/docker.sock':
            networks.fail('synthetic_handoff_mismatch')
        return {'ok': True, 'code': 'network_synthetic_qualified', 'stage': 'network',
                'control': args.control, 'runtime_ready': False, 'network_id': daemon.network_id,
                'created': args.control == 'positive',
                'api_events': [{'method': method, 'path': path} for method, path, _ in daemon.events]}


def main(argv=None):
    try:
        parser = dev.Parser(add_help=False, allow_abbrev=False)
        parser.add_argument('--target', required=True)
        parser.add_argument('--run-id', required=True)
        parser.add_argument('--control', choices=CONTROLS, default='positive')
        result = qualify(parser.parse_args(argv))
        print(json.dumps(result, sort_keys=True))
        return 0
    except dev.Refusal as error:
        result = {'ok': False, 'runtime_ready': False, 'stage': error.stage, 'code': error.code}
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        result = {'ok': False, 'runtime_ready': False, 'stage': 'network', 'code': 'network_proof_refused'}
    print(json.dumps(result, sort_keys=True))
    return 2


if __name__ == '__main__':
    sys.exit(main())
