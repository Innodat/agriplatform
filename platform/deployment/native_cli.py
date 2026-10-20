"""Thin, explicitly selected Supabase CLI lifecycle for disposable local targets.

No historical qualifier receipts, service interception, migrations or cleanup.
"""
import fcntl
import http.client
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import tempfile
import uuid

import dev

VERSION = '2.120.0'
BINDING = 'com.docker.network.bridge.host_binding_ipv4'
LABEL_PREFIX = 'io.agriplatform.env.'
TIMEOUTS = {'version': 10, 'prepare': 10, 'up': 600, 'verify': 30, 'stop': 120, 'reset': 300}


def fail(code, stage='native'):
    dev.refuse(stage, code)


def write_private(fd, name, raw):
    descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    with os.fdopen(descriptor, 'wb') as output:
        output.write(raw)
        output.flush()
        os.fsync(output.fileno())
    os.fsync(fd)


def marker(target, raw, run_id):
    return {'schema_version': 1, 'run_id': run_id, 'target_id': target['target_id'],
            'project': dev.project_identity(target, run_id), 'target_sha256': dev.digest(raw),
            'configuration_sha256': dev.digest(dev.configuration(target, run_id))}


def check_run(path, target, raw, run_id):
    with dev.directory(path) as run:
        dev.check_private(run)
        actual = dev.decode(dev.read_at(run, 'native.json', protected=True))
        if json.dumps(actual, sort_keys=True) != json.dumps(marker(target, raw, run_id), sort_keys=True):
            fail('native_marker_changed')
        with dev.directory(path / 'supabase') as config:
            dev.check_private(config)
            if dev.read_at(config, 'config.toml', protected=True) != dev.configuration(target, run_id):
                fail('prepared_config_changed')
        for name in ['supabase-home', 'docker']:
            with dev.directory(path / name) as private:
                dev.check_private(private)
                if name == 'docker' and dev.read_at(private, 'config.json', protected=True) != b'{}\n':
                    fail('docker_config_changed')


def prepare(path, target, raw, run_id):
    # Validate existing ancestors before adding a new run; never adopt old runs.
    ancestor = dev.ROOT / 'platform/deployment'
    for name in ['.local', 'kdg']:
        ancestor /= name
        if ancestor.exists() or ancestor.is_symlink():
            with dev.directory(ancestor) as fd:
                info = os.fstat(fd)
                if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o022:
                    dev.refuse('inventory', 'unprotected_directory')
    with dev.directory(path.parent, create=True) as parent:
        dev.check_private(parent)
        try:
            os.mkdir(run_id, 0o700, dir_fd=parent)
        except FileExistsError:
            check_run(path, target, raw, run_id)
            return
        with dev.directory(path) as run:
            dev.install_configuration(run, target, run_id)
            for name in ['supabase-home', 'docker']:
                os.mkdir(name, 0o700, dir_fd=run)
            with dev.directory(path / 'docker') as docker:
                write_private(docker, 'config.json', b'{}\n')
            write_private(run, 'native.json', (json.dumps(marker(target, raw, run_id), sort_keys=True) + '\n').encode())
        os.fsync(parent)


def environment(path):
    # HOME remains the user's HOME; vendor mutable state is explicitly run-local.
    result = {'PATH': '/usr/local/bin:/usr/bin:/bin', 'LANG': 'C.UTF-8',
              'DOCKER_HOST': 'unix:///var/run/docker.sock',
              'DOCKER_CONFIG': str(path / 'docker'),
              'SUPABASE_HOME': str(path / 'supabase-home'),
              'SUPABASE_EXPERIMENTAL_STACK': '0', 'CI': 'true'}
    if 'HOME' in os.environ:
        result['HOME'] = os.environ['HOME']
    return result


def vendor(executable, arguments, path, stage, allow_failure=False):
    try:
        # Version is the only output read, and only a bounded prefix is inspected.
        with tempfile.TemporaryFile() as version_output:
            result = subprocess.run([executable, *arguments], env=environment(path), cwd=path,
                stdin=subprocess.DEVNULL, stdout=version_output if stage == 'version' else subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, timeout=TIMEOUTS[stage], check=False)
            if result.returncode:
                if allow_failure:
                    return False
                error = dev.Refusal(stage, 'vendor_failed')
                error.vendor_exit = result.returncode
                raise error
            if stage == 'version':
                version_output.seek(0)
                if version_output.read(128).strip() != VERSION.encode():
                    fail('supabase_version_required', 'version')
            return True
    except subprocess.TimeoutExpired:
        fail('vendor_timeout', stage)
    except OSError:
        fail('vendor_unavailable', stage)


def docker(arguments, path, missing=False):
    """Ordinary local Docker CLI; output is data only and never printed."""
    try:
        with tempfile.TemporaryFile() as output:
            result = subprocess.run(['docker', *arguments], env=environment(path), cwd=path,
                stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.DEVNULL,
                timeout=15, check=False)
            if result.returncode:
                if missing and result.returncode == 1:
                    return None
                fail('docker_failed', 'docker')
            output.seek(0)
            raw = output.read(dev.LIMIT + 1)
            if len(raw) > dev.LIMIT:
                fail('docker_response_invalid', 'docker')
            return raw
    except subprocess.TimeoutExpired:
        fail('docker_timeout', 'docker')
    except OSError:
        fail('docker_unavailable', 'docker')


def docker_prerequisite(path):
    value = dev.decode(docker(['version', '--format', '{{json .Server}}'], path))
    if type(value) is not dict or value.get('Os') != 'linux':
        fail('docker_response_invalid', 'docker')
    version = value.get('Version')
    if type(version) is not str or re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version) is None:
        fail('docker_response_invalid', 'docker')
    if tuple(map(int, version.split('.'))) < (28, 0, 0):
        fail('docker_28_required', 'docker')


def network(target, run_id, create, path, allow_absent=False):
    project = dev.project_identity(target, run_id)
    name = project + '-network'
    labels = {LABEL_PREFIX + 'owner': 'platform/deployment', LABEL_PREFIX + 'target': target['target_id'],
              LABEL_PREFIX + 'run': run_id, LABEL_PREFIX + 'project': project}
    inspect = ['network', 'inspect', '--format', '{{json .}}', name]
    raw = docker(inspect, path, missing=True)
    if raw is None and create:
        arguments = ['network', 'create', '--driver', 'bridge', '--opt', BINDING + '=127.0.0.1']
        for key, value in labels.items():
            arguments += ['--label', key + '=' + value]
        docker(arguments + [name], path)
        raw = docker(inspect, path)
    if raw is None:
        if allow_absent:
            return None
        fail('network_unavailable')
    value = dev.decode(raw)
    if (type(value) is not dict or value.get('Name') != name or value.get('Driver') != 'bridge'
            or type(value.get('Options')) is not dict or value['Options'].get(BINDING) != '127.0.0.1'
            or type(value.get('Labels')) is not dict
            or any(value['Labels'].get(key) != item for key, item in labels.items())):
        fail('network_not_run_owned')
    identity = value.get('Id')
    if type(identity) is not str or re.fullmatch('[0-9a-f]{64}', identity) is None:
        fail('network_id_invalid')
    return identity


def reachability(target):
    try:
        with socket.create_connection(('127.0.0.1', target['ports']['database']), timeout=5):
            pass
        connection = http.client.HTTPConnection('127.0.0.1', target['ports']['supabase_api'], timeout=5)
        try:
            connection.request('GET', '/auth/v1/health')
            response = connection.getresponse()
            if response.status != 200:
                fail('supabase_unreachable', 'verify')
        finally:
            connection.close()
    except (OSError, http.client.HTTPException):
        fail('supabase_unreachable', 'verify')


def main(argv=None):
    safe = {}
    try:
        parser = dev.Parser(add_help=False, allow_abbrev=False)
        parser.add_argument('command', choices=['prepare', 'up', 'verify', 'stop', 'reset'])
        parser.add_argument('--target', required=True)
        parser.add_argument('--run-id', required=True)
        parser.add_argument('--supabase', required=True)
        parser.add_argument('--confirm-target')
        args = parser.parse_args(argv)
        if str(uuid.UUID(args.run_id)) != args.run_id:
            fail('invalid_run_id', 'arguments')
        source = Path(args.target)
        if '..' in source.parts:
            fail('unsafe_path', 'paths')
        source = Path(os.path.abspath(source))
        raw = dev.read(source)
        target = dev.decode(raw)
        dev.validate(target, dev.decode(dev.read(dev.ROOT / dev.SCHEMA)))
        if target['workspace_root'] != str(dev.ROOT):
            fail('workspace_mismatch', 'paths')
        if args.command == 'reset' and args.confirm_target != target['target_id']:
            fail('target_confirmation_required', 'confirmation')
        if args.command != 'reset' and args.confirm_target is not None:
            fail('invalid_arguments', 'arguments')
        executable = Path(args.supabase)
        if not executable.is_absolute() or '..' in executable.parts or not executable.is_file() or not os.access(executable, os.X_OK):
            fail('explicit_executable_required', 'arguments')
        path = dev.ROOT / 'platform/deployment/.local/kdg' / args.run_id
        safe = {'run_id': args.run_id, 'project': dev.project_identity(target, args.run_id)}
        if args.command == 'prepare':
            prepare(path, target, raw, args.run_id)
        check_run(path, target, raw, args.run_id)
        with dev.directory(path) as run:
            lock = os.open('native.lock', os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=run)
            try:
                info = os.fstat(lock)
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
                    fail('unsafe_lock')
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    fail('run_busy')
                vendor(str(executable), ['--version'], path, 'version')
                if args.command != 'prepare':
                    docker_prerequisite(path)
                    if args.command == 'up':
                        network_id = network(target, args.run_id, False, path, allow_absent=True)
                        check_run(path, target, raw, args.run_id)
                        running = network_id is not None and vendor(str(executable),
                            ['--workdir', str(path), '--network-id', network_id, 'status'],
                            path, 'verify', allow_failure=True)
                        if not running:
                            with dev.free_ports(target['ports']):
                                network_id = network(target, args.run_id, True, path)
                    else:
                        network_id = network(target, args.run_id, False, path)
                    check_run(path, target, raw, args.run_id)
                    if dev.read(source) != raw:
                        fail('target_changed')
                    commands = {'up': ['start'], 'verify': ['status'],
                                'stop': ['stop', '--project-id', safe['project']],
                                'reset': ['db', 'reset', '--local', '--no-seed', '--yes']}
                    vendor(str(executable), ['--workdir', str(path), '--network-id', network_id,
                                            *commands[args.command]], path, args.command)
                    if args.command == 'verify':
                        reachability(target)
            finally:
                os.close(lock)
        result = dict(safe, ok=True, stage=args.command, code='completed', runtime_ready=False)
        if args.command == 'verify':
            result['supabase_reachable'] = True
        status = 0
    except dev.Refusal as error:
        result = dict(safe, ok=False, stage=error.stage, code=error.code, runtime_ready=False)
        if hasattr(error, 'vendor_exit'):
            result['exit_code'] = error.vendor_exit
        status = 2
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        result = dict(safe, ok=False, stage='validation', code='unsafe_or_unavailable_input', runtime_ready=False)
        status = 2
    print(json.dumps(result, sort_keys=True))
    return status
