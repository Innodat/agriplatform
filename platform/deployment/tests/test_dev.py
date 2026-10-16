"""Public CLI acceptance/guard tests; all writes use a copied synthetic workspace."""
import copy
import base64
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

ROOT = Path(__file__).resolve().parents[3]
FILES = [
    'platform/deployment/dev.py',
    'platform/deployment/schema/development-target-v1.json',
    'platform/deployment/environments/kdg-local.json',
    'platform/deployment/fixtures/kdg-synthetic-v1.json',
    'platform/deployment/registry.json',
    'platform/docs/architecture/contracts/scaffold-environment-and-generation.md',
    'platform/deployment/resources.py',
    'platform/deployment/tests/qualify_resources.py',
    'platform/deployment/networks.py',
    'platform/deployment/daemon_images.py',
    'platform/deployment/tests/qualify_daemon_images.py',
    'platform/deployment/volumes.py',
    'platform/deployment/tests/qualify_volumes.py',
    'platform/deployment/startup.py',
    'platform/deployment/create_profile.py',
    'platform/deployment/startup_lifecycle.py',
    'platform/deployment/fixtures/supabase-pg17-lifecycle.md',
    'platform/deployment/fixtures/supabase-pg17-bootstrap.txt',
    'platform/deployment/fixtures/supabase-pg17-profile.md',
    'platform/deployment/tests/qualify_networks.py',
    'platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md',
]


class PreparationAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in FILES:
            source = ROOT / name
            if source.exists():
                destination = self.root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
        sample = self.root / FILES[2]
        self.target = json.loads(sample.read_text()) if sample.exists() else {}
        self.target['workspace_root'] = str(self.root)
        self.input = self.root / 'target.json'
        self.run_id = str(uuid.uuid4())
        self.run = self.root / 'platform/deployment/.local/kdg' / self.run_id

    def invoke(self, command='prepare', target=None, extra=()):
        self.input.write_text(json.dumps(self.target if target is None else target))
        return subprocess.run([sys.executable, str(self.root / FILES[0]), command,
                               '--target', str(self.input), '--run-id', self.run_id, *extra],
                              capture_output=True, text=True, cwd='/tmp')

    def refused(self, result, stage=None, code=None):
        self.assertNotEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertFalse(data['ok'])
        self.assertEqual(result.stderr, '')
        self.assertNotIn('sensitive-marker', result.stdout)
        if stage is not None:
            self.assertEqual(data['stage'], stage)
        if code is not None:
            self.assertEqual(data['code'], code)

    def test_prepare_repeat_binds_sources_and_stays_unqualified(self):
        first = self.invoke()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        inventory = self.run / 'inventory.json'
        original = inventory.read_bytes()
        data = json.loads(original)
        self.assertFalse(data['runtime_ready'])
        self.assertEqual(data['run_id'], self.run_id)
        self.assertEqual(set(data['identities']['containers']), {'identity', 'access', 'kdg_capture'})
        self.assertIn('baseline_sha256', data)
        self.assertEqual(inventory.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.run.stat().st_mode & 0o777, 0o700)
        self.assertEqual(self.invoke().returncode, 0)
        self.assertEqual(inventory.read_bytes(), original)
        source = self.root / FILES[-1]
        source.write_text(source.read_text() + '\nchanged\n')
        self.refused(self.invoke())
        self.assertEqual(inventory.read_bytes(), original)

    def test_closed_input_adversaries_refused_before_run_write(self):
        mutations = [lambda x: x.pop('owner_ids'),
                     lambda x: x.update(unknown='sensitive-marker'),
                     lambda x: x.update(schema_version=True),
                     lambda x: x.update(environment_kind='production'),
                     lambda x: x.update(owner_ids=['identity', 'access', 'people']),
                     lambda x: x.update(workspace_root='/tmp/foreign'),
                     lambda x: x['ports'].update(web=True),
                     lambda x: x['ports'].update(web=5189),
                     lambda x: x['origins'].append('https://sensitive-marker.supabase.co'),
                     lambda x: x.update(fixture_ref='../sensitive-marker'),
                     lambda x: x.update(secret_refs=['sensitive-marker']),
                     lambda x: x.update(project_id_prefix='foreign')]
        for mutate in mutations:
            target = copy.deepcopy(self.target)
            mutate(target)
            with self.subTest(target=target):
                self.refused(self.invoke(target=target))
                self.assertFalse(self.run.exists())

    def test_duplicate_key_invalid_uuid_and_unknown_cli_safe(self):
        self.input.write_text('{"schema_version":1,"schema_version":1,"secret":"sensitive-marker"}')
        args = [sys.executable, str(self.root / FILES[0]), 'prepare', '--target', str(self.input), '--run-id', self.run_id]
        self.refused(subprocess.run(args, capture_output=True, text=True))
        self.run_id = '../sensitive-marker'
        self.refused(self.invoke())
        self.run_id = str(uuid.uuid4()).upper()
        self.refused(self.invoke())
        self.refused(self.invoke(extra=['--sensitive-marker']))

    def test_foreign_run_and_unexpected_inventory_files_refused(self):
        self.run.mkdir(parents=True)
        (self.run / 'foreign').write_text('untouched')
        self.refused(self.invoke())
        self.assertEqual((self.run / 'foreign').read_text(), 'untouched')

    def test_changed_target_refuses_reuse(self):
        self.assertEqual(self.invoke().returncode, 0)
        original = (self.run / 'inventory.json').read_bytes()
        target = copy.deepcopy(self.target)
        target['environment_kind'] = 'ci_disposable'
        self.refused(self.invoke(target=target))
        self.assertEqual((self.run / 'inventory.json').read_bytes(), original)

    def test_symlink_target_source_and_run_ancestor_refused(self):
        self.input.write_text(json.dumps(self.target))
        linked = self.root / 'linked.json'
        linked.symlink_to(self.input)
        self.refused(subprocess.run([sys.executable, str(self.root / FILES[0]), 'prepare', '--target', str(linked), '--run-id', self.run_id], capture_output=True, text=True))
        source = self.root / FILES[-1]
        real = source.with_suffix('.real')
        source.rename(real)
        source.symlink_to(real)
        self.refused(self.invoke())
        source.unlink()
        real.rename(source)
        outside = self.root / 'outside'
        outside.mkdir()
        (self.root / 'platform/deployment/.local').symlink_to(outside, target_is_directory=True)
        self.refused(self.invoke())
        self.assertEqual(list(outside.iterdir()), [])

    def test_occupied_port_refuses_before_run_write(self):
        for family, host, port in [(socket.AF_INET, '127.0.0.1', 5188),
                                   (socket.AF_INET6, '::1', 55482)]:
            with self.subTest(host=host, port=port), socket.socket(family) as listener:
                if family == socket.AF_INET6:
                    listener.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                listener.bind((host, port))
                listener.listen()
                self.refused(self.invoke(), 'ports', 'port_unavailable')
            self.assertFalse(self.run.exists())

    def test_undelivered_commands_fail_without_mutation(self):
        # up now has dedicated read-only prerequisite acceptance in test_docker_gate.
        for command in ['verify', 'stop']:
            self.refused(self.invoke(command), command, 'runtime_adapter_unqualified')
        self.refused(self.invoke('reset'), 'confirmation', 'target_confirmation_required')
        self.refused(self.invoke('reset', extra=['--confirm-target', 'foreign']),
                     'confirmation', 'target_confirmation_required')
        self.refused(self.invoke('reset', extra=['--confirm-target', 'kdg-local']),
                     'reset', 'runtime_adapter_unqualified')
        self.assertFalse(self.run.exists())
        self.assertEqual(self.invoke().returncode, 0)
        original = (self.run / 'inventory.json').read_bytes()
        for command in ['verify', 'stop', 'reset']:
            self.refused(self.invoke(command, extra=['--confirm-target', 'kdg-local'] if command == 'reset' else []),
                         command, 'runtime_adapter_unqualified')
            self.assertEqual((self.run / 'inventory.json').read_bytes(), original)

    def test_all_source_changes_refuse_reuse(self):
        self.assertEqual(self.invoke().returncode, 0)
        original = (self.run / 'inventory.json').read_bytes()
        for name in [FILES[1], FILES[3], FILES[4]]:
            source = self.root / name
            before = source.read_bytes()
            source.write_bytes(before + b'\n')
            self.refused(self.invoke())
            self.assertEqual((self.run / 'inventory.json').read_bytes(), original)
            source.write_bytes(before)
        target = copy.deepcopy(self.target)
        target['secret_refs'][0] = 'sensitive-marker'
        self.refused(self.invoke(target=target))
        self.assertEqual((self.run / 'inventory.json').read_bytes(), original)

    def test_tampering_permissions_and_inventory_symlink_refused(self):
        self.assertEqual(self.invoke().returncode, 0)
        inventory = self.run / 'inventory.json'
        original = inventory.read_bytes()
        tampered = json.loads(original)
        tampered['identities']['project'] = 'foreign'
        inventory.write_text(json.dumps(tampered))
        self.refused(self.invoke())
        inventory.write_bytes(original)
        inventory.chmod(0o644)
        self.refused(self.invoke())
        self.assertEqual(inventory.stat().st_mode & 0o777, 0o644)
        inventory.chmod(0o600)
        self.run.chmod(0o755)
        self.refused(self.invoke())
        self.run.chmod(0o700)
        inventory.unlink()
        outside = self.root / 'outside-inventory'
        outside.write_bytes(original)
        inventory.symlink_to(outside)
        self.refused(self.invoke())
        self.assertTrue(inventory.is_symlink())
        self.assertEqual(outside.read_bytes(), original)

    def test_concurrent_same_run_never_replaces_inventory(self):
        self.input.write_text(json.dumps(self.target))
        args = [sys.executable, str(self.root / FILES[0]), 'prepare', '--target', str(self.input), '--run-id', self.run_id]
        processes = [subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(4)]
        results = [process.communicate(timeout=15) for process in processes]
        self.assertTrue(any(process.returncode == 0 for process in processes), results)
        for process, (out, err) in zip(processes, results):
            self.assertEqual(err, '')
            self.assertEqual(json.loads(out)['ok'], process.returncode == 0)
        self.assertEqual(set(path.name for path in self.run.iterdir()), {'inventory.json', 'supabase'})
        before = (self.run / 'inventory.json').read_bytes()
        self.assertEqual(self.invoke().returncode, 0)
        self.assertEqual((self.run / 'inventory.json').read_bytes(), before)

    def test_target_traversal_and_source_ancestor_symlink_refused(self):
        self.input.write_text(json.dumps(self.target))
        args = [sys.executable, str(self.root / FILES[0]), 'prepare', '--target', str(self.root / 'missing/../target.json'), '--run-id', self.run_id]
        self.refused(subprocess.run(args, capture_output=True, text=True))
        source = self.root / 'platform/docs'
        moved = self.root / 'moved-docs'
        source.rename(moved)
        source.symlink_to(moved, target_is_directory=True)
        self.refused(self.invoke())
        self.assertFalse(self.run.exists())

    def test_inventory_boolean_number_substitution_refused(self):
        self.assertEqual(self.invoke().returncode, 0)
        inventory = self.run / 'inventory.json'
        original = inventory.read_bytes()
        for field, value in [('schema_version', True), ('runtime_ready', 0)]:
            with self.subTest(field=field):
                tampered = json.loads(original)
                tampered[field] = value
                inventory.write_text(json.dumps(tampered))
                self.refused(self.invoke(), 'inventory', 'prepared_input_changed')
                self.assertEqual(json.loads(inventory.read_bytes())[field], value)
        inventory.write_bytes(original)
        self.assertEqual(self.invoke().returncode, 0)

    def test_malformed_schema_refuses_without_traceback_or_run(self):
        schema = self.root / FILES[1]
        for malformed in [[], '', None, True]:
            schema.write_text(json.dumps(malformed))
            self.refused(self.invoke(), 'schema', 'unsupported_schema')
            self.assertFalse(self.run.exists())

    def test_writable_output_ancestors_refused_before_run_write(self):
        local = self.root / 'platform/deployment/.local'
        local.mkdir(mode=0o755)
        local.chmod(0o777)
        self.refused(self.invoke(), 'inventory', 'unprotected_directory')
        self.assertEqual(list(local.iterdir()), [])
        local.chmod(0o755)
        kdg = local / 'kdg'
        kdg.mkdir(mode=0o700)
        kdg.chmod(0o777)
        self.refused(self.invoke(), 'inventory', 'unprotected_directory')
        self.assertEqual(list(kdg.iterdir()), [])
        kdg.chmod(0o700)
        self.assertEqual(self.invoke().returncode, 0)

    def test_reserved_resource_names_are_exact_and_disjoint_between_runs(self):
        names = []
        for run_id in [self.run_id, str(uuid.uuid4())]:
            self.run_id = run_id
            self.assertEqual(self.invoke().returncode, 0)
            inventory = self.root / 'platform/deployment/.local/kdg' / run_id / 'inventory.json'
            data = json.loads(inventory.read_bytes())
            token = base64.urlsafe_b64encode(uuid.UUID(run_id).bytes).decode().rstrip('=')
            project = 'agriplatform-kdg-' + token
            expected = {'project': project, 'network': project + '-network',
                        'volumes': {'database': 'supabase_db_' + project},
                        'containers': {owner: project + '-' + owner for owner in self.target['owner_ids']}}
            self.assertEqual(data['identities'], expected)
            names.append({project, expected['network'], *expected['volumes'].values(),
                          *expected['containers'].values()})
        self.assertTrue(names[0].isdisjoint(names[1]))
