"""Public ENV config acceptance in copied synthetic workspaces; no live runtime."""
from contextlib import redirect_stdout
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tomllib
import unittest
from unittest.mock import patch
import uuid

import test_dev

sys.path.insert(0, str(test_dev.ROOT / 'platform/deployment'))
import dev


class RunConfiguration(unittest.TestCase):
    setUp = test_dev.PreparationAcceptance.setUp
    invoke = test_dev.PreparationAcceptance.invoke
    refused = test_dev.PreparationAcceptance.refused

    def prepared(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return self.run / 'supabase/config.toml'

    def test_public_prepare_installs_closed_configuration_and_immutable_binding(self):
        config = self.prepared()
        self.assertTrue(config.is_file(), 'prepare must materialize its run-local config')
        raw = config.read_bytes()
        value = tomllib.loads(raw.decode())
        token = value['project_id'].removeprefix('agriplatform-kdg-')
        self.assertEqual(base64.urlsafe_b64decode(token + '=='), uuid.UUID(self.run_id).bytes)
        self.assertLessEqual(len(value['project_id']), 40)
        self.assertEqual(value['api']['port'], 55481)
        self.assertTrue(value['api']['enabled'])
        self.assertFalse(value['api']['tls']['enabled'])
        self.assertEqual(value['api']['schemas'], [])
        self.assertEqual(value['api']['extra_search_path'], [])
        self.assertFalse(value['api']['auto_expose_new_tables'])
        self.assertEqual(value['db']['port'], 55482)
        self.assertEqual(value['db']['shadow_port'], 55480)
        self.assertEqual(value['db']['major_version'], 17)
        self.assertEqual(value['db']['migrations'], {'enabled': False, 'schema_paths': []})
        self.assertEqual(value['db']['seed'], {'enabled': False, 'sql_paths': []})
        self.assertEqual(value['studio']['port'], 55483)
        self.assertEqual(value['local_smtp']['port'], 55484)
        for name in ['realtime', 'studio', 'local_smtp', 'storage', 'edge_runtime', 'analytics']:
            self.assertFalse(value[name]['enabled'])
        self.assertFalse(value['db']['pooler']['enabled'])
        for name in ['s3_protocol', 'vector', 'analytics']:
            self.assertFalse(value['storage'][name]['enabled'])
        self.assertEqual(value['auth']['site_url'], 'http://localhost:5188')
        self.assertEqual(value['auth']['external_url'], 'http://localhost:55481/auth/v1')
        self.assertEqual(value['auth']['additional_redirect_urls'], ['http://localhost:5188/auth/callback'])
        self.assertTrue(value['auth']['enabled'])
        self.assertTrue(value['auth']['enable_refresh_token_rotation'])
        self.assertFalse(value['auth']['email']['enable_signup'])
        self.assertFalse(value['auth']['sms']['enable_signup'])
        for name in ['enable_signup', 'enable_anonymous_sign_ins', 'enable_manual_linking']:
            self.assertFalse(value['auth'][name])
        inventory = (self.run / 'inventory.json').read_bytes()
        receipt = json.loads(inventory)
        self.assertEqual(receipt['configuration_sha256'], {'supabase/config.toml': hashlib.sha256(raw).hexdigest()})
        self.assertFalse(receipt['runtime_ready'])
        self.assertEqual(receipt['identities']['project'], value['project_id'])
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)
        self.assertEqual(config.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(set(p.name for p in self.run.iterdir()), {'inventory.json', 'supabase'})
        self.assertEqual(set(p.name for p in config.parent.iterdir()), {'config.toml'})
        self.assertEqual(self.invoke().returncode, 0)
        self.assertEqual(config.read_bytes(), raw)
        self.assertEqual((self.run / 'inventory.json').read_bytes(), inventory)

    def test_project_identity_preserves_all_uuid_bits_within_cli_limit(self):
        projects = []
        for run_id in ['00000000-0000-4000-8000-000000000001', '00000000-0000-4000-8000-000000000002']:
            self.run_id = run_id
            self.run = self.root / 'platform/deployment/.local/kdg' / run_id
            config = self.prepared()
            value = tomllib.loads(config.read_text())['project_id']
            projects.append(value)
            self.assertLessEqual(len(value), 40)
            token = value.removeprefix('agriplatform-kdg-')
            self.assertEqual(base64.urlsafe_b64decode(token + '=='), uuid.UUID(run_id).bytes)
        self.assertNotEqual(*projects)

    def test_tampered_config_refuses_repeat_and_startup_before_daemon_without_repair(self):
        config = self.prepared()
        inventory = (self.run / 'inventory.json').read_bytes()
        config.write_text('sensitive-marker = true\n')
        self.refused(self.invoke())
        with patch.object(dev, 'ROOT', self.root), patch.object(dev, 'docker_prerequisite') as probe:
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(dev.main(['up', '--target', str(self.input), '--run-id', self.run_id]), 2)
            probe.assert_not_called()
        self.assertNotIn('sensitive-marker', output.getvalue())
        self.assertEqual(config.read_text(), 'sensitive-marker = true\n')
        self.assertEqual((self.run / 'inventory.json').read_bytes(), inventory)

    def test_missing_extra_unprotected_and_linked_configuration_refuses(self):
        for scenario in ['missing', 'roles', 'migration', 'directory_mode', 'file_mode', 'symlink', 'hardlink', 'directory_link']:
            with self.subTest(scenario=scenario):
                self.run_id = str(uuid.uuid4())
                self.run = self.root / 'platform/deployment/.local/kdg' / self.run_id
                config = self.prepared()
                inventory = (self.run / 'inventory.json').read_bytes()
                outside = self.root / ('outside-' + self.run_id)
                outside.write_text('sensitive-marker')
                if scenario == 'missing':
                    config.unlink()
                elif scenario == 'roles':
                    (config.parent / 'roles.sql').write_text('sensitive-marker')
                elif scenario == 'migration':
                    (config.parent / 'migrations').mkdir()
                elif scenario == 'directory_mode':
                    config.parent.chmod(0o755)
                elif scenario == 'file_mode':
                    config.chmod(0o644)
                elif scenario in ['symlink', 'hardlink']:
                    config.unlink()
                    if scenario == 'symlink':
                        config.symlink_to(outside)
                    else:
                        os.link(outside, config)
                else:
                    config.parent.rename(self.root / ('saved-' + self.run_id))
                    config.parent.symlink_to(self.root, target_is_directory=True)
                def snapshot():
                    entries = [config.parent] if config.parent.is_symlink() else [config.parent, *config.parent.iterdir()]
                    return {str(p): (p.lstat().st_mode, os.readlink(p) if p.is_symlink() else p.read_bytes() if p.is_file() else None)
                            for p in entries}
                rejected = snapshot()
                self.refused(self.invoke())
                self.assertEqual(snapshot(), rejected)
                with patch.object(dev, 'ROOT', self.root), patch.object(dev, 'docker_prerequisite') as probe:
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(dev.main(['up', '--target', str(self.input), '--run-id', self.run_id]), 2)
                    probe.assert_not_called()
                self.assertEqual(snapshot(), rejected)
                self.assertEqual(outside.read_text(), 'sensitive-marker')
                self.assertEqual((self.run / 'inventory.json').read_bytes(), inventory)

    def test_interrupted_inventory_publication_leaves_unadopted_config(self):
        self.input.write_text(json.dumps(self.target))
        with patch.object(dev, 'ROOT', self.root), patch.object(dev.os, 'link', side_effect=OSError('sensitive-marker')):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(dev.main(['prepare', '--target', str(self.input), '--run-id', self.run_id]), 2)
        config = self.run / 'supabase/config.toml'
        self.assertTrue(config.is_file())
        self.assertFalse((self.run / 'inventory.json').exists())
        before = config.read_bytes()
        self.refused(self.invoke())
        self.assertEqual(config.read_bytes(), before)

    def test_fresh_config_is_verified_before_inventory_publication(self):
        install = dev.install_configuration
        def altered(*args):
            install(*args)
            (self.run / 'supabase/config.toml').write_text('changed = true\n')
        self.input.write_text(json.dumps(self.target))
        with patch.object(dev, 'ROOT', self.root), patch.object(dev, 'install_configuration', side_effect=altered):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(dev.main(['prepare', '--target', str(self.input), '--run-id', self.run_id]), 2)
        self.assertFalse((self.run / 'inventory.json').exists())

    def test_directory_or_file_replacement_during_validation_refuses(self):
        for kind in ['directory', 'file']:
            self.run_id = str(uuid.uuid4())
            self.run = self.root / 'platform/deployment/.local/kdg' / self.run_id
            config = self.prepared()
            read = dev.read_at
            replaced = []
            def swap(fd, name, **kwargs):
                raw = read(fd, name, **kwargs)
                if name == 'config.toml' and not replaced:
                    replaced.append(True)
                    if kind == 'directory':
                        config.parent.rename(self.run / 'detached')
                        config.parent.mkdir(mode=0o700)
                    else:
                        config.rename(config.with_suffix('.old'))
                    config.write_text('changed = true\n')
                    config.chmod(0o600)
                return raw
            with patch.object(dev, 'ROOT', self.root), patch.object(dev, 'read_at', side_effect=swap), patch.object(dev, 'docker_prerequisite') as probe:
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(dev.main(['up', '--target', str(self.input), '--run-id', self.run_id]), 2)
                probe.assert_not_called()

    def test_config_write_flush_and_fsync_failures_leave_no_complete_inventory(self):
        fdopen, fsync = dev.os.fdopen, dev.os.fsync
        for fault in ['write', 'flush', 'file_fsync', 'directory_fsync']:
            self.run_id = str(uuid.uuid4())
            self.run = self.root / 'platform/deployment/.local/kdg' / self.run_id
            self.input.write_text(json.dumps(self.target))
            class FaultyOutput:
                def __init__(self, output): self.output = output
                def __enter__(self): return self
                def __exit__(self, *args): return self.output.__exit__(*args)
                def fileno(self): return self.output.fileno()
                def write(self, data):
                    if fault == 'write':
                        self.output.write(data[:10])
                        raise OSError('synthetic')
                    return self.output.write(data)
                def flush(self):
                    if fault == 'flush': raise OSError('synthetic')
                    return self.output.flush()
            def open_output(fd, *args, **kwargs):
                is_config = Path('/proc/self/fd/' + str(fd)).resolve().name == 'config.toml'
                output = fdopen(fd, *args, **kwargs)
                return FaultyOutput(output) if is_config else output
            def sync(fd):
                name = Path('/proc/self/fd/' + str(fd)).resolve().name
                if (fault == 'file_fsync' and name == 'config.toml') or (fault == 'directory_fsync' and name == 'supabase'):
                    raise OSError('synthetic')
                return fsync(fd)
            with patch.object(dev, 'ROOT', self.root), patch.object(dev.os, 'fdopen', side_effect=open_output), patch.object(dev.os, 'fsync', side_effect=sync):
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(dev.main(['prepare', '--target', str(self.input), '--run-id', self.run_id]), 2)
            self.assertFalse((self.run / 'inventory.json').exists())
            before = (self.run / 'supabase/config.toml').read_bytes()
            self.refused(self.invoke())
            self.refused(self.invoke('up'))
            self.assertEqual((self.run / 'supabase/config.toml').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
