"""Local archive guards and public qualification refusal; no downloads or tool substitutes."""
import hashlib
from contextlib import redirect_stdout
from concurrent.futures import ThreadPoolExecutor
import base64
import http.client
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

from test_dev import FILES, ROOT

sys.path.insert(0, str(ROOT / 'platform/deployment'))
import toolchain
import dev


class QualificationGuards(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in FILES + ['platform/deployment/toolchain.py', 'platform/deployment/toolchain-pins.json']:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, path)
        target = json.loads((self.root / FILES[2]).read_text())
        target['workspace_root'] = str(self.root)
        self.target = self.root / 'target.json'
        self.target.write_text(json.dumps(target))
        self.run_id = str(uuid.uuid4())
        self.run = self.root / 'platform/deployment/.local/kdg-toolchains' / self.run_id

    def cli(self, extra=()):
        return subprocess.run([sys.executable, str(self.root / 'platform/deployment/toolchain.py'),
                               'qualify', '--target', str(self.target), '--run-id', self.run_id, *extra],
                              text=True, capture_output=True, cwd='/tmp')

    def test_public_missing_preparation_refuses_without_tool_writes(self):
        result = self.cli()
        self.assertEqual(result.returncode, 2)
        data = json.loads(result.stdout)
        self.assertFalse(data['toolchain_ready'])
        self.assertFalse(data['runtime_ready'])
        self.assertEqual(result.stderr, '')
        self.assertFalse(self.run.parent.exists())

    def test_public_invalid_uuid_unknown_argument_and_symlink_target(self):
        self.run_id = '../sensitive-marker'
        for extra in [(), ('--sensitive-marker',)]:
            result = self.cli(extra)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn('sensitive-marker', result.stdout)
            self.assertEqual(result.stderr, '')
        self.run_id = str(uuid.uuid4())
        original = self.target
        self.target = self.root / 'link.json'
        self.target.symlink_to(original)
        self.assertEqual(self.cli().returncode, 2)
        self.assertFalse(self.run.exists())

    def archive(self, entries):
        archive = self.root / 'fixture.tar'
        with tarfile.open(archive, 'w') as output:
            for name, kind, content in entries:
                member = tarfile.TarInfo(name)
                member.mode = 0o755
                if kind == 'file':
                    raw = content.encode()
                    member.size = len(raw)
                    output.addfile(member, io.BytesIO(raw))
                else:
                    member.type = tarfile.SYMTYPE
                    member.linkname = content
                    output.addfile(member)
        return archive

    def test_archive_escape_and_link_parent_refuse_before_extraction(self):
        for entries in [[('../outside', 'file', 'bad')],
                        [('link', 'link', '../../outside')],
                        [('link', 'link', 'inside'), ('link/file', 'file', 'bad')]]:
            with self.subTest(entries=entries):
                archive = self.archive(entries)
                payload = self.root / ('payload-' + uuid.uuid4().hex)
                payload.mkdir(mode=0o700)
                with self.assertRaises(dev.Refusal):
                    toolchain.extract(archive, {'format': 'tar', 'destination': 'tool', 'strip_prefix': ''}, payload)
                self.assertEqual(list((payload / 'tool').iterdir()), [])
                self.assertFalse((self.root / 'outside').exists())

    def test_payload_safe_symlink_recorded_and_tampering_detectable(self):
        payload = self.root / 'payload'
        payload.mkdir(mode=0o700)
        (payload / 'binary').write_bytes(b'original')
        (payload / 'binary').chmod(0o700)
        (payload / 'link').symlink_to('binary')
        before = toolchain.payload_evidence(payload)
        self.assertEqual(before['link'], {'kind': 'symlink', 'target': 'binary'})
        (payload / 'binary').write_bytes(b'changed')
        self.assertNotEqual(toolchain.payload_evidence(payload), before)

    def test_digest_mismatch_and_symlink_archive_never_extract(self):
        archive = self.archive([('binary', 'file', 'contents')])
        archive.chmod(0o600)
        with self.assertRaises(dev.Refusal):
            toolchain.verify_digest(archive, 'sha256', b'0' * 32)
        link = self.root / 'archive-link'
        link.symlink_to(archive)
        with self.assertRaises(OSError):
            toolchain.verify_digest(link, 'sha256', hashlib.sha256(archive.read_bytes()).digest())

    def test_unknown_malformed_pins_fail_closed(self):
        pins_path = self.root / 'platform/deployment/toolchain-pins.json'
        original = json.loads(pins_path.read_text())
        for mutation in [lambda p: p.update(unknown=True),
                         lambda p: p['archives'][0].update(integrity='sha256-invalid'),
                         lambda p: p['archives'][0].update(destination='../outside'),
                         lambda p: p['archives'].append(p['archives'][0])]:
            pins = json.loads(json.dumps(original))
            mutation(pins)
            pins_path.write_text(json.dumps(pins))
            with patch.object(dev, 'ROOT', self.root), self.assertRaises(dev.Refusal):
                toolchain.load_pins()

    def test_prepared_source_change_refuses_before_tool_writes(self):
        result = subprocess.run([sys.executable, str(self.root / FILES[0]), 'prepare',
                                 '--target', str(self.target), '--run-id', self.run_id], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        path = self.root / FILES[-1]
        path.write_bytes(path.read_bytes() + b'\nchanged\n')
        self.assertEqual(self.cli().returncode, 2)
        self.assertFalse(self.run.parent.exists())

    def prepare(self):
        result = subprocess.run([sys.executable, str(self.root / FILES[0]), 'prepare',
                                 '--target', str(self.target), '--run-id', self.run_id], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout)

    def unit_install(self):
        """Exercise receipt sequencing only; real six-tool execution is separate acceptance."""
        self.prepare()
        def fixture_extract(archive, item, payload):
            path = payload / item['id']
            path.write_bytes(b'synthetic unit payload')
            path.chmod(0o600)
        self.args = SimpleNamespace(target=str(self.target), run_id=self.run_id)
        self.addCleanup(patch.stopall)
        patch.object(dev, 'ROOT', self.root).start()
        patch.object(toolchain, 'verified_archive', return_value=self.root / 'unused').start()
        self.extractor = patch.object(toolchain, 'extract', side_effect=fixture_extract).start()
        self.executor = patch.object(toolchain, 'execute', return_value=toolchain.expected_checks()).start()
        result = toolchain.qualify(self.args)
        self.assertTrue(result['toolchain_ready'])
        self.assertFalse(result['runtime_ready'])

    def test_unit_repeat_preserves_receipt_and_rejects_receipt_tampering_before_execution(self):
        self.unit_install()
        receipt = self.run / 'receipt.json'
        original = receipt.read_bytes()
        self.assertLess(len(original), dev.LIMIT)
        self.executor.reset_mock()
        self.extractor.reset_mock()
        toolchain.qualify(self.args)
        self.executor.assert_called_once()
        self.extractor.assert_not_called()
        self.assertEqual(receipt.read_bytes(), original)
        mutations = [lambda x: x.update(schema_version=True),
                     lambda x: x['checks'].update(python_gil_platform_stdlib=1),
                     lambda x: x.update(runtime_blockers=[]),
                     lambda x: x['binding'].update(target_sha256='changed')]
        for mutate in mutations:
            data = json.loads(original)
            mutate(data)
            receipt.write_text(json.dumps(data))
            self.executor.reset_mock()
            with self.assertRaises(dev.Refusal):
                toolchain.qualify(self.args)
            self.executor.assert_not_called()
        receipt.write_bytes(original)

    def test_unit_changed_payload_refuses_before_execution_and_keeps_receipt(self):
        self.unit_install()
        receipt = (self.run / 'receipt.json').read_bytes()
        (self.run / 'payload/node').write_bytes(b'tampered')
        self.executor.reset_mock()
        with self.assertRaises(dev.Refusal):
            toolchain.qualify(self.args)
        self.executor.assert_not_called()
        self.assertEqual((self.run / 'receipt.json').read_bytes(), receipt)

    def test_config_changed_during_execution_refuses_without_replacing_receipt(self):
        self.unit_install()
        receipt = (self.run / 'receipt.json').read_bytes()
        def execute(*args, **kwargs):
            path = self.root / 'platform/deployment/.local/kdg' / self.run_id / 'supabase/config.toml'
            path.write_text('changed = true\n')
            return toolchain.expected_checks()
        self.executor.side_effect = execute
        with self.assertRaises(dev.Refusal):
            toolchain.qualify(self.args)
        self.assertEqual((self.run / 'receipt.json').read_bytes(), receipt)

    def test_public_partial_install_and_concurrent_lock_refused_without_repair(self):
        self.prepare()
        self.run.mkdir(parents=True, mode=0o700)
        self.run.parent.chmod(0o700)
        marker = self.run / 'partial'
        marker.write_bytes(b'untouched')
        result = self.cli()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['code'], 'incomplete_install')
        self.assertEqual(set(p.name for p in self.run.iterdir()), {'partial'})
        lock = self.run / '.qualify.lock'
        lock.write_bytes(b'owned by another installer')
        lock.chmod(0o600)
        self.assertEqual(self.cli().returncode, 2)
        self.assertEqual(marker.read_bytes(), b'untouched')
        self.assertEqual(lock.read_bytes(), b'owned by another installer')

    def test_state_symlink_and_hardlink_cannot_overwrite_outside_file(self):
        state = self.root / 'state'
        state.mkdir(mode=0o700)
        outside = self.root / 'outside'
        outside.write_bytes(b'untouched')
        path = state / 'valid.ts'
        path.symlink_to(outside)
        with self.assertRaises(dev.Refusal):
            toolchain.check_state(state)
        with self.assertRaises(OSError):
            toolchain.write_fixture(path, 'bad')
        path.unlink()
        os.link(outside, path)
        with self.assertRaises(dev.Refusal):
            toolchain.write_fixture(path, 'bad')
        self.assertEqual(outside.read_bytes(), b'untouched')

    def test_archive_nested_parents_private_and_payload_link_escape_refused(self):
        archive = self.archive([('package/nested/tool', 'file', 'synthetic')])
        payload = self.root / 'payload'
        payload.mkdir(mode=0o700)
        toolchain.extract(archive, {'format': 'tar', 'destination': 'packages/node_modules/tool',
                                   'strip_prefix': 'package/'}, payload)
        toolchain.payload_evidence(payload)
        for path in payload.rglob('*'):
            self.assertFalse(path.lstat().st_mode & 0o077)
        (payload / 'escape').symlink_to(self.root / 'outside')
        with self.assertRaises(dev.Refusal):
            toolchain.payload_evidence(payload)

    def test_planned_link_graph_escape_refused(self):
        archive = self.archive([('a', 'link', '.'), ('b', 'link', 'a/a/../../outside')])
        payload = self.root / 'payload'
        payload.mkdir(mode=0o700)
        with self.assertRaises(dev.Refusal):
            toolchain.extract(archive, {'format': 'tar', 'destination': 'tool', 'strip_prefix': ''}, payload)
        self.assertFalse((self.root / 'outside').exists())

    def test_unit_receipt_changed_during_execution_refuses(self):
        self.unit_install()
        receipt = self.run / 'receipt.json'
        def change_receipt(*args, **kwargs):
            receipt.write_text('{}')
            return toolchain.expected_checks()
        self.executor.side_effect = change_receipt
        with self.assertRaises(dev.Refusal):
            toolchain.qualify(self.args)

    def test_pin_snapshot_changed_after_decode_refuses(self):
        original = toolchain.load_pins
        def change_after_decode(*args, **kwargs):
            result = original(*args, **kwargs)
            pin = self.root / 'platform/deployment/toolchain-pins.json'
            pin.write_bytes(pin.read_bytes() + b'\n')
            return result
        with patch.object(toolchain, 'load_pins', side_effect=change_after_decode):
            with self.assertRaises(dev.Refusal):
                self.unit_install()

    def test_corrupt_cached_archive_refuses_before_extraction_or_receipt(self):
        self.prepare()
        pins = json.loads((self.root / 'platform/deployment/toolchain-pins.json').read_text())
        item = pins['archives'][0]
        algorithm, digest = toolchain.integrity(item)
        cache = self.root / 'platform/deployment/.local/kdg-toolchain-downloads'
        cache.mkdir(mode=0o700)
        entry = cache / (item['id'] + '-' + digest.hex() + '.archive')
        entry.write_bytes(b'corrupt')
        entry.chmod(0o600)
        with self.assertRaises(dev.Refusal) as error:
            toolchain.verified_archive(item, cache)
        self.assertEqual(error.exception.code, 'archive_digest_mismatch')
        result = self.cli()
        self.assertEqual(json.loads(result.stdout)['code'], 'archive_digest_mismatch')
        self.assertEqual(list((self.run / 'payload').iterdir()), [])
        self.assertFalse((self.run / 'receipt.json').exists())

    def test_truncated_download_is_safe_json_refusal(self):
        self.prepare()
        with patch.object(dev, 'ROOT', self.root), patch.object(toolchain.urllib.request, 'urlopen',
                  side_effect=http.client.IncompleteRead(b'sensitive-marker')):
            output = io.StringIO()
            with redirect_stdout(output):
                code = toolchain.main(['qualify', '--target', str(self.target), '--run-id', self.run_id])
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(output.getvalue())['toolchain_ready'])
        self.assertNotIn('sensitive-marker', output.getvalue())

    def test_ancestor_replacement_cannot_redirect_installation_writes(self):
        original_mkdir = os.mkdir
        outside = self.root / 'outside'
        outside.mkdir(mode=0o700)
        fired = False
        def replace_ancestor(path, mode=0o777, *, dir_fd=None):
            nonlocal fired
            if not fired and self.run.parent.is_dir() and str(path) in {str(self.run), self.run_id}:
                fired = True
                self.run.parent.rename(self.root / 'moved-original-tools')
                self.run.parent.symlink_to(outside, target_is_directory=True)
            return original_mkdir(path, mode, dir_fd=dir_fd)
        with patch.object(os, 'mkdir', side_effect=replace_ancestor):
            with self.assertRaises((dev.Refusal, OSError)):
                self.unit_install()
        self.assertTrue(fired)
        self.assertEqual(list(outside.iterdir()), [])

    def controlled_execution(self, settings):
        """Controlled subprocess protocol model, never actual tool-version evidence."""
        payload = self.root / ('execution-' + uuid.uuid4().hex)
        state = self.root / ('state-' + uuid.uuid4().hex)
        state.mkdir(mode=0o700)
        body = r'''
import sys
from pathlib import Path
args = sys.argv[1:]
if role == 'node':
    if args == ['--version']:
        print(settings.get('node_version', 'v26.11.1'))
    elif args[0].endswith('npm-cli.js'):
        print('12.2.0')
    elif '--version' in args:
        print('Version 7.0.2')
    else:
        assert '--typeRoots' in args
        roots = Path(args[args.index('--typeRoots') + 1])
        assert not list(roots.iterdir())
        if args[-1].endswith('invalid.ts'):
            print(settings.get('diagnostic', 'TS2322'))
            sys.exit(settings.get('invalid_exit', 1))
elif role == 'python':
    print('Python 3.15.0' if '--version' in args else 'qualified')
elif role == 'uv':
    print('uv 0.13.1 (x86_64-unknown-linux-gnu)')
else:
    print('2.120.0')
'''
        for role, name in [('node', 'node/bin/node'), ('python', 'python/bin/python3'),
                           ('uv', 'uv/uv'), ('supabase', 'supabase/supabase')]:
            path = payload / name
            path.parent.mkdir(parents=True)
            path.write_text('#!' + sys.executable + '\nrole=' + repr(role) + '\nsettings=' + repr(settings) + '\n' + body)
            path.chmod(0o700)
        return toolchain.execute(payload, state)

    def test_execute_rejects_wrong_version_exit_and_diagnostic(self):
        self.assertEqual(self.controlled_execution({}), toolchain.expected_checks())
        for settings, code in [({'node_version': 'v24.0.0'}, 'tool_version_mismatch'),
                               ({'invalid_exit': 0}, 'tool_execution_failed'),
                               ({'diagnostic': 'different_failure'}, 'compiler_fixture_failed')]:
            with self.subTest(settings=settings), self.assertRaises(dev.Refusal) as error:
                self.controlled_execution(settings)
            self.assertEqual(error.exception.code, code)

    def test_concurrent_cache_publication_verifies_one_complete_archive(self):
        data = b'synthetic publisher archive'
        digest = hashlib.sha256(data).digest()
        item = {'id': 'node', 'integrity': 'sha256-' + base64.b64encode(digest).decode(),
                'url': 'https://nodejs.org/synthetic'}
        cache = self.root / 'cache'
        cache.mkdir(mode=0o700)
        class Response(io.BytesIO):
            url = item['url']
        original_link = os.link
        def slow_publish(*args, **kwargs):
            original_link(*args, **kwargs)
            time.sleep(0.05)
        with patch.object(toolchain.urllib.request, 'urlopen', side_effect=lambda *a, **k: Response(data)) as request:
            with patch.object(os, 'link', side_effect=slow_publish), ThreadPoolExecutor(max_workers=4) as workers:
                paths = list(workers.map(lambda _: toolchain.verified_archive(item, cache), range(4)))
        self.assertEqual(request.call_count, 1)
        self.assertEqual(len(set(paths)), 1)
        self.assertEqual(paths[0].read_bytes(), data)
        self.assertEqual(paths[0].stat().st_nlink, 1)

    def test_progressing_download_has_total_deadline(self):
        item = {'id': 'node', 'integrity': 'sha256-' + base64.b64encode(b'0' * 32).decode(),
                'url': 'https://nodejs.org/synthetic'}
        cache = self.root / 'cache'
        cache.mkdir(mode=0o700)
        class Response(io.BytesIO):
            url = item['url']
            def read1(self, _):
                return b'progress'
        ticks = iter(range(0, 1000, 40))
        with patch.object(toolchain.time, 'monotonic', side_effect=lambda: next(ticks)), patch.object(
                toolchain.urllib.request, 'urlopen', return_value=Response()):
            with self.assertRaises(dev.Refusal) as error:
                toolchain.verified_archive(item, cache)
        self.assertEqual(error.exception.code, 'download_deadline')

    def test_archive_limits_checked_before_eager_indexing(self):
        class Stream:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def getmembers(self): raise AssertionError('must not eagerly index')
            def __iter__(self):
                for index in range(10):
                    member = tarfile.TarInfo('file' + str(index))
                    member.size = 1
                    yield member
        payload = self.root / 'payload'
        payload.mkdir(mode=0o700)
        with patch.object(toolchain.tarfile, 'open', return_value=Stream()), patch.object(toolchain, 'MAX_EXPANDED', 3):
            with self.assertRaises(dev.Refusal):
                toolchain.extract(self.root / 'unused', {'format': 'tar', 'destination': 'tool', 'strip_prefix': ''}, payload)
        self.assertEqual(list((payload / 'tool').iterdir()), [])

    def test_pinned_directory_path_survives_grandchild_descriptor_closure(self):
        (self.root / 'fixture').write_bytes(b'synthetic')
        fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
        try:
            child = ('import subprocess,sys;'
                     'raise SystemExit(subprocess.run([sys.executable,"-c",'
                     '"import pathlib,sys; assert pathlib.Path(sys.argv[1]).read_bytes()==b\\\"synthetic\\\"",'
                     'sys.argv[1]],close_fds=True).returncode)')
            result = subprocess.run([sys.executable, '-c', child, str(toolchain.descriptor_path(fd) / 'fixture')],
                                    close_fds=True, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
        finally:
            os.close(fd)


if __name__ == '__main__':
    unittest.main()
