# Proven owner boundary examples

PtS verifies the `transaction_context.py` pattern with actual non-owner PostgreSQL
roles, pool reuse, rollback and concurrent organizations. Copy the helper into the
owning application during future scaffold work; platform build-time examples are
not shared backend runtime implementations.

See `apps/pts/alembic.ini`, its `migrations/env.py`, restricted role bootstrap,
`services/access` current authorization HTTP contract, and `tools/py/deploy_pts.py`
for the independently owned-history pattern. Each owner keeps its own versions and
schema, requires explicit migration configuration, and never migrates on startup.
The builder CLI remains a placeholder; these examples do not claim generation tests
or a working generator. Existing legacy SQL composition remains supported.

## Keyed command fingerprint candidate

`command_fingerprint.py` is a copyable prerequisite candidate, not an installed
runtime pattern or complete WRITE implementation. It uses the owner's existing
`rfc8785==0.1.4` pin and Python standard-library HMAC/SHA-256. It does not change
`transaction_context.py`, templates or dependency baselines.

The owner first validates the raw request (including duplicate keys, body bounds
and domain DTOs) and normalizes typed IDs, dates and revisions. The owner must
also bound the normalized document, including expansion introduced by normalization.
Raw-input bounds alone do not protect programmatically constructed acyclic graphs
with repeated references that expand during traversal and serialization. This candidate
provides no traversal or output resource budget. Pass the bounded Python JSON object to `create_fingerprint(document, key_id=..., key=...)` with an explicitly
chosen 1–64 ASCII letter/digit/underscore/hyphen key ID and exactly 32 bytes of key
material. KDG-shaped tests use its command type/version, organization, executor
account and exact accepted payload envelope; KDG remains responsible for that meaning.
Arrays retain order, valid strings remain unchanged, and JCS determines object key
ordering and numeric encoding. Unsupported JSON types, cycles, excessive recursion,
NUL, surrogate code points, nonfinite floats and integers outside ±(2^53−1) raise
`FingerprintError('invalid_fingerprint_input')`. Typed big integers belong in domain-
normalized decimal strings. Only exact built-in dict/list/string/number/bool/null
values are accepted, with a dict command document at the root.

Retain the immutable internal `CommandFingerprint` fields `version`, `algorithm`,
`key_id` and full 32-byte `digest` privately with the outcome. Its representation is
redacted and it holds no key bytes. Do not log or expose it. For retries, reconstruct
those original fields and call `verify_fingerprint(document, stored, keys=...)`,
where `keys` is an owner-supplied dict of key IDs to 32-byte bytes values. Verification
uses the recorded supported metadata and key only, then `hmac.compare_digest`.
A mismatch returns false. Missing/bad key material or malformed/unsupported stored
metadata raises `FingerprintError('operation_verification_unavailable')`; preserve
the original outcome and refuse verification, never treat this as fresh execution.
New creation explicitly selects a new key after rotation; retained retries still
need their old key. Secret provisioning, loading, mounting and recovery remain owner
work. Authorization, transactions, receipt persistence and raw HTTP decoding are
outside this helper.

The focused synthetic offline proof uses the actual existing
`installScaffold`/`checkScaffold` extension import: exact initial helper bytes execute,
provenance records their hash, and owner edits/additions survive replay with the
source removed. It does not promote a proven runtime pattern. Run from repository root:

```sh
FINGERPRINT_TEST_NODE="$PWD/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node" \
  platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python \
  -m pytest platform/builder-cli/tests/test_command_fingerprint.py -q
```

The test requires the explicit prepared Node binary and fails if it is unavailable.
See the owner's `WRITE_FINGERPRINT_EVIDENCE.md` for exact results and requirement-to-test
traceability. Independent RFC/JCS byte expectations cover UTF-16 ordering of non-BMP
keys, numeric formatting, integer limits and distinct Unicode compositions; digest
expectations use standard-library HMAC over those independently specified bytes.

Impact decisions: scaffold adds only this copyable example/import proof; shared UI
is unchanged; existing agent context suffices; documentation adds this guide and
owner evidence/current handoff; ADRs are unchanged. No Access/Identity history,
database, Docker, KDG API/editor or Leave implementation is involved.
