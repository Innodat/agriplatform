# Private Studies migration report

The app-owned pure contract is
[`deployment/studies_release_contract.py`](../deployment/studies_release_contract.py).
The optional private worker, app migration supervisor and platform host adopt it
together. It changes release evidence only; no schema or runtime/API wire changes.

A successful private report has exactly these fields:

```json
{"complete":true,"owner":"scribeswell_studies","before":null,"after":"scribeswell_studies_0009","recovery":"forward-only"}
```

`before` is the observed prior Alembic revision: null for a fresh schema, or a
supported revision `scribeswell_studies_0001` through `scribeswell_studies_0009`.
`after` is the observed committed revision and must equal this release's declared
target `scribeswell_studies_0009`. Owner and recovery are fixed. Additional fields,
old four-field reports, foreign/unknown revisions and nonboolean success are refused.
The existing public corpus report/profile and private opt-in remain unchanged.

The controlled private worker first checks packaged Alembic history against the
release declaration and pins its expected head in Config. The environment reads
ordinary Alembic current heads before/after migration under the existing restricted
migration transaction and owner lock. Multiple/unknown current heads, packaged-head
mismatch and missing observations fail closed. Config observations are published
only after transaction exit successfully commits; a reused Config loses stale
observations before every attempt. The worker consumes these committed attributes,
without querying `alembic current` on a second connection or presuming success.
Ordinary head-only Alembic remains usable for genuinely frozen historical fixtures.

The supervisor strictly parses bounded child output, validates it, and persists
that actual object with create-only private evidence semantics. The host loads the
same pure app contract and strictly parses the private evidence within 4096 UTF-8
bytes, rejecting duplicate keys and unsafe/malformed values. Successful private
observations are retained under the migration group's `private_detail`; invalid
raw child payloads are omitted. Existing image digest/release SHA, compatibility
fingerprint, network cleanup and before-activation gates remain binding.

Recovery follows platform ADR-0020: any failed or unknown required step blocks
activation. Reconcile actual ledger/data with restricted owner evidence before a
forward retry or corrective migration. Do not automatically downgrade or claim a
failed commit rolled back without checking the database. Previous application
recovery requires verified compatibility with actual database state. This helper
performs no activation, production migration, owner readiness or external delivery.

## Verification and traceability — 2026-10-27

The persistent interpreter is
`apps/scribeswell/.local/owner-integration-20261027/python/bin/python`.
All commands below set `PYTHONDONTWRITEBYTECODE=1`.

- Existing public/private supervisor and host characterization:
  `python -m pytest apps/scribeswell/tests/test_personal_notes_release.py platform/deployment/tests/test_host.py -q`
  **23 passed in 8.94s**, before behavior edits.
- Acceptance red: the same existing successful supervisor test supplied actual
  `before:0008/after:0009` instead of the false `after:0001` marker.
  `python -m pytest apps/scribeswell/tests/test_personal_notes_release.py -q`
  **1 failed, 4 passed in 1.83s**. The supervisor refused the truthful report.
- After coordinated implementation, focused app report/host checks:
  `python -m pytest apps/scribeswell/tests/test_personal_notes_release.py platform/deployment/tests/test_host.py -q`
  **45 passed in 12.36s**. Contract/history/package synchronization, actual report
  persistence, missing/stale/foreign/duplicate/malformed/oversized report refusal,
  committed-attribute consumption and host activation ordering are covered.
- Affected app migration wrappers and platform release/registry regression:
  `python -m pytest apps/scribeswell/tests/test_personal_notes_release.py apps/scribeswell/tests/test_owned_migrations.py platform/deployment/tests/test_host.py platform/deployment/tests/test_release.py platform/deployment/tests/test_registry_auth.py -q`
  **92 passed, 77 skipped in 30.10s**. The skips require explicitly supplied native
  databases; they are not permission or compatibility proof. This final run includes
  private timeout kill/reap/unknown-state and retained existing-evidence refusal.
  The preceding run was **90 passed, 77 skipped in 38.74s** before those two additions.
- Native collection:
  `python -m pytest apps/scribeswell/tests/test_studies_migration_report_native.py --collect-only -q`
  **6 collected in 1.12s**. The parent owns actual fresh PostgreSQL17 execution;
  collection alone establishes no native result.

Native invocation uses the same interpreter and
`python -m pytest apps/scribeswell/tests/test_studies_migration_report_native.py -q`,
with `SCRIBESWELL_NOTES_TEST_ADMIN_URL` supplied privately for a uniquely owned fresh
local PostgreSQL17 cluster (`127.0.0.1`, initial database `postgres`; KDG/Leave ports
excluded). Each case creates a random database and explicitly tracked roles, then
removes exactly those resources. Do not put the URL in retained safe evidence.

Native requirement mapping: fresh/repeat and ledger assertions prove committed
observations; populated `0001` upgrades retain real frozen previous private SQL
consumer reads/writes/receipts and existing public API reads. Restricted runtime
checks preserve ledger/DDL/cross-owner denial and cross-account RLS. Injected actual
migration DDL failure and PostgreSQL deferred COMMIT failure prove absent success
attributes, unchanged ledger/data and explicit forward retry. Unknown/multiple
current heads are refused with preserved previous data. Existing historical native
compatibility/rollback assertions remain unchanged. No full application suite or
browser matrix is required for this release-evidence change.

## Impact decisions

- Scaffold: no generated helper/template changes; this is an app-specific report
  contract. Migration image packaging and the existing platform compatibility
  fingerprint include the pure contract and all private revisions `0001`–`0009`.
- Shared UI: none; no product surface changes.
- Agent context: no new policy or ownership rule; root instructions already cover
  controlled migrations, sensitive evidence and release safety.
- Documentation: this contract, deployment guidance and delivery record explain
  evidence, refusal, verification limits and forward recovery. Canonical readiness
  reconciliation remains the parent's source-bound review step.
- ADR: no new decision; implements accepted release safety ADR-0020 and existing
  ownership/restricted-authority requirements. Accepted ADRs remain unchanged.

Selected implementation model/effort: Sol High as dispatched; actual model, usage
and compute elapsed unavailable. No implementation subagents or production activation.


## Parent verification and review — 2026-10-27

The parent executed both fresh PostgreSQL17 selections on unchanged source:
**6 new native cases passed in30.47s** (runner39.60s), then the existing
`test_native_migration_failure_rollback_retry_and_owner_force_rls` passed in11.07s
(runner22.12s) on a separate fresh cluster. All131 checked source hashes were unchanged.
Both exact containers stopped with exit0, were removed with their own volumes, and
released dynamic ports32768/32769 without forced termination. KDG/Leave ports and
fixtures were untouched. [Actual native commands/results/source pair](evidence/private-migration-report-20261027/results.json)
and safe logs are retained; these are executed results, not collected tests.

Parent affected regression passed **92 tests,77 native skips in30.41s**. The skipped
other opt-in groups are not claimed as executed; the six new cases and historical
compatibility case above were executed separately. Three independent BMAD review
lenses returned no supported findings or deferrals. The verification reviewer also
ran47app/host checks, passing13.43s, and read the parent native proof.
[Focused command and source comparison](evidence/private-migration-report-20261027/parent-focused.json)
retain exact bounds. No UI/build/full-browser or full repository suite ran for this
release-only correction, and no such result is inferred.

This closes the false private-head-report contract defect. It does not qualify
default Access startup, an actual production release/rollback, external SMTP or
physical devices. Production Studies remains disabled. Shared platform hunks are
isolated from the pre-existing working changes for the local checkpoint; the exact
[additive patch](evidence/private-migration-report-20261027/shared-platform.patch)
is retained. Existing unrelated platform/application changes stay in the working tree.
