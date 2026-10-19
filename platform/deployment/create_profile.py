"""Exact Linux PG17 first-create profile for Supabase CLI 2.120.0.

Only compares public bootstrap bytes; never hashes or emits runtime input.
Authority and derivation: fixtures/supabase-pg17-profile.md.
"""
from pathlib import Path
import re

import dev
import images

BOOTSTRAP = 'platform/deployment/fixtures/supabase-pg17-bootstrap.txt'
AUTHORITY = 'platform/deployment/fixtures/supabase-pg17-profile.md'
CONTAINER_ENV = {
    'POSTGRES_PASSWORD': 'postgres',
    'POSTGRES_HOST': '/var/run/postgresql',
    'JWT_SECRET': 'super-secret-jwt-token-with-at-least-32-characters-long',
    'JWT_EXP': '3600',
}
ROUTING_KEYS = ('DOCKER_HOST', 'DOCKER_CONFIG', 'DOCKER_CONTEXT', 'DOCKER_TLS_VERIFY',
                'DOCKER_CERT_PATH', 'DOCKER_API_VERSION', 'DOCKER_TLS',
                'DOCKER_DEFAULT_PLATFORM', 'DOCKER_CUSTOM_HEADERS')


def refuse():
    dev.refuse('startup', 'unsafe_create')


def environment(fixture):
    """Public synthetic values for explicit tests; not an ambient environment fallback."""
    work = Path(fixture['workdir'])
    return {**CONTAINER_ENV, 'DOCKER_HOST': 'unix://' + str(work / 'no-daemon.sock'),
            'DOCKER_CONFIG': str(work / 'docker')}


def request(fixture):
    """Pinned ordered argv, with only owner/run-derived operands varying."""
    project = fixture['project']
    name = 'supabase_db_' + project
    return ['create', '--name', name,
            '-e', 'POSTGRES_PASSWORD', '-e', 'POSTGRES_HOST', '-e', 'JWT_SECRET', '-e', 'JWT_EXP',
            '-v', name + ':/var/lib/postgresql/data', '-p', str(fixture['database_port']) + ':5432',
            '--health-cmd', 'pg_isready -U postgres -h 127.0.0.1 -p 5432',
            '--health-interval', '10s', '--health-timeout', '2s', '--health-retries', '3',
            '--restart', 'unless-stopped', '--add-host', 'host.docker.internal:host-gateway',
            '--network', fixture['network']['Id'], '--network-alias', 'db',
            '--network-alias', 'db.supabase.internal',
            '--label', 'com.supabase.cli.project=' + project,
            '--label', 'com.docker.compose.project=' + project,
            '--label', 'com.supabase.cli.workdir=' + fixture['workdir'],
            '--entrypoint', 'sh', fixture['postgres_image'], '-c', dev.read(dev.ROOT / BOOTSTRAP).decode('utf-8')]


def validate(args, fixture, inherited):
    if (type(args) not in (list, tuple) or len(args) > 256
            or any(type(arg) is not str for arg in args)
            or sum(map(len, args)) > 65536 or type(inherited) is not dict):
        refuse()
    if type(fixture.get('database_port')) is not int or not 1 <= fixture['database_port'] <= 65535:
        refuse()
    expected = request(fixture)
    if list(args) != expected:
        refuse()
    wanted = environment(fixture)
    # Only -e names are container inputs. Unrelated inherited process variables
    # are neither container inputs nor recorded evidence. Routing is checked separately.
    if (any(type(inherited.get(key)) is not str or inherited[key] != value for key, value in wanted.items())
            or any(key in inherited for key in ROUTING_KEYS if key not in wanted)):
        refuse()
    return len(expected) - 3


def _execution_request(fixture):
    """Closed API input, deliberately tighter than CLI host/platform defaults."""
    pins = images.load_pins(dev.read(dev.ROOT / images.PINS))
    postgres = next(item for item in pins['images'] if item['id'] == 'postgres')
    tag = 'public.ecr.aws/' + postgres['repository'] + ':' + postgres['tag']
    selected = fixture['postgres_image']
    if (type(selected) is not str
            or not re.fullmatch(re.escape('public.ecr.aws/' + postgres['repository']) + r'@sha256:[0-9a-f]{64}', selected)
            or type(fixture.get('selection_plan')) is not dict or fixture['selection_plan'].get(tag) != selected):
        refuse()
    project = fixture['project']
    name = 'supabase_db_' + project
    network = fixture['network']['Id']
    return {'method': 'POST',
            'path': '/v1.48/containers/create?name=' + name + '&platform=linux%2Famd64',
            'body': {
                'Image': fixture['postgres_image'],
                'Env': [key + '=' + value for key, value in CONTAINER_ENV.items()],
                'Entrypoint': ['sh'],
                'Cmd': ['-c', dev.read(dev.ROOT / BOOTSTRAP).decode('utf-8')],
                'Labels': {'com.supabase.cli.project': project, 'com.docker.compose.project': project,
                           'com.supabase.cli.workdir': fixture['workdir']},
                'ExposedPorts': {'5432/tcp': {}},
                'Healthcheck': {'Test': ['CMD-SHELL', 'pg_isready -U postgres -h 127.0.0.1 -p 5432'],
                                'Interval': 10000000000, 'Timeout': 2000000000, 'Retries': 3},
                'HostConfig': {
                    'Binds': [name + ':/var/lib/postgresql/data'],
                    'PortBindings': {'5432/tcp': [{'HostIp': '127.0.0.1', 'HostPort': str(fixture['database_port'])}]},
                    'RestartPolicy': {'Name': 'unless-stopped', 'MaximumRetryCount': 0},
                    'ExtraHosts': ['host.docker.internal:host-gateway'], 'NetworkMode': network},
                'NetworkingConfig': {'EndpointsConfig': {network: {'Aliases': ['db', 'db.supabase.internal']}}}}}


def _exact_tree(actual, expected):
    # Python equality alone accepts bool/int and int/float substitutions.
    if type(actual) is not type(expected):
        return False
    if type(expected) is dict:
        return (set(actual) == set(expected)
                and all(type(key) is str for key in actual)
                and all(_exact_tree(actual[key], value) for key, value in expected.items()))
    if type(expected) is list:
        return len(actual) == len(expected) and all(_exact_tree(a, e) for a, e in zip(actual, expected))
    return actual == expected


def validate_execution_request(execution, args, fixture, inherited):
    """Compare every key/type/value against authority, never record rejected input."""
    validate(args, fixture, inherited)
    if not _exact_tree(execution, _execution_request(fixture)):
        refuse()


def execution_request(args, fixture, inherited):
    """Detached tree after caller-owned image/network/volume evidence validation.

    Digest grammar/selection binding cannot establish image-owner provenance.
    No transport or ambient env lookup exists here.
    """
    validate(args, fixture, inherited)
    return _execution_request(fixture)


def disposable_execution_request(args, fixture, inherited):
    """Validate original CLI inputs, then explicitly tighten disposable execution."""
    body = execution_request(args, fixture, inherited)
    host = body['body']['HostConfig']
    host.update(RestartPolicy={'Name': 'no', 'MaximumRetryCount': 0},
                Memory=2147483648, MemorySwap=2147483648, NanoCpus=2000000000,
                PidsLimit=256, LogConfig={'Type': 'none', 'Config': {}}, Privileged=False)
    return body


def auth_environment(fixture):
    """Six source-fixed public synthetic inputs, never observed-input authority."""
    return {'API_EXTERNAL_URL': fixture['origins'][1] + '/auth/v1',
            'GOTRUE_LOG_LEVEL': 'error', 'GOTRUE_DB_DRIVER': 'postgres',
            'GOTRUE_DB_DATABASE_URL': 'postgresql://supabase_auth_admin:postgres@supabase_db_' + fixture['project'] + ':5432/postgres',
            'GOTRUE_SITE_URL': fixture['origins'][0], 'GOTRUE_JWT_SECRET': CONTAINER_ENV['JWT_SECRET']}


def validate_auth_job(args, fixture, inherited):
    """Validate original CLI Auth migration-job input before any admission."""
    if type(inherited) is not dict or type(args) is not list:
        refuse()
    pins = images.load_pins(dev.read(dev.ROOT / images.PINS))
    auth = next(item for item in pins['images'] if item['id'] == 'gotrue')
    tag = 'public.ecr.aws/' + auth['repository'] + ':' + auth['tag']
    selected = fixture['selection_plan'].get(tag)
    observation = fixture['image_observations'].get(selected)
    if (type(selected) is not str or observation is None
            or not re.fullmatch(re.escape('public.ecr.aws/' + auth['repository']) + r'@sha256:[0-9a-f]{64}', selected)):
        refuse()
    env = auth_environment(fixture)
    expected = ['run', '--rm', '--network', fixture['network']['Id'],
                '--add-host', 'host.docker.internal:host-gateway']
    for key in env:
        expected += ['-e', key]
    expected += ['--label', 'com.supabase.cli.project=' + fixture['project'],
                 '--label', 'com.docker.compose.project=' + fixture['project'], tag, 'gotrue', 'migrate']
    routing = environment(fixture)
    wanted = dict(env, **{key: routing[key] for key in ('DOCKER_HOST', 'DOCKER_CONFIG')})
    if (not _exact_tree(args, expected)
            or any(type(inherited.get(key)) is not str or inherited[key] != value for key, value in wanted.items())
            or any(key in inherited for key in ROUTING_KEYS if key not in wanted)):
        refuse()


AUTH_IMAGE_CONFIG = {
    'User': 'supabase',
    'Env': ['PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
            'GOTRUE_DB_MIGRATIONS_PATH=/usr/local/etc/auth/migrations'],
    'Cmd': ['auth'], 'WorkingDir': '/', 'ArgsEscaped': True,
}


def auth_execution_request(args, fixture, inherited):
    """Admit original CLI profile, then construct the one detached bounded job."""
    validate_auth_job(args, fixture, inherited)
    tag = args[-3]
    network = fixture['network']['Id']
    return {'method': 'POST', 'path': '/v1.48/containers/create?name=supabase_auth_migrate_' + fixture['project'] + '&platform=linux%2Famd64',
            'body': {'Image': fixture['selection_plan'][tag],
                     'Env': [key + '=' + value for key, value in auth_environment(fixture).items()],
                     'Cmd': ['gotrue', 'migrate'],
                     'Labels': {'com.supabase.cli.project': fixture['project'],
                                'com.docker.compose.project': fixture['project']},
                     'HostConfig': {'AutoRemove': False, 'NetworkMode': network, 'CgroupnsMode': 'private',
                                    'ExtraHosts': ['host.docker.internal:host-gateway'],
                                    'RestartPolicy': {'Name': 'no', 'MaximumRetryCount': 0},
                                    'Memory': 2147483648, 'MemorySwap': 2147483648,
                                    'NanoCpus': 2000000000, 'PidsLimit': 256,
                                    'LogConfig': {'Type': 'none', 'Config': {}}, 'Privileged': False},
                     'NetworkingConfig': {'EndpointsConfig': {network: {}}}}}


AUTH_IMAGE_API_CONFIG = {
    **AUTH_IMAGE_CONFIG,
    'AttachStderr': False, 'AttachStdin': False, 'AttachStdout': False,
    'Domainname': '', 'Entrypoint': None, 'Hostname': '', 'Image': '',
    'Labels': None, 'OnBuild': None, 'OpenStdin': False, 'StdinOnce': False,
    'Tty': False, 'Volumes': None,
}


def validate_auth_image_config(config):
    """Exact pinned image Config as returned by the selected Docker API 1.48."""
    if not _exact_tree(config, AUTH_IMAGE_API_CONFIG):
        refuse()


KONG_SOURCES = 'platform/deployment/fixtures/supabase-kong-source/'
# Deliberately public markers, never minted JWTs or caller-supplied credentials.
KONG_KEYS = ('public-synthetic-secret-key', 'public-synthetic-service-role-key',
             'public-synthetic-publishable-key', 'public-synthetic-anon-key')
KONG_ENV = {
    'KONG_DATABASE': 'off', 'KONG_DECLARATIVE_CONFIG': '/home/kong/kong.yml',
    'KONG_DNS_ORDER': 'LAST,A,CNAME', 'KONG_DNS_NOT_FOUND_TTL': '1',
    'KONG_DNS_VALID_TTL': '5', 'KONG_PLUGINS': 'request-transformer,cors',
    'KONG_PORT_MAPS': '55481:8000', 'KONG_NGINX_PROXY_PROXY_BUFFER_SIZE': '160k',
    'KONG_NGINX_PROXY_PROXY_BUFFERS': '64 160k', 'KONG_NGINX_WORKER_PROCESSES': '1',
    'KONG_SSL_CERT': '/home/kong/localhost.crt', 'KONG_SSL_CERT_KEY': '/home/kong/localhost.key',
}


def _kong_source(name):
    # Hash only immutable public source authority, never rendered/transfer inputs.
    import json
    manifest = dev.read(dev.ROOT / (KONG_SOURCES + 'sources.json'))
    if dev.digest(manifest) != '054cb89c47d19e55b46eeb5d0c9b4b81d04316ede0facb437c4628ff09b08da1':
        refuse()
    authority = [entry for path, entry in json.loads(manifest).items() if path.rsplit('/', 1)[-1] == name]
    raw = dev.read(dev.ROOT / (KONG_SOURCES + name))
    if len(authority) != 1 or dev.digest(raw) != authority[0]['sha256']:
        refuse()
    return raw.decode('utf-8')


def _kong_literal(name, constant):
    # Closed public upstream JS template literals contain only escaped dollar signs.
    match = re.search(r'export const ' + constant + r' = `([\s\S]*)`;\s*$', _kong_source(name))
    if match is None:
        refuse()
    return match[1].replace('\\$', '$')


def kong_script():
    return ("cat <<'EOF' > /home/kong/custom_nginx.template && \\\n"
            "exec ./docker-entrypoint.sh kong docker-start --nginx-conf /home/kong/custom_nginx.template\n"
            + _kong_literal('custom_nginx.template.ts', 'START_CUSTOM_NGINX_TEMPLATE') + '\nEOF\n')


def _kong_selected(fixture):
    pins = images.load_pins(dev.read(dev.ROOT / images.PINS))
    pin = next(item for item in pins['images'] if item['id'] == 'kong')
    repository = 'public.ecr.aws/' + pin['repository']
    selected = fixture['selection_plan'].get(repository + ':' + pin['tag'])
    observations = fixture['image_observations']
    if (type(selected) is not str or not re.fullmatch(re.escape(repository) + r'@sha256:[0-9a-f]{64}', selected)
            or selected not in observations or type(observations[selected]) is not dict
            or set(observations[selected]) != {'Id', 'Os', 'Architecture'}
            or not re.fullmatch(r'sha256:[0-9a-f]{64}', observations[selected].get('Id', ''))
            or observations[selected]['Os'] != 'linux' or observations[selected]['Architecture'] != 'amd64'
            or type(fixture.get('project')) is not str
            or not re.fullmatch(r'agriplatform-kdg-[A-Za-z0-9_-]{22}', fixture['project'])
            or type(fixture.get('workdir')) is not str or not fixture['workdir'].startswith('/')
            or type(fixture.get('network')) is not dict
            or type(fixture['network'].get('Id')) is not str
            or not re.fullmatch(r'[0-9a-f]{64}', fixture['network']['Id'])):
        refuse()
    return selected


def kong_request(fixture):
    """One source-derived synthetic create intent. This is never execution authority."""
    selected = _kong_selected(fixture)
    project, network = fixture['project'], fixture['network']['Id']
    args = ['create', '--name', 'supabase_kong_' + project]
    for key in KONG_ENV:
        args += ['-e', key]
    args += ['-p', '55481:8000', '--expose', '8000', '--expose', '8443', '--expose', '8088',
             '--restart', 'unless-stopped', '--add-host', 'host.docker.internal:host-gateway',
             '--network', network, '--network-alias', 'kong', '--network-alias', 'api.supabase.internal',
             '--label', 'com.supabase.cli.project=' + project,
             '--label', 'com.docker.compose.project=' + project,
             '--label', 'com.supabase.cli.workdir=' + fixture['workdir'],
             '--entrypoint', 'sh', selected, '-c', kong_script()]
    return args


def kong_execution_request(fixture):
    """Detached source intent; no inherited inputs, secrets or transport."""
    selected = _kong_selected(fixture)
    project, network = fixture['project'], fixture['network']['Id']
    return {'method': 'POST',
            'path': '/v1.48/containers/create?name=supabase_kong_' + project + '&platform=linux%2Famd64',
            'body': {'Image': selected, 'Env': [k + '=' + v for k, v in KONG_ENV.items()],
                     'Entrypoint': ['sh'], 'Cmd': ['-c', kong_script()],
                     'Labels': {'com.supabase.cli.project': project, 'com.docker.compose.project': project,
                                'com.supabase.cli.workdir': fixture['workdir']},
                     'ExposedPorts': {'8000/tcp': {}, '8443/tcp': {}, '8088/tcp': {}},
                     'HostConfig': {'Binds': [],
                                    'PortBindings': {'8000/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '55481'}]},
                                    'RestartPolicy': {'Name': 'unless-stopped', 'MaximumRetryCount': 0},
                                    'ExtraHosts': ['host.docker.internal:host-gateway'], 'NetworkMode': network},
                     'NetworkingConfig': {'EndpointsConfig': {network: {'Aliases': ['kong', 'api.supabase.internal']}}}}}


def kong_transfer_files(fixture):
    """Three in-memory files, including public embedded TLS with API TLS disabled."""
    import json
    _kong_selected(fixture)
    secret, service, publishable, anon = KONG_KEYS
    bearer = ("$((headers.authorization ~= nil and headers.authorization:sub(1, 10) ~= 'Bearer sb_' and headers.authorization) "
              + "or (headers.apikey == '" + secret + "' and 'Bearer " + service + "') "
              + "or (headers.apikey == '" + publishable + "' and 'Bearer " + anon + "') or headers.apikey)")
    query = ("$((query_params.apikey == '" + secret + "' and '" + service + "') "
             + "or (query_params.apikey == '" + publishable + "' and '" + anon + "') or query_params.apikey)")
    fields = {key: 'supabase_' + suffix + '_' + fixture['project'] for key, suffix in
              [('GotrueId', 'auth'), ('RestId', 'rest'), ('StorageId', 'storage'), ('StudioId', 'studio'),
               ('PgmetaId', 'pg_meta'), ('EdgeRuntimeId', 'edge_runtime'), ('LogflareId', 'analytics'), ('PoolerId', 'pooler')]}
    fields.update(RealtimeId='realtime-dev', ApiHost='127.0.0.1', ApiPort='55481', BearerToken=bearer, QueryToken=query)
    template = _kong_literal('kong.yml.ts', 'START_KONG_YML_TEMPLATE')
    config = re.sub(r'\{\{\s*\.(\w+)\s*\}\}', lambda match: fields[match[1]], template).encode()
    tls = _kong_source('kong-local-tls.ts')
    def embedded(constant):
        match = re.search(r'export const ' + constant + r' =\s*("(?:[^"\\]|\\.)*");', tls)
        if match is None:
            refuse()
        return json.loads(match[1]).encode()
    return {'home/kong/kong.yml': config, 'home/kong/localhost.crt': embedded('KONG_LOCAL_TLS_CERT'),
            'home/kong/localhost.key': embedded('KONG_LOCAL_TLS_KEY')}


def validate_kong_intent(args, environment, execution, files, fixture):
    """Every key/type/byte is closed; rejected input is never formatted or hashed."""
    if (not _exact_tree(args, kong_request(fixture)) or not _exact_tree(environment, dict(KONG_ENV))
            or not _exact_tree(execution, kong_execution_request(fixture))
            or not _exact_tree(files, kong_transfer_files(fixture))):
        refuse()
