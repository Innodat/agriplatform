"""Independent public test inputs; no TestCase lifecycle or validator builders."""
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'platform/deployment'))
import dev
import startup

def expected_environment(f):
    return {'POSTGRES_PASSWORD': 'postgres', 'POSTGRES_HOST': '/var/run/postgresql',
            'JWT_SECRET': 'super-secret-jwt-token-with-at-least-32-characters-long', 'JWT_EXP': '3600',
            'DOCKER_HOST': 'unix://' + f['workdir'] + '/no-daemon.sock',
            'DOCKER_CONFIG': f['workdir'] + '/docker'}


def expected_request(f):
    p = f['project']
    script = (ROOT / 'platform/deployment/fixtures/supabase-pg17-bootstrap.txt').read_text()
    return ['create', '--name', 'supabase_db_' + p,
            '-e', 'POSTGRES_PASSWORD', '-e', 'POSTGRES_HOST', '-e', 'JWT_SECRET', '-e', 'JWT_EXP',
            '-v', 'supabase_db_' + p + ':/var/lib/postgresql/data', '-p', str(f['database_port']) + ':5432',
            '--health-cmd', 'pg_isready -U postgres -h 127.0.0.1 -p 5432', '--health-interval', '10s',
            '--health-timeout', '2s', '--health-retries', '3', '--restart', 'unless-stopped',
            '--add-host', 'host.docker.internal:host-gateway', '--network', f['network']['Id'],
            '--network-alias', 'db', '--network-alias', 'db.supabase.internal',
            '--label', 'com.supabase.cli.project=' + p, '--label', 'com.docker.compose.project=' + p,
            '--label', 'com.supabase.cli.workdir=' + f['workdir'], '--entrypoint', 'sh',
            f['postgres_image'], '-c', script]


RUN = 'b3b805d5-adc6-4168-a79c-5945547d3320'


def test_plan():
    # Independent child bytes: index and config digests are deliberately different.
    import test_images
    pins = startup.images.load_pins(dev.read(ROOT / startup.images.PINS))
    return {'public.ecr.aws/' + item['repository'] + ':' + item['tag']:
            'public.ecr.aws/' + item['repository'] + '@sha256:' + dev.digest(test_images.fixture(item['id'])[1])
            for item in pins['images']}


def test_observations():
    import test_images
    pins = startup.images.load_pins(dev.read(ROOT / startup.images.PINS))
    return {child: {'Id': json.loads(test_images.fixture(item['id'])[1])['config']['digest'],
                    'Os': 'linux', 'Architecture': 'amd64'}
            for item, child in zip(pins['images'], test_plan().values())}


SYNTHETIC_CLI_SOURCE = '''import json, os, subprocess, sys
from pathlib import Path
work = Path(sys.argv[sys.argv.index('--workdir')+1])
f = json.loads((work/'fixture.json').read_text())
p = f['project']
sys.path.insert(0, __PROFILE_TESTS__)
from create_profile_fixtures import expected_request, expected_environment
args = expected_request(f)
os.environ.update(expected_environment(f))
assert os.environ['PATH'] == str(work/'bin')
assert os.environ['DOCKER_HOST'] == 'unix://'+str(work/'no-daemon.sock')
assert 'DOCKER_CONTEXT' not in os.environ
assert 'SUPABASE_DB_PASSWORD' not in os.environ
commands = [['container','inspect','supabase_db_'+p,'--format','{{json .State}}']]
commands += [['image','inspect',image] for image in f['images']]
commands += [['volume','inspect','supabase_db_'+p], ['network','inspect',f['network']['Id']],
             ['volume','create','--label','com.supabase.cli.project='+p,'--label',
              'com.docker.compose.project='+p,'supabase_db_'+p]]
for command in commands:
    subprocess.run(['docker',*command], start_new_session=True)
code = subprocess.run(['docker',*args], start_new_session=True).returncode
(work/'forbidden_after_create').write_text('cleanup must never run')
sys.exit(code)
'''.replace('__PROFILE_TESTS__', repr(str(ROOT / 'platform/deployment/tests')))

def target_fixture():
    return dev.decode(dev.read(ROOT / 'platform/deployment/environments/kdg-local.json'))


def boundary_fixture():
    target = target_fixture()
    return {'target_id': target['target_id'], 'run_id': RUN,
            'volume': startup.fixture_volume(target, RUN), 'project': dev.project_identity(target, RUN),
            'workdir': '/private', 'network': startup.fixture_network(target, RUN),
            'executable': '/does-not-exist', 'database_port': 55482,
            'postgres_image': 'public.ecr.aws/supabase/postgres:17.11.0.004',
            'images': ['public.ecr.aws/supabase/postgres:17.11.0.004'],
            'selection_plan': test_plan(), 'image_observations': test_observations()}


def expected_execution_request(f):
    """Full independent Docker API oracle; never calls the production builder."""
    p = f['project']
    network = f['network']['Id']
    name = 'supabase_db_' + p
    return {'method': 'POST',
            'path': '/v1.48/containers/create?name=' + name + '&platform=linux%2Famd64',
            'body': {'Image': f['postgres_image'],
                     'Env': ['POSTGRES_PASSWORD=postgres', 'POSTGRES_HOST=/var/run/postgresql',
                             'JWT_SECRET=super-secret-jwt-token-with-at-least-32-characters-long', 'JWT_EXP=3600'],
                     'Entrypoint': ['sh'],
                     'Cmd': ['-c', (ROOT / 'platform/deployment/fixtures/supabase-pg17-bootstrap.txt').read_text()],
                     'Labels': {'com.supabase.cli.project': p, 'com.docker.compose.project': p,
                                'com.supabase.cli.workdir': f['workdir']},
                     'ExposedPorts': {'5432/tcp': {}},
                     'Healthcheck': {'Test': ['CMD-SHELL', 'pg_isready -U postgres -h 127.0.0.1 -p 5432'],
                                     'Interval': 10000000000, 'Timeout': 2000000000, 'Retries': 3},
                     'HostConfig': {'Binds': [name + ':/var/lib/postgresql/data'],
                                    'PortBindings': {'5432/tcp': [{'HostIp': '127.0.0.1', 'HostPort': str(f['database_port'])}]},
                                    'RestartPolicy': {'Name': 'unless-stopped', 'MaximumRetryCount': 0},
                                    'ExtraHosts': ['host.docker.internal:host-gateway'], 'NetworkMode': network},
                     'NetworkingConfig': {'EndpointsConfig': {network: {'Aliases': ['db', 'db.supabase.internal']}}}}}
