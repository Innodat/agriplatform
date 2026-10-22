"""Copyable JCS/HMAC candidate, not a shared runtime or complete WRITE implementation.

Requires the owner's pinned rfc8785==0.1.4. Call only after domain validation and
normalization. No raw decoding, key loading, logging or wire serialization lives here.
"""
from dataclasses import dataclass
import hashlib
import hmac
import math
import re

import rfc8785


class FingerprintError(ValueError):
    """A bounded identifier only; never attach command or secret details."""


@dataclass(frozen=True, repr=False, slots=True)
class CommandFingerprint:
    """Internal retained metadata. The owner stores it privately with its outcome.

    Construction permits unknown historical metadata so verification can refuse it
    without rewriting it. This object must never be returned through an API or log.
    """

    version: int
    algorithm: str
    key_id: str
    digest: bytes

    def __repr__(self):
        return '<CommandFingerprint redacted>'


def _valid_key_id(key_id):
    return type(key_id) is str and re.fullmatch(r'[A-Za-z0-9_-]{1,64}', key_id) is not None


def _require_key(key):
    if type(key) is not bytes or len(key) != 32:
        raise FingerprintError('operation_verification_unavailable')


def _validate(value, active):
    kind = type(value)
    if value is None or kind is bool:
        return
    if kind is str:
        if '\0' in value or any(0xD800 <= ord(character) <= 0xDFFF for character in value):
            raise FingerprintError('invalid_fingerprint_input')
        return
    if kind is int:
        if not -(2**53 - 1) <= value <= 2**53 - 1:
            raise FingerprintError('invalid_fingerprint_input')
        return
    if kind is float:
        if not math.isfinite(value):
            raise FingerprintError('invalid_fingerprint_input')
        return
    if kind not in (list, dict) or id(value) in active:
        raise FingerprintError('invalid_fingerprint_input')
    active.add(id(value))
    try:
        if kind is dict:
            for key, item in value.items():
                if type(key) is not str:
                    raise FingerprintError('invalid_fingerprint_input')
                _validate(key, active)
                _validate(item, active)
        else:
            for item in value:
                _validate(item, active)
    finally:
        active.remove(id(value))


def _canonical(document):
    # Only exact Python JSON types enter the canonicalizer. In particular, tuples,
    # custom mappings and numeric subclasses cannot execute conversion hooks here.
    if type(document) is not dict:
        raise FingerprintError('invalid_fingerprint_input')
    try:
        _validate(document, set())
        return rfc8785.dumps(document)
    except (RecursionError, rfc8785.CanonicalizationError):
        # Canonicalizer exceptions may contain values; never expose their message.
        raise FingerprintError('invalid_fingerprint_input') from None


def create_fingerprint(document, *, key_id, key):
    """Fingerprint an already normalized command with an explicitly chosen key."""
    if not _valid_key_id(key_id):
        raise FingerprintError('operation_verification_unavailable')
    _require_key(key)
    digest = hmac.new(key, _canonical(document), hashlib.sha256).digest()
    return CommandFingerprint(version=1, algorithm='hmac-sha256', key_id=key_id, digest=digest)


def verify_fingerprint(document, stored, *, keys):
    """Return match/mismatch only when the recorded metadata/key can be verified.

    keys is an owner-supplied dictionary of key IDs to 32-byte key material. It has
    no active-key fallback. Missing/unsupported material raises a safe identifier;
    callers must preserve the outcome and must not interpret that as nonexistence.
    """
    if (type(stored) is not CommandFingerprint
            or type(stored.version) is not int or stored.version != 1
            or type(stored.algorithm) is not str or stored.algorithm != 'hmac-sha256'
            or not _valid_key_id(stored.key_id)
            or type(stored.digest) is not bytes or len(stored.digest) != 32
            or type(keys) is not dict):
        raise FingerprintError('operation_verification_unavailable')
    key = keys.get(stored.key_id)
    _require_key(key)
    candidate = hmac.new(key, _canonical(document), hashlib.sha256).digest()
    return hmac.compare_digest(candidate, stored.digest)
