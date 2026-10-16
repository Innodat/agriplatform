"""Bounded in-memory validation for one synthetic PostgreSQL secret transfer.

No extraction, input hashes, secret persistence, or daemon operations.
Source authority: fixtures/supabase-pg17-lifecycle.md.
"""
import os
import re
import select
import stat
import time

import dev

CONTAINER_ID = 'e' * 64
MEMBER = b'etc/postgresql-custom/pgsodium_root.key'
ROOT_KEY = b'd4dc5b6d4a1d6a10b2c1e76112c994d65db7cec380572cc1839624d4be3fa275'
MAX_BYTES = 10240
READ_SECONDS = 1.0


def refuse():
    dev.refuse('startup', 'unsafe_lifecycle')


def read_archive(fd):
    """Only called after exact cp operands and prerequisite sequence validate."""
    if not (stat.S_ISFIFO(os.fstat(fd).st_mode) or stat.S_ISSOCK(os.fstat(fd).st_mode)):
        refuse()
    deadline = time.monotonic() + READ_SECONDS
    chunks = []
    size = 0
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not select.select([fd], [], [], remaining)[0]:
            refuse()
        chunk = os.read(fd, min(4096, MAX_BYTES + 1 - size))
        if not chunk:
            return b''.join(chunks)
        size += len(chunk)
        if size > MAX_BYTES:
            refuse()
        chunks.append(chunk)


def number(field):
    # Octal digits, optionally preceded by spaces, then NUL/space padding.
    # No digit may follow a terminator and NUL cannot precede the digits.
    if not re.fullmatch(rb' *[0-7]+[\x00 ]*', field):
        refuse()
    return int(field.rstrip(b'\x00 '), 8)


def validate_archive(raw):
    if type(raw) is not bytes or len(raw) != MAX_BYTES:
        refuse()
    h = raw[:512]
    if (h[:100] != MEMBER.ljust(100, b'\0') or h[156:157] != b'0'
            or h[157:257] != b'\0' * 100 or h[257:265] != b'ustar\00000'
            or any(h[265:329]) or any(h[345:512])
            or number(h[100:108]) != 0o644 or number(h[108:116]) != 0
            or number(h[116:124]) != 0 or number(h[124:136]) != len(ROOT_KEY)
            or number(h[148:156]) != sum(h[:148]) + 8 * 32 + sum(h[156:])):
        refuse()
    number(h[136:148])
    for field in [h[329:337], h[337:345]]:
        if field != b'\0' * len(field) and number(field) != 0:
            refuse()
    if raw[512:512+len(ROOT_KEY)] != ROOT_KEY or any(raw[512+len(ROOT_KEY):]):
        refuse()
    return {'member_count': 1, 'regular_file': True, 'mode': '0644',
            'uid': 0, 'gid': 0, 'content_verified': True, 'archive_bytes': len(raw)}


def transfer_event():
    return {'kind': 'secret_transfer', 'facts': {'member_count': 1, 'regular_file': True,
            'mode': '0644', 'uid': 0, 'gid': 0, 'content_verified': True}}
