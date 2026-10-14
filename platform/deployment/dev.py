#!/usr/bin/env python3
"""Bounded ENV preparation. No runtime adapter, migration or secret reader."""
import argparse
from contextlib import ExitStack, contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import stat
import sys
import uuid

ROOT = Path(os.path.abspath(__file__)).parents[2]
SCHEMA = 'platform/deployment/schema/development-target-v1.json'
BASELINE = 'platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md'
CONTRACT = 'platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
SOURCES = ['platform/deployment/dev.py', SCHEMA, BASELINE, CONTRACT,
           'platform/deployment/fixtures/kdg-synthetic-v1.json', 'platform/deployment/registry.json']
LIMIT = 1024 * 1024


class Refusal(Exception):
    def __init__(self, stage, code):
        self.stage, self.code = stage, code


def refuse(stage, code):
    raise Refusal(stage, code)


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            refuse('input', 'duplicate_key')
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: refuse('input', 'invalid_json'))


@contextmanager
def directory(path, create=False):
    """Walk from / using pinned directory descriptors; never follow a symlink."""
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        refuse('paths', 'unsafe_path')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in path.parts[1:]:
            if create:
                try:
                    os.mkdir(component, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
                else:
                    os.fsync(fd)
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd
    finally:
        os.close(fd)


def read_at(fd, name, protected=False):
    file_fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
    with os.fdopen(file_fd, 'rb') as source:
        info = os.fstat(source.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            refuse('paths', 'unsafe_file')
        if protected and (info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600):
            refuse('inventory', 'unprotected_inventory')
        raw = source.read(LIMIT + 1)
        if len(raw) > LIMIT:
            refuse('input', 'input_too_large')
        return raw


def read(path):
    path = Path(path)
    with directory(path.parent) as fd:
        return read_at(fd, path.name)


def validate(value, schema):
    """Evaluate the checked-in schema's deliberately small JSON Schema vocabulary.

    Unsupported assertions fail closed, so editing the schema cannot silently weaken
    runtime validation. No remote schema resolution or third-party bootstrap tools.
    """
    if type(schema) is not dict:
        refuse('schema', 'unsupported_schema')
    supported = {'$schema', '$id', 'title', 'type', 'const', 'enum', 'pattern',
                 'minLength', 'maxLength', 'required', 'properties', 'additionalProperties'}
    if set(schema) - supported:
        refuse('schema', 'unsupported_schema')
    kind = schema.get('type')
    if kind and not {'object': type(value) is dict, 'string': type(value) is str,
                     'integer': type(value) is int}.get(kind, False):
        refuse('input', 'schema_mismatch')
    # Python's True == 1 is deliberately excluded, including nested const arrays.
    if 'const' in schema and json.dumps(value, sort_keys=True) != json.dumps(schema['const'], sort_keys=True):
        refuse('input', 'schema_mismatch')
    if 'enum' in schema and value not in schema['enum']:
        refuse('input', 'schema_mismatch')
    if kind == 'object':
        properties = schema['properties']
        if set(schema['required']) - set(value) or (schema.get('additionalProperties') is False and set(value) - set(properties)):
            refuse('input', 'schema_mismatch')
        for key, item in value.items():
            validate(item, properties[key])
    if kind == 'string':
        if not schema.get('minLength', 0) <= len(value) <= schema.get('maxLength', 512):
            refuse('input', 'schema_mismatch')
        if 'pattern' in schema and re.fullmatch(schema['pattern'], value) is None:
            refuse('input', 'schema_mismatch')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def source_evidence():
    return {name: digest(read(ROOT / name)) for name in SOURCES}


@contextmanager
def free_ports(ports):
    # Hold all probes until preparation finishes. This is a point-in-time check,
    # never an allocation or readiness promise; future up must recheck.
    with ExitStack() as stack:
        for port in ports.values():
            for family, host in [(socket.AF_INET, '0.0.0.0'), (socket.AF_INET6, '::')]:
                try:
                    probe = stack.enter_context(socket.socket(family, socket.SOCK_STREAM))
                    if family == socket.AF_INET6:
                        probe.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                    probe.bind((host, port))
                except OSError:
                    refuse('ports', 'port_unavailable')
        yield


def check_private(fd):
    info = os.fstat(fd)
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        refuse('inventory', 'unprotected_directory')


def prepare(target, raw, run_id, target_path, sources):
    project = target['project_id_prefix'] + '-' + run_id
    expected = {
        'schema_version': 1, 'stage': 'prepared', 'runtime_ready': False,
        'identities_state': 'reserved_only',
        'run_id': run_id, 'target_id': target['target_id'],
        'environment_kind': target['environment_kind'], 'owner_ids': target['owner_ids'],
        'target_sha256': digest(raw), 'source_sha256': sources,
        'fixture_sha256': sources[target['fixture_ref']],
        'registry_sha256': sources[target['release_registry_ref']],
        'schema_sha256': sources[SCHEMA], 'baseline_sha256': sources[BASELINE],
        'identities': {'project': project, 'network': project + '-network',
                       'volumes': {'database': project + '-database'},
                       'containers': {owner: project + '-' + owner for owner in target['owner_ids']}},
    }
    base = ROOT / 'platform/deployment/.local/kdg'
    with free_ports(target['ports']):
        # Validate all preexisting ancestors before mkdir can write anything.
        ancestor = ROOT / 'platform/deployment'
        for component in ['.local', 'kdg', run_id]:
            ancestor = ancestor / component
            if ancestor.exists() or ancestor.is_symlink():
                with directory(ancestor) as ancestor_fd:
                    info = os.fstat(ancestor_fd)
                    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o022:
                        refuse('inventory', 'unprotected_directory')
        with directory(base, create=True) as parent:
            check_private(parent)
            fresh = False
            try:
                os.mkdir(run_id, 0o700, dir_fd=parent)
                os.fsync(parent)
                fresh = True
            except FileExistsError:
                pass
            run = os.open(run_id, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            try:
                check_private(run)
                if not fresh and set(os.listdir(run)) != {'inventory.json'}:
                    refuse('inventory', 'unexpected_run_contents')
                lock = os.open('.prepare.lock', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=run)
                os.close(lock)
                try:
                    # Recheck source and target observations immediately before installation.
                    if source_evidence() != sources or read(target_path) != raw:
                        refuse('inventory', 'source_changed')
                    if not fresh:
                        actual = decode(read_at(run, 'inventory.json', protected=True))
                        if json.dumps(actual, sort_keys=True) != json.dumps(expected, sort_keys=True):
                            refuse('inventory', 'prepared_input_changed')
                    else:
                        temporary = '.inventory-' + uuid.uuid4().hex
                        file_fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=run)
                        # On interruption, incomplete evidence remains; never guess recovery.
                        with os.fdopen(file_fd, 'w') as output:
                            output.write(json.dumps(expected, indent=2, sort_keys=True) + '\n')
                            output.flush()
                            os.fsync(output.fileno())
                        # Atomic no-clobber installation; never replace an existing file.
                        os.link(temporary, 'inventory.json', src_dir_fd=run, dst_dir_fd=run, follow_symlinks=False)
                        os.unlink(temporary, dir_fd=run)
                        os.fsync(run)
                finally:
                    os.unlink('.prepare.lock', dir_fd=run)
                    os.fsync(run)
            finally:
                os.close(run)
    return {'ok': True, 'stage': 'prepared', 'code': 'prepared', 'run_id': run_id, 'runtime_ready': False}


class Parser(argparse.ArgumentParser):
    def error(self, message):
        refuse('arguments', 'invalid_arguments')


def main(argv=None):
    try:
        parser = Parser(add_help=False, allow_abbrev=False)
        parser.add_argument('command', choices=['prepare', 'up', 'verify', 'stop', 'reset'])
        parser.add_argument('--target', required=True)
        parser.add_argument('--run-id', required=True)
        parser.add_argument('--confirm-target')
        args = parser.parse_args(argv)
        if str(uuid.UUID(args.run_id)) != args.run_id:
            refuse('arguments', 'invalid_run_id')
        target_path = Path(args.target)
        if '..' in target_path.parts:
            refuse('paths', 'unsafe_path')
        target_path = Path(os.path.abspath(target_path))
        raw = read(target_path)
        target = decode(raw)
        validate(target, decode(read(ROOT / SCHEMA)))
        if target['workspace_root'] != str(ROOT):
            refuse('paths', 'workspace_mismatch')
        if args.command == 'reset' and args.confirm_target != target['target_id']:
            refuse('confirmation', 'target_confirmation_required')
        if args.command != 'reset' and args.confirm_target is not None:
            refuse('arguments', 'invalid_arguments')
        sources = source_evidence()
        if args.command != 'prepare':
            refuse(args.command, 'runtime_adapter_unqualified')
        result = prepare(target, raw, args.run_id, target_path, sources)
        status = 0
    except Refusal as error:
        result = {'ok': False, 'stage': error.stage, 'code': error.code, 'runtime_ready': False}
        status = 2
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        # Never expose raw configuration, OS errors, JSON excerpts or exception messages.
        result = {'ok': False, 'stage': 'validation', 'code': 'unsafe_or_unavailable_input', 'runtime_ready': False}
        status = 2
    print(json.dumps(result, sort_keys=True))
    return status


if __name__ == '__main__':
    sys.exit(main())
