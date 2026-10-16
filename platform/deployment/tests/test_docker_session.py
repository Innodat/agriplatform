"""Connection continuity and fail-closed framing, using private Unix sockets only."""
from contextlib import contextmanager
import json
from pathlib import Path
import socket
import socketserver
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import test_docker_gate
import dev


def response(body=None, status=200, headers=b'', protocol=b'HTTP/1.1'):
    raw = json.dumps(body if body is not None else {}).encode()
    return protocol + b' ' + str(status).encode() + b' Result\r\nContent-Length: ' + str(len(raw)).encode() + b'\r\n' + headers + b'\r\n' + raw


class Peer:
    def __init__(self, replies):
        self.replies = replies
        self.connections = 0
        self.requests = []
        self.closed = threading.Event()
        self.hook = None

    @contextmanager
    def serve(self):
        peer = self
        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                peer.connections += 1
                self.request.settimeout(1)
                try:
                    while True:
                        data = b''
                        while b'\r\n\r\n' not in data:
                            chunk = self.request.recv(4096)
                            if not chunk:
                                return
                            data += chunk
                        header, body = data.split(b'\r\n\r\n', 1)
                        fields = dict(line.lower().split(b':', 1) for line in header.split(b'\r\n')[1:])
                        length = int(fields.get(b'content-length', b'0'))
                        while len(body) < length:
                            chunk = self.request.recv(4096)
                            if not chunk:
                                return
                            body += chunk
                        peer.requests.append(header.split(b'\r\n')[0])
                        if peer.hook:
                            if peer.hook(self.request, len(peer.requests)):
                                continue
                        reply = peer.replies[len(peer.requests) - 1]
                        if reply is None:
                            return
                        self.request.sendall(reply)
                except OSError:
                    pass
                finally:
                    peer.closed.set()
        with tempfile.TemporaryDirectory(prefix='env-session-') as temp:
            self.path = str(Path(temp) / 'daemon.sock')
            with socketserver.UnixStreamServer(self.path, Handler) as server:
                worker = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': .01}, daemon=True)
                worker.start()
                try:
                    yield self.path
                finally:
                    server.shutdown()
                    worker.join(2)


class DockerSessionTests(unittest.TestCase):
    def test_partial_request_body_eof_releases_peer_promptly(self):
        peer = Peer([])
        with peer.serve() as endpoint:
            with socket.socket(socket.AF_UNIX) as client:
                client.connect(endpoint)
                client.sendall(b'POST /v1.48/volumes/create HTTP/1.1\r\nContent-Length: 9\r\n\r\n{}')
                client.shutdown(socket.SHUT_WR)
                self.assertTrue(peer.closed.wait(.5))
        self.assertEqual(peer.requests, [])

    def test_high_descriptor_supports_idle_observation(self):
        import fcntl
        left, right = socket.socketpair()
        self.addCleanup(left.close)
        self.addCleanup(right.close)
        high = socket.socket(fileno=fcntl.fcntl(left.fileno(), fcntl.F_DUPFD_CLOEXEC, 2048))
        self.addCleanup(high.close)
        session = dev.DockerSession()
        session.stream = high
        session.idle()
        right.sendall(b'extra')
        with self.assertRaises(dev.Refusal) as caught:
            session.idle()
        self.assertEqual(caught.exception.code, 'docker_response_invalid')

    def test_decode_processing_cannot_exceed_total_deadline(self):
        current = [0.0]
        transport = test_docker_gate.ScriptedSocket(response())
        def decode(raw):
            current[0] = 2.0
            return {}
        with patch.object(dev.socket, 'socket', return_value=transport), \
                patch.object(dev.time, 'monotonic', side_effect=lambda: current[0]), \
                patch.object(dev, 'decode', side_effect=decode):
            with self.assertRaises(dev.Refusal) as caught:
                dev.docker_exchange('GET', '/version', deadline=1)
        self.assertEqual(caught.exception.code, 'docker_timeout')

    def test_final_idle_processing_cannot_exceed_total_deadline(self):
        current = [0.0]
        transport = test_docker_gate.ScriptedSocket(response())
        def idle(session):
            current[0] = 2.0
        with patch.object(dev.socket, 'socket', return_value=transport), \
                patch.object(dev.time, 'monotonic', side_effect=lambda: current[0]), \
                patch.object(dev.DockerSession, 'idle', idle):
            with dev.DockerSession(deadline=1) as session, self.assertRaises(dev.Refusal) as caught:
                session.exchange('GET', '/version')
        self.assertEqual(caught.exception.code, 'docker_timeout')

    def test_final_observable_trailing_bytes_and_eof_refuse(self):
        for ending in ['bytes', 'eof']:
            peer = Peer([response()])
            ready = threading.Event()
            def finish(stream, count):
                stream.sendall(response())
                if ending == 'bytes':
                    stream.sendall(b'extra')
                else:
                    stream.shutdown(socket.SHUT_WR)
                ready.set()
                return True
            peer.hook = finish
            original_idle = dev.DockerSession.idle
            def synchronized_idle(session):
                self.assertTrue(ready.wait(1))
                return original_idle(session)
            with peer.serve() as endpoint, patch.object(dev.DockerSession, 'idle', synchronized_idle):
                with dev.DockerSession(_socket_path=endpoint) as session, self.assertRaises(dev.Refusal) as caught:
                    session.exchange('GET', '/version')
                self.assertEqual(caught.exception.code, 'docker_response_invalid')
            self.assertEqual(peer.connections, 1)
            self.assertEqual(len(peer.requests), 1)

    def test_sequential_requests_share_one_connection_and_release_descriptor(self):
        peer = Peer([test_docker_gate.version_response('28.0.0'), response()])
        with peer.serve() as endpoint:
            with dev.DockerSession(_socket_path=endpoint) as session:
                self.assertEqual(dev.docker_prerequisite(_session=session), '28.0.0')
                descriptor = session.stream
                self.assertEqual(session.exchange('GET', '/v1.48/volumes/owned'), (200, {}))
            self.assertEqual(descriptor.fileno(), -1)
            self.assertTrue(peer.closed.wait(1))
            with self.assertRaises(dev.Refusal):
                session.exchange('GET', '/version')
        self.assertEqual(peer.connections, 1)
        self.assertEqual(len(peer.requests), 2)

    def test_bad_second_response_poisoning_cannot_send_or_reconnect(self):
        samples = [b'bad\r\n\r\n',
                   b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\nContent-Length: 2\r\n\r\n{}',
                   b'HTTP/1.1 200 OK\r\nContent-Length: 999999\r\n\r\n',
                   response() + b'extra', response(headers=b'Connection: keep-alive, CLOSE\r\n'),
                   response(protocol=b'HTTP/1.0'), response(headers=b'Transfer-Encoding: chunked\r\n'),
                   response(headers=b'Content-Encoding: gzip\r\n'), response([]),
                   response(headers=b'X: bad\x00value\r\n')]
        for wire in samples:
            with self.subTest(wire=wire[:70]):
                peer = Peer([response(), wire])
                with peer.serve() as endpoint, dev.DockerSession(_socket_path=endpoint) as session:
                    session.exchange('GET', '/version')
                    descriptor = session.stream
                    with self.assertRaises(dev.Refusal) as caught:
                        session.exchange('GET', '/v1.48/volumes/owned')
                    self.assertEqual(caught.exception.code, 'docker_response_invalid')
                    self.assertEqual(descriptor.fileno(), -1)
                    with self.assertRaises(dev.Refusal):
                        session.exchange('GET', '/version')
                self.assertEqual(peer.connections, 1)
                self.assertEqual(len(peer.requests), 2)

    def test_truncated_second_response_refuses_on_eof(self):
        peer = Peer([response(), None])
        def truncate(stream, count):
            if count == 2:
                stream.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 9\r\n\r\n{}')
        peer.hook = truncate
        with peer.serve() as endpoint, dev.DockerSession(_socket_path=endpoint) as session:
            session.exchange('GET', '/version')
            with self.assertRaises(dev.Refusal) as caught:
                session.exchange('GET', '/v1.48/volumes/owned')
        self.assertEqual(caught.exception.code, 'docker_response_invalid')
        self.assertEqual(peer.connections, 1)
        self.assertEqual(len(peer.requests), 2)

    def test_slow_trickle_cannot_reset_total_deadline(self):
        peer = Peer([response()])
        def trickle(stream, count):
            for byte in response():
                stream.sendall(bytes([byte]))
                time.sleep(.02)
            return True
        peer.hook = trickle
        started = time.monotonic()
        with peer.serve() as endpoint, dev.DockerSession(_socket_path=endpoint, deadline=started + .1) as session:
            with self.assertRaises(dev.Refusal) as caught:
                session.exchange('GET', '/version')
        self.assertEqual(caught.exception.code, 'docker_timeout')
        self.assertLess(time.monotonic() - started, .5)
        self.assertEqual(peer.connections, 1)

    def test_disconnect_before_or_after_mutation_never_replays(self):
        for at in [1, 2, 3]:
            peer = Peer([response(), response(status=201), response()])
            peer.replies[at - 1] = None
            with peer.serve() as endpoint, dev.DockerSession(_socket_path=endpoint) as session:
                with self.assertRaises(dev.Refusal):
                    session.exchange('GET', '/version')
                    session.exchange('POST', '/v1.48/volumes/create', {})
                    session.exchange('GET', '/v1.48/volumes/owned')
                with self.assertRaises(dev.Refusal):
                    session.exchange('POST', '/v1.48/volumes/create', {})
            self.assertEqual(peer.connections, 1)
            self.assertEqual(sum(request.startswith(b'POST') for request in peer.requests), int(at > 1))

    def test_socket_path_replacement_cannot_receive_subsequent_requests(self):
        peer = Peer([response(), response()])
        with peer.serve() as endpoint, socket.socket(socket.AF_UNIX) as replacement:
            with dev.DockerSession(_socket_path=endpoint) as session:
                session.exchange('GET', '/version')
                Path(endpoint).unlink()
                replacement.bind(endpoint)
                replacement.listen()
                replacement.settimeout(.03)
                session.exchange('GET', '/v1.48/volumes/owned')
                with self.assertRaises(TimeoutError):
                    replacement.accept()
        self.assertEqual(peer.connections, 1)
        self.assertEqual(len(peer.requests), 2)

    def test_total_deadline_spans_individually_fast_requests(self):
        peer = Peer([response()] * 4)
        peer.hook = lambda stream, count: time.sleep(.06)
        with peer.serve() as endpoint, dev.DockerSession(_socket_path=endpoint, deadline=time.monotonic() + .1) as session:
            session.exchange('GET', '/version')
            with self.assertRaises(dev.Refusal) as result:
                session.exchange('GET', '/v1.48/volumes/owned')
        self.assertEqual(result.exception.code, 'docker_timeout')
        self.assertEqual(peer.connections, 1)

    def test_callback_exception_and_invalid_route_close_without_additional_send(self):
        peer = Peer([response()])
        with peer.serve() as endpoint:
            with self.assertRaises(RuntimeError):
                with dev.DockerSession(_socket_path=endpoint) as session:
                    session.exchange('GET', '/version')
                    descriptor = session.stream
                    raise RuntimeError('callback')
            self.assertEqual(descriptor.fileno(), -1)
        self.assertEqual(peer.connections, 1)
        with patch.object(dev.socket, 'socket') as connect:
            with dev.DockerSession() as session, self.assertRaises(dev.Refusal):
                session.exchange('DELETE', '/containers/foreign')
            connect.assert_not_called()

    def test_late_unsolicited_bytes_are_refused_before_next_request(self):
        peer = Peer([response()])
        sent = threading.Event()
        def trailing(stream, count):
            stream.sendall(response())
            time.sleep(.03)
            stream.sendall(b'unsolicited')
            sent.set()
            return True
        peer.hook = trailing
        with peer.serve() as endpoint, dev.DockerSession(_socket_path=endpoint) as session:
            session.exchange('GET', '/version')
            self.assertTrue(sent.wait(1))
            with self.assertRaises(dev.Refusal):
                session.exchange('GET', '/v1.48/volumes/owned')
        self.assertEqual(len(peer.requests), 1)


if __name__ == '__main__':
    unittest.main()
