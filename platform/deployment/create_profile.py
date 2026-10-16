"""Exact Linux PG17 first-create profile for Supabase CLI 2.120.0.

Only compares public bootstrap bytes; never hashes or emits runtime input.
Authority and derivation: fixtures/supabase-pg17-profile.md.
"""
from pathlib import Path

import dev

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
