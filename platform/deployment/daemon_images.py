"""Read-only daemon image observations from current owner-qualified identities.

No CLI dispatch. Private socket injection exists only for synthetic qualification.
This checks reported identities on one connection, not daemon bytes or runtime readiness.
"""
import os
from pathlib import Path
import time
from types import SimpleNamespace

import dev
import networks
import startup
import toolchain

SECONDS = 5


def fail(code):
    dev.refuse('daemon_images', code)


def descriptor(actual, config):
    if (type(actual) is not dict or actual.get('Id') != config
            or actual.get('Os') != 'linux' or actual.get('Architecture') != 'amd64'
            or actual.get('Variant', '') != ''):
        fail('image_identity_mismatch')
    return {'Id': config, 'Os': 'linux', 'Architecture': 'amd64'}


def file_snapshot(paths):
    result = {}
    for path in paths:
        with dev.directory(path.parent) as fd:
            def signature():
                info = os.stat(path.name, dir_fd=fd, follow_symlinks=False)
                return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_nlink,
                        info.st_size, info.st_mtime_ns, info.st_ctime_ns)
            before = signature()
            raw = dev.read_at(fd, path.name)
            if signature() != before:
                fail('image_evidence_changed')
            result[str(path)] = (before, dev.digest(raw))
    return result


def acquire(target_path, run_id, *, _socket_path='/var/run/docker.sock'):
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
    sources = startup.source_snapshot()
    preparation_sources = dev.source_evidence()
    dev.validate_prepared(target, raw, run_id, path, preparation_sources)
    run_path = dev.ROOT / 'platform/deployment/.local/kdg' / run_id
    args = SimpleNamespace(target=str(path), run_id=run_id)
    with dev.directory(run_path) as run, networks.run_lock(run_path, time.monotonic() + SECONDS) as check_lock:
        identity = os.fstat(run)
        inputs = [path, run_path / 'inventory.json', run_path / 'supabase/config.toml',
                  dev.ROOT / 'platform/deployment/.local/kdg-toolchains' / run_id / 'receipt.json']
        inputs += [dev.ROOT / name for name in sources]
        input_snapshot = file_snapshot(inputs)
        # Owner tool probes have their own bounds, outside the daemon phase.
        evidence = startup.existing_images(args)
        config_plan = evidence[3]
        image_root = dev.ROOT / 'platform/deployment/.local/kdg-base-images' / run_id
        with toolchain.anchored_directory(image_root) as (image_fd, _):
            def current():
                check_lock()
                dev.validate_prepared(target, raw, run_id, path, preparation_sources)
                with dev.directory(run_path) as now:
                    info = os.fstat(now)
                    if (info.st_dev, info.st_ino) != (identity.st_dev, identity.st_ino):
                        fail('image_evidence_changed')
                if (dev.read(path) != raw or startup.source_snapshot() != sources
                        or file_snapshot(inputs) != input_snapshot
                        or not toolchain.anchor_current(image_root, image_fd)
                        or startup.evidence_snapshot(image_fd) != evidence[2]):
                    fail('image_evidence_changed')

            current()
            deadline = time.monotonic() + SECONDS
            with dev.DockerSession(_socket_path=_socket_path, deadline=deadline) as session:
                dev.docker_prerequisite(_session=session)

                def inspect(reference, config):
                    status, actual = session.exchange('GET', '/v1.48/images/' + reference + '/json')
                    if status != 200:
                        fail('image_missing' if status == 404 else 'image_inspection_failed')
                    return descriptor(actual, config)

                observations = {reference: inspect(reference, config) for reference, config in config_plan.items()}
                current()
                for reference, config in config_plan.items():
                    if inspect(config, config) != observations[reference]:
                        fail('image_identity_mismatch')
                current()
                if time.monotonic() >= deadline:
                    fail('image_deadline')
            # Recheck owner receipts/payload after the bounded daemon observations.
            if startup.existing_images(args) != evidence:
                fail('image_evidence_changed')
            current()
            return observations
