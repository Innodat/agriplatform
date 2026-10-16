"""Independent archive and sequence proof for the synthetic start boundary."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dev
import startup
from create_profile_fixtures import (boundary_fixture, expected_request, expected_environment,
                                     test_plan, test_observations, target_fixture, RUN, SYNTHETIC_CLI_SOURCE)

KEY = b'd4dc5b6d4a1d6a10b2c1e76112c994d65db7cec380572cc1839624d4be3fa275'
NAME = 'etc/postgresql-custom/pgsodium_root.key'
ID = 'e' * 64


def archive(**changes):
    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode='w', format=tarfile.USTAR_FORMAT) as tf:
        member = tarfile.TarInfo(changes.pop('name', NAME))
        content = changes.pop('content', KEY)
        member.size = len(content)
        member.mode = 0o644
        for key, value in changes.items(): setattr(member, key, value)
        tf.addfile(member, io.BytesIO(content))
    return out.getvalue()


def prerequisites(f):
    return ([{'kind': 'container_inspect'}] +
            [{'kind': 'image_inspect', 'image_index': i, 'descriptor': f['image_observations'][f['selection_plan'][tag]]}
             for i, tag in enumerate(f['images'])] +
            [{'kind': 'volume_inspect'}, {'kind': 'network_inspect'}, {'kind': 'existing_volume_create_refused'}])


class Lifecycle(unittest.TestCase):
    def fixture(self):
        f = boundary_fixture()
        f['images'] = list(test_plan())
        f['lifecycle'] = True
        return f

    def test_exact_sequence_simulates_create_transfers_then_refuses_start(self):
        f = self.fixture()
        events = prerequisites(f)
        code, output, _ = startup.fixture_command('docker', expected_request(f), f, events, environment=expected_environment(f))
        self.assertEqual(code, 0)
        self.assertEqual(output.strip(), ID)
        self.assertEqual(startup.fixture_command('docker', ['cp', '-', ID+':/'], f, events, archive=archive())[0], 0)
        self.assertEqual(startup.fixture_command('docker', ['start', ID], f, events)[0], 125)
        self.assertEqual([e['kind'] for e in events[-3:]], ['postgres_create', 'secret_transfer', 'postgres_start_refused'])
        self.assertFalse(events[-3]['facts']['create_refused'])
        self.assertNotIn(KEY.decode(), json.dumps(events))

    def test_archive_adversarial_matrix(self):
        import startup_lifecycle as lifecycle
        lifecycle.validate_archive(archive())
        for changes in [dict(content=b'sensitive-canary'), dict(name='../sensitive-canary'),
                        dict(name='/'+NAME), dict(name=NAME+'/'), dict(mode=0o600), dict(uid=1), dict(gid=1),
                        dict(uname='sensitive-canary'), dict(gname='root'), dict(type=tarfile.SYMTYPE, linkname='sensitive-canary'),
                        dict(type=tarfile.LNKTYPE), dict(type=tarfile.DIRTYPE), dict(type=tarfile.XHDTYPE)]:
            with self.subTest(changes=changes), self.assertRaises(dev.Refusal) as caught:
                lifecycle.validate_archive(archive(**changes))
            self.assertNotIn('sensitive-canary', str(caught.exception))
        good = archive()
        import gzip
        for raw in [b'', good[:512], good[:1536], good[:-1], good+b'\0', good+b'\0'*512,
                    good[:1024]+good, gzip.compress(good), good[:800]+b'sensitive-canary'+good[816:],
                    b'sensitive-canary'+good[16:], good[:148]+b'0000000\0'+good[156:]]:
            with self.subTest(length=len(raw)), self.assertRaises(dev.Refusal):
                lifecycle.validate_archive(raw)

    def test_pipe_deadline_size_eof_and_no_regular_input(self):
        import startup_lifecycle as lifecycle
        import threading
        import time
        from unittest.mock import patch
        for content in [archive(), b'x' * (lifecycle.MAX_BYTES+1)]:
            read, write = os.pipe()
            def send():
                try: os.write(write, content)
                finally: os.close(write)
            thread = threading.Thread(target=send)
            thread.start()
            try:
                if len(content) <= lifecycle.MAX_BYTES:
                    self.assertEqual(lifecycle.read_archive(read), content)
                else:
                    with self.assertRaises(dev.Refusal): lifecycle.read_archive(read)
            finally:
                os.close(read)
                thread.join()
        read, write = os.pipe()
        try:
            os.write(write, b'a')
            with patch.object(lifecycle, 'READ_SECONDS', .03), self.assertRaises(dev.Refusal):
                lifecycle.read_archive(read)
        finally:
            os.close(read); os.close(write)
        with tempfile.TemporaryFile() as stream, self.assertRaises(dev.Refusal):
            lifecycle.read_archive(stream.fileno())

    def test_missing_duplicate_reordered_and_unsupported_operations(self):
        f = self.fixture()
        before = prerequisites(f)
        for events in [[], before[:-1], before+[before[-1]], before[1:]+before[:1]]:
            with self.subTest(events=len(events)), self.assertRaises(dev.Refusal):
                startup.fixture_command('docker', expected_request(f), f, events, environment=expected_environment(f))
        events = prerequisites(f)
        startup.fixture_command('docker', expected_request(f), f, events, environment=expected_environment(f))
        created = list(events)
        for args in [['start', ID], ['cp', '-', 'f'*64+':/'], ['cp', '-', ID+':/etc'], ['cp', '-', ID+':/', 'extra'],
                     ['run', 'sensitive-canary'], expected_request(f), ['network', 'inspect', f['network']['Id']]]:
            with self.subTest(command=args[:1]), self.assertRaises(dev.Refusal):
                startup.fixture_command('docker', args, f, list(created), environment=expected_environment(f), archive=archive())
        startup.fixture_command('docker', ['cp', '-', ID+':/'], f, events, archive=archive())
        with self.assertRaises(dev.Refusal):
            startup.fixture_command('docker', ['cp', '-', ID+':/'], f, events, archive=archive())
        startup.fixture_command('docker', ['start', ID], f, events)
        with self.assertRaises(dev.Refusal):
            startup.fixture_command('docker', ['start', ID], f, events)

    def process_source(self):
        suffix = '''result = subprocess.run(['docker',*args], start_new_session=True, capture_output=True, text=True)
container = result.stdout.strip()
from test_startup_lifecycle import archive
result = subprocess.run(['docker','cp','-',container+':/'], input=archive(), start_new_session=True)
if result.returncode: sys.exit(result.returncode)
result = subprocess.run(['docker','start',container], start_new_session=True)
(work/'forbidden_after_start').write_text('cleanup must never run')
sys.exit(result.returncode)
'''
        return SYNTHETIC_CLI_SOURCE.split("code = subprocess.run")[0]+suffix

    def test_process_boundary_lifecycle_and_controls(self):
        source = self.process_source()
        for control in ['lifecycle-positive', 'invalid-lifecycle-target', 'invalid-lifecycle-archive', 'invalid-lifecycle-order']:
            with tempfile.TemporaryDirectory() as temporary:
                executable = Path(temporary)/'synthetic-cli'
                executable.write_text('#!'+sys.executable+'\n'+source)
                executable.chmod(0o700)
                if control == 'lifecycle-positive':
                    result = startup.synthetic_probe(executable, target_fixture(), RUN, control=control,
                                                     selection_plan=test_plan(), image_observations=test_observations())
                    self.assertFalse(result['runtime_ready'])
                    self.assertTrue(result['synthetic_create_acknowledged'])
                else:
                    with self.assertRaises(dev.Refusal) as caught:
                        startup.synthetic_probe(executable, target_fixture(), RUN, control=control,
                                                selection_plan=test_plan(), image_observations=test_observations())
                    self.assertEqual(caught.exception.code, 'expected_lifecycle_rejected')


    def test_invalid_baseline_cannot_qualify_negative_controls(self):
        for mutation in ["input=b''", "input=b'sensitive-canary'", "input=archive(name='../sensitive-canary')"]:
            source = self.process_source().replace('input=archive()', mutation)
            for control in ['invalid-lifecycle-target', 'invalid-lifecycle-archive', 'invalid-lifecycle-order']:
                with self.subTest(mutation=mutation, control=control), tempfile.TemporaryDirectory() as temporary:
                    executable = Path(temporary)/'synthetic-cli'
                    executable.write_text('#!'+sys.executable+'\n'+source)
                    executable.chmod(0o700)
                    with self.assertRaises(dev.Refusal) as caught:
                        startup.synthetic_probe(executable, target_fixture(), RUN, control=control,
                                                selection_plan=test_plan(), image_observations=test_observations())
                    self.assertEqual(caught.exception.code, 'boundary_not_proven')

    def test_socketpair_read_and_stalled_writer(self):
        import socket
        import startup_lifecycle as lifecycle
        from unittest.mock import patch
        left, right = socket.socketpair()
        try:
            right.sendall(archive())
            right.shutdown(socket.SHUT_WR)
            self.assertEqual(lifecycle.read_archive(left.fileno()), archive())
        finally:
            left.close(); right.close()
        left, right = socket.socketpair()
        try:
            right.sendall(b'a')
            with patch.object(lifecycle, 'READ_SECONDS', .03), self.assertRaises(dev.Refusal):
                lifecycle.read_archive(left.fileno())
        finally:
            left.close(); right.close()

    def test_lifecycle_wrong_parent_refuses_before_read_or_signal(self):
        from unittest.mock import patch
        import startup_lifecycle as lifecycle
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            startup.initialize_workdir(work, target_fixture(), RUN)
            startup.install_fixture(work, target_fixture(), RUN, startup.fixture_network(target_fixture(), RUN),
                                    selection_plan=test_plan(), image_observations=test_observations(),
                                    profile_control='lifecycle-positive')
            with patch.object(startup, 'parent_identity', side_effect=dev.Refusal('startup', 'fixture_parent_identity')), \
                    patch.object(lifecycle, 'read_archive') as read, patch.object(startup.signal, 'pidfd_send_signal') as kill:
                self.assertEqual(startup.fixture_main('docker', ['cp', '-', ID+':/'], work, stop_parent=True), 125)
                read.assert_not_called()
                kill.assert_not_called()
            self.assertEqual(startup.decode_fixture(work/'events.json'), [])

    def test_numeric_headers_with_independent_checksums(self):
        import startup_lifecycle as lifecycle
        def changed(offset, value):
            raw = bytearray(archive())
            raw[offset:offset+len(value)] = value
            raw[148:156] = b' ' * 8
            checksum = sum(raw[:512])
            raw[148:156] = ('%06o\0 ' % checksum).encode()
            return bytes(raw)
        for offset, value in [(100, b'\x00000644\0'), (100, b'000\x00644\0'),
                              (100, b'0000644x'), (100, b'\x80'+b'\0'*7),
                              (108, b'-000000\0'), (116, b'0000008\0'),
                              (124, b'0000000010\0x'), (136, b'\0'*12),
                              (329, b'0000001\0'), (337, b'\x80000000\0'),
                              (329, b'\0' + b'000000\0'), (257, b'ustar '),
                              (263, b'01'), (345, b'sensitive-canary'), (156, b'\0')]:
            with self.subTest(offset=offset, value=value), self.assertRaises(dev.Refusal):
                lifecycle.validate_archive(changed(offset, value))
        for offset, value in [(100, b' 000644\0'), (100, b'00000644'),
                              (100, b'0000644 '), (100, b'000644\0 '),
                              (136, b'00000000000\0'), (136, b'77777777777\0'),
                              (329, b'0000000\0'), (337, b'0000000 ')]:
            with self.subTest(offset=offset, value=value):
                lifecycle.validate_archive(changed(offset, value))
        # Checksum formatting itself is validated independently of its value.
        raw = bytearray(archive())
        checksum = sum(raw[:148]) + 8*32 + sum(raw[156:512])
        raw[148:156] = b'\0' + ('%06o' % checksum).encode() + b'\0'
        with self.assertRaises(dev.Refusal): lifecycle.validate_archive(bytes(raw))

    def test_trickling_input_uses_one_total_deadline(self):
        import startup_lifecycle as lifecycle
        from unittest.mock import patch
        from types import SimpleNamespace
        import stat
        # Each chunk is ready in under one second; cumulative time exceeds it.
        with patch.object(lifecycle.os, 'fstat', return_value=SimpleNamespace(st_mode=stat.S_IFIFO)), \
                patch.object(lifecycle.time, 'monotonic', side_effect=[0, .1, .6, 1.1]), \
                patch.object(lifecycle.select, 'select', return_value=([7], [], [])) as ready, \
                patch.object(lifecycle.os, 'read', side_effect=[b'a', b'b', b'']) as read:
            with self.assertRaises(dev.Refusal): lifecycle.read_archive(7)
        self.assertEqual(read.call_count, 2)
        self.assertEqual([round(call.args[3], 1) for call in ready.call_args_list], [.9, .4])

    def test_original_sequence_defects_cannot_qualify_injection(self):
        original = "result = subprocess.run(['docker','cp','-',container+':/'], input=archive(), start_new_session=True)"
        variants = ["result = subprocess.run(['docker','start',container], start_new_session=True)",
                    original.replace("container+':/'", "'f'*64+':/'"),
                    original.replace("container+':/'", "container+':/etc'"),
                    "sys.exit(125)"]
        for replacement in variants:
            for control in ['invalid-lifecycle-target', 'invalid-lifecycle-archive', 'invalid-lifecycle-order']:
                with self.subTest(replacement=replacement, control=control), tempfile.TemporaryDirectory() as temporary:
                    executable = Path(temporary)/'synthetic-cli'
                    executable.write_text('#!'+sys.executable+'\n'+self.process_source().replace(original, replacement))
                    executable.chmod(0o700)
                    with self.assertRaises(dev.Refusal) as caught:
                        startup.synthetic_probe(executable, target_fixture(), RUN, control=control,
                                                selection_plan=test_plan(), image_observations=test_observations())
                    self.assertEqual(caught.exception.code, 'boundary_not_proven')

    def test_duplicate_original_transfer_rejected_before_read_or_injection(self):
        from contextlib import redirect_stderr
        from unittest.mock import patch
        import startup_lifecycle as lifecycle
        for control in ['invalid-lifecycle-target', 'invalid-lifecycle-archive', 'invalid-lifecycle-order']:
            with tempfile.TemporaryDirectory() as temporary:
                work = Path(temporary)
                startup.initialize_workdir(work, target_fixture(), RUN)
                startup.install_fixture(work, target_fixture(), RUN, startup.fixture_network(target_fixture(), RUN),
                                        selection_plan=test_plan(), image_observations=test_observations(), profile_control=control)
                f = startup.decode_fixture(work/'fixture.json')
                events = prerequisites(f)
                startup.fixture_command('docker', expected_request(f), f, events, environment=expected_environment(f))
                startup.fixture_command('docker', ['cp', '-', ID+':/'], f, events, archive=archive())
                (work/'events.json').write_text(json.dumps(events))
                with patch.object(lifecycle, 'read_archive') as read, redirect_stderr(io.StringIO()):
                    self.assertEqual(startup.fixture_main('docker', ['cp', '-', ID+':/'], work, profile_control=control), 125)
                    read.assert_not_called()
                observed = startup.decode_fixture(work/'events.json')
                self.assertEqual(observed[-1]['reason'], 'fixture_refused')
                self.assertNotIn('lifecycle_control_injected', [event['kind'] for event in observed])

    def test_cp_terminal_refusal_kills_parent_before_cleanup(self):
        for control in ['invalid-lifecycle-target', 'invalid-lifecycle-archive', 'invalid-lifecycle-order']:
            source = self.process_source().replace('if result.returncode: sys.exit(result.returncode)',
                "(work/'forbidden_after_cp').write_text('cleanup must never run')\nif result.returncode: sys.exit(result.returncode)")
            with tempfile.TemporaryDirectory() as temporary:
                executable = Path(temporary)/'synthetic-cli'
                executable.write_text('#!'+sys.executable+'\n'+source)
                executable.chmod(0o700)
                # synthetic_probe checks the work directory, so any cleanup sentinel
                # causes contamination refusal instead of successful negative proof.
                with self.assertRaises(dev.Refusal) as caught:
                    startup.synthetic_probe(executable, target_fixture(), RUN, control=control,
                                            selection_plan=test_plan(), image_observations=test_observations())
                self.assertEqual(caught.exception.code, 'expected_lifecycle_rejected')
