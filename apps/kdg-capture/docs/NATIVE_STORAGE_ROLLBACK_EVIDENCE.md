# Rollback-only native KDG storage qualification — 2026-10-24

bmad-help [BD] selected actual PostgreSQL qualification after the linked storage candidate.
`migrations/tests/qualify_capture_storage.py --run` uses only the custody-verified retained
fixture from run99b7231c-0a5b-4bdb-98e8-3329564c526a, localhost55482, isolated database
kdg_schema_659350f762c8494c9241b7b1c8ea9566. It never prepares a fixture or creates another
role/database/schema. The same stopped run was resumed with the pinned CLI wrapper.
No active Alembic revision, deployment, real account/access or production API is changed.

## What the native test executes

The existing managed write.transaction owns one fresh ten-second transaction on the
fixture administrator connection. SET LOCAL ROLE migrator applies the actual candidate
using connection-bound Alembic Operations. Administrator-only synthetic parent seeding
occurs inside that transaction; SET LOCAL ROLE runtime then executes concrete capture,
outcome and history SQL using validated pinned answers and the existing outcome adapter.
The create operation ID stays bound to its parsed command. The original receipt is read
back through the existing scoped adapter; no-op edit receipts keep the existing revision.

The suite explicitly forces SET CONSTRAINTS ALL IMMEDIATE before accepting positive or
negative cases. A private sentinel then forces the transaction wrapper to rollback all
candidate DDL and rows. New connections verify only the original Alembic ledger remains,
head0001_kdg_foundation and foreign sentinel are unchanged, and the current before/after
cluster metadata digest matches. No automatic downgrade, reset, drop or cleanup runs.
The candidate source and production modules/templates remain unchanged.

The27 native cases cover DDL execution; installed bounded SQL/lock/transaction limits;
capture/outcome/history linkage and original receipt; no-op without fake history; runtime
owner/outcome mutation and DDL denial; invalid device hour; missing history/foreign child/
unknown reported revision; other-owner and foreign-org isolation; own-only outcomes even
under all-read; read-only and missing-mode refusal; immutable facts under an alternate
writer; Unicode blank names; nullable initiator disagreement; fabricated future history;
forced deferred checks; actual outer rollback and final ledger/current metadata retention.
Exact case names/SQLSTATEs and source hashes are retained in the private native report.

## Identity and evidence limits

Actual restricted logins are checked separately, SELECT-only, for all three fixture
roles. They have expected identities/flags, no superuser/migrator membership escalation
and no runtime/operator schema creation authority. Candidate-table SQL executes with
current_user=kdg_capture_runtime but session_user=supabase_admin, because the candidate
is uncommitted inside the administrator-owned transaction. This proves privileges/RLS
under the current role, not role-switch denials from a restricted session. Synthetic
asserted account/actor context is test input, not real Identity/Access authorization.

No durable COMMIT acknowledgement, committed cross-connection replay/uniqueness race,
pool reuse or current Access HTTP/production owner orchestration is qualified. Applying
active revisions and release safety remain consuming gates. These limitations are not
represented as successful native cases.

The unchanged historical inspector was attempted. Its cluster-wide metadata hash differs
from the2026-10-23 baseline; the cause remains unresolved. The old proof and inspector
are preserved, and no historical PASS is claimed for this run. Fresh narrow checks confirm
the exact fixture, role identities, private ledger and sentinel. Current before/after
metadata preservation is checked independently for this rollback-only execution. This
neither repairs nor overwrites the older global baseline or other owners' local work.

## ATDD, focused tests and commands

P = retained `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
Supabase = retained `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase`.
All operations target only the recorded synthetic run; no installation or baseline change.

- Acceptance RED: actual restricted SELECT on capture returned42P01 (undefined table)
  on the original fixture before candidate application; `/tmp/kdg-native-storage-atdd-red.log`.
- Native qualification exposed a test-oracle gap: managed SQL failures are wrapped in
  safe WriteError. A focused unit test first errored, then passed after accepting only
  expected underlying SQLSTATE through that safe wrapper. Application error handling
  and managed helper remain unchanged.
- A negative fixture incorrectly built a VerifiedContext for missing mode, failing before
  it reached PostgreSQL. The regression first failed; the fixture now installs the
  malformed transaction-local test value directly. Runtime context validation is unchanged.
- Optimized Python is refused before native I/O, keeping assertion-based checks effective.
- `P -I -B -m unittest discover -s apps/kdg-capture/write-tests -p 'test_*.py'`:
  45 PASS, including12 focused CLI/error-oracle cases,13 schema smoke,16 outcome and4 owner
  context tests. `/tmp/kdg-native-storage-write-regression.log`.
- `P -I -B apps/kdg-capture/migrations/tests/qualify_capture_storage.py --run`:
  27 native cases PASS; all candidate objects/rows rolled back. Current final report and
  source/log bindings are in [the receipt](evidence/native-storage-rollback-20261024.json).

Lifecycle uses `python3 platform/deployment/dev.py up|stop --target platform/deployment/environments/kdg-local.json --run-id 99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase <absolute retained Supabase executable>`.
Normal stop preserves retained data/resources; no new fixture or cleanup is performed.

## Delivery impact and next step

Scaffold: no new neutral pattern; existing controlled migration/transaction code and tests
are reused unchanged. Domain schema/scenarios remain KDG-owned. Shared UI: none. Agent
context: existing guidance sufficient. Documentation: current handoff, owner/migration
guide and this source-bound evidence; all previous handoffs/reports retained. ADR: none
changed; ADR-0020 controlled migrations/failure-blocked activation/previous-code compatibility
and recovery still apply. Dependencies and TypeScript7.0.2 stay unchanged.

Next implement the concrete protected owner write orchestration and qualify durable
commit/lost-response recovery/concurrent duplicates through restricted connections on
an appropriately authorized committed fixture. Keep current stored-resource authority,
exact original definitions/eligibility/member/assignment checks and short transactions.
Do not promote the candidate merely because rollback qualification passes. Story1.2's
separate fingerprint bootstrap gate remains. Fingerprints/HMAC, Leave/editor, real accounts/
access, provisioning/deployment/pilot/production and cleanup remain outside this delivery.

## Independent review and final proof

All8 blind review findings are individually triaged in the
[delivery spec](../../../_bmad-output/implementation-artifacts/spec-kdg-native-storage-rollback.md).
Tests now distinguish immediate guard refusals from deferred missing-history failures;
a successful changed-answer/date edit proves edits are accepted. Both capture and history
are read back against parsed values and original operation IDs. Fresh login checks include
private ledger ACLs; every domain table has seeded isolation checks. Unexpected failures
still attempt independent restoration inspection and report whether rollback was verified,
without replacing the original failure. Oracle regressions failed before these corrections.
The native report also hashes fixture-custody and historical-inspection code. No finding
deferred; production candidate/helper sources were not changed to make tests pass.

The final27-case native report binds the exact executed source and verifies ledger-only
state, sentinel and current metadata after rollback. All45 offline write tests pass
(including12 qualifier-oracle tests). The final report/log/stop references and source hashes
are captured in the evidence receipt. Historical global inspection remains false, explicitly
separate from this run's current preservation result; its cause is not asserted.
