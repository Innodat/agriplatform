#!/usr/bin/env python3
"""Private Unix daemon image proof; no real Docker dispatch or writes."""
from contextlib import contextmanager
import copy
import json
from pathlib import Path
import socket
import socketserver
import sys
import tempfile
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dev
import daemon_images
import startup

CONTROLS = ['positive', 'index-only', 'missing', 'wrong-id', 'wrong-platform', 'variant',
            'replacement', 'old-daemon', 'malformed', 'oversized', 'slow', 'daemon-error']
EXPECTED = {'missing': 'image_missing', 'wrong-id': 'image_identity_mismatch',
            'wrong-platform': 'image_identity_mismatch', 'variant': 'image_identity_mismatch',
            'replacement': 'image_identity_mismatch', 'old-daemon': 'docker_28_required',
            'malformed': 'docker_response_invalid', 'oversized': 'docker_response_invalid',
            'slow': 'docker_timeout', 'daemon-error': 'image_inspection_failed'}


def expected_images(run_id):
    # Independent oracle reads retained child bytes, never the production plan/map.
    root = dev.ROOT / 'platform/deployment/.local/kdg-base-images' / run_id
    result = {}
    for name in ['postgres', 'kong', 'gotrue', 'postgrest']:
        raw = dev.read(root / (name + '-linux-amd64.json'))
        result['public.ecr.aws/supabase/' + name + '@sha256:' + dev.digest(raw)] = {
            'Id': dev.decode(raw)['config']['digest'], 'Os': 'linux', 'Architecture': 'amd64'}
    return result


class SyntheticDaemon:
    def __init__(self, observations, control='positive'):
        self.observations, self.control = copy.deepcopy(observations), control
        self.events, self.errors, self.hook = [], [], None
        self.connections = 0
        self.disconnect_at = self.disconnect_after = self.truncated_at = None
        self.disconnected = threading.Event()
        self.routes = {}
        for child, descriptor in self.observations.items():
            self.routes['/v1.48/images/' + child + '/json'] = descriptor
            self.routes['/v1.48/images/' + descriptor['Id'] + '/json'] = descriptor

    def dispatch(self, method, path, body):
        self.events.append((method, path, body))
        if self.hook:
            self.hook(method, path)
        if method == 'GET' and body is None and path == '/version':
            return 200, {'Os': 'linux', 'Version': '27.0.0' if self.control == 'old-daemon' else '28.0.0'}
        if method != 'GET' or body is not None or path not in self.routes:
            self.errors.append('unauthorized_operation')
            return 500, {}
        if self.control in ['missing', 'daemon-error']:
            return (404 if self.control == 'missing' else 500), {'message': 'sensitive-marker'}
        result = dict(self.routes[path], Config={'Env': ['sensitive-marker']}, Created='sensitive-marker')
        if self.control == 'index-only':
            result['RepoDigests'] = ['public.ecr.aws/supabase/postgres@sha256:' + 'e' * 64]
            result['RepoTags'] = ['untrusted:latest']
        if self.control == 'wrong-id' or self.control == 'replacement' and len(self.events) > 5:
            result['Id'] = 'sha256:' + 'f' * 64
        if self.control == 'wrong-platform':
            result['Architecture'] = 'arm64'
        if self.control == 'variant':
            result['Variant'] = 'v8'
        return 200, result

    def validate_events(self):
        if self.connections != 1:
            dev.refuse("docker", "synthetic_connection_mismatch")
        expected = [('GET', '/version', None)]
        expected += [('GET', '/v1.48/images/' + child + '/json', None) for child in self.observations]
        expected += [('GET', '/v1.48/images/' + value['Id'] + '/json', None) for value in self.observations.values()]
        count = 9 if self.control in ['positive', 'index-only'] else 6 if self.control == 'replacement' else 1 if self.control == 'old-daemon' else 2
        if self.errors or self.events != expected[:count]:
            daemon_images.fail('synthetic_event_mismatch')

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
                        if '/images/' in path:
                            if daemon.control == 'malformed':
                                self.request.sendall(b'not-http-sensitive-marker')
                                return
                            if daemon.control == 'oversized':
                                self.request.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 999999\r\n\r\n')
                                return
                            if daemon.control == 'slow':
                                daemon.stop.wait(daemon_images.SECONDS + .2)
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
        with tempfile.TemporaryDirectory(prefix='env-image-socket-') as temporary:
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
    # Repeat qualification before reading oracle bytes; absent evidence is never collected.
    startup.existing_images(args)
    expected = expected_images(args.run_id)
    daemon = SyntheticDaemon(expected, args.control)
    with daemon.serve() as endpoint:
        try:
            observed = daemon_images.acquire(args.target, args.run_id, _socket_path=endpoint)
        except dev.Refusal as error:
            if EXPECTED.get(args.control) != error.code:
                raise
            daemon.validate_events()
            raise
    daemon.validate_events()
    if observed != expected or args.control not in ['positive', 'index-only']:
        daemon_images.fail('synthetic_handoff_mismatch')
    return {'ok': True, 'stage': 'daemon_images', 'code': 'daemon_images_synthetic_qualified',
            'runtime_ready': False, 'control': args.control, 'observations': observed,
            'api_events': [{'method': method, 'path': path} for method, path, _ in daemon.events]}


def main(argv=None):
    try:
        parser = dev.Parser(add_help=False, allow_abbrev=False)
        parser.add_argument('--target', required=True)
        parser.add_argument('--run-id', required=True)
        parser.add_argument('--control', choices=CONTROLS, default='positive')
        print(json.dumps(qualify(parser.parse_args(argv)), sort_keys=True))
        return 0
    except dev.Refusal as error:
        result = {'ok': False, 'runtime_ready': False, 'stage': error.stage, 'code': error.code}
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        result = {'ok': False, 'runtime_ready': False, 'stage': 'daemon_images', 'code': 'image_proof_refused'}
    print(json.dumps(result, sort_keys=True))
    return 2


if __name__ == '__main__':
    sys.exit(main())
