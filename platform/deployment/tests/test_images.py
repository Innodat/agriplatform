"""Synthetic metadata qualification; no image pulls, daemon or real data."""
import copy
from contextlib import nullcontext
from concurrent.futures import ThreadPoolExecutor
import json
import multiprocessing
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

from test_dev import FILES

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'platform/deployment'))
import dev
import images
import toolchain


INDEX = 'application/vnd.oci.image.index.v1+json'
MANIFEST = 'application/vnd.oci.image.manifest.v1+json'
CONFIG = 'application/vnd.oci.image.config.v1+json'
LAYER = 'application/vnd.oci.image.layer.v1.tar+gzip'


def encoded(value):
    return json.dumps(value, sort_keys=True).encode()


def fixture(seed='postgres'):
    child = encoded({'schemaVersion': 2, 'mediaType': MANIFEST,
                     'config': {'mediaType': CONFIG, 'digest': 'sha256:' + dev.digest(seed.encode()), 'size': 200},
                     'layers': [{'mediaType': LAYER, 'digest': 'sha256:' + '2' * 64, 'size': 500}]})
    index = encoded({'schemaVersion': 2, 'mediaType': INDEX, 'manifests': [
        {'mediaType': MANIFEST, 'digest': 'sha256:' + dev.digest(child), 'size': len(child),
         'platform': {'os': 'linux', 'architecture': 'amd64'}}]})
    return index, child


def response(raw, media):
    return 200, {'content-type': media, 'docker-content-digest': 'sha256:' + dev.digest(raw)}, raw


def services(pins):
    return encoded([{'name': row['cli_service'], 'local': row['tag'], 'remote': ''}
                    for row in pins['images'] if row['cli_service'] is not None])


def manifest_responses(pins):
    result = {}
    for item in pins['images']:
        index, child = fixture(item['id'])
        prefix = '/v2/' + item['repository'] + '/manifests/'
        result[prefix + item['tag']] = response(index, INDEX)
        result[prefix + 'sha256:' + dev.digest(child)] = response(child, MANIFEST)
    return result


class PublicAcceptance(unittest.TestCase):
    def test_public_missing_preparation_refuses_safely(self):
        result = subprocess.run([
            sys.executable, str(ROOT / 'platform/deployment/images.py'), 'qualify',
            '--target', str(ROOT / 'platform/deployment/environments/kdg-local.json'),
            '--run-id', str(uuid.uuid4())],
            capture_output=True, text=True, cwd='/tmp')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, '')
        data = json.loads(result.stdout)
        self.assertFalse(data['ok'])
        self.assertFalse(data['runtime_ready'])
        self.assertEqual(data['code'], 'prepared_run_required')

    def test_unknown_argument_invalid_uuid_and_help_are_safe(self):
        for args in [['--help'], ['qualify', '--target', 'sensitive-marker', '--run-id', '../bad'],
                     ['qualify', '--target', 'sensitive-marker', '--run-id', str(uuid.uuid4()), '--bad']]:
            result = subprocess.run([sys.executable, str(ROOT / 'platform/deployment/images.py'), *args],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stderr, '')
            self.assertNotIn('sensitive-marker', result.stdout)
            self.assertFalse(json.loads(result.stdout)['runtime_ready'])


class MetadataGuards(unittest.TestCase):
    def setUp(self):
        self.pins = images.load_pins(dev.read(ROOT / images.PINS))

    def refused(self, call, code=None):
        with self.assertRaises(dev.Refusal) as caught:
            call()
        if code:
            self.assertEqual(caught.exception.code, code)

    def test_exact_catalogue_rejects_every_changed_field_and_booleans(self):
        for field in self.pins:
            value = copy.deepcopy(self.pins)
            value[field] = None
            self.refused(lambda: images.load_pins(encoded(value)), 'invalid_selection')
        for mutate in [lambda p: p.update(schema_version=True),
                       lambda p: p['images'][0].update(repository='mirror/postgres'),
                       lambda p: p['images'][0].update(tag='latest'),
                       lambda p: p['images'].append(p['images'][0]),
                       lambda p: p['policy'].update(slim=True)]:
            value = copy.deepcopy(self.pins)
            mutate(value)
            self.refused(lambda: images.load_pins(encoded(value)), 'invalid_selection')

    def test_collect_only_eight_exact_manifest_requests_no_blobs(self):
        expected = manifest_responses(self.pins)
        calls = []
        def request(path, headers, limit, deadline):
            calls.append((path, headers, limit))
            self.assertNotIn('/blobs/', path)
            self.assertNotIn('Authorization', headers)
            return expected[path]
        with patch.object(images, 'https', side_effect=request):
            artifacts, records = images.collect(self.pins)
        self.assertEqual(len(calls), 8)
        self.assertEqual(len(artifacts), 8)
        self.assertEqual([r['id'] for r in records], [r['id'] for r in self.pins['images']])
        self.assertEqual([p for p, _, _ in calls], list(expected))
        for item, record in zip(self.pins['images'], records):
            index, child = fixture(item['id'])
            self.assertEqual(artifacts[item['id'] + '-index.json'], index)
            self.assertEqual(artifacts[item['id'] + '-linux-amd64.json'], child)
            self.assertEqual(record['index']['digest'], 'sha256:' + dev.digest(index))
            self.assertEqual(record['linux_amd64']['digest'], 'sha256:' + dev.digest(child))

    def test_auth_token_memory_only_and_scope_realm_are_exact(self):
        index, _ = fixture()
        challenge = {'www-authenticate': 'Bearer realm="https://public.ecr.aws/token/",service="public.ecr.aws",scope="aws"'}
        calls = []
        def request(path, headers, limit, deadline):
            calls.append((path, dict(headers)))
            if len(calls) == 1:
                return 401, challenge, b''
            if len(calls) == 2:
                return 200, {'content-type': 'application/json'}, b'{"token":"sensitive-marker"}'
            self.assertEqual(headers['Authorization'], 'Bearer sensitive-marker')
            return response(index, INDEX)
        with patch.object(images, 'https', side_effect=request):
            raw, _, _ = images.Registry().manifest('supabase/postgres', '17.11.0.004')
        self.assertNotIn(b'sensitive-marker', raw)
        self.assertTrue(calls[1][0].startswith('/token/?service=public.ecr.aws&scope='))
        for changed in ['https://foreign.invalid/token/', 'http://public.ecr.aws/token/',
                        'https://public.ecr.aws/token/?secret=x']:
            altered = {'www-authenticate': challenge['www-authenticate'].replace('https://public.ecr.aws/token/', changed)}
            with patch.object(images, 'https', return_value=(401, altered, b'')) as network:
                self.refused(lambda: images.Registry().manifest('supabase/postgres', '17.11.0.004'), 'foreign_auth_challenge')
                self.assertEqual(network.call_count, 1)
        altered = {'www-authenticate': challenge['www-authenticate'].replace('scope="aws"', 'scope="repository:supabase/gotrue:pull"')}
        with patch.object(images, 'https', return_value=(401, altered, b'')):
            self.refused(lambda: images.Registry().manifest('supabase/postgres', '17.11.0.004'), 'foreign_auth_challenge')

    def test_redirect_status_digest_header_and_media_refuse_without_fallback(self):
        index, _ = fixture()
        good = response(index, INDEX)
        cases = [(302, {'location': 'https://foreign.invalid'}, b'sensitive-marker'),
                 (404, {}, b'sensitive-marker'), (429, {}, b''),
                 (200, {'content-type': INDEX, 'docker-content-digest': 'sha256:' + 'a' * 64}, index),
                 (200, {**good[1], 'content-type': 'text/plain'}, index),
                 (200, {**good[1], 'content-encoding': 'gzip'}, index)]
        for case in cases:
            with self.subTest(case=case[:2]), patch.object(images, 'https', return_value=case) as network:
                self.refused(lambda: images.Registry().manifest('supabase/postgres', '17.11.0.004'))
                self.assertEqual(network.call_count, 1)
        with patch.object(images, 'https', return_value=good):
            self.refused(lambda: images.Registry().manifest('supabase/postgres', 'sha256:' + 'b' * 64), 'manifest_digest_mismatch')
        with patch.object(images, 'https') as network:
            self.refused(lambda: images.Registry().manifest('mirror/postgres', 'latest'), 'invalid_reference')
            network.assert_not_called()

    def test_absent_digest_header_requires_identical_digest_addressed_root(self):
        index, _ = fixture()
        without_header = (200, {'content-type': INDEX}, index)
        with patch.object(images, 'https', return_value=without_header) as network:
            raw, media, digest = images.Registry().manifest('supabase/postgres', '17.11.0.004')
            self.assertEqual(network.call_count, 2)
            self.assertTrue(network.call_args.args[0].endswith('/manifests/sha256:' + dev.digest(index)))
            self.assertEqual(digest, 'sha256:' + dev.digest(raw))
        with patch.object(images, 'https', side_effect=[without_header, (200, {'content-type': INDEX}, index + b' ')]):
            self.refused(lambda: images.Registry().manifest('supabase/postgres', '17.11.0.004'), 'manifest_digest_mismatch')

    def test_invalid_schema_platform_child_and_config_shapes(self):
        index, child = fixture()
        original = json.loads(index)
        mutations = [lambda x: x.update(schemaVersion=True), lambda x: x.update(schemaVersion=1),
                     lambda x: x.update(mediaType=MANIFEST), lambda x: x.update(manifests=[]),
                     lambda x: x['manifests'][0].update(size=True),
                     lambda x: x['manifests'][0].update(digest='sha256:' + 'A' * 64),
                     lambda x: x['manifests'][0].update(urls=['https://foreign.invalid']),
                     lambda x: x['manifests'][0]['platform'].update(architecture='arm64'),
                     lambda x: x['manifests'][0]['platform'].update(os='windows'),
                     lambda x: x['manifests'][0]['platform'].update(variant='v3'),
                     lambda x: x['manifests'][0]['platform'].update({'os.features': ['special-kernel']}),
                     lambda x: x['manifests'][0]['platform'].update(features=['sse4']),
                     lambda x: x['manifests'].append(copy.deepcopy(x['manifests'][0]))]
        for mutate in mutations:
            value = copy.deepcopy(original)
            mutate(value)
            self.refused(lambda: images.document(encoded(value), INDEX))
        original = json.loads(child)
        for mutate in [lambda x: x.update(config=None), lambda x: x.update(layers=[]),
                       lambda x: x['config'].update(mediaType=LAYER),
                       lambda x: x['layers'][0].update(mediaType='foreign/layer')]:
            value = copy.deepcopy(original)
            mutate(value)
            self.refused(lambda: images.document(encoded(value), MANIFEST))
        self.refused(lambda: images.document(b'x' * (images.LIMITS['manifest_bytes'] + 1), INDEX), 'metadata_too_large')
        with patch.object(images, 'https', return_value=response(child, MANIFEST)):
            self.refused(lambda: images.collect(self.pins), 'platform_index_required')
        value = json.loads(index)
        value['manifests'][0]['size'] += 1
        with patch.object(images, 'https', side_effect=[response(encoded(value), INDEX), response(child, MANIFEST)]):
            self.refused(lambda: images.collect(self.pins), 'child_binding_mismatch')

    def test_unlinked_cli_three_pins_and_no_remote_fields(self):
        self.assertEqual(len(images.check_services(services(self.pins), self.pins)), 3)
        for mutate in [lambda x: x[0].update(remote='sensitive-marker'),
                       lambda x: x[0].update(local='latest'),
                       lambda x: x.append(copy.deepcopy(x[0])), lambda x: x.pop(),
                       lambda x: x[0].update(extra='bad')]:
            value = json.loads(services(self.pins))
            mutate(value)
            self.refused(lambda: images.check_services(encoded(value), self.pins))

    def test_cli_environment_private_socket_and_workdir(self):
        target = dev.decode(dev.read(ROOT / FILES[2]))
        def execute(command, work, env, timeout, limit):
            self.assertEqual(env['DOCKER_HOST'], 'unix://' + str(work / 'no-daemon.sock'))
            self.assertFalse((work / 'no-daemon.sock').exists())
            self.assertNotIn('HOME', env)
            self.assertNotIn('SUPABASE_ACCESS_TOKEN', env)
            self.assertEqual(command[-2:], ['--workdir', work])
            self.assertEqual((work / 'supabase/config.toml').read_bytes(), dev.configuration(target, RUN))
            self.assertEqual((work / 'supabase/config.toml').stat().st_mode & 0o777, 0o600)
            return services(self.pins)
        with patch.object(images, 'bounded_command', side_effect=execute):
            images.capture_services(Path('/never-installed'), target, RUN, self.pins)

    def test_cli_generated_latest_marker_allowed_but_link_and_version_overrides_refuse(self):
        target = dev.decode(dev.read(ROOT / FILES[2]))
        def execute(command, work, env, timeout, limit):
            folder = work / 'supabase/.temp'
            folder.mkdir()
            (folder / 'cli-latest').write_bytes(marker)
            return services(self.pins)
        for marker in [b'', b'v2.121.0', b'2.121.0\n']:
            with patch.object(images, 'bounded_command', side_effect=execute):
                images.capture_services(Path('/never-installed'), target, RUN, self.pins)
        for name in ['project-ref', 'postgres-version', 'gotrue-version', 'postgrest-version']:
            def unsafe(command, work, env, timeout, limit):
                folder = work / 'supabase/.temp'
                folder.mkdir()
                (folder / 'cli-latest').write_bytes(b'')
                (folder / name).write_bytes(b'bad')
                return services(self.pins)
            with patch.object(images, 'bounded_command', side_effect=unsafe):
                self.refused(lambda: images.capture_services(Path('/never-installed'), target, RUN, self.pins), 'cli_state_not_unlinked')
        for mutation in ['symlink-marker', 'symlink-temp', 'bad-marker', 'changed-config', 'dotenv']:
            def unsafe(command, work, env, timeout, limit):
                folder = work / 'supabase/.temp'
                if mutation == 'symlink-temp':
                    folder.symlink_to(work / 'state')
                elif mutation in {'symlink-marker', 'bad-marker'}:
                    folder.mkdir()
                    if mutation == 'symlink-marker':
                        (folder / 'cli-latest').symlink_to(work / 'supabase/config.toml')
                    else:
                        (folder / 'cli-latest').write_bytes(b'sensitive-marker')
                elif mutation == 'changed-config':
                    (work / 'supabase/config.toml').write_bytes(b'changed')
                else:
                    (work / '.env').write_bytes(b'bad')
                return services(self.pins)
            with patch.object(images, 'bounded_command', side_effect=unsafe):
                with self.assertRaises((dev.Refusal, OSError)):
                    images.capture_services(Path('/never-installed'), target, RUN, self.pins)

    def test_worker_bounds_dns_slow_headers_and_total_deadline(self):
        # Keep the production worker; only control the network stages it enters.
        context = multiprocessing.get_context('fork')
        for stage in ['dns', 'headers', 'body']:
            entered = context.Event()
            def stall(*args, **kwargs):
                entered.set()
                time.sleep(5)
            class Response:
                status = 200
                def getheaders(self):
                    return []
                def read(self, limit):
                    stall()
                    return b''
            class Connection:
                def __init__(self, host, timeout):
                    pass
                def request(self, method, path, headers):
                    if stage == 'dns':
                        socket.getaddrinfo('public.ecr.aws', 443)
                def getresponse(self):
                    if stage == 'headers':
                        stall()
                    return Response()
                def close(self):
                    pass
            before = {p.pid for p in multiprocessing.active_children()}
            started = time.monotonic()
            with patch.object(images.http.client, 'HTTPSConnection', Connection), patch.object(images.socket, 'getaddrinfo', side_effect=stall):
                self.refused(lambda: images.https('/v2/x', {}, 100, time.monotonic() + .15), 'metadata_deadline')
            self.assertTrue(entered.is_set(), stage)
            self.assertLess(time.monotonic() - started, 2)
            self.assertEqual({p.pid for p in multiprocessing.active_children()}, before)
        self.refused(lambda: images.https('/v2/x', {}, 100, time.monotonic() - 1), 'metadata_deadline')

    def test_https_worker_rejects_oversize_headers_body_and_duplicate_headers(self):
        class Response:
            status = 200
            def getheaders(self):
                return self.fields
            def read(self, limit):
                return self.body[:limit]
        class Connection:
            def __init__(self, host, timeout):
                self.host = host
            def request(self, method, path, headers):
                if self.host != 'public.ecr.aws' or method != 'GET':
                    raise AssertionError('foreign host or method')
            def getresponse(self):
                return reply
            def close(self):
                pass
        for fields, body in [([('X-Test', 'a' * 17000)], b'{}'),
                             ([('Content-Type', 'x'), ('content-type', 'y')], b'{}'),
                             ([], b'x' * 101)]:
            reply = Response()
            reply.fields, reply.body = fields, body
            with patch.object(images.http.client, 'HTTPSConnection', Connection):
                self.refused(lambda: images.https('/v2/test', {}, 100, time.monotonic() + 1), 'metadata_unavailable')

    def test_bounded_cli_execution_refuses_output_timeout_and_failure_without_child_text(self):
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            for code, timeout, limit in [
                ('import time;time.sleep(5)', .05, 1000),
                ('print("sensitive-marker"*1000)', 1, 100),
                ('raise RuntimeError("sensitive-marker")', 1, 1000)]:
                with self.assertRaises(dev.Refusal) as error:
                    images.bounded_command([sys.executable, '-c', code], work, {'PATH': '/usr/bin:/bin'}, timeout, limit)
                self.assertNotIn('sensitive-marker', error.exception.code)

    def test_continuous_output_uses_only_bounded_pipes_and_cleans_group(self):
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            pidfile = work / 'pid'
            code = ('import os;from pathlib import Path;'
                    'Path("pid").write_text(str(os.getpid()));'
                    '\nwhile True: os.write(1,b"x"*65536);os.write(2,b"y"*65536)')
            original_read, original_popen = os.read, subprocess.Popen
            captured, children = [], []
            def read(fd, amount):
                chunk = original_read(fd, amount)
                if children and fd in {children[0].stdout.fileno(), children[0].stderr.fileno()}:
                    captured.append(len(chunk))
                return chunk
            def popen(*args, **kwargs):
                self.assertEqual(kwargs['stdout'], subprocess.PIPE)
                self.assertEqual(kwargs['stderr'], subprocess.PIPE)
                child = original_popen(*args, **kwargs)
                children.append(child)
                return child
            started = time.monotonic()
            with patch.object(images.subprocess, 'Popen', side_effect=popen), patch.object(images.os, 'read', side_effect=read):
                self.refused(lambda: images.bounded_command([sys.executable, '-c', code], work,
                             {'PATH': '/usr/bin:/bin'}, 3, 1024), 'command_output_too_large')
            self.assertLessEqual(sum(captured), 1025)
            self.assertLess(time.monotonic() - started, 2)
            self.assertIsNotNone(children[0].returncode)
            self.assertTrue(children[0].stdout.closed)
            self.assertTrue(children[0].stderr.closed)
            with self.assertRaises(ProcessLookupError):
                os.killpg(int(pidfile.read_text()), 0)
            self.assertEqual({p.name for p in work.iterdir()}, {'pid'})


RUN = '90f4bedd-27d9-4ed4-8390-0ccc55970ba5'


class PersistenceGuards(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in FILES + ['platform/deployment/images.py', images.PINS,
                             'platform/deployment/toolchain.py', toolchain.PINS]:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, path)
        self.patch_root = patch.object(dev, 'ROOT', self.root)
        self.patch_root.start()
        self.addCleanup(self.patch_root.stop)
        self.target = dev.decode(dev.read(self.root / FILES[2]))
        self.target['workspace_root'] = str(self.root)
        self.target_path = self.root / 'target.json'
        self.raw = encoded(self.target)
        self.target_path.write_bytes(self.raw)
        self.args = SimpleNamespace(target=str(self.target_path), run_id=RUN)
        self.run = self.root / 'platform/deployment/.local/kdg-base-images' / RUN
        with patch.object(dev, 'free_ports', return_value=nullcontext()):
            dev.prepare(self.target, self.raw, RUN, self.target_path, dev.source_evidence())
        self.tools = self.root / 'platform/deployment/.local/kdg-toolchains' / RUN
        self.tools.mkdir(parents=True, mode=0o700)
        self.payload = self.tools / 'payload'
        self.payload.mkdir(mode=0o700)
        self.tool_receipt = self.tools / 'receipt.json'
        self.tool_receipt.write_bytes(encoded({'toolchain_ready': True,
                                              'payload': toolchain.payload_fingerprint(self.payload)}))
        self.tool_receipt.chmod(0o600)
        self.pins = images.load_pins(dev.read(self.root / images.PINS))
        self.owner = patch.object(images, 'existing_tools', return_value=(self.payload, dev.digest(self.tool_receipt.read_bytes())))
        self.owner.start()
        self.addCleanup(self.owner.stop)
        self.cli = patch.object(images, 'capture_services', return_value=services(self.pins))
        self.capture = self.cli.start()
        self.addCleanup(self.cli.stop)
        self.responses = manifest_responses(self.pins)
        def network(path, headers, limit, deadline):
            return self.responses[path]
        self.network_patch = patch.object(images, 'https', side_effect=network)
        self.network = self.network_patch.start()
        self.addCleanup(self.network_patch.stop)

    def qualify(self):
        return images.qualify(self.args)

    def refused(self, code=None):
        with self.assertRaises((dev.Refusal, OSError)) as caught:
            self.qualify()
        if code:
            self.assertEqual(caught.exception.code, code)

    def test_selection_plan_binds_exact_distinct_child_manifests(self):
        result = self.qualify()
        expected = {'public.ecr.aws/' + item['repository'] + ':' + item['tag']:
                    'public.ecr.aws/' + item['repository'] + '@sha256:' + dev.digest(fixture(item['id'])[1])
                    for item in self.pins['images']}
        self.assertEqual(result['selection_plan'], expected)
        self.assertEqual(result['config_plan'], {
            reference: json.loads(fixture(item['id'])[1])['config']['digest']
            for item, reference in zip(self.pins['images'], expected.values())})
        self.assertEqual(len({ref.split('@')[1] for ref in expected.values()}), 4)
        self.network.reset_mock()
        self.capture.reset_mock()
        self.assertEqual(images.qualify(self.args, existing_only=True)['selection_plan'], expected)
        self.network.assert_not_called()
        self.capture.assert_not_called()

    def test_protected_complete_repeat_never_fetches_or_changes_any_evidence(self):
        self.assertFalse(self.qualify()['runtime_ready'])
        self.assertEqual([call.args[0] for call in self.network.call_args_list], list(self.responses))
        receipt = json.loads((self.run / 'receipt.json').read_bytes())
        for item, record in zip(self.pins['images'], receipt['images']):
            index, child = fixture(item['id'])
            self.assertEqual((self.run / record['index']['file']).read_bytes(), index)
            self.assertEqual((self.run / record['linux_amd64']['file']).read_bytes(), child)
            self.assertEqual(record['index']['digest'], 'sha256:' + dev.digest(index))
            self.assertEqual(record['linux_amd64']['digest'], 'sha256:' + dev.digest(child))
        before = {p.name: (p.read_bytes(), p.stat().st_ino, p.stat().st_mtime_ns) for p in self.run.iterdir()}
        self.assertEqual(len(before), 10)
        self.network.reset_mock()
        self.capture.reset_mock()
        self.assertTrue(self.qualify()['base_identities_ready'])
        self.network.assert_not_called()
        self.capture.assert_not_called()
        self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_ino, p.stat().st_mtime_ns) for p in self.run.iterdir()})
        self.assertEqual(self.run.stat().st_mode & 0o777, 0o700)
        for p in self.run.iterdir():
            self.assertEqual(p.stat().st_mode & 0o777, 0o600)
            self.assertNotIn(b'sensitive-marker', p.read_bytes())

    def test_changed_target_preparation_selection_source_and_payload_refuse_before_registry(self):
        self.qualify()
        for path in [self.target_path, self.root / images.PINS, self.root / images.SOURCE,
                     self.root / 'platform/deployment/.local/kdg' / RUN / 'supabase/config.toml', self.tool_receipt]:
            original = path.read_bytes()
            path.write_bytes(original + b' ')
            self.network.reset_mock()
            self.refused()
            self.network.assert_not_called()
            path.write_bytes(original)
        payload_file = self.payload / 'unrecorded'
        payload_file.write_bytes(b'bad')
        payload_file.chmod(0o600)
        self.network.reset_mock()
        self.refused('tool_payload_changed')
        self.network.assert_not_called()

    def test_tamper_modes_symlink_extra_hardlink_and_partial_fail_without_repair(self):
        self.qualify()
        manifest = self.run / 'postgres-index.json'
        original = manifest.read_bytes()
        manifest.write_bytes(original + b' ')
        self.network.reset_mock()
        self.refused('evidence_bytes_changed')
        manifest.write_bytes(original)
        manifest.chmod(0o644)
        self.refused()
        manifest.chmod(0o600)
        manifest.unlink()
        manifest.symlink_to(self.target_path)
        self.refused()
        manifest.unlink()
        manifest.write_bytes(original)
        manifest.chmod(0o600)
        external_link = self.root / 'external-hardlink'
        os.link(manifest, external_link)
        self.refused('unsafe_file')
        external_link.unlink()
        extra = self.run / 'foreign'
        os.link(manifest, extra)
        self.refused('unexpected_evidence_contents')
        extra.unlink()
        extra.write_bytes(b'partial')
        self.refused('unexpected_evidence_contents')
        extra.unlink()
        (self.run / 'receipt.json').unlink()
        self.refused()
        self.network.assert_not_called()
        self.assertFalse((self.run / 'receipt.json').exists())

    def test_timeout_and_interrupted_publication_remain_unqualified(self):
        with patch.object(images, 'collect', side_effect=dev.Refusal('registry', 'metadata_deadline')):
            self.refused('metadata_deadline')
        self.assertFalse((self.run / 'receipt.json').exists())
        self.network.reset_mock()
        self.refused()
        self.network.assert_not_called()

    def test_input_mutation_during_collection_never_publishes_receipt(self):
        original = images.collect
        def change(pins):
            result = original(pins)
            self.target_path.write_bytes(self.raw + b' ')
            return result
        with patch.object(images, 'collect', side_effect=change):
            self.refused()
        self.assertFalse((self.run / 'receipt.json').exists())

    def test_inventory_byte_mutation_during_collection_refuses(self):
        original = images.collect
        def change(pins):
            result = original(pins)
            inventory = self.root / 'platform/deployment/.local/kdg' / RUN / 'inventory.json'
            inventory.write_bytes(inventory.read_bytes() + b' ')
            return result
        with patch.object(images, 'collect', side_effect=change):
            self.refused('qualification_input_changed')
        self.assertFalse((self.run / 'receipt.json').exists())

    def test_output_mode_mutation_during_collection_refuses(self):
        original = images.collect
        def change(pins):
            result = original(pins)
            self.run.chmod(0o777)
            return result
        with patch.object(images, 'collect', side_effect=change):
            self.refused('unprotected_directory')
        self.assertFalse((self.run / 'receipt.json').exists())

    def test_output_ancestor_mode_mutation_during_collection_refuses(self):
        original = images.collect
        def change(pins):
            result = original(pins)
            self.run.parent.parent.chmod(0o777)
            return result
        with patch.object(images, 'collect', side_effect=change):
            self.refused('unprotected_directory')
        self.assertFalse((self.run / 'receipt.json').exists())

    def test_concurrent_writer_cannot_adopt_or_remove_active_lock(self):
        entered, release = threading.Event(), threading.Event()
        original = images.collect
        def wait(pins):
            entered.set()
            self.assertTrue(release.wait(5))
            return original(pins)
        with patch.object(images, 'collect', side_effect=wait), ThreadPoolExecutor(max_workers=1) as pool:
            pending = pool.submit(self.qualify)
            self.assertTrue(entered.wait(5))
            try:
                self.refused()
                self.assertTrue((self.run / '.qualify.lock').exists())
            finally:
                release.set()
            self.assertTrue(pending.result(5)['base_identities_ready'])
        self.assertFalse((self.run / '.qualify.lock').exists())

    def test_replaced_output_inode_and_unsafe_ancestor_refuse(self):
        original = images.collect
        def change(pins):
            result = original(pins)
            self.run.rename(self.run.with_name('displaced'))
            self.run.mkdir(mode=0o700)
            return result
        with patch.object(images, 'collect', side_effect=change):
            self.refused('evidence_directory_changed')
        self.assertFalse((self.run / 'receipt.json').exists())
        self.run.parent.chmod(0o777)
        self.refused('unprotected_directory')

    def test_missing_receipts_do_not_invoke_owner_install_or_registry(self):
        self.owner.stop()
        self.tool_receipt.unlink()
        with patch.object(images, 'bounded_command') as execute:
            self.refused('existing_tools_required')
            execute.assert_not_called()
        self.network.assert_not_called()
        self.assertFalse(self.run.parent.exists())

    def test_real_owner_preflight_success_checks_command_environment_and_preserves_receipt(self):
        self.owner.stop()
        (self.tools / 'state').mkdir(mode=0o700)
        before = (self.tool_receipt.read_bytes(), self.tool_receipt.stat().st_ino)
        expected = {'ok': True, 'stage': 'qualified', 'code': 'toolchain_qualified',
                    'run_id': RUN, 'toolchain_ready': True, 'runtime_ready': False}
        def execute(command, work, env, timeout, limit):
            self.assertEqual(command, [sys.executable, '-B', self.root / 'platform/deployment/toolchain.py',
                                      'qualify', '--target', self.target_path, '--run-id', RUN])
            self.assertEqual(env, {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C.UTF-8', 'PYTHONDONTWRITEBYTECODE': '1'})
            self.assertEqual(timeout, images.LIMITS['owner_seconds'])
            self.assertEqual(limit, images.LIMITS['cli_output_bytes'])
            self.assertEqual(work.stat().st_mode & 0o777, 0o700)
            self.assertEqual(list(work.iterdir()), [])
            return encoded(expected)
        with patch.object(images, 'bounded_command', side_effect=execute) as execute:
            self.assertTrue(self.qualify()['base_identities_ready'])
        self.assertEqual(execute.call_count, 1)
        self.assertEqual((self.tool_receipt.read_bytes(), self.tool_receipt.stat().st_ino), before)

    def test_real_owner_preflight_refused_changed_results_and_receipts_block_registry(self):
        self.owner.stop()
        (self.tools / 'state').mkdir(mode=0o700)
        expected = {'ok': True, 'stage': 'qualified', 'code': 'toolchain_qualified',
                    'run_id': RUN, 'toolchain_ready': True, 'runtime_ready': False}
        for key, value in [('ok', False), ('stage', 'wrong'), ('code', 'wrong'),
                           ('run_id', str(uuid.uuid4())), ('toolchain_ready', False), ('runtime_ready', True)]:
            changed = {**expected, key: value}
            with self.subTest(key=key), patch.object(images, 'bounded_command', return_value=encoded(changed)):
                self.refused('tool_verification_refused')
                self.network.assert_not_called()
                self.assertFalse(self.run.parent.exists())
        for mutation in ['bytes', 'inode', 'exception']:
            original = self.tool_receipt.read_bytes()
            def execute(*args):
                if mutation == 'exception':
                    raise dev.Refusal('images_cli', 'command_refused')
                if mutation == 'inode':
                    self.tool_receipt.rename(self.root / 'original-receipt')
                    self.tool_receipt.write_bytes(original)
                    self.tool_receipt.chmod(0o600)
                else:
                    self.tool_receipt.write_bytes(original + b' ')
                return encoded(expected)
            with self.subTest(mutation=mutation), patch.object(images, 'bounded_command', side_effect=execute):
                self.refused()
                self.network.assert_not_called()
                self.assertFalse(self.run.parent.exists())
            self.tool_receipt.write_bytes(original)

    def test_partial_file_write_is_never_adopted(self):
        original = images.write_at
        def interrupted(fd, name, raw):
            original(fd, name, raw)
            raise OSError('synthetic interruption')
        with patch.object(images, 'write_at', side_effect=interrupted):
            self.refused()
        self.assertEqual(len(list(self.run.iterdir())), 2)
        self.assertTrue((self.run / '.qualify.lock').exists())
        self.assertFalse((self.run / 'receipt.json').exists())
        self.network.reset_mock()
        self.refused()
        self.network.assert_not_called()

    def test_payload_inode_replacement_before_registry_refuses(self):
        def capture(*args):
            self.payload.rename(self.tools / 'old-payload')
            self.payload.mkdir(mode=0o700)
            return services(self.pins)
        with patch.object(images, 'capture_services', side_effect=capture):
            self.refused('qualification_input_changed')
        self.network.assert_not_called()
        self.assertFalse((self.run / 'receipt.json').exists())

    def test_anonymous_tokens_never_persist_in_completed_evidence(self):
        responses = manifest_responses(self.pins)
        def network(path, headers, limit, deadline):
            if path.startswith('/token/'):
                return 200, {'content-type': 'application/json'}, b'{"token":"sensitive-marker"}'
            if not headers.get('Authorization'):
                return 401, {'www-authenticate': 'Bearer realm="https://public.ecr.aws/token/",service="public.ecr.aws",scope="aws"'}, b''
            self.assertEqual(headers['Authorization'], 'Bearer sensitive-marker')
            return responses[path]
        with patch.object(images, 'https', side_effect=network):
            self.qualify()
        for path in self.run.iterdir():
            self.assertNotIn(b'sensitive-marker', path.read_bytes())


class PublicationBoundaries(unittest.TestCase):
    def test_every_failed_publication_boundary_remains_blocked(self):
        boundaries = ['pending-before', 'pending-after', 'link-before', 'link-after',
                      'unlink-pending-before', 'unlink-pending-after', 'fsync-lock',
                      'fsync-pending-file', 'fsync-pending-directory', 'fsync-after-link',
                      'retained-after-link', 'fsync-final', 'unlink-lock-before',
                      'unlink-lock-after', 'fsync-released-lock', 'foreign-receipt',
                      'foreign-pending', 'foreign-lock']
        for boundary in boundaries:
            with self.subTest(boundary=boundary):
                case = PersistenceGuards()
                case.setUp()
                try:
                    write, link, unlink, fsync, retained = (images.write_at, os.link, os.unlink,
                                                           os.fsync, images.retained)
                    fired = False
                    validated = False
                    def fault():
                        nonlocal fired
                        fired = True
                        raise OSError('synthetic publication failure')
                    def write_fault(fd, name, raw):
                        if name == '.receipt-pending' and boundary == 'pending-before' and not fired:
                            fault()
                        write(fd, name, raw)
                        if name == '.receipt-pending' and boundary == 'pending-after' and not fired:
                            fault()
                    def link_fault(src, dst, **kwargs):
                        nonlocal fired
                        if dst == 'receipt.json' and not fired:
                            if boundary == 'foreign-receipt':
                                fired = True
                                write(kwargs['dst_dir_fd'], 'receipt.json', b'foreign-receipt')
                            elif boundary == 'link-before':
                                fault()
                        link(src, dst, **kwargs)
                        if dst == 'receipt.json' and boundary == 'foreign-pending' and not fired:
                            unlink(src, dir_fd=kwargs['src_dir_fd'])
                            write(kwargs['src_dir_fd'], src, b'foreign-pending')
                            fired = True
                        if dst == 'receipt.json' and boundary == 'link-after' and not fired:
                            fault()
                    def unlink_fault(name, **kwargs):
                        stage = 'pending' if name == '.receipt-pending' else 'lock' if name == '.qualify.lock' else ''
                        if boundary == 'unlink-' + stage + '-before' and not fired:
                            fault()
                        unlink(name, **kwargs)
                        if boundary == 'unlink-' + stage + '-after' and not fired:
                            fault()
                    def fsync_fault(fd):
                        target = os.readlink('/proc/self/fd/' + str(fd))
                        pending = (case.run / '.receipt-pending').exists()
                        receipt = (case.run / 'receipt.json').exists()
                        lock = (case.run / '.qualify.lock').exists()
                        point = ('fsync-lock' if target == str(case.run / '.qualify.lock') else
                                 'fsync-pending-file' if target == str(case.run / '.receipt-pending') else
                                 'fsync-pending-directory' if target == str(case.run) and pending and not receipt else
                                 'fsync-released-lock' if target == str(case.run) and receipt and not lock else
                                 'fsync-final' if target == str(case.run) and receipt and validated else
                                 'fsync-after-link' if target == str(case.run) and receipt and not pending else '')
                        if boundary == point and not fired:
                            fault()
                        fsync(fd)
                    def retained_fault(fd, pins, binding, **kwargs):
                        nonlocal validated, fired
                        result = retained(fd, pins, binding, **kwargs)
                        validated = True
                        if boundary == 'retained-after-link' and not fired:
                            fault()
                        if boundary == 'foreign-lock' and not fired:
                            unlink('.qualify.lock', dir_fd=fd)
                            write(fd, '.qualify.lock', b'foreign-lock')
                            fired = True
                        return result
                    with patch.object(images, 'write_at', side_effect=write_fault), \
                         patch.object(images.os, 'link', side_effect=link_fault), \
                         patch.object(images.os, 'unlink', side_effect=unlink_fault), \
                         patch.object(images.os, 'fsync', side_effect=fsync_fault), \
                         patch.object(images, 'retained', side_effect=retained_fault):
                        case.refused()
                    self.assertTrue(fired)
                    self.assertTrue((case.run / '.qualify.lock').exists())
                    if boundary == 'foreign-receipt':
                        self.assertEqual((case.run / 'receipt.json').read_bytes(), b'foreign-receipt')
                    if boundary == 'foreign-lock':
                        self.assertEqual((case.run / '.qualify.lock').read_bytes(), b'foreign-lock')
                    if boundary == 'foreign-pending':
                        self.assertEqual((case.run / '.receipt-pending').read_bytes(), b'foreign-pending')
                    before = {p.name: (p.read_bytes(), p.stat().st_ino) for p in case.run.iterdir()}
                    case.network.reset_mock()
                    case.refused()
                    case.network.assert_not_called()
                    self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_ino) for p in case.run.iterdir()})
                finally:
                    case.doCleanups()

    def test_preexisting_pending_and_stale_lock_are_never_adopted_or_removed(self):
        for name in ['.receipt-pending', '.qualify.lock']:
            with self.subTest(name=name):
                case = PersistenceGuards()
                case.setUp()
                try:
                    case.run.parent.mkdir(mode=0o700)
                    case.run.mkdir(mode=0o700)
                    artifact = case.run / name
                    artifact.write_bytes(b'prior-run')
                    artifact.chmod(0o600)
                    before = (artifact.read_bytes(), artifact.stat().st_ino)
                    case.refused()
                    self.assertEqual((artifact.read_bytes(), artifact.stat().st_ino), before)
                    case.network.assert_not_called()
                    self.assertFalse((case.run / 'receipt.json').exists())
                finally:
                    case.doCleanups()
