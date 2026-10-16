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
