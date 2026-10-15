"""Guard and copied-root regression checks; no registry, install, or browser needed."""
import base64
import contextlib
import importlib.util
import io
import json
import os
import signal
import threading
import re
import sys
import time
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('prove', Path(__file__).with_name('prove.py'))
prove = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prove)


class ProofGuards(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / 'source'
        self.root.mkdir()
        (self.root / 'package.json').write_text(json.dumps({'workspaces': ['platform/*', 'apps/example/web', 'tools']}))
        (self.root / 'package-lock.json').write_text(json.dumps({'lockfileVersion': 3, 'packages': {'': {}}}))
        for owner in ['platform/existing', 'platform/env-web-qualification', 'apps/example/web']:
            path = self.root / owner
            path.mkdir(parents=True)
            (path / 'package.json').write_text(json.dumps({'name': owner}))
            (path / 'source.ts').write_text('export const value = 1;')
        (self.root / 'platform/existing/package-lock.json').write_text('historical')
        self.tools = self.base / 'tools'
        for tool in ['node/bin/node', 'npm/bin/npm-cli.js']:
            path = self.tools / tool
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('qualified tool test double')
        (self.tools.parent / 'receipt.json').write_text('{}')
        preparation = self.root / f'platform/deployment/.local/kdg/{prove.RUN_ID}/inventory.json'
        preparation.parent.mkdir(parents=True)
        preparation.write_text('{}')
        self.preflight_calls = []
        self.destination = self.base / 'proof'
        self.cache = self.base / 'cache'

    def invoke(self, mode='resolve', execute=None, versions=None, host='Linux', machine='x86_64', browser=False, offline=False, preflight=None):
        args = ['prove.py', '--destination', str(self.destination), '--cache', str(self.cache), '--mode', mode]
        if offline:
            args += ['--offline']
        if browser:
            args += ['--browser-path', str(self.base / 'explicit-browser-cache')]
        versions = iter(versions or ['v26.11.1\n', '12.2.0\n'])
        def dispatch(command, **kwargs):
            if any(str(value).endswith('/toolchain.py') for value in command) or '--version' in command:
                self.preflight_calls.append((command, kwargs))
                if preflight:
                    return preflight(command, **kwargs)
                output = (json.dumps({'ok': True, 'code': 'toolchain_qualified', 'runtime_ready': False})
                          if '--version' not in command else next(versions))
                return subprocess.CompletedProcess(command, 0, output)
            return (execute(command, **kwargs) if execute else subprocess.CompletedProcess(command, 0, 'synthetic check'))
        with patch.object(prove, 'ROOT', self.root), patch.object(prove, 'TOOLS', self.tools), \
             patch('sys.argv', args), patch.object(prove.platform, 'system', return_value=host), \
             patch.object(prove.platform, 'machine', return_value=machine), \
             patch.object(prove.platform, 'platform', return_value='Linux-test-x86_64'), \
             patch.object(prove, 'execute', side_effect=dispatch), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            prove.main()

    def test_offline_resolve_applies_to_both_npm_commands(self):
        calls = []
        self.invoke(offline=True, execute=lambda command, **kwargs: (calls.append(command) or subprocess.CompletedProcess(command, 0, '')))
        self.assertEqual(len(calls), 2)
        self.assertTrue(all('--offline' in command for command in calls))

    def test_qualification_rejects_changed_foreign_lock_before_install(self):
        lock = {'lockfileVersion': 3, 'packages': {'': {}, 'node_modules/foreign': {
            'version': '1.0.0', 'resolved': 'https://foreign.example/pkg.tgz'}}}
        (self.root / 'package-lock.json').write_text(json.dumps(lock))
        calls = []
        with self.assertRaisesRegex(ValueError, 'foreign artifact'):
            self.invoke(mode='qualify', execute=lambda *a, **k: calls.append(a))
        self.assertEqual(calls, [])
        self.assertFalse(self.destination.exists())

    def test_cache_and_proof_overlap_refused_in_both_directions(self):
        for cache in [self.destination, self.destination / 'cache', self.base]:
            with self.subTest(cache=cache):
                self.cache = cache
                with self.assertRaises(SystemExit): self.invoke()
                self.assertFalse(self.destination.exists())
        self.assertEqual(self.preflight_calls, [])

    def test_preflight_ignores_hostile_environment_and_cleans_private_configs(self):
        configs = []
        def preflight(command, **kwargs):
            env = kwargs['env']
            self.assertNotIn('NODE_OPTIONS', env)
            self.assertNotIn('PYTHONPATH', env)
            self.assertEqual(env['PATH'], '/usr/bin:/bin')
            self.assertLessEqual(kwargs['timeout'], 180)
            user, global_ = Path(env['NPM_CONFIG_USERCONFIG']), Path(env['NPM_CONFIG_GLOBALCONFIG'])
            self.assertNotEqual(user, global_)
            for path in [user, global_]:
                self.assertEqual(path.read_text(), '')
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
                configs.append(path)
            output = (json.dumps({'ok': True, 'code': 'toolchain_qualified', 'runtime_ready': False})
                      if '--version' not in command else ('v26.11.1' if len(command) == 2 else '12.2.0'))
            return subprocess.CompletedProcess(command, 0, output)
        with patch.dict(os.environ, {'NODE_OPTIONS': '--require /hostile', 'NPM_CONFIG_USERCONFIG': '/hostile', 'PYTHONPATH': '/hostile'}):
            self.invoke(preflight=preflight)
        self.assertTrue(configs)
        self.assertTrue(all(not path.parent.exists() for path in configs))
        self.assertIn('qualify', self.preflight_calls[0][0])
        self.assertIn(prove.RUN_ID, self.preflight_calls[0][0])
        provenance = json.loads((self.destination / 'provenance.json').read_text())
        self.assertEqual(provenance['toolchain']['receipt_sha256'], prove.digest(self.tools.parent / 'receipt.json'))
        self.assertTrue(provenance['toolchain']['owner_result']['ok'])
        self.assertEqual(provenance['runner_sha256'], prove.digest(Path(prove.__file__)))

    def test_missing_receipt_or_preparation_refuses_before_tool_execution(self):
        for path in [self.tools.parent / 'receipt.json', self.root / f'platform/deployment/.local/kdg/{prove.RUN_ID}/inventory.json']:
            with self.subTest(path=path):
                content = path.read_text()
                path.unlink()
                try:
                    with self.assertRaises(SystemExit): self.invoke()
                    self.assertFalse(self.destination.exists())
                    self.assertEqual(self.preflight_calls, [])
                finally: path.write_text(content)

    def test_owner_refusal_and_version_timeout_leave_no_destination_or_configs(self):
        for fail_owner in [True, False]:
            configs = []
            def preflight(command, **kwargs):
                configs.append(Path(kwargs['env']['NPM_CONFIG_USERCONFIG']).parent)
                if fail_owner or '--version' in command:
                    return subprocess.CompletedProcess(command, 124, 'bounded command timeout')
                return subprocess.CompletedProcess(command, 0, json.dumps({'ok': True, 'code': 'toolchain_qualified', 'runtime_ready': False}))
            with self.subTest(fail_owner=fail_owner):
                with self.assertRaises(SystemExit): self.invoke(preflight=preflight)
                self.assertFalse(self.destination.exists())
                self.assertTrue(all(not folder.exists() for folder in configs))

    def test_every_required_fixture_failure_retains_evidence_and_raises(self):
        self.prepare_browser_input()
        for name in ['type-check', 'test', 'build', 'tools', 'browser-smoke']:
            self.destination = self.base / ('failed-' + name)
            def execute(command, **kwargs):
                failed = (('run' in command and command[command.index('run') + 1] == name) or
                          (name == 'browser-smoke' and 'scripts/browser-smoke.mjs' in command))
                return subprocess.CompletedProcess(command, 9 if failed else 0, 'required fixture failed' if failed else '')
            with self.subTest(name=name):
                with self.assertRaisesRegex(RuntimeError, 'fixture-' + name):
                    self.invoke(mode='qualify', browser=True, execute=execute)
                record = json.loads((self.destination / 'commands.json').read_text())[-1]
                self.assertEqual(record['label'], 'fixture-' + name)
                self.assertEqual(record['exit_code'], 9)
                self.assertIn('required fixture failed', (self.destination / ('fixture-' + name + '.log')).read_text())

    def test_recorded_actual_browser_executable_is_passed_to_smoke(self):
        self.prepare_browser_input()
        executable = self.base / 'headless-shell'
        executable.write_text('selected executable')
        metadata = self.base / 'browsers.json'
        metadata.write_text('{}')
        smoke_calls = []
        def execute(command, **kwargs):
            if '-e' in command:
                return subprocess.CompletedProcess(command, 0, json.dumps({
                    'executable': str(executable), 'metadata': str(metadata),
                    'package': str(metadata), 'test_package': str(metadata)}))
            if 'scripts/browser-smoke.mjs' in command:
                smoke_calls.append(kwargs['env']['ENV_CHROMIUM_EXECUTABLE'])
            return subprocess.CompletedProcess(command, 0, '')
        self.invoke(mode='qualify', browser=True, execute=execute)
        self.assertEqual(smoke_calls, [str(executable)])

    def prepare_browser_input(self):
        path = self.root / 'apps/scribeswell/data/hebrew-lexicon/lexicon.json'
        path.parent.mkdir(parents=True)
        path.write_text('{"public":"synthetic lexicon"}')
        private = self.root / 'apps/pts/reference/private-library/sentinel'
        private.parent.mkdir(parents=True)
        private.write_text('must never be copied')
        return path

    def test_browser_copy_contains_exact_public_input_and_empty_reference_only(self):
        source = self.prepare_browser_input()
        self.invoke(mode='characterize', browser=True)
        copy = self.destination / 'root'
        target = copy / source.relative_to(self.root)
        self.assertEqual(target.read_bytes(), source.read_bytes())
        reference = copy / 'apps/pts/reference'
        self.assertEqual(list(reference.iterdir()), [])
        provenance = json.loads((self.destination / 'provenance.json').read_text())
        self.assertEqual(provenance['sources'][str(source.relative_to(self.root))], prove.digest(source))
        self.assertTrue((self.root / 'apps/pts/reference/private-library/sentinel').exists())

    def test_browser_input_symlink_refuses_before_output(self):
        source = self.prepare_browser_input()
        source.unlink()
        source.symlink_to(self.root / 'package.json')
        with self.assertRaises(SystemExit):
            self.invoke(mode='characterize', browser=True)
        self.assertFalse(self.destination.exists())

    def test_nonbrowser_proof_excludes_browser_input_and_pts_reference(self):
        source = self.prepare_browser_input()
        self.invoke(mode='characterize')
        copy = self.destination / 'root'
        self.assertFalse((copy / source.relative_to(self.root)).exists())
        self.assertFalse((copy / 'apps/pts').exists())

    def test_existing_destination_is_untouched(self):
        self.destination.mkdir()
        sentinel = self.destination / 'sentinel'
        sentinel.write_text('preserve')
        with self.assertRaises(SystemExit):
            self.invoke()
        self.assertEqual(sentinel.read_text(), 'preserve')

    def test_symlink_parent_refused_before_write(self):
        alias = self.base / 'alias'
        alias.symlink_to(self.base, target_is_directory=True)
        self.destination = alias / 'proof'
        with self.assertRaises(SystemExit):
            self.invoke()
        self.assertFalse((self.base / 'proof').exists())

    def test_symlink_cache_refused(self):
        real = self.base / 'real-cache'
        real.mkdir()
        self.cache.symlink_to(real, target_is_directory=True)
        with self.assertRaises(SystemExit):
            self.invoke()
        self.assertFalse(self.destination.exists())

    def test_symlink_source_refused(self):
        (self.root / 'platform/existing/link.ts').symlink_to(self.root / 'package.json')
        with self.assertRaises(SystemExit):
            self.invoke()
        self.assertFalse(self.destination.exists())

    def test_wrong_tool_refused(self):
        with self.assertRaises(SystemExit):
            self.invoke(versions=['v24.0.0\n'])
        self.assertFalse(self.destination.exists())

    def test_unsupported_host_refuses_before_output(self):
        for host, machine in [('Darwin', 'x86_64'), ('Linux', 'aarch64')]:
            with self.subTest(host=host, machine=machine):
                with self.assertRaises(SystemExit):
                    self.invoke(host=host, machine=machine)
                self.assertFalse(self.destination.exists())

    def test_new_nested_lock_refused(self):
        (self.root / 'platform/env-web-qualification/package-lock.json').write_text('{}')
        with self.assertRaises(SystemExit):
            self.invoke()
        self.assertFalse(self.destination.exists())

    def test_resolve_copies_every_actual_workspace_and_isolates_configs(self):
        calls = []
        def execute(command, **kwargs):
            calls.append((command, kwargs))
            return subprocess.CompletedProcess(command, 0, '')
        self.invoke(execute=execute)
        copy = self.destination / 'root'
        self.assertIs(json.loads((self.destination / 'provenance.json').read_text())['runtime_ready'], False)
        for owner in ['platform/existing', 'platform/env-web-qualification', 'apps/example/web']:
            self.assertTrue((copy / owner / 'source.ts').exists())
        self.assertFalse((copy / 'platform/existing/package-lock.json').exists())
        self.assertEqual((self.root / 'platform/existing/package-lock.json').read_text(), 'historical')
        self.assertIn('--ignore-scripts', calls[0][0])
        self.assertIn('--allow-remote=all', calls[0][0])
        self.assertEqual(calls[1][0][2:], [
            'update', '@types/react', '@types/prop-types', '--workspace', 'platform/shared',
            '--package-lock-only', '--ignore-scripts', '--allow-remote=all'])
        self.assertEqual(calls[1][1]['cwd'], copy)
        self.assertNotIn('HOME', calls[0][1]['env'])
        self.assertNotIn('NODE_OPTIONS', calls[0][1]['env'])
        self.assertNotIn('PLAYWRIGHT_BROWSERS_PATH', calls[0][1]['env'])
        self.assertEqual(calls[0][1]['cwd'], copy)

    def test_characterize_excludes_only_new_fixture(self):
        calls = []
        def execute(command, **kwargs):
            calls.append(command)
            return subprocess.CompletedProcess(command, 0, '')
        self.invoke(mode='characterize', execute=execute)
        self.assertTrue(all('--allow-remote=all' not in command for command in calls))
        copy = self.destination / 'root'
        self.assertFalse((copy / 'platform/env-web-qualification').exists())
        self.assertTrue((copy / 'platform/existing/source.ts').exists())
        self.assertTrue((copy / 'apps/example/web/source.ts').exists())

    def test_ci_lock_mutation_refused(self):
        def execute(command, **kwargs):
            (kwargs['cwd'] / 'package-lock.json').write_text('changed')
            return subprocess.CompletedProcess(command, 0, '')
        with self.assertRaisesRegex(RuntimeError, 'ci changed lock'):
            self.invoke(mode='qualify', execute=execute)


class ProcessTimeout(unittest.TestCase):
    @staticmethod
    def exited(pid):
        try:
            return Path(f'/proc/{pid}/stat').read_text().split()[2] == 'Z'
        except (FileNotFoundError, ProcessLookupError):
            # A reaped process can disappear between /proc lookup and read.
            return True

    @unittest.skipUnless(sys.platform == 'linux', 'Linux process-group proof')
    def test_timeout_terminates_child_and_grandchild_holding_stdout(self):
        grandchild = "import os,signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); print('GRANDCHILD',os.getpid(),flush=True); time.sleep(30)"
        child = ("import os,signal,subprocess,sys,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
                 f"subprocess.Popen([sys.executable,'-u','-c',{grandchild!r}]); "
                 "print('CHILD',os.getpid(),flush=True); time.sleep(30)")
        parent = ("import os,subprocess,sys,time; "
                  f"subprocess.Popen([sys.executable,'-u','-c',{child!r}]); "
                  "print('PARENT',os.getpid(),flush=True); time.sleep(30)")
        started = time.monotonic()
        result = prove.execute([sys.executable, '-u', '-c', parent], cwd=Path.cwd(),
                               env={'PATH': '/usr/bin:/bin'}, timeout=0.5, grace=0.1)
        self.assertLess(time.monotonic() - started, 3)
        self.assertEqual(result.returncode, 124)
        self.assertIn('bounded command timeout', result.stdout)
        pids = re.findall(r'(?:PARENT|CHILD|GRANDCHILD) (\d+)', result.stdout)
        self.assertEqual(len(pids), 3, result.stdout)
        for pid in pids:
            deadline = time.monotonic() + 0.5
            while not self.exited(pid) and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(self.exited(pid), f'live descendant {pid}')

    @unittest.skipUnless(sys.platform == 'linux', 'Linux process-group proof')
    def test_keyboard_interrupt_terminates_real_child_and_grandchild(self):
        with tempfile.TemporaryDirectory() as folder:
            pids_file = Path(folder) / 'pids'
            record = f"open({str(pids_file)!r},'a').write(str(os.getpid())+'\\n'); "
            grandchild = "import os,signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); " + record + "time.sleep(30)"
            child = ("import os,signal,subprocess,sys,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); " +
                     record + f"subprocess.Popen([sys.executable,'-u','-c',{grandchild!r}]); time.sleep(30)")
            parent = ("import os,subprocess,sys,time; " + record +
                      f"subprocess.Popen([sys.executable,'-u','-c',{child!r}]); time.sleep(30)")
            timer = threading.Timer(0.5, os.kill, args=(os.getpid(), signal.SIGINT))
            started = time.monotonic()
            timer.start()
            try:
                with self.assertRaises(KeyboardInterrupt):
                    prove.execute([sys.executable, '-u', '-c', parent], cwd=Path(folder),
                                  env={'PATH': '/usr/bin:/bin'}, timeout=30, grace=0.1)
            finally:
                timer.cancel()
                timer.join()
            self.assertLess(time.monotonic() - started, 3)
            pids = pids_file.read_text().splitlines()
            self.assertEqual(len(pids), 3)
            for pid in pids:
                deadline = time.monotonic() + 0.5
                while not self.exited(pid) and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(self.exited(pid), f'live interrupted descendant {pid}')


class BrowserIdentity(unittest.TestCase):
    def test_actual_executable_and_installed_metadata_hashes_and_missing_binary(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            records = {}
            for key in ['executable', 'metadata', 'package', 'test_package']:
                path = root / key
                path.write_text('public-' + key)
                records[key] = str(path)
            with patch.object(prove, 'execute', return_value=subprocess.CompletedProcess([], 0, json.dumps(records))):
                identity = prove.browser_identity(root, root, {}, Path('node'), Path('.'))
                self.assertEqual(identity['status'], 'qualified-identity-only')
                for key, path in records.items():
                    self.assertEqual(identity['artifacts'][key]['sha256'], prove.digest(Path(path)))
                Path(records['executable']).unlink()
                missing = prove.browser_identity(root, root, {}, Path('node'), Path('.'))
                self.assertEqual(missing['status'], 'unqualified')
                self.assertTrue(missing['artifacts']['executable']['missing'])

    def test_headless_shell_is_recorded_when_full_chromium_is_absent(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shell = root / 'chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell'
            shell.parent.mkdir(parents=True)
            shell.write_text('publisher headless executable')
            full = root / 'chromium-1248/chrome-linux64/chrome'
            metadata = root / 'browsers.json'
            metadata.write_text('{"browsers":[{"name":"chromium-headless-shell","revision":"1248"}]}')
            package = root / 'package.json'
            package.write_text('{"version":"1.64.0"}')
            def probe(command, **kwargs):
                self.assertIn('launchServer({headless:true', command[-1])
                self.assertIn('server.process().spawnfile', command[-1])
                self.assertNotIn('chromium.executablePath()', command[-1])
                return subprocess.CompletedProcess(command, 0, json.dumps({
                    'executable': str(shell), 'metadata': str(metadata), 'package': str(package), 'test_package': str(package)}))
            with patch.object(prove, 'execute', side_effect=probe):
                identity = prove.browser_identity(root, root, {'PLAYWRIGHT_BROWSERS_PATH': str(root)}, Path('node'), Path('.'))
            self.assertFalse(full.exists())
            self.assertEqual(identity['status'], 'qualified-identity-only')
            self.assertEqual(identity['artifacts']['executable']['path'], str(shell))
            self.assertEqual(identity['artifacts']['executable']['sha256'], prove.digest(shell))

    def test_no_explicit_browser_stays_unqualified_without_subprocess(self):
        with patch.object(prove, 'execute') as execute:
            self.assertEqual(prove.browser_identity(Path('.'), None, {}, Path('node'), Path('.'))['status'], 'unqualified')
            execute.assert_not_called()


class LockSources(unittest.TestCase):
    def setUp(self):
        self.registry = {'version': '12.2.0', 'resolved': 'https://registry.npmjs.org/npm/-/npm-12.2.0.tgz',
                         'integrity': 'sha512-' + base64.b64encode(b'x' * 64).decode()}
        self.lock = {'lockfileVersion': 3, 'packages': {
            '': {}, 'platform/fixture': {'name': '@platform/fixture'},
            'node_modules/@platform/fixture': {'link': True, 'resolved': 'platform/fixture'},
            'node_modules/npm': dict(self.registry),
            'node_modules/npm/node_modules/abbrev': {'version': '4.0.0', 'inBundle': True}}}

    def validate(self):
        prove.validate_lock(self.lock, {'@platform/fixture': 'platform/fixture'})

    def test_registry_integrity_known_workspace_and_pinned_bundle_are_accepted(self):
        self.validate()

    def test_foreign_or_non_registry_sources_are_rejected(self):
        for source in ['https://evil.example/npm.tgz', 'https://registry.npmjs.org.evil/npm.tgz',
                       'http://registry.npmjs.org/npm.tgz', 'git+https://registry.npmjs.org/npm',
                       'file:../npm.tgz', 'https://user@registry.npmjs.org/npm.tgz']:
            with self.subTest(source=source):
                self.lock['packages']['node_modules/npm']['resolved'] = source
                with self.assertRaises(ValueError): self.validate()

    def test_missing_or_invalid_integrity_is_rejected(self):
        for integrity in [None, 'sha512-invalid', 'sha1-' + 'A' * 28]:
            with self.subTest(integrity=integrity):
                self.lock['packages']['node_modules/npm']['integrity'] = integrity
                with self.assertRaises(ValueError): self.validate()

    def test_unknown_workspace_link_is_rejected(self):
        self.lock['packages']['node_modules/@platform/fixture']['resolved'] = '../outside'
        with self.assertRaises(ValueError): self.validate()

    def test_unpinned_bundle_owner_is_rejected(self):
        self.lock['packages']['node_modules/npm']['version'] = '12.3.0'
        with self.assertRaises(ValueError): self.validate()

    def test_unknown_bundle_and_unresolved_artifact_are_rejected(self):
        self.lock['packages']['node_modules/foreign/node_modules/payload'] = {'version': '1', 'inBundle': True}
        with self.assertRaises(ValueError): self.validate()
        del self.lock['packages']['node_modules/foreign/node_modules/payload']
        self.lock['packages']['node_modules/missing'] = {'version': '1'}
        with self.assertRaises(ValueError): self.validate()


if __name__ == '__main__':
    unittest.main()
