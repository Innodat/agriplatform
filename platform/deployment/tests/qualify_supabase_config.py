#!/usr/bin/env python3
"""Opt-in pinned CLI parser proof against a temporary read-only Docker fixture.

No real Docker access, downloaded tools, container startup or live credentials.
Supply the executable from a verified ENV toolchain; never uses PATH discovery.
"""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'platform/deployment'))
import dev


def probe(executable, target, work, valid, run_id='00000000-0000-4000-8000-000000000001'):
    (work / 'supabase').mkdir(parents=True, mode=0o700)
    (work / 'supabase/config.toml').write_bytes(
        dev.configuration(target, run_id) if valid else b'invalid = [')
    endpoint = work / 'docker.sock'
    requests, errors = [], []
    done = threading.Event()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
        server.bind(str(endpoint))
        server.listen()
        server.settimeout(0.1)

        def respond():
            try:
                while not done.is_set():
                    try:
                        connection, _ = server.accept()
                    except TimeoutError:
                        continue
                    with connection:
                        connection.settimeout(2)
                        request = b''
                        while b'\r\n\r\n' not in request and len(request) <= 8192:
                            chunk = connection.recv(4096)
                            if not chunk:
                                break
                            request += chunk
                        line = request.split(b'\r\n', 1)[0].decode()
                        requests.append(line)
                        if line in ['HEAD /_ping HTTP/1.1', 'GET /_ping HTTP/1.1']:
                            connection.sendall(b'HTTP/1.1 200 OK\r\nAPI-Version: 1.46\r\n'
                                               b'Content-Length: 0\r\nConnection: close\r\n\r\n')
                            continue
                        body = b'{"message":"synthetic missing container"}'
                        connection.sendall(b'HTTP/1.1 404 Not Found\r\nContent-Type: application/json\r\n'
                                           b'Content-Length: ' + str(len(body)).encode()
                                           + b'\r\nConnection: close\r\n\r\n' + body)
            except (OSError, ValueError):
                errors.append('fixture_protocol_error')

        thread = threading.Thread(target=respond, daemon=True)
        thread.start()
        try:
            result = subprocess.run(
                [str(executable), 'status', '--workdir', str(work), '--output', 'json', '--agent', 'no'],
                cwd=work, env={'PATH': '/usr/bin:/bin', 'SUPABASE_HOME': str(work / 'private'),
                               'DOCKER_HOST': 'unix://' + str(endpoint),
                               'SUPABASE_TELEMETRY_DISABLED': '1', 'NO_COLOR': '1'},
                capture_output=True, text=True, timeout=15)
        finally:
            done.set()
            thread.join(timeout=3)
        expected = 'GET /v1.46/containers/supabase_db_' + dev.project_identity(target, run_id) + '/json HTTP/1.1'
        permitted = {expected, 'HEAD /_ping HTTP/1.1', 'GET /_ping HTTP/1.1'}
        if valid:
            passed = (result.returncode != 0 and requests.count(expected) == 1
                      and set(requests) <= permitted and 'failed to inspect container health' in result.stderr)
        else:
            passed = result.returncode != 0 and not requests and 'CliConfigParseError' in result.stderr
        return {'fixture': work.name, 'passed': bool(passed and not errors and not thread.is_alive()),
                'request_count': len(requests), 'only_expected_reads': set(requests) <= permitted}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--supabase', type=Path, required=True)
    args = parser.parse_args()
    try:
        executable = args.supabase.absolute()
        with tempfile.TemporaryDirectory(prefix='kdg-config-') as directory:
            base = Path(directory)
            env = {'PATH': '/usr/bin:/bin', 'SUPABASE_HOME': str(base / 'private'),
                   'SUPABASE_TELEMETRY_DISABLED': '1'}
            version = subprocess.run([str(executable), '--version'], cwd=base, env=env,
                                     capture_output=True, text=True, timeout=10)
            if version.returncode or version.stdout.strip() != '2.120.0':
                raise ValueError('wrong_version')
            target = dev.decode(dev.read(ROOT / 'platform/deployment/environments/kdg-local.json'))
            dev.validate(target, dev.decode(dev.read(ROOT / dev.SCHEMA)))
            results = [probe(executable, target, base / 'valid', True),
                       probe(executable, target, base / 'valid-punctuation', True,
                             'deadbeef-ffff-4fff-bfff-0123456789ab'),
                       probe(executable, target, base / 'invalid', False)]
        passed = all(item['passed'] for item in results)
        print(json.dumps({'ok': passed, 'runtime_ready': False, 'checks': results}, sort_keys=True))
        return 0 if passed else 1
    except (OSError, ValueError, subprocess.SubprocessError, dev.Refusal):
        print(json.dumps({'ok': False, 'runtime_ready': False, 'code': 'parser_probe_failed'}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
