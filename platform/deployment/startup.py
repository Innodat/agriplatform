"""Guarded ENV startup boundaries and explicit pinned-CLI PostgreSQL proof.

Default controls use synthetic descriptors and refuse execution. The explicit
qualifier retains real owner observations through its first PostgreSQL start,
health, clean shutdown and disposable cleanup. Public dev.py up remains gated.
"""
from contextlib import contextmanager, ExitStack
import json
import base64
import os
from pathlib import Path
import re
import signal
import socket
import selectors
import struct
import subprocess
import stat
import sys
import time
import tempfile
import uuid

import dev
import copy
import create_profile
import startup_lifecycle as lifecycle
import images
import toolchain

SOURCE = 'platform/deployment/startup.py'
LIMIT = 65536
LABEL_PREFIX = 'io.agriplatform.env.'
BINDING = 'com.docker.network.bridge.host_binding_ipv4'
FIXTURE_SECONDS = 5
LOCK_SECONDS = .5
CREATE_BOUNDARY = 9  # Eight exact prerequisites followed by the validated create.
PROOF_SOURCES = [SOURCE, 'platform/deployment/tests/qualify_startup.py',
                 'platform/deployment/dev.py', 'platform/deployment/images.py', images.PINS,
                 'platform/deployment/toolchain.py', toolchain.PINS]


def source_snapshot():
    return {name: dev.digest(dev.read(dev.ROOT / name)) for name in sorted(set(PROOF_SOURCES + dev.SOURCES))}


def check_root(work, fd):
    held = os.fstat(fd)
    current = os.stat(work, follow_symlinks=False)
    if (not stat.S_ISDIR(current.st_mode) or current.st_uid != os.getuid()
            or stat.S_IMODE(current.st_mode) != 0o700
            or (current.st_dev, current.st_ino) != (held.st_dev, held.st_ino)):
        fail('workdir_identity_changed')


@contextmanager
def work_anchor(work):
    with dev.directory(work) as fd:
        check_root(work, fd)
        yield fd
        check_root(work, fd)


def fail(code):
    dev.refuse('startup', code)


class ExecutableCustody:
    """Retain one executable across owner byte verification; checks never rehash it."""
    def __init__(self, path, parent, descriptor, execution_path):
        self.path, self.parent, self.descriptor = path, parent, descriptor
        self.execution_path = execution_path
        self.parent_identity = os.fstat(parent)
        self.identity = os.fstat(descriptor)
        info = self.identity
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o700):
            fail('tool_payload_changed')
        self.check()

    @staticmethod
    def signature(info):
        return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_nlink,
                info.st_size, info.st_mtime_ns, info.st_ctime_ns)

    def check(self):
        try:
            with dev.directory(self.path.parent) as current:
                now = os.fstat(current)
                dev.check_private(current)
                if (now.st_dev, now.st_ino) != (self.parent_identity.st_dev, self.parent_identity.st_ino):
                    fail('tool_payload_changed')
            actual = os.stat(self.path.name, dir_fd=self.parent, follow_symlinks=False)
            if (self.signature(actual) != self.signature(self.identity)
                    or self.signature(os.stat(self.execution_path)) != self.signature(self.identity)
                    or self.signature(os.fstat(self.descriptor)) != self.signature(self.identity)):
                fail('tool_payload_changed')
        except OSError:
            fail('tool_payload_changed')


@contextmanager
def executable_custody(executable):
    """Bind before existing owner preflight verifies payload bytes, then retain it.

    That preflight remains the qualified-byte authority. Unchanged held/path
    identity, size, mode, mtime and ctime bind its result without hashing the
    large executable or entire payload again at each daemon exchange.
    """
    execution_path = Path(executable)
    # The existing qualified caller deliberately uses its held /proc/PID/fd
    # payload alias. Anchor the resolved directory while also rechecking that
    # exact launch alias against the same held executable identity.
    path = execution_path.resolve(strict=True)
    with dev.directory(path.parent) as parent:
        descriptor = os.open(path.name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=parent)
        try:
            yield ExecutableCustody(path, parent, descriptor, execution_path)
        finally:
            os.close(descriptor)


def labels(target, run_id):
    return {LABEL_PREFIX + 'owner': 'platform/deployment', LABEL_PREFIX + 'target': target['target_id'],
            LABEL_PREFIX + 'run': run_id, LABEL_PREFIX + 'project': dev.project_identity(target, run_id)}


def fixture_volume(target, run_id):
    """Synthetic profile only; acquisition is required for a daemon observation."""
    project = dev.project_identity(target, run_id)
    return {'Name': 'supabase_db_' + project, 'Driver': 'local', 'Scope': 'local',
            'Labels': dict(labels(target, run_id), **{'com.supabase.cli.project': project,
                          'com.docker.compose.project': project}), 'Options': None}


def volume_descriptor(actual, target, run_id):
    """Select safety/continuity evidence; never expose or follow Mountpoint."""
    expected = fixture_volume(target, run_id)
    if type(actual) is not dict or 'ClusterVolume' in actual:
        dev.refuse('volume', 'volume_not_run_owned')
    for key in ['Name', 'Driver', 'Scope', 'Labels']:
        if key not in actual or type(actual[key]) is not type(expected[key]) or actual[key] != expected[key]:
            dev.refuse('volume', 'volume_not_run_owned')
    if 'Options' not in actual or not (actual['Options'] is None or
            (type(actual['Options']) is dict and not actual['Options'])):
        dev.refuse('volume', 'volume_not_run_owned')
    result = {key: actual[key] for key in expected}
    if 'CreatedAt' in actual:
        if type(actual['CreatedAt']) is not str or len(actual['CreatedAt']) > 128:
            dev.refuse('volume', 'volume_not_run_owned')
        result['CreatedAt'] = actual['CreatedAt']
    return result


def validate_fixture_volume(fixture):
    if type(fixture.get('fresh', False)) is not bool:
        fail('fresh_volume_required')
    if fixture.get('fresh'):
        if ('volume' in fixture or 'planned_volume' not in fixture
                or type(fixture.get('fresh_existing', False)) is not bool
                or type(fixture.get('fresh_racing', False)) is not bool):
            fail('fresh_volume_required')
    elif 'planned_volume' in fixture:
        fail('fresh_volume_required')
    project = fixture['project']
    run_id = fixture['run_id']
    suffix = '-' + base64.urlsafe_b64encode(uuid.UUID(run_id).bytes).decode().rstrip('=')
    if not project.endswith(suffix):
        dev.refuse('volume', 'volume_not_run_owned')
    target = {'target_id': fixture['target_id'], 'project_id_prefix': project[:-len(suffix)]}
    if fixture.get('fresh') and not create_profile._exact_tree(fixture['planned_volume'], fixture_volume(target, run_id)):
        fail('fresh_volume_required')
    result = volume_descriptor(fixture.get('planned_volume') if fixture.get('fresh') else fixture.get('volume'), target, run_id)
    return result


def fixture_network(target, run_id):
    return {'Name': dev.project_identity(target, run_id) + '-network',
            'Id': 'env-fixture-' + run_id, 'Driver': 'bridge', 'Scope': 'local',
            'Internal': False, 'Options': {BINDING: '127.0.0.1'},
            'Labels': labels(target, run_id), 'Containers': {}}


def validate_network(network, target, run_id):
    if (type(network) is not dict or set(network) != set(fixture_network(target, run_id))
            or network['Name'] != dev.project_identity(target, run_id) + '-network'
            or type(network['Id']) is not str
            or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', network['Id'])
            or network['Driver'] != 'bridge' or network['Scope'] != 'local'
            or network['Internal'] is not False or network['Containers'] != {}
            or network['Options'] != {BINDING: '127.0.0.1'}
            or network['Labels'] != labels(target, run_id)):
        fail('network_not_run_owned')
    return network['Id']


def write_private(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)


def initialize_workdir(work, target, run_id):
    with work_anchor(work) as root:
        if os.listdir(root):
            fail('workdir_not_empty')
        for name in ['supabase', 'state', 'config', 'cache', 'tmp', 'bin', 'docker']:
            os.mkdir(name, mode=0o700, dir_fd=root)
        supabase = os.open('supabase', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root)
        try:
            fd = os.open('config.toml', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=supabase)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(dev.configuration(target, run_id))
        finally:
            os.close(supabase)


def check_workdir(work, target, run_id, after=False, fixture=False):
    with work_anchor(work):
        _check_workdir(work, target, run_id, after, fixture)


def _check_workdir(work, target, run_id, after=False, fixture=False):
    expected = {'supabase', 'state', 'config', 'cache', 'tmp', 'bin', 'docker'}
    if fixture:
        expected |= {'fixture.json', 'events.json'}
    if set(os.listdir(work)) != expected:
        fail('workdir_contaminated')
    for directory in ['state', 'config', 'cache', 'tmp', 'docker', 'bin']:
        root = work / directory
        with dev.directory(root) as private:
            dev.check_private(private)
        if directory == 'bin' and set(os.listdir(root)) != ({'docker', 'podman'} if fixture else set()):
            fail('workdir_contaminated')
        count = 0
        for base, directories, files in os.walk(root, followlinks=False):
            count += len(directories) + len(files)
            if count > 128:
                fail('workdir_contaminated')
            for name in directories + files:
                entry = Path(base) / name
                info = entry.lstat()
                if entry.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o022:
                    fail('workdir_contaminated')
                if entry.is_file() and (info.st_size > 1024 * 1024 or info.st_nlink != 1):
                    fail('workdir_contaminated')
    with dev.directory(work / 'supabase') as fd:
        dev.check_private(fd)
        names = set(os.listdir(fd))
        if names not in ([{'config.toml'}, {'config.toml', '.temp'}] if after else [{'config.toml'}]):
            fail('workdir_contaminated')
        if dev.read_at(fd, 'config.toml', protected=True) != dev.configuration(target, run_id):
            fail('configuration_changed')
        if '.temp' in names:
            with dev.directory(work / 'supabase/.temp') as temporary:
                if set(os.listdir(temporary)) - {'cli-latest'}:
                    fail('workdir_contaminated')
                if 'cli-latest' in os.listdir(temporary) and len(dev.read_at(temporary, 'cli-latest')) > 128:
                    fail('workdir_contaminated')


def invocation(executable, work, target, run_id, network):
    network_id = validate_network(network, target, run_id)
    check_workdir(work, target, run_id)
    env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C.UTF-8', 'CI': '1',
           'SUPABASE_WORKDIR': str(work), 'SUPABASE_HOME': str(work / 'state'),
           'XDG_CONFIG_HOME': str(work / 'config'), 'XDG_CACHE_HOME': str(work / 'cache'),
           'TMPDIR': str(work / 'tmp'), 'DOCKER_CONFIG': str(work / 'docker'),
           'DOCKER_HOST': 'unix:///var/run/docker.sock',
           'SUPABASE_TELEMETRY_DISABLED': '1', 'NO_UPDATE_NOTIFIER': '1', 'NO_COLOR': '1',
           'SUPABASE_EXPERIMENTAL_STACK': '0', 'SUPABASE_USE_SLIM_IMAGES': '0',
           'SUPABASE_INTERNAL_IMAGE_REGISTRY': 'public.ecr.aws'}
    return [str(executable), 'start', '--agent', 'no', '--workdir', str(work), '--network-id', network_id], env


def existing_images(args):
    """Require existing evidence before calling owner repeat qualification.

    The owner takes transient locks and executes installed-tool probes. This is
    deliberately not a read-only operation and cannot install/refresh absent evidence.
    """
    root = dev.ROOT / 'platform/deployment/.local/kdg-base-images' / args.run_id
    try:
        with toolchain.anchored_directory(root) as (fd, _):
            receipt = dev.read_at(fd, 'receipt.json', protected=True)
            identity = os.stat('receipt.json', dir_fd=fd, follow_symlinks=False)
            if ('.qualify.lock' in os.listdir(fd) or '.receipt-pending' in os.listdir(fd)
                    or dev.decode(receipt).get('base_identities_ready') is not True):
                fail('existing_images_required')
            before = evidence_snapshot(fd)
            result = images.qualify(args, existing_only=True)
            current = os.stat('receipt.json', dir_fd=fd, follow_symlinks=False)
            if (not result.get('base_identities_ready') or dev.read_at(fd, 'receipt.json', protected=True) != receipt
                    or (current.st_dev, current.st_ino) != (identity.st_dev, identity.st_ino)
                    or not toolchain.anchor_current(root, fd) or evidence_snapshot(fd) != before):
                fail('image_verification_refused')
    except FileNotFoundError:
        fail('existing_images_required')
    plan = result['selection_plan']
    validate_selection_plan(plan)
    config_plan = result['config_plan']
    if (type(config_plan) is not dict or set(config_plan) != set(plan.values())
            or any(type(value) is not str or not re.fullmatch(r'sha256:[0-9a-f]{64}', value)
                   for value in config_plan.values())):
        fail('invalid_config_plan')
    return dev.digest(receipt), plan, before, config_plan


def evidence_snapshot(fd):
    result = {}
    for name in os.listdir(fd):
        held = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        try:
            info = os.fstat(held)
            if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
                    or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600):
                fail('image_verification_refused')
            raw = b''
            while len(raw) <= dev.LIMIT:
                chunk = os.read(held, dev.LIMIT + 1 - len(raw))
                if not chunk:
                    break
                raw += chunk
            current = os.stat(name, dir_fd=fd, follow_symlinks=False)
            after = os.fstat(held)
            if (len(raw) > dev.LIMIT
                    or (info.st_mode, info.st_uid, info.st_nlink, info.st_size)
                    != (after.st_mode, after.st_uid, after.st_nlink, after.st_size)
                    or info.st_mtime_ns != after.st_mtime_ns or info.st_ctime_ns != after.st_ctime_ns
                    or (current.st_dev, current.st_ino) != (info.st_dev, info.st_ino)):
                fail('image_verification_refused')
            result[name] = (info.st_dev, info.st_ino, info.st_mode, info.st_uid,
                            info.st_mtime_ns, info.st_ctime_ns, dev.digest(raw))
        finally:
            os.close(held)
    return result


def decode_fixture(path):
    with dev.directory(path.parent) as fd:
        raw = dev.read_at(fd, path.name, protected=True)
    if len(raw) > LIMIT:
        fail('fixture_too_large')
    return dev.decode(raw)


def create_facts(args, fixture, *, environment, image_index=False):
    """Validate all inputs, then extract only safe selected facts."""
    index = create_profile.validate(args, fixture, environment)
    return index if image_index else selected_facts(fixture)


def validate_selection_plan(plan):
    pins = images.load_pins(dev.read(dev.ROOT / images.PINS))
    expected = {'public.ecr.aws/' + item['repository'] + ':' + item['tag']:
                'public.ecr.aws/' + item['repository'] for item in pins['images']}
    if (type(plan) is not dict or set(plan) != set(expected)
            or any(type(plan[tag]) is not str or not re.fullmatch(re.escape(repository) + r'@sha256:[0-9a-f]{64}', plan[tag])
                   for tag, repository in expected.items())
            or len({value.rsplit('@', 1)[1] for value in plan.values()}) != 4):
        fail('invalid_selection_plan')


def immutable_first_create(args, fixture, plan, *, environment):
    """Internal construction only; plan must already be verified by the image owner.

    Structural validation here cannot establish manifest provenance. The public
    qualify path obtains and rechecks owner evidence around the process proof.
    No dispatch is available from this constructor.
    """
    validate_selection_plan(plan)
    original = tuple(args)
    inherited = copy.deepcopy(environment)
    index = create_facts(original, fixture, environment=inherited, image_index=True)
    pins = images.load_pins(dev.read(dev.ROOT / images.PINS))
    postgres = next(item for item in pins['images'] if item['id'] == 'postgres')
    expected = 'public.ecr.aws/' + postgres['repository'] + ':' + postgres['tag']
    if fixture['postgres_image'] != expected:
        fail('invalid_selection_plan')
    selected = list(original)
    selected[index] = plan[original[index]]
    selected_fixture = dict(fixture, postgres_image=selected[index])
    create_facts(selected, selected_fixture, environment=inherited)
    if tuple(args) != original or environment != inherited:
        fail('unsafe_create')
    return selected


def selected_facts(fixture):
    project = fixture['project']
    return {'image': fixture['postgres_image'], 'name': 'supabase_db_' + project,
            'network': fixture['network']['Id'], 'publish': str(fixture['database_port']) + ':5432',
            'database_volume': 'supabase_db_' + project, 'host_bind_mounts': False,
            'create_refused': not fixture.get('lifecycle', False), 'complete_create_profile_proven': True}


def lifecycle_control_event(control):
    return {'kind': 'lifecycle_control_injected', 'control': control, 'baseline_validated': True}


def lifecycle_prefix(fixture, events, phase):
    facts = selected_facts(dict(fixture, postgres_image=fixture['selection_plan'][fixture['postgres_image']]))
    facts.update(original_image=fixture['postgres_image'], immutable_selection_proven=True, create_request_proven=True)
    descriptors = [fixture['image_observations'][fixture['selection_plan'][tag]] for tag in fixture['images']]
    if phase == 'create':
        validate_observations(events + [{'kind': 'postgres_create', 'facts': facts}], facts, descriptors, fresh=fixture.get('fresh', False), initialized=fixture.get('initialized', False))
    else:
        validate_observations(events[:CREATE_BOUNDARY], facts, descriptors, fresh=fixture.get('fresh', False), initialized=fixture.get('initialized', False))
        if phase == 'cp' and len(events) != CREATE_BOUNDARY:
            fail('unsafe_lifecycle')
        if phase == 'start' and (len(events) != CREATE_BOUNDARY + 1 or events[CREATE_BOUNDARY] != lifecycle.transfer_event()):
            fail('unsafe_lifecycle')


def fixture_command(runtime, args, fixture, events, *, environment=None, archive=None, corrupt_request=False):
    if (type(args) not in (list, tuple) or any(type(a) is not str for a in args)
            or len(args) > 256 or sum(len(a) for a in args) > LIMIT or len(events) >= 64
            or runtime != 'docker'):
        fail('unexpected_container_command')
    project = fixture['project']
    if fixture.get('auth_boundary') and len(events) >= CREATE_BOUNDARY + 2:
        poststart_prefix(fixture, events)
        if args == ['container', 'inspect', 'supabase_db_' + project, '--format', '{{json .State}}']:
            state = owner_handoff(fixture, 'poststart_health', args, environment)
            events.append({'kind': 'postgres_health', 'health': state['Health']['Status']})
            return 0, json.dumps(state), ''
        auth = next(tag for tag in fixture['images'] if '/gotrue:' in tag)
        if args == ['image', 'inspect', auth]:
            owner_handoff(fixture, 'poststart_image', args, environment)
            observed = fixture['image_observations'][fixture['selection_plan'][auth]]
            events.append({'kind': 'auth_image_inspect'})
            return 0, json.dumps([observed]), ''
        if args[:1] == ['run']:
            create_profile.validate_auth_job(args, fixture, environment)
            owner_handoff(fixture, 'auth_job', args, environment)
            fail('auth_job_refused')
        fail('unexpected_container_command')
    if 'fresh' in fixture or 'planned_volume' in fixture:
        validate_fixture_volume(fixture)
    if fixture.get('lifecycle'):
        if args[:1] == ['cp']:
            lifecycle_prefix(fixture, events, 'cp')
            if args != ['cp', '-', lifecycle.CONTAINER_ID + ':/']:
                fail('unsafe_lifecycle')
            lifecycle.validate_archive(archive)
            events.append(lifecycle.transfer_event())
            return 0, '', ''
        if args[:1] == ['start']:
            lifecycle_prefix(fixture, events, 'start')
            if args != ['start', lifecycle.CONTAINER_ID]:
                fail('unsafe_lifecycle')
            events.append({'kind': 'postgres_start_refused'})
            return 125, '', 'ENV synthetic start refused'
        if len(events) >= CREATE_BOUNDARY:
            fail('unsafe_lifecycle')
    if tuple(args[:1]) == ('create',) or tuple(args[:2]) == ('image', 'inspect'):
        validate_image_observations(fixture.get('image_observations'), fixture['selection_plan'])
    if tuple(args[:1]) == ('create',):
        validate_fixture_volume(fixture)
        suffix = '-' + base64.urlsafe_b64encode(uuid.UUID(fixture['run_id']).bytes).decode().rstrip('=')
        validate_network(fixture['network'], {'target_id': fixture['target_id'],
                         'project_id_prefix': fixture['project'][:-len(suffix)]}, fixture['run_id'])
        if type(environment) is not dict:
            fail('unsafe_create')
        original = tuple(args)
        inherited = copy.deepcopy(environment)
        held_fixture = copy.deepcopy(fixture)
        index = create_facts(original, held_fixture, environment=inherited, image_index=True)
        expected = list(original)
        expected[index] = held_fixture['selection_plan'][held_fixture['postgres_image']]
        transform_args, transform_env = list(original), copy.deepcopy(inherited)
        selected = immutable_first_create(transform_args, held_fixture, held_fixture['selection_plan'],
                                          environment=transform_env)
        if (selected != expected or tuple(args) != original or tuple(transform_args) != original
                or not create_profile._exact_tree(environment, inherited)
                or not create_profile._exact_tree(transform_env, inherited)
                or not create_profile._exact_tree(fixture, held_fixture)):
            fail('unsafe_create')
        selected_fixture = dict(held_fixture, postgres_image=selected[index])
        facts = create_facts(selected, selected_fixture, environment=inherited)
        request_args, request_fixture, request_env = copy.deepcopy((selected, selected_fixture, inherited))
        try:
            execution = create_profile.execution_request(request_args, request_fixture, request_env)
            if (request_args != selected or not create_profile._exact_tree(request_fixture, selected_fixture)
                    or not create_profile._exact_tree(request_env, inherited) or tuple(args) != original
                    or not create_profile._exact_tree(environment, inherited)
                    or not create_profile._exact_tree(fixture, held_fixture)):
                fail('unsafe_create')
            create_profile.validate_execution_request(execution, selected, selected_fixture, inherited)
        except dev.Refusal:
            if corrupt_request:
                fail('invalid_control_baseline')
            raise
        if corrupt_request:
            # Qualifier-only negative control: unchanged baseline passed first.
            execution['body']['HostConfig']['PortBindings']['5432/tcp'][0]['HostIp'] = '0.0.0.0'
            create_profile.validate_execution_request(execution, selected, selected_fixture, inherited)
        facts['create_request_proven'] = True
        facts['original_image'] = fixture['postgres_image']
        facts['immutable_selection_proven'] = True
        if fixture.get('lifecycle'):
            lifecycle_prefix(fixture, events, 'create')
        events.append({'kind': 'postgres_create', 'facts': facts})
        if fixture.get('lifecycle'):
            return 0, lifecycle.CONTAINER_ID + '\n', ''
        return 125, '', 'ENV synthetic create refused'
    if args == ['container', 'inspect', 'supabase_db_' + project, '--format', '{{json .State}}']:
        events.append({'kind': 'container_inspect'})
        return 1, '', 'Error: No such container'
    if len(args) == 3 and args[:2] == ['image', 'inspect'] and args[-1] in fixture['images']:
        observed = fixture['image_observations'][fixture['selection_plan'][args[-1]]]
        events.append({'kind': 'image_inspect', 'image_index': fixture['images'].index(args[-1]),
                       'descriptor': observed})
        return 0, json.dumps([observed]), ''
    if args == ['network', 'inspect', fixture['network']['Id']]:
        events.append({'kind': 'network_inspect'})
        return 0, json.dumps([fixture['network']]), ''
    if args == ['volume', 'inspect', 'supabase_db_' + project]:
        if fixture.get('initialized'):
            if len(events) != 5:
                fail('unsafe_lifecycle')
            owner_handoff(fixture, 'initialized_probe', args, environment)
        if fixture.get('fresh'):
            if len(events) != 5 or fixture.get('fresh_existing'):
                fail('fresh_volume_required')
            if fixture.get('guarded_owner'):
                owner_handoff(fixture, 'probe', args, environment)
            # This probe truthfully reports the private fixture's absent state.
            events.append({'kind': 'volume_missing'})
            return 1, '', 'Error: No such volume'
        events.append({'kind': 'volume_inspect'})
        return 0, json.dumps([validate_fixture_volume(fixture)]), ''
    volume = 'supabase_db_' + project
    if args == ['volume', 'create', '--label', 'com.supabase.cli.project=' + project,
                '--label', 'com.docker.compose.project=' + project, volume]:
        validate_fixture_volume(fixture)
        if fixture.get('fresh'):
            expected = [{'kind': 'volume_missing'}, {'kind': 'network_inspect'}]
            if len(events) != 7 or events[5:] != expected:
                fail('unsafe_lifecycle')
            # Validate the whole baseline before acknowledging synthetic creation.
            facts = selected_facts(dict(fixture, postgres_image=fixture['selection_plan'][fixture['postgres_image']]))
            facts.update(original_image=fixture['postgres_image'], immutable_selection_proven=True, create_request_proven=True)
            descriptors = [fixture['image_observations'][fixture['selection_plan'][tag]] for tag in fixture['images']]
            validate_observations(events + [{'kind': 'fresh_volume_create_acknowledged'}, {'kind': 'postgres_create', 'facts': facts}], facts, descriptors, fresh=True)
            if fixture.get('fresh_racing'):
                fail('fresh_volume_required')
            if fixture.get('guarded_owner'):
                owner_handoff(fixture, 'create', args, environment)
            events.append({'kind': 'fresh_volume_create_acknowledged'})
            return 0, volume + '\n', ''
        if fixture.get('initialized'):
            facts = selected_facts(dict(fixture, postgres_image=fixture['selection_plan'][fixture['postgres_image']]))
            facts.update(original_image=fixture['postgres_image'], immutable_selection_proven=True, create_request_proven=True)
            validate_observations(events + [{'kind': 'initialized_volume_ensure_acknowledged'}, {'kind': 'postgres_create', 'facts': facts}], facts,
                                  [fixture['image_observations'][fixture['selection_plan'][tag]] for tag in fixture['images']], initialized=True)
            owner_handoff(fixture, 'initialized_ensure', args, environment)
            events.append({'kind': 'initialized_volume_ensure_acknowledged'})
            return 0, volume + '\n', ''
        events.append({'kind': 'existing_volume_create_refused'})
        return 1, '', 'volume already exists'
    fail('unexpected_container_command')


def parent_identity(fixture):
    parent = os.getppid()
    if not hasattr(os, 'pidfd_open') or not hasattr(signal, 'pidfd_send_signal'):
        fail('fixture_parent_not_isolated')
    # Pin the process before observing /proc, preventing PID reuse from retargeting a signal.
    parent_fd = os.pidfd_open(parent)
    try:
        if os.stat(f'/proc/{parent}').st_uid != os.getuid():
            fail('fixture_parent_not_isolated')
        if os.getsid(parent) != parent:
            fail('fixture_parent_session')
        if os.getpgid(parent) != parent:
            fail('fixture_parent_group')
        executable = Path(fixture['executable']).resolve()
        expected = [fixture['executable'], 'start', '--agent', 'no', '--workdir', fixture['workdir'],
                    '--network-id', fixture['network']['Id']]
        with open(f'/proc/{parent}/cmdline', 'rb') as stream:
            raw = stream.read(LIMIT + 1)
        if len(raw) > LIMIT:
            fail('fixture_parent_not_isolated')
        actual = [value.decode() for value in raw.rstrip(b'\0').split(b'\0')]
        native = Path(os.readlink(f'/proc/{parent}/exe')).resolve()
        if not ((actual[1:] == expected[1:] and native == executable)
                or (actual == [sys.executable, *expected] and native == Path(sys.executable).resolve())):
            fail('fixture_parent_identity')
        if os.getppid() != parent:
            fail('fixture_parent_identity')
        # Signal 0 checks that this exact pinned process is still alive and signalable.
        signal.pidfd_send_signal(parent_fd, 0)
        return parent_fd
    except BaseException:
        os.close(parent_fd)
        raise


def check_event_file(root, fd):
    info = os.fstat(fd)
    path = os.stat('events.json', dir_fd=root, follow_symlinks=False)
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1 or info.st_size > LIMIT
            or (path.st_dev, path.st_ino) != (info.st_dev, info.st_ino)):
        fail('fixture_state_unsafe')


@contextmanager
def event_file(directory):
    import fcntl
    with work_anchor(directory) as root:
        fd = os.open('events.json', os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=root)
        try:
            check_event_file(root, fd)
            deadline = time.monotonic() + LOCK_SECONDS
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        fail('fixture_lock_deadline')
                    time.sleep(.01)
            check_event_file(root, fd)
            with os.fdopen(fd, 'r+b', closefd=False) as stream:
                yield root, stream
                check_event_file(root, fd)
        finally:
            os.close(fd)


def rejected_event(args, code):
    verbs = {'container', 'image', 'network', 'volume', 'inspect', 'version', 'info',
             'ps', 'ls', 'create', 'cp', 'pull', 'run', 'start', 'rm', 'stop', 'prune'}
    flags = {'--format', '--filter', '--quiet', '-q', '-a', '--all', '--type', '--name',
             '--network', '-p', '-v', '-e', '--label', '--entrypoint', '--rm'}
    return {'kind': 'rejected', 'reason': code if code in {'unsafe_create', 'unexpected_container_command', 'unsafe_lifecycle'}
            else 'fixture_refused', 'command': [arg if arg in verbs else 'other' for arg in args[:2]],
            'flags': sorted({arg for arg in args if arg in flags})}


def fixture_main(runtime, args, directory, stop_parent=False, *, environment=None, profile_control='positive'):
    """Private docker/podman executable: no dispatch, subprocess or daemon code exists."""
    lifecycle_control = profile_control.removeprefix('fresh-')
    parent_fd = None
    try:
        fixture = decode_fixture(directory / 'fixture.json')
        if stop_parent:
            parent_fd = parent_identity(fixture)
        with event_file(directory) as (root, stream):
            check_root(directory, root)
            raw = stream.read(LIMIT + 1)
            if len(raw) > LIMIT:
                fail('fixture_too_large')
            events = dev.decode(raw)
            if type(events) is not list or len(events) > 64:
                fail('fixture_invalid')
            control_event = None
            try:
                if tuple(args[:1]) == ('create',) and profile_control.startswith('invalid-create-'):
                    # A negative control proves rejection only after the unchanged
                    # pinned request has independently passed the same validator.
                    try:
                        create_facts(args, fixture, environment=environment)
                    except dev.Refusal:
                        fail('invalid_control_baseline')
                    args, environment = list(args), dict(environment)
                    if profile_control == 'invalid-create-script':
                        args[-1] += 'ENV_SYNTHETIC_CANARY'
                    elif profile_control == 'invalid-create-environment':
                        environment['JWT_SECRET'] = 'ENV_SYNTHETIC_CANARY'
                    elif profile_control == 'invalid-create-routing':
                        environment['DOCKER_CONTEXT'] = 'ENV_SYNTHETIC_CANARY'
                archive = None
                original_execution_args = list(args)
                if fixture.get('execute') and args[:1] in (['cp'], ['start']):
                    if args[:1] == ['cp'] and len(args) == 3 and re.fullmatch('[0-9a-f]{64}:/', args[-1]):
                        args = ['cp', '-', lifecycle.CONTAINER_ID + ':/'] if args[1] == '-' else args
                    elif args[:1] == ['start'] and len(args) == 2 and re.fullmatch('[0-9a-f]{64}', args[-1]):
                        args = ['start', lifecycle.CONTAINER_ID]
                    else:
                        fail('unsafe_lifecycle')
                if fixture.get('lifecycle') and args[:1] == ['cp']:
                    # Validate operands/order before consuming any stdin.
                    try:
                        lifecycle_prefix(fixture, events, 'cp')
                        if runtime != 'docker' or args != ['cp', '-', lifecycle.CONTAINER_ID + ':/']:
                            fail('unsafe_lifecycle')
                        archive = lifecycle.read_archive(sys.stdin.fileno())
                        lifecycle.validate_archive(archive)
                    except dev.Refusal:
                        if lifecycle_control.startswith('invalid-lifecycle-'):
                            fail('invalid_control_baseline')
                        raise
                    if lifecycle_control.startswith('invalid-lifecycle-'):
                        # Original transfer independently passed before injection.
                        args = list(args)
                        if lifecycle_control == 'invalid-lifecycle-target':
                            args[-1] = 'f' * 64 + ':/'
                        elif lifecycle_control == 'invalid-lifecycle-archive':
                            archive = b'ENV_SYNTHETIC_CANARY'
                        elif lifecycle_control == 'invalid-lifecycle-order':
                            args = ['start', lifecycle.CONTAINER_ID]
                        control_event = lifecycle_control_event(profile_control)
                code, output, error = fixture_command(runtime, args, fixture, events, environment=environment, archive=archive,
                                                     corrupt_request=profile_control == 'invalid-create-request')
                if fixture.get('execute') and args[:1] in (['create'], ['cp'], ['start']):
                    phase = {'create': 'container_create', 'cp': 'container_copy', 'start': 'container_start'}[args[0]]
                    actual_id = owner_handoff(fixture, phase, original_execution_args, environment, archive=archive)
                    if phase == 'container_create':
                        output = actual_id + '\n'
                    elif phase == 'container_start':
                        if fixture.get('auth_boundary'):
                            events[-1] = {'kind': 'postgres_start_acknowledged'}
                            code, output, error = 0, '', ''
                        else:
                            code, output, error = 125, '', 'ENV first executed start boundary'

            except dev.Refusal as refusal:
                if control_event is not None:
                    events.append(control_event)
                events.append(rejected_event(args, refusal.code))
                code, output, error = 125, '', 'ENV synthetic command refused'
            check_root(directory, root)
            check_event_file(root, stream.fileno())
            encoded = images.canonical(events).encode()
            if len(encoded) > LIMIT:
                fail('fixture_too_large')
            stream.seek(0)
            stream.write(encoded)
            stream.truncate()
            stream.flush()
            os.fsync(stream.fileno())
            check_event_file(root, stream.fileno())
        if parent_fd is not None and (events[-1]['kind'] in {'rejected', 'postgres_start_refused'}
                or not fixture.get('lifecycle') and args[:1] == ['create'] and events[-1]['kind'] == 'postgres_create'):
            signal.pidfd_send_signal(parent_fd, signal.SIGKILL)
        sys.stdout.write(output)
        sys.stderr.write(error)
        return code
    except (OSError, ValueError, KeyError, TypeError, dev.Refusal):
        if parent_fd is not None:
            try:
                signal.pidfd_send_signal(parent_fd, signal.SIGKILL)
            except OSError:
                pass
        return 125
    finally:
        if parent_fd is not None:
            os.close(parent_fd)


def validate_image_observations(observations, selection_plan, config_plan=None):
    if (type(observations) is not dict or set(observations) != set(selection_plan.values())
            or any(type(value) is not dict or set(value) != {'Id', 'Os', 'Architecture'}
                   or type(value['Id']) is not str or not re.fullmatch(r'sha256:[0-9a-f]{64}', value['Id'])
                   or value['Os'] != 'linux' or value['Architecture'] != 'amd64'
                   for value in observations.values())
            or config_plan is not None and any(observations[key]['Id'] != value for key, value in config_plan.items())):
        fail('invalid_image_observations')


def owner_handoff(fixture, phase, args, environment, *, archive=None):
    """Closed fixture-only request. No daemon address, route or payload selector."""
    token = (environment or {}).get('ENV_PRIVATE_OWNER_TOKEN')
    owner_pid = (environment or {}).get('ENV_PRIVATE_OWNER_PID')
    if (type(token) is not str or not re.fullmatch('[0-9a-f]{32}', token)
            or type(owner_pid) is not str or not re.fullmatch('[1-9][0-9]{0,9}', owner_pid)):
        fail('invalid_owner_handoff')
    data = {'token': token, 'phase': phase, 'args': args}
    if phase.startswith('container_') or phase in ('poststart_health', 'poststart_image', 'auth_job'):
        if any(key in environment for key in create_profile.ROUTING_KEYS if key not in ('DOCKER_HOST', 'DOCKER_CONFIG')):
            fail('unsafe_create')
        public_inputs = (tuple(create_profile.CONTAINER_ENV) if phase == 'container_create' else
                         tuple(create_profile.auth_environment(fixture)) if phase == 'auth_job' else ())
        data['environment'] = {key: environment[key] for key in (*public_inputs, 'DOCKER_HOST', 'DOCKER_CONFIG') if key in environment}
        if archive is not None:
            data['archive'] = base64.b64encode(archive).decode()
    request = images.canonical(data).encode()
    if len(request) > 32768:
        fail('invalid_owner_handoff')
    with socket.socket(socket.AF_UNIX) as peer:
        peer.settimeout(FIXTURE_SECONDS)
        peer.connect(str(Path(fixture['workdir']) / 'docker/owner.sock'))
        pid, uid, _ = struct.unpack('3i', peer.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
        if pid != int(owner_pid) or uid != os.getuid():
            fail('invalid_owner_handoff')
        peer.sendall(request)
        peer.shutdown(socket.SHUT_WR)
        response = b''
        response_limit = 512 if phase == 'poststart_health' else 65
        while len(response) <= response_limit:
            chunk = peer.recv(response_limit + 1 - len(response))
            if not chunk:
                break
            response += chunk
        if len(response) > response_limit:
            fail('invalid_owner_handoff')
        if phase == 'container_create':
            if not re.fullmatch(rb'[0-9a-f]{64}\n', response):
                fail('invalid_owner_handoff')
            return response.decode().strip()
        if phase == 'poststart_health':
            try:
                state = dev.decode(response)
            except ValueError:
                fail('invalid_owner_handoff')
            if (type(state) is not dict or set(state) != {'Status', 'Running', 'Health'}
                    or state['Status'] != 'running' or state['Running'] is not True
                    or type(state['Health']) is not dict or set(state['Health']) != {'Status'}
                    or state['Health']['Status'] not in ('starting', 'unhealthy', 'healthy')):
                fail('invalid_owner_handoff')
            return state
        if response != b'OK\n':
            fail('invalid_owner_handoff')


def check_fixture_custody(work, work_fd, sources, fixture_hash, wrappers, target, run_id, *, listener_identity=None):
    """Check the concrete closed fixture, including before each owner exchange."""
    check_root(work, work_fd)
    check_workdir(work, target, run_id, after=True, fixture=True)
    if (source_snapshot() != sources or dev.digest(dev.read(work / 'fixture.json')) != fixture_hash
            or any(dev.digest(dev.read(work / 'bin' / name)) != value for name, value in wrappers.items())):
        fail('fixture_changed')
    if listener_identity is not None:
        try:
            current = (work / 'docker/owner.sock').lstat()
        except OSError:
            fail('invalid_owner_handoff')
        if (not stat.S_ISSOCK(current.st_mode) or current.st_uid != os.getuid()
                or stat.S_IMODE(current.st_mode) != 0o600 or current.st_nlink != 1
                or (current.st_dev, current.st_ino) != (listener_identity.st_dev, listener_identity.st_ino)):
            fail('invalid_owner_handoff')


def validate_owner_request(raw, token, fixture, events, phase):
    """Validate the exact original CLI baseline before any private owner action."""
    try:
        request = dev.decode(raw)
    except (ValueError, dev.Refusal):
        fail('invalid_owner_handoff')
    project = fixture['project']
    initialized = fixture.get('initialized', False)
    if initialized:
        phase = {10: 0, 11: 1}.get(phase, -1)
    args = (['volume', 'inspect', 'supabase_db_' + project] if phase == 0 else
            ['volume', 'create', '--label', 'com.supabase.cli.project=' + project, '--label',
             'com.docker.compose.project=' + project, 'supabase_db_' + project])
    if (phase not in [0, 1] or type(request) is not dict or request != {
            'token': token, 'phase': ('initialized_probe' if phase == 0 else 'initialized_ensure') if initialized else ('probe' if phase == 0 else 'create'), 'args': args}):
        fail('invalid_owner_handoff')
    validate_fixture_volume(fixture)
    facts = selected_facts(dict(fixture, postgres_image=fixture['selection_plan'][fixture['postgres_image']]))
    facts.update(original_image=fixture['postgres_image'], immutable_selection_proven=True, create_request_proven=True)
    suffix = ([{'kind': 'volume_inspect' if initialized else 'volume_missing'}, {'kind': 'network_inspect'}] if phase == 0 else [])
    validate_observations(events + suffix + [{'kind': 'initialized_volume_ensure_acknowledged' if initialized else 'fresh_volume_create_acknowledged'},
                                           {'kind': 'postgres_create', 'facts': facts}], facts,
                          [fixture['image_observations'][fixture['selection_plan'][tag]] for tag in fixture['images']], fresh=not initialized, initialized=initialized)


def poststart_prefix(fixture, events):
    if not fixture.get('auth_boundary') or len(events) < CREATE_BOUNDARY + 2:
        fail('unsafe_lifecycle')
    lifecycle_prefix(fixture, events, 'poststart')
    if events[CREATE_BOUNDARY:CREATE_BOUNDARY + 2] != [lifecycle.transfer_event(), {'kind': 'postgres_start_acknowledged'}]:
        fail('unsafe_lifecycle')
    tail = events[CREATE_BOUNDARY + 2:]
    image_seen = False
    healthy = False
    for event in tail:
        if event == {'kind': 'auth_image_inspect'} and healthy and not image_seen:
            image_seen = True
        elif (not image_seen and type(event) is dict and set(event) == {'kind', 'health'}
              and event['kind'] == 'postgres_health' and event['health'] in ('starting', 'unhealthy', 'healthy')):
            healthy = event['health'] == 'healthy'
        else:
            fail('unsafe_lifecycle')
    return healthy, image_seen


def validate_poststart_handoff(raw, token, fixture, events):
    try:
        request = dev.decode(raw)
    except ValueError:
        fail('invalid_owner_handoff')
    if (type(request) is not dict or set(request) != {'token', 'phase', 'args', 'environment'}
            or request.get('token') != token or type(request.get('args')) is not list
            or type(request.get('environment')) is not dict):
        fail('invalid_owner_handoff')
    healthy, image_seen = poststart_prefix(fixture, events)
    phase = request['phase']
    auth = next(tag for tag in fixture['images'] if '/gotrue:' in tag)
    routing = create_profile.environment(fixture)
    wanted = {key: routing[key] for key in ('DOCKER_HOST', 'DOCKER_CONFIG')}
    if phase == 'auth_job':
        if not healthy or not image_seen:
            fail('invalid_owner_handoff')
        wanted.update(create_profile.auth_environment(fixture))
        create_profile.validate_auth_job(request['args'], fixture, request['environment'])
    elif phase == 'poststart_health':
        if image_seen or request['args'] != ['container', 'inspect', 'supabase_db_' + fixture['project'], '--format', '{{json .State}}']:
            fail('invalid_owner_handoff')
    elif phase == 'poststart_image':
        if not healthy or image_seen or request['args'] != ['image', 'inspect', auth]:
            fail('invalid_owner_handoff')
    else:
        fail('invalid_owner_handoff')
    if not create_profile._exact_tree(request['environment'], wanted):
        fail('invalid_owner_handoff')
    return request


def validate_execution_handoff(raw, token, fixture, events, phase):
    """Only original validated operands/public inputs can reach retained execution."""
    request = dev.decode(raw)
    if fixture.get('initialized') and phase == 9:
        phase = 2
    expected_phase = {2: 'container_create', 3: 'container_copy', 4: 'container_start'}.get(phase)
    keys = {'token', 'phase', 'args', 'environment'} | ({'archive'} if phase == 3 else set())
    expected_environment = create_profile.environment(fixture)
    if phase in (3, 4):
        expected_environment = {key: expected_environment[key] for key in ('DOCKER_HOST', 'DOCKER_CONFIG')}
    if (not fixture.get('execute') or type(request) is not dict or set(request) != keys
            or request.get('token') != token or expected_phase is None or request.get('phase') != expected_phase
            or type(request.get('args')) is not list or type(request.get('environment')) is not dict
            or request['environment'] != expected_environment):
        fail('invalid_owner_handoff')
    args = request['args']
    if phase == 2:
        create_profile.validate(args, fixture, request['environment'])
        lifecycle_prefix(fixture, events, 'create')
    elif phase == 3:
        lifecycle_prefix(fixture, events, 'cp')
        try:
            lifecycle.validate_archive(base64.b64decode(request['archive'], validate=True))
        except (ValueError, TypeError):
            fail('unsafe_lifecycle')
    else:
        lifecycle_prefix(fixture, events, 'start')
    return request


def guarded_fixture_command(command, work, env, guard):
    """Service the private handoff on the owner thread while bounding the CLI group.

    The capability lives only in process memory/environment and socket bytes; it
    is never persisted or hashed. The listener address is generated from private
    work custody, never accepted as a caller-selected daemon endpoint.
    """
    token = uuid.uuid4().hex
    env = dict(env, ENV_PRIVATE_OWNER_TOKEN=token, ENV_PRIVATE_OWNER_PID=str(os.getpid()))
    path = work / 'docker/owner.sock'
    with socket.socket(socket.AF_UNIX) as listener:
        listener.bind(str(path))
        path.chmod(0o600)
        identity = path.lstat()
        listener.listen(1)
        if guard._second_fixture is not None:
            guard.bind_second_listener(identity)
        else:
            guard.bind_listener(identity)
        def check():
            guard.check()
        check()
        process = subprocess.Popen([str(arg) for arg in command], cwd=work, env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        total = 0
        group_terminated = False
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(listener, selectors.EVENT_READ)
                for stream in [process.stdout, process.stderr]:
                    os.set_blocking(stream.fileno(), False)
                    selector.register(stream, selectors.EVENT_READ)
                while len(selector.get_map()) > 1:
                    check()
                    for key, _ in selector.select(guard.remaining()):
                        check()
                        if key.fileobj is listener:
                            peer, _ = listener.accept()
                            with peer:
                                peer.settimeout(guard.remaining())
                                pid, uid, _ = struct.unpack('3i', peer.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
                                # Only the exact CLI's direct fixture child may ask.
                                try:
                                    status = Path('/proc/' + str(pid) + '/status').read_text()
                                except OSError:
                                    fail('invalid_owner_handoff')
                                parent = next((line.split()[1] for line in status.splitlines() if line.startswith('PPid:')), '')
                                if uid != os.getuid() or parent != str(process.pid):
                                    fail('invalid_owner_handoff')
                                raw = b''
                                while len(raw) <= 32768:
                                    check()
                                    peer.settimeout(guard.remaining())
                                    chunk = peer.recv(32769 - len(raw))
                                    if not chunk:
                                        break
                                    raw += chunk
                                if len(raw) > 32768:
                                    fail('invalid_owner_handoff')
                                check()
                                fixture = decode_fixture(work / 'fixture.json')
                                events = decode_fixture(work / 'events.json')
                                response = b'OK\n'
                                if guard.auth_boundary and guard.phase == 5:
                                    request = validate_poststart_handoff(raw, token, fixture, events)
                                    if request['phase'] == 'poststart_health':
                                        response = images.canonical(guard.poststart_health()).encode()
                                    elif request['phase'] == 'poststart_image':
                                        guard.joint()
                                    else:
                                        if guard.auth_migration:
                                            guard.admit_auth_job(request['args'], request['environment'], fixture)
                                        else:
                                            guard.refuse_auth_job(request['args'], request['environment'], fixture)
                                elif guard.execution and guard.phase in (2, 3, 4, 9):
                                    request = validate_execution_handoff(raw, token, fixture, events, guard.phase)
                                    if guard.phase in (2, 9):
                                        actual_id = guard.container_create(request['args'], fixture, request['environment'], _replacement=guard.phase == 9)
                                        response = (actual_id + '\n').encode()
                                    elif guard.phase == 3:
                                        guard.container_copy(request['args'], base64.b64decode(request['archive'], validate=True))
                                    else:
                                        guard.container_start(request['args'])
                                else:
                                    validate_owner_request(raw, token, fixture, events, guard.phase)
                                    if guard.phase == 0:
                                        guard.probe()
                                    elif guard.phase == 1:
                                        guard.create()
                                    elif guard.phase == 10:
                                        guard.initialized_probe()
                                    else:
                                        guard.initialized_ensure()
                                check()
                                peer.settimeout(guard.remaining())
                                if guard.execution and guard.phase == 5 and (not guard.auth_boundary or guard.auth_job_refused or guard.auth_job_input is not None):
                                    os.killpg(process.pid, signal.SIGKILL)
                                    process.wait(timeout=min(2, guard.remaining()))
                                    group_terminated = True
                                    guard.auth_cli_terminated = True
                                    if guard.auth_migration:
                                        guard.execute_auth_job()
                                    if guard.initialized_cli and guard.old_container_id is None:
                                        guard.prepare_initialized_cli()
                                        initialized_cli_command(guard, guard._secondary_retained)
                                    else:
                                        guard.finish_execution()
                                    dev.refuse('images_cli', 'command_refused')
                                peer.sendall(response)
                        else:
                            chunk = os.read(key.fd, min(65536, 1024 * 1024 - total + 1))
                            if not chunk:
                                selector.unregister(key.fileobj)
                            total += len(chunk)
                            if total > 1024 * 1024:
                                fail('command_output_too_large')
                process.wait(timeout=guard.remaining())
                check()
                if process.returncode == 0:
                    fail('cli_unexpected_success')
                dev.refuse('images_cli', 'command_refused')
        except (TimeoutError, subprocess.TimeoutExpired):
            dev.refuse('docker', 'docker_timeout')
        finally:
            if not group_terminated:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            process.stdout.close()
            process.stderr.close()
            process.wait(timeout=2)
            if guard.execution and guard.container_id is not None and not guard.cleanup_attempted:
                guard.cleanup_execution()
            # Retain the closed private socket's path custody through the final
            # owner observations; the private workdir context removes it on exit.


def initialized_cli_command(guard, retained):
    """Closed second CLI launch; both private fixtures survive final disposal."""
    if not guard.initialized_cli or guard.phase != 10 or guard._second_fixture is not None:
        fail('invalid_owner_handoff')
    temporary = retained.enter_context(tempfile.TemporaryDirectory(prefix='env-initialized-startup-'))
    work = Path(temporary)
    work_fd = retained.enter_context(work_anchor(work))
    initialize_workdir(work, guard.target, guard.run_id)
    executable = guard.command[0][0]
    command, env = invocation(executable, work, guard.target, guard.run_id, guard.network)
    install_fixture(work, guard.target, guard.run_id, guard.network, executable,
                    selection_plan=guard._create_operands[1]['selection_plan'], volume=guard.volume, image_observations=guard.images,
                    profile_control='initialized-pinned-cli-postgres', guarded_owner=True)
    fixture_hash = dev.digest(dev.read(work / 'fixture.json'))
    wrappers = {name: dev.digest(dev.read(work / 'bin' / name)) for name in ['docker', 'podman']}
    guard.bind_second_fixture(work, work_fd, source_snapshot(), fixture_hash, wrappers)
    env['PATH'] = str(work / 'bin')
    env['DOCKER_HOST'] = 'unix://' + str(work / 'no-daemon.sock')
    guarded_fixture_command(command, work, env, guard)


def install_fixture(work, target, run_id, network, executable=None, guard_parent=True, *, selection_plan, volume=None, image_observations=None, profile_control='positive', guarded_owner=False):
    fresh = profile_control.startswith('fresh-')
    initialized = profile_control == 'initialized-pinned-cli-postgres'
    if fresh and volume is not None:
        fail('fresh_volume_required')
    volume = volume_descriptor(fixture_volume(target, run_id) if volume is None else volume, target, run_id)
    validate_selection_plan(selection_plan)
    validate_image_observations(image_observations, selection_plan)
    pins = images.load_pins(dev.read(dev.ROOT / images.PINS))
    references = ['public.ecr.aws/' + item['repository'] + ':' + item['tag'] for item in pins['images']]
    fixture = {'project': dev.project_identity(target, run_id), 'workdir': str(work),
               'target_id': target['target_id'], 'run_id': run_id,
               **({'planned_volume': volume, 'fresh': True, 'fresh_existing': profile_control == 'fresh-existing',
                   'fresh_racing': profile_control == 'fresh-racing'} if fresh else {'volume': volume}),
               'executable': str(executable) if executable is not None else '',
               'database_port': target['ports']['database'], 'network': network,
               'origins': target['origins'],
               'auth_boundary': profile_control in ('fresh-pinned-cli-postgres-auth-boundary', 'fresh-pinned-cli-postgres-auth-migration'),
               'images': references, 'postgres_image': references[0], 'selection_plan': selection_plan,
               'image_observations': image_observations,
               'initialized': initialized,
               'execute': profile_control in ('fresh-pinned-cli-postgres', 'fresh-pinned-cli-postgres-persistence', 'fresh-pinned-cli-postgres-initialized', 'fresh-pinned-cli-postgres-auth-boundary', 'fresh-pinned-cli-postgres-auth-migration', 'initialized-pinned-cli-postgres'),
               'lifecycle': fresh or initialized or profile_control == 'lifecycle-positive' or profile_control.startswith('invalid-lifecycle-')}
    if guarded_owner:
        if not fresh and not initialized:
            fail('fresh_volume_required')
        fixture['guarded_owner'] = True
    write_private(work / 'fixture.json', images.canonical(fixture).encode())
    write_private(work / 'events.json', b'[]')
    for runtime in ['docker', 'podman']:
        wrapper = (f'#!{sys.executable}\nimport os, signal, ctypes\n'
                   f'parent = os.getppid()\n'
                   f'if ctypes.CDLL(None, use_errno=True).prctl(1, signal.SIGKILL, 0, 0, 0) != 0: os._exit(125)\n'
                   f'if os.getppid() != parent: os._exit(125)\n'
                   f'signal.alarm({FIXTURE_SECONDS})\nimport sys\nfrom pathlib import Path\n'
                   f'sys.path.insert(0, {str(Path(__file__).resolve().parent)!r})\nimport startup\n'
                   f'args, env = sys.argv[1:], dict(os.environ)\n'
                   f'sys.exit(startup.fixture_main({runtime!r}, args, Path({str(work)!r}), stop_parent={guard_parent!r}, environment=env, profile_control={profile_control!r}))\n')
        write_private(work / 'bin' / runtime, wrapper.encode())
        (work / 'bin' / runtime).chmod(0o700)


def synthetic_probe(executable, target, run_id, network=None, control='positive', *, selection_plan, volume=None, image_observations=None, _guarded_target=None):
    if control not in ['positive', 'invalid-network', 'contaminated-workdir', 'reject-command', 'invalid-selection-plan',
                       'invalid-create-script', 'invalid-create-environment', 'invalid-create-routing', 'invalid-create-request',
                       'lifecycle-positive', 'invalid-lifecycle-target', 'invalid-lifecycle-archive', 'invalid-lifecycle-order',
                       'fresh-pinned-cli-postgres', 'fresh-pinned-cli-postgres-persistence', 'fresh-pinned-cli-postgres-initialized', 'fresh-pinned-cli-postgres-auth-boundary', 'fresh-pinned-cli-postgres-auth-migration', 'fresh-lifecycle-positive', 'fresh-existing', 'fresh-racing', 'fresh-invalid-lifecycle-target',
                       'fresh-invalid-lifecycle-archive', 'fresh-invalid-lifecycle-order']:
        fail('unknown_control')
    if control == 'invalid-selection-plan':
        selection_plan = dict(selection_plan)
        selection_plan.pop(next(iter(selection_plan)))
    validate_selection_plan(selection_plan)
    validate_image_observations(image_observations, selection_plan)
    network = fixture_network(target, run_id) if network is None else network
    before_sources = source_snapshot()
    with tempfile.TemporaryDirectory(prefix='env-startup-') as temporary, work_anchor(Path(temporary)) as work_fd, ExitStack() as second_retained, ExitStack() as retained:
        work = Path(temporary)
        initialize_workdir(work, target, run_id)
        if control == 'invalid-network':
            network['Options'] = {}
        if control == 'contaminated-workdir':
            write_private(work / '.env', b'ENV_SYNTHETIC_UNTRUSTED=1')
        guard = None
        if _guarded_target is not None:
            import resources
            if not control.startswith('fresh-') or volume is not None:
                fail('fresh_volume_required')
            executable_guard = retained.enter_context(executable_custody(executable))
            guard = retained.enter_context(resources.fresh_session(
                _guarded_target[0], run_id, executable, work, _socket_path=_guarded_target[1],
                _executable_custody=executable_guard))
            if guard.target != target or guard.images != image_observations:
                fail('invalid_owner_handoff')
            network = guard.network
            command, env = guard.command
            if control in ('fresh-pinned-cli-postgres', 'fresh-pinned-cli-postgres-persistence', 'fresh-pinned-cli-postgres-initialized', 'fresh-pinned-cli-postgres-auth-boundary', 'fresh-pinned-cli-postgres-auth-migration'):
                guard.enable_execution()
                if control.endswith('-auth-migration'):
                    guard.enable_auth_migration()
                elif control.endswith('-auth-boundary'):
                    guard.enable_auth_boundary()
                if control.endswith(('-persistence', '-initialized')):
                    guard.enable_persistence()
                if control.endswith('-initialized'):
                    guard.enable_initialized_cli()
                    guard._secondary_retained = second_retained
        else:
            command, env = invocation(executable, work, target, run_id, network)
        install_fixture(work, target, run_id, network, executable, guard_parent=control != 'reject-command', selection_plan=selection_plan, volume=volume, image_observations=image_observations, profile_control=control, guarded_owner=guard is not None)
        fixture_hash = dev.digest(dev.read(work / 'fixture.json'))
        wrappers = {name: dev.digest(dev.read(work / 'bin' / name)) for name in ['docker', 'podman']}
        env['PATH'] = str(work / 'bin')
        env['DOCKER_HOST'] = 'unix://' + str(work / 'no-daemon.sock')
        check_workdir(work, target, run_id, fixture=True)
        if control == 'reject-command':
            # An unrecognized command proves that the executable boundary refuses.
            command = [work / 'bin/docker', 'run', 'forbidden']
        if guard is not None:
            guard.bind_fixture(work, work_fd, before_sources, fixture_hash, wrappers)
        try:
            if guard is None:
                images.bounded_command(command, work, env, 30, 1024 * 1024)
            else:
                guarded_fixture_command(command, work, env, guard)
        except dev.Refusal as refused:
            if refused.code != 'command_refused':
                raise
        else:
            fail('cli_unexpected_success')
        check_root(work, work_fd)
        if source_snapshot() != before_sources:
            fail('proof_source_changed')
        if (dev.digest(dev.read(work / 'fixture.json')) != fixture_hash
                or any(dev.digest(dev.read(work / 'bin' / name)) != value for name, value in wrappers.items())):
            fail('fixture_changed')
        events = decode_fixture(work / 'events.json')
        if type(events) is not list or len(events) > 64 or any(type(event) is not dict for event in events):
            fail('fixture_invalid')
        check_workdir(work, target, run_id, after=True, fixture=True)
        fixture = decode_fixture(work / 'fixture.json')
        if fixture['selection_plan'] != selection_plan or fixture['image_observations'] != image_observations:
            fail('invalid_selection_plan')
        if guard is not None and guard.execution:
            if guard.phase != 7 or not guard.cleaned or (guard.persistence and not guard.persistence_verified):
                fail('execution_cleanup_unresolved')
            if guard.auth_boundary:
                poststart_prefix(fixture, events)
                if not (guard.auth_job_refused or (guard.auth_migration and guard.auth_job_exit_verified and guard.auth_job_disposed)) or not guard.poststart_healthy:
                    fail('boundary_not_proven')
                return {'ok': True, 'stage': 'pinned_cli_postgres_auth_migration' if guard.auth_migration else 'pinned_cli_postgres_auth_boundary', 'code': 'qualified',
                        'runtime_ready': False, 'container_executed': True, 'healthy_verified': True,
                        'cli_health_observed': True, 'auth_job_profile_validated': True, 'auth_job_refused': guard.auth_job_refused,
                        'auth_job_dispatched': guard.auth_job_dispatched,
                        **({'auth_job_exit_verified': True, 'auth_job_disposal_verified': True, 'cli_terminated_before_dispatch': True, 'pg_shutdown_verified': True} if guard.auth_migration else {}), 'fresh_setup_completed': False,
                        'shutdown_verified': True, 'forced_shutdown': False, 'cleanup_verified': True,
                        'source_sha256': before_sources}
            return {'ok': True, 'stage': 'pinned_cli_postgres_initialized' if guard.initialized_cli else ('pinned_cli_postgres_persistence' if guard.persistence else 'pinned_cli_postgres'), 'code': 'qualified',
                    'runtime_ready': False, 'container_executed': True, 'healthy_verified': True,
                    'shutdown_verified': True, 'forced_shutdown': False, 'cleanup_verified': True,
                    'named_volume_verified': True,
                    **({'cli_start_count': 2, 'cli_start_boundaries': ['fresh', 'initialized'], 'initialized_cli_recreation_verified': True}
                       if guard.initialized_cli else ({'cli_first_start_only': True, 'owner_start_count': 2}
                       if guard.persistence else {'first_start_only': True})),
                    **({'owner_recreation_verified': True, 'distinct_container_verified': True,
                        'persisted_run_marker_verified': True, 'same_cluster_verified': True,
                        'initialization_markers_verified': True, 'both_shutdowns_verified': True}
                       if guard.persistence and guard.persistence_verified else {}),
                    'source_sha256': before_sources}
        if guard is not None:
            if guard.phase != 2 or guard.volume is None:
                fail('invalid_owner_handoff')
        expected_facts = selected_facts(dict(fixture, postgres_image=selection_plan[fixture['postgres_image']]))
        expected_facts.update(original_image=fixture['postgres_image'], immutable_selection_proven=True, create_request_proven=True)
        if control == 'reject-command':
            if events != [rejected_event(['run', 'forbidden'], 'unexpected_container_command')]:
                fail('boundary_not_proven')
            fail('expected_command_rejected')
        if control.startswith('invalid-create-'):
            # Match every prerequisite and one exact redacted rejection. No positive
            # create can survive the replacement used only for sequence checking.
            rejection = {'kind': 'rejected', 'reason': 'unsafe_create', 'command': ['create', 'other'],
                         'flags': ['--entrypoint', '--label', '--name', '--network', '-e', '-p', '-v']}
            if not events or events[-1] != rejection:
                fail('boundary_not_proven')
            validate_observations(events[:-1] + [{'kind': 'postgres_create', 'facts': expected_facts}],
                                  expected_facts, list(image_observations[selection_plan[tag]] for tag in fixture['images']), fresh=fixture.get('fresh', False), initialized=fixture.get('initialized', False))
            fail('expected_create_profile_rejected')
        if control in ['fresh-existing', 'fresh-racing']:
            command = ['volume', 'inspect', 'supabase_db_' + fixture['project']] if control == 'fresh-existing' else [
                'volume', 'create', '--label', 'com.supabase.cli.project=' + fixture['project'], '--label',
                'com.docker.compose.project=' + fixture['project'], 'supabase_db_' + fixture['project']]
            rejection = rejected_event(command, 'fresh_volume_required')
            boundary = 5 if control == 'fresh-existing' else 7
            if len(events) != boundary + 1 or events[-1] != rejection:
                fail('boundary_not_proven')
            # Independently check all original prerequisites before expected refusal.
            validate_observations(events[:boundary] + ([{'kind': 'volume_missing'}, {'kind': 'network_inspect'}] if boundary == 5 else []) + [
                                  {'kind': 'fresh_volume_create_acknowledged'}, {'kind': 'postgres_create', 'facts': expected_facts}],
                                  expected_facts, list(image_observations[selection_plan[tag]] for tag in fixture['images']), fresh=True)
            fail('expected_fresh_volume_rejected')
        if fixture.get('lifecycle'):
            if control.removeprefix('fresh-').startswith('invalid-lifecycle-'):
                command = ['start', 'other'] if control.removeprefix('fresh-') == 'invalid-lifecycle-order' else ['cp', 'other']
                expected_rejection = {'kind': 'rejected', 'reason': 'unsafe_lifecycle', 'command': command, 'flags': []}
                if (len(events) != CREATE_BOUNDARY + 2
                        or events[CREATE_BOUNDARY:] != [lifecycle_control_event(control), expected_rejection]):
                    fail('boundary_not_proven')
                validate_observations(events[:CREATE_BOUNDARY], expected_facts,
                                      list(image_observations[selection_plan[tag]] for tag in fixture['images']), fresh=fixture.get('fresh', False), initialized=fixture.get('initialized', False))
                fail('expected_lifecycle_rejected')
            if len(events) != CREATE_BOUNDARY + 2 or events[CREATE_BOUNDARY:] != [lifecycle.transfer_event(), {'kind': 'postgres_start_refused'}]:
                fail('boundary_not_proven')
            validate_observations(events[:CREATE_BOUNDARY], expected_facts,
                                  list(image_observations[selection_plan[tag]] for tag in fixture['images']), fresh=fixture.get('fresh', False), initialized=fixture.get('initialized', False))
        else:
            validate_observations(events, expected_facts, list(image_observations[selection_plan[tag]] for tag in fixture['images']), fresh=fixture.get('fresh', False), initialized=fixture.get('initialized', False))
        return {'ok': True, 'stage': 'startup_invocation', 'code': 'synthetic_boundary_proven',
                'runtime_ready': False, 'synthetic_network': True, 'container_executed': False,
                'synthetic_create_acknowledged': fixture.get('lifecycle', False),
                'secret_transfer_validated': fixture.get('lifecycle', False),
                'first_start_refused': fixture.get('lifecycle', False),
                'fresh_branch_proven': fixture.get('fresh', False),
                **({'guarded_volume_owner_proven': True,
                    'observed_volume': {key: guard.volume[key] for key in ['Name', 'Driver', 'Scope', 'Labels', 'Options']}}
                   if guard is not None else {}),
                'facts': expected_facts, 'event_count': len(events), 'image_observations': image_observations,
                'configuration': {'exact_generated_bytes_verified': True,
                                  'supabase_files_config_and_optional_cli_latest_only': True},
                'source_sha256': before_sources,
                'limits': {'first_postgres_create_only': not fixture.get('lifecycle', False),
                           'first_postgres_start_only': fixture.get('lifecycle', False), 'digest_enforcement': False,
                           'immutable_selection': True,
                           'runtime_isolation': False, 'startup_helpers': False, 'shell_command_sql_qualified': False}}


def validate_observations(events, facts, descriptors=None, *, fresh=False, initialized=False):
    # Image preflight is concurrent: each of the four selected images appears once.
    if (type(events) is not list or len(events) != CREATE_BOUNDARY or any(type(event) is not dict for event in events)
            or any(type(event.get('image_index')) is not int for event in events[1:5])
            or events[0] != {'kind': 'container_inspect'}
            or sorted([event.get('image_index', -1) for event in events[1:5]]) != list(range(4))
            or any(event != dict({'kind': 'image_inspect', 'image_index': event.get('image_index')},
                                **({'descriptor': descriptors[event['image_index']]} if descriptors is not None else {}))
                   for event in events[1:5])
            or events[5:] != [{'kind': 'volume_missing' if fresh else 'volume_inspect'}, {'kind': 'network_inspect'},
                              {'kind': 'fresh_volume_create_acknowledged' if fresh else ('initialized_volume_ensure_acknowledged' if initialized else 'existing_volume_create_refused')}, {'kind': 'postgres_create', 'facts': facts}]):
        fail('boundary_not_proven')


def qualify(args):
    if str(uuid.UUID(args.run_id)) != args.run_id:
        fail('invalid_run_id')
    path = Path(args.target)
    if '..' in path.parts:
        fail('unsafe_path')
    path = Path(os.path.abspath(path))
    raw = dev.read(path)
    target = dev.decode(raw)
    dev.validate(target, dev.decode(dev.read(dev.ROOT / dev.SCHEMA)))
    if target['workspace_root'] != str(dev.ROOT):
        fail('workspace_mismatch')
    proof_sources = source_snapshot()
    sources = dev.source_evidence()
    dev.validate_prepared(target, raw, args.run_id, path, sources)
    evidence = existing_images(args)
    receipt_hash, selection_plan, _, config_plan = evidence
    observations = getattr(args, '_image_observations', None)
    if getattr(args, 'control', None) in ('pinned-cli-postgres', 'pinned-cli-postgres-persistence', 'pinned-cli-postgres-initialized', 'pinned-cli-postgres-auth-boundary', 'pinned-cli-postgres-auth-migration'):
        observations = {reference: {'Id': config, 'Os': 'linux', 'Architecture': 'amd64'} for reference, config in config_plan.items()}
        args._profile_control = 'fresh-' + args.control
        args._guarded_target = (args.target, '/var/run/docker.sock')
    validate_image_observations(observations, selection_plan, config_plan)
    payload = dev.ROOT / 'platform/deployment/.local/kdg-toolchains' / args.run_id / 'payload'
    with toolchain.anchored_directory(payload) as (fd, pinned):
        result = synthetic_probe(pinned / 'supabase/supabase', target, args.run_id,
                                 control=getattr(args, '_profile_control', getattr(args, 'control', 'positive')), selection_plan=selection_plan,
                                 volume=getattr(args, '_volume', None), image_observations=observations,
                                 _guarded_target=getattr(args, '_guarded_target', None))
        if not toolchain.anchor_current(payload, fd):
            fail('tool_payload_changed')
    # Repeat existing owner checks: no repair/registry fetch; evidence must remain unchanged.
    if existing_images(args) != evidence:
        fail('image_verification_refused')
    dev.validate_prepared(target, raw, args.run_id, path, sources)
    if source_snapshot() != proof_sources:
        fail('proof_source_changed')
    result['image_receipt_sha256'] = receipt_hash
    return result
