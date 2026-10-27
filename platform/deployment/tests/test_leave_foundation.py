"""Synthetic fixture boundaries; real PostgreSQL/Auth proof remains integration evidence."""
import contextlib
import io
import json
import subprocess
import unittest
from unittest.mock import Mock, patch

import dev
import leave_foundation as foundation
import native_cli
import test_native_cli


class FoundationAcceptance(unittest.TestCase):
    def setUp(self):
        fixture = test_native_cli.LeaveNativeAcceptance()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        for name in ['root', 'target', 'target_path', 'run_id', 'run', 'vendor']:
            setattr(self, name, getattr(fixture, name))
        self.assertEqual(fixture.invoke().returncode, 0)

    def call(self, command):
        output = io.StringIO()
        with patch.object(dev, 'ROOT', self.root), contextlib.redirect_stdout(output):
            status = foundation.main([command, '--target', str(self.target_path), '--run-id', self.run_id,
                                      '--supabase', str(self.vendor)])
        self.assertNotIn('credential-sentinel', output.getvalue())
        return status, json.loads(output.getvalue())

    def test_smoke_requires_completed_setup_before_external_commands(self):
        with patch.object(foundation, 'credentials') as credentials, patch.object(native_cli, 'vendor') as vendor:
            status, result = self.call('smoke')
        self.assertEqual(status, 2)
        self.assertEqual(result['code'], 'fixture_not_ready')
        credentials.assert_not_called()
        vendor.assert_not_called()

    def test_changed_marker_and_foreign_target_refuse_before_fixture_writes(self):
        with patch.object(foundation, 'setup') as setup:
            (self.run / 'native.json').write_text('{}')
            self.assertEqual(self.call('setup')[0], 2)
            self.target['environment_kind'] = 'production'
            self.target_path.write_text(json.dumps(self.target))
            self.assertEqual(self.call('setup')[0], 2)
            setup.assert_not_called()
        self.assertFalse((self.run / 'foundation-attempt.json').exists())

    def test_failed_setup_is_preserved_and_refuses_retry_and_smoke(self):
        with patch.object(native_cli, 'vendor'), patch.object(native_cli, 'docker_prerequisite'), \
                patch.object(native_cli, 'network', return_value='a'*64), \
                patch.object(foundation, 'credentials', return_value={'SERVICE_ROLE_KEY': 'credential-sentinel'}), \
                patch.object(foundation, 'auth', side_effect=dev.Refusal('foundation', 'auth_failed')):
            status, result = self.call('setup')
        self.assertEqual(status, 2)
        self.assertEqual(result['code'], 'auth_failed')
        self.assertTrue((self.run / 'foundation-attempt.json').exists())
        self.assertFalse((self.run / 'foundation-ready.json').exists())
        self.assertEqual(self.call('setup')[1]['code'], 'fixture_already_attempted')
        self.assertEqual(self.call('smoke')[1]['code'], 'fixture_not_ready')

    def test_setup_private_accounts_and_separate_sql_credentials(self):
        ids = ['11111111-1111-4111-8111-111111111111', '22222222-2222-4222-8222-222222222222']
        with dev.directory(self.run) as state, patch.object(foundation, 'auth', side_effect=[{'id': i} for i in ids]), \
                patch.object(foundation, 'sql') as sql:
            foundation.setup(self.run, self.target, self.run_id, {'SERVICE_ROLE_KEY': 'credential-sentinel'}, state)
        saved = json.loads((self.run / 'foundation-ready.json').read_text())
        self.assertEqual(saved['status'], 'complete')
        self.assertEqual(len(set(saved['passwords'])), 3)
        self.assertEqual((self.run / 'foundation-ready.json').stat().st_mode & 0o777, 0o600)
        self.assertIsNone(sql.call_args_list[0].kwargs.get('role'))
        self.assertEqual(sql.call_args_list[1].args[3], foundation.ROLES[0])
        self.assertIn('for_profit', sql.call_args_list[1].args[2])
        self.assertIn('ROW LEVEL SECURITY', sql.call_args_list[1].args[2])

    def test_process_errors_timeout_and_oversize_are_safe(self):
        for effect, code in [(subprocess.TimeoutExpired('credential-sentinel', 30), 'command_timeout'),
                             (OSError('credential-sentinel'), 'command_unavailable')]:
            with patch.object(foundation.subprocess, 'run', side_effect=effect):
                with self.assertRaises(dev.Refusal) as failure:
                    foundation.process(['unused'], self.run)
            self.assertEqual(failure.exception.code, code)
            self.assertNotIn('credential-sentinel', str(failure.exception))
        with patch.object(foundation.subprocess, 'run', return_value=subprocess.CompletedProcess([], 7)):
            with self.assertRaises(dev.Refusal) as failure:
                foundation.process(['unused'], self.run)
        self.assertEqual(failure.exception.code, 'command_failed')
        def oversized(arguments, **kwargs):
            kwargs['stdout'].write(b'x' * (dev.LIMIT + 1))
            return subprocess.CompletedProcess(arguments, 0)
        with patch.object(foundation.subprocess, 'run', side_effect=oversized):
            with self.assertRaises(dev.Refusal) as failure:
                foundation.process(['unused'], self.run)
        self.assertEqual(failure.exception.code, 'response_too_large')

    def test_sql_credentials_are_only_sent_on_stdin(self):
        with patch.object(foundation, 'process', return_value=b'1\n') as process:
            self.assertEqual(foundation.sql(self.run, 'container', 'SELECT 1;', foundation.ROLES[1], 'credential-sentinel'), '1')
        args, path, payload = process.call_args.args
        self.assertNotIn('credential-sentinel', ' '.join(args))
        self.assertEqual(payload, b'credential-sentinel\nSELECT 1;')

    def test_fixture_bootstrap_uses_explicit_native_admin_only(self):
        with patch.object(foundation, 'process', return_value=b'') as process:
            foundation.sql(self.run, 'container', 'CREATE ROLE leave_foundation_owner;')
        arguments, path, payload = process.call_args.args
        self.assertEqual(arguments[7:], ['container', 'psql', '-X',
            '-v', 'ON_ERROR_STOP=1', '-At', '-U', 'supabase_admin', '-d', 'postgres'])
        self.assertEqual(path, self.run)
        self.assertEqual(payload, b'CREATE ROLE leave_foundation_owner;')

    def test_permission_probe_catches_only_postgres_insufficient_privilege(self):
        with patch.object(foundation, 'sql', return_value='DO') as sql:
            foundation.expect_permission_denied(self.run, 'container',
                'SET ROLE leave_foundation_owner;', foundation.ROLES[1], 'credential-sentinel')
        statement = sql.call_args.args[2]
        self.assertIn('WHEN insufficient_privilege', statement)
        self.assertIn("EXECUTE 'SET ROLE leave_foundation_owner;'", statement)
        self.assertIn('RAISE EXCEPTION', statement)
        for missing in ['', 'unexpected']:
            with patch.object(foundation, 'sql', return_value=missing):
                with self.assertRaises(dev.Refusal) as failure:
                    foundation.expect_permission_denied(self.run, 'container',
                        'DELETE FROM env_leave_foundation.organizations;', foundation.ROLES[1], 'credential-sentinel')
                self.assertEqual(failure.exception.code, 'permission_denial_unverified')
        for code in ['command_failed', 'command_timeout', 'command_unavailable']:
            with patch.object(foundation, 'sql', side_effect=dev.Refusal('foundation', code)):
                with self.assertRaises(dev.Refusal) as failure:
                    foundation.expect_permission_denied(self.run, 'container',
                        'SET ROLE leave_foundation_owner;', foundation.ROLES[1], 'credential-sentinel')
                self.assertEqual(failure.exception.code, code)

    def test_password_probe_requires_selected_authentication_diagnostic(self):
        def result(code, diagnostic):
            def run(arguments, **kwargs):
                kwargs['stderr'].write(diagnostic)
                return subprocess.CompletedProcess(arguments, code)
            return run
        role = foundation.ROLES[1]
        diagnostic = ('psql: error: connection failed: FATAL:  password authentication failed for user "' + role + '"\n').encode()
        with patch.object(foundation.subprocess, 'run', side_effect=result(2, diagnostic)):
            self.assertEqual(foundation.process(['unused'], self.run, password_rejection_role=role), b'')
        for code, diagnostic in [(2, b'connection refused credential-sentinel'),
                                 (1, diagnostic), (0, b''), (2, b'x' * (dev.LIMIT + 1))]:
            with patch.object(foundation.subprocess, 'run', side_effect=result(code, diagnostic)):
                with self.assertRaises(dev.Refusal) as failure:
                    foundation.process(['unused'], self.run, password_rejection_role=role)
                self.assertNotIn('credential-sentinel', str(failure.exception))

    def ready(self, state):
        (self.run / 'foundation-ready.json').unlink(missing_ok=True)
        accounts = [{'email': i + '@example.invalid', 'password': 'credential-sentinel', 'id': i}
                    for i in ['a', 'b']]
        native_cli.write_private(state, 'foundation-ready.json', json.dumps(dict(status='complete',
            run_id=self.run_id, target_id=self.target['target_id'], accounts=accounts,
            passwords=['a', 'b', 'c'])).encode())

    def signed_in(self):
        return [{'user': {'id': i}, 'access_token': 'credential-sentinel'} for i in ['a', 'b']]

    def test_sign_in_rejections_stop_all_subsequent_probes(self):
        cases = [{'user': {'id': 'foreign'}, 'access_token': 'token'},
                 {'user': {'id': 'a'}}, {'user': {'id': 'a'}, 'access_token': ''}]
        for response in cases:
            with self.subTest(response=response), dev.directory(self.run) as state:
                self.ready(state)
                with patch.object(foundation, 'auth', return_value=response) as auth, \
                        patch.object(foundation, 'sql') as sql:
                    with self.assertRaises(dev.Refusal) as failure:
                        foundation.smoke(self.run, self.target, self.run_id, {'ANON_KEY': 'key'}, state)
                    self.assertEqual(failure.exception.code, 'sign_in_failed')
                    self.assertEqual(auth.call_count, 1)
                    sql.assert_not_called()

    def test_row_and_role_rejections_stop_subsequent_probes(self):
        for observed, flags, code in [('', 't', 'organization_isolation_failed'),
                ('2', 't', 'organization_isolation_failed'), ('1\n2', 't', 'organization_isolation_failed'),
                ('1', 'f', 'runtime_role_unsafe'), ('1', '', 'runtime_role_unsafe')]:
            with self.subTest(observed=observed, flags=flags), dev.directory(self.run) as state:
                self.ready(state)
                with patch.object(foundation, 'auth', side_effect=self.signed_in() + [{}, {}]), \
                        patch.object(foundation, 'sql', side_effect=[observed, flags]) as sql:
                    with self.assertRaises(dev.Refusal) as failure:
                        foundation.smoke(self.run, self.target, self.run_id, {'ANON_KEY': 'key'}, state)
                    self.assertEqual(failure.exception.code, code)
                    self.assertEqual(sql.call_count, 1 if code == 'organization_isolation_failed' else 2)

    def test_smoke_checks_auth_denials_role_flags_and_all_write_denials(self):
        with dev.directory(self.run) as state:
            self.ready(state)
            with patch.object(foundation, 'auth', side_effect=self.signed_in() + [{}, {}]) as auth, \
                    patch.object(foundation, 'sql', side_effect=['1', 't', '', 'DO', 'DO', 'DO', 'DO', 'DO',
                                                               '2', 't', '', 'DO', 'DO', 'DO', 'DO', 'DO']) as sql:
                foundation.smoke(self.run, self.target, self.run_id, {'ANON_KEY': 'key'}, state)
            self.assertEqual(auth.call_args_list[2].kwargs['expected_error'], (422, 'signup_disabled'))
            self.assertEqual(auth.call_args_list[3].kwargs['expected_error'], (400, 'invalid_credentials'))
            self.assertEqual(sql.call_count, 16)
            for offset in [0, 8]:
                for flag in ['rolsuper', 'rolcreatedb', 'rolcreaterole', 'rolbypassrls']:
                    self.assertIn('NOT ' + flag, sql.call_args_list[offset + 1].args[2])
                self.assertTrue(sql.call_args_list[offset + 2].kwargs['expect_password_rejection'])
                for verb, call in zip(['CREATE TABLE', 'SET ROLE', 'INSERT', 'UPDATE', 'DELETE'],
                                      sql.call_args_list[offset + 3:offset + 8]):
                    self.assertIn(verb, call.args[2])

    def test_new_probe_failures_stop_smoke(self):
        for failing_index in range(2, 8):
            with self.subTest(index=failing_index), dev.directory(self.run) as state:
                self.ready(state)
                responses = ['1', 't', '', 'DO', 'DO', 'DO', 'DO', 'DO']
                responses[failing_index] = dev.Refusal('foundation', 'command_failed')
                with patch.object(foundation, 'auth', side_effect=self.signed_in() + [{}, {}]), \
                        patch.object(foundation, 'sql', side_effect=responses) as sql:
                    with self.assertRaises(dev.Refusal) as failure:
                        foundation.smoke(self.run, self.target, self.run_id, {'ANON_KEY': 'key'}, state)
                    self.assertEqual(failure.exception.code, 'command_failed')
                    self.assertEqual(sql.call_count, failing_index + 1)

    def test_auth_denial_probe_failure_stops_before_sql(self):
        for index in [2, 3]:
            with self.subTest(index=index), dev.directory(self.run) as state:
                self.ready(state)
                responses = self.signed_in() + [{}, {}]
                responses[index] = dev.Refusal('foundation', 'auth_denial_unverified')
                with patch.object(foundation, 'auth', side_effect=responses) as auth, \
                        patch.object(foundation, 'sql') as sql:
                    with self.assertRaises(dev.Refusal) as failure:
                        foundation.smoke(self.run, self.target, self.run_id, {'ANON_KEY': 'key'}, state)
                    self.assertEqual(failure.exception.code, 'auth_denial_unverified')
                    self.assertEqual(auth.call_count, index + 1)
                    sql.assert_not_called()

    def test_typed_http_denial_requires_exact_status_and_code(self):
        for expected in [(422, 'signup_disabled'), (400, 'invalid_credentials')]:
            for status, code, accepted in [(expected[0], expected[1], True),
                    (200, expected[1], False), (expected[0], 'other', False),
                    (503, expected[1], False)]:
                with self.subTest(expected=expected, status=status, code=code):
                    connection = Mock()
                    connection.getresponse.return_value.status = status
                    connection.getresponse.return_value.read.return_value = json.dumps(
                        dict(error_code=code, message='credential-sentinel')).encode()
                    with patch.object(foundation.http.client, 'HTTPConnection', return_value=connection):
                        if accepted:
                            foundation.auth(self.target, 'POST', 'signup', 'key', {}, expected_error=expected)
                        else:
                            with self.assertRaises(dev.Refusal) as failure:
                                foundation.auth(self.target, 'POST', 'signup', 'key', {}, expected_error=expected)
                            self.assertEqual(failure.exception.code, 'auth_denial_unverified')
                            self.assertNotIn('credential-sentinel', str(failure.exception))
                    connection.close.assert_called_once()

    def test_every_sql_connection_has_server_deadlines(self):
        for role in [None, foundation.ROLES[1]]:
            with patch.object(foundation, 'process', return_value=b'') as process:
                foundation.sql(self.run, 'container', 'SELECT 1;', role, 'credential-sentinel')
            arguments = process.call_args.args[0]
            self.assertIn('PGCONNECT_TIMEOUT=5', arguments)
            self.assertIn('PGOPTIONS=-c lock_timeout=3000 -c statement_timeout=8000 '
                          '-c transaction_timeout=20000 -c idle_in_transaction_session_timeout=5000', arguments)


if __name__ == '__main__':
    unittest.main()
