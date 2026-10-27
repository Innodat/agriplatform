"""Explicit disposable synthetic acceptance substrate, never application readiness."""
import fcntl
import http.client
import json
import os
from pathlib import Path
import secrets
import stat
import subprocess
import tempfile
import uuid

import dev
import native_cli as native

SCHEMA = 'env_leave_foundation'
ROLES = ['leave_foundation_owner', 'leave_foundation_a', 'leave_foundation_b']


def refuse(code):
    dev.refuse('foundation', code)


def process(arguments, path, payload=None, password_rejection_role=None):
    try:
        with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as diagnostic:
            result = subprocess.run(arguments, input=payload, stdout=output, stderr=diagnostic,
                                    cwd=path, env=native.environment(path), timeout=30, check=False)
            output.seek(0)
            raw = output.read(dev.LIMIT + 1)
            if len(raw) > dev.LIMIT:
                refuse('response_too_large')
            if password_rejection_role is not None:
                diagnostic.seek(0)
                detail = diagnostic.read(dev.LIMIT + 1)
                if len(detail) > dev.LIMIT:
                    refuse('response_too_large')
                # Pinned psql/libpq reports connection authentication failure on stderr.
                # Select only this diagnostic; never emit vendor text or credit another
                # transport failure as proof that the runtime password is enforced.
                rejection = ('FATAL:  password authentication failed for user "'
                             + password_rejection_role + '"').encode()
                if result.returncode == 2 and any(line.endswith(rejection) for line in detail.splitlines()):
                    return b''
                refuse('runtime_password_rejection_unverified')
            if result.returncode:
                refuse('command_failed')
            return raw
    except subprocess.TimeoutExpired:
        refuse('command_timeout')
    except OSError:
        refuse('command_unavailable')


def sql(path, container, statement, role=None, password=None, expect_password_rejection=False):
    if role is None:
        # Disposable native fixture bootstrap alone needs the native administrator:
        # its postgres login cannot assign a new role as schema owner. Subsequent
        # schema setup and probes authenticate as their own restricted fixture roles.
        args = ['docker', 'exec', '-i', container, 'psql', '-X', '-v', 'ON_ERROR_STOP=1', '-At', '-U', 'supabase_admin', '-d', 'postgres']
        payload = statement.encode()
    else:
        # Password is sent through stdin, never argv, environment of the host, or output.
        args = ['docker', 'exec', '-i', container, 'sh', '-c',
                'IFS= read -r PGPASSWORD; export PGPASSWORD; exec psql -X -v ON_ERROR_STOP=1 -At -h "$2" -U "$1" -d postgres', 'fixture', role, container]
        payload = (password + '\n' + statement).encode()
    args[3:3] = ['-e', 'PGCONNECT_TIMEOUT=5', '-e',
                  'PGOPTIONS=-c lock_timeout=3000 -c statement_timeout=8000 '
                  '-c transaction_timeout=20000 -c idle_in_transaction_session_timeout=5000']
    if expect_password_rejection:
        return process(args, path, payload, password_rejection_role=role).decode().strip()
    return process(args, path, payload).decode().strip()


def expect_permission_denied(path, container, statement, role, password):
    # PostgreSQL must execute the valid probe and catch SQLSTATE 42501 itself.
    # Syntax, connection and other command failures propagate rather than proving
    # restricted authority. The DO subtransaction rolls back unexpected writes
    # when its deliberate P0001 exception fails the probe.
    quoted = statement.replace("'", "''")
    result = sql(path, container, f'''DO $foundation$
BEGIN
  EXECUTE '{quoted}';
  RAISE EXCEPTION 'foundation permission denial was not enforced';
EXCEPTION WHEN insufficient_privilege THEN
  NULL;
END;
$foundation$;''', role, password)
    if result != 'DO':
        refuse('permission_denial_unverified')


def auth(target, method, route, key, body, expected_error=None):
    connection = http.client.HTTPConnection('127.0.0.1', target['ports']['supabase_api'], timeout=10)
    try:
        connection.request(method, '/auth/v1/' + route, json.dumps(body),
                           {'apikey': key, 'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
        response = connection.getresponse()
        raw = response.read(dev.LIMIT + 1)
        if len(raw) > dev.LIMIT:
            refuse('auth_failed')
        if expected_error is not None:
            value = dev.decode(raw)
            if (type(value) is not dict or response.status != expected_error[0]
                    or value.get('error_code') != expected_error[1]):
                refuse('auth_denial_unverified')
            return {}
        if response.status not in (200, 201):
            refuse('auth_failed')
        value = dev.decode(raw)
        if type(value) is not dict:
            refuse('auth_response_invalid')
        return value
    except (OSError, http.client.HTTPException):
        refuse('auth_unavailable')
    finally:
        connection.close()


def credentials(executable, path, network_id):
    value = dev.decode(process([executable, '--workdir', str(path), '--network-id', network_id,
                                'status', '--output', 'json'], path))
    if type(value) is not dict or any(type(value.get(k)) is not str or not value[k] for k in ['ANON_KEY', 'SERVICE_ROLE_KEY']):
        refuse('local_credentials_unavailable')
    return value


def setup(path, target, run_id, keys, state):
    container = 'supabase_db_' + dev.project_identity(target, run_id)
    passwords = [secrets.token_urlsafe(32) for _ in ROLES]
    accounts = [{'email': 'foundation-' + run_id + '-' + str(i) + '@example.invalid',
                 'password': secrets.token_urlsafe(32)} for i in range(2)]
    # A failed attempt remains explicitly unknown; never repair or adopt automatically.
    native.write_private(state, 'foundation-attempt.json', b'{"status":"incomplete"}\n')
    for account in accounts:
        user = auth(target, 'POST', 'admin/users', keys['SERVICE_ROLE_KEY'], dict(account, email_confirm=True))
        account['id'] = str(uuid.UUID(user['id']))
    statements = ['BEGIN;']
    for role, password in zip(ROLES, passwords):
        statements.append(f"CREATE ROLE {role} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS PASSWORD '{password}';")
    statements += [f'CREATE SCHEMA {SCHEMA} AUTHORIZATION {ROLES[0]};', 'COMMIT;']
    sql(path, container, '\n'.join(statements))
    sql(path, container, f'''BEGIN;
CREATE TABLE {SCHEMA}.organizations (org_id integer PRIMARY KEY, kind text NOT NULL, marker text NOT NULL);
INSERT INTO {SCHEMA}.organizations VALUES (1, 'nonprofit', 'synthetic-a'), (2, 'for_profit', 'synthetic-b');
ALTER TABLE {SCHEMA}.organizations ENABLE ROW LEVEL SECURITY;
CREATE POLICY organization_isolation ON {SCHEMA}.organizations USING
 ((current_user = '{ROLES[1]}' AND org_id = 1) OR (current_user = '{ROLES[2]}' AND org_id = 2));
GRANT USAGE ON SCHEMA {SCHEMA} TO {ROLES[1]}, {ROLES[2]};
GRANT SELECT ON {SCHEMA}.organizations TO {ROLES[1]}, {ROLES[2]};
COMMIT;''', ROLES[0], passwords[0])
    value = {'run_id': run_id, 'target_id': target['target_id'], 'accounts': accounts,
             'passwords': passwords, 'status': 'complete'}
    native.write_private(state, 'foundation-ready.json', (json.dumps(value) + '\n').encode())


def smoke(path, target, run_id, keys, state):
    value = dev.decode(dev.read_at(state, 'foundation-ready.json', protected=True))
    if (type(value) is not dict or value.get('status') != 'complete' or value.get('run_id') != run_id
            or value.get('target_id') != target['target_id'] or len(value.get('accounts', [])) != 2
            or len(value.get('passwords', [])) != 3):
        refuse('fixture_not_ready')
    for account in value['accounts']:
        response = auth(target, 'POST', 'token?grant_type=password', keys['ANON_KEY'],
                        {'email': account['email'], 'password': account['password']})
        if (type(response.get('user')) is not dict or response['user'].get('id') != account['id']
                or type(response.get('access_token')) is not str or not response['access_token']):
            refuse('sign_in_failed')
    auth(target, 'POST', 'signup', keys['ANON_KEY'],
         {'email': 'signup-probe-' + run_id + '@example.invalid', 'password': secrets.token_urlsafe(32)},
         expected_error=(422, 'signup_disabled'))
    auth(target, 'POST', 'token?grant_type=password', keys['ANON_KEY'],
         {'email': value['accounts'][0]['email'], 'password': secrets.token_urlsafe(32)},
         expected_error=(400, 'invalid_credentials'))
    container = 'supabase_db_' + dev.project_identity(target, run_id)
    for index in (1, 2):
        role, password = ROLES[index], value['passwords'][index]
        observed = sql(path, container, f'SELECT org_id FROM {SCHEMA}.organizations ORDER BY org_id;', role, password)
        if observed != str(index):
            refuse('organization_isolation_failed')
        flags = sql(path, container,
                    'SELECT NOT rolsuper AND NOT rolcreatedb AND NOT rolcreaterole AND NOT rolbypassrls '
                    'FROM pg_roles WHERE rolname = current_user;', role, password)
        if flags != 't':
            refuse('runtime_role_unsafe')
        sql(path, container, 'SELECT 1;', role, secrets.token_urlsafe(32), expect_password_rejection=True)
        for denied in [f'CREATE TABLE {SCHEMA}.forbidden (id integer);', f'SET ROLE {ROLES[0]};',
                       f'INSERT INTO {SCHEMA}.organizations SELECT * FROM {SCHEMA}.organizations WHERE org_id = {index};',
                       f"UPDATE {SCHEMA}.organizations SET marker = 'probe' WHERE org_id = {index};",
                       f'DELETE FROM {SCHEMA}.organizations WHERE org_id = {index};']:
            expect_permission_denied(path, container, denied, role, password)


def main(argv=None):
    safe = {}
    try:
        parser = dev.Parser(add_help=False, allow_abbrev=False)
        parser.add_argument('command', choices=['setup', 'smoke'])
        for name in ['target', 'run-id', 'supabase']:
            parser.add_argument('--' + name, required=True)
        args = parser.parse_args(argv)
        if str(uuid.UUID(args.run_id)) != args.run_id:
            refuse('invalid_run_id')
        source = Path(args.target)
        if '..' in source.parts:
            refuse('unsafe_path')
        source = Path(os.path.abspath(source))
        raw = dev.read(source)
        target = dev.decode(raw)
        native.validate_target(target)
        if target['target_id'] != 'leave-local' or target['workspace_root'] != str(dev.ROOT):
            refuse('leave_local_target_required')
        executable = Path(args.supabase)
        if not executable.is_absolute() or '..' in executable.parts or not executable.is_file() or not os.access(executable, os.X_OK):
            refuse('explicit_executable_required')
        path = native.run_path(target, args.run_id)
        native.check_run(path, target, raw, args.run_id)
        safe = {'run_id': args.run_id, 'project': dev.project_identity(target, args.run_id)}
        with dev.directory(path) as state:
            lock = os.open('native.lock', os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=state)
            try:
                info = os.fstat(lock)
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
                    refuse('unsafe_lock')
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    refuse('run_busy')
                if args.command == 'setup' and any((path / name).exists() or (path / name).is_symlink()
                        for name in ['foundation-attempt.json', 'foundation-ready.json']):
                    refuse('fixture_already_attempted')
                if args.command == 'smoke' and not (path / 'foundation-ready.json').exists():
                    refuse('fixture_not_ready')
                native.vendor(str(executable), ['--version'], path, 'version')
                native.docker_prerequisite(path)
                network_id = native.network(target, args.run_id, False, path)
                native.check_run(path, target, raw, args.run_id)
                if dev.read(source) != raw:
                    refuse('target_changed')
                keys = credentials(str(executable), path, network_id)
                {'setup': setup, 'smoke': smoke}[args.command](path, target, args.run_id, keys, state)
            finally:
                os.close(lock)
        result = dict(safe, ok=True, stage=args.command, code='completed', runtime_ready=False)
        if args.command == 'smoke':
            result['synthetic_foundation_verified'] = True
        status = 0
    except dev.Refusal as error:
        result = dict(safe, ok=False, stage=error.stage, code=error.code, runtime_ready=False)
        status = 2
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        result = dict(safe, ok=False, stage='foundation', code='unsafe_or_unavailable_input', runtime_ready=False)
        status = 2
    print(json.dumps(result, sort_keys=True))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
