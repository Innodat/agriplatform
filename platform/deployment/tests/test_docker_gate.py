"""ENV startup prerequisite: synthetic Unix API, no Docker mutations or downloads."""
from contextlib import redirect_stdout
import io
import json
import os
import socket
import sys
import unittest
from unittest.mock import patch

import test_dev

ROOT = test_dev.ROOT

sys.path.insert(0, str(ROOT / 'platform/deployment'))
import dev


class StartupAcceptance(unittest.TestCase):
    setUp = test_dev.PreparationAcceptance.setUp
    invoke = test_dev.PreparationAcceptance.invoke
    refused = test_dev.PreparationAcceptance.refused
    def test_public_up_requires_existing_preparation_without_creating_it(self):
        self.refused(self.invoke('up'), 'preparation', 'prepared_run_required')
        self.assertFalse(self.run.exists())

    def test_valid_preparation_inspects_only_local_version_and_still_refuses_start(self):
        self.assertEqual(self.invoke().returncode, 0)
        before = (self.run / 'inventory.json').read_bytes()
        transport = ScriptedSocket(version_response('28.0.0'))
        with patch.object(dev, 'ROOT', self.root), patch.object(dev.socket, 'socket', return_value=transport), patch.object(dev, 'free_ports'):
            output = io.StringIO()
            with redirect_stdout(output):
                result = dev.main(['up', '--target', str(self.input), '--run-id', self.run_id])
        self.assertEqual(result, 2)
        self.assertEqual(json.loads(output.getvalue())['code'], 'runtime_adapter_unqualified')
        self.assertEqual(transport.address, '/var/run/docker.sock')
        self.assertEqual(transport.request, b'GET /version HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        self.assertEqual((self.run / 'inventory.json').read_bytes(), before)
        self.assertEqual(set(p.name for p in self.run.iterdir()), {'inventory.json', 'supabase'})

    def test_tampered_preparation_refuses_before_daemon_contact(self):
        self.assertEqual(self.invoke().returncode, 0)
        path = self.run / 'inventory.json'
        record = json.loads(path.read_bytes())
        record['identities']['project'] = 'foreign'
        path.write_text(json.dumps(record))
        with patch.object(dev, 'ROOT', self.root), patch.object(dev.socket, 'socket') as connect:
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(dev.main(['up', '--target', str(self.input), '--run-id', self.run_id]), 2)
        self.assertEqual(json.loads(output.getvalue())['code'], 'prepared_input_changed')
        connect.assert_not_called()

    def test_preparation_source_mode_and_symlink_adversaries_refuse_read_only(self):
        self.assertEqual(self.invoke().returncode, 0)
        path = self.run / 'inventory.json'
        original = path.read_bytes()
        outside = self.root / 'outside'
        outside.write_bytes(original)
        scenarios = ['source', 'boolean', 'file_mode', 'run_mode', 'symlink', 'extra', 'local_mode', 'kdg_mode']
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                source = self.root / test_dev.FILES[-1]
                source_before = source.read_bytes()
                if scenario == 'source':
                    source.write_bytes(source_before + b'\n')
                elif scenario == 'boolean':
                    value = json.loads(original)
                    value['schema_version'] = True
                    path.write_text(json.dumps(value))
                elif scenario == 'file_mode':
                    path.chmod(0o644)
                elif scenario == 'run_mode':
                    self.run.chmod(0o755)
                elif scenario in ['local_mode', 'kdg_mode']:
                    ancestor = self.run.parent.parent if scenario == 'local_mode' else self.run.parent
                    ancestor.chmod(0o777)
                elif scenario == 'symlink':
                    path.unlink()
                    path.symlink_to(outside)
                else:
                    (self.run / 'unexpected').write_text('sensitive-marker')
                with patch.object(dev, 'ROOT', self.root), patch.object(dev, 'docker_prerequisite') as probe:
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(dev.main(['up', '--target', str(self.input), '--run-id', self.run_id]), 2)
                    probe.assert_not_called()
                self.assertEqual(outside.read_bytes(), original)
                source.write_bytes(source_before)
                self.run.chmod(0o700)
                self.run.parent.chmod(0o700)
                self.run.parent.parent.chmod(0o700)
                if path.is_symlink():
                    path.unlink()
                path.write_bytes(original)
                path.chmod(0o600)
                (self.run / 'unexpected').unlink(missing_ok=True)

    def test_occupied_port_prevents_daemon_probe(self):
        self.assertEqual(self.invoke().returncode, 0)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.bind(('127.0.0.1', 5188))
            with patch.object(dev, 'ROOT', self.root), patch.object(dev, 'docker_prerequisite') as probe:
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(dev.main(['up', '--target', str(self.input), '--run-id', self.run_id]), 2)
                self.assertEqual(json.loads(output.getvalue())['code'], 'port_unavailable')
                probe.assert_not_called()

    def test_daemon_failure_output_is_safe_json(self):
        self.assertEqual(self.invoke().returncode, 0)
        for error in [PermissionError('sensitive-marker'), TimeoutError('sensitive-marker')]:
            with patch.object(dev, 'ROOT', self.root), patch.object(dev, 'free_ports'), patch.object(dev.socket, 'socket', side_effect=error):
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(dev.main(['up', '--target', str(self.input), '--run-id', self.run_id]), 2)
                record = json.loads(output.getvalue())
                self.assertEqual(record['stage'], 'docker')
                self.assertFalse(record['runtime_ready'])
                self.assertNotIn('sensitive-marker', output.getvalue())

    def test_nested_json_is_reported_as_daemon_response_failure(self):
        self.assertEqual(self.invoke().returncode, 0)
        body = b'[' * 10000 + b'0' + b']' * 10000
        response = b'HTTP/1.1 200 OK\r\nContent-Length: ' + str(len(body)).encode() + b'\r\n\r\n' + body
        with patch.object(dev, 'ROOT', self.root), patch.object(dev, 'free_ports'), patch.object(dev.socket, 'socket', return_value=ScriptedSocket(response)):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(dev.main(['up', '--target', str(self.input), '--run-id', self.run_id]), 2)
            record = json.loads(output.getvalue())
            self.assertEqual((record['stage'], record['code']), ('docker', 'docker_response_invalid'))


def version_response(version, ostype='linux', **extra):
    body = json.dumps({'Version': version, 'Os': ostype, **extra}).encode()
    return b'HTTP/1.1 200 OK\r\nContent-Length: ' + str(len(body)).encode() + b'\r\n\r\n' + body


class ScriptedSocket:
    def __init__(self, response):
        self.response = response
        self.address = self.request = None
        self.timeouts = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def close(self):
        pass

    def settimeout(self, value):
        self.timeouts.append(value)

    def connect(self, address):
        self.address = address

    def sendall(self, request):
        self.request = request

    def recv(self, size):
        result, self.response = self.response[:size], self.response[size:]
        return result


class DockerProtocol(unittest.TestCase):
    def inspect(self, response):
        transport = ScriptedSocket(response)
        with patch.object(dev.socket, 'socket', return_value=transport):
            return dev.docker_prerequisite()

    def test_old_and_prerelease_or_nonlinux_daemons_refuse(self):
        for version, osname, code in [('27.9.9', 'linux', 'docker_28_required'),
                                      ('28.0.0-rc.1', 'linux', 'docker_response_invalid'),
                                      ('28.0.0', 'windows', 'docker_response_invalid'),
                                      (True, 'linux', 'docker_response_invalid'),
                                      ('garbage-sensitive-marker', 'linux', 'docker_response_invalid')]:
            with self.subTest(version=version), self.assertRaises(dev.Refusal) as result:
                self.inspect(version_response(version, osname))
            self.assertEqual(result.exception.code, code)

    def test_stable_current_or_future_major_passes_only_prerequisite(self):
        for version in ['28.0.0', '28.1.2', '29.0.0']:
            self.assertEqual(self.inspect(version_response(version)), version)

    def test_malformed_oversized_truncated_and_error_responses_refuse(self):
        samples = [b'', b'sensitive-marker', b'HTTP/1.1 500 Error\r\nContent-Length: 0\r\n\r\n',
                   b'HTTP/1.1 200 OK\r\nContent-Length: 999999\r\n\r\n',
                   b'HTTP/1.1 200 OK\r\nContent-Length: 100\r\n\r\n{}',
                   b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\n',
                   b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\nContent-Length: 2\r\n\r\n{}',
                   b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\n[]',
                   b'HTTP/1.1 200 OK\r\nX: ' + b'x' * 65536]
        for response in samples:
            with self.subTest(length=len(response)), self.assertRaises(dev.Refusal):
                self.inspect(response)

    def test_unavailable_and_timeout_are_safe_refusals(self):
        for error, code in [(PermissionError('sensitive-marker'), 'docker_unavailable'),
                            (FileNotFoundError(), 'docker_unavailable'),
                            (TimeoutError(), 'docker_timeout')]:
            with patch.object(dev.socket, 'socket', side_effect=error), self.assertRaises(dev.Refusal) as result:
                dev.docker_prerequisite()
            self.assertEqual(result.exception.code, code)

    def test_malformed_header_control_characters_refuse(self):
        for value in [b'bad\x00value', b'bad\nheader', b'bad\x7fvalue', b'bad\rvalue']:
            response = version_response('28.0.0').replace(b'Content-Length:', b'X-Test: ' + value + b'\r\nContent-Length:')
            with self.subTest(value=value):
                with self.assertRaises(dev.Refusal) as result:
                    self.inspect(response)
                self.assertEqual(result.exception.code, 'docker_response_invalid')

    def test_fragmented_success_and_exact_response_cap(self):
        response = version_response('28.0.0')
        for width in [1, 2, 7, 31]:
            transport = ScriptedSocket(response)
            receive = transport.recv
            transport.recv = lambda size, width=width: receive(min(size, width))
            with patch.object(dev.socket, 'socket', return_value=transport):
                self.assertEqual(dev.docker_prerequisite(), '28.0.0')
        body = b'{"Version":"28.0.0","Os":"linux","padding":""}'
        # A five-digit Content-Length keeps header size stable around the cap.
        header_size = len(b'HTTP/1.1 200 OK\r\nContent-Length: 00000\r\n\r\n')
        for total in [65536, 65537]:
            padded = body[:-2] + b'x' * (total - header_size - len(body)) + body[-2:]
            response = b'HTTP/1.1 200 OK\r\nContent-Length: ' + str(len(padded)).encode() + b'\r\n\r\n' + padded
            self.assertEqual(len(response), total)
            if total == 65536:
                self.assertEqual(self.inspect(response), '28.0.0')
            else:
                with self.assertRaises(dev.Refusal):
                    self.inspect(response)

    def test_slow_progress_uses_one_deadline_and_shrinking_timeouts(self):
        current = [0.0]
        transport = ScriptedSocket(version_response('28.0.0'))
        receive = transport.recv
        def drip(size):
            current[0] += 0.9
            return receive(1)
        transport.recv = drip
        with patch.object(dev.socket, 'socket', return_value=transport), patch.object(dev.time, 'monotonic', side_effect=lambda: current[0]), self.assertRaises(dev.Refusal) as result:
            dev.docker_prerequisite()
        self.assertEqual(result.exception.code, 'docker_timeout')
        self.assertGreater(current[0], 5)
        self.assertLess(current[0], 6)
        self.assertEqual(transport.timeouts, sorted(transport.timeouts, reverse=True))
        self.assertLess(transport.timeouts[-1], 1)
        for operation in ['connect', 'sendall', 'recv']:
            transport = ScriptedSocket(version_response('28.0.0'))
            with patch.object(transport, operation, side_effect=TimeoutError('sensitive-marker')), patch.object(dev.socket, 'socket', return_value=transport), self.assertRaises(dev.Refusal) as result:
                dev.docker_prerequisite()
            self.assertEqual(result.exception.code, 'docker_timeout')

    def test_total_deadline_and_environment_override(self):
        transport = ScriptedSocket(version_response('28.0.0'))
        with patch.dict(os.environ, {'DOCKER_HOST': 'tcp://sensitive-marker:2375', 'DOCKER_CONTEXT': 'production'}), patch.object(dev.socket, 'socket', return_value=transport):
            self.assertEqual(dev.docker_prerequisite(), '28.0.0')
        self.assertEqual(transport.address, '/var/run/docker.sock')
        with patch.object(dev.socket, 'socket', return_value=ScriptedSocket(b'')), patch.object(dev.time, 'monotonic', side_effect=[0, 0, 0, 6]), self.assertRaises(dev.Refusal) as result:
            dev.docker_prerequisite()
        self.assertEqual(result.exception.code, 'docker_timeout')


if __name__ == '__main__':
    unittest.main()
