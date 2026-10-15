#!/usr/bin/env python3
"""Run-bound, digest-verified ENV toolchain qualification; never starts runtime."""
import base64
from contextlib import contextmanager
from collections import deque
import fcntl
import hashlib
import http.client
import json
import lzma
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
import uuid
import zipfile
import zlib

import dev

PINS = 'platform/deployment/toolchain-pins.json'
VERSIONS = {'node': '26.11.1', 'npm': '12.2.0', 'typescript': '7.0.2',
            'python': '3.15.0', 'uv': '0.13.1', 'supabase': '2.120.0'}
LAYOUT = {'node': ('tar', 'node'), 'npm': ('tar', 'npm'),
          'typescript': ('tar', 'packages/node_modules/typescript'),
          'typescript_native': ('tar', 'packages/node_modules/@typescript/typescript-linux-x64'),
          'python': ('tar', 'python'), 'uv': ('wheel', 'uv'), 'supabase': ('tar', 'supabase')}
MAX_ARCHIVE = 300 * 1024 * 1024
MAX_EXPANDED = 1024 * 1024 * 1024


def fail(code, stage='toolchain'):
    dev.refuse(stage, code)


def load_pins(raw=None):
    pins = dev.decode(dev.read(dev.ROOT / PINS) if raw is None else raw)
    if (type(pins) is not dict or set(pins) != {'schema_version', 'platform', 'baseline_ref', 'versions', 'archives'}
            or type(pins['schema_version']) is not int or pins['schema_version'] != 1
            or pins['platform'] != 'linux-x86_64-gnu' or pins['baseline_ref'] != dev.BASELINE
            or pins['versions'] != VERSIONS or type(pins['archives']) is not list):
        fail('invalid_pins')
    seen = set()
    for item in pins['archives']:
        if type(item) is not dict or item.get('id') not in LAYOUT or item['id'] in seen:
            fail('invalid_pins')
        seen.add(item['id'])
        fmt, destination = LAYOUT[item['id']]
        extra = 'member' if fmt == 'wheel' else 'strip_prefix'
        if set(item) != {'id', 'url', 'integrity', 'format', 'destination', extra}:
            fail('invalid_pins')
        if item['format'] != fmt or item['destination'] != destination:
            fail('invalid_pins')
        if type(item['url']) is not str or not re.fullmatch(
                r'https://(?:nodejs\.org|registry\.npmjs\.org|github\.com|files\.pythonhosted\.org)/[^\s?#]+', item['url']):
            fail('invalid_pins')
        if type(item[extra]) is not str:
            fail('invalid_pins')
        if item[extra]:
            safe_name(item[extra].rstrip('/'))
        integrity(item)
    if seen != set(LAYOUT):
        fail('invalid_pins')
    return pins


def integrity(item):
    value = item.get('integrity')
    if type(value) is not str or '-' not in value:
        fail('invalid_pins')
    algorithm, encoded = value.split('-', 1)
    if algorithm not in {'sha256', 'sha512'}:
        fail('invalid_pins')
    try:
        expected = base64.b64decode(encoded, validate=True)
    except ValueError:
        fail('invalid_pins')
    if len(expected) != hashlib.new(algorithm).digest_size:
        fail('invalid_pins')
    return algorithm, expected


def safe_name(name):
    if (not name or '\\' in name or '\x00' in name or name.startswith('/')
            or any(part in {'', '.', '..'} for part in name.split('/'))):
        fail('unsafe_archive')
    return PurePosixPath(name)


def verified_archive(item, cache):
    _, digest = integrity(item)
    with archive_lock(cache / ('.lock-' + item['id'] + '-' + digest.hex())):
        return _verified_archive(item, cache)


@contextmanager
def archive_lock(path):
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
                or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600):
            fail('unsafe_archive')
        deadline = time.monotonic() + 120
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    fail('archive_lock_timeout')
                time.sleep(0.025)
        yield
    finally:
        os.close(fd)


def _verified_archive(item, cache):
    algorithm, expected = integrity(item)
    name = item['id'] + '-' + expected.hex() + '.archive'
    archive = cache / name
    if not archive.exists() and not archive.is_symlink():
        temporary = cache / ('.download-' + uuid.uuid4().hex)
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        # Keep partial downloads on failure; never adopt them as verified archives.
        with os.fdopen(fd, 'wb') as output:
            request = urllib.request.Request(item['url'], headers={'User-Agent': 'agriplatform-env/1'})
            deadline = time.monotonic() + 120
            with urllib.request.urlopen(request, timeout=30) as response:
                if not response.url.startswith('https://'):
                    fail('download_failed')
                total = 0
                while True:
                    if time.monotonic() >= deadline:
                        fail('download_deadline')
                    chunk = response.read1(1024 * 1024)
                    if time.monotonic() >= deadline:
                        fail('download_deadline')
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_ARCHIVE:
                        fail('archive_too_large')
                    output.write(chunk)
            output.flush()
            os.fsync(output.fileno())
        verify_digest(temporary, algorithm, expected)
        try:
            os.link(temporary, archive, follow_symlinks=False)
        except FileExistsError:
            pass
        temporary.unlink()
        sync_directory(cache)
    verify_digest(archive, algorithm, expected)
    return archive


def verify_digest(path, algorithm, expected):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as source:
        info = os.fstat(source.fileno())
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) != 0o600 or info.st_size > MAX_ARCHIVE):
            fail('unsafe_archive')
        digest = hashlib.new(algorithm)
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    if digest.digest() != expected:
        fail('archive_digest_mismatch')


def extract(archive, item, payload):
    destination = payload / item['destination']
    make_payload_directory(destination, payload)
    if item['format'] == 'wheel':
        with zipfile.ZipFile(archive) as source:
            if len(source.infolist()) > 50000:
                fail('unsafe_archive')
            for member in source.infolist():
                safe_name(member.filename.rstrip('/'))
                if stat.S_ISLNK(member.external_attr >> 16):
                    fail('unsafe_archive')
            matches = [m for m in source.infolist() if m.filename == item['member']]
            if len(matches) != 1 or matches[0].file_size > MAX_EXPANDED:
                fail('unsafe_archive')
            with source.open(matches[0]) as stream, (destination / 'uv').open('xb') as output:
                shutil.copyfileobj(stream, output)
            (destination / 'uv').chmod(0o700)
        return
    with tarfile.open(archive, 'r:*') as source:
        members = []
        expanded = 0
        for member in source:
            expanded += member.size
            if len(members) >= 50000 or member.size < 0 or expanded > MAX_EXPANDED:
                fail('unsafe_archive')
            members.append(member)
        planned = []
        names = set()
        prefix = item['strip_prefix']
        for member in members:
            original = member.name.rstrip('/')
            safe_name(original)
            if prefix and original == prefix.rstrip('/') and member.isdir():
                continue
            if not original.startswith(prefix):
                fail('unsafe_archive')
            relative = original[len(prefix):]
            safe_name(relative)
            if relative in names or not (member.isdir() or member.isfile() or member.issym() or member.islnk()):
                fail('unsafe_archive')
            names.add(relative)
            if member.issym() or member.islnk():
                link = member.linkname
                if not link or link.startswith('/') or '\\' in link:
                    fail('unsafe_archive')
                base = destination / Path(relative).parent if member.issym() else destination
                if member.islnk() and prefix:
                    if not link.startswith(prefix):
                        fail('unsafe_archive')
                    link = link[len(prefix):]
                target = Path(os.path.abspath(base / link))
                if not target.is_relative_to(destination):
                    fail('unsafe_archive')
            planned.append((member, relative))
        link_names = {relative for member, relative in planned if member.issym() or member.islnk()}
        for _, relative in planned:
            if any(str(parent) in link_names for parent in PurePosixPath(relative).parents):
                fail('unsafe_archive')
        validate_link_graph(planned, prefix)
        # Only regular files/directories are materialized before links, so no archive
        # entry can turn an extraction parent into an escaping symlink.
        for member, relative in planned:
            target = destination / relative
            make_payload_directory(target.parent, payload)
            if member.isdir():
                target.mkdir(mode=0o700, exist_ok=True)
            elif member.isfile():
                with source.extractfile(member) as stream, target.open('xb') as output:
                    shutil.copyfileobj(stream, output)
                target.chmod(0o700 if member.mode & 0o111 else 0o600)
        for member, relative in planned:
            target = destination / relative
            if member.issym():
                target.symlink_to(member.linkname)
            elif member.islnk():
                link = member.linkname[len(prefix):] if prefix else member.linkname
                original = destination / link
                if original.is_symlink() or not original.is_file():
                    fail('unsafe_archive')
                # Copy to preserve the one-link integrity invariant for installed files.
                with original.open('rb') as stream, target.open('xb') as output:
                    shutil.copyfileobj(stream, output)
                target.chmod(original.stat().st_mode & 0o700)


def validate_link_graph(planned, prefix):
    links = {}
    for member, relative in planned:
        if member.issym():
            links[relative] = (False, member.linkname)
        elif member.islnk():
            links[relative] = (True, member.linkname[len(prefix):] if prefix else member.linkname)
    for origin in links:
        pending, resolved, hops = deque(PurePosixPath(origin).parts), [], 0
        while pending:
            part = pending.popleft()
            if part in ('', '.'):
                continue
            if part == '..':
                if not resolved:
                    fail('unsafe_archive')
                resolved.pop()
                continue
            candidate = '/'.join([*resolved, part])
            if candidate in links:
                hops += 1
                if hops > 40:
                    fail('unsafe_archive')
                absolute, target = links[candidate]
                if absolute:
                    resolved = []
                pending.extendleft(reversed(PurePosixPath(target).parts))
            else:
                resolved.append(part)


def make_payload_directory(path, payload):
    current = payload
    for part in path.relative_to(payload).parts:
        current = current / part
        current.mkdir(mode=0o700, exist_ok=True)
        if current.is_symlink():
            fail('unsafe_archive')


def payload_evidence(payload):
    result = {}
    for current, dirs, files in os.walk(payload, followlinks=False):
        for name in sorted(dirs + files):
            path = Path(current) / name
            info = path.lstat()
            relative = str(path.relative_to(payload))
            if info.st_uid != os.getuid() or (not stat.S_ISLNK(info.st_mode) and info.st_mode & 0o077):
                fail('changed_install')
            if stat.S_ISLNK(info.st_mode):
                # Symlink mode is always 0777 on Linux; validated separately below.
                pass
            if stat.S_ISREG(info.st_mode):
                if info.st_nlink != 1:
                    fail('changed_install')
                with path.open('rb') as stream:
                    value = hashlib.file_digest(stream, 'sha256').hexdigest()
                result[relative] = {'kind': 'file', 'sha256': value, 'mode': stat.S_IMODE(info.st_mode)}
            elif stat.S_ISDIR(info.st_mode):
                result[relative] = {'kind': 'directory', 'mode': stat.S_IMODE(info.st_mode)}
            elif stat.S_ISLNK(info.st_mode):
                value = os.readlink(path)
                try:
                    resolved = path.resolve()
                except (OSError, RuntimeError):
                    fail('changed_install')
                if not resolved.is_relative_to(payload.resolve()):
                    fail('changed_install')
                result[relative] = {'kind': 'symlink', 'target': value}
            else:
                fail('changed_install')
    return result


def payload_fingerprint(payload):
    entries = payload_evidence(payload)
    return {'sha256': dev.digest(canonical(entries).encode()), 'entries': len(entries)}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def expected_checks():
    return {'versions': VERSIONS, 'python_gil_platform_stdlib': True,
            'typescript_valid_accepted': True, 'typescript_invalid_rejected': True}


def check_state(state):
    for current, dirs, files in os.walk(state, followlinks=False):
        for name in dirs + files:
            info = (Path(current) / name).lstat()
            if (info.st_uid != os.getuid() or info.st_mode & 0o022
                    or not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode))
                    or (stat.S_ISREG(info.st_mode) and info.st_nlink != 1)):
                fail('unsafe_tool_state')


def write_fixture(path, content):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as output:
        info = os.fstat(output.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.getuid():
            fail('unsafe_tool_state')
        output.truncate(0)
        output.write(content)


def execute(payload, state, pass_fds=()):
    env = {'PATH': str(payload / 'node/bin') + ':/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C',
           'TZ': 'UTC', 'PYTHONDONTWRITEBYTECODE': '1', 'NPM_CONFIG_USERCONFIG': str(state / 'npm-user.npmrc'),
           'NPM_CONFIG_GLOBALCONFIG': str(state / 'npm-global.npmrc'), 'NPM_CONFIG_CACHE': str(state / 'npm-cache'),
           'XDG_CONFIG_HOME': str(state / 'config'), 'XDG_CACHE_HOME': str(state / 'cache'),
           'TMPDIR': str(state / 'tmp'), 'SUPABASE_WORKDIR': str(state / 'supabase'),
           'SUPABASE_HOME': str(state / 'supabase'),
           'NO_UPDATE_NOTIFIER': '1', 'SUPABASE_TELEMETRY_DISABLED': '1'}
    check_state(state)
    write_fixture(state / 'npm-user.npmrc', '')
    write_fixture(state / 'npm-global.npmrc', '')
    for name in ['config', 'cache', 'tmp', 'supabase', 'npm-cache']:
        (state / name).mkdir(mode=0o700, exist_ok=True)
    def run(args, expected=0, label='check'):
        # Never print downloaded child output, even on an error path.
        with tempfile_output(state) as (out, err):
            process = subprocess.run([str(arg) for arg in args], cwd=state, env=env,
                                     stdout=out, stderr=err, timeout=60, check=False, pass_fds=pass_fds)
            if process.returncode != expected:
                fail('tool_execution_failed', 'toolchain_' + label)
            out.seek(0)
            raw = out.read(65537)
            if len(raw) > 65536:
                fail('tool_output_invalid')
            return raw.decode('utf-8').strip()
    node = payload / 'node/bin/node'
    commands = {'node': [node, '--version'],
                'npm': [node, payload / 'npm/bin/npm-cli.js', '--version'],
                'typescript': [node, payload / 'packages/node_modules/typescript/bin/tsc', '--version'],
                'python': [payload / 'python/bin/python3', '-I', '-B', '--version'],
                'uv': [payload / 'uv/uv', '--version'],
                'supabase': [payload / 'supabase/supabase', '--version']}
    results = {name: run(command, label=name + '_version') for name, command in commands.items()}
    expected = {'node': 'v26.11.1', 'npm': '12.2.0', 'typescript': 'Version 7.0.2',
                'python': 'Python 3.15.0', 'uv': 'uv 0.13.1 (x86_64-unknown-linux-gnu)', 'supabase': '2.120.0'}
    if results != expected:
        fail('tool_version_mismatch')
    probe = ('import sys,sysconfig,platform,ssl,sqlite3,ctypes,zlib,bz2,lzma,venv,ensurepip;'
             'assert sys.version_info[:3]==(3,15,0);assert platform.python_implementation()=="CPython";'
             'assert platform.system()=="Linux" and platform.machine()=="x86_64";'
             'assert not sysconfig.get_config_var("Py_GIL_DISABLED");assert sys._is_gil_enabled();print("qualified")')
    if run([payload / 'python/bin/python3', '-I', '-B', '-c', probe], label='python_probe') != 'qualified':
        fail('python_probe_failed')
    type_roots = state / 'type-roots'
    type_roots.mkdir(mode=0o700, exist_ok=True)
    if any(type_roots.iterdir()):
        fail('unsafe_tool_state')
    compiler = [node, payload / 'packages/node_modules/typescript/bin/tsc', '--noEmit', '--strict',
                '--ignoreConfig', '--typeRoots', type_roots]
    valid, invalid = state / 'valid.ts', state / 'invalid.ts'
    write_fixture(valid, 'const value: number = 42;\n')
    write_fixture(invalid, 'const value: number = "invalid";\n')
    run([*compiler, valid], label='typescript_valid')
    if 'TS2322' not in run([*compiler, invalid], expected=1, label='typescript_invalid'):
        fail('compiler_fixture_failed')
    return expected_checks()


@contextmanager
def tempfile_output(state):
    with tempfile.TemporaryFile(dir=state) as out, tempfile.TemporaryFile(dir=state) as err:
        yield out, err


@contextmanager
def anchored_directory(path, create=False):
    """Keep the owned directory inode pinned across later path-based operations."""
    root = dev.ROOT / 'platform/deployment'
    with dev.directory(root) as root_fd:
        fd = os.dup(root_fd)
    try:
        for part in path.relative_to(root).parts:
            if create:
                try:
                    os.mkdir(part, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
                else:
                    os.fsync(fd)
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
            info = os.fstat(fd)
            if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o022:
                fail('unprotected_directory')
        dev.check_private(fd)
        yield fd, descriptor_path(fd)
    finally:
        os.close(fd)


def anchor_current(path, fd):
    with dev.directory(path) as observed:
        a, b = os.fstat(observed), os.fstat(fd)
        return (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino)


def descriptor_path(fd):
    # Compiler launchers spawn native grandchildren that close inherited FDs.
    # Refer to this still-running owner process, rather than each child's self/fd.
    return Path('/proc') / str(os.getpid()) / 'fd' / str(fd)


def qualify(args):
    if str(uuid.UUID(args.run_id)) != args.run_id:
        fail('invalid_run_id', 'arguments')
    target_path = Path(args.target)
    if '..' in target_path.parts:
        fail('unsafe_path', 'paths')
    target_path = Path(os.path.abspath(target_path))
    raw = dev.read(target_path)
    target = dev.decode(raw)
    dev.validate(target, dev.decode(dev.read(dev.ROOT / dev.SCHEMA)))
    if target['workspace_root'] != str(dev.ROOT):
        fail('workspace_mismatch', 'paths')
    prepared = dev.ROOT / 'platform/deployment/.local/kdg' / args.run_id
    with dev.directory(prepared) as fd:
        dev.check_private(fd)
        inventory = dev.read_at(fd, 'inventory.json', protected=True)
    sources = dev.source_evidence()
    dev.prepare(target, raw, args.run_id, target_path, sources)
    if platform.system() != 'Linux' or platform.machine() != 'x86_64' or platform.libc_ver()[0] != 'glibc':
        fail('unsupported_platform')
    pin_raw = dev.read(dev.ROOT / PINS)
    pins = load_pins(pin_raw)
    binding = {'run_id': args.run_id, 'target_sha256': dev.digest(raw),
               'preparation_sha256': dev.digest(inventory), 'preparation_sources': sources,
               'source_sha256': {'platform/deployment/toolchain.py': dev.digest(dev.read(dev.ROOT / 'platform/deployment/toolchain.py')),
                                 PINS: dev.digest(pin_raw)}}

    def inputs_current():
        # Preparation now includes a protected config observation, not inventory alone.
        dev.validate_prepared(target, raw, args.run_id, target_path, sources)
        return (dev.read(target_path) == raw and dev.source_evidence() == sources
                and dev.read(prepared / 'inventory.json') == inventory
                and all(dev.digest(dev.read(dev.ROOT / name)) == value
                        for name, value in binding['source_sha256'].items()))

    if not inputs_current():
        fail('qualification_input_changed')
    base = dev.ROOT / 'platform/deployment/.local/kdg-toolchains'
    cache = dev.ROOT / 'platform/deployment/.local/kdg-toolchain-downloads'
    run_path = base / args.run_id
    with anchored_directory(base, create=True) as (base_fd, _), anchored_directory(cache, create=True) as (cache_fd, cache_dir):
        fresh = False
        try:
            os.mkdir(args.run_id, 0o700, dir_fd=base_fd)
            os.fsync(base_fd)
            fresh = True
        except FileExistsError:
            pass
        run_fd = os.open(args.run_id, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=base_fd)
        try:
            dev.check_private(run_fd)
            run = descriptor_path(run_fd)
            lock = os.open('.qualify.lock', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                           0o600, dir_fd=run_fd)
            os.close(lock)
            payload_fd = state_fd = None
            try:
                if fresh:
                    os.mkdir('payload', 0o700, dir_fd=run_fd)
                    os.mkdir('state', 0o700, dir_fd=run_fd)
                    receipt = receipt_raw = receipt_identity = None
                else:
                    if set(os.listdir(run_fd)) != {'payload', 'state', 'receipt.json', '.qualify.lock'}:
                        fail('incomplete_install')
                    receipt_raw = dev.read_at(run_fd, 'receipt.json', protected=True)
                    info = os.stat('receipt.json', dir_fd=run_fd, follow_symlinks=False)
                    receipt_identity = (info.st_dev, info.st_ino)
                    receipt = dev.decode(receipt_raw)
                payload_fd = os.open('payload', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=run_fd)
                state_fd = os.open('state', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=run_fd)
                dev.check_private(payload_fd)
                dev.check_private(state_fd)
                payload, state = descriptor_path(payload_fd), descriptor_path(state_fd)
                if fresh:
                    for item in pins['archives']:
                        if not inputs_current() or not anchor_current(base, base_fd) or not anchor_current(cache, cache_fd):
                            fail('qualification_input_changed')
                        extract(verified_archive(item, cache_dir), item, payload)
                before = payload_fingerprint(payload)
                expected = {'schema_version': 1, 'binding': binding, 'payload': before,
                            'checks': expected_checks(), 'toolchain_ready': True, 'runtime_ready': False,
                            'runtime_blockers': ['docker_28_loopback_minimum_unqualified', 'runtime_adapter_unqualified']}
                if receipt is not None and canonical(receipt) != canonical(expected):
                    fail('changed_install')
                if not inputs_current() or not anchor_current(run_path, run_fd) or not anchor_current(cache, cache_fd):
                    fail('qualification_input_changed')
                checks = execute(payload, state, pass_fds=(payload_fd, state_fd))
                if payload_fingerprint(payload) != before or canonical(checks) != canonical(expected_checks()):
                    fail('changed_install')
                if not inputs_current() or not anchor_current(run_path, run_fd) or not anchor_current(cache, cache_fd):
                    fail('qualification_input_changed')
                if receipt is not None:
                    after = dev.read_at(run_fd, 'receipt.json', protected=True)
                    info = os.stat('receipt.json', dir_fd=run_fd, follow_symlinks=False)
                    if after != receipt_raw or (info.st_dev, info.st_ino) != receipt_identity:
                        fail('changed_install')
                else:
                    with (run / 'receipt.json').open('x', encoding='utf-8') as output:
                        os.chmod(output.fileno(), 0o600)
                        json.dump(expected, output, indent=2, sort_keys=True)
                        output.write('\n')
                        output.flush()
                        os.fsync(output.fileno())
                    os.fsync(run_fd)
                return {'ok': True, 'stage': 'qualified', 'code': 'toolchain_qualified',
                        'run_id': args.run_id, 'toolchain_ready': True, 'runtime_ready': False}
            finally:
                if payload_fd is not None:
                    os.close(payload_fd)
                if state_fd is not None:
                    os.close(state_fd)
                os.unlink('.qualify.lock', dir_fd=run_fd)
                os.fsync(run_fd)
        finally:
            os.close(run_fd)


def sync_directory(path):
    fd = os.open(path / '.', os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def main(argv=None):
    try:
        parser = dev.Parser(add_help=False, allow_abbrev=False)
        parser.add_argument('command', choices=['qualify'])
        parser.add_argument('--target', required=True)
        parser.add_argument('--run-id', required=True)
        result = qualify(parser.parse_args(argv))
        status = 0
    except dev.Refusal as error:
        result = {'ok': False, 'stage': error.stage, 'code': error.code,
                  'toolchain_ready': False, 'runtime_ready': False}
        status = 2
    except (OSError, ValueError, TypeError, KeyError, RecursionError, tarfile.TarError,
            zipfile.BadZipFile, subprocess.SubprocessError, UnicodeError, EOFError,
            http.client.HTTPException, lzma.LZMAError, zlib.error):
        result = {'ok': False, 'stage': 'toolchain', 'code': 'unsafe_or_unavailable_input',
                  'toolchain_ready': False, 'runtime_ready': False}
        status = 2
    print(json.dumps(result, sort_keys=True))
    return status


if __name__ == '__main__':
    sys.exit(main())
