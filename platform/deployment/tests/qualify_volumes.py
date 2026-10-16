#!/usr/bin/env python3
"""Private synthetic volume proof. No configurable daemon or real Docker writes."""
from contextlib import contextmanager
import base64
import copy
import json
from pathlib import Path
import socket
import socketserver
import sys
import tempfile
import threading
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dev
import networks
import startup
import volumes

CONTROLS = ['positive', 'existing', 'racing-owned', 'foreign', 'racing-foreign',
            'unsafe-options', 'cluster', 'changed', 'lost-response', 'old-daemon',
            'malformed', 'oversized', 'slow', 'daemon-error', 'missing-preparation', 'use-running', 'use-stopped', 'use-same-owner',
            'use-object', 'use-null', 'use-scalar', 'use-error', 'use-oversized',
            'use-truncated', 'use-eof', 'use-malformed']
EXPECTED = {name: 'volume_not_run_owned' for name in ['foreign', 'racing-foreign', 'unsafe-options', 'cluster']}
EXPECTED.update({'changed': 'volume_changed', 'lost-response': 'docker_response_invalid',
                 'old-daemon': 'docker_28_required', 'malformed': 'docker_response_invalid',
                 'oversized': 'docker_response_invalid', 'slow': 'docker_timeout',
                 'daemon-error': 'volume_inspection_failed', 'missing-preparation': 'prepared_run_required'})
EXPECTED.update({name: 'volume_in_use' for name in ['use-running', 'use-stopped', 'use-same-owner']})
EXPECTED.update({name: 'docker_response_invalid' for name in
                 ['use-object', 'use-null', 'use-scalar', 'use-oversized', 'use-truncated', 'use-eof', 'use-malformed']})
EXPECTED['use-error'] = 'volume_use_failed'
API_PREFIX = '/v1.48/volumes/'


def expected_request(target, run_id):
    """Independent literal Docker volume create oracle."""
    token = base64.urlsafe_b64encode(uuid.UUID(run_id).bytes).decode().rstrip('=')
    project = target['project_id_prefix'] + '-' + token
    return {'Name': 'supabase_db_' + project, 'Driver': 'local', 'DriverOpts': {},
            'Labels': {'io.agriplatform.env.owner': 'platform/deployment',
                       'io.agriplatform.env.target': target['target_id'],
                       'io.agriplatform.env.run': run_id,
                       'io.agriplatform.env.project': project,
                       'com.supabase.cli.project': project,
                       'com.docker.compose.project': project}}


def expected_use_path(name):
    # Independent literal URL oracle; never call the production route/helper.
    return '/v1.48/containers/json?all=true&filters=%7B%22volume%22%3A%5B%22' + name + '%22%5D%7D'


class SyntheticDaemon:
    def __init__(self, target, run_id, control='positive'):
        self.target, self.run_id, self.control = target, run_id, control
        request = expected_request(target, run_id)
        self.name = request['Name']
        self.volume = {key: value for key, value in request.items() if key != 'DriverOpts'}
        self.volume.update(Scope='local', Options=None, CreatedAt='2026-10-15T00:00:00Z',
                           Mountpoint='/private-sensitive-marker')
        self.present = control not in ['positive', 'racing-owned', 'racing-foreign', 'lost-response']
        self.events, self.errors, self.inspect_count = [], [], 0
        self.hook = None
        self.connections = 0
        self.disconnect_at = self.disconnect_after = self.truncated_at = None
        self.disconnected = threading.Event()
        if control == 'use-truncated':
            self.truncated_at = 4
        if control == 'use-eof':
            self.disconnect_at = 4
        if control == 'foreign':
            self.volume['Labels']['io.agriplatform.env.owner'] = 'foreign'
        if control == 'unsafe-options':
            self.volume['Options'] = {'device': '/private'}
        if control == 'cluster':
            self.volume['ClusterVolume'] = {}

    def dispatch(self, method, path, body):
        self.events.append((method, path, body))
        if self.hook:
            self.hook(method, path)
        if (method, path) == ('GET', '/version'):
            return 200, {'Version': '27.9.9' if self.control == 'old-daemon' else '28.0.0', 'Os': 'linux'}
        if (method, path, body) == ('GET', expected_use_path(self.name), None):
            if self.control in ['use-running', 'use-stopped', 'use-same-owner']:
                return 200, [{'Id': 'sensitive-container-marker',
                              'State': 'exited' if self.control == 'use-stopped' else 'running',
                              'Labels': self.volume['Labels'] if self.control == 'use-same-owner' else {}}]
            if self.control == 'use-error':
                return 500, {'message': 'sensitive-container-marker'}
            if self.control == 'use-object':
                return 200, {}
            if self.control == 'use-null':
                return 200, None
            if self.control == 'use-scalar':
                return 200, 'sensitive-container-marker'
            return 200, []
        if (method, path) == ('POST', API_PREFIX + 'create'):
            if body != expected_request(self.target, self.run_id):
                self.errors.append('create_input_mismatch')
                return 500, {}
            # Docker returns 201 for an existing winner, without changing it.
            if self.control == 'racing-foreign':
                self.volume['Labels']['io.agriplatform.env.owner'] = 'foreign'
            if self.control == 'racing-owned':
                self.volume['CreatedAt'] = '2026-10-14T00:00:00Z'
            self.present = True
            return 201, copy.deepcopy(self.volume)
        if (method, path) == ('GET', API_PREFIX + self.name):
            self.inspect_count += 1
            if self.control == 'daemon-error':
                return 500, {'message': 'sensitive-marker'}
            if not self.present:
                return 404, {}
            result = copy.deepcopy(self.volume)
            if self.control == 'changed' and self.inspect_count > 1:
                result['CreatedAt'] = '2026-10-15T00:00:01Z'
            return 200, result
        self.errors.append('unauthorized_operation')
        return 500, {}

    def validate_events(self):
        if self.connections != 1:
            dev.refuse("docker", "synthetic_connection_mismatch")
        version = ('GET', '/version', None)
        inspect = ('GET', API_PREFIX + self.name, None)
        create = ('POST', API_PREFIX + 'create', expected_request(self.target, self.run_id))
        if self.control == 'old-daemon':
            expected = [version]
        elif self.control in ['positive', 'racing-owned']:
            expected = [version, inspect, create, inspect, ('GET', expected_use_path(self.name), None)]
        elif self.control == 'existing' or self.control.startswith('use-'):
            expected = [version, inspect, inspect, ('GET', expected_use_path(self.name), None)]
        elif self.control == 'changed':
            expected = [version, inspect, inspect]
        elif self.control in ['lost-response', 'racing-foreign']:
            expected = [version, inspect, create]
        else:
            expected = [version, inspect]
        if self.errors or self.events != expected:
            volumes.fail('synthetic_event_mismatch')

    @contextmanager
    def serve(self):
        daemon = self
        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                try:
                    self.request.settimeout(1)
                    daemon.connections += 1
                    while True:
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
                        if len(daemon.events) == daemon.disconnect_at:
                            return
                        if method == 'POST' and daemon.control == 'lost-response':
                            return
                        if '/volumes/' in path:
                            if daemon.control == 'malformed':
                                self.request.sendall(b'not-http-sensitive-marker')
                                return
                            if daemon.control == 'oversized':
                                self.request.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 999999\r\n\r\n')
                                return
                            if daemon.control == 'slow':
                                daemon.stop.wait(volumes.SECONDS + .2)
                                return
                        if path.startswith('/v1.48/containers/json?') and daemon.control == 'use-malformed':
                            self.request.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 1\r\n\r\n[')
                            return
                        if path.startswith('/v1.48/containers/json?') and daemon.control == 'use-oversized':
                            self.request.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 999999\r\n\r\n')
                            return
                        raw = json.dumps(response).encode()
                        wire = (f'HTTP/1.1 {status} Result\r\nContent-Length: {len(raw)}\r\n\r\n'.encode() + raw)
                        if len(daemon.events) == daemon.truncated_at:
                            self.request.sendall(wire[:-1])
                            return
                        self.request.sendall(wire)
                        if len(daemon.events) == daemon.disconnect_after:
                            self.request.shutdown(socket.SHUT_WR)
                            daemon.disconnected.set()
                            return
                except (OSError, ValueError, dev.Refusal):
                    # Keep uncontrolled response/request content out of diagnostics.
                    daemon.errors.append('synthetic_transport_error')
        with tempfile.TemporaryDirectory(prefix='env-volume-socket-') as temporary:
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
    with daemon.serve() as endpoint:
        try:
            result = volumes.acquire(path, args.run_id, _socket_path=endpoint)
        except dev.Refusal as error:
            if args.control in EXPECTED and EXPECTED[args.control] != error.code:
                volumes.fail('synthetic_outcome_mismatch')
            if args.control == 'missing-preparation':
                if daemon.events:
                    volumes.fail('synthetic_event_mismatch')
            else:
                daemon.validate_events()
            raise
    if args.control not in ['positive', 'existing', 'racing-owned']:
        volumes.fail('negative_control_failed')
    daemon.validate_events()
    fixture = {'network': startup.fixture_network(target, args.run_id),
               'project': dev.project_identity(target, args.run_id), 'target_id': target['target_id'],
               'run_id': args.run_id, 'volume': result['volume']}
    status, output, _ = startup.fixture_command('docker', ['volume', 'inspect', daemon.name], fixture, [])
    if status != 0 or json.loads(output) != [result['volume']]:
        volumes.fail('synthetic_handoff_mismatch')
    return {'ok': True, 'stage': 'volume', 'code': 'volume_synthetic_qualified',
            'control': args.control, **result,
            'volume': {key: value for key, value in result['volume'].items() if key != 'CreatedAt'},
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
        result = {'ok': False, 'runtime_ready': False, 'stage': 'volume', 'code': 'volume_proof_refused'}
    print(json.dumps(result, sort_keys=True))
    return 2


if __name__ == '__main__':
    sys.exit(main())
