"""Boabab private SSH acceptance with no network or root mutations."""
import base64
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
WG = ROOT / 'platform/deployment/wireguard'
sys.path.insert(0, str(WG))
import common
import runner
import peers

KEY = base64.b64encode(bytes(range(32))).decode()
OTHER = base64.b64encode(bytes(range(1, 33))).decode()
THIRD = base64.b64encode(bytes(range(2, 34))).decode()

def inputs():
    return dict(WG_CLIENT_PRIVATE_KEY=KEY, WG_SERVER_PUBLIC_KEY=OTHER,
                WG_ENDPOINT='8.8.8.8:51820', WG_SERVER_ADDRESS='10.77.80.1/32',
                WG_CLIENT_ADDRESS='10.77.80.3/32', DEPLOY_HOST='10.77.80.1',
                DEPLOY_USER='root', SSH_PRIVATE_KEY='fixture-ssh-key',
                SSH_KNOWN_HOSTS='10.77.80.1 ssh-ed25519 fixture')

class Inputs(unittest.TestCase):
    def test_only_server_route(self):
        config = runner.configuration(common.validate_inputs(inputs()))
        self.assertIn('AllowedIPs = 10.77.80.1/32', config)
        self.assertNotIn('0.0.0.0/0', config)
        self.assertNotIn('PostUp', config)
    def test_invalid_inputs_are_safe(self):
        for field, value in [('WG_CLIENT_PRIVATE_KEY','secret-invalid'),
                             ('WG_SERVER_PUBLIC_KEY', KEY[:-1]),
                             ('WG_ENDPOINT','example.org:51820'),
                             ('WG_ENDPOINT','8.8.8.8:22'),
                             ('WG_ENDPOINT','10.1.1.1:51820'),
                             ('WG_ENDPOINT','224.0.0.1:51820'),
                             ('WG_SERVER_ADDRESS','10.77.80.1/24'),
                             ('WG_CLIENT_ADDRESS','10.77.80.1/32'),
                             ('WG_CLIENT_ADDRESS','10.77.81.3/32'),
                             ('WG_CLIENT_ADDRESS','10.77.80.0/32'),
                             ('WG_CLIENT_ADDRESS','10.77.80.255/32'),
                             ('WG_SERVER_ADDRESS','10.77.80.0/32'),
                             ('WG_SERVER_ADDRESS','10.77.80.255/32'),
                             ('DEPLOY_HOST','1.2.3.4'),
                             ('DEPLOY_USER','root;echo secret')]:
            with self.subTest(field=field, value=value):
                env = inputs(); env[field] = value
                with self.assertRaises(common.SafeError) as error:
                    common.validate_inputs(env)
                self.assertNotIn(value, str(error.exception))
    def test_missing_inputs(self):
        with self.assertRaises(common.SafeError): common.validate_inputs({})

class PeerRegistry(unittest.TestCase):
    def setUp(self):
        self.original = f'[Interface]\nPrivateKey = {KEY}\nAddress = 10.77.80.1/24\nListenPort = 51820\n'
    def test_add_replay_remove_preserves_server_and_other_peer(self):
        added = peers.update(self.original, 'add', 'ck-wsl', '10.77.80.2/32', OTHER)
        self.assertTrue(added.startswith(self.original))
        self.assertEqual(added, peers.update(added, 'add', 'ck-wsl', '10.77.80.2/32', OTHER))
        two = peers.update(added, 'add', 'github-production', '10.77.80.3/32', THIRD)
        removed = peers.update(two, 'remove', 'ck-wsl')
        self.assertNotIn(OTHER, removed)
        self.assertIn(THIRD, removed)
        self.assertTrue(removed.startswith(self.original))
        self.assertEqual(removed, peers.update(removed, 'remove', 'ck-wsl'))
    def test_ipv4_path_mtu_1200_is_supported_and_bounded(self):
        config = self.original + 'MTU = 1200\n'
        added = peers.update(config, 'add', 'ck-wsl', '10.77.80.2/32', OTHER)
        self.assertIn('MTU = 1200', added)
        for mtu in (1199, 1421):
            with self.subTest(mtu=mtu):
                with self.assertRaises(common.SafeError):
                    peers.update(self.original + f'MTU = {mtu}\n', 'remove', 'absent')

    def test_conflicts_and_unsafe_config_fail(self):
        added = peers.update(self.original, 'add', 'ck-wsl', '10.77.80.2/32', OTHER)
        cases = [('ck-wsl','10.77.80.3/32',THIRD), ('other','10.77.80.2/32',THIRD),
                 ('other','10.77.80.3/32',OTHER), ('bad id','10.77.80.3/32',THIRD),
                 ('other','10.77.80.1/32',THIRD), ('other','10.77.80.3/24',THIRD), ('other','10.77.81.3/32',THIRD),
                 ('other','10.77.80.0/32',THIRD), ('other','10.77.80.255/32',THIRD)]
        for name, address, key in cases:
            with self.subTest(name=name, address=address):
                with self.assertRaises(common.SafeError): peers.update(added,'add',name,address,key)
        for extra in ['SaveConfig = true\n', 'PostUp = echo secret\n', '[Peer]\nPublicKey = '+OTHER+'\nAllowedIPs = 10.77.80.2/32\n']:
            with self.assertRaises(common.SafeError): peers.update(self.original+extra,'remove','absent')


class RunnerBehavior(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name) / 'state'
        self.calls = []
        self.live = False
        self.interface_alias = None
        self.fail_ssh = False
        self.unowned = False
        self.fail_delete = False
        self.fail_down = False
        self.guard = patch.object(runner, 'protected_state')
        self.guard.start(); self.addCleanup(self.guard.stop)
        self.fake = patch.object(runner, 'command', side_effect=self.command)
        self.fake.start(); self.addCleanup(self.fake.stop)
    def command(self, argv, **kwargs):
        from types import SimpleNamespace
        import json
        self.calls.append(argv)
        if argv[:3] == ['ip','link','add']:
            self.live = True
        if argv[:5] == ['ip','link','set','dev',runner.INTERFACE] and argv[5] == 'alias':
            self.interface_alias = argv[6]
        if argv[:3] == ['ip','link','delete']:
            if self.fail_delete: raise common.SafeError('Fixture command failed')
            self.live = False
        if argv == ['ip','link','set','dev',runner.INTERFACE,'down'] and self.fail_down:
            raise common.SafeError('Fixture down failed')
        if argv[0] == 'ssh' and self.fail_ssh:
            raise common.SafeError('Fixture host key mismatch')
        if argv[:3] == ['ip','-json','link']:
            marker = (self.state / 'owner').read_text()
            # Ubuntu 24.04 ignores alias in link-add; only link-set installs it.
            alias = 'other-owner' if self.unowned else self.interface_alias
            return SimpleNamespace(returncode=0, stdout=json.dumps([{'ifname':runner.INTERFACE,'ifalias':alias}] if self.live else []))
        return SimpleNamespace(returncode=0, stdout='')
    def test_valid_setup_and_teardown_have_single_route_and_strict_ssh(self):
        runner.setup(inputs(), self.state)
        self.assertEqual([call for call in self.calls if call[:3] == ['ip','route','add']],
                         [['ip','route','add','10.77.80.1/32','dev',runner.INTERFACE]])
        self.assertIn(['ip','link','set','dev',runner.INTERFACE,'mtu','1200'],self.calls)
        ssh = next(call for call in self.calls if call[0] == 'ssh')
        self.assertIn('StrictHostKeyChecking=yes', ssh)
        self.assertIn('root@10.77.80.1', ssh)
        self.assertEqual(ssh[-1], 'true')
        for path in self.state.iterdir(): self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        runner.teardown(self.state)
        self.assertFalse(self.live); self.assertFalse(self.state.exists())
        runner.teardown(self.state)
    def test_host_mismatch_cleans_up_without_mutation(self):
        self.fail_ssh = True
        with self.assertRaises(common.SafeError): runner.setup(inputs(), self.state)
        self.assertFalse(self.live); self.assertFalse(self.state.exists())
        self.assertFalse(any('mkdir' in part for call in self.calls for part in call))
    def test_invalid_inputs_have_no_side_effects(self):
        env = inputs(); env['WG_ENDPOINT'] = 'secret-invalid'
        with self.assertRaises(common.SafeError): runner.setup(env, self.state)
        self.assertFalse(self.state.exists()); self.assertEqual(self.calls, [])
    def test_existing_state_is_not_overwritten(self):
        self.state.mkdir(); (self.state/'owner').write_text('previous')
        with self.assertRaises(FileExistsError): runner.setup(inputs(), self.state)
        self.assertEqual((self.state/'owner').read_text(), 'previous')
        self.assertEqual(self.calls, [])
    def test_cleanup_preserves_unowned_interface_and_removes_our_secrets(self):
        runner.setup(inputs(), self.state); self.unowned = True
        with self.assertRaises(common.SafeError): runner.teardown(self.state)
        self.assertTrue(self.live)
        self.assertFalse((self.state/'tunnel.conf').exists())
        self.assertFalse(any(call[:3] == ['ip','link','delete'] for call in self.calls))
        self.assertNotIn(['ip','link','set','dev',runner.INTERFACE,'down'], self.calls)
        self.assertFalse(any(call[:3] == ['ip','route','del'] for call in self.calls))
    def test_cleanup_failure_retains_marker_for_retry_without_secrets(self):
        runner.setup(inputs(), self.state); self.fail_delete = True
        with self.assertRaises(common.SafeError): runner.teardown(self.state)
        self.assertTrue((self.state/'owner').exists())
        self.assertTrue((self.state/'route').exists())
        self.assertIn(['ip','link','set','dev',runner.INTERFACE,'down'], self.calls)
        self.assertIn(['ip','route','del','10.77.80.1/32','dev',runner.INTERFACE], self.calls)
        self.assertFalse((self.state/'ssh_key').exists())
        self.fail_delete = False
        runner.teardown(self.state)
        self.assertFalse(self.state.exists())

    def test_failed_disable_still_attempts_route_removal_and_erases_secrets(self):
        runner.setup(inputs(), self.state)
        self.fail_delete = self.fail_down = True
        with self.assertRaisesRegex(common.SafeError, 'cleanup incomplete'):
            runner.teardown(self.state)
        self.assertIn(['ip','route','del','10.77.80.1/32','dev',runner.INTERFACE], self.calls)
        self.assertTrue((self.state/'owner').exists())
        self.assertFalse((self.state/'tunnel.conf').exists())
        self.assertFalse((self.state/'ssh_key').exists())

class PeerPersistence(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.config = Path(self.temp.name) / 'wg0.conf'
        self.original = f'[Interface]\nPrivateKey = {KEY}\nAddress = 10.77.80.1/24\nListenPort = 51820\n'
        self.config.write_text(self.original); self.config.chmod(0o600)
        self.guard = patch.object(peers, 'protected')
        self.guard.start(); self.addCleanup(self.guard.stop)
        self.commands = patch.object(peers, 'command')
        self.mock_command = self.commands.start(); self.addCleanup(self.commands.stop)
    def test_persisted_add_and_removal_sync_only_selected_interface(self):
        snapshots=[]
        def inspect(argv):
            if argv[1] == 'syncconf':
                path = Path(argv[-1]); snapshots.append(path.read_text())
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                self.assertEqual(argv[2], 'wg0')
        self.mock_command.side_effect = inspect
        self.assertTrue(peers.apply(self.config,'add','ci','10.77.80.3/32',OTHER))
        self.assertEqual(self.config.stat().st_mode & 0o777, 0o600)
        self.assertIn(OTHER,self.config.read_text())
        self.assertNotIn('Address =',snapshots[-1])
        self.assertFalse(peers.apply(self.config,'add','ci','10.77.80.3/32',OTHER))
        self.assertTrue(peers.apply(self.config,'remove','ci'))
        self.assertNotIn(OTHER,self.config.read_text())
        self.assertEqual(len(snapshots),3)
    def test_failed_sync_restores_persistent_and_running_configuration(self):
        synced = []
        def failed_sync_then_recover(argv):
            if argv[1] == 'syncconf':
                synced.append(Path(argv[-1]).read_text())
                if len(synced) == 1: raise common.SafeError('Fixture failure')
        self.mock_command.side_effect = failed_sync_then_recover
        with self.assertRaisesRegex(common.SafeError,'previous configuration restored'):
            peers.apply(self.config,'add','ci','10.77.80.3/32',OTHER)
        self.assertEqual(self.config.read_text(),self.original)
        self.assertEqual(len(synced), 2)
        self.assertEqual(synced[1], peers.stripped(self.original))
        self.assertNotIn(OTHER, synced[1])
        self.assertEqual(list(self.config.parent.glob('.sync-*')),[])
        self.assertEqual(list(self.config.parent.glob('.agriplatform-*')),[])
    def test_failure_after_atomic_replace_restores_saved_config(self):
        original_write = peers.atomic_write
        calls = []
        def fail_after_replace(path, text):
            original_write(path, text)
            calls.append(text)
            if len(calls) == 1: raise OSError('fixture directory fsync failure')
        with patch.object(peers, 'atomic_write', side_effect=fail_after_replace):
            with self.assertRaisesRegex(common.SafeError, 'previous configuration restored'):
                peers.apply(self.config,'add','ci','10.77.80.3/32',OTHER)
        self.assertEqual(self.config.read_text(), self.original)

    def test_recovery_failure_is_explicit_and_preserves_saved_config(self):
        self.mock_command.side_effect = [None, common.SafeError('Fixture failure'), common.SafeError('Fixture failure')]
        with self.assertRaisesRegex(common.SafeError,'live recovery is required'):
            peers.apply(self.config,'add','ci','10.77.80.3/32',OTHER)
        self.assertEqual(self.config.read_text(),self.original)
    def test_invalid_request_does_not_write_or_sync(self):
        with self.assertRaises(common.SafeError): peers.apply(self.config,'add','ci','10.77.80.1/32',OTHER)
        self.assertEqual(self.config.read_text(),self.original)
        self.mock_command.assert_not_called()
    def test_stopped_interface_does_not_mutate_config(self):
        self.mock_command.side_effect = common.SafeError('Fixture inactive')
        with self.assertRaises(common.SafeError): peers.apply(self.config,'add','ci','10.77.80.3/32',OTHER)
        self.assertEqual(self.config.read_text(),self.original)

class SafeCommands(unittest.TestCase):
    def test_command_errors_never_expose_output(self):
        import subprocess
        result = subprocess.CompletedProcess(['wg'], 1, 'private-secret', 'private-secret')
        with patch.object(common.subprocess,'run',return_value=result) as fake:
            with self.assertRaises(common.SafeError) as caught: common.command(['wg','show'])
            self.assertNotIn('private-secret',str(caught.exception))
            self.assertEqual(fake.call_args.kwargs['timeout'],30)
            self.assertNotIn('shell',fake.call_args.kwargs)

class WorkflowContract(unittest.TestCase):
    def test_runner_wraps_existing_release_and_always_cleans(self):
        text=(ROOT/'.github/workflows/production.yml').read_text()
        self.assertLess(text.index('container_smoke.py'),text.index('runner.py setup'))
        self.assertLess(text.index('runner.py setup'),text.index('ci-deploy.sh'))
        self.assertLess(text.index('ci-deploy.sh'),text.index('runner.py teardown'))
        self.assertIn('if: always()\n        run: sudo python3 platform/deployment/wireguard/runner.py teardown',text)
        self.assertIn('cancel-in-progress: false',text)
        self.assertNotIn('pull_request:',text)
        self.assertIn('WG_CLIENT_PRIVATE_KEY: ${{ secrets.WG_CLIENT_PRIVATE_KEY }}',text)

    def test_manual_connectivity_workflow_has_no_release_actions(self):
        text=(ROOT/'.github/workflows/wireguard-connectivity.yml').read_text()
        self.assertIn('workflow_dispatch:', text)
        self.assertNotIn('push:', text)
        self.assertNotIn('pull_request:', text)
        self.assertIn("if: github.ref == 'refs/heads/main'", text)
        self.assertIn('environment: production', text)
        self.assertIn('group: platform-production', text)
        self.assertIn('cancel-in-progress: false', text)
        self.assertIn('contents: read', text)
        self.assertNotIn('packages: write', text)
        self.assertLess(text.index('runner.py validate'), text.index('runner.py setup'))
        self.assertIn('if: always()\n        run: sudo python3 platform/deployment/wireguard/runner.py teardown', text)
        for forbidden in ('ci-deploy', 'host-release', 'ci-build', 'netlify', 'upload-artifact', 'release.py'):
            self.assertNotIn(forbidden, text)
    def test_deploy_has_bounded_ssh_keepalive(self):
        text=(ROOT/'platform/deployment/ci-deploy.sh').read_text()
        self.assertIn('-o ServerAliveInterval=15', text)
        self.assertIn('-o ServerAliveCountMax=3', text)

class ProtectedFiles(unittest.TestCase):
    def setUp(self):
        from types import SimpleNamespace
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.directory.chmod(0o700)
        self.bad_owner = None
        actual_lstat = Path.lstat
        def metadata(path):
            info = actual_lstat(path)
            return SimpleNamespace(st_mode=info.st_mode, st_uid=1234 if path == self.bad_owner else 0)
        self.metadata = patch.object(Path, 'lstat', metadata)
        self.metadata.start(); self.addCleanup(self.metadata.stop)
    def test_runner_rejects_unsafe_mode_and_owner_without_actions(self):
        state = self.directory / 'state'; state.mkdir(mode=0o700)
        marker = state / 'owner'; marker.write_text('a' * 32)
        secret = state / 'tunnel.conf'; secret.write_text('unchanged-secret')
        for mode, owner in [(0o755, None), (0o700, state)]:
            with self.subTest(mode=mode, owner=owner):
                state.chmod(mode); self.bad_owner = owner
                with patch.object(runner, 'command') as command:
                    with self.assertRaises(common.SafeError): runner.teardown(state)
                    command.assert_not_called()
                self.assertEqual(secret.read_text(), 'unchanged-secret')
                self.assertEqual(marker.read_text(), 'a' * 32)
    def test_runner_rejects_symlink_and_dangling_symlink(self):
        target = self.directory / 'target'; target.mkdir(mode=0o700)
        secret = target / 'tunnel.conf'; secret.write_text('unchanged-secret')
        link = self.directory / 'state'; link.symlink_to(target, target_is_directory=True)
        with patch.object(runner, 'command') as command:
            with self.assertRaises(common.SafeError): runner.teardown(link)
            command.assert_not_called()
        self.assertEqual(secret.read_text(), 'unchanged-secret')
        link.unlink(); link.symlink_to(self.directory / 'absent')
        with self.assertRaises(common.SafeError): runner.teardown(link)
    def test_peer_rejects_unsafe_file_mode_owner_and_symlink_without_commands(self):
        config = self.directory / 'wg0.conf'
        config.write_text('unchanged-config'); config.chmod(0o600)
        for mode, owner in [(0o644, None), (0o600, config)]:
            with self.subTest(mode=mode, owner=owner):
                config.chmod(mode); self.bad_owner = owner
                with patch.object(peers, 'command') as command:
                    with self.assertRaises(common.SafeError): peers.apply(config, 'remove', 'ci')
                    command.assert_not_called()
                self.assertEqual(config.read_text(), 'unchanged-config')
        self.bad_owner = None
        target = self.directory / 'target'; config.rename(target); config.symlink_to(target)
        with patch.object(peers, 'command') as command:
            with self.assertRaises(common.SafeError): peers.apply(config, 'remove', 'ci')
            command.assert_not_called()
        self.assertEqual(target.read_text(), 'unchanged-config')
    def test_peer_rejects_unsafe_parent_before_files_or_commands_change(self):
        config = self.directory / 'wg0.conf'; config.write_text('unchanged-config')
        for mode, owner in [(0o755, None), (0o700, self.directory)]:
            with self.subTest(mode=mode, owner=owner):
                self.directory.chmod(mode); self.bad_owner = owner
                with patch.object(peers, 'command') as command:
                    with self.assertRaises(common.SafeError): peers.apply(config, 'remove', 'ci')
                    command.assert_not_called()
                self.assertEqual(config.read_text(), 'unchanged-config')
                self.assertFalse(config.with_suffix('.lock').exists())
        self.bad_owner = None; self.directory.chmod(0o700)
        link = self.directory / 'linked'; link.symlink_to(self.directory, target_is_directory=True)
        with self.assertRaises(common.SafeError): peers.apply(link / 'wg0.conf', 'remove', 'ci')

if __name__ == '__main__': unittest.main()
