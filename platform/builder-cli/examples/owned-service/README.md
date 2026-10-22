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

## Atomic owner-local write candidate

`atomic_write.py` supplies account-command transaction primitives to copy beside
`command_fingerprint.py`. It requires the owner's SQLAlchemy/psycopg dependencies,
pinned RFC8785 helper and PostgreSQL17 or newer. It is a bounded prerequisite
candidate. `tests/atomic_write_sample.py` demonstrates explicit owner orchestration;
`tests/atomic_write_fixture.sql` is exclusively a synthetic fixture, never a production
migration or application model. The older PtS context example remains independent.

Create `Budget()` before validating authorization. Complete current exact-resource
checks and external observations before entering `transaction`; cap the authority
request at `min(3, budget.remaining())` seconds. Construct `VerifiedContext` from
verified backend organization/account/actor/mode and server-monotonic observation
time. Transaction start requires an observation within the current execution's budget
and no older than one second. Context fields are trusted backend assertions; database
settings do not authenticate someone holding compromised backend credentials.

Use a fresh, idle, non-autocommit READ COMMITTED connection. The context manager
sets all context transaction-locally and caps the total PostgreSQL transaction at the
remaining ten-second execution budget. Server and monotonic checks cannot interrupt a
blocked client socket or a delayed commit acknowledgement. Request/transport timeout
bounds remain consuming owner work; a late acknowledgement is uncertain even when
the server committed successfully. Every owner SQL operation uses `execute`,
which caps statements at five seconds and lock waits at two seconds, also capped by
remaining budget. It checks the deadline after the SQL response. No network or external
delivery belongs inside this transaction. Keep one Budget across any rollback/recheck
restart. A new request obtains new current authority.

Build the exact `OutcomeKey(owner_schema, org_id, account_id, command_type,
operation_id)` and acquire `outcome_lock` before reading outcome or business effects.
Its stable v1 JCS/SHA256 signed64 advisory lock is transaction-scoped; a database
unique constraint on the full outcome tuple remains essential. Only a lock timeout
in this dedicated wait produces `operation_busy`; other SQL errors produce bounded
`internal_error`. Framework adapters must preserve truthful uncertainty, safe trace
references and operation identity, without exposing exception locals or SQL values.

The owner reads its outcome, verifies the stored resource against the authority it
checked, verifies original fingerprint/command/result versions with `verify_existing`,
and validates its command-specific compact result. The sample conservatively refuses a changed stored target before disclosing a receipt.
A full consumer must rollback, check that target's exact authority outside locks and
restart within the original Budget; no receipt may be disclosed beforehand.
Unsupported metadata or unavailable original key produces
`operation_verification_unavailable`, and payload mismatch produces
`operation_payload_mismatch`. Both preserve the original outcome. This candidate
supports v1 commands/results only; the owner defines any later compatible evolution.
It does not supply an unverified lookup API or a generic result dictionary contract.

For a new operation, the owner locks its local records, checks current lifecycle and
expected revision, and updates business state and attribution. Reserve the outcome
UUID in memory, insert its compact outcome and required immutable revision/evidence
with exact organization/executor/command/operation linkage in the same transaction.
A no-op inserts the outcome without inventing a business revision. Evidence or outcome
failure rolls back every local effect. Leave the context manager before returning the
acknowledgement. A later retry checks current authority and returns the original
receipt even if domain state has moved on. Domain models, SQL, validation, authority,
receipt DTO, constraints and named domain error mapping stay with the owning service.

The test fixture uses an exclusive fresh synthetic database and restricted runtime
login separate from its migrator. FORCE RLS, immutable-write guards and scoped composite
foreign keys protect records/outcomes/revisions. The preparation command accepts only
the existing local native target and retains all roles, data and private configuration.
It does not activate a public recipe, alter installer/templates/schema/catalogue or
provision real users. For the exact prepared Python/Node commands, private fixture
location, retained evidence and requirement mapping see
[WRITE_ATOMIC_EVIDENCE.md](../../WRITE_ATOMIC_EVIDENCE.md).

Impact decisions: scaffold adds the copied sibling candidate and actual installer
import/replay proof only; shared UI and agent context remain unchanged; documentation
adds this guide, evidence and the current KDG handoff; accepted ADRs remain unchanged.
Full WRITE, secret-file lifecycle, release/data recovery and first KDG business API
qualification remain separate work.
