"""Native lifecycle acceptance with an isolated workspace and fake vendor process."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch

import dev
import native_cli

ROOT = Path(__file__).resolve().parents[3]


class NativeAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ['dev.py', 'native_cli.py', 'schema/development-target-v1.json']:
            source = ROOT / 'platform/deployment' / name
            if source.exists():
                destination = self.root / 'platform/deployment' / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
        self.target = json.loads((ROOT / 'platform/deployment/environments/kdg-local.json').read_text())
        self.target['workspace_root'] = str(self.root)
        self.target_path = self.root / 'target.json'
        self.target_path.write_text(json.dumps(self.target))
        self.run_id = str(uuid.uuid4())
        self.run = self.root / 'platform/deployment/.local/kdg' / self.run_id
        self.vendor = self.root / 'supabase'
        self.vendor.write_text('#!' + sys.executable + '\nimport sys\nprint("2.120.0" if sys.argv[1:] == ["--version"] else "credential-sentinel")\n')
        self.vendor.chmod(0o700)

    def invoke(self, command='prepare', extra=()):
        return subprocess.run([sys.executable, str(self.root / 'platform/deployment/dev.py'), command,
            '--target', str(self.target_path), '--run-id', self.run_id,
            '--supabase', str(self.vendor), *extra], capture_output=True, text=True)

    def test_prepare_is_private_idempotent_without_qualifier_receipts(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        marker = self.run / 'native.json'
        original = marker.read_bytes()
        self.assertEqual(marker.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.run.stat().st_mode & 0o777, 0o700)
        self.assertEqual(self.invoke().returncode, 0)
        self.assertEqual(marker.read_bytes(), original)
        self.assertFalse((self.run / 'inventory.json').exists())

    def test_unsafe_targets_and_run_refused(self):
        for field, value in [('environment_kind', 'production'), ('workspace_root', '/foreign'), ('unknown', 'secret')]:
            target = dict(self.target, **{field: value})
            self.target_path.write_text(json.dumps(target))
            self.assertNotEqual(self.invoke().returncode, 0)
            self.assertFalse(self.run.exists())
        self.target_path.write_text(json.dumps(self.target))
        self.run_id = self.run_id.upper()
        self.assertNotEqual(self.invoke().returncode, 0)

    def test_legacy_and_changed_or_symlink_config_refused(self):
        self.run.mkdir(parents=True, mode=0o700)
        self.run.parent.chmod(0o700)
        self.run.parent.parent.chmod(0o700)
        (self.run / 'inventory.json').write_text('{}')
        self.assertNotEqual(self.invoke().returncode, 0)
        shutil.rmtree(self.run)
        self.assertEqual(self.invoke().returncode, 0)
        config = self.run / 'supabase/config.toml'
        original = config.read_bytes()
        config.write_bytes(original + b'\nchanged')
        self.assertNotEqual(self.invoke('stop').returncode, 0)
        config.unlink()
        other = self.root / 'other'
        other.write_bytes(original)
        config.symlink_to(other)
        self.assertNotEqual(self.invoke('stop').returncode, 0)

    def test_shared_local_readable_parent_allowed_writable_parent_refused(self):
        local = self.root / 'platform/deployment/.local'
        local.mkdir(mode=0o755)
        local.chmod(0o755)
        self.assertEqual(self.invoke().returncode, 0)
        self.assertEqual((local / 'kdg').stat().st_mode & 0o777, 0o700)
        self.assertEqual(self.run.stat().st_mode & 0o777, 0o700)
        for mode in [0o775, 0o777]:
            local.chmod(mode)
            self.run_id = str(uuid.uuid4())
            result = self.invoke()
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((local / 'kdg' / self.run_id).exists())
        local.chmod(0o755)
        (local / 'kdg').chmod(0o755)
        self.run_id = str(uuid.uuid4())
        self.assertNotEqual(self.invoke().returncode, 0)
        self.assertFalse((local / 'kdg' / self.run_id).exists())

    def test_reset_confirmation_and_wrong_version(self):
        self.assertNotEqual(self.invoke('reset').returncode, 0)
        self.vendor.write_text('#!' + sys.executable + '\nprint("2.119.0 credential-sentinel")\n')
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('credential-sentinel', result.stdout + result.stderr)


class LifecycleAcceptance(unittest.TestCase):
    invoke = NativeAcceptance.invoke

    def setUp(self):
        NativeAcceptance.setUp(self)
        self.assertEqual(self.invoke().returncode, 0)
        self.trace = self.root / 'calls.jsonl'
        self.vendor.write_text('#!' + sys.executable + '\n' +
            'import json, os, sys, time\n' +
            'with open(' + repr(str(self.trace)) + ', "a") as f: f.write(json.dumps({"args": sys.argv[1:], "env": dict(os.environ), "cwd": os.getcwd()}) + "\\n")\n' +
            'print("2.120.0" if sys.argv[1:] == ["--version"] else "credential-sentinel")\n' +
            'print("credential-sentinel", file=sys.stderr)\n')
        self.identity = 'a' * 64
        self.network_value = None
        self.docker_calls = []
        self.docker_version = '28.0.0'

    def docker(self, arguments, path, missing=False):
        self.docker_calls.append(arguments)
        if arguments[0] == 'version':
            return json.dumps({'Os': 'linux', 'Version': self.docker_version}).encode()
        if arguments[1] == 'create':
            self.network_value = {'Name': arguments[-1], 'Driver': 'bridge', 'Id': self.identity,
                'Options': {native_cli.BINDING: '127.0.0.1'}, 'Labels': {}}
            for index, value in enumerate(arguments):
                if value == '--label':
                    key, item = arguments[index + 1].split('=', 1)
                    self.network_value['Labels'][key] = item
            return self.identity.encode()
        if self.network_value is None:
            return None
        return json.dumps(self.network_value).encode()

    def run_native(self, command, extra=(), port_conflict=False):
        output = io.StringIO()
        with patch.object(dev, 'ROOT', self.root), patch.object(native_cli, 'docker', side_effect=self.docker), \
                patch.object(dev, 'free_ports', return_value=contextlib.nullcontext(),
                    side_effect=dev.Refusal('ports', 'port_unavailable') if port_conflict else None), contextlib.redirect_stdout(output):
            status = native_cli.main([command, '--target', str(self.target_path), '--run-id', self.run_id,
                                      '--supabase', str(self.vendor), *extra])
        self.assertNotIn('credential-sentinel', output.getvalue())
        return status, json.loads(output.getvalue())

    def calls(self):
        return [json.loads(line) for line in self.trace.read_text().splitlines()] if self.trace.exists() else []

    def test_exact_lifecycle_and_clean_environment(self):
        with patch.dict(os.environ, {'DOCKER_HOST': 'tcp://foreign:2375', 'DOCKER_CONTEXT': 'foreign',
                                    'SUPABASE_ACCESS_TOKEN': 'credential-sentinel', 'HTTP_PROXY': 'http://foreign'}):
            self.assertEqual(self.run_native('up')[0], 0)
        with patch.object(native_cli, 'reachability') as probe:
            status, result = self.run_native('verify')
            self.assertEqual(status, 0)
            self.assertTrue(result['supabase_reachable'])
            self.assertFalse(result['runtime_ready'])
            probe.assert_called_once_with(self.target)
        self.assertEqual(self.run_native('stop')[0], 0)
        self.assertEqual(self.run_native('reset', ['--confirm-target', self.target['target_id']])[0], 0)
        operations = [call for call in self.calls() if call['args'] != ['--version']]
        common = ['--workdir', str(self.run), '--network-id', self.identity]
        self.assertEqual([c['args'] for c in operations], [common + ['start'], common + ['status'],
            common + ['stop', '--project-id', dev.project_identity(self.target, self.run_id)],
            common + ['db', 'reset', '--local', '--no-seed', '--yes']])
        for call in self.calls():
            self.assertEqual(call['env']['DOCKER_HOST'], 'unix:///var/run/docker.sock')
            self.assertEqual(call['env']['SUPABASE_HOME'], str(self.run / 'supabase-home'))
            self.assertEqual(call['env']['DOCKER_CONFIG'], str(self.run / 'docker'))
            self.assertEqual(call['env'].get('HOME'), os.environ.get('HOME'))
            self.assertEqual(call['env']['SUPABASE_EXPERIMENTAL_STACK'], '0')
            self.assertNotIn('DOCKER_CONTEXT', call['env'])
            self.assertNotIn('SUPABASE_ACCESS_TOKEN', call['env'])
            self.assertNotIn('HTTP_PROXY', call['env'])
            self.assertEqual(call['cwd'], str(self.run))
        self.assertEqual(sum(args[:2] == ['network', 'create'] for args in self.docker_calls), 1)
        self.assertFalse(any('rm' in args or 'prune' in args for args in self.docker_calls))

    def test_unsafe_bridge_and_absent_network_never_start_vendor(self):
        self.assertNotEqual(self.run_native('stop')[0], 0)
        self.assertTrue(all(call['args'] == ['--version'] for call in self.calls()))
        self.assertEqual(self.run_native('up')[0], 0)
        for key, value in [('Driver', 'overlay'), ('Options', {}), ('Labels', {})]:
            original = self.network_value[key]
            self.network_value[key] = value
            before = len(self.calls())
            self.assertNotEqual(self.run_native('up')[0], 0)
            self.assertEqual(len(self.calls()), before + 1)  # only the version probe
            self.network_value[key] = original

    def test_port_conflict_and_old_docker_refuse_before_start(self):
        with patch.object(dev, 'free_ports', side_effect=dev.Refusal('ports', 'port_unavailable')):
            # run_native's own free-port substitute is deliberately overridden here.
            with patch.object(dev, 'ROOT', self.root), patch.object(native_cli, 'docker', side_effect=self.docker), contextlib.redirect_stdout(io.StringIO()):
                status = native_cli.main(['up', '--target', str(self.target_path), '--run-id', self.run_id, '--supabase', str(self.vendor)])
        self.assertEqual(status, 2)
        self.docker_version = '27.9.9'
        status, result = self.run_native('up')
        self.assertEqual(status, 2)
        self.assertEqual(result['code'], 'docker_28_required')
        self.assertTrue(all(call['args'] == ['--version'] for call in self.calls()))
        self.assertFalse(any(args[:2] == ['network', 'create'] for args in self.docker_calls))

    def test_repeat_up_accepts_same_running_project_despite_occupied_ports(self):
        self.assertEqual(self.run_native('up')[0], 0)
        status, result = self.run_native('up', port_conflict=True)
        self.assertEqual(status, 0, result)
        common = ['--workdir', str(self.run), '--network-id', self.identity]
        self.assertEqual([call['args'] for call in self.calls() if call['args'] != ['--version']],
                         [common + ['start'], common + ['status'], common + ['start']])
        self.assertEqual(sum(args[:2] == ['network', 'create'] for args in self.docker_calls), 1)
        # The same network alone cannot bypass conflicts for a stopped project.
        with self.vendor.open('a') as script:
            script.write('if sys.argv[-1] == "status": sys.exit(1)\n')
        before = len(self.calls())
        status, result = self.run_native('up', port_conflict=True)
        self.assertEqual(status, 2)
        self.assertEqual(result['code'], 'port_unavailable')
        self.assertEqual([call['args'] for call in self.calls()[before:]], [['--version'], common + ['status']])

    def test_partial_initial_configuration_is_preserved_and_fresh_uuid_recovers(self):
        self.run_id = str(uuid.uuid4())
        self.run = self.run.parent / self.run_id
        def failed_write(run, target, run_id):
            os.mkdir('supabase', 0o700, dir_fd=run)
            config_dir = os.open('supabase', os.O_RDONLY | os.O_DIRECTORY, dir_fd=run)
            try:
                config = os.open('config.toml', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=config_dir)
                with os.fdopen(config, 'wb') as output:
                    output.write(b'partial configuration')
                    output.flush()
                    raise OSError('credential-sentinel')
            finally:
                os.close(config_dir)
        with patch.object(dev, 'install_configuration', side_effect=failed_write):
            status, result = self.run_native('prepare')
        self.assertEqual(status, 2)
        self.assertFalse((self.run / 'native.json').exists())
        partial = self.run / 'supabase/config.toml'
        original_bytes = partial.read_bytes()
        self.assertEqual(self.calls(), [])
        self.assertNotEqual(self.run_native('prepare')[0], 0)
        self.assertNotEqual(self.run_native('up')[0], 0)
        self.assertEqual(partial.read_bytes(), original_bytes)
        self.assertEqual(self.calls(), [])
        self.run_id = str(uuid.uuid4())
        self.run = self.run.parent / self.run_id
        self.assertEqual(self.invoke().returncode, 0)
        self.assertTrue((self.run / 'native.json').exists())
        self.assertEqual([call['args'] for call in self.calls()], [['--version']])

    def test_vendor_error_timeout_and_reset_confirmation_are_safe(self):
        self.assertEqual(self.run_native('up')[0], 0)
        before = len(self.calls())
        self.assertNotEqual(self.run_native('reset')[0], 0)
        self.assertEqual(len(self.calls()), before)
        self.vendor.write_text('#!' + sys.executable + '\nimport sys\nprint("2.120.0")\nif sys.argv[1:] != ["--version"]:\n print("credential-sentinel", file=sys.stderr)\n sys.exit(7)\n')
        status, result = self.run_native('stop')
        self.assertEqual(status, 2)
        self.assertEqual(result['exit_code'], 7)
        self.vendor.write_text('#!' + sys.executable + '\nimport sys, time\nprint("2.120.0")\nif sys.argv[1:] != ["--version"]: time.sleep(1)\n')
        with patch.dict(native_cli.TIMEOUTS, stop=.02):
            status, result = self.run_native('stop')
        self.assertEqual(status, 2)
        self.assertEqual(result['code'], 'vendor_timeout')
        self.assertFalse(any('rm' in args or 'prune' in args for args in self.docker_calls))

    def test_docker_process_boundary_is_local_bounded_and_silent(self):
        real_run = subprocess.run
        docker_executable = self.root / 'docker-test'
        docker_executable.write_text('#!' + sys.executable + '\nimport json, os, sys\n'
            'assert os.environ["DOCKER_HOST"] == "unix:///var/run/docker.sock"\n'
            'assert "DOCKER_CONTEXT" not in os.environ\n'
            'assert os.environ["SUPABASE_EXPERIMENTAL_STACK"] == "0"\n'
            'assert sys.argv[1:] == ["version", "--format", "{{json .Server}}"]\n'
            'print(json.dumps({"Os": "linux", "Version": "28.0.1"}))\n'
            'print("credential-sentinel", file=sys.stderr)\n')
        docker_executable.chmod(0o700)
        calls = []
        def process(arguments, **kwargs):
            calls.append((arguments, kwargs))
            self.assertEqual(arguments[0], 'docker')
            return real_run([str(docker_executable), *arguments[1:]], **kwargs)
        with patch.object(native_cli.subprocess, 'run', side_effect=process):
            native_cli.docker_prerequisite(self.run)
        self.assertEqual(calls[0][1]['timeout'], 15)
        self.assertEqual(calls[0][1]['cwd'], self.run)
        docker_executable.write_text('#!' + sys.executable + '\nimport sys\nprint("credential-sentinel")\nprint("credential-sentinel", file=sys.stderr)\nsys.exit(7)\n')
        with patch.object(native_cli.subprocess, 'run', side_effect=process):
            with self.assertRaises(dev.Refusal) as failure:
                native_cli.docker_prerequisite(self.run)
        self.assertEqual(failure.exception.code, 'docker_failed')
        self.assertNotIn('credential-sentinel', str(failure.exception))
        with patch.object(native_cli.subprocess, 'run', side_effect=subprocess.TimeoutExpired('credential-sentinel', 15)):
            with self.assertRaises(dev.Refusal) as failure:
                native_cli.docker_prerequisite(self.run)
        self.assertEqual(failure.exception.code, 'docker_timeout')

    def test_private_state_symlink_and_marker_changes_refuse_before_vendor(self):
        (self.run / 'native.json').write_text('{}')
        self.assertNotEqual(self.run_native('stop')[0], 0)
        self.assertEqual(self.calls(), [])
        shutil.rmtree(self.run)
        self.assertEqual(self.invoke().returncode, 0)
        shutil.rmtree(self.run / 'supabase-home')
        (self.run / 'supabase-home').symlink_to(self.root, target_is_directory=True)
        self.trace.unlink(missing_ok=True)
        self.assertNotEqual(self.run_native('stop')[0], 0)
        self.assertEqual(self.calls(), [])

    def test_reachability_requires_db_and_auth(self):
        with patch.object(socket, 'create_connection', side_effect=OSError):
            with self.assertRaises(dev.Refusal):
                native_cli.reachability(self.target)
        with patch.object(socket, 'create_connection') as tcp, patch.object(native_cli.http.client, 'HTTPConnection') as http:
            http.return_value.getresponse.return_value.status = 503
            with self.assertRaises(dev.Refusal):
                native_cli.reachability(self.target)
            http.return_value.getresponse.return_value.status = 200
            native_cli.reachability(self.target)
            self.assertEqual(tcp.call_args.args[0], ('127.0.0.1', self.target['ports']['database']))
            http.return_value.request.assert_called_with('GET', '/auth/v1/health')


if __name__ == '__main__':
    unittest.main()
