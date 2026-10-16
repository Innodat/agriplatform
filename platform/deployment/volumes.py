"""Bounded run-volume acquisition; no public mutation command or startup activation.

Uses the existing .network-UUID.lock for both ENV resource adapters. Volumes are
name-addressed: matching selected observations do not prove immutable identity,
empty storage, lack of attachments, isolation or runtime readiness.
"""
import os
from pathlib import Path
import time

import dev
import networks
import startup

SECONDS = 5
PREFIX = '/v1.48/volumes/'


def fail(code):
    dev.refuse('volume', code)


def create_input(target, run_id):
    profile = startup.fixture_volume(target, run_id)
    return {key: profile[key] for key in ['Name', 'Driver', 'Labels']} | {'DriverOpts': {}}


def acquire(target_path, run_id, *, _socket_path='/var/run/docker.sock', _handoff=None):
    """Acquire/verify the exact name-addressed local volume before handoff.

    A lost POST response refuses without retry. A later invocation always starts
    with name inspection, so uncertainty never causes blind duplicate creation.
    _handoff is a trusted immediate, nonblocking constructor only, never runtime
    execution. Deadline checks surround it but cannot preempt arbitrary Python.
    """
    deadline = time.monotonic() + SECONDS
    networks.validate_run_id(run_id)
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
    with dev.directory(run_path) as run, networks.run_lock(run_path, deadline) as check_lock, \
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
                fail('volume_inspection_failed')
            return startup.volume_descriptor(value, target, run_id)
        evidence()
        dev.docker_prerequisite(_session=session)
        evidence()
        expected = create_input(target, run_id)
        volume = inspect(expected['Name'])
        post_attempted = volume is None
        if post_attempted:
            evidence()
            status, response = exchange('POST', 'create', expected)
            if status != 201:
                fail('volume_create_failed')
            volume = startup.volume_descriptor(response, target, run_id)
        evidence()
        latest = inspect(expected['Name'])
        if latest is None or latest != volume:
            fail('volume_changed')
        evidence()
        result = {'volume': latest, 'post_attempted': post_attempted, 'runtime_ready': False}
        if _handoff is not None:
            result = _handoff(target, result)
        evidence()
        return result
