"""Acquire only the prepared disposable run bridge; never activate startup.

The public adapter uses /var/run/docker.sock only. Underscored injection points are
internal synthetic-proof plumbing, never command-line or environment configuration.
"""
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path
import re
import stat
import time
import uuid

import dev
import startup

SECONDS = 5
LOCK_SECONDS = .5
PREFIX = '/v1.48/networks/'


def fail(code):
    dev.refuse('network', code)


def validate_run_id(run_id):
    if type(run_id) is not str:
        fail('invalid_run_id')
    try:
        canonical = str(uuid.UUID(run_id))
    except ValueError:
        fail('invalid_run_id')
    if canonical != run_id:
        fail('invalid_run_id')


def safe_lock(info):
    return (stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid()
            and stat.S_IMODE(info.st_mode) == 0o600 and info.st_nlink == 1 and info.st_size == 0)


def canonical_id(value):
    if type(value) is not str or re.fullmatch(r'[0-9a-f]{64}', value) is None:
        fail('network_id_invalid')
    return value


def create_input(target, run_id):
    return {'Name': dev.project_identity(target, run_id) + '-network',
            'Driver': 'bridge', 'Scope': 'local', 'EnableIPv4': True,
            'EnableIPv6': False, 'Internal': False, 'Attachable': False,
            'Ingress': False, 'ConfigOnly': False,
            'Options': {startup.BINDING: '127.0.0.1'},
            'Labels': startup.labels(target, run_id)}


def descriptor(actual, target, run_id):
    """Validate Docker's actual safety fields before closing the startup projection.

    Docker adds Created/IPAM and may add future diagnostic fields; those fields
    never enter the startup descriptor. ConfigFrom must explicitly be empty.
    """
    if type(actual) is not dict:
        fail('network_not_run_owned')
    expected = dict(create_input(target, run_id), ConfigFrom={'Network': ''})
    for key, value in expected.items():
        if key not in actual or type(actual[key]) is not type(value) or actual[key] != value:
            fail('network_not_run_owned')
    if type(actual.get('Containers')) is not dict or actual['Containers']:
        fail('network_not_run_owned')
    network_id = canonical_id(actual.get('Id'))
    result = {key: actual[key] for key in startup.fixture_network(target, run_id)}
    startup.validate_network(result, target, run_id)
    if result['Id'] != network_id:
        fail('network_id_invalid')
    return result


@contextmanager
def run_lock(run_path, deadline):
    """Persistent flock inode in protected preparation parent; no unlink race."""
    with dev.directory(run_path.parent) as parent:
        dev.check_private(parent)
        name = '.network-' + run_path.name + '.lock'
        fd = os.open(name, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=parent)
        try:
            info = os.fstat(fd)
            if not safe_lock(info):
                fail('network_lock_unsafe')
            until = min(deadline, time.monotonic() + LOCK_SECONDS)
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= until:
                        fail('network_busy')
                    time.sleep(.01)
            def check():
                with dev.directory(run_path.parent) as current_parent:
                    held_parent = os.fstat(parent)
                    current = os.fstat(current_parent)
                    dev.check_private(parent)
                    dev.check_private(current_parent)
                    held = os.fstat(fd)
                    entry = os.stat(name, dir_fd=current_parent, follow_symlinks=False)
                    if ((held_parent.st_dev, held_parent.st_ino) != (current.st_dev, current.st_ino)
                            or (info.st_dev, info.st_ino) != (entry.st_dev, entry.st_ino)
                            or not safe_lock(held) or not safe_lock(entry)):
                        fail('network_lock_changed')
            check()
            yield check
            check()
        finally:
            os.close(fd)


def acquire(target_path, run_id, *, _socket_path='/var/run/docker.sock', _handoff=None):
    """Acquire/verify a bridge and revalidate immutable ID just before handoff.

    A lost POST response refuses without retry. A later invocation always starts
    with name inspection, so uncertainty never causes blind duplicate creation.
    """
    deadline = time.monotonic() + SECONDS
    validate_run_id(run_id)
    path = Path(target_path)
    if '..' in path.parts:
        fail('unsafe_path')
    path = Path(os.path.abspath(path))
    raw = dev.read(path)
    target = dev.decode(raw)
    dev.validate(target, dev.decode(dev.read(dev.ROOT / dev.SCHEMA)))
    if target['workspace_root'] != str(dev.ROOT):
        fail('workspace_mismatch')
    sources = dev.source_evidence()
    dev.validate_prepared(target, raw, run_id, path, sources)
    run_path = dev.ROOT / 'platform/deployment/.local/kdg' / run_id
    with dev.directory(run_path) as run, run_lock(run_path, deadline) as check_lock, \
            dev.DockerSession(_socket_path=_socket_path, deadline=deadline) as session:
        identity = os.fstat(run)
        def evidence():
            check_lock()
            dev.validate_prepared(target, raw, run_id, path, sources)
            with dev.directory(run_path) as current:
                now = os.fstat(current)
                if (identity.st_dev, identity.st_ino) != (now.st_dev, now.st_ino):
                    fail('prepared_run_changed')
            if time.monotonic() >= deadline:
                dev.refuse('docker', 'docker_timeout')
        def exchange(method, suffix, body=None):
            return session.exchange(method, PREFIX + suffix, body)
        def inspect(reference):
            status, value = exchange('GET', reference)
            if status == 404:
                return None
            if status != 200:
                fail('network_inspection_failed')
            return descriptor(value, target, run_id)
        evidence()
        dev.docker_prerequisite(_session=session)
        evidence()
        expected = create_input(target, run_id)
        network = inspect(expected['Name'])
        if network is None:
            evidence()
            status, response = exchange('POST', 'create', expected)
            if status == 409:
                network = inspect(expected['Name'])
                if network is None:
                    fail('network_create_conflict')
            elif status == 201:
                created_id = canonical_id(response.get('Id'))
                # Do not emit warnings: they are uncontrolled daemon content.
                if type(response.get('Warning')) is not str or response['Warning']:
                    fail('network_create_uncertain')
                network = inspect(created_id)
                if network is None or network['Id'] != created_id:
                    fail('network_replaced')
            else:
                fail('network_create_failed')
        network_id = network['Id']
        evidence()
        latest = inspect(network_id)
        if latest is None or latest['Id'] != network_id:
            fail('network_replaced')
        # A name lookup also detects replacement even if the old ID is retained.
        named = inspect(expected['Name'])
        if named is None or named['Id'] != network_id:
            fail('network_replaced')
        # Last daemon observation is by immutable ID, immediately before handoff.
        latest = inspect(network_id)
        if latest is None or latest['Id'] != network_id:
            fail('network_replaced')
        evidence()
        result = latest if _handoff is None else _handoff(target, latest)
        evidence()
        return result


def invocation(target_path, run_id, executable, work, *, _socket_path='/var/run/docker.sock'):
    """Construct startup arguments under the acquisition lock; never execute them."""
    return acquire(target_path, run_id, _socket_path=_socket_path,
                   _handoff=lambda target, network: startup.invocation(executable, work, target, run_id, network))
