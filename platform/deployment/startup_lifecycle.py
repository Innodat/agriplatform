"""Synthetic secret-transfer validation and opt-in real PostgreSQL qualification.

Default validation has no daemon operations. The explicit bootstrap qualifier
executes a bounded disposable selected-image container without persisting secrets.
Source authority: fixtures/supabase-pg17-lifecycle.md.
"""
import os
import re
import select
import stat
import time

import dev

CONTAINER_ID = 'e' * 64
MEMBER = b'etc/postgresql-custom/pgsodium_root.key'
ROOT_KEY = b'd4dc5b6d4a1d6a10b2c1e76112c994d65db7cec380572cc1839624d4be3fa275'
MAX_BYTES = 10240
READ_SECONDS = 1.0


def refuse():
    dev.refuse('startup', 'unsafe_lifecycle')


def read_archive(fd):
    """Only called after exact cp operands and prerequisite sequence validate."""
    if not (stat.S_ISFIFO(os.fstat(fd).st_mode) or stat.S_ISSOCK(os.fstat(fd).st_mode)):
        refuse()
    deadline = time.monotonic() + READ_SECONDS
    chunks = []
    size = 0
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not select.select([fd], [], [], remaining)[0]:
            refuse()
        chunk = os.read(fd, min(4096, MAX_BYTES + 1 - size))
        if not chunk:
            return b''.join(chunks)
        size += len(chunk)
        if size > MAX_BYTES:
            refuse()
        chunks.append(chunk)


def number(field):
    # Octal digits, optionally preceded by spaces, then NUL/space padding.
    # No digit may follow a terminator and NUL cannot precede the digits.
    if not re.fullmatch(rb' *[0-7]+[\x00 ]*', field):
        refuse()
    return int(field.rstrip(b'\x00 '), 8)


def validate_archive(raw):
    if type(raw) is not bytes or len(raw) != MAX_BYTES:
        refuse()
    h = raw[:512]
    if (h[:100] != MEMBER.ljust(100, b'\0') or h[156:157] != b'0'
            or h[157:257] != b'\0' * 100 or h[257:265] != b'ustar\00000'
            or any(h[265:329]) or any(h[345:512])
            or number(h[100:108]) != 0o644 or number(h[108:116]) != 0
            or number(h[116:124]) != 0 or number(h[124:136]) != len(ROOT_KEY)
            or number(h[148:156]) != sum(h[:148]) + 8 * 32 + sum(h[156:])):
        refuse()
    number(h[136:148])
    for field in [h[329:337], h[337:345]]:
        if field != b'\0' * len(field) and number(field) != 0:
            refuse()
    if raw[512:512+len(ROOT_KEY)] != ROOT_KEY or any(raw[512+len(ROOT_KEY):]):
        refuse()
    return {'member_count': 1, 'regular_file': True, 'mode': '0644',
            'uid': 0, 'gid': 0, 'content_verified': True, 'archive_bytes': len(raw)}


def transfer_event():
    return {'kind': 'secret_transfer', 'facts': {'member_count': 1, 'regular_file': True,
            'mode': '0644', 'uid': 0, 'gid': 0, 'content_verified': True}}

# This separate opt-in proof never uses the guarded DockerSession container routes.
BOOTSTRAP_SECONDS = 120
SHUTDOWN_SECONDS = 15
BOOTSTRAP_OUTPUT = 65536
ROLES = ('postgres', 'authenticator', 'pgbouncer', 'supabase_auth_admin',
         'supabase_storage_admin', 'supabase_replication_admin', 'supabase_read_only_user')


def bootstrap_fail(code):
    dev.refuse('postgres_bootstrap', code)


def bootstrap_success():
    return dict(ok=True, stage='postgres_bootstrap', code='qualified', initialized=True,
                runtime_ready=False, cleanup_verified=True, shutdown_verified=True,
                forced_shutdown=False, role_passwords_verified=True,
                jwt_settings_verified=True, migration_markers_verified=True,
                internal_schemas_verified=True, root_key_verified=True)


def public_archive():
    """The same independently validated public regular-file transfer; memory only."""
    import io
    import tarfile
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w', format=tarfile.USTAR_FORMAT) as archive:
        entry = tarfile.TarInfo(MEMBER.decode())
        entry.size, entry.mode = len(ROOT_KEY), 0o644
        archive.addfile(entry, io.BytesIO(ROOT_KEY))
    raw = stream.getvalue()
    validate_archive(raw)
    return raw


def password_matches(role, verifier):
    """Check actual catalog verifier without emitting credential-derived bytes."""
    import hashlib
    import hmac
    import base64
    if type(verifier) is not str:
        return False
    if verifier.startswith('md5'):
        return hmac.compare_digest(verifier, 'md5' + hashlib.md5(('postgres' + role).encode()).hexdigest())
    try:
        prefix, parameters, keys = verifier.split('$')
        iterations, salt = parameters.split(':')
        stored, server = keys.split(':')
        if prefix != 'SCRAM-SHA-256' or not 1 <= int(iterations) <= 100000:
            return False
        salted = hashlib.pbkdf2_hmac('sha256', b'postgres', base64.b64decode(salt, validate=True), int(iterations))
        client = hmac.digest(salted, b'Client Key', 'sha256')
        return (hmac.compare_digest(hashlib.sha256(client).digest(), base64.b64decode(stored, validate=True))
                and hmac.compare_digest(hmac.digest(salted, b'Server Key', 'sha256'), base64.b64decode(server, validate=True)))
    except (ValueError, TypeError):
        return False


def shutdown_timestamp(value):
    """Validate Docker UTC timestamps without losing nanosecond ordering."""
    import datetime
    if type(value) is not str:
        bootstrap_fail('shutdown_invalid_state')
    match = re.fullmatch(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?Z', value)
    if not match:
        bootstrap_fail('shutdown_invalid_state')
    try:
        instant = datetime.datetime.strptime(match[1], '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        bootstrap_fail('shutdown_invalid_state')
    if instant.year <= 1:
        bootstrap_fail('shutdown_invalid_state')
    return instant, int((match[2] or '').ljust(9, '0'))


def shutdown_state(row, started_at=None):
    """Only exact, observed normal exit of the verified started instance qualifies."""
    state = row.get('State')
    if type(state) is not dict:
        bootstrap_fail('shutdown_invalid_state')
    started = shutdown_timestamp(state.get('StartedAt'))
    if state.get('OOMKilled') is True:
        bootstrap_fail('shutdown_oom')
    if started_at is not None and type(state.get('ExitCode')) is int and state['ExitCode'] != 0:
        bootstrap_fail('shutdown_forced_exit' if state['ExitCode'] == 137 else 'shutdown_nonzero_exit')
    if started_at is not None and state.get('Running') is True:
        bootstrap_fail('shutdown_still_running')
    if (state.get('Dead') is not False or state.get('OOMKilled') is not False
            or state.get('Error') != ''):
        bootstrap_fail('shutdown_invalid_state')
    if started_at is None:
        if (state.get('Status') != 'running' or state.get('Running') is not True
                or type(state.get('Pid')) is not int or state['Pid'] <= 0):
            bootstrap_fail('shutdown_invalid_state')
        return state['StartedAt']
    if (state.get('StartedAt') != started_at or state.get('Status') != 'exited'
            or state.get('Running') is not False or type(state.get('Pid')) is not int
            or state['Pid'] != 0 or type(state.get('ExitCode')) is not int
            or state['ExitCode'] != 0 or shutdown_timestamp(state.get('FinishedAt')) <= started):
        bootstrap_fail('shutdown_invalid_state')


def run_bootstrap(image, config, run_id, command):
    """Closed commands through an injected bounded runner. No adoption or replay."""
    import json
    import uuid
    import create_profile
    if (str(uuid.UUID(run_id)) != run_id or not re.fullmatch(r'public\.ecr\.aws/supabase/postgres@sha256:[0-9a-f]{64}', image)
            or not re.fullmatch(r'sha256:[0-9a-f]{64}', config)):
        bootstrap_fail('invalid_selection')
    deadline = time.monotonic() + BOOTSTRAP_SECONDS
    name = 'env-pg-bootstrap-' + run_id
    labels = {'io.agriplatform.env.run': run_id, 'io.agriplatform.env.proof': 'postgres-bootstrap'}
    tmpfs = {'/var/lib/postgresql/data': 'rw,noexec,nosuid,size=1073741824'}
    container_id = None
    expected_labels = None
    ownership_changed = False
    phase = 'initialization'
    shutdown_verified = False
    def call(argv, **kwargs):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            bootstrap_fail(phase + '_deadline')
        result = command(argv, timeout=min(10, remaining), limit=BOOTSTRAP_OUTPUT, **kwargs)
        if phase in ('shutdown', 'cleanup') and time.monotonic() >= deadline:
            bootstrap_fail(phase + '_deadline')
        return result
    def decoded(argv):
        try:
            return dev.decode(call(argv))
        except (ValueError, TypeError):
            bootstrap_fail('invalid_observation')
    def inspect_owned():
        rows = decoded(['container', 'inspect', container_id])
        if type(rows) is not list or len(rows) != 1:
            bootstrap_fail('ownership_changed')
        row = rows[0]
        host = row.get('HostConfig', {})
        if (row.get('Id') != container_id or row.get('Name') != '/' + name or row.get('Image') != config
                or row.get('Config', {}).get('Image') != image or row.get('Config', {}).get('Labels') != expected_labels
                or host.get('NetworkMode') != 'none' or host.get('Binds') not in (None, [])
                or host.get('PortBindings') not in (None, {}) or host.get('Tmpfs') != tmpfs
                or host.get('Memory') != 2147483648 or host.get('MemorySwap') != 2147483648
                or host.get('NanoCpus') != 2000000000 or host.get('PidsLimit') != 256
                or host.get('LogConfig') != {'Type': 'none', 'Config': {}}
                or host.get('Privileged') is not False
                or set(row.get('NetworkSettings', {}).get('Networks', {})) != {'none'}
                or any(m.get('Type') != 'tmpfs' or m.get('Destination') not in tmpfs for m in row.get('Mounts', []))):
            bootstrap_fail('ownership_changed')
        return row
    def owned():
        nonlocal ownership_changed
        if ownership_changed:
            bootstrap_fail('ownership_changed')
        try:
            return inspect_owned()
        except (ValueError, KeyError, TypeError, AttributeError):
            ownership_changed = True
            bootstrap_fail('ownership_changed')
        except dev.Refusal as error:
            if error.code in ('ownership_changed', 'invalid_observation', 'duplicate_key', 'invalid_json'):
                ownership_changed = True
            raise
    rows = decoded(['image', 'inspect', image])
    if (type(rows) is not list or len(rows) != 1 or rows[0].get('Id') != config
            or rows[0].get('Os') != 'linux' or rows[0].get('Architecture') != 'amd64'
            or image not in rows[0].get('RepoDigests', [])):
        bootstrap_fail('image_identity_mismatch')
    image_config = rows[0].get('Config', {})
    if set(image_config.get('Volumes') or {}) - set(tmpfs):
        bootstrap_fail('unsupported_image_volumes')
    inherited_labels = image_config.get('Labels') or {}
    if type(inherited_labels) is not dict or any(type(k) is not str or type(v) is not str for k, v in inherited_labels.items()):
        bootstrap_fail('invalid_image_labels')
    expected_labels = {**inherited_labels, **labels}
    if call(['container', 'ls', '--all', '--quiet', '--filter', 'name=^/' + name + '$']).strip():
        bootstrap_fail('existing_container')
    create = ['create', '--platform', 'linux/amd64', '--name', name, '--network', 'none',
              '--tmpfs', '/var/lib/postgresql/data:' + tmpfs['/var/lib/postgresql/data'],
              '--memory', '2147483648', '--memory-swap', '2147483648',
              '--cpus', '2', '--pids-limit', '256', '--log-driver', 'none']
    for key, value in labels.items():
        create += ['--label', key + '=' + value]
    for key, value in create_profile.CONTAINER_ENV.items():
        create += ['--env', key + '=' + value]
    create += ['--entrypoint', 'sh', image, '-c', dev.read(dev.ROOT / create_profile.BOOTSTRAP).decode()]
    # If create is lost/failed, there is no authoritative ID and no cleanup/adoption.
    raw = call(create).strip()
    if not re.fullmatch(rb'[0-9a-f]{64}', raw):
        bootstrap_fail('uncertain_creation')
    container_id = raw.decode()
    failure = None
    step = 'ownership'
    try:
        owned()
        step = 'key_transfer'
        call(['cp', '-', container_id + ':/'], input_data=public_archive())
        owned()
        step = 'start'
        call(['start', container_id])
        step = 'bootstrap_wait'
        verified_started_at = None
        while True:
            row = owned()
            if row.get('State', {}).get('Running') is not True:
                bootstrap_fail('initialization_stopped')
            if verified_started_at is None:
                verified_started_at = shutdown_state(row)
            elif row.get('State', {}).get('StartedAt') != verified_started_at:
                bootstrap_fail('initialization_instance_changed')
            try:
                call(['exec', container_id, 'pg_isready', '-U', 'postgres', '-h', '/var/run/postgresql', '-d', 'postgres'])
                break
            except dev.Refusal as error:
                if error.code != 'command_refused':
                    raise
                time.sleep(min(.2, max(0, deadline - time.monotonic())))
        def sql(database, query):
            owned()
            return call(['exec', '--env', 'PGPASSWORD=postgres', container_id, 'psql', '-X', '-A', '-t',
                         '-v', 'ON_ERROR_STOP=1', '-h', '127.0.0.1', '-U', 'postgres', '-d', database, '-c', query]).strip()
        # pg_isready can observe the temporary init server. Require the final TCP server.
        while True:
            try:
                sql('postgres', 'SELECT 1')
                break
            except dev.Refusal as error:
                if error.code != 'command_refused':
                    raise
                time.sleep(min(.2, max(0, deadline - time.monotonic())))
        owned()
        step = 'catalog'
        catalog = dev.decode(call(['exec', '--env', 'PGPASSWORD=postgres', container_id, 'psql', '-X', '-A', '-t', '-v', 'ON_ERROR_STOP=1',
                                  '-h', '/var/run/postgresql', '-U', 'supabase_admin', '-d', 'postgres', '-c',
                                  "SELECT json_object_agg(rolname,rolpassword) FROM pg_authid WHERE rolname IN (" + ','.join("'" + r + "'" for r in ROLES) + ')']))
        if set(catalog) != set(ROLES) or not all(password_matches(r, catalog[r]) for r in ROLES):
            bootstrap_fail('role_password_check_failed')
        owned()
        step = 'loopback_authentication'
        # The immutable image has local-loopback trust. Verifier installation is
        # proved above; this separate observation must not claim password enforcement.
        hba = call(['exec', container_id, 'sha256sum', '/etc/postgresql/pg_hba.conf']).split()
        if not hba or hba[0] != b'a925911753f4975548eb4079177441c886aa22b6dd69f2b0cff98f779fb0b66a':
            bootstrap_fail('unexpected_authentication_policy')
        owned()
        wrong_password = call(['exec', '--env', 'PGPASSWORD=deliberately-wrong-public-password', container_id, 'psql',
                  '-X', '-A', '-t', '-v', 'ON_ERROR_STOP=1', '-h', '127.0.0.1', '-U', 'postgres',
                  '-d', 'postgres', '-c', 'SELECT 1']).strip()
        if wrong_password != b'1' or sql('postgres', 'SELECT 1') != b'1':
            bootstrap_fail('unexpected_loopback_authentication')
        step = 'storage'
        if sql('postgres', 'SHOW data_directory') != b'/var/lib/postgresql/data':
            bootstrap_fail('unexpected_data_directory')
        owned()
        if call(['exec', container_id, 'stat', '-f', '-c', '%T', '/var/lib/postgresql/data']).strip() != b'tmpfs':
            bootstrap_fail('storage_not_tmpfs')
        import create_profile as profile
        step = 'jwt'
        settings = sql('postgres', "SELECT current_setting('app.settings.jwt_secret') = '" + profile.CONTAINER_ENV['JWT_SECRET'] + "' AND current_setting('app.settings.jwt_exp') = '3600'")
        if settings != b't':
            bootstrap_fail('jwt_check_failed')
        step = 'markers'
        if sql('postgres', "SELECT array_agg(version ORDER BY version) = ARRAY['20210809183423_update_grants','initial'] FROM supabase_functions.migrations") != b't':
            bootstrap_fail('migration_check_failed')
        step = 'schemas'
        if sql('_supabase', "SELECT count(*) = 2 FROM pg_namespace WHERE nspname IN ('_analytics','_supavisor')") != b't':
            bootstrap_fail('schema_check_failed')
        owned()
        # Fixed public bytes/path; shell never receives caller-controlled operands.
        step = 'key'
        key_check = "test -f /etc/postgresql-custom/pgsodium_root.key && test ! -L /etc/postgresql-custom/pgsodium_root.key && test \"$(stat -c '%a:%u:%g:%s' /etc/postgresql-custom/pgsodium_root.key)\" = '644:0:0:64' && test \"$(cat /etc/postgresql-custom/pgsodium_root.key)\" = '" + ROOT_KEY.decode() + "' && printf verified"
        if call(['exec', container_id, 'sh', '-c', key_check]) != b'verified':
            bootstrap_fail('key_check_failed')
        # A late final initialization command cannot acquire a fresh shutdown budget.
        if time.monotonic() >= deadline:
            bootstrap_fail('initialization_deadline')
        # Initialization and shutdown each have their own fixed total deadline.
        phase = 'shutdown'
        deadline = time.monotonic() + SHUTDOWN_SECONDS
        step = 'shutdown'
        started_at = shutdown_state(owned())
        if started_at != verified_started_at:
            bootstrap_fail('shutdown_instance_changed')
        call(['stop', '--timeout', '5', container_id])
        shutdown_state(owned(), started_at)
        shutdown_verified = True
    except (dev.Refusal, OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        failure = error
    finally:
        # Cleanup has its own short deadline, even if initialization exhausted its budget.
        deadline = time.monotonic() + 10
        phase = 'cleanup'
        try:
            cleanup_row = owned()
            if shutdown_verified:
                shutdown_state(cleanup_row, started_at)
            call(['rm', container_id] if shutdown_verified else ['rm', '--force', container_id])
            if call(['container', 'ls', '--all', '--quiet', '--filter', 'id=' + container_id]).strip():
                bootstrap_fail('cleanup_unresolved')
        except (dev.Refusal, OSError, ValueError, KeyError, TypeError, AttributeError):
            bootstrap_fail('cleanup_unresolved')
    if failure is not None:
        if step == 'shutdown':
            bootstrap_fail(failure.code if isinstance(failure, dev.Refusal) and failure.code.startswith('shutdown_') else 'shutdown_failed')
        bootstrap_fail('execution_failed_' + step)
    result = bootstrap_success()
    result['loopback_password_required'] = False
    return result


def qualify_bootstrap(args):
    """Fresh source-bound prerequisite verification before any Docker execution."""
    from pathlib import Path
    import tempfile
    import shutil
    import startup
    import images
    import uuid
    if str(uuid.UUID(args.run_id)) != args.run_id:
        bootstrap_fail('invalid_run_id')
    path = Path(args.target)
    if '..' in path.parts:
        bootstrap_fail('unsafe_target')
    path = path.absolute()
    raw = dev.read(path)
    target = dev.decode(raw)
    dev.validate(target, dev.decode(dev.read(dev.ROOT / dev.SCHEMA)))
    if target['workspace_root'] != str(dev.ROOT):
        bootstrap_fail('workspace_mismatch')
    sources = dev.source_evidence()
    dev.validate_prepared(target, raw, args.run_id, path, sources)
    evidence = startup.existing_images(args)
    _, plan, _, configs = evidence
    selected = [value for key, value in plan.items() if '/supabase/postgres:' in key]
    if len(selected) != 1:
        bootstrap_fail('invalid_selection')
    docker = shutil.which('docker', path='/usr/bin:/usr/local/bin:/bin')
    if not docker:
        bootstrap_fail('docker_unavailable')
    with tempfile.TemporaryDirectory(prefix='env-pg-bootstrap-') as work:
        environment = {'PATH': '/usr/bin:/usr/local/bin:/bin', 'HOME': work,
                       'DOCKER_CONFIG': work, 'LANG': 'C', 'LC_ALL': 'C'}
        def command(argv, **kwargs):
            return images.bounded_command([docker, '--host', 'unix:///var/run/docker.sock'] + argv,
                                          work, environment, **kwargs)
        result = run_bootstrap(selected[0], configs[selected[0]], args.run_id, command)
    if startup.existing_images(args) != evidence or dev.source_evidence() != sources or dev.read(path) != raw:
        bootstrap_fail('source_changed')
    dev.validate_prepared(target, raw, args.run_id, path, sources)
    return result


def persistence_exec(run_id, mode):
    """Closed UUID-bound predicates: false/NULL is an SQL error, never a success row."""
    import uuid
    import create_profile
    try:
        valid = str(uuid.UUID(run_id)) == run_id
    except (ValueError, TypeError, AttributeError):
        valid = False
    if not valid or mode not in ('write', 'verify', 'schemas'):
        refuse()
    predicate = ("(SELECT array_agg(version ORDER BY version) = ARRAY['20210809183423_update_grants','initial'] "
                 "FROM supabase_functions.migrations) AND current_setting('app.settings.jwt_secret') = '"
                 + create_profile.CONTAINER_ENV['JWT_SECRET'] + "' AND current_setting('app.settings.jwt_exp') = '3600'")
    marker = ('env_persistence_probe')
    if mode == 'schemas':
        query = "DO $$ BEGIN IF (SELECT count(*) = 2 FROM pg_namespace WHERE nspname IN ('_analytics','_supavisor')) IS NOT TRUE THEN RAISE EXCEPTION 'initialization predicate failed'; END IF; END $$;"
    else:
        prefix = ("BEGIN; CREATE TABLE public." + marker + " (run_id uuid PRIMARY KEY, system_identifier text NOT NULL); "
                  "INSERT INTO public." + marker + " SELECT '" + run_id + "'::uuid, system_identifier::text FROM pg_control_system(); ") if mode == 'write' else 'BEGIN; '
        query = prefix + "DO $$ BEGIN IF (" + predicate + ") IS NOT TRUE OR (SELECT count(*) = 1 AND bool_and(run_id = '" + run_id + "'::uuid AND system_identifier = (SELECT system_identifier::text FROM pg_control_system())) FROM public." + marker + ") IS NOT TRUE THEN RAISE EXCEPTION 'persistence predicate failed'; END IF; END $$; COMMIT;"
    return {'AttachStdin': False, 'AttachStdout': False, 'AttachStderr': False,
            'Tty': False, 'Privileged': False, 'User': 'postgres', 'Env': ['PGPASSWORD=postgres'],
            'Cmd': ['psql', '-X', '-A', '-t', '-v', 'ON_ERROR_STOP=1', '-h', '127.0.0.1',
                    '-U', 'postgres', '-d', '_supabase' if mode == 'schemas' else 'postgres', '-c', query]}


def valid_persistence_exec(body):
    if type(body) is not dict or type(body.get('Cmd')) is not list or not body['Cmd']:
        return False
    # Rebuild from the only caller-controlled value, a canonical UUID in closed SQL.
    candidates = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", str(body['Cmd'][-1]))
    for run_id in candidates or ['00000000-0000-0000-0000-000000000000']:
        if any(body == persistence_exec(run_id, mode) and all(type(body.get(k)) is type(v) for k, v in persistence_exec(run_id, mode).items())
               for mode in ('write', 'verify', 'schemas')):
            return True
    return False


# Auth v2.197.0, commit 4eee58f296d9698a1c2c0ae14d7a0b379c7622d3.
# Pop v6.1.1 uses literal filename versions, including the leading-zero "00".
AUTH_MIGRATION_VERSIONS = ('00', '20210710035447', '20210722035447', '20210730183235', '20210909172000', '20210927181326', '20211122151130', '20211124214934', '20211202183645', '20220114185221', '20220114185340', '20220224000811', '20220323170000', '20220429102000', '20220531120530', '20220614074223', '20220811173540', '20221003041349', '20221003041400', '20221011041400', '20221020193600', '20221021073300', '20221021082433', '20221027105023', '20221114143122', '20221114143410', '20221125140132', '20221208132122', '20221215195500', '20221215195800', '20221215195900', '20230116124310', '20230116124412', '20230131181311', '20230322519590', '20230402418590', '20230411005111', '20230508135423', '20230523124323', '20230818113222', '20230914180801', '20231027141322', '20231114161723', '20231117164230', '20240115144230', '20240214120130', '20240306115329', '20240314092811', '20240427152123', '20240612123726', '20240729123726', '20240802193726', '20240806073726', '20241009103726', '20250717082212', '20250731150234', '20250804100000', '20250901200500', '20250903112500', '20250904133000', '20250925093508', '20251007112900', '20251104100000', '20251111201300', '20251201000000', '20260115000000', '20260121000000', '20260219120000', '20260302000000', '20260625000000', '20260821000000', '20260821010000', '20260824000000', '20260824000001', '20260831180000')


# PostgreSQL 17.11.0.004 auth-schema bootstrap, commit cf90815413819eb057a9916c1598692c160ebeb4.
AUTH_POSTGRES_BASELINE_VERSIONS = ('20171026211738', '20171026211808', '20171026211834', '20180103212743', '20180108183307', '20180119214651', '20180125194653')
AUTH_CATALOG_VERSIONS = tuple(sorted(AUTH_POSTGRES_BASELINE_VERSIONS + AUTH_MIGRATION_VERSIONS))

def auth_catalog_exec(mode):
    """Two closed, read-only predicates; never returns catalog rows or logs."""
    if mode not in ('pre', 'post'):
        refuse()
    tables = ('users', 'identities', 'sessions', 'one_time_tokens',
              'mfa_recovery_code_sets', 'mfa_recovery_codes')
    if mode == 'pre':
        baseline = ','.join("'" + version + "'" for version in AUTH_POSTGRES_BASELINE_VERSIONS)
        predicate = ("(SELECT count(*) = 7 AND count(version) = 7 AND count(DISTINCT version) = 7 "
                     "AND array_agg(version::text ORDER BY version::text) = ARRAY[" + baseline + "]::text[] "
                     "FROM auth.schema_migrations) "
                     "AND to_regclass('auth.mfa_recovery_code_sets') IS NULL "
                     "AND to_regclass('auth.mfa_recovery_codes') IS NULL "
                     "AND NOT EXISTS (SELECT 1 FROM pg_attribute WHERE attrelid = to_regclass('auth.one_time_tokens') "
                     "AND attname = 'expires_at' AND attnum > 0 AND NOT attisdropped)")
        message = 'fresh auth precondition failed'
    else:
        ledger = ','.join("'" + version + "'" for version in AUTH_CATALOG_VERSIONS)
        predicate = ("(SELECT count(*) = 82 AND count(version) = 82 AND count(DISTINCT version) = 82 "
                     "AND array_agg(version::text ORDER BY version::text) = ARRAY[" + ledger + "]::text[] "
                     "FROM auth.schema_migrations) AND "
                     + ' AND '.join("EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                                    "WHERE n.nspname='auth' AND c.relname='" + name + "' AND c.relkind='r')"
                                    for name in tables)
                     + " AND EXISTS (SELECT 1 FROM pg_attribute WHERE attrelid=to_regclass('auth.one_time_tokens') "
                       "AND attname='expires_at' AND attnum > 0 AND NOT attisdropped "
                       "AND atttypid='timestamp with time zone'::regtype AND NOT attnotnull)")
        message = 'auth catalog predicate failed'
    query = ("BEGIN READ ONLY; SET LOCAL statement_timeout = '5s'; SET LOCAL lock_timeout = '1s'; "
             "SET LOCAL idle_in_transaction_session_timeout = '5s'; DO $$ BEGIN IF (" + predicate
             + ") IS NOT TRUE THEN RAISE EXCEPTION '" + message + "'; END IF; END $$; COMMIT;")
    return {'AttachStdin': False, 'AttachStdout': False, 'AttachStderr': False,
            'Tty': False, 'Privileged': False, 'User': 'postgres', 'Env': ['PGPASSWORD=postgres'],
            'Cmd': ['psql', '-X', '-A', '-t', '-v', 'ON_ERROR_STOP=1', '-h', '127.0.0.1',
                    '-U', 'postgres', '-d', 'postgres', '-c', query]}


def valid_auth_catalog_exec(body):
    import create_profile
    return any(create_profile._exact_tree(body, auth_catalog_exec(mode)) for mode in ('pre', 'post'))


# Supabase CLI 2.120.0, commit 753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4,
# db-setup.ts START_REVOKE_API_PRIVILEGES_SQL (including boundary newlines).
# This profile is construction-only and deliberately absent from dev's allowlist.
API_DEFAULT_PRIVILEGES_SQL = '''
alter default privileges for role postgres in schema public
  revoke select, insert, update, delete on tables from anon, authenticated, service_role;
alter default privileges for role postgres in schema public
  revoke usage, select on sequences from anon, authenticated, service_role;
alter default privileges for role postgres in schema public
  revoke execute on functions from anon, authenticated, service_role;
'''


def _api_default_privileges_profile():
    return {'AttachStdin': False, 'AttachStdout': False, 'AttachStderr': False,
            'Tty': False, 'Privileged': False, 'User': 'postgres', 'Env': ['PGPASSWORD=postgres'],
            'Cmd': ['psql', '-X', '-A', '-t', '-v', 'ON_ERROR_STOP=1', '-h', '127.0.0.1',
                    '-U', 'postgres', '-d', 'postgres', '-c', API_DEFAULT_PRIVILEGES_SQL]}


def api_default_privileges_exec():
    """Detached owner-derived request, never an observed CLI command or SQL dispatch."""
    return _api_default_privileges_profile()


def valid_api_default_privileges_exec(body):
    import create_profile
    return create_profile._exact_tree(body, _api_default_privileges_profile())


def cli_db_backend_exec(mode):
    """Closed independent session observations; no backend rows leave PostgreSQL."""
    if mode not in ('present', 'departed'):
        refuse()
    external = ("FROM pg_stat_activity WHERE pid <> pg_backend_pid() "
                "AND backend_type = 'client backend' AND client_addr IS NOT NULL "
                "AND NOT (client_addr <<= '127.0.0.0/8'::inet OR client_addr = '::1'::inet)")
    if mode == 'present':
        predicate = ("SELECT count(*) = 1 AND bool_and((usename = 'postgres' "
                     "AND datname = 'postgres' AND client_port > 0 AND state = 'idle') IS TRUE) " + external)
        block = ("BEGIN IF (" + predicate + ") IS NOT TRUE THEN "
                 "RAISE EXCEPTION 'cli db backend presence failed'; END IF; END")
    else:
        block = ("DECLARE deadline timestamptz := clock_timestamp() + interval '3 seconds'; "
                 "BEGIN LOOP PERFORM pg_stat_clear_snapshot(); "
                 "IF (SELECT count(*) = 0 " + external + ") IS TRUE THEN "
                 "IF clock_timestamp() >= deadline THEN RAISE EXCEPTION 'cli db backend departure failed'; "
                 "END IF; EXIT; END IF; "
                 "IF clock_timestamp() >= deadline THEN RAISE EXCEPTION 'cli db backend departure failed'; "
                 "END IF; PERFORM pg_sleep(LEAST(0.05, GREATEST(0, "
                 "extract(epoch FROM deadline - clock_timestamp())))); END LOOP; END")
    # Other-user session endpoints can be NULL without full statistics visibility.
    # USAGE checks inherited privileges too; superusers satisfy pg_has_role.
    visibility = ("IF pg_has_role(current_user, 'pg_read_all_stats', 'USAGE') IS NOT TRUE "
                  "THEN RAISE EXCEPTION 'cli db backend visibility failed'; END IF; ")
    block = block.replace('BEGIN ', 'BEGIN ' + visibility, 1)
    query = ("BEGIN READ ONLY; SET LOCAL statement_timeout = '5s'; SET LOCAL lock_timeout = '1s'; "
             "SET LOCAL idle_in_transaction_session_timeout = '5s'; DO $$ " + block + " $$; COMMIT;")
    body = auth_catalog_exec('pre')
    body['Cmd'][-1] = query
    return body


def valid_cli_db_backend_exec(body):
    import create_profile
    return any(create_profile._exact_tree(body, cli_db_backend_exec(mode)) for mode in ('present', 'departed'))
