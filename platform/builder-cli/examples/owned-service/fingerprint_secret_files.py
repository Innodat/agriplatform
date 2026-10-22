"""Owner-copied, read-only KDG secret-file candidate; no provisioning or fallback.

The owner supplies public configuration explicitly. This checks local descriptors,
not deployment mounts, independent archives, transport readiness or authorization.
"""
import base64
from dataclasses import dataclass
import json
import os
import re
import stat

from command_fingerprint import FingerprintError, _valid_key_id

_MAX_DOCUMENT = 4096
_FIELDS = {'schema_version', 'owner_id', 'environment_id', 'key_id', 'key_b64'}


@dataclass(frozen=True, slots=True, repr=False)
class SecretFileConfig:
    active_key_id: str
    secret_dir: str
    environment_id: str
    owner_id: str

    def __post_init__(self):
        if (not _valid_key_id(self.active_key_id)
                or type(self.secret_dir) is not str
                or not 1 < len(self.secret_dir) <= 4096
                or not self.secret_dir.startswith('/')
                or any(part in ('', '.', '..') for part in self.secret_dir.split('/')[1:])
                or any(ord(character) < 32 or ord(character) == 127
                       or 0xD800 <= ord(character) <= 0xDFFF for character in self.secret_dir)
                or type(self.environment_id) is not str
                or re.fullmatch(r'[A-Za-z0-9_.-]{1,128}', self.environment_id) is None
                or type(self.owner_id) is not str or self.owner_id != 'kdg_capture'):
            raise FingerprintError('operation_verification_unavailable')

    def __repr__(self):
        return '<SecretFileConfig redacted>'


@dataclass(frozen=True, slots=True, repr=False)
class FingerprintSecret:
    key_id: str
    key: bytes

    def __repr__(self):
        return '<FingerprintSecret redacted>'


def _pairs(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError()
        result[name] = value
    return result


def _protected(info, mode, kind):
    if (not kind(info.st_mode) or info.st_uid != 10001 or info.st_gid != 10001
            or stat.S_IMODE(info.st_mode) != mode):
        raise ValueError()


def _signature(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _read(config, key_id):
    if type(config) is not SecretFileConfig or not _valid_key_id(key_id):
        raise ValueError()
    if os.geteuid() != 10001 or os.getegid() != 10001:
        raise ValueError()
    directory = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        # Open each component relative to the held descriptor. No ancestor symlink
        # is followed, and renaming a path cannot redirect the open descriptor.
        for component in config.secret_dir.split('/')[1:]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                            | os.O_CLOEXEC, dir_fd=directory)
            os.close(directory)
            directory = child
        _protected(os.fstat(directory), 0o700, stat.S_ISDIR)
        filename = key_id + '.json'
        descriptor = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
                             | os.O_CLOEXEC, dir_fd=directory)
        try:
            before = os.fstat(descriptor)
            _protected(before, 0o400, stat.S_ISREG)
            if before.st_size > _MAX_DOCUMENT:
                raise ValueError()
            chunks = []
            remaining = _MAX_DOCUMENT + 1
            while remaining:
                chunk = os.read(descriptor, remaining)
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            raw = b''.join(chunks)
            if len(raw) > _MAX_DOCUMENT:
                raise ValueError()
            if (_signature(before) != _signature(os.fstat(descriptor))
                    or _signature(before) != _signature(os.stat(filename, dir_fd=directory,
                                                               follow_symlinks=False))):
                raise ValueError()
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)
    document = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs)
    if (type(document) is not dict or set(document) != _FIELDS
            or type(document['schema_version']) is not int or document['schema_version'] != 1
            or type(document['owner_id']) is not str or document['owner_id'] != config.owner_id
            or type(document['environment_id']) is not str
            or document['environment_id'] != config.environment_id
            or type(document['key_id']) is not str or document['key_id'] != key_id
            or type(document['key_b64']) is not str):
        raise ValueError()
    encoded = document['key_b64']
    key = base64.b64decode(encoded, validate=True)
    if len(key) != 32 or base64.b64encode(key).decode('ascii') != encoded:
        raise ValueError()
    return FingerprintSecret(key_id=key_id, key=key)


def load_verification(config, key_id):
    """Load only the recorded ID; preserve outcomes if this safely refuses.

    Errors have no underlying exception chain or content-bearing diagnostics.
    Consumers must not render traceback locals, which can contain runtime secrets.
    """
    try:
        return _read(config, key_id)
    except (OSError, ValueError, UnicodeError, RecursionError):
        pass
    # Raise outside the handler so even __context__ contains no file/JSON error.
    raise FingerprintError('operation_verification_unavailable')


def load_active(config):
    """Refuse write readiness on missing/bad active material; never create keys."""
    if type(config) is not SecretFileConfig:
        raise FingerprintError('operation_verification_unavailable')
    return load_verification(config, config.active_key_id)
