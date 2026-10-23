"""Linux-only synthetic local fixtures; no SQL, live admission or deadline guarantee.

A reloaded prefix establishes retained syntax/custody checks, never historical
fsync acknowledgement. The caller must independently trust the supplied root and
exclude malicious same-owner mutation. Filesystem calls require future external
supervision before effects can depend on them. No reopen, retry or cleanup API.
"""
from dataclasses import dataclass
from functools import wraps
import fcntl
import hashlib
import os
import stat

from apps.scribeswell.backend.caller_preparation_input import parse_preparation_request
from apps.scribeswell.backend.caller_preparation_evidence import parse_attempt, target_digest


class PreparationStorageError(ValueError):
    code = 'scribeswell_preparation_storage_invalid'

    def __init__(self):
        super().__init__(self.code)


def _safe(function):
    @wraps(function)
    def call(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (OSError, ValueError, TypeError, AttributeError, RecursionError, OverflowError):
            pass
        try:
            raise PreparationStorageError() from None
        except PreparationStorageError as error:
            error.__context__ = None
            raise
    return call


def _require(condition):
    if not condition:
        raise ValueError()


@dataclass(frozen=True, slots=True, repr=False)
class StoredRecord:
    sequence: int
    record_sha256: str


_DIRECTORY = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_READ = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
_WRITE = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
_NAMES = tuple(f'{index:06d}.json' for index in range(1, 5))
_PENDING = '.pending.json'


def _directory(fd):
    info = os.fstat(fd)
    _require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid()
             and stat.S_IMODE(info.st_mode) == 0o700 and info.st_nlink > 0)
    return info


def _file(info):
    _require(stat.S_ISREG(info.st_mode) and info.st_uid == os.geteuid()
             and stat.S_IMODE(info.st_mode) == 0o600 and info.st_nlink == 1
             and 0 < info.st_size <= 32768)


def _identity(info):
    return info.st_dev, info.st_ino


def _fingerprint(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
            info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _binding(root, run, name, identity):
    _directory(root)
    _require(_identity(_directory(run)) == identity)
    named = os.stat(name, dir_fd=root, follow_symlinks=False)
    _require(stat.S_ISDIR(named.st_mode) and _identity(named) == identity)


def _names(run):
    names = []
    with os.scandir(run) as entries:
        for entry in entries:
            _require(len(names) < 4 and entry.name in _NAMES)
            names.append(entry.name)
    names.sort()
    _require(tuple(names) == _NAMES[:len(names)])
    return names


def _read_file(run, name):
    fd = os.open(name, _READ, dir_fd=run)
    try:
        before = os.fstat(fd)
        _file(before)
        _require(_fingerprint(before) == _fingerprint(os.stat(name, dir_fd=run, follow_symlinks=False)))
        parts, size = [], 0
        while True:
            data = os.read(fd, 32769-size)
            if not data:
                break
            size += len(data)
            _require(size <= 32768)
            parts.append(data)
        _require(size == before.st_size)
        after = os.fstat(fd)
        _file(after)
        _require(_fingerprint(before) == _fingerprint(after)
                 == _fingerprint(os.stat(name, dir_fd=run, follow_symlinks=False)))
        return b''.join(parts)
    finally:
        os.close(fd)


def _prefix(root, run, name, identity, request_raw, target):
    _binding(root, run, name, identity)
    names = _names(run)
    raw = tuple(_read_file(run, filename) for filename in names)
    _require(_names(run) == names)
    _binding(root, run, name, identity)
    if raw:
        parsed = parse_attempt(raw, request_raw=request_raw, target=target)
        _require(parsed[0].payload.admission_class == 'synthetic_fixture')
    return raw


def _inputs(root_fd, request_raw, target):
    _require(type(root_fd) is int and root_fd >= 0)
    request = parse_preparation_request(request_raw)
    target_digest(target) # revalidate manually constructed values too
    _require(target.kind == 'local_disposable')
    _directory(root_fd)
    return request.run_id


def _close_pair(root, run):
    try:
        if run is not None:
            os.close(run)
    finally:
        os.close(root)


class FixtureAttemptWriter:
    """Only create_fixture_attempt allocates a writer; no existing run resumes."""
    __slots__ = ('_root', '_run', '_name', '_identity', '_request', '_target', '_records', '_poisoned', '_closed')

    @_safe
    def append(self, raw: bytes) -> StoredRecord:
        try:
            _require(not self._closed and not self._poisoned)
            _require(type(raw) is bytes)
            candidate = self._records + (raw,)
            parsed = parse_attempt(candidate, request_raw=self._request, target=self._target)
            _require(parsed[0].payload.admission_class == 'synthetic_fixture')
            retained = _prefix(self._root, self._run, self._name, self._identity, self._request, self._target)
            _require(retained == self._records)
            filename = _NAMES[len(self._records)]
            fd = os.open(_PENDING, _WRITE, 0o600, dir_fd=self._run)
            try:
                info = os.fstat(fd)
                _require(stat.S_ISREG(info.st_mode) and info.st_uid == os.geteuid()
                         and stat.S_IMODE(info.st_mode) == 0o600 and info.st_nlink == 1 and info.st_size == 0)
                offset = 0
                while offset < len(raw):
                    written = os.write(fd, raw[offset:])
                    _require(type(written) is int and 0 < written <= len(raw)-offset)
                    offset += written
                os.fsync(fd)
                complete = os.fstat(fd)
                _file(complete)
                _require(complete.st_size == len(raw) and _identity(info) == _identity(complete))
                _require(_fingerprint(complete) == _fingerprint(os.stat(_PENDING, dir_fd=self._run, follow_symlinks=False)))
                _binding(self._root, self._run, self._name, self._identity)
                os.link(_PENDING, filename, src_dir_fd=self._run, dst_dir_fd=self._run, follow_symlinks=False)
                linked = os.fstat(fd)
                _require(linked.st_nlink == 2 and _identity(linked) == _identity(complete))
                for name in (_PENDING, filename):
                    _require(_fingerprint(os.stat(name, dir_fd=self._run, follow_symlinks=False)) == _fingerprint(linked))
                os.unlink(_PENDING, dir_fd=self._run)
                final = os.fstat(fd)
                _file(final)
                _require(_fingerprint(final) == _fingerprint(os.stat(filename, dir_fd=self._run, follow_symlinks=False)))
            finally:
                os.close(fd)
            os.fsync(self._run)
            _require(_prefix(self._root, self._run, self._name, self._identity, self._request, self._target) == candidate)
            self._records = candidate
            return StoredRecord(len(candidate), hashlib.sha256(raw).hexdigest())
        except BaseException:
            self._poisoned = True
            raise

    @_safe
    def close(self):
        if not self._closed:
            self._closed = True
            _close_pair(self._root, self._run)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


@_safe
def create_fixture_attempt(root_fd: int, *, request_raw: bytes, target) -> FixtureAttemptWriter:
    """Reserve one new synthetic run; never clean up a failed reservation."""
    name = _inputs(root_fd, request_raw, target)
    root, run = os.dup(root_fd), None
    try:
        os.mkdir(name, 0o700, dir_fd=root)
        run = os.open(name, _DIRECTORY, dir_fd=root)
        identity = _identity(_directory(run))
        fcntl.flock(run, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _binding(root, run, name, identity)
        _require(_names(run) == [])
        os.fsync(root)
        _binding(root, run, name, identity)
        writer = object.__new__(FixtureAttemptWriter)
        writer._root, writer._run, writer._name, writer._identity = root, run, name, identity
        writer._request, writer._target, writer._records = request_raw, target, ()
        writer._closed = writer._poisoned = False
        return writer
    except BaseException:
        _close_pair(root, run)
        raise


@_safe
def read_fixture_prefix(root_fd: int, *, request_raw: bytes, target) -> tuple[bytes, ...]:
    """Read validated retained bytes only; no past acknowledgement is inferred."""
    name = _inputs(root_fd, request_raw, target)
    root, run = os.dup(root_fd), None
    try:
        run = os.open(name, _DIRECTORY, dir_fd=root)
        identity = _identity(_directory(run))
        fcntl.flock(run, fcntl.LOCK_SH | fcntl.LOCK_NB)
        return _prefix(root, run, name, identity, request_raw, target)
    finally:
        _close_pair(root, run)
